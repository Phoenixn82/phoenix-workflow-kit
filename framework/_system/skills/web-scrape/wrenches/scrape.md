---
name: web-scrape-scrape
description: Single-URL Firecrawl markdown extraction. The workhorse of web-scrape — 90% of one-off scrape jobs end here. Handles JS-rendered SPAs by default. Returns clean markdown optimized for LLM consumption. Use whenever the ask is "scrape this URL" / "get the content from \<url\>" / "what does this page say" / "extract from \<single URL\>" / "fetch this webpage" / "read this for me" with a URL.
---

# web-scrape-scrape — single-URL markdown extraction

One URL in, clean markdown out. The vast majority of scrape jobs are this shape. Don't over-think it.

---

## When to fire

- The user pastes a URL with "scrape this" / "get the content" / "what does this say"
- A pipeline needs the markdown of a specific known URL
- Following up after a `search` to deep-read 1-3 promising results
- Saving a reference article to second-brain
- Pre-processing a single source for `content-forge fact-checker`

Don't fire when:
- Multiple URLs on the same domain → use `crawl` (one bulk call beats N scrapes)
- You don't know the URL yet → use `search` or `map`
- The page needs a click / login first → use `interact`

---

## CLI patterns

```bash
# Default: clean markdown out
firecrawl scrape "<url>"

# Multiple formats in one call (real flag is -f/--format; comma-separated)
firecrawl scrape "<url>" --format markdown,html,links,screenshot

# Wait for late-rendering content
firecrawl scrape "<url>" --wait-for 3000   # ms

# Only extract main content (strip nav, footer, ads)
firecrawl scrape "<url>" --only-main-content

# Persistent browser profile (keeps cookies/session across scrapes — for paywalled/logged-in sites)
firecrawl scrape "<url>" --profile "<profile-name>"

# Include specific selectors only
firecrawl scrape "<url>" --include-tags "article,main,h1,h2,p"

# Exclude specific selectors
firecrawl scrape "<url>" --exclude-tags "nav,footer,aside,.ad"

# Output to file
firecrawl scrape "<url>" --output content.md
```

Defaults are good. Most jobs don't need flags. Reach for `--wait-for` when content is missing (signals late JS render); reach for `--only-main-content` when results are noisy with chrome.

---

## Cost shape

- One service call per URL, ~$0.01 equivalent
- JS render included (no surcharge)
- Screenshot adds modest overhead, only request when needed
- Multiple formats in one `--format` (comma-separated) call is cheaper than separate calls per format

---

## Common failure modes and what they mean

| Symptom | What it usually means | What to try |
|---|---|---|
| Returns empty `markdown` but `html` is fine | Markdown extractor confused by page structure | Add `--include-tags "article,main,h1,h2,p,li"` |
| Returns the page chrome but not the article | Late-rendering JS | `--wait-for 3000` first, then `--wait-for 5000` |
| Returns "Please verify you are human" / Cloudflare challenge | Bot detection | **Escalate to `interact` with Cloak Browser** |
| Returns 403/429 immediately | IP/rate limit or bot detection | Try `--profile` (persistent session) or `--country <code>`; if still blocked, escalate to Cloak |
| Returns 200 but content is "Please enable JavaScript" | Firecrawl JS render didn't catch | `--wait-for` first; if still blocked, escalate to `interact` |
| Returns 451 or geo-block message | Geographically restricted | Escalate to Cloak (residential IPs in the right region) |
| Returns login wall / paywall | Auth required | Escalate to `interact` for session-based scrape |

**Escalation rule:** try 2 Firecrawl flag tweaks (wait-for, user-agent, include-tags) before falling through to `interact`. Don't speed-jump to the more expensive tier.

---

## Pairing patterns

- **`search` → `scrape` per result** when only a few results matter
- **`scrape` → `humanizer`** when turning a source into casual content
- **`scrape` → `fact-checker`** when verifying claims against the source
- **`scrape` (one page of a docs site) → if good, `crawl` the rest** when one sample tells you the whole domain is worth grabbing

---

## Multi-URL note

If the user gives you 3+ URLs to scrape, don't loop scrape calls. Either:

1. **Same domain → use `crawl`** with seed URLs and a depth of 1 (one call extracts all of them)
2. **Different domains → use parallel** — scrape calls don't block each other, so dispatch in one message via multiple tool calls

Looping scrape sequentially is the slowest pattern.

---

## See also

- [SKILL.md](../SKILL.md) — mechanic entry
- [search.md](search.md) — discovery (precedes scrape)
- [interact.md](interact.md) — escalation tier for blocked / auth-walled pages
- [crawl.md](crawl.md) — bulk multi-URL alternative on the same domain
