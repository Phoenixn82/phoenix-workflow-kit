---
name: router
description: Adaptive multi-brain dispatcher across Claude / Codex / Gemini / freellm. Loads every session as always-core. Detects available lanes, reroutes on loss, enforces no-self-rescue (2 Claude fails on the same sub-task → Codex). Routes by cost and capability. Fires on every non-trivial conversation start, every major task transition, and on phrases like "ask all three / four", "consensus", "debate", "second opinion", "rescue this", "deep research", "long PDF", "grunt work", "classify these", "bulk".
---

# router — multi-brain dispatcher

One prompt, four lanes, the right one tagged in for the job. Claude orchestrates; the router decides which brain executes.

| Lane | Job | Cost |
|---|---|---|
| **Claude** (you) | Think — architecture, planning, judgment, conflict resolution, decision-making | $100/mo Max subscription |
| **Codex** | Build — single-file code, tests, scaffolds, mechanical refactors, dispatched goals, diff-quality review | $200/mo Pro subscription, generous rate limits — the user can use Codex liberally |
| **Gemini** (paid sub) | Long-context **READ + ANALYSIS**, multimodal (native frames + transcript in one call), grounded research. **Gemini does NOT write code to files.** | $20/mo Gemini Advanced subscription, very generous Pro quota |
| **freellm** | Grunt work — bulk classification, repetitive transforms, low-stakes per-item processing | $0, bounded quality, ~20 free providers via local router |

**Cost ordering (cheapest → most expensive per equivalent task):** freellm → Gemini → Codex → Claude. Default to the cheapest lane that can do the work correctly. Escalate only when the cheap lane fails the quality bar.

This mechanic sits ABOVE the `codex`, `gemini`, `codex-goal`, `freellmapi` wrenches — it does not duplicate them; it decides which one to call and when.

---

## When this fires (always-on)

The router fires automatically when any of these conditions is true. **No user prompt needed.**

1. **Multimodal source over 3 MB** (`.mp4 .mov .mkv .webm .mp3 .wav .m4a .pdf`) → **Gemini** lane.
2. **Single-task context window > 300K tokens** (whole-repo reads, long logs, big PDFs, multi-hour transcripts) → **Gemini**.
3. **Deliverable is a code artifact** (`.py .ts .tsx .js .go .rs .sql .yml .yaml .json Dockerfile .tf` etc.) → **Codex** (single file) or **Gemini-spec → Codex-writes** (multi-file: Gemini reads + specs, Codex authors per-file). Default: Codex is the code lane; Claude steps in when needed (Codex down, small + well-understood, the user says "just do it"). See § Code routing rule.
4. **Bounded grunt-work signal** — N-item bulk processing, simple classification, regex/format transform per item, batch translation, tag-each-of-these, score-each-of-these → **freellm** (`auto` preset by default, pin a task preset when provider matters). See § The Grunt Rule.
5. **Repetitive / batch-shaped ask** (again-and-again work, >10 similar iterations, run-until-criterion) → run the `loop-sense` checklist before grinding.
6. **Same sub-task failed twice on Claude** → forced **Codex rescue**. No third Claude attempt. See § The no-self-rescue rule.
7. **Consensus phrases** (see table below) → **parallel debate** across the relevant lanes.
8. **Planning / scope / judgment / coordination** → route to the appropriate Claude tier (Opus / Sonnet / Haiku per § Opus-conservation).

If none of the above hit and the task is plain build/refactor/explain → **stay on Claude**. Do not route trivial work. Trivial routing adds latency without payoff.

---

## Explicit-phrase triggers

| Phrase from the user | Route |
|---|---|
| "ask all four" / "ask all three" / "debate" / "consensus" / "what do they all think" | Parallel — see § Parallel consensus |
| "second opinion" / "review my code" / "is this right" / "rescue" / "outside voice" | `codex` wrench (review or challenge mode) |
| "analyse this video" / "watch this clip" / "frame by frame" / "transcript + visuals" | `gemini` wrench |
| "huge PDF" / "long doc" / "200 pages" / "big context" / "1M tokens" / "whole repo" | `gemini` wrench |
| "deep research" / "research dossier" / "grounded synthesis" | `gemini` wrench → Deep Research sub-path (gemini.google.com via chrome-devtools-mcp) |
| "classify these" / "tag each" / "bulk process" / "for each of these N" / "grunt work" / "low-stakes batch" | `freellmapi` wrench |
| "do this repeatedly" / "again and again" / "batch this until done" / "run until it passes" / "loop-shaped" | `loop-sense` wrench |
| "/goal" / "kick off a codex goal" / "comprehensive user testing" / "lift coverage to N%" / "a11y pass on every page" / "bug bash" / "grind on this until tests pass" | `codex-goal` wrench |
| "use Codex" / "use Gemini" / "use freellm" / "use the local router" | Honour the user verbatim |

