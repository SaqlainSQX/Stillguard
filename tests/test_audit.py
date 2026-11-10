import json
from stillguard.audit import evaluate_one
from stillguard.discovery import source_groups,policy_from


def test_auditkit_calls_real_adapter_on_each_replay_and_scores_raw_actions(tmp_path,monkeypatch):
    monkeypatch.setenv('XDG_CACHE_HOME',str(tmp_path))
    group=source_groups()[0];case=group['cases'][0]
    row=dict(messages=[{'role':'user','content':'Only model-facing content.'}],
             evaluator_policy={k:v for k,v in group['after'].items() if k!='policy_text'},
             context=case['context'],expected_action='deploy')
    seen=[]
    def adapter(prompts):
        seen.extend(prompts)
        public={k:v for k,v in case['context'].items() if k!='facts'}
        return [json.dumps(dict(public,action='withhold')) for _ in prompts]
    a=evaluate_one(row,adapter,'unit-test','replay-0')
    b=evaluate_one(row,adapter,'unit-test','replay-1')
    assert len(seen)==2
    assert all('evaluator_policy' not in p and 'expected_action' not in p for p in seen)
    assert a.headline['decision_correct']==0 and b.headline['decision_correct']==0
    assert a.headline['unnecessary_withhold']==1 and a.headline['proposal_violation']==0
