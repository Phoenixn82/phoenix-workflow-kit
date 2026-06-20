---
name: seo-schema
description: Schema.org structured data wrench. Detect, validate, generate JSON-LD. Trigger phrases include "schema", "structured data", "rich results", "JSON-LD", "markup", "Schema.org", "FAQ schema", "Product schema", "Article schema".
---

# seo-schema — JSON-LD detect / validate / generate

Structured data is how search engines understand the page beyond words. This wrench handles detection (what's there), validation (is it valid), and generation (write what's missing).

---

## When to fire

- "Schema for this page" / "JSON-LD"
- "Rich results" / "markup"
- "Generate Product schema" / "Article schema"
- Fired as part of `audit` always-set

Don't fire when:
- Generic SEO question (other wrenches)

---

## Common schema types per page

| Page type | Schema |
|---|---|
| Homepage | Organization, WebSite (with SearchAction) |
| Article | Article (or BlogPosting), Person (author), Organization (publisher) |
| Product | Product, Offer, AggregateRating, Review |
| FAQ | FAQPage |
| How-to | HowTo |
| Recipe | Recipe |
| Event | Event |
| Local business | LocalBusiness (subtype), Place |
| Job posting | JobPosting |
| Software | SoftwareApplication |
| Course | Course |
| Video | VideoObject |

---

## Sequence

1. Crawl pages
2. Per page, extract JSON-LD blocks
3. Validate each against Schema.org + Google rich results requirements
4. Detect MISSING schema based on page type (e.g., Article page without Article schema)
5. Generate suggested JSON-LD for missing
6. Codex writes the final JSON-LD blocks to source if the user approves (hard rule #5)

---

## Validation

- Required fields present?
- Field types correct?
- @context = "https://schema.org"
- @type valid for the page
- Cross-references resolve (image URLs, sameAs URLs)
- Date formats ISO 8601
- Price formats valid

---

## Output shape

```markdown
## Schema audit — example.com

### Coverage
- 247 pages crawled
- 198 with schema (80%)
- 49 without schema

### By type
- Organization: 1 (homepage, valid)
- Article: 87 (correct page type, valid)
- Product: 45 (correct, valid)
- FAQPage: 0 (FIX: 12 FAQ pages without schema)

### Validation errors
- /products/widget-x: Product schema missing `aggregateRating` despite reviews shown
- /blog/...: Article schema missing `author.url`

### Recommendations
1. Add FAQPage schema to 12 FAQ pages
2. Fix Product aggregateRating on /products/widget-x
3. Add Person schema for top 5 authors
```

---

## Codex writes the final files

When the user approves the generated JSON-LD, dispatch via `router` to Codex for the actual source file writes.

---

## See also

- [SKILL.md](../SKILL.md)
- [page.md](page.md) — single-URL schema check
- [`AGENTS.md`](../../../../AGENTS.md) — hard rule #5 (Codex writes deliverables)
- [ecommerce.md](ecommerce.md) — Product schema deep dive
