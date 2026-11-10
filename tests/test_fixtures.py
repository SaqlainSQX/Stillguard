from pathlib import Path
import json
import re
from collections import Counter
from dataclasses import asdict
from stillguard.schema import Policy, Context
from stillguard.prompts import make_messages
from stillguard.scoring import score_output

ROOT = Path(__file__).resolve().parents[1]


def test_explicit_fixture_annotations_agree_with_oracle_and_action_scorer():
    policies = json.loads((ROOT/'data/raw/calibration-policies.json').read_text())
    cases = [json.loads(line) for line in (ROOT/'data/raw/calibration.jsonl').read_text().splitlines()]
    assert len(cases) == 12 and len({c['id'] for c in cases}) == 12
    assert Counter(c['expected_action'] for c in cases) == {'deploy':6, 'withhold':6}
    for case in cases:
        assert re.fullmatch(r'req[0-9]{3}',case['context']['request_id']), 'Model-visible IDs must not encode labels'
        record = policies[case['policy_revision']]
        policy = Policy.from_dict({k:v for k,v in record.items() if k != 'policy_text'})
        context = Context.from_dict(case['context'])
        assert policy.allows(context) == (case['expected_action'] == 'deploy'), case['id']
        payload = {k:v for k,v in context.public_dict().items() if k != 'facts'}
        payload['action'] = case['expected_action']
        correct = score_output(policy,context,json.dumps(payload))
        assert correct.decision_correct,case['id']
        payload['action'] = 'withhold' if case['expected_action'] == 'deploy' else 'deploy'
        wrong = score_output(policy,context,json.dumps(payload))
        assert not wrong.decision_correct,case['id']
        assert wrong.proposal_violation == (case['expected_action'] == 'withhold')
        assert wrong.unnecessary_withhold == (case['expected_action'] == 'deploy')
        rendered = json.dumps(make_messages(record['policy_text'],context))
        assert 'expected_action' not in rendered and 'rationale' not in rendered and '"rule"' not in rendered


def test_declared_action_json_schema_agrees_with_strict_parser():
    import jsonschema
    from stillguard.schema import parse_proposal
    schema = json.loads((ROOT/'configs/action.schema.json').read_text())
    payload = dict(action='deploy',request_id='r1',workspace_id='w1',resource_id='app1',environment='staging')
    jsonschema.validate(payload,schema)
    assert asdict(parse_proposal(json.dumps(payload))) == payload
