$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$env:UV_CACHE_DIR = Join-Path $projectRoot '.cache\uv'
$env:PIP_CACHE_DIR = Join-Path $projectRoot '.cache\pip'
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    $runtime = Get-ChildItem -LiteralPath (Join-Path $projectRoot 'tools\python') -Filter python.exe -Recurse | Select-Object -First 1
    if (-not $runtime) { throw 'Project-local Python runtime is missing.' }
    & $runtime.FullName -m venv (Join-Path $projectRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Environment creation failed.' }
}
& $python -m pip install --no-index --find-links (Join-Path $projectRoot 'downloads\wheels') -r (Join-Path $projectRoot 'requirements.lock.txt')
if ($LASTEXITCODE -ne 0) { throw 'Offline installation failed.' }
& $python -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency check failed.' }
& $python (Join-Path $projectRoot 'scripts\check_environment.py')
