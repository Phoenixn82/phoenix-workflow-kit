---
name: seo
description: Comprehensive SEO mechanic. One entry, 22 sub-wrenches. Detects business type (SaaS / ecommerce / local / publisher / agency / programmatic) and dispatches the right wrench set. Covers classic SEO + GEO (AI Overviews / ChatGPT / Perplexity / llms.txt) + image SEO + maps + international + structured data. Per AGENTS.md hard rule #5, Codex writes the actual schema files / sitemaps / robots.txt; seo analyzes and recommends. Trigger phrases include "SEO", "audit", "schema", "Core Web Vitals", "sitemap", "E-E-A-T", "AI Overviews", "GEO", "technical SEO", "content quality", "page speed", "structured data", "local SEO", "GBP", "map pack", "backlinks", "topic cluster", "competitor page", "robots.txt".
---

# seo — comprehensive SEO mechanic

One mechanic, 22 wrenches across all SEO surfaces. Business-type detection at the entry routes to the right wrench set. Classic SEO + GEO (AI search) + maps + international + e-commerce + programmatic all under one home.

---

## Cardinals

1. **One entry, business-type detection.** `seo` dispatches based on detected business type. Audit fires 8 always-wrenches + up to 9 conditional in parallel. Single-wrench invocations (`seo page <url>` / `seo schema <url>` / etc.) are direct.

2. **Conditional wrenches gate on infrastructure.** `image-gen` needs banana MCP. `google` needs the user's GSC / GA4 / PageSpeed API credentials wired. `dataforseo` needs the DataForSEO MCP extension. SKILL.md checks availability; surfaces "install X to enable Y" rather than failing silently. Doesn't fire conditionals that aren't ready.

3. **Codex writes the deliverables.** When seo work produces schema JSON-LD files, sitemap.xml, robots.txt, hreflang tags as deliverables to the project, Codex writes them per AGENTS.md hard rule #5. seo analyzes + recommends; the integration is Codex via `router`.

4. **GEO is first-class.** `geo` covers AI Overviews / ChatGPT web search / Perplexity citations / llms.txt — increasingly the lane the user's projects need. Not bolted-on; one of the 8 always-wrenches in a full audit.

5. **Cost-aware tier selection.** Live SERP / keyword volume / backlink data goes through `dataforseo` when wired (cost-controlled). Without DataForSEO, the wrench falls back to free sources (Bing Webmaster, Common Crawl, Moz API limited tier) — slower / less coverage but $0.

6. **printing-press-router fires first for new integrations.** Adding DataForSEO / Search Console / new API → CLI > API > MCP ladder via printing-press-router before this mechanic builds the wrapper.

---

## Business-type detection

When `seo audit <site>` fires, the SKILL.md detects:

| Signal | Type | Adds wrenches |
|---|---|---|
| Product pages + cart + checkout | E-commerce | `ecommerce` |
| Multiple `/blog/`, `/articles/`, author tags | Publisher | content-heavy weights |
| GBP markup, NAP visible, address visible | Local | `local`, `maps` |
| Multiple languages / `hreflang` tags / `/es/`, `/fr/` paths | International | `hreflang` |
| Many templated pages from one schema | Programmatic | `programmatic` |
| "vs", "alternatives", "best" pages | Comparison-heavy | `competitor-pages` |
| SaaS pricing page + feature pages | SaaS | content + technical focus |

A site can match multiple types; wrench set is union. The user can override detection.

---

## Audit dispatch (8 always + up to 9 conditional)

**Always-fire (8):**
- `technical` — crawlability / indexability / security / CWV
- `content` — E-E-A-T / readability / thin content
- `schema` — JSON-LD validate
- `sitemap` — XML validate
- `images` — alt text / file size / WebP-AVIF
- `geo` — AI Overviews / llms.txt / passage citability
- `page` (top-10 pages by signal) — deep per-URL
- `backlinks` (free-tier data only when DataForSEO unavailable)

**Conditional (fire if business type + infrastructure):**
- `local` (if local business) + `maps` (if local + DataForSEO or Overpass) + `hreflang` (if international) + `ecommerce` (if products) + `programmatic` (if templated) + `competitor-pages` (if comparison) + `dataforseo` (if MCP wired) + `google` (if API creds) + `image-gen` (if banana MCP)

---

## When this mechanic fires

- "SEO audit" / "audit my site"
- "Check the SEO" / "is my site optimized"
- "Schema for this page" / "JSON-LD"
- "Core Web Vitals" / "page speed" / "LCP"
- "Sitemap" / "robots.txt"
- "AI Overviews" / "GEO" / "show up in ChatGPT"
- "Local SEO" / "GBP" / "map pack"
- "Topic cluster" / "content strategy"
- "Backlinks" / "link profile"
- "Competitor comparison" / "vs page"

Don't fire when:
- The user wants brand-side design (route to design-studio)
- The user wants content production (route to content-forge)
- The user wants to ship a feature (route to ship)

---

## Picking the wrench

| Shape of the ask | Wrench |
|---|---|
| Full site audit | `audit` (dispatches the set) |
| Single URL deep dive | `page` |
| Strategy / roadmap | `plan` |
| Specific dimension | `technical` / `content` / `schema` / `sitemap` / `images` / `geo` / `local` / `maps` / `hreflang` / `backlinks` / `cluster` / `sxo` |
| E-commerce SEO | `ecommerce` |
| Programmatic SEO planning | `programmatic` |
| Versus / alternatives pages | `competitor-pages` |
| Generate OG / hero images | `image-gen` (banana MCP) |
| Real Google data | `google` (API creds) |
| Live SERP / keyword data | `dataforseo` (DataForSEO MCP) |
| Track changes over time | `drift` |

