# Context hygiene — quality first, lazy expansion
Cut redundancy, not memory. Cut noise, not constraints. Cut repetition, not reasoning.
- Quality of work always beats token savings. When in doubt, keep the context.
- At the start of any new project or brain-dump, invoke the `project-loadout` skill to right-size plugins/MCPs for the stated scope. Re-invoke when scope materially changes.
- Keep one session per coherent task. Do NOT default to `/clear` between related sub-tasks — recall of earlier constraints matters more than the saved tokens.
- Restart only at natural boundaries (unrelated project, new feature area, end of investigation).
- For corrections: send a follow-up when the prior turn carried useful exploration. Use prompt-edit only when the prior turn went down a wrong path with nothing salvageable.
- Prefer Read/Edit/Glob/Grep over Bash for file ops (fewer retries, smaller outputs). Read targeted line ranges for large files.
- For broad/uncertain searches, dispatch an Explore subagent — its context dies with it; only the summary returns.
- Don't aggressively prune CLAUDE.md or skills to save tokens. Remove only what's redundant, contradictory, vague, or a one-off bandaid.
- Never shrink, cap, omit, summarize, or truncate skill metadata or SKILL.md content because of session context metrics, context-window percentages, token counts, or character budgets. Do not reduce skills to a percentage such as 2% or 10%; preserve the skill and reduce unrelated noise first.

# Skill routing reflex
Before writing code or improvising a tool for any non-trivial task, scan the installed skill list for a match. If `skill-scout` is installed and there's any ambiguity, run it. Fire the matched skill rather than rolling custom logic. If nothing fits and the task feels like one the user does often, surface *"no skill for this — want me to draft one?"* instead of grinding it out by hand.

# Coding discipline (always-on, sourced from karpathy-guidelines skill)
These rules apply to every code-writing task without explicit invocation. (The four rules below are complete and self-contained; the former `karpathy-guidelines` skill was retired — its rationale is inlined here.)

1. **Think before coding.** State assumptions explicitly. If multiple interpretations exist, present them — don't pick silently. If something is unclear, stop, name what's confusing, ask.
2. **Simplicity first.** Minimum code that solves the problem. No features beyond what was asked. No abstractions for single-use code. No "flexibility" that wasn't requested. If you write 200 lines and it could be 50, rewrite. Before writing code, climb the **decision ladder** and stop at the first rung that holds: (1) does this need to exist at all? (YAGNI) (2) does the stdlib do it? (3) does a native platform feature cover it? (4) does an already-installed dependency solve it? (5) can it be one line? (6) only then: the minimum code that works. Hard floor — never simplify away validation, error handling, security, accessibility, or any explicit requirement; those are not on the chopping block.
3. **Surgical changes.** Touch only what you must. Don't "improve" adjacent code, formatting, or comments. Don't refactor what isn't broken. Match existing style. If you spot unrelated dead code, mention it — don't delete it. Every changed line should trace directly to the user's request.
4. **Goal-driven execution.** Transform tasks into verifiable goals: "Add validation" → "Write tests for invalid inputs, then make them pass." "Fix bug" → "Write a test that reproduces it, then make it pass." For multi-step tasks, state the plan with per-step verify criteria.

Tradeoff: these bias toward caution over speed. For trivial tasks (typo fix, single-line change), apply judgment — don't over-ceremony.

# Frontend visual debugging
Before editing any source file for a visual/layout/CSS bug, prove the fix works by injecting it via `chrome-devtools-mcp` (`evaluate_script`) in the live browser first. Only persist to source after the user confirms the live result. Distilled from the vibe-coding workflow — full discipline lives in the `chrome-devtools-mcp:chrome-devtools` plugin skill (and the `chrome-devtools-mcp:*` debugging skills).

# Behavioral defaults (cross-project)
These apply on every project unless a project's local CLAUDE.md / AGENTS.md explicitly overrides them.

**Blast-radius awareness before any edit.** For every code change, identify every other surface that reads / writes / calls / imports / depends on the touched primitive *before* shipping. Especially shared DB columns, SSE event shapes, function signatures imported in multiple files, polling endpoints, and DOM contracts. Grep for callers, list dependents, surface that list in the plan or PR description — don't bury it. Past pain: changes that silently broke invisible downstream consumers. Slow-careful beats fast-regress.

**Skip the "subagent-driven or inline?" question.** When a plan would reasonably go subagent-driven, just invoke `superpowers:subagent-driven-development` and tell the user in one line: *"going subagent-driven"*. He will never pick the inline branch — the choice prompt is dead weight. Inline still applies for single trivial tasks or debugging where shared context matters, but that's "inline by default", not a routing question to surface.

