---
name: seo-page
description: Single-URL deep SEO analysis. Covers on-page elements, content quality, technical meta tags, schema, images, performance, GEO citability. Trigger phrases include "analyze this page", "check page SEO", "single URL", "check this page", "page analysis", or a single URL alone for review.
---

# seo-page — deep per-URL audit

When the user wants one URL examined thoroughly. Not a quick check — pulls everything: on-page, content, schema, perf, image, GEO citability.

---

## When to fire

- Single URL + SEO ask
- "Analyze https://..."
- "Check page SEO on X"
- After `audit` flags a URL needing deep dive

Don't fire when:
- Multiple URLs → audit or per-URL loop
- Sitewide question → other wrenches

---

## Dimensions checked

| Dimension | What |
|---|---|
| **Title tag** | Length 30-60 chars, keyword inclusion, brand handling |
| **Meta description** | Length 120-160 chars, CTA, unique vs other pages |
| **H1** | Present, unique, contains primary topic |
| **Heading hierarchy** | H1 → H2 → H3 logical; no skipped levels |
| **Canonical** | Self-referencing or correctly pointing elsewhere |
| **Open Graph** | Title / description / image / type present |
| **Twitter Card** | Same |
| **Schema** | Detected JSON-LD types; validation |
| **Internal links** | Count, anchor text variety, link to relevant other pages |
| **External links** | rel attributes, link to authority |
| **Images** | Alt text, file size, modern format |
| **Word count** | Total + main-content-only |
| **Content depth** | Topic coverage vs SERP top 10 |
| **Performance** | LCP / INP / CLS via PageSpeed (if google wrench ready) |
| **GEO citability** | Passage-level quotability, structured answers |
| **Mobile-friendliness** | Viewport meta, touch targets, font size |

---

## Output shape

```markdown
## Page audit — https://example.com/page

**Composite score:** 7.2/10

### On-page
- Title: 52 chars — OK
- Meta description: 134 chars — OK
- H1: present, matches title intent
- Heading hierarchy: valid

### Content
- Word count: 1247 (main content: 980)
- Depth vs SERP top 10: covers 60% of topics; missing X, Y, Z
- E-E-A-T signals: author present, citations present, no bio link (FIX)
- Reading level: grade 9

### Schema
- Detected: Article, BreadcrumbList, FAQPage
- Validation: pass
- Missing for this page type: Person (author)

### Performance (from PSI)
- LCP: 2.1s (good)
- INP: 180ms (good)
- CLS: 0.04 (good)
- Bundle: 287 KB

### Images
- 8 images total
- 6 with alt text (75%)
- 2 oversized (>500 KB each) — recommend WebP

### GEO
- Passage citability: 6/10 (some answers buried in prose; add structured Q&A)
- llms.txt referenced: yes
- AI Overviews match: unknown (need DataForSEO or live check)

### Top fixes
1. Add alt text to 2 images
2. Compress 2 oversized images / convert to WebP
3. Add Person schema for author
4. Restructure intro to lead with direct answer for AI citation
```

---

## See also

- [SKILL.md](../SKILL.md)
- [audit.md](audit.md) — dispatches `page` on top 10 pages
- [technical.md](technical.md) / [content.md](content.md) / [schema.md](schema.md) / [images.md](images.md) / [geo.md](geo.md) — dimension-specific deep dives
