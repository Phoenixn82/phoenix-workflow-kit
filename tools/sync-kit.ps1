<#
  sync-kit.ps1 - re-sync the shared workflow kit from the live machine.

  Pulls the current skills/hooks/scripts from their live locations, runs the privacy
  scrub + safety guard (scrub.py), rebuilds the dist zips, and reports what changed.
  Nothing is committed or pushed unless you pass -Commit / -Push.

  Source paths are derived from $env:USERPROFILE at runtime, so this script contains
  no real username and is safe to commit.

  Usage:
    pwsh tools/sync-kit.ps1                       # stage + scrub + rebuild + report
    pwsh tools/sync-kit.ps1 -Commit -Message "..."# also git commit
    pwsh tools/sync-kit.ps1 -Commit -Push -Message "..."  # commit + push
#>
[CmdletBinding()]
param(
  [switch]$Commit,
  [switch]$Push,
  [string]$Message
)
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$FW       = Join-Path $RepoRoot "framework"
$DIST     = Join-Path $RepoRoot "dist"
$HOMEDIR  = $env:USERPROFILE
$CLAUDE   = Join-Path $HOMEDIR ".claude"
$AIP      = Join-Path $HOMEDIR "Desktop\AI_Projects"

# NOTE: do NOT add "second-brain" here — that's also the shippable skill's dir name.
# The vault CONTENT (_system/second-brain, a sibling of _system/skills) is never mirrored,
# and scrub.py's path guard is the backstop. These extra excludes keep private dirs from
# ever being transiently staged before the scrub runs.
$ExcludeDirs  = @("__pycache__","node_modules",".git","logs","state","pipeline","tests","secrets","_staging","voice-corpus",".secrets","claude_vault",".codex")
$ExcludeFiles = @("*.log",".claude-codex-log.md","desktop.ini","Thumbs.db",".DS_Store","denylist.local.json")

function Sync-Tree($src, $dst) {
  if (-not (Test-Path $src)) { Write-Warning "skip (missing source): $src"; return }
  New-Item -ItemType Directory -Force -Path $dst | Out-Null
  $args = @($src, $dst, "/MIR","/NJH","/NJS","/NDL","/NP","/NFL","/R:1","/W:1")
  $args += "/XD"; $args += $ExcludeDirs
  $args += "/XF"; $args += $ExcludeFiles
  robocopy @args | Out-Null
  if ($LASTEXITCODE -ge 8) { throw "robocopy failed ($LASTEXITCODE) for $src" }
}

function Copy-One($src, $dst) {
  if (-not (Test-Path $src)) { Write-Warning "skip (missing source): $src"; return }
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
  Copy-Item -Path $src -Destination $dst -Force
}

Write-Host "== Staging live sources into framework/ ==" -ForegroundColor Cyan

# Mirrored subtrees (clean 1:1 source -> dest)
Sync-Tree (Join-Path $AIP "_system\skills")      (Join-Path $FW "_system\skills")
Sync-Tree (Join-Path $AIP "_system\tool-parity") (Join-Path $FW "_system\tool-parity")
Sync-Tree (Join-Path $CLAUDE "hooks")            (Join-Path $FW "harness\hooks")
Sync-Tree (Join-Path $CLAUDE "scripts")          (Join-Path $FW "harness\scripts")
Sync-Tree (Join-Path $CLAUDE "skills\codex-goal-dispatcher") (Join-Path $FW "harness\skills\codex-goal-dispatcher")

# Single files
Copy-One (Join-Path $AIP "AGENTS.md")              (Join-Path $FW "AGENTS.md")
Copy-One (Join-Path $AIP "CLAUDE.md")              (Join-Path $FW "CLAUDE.md")
Copy-One (Join-Path $AIP "DECISION_MAP.md")        (Join-Path $FW "DECISION_MAP.md")
Copy-One (Join-Path $AIP "SKILLS_INDEX.md")        (Join-Path $FW "SKILLS_INDEX.md")
Copy-One (Join-Path $AIP "RELIABILITY_STANDARD.md")(Join-Path $FW "RELIABILITY_STANDARD.md")
Copy-One (Join-Path $AIP "_system\verify-bridge.py") (Join-Path $FW "_system\verify-bridge.py")
Copy-One (Join-Path $CLAUDE "CLAUDE.md")           (Join-Path $FW "harness\CLAUDE.global.md")
Copy-One (Join-Path $CLAUDE "settings.json")       (Join-Path $FW "harness\settings.reference.json")
Copy-One (Join-Path $HOMEDIR "agentic-os\bin\aos_lock.py") (Join-Path $FW "agentic-os\aos_lock.py")
# NOTE: framework/MANIFEST.md and framework/agentic-os/spawn-args.ts have no live source
#       and are preserved as-is (not overwritten, not deleted).

Write-Host "== Privacy scrub + safety guard ==" -ForegroundColor Cyan
python (Join-Path $PSScriptRoot "scrub.py") $FW
if ($LASTEXITCODE -ne 0) {
  Write-Host "ABORT: scrub blocked. Nothing was committed. Resolve the items above and re-run." -ForegroundColor Red
  exit 2
}

Write-Host "== Rebuilding dist zips ==" -ForegroundColor Cyan
Add-Type -AssemblyName System.IO.Compression.FileSystem
function Rebuild-Zip($srcDir, $zipPath) {
  if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
  [System.IO.Compression.ZipFile]::CreateFromDirectory($srcDir, $zipPath, [System.IO.Compression.CompressionLevel]::Optimal, $false)
}
New-Item -ItemType Directory -Force -Path $DIST | Out-Null
$fwZip = Join-Path $DIST "phoenix-workflow-framework.zip"
Rebuild-Zip $FW $fwZip

# Full kit zip = pamphlet + prompt + framework.zip + a short README.txt
$stage = Join-Path $PSScriptRoot "_staging"
if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $stage | Out-Null
Copy-Item -LiteralPath (Join-Path $RepoRoot "phoenix-workflow-pamphlet.html") -Destination $stage -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "implementation-prompt.md") -Destination $stage -Force
Copy-Item -LiteralPath $fwZip -Destination $stage -Force
$kitReadme = @"
# AI Workflow - share kit

1. Open  phoenix-workflow-pamphlet.html  in a browser. Read the philosophy (~5 min).
2. Copy the implementation prompt (button in the pamphlet, or implementation-prompt.md).
3. Paste it into WHATEVER AI you use, and attach  phoenix-workflow-framework.zip.
4. Answer its questions - it maps the framework's roles onto your own AIs and takes only what fits.

Paths inside are placeholders (C:\Users\<you>\...) and the operator is generalized as 'the user' -
your AI rewrites both for your machine.
"@
Set-Content -LiteralPath (Join-Path $stage "README.txt") -Value $kitReadme -Encoding UTF8
$kitZip = Join-Path $DIST "phoenix-workflow-kit.zip"
Rebuild-Zip $stage $kitZip
Remove-Item -LiteralPath $stage -Recurse -Force

Write-Host "== Git status ==" -ForegroundColor Cyan
Push-Location $RepoRoot
try {
  git add -A
  git status --short
  Write-Host ""
  git diff --cached --stat | Select-Object -Last 40
  if ($Commit) {
    if (-not $Message) { $Message = "sync: update workflow kit from live sources" }
    git commit -m $Message | Out-Null
    Write-Host "Committed: $Message" -ForegroundColor Green
    if ($Push) { git push; Write-Host "Pushed." -ForegroundColor Green }
  } else {
    Write-Host "`nReview the diff above. Re-run with -Commit (and -Push) to publish." -ForegroundColor Yellow
  }
} finally { Pop-Location }
