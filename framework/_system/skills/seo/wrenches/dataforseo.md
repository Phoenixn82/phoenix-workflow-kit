---
name: seo-dataforseo
description: Live SEO data via DataForSEO MCP. SERP analysis (Google / Bing / Yahoo / YouTube / Google Images), keyword research (volume / difficulty / intent / trends), backlink profiles, on-page analysis (Lighthouse / content parsing), competitor analysis, business listings, AI visibility (ChatGPT scraper / LLM mention tracking), domain analytics. Conditional wrench — requires DataForSEO extension installed. Trigger phrases include "dataforseo", "live SERP", "keyword volume", "backlink data", "competitor data", "AI visibility check", "LLM mentions", "image SERP", "real search data".
---

# seo-dataforseo — live SEO data layer

DataForSEO is the comprehensive paid SEO data API. This wrench wraps it via the MCP. When wired, it's the primary data source for SERP / keyword / backlink data across the seo mechanic.

CONDITIONAL: requires DataForSEO MCP extension installed. Without it, other wrenches fall back to free sources (slower, less coverage).

---

## When to fire

- Any SEO work needing live data
- "Live SERP" / "keyword volume" / "backlink data" / "competitor data"
- "AI visibility check" / "LLM mentions"
- "Image SERP rankings"
- Auto-fires when wired + other wrenches need live data

Don't fire when:
- MCP not installed → use free fallbacks via web-scrape
- Single one-off lookup that doesn't justify the cost

---

## What it covers

| Category | Detail |
|---|---|
| **SERP analysis** | Google / Bing / Yahoo / YouTube / Google Images — top N results with snippets |
| **Keyword research** | Search volume, difficulty, intent, trends, related |
| **Backlinks** | Referring domains, anchor text, follow/nofollow, lost links |
| **On-page** | Lighthouse audit, content parsing, technical scan |
| **Competitor analysis** | Their keywords, content, traffic estimates |
| **Business listings** | GBP data, citation health |
| **AI visibility** | Track mentions across ChatGPT, Perplexity, Bing Copilot |
| **Domain analytics** | Traffic estimates, top pages, keyword coverage |

---

## Cost discipline

DataForSEO bills per API call. The wrench:

- Batches requests where possible
- Caches results in second-brain for re-use within the same session
- Surfaces cost estimates BEFORE long-running queries (e.g., "this competitor analysis will cost ~$0.50")
- The user approves expensive queries

---

## See also

- [SKILL.md](../SKILL.md)
- All other seo wrenches that consume this data
- [`printing-press-router`](../../printing-press-router/) — fires first if the user is wiring DataForSEO
