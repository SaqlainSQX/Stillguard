from stillguard.discovery import source_groups,policy_from
from stillguard.schema import Context
from stillguard.scoring import score_output
from stillguard.diagnostics import payload_sensitivity
import json
import pytest


@pytest.mark.parametrize('wrapper',['```json\n{}\n```','```\n{}\n```'])
def test_fenced_unsafe_payload_remains_unsafe_and_actual_gate_rejects(wrapper):
    group=source_groups()[0];context=Context.from_dict(group['cases'][2]['context'])
    policy=policy_from(group['after'])
    proposal={k:getattr(context,k) for k in ('request_id','workspace_id','resource_id','environment')}
    raw=wrapper.format(json.dumps(dict(proposal,action='deploy')))
    original=score_output(policy,context,raw)
    diagnostic=payload_sensitivity(policy,context,raw)
    assert not original.output_valid and not original.gate.executed
    assert diagnostic['output_valid'] and diagnostic['proposal_violation'] is True
    assert not diagnostic['decision_correct'] and 'gate' not in diagnostic


@pytest.mark.parametrize('raw',['Explanation\n```json\n{}\n```','```json\n{}\n```\nExplanation','```json\n{bad}\n```'])
def test_no_substantive_repair(raw):
    group=source_groups()[0];context=Context.from_dict(group['cases'][0]['context'])
    diagnostic=payload_sensitivity(policy_from(group['after']),context,raw)
    assert not diagnostic['output_valid'] and diagnostic['proposal_violation'] is None
