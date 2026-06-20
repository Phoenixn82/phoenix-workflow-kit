---
name: web-scrape-crawl
description: Bulk multi-page Firecrawl extraction. Crawls a site or subsection and returns all page results as one JSON payload (stdout or --output file). Supports depth limits (--max-depth/--limit), path filters (--include-paths/--exclude-paths), and concurrency (--max-concurrency). Use when the ask is "crawl this site", "extract all pages from /docs", "bulk scrape", "get every product page", or any multi-page same-domain extraction.
---

# web-scrape-crawl — bulk multi-page extraction

When you want N pages from one domain, this is the wrench. Crawl is one Firecrawl job that returns N markdown blobs — not N scrape calls. Cheaper, faster, and one place to set depth/path filters.

Crawl returns the pages as JSON (write it with `--output crawl.json`). For per-page files on disk, parse that JSON or `scrape` the individual URLs — the installed CLI has no `--write-files`.

---

## When to fire

- "Crawl this site" / "crawl X"
- "Get all pages from \<site\>" / "extract every page under /docs"
- "Download these docs for offline reading"
- "Bulk scrape" / "pull all the product pages"
- "Save \<site\> as local markdown files"
- Building a RAG corpus from a docs site (chain with `rag-architect`)
- Building seed data for a project (chain with `build`)

Don't fire when:
- Single URL → use `scrape`
- You don't know which URLs you want → `map` first to scope, then crawl with seeds
- Pages require interaction (login, click, paginate) → use `interact` per page or `agent` for structured extract

---

## CLI patterns

```bash
# Default: crawl from seed URL, follow internal links
firecrawl crawl "<seed-url>"

# Depth-limited (don't go deeper than N hops from seed)
firecrawl crawl "<seed-url>" --max-depth 2

# Page-count-limited
firecrawl crawl "<seed-url>" --limit 50

# Path filter (only crawl URLs matching)  — real flags are --include-paths / --exclude-paths
firecrawl crawl "<seed-url>" --include-paths "/docs/*"
firecrawl crawl "<seed-url>" --exclude-paths "/blog/*,/tag/*"

# Concurrent extraction speed  (real flag is --max-concurrency, not --concurrency)
firecrawl crawl "<seed-url>" --max-concurrency 5

# Output as one consolidated JSON (crawl emits structured JSON; --output writes it to a file)
firecrawl crawl "<seed-url>" --output crawl.json
```

NOTE (verified against the installed CLI, 2026-06): crawl has **no** `--write-files`, `--seeds`, or `--format(s)` flags — it produces one JSON result (stdout or `--output <file>`). To land per-page markdown files on disk, parse `crawl.json` yourself, or `scrape` the individual URLs (scrape supports `--format` and `--output`). The old "`--write-files` replaces firecrawl-download" claim no longer matches the CLI.

---

## Cost shape

- N service calls bundled into one job, charged per page
- Concurrency (`--max-concurrency`) affects speed, not cost
- Writing the result to disk (`--output`) adds zero scraping cost
- Compared to looping N scrape calls: roughly the same Firecrawl cost, but **much** less token cost on Claude's side because results bundle into one tool result

---

## Common failure modes

| Symptom | What it usually means | What to try |
|---|---|---|
| Crawl finishes with very few pages | Seed URL has few outgoing links, or `--max-depth` too tight | Bump `--max-depth`; check if site uses JS routing (escalate to interact) |
| Many pages return blank markdown | Site uses heavy late-render JS | Increase `--wait-for` in Firecrawl config; check sample page with `scrape --wait-for 5000` first |
| Rate-limited mid-crawl | Site has anti-scraping protection | Lower `--max-concurrency` to 1-2; if still blocked, escalate the whole job to Cloak via `cloakscrape.py` per page |
| Crawl returns unexpected paths | Internal links go to subdomains | Use `--include-paths` to filter; the map command has `--include-subdomains` if subdomains are wanted |
| Crawl hangs or times out | Large site, no limit set | Set `--limit` or `--max-depth` defensively |

---

## Cost discipline

Crawls can run up the bill if uncapped. Defaults to set:

- **First crawl on an unknown site:** `--max-depth 2 --limit 20` to sample
- **Production crawl after sampling:** raise limits to what's actually needed
- **Watch for crawl traps:** infinite faceted-search URLs, calendar widgets, language switchers that multiply paths. Use `--exclude-paths` aggressively.

When uncertain about scope, run `map --search "..."` first to count target URLs before launching the crawl.

---

## Output handling

Output:

- **JSON** (`--output crawl.json`, or stdout) — one payload with an array of `{url, markdown, html?, ...}` objects. Codex consumes downstream.
- **Per-page files on disk** — the installed CLI has no `--write-files`; to get one file per page, parse `crawl.json` and write the slices yourself, or `scrape` the individual URLs (scrape supports `--output`). Useful for offline reading or feeding a downstream tool (RAG ingestion, static hosting).

---

## Pairing patterns

- **`map` → `crawl --include-paths`** (or scrape the mapped URLs individually) when you want bulk extract of only specific URLs from a large site — there is no `crawl --seeds`
- **`crawl` → `rag-architect`** when building a RAG corpus
- **`crawl --output` → split the JSON** when the user wants a local archive (offline reading, reference docs)
- **`crawl` → `humanizer` / `marketing`** when scraped content becomes input for content production

---

## Escalation

Crawl is harder to escalate than single-URL scrape because the tier-2 (Cloak) tier-3 (chrome-devtools-mcp) browser-driven approaches don't bulk-extract well. If a whole crawl fails due to bot detection:

1. **First try `--max-concurrency 1`** to look more like a real user
2. **Then try cloaking the crawl** — Firecrawl with a residential proxy flag if supported
3. **Last resort:** loop `interact` per page with Cloak Browser. This is much more expensive than tier-1 crawl, so push back to the user on whether the data is worth the cost before running it.

---

## See also

- [SKILL.md](../SKILL.md) — mechanic entry
- [scrape.md](scrape.md) — single-URL alternative
- [map.md](map.md) — URL discovery before crawl
- [interact.md](interact.md) — per-page fallback when crawl bot-blocks
- [agent.md](agent.md) — structured-data alternative when you want JSON not markdown
