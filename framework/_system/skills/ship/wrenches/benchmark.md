---
name: ship-benchmark
description: Performance regression detection wrench. Baselines page-load time, Core Web Vitals (LCP, INP, CLS, FCP, TTFB), and bundle size. Compares before/after on each ship. Tracks trends in second-brain. Off the cut gstack browse daemon; uses chrome-devtools-mcp performance traces directly. Trigger phrases include "benchmark", "perf check", "did this slow things down", "page speed", "web vitals", "bundle size", "load time check", "performance regression".
---

# ship-benchmark — perf regression on every ship

When ship lands a change, benchmark answers: did this make the site slower? Compares post-deploy metrics against a stored baseline. Surfaces regressions with magnitude. Trends stored in second-brain for cross-deploy visibility.

---

## When to fire

- Auto-fires as part of post-deploy parallel dispatch from `land-and-deploy`
- Direct: "benchmark this" / "did the deploy slow things down" / "perf check"
- Before a deploy to establish a baseline (the user triggers explicitly)

Don't fire when:
- No baseline exists and the user doesn't want one (first run is informational only)
- The user wants live monitoring not a snapshot (that's `canary`, different lane)
- The change is doc-only / config-only / has zero runtime impact

---

## What it measures

| Metric | Why it matters | Threshold (default) |
|---|---|---|
| **LCP** (Largest Contentful Paint) | User-perceived load | Good < 2.5s; alert if regressed by > 200ms |
| **INP** (Interaction to Next Paint) | Interactivity | Good < 200ms; alert if regressed by > 50ms |
| **CLS** (Cumulative Layout Shift) | Visual stability | Good < 0.1; alert if regressed by > 0.05 |
| **FCP** (First Contentful Paint) | Perceived speed | Good < 1.8s; alert if regressed by > 200ms |
| **TTFB** (Time to First Byte) | Server speed | Good < 800ms; alert if regressed by > 100ms |
| **Bundle size** (JS + CSS + images) | Download cost | Alert if total grew by > 10% |

Thresholds configurable per project in CLAUDE.md. Default thresholds are sensible for most sites.

---

## Sequence

```
1. Read Deploy configuration block for production URL + critical pages list
2. Load latest baseline from second-brain Actions/perf-baselines/<project>.json
3. For each critical page:
   a. chrome-devtools-mcp navigate
   b. performance_start_trace / performance_stop_trace
   c. performance_analyze_insight for LCP, INP, CLS, FCP, TTFB
   d. Sample bundle size from network logs (total JS + CSS + images)
   e. Record current values
4. Diff current vs baseline:
   a. Per metric, compute delta + percent change
   b. Flag metrics that crossed threshold
5. Update second-brain trend log
6. Surface report
7. Update baseline IF the user says the new state is the new normal
```

---

## Baseline management

Baselines live at `_system/second-brain/Actions/perf-baselines/<project>.json`:

```json
{
  "url": "https://example.app",
  "captured_at": "2026-05-28T14:00:00Z",
  "commit_sha": "abc1234",
  "pages": {
    "/": { "LCP": 1.8, "INP": 120, "CLS": 0.04, "FCP": 1.2, "TTFB": 320, "bundle_kb": 245 },
    "/pricing": { "LCP": 2.1, "INP": 130, "CLS": 0.02, "FCP": 1.4, "TTFB": 340, "bundle_kb": 245 }
  }
}
```

**When to update the baseline:**
- After a deploy that intentionally improved perf (compress to new normal)
- After the user says "this is the new baseline" explicitly
- NOT automatically on every deploy — that would silently absorb regressions

**When to NOT update:**
- A regression the user wants to track (let it stay visible against the old baseline)
- A change that's still being investigated

---

## Report format

```markdown
## Benchmark report — 2026-05-28 14:23

**Baseline:** commit abc1234 (2026-05-15) vs current commit def5678

### Home page (/)
| Metric | Baseline | Current | Δ | Status |
|---|---|---|---|---|
| LCP | 1.8s | 1.9s | +100ms | OK (under threshold) |
| INP | 120ms | 145ms | +25ms | OK |
| CLS | 0.04 | 0.04 | 0 | OK |
| FCP | 1.2s | 1.2s | 0 | OK |
| TTFB | 320ms | 380ms | +60ms | OK |
| Bundle | 245KB | 268KB | +9.4% | OK (under 10%) |

### Pricing page (/pricing)
| ... |

### Verdict
No regressions over threshold. Bundle grew 9.4% — under threshold but worth watching.
```

If any metric crosses threshold, that line gets flagged. The verdict summarizes the overall picture.

---

## Trend tracking

Each run appends to `_system/second-brain/Actions/perf-trends/<project>.jsonl`:

```jsonl
{"date": "2026-05-15", "commit": "abc1234", "page": "/", "LCP": 1.8, "INP": 120, ...}
{"date": "2026-05-28", "commit": "def5678", "page": "/", "LCP": 1.9, "INP": 145, ...}
```

The user can query this for "what's our LCP trend over the past month" — surfaces creeping regressions that pass per-deploy threshold but accumulate.

---

## Cost shape

- chrome-devtools-mcp performance trace = several model calls per page (navigate, start_trace, stop_trace, analyze)
- N critical pages × ~5 calls per page = bench cost
- Default 2 critical pages = ~10 model calls per benchmark run
- Cheap unless the user asks for 20+ pages

---

## Off browse-daemon (per DECISIONS_LOCKED)

The old benchmark used a gstack browse daemon. Cut. This wrench drives chrome-devtools-mcp directly. For automated perf monitoring on a schedule, Codex writes a Playwright script per AGENTS.md hard rule #5 (Codex writes; Claude specs).

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| LCP wildly varies between runs | Network / CDN variability | Run 3 samples, take median |
| INP can't be measured | No user interaction simulated | Use chrome-devtools-mcp interaction or skip INP this run |
| Bundle size jumped but visual perf same | Compression / minification change | Note as info, not regression |
| Baseline file missing | First run | Treat as "informational" run; ask the user if this should become the baseline |
| Threshold too tight, false alarms | Sensitive thresholds | Tune per project in CLAUDE.md |

---

## See also

- [SKILL.md](../SKILL.md) — pipeline mechanic
- [canary.md](canary.md) — paired post-deploy (monitoring window)
- [pay-for-this.md](pay-for-this.md) — paired post-deploy (UX walkthrough)
- `chrome-devtools-mcp:debug-optimize-lcp` (plugin skill, invokable by name) — when LCP is the regression to investigate
