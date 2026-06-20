---
name: design-studio-stitch
description: Google Stitch AI design generator driver. Collects reference images (godly.website / dribbble) → opens stitch.withgoogle.com in Chrome → crafts the prompt → generates → refines → downloads ZIP (DESIGN.md + HTML). Returns the artifacts. Alternative variant source to design-shotgun. Trigger phrases include "use stitch", "generate a stitch design", "stitch mockup", "vibe design", "design this in stitch", "make a stitch UI", "Google stitch".
---

# design-studio-stitch — Google Stitch driver

Drives Google's Stitch AI design tool via chrome-devtools-mcp. Outputs a ZIP with DESIGN.md + HTML that's drop-in usable for the project.

---

## When to fire

- The user says "use stitch" / "stitch mockup"
- After design-shotgun if the user wants AI-generated variants in addition
- For greenfield UI work where reference-image-driven generation is the easiest path

Don't fire when:
- The user has DESIGN.md already (skip to design-html)
- Internet / Stitch unavailable

---

## Sequence

1. The user describes the design (project type + aesthetic + must-haves)
2. Wrench searches godly.website / dribbble for 2-3 reference images
3. Open chrome-devtools-mcp to stitch.withgoogle.com
4. Type the prompt + upload references
5. Wait for generation
6. The user picks a variant
7. Download the ZIP
8. Extract DESIGN.md + HTML into the project

---

## See also

- [SKILL.md](../SKILL.md)
- [design-shotgun.md](design-shotgun.md) — alternative variant source (Claude-generated)
- [design-html.md](design-html.md) — what follows once a design is picked
