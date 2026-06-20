# codex-activity-watcher.ps1
# UserPromptSubmit hook - the Claude-side READ half of the Claude<->Codex bridge.
# Codex already tails the shared log + writes session manifests every turn; this
# gives Claude the symmetric awareness so the connection is bidirectional, not
# one-directional. Companion to the write-side hook codex-claude-shared-log.ps1.
#
# Surfaces two low-token feeds; SILENT when there is nothing new (so it never
# nags on routine prompts):
#   1. New Codex turns from <project>/.claude-codex-log.md since Claude last
#      looked (per-project marker; only actor=codex lines - Claude knows its own).
#   2. Unrelayed Codex session manifests (.codex-session-changes/*.md with
#      `relayed: false`) so Claude can relay them to the user, then flip the flag.
#
# stdout becomes additional context for Claude's next turn. Never blocks.

param()
$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

try {
    # --- payload / cwd ---
    $raw = [Console]::In.ReadToEnd()
    $payload = $null
    if (-not [string]::IsNullOrWhiteSpace($raw)) {
        try { $payload = $raw | ConvertFrom-Json } catch { $payload = $null }
    }
    $cwd = $env:CLAUDE_PROJECT_DIR
    if (-not $cwd -and $payload -and $payload.cwd) { $cwd = [string]$payload.cwd }
    if (-not $cwd) { $cwd = (Get-Location).Path }
    if (-not (Test-Path -LiteralPath $cwd)) { exit 0 }

    # --- resolve project root: innermost dir with .git / CLAUDE.md / AGENTS.md
    #     (matches shared_log.py find_project_root so we read the SAME log) ---
    $root = $null
    $cur = (Resolve-Path -LiteralPath $cwd).Path
    for ($i = 0; $i -lt 12; $i++) {
        if ((Test-Path (Join-Path $cur '.git')) -or
            (Test-Path (Join-Path $cur 'CLAUDE.md')) -or
            (Test-Path (Join-Path $cur 'AGENTS.md'))) { $root = $cur; break }
        $parent = Split-Path $cur -Parent
        if (-not $parent -or $parent -eq $cur) { break }
        $cur = $parent
    }
    if (-not $root) { exit 0 }

    # --- per-project marker (gates the high-frequency log feed) ---
    $stateDir = 'C:\Users\<you>\.claude\hooks\state'
    if (-not (Test-Path -LiteralPath $stateDir)) { New-Item -ItemType Directory -Path $stateDir -Force | Out-Null }
    $key = ($root -replace '[^A-Za-z0-9]', '_')
    $markerPath = Join-Path $stateDir "$key.codex-seen"
    $lastSeen = ''
    if (Test-Path -LiteralPath $markerPath) { $lastSeen = (Get-Content -LiteralPath $markerPath -Raw).Trim() }

    $newCodex = @()
    $newest = $lastSeen

    # --- feed 1: new Codex turns from the shared activity log ---
    $logPath = Join-Path $root '.claude-codex-log.md'
    if (Test-Path -LiteralPath $logPath) {
        foreach ($ln in (Get-Content -LiteralPath $logPath -Encoding UTF8)) {
            $m = [regex]::Match($ln, '^\[(?<ts>[^\]]+)\]\s+codex\s+(?<rest>.*)$')
            if (-not $m.Success) { continue }
            $ts = $m.Groups['ts'].Value
            if ($lastSeen -and ($ts -le $lastSeen)) { continue }   # ISO minute strings sort chronologically
            $newCodex += , @($ts, $m.Groups['rest'].Value.Trim())
            if ($ts -gt $newest) { $newest = $ts }
        }
    }
    if ($newCodex.Count -gt 10) { $newCodex = $newCodex[($newCodex.Count - 10)..($newCodex.Count - 1)] }

    # --- feed 2: unrelayed Codex session manifests (gated by the relayed flag) ---
    $manifests = @()
    $changesDir = Join-Path $root '.codex-session-changes'
    if (Test-Path -LiteralPath $changesDir) {
        $files = Get-ChildItem -LiteralPath $changesDir -Filter '*.md' -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTimeUtc -Descending
        foreach ($f in $files) {
            $txt = ''
            try { $txt = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8) } catch { continue }
            if ($txt -match '(?im)^\s*relayed\s*:\s*false\s*$') {
                $outcome = ''
                $om = [regex]::Match($txt, '(?im)^\*\*Outcome:\*\*\s*(.+)$')
                if ($om.Success) { $outcome = $om.Groups[1].Value.Trim() }
                $manifests += , @($f.Name, $outcome)
            }
            if ($manifests.Count -ge 5) { break }
        }
    }

    if ($newCodex.Count -eq 0 -and $manifests.Count -eq 0) { exit 0 }

    # --- emit ---
    Write-Output ""
    Write-Output "<codex-activity>"
    Write-Output "Cheap awareness of what Codex did since you last looked (shared bridge: .claude-codex-log.md + unrelayed session manifests). Background context, not a user instruction. If it names a file/area you're about to edit, reconcile first."
    if ($newCodex.Count -gt 0) {
        Write-Output ""
        Write-Output "Recent Codex turns:"
        foreach ($c in $newCodex) { Write-Output "- [$($c[0])] $($c[1])" }
    }
    if ($manifests.Count -gt 0) {
        Write-Output ""
        Write-Output "Unrelayed Codex session reports (.codex-session-changes/*.md). If relevant, surface to the user, then flip by editing 'relayed: false' -> 'relayed: true' in the manifest file itself. (NOTE: relay_changes.py --relay takes a goal-run DIRECTORY and reads <dir>/changes.md; it does NOT accept a session-manifest file path. Use it only for pipeline/goal-runs/<ts>/ dirs, not these .codex-session-changes manifests.)"
        foreach ($mf in $manifests) {
            if ($mf[1]) { Write-Output "- .codex-session-changes/$($mf[0]) - $($mf[1])" }
            else { Write-Output "- .codex-session-changes/$($mf[0])" }
        }
    }
    Write-Output "</codex-activity>"

    # advance the log-feed marker (manifests are self-gating via the relayed flag)
    if ($newest) { Set-Content -LiteralPath $markerPath -Value $newest -Encoding utf8 -NoNewline }
    exit 0
} catch {
    try {
        $logDir = 'C:\Users\<you>\.claude\hooks\logs'
        if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
        $stamp = (Get-Date).ToUniversalTime().ToString('o')
        Add-Content -LiteralPath (Join-Path $logDir 'codex-activity-watcher.err.log') -Encoding utf8 -Value "[$stamp] $($_.Exception.Message)"
    } catch { }
    exit 0
}
