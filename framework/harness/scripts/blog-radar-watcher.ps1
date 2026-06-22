# Passive: surface top blog-radar candidates at session start. No spend, no prompt.
$ErrorActionPreference = "SilentlyContinue"
$radar = "C:\Users\<you>\Desktop\AI_Projects\_system\second-brain\Blog\_RADAR.md"
if (-not (Test-Path $radar)) { exit 0 }

$lines = Get-Content $radar
$weekly = ($lines | Where-Object { $_ -match "Weekly digest" } | Select-Object -First 1)
$cands = $lines | Where-Object { $_ -match "^\| .+\*\*(NEW_ANCHOR|UPDATE_ARTICLE|STALE|WEEKLY_ITEM)\*\*" }

if (-not $cands -and $weekly -notmatch "READY") { exit 0 }

Write-Output "<blog-radar>"
Write-Output "Personal-site blog candidates (detector only; fire /blog-write to act). Source: Blog/_RADAR.md"
if ($weekly) { Write-Output $weekly }
$cands | Select-Object -First 6 | ForEach-Object { Write-Output $_ }
Write-Output "</blog-radar>"
exit 0
