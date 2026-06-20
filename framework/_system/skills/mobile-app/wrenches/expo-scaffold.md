---
name: expo-scaffold
description: Wrench inside the `mobile-app` mechanic. Takes a mobile app from nothing to a running, on-device Expo + React Native build — workspace init from a single Claude Code prompt, project structure / dev-environment setup, the `/init` + `/clear` CLAUDE.md ritual, the Claude-Code-driven build loop (demo → MVP → iterate via Chrome), plus Nick Saraev's five-part "designing a successful app" framework that scopes the MVP before any real code. This is the opinionated Expo/RN entry point that SUPERSEDES `build/mobile` for the Expo path; routes back to `build/mobile` only for the "which runtime" decision when the stack is not Expo/RN. Codex is the default code lane for the actual app code (AGENTS.md rule #5); inside this Claude-Code-in-a-terminal workflow Nick drives Claude directly, so Claude authoring is the documented carve-out here. Fires on "start a mobile app", "scaffold an Expo app", "new React Native project", "build me a mobile app" (Expo/RN path).
---

# expo-scaffold — nothing to a running app (Expo + React Native via Claude Code)

The from-scratch pathway for the `mobile-app` mechanic. Spins up an Expo + React Native workspace from a single Claude Code prompt, scopes the MVP with the five-part app-design framework, builds a rough demo, locks it down with the `/init` → `/clear` CLAUDE.md ritual, then drives the MVP build loop through Chrome (`localhost:8081`) with the physical phone reserved as the final check. This is Nick Saraev's full-course workflow ("How to Build Mobile Apps with Claude Code", 2026), normalized to Claude-Code-in-a-terminal (no Antigravity).

**Cardinal: web-first, then port, then optimize.** Build as a web application FIRST (runs in a browser, can ship to a website), THEN port to phone, THEN optimize for phones and tablets. Simplest, most straightforward path. The dev loop happens on the computer (Chrome at `localhost:8081`); the phone is the final experience check.

**Cardinal: scope the MVP with the five-part framework before any real build.** Core function → core loop → accessory features → surface-area check → retention hook. Feed that high-level design to Claude as text and it becomes the build spec. Skipping this produces bloat — "millions of pages" — instead of one thing done well.

**Cardinal: make Claude do the work, don't take the handoff.** When Claude tries to hand you a command to run ("run `npx expo start`"), tell it "do this for me in a new terminal window." That single move "does 80 to 90% of the work." The hard part of app building is not the code — it's building the RIGHT things and getting them onto the internet.

**Cardinal: test on the real physical phone, never just mirroring.** iPhone Mirroring hides navigation/UX problems and gesture-based hidden functionality (swipe left/right, pull-and-drag). Nick only discovered an auto-created "create a new habit" page by using his actual phone. Mirroring also can't be zoomed enough for the dev loop — that's what Chrome is for.

---

## Prerequisites — Claude Code, plan, smoke test

The user already runs Claude Code in a terminal — skip the install fluff. For reference / onboarding others:

- **Plan:** Claude **Pro at $20/month** is sufficient for the whole course ("probably the highest return on investment you will ever get"). Max is "several hundred a month" (the plan Nick runs his ~$300K/month business on).
- **Surface:** Claude Code, not vanilla Claude chat — chat alone cannot develop/design mobile apps. All surfaces (web app, desktop app, third-party shell) are "just wrappers around the brain of the model." the user's choice: Claude Code in a terminal scoped to the project folder, with a file tree alongside (file-level granularity → more sophisticated apps).
- **Login (if needed):** `/login` then sign in via the browser flow. Success = a working chat plus the Claude Code "space invader" icon present. If "Hey, what's going on?" gets no response, you're not logged in.
- **Smoke test (for a fresh install):** open an empty project folder, prompt `make me a really simple one-page site in the current directory. Then open it.`, then `adjust this so it greets me, Nick.` — confirms the build + edit loop works.

