# Analytics Sites — design spec

**Date:** 2026-06-08 (status updated 2026-06-12)
**Status:** engine built + tested (9/9) + live-OAuth-verified end-to-end 2026-06-09 (GSC data syncing live, real refresh tokens stored). Remaining: GA4 property selection, @Sites deploy, OAuth state CSRF validation (see worker.mjs handleCallback).
**Author:** Claude (architect). Implementation: Codex.

## What this is

Reusable, **company-agnostic bones** for spinning up a business-analytics dashboard, deployed as an **OpenAI Codex Site**. One engine; each company is a thin config + secrets. `example_client` is the first instance and proof. Once proven, the engine graduates into a skill via `skill-forge` (trigger: "make an analytics site for &lt;company&gt;").

The design target is the existing rendered shell: a blank dashboard where every KPI card reads **"Connect"**, you click a card, sign in with Google, authorize read-only access, and that card populates live.

## Locked decisions

1. **Deploy target:** OpenAI Codex Sites (`@Sites` available in the user's desktop app). Every Sites URL is production → **save a version → the user reviews → deploy**, `admins_only`.
2. **v1 live sources:** GA4 + Google Search Console. The other four (GBP, Vercel, SMS Leads, PageSpeed) ship as blank "Connect" cards, wired in a later pass.
3. **Connect UX:** blank by default. Click card → Google OAuth consent → authorize read-only → redirect back → card populates live in the deployed app.
4. **Auth method:** Sign in with Google (OAuth), read-only scopes. One free Google OAuth client, created once by the user (exact steps provided).
5. **Connectors:** a bulletproof, CLI-shaped, **free-only-guarded** framework (elevated from what Codex already built). No paid APIs — hard rule.
6. **Reliability:** built to `RELIABILITY_STANDARD.md` — owns its world, every source treated as absent/hostile until proven, fail-closed (a dead source renders a clean status card, never crashes the page).
7. **Roles:** Claude architects + spec-reviews; Codex implements + diff-reviews. Built via the Claude↔Codex bridge.

## Architecture — three layers

```
_system/skills/analytics-sites/          ← the reusable engine (and future skill body)
  engine/        Sites worker shell, OAuth handler, snapshot/render, free-only guard
  connectors/    one module per source (ga4, gsc, gbp, vercel, smsleads, pagespeed)
                 (v1 dashboard skeleton is inlined in engine/dashboard.mjs renderDashboard();
                  extract to a templates/ dir when themeable theming work starts — no templates/ on disk yet)
  SPEC.md        this file

projects/<company>-sites-analytics/       ← a thin instance
  company.config.json                     ← the only thing that varies per company
  .env.local                              ← per-company secrets (never in git, never in hosting.json)
  .openai/hosting.json                    ← Sites hosting descriptor (no secrets)
```

**Data flow:** `card click → OAuth connect → token stored server-side → connector.fetch() (free-only guarded) → normalized metric → card populates`.

## The connect / auth model (the hard part)

### OAuth
- Provider: Google. Authorization `https://accounts.google.com/o/oauth2/v2/auth`, token `https://oauth2.googleapis.com/token`.
- Params: `access_type=offline`, `prompt=consent` (to obtain a refresh token), `state` (CSRF + which source).
- Scopes (read-only): GA4 `analytics.readonly`; Search Console `webmasters.readonly`. (GBP later: `business.manage` — broader, deferred.)
- Redirect URI: `<app-origin>/oauth/callback`, where `<app-origin>` is configurable (localhost for dev, the Sites URL in prod).

### Worker routes (the engine)
- `GET /connect/:source` → builds the consent URL, redirects to Google.
- `GET /oauth/callback` → exchanges `code` for tokens, persists the **refresh token** keyed by source, redirects back to the dashboard.
- `GET /api/:source/data` → if connected, uses the stored token to call the source API and returns normalized JSON; else returns `{status:"connect"}`.
- `GET /health`, `GET /api/snapshot` (existing).

### Token storage — KEY BUILD INVESTIGATION
The dashboard is `admins_only` and shared: an admin connects once and data shows for all admin viewers, so the refresh token must live **server-side**, not in a per-viewer cookie. Codex must determine what persistence OpenAI Sites exposes (KV / Durable Object / secret store) and put token storage **behind a `TokenStore` interface** with two implementations: a local file store (dev) and the Sites-native store (prod). If Sites exposes no writable persistence, fall back to: admin connects → engine prints the refresh token → the user saves it as a Sites secret (documented), and the app reads it from env. The interface keeps either path from leaking into connector code.

### Google verification — avoids a multi-week block
Read-only analytics scopes are "sensitive," so an unverified OAuth app shows a warning screen. For an internal `admins_only` tool this is fine **without** full verification if the OAuth consent screen is in **Testing** mode and the user's (and any admin) email is added as a **test user**. Document this; it's what makes "works now" true.

### Redirect-URI ordering (chicken-and-egg)
1. Build + validate the whole flow **locally first** with redirect URI `http://localhost:8787/oauth/callback` registered on the OAuth client.
2. Then `@Sites` save → deploy to get the production URL.
3. The user adds `<sites-url>/oauth/callback` to the OAuth client's authorized redirect URIs and sets client id/secret as Sites secrets.
4. Connect works in prod.

## Connector framework

Uniform interface, one module per source:
```
{
  id, label,
  auth: { type: 'google_oauth', scopes } | { type: 'token' } | { type: 'none' },
  connectUrl(ctx) -> string,        // where the card click goes
  isConnected(ctx) -> bool,
  fetch(ctx) -> NormalizedMetric[], // free-only guarded
  healthcheck(ctx) -> { status, detail }
}
```
- Adding a source = drop a module + a `source-registry.json` row. No engine change. Connect UX is automatic.
- **Free-only guard** wraps every `fetch`: tier order `printing_press_cli → first_party_cli → local_export → included_account_api → free_public_api → mcp`; **blocks** `paid_api`, `metered_api_without_confirmed_free_quota`, `unknown_cost_api`. (Reuse Codex's `source-registry.json` + policy, moved into the engine.)
- Also exposed as a CLI for headless sync / future Printing-Press swap-in: `analytics-connect <source> --config company.config.json`.

### v1 connectors
- **ga4:** `POST analyticsdata.googleapis.com/v1beta/properties/{propertyId}:runReport`. v1 KPI: sessions (+ activeUsers, top pages). Free Google quota.
- **gsc:** `POST searchconsole.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query`. v1 KPI: clicks/impressions/CTR/position, top queries + pages. Free Google quota.

## Per-company config — `company.config.json`

```jsonc
{
  "company": { "name": "", "tagline": "", "domains": [],
               "brand": { "primary": "", "accent": "", "font": "", "logo": "" } },
  "access": "admins_only",
  "sources": {
    "ga4":      { "enabled": true,  "propertyId": "" },
    "gsc":      { "enabled": true,  "siteUrl": "" },
    "gbp":      { "enabled": false },
    "vercel":   { "enabled": false },
    "smsleads":  { "enabled": false },
    "pagespeed":{ "enabled": false }
  },
  "cards": ["ga4","gsc","gbp","smsleads","vercel","pagespeed"]
}
```
Secrets (OAuth client id/secret, refresh tokens) never go here — `.env.local` / Sites secrets only. Brand tokens drive light theming so company #2 isn't visually identical (deeper variety lands at skill-graduation; v1 keeps the current shell look).

## Card states

`connect` (blank default) → `connecting` (OAuth in flight) → `live` (data) → `error` (actionable detail, e.g. "PageSpeed quota exceeded — add key").

## example_client instance (first proof)

- Refactor existing `projects/example_client_sites_analytics/` to consume the engine + `example_client.config.json` (reuse Codex's worker/CLI/policy; don't discard).
- Config: name "Example Co", tagline "Mobile hybrid battery repair and replacement", GA4 `propertyId`, Search Console `siteUrl`.
- Wire GA4 + Search Console live via Google OAuth.
- Deploy via `@Sites`: save → the user reviews → deploy `admins_only`.

## Build order & verification

1. **Engine + connector framework + OAuth handler + TokenStore interface** — unit: free-only guard blocks a paid/unknown endpoint; OAuth URL builds with correct scopes.
2. **GA4 + GSC connectors** — verify: real data fetched against the user's account locally; normalized output matches card contract.
3. **example_client instance** — verify: blank shell renders; click GA4 → Google sign-in → authorize → card populates **locally** at `localhost:8787`.
4. **Sites deploy** — `@Sites` save → review → deploy; register prod redirect URI + secrets; confirm connect+populate in prod.

Each step independently verifiable (full-stack: source API → connector → snapshot/route → card render → screenshot).

## the user's one-time setup (his critical path; can run in parallel with the build)

Create a free Google OAuth client (exact click-steps delivered separately): Google Cloud project → enable Analytics Data API + Search Console API → OAuth consent screen (External, **Testing**, add your email as **test user**) → Credentials → OAuth client (Web) → add redirect URIs `http://localhost:8787/oauth/callback` (now) and the Sites URL later → copy client id + secret to `.env.local`. Zero cost.

## Graduation to a skill

After the instance is live, `skill-forge` wraps the engine as a skill, placed per the Skill Law (likely a wrench under `build` or `design-studio`, or standalone). Reuse-first design now → skill-ification is packaging, not a rewrite.

## Out of scope for v1 (YAGNI)

- Live connectors for GBP / Vercel / SMS Leads / PageSpeed (blank cards now; wired later).
- Full per-company theming variety (config carries brand tokens; rich theming at graduation).
- Any scheduled/automatic sync (manual/triggered only — AGENTS hard rule #1).

## Open risks

- **Sites persistence for refresh tokens** — the one real unknown; `TokenStore` interface + documented secret-fallback de-risks it.
- **OAuth verification** — mitigated by Testing-mode + test users for an internal tool.
- **Sites server-side capability** — assumes Sites runs the Worker's OAuth/data routes (consistent with Sites being "interactive hosted apps with auth + data"); confirm early in build step 1.
