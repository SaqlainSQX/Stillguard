import copy,json
from pathlib import Path
import pytest
from stillguard.discovery import source_groups,render_condition
from stillguard.reminders import policy_reminder,reminder_pair,measure


def test_specific_reminder_accepts_only_policy_prose():
    for value in ('',None,{},'   '):
        with pytest.raises(ValueError):policy_reminder(value)
    assert 'Only this rule.' in policy_reminder('Only this rule.')


def test_failed_generations_and_old_execution_ids_share_one_budget(tmp_path):
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'scripts/run_reminders.py'
    spec=importlib.util.spec_from_file_location('reminder_runner',path)
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    for name,dataset,calls in [('a','same',[1,1]),('b','same',[1,0]),('c','other',[1])]:
        folder=tmp_path/('reminder-'+name);folder.mkdir()
        (folder/'manifest.json').write_text(json.dumps(dict(dataset_sha256=dataset)))
        (folder/'calls.jsonl').write_text('\n'.join(json.dumps(dict(status='error',model_calls=n)) for n in calls))
    assert runner.prior_generation_count(tmp_path,'same')==3


def test_actual_tokenizer_matching_and_no_source_mutation():
    root=Path(__file__).resolve().parents[1]
    if not (root/'models/tiny-aya-global/tokenizer.json').exists():pytest.skip('Pinned tokenizer absent')
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(root/'models/tiny-aya-global',local_files_only=True)
    for group in source_groups():
        case=group['cases'][0]
        messages,_=render_condition(group,case,'HC',tokenizer)
        original=copy.deepcopy(messages)
        specific,generic,metadata=reminder_pair(messages,group['after']['policy_text'],tokenizer)
        assert messages==original
        assert specific[:-1]==generic[:-1]==original[:-1]
        assert specific[-1]['content'].endswith(original[-1]['content'])
        assert generic[-1]['content'].endswith(original[-1]['content'])
        assert group['after']['policy_text'] in specific[-1]['content']
        assert group['after']['policy_text'] not in generic[-1]['content']
        for variant in (specific,generic):
            actual=tokenizer.apply_chat_template(variant,tokenize=True,add_generation_prompt=True,return_dict=True,return_tensors='pt')
            assert actual['input_ids'].shape[1]==metadata['input_tokens']
        assert measure(specific,original[-1]['content'],tokenizer)==measure(generic,original[-1]['content'],tokenizer)
        # Changes to evaluator-only data cannot affect a prose-only reminder.
        altered=copy.deepcopy(group);altered['after']['rule']={'op':'SECRET_AST'}
        altered['cases'][0]['expected_after']='SECRET_LABEL'
        altered['group_id']='SECRET_GROUP'
        assert reminder_pair(messages,altered['after']['policy_text'],tokenizer)==(specific,generic,metadata)
