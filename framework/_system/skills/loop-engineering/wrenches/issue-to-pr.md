---
name: loop-engineering-issue-to-pr
description: The worker loop. Codex picks ONE GitHub issue labelled risk:low + agent:ready, plans it, makes the smallest complete change in an isolated worktree, runs checks, has a SEPARATE Codex pass review the diff (maker != checker), opens a DRAFT PR, links the issue, and stops before merge. Never merges. Trigger phrases include "issue to PR loop", "run the worker loop", "turn the ticket into a PR", "work the agent-ready queue".
---

# issue-to-pr — the worker loop (inner loop)

Codex pulls one ready ticket off the queue and turns it into a **draft pull request**. One issue,
one thread, one branch, one worktree — so a failure stays disposable. Full upstream prompt is
vendored at `../vendor/issue-to-pr-loop.md`.

**Lane:** Codex. **Pilot repo:** `<your-github>/agentic-os-97`. **Base branch:** `main` (confirm).

## Budget contract (every scheduled run)

1. `python _system/automations/preflight.py` → if exit ≠ 0, STOP. Do nothing.
2. Run the worker job below.
3. `python _system/automations/record_spend.py <automations-dir> issue-to-pr <tokens> <status>`.

## Selection

Pick the **oldest** open issue carrying BOTH `risk:low` AND `agent:ready`. **Skip** anything with
`needs:human`, `risk:medium`, `risk:high`, or a pre-existing `agent:blocked`. (We never create
`agent:blocked` ourselves — completion/blocked state lives in GitHub issue/PR state.)

## The inner loop (one ticket)

```
1.  Read the issue body, comments, and its Agent Assessment.
2.  Write a short implementation plan before editing code.
3.  Create a traceable branch/worktree from the base branch.
4.  Make the smallest complete change that satisfies the issue.
5.  Run the relevant tests / lint / typecheck / build.
6.  Have a SEPARATE Codex reviewer pass review the diff against the ticket (maker != checker).
7.  Fix valid, in-scope review findings; re-run checks.
8.  Open a DRAFT pull request.
9.  Link the issue in the PR body.
10. Include the plan, acceptance criteria, verification output, and reviewer result in the PR body.
11. Move the issue to "review" if the tracker supports status.
12. STOP before merge.
```

The review step is load-bearing: the model that wrote the code is too kind to it. Maker and
checker are different agents; the final approver is **the user**.

## If the issue is unclear / unsafe / too broad / unverifiable

Do **not** code. Comment on the issue with the specific blocker and what human input is needed,
add `needs:human`, and report. (Honor a repo's pre-existing `agent:blocked` convention if present.)

## Guardrails

- **Draft PRs only. Never merge.** the user owns every merge — that's the system's speed governor.
- Public repo → the branch push / PR **passes the guard public-push gate** (gitleaks + denylist,
  fail-closed). Never bypass it. If the gate blocks, stop and report.
- One issue → one branch → one draft PR → one human review. Stay linear until proven.

## Ready-to-run prompt (dispatch to Codex)

```text
$codex-run-loop

Repository: <your-github>/agentic-os-97
Repository path: <local path>
Base branch: main

Find one open GitHub issue with BOTH labels: risk:low, agent:ready.
Skip issues with any of: needs:human, agent:blocked, risk:medium, risk:high.
Select the oldest eligible issue unless there's a clear reason to choose another.

For the selected issue, run the 12-step inner loop: read → plan → worktree → smallest complete
change → run checks → separate reviewer pass (maker != checker) → fix valid findings → open a
DRAFT PR → link the issue → include plan/acceptance/verification/reviewer result in the body →
move to review → STOP before merge.

If the issue is unclear, unsafe, too broad, or unverifiable: do not code. Comment the blocker,
add needs:human, report what's needed.
```

## Parallel variant (only after the linear loop is proven)

Find up to three independent `risk:low`+`agent:ready` issues; one worktree + branch + draft PR
each; only run in parallel when each is independently reviewable, mergeable, and revertible.
Stop before merge. Respect the workflow batch-throttle default.

## See also

`../SKILL.md` · `backlog-manager.md` · `../automations/worker-automation.md` · `../reference/job-card.md`
