---
name: morning-briefing
description: Synthesis mechanic for daily / weekly briefings. briefing-compiler (the main one — fires on the user's command, NOT scheduled per AGENTS.md hard rule #1) + video-curator (IG/YT feeder that proposes content cards) + retro (weekly engineering retrospective variant). All on-demand. No autonomous schedule. Trigger phrases include "morning briefing", "daily synthesis", "what happened", "weekly retro", "engineering retro", "what did we ship", "video curator", "curate videos", "compile briefing".
---

# morning-briefing — on-demand synthesis

Synthesizes signals across the user's stack into briefings he triggers explicitly. NEVER on a schedule per AGENTS.md hard rule #1.

The lane that the cut `skill-stack-audit` used to occupy (badly, via autonomous spam) — this version is the disciplined opposite.

---

## Cardinals

1. **NEVER scheduled, ALWAYS triggered.** Per AGENTS.md hard rule #1, no timers / cron / hooks fire briefing-compiler. The user runs it when he wants synthesis. Past trauma: skill-stack-audit's 02:00 nightly task became autonomous noise.

2. **Vault-first.** Briefings draw from `_system/second-brain/` (today's daily note, project status, decisions log, open loops) — not random external signals.

3. **Surface drafts, don't auto-publish.** briefing-compiler always shows the draft. The user approves before anything writes / sends.

4. **Multiple cadences.** Daily / weekly / monthly / quarterly / project-specific. The user picks; wrench adapts.

---

## When this fires

- "Morning briefing" / "compile briefing" / "what should I know today"
- "Weekly retro" / "engineering retro" / "what did we ship this week"
- "Video curator" / "curate from my feeds" / "what's worth watching"
- After major events when synthesis would help

Don't fire when:
- The user wants a single specific item (route to second-brain recall)
- The user wants real-time monitoring (that's `ship/canary` for production)

---

## Picking the wrench

| Shape of the ask | Wrench |
|---|---|
| "Compile today's briefing" / daily synthesis | `briefing-compiler` |
| "Weekly retro" / "what did we ship" | `retro` |
| "Curate videos from my feeds" | `video-curator` |

---

## Cross-mechanic dependencies

- **`second-brain`** is the primary source (vault, project status, decisions, open loops)
- **`video-scan`** for any actual transcription if video-curator surfaces a candidate
- **`router`** — most wrenches are Claude reasoning, but the `video-curator` wrench is multi-lane: the implemented pipeline at `projects/video_curator/curate.py` runs Gemini ingest (objective description) → Claude analysis (title/extract/route/score) → pure-Python note write, plus yt-dlp/ffmpeg scrape. Reuse that pipeline rather than re-grinding curation in Claude reasoning.
- **`_system/briefing/`** — where the curator queue lives (`curator/`), read by `briefing-compiler`

---

## What this mechanic does NOT do

- Does not run on a schedule
- Does not auto-publish / auto-send anything
- Does not analyze production metrics (that's separate platform tooling)
- Does not generate marketing content (that's `content-forge`)

---

## Wrenches

| Wrench | Path | What it does |
|---|---|---|
| **briefing-compiler** | `wrenches/briefing-compiler.md` | Daily synthesis from vault signals — vault index + active projects + open loops + queued cards |
| **video-curator** | `wrenches/video-curator.md` | IG/YT feeder. Proposes content cards from the user's feeds; he reviews + approves |
| **retro** | `wrenches/retro.md` | Weekly engineering retrospective from commit history + work patterns + quality metrics |

---

## See also

- [wrenches/briefing-compiler.md](wrenches/briefing-compiler.md)
- [wrenches/video-curator.md](wrenches/video-curator.md)
- [wrenches/retro.md](wrenches/retro.md)
- [`AGENTS.md`](../../../AGENTS.md) — hard rule #1 (nothing self-fires)
- [`second-brain/SKILL.md`](../second-brain/SKILL.md) — primary signal source
