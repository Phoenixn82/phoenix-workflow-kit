---
name: plan-room
description: Planning pipeline mechanic. Brief → loadout → review → ready-to-build. Intake via process-interviewer (default), office-hours (fuzzy idea), or decision-toolkit (stuck on a choice). Recommends answers for every question, never grills. autoplan auto-decides on 6 principles and surfaces only borderline / taste calls. Planning is Claude's home turf per AGENTS.md hard rule #5. Fires on "plan this", "let's design", "new project", "brain dump", "should I", "is this worth building", "review the architecture", "lock in the plan", "ceo review", "eng review", "devex review", "office hours", "decision framework", "stuck on a decision", "intake".
---

# plan-room — planning pipeline

The lane where intent becomes plan. The user arrives with anything from a single sentence ("rebuild my workflow") to a 20-paragraph brain-dump ("I want X to do Y because Z and I'm thinking maybe..."). The plan-room turns that into:

1. A clear-enough brief
2. The right capability loadout
3. A reviewed plan that's ready for `build` to execute

Planning happens BEFORE any code is written. Per AGENTS.md hard rule #5, planning is Claude's home turf — Codex doesn't enter this mechanic. When the review pipeline needs implementation-level second opinions on a tricky bit (e.g., "is this DB migration safe"), the call routes to Codex through `router`, but the plan itself stays in Claude's hands.

---

## Cardinals

1. **Brainstorm before plan, plan before build.** No implementation work starts without a plan. No plan starts without a clear-enough intent. The sequence is intake → brief → loadout → review → ready-to-build. Skipping steps is allowed only when the user explicitly trims scope ("brief only, no review yet"). This is the superpowers:brainstorming rule applied at the mechanic level.

2. **Intake recommends answers, doesn't grill.** Every question in `process-interviewer` and `office-hours` comes with a recommended answer based on context the wrench can infer (from the conversation, the project files, the prior plan-room state). The user can accept, edit, or override. Forcing him to type long answers to 20 follow-up questions is a bad pattern. Suggested-answer-plus-edit always beats blank-prompt-plus-question.

3. **autoplan auto-decides, surfaces only taste.** The autoplan wrench has 6 decision principles and uses them to make most decisions automatically (smallest reasonable scope, simplest reasonable architecture, established over novel, obvious over clever, reversible over locked-in, smaller surface area over bigger). It surfaces only borderline calls and taste decisions (close approaches between alternatives, scope edge cases, Codex disagreements) at a final approval gate. Default isn't "ask 30 questions"; default is "make the obvious calls, ask only the hard ones." the user's preference per the prior session: "make the decisions for me" + surface judgment calls.

4. **Right-sized loadout, not max loadout.** `project-loadout` proposes the MINIMUM plugins / MCPs / skills needed for the stated scope, not a maximalist set. Re-invoke when scope materially shifts, but never silently remove capability mid-project. Loadout is the cost-control discipline that prevents token bloat.

5. **Planning is Claude's lane.** Per AGENTS.md hard rule #5, architecture / planning / brainstorming / decisions / orchestration are Claude's home turf, not Codex's. Codex doesn't enter the plan-room. The review pipeline (CEO / eng / design / devex lenses) is Claude reasoning, not Codex code review. When implementation-level second opinions are needed on a specific tricky decision, route through `router` to Codex for that ONE question, then come back.

6. **decision-toolkit and office-hours are separate intake paths.** Both can start a plan-room flow. They answer different questions.
   - **decision-toolkit** answers "should I do X?" → Bezos 1/2 door triage → right framework (WRAP / pre-mortem / OODA / EV / regret min / etc.) → kill criteria + review date
   - **office-hours** answers "is this idea worth building?" → YC 6 forcing questions (demand reality / status quo / desperate specificity / narrowest wedge / observation / future-fit) plus builder-mode brainstorm for side projects
   - **process-interviewer** is the default intake for projects that already have implied scope
   The SKILL.md dispatcher picks based on the intake signal.

