"""Final paired-grid validation, independent of model inference."""
from .schema import Policy,Context

CONDITIONS=('P1','P1R','H','HC','NC')


def validate_final_inputs(rows,tokenizer=None):
    cases={f'h{g:02}-c{c:02}' for g in range(1,21) for c in range(1,7)}
    expected={(case,condition) for case in cases for condition in CONDITIONS}
    if len(rows)!=600 or {(r['case_id'],r['condition']) for r in rows}!=expected:
        raise ValueError('Incomplete final paired coverage')
    if len({r['id'] for r in rows})!=600:raise ValueError('Duplicate input identity')
    lookup={(r['case_id'],r['condition']):r for r in rows}
    encode=lambda messages:tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,return_dict=True,return_tensors='pt')['input_ids'].shape[1]
    for case in sorted(cases):
        baseline=lookup[case,'P1']
        if baseline['messages']!=lookup[case,'P1R']['messages']:raise ValueError('Cold replay prompt mismatch')
        hc,nc=(lookup[case,c] for c in ('HC','NC'))
        if hc['messages'][0]!=nc['messages'][0] or hc['messages'][-1]!=nc['messages'][-1]:
            raise ValueError('Authoritative policy/request differs between HC and NC')
        if hc['matching']!=nc['matching'] or hc['input_tokens']!=nc['input_tokens']:
            raise ValueError('HC/NC token/position mismatch')
        for condition in CONDITIONS:
            row=lookup[case,condition]
            if row['id']!=case+'-'+condition:raise ValueError('Input ID/condition mismatch')
            if row['context']!=baseline['context'] or row['evaluator_policy']!=baseline['evaluator_policy']:
                raise ValueError('State/current gold policy differs across paired conditions')
            if row['kind']!=baseline['kind'] or row['expected_action']!=baseline['expected_action']:
                raise ValueError('Labels differ across current-policy conditions')
            correct='deploy' if Policy.from_dict(row['evaluator_policy']).allows(Context.from_dict(row['context'])) else 'withhold'
            if correct!=row['expected_action']:raise ValueError('Frozen annotation disagrees with independent oracle')
            if row['input_tokens']<=100:raise ValueError('Implausible token count')
            if tokenizer is not None and encode(row['messages'])!=row['input_tokens']:
                raise ValueError('Actual tensor token count differs from freeze')
        if tokenizer is not None:
            for row in (hc,nc):
                prefix=len(tokenizer.apply_chat_template(row['messages'][:-1],tokenize=True,add_generation_prompt=False,return_dict=True)['input_ids'])
                if prefix!=row['matching']['request_prefix_tokens']:
                    raise ValueError('Actual request position differs from freeze')
    return dict(cases=120,inputs=600,conditions=list(CONDITIONS))
