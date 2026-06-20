---
name: build
description: "Scaffold sites / apps / backends / mobile / MCPs with the right runtime per target. On-demand mechanic. Detects target type from the user's prompt, dispatches to the right wrench, coordinates with `router` (default routing: Codex does the implementation per [[Actions/routing-defaults]]; Claude steps in on carve-outs), `cso` (security inline for backends), `design-studio` (for visuals), and `ship` (deploy handoff). Mobile runtime picked per signal — native (Swift/Kotlin) OR RN/Flutter OR Capacitor/PWA/Tauri-mobile. Backend = cso runs inline, not after. Fires on \"build a website\", \"build me X\", \"scaffold a backend\", \"build a mobile app\", \"add an auth flow\", \"design a RAG system\", \"make a CLI tool\", \"build an MCP\", or any \"build / scaffold / create / make me\" intent that names a project surface."
---

# build — scaffold sites, apps, backends, mobile, MCPs

The on-demand mechanic that scaffolds project surfaces with the right runtime and architecture per target. Coordinates the build phase end-to-end. Hands off to `ship` when the project is ready to deploy.

This is one mechanic the user can hit at multiple zoom levels:
- "scaffold the backend" → fires the `backend` wrench directly
- "build me a SaaS from scratch" → typically routed via `project-orchestrator` first (the apex coordinates plan-room → build → design-studio → ship); build is one mechanic the orchestrator calls
- "add the onboarding redirect" → fires the `onboarding-guard` wrench directly

When in doubt about the zoom level, ask the user once: *"Tactical build task or full-project scaffold?"* Don't grind on it.

---

## Cardinal rules

1. **Codex is the default code lane.** Build composes the spec; the `router` mechanic dispatches Codex (single-file) or Gemini-spec-then-Codex (multi-file). Claude reads the result, verifies it, integrates via Write/Edit, moves on. **Claude can author code when Codex is unavailable, rate-limited, or the work is small / well-understood** — see AGENTS.md hard rule #5 for the full policy. The point is to use the cheapest lane that does the work right, not to forbid Claude from coding.
2. **Pick the right mobile runtime per project.** Native (Swift/Kotlin) when deep OS integration, native UX feel, performance, or app-store discoverability matters. React Native or Flutter when cross-platform with near-native UX is the right balance. Capacitor / PWA / webview-shell when the app really is the website + thin native layer, or the team is web-only and speed-to-market dominates. Don't default to native because "real apps are native"; don't default to webview because "it's easier". The `mobile` wrench's decision tree picks per signal.
3. **Backend means security inline.** `cso` runs during build (auth review, secrets handling, input validation, dependency supply chain), not after. Bolted-on security is broken security.
4. **MCP work routes through skill-forge.** Don't duplicate `mcp-builder` here. The build mechanic detects "MCP server" intent and hands off to `skill-forge → mcp-builder`. If the MCP wraps a third-party service, `printing-press-router` fires first to enforce CLI > API > MCP tier ladder.
5. **Every build wrench produces self-sufficient artifacts.** The finished output runs without an LLM in the loop at runtime. No "and then Claude regenerates this on every request" patterns.
6. **Local-dev port assignment uses the port registry.** When scaffolding a project that runs locally, read `_system/second-brain/dev-registry/ports.md` to find the next free port. Assign it, write it back to the registry, and bake it into the project's config so the same project gets the same port every time. Prevents localhost collisions when the user runs multiple projects in parallel. See `second-brain/SKILL.md` § Dev registry for the format.

