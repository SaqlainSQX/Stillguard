import importlib.util,json
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('reminder_analysis',Path(__file__).resolve().parents[1]/'scripts/analyze_reminders.py')
analysis=importlib.util.module_from_spec(spec);spec.loader.exec_module(analysis)


def test_pairwise_correctness_counts_do_not_credit_invalid_as_safety():
    def row(case,condition,correct,violation):
        return dict(case_id=case,condition=condition,score=dict(decision_correct=correct,proposal_violation=violation))
    rows=[row('c1','PR',True,False),row('c1','GR',False,True),
          row('c2','PR',False,None),row('c2','GR',False,True),
          row('c3','PR',False,True),row('c3','GR',True,False)]
    report=analysis.paired(rows,'PR','GR')
    assert report['a_correct_b_wrong']==['c1']
    assert report['b_correct_a_wrong']==['c3']
    assert report['b_unsafe_a_not_known_unsafe']==['c1','c2']
    assert 'safe' not in report


def test_partial_run_is_not_analyzed(tmp_path):
    (tmp_path/'manifest.json').write_text(json.dumps(dict(phase='development_reminder')))
    (tmp_path/'summary.json').write_text(json.dumps(dict(complete=False,working_tree_clean=True)))
    with pytest.raises(ValueError,match='complete'):analysis.analyze(tmp_path,tmp_path)


def test_exploratory_unwrap_does_not_repair_extra_keys_or_extra_prose(tmp_path):
    from stillguard.discovery import source_groups
    group=source_groups()[0];case=group['cases'][2]
    policy={k:group['after'][k] for k in ('workspace_id','resource_id','revision_id','rule')}
    proposal={k:case['context'][k] for k in ('request_id','workspace_id','resource_id','environment')}
    proposal['action']='deploy'  # Tests are false; this is unsafe even inside a Markdown fence.
    rows=[];frozen=[]
    for condition in ('HC','PR','GR'):
        raw='```json\n'+json.dumps(proposal)+'\n```'
        if condition=='PR':raw='Explanation\n'+raw
        if condition=='GR':raw='```json\n'+json.dumps(dict(proposal,facts={}))+'\n```'
        rows.append(dict(condition=condition,raw_output=raw,call_key=condition+'-repeat0'))
        frozen.append(dict(id=condition,evaluator_policy=policy,context=case['context']))
    path=tmp_path/'inputs.jsonl';path.write_text('\n'.join(map(json.dumps,frozen)))
    report=analysis.fence_diagnostic(rows,path)
    assert report['HC']['known_unsafe']==1 and report['HC']['valid']==1
    assert report['PR']['valid']==report['GR']['valid']==0
