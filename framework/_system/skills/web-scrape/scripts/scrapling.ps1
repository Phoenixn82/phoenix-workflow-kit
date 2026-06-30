$ErrorActionPreference = "Stop"

$Ensure = Join-Path $PSScriptRoot "ensure-scrapling-venv.ps1"
& $Ensure

$SkillRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Scrapling = Join-Path $SkillRoot ".venv-scrapling\Scripts\scrapling.exe"

& $Scrapling @args
exit $LASTEXITCODE
