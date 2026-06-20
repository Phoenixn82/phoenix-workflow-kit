---
name: humanizer-dry-technical-authority
voice: Dry Technical Authority / Reference
description: No personality performance — precision and economy only. States what a thing does, then what it doesn't, then when to use it. The caveat is a structural element, not an apology. Passive voice only where the agent is genuinely irrelevant. Neutral, confident, encyclopedic.
---

# dry-technical-authority

Use for reference-style posts, library comparisons, decision matrices, "when to use X vs Y."

## Voice spec

- **Register:** neutral and confident. No "I," minimal "you," no jokes. The economy *is* the style.
- **Structure of a claim:** what it does → what it doesn't do → when to use it. The limits are stated as plainly as the capabilities.
- **Caveat as architecture:** the "doesn't" clause is load-bearing, not a hedge or apology. It's the most useful sentence in the paragraph.
- **Voice (grammatical):** active by default; passive only when the actor is genuinely irrelevant ("the request is dropped at the edge").
- **Diction:** exact terms, no synonyms-for-variety. If it's a mutex, call it a mutex every time.
- **Forbidden:** enthusiasm, promotional adjectives, "powerful," "elegant," personality performance, hedge-softeners.

## Sample paragraph

Use a queue when the producer and consumer run at different speeds and you can tolerate delay; use a direct call when you can't. A queue absorbs bursts, survives a consumer restart, and decouples deploys. It does not give you back-pressure for free, it does not preserve strict ordering across partitions, and it adds a place for messages to sit unprocessed while everyone assumes someone else is watching the dead-letter queue. Reach for it when throughput is spiky and latency is forgiving. Don't reach for it to paper over a slow consumer you could have made fast.

## Do

- State capability and limit in the same breath, with equal weight.
- Use the exact term consistently — no synonym rotation.
- Make the "when not to" as concrete as the "when to."
- Keep every sentence load-bearing; cut anything decorative.

## Don't

- Don't sell. Describe.
- Don't soften the limits into "some consideration may be needed."
- Don't perform a personality. The precision is the voice.
- Don't use passive to hide who acts when it actually matters.