"""Render the preselected h01 actual-response demo, only after complete scoring."""
from pathlib import Path
import argparse,html,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))


def render_demo(group,rows,manifest):
    if group['group_id']!='h01' or len(rows)!=30:
        raise ValueError('Use every response from preselected h01 only')
    lookup={(r['case_id'],r['condition']):r for r in rows}
    esc=lambda value:html.escape(str(value),quote=True)
    sections=[]
    for case in group['cases']:
        records=[]
        for condition in ('P1','P1R','H','HC','NC'):
            record=lookup[case['case_id'],condition];score=record['score'];payload=record['payload_sensitivity']
            records.append('<tr><td>'+esc(condition)+'</td><td>'+esc(score['proposed_action'] or 'invalid / unknown')+
                '</td><td>'+esc(score['decision_correct'])+'</td><td>'+esc(score['proposal_violation'])+
                '</td><td>'+esc(score['gate']['reason'])+'</td><td>'+esc(payload['proposed_action'] or 'invalid / unknown')+
                '</td><td><details><summary>Raw response</summary><pre>'+esc(record['raw_output'])+'</pre></details></td></tr>')
        sections.append('<section><h2>'+esc(case['case_id'])+' — '+esc(case['kind'])+'</h2><p>Expected current action: <strong>'+
            esc(case['expected_after'])+'</strong></p><details><summary>Trusted request and state</summary><pre>'+
            esc(json.dumps(case['context'],indent=2))+'</pre></details><div class="scroll"><table><thead><tr><th>Condition</th>'+
            '<th>Strict proposal</th><th>Correct</th><th>Known unsafe</th><th>Actual gate reason</th><th>Payload after optional fence removal</th>'+
            '<th>Unedited model output</th></tr></thead><tbody>'+''.join(records)+'</tbody></table></div></section>')
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+
        '<title>Stillguard — preselected held-out demo</title><style>body{font:16px system-ui,sans-serif;max-width:1250px;margin:40px auto;padding:0 24px;color:#17212b;background:#f7f9fb}section{background:white;border:1px solid #d9e1e8;border-radius:8px;padding:20px;margin:24px 0}th,td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #dde3e9}th{background:#edf2f7}table{border-collapse:collapse;width:100%}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-width:700px;font-size:13px}.scroll{overflow-x:auto}summary{cursor:pointer}code{overflow-wrap:anywhere}</style><body>'+
        '<h1>Stillguard: one preselected held-out group</h1><p>All six h01 requests and all five conditions are shown. '+
        'This group was selected before any held-out outputs. Responses are saved actual model generations, not scripted examples. '+
        'All actions are simulated; no real deployment occurs.</p>'+
        '<p>Run: <code>'+esc(manifest['run_id'])+'</code></p><p>P1/P1R: current-policy-only action context and fresh replay. '+
        'H: original plus verified amendment. HC: current policy plus obsolete archive. NC: current policy plus token/position-matched neutral archive.</p>'+
        '<p>Invalid outputs have unknown violation status and are rejected by the actual strict gate. The payload view is hypothetical exact-fence removal; it never changes actual gate behavior. '+
        'This fictional group is not independent real-world safety evidence.</p><section><h2>Original policy</h2><p>'+esc(group['before']['policy_text'])+
        '</p><h2>Current policy</h2><p>'+esc(group['after']['policy_text'])+'</p></section>'+''.join(sections)+'</body></html>')


if __name__=='__main__':
    from analyze_heldout import load_complete
    parser=argparse.ArgumentParser();parser.add_argument('--run',required=True)
    parser.add_argument('--source',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();manifest,summary,records,rows=load_complete(args.run)
    import hashlib
    if hashlib.sha256(Path(args.source).read_bytes()).hexdigest()!=manifest['source_sha256']:
        raise ValueError('Demo source digest mismatch')
    groups=json.loads(Path(args.source).read_text())
    group=next(g for g in groups if g['group_id']=='h01')
    Path(args.output).write_text(render_demo(group,[r for r in rows if r['group_id']=='h01'],manifest),encoding='utf-8')
