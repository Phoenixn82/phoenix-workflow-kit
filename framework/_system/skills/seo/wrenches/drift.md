---
name: seo-drift
description: SEO drift monitoring. Captures baselines of SEO-critical elements, detects changes, tracks regressions over time. Git for SEO — baseline, diff, track changes to on-page SEO. Trigger phrases include "SEO drift", "baseline", "track changes", "did anything break", "SEO regression", "compare SEO", "before and after", "monitor SEO changes", "deployment check", "SEO snapshot".
---

# seo-drift — SEO regression monitoring

Like git for SEO. Capture a baseline of SEO-critical elements; later, run a diff to surface changes. Catches accidental drift after deploys.

Per AGENTS.md hard rule #1, this runs on-demand — not on a schedule.

---

## When to fire

- After every significant deploy (the user triggers)
- "Did SEO change after the deploy"
- "Baseline this site"
- "SEO regression check"

Don't fire when:
- No prior baseline + nothing to compare → just capture baseline
- Continuous monitoring wanted → push back per hard rule #1

---

## What gets baselined per page

| Element | Why track |
|---|---|
| Title tag | Common accidental change |
| Meta description | Same |
| H1 | Same |
| Canonical | Critical |
| Robots meta | Accidental noindex is a disaster |
| Schema JSON-LD | Schema regression silently kills rich results |
| Internal links to/from | Architecture drift |
| Word count | Content removal |
| Image alt text count | Accessibility regression |
| Hreflang tags | International regression |
| Open Graph tags | Social regression |

Sitewide: robots.txt, sitemap.xml, .htaccess / redirects.

---

## Sequence

1. **Baseline mode.** Crawl + extract all tracked elements per page. Save to `_system/second-brain/Actions/seo-baselines/<project>/<date>.json`.
2. **Diff mode.** Crawl current state + load latest baseline + diff per page + per element.
3. **Surface differences.** Sorted by severity (noindex / canonical changes = HIGH; word count drop > 30% = HIGH; title change = MEDIUM; etc.).
4. **the user decides.** Was the change intentional or a regression?

---

## Output shape

```markdown
## SEO drift report — example.com

**Baseline:** 2026-05-15 (commit abc1234)
**Current:** 2026-05-28 (commit def5678)
**Pages compared:** 247

### Critical changes (HIGH)
- /products/widget-x: canonical changed from /products/widget-x to /products/widget (likely intentional?)
- /blog/old-post: now has noindex meta (intentional?)

### Moderate changes (MEDIUM)
- 12 pages: title tag changed (list)
- 8 pages: schema JSON-LD changed (list)

### Minor changes (LOW)
- 23 pages: meta description tweaked
- 47 pages: word count changed by < 10%

### Status
The user: review HIGH first, approve / flag regressions
```

---

## Baseline storage

JSON per page per baseline date. Multiple baselines accumulate; the wrench compares against latest by default, or specified date.

```
_system/second-brain/Actions/seo-baselines/
  <project>/
    2026-05-15.json
    2026-05-22.json
    2026-05-28.json
```

---

## See also

- [SKILL.md](../SKILL.md)
- [audit.md](audit.md) — broader (drift is regression-focused)
- [`AGENTS.md`](../../../../AGENTS.md) — hard rule #1
- [`ship/wrenches/canary.md`](../../ship/wrenches/canary.md) — post-deploy parallel — drift can run here
