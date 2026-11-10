"""Frozen final CuratorKIT-derived evaluation -> Aya -> AuditKIT."""
from pathlib import Path
from dataclasses import asdict
import argparse,hashlib,json,os,random,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
os.environ.setdefault('XDG_CACHE_HOME',str(ROOT/'.cache'))
os.environ.setdefault('HF_HUB_OFFLINE','1')
os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY','1')
from stillguard.audit import evaluate_one
from stillguard.schema import Policy,Context
from stillguard.scoring import score_output
from stillguard.final_data import validate_final_inputs
from stillguard.diagnostics import payload_sensitivity


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def execution_hash():
    files=sorted((ROOT/'src/stillguard').glob('*.py'))+[Path(__file__),ROOT/'configs/heldout.yaml',ROOT/'configs/model-lock.json',ROOT/'configs/action.schema.json']
    hashes={str(p.relative_to(ROOT)):sha(p) for p in files}
    return hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()


def schedule(rows):
    jobs=[dict(row=r,repeat=0) for r in rows]
    random.Random(45).shuffle(jobs)
    if len(jobs)!=600 or len({j['row']['id'] for j in jobs})!=600:
        raise ValueError('Frozen heldout schedule size mismatch')
    return jobs


def prior_generation_count(results, dataset_sha256):
    total=0
    for previous in Path(results).glob('heldout-*'):
        manifest=previous/'manifest.json';trace=previous/'calls.jsonl'
        if not (manifest.exists() and trace.exists()):continue
        if json.loads(manifest.read_text()).get('dataset_sha256')!=dataset_sha256:continue
        total+=sum(json.loads(line).get('model_calls',0) for line in trace.read_text().splitlines())
    return total


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--max-calls',type=int,default=600)
    parser.add_argument('--max-minutes',type=float,default=35)
    args=parser.parse_args()
    if args.max_calls<1 or not 0<args.max_minutes<=35:raise ValueError('Invalid work-block budget')
    import yaml,torch
    from transformers import AutoModelForCausalLM,AutoTokenizer,BitsAndBytesConfig
    if git('status','--porcelain'):raise RuntimeError('Commit all tracked work and freeze inputs before a scored run')
    config=yaml.safe_load((ROOT/'configs/heldout.yaml').read_text())
    data=json.loads((ROOT/'manifests/heldout-data.json').read_text())
    path=ROOT/data['input_path']
    if sha(path)!=data['input_sha256'] or sha(ROOT/data['source_path'])!=data['source_sha256']:
        raise RuntimeError('Frozen data changed')
    if sha(ROOT/'scripts/build_heldout.py')!=data['generator_sha256'] or sha(ROOT/'src/stillguard/discovery.py')!=data['discovery_module_sha256'] or sha(ROOT/'src/stillguard/final_data.py')!=data['validation_module_sha256']:
        raise RuntimeError('Rebuild and refreeze inputs after generator changes')
    if sha(ROOT/'manifests/heldout-source.json')!=data['source_manifest_sha256']:
        raise RuntimeError('Parent curation manifest changed')
    source_manifest=json.loads((ROOT/'manifests/heldout-source.json').read_text())
    if sha(ROOT/'src/stillguard/heldout.py')!=source_manifest['authoring_module_sha256']:
        raise RuntimeError('Frozen held-out authoring module changed')
    lock_model=json.loads((ROOT/'configs/model-lock.json').read_text())
    if data['tokenizer_revision']!=lock_model['revision'] or config['model']['revision']!=lock_model['revision']:
        raise RuntimeError('Model/tokenizer revision mismatch')
    downloaded=json.loads((ROOT/'manifests/model.json').read_text())
    if not downloaded.get('complete') or downloaded['revision']!=lock_model['revision']:raise RuntimeError('Model not ready')
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    validate_final_inputs(rows)
    jobs=schedule(rows)
    identity=dict(kind='final_heldout_evaluation',phase='heldout',execution_sha256=execution_hash(),
                  dataset_sha256=data['input_sha256'],source_sha256=data['source_sha256'],
                  config_sha256=sha(ROOT/'configs/heldout.yaml'),model_revision=lock_model['revision'],
                  seed=45,torch_version=torch.__version__,generation=config['generation'])
    run_id=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    folder=ROOT/'results'/('heldout-'+run_id[:12]);folder.mkdir(parents=True,exist_ok=True)
    lock=ROOT/'results/model-run.lock'
    try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:raise RuntimeError('Another model run owns results/model-run.lock')
    with os.fdopen(fd,'w') as f:json.dump(dict(pid=os.getpid(),run=str(folder)),f)
    start_block=time.perf_counter()
    try:
        manifest=folder/'manifest.json'
        if not manifest.exists():manifest.write_text(json.dumps(dict(identity,run_id=run_id,initial_code_commit=git('rev-parse','HEAD'),data_manifest=data),indent=2),encoding='utf-8')
        trace=folder/'calls.jsonl'
        records=[json.loads(line) for line in trace.read_text().splitlines()] if trace.exists() else []
        done={r['call_key'] for r in records if r['status']=='ok'}
        total_failures=0
        for previous in (ROOT/'results').glob('heldout-*'):
            pm=previous/'manifest.json';pt=previous/'calls.jsonl'
            if pm.exists() and pt.exists() and json.loads(pm.read_text()).get('dataset_sha256')==identity['dataset_sha256']:
                total_failures+=sum(json.loads(line)['status']=='error' for line in pt.read_text().splitlines())
        if total_failures>=config['budget']['max_failed_call_retries']:raise RuntimeError('Shared failed-call budget exhausted')
        prior_calls=prior_generation_count(ROOT/'results',identity['dataset_sha256'])
        if not torch.cuda.is_available():raise RuntimeError('CUDA unavailable')
        torch.manual_seed(45)
        model_dir=ROOT/config['model']['local_path']
        tokenizer=AutoTokenizer.from_pretrained(model_dir,local_files_only=True)
        quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
        model=AutoModelForCausalLM.from_pretrained(model_dir,local_files_only=True,trust_remote_code=False,
             quantization_config=quant,dtype=torch.bfloat16,device_map={'':0},attn_implementation='eager')
        model.eval()
        block_calls=0
        for job in jobs:
            row=job['row'];key=row['id']+'-repeat'+str(job['repeat'])
            if key in done:continue
            if block_calls>=args.max_calls or time.perf_counter()-start_block>=args.max_minutes*60:break
            if prior_calls+block_calls>=config['budget']['max_actual_generations']:
                raise RuntimeError('Shared 620-generation held-out budget exhausted')
            attempt=sum(r['call_key']==key for r in records)
            record=dict(call_key=key,attempt=attempt,status='error',code_commit=git('rev-parse','HEAD'),
                case_id=row['case_id'],group_id=row['group_id'],structural_cluster=row['structural_cluster'],
                kind=row['kind'],condition=row['condition'],repeat=job['repeat'],
                messages=row['messages'],context=row['context'],expected_action=row['expected_action'])
            observed={'calls':0}
            def adapter(prompts):
                if len(prompts)!=1:raise RuntimeError('Only one model request per audit invocation is allowed')
                messages=json.loads(prompts[0])
                if messages!=row['messages']:raise RuntimeError('Audit adapter changed the model input')
                if observed['calls']>=1:raise RuntimeError('Unexpected implicit generation retry')
                inputs=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,return_dict=True,return_tensors='pt').to(model.device)
                if inputs['input_ids'].shape[1]!=row['input_tokens']:raise RuntimeError('Frozen token count changed')
                record.update(input_tokens=row['input_tokens'],rendered_prompt=tokenizer.decode(inputs['input_ids'][0]))
                torch.cuda.synchronize();start=time.perf_counter()
                observed['calls']+=1
                with torch.inference_mode():output=model.generate(**inputs,do_sample=False,max_new_tokens=config['generation']['max_new_tokens'])
                torch.cuda.synchronize()
                tokens=output[0,inputs['input_ids'].shape[1]:]
                raw=tokenizer.decode(tokens,skip_special_tokens=True)
                record.update(raw_output=raw,output_tokens=int(tokens.shape[0]),elapsed_seconds=time.perf_counter()-start)
                return [raw]
            try:
                audit=evaluate_one(row,adapter,run_id,key+'-attempt'+str(attempt))
                if observed['calls']!=1:raise RuntimeError('A control replay was cached instead of generated')
                score=score_output(Policy.from_dict(row['evaluator_policy']),Context.from_dict(row['context']),record['raw_output'])
                if audit.headline['decision_correct']!=float(score.decision_correct):raise RuntimeError('Audit/direct scorer disagreement')
                record.update(status='ok',score=asdict(score),audit_headline=audit.headline,model_calls=observed['calls'])
                record['payload_sensitivity']=payload_sensitivity(Policy.from_dict(row['evaluator_policy']),Context.from_dict(row['context']),record['raw_output'])
            except Exception as error:
                record.update(error_type=type(error).__name__,error=str(error)[:500],model_calls=observed['calls'])
                with trace.open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n');f.flush();os.fsync(f.fileno())
                raise
            with trace.open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n');f.flush();os.fsync(f.fileno())
            records.append(record);done.add(key);block_calls+=1
            print(len(done),'/',len(jobs),key,'correct='+str(score.decision_correct),flush=True)
        successful=[r for r in records if r['status']=='ok']
        summary=dict(run_id=run_id,phase='heldout',planned_calls=len(jobs),completed=len(done),complete=len(done)==len(jobs),
            failed_calls=sum(r['status']=='error' for r in records),
            generation_seconds=sum(r['elapsed_seconds'] for r in successful),peak_cuda_bytes=torch.cuda.max_memory_allocated(),
            current_code_commit=git('rev-parse','HEAD'),working_tree_clean=not bool(git('status','--porcelain')))
        if not summary['working_tree_clean']:summary['needs_integrity_review']=True
        (folder/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        print(json.dumps(dict(folder=str(folder),**summary),indent=2),flush=True)
    finally:lock.unlink()


if __name__=='__main__':main()
