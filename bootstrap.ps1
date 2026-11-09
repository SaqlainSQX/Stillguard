param([switch]$SkipModel)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:UV_CACHE_DIR = Join-Path $PSScriptRoot '.cache\uv'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $PSScriptRoot 'tools\python'
$env:UV_PYTHON_BIN_DIR = Join-Path $PSScriptRoot 'tools\bin'
$env:PIP_CACHE_DIR = Join-Path $PSScriptRoot '.cache\pip'
$env:XDG_CACHE_HOME = Join-Path $PSScriptRoot '.cache'
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/'
}
uv python install 3.12
if ($LASTEXITCODE -ne 0) { throw 'Python download failed.' }
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    uv venv .venv --python 3.12 --seed
    if ($LASTEXITCODE -ne 0) { throw 'Environment creation failed.' }
}
New-Item -ItemType Directory -Force -Path downloads/wheels,logs,manifests,results | Out-Null
& $python -m pip download 'torch==2.7.1+cu128' --index-url https://download.pytorch.org/whl/cu128 --dest downloads/wheels
if ($LASTEXITCODE -ne 0) { throw 'CUDA PyTorch download failed.' }
& $python -m pip download -r requirements.lock.txt --find-links downloads/wheels --dest downloads/wheels
if ($LASTEXITCODE -ne 0) { throw 'Package download failed.' }
& $python -m pip install --no-index --find-links downloads/wheels -r requirements.lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Installation failed.' }
& $python scripts/download_assets.py
if ($LASTEXITCODE -ne 0) { throw 'Reference download failed.' }
& $python scripts/inventory_downloads.py
if ($LASTEXITCODE -ne 0) { throw 'Inventory failed.' }
if (-not $SkipModel) {
    & .\download-model.ps1
}
& $python scripts/check_environment.py
& $python scripts/smoke_toolkits.py
if ($LASTEXITCODE -ne 0) { throw 'Toolkit smoke check failed.' }
