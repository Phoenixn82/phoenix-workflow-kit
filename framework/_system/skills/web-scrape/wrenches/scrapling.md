# scrapling — free local adaptive scraper (web-scrape wrench)

Local, zero-cost Python scraper that **relocates elements after a site's layout changes**
(adaptive selectors, no LLM) and can run **stealth fetchers that bypass Cloudflare Turnstile
locally**. It is the *free local* lane of the cost ladder — reach for it instead of the
chrome-devtools-mcp / Playwright tier 3, and as a no-credit alternative to Cloak for some
Turnstile targets.

> **Not the new default.** Firecrawl still wins for one-off / frictionless "give me this page as
> markdown" — it's one service call, no selectors, JS rendered. Scrapling earns its place when you
> want **zero Firecrawl spend at volume**, **layout-change resilience** on a recurring target, or a
> **free local Cloudflare-Turnstile bypass**. Don't reach for it just because "local feels safer."

## When to pick this wrench

| Signal | Why Scrapling |
|---|---|
| Recurring scrape target whose markup keeps breaking your selectors | Adaptive mode re-finds the same element by similarity after the page changes — no re-coding selectors, no LLM |
| High-volume / repeated local scraping where Firecrawl credits add up | Fully local + free; one-time `pip` cost, then $0 per page |
| Cloudflare Turnstile / headless-fingerprint block, and you'd rather not spend Cloak credits | `StealthyFetcher` (curl_cffi TLS impersonation + patchright) bypasses many bot grids locally |
| You need the scrape inside project Python anyway | It's a library (Scrapy-like `Fetcher`/`Spider`), not a service |

Still escalate to **Cloak Browser** when a target needs residential IPs or a held auth session
Scrapling can't manage locally; Firecrawl remains tier 1 for plain extraction.

## Install state (this box)

Installed in a dedicated venv so it never pollutes global Python:

- Python: `C:/Users/<you>/Desktop/AI_Projects/_system/skills/web-scrape/.venv-scrapling/Scripts/python.exe`
- CLI:    `C:/Users/<you>/Desktop/AI_Projects/_system/skills/web-scrape/.venv-scrapling/Scripts/scrapling.exe`
- Installed extra: `scrapling[shell]` → HTTP `Fetcher`, adaptive selectors, and the no-code `scrapling extract` CLI. **HTTP-only — no browser download.**
- **Stealth/dynamic fetchers** (`StealthyFetcher`, `DynamicFetcher` for JS/Cloudflare) need a one-time browser fetch:
  `& ".../.venv-scrapling/Scripts/scrapling.exe" install` (downloads patchright/Playwright browsers, several hundred MB). Run that only when you actually need the Turnstile-bypass tier.

## Usage

**No-code: URL → markdown (HTTP fetcher, the workhorse)**
```bash
"C:/Users/<you>/Desktop/AI_Projects/_system/skills/web-scrape/.venv-scrapling/Scripts/scrapling.exe" extract get "<url>" out.md
# add --css-selector "<sel>" to narrow; --txt for plain text
```

**Library: adaptive selectors (survive layout change)**
```python
from scrapling.fetchers import Fetcher
Fetcher.configure(adaptive=True, adaptive_domain="example.com")
page = Fetcher.get(url)
el = page.css("#some > selector", auto_save=True)[0]   # first run: learn + save the element fingerprint
# ...later, after the site's markup changes...
el = page.css("#some > selector", adaptive=True)[0]      # relocates the same element by similarity
```

**Stealth (Cloudflare Turnstile / bot grids — needs `scrapling install` first)**
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
```

## After a run
- If this wrench was reached only because Firecrawl/Cloak fell through, log it:
  `python ../scripts/scrape-lesson-log.py --project <slug> --url <url> --tier-used 3 --tier-cheaper 1 --tokens-burned N`
- Recurring target + the working adaptive selector / stealth recipe → the project's vault note
  (`Projects/<slug>/`) so the next run goes straight to Scrapling.
- Scrapling ships its own agent SKILL.md under the repo's `agent-skill/` — if a project leans on it
  heavily, that's the seed for promoting this wrench into a fuller mechanic.

## See also
- [`../SKILL.md`](../SKILL.md) — the web-scrape mechanic + cost ladder (Scrapling = free local lane)
- [`Actions/scraping-tier.md`](../../../second-brain/Actions/scraping-tier.md) — canonical tier order
- [`wrenches/scrape.md`](scrape.md) — Firecrawl single-URL (tier 1 default)
- [`wrenches/interact.md`](interact.md) — Cloak Browser fallback (tier 2)
