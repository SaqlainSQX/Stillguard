# Stillguard

**Policies change. Safeguards should hold—and legitimate permissions should still work.**

Stillguard is a reproducible, formally labelled audit of small-model decisions after authorized policy updates. It separates unchanged safeguards, legitimate new permissions, basic rule errors, output-format failures and actions blocked by an independent simulated gateway. The actual pipeline uses CuratorKIT, pinned local Tiny Aya Global and AuditKIT.

The final audit is complete: **600 held-out calls independently verified; 117 tests pass.** Across the pilot, reminder development and final evaluation, 1,176 actual calls are preserved, with calibration/excluded attempts reported separately. No new weights or adapter were trained.

| Held-out result | Obsolete archive (HC) | Current policy only (P1) |
|---|---:|---:|
| Correct decisions / 120 | 45 | 71 |
| Known unsafe proposals | 43 | 26 |
| Invalid / violation unknown | 23 | 5 |
| All allowed tasks completed / 60 | 40 | 39 |
| **Legitimate new permissions accepted / 20** | **11** | **5** |
| New restrictions obeyed / 20 | 5 | 12 |

**Better aggregate scores concealed worse legitimate adaptation.** Current-policy-only context gained 21.7 percentage points of correctness but lost 30 points of new-permission completion. The trusted-amendment reference H also scored 71/120. Only one held-out case survived the strict history-specific controls; neutral filler itself caused many failures. We do not claim broad update-induced safety drift, a new internal mechanism or a successful safety repair preserving usefulness. The original pilot gate and the fixed reminder intervention failed, and those results remain public.

[Full results and limitations](experiments/heldout-001/REPORT.md) · [Saved actual-response demo](experiments/heldout-001/demo.html) · [Dataset card](docs/DATASET_CARD.md) · [Frozen protocol](experiments/heldout-001/PROTOCOL.md) · [Machine-readable results](experiments/heldout-001/summary.json)

The 20 held-out groups contain 120 probes and 20 unique current-policy truth functions disjoint from development. They share three component templates and some before policies; they are not independent real-world families. Policy/probe authoring was AI-assisted, with exhaustive direct-condition/AST checks over 64 states. Gold labels never enter model prompts. Every deployment is simulated. The gateway blocks unsafe execution by construction; that is not model-safety credit.

CuratorKIT actually ingests/deduplicates/exports complete factual payloads; AuditKIT evaluates every real model generation against the separate scorer. A prespecified exact-fence payload diagnostic exposes formatting-dependent safety measurements without changing the actual strict gate. SafeTune/CircuitKIT are references, not claimed integrations. This submission fits Track 2a's domain-specific safety benchmark deliverable.

