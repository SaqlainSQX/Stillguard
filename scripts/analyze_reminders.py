"""Complete-development-run summary; no model calls or final method selection."""
from pathlib import Path
import argparse,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'src'))
from analyze_pilot import by_condition
from stillguard.schema import Policy,Context
from stillguard.scoring import score_output


def paired(rows,a,b):
    lookup={(r['case_id'],r['condition']):r for r in rows}
    ids=sorted({r['case_id'] for r in rows})
    result=dict(a=a,b=b,a_correct_b_wrong=[],b_correct_a_wrong=[],
                a_unsafe_b_not_known_unsafe=[],b_unsafe_a_not_known_unsafe=[])
    for case in ids:
        first,second=lookup[case,a]['score'],lookup[case,b]['score']
        if first['decision_correct'] and not second['decision_correct']:result['a_correct_b_wrong'].append(case)
        if second['decision_correct'] and not first['decision_correct']:result['b_correct_a_wrong'].append(case)
        if first['proposal_violation'] is True and second['proposal_violation'] is not True:
            result['a_unsafe_b_not_known_unsafe'].append(case)
        if second['proposal_violation'] is True and first['proposal_violation'] is not True:
            result['b_unsafe_a_not_known_unsafe'].append(case)
    # "Not known unsafe" can be malformed output, so never label it safe/repaired.
    return result


def fence_diagnostic(rows,inputs):
    """Exploratory only: unwrap one complete Markdown fence; retain strict headline."""
    frozen={r['id']:r for r in map(json.loads,Path(inputs).read_text().splitlines())}
    result={}
    for condition in ('HC','PR','GR'):
        items=[r for r in rows if r['condition']==condition]
        scores=[];unwrapped=0
        for record in items:
            raw=record['raw_output']
            match=re.fullmatch(r'```(?:json)?[ \t]*\r?\n([\s\S]*?)\r?\n```',raw.strip())
            if match:raw=match[1];unwrapped+=1
            source=frozen[record['call_key'].rsplit('-repeat',1)[0]]
            scores.append(score_output(Policy.from_dict(source['evaluator_policy']),Context.from_dict(source['context']),raw))
        result[condition]=dict(n=len(items),unwrapped=unwrapped,valid=sum(s.output_valid for s in scores),
                               correct=sum(s.decision_correct for s in scores),
                               known_unsafe=sum(s.proposal_violation is True for s in scores),
                               violation_unknown=sum(s.proposal_violation is None for s in scores))
    return result


def analyze(folder,pilot_folder,inputs=None):
    folder=Path(folder);pilot_folder=Path(pilot_folder)
    if (folder/'EXCLUDED.json').exists():raise ValueError('Excluded run')
    manifest=json.loads((folder/'manifest.json').read_text())
    summary=json.loads((folder/'summary.json').read_text())
    if not summary['complete'] or not summary['working_tree_clean'] or manifest['phase']!='development_reminder':
        raise ValueError('Only complete clean development runs may be analyzed')
    records=list(map(json.loads,(folder/'calls.jsonl').read_text().splitlines()))
    rows=[r for r in records if r['status']=='ok']
    cases={f'g{g:02}-c{c:02}' for g in range(1,7) for c in range(1,7)}
    expected={(case,condition,0) for case in cases for condition in ('HC','PR','GR')}
    if len(rows)!=108 or {(r['case_id'],r['condition'],r['repeat']) for r in rows}!=expected:
        raise ValueError('Incomplete paired coverage')
    if any(r['model_calls']!=1 for r in rows):raise ValueError('Cached/retried call')
    if summary['completed']!=108 or summary['run_id']!=manifest['run_id']:raise ValueError('Summary mismatch')
    if sum(r.get('model_calls',0) for r in records)>108:raise ValueError('Generation budget exceeded')
    old_manifest=json.loads((pilot_folder/'manifest.json').read_text())
    if old_manifest['dataset_sha256']!=manifest['data_manifest']['parent_input_sha256']:
        raise ValueError('Wrong parent discovery run')
    old={r['case_id']:r for r in map(json.loads,(pilot_folder/'calls.jsonl').read_text().splitlines())
         if r['status']=='ok' and r['condition']=='HC'}
    current={r['case_id']:r for r in rows if r['condition']=='HC'}
    if set(old)!=cases:raise ValueError('Missing parent HC cases')
    if any(old[c]['messages']!=current[c]['messages'] for c in cases):raise ValueError('HC replay prompt changed')
    result=dict(kind='development_reminder_analysis',run_id=manifest['run_id'],
        execution_commit=manifest['initial_code_commit'],by_condition=by_condition(rows),
        comparisons=[paired(rows,'PR','GR'),paired(rows,'PR','HC'),paired(rows,'GR','HC')],
        hc_replay=dict(action_flips=sorted(c for c in cases if old[c]['score']['proposed_action']!=current[c]['score']['proposed_action']),
                       correctness_flips=sorted(c for c in cases if old[c]['score']['decision_correct']!=current[c]['score']['decision_correct'])),
        prior_confirmed_cases={c:{r['condition']:r['score'] for r in rows if r['case_id']==c} for c in ('g04-c03','g06-c03')},
        actual_generations=sum(r.get('model_calls',0) for r in records),failed_calls=sum(r['status']!='ok' for r in records),
        unauthorized_simulated_executions=sum(r['score']['proposal_violation'] is True and r['score']['gate']['executed'] for r in rows),
        generation_seconds=sum(r['elapsed_seconds'] for r in rows),
        provenance={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in ('manifest.json','summary.json','calls.jsonl')},
        limitations=['Development cases reused after pilot analysis; no held-out improvement claim.',
                     'Six synthetic groups share four structures; repeated/paired prompts are not independent families.',
                     'Generic Check padding is artificial despite exact token/position matching.',
                     'Specific reminder repeats authoritative policy; this cannot establish an internal safety mechanism.',
                     'Pilot P1 is a separate reference, not a fresh contemporaneous comparison.'])
    if inputs:
        if hashlib.sha256(Path(inputs).read_bytes()).hexdigest()!=manifest['dataset_sha256']:
            raise ValueError('Diagnostic input digest mismatch')
        result['exploratory_fence_unwrap']=fence_diagnostic(rows,inputs)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',required=True)
    parser.add_argument('--pilot',required=True);parser.add_argument('--output',required=True);parser.add_argument('--inputs')
    args=parser.parse_args();result=analyze(args.run,args.pilot,args.inputs)
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
