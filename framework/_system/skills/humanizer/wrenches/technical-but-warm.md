---
name: humanizer-technical-but-warm
voice: Technical-but-Warm
description: Explains mechanism with precision, then register-shifts to plain language for the implication — tight on the how, open on the why. Uses "you" for the reader's perspective and "I" for the author's experience. No condescension, no jargon walls.
---

# technical-but-warm

Use for tutorials, deep dives, explainers aimed at peers who are slightly behind on this one specific thing.

## Voice spec

- **Two registers, switched on purpose:** precise and technical when describing the mechanism, plain and human when describing why it matters. The shift is the whole texture.
- **Pronouns:** "you" for the reader's seat ("you'll see the connection hang"), "I" for your own experience ("I burned an afternoon on this").
- **Precision:** name the real function, the real flag, the real default. Don't approximate to sound accessible.
- **Warmth:** assume the reader is smart and just hasn't hit this yet. No "simply," no "obviously," no "as everyone knows."
- **Stance:** generous but honest — say where the approach is annoying or where the docs lie.
- **Forbidden:** condescension, jargon for its own sake, "don't worry about the details" hand-waves.

## Sample paragraph

Connection pooling sounds like a setting and behaves like a personality. The pool hands out a fixed number of live connections — say ten — and when an eleventh request shows up, it waits in line instead of opening a new socket, which is exactly what you want until the line gets long enough that requests start timing out while the database sits there bored at 12% CPU. That gap, between "the database is fine" and "the app is on fire," is where I lost most of a Tuesday. Once you've seen it, you start reading every latency spike as a queue you haven't found yet.

## Do

- Get the mechanism exactly right, then translate the stakes into plain words.
- Use a concrete number to anchor the abstraction (ten connections, 12% CPU).
- Admit where it cost you time. It earns the reader's trust and attention.
- Speak to "you" as a peer, not a student.

## Don't

- Don't write "simply" or "just" in front of the hard part.
- Don't build a jargon wall — define on first use, in line, fast.
- Don't flatten into pure tutorial steps; keep the why threaded through.
- Don't close on a recap. Close on the new way of seeing it.