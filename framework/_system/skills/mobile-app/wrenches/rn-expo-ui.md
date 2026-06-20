---
name: rn-expo-ui
description: React Native + Expo UI/UX procedural knowledge — Nick's 5-part app-design framework (core function, core loop, accessory features, surface-area check, retention hook), MVP feature scoping, screen/tab layout patterns, and the iterate-on-design test-and-fix loop (Chrome screenshot pass, reference-app emulation, palette/font/corner tokens). Claude OWNS this wrench (it is design + spec thinking, AGENTS.md rule #5 carve-out); Codex writes the actual RN code that the design spec drives. Routes the visual brand/design-system layer to ui-ux-pro-max / design-studio. Fires on "design the app screens", "build the RN UI", "app layout/navigation", "polish the mobile UI", "what makes a successful app", "scope the MVP", "iterate on the design".
---

# rn-expo-ui — design + iterate the Expo/RN screen layer

This wrench turns a fuzzy app idea into a tight, opinionated MVP spec and then drives the iterate-on-design loop that gets an Expo/React Native app from "looks pretty weak" to "one of the nicer apps I've put together in 15-20 minutes." It carries Nick's 5-part app-design framework (the canonical product spec every app must satisfy), the surface-area discipline (5-7 screens max), the retention-hook playbook, and the exact prompt-driven design refinement loop (Chrome screenshot test pass, reference-app emulation, color/font/corner tokens). The framework is the reusable artifact — once you have it, you feed it to the build lane as the spec.

**Cardinal: design IS thinking — Claude owns it.** Spec'ing the framework, deciding screens, choosing the retention mechanic, and judging "does this look high-end" are decisions, not typing. Claude does this. Codex (or Claude Code when carved in) writes the RN code the spec produces. Never silently pick one of several interpretations of "make it look better" — name the design direction (palette, fonts, corner rounding) explicitly before prompting.

**Cardinal: do ALL design iteration while data is still LOCAL.** Iterating design after a live Supabase DB exists forces a new schema push every change, deprecates old data, and balloons the loop. Build core local functionality → design-to-done on local storage → only then add the DB (`supabase-mobile.md`).

**Cardinal: 5-7 screens, hard cap. Three to four is better.** Beginners balloon to "millions of pages." The whole job is doing one specific thing really well, not doing everything. Run the surface-area check on every feature before it goes in.

**Cardinal: never design for one-time use — build the retention hook in from day one.** "Any app claiming one-time use as its goal is lying." You must create an unfinished state the user returns to (challenges, scheduled check-ins, escalating rewards). This leans on dark patterns in user behavior by design — that is the point, not a bug.

---

## The 5-part app-design framework (the reusable artifact)

This is the spec every app must satisfy, in order. Define each one specifically for the app, annotate it, then hand the whole thing to the build lane as the MVP scope. "If you have all five of these things, you now basically have an MVP… you have like a scope."

1. **Core function** — the one thing that, if you removed everything else, would still BE the app. (Habit tracker: create a habit, tap it, each tap logs to the DB. Annotate `core function = track a habit`. CalTracker: photograph food → AI returns probable calories + macros → add to daily goal.)
2. **Core loop** — a cycle mapping an **action → reward**, ideally **under ~30 seconds**. The reward is sensory: nice sound/chime on tap, animation on tap, confetti raining down at a goal, haptics/vibration. Humans are tactile — stack sensory rewards. Annotate `core loop = some stimulating reward`. The loop tightens for games; same action-reward idea applies to any app. The reward mechanism can be made arbitrarily complex (financial stakes, accountability partners who get your money if you miss) — keep it simple by default.
3. **Accessory features** — things that wrap around and SUPPORT the core loop without changing it: a log/history of past entries (e.g. "on May 4th you logged X"), a chart/visualization tied to logging (`chart + logging`), customization including multi-tier types, and optionally a social feature (add friends, get notified when they log).
4. **Surface-area check** — don't bloat into 10 core functions, 100 loops, 1000 features. Minimize digital surface area so users aren't confused. Aim for a simple core loop served by a handful of screens a user understands in one run-through **with no onboarding explanation**. Cap at 5-7 screens (3-4 is the target).
5. **Retention hook** — create an unfinished state the user must return to. Starter mechanic: a **3-day challenge** (log the habit every day for three days → forces three separate visits over a 72-hour window). Alternatives: scheduled check-ins / push notifications ("Have you tracked breakfast? lunch? dinner?", streak congratulations) that "knock on the door" once or twice a day.