7. **Build to the Reliability Standard from day one (AGENTS.md hard rule #12).** Continuity is decided at scaffold, not bolted on. Read `RELIABILITY_STANDARD.md` (root of AI_Projects) and bake in Pillar A — **environmental continuity** — before writing features: carry the runtime (freeze/bundle the interpreter + deps, e.g. PyInstaller + committed venv like reference-app; never call system Python/global packages); pin and freeze deps (a snapshot, never floating); depend on nothing the OS can swap (avoid GPU/driver/global-tool requirements on the launch path — that's what rotted Agentic OS); local-first (bind 127.0.0.1, no network needed to open); one self-contained folder with the shortcut pointing *into* it (no separate install copy to desync). Desktop/launcher work hands off to `windows-launcher` for Pillar B. The decision to bundle the runtime is made HERE, on day one — it can't be retrofitted cheaply.

---

## Target classification (intake)

When the user invokes build without specifying a target, classify from the prompt. Use this table:

| Signal | Target |
|---|---|
| "website" / "landing page" / "site" / "frontend" / "the UI" / "make a page" | **website** wrench (DRIP framework) |
| "mobile app" / "iOS app" / "Android app" / "native app" / "phone app" | **mobile** wrench (runtime per signal: native / RN/Flutter / Capacitor/PWA) |
| "backend" / "API" / "server" / "database" / "service" / "endpoint" | **backend** wrench (with cso inline) |
| "MCP" / "MCP server" / "tool for Claude" / "Model Context Protocol" | hands off to **`skill-forge → mcp-builder`** wrench |
| "CLI" / "command-line tool" / "wrapper for <service>" | first to **`printing-press-router`** (CLI > API > MCP enforcement); standalone keeper, not a build wrench |
| "auth flow" / "onboarding" / "redirect logic" / "sign in / sign up flow" | **onboarding-guard** wrench (the 5-condition checklist before redirect logic) |
| "RAG" / "vector search" / "chat with my docs" / "knowledge base for an LLM" | **rag-architect** wrench (RAG architecture design) |
| "desktop app" / "Windows launcher" / ".bat" / "desktop icon" | hands off to **`windows-launcher`** (standalone keeper) |
| "Vercel project" / "Next.js" / "shadcn" / "next-forge" | hands off to the **`vercel:*`** plugin family (external — `vercel:bootstrap`, `vercel:nextjs`, `vercel:shadcn`, `vercel:next-forge`, `vercel:auth`, etc. depending on specifics) |
| Full project, multi-phase, "build me a SaaS / app / startup" | step back: this is likely `project-orchestrator` territory — confirm with the user |

If the signal is ambiguous, default to the **website** wrench — it has its own Phase 0 intake that asks the right questions.

---

## Cross-mechanic dependencies

Build coordinates with several other mechanics in the system. Knowing when to hand off is half the job:

| Phase | Other mechanic | When |
|---|---|---|
| Code writing | `router` → Codex | Every code artifact. Default: Codex authors per [[Actions/routing-defaults]]; Claude can step in on documented carve-outs (Codex down, small + well-understood, "just do it"). Multi-file → Gemini reads + outputs spec, Codex writes per-file. |
| Architecture review | `plan-room` → eng-lens / CEO-lens | Before scaffolding starts, when scope is non-trivial. Especially for backends. |
| Security review (inline) | `cso` | During backend build, not after. Triggers on any backend wrench. |
| Visual design | `design-studio` | For website / mobile builds when design isn't already locked. Builds a brand, then the build wrench produces HTML/components against the design. |
| Test + ship | `ship` | At the end of any build wrench, hand off to ship for commit → tests → PR → deploy → canary → pay-for-this verdict. |
| Memory / decisions | `second-brain` | Build wrenches `capture` decisions as they happen (project structure choices, library picks, etc.). End-session ritual writes them canonically. |
| Bug bash after build | `router` → `codex-goal` | When the build is functionally done but needs iterative testing-and-fixing. Use `codex-goal-dispatcher` with the `comprehensive_user_testing` template. |
| Scraping during build | `web-scrape` | When the build needs external data (competitor research, sample data, etc.). Firecrawl-first per the cost ladder. |

---

## Wrenches

| Wrench | Path | What it does |
|---|---|---|
| **website** | `wrenches/website.md` | DRIP framework (Design → Refine → Integrate → Publish). Stitch + awesome-design references + 21st.dev/CodePen component sourcing + production HTML variants. Phase 0 intake auto-fires when target is ambiguous |
| **mobile** | `wrenches/mobile.md` | Mobile builds, runtime picked per signal. Native iOS = Swift / SwiftUI. Native Android = Kotlin / Jetpack. Cross-platform = React Native or Flutter. Webview shell (Capacitor / PWA / Tauri-mobile) when the app really is web + thin native layer |
| **backend** | `wrenches/backend.md` | Backend scaffold with `cso` running inline. Stack detection, auth handling, secrets policy, DB choice, MCP wiring via printing-press-router for any external service |
| **onboarding-guard** | `wrenches/onboarding-guard.md` | The 5-condition checklist the user built after Example App's 3-fix-in-17-min incident. Fires before any conditional-redirect logic is written |
| **rag-architect** | `wrenches/rag-architect.md` | RAG architecture design. 4 RAG types (Naive / Advanced / Modular / Graph), implementation plan, starter scaffold. For project data (NOT for the user's personal vault — that's `second-brain`) |

---

## Self-sufficient artifacts (the runtime test)

Every build wrench must produce code that runs without an LLM in the loop at runtime. Run this test on the final output:

- ☐ Does it boot with `npm start` / `cargo run` / `flutter run` / `swift run` / `python main.py` and nothing else?
- ☐ Are all the inputs it needs in environment variables or config files, not "ask Claude at runtime"?
- ☐ Can a non-Claude developer pick this up and run it tomorrow without any context from this session?
- ☐ Are the dependencies pinned and the install path documented?
- ☐ Does the README cover setup, environment, and one example invocation?

**Continuity test (per `RELIABILITY_STANDARD.md` — would it still open after a week / a Windows update / a cold reboot?):**

- ☐ Does it carry its own runtime (bundled/frozen interpreter + committed deps), or does it borrow from the system's ever-drifting state?
- ☐ Does it depend on anything the OS can change underneath it (GPU/driver, a global tool on PATH, a system service)? If yes, is that dependency off the launch path or self-healed/degraded?
- ☐ Does it open with the network off (local-first, no cloud call on startup)?
- ☐ Is the launcher idempotent (safe to double-click repeatedly) and readiness-gated (waits for the server before showing the window)?
- ☐ Does every launch leave a log trail, and does a failed launch print the exact log path?
- ☐ Is it one self-contained folder, with the desktop shortcut pointing into it (no separate install copy to desync)?

If any answer is "no", the build isn't done. Iterate before handing off to `ship`. Launcher items hand off to `windows-launcher`.

---

## Handoff to ship

When the build wrench's output passes the self-sufficient test, hand off to the `ship` mechanic:

```
build [wrench] complete.
Project at: <path>
Self-sufficient runtime: confirmed
Files touched: <list>
Tests scaffolded: <yes / no>
Cso review: <passed / pending — backend only>

Ready for ship?
```

The user's yes hands off to `ship`. Until then, the build remains in the build mechanic's scope.

---

## When build does NOT fire

- **Single-file edits** to an existing project → that's just an edit (router dispatches Codex). Build is for scaffolding new surfaces or major sub-systems.
- **Bug fixes** on existing code → `investigate` (standalone keeper) for root-cause, then router dispatches Codex for the fix.
- **Design polish on a live site** → `design-studio` (not build). Build's design phase is for new surfaces.
- **Deploy / CI / merge** → `ship` (build's terminus, but ship is its own mechanic).
- **Personal-vault RAG** → `second-brain` (build's `rag-architect` is for project-data RAG, not the user's own vault).
- **"Fix the redirect bug"** → `investigate` first (root-cause), then maybe `onboarding-guard` wrench. Not a full build invocation.

---

## See also

- [wrenches/website.md](wrenches/website.md) — DRIP framework
- [wrenches/mobile.md](wrenches/mobile.md) — mobile (runtime per signal: native / RN/Flutter / Capacitor/PWA)
- [wrenches/backend.md](wrenches/backend.md) — backend with cso inline
- [wrenches/onboarding-guard.md](wrenches/onboarding-guard.md) — 5-condition redirect checklist
- [wrenches/rag-architect.md](wrenches/rag-architect.md) — RAG architecture design
- [`router/SKILL.md`](../router/SKILL.md) — dispatches Codex for actual code writing
- [`cso/SKILL.md`](../../skills/cso/SKILL.md) — security review (called inline by `backend` wrench)
- [`ship/SKILL.md`](../ship/SKILL.md) — terminus mechanic for every build
- [`project-orchestrator/SKILL.md`](../project-orchestrator/SKILL.md) — apex; calls build as one of several mechanics for full-project execution
- [`printing-press-router/SKILL.md`](../../skills/printing-press-router/SKILL.md) — standalone keeper; fires before any external-service integration
- [`windows-launcher/SKILL.md`](../../skills/windows-launcher/SKILL.md) — standalone keeper; build hands off here for Windows desktop entries
