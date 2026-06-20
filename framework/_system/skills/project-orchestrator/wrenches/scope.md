---
name: project-orchestrator-scope
description: Phases 0.5 and 1 of the apex pipeline. Project brief generation, capability loadout, autoplan 4-lens review. Produces the approved plan that subsequent phases execute. Trigger phrases include "scope", "phase 1", "produce the plan", routes from intake.
---

# project-orchestrator-scope — phases 0.5 + 1

Brief → loadout → autoplan → user-approved plan.

---

## Sequence

1. **Phase 0.5: Brief.** Dispatch to `plan-room/project-brief-generator` with the intake output. Emit project's CLAUDE.md.
2. **Phase 1.a: Loadout.** Dispatch to `plan-room/project-loadout`. The user confirms minimum capability set.
3. **Phase 1.b: Autoplan.** Dispatch to `plan-room/autoplan` for the 4-lens review pipeline (CEO + eng + design via cross-mechanic to design-studio + devex if applicable).
4. **Borderline gate.** autoplan surfaces close approaches / Codex disagreements / cross-cutting taste. The user decides.
5. **Plan locked.** Final reviewed plan goes to project's `memory/plan.md`. Decisions log to `memory/decisions.md` via second-brain.
6. **GATE.** the user go/no-go before any build work starts.

---

## Output

- Approved plan at `<project>/memory/plan.md`
- Loadout config at `<project>/.claude/settings.local.json`
- Decision records in `<project>/memory/decisions.md`
- Approved go signal for the dispatch phase

---

## Resume

Writes `<project>/plan-state.json` so the apex can resume across sessions if mid-phase.

---

## See also

- [SKILL.md](../SKILL.md)
- [intake.md](intake.md) — previous phase
- [dispatch.md](dispatch.md) — next phase
- [`plan-room/wrenches/project-brief-generator.md`](../../plan-room/wrenches/project-brief-generator.md)
- [`plan-room/wrenches/project-loadout.md`](../../plan-room/wrenches/project-loadout.md)
- [`plan-room/wrenches/autoplan.md`](../../plan-room/wrenches/autoplan.md)
