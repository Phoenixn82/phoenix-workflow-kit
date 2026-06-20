---
name: content-forge-humanizer
description: Redirect. The humanizer outgrew a single wrench and is now a standalone mega-mechanic. Trigger phrases ("humanize this", "remove AI tells", "make it less AI", "de-slop", "does this sound AI", "rewrite in my voice", "match my voice") route to the `humanizer` mechanic.
---

# content-forge-humanizer — moved to the `humanizer` mechanic

The humanizer is now a standalone mechanic with a tiered 47-item AI-tells blocklist, a 9-step humanize pass, a 21-point pre-ship checklist, and 9 voice-mode wrenches. It was rebuilt from the best craft sources on GitHub (lguz/humanize-writing-skill, spuvr/humanizer, hardikpandya/stop-slop) plus empirical work (Jordan Gibbs' 841k-datapoint study, Reuters Institute, NNGroup tone dimensions, Paul Graham's plain rhetoric).

**Use it:** `_system/skills/humanizer/SKILL.md`

- Voice modes: `build-in-public-engineer` (default), `plainspoken-founder`, `editorial-essayist`, `technical-but-warm`, `wry-minimalist`, `reflective-retrospective`, `dry-technical-authority`, `challenger-contrarian`, `mirror` (voice-match from the writer's own samples — overrides presets).
- The old pre/post claim-diff and voice-match live on, expanded: Steps 1 + 8 (fact snapshot → fact-diff) and the `mirror` wrench.

See also: [marketing.md](marketing.md) · [fact-checker.md](fact-checker.md) · [../../humanizer/SKILL.md](../../humanizer/SKILL.md)
