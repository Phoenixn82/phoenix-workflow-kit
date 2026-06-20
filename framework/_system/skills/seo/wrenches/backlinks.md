---
name: seo-backlinks
description: Backlink profile analysis. Referring domains, anchor text distribution, toxic link detection, competitor link gap analysis. Three tiers — free (Moz API limited + Bing Webmaster + Common Crawl) / DataForSEO (full) / paid Ahrefs/Majestic (if the user wires). Trigger phrases include "backlinks", "link profile", "referring domains", "anchor text", "toxic links", "link gap", "link building", "disavow", "backlink audit", "competitor links".
---

# seo-backlinks — link profile analysis

Backlinks remain a top ranking factor. This wrench audits the profile + finds gaps + flags toxic.

---

## When to fire

- "Backlink audit" / "link profile"
- "Toxic links" / "disavow file"
- "Link gap analysis vs competitors"
- "Anchor text distribution"
- Fired as part of `audit` always-set (free tier)

---

## Three data tiers

| Tier | Source | Coverage |
|---|---|---|
| **Free** | Moz API free tier + Bing Webmaster + Common Crawl | Limited but sufficient for direction |
| **DataForSEO** | Backlinks API | Comprehensive |
| **Paid (Ahrefs / Majestic)** | If the user wires API key | Industry-leading depth |

---

## Dimensions

| Dimension | What |
|---|---|
| **Referring domains** | Count, distribution by quality |
| **Anchor text** | Distribution: branded / generic / exact-match / partial / naked URL |
| **Link velocity** | New links per month trend |
| **Top linking content** | Which pages on the site earn most links |
| **Toxic links** | Spammy, low-quality, link-scheme patterns |
| **Link gap** | Domains linking to competitors but not to us |
| **Lost links** | Previously linking, now removed (recoverable?) |

---

## Anchor text health

Healthy distribution roughly:
- Branded: 40-60%
- Generic ("click here", "read more"): 10-20%
- Naked URL: 10-15%
- Partial match (topic words): 10-20%
- Exact match: < 5% (over-optimization risk)

Imbalanced distribution (especially > 20% exact match) is a red flag.

---

## Toxic link detection

Flagged as toxic:
- Sites with very low DA + spammy content
- Sites with sudden link explosion patterns
- Sites with foreign language unrelated to ours
- Sites Google has previously penalized
- Link schemes / PBNs / private blog networks

The wrench generates a disavow file candidate (the user reviews before submitting).

---

## Link gap analysis

For 3-5 competitors:
- Crawl their backlink profile
- Find domains linking to them but not to us
- Filter to high-quality, relevant
- Rank by potential value

Output: outreach target list.

---

## See also

- [SKILL.md](../SKILL.md)
- [dataforseo.md](dataforseo.md) — full backlink data
- [competitor-pages.md](competitor-pages.md) — different lane (your pages vs theirs)
