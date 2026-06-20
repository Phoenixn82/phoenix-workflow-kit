---
name: web-scrape-search
description: Firecrawl web search wrench. Real Google-grade results with optional full-page markdown for each hit. Use for discovery before extraction — when the ask starts with "find me X" / "search the web for Y" / "what are people saying about Z" / "look up", before any specific URL is known. Pairs naturally with scrape (search then scrape each result) or with content-forge (search then summarize).
---

# web-scrape-search — discovery before extraction

When the user doesn't have URLs yet, this is the first wrench. Returns search results with snippets, and optionally fetches the full markdown of each hit in one pass. One service call beats running a separate scrape per result.

---

## When to fire

- "Search the web for X"
- "Find articles about Y"
- "What's been written recently about Z"
- "Look up the latest on \<topic\>"
- "Find me 10 sources on X"
- "Research X across the web" (often pairs with content-forge fact-checker afterwards)

Don't fire when:
- The URL is already known → use `scrape` directly
- The intent is discovery WITHIN one domain → use `map` instead (cheaper, no SERP overhead)
- The ask is "deep research dossier" → route to Gemini Deep Research via the `router` mechanic. Web-scrape search is a primitive; Gemini Deep Research is the full pipeline.

---

## CLI patterns

```bash
# Default: 10 results, snippets only (cheap)
firecrawl search "<query>"

# With full markdown for each result (one service call, all hits)
firecrawl search "<query>" --limit 10 --fetch-content

# Time-filtered (recent only)
firecrawl search "<query>" --tbs "qdr:w"   # past week
firecrawl search "<query>" --tbs "qdr:m"   # past month

# Region/language filtered
firecrawl search "<query>" --location "United States" --lang "en"

# Specific result count
firecrawl search "<query>" --limit 25
```

The `--fetch-content` flag is the killer feature: one call returns N pages of full markdown. Without it, Claude has to loop scrape-per-result, which is N+1 service calls instead of 1.

---

## Cost shape

- Without `--fetch-content`: very cheap (SERP-only, ~1 Firecrawl unit)
- With `--fetch-content`: cheap per page (N Firecrawl units, but bundled — saves token overhead vs. looping)
- Compared to N separate scrapes: roughly half the cost because the SERP fetch isn't repeated

**When to use `--fetch-content`:** if you'll definitely read all results. **When to skip:** if you'll triage snippets first and only deep-dive 1-3.

---

## Output handling

Search returns JSON with results array. Each result has `title`, `url`, `description`, and (if `--fetch-content`) `markdown`. Pipe to a file for downstream use:

```bash
firecrawl search "<query>" --fetch-content --output results.json
```

For one-off interactive use (the user asks a question, Claude answers from the results), parse inline. For pipelines, write to disk and have Codex consume.

---

## Escalation signals

Search rarely needs to escalate, but if results are sparse or off-topic:

1. **Re-query with better keywords first.** "best practices" → "production patterns 2026"; vague nouns → specific tech terms
2. **Try `--tbs` time filter** if results are stale
3. **Try `--location` filter** if results are wrong region
4. **Only after 2 reformulations fail:** consider Gemini grounded search (Deep Research) for higher-quality result curation. Don't escalate to Cloak / chrome-devtools — those are for blocked pages, not bad results.

---

## Pairing patterns

- **`search` → `scrape` per result** when you need full content from only a few hits
- **`search --fetch-content`** when you need full content from all hits (more efficient)
- **`search` → `content-forge → fact-checker`** when verifying claims across sources
- **`search` → `agent` with schema** when extracting structured data across multiple sources (e.g., pricing comparison, feature matrix)

---

## See also

- [SKILL.md](../SKILL.md) — mechanic entry
- [scrape.md](scrape.md) — single-URL extraction (pairs with search)
- [agent.md](agent.md) — schema-driven structured extraction across results