---

## Cross-mechanic dependencies

- `web-scrape` for SERP scraping, competitor page extraction, backlink discovery (when DataForSEO unavailable)
- `router` for Gemini lane on grounded SERP research; Codex for schema / sitemap / hreflang generation
- `build` consumes seo recommendations (writes schema files, sitemap.xml, robots.txt to project)
- `second-brain` captures SEO baselines (for drift), recurring patterns, what worked
- `content-forge` produces the content seo's `content` wrench recommends
- `printing-press-router` fires first for any new SEO data integration

---

## What seo does NOT do

- Does not write content (`content-forge`)
- Does not implement schema files in the project (Codex via `router`)
- Does not design pages (`design-studio`)
- Does not ship code (`ship`)
- Does not auto-monitor (per hard rule #1; `drift` is on-demand)
- Does not auto-fire conditionals when infrastructure isn't ready (surfaces "install X" instead)

---

## Wrenches

### Always-available (15)

| Wrench | Path | What it does |
|---|---|---|
| **audit** | `wrenches/audit.md` | Full-site sweep dispatching 8 always + up to 9 conditional wrenches in parallel |
| **page** | `wrenches/page.md` | Single-URL deep analysis (on-page + content + schema + perf + GEO) |
| **plan** | `wrenches/plan.md` | Strategy + roadmap with industry-specific templates |
| **technical** | `wrenches/technical.md` | Crawlability / indexability / security / CWV / mobile / JS rendering / IndexNow |
| **content** | `wrenches/content.md` | E-E-A-T / readability / depth / AI citation readiness / thin content |
| **schema** | `wrenches/schema.md` | JSON-LD detect / validate / generate |
| **sitemap** | `wrenches/sitemap.md` | XML validate / generate with industry templates |
| **images** | `wrenches/images.md` | Alt text / file size / WebP-AVIF / responsive / lazy load / image SERP |
| **geo** | `wrenches/geo.md` | AI Overviews / ChatGPT / Perplexity / llms.txt / passage citability / brand mention signals |
| **local** | `wrenches/local.md` | GBP / NAP / citations / local schema / location pages / multi-location |
| **maps** | `wrenches/maps.md` | Geo-grid rank tracking / SoLV / review intelligence / cross-platform NAP |
| **hreflang** | `wrenches/hreflang.md` | i18n / language-region tags / multi-region |
| **backlinks** | `wrenches/backlinks.md` | Referring domains / anchor text / toxic links / disavow / link gap |
| **cluster** | `wrenches/cluster.md` | SERP-based topic clustering / hub-and-spoke / internal link matrices |
| **sxo** | `wrenches/sxo.md` | Search experience / SERP backwards / persona scoring / page-type mismatch |

### Infrastructure-gated + monitoring (4)

The first three are **infrastructure-gated** (Cardinal #2): they don't fire until their MCP / creds are wired. `drift` requires nothing — it's grouped here as an on-demand monitor, not as a gated wrench. This is distinct from the **business-type-gated** conditionals in the audit-dispatch list above (`local` / `maps` / `hreflang` / `ecommerce` / `programmatic` / `competitor-pages`), which are always-available wrenches that the audit fires based on detected business type.

| Wrench | Path | Requires | What it does |
|---|---|---|---|
| **image-gen** | `wrenches/image-gen.md` | Banana MCP | OG / social preview / hero / schema images via Gemini |
| **google** | `wrenches/google.md` | GSC / PSI / GA4 / CrUX / Indexing API creds | Real Google field data |
| **dataforseo** | `wrenches/dataforseo.md` | DataForSEO MCP | Live SERP / keyword volume / backlinks / AI visibility |
| **drift** | `wrenches/drift.md` | None | SEO regression monitoring; baseline + diff |

### E-commerce + programmatic specific (3)

| Wrench | Path | What it does |
|---|---|---|
| **ecommerce** | `wrenches/ecommerce.md` | Product schema / Shopping / Amazon / marketplace / pricing gaps |
| **competitor-pages** | `wrenches/competitor-pages.md` | "X vs Y" / alternatives / feature matrices / comparison schema |
| **programmatic** | `wrenches/programmatic.md` | Pages-at-scale templates / URL patterns / thin content safeguards / index bloat |

---

## See also

- [wrenches/audit.md](wrenches/audit.md) — entry dispatcher
- [wrenches/page.md](wrenches/page.md) — single URL
- [wrenches/plan.md](wrenches/plan.md) — strategy
- All other wrenches as listed in tables above
- [`AGENTS.md`](../../../AGENTS.md) — hard rule #5 (Codex writes deliverables); hard rule #6 (cost-first)
- [`printing-press-router`](../printing-press-router/) — fires first for new API integrations
- [`web-scrape/SKILL.md`](../web-scrape/SKILL.md) — SERP scraping primitive
- [`router/SKILL.md`](../router/SKILL.md) — Codex / Gemini dispatch
- [`second-brain/SKILL.md`](../second-brain/SKILL.md) — baseline + lesson capture
