---
name: seo-sxo
description: Search Experience Optimization. Reads Google SERPs backwards to detect page-type mismatches (you ranked an article when SERP wants a tool), derives user stories from intent signals, scores pages from multiple persona perspectives. Identifies why well-optimized content fails to rank by analyzing what Google actually rewards for each keyword. Trigger phrases include "SXO", "search experience", "page type mismatch", "SERP analysis", "user story", "persona scoring", "why isn't my page ranking", "intent mismatch", "wireframe".
---

# seo-sxo — search experience optimization

When a page is well-optimized but won't rank, the answer is usually intent mismatch. SXO reads what Google IS ranking for a keyword and tells you what page TYPE / format / depth Google wants.

---

## When to fire

- "Why isn't this page ranking"
- "Intent mismatch on X"
- "SERP analysis for keyword Y"
- "Page-type wireframe"

Don't fire when:
- Generic SEO question (audit / page)
- Pure technical issue (technical)

---

## Sequence

1. **Pull SERP for target keyword.** Top 10 URLs.
2. **Classify each.** Page type (article / listicle / tool / video / comparison / etc.), depth (word count, sections), format signals.
3. **Find the dominant type.** What's Google rewarding?
4. **Compare to your page.** Same type? Same depth? Same format signals?
5. **Derive user stories.** What is the searcher actually trying to do? (Based on SERP results being more interactive vs more informational, more brand-led vs more comparison, etc.)
6. **Score from personas.** Tech-savvy / beginner / mobile-first / buyer / researcher — would each persona find what they need on your page?
7. **Recommend.** Restructure to match dominant type, or accept the mismatch and target a different keyword.

---

## Output shape

```markdown
## SXO analysis — keyword "best self-hosted databases"

### SERP analysis
- 7 of 10 results are listicles ("Top 10 self-hosted databases")
- 2 are comparison tables
- 1 is a tools directory
- 0 are deep guides / tutorials

### Your page
- Type: deep guide (5000 words, 12 sections)
- Mismatch: SERP wants quick scannable lists; you offer deep reading

### User stories
- "I want to quickly see options" (listicle satisfies)
- "I want to compare features" (comparison satisfies)
- Your page doesn't satisfy the dominant intent

### Persona scores
- Tech-savvy researcher: 8/10 (loves the depth)
- Quick browser: 3/10 (too long)
- Comparison shopper: 4/10 (no table)

### Recommendation
Option A: restructure top of page as scannable list of 10 options + link to deep guide
Option B: split — create new listicle page targeting this keyword; keep deep guide for related long-tail keywords
Option C: accept the mismatch; target different keyword that wants the deep-guide format
```

---

## See also

- [SKILL.md](../SKILL.md)
- [page.md](page.md) — single-URL analysis
- [content.md](content.md) — content depth + structure
- [cluster.md](cluster.md) — when multiple keywords need different page types
