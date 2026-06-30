---
name: web-scrape
description: Cost-first web scraping mechanic. Firecrawl (default cheap tier) → Cloak Browser (bot-detection / geo / auth fallback) → chrome-devtools-mcp or Playwright (local driver, last resort). Dispatches to one of seven wrenches based on the shape of the ask. Fires on phrases like "scrape this", "get the content from", "extract from URL", "crawl this site", "find pages about X on Y.com", "search the web for", "log into and pull", "structured data from", "all products from this catalog", or any URL the user wants turned into usable text/data.
---

# web-scrape — cost-first scraping mechanic

One mechanic, one cost ladder, seven wrenches. Claude reads the ask, picks the cheapest wrench that can do the job, falls through tiers only when the cheap one actually fails — never speculatively.

The cost ladder is not a capability ladder. Firecrawl can render JS, hold a browser session, log into auth-walled pages, and extract structured JSON. It loses only to bot-detection grids that fingerprint the headless browser, geo-restricted content, or flows that need a real residential IP. The instinct to reach for chrome-devtools-mcp "because it's a real browser" is wrong almost every time.

---

## Cardinals

1. **Cost-first ladder, never inverted.** Firecrawl → Cloak Browser → chrome-devtools-mcp / Playwright. Try the cheap tier first. Fall through only on actual failure, never on speculation. Each tier downward is roughly 10× the per-page cost in tokens (Firecrawl returns one markdown blob; chrome-devtools-mcp is a model call per click / scroll / wait).

2. **Pick the right wrench, not the heaviest.** Single URL → `scrape`. List URLs on a domain → `map`. Extract every page on a domain → `crawl`. Discovery from a query → `search`. Login, clicks, pagination, multi-step → `interact`. Structured JSON across multiple pages with a schema → `agent`. When the ask is unclear, ask the user — don't guess the heaviest.

3. **JS-rendered SPAs are Firecrawl's home turf.** Don't escalate to chrome-devtools-mcp just because a page is React / Vue / Next / Svelte. Firecrawl renders JS by default. Escalate only on documented signals: 403/429 with bot-detection wording in the body, geo-block redirect, captcha challenge, auth flow Firecrawl can't hold.

4. **Codex writes integration code, not Claude.** Per AGENTS.md hard rule #5, when a scrape result feeds into project code (parser, transformer, persistence layer, scheduled job), Claude composes the spec and Codex writes the implementation. Claude can author for the small / one-file / well-understood case, but the default is Codex. Web-scrape is the data layer; the integration is build territory.

5. **Save what's worth saving to second-brain.** Recurring scrape targets, working selectors, and anti-bot patterns that broke through → the project's own vault note (`Projects/<slug>/`). Cost-vs-result fall-through lessons are written automatically by `scrape-lesson-log.py` to `Projects/<slug>/tokens.md` (the per-project token-expense ledger). Don't re-learn the same site twice, and don't leave the next Claude blind to "we already tried Firecrawl on this domain, it bot-blocks, go straight to Cloak." (The default tier order itself lives at `_system/second-brain/Actions/scraping-tier.md`.)

6. **Don't self-loop on scraping.** Per AGENTS.md rule #1, no skill self-schedules. A 500-URL crawl is fine because the user triggered it. A recurring "watch this site for changes" is fine too — but only as an automation the user explicitly stands up and registers under `_system/automations/` (budget-gated), never one the scraper starts on its own.

---

## The cost ladder, spelled out

