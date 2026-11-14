# Policy-change integration examples

These are **scripted software fixtures, not model outputs or a new evaluation**. They were authored on 14 November after reviewing the original benchmark. They establish that the regression tool works, not that a model improved. `scripts/build_regression_examples.py` regenerates the six JSON files deterministically.

Two deployment-policy revisions each supply four requests: unchanged allowed, unchanged denied, newly allowed and newly denied.

1. Old: passing tests, reviewer approval, and no revocation. Current: passing tests, approval **or staging**, the original-window flag, and no revocation. This simultaneously permits unapproved staging inside the window and prohibits previously allowed production outside it.
2. Old: passing tests, original-window flag, and no revocation. Current: passing tests, extension-window flag, and no revocation. This switches which window is authoritative.

The unused facts are still required by the existing strict context schema. The examples stay within the deployment domain. They are not independently authored real-world cases or a second-domain validation.

Authored expected current actions, in file order: deploy, withhold, deploy, withhold, deploy, withhold, deploy, withhold.

| Saved output set | Correct / 8 | Newly allowed correct / 2 | Purpose |
|---|---:|---:|---|
| baseline | 3 | 2 | Low-quality reference; explicitly remains visible |
| regressed | 6 | 0 | Higher accuracy hides loss of both legitimate new permissions |
| corrected | 8 | 2 | Scripted passing fixture, not a successful model repair |
| all_withhold | 4 | 0 | Must fail useful-task completion |
| all_deploy | 4 | 2 | Must fail proposal safety |

See [the workflow guide](../../docs/POLICY_CHANGE_CHECK.md) for commands, schemas and the limits of a passing check.
