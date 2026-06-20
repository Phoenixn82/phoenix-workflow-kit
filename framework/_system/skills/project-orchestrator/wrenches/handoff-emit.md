---
name: project-orchestrator-handoff-emit
description: Produces the handoff file + exact next-session prompt at apex completion. Standard handoff format that matches the user's existing handoff conventions. Trigger phrases include "emit handoff", "handoff file", "next session prompt", "close out artifact", routes from completion.
---

# project-orchestrator-handoff-emit — close-out artifact

The apex's final output. Writes the handoff file in the format the user expects, with the exact next-session prompt at the bottom.

---

## Handoff file format

Matches the user's existing handoff convention:

```markdown
---
type: handoff
project: <project-slug>
session-date: <YYYY-MM-DD>
session-model: claude-opus-4-7[1m]
phase-on-handoff: <current state>
supersedes: <previous handoff if any>
---

# For future Claude

[Opening paragraph: what this project is, what state it's in, where to pick up]

---

## Required reading (read these BEFORE acting)

1. This file
2. <project>/CLAUDE.md
3. <project>/memory/plan.md
4. <project>/memory/decisions.md (recent entries)
5. <project>/memory/open-loops.md

---

## What landed this session

[Summary of what the apex run accomplished]

---

## Phase status (what's done, what's next)

[Status per phase of the apex pipeline]

---

## Hard rules (carried from AGENTS.md, never violate)

[The hard rules from AGENTS.md, abbreviated]

---

## Open loops

[From open-loops.md]

---

## Exact next-session prompt

\`\`\`
[the prompt to paste into the next session]
\`\`\`
```

---

## Where it lives

`<project>/HANDOFF_<YYYY-MM-DD>.md` for project-level apex runs.

For the AI_Projects rebuild itself, the convention is `Desktop/AI_Projects/HANDOFF_<YYYY-MM-DD>.md` per the existing pattern.

---

## Next-prompt construction

The prompt should:
- Reference this handoff at the top
- Reference the 4-5 required files
- State the phase the next session should start in
- Be self-contained (the next Claude doesn't see this session)
- Be terse (the user pastes it; doesn't read every word again)

---

## See also

- [SKILL.md](../SKILL.md)
- [completion.md](completion.md) — runs before this
- [`second-brain/wrenches/end-session.md`](../../second-brain/wrenches/end-session.md) — parallel end-session work
