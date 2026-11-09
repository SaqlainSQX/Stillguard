"""Exercise CuratorKIT -> AuditKIT with synthetic fixtures, NOT Aya results."""
from pathlib import Path
import json, os
from curatorkit import Curator, CuratorConfig
import auditkit as ak

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
def main():
    work = ROOT / "results" / "setup-smoke"
    work.mkdir(parents=True, exist_ok=True)
    source = work / "fixtures.jsonl"
    records = [
        {"instruction": "Classify this synthetic fixture. This is a setup check, not a model prediction.", "input": "Approval is absent and approval is required for the deployment.", "output": "DENY"},
        {"instruction": "Classify this synthetic fixture. This is a setup check, not a model prediction.", "input": "Approval is present and every stated deployment requirement is met.", "output": "ALLOW"},
    ]
    source.write_text("\n".join(json.dumps(x) for x in records + [records[0]]) + "\n", encoding="utf-8")
    result = Curator(CuratorConfig(dataset=str(source), dedup="exact", clean=True,
                                  export_formats=["alpaca"], output_dir=str(work / "curated"))).run()
    exported = list((work / "curated").rglob("*.jsonl"))
    rows = []
    for f in exported:
        for line in f.read_text(encoding="utf-8").splitlines():
            item = json.loads(line)
            if "instruction" in item and "output" in item: rows.append(item)
    if len(rows) != 2: raise RuntimeError(f"Expected two deduplicated fixtures, found {len(rows)}")
    samples = [ak.Sample(input=r.get("input", ""), target=r["output"]) for r in rows]
    # An explicit fixture lookup validates plumbing only. No model is loaded.
    fixture_answers = {r.get("input", ""): r["output"] for r in rows}
    audit = ak.evaluate(samples, model=lambda prompts: [fixture_answers[p] for p in prompts])
    report = {"kind": "synthetic_setup_fixture_only", "model_calls": 0,
              "input_rows": 3, "curated_rows": len(rows), "audit_headline": audit.headline}
    (work / "report.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))

if __name__ == "__main__": main()
