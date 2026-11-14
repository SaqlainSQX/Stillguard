# Improvement decision — 14 November 2026

Five fresh-context advisers inspected the submission and completed recommendations. These were improvement advisers, not a repeat scoring panel; no new judge score or probability is claimed.

| Adviser | Strongest proposal | Assessment |
|---|---|---|
| `/root/improve_science` | Independently authored two-domain transfer study | Strong scientific value, but requires independent human authors/reviewers not currently available. Solo AI-assisted writing cannot substitute for independent validation. |
| `/root/improve_product` | Reusable policy-change regression CLI | Feasible practical workflow; can expose permission regressions hidden by aggregate improvement. |
| `/root/improve_repair` | Separately frozen naturalness-matched archive diagnostic | Addresses the weak neutral control; needs new construction, preregistration and inference, with uncertain outcomes. Recommends CLI for reliable delivery. |
| `/root/improve_judge` | Transfer study with a thin regression CLI | Potentially stronger evidence, but recommends CLI fallback if second-domain labels cannot be convincingly verified. |
| `/root/improve_challenger` | Deployment-specific regression CLI | Prefer a genuine user-supplied workflow to another synthetic domain or post-hoc corrective search; insist on fail-closed input validation and explicit baseline quality. |

## Selected scope

Implement a CPU-only, saved-output policy-change check for the existing deployment contract. A user supplies trusted before/after formal policies, request facts, and two agents' saved proposals. Derive transition categories from the policies, independently rescore both proposal sets against the **current** policy, and report absolute candidate quality as well as paired regressions. Input identity and complete coverage are mandatory. An explicit fixture-level budget controls the CI exit status.

This turns the observed aggregate-versus-adaptation tradeoff into a reusable engineering check. It does not add model generalization evidence, repair model weights, establish production readiness, or demonstrate arbitrary-domain support. A passing check applies only to the supplied finite fixture and declared budget. Policy authoring and fact collection remain trusted work.

Two new policy transitions and their scripted output sets are integration examples, **not model generations or new benchmark results**. A separate read-only export demonstrates the tool on every saved HC/P1 pair in heldout-001. That demonstration is retrospective; its release budgets are illustrative and were not preregistered for the original study. No held-out prompts, parsers, labels, scores or generation settings are tuned.

## Acceptance criteria

- Aggregate correctness can improve while lost newly allowed successes still fail the check.
- All-withhold fails usefulness and all-deploy fails safety under the strict example budget.
- Malformed proposals remain incorrect with unknown violation status; target substitutions remain visible.
- Missing/duplicate outputs, stale contract fingerprints and invalid budgets cannot produce a passing report.
- Baseline defects remain visible; no-regression does not excuse an unacceptable candidate.
- Identical inputs yield deterministic reports; all four transition slices include denominators.
- Original frozen audit files remain byte-identical, and the existing independent 600-call scorer replay still passes.

The selected work primarily addresses practical impact and communication. It does not resolve the single-model/domain limitations or guarantee a higher jury score. New research remains a separate prospective decision.

## Observed implementation result

The actual saved HC-to-P1 comparison reproduced 45/120 to 71/120 correct, with newly allowed completion 11/20 to 5/20. Pairwise analysis identifies 36 gained correct decisions, 10 lost allowed successes (six newly allowed), six newly introduced known unsafe proposals, and four newly invalid outputs. Aggregate reductions can therefore conceal individual regressions in both safety and usefulness. The default check correctly exits 1. These are descriptive reanalyses of the same 120 paired cases, not new independent evidence.

All eight scripted integration requests behave as documented: 3/8 to 6/8 accuracy with two lost new permissions fails; the authored 8/8 candidate passes. Missing responses exit 2 and replace a stale passing artifact with an error report. All-withhold, all-deploy and unchanged bad baselines fail absolute quality checks. Partial coverage requires an explicit recorded waiver.

Full implementation verification: 117 tests passed, including strict input/budget validation, revision consistency, scope binding, deterministic artifacts, markup isolation, CI exit codes and source-export alignment. An isolated Python `-I -S` export independently replayed all 600 original scores without installed packages or weights. Sixteen original frozen audit files retain their recorded SHA256 hashes. See [the saved actual-result report](../experiments/regression-001/REPORT.md) and [verification/provenance](../experiments/regression-001/verification.json).
