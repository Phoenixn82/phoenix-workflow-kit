# codex-handoff-watcher.ps1
# UserPromptSubmit hook — scans the active project's .codex-claude-handoff dir
# for any *.request.md without a matching *.done.md and injects them as
# additional context for Claude's next turn.
#
# Output to stdout becomes additional context appended to the user's prompt.
# Stays silent (no output) when there's nothing pending — zero noise.

param()

$ErrorActionPreference = 'SilentlyContinue'

# Ensure UTF-8 I/O — Claude/Codex files contain em-dashes, arrows, etc.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

try {
    $raw = [Console]::In.ReadToEnd()
    if (-not [string]::IsNullOrWhiteSpace($raw)) {
        $payload = $raw | ConvertFrom-Json
    }
} catch {
    $payload = $null
}

# Resolve the project root. Prefer the env Claude exposes; fall back to CWD.
$projectRoot = $env:CLAUDE_PROJECT_DIR
if (-not $projectRoot) {
    if ($payload -and $payload.cwd) {
        $projectRoot = [string]$payload.cwd
    } else {
        $projectRoot = (Get-Location).Path
    }
}

if (-not $projectRoot -or -not (Test-Path $projectRoot)) {
    exit 0
}

# Walk up from $projectRoot looking for .codex-claude-handoff/ (Codex may have
# written into a parent dir if it considers the parent the project root).
$current = (Resolve-Path $projectRoot).Path
$handoffDir = $null
for ($i = 0; $i -lt 6; $i++) {
    $candidate = Join-Path $current '.codex-claude-handoff'
    if (Test-Path $candidate) {
        $handoffDir = $candidate
        break
    }
    $parent = Split-Path $current -Parent
    if (-not $parent -or $parent -eq $current) { break }
    $current = $parent
}

if (-not $handoffDir) { exit 0 }

# Find pending requests: *.request.md files whose matching *.done.md is absent.
$requests = Get-ChildItem -Path $handoffDir -Filter '*.request.md' -ErrorAction SilentlyContinue
if (-not $requests) { exit 0 }

$pending = @()
foreach ($req in $requests) {
    $id = $req.BaseName -replace '\.request$',''
    $donePath = Join-Path $handoffDir "$id.done.md"
    if (-not (Test-Path $donePath)) {
        $pending += $req
    }
}

if ($pending.Count -eq 0) { exit 0 }

# Emit a single block Claude will see as additional context for this turn.
Write-Output ""
Write-Output "<codex-handoff-pending>"
Write-Output "Codex has left $($pending.Count) pending handoff request(s) for you in $handoffDir."
Write-Output "Read each one, fire the named skill, then write a matching <id>.done.md per the schema in ~/.codex/AGENTS.md so Codex can resume."
Write-Output ""
foreach ($req in $pending) {
    Write-Output "## $($req.Name)"
    try {
        $content = [System.IO.File]::ReadAllText($req.FullName, [System.Text.Encoding]::UTF8)
        Write-Output $content
    } catch {
        Write-Output "(could not read $($req.FullName): $_)"
    }
    Write-Output ""
}
Write-Output "</codex-handoff-pending>"
exit 0
