---
name: ship-pay-for-this
description: Post-deploy paying-user audit. Drives the live app via chrome-devtools-mcp as if the user were considering a $20/mo subscription — clicks the nav, tries the CTAs, fills a form, sniffs out demo data, times the loads. Emits a "would I pay for this?" verdict with score, screenshots, and concrete frictions. Severe failures auto-spawn fix tasks. Skips silently if no live URL is configured. Trigger phrases include "pay for this", "user audit", "would I pay", "live audit", "deploy audit", "test it like a customer", "be a user", "walk through as a paying customer".
---

# ship-pay-for-this — paying-customer audit

The blunt question: if the user saw this app today as a stranger considering a paid subscription, would he pay? This wrench walks the live deploy with that frame, surfaces friction, and returns a verdict.

Different from `qa`: qa is exhaustive bug-finding. `pay-for-this` is the gut-check first-impression audit, focused on the customer journey from "I just landed on the home page" to "I'm reaching for my credit card." Two different jobs.

---

## When to fire

- Auto-fires as part of post-deploy parallel dispatch from `land-and-deploy`
- Direct: "pay for this" / "would I pay $20/mo" / "live audit" / "walk through as a customer"
- After a major feature launch when the UX matters more than the bug count
- Before showing the app to a real customer (the user wants a sanity check first)

Don't fire when:
- No production URL configured (skip silently — log a note that it skipped, no error)
- The change is doc-only / backend-only / no user-visible diff
- `qa` is already running (one audit at a time on the live app; pay-for-this is more focused than qa)

---

## The walk

The audit follows a paying-customer arc, not an exhaustive test plan:

1. **Land on home page.** First impression. What's the value prop? How fast does it load? Does it look credible?
2. **Skim the nav.** Is structure obvious? Where's pricing? Where's docs/help?
3. **Click the primary CTA.** Does it work? Does it route somewhere useful? Does it feel slow?
4. **Read the pricing page.** Are tiers clear? Is there a free trial? Is the differentiation obvious?
5. **Try the signup flow.** Fill the form. Submit. Did it work? Is there demo data? Did the onboarding teach me anything?
6. **Walk the core feature.** Once "in," does the main thing actually do its main thing? Does it feel polished or feel like a v0.1?
7. **Trigger some edges.** Click 3-4 random things. Do they work? Empty states? Error handling?
8. **Final read.** Would I pay $20/mo for this right now? Why or why not?

---

## Scoring rubric (0-10)

The verdict isn't a vibe — it's a scored rubric the user can defend:

| Dimension | Weight | What's a 10 |
|---|---|---|
| **First impression** (home page in 5s) | 2 | Clear value, polished, fast |
| **Nav clarity** (find anything in 3 clicks) | 1 | Pricing / docs / signup all obvious |
| **CTA experience** (the primary action works smoothly) | 2 | Fast, clear feedback, lands somewhere useful |
| **Pricing clarity** (would I know what I'm buying) | 1 | Tiers obvious, no surprises, trial available |
| **Signup + onboarding** (zero-to-hero path) | 2 | Smooth, fast, teaches something |
| **Core feature polish** (the main thing works well) | 2 | Reliable, fast, feels finished |

Composite score is weighted average. Threshold for "would pay" is 7.0. Below that gets a specific friction list.

---

## Report shape

```markdown
## Paying-customer audit — example.app — 2026-05-28 14:35

### Composite score: 7.4 / 10 — Likely yes, conditional on the frictions below

### Per-dimension
| Dimension | Score | Notes |
|---|---|---|
| First impression | 8 | Home loads in 1.8s, hero is clear, polished. |
| Nav clarity | 6 | "Pricing" is in the footer, not the nav. Cost me a tab. |
| CTA experience | 8 | Sign-up form works smoothly; redirect feels fast. |
| Pricing clarity | 7 | Tiers OK but no annual discount shown. |
| Signup + onboarding | 9 | Zero friction. Skipped the wizard via "Show me later." |
| Core feature polish | 6 | The main editor lags on first keystroke (~250ms). Second-time fine. |

### Frictions found (would lower the verdict)
1. **Pricing in footer, not nav** — costs me a tab. (Nav clarity)
2. **First-keystroke editor lag** ~250ms — feels janky on first try. (Core feature polish)
3. **No annual pricing option** — likely losing some yes-but-cheaper buyers. (Pricing clarity)

### Would the user pay $20/mo? Likely yes, but #2 is the kind of thing that loses subscriptions on the second day.
```

If composite is below 4, auto-spawn fix tasks. Between 4-7, surface for the user's call. Above 7, ship's verdict is positive and no fixes auto-spawn.

---

## Auto-spawn fix tasks (severe failures only)

For frictions that score that dimension below 4, the wrench can spawn a fix task back through the qa lane (Codex `/goal` for sustained fix iteration). Threshold:

- Any dimension scoring < 4 → automatic fix task
- 2+ dimensions scoring < 6 → surface for the user's call on whether to spawn

Don't auto-spawn fixes on cosmetic frictions or matters of opinion. The wrench is opinionated but should be conservative on auto-firing fix work.

---

## Sequence

```
1. Read Deploy configuration block for production URL (skip silently if not set)
2. Open chrome-devtools-mcp page on production URL
3. Walk the 8-step arc, capturing:
   - Screenshots at each step
   - Load times (performance_start_trace / stop_trace)
   - Console errors / network failures
   - DOM snapshot at key states
4. Score each dimension based on observations
5. Compute composite
6. Assemble report
7. If severe failure → auto-spawn fix tasks
8. Surface to the user
9. Close chrome-devtools-mcp page
```

---

## Cost shape

- One full walk = ~15-25 chrome-devtools-mcp calls (navigate, snapshot, screenshot, click, fill across the 8 steps)
- One run per ship = bounded cost
- Auto-spawned fix tasks add Codex `/goal` cost (Codex Pro absorbs)

Much cheaper than `qa` because it's the customer-arc focus, not exhaustive path coverage. Run it on every deploy without thinking about cost.

---

## Off browse-daemon (per DECISIONS_LOCKED)

Old `pay-for-this` used a gstack Stop hook auto-firing post-deploy via a browse daemon. Cut. This wrench now drives chrome-devtools-mcp directly. Triggered by `land-and-deploy`'s post-deploy dispatch, not by a settings.json hook.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Walk stalls on signup form | Form requires email verification | Use a test email pattern; surface the friction in the report |
| Auto-spawned fix task is wrong | Score was misjudged | Surface and let the user tune rubric weights for the project |
| Score consistently low | Project genuinely needs work | Use the report as input for plan-room |
| Score consistently high | Threshold is loose, or app is genuinely good | Tune threshold per project; don't inflate scores to validate |

---

## Pairing patterns

- After `land-and-deploy` → pay-for-this auto-fires
- After major feature launch → the user triggers direct
- pay-for-this surfaces UX issue → escalate to `qa` for systematic testing if pattern emerges
- Pair with `benchmark` — both run post-deploy, both surface different angle on "is this good"

---

## See also

- [SKILL.md](../SKILL.md) — pipeline mechanic
- [land-and-deploy.md](land-and-deploy.md) — dispatches pay-for-this post-deploy
- [qa.md](qa.md) — escalation when pay-for-this surfaces patterns needing deeper test
- [canary.md](canary.md) / [benchmark.md](benchmark.md) — paired post-deploy wrenches
