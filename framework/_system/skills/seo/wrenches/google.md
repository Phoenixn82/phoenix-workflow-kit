---
name: seo-google
description: Google SEO APIs. Search Console (Search Analytics / URL Inspection / Sitemaps), PageSpeed Insights v5, CrUX field data with 25-week history, Indexing API v3, GA4 organic traffic. Conditional wrench — requires the user's API credentials wired. Trigger phrases include "search console", "GSC", "PageSpeed", "CrUX", "field data", "indexing API", "GA4 organic", "URL inspection", "impressions", "clicks", "CTR", "position data", "LCP field", "INP field", "Lighthouse scores".
---

# seo-google — Google's official APIs

When you have a verified site in Search Console, Google offers the most accurate data. This wrench wraps GSC, PSI, CrUX, Indexing API, and GA4.

CONDITIONAL: requires the user's API credentials wired in his harness env (GSC OAuth, GA4 service account, PageSpeed API key, etc.). If not available, surface "wire X creds to enable" and use free fallbacks.

---

## When to fire

- "Search Console data" / "GSC report"
- "PageSpeed Insights" / "Lighthouse score"
- "CrUX field data" / "real LCP"
- "Submit URL for indexing" (Indexing API)
- "GA4 organic traffic"

Don't fire when:
- Credentials not wired → push back to setup
- Lab data sufficient → `technical` runs PSI lab without GSC

---

## API capabilities

### Search Console
- Search Analytics (impressions / clicks / CTR / position by query / page / country / device)
- URL Inspection (indexed / discovered / mobile usability)
- Sitemaps (submit / status)

### PageSpeed Insights v5
- Lighthouse lab data per URL
- Performance / Accessibility / Best Practices / SEO scores

### CrUX
- Real user field data (LCP / INP / CLS / FCP / TTFB)
- 25-week history for trend analysis

### Indexing API v3
- Submit URLs for indexing
- Currently only for Job Posting + BroadcastEvent per Google's guidance, but useful for those

### GA4 Data API
- Organic search sessions
- Conversion rates by source
- Page-level engagement

---

## Setup checklist

```
1. Google Cloud project with APIs enabled
2. OAuth credentials for Search Console (per the user account)
3. Service account for GA4 (if multi-site)
4. PageSpeed API key (free tier sufficient for most)
5. Save creds to ~/.claude/seo/google-creds.json (gitignored)
```

If creds aren't set up, the wrench guides the user through OAuth one-time.

---

## See also

- [SKILL.md](../SKILL.md)
- [technical.md](technical.md) — lab CWV (no API needed)
- [dataforseo.md](dataforseo.md) — alternative for SERP / volume data
- [`printing-press-router`](../../printing-press-router/) — CLI > API > MCP ladder for new integrations
