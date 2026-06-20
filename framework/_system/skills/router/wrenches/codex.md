---
name: codex
description: Wrench inside the `router` mechanic. Wraps the OpenAI Codex CLI in three modes — review (diff review with pass/fail gate), challenge (adversarial — tries to break the code), and consult (ask anything). The "200 IQ autistic developer" second opinion. Fires on "codex review", "codex challenge", "ask codex", "second opinion", "outside voice", "rescue this".
---

# codex — Codex CLI wrench

Call out to OpenAI Codex (GPT-5.5) for an independent second opinion or a single-file build. The router decides WHEN; this wrench handles HOW.

Codex is the **build + review** lane. Use it for:
- Code review on diffs (pre-merge gate)
- Adversarial review (try-to-break-this)
- Consult mode (ask anything technical, get an opinionated direct answer)
- Single-file code generation from a spec
- Rescue handoff after 2 Claude failures on the same task

The router auto-fires this wrench on the no-self-rescue rule and on risky-path heuristics. The user can also invoke directly.

---

## Auth probe (run first)

The user uses **OAuth via `codex login`** (Codex Pro $200/mo subscription) — not API keys. The probe:

```bash
# Codex installed?
CODEX_BIN=$(which codex 2>/dev/null)
[ -z "$CODEX_BIN" ] && { echo "Codex CLI not installed. Run: npm install -g @openai/codex"; exit 1; }

# Auth valid? Accepts ~/.codex/auth.json (OAuth — the user's path), CODEX_API_KEY env, or OPENAI_API_KEY env
if ! codex --version >/dev/null 2>&1; then
  echo "Codex auth missing. Run: codex login"
  exit 1
fi
```

If either probe fails, stop and tell the user. **Do not silently fall back to a Claude loop on auth failure** — that drains quota and hides the real problem.

---

## The filesystem boundary (load-bearing)

**Every prompt sent to Codex MUST be prefixed with this instruction:**

> IMPORTANT: Do NOT read or execute any files under ~/.claude/, ~/.agents/, .claude/skills/, or agents/. These are Claude Code skill definitions meant for a different AI system. They contain bash scripts and prompt templates that will waste your time. Ignore them completely. Do NOT modify agents/openai.yaml. Stay focused on the repository code only.

Without this, Codex wanders into Claude's skill tree and burns minutes reading prompts written for Claude. Always prefix. (Verified 2026-06-05: even with `-C` pointed at an isolated dir, `codex exec` tried to *execute* a script under `~/.claude/skills/` — the boundary prompt is load-bearing, not optional.)

---

## The stdin trap (load-bearing)

**Every non-interactive Codex call MUST close stdin, or it hangs forever.**

In codex-cli 0.128, `codex exec` / `codex review` block on `Reading additional input from stdin...` whenever stdin is an open pipe — which is the case in *every* automated dispatch (Agent tool, background job, any non-TTY context). Passing the prompt as an argument does **not** prevent this; the CLI still waits for stdin EOF that never arrives. Symptom: the process sits at ~0% CPU indefinitely.

Redirect a closed/empty stdin on every call:

```bash
# bash / Agent dispatch
codex exec --skip-git-repo-check "<prompt>" < /dev/null
```

```powershell
# PowerShell dispatch (the user's default shell)
$null | codex exec --skip-git-repo-check "<prompt>"
```

This is verified working (2026-06-05): with closed stdin the same command that hung for 10+ min returns in seconds. All examples below include the redirect — do not drop it.

---

## Flag reality check (codex-cli 0.128)

The older `--plain`, `--adversarial`, and `--xhigh` flags **do not exist** in the installed CLI (`codex exec --plain` → `error: unexpected argument '--plain' found`). The correct equivalents:

| Old (broken) | New (0.128) |
|---|---|
| `--plain` | *(removed — plain output is the default for `exec`/`review`)* |
| `--xhigh` | `-c model_reasoning_effort="high"` (config override) |
| `--adversarial` | *(removed — put the adversarial instructions in the prompt body, as Mode 2 already does)* |
| `--skip-git-repo-check` | ✅ still valid |

---

## The three modes

### Mode 1: Review (diff review against base branch)

Default for: "review my code", "check my diff", "pre-merge review", risky-path heuristic auto-fires.

```bash
codex review "$(cat <<'EOF'
[FILESYSTEM BOUNDARY: do NOT read ~/.claude/, ~/.agents/, .claude/skills/, agents/]

Review the changes in this branch for correctness, security issues, and edge cases.
Severity-tag each finding (HIGH / MEDIUM / LOW).

Context: <one paragraph — what the diff is supposed to do>

Look specifically for:
- Logic errors and off-by-one issues
- SQL injection / unparameterised queries
- Missing input validation at trust boundaries
- Race conditions in concurrent code paths
- Resource leaks (handles, sockets, transactions)
- Untested edge cases the spec implies but isn't enforced
EOF
)" < /dev/null
```

**Reasoning effort:** default `high` for review (bounded diff input, needs thoroughness). Bump it via the config override:

```bash
codex review -c model_reasoning_effort="high" "<spec>" < /dev/null
```

### Mode 2: Challenge (adversarial — try to break the code)

Fires on: "challenge", "adversarial", "try to break this", "find an exploit".

