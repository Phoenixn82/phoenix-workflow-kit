---
name: mobile-app
description: Build and ship mobile apps end-to-end with the Nick Saraev stack — Expo + React Native frontend, Supabase DB/auth, Supabase Edge Function → Claude API for in-app AI, Expo Go on-device testing, a pre-launch security audit, and EAS Build → TestFlight/App Store + Google Play submission. On-demand mechanic. SUPERSEDES the `build`/`mobile` wrench for the Expo/RN end-to-end path (build/mobile only owns the "which runtime" decision and the non-Expo/RN native cases). Codex is the default code lane — Claude thinks, Codex writes the app code (AGENTS.md rule #5); Claude steps in on documented carve-outs. Fires on "we're building a mobile app", "build a mobile app", "build an Expo app", "ship my app to the App Store", "submit to TestFlight / Google Play", "add AI to my app", "wire Supabase into my app", "test the app on my phone", "run a security audit on my app", or any Expo/React Native build-and-ship intent.
---

# mobile-app — build & ship mobile apps end-to-end (Expo/RN + Supabase + Claude AI)

The on-demand mechanic that owns the full mobile-app pipeline mined from the Nick Saraev course: scaffold an Expo + React Native app, design a successful MVP, wire Supabase (DB / RLS / auth), add in-app AI via a Supabase Edge Function calling the Claude API, test live on a real phone through Expo Go, run a pre-launch security audit, and ship to the App Store and Google Play via EAS. It coordinates seven wrenches and routes the parts other surfaces already own (visual design, deep infra security, git/CI, live DB ops) instead of duplicating them.

This is one mechanic the user can hit at multiple zoom levels:
- **One narrow ask** → fire a single wrench directly. "Wire Supabase into this app" → `supabase-mobile.md`. "Submit to TestFlight" → `ship-to-stores.md`. Don't spin up the whole mechanic.
- **The full pipeline** → fire the whole `mobile-app` mechanic and walk the stages in order (scaffold → UI → Supabase → Edge-Fn AI → device test → security audit → ship).
- **A multi-week full project from one prompt** → step back to `project-orchestrator` (the apex). It calls `mobile-app` as one mechanic among plan-room → mobile-app → design-studio → ship.

When in doubt about the zoom level, ask the user once: *"Single stage, or the whole build-and-ship pipeline?"* Don't grind on it.

---

## Cardinal rules

1. **Codex is the default code lane.** Claude composes the spec, the prompt, and the architecture; the `router` mechanic dispatches Codex to write the actual app code (per AGENTS.md rule #5 and [[Actions/routing-defaults]]). Claude reads the result, verifies it on-device, integrates, and moves on. Claude authors code directly only on documented carve-outs (Codex down / rate-limited, small + well-understood change, explicit "just do it"). The Nick workflow is itself a Claude-Code-in-a-terminal loop — keep it that way; the model writes, the user tests, the model fixes.
2. **This mechanic SUPERSEDES `build`/`mobile` for the Expo/RN end-to-end path.** Once the runtime is "Expo + React Native", `mobile-app` owns scaffold → ship. It routes back to the `build`/`mobile` wrench for exactly one decision: *which runtime* when the project might not be Expo/RN (native Swift/Kotlin, Flutter, Capacitor/PWA). If that decision lands on Expo/RN, control comes straight here.
3. **Security is a stage, not an afterthought.** The `mobile-security-audit` wrench runs the reusable security-audit prompt against Claude Code before any store submission (clearing context between runs, accepting 80/20 risk reduction). Deep infrastructure security routes to `cso` (standalone keeper). The Edge Function is the secret boundary — API keys never live on the client.
4. **Every artifact is self-sufficient.** The finished app runs without an LLM in the loop at runtime: `npx expo start` boots it, all secrets live in env / the Edge Function, and a non-Claude developer can clone and run it tomorrow. No "Claude regenerates this each request" patterns.
5. **Local-dev ports come from the registry.** When the Expo dev server (or any local service) needs a port, read `_system/second-brain/dev-registry/ports.md`, take the next free port, write it back, and bake it into the project so the same app gets the same port every time. Prevents localhost collisions across parallel projects.

---

## The pipeline

The end-to-end stage order. Each stage maps to a wrench; fire them in sequence for a full build, or jump to any single stage for a narrow ask.

1. **Scaffold** — `expo-scaffold.md` — Expo + React Native init from a single Claude Code prompt, file-based routing, project structure, dev environment, and the build-from-nothing-to-running-app loop. Frames the "designing a successful app" + MVP scope before code.
2. **UI / UX** — `rn-expo-ui.md` — React Native + Expo component/navigation/screen patterns, the "what makes a successful app" design heuristics, MVP feature scoping, and the iterate-on-design loop. Routes the brand/design-system layer to `ui-ux-pro-max` / `design-studio`.
3. **Supabase DB + auth** — `supabase-mobile.md` — Supabase client setup, schema/tables, Row Level Security, and mobile auth flows. Uses the Supabase MCP for live ops.
4. **In-app AI** — `edge-fn-claude-ai.md` — the Supabase Edge Function → Claude API pattern (smart coaching, AI reports/insights): function code, server-side Anthropic calls, keys off the client, wiring the app to invoke the function.
5. **On-device test** — `expo-go-test.md` — Expo Go pairing via QR code, on-device hot reload, and the on-phone debug loop (paste runtime logs into Claude Code → fix). Fills the build/mobile gap of "does not run the live app".
6. **Security audit** — `mobile-security-audit.md` — the pre-launch security-prompt audit (run repeatedly, context cleared between runs) plus mobile-specific risks (exposed keys, client trust boundaries, RLS gaps, Edge Function as the secret boundary). Routes deep infra to `cso`.
7. **Ship** — `ship-to-stores.md` — EAS Build (`eas.json`, build profiles), TestFlight + App Store Connect submission, and Google Play Console submission. Fills the build/mobile gap of "does not handle app-store submission". Routes git/CI to `ship`.

The middle stages iterate (UI ⇄ Supabase ⇄ AI ⇄ device test) before the audit-and-ship terminus. Don't treat it as strictly linear — the on-device test loop fires throughout.

---

## Wrenches

| Wrench | Path | What it does |
|---|---|---|
| **expo-scaffold** | `wrenches/expo-scaffold.md` | Expo + React Native project init from a single Claude Code prompt: file-based routing, project structure, dev-environment setup, and the Claude-Code-driven mobile build loop (from nothing to a running app). Includes the "designing a successful app" five-part framework + MVP framing as it scopes the scaffold |
| **rn-expo-ui** | `wrenches/rn-expo-ui.md` | React Native + Expo UI/UX patterns: component patterns, navigation/tabs, screen design, the "what makes a successful app" design heuristics, MVP feature scoping, and the iterate-on-design loop. Routes the visual brand / design-system layer to `ui-ux-pro-max` / `design-studio` |
| **supabase-mobile** | `wrenches/supabase-mobile.md` | Wiring Supabase into an Expo/RN app: client setup, database schema / tables, Row Level Security, and user authentication flows on mobile. Uses the Supabase MCP for live ops |
| **edge-fn-claude-ai** | `wrenches/edge-fn-claude-ai.md` | The Supabase Edge Function → Claude API pattern for in-app AI features (smart coaching, AI reports/insights): the function code, calling the Anthropic API server-side, keeping keys off the client, and wiring the app to call the function |
| **expo-go-test** | `wrenches/expo-go-test.md` | Expo Go device pairing + on-device hot-reload testing + the on-phone debug loop (paste runtime logs into Claude Code → fix). Fills the build/mobile gap of "does not run the live app" |
| **ship-to-stores** | `wrenches/ship-to-stores.md` | The release pipeline: EAS Build (`eas.json`, build profiles — dev / preview / production), TestFlight + App Store Connect submission ($99/yr Apple Developer account, required metadata + assets, review), and Google Play Console submission ($25 one-time, tracks, required metadata). Fills the build/mobile gap of "does not handle app-store submission". Routes git/CI to `ship` |
| **mobile-security-audit** | `wrenches/mobile-security-audit.md` | The pre-launch security-prompt audit pattern from the video + mobile-specific risks (exposed API keys, client trust boundaries, RLS gaps, Edge Function as the secret boundary). Describes the audit prompt's required shape (the five named vulnerability patterns + tier-list output) and where the original "vibe coding security" prompt lives; embeds the verbatim fix-loop follow-up prompts. Routes deep infra security to `cso` |

---

## Cross-mechanic routing

`mobile-app` ROUTES to (does NOT duplicate) these existing surfaces:

| Routes to | When |
|---|---|
| `ui-ux-pro-max` / `design-studio` | Visual brand + UI design system. `rn-expo-ui` owns RN component/navigation mechanics; the look-and-feel layer (palette, fonts, icon set, brand identity) hands off here |
| `cso` (standalone keeper) | Deep infrastructure security audit. `mobile-security-audit` runs the 80/20 vibe-coding security prompt; anything deeper (threat modeling, infra hardening, supply chain) routes to `cso` |
| Supabase MCP | Live DB/auth ops: `apply_migration`, `execute_sql`, `deploy_edge_function`, `get_advisors`. `supabase-mobile` and `edge-fn-claude-ai` call the MCP for real schema, RLS, and function deploys instead of hand-waving them |
| `ship` (mechanic) | Git / commit / tests / PR / CI / deploy plumbing. `ship-to-stores` owns the EAS + store-submission specifics; the version-control and CI wiring around it routes to `ship` |
| `windows-launcher` (keeper) | A clickable desktop launcher for the Expo dev server, so the user double-clicks to start `npx expo start` instead of typing it |
| `build`/`mobile` wrench | The "which runtime" decision when the project might not be Expo/RN (native Swift/Kotlin, Flutter, Capacitor/PWA). If that decision lands on Expo/RN, control returns here |
| `router` → Codex | The ACTUAL app code. Claude thinks, Codex does (AGENTS.md rule #5). Every code artifact in every stage is written by Codex via `router` unless a documented carve-out applies |
| `second-brain` | Capture project decisions (stack picks, schema choices, MVP scope) as they happen; `dev-registry/ports.md` for the local Expo dev-server port |

---

## When mobile-app does NOT fire

- **A single-file edit** to an existing Expo project → that's just an edit (router dispatches Codex). This mechanic is for the pipeline or a whole stage, not one-line tweaks.
- **A bug fix** on existing app code → `investigate` (standalone keeper) for root cause first, then router dispatches Codex for the fix. Don't fire the whole mechanic to chase one crash.
- **A full multi-week project** spanning more than the mobile-app pipeline → `project-orchestrator` (the apex), which calls `mobile-app` as one mechanic among several.
- **A non-Expo/RN runtime question** ("should this be native Swift?" / "Flutter or React Native?" / "can I just ship the website as a webview?") → `build`/`mobile` wrench owns the runtime decision. It returns here only if the answer is Expo/RN.

---

## See also

- [wrenches/expo-scaffold.md](wrenches/expo-scaffold.md) — Expo + RN scaffold + designing-a-successful-app framework
- [wrenches/rn-expo-ui.md](wrenches/rn-expo-ui.md) — RN/Expo UI/UX patterns + MVP scoping + iterate-on-design loop
- [wrenches/supabase-mobile.md](wrenches/supabase-mobile.md) — Supabase client + schema + RLS + mobile auth
- [wrenches/edge-fn-claude-ai.md](wrenches/edge-fn-claude-ai.md) — Edge Function → Claude API in-app AI
- [wrenches/expo-go-test.md](wrenches/expo-go-test.md) — Expo Go device pairing + on-phone debug loop
- [wrenches/ship-to-stores.md](wrenches/ship-to-stores.md) — EAS Build + TestFlight/App Store + Google Play
- [wrenches/mobile-security-audit.md](wrenches/mobile-security-audit.md) — pre-launch security-audit prompt + mobile risks
- [`build/SKILL.md`](../build/SKILL.md) — owns the "which runtime" decision; hands off here for Expo/RN
- [`ship/SKILL.md`](../ship/SKILL.md) — git / commit / tests / PR / CI plumbing around the store release
- [`design-studio/SKILL.md`](../design-studio/SKILL.md) — visual brand + UI design system
- [`cso/SKILL.md`](../../skills/cso/SKILL.md) — deep infrastructure security audit
- [`router/SKILL.md`](../router/SKILL.md) — dispatches Codex for the actual app code (Claude thinks, Codex does)
