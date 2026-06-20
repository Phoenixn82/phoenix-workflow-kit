---
name: web-scrape-interact
description: Live browser session wrench. Click buttons, fill forms, navigate flows, handle authentication, paginate infinite scroll, then extract. Serves both Firecrawl-hosted browser sessions (tier 1 for interactive scrapes) and the Cloak Browser fallback tier (tier 2 when Firecrawl bot-blocks). Use when the ask requires multi-step interaction with a page, or when scrape failed due to bot detection or auth. Trigger phrases include "log into and scrape", "click through pagination", "submit the form on", "infinite scroll", "scrape failed because", "needs authentication", "interact with this page".
---

# web-scrape-interact — live browser session

> **⚠️ CLI-accuracy correction (2026-06-12 audit):** The `firecrawl interact start --url … --provider cloak` / `interact click|fill|type|navigate|extract` session API documented below **does not exist** in the installed firecrawl CLI. The real `firecrawl interact` runs an AI prompt or Playwright `--code` against a *previous* scrape (`firecrawl scrape <url>` first, then `firecrawl interact "<prompt>"` or `firecrawl interact --code "<js>"`). **Cloak Browser (tier 2) is invoked through the helper, not firecrawl:** `python C:\Users\<you>\.claude\scripts\cloakscrape.py "<url>" [--profile NAME] [--humanize] [--wait-for SELECTOR] [--timezone TZ] [--locale LOC] [--proxy URL]` → rendered HTML on stdout. Treat the command snippets in the rest of this wrench as *intent* (what to accomplish), not literal syntax, until they are rewritten.

For everything scrape can't handle alone: auth flows, multi-step forms, pagination, infinite scroll, click-to-reveal content, and bot-detection escalation. The wrench that holds a browser session and runs actions in it.

This wrench wears two hats:
- **Tier 1 hat:** Firecrawl-hosted browser session for legitimate interactive scrapes (the auth / click / paginate work)
- **Tier 2 hat:** Cloak Browser fallback when Firecrawl gets bot-blocked

The CLI flags pick the provider.

---

## When to fire

**Tier 1 reasons:**
- "Log into \<site\> and scrape Y"
- "Click through pagination on \<list page\>"
- "Submit the form on \<URL\> with these values, then scrape"
- "Infinite scroll until you see X, then extract"
- "Scrape this multi-step wizard / checkout flow"
- "Accept the cookie banner first, then scrape"

**Tier 2 reasons (escalation):**
- `scrape` returned a Cloudflare challenge / "Please verify you are human"
- `scrape` returned 403 with bot-detection signature in body
- `scrape` returned 451 geo-block
- `scrape` returned 200 but body is the bot-block placeholder
- Auth flow Firecrawl tier-1 couldn't hold across requests

Don't fire when:
- A flag tweak to `scrape` would fix it (try `--wait-for`, `--user-agent`, `--include-tags` first)
- The site is just slow (use `scrape --wait-for`)
- The page is JS-rendered but otherwise normal (Firecrawl renders JS by default)

---

## CLI patterns

```bash
# Start an interactive session (Firecrawl tier 1)
firecrawl interact start --url "<url>"

# Start with Cloak Browser tier 2 (escalation)
firecrawl interact start --url "<url>" --provider cloak

# Start with residential-IP region (Cloak)
firecrawl interact start --url "<url>" --provider cloak --region "us"

# Actions on the session
firecrawl interact click --selector "button.next"
firecrawl interact fill --selector "input[name=email]" --value "<value>"
firecrawl interact type --selector "input#search" --text "<query>"
firecrawl interact wait --selector ".results-loaded"
firecrawl interact scroll --direction down --pixels 1000
firecrawl interact press --key "Enter"
firecrawl interact navigate --url "<next-url>"   # within same session

# Extract content from the current page state
firecrawl interact extract --format markdown
firecrawl interact extract --format json --schema schema.json

# Natural-language action (AI-driven)
firecrawl interact do "Click 'Load more' until all results are visible"

# Close session
firecrawl interact stop
```

The natural-language `do` command is the workhorse. The user describes what should happen ("log in with these creds, then click 'My Orders', then extract the table") and Firecrawl handles the DOM specifics.

---

## Cost shape

