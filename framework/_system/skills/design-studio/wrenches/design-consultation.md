---
name: design-studio-design-consultation
description: DRIP intake wrench. Understands the product, researches the design landscape, proposes a complete design system (aesthetic, typography, color, layout, spacing, motion), generates font and color preview pages, writes DESIGN.md as the project's design source of truth. For existing sites with no DESIGN.md, can infer the system instead. Trigger phrases include "design consultation", "design system from scratch", "brand guidelines", "create DESIGN.md", "design intake", "what's the design system for this".
---

# design-studio-design-consultation — DRIP intake

The intake step of DRIP. Turns "I want this designed well" into a concrete design system the user can hand to design-html / awesome-design / deck-builder.

---

## When to fire

- New project needing a design system
- Existing project with no DESIGN.md (infer current system)
- The user says "let's pick a design language" / "what's our brand"
- Before design-html when no system is established

Don't fire when:
- Project already has a DESIGN.md that's still right
- The user already picked an awesome-design brand (skip to that wrench)
- The ask is a visual fix on an existing page (route to design-review)

---

## Sequence

1. **Understand product.** Read brief + CLAUDE.md. What is it, who is it for, what feeling should it evoke?
2. **Research landscape.** Sample 5-10 sites in the space. Note common patterns + interesting outliers. Use Gemini lane for deep landscape research; web-scrape for sampling specific sites.
3. **Propose system.** Aesthetic direction (modern minimal / brutalist / glassmorphic / bento / etc.), typography (heading + body + mono), color (primary + accents + neutrals), layout grid, spacing scale, motion language.
4. **Generate previews.** Font preview page (all weights, sample text, hierarchy). Color preview page (palette + gradients + UI samples).
5. **Write DESIGN.md.** Project's design source of truth.
6. **Confirm.** the user approves the system before any production HTML is built.

---

## DESIGN.md shape

```markdown
# <Project> — Design System

## Aesthetic direction
<one paragraph: the feeling, the references, what we're not>

## Typography
- **Heading:** <font + weights + use>
- **Body:** <font + weights + use>
- **Mono:** <font + use>
- **Scale:** <h1 / h2 / h3 / body / small in rem>

## Color
- **Primary:** <hex>
- **Accent:** <hex>
- **Neutrals:** <list>
- **Semantic:** success / warning / danger / info
- **Backgrounds:** light / dark

## Layout
- **Grid:** <12-col / 16-col / asymmetric>
- **Max-width:** <px>
- **Spacing scale:** <4 / 8 / 12 / 16 / ... rem>

## Motion
- **Easing:** <standard / spring / linear>
- **Duration:** <150 / 250 / 400 ms ranges>
- **What animates:** <list>

## References
- <site 1>: <what we took>
- <site 2>: <what we took>
```

---

## See also

- [SKILL.md](../SKILL.md)
- [awesome-design.md](awesome-design.md) — alternative path: pick a brand DNA
- [design-html.md](design-html.md) — consumes the system
- [ui-ux-pro-max.md](ui-ux-pro-max.md) — reference for choices