7. **Cross-mechanic design lens.** The design lens for review (`plan-design-review`) lives in `design-studio`, not in plan-room, per DECISIONS_LOCKED. `autoplan` reaches across mechanics to invoke it. This is the same pattern as `cso` running inline during `build` rather than as a wrench inside `ship`.

---

## The pipeline

```
                                ┌────────────────────────────┐
                                │   the user's intent         │
                                │  - sentence                │
                                │  - brain-dump              │
                                │  - "should I X"            │
                                │  - "is X worth building"   │
                                └─────────────┬──────────────┘
                                              │
                       ┌──────────────────────┼──────────────────────┐
                       │                      │                      │
              ┌────────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
              │ decision-toolkit│    │ office-hours    │    │ process-        │
              │  "should I X"   │    │ "is X worth     │    │ interviewer     │
              │                 │    │  building"      │    │ (default intake)│
              └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
                       │                      │                      │
                       │                      └──────────┬───────────┘
                       │                                 │
                       │                       ┌─────────▼──────────┐
                       │                       │ project-brief-     │
                       │                       │ generator          │
                       │                       │ (emits CLAUDE.md)  │
                       │                       └─────────┬──────────┘
                       │                                 │
                       │                       ┌─────────▼──────────┐
                       │                       │ project-loadout    │
                       │                       │ (right-size caps)  │
                       │                       └─────────┬──────────┘
                       │                                 │
                       │                       ┌─────────▼──────────┐
                       │                       │ autoplan           │
                       │                       │ (4-lens pipeline,  │
                       │                       │  auto-decisions)   │
                       │                       └─────────┬──────────┘
                       │                                 │
                       │            ┌────────────────────┼────────────────────┐
                       │            │                    │                    │
                       │  ┌─────────▼────────┐ ┌─────────▼────────┐ ┌─────────▼────────┐
                       │  │ plan-ceo-review  │ │ plan-eng-review  │ │ plan-devex-review│
                       │  └─────────┬────────┘ └─────────┬────────┘ └─────────┬────────┘
                       │            │                    │                    │
                       │            └────────────────────┼────────────────────┘
                       │                                 │
                       │                       ┌─────────▼──────────┐
                       │                       │ design-studio →    │
                       │                       │ plan-design-review │
                       │                       │ (cross-mechanic)   │
                       │                       └─────────┬──────────┘
                       │                                 │
                       │                       ┌─────────▼──────────┐
                       │                       │ autoplan synth     │
                       │                       │ surfaces border-   │
                       │                       │ lines for the user  │
                       │                       └─────────┬──────────┘
                       │                                 │
                       └────────────────┬────────────────┘
                                        │
                              ┌─────────▼──────────┐
                              │ the user approves → │
                              │ ready for build →  │
                              │ ship pipeline      │
                              └────────────────────┘
```

---

## When this mechanic fires (auto-detect)

- "Plan this" / "let's plan" / "I want to build X" / "new project: ..."
- "Brain dump:" / "I have an idea" / "thinking through ..."
- "Should I X" / "stuck on a decision" / "help me decide"
- "Is this worth building" / "office hours" / "pressure-test this idea"
- "Review the architecture" / "lock in the plan"
- "CEO review" / "eng review" / "devex review"
- "Autoplan" / "auto review" / "run all reviews"
- "Right-size capabilities" / "loadout" / "what plugins do I need"
- "Decision framework" / "pre-mortem" / "framework for this"

When it does NOT fire — even though it sounds like it might:
- "Build X" without a plan → push back: needs plan-room first OR the user explicitly says "skip planning"
- "Ship this" → that's `ship`, not plan-room
- "Design a UI" → that's `design-studio` (which owns the design lens autoplan calls)
- "What is X" / pure question → just answer; planning isn't needed

---

## Picking the wrench

