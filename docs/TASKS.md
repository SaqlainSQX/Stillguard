# Stillguard task board

Updated 9 November 2026. See `../PLAN.md` for acceptance criteria and branch rules.

| ID | Deliverable | Depends on | Status |
|---|---|---|---|
| S0 | Model/environment/toolkit setup and GitHub repository | — | Done; setup evidence only |
| P0 | Execution plan, gates and decision journal | S0 | Prepared |
| T1 | Policy/state/action schemas and independent oracle | P0 | Next |
| T2 | Mock tool simulator and deterministic scorer | T1 | Pending |
| T3 | Hand-checked fixtures and focused scorer tests | T2 | Pending |
| T4 | Resumable Aya runner and 12-call calibration | T3 | Pending |
| T5 | Six-group discovery data, real CuratorKIT export and frozen manifest | T3,T4 | Pending |
| T6 | Actual AuditKIT baseline sweep and confirmation panel | T5 | Pending |
| G1 | Gate A evidence review and continue/reframe decision | T6 | Pending |
| T7 | Simple mitigation and equal-budget comparison | G1 | Conditional |
| T8 | Tiny adaptation compatibility test and one training run | T7 | Optional, evidence-dependent |
| T9 | New grouped held-out evaluation and one ablation | T7 | Pending |
| T10 | Actual-run comparison viewer and reproducibility check | T9 | Pending |
| T11 | HF artifacts/collections, report and submission package | T9,T10 | Pending |

Do not mark research stages complete from generated code alone. Completion requires their observable output and acceptance checks.
