$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:HF_HUB_DISABLE_TELEMETRY = '1'
& .\.venv\Scripts\python.exe -u scripts/download_model.py
$model = Get-Content -LiteralPath 'manifests\model.json' -Raw | ConvertFrom-Json
if (-not $model.complete) { throw 'Model download is incomplete; check gated-model access and manifests/model.json.' }
