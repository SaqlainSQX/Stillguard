import copy,importlib.util,json
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('demo_builder',Path(__file__).resolve().parents[1]/'scripts/build_demo.py')
demo=importlib.util.module_from_spec(spec);spec.loader.exec_module(demo)


def fixture():
    groups=json.loads((Path(__file__).resolve().parents[1]/'data/raw/heldout-groups.json').read_text())
    group=groups[0]
    rows=[dict(case_id=case['case_id'],condition=condition,raw_output='<script>alert(1)</script>',
               score=dict(proposed_action=None,decision_correct=False,proposal_violation=None,gate=dict(reason='invalid_output')),
               payload_sensitivity=dict(proposed_action=None))
          for case in group['cases'] for condition in ('P1','P1R','H','HC','NC')]
    return group,rows


def test_untrusted_model_output_and_policy_are_escaped():
    group,rows=fixture();group['before']['policy_text']='<script>policy</script>'
    rendered=demo.render_demo(group,rows,dict(run_id='<script>run</script>'))
    assert '<script>' not in rendered
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in rendered
    assert '&lt;script&gt;policy&lt;/script&gt;' in rendered
    assert 'All actions are simulated' in rendered
    assert rendered.count('Raw response</summary>')==30


def test_demo_cannot_choose_another_group_or_omit_requests():
    group,rows=fixture()
    with pytest.raises(ValueError):demo.render_demo(group,rows[:-1],dict(run_id='test'))
    group['group_id']='h02'
    with pytest.raises(ValueError):demo.render_demo(group,rows,dict(run_id='test'))
