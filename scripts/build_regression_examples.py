"""Build new, scripted integration examples. These are NOT model evaluations."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def atom(name):
    return {'op': 'atom', 'atom': name}


def join(op, *children):
    return {'op': op, 'children': list(children)}


def build():
    t, a, w, e, s, r = map(atom, ('tests_passed', 'reviewer_approved',
        'within_original_window', 'within_extension', 'is_staging', 'revoked'))
    pairs = [
        (join('and', t, a, join('not', r)),
         join('and', t, join('or', a, s), w, join('not', r))),
        (join('and', t, w, join('not', r)),
         join('and', t, e, join('not', r))),
    ]
    # In each pair: unchanged allowed, unchanged denied, newly allowed, newly denied.
    states = [
        [{}, {'revoked': True}, {'reviewer_approved': False, 'environment': 'staging'},
         {'within_original_window': False}],
        [{}, {'tests_passed': False}, {'within_original_window': False},
         {'within_extension': False}],
    ]
    cases = []
    for index, (before, after) in enumerate(pairs):
        for offset, changes in enumerate(states[index]):
            number = index * 4 + offset + 1
            facts = dict(tests_passed=True, reviewer_approved=True,
                         within_original_window=True, within_extension=True, revoked=False)
            facts.update({k: v for k, v in changes.items() if k != 'environment'})
            scope = dict(workspace_id='example_workspace', resource_id=f'example_service_{index+1}')
            context = dict(request_id=f'example_request_{number:02}', **scope,
                           environment=changes.get('environment', 'production'), facts=facts)
            cases.append(dict(case_id=f'example_{number:02}', context=context,
                before_policy=dict(**scope, revision_id='example_r0', rule=before),
                after_policy=dict(**scope, revision_id='example_r1', rule=after)))
    contract = dict(schema_version=1, cases=cases)
    digest = hashlib.sha256(json.dumps(contract, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    # Authored answers, not generated outputs or benchmark evidence.
    gold = ['deploy', 'withhold', 'deploy', 'withhold'] * 2
    baseline = [action if i in (0, 2, 6) else ('withhold' if action == 'deploy' else 'deploy')
                for i, action in enumerate(gold)]
    regressed = ['withhold' if i in (2, 6) else action for i, action in enumerate(gold)]
    result = {'contract.json': contract}
    for name, actions in [('baseline', baseline), ('regressed', regressed), ('corrected', gold),
                          ('all_withhold', ['withhold'] * 8), ('all_deploy', ['deploy'] * 8)]:
        records = []
        for case, action in zip(cases, actions):
            target = {k: case['context'][k] for k in ('request_id', 'workspace_id', 'resource_id', 'environment')}
            records.append(dict(case_id=case['case_id'], raw_output=json.dumps(dict(action=action, **target))))
        result[name + '.json'] = dict(schema_version=1, contract_sha256=digest, records=records)
    return result


if __name__ == '__main__':
    destination = ROOT / 'examples/policy-change'
    destination.mkdir(parents=True, exist_ok=True)
    for name, value in build().items():
        (destination / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    print('Wrote scripted integration fixtures; zero model calls.')
