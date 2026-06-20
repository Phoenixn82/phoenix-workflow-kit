---
name: design-studio-awesome-design
description: Brand DNA library wrench (dispatcher). Brand identities are codified on demand as markdown design systems at awesome-design-library/<slug>.md; currently 1 is seeded (phoenix-web-ai) — the rest (Apple, Claude, Stripe, Vercel, Notion, Linear, Anthropic, ...) are generated when first requested, NOT pre-stocked. Pick/seed a brand → adopt its design language. Trigger phrases include "awesome design", "design like Apple", "design like Claude", "use a brand DNA", "make it look like Stripe", "brand-inspired design", "design system from library".
---

# design-studio-awesome-design — brand DNA library

A brand-DNA **dispatcher**, not a pre-stocked shelf. Each brand's design system is codified as a markdown file the first time it's requested; **only `phoenix-web-ai.md` is seeded today.** When the user says "design like Stripe" and `stripe.md` doesn't exist yet, generate it (via Firecrawl brand extraction / design-consultation) and save it to the library so the next call is instant. Faster than design-consultation from scratch once a brand's DNA is captured.

---

## When to fire

- The user says "design like X" / "make it look like Apple/Stripe/Claude/etc."
- New project where a known brand's aesthetic would fit
- After design-shotgun when one variant matched a known brand's feel

Don't fire when:
- Project has its own established brand
- The user wants something genuinely original (route to design-consultation)
- The brand requested isn't in the library (push back; offer closest match or design-consultation)

---

## The library shape

Each brand DNA is a markdown file at `_system/skills/design-studio/awesome-design-library/<brand-slug>.md` containing:

- Aesthetic direction (the feeling, the references, what they don't do)
- Typography (fonts + weights + scale)
- Color (palette + how it's used)
- Layout (grid + max-widths + spacing)
- Motion (easing + duration + what animates)
- Pattern library (their hero / features / pricing patterns)
- Voice (their copy style if relevant)
- Reference URL (their actual site)

(Library is seed-on-demand — this wrench is the dispatcher. Seeded so far: `phoenix-web-ai.md`. Generate-and-save any other brand the first time it's asked for; don't promise a brand file exists without checking the dir.)

---

## How it integrates with design-html

```
1. The user: "design like Anthropic"
2. awesome-design loads anthropic.md
3. Becomes the project's DESIGN.md (or merges into existing)
4. design-html consumes it as the system
```

---

## See also

- [SKILL.md](../SKILL.md)
- [design-consultation.md](design-consultation.md) — alternative: design from scratch
- [design-html.md](design-html.md) — consumes the picked brand
