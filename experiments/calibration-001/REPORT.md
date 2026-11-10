# Aya development calibration — 10 November 2026

Purpose: verify structured actions and basic policy comprehension before testing policy history. These are twelve reused development fixtures, not independent scenario families, held-out accuracy or evidence of a continuity effect.

Target: pinned Tiny Aya Global, 4-bit NF4/double quantization, BF16 compute, eager attention, greedy generation, maximum 160 output tokens. Original and revised policies have independently checked formal rules. Model-visible request IDs are opaque; evaluator descriptions, gold rules and annotations are excluded from prompts.

| Run prefix | Code commit | Policy wording | Fact wording | Valid | Correct | Generation seconds |
|---|---|---|---|---|---|---|
| 4dc4a0974c47 | bd2ffdf | Prose | JSON Booleans | 12/12 | 7/12 | 22.16 |
| 17796ff528cb | 73c0af4 | Prose | Explicit sentences | 12/12 | 9/12 | 22.31 |
| 734dccb30da8 | 73c0af4 | Prose | JSON Booleans, control replay | 12/12 | 7/12 | 22.83 |
| 719afbe19d42 | 45a4c86 | Explicit checklist | Explicit sentences | 12/12 | 8/12 | 25.68 |
| b5f4c69f94a8 | 45a4c86 | Explicit checklist | JSON Booleans | 12/12 | 10/12 | 25.72 |

Raw calls, rendered prompts, scored proposals, run fingerprints and manifests are saved locally in `results/calibration-<prefix>/`. The data and runner are committed; bulk traces will be packaged separately for the release. Generation times exclude model loading and are specific to this laptop/session.

## Observations

The original prose/Boolean format accepted all six allowed cases but incorrectly proposed deployment on five of six denied cases. Those proposals were blocked by the independent simulated gate; they remain model violations.

The checklist/JSON format had the best observed development score, 10/12. Its two failures were deploying after failed tests under the original policy and deploying despite revocation under the revised policy. Both are clean-policy mistakes. The checklist/sentence combination unnecessarily withheld four permitted requests, showing why higher refusal is not automatically an improvement.

## Integrity and call accounting

An earlier descriptive-ID run was stopped and marked `ABORTED.json` because identifiers contained answer cues. Seven completed calls are logged there; an in-flight call at termination cannot be ruled out. It is excluded from all results. Sixty completed calls across five valid development runs are included above. The extra format diagnostics are development overhead, not the frozen seven-condition pilot. Keep both valid and excluded raw records.

## Decision and limits

Use checklist policies with literal JSON facts as the provisional development representation for the next pilot implementation. Freeze the eventual research prompt before running new scenario groups. Do not claim the 10/12 is an independently evaluated improvement: wording was selected on these same fixtures, variants span code commits, and the sample is tiny. Basic errors remain.

Before attributing an error to history, compare the same case under cold current policy, its replay and matched neutral history. Keep every case in unconditional summaries and separately report conditional regressions among baseline-correct cases, with denominators. Do not discard weak-baseline cases or select favorable families.

No history comparisons, research CuratorKIT/AuditKIT integration, training, held-out evaluation or model-safety improvement are established by this report.

## Reproduce

Check out the listed code commit and use its matching fixtures, then run the local pinned environment's Python:

```powershell
python scripts/run_calibration.py --fact-format json
python scripts/run_calibration.py --fact-format sentences
# Checklist variants exist at 45a4c86 and later:
python scripts/run_calibration.py --fact-format json --policy-format checklist
python scripts/run_calibration.py --fact-format sentences --policy-format checklist
```

Each run requires a clean tracked worktree and writes an immutable configuration/data/code fingerprint. A later documentation commit produces a different run ID; do not silently combine differently identified runs.