**Gold-standard reference (escalating reward):** Opal (app blocker) gives you a gem that grows shinier the more consecutive days you block apps — a basic gem on day one becomes a shiny amethyst after a week or two. Escalating visual reward = retention.

### The framework as a build prompt (verbatim spec dictation)

Dictate the framework as the build spec (Nick uses Aqua voice transcription; the terminal collapses a long paste to `pasted text #1 + 8 lines` — press enter to populate). Lead-in:

> Hey, so I really like the app as it stands, but I'd like to level this up with an app design framework that high-quality app devs and designers use where essentially every app that I build requires a core function, then a core loop, some accessory features, a surface area check to minimize the number of screens, and then some sort of retention hook.

Then fill each slot specifically. Habit-tracker example, verbatim:

- **Core function:** "it needs to be able to create and then track habits."
- **Core loop:** "every time a person creates a habit and then tracks it, they need to be rewarded in some way. It needs to be visually stimulating. There needs to be some form of haptic feedback and then ideally there's some sort of sound like a chime… Also, we need some form of challenge. So if they're embarking on a 3-day habit challenge… at the end of that 3-day challenge, we also need to reward them for the fulfillment of their efforts."
- **Accessory features:** "logging. So the user should be able to see all of their prior habits tracked, some sort of accountability thing… maybe see a graph or a chart of just how consistent they've been. And then… a way to create multiple types of habits, not just one. Being aware that a habit where you log it once per day is different from a volume based habit where you need to maybe do it three or four times a day."
- **Surface-area check:** "just make sure that we don't have more than somewhere between five to seven screens in our app. We want it to be as simple as possible."
- **Retention hook:** "create challenges for the user and… some sort of ongoing thing that checks in with them via push notifications probably once a day or maybe a couple times a day. Just consistently knocking on their door…"

**Force the whole build at once.** Claude conserves tokens/effort and "won't try as hard as it realistically can" — it will offer to split into phases. Refuse:

> No, I just want you to do the whole thing. I'd like us to do all of it, including phase 1 through 4. Once done, open in Chrome, not Expo, so I can test locally.

(Framework mapping ~1m29s; building phases 1-4 ~5 min. Claude may auto-open Chrome tabs as part of its own internal testing loop.)

---

## Screen / navigation layout patterns (what shipped)

**Habit-tracker six-screen MVP layout** Claude proposed (note: a tighter version with three bottom-nav tabs — Today, Manage, History — was the demo that actually shipped):

1. **Onboarding / first-launch** — picks three habits for you and starts a 3-day challenge.
2. **Today** — daily checklist; the core loop lives here. (Rename to "Dashboard" if the date must be changeable for backdating.)
3. **History** — calendar/graph of past completions + a consistency chart.
4. **Manage** — add/remove a habit, configure habit type.
5. **Challenge** — challenges you're enrolled in.
6. **Settings** — notification preferences, theme.

Bottom tab bar: Home, Progress, Profile (CalTracker) / Today, Manage, History (habit tracker).

**CalTracker 3-4 screen target** (deliberately tighter): Home (at-a-glance functionality), Take-photo, Post-photo nutrition result (editable), Progress, plus Settings if it stays under the cap.

**Habit-type distinction (model this in the schema and the UI):**
- **Daily habit** — log once per day (e.g. sleep before 9pm, zero/one daily).
- **Count / volume habit** — multiple per day (e.g. drink water 8x/day, a count of 5).

**Challenge durations to offer:** 3-day, 7-day, 14-day, 30-day. **Default seeded habits:** exercise, meditate, drink water, healthy meal, journal, sleep 8 hours.

