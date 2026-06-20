---
name: seo-maps
description: Maps intelligence. Geo-grid rank tracking, Share of Local Voice (SoLV), GBP profile audit via API, review intelligence across Google / Tripadvisor / Trustpilot, cross-platform NAP verification (Google / Bing / Apple / OSM), competitor radius mapping, LocalBusiness schema generation from API data. Three-tier capability — free (Overpass + Geoapify) / DataForSEO (full) / DataForSEO + Google Maps (max coverage). Trigger phrases include "maps", "geo-grid", "rank tracking", "GBP audit", "review velocity", "competitor radius", "maps analysis", "local rank tracking", "Share of Local Voice", "SoLV".
---

# seo-maps — local maps intelligence

Deeper than `local` — uses API data (DataForSEO or free fallbacks) to track local rankings on a geographic grid, audit competitors in the radius, and aggregate review intelligence across platforms.

---

## When to fire

- Local business + need for rank data
- "Geo-grid rank tracking" / "Share of Local Voice"
- "Competitor radius mapping"
- "Cross-platform NAP" verification

Don't fire when:
- Basic local audit → `local` instead
- No physical presence (not local)

---

## Three tiers

| Tier | Capability | Cost |
|---|---|---|
| **Tier 1 — Free** | Overpass (OSM data) + Geoapify | Free |
| **Tier 2 — DataForSEO** | Full geo-grid rank tracking, review aggregation, competitor data | DataForSEO MCP |
| **Tier 3 — DataForSEO + Google Maps** | Max coverage, real-time GBP data | Both extensions wired |

The wrench detects which is available and uses the highest tier.

---

## What it does

| Capability | How |
|---|---|
| **Geo-grid rank tracking** | Grid of N×M points across service area; query rank at each; visualize SoLV |
| **GBP profile audit** | Via DataForSEO Maps API: completeness, attributes, posts, photos, hours |
| **Review intelligence** | Aggregate reviews across Google / Yelp / Tripadvisor / Trustpilot: sentiment, recency, response rate |
| **Cross-platform NAP** | Compare NAP across Google / Bing / Apple Maps / OSM |
| **Competitor radius mapping** | Within N-mile radius: who's competing, their ratings, their rankings |
| **Schema generation** | LocalBusiness JSON-LD with all the right fields populated from API data |

---

## Geo-grid output

```
Grid: 5×5 points centered on (lat, lng) at 0.5-mile spacing
Keyword: "best pizza near me"

       W      W-C    C      C-E    E
N    rank-3  rank-2 rank-1 rank-2 rank-4
N-C  rank-4  rank-2 rank-1 rank-3 rank-5
C    rank-5  rank-3 rank-1 rank-2 rank-3
C-S  rank-7  rank-4 rank-2 rank-3 rank-6
S    rank-12 rank-6 rank-3 rank-5 rank-9

SoLV: 68% (weighted by query volume per grid cell)
```

---

## See also

- [SKILL.md](../SKILL.md)
- [local.md](local.md) — broader local SEO
- [dataforseo.md](dataforseo.md) — primary data source
- [schema.md](schema.md) — LocalBusiness schema integration
