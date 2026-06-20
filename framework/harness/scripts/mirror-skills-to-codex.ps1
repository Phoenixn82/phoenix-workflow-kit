# mirror-skills-to-codex.ps1
# Re-syncs the user's mechanic/wrench skills into the Codex skill directory via
# Windows junctions, so Codex sees the same skills Claude does.
#
# Canonical source : C:\Users\<you>\Desktop\AI_Projects\_system\skills\<name>
# Codex mirror      : C:\Users\<you>\.codex\skills\<name>  (junction -> source)
#
# Idempotent + safe to re-run. Removes ONLY stale junctions (reparse points),
# never real directories/files (e.g. a real ".system" dir is left untouched).
# Manual / skill-invoked only — nothing auto-fires (per AGENTS.md hard rule #1).
# Run after adding or renaming a skill under _system/skills.

$ErrorActionPreference = 'Stop'
$src = 'C:\Users\<you>\Desktop\AI_Projects\_system\skills'
$dst = 'C:\Users\<you>\.codex\skills'

if (-not (Test-Path -LiteralPath $src)) { Write-Error "Source skills dir not found: $src"; exit 1 }
New-Item -ItemType Directory -Force -Path $dst | Out-Null

# 1) Remove existing junctions (reparse points) only. Leave real dirs/files alone.
$removed = 0
Get-ChildItem -LiteralPath $dst -Force | ForEach-Object {
  if ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) {
    cmd /c rmdir "$($_.FullName)" 2>$null
    if (-not (Test-Path -LiteralPath $_.FullName)) { $removed++ }
  }
}

# 2) Create a fresh junction for every skill directory in the canonical source.
$created = 0
Get-ChildItem -LiteralPath $src -Directory | ForEach-Object {
  $link = Join-Path $dst $_.Name
  if (-not (Test-Path -LiteralPath $link)) {
    New-Item -ItemType Junction -Path $link -Target $_.FullName | Out-Null
    $created++
  }
}

Write-Output "mirror-skills-to-codex: removed $removed stale junction(s), created $created fresh junction(s)."
Write-Output "Source: $src"
Write-Output "Mirror: $dst"
