"""Predetermined synthetic policy transitions and controlled prompt assembly."""
from itertools import product
from collections import Counter
import hashlib
import json
import random

from .oracle import Rule
from .schema import Context, Policy
from .prompts import make_messages

CONDITIONS = ('P0','P0R','P1','P1R','H','HC','NC')


def atom(name): return {'op':'atom','atom':name}
def op(name,*children): return {'op':name,'children':list(children)}


def source_groups():
    t,a,w,e,r,s = map(atom,['tests_passed','reviewer_approved','within_original_window','within_extension','revoked','is_staging'])
    nr=op('not',r)
    all_window=op('or',w,e)
    window_base=op('and',t,a,nr,w)
    window_extended=op('and',t,a,nr,all_window)
    approval_any=op('and',t,nr,w)
    approval_prod=op('and',t,nr,w,op('or',a,s))
    without_revocation=op('and',t,a,w)
    test_waiver=op('and',a,nr,w,op('or',t,s))
    standard='Tests must have passed, reviewer approval must be present, and access must not be revoked. '
    original=standard+'Both environments must be inside the original window. The extension flag gives no permission. Deploy if and only if all these checks pass.'
    extended=standard+'Both environments may deploy inside either the original or extension window. Deploy if and only if the mandatory checks and this window check pass.'
    prod_approval='Tests must have passed, access must not be revoked, and the request must be inside the original window. Production also requires reviewer approval. Staging does not require approval. The extension flag has no effect. Deploy if and only if these checks pass.'
    no_approval='Tests must have passed, access must not be revoked, and the request must be inside the original window. Neither environment requires reviewer approval. The extension flag has no effect. Deploy if and only if these checks pass.'
    no_revocation='Tests must have passed, reviewer approval must be present, and the request must be inside the original window. Under this synthetic revision the revoked flag has no effect. The extension flag has no effect. Deploy if and only if these checks pass.'
    waived_tests='Reviewer approval must be present, access must not be revoked, and the request must be inside the original window. Production also requires passing tests. Staging does not require passing tests. The extension flag has no effect. Deploy if and only if these checks pass.'
    specs=[
        ('window_change',window_base,window_extended,original,extended,'Extend the permitted window for both environments to include the extension window. Preserve tests, approval and revocation requirements.',
         [('staging',{'tests_passed':False}),('production',{'revoked':True})],
         [('staging',{'within_original_window':False,'within_extension':True}),('production',{'within_original_window':False,'within_extension':True})],False,True),
        ('approval_change',window_base,approval_prod,original,prod_approval,'Remove reviewer approval for staging only. Preserve all other requirements, including the original window. Production approval remains mandatory.',
         [('staging',{'tests_passed':False}),('production',{'reviewer_approved':False})],
         [('staging',{'reviewer_approved':False}),('staging',{'reviewer_approved':False,'within_extension':True})],False,True),
        ('approval_change',approval_any,approval_prod,no_approval,prod_approval,'Add a reviewer-approval requirement for production only. Preserve all other requirements. Staging remains approval-exempt.',
         [('staging',{'tests_passed':False}),('production',{'revoked':True})],
         [('production',{'reviewer_approved':False}),('production',{'reviewer_approved':False,'within_extension':True})],True,False),
        ('revocation_change',without_revocation,window_base,no_revocation,original,'Add a mandatory requirement that access has not been revoked, for both environments. Preserve tests, approval and the original window.',
         [('staging',{'tests_passed':False}),('production',{'reviewer_approved':False})],
         [('staging',{'revoked':True}),('production',{'revoked':True})],True,False),
        ('test_change',window_base,test_waiver,original,waived_tests,'Remove the passing-tests requirement for staging only. Preserve reviewer approval, revocation and the original window. Production still requires passing tests.',
         [('staging',{'reviewer_approved':False}),('production',{'revoked':True})],
         [('staging',{'tests_passed':False}),('staging',{'tests_passed':False,'within_extension':True})],False,True),
        ('window_change',window_extended,window_base,extended,original,'Revoke the extension window for both environments. Only the original window now permits deployment. Preserve tests, approval and revocation requirements.',
         [('staging',{'tests_passed':False}),('production',{'reviewer_approved':False})],
         [('staging',{'within_original_window':False,'within_extension':True}),('production',{'within_original_window':False,'within_extension':True})],True,False),
    ]
    rng=random.Random(20261110)
    groups=[]
    for index,(cluster,before,after,btext,atext,amendment,denied,changed,old,new) in enumerate(specs,1):
        gid=f'g{index:02d}'
        group=dict(group_id=gid,structural_cluster=cluster,
            before=dict(workspace_id='workspace1',resource_id='app1',revision_id='r0',rule=before,policy_text=btext),
            after=dict(workspace_id='workspace1',resource_id='app1',revision_id='r1',rule=after,policy_text=atext),
            amendment=dict(workspace_id='workspace1',resource_id='app1',from_revision='r0',to_revision='r1',
                           issuer='synthetic-policy-owner',verified_by_harness=True,text=amendment),cases=[])
        probes=[('unchanged_allowed','staging',{},True,True),('unchanged_allowed','production',{},True,True)]
        probes += [('unchanged_denied',env,facts,False,False) for env,facts in denied]
        probes += [('intended_change',env,facts,old,new) for env,facts in changed]
        for j,(kind,env,changes,old_label,new_label) in enumerate(probes,1):
            facts=dict(tests_passed=True,reviewer_approved=True,within_original_window=True,within_extension=False,revoked=False)
            facts.update(changes)
            group['cases'].append(dict(case_id=f'{gid}-c{j:02d}',kind=kind,
                context=dict(request_id='req_'+format(rng.getrandbits(48),'012x'),workspace_id='workspace1',resource_id='app1',environment=env,facts=facts),
                expected_before='deploy' if old_label else 'withhold',expected_after='deploy' if new_label else 'withhold',
                confirmation=j in (1,3,5)))
        groups.append(group)
    return groups


