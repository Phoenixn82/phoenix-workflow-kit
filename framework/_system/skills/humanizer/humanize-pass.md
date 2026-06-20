---
name: humanizer-humanize-pass
description: The detailed 9-step humanize editing algorithm (diagnose -> diction -> structure -> specificity -> voice -> self-critique -> fact-diff -> roughen). Run in order; never collapse passes.
---

# The humanize pass (detailed)

The concrete editing algorithm. Run the steps in order — never collapse diction, structure, and voice into one sweep, because doing all three at once does all three badly.

STEP 0 — HOLISTIC READ (no edits)
Read the whole draft as a human reader, start to finish. Mark (don't fix) two things: where your attention drifts, and the 3–5 sentences that feel most machine-made. This preserves coherence and tells you where the real work is before you start cutting.

STEP 1 — FACT SNAPSHOT
Extract every load-bearing fact into a list: numbers, names, dates, error strings, quotes, versions, dollar figures. This is the baseline for the fact-diff at the end. The rewrite is allowed to change everything except these.

STEP 2 — DIAGNOSE TELLS (label, don't rewrite yet)
Pass the draft against the blocklist and tag each hit inline by category:
  [V] vocabulary — Tier-1/Tier-2 words, Latinate inflation, adverbs, hedge softeners, filler.
  [S] structure — rule of three, "not X but Y," copula avoidance, participle tails, topic-sentence padding, signposting, throat-clearing, clustered transitions, moral wrap-ups.
  [R] rhythm — runs of 3+ same-length sentences, uniform paragraph blocks, metronomic cadence.
  [C] concreteness — abstractions where a number/name/date belongs, vague attribution, vague declaratives, tell-don't-show.
  [P] surface — em-dash overuse, semicolons, smart quotes, mechanical bolding, emoji, chatbot artifacts, zero-width chars, missing contractions.
Now you have a map. Work it category by category.

STEP 3 — PASS A: DICTION (the [V] tags)
Word by word: delete Tier-1 vocabulary outright; replace Tier-2 with the plain word; swap Latinate verbs for Anglo-Saxon (leverage→use, facilitate→help, streamline→cut); delete adverbs and intensifiers; cut hedge softeners and filler phrases; add contractions where speech would. Don't touch sentence structure in this pass — only words.

STEP 4 — PASS B: STRUCTURE & RHYTHM (the [S] and [R] tags)
Break the patterns: convert rules of three to one/two/four/none; rewrite "not X but Y" pivots to plain statements; replace copula-avoidance ("serves as") with "is"; cut participle tails at the thought's end; delete topic sentences that restate the paragraph; cut signposting and the first-10% throat-clearing. Reorder to why→how→what. Then fix rhythm deliberately: split clause-stackers, insert one fragment for punch, follow a long sentence with a short one, make sure no three consecutive sentences share a length or shape, and break at least one paragraph into a one-liner for contrast. Cap formal transitions at ~2 per section. Make at least 30% of paragraphs NOT end on a tidy takeaway.

STEP 5 — PASS C: SPECIFICITY (the [C] tags)
Hunt every remaining abstraction and replace it with the concrete thing: the real number, the proper noun, the date, the error message, the named source. Convert "performed well" to the measured result. Replace "experts say" with a named source/date or cut the sentence. Turn every "tell" into a "show" — behavior, events, and numbers instead of broad emotional claims. This pass is where AI prose becomes human prose; spend the most time here.

STEP 6 — COMMIT A VOICE → FIRE THE WRENCH
Pick the mode from the dispatch table by the shape of the piece (default: build-in-public-engineer). If the writer supplied samples, fire `mirror` instead — it overrides presets. Load that wrench, internalize its spec and sample, and rewrite the whole piece inside its fingerprint. This adds the pulse: stance, texture, the human thinking-traces (mid-thought correction, parenthetical admission, one earned caveat).

STEP 7 — SELF-CRITIQUE META-PASS (mandatory, not optional)
Ask explicitly: "Which sentences in THIS rewrite can still be identified as AI-written?" List them by number. The first rewrite always misses some. Then rewrite ONLY those sentences (surgical — preserves the accuracy of everything you already got right). Repeat once if the list is still long.

STEP 8 — FACT-DIFF (verify)
Re-extract the fact list from the rewritten text. Diff against the Step 1 snapshot. Any number, name, date, or quote that drifted → revert that specific sentence and redo the rewrite without changing the fact. "Humanized but now wrong" is a failure, not a success.

STEP 9 — ROUGHEN & SCORE (verify)
Read aloud or run text-to-speech. If it sounds like a textbook read by a news anchor, the rhythm is still uniform — go back to Step 4. Score the five dimensions (Directness, Rhythm, Trust, Authenticity, Density), 1–10 each; if total < ~35/50, revise the weakest dimension. Final move: ROUGHEN, don't polish. Restore one bit of deliberate unevenness if your editing smoothed it away — over-polishing pushes the text back toward the AI-average distribution. Stop before it gets smooth again. Ship.
