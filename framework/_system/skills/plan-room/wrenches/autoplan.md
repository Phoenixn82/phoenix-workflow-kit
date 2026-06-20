---
name: plan-room-autoplan
description: 4-lens review pipeline driver. Runs plan-ceo-review + plan-eng-review + plan-design-review (cross-mechanic to design-studio) + plan-devex-review sequentially with auto-decisions on 6 principles. Surfaces only borderline calls and taste decisions at a final approval gate. One command, fully reviewed plan out. Per the user's preference, this is the default route — not the 4 lenses individually. Trigger phrases include "auto review", "autoplan", "run all reviews", "review this plan automatically", "make the decisions for me", "/autoplan", "full review pipeline", "review my plan".
---

# plan-room-autoplan — auto-reviewed plan pipeline

The user has a plan. autoplan runs all 4 review lenses, makes the obvious calls automatically using 6 decision principles, and surfaces only what needs his taste at a final gate. One command, fully reviewed plan out.

This is the default route per the user's stated preference: he'd rather not answer 15-30 intermediate questions when most decisions have an obvious right call. autoplan makes those calls; the borderlines come to him at the end.

---

## When to fire

- After `project-brief-generator` emits CLAUDE.md and `project-loadout` confirms capabilities
- Direct: "autoplan" / "auto review" / "run all reviews" / "make the decisions for me"
- After the user updates a plan and wants a re-review
- Before invoking `build` mechanic (autoplan is the gate)

Don't fire when:
- Plan doesn't exist yet (push back to brief generation)
- The user wants only ONE lens (call that lens direct)
- The user wants to drive each lens interactively (call individual lenses)
- The change is trivial enough to skip review (the user decides; default is "no")

---

## The 4 lenses

Run in this order:

1. **plan-ceo-review** — scope / ambition / 10-star product lens
2. **plan-eng-review** — architecture / data flow / edge cases / test coverage / perf lens
3. **plan-design-review** — visual / UX / hierarchy / interaction lens (CROSS-MECHANIC to `design-studio`)
4. **plan-devex-review** — DX lens for dev-facing projects (APIs / CLIs / SDKs / docs). SKIPPED for non-dev-facing projects.

Each lens scores 0-10 across its dimensions, surfaces findings, proposes fixes. autoplan reads all four reports and applies the auto-decision rules.

---

## The 6 decision principles (auto-decide rules)

When autoplan encounters a finding with multiple possible fixes, it applies these principles in order:

1. **Smallest reasonable scope.** Pick the smaller scope unless it doesn't solve the problem.
2. **Simplest reasonable architecture.** Pick boring tech over novel tech unless boring won't.
3. **Established over novel.** Pick the pattern already in use unless it won't fit.
4. **Obvious over clever.** Pick the code that reads like prose unless cleverness is load-bearing.
5. **Reversible over locked-in.** Pick Bezos type-2 doors over type-1 unless locked-in is necessary.
6. **Smaller surface area over bigger.** Pick fewer features / fewer deps / fewer integration points unless each is justified.

If a finding's resolution is obvious under these principles → auto-decide.
If two principles conflict (e.g., simpler architecture conflicts with established pattern) → SURFACE for the user.
If no principle applies cleanly (e.g., taste decision on close approaches) → SURFACE for the user.
If Codex disagrees with autoplan's call (when Codex was consulted for a specific question) → SURFACE for the user.

---

## When to surface (the borderline gate)

autoplan surfaces ONLY:

- **Close approaches** — two valid options where the choice is judgment, not principle
- **Borderline scope** — features that could go either way (in or out)
- **Codex disagreements** — when Codex was consulted and disagreed with autoplan
- **Cross-cutting decisions** — choices that ripple to multiple lenses (a stack decision the eng lens loves but the DX lens questions)
- **Conflicts between principles** — when two principles point different directions
- **Anything the user has flagged as taste** in prior sessions (read from `_system/second-brain/Actions/`)

The surface gate is a SINGLE batched decision moment at the end, not a stream of mid-pipeline questions. The user sees:

```markdown
## Autoplan complete. Plan ready except:

### Decision 1: Cache layer
- Option A: in-memory (smaller scope, simpler, established in the user's stack)
- Option B: Redis (more scalable, novel for this project)
- Auto-decision lean: A (principles 1, 2, 3)
- Why surface: Eng lens flagged "if you expect > 100 users, B is needed." First-slice says 10 users. Choose now or defer to v2?

### Decision 2: Auth flow
...

### Decision 3: ...
```

The user accepts auto-leans, edits, or overrides. autoplan applies all decisions in one pass, writes the final plan.

---

## Sequence

```
1. Read project brief (CLAUDE.md) + loadout
2. Read prior `.plan-state.json` if it exists (resume)
3. Run plan-ceo-review
   - Output: score + findings + recommendations
4. Run plan-eng-review
   - Output: score + findings + recommendations
5. If project is dev-facing, run plan-devex-review
   - Output: score + findings + recommendations
6. If project has UI surface, call cross-mechanic into design-studio's plan-design-review
   - Output: score + findings + recommendations
7. For each finding across all 4 lenses:
   - Apply 6 decision principles
   - If obvious resolution → auto-decide, log in `.plan-state.json`
   - If borderline → queue for surfacing
8. Synthesize: read all auto-decisions + queued borderlines
9. Surface borderlines to the user in ONE batched message
10. Apply the user's choices
11. Emit final reviewed plan
12. Write to project's plan.md + log decisions to second-brain
```

---

## Cross-mechanic design-lens call

