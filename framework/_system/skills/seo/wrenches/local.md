---
name: seo-local
description: Local SEO. Google Business Profile optimization, NAP consistency across citations, review signals, local schema (LocalBusiness + subtype), location page quality, multi-location SEO, industry-vertical specifics (restaurant / healthcare / legal / home services / real estate / automotive). Trigger phrases include "local SEO", "Google Business Profile", "GBP", "map pack", "local pack", "citations", "NAP consistency", "local rankings", "service area", "multi-location", "local search".
---

# seo-local — local SEO

For brick-and-mortar, service-area businesses (SAB), and multi-location operations. Different game than classic SEO — local pack rankings + GBP optimization + citation hygiene matter as much as on-page.

---

## When to fire

- Local business detected during audit
- "Local SEO" / "GBP" / "map pack"
- "Citations" / "NAP consistency"
- "Service area" / "multi-location"

Don't fire when:
- Pure online business (no physical / service area)
- Pure ecommerce shipping nationally (use ecommerce wrench)

---

## Business type detection (local sub-types)

| Type | Examples |
|---|---|
| **Brick-and-mortar single** | Single physical store |
| **Brick-and-mortar multi** | Chain or multi-location |
| **Service area business (SAB)** | Visits customers (plumber, mobile mechanic) |
| **Hybrid** | Both physical location AND service area |

Industry verticals adjust focus: restaurant (Google reviews crucial), legal (E-E-A-T strict), healthcare (HIPAA + YMYL), home services (citations + reviews), real estate (listings + agents), automotive (inventory + reviews).

---

## What gets checked

| Dimension | What |
|---|---|
| **GBP completeness** | Name / address / phone / website / hours / categories / photos / posts / services |
| **GBP optimization** | Primary category accuracy, attributes filled, Q&A used, posts recent |
| **NAP consistency** | Name / Address / Phone identical across GBP, citations, website footer |
| **Local schema** | LocalBusiness schema (with subtype matching business — Restaurant / Dentist / LegalService / etc.) |
| **Location pages** | Per-location pages with unique content (multi-location), embedded map, reviews |
| **Review signals** | Volume, recency, rating, response rate |
| **Citation health** | Listed in core directories (Yelp, BBB, industry-specific), NAP consistent across all |
| **Content** | Locally-relevant content (neighborhood guides, local events, service-area-specific) |

---

## Sequence

1. Detect local sub-type
2. Pull GBP data (via maps wrench if DataForSEO wired; manual otherwise)
3. Scan website for NAP, schema, location pages
4. Check core citation directories (top 20 for industry vertical)
5. Sample reviews across platforms (Google, Yelp, industry-specific)
6. Compile findings + prioritized fixes

---

## Output shape

```markdown
## Local SEO — example.com

**Business type:** Brick-and-mortar single, restaurant
**Composite score:** 6.5/10

### GBP — 7/10
- Completeness: 85%
- Categories: primary correct, secondary missing
- Photos: 23 (good), no posts in 60 days

### NAP consistency — 8/10
- GBP / website / Yelp all match
- 2 outdated old addresses on minor directories

### Local schema — 5/10
- LocalBusiness present but using generic; should use Restaurant subtype
- Missing: openingHoursSpecification, servesCuisine, menu URL

### Reviews — 7/10
- Google: 4.6 stars (124 reviews)
- Yelp: 4.0 stars (67 reviews)
- Response rate: 35% (FIX — aim for 80%+)
- Recency: 12 reviews in last 30 days (healthy)

### Top 10 priority fixes
1. [HIGH] Switch LocalBusiness schema to Restaurant subtype + add menu
2. [HIGH] Increase review response rate to 80%
3. [HIGH] Fix 2 outdated addresses on minor directories
4. [MEDIUM] Resume GBP posts (weekly cadence)
```

---

## See also

- [SKILL.md](../SKILL.md)
- [maps.md](maps.md) — geo-grid rank tracking + review intelligence
- [schema.md](schema.md) — LocalBusiness + subtype JSON-LD
- [dataforseo.md](dataforseo.md) — GBP profile audit via API
