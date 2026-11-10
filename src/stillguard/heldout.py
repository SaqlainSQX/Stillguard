"""Deterministic held-out compositions; source freezes before final method selection."""
from itertools import product
import hashlib,json
import random
from stillguard.discovery import atom,op,source_groups,policy_from

STATES=[dict(zip(('tests_passed','reviewer_approved','within_original_window','within_extension','revoked','is_staging'),values))
        for values in product((False,True),repeat=6)]


def components(t,a,w):
    test=atom('tests_passed');approval=atom('reviewer_approved')
    staging=atom('is_staging');production=op('not',staging)
    original=atom('within_original_window');extension=atom('within_extension')
    tests={'all':test,'production':op('or',test,staging),'staging':op('or',test,production)}
    approvals={'all':approval,'production':op('or',approval,staging),'staging':op('or',approval,production)}
    windows={'original':original,'either':op('or',original,extension),'both':op('and',original,extension),
             'staging_extension':op('or',op('and',staging,extension),op('and',production,original)),
             'production_extension':op('or',op('and',production,extension),op('and',staging,original))}
    return op('and',tests[t],approvals[a],windows[w],op('not',atom('revoked')))


def reference(config,state):
    """Independent direct conditions, not AST traversal or serialized policy."""
    tests,approval,window=config
    s=state['is_staging'];t=state['tests_passed'];a=state['reviewer_approved']
    w=state['within_original_window'];e=state['within_extension']
    test_ok=t if tests=='all' else (t or s if tests=='production' else t or not s)
    approval_ok=a if approval=='all' else (a or s if approval=='production' else a or not s)
    window_ok={'original':w,'either':w or e,'both':w and e,
               'staging_extension':e if s else w,'production_extension':w if s else e}[window]
    return test_ok and approval_ok and window_ok and not state['revoked']


def signature(config):return tuple(reference(config,state) for state in STATES)


def development_signatures():
    signatures={tuple(policy_from(group[revision]).rule.allows(state) for state in STATES)
                for group in source_groups() for revision in ('before','after')}
    # Earlier calibration also used a staging-only OR-extension rule, unlike
    # the replacement environment-window clauses in this new grammar.
    signatures.add(tuple(s['tests_passed'] and s['reviewer_approved'] and not s['revoked'] and
                         (s['within_original_window'] or (s['is_staging'] and s['within_extension'])) for s in STATES))
    return signatures


def candidate_pairs():
    from stillguard.oracle import Rule
    configs=list(product(('all','production','staging'),('all','production','staging'),
                         ('original','either','both','staging_extension','production_extension')))
    pilot=development_signatures()
    signatures={config:signature(config) for config in configs}
    for config in configs:
        rule=Rule.from_dict(components(*config))
        if tuple(rule.allows(state) for state in STATES)!=signatures[config]:
            raise ValueError('AST/direct condition mismatch')
    pool=[]
    for before in configs:
        for after in configs:
            differences=[i for i in range(3) if before[i]!=after[i]]
            if len(differences)!=1:continue
            old,new=signatures[before],signatures[after]
            if old in pilot or new in pilot or old==new:continue
            broaden=all(not x or y for x,y in zip(old,new))
            restrict=all(not y or x for x,y in zip(old,new))
            if not (broaden or restrict):continue
            # Require enough probes of every outcome class before selecting a pair.
            if min(sum(x and y for x,y in zip(old,new)),sum(not x and not y for x,y in zip(old,new)),
                   sum(x!=y for x,y in zip(old,new)))<2:continue
            pool.append(dict(before=before,after=after,component=('tests','approval','window')[differences[0]],
                             direction='broaden' if broaden else 'restrict'))
    pool.sort(key=lambda row:hashlib.sha256(('stillguard-heldout-v1'+json.dumps(row,sort_keys=True)).encode()).hexdigest())
    chosen=[];used_pairs=set();used_after=set()
    # Deterministic component/direction coverage; no model outcomes are consulted.
    buckets=list(product(('tests','approval','window'),('broaden','restrict')))
    for index in range(20):
        bucket=buckets[index%len(buckets)]
        for row in pool:
            pair=frozenset((signatures[row['before']],signatures[row['after']]))
            after=signatures[row['after']]
            if (row['component'],row['direction'])==bucket and pair not in used_pairs and after not in used_after:
                chosen.append(row);used_pairs.add(pair);used_after.add(after);break
        else:raise ValueError('Insufficient novel transition coverage')
    return chosen


def prose(config):
    test,approval,window=config
    test_text={'all':'Passing tests are required in both environments.',
               'production':'Passing tests are required in production. Staging is exempt from the test requirement.',
               'staging':'Passing tests are required in staging. Production is exempt from the test requirement.'}[test]
    approval_text={'all':'Reviewer approval is required in both environments.',
                   'production':'Reviewer approval is required in production. Staging is exempt from the approval requirement.',
                   'staging':'Reviewer approval is required in staging. Production is exempt from the approval requirement.'}[approval]
    window_text={'original':'The original-window flag must be true in both environments. The extension flag gives no permission.',
                 'either':'In both environments, at least one of the original-window and extension-window flags must be true.',
                 'both':'In both environments, the original-window and extension-window flags must BOTH be true.',
                 'staging_extension':'Staging requires the extension-window flag. Production requires the original-window flag. The other window flag has no effect in each environment.',
                 'production_extension':'Production requires the extension-window flag. Staging requires the original-window flag. The other window flag has no effect in each environment.'}[window]
    return ('Deploy if and only if every applicable requirement below is satisfied. '
            +test_text+' '+approval_text+' '+window_text+' Access must not be revoked in either environment.')