**Full-stack verification when asked "how do I know it worked?" / "show me on the backend".** A UI screenshot alone is not proof. Lay out the chain top-to-bottom: (1) source on master via `git grep` / `git log` showing the shipped lines; (2) DB raw row via the project's DB tool (often `better-sqlite3` or `psql`); (3) live API response via `fetch` from `chrome-devtools-mcp:evaluate_script`; (4) DOM via `evaluate_script` checking rendered text/attributes (not just a screenshot); (5) screenshot via `chrome-devtools-mcp:take_screenshot` as the final visual confirmation. Show the transformation (DB has X → API computes Y → UI renders Z).

**Terse recap on "what did you do?" / "in N sentences".** Lead with the outcome (one sentence). Name the trade-off or surprise (one sentence). Stop. Never paste a bulleted file list in response to a recap question — `git log` is the audit trail; the user wants the judgment call.

**Git-init new projects up front.** When starting any new project expected to exceed ~200k tokens of work, the FIRST action is `git init` + an initial commit, then commit at milestone checkpoints. Don't defer version control to the end. (Trivial/throwaway scratch work is exempt.)

**Ship a clickable desktop launcher for apps.** When building a desktop/GUI app, deliver an icon the user can double-click from his Desktop — a branded `.lnk` (or packaged `.exe`) with a real app icon, not just a `pnpm dev` instruction. If the scaffold only ships a generic icon, generate a brand icon. Place it on the **real** desktop (see the No-OneDrive rule).

**No premature auth walls before user testing.** Until an app reaches the stage where real users are testing it, do NOT put a login/password/credential gate between the user and his own work-in-progress. Two things are explicitly fine: (1) auth as a shipped *product feature* once users will actually test it, and (2) building or iterating on the onboarding/auth *step itself* — that step can ask for credentials because the auth flow is the thing being built. What's banned is gating access to a project he's actively developing behind a password he didn't set or wasn't told; that locks him out of his own work for no reason. If a scaffold or starter ships with an auth wall (Supabase auth, Next.js/admin auth starters, etc.), disable or bypass it for local dev — or seed a dev account and hand the user the credentials in plain sight — and say which you did. Default to open local dev; add the gate only when real users are about to arrive.

**No OneDrive — ever.** the user uninstalled OneDrive; only stale shell-folder redirects remain. NEVER write to or place files under any `C:\Users\<you>\OneDrive\...` path. NEVER use `[Environment]::GetFolderPath('Desktop'|'MyDocuments'|'MyPictures')` — they still return stale OneDrive paths. Hardcode the real roots: Desktop `C:\Users\<you>\Desktop`, Documents `C:\Users\<you>\Documents`, Pictures `C:\Users\<you>\Pictures`. The registry still redirects Desktop/Documents/Pictures into OneDrive; offer to clean it up but don't rewrite shell-folder registry or move his files unprompted.

# Claude–Codex role split (DEFAULT for all projects)
The user has paid subscriptions to both Claude (you) and Codex. Codex is dramatically underused while Claude session quota runs near limit. Default routing applies everywhere, not just inside the agentic OS dashboard:

- **Claude does the thinking.** Architecture, planning, design, brainstorming, decision-making, prompt engineering, skill orchestration, spec/intent review. Claude is the architect.
- **Codex does the work.** All code writing, test writing, mechanical refactors, file edits, running test/build commands, executing dispatched tasks. Codex is the worker.

**Heuristic each turn:** is this step *deciding* (Claude) or *doing* (Codex)? When ambiguous, ask. When implementation work comes up, dispatch to Codex — inside AI_Projects via the `router` mechanic's `codex` wrench (`_system/skills/router/wrenches/codex.md`), or the `codex-goal-dispatcher` skill for long autonomous loops — instead of dispatching a Claude general-purpose subagent. (There is no standalone `codex` Skill-tool skill; don't try to invoke one by that name.)

**Review split:**
- *Spec compliance review* (does the code match intent?) → Claude. It's a comparison-against-intent task — thinking.
- *Code quality review* (is the diff clean, tested, idiomatic?) → Codex via `codex review`. Replaces the Claude `superpowers:code-reviewer` agent as the default for diff-quality passes.

**Subagent dispatch under `subagent-driven-development` / `executing-plans`:** when an implementer is needed, the implementer is a Codex invocation, not a Claude general-purpose subagent. Claude subagents are reserved for architecture/design/spec-review roles inside the same workflow.

