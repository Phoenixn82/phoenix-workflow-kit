# Claude PostToolUse hook: aos_lock read-fingerprinting (bridge read-side).
#
# Pipes the Read tool event JSON to "aos_lock.py hook postuse-read" so Claude's
# reads are recorded as sha256 fingerprints in
# ~/agentic-os/locks/session_reads/<session_id>.json. This is the Claude half
# of the shared Claude/Codex stale-read gate: it lets either side see what the
# other has read, and seeds the fingerprints an acquire would later check.
#
# Scope by design: read-fingerprinting ONLY. There is intentionally NO
# PreToolUse acquire hook on Edit/Write. aos_lock's preuse-edit gate exits 2
# (deny-with-feedback) whenever the session has no prior read fingerprint for a
# file -- which would block routine Claude edits (overwrites, harness-cached
# reads, or a read whose async fingerprint has not landed yet). That friction
# breaks the user's no-permission-prompts / never-block-routine-work rule, so
# acquire/release stay a manual or skill-invoked step:
#   python C:/Users/<you>/agentic-os/bin/aos_lock.py acquire <path> --agent claude --intent "..."
#   python C:/Users/<you>/agentic-os/bin/aos_lock.py release <path>
#
# Silent by design: never prints context, never blocks Claude. Pure ASCII.

$ErrorActionPreference = "Stop"

try {
    $aosLock = "C:\Users\<you>\agentic-os\bin\aos_lock.py"
    if (-not (Test-Path -LiteralPath $aosLock)) { exit 0 }

    # Read Claude's raw stdin payload as UTF-8 directly off the standard input
    # stream, bypassing [Console]::InputEncoding (which is the OEM code page in
    # PowerShell 5.1 and would corrupt non-ASCII file paths in the payload).
    $stdin = [Console]::OpenStandardInput()
    $reader = New-Object System.IO.StreamReader($stdin, (New-Object System.Text.UTF8Encoding $false))
    try {
        $raw = $reader.ReadToEnd()
    } finally {
        $reader.Dispose()
    }
    if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }

    # Force python's stdin/stdout to UTF-8, and encode the pipe write as UTF-8
    # without a BOM, so the JSON survives the PowerShell -> python hop intact.
    $env:PYTHONUTF8 = "1"
    $env:PYTHONIOENCODING = "utf-8"
    $prevOut = $OutputEncoding
    $OutputEncoding = New-Object System.Text.UTF8Encoding $false
    try {
        $raw | & python $aosLock hook postuse-read 2>$null | Out-Null
    } finally {
        $OutputEncoding = $prevOut
    }
    exit 0
} catch {
    try {
        $logDir = "C:\Users\<you>\.claude\hooks\logs"
        if (-not (Test-Path -LiteralPath $logDir)) {
            New-Item -ItemType Directory -Path $logDir -Force | Out-Null
        }
        $stamp = (Get-Date).ToUniversalTime().ToString("o")
        Add-Content -LiteralPath (Join-Path $logDir "aos-lock-read-fingerprint.err.log") -Encoding utf8 -Value "[$stamp] $($_.Exception.Message)"
    } catch { }
    exit 0
}
