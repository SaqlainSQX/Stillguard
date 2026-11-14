# Stillguard task board

Updated 14 November 2026. Original finish target: **12 November IST**, with 13–14 November reserved as buffer. The owner authorized a further five-adviser improvement review and implementation on 14 November. See `../PLAN.md` for acceptance criteria and branch rules.

| ID | Deliverable | Depends on | Status |
|---|---|---|---|
| S0 | Model/environment/toolkit setup and GitHub repository | — | Done; setup evidence only |
| P0 | Execution plan, gates and decision journal | S0 | Done; maintained through public release |
| T1 | Policy/state/action schemas and independent oracle | P0 | Done for bounded deployment contract v1 |
| T2 | Mock tool simulator and deterministic scorer | T1 | Done; proposal and gateway scored separately |
| T3 | Hand-checked fixtures and focused scorer tests | T2 | Done; 12 development fixtures; full suite now 91 passing tests |
| T4 | Resumable Aya runner and 12-call calibration | T3 | Done, with limitations: five development runs; best 10/12 correct; see calibration report |
| T5 | Six-group discovery data, real CuratorKIT export and frozen manifest | T3,T4 | Done: 36 cases, 252 frozen inputs, exact HC/NC matching; see DISCOVERY_DATA.md |
| T6 | Actual AuditKIT baseline sweep and confirmation panel | T5 | Done: 252 discovery + 216 confirmation calls; every score independently replayed |
| G1 | Gate A evidence review and continue/reframe decision | T6 | Done: two reproducible groups, below three-group gate; narrow scope per D010 |
| T7 | Simple mitigation and equal-budget comparison | G1 | Done: 108 verified calls; reminder rejected; retain current-policy-only architecture per D013 |
| T8 | Tiny adaptation compatibility test and one training run | T7 | Deferred; outside the default three-day plan |
| T9 | New grouped held-out evaluation and one ablation | T7 | Done: 600/600 calls, zero failures; all strict/payload scores replayed; full tradeoff report complete |
| T10 | Lightweight actual-run report/demo and reproducibility check | T9 | Done: all 30 preselected h01 responses exported; HTML and tradeoff chart visually checked |
| T11 | HF artifacts/collections, report and submission package | T9,T10 | Done: public HF bundle/collections, anonymous full replay, clean source reproduction and viewer/client checks; owner review/form submission remain |
| T12 | Five-adviser improvement decision and usable policy-change CI check | T11, owner request | Done: saved-output CLI, two authored integration transitions, independently verified actual HC/P1 replay, 117 passing tests; frozen audit unchanged; see IMPROVEMENT_001.md |

Do not mark research stages complete from generated code alone. Completion requires their observable output and acceptance checks.

Post-review transfer extension (14 November): owner approved AI-authored fictional scenarios; 96/96 new calls completed, but every response failed strict output formatting. Retained as a failed appendix in experiments/transfer-001/REPORT.md, not successful cross-domain validation. Original heldout unchanged; 121 tests pass. No rescue tuning or further inference.

Completed ahead of 12 November: all required implementation/evaluation/release milestones. Optional T8 training was intentionally dropped. No submission form has been sent.

Original milestones: T1–T6 and G1 on 10 November; T7 plus frozen T9 data/config and draft release material on 11 November; final T9–T11 by 12 November. If a milestone slips, drop optional scope and preserve the scoring controls.
