"""Offline complete-run replay of both strict and sensitivity scores."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'src'))
from verify_pilot import verify
from stillguard.schema import Policy,Context
from stillguard.diagnostics import payload_sensitivity


def verify_final(inputs,folder):
    from analyze_heldout import load_complete
    load_complete(folder)  # Enforce the complete five-way paired grid, not just a count.
    result=verify(inputs,[folder])
    frozen={r['id']:r for r in map(json.loads,Path(inputs).read_text().splitlines())}
    checked=0
    for record in map(json.loads,(Path(folder)/'calls.jsonl').read_text().splitlines()):
        if record['status']!='ok':continue
        row=frozen[record['call_key'].rsplit('-repeat',1)[0]]
        expected=payload_sensitivity(Policy.from_dict(row['evaluator_policy']),Context.from_dict(row['context']),record['raw_output'])
        if expected!=record['payload_sensitivity']:raise ValueError('Payload sensitivity replay mismatch')
        checked+=1
    if checked!=600:raise ValueError('Incomplete final payload verification')
    result['payload_sensitivity_verified']=checked
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--inputs',required=True)
    parser.add_argument('--run',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();result=verify_final(args.inputs,args.run)
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