```
                    ┌─────────────────────────────────┐
       ask ──────►  │ Tier 1: Firecrawl               │
                    │ - Service call, markdown out    │
                    │ - JS render included            │
                    │ - ~$0.01 per page equivalent    │
                    │ - 95% of jobs end here          │
                    └────────────┬────────────────────┘
                                 │
                          works? │
                            yes  │  no (bot-block / geo / auth Firecrawl can't hold)
                                 │
                                 ▼
                    ┌─────────────────────────────────┐
                    │ Tier 2: Cloak Browser           │
                    │ - Anti-detection browser pool   │
                    │ - Residential IPs available     │
                    │ - Holds auth sessions           │
                    │ - ~5× Tier 1 cost               │
                    │ - 4% of jobs land here          │
                    └────────────┬────────────────────┘
                                 │
                          works? │
                            yes  │  no (live debugging needed, custom JS injection,
                                 │       page state inspection)
                                 ▼
                    ┌─────────────────────────────────┐
                    │ Tier 3: chrome-devtools-mcp /   │
                    │         Playwright (LAST RESORT)│
                    │ - Local browser, model-driven   │
                    │ - Every click is a model call   │
                    │ - ~10-20× Tier 1 cost           │
                    │ - 1% of jobs need this          │
                    └─────────────────────────────────┘
```

**Inversion trap:** the local browser feels more powerful, so the instinct is to reach for it first. That instinct is wrong. The local browser is a model-call-per-action — a 20-page scrape is 200+ model calls. Firecrawl is one service call per page. Use the local browser only when you genuinely need live JS injection (visual debugging via `chrome-devtools-mcp:evaluate_script` per the global CLAUDE.md) or page-state inspection. Never for "I want to be safe."

---

## Picking the wrench

| Shape of the ask | Wrench | Why |
|---|---|---|
| "What's the latest on X / search the web for Y" | `search` | Discovery before extraction. Returns results + optionally hydrated content |
| "Scrape this URL" / "get the content from \<one URL\>" | `scrape` | Single URL, markdown out, the workhorse |
| "What pages are on this site" / "find the URL for X on Y.com" | `map` | URL discovery without extraction |
| "Get all pages under /docs" / "crawl this site" / "bulk extract" | `crawl` | Depth-filtered, multi-page extraction |
| "Log in and pull" / "click through pagination" / "fill the form first" / "scrape failed because JS" | `interact` | Holds a live browser session, runs actions, then extracts. Also serves the Cloak Browser fallback tier |
| "Extract all products as JSON with these fields" / "structured data from multiple pages with this schema" | `agent` | Schema-driven, AI-navigated structured extraction |
| "scrape it free / locally" / "this selector keeps breaking" / "Cloudflare Turnstile, no Cloak credits" | `scrapling` | Free local adaptive scraper — relocates elements after layout change (no LLM); local Turnstile bypass. The free-local lane, cheaper than tier 3 |

If the ask mixes shapes (e.g., "search for blog posts about X then extract them all"), chain wrenches: `search` → loop `scrape` per result. Don't try to pack into one wrench.

---

## When this mechanic fires (auto-detect)

- Any URL pasted with a request to extract / pull / read / get / fetch / scrape it
- "Search the web for X" / "find articles about Y" / "look up Z online"
- "Crawl X" / "get all pages from X" / "bulk extract from X"
- "What pages are on \<site\>" / "find the URL for X" / "map \<site\>"
- "Log into X and pull Y" / "interact with X" / "submit the form on X"
- "Extract structured data" / "extract as JSON with this schema"

When it does NOT fire — even though it sounds like it might:

- "Build an MCP for X" / "wire up the Y API" → `printing-press-router` first (CLI > API > MCP ladder)
- "Read this PDF I downloaded" → `gemini` lane via `router` (long-context read, not scraping)
- "Watch a video" → `video-scan`
- "Debug why this React component renders weird" → `chrome-devtools-mcp` directly via the global frontend-visual-debugging rule, NOT web-scrape. Different tool, same protocol.

---

## Cross-mechanic dependencies

