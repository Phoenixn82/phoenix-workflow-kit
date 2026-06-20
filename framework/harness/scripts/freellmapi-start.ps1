# freellmapi-start.ps1 - idempotent, hidden auto-start for the local FreeLLMAPI router.
#
# Invoked by the "FreeLLMAPI Router" Scheduled Task (at logon + every 30 min as a watchdog).
# Safe to run repeatedly and safe to double-click: if :3001 already answers, it exits
# without spawning a duplicate. If the server is down (crash / fresh boot), it relaunches it
# hidden and detached, then readiness-gates the boot and logs the outcome.
#
# Zero Claude involvement - once the task is registered the OS keeps the lane alive.
# NOTE: keep this file pure ASCII. Windows PowerShell 5.1 reads BOM-less files as cp1252,
# which corrupts non-ASCII chars (em-dashes etc.) and breaks the parser.

$ErrorActionPreference = 'Stop'

$installDir = 'C:\Users\<you>\Documents\Codex\2026-05-25\tashfeenahmed-freellmapi-https-github-com-tashfeenahmed'
$entry      = Join-Path $installDir 'server\dist\index.js'
$port       = 3001
$svcOut     = Join-Path $installDir 'freellmapi.svc.out.log'
$svcErr     = Join-Path $installDir 'freellmapi.svc.err.log'
$lifeLog    = Join-Path $installDir 'freellmapi-start.log'

function Write-Life([string]$msg) {
    "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $msg" | Out-File -FilePath $lifeLog -Append -Encoding utf8
}

function Test-Up {
    try {
        $null = Invoke-RestMethod -Uri "http://127.0.0.1:$port/v1/models" -TimeoutSec 3 -ErrorAction Stop
        return $true
    } catch { return $false }
}

# 1. Idempotent: already up? Nothing to do.
if (Test-Up) { exit 0 }

# 2. Self-healing: the build must exist.
if (-not (Test-Path $entry)) {
    Write-Life "ERROR build missing at $entry - run: npm run build:server"
    exit 1
}

# 3. Resolve node.
$node = (Get-Command node -ErrorAction SilentlyContinue).Source
if (-not $node) {
    Write-Life "ERROR node not found on PATH"
    exit 1
}

# 4. Start hidden + detached, server stdout/stderr teed to service logs.
Write-Life "START launching node $entry"
Start-Process -FilePath $node -ArgumentList "`"$entry`"" -WorkingDirectory $installDir -WindowStyle Hidden -RedirectStandardOutput $svcOut -RedirectStandardError $svcErr | Out-Null

# 5. Readiness-gate the boot (fail loud with a map if it never comes up).
$deadline = (Get-Date).AddSeconds(30)
while ((Get-Date) -lt $deadline) {
    if (Test-Up) { Write-Life "OK up on :$port"; exit 0 }
    Start-Sleep -Milliseconds 750
}
Write-Life "ERROR did not answer on :$port within 30s - check $svcErr"
exit 1
