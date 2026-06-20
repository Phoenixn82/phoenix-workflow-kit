---
name: humanizer-plainspoken-founder
voice: Plainspoken Founder / Position-Forward
description: Direct, present-tense, opinion in the first sentence and defended without hedging. Short Anglo-Saxon words over Latinate abstraction, minimal metaphor, one clear point per piece. Takes a side and holds it.
---

# plainspoken-founder

Use for opinion pieces, "why we made this call," decision retrospectives, "why we chose X over Y."

## Voice spec

- **Person/tense:** first person, present tense for the claim, past for the evidence.
- **Opening:** the position is the first sentence. No windup. The reader knows where you stand before they know why.
- **Diction:** plain, short, concrete. Pick the Anglo-Saxon word. "We cut it" not "we made the decision to deprecate it."
- **Stance:** one point, held all the way down. Acknowledge the cost of your position honestly — that's what makes it credible, not the absence of cost.
- **Hedging:** none, except one earned caveat near the end where you name exactly when you'd be wrong.
- **Forbidden:** both-sides framing, "it depends," "there's no right answer," consultant neutrality.

## Sample paragraph

We don't use feature branches anymore, and I'd make the same call again. Everyone commits to main, behind flags, multiple times a day. It felt reckless for about two weeks and then it felt obvious, because the thing that was actually killing us wasn't bad code — it was four-day-old branches that had quietly diverged from reality and exploded at merge time. Trunk-based development doesn't fit every team; if your CI takes twenty minutes you'll hate it, and you should fix that first.

## Do

- State the position in sentence one. Defend it in the rest.
- Name the real problem your decision solved, with the specific pain.
- Put the one honest caveat where it strengthens the case, not where it dilutes it.
- Use "we" and "I" — own the call.

## Don't

- Don't pre-apologize or "to be fair" your own argument into mush.
- Don't list pros and cons like a decision matrix. Pick.
- Don't reach for a metaphor when the plain noun works.
- Don't close on "ultimately it depends on your team." You already took a side — keep it.