---
name: seo-content
description: Content quality + E-E-A-T audit. AI citation readiness, readability, depth, thin content detection. Per-page scoring. Trigger phrases include "content quality", "E-E-A-T", "content analysis", "readability check", "thin content", "content audit", "content depth", "AI citation ready".
---

# seo-content — content quality + E-E-A-T

Content is half of SEO. This wrench audits depth, E-E-A-T signals, readability, and AI-citation readiness.

---

## When to fire

- "Content quality audit"
- "E-E-A-T"
- "Find thin content"
- "Is this AI-citation ready"
- Fired as part of `audit` always-set

Don't fire when:
- Content production needed → `content-forge`
- Single URL → `page`

---

## E-E-A-T dimensions

| Dimension | What |
|---|---|
| **Experience** | First-hand evidence, photos, anecdotes, dates, specifics |
| **Expertise** | Author credentials, citations, technical accuracy |
| **Authoritativeness** | Backlinks, mentions, author rep, domain rep |
| **Trustworthiness** | Contact info, about page, privacy policy, ToS, business info |

For YMYL (Your Money or Your Life) topics — health, finance, legal — bar is higher across all 4.

---

## Quality dimensions

| Dimension | Checks |
|---|---|
| **Depth** | Word count + topic coverage vs SERP top 10 |
| **Readability** | Grade level (target 8-10 for general audience), sentence variety |
| **Structure** | Headings, scannable, bullets / lists where appropriate |
| **Original value** | Not just rehash of competitors — unique angle / data / experience |
| **AI-citation ready** | Direct answers near the top, structured Q&A, clear claims that can be quoted |
| **Internal linking** | Linked to relevant other pages, anchor variety |
| **Freshness** | Last updated date, recent enough for topic |

---

## Thin content detection

Pages flagged as thin:
- Under 300 words main content
- Heavily templated with little unique content
- Auto-generated descriptions
- Doorway pages targeting close-variant keywords
- Index pages with no unique value

These need either: expansion, consolidation with siblings, or noindex.

---

## Sequence

1. Crawl sitewide (or use audit's output)
2. Per page: word count, headings, readability, content uniqueness fingerprint
3. Per page: E-E-A-T signal check (author presence, citations, contact, etc.)
4. Per page: AI-citation readiness score (structured answers, Q&A, claims-quotability)
5. SERP comparison for top-priority pages (depth vs top 10 ranking pages)
6. Flag thin content + recommend action

---

## Output shape

```markdown
## Content audit — example.com

**Composite:** 6.0/10

### E-E-A-T overall — 6.5/10
- Experience: weak (no first-hand anecdotes on most pages)
- Expertise: medium (author bylines present, credentials missing)
- Authoritativeness: medium (some backlinks, no industry mentions)
- Trust: strong (about page, contact, policies all present)

### Quality patterns
- Average word count (main content): 847 words
- Average readability: grade 11 (target 8-10 for this audience)
- AI-citation readiness: weak — answers buried in prose, not structured

### Thin content
- 23 pages under 300 words → list at `$env:TEMP\seo-thin-content.md`
- Recommended action: 8 expand, 12 consolidate, 3 noindex

### Top 10 priority fixes
1. [HIGH] Add author bio + credentials sitewide
2. [HIGH] Restructure top 20 pages: lead with direct answer
3. [HIGH] Consolidate 12 thin pages into hub pages
4. ...
```

---

## See also

- [SKILL.md](../SKILL.md)
- [page.md](page.md) — single-URL content check
- [geo.md](geo.md) — AI-citation focus
- [`content-forge/SKILL.md`](../../content-forge/SKILL.md) — production lane
