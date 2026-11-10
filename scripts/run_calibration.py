"""Resumable local Aya calibration on development fixtures, not a research audit."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
os.environ.setdefault('XDG_CACHE_HOME', str(ROOT/'.cache'))
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY', '1')
from stillguard.schema import Policy, Context
from stillguard.prompts import make_messages
from stillguard.scoring import score_output


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import yaml
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git','status','--porcelain'], cwd=ROOT, text=True).strip()
    if dirty: raise RuntimeError('Commit tracked work before scored calibration; working tree is dirty.')
    config = yaml.safe_load((ROOT/'configs/pilot.yaml').read_text())
    model_lock = json.loads((ROOT/'configs/model-lock.json').read_text())
    status = json.loads((ROOT/'manifests/model.json').read_text())
    if not status.get('complete') or status['revision'] != model_lock['revision']:
        raise RuntimeError('Pinned model download is incomplete or mismatched')
    if config['model']['revision'] != model_lock['revision']:
        raise RuntimeError('Pilot and model lock disagree')
    policies_path = ROOT/'data/raw/calibration-policies.json'
    cases_path = ROOT/'data/raw/calibration.jsonl'
    policies = json.loads(policies_path.read_text())
    cases = [json.loads(line) for line in cases_path.read_text().splitlines()]
    if len(cases) != 12 or len({c['id'] for c in cases}) != 12:
        raise RuntimeError('Calibration requires twelve unique development cases')
    manifest = dict(kind='development_calibration_only', code_commit=commit,
                    model_revision=model_lock['revision'], config_sha256=sha(ROOT/'configs/pilot.yaml'),
                    cases_sha256=sha(cases_path), policies_sha256=sha(policies_path),
                    generation=config['generation'], quantization=config['model'], seed=42,
                    torch_version=torch.__version__, max_successful_calls=12, max_failed_calls=20)
    fingerprint = hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    folder = ROOT/'results'/('calibration-'+fingerprint[:12]); folder.mkdir(parents=True,exist_ok=True)
    # Cross-run GPU lock: never overlap two calibration processes.
    lock = ROOT/'results/model-run.lock'
    try:
        fd = os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:
        raise RuntimeError('Another model run owns results/model-run.lock; inspect it before resuming.')
    with os.fdopen(fd,'w') as f: json.dump({'pid':os.getpid(),'run':str(folder)},f)
    try:
        (folder/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        trace = folder/'calls.jsonl'
        records = [json.loads(line) for line in trace.read_text().splitlines()] if trace.exists() else []
        done = {r['case_id'] for r in records if r['status']=='ok'}
        if sum(r['status']=='error' for r in records) >= 20:
            raise RuntimeError('Calibration failed-call budget exhausted')
        if not torch.cuda.is_available(): raise RuntimeError('CUDA unavailable')
        torch.manual_seed(42)
        tokenizer = AutoTokenizer.from_pretrained(ROOT/config['model']['local_path'],local_files_only=True)
        quant = BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',
                                  bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
        model = AutoModelForCausalLM.from_pretrained(ROOT/config['model']['local_path'],local_files_only=True,
                    trust_remote_code=False,quantization_config=quant,dtype=torch.bfloat16,
                    device_map={'':0},attn_implementation='eager')
        model.eval()
        for case in cases:
            if case['id'] in done: continue
            record = policies[case['policy_revision']]
            policy = Policy.from_dict({k:v for k,v in record.items() if k!='policy_text'})
            context = Context.from_dict(case['context'])
            messages = make_messages(record['policy_text'],context)
            inputs = tokenizer.apply_chat_template(messages,add_generation_prompt=True,tokenize=True,
                            return_dict=True,return_tensors='pt').to(model.device)
            start = time.perf_counter()
            row = dict(case_id=case['id'],status='error',messages=messages,
                       rendered_prompt=tokenizer.decode(inputs['input_ids'][0]),
                       input_tokens=int(inputs['input_ids'].shape[1]))
            try:
                torch.cuda.synchronize()
                start = time.perf_counter()
                with torch.inference_mode():
                    output = model.generate(**inputs,do_sample=False,max_new_tokens=config['generation']['max_new_tokens'])
                torch.cuda.synchronize()
                elapsed = time.perf_counter()-start
                generated = output[0,inputs['input_ids'].shape[1]:]
                raw = tokenizer.decode(generated,skip_special_tokens=True)
                score = score_output(policy,context,raw)
                row.update(status='ok',raw_output=raw,elapsed_seconds=elapsed,
                           output_tokens=int(generated.shape[0]),score=asdict(score))
            except Exception as error:
                row.update(error_type=type(error).__name__,error=str(error)[:500],elapsed_seconds=time.perf_counter()-start)
                with trace.open('a',encoding='utf-8') as f:
                    f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
                raise
            with trace.open('a',encoding='utf-8') as f:
                f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
            records.append(row)
            print(case['id'], 'valid='+str(score.output_valid), 'correct='+str(score.decision_correct),
                  'seconds='+str(round(elapsed,2)),flush=True)
        successes = [r for r in records if r['status']=='ok']
        report = dict(kind='development_calibration_only',run_id=fingerprint,code_commit=commit,
                      cases=len(successes),valid=sum(r['score']['output_valid'] for r in successes),
                      correct=sum(r['score']['decision_correct'] for r in successes),
                      elapsed_generation_seconds=sum(r['elapsed_seconds'] for r in successes),
                      peak_cuda_bytes=torch.cuda.max_memory_allocated(),
                      failed_calls=sum(r['status']=='error' for r in records),
                      policy_history_experiment=False)
        (folder/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps({'folder':str(folder),**report},indent=2),flush=True)
    finally:
        lock.unlink()


if __name__=='__main__': main()
