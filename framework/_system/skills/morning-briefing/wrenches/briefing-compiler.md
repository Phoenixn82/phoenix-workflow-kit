---
name: morning-briefing-briefing-compiler
description: Daily synthesis wrench. Reads vault signals (today's daily note, active project status, open loops, queued cards from video-curator, decisions log) and assembles a morning briefing. Fires on the user's command — NO schedule per AGENTS.md hard rule #1. Trigger phrases include "compile briefing", "morning briefing", "daily synthesis", "what's happening today", "summarize where I'm at", "today's brief".
---

# morning-briefing-briefing-compiler — daily synthesis

Reads vault state, assembles a morning briefing. The user triggers; never auto-fires.

---

## When to fire

- "Morning briefing" / "compile briefing" / "today's brief"
- The user starting his day and wants synthesis
- After a multi-day break to re-orient

Don't fire when:
- The user has a specific question (route to second-brain/recall)
- It's mid-day and the user wants quick-look (just summarize from conversation context, no full briefing)

---

## Signals read

From `_system/second-brain/`:

| Signal | Path |
|---|---|
| Recent vault changes | `log.md` (newest entries) — the vault has no `Daily/` convention; use the change log for day-context |
| Active project statuses | `Projects/*/status.md` |
| Open loops | `Projects/*/open-loops.md` |
| Decisions log recent | `Projects/*/decisions.md` last 5 entries |
| Queued video cards | `_system/briefing/curator/` — the implemented store: per-item cards `yt-<id>.md` / `ig-<id>.md`, queue/seen state in `_system/briefing/import-state.json`, feed config in `import-sources.json`, last run in `last-briefing.json`. (NOT a vault `Cards/video-curator/` path — that was never built.) |
| Action defaults touched recently | `Actions/*.md` last 3 modified |
| Mechanic state changes | `Mechanics/*/state.md` last 3 modified |

If a signal source doesn't exist, skip silently.

---

## Output shape

```markdown
# Morning briefing — 2026-05-28

## Where I'm at
[2-3 sentence overall state from active project statuses]

## Today's priorities
[inferred from open loops + active project status]
1. <item>
2. <item>
3. <item>

## Open loops needing attention
- [ ] <loop 1> (project / waiting on)
- [ ] <loop 2>
- ...

## Recent decisions worth remembering
- <decision 1> ([[link]])
- <decision 2>

## Queued for review
[from video-curator queue + any awaiting-human files]
- <video card 1>
- <video card 2>

## What I'd recommend doing first
[opinionated suggestion — what's the highest-leverage thing in the next 2 hours]
```

The "what I'd recommend doing first" line is the most useful part — gives the user one specific action instead of a list of options.

---

## What's excluded (intentional)

Per the handoff notes: Gmail / email is excluded from morning briefings since 2026-05-24 (the user uses Gmail outside the dashboard). Don't pull from email even if access exists.

Per AGENTS.md hard rule #1: no auto-scheduling. The briefing is on-demand only.

---

## Cost shape

- Read N small files: small
- Synthesize into briefing: medium (one Claude reasoning pass)
- Total: low. Should run in seconds.

---

## See also

- [SKILL.md](../SKILL.md)
- [retro.md](retro.md) — weekly variant
- [video-curator.md](video-curator.md) — feeds queued cards
- [`second-brain/SKILL.md`](../../second-brain/SKILL.md) — signal source
- [`AGENTS.md`](../../../../AGENTS.md) — hard rule #1
