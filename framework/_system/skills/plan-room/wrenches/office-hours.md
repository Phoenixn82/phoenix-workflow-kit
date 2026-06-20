---
name: plan-room-office-hours
description: YC office hours wrench. Two modes — startup mode (6 forcing questions on demand reality, status quo, desperate specificity, narrowest wedge, observation, future-fit) and builder mode (design-thinking brainstorming for side projects, hackathons, learning, open source). Pressure-tests fuzzy ideas BEFORE plan-room scaffolds anything. Saves a design doc. Trigger phrases include "office hours", "is this worth building", "brainstorm this", "pressure-test this idea", "I have an idea", "help me think through this".
---

# plan-room-office-hours — pressure-test before plan

When the user has a fuzzy idea — not yet clear enough for `process-interviewer` to intake — this wrench pressure-tests it first. Two modes: startup (YC-style demand reality check) and builder (design-thinking brainstorm for non-commercial work).

The point is to validate the idea is worth planning BEFORE plan-room invests in briefs / loadouts / autoplan reviews. Cheap upfront filter; saves heavy review on ideas that should have been killed at intake.

---

## When to fire

- "Office hours" / "is this worth building" / "pressure-test this"
- "I have an idea" / "brainstorm this with me" / "help me think through this"
- The user describes a product idea that no code exists for yet
- The user is exploring (not deciding — that's `decision-toolkit`)
- Auto-fires from plan-room SKILL.md when Q1 of process-interviewer can't be answered confidently

Don't fire when:
- The user has already validated the idea elsewhere → skip to process-interviewer
- The decision shape is "should I X" not "is X worth building" → route to decision-toolkit
- The user wants to plan execution, not exploration → skip to process-interviewer

---

## Mode 1: Startup mode (YC forcing questions)

Used when the idea has commercial / user-facing aspirations. Validates demand reality before any planning.

### Q1: Demand reality

Who has this problem today, badly enough to seek a solution, often enough to remember, and frequently enough to pay?

Recommended answer: <Claude infers from the user's pitch + Mom Test framing>

The hard version: name 3 specific people (or 1 specific user persona the user could find 10 of). If the user can't, that's signal #1 against.

### Q2: Status quo

What do these people do today instead? What's their hack / workaround / spreadsheet / 3rd-party tool?

Recommended answer: <inferred>

The hard version: if the user can't name the status quo, his target users haven't actually felt the pain. They might want it in theory; they don't have it in practice.

### Q3: Desperate specificity

How desperate is the pain, and how specific is the user? "Tech-savvy people who want better tools" doesn't count. "Solo Shopify operators with under $50K MRR who lose 2+ hours/week to spreadsheet reconciliation" counts.

Recommended answer: <inferred specificity>

The hard version: every adjective you can drop without changing the answer is fuel. Strip until the description is uncomfortably narrow.

### Q4: Narrowest wedge

What's the smallest, sharpest version of the product that solves the desperate-specific problem for the named user?

Recommended answer: <inferred narrow wedge>

The hard version: "first product" not "platform vision." Solve ONE thing extremely well; expand only after that proves out.

### Q5: Observation

Have you actually watched / interviewed / shadowed your target user doing the painful thing? Or are you guessing what they need?

Recommended answer: typically "guessing" for early ideas

The hard version: if no, that's the next step before any code. Observation > assumption.

### Q6: Future-fit

If this works as planned, what does the world look like in 5 years? Is that a world worth building? Does it fit a trend you believe in?

Recommended answer: <inferred future state>

The hard version: if the answer is "incremental improvement to status quo," consider whether the activation energy of building it is justified. If the answer is "this changes the shape of the space," that's the swing worth taking.

---

## After the 6 questions: verdict

The wrench synthesizes:

```markdown
## Office hours verdict — <idea>

**Mode:** Startup

### Demand reality
- People with this problem: <named or inferred>
- Pain frequency: <how often>
- Pain magnitude: <willing to pay, willing to work around, indifferent>

### Status quo
- Current solution: <named>
- Strength of current solution: <weak / adequate / strong>

### Desperate specificity score
- 0-10 on how specific the target is. <Strip more if < 7.>

### Narrowest wedge
- Sharpest v1: <one sentence>

### Observation gap
- Need to do: <interviews / shadowing / data review> BEFORE code

### Future-fit
- 5-year picture: <one paragraph>
- Trend bet: <explicit>

### Verdict
- KILL: <if the idea fails core forcing questions>
- VALIDATE FIRST: <if it needs observation before planning>
- PROCEED: <if it passes all 6 forcing questions>

### If PROCEED, next: process-interviewer to scope the v1 wedge
```

The verdict drives the routing. KILL means stop here. VALIDATE FIRST means observation work before planning. PROCEED means the idea has legs and `process-interviewer` is the next wrench.

---

## Mode 2: Builder mode (design thinking)

Used when the idea has no commercial intent — side projects, hackathons, learning, open source. Different question set; demand reality matters less.

### Build-mode questions

1. **Why this, why now?** What about the user's current state makes this the right thing to build right now? What would change if he didn't?
2. **What does the magical moment feel like?** When this thing exists and works, what's the first moment that makes you smile? Build the rest backward from there.
3. **What would 80% / 20% / 5% look like?** Different levels of done. 80% = polished, demo-worthy. 20% = works for the user only. 5% = the spike that proves the core mechanism.
4. **What's the spike?** The smallest test of the core idea. Could be a script, a sketch, a 1-page mock. The user should know what the spike is by end of this question.
5. **What does sharing this look like?** Showing one friend? Hacker News post? Tweet thread? Github repo? Discord channel? No share is fine too. The frame matters.
6. **What about this would teach the user something he'd want to know?** If the project's purpose is partly learning, name the lesson.

### Builder verdict

```markdown
## Office hours verdict — <idea>

**Mode:** Builder

### Why now
<answer>

### Magical moment
<one sentence>

### Done levels
- 80%: <description>
- 20%: <description>
- 5% (the spike): <description>

### The spike
<concrete first thing to build, ~1 day max>

### Sharing frame
<answer>

### Lessons embedded
<answer>

### Verdict
- BUILD THE SPIKE: ready to go small
- BIGGER PLAN NEEDED: scope is too big for spike alone; go to process-interviewer
- NOT YET: idea isn't crystallized enough; keep brainstorming
```

Builder mode bias is toward shipping the spike fast. Most builder-mode ideas should end with "go build the spike, see how it feels, decide next."

---

## Save the design doc

After the verdict, save the office-hours session as a design doc in `_system/second-brain/Ideas/<slug>.md`:

```markdown
---
type: idea
date: 2026-05-28
status: parked | exploring | promoted
mode: startup | builder
tags: [<domain>]
---

# <Idea title>

**For future Claude:** <one paragraph: what the idea is, what problem it solves, why the user is/isn't building it yet>

[Full office-hours output verbatim]

**Verdict:** <KILL / VALIDATE FIRST / PROCEED / BUILD SPIKE>
**Next step:** <specific action>

**Links:** [[<related ideas>]] [[<adjacent projects>]]
```

If verdict is PROCEED or BUILD SPIKE and the user says go, the next wrench fires. If verdict is KILL or NOT YET, the idea sits in `Ideas/` until the user returns to it.

---

## Cost shape

- 6 forcing questions: medium (each with recommended answer + the user's response)
- Verdict synthesis: small
- Save design doc: small
- Total: low-medium. Half the cost of process-interviewer because the questions are forcing (single-answer), not open-ended.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Every idea ends in KILL | Forcing questions too aggressive for builder mode | Pick mode first; builder mode has different bar |
| the user can't answer the demand questions | Idea genuinely hasn't been validated | Verdict is VALIDATE FIRST; that's the right answer |
| Recommendations feel like cold reads | Not enough conversation context to infer | Ask the user to elaborate before recommending |
| the user wants to PROCEED on an idea that failed Q1 | His call; surface the risk, let him override | Record the override in the design doc; future sessions remember |

---

## See also

- [SKILL.md](../SKILL.md) — plan-room mechanic
- [process-interviewer.md](process-interviewer.md) — runs after PROCEED verdict
- [decision-toolkit.md](decision-toolkit.md) — different intake path ("should I X" vs "is X worth building")
- [project-brief-generator.md](project-brief-generator.md) — emits CLAUDE.md after process-interviewer
- [`second-brain/wrenches/capture.md`](../../second-brain/wrenches/capture.md) — where idea design docs land
