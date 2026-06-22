# Changelog

## 2026-06-22 - YAGNI ladder, handoff sync, public push gate

- Added the YAGNI decision ladder to global coding Rule 2.
- Added the kit-sync-on-handoff ritual as second-brain end-session Step 7.
- Shipped the guard public-push gate with an externalized local denylist: `denylist.example.json` is tracked, real values stay in gitignored `denylist.local.json`.
- Added the `blog-write` skill.
- Generalized the operator GitHub owner handle in `scrub-rules.json` to a placeholder.

## 2026-06-20 - Public release prep refresh

- Re-synced the framework from live sources through `tools/sync-kit.ps1`; scrub gate passed clean.
- Refreshed the humanizer skill text from the live framework and rebuilt both `dist/` zips.
- Added the current global fan-out discipline to the shared harness reference.
- Added MIT license text and a root `.env.example` checklist for optional env-backed pieces.
- Verified `tools/scrub.py framework` and analytics-sites tests: 15/15 pass.

What changed in the workflow kit, newest first. After a `git pull`, read the top entry
to decide whether the new pieces are worth adopting into your own setup.

Format: each entry lists **Added / Changed / Removed** at the level of skills, hooks,
scripts, and docs â€” the things you'd actually choose to adopt or skip.

---

## 2026-06-13 â€” Validation hardening

A multi-agent adversarial validation pass (independent leak-hunt + tooling audit that
empirically proved the gate blocks) returned **GO / safe to share** with no must-fix leaks.
Applied its non-blocking polish so future syncs inherit it:

- Caught two residual tokens the first scrub missed: a hyphenated private-project variant and
  a foreign/old `phoen` username foil â†’ both now genericized + denylisted.
- Fixed the Phoenixâ†’"the user" grammar artifacts: `a Phoenix-triggered` â†’ `a user-triggered`
  (no more `a the user-`), sentence-initial capitalization (`The user`), and a doubled-word stutter.
- Portability: the username scrub is now derived from the runtime account, not hardcoded.
- Defense-in-depth: added denylist backstops (`lead_log`, `EWR`, `ai-projects-rebuild`) and
  excluded private dirs from the sync stage so they're never transiently written.

## 2026-06-13 â€” Comprehensive identity scrub + auto-generalization gate

Re-derived the entire `framework/` from pristine live sources through a new rules-driven
scrub, and added a **verification gate** so this can never regress.

**What changed**
- The original publish only swapped the operator's first name. A multi-category identity
  audit found much more that the names-pass missed and that survived into the shipped repo:
  home city/state (home city/state), a real client (`client_slug`) â€” *including their live
  domain and a GA4 property id baked into test fixtures* â€” the agency name (which the names-pass
  had mangled into "the user Web & AI"), competitor names, and the private project roster.
- All of it is now genericized: operator â†’ "the user", agency â†’ "Acme Web & AI", city â†’
  "Springfield", client â†’ "Example Co" / `example_client` / `example.com`, projects â†’
  `example-*`, `Odysseus` â†’ `reference-app`, the `TextP2P` vendor â†’ a generic `sms-leads`
  connector. Functional names the framework depends on (the `agentic-os` lock tool, the
  `analytics-sites` engine, the `apex` tier, ports) are explicitly **kept**.
- The design-library brand example is now a coherent generic brand (logo/mascot/palette
  craft retained; identity fields genericized).

**Verification**
- `tools/scrub.py` now runs an auto-generalization pass + a push-blocking verify gate: if any
  of ~22 identity patterns survive, the sync aborts and nothing is committed.
- The genericized `analytics-sites` test suite still passes (15/15) â€” the domain/name/id
  replacements are whole-file-consistent, so the tests stay green.
- Full-tree sweep: 0 username / surname / email / handle / city / client / project leaks.

## 2026-06-13 â€” Initial publish

First public cut of the kit. Privacy-scrubbed snapshot of the live workflow.

**Included**
- Full mechanic/wrench skill framework (`framework/_system/skills/`) â€” 215 files total.
- Cross-AI bridge hooks + secret-firewall (`framework/harness/hooks/`).
- The `codex-goal-dispatcher` autonomous-loop skill + templates (`framework/harness/skills/`).
- Cross-session file-lock and headless spawn args (`framework/agentic-os/`).
- Operating manual, skills index, decision map, reliability standard (top-level docs).
- Pamphlet + AI-agnostic implementation prompt for adoption.

**Scrub fixes** (vs. the original hand-built zip)
- Generalized two leftover operator-name residues to match the rest of the kit:
  `voice-corpus/phoenix/` â†’ `voice-corpus/<you>/` (content-forge humanizer wrench), and
  `PHOENIX DECIDES` â†’ `USER DECIDES` (ship review wrench). No other content changed.

**Verified clean**
- 0 real-username leaks, 0 secrets/keys/tokens, 0 vault content, 0 `.env`/`.pem`/`.key` files.
- The only "secret-pattern" matches in the tree are the secret-firewall's own detection
  regexes and documentation examples â€” not real credentials.