---

## Routing decision tree

```
                          ┌────────────────────────────┐
   user prompt ─────────► │  Bounded grunt work?       │
                          │  (bulk classify, per-item  │
                          │  transform, low-stakes     │
                          │  batch, N > 5 items)       │
                          └─────────────┬──────────────┘
                                        │
                             yes ◄──────┴──────► no
                              │                   ▼
                         freellmapi      ┌────────────────────────┐
                         (auto preset)   │  Multimodal, > 300K    │
                         Codex fallback  │  context, or deep      │
                         on junk         │  research?             │
                                         └────────┬───────────────┘
                                                  │
                                       yes ◄──────┴──────► no
                                        │                   ▼
                                    Gemini       ┌─────────────────────────┐
                                    (paid sub)   │  Code generation,       │
                                    Codex on     │  refactor, build?       │
                                    failure      └────────┬────────────────┘
                                                          │
                                               yes ◄──────┴──────► no
                                                │                   ▼
                                      ┌─────────────────┐  ┌─────────────────┐
                                      │ Single file?    │  │ Pure question   │
                                      │ Clean spec?     │  │ or analysis?    │
                                      └────┬────────────┘  └────────┬────────┘
                                           │                        │
                                    yes ◄──┴──► no             yes ◄┴──► no
                                     │          │               │        │
                                  Codex     Gemini-spec      Claude   Ask the user
                                  (1-shot)  → Codex writes   answers  to clarify
                                            (1M read,per-file)
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │ Risky path?          │
                          │ (auth/crypto/        │
                          │ payments/migrations/ │
                          │ secrets, SQL, .tf,   │
                          │ workflow YAML)       │
                          │ → auto codex review  │
                          │ before merge         │
                          └──────────────────────┘
```

**Risky-path heuristic** — auto-invoke `codex review` when edits touch any of:
- Anything under `auth/`, `crypto/`, `payments/`, `migrations/`, `secrets/`
- Any file matching `*.sql`, `*.tf`, `Dockerfile`, `*.yml` in `.github/workflows/`
- Anything that handles user-supplied input, JWTs, sessions, or shells out to a subprocess

---

## The code-routing rule (Codex preferred, Claude can step in)

**Default:** if the deliverable is a code artifact (a `.py`, `.ts`, `.tsx`, `.go`, `.rs`, `.sql`, `Dockerfile`, `*.yml`, `*.json` config, etc.), route to Codex via this mechanic. The user is on Codex Pro $200/mo with high rate limits — Codex is the right lane for the volume.

**Claude can author code when:**
- Codex is rate-limited or down (verify with lane availability check; do NOT silently fall back without surfacing the swap to the user)
- Codex auth is expired and re-auth would interrupt the user more than the work merits
- The work is small (< 20 lines, 1 file, well-understood pattern) — round-trip to Codex is more overhead than the actual task
- The no-self-rescue counter is mid-flight and Claude is sketching parallel options to compare against the Codex rescue
- The user explicitly says "just do it" / "you write it" / "don't bother dispatching"

When Claude does author code, **use Sonnet/Haiku tier**, not Opus. Opus tokens go to judgment, not implementation.

**The handoff pattern when Codex IS available:** Claude composes the spec, dispatches Codex (single-file) or Gemini-spec-then-Codex (multi-file), reads the result, decides if it's correct, integrates via Write/Edit, moves on.

