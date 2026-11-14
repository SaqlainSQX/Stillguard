# Transfer attempt: output-contract failure

The prospective extension completed all **96 scheduled local Aya generations**, across 32 distinct requests and three conditions. **All 96 responses failed the frozen strict JSON output contract.** Every group/condition therefore has 0/8 strict correct decisions and eight unknown safety outcomes. Zero known unsafe proposals is not evidence of safe behavior: none of these outputs could be evaluated as a valid proposal.

Inspection identified Markdown-fenced JSON responses. We did not strip fences, change scoring, select favorable cases, or run tuned prompts again. The saved strict scores replay exactly. The pre-inference protocol/code/input freeze is commit `02cc8da`; [summary and trace identity](summary.json) preserve the run configuration and group denominators. Raw responses remain in local `results/transfer-001/calls.jsonl` rather than being duplicated as bulk Git traces.

## Interpretation

This attempt **does not validate transfer of the original safety/usefulness tradeoff**, establish model safety, or demonstrate a correction. The strict output interface failed first. A model-backed development format check should have preceded the scored freeze; that execution omission limited the value of the study. The original deployment audit and its prespecified payload analysis remain unchanged. No post-hoc normalization is promoted to a primary result here.

The four fictional policies were AI-authored and approved by the project owner. They are not actual institutional policies, independently human-authored scenarios or external replication. A1/A2 each contribute one distinct changed-permission case; B1/B2 each contribute two. These tiny constructed slices could not establish population generalization even if their output format had succeeded.

## Decision

Retain this negative extension as an appendix and keep the completed regression-check workflow and original audit as the submission's main contributions. No improved score or new cross-domain success is claimed. A future study needs a separately frozen development adapter check and fresh evaluation cases, with failures here disclosed as development knowledge. Do not retune on these 32 cases and call them untouched evaluation.

Verification: 121 tests pass. All 96 records replay against the frozen input messages and scorer. The 16 original held-out audit files retain their previously recorded SHA256 hashes. There were no hidden generation retries or further model calls.
