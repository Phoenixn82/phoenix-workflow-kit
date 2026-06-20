---
name: ship-to-stores
description: Wrench inside the `mobile-app` mechanic. The Expo/RN release pipeline — prepare for production (app.json + eas.json), EAS Build (free vs paid queue, build profiles), and submit to TestFlight + App Store Connect ($99/yr Apple developer account) and Google Play Console ($25 one-time, business email + verified Android device). Covers required store metadata, 1024x1024 icon, screenshots, privacy/support pages, reviewer sign-in, and pricing/IAP/gambling declarations. Claude Code does all the config + metadata generation, the browser screenshots, and the privacy/support page authoring; the actual app-feature code stays on Codex (AGENTS.md rule #5). Fires on "submit to the App Store", "ship to TestFlight", "EAS build", "publish to Google Play", "release the app".
---

# ship-to-stores — Expo/RN release pipeline (EAS → TestFlight/App Store + Google Play)

Takes a finished Expo/React Native app from "runs on a device" to "live in the stores". Prepares the production config (`app.json` + `eas.json`), runs an EAS production build, and submits via `eas submit` to TestFlight/App Store Connect and to Google Play Console — including all the laborious store metadata, assets, privacy/support pages, and reviewer-login plumbing that gatekeeps submission. The single highest-leverage fact: Claude Code does almost all of this for you — generates both config files, writes and hosts the privacy + support pages, opens the browser and takes the App Store screenshots, and walks you through every submission field.

**Cardinal: never build-and-immediately-submit to production. Run a TestFlight period first.** Skipping the test period is odd and risky — push a private TestFlight link to people in your network so real users hit bugs/jank before public launch, then use analytics post-launch to optimize. (Nick only skipped his ~2-week test window because he wanted to ship the video.)

**Cardinal: you MUST be in the correct project directory before any `eas` command.** If you're not in the project dir when you run build/submit, it breaks. Ask Claude Code for the exact `cd` command ("Give me command with cd") and run it first.

**Cardinal: approval is never guaranteed.** All you can do is maximize the odds — every required page present, a working app, a working reviewer login. If rejected, reviewers usually hand back guidance/steps; feed those back to Claude Code to fix.

---

## Phase 0 — Prepare for production (app.json + eas.json)

The shorthand prompt Nick used in the terminal:

```
prepare for production
```

(meaning: make sure the app is ready to go — all bells and whistles and steps in the right places — then build it, then push it to Apple.)

Then feed BOTH config files into Claude Code so it runs a quick configuration, creates them if missing, and walks you through everything:

```
Generate the app.json and eas.json — run through a quick configuration,
create them if they don't already exist, and walk me through everything
needed to get this up and running.
```

**`app.json`** — Expo/Apple app config. Holds the fields Apple uses to identify the app:

- `name` (app name)
- bundle identifier
- `version` (set to **1.0** for the first submission)
- app `icon` (the 1024x1024 image — see assets below)
- splash screen reference
- Android adaptive icon — a foreground image on a colored background, so it works in dark and light mode

Some `app.json` fields auto-generate as you develop, but **run this final config step before submitting anyway** to confirm everything is 100% good. Let Claude Code apply fixes here — e.g. in Nick's case it added camera + audio runtime permission strings (the app needs audio while the camera is active) and set runtime version policies.

**`eas.json`** — Expo Application Services build/submit config. Generate it alongside `app.json` (feed both in together). EAS reads it to build for production and submit to the stores. This is where the build profiles live (dev / preview / production).

> "We sort of crystallize the app by building it. And building it just like sets a bunch of these parameters automatically so that it runs a lot faster." — the built/crystallized production artifact differs from the live Expo dev app (which expo-go-test handles).

File structure this phase produces / touches:

```
app.json     — Expo/Apple app config (name, identifier, version, icon)
eas.json     — Expo Application Services build/submit config (profiles)
assets/icon.png — the 1024x1024 app icon (referenced by app.json's `icon` field; filename is conventional, not required)
```

Confirm your Apple ID is set up before moving on (create it beforehand if you haven't).

---

## Phase 1 — EAS Build (production)

Paste the build terminal commands Claude Code gives you into your terminal. The step checks whether the EAS CLI is installed and lets you log into EAS.

```
Okay, let's build it.
```

- If you're not in the project directory, ask Claude Code: **`Give me command with cd`** and run that first.
- Log into EAS / Expo. No account? Sign up at **expo.dev/signup**.
- The build runs through portal ID, build, etc. and produces the build artifact (the "finished file" you submit).

**Cost / queue gotcha:** the **free Expo/EAS build tier uses a queue that is much slower** than the paid tier. Budget time, or pay for faster builds.

**While the build runs**, set up the store developer accounts (Phase 2) and stand up the privacy/support pages (Phase 3) in parallel.

View the build when done: Expo account → **Builds** → find the iOS App Store build → click it to see the finished artifact. From there you can click submit to a store, or use the CLI (Phase 4). Note: Expo also offers over-the-air (OTA) updates for shipping JS changes without a new store build.

---

## Phase 2 — Store developer accounts (do during the build)

**Apple Developer ($99/yr):**
- Register at **developer.apple.com/account**. Create a profile, give your info + email, verify email.

**Google Play Console ($25 one-time):**
- Register at **play.google.com/console/signup**.
- **Use a business email, NOT a plain gmail.com.** Set up a Google Workspace account (~$6–7/month) — verification is faster because Google already verified you when you set up Workspace.
- **You must verify access to an actual Android mobile device and test the app on it.** Google won't let you proceed without one.

---

## Phase 3 — Privacy & compliance pages (the most laborious step)

Apple/Google force a web-accessible landing page with a **privacy policy page** and a **compliance/policy page** before you can submit. You also need a working **support page** (the Support URL is REQUIRED at submission). Host these on the same domain as your email if you can.

Claude Code writes AND hosts these. Nick's exact approach — feed it the full requirements as context, then ask:

```
[paste the entire Apple app submission guidelines page as context]

Hey, I'm coming up with an app called Cal Tracker. Can you create a
privacy policy and then host it on my website?
```

For the support / landing page:

```
Hey, make me a web page. Host it on my website.
```

> "I didn't even have to come up with any of the text." — you only feed the requirement; Claude generates and hosts the copy.

Pages this produces:

```
<yourdomain>/privacy    — web-accessible privacy policy (required)
<yourdomain>/support    — web-accessible support page (Support URL is required)
```

(Routes the visual brand/design of these pages to design-studio if they need to match a real brand system — see also.)

---

## Phase 4 — Submit to App Store Connect (eas submit)

From inside the project directory:

```
eas submit --platform ios
```

- Log in if prompted.
- Choose **"select a build from EAS"** and pick the correct **build ID** (multiple IDs = different apps/dates — pick carefully).
- Log into your Apple developer account. If an App Store Connect API key already exists on your computer, it auto-logs you in and connects the key to your App Store.
- App Store Connect submission (managed by Expo) takes **~3–5 minutes**; a link then appears that opens the iOS App Store submission page.

**Gotcha:** if you get an error like "your IDs aren't matched up", ask Claude Code to walk you through fixing it.

---

## Phase 5 — Fill the App Store Connect submission page (top to bottom)

Claude generates the metadata copy and the screenshots. App icon spec and screenshots:

- **App icon:** 1024x1024 PNG referenced by `app.json`'s `icon` field (conventionally `assets/icon.png`); the filename itself is not load-bearing.
- **Screenshots:** required for the **6.5-inch display iPhone** (drag them in) and for **iPad** (iPad auto-generates additional variants). Claude Code now does these automatically — it opens the browser and takes the screenshots.

> "Claude does it all automatically now. It'll actually open up your browser, take screenshots."

Fill these fields (copy-paste the text ones from Claude):

| Field | Value / note |
|---|---|
| Promotional text | copy-pasted from Claude |
| Description | copy-pasted from Claude (e.g. "Track your calories and macros effortlessly with Cal Tracker.") |
| Keywords | — |
| Support URL | **required** — your `/support` page |
| Marketing URL | your website homepage |
| Version | **1.0** (first submission) |
| Copyright | your company / name |
| Build | tie the submission to the specific EAS build you submitted |
| Required sign-in | a working reviewer login (username + password) so a human App Store reviewer can sign in and test functionality — e.g. `e@gmail.com` / `t3stx!.414` |
| Release option | "automatically release this version" |

> "It's a login that an actual human reviewer on the app store end will use to sign into your app and test the functionality."

Then complete the remaining pages:

- **App Information** — app name (e.g. "Cal Tracker by Nick")
- **Age ratings**
- **Content rights**
- **Category**
- **App reviews**
- **App privacy** — add the privacy policy URL. **User privacy choices URL is optional** (Nick recommends skipping it; optional fields are explicitly labeled).
- **Product page preview**
- **Data types**
- **Pricing** — you MUST select a schedule. Free is allowed (Nick set Cal Tracker to free).
- **In-app purchases** — must be clearly declared.
- **Gambling** — confirm the app is not gambling.

(Growth/marketing fields are typically optional and flagged as such.)

Click **"Submit for review"** (top-right). Apple reviews; approval is not guaranteed.

> "There's no way I can guarantee that this app actually makes it onto the app store. All we can do is significantly improve the chances by making sure that we have all the pages and stuff like that."

**Note:** the Apple developer submission and the App Store submission are very similar in shape but lay out the form fields differently — same content, different placement.

---

## Phase 6 — TestFlight (do this BEFORE public launch)

TestFlight is an App Store Connect feature for pre-release distribution. Before rolling the app out publicly, push it to people in your network via a private download link so they can download it "secretly" and surface bugs/jank.

> "It allows you, before you roll out the app, to push this to people you know within your network to give them a link that allows them to download your app sort of secretly."

After launch, use analytics to see how it's going and optimize. Post-launch growth tools on App Store Connect: product page optimization, custom product pages, promo codes, and Game Center.

---

## Phase 7 — Google Play submission

Google Play Console submission mirrors the Apple flow: select your build/track, fill the required metadata (store listing, category, content rating, data safety / privacy policy URL, pricing). The hard prerequisites are the ones in Phase 2:

- $25 one-time developer registration
- business email / Google Workspace account (not plain gmail.com)
- verified access to a real Android device, with the app tested on it

The same privacy-policy and support pages from Phase 3 satisfy Google's requirements.

---

## Build profiles (eas.json)

`eas.json` defines build profiles. The three standard profiles:

- **development** — internal dev client builds (for the on-device dev loop; see expo-go-test).
- **preview** — internal distribution / TestFlight-style pre-release.
- **production** — the store-bound artifact used by `eas submit`.

Claude Code generates these when you feed `eas.json` in during Phase 0; let it pick sane defaults and only adjust the production profile fields it flags.

---

## What this wrench does NOT do

- **Does not run the live app or do the on-device dev loop** — that's `expo-go-test.md` (Expo Go pairing + hot-reload debug).
- **Does not scaffold the project or write the app code** — `expo-scaffold.md` inits the project; the actual feature code is written by Codex via router (AGENTS.md rule #5). Claude steps in only on the documented carve-outs.
- **Does not handle git/commits/tests/PR/CI plumbing** — route that to the `ship` mechanic (`../../ship/SKILL.md`). ship-to-stores is the *store-submission* pipeline, not the source-control/CI pipeline.
- **Does not design the brand/UI of the privacy & support pages** — author copy here, route real brand/design-system work to `design-studio` / `ui-ux-pro-max`.
- **Does not run a security/secret-boundary audit before launch** — that's `mobile-security-audit.md` (and `cso` for deep infra). Run that audit BEFORE this submission, not after.
- **Does not pick the runtime** — if the stack isn't Expo/RN, defer the "which runtime" decision to the `build/mobile` wrench.

---

## See also

- [../SKILL.md](../SKILL.md) — mobile-app mechanic
- [expo-scaffold.md](expo-scaffold.md) — project init + structure (upstream of this wrench)
- [expo-go-test.md](expo-go-test.md) — on-device hot-reload testing (run before building)
- [mobile-security-audit.md](mobile-security-audit.md) — pre-launch security audit (run before submitting)
- [rn-expo-ui.md](rn-expo-ui.md) — UI/UX patterns; routes design to design-studio
- [../../ship/SKILL.md](../../ship/SKILL.md) — git/commit/tests/PR/CI/deploy plumbing
- [../../design-studio/SKILL.md](../../design-studio/SKILL.md) — brand + UI design system for the privacy/support pages
- [../../build/wrenches/mobile.md](../../build/wrenches/mobile.md) — the "which runtime" decision when not Expo/RN
- [../../router/wrenches/codex.md](../../router/wrenches/codex.md) — Codex dispatch for any app-feature code
