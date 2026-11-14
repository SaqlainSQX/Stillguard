"""Export verified saved generations as a retrospective regression illustration."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_heldout import verify_final
from analyze_heldout import load_complete
from stillguard.schema import Policy, Context


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def export(inputs, source, run, output_dir):
    inputs, source, run, output = map(Path, (inputs, source, run, output_dir))
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError('Output directory must be new or empty')
    verification = verify_final(inputs, run)
    manifest, _, _, rows = load_complete(run)
    if file_hash(source) != manifest['source_sha256']:
        raise ValueError('Source digest mismatch')
    frozen = [json.loads(line) for line in inputs.read_text(encoding='utf-8').splitlines()]
    lookup = {(r['case_id'], r['condition']): r for r in frozen}
    if len(lookup) != 600 or len(frozen) != 600:
        raise ValueError('Duplicate or incomplete frozen inputs')
    cases = []
    for group in json.loads(source.read_text(encoding='utf-8')):
        policies = {name: {k: v for k, v in group[name].items() if k != 'policy_text'} for name in ('before', 'after')}
        before, after = (Policy.from_dict(policies[name]) for name in ('before', 'after'))
        for case in group['cases']:
            case_id = case['case_id']
            context = Context.from_dict(case['context'])
            for name, policy in (('before', before), ('after', after)):
                expected = 'deploy' if policy.allows(context) else 'withhold'
                if case['expected_' + name] != expected:
                    raise ValueError('Source label disagrees with oracle')
            for condition in ('P1', 'P1R', 'H', 'HC', 'NC'):
                row = lookup[case_id, condition]
                if row['context'] != case['context'] or row['evaluator_policy'] != policies['after']:
                    raise ValueError('Source/frozen input alignment mismatch')
            cases.append(dict(case_id=case_id, before_policy=policies['before'], after_policy=policies['after'], context=case['context']))
    ids = {c['case_id'] for c in cases}
    if len(cases) != 120 or len(ids) != 120 or ids != {r['case_id'] for r in frozen}:
        raise ValueError('Source cases must uniquely cover all frozen inputs')
    contract = dict(schema_version=1, cases=sorted(cases, key=lambda c: c['case_id']))
    contract_hash = digest(contract)
    artifacts = {'contract.json': contract}
    for label, condition in (('baseline', 'HC'), ('candidate', 'P1')):
        selected = [dict(case_id=r['case_id'], raw_output=r['raw_output']) for r in rows if r['condition'] == condition]
        if len(selected) != 120 or {r['case_id'] for r in selected} != ids:
            raise ValueError('Output alignment mismatch')
        artifacts[label + '.json'] = dict(schema_version=1, contract_sha256=contract_hash, records=sorted(selected, key=lambda r: r['case_id']))
    provenance = dict(schema_version=1, description='Retrospective illustration; zero new model calls; not new validation.', chosen_conditions=dict(baseline='HC', candidate='P1'), verification=verification, contract_sha256=contract_hash, input_sha256=file_hash(inputs), source_sha256=file_hash(source), run_file_sha256={p.name: file_hash(p) for p in sorted(run.iterdir()) if p.is_file()})
    artifacts['provenance.json'] = provenance
    output.mkdir(parents=True, exist_ok=True)
    for name, value in artifacts.items():
        with (output / name).open('x', encoding='utf-8') as handle:
            handle.write(json.dumps(value, indent=2) + '\n')
    return provenance


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('inputs', 'source', 'run', 'output-dir'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    export(args.inputs, args.source, args.run, args.output_dir)
