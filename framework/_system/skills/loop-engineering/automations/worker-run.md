# Worker loop — run instructions (editable brain)

This file is the editable logic for the `loop-engineering-issue-to-pr` Codex Automation.
The automation's registered prompt is a thin pointer that runs `preflight.py` then reads and
follows THIS file. Edit this file to change scope/behaviour — no need to touch the automation.

You are running the ISSUE-TO-PR worker job across MULTIPLE repositories, one bounded pass.
Pick at most ONE issue total (across all target repos), open at most one DRAFT PR, then STOP.

**THE RUN REPORT IS MANDATORY AND IS NOT THE LAST STEP — IT IS THE FIRST.** Before selecting an
issue, your very first action is to create the run-report file (see "Run report + spend" below) with
a `STARTED` stub, then append to / finalize it as you go. A run that opens a PR but leaves no report
file on disk is a FAILED run. Past runs skipped this trailing step; writing the stub first removes
that failure mode.

## Tooling / credits
- Codex Pro subscription only. Never metered OpenAI API credits.
- Drive GitHub only through `gh` authenticated as <your-github>. Never the Codex GitHub connector or Khaphora.
- Verify with `gh auth status`; if the active account is not <your-github>, stop and report.
- On any `gh` rate-limit / secondary-limit / HTTP-403-rate response: sleep ~60s and retry (up to 3×)
  rather than aborting; if still limited, skip that sub-step, note it in the report, and continue.

## Target repositories (auto-discovered each run)
- All public repos owned by <your-github>:
  `gh repo list <your-github> --visibility public --limit 100 --json nameWithOwner --jq ".[].nameWithOwner"`
- ALWAYS also include `<your-github>/agentic-os-97` (private pilot).
- New public repos picked up automatically. If enumeration fails, stop and report.

## Selection — one issue across ALL target repos
Across all target repos, find open issues that have BOTH `risk:low` and `agent:ready`, do NOT already
have an open linked PR, and do NOT have `needs:human` / `agent:blocked` / `risk:medium` / `risk:high`.
From the combined pool, pick the single OLDEST eligible issue by created_at — exactly ONE, regardless of repo.
If none eligible anywhere, report that and record spend.

Before coding, inspect the issue body, comments, labels, linked PR evidence, and its `## Agent Assessment`.
If unclear / unsafe / too broad / needs judgment / unverifiable: do NOT code — comment the specific blocker,
add `needs:human`, record spend, STOP.

## Inner loop (for the selected issue's repo = TARGET)
Use TARGET's default branch from `gh repo view TARGET --json defaultBranchRef` (do not assume main).
Repo path: use `C:\Users\<you>\Desktop\AI_Projects\projects\agentic_os_97` if TARGET is agentic-os-97 and it
exists; otherwise clone TARGET into a temp work area.

1. Read the issue, write a short implementation plan before editing.
2. Create a traceable branch + isolated worktree from the default branch.
3. Make the smallest complete fix that satisfies the issue.
4. Run available checks discovered from the repo (pnpm typecheck/test/build, npm/yarn, pytest, existing scripts).
   Do not invent unavailable checks.
5. Run a SEPARATE checker pass on the diff with a new Codex process (`codex exec` review prompt). Maker != checker.
6. Fix valid in-scope reviewer findings, rerun checks.
7. Open a DRAFT PR with `gh pr create --draft` against TARGET.
8. Link the issue in the PR body; include plan, acceptance criteria, verification output, reviewer result.
9. STOP before merge. Never merge.

Branch/PR rules: one issue -> one branch -> one draft PR · never push to default branch · never force-push ·
if TARGET is public, obey the guard public-push gate before push/PR (if it blocks, stop and report; private repos
skip the gate) · no forks or non-<your-github> namespaces.

## Run report + spend
**SAVE THE RUN REPORT — write it FIRST as a stub, finalize it LAST. Never skip it.**

The report file is `C:\Users\<you>\Desktop\AI_Projects\_system\automations\runs\issue-to-pr\<UTC-timestamp>.md`
where `<UTC-timestamp>` is the current time formatted `YYYY-MM-DDTHHmmZ` (create the `issue-to-pr`
folder if missing).

1. **At the very start of the run** (before selection), write this file with a `STARTED` stub —
   a header line plus `status: started` and the UTC start time. This guarantees a report exists on
   disk even if a later step aborts, and proves write access early.
2. **As the run proceeds**, finalize it into the full report: which repo + issue was selected (or that
   none were eligible), the plan, checks run, reviewer result, the draft PR link (if any), blockers,
   and a final `status: completed` / `status: no-op` / `status: blocked` line.
3. Always leave a finalized file — even on a no-op run write a short note saying so.

Then record spend:
`python C:\Users\<you>\Desktop\AI_Projects\_system\automations\record_spend.py C:\Users\<you>\Desktop\AI_Projects\_system\automations issue-to-pr <tokens> ok`
(actual token count if exposed, else estimate 300000). Then STOP.
