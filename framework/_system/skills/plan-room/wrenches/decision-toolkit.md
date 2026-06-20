---
name: plan-room-decision-toolkit
description: Decision framework wrench. Triages by reversibility (Bezos type 1/2 door), classifies the decision type, routes to the right framework (WRAP / pre-mortem / OODA / expected value / regret minimization / second-order thinking / ICE-RICE / SWOT / decision matrix / Eisenhower), walks the user through it one question at a time with recommended answers, runs a Munger blind-spot pass, and emits a saved decision record with kill criteria and review date. Trigger phrases include "should I", "stuck on a decision", "help me decide", "pros and cons", "decision framework", "pre-mortem", "weigh options", "decision toolkit".
---

# plan-room-decision-toolkit — Bezos triage + right framework

When the user is stuck on a decision, this wrench picks the right framework for the shape of the decision and walks him through it — one question at a time, with recommended answers. Output is a saved decision record with kill criteria and a review date.

This is one of plan-room's two intake paths (the other is `office-hours` for fuzzy ideas). Pick this when the user asks "should I do X" rather than "is X worth building."

---

## When to fire

- "Should I X" / "help me decide" / "stuck on a decision"
- "Pros and cons" / "weigh options" / "decision framework"
- "Pre-mortem this" / "what could go wrong if I X"
- Direct: "/decide" / "decision toolkit"
- After the user has been deliberating without progress for 2+ exchanges

Don't fire when:
- The decision is already made (the user wants execution, not deliberation)
- The choice is between option A or option A (no real decision)
- The user is exploring an idea, not choosing (route to `office-hours`)
- It's a quick decision with no consequence (just answer)

---

## Step 1: Bezos type 1 / type 2 door triage

Every decision is one of:

- **Type 1 (irreversible).** Once made, you can't un-make it cheaply. Examples: hiring senior leadership, choosing a database, committing to a public launch date, marrying a vendor.
- **Type 2 (reversible).** You can change course later for low cost. Examples: trying a feature, picking a tool to test, framing a hypothesis.

Type 2 doors should be walked through fast — bias toward action. Type 1 doors deserve deep analysis — slow down.

The wrench's first question:

```
Reversibility check:
- If you make this decision and it's wrong, what does undoing it cost?
- Days/weeks of work, money on the table, relationships damaged, public commitments to walk back?

Recommended classification: Type 2 (most decisions are; if in doubt, it's type 2)
- Type 1: <if the user confirms type 1>
- Type 2: <if the user confirms type 2>
```

The classification routes everything downstream. Type 2 gets a fast framework. Type 1 gets a careful one.

---

## Step 2: Classify the decision shape

Different decisions need different frameworks. After reversibility, the wrench classifies the shape:

| Shape | Framework | When |
|---|---|---|
| Multiple options, weighing pros/cons | **WRAP** (Widen options / Reality-test / Attain distance / Prepare for wrong) | Standard comparison |
| Bet on uncertain outcomes | **Expected value** | Numerical probabilities + outcomes |
| Pre-launch / pre-ship risk | **Pre-mortem** | Imagine it failed in 1 year, write the story |
| Strategic positioning | **SWOT** | When understanding competitive context matters |
| Resource allocation across many options | **ICE / RICE** | Prioritization across N candidates |
| Operational urgency | **Eisenhower** (urgent vs important) | Triage today's choices |
| Reactive / fast-moving | **OODA** (Observe / Orient / Decide / Act) | Time-pressured situations |
| Regret-avoidance | **Regret minimization** | Big life-shape decisions ("would 80-year-old me regret this?") |
| Long-chain consequences | **Second-order thinking** | Decisions whose consequences ripple |
| Multi-dimensional comparison | **Decision matrix** | When you can score options against weighted criteria |

The wrench picks based on signals in the user's question. Most "should I" decisions are WRAP. Specific phrases route differently:

- "What could go wrong" → Pre-mortem
- "Is the bet worth it" → Expected value
- "Will I regret it" → Regret minimization
- "What's the downstream impact" → Second-order thinking
- "How do I prioritize these N options" → ICE/RICE
- "Where does this fit in the market" → SWOT

If multiple shapes apply, pick the dominant one and offer the others as supplementary passes.

---

## Step 3: Walk the framework

Once the framework is picked, the wrench walks the user through it. Same recommended-answer rule applies — every question has a suggested answer the user can accept / edit / override.

### Example: WRAP walkthrough (most common)

**Widen options**
```
Q: What other options exist beyond <option A> and <option B>?
Recommended: <list 2-3 inferred options>
The user: accept / edit / override
```

**Reality-test**
```
Q: What evidence supports each option? What evidence contradicts?
Recommended: <for each option, infer 1-2 evidence points pro/con>
The user: accept / edit / override
```

