"""Prepare an allowlisted local HF dataset bundle; never uploads or copies weights."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
RUN_FILES=('manifest.json','summary.json','calls.jsonl','EXCLUDED.json','ABORTED.json')


def copy_inside(root,source,destination):
    root=Path(root).resolve();source=Path(source)
    if source.is_symlink():raise ValueError('Do not package symlinked artifacts')
    source=source.resolve()
    if not source.is_relative_to(root):raise ValueError('Artifact source escapes project root')
    relative=source.relative_to(root)
    if any(part in {'.git','.aws','.codex','.cache','.venv','models','downloads','tools'} for part in relative.parts):
        raise ValueError('Private/runtime paths are excluded from artifacts')
    if source.name.startswith('.env') or source.name in {'token','stored_tokens','credentials'} or source.suffix in {'.safetensors','.bin','.pt','.pth','.gguf','.whl'}:
        raise ValueError('Credentials/weights/packages are excluded from artifacts')
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,destination)


def export_cases(groups,split):
    result=[]
    for group in groups:
        for case in group['cases']:
            context=case['context']
            result.append(dict(case_id=case['case_id'],group_id=group['group_id'],split=split,
                structural_component=group['structural_cluster'],kind=case['kind'],
                before_policy=group['before']['policy_text'],current_policy=group['after']['policy_text'],
                amendment=group['amendment']['text'],request_id=context['request_id'],
                workspace_id=context['workspace_id'],resource_id=context['resource_id'],
                environment=context['environment'],facts=context['facts'],
                expected_before=case['expected_before'],expected_current=case['expected_after'],
                before_rule_json=json.dumps(group['before']['rule'],sort_keys=True),
                current_rule_json=json.dumps(group['after']['rule'],sort_keys=True),
                design_json=json.dumps(group.get('design',{}),sort_keys=True)))
    return result


def export_calls(manifest,rows):
    result=[]
    for row in rows:
        score=row['score'];payload=row.get('payload_sensitivity',{})
        result.append(dict(run_id=manifest['run_id'],phase=manifest['phase'],call_key=row['call_key'],
            case_id=row['case_id'],group_id=row['group_id'],condition=row['condition'],kind=row['kind'],
            expected_action=row['expected_action'],raw_output=row['raw_output'],
            messages_json=json.dumps(row['messages']),context_json=json.dumps(row['context']),
            input_tokens=row['input_tokens'],output_tokens=row['output_tokens'],elapsed_seconds=row['elapsed_seconds'],
            model_calls=row['model_calls'],code_commit=row['code_commit'],model_revision=manifest['model_revision'],
            output_valid=score['output_valid'],decision_correct=score['decision_correct'],
            proposed_action=score['proposed_action'],proposal_violation=score['proposal_violation'],
            target_matches=score['target_matches'],unnecessary_withhold=score['unnecessary_withhold'],
            gate_executed=score['gate']['executed'],gate_reason=score['gate']['reason'],
            payload_outer_fence_removed=payload.get('outer_fence_removed'),payload_valid=payload.get('output_valid'),
            payload_correct=payload.get('decision_correct'),payload_proposal_violation=payload.get('proposal_violation')))
    return result


def write_jsonl(path,rows):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(row)+'\n' for row in rows),encoding='utf-8',newline='\n')


def copy_runs(root,out):
    copied=[]
    for pattern in ('calibration-*','pilot-*','reminder-*','heldout-*'):
        for folder in sorted((Path(root)/'results').glob(pattern)):
            if not folder.is_dir() or not (folder/'manifest.json').exists():continue
            for name in RUN_FILES:
                source=folder/name
                if source.exists():
                    target=Path(out)/'provenance/runs'/folder.name/name
                    copy_inside(root,source,target);copied.append(str(target.relative_to(out)))
    return copied


def build(root,run,out):
    from analyze_heldout import load_complete
    from verify_heldout import verify_final
    root=Path(root).resolve();run=Path(run).resolve();out=Path(out).resolve()
    if not run.is_relative_to(root/'results') or not out.is_relative_to(root/'results'):
        raise ValueError('Use project-local results paths')
    if out.exists() and any(out.iterdir()):raise ValueError('Use a new empty release directory')
    manifest,summary,records,rows=load_complete(run)
    inputs=root/manifest['data_manifest']['input_path']
    verification=verify_final(inputs,run)
    # Card/results/demo must be concrete and reviewed before packaging; no fake placeholders.
    required=['docs/DATASET_CARD.md','experiments/heldout-001/REPORT.md',
              'experiments/heldout-001/summary.json','experiments/heldout-001/verification.json',
              'experiments/heldout-001/demo.html']
    for path in required:
        if not (root/path).is_file():raise ValueError('Missing release artifact: '+path)
    report=json.loads((root/'experiments/heldout-001/summary.json').read_text())
    checked=json.loads((root/'experiments/heldout-001/verification.json').read_text())
    if report['run_id']!=manifest['run_id'] or checked['verified_calls']!=600 or checked['dataset_sha256']!=manifest['dataset_sha256']:
        raise ValueError('Reviewed report/verification does not match the release run')
    if subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip():
        raise ValueError('Commit reviewed release material first')
    out.mkdir(parents=True,exist_ok=True)
    copy_inside(root,root/'docs/DATASET_CARD.md',out/'README.md')
    for source,split in [('discovery-groups.json','development'),('heldout-groups.json','heldout')]:
        groups=json.loads((root/'data/raw'/source).read_text())
        write_jsonl(out/'data'/(split+'_cases.jsonl'),export_cases(groups,split))
    write_jsonl(out/'data/heldout_calls.jsonl',export_calls(manifest,rows))
    copy_runs(root,out)
    for name in ('LICENSE','THIRD_PARTY_NOTICES.md'):
        copy_inside(root,root/name,out/name)
    for path in ['data/raw/calibration.jsonl','data/raw/calibration-policies.json',
                 'data/raw/discovery-groups.json','data/raw/heldout-groups.json',
                 'manifests/model-lock.json','configs/model-lock.json']:
        if (root/path).is_file():copy_inside(root,root/path,out/'provenance'/path)
    for path in sorted((root/'manifests').glob('*data.json')):
        copy_inside(root,path,out/'provenance/manifests'/path.name)
    for name in ('heldout-source.json','assets.json'):
        if (root/'manifests'/name).is_file():copy_inside(root,root/'manifests'/name,out/'provenance/manifests'/name)
    for name in ('pilot','reminder','heldout'):
        copy_inside(root,root/'configs'/(name+'.yaml'),out/'provenance/configs'/(name+'.yaml'))
        copy_inside(root,root/'data/curated'/(name+'-001')/'inputs.jsonl',out/'provenance/inputs'/(name+'.jsonl'))
    copy_inside(root,root/'configs/action.schema.json',out/'provenance/configs/action.schema.json')
    copy_inside(root,root/'requirements.lock.txt',out/'provenance/requirements.lock.txt')
    for path in required[1:]:copy_inside(root,root/path,out/'report'/Path(path).name)
    for name in ('tradeoffs.png','tradeoffs.svg'):
        copy_inside(root,root/'experiments/heldout-001'/name,out/'report'/name)
    for phase in ('pilot','reminder'):
        copy_inside(root,root/'experiments'/(phase+'-001')/'REPORT.md',out/'report'/(phase+'-REPORT.md'))
    files={path.relative_to(out).as_posix():hashlib.sha256(path.read_bytes()).hexdigest()
           for path in sorted(out.rglob('*')) if path.is_file()}
    release=dict(kind='stillguard_local_release_bundle',uploaded=False,run_id=manifest['run_id'],
                 code_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
                 final_verified_calls=verification['verified_calls'],files=files,
                 exclusions=['credentials','model weights','environments','package archives','downloaded third-party sources'])
    (out/'release-manifest.json').write_text(json.dumps(release,indent=2)+'\n',encoding='utf-8',newline='\n')
    return dict(directory=str(out),files=len(files)+1,verified_final_calls=verification['verified_calls'],uploaded=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args();print(json.dumps(build(ROOT,args.run,args.out),indent=2))
