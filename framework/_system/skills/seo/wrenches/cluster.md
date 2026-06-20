---
name: seo-cluster
description: SERP-based semantic topic clustering. Groups keywords by actual Google SERP overlap (not text similarity), designs hub-and-spoke content clusters with internal link matrices, generates interactive visualizations. Trigger phrases include "topic cluster", "content cluster", "semantic clustering", "pillar page", "hub and spoke", "content architecture", "keyword grouping", "cluster plan".
---

# seo-cluster — SERP-based topic clustering

Topic clusters built from actual SERP overlap, not text similarity. If two keywords share top-10 results, they belong in the same cluster (Google sees them as related). This is more accurate than text-similarity clustering.

---

## When to fire

- "Topic cluster" / "content cluster"
- "Pillar page strategy"
- "Hub and spoke architecture"
- After `plan` when content strategy needs cluster structure

Don't fire when:
- Single-page question
- Already-clustered site (audit instead)

---

## Sequence

1. **Seed keywords.** the user provides 10-50 seeds, or wrench expands from a single topic.
2. **SERP fetch.** For each keyword, get top 10 ranking URLs (via DataForSEO if wired, else web-scrape).
3. **Pairwise SERP overlap.** For every pair of keywords, count shared URLs in top 10. Threshold (e.g., 3+ shared) = related.
4. **Cluster.** Group keywords by overlap graph.
5. **Intent classification.** Per cluster, classify dominant intent (informational / transactional / navigational).
6. **Hub-and-spoke design.** One pillar page per cluster covering the topic broadly; spoke pages target specific keywords with depth.
7. **Internal link matrix.** Pillar → spokes (always), spokes → pillar (always), spokes → related spokes (selective).
8. **Visualization.** Generate interactive cluster graph HTML.

---

## Output shape

```markdown
## Topic cluster plan

### Cluster 1: "Self-hosted databases"
**Pillar page:** /self-hosted-databases (covering the broad topic)
**Spokes:**
- /self-hosted-postgres-guide → "self-hosted postgres"
- /self-hosted-mysql-guide → "self-hosted mysql"
- /comparing-self-hosted-vs-managed → "self-hosted vs managed"

**Internal links:**
- pillar ↔ each spoke
- self-hosted-postgres-guide → comparing (related)
- ...

**Intent:** informational (educational)
**Search volume:** 2,400/mo across cluster
**Difficulty:** medium

### Cluster 2: ...
```

---

## See also

- [SKILL.md](../SKILL.md)
- [plan.md](plan.md) — broader strategy (cluster fits within)
- [dataforseo.md](dataforseo.md) — SERP data source
- [`web-scrape/wrenches/search.md`](../../web-scrape/wrenches/search.md) — SERP fallback when DataForSEO unavailable
