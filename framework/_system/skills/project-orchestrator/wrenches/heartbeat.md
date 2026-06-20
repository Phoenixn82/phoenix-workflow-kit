---
name: project-orchestrator-heartbeat
description: Cross-cutting progress log. Writes status updates throughout the apex pipeline so the user can check progress between sessions or while the orchestrator runs. Lives at _system/second-brain/Projects/<slug>/heartbeat.md. Trigger phrases include "heartbeat", "progress", "where is the orchestrator", "what's the orchestrator doing".
---

# project-orchestrator-heartbeat — progress log

A live progress log the user can check. Written by dispatch + other phase wrenches throughout the apex pipeline.

---

## File location

`_system/second-brain/Projects/<slug>/heartbeat.md`

The user can `cat` this file anytime to see where the apex is.

---

## Format

```markdown
## Project: <slug> — apex run started 2026-05-28 14:00

### Current phase: <phase name>
### Phase started: <time>
### Elapsed in phase: <minutes>

### Sub-agents active
- [<role>] Codex implementing <file/component> (<min> in, est. <min> remaining)
- [<role>] Claude reviewing <file/component>

### Completed phases
- Phase 0: Intake ✓ (10 min) — <one-line takeaway>
- Phase 0.5: Brief ✓ (5 min) — <takeaway>
- Phase 1: Plan ✓ (20 min, 2 borderlines surfaced + resolved) — <takeaway>

### Up next
- <next phase>
- Est. <time> remaining at current pace

### Notes / surprises
- <anything the user should know about>
```

---

## Update cadence

- After every sub-agent completion
- At every phase boundary
- On any error / surprise
- Hourly during long-running phases (e.g., build with many components)

---

## See also

- [SKILL.md](../SKILL.md)
- [dispatch.md](dispatch.md) — primary writer
- [`second-brain/SKILL.md`](../../second-brain/SKILL.md) — vault home
