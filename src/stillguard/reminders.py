"""One frozen policy repetition versus an ordinary, token-matched reminder.

This is development prompting, not a learned intervention or policy oracle.
Only authoritative policy prose enters the specific reminder; no labels/state.
"""
import copy

CONDITIONS = ('HC', 'PR', 'GR')
GENERIC = ('Application reminder: carefully review the operative policy and the supplied request. '
           'Check every applicable requirement before choosing an action. '
           'Return only the specified action JSON with the supplied target identifiers.')


def policy_reminder(policy_text):
    if type(policy_text) is not str or not policy_text.strip():
        raise ValueError('Missing authoritative policy prose')
    return ('Application reminder of the current operative policy (the same policy as the system record): '
            + policy_text + '\nCheck every applicable requirement. Return only the specified action JSON.')


def prepend(messages, reminder):
    result=copy.deepcopy(messages)
    if result[-1]['role']!='user':raise ValueError('Expected final request message')
    result[-1]['content']=reminder+'\n\nCURRENT REQUEST:\n'+messages[-1]['content']
    return result


def measure(messages, request, tokenizer):
    rendered=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
    position=rendered.rfind(request)
    if position<0:raise ValueError('Request missing from rendered prompt')
    prefix=tokenizer(rendered[:position],add_special_tokens=False)['input_ids']
    tokens=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,return_dict=True)['input_ids']
    return dict(input_tokens=len(tokens),request_prefix_tokens=len(prefix))


def reminder_pair(hc_messages, policy_text, tokenizer):
    specific=prepend(hc_messages,policy_reminder(policy_text))
    request=hc_messages[-1]['content']
    target=measure(specific,request,tokenizer)
    for n in range(1024):
        # Explicitly disclose repetitive generic padding; it is not natural prose.
        ordinary=prepend(hc_messages,GENERIC+' Check'*n)
        observed=measure(ordinary,request,tokenizer)
        if observed==target:return specific,ordinary,target
        if observed['input_tokens']>target['input_tokens']:
            break
    raise ValueError('Could not exactly match ordinary reminder tokens/position')