**Onboarding done right (CalTracker):** ask goal (lose / maintain / gain weight, build muscle), collect height/weight/sex/age/activity level (sedentary, lightly active, moderately active), then COMPUTE a recommended plan + macro targets. Tell Claude to actually research the math, not guess ("Actually do the research because I don't just want you to pull it out of your ass") — it used the **Mifflin-St Jeor equation** (feature took 2m56s). Always give a recommended plan so the user isn't building it from scratch. Add one final onboarding screen that plainly explains how the app works (core functionality → track → milestones → push notifications). Re-running onboarding must NOT wipe existing logged entries — it should only update calorie totals on existing entries; verify this explicitly.

**Opinionated, not locked-in:** "do some of the thinking for the user, offer flexibility (extra reminders, end-of-day log) but not too much flexibility."

---

## The iterate-on-design loop (the core procedure)

Once core local functionality exists, design is "much easier" — "all we're really doing is changing the styles… fonts… colors." The loop:

**Phase 1 — UX polish pass.** Walk every page in Chrome at the project's dev port (8081 is Expo's default; use the registry-allocated port per SKILL.md cardinal rule 5 — see `expo-scaffold.md`; shrink window / ~150% zoom to fake a phone). Feed concrete UX requests in one prompt:

> Excellent job. This looks fantastic. The first thing I want to change is I need some sort of testing view for a developer so that I can modify the day of the challenge or at least trigger the event that occurs when we hit let's say 3 days out of the 3-day kickstart. Right now I just sort of have to trust that it's working…

Then list every bug top-to-bottom and end with:

> Okay, with all that in mind, go through everything top to bottom, implement those changes, and then just open it up in another Chrome tab. I'll test it.

State explicitly when it's a minor-changes pass ("We're not actually building the whole thing now") so Claude doesn't re-architect.

**Phase 2 — design upgrade via reference-app emulation.** Screenshot an app you admire, paste it, ask Claude to emulate, then deliberately diverge (rename, change palette/fonts) so it isn't a carbon clone:

> I love the design of the app that I just screenshotted over to you. I want you to start by emulating that design. Right now, the design is pretty weak. I'd like you to upgrade it so it more or less looks exactly like this app does, just without some minor logo things — rather than call it Cal AI, call it Cal Tracker.

**Phase 3 — apply design tokens.** Generate a palette in **uicolors.app** (the "UI colors app generator"; press spacebar to randomize/customize hue — go cool gray / dark blue-gray, NOT pure black, avoid indigo; copy the hex values; full palette walkthrough is gated behind Pro upgrade). Paste hex + token prompt:

> great, update color scheme so it looks like this. Also make sure all icons, emojis are monochrome, e.g. they're of the same color as that palette. Important we stick to that palette from now on. Also apply high-end lux style serif fonts rather than sans serif — let's do serif fonts for the display/headings rather than sans serif, and focus on reducing the corner rounding just a tad to make it feel higher end.

Design tokens that work for a "lux" feel: one palette everywhere; monochrome icons + emojis matching the palette; **reduced corner rounding** (phones have rounded corners so apps default to rounded — less rounding reads higher-end). **Serif headings looked "lame" in practice — switch to a good common sans-serif** associated with high-end clean designs. Design is reversible anytime; experiment.

**Phase 4 — harmonize cross-page drift.** Claude silently changes colors without screenshotting every page, leaving some pages with card outlines and some without:

> I'm noticing that there are slightly different types of designs on each different page… the homepage has an outline around each card, whereas the profile page doesn't… remove outlines around all cards and favor clean, minimalistic design over busy design. Also… the homepage is very compressed and kind of stacked up top — I'd like you to distribute each of the elements a little bit more organically… And then instead of using a serif font like I talked about before, just pick a really good common sans serif font…

**Phase 5 — autonomous Chrome screenshot test loop.** When a layout keeps being misunderstood (macro circles, card alignment — the model is "fundamentally misunderstanding something"), stop hand-describing and make Claude self-test. Bake this instruction into the prompt:

> when you do a test, you actually run through every single page, take a screenshot of it, and itemize anything that may be sub-optimal or below par before modifying it on your own to make sure that it's as clean as possible.

Then hand it the keys:

> great, now open up in your own Chrome window and screenshot through the app. Enumerate all of the minor incongruencies in design — like spacing, margins, alignment on left and right sides, etc. — and then fix each in turn… Want this fixed in a mobile responsive way.

And the self-loop directive for a final polish sweep:

