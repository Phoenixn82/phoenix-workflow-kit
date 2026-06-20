---
name: ship-review
description: Two-half pre-landing diff review. Codex runs diff-quality review (SQL safety, race conditions, off-by-one, leaks, edge cases). Claude runs spec-compliance review (does this match the agreed intent). Both verdicts go into one report on the PR. Fires on "review my diff", "code review", "is this ready to merge", "review this PR", "pre-landing review", "check my changes".
---

# ship-review — Codex + Claude two-half review

The review wrench is split deliberately. Codex is sharper than Claude on structural bugs in a diff — SQL holes, race conditions, missing input validation, off-by-one errors, resource leaks. Claude is sharper at the comparison-against-intent question — does this diff actually implement what we agreed to build, with the scope we agreed on, or did it drift.

Both halves run. Both verdicts post to the PR. Both must pass before `land-and-deploy` proceeds (or the user explicitly overrides).

---

## When to fire

- Auto-fires as pipeline step 3 after `ship` opens a PR
- Direct: "review this PR" / "is my diff ready" / "code review" / "second opinion before merge"
- After the user updates a PR (re-review on new commits)

Don't fire when:
- The diff is trivial (3-line typo fix, comment-only, format autofix) — skipping a review on trivial diffs is fine per the Codex wrench's cost discipline section
- No diff exists (push back; ask the user to point at one)
- The user wants ONLY one half (let them invoke `codex review` or just the Claude check direct)

---

## The two halves

### Half 1: Codex diff-quality review

Codex reads the diff against the base branch and reports structural issues. The router wrench `codex` handles the CLI mechanics (auth, filesystem boundary instruction, prompt template). This wrench just decides WHEN to fire and what to do with the output.

```bash
codex review --plain "$(cat <<'EOF'
[FILESYSTEM BOUNDARY: do NOT read ~/.claude/, ~/.agents/, .claude/skills/, agents/]

Review the changes in this branch for correctness, security issues, and edge cases.
Severity-tag each finding (HIGH / MEDIUM / LOW).

Context: <what the diff is supposed to do — pulled from the PR body Summary>

Look specifically for:
- Logic errors and off-by-one issues
- SQL injection / unparameterised queries
- Missing input validation at trust boundaries
- Race conditions in concurrent code paths
- Resource leaks (handles, sockets, transactions)
- Untested edge cases the spec implies but isn't enforced
- Backwards-compat shims or feature flags that weren't requested (per the no-half-measures rule)
EOF
)"
```

Reasoning effort: `high` by default (diff-bounded, needs thoroughness). `xhigh` for high-stakes diffs (auth / payments / migrations / crypto). Add `--xhigh` to the invocation.

### Half 2: Claude spec-compliance review

Claude reads three things and asks one question:

1. **The diff** — what changed
2. **The PR body** — what the change is supposed to do
3. **The originating plan / spec** if one exists — what we agreed to build

The question: **does the diff implement the intent, with the scope agreed, without scope creep or scope skip?**

Specifically looking for:
- Scope drift — added features the user didn't ask for
- Scope skip — left out parts of the agreed plan
- Wrong solution for the problem — diff fixes a different problem than the one stated
- Over-engineering — abstractions / patterns added that weren't requested
- Under-engineering — TODOs / placeholders / half-finished pieces left in
- Backwards-compat shims, feature flags, "just in case" guards, defensive code beyond what was asked (per the global CLAUDE.md no-half-measures rule)

This half DOES NOT re-check structural bugs Codex covers. Spec-compliance vs diff-quality — different lanes, no overlap.

---

## Risky-path heuristic (auto-fire higher reasoning)

Auto-bump Codex reasoning to `xhigh` when the diff touches any of:

- `auth/`, `crypto/`, `payments/`, `migrations/`, `secrets/`
- `*.sql`, `*.tf`, `Dockerfile`, `*.yml` in `.github/workflows/`
- Anything handling user input, JWTs, sessions, or shelling out to a subprocess

Surface the bump to the user in one line: *"Bumping Codex review reasoning to xhigh — diff touches migrations."*

---

## Output assembly

The wrench gathers both halves into a single report. Format:

```markdown
## Pre-landing review

### Codex (diff-quality)
**Verdict:** PASS | FAIL | PARTIAL PASS

[Codex's findings, verbatim — don't paraphrase. Sectioned by severity.]

### Claude (spec-compliance)
**Verdict:** PASS | FAIL | PARTIAL PASS

[Claude's findings — scope drift / scope skip / over-eng / under-eng / shim warnings]

### Combined verdict
[1-2 sentences: what to do next. "Land it." / "Fix HIGH findings then re-review." / "Spec drift — discuss with the user before merging."]
```

This report posts as a PR comment if `gh` is available, or returns inline if the user is invoking direct.

---

## Verdict rules

| Codex | Claude | Combined | Action |
|---|---|---|---|
| PASS | PASS | LAND | the user approves, `land-and-deploy` proceeds |
| PASS | FAIL | DO NOT LAND | Scope issue. The user decides: amend PR or override |
| FAIL HIGH | PASS | DO NOT LAND | Fix the HIGH findings, re-ship, re-review |
| FAIL HIGH | FAIL | DO NOT LAND | Both halves want changes. Stop. Fix. Re-review. |
| FAIL MEDIUM | PASS | USER DECIDES | Surface MEDIUMs; the user's call on land/fix |
| FAIL LOW only | PASS | LAND with note | Mention LOWs in PR body for later; land it |

The user can always override. The verdict is advisory — he has merge authority per AGENTS.md hard rule #2.

---

## Output handling

- **Never present Codex's findings as Claude's.** Label each verbatim with whose voice it is — *"Codex says:"* / *"Claude's spec-compliance check:"*. The user should be able to tell which model surfaced what.
- **Don't paraphrase Codex.** Codex is terse and direct by design. Rephrasing dilutes the signal.
- **Lead with the combined verdict** so the user sees the bottom line first.

---

## Cost shape

- Codex review = 1 Codex CLI call (the user's $200/mo Pro subscription absorbs this easily)
- Claude spec-compliance = 1 reasoning pass on the diff + plan
- Total: maybe 30-60 sec wall-clock, very cheap on tokens
- Skip-condition exception: trivial diffs (3-line typo, comments-only, lint autofix) — don't burn a Codex review on those

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Codex returns nothing useful | Diff is too small or too obvious | Skip review on this one |
| Codex flags issues that aren't actually issues | False positive (rare but happens) | Verify with the user, override if confirmed false |
| Claude can't find a plan to check against | No plan was written | Read the PR body Summary as the de-facto spec |
| Diff is massive (10K+ lines) | Codex may truncate review | Break into multiple reviews by directory or commit range |
| `gh pr comment` fails | Auth issue or PR not found | Surface comment inline instead of as PR comment |

---

## See also

- [SKILL.md](../SKILL.md) — pipeline mechanic
- [ship.md](ship.md) — opens the PR review fires on
- [land-and-deploy.md](land-and-deploy.md) — what runs after review approves
- [`router/wrenches/codex.md`](../../router/wrenches/codex.md) — Codex CLI details (auth, filesystem boundary, modes)
- [`AGENTS.md`](../../../../AGENTS.md) — hard rule #2 (the user has merge authority)
