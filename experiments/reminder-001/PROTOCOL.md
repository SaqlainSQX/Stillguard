# Development reminder comparison 001

Frozen before new model calls on 10 November 2026. This is development data, not a held-out result or final method selection. One fixed wording; no search over reminder variants.

All 36 CuratorKIT-preserved pilot cases are reused with current-policy labels and the same trusted state, archive and independent scorer. The frozen parent export must retain its SHA-256 identity. No new curation or synthetic model-generated labels are claimed.

| Condition | Model-visible change from HC |
|---|---|
| HC | None; freshly generated replay of the frozen pilot HC prompt |
| PR | Prepend a reminder containing the authoritative current policy prose to the final request |
| GR | Prepend an ordinary instruction to check the operative policy and return action JSON, at the same location |

PR and GR have exactly equal full input token counts and request-prefix token positions under the pinned real tokenizer. GR uses disclosed repeated `Check` padding to reach that count; it is artificial, and does not control naturalness or every semantic effect of PR. HC is shorter: the PR-versus-GR comparison controls added length; HC alone does not. The current policy is already in every system message; PR tests redundant local policy presentation, not additional authorization or knowledge. It repeats the entire authoritative policy, including intended exceptions, rather than selectively quoting observed failing clauses.

Prompt construction uses only the current policy prose, the existing HC messages and the tokenizer. Gold labels, ASTs, independent-oracle decisions, case names and group IDs do not enter the reminder. Case-specific outcome hints and fabricated proof records are forbidden.

108 scheduled generations, one per case/condition; seed 44 fixed shuffle and greedy decoding, same pinned model/quantization/generation limit as the pilot. A shared GPU lock prevents overlap. Clean tracked worktrees, frozen hashes, actual generation counts, no implicit retry and the AuditKIT/direct scorer agreement remain mandatory. The global budget is 108 actual generations across execution fingerprints for this input digest, including logged failed generations; a failure may leave incomplete coverage. Resume only within that budget. Each work block is separately bounded.

Report unconditional decision correctness, valid output, known unauthorized proposals, unknown violation status, legitimate allowed-task completion, unnecessary withholding, and intended-update correctness. Report paired PR/GR wins/losses and the fresh-HC versus original-HC action/correctness changes. Keep every case. The P1 pilot result is a separate, stronger current-policy-only reference, not a new contemporaneous run.

Review both confirmed discovery failures without treating them as a test set. An apparent gain must not come solely from blanket withholding or invalid-output changes. If PR adds no useful value beyond GR or current-policy isolation, select the simpler architecture or report the null. No safety-improvement/generalization claim until new grouped held-out data is frozen before final selection and scored under the chosen configuration. The original three-group pilot gate remains failed.

Diagnosis/implementation cap: 90 minutes under D010. No extra prompt variants, training, third toolkit or UI on this branch. The next milestone after this comparison is held-out construction and release preparation, not another development search.

Rebuild: `python scripts/build_reminders.py`. Run only from a clean committed tree: `python scripts/run_reminders.py --max-minutes 20`. Frozen identities live in `manifests/reminder-data.json`; full local traces are ignored by Git.
