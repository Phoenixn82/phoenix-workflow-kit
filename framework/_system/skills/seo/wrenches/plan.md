---
name: seo-plan
description: Strategic SEO planning. Industry-specific templates, competitive analysis, content strategy, implementation roadmap. For new sites or existing sites pivoting strategy. Trigger phrases include "SEO plan", "SEO strategy", "content strategy", "keyword strategy", "content calendar", "site architecture", "SEO roadmap", "build an SEO plan".
---

# seo-plan — strategy + roadmap

Different from `audit` (analyzes current state). `plan` proposes a forward-looking strategy + roadmap.

---

## When to fire

- "SEO plan" / "SEO strategy"
- "Content strategy for [project]"
- "Site architecture for SEO"
- "Where should we focus first"

Don't fire when:
- Site already has a strategy and just needs analysis (audit)
- Single content piece (content-forge for production)

---

## Industry templates

The wrench has templates for:
- SaaS
- E-commerce
- Local business
- Publisher / media
- Agency
- B2B services
- Educational
- Programmatic (pages-at-scale)

Each template includes typical keyword pools, content patterns, link-building priorities, technical priorities, and metrics.

---

## Sequence

1. Detect business type + current state (if existing site, scan)
2. Pull industry template
3. Run competitive analysis: top 5-10 competitors, their content patterns, their keyword targets
4. Define keyword pillars (3-7 main pillars + cluster topics under each)
5. Site architecture proposal (hub-and-spoke if cluster strategy)
6. Content calendar template (3 months out)
7. Technical priorities (what to fix first)
8. Link priorities (what to target)
9. Metrics + review cadence

---

## Output shape

```markdown
## SEO plan — <project>

### Business type
SaaS — developer-tools subcategory

### Keyword pillars
1. <pillar 1>: <reasoning + cluster topics>
2. <pillar 2>: ...
3. ...

### Competitive analysis
- <competitor 1>: ranks for X, content pattern Y, gap: Z
- ...

### Site architecture proposal
[hub-and-spoke or category-based with diagram]

### Content calendar (next 90 days)
- Week 1-2: <topic>
- Week 3-4: <topic>
- ...

### Technical priorities (first 30 days)
1. <fix 1>
2. <fix 2>
...

### Link priorities
- <target 1>
- <target 2>

### Metrics + cadence
- Track: <metrics>
- Review: monthly via `drift` wrench
```

---

## See also

- [SKILL.md](../SKILL.md)
- [cluster.md](cluster.md) — implementation of hub-and-spoke
- [audit.md](audit.md) — checks current state first
- [drift.md](drift.md) — monthly review tool
