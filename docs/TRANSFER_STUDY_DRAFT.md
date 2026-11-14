# Prospective transfer study — draft, not frozen or executed

Purpose: test whether policy-transition safety/usefulness diagnostics transfer beyond the constructed deployment domain. This study is optional and must not delay submission of the completed project. It does not change heldout-001.

## Authorship and review gate

The project owner will supply four original fictional policy transitions across two familiar non-deployment areas, with old/current prose and available trusted facts. The owner has seen the existing findings and general suggested study direction; this is not blinded external validation. Record the original supplied text verbatim and disclose any assistance. Do not label agent-generated scenarios human-authored.

Before inference, formalize the supplied rules and construct request cases. Have the owner explicitly review prose/formal-rule correspondence and expected decisions. Record corrections before freezing. Acknowledging willingness to participate is not completed authorship or validation. Until the scenarios and review arrive, no scored model generations are authorized by this protocol.

## Proposed bounded design, subject to feasibility review

- Two distinct domains, two owner-authored transitions per domain. Use genuinely different predicates and structures rather than renaming deployment facts.
- Up to eight requests per transition, covering unchanged allowed/denied and newly allowed/denied where those categories logically exist. Never invent a transition category absent from the supplied policy. Report absent coverage.
- Current policy only, trusted replacement amendment, and current policy plus obsolete archive: at most 96 scored generations using the original pinned Aya model/decoding. This tests transfer of descriptive contrasts, not history-specific causation. No neutral-control or internal-mechanism claim.
- New domain-specific strict action schemas and exhaustive finite rule checks, with a separately implemented direct-condition reference. Gold rules/labels/transition categories remain outside model prompts.
- A separate development-only plumbing set checks the adapter. Freeze source text, validated cases, prompts, parsers, configuration, schedule, hashes, analysis and exclusions before any scored generation. No tuning after viewing scored outputs; retain all failures and null/reversed findings.

## Analysis and stopping rules

Report every domain/transition and condition, strict correctness, known unsafe proposals, invalid/unknown outputs, target mismatches, newly allowed completion and newly denied compliance. Preserve paired case identities and denominators. Four authored transitions cannot support population significance or prevalence estimates.

The original aggregate-improvement/permission-loss pattern may reproduce, reverse or disappear; all outcomes count as results. Do not promise a score uplift or successful mitigation. Results remain a small owner-authored, AI-formalized constructed transfer study, not independent external replication.

Stop before inference if the owner cannot review labels, rules are ambiguous, the task needs unavailable facts, or domain structure cannot be implemented and verified within the delivery buffer. Preserve the already completed submission rather than rush a weak validation. Model runs must respect the existing exclusive GPU lock, access conditions and bounded compute controls.