- **`printing-press-router`** fires first if the ask is "build an integration with X" — that's an integration job, not a scrape job. Web-scrape is for grabbing existing public content, not wiring an app to a third-party service.
- **`router`** dispatches Codex when a scrape result feeds into code; dispatches Gemini when the scraped content is a long document needing long-context analysis after extraction.
- **`second-brain`** captures scraping lessons per project (`Projects/<slug>/` for target sites, working patterns, anti-bot signals; `Projects/<slug>/tokens.md` is the cost-vs-result ledger `scrape-lesson-log.py` writes). The default tier order lives at `Actions/scraping-tier.md`.
- **`build`** consumes scrape outputs when building data ingestion (a scraped catalog becomes seed data for the project DB; a scraped docs site becomes RAG corpus for `rag-architect`).
- **`seo`** uses scrape output for competitor page audits, SERP scraping, backlink discovery — those wrenches call into web-scrape rather than re-implementing scraping logic.

---

## What this mechanic does NOT do

- It does not build CLIs, MCPs, or integrations. That's `printing-press-router` → `skill-forge`.
- It does not analyze long PDFs or multimodal sources. That's the Gemini lane via `router`.
- It does not transcribe or screenshot videos. That's `video-scan`.
- It does not replace `chrome-devtools-mcp` for live frontend debugging. The global CLAUDE.md mandates `evaluate_script` for visual/layout/CSS bugs before editing source — that's a debug tool, not a scraper. Web-scrape's tier 3 only borrows chrome-devtools-mcp for content extraction when Cloak Browser also fails.
- It does not save outputs by itself. The user decides where the markdown / JSON lands. Web-scrape returns the content; the caller (Claude or a downstream mechanic) decides what to do with it.
- It does not auto-schedule. No "watch this site every hour" loops. The user triggers each run, or kicks off a Codex `/goal` that loops manually.

---

## Wrenches

| Wrench | Path | What it does |
|---|---|---|
| **search** | `wrenches/search.md` | Firecrawl web search. Real results with optional full-page markdown. Use for discovery before extraction |
| **scrape** | `wrenches/scrape.md` | Single-URL markdown extraction. Handles JS-rendered SPAs by default. The workhorse |
| **map** | `wrenches/map.md` | URL discovery on a domain. Returns a list of URLs, optionally search-filtered. No extraction |
| **crawl** | `wrenches/crawl.md` | Bulk extract every page (or filtered subset) on a domain. Depth, path, and content-type filters. Includes `--write-files` for download-to-disk |
| **interact** | `wrenches/interact.md` | Live browser session. Click, fill, navigate, then extract. Serves the Cloak Browser fallback tier. Also handles auth flows |
| **agent** | `wrenches/agent.md` | Structured JSON extraction with a schema, AI-navigated across multiple pages. For directories, catalogs, pricing pages, anything tabular |
| **scrapling** | `wrenches/scrapling.md` | Free **local** adaptive scraper. Relocates elements after layout changes (no LLM); local Cloudflare-Turnstile bypass. The free-local lane — use for zero-cost/high-volume scraping or recurring targets that keep breaking selectors. Cheaper than the tier-3 local drivers |

---

## Tier 1: Firecrawl (default)

The user has the `firecrawl` npm CLI installed and authenticated (manage auth via `firecrawl config` / `firecrawl login` / `firecrawl --status`; the Firecrawl MCP server is the fallback lane). Web-scrape calls Firecrawl through these CLI patterns (verified against the installed CLI, 2026-06):

```bash
# search
firecrawl search "<query>" --limit 10

# scrape one URL  (real flag is -f/--format, comma-separated)
firecrawl scrape "<url>" --format markdown

# map a domain
firecrawl map "<domain>" --search "<optional filter>"

# crawl a domain  (real path filters are --include-paths/--exclude-paths)
firecrawl crawl "<url>" --max-depth 3 --include-paths "/docs/*"

# interact: run an AI prompt or code against a PREVIOUS scrape (not a live "start" session)
firecrawl scrape "<url>"            # scrape first
firecrawl interact "<prompt>"       # or: firecrawl interact --code "<playwright-js>"

# agent (structured extraction)
firecrawl agent "<prompt>" --schema schema.json
```

Each wrench documents its full flag set. The mechanic just ensures the right wrench fires.

---

## Tier 2: Cloak Browser (escalation)

