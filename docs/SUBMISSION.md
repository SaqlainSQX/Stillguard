# Submission package

Working finish target: **12 November IST**. The [official page](https://hackathon.lexsi.ai/#submit), rechecked 11 November, now gives **15 November, 11:59 PM AoE** as the submission deadline. The earlier 14 November note is superseded; keep the earlier internal target.

Track: **2a — AI Safety and Red Teaming**, problem 2: domain-specific adversarial/safety evaluation set. The contribution is a benchmark and audit report, not a successful fine-tuning/repair claim.

## Abstract (under 500 words)

Stillguard audits what an AI action proposer must preserve—and what it must change—after a legitimate policy amendment. A model can appear safer by refusing useful new permissions, or appear safe because malformed outputs hide unsafe payloads. Our benchmark measures both failures explicitly.

We built an actual CuratorKIT-to-Tiny Aya Global-to-AuditKIT pipeline with a separately implemented finite-policy oracle and simulated tool gateway. A 20-group, 120-probe held-out set contains new policy truth functions disjoint from development, with five fixed current-policy, replay, trusted-amendment and matched-archive conditions. The groups share three component templates; they are not independent real-world families. Gold rules and labels never enter model prompts. All 600 held-out strict scores and prespecified exact-fence payload scores were independently replayed.

Removing an obsolete archive improved strict correctness from 45/120 to 71/120 and reduced known unsafe proposals from 43 to 26. Yet legitimate new-permission completion fell from 11/20 to 5/20. Aggregate allowed completion, 40/60 versus 39/60, concealed that adaptation loss. A strong trusted-amendment reference also scored 71/120. Only one held-out case survived the strict history-specific controls; extensive neutral-history failures limit causal interpretation. Our original pilot gate and a fixed reminder intervention failed, and both remain disclosed.

We release the formally labelled source, frozen prompts/configuration, actual call traces, complete metrics, failed approaches and a saved-response demo group selected before held-out outcomes. The gateway's zero unauthorized executions are an engineered property, not model-safety credit. No new weights or adapter were trained. Stillguard contributes a reproducible, validity-aware audit of safety/usefulness tradeoffs, not a claim of broad update-induced drift or a novel safety mechanism.

## Links and required fields

- Code/write-up: https://github.com/SaqlainSQX/Stillguard
- Detailed report: experiments/heldout-001/REPORT.md
- Saved actual-response demo: experiments/heldout-001/demo.html
- Hugging Face dataset and public collections: publication links are recorded in manifests/publication.json once verified.
- Model used: CohereLabs/tiny-aya-global, revision af89d219b53ed9b13b8a4645f9c8028973510324.
- Track repositories actually used together: CuratorKIT and AuditKIT. Optional SafeTune/CircuitKIT downloads are not integrations.
- Registration email: enter the address used to register; it is deliberately not stored in this public repository.

The official form requests model/data collections and a write-up; a GitHub README is accepted. All newly created dataset/log repositories and collections must be public. No model/adapters were created: the model collection should identify the official upstream checkpoint and retain its access terms, without pretending to publish new weights or changing upstream gating.

Before submitting: verify the public artifact links, include all planned conditions/failed attempts, check the abstract word count and confirm the registration details. **No submission form has been sent.**
