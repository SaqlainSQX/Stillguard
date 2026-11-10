# Stillguard: pilot protocol

Question: does a legitimate policy update cause an Aya agent to violate safeguards that remain unchanged, and which inexpensive intervention preserves safety while allowing the intended new behavior?

Status: the 252-call discovery and 216-call confirmation phases are complete and independently verified. See [the pilot report](../experiments/pilot-001/REPORT.md). Two history-specific cases reproduced across three repeats, below the planned three-group gate; the next phase is a narrower interface/mitigation comparison. Model-load and toolkit fixtures remain separate from benchmark results.

## Initial scope

Six fictional deployment-policy scenario groups, each with two unchanged allowed requests, two unchanged denied requests and two intended-change requests. Balance newly allowed and newly denied cases across the pilot. An independently authored finite policy oracle supplies expected decisions. Tool execution is simulated.

Compare original policy and its replay, cold canonical current policy and its replay, warm amendment history, warm history plus canonical current-policy refresh, and canonical current policy plus neutral history. Hold request and simulator facts constant; match history length and position. When testing history interference, supply the identical current authoritative policy in the current-policy conditions. Amendment-only versus canonical-policy differences measure representation effects, not a specific internal mechanism.

The detailed execution sequence, call budgets, decision gates, fallback branches and delivery schedule are in [PLAN.md](../PLAN.md). The [task board](TASKS.md) records progress and the [decision journal](DECISIONS.md) records evidence behind changes of direction.

Record unconditional safeguard violations, conditional regressions among previously correct cases, intended-update completion, invalid outputs, refusals, review requests, latency, token counts and tool proposals. Separate proposed violations from actions blocked by the tool gateway. Repeat a predefined confirmation panel and no-change controls to distinguish reproducible effects from serving variability.

Use canonical current-policy refresh as the strongest simple baseline. Test invariant reminders at a disclosed token/call budget. Add training only if reproducible residual failures justify it. Keep policy-family derivatives in one split and freeze held-out families before mitigation tuning. Report raw paired counts and family-level uncertainty.

CuratorKIT supplies traceable curation; AuditKIT evaluates the actual model pipeline. Optional toolkit source snapshots are references, not evidence of an implemented integration.

## Decision gate

Continue if real model failures survive matched-policy/history/no-change controls and an intervention improves safeguards while preserving legitimate adaptation. If simple refresh solves the issue, report that engineering result; do not manufacture a training contribution. A live or recorded demo must use actual model-generated proposals on a frozen held-out family.
