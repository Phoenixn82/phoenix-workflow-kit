---
name: expo-go-test
description: Expo Go device pairing + on-device hot-reload testing + the on-phone debug loop — runs the LIVE app on a real phone via QR code, catches the errors that never show up in local/Chrome preview, and feeds runtime logs straight back into Claude Code to diagnose. Also covers the iPhone-Mirroring screen-test rung and the GitHub version-control checkpoint that anchors the on-device test cycle. Code edits route to Codex (AGENTS.md rule #5); Claude steps in to diagnose pasted error logs and direct the debug loop. Fires on "test the app on my phone", "Expo Go", "run it on a device", "debug on phone", "QR pairing", "scan the QR code", "why does it error on my phone but not locally", "test the live app".
---

# expo-go-test — run the live app on a real phone

Closes the gap that `build/mobile` explicitly leaves open: **it does not run the live app.** This wrench is the on-device loop — start an Expo dev server in a *new terminal*, scan the QR code into Expo Go, drive the real app with your thumb, and when it errors (it will error in ways local preview never does) paste the entire log into Claude Code and let it diagnose. It also anchors the test cycle with a GitHub version-control checkpoint so on-device iteration has a rollback point, and chains up the testing ladder: **computer/Chrome → phone mirror → phone reel.**

**Cardinal: Start the Expo dev server in a NEW, SEPARATE terminal window — never the same terminal Claude Code is running in.** If it runs locally in Claude Code's terminal, the QR-code-to-phone flow does not work and you cannot scan it onto the device.

**Cardinal: Running on a real phone surfaces errors that NEVER appear locally.** Push notifications, the iOS permission prompt, and AsyncStorage incompatibilities only manifest on-device. On-device testing is not optional polish — it is where the real bugs live.

**Cardinal: To fix any runtime error, copy ALL the error messages verbatim and paste them straight into Claude Code with no extra wording.** Do not interpret them yourself. Claude diagnoses (this is the Claude carve-out on the code lane); Codex applies the fix.

---

## Phase 1 — Pair Expo Go to the phone

1. In a **new terminal window** (separate from Claude Code), start the Expo dev server. Prompt Claude Code with intent:
   > start an expo server for this in a new terminal window — run it on my phone so I can see the QR code
2. The QR code prints in that new terminal. **Scan it with the phone camera** to open the app inside Expo Go.
3. The app loads on-device with hot-reload. From here, every save re-bundles to the phone.

```
# Server lifecycle in the Expo terminal (Mac keys; on-device hot-reload loop):
Ctrl+C        # hold Control, press C → kills the running Expo server
              # (then clear the terminal)
Up arrow      # recall + re-run the LAST command → restarts Expo
              # re-scan the QR code to reload in Expo Go
```

> "it's important to say new terminal window because if it does so locally here, you'll find that you can't actually take the QR code ... flow" — 00:55:02

---

## Phase 2 — The on-phone debug loop

On-device behaves differently from the computer. Expect errors that did not appear in local/Chrome preview. The loop:

1. **Drive the live app on the phone.** Tap, scroll, long-press, complete a flow (e.g. `force complete challenge` to exercise that path).
2. **When a runtime error appears** — typically an `uncaught in promise` line at the bottom of the log, or a get-item failure — **copy ALL the error messages.**
3. **Paste the full log straight into Claude Code, verbatim, no extra wording.** Claude diagnoses.
4. **Codex applies the fix** (AGENTS.md rule #5). Claude reviews spec compliance.
5. **Re-run:** `Ctrl+C` to kill the server → clear terminal → press **Up** to recall the last command → re-run → re-scan the QR code to reload in Expo Go.
6. Repeat until clean.

### Known on-device gotcha: AsyncStorage v3 ✗ Expo Go

The canonical example from the transcript. **AsyncStorage v3 is NOT compatible with Expo Go.**

```
Symptom : 'uncaught in promise' at the bottom of the log + a get-item failure on-device
Cause   : @react-native-async-storage/async-storage v3 incompatible with Expo Go
Fix     : downgrade to ~v2.2.0 (Claude identifies this after you paste the logs; Codex pins it)
```

> "When this occurs, just copy over all of the error messages. Okay, paste it into [Claude Code]. ... now you're seeing it's saying the async storage v3 isn't compatible with expo go. We're going to download v2.2.0" — 00:56:06

### What ONLY the real phone reveals

- **Push notifications + the iOS permission prompt** ("...would like to send you notifications") fire **on-device only**, never in local preview. The prompt appears **only when the user clicks the relevant button** — it is deliberately *not* forced on first launch (lower-friction UX).
- **Thumb-reach UX.** A phone is driven with a **thumb**, not a mouse. Verify that most major functionality sits within thumb's reach; check scroll behavior and long-press interactions you cannot catch coding on a computer.
- **Visual bugs against real hardware.** Icons cut off vertically / "heads cut off"; the iOS time overlaying the date at the top. Feed each back to Claude as a concrete prompt, e.g.:
  > there's not a lot of visual space up top ... the time is basically immediately overlaying the date ... add some sort of padding up at the top to accommodate for the fact that the iPhone has its own little bar (the notch / status bar with battery, time, etc.)

> "me as a user, I'm going to be mostly using my thumb. So, it's actually important that most of the major functionality is sort of within thumb's reach." — 00:59:35

---

## Phase 3 — The testing ladder (where Expo Go sits)

From the roadmap, on-device testing is rung 2 of 3:

```
(1) test on the computer / in Chrome        ← rn-expo-ui.md autonomous Chrome DevTools loop
(2) test with phone mirror (iPhone Mirroring app)   ← THIS WRENCH
(3) phone reel / final recording
```

- **iPhone Mirroring app (macOS)** lets you demo the on-device app on screen, including haptics. The mirror window is **quite small — just deal with it** when demoing.
- **Windows adaptation (rung 2 is macOS-only):** iPhone Mirroring does not exist on Windows. On this machine, substitute scrcpy or Phone Link for an Android device, or drop to a two-rung ladder — Chrome at a mobile viewport (rung 1) → the physical phone via Expo Go (skip the on-screen mirror). The on-device debug loop (paste runtime logs into Claude Code) is identical either way.
- The mirror **cannot screen-record the camera/photo feature** (it bugs out / can't show the live camera) even though the camera works fine on-device. Demo camera UX directly on the phone.
- Real-hardware testing surfaced the working MVP: notification sounds + completion animation, a history view with correct dates/times, an example habit, "one day completed, three habits tracked", and creating a new challenge (e.g. `healthy meal → start challenge`).
- Note residual misalignments **only visible on the real phone** (e.g. left-most height/weight not aligned with the text underneath) and queue them for the next fix pass.
- **Expo Go ≠ live on the store.** Testing in Expo Go is NOT the same as being published — that requires actually pushing/publishing the app (see `ship-to-stores.md`).

---

## Phase 4 — GitHub checkpoint (anchor the on-device cycle)

Before/after a hard on-device debug session, push to GitHub so iteration has a rollback point.

1. Prompt Claude Code:
   > Great, create a GitHub repo for this as well as a readme then push
2. **Authenticate to GitHub** if prompted (opens a page to log in / connect). GitHub signup is free; it may ask for email + phone number (double verification).
3. The repo gets **auto-named `example project`** (or whatever the folder is). Rename both the repo and the local folder to a meaningful name:
   > rename it to habit tracker and rename this folder as well
4. **Renaming/reopening the project folder REVERTS your Claude Code session** — you will NOT be in the same session afterward. Finish or checkpoint work first.
5. **Verify on GitHub:** the repo shows all code, commit history (changes from "X minutes ago"), and collaborators. **Claude always auto-adds itself as a collaborator**, so the repo shows two people (Claude + you).

```
Commit / repo metadata you will see on GitHub:
- GitHub repo name        (rename example project → habit tracker)
- README                  (created + pushed with the repo; may still reference
                           the old name until you re-prompt or edit/commit it)
- collaborators list      (Claude auto-adds itself; you are the other)
- commit message + time of change + the specific files changed (in commit history)
```

> "Claude always likes adding itself as one of the collaborators on any project now, which I find hilarious." — 01:02:37
> "It will have reverted our session though. So just keep that in mind. You won't be in the same session." — 01:03:10

**After reaching MVP, update `CLAUDE.md` again** so it describes all the new functionality. `CLAUDE.md` is auto-loaded into every Claude Code conversation — a stale one misinforms every future edit.

> "you should update that [CLAUDE.md] again ... [it] provides all of like the base information and is immediately loaded into every conversation ... should describe like all of the additional functionality." — 01:00:36

---

## Why design-iterate on local storage BEFORE this loop forces a DB push

On-device testing surfaces the need for cloud persistence, but **do all design + data iteration while storage is still LOCAL (AsyncStorage).** Local-only data lives on a single device — send the app to someone else and they can't use your data; it won't sync between phone and computer. That is the whole reason to add a database *later*. But once a live Supabase DB exists, every design/data change forces a new schema push and consistently deprecates old data, ballooning the test loop. Iterate cheap on local first; migrate to Supabase only after design + on-device UX is verified.

> "If we were to try and make all these modifications after we had like an actual live database, every time we do this, we have to push to like a new schema inside of [Supabase] ... and then also consistently deprecate any old data." — 02:44:07

When it IS time to migrate, hand off with the full intent in one prompt and **parallelize** — have Claude work on everything it can while you create the free Supabase account:
> I'd like to add a database ... I also want local caching so the user has a very immediate and snappy experience ... We're going to be using Supabase ... we're going to need to set up user authentication so that you know which user is accessing which data. Help me through this process.
> I don't yet have Supabase set up, but I'll do that now. Let's go with email and password. Work on everything that you can up until that point.

**Keep AsyncStorage as the immediate read layer even after the DB lands** — writing/reading the DB on every change adds milliseconds-to-seconds of lag; cache locally and sync periodically so the app stays snappy with no added initial load. (Full schema/auth/RLS wiring → `supabase-mobile.md`.)

> "we're going to keep async storage as the immediate read layer so the app feels instant ... We're just going to add the database and periodically sync." — 01:11:46

---

## Costs

- **Claude Code:** $20/month subscription. Nick built a habit tracker "better than 90% of what is currently available on the app store" for roughly **50% of one session's usage** (sessions reset every couple of hours).
- **GitHub:** free to sign up (may ask for email + phone / double verification).
- **Supabase:** totally free to create an account and start a project (the migration target, not part of this loop).
- Context: Nick's first app (for "1 Second Copy", a company he scaled past $90,000/month) — the DB/SQL schema setup alone took ~2.5 of 3 weeks back then; with AI it now takes ~30 seconds.

> "It's a $20 a month subscription. I was able to build a better app than 90% of what is currently available on the app store and I was able to do it ... entirely myself." — 01:00:04

---

## What this wrench does NOT do

- **Scaffold the Expo/RN project or set up the dev environment** → `expo-scaffold.md`.
- **UI/UX patterns, the autonomous Chrome DevTools screenshot-and-fix loop, design iteration, MVP scoping** → `rn-expo-ui.md` (rung 1 of the testing ladder).
- **Visual brand / design system** → routes through `rn-expo-ui.md` to `../../design-studio/SKILL.md` (ui-ux-pro-max / design-studio).
- **Supabase client setup, schema/tables, RLS, auth flows** → `supabase-mobile.md` (uses the Supabase MCP for live ops).
- **In-app AI features via Edge Function → Claude API** → `edge-fn-claude-ai.md`.
- **EAS Build, TestFlight, App Store / Play Store submission ($99/yr Apple, $25 one-time Google)** → `ship-to-stores.md`. Expo Go is NOT publishing.
- **git/commit/tests/PR/CI plumbing** beyond the checkpoint push → `../../ship/SKILL.md`.
- **A clickable desktop launcher for the Expo dev server** → `../../windows-launcher/SKILL.md`.
- **The actual app code edits** → Codex via `router` (Claude thinks/diagnoses, Codex does; AGENTS.md rule #5).
- **The "which runtime" decision when the stack is not Expo/RN** → defer to the `build/mobile` wrench; the mobile-app mechanic supersedes build/mobile for the opinionated Expo/RN path only.
- **Pre-launch security audit of exposed keys / client trust boundaries** → `mobile-security-audit.md`; deep infra security → `../../cso/SKILL.md`.

---

## See also

- [expo-scaffold.md](expo-scaffold.md) — project init, file-based routing, the build loop from nothing to a running app
- [rn-expo-ui.md](rn-expo-ui.md) — UI/UX patterns + the Chrome DevTools test loop (testing-ladder rung 1)
- [supabase-mobile.md](supabase-mobile.md) — the DB + auth migration this loop sets up
- [edge-fn-claude-ai.md](edge-fn-claude-ai.md) — Edge Function → Claude API for in-app AI
- [ship-to-stores.md](ship-to-stores.md) — EAS Build + store submission (the rung past Expo Go)
- [mobile-security-audit.md](mobile-security-audit.md) — pre-launch security-prompt audit
- [../SKILL.md](../SKILL.md) — mobile-app mechanic dispatch
- [../../ship/SKILL.md](../../ship/SKILL.md) — git/commit/PR/CI plumbing
- [../../windows-launcher/SKILL.md](../../windows-launcher/SKILL.md) — clickable launcher for the dev server
- [../../second-brain/SKILL.md](../../second-brain/SKILL.md) — capture project decisions; dev-registry/ports.md for local ports
