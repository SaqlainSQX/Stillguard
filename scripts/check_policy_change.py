"""Run offline regression checks, without model calls or deployment."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from stillguard.regression import load_json, validate_contract, evaluate


def markdown(report):
    """Readable outcome; raw untrusted responses remain in the JSON artifact."""
    esc = lambda value: html.escape(str(value), quote=True).replace('|', '&#124;').replace('\n', ' ')
    lines = ['# Policy change check', '', '**Status: ' + esc(report['status']) + '**', '']
    if 'aggregate' not in report:
        lines += [esc(report.get('error', report.get('warning', ''))), '']
        return '\n'.join(lines)
    lines += [report['warning'], '', 'Both output sets are scored against the current policy.', '',
              '| Transition | Baseline correct / n | Candidate correct / n | Baseline unsafe / unknown | Candidate unsafe / unknown |',
              '|---|---:|---:|---:|---:|']
    for label, scores in [('All requests', report['aggregate']), *report['slices'].items()]:
        b, c = scores['baseline'], scores['candidate']
        lines.append(f"| {esc(label)} | {b['correct']}/{b['n']} | {c['correct']}/{c['n']} | {b['unsafe']} / {b['unknown_violation_status']} | {c['unsafe']} / {c['unknown_violation_status']} |")
    lines += ['', '## Paired changes', '']
    lines += ['- ' + esc(key) + ': **' + str(value) + '**' for key, value in report['paired'].items()]
    lines += ['', 'Failed budgets: ' + (', '.join(report['failures']) or 'none') + '.',
              'Missing transitions: ' + (', '.join(report['missing_transitions']) or 'none') + '.',
              'Partial coverage explicitly allowed: ' + str(report['allow_partial_coverage']) + '.', '',
              '## Cases losing a legitimate allowed success', '']
    lost = [r for r in report['cases'] if r['after_allowed'] and r['baseline']['decision_correct'] and not r['candidate']['decision_correct']]
    lines += ['- ' + esc(r['case_id']) + ' (' + r['transition'] + ')' for r in lost] or ['None.']
    lines += ['', '## Effective budgets', '', '```json', json.dumps(report['budgets'], indent=2, sort_keys=True), '```', '',
              'Contract SHA256: `' + report['contract_sha256'] + '`.', '',
              'The companion JSON preserves every raw response, context, policy, score and source-file hash.', '']
    return '\n'.join(lines)

def atomic(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.regression-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream: stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('contract','baseline','candidate','output','markdown','budgets'): parser.add_argument('--'+name, required=name=='contract')
    parser.add_argument('--validate-only', action='store_true')
    parser.add_argument('--allow-partial-coverage', action='store_true')
    args = parser.parse_args()
    inputs = [Path(p).resolve() for p in (args.contract, args.baseline, args.candidate, args.budgets) if p]
    destinations = [Path(p).resolve() for p in (args.output, args.markdown) if p]
    if len(set(destinations)) != len(destinations) or any(p in inputs for p in destinations):
        print('Report paths must differ from input files and from each other.', file=sys.stderr)
        return 2
    try:
        contract = load_json(args.contract)
        digest, _ = validate_contract(contract)
        if args.validate_only:
            report = dict(status='validated', contract_sha256=digest, warning='Contract validation only; no outputs evaluated.')
        else:
            if not all((args.baseline,args.candidate,args.output)): raise ValueError('--baseline, --candidate and --output required')
            report = evaluate(contract, load_json(args.baseline), load_json(args.candidate), load_json(args.budgets) if args.budgets else None, args.allow_partial_coverage)
        report['source_file_sha256'] = {name: hashlib.sha256(Path(path).read_bytes()).hexdigest()
            for name, path in [('contract', args.contract), ('baseline', args.baseline), ('candidate', args.candidate), ('budgets', args.budgets)] if path}
    except (ValueError, TypeError, KeyError, OSError, RecursionError) as error:
        report = dict(status='error', error=str(error))
    rendered = json.dumps(report, indent=2, sort_keys=True)
    try:
        if args.output: atomic(args.output, rendered+'\n')
        if args.markdown: atomic(args.markdown, markdown(report))
    except OSError as error:
        print('Report write failed: '+str(error), file=sys.stderr)
        return 2
    print(json.dumps({k:v for k,v in report.items() if k != 'cases'}, sort_keys=True))
    return 0 if report['status'] in ('pass','validated') else 1 if report['status']=='fail' else 2

if __name__ == '__main__': raise SystemExit(main())
