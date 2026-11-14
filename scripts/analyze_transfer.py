"""Offline replay and unconditional four-group descriptive summaries."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from stillguard.transfer import score

def analyze(run):
    import hashlib
    frozen=json.loads((ROOT/'manifests/transfer-001.json').read_text(encoding='utf-8'))
    for name,digest in frozen['files'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise ValueError('Freeze changed')
    identity=json.loads((Path(run)/'manifest.json').read_text(encoding='utf-8'))
    if identity['freeze']!=frozen or identity['config']!=json.loads((ROOT/'configs/transfer-001.json').read_text(encoding='utf-8')):raise ValueError('Run identity mismatch')
    inputs=json.loads((ROOT/'experiments/transfer-001/inputs.json').read_text(encoding='utf-8')); lookup={r['id']:r for r in inputs}
    records=[json.loads(l) for l in (Path(run)/'calls.jsonl').read_text(encoding='utf-8').splitlines()]
    if len({r['id'] for r in records})!=len(records): raise ValueError('Duplicate calls')
    if len(records)>96:raise ValueError('Budget exceeded')
    for r in records:
        if r['id'] not in lookup:raise ValueError('Unknown call')
        if r.get('model_calls')!=1 or r['status']!='ok':raise ValueError('Failed generation; no complete analysis')
        if r['messages']!=lookup[r['id']]['messages']:raise ValueError('Prompt mismatch')
        if score(lookup[r['id']],r['raw_output'])!=r['score']:raise ValueError('Replay disagreement')
    report=dict(complete=len(records)==96,actual_calls=len(records),groups={})
    for group in ('A1','A2','B1','B2'):
        report['groups'][group]={}
        for condition in ('currentonly','trustedamendment','obsoletearchive'):
            selected=[r['score'] for r in records if lookup[r['id']]['group_id']==group and lookup[r['id']]['condition']==condition]
            report['groups'][group][condition]=dict(n=len(selected),correct=sum(s['correct'] for s in selected),known_unsafe=sum(s['unsafe'] is True for s in selected),invalid=sum(not s['valid'] for s in selected),unknown_unsafe=sum(s['unsafe'] is None for s in selected),target_mismatches=sum(s['target_matches'] is False for s in selected),new_restrictions_correct=sum(r['score']['correct'] for r in records if lookup[r['id']]['group_id']==group and lookup[r['id']]['condition']==condition and lookup[r['id']]['kind']=='new_restriction'),new_restriction_denominator=sum(r['group_id']==group and r['condition']==condition and r['kind']=='new_restriction' for r in inputs),new_permissions_completed=sum(s['new_permission_completed'] for s in selected),new_permission_denominator=sum(r['group_id']==group and r['condition']==condition and r['kind']=='new_permission' for r in inputs))
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args();print(json.dumps(analyze(a.run),indent=2))
