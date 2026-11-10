import copy,importlib.util,json
from pathlib import Path
import pytest
from stillguard.final_data import validate_final_inputs

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture
def rows():
    path=ROOT/'data/curated/heldout-001/inputs.jsonl'
    if not path.exists():pytest.skip('Build final CuratorKIT inputs first')
    return list(map(json.loads,path.read_text().splitlines()))


def runner():
    spec=importlib.util.spec_from_file_location('heldout_runner',ROOT/'scripts/run_heldout.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_complete_final_grid_and_fixed_schedule(rows):
    assert validate_final_inputs(rows)['inputs']==600
    module=runner()
    assert module.schedule(rows)==module.schedule(rows)
    assert len({job['row']['id'] for job in module.schedule(rows)})==600
    with pytest.raises(ValueError):module.schedule(rows[:-1])


@pytest.mark.parametrize('corruption',['missing','replay','position','state','label','identity'])
def test_bad_final_controls_rejected(rows,corruption):
    if corruption=='missing':rows.pop()
    if corruption=='replay':next(r for r in rows if r['condition']=='P1R')['messages'][0]['content']+=' changed'
    if corruption=='position':next(r for r in rows if r['condition']=='NC')['matching']['request_prefix_tokens']+=1
    if corruption=='state':next(r for r in rows if r['condition']=='HC')['context']['facts']['tests_passed']=False
    if corruption=='label':rows[0]['expected_action']='withhold' if rows[0]['expected_action']=='deploy' else 'deploy'
    if corruption=='identity':rows[0]['id']='other'
    with pytest.raises(ValueError):validate_final_inputs(rows)


def test_actual_pinned_tokenizer_final_positions(rows):
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(ROOT/'models/tiny-aya-global',local_files_only=True)
    assert validate_final_inputs(rows,tokenizer)['cases']==120


def test_failed_generations_share_global_budget_across_execution_versions(tmp_path):
    for name,dataset,calls in [('a','same',[1,1]),('b','same',[1,0]),('c','other',[1])]:
        folder=tmp_path/('heldout-'+name);folder.mkdir()
        (folder/'manifest.json').write_text(json.dumps(dict(dataset_sha256=dataset)))
        (folder/'calls.jsonl').write_text('\n'.join(json.dumps(dict(status='error',model_calls=n)) for n in calls))
    assert runner().prior_generation_count(tmp_path,'same')==3
