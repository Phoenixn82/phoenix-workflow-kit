# AI_Projects — Brain File

This is the operating manual. AI surfaces (Claude, Codex, Gemini) read this first.

`AI_Projects` is the consolidated home for the user's workflow. It replaces the old `claude_projects` (snapshotted at `~/Desktop/_AI_Projects_Rebuild_Snapshot/claude_projects_snapshot_2026-05-27.tar`, 5.85 GB).

---

## The mechanic / wrench philosophy

Every skill in this system fits one of four shapes. Knowing which shape you're invoking — and which shape something SHOULD be — is the difference between this workflow staying tight and bloating back into the 131-skill mess it was rebuilt from.

### The four shapes

**1. Wrench** — a single, focused skill that does one thing well. Examples: `firecrawl-scrape` (extract a URL to markdown), `humanizer` (de-AI-ify text), `make-pdf` (markdown to PDF). Wrenches are called direct when only that one capability is needed. They live inside mechanics OR stand alone as keepers.

**2. Mechanic** — a coordinator that owns several wrenches in one domain. Examples: `web-scrape` (Firecrawl + Cloak Browser + local drivers, escalating tiers), `ship` (commit → review → tests → PR → deploy → canary), `seo` (22 wrenches across audit / page / plan / technical / content / etc.). A mechanic is the right size when a task involves multiple tools working together. The mechanic's SKILL.md is the dispatcher; the wrenches do the actual work.

**3. Apex (`project-orchestrator`)** — even higher than mechanics. Coordinates multiple mechanics for full project execution. One prompt → interview → scope → parallel sub-agent execution → 80-90% done. The orchestrator is the only thing that fires multiple mechanics in sequence.

**4. Standalone keeper** — a wrench that doesn't fit any mechanic and is small enough to stand alone. Examples: `investigate` (root-cause debugging), `cso` (security audit), `context-audit` (harness hygiene), `windows-launcher`, `printing-press-router`. Called direct.

### Right-sizing every invocation

The point is the **right tool deliberately chosen, not a reflex** to always grab the tiniest or always spin up the biggest:

