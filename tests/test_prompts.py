import json
import pytest
from stillguard.prompts import make_messages
from stillguard.schema import Context


def test_model_projection_excludes_gold_ast_rationale_and_expected_labels():
    record = {'expected_action':'SECRET_GOLD_CANARY', 'policy_ast':'SECRET_AST_CANARY',
              'rationale':'SECRET_RATIONALE_CANARY', 'policy_text':'Deploy iff all stated requirements hold.',
              'context':dict(request_id='req1', workspace_id='w1', resource_id='app1', environment='staging',
                facts=dict(tests_passed=True,reviewer_approved=False,within_original_window=True,within_extension=False,revoked=False))}
    messages = make_messages(record['policy_text'], Context.from_dict(record['context']))
    rendered = json.dumps(messages)
    assert all(value not in rendered for key,value in record.items() if key in ('expected_action','policy_ast','rationale'))
    assert 'expected_action' not in rendered and 'policy_ast' not in rendered
    assert json.loads(messages[1]['content']) == record['context']


def test_extra_gold_field_in_context_is_rejected():
    with pytest.raises(ValueError): Context.from_dict({'expected_action':'deploy'})


@pytest.mark.parametrize('text', ['', '  ', None])
def test_empty_policy_is_not_silently_accepted(text):
    with pytest.raises(ValueError): make_messages(text, None)


def test_sentence_facts_preserve_negative_approval_and_revocation_without_gold():
    c=Context('req001','w1','app1','staging',dict(tests_passed=True,reviewer_approved=False,
        within_original_window=False,within_extension=True,revoked=True))
    public=json.loads(make_messages('Policy text.',c,fact_format='sentences')[1]['content'])
    assert public['request_id']=='req001'
    assert set(public['facts'])=={'Tests passed.','Reviewer approval is absent.',
        'Outside the original deployment window.','Inside the extension window.','Access has been revoked.'}
    assert 'expected_action' not in public
