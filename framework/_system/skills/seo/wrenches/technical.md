---
name: seo-technical
description: Technical SEO audit. 9 categories — crawlability, indexability, security, URL structure, mobile, Core Web Vitals (LCP / INP / CLS / FCP / TTFB), structured data, JavaScript rendering, IndexNow protocol. Trigger phrases include "technical SEO", "crawl issues", "robots.txt", "Core Web Vitals", "site speed", "security headers", "indexability", "mobile SEO".
---

# seo-technical — technical SEO audit

Technical foundations. If technical is broken, content doesn't matter.

---

## When to fire

- "Technical SEO audit"
- "Crawl issues" / "robots.txt"
- "Core Web Vitals" / "page speed"
- "Mobile SEO" / "is the site mobile-friendly"
- "Security headers"
- Fired as part of `audit` always-set

Don't fire when:
- Single URL → `page`
- Content quality → `content`

---

## 9 categories

| Category | Checks |
|---|---|
| **Crawlability** | robots.txt, sitemap referenced, crawl budget waste, blocked critical paths |
| **Indexability** | noindex audit, canonical errors, duplicate content, parameter URLs |
| **Security** | HTTPS, HSTS, mixed content, CSP, X-Frame-Options |
| **URL structure** | Clean URLs, parameter handling, trailing slash consistency, lowercase |
| **Mobile** | Viewport meta, responsive layout, touch targets, font size, mobile-first signals |
| **Core Web Vitals** | LCP / INP / CLS / FCP / TTFB (from PSI lab; CrUX field via `google` wrench if available) |
| **Structured data** | JSON-LD presence (handoff to `schema` wrench for details) |
| **JavaScript rendering** | Client-side vs server-side, hydration timing, content visible without JS |
| **IndexNow** | Endpoint configured, sending notifications, accepted by Bing |

---

## Sequence

1. Crawl sitewide (or use audit's crawl output)
2. Run each category sequentially (some depend on prior — e.g., indexability depends on crawlability)
3. Test live URLs via chrome-devtools-mcp for JS rendering + CWV ($0 API cost but token-expensive — use for a handful of URLs only, per AGENTS.md hard rule #6)
4. If `google` wrench ready, pull CrUX field data
5. Compile findings sorted by severity

---

## Output shape

```markdown
## Technical SEO — example.com

**Composite:** 7.5/10

### Crawlability — 8/10
- robots.txt: present, blocks /api/ correctly, sitemap referenced
- Crawl waste: ~5% of crawl budget on parameter URLs (FIX)

### Indexability — 7/10
- 247 indexable pages, 12 noindex (intentional)
- 3 duplicate-content clusters detected

### Security — 9/10
- HTTPS enforced, HSTS present, no mixed content
- Missing: CSP, X-Frame-Options

### URL structure — 8/10
- Clean URLs, lowercase, trailing slash inconsistent

### Mobile — 7/10
- Viewport meta present
- 4 pages with touch targets under 44px

### Core Web Vitals — 6/10
- LCP: 2.8s (needs improvement)
- INP: 220ms (needs improvement)
- CLS: 0.06 (good)

### Structured data — see schema wrench
### JS rendering — content visible without JS (good)
### IndexNow — configured, sending

### Top fixes
1. [HIGH] Block parameter URLs in robots.txt or canonicalize
2. [HIGH] Fix LCP on slow pages (image optimization, lazy load below fold)
3. [MEDIUM] Add CSP + X-Frame-Options headers
4. [MEDIUM] Fix touch targets on 4 pages
```

---

## See also

- [SKILL.md](../SKILL.md)
- [schema.md](schema.md) — structured data deep dive
- [google.md](google.md) — CrUX field data
- [sitemap.md](sitemap.md) — sitemap analysis
