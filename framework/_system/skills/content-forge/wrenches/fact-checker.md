---
name: content-forge-fact-checker
description: Decompose any text into atomic claims (SAFE / FActScore-style), retrieve evidence via web search, assign per-claim verdict (supported / refuted / unsupported / partially-supported / opinion / unverifiable) with confidence. Cite sources by URL + exact quote span. Rank sources by transparent tier schema. Handles temporal claims. Trigger phrases include "fact-check this", "verify claims", "is this accurate", "source this", "check my sources", "check the facts", "are these numbers right".
---

# content-forge-fact-checker — claim-by-claim verification

The user has written or generated text with claims. This wrench decomposes into atomic claims, hunts evidence, and grades each claim with verdict + confidence + sources.

---

## When to fire

- "Fact-check this"
- "Verify claims" / "is this accurate"
- "Source this article" / "check my sources"
- Before publishing claims-heavy content
- After marketing wrench produces content with specific statistics / dates / names

Don't fire when:
- No specific claims to check (route back; ask the user what to verify)
- Content is pure opinion / marketing puffery (no factual claims)

---

## Atomic claim decomposition

Split input into atomic claims following SAFE / FActScore pattern:

```
Input: "GPT-4 was released in March 2023 and has 1.76 trillion parameters,
        making it Anthropic's flagship model."

Atomic claims:
1. "GPT-4 was released in March 2023"
2. "GPT-4 has 1.76 trillion parameters"
3. "GPT-4 is Anthropic's flagship model"
```

Each gets independent verification. Claim 3 is refuted (GPT-4 is OpenAI, not Anthropic) — split prevents one wrong fact from undermining one right fact's verdict.

---

## Evidence retrieval

Via the web-scrape mechanic (Firecrawl search → grab content):

```
search "<claim phrasing>" → top results
scrape top 3 results → markdown
extract supporting / refuting quotes with exact URL + character offset
```

For the user's heavier research (deep dossiers), route through Gemini Deep Research instead.

---

## Verdict schema

Per claim:

- **supported** — evidence directly confirms
- **refuted** — evidence directly contradicts
- **unsupported** — no evidence found (different from refuted)
- **partially supported** — some elements confirmed, others not
- **opinion** — claim is subjective, not factual
- **unverifiable** — no public source can confirm or refute

Plus confidence: low / medium / high.

---

## Source ranking tier (transparent + override-able)

Default tier schema (the user can override):

| Tier | Examples |
|---|---|
| **1 — Primary** | Official docs, government records, peer-reviewed papers, court filings, company SEC filings |
| **2 — Reputable secondary** | Major newspapers (NYT / WaPo / Reuters / AP / FT), industry publications (TechCrunch / The Verge) |
| **3 — Subject-matter sites** | Wikipedia for established facts, vendor blogs for product details, expert blogs |
| **4 — User-generated** | Reddit, forums, Q&A sites — useful for sentiment, weak on facts |
| **5 — Unknown / questionable** | Random blogs, low-traffic sites, AI-generated content farms |

Verdicts cite the highest-tier source available. If only tier 4-5 sources exist, claim's confidence drops.

---

## Temporal claim handling

Claims with "as of [date]" or "in [year]" need date-aware verification:

- For past dates: verify against sources from that period
- For "current" claims: check date of most recent verifying source
- For future claims: mark as unverifiable

The wrench surfaces temporal context: "Verified as of 2026-05-28; may have changed since."

---

## Output format

```markdown
## Fact-check report — 2026-05-28

### Summary
- Total claims: 8
- Supported: 5
- Refuted: 1
- Unsupported: 1
- Opinion: 1

### Per claim

**Claim 1:** "GPT-4 was released in March 2023"
- Verdict: **supported** (high confidence)
- Source: [OpenAI blog](https://openai.com/...) tier 1
- Quote: "Today we release GPT-4..." (March 14, 2023)

**Claim 2:** "GPT-4 is Anthropic's flagship model"
- Verdict: **refuted** (high confidence)
- Source: [OpenAI](https://openai.com/...) tier 1
- Quote: "GPT-4, OpenAI's most advanced..."
- **Correction:** GPT-4 is OpenAI's model. Anthropic's flagship is Claude.

...
```

---

## See also

- [SKILL.md](../SKILL.md)
- [marketing.md](marketing.md) — chain when claims-heavy content needs verification
- [`web-scrape/SKILL.md`](../../web-scrape/SKILL.md) — evidence retrieval
- [`router/wrenches/gemini.md`](../../router/wrenches/gemini.md) — Deep Research for deeper grounding
