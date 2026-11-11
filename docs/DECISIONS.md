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

### D005 diagnostic follow-up

At code `73c0af4`, lossless sentence facts produced 12 valid/9 correct development responses (`17796ff528cb`), including two unnecessary denials and one unauthorized production-extension proposal. The literal JSON-fact control repeated 12 valid/7 correct (`734dccb30da8`). No history comparison was run. These twelve-case development observations do not establish statistical improvement or generalization.

Next bounded diagnostic: use manually authored explicit mandatory/environment-specific checklist wording with the same formal policies, trusted facts and expected answers. This is task-interface clarification, not a new mitigation claim. Keep both policy/fact formats in run manifests and retain all unsuccessful outputs. Do not use the diagnostic accuracy as a held-out result.

## D006 — 10 November 2026: finish the bounded calibration diagnostic

Checklist/sentence facts scored 8/12 (`719afbe19d42`); checklist/JSON facts scored 10/12 (`b5f4c69f94a8`), both at code `45a4c86` with 12 valid proposals. The latter still deployed after failed tests and despite revocation. These are basic policy errors, not history effects.

Decision: end wording search and provisionally use explicit policy checklists plus literal JSON facts when implementing the new discovery pilot. Maintain all planned cold/replay/history/neutral controls and retain all cases, including weak-baseline cases. Report unconditional errors separately from conditional regressions. Do not present development selection as held-out improvement. See experiments/calibration-001/REPORT.md for all five valid runs and excluded-call accounting.

Next: six research scenario groups, authenticated history construction and matched token/position controls, real CuratorKIT/AuditKIT dataflow, then frozen pilot traces. Gate A remains unreached. No training or UI work is justified yet.

## D007 — 10 November 2026: freeze discovery construction before outcomes

Six synthetic groups/36 probes are validated with exhaustive independent rule checks. They share four structural clusters and are not independent real-world samples. All 252 inputs are frozen with the pinned tokenizer; HC/NC match authoritative instructions, total tokens and request position. Cold replay prompts are identical. Gold labels, formal ASTs, descriptive group/case names and evaluator metadata are excluded from model inputs.

The first Curator adapter attempt revealed that SFT deduplication ignored the separate input payload, collapsing cases by shared instruction/label. Coverage checks stopped the build. The corrected adapter puts complete source payloads in the dedup-relevant instruction field, preserving every case and removing only the declared duplicate (37 to 36). This is an integration correction, not a model result.

Thirty-nine tests pass, including real pinned-tokenizer matching and actual AuditKIT adapter replay checks. Decide to launch the frozen discovery sweep with a 20-minute work-block limit; confirmation and Gate A interpretation remain pending. A GPU lock and resumable call logs prevent overlapping or silently repeated work.

## D008 — 10 November 2026: tokenizer-count preflight catches invalid freeze

The first discovery launch stopped before generation: the frozen count used the length of the tokenizer's encoding container rather than its input_ids. The saved error has model_calls=0 and is not model evidence. No research answer was generated under that invalid freeze.

Corrected all counts to explicit input_ids and checked matching against the actual return_tensors interface used by inference, with nontrivial token-count assertions. Normalized JSON/JSONL line endings so clone/rebuild hashes are stable. Rebuilt the frozen inputs and passed all 39 tests. The old stopped run is retained for provenance; start the corrected dataset under a new run fingerprint.

## D009 — 10 November 2026: preserve nonapplicable metric denominators

AuditKIT marked explicit unknown/nonapplicable metric scores as failures. The first denied request exposed this integration behavior: unnecessary withholding is not applicable when denial is expected. Corrected the adapter to omit nonapplicable metrics while preserving invalid-output and task-correctness scores. Direct traces still record nullable violation/withholding status and their denominators. Tests now exercise allowed, denied, malformed and repeated-call cases; 41 pass.

Stopped preflight/integration runs are marked EXCLUDED and retained with their actual logged model-call counts. Start a new execution fingerprint after this scoring correction. No full discovery result or Gate A decision has been claimed.

## D010 — 10 November 2026: complete the pilot and narrow the continuation claim

Discovery `95d96eb52486` completed 252 calls; confirmation `82c43bb4aeb7` completed 216, both at clean execution commit `5853db8d5d3aad941701f9ff01b23eb12f09523e`, without failed research calls. All 468 prompts/states/labels/token counts match frozen inputs; offline full-score replay and AuditKIT correctness agree. Forty-eight tests pass. See experiments/pilot-001/REPORT.md and its hashed machine-readable summary.

Discovery P1/H/HC/NC correctness was 26/20/16/14 out of 36. HC had 13 known unsafe proposals and three invalid outputs; NC had ten known unsafe proposals and ten invalid outputs. Neither invalid outputs nor the aggregate HC/NC comparison establishes history-specific drift. Cold-current policy already mishandles revocation and some legitimate exceptions. Original/current exact replays had no action/correctness flips.

Two unchanged-denied cases (g04-c03 and g06-c03) passed P1/P1R/NC but failed HC. Both reproduced with matched correct controls in 3/3 confirmation repeats, spanning two groups/two structural clusters. No refresh-resolved candidate qualified. The **original three-group gate failed**. These repeats are reproducibility checks, not independent families or a significance test. Do not lower the gate retroactively.

