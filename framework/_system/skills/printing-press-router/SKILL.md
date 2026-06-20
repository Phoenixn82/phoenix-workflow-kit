---
name: printing-press-router
description: >-
  ROUTING SKILL — fires whenever any skill needs to talk to a third-party API,
  website, or service. Enforces Mike Van Horn's CLI > API > MCP tier ladder.
  Checks the printing-press library catalog first; if no entry exists, generates
  a Go CLI via /printing-press; falls back to MCP/raw-API only if the CLI tier
  fails. Use this skill BEFORE wiring any new MCP server, BEFORE writing raw
  HTTP calls, and BEFORE adding a new integration to a project. Triggers:
  "I need to talk to <service>", "add integration for X", "scrape website Y",
  "wire up <API>", any skill that names an external service.
domain: OPS
cadence: SKILL
prompt_template: |
  Route the integration request: {input}
  Run the tier-1-CLI workflow:
  1. Check printing-press-library catalog (npx -y @mvanhorn/printing-press list | search)
  2. If hit: install via npx -y @mvanhorn/printing-press install <slug>
  3. If miss: fire /printing-press <service-or-url>
  4. Only fall back to MCP/raw-API if the CLI tier explicitly fails (websocket-only, hostile bot detection, ToS forbids sniffing)
input_label: Service, API, URL, or integration name
allow_in_packages:
  - my-agentic-os
estimated_tokens: 60000
---

# Printing Press Router

Default routing layer for third-party integrations. Mike Van Horn's tier ladder: **CLI > API > MCP**.

## When this fires

ANY time a skill needs to:
- Talk to a SaaS API (Notion, HubSpot, Stripe, Linear, etc.)
- Scrape a website without a public API (ESPN, Allrecipes, school.so)
- Add a new MCP server to a project
- Wire a new integration into the apex orchestrator (`project-orchestrator`) for a build
- Replace an existing MCP with a more agent-native interface

## The workflow (do this exactly)

### Step 1 — Check the library first

The library currently holds 68 CLIs across 16 categories. Search before building.

```bash
npx -y @mvanhorn/printing-press search <topic>
npx -y @mvanhorn/printing-press list
```

Or grep `registry.json` directly if you've cloned the library.

### Step 2 — Install if hit

```bash
npx -y @mvanhorn/printing-press install <slug>
```

This installs:
- The Go binary (`<slug>-pp-cli`) to `$GOBIN`
- The matching Claude Code skill to `~/.claude/skills/pp-<slug>/`
- Slash form: `/pp-<slug>` (immediately available in any Claude Code session)

Multi-install:
```bash
npx -y @mvanhorn/printing-press install starter-pack    # ESPN + flight-goat + movie-goat + recipe-goat
npx -y @mvanhorn/printing-press install espn sentry dub
```

Skill-only (no binary):
```bash
npx skills add mvanhorn/printing-press-library/cli-skills/pp-<slug> -g
```

### Step 3 — Generate a CLI if miss

From inside Claude Code (NOT bash):

```text
/printing-press <api-name>          # by API name
/printing-press <url>               # by URL — sniffs browser
/printing-press <api> codex         # 60% fewer Opus tokens via Codex CLI (PREFERRED for cost)
/printing-press --har ./capture.har # from HAR file
```

The press runs a 9-phase pipeline (resolve → research → ecosystem-absorb → browser-sniff → generate → build → shipcheck → smoke → polish). Output: `<api>-pp-cli` binary + `<api>-pp-mcp` server + `/pp-<api>` skill + research manuscript + scorecard.

### Step 4 — Use the printed skill

Once installed:
```text
/pp-espn lakers score
/pp-flightgoat sea to lax dec 24 nonstop
/pp-linear sql 'blocked issues'
```

Skills support universal flags inherited from the press: `--json`, `--select`, `--csv`, `--compact`, `--quiet`, `--dry-run`, `--no-cache`. Auto-JSON when piped. Typed exit codes (0 success / 2 usage / 3 not-found / 4 auth / 5 API / 7 rate-limit).

### Step 5 — Publish back (optional)

After printing a useful new CLI, contribute it back:

```text
/printing-press-publish <slug>
```

This validates and opens a PR against `mvanhorn/printing-press-library`.

## Fallback rules — when to NOT use printing-press

CLI tier is the default. Use raw API or MCP only when:

- The service is **websocket-only** or **gRPC-only** (the press generates HTTP-based clients)
- The service has **hostile bot detection** that defeats the browser-sniff gate (Cloudflare strict mode, etc.)
- The service's **ToS forbids automated reverse-engineering** (consult the rule before printing)
- The skill needs **IDE-discovery semantics** (Cursor / Windsurf MCP integrations, etc.) — keep MCP for those
- **Chrome control** specifically — keep `chrome-devtools-mcp` because the press doesn't replace browser-control MCPs

## Cost discipline

Every print run is Opus-heavy by default. ALWAYS pass `codex` to offload Phase 3 codegen to Codex CLI:

```text
/printing-press notion codex
```

This respects the user's three-brain-router conservation rule (Opus for judgment, Codex/Sonnet for codegen).

## Prerequisites (one-time)

Verify these before the first print:

```bash
go version              # need 1.26.3+
node --version          # need 18+
claude --version        # need Claude Code CLI
go install github.com/mvanhorn/cli-printing-press/v4/cmd/printing-press@latest
gh skill install mvanhorn/cli-printing-press --agent claude-code --scope user
```

## Conflicts with existing stack

The user already runs MCPs for: supabase, firecrawl, vercel, notebooklm, chrome-devtools, etc. After installing a `pp-<x>` for the same service:

- **Prefer pp-CLI for**: read/sync/SQL queries, batch ops, anything piped or scripted
- **Keep MCP for**: IDE discovery (Cursor/Windsurf), Chrome control, anything where the MCP exposes capabilities the CLI doesn't

## Provenance

Each printed CLI ships with `.printing-press.json` containing the source spec, run ID, scorecard, and the model that generated it. Inspect with:

```bash
cat ~/printing-press/library/<api>/.printing-press.json
```

## Catalog refresh

The library publishes via `release-please` per-CLI tags. To check for updates:

```bash
npx -y @mvanhorn/printing-press list --updates
npx -y @mvanhorn/printing-press update <slug>
```

Run this as a user-triggered check (e.g. when the user asks for a catalog refresh) — never as an unattended nightly job (AGENTS.md hard rule #1: nothing runs on its own).

## References

- Library catalog: https://printingpress.dev
- cli-printing-press: https://github.com/mvanhorn/cli-printing-press
- printing-press-library: https://github.com/mvanhorn/printing-press-library
- Research notes: `C:/Users/<you>/Downloads/printing-press-research/`
- Author: Matt Van Horn (@mvanhorn)
- Co-creator: Trevin Chow (@trevin on X)
