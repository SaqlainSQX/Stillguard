# Run this yourself in a local terminal if the saved Hugging Face login needs refreshing.
# The CLI prompts privately. Never put a token in this script or in chat.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& .\.venv\Scripts\hf.exe auth login
if ($LASTEXITCODE -ne 0) { throw 'Local Hugging Face sign-in did not complete.' }
& .\download-model.ps1