`plan-design-review` lives in `design-studio` per `DECISIONS_LOCKED` (archived at `_archive/claude_projects_2026-05-pre-rebuild/Rebuild/DECISIONS_LOCKED.md`). autoplan calls across:

```
Agent: dispatch to design-studio mechanic with subagent_type
       "Run plan-design-review on the current plan at <path>.
        Return: score per dimension, findings, recommendations.
        Format: same as other plan-room lens reports."
```

The cross-mechanic call adds one Agent dispatch worth of latency. Same pattern as `cso` being inline during `build` — capabilities live where they fit, not where they're sometimes used.

---

## Resume across sessions

autoplan writes `.plan-state.json` (at the project root) via `plan-state.py` as it runs. The schema is:

```json
{
  "session_id": "plan-2026-05-28T13-00-00Z",
  "project": "<slug>",
  "started_at": "2026-05-28T13:00:00+00:00",
  "phase": "intake",
  "intake": { "questions_answered": [], "brief_emitted": false },
  "loadout": { "plugins": [], "mcps": [], "skills": [] },
  "autoplan": {
    "lenses_run": ["plan-ceo-review", "plan-eng-review"],
    "auto_decisions": [],
    "judgment_calls_surfaced": [],
    "approval_gate_passed": false
  }
}
```

Set fields by dot-path, e.g. `plan-state.py set --field autoplan.lenses_run --value '["plan-ceo-review"]'`.

If the user's session ends mid-pipeline, the next autoplan invocation resumes at the next lens. Doesn't re-run completed lenses.

---

## Output: the reviewed plan

```markdown
# <Project> — Reviewed Plan

## Summary
<one paragraph: what's being built, the approach, why>

## Lens verdicts
- CEO: 7.5/10 — <one-line takeaway>
- Eng: 8.0/10 — <one-line takeaway>
- Design: 8.5/10 (cross-mechanic from design-studio) — <one-line takeaway>
- DevEx: SKIPPED (not dev-facing)

## Plan
<the actual plan: phases, deliverables, dependencies>

## Decisions made by autoplan
- <decision 1> → chose <option>, principle: smallest scope
- <decision 2> → chose <option>, principle: established pattern
- ...

## Decisions made by the user at borderline gate
- <decision A> → the user chose <option>, reasoning: ...
- <decision B> → the user chose <option>, reasoning: ...
- ...

## What this plan does NOT cover
<bounded explicitly>

## Risks + mitigations
<from CEO + eng lenses>

## Success criteria + how we'll measure
<from brief + CEO lens>

## Next: build mechanic when the user is ready
```

The plan goes in `<project>/memory/plan.md` (or wherever the project's existing pattern places plans). Decisions log to the vault at `_system/second-brain/Projects/<slug>/decisions.md` via `decision-log.py` — that vault copy is canonical (per the hard rules). `<project>/memory/decisions.md`, if the project scaffolds one, is the project-local mirror.

---

## Cost shape

- 4 lens runs (3 if no DX surface, 4 if all apply): each is one Claude reasoning pass = medium
- Cross-mechanic design lens: one Agent dispatch + reasoning pass = medium
- Auto-decision pass: small (mostly pattern matching)
- Synthesis + borderline surface: small
- The user gate + apply: conversational, small
- Total: medium-high. Most expensive wrench in plan-room. Dominates a planning pass.

For a project of moderate complexity, expect ~5-10 minutes wall-clock and a non-trivial token spend. Worth it because the plan it emits is genuinely reviewed across 4 angles with auto-decisions applied — what would otherwise take 30+ interactive questions becomes one batched gate.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Borderlines list too long (> 10 items) | Principles aren't aggressive enough on this project | Tune principles for the project; the user takes one pass to override auto-leans, then autoplan re-runs with tighter calls |
| Auto-decisions feel wrong | Principles applied without context the user knows | Surface MORE; auto-decide LESS for this project's domain |
| Design lens cross-mechanic call fails | design-studio unavailable | Skip with warning; manual design-review later |
| Two lenses contradict | Real design tension | SURFACE it; that's why it's a borderline |
| Resume across sessions confused | `.plan-state.json` corrupted | Delete state, re-run from start |

---

## Helper scripts

| Script | What it does |
|---|---|
| `../scripts/plan-state.py {get\|set\|init\|complete} [--project <slug>] [--field <dot.path>] [--value <json>]` | Persistent state across plan-room sessions. Dot-path field access. `init` requires `--project` and writes `.plan-state.json` at project root; `complete` archives to `.plan-state-archive/<session_id>.json`. |
| `../scripts/decision-log.py --project <slug> --title "..." --decision "..." --reasoning "..." [--alternatives "..." --confidence X --links "..."]` | Appends an autoplan-surfaced decision to `Projects/<slug>/decisions.md` per the capture wrench `decision` category format. 60s dupe-skip. |

Spec: `_archive/claude_projects_2026-05-pre-rebuild/Rebuild/PHASE_5_DISPATCH.md` § 6.1 + § 6.2 (archive only; behavior is documented in the table above).

---

## See also

- [SKILL.md](../SKILL.md) — plan-room mechanic
- [plan-ceo-review.md](plan-ceo-review.md) — lens 1
- [plan-eng-review.md](plan-eng-review.md) — lens 2
- [plan-devex-review.md](plan-devex-review.md) — lens 4 (DX-facing projects)
- [`design-studio/wrenches/plan-design-review`](../../design-studio/wrenches/plan-design-review.md) — lens 3 (cross-mechanic)
- [project-loadout.md](project-loadout.md) — runs before autoplan
- [project-brief-generator.md](project-brief-generator.md) — emits the brief autoplan reviews
