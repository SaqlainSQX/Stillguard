$projectRoot = $PSScriptRoot
$env:UV_CACHE_DIR = Join-Path $projectRoot '.cache\uv'
$env:PIP_CACHE_DIR = Join-Path $projectRoot '.cache\pip'
$env:XDG_CACHE_HOME = Join-Path $projectRoot '.cache'
$env:HF_HUB_CACHE = Join-Path $projectRoot '.cache\huggingface\hub'
$env:HF_DATASETS_CACHE = Join-Path $projectRoot '.cache\huggingface\datasets'
$env:HF_HUB_DISABLE_TELEMETRY = '1'
$env:WANDB_MODE = 'disabled'
& (Join-Path $projectRoot '.venv\Scripts\Activate.ps1')
Set-Location -LiteralPath $projectRoot
