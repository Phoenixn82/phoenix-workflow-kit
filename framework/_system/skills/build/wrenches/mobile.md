---
name: mobile
description: "Wrench inside the `build` mechanic. Builds mobile apps — picks the right runtime per project signals: iOS native (Swift / SwiftUI), Android native (Kotlin / Jetpack Compose), cross-platform with near-native UX (React Native or Flutter), or webview-based shells (Capacitor, PWA, Tauri-mobile) when the app really is web + thin native layer, or when speed-to-market and web-team constraints make sense. Decision tree picks per signal — no blanket \"always native\" or \"always webview\" rule. Codex is the default code lane (per AGENTS.md hard rule #5); Claude can author when Codex is unavailable. Fires on \"build a mobile app\", \"iOS app\", \"Android app\", \"native app\", \"phone app\", \"make me an app for iPhone / Android\"."
---

# mobile — mobile app builder (runtime picked per project)

The mobile pathway for the build mechanic. Picks the right runtime for the actual project — native, cross-platform, or webview-shell — based on the project's real signals.

**Cardinal: pick per signal, don't default.** Native (Swift/Kotlin) is right when deep OS APIs, native UX feel, performance, or app-store discoverability matter. Cross-platform (React Native, Flutter) is the middle ground for native-grade UX across both platforms with one codebase. Capacitor / PWA / Tauri-mobile (webview shells) are valid when the app really is the website + thin native (push, biometrics, deep links), the team is web-only, or speed-to-market dominates and native UX is good-enough. Don't default to native because "real apps are native". Don't default to webview because "it's easier". Pick per signal.

**Cardinal: Codex is the default code lane.** Specs go through router → Codex per AGENTS.md hard rule #5. Claude can author code when Codex is rate-limited, down, or for small / well-understood patterns. Mobile-heavy projects often have multi-file scope → Gemini reads + outputs spec, Codex writes per-file.

---

## Runtime selection

The first real decision. Use this tree:

```
Single target platform (iOS only OR Android only)?
  → Native (Swift for iOS, Kotlin for Android)
  → Best DX, best performance, best OS integration, app-store-blessed

Both platforms, deep native features needed (camera ML, AR, complex gestures)?
  → Native (separate iOS + Android codebases)
  → Cross-platform tools cripple on edge-case native APIs

Both platforms, mostly business logic + standard UI?
  → React Native OR Flutter
  → Pick React Native if the team / the user knows JS / TS
  → Pick Flutter if the user prefers strong typing + a single language (Dart)

Both platforms, prototype only, throwaway?
  → React Native (faster to bootstrap with Expo)
  → Or: PWA if "appiness" matters more than store distribution

The app is basically the website + thin native (push, biometrics, deep links, deep-linked notifications)?
  → Capacitor (Ionic) — wraps a webview but supports native plugins, ships to App Store + Play
  → OR PWA — installs from the browser, no store review process, no app distribution overhead
  → Pick Capacitor when store presence matters; pick PWA when it doesn't
  → Don't pick this tier when native UX / native performance / deep OS integration is the real requirement

Team is web-only, deadline is real, and "good enough" UX is fine?
  → Capacitor or PWA, same calculus as above
  → Don't force native on a web team for an MVP — ship and iterate
```

Ask the user once if the answer isn't clear from the brief. Use AskUserQuestion with the relevant real options for the project — including webview shells when they're a legitimate fit.

---

## Stack defaults per runtime

### iOS native

- **Language:** Swift (Swift 6 if Xcode supports; Swift 5.9 otherwise)
- **UI:** SwiftUI (iOS 15+) preferred; UIKit only if targeting older versions
- **State:** SwiftUI's `@State` / `@Observable`; for complex apps, The Composable Architecture (TCA) or Redux-like patterns
- **Storage:** SwiftData (iOS 17+) preferred; Core Data otherwise; UserDefaults for trivial prefs
- **Networking:** URLSession + async/await; Alamofire only if existing project uses it
- **Build:** Xcode + xcodebuild for CI

### Android native

- **Language:** Kotlin (never Java for new projects)
- **UI:** Jetpack Compose preferred; XML layouts only if existing project uses them
- **State:** Compose's `mutableStateOf` + ViewModel + StateFlow
- **Storage:** Room for relational; DataStore for key-value; Preferences only for trivial
- **Networking:** Retrofit + OkHttp + Kotlinx Serialization
- **Build:** Gradle + KSP for annotation processing

### React Native (cross-platform)

- **Bootstrap:** Expo (managed workflow) unless deep native module work is needed
- **Language:** TypeScript (always — no JS for new RN projects)
- **State:** Zustand for app state, React Query for server state
- **Navigation:** React Navigation 7+
- **Storage:** Expo SecureStore (sensitive), AsyncStorage (non-sensitive), SQLite or WatermelonDB (structured)
- **Build:** EAS Build for app-store distribution

### Flutter (cross-platform)

