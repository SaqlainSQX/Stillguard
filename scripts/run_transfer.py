"""Bounded offline prospective inference; no hidden retries."""
from pathlib import Path
import argparse,hashlib,json,os,random,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from stillguard.transfer import score
os.environ['HF_HUB_OFFLINE']='1'
def main():
    p=argparse.ArgumentParser();p.add_argument('--max-minutes',type=float,default=15);p.add_argument('--max-calls',type=int,default=96);a=p.parse_args()
    if not 0<a.max_minutes<=15 or not 1<=a.max_calls<=96:raise ValueError('Invalid block budget')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise RuntimeError('Commit reviewed freeze first')
    manifest=json.loads((ROOT/'manifests/transfer-001.json').read_text(encoding='utf-8'))
    for name,digest in manifest['files'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('Freeze changed: '+name)
    config=json.loads((ROOT/'configs/transfer-001.json').read_text(encoding='utf-8'));model_manifest=json.loads((ROOT/'manifests/model.json').read_text(encoding='utf-8'))
    if not model_manifest.get('complete') or model_manifest['revision']!=config['model_revision']:raise RuntimeError('Model revision unavailable')
    rows=json.loads((ROOT/'experiments/transfer-001/inputs.json').read_text(encoding='utf-8'));random.Random(45).shuffle(rows)
    folder=ROOT/'results/transfer-001';folder.mkdir(parents=True,exist_ok=True);trace=folder/'calls.jsonl'
    lock=ROOT/'results/model-run.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
    start=time.monotonic()
    try:
        previous=[json.loads(l) for l in trace.read_text(encoding='utf-8').splitlines()] if trace.exists() else []
        if any(r['status']!='ok' or r.get('model_calls')!=1 for r in previous):raise RuntimeError('Prior failure; no retries allowed')
        if len({r['id'] for r in previous})!=len(previous):raise RuntimeError('Duplicate trace')
        done={r['id'] for r in previous}
        if not done <= {r['id'] for r in rows}:raise RuntimeError('Unknown prior call')
        run_manifest=folder/'manifest.json'
        identity=dict(freeze=manifest,code_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),config=config)
        if run_manifest.exists() and json.loads(run_manifest.read_text(encoding='utf-8'))!=identity:raise RuntimeError('Prior run identity differs')
        if not run_manifest.exists():run_manifest.write_text(json.dumps(identity,indent=2),encoding='utf-8')
        import torch
        from transformers import AutoTokenizer,AutoModelForCausalLM,BitsAndBytesConfig
        torch.manual_seed(45);random.seed(45)
        model_dir=ROOT/'models/tiny-aya-global'
        tokenizer=AutoTokenizer.from_pretrained(model_dir,local_files_only=True)
        quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
        model=AutoModelForCausalLM.from_pretrained(model_dir,local_files_only=True,trust_remote_code=False,quantization_config=quant,dtype=torch.bfloat16,device_map={'':0},attn_implementation='eager');model.eval()
        block=0
        for row in rows:
            if row['id'] in done:continue
            if block>=a.max_calls or time.monotonic()-start>=a.max_minutes*60:break
            if len(previous)+block>=96:raise RuntimeError('Actual budget exhausted')
            record=dict(id=row['id'],status='error',model_calls=0,messages=row['messages'])
            try:
                tokens=tokenizer.apply_chat_template(row['messages'],tokenize=True,add_generation_prompt=True,return_dict=True,return_tensors='pt').to(model.device)
                # Persist attempted generation before calling the backend. Interrupted attempts cannot retry.
                record['model_calls']=1
                with trace.open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n');f.flush();os.fsync(f.fileno())
                started=time.monotonic()
                with torch.inference_mode():out=model.generate(**tokens,do_sample=False,max_new_tokens=160)
                raw=tokenizer.decode(out[0,tokens['input_ids'].shape[1]:],skip_special_tokens=True)
                record.update(status='ok',raw_output=raw,score=score(row,raw),elapsed_seconds=time.monotonic()-started,input_tokens=int(tokens['input_ids'].shape[1]),output_tokens=int(out.shape[1]-tokens['input_ids'].shape[1]))
                # Replace only this run's final provisional line, preserving all earlier attempts.
                lines=trace.read_text(encoding='utf-8').splitlines();lines[-1]=json.dumps(record)
                temporary=folder/'calls.pending'
                with temporary.open('w',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n');f.flush();os.fsync(f.fileno())
                os.replace(temporary,trace)
            except Exception:raise
            block+=1;print(row['id'],flush=True)
    finally:lock.unlink()
if __name__=='__main__':main()