> I want you now to go through the design page by page and then itemize and enumerate a list of all possible improvements you can make to make it higher-end, sleeker, and more lux. Self loop as many times as you need to implement all of that design functionality…

> NOTE: For the live-browser inject-then-persist discipline (prove the CSS/layout fix in the browser before writing it to source) the user already runs `chrome-devtools-mcp`. Use it as the engine behind this self-test loop — `evaluate_script` to inject, `take_screenshot` to verify — then persist.

**Phase 6 — final device check (mandatory, non-negotiable).** Chrome/mirror is NOT enough. Run on a real phone via Expo to feel haptics, hear the chime, and test the camera/photo UX. Three-tier ladder: computer/Chrome → phone mirror (iPhone Mirroring app) → real physical phone. Catch issues at the cheapest level first. (Phone testing stays manual; budget +10-15 min per error. See `expo-go-test.md`.)

**Be deliberate before each prompt — "I am spending tokens."** Know the exact card layout you want before directing the AI; the "80/20" framing closes each pass.

---

## Concrete design bugs from the build (recognize and fix these on sight)

These recurred across the habit-tracker and CalTracker builds — pattern-match them in your own QA:

- **Invisible text/icons** — font color == background color, so check-mark icons and text on History/Manage pages vanish. Widespread across habit-type selectors and habit names. Most common bug. ("the font color that you're using is the same as the background color for a lot of these icons. The check mark icon for instance is invisible…")
- **Wrong stats math** — "exercise 3% after one day" implied a 30-day denominator while the label said 7 days. Verify the percentage denominator matches the stated challenge length.
- **Text wrap + left-align** — "current streak / best streak" wraps on mobile and defaults to left-aligned (looks off). Tighten copy or fix alignment.
- **Single global reminder** — one 9:00 a.m. reminder across all habits. Need per-habit, customizable date/time reminders + a **confirmation button** (users can't tell a reminder is set without one) + add/delete/rename reminders (a 2-meal user deletes "dinner").
- **Reminder section cut off** — borders weren't rounded → combine into one "seamless, fluid" section.
- **Over-generated icons** — asked for 15 (3 rows × 5), it produced 17, spilling the layout. ("On the manage page, add five more icons… for the placeholder text, morning run, capitalize the R.")
- **Invisible container** — new-challenge section indented weirdly because a hidden div/box's background matched the page.
- **Counted-habit layout** — "healthy meal 3/3" looked broken because the count sat under a centered icon. Fix: everything on one line.
- **Weird checkboxes** — new-challenge edit section rendered checkboxes that looked unfinished / unapplied styles.
- **Tight card spacing** — streak/best/7-day-average cards too tight vertically; add vertical spacing between emoji, number, descriptor.
- **Fixed-width breaks mobile** — height feet/inches inputs and the weight-log field spilled off the right edge because widths were fixed, not responsive. "make them a lot tighter."
- **Small-display overflow** — calorie + macro cards spilled to four lines. Combine calorie + macro lines with abbreviations/compressed/smaller text; cap cards at **two lines max** on tiny displays (check actual aspect ratio + pixel counts to pick a target). "You can truncate the text, but do so significantly wider… combine the calorie and macronutrient lines using a smart combination of abbreviations…"
- **Stray off-palette toggle** — a green meal-reminders switch kept reappearing off-palette across multiple passes; re-prompt to a blue shade more than once: "make it a shade of blue similar to the rest of our color palette."
- **Delete hit-target bug** — full-screen entry delete failed when tapped top-right, worked lower down (UX/hit-target, not a data bug).
- **x-axis font drift** — the weight-graph x-axis labels came out serif; "I want sans serif." (Also: a weight trend line needs ≥2 weigh-ins on 2 SEPARATE days — so backdated weight logging is required for the chart to render at all.)

**Reward visuals (the core loop made real):** crown/trophy + **confetti particle burst (reanimated)** + chime. Confetti is CPU-heavy — fine for proof-of-concept, a "cracked-out app dev" might avoid it in production. The chime/sound uses **Expo AV** (swappable). The reward being re-triggerable on purpose ("I can trigger it over and over because I'm addicted to that paper") is the retention-by-design point, not a bug.

**Developer testing view (build this so you don't "just trust it works"):** simulate full challenge completion, force complete challenge, reset onboarding, clear all data. Lets you fast-forward the 3-day kickstart to verify the completion animation/achievement, then do a clean from-scratch run by resetting onboarding + clearing all data.

---

## The standard build framework this design step lives inside

Design is one named step in the repeatable per-app/per-feature pipeline — "Whether you're implementing a whole app or a new feature, this is the exact same flow." Insert **design between build and test**:

1. MVP ideation (the 5-part framework above)
2. Build (scaffold + first demo → `expo-scaffold.md`)
3. **Design** (this wrench — the iterate-on-design loop)
4. Test (computer/Chrome → mirror → real phone → `expo-go-test.md`)
5. Add database + auth (`supabase-mobile.md`)
6. Test again
7. Security audit (`mobile-security-audit.md`)
8. Third end-to-end test
9. Deploy (`ship-to-stores.md`)

There's an emerging class of SaaS that takes existing app functionality and respins the design 5-10 ways (move icons, restyle) to appeal to different user subsets — the design step is exactly what enables that. While Claude implements a change in one window, you can run a parallel/second app window and keep clicking through (logging meals/weight) and even dump in the NEXT change before the previous one finishes, since changes tend to be well-separated.

---

## What this wrench does NOT do

- **Visual brand identity / a real design system (tokens, type scale, component library, logo).** This wrench is product-design heuristics + the iterate loop, not brand. Route deep visual-system work to **ui-ux-pro-max / design-studio** (`../../design-studio/SKILL.md`). `frontend-design` / `vercel:shadcn` are web, not RN — don't pull them in for the mobile screen layer.
- **Write the actual RN component code.** Per AGENTS.md rule #5, Codex is the default code lane — Claude produces the spec/design direction, Codex implements. Route via `router` → Codex.
- **Project init / scaffolding / file-based routing / dev-environment setup.** → `expo-scaffold.md`.
- **Running the live app on a device / Expo Go pairing / on-phone hot-reload.** → `expo-go-test.md`.
- **Generic runtime selection (native vs RN/Flutter vs Capacitor) and base stack defaults.** Already owned by the existing `build/mobile` wrench — this mechanic supersedes it for the opinionated Expo/RN path and routes back only for the "which runtime" decision when the stack is NOT Expo/RN.
- **DB schema, RLS, auth wiring.** → `supabase-mobile.md`. **In-app AI features (coaching, reports) via Edge Function → Claude API.** → `edge-fn-claude-ai.md`.
- **App-store submission / EAS build profiles.** → `ship-to-stores.md`. **Git/commit/tests/PR/CI plumbing.** → `ship` mechanic.
- **Security audit of exposed keys / client trust boundaries.** → `mobile-security-audit.md`; deep infra security → `cso`.
- **Live browser inject-then-persist execution** is the engine, not the policy — driven via the `chrome-devtools-mcp:chrome-devtools` plugin skill (invokable by name; the discipline lives in that plugin's skill body).

---

## See also

- [`expo-scaffold.md`](expo-scaffold.md) — project init, file-based routing, scaffolding scope (carries the "designing a successful app" framing as it pertains to scaffolding).
- [`expo-go-test.md`](expo-go-test.md) — device pairing + on-phone hot-reload; the mandatory Phase-6 real-device check.
- [`supabase-mobile.md`](supabase-mobile.md) — wire the DB/RLS/auth AFTER design is verified on local storage.
- [`edge-fn-claude-ai.md`](edge-fn-claude-ai.md) — Edge Function → Claude API for AI coaching/report features.
- [`ship-to-stores.md`](ship-to-stores.md) — EAS build + store submission.
- [`mobile-security-audit.md`](mobile-security-audit.md) — pre-launch key/trust-boundary audit.
- [`../SKILL.md`](../SKILL.md) — the mobile-app mechanic (dispatches across these wrenches).
- [`../../design-studio/SKILL.md`](../../design-studio/SKILL.md) — ui-ux-pro-max / design-studio for the visual brand + design-system layer.
- [`../../cso/SKILL.md`](../../cso/SKILL.md) — deep infrastructure security audit.
