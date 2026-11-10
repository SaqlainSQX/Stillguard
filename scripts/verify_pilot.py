"""Offline verification of frozen prompts and independently recomputed scores."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from stillguard.schema import Policy, Context
from stillguard.scoring import score_output


def verify(inputs, folders):
    inputs=Path(inputs)
    digest=hashlib.sha256(inputs.read_bytes()).hexdigest()
    frozen={r['id']:r for r in map(json.loads,inputs.read_text().splitlines())}
    verified=0
    for folder in map(Path,folders):
        manifest=json.loads((folder/'manifest.json').read_text())
        summary=json.loads((folder/'summary.json').read_text())
        if not summary['complete'] or not summary['working_tree_clean']:
            raise ValueError('Incomplete/dirty run')
        if manifest['dataset_sha256']!=digest:
            raise ValueError('Frozen input digest mismatch')
        records=list(map(json.loads,(folder/'calls.jsonl').read_text().splitlines()))
        for record in records:
            if record['status']!='ok':continue
            source_id,repeat=record['call_key'].rsplit('-repeat',1)
            row=frozen[source_id]
            for key in ('messages','context','expected_action','case_id','condition','kind','group_id','structural_cluster','input_tokens'):
                if record[key]!=row[key]:raise ValueError(f'Frozen field mismatch: {key}')
            if int(repeat)!=record['repeat']:raise ValueError('Repeat identity mismatch')
            score=asdict(score_output(Policy.from_dict(row['evaluator_policy']),
                                     Context.from_dict(row['context']),record['raw_output']))
            # JSON serialization normalizes tuple events to lists in saved traces.
            if json.loads(json.dumps(score))!=record['score']:
                raise ValueError('Independent score replay mismatch')
            if record['audit_headline']['decision_correct']!=float(score['decision_correct']):
                raise ValueError('Audit/direct correctness mismatch')
            verified+=1
    return dict(verified_calls=verified,dataset_sha256=digest,
                checks=['frozen prompt/state/labels/tokens','independent full score replay','AuditKIT correctness agreement'])


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--inputs',required=True)
    parser.add_argument('--runs',nargs='+',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    result=verify(args.inputs,args.runs)
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
