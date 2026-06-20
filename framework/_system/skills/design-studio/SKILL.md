---
name: design-studio
description: "Design pipeline mechanic. Brand consultation → variant exploration → production HTML/decks/PDFs → live visual QA. Owns the design lens (plan-design-review) that plan-room's autoplan calls cross-mechanic. Default: DRIP framework (Design → Refine → Integrate → Publish). Fires on \"design this\", \"build a website\", \"make a landing page\", \"design system\", \"brand guidelines\", \"deck\", \"presentation\", \"design review\", \"audit the look\", \"polish the UI\", \"visual QA\", \"plan-design-review\"."
---

# design-studio — brand-driven design pipeline

The lane where intent becomes a designed surface. Brand DNA in, polished HTML / decks / PDFs out. Owns the design lens that plan-room's autoplan calls across mechanics for plan-design-review.

Per AGENTS.md, plan happens before design; design happens before build. The user's design pipeline runs from "I need a system" through to "this thing looks shipped."

---

## Cardinals

1. **DRIP framework default.** Design → Refine → Integrate → Publish. Each step has its wrenches. Don't skip Refine — variant exploration prevents committing to a v1 that's worse than v2 would have been.

2. **Brand DNA over generic.** awesome-design is a seed-on-demand brand-DNA library (only `phoenix-web-ai` is codified today; generate + save any other brand the first time it's requested — see the wrench). Use a brand identity as the reference unless the user's project has its own established system. Generic "Tailwind components on a white background" is the AI-slop default to avoid.

   **Design-variety system (load these — they make the difference between distinct sites and same-y ones):** every site = **STRUCTURE × STYLE × STACK**, rotated so no two builds repeat the combo. STRUCTURE = pick a layout archetype from [`layout-library/ARCHETYPES.md`](layout-library/ARCHETYPES.md); STYLE = the brand DNA above (`awesome-design-library/<slug>.md`); STACK = pick a framework/tooling combo from [`framework-library/FRAMEWORKS.md`](framework-library/FRAMEWORKS.md). Consult all three before scaffolding (standing rule [[Actions/design-variety]]).

3. **Real text, real heights, real responsive.** Per the legacy design-html skill: text actually reflows, heights compute dynamically, layouts adapt. Static-width-only mockups are insufficient. Production output is the deliverable, not a screenshot.

4. **Live debug via chrome-devtools-mcp before persisting.** Per the global CLAUDE.md frontend-visual-debugging rule, every CSS/layout fix gets injected via `evaluate_script` in the live browser first. Only after the user sees it working live does the change land in source.

5. **plan-design-review is the cross-mechanic lens.** plan-room's autoplan calls into this mechanic for the design lens. The lens lives here because design knowledge lives here, not because plan-room is the right home for it. Same pattern as cso inline during build.

6. **Codex writes the integration code, not Claude.** Per AGENTS.md hard rule #5, when designs translate to production code (Tailwind tokens to design system, React components from mockups), Codex writes the code. Claude does the design + spec.

---

## The DRIP pipeline

```
                    ┌─────────────────────────────────┐
       intent ────► │ Design                          │
                    │ - design-consultation (intake)  │
                    │ - awesome-design (brand DNA)    │
                    │ - ui-ux-pro-max (knowledge)     │
                    └─────────────┬───────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────┐
                    │ Refine                          │
                    │ - design-shotgun (variants)     │
                    │ - stitch (Google AI driver)     │
                    └─────────────┬───────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────┐
                    │ Integrate                       │
                    │ - design-html (production HTML) │
                    │ - deck-builder (HTML or Marp)   │
                    │ - make-pdf (publication PDF)    │
                    └─────────────┬───────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────┐
                    │ Publish                         │
                    │ - design-review (visual QA loop)│
                    │ - hand off to ship              │
                    └─────────────────────────────────┘
```

The user can call individual wrenches direct. The dispatcher walks DRIP by default for "design a website" / "build me a landing page" / "design system from scratch."

---

## Picking the wrench

| Shape of the ask | Wrench | Why |
|---|---|---|
| "Design system from scratch" / "brand guidelines" | `design-consultation` (intake) → `awesome-design` (brand DNA) | DRIP Design step |
| "Build a website" / "landing page" | full DRIP pipeline | the user doesn't see the mechanic split; he just gets a shipped site |
| "Show me variants of X" / "design options" | `design-shotgun` direct | Just want exploration |
| "Use Stitch / AI design generator" | `stitch` direct | Stitch's specific workflow |
| "Final HTML / production code" | `design-html` direct | Skip to integrate |
| "Build a deck / presentation / slides" | `deck-builder --format=html\|marp` | Specific to decks |
| "Publication PDF" | `make-pdf` (shared with content-forge) | Both mechanics use this wrench |
| "Visual QA the live site" / "audit the design" / "polish the UI" | `design-review` direct | Live audit + fix loop |
| "What design pattern for X" / "knowledge base" | `ui-ux-pro-max` direct | Reference lookup |
| "Plan-design-review" (called from autoplan) | `plan-design-review` direct | Cross-mechanic call from plan-room |

---

## Cross-mechanic dependencies

- **`plan-room`** calls `plan-design-review` cross-mechanic during autoplan
- **`build`** consumes design outputs; design-html's HTML becomes the production code base
- **`content-forge`** shares `make-pdf` (lives here; content-forge cross-references)
- **`ship`** receives the designed surface; design-review can fire after ship deploys
- **`router`** dispatches Codex for design → code translation (Tailwind component generation, React component scaffolds)
- **`second-brain`** captures design decisions, brand notes, variant rejections at `Actions/design-variety.md` (or per-project vault notes, matching current practice in `Projects/phoenix-web-ai/`)

---

## What design-studio does NOT do

- Does not implement (Codex via router)
- Does not ship or deploy (that's `ship`)
- Does not own content production (`content-forge`)
- Does not do scope / ambition lens (that's `plan-ceo-review`)
- Does not do architecture lens (that's `plan-eng-review`)
- Does not run security audits (`cso`)

---

## Wrenches

| Wrench | Path | What it does |
|---|---|---|
| **design-consultation** | `wrenches/design-consultation.md` | Intake: understand product → research landscape → propose complete system + font/color preview |
| **design-html** | `wrenches/design-html.md` | Production-quality Pretext-native HTML/CSS, real text reflow, dynamic heights |
| **design-shotgun** | `wrenches/design-shotgun.md` | Generate multiple AI design variants, comparison board, structured feedback |
| **design-review** | `wrenches/design-review.md` | Live visual QA with fix loop. chrome-devtools-mcp drives; Codex writes fixes |
| **awesome-design** | `wrenches/awesome-design.md` | Brand DNA library (seed-on-demand; `phoenix-web-ai` seeded — generate others on first request) |
| **ui-ux-pro-max** | `wrenches/ui-ux-pro-max.md` | Design knowledge guidance (styles, palettes, font pairings, chart types — model-generated guidance, not a stored dataset) |
| **deck-builder** | `wrenches/deck-builder.md` | Slide decks: `--format=html` (brand decks) or `--format=marp` (Markdown) |
| **stitch** | `wrenches/stitch.md` | Google Stitch AI design generator driver (chrome-devtools-mcp) |
| **make-pdf** | `wrenches/make-pdf.md` | Publication-quality PDF (shared with content-forge) |
| **plan-design-review** | `wrenches/plan-design-review.md` | Plan-time design lens called by plan-room's autoplan |

---

## See also

- [wrenches/design-consultation.md](wrenches/design-consultation.md) — DRIP intake
- [wrenches/design-html.md](wrenches/design-html.md) — production HTML output
- [wrenches/design-shotgun.md](wrenches/design-shotgun.md) — variant explorer
- [wrenches/design-review.md](wrenches/design-review.md) — live visual QA + fix
- [wrenches/awesome-design.md](wrenches/awesome-design.md) — brand DNA library (STYLE axis)
- [wrenches/ui-ux-pro-max.md](wrenches/ui-ux-pro-max.md) — design knowledge guidance
- [layout-library/ARCHETYPES.md](layout-library/ARCHETYPES.md) — STRUCTURE axis (layout archetypes for design variety)
- [framework-library/FRAMEWORKS.md](framework-library/FRAMEWORKS.md) — STACK axis (framework/tooling combos for design variety)
- [wrenches/deck-builder.md](wrenches/deck-builder.md) — decks (HTML or Marp)
- [wrenches/stitch.md](wrenches/stitch.md) — Google Stitch
- [wrenches/make-pdf.md](wrenches/make-pdf.md) — publication PDFs
- [wrenches/plan-design-review.md](wrenches/plan-design-review.md) — cross-mechanic plan lens
- [`AGENTS.md`](../../../AGENTS.md) — hard rule #5 (Codex writes code, including design→code)
- [`plan-room/wrenches/autoplan.md`](../plan-room/wrenches/autoplan.md) — calls plan-design-review cross-mechanic
- [`content-forge/SKILL.md`](../content-forge/SKILL.md) — make-pdf is shared with content-forge; its SKILL.md cross-references this wrench (there is no `content-forge/wrenches/make-pdf.md` — the wrench lives here)
