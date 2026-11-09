# Stillguard: pilot protocol

Question: does a legitimate policy update cause an Aya agent to violate safeguards that remain unchanged, and which inexpensive intervention preserves safety while allowing the intended new behavior?

Status: setup is verified; the research pilot has not run. Model-load and toolkit fixtures are not benchmark results.

## Initial scope

Six independent fictional deployment-policy families, with four unchanged-safeguard requests and two intended-change requests per family. An independently authored finite policy oracle supplies expected decisions. Tool execution is simulated.

Compare original policy, warm amendment history, cold canonical current policy, warm history plus canonical current-policy refresh, and repeated no-change controls. Hold request and simulator facts constant; match history length and position. When testing history interference, supply the identical current authoritative policy in warm and cold conditions. Amendment-only versus canonical-policy differences measure representation effects, not a specific internal mechanism.

Record unconditional safeguard violations, conditional regressions among previously correct cases, intended-update completion, invalid outputs, refusals, review requests, latency, token counts and tool proposals. Separate proposed violations from actions blocked by the tool gateway. Repeat a predefined confirmation panel and no-change controls to distinguish reproducible effects from serving variability.

Use canonical current-policy refresh as the strongest simple baseline. Test invariant reminders at a disclosed token/call budget. Add training only if reproducible residual failures justify it. Keep policy-family derivatives in one split and freeze held-out families before mitigation tuning. Report raw paired counts and family-level uncertainty.

CuratorKIT supplies traceable curation; AuditKIT evaluates the actual model pipeline. Optional toolkit source snapshots are references, not evidence of an implemented integration.

## Decision gate

Continue if real model failures survive matched-policy/history/no-change controls and an intervention improves safeguards while preserving legitimate adaptation. If simple refresh solves the issue, report that engineering result; do not manufacture a training contribution. A live or recorded demo must use actual model-generated proposals on a frozen held-out family.
