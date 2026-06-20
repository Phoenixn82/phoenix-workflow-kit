---
name: design-studio-design-shotgun
description: Variant explorer. Generates multiple AI design variants (3-6), opens a comparison board, collects structured feedback, iterates. Standalone design exploration usable anytime — not gated to a specific DRIP step. Trigger phrases include "design shotgun", "explore designs", "show me options", "design variants", "visual brainstorm", "I don't like how this looks", "what else could this look like".
---

# design-studio-design-shotgun — variant explorer

When the user isn't sure what direction to go (or the current direction isn't right), shotgun generates multiple variants and lets him pick.

---

## When to fire

- "Show me options" / "explore designs" / "variants of X"
- After design-consultation when the user wants to see what the system could look like before committing
- After design-html when the output isn't working visually

Don't fire when:
- The user already knows what he wants (skip to design-html)
- The brand is locked-in via awesome-design (variants aren't needed)

---

## Sequence

1. Take a brief or existing reference
2. Generate 3-6 variants spanning different directions (minimal / brutalist / glassy / playful / etc.)
3. Render each as static HTML in a project-local scratch dir, e.g. `.scratch/shotgun-<n>/index.html` (or `$env:TEMP\shotgun-<n>\index.html`) — Windows-real paths, not POSIX `/tmp`
4. Open them in chrome-devtools-mcp side-by-side (or screenshot grid for review)
5. The user reviews + picks favorite + says what to change
6. Iterate on the picked variant or re-shotgun if none clicked

---

## Comparison board

For 4+ variants, generate a side-by-side comparison HTML at `.scratch/shotgun-board.html` (or `$env:TEMP\shotgun-board.html`) — Windows-real, not `/tmp` — with:
- Variant name / direction
- Screenshot
- One-line feel description
- Voting / picking UI (just visual; the user says which)

---

## Cost shape

- Variant generation = N variants × medium reasoning each
- Render = trivial (HTML to disk)
- The user review = conversational

---

## See also

- [SKILL.md](../SKILL.md)
- [design-consultation.md](design-consultation.md) — broader intake
- [design-html.md](design-html.md) — what to do after variant is picked
- [stitch.md](stitch.md) — Google's AI design generator (alternative variant source)
