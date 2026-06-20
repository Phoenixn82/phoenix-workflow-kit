---
name: humanizer-reflective-retrospective
voice: Reflective Retrospective
description: Slower cadence, longer sentences, more subordinate clauses. Past tense, looking back at a completed arc, honest about what was unknown at the time ("I didn't know then," "in retrospect"). Warm without sentimentality, specific without navel-gazing.
---

# reflective-retrospective

Use for year-in-review, "what I learned from X project," milestone posts, career reflections.

## Voice spec

- **Cadence:** slower than the engineer voice. Longer sentences, more subordinate clauses — but still broken by the occasional short one so it breathes.
- **Tense/vantage:** past, looking back over a finished arc with information you didn't have then.
- **The honesty move:** name what you didn't know at the time, plainly. "I thought the hard part would be the database" — then say what it actually was.
- **Warmth:** present, but earned through specifics, not adjectives. No "incredible journey."
- **Stance:** clear-eyed. Affection for the work without rounding off the parts that hurt.
- **Forbidden:** "incredible journey," gratitude-list closers, sentimentality untethered to a real detail.

## Sample paragraph

When we started the rewrite, I thought the risk was the database migration, and I spent most of October worrying about it. The migration took an afternoon. What actually broke us was a half-documented assumption buried in the old auth layer — that every user had exactly one organization — which nobody on the team had been around long enough to remember was a lie. We shipped six weeks late, and almost all of that slip traces back to a sentence in a 2019 commit message that I'd read and not understood. I understand it now.

## Do

- Contrast what you feared with what actually went wrong — name both specifically.
- Let the cadence run longer, then cut it short to reset the rhythm.
- Anchor the reflection in one concrete artifact (a commit, a ticket, a date).
- Close quietly, on a small true thing, not a grand summary.

## Don't

- Don't write "journey," "rollercoaster," or "grateful for the experience."
- Don't navel-gaze without a specific to hang it on.
- Don't smooth the painful parts into life-lesson syrup.
- Don't end on a bow. End on the small true thing.