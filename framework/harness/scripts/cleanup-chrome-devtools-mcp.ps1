# Kill any orphaned chrome.exe processes left over from a previous
# chrome-devtools-mcp session, and clear the SingletonLock so the next
# session can launch a fresh browser instance.
#
# Wired into SessionStart in C:/Users/<you>/.claude/settings.json so it
# runs at the top of every Claude Code session, async + short timeout.

$ErrorActionPreference = "SilentlyContinue"

try {
  Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" |
    Where-Object { $_.CommandLine -match 'chrome-devtools-mcp' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
} catch {}

$profile = "$env:USERPROFILE\.cache\chrome-devtools-mcp\chrome-profile"
if (Test-Path $profile) {
  foreach ($lock in @("lockfile", "SingletonLock", "SingletonCookie", "SingletonSocket")) {
    $p = Join-Path $profile $lock
    if (Test-Path $p) {
      try { Remove-Item -Force $p } catch {}
    }
  }
}