| Shape of the ask | Wrench | Why |
|---|---|---|
| New project / brain dump with implied scope | `process-interviewer` (default intake) | Recommends answers, fills the brief |
| Fuzzy idea with no clear scope | `office-hours` | YC forcing questions before any plan |
| "Should I X" / decision needed | `decision-toolkit` | Reversibility triage + right framework |
| Have a brief already, need the CLAUDE.md | `project-brief-generator` direct | Skip intake |
| Need to right-size plugins / MCPs / skills | `project-loadout` direct | Capability hygiene |
| Plan exists, run reviews | `autoplan` direct | 4-lens pipeline |
| One specific lens | `plan-ceo-review` / `plan-eng-review` / `plan-devex-review` direct | Targeted review |

The SKILL.md dispatcher picks the intake at session start when the user's signal is ambiguous, by asking ONE question: "is this a 'should I do X' decision, an 'is this worth building' idea pressure-test, or a 'let's plan X' project intake?"

---

## autoplan's 6 decision principles

When autoplan auto-decides, it applies these in order:

1. **Smallest reasonable scope.** When in doubt, ship less. The CEO lens can override (scope expansion mode) when the smaller scope wouldn't actually solve the user's problem.
2. **Simplest reasonable architecture.** Boring tech that works > novel tech that might work. Eng lens overrides only when boring tech genuinely can't.
3. **Established over novel.** Pick the pattern the user's team / the user himself has used before. Novel only when established won't.
4. **Obvious over clever.** Code that reads like prose > code that's cute. This applies to plans too — a one-line explanation that a stranger could follow > a five-paragraph rationale.
5. **Reversible over locked-in.** Bezos type-2 doors first when possible. Type-1 doors (irreversible) need explicit approval.
6. **Smaller surface area over bigger.** Fewer features, fewer dependencies, fewer integration points. Each addition has to justify itself.

When two principles conflict (e.g., simpler architecture conflicts with established pattern), autoplan surfaces the conflict for the user instead of guessing.

---

## Cross-mechanic dependencies

- **`design-studio`** owns `plan-design-review`. autoplan calls it as the design lens.
- **`build`** consumes the approved plan + loadout. The plan-room → build handoff is the moment the user says "go build it."
- **`ship`** comes after build; gets the plan's success criteria as the ship verdict bar.
- **`second-brain`** captures decisions (`Projects/<slug>/decisions.md`), preferences (`Actions/<slug>.md`), and status (`Projects/<slug>/status.md`).
- **`router`** dispatches Codex when a review lens needs implementation-level second-opinion ("is this DB migration safe under concurrent writes?").
- **`project-orchestrator`** (apex, Phase 6) wraps plan-room → build → design-studio → ship → second-brain into one prompt.

---

## What plan-room does NOT do