Cloak Browser is the bot-detection-aware alternative. Use when Firecrawl returns 403/429 with bot-detection signatures, geo-blocks the request, or fails to hold an auth session. **Cloak is invoked via the `cloakscrape.py` helper, NOT a firecrawl flag:** `python C:\Users\<you>\.claude\scripts\cloakscrape.py "<url>" [--profile NAME] [--humanize] [--wait-for SELECTOR] [--timezone TZ] [--locale LOC]` (outputs rendered HTML to stdout). See the `interact` wrench for the full escalation flow.

Signal to escalate to Cloak:
- HTTP 403 with response body mentioning "automated", "bot", "Cloudflare", "captcha", "Imperva"
- HTTP 429 followed by 403 (rate-limit then block pattern)
- Page returns successfully but content is the bot-block placeholder ("Please verify you are human")
- Auth flow requires a session cookie Firecrawl can't persist across calls

Don't escalate to Cloak just because:
- The page is slow (use `--wait-for` in Firecrawl scrape)
- The page renders late (Firecrawl already waits for JS)
- The page looks complex (irrelevant — Firecrawl handles complex SPAs fine)

---

## Tier 3: chrome-devtools-mcp / Playwright (last resort)

Used when Cloak also fails AND the failure points to needing live JS injection, page-state inspection, or interactive debugging. Drive through `mcp__plugin_chrome-devtools-mcp_chrome-devtools__*` tools or Playwright scripts (Codex authors the Playwright script per AGENTS.md hard rule #5; Claude just specs).

This is also the tool the global CLAUDE.md mandates for frontend visual debugging — but that's a separate use case (debugging the user's own apps, not scraping external sites). Don't confuse the two paths.

---

## Helper scripts

Cost-first probe + lesson-logger at `scripts/` (built Phase 5, acceptance-tested 2026-05-28):

| Script | What it does |
|---|---|
| `scripts/cost-tier-check.py --url <url> [--json]` | Probes tier 1 (Firecrawl) → tier 2 (Cloak) → tier 3 (local driver) in order. Returns the verified tier with reason + latency_ms. Use BEFORE invoking a wrench so the right tier is chosen first-try. |
| `scripts/scrape-lesson-log.py --project <slug> --url <url> --tier-used N --tier-cheaper M --tokens-burned N` | Appends a `token-note` entry to `Projects/<slug>/tokens.md` when a scrape fell through to a higher (more expensive) tier. 24h dupe-skip. Auto-invoke from wrenches when tier_used > 1. |

Spec (provenance only): `PHASE_5_DISPATCH.md` § 4.1 + § 4.2 — that file now lives solely at `_archive\claude_projects_2026-05-pre-rebuild\Rebuild\`; the shipped scripts are self-documenting. The same `Spec:` headers in `cost-tier-check.py` / `scrape-lesson-log.py` are likewise just provenance.

---

## See also

- [wrenches/search.md](wrenches/search.md) — Firecrawl web search
- [wrenches/scrape.md](wrenches/scrape.md) — single-URL extraction (workhorse)
- [wrenches/map.md](wrenches/map.md) — URL discovery on a domain
- [wrenches/crawl.md](wrenches/crawl.md) — bulk multi-page extraction
- [wrenches/interact.md](wrenches/interact.md) — live browser session + Cloak fallback
- [wrenches/agent.md](wrenches/agent.md) — structured JSON extraction with schema
- [wrenches/scrapling.md](wrenches/scrapling.md) — free local adaptive scraper (zero Firecrawl spend; layout-change resilience; local Turnstile bypass)
- [`AGENTS.md`](../../../AGENTS.md) — operating manual (hard rule #5 code-routing, hard rule #6 cost-first scraping)
- [`DECISION_MAP.md`](../../../DECISION_MAP.md) — task → tool routing
- [`router/SKILL.md`](../router/SKILL.md) — multi-brain dispatcher (Codex/Gemini routing for downstream work)
- [`second-brain/SKILL.md`](../second-brain/SKILL.md) — where scraping lessons land
