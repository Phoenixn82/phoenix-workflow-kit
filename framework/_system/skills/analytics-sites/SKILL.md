---
name: analytics-sites
description: Engine for reusable business analytics sites and client analytics dashboards. Trigger phrases: "business analytics site", "analytics dashboard for a client", "client KPI dashboard", "make an analytics site for <company>".
---

# analytics-sites - business analytics dashboard engine

Reusable, company-agnostic engine for spinning up business analytics dashboards as OpenAI Codex Sites. The first proof is `projects/example_client_sites_analytics`; the reusable engine lives here under `_system/skills/analytics-sites/`.

## What it is

- `SPEC.md` is the design source.
- `engine/` contains the worker shell, OAuth/data routes, dashboard renderer, snapshot flow, free-only guard, and TokenStore abstraction.
- `connectors/` contains source policy/connector code for GA4, GSC, GBP, Vercel, SMS Leads, and PageSpeed-style sources.
- `tests/` covers the engine; `package.json` exposes `npm test` as `node --test tests/*.test.mjs`.

## Status

Engine present, tests present, and SPEC says the Example Co proof was live-OAuth-verified. This has not yet been routed-tested as a skill, so verify before first use.

## Entry points

1. Read `SPEC.md`.
2. For engine work, run `npm test` from this directory.
3. For a client instance, start from the existing `projects/example_client_sites_analytics` shape: company config, local env, sync/build/dev scripts, then Codex Sites save/review/deploy.

## Guardrails

- No paid APIs by default. Preserve the free-only connector policy.
- Runtime secrets stay in `.env.local` or Sites secrets, never in hosting descriptors or git.
- Codex Sites deployments are production URLs; save/review before deploy.