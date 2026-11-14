"""Adversarial CI behavior and authored integration-example acceptance checks."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

from stillguard.regression import evaluate, validate_contract

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'examples/policy-change'


def read(name):
    return json.loads((EXAMPLES / name).read_text(encoding='utf-8'))


def run(*args):
    return subprocess.run([sys.executable, '-I', '-S', str(ROOT/'scripts/check_policy_change.py'),
                           *map(str, args)], capture_output=True, text=True, encoding='utf-8')


def test_authored_example_matches_independent_direct_conditions():
    contract = read('contract.json')
    for i, case in enumerate(contract['cases']):
        f = case['context']['facts']
        if i < 4:
            before = f['tests_passed'] and f['reviewer_approved'] and not f['revoked']
            after = f['tests_passed'] and (f['reviewer_approved'] or case['context']['environment']=='staging') and f['within_original_window'] and not f['revoked']
        else:
            before = f['tests_passed'] and f['within_original_window'] and not f['revoked']
            after = f['tests_passed'] and f['within_extension'] and not f['revoked']
        _, parsed = validate_contract(dict(schema_version=1, cases=[case]))
        assert parsed[0][-2:] == (before, after)
        assert after == (i % 4 in (0, 2))
    report = evaluate(contract, read('baseline.json'), read('regressed.json'))
    assert report['aggregate']['baseline']['correct'] == 3
    assert report['aggregate']['candidate']['correct'] == 6
    assert report['paired']['lost_newly_allowed'] == 2
    assert 'lost_allowed' in report['failures']
    assert evaluate(contract, read('baseline.json'), read('corrected.json'))['status'] == 'pass'


@pytest.mark.parametrize('budgets', [dict(max_new_unsafe=True), dict(max_new_unsafe=-1),
    dict(min_candidate_correct_fraction=float('nan')), dict(min_candidate_correct_fraction=True),
    dict(min_candidate_correct_fraction=float('inf')), dict(unknown=0)])
def test_invalid_budgets_rejected(budgets):
    with pytest.raises(ValueError):
        evaluate(read('contract.json'), read('corrected.json'), read('corrected.json'), budgets)


def test_partial_coverage_is_incomplete_unless_explicitly_waived():
    c, o = read('contract.json'), read('corrected.json')
    c['cases'] = c['cases'][:1]
    o['records'] = o['records'][:1]
    o['contract_sha256'], _ = validate_contract(c)
    assert evaluate(c, o, o)['status'] == 'incomplete'
    waived = evaluate(c, o, o, allow_partial_coverage=True)
    assert waived['status'] == 'pass' and waived['allow_partial_coverage'] is True
    assert len(waived['missing_transitions']) == 3
    with pytest.raises(ValueError): evaluate(c, o, o, allow_partial_coverage='yes')


def test_bad_unchanged_baseline_does_not_pass_and_scope_mismatch_rejected():
    c, o = read('contract.json'), read('all_withhold.json')
    result = evaluate(c, o, o)
    assert result['paired']['lost_allowed'] == 0 and result['status'] == 'fail'
    c['cases'][0]['before_policy']['workspace_id'] = 'wrong_scope'
    with pytest.raises(ValueError): evaluate(c, o, o)


def test_same_revision_cannot_mean_different_rules():
    c = read('contract.json')
    c['cases'][1]['after_policy']['rule'] = dict(op='atom', atom='tests_passed')
    with pytest.raises(ValueError): validate_contract(c)


def test_cli_exit_codes_determinism_and_stale_pass_replaced_by_error(tmp_path):
    output, md = tmp_path/'check.json', tmp_path/'check.md'
    args = ['--contract', EXAMPLES/'contract.json', '--baseline', EXAMPLES/'baseline.json',
            '--output', output, '--markdown', md, '--candidate']
    assert run(*args, EXAMPLES/'corrected.json').returncode == 0
    first = output.read_bytes(), md.read_bytes()
    assert run(*args, EXAMPLES/'corrected.json').returncode == 0
    assert first == (output.read_bytes(), md.read_bytes())
    assert run(*args, EXAMPLES/'regressed.json').returncode == 1
    assert '6/8' in md.read_text(encoding='utf-8')
    missing = read('corrected.json'); missing['records'].pop()
    path = tmp_path/'missing.json'; path.write_text(json.dumps(missing), encoding='utf-8')
    assert run(*args, path).returncode == 2
    assert json.loads(output.read_text(encoding='utf-8'))['status'] == 'error'


def test_cli_does_not_overwrite_input(tmp_path):
    path = tmp_path/'contract.json'
    original = (EXAMPLES/'contract.json').read_bytes(); path.write_bytes(original)
    assert run('--contract', path, '--validate-only', '--output', path).returncode == 2
    assert path.read_bytes() == original


def test_report_does_not_render_untrusted_raw_markup(tmp_path):
    spec = importlib.util.spec_from_file_location('check', ROOT/'scripts/check_policy_change.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    c, b, o = read('contract.json'), read('baseline.json'), read('regressed.json')
    o['records'][0]['raw_output'] = '```\n<script>hostile()</script>'
    result = evaluate(c, b, o)
    assert result['cases'][0]['candidate']['proposal_violation'] is None
    assert result['aggregate']['candidate']['unknown_violation_status'] == 1
    assert '<script>' not in module.markdown(result)
