---
name: web-scrape-map
description: URL discovery wrench. Returns a list of URLs on a domain without extracting their content. Use when the question is "what pages are on this site" or "find the URL for X on Y.com" — when you need the URL but not the body. Cheap discovery step before crawl, or shortcut to find a specific page without crawling the whole site. Trigger phrases include "map this site", "list URLs on", "what's the URL for X", "find the page about Y", "site structure".
---

# web-scrape-map — URL discovery only

A list of URLs, no content. The cheapest way to answer "does this site have a page about X" or "what's the URL for the pricing page" or "show me everything under /docs".

This is the wrench that prevents over-crawling. If the user wants one specific page from a large site, mapping first and then scraping the one URL beats crawling the whole site.

---

## When to fire

- "What pages are on this site"
- "Find the URL for the pricing page on \<site\>"
- "Map this site"
- "Site structure for X"
- "Where's the changelog on \<site\>"
- Pre-crawl reconnaissance: "before we crawl, let me see what's there"

Don't fire when:
- You want the content of those URLs → use `crawl` directly (map + crawl is 2 calls when crawl alone is 1)
- You want one specific known URL → use `scrape`
- The site is small (under ~20 pages) and you want everything → use `crawl` directly

---

## CLI patterns

```bash
# Default: list all discoverable URLs
firecrawl map "<domain>"

# Search-filtered (only URLs matching a query)
firecrawl map "<domain>" --search "pricing"
firecrawl map "<domain>" --search "changelog OR release notes"

# Path filtering: map has NO --include/--exclude. Filter with --search (matches path + content),
# then post-filter the returned URL list yourself for exact path globs.
firecrawl map "<domain>" --search "docs"

# Include subdomains in discovery
firecrawl map "<domain>" --include-subdomains

# Limit result count
firecrawl map "<domain>" --limit 100

# Output to file for downstream consumption
firecrawl map "<domain>" --output urls.txt
```

The `--search` flag is the killer feature — semantic filter without crawling. "Find the pricing page" becomes one call instead of crawl-and-grep.

---

## Cost shape

- Single Firecrawl call, very cheap (~$0.005 equivalent)
- Returns URLs only, no markdown extraction
- Pre-filtering with `--search` doesn't change cost — Firecrawl filters server-side

---

## Output handling

Returns a JSON or newline-delimited list of URLs. Typical shapes:

```
firecrawl map "example.com" --search "pricing"
→ ["https://example.com/pricing", "https://example.com/enterprise/pricing", ...]

firecrawl map "docs.example.com" --search "api"
→ ["https://docs.example.com/api/auth", "https://docs.example.com/api/users", ...]
```

Common downstream uses:
- Feed into `scrape` for the specific URLs that matter
- Feed into `crawl` with `--seeds <urls.txt>` for bulk extract of just those URLs
- Save to second-brain as a site reference

---

## Escalation signals

Map rarely needs escalation. If it returns sparse results:

1. **Site has no sitemap.xml and few internal links** — map has nothing to traverse. Try `crawl` with shallow depth to discover URLs by following links.
2. **JavaScript-rendered routes** — single-page apps with client-side routing may not expose URLs to map. Try `crawl` with JS rendering, or `interact` to enumerate routes manually.
3. **Auth-walled site** — map can't see behind login. Escalate to `interact` with session held.

---

## Pairing patterns

- **`map --search "X"` → `scrape` the one matching URL** is the fastest "find me the page about X" pattern
- **`map --search "docs"` → `crawl --include-paths "/docs/*"`** (or scrape the mapped URLs individually) when you want bulk extract of a specific subset
- **`map` → review with the user → decide which URLs matter** before any extraction. Useful when the site is large and the ask is loose.

---

## See also

- [SKILL.md](../SKILL.md) — mechanic entry
- [scrape.md](scrape.md) — extract one URL after map locates it
- [crawl.md](crawl.md) — bulk extract many URLs; can take map output as seeds
- [interact.md](interact.md) — escalation for auth-walled or JS-routed sites
