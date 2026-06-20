---
name: project-orchestrator-completion
description: Phase 6 of the apex. Hard completion detection. Checks success criteria, ship verdict, open loops, the user approval. When all four pass, declares the apex done and dispatches to second-brain end-session ritual. Doesn't grind past completion. Trigger phrases include "completion", "are we done", "phase 6", "close out", "end the project".
---

# project-orchestrator-completion — hard completion logic

The apex's hard stop. Doesn't grind on adjacent improvements once scope is done. Knows when to call it.

---

## Completion checklist

Four conditions, checked sequentially. ALL four must pass.

### 1. Success criteria met

Read the project's brief.md → success criteria list. For each criterion:
- Is it observable? (If not, criterion was vague; flag)
- Is it observed? (Did the actually-shipped product hit it?)

If any criterion isn't observed, NOT complete. Either fix the gap or rescope.

### 2. Ship verdict positive

- ship/review passed
- ship/land-and-deploy succeeded
- ship/canary clean (no critical findings in window)
- ship/benchmark within thresholds
- ship/pay-for-this score >= 7

If any ship-phase output is RED, NOT complete.

### 3. No critical open loops

Scan `<project>/memory/open-loops.md` for HIGH severity items related to this scope.

If any HIGH severity open loops remain, NOT complete.

### 4. user-approved

Surface the above three checks + the synthesis report to the user. Ask explicitly: "Apex ready to close. Confirm done?"

If the user says no, NOT complete. The user's call is the final gate.

---

## When all four pass

Dispatch to:
1. `second-brain/wrenches/end-session.md` — runs the end-session ritual (extracts decisions / preferences / errors / status / new skills / open loops / corrections; shows draft; writes approved)
2. `handoff-emit.md` — emits handoff file + exact next-prompt
3. Surface to the user: "Apex done. Handoff at <path>. Next prompt copied for paste."

---

## When NOT all four pass

Surface specific failures. Recommend:
- Failed criterion → fix the gap (re-dispatch to build / ship)
- Failed ship verdict → fix what broke
- Open critical loop → escalate to investigate
- The user not approving → ask what's blocking

Don't auto-loop forever. Three rounds of completion-check → fix → recheck max; if still failing, surface to the user for explicit decision.

---

## See also

- [SKILL.md](../SKILL.md)
- [dispatch.md](dispatch.md) — phases preceding completion
- [handoff-emit.md](handoff-emit.md) — runs after completion confirmed
- [`second-brain/wrenches/end-session.md`](../../second-brain/wrenches/end-session.md) — the ritual