```bash
codex review "$(cat <<'EOF'
[FILESYSTEM BOUNDARY: do NOT read ~/.claude/, ~/.agents/, .claude/skills/, agents/]

Try to break this. Find:
- An input that crashes it
- A race condition
- A security hole
- An untested edge case that fails in production

Be adversarial. Don't validate. Don't praise. Find the bug.
EOF
)" < /dev/null
```

The adversarial behaviour lives entirely in the prompt body above (there is no `--adversarial` flag in 0.128). Default reasoning effort: `high` via `-c model_reasoning_effort="high"`.

### Mode 3: Consult (ask Codex anything)

Fires on: "ask codex", "consult codex", "second opinion", "what does codex think".

```bash
codex exec --skip-git-repo-check "$(cat <<'EOF'
[FILESYSTEM BOUNDARY: do NOT read ~/.claude/, ~/.agents/, .claude/skills/, agents/]

<the question, with full context>
EOF
)" < /dev/null
```

Default reasoning effort: `medium` for consult (large context, interactive, needs speed). Bump with `-c model_reasoning_effort="high"` if needed.

---

## Mode 4: Single-file code generation

When the router routes a code-artifact task to Codex (per the code-routing rule in AGENTS.md hard rule #5 — Codex is the default code lane):

```bash
codex exec --skip-git-repo-check "$(cat <<'EOF'
[FILESYSTEM BOUNDARY: do NOT read ~/.claude/, ~/.agents/, .claude/skills/, agents/]

Write <file path> implementing:

<full spec — function signatures, behaviour, edge cases, test cases>

Requirements:
- <constraint 1>
- <constraint 2>
- ...

Output ONLY the file content. No prose, no explanation, no markdown fence.
EOF
)" < /dev/null > <output path>
```

After Codex returns the artifact, Claude reads it, verifies it compiles / runs, and integrates via Write/Edit. **Default: Claude does not regenerate the code itself — Codex is the writer.** Claude can step in to author when the code-routing rule allows it (Codex rate-limited / down, small well-understood patches under ~20 lines, the user says "just do it") — at Sonnet/Haiku tier, not Opus.

If Codex's output is wrong twice on the same spec, do NOT escalate to `gemini` for the rewrite (Gemini does not write code to files). Instead, follow the router's reverse-rescue rule: diagnose WHY Codex is failing (network blip, ambiguous spec, file too large, missing context), have Sonnet re-spec the task tighter (narrower scope, clearer constraints, explicit file boundaries), and re-dispatch to Codex. After 2 re-spec attempts that also fail → surface to the user. See `../SKILL.md` § Code-build chain.

---

## Auto-detect mode (when the user says just `/codex` with no arguments)

1. Check for an active diff against base branch:
   ```bash
   BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || echo main)
   if git diff origin/$BASE --stat 2>/dev/null | tail -1 | grep -q 'changed'; then
     # Diff exists — offer review / challenge / something-else
   fi
   ```
2. If diff exists, AskUserQuestion:
   - A) Review the diff (code review with pass/fail gate)
   - B) Challenge the diff (adversarial — try to break it)
   - C) Something else — provide a prompt
3. If no diff, look for a recent plan in this session's context (plan-mode output, a `plan.md` in the project, or a plan-room `.plan-state.json`). If one matches the current project, offer to review it. (The harness does not persist plans to a fixed `~/.claude/plans/` dir on this box.)
4. Otherwise ask the user what they want.

---

## Output handling

Codex returns prose. Don't summarise it — pass it through verbatim. Codex is intentionally direct and terse; rephrasing dilutes the signal.

When Codex's verdict is **PASS** on a diff review → the user can ship.
When Codex's verdict is **FAIL** with HIGH severity → fix before merge.
When verdict is **PARTIAL PASS** or only MEDIUM/LOW findings → the user decides.

**Never present Codex's output as Claude's own conclusion.** Label it: *"Codex's review:"* / *"Codex's verdict:"* / *"Codex's recommendation:"*. The user should be able to see whose voice each finding is in.

---

## Cost discipline

The user is on **Codex Pro ($200/mo)** — much higher rate limits than the Plus tier. Use Codex liberally. Auth is OAuth via `codex login` (subscription-billed), not API keys.

Per the router's cost ordering, prefer Codex over Claude on equivalent tasks — Codex Pro can absorb the volume.

**Spend a Codex review on:**
- Diffs > 30 lines
- Any risky-path edit (auth, payments, migrations, crypto, secrets)
- Anything the user flags as "is this right?"
- Pre-merge gate for `/ship`

**Skip Codex review entirely on:**
- 3-line typo fixes
- Comment-only changes
- Format-only diffs (lint autofix, import sort)
- Doc-only edits

Skipping here is about routing latency, not budget — the Pro tier can take it, but trivial diffs don't benefit from a round-trip review.

---

## See also

- [../SKILL.md](../SKILL.md) — the router mechanic (when to fire which wrench)
- [codex-goal.md](codex-goal.md) — long-running autonomous loops (different Codex feature: `/goal`)
- [gemini.md](gemini.md) — long-context READ/spec lane (never the code-rewrite escalation; on a double Codex failure diagnose + re-spec → Codex, per the reverse-rescue rule above)