**Attain distance**
```
Q: If a friend in your situation asked your advice, what would you tell them?
Recommended: <inferred outside-view advice>
The user: accept / edit / override
```

**Prepare for wrong**
```
Q: What's the early signal you'd watch for to know you picked the wrong option?
Recommended: <inferred signal>
The user: accept / edit / override
```

Frame each as one question at a time. Don't dump the whole framework.

### Other frameworks: same shape

Pre-mortem: "It's 1 year later, this decision was a disaster. Write the story of why." → the user lists 3-5 reasons; the wrench groups them into root causes; the user picks mitigations.

Expected value: probabilities × outcomes. The wrench helps the user put rough numbers (10% / 50% / 90%, not exact) on each branch.

Regret minimization: project to 80-year-old self; "would past me regret not taking this swing?"

Second-order thinking: for each first-order consequence, what's the second-order effect? Third? Stops when patterns stabilize.

---

## Step 4: Munger blind-spot pass

After the framework walks, the wrench runs one final pass: Charlie Munger's "invert, always invert" + common cognitive blind spots.

```
Munger checks:
- Confirmation bias: am I only counting evidence that supports my preferred answer?
- Anchoring: am I stuck on the first option I considered?
- Sunk cost: am I picking this because I've already invested, not because it's right?
- Availability heuristic: am I overweighting recent / vivid memories?
- Authority bias: am I deferring to someone whose context doesn't match mine?
- Overconfidence: am I more certain than the evidence warrants?

For each YES signal, the wrench flags it for the user's awareness.
```

This is a quick pass — doesn't redo the framework, just sanity-checks the conclusion.

---

## Step 5: Kill criteria + review date

Every decision record includes:

- **Decision:** the chosen option
- **Reasoning:** one paragraph
- **Alternatives considered + why rejected:** one bullet each
- **Confidence:** stated low / medium / high
- **Kill criteria:** specific signals that would say "I picked wrong, change course"
- **Review date:** when to check if kill criteria fired

Kill criteria are concrete: "If by <date> we don't see X, abandon and switch to Y." Not vague: "If it's not working, reconsider."

Review date is calendared. The wrench writes to `_system/second-brain/Projects/<slug>/decisions.md` so future sessions can read.

---

## Output: the decision record

```markdown
## 2026-05-28 — Switch from REST to GraphQL for v2 API?

**Decision:** Stay with REST for v2. Defer GraphQL until v3 if needed.

**Reasoning:** the user's primary API users are existing REST integrations. The GraphQL benefits (precise queries, single endpoint) don't outweigh migration cost for current users. Re-evaluate when 30% of users want GraphQL-specific features.

**Framework used:** WRAP

**Reversibility:** Type 2 (can layer GraphQL on later without breaking REST)

**Alternatives considered:**
- Full GraphQL migration → too disruptive for existing users
- REST + GraphQL parallel → infrastructure cost too high for v2 timeline
- Stay REST (chosen)

**Confidence:** medium-high

**Kill criteria:**
- If by 2026-08-01, 5+ paying customers request GraphQL specifically → revisit
- If response payload over-fetching becomes a top-3 complaint → revisit
- If a competitor launches GraphQL and starts pulling users → revisit

**Review date:** 2026-08-01

**Munger blind spots flagged:**
- Anchoring on existing REST (declared; weighted in reasoning)

**Links:** [[<project>]] [[<related-decisions>]]
```

This record gets appended to the project's `decisions.md` via second-brain. Future sessions can grep the file for "GraphQL" and find the prior thinking.

---

## Cost shape

- Triage + framework selection: small
- Framework walkthrough: small-medium per question (the user answers, wrench thinks)
- Munger pass: small
- Decision record write: small
- Total: low-medium. Cheaper than autoplan, deeper than office-hours.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| the user bails partway | Framework too heavy for the decision | Suggest a simpler framework (regret min for big, decision matrix for simple) |
| Reasoning feels generic | Recommendations didn't pull project context | Read CLAUDE.md + prior decisions before recommending |
| Kill criteria too vague | Default was bad | Force specificity: "If X by Y date" |
| Decision gets reversed soon after | Underweighted reversibility | Bias toward type 2 framing; less analysis paralysis |

---

## See also

- [SKILL.md](../SKILL.md) — plan-room mechanic
- [process-interviewer.md](process-interviewer.md) — when "should I X" turns into "let's plan X"
- [office-hours.md](office-hours.md) — when the decision is "should I build this idea"
- [`second-brain/wrenches/capture.md`](../../second-brain/wrenches/capture.md) — where decision records land
- [`AGENTS.md`](../../../../AGENTS.md) — the user's preferences (recommended answers, no grilling)
