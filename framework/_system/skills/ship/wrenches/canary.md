---
name: ship-canary
description: Post-deploy canary monitoring wrench. Watches the live app for console errors, network failures, page-render failures, and visible regressions via chrome-devtools-mcp. Runs for a finite user-set window (default 30 min, max 24 hr) then stops. NO recurring schedule per AGENTS.md hard rule #1. Trigger phrases include "canary", "monitor the deploy", "watch production", "post-deploy check", "verify the deploy", "is production healthy".
---

# ship-canary — finite post-deploy monitoring window

After a deploy lands, the canary opens a watchful window on production. It periodically takes screenshots, checks console for errors, samples critical pages, and surfaces regressions. The window closes when it ends (no infinite loops, no recurring schedule).

Per AGENTS.md hard rule #1, this wrench is finite by design. The user triggers it; it runs; it ends.

---

## When to fire

- Auto-fires as part of post-deploy parallel dispatch from `land-and-deploy`
- Direct: "run a canary" / "monitor the deploy" / "watch production for 1 hour"
- After a hotfix to verify the fix took without breaking anything else

Don't fire when:
- Production isn't yet up (wait for `land-and-deploy` health check first)
- The user wants long-term monitoring (push back; that's a platform decision — Sentry, Datadog — not this wrench)
- The user asks for it on a non-production URL (allowed but flag: "Running canary on a preview URL — confirm?")

---

## Window options

Default: 30 minutes. Configurable via `--window`:

```bash
canary --window 30m       # default
canary --window 5m        # quick sanity check
canary --window 2h        # extended (e.g., after a risky deploy)
canary --window 24h       # max; pushes back if requested
```

Polling interval defaults to 2 minutes; configurable via `--interval`. Lower intervals mean more chrome-devtools-mcp calls (more cost).

---

## What canary checks each poll

1. **Console errors.** `list_console_messages` filtered to errors and warnings. Compare against a baseline of "expected" warnings.
2. **Network failures.** `list_network_requests` filtered to 4xx and 5xx. Investigate any new ones.
3. **Page render.** Hit the home page + a critical-path page (the user configures which); `take_snapshot` and verify expected content marker is present.
4. **Visual regression.** Optional: `take_screenshot` and diff against a pre-deploy baseline. Only run if the user asked for visual checks.
5. **Performance sample.** Optional: one `performance_start_trace` / `performance_stop_trace` per window. Compare against benchmark baseline.

Critical-path pages are configured per-project in CLAUDE.md or asked at first canary run.

---

## What canary does when it finds something

| Finding | Action |
|---|---|
| New JS error in console | Surface to the user immediately. Don't wait for window end. |
| New 5xx in network logs | Surface immediately. |
| Page render returns 4xx/5xx | Surface immediately. |
| Page render returns 200 but content marker missing | Surface immediately. |
| Visual regression (if enabled) | Surface with before/after screenshots. |
| Performance regression > threshold | Surface with metric deltas. |

Surfacing happens via the conversation, not via a separate notification channel. If the user isn't watching the session, the finding waits in conversation history — that's the trade-off of no autonomous notification per hard rule #1.

---

## Sequence

```
1. Read Deploy configuration block from CLAUDE.md for production URL + critical pages
2. Optionally read pre-deploy baseline from second-brain
3. Open chrome-devtools-mcp page on production URL
4. Start window timer
5. Loop until window expires:
   a. Sleep --interval
   b. Refresh page
   c. Check console (errors + warnings)
   d. Check network (4xx/5xx)
   e. Sample critical pages
   f. (Optional) Visual + perf check
   g. If finding: surface immediately, continue loop
6. Window ends:
   - Emit summary: findings count, severity breakdown, time window
   - Close chrome-devtools-mcp page
```

---

## Cost shape

- chrome-devtools-mcp poll = several model calls per cycle (navigate, snapshot, list_console, list_network, screenshot)
- Total = cycles × calls-per-cycle
- 30-min window at 2-min intervals = 15 cycles × ~6 calls = ~90 model calls
- 24-hr window at 5-min intervals = 288 cycles × ~6 calls = ~1700 model calls — large bill, push back if the user didn't think about it

Use the shortest window that gives the user the confidence he wants. 30 min covers most deploys.

---

## Recurring monitoring (NOT this wrench)

If the user wants ongoing production monitoring (24/7, alerts on anomalies), push back: that's not what canary does. Options to recommend:

- Sentry for error tracking
- Datadog / Honeycomb for metrics + traces
- Statuspage / Pingdom for uptime
- A Codex-authored Playwright script run on a CI schedule (mention but don't auto-build)

Canary is a finite window after a specific deploy. The user triggers each run.

---

## Pre-deploy baseline (optional)

For meaningful "is this new" detection, canary can compare against a pre-deploy baseline:

```bash
# Capture baseline before deploy
canary --baseline --window 5m  # captures normal-state errors, network, perf

# Stored at second-brain Actions/canary-baselines/<project>.json

# Then canary post-deploy diffs against it
canary --window 30m  # uses latest baseline automatically
```

Without baseline, every console warning is "new" and noisy. With baseline, only deltas surface. Worth running for projects the user ships to often.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| chrome-devtools-mcp can't reach prod URL | Network / firewall / cold start | Wait for cold start; if persistent, surface to the user |
| Every poll surfaces "new" warnings | No baseline | Capture baseline first; re-run |
| Window ran out without surfacing anything | Healthy deploy or interval too long | Both possible; check window summary |
| Costs ballooned | Long window + tight interval | Lower interval or shorten window next time |

---

## Off browse-daemon (per DECISIONS_LOCKED)

The old canary skill used a gstack browse daemon. That daemon is cut. This wrench drives chrome-devtools-mcp directly via the chrome-devtools plugin MCP tools (`mcp__plugin_chrome-devtools-mcp_chrome-devtools__*`, e.g. `mcp__plugin_chrome-devtools-mcp_chrome-devtools__take_screenshot`). For repeatable monitoring patterns the user wants to schedule via Codex `/goal`, Codex authors a Playwright script per AGENTS.md hard rule #5.

---

## See also

- [SKILL.md](../SKILL.md) — pipeline mechanic
- [land-and-deploy.md](land-and-deploy.md) — dispatches canary post-deploy
- [benchmark.md](benchmark.md) — paired post-deploy wrench (perf regression check)
- [pay-for-this.md](pay-for-this.md) — paired post-deploy wrench (paying-user audit)
- [`AGENTS.md`](../../../../AGENTS.md) — hard rule #1 (nothing runs on its own)
