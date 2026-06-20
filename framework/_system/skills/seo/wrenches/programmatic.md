---
name: seo-programmatic
description: Programmatic SEO planning. Pages generated at scale from data sources. Covers template engines, URL patterns, internal linking automation, thin content safeguards, index bloat prevention. Trigger phrases include "programmatic SEO", "pages at scale", "dynamic pages", "template pages", "generated pages", "data-driven SEO", "pSEO", "pages from database".
---

# seo-programmatic — pages-at-scale SEO

When you have a dataset (locations, products, comparison combinations, feature pairs, etc.) and want each row to be its own SEO-targeted page. Done well, it dominates long-tail. Done poorly, it's index bloat + thin content disaster.

---

## When to fire

- "Programmatic SEO for X dataset"
- "Generate pages from this database"
- "Template page strategy"

Don't fire when:
- Editorial content (use content / cluster)
- One-off pages (just write them)

---

## Core decisions

### 1. URL pattern

| Pattern | Use |
|---|---|
| `/<category>/<item>` | "/restaurants/pizza-place-nyc" |
| `/<location>/<service>` | "/new-york/dentist" |
| `/<a>-vs-<b>` | "/postgres-vs-mysql" |
| `/<topic>/<aspect>` | "/marketing/email-automation" |

Pattern affects crawl, internal linking, hierarchy.

### 2. Template depth

Each page must have substantial unique content per row. The wrench scores:

- Template variables that change: 0 (low) — 50 (high)
- Unique paragraphs per row: target 3+
- Unique data per row: target 5+ data points
- Unique images per row: target 1+

If rows are too template-similar, Google sees doorway pages. Cut OR enrich.

### 3. Index strategy

- All in index → simple but risks bloat if pages are thin
- Top N% in index, rest noindex → quality over quantity
- Tier-based → top tier in index, mid tier in index with noindex on near-duplicates

The wrench recommends based on dataset shape + content depth per row.

### 4. Internal linking automation

- Each programmatic page links to: 3-5 related programmatic pages, 1 hub page, 1-2 supporting editorial
- Related selection: by data similarity (e.g., same category, geographic neighbor) NOT random
- Anchor text: variety (mix of exact / partial / generic / branded)

### 5. Thin content safeguards

- Per-row minimum word count (e.g., 400 unique words)
- Per-row minimum data points
- Skip rows with insufficient source data
- Periodic audit: pages with low impressions / no clicks after 90 days → consolidate or noindex

---

## Implementation handoff

The wrench plans + audits. Implementation (writing the template engine, the data pipeline, the page generator) is `build` + Codex per hard rule #5.

---

## See also

- [SKILL.md](../SKILL.md)
- [plan.md](plan.md) — broader strategy context
- [content.md](content.md) — thin-content audit for live programmatic pages
- [sitemap.md](sitemap.md) — sitemap structure for programmatic
- [`build/SKILL.md`](../../build/SKILL.md) — implementation
- [`AGENTS.md`](../../../../AGENTS.md) — hard rule #5 (Codex implements)