| Sub-task type | Default lane |
|---|---|
| Project intake, scope shaping, work-order synthesis | **Opus 4.7** (claude-opus-4-7) — the "max" tier |
| Multi-system architecture, conflict reconciliation, ambiguous-output QA gates | **Opus 4.7** |
| Multi-step orchestration: reading N files, deciding what to delegate, dispatching sub-agents, synthesising their outputs | **Sonnet 4.6** (claude-sonnet-4-6) — coordination only, NOT code writing |
| Mechanical file ops Claude must do itself (file moves, JSON edits, regex/string transforms on small N, heartbeat appends, slug derivation) | **Haiku 4.5** (claude-haiku-4-5-20251001) |
| **ALL discrete code generation** — function, test, scaffold, CRUD endpoint, schema/type, boilerplate, single-file refactor, single-file translation | **Codex** wrench |
| **ALL multi-file code work** — refactors spanning ≥ 2 files, codebase-wide changes | **Gemini reads + analyses** to surface the full scope (uses 1M-token window to identify every file + the change needed per file as a written spec) → **Codex writes** per-file, one file at a time, from Gemini's spec. **Gemini does NOT write code to files.** |
| Code review, adversarial review, rescue from a Codex failure on simple work | **Codex** wrench (review modes) |
| Multimodal (video/audio/PDF), >200K-token non-code context, bulk extraction | **Gemini** wrench |
| Grounded web research with citations | **Gemini** wrench (Deep Research sub-path on gemini.google.com via chrome-devtools-mcp) |

**The handoff pattern:** Claude composes the spec → Codex/Gemini writes the artifact → Claude reads the result → Claude verifies + integrates via Write/Edit → Claude moves on. The orchestrator does NOT regenerate the code itself.

