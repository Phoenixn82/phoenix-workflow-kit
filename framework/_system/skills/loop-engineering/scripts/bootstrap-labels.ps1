<#
.SYNOPSIS
  Bootstrap the 11 loop-engineering managed labels on a GitHub repo.
.DESCRIPTION
  Dry-run by default (reports which labels are missing, creates nothing).
  Pass -Apply to create the missing labels via `gh label create`.
.EXAMPLE
  pwsh bootstrap-labels.ps1 -Repo <your-github>/agentic-os-97
  pwsh bootstrap-labels.ps1 -Repo <your-github>/agentic-os-97 -Apply
#>
[CmdletBinding()]
param(
  [string]$Repo = "<your-github>/agentic-os-97",
  [switch]$Apply
)

$ErrorActionPreference = "Stop"

$labels = @(
  @{ name = "risk:low";      color = "0E8A16"; desc = "Low-risk issue, safe for agent execution when agent:ready" },
  @{ name = "risk:medium";   color = "FBCA04"; desc = "Possibly agent-suitable later; not unattended by default" },
  @{ name = "risk:high";     color = "B60205"; desc = "Human-led; agents may investigate/plan, not execute unattended" },
  @{ name = "type:bug";      color = "5319E7"; desc = "Incorrect behavior or regression" },
  @{ name = "type:feature";  color = "5319E7"; desc = "New user- or developer-facing capability" },
  @{ name = "type:docs";     color = "5319E7"; desc = "Docs, examples, README, comments, links" },
  @{ name = "type:test";     color = "5319E7"; desc = "Test additions, fixes, coverage, fixtures" },
  @{ name = "type:refactor"; color = "5319E7"; desc = "Internal restructuring, no behavior change" },
  @{ name = "type:chore";    color = "5319E7"; desc = "Deps, build, CI config, formatting, cleanup" },
  @{ name = "agent:ready";   color = "1D76DB"; desc = "Permission for the worker loop to pick up this issue" },
  @{ name = "needs:human";   color = "D93F0B"; desc = "A human decision/clarification/judgment is required" }
)

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  Write-Error "gh CLI not found on PATH. Install GitHub CLI and authenticate."; exit 1
}
& gh auth status 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Error "gh is not authenticated. Run 'gh auth login'."; exit 1 }

$existing = (& gh label list --repo $Repo --limit 200 --json name | ConvertFrom-Json).name
$mode = if ($Apply) { "APPLY" } else { "DRY-RUN" }
Write-Output "[$mode] loop-engineering labels on $Repo"

$missing = 0; $created = 0
foreach ($l in $labels) {
  if ($existing -contains $l.name) { Write-Output "  ok      $($l.name)"; continue }
  $missing++
  if ($Apply) {
    & gh label create $l.name --color $l.color --description $l.desc --repo $Repo --force | Out-Null
    if ($LASTEXITCODE -eq 0) { $created++; Write-Output "  created $($l.name)" }
    else { Write-Output "  FAILED  $($l.name)" }
  }
  else {
    Write-Output "  missing $($l.name)  (would create #$($l.color))"
  }
}

if ($Apply) {
  Write-Output "Summary: $($labels.Count) managed labels, $missing were missing, $created created."
}
else {
  Write-Output "Summary: $($labels.Count) managed labels, $missing missing (dry-run, nothing created). Re-run with -Apply to create."
}
