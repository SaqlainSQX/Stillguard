import copy
import json
import pytest
from stillguard.regression import evaluate, validate_contract, load_json


def fixture():
    cases=[]
    for i,(old,new) in enumerate(((False,True),(True,False),(True,True),(False,False))):
        ctx=dict(request_id=f'r{i}',workspace_id='w',resource_id='s',environment='production',facts=dict(tests_passed=new,reviewer_approved=old,within_original_window=True,within_extension=False,revoked=False))
        def policy(rev,atom): return dict(workspace_id='w',resource_id='s',revision_id=rev,rule=dict(op='atom',atom=atom))
        cases.append(dict(case_id=str(i),before_policy=policy('v1','reviewer_approved'),after_policy=policy('v2','tests_passed'),context=ctx))
    contract=dict(schema_version=1,cases=cases)
    digest,_=validate_contract(contract)
    out=dict(schema_version=1,contract_sha256=digest,records=[dict(case_id=c['case_id'],raw_output=json.dumps(dict(action='deploy' if c['context']['facts']['tests_passed'] else 'withhold',**{k:v for k,v in c['context'].items() if k!='facts'}))) for c in cases])
    return contract,out


def test_identity_and_determinism():
    c,o=fixture()
    assert evaluate(c,o,o)==evaluate(c,o,o)
    assert evaluate(c,o,o)['status']=='pass'

@pytest.mark.parametrize('action',['withhold','deploy'])
def test_constant_candidate_fails(action):
    c,o=fixture(); candidate=copy.deepcopy(o)
    for row in candidate['records']:
        value=json.loads(row['raw_output']);value['action']=action;row['raw_output']=json.dumps(value)
    assert evaluate(c,o,candidate)['status']=='fail'

@pytest.mark.parametrize('mutation',['missing','duplicate','digest','target','malformed'])
def test_bad_records(mutation):
    c,o=fixture();candidate=copy.deepcopy(o)
    if mutation=='missing': candidate['records'].pop()
    if mutation=='duplicate': candidate['records'].append(candidate['records'][0])
    if mutation=='digest': candidate['contract_sha256']='stale'
    if mutation=='target': candidate['records'][0]['raw_output']=candidate['records'][0]['raw_output'].replace('"r0"','"other"')
    if mutation=='malformed': candidate['records'][0]['raw_output']='```json\n{}\n```'
    if mutation in ('missing','duplicate','digest'):
        with pytest.raises(ValueError): evaluate(c,o,candidate)
    else: assert evaluate(c,o,candidate)['status']=='fail'


def test_aggregate_gain_does_not_hide_permission_loss():
    c,o=fixture();base=copy.deepcopy(o);candidate=copy.deepcopy(o)
    for row in base['records'][1:]: row['raw_output']='invalid'
    value=json.loads(candidate['records'][0]['raw_output']);value['action']='withhold';candidate['records'][0]['raw_output']=json.dumps(value)
    report=evaluate(c,base,candidate)
    assert report['aggregate']['candidate']['correct'] > report['aggregate']['baseline']['correct']
    assert report['paired']['lost_newly_allowed']==1
    assert report['status']=='fail'


def test_duplicate_json_keys(tmp_path):
    p=tmp_path/'input.json';p.write_text('{"a":1,"a":2}',encoding='utf-8')
    with pytest.raises(ValueError): load_json(p)
