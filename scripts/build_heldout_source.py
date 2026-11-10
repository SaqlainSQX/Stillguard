"""Freeze raw held-out rule compositions before final method selection."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from stillguard.heldout import heldout_groups,validate_heldout


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    groups=heldout_groups();checks=validate_heldout(groups)
    source=ROOT/'data/raw/heldout-groups.json'
    payload=(json.dumps(groups,indent=2)+'\n').encode()
    if source.exists() and source.read_bytes()!=payload:
        raise RuntimeError('Held-out source already exists with different contents; explicitly version a change')
    source.write_bytes(payload)
    manifest=dict(kind='frozen_heldout_source_only',source_path=str(source.relative_to(ROOT)),source_sha256=sha(source),
                  generator_sha256=sha(Path(__file__)),authoring_module_sha256=sha(ROOT/'src/stillguard/heldout.py'),
                  discovery_module_sha256=sha(ROOT/'src/stillguard/discovery.py'),
                  pilot_source_sha256=sha(ROOT/'data/raw/discovery-groups.json'),
                  calibration_source_sha256=sha(ROOT/'data/raw/calibration-policies.json'),
                  validation=checks,freeze_date_ist='2026-11-10',
                  scope='Twenty new policy compositions, 120 probes, three shared component templates; no model calls.',
                  status='Raw source frozen before final method selection. Curator export and final prompt/config freeze remain pending.',
                  caveats=['No independence or real-world representativeness claim.',
                           'Logical functions are disjoint from discovery and calibration policies; primitive facts and rule components are shared.',
                           'Within-group probes and policy components are dependent; intended-change probes may vary irrelevant facts.',
                           'Original and extension window flags are independent synthetic facts and may both be true.'])
    (ROOT/'manifests/heldout-source.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':main()