**Autonomy toggle:** Nick enables **"dangerously skip permissions"** so Claude acts without per-step approval. (the user already runs no-prompt-by-default per AGENTS.md, so this is the default posture here.)

> Aspirational end-state Nick anchors to: **Cal AI** (AI calorie-photo app, reportedly sold for $50M–$100M to MyFitnessPal) = cloud + API + authentication + database.

---

## Phase 1 — Scaffold the Expo workspace (one prompt)

Start from an **empty project folder** — delete any leftover files (e.g. an `index.html` from a smoke test) so nothing pollutes the build. Claude Code already knows Expo's setup and the files needed for a working app; it scaffolds the whole workspace itself rather than downloading a template.

The verbatim init prompt:

```
I want to build a mobile app with Expo and React Native. Set up my workspace for me.
```

Claude generates the entire Expo/React Native workspace. Stack this maps to (deeper than `build/mobile`'s RN defaults):

- **Expo** (managed) + **React Native**, one JS/TypeScript codebase → iOS, Android, and web
- **Expo cloud builds** (EAS-style — offloads builds to a standardized tool; hot reload on device)
- **Expo Go** as the mobile companion app for on-device runs (see `expo-go-test.md`)

---

## Phase 2 — Build a rough demo and run it on the phone

Before scoping the real app, build a throwaway demo to prove the loop end to end. Verbatim prompt:

```
create a simple demo application, some habit tracker for demo purposes, and then let me launch it on my phone
```

- Planning the demo takes ~1.5–2 minutes. Claude writes the app code into files and **solves its own errors** as they appear. Minor errors (e.g. `uncaught for promise ID 1`) can be **ignored** — focus on core functionality.
- **Demo builds store data locally by default** (no database, no backend) when you just ask for a "demo." Local storage on the phone.
- When done, Claude reports what it built (the demo had a **Today tab**, a **Manage tab**, and **local data persistence**) and gives run instructions: install Expo Go, run the start command, scan a QR code.

The start command Claude will try to hand you:

```
npx expo start
```

**Do not run it yourself.** Tell Claude:

```
do this for me in a new terminal window
```

Claude opens a new terminal window it manages, runs the local dev server, and displays a large QR code. Then on the phone:

1. Install **Expo Go** from the App Store (search "Expo Go") or Play Store. Nick uses iPhone for simplicity; Android equivalents exist.
2. Open Expo Go and **log in / sign up** — an account is required before you can load the app.
3. Scan the QR code, open the `exp://` link (enter your passcode if prompted). The app launches directly on the phone.

iPhone Mirroring can show the phone on desktop for demos, but **real testing runs on the physical phone** (per the Cardinal — catches nav/UX issues and hidden gestures).

---

## Phase 3 — Lock it down: `/init` then `/clear` (the CLAUDE.md ritual)

After the rough demo exists, generate the system file that teaches Claude the app on every init without re-reading every file (saves tokens — "most of the time you're billed by token or your token usage consumes your plan").

```
/init
```

This writes **`CLAUDE.md`** at the repo root. It opens with the line:

```
This file provides guidance to Claude Code when working with code in this repository.
```

It stores: the **architecture** of the app, the **theme**, the **state**, and the **path(s) to files** — "everything that you need in order to basically run it." Purpose: on every initialization Claude knows what the app is and where all the files are, without crawling every file itself.

Then reset the conversation context:

```
/clear
```

The token meter on the right resets to "basically nothing." Continue building from a clean slate that's still anchored by `CLAUDE.md`.

> Why this order: build a brief demo → `/init` (so CLAUDE.md captures a real, working app, not an empty shell) → `/clear` (reclaim the context budget) → continue.

---

## Phase 4 — Design the app (five-part framework = the MVP spec)

Run this BEFORE scoping the real build. The five elements in order; combine all five and you have an MVP scope to feed Claude as text. Nick dictates the spec by voice (he uses **Aqua** voice transcription into the mic instead of typing). When you paste/dictate a long prompt the terminal collapses it to `pasted text #1 + 8 lines` — press enter to populate it.

1. **Core function** — the one thing that, if you removed everything else, the app would still be the app. Habit tracker: create a habit, tap it, each tap logs to a database. *Annotation: "core function = track a habit".*
2. **Core loop** — a cycle mapping an **action → reward**, ideally under **~30 seconds**. Humans are tactile, so stack sensory rewards: a nice sound on tap, animation on tap, confetti at a goal, haptics/vibration. *Annotation: "core loop = some stimulating reward".* (Reward can be made arbitrarily complex — monetary stakes, an accountability partner you pay if you miss — Nick keeps his simple. Opal's escalating gem that grows shinier per consecutive day is his gold-standard example; not sponsored.)
3. **Accessory features** — wrap around and support the core loop without changing it: a list/history of past logs ("on May 4th you logged X"), a chart/visualization tied to logging (*"chart + logging"*), habit customization including multi-tier habits (daily/one-shot vs count-based like cups of water), optionally a social feature (add friends, get notified when they log).
4. **Surface-area check** — minimize digital surface area. Don't bloat into 10 core functions, 100 loops, 1000 features. Aim for a simple core loop served by a handful of screens a user understands in one run-through with no onboarding explanation. "In a world where you can do everything... it's about doing one specific thing really well."
5. **Retention hook** — create an **unfinished state the user must return to.** Nick's starter: a **3-day challenge** (log the habit every day for three days → forces three visits over a 72-hour window). Alternative: scheduled check-ins / push notifications that "knock on the door." Never design for one-time use — "any app claiming one-time use as its goal is lying"; build in retention (leveraging dark patterns in user behavior).

> "If you have all five of these things, you now basically have an MVP... at least the MVP you can give to Claude to turn into the actual thing. You have a scope."

---

## Phase 5 — The MVP build loop (drive it through Chrome)

Feed the framework to Claude as the build spec. The verbatim spec preamble Nick dictated:

```
Hey, so I really like the app as it stands, but I'd like to level this up with an app design framework that high-quality app devs and designers use where essentially every app that I build requires a core function, then a core loop, some accessory features, a surface area check to minimize the number of screens, and then some sort of retention hook.
```

Then fill in each element specifically (verbatim, condensed to the load-bearing parts):

```
The core function for this app is it needs to be able to create and then track habits. The core loop ... every time a person creates a habit and then tracks it, they need to be rewarded ... visually stimulating ... some form of haptic feedback and ... ideally there's some sort of sound like a chime. Also, we need some form of challenge ... a 3-day habit challenge ... immediately after onboarding ... at the end of that 3-day challenge ... reward them for the fulfillment of their efforts.

The accessory features ... logging. The user should be able to see all of their prior habits tracked, some sort of accountability thing ... a graph or chart of how consistent they've been ... a way to create multiple types of habits ... a habit where you log it once per day is different from a volume based habit where you need to do it three or four times a day.

For surface area check just make sure that we don't have more than somewhere between five to seven screens in our app. We want it to be as simple as possible.

And then in terms of retention hook ... create challenges for the user ... some sort of ongoing thing that checks in with them via push notifications probably once a day or maybe a couple times a day. Just consistently knocking on their door, seeing whether or not they've done the habit.
```

**Switch testing to Chrome for the dev loop.** Tell Claude to open in Chrome, not Expo — the iPhone Mirroring app can't be zoomed/enlarged enough for development. **`8081` is Expo's default port** — per SKILL.md cardinal rule 5, allocate this project's port from `_system/second-brain/dev-registry/ports.md` (take the next free one, write it back) and bake it in with `npx expo start --port <n>` so parallel projects don't collide on 8081. Open that port in Chrome. Reserve the physical phone (via Expo) for the **final** check — you can't feel haptics or hear the chime in a browser.

**Force all phases at once.** Claude defaults to conserving tokens/effort — it proposes breaking a substantial build into phases and "won't try as hard as it realistically can." Counter it. Verbatim:

```
No, I just want you to do the whole thing. I'd like us to do all of it, including phase 1 through 4. Once done, open in Chrome, not Expo, so I can test locally.
```

It spent ~1m29s mapping the framework, ~5 min building phases 1–4, and may auto-open Chrome tabs as part of its own internal testing loop. Let it run.

### The six-screen MVP layout Claude proposed (cap: 5–7 screens)

```
1. Onboarding / first-launch — picks three habits for you, starts a 3-day challenge
2. Today      — daily checklist (the core loop)
3. History    — calendar/graph of past completions + a consistency chart
4. Manage     — add/remove a habit, configure habit type
5. Challenge  — view challenges you're currently enrolled in
6. Settings   — notification preferences, theme
```

Rendered app: three bottom navigation tabs. Habit types: **daily** (log once/day, e.g. sleep before 9pm) vs **count/counted** (volume-based, e.g. water 8x/day). Challenge durations: 3-day, 7-day, 14-day, 30-day. Seeded habits seen: exercise, meditate, drink water, healthy meal, journal, sleep 8 hours.

### Reward/animation libraries Claude reached for

- **reanimated** — the confetti particle burst on completion. (CPU-heavy, fine for a proof-of-concept; a "cracked-out app dev" might avoid it in production.)
- **Expo AV** — the library typically used for sound/audio (an opinionated dev could swap it).
- Completion reward visuals: crown/trophy + confetti (reanimated) + chime.

---

## Phase 6 — Iterate via narrowing Chrome feedback passes

Manually test every screen in Chrome, then run **progressively narrower** voice-dictated feedback passes. On a refine pass, explicitly tell Claude you're making minor changes only ("We're not actually building the whole thing now"), list every issue top-to-bottom, and have it open a fresh Chrome tab. Each pass ends with an 80/20 framing.

Recurring bugs from the actual build (watch for these — they recur in Claude RN output):

- **Invisible text/icons** — font/text color came out the same as the background; the check-mark icon was invisible, and text on History and Manage pages disappeared. Widespread across habit-type selectors and habit names.
- **Wrong stats math** — "exercise 3% after one day" implied a 30-day denominator while the label said 7 days. Verify percentage denominators match the stated challenge length.
- **Mobile text wrap** — "current streak" / "best streak" wraps on mobile and defaults to left-aligned, looking off. Tighten copy or fix alignment.
- **Single global reminder time** (9:00 a.m. across all habits) instead of per-habit. Add per-habit, customizable date/time reminders **plus a confirmation button** so users know a reminder is actually set.
- **Reminder section cut off** because borders weren't rounded — combine into one seamless, fluid section.
- **Over-generated icons** — asked for 15 (5/row × 3 rows), produced 17, spilling layout.
- **"Weird checkboxes"** on the new-challenge edit section — looked unfinished / unapplied styles.
- **Invisible container** — new-challenge section at top of Today indented weirdly; a hidden div whose background matched the page.
- **Counted-habit layout** — "healthy meal" 3/3 looked broken under a centered icon; fix to put everything on one line.
- **No-op `set` button** that did nothing; a skip button on onboarding Claude added for developer convenience.

The confetti/chime loop is **intentionally addictive** ("I can trigger it over and over because I'm addicted to that paper") — that's retention-by-design, not a bug.

### Build a developer testing view

To properly test the 3-day kickstart you must build dev tools, or you "just have to trust that it's working." Verbatim ask:

```
I need some sort of testing view for a developer so that I can modify the day of the challenge or at least trigger the event that occurs when we hit let's say 3 days out of the 3-day kickstart.
```

Tools Claude built: **simulate full challenge completion, force complete challenge, reset onboarding, clear all data.** Use them to fast-forward the 3-day kickstart and verify the completion animation/achievement.

### Final validation on the physical phone

Do a clean from-scratch run (reset onboarding + clear all data), then start an Expo server and run on the **physical phone** to validate haptics, chime, and the real experience before shipping. "If you can't physically play with the haptics, hear the chime... you're not really getting the whole experience." Hand off to `expo-go-test.md` for the device loop and `ship-to-stores.md` to release.

---

## App-complexity progression (the course ladder)

Follow this escalation across builds — the habit tracker is deliberate, not trivial ("the means to an end"): it exercises a DB, read/write/modify, a front end that talks to the DB, and authentication.

```
1. Local habit tracker  — NO API, NO database (local storage on the phone)
2. + an API             — wrap someone else's functionality
3. + a database
4. push to a cloud solution
5. Full app             — cloud + API + authentication (login) + database (≈ Cal AI)
```

Each rung up the ladder routes to a sibling wrench: API/DB/auth → `supabase-mobile.md`; in-app AI features → `edge-fn-claude-ai.md`.

---

## What this wrench does NOT do

- **Does not pick the runtime.** This wrench assumes Expo + React Native. For the "which runtime" decision when the stack is NOT Expo/RN (native Swift/Kotlin, Flutter, Capacitor), defer to [../../build/wrenches/mobile.md](../../build/wrenches/mobile.md). Nick's runtime rationale for reference: he chose Expo+RN over Flutter+Firebase+Dart (Google's opinionated material design limits custom design; avoids an unfamiliar language + Firebase lock-in) and over Capacitor (website-first, not app-first — "optimizing for everything means you're not great at anything").
- **Does not write the production app code by default.** Per AGENTS.md rule #5, Codex is the default code lane via `router`. The carve-out: inside this Claude-Code-in-a-terminal demo loop, Claude authors directly (that's the workflow Nick teaches). For larger structured builds, route per-file specs to Codex.
- **Does not design the visual brand / design system.** UI/UX component patterns, navigation, and design heuristics → [rn-expo-ui.md](rn-expo-ui.md). Deep brand + design-system work → [../../design-studio/SKILL.md](../../design-studio/SKILL.md).
- **Does not wire Supabase / auth / database.** → [supabase-mobile.md](supabase-mobile.md) (uses the Supabase MCP for live ops).
- **Does not add in-app AI features.** The Edge Function → Claude API pattern → [edge-fn-claude-ai.md](edge-fn-claude-ai.md).
- **Does not run the live app on a device / handle hot-reload pairing.** → [expo-go-test.md](expo-go-test.md).
- **Does not handle app-store submission.** EAS Build, TestFlight, App Store Connect, Play Console → [ship-to-stores.md](ship-to-stores.md).
- **Does not run the pre-launch security audit.** → [mobile-security-audit.md](mobile-security-audit.md).

---

## See also

- [../SKILL.md](../SKILL.md) — mobile-app mechanic
- [rn-expo-ui.md](rn-expo-ui.md) — UI/UX patterns, navigation, design heuristics, the iterate-on-design loop
- [supabase-mobile.md](supabase-mobile.md) — Supabase client, schema, RLS, auth (rungs 2–5 of the ladder)
- [edge-fn-claude-ai.md](edge-fn-claude-ai.md) — Edge Function → Claude API for in-app AI
- [expo-go-test.md](expo-go-test.md) — Expo Go device pairing + on-phone hot-reload loop
- [ship-to-stores.md](ship-to-stores.md) — EAS Build + TestFlight / App Store + Play Console
- [mobile-security-audit.md](mobile-security-audit.md) — pre-launch security-prompt audit
- [../../build/wrenches/mobile.md](../../build/wrenches/mobile.md) — "which runtime" decision when NOT Expo/RN
- [../../router/wrenches/codex.md](../../router/wrenches/codex.md) — Codex dispatch for structured per-file code writing
- [../../windows-launcher/SKILL.md](../../windows-launcher/SKILL.md) — clickable launcher for the Expo dev server
- [../../second-brain/SKILL.md](../../second-brain/SKILL.md) — capture project decisions; `dev-registry/ports.md` for `localhost:8081`