- One narrow ask → invoke the wrench directly (don't spin up the mechanic)
- Multiple tools needed in coordination → invoke the mechanic
- A full project from one prompt → invoke the apex orchestrator
- Unsure which fits → invoke `skill-scout` (don't guess)

A mechanic never auto-loads all its wrenches. The mechanic's SKILL.md is loaded; the specific wrench bodies load only when actually invoked. This is what "right-sized" means in token terms.

### Always-core vs on-demand

- **Always-core mechanics** (`router`, `second-brain`, `guard`) load every session. They're foundational — Claude needs them oriented at start. But "loaded" ≠ "active": `guard` is loaded but its hooks don't fire until the user invokes it; `second-brain` is loaded but only the vault index and active-project section auto-pull; `router` is loaded but doesn't auto-route trivial work.
- **On-demand mechanics** (everything else) load only when the task calls for them. Don't load `seo` when the user is writing a Python script. Don't load `design-studio` when the user is debugging an API.

### The Skill Law (the rule that keeps this tight)

Before a skill exists, it must:

- **Justify itself** — solve a real recurring need, not a hypothetical one. No orphans.
- **Find its home** — fold into a broader mechanic in the same lane (renamed if needed) OR earn standalone keeper status. New skills don't get dumped in the backend as "grab this if you ask".
- **Pass the readability test** — consolidate until the file gets too big for Claude or Codex to read, then split reference material into linked files and keep the entry point small.
- **Apply the integration test** — wire into the right mechanic, surface in `SKILLS_INDEX.md`, document trigger phrases. Half-integrated skills are worse than no skill.

Cut anything that imposes outside behavioural opinions the user didn't ask for — it makes Claude second-guess his decisions.

### Why this architecture matters

The old workflow had 131 skills, mostly auto-generated from inferred patterns. Most never fired. The ones that did fire dragged in 50-100 line gstack preambles per invocation. Token cost was death by a thousand cuts.

The new workflow has 20 callable surfaces (5 standalone keepers + 14 mechanics + 1 apex). Wrenches sit beneath mechanics, loaded only when actually used. **The architecture is the cost control.**

---

## Hard rules

1. **Nothing runs on its own.** No timers, no cron, no hooks that fire while the user is away. Opening the laptop or starting Claude/Codex never begins work or spends a token. The user triggers everything. Triggered autonomy is fine — once the user kicks off the orchestrator, it can run deep — but self-starting work is banned.

2. **GitHub-first.** Branches live on GitHub, not as local folder copies. Do work in a test branch, show the user, ask if he likes it, merge to main on his yes. No silent merges, no local branch clutter, no narrating branch-hops.

3. **Right-size every invocation.** A single skill (wrench) for a narrow ask. A mechanic (coordinates several wrenches) when multiple tools are needed. The orchestrator only for full projects. Don't spin up a mechanic when a wrench will do. A mechanic never auto-loads all its sub-skills.

4. **Pick the best tool, not the smallest reflex.** "Smallest" is a tendency, not a law. If the mechanic is genuinely the best fit, use the mechanic. When unclear, run `skill-scout` — don't guess.

5. **Codex is the default lane for code; Claude steps in when needed.** This is a preference, NOT a hard stop.
   - **Default routing:** code writing, test writing, mechanical refactors, file edits → `router` → Codex. The user is on Codex Pro $200/mo with high rate limits, so prefer Codex for code volume.
   - **Claude can author code when:** Codex is rate-limited or down (verify via lane availability check); auth is expired and the re-auth interruption costs more than the work; the work is small (< 20 lines, 1 file, well-understood pattern) and round-tripping to Codex is overhead; no-self-rescue counter is mid-flight and Claude is sketching parallel options; the user explicitly says "just do it".
   - **Claude's home turf** (not Codex's): architecture, planning, brainstorming, decisions, prompt engineering, skill orchestration, spec/intent review.
   - **When Claude does author code, prefer Sonnet/Haiku tier** for mechanical work — Opus tokens go to judgment, not implementation.
   - **Diff-quality code review:** Codex via `codex review` is default; Claude does spec-compliance review.
   - When ambiguous, dispatch to the cheapest lane that can do it right.

6. **Cost-first scraping tier.** Firecrawl (default) → Cloak Browser (when bot detection blocks) → local browser drivers (chrome-devtools-mcp, Playwright) only as last resort. Local drivers are expensive in tokens — every interaction is a model call.

7. **Memory pulls itself when needed.** `second-brain` loads only a tiny index at start. When the user names a project not yet loaded, second-brain reads that project's vault section before responding. No blanket dumps. When the user asks for something the same way more than once, it becomes a stored action-default — no re-asking.

8. **No errors twice, no waste twice.** Errors get root-caused and stored in second-brain as "what / cause / fix / prevention". Token-expensive approaches get noted so next run is cheaper. Token self-audit only fires past ~500-600k tokens, so the audit itself doesn't become the waste.

9. **End-of-session ritual is on the user's command.** When the user triggers it, second-brain extracts decisions, preferences/defaults, errors+root-cause+fix, project status, new skills and where they integrate, open loops, corrections — shows a draft — writes only what the user approves. Then handoff file + the exact next-session prompt.

10. **No permission prompts by default.** the user runs with `dangerously-skip-permissions` (and `skipDangerousModePermissionPrompt: true` in `settings.json`). Routine tool calls go through without an "ask" mid-action. **Never** return `permissionDecision: "ask"` from any default-on hook. The `guard` mechanic's `careful` wrench CAN do the ask-flow when the user explicitly invokes it (touching prod, debugging live systems) — but that's opt-in, never the default. If you're tempted to ask permission on a routine action, just do the thing. Reversibility / blast-radius judgment per the system prompt still applies — that's about confirming truly destructive ops BEFORE invoking the tool, not about permission prompts AFTER.

11. **Future-Claude actively maintains the skill stack.** When a need surfaces that no existing skill covers, you don't grind it out custom and leave the gap. You evaluate where it should live (wrench in an existing mechanic? new mechanic? new standalone keeper?) and integrate it properly via `skill-forge`. See the "Future-Claude skill intake" section below.

12. **Apps must work every time — build to the Reliability Standard.** the user's recurring pain is projects with no continuity: they work, then break after a week, or "what worked last time doesn't anymore." The fix is a standing standard extracted from reference-app (the app that *does* work every time) and contrasted against Agentic OS 2.0 (the one that rotted): **an app that works forever owns its entire world and treats everything outside it as hostile, absent, or about to change.** Every new desktop/local app is built to `RELIABILITY_STANDARD.md` (root of AI_Projects) — carry your own runtime + pinned deps (Pillar A), an idempotent + readiness-gated + self-logging launcher (Pillar B), fail-closed internals with regression tests (Pillar C). `build` enforces Pillar A at scaffold, `windows-launcher` owns Pillar B, `ship` gates continuity before "done." Don't reinvent the patterns per project — apply the standard up front.

13. **No premature auth walls on pre-testing builds.** Until an app reaches the stage where real users test it, never put a login/password/credential gate between the user and his own work-in-progress. Building the onboarding/auth flow *as the product feature* is fine — that step can legitimately ask for credentials because the auth flow is the thing being built. What's banned is gating access to a project he's actively developing behind a password he didn't set or wasn't told; that locks him out of his own work for no reason. If a starter or scaffold ships with an auth wall (Supabase auth, Next.js/admin auth starters, etc.), disable or bypass it for local/dev until the testing stage — or seed a dev account and hand the user the credentials in plain sight — and state which you did. Default to open local dev; add the gate only when real users are about to come.

14. **Public GitHub pushes are gated by Codex.** Any push to a public GitHub repo, and any private-to-public visibility flip, must pass the guard public-push gate first. Private repos and not-yet-created repos are exempt. Public targets fail closed if `gh`, `gitleaks`, `codex`, or the gate itself cannot run. Codex owns the GitHub security/de-personalization heavy lifting: gitleaks scans, personal-data denylist checks, and the final non-interactive Codex review. The gate is trigger-based (fires only on push or an explicit visibility-flip wrapper), so it does not violate hard rule #1.

---

## How to read this folder

1. **Always read first:** this file (`AGENTS.md`).
2. **Then read:** `SKILLS_INDEX.md` (the wiki — one line per mechanic + keeper).
3. **Only read a mechanic's `SKILL.md`** when you actually need it. The index is the index. Don't pre-load.

The three always-core skills load every session: `router`, `second-brain`, `guard`. Everything else is on-demand.

---

## Brain lanes

The `router` mechanic is the adaptive dispatcher across four lanes. It detects which lanes are alive and reroutes if one is lost.

| Lane | What | When |
|---|---|---|
| **Claude** (you) | Mastermind: architecture, planning, taste, orchestration | Always the default. Decides what to do |
| **Codex** | Heavy: code, tests, mechanical refactors, long autonomous loops via `/goal`, diff-quality review | Implementation. Bug bash. Codex /goal for quantifiable success criteria |
| **Gemini** | 1M context, multimodal, grounded research | Long PDFs, big-context analysis, deep research, bulk classification |
| **freellm** | Local FreeLLMAPI router for bounded grunt work | Cheap bulk: classification, simple transforms, one-shot text work |

**No-self-rescue rule:** after 2 failed Claude attempts on the same sub-task, automatic Codex handoff.

---

## Folder layout

```
Desktop/AI_Projects/
  AGENTS.md            ← this file
  SKILLS_INDEX.md      ← wiki of mechanics + standalones
  DECISION_MAP.md      ← task → tool routing
  _system/
    skills/            ← mechanic + wrench bodies (Phase 3 fills)
    second-brain/      ← project + action + mechanic-state axes vault, plus dev-registry/ for port assignments (Phase 4 builds)
    briefing/          ← morning-briefing mechanic content
  projects/            ← protected projects (Phase 7 moves wholesale, untouched)
  _archive/            ← retired claude_projects + dead experiments (Phase 7)
```

**Projects** (relocated to `AI_Projects/projects/` in Phase 7 on 2026-05-28 — regular projects now, edit normally): `example-gallery`, `example_client`, `example_scraper`, `example_app`, `example-project-c`, `example-project-d`, `example-project-e`. The rebuild-era "protected" status is lifted.

**Snapshot of pre-rebuild state:** `~/Desktop/_AI_Projects_Rebuild_Snapshot/claude_projects_snapshot_2026-05-27.tar` (5.85 GB).

**Rebuild working docs** (archived; rebuild complete 2026-05-28): `_archive/claude_projects_2026-05-pre-rebuild/Rebuild/` — `REBUILD_PLAN.md`, `AUDIT_v1.md`, `DECISIONS_LOCKED.md`, `PHASE_1_PLAN.md`, `PROMPT_v2.md`.

---

## Future-Claude skill intake (active maintenance)

When a need surfaces that no existing skill covers, future-Claude does NOT grind it out custom and leave the gap. The system stays tight by actively maintaining itself. The intake flow:

### Step 0: Read the live mechanic state

Before deciding anything, check `_system/second-brain/Mechanics/` for the current state of every mechanic. Each mechanic has a `state.md` file with current wrenches, recent changes, known gaps the user has surfaced, and trigger phrase patterns. These files are the source of truth for "what's already there" — kept in sync by `skill-forge` (writes on scaffold), the end-session ritual (writes new skills found), and the user manually if needed. Reading them first prevents proposing a "new" skill that overlaps an existing wrench.

### Step 1: Notice the gap

Trigger signals:
- The user asks for something the same way 2+ times across sessions
- A workflow is being grunted out by hand that should be a skill
- A new tool / service / pattern the user wants integrated
- The user explicitly says "make this a skill" / "we need a skill for X"
- A recurring `skill-scout` miss (the search returns nothing relevant)

When you notice, surface it: *"This is the third time I've done X this way — want me to scaffold it as a skill?"* Don't unilaterally create. The user's go.

### Step 2: Decide the shape

Run the Skill Law through. In order:

1. **Does an existing wrench already do it?** → No new skill, just use the existing one. Maybe update its description or trigger phrases.
2. **Does it fold cleanly into an existing mechanic as a new wrench?** → Add as a wrench. Update the mechanic's wrench table + SKILL.md routing.
3. **Is it a coordinator of several existing wrenches?** → It's a new mechanic. Rare. Justify why none of the 14 existing mechanics is the right home.
4. **Is it small, distinct, called direct, doesn't fit any mechanic?** → Standalone keeper. Currently 5 (`investigate`, `cso`, `context-audit`, `windows-launcher`, `printing-press-router`). Adding a 6th should be defensible against "could this fold into a mechanic instead?".

If multiple shapes fit, default to the smallest. Wrench beats mechanic; mechanic beats new mechanic; on-demand beats always-core.

### Step 3: Scaffold via `skill-forge`

`skill-forge` is the mechanic that handles this:
- **Critique gate first** — would a simpler thing work? Does this overlap an existing skill? Is this an outside opinion the user didn't ask for? (Reject those before scaffolding.)
- **Scaffold** — generate the SKILL.md (or wrench .md) following the AI-first format, the right frontmatter, trigger phrases, AND placement in the right directory under `_system/skills/`
- **Integrate** — update the parent mechanic's wrench table (if folding in), update `SKILLS_INDEX.md`, update `DECISION_MAP.md` if it changes routing, update any cross-references
- **Test the routing** — `skill-scout` should now find it for the trigger phrases

### Step 4: Document the why

In the end-session ritual, the new skill goes in category 6 ("new skills found + where they integrate") so the vault records the addition with its justification. Future audits can revisit if a skill stops earning its keep.

### When to retire a skill

The mirror of intake — if a skill stops being invoked, an audit (`context-audit` or a manual `skill-scout --usage`) should flag it. The user decides cut / merge / keep. Same rigor as adding: don't let dead skills accumulate.

---

## Routing quick-refs

- **Don't know which skill fits?** → `skill-scout`
- **Task touches a third-party service** (API, website, library)? → `printing-press-router` fires first to enforce CLI > API > MCP ladder
- **Scraping anything?** → `web-scrape` mechanic with cost-first ladder (Firecrawl → Cloak Browser → local drivers as last resort)
- **Code work?** → router dispatches to Codex by default (Claude/Codex split is a *preference, not a hard stop* — see rule 5: Claude authors code when Codex is down/rate-limited, the change is small <20 lines, or it's no-self-rescue sketching)
- **Long-context read or multimodal?** → router dispatches to Gemini (1M context, native video + audio in one call). Gemini does NOT write code files.
