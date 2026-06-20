# AI_Projects — session loader

This file auto-loads for any session whose working directory is under `AI_Projects/`. Its only job is to boot the mechanic/wrench skill system so the right tool gets grabbed for the job. Keep it thin. The real content lives in the files it points at.

## Read at session start (in order)

1. **`AGENTS.md`** (this folder) — the operating manual: 12 hard rules, the mechanic/wrench philosophy, the brain-lane split, future-Claude skill intake.
2. **`SKILLS_INDEX.md`** (this folder) — one line per callable surface. This is the menu. Do NOT pre-load any mechanic's `SKILL.md` body; read only the one you actually need.
3. **`DECISION_MAP.md`** (this folder) — task → tool routing when the choice isn't obvious.

Skill bodies live at `_system/skills/<name>/SKILL.md`; their sub-wrenches at `_system/skills/<name>/wrenches/<wrench>.md`. Load a wrench body only when you invoke it.

## How to grab the right tool

Every task gets the right-sized surface, deliberately chosen, not by reflex:

- **One narrow ask** → call the **wrench** directly (don't spin up its mechanic).
- **Several tools in coordination** → call the **mechanic** (its `SKILL.md` dispatches to wrenches).
- **A full project from one prompt** → call the **apex** (`project-orchestrator`).
- **Unsure which fits** → run `skill-forge → skill-scout`. Don't guess.

**Always-core (orient at start):** `router`, `second-brain`, `guard`. Loaded for orientation, not auto-fired — `guard` hooks stay opt-in, `second-brain` auto-pulls only the vault index + Actions + active project, `router` does not route trivial work.

**Standalone keepers (called direct):** `investigate`, `cso`, `context-audit`, `windows-launcher`, `printing-press-router`.

**On-demand mechanics (load only when the task calls for it):** `web-scrape`, `build`, `mobile-app`, `ship`, `seo`, `design-studio`, `plan-room`, `content-forge`, `morning-briefing`, `video-scan`, `skill-forge`.

## Hard reminders (full text in AGENTS.md)

- Nothing runs on its own. The user triggers everything.
- Codex is the default code lane; Claude steps in when needed (preference, not a hard stop).
- Cost-first scraping: Firecrawl → Cloak Browser → local drivers.
- No permission prompts by default. Never return `permissionDecision: "ask"` from a default-on hook.
- The vault (`_system/second-brain/`) is canonical; the end-of-session ritual runs only on the user's command.

The user's global `~/.claude/CLAUDE.md` still takes precedence over everything here.