Decision: narrow to an update-aware action audit and one small policy-interface comparison, retaining the limited positive cases and the larger context/basic-task failures. This is the planned narrowing branch, not a claim that the original thesis passed. No training, circuits, multilingual expansion or UI work. No internal-mechanism or real-world prevalence claim.

Next bounded budget: at most 90 minutes of diagnosis/implementation and 108 new development generations: 36 cases × fresh HC, HC plus an authoritative-policy reminder, and HC plus an ordinary reminder matched in token count/placement. Freeze wording/config/data before any new calls. Reminders may use authoritative policy text, never oracle decisions, gold labels or evaluator metadata. Keep P1 as the strong current-policy-only baseline. Report allowed-task completion, intended changes, invalid outputs and unsafe proposals together. If the specific reminder adds no value beyond generic prompting or state isolation, keep the simpler method and report the null. Freeze new grouped held-out data before final selection; do not reuse these development outcomes as test evidence.

## D011 — 10 November 2026: freeze one controlled reminder comparison

Before any new model outcomes, freeze 36 existing curated development cases × HC/PR/GR (108 inputs). PR repeats only authoritative current policy prose before the final request. GR uses ordinary policy-checking instructions with disclosed repeated `Check` padding; real-tokenizer full length and request-prefix position exactly match PR. HC is byte-identical to the pilot archive baseline and is freshly generated. No AST, oracle answer or evaluator label enters a reminder.

The separate runner retains the shared GPU lock, actual generation accounting, clean-tree/frozen-hash checks, strict independent scoring and AuditKIT agreement. The 108-generation cap includes logged failed calls across execution versions for this input digest. This is one fixed development wording, not a new test or a passed pilot gate. Protocol: experiments/reminder-001/PROTOCOL.md. Next: run the frozen comparison, keep all outputs and decide once; no extra variant search.

## D012 — 10 November 2026: freeze new held-out source before final selection

The fixed 108-call development comparison completed cleanly. Before its aggregate analysis or final method selection, freeze raw held-out source `267a8e58f979308082cb45789d9c3b02457c2ad2047bf91cfb1619d16deef4d8`: 20 new rule-composition transitions / 120 probes, balanced broadening/restriction and current allowed/denied labels. No held-out model calls have occurred.

Exhaustive 64-state direct-condition/AST checks verify each policy. Truth functions are disjoint from discovery and calibration; 20 current functions are unique and inverse transition duplicates are excluded. The groups still share three component templates, primitive facts and some before policies; they are not independent real-world families. Some within-group contrasts can vary irrelevant facts. Eight new tests cover deterministic authoring, actual calibration exclusion, boundary cases, corruption/scope errors and gold-metadata projection.

This is a raw-source freeze only, not completion of T9. The pilot informed the grammar, and the source was authored during development prompting. Next: analyze the fixed development run once, select a provisional simple comparison without another wording search, then curate/render/freeze final evaluation inputs and configuration. Preserve every held-out source case. See docs/HELDOUT_DATA.md and manifests/heldout-source.json.

## D013 — 10 November 2026: reject reminders and freeze the final comparison plan

The fixed run `67b0c7b82603` completed 108 calls at clean commit `b9550f1`, with no failed calls; all frozen inputs and direct scores independently replayed. HC/PR/GR strict correctness was 16/14/0 out of 36, with 3/11/36 invalid outputs and 13/9/0 known unsafe proposals. Fresh HC matched the original HC in action and correctness on every case. PR gained two correct decisions and lost four; it did not fix either previously confirmed unsafe case. Lower known violations caused by invalid outputs are not improvement.

GR emitted fenced JSON on every request and is a failed strict-interface control, not evidence that PR provides a specific safety mechanism. Disclosed exploratory offline exact-fence removal gives HC/PR/GR correctness 16/19/17 and unsafe payloads 13/15/17. No extra prose/keys or substantive content was repaired. These are secondary diagnostics; the original parser, primary results and gate behavior remain unchanged. See experiments/reminder-001/REPORT.md and hashed summaries.

Decision: **end reminder search** and retain the simpler current-policy-only action context as the architectural reference, including its known errors. P1's earlier 26/36 is a separate reference, not a new contemporaneous result. No successful mitigation, training contribution or broad safety-drift claim. Preserve the negative comparison and weak generic control.

After raw held-out source freeze at `114cbf6`, fix the final evaluation plan to P1/P1R/H/HC/NC over all 120 source probes: 600 scheduled calls, at most 20 failed-generation retries (620 actual maximum), seed 45 shuffle, same pinned model/generation settings. Predefine strict primary scores and a separate exact-fence sensitivity view. Select h01 for the demo before outcomes. The original pilot gate remains failed. Protocol: experiments/heldout-001/PROTOCOL.md.

