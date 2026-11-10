# Stillguard task board

Updated 10 November 2026. Finish target: **12 November IST**, with 13–14 November reserved as buffer. See `../PLAN.md` for acceptance criteria and branch rules.

| ID | Deliverable | Depends on | Status |
|---|---|---|---|
| S0 | Model/environment/toolkit setup and GitHub repository | — | Done; setup evidence only |
| P0 | Execution plan, gates and decision journal | S0 | Prepared |
| T1 | Policy/state/action schemas and independent oracle | P0 | Done for bounded deployment contract v1 |
| T2 | Mock tool simulator and deterministic scorer | T1 | Done; proposal and gateway scored separately |
| T3 | Hand-checked fixtures and focused scorer tests | T2 | Done; 12 development fixtures and 32 passing tests |
| T4 | Resumable Aya runner and 12-call calibration | T3 | First valid run: 12/12 valid JSON, 7/12 correct; basic-task diagnostic in progress |
| T5 | Six-group discovery data, real CuratorKIT export and frozen manifest | T3,T4 | Pending |
| T6 | Actual AuditKIT baseline sweep and confirmation panel | T5 | Pending |
| G1 | Gate A evidence review and continue/reframe decision | T6 | Pending |
| T7 | Simple mitigation and equal-budget comparison | G1 | Conditional |
| T8 | Tiny adaptation compatibility test and one training run | T7 | Deferred; outside the default three-day plan |
| T9 | New grouped held-out evaluation and one ablation | T7 | Pending |
| T10 | Lightweight actual-run report/demo and reproducibility check | T9 | Pending |
| T11 | HF artifacts/collections, report and submission package | T9,T10 | Pending |

Do not mark research stages complete from generated code alone. Completion requires their observable output and acceptance checks.

Milestones: T1–T6 and G1 on 10 November; T7 plus frozen T9 data/config and draft release material on 11 November; final T9–T11 by 12 November. If a milestone slips, drop optional scope and preserve the scoring controls.