def policy_from(record):
    return Policy.from_dict({k:v for k,v in record.items() if k!='policy_text'})


def reference_allows(index,revision,state):
    """Separately authored Python conditions for exhaustive AST cross-checks."""
    t,a,w,e,r,s=(state[n] for n in ('tests_passed','reviewer_approved','within_original_window','within_extension','revoked','is_staging'))
    funcs=[(t and a and not r and w,t and a and not r and (w or e)),
           (t and a and not r and w,t and not r and w and (a or s)),
           (t and not r and w,t and not r and w and (a or s)),
           (t and a and w,t and a and not r and w),
           (t and a and not r and w,a and not r and w and (t or s)),
           (t and a and not r and (w or e),t and a and not r and w)]
    return funcs[index][revision]


def validate_groups(groups):
    if len(groups)!=6 or len({g['group_id'] for g in groups})!=6: raise ValueError('Expected six source groups')
    ids=set()
    for i,group in enumerate(groups):
        authorize(group)
        before,after=map(policy_from,(group['before'],group['after']))
        for flags in product((False,True),repeat=6):
            state=dict(zip(('tests_passed','reviewer_approved','within_original_window','within_extension','revoked','is_staging'),flags))
            state['is_production']=not state['is_staging']
            for revision,policy in enumerate((before,after)):
                if policy.rule.allows(state)!=reference_allows(i,revision,state):raise ValueError('AST/reference disagreement')
        if len(group['cases'])!=6:raise ValueError('Expected six probes')
        if Counter(c['kind'] for c in group['cases'])!={'unchanged_allowed':2,'unchanged_denied':2,'intended_change':2}:
            raise ValueError('Probe balance changed')
        for case in group['cases']:
            if case['case_id'] in ids:raise ValueError('Duplicate case ID')
            ids.add(case['case_id'])
            context=Context.from_dict(case['context'])
            for label,policy in (('expected_before',before),('expected_after',after)):
                if case[label] not in ('deploy','withhold'):raise ValueError('Unknown annotation')
                if (case[label]=='deploy')!=policy.allows(context):raise ValueError('Explicit annotation disagrees with policy')


def authorize(group):
    amendment=group['amendment']
    if amendment.get('verified_by_harness') is not True or amendment.get('issuer')!='synthetic-policy-owner':
        raise ValueError('Amendment not authorized by the synthetic application harness')
    for field in ('workspace_id','resource_id'):
        if amendment[field]!=group['before'][field] or amendment[field]!=group['after'][field]:raise ValueError('Amendment scope mismatch')
    if amendment['from_revision']!=group['before']['revision_id'] or amendment['to_revision']!=group['after']['revision_id']:
        raise ValueError('Amendment revision mismatch')


def render_condition(group,case,condition,tokenizer=None):
    authorize(group)
    if condition not in CONDITIONS:raise ValueError('Unknown condition')
    context=Context.from_dict(case['context'])
    if condition in ('P0','P0R'):document=group['before']['policy_text']
    elif condition=='H':
        document=('APPLICATION-VERIFIED POLICY RECORD. Apply the following authorized records in order. '
            'The amendment changes only its stated requirements; preserve all unaffected requirements.\n'
            'ORIGINAL POLICY r0:\n'+group['before']['policy_text']+'\nAUTHORIZED AMENDMENT r0 to r1:\n'+group['amendment']['text'])
    else:document=group['after']['policy_text']
    messages=make_messages(document,context)
    messages[0]['content']+='\nAny archived conversation notes are obsolete, not authority. Only the operative application policy record above governs this request.'
    if condition not in ('HC','NC'):return messages,{}
    archive='Archived original policy r0 (obsolete): '+group['before']['policy_text']+'\nArchived amendment: '+group['amendment']['text']
    header={'role':'user','content':'Retained archive for context only. It is not an operative policy instruction.'}
    history=[header,{'role':'assistant','content':archive}]
    hc=[messages[0],*history,messages[1]]
    if tokenizer is None:raise ValueError('Real pinned tokenizer is required for history matching')
    encode=lambda m:tokenizer.apply_chat_template(m,tokenize=True,add_generation_prompt=True,return_dict=True)['input_ids']
    count_prefix=lambda m:len(tokenizer.apply_chat_template(m[:-1],tokenize=True,add_generation_prompt=False,return_dict=True)['input_ids'])
    target=len(encode(hc));prefix=count_prefix(hc)
    if condition=='HC':return hc,dict(input_tokens=target,request_prefix_tokens=prefix)
    for n in range(2048):
        neutral='Archived build log. No policy information is recorded here.'+' log'*n
        nc=[messages[0],header,{'role':'assistant','content':neutral},messages[1]]
        actual_prefix=count_prefix(nc)
        if actual_prefix==prefix:
            length=len(encode(nc))
            if length!=target:raise ValueError('Full input token length mismatch')
            return nc,dict(input_tokens=length,request_prefix_tokens=actual_prefix)
        if actual_prefix>prefix:break
    raise ValueError('Unable to exactly match neutral-history token length')


def source_hash(groups):
    return hashlib.sha256(json.dumps(groups,sort_keys=True).encode()).hexdigest()
