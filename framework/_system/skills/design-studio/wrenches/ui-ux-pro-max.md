---
name: design-studio-ui-ux-pro-max
description: Design knowledge guidance wrench. Generates design guidance across many styles, color palettes, font pairings, product types, UX guidelines, and chart types — model-generated on demand, NOT a stored/counted dataset on disk. Reference lookup tool — used by other wrenches as a knowledge source, also directly when the user asks "what's a good color palette for X" / "font pairing for Y" / "UX pattern for Z". Trigger phrases include "ui ux pro max", "color palette for", "font pairing", "design pattern", "UX guideline", "chart type", "design knowledge", "what's the right pattern for".
---

# design-studio-ui-ux-pro-max — design knowledge base

Reference wrench. Other wrenches in design-studio (design-consultation, design-html, deck-builder) consult this for typography, color, layout, and pattern decisions. Also fires directly when the user asks lookup questions.

---

## When to fire

- "What's a good color palette for [domain]"
- "Font pairing for [aesthetic]"
- "Best chart type for [data shape]"
- "UX pattern for [situation]"
- "What style suits [project]"
- Called as a sub-step from other design-studio wrenches

Don't fire when:
- The user wants to actually build something (route to design-html / deck-builder / design-shotgun)
- The knowledge gap is broader than reference lookup (route to design-consultation)

---

## Knowledge domains

| Domain | Examples |
|---|---|
| Styles | Glassmorphism, claymorphism, minimalism, brutalism, neumorphism, bento grid, dark mode, responsive, skeuomorphism, flat design |
| Color | Palettes: primary + accent + neutral schemes, accessibility-aware |
| Typography | Font pairings, scale recommendations, web-safe + custom |
| Layout | Grid systems, hero patterns, navigation patterns, footer patterns |
| UX guidelines | Patterns: hierarchy, focus, feedback, loading, errors, empty states |
| Charts | Chart types across the 9 stacks (React, Vue, Svelte, SwiftUI, RN, Flutter, Tailwind, shadcn, HTML/CSS) |
| Component patterns | Buttons, modals, navbars, sidebars, cards, tables, forms |
| Product types | Website, landing, dashboard, admin, ecommerce, SaaS, portfolio, blog, mobile |

---

## How to use

For a lookup query, the wrench:
1. Identifies the domain
2. Filters by relevant constraints (the user's stack, project aesthetic, content)
3. Returns 2-3 top recommendations with rationale
4. Optionally generates inline preview (mini HTML sample)

For other wrenches consuming this, it's a function call — they ask "give me a 3-color palette for [aesthetic + use case]" and get back the palette + reasoning.

---

## See also

- [SKILL.md](../SKILL.md)
- [design-consultation.md](design-consultation.md) — uses this for system decisions
- [design-html.md](design-html.md) — uses this for pattern selection
- [awesome-design.md](awesome-design.md) — alternative: pick a full brand DNA instead
