---
name: design-studio-design-review
description: Live visual QA wrench. Finds visual inconsistency, spacing issues, hierarchy problems, AI-slop patterns, slow interactions on the live site. Iteratively fixes each issue in source via Codex (per AGENTS.md hard rule #5), commits atomically, re-verifies with before/after screenshots. For plan-time design review (before implementation), use plan-design-review instead. Trigger phrases include "design review", "visual QA", "audit the design", "polish the UI", "check if it looks good", "the site looks off", "find AI slop".
---

# design-studio-design-review — live visual QA + fix

After ship lands a UI change, design-review audits it visually and fixes what's off. Drives chrome-devtools-mcp for the walk; dispatches Codex via router for the fix work.

For PLAN-time design review (before code exists), use `plan-design-review` cross-mechanic call from autoplan.

---

## When to fire

- After ship deploys a UI-touching change
- Direct: "design review" / "polish the UI" / "audit the look"
- The user says "the site looks off" / "find what's wrong visually"

Don't fire when:
- No live site exists yet (use plan-design-review at plan time instead)
- Issue is functional, not visual (route to qa)

---

## What gets checked

| Category | Examples |
|---|---|
| Spacing | Inconsistent gaps between sections; touchpoints too close |
| Hierarchy | Heading sizes don't communicate priority; CTAs lost in noise |
| Alignment | Things that should align don't; baseline drift |
| Color | Contrast failures; off-palette colors crept in |
| Typography | Mixed fonts; inconsistent line-heights; widow/orphan lines |
| Responsiveness | Layouts break at mobile / tablet / wide |
| Motion | Janky animations; too-slow transitions; surprise motion |
| AI-slop tells | Generic centered-card-on-gradient; emoji as design; lorem ipsum left in; Tailwind purple-to-pink by default |
| Interaction | Hover states missing; focus rings invisible; loading states absent |

---

## Sequence

1. Navigate to live URL via chrome-devtools-mcp
2. take_snapshot + take_screenshot at desktop / tablet / mobile
3. Walk critical pages from the brief
4. Compile findings list, severity-tagged
5. For each finding, propose fix
6. The user approves fixes (batch)
7. Dispatch Codex per AGENTS.md hard rule #5 for the source changes
8. Re-verify via chrome-devtools-mcp screenshots before/after
9. Commit atomically per fix
10. Surface final state

---

## Live debug requirement

Per global CLAUDE.md frontend-visual-debugging rule, every CSS fix gets injected via `evaluate_script` before persisting. The user sees it live in his browser; only on confirmation does Codex commit to source.

---

## Cost shape

- chrome-devtools-mcp walk = medium (multiple snapshots + screenshots per page)
- Findings reasoning = medium
- Codex dispatch per fix = low per fix, but N fixes adds up
- Total: medium-high; dominated by fix count

---

## See also

- [SKILL.md](../SKILL.md)
- [plan-design-review.md](plan-design-review.md) — plan-time variant
- [`ship/wrenches/qa.md`](../../ship/wrenches/qa.md) — functional QA equivalent
- [`AGENTS.md`](../../../../AGENTS.md) — hard rule #5 (Codex writes fixes)
