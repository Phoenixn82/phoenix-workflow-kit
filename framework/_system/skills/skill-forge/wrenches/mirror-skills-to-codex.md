---
name: skill-forge-mirror-skills-to-codex
description: Mirrors every Claude skill into Codex's skill directory using Windows junction points so both runtimes share one source of truth. Manual, idempotent re-sync — nothing auto-fires (AGENTS.md hard rule #1). Invoked for bulk re-sync / recovery after adding, renaming, or removing a skill. Trigger phrases include "mirror skills to codex", "sync skills to codex", "audit skill drift between claude and codex", "bulk re-sync skills".
---

# skill-forge-mirror-skills-to-codex — Claude → Codex sync via junctions

The user uses both Claude and Codex. Both runtimes have a skill system. Maintaining two copies of every skill is the duplicate-state trap. This wrench mirrors via Windows junction points so there's one source of truth.

---

## When to fire

- "Sync skills to codex" / "mirror skills"
- "Audit skill drift between claude and codex"
- After bulk manual edits to confirm Codex side is current
- After this rebuild's Phase 7 relocation, to re-establish junctions

Don't fire when:
- The user wants to delete from Codex side specifically (manual)

Note: there is **no** auto-sync hook — after any single-skill add/rename/remove you must re-run the script below; the junctions do not refresh themselves.

---

## How junction-based mirroring works

Windows junction points are filesystem-level "this path IS another path." Unlike symlinks (which need elevation), junctions work as a regular user.

```
C:\Users\<you>\.codex\skills\<skill-name>
  ↓ (junction)
C:\Users\<you>\Desktop\AI_Projects\_system\skills\<skill-name>
```

Both paths show the same files. Edit one, both update. Delete one (carefully), both go.

---

## Re-sync (this wrench's main job)

Mirroring is a manual, idempotent re-sync. Nothing auto-fires (AGENTS.md hard rule #1). Run the script after adding, renaming, or removing a skill under `_system/skills`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\<you>\.claude\scripts\mirror-skills-to-codex.ps1
```

The script (`~/.claude/scripts/mirror-skills-to-codex.ps1`):
- Clears stale junctions in `~/.codex/skills` (reparse points only — never real dirs like `.system`)
- Creates a fresh junction `~/.codex/skills/<name>` → `C:\Users\<you>\Desktop\AI_Projects\_system\skills\<name>` for every skill on disk
- Is safe to re-run; reports how many junctions it removed and created

Last full rebuild: 2026-05-30 (cleared 125 old-generation junctions, created 19 for the skills present then). Drift since: `_system/skills` now has 21 dirs but `~/.codex/skills` has only 20 junctions — `analytics-sites` landed later with no re-sync (and is also missing a `SKILL.md`, so confirm it's a complete skill before mirroring). Re-run the script to reconcile. Junctions work as a regular user; no elevation needed.

---

## Auditing drift

The script takes **no flags** (no `--audit` / `--fix`) — it is a single idempotent re-sync. To audit drift, just re-run it: it tears down every stale junction and recreates one per skill on disk, then reports how many it removed and created. A mismatch between "created" and the skill count, or any leftover real (non-junction) folder it refuses to touch, is the drift signal.

To inspect by hand without running it:

```powershell
# Skills on the Claude side
Get-ChildItem 'C:\Users\<you>\Desktop\AI_Projects\_system\skills' -Directory | Select-Object -Expand Name
# What Codex sees (J = junction/reparse point; a plain Directory is a real duplicate to clean up)
Get-ChildItem 'C:\Users\<you>\.codex\skills' -Force | Select-Object Name, Mode, Attributes
```

Then re-run the script (above) to reconcile.

---

## See also

- [SKILL.md](../SKILL.md)
- [skill-creator.md](skill-creator.md) — the wrench whose output triggers mirroring
- [`AGENTS.md`](../../../../AGENTS.md) — Claude/Codex split
