# Final pipeline freeze — 10 November 2026

The pre-scoring gate in [PROTOCOL.md](PROTOCOL.md) is satisfied. **600 inputs are frozen; outcome analysis remains pending.** Pipeline construction and tests are not model-performance results.

- Real CuratorKIT processed 121 source rows (120 cases plus one declared duplicate), recovering all 120 distinct factual payloads and both labels byte-for-byte. Deduplication did not remove counterfactual conditions or fresh replays: those are assembled after curation.
- Five current-policy conditions per case: P1, P1R, H, HC and NC. Current gold labels and trusted request/state remain identical across each five-way pair.
- The actual pinned tokenizer's tensor interface checked every input count. All 120 HC/NC pairs match full token count and request-prefix position, with identical authoritative system policy and final request. All P1/P1R messages are byte-identical.
- Exhaustive source-rule/reference checks, scope binding and the independent oracle remain active. Gold rules, labels and design metadata are projected only to evaluator records, never to model messages.
- A separate prespecified payload sensitivity function removes only one complete outer JSON fence. It records no gate receipts and cannot change primary strict-parser decisions or actual simulated gate behavior.
- The final runner uses seed 45, the pinned local quantized model, real AuditKIT generation, fresh per-attempt cache identity, no implicit retry, full per-call traces, independent score agreement, a shared GPU lock, clean-tree checks and content-derived run IDs. It resumes successful keys and accounts for failed generations across execution versions sharing the input digest.
- Budget: 600 scheduled calls, at most 20 logged failed-generation retries and 620 actual generations total. Per-block maximum is 35 minutes; each continuation remains at most 45 minutes. Demo group h01 was selected before outputs.

Frozen input SHA-256: `011c34fda8a9bdb589e71d51b68dd9abf6c11eb7a1e70d98b7356a55141bcbee`.

Frozen raw source SHA-256: `267a8e58f979308082cb45789d9c3b02457c2ad2047bf91cfb1619d16deef4d8`.

`manifests/heldout-data.json` records generator, source-manifest, validation and renderer hashes; `configs/heldout.yaml` fixes generation, conditions and budget. The run manifest additionally records all execution-source/config/model identities and the clean starting commit. Full inputs and outputs remain in ignored local data/results folders, pending a reviewed artifact release.

Verification at freeze: **76 tests pass**, including complete-grid corruption checks, real-tokenizer matching, fixed scheduling/shared budget, strict gate behavior and exact-fence sensitivity boundaries.

```powershell
python scripts/build_heldout.py
python -m pytest -q
# Only from a clean committed worktree:
python scripts/run_heldout.py --max-minutes 25
```

Do not interpret partial scores or tune methods after scoring begins. Resume the matching frozen run until all 600 succeed or a documented failure/budget limit requires review. Preserve the failed pilot gate, rejected reminder and all synthetic/dependence limitations.