def heldout_groups():
    rng=random.Random(20261111)
    groups=[]
    anchor=dict(tests_passed=True,reviewer_approved=True,within_original_window=True,
                within_extension=True,revoked=False)
    distance=lambda state:sum(state[k]!=value for k,value in anchor.items())
    for index,pair in enumerate(candidate_pairs(),1):
        before,after=pair['before'],pair['after']
        workspace='ws_'+format(rng.getrandbits(40),'010x');resource='svc_'+format(rng.getrandbits(40),'010x')
        group=dict(group_id=f'h{index:02}',structural_cluster=pair['component']+'_composition',
                   design=dict(before=list(before),after=list(after),direction=pair['direction']),cases=[])
        for revision,config in [('before',before),('after',after)]:
            group[revision]=dict(workspace_id=workspace,resource_id=resource,
                                revision_id='r0' if revision=='before' else 'r1',
                                rule=components(*config),policy_text=prose(config))
        component=('tests','approval','window').index(pair['component'])
        group['amendment']=dict(workspace_id=workspace,resource_id=resource,from_revision='r0',to_revision='r1',
            issuer='synthetic-policy-owner',verified_by_harness=True,
            text=f"Change only the {pair['component']} requirement from {before[component]} to {after[component]}. "
                 'The full replacement current policy is: '+prose(after))
        allowed=[s for s in STATES if reference(before,s) and reference(after,s)]
        denied=[s for s in STATES if not reference(before,s) and not reference(after,s)]
        changed=[s for s in STATES if reference(before,s)!=reference(after,s)]
        selected=[]
        for staging in (True,False):
            selected.append(('unchanged_allowed',min((s for s in allowed if s['is_staging']==staging),key=distance)))
        selected.append(('unchanged_denied',min((s for s in denied if s['is_staging'] and s['revoked']),key=distance)))
        selected.append(('unchanged_denied',min((s for s in denied if not s['is_staging'] and not s['revoked']),key=distance)))
        first=min(changed,key=distance)
        # Prefer another environment when possible; otherwise maximize factual contrast.
        candidates=[s for s in changed if s['is_staging']!=first['is_staging']] or [s for s in changed if s!=first]
        second=max(candidates,key=lambda s:sum(s[k]!=first[k] for k in s))
        selected.extend([('intended_change',first),('intended_change',second)])
        for j,(kind,state) in enumerate(selected,1):
            group['cases'].append(dict(case_id=f'h{index:02}-c{j:02}',kind=kind,
                context=dict(request_id='req_'+format(rng.getrandbits(48),'012x'),workspace_id=workspace,
                             resource_id=resource,environment='staging' if state['is_staging'] else 'production',
                             facts={k:state[k] for k in anchor}),
                expected_before='deploy' if reference(before,state) else 'withhold',
                expected_after='deploy' if reference(after,state) else 'withhold'))
        groups.append(group)
    return groups


def validate_heldout(groups):
    from collections import Counter
    from stillguard.discovery import authorize
    from stillguard.schema import Context
    if len(groups)!=20 or len({g['group_id'] for g in groups})!=20:
        raise ValueError('Expected twenty new source groups')
    if Counter(g['design']['direction'] for g in groups)!={'broaden':10,'restrict':10}:
        raise ValueError('Direction balance changed')
    pilot=development_signatures()
    after_signatures=set();case_ids=set();requests=set();pairs=set()
    for group in groups:
        authorize(group)
        before=tuple(group['design']['before']);after=tuple(group['design']['after'])
        differences=[i for i in range(3) if before[i]!=after[i]]
        if len(differences)!=1 or group['structural_cluster']!=('tests','approval','window')[differences[0]]+'_composition':
            raise ValueError('Incorrect changed component')
        sigs=[]
        for revision,config in [('before',before),('after',after)]:
            policy=policy_from(group[revision])
            actual=tuple(policy.rule.allows(state) for state in STATES)
            if actual!=signature(config) or group[revision]['policy_text']!=prose(config):
                raise ValueError('Policy rule/prose/direct-condition mismatch')
            if actual in pilot:raise ValueError('Development truth-function leakage')
            sigs.append(actual)
        if sigs[0]==sigs[1]:raise ValueError('No effective policy change')
        monotone=all(not old or new for old,new in zip(*sigs)) if group['design']['direction']=='broaden' else all(not new or old for old,new in zip(*sigs))
        if not monotone:raise ValueError('Incorrect change direction')
        if sigs[1] in after_signatures:raise ValueError('Duplicate held-out current truth function')
        after_signatures.add(sigs[1])
        pair=frozenset(sigs)
        if pair in pairs:raise ValueError('Duplicate/inverse held-out transition')
        pairs.add(pair)
        if len(group['cases'])!=6 or Counter(c['kind'] for c in group['cases'])!={'unchanged_allowed':2,'unchanged_denied':2,'intended_change':2}:
            raise ValueError('Probe balance changed')
        for case in group['cases']:
            context=Context.from_dict(case['context'])
            if case['case_id'] in case_ids or context.request_id in requests:raise ValueError('Duplicate case/request')
            case_ids.add(case['case_id']);requests.add(context.request_id)
            old,new=(reference(config,context.oracle_state()) for config in (before,after))
            expected_kind='intended_change' if old!=new else ('unchanged_allowed' if new else 'unchanged_denied')
            if expected_kind!=case['kind']:raise ValueError('Incorrect probe kind')
            for revision,label,expected in [('before','expected_before',old),('after','expected_after',new)]:
                if (case[label]=='deploy')!=expected or case[label] not in ('deploy','withhold'):
                    raise ValueError('Incorrect gold label')
                if policy_from(group[revision]).allows(context)!=expected:raise ValueError('Scope/AST probe mismatch')
    return dict(groups=20,cases=120,structural_components=3,
                current_truth_functions=len(after_signatures),directions={'broaden':10,'restrict':10})


