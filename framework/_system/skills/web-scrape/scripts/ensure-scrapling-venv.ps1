$ErrorActionPreference = "Stop"

$SkillRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvDir = Join-Path $SkillRoot ".venv-scrapling"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$VenvScrapling = Join-Path $VenvDir "Scripts\scrapling.exe"
$Requirements = Join-Path $SkillRoot "requirements-scrapling.txt"

if (-not (Test-Path $Requirements)) {
    throw "Missing requirements file: $Requirements"
}

if ((Get-Item $Requirements).Length -le 0) {
    throw "Requirements file is empty: $Requirements"
}

if (-not (Test-Path $VenvPython)) {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $Python) {
        throw "python was not found on PATH; install Python 3, then rerun this script."
    }

    & $Python.Source -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        throw "python -m venv failed with exit code $LASTEXITCODE"
    }
}

if (-not (Test-Path $VenvScrapling)) {
    & $VenvPython -m pip install -r $Requirements
    if ($LASTEXITCODE -ne 0) {
        throw "pip install -r requirements-scrapling.txt failed with exit code $LASTEXITCODE"
    }
}

Write-Host "Scrapling venv ready: $VenvDir"
