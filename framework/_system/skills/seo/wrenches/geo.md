---
name: seo-geo
description: Generative Engine Optimization. AI Overviews / ChatGPT web search / Perplexity citations / llms.txt compliance / brand mention signals / passage-level citability scoring / AI crawler accessibility. First-class wrench (one of the 8 always-fire on audit). Trigger phrases include "AI Overviews", "SGE", "GEO", "AI search", "LLM optimization", "Perplexity", "AI citations", "ChatGPT search", "AI visibility", "llms.txt", "Claude Overviews".
---

# seo-geo — Generative Engine Optimization

Classic SEO targets the SERP. GEO targets the AI summary that increasingly REPLACES the SERP. This is first-class — fires as part of every audit.

---

## When to fire

- "GEO" / "AI Overviews" / "AI search optimization"
- "Show up in ChatGPT / Perplexity / Claude"
- "llms.txt" / "AI crawler accessibility"
- "Passage citability"
- Fired as part of `audit` always-set

---

## What gets checked

| Dimension | What |
|---|---|
| **AI crawler accessibility** | robots.txt allowing GPTBot, ClaudeBot, PerplexityBot, OAI-SearchBot, etc. (or intentionally blocking) |
| **llms.txt** | Present, well-formed, accurately describes site |
| **Passage-level citability** | Are direct answers near the top? Are claims quotable as standalone snippets? |
| **Structured Q&A** | FAQPage schema, clear question + answer structure |
| **Brand mention signals** | Mentions of brand on authority sites (3rd-party citation patterns AI relies on) |
| **First-party data** | Original research, surveys, data that earns citations |
| **Author attribution** | Clear author byline + credentials AI can attribute |
| **Date freshness** | Recent dates AI surfaces when freshness matters |

---

## llms.txt

This wrench can generate llms.txt for the project:

```
# Project Name

> One-paragraph description of what the site is about

## Docs
- [Page name](/url): description

## Examples
- [Example name](/url): description

## Optional
- [Less critical page](/url): description
```

Per the proposed standard. Codex writes the final file to project root.

---

## Passage citability scoring

For top pages, the wrench scores how citable each is:

- Direct answer in first 100 words? (high score)
- Claims as standalone sentences? (high)
- Statistics with sources? (high)
- Quotable definitions? (high)
- Buried in flowery prose? (low)
- No structured answers? (low)

Recommends restructuring for citability when low.

---

## AI crawler config

Recommends robots.txt config per the user's intent:

```
# Allow AI crawlers (default — increases AI visibility)
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

# Or block selectively if the user doesn't want training use
User-agent: GPTBot
Disallow: /

# But typically allow OAI-SearchBot, ClaudeBot for search visibility even when blocking training
```

Default recommendation: allow search-purpose bots, block training-purpose bots if the user prefers.

---

## Output shape

```markdown
## GEO audit — example.com

**Composite GEO score:** 5.5/10

### AI crawler accessibility — 8/10
- GPTBot: allowed
- ClaudeBot: allowed
- PerplexityBot: blocked (FIX — likely intended Allow)
- Google-Extended: not specified (defaults to allow)

### llms.txt — 0/10
- Missing entirely (HIGH FIX — generate)

### Passage citability — 5/10
- Average page: direct answers in first 100 words only 40% of time
- Restructure recommendation for top 20 pages

### Structured Q&A — 4/10
- 12 FAQ pages without FAQPage schema (FIX — see schema wrench)

### Brand mention signals — 6/10
- 23 unlinked brand mentions on authority sites (could pursue link reclaim)

### Top 10 priority fixes
1. [HIGH] Generate llms.txt
2. [HIGH] Restructure top 20 pages for citability (lead with answer)
3. [HIGH] Add FAQPage schema to 12 pages
4. [HIGH] Fix PerplexityBot block in robots.txt
```

---

## See also

- [SKILL.md](../SKILL.md)
- [content.md](content.md) — content depth + citability overlap
- [schema.md](schema.md) — FAQPage / HowTo schema for AI citation
- [technical.md](technical.md) — robots.txt for AI bots
