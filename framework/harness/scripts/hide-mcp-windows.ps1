# hide-mcp-windows.ps1
# Hides the cmd.exe consoles spawned for stdio-piped MCP servers.
# Process + stdio stay alive; only the visible window is hidden.
#
# Fires from settings.json SessionStart hook. Safe to invoke ad-hoc too:
#   powershell -NoProfile -File "$HOME\.claude\scripts\hide-mcp-windows.ps1"
#
# Output is JSON so Claude Code's hook system can read it.

$ErrorActionPreference = 'Stop'

function Write-HookLog {
    param(
        [Parameter(Mandatory = $true)]
        [System.Management.Automation.ErrorRecord]$ErrorRecord
    )

    try {
        $logDir = 'C:\Users\<you>\.claude\hooks\logs'
        if (-not (Test-Path -LiteralPath $logDir)) {
            New-Item -ItemType Directory -Path $logDir -Force | Out-Null
        }

        $logFile = Join-Path $logDir 'hide-mcp-windows.log'
        $stamp = (Get-Date).ToString('o')
        Add-Content -LiteralPath $logFile -Encoding utf8 -Value "[$stamp] $($ErrorRecord.Exception.Message)`n$($ErrorRecord.ScriptStackTrace)`n"
    } catch {
        # Logging must never make a hook visible to Claude Code.
    }
}

try {
    # Claude Code hook input arrives as JSON on stdin. The payload is not needed
    # for this hook's behavior, but malformed hook input should still be silent.
    $raw = [Console]::In.ReadToEnd()
    if ($raw -and $raw.Trim().Length -gt 0) {
        try {
            $null = $raw | ConvertFrom-Json
        } catch {
            exit 0
        }
    }

    # Patterns identifying MCP server cmd processes the user never needs to see.
    # Each plugin's `.mcp.json` should be discoverable here as a substring.
    $mcpPatterns = @(
        'context7-mcp',
        'chrome-devtools-mcp',
        'mcp-server-supabase',
        'mcp-server-',
        '@modelcontextprotocol',
        'gemini-mcp'
    )

    # Pause briefly so the spawn race settles; at SessionStart the windows may
    # not have main handles yet.
    Start-Sleep -Milliseconds 800

    if (-not ('Win32.Native' -as [type])) {
        Add-Type -Namespace Win32 -Name Native -MemberDefinition @'
[System.Runtime.InteropServices.DllImport("user32.dll")]
public static extern bool ShowWindow(System.IntPtr hWnd, int nCmdShow);
[System.Runtime.InteropServices.DllImport("user32.dll")]
public static extern bool IsWindowVisible(System.IntPtr hWnd);
'@
    }

    $SW_HIDE = 0
    $hidden = 0
    $skipped = 0

    $candidates = @(Get-CimInstance Win32_Process -Filter "Name='cmd.exe'" -ErrorAction SilentlyContinue)
    foreach ($c in $candidates) {
        if (-not $c.CommandLine) { continue }

        $cmdline = $c.CommandLine
        $matched = $false
        foreach ($p in $mcpPatterns) {
            if ($cmdline -like "*$p*") {
                $matched = $true
                break
            }
        }
        if (-not $matched) { continue }

        try {
            $proc = Get-Process -Id $c.ProcessId -ErrorAction Stop
        } catch {
            $skipped++
            continue
        }

        $h = $proc.MainWindowHandle
        if (-not $h -or $h -eq [System.IntPtr]::Zero) {
            $skipped++
            continue
        }

        if ([Win32.Native]::IsWindowVisible($h)) {
            [Win32.Native]::ShowWindow($h, $SW_HIDE) | Out-Null
            $hidden++
        }
    }

    # Hooks read JSON from stdout: stay silent unless there is a message worth
    # surfacing. Skip the systemMessage when nothing was hidden to keep the UI quiet.
    if ($hidden -gt 0) {
        $msg = "Hid $hidden MCP server window(s)"
        if ($skipped -gt 0) { $msg += " ($skipped not yet ready)" }
        @{ systemMessage = $msg; suppressOutput = $true } | ConvertTo-Json -Compress
    }

    exit 0
} catch [System.Exception] {
    Write-HookLog -ErrorRecord $_
    exit 0
}
