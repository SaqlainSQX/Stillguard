# Submission package

Working finish target: **12 November IST**. The [official page](https://hackathon.lexsi.ai/#submit), rechecked 11 November, now gives **15 November, 11:59 PM AoE** as the submission deadline. The earlier 14 November note is superseded; keep the earlier internal target.

Track: **2a — AI Safety and Red Teaming**, problem 2: domain-specific adversarial/safety evaluation set. The contribution is a benchmark and audit report, not a successful fine-tuning/repair claim.

Team declaration: **solo submission — Saqlain (SaqlainSQX)**, confirmed by the participant on 14 November. No teammates to credit. AI-assisted development and upstream contributions remain disclosed separately; solo participation does not imply authorship of upstream models or libraries.

## Abstract (under 500 words)

Stillguard audits what an AI action proposer must preserve—and what it must change—after a legitimate policy amendment. A model can appear safer by refusing useful new permissions, or appear safe because malformed outputs hide unsafe payloads. Our benchmark measures both failures explicitly.

We built an actual CuratorKIT-to-Tiny Aya Global-to-AuditKIT pipeline with a separately implemented finite-policy oracle and simulated tool gateway. A 20-group, 120-probe held-out set contains new policy truth functions disjoint from development, with five fixed current-policy, replay, trusted-amendment and matched-archive conditions. The groups share three component templates; they are not independent real-world families. Gold rules and labels never enter model prompts. All 600 held-out strict scores and prespecified exact-fence payload scores were independently replayed.

Removing an obsolete archive improved strict correctness from 45/120 to 71/120 and reduced known unsafe proposals from 43 to 26. Yet legitimate new-permission completion fell from 11/20 to 5/20. Aggregate allowed completion, 40/60 versus 39/60, concealed that adaptation loss. A strong trusted-amendment reference also scored 71/120. Only one held-out case survived the strict history-specific controls; extensive neutral-history failures limit causal interpretation. Our original pilot gate and a fixed reminder intervention failed, and both remain disclosed.

We release the formally labelled source, frozen prompts/configuration, actual call traces, complete metrics, failed approaches and a saved-response demo group selected before held-out outcomes. The gateway's zero unauthorized executions are an engineered property, not model-safety credit. No new weights or adapter were trained. Stillguard contributes a reproducible, validity-aware audit of safety/usefulness tradeoffs, not a claim of broad update-induced drift or a novel safety mechanism.

A CPU-only regression CLI now accepts user-supplied deployment-policy fixtures and saved proposals, checking absolute candidate quality and paired safety/usefulness losses. Its read-only replay exposes six lost newly allowed successes in the original HC-to-P1 comparison. New scripted integration examples test the tool; they are not new model evidence.

## Contribution and additional-compute declaration

Solo contributor: SaqlainSQX. Stillguard's new implementation, synthetic fixtures, experiments and reports were developed for this event; the repository's recorded implementation history begins on 9 November. Prior Memopops work supplied inspiration, not an imported experimental component. CuratorKIT, AuditKIT, the official Aya checkpoint and other dependencies are upstream work under their own terms. Development and writing were AI-assisted; generated suggestions were checked through tests and the separate scorer. No teammates or external human validators are claimed.

With more credits, we would preregister a naturally structured archive-control study and a separately authored policy-transfer set, then compare additional open Cohere models under pinned generation settings. The expected before/after is a hypothesis: replacing repeated neutral filler with a structurally matched archive may reduce malformed controls and sharpen the stale-history contrast; additional models/domains may reproduce, reverse or eliminate the permission-loss tradeoff. We would measure strict correctness, unsafe proposals, unknown violations and newly allowed completion, publish all outcomes, and make no numerical gain promise. No such additional study or successful repair has been completed.

## Links and required fields

- Code/write-up: https://github.com/SaqlainSQX/Stillguard
- Detailed report: experiments/heldout-001/REPORT.md
- Saved actual-response demo: experiments/heldout-001/demo.html
- Hugging Face benchmark/logs: https://huggingface.co/datasets/SaqlainSQX/stillguard
- Public dataset collection: https://huggingface.co/collections/SaqlainSQX/stillguard-datasets-and-audit-traces-6af3eacf31b186e19999681d
- Public model-reference collection: https://huggingface.co/collections/SaqlainSQX/stillguard-evaluated-model-6af3eacfe8cfcf8046d4e2a3
- Model used: CohereLabs/tiny-aya-global, revision af89d219b53ed9b13b8a4645f9c8028973510324.
- Track repositories actually used together: CuratorKIT and AuditKIT. Optional SafeTune/CircuitKIT downloads are not integrations.
- Registration email and Discord username: enter the contacts used for the event; they are deliberately not stored in this public repository. The first form page was checked read-only; no answers were entered.

The official form requests model/data collections and a write-up; a GitHub README is accepted. All newly created dataset/log repositories and collections must be public. No model/adapters were created: the model collection should identify the official upstream checkpoint and retain its access terms, without pretending to publish new weights or changing upstream gating.

Public links, all 68 payload checksums, the 36/120/600 viewer splits and anonymous 600-score replay are verified. The abstract has 301 words. A clean isolated source snapshot reproduced identical analysis and demo without site packages or weights. Confirm your registration details and review the final links before submitting. **No submission form has been sent.** Submit at https://hackathon.lexsi.ai/submission/ after your final review.
