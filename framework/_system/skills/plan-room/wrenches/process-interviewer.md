---
name: plan-room-process-interviewer
description: Default intake wrench for plan-room. One question at a time, every question with a recommended answer the user can accept / edit / override. Validates against JTBD + Mom Test signals. Emits a PRD-style brief that project-brief-generator turns into CLAUDE.md. For fuzzy ideas, routes to office-hours first; for "should I" decisions, routes to decision-toolkit. Trigger phrases include "interview me about X", "intake", "process me through this", "let's plan X", "I want to build X", "new project", "brain dump", "PRD for X", "before we build".
---

# plan-room-process-interviewer — recommended-answer intake

When the user arrives with a project idea — anything from "I want to build a search filter" to a 20-paragraph brain dump — this wrench turns it into a clear-enough brief. Every question comes with a recommended answer. The user can accept, edit, or override.

This is the default intake. For "is this worth building" pressure-tests, use `office-hours` first. For "should I do X" decisions, use `decision-toolkit`. process-interviewer assumes scope is implied and just needs articulation.

---

## When to fire

- New project intake when the user has a rough idea
- After a brain-dump when the user needs structure
- Direct: "interview me about X" / "PRD for X" / "intake"
- Pipeline auto-fires from plan-room SKILL.md when intent isn't decision / pressure-test

Don't fire when:
- The user is in "should I X" mode → route to `decision-toolkit`
- The idea is fuzzy and needs pressure-test → route to `office-hours`
- The user has a brief already → skip to `project-brief-generator`
- The ask is trivial (one-file change, no scope to interview) → just do the work

---

## The recommended-answer rule (load-bearing)

Every question this wrench asks comes with a recommended answer based on what's already known from:

- The current conversation context
- Files in the working directory (codebase state, existing CLAUDE.md, prior plan-state.json)
- The user's known preferences from `_system/second-brain/Actions/`
- Prior projects in `_system/second-brain/Projects/`
- The default for projects of this shape

The format is always:
```
Q: <question>
Recommended: <inferred answer>
[the user: accept / edit / override]
```

NOT:
```
Q: <question>
[the user: type long answer]
```

Forcing the user to type long answers to 20 questions is the bad pattern this wrench is designed to avoid. He reviews recommended answers fast; he types slow.

---

## The intake questions (default set)

Asked in order, one at a time. The user can short-circuit ("just generate the brief now") at any point.

### Q1: North star

What is this project for? (One sentence — the "why," not the "what.")

Recommendation source: inferred from conversation + brain dump.

### Q2: Target user

Who is this for? (the user himself? Specific users? Internal team? Customers paying $X/mo?)

Recommendation source: inferred from context, with default "the user himself" for personal-workflow projects.

### Q3: Real job-to-be-done

What's the JTBD this solves? (The Mom Test frame: would users actually pay / use / show up for this, or are you assuming they will?)

Recommendation source: if office-hours has already run, pull from there. Otherwise infer + flag for the user to validate.

### Q4: Core stack

What's the tech stack? (Per project conventions if it's not greenfield. For greenfield, the simplest reasonable choice for the JTBD.)

Recommendation source: detect existing stack from project files (package.json, pyproject.toml, etc.) OR default to the user's known preferences (Next.js + Tailwind + Vercel for web, etc.).

### Q5: Success criteria

How do we know it worked? (Quantifiable when possible. "Users do X" / "metric Y moves" / "the user uses it daily" / "ships in N weeks.")

Recommendation source: infer the obvious metric for the JTBD. If unclear, flag as borderline for autoplan.

### Q6: Out of scope

What's explicitly NOT in this project? (Important — bounds the work.)

Recommendation source: the obvious adjacent things the user might want but shouldn't bundle. List 2-3 candidates.

### Q7: Constraints

Time / budget / dependencies / team that constrain how this can be built?

Recommendation source: infer from context. Default to "the user's time + the tools already in his stack."

### Q8: Risks

What could kill this? (Tech risk, demand risk, scope creep, etc.)

Recommendation source: infer 2-3 candidate risks. Flag as borderlines for autoplan.

### Q9: First slice

What's the smallest version of this that's still useful?

Recommendation source: derive from north star + success criteria. Apply the smallest-reasonable-scope principle.

### Q10: Done condition

When is "v1 done"? (Specific: "X works for Y user in Z context." Not vague: "feels good.")

Recommendation source: derive from success criteria + first slice.

---

## Short-circuit conditions

The user can stop the interview at any point:

- "Just generate the brief now" → skip remaining questions, fill defaults, hand off to project-brief-generator
- "I'll fill the rest in CLAUDE.md myself" → emit a partial brief with TODO markers
- "Skip to autoplan" → emit brief from what's gathered, route to autoplan directly
- "Actually, this should be office-hours" → re-route mid-flow

The wrench accepts these without complaint. The point is intake hygiene, not bureaucracy.

---

## Routing decisions

After Q1-Q3 (the first 3 questions), the wrench can decide whether process-interviewer is still the right wrench:

| Signal | Action |
|---|---|
| the user can't answer Q1 clearly ("I'm not sure what this is for") | Pause; suggest office-hours pressure-test instead |
| the user says "I'm not sure if this is worth doing" | Pause; suggest decision-toolkit instead |
| the user can answer Q1-Q3 confidently | Continue with Q4-Q10 |

Re-routing is fine and good. Don't grind through 10 questions on an idea that hasn't passed Q1.

---

## Output: PRD-style brief

Once questions are answered (fully or partially), emit:

```markdown
# <Project name> — Brief

## North star
<answer to Q1>

## Target user
<answer to Q2>

## JTBD
<answer to Q3 — including Mom Test signal>

## Stack
<answer to Q4>

## Success criteria
<answer to Q5 — quantified where possible>

## Out of scope
<answer to Q6>

## Constraints
<answer to Q7>

## Risks
<answer to Q8>

## First slice
<answer to Q9>

## Done condition (v1)
<answer to Q10>

## Notes from intake
- <any borderline calls flagged for autoplan>
- <any conflicting signals between answers>
```

This brief hands off to `project-brief-generator` to become the project's CLAUDE.md.

---

## Cost shape

- One Claude reasoning pass per question + recommended answer
- 10 questions max, but most flows are 5-7 (short-circuits, partial fills)
- Total: low. Intake should be fast.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| the user says "this is taking too long" | Too many questions for a small project | Apply smallest-reasonable-scope to the intake itself; cut to 3-4 questions |
| Recommended answer is way off | Bad context inference | Ask the user to override; learn from the override |
| the user can't answer Q1 | Idea isn't clear enough for an intake | Re-route to office-hours |
| the user wants to debate every recommendation | Recommendations aren't strong enough | Make recommendations more opinionated (more like the office-hours forcing questions); fewer hedges |

---

## See also

- [SKILL.md](../SKILL.md) — plan-room mechanic
- [office-hours.md](office-hours.md) — pressure-test fuzzy ideas before this wrench
- [decision-toolkit.md](decision-toolkit.md) — "should I X" route
- [project-brief-generator.md](project-brief-generator.md) — what consumes this wrench's output
- [`AGENTS.md`](../../../../AGENTS.md) — the user's preferences (terse, no grilling, recommended answers)
