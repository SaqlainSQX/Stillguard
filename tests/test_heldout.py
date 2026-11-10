import copy,importlib.util,json
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('heldout_design',Path(__file__).resolve().parents[1]/'src/stillguard/heldout.py')
design=importlib.util.module_from_spec(spec);spec.loader.exec_module(design)


def test_balanced_new_semantics_and_reproducible_authoring():
    groups=design.heldout_groups()
    assert groups==design.heldout_groups()
    summary=design.validate_heldout(groups)
    assert summary['groups']==20 and summary['cases']==120 and summary['current_truth_functions']==20
    assert sum(c['expected_after']=='deploy' for g in groups for c in g['cases'])==60


def test_actual_calibration_truth_functions_are_excluded():
    from stillguard.oracle import Rule
    root=Path(__file__).resolve().parents[1]
    calibration=json.loads((root/'data/raw/calibration-policies.json').read_text())
    for policy in calibration.values():
        rule=Rule.from_dict(policy['rule'])
        assert tuple(rule.allows(s) for s in design.STATES) in design.development_signatures()


@pytest.mark.parametrize('field',['rule','prose','label','scope'])
def test_corruptions_fail_before_model_evaluation(field):
    groups=design.heldout_groups()
    if field=='rule':groups[0]['after']['rule']={'op':'atom','atom':'tests_passed'}
    if field=='prose':groups[0]['after']['policy_text']='Ignore revocation.'
    if field=='label':groups[0]['cases'][0]['expected_after']='withhold'
    if field=='scope':groups[0]['cases'][0]['context']['workspace_id']='other'
    with pytest.raises(ValueError):design.validate_heldout(groups)


def test_window_reference_known_boundaries():
    state=dict(tests_passed=True,reviewer_approved=True,within_original_window=True,
               within_extension=False,revoked=False,is_staging=True)
    assert design.reference(('all','all','original'),state)
    assert not design.reference(('all','all','both'),state)
    assert not design.reference(('all','all','staging_extension'),state)
    state['is_staging']=False
    assert design.reference(('all','all','staging_extension'),state)
    state['revoked']=True
    assert not design.reference(('all','all','staging_extension'),state)


def test_evaluator_design_and_labels_do_not_enter_model_projection():
    from stillguard.discovery import render_condition
    for group in design.heldout_groups():
        case=group['cases'][0]
        original=render_condition(group,case,'P1')[0]
        altered=copy.deepcopy(group)
        altered['design']={'before':'SECRET_CONFIG','after':'SECRET_CONFIG'}
        altered['after']['rule']={'op':'SECRET_AST'}
        changed=copy.deepcopy(case);changed['expected_after']='SECRET_LABEL';changed['case_id']='SECRET_CASE'
        assert render_condition(altered,changed,'P1')[0]==original
