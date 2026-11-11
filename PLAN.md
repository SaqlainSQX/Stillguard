# Stillguard execution plan

Prepared 9 November; revised 10 November 2026. User target: finish by 12 November IST. Evidence-driven plan; no pilot result is assumed.

## Objective and current state

Build a reproducible audit of whether a small Aya agent preserves unchanged safeguards while adapting to legitimate policy updates. Deliver a useful dataset, an actual CuratorKIT-to-AuditKIT model pipeline, measured mitigation tradeoffs, and inspectable transcripts.

Verified as of 10 November: official pinned local model/environment, independent oracle/scorer/gate, real CuratorKIT-to-Aya-to-AuditKIT pipeline, 468 pilot calls, 108 reminder-development calls and 84 tests. The pilot gate failed (two reproducible groups, threshold three); the reminder was rejected. Retain the simpler current-policy-only architecture and publish its limits. New 20-group/120-probe held-out raw source is frozen before final selection. Final input/config/runner freeze is complete; actual held-out scoring and release packaging remain pending. See the experiment reports and task board.

The evidence-driven narrowing decision is recorded in D010â€“D013. Eleven proposal reviews were design work; claims now follow saved model outputs and controls, including null and failed results.

Official submission deadline: 14 November, end of day AoE. The working deadline is now **12 November IST for the complete submission-ready package**. Keep 13â€“14 November as buffer, not planned development time. Source: https://hackathon.lexsi.ai/#submit (checked 9 November).

## Revised three-day critical path

| Date (IST) | Required output | Decision / scope control |
|---|---|---|
| 10 November | Verified oracle/scorer, runnable Aya pilot, actual baseline traces and Gate A decision | Stop speculative planning; make the continue/reframe choice today. If full confirmation cannot finish, report the incomplete gate and finish it first on 11 November. No mitigation claims from an incomplete pilot. |
| 11 November | Selected simple mitigation, real CuratorKIT/AuditKIT integration, reviewed held-out data and frozen evaluation configuration | Freeze the method and core features by day's end. Training is outside the default plan. |
| 12 November | Held-out evaluation, reproducibility check, concise actual-run demo/report, HF artifacts and submission text/links | Finish the complete reviewable package. Reduce presentation polish before dropping evaluation controls. |
| 13â€“14 November | Reserved buffer and submission | Only correctness fixes, access checks and submission handling; no planned new research. |

Default deliverable: one model, one domain, two genuinely integrated track repositories, a controlled benchmark, one simple mitigation comparison and reproducible traces. Adapter training, a third toolkit, multilingual work and a full dashboard are excluded from the critical path. If measured runtime exceeds the budget, reduce evaluation breadth before launching the frozen test and disclose the smaller scope; never select cases by favorable test outcomes.

## Fixed operating rules

1. Start with one target model and one fictional deployment-policy domain. No real deployment actions.
2. Authenticate policy updates in application code. A model does not decide whether text is authoritative.
3. Gold expected decisions and gold policy ASTs are evaluator-only; never include them in model prompts or mitigation inputs.
4. Separate unchanged-safeguard violations, failures to adopt a valid change, malformed outputs, pre-existing errors, and gateway-blocked proposals.
5. A policy-history effect requires matched authoritative current-policy controls. An amendment-only versus full-policy difference is a representation/deployment result.
6. Freeze datasets, prompts, scoring and model settings before each named evaluation. Later changes start a new run; keep old results.
7. Count model calls, input/output tokens, retries, rejected outputs and runtime. Start with microbatch one and resumable per-call JSONL logs.
8. Use development cases to improve methods. Never tune on the final held-out evaluation.
9. Allow a cheap baseline to win. No compulsory fine-tuning, third toolkit or new algorithm.
10. Preserve useful allowed behavior. Blocking all actions is not a successful mitigation.

## Stage 1 â€” trustworthy task and scorer

Target: first 2â€“3 working hours on 10 November; estimates are planning bounds, not promises.

Actions:

