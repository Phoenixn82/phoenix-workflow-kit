---
name: humanizer
description: Mega humanizer mechanic for a build-in-public developer blog. Strips AI tells and rebuilds prose in a sharp, senior, honest human voice — varied rhythm, specific evidence, real stance, dry wit allowed. This is a CRAFT tool, not a detector-evasion tool. Dispatches to ten voice-mode wrenches. Fires on "humanize this", "make it less AI", "does this sound AI", "rewrite in my voice", "de-slop", "make this sound human", "match my voice", "kill the AI tells", "tighten this post", "sharpen this draft".
---

# humanizer — make the writing read like a sharp human wrote it

A draft comes in reading like a model wrote it. This mechanic rewrites it so a senior, honest, specific human wrote it instead — and then routes the final voice to whichever mode the piece calls for.

The goal is craft, not evasion. We are not gaming GPTZero or Turnitin. Injecting typos, slang, or "chaos" to fool a classifier makes the prose *worse* and is banned. The bar is the same one a good editor at a serious publication holds: does this say something specific, does it have a stance, does it have a pulse. AI text fails that bar in predictable, fixable ways. We fix them.

The root cause of nearly every tell: **AI doesn't trust the reader.** It over-explains, hedges, signposts, summarizes what it just said, and wraps a moral around every paragraph because it can't risk being misread. Human writers trust the reader to keep up. Most of this skill is teaching that trust.

---

## Cardinals

1. **Craft over evasion.** Every change must make the prose *better* to a human editor. If a change only helps "beat a detector" and reads worse, don't make it. Reject any technique whose whole value is fooling a classifier.

2. **Specificity is the spine.** The single biggest upgrade from AI to human is replacing abstraction with the concrete thing — the number, the name, the date, the error message, the dollar figure. When in doubt, get more specific, not more polished.

3. **Preserve the facts.** Rewriting for voice must never change a claim. Snapshot every number/name/date/quote before the rewrite, diff after. If a claim shifted, revert that sentence and redo.

4. **Commit to one voice.** Passes 1–2 (kill vocabulary, break structure) are voice-agnostic. Pass 3 requires a committed mode — without one, the rewrite drifts back to AI-average. Pick the wrench *before* Pass 3.

5. **Mirror beats default.** If the writer supplied prior samples, the `mirror` wrench wins over any preset mode. A voice-matched rewrite continues the writer's fingerprint; a preset is a fallback when there's no sample.

6. **Leave it slightly uneven.** Over-polishing re-introduces AI smoothness. The last pass roughens, it doesn't buff. A little unevenness *is* the human signal — don't sand it off.

---

## When this mechanic fires

- "Humanize this" / "make it less AI" / "de-slop this"
- "Does this sound AI?" → if yes, this mechanic
- "Rewrite this in my voice" / "match my writing" → `mirror`
- "Sharpen / tighten this draft" for the blog
- After a draft is AI-assisted and headed for the build-in-public blog