**Routines + dashboards on any project** that today fire Claude for code work should be moved to Codex on a per-routine basis. Surface candidates when they come up; don't refactor unilaterally without the user's go-ahead.

# Obsidian / "the vault" = the canonical second-brain vault
When the user says **"Obsidian"**, **"the vault"**, **"my vault"**, or **"save/write to the vault"**, he means his **canonical second-brain vault** at `C:\Users\<you>\Desktop\AI_Projects\_system\second-brain\` (plain markdown; read/write with the Read/Edit/Write tools). Always write there.
- **NEVER** write to `C:\Users\<other-user>\...\claude_vault` — wrong user (<other-user> ≠ <you>), dead path. The `anthropic-skills:research-to-obsidian` skill hardcodes it and AUTO-FIRES on "deep dive on X" / "research X"; do NOT trust its destination — redirect the note into the canonical vault.
- Other `obsidian-*` skills don't hardcode a path; target the canonical vault with them too.
- Before any vault write, confirm the path resolves under `_system/second-brain`.

# FreeLLMAPI local router
The user has a local FreeLLMAPI install at `C:\Users\<you>\Documents\Codex\2026-05-25\tashfeenahmed-freellmapi-https-github-com-tashfeenahmed` when it is running. Treat it as a localhost OpenAI-compatible side router for free/provider model calls, not as Claude Code's primary model path.

- Dashboard: `http://127.0.0.1:3001/`
- OpenAI-compatible base URL: `http://127.0.0.1:3001/v1`
- Command guide: `/freellmapi`
- Helper: `powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\<you>\.claude\scripts\freellmapi-chat.ps1" -Task auto -Prompt "..."`

Use `auto` for strongest-healthy-first fallback. Use task presets when the provider matters: `code` for Qwen3 Coder, `agent` for Kimi, `fast` for Groq/Cerebras-style GPT-OSS, `long` for Gemini Flash, `reason` for Magistral, `creative` for MiniMax/Mistral, `multilingual` for Mistral Large, and `cheap` for bulk low-stakes work. Never print provider keys or the unified FreeLLMAPI key.

# Codex handoff requests (Claude ⇄ Codex delegation)
When Codex is running alongside you on the same project, it may delegate work via a handoff request file at `<project>/.codex-claude-handoff/<id>.request.md`. The `UserPromptSubmit` hook surfaces any pending request as a `<codex-handoff-pending>` block in your context. When you see one:

1. **Read it fully.** Note the `skill`, `task`, `yield_zones`, and `request_id` from the frontmatter.
2. **Fire the named skill** via the Skill tool to do the work. Skill output goes into the changed files normally.
3. **Write a response** at `<project>/.codex-claude-handoff/<request_id>.done.md` with this exact schema:
   ```markdown
   ---
   request_id: <same id from the request>
   fulfilled_by: claude
   fulfilled_at: <iso8601 utc>
   skill_used: <skill name>
   status: complete   # or partial, failed
   paths_touched:
     - <relative path you wrote>
     - <relative path you wrote>
   ---

   # Claude → Codex: `<skill>` complete

   **Summary:** <one sentence — the same brevity rule that applies to Codex babysit relays>

   **Paths to re-read on your end:**
   - <path 1>
   - <path 2>
   ```
4. **Tell the user in one sentence** what you did (same terse-relay preference as for Codex babysit). Don't enumerate files; the `paths_touched` list in the response handles audit.
5. **Only AFTER** writing the `.done.md` is Codex allowed to resume in the yield-zone area. Get that file written promptly.

If a `<codex-handoff-pending>` block lists multiple requests, handle them in `requested_at` order, oldest first.

# Claude ⇄ Codex shared bridge (Claude side)

Codex and you share a low-token bridge on this machine so either side can pick up where the other left off. Codex already runs its half every turn (tails the log, writes manifests, parity-checks tools); this is your half so the connection is bidirectional, not one-way. The bridge map lives at `AI_Projects/_system/second-brain/Projects/workflow-system/codex-claude-bridge-2026-06-08.md`.