Next bounded milestone: real CuratorKIT recovery/export, matching and gold-exclusion tests, final prompt/config manifests and a tested resumable held-out runner. Commit that full freeze before any held-out scoring; raw data freeze alone does not authorize treating generated code as results. Then execute sequential bounded blocks and prioritize report/artifact release by 12 November. No new methods, extra models or optional training.

## D014 — 10 November 2026: complete the final input/configuration freeze

Real CuratorKIT preserved all 120 held-out factual payloads/labels from 121 declared source rows and removed only the intentional duplicate. Assemble P1/P1R/H/HC/NC after curation to retain all 600 fresh-call controls. Input SHA-256: `011c34fda8a9bdb589e71d51b68dd9abf6c11eb7a1e70d98b7356a55141bcbee`; raw-source SHA remains unchanged.

Seventy-six tests pass. Actual tensor-tokenizer checks validate every input count and all HC/NC token/position matches; cold replays are identical. The separately frozen exact-fence payload view records no gate receipts and cannot alter strict scoring. Shared locking, 620-generation global accounting including failures, content-derived execution IDs, per-call persistence, AuditKIT/direct agreement and clean-tree checks remain mandatory. See experiments/heldout-001/FREEZE.md.

Decision: the full pre-scoring gate is satisfied; start only this frozen 600-call evaluation and resume in bounded blocks. Do not change methods, code/configuration or source from partial outcomes. Do not infer performance from this construction milestone or from incomplete traces. After completion, independently replay all primary and payload-sensitivity scores, report every condition and build the actual h01 demo/release package. Training and reminder search remain closed.

## D015 — 11 November 2026: resume the unchanged final run from its bounded checkpoint

The first model block stopped normally on 10 November with 383/600 calls saved, zero failures, clean tracked worktree and released GPU lock. Run `3b6f24e74100` retains execution commit `c23ab9b`; execution/data fingerprints were rechecked unchanged. No partial outcome analysis was performed. The remaining 217 calls must resume this run, not restart the experiment or rebuild inputs.

Eighty-four tests pass. Complete-run analysis, full strict/payload replay verification and the preselected h01 HTML demo generators are now tested. They reject incomplete coverage; HTML escapes untrusted model output. Their preparation is not completion of the evaluation or demo. Public PROGRESS.json records counts only, not performance conclusions. A local, unreleased dataset-card draft exists in results/DATASET_CARD_draft.md.

The user's 11 November timer request changes the standing continuation cycle and maximum work window to 90 minutes; all usage/access/compute limits still apply, and model blocks remain at most 35 minutes. Next: resume `python scripts/run_heldout.py --max-minutes 35`, verify all 600 primary and sensitivity scores only after completion, analyze every condition and generate the fixed h01 demo. Do not change execution sources/configuration or select cases from partial outcomes. Finish release preparation by 12 November IST.

## D016 — 11 November 2026: complete and verify all held-out outcomes

Run `3b6f24e74100` completed all 600 scheduled calls with zero failures/retries and clean tracked worktrees. All primary and payload-sensitivity scores independently replayed; AuditKIT agrees. P1/P1R have no action/correctness flips, including 64 pairs split across the model restart/checkpoint. Total generation time is 2,368.67 seconds; block snapshots preserve the observed peak allocation separately from the final block's peak.

P1/HC strict correctness is 71/45 out of 120, with 26/43 known unsafe proposals and 5/23 invalid outputs. However, new-permission completion drops from 11/20 under HC to 5/20 under P1, while new restrictions improve from 5/20 to 12/20. Aggregate allowed completion (40/60 versus 39/60) hides the adaptation loss. H ties P1 at 71/120. One primary held-out case qualifies beyond stable cold and neutral controls; two qualify in the separate payload view. Neutral filler has extensive validity failures. No broad causal continuity or successful safety-with-usefulness claim is justified.

Decision: close evaluation/method search and release the domain-specific benchmark/audit under Track 2a problem 2, including negative findings. Do not train or invent an extra method to rescue the thesis. The original three-group pilot gate remains failed. Final report, machine-readable results, verification, all h01 demo responses and a checked tradeoff figure are generated. Ninety-one tests pass; the saved HTML was rendered in an isolated headless browser and inspected.

The owner explicitly chose MIT for original code and synthetic data. LICENSE/THIRD_PARTY_NOTICES distinguish those rights from the base model's declared CC-BY-NC-4.0 and upstream dependencies. No weights/adapters were created or redistributed. The official event page, rechecked today, now lists 15 November 11:59 PM AoE; the internal 12 November target remains unchanged.

Next: commit the reviewed report/card/export tools, build an allowlisted local bundle, test its case/call reader schemas and checksums, publish the new dataset/log artifacts and public collections on Hugging Face, and verify all submission links. The registration email stays out of Git; no submission form has been sent. A 254-word abstract is prepared. Respect the user's updated 90-minute continuation limit and all existing compute/access limits.

## Entry template for the next gate

- Date / decision ID:
- Question and previous assumption:
- Run IDs / code, config and dataset revisions:
- Observations, counts and controls:
- Alternative explanations and unresolved defects:
- Decision: continue / narrow / pivot / stop branch:
- Claim we can support; claim we cannot support:
- Next action and bounded budget:
