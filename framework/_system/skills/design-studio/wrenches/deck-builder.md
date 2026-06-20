---
name: design-studio-deck-builder
description: Slide deck builder. Two formats — --format=html (brand-driven HTML decks with Awesome Design DNA + 20 codified design principles) or --format=marp (Marp-flavored Markdown, marp-cli renders to HTML). Caps slide count per deck type (pitch ≤ 12, lightning ≤ 6, workshop ≤ 25). Proposes outline before generation to prevent sprawl. Saves to ~/Documents/claude-decks/. Merged from the old power-design + slide-builder skills. Trigger phrases include "build a deck", "presentation for", "make slides", "pitch deck", "slideshow", "slides about", "turn this into a deck", "marp deck".
---

# design-studio-deck-builder — decks in two formats

Merged from `power-design` (HTML brand decks) and `slide-builder` (Marp Markdown decks). The user picks the format with `--format=html|marp`.

---

## When to fire

- "Build a deck" / "make slides" / "pitch deck for"
- "Presentation about X" / "slides on Y"
- "Marp deck" / "html deck"

Don't fire when:
- The deliverable is a doc, not slides (route to make-pdf or content-forge)
- The user wants a single page, not slides (route to design-html)

---

## The two formats

### `--format=html` (brand-driven HTML decks)

- Uses awesome-design brand DNA + 20 codified design principles
- Outputs `index.html` + assets in `~/Documents/claude-decks/<slug>/`
- Slide nav: arrow keys, swipe, click
- Speaker notes via `?speaker-notes`
- Print-friendly print stylesheet

### `--format=marp` (Marp Markdown)

- Outputs `slides.md` with Marp frontmatter
- If marp-cli installed, renders to HTML automatically
- Speaker notes in HTML comments
- Easier to version-control and edit later

---

## Slide count caps

| Deck type | Max slides |
|---|---|
| Lightning talk | 6 |
| Pitch deck | 12 |
| Demo deck | 15 |
| Standard talk | 20 |
| Workshop | 25 |

Caps prevent sprawl. The user can override but the cap is a forcing function for "is this slide carrying weight."

---

## Outline approval rule (load-bearing)

Before generating ANY slides, deck-builder proposes a slide outline:

```markdown
## Proposed outline (12 slides max — pitch deck)
1. Title / opening
2. The problem
3. The status quo
4. The solution (visual)
5. How it works (3 steps)
6. Why now
7. Traction / proof
8. The market
9. Business model
10. The team
11. The ask
12. Thank you / contact
```

The user approves before any slide content gets drafted. Prevents the "AI generated 25 fluff slides" anti-pattern.

---

## See also

- [SKILL.md](../SKILL.md)
- [awesome-design.md](awesome-design.md) — brand DNA for HTML decks
- [make-pdf.md](make-pdf.md) — alternative when deliverable is a doc
- [ui-ux-pro-max.md](ui-ux-pro-max.md) — chart types for data slides
