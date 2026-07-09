# SKILLS_INDEX — Wiki

One line per skill. Read `AGENTS.md` first for the operating rules.

This is the only skill context loaded at session start. Don't pre-load any mechanic's body — read only the one you'll actually use.

---

## Always-core (loads every session)

| Skill | What |
|---|---|
| **router** | Adaptive dispatcher across Claude / Codex / Gemini / freellm. Detects available lanes, reroutes on loss, enforces no-self-rescue (2 Claude fails → Codex). Wrenches: codex, codex-goal, loop-sense, gemini, freellmapi |
| **second-brain** | Memory engine. Project axis + action/preference axis. Scoped auto-pull on unknown projects. End-of-session extraction ritual on the user's command. Wrenches: capture, recall, learn, end-session |
| **guard** | File-edit safety + destructive-command warnings + public GitHub push gate. Freeze edits to a directory; warn before rm -rf / DROP TABLE / force-push / git reset --hard. Global `pre-push` blocks public pushes/flips unless Codex + gitleaks + denylist pass; private repos are skipped. Wrenches: careful, freeze (incl. `--clear`, formerly `unfreeze`) |

## Apex (on-demand, one prompt → 80-90% done)

| Skill | What |
|---|---|
| **project-orchestrator** | One prompt → interview the user → scope into deliverables → parallel sub-agent execution via router → covers full stack (backend, security, networking, MCP/CLI wiring, correct runtime per target). Hard completion logic: when scope is done, declares the session done, auto-runs summary → handoff file → end-session extraction → emits next-session prompt. Audit-everything mode bundles cso + review + investigate + angry-code-auditor via Codex. Wrenches: intake, scope, dispatch, heartbeat, completion, handoff-emit, audit-everything |

## Mechanics (on-demand)

| Mechanic | What |
|---|---|
| **web-scrape** | Cost-first scraping. Firecrawl (default) → Cloak Browser (bot detection) → local browser drivers (chrome-devtools-mcp / Playwright) last resort. Wrenches: search, scrape, map, crawl, interact, agent, scrapling (free local adaptive tier) |
| **build** | Scaffold sites/apps/backends/mobile with the right runtime per target. Mobile runtime picked per signal — native (Swift/Kotlin) OR RN/Flutter OR Capacitor/PWA/Tauri-mobile (no blanket always-native or always-webview rule). Wrenches: `website` (DRIP framework), `mobile` (per-signal runtime), `backend`, `rag-architect` (RAG design for project data), `onboarding-guard` (redirect-logic pattern checklist) |
| **analytics-sites** | Engine - verify before first use. Reusable business analytics site / client KPI dashboard engine for Codex Sites; first proof is Example Co. Trigger phrases: business analytics site, analytics dashboard for a client. |
| **ship** | Commit → tests → review → PR → merge → deploy → canary → pay-for-this verdict. Wrenches: ship, land-and-deploy, setup-deploy, canary, document-release, python-ci-preflight, review (Codex runs diff-quality), qa (--report-only flag), pay-for-this, benchmark |
| **seo** | One entry, 22 sub-wrenches. `audit` (full sweep) / `page` (single URL) / `plan` (strategy) / `technical` / `content` / `schema` / `sitemap` / `images` / `image-gen` (banana MCP) / `geo` (AI Overviews) / `local` / `maps` / `hreflang` / `google` (API creds) / `backlinks` / `cluster` / `sxo` / `drift` / `ecommerce` / `competitor-pages` / `programmatic` / `dataforseo` (MCP) |
| **design-studio** | Design system → production HTML/PDF. Wrenches: design-consultation (intake), design-html (terminal), design-shotgun (variant explorer), design-review (live visual QA + auto-fix), awesome-design (68 brand DNAs), ui-ux-pro-max (knowledge base), stitch (Google Stitch driver), deck-builder (merged power-design + slide-builder; `--format=html\|marp`), make-pdf (shared with content-forge), plan-design-review (planning lens). 3D/Blender work uses the external Blender + blender-mcp route in second-brain |
| **plan-room** | Brief → plan → review. Flow: process-interviewer (intake) → project-brief-generator (CLAUDE.md emitter) → project-loadout (right-size capabilities) → autoplan (4 review lenses, dispatching the lens wrenches plan-ceo-review / plan-eng-review / plan-devex-review). Plus decision-toolkit (decision coach) and office-hours (idea pressure-test) |
| **content-forge** | Produce / verify / polish content. Wrenches: marketing (ad copy, social, blog, email, repurpose), prompt-master, humanizer (→ `humanizer` mechanic), fact-checker, make-pdf (shared with design-studio). Voice/narration can TRY the external voicebox route after scriptwriting |
| **blog-write** | Write/update the personal-site blog from radar candidates. Four modes: new anchor, update article, anchor reconcile, weekly digest. Detector is `Blog/tools/blog_radar.py`. |
| **humanizer** | Mega humanizer — strips a tiered 47-item AI-tells blocklist and rebuilds prose in a sharp, senior, honest human voice (CRAFT, not detector-evasion). 9-step pass + 21-point pre-ship check + fact-diff. Dispatches to 9 voice-mode wrenches: `build-in-public-engineer` (default), `plainspoken-founder`, `editorial-essayist`, `technical-but-warm`, `wry-minimalist`, `reflective-retrospective`, `dry-technical-authority`, `challenger-contrarian`, `mirror` (voice-match from samples — overrides presets). Built from the top craft repos + empirical studies (2026-06-13) |
| **morning-briefing** | On-demand daily synthesis. Wrenches: briefing-compiler (the main one), video-curator (feeder), retro (weekly engineering retrospective variant) |
| **video-scan** | Transcribe + screenshot a video on demand. yt-dlp + ffmpeg, native YouTube captions, Whisper fallback. Frame analysis routed to Codex (ChatGPT subscription, not Claude tokens). Video generation routes through the external LTX-2 action, not video-scan |
| **skill-forge** | Build / maintain skills + MCPs. Wrenches: aos-add-a-skill (critique gate), skill-creator (scaffold), mcp-builder (FastMCP/TS SDK scaffold), skill-scout (search + conflict detection), mirror-skills-to-codex (junction-based sync). Uses the company-skills marketplace template as a reference for dual Claude/Codex distribution |
| **mobile-app** | End-to-end Claude-Code-driven Expo + React Native app build (the full Nick Saraev mobile course). Wrenches: expo-scaffold (Expo/RN init + build loop), rn-expo-ui (UI/UX + "successful app" framework + MVP scoping), supabase-mobile (DB + RLS + auth via Supabase MCP), edge-fn-claude-ai (Supabase Edge Function → Claude API for in-app AI, keys off the client), expo-go-test (Expo Go QR pairing + on-device hot-reload debug loop), ship-to-stores (EAS Build + TestFlight/App Store $99/yr + Google Play $25), mobile-security-audit (pre-launch 80/20 security-prompt audit). Routes brand/design-system → design-studio (ui-ux-pro-max), git/CI → ship, deep infra security → cso; build/mobile still owns the NON-Expo runtime decision |
| **loop-engineering** | ⛔ RETIRED 2026-06-30 — do NOT route work here (net-negative in practice: 1 trivial fix vs ~26 noise issues in 7 days; pipeline self-starved on needs:human; fake spend ledger). Source kept on disk for salvage (job-card format, labels). See Mechanics/loop-engineering/state.md + harness memory loop-engineering-system. For bounded autonomous work use codex-goal-dispatcher instead |