Don't fire when:
- The text is already human and good (don't rewrite for its own sake)
- The ask is net-new content (write it first; humanize after if needed)
- The ask is fact-checking (separate concern — claims accuracy, not voice)

---

## Core principles of human writing (the spine)

Distilled from the research. These are what we rebuild *toward*, not just what we strip.

**Rhythm is planned, not random.** Humans vary sentence length on purpose — a 4-word punch after a 30-word clause-stacker. AI locks into uniform 12–22 word sentences and complex/compound-complex shapes ~75% of the time (Gibbs, 841k datapoints). Never let three consecutive sentences run the same length or the same shape. Vary paragraph length too: a one-line paragraph earns weight by contrast.

**Concrete before abstract.** Show the example, then name the principle — never the textbook order of concept-then-explanation. "It handled 4,200 concurrent users before the first timeout" beats "it performed well under load." Replace abstraction with the actual thing every time you can.

**Take a position.** Kill both-sides hedging. One carefully-placed caveat per piece, not one per paragraph. The sharpest move is an opinion with stakes and a named failure mode: "this breaks in six months, here's the exact mode." The caveat is what trust looks like — name where your advice fails.

**One thought per paragraph.** If you reach for "also" or "additionally," start a new paragraph instead. Drop topic sentences that merely restate the paragraph's subject; experienced writers open on the detail.

**Why → how → what.** Lead with the problem and the motivation, then the approach, then the implementation. AI defaults to what-then-how. The reader's time is the priority (Pragmatic Engineer).

**Don't announce, move.** No "let's dive in," no "in this section we'll," no dramatic mic-drops. The writing should move, not narrate its own structure. Cut the first 10% — the setup-for-the-setup. Open on the conflict, the claim, or the concrete moment.

**Don't land every paragraph on a bow.** At least 30% of paragraphs should not end on a tidy takeaway. Leave thoughts unresolved. End on a specific detail, an open question, or a partial thought — not "the future looks bright" or "ultimately it depends on your needs."

**Human thinking shows.** Mid-thought corrections, parenthetical admissions, second-guessing. "(Or maybe I'm wrong — that benchmark was from 2022.)" AI never reconsiders mid-sentence. That reconsidering is a fingerprint of a real mind at work.

---

## AI-tells blocklist (strip on sight)

**Tier-1 vocabulary — avoid entirely.** delve, tapestry, pivotal, testament (to), meticulous/meticulously, nuanced, multifaceted, embark, spearhead, bolster/bolstered, garner, interplay, realm, labyrinth, symphony, intricate/intricacies, landscape (abstract), underscore (verb).

**Tier-2 vocabulary — limit or replace.** crucial, leverage, utilize, foster, enhance, navigate (challenges), resonate, robust, holistic, comprehensive, seamless/seamlessly, innovative, dynamic, cutting-edge, game-changer, vibrant, showcase, illuminate, streamline, harness, elevate, facilitate, commendable, boast. Swap Latinate for Anglo-Saxon: leverage/utilize→use, facilitate→help, streamline→cut, harness→use, elevate→lift, foster→build.

**Structural tells.**
- Rule of three — exactly three items/adjectives in every list. Use one, two, four, or none.
- "Not X, but Y" / "It's not just X, it's Y" / "Not only X but also Y" pivots — state Y plainly.
- Copula avoidance — "serves as / acts as / stands as / represents / functions as / aims to / boasts" replacing plain "is"/"has."
- Present-participle tail clauses faking depth — "...reflecting the growing recognition of..."
- False agency — "the data tells us," "the decision emerges." Name the actor.
- False range — "from small startups to Fortune 500s" with non-parallel items.
- Wh- lecturer openers (What/When/Where/Which/Why/How starting sentence after sentence).

**Filler and hedge tells.**
- All adverbs/intensifiers: really, just, literally, genuinely, honestly, simply, actually, deeply, truly, fundamentally, inherently, crucially, importantly.
- Hedge softeners: "it could be argued that," "one might say," "arguably," "you may want to," "it is advisable."
- Filler hedges: "it's worth noting that," "it is important to note," "needless to say," "that being said," "to put it simply."
- Clustered formal transitions in sequence: Furthermore, Moreover, Additionally, Consequently, Notably, Indeed, Thus. One alone is fine; clustered is lethal. Replace with Also/And/So or delete. Cap ~2 per section.
- Throat-clearing openers: "it turns out," "the uncomfortable truth is," "at its core," "here's the thing," "in a world where," "in today's fast-paced digital world."
- Signposting: "let's dive in," "let's unpack this," "in this section we'll," "as we'll see."
- Dramatic reveals: "here's what nobody tells you," "the result:," "let that sink in," standalone "this is where most developers go wrong."

**Stance/substance tells.**
- Vague attribution: "experts say," "studies show," "industry reports suggest" — name the source/date/claim or cut it.
- Vague declaratives: "the implications are significant," "the stakes are high" — name the specific implication or cut.
- Broad sweeping emotional statements that say nothing: "AI isn't just a tool, it's a revolution."
- Generic positive conclusions: "the future looks bright," "exciting times lie ahead."
- Moral wrap-up: every section closing on a tidy lesson.
- Fake balance: "on one hand / on the other hand" with no position taken.
- Promotional adjectives instead of description: stunning, vibrant, breathtaking, powerful, remarkable.

**Surface tells.**
- Em-dash overuse — the misuse is the tell, not presence. Cap ~1–2 per 500 words; prefer commas/periods.
- Semicolons in casual/expository prose reaching for polish.
- Smart/curly quotes (ChatGPT fingerprint — use straight quotes).
- Mechanical bolding of every key term; "**Term:** explanation" inline-header bullets.
- Title Case In Every Heading Word (use sentence case).
- Emoji decoration (✅🚀💡) in serious technical prose.
- Chatbot artifacts: "Great question!," "Hope this helps!," "Let me know if you'd like more," knowledge-cutoff disclaimers.
- Hidden/zero-width Unicode left by the generator (strip them).
- Absence of contractions in conversational prose.
- Synonym cycling: rotating velocity/speed/pace for the same concept. Humans repeat the exact right word.

---

## The humanize pass (run in order, one concern at a time)

Never attempt vocabulary, structure, and voice in one sweep — you'll do all three badly.

1. **Holistic read.** Read the whole thing as a person. Note where attention drifts and which sentences feel most machine-made. Don't edit yet — this preserves coherence and tells you where the real problems are.

2. **Snapshot the facts.** Pull every number, name, date, error string, and quote into a list. This is the fact-diff baseline for the end.

3. **Pass A — diction.** Word by word, kill Tier-1 vocabulary, replace Tier-2, swap Latinate verbs for Anglo-Saxon, delete adverbs and hedge softeners, strip filler. Don't touch structure yet.

4. **Pass B — structure & rhythm.** Break AI sentence/paragraph patterns: kill rules of three, "not X but Y" pivots, copula-avoidance, participle tails. Vary sentence length deliberately (insert a fragment, split a clause-stacker, follow a long sentence with a short punch). Reorder to why→how→what. Drop topic sentences and throat-clearing. Cut clustered transitions. Make at least 30% of paragraphs not land on a bow.

5. **Pass C — specificity.** Hunt every abstraction and replace it with the concrete thing: real number, proper noun, date, error message. Replace vague attribution with a named source or cut it. Convert "tell" into "show."

6. **Commit a voice → fire the wrench.** Decide the mode (or `mirror` if samples exist). Load that wrench and rewrite for its fingerprint. This is where the prose gets a pulse, not just a clean surface.

7. **Self-critique meta-pass (mandatory).** Ask explicitly: "which sentences here can still be flagged as AI-written?" List them. The first pass always misses some. Rewrite only those — surgical, not wholesale (preserves accuracy).

8. **Fact-diff.** Re-extract claims, diff against the Step 2 snapshot. Any drift → revert that sentence, redo without changing the fact.

9. **Roughen, don't polish.** Final read aloud (or text-to-speech). If it sounds like a textbook read by a news anchor, the rhythm is still uniform — rebuild it. Leave slight unevenness. Stop before it gets smooth again.

---

## Dispatching to voice-mode wrenches

Passes A–C are mechanic-level and voice-agnostic. The voice lives in the wrench. Pick by the *shape of the piece*, not by reflex.

| The piece is... | Wrench | Voice |
|---|---|---|
| "What I built/broke this week," a postmortem, a shipping log | `build-in-public-engineer` | First-person, incident-driven, dry |
| "Why we chose X over Y," a decision defended | `plainspoken-founder` | Position-forward, no hedging |
| "I've been thinking about X," a longer reflection | `editorial-essayist` | Graham register, self-questioning |
| A tutorial / explainer for peers slightly behind | `technical-but-warm` | Precise on how, plain on why |
| A hot take, a link comment, a short dry aside | `wry-minimalist` | Short, dry, understated |
| A year-in-review, "what I learned from X" | `reflective-retrospective` | Slower, looking back, honest |
| "When to use X vs Y," a library comparison | `dry-technical-authority` | Neutral, encyclopedic, caveat-as-structure |
| "Everyone says X, but," pushback with receipts | `challenger-contrarian` | Names the orthodoxy, dismantles it |
| The writer supplied prior samples | `mirror` | Their own fingerprint (wins over presets) |

If the mode isn't obvious, default to `build-in-public-engineer` — it's the blog's home voice. If a sample exists, `mirror` overrides everything.

---

## Voice-by-example (the strongest lever)

Description ("write conversationally") is weak. A sample is strong. When the writer hands over ~200 words of target writing, the model latches onto cadence you can't articulate. The `mirror` wrench formalizes this: fingerprint six axes (sentence-length distribution, word register, paragraph-opening patterns, punctuation habits, recurring phrases, transition methods) and rewrite *inside* that fingerprint. Apply it silently — never describe the fingerprint back to the reader.

---

## Scoring before ship

Score five dimensions, 1–10 each. Revise anything below ~35/50 total.

- **Directness** — does it state things plainly, or hedge and signpost?
- **Rhythm** — is sentence length varied, or metronomic?
- **Trust** — does it trust the reader, or over-explain and wrap morals?
- **Authenticity** — stance, specifics, human thinking-traces present?
- **Density** — every sentence carrying weight, or padding?

Burstiness (sentence-length variance) is a useful proxy for Rhythm: AI sits near 0.50, good human prose ≥0.72. But it's a thermometer, not a target — don't randomize length to hit a number; vary it because the meaning calls for it.

---

## See also

- `wrenches/build-in-public-engineer.md`
- `wrenches/plainspoken-founder.md`
- `wrenches/editorial-essayist.md`
- `wrenches/technical-but-warm.md`
- `wrenches/wry-minimalist.md`
- `wrenches/reflective-retrospective.md`
- `wrenches/dry-technical-authority.md`
- `wrenches/challenger-contrarian.md`
- `wrenches/mirror.md`
- `AGENTS.md` — hard rule #5 (content = Claude's turf; no Codex in this lane)