# Stillguard decision journal

## D001 — 9 November 2026: freeze a bounded discovery-first plan

Evidence: pinned Tiny Aya downloaded, hashes verified, GPU generation and required imports passed; CuratorKIT/AuditKIT setup fixture passed. No policy-continuity model runs exist yet.

Decision: implement a verified scorer and a bounded seven-condition pilot before mitigation training or UI work. Treat canonical refresh as a strong baseline. Limit optional work and reserve release time.

Scope correction: add explicit original/current no-change replays and a neutral-history control to the earlier five-condition draft. A direct history-interference comparison must supply identical authoritative current policy and match history length/position. Amendment-only versus canonical-policy comparisons do not establish the same claim.

Next evidence required: model-independent scorer checks, measured calibration throughput and frozen pilot traces.

Gate status: not reached. No decision to continue the research thesis has been justified by experiments.

## D002 — 10 November 2026: finish by 12 November

User constraint: today is 10 November and the complete work should finish by 12 November, leaving buffer before the event deadline.

Decision: use a three-day critical path. Pilot and direction gate today; simple intervention, integration and evaluation freeze on 11 November; evaluation, reproducibility and full submission-ready package on 12 November. Reserve 13–14 November as buffer. Adapter training, a third toolkit and a full dashboard are not default deliverables. If evidence arrives late, narrow scope instead of launching another speculative thesis.

Evidence status unchanged: setup passed; no research pilot results exist. Dates are targets, not completed milestones or guarantees.

## D003 — 10 November 2026: start implementation and hourly continuation

Implemented the initial finite Boolean oracle, explicit missing-fact rejection and exact decision-change enumeration. Seven tests pass, including exhaustive deployment-window extension checks that preserve approval and tests, explicit revocation, and malformed rules. These are software correctness checks, not Aya safety results.

An hourly thread continuation was requested and configured. Each run must inspect current state, avoid overlapping work, respect all app/compute/access limits, checkpoint within 45 minutes, and disable further scheduling on completion or after 12 November IST. Scheduler availability and app usage limits still apply.

Next: complete policy/state/action schemas, strict mock proposal parsing and separate proposal/gateway scoring, then add fixtures and leakage checks before model calibration. Stage 1 is incomplete; Gate A has not been reached.

## D004 — 10 November 2026: Stage 1 software gate passes

Implemented strict immutable policy/context/proposal records, derived environment predicates, target binding, isolated mock gate receipts and separate proposal scoring. Invalid outputs remain unknown for violation scoring and incorrect for task correctness. The model cannot submit facts or approval changes. Scope mismatch stops evaluation.

Thirty-two tests pass, including independent truth-table expectations, twelve explicit development annotations (six deploy/six withhold), target substitution, malformed/duplicate-key JSON, current-revision rechecking and gold-input exclusion. These validate software behavior, not the continuity hypothesis.

Decision: proceed to the prepared resumable 12-call local Aya calibration. Do not begin history comparisons until formatting, task ability and throughput are reviewed. See ACTION_CONTRACT.md for exact initial scope and remaining controls.

Calibration integrity correction: the first preliminary launch exposed descriptive request IDs (including answer-like words). That process was stopped and its output marked ABORTED, excluded from all result claims. Retain its trace and account for logged/in-flight calls as setup overhead. Model-visible IDs are now opaque reqNNN values; descriptive case IDs remain evaluator-only. The fixture test guards this convention. Rerun calibration under the new dataset and code fingerprint.

## D005 — 10 November 2026: diagnose basic policy comprehension first

Valid development run `4dc4a0974c47` at code `bd2ffdf`: 12 calls, 12 valid proposals, 7 correct, no generation failures, about 22.16 seconds of generation, peak PyTorch CUDA allocation 2,686,910,464 bytes. All six allowed fixtures passed; five of six denied fixtures were incorrectly proposed for deployment. The mock gate blocked those violations. This is not a policy-history experiment.

Decision: hold the history pilot and take the planned bounded diagnostic branch. Compare literal Boolean facts with lossless factual sentence wording while preserving policies, trusted states and gold decisions. No examples or expected labels are added to model inputs. Record prompt-format variants under separate run fingerprints. Additional diagnostic calls count as development overhead, not part of the frozen research pilot budget. Keep all earlier traces, including the excluded preliminary run.

## Entry template for the next gate

### D005 diagnostic follow-up

At code `73c0af4`, lossless sentence facts produced 12 valid/9 correct development responses (`17796ff528cb`), including two unnecessary denials and one unauthorized production-extension proposal. The literal JSON-fact control repeated 12 valid/7 correct (`734dccb30da8`). No history comparison was run. These twelve-case development observations do not establish statistical improvement or generalization.

Next bounded diagnostic: use manually authored explicit mandatory/environment-specific checklist wording with the same formal policies, trusted facts and expected answers. This is task-interface clarification, not a new mitigation claim. Keep both policy/fact formats in run manifests and retain all unsuccessful outputs. Do not use the diagnostic accuracy as a held-out result.

- Date / decision ID:
- Question and previous assumption:
- Run IDs / code, config and dataset revisions:
- Observations, counts and controls:
- Alternative explanations and unresolved defects:
- Decision: continue / narrow / pivot / stop branch:
- Claim we can support; claim we cannot support:
- Next action and bounded budget:
