---
name: design-studio-make-pdf
description: Publication-quality PDF generator. Shared wrench between design-studio and content-forge (lives here; content-forge cross-references). Proper 1-inch margins, intelligent page breaks, page numbers, cover pages, running headers, curly quotes and em dashes, clickable TOC, optional diagonal DRAFT watermark. Not a draft artifact — a finished artifact. Trigger phrases include "make a pdf", "publication pdf", "export to pdf", "generate document", "turn markdown into pdf", "professional pdf", "pdf with cover page".
---

# design-studio-make-pdf — publication-quality PDF

Markdown in, publication-quality PDF out. Shared with content-forge (lives physically here; content-forge cross-references).

---

## When to fire

- "Make a PDF" / "export to PDF" / "publication PDF"
- After content-forge content is final and the user wants a publishable artifact
- After a doc is approved and a PDF deliverable is needed

Don't fire when:
- Output should be HTML (route to design-html or deck-builder)
- Output is a deck (route to deck-builder)

---

## Quality bar

This wrench produces a finished artifact, not a draft. Everything renders correctly:

- Proper 1-inch margins (top / bottom / left / right)
- Intelligent page breaks (no widow/orphan, no page break mid-paragraph if avoidable)
- Page numbers (footer center; first page optional)
- Cover page (title / author / date / project)
- Running headers (project title or chapter title)
- Curly quotes and em dashes (typography pass)
- Clickable TOC (if the doc has headings)
- Inline images rendered correctly with captions
- Code blocks with syntax highlighting + proper monospace
- Optional diagonal DRAFT watermark via `--draft`

---

## Sequence

1. Read input markdown
2. Pre-process: curly quotes, em dashes, smart typography
3. Generate cover page
4. Generate TOC from headings (if 3+ headings)
5. Render to PDF (Pandoc / Typst / WeasyPrint depending on what's available)
6. Add page numbers + running headers
7. Add DRAFT watermark if `--draft`
8. Save to specified output path

---

## Flags

```bash
make-pdf input.md --output output.pdf
make-pdf input.md --output output.pdf --draft
make-pdf input.md --output output.pdf --no-cover
make-pdf input.md --output output.pdf --no-toc
make-pdf input.md --output output.pdf --title "Custom Title"
make-pdf input.md --output output.pdf --author "the user"
```

---

## See also

- [SKILL.md](../SKILL.md)
- [`content-forge/SKILL.md`](../../content-forge/SKILL.md) — make-pdf is shared with content-forge, which cross-references this wrench (there is no separate `content-forge/wrenches/make-pdf.md`)
- [design-html.md](design-html.md) — alternative when output should be web
- [deck-builder.md](deck-builder.md) — alternative when output should be slides
