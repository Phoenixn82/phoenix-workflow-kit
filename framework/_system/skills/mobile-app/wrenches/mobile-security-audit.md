---
name: mobile-security-audit
description: Pre-launch security-prompt audit for a vibe-coded Expo/RN app — run a reusable Claude Code security-audit prompt iteratively (clearing context between passes) to kill low-hanging-fruit vulns, plus the mobile-specific risk model (exposed API keys, client trust boundary, RLS gaps, Edge Function as the secret boundary). Codex is the default code lane for applying the fixes (AGENTS.md rule #5); Claude runs the audit, reads the tier list, and decides what ships. Routes deep infra/scale security to cso. Fires on "security audit before launch", "is my app secure", "check for exposed keys", "pre-launch security pass".
---

# mobile-security-audit — the 80/20 pre-launch security pass nobody does

This is the one final step ~99% of the vibe-coded economy skips because it takes time and isn't sexy — and it's the 1% who do it whose apps scale and make money. You feed Claude Code a large pre-written security-audit prompt that methodically and consistently checks the major low-hanging fruit, get back a ~50-60 finding tier list ranked by severity, fix everything, then **clear context and re-run the whole prompt from scratch 2-3 times** so a fresh, context-free instance catches the vulnerabilities the prior pass created or missed. The goal is not perfection (impossible for a solo/small team) — it's getting an attacker to look at your app and think "not worth hacking, move to the next less-secure one."

**Cardinal: Do it AT ALL > do it perfectly.** "The most important thing is not to get it 100% correct. The most important thing is just to do it." Aim for ~90% satisfied after two passes, not 100% secure.

**Cardinal: Re-run with a FRESH context every pass.** Fixing one security problem creates another somewhere else. Clear conversation history to zero tokens between runs so a future Claude can spot issues a past Claude created. Findings are NOT stable across runs — green items flip to broken (Nick's `getUser` vs `getSession` broke on the second pass). That instability is the whole reason you re-run.

**Cardinal: Audit LAST, on a verified-ready app.** Only run after the app passed all three testing prongs (Chrome → Expo → physical phone) and you've 100% verified it's basically launch-ready. This sits between finishing AI/API functionality and app-store deployment — not before.

**Cardinal: Claude reads the tier list and decides; Codex applies the fixes.** Per AGENTS.md rule #5, the actual code edits are Codex's lane. Claude runs the audit, interprets severity, and makes the ship/no-ship call. Hand the findings to Codex via `router → Codex` (or the `codex` skill) to implement "move yellows and reds to greens."

---

## Phase 1 — Pre-flight (do these before pasting anything)

1. **Verify the app is launch-ready.** All three testing prongs green: browser/Chrome, Expo, physical phone via Expo. If it isn't ready, you're auditing a moving target — stop and finish testing first (see `expo-go-test.md`).
2. **Clear all conversation history.** Start a fresh Claude Code instance with **zero context** of the prior build conversation. The audit prompt is large; you want a clean ~0-token start so it runs clean and so the instance has no memory of how the code was built.
3. (Optional) `Ctrl+O` toggles Claude Code's detailed under-the-hood view so you can see what documentation/context is being loaded (works on Mac and PC).

---

## Phase 2 — The audit prompt

The reusable audit prompt comes from Nick's older "security for vibe-coded apps" module — a comprehensive list plus formatting of ways to identify and then solve the major low-hanging fruit. Paste the **entire** pre-written string in one shot (Cmd+V / the giant block) and let it run. The prompt methodically checks, at minimum, these named vulnerability patterns:

- **Hallucinated packages** — AI-invented dependencies that don't exist / are typosquats.
- **Missing server-side validation** — trusting client-supplied data; no startup/input validation.
- **Default-open database policies** — tables shipped without restrictive RLS.
- **Hard-coded secrets** — API keys/tokens baked into client code or committed.
- **Inconsistent auth/OAuth middleware** — protected routes not actually protected; mixed auth on the mobile app.

> If you have the original "vibe coding security page" / security-audit-prompt section saved, copy from the top down to and including the **"security audit prompt"** section verbatim — that exact text is the tool. This specific prompt is **one of many** valid audits; the value is in running a methodical one consistently, not in this exact wording.

### Output format — the tier list

Claude returns ~50-60 findings as a tier list. Each finding carries these exact fields:

- **finding number**
- **severity** — `critical` / `high` / `medium` / `low`
- **category**
- **location**
- **CWE** (Common Weakness Enumeration) reference — the catalogued common ways people get access to apps
- **status** — `pass` / `partial` / `fail` per check

Most findings should come back as **partials** rather than total fails — that's a good sign. Real failures Nick hit even on a simple habit tracker:

| Check | First-pass status |
|---|---|
| Git ignore coverage | partial |
| Console error leaks | partial |
| Startup validation | **fail** (complete) |
| Protected API routes | **fail** (major) |
| Hard-coded secrets | **pass** (key was only in the env file / stored in Supabase itself, nowhere else) |

---

## Phase 3 — Fix loop (iterate 2-3×, fresh context each time)

**Pass 1 — fix and verify:**
```
Run through and fix all of these errors end to end. After you're done, test and ensure they're 100% solved.
```

**Then clear context entirely and re-run the full audit prompt from scratch.** A fresh Claude instance with zero memory of the prior fixes will catch newly-generated vulns.

**Pass 2 — fix partials + report new vulns:**
```
Great work. Fix all things even if they're partial. Once sorted, let me know if the changes produced new vulnerabilities.
```

**Implementation directive Codex runs (move the colors):**
```
great work. run through and implement all changes to move the newly... move any yellows or reds to greens pass
```
Then run the audit **one more time** to confirm the greens held.

On the second pass most prior failures flip to passes/partials with low severities (startup validation went `fail → partial`). Watch for regressions: `getUser` vs `getSession` broke on the second pass, and Git ignore coverage hadn't changed at all. **Stop when ~90% satisfied.** A couple of audit passes beats hand-reviewing every line yourself — humans make mistakes too.

---

## Mobile-specific risk model (what to actually verify)

The phone is an **untrusted client**. Treat everything that ships to the device as readable by an attacker.

1. **The Edge Function is the secret boundary.** The Anthropic/Claude API key (and any provider key) lives **server-side only**, inside a Supabase Edge Function, never in the Expo/RN bundle. If an AI feature calls a model directly from the client, the key is exposed — route it through the function. See `edge-fn-claude-ai.md`.
2. **Keys live in exactly two safe places.** The env file (gitignored) and Supabase itself. Nowhere else. Hard-coded secrets check passes only when the key was pasted into the env file or stored in Supabase and nowhere in client code.
3. **RLS on every table, default-deny.** `sessions`, `trees`, `user_stats` (or whatever your schema is) must enforce Row Level Security so user A can never read user B's rows. Enable automatic RLS at project creation; verify with the Supabase MCP `get_advisors` (security lint). See `supabase-mobile.md`.
4. **Server-side validation / protected routes.** Never trust the client to enforce auth or shape data. Auth middleware must be consistent across every protected route. "Protected API routes" was a *major* fail on a simple app — assume it's failing until proven.
5. **Expensive-operation abuse (token-burn DoS).** An attacker who just wants to take you down can re-run an expensive operation (e.g., an AI call) over and over to burn your Claude/API tokens. Rate-limit and cap server-side. Leaked tokens let attackers run your bill into the millions/tens of millions, and providers are only *loosely* able to reimburse it — "at the end of the day it is your fault."
6. **Git ignore coverage + console error leaks.** Ensure `.env`, keys, and secrets are gitignored; strip verbose error/console output that leaks internals. Both came back partial — re-check them every pass (Git ignore coverage notably did NOT improve between passes unless explicitly pushed).

---

## Stakes (why this matters, brief)

- An insecure app that leaks usernames/passwords to the dark web destroys your reputation **and** exposes you to massive fiduciary liability.
- Government regulation around sensitive data — personal health data, personal financial data, OAuth connectors tied to bank-account sign-in — puts you on the hook for serious money. Be **extra** careful past a simple habit tracker.
- Never assume the app is 100% secure. Even if you think it is, it isn't — there's probably still a loophole.

---

## What this wrench does NOT do

- **Deep infrastructure / scale security review** → route to **`cso`** (standalone keeper). This wrench is the 80/20 low-hanging-fruit pass. Nick is "not a lawyer and not a security specialist" — the prompt is a leverage tool, not a security team. If you're scaling to hundreds of thousands of users, sensitive-data, or regulated domains, get an actual human review team to minimize attack surface; `cso` is the in-house version of that escalation.
- **Apply the code fixes itself** → that's **Codex's** lane (`router → Codex`, or the `codex` skill). Claude runs the audit, reads the tier list, decides ship/no-ship.
- **Live RLS/auth/Edge-Function setup** → `supabase-mobile.md` (RLS, auth) and `edge-fn-claude-ai.md` (server-side key boundary); live ops via the **Supabase MCP** (`get_advisors`, `apply_migration`, `execute_sql`, `deploy_edge_function`).
- **On-device testing that must precede the audit** → `expo-go-test.md`.
- **App-store submission / privacy policy / store metadata** → `ship-to-stores.md` (the audit happens *before* this).
- **Git/commit/CI plumbing for the fixes** → the `ship` mechanic.

---

## See also

- [expo-go-test.md](expo-go-test.md) — the three-prong device test loop you must pass before auditing.
- [supabase-mobile.md](supabase-mobile.md) — RLS, tables, mobile auth flows (the DB trust boundary).
- [edge-fn-claude-ai.md](edge-fn-claude-ai.md) — the Edge Function as the server-side secret boundary for AI features.
- [ship-to-stores.md](ship-to-stores.md) — the release pipeline that comes after a clean audit.
- [expo-scaffold.md](expo-scaffold.md) · [rn-expo-ui.md](rn-expo-ui.md) — the build/UI context for the app being audited.
- [../SKILL.md](../SKILL.md) — the mobile-app mechanic dispatcher.
- [../../cso/SKILL.md](../../cso/SKILL.md) — deep infrastructure security audit / scale-grade review.
- [../../ship/SKILL.md](../../ship/SKILL.md) — git/commit/tests/PR/CI for landing the fixes.
- [../../router/SKILL.md](../../router/SKILL.md) — routes the actual fix implementation to Codex (AGENTS.md rule #5).
