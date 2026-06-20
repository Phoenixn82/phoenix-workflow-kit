---
name: content-forge
description: Content production mechanic. Marketing copy + prompt sharpening + AI-detection humanizing + factual verification. Shared make-pdf with design-studio (lives there; cross-referenced from here). Fires on "write copy for", "ad for", "blog post", "email sequence", "social post", "repurpose this", "humanize this", "fact-check", "verify claims", "sharpen this prompt", "prompt for X", "marketing".
---

# content-forge — produce / verify / polish content

The lane where intent becomes shipped content. Marketing copy, blog posts, ad creative, prompt-engineered specs, humanized rewrites, fact-checked statements.

Per AGENTS.md hard rule #5, content production is Claude's home turf (writing IS thinking, not implementation). Codex doesn't enter content-forge.

---

## Cardinals

1. **Per-client memory.** When marketing wrench runs for a recurring client, it reads `~/.claude/clients/<slug>/profile.md` first to skip duplicate intake. Returning clients shouldn't re-answer brand voice questions every session.

2. **Platform-accurate constraints.** Every output respects platform limits: tweet 280 chars, LinkedIn 3000 chars + headline 200, Meta ad headline 40 chars, Google ad headline 30 chars × 3 + descriptions 90 chars × 2, blog SEO title 60 chars. The wrench doesn't ship copy that violates the platform.

3. **Humanizer applies on AI-detected risk.** When content might be detector-checked (academic / corporate / sensitive), run through humanizer before delivery. Detector-naive content goes out as-is.

4. **Fact-check anything claims-heavy.** Marketing puffery is fine; specific claims (numbers, dates, names, citations) get fact-checked before delivery. The humanizer + fact-checker chain is the safety net.

5. **Codex is not in this mechanic.** Writing is Claude's home turf. content-forge dispatches nothing to Codex; the lane stays in Claude.

---

## When this mechanic fires

- "Write ad / blog / email / post / sequence for X"
- "Marketing for [client]"
- "Repurpose this content for [channel]"
- "Sharpen this prompt" / "make this a production prompt"
- "Humanize this" / "make it less AI" / "does this sound AI"
- "Fact-check this" / "verify these claims"

---

## Picking the wrench

| Shape of the ask | Wrench | Why |
|---|---|---|
| Ad copy / social / blog / email / repurpose | `marketing` | Production lane |
| Prompt engineering | `prompt-master` | Take rough → production |
| AI-detected text rewrite | `humanizer` | De-AI |
| Verify claims | `fact-checker` | Source-grounded |
| Publication PDF | `make-pdf` (cross-mechanic to design-studio) | Both mechanics share |

---

## Cross-mechanic dependencies

- **`design-studio`** owns `make-pdf` physically; content-forge cross-references
- **`router`** dispatches Gemini for grounded fact-check research (Deep Research path)
- **`second-brain`** captures client profiles (`~/.claude/clients/<slug>/profile.md`) and per-session revision logs
- **`web-scrape`** for source gathering when fact-checking pulls citations

---

## What content-forge does NOT do

- Does not implement (no Codex dispatch from this mechanic)
- Does not design visual surfaces (`design-studio`)
- Does not build slide decks (`design-studio/deck-builder`)
- Does not own brand-system design (`design-studio/design-consultation`)
- Does not architect projects (`plan-room`)

---

## Wrenches

| Wrench | Path | What it does |
|---|---|---|
| **marketing** | `wrenches/marketing.md` | Ad copy / social / blog / email / repurpose. Platform-aware. Per-client memory |
| **prompt-master** | `wrenches/prompt-master.md` | Turn rough into production prompt. Provider-aware (XML for Claude, MD for OpenAI) |
| **humanizer** | `wrenches/humanizer.md` | Strip AI tells. Per-sentence changelog. Detector-aware rubric |
| **fact-checker** | `wrenches/fact-checker.md` | Decompose into atomic claims → cite sources with quotes → verdict + confidence |
| **make-pdf** | `[design-studio/wrenches/make-pdf.md](../design-studio/wrenches/make-pdf.md)` | Shared with design-studio — see there |

---

## See also

- [wrenches/marketing.md](wrenches/marketing.md)
- [wrenches/prompt-master.md](wrenches/prompt-master.md)
- [wrenches/humanizer.md](wrenches/humanizer.md)
- [wrenches/fact-checker.md](wrenches/fact-checker.md)
- [`design-studio/wrenches/make-pdf.md`](../design-studio/wrenches/make-pdf.md) — shared PDF wrench
- [`AGENTS.md`](../../../AGENTS.md) — hard rule #5 (content = Claude's turf)
