# Stillguard

**Policies change. Safeguards should hold.**

Stillguard investigates whether legitimate policy updates cause small Aya agents to violate safeguards that remain unchanged. It measures correct adaptation alongside safety regressions, with matched-policy and no-change controls.

Current stage: verified research setup. The policy-continuity pilot has not run; no safety improvement is claimed. Synthetic setup fixtures and model-load checks are labeled separately. See [the pilot protocol](docs/PROTOCOL.md).

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
| `data/` | Separate raw, curated and split directories; benchmark not generated yet |
| `experiments/`, `results/`, `logs/` | Run configuration, output and setup logs |
| `notebooks/`, `src/` | Reserved for the upcoming pilot implementation |
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

## Next research step

Implement the six-family pilot in `configs/pilot.yaml`, with independently defined expected decisions, matched current-policy/history controls and a confirmation panel. Preserve held-out policy families before tuning a mitigation. The setup does not assert that the hypothesized failure exists.

## Upstream tools and inspiration

The planned core pipeline uses [CuratorKIT](https://github.com/Lexsi-Labs/CuratorKIT) and [AuditKIT](https://github.com/Lexsi-Labs/AuditKIT). [SafeTune](https://github.com/Lexsi-Labs/SafeTune) and [CircuitKIT](https://github.com/Lexsi-Labs/CircuitKIT) are optional research references. Prior [Memopops](https://github.com/SaqlainSQX/memopops) work inspires revision-aware auditing; Stillguard's new experiments and results will be identified separately. Upstream licenses remain attached to downloaded snapshots.
