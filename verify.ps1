$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $python -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency check failed.' }
& $python scripts/check_environment.py
if ($LASTEXITCODE -ne 0) { throw 'Environment check failed.' }
& $python scripts/smoke_toolkits.py
if ($LASTEXITCODE -ne 0) { throw 'Toolkit smoke check failed.' }
$model = Get-Content -LiteralPath 'manifests\model.json' -Raw | ConvertFrom-Json
if ($model.complete) {
    & $python scripts/smoke_model.py
    if ($LASTEXITCODE -ne 0) { throw 'Model smoke check failed.' }
} else {
    Write-Output 'Model check pending: weights have not finished downloading. See manifests/model.json.'
}