- **Language:** Dart (Dart 3+ for null safety + records)
- **State:** Riverpod or Bloc — pick one per project, don't mix
- **Navigation:** GoRouter
- **Storage:** Drift (relational) or Hive (key-value)
- **Build:** flutter build ios / flutter build apk

---

## Phase flow

### Phase 0 — Intake

Get the brief tight before any code dispatch:
- **Platforms:** iOS / Android / both
- **The one job:** what does the app actually do (one sentence)
- **Native APIs needed:** camera, GPS, push notifications, biometric auth, ARKit/ARCore, Bluetooth, HealthKit, etc.
- **Offline behaviour:** fully offline / online-required / sync-when-available
- **Auth + accounts:** anonymous / email-password / OAuth / Apple Sign In / Google Sign In
- **Backend dependency:** existing API / building one alongside / serverless / no backend

If a backend needs building alongside, the build mechanic also fires the `backend` wrench. Two builds in parallel, coordinated.

### Phase 1 — Architecture spec

Compose the high-level architecture as PROSE (the user reviews before code starts):
- Runtime + language (per Phase 0)
- App structure (tabs / stack / drawer)
- Screen list (one screen per "view" the user reaches)
- Data layer (storage choice + sync strategy)
- Auth flow (with `onboarding-guard` wrench applied if any conditional redirects)
- Native integrations (push, camera, etc.)
- Test strategy (UI tests + unit tests, framework per runtime)

### Phase 2 — Scoping (multi-file via Gemini)

For non-trivial apps (> 5 screens or > 20 components), route the scoping through Gemini first. Gemini reads the architecture spec + any reference codebases and outputs:
- File-by-file structure (paths + purpose)
- Dependency order (what gets written first)
- Shared types and interfaces
- Per-file change spec as PROSE (Gemini does NOT write code per router's rule)

Then Codex writes per-file in the dependency order.

### Phase 3 — Implementation (Codex)

Dispatch Codex per-file. Each spec includes:
- File path
- Runtime + language
- Imports + types
- The functional contract (what this file exposes, how it's used)
- Output contract (idiomatic for the runtime, follows the stack defaults above, includes inline tests where the runtime convention supports it)

For React Native + Flutter, use `codex-goal-dispatcher` if the build is large (many similar screens, batch component generation) — `/goal` loops handle the repetitive work without burning Claude tokens.

### Phase 4 — Native build + test

After Codex writes the files:
- **iOS:** `xcodebuild build` + `xcodebuild test` against simulator — requires macOS hardware or a cloud build service (EAS / Xcode Cloud); not runnable locally on this Windows machine
- **Android:** `./gradlew build` + `./gradlew test` + emulator UI test
- **React Native:** `eas build --platform <target>` (Expo) or native build pipelines
- **Flutter:** `flutter build <platform>` + `flutter test`

Build failures → diagnose (often a missing import, version mismatch, or simulator config) → dispatch Codex to fix. Don't have Claude pattern-match build errors when Codex can do it.

### Phase 5 — Hand off to ship

When the app builds clean and the simulator launches the happy path:

```
mobile build complete.
Runtime: <iOS native | Android native | React Native | Flutter>
Project at: <path>
Builds: confirmed
Simulator happy path: passed

Ready for ship? (ship will run tests + version bump + app-store-prep tasks)
```

For app-store distribution, ship coordinates with `setup-deploy` to configure App Store Connect + Play Console artifacts. This is a one-time setup per app — once configured, future ships use the saved config.

---

## When to escalate

- **Backend needed alongside** → fire `backend` wrench in parallel
- **Visual design from scratch** → fire `design-studio` first to establish the design system
- **Full project orchestration needed** (multi-week, multi-platform, with backend + ship + monitoring) → `project-orchestrator` calls mobile as one of many mechanics

---

## What this wrench does NOT do

- **Does not default to webview shells.** Runtime picked per signal (native Swift/Kotlin vs RN/Flutter vs Capacitor/PWA/Tauri-mobile). PWA via the `website` wrench if "appy website" is the real need.
- **Does not write code by default.** Codex via router does (per [[Actions/routing-defaults]]). Claude steps in only on the documented carve-outs.
- **Does not handle app-store submission directly.** `ship` + `setup-deploy` coordinate that.
- **Does not run the live app.** `chrome-devtools-mcp` doesn't apply to native apps — use the actual simulator / device for QA.

---

## See also

- [../SKILL.md](../SKILL.md) — build mechanic
- [onboarding-guard.md](onboarding-guard.md) — fires before any auth redirect in the app
- [backend.md](backend.md) — when a backend needs building alongside
- [../../design-studio/SKILL.md](../../design-studio/SKILL.md) — when design needs deep exploration first
- [../../router/wrenches/codex.md](../../router/wrenches/codex.md) — Codex dispatch for code writing
- [../../router/wrenches/codex-goal.md](../../router/wrenches/codex-goal.md) — for batch-generation work (many similar screens)
- [../../ship/SKILL.md](../../ship/SKILL.md) — terminus, app-store distribution
