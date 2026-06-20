---
name: design-studio-design-html
description: Production HTML/CSS output wrench. Generates Pretext-native HTML with real text reflow, dynamic heights, responsive layouts (not static screenshots). 30KB overhead, zero deps. Smart pattern routing per design type (landing / dashboard / docs / blog / etc.). Consumes DESIGN.md or an awesome-design brand. Trigger phrases include "design-html", "finalize this design", "turn this into HTML", "build me a page", "implement this design", "production HTML", "final code".
---

# design-studio-design-html — production HTML output

The Integrate step of DRIP. Real production code — text reflows, heights compute, layouts adapt. The deliverable for "build me a landing page" / "make the production HTML."

Per AGENTS.md hard rule #5, when this wrench produces an actual code file, it's working FROM Claude's design spec but Codex does the per-file authorship for any production codebase. For one-off mockup HTML, Claude can author.

---

## When to fire

- After design-consultation OR awesome-design picks a system
- The user says "build the page" / "production HTML" / "finalize this design"
- After plan-design-review approves a plan with UI components

Don't fire when:
- DESIGN.md doesn't exist yet (run design-consultation first)
- The user wants to explore options (route to design-shotgun)
- Output should be a deck (route to deck-builder)
- Output should be a PDF (route to make-pdf)

---

## Output discipline

- **Real text.** Lorem ipsum allowed only for placeholder; final output has the user's actual copy
- **Real heights.** No fixed `height: 600px` on a hero. Heights compute from content
- **Real responsive.** Mobile-first; test at 375px, 768px, 1024px, 1440px
- **No JS frameworks** unless the user specifies. Vanilla HTML/CSS for mockups
- **Zero deps** for the mockup tier; if production needs Tailwind/Next, Codex translates per AGENTS.md

---

## Pattern routing

| Design type | Pattern set |
|---|---|
| Landing page | Hero / features / social proof / pricing / CTA / footer |
| Dashboard | Sidebar / topbar / main grid / cards / charts |
| Docs site | Sidebar TOC / main content / inline ToC / search |
| Blog | List / detail / author / archive |
| Pricing page | Tiers / comparison table / FAQ / CTA |
| Settings | Sidebar nav / form fields / save bar |

The wrench picks patterns based on the brief + DESIGN.md. Custom patterns supported via the user's spec.

---

## Live debug requirement

Per global CLAUDE.md frontend-visual-debugging rule, every CSS/layout fix during this process MUST be injected via `chrome-devtools-mcp` `evaluate_script` first. The user sees it live. Only after he confirms does the change land in the HTML/CSS source.

---

## See also

- [SKILL.md](../SKILL.md)
- [design-consultation.md](design-consultation.md) — emits DESIGN.md
- [awesome-design.md](awesome-design.md) — alternative system source
- [design-review.md](design-review.md) — post-build visual QA
- [`AGENTS.md`](../../../../AGENTS.md) — hard rule #5
