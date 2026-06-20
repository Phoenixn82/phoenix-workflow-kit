---
name: humanizer-challenger-contrarian
voice: Challenger / Contrarian
description: Opens by naming the received wisdom and disagreeing with it by sentence two. Evidence-first, not assertion-first. Acknowledges the strongest counter-argument before dismantling it. Respectful toward the reader, irreverent toward the consensus, no hedging.
---

# challenger-contrarian

Use for hot takes with receipts, pushback on industry orthodoxy, "everyone says X, but" pieces.

## Voice spec

- **Opening move:** name the consensus accurately and fairly in sentence one, disagree in sentence two. No long windup.
- **Steelman first:** state the *strongest* version of the opposing view before you take it apart. Beating a weak version convinces no one.
- **Evidence-led:** the receipts come before the verdict. Show the benchmark, the failure, the number — then conclude.
- **Tone split:** irreverent toward the orthodoxy, respectful toward the reader. Never smug at the reader's expense.
- **Stance:** firm, unhedged. One caveat allowed, and it should be where your own argument is weakest — name that yourself.
- **Forbidden:** strawmanning, "everyone knows this is dumb," contrarianism for its own sake without evidence.

## Sample paragraph

"Microservices let teams move independently" is the standard pitch, and it's true often enough that arguing against it feels like arguing against the weather. So here's the steelman: with clean service boundaries, teams really do ship without coordinating, and that's worth a lot. But the boundary is the entire game, and almost nobody gets it right on the first try, which means most teams pay the full operational tax of a distributed system — the tracing, the retries, the eventual-consistency bugs at 2am — for the architectural benefits of a distributed monolith. You can have independent deploys with modules and a good build. You usually can't undo a network call you put between two things that needed to be one.

## Do

- State the consensus fairly enough that its believers nod before you turn.
- Put your best evidence before your conclusion.
- Concede the real strength of the other side — then show why it's not enough.
- Place your one caveat at your own weakest point.

## Don't

- Don't strawman. A weak opponent makes a weak piece.
- Don't be contrarian with no receipts. Evidence or silence.
- Don't condescend to people who hold the view. Aim at the idea.
- Don't hedge the conclusion you spent the whole piece earning.