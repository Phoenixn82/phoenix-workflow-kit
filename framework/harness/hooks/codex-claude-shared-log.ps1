# Claude PostToolUse hook for the shared Claude/Codex activity log.
# Silent by design: never prints context, never blocks Claude.

$ErrorActionPreference = "Stop"

function Shorten([string]$Text, [int]$Limit = 150) {
    if (-not $Text) { return "" }
    $clean = ($Text -replace "\s+", " ").Trim()
    $clean = $clean -replace "(?i)(api[_-]?key|token|secret|password)\s*=\s*\S+", '$1=<redacted>'
    $clean = $clean -replace "sk-[A-Za-z0-9_-]{12,}", "sk-<redacted>"
    if ($clean.Length -gt $Limit) { return $clean.Substring(0, $Limit - 1) + "..." }
    return $clean
}

function RelativePath([string]$Path, [string]$Root) {
    if (-not $Path) { return "" }
    try {
        $full = [IO.Path]::GetFullPath($Path)
        $base = [IO.Path]::GetFullPath($Root)
        if (-not $base.EndsWith("\")) { $base += "\" }
        if ($full.StartsWith($base, [StringComparison]::OrdinalIgnoreCase)) {
            return $full.Substring($base.Length)
        }
        return $full
    } catch {
        return $Path
    }
}

try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }

    try { $payload = $raw | ConvertFrom-Json } catch { exit 0 }
    if (-not $payload) { exit 0 }

    $tool = [string]$payload.tool_name
    $loggedTools = @("Edit", "MultiEdit", "Write", "NotebookEdit", "Bash", "PowerShell")
    if ($loggedTools -notcontains $tool) { exit 0 }

    $cwd = [string]$payload.cwd
    if (-not $cwd -or -not (Test-Path -LiteralPath $cwd)) { exit 0 }

    $emitter = "C:\Users\<you>\.claude\skills\codex-goal-dispatcher\scripts\shared_log.py"
    if (-not (Test-Path -LiteralPath $emitter)) { exit 0 }

    $projectRoot = (& python $emitter find-project --cwd $cwd 2>$null)
    if ($LASTEXITCODE -ne 0 -or -not $projectRoot) { exit 0 }
    $projectRoot = $projectRoot.Trim()
    if (-not (Test-Path -LiteralPath $projectRoot)) { exit 0 }

    $action = "note"
    $summary = ""

    switch ($tool) {
        "Edit" {
            $action = "edit"
            $summary = "edited $(RelativePath ([string]$payload.tool_input.file_path) $projectRoot)"
        }
        "MultiEdit" {
            $action = "edit"
            $summary = "multi-edited $(RelativePath ([string]$payload.tool_input.file_path) $projectRoot)"
        }
        "Write" {
            $action = "write"
            $summary = "wrote $(RelativePath ([string]$payload.tool_input.file_path) $projectRoot)"
        }
        "NotebookEdit" {
            $action = "edit"
            $summary = "edited notebook $(RelativePath ([string]$payload.tool_input.notebook_path) $projectRoot)"
        }
        { $_ -in @("Bash", "PowerShell") } {
            $action = "run"
            $description = [string]$payload.tool_input.description
            $command = [string]$payload.tool_input.command
            $summary = "ran: $(Shorten $(if ($description) { $description } else { $command }))"
        }
    }

    if (-not $summary) { exit 0 }
    if ($summary -match "\.claude-codex-log\.md") { exit 0 }
    if ($summary -match "pipeline[\\/]goal-runs[\\/].*(status|attempts|events)\.") { exit 0 }

    & python $emitter append --project $projectRoot --actor claude --action $action --summary $summary 2>$null | Out-Null
    exit 0
} catch {
    try {
        $logDir = "C:\Users\<you>\.claude\hooks\logs"
        if (-not (Test-Path -LiteralPath $logDir)) {
            New-Item -ItemType Directory -Path $logDir -Force | Out-Null
        }
        $stamp = (Get-Date).ToUniversalTime().ToString("o")
        Add-Content -LiteralPath (Join-Path $logDir "codex-claude-shared-log.err.log") -Encoding utf8 -Value "[$stamp] $($_.Exception.Message)"
    } catch { }
    exit 0
}
