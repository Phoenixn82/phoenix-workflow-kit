---
name: morning-briefing-video-curator
description: Feeds the briefing with IG/YT video curation. Proposes content cards based on the user's feeds + interests; he reviews + approves + lets through to briefing or rejects. NO autonomous queue building per AGENTS.md hard rule #1 — fires on the user's command. Tracks "way off base" feedback to improve future curation. Trigger phrases include "video curator", "curate videos", "what's worth watching", "review the curator queue", "approve this card", "skip this card", "way off base", "the curator misread X".
---

# morning-briefing-video-curator — content card proposer

Proposes video / content cards the user might want in the morning briefing or to watch later. The user approves / rejects / flags as off-base. No autonomous queue building.

---

## When to fire

- "Video curator" / "curate videos" / "what should I watch"
- "Review the curator queue" / "approve this card"
- After the user watches videos and wants the curator to learn

Don't fire when:
- The user has a specific video URL → that's `video-scan` (different lane)
- The user wants automated daily curation → that's a sanctioned automation; offer to register it under `_system/automations/` (rule #1), don't refuse

---

## Sources

The user's configured feeds:
- YouTube subscriptions (via yt-dlp or RSS)
- Instagram saved / favorites (if accessible)
- X bookmarks (if configured)
- Custom RSS feeds

If no sources configured, the wrench asks the user what to watch and offers to set up sources.

---

## Card shape

Each proposed card:

```markdown
## <Title>
**Source:** YouTube — <channel>
**Length:** <duration>
**Published:** <date>
**URL:** <link>

**Why it's worth watching (proposed):**
<one paragraph — based on title, description, channel context, alignment with the user's interests>

**Status:** queued / approved / rejected / off-base

**the user notes:** [empty until the user reviews]
```

Cards land in `_system/briefing/curator/` as per-item `yt-<id>.md` / `ig-<id>.md` notes (written by `projects/video_curator/curate.py`), with queue/seen state in `_system/briefing/import-state.json` and feed config in `import-sources.json`. Standing curation rules live at `Mechanics/video-curator/learnings.md`. briefing-compiler reads from `_system/briefing/curator/`. (The `Cards/video-curator/queued.md` vault path described in older drafts was never implemented — `_system/briefing/curator/` is the real store.)

---

## "Way off base" feedback loop

When the user says a card was off-base ("this was misread" / "I'd never watch this"), the wrench logs the rejection + the user's reason under `_system/briefing/curator-feedback/` (one `*.md` per item). Future curation passes read this (and `Mechanics/video-curator/learnings.md`) and avoid similar mismatches.

```markdown
## <card title> — rejected 2026-05-28

**Reason the user gave:** <quote or summary>
**What went wrong:** <inferred>
**Patterns to avoid:** <topic / channel / framing>
```

---

## Cost shape

- Source feed scan: medium (depends on feed size)
- Per-card "why it's worth watching": small per card
- Queue + log writes: small
- Total: medium for a fresh curation run; small for queue reviews

---

## See also

- [SKILL.md](../SKILL.md)
- [briefing-compiler.md](briefing-compiler.md) — consumes the queue
- [`video-scan/SKILL.md`](../../video-scan/SKILL.md) — different lane (scrape a specific video)
- [`AGENTS.md`](../../../../AGENTS.md) — hard rule #1 (no auto-fire)