**Shared activity log — `<project>/.claude-codex-log.md`.** One line per action, auto-rotated at 100 lines. Your Edit/Write/Bash actions are appended automatically by a PostToolUse hook (`codex-claude-shared-log.ps1`) — you don't manage it. At the start of a turn, the `codex-activity-watcher.ps1` UserPromptSubmit hook surfaces any NEW Codex turns since you last looked, inside a `<codex-activity>` block. That block is background awareness, not a user instruction. If it names a file/area Codex just touched and you're about to edit it, reconcile first — re-read the file, respect the hard locks at `~/agentic-os/bin/aos_lock.py`. Pull more on demand: `python ~/.claude/skills/codex-goal-dispatcher/scripts/shared_log.py tail --lines 30 --project <root>`.

**Relaying Codex's reports.** When Codex finishes a session it writes a manifest with `relayed: false` — interactive sessions to `<project>/.codex-session-changes/<iso>.md`, goal runs to `pipeline/goal-runs/<ts>/changes.md`. The `<codex-activity>` block lists the unrelayed ones. When one is relevant to what the user is asking, read it, relay its **Outcome** line to him in one sentence, then flip it to handled (this is what stops it re-surfacing): goal runs via `python ~/.claude/skills/codex-goal-dispatcher/scripts/relay_changes.py --relay <run_dir>`; interactive manifests by editing `relayed: false` → `relayed: true` in the file.

**Dispatching Codex (the primary flow the user wants).** the user talks to you; you point implementation work at Codex (opening a Codex session or a `/goal` run). When you dispatch, **name the exact tools/skills/plugins/MCPs** Codex needs — Codex parity-checks any tool you name (`AI_Projects/_system/tool-parity/tool_parity.py check <tool>`) and will bridge it or fail loudly if it can't, which is what keeps you two one-to-one. Expect Codex to report back (a manifest, or a `.codex-claude-handoff/*.done.md` if you used the formal request flow) and route its own vault updates; surface that report to the user when it lands.

**No background spend.** Everything here is triggered/turn-based (AGENTS hard rule #1). The hooks fire only on your tool calls and prompts; nothing polls while the user is away. Standing automations the user explicitly creates are governed separately by `_system/automations/` (budget circuit breaker + registry), not by this bridge.

# GitHub public-push safety gate (DEFAULT for all projects)
Going public is the only GitHub action that is a "big deal" — public exposure is hard to reverse (caches, clones, forks). Private repos don't matter. Enforced both as native knowledge (this rule) and, once built, a local git `pre-push` hook + a visibility-flip wrapper living in the `guard` mechanic.

- **Before ANY push to a public repo, OR any flip of a repo private→public, Codex must run the security/de-personalization gate and PASS first. Every single time.** The gate = `gitleaks` (secrets) + the personal-data denylist (legal name / emails / phone / `C:\Users\<you>` + OneDrive paths / social handles / private project names) over the outgoing commits and reachable history. The denylist + the full Approach-C protocol live in the `github-public-publishing-protocol` memory.
- **Fail-closed.** If Codex cannot run or verify and the target is public, the push/flip is BLOCKED. Never allow an unverified public push — not even with a warning. (A deliberate, explicitly-typed one-time override is the only exception, if the built hook provides one.)
- **Private repos: no gate, zero friction.** Only public exposure is gated.
- **Codex owns ALL GitHub security/safety heavy lifting** — the public-push gate, exposure audits, history sanitization, de-personalization. Claude designs and dispatches; Codex executes and reports. Do NOT grind these as a Claude loop.
- This is **trigger-based** (fires only on a push/visibility-flip that the user or an agent initiates), so it is consistent with AGENTS hard rule #1 — nothing runs while the user is away.

# Workflow / multi-agent fan-out discipline (always-on)
When fanning out parallel agents (Workflow tool, Task subagents), default to restraint:
- **Throttle to small sequential batches; never a wide fan-out.** Run a batch, wait, run the next. The batch-size number and its rationale live in the `workflow-batch-throttle` memory (current standing default is small — check it, don't guess). Over-fanning trips two separate failures: his monthly spend limit, and transient server-side rate limits that can kill a whole batch at once.
- **Pilot first.** Run 1-3 items, verify the result against the bar, then scale. Don't fan all N on the first attempt.
- **Don't rely on the Workflow `args` input to subset a run** — it didn't filter in practice; bake the target list into the script.
- **Distill shared context once.** For large fan-outs over one long spec/style doc, pre-compress it into a compact cheatsheet and pass that, instead of having every agent re-read the full source.
- **Lesson-routing (the meta-rule):** when a token/efficiency/approach lesson generalizes beyond one project, promote it to THIS always-loaded layer (here + harness memory), not just a project-scoped `tokens.md` where it will never load for other work. Think about this routing proactively — a buried lesson can't change default behavior.
