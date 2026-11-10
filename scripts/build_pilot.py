"""CuratorKIT source curation -> frozen, tokenizer-checked research inputs."""
from pathlib import Path
import hashlib,json,os,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
os.environ.setdefault('XDG_CACHE_HOME',str(ROOT/'.cache'))
os.environ.setdefault('HF_HUB_OFFLINE','1')
from stillguard.discovery import validate_groups,render_condition,CONDITIONS


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    from curatorkit import Curator,CuratorConfig
    from transformers import AutoTokenizer
    source=ROOT/'data/raw/discovery-groups.json'
    groups=json.loads(source.read_text());validate_groups(groups)
    folder=ROOT/'data/curated/pilot-001';folder.mkdir(parents=True,exist_ok=True)
    records=[]
    for group in groups:
        base={k:v for k,v in group.items() if k!='cases'}
        for case in group['cases']:
            public_case={k:v for k,v in case.items() if k not in ('expected_before','expected_after')}
            # Curator's SFT dedup keys include instruction/output, not input.
            # Put the COMPLETE evaluator source payload in instruction so distinct
            # policy/state pairs cannot collapse merely because labels coincide.
            records.append(dict(instruction=json.dumps(dict(group=base,case=public_case),sort_keys=True),input='',
                output=json.dumps({k:case[k] for k in ('expected_before','expected_after')},sort_keys=True)))
    source_rows=folder/'source.jsonl'
    # One declared duplicate verifies real dedup; it must not remove repeated-call controls.
    source_rows.write_text(''.join(json.dumps(r)+'\n' for r in records+[records[0]]),encoding='utf-8',newline='\n')
    curator=Curator(CuratorConfig(dataset=str(source_rows),dedup='exact',clean=False,max_tokens=8192,
                        export_formats=['alpaca'],output_dir=str(folder/'curator'))).run()
    recovered={}
    for path in (folder/'curator').rglob('*.jsonl'):
        for line in path.read_text().splitlines():
            row=json.loads(line)
            if not all(k in row for k in ('instruction','input','output')):continue
            payload=json.loads(row['instruction']);labels=json.loads(row['output'])
            recovered[payload['case']['case_id']]={**row,'payload':payload,'labels':labels}
    if len(recovered)!=36:raise RuntimeError('Curator changed source case coverage')
    originals={json.loads(r['instruction'])['case']['case_id']:r for r in records}
    for key,row in recovered.items():
        if any(row[k]!=originals[key][k] for k in ('instruction','input','output')):
            raise RuntimeError('Curation changed a factual source payload')
    tokenizer=AutoTokenizer.from_pretrained(ROOT/'models/tiny-aya-global',local_files_only=True)
    assembled=[]
    for key in sorted(recovered):
        row=recovered[key];group=row['payload']['group'];case={**row['payload']['case'],**row['labels']}
        for condition in CONDITIONS:
            messages,matching=render_condition(group,case,condition,tokenizer)
            tokens=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True)
            revision='before' if condition in ('P0','P0R') else 'after'
            assembled.append(dict(id=key+'-'+condition,case_id=key,group_id=group['group_id'],
                structural_cluster=group['structural_cluster'],kind=case['kind'],confirmation=case['confirmation'],
                condition=condition,messages=messages,input_tokens=len(tokens),matching=matching,
                context=case['context'],evaluator_policy={k:v for k,v in group[revision].items() if k!='policy_text'},
                expected_action=case['expected_before' if revision=='before' else 'expected_after']))
    if len(assembled)!=252:raise RuntimeError('Condition coverage mismatch')
    output=folder/'inputs.jsonl';output.write_text(''.join(json.dumps(r)+'\n' for r in assembled),encoding='utf-8',newline='\n')
    manifest=dict(kind='synthetic_discovery_pilot',source_sha256=digest(source),input_sha256=digest(output),
                  input_path=str(output.relative_to(ROOT)),source_path=str(source.relative_to(ROOT)),
                  generator_sha256=digest(Path(__file__)),discovery_module_sha256=digest(ROOT/'src/stillguard/discovery.py'),
                  tokenizer_revision=json.loads((ROOT/'configs/model-lock.json').read_text())['revision'],
                  source_rows=37,curated_cases=36,conditions=list(CONDITIONS),discovery_calls=252,
                  structural_clusters=4,scenario_groups=6,
                  caveat='Synthetic groups share policy structures; no independence or real-world representativeness claim.',
                  input_format='checklist policies and JSON facts; selected using development calibration only')
    (ROOT/'manifests/pilot-data.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':main()
