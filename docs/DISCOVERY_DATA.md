# Discovery pilot 001: frozen construction

Source: `data/raw/discovery-groups.json`; hashes and pinned tokenizer revision: `manifests/pilot-data.json`. Build with `python scripts/build_pilot.py` after downloading the pinned model/tokenizer. Generated inputs and CuratorKIT exports remain local in `data/curated/pilot-001/` until release packaging.

Six predetermined synthetic amendment groups cover universal window extension, staging approval exemption, production approval tightening, revocation enforcement, staging test exemption and extension withdrawal. Some share the same formal policies or reverse an update. There are four structural clusters, not six statistically independent real-world samples. Some intended-change probes vary an irrelevant extension flag to test invariance; do not count those as independent policy discoveries.

Each group has two unchanged-allowed, two unchanged-denied and two intended-change probes. Explicit before/after annotations are checked against a finite Boolean AST and separately authored Python expressions over all 64 combinations of five trusted facts and environment. Environment predicates are derived in code. This verifies formal consistency, not arbitrary natural-language equivalence. Source wording is explicit and manually inspectable.

The synthetic application harness whitelists the amendment issuer and checks workspace, resource and revision bindings. This represents trusted application metadata; it is not cryptographic authentication or an experiment in discovering authority from text. Unverified or mismatched records fail before prompt assembly.

CuratorKIT reads 37 source records (36 cases plus one deliberate exact duplicate), validates and deduplicates them, and exports 36. The complete source payload is placed in its instruction field because SFT exact deduplication does not use the input field. A coverage/byte-preservation check prevents silent loss of distinct cases. Gold rules and labels occur only in evaluator source records; the model receives an explicit allowlisted projection.

Seven conditions are assembled after curation: original and current cold policies and exact replays, original-plus-authorized-amendment, current-policy-plus-obsolete-archive, and current-policy-plus-neutral-archive. Cold replays are byte-identical model messages. Every condition for a case uses identical request facts and opaque request identifiers.

HC and NC use the identical authoritative system instruction, roles and final request. The neutral archive is constructed using the actual pinned tokenizer until its total input length AND request-prefix token count exactly match HC. The neutral text is synthetic build-log filler; this controls length/position, not every possible discourse or attention effect. The history is constructed, not a claim about naturally occurring autonomous agent memory.

The initial frozen schedule is 252 calls. A separately scheduled confirmation panel covers one unchanged allowed, one unchanged denied and one changed probe per group, repeating P1/H/HC/NC three times (216 calls). Both schedules are outcome-independent and retain baseline failures. Calls use greedy generation, reset inputs, no in-run adaptation and no hidden judge model.

`scripts/run_pilot.py` uses actual Aya responses through AuditKIT, custom contract metrics, a cross-run GPU lock, per-call JSONL checkpointing, unique audit attempt identities, a shared failed-call ceiling and a bounded work-block clock. Exact repeats are generated afresh; cache substitution raises an error. Model inputs never contain sample targets or evaluator metadata.

```powershell
python scripts/build_pilot.py
python -m pytest -q
# Commit source/config/manifest changes before scored runs.
python scripts/run_pilot.py --phase discovery --max-minutes 20
python scripts/run_pilot.py --phase confirmation --max-minutes 20
```

Resume by invoking the same phase under the same execution/config/data hashes. Documentation-only commits do not reset a partially completed run. Execution changes create a new run identity. If an input, tokenizer count or scorer disagrees, the run stops. Review all invalid calls, weak cold baselines and no-change flips before attributing an error to history.
