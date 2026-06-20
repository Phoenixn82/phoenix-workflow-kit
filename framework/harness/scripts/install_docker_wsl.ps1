# Elevated installer for WSL2 + Docker Desktop.
# Spawned by claude via Start-Process -Verb RunAs so this runs as Administrator.
# Logs to a known path so the non-elevated parent can tail progress.

$LogFile = "C:\Users\<you>\.claude\logs\install_docker_wsl.log"
$null = New-Item -ItemType Directory -Force -Path (Split-Path $LogFile)

function Log($msg) {
    $line = "[$((Get-Date).ToString('s'))] $msg"
    $line | Tee-Object -FilePath $LogFile -Append | Out-Host
}

Log "===== install_docker_wsl.ps1 START ====="
Log "Running as user: $env:USERNAME"
Log "Admin: $(([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator))"

# --- WSL2 ---
Log "--- Installing WSL2 ---"
try {
    & wsl.exe --install --no-launch 2>&1 | ForEach-Object { Log "wsl: $_" }
    Log "wsl --install exit code: $LASTEXITCODE"
} catch {
    Log "WSL install threw: $($_.Exception.Message)"
}

# Set WSL2 as default version (idempotent if already)
try {
    & wsl.exe --set-default-version 2 2>&1 | ForEach-Object { Log "wsl-default: $_" }
} catch {
    Log "wsl --set-default-version threw: $($_.Exception.Message)"
}

# --- Docker Desktop ---
Log "--- Installing Docker Desktop via winget ---"
try {
    & winget install --id Docker.DockerDesktop `
        --accept-package-agreements `
        --accept-source-agreements `
        --silent `
        --disable-interactivity 2>&1 | ForEach-Object { Log "winget: $_" }
    Log "winget exit code: $LASTEXITCODE"
} catch {
    Log "Docker Desktop install threw: $($_.Exception.Message)"
}

Log "===== install_docker_wsl.ps1 DONE ====="
Log "Reboot REQUIRED for WSL2 + Docker Desktop to become active."
"COMPLETE" | Out-File -FilePath "C:\Users\<you>\.claude\logs\install_docker_wsl.done" -Encoding ascii