## Harness-level skills (live at `~/.claude/skills/`, called direct as slash commands)

| Skill | What |
|---|---|
| **codex-goal-dispatcher** | Dispatch long autonomous loops to Codex `/goal` with verification gates + babysit/relay. Mirrored by router's codex-goal wrench |
| **grill-me-codex / grill-with-docs-codex** | Deep one-question-at-a-time interview (Matt Pocock grill-me) → locked PLAN.md → Codex adversarial review loop. Installed 2026-07-08; see [[Reference/grill-codex-adversarial-pipeline]] |
| **codex-review** | Standalone adversarial PLAN review: Codex read-only critic, VERDICT:APPROVED/REVISE, MAX_ROUNDS=5, PLAN-REVIEW-LOG.md artifact |
| **codex-build** | Frozen spec → Codex implements (--yolo), Claude reviews diff + runs proof, MAX_FIX_ROUNDS=2 then Claude takes over, human-gated commit |

## Standalone keepers (no mechanic, called directly)

| Skill | What |
|---|---|
| **investigate** | Root-cause debugging discipline. Iron law: no fixes without root cause. 4 phases: investigate → analyze → hypothesize → implement |
| **cso** | Chief Security Officer mode. Infrastructure-first: secrets archaeology, supply chain, CI/CD, LLM trust boundaries, plus OWASP Top 10 + STRIDE |
| **context-audit** | Harness hygiene. Audit MCP servers / CLAUDE.md / skills / settings for token waste. Returns a health score with specific fixes |
| **windows-launcher** | Windows desktop launchers, port management, hidden CMD windows, shortcut icons. Reusable across projects. Can use `get-windows` as a foreground-window metadata primitive |
| **printing-press-router** | Fires whenever a task touches a third-party service. Enforces CLI > API > MCP tier ladder. Triggers: "build a CLI", "scrape X", "wire up API Y", "I need to talk to <service>" |

---

## What's not here (27 cuts from the old set)

See `_archive/claude_projects_2026-05-pre-rebuild/Rebuild/DECISIONS_LOCKED.md` for the full list with rationale. Highlights:

- **Entire gstack family** (5 skills, ~4000 lines) — replaced by Firecrawl + chrome-devtools-mcp + Playwright
- **All 4 dead firecrawl-build-* wrappers** — vendor onboarding prose, no value beyond the firecrawl-* command skills
- **All 8 aos-* router skills** — mechanics own classification now
- **three-brain-router** — replaced by `router` mechanic
- **skill-stack-audit** — autonomous spam source
- **health** — vanity score, redundant with ship + review
- **devex-review** — no dev-facing projects in the user's portfolio
- **notebook-lm-pipeline** — one-off tutorial
- **karpathy-guidelines** — rules already in `~/.claude/CLAUDE.md` verbatim
- **video-lens** + **video-lens-gallery** — replaced by `video-watch` (video-scan mechanic)
- **All draft auto-stubs** — bleeding from skill-stack-audit
- **benchmark-models, plan-tune, session-takeaway, aos-manage-memory-harness** — see DECISIONS_LOCKED
