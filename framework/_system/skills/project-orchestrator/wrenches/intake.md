---
name: project-orchestrator-intake
description: Phase 0 of the apex pipeline. Routes the user's brain-dump or one-line ask to the right plan-room intake wrench — process-interviewer for projects with implied scope, office-hours for fuzzy ideas, decision-toolkit for "should I" decisions. Doesn't intake directly; dispatches to plan-room. Trigger phrases include "intake", "start project", "phase 0", routes from apex top-level triggers.
---

# project-orchestrator-intake — phase 0 routing

The apex's first phase. Decides which plan-room intake fits the input, then dispatches.

---

## Sequence

1. Read the user's input — brain-dump, one-liner, brief, or full spec
2. Classify shape:
   - Has implied scope, just needs articulation → `process-interviewer`
   - Fuzzy idea, demand reality unclear → `office-hours`
   - "Should I" or stuck on a choice → `decision-toolkit`
   - Already has a brief → skip intake, route to scope phase
3. Dispatch to the picked wrench via Agent call into plan-room
4. Wait for output (brief, idea verdict, or decision record)
5. Hand off to `scope` phase

---

## Classification signals

| Input signal | Route |
|---|---|
| "Build me <noun>" / "spin up <noun>" / clear deliverable | process-interviewer |
| "I have an idea — <vague>" / "should we build" | office-hours |
| "Should I X" / "pros and cons of X" | decision-toolkit |
| 5+ paragraphs of context describing what exists + what's needed | process-interviewer (likely full enough) |
| Brief.md already exists in conversation or project | skip intake |

---

## Output

The brief / idea verdict / decision record from plan-room. The apex's `scope` phase consumes this.

---

## See also

- [SKILL.md](../SKILL.md)
- [scope.md](scope.md) — next phase
- [`plan-room/SKILL.md`](../../plan-room/SKILL.md) — where intake actually runs
