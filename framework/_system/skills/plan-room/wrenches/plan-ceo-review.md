---
name: plan-room-plan-ceo-review
description: CEO / founder-mode plan review lens. Rethinks the problem, hunts for the 10-star product, challenges premises, expands scope when bigger creates a better product. 4 modes — SCOPE EXPANSION (dream big), SELECTIVE EXPANSION (hold scope, cherry-pick), HOLD SCOPE (max rigor on existing scope), SCOPE REDUCTION (strip to essentials). Lens 1 of autoplan's 4-lens pipeline. Also fires direct on "ceo review", "think bigger", "is this ambitious enough", "rethink scope", "expand scope", "strategy review", "10 star product".
---

# plan-room-plan-ceo-review — scope / ambition lens

The CEO lens asks: is this plan the right plan? Not "is the architecture right" (that's eng). Not "does it look good" (that's design). Not "is the DX clean" (that's devex). The CEO lens asks "is the product good — is the scope right, is the ambition right, is this the 10-star version of what's possible, or are we settling for 3-star."

---

## When to fire

- Auto-fires as lens 1 of autoplan's 4-lens pipeline
- Direct: "CEO review" / "think bigger" / "is this ambitious enough" / "strategy review"
- After project-brief-generator when the user asks for a scope sanity check before eng

Don't fire when:
- Plan is already locked and the user just wants execution review (skip to eng)
- The change is small (< 1 day of work; CEO review is over-engineering)
- The user is mid-build (CEO review is upstream)

---

## The 4 modes

The lens picks one mode based on signal from the plan + the user's stated preference. The user can override:

### Mode 1: SCOPE EXPANSION (dream big)

Fires when:
- The user says "think bigger" / "what's the 10-star version"
- The plan feels conservative for what's possible
- The brief's first slice is so small it might not validate anything

Mode behavior:
- Challenge the boundaries of the brief — is "out of scope" right?
- Propose adjacent features that would make this a step-change product
- Frame: if you could 10x this, what would it be?
- Output: list of expansion options + tradeoffs

### Mode 2: SELECTIVE EXPANSION (hold scope, cherry-pick)

Fires when:
- The plan is mostly right but one or two areas would benefit from bigger thinking
- The user says "mostly keep this scope, but consider adding X"

Mode behavior:
- Accept the existing scope as the baseline
- Cherry-pick 1-2 high-leverage expansions
- Per expansion: what changes + cost + payoff
- Output: kept scope + 1-2 specific additions

### Mode 3: HOLD SCOPE (max rigor on existing scope)

Default mode when no signal pushes elsewhere.

Mode behavior:
- Don't expand or reduce
- Stress-test the existing plan: is it solving the right problem? Is the success criteria the right metric? Is the first slice actually useful?
- Find weak premises the plan assumes
- Output: scored findings on what to firm up, NOT what to add/remove

### Mode 4: SCOPE REDUCTION (strip to essentials)

Fires when:
- The plan is too big for the time / budget / risk tolerance
- The user says "this is too much; what's the minimum"
- Smallest-reasonable-scope principle applies hard

Mode behavior:
- Identify the absolute minimum that still solves the JTBD
- Propose cuts with rationale
- Output: stripped-down plan + what got cut + why

---

## Dimensions scored (0-10)

| Dimension | What a 10 looks like |
|---|---|
| **Problem fit** | Solves a real, frequent, painful problem the user can name with users |
| **Solution leverage** | The smallest intervention that creates the biggest user-visible improvement |
| **Ambition** | Goes for the 10-star version, not settling for 3-star "good enough" |
| **First slice** | The first thing shipped is small enough to validate quickly, useful enough to prove the idea |
| **Success criteria** | Quantifiable, observable, falsifiable (not "users love it") |
| **Scope discipline** | "Out of scope" list bounds the work; no creep happens |
| **Risk awareness** | Names the 2-3 things that could kill this, with plans to test for them early |

Composite score weights problem fit + first slice + risk awareness highest (those kill most projects).

---

## The 10-star question

For every plan, the CEO lens asks: if this works exactly as planned, is it a 10-star product, or a 3-star product?

3-star answer: "It works. The user uses it. Nobody talks about it."
10-star answer: "the user uses it daily. People he tells about it can't stop asking when it's launching. He'd rebuild it from scratch if he had to."

If the answer is 3-star, the lens proposes what would bridge to 10. Often that's not "more features" — it's "deeper insight into the user, narrower target, more specific JTBD."

---

## The Mom Test frame

Beyond scoring, the lens checks: does this plan assume user behavior the user hasn't validated? Common Mom Test failures:

- "Users will want X" without evidence
- "Users will pay for X" without anyone having paid
- "This will replace X" without anyone trying to switch
- "This solves X problem" without anyone naming X as a problem

The lens flags Mom Test risks as borderlines for autoplan to surface — they don't have an obvious fix, but the user should know they exist.

---

## Output format

```markdown
## CEO review — <project>

**Mode:** HOLD SCOPE (selected because <reason>)
**Composite score:** 7.5/10

### Per-dimension
| Dimension | Score | Notes |
|---|---|---|
| Problem fit | 9 | the user has the problem himself, daily |
| Solution leverage | 7 | Solves it but the intervention is bigger than minimum |
| Ambition | 6 | First slice is good; full vision is incremental, not step-change |
| First slice | 8 | Ships in 2 weeks, validates the core mechanism |
| Success criteria | 9 | "the user uses it daily for 30 days" — quantifiable, observable |
| Scope discipline | 8 | Out-of-scope list is tight |
| Risk awareness | 6 | Names tech risk but misses demand risk (Mom Test) |

### Key findings
1. **Demand risk underweighted** (risk awareness) — Plan assumes the user's pain is shared by others without evidence. Validate or bound.
2. **First slice could go smaller** (solution leverage) — Could the validation happen in 1 week instead of 2?
3. **Ambition tradeoff** — HOLD SCOPE chose; if EXPAND was the right mode, here's the 10-star version: [...]

### Recommendations
- Keep scope as-is
- Add a validation milestone before first slice ships: 5 user interviews with similar JTBDs (1 week, no code)
- Defer ambition expansion to v2

### What I would NOT do
- Don't add features in v1
- Don't expand the user persona
- Don't pre-build for hypothetical edge cases
```

---

## Cost shape

- One Claude reasoning pass on the brief + plan
- One reasoning pass to score dimensions
- One pass to draft findings + recommendations
- Total: medium. Cheaper than eng review (no architecture analysis) but deeper than checklist work.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Always picks "EXPAND" mode | Plan IS conservative | Validate with the user — sometimes the plan really is too small |
| Always picks "REDUCE" mode | Plan IS too big | Same — validate |
| Scores feel arbitrary | Dimensions not weighted right for this project | Tune weights per project |
| Doesn't flag obvious Mom Test risk | Inference missed it | Pull from second-brain — the user may have flagged similar risks before |
| Recommendations conflict with eng lens | Two valid angles | autoplan surfaces the tension; the user decides |

---

## Pairing with autoplan

CEO is lens 1. Its output feeds autoplan's auto-decision step alongside the other 3 lenses. CEO's findings get classified:

- Findings that an auto-decision principle resolves → auto-resolved by autoplan
- Findings that need the user's taste → queued for the borderline gate

When CEO flags a Mom Test risk, that's almost always a borderline (no principle auto-resolves "do you have evidence for this assumption?").

---

## See also

- [SKILL.md](../SKILL.md) — plan-room mechanic
- [autoplan.md](autoplan.md) — pipeline driver that calls this lens
- [plan-eng-review.md](plan-eng-review.md) — lens 2
- [plan-devex-review.md](plan-devex-review.md) — lens 4
- [office-hours.md](office-hours.md) — when scope itself is unclear, run office-hours BEFORE this lens
- [`design-studio/wrenches/plan-design-review`](../../design-studio/wrenches/plan-design-review.md) — design lens (lives in design-studio)
