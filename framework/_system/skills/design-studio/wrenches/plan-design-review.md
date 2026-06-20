---
name: design-studio-plan-design-review
description: Plan-time design lens. Called cross-mechanic by plan-room's autoplan as lens 3 of the 4-lens review pipeline. Rates design dimensions 0-10, explains what would make each a 10, then fixes the plan to get there. Plan-time only — for live site visual audits, use design-review. Trigger phrases include "plan-design-review", "design lens", "design critique on the plan", "review the design plan", "is the design plan good".
---

# design-studio-plan-design-review — plan-time design lens

Cross-mechanic lens called by `plan-room/autoplan`. Reviews the PLAN's design surface BEFORE any HTML is built. Catches design issues at plan time.

For LIVE visual audit after the site is built, use `design-review` instead.

---

## When to fire

- Called cross-mechanic from `plan-room/autoplan` (lens 3 of 4-lens pipeline)
- Direct: "plan-design-review" / "design lens on the plan"
- Before any design-html work, when the user has a plan with UI components

Don't fire when:
- No plan exists (push back to plan-room)
- The project has no UI surface (skip entirely)
- The site is already live (route to design-review)

---

## Dimensions scored (0-10)

| Dimension | What a 10 looks like |
|---|---|
| **Information hierarchy** | Plan specifies what's primary / secondary / tertiary on each page; CTAs prioritized |
| **Visual identity** | Brand DNA picked (awesome-design or design-consultation done); colors / type / spacing established |
| **User flow clarity** | Plan walks the user from entry to goal in clear steps |
| **Responsive strategy** | Plan addresses mobile / tablet / desktop intentionally, not as an afterthought |
| **Accessibility** | Plan addresses contrast, focus states, alt text, semantic HTML |
| **Interaction language** | Plan names how things animate, hover, focus, load |
| **Empty / error states** | Plan addresses what users see when there's no data / something fails |
| **Component reuse** | Plan identifies reusable patterns instead of one-off designs per page |

---

## Output format

Same shape as plan-ceo-review / plan-eng-review / plan-devex-review (consistent for autoplan synthesis):

```markdown
## Design review (plan-time) — <project>

**Composite score:** 7.0/10

### Per-dimension
[table with scores + notes]

### Key findings
1. **<finding 1>** — what to fix
2. **<finding 2>** — what to fix

### What would make this a 10
- <specific change 1>
- <specific change 2>

### What I would NOT change
- <intentional choices to preserve>
```

---

## Common findings

- "No brand DNA picked yet" → recommend awesome-design or design-consultation
- "Mobile-first not addressed in plan" → push back
- "All pages designed individually, no component reuse" → propose pattern library
- "Empty states / loading states / errors not in plan" → add them
- "Plan describes layouts but not interactions" → tighten
- "Plan mentions 'modern minimal' but no spec for what that means" → push to specifics

---

## See also

- [SKILL.md](../SKILL.md)
- [`plan-room/wrenches/autoplan.md`](../../plan-room/wrenches/autoplan.md) — caller
- [design-review.md](design-review.md) — live (post-build) equivalent
- [design-consultation.md](design-consultation.md) — fix path when brand isn't picked
- [awesome-design.md](awesome-design.md) — fix path when brand DNA is needed