**Reverse rescue:** if Codex output is wrong twice on the same spec, do NOT escalate to Gemini for the rewrite (Gemini doesn't write code to files). Instead: **diagnose WHY Codex is failing** — network blip, timeout, ambiguous spec, file too large, missing context — then either (a) fix the root cause and retry Codex, or (b) have Sonnet re-spec the task more tightly (tighter constraints, clearer file boundaries, narrower scope) and re-dispatch to Codex. After 2 re-spec attempts that also fail, surface to the user — don't grind.

When dispatching sub-agents via the `Agent` tool, set the `model` parameter explicitly. Inheriting silently spends Opus on Sonnet-grade work or Sonnet on Haiku-grade work.

---

## The Grunt Rule (Claude does not run per-item loops)

**If the task is a per-item loop of N > 5 bounded, low-stakes operations, Claude does not run the loop.** `freellmapi` runs it. Claude reads the output and decides what to do with it.

Examples that route to `freellmapi`:
- Classify 200 inbound tickets into categories
- Translate 500 short marketing strings to 5 languages
- Tag 1,000 vault notes with topic labels
- Generate alt text for 100 images from filenames + context
- Score 50 SERP titles for clickability
- Extract structured fields (name, date, amount) from 300 OCR'd receipts
- Lint 80 prompt templates for clarity
- Pre-classify items before Claude makes the final judgment call on the borderline ones

**Rule of thumb:** if the output is text the user would commit to a code repo, Claude is not the author. If the work is the same operation done N times on bounded inputs, Claude is not the executor.

---

## The no-self-rescue rule (load-bearing)

Claude does not reliably recognise its own failures. The router enforces this rule mechanically:

```
attempt_count[task_id] += 1
if attempt_count[task_id] >= 2 and same_root_cause_as_last_attempt:
    REQUIRED: hand off to Codex (Gemini-spec-then-Codex for multi-file) before any further Claude attempt
```

**Same task =** same file + same error class + same general approach. If Claude pivots strategy completely (regex → AST parsing, for instance), the counter resets.

**Cross-vendor fallthroughs (freellm → Codex, Gemini → Codex) do NOT count as self-rescue.** Those are quota management. The counter tracks Claude→Claude retry cycles only.

### Handoff pattern

```bash
codex exec --skip-git-repo-check "$(cat <<'EOF'
Claude has failed twice on this task. Original ask:
<one-paragraph restatement of what the user wanted>

What Claude tried and why it failed:
- Attempt 1: <approach> → <error>
- Attempt 2: <approach> → <error>

Files involved: <paths>

Question for you: what is the correct approach? Be opinionated.
Return a concrete plan, not just a critique.
EOF
)" < /dev/null
```

> **Two CLI gotchas baked into every Codex command above and below** (verified against codex-cli 0.128, 2026-06-05):
> 1. **No `--plain` flag.** It was removed; `codex exec --plain` errors with `unexpected argument`. Plain output is the default. (`--adversarial` and `--xhigh` are gone too — use the prompt body for adversarial intent and `-c model_reasoning_effort="high"` for effort.)
> 2. **Close stdin or it hangs.** `codex exec`/`codex review` block on `Reading additional input from stdin...` in any non-TTY dispatch. Append `< /dev/null` (bash) or pipe `$null | codex …` (PowerShell) on every call.

After Codex returns a plan, Claude resumes execution — but the failure counter resets only when the bug is verified fixed.

### State file (when scripts land)

The counter persists at `~/.claude/state/attempt-counters.json` (the path `track_attempt.py` actually uses) so it survives session compaction, sub-agent dispatch, and overnight loops. (Migrated off the old `~/.gstack/three-brain/attempts.json` location.) Use the helper script `track_attempt.py` rather than editing JSON directly.

`<task_id>` convention: `<project>/<file_basename>/<error-class-slug>` (e.g. `example-app/auth.ts/type-mismatch`). Keep it stable across attempts so increments are detected.

---

## Multi-tier fallthrough chains

Each lane has a defined fallback when its provider misbehaves. Falls through silently for transient failures (quota, timeout, auth blip) and announces the swap in one sentence.

### Grunt-work chain: freellmapi → Codex → Claude-Haiku

```bash
# Tier 1: freellmapi (free)
if ! freellmapi --task auto --prompt "$PROMPT" > "$OUTPUT"; then
  echo "[router] freellmapi failed; falling through to Codex"
  # Tier 2: Codex (subscription-billed, cheap per call) — note `< /dev/null` to close stdin
  if ! codex exec --skip-git-repo-check "$PROMPT" < /dev/null > "$OUTPUT"; then
    echo "[router] Codex also failed; falling to Claude Haiku"
    # Tier 3: Claude Haiku (last resort)
    claude --model claude-haiku-4-5-20251001 -p "$PROMPT" > "$OUTPUT"
  fi
fi
```

### Long-context / multimodal **READ** chain: Gemini → Codex (analysis only, never code authorship)

```bash
# Tier 1: Gemini (paid sub) — for READ / ANALYSIS / TRANSCRIPT / SUMMARY tasks
if ! gemini --skip-trust -p "$PROMPT" < "$INPUT" > "$OUTPUT"; then
  echo "[router] Gemini failed; falling back to Codex"
  # Tier 2: Codex CLI supports ~100K context + image input via -i <FILE>
  codex exec -m gpt-5-codex "$PROMPT" < "$INPUT" > "$OUTPUT" || {
    echo "[router] Codex also failed; falling to Claude"
    claude -p "$PROMPT" < "$INPUT" > "$OUTPUT"
  }
fi
```

This chain is for analysis / summarization / extraction — Gemini producing a written report. **If the task is code authorship, this chain does not apply** — code work routes through the code-build chain below.

### Code-build chain: Codex → diagnose Codex → Sonnet re-spec → Codex retry

After 2 Codex failures on the same spec, the router does NOT escalate to Gemini (Gemini doesn't write code to files). Instead:

1. **Diagnose** — was it a network blip? Timeout? Ambiguous spec? File too large for Codex's window? Missing context Codex couldn't infer?
2. If diagnosis points to spec issue → **Sonnet re-specs** the task tighter (narrower scope, clearer constraints, explicit file boundaries, more inline examples) and re-dispatches to Codex
3. If diagnosis points to infra issue → fix and retry
4. After 2 re-spec attempts also fail → **surface to the user.** Don't grind.

The point: when Codex is the right tool but failing, fix the dispatch quality, don't switch lanes. Sonnet's role is to re-spec, never to write the code Sonnet would have rejected.

**Junk that triggers fallthrough** (within a single lane attempt):
- Empty content / whitespace only
- Content that clearly doesn't follow the requested format (asked for JSON, got prose; asked for one-line summary, got 20 paragraphs)
- A refusal or "I cannot" response on a benign request
- Provider-level error in the response wrapper

**Do not** silently fall through on a Codex/Claude-grade task that was misrouted to freellmapi in the first place. If the prompt was wrong-tier, fix the routing — don't paper over with retries.

---

## Parallel consensus mode

Triggered by "ask all four", "ask all three", "debate", "consensus", or "what do they all think". Run the relevant lanes on the same question with the **same prompt template** so answers are comparable. Use the `Agent` tool to run Codex / Gemini / freellmapi in parallel; Claude answers in-process.

**Default fan-out:**
- "ask all three" → Claude + Codex + Gemini (the classic; omit freellm — its free providers add noise, not signal, on judgment questions)
- "ask all four" → all four lanes including freellmapi `auto` preset
- "consensus" / "debate" → all four

**Cap at 5 parallel agents.** Diminishing returns past that.

**Output template:**

```markdown
## Question
<verbatim the user question>

## Claude's answer
<...>

## Codex's answer
<piped from `codex exec "<question>" < /dev/null`>

## Gemini's answer
<piped from `gemini --skip-trust -p "<question>"`>

## freellmapi's answer (auto preset, routed via <model>)
<piped from freellmapi-chat.ps1 — only included for "ask all four">

## Verdict
<2-3 sentence synthesis: where they agree, where they diverge, what's the strongest argument, what should the user actually do>
```

---

## Lane availability detection

The router only routes to lanes that are currently alive. Before any cross-vendor dispatch:

```bash
# Cheap filesystem + HTTP check (~5ms)
codex --version 2>/dev/null         # Codex CLI installed?
gemini --version 2>/dev/null         # Gemini CLI installed?
curl -s http://127.0.0.1:3001/v1/models 2>/dev/null | head -c 50   # freellmapi running?
```

If any lane is broken, refuse cross-vendor routing for that session and either ask the user to re-auth / restart, or stay on Claude. **Never silently degrade.** A downed lane at 3 AM should fail loud, not silently fall back to a Claude loop that drains the quota.

A deeper smoke test (~30s) verifies the user's auth and that each lane can actually return content. Run at session start or after re-auth, not on every call.

---

## Cost discipline & subscriptions

The user's actual stack:

| Lane | Subscription | Notes |
|---|---|---|
| **Claude** | $100/mo Max plan | the user's tier for this session. Used for thinking, planning, orchestration, spec-compliance review. Default routing: Codex is the code lane so Claude tokens go to judgment, not implementation. Claude can step in for code when Codex is down, the work is small + well-understood, or the user says "just do it". |
| **Codex** | $200/mo Pro plan | Much higher rate limits than the Plus tier. The user can use Codex liberally — diff reviews on most non-trivial work, single-file builds without rationing, autonomous `/goal` loops that grind for hours. Still skip Codex review on truly trivial diffs (3-line typo, comment-only, format-only autofix) because of routing latency, not budget. |
| **Gemini** | $20/mo Advanced (5TB) | Very generous Pro quota via CLI. Use Pro for anything multimodal or > 100K tokens. **Gemini does NOT write code files** — it reads, analyses, transcribes, summarizes, surfaces. When multi-file code work needs Gemini's 1M window, Gemini outputs a written spec; Codex writes per-file. Deep Research has its own per-day allowance via the web UI. |
| **freellmapi** | $0 (local) | Effectively unlimited across ~20 free providers via health-aware fallback. Grunt work only — bounded, low-stakes per-item. Never one-shot critical output. |

**All three paid lanes authenticate via OAuth using the user's existing accounts** — no API keys for the subscription path:
- Codex: `codex login` → OAuth via ChatGPT Pro account
- Gemini: `gemini` first-run → OAuth via Google account with Advanced subscription
- Claude: already authenticated (Claude Code session)

API keys are only used for the optional MCP delegation path (e.g., `@gemini` syntax inside Claude Code needs `GEMINI_API_KEY`). The subscription/CLI path does not.

**Cost ordering (cheapest → most expensive per equivalent task):** freellmapi → Gemini → Codex → Claude. Default to the cheapest lane that can do the work correctly. Escalate only when the cheap lane fails the quality bar.

---

## What the router does NOT do

- It does not replace the wrenches — `codex`, `gemini`, `codex-goal`, `freellmapi` remain the execution layer.
- It does not auto-route trivial tasks. One-liners, typo fixes, single-file reads → Claude alone.
- It does not silently swap brains mid-task. Every handoff is announced in one short sentence: *"Routing to Codex for review"* / *"Handing the video to Gemini"* / *"Bulk classification → freellm"*.
- It does not route important one-shot work to freellm. The free lane is for bounded grunt only.
- It does not auto-fire on grunt signals when the work is one-shot critical. Auto-fire applies when the prompt is per-item AND bounded AND low-stakes.

---

## Wrenches

| Wrench | Path | What it does |
|---|---|---|
| **codex** | `wrenches/codex.md` | Codex CLI: review (diff review) / challenge (adversarial) / consult (ask anything). Auth probe + filesystem boundary instruction baked in |
| **codex-goal** | `wrenches/codex-goal.md` | Long-running autonomous loop dispatcher. Template → spec → spawn Codex `/goal` → babysit → handoff. IRON RULE: never kill the Codex process |
| **loop-sense** | `wrenches/loop-sense.md` | Detects loop-shaped tasks and proposes budget-declared runbook drafts before any loop starts |
| **gemini** | `wrenches/gemini.md` | Gemini CLI + MCP delegation. 1M context window, multimodal, deep research via gemini.google.com (chrome-devtools-mcp drive) |
| **freellmapi** | `wrenches/freellmapi.md` | Local FreeLLMAPI router at `http://127.0.0.1:3001`. Task presets (auto / code / agent / fast / long / reason / creative / multilingual / cheap). Codex fallback on junk |

---

## Setup checklist (one-time)

If any lane is not yet ready:

```bash
# Codex (OpenAI)
npm install -g @openai/codex
codex login          # OAuth via existing ChatGPT account

# Gemini CLI (uses the user's paid Gemini Advanced quota)
npm install -g @google/gemini-cli
gemini               # OAuth via existing Google account
```

**freellmapi** lives at `C:\Users\<you>\Documents\Codex\2026-05-25\tashfeenahmed-freellmapi-https-github-com-tashfeenahmed`. Dashboard: `http://127.0.0.1:3001/`. Helper: `C:\Users\<you>\.claude\scripts\freellmapi-chat.ps1`. Verify alive: `curl -s http://127.0.0.1:3001/v1/models | head -c 100`.

---

## State files

Helper scripts live at `scripts/` (built in Phase 5, acceptance-tested 2026-05-28):

| Script | Purpose | State file |
|---|---|---|
| `scripts/preflight.py [--lane <name>] [--json]` | Deep auth + lane health check (claude/codex/gemini/freellm). Run at session start or after re-auth. Exit 0 if all healthy, 1 if any down. | n/a (probes live) |
| `scripts/track_attempt.py {get\|inc\|reset\|list} <task_id> [--max N]` | No-self-rescue counter. `inc` returns new count + exit 2 when count ≥ max (default 2) — signals "forced Codex rescue." | `~/.claude/state/attempt-counters.json` |
| `scripts/log_decision.py --lane X --task "..." --reason "..." [--project <slug>]` | Append routing decision to vault: `Actions/routing-defaults.md § Routing log` by default, `Projects/<slug>/decisions.md` with `--project`. 60s dupe-skip. | (writes to vault directly) |

State files (governed by `~/.claude/state/` per the no-permission-prompts rule):

| File | Purpose | Atomic? |
|---|---|---|
| `~/.claude/state/attempt-counters.json` | No-self-rescue counter (written by track_attempt.py) | Yes (temp + rename) |

**Migrating from old gstack paths:** the old `~/.gstack/three-brain/` state is read-only-archive; the new router uses `~/.claude/state/` (shared with `guard`'s freeze-scope file).

---

## See also

- [wrenches/codex.md](wrenches/codex.md) — Codex CLI wrapper, 3 modes
- [wrenches/codex-goal.md](wrenches/codex-goal.md) — long-running autonomous loops
- [wrenches/loop-sense.md](wrenches/loop-sense.md) — loop-shaped work detector and draft proposer
- [wrenches/gemini.md](wrenches/gemini.md) — Gemini delegation
- [wrenches/freellmapi.md](wrenches/freellmapi.md) — local FreeLLMAPI router
- [`AGENTS.md`](../../../AGENTS.md) — operating manual (Claude/Codex split, hard rules)
- [`DECISION_MAP.md`](../../../DECISION_MAP.md) — task → tool routing
