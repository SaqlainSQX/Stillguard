import copy,json
from pathlib import Path
import pytest
from stillguard.discovery import source_groups,validate_groups,render_condition


def test_all_source_rules_annotations_and_balance():
    groups=source_groups();validate_groups(groups)
    assert len({c['context']['request_id'] for g in groups for c in g['cases']})==36
    assert {g['structural_cluster'] for g in groups}=={'window_change','approval_change','revocation_change','test_change'}


def test_bad_annotations_and_unverified_amendments_fail_closed():
    groups=source_groups();groups[0]['cases'][0]['expected_before']='invalid'
    with pytest.raises(ValueError):validate_groups(groups)
    group=source_groups()[0];group['amendment']['verified_by_harness']=False
    with pytest.raises(ValueError):render_condition(group,group['cases'][0],'H')


def test_replays_are_identical_and_gold_does_not_enter_prompt():
    for group in source_groups():
        for case in group['cases']:
            assert render_condition(group,case,'P0')[0]==render_condition(group,case,'P0R')[0]
            assert render_condition(group,case,'P1')[0]==render_condition(group,case,'P1R')[0]
            changed=copy.deepcopy(case);changed['expected_after']='SECRET_GOLD_CANARY'
            changed['case_id']='SECRET_CASE_CANARY';changed['kind']='SECRET_KIND_CANARY'
            rendered=json.dumps(render_condition(group,changed,'H')[0])
            assert all(x not in rendered for x in ('SECRET_GOLD_CANARY','SECRET_CASE_CANARY','SECRET_KIND_CANARY','expected_before','expected_after','"rule"'))


def test_real_pinned_tokenizer_matches_history_and_request_position():
    root=Path(__file__).resolve().parents[1]
    if not (root/'models/tiny-aya-global/tokenizer.json').exists():pytest.skip('Local gated tokenizer not downloaded')
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(root/'models/tiny-aya-global',local_files_only=True)
    for group in source_groups():
        case=group['cases'][0]
        hc,hm=render_condition(group,case,'HC',tokenizer)
        nc,nm=render_condition(group,case,'NC',tokenizer)
        assert hc[0]==nc[0] and hc[-1]==nc[-1]
        assert hm==nm
        assert len(tokenizer.apply_chat_template(hc,tokenize=True,add_generation_prompt=True))==len(tokenizer.apply_chat_template(nc,tokenize=True,add_generation_prompt=True))


def test_frozen_artifact_keeps_every_case_and_control():
    import hashlib
    root=Path(__file__).resolve().parents[1]
    path=root/'data/curated/pilot-001/inputs.jsonl'
    if not path.exists():pytest.skip('Run scripts/build_pilot.py to build pinned inputs')
    manifest=json.loads((root/'manifests/pilot-data.json').read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['input_sha256']
    assert hashlib.sha256((root/manifest['source_path']).read_bytes()).hexdigest()==manifest['source_sha256']
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    assert len(rows)==252 and len({r['id'] for r in rows})==252
    cases={}
    for row in rows:
        cases.setdefault(row['case_id'],{})[row['condition']]=row
        rendered=json.dumps(row['messages'])
        assert all(name not in rendered for name in ('expected_before','expected_after','expected_action','evaluator_policy','"rule"'))
        assert row['case_id'] not in rendered
    assert len(cases)==36
    for conditions in cases.values():
        assert conditions['P0']['messages']==conditions['P0R']['messages']
        assert conditions['P1']['messages']==conditions['P1R']['messages']
        hc,nc=conditions['HC'],conditions['NC']
        assert hc['messages'][0]==nc['messages'][0] and hc['messages'][-1]==nc['messages'][-1]
        assert hc['matching']==nc['matching']
        assert len({json.dumps(v['context'],sort_keys=True) for v in conditions.values()})==1