- **Tier 1 Firecrawl interact:** ~5× a regular scrape (session overhead + per-action calls)
- **Tier 2 Cloak Browser:** ~5-10× tier 1 (anti-detection infrastructure)
- **Both tiers:** still cheaper than tier 3 chrome-devtools-mcp because the session is service-side, not Claude making model calls per action

Cost adds up fast on multi-step flows. Budget consciously. If a flow takes 20 clicks to extract one page, ask whether the data is worth it before running.

---

## Auth handling

Three patterns:

1. **Cookie injection** — fastest. If the user has a session cookie already, pass it:
   ```bash
   firecrawl interact start --url "<url>" --cookies "session=<value>"
   ```

2. **Login flow** — when the user has creds and the site has a normal login form:
   ```bash
   firecrawl interact start --url "<login-url>"
   firecrawl interact fill --selector "input[name=email]" --value "$EMAIL"
   firecrawl interact fill --selector "input[name=password]" --value "$PASSWORD"
   firecrawl interact click --selector "button[type=submit]"
   firecrawl interact wait --selector ".dashboard"
   ```
   Pull creds from environment variables, never hardcode.

3. **OAuth / 2FA** — usually impossible to automate cleanly. Push back to the user; either the user does the auth in his own browser and shares the session cookie, or this isn't the right tier of automation.

---

## Tier 2 escalation: Cloak Browser

Cloak Browser is the bot-detection-resistant tier. Use when Firecrawl tier 1 fails with bot-block signatures.

```bash
# Same interface, different provider
firecrawl interact start --url "<url>" --provider cloak
```

Cloak offers:
- Anti-detection browser fingerprinting (canvas, WebGL, fonts, plugins all randomized)
- Residential IP pool (`--region us|eu|asia|...`)
- Stealth mode that bypasses common bot-checks (Cloudflare, Imperva, PerimeterX, DataDome)

When NOT to escalate to Cloak:
- The block is geo-only with no anti-bot (try Firecrawl with a region flag first if supported)
- The block is rate-limit only (slow down, don't switch tier)
- The auth flow needs 2FA (Cloak doesn't solve that)

When to push back from Cloak to tier 3:
- Need to inspect page state mid-flight (`evaluate_script` in chrome-devtools-mcp)
- Need to inject custom JS (Cloak does limited JS injection)
- Debugging a complex interaction (live driving is faster than scripted)

---

## Tier 3 fallthrough: chrome-devtools-mcp / Playwright

When Cloak also fails, route through chrome-devtools-mcp directly OR have Codex write a Playwright script. This is the most expensive tier — every action is a model call.

```python
# Codex authors this per AGENTS.md hard rule #5
# Sample Playwright shape for a 5-step scrape
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("<url>")
    page.fill("input[name=email]", "<email>")
    page.click("button[type=submit]")
    page.wait_for_selector(".dashboard")
    content = page.content()
    browser.close()
```

For one-off interactive sessions, drive chrome-devtools-mcp directly through MCP tools. For repeatable / scheduled work, Codex writes a Playwright script.

**Cost reminder:** a 20-action chrome-devtools-mcp flow is ~20 model calls. The same flow via Firecrawl interact is 1 service call with 20 actions. Use tier 3 sparingly.

---

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Selector not found | DOM differs from expectation | Use `firecrawl interact snapshot` to see the DOM; update selector |
| Action timed out | Page slow / network blip | Bump `--timeout`; check site is up |
| Page bot-checks mid-session | Detection scored up over actions | Add `wait` actions between clicks to look human; escalate to Cloak |
| Auth cookies expire | Long session | Shorter sessions, or refresh auth at start of each |
| Captcha appears | Triggered defenses | Can't solve programmatically. Push back to the user or try a different angle |

---

## Pairing patterns

- **`scrape` fails on bot-block → `interact --provider cloak --do "extract main content"`** — escalation pattern
- **`interact start` → multi-step flow → `extract`** — the auth/paginate/scrape pattern
- **`interact` for one page, then `scrape` for related URLs** — when only the entry needs interaction
- **`agent` instead of `interact`** when the multi-page work is structured extraction (agent handles navigation; interact handles arbitrary actions)

---

## See also

- [SKILL.md](../SKILL.md) — mechanic entry (cost ladder explained)
- [scrape.md](scrape.md) — tier-1 single URL (interact is the escalation tier)
- [agent.md](agent.md) — schema-driven alternative for structured extraction
- [crawl.md](crawl.md) — bulk extraction without interaction