[Hugging Face benchmark and logs](https://huggingface.co/datasets/SaqlainSQX/stillguard) · [Dataset collection](https://huggingface.co/collections/SaqlainSQX/stillguard-datasets-and-audit-traces-6af3eacf31b186e19999681d) · [Evaluated model collection](https://huggingface.co/collections/SaqlainSQX/stillguard-evaluated-model-6af3eacfe8cfcf8046d4e2a3)

## Use the finding in a regression check

Before merging a deployment agent or policy change, compare two saved proposal sets against the same current policy. The [CPU-only policy-change check](docs/POLICY_CHANGE_CHECK.md) separates unchanged safeguards, new restrictions and legitimate new permissions, binds outputs to a hashed fixture, and returns a failing CI exit status when explicit safety/usefulness budgets are exceeded. It reports absolute candidate quality as well as paired regressions, so a bad baseline cannot excuse a bad candidate.

The [eight-request integration example](examples/policy-change/README.md) demonstrates an accuracy increase from 3/8 to 6/8 that still fails because both newly allowed successes disappear. Those example answers are **scripted fixtures**, not new model results. A read-only exporter also applies the check to all 120 actual HC/P1 pairs from the frozen audit. This addition makes the diagnostic reusable; it does not establish a successful model repair, production safety, or broader generalization.

Execution: [plan](PLAN.md) · [tasks](docs/TASKS.md) · [decisions](docs/DECISIONS.md). Original code/policy fixtures/case annotations are MIT; [upstream model and dependency terms stay separate](THIRD_PARTY_NOTICES.md).

## Reproduce the final audit

After the environment and official model are prepared below:

```powershell
python scripts/build_heldout.py
python -m pytest -q
# Clean committed worktree required. Calls resume by frozen identity:
python scripts/run_heldout.py --max-minutes 35
```

For saved-answer replay, use the release's original `provenance/inputs/heldout.jsonl` and `provenance/runs/heldout-3b6f24e74100` folder with `scripts/verify_heldout.py` and `scripts/analyze_heldout.py`. Replay needs no GPU or weights; regeneration uses the official checkpoint. See the [exact commands](experiments/heldout-001/REPORT.md) and [frozen identities](experiments/heldout-001/FREEZE.md). Generation took 39.48 minutes on an RTX 4060 Laptop GPU; tooling/reloads/pauses are additional. Windows generation is tested; Linux/cloud is unvalidated.

## Fresh clone (Windows + NVIDIA GPU)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```powershell
git clone https://github.com/SaqlainSQX/Stillguard.git
cd Stillguard
.\bootstrap.ps1
```

The bootstrap downloads a project-local Python 3.12 runtime, CUDA-enabled PyTorch, pinned dependencies, toolkit source snapshots, papers and the official model. Accept access conditions for [Tiny Aya Global](https://huggingface.co/CohereLabs/tiny-aya-global) using your own Hugging Face account and authenticate locally. Use `bootstrap.ps1 -SkipModel` to prepare the rest first.

Model weights, binaries, downloaded references, runtime files and local reports are intentionally excluded from Git. Downloaded files remain on your machine. `bootstrap.ps1` needs network access; `setup-offline.ps1` uses the resulting local archive. The pinned Windows environment was checked on an RTX 4060 Laptop GPU; Linux/cloud setup is not yet validated.

## Start here

```powershell
# In your existing project folder:
. .\activate.ps1
python scripts/check_environment.py
python scripts/smoke_toolkits.py
```

`manifests/environment.json` records the tested environment. `requirements.lock.txt` records exact installed versions. `setup-offline.ps1` reconstructs the Windows environment from the saved package wheels once the initial setup is complete.

## Contents

| Folder | Contents |
|---|---|
| `vendor/` | Pinned source snapshots of CuratorKIT, AuditKIT, SafeTune, CircuitKIT, and Memopops as a prior-work reference |
| `downloads/sources/` | Original source ZIP archives |
| `downloads/wheels/` | Windows/Python 3.12 packages, including CUDA-enabled PyTorch |
| `tools/python/` | Project-local Python 3.12 runtime |
| `.venv/` | Isolated installed environment |
| `models/tiny-aya-global/` | Official model snapshot; completion is recorded in `manifests/model.json` |
| `references/papers/` | Twelve primary research PDFs |
| `references/pages/` | Downloaded documentation and event-page snapshots |
| `references/planning/` | Previous design and review records |
| `references/preparation/` | Existing curriculum, workbook and reading references |
| `configs/pilot.yaml` | Model and pilot design contract |
| `data/` | Synthetic raw discovery cases and locally generated, frozen CuratorKIT exports |
| `experiments/`, `results/`, `logs/` | Run configuration, output and setup logs |
| `src/stillguard/` | Policy oracle, strict schemas, prompt projection and simulated proposal/gate scoring |
| `notebooks/` | Reserved for later analysis |
| `manifests/` | Download provenance, pinned commits, package checksums and environment status |

Toolkit source snapshots are kept separate from the installed distributions. Installed versions are in the lockfile; source commit IDs are in `manifests/assets.json`. Optional SafeTune/CircuitKIT source and examples are available for inspection; their full optional training/interpretability stacks are not installed into the core environment.

## Model access

The target is `CohereLabs/tiny-aya-global`, revision `af89d219b53ed9b13b8a4645f9c8028973510324`, approximately 6.7 GB of weights. Model metadata, README and weights are not interchangeable: check `manifests/model.json` for actual download completion.

The repository is gated. The account used by the local HF login must have accepted access conditions at:

<https://huggingface.co/CohereLabs/tiny-aya-global>

To resume the download after access is enabled:

```powershell
.\download-model.ps1
python scripts/smoke_model.py
```

If local authentication needs refreshing, run `sign-in-locally.ps1` yourself. Enter credentials only in the local CLI prompt, never in chat, source files or notebooks. This project does not copy your token into its folder or auto-accept model conditions.

The smoke loader uses 4-bit NF4 quantization on the GPU, eager attention, local files only and no remote Python code. Original weights remain unchanged. Training memory and compatibility require a separate check.

## Reproducibility and verification

- `verify.ps1` runs dependency checks, CUDA/import checks, a synthetic CuratorKIT-to-AuditKIT fixture and, if weights are present, an actual model-load check.
- `scripts/smoke_toolkits.py` uses a declared fixture lookup, not Aya. Its score is plumbing verification and must not be reported as model accuracy.
- `scripts/smoke_model.py` records only successful loading and a short generated response. It is not a policy-continuity experiment.
- `manifests/assets.json` records downloaded files, checksums, repository commits and fetch failures.
- `configs/model-lock.json` pins the public model revision and expected files; the ignored `manifests/model.json` records this machine's access/download status.
- `manifests/wheels.json` records package archive checksums.
- The Windows wheel archive is platform-specific. Kaggle/Colab require Linux-compatible packages; do not install these Windows wheels there.

Licenses and upstream attribution files remain with the source snapshots. Keep reused prior work distinct from the new hackathon contribution. No artifacts are uploaded or published by the setup scripts.

## Release status

An optional [owner-reviewed fictional transfer attempt](experiments/transfer-001/REPORT.md) added 96 calls after the original release. All failed its strict output contract; it provides no successful transfer evidence and is retained as a negative appendix. The original 1,176-call research corpus and all frozen held-out results remain unchanged. The expanded software suite passes 121 tests.

Final scoring, report, saved h01 demo, MIT original-material release and public Hugging Face collections are complete. All published payload hashes and viewer splits are verified. A clean isolated source snapshot reproduced every score and the identical demo from anonymous downloads, without weights or site packages. See [submission links and abstract](docs/SUBMISSION.md). No submission form has been sent.

## Upstream tools and inspiration

The actual research pipeline uses [CuratorKIT](https://github.com/Lexsi-Labs/CuratorKIT) and [AuditKIT](https://github.com/Lexsi-Labs/AuditKIT). [SafeTune](https://github.com/Lexsi-Labs/SafeTune) and [CircuitKIT](https://github.com/Lexsi-Labs/CircuitKIT) are optional research references. Prior [Memopops](https://github.com/SaqlainSQX/memopops) work inspires revision-aware auditing; Stillguard's new experiments and results are reported separately. Upstream licenses remain attached to downloaded snapshots.
