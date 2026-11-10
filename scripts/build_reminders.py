"""Freeze all 36 curated development cases under three reminder conditions."""
from pathlib import Path
import hashlib,json,os,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
os.environ.setdefault('XDG_CACHE_HOME',str(ROOT/'.cache'))
os.environ.setdefault('HF_HUB_OFFLINE','1')
from stillguard.reminders import reminder_pair,measure


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    from transformers import AutoTokenizer
    parent=json.loads((ROOT/'manifests/pilot-data.json').read_text())
    source=ROOT/parent['input_path']
    if digest(source)!=parent['input_sha256']:raise ValueError('Parent curated input changed')
    groups=json.loads((ROOT/parent['source_path']).read_text())
    if digest(ROOT/parent['source_path'])!=parent['source_sha256']:raise ValueError('Authoritative policy source changed')
    prose={g['group_id']:g['after']['policy_text'] for g in groups}
    tokenizer=AutoTokenizer.from_pretrained(ROOT/'models/tiny-aya-global',local_files_only=True)
    rows=[]
    for base in map(json.loads,source.read_text().splitlines()):
        if base['condition']!='HC':continue
        specific,generic,matched=reminder_pair(base['messages'],prose[base['group_id']],tokenizer)
        for condition,messages in [('HC',base['messages']),('PR',specific),('GR',generic)]:
            tokens=measure(messages,base['messages'][-1]['content'],tokenizer)
            rows.append(dict(base,id=base['case_id']+'-'+condition,condition=condition,messages=messages,
                             input_tokens=tokens['input_tokens'],matching=tokens if condition=='HC' else matched))
    if len(rows)!=108 or len({r['id'] for r in rows})!=108:raise ValueError('Unexpected development coverage')
    output=ROOT/'data/curated/reminder-001/inputs.jsonl';output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8',newline='\n')
    manifest=dict(kind='development_reminder_comparison',input_path=str(output.relative_to(ROOT)),input_sha256=digest(output),
                  source_path=parent['source_path'],source_sha256=parent['source_sha256'],
                  parent_input_sha256=parent['input_sha256'],parent_manifest_sha256=digest(ROOT/'manifests/pilot-data.json'),
                  generator_sha256=digest(Path(__file__)),reminder_module_sha256=digest(ROOT/'src/stillguard/reminders.py'),
                  tokenizer_revision=parent['tokenizer_revision'],cases=36,calls=108,conditions=['HC','PR','GR'],
                  selection='One fixed wording; all pilot cases are development data; no held-out improvement claim.',
                  matching='PR/GR exact input token count and request prefix position; generic repeated Check padding disclosed.')
    (ROOT/'manifests/reminder-data.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':main()