- [x] Define a small policy AST and explicit policy/state/request schemas, including scope and revision IDs.
- [x] Write a deterministic finite-domain evaluator independently of the language model.
- [x] Define a mock action proposal schema and a separate execution gate. Score the proposal and final simulated outcome separately.
- [x] Hand-check allowed/denied boundary cases, negation, exceptions and unrelated updates. Check that applying an amendment preserves all intended invariants in gold.
- [x] Write meaningful tests: exhaustive small-state oracle checks, counterfactual pairs, malformed action rejection, and gold-exclusion checks on assembled prompts.
- [x] Author a dozen calibration requests, including allowed tasks. These are development fixtures, not held-out evidence.

Outputs: `src/stillguard/` schemas, oracle, simulator and scorer; `tests/`; `data/raw/` calibration fixtures; a documented action contract.

Exit gate: a model-independent hand-labeled fixture set agrees with the scorer; intentionally wrong and malformed proposals are detected. If this fails, fix the oracle before any research claims or expensive model runs.

## Stage 2 â€” actual Aya runner and frozen discovery pilot

Target: next 2â€“4 working hours on 10 November. First measure real latency on 12 calibration calls; estimate the remaining budget from that measurement. The pilot and gate have priority over every optional component.

Actions:

- [x] Implement a local-files-only Aya runner using the pinned checkpoint, NF4 settings, eager attention and fixed generation settings.
- [x] Save actual rendered messages, token counts, output, parse status, latency, condition, scenario group, model revision, seed/settings, Git commit and config/dataset hashes.
- [x] Confirm that the schema is usable on both allowed and denied calibration requests. Repair a formatting/interface problem before treating output failures as safety violations.
- [x] Author six distinct scenario groups with six probes each: two unchanged allowed requests, two unchanged denied requests and two intended-change requests. Balance newly allowed/newly denied behavior across the pilot, and include useful allowed work in every group. Vary rule structure and amendment scope, not just names or numeric values.
- [x] Pass these through a real CuratorKIT validation/deduplication/export step. Preserve distinct condition variants and group IDs; deduplication must not erase counterfactual pairs.
- [x] Freeze the discovery dataset, prompt templates, scorer and generation configuration. Assign every run a content-derived ID.
- [x] Use AuditKIT with the real Aya adapter and task-specific scoring, retaining raw per-case traces. The previous lookup fixture is not this integration.

### Seven discovery conditions

| ID | Condition | Purpose |
|---|---|---|
| P0 | Cold original policy | Original task ability |
| P0R | Identical original-policy replay | No-change variability |
| P1 | Cold canonical current policy | Current task ability |
| P1R | Identical current-policy replay | Current-policy variability |
| H | Original policy plus authenticated amendment history | Realistic reconstruction/deployment condition |
| HC | Canonical current policy plus explicitly obsolete policy/update history | Residual history interference |
| NC | Identical canonical current policy plus neutral history | Length/position/content control |

In HC and NC, the current authoritative instruction must be identical. Match token counts and request positions, record any mismatch, and keep request facts/tool state identical. Neutral histories must contain no conflicting policy instructions. H must explicitly authorize ordered amendments in the application-supplied instruction; do not ask a lower-authority message to override an immutable system policy.

Initial sweep: 6 groups Ã— 6 probes Ã— 7 conditions = 252 calls. Predefine a confirmation panel of 3 probes per group (one unchanged allowed, one unchanged denied, one intended change) and repeat P1/H/HC/NC three times: 216 calls. With 12 calibration calls, the intended first-pass budget is 480 calls. Reserve at most 20 failed-call retries; record every retry. Use fixed primary decoding; repeated runs measure serving variability, not independent scenario evidence.

If measured latency makes 480 calls infeasible, reduce confirmation breadth before launching it, record the protocol change and retain all conditions for the selected groups. Do not remove the strongest baseline or confirm only the failures that look interesting.

Outputs: frozen pilot manifest, actual model JSONL traces, scorer output and `experiments/pilot-001/REPORT.md`.

## Gate A â€” decide the direction from the pilot

Review every apparent violation, its clean counterpart, its current-policy counterpart, and its no-change/control behavior. Report unconditional error rates as well as conditional regressions among previously correct requests.

