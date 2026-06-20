---
name: seo-sitemap
description: XML sitemap analysis + generation. Validates format, URLs, lastmod dates, priority hints. Generates new sitemaps with industry-specific templates. Trigger phrases include "sitemap", "generate sitemap", "sitemap issues", "XML sitemap", "sitemap.xml", "submit sitemap".
---

# seo-sitemap — XML sitemap validate / generate

Sitemaps tell search engines what to crawl. This wrench validates existing ones and generates new ones.

---

## When to fire

- "Sitemap audit" / "sitemap issues"
- "Generate sitemap"
- "Submit sitemap"
- Fired as part of `audit` always-set

Don't fire when:
- robots.txt audit → `technical`
- URL discovery → web-scrape/map

---

## Sitemap types

| Type | Use |
|---|---|
| **Standard XML** | One file, < 50K URLs, < 50MB |
| **Sitemap index** | Multiple sub-sitemaps when site exceeds limits |
| **Image sitemap** | Image URLs (or via extensions in main sitemap) |
| **Video sitemap** | Video URLs with metadata |
| **News sitemap** | News articles (last 48 hours) |

---

## Validation

- Valid XML
- < 50K URLs per file
- < 50MB uncompressed
- Each URL: absolute, on this domain, no nofollow
- lastmod dates ISO 8601
- changefreq / priority valid (or absent — both fine)
- Referenced in robots.txt
- Submitted to Search Console (if `google` wrench wired)

---

## Generation

For projects without a sitemap (or with a stale one):

1. Crawl site for URLs
2. Filter: only canonical, indexable URLs
3. Group by section if large (index + sub-sitemaps)
4. Add lastmod from git commit dates or page metadata
5. Output to project's expected sitemap path
6. Codex writes the file (hard rule #5) and updates robots.txt if needed

---

## Industry templates

| Industry | Sitemap structure |
|---|---|
| E-commerce | Index → products / categories / brand / blog sub-sitemaps |
| Publisher | Index → articles by date / sections / authors |
| SaaS | Single sitemap with feature pages, blog, docs |
| Local multi-location | Index → per-location sub-sitemaps |
| Programmatic | Index → templated-page sub-sitemaps by category |

---

## Output shape

```markdown
## Sitemap audit — example.com

### Current state
- 1 sitemap at /sitemap.xml
- 247 URLs
- Last modified: 2026-05-20
- Submitted to GSC: yes

### Validation
- All URLs canonical: yes
- All URLs return 200: 245 of 247 (2 are 404 — FIX)
- lastmod dates present: 90%
- Image extensions used: no

### Recommendations
- Remove 2 dead URLs
- Add image:image extensions for product pages
- Add lastmod to 10% missing
```

---

## See also

- [SKILL.md](../SKILL.md)
- [technical.md](technical.md) — robots.txt + indexability
- [`AGENTS.md`](../../../../AGENTS.md) — hard rule #5 (Codex writes the sitemap file)