- Does not implement (that's `build` + Codex via `router`)
- Does not write code (that's Codex)
- Does not design UIs (that's `design-studio`)
- Does not ship or deploy (that's `ship`)
- Does not run security audits (that's `cso`, inline during `build`)
- Does not own the design lens (lives in `design-studio`; autoplan calls across)
- Does not grill the user with 30 questions — recommends answers, surfaces only what needs the user's taste
- Does not auto-execute the plan after approval — the user triggers the next mechanic explicitly

---

## Wrenches

| Wrench | Path | What it does |
|---|---|---|
| **process-interviewer** | `wrenches/process-interviewer.md` | Default intake. 1-question-at-a-time with recommended answers. Routes to brief-generator |
| **project-brief-generator** | `wrenches/project-brief-generator.md` | Emits the project's CLAUDE.md (north star, stack, constraints, success criteria, out of scope) |
| **project-loadout** | `wrenches/project-loadout.md` | Right-sizes plugins / MCPs / skills for the stated scope. Minimum set, not max |
| **autoplan** | `wrenches/autoplan.md` | Runs the 4-lens review pipeline with auto-decisions. Surfaces only borderlines |
| **plan-ceo-review** | `wrenches/plan-ceo-review.md` | Scope / ambition / 10-star product lens. 4 modes: expand / selective / hold / reduce |
| **plan-eng-review** | `wrenches/plan-eng-review.md` | Architecture / data flow / edge cases / test coverage / perf lens |
| **plan-devex-review** | `wrenches/plan-devex-review.md` | DX lens for dev-facing projects (APIs / CLIs / SDKs / docs) |
| **decision-toolkit** | `wrenches/decision-toolkit.md` | Bezos 1/2 door triage → right framework → kill criteria + review date |
| **office-hours** | `wrenches/office-hours.md` | YC 6 forcing questions (startup mode) OR builder-mode brainstorm (side projects) |

---

## Cost shape

| Wrench | Lane | Cost ballpark |
|---|---|---|
| `process-interviewer` | Claude reasoning, recommended-answer style | low (5-10 questions, fast) |
| `office-hours` | Claude reasoning, YC forcing questions | low-medium (6 questions deep) |
| `decision-toolkit` | Claude reasoning, framework selection | low-medium |
| `project-brief-generator` | Claude writes CLAUDE.md | low (one document) |
| `project-loadout` | Claude maps scope → capability set | low |
| `autoplan` | 4 lens runs + synthesis | medium-high (4 Claude reasoning passes + 1 synth) |
| Individual lens wrench | Claude reasoning + scoring | medium |
| Cross-mechanic to design-studio | one lens call | medium |
| Cross-mechanic to Codex (when needed) | rare; only for one specific question | low |

Total full-pipeline cost is dominated by autoplan. The intake wrenches are cheap because they're conversational.

---

## Helper scripts (live at `scripts/`)

- `plan-state.py` — `.plan-state.json` reader/writer (`get` / `set` / `init --project` / `complete`); tracks which lens has been run, with what verdict, across the autoplan pipeline so resume across sessions works without re-running passed lenses
- `decision-log.py` — appends decision-toolkit outputs to `_system/second-brain/Projects/<slug>/decisions.md` (fields: `--decision` / `--reasoning` / `--alternatives` / `--confidence` / `--links`). Full decision-toolkit records — kill criteria, review date, framework, reversibility — are written by the `decision-toolkit` wrench directly, not via this script.
- `loadout-detect.sh` — snapshots the current plugin / MCP / skill loadout (via the `claude` CLI, with filesystem fallback). Mapping the snapshot against capability signals (Python backend? mobile? scraping? deep research? long context?) to compute a suggested loadout is the `project-loadout` wrench's job, not the script's.

All three shipped and were acceptance-tested 2026-05-28. Invocations are documented in `autoplan.md` and `project-loadout.md`.

---

## See also

- [wrenches/process-interviewer.md](wrenches/process-interviewer.md) — default intake
- [wrenches/project-brief-generator.md](wrenches/project-brief-generator.md) — CLAUDE.md emitter
- [wrenches/project-loadout.md](wrenches/project-loadout.md) — capability right-sizing
- [wrenches/autoplan.md](wrenches/autoplan.md) — 4-lens review pipeline
- [wrenches/plan-ceo-review.md](wrenches/plan-ceo-review.md) — scope / ambition lens
- [wrenches/plan-eng-review.md](wrenches/plan-eng-review.md) — architecture lens
- [wrenches/plan-devex-review.md](wrenches/plan-devex-review.md) — DX lens
- [wrenches/decision-toolkit.md](wrenches/decision-toolkit.md) — Bezos 1/2 door + framework
- [wrenches/office-hours.md](wrenches/office-hours.md) — YC forcing questions + builder brainstorm
- [`AGENTS.md`](../../../AGENTS.md) — hard rule #5 (Claude does planning, Codex does code)
- [`design-studio/SKILL.md`](../design-studio/SKILL.md) — owns plan-design-review (cross-mechanic call)
- [`build/SKILL.md`](../build/SKILL.md) — what consumes the approved plan
- [`second-brain/SKILL.md`](../second-brain/SKILL.md) — where decisions land