| Observation | Interpretation | Action |
|---|---|---|
| HC fails unchanged safeguards more consistently than P1/NC, across several scenario groups | Candidate residual continuity problem | Continue the continuity thesis; test a targeted mitigation |
| H fails, but HC and P1 work | Policy reconstruction/representation weakness | Reframe as an architectural refresh result; drop claims of residual interference and skip unnecessary training |
| P1 already fails the task | Basic policy-following or interface problem | Diagnose on development cases with a 90-minute repair cap; do not label it update-induced |
| Differences are comparable to unchanged replays or disappear under length/position controls | Inconclusive or confounded effect | Do not claim a continuity failure; run one bounded diagnostic follow-up or change the question |
| All conditions work reliably at the tested scale | Informative null result | Stop the proposed failure claim; do not add arbitrary distracting context just to force a headline |
| Candidate mitigation blocks intended new permissions | Safety/usefulness failure | Reject or revise the mitigation |

A provisional engineering signal for proceeding is a reviewed effect in at least three of the six scenario groups, reproduced in at least two of three confirmation runs, beyond matched-control behavior. This is a triage rule, not a significance threshold, independence guarantee or proof of generality. Report actual counts even when the rule is not met.

Write the gate decision in `docs/DECISIONS.md`: observed evidence, limits, selected branch, rejected interpretation and next budget. No automatic scope expansion.

## Stage 3 â€” the smallest useful intervention

Target: 11 November, conditional on Gate A.

- [x] Compare current-policy refresh with one local authoritative-policy reminder (full prose, not a learned invariant extractor); reject it on development outcomes.
- [x] Include a token/position-matched generic reminder; disclose its repetitive padding and failed strict formatting control. Do not claim policy-specific safety from its zero primary accuracy.
- [x] Report cost/usefulness tradeoffs with the same request groups, settings and action gate, plus a separately labeled exploratory exact-fence sensitivity check.
- [ ] Defer adaptation from the default plan. Consider a tiny compatibility/VRAM check only if all core development outputs are already complete with time remaining before the 11 November feature freeze.
- [ ] If that optional training branch proceeds, compare base versus adapted Aya under an identical harness; include equal-sized generic replay data. Use training/development groups only. It must not delay the frozen evaluation or 12 November delivery.
- [ ] Keep SafeTune optional; add it only if a specific supported intervention is already demonstrated active and the core two-repository deliverable is complete.

Exit gate: the intervention reduces reviewed failures while retaining intended behavior. The earlier target of halving violations with at most five percentage points lost in intended-update completion is an engineering ambition, not a result or an acceptable substitute for reporting raw counts and uncertainty.

Stop optional training if compatibility cannot be established in two working hours or one short job produces no development benefit. Keep a working audit/architectural result rather than depending on a training rescue.

## Stage 4 â€” independent evaluation and robustness

Target: prepare and freeze on 11 November; execute the final evaluation on 12 November.

- [ ] Author a new held-out set targeting at least 20 distinct scenario groups, with grouped paraphrases and update sequences. Freeze it before method selection is finalized.
- [ ] Check test wording for ambiguity and independently verify gold policy transitions. Clearly label synthetic scope.
- [ ] Select one method using development data, then run the frozen test once. If a scorer bug is discovered, version the fix, explain it and rerun all affected methods.
- [ ] Include legitimate broadening, new restrictions/revocation, narrow exceptions and unrelated amendments. Any expiry case uses explicit simulated time, not the machine clock.
- [ ] Perform one meaningful ablation tied to the claimed mechanism; avoid a broad method grid.
- [ ] Report paired counts, family/group-level uncertainty, refusal/invalid-output rates, legitimate task success, costs and limitations. Do not treat paraphrases or repeated decoding as independent families.
- [ ] Keep unsuccessful attacks and null results in the report, not just the best transcript.

Exit gate: all headline numbers trace to saved runs; a clean rerun reproduces representative outputs within disclosed variability; a model-written explanation is not presented as causal evidence.

## Stage 5 â€” usable demonstration and release package

Target: draft report/artifact metadata alongside development on 11 November; complete the entire release package on 12 November. Prioritize this over optional training and features.

