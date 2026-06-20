---
name: seo-audit
description: Full-site SEO audit dispatcher. Crawls up to 500 pages, detects business type, fires 8 always-wrenches + up to 9 conditional in parallel via the Agent tool. Generates composite health score. Trigger phrases include "SEO audit", "full SEO check", "audit my site", "website health check", "comprehensive SEO", "audit example.com".
---

# seo-audit — full-site sweep

The entry point most users want. Crawls, detects, dispatches in parallel, synthesizes a composite report.

---

## When to fire

- "Audit example.com" / "SEO audit on X"
- "Full SEO check" / "comprehensive SEO review"
- "Website health check"
- Periodic re-audit (the user triggers)

Don't fire when:
- Single URL → `page`
- Specific dimension → that specific wrench
- Strategy question → `plan`

---

## Sequence

1. **Crawl.** Up to 500 pages via web-scrape (Firecrawl). Capture HTML, headers, status codes, page metadata.
2. **Detect business type** from signals (per SKILL.md detection table).
3. **Dispatch always-wrenches in parallel** via Agent tool: technical, content, schema, sitemap, images, geo, page (top 10), backlinks.
4. **Dispatch conditional wrenches** if infrastructure ready + business type matches: local, maps, hreflang, ecommerce, programmatic, competitor-pages, dataforseo, google, image-gen.

> **Subagent mapping (verified 2026-06-12):** only lanes with a registered `seo-*` subagent may be dispatched via `Agent(subagent_type=…)`. Registered: `seo-technical, seo-content, seo-schema, seo-sitemap, seo-geo, seo-backlinks, seo-local, seo-maps, seo-ecommerce, seo-dataforseo, seo-google, seo-image-gen, seo-drift, seo-sxo, seo-cluster, seo-performance, seo-visual, seo-flow`. The lanes **`images`, `page`, `hreflang`, `programmatic`, `competitor-pages` have NO dedicated subagent** — run their wrench logic inline (or fold `images`→`seo-visual`, `page`→`seo-sxo`), and never pass a `seo-images`/`seo-page`/`seo-hreflang`/`seo-programmatic`/`seo-competitor-pages` type to the Agent tool (it will error — no such subagent).
5. **Synthesize** per-wrench results into a composite report with health score.
6. **Surface** to the user with prioritized findings.

---

## Output shape

```markdown
## SEO audit — example.com — 2026-05-28

**Pages crawled:** 247
**Business type:** SaaS + Comparison-heavy (vs/alternatives pages detected)
**Composite health score:** 6.8/10

### Per-dimension scores
| Dimension | Score | Critical findings |
|---|---|---|
| Technical | 7.5 | Robots blocks /api/ correctly; 12 pages with slow LCP |
| Content | 6.0 | 23 thin-content pages (< 300 words); E-E-A-T weak on /blog/ |
| Schema | 8.5 | Product + Organization schema present; FAQ schema missing |
| Sitemap | 9.0 | Valid, current, submitted |
| Images | 5.0 | 45% of images missing alt text |
| GEO | 4.5 | No llms.txt; passages not citable; brand mentions weak |
| Backlinks | 7.0 | 247 referring domains; mix is healthy |
| (Competitor pages) | 6.5 | 5 vs pages, schema OK, conversion CTAs weak |

### Top 10 prioritized fixes
1. [HIGH] Add alt text to 45% of images
2. [HIGH] Create llms.txt for AI search visibility
3. [HIGH] Fix LCP on 12 slow pages
4. [HIGH] Address 23 thin-content pages
5. [MEDIUM] Add FAQ schema to relevant pages
6. ...

### What's working well
- ...
```

---

## Cost shape

- Crawl 500 pages: medium (web-scrape Firecrawl)
- 8-17 parallel wrenches dispatched: medium-high
- Synthesis: medium
- Total: significant — full audits are not cheap. Reserve for actual audit needs.

---

## See also

- [SKILL.md](../SKILL.md)
- All other seo wrenches it dispatches
- [`web-scrape/wrenches/crawl.md`](../../web-scrape/wrenches/crawl.md) — crawl primitive
