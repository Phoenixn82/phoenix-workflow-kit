---
name: content-forge-marketing
description: Marketing production wrench. Ad copy (Google / Meta / LinkedIn / X with character limits), social posts, blog posts, email sequences, content repurposing across channels, quick brand/ICP work for clients. Reads per-client memory at ~/.claude/clients/<slug>/profile.md to skip duplicate intake on returning clients. Runs silent 5-category self-eval before delivery. Logs every session to per-client revision log. Trigger phrases include "write a [platform] [post / ad / sequence]", "draft N variants of X", "repurpose this for [channel]", "quick ICP for", "brand voice for", "marketing task for", "ad copy for".
---

# content-forge-marketing — marketing production lane

Ad-hoc per-task marketing work. NOT full multi-phase campaigns (that's `project-orchestrator`). This wrench handles "write me a LinkedIn post" / "draft 3 Meta ad variants" / "repurpose this blog for email."

---

## When to fire

- Direct marketing request with a specific deliverable
- "Write [platform] [content type] for [client/project]"
- "Repurpose this for [channel]"
- "Quick ICP for [client]" / "brand voice for [client]"

Don't fire when:
- Full multi-deliverable multi-phase campaign → escalate to `project-orchestrator`
- Content is for the user himself with no platform constraint (just write it conversationally)

---

## Per-client memory

Read at session start:
```
~/.claude/clients/<slug>/profile.md
```

Contains: ICP, brand voice, prior deliverables, tone preferences, things-to-avoid, known performers (high-CTR ads, high-engagement posts).

If file doesn't exist, prompt for intake (5 questions max). Don't grill returning clients.

---

## Platform constraints (load-bearing)

| Platform | Constraint |
|---|---|
| X / Twitter | 280 chars per post; threading common |
| LinkedIn post | 3000 chars body; first 200 chars are the hook |
| LinkedIn ad | Headline 200 chars; intro 150 chars; description 600 chars |
| Meta ad | Primary text 125 chars (visible); headline 40 chars; description 30 chars |
| Google ad | 3× headlines 30 chars; 2× descriptions 90 chars |
| Email subject | 50 chars (mobile preview); 60-70 max |
| Email preheader | 90 chars |
| Blog SEO title | 60 chars |
| Blog meta description | 155 chars |
| TikTok caption | 2200 chars (but 150 visible) |
| Instagram caption | 2200 chars (line breaks render) |
| YouTube title | 60 chars / 100 max |
| YouTube description | first 125 chars in preview |

The wrench never delivers copy that violates these. If forced (the user overrides), flag the violation in the delivery.

---

## Pattern routing

| Ask | Pattern |
|---|---|
| Ad copy | 3 variants (cautious / mid / aggressive); same hook style per platform |
| Social post | Hook + meat + CTA; platform-appropriate length |
| Blog post | Title + meta + intro + 3-5 sections + close + CTA |
| Email sequence | Welcome / nurture / pitch / re-engage; 4-7 emails typical |
| Repurpose | Source content → channel-specific reformat preserving core message |
| Quick ICP | 1-paragraph ideal customer profile + 3 sample personas + objections |
| Brand voice quick | tone words / what we sound like / what we don't sound like |

---

## Silent 5-category self-eval (before delivery)

Before handing the output back to the user, the wrench runs a silent self-check:

1. **On-brand?** Does this sound like the client's brand?
2. **On-platform?** Does it respect the platform's constraints + conventions?
3. **On-message?** Does it deliver the actual message the user asked for?
4. **Hooks early?** Is the hook in the first line / first 200 chars?
5. **AI-tell-free?** Are there obvious AI tells (em dashes everywhere, "dive into," "unlock," "navigate the landscape")?

Any FAIL → revise before delivery. Don't surface the self-eval to the user unless he asks — it's silent quality control.

---

## Per-session revision log

Every session writes a log at `~/.claude/clients/<slug>/revision-log.md`:

```markdown
## 2026-05-28 — LinkedIn post for product launch

**Brief:** [what the user asked for]
**Delivered:** [final output]
**Iterations:** [v1 → v2 changes]
**the user feedback:** [what he changed / approved]
```

Logs accumulate. Future sessions read prior logs to maintain voice consistency.

---

## Cost shape

- Marketing draft: low-medium (mostly writing, some structure reasoning)
- Self-eval: small (silent)
- Per-client memory load + log write: small
- Total: low. Marketing work shouldn't burn tokens.

---

## See also

- [SKILL.md](../SKILL.md)
- [humanizer.md](humanizer.md) — chain when output might be AI-detected
- [fact-checker.md](fact-checker.md) — chain when claims need verification
- [prompt-master.md](prompt-master.md) — different lane: prompts not marketing
