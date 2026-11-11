import importlib.util,json
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('release_builder',Path(__file__).resolve().parents[1]/'scripts/build_release.py')
release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)


@pytest.mark.parametrize('relative',['.env','models/model.safetensors','.cache/token','downloads/package.whl','.aws/credentials'])
def test_credentials_weights_and_caches_cannot_be_packaged(tmp_path,relative):
    root=tmp_path/'project';source=root/relative;source.parent.mkdir(parents=True,exist_ok=True);source.write_text('DO_NOT_COPY')
    with pytest.raises(ValueError):release.copy_inside(root,source,tmp_path/'bundle'/'data')
    assert not (tmp_path/'bundle'/'data').exists()


def test_run_copy_is_allowlisted_and_root_bound(tmp_path):
    root=tmp_path/'project';folder=root/'results/heldout-test';folder.mkdir(parents=True)
    for name in ('manifest.json','calls.jsonl','summary.json','.env','model.safetensors'):(folder/name).write_text('{}')
    out=tmp_path/'bundle';copied=release.copy_runs(root,out)
    assert len(copied)==3
    assert not list(out.rglob('.env')) and not list(out.rglob('*.safetensors'))
    external=tmp_path/'outside.json';external.write_text('{}')
    with pytest.raises(ValueError):release.copy_inside(root,external,out/'outside.json')


def test_case_export_round_trips_rule_and_labels_without_recursive_viewer_schema():
    from stillguard.discovery import source_groups
    group=source_groups()[0];rows=release.export_cases([group],'development')
    assert len(rows)==6
    assert json.loads(rows[0]['before_rule_json'])==group['before']['rule']
    assert rows[0]['expected_current']==group['cases'][0]['expected_after']
    assert 'rule' not in rows[0] and rows[0]['facts']==group['cases'][0]['context']['facts']
