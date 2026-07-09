# DECISION_MAP — Task → Tool routing

The right tool deliberately chosen, not a reflex. When unclear, run `skill-scout`.

---

## The base cases

| Task | First tool | Lane | Why |
|---|---|---|---|
| **Sharpen a prompt** | `prompt-master` (wrench inside content-forge, called direct) | Claude | One wrench. Don't spin up content-forge for a prompt rewrite |
| **Build an MCP from scratch** | `skill-forge` → `mcp-builder` (wrench, called direct) | Claude designs surface, Codex writes scaffold | Wrench, not the whole skill-forge mechanic |
| **Build an MCP that wraps a 3rd-party service** | `printing-press-router` FIRST → may end up calling `mcp-builder` if no CLI option exists | Claude routes, Codex writes | CLI > API > MCP ladder. Don't reach for MCP if a CLI exists |
| **Build a CLI to a service with no API** | `printing-press-router` (standalone, top-level) | Codex executes, Claude designs command surface | Honors CLI > API > MCP ladder |
| **Scrape a site (default)** | `web-scrape` → `scrape`/`search` (Tier 1 = Firecrawl) | Firecrawl service | Cost-first |
| **Scrape a site with bot detection** | `web-scrape` → fallback to **Cloak Browser** | Cloak service | Defeats bot detection without local token cost |
| **Scrape locally/free/high-volume or with fragile selectors** | `web-scrape` → `scrapling` | Local Python; Codex writes any integration code | Use for zero-spend recurring targets, selector drift, or local Turnstile attempts. Firecrawl is still the default for ordinary extraction |
| **Scrape when both above fail** | `web-scrape` → chrome-devtools-mcp or Playwright | Local browser | Last resort. Local drivers are expensive per page (every action is a model call) |
| **Build a website** | `project-orchestrator` → plan-room → build + design-studio | Claude plans, Codex implements, Gemini for research | Full-stack scope = orchestrator |
| **Build a business analytics site / analytics dashboard for a client** | nalytics-sites engine (verify before first use) | Codex implements, Claude reviews source policy | Reuse the Sites dashboard engine; preserve free-only connector policy and save/review before production deploy. |
| **"We're building a mobile app" (Expo + React Native, end-to-end)** | `mobile-app` mechanic → dispatches expo-scaffold → rn-expo-ui → supabase-mobile → edge-fn-claude-ai → expo-go-test → ship-to-stores → mobile-security-audit | Claude plans/designs, Codex implements | Owns the full Claude-Code-driven Expo/RN path: scaffold → MVP design → Supabase (DB/RLS/auth) → Claude AI via Edge Functions → on-phone test → EAS store submission → security audit. Routes brand → design-studio, git/CI → ship, deep security → cso |
| **Build a mobile app (full multi-week project)** | `project-orchestrator` → interview → scope → may call `mobile-app` (Expo/RN) or `build` (other runtime) | Claude plans, Codex implements | Full-stack scope = orchestrator; it picks the mechanic per target |
| **Which mobile runtime? (NOT Expo/RN)** | `build` → `mobile` wrench (native Swift/Kotlin, Flutter, Capacitor — NOT webview shell) | Claude decides, Codex implements | build/mobile owns the runtime decision when Expo + React Native isn't the chosen stack |
| **Build a backend** | `project-orchestrator` → build + cso inline + ship | Claude architects, Codex writes, Gemini reads specs | cso runs inline during build, not after |
| **UI / bug testing on an app** | `chrome-devtools-mcp` for live driving + `codex-goal-dispatcher` for the iteration loop | Codex (goal loop) | Bulk iterative bug-bash is exactly what codex-goal-dispatcher exists for |
| **Major audit of a project** | `project-orchestrator` audit-everything mode → cso + review + investigate + angry-code-auditor (parallel, via Codex) | Codex runs the angry sweep, Claude synthesizes | All critical-bug-finding lenses paired. Codex does the heavy auditing so Claude tokens stay free |
| **Autonomous backlog / agent loops (triage tickets, issue→PR)** | ~~`loop-engineering` mechanic~~ ⛔ RETIRED 2026-06-30 → use `codex-goal-dispatcher` (bounded goals with verification gates) or a Claude Workflow loop instead | Codex `/goal` or Claude Workflow | loop-engineering proved net-negative (noise tickets, self-starving pipeline, fake spend ledger); see Mechanics/loop-engineering/state.md |
| **Research / first-pass intake** | `router` → Gemini lane (long context + grounded search) → `second-brain` saves findings | Gemini | Heavy reading is cheap; doesn't burn Claude tokens |
| **Bulk menial work cheaply** | `router` → freellm lane with task preset (`cheap`, `code`, `fast`, etc.) | freellm | Lowest cost lane that meets the bar |
| **Task smells repetitive / batch-shaped / run-until-criterion** | `router` → `loop-sense` | Claude proposes; the user approves before any loop starts | Detects loop-shaped work and drafts a budget-declared runbook instead of grinding |
| **"Should I" / stuck on a decision** | `plan-room` → `decision-toolkit` wrench | Claude | Reversibility triage (Bezos 1/2 door) + right framework + kill criteria + review date |
| **New project brain-dump** | `plan-room` → process-interviewer → project-brief-generator → project-loadout → autoplan (4 review lenses) | Claude with Gemini for research | Full intake before any code touches disk |
| **Turn AI text into human-sounding text / de-slop / "sound less AI" / "match my voice"** | `humanizer` mechanic → pick a voice wrench (default `build-in-public-engineer`; `mirror` when the writer supplied samples) | Claude | Mega humanizer: 47 tiered AI-tells, 9-step pass, 21-point check, 9 voice modes. Craft, not detector-evasion. content-forge's old humanizer wrench now redirects here |
| **Verify factual claims in text** | `content-forge` → `fact-checker` | Claude | One wrench |
| **"Time to blog?" / "what should I blog" / weekly digest / project update post** | Run `python Blog/tools/blog_radar.py report`, then fire `blog-write` | Claude plans, Codex writes | Detector selects the lane; writer produces the right blog surface and calls `blog_radar.py mark` |
| **Design RAG for a project's data** | `build` → `rag-architect` wrench | Claude designs, Codex implements | Architecture decision for a project. NOT personal-memory infrastructure (that's `second-brain`) |
| **Save context for next session** | `second-brain` end-of-session ritual (the user triggers) | Claude | Auto-extracts decisions, errors+fixes, defaults, status, open loops, corrections; shows draft; writes only what the user approves |
| **Transcribe + screenshot a video** | `video-scan` (video-watch entry) | Codex (frame analysis routes there) | yt-dlp + ffmpeg + native captions; frame analysis on Codex subscription, not Claude tokens |
| **Daily morning briefing** | `morning-briefing` → briefing-compiler (on the user's command, NOT scheduled) | Claude | No autonomous schedule. The user runs it when he wants the synthesis |
| **Weekly engineering retro** | `morning-briefing` → retro (weekly variant of briefing-compiler) | Claude | Same scheduling lane as morning briefing; on-demand |
| **SEO work of any kind** | `seo` mechanic, which dispatches to the right wrench based on intent | Claude with Gemini for research-heavy SERP analysis | One entry, ~22 wrenches; mechanic detects business type + dispatches |
| **Design a brand/look from scratch** | `design-studio` → design-consultation → design-shotgun → design-html | Claude with Gemini for brand research | Full DRIP pipeline through the mechanic |
| **Build a slide deck** | `design-studio` → deck-builder (`--format=html` for brand decks, `--format=marp` for Marp Markdown) | Claude | Merged from power-design + slide-builder; choose output format |
| **Build or control a Blender / 3D asset workflow** | `design-studio` or `build` + [[Reference/blender-mcp-setup]] | Claude designs, Blender/Codex executes | Local Blender 5.1 + `blender-mcp` exists; requires the Blender GUI socket on `localhost:9876` |
| **Export a doc to publication-quality PDF** | `make-pdf` (shared between design-studio and content-forge) | Claude | Cross-mechanic wrench |
| **Generate AI video with LTX-2** | `ltx2` command via [[Actions/ltx2-video-generation]] | Local or remote GPU path | External tool route, not a mechanic. Do not download weights or run generation unless the user asks |
| **Create local narration / voiceover audio** | `content-forge` writes the script → TRY `voicebox` | Claude writes, local tool renders | Repo-backed helper only; use when the user explicitly asks for audio or narration |
| **Job/resume fit-scoring reference work** | `example_app` project notes → TRY JustHireMe / hiring-agent | Codex if integrating | Reference/eval lane only. Do not replace production ranking/scraping without a spec |
| **Find or recommend a skill for a task** | `skill-scout` (inside skill-forge) | Claude | TF-IDF rank over installed skills; flags conflicts; falls back to external registries |
| **Create a new skill** | `skill-forge` → aos-add-a-skill (critique gate) → skill-creator (scaffold) | Claude | Critique-then-scaffold. The critique prevents skill bloat |
| **Design single-source Claude/Codex skill distribution** | `skill-forge` + company-skills marketplace template reference | Claude designs, Codex scripts | Reference pattern from the June 2026 intake; critique gate still applies before adding skills |
| **Build a Windows desktop launcher / shortcut / .lnk / hidden CMD** | `windows-launcher` (standalone keeper) | Claude | Port-aware launchers, branded icons, process hiding; reads dev-registry/ports.md. Hardcodes real Desktop (no OneDrive/GetFolderPath) |
| **Need active-window title / bounds / foreground metadata** | `windows-launcher` + `get-windows` primitive | Codex/PowerShell/Node | Use only as an implementation helper for launchers or desktop automation, not a new top-level skill |
| **Audit the harness for token waste / context bloat** | `context-audit` (standalone keeper) | Claude | Audits MCP servers, CLAUDE.md, skills, settings; returns a health score with specific fixes |
| **High-stakes plan needs a second-model stress-test / "argue this plan with Codex"** | `/codex-review` (harness skill, ~/.claude/skills) — or `/grill-me-codex` for interview-first | Claude drafts + arbitrates, Codex critiques read-only | Adversarial VERDICT loop, MAX_ROUNDS=5, log = PLAN-REVIEW-LOG.md. Installed 2026-07-08; see [[Reference/grill-codex-adversarial-pipeline]] |
| **Frozen spec ready → have Codex implement it with a bounded verify loop** | `/codex-build` (harness skill) | Codex writes (--yolo), Claude reviews diff + runs proof | Clean-tree gate; MAX_FIX_ROUNDS=2 then Claude takes over; human-gated Claude-authored commit |

---

## Cross-cutting rules

- **When the chooser is unclear → run `skill-scout`.** Don't guess.
- **When the user corrects a tool choice → store as action-default in second-brain.** Don't ask twice (same session or future).
- **A mechanic never auto-spins-up all its wrenches.** Pick the one or few that fit the job.
- **Always-core at session start:** `router`, `second-brain`, `guard`. Everything else on-demand.
- **Claude thinks, Codex does.** When ambiguous, ask. When implementation work appears, dispatch to Codex via router. Don't grind code in Claude.
- **No errors twice.** Every error → root-cause → fix → stored in second-brain as "what / cause / fix / prevention".
- **Autonomy is opt-in.** No skill self-starts, but the user may stand up unlimited automations — budget-gated by `_system/automations/` (10M/day circuit breaker + `HALT` kill-switch). See AGENTS.md rule #1.
- **Cost-first scraping.** Firecrawl → Cloak Browser → local drivers. Always.
