---
name: end-session
description: Wrench inside the `second-brain` mechanic. The full end-of-session extraction ritual. The user triggers. Extracts decisions / preferences / errors+root-cause+fix / status changes / new skills / open loops / corrections / token-expensive approaches → shows a draft → writes only what the user approves → writes handoff file + next-session prompt. The orchestrator (when built) triggers this automatically on scope completion. Fires on "end session", "save my work", "wrap up", "extract takeaways", "session done", "save and quit", "checkpoint this".
---

# end-session — the full extraction ritual

The most important wrench in the mechanic. When the user says "end session" / "save my work" / "wrap up", this fires the complete extraction → draft → approve → write → handoff flow. The point: every session's worth of learning lands in the vault so the next session picks up perfectly.

**Triggered by the user only.** Never auto-fires. (The orchestrator, when built in Phase 6, will trigger it programmatically on scope completion — that counts as the user's trigger by extension.)

---

## The 9-category extraction

Walk the session's history and pull out every instance of each category. Don't paraphrase — capture verbatim where possible, then rewrite into vault format.

| # | Category | Vault target | Format |
|---|---|---|---|
| 1 | **Decisions** | `Projects/<slug>/decisions.md` (appends) | Dated entry with reasoning, alternatives considered, confidence |
| 2 | **Preferences / defaults** | `Actions/<slug>.md` (creates or appends) | Rule + Why + How-to-apply (the feedback memory format) |
| 3 | **Errors + root-cause + fix** | `Projects/<slug>/errors.md` (appends) | what / cause / fix / prevention (all four required) |
| 4 | **Token-expensive approaches** | `Projects/<slug>/tokens.md` (appends) | expensive / cheaper / when-to-apply |
| 5 | **Project status changes** | `Projects/<slug>/status.md` (overwrites) | Live snapshot: phase, done, in-flight, blocked |
| 6 | **New skills found + integration** | `Mechanics/<mechanic>/state.md` (the mechanic-state axis — source of truth for what's already there) + vault catalog `index.md` | Per the Skill Law — every new skill earns a home |
| 7 | **Open loops** | `Projects/<slug>/open-loops.md` (appends) | Loop / waiting-on / unblocks / ETA |
| 8 | **Corrections** | `Actions/corrections-<date>.md` (creates) | What I did / what the user corrected / why / new default |
| 9 | **Next-session prompt** | `Projects/<slug>/next-prompt.md` (overwrites) | The exact prompt the user can paste into a fresh session to continue |

---

## The flow

### Step 1: Scan the session transcript

Walk the session chronologically. For each turn, mark which of the 9 categories apply. A single turn often hits multiple categories (a correction that becomes a preference, a decision that resolves an open loop).

### Step 2: Build the draft

Render every extracted item in vault format, but as a DRAFT — not yet written to disk. Show the user the full set, grouped by category. Format:

```markdown
## Draft extraction — session <id>

### 1. Decisions (3)

#### 2026-05-27 — Cut gstack family entirely
**Decision:** Cut gstack + gstack-upgrade + open-gstack-browser + setup-browser-cookies + pair-agent (5 skills, ~4000 lines).
**Reasoning:** Replaceable by Firecrawl + chrome-devtools-mcp + Playwright at lower token cost.
**Alternatives considered:** Keep gstack for stealth value (rejected — Firecrawl handles bot detection cheaper).
**Confidence:** stated (the user locked in this session)

[2 more decisions...]

### 2. Preferences / defaults (2)

#### Action: scraping-tier.md
[Full preference body — Firecrawl → Cloak → local drivers]

#### Action: gemini-no-code-files.md
[Full preference body — Gemini reads + analyses, never writes code]

### 3. Errors + root-cause + fix (1)

#### 2026-05-27 — Snapshot tar exit code 255 despite success
[what / cause / fix / prevention]

### 4. Token-expensive approaches (1)

#### 2026-05-27 — Skip gstack preamble when reading source skills
[expensive / cheaper / when-to-apply]

### 5. Project status changes

#### Projects/example-project/status.md (overwrite)
**Phase:** 3 (mechanic consolidation)
**Done:** Phase 0 snapshot (5.85 GB), Phase 1 autonomy kill, Phase 2 scaffold, Phase 3 router + second-brain mechanic SKILL files
**In flight:** Phase 3 wrenches for second-brain
**Blocked:** none

### 6. New skills found + integration

None this session.

### 7. Open loops (3)

- guard mechanic not yet built — unblocks: rest of Phase 3
- 10 on-demand mechanics still to build — unblocks: Phase 4
- Codex helper scripts for router state files (track_attempt.py, log_decision.py, preflight.py) — waiting on: Codex dispatch in Phase 5/6

### 8. Corrections (2)

#### Correction: Chrome extension as bot-detection default
**What I did:** Recommended Chrome extension + real cookies as the bot-detection scraping default.
**What the user corrected:** Should be Firecrawl default, Cloak Browser fallback, local drivers last resort.
**Why:** Token cost wins over capability flex.
**New default:** stored as Action/scraping-tier.md

#### Correction: Gemini routing for code rescue
**What I did:** Designed Codex twice-fails → Gemini multi-file rebuild fallback.
**What the user corrected:** Gemini doesn't write code files. Should be Codex twice-fails → diagnose / Sonnet re-spec → Codex retry.
**Why:** Gemini reads and analyses, doesn't author code artifacts.
**New default:** stored as Action/gemini-no-code-files.md

### 9. Next-session prompt

```
Pick up <project>. Last completed: <what landed last session>.
Next: <the immediate next task>.
Then: <subsequent tasks in order, with the one-line reasoning for the order>.
Plan: <path to the plan/spec doc, if any>.
Open loops: <carried-forward items that aren't blocking>.
Read first: <key files to load before acting>.
```
```

### Step 3: the user reviews

Present the draft. Ask: *"Approve, trim, or call out what's wrong?"* the user can:
- "agree all" → write everything
- Call out specific items to drop / edit
- "Trim 6 and 8 corrections — those are obvious, don't need vault entries"
- "Re-word decision 2"

Default vote on every item: write it. The user's bar should be "is this worth a node?", not "do I want to bother saving this?" — second-brain errs on the side of preservation.

### Step 4: Write to vault + harness

For approved items:
1. Write each item to its vault target (categories 1-8 above)
2. Mirror the relevant subset into the harness layer at `~/.claude/projects/<project-slug>/memory/`:
   - New preferences → `feedback_<slug>.md` + index entry in `MEMORY.md`
   - Status changes → `project_status.md`
   - Active error patterns → `error_<slug>.md` + index entry
3. Update `_system/second-brain/index.md` (the vault catalog) with one-line entries for any new top-level nodes
4. Append a one-line entry to `_system/second-brain/log.md` recording the session and what changed

### Step 5: Write the handoff file

At `Projects/<slug>/handoff-<date>.md`, write the handoff with:
- "For future Claude" preamble
- State at end of session
- Exact next prompt (verbatim from category 9)
- Open loops
- Links to any new vault nodes from this session

### Step 6: Confirm to the user

One sentence: *"Session saved. Wrote N nodes, handoff at <path>, next-prompt ready."* Don't enumerate. He can read the log if he wants details.

---

## What gets discarded (the user's rule)

Things that NEVER write to the vault, even if surfaced by extraction:

- **Raw code.** Source lives in source files, vault notes the DECISION about the code.
- **Trivia.** "the user ran ls" — no. "the user discovered the vault was 101MB" — yes, as a status.
- **Errors without fixes.** Half-fixed errors stay as open-loops, not error entries.
- **Junk nodes.** Things that aren't both human-readable AND AI-readable.
- **Routine tool calls.** Read, Edit, Bash invocations don't earn nodes. Decisions / observations from them might.

If a candidate item doesn't pass the bar, it doesn't go in the draft. The draft itself is already filtered.

---

## When the orchestrator triggers this

In Phase 6, the project-orchestrator gets hard completion logic: when scope is done, it auto-runs `summary → handoff file → end-session extraction → paste-next-prompt`. The orchestrator's trigger counts as the user's trigger by delegation.

The orchestrator still shows the DRAFT and waits for approval before writing — autonomy doesn't bypass the user's review on the final canonical write. The exception: if the user has set `orchestrator-auto-approve: true` as a standing preference in `Actions/`, the orchestrator auto-approves typical entries and only surfaces unusual ones.

---

## When the session token count is high

If the session is past ~500-600K tokens, run a token self-audit alongside the extraction:
1. Scan the session for token-expensive patterns (massive file reads, large agent dispatches, parallel fan-outs)
2. Note the cheaper paths
3. Add the entries to category 4 (token-expensive approaches)

Only run the self-audit when the session is genuinely large. Below 500K, skip it — the audit itself costs tokens, and on a small session it's net-negative.

---

## Helper scripts

After the draft is approved and written, end-session MAY call (opt-in, run-and-verify — not an automatic step):

| Script | What it does |
|---|---|
| `../scripts/vault-sync.py --direction both --commit` | Bidirectional sync vault ↔ Claude Code harness memory layer. Conflicts surface as failures (no silent overwrite). State persisted at `.vault-sync-state.json`. **Verify the first run by hand** — the documented auto-sync has not been exercised in practice (no `.vault-sync-state.json` on disk, no harness `feedback_*`/`project_status.md` mirrors despite many handoffs), so confirm output before trusting it. |
| `../scripts/vault-export.py --axis all --since <last-handoff-date>` | (optional) Export everything written this session as a portable bundle if the user wants to archive it externally. |

Both built in Phase 5 (spec: `PHASE_5_DISPATCH.md` § 1.1 + § 1.2, in `_archive/claude_projects_2026-05-pre-rebuild/Rebuild/`). Acceptance-tested 2026-05-28.

---

## See also

- [../SKILL.md](../SKILL.md) — the second-brain mechanic (the 9 categories defined there)
- [capture.md](capture.md) — mid-session quick writes (subset of what this wrench batches)
- [recall.md](recall.md) — reads the handoff files this wrench emits
- [learn.md](learn.md) — manages the accumulated learnings after multiple end-session passes
