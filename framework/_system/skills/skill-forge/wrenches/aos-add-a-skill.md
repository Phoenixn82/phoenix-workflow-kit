---
name: skill-forge-aos-add-a-skill
description: Critique gate before any new skill gets scaffolded. Two-phase — phase 1 brutally honest "should this skill exist" review (overlap with existing skills, simpler alternatives, redundancy); phase 2 (HARD STOP — wait for explicit user approval) scaffolds via skill-creator, wires into domain-overrides, adds to allow_in_packages, commits. Trigger phrases include "should I add a skill", "critique this skill idea", "add a skill for X", "/aos-add-a-skill", "evaluate this skill proposal", "is this skill worth building".
---

# skill-forge-aos-add-a-skill — critique gate

Phase 1 is the brutally honest review of whether a skill should exist. Phase 2 is hard-stopped until the user explicitly approves what survived phase 1.

---

## When to fire

- "Should I add a skill for X" / "is this skill worth building"
- "Critique this skill idea" / "evaluate this skill proposal"
- Before `skill-creator` ever runs

Don't fire when:
- The user said skip critique (rare, but allowed)
- The skill already exists (route to `skill-scout` to find it)

---

## Phase 1: Brutally honest critique

Check in order:

1. **Does an existing skill already do this?** Run `skill-scout` internally. If yes → no new skill needed; update the existing one's description or trigger phrases.
2. **Does it fold into an existing mechanic as a new wrench?** If yes → add as a wrench. Update the mechanic's wrench table + SKILL.md routing. Update `_system/second-brain/Mechanics/<mechanic>/state.md`.
3. **Is this a recurring need or hypothetical?** the user has asked for it the same way 3+ times across sessions? If hypothetical → kill the idea.
4. **Is this imposing outside opinion the user didn't ask for?** Behavioral / process / convention skills that aren't his preference should be cut.
5. **Will the user actually invoke it?** Or will it sit unfired? If unfired-skill-graveyard risk is high → kill.
6. **Does it pass the readability test?** Will the SKILL.md fit in one Read call without being too dense? If not, scope it down.

The user gets the critique verbatim. If any check fails, kill recommendation. He can override but the critique is on record.

---

## HARD STOP between phases

After phase 1 emits the critique + recommendation, the wrench WAITS for the user's explicit approval before phase 2 fires. No auto-progression.

```
Phase 1 verdict: KEEP — folds into existing `web-scrape` mechanic as a new wrench
Recommendation: add `web-scrape/wrenches/auth-flow.md`

The user: approve / edit / kill
```

If the user says approve → phase 2. Anything else → stop.

---

## Phase 2: Scaffold (after approval)

Once approved:

1. Dispatch to `skill-creator` to write the SKILL.md / wrench .md following AI-first format
2. Wire into parent mechanic's wrench table (if folding in)
3. Update `SKILLS_INDEX.md`
4. Update `DECISION_MAP.md` if routing changes
5. Update `_system/second-brain/Mechanics/<mechanic>/state.md`
6. Run `skill-scout` to verify trigger phrases route to the new skill
7. Commit (the user's call on when)

---

## See also

- [SKILL.md](../SKILL.md)
- [skill-creator.md](skill-creator.md) — phase 2 implementation
- [skill-scout.md](skill-scout.md) — phase 1 overlap check
- [`AGENTS.md`](../../../../AGENTS.md) — skill-intake flow