- [ ] Produce a compact comparison report over actual saved runs: policy, amendment, still-applicable safeguard, model proposal, expected action and intervention outcome. A saved HTML or terminal report is sufficient; no full dashboard is required.
- [ ] Use a held-out group selected without seeing its outputs. Present both a legitimate allowed update and safeguard checks. Do not script a fake faulty model answer.
- [ ] Prepare a public benchmark/data card, run logs, model/configuration references, and any adapter actually produced on Hugging Face. Organize the required public collections and verify access before submission.
- [ ] Write the article/README with exact scope, prior work, rationale, multiple before/after metrics, failed approaches, compute cost and reproduction commands.
- [ ] Verify the contribution uses at least two Track 2 repositories in a real pipeline. Imports and fixture scores do not count as research integrations.
- [ ] Prepare the under-500-word abstract and submission links. Check current form requirements and latest event announcements.

Feature/method freeze: end of 11 November IST, before held-out scoring. Submission-ready package: 12 November IST. Keep 13â€“14 November for buffer, access/correctness checks and submission; do not allocate new research to that buffer.

## Steering rules when progress deteriorates

| Trigger | Immediate response | Work we keep |
|---|---|---|
| Oracle or parser gives inconsistent labels | Pause model comparisons, fix scorer and replay all affected runs | Fixtures, schema, audit tests |
| GPU OOM or throughput too low | Microbatch one, shorter declared context budget, sequential resumable runs; use available cloud only after a smoke test | Same prompts/cases/scoring; record backend/precision changes |
| No trustworthy residual continuity effect | Narrow to the observed representation/refresh result, or run one adjacent update-aware audit grounded in actual failures | Simulator, grouped data, runner, Curator/Audit integration |
| No informative weakness anywhere | Report the null; choose a new bounded question using observed outputs, with a fresh protocol, rather than imply success | Reusable benchmark and negative findings |
| Mitigation succeeds only by denying work | Compare at comparable legitimate task completion or reject it | Raw traces, false-positive analysis |
| Proposed mechanism adds no value beyond a simple baseline | Use the simple baseline and revise the contribution claim | Useful engineering result and artifact |
| Training/install research consumes the schedule | Drop that branch; keep measured prompt/state mitigation | Audit and deployable configuration |
| By 11 November the core runner or evaluation is behind schedule | Stop training, extra methods and presentation features; finish the controlled audit and report | A coherent smaller submission by 12 November |

At most one major thesis pivot, decided from the 10 November pilot with a bounded diagnostic budget. Each pivot must name the failed assumption, an observed alternative failure, a falsifiable replacement question, a maximum exploration budget and the required reused components. If evidence is delayed into 11 November, narrow the existing audit rather than restart. No speculative circuit discovery, RLHF, multilingual expansion or multi-agent system on the critical path.

## Git and experiment discipline

Small commits after coherent milestones: task contract, scorer tests, frozen pilot, runner, baseline audit, gate decision, mitigation, held-out audit, release package. Push completed milestones using the established repository workflow.

Never commit credentials, original model weights, environments or bulk traces. Keep reviewed summaries in Git and full artifacts on HF. A run stores the code commit/config/data hashes; evaluation IDs must not depend on mutable branch names. Commit before a scored run and record any dirty state as a run-invalidating condition until explained.

After every work block, update the task board and a short decision log: completed output, new evidence, unresolved risk, next action and why. Failed gates change the plan explicitly. They do not become excuses to delete results or quietly redefine success.

## Immediate next action

Stages 1â€“3 and Gate A are complete as of 10 November: 468 verified pilot calls, 108 verified reminder-development calls and 84 tests. The original three-group gate failed; the reminder was rejected. Preserve these outcomes and use the simpler current-policy-only action context as the architectural reference.

Next bounded milestone: complete the matching frozen P1/P1R/H/HC/NC run over all 600 inputs using `scripts/run_heldout.py` in sequential bounded blocks. Full CuratorKIT preservation, tokenizer matching, final config/runner freeze and 84 tests are complete (D014; experiments/heldout-001/FREEZE.md). Keep the 620-actual-generation cap including logged failures, shared GPU lock and independent scorer gate. Do not tune methods or analyze partial outcomes. After completion, replay all saved strict and payload-sensitivity scores, report every condition and build the preselected h01 actual-response demo plus release package. No new method search or training on the critical path.
