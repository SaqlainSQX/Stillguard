import json
from stillguard.transfer import source,score,Rule

def test_exhaustive_reference_and_coverage():
    groups=source()
    assert len(groups)==4
    assert all(len(g['cases'])==8 for g in groups)
    assert len({c['case_id'] for g in groups for c in g['cases']})==32
    for g in groups:
        kinds={c['kind'] for c in g['cases']}
        assert kinds=={'unchanged_allowed','unchanged_denied','new_permission' if g['group_id'] in ('A1','B1') else 'new_restriction'}

def test_strict_score_binding_and_unknown():
    g=source()[0];c=dict(g['cases'][0],after_rule=g['after_rule'])
    payload={k:c['context'][k] for k in ('request_id','subject_id','resource_id')};payload['action']=c['expected_after']
    assert score(c,json.dumps(payload))['correct']
    payload['subject_id']='other'
    assert score(c,json.dumps(payload))['unsafe']
    assert score(c,'```json\n{}\n```')['unsafe'] is None
    assert not score(c,'{"action":"grant","action":"deny"}')['valid']


def test_deny_wrong_target_is_incorrect_not_unsafe():
    g=source()[0]; c=dict(g['cases'][3],after_rule=g['after_rule'])
    p={k:c['context'][k] for k in ('request_id','subject_id','resource_id')}
    p.update(action='deny',subject_id='wrong')
    result=score(c,json.dumps(p))
    assert not result['correct'] and result['unsafe'] is False and result['target_matches'] is False


def test_unique_states_and_varying_change_denominators():
    groups=source()
    assert [sum(c['kind'].startswith('new_') for c in g['cases']) for g in groups]==[1,1,2,2]
    for g in groups:
        assert len({json.dumps(c['context']['facts'],sort_keys=True) for c in g['cases']})==8
