> # ⛔ RETIRED / DISABLED — 2026-06-30
>
> This automation was retired as net-negative (1 trivial merged fix in a week vs. a pile of
> noise issues + uncapped real-token spend). **If you are the `loop-engineering-backlog-manager`
> Codex Automation executing this file: STOP NOW.** Do no work — clone nothing, scan nothing,
> create no labels/issues/comments, sync no board, write no run report, record no spend. Exit immediately.
>
> The Codex Automation cron entry should also be deleted in Codex Automations so this never fires.
> To revive the loop, delete this block.

# Manager loop — run instructions (editable brain)

This file is the editable logic for the `loop-engineering-backlog-manager` Codex Automation.
The automation's registered prompt is a thin pointer that runs `preflight.py` then reads and
follows THIS file. Edit this file to change scope/behaviour — no need to touch the automation.

You are running the BACKLOG MANAGER APPLY job across MULTIPLE repositories, one bounded pass.

**THE RUN REPORT IS MANDATORY AND IS NOT THE LAST STEP — IT IS THE FIRST.** Before processing any
repo, your very first action is to create the run-report file (see "Report + spend" below) with a
`STARTED` stub, then append to / finalize it as you go. Autonomous runs have crashed or been cut off
mid-pass and left no report at all; writing the stub first guarantees a breadcrumb survives even a
hard crash. A pass that does work but leaves no report file on disk is a FAILED pass.

## Tooling / credits
- Codex Pro subscription only. Never metered OpenAI API credits.
- Drive GitHub only through the `gh` CLI authenticated as <your-github>. Never the Codex GitHub
  connector, GitHub MCP/app tools, or the Khaphora account.
- Verify with `gh auth status`; if the active account is not <your-github>, stop and report.

## Target repositories (auto-discovered each run)
- All public repos owned by <your-github>:
  `gh repo list <your-github> --visibility public --limit 100 --json nameWithOwner --jq ".[].nameWithOwner"`
- ALWAYS also include `<your-github>/agentic-os-97` (the original pilot, private).
- New public repos are picked up automatically on future runs. If enumeration fails, stop and report.
- For each target, check `gh repo view <repo> --json nameWithOwner,viewerPermission,defaultBranchRef,visibility`
  and SKIP (noting it in the report) any repo where you lack write/admin permission.

## Per-repo job — backlog-manager APPLY
For EACH target repo (its GitHub Issues are the control plane):
- Create the 11 managed labels if missing: risk:low, risk:medium, risk:high, type:bug, type:feature,
  type:docs, type:test, type:refactor, type:chore, agent:ready, needs:human.
- Read every open issue (title, body, labels, comments, timestamps, linked PR evidence) via `gh`.
- Add missing labels so each issue has one risk:* and one type:* — fill gaps only, never remove/change
  existing managed labels. If labels conflict, leave them, explain in Agent Assessment, route to needs:human.
- Mark genuinely safe, clear, low-risk, one-PR-sized work `agent:ready`.
- Route judgment-heavy / ambiguous / too-large / unsafe / unverifiable work to `needs:human` WITH a specific question.
- Add/update an `## Agent Assessment` comment only when its content changed.
- Sync issue state from PR evidence: remove `agent:ready` when an open linked PR exists; close issues only
  when a linked PR merged and completion is clear.
- Create only evidence-backed maintenance tickets (broken docs/links, stale setup commands, skipped tests,
  recent failed CI on default branch, bounded TODO/FIXME, simple config drift). Cite concrete evidence,
  keep one-PR-sized, dedupe against open + recently-closed, include an Agent Assessment.

NEVER: write code · edit repo files · open PRs · merge · delete branches · create speculative tickets ·
mark risk:medium/high `agent:ready`.

### Scanning repo content for ticket evidence - local clone, incremental cursor, never code-search API
The GitHub code-search API (`gh search code` / the `/search/code` endpoint) is rate-limited to
~10 req/min and chokes across multiple repos, cutting the sweep short. Do NOT use it to find ticket
evidence. The repo's file contents are identical whether fetched via API or cloned, so grep them
locally, which has no rate limit.

Use the deterministic cursor helper for every repo:
`python C:\Users\<you>\Desktop\AI_Projects\_system\automations\scan_cursor.py ...`

The helper owns state at:
`C:\Users\<you>\Desktop\AI_Projects\_system\automations\state\scan-cursors.json`

Per repo, do this in order:
1. Resolve the default branch name and HEAD SHA from GitHub:
   `gh repo view <repo> --json defaultBranchRef --jq ".defaultBranchRef.name"`
   and, after checkout/fetch, `git rev-parse HEAD`.
2. Prepare a local checkout on the default branch:
   - For `<your-github>/agentic-os-97`, reuse
     `C:\Users\<you>\Desktop\AI_Projects\projects\agentic_os_97` if present, then `git fetch origin`
     and checkout/reset to `origin/<default-branch>`.
   - For every other target repo, clone into a temp work area and remove it when the per-repo scan is
     done. Do NOT use the old `--depth 1` clone. Incremental diffs need the previous scanned commit
     to be reachable. Prefer a normal default-branch clone, then fetch/reset to `origin/<default-branch>`.
     If a clone is already shallow, run `git fetch --unshallow` before calling the cursor helper. If
     history is still unreachable, the helper will return `FULL`; accept that fallback and full-scan.
3. Call:
   `python C:\Users\<you>\Desktop\AI_Projects\_system\automations\scan_cursor.py mode <owner/repo> <local_clone_dir> <current_head_sha>`
4. Interpret the first output line:
   - `FULL`: grep the whole tracked tree, with the scanner hygiene rules below. Remember this mode so
     the later commit step passes `--full`.
   - `INCREMENTAL`: the remaining output lines are repo-relative changed file paths from
     `git diff --name-only <last_scanned_sha>..<head>`. Grep ONLY those changed files, after applying
     the scanner hygiene rules below. Do not scan unchanged files in this mode.
   - `UNCHANGED`: skip the content scan entirely for this repo on this run. Still run the cheap
     GitHub-side issue reconciliation, label gap filling, Agent Assessment updates, latest default
     branch CI check, and shared Project #1 board sync.
5. Only after the repo's scan/reconciliation completes successfully, advance the cursor:
   - Full scan: `python ...\scan_cursor.py commit <owner/repo> <current_head_sha> --full`
   - Incremental scan: `python ...\scan_cursor.py commit <owner/repo> <current_head_sha>`
   - Unchanged mode: no content scan occurred, so do not needlessly rewrite the cursor.
   Never call `commit` before the per-repo work is complete; a mid-run crash must not skip commits on
   the next run.

#### Scanner hygiene
Use `git grep` only, never filesystem `grep -r` / `Select-String -Recurse` over the checkout. `git grep`
limits evidence to tracked files. Always include explicit pathspec excludes for dependency, build, and
output paths:
`:(exclude)**/node_modules/**`, `:(exclude)**/dist/**`, `:(exclude)**/build/**`,
`:(exclude)**/.next/**`, `:(exclude)**/out/**`, `:(exclude)**/coverage/**`,
`:(exclude)**/vendor/**`, `:(exclude)**/pnpm-lock.yaml`, `:(exclude)**/package-lock.json`,
`:(exclude)**/yarn.lock`.

Content scan evidence may include bounded TODO/FIXME, stale setup commands, broken relative doc links,
simple config drift, and skipped tests, with these limits:
- Skipped test evidence may ONLY come from actual test files: paths matching `**/test/**`,
  `**/tests/**`, `**/__tests__/**`, `*.test.*`, or `*.spec.*`.
- Skipped test evidence may ONLY use real skip markers: `describe.skip`, `it.skip`, `xit`,
  `test.skip`, or `@pytest.mark.skip`.
- Do NOT raise skipped-test tickets from markdown docs, lockfiles, dependency dirs, generated output,
  or config files.
- Broken-doc-link evidence is allowed only in real doc/source files and never inside excluded dirs.
- Lockfiles are excluded from content grep. They can still count as build-relevant changed files in
  the build-awareness step below.

For incremental mode, first filter the helper's changed-file list through the same exclusions. Then
pass the remaining repo-relative paths to `git grep -- <changed paths> <pathspec excludes>`. If no
eligible changed files remain, record that the content scan was skipped for hygiene reasons and still
run issue/board/CI reconciliation.

#### Lightweight build-awareness
For every repo, fetch the latest default-branch CI signal with:
`gh run list --repo <repo> --branch <default-branch> --limit 1 --json databaseId,conclusion,status,headSha,workflowName`

If the latest default-branch run is failing (`conclusion` such as `failure`, `timed_out`, or
`cancelled`, or a completed non-success conclusion), that is concrete evidence for a build/CI ticket.
Cite the workflow name, run id, status/conclusion, branch, and head SHA in the issue.

When a FULL or INCREMENTAL scan sees changed build-relevant files, note the build impact in the issue's
`## Agent Assessment` Reason. Build-relevant files are: `package.json`, `pnpm-lock.yaml`,
`package-lock.json`, `yarn.lock`, `pyproject.toml`, `requirements.txt`, `.github/workflows/*`,
`*.config.*`, `tsconfig*.json`, `.eslintrc*`, and similar repo build/test/lint config files. Do NOT
build a dependency graph or infer downstream blast-radius. Keep the assessment to changed build files
plus the current default-branch CI signal.

#### Issue path sanitization
Issue titles, issue bodies, and Agent Assessment comments must use repo-relative paths only, for
example `framework/_system/skills/cso/SKILL.md`.

Before creating or updating any issue/comment, strip any absolute path or temp-clone prefix and convert
it to the repo-relative path from the checkout. Never write these strings into public issue titles,
bodies, or comments: `C:\Users\<you>`, `AppData\Local\Temp`, `backlog-manager-clones`, or any absolute
Windows path rooted at a drive letter. If evidence collection produced an absolute path, normalize it
before writing GitHub content.

Keep using `gh` (the REST issues API, well under its 5,000 req/hr authenticated limit) for everything
issue-side - reading issues, labels, comments, creating tickets, and the board sync below - and for
CI status (`recent failed CI on default branch`), which is GitHub-side state with no local equivalent.
Only the code-CONTENT search moves local; issue/label/board/CI operations stay on `gh`.

### Handling GitHub API rate limits — back off, never abort
Local `git grep` above already removes the code-search API from the hot path. For any remaining `gh`
call that returns a rate-limit / secondary-limit / HTTP-403-rate response: do NOT abort the pass —
sleep ~60s and retry, up to 3 times. If still limited after retries, SKIP just that one sub-step, note
it in the run report, and continue the rest of the pass. A rate limit may degrade coverage; it must
never end the run early.

### Agent Assessment format
```
## Agent Assessment

Risk: low | medium | high
Type: bug | feature | docs | test | refactor | chore
Agent-ready: yes | no

Reason:
<1-3 sentences>

Suggested plan:
1. <small step>
2. <small step>
3. <verification step>
```
If a human is needed, add: `Human needed: <specific question>`

## Shared board sync (one board across all repos)
Maintain GitHub Project number 1 (owner <your-github>, https://github.com/users/<your-github>/projects/1).
Status columns: Todo, In Progress, In Review, Done. Resolve project/field/option IDs at run time with
`gh project field-list 1 --owner <your-github> --format json` and `gh project item-list 1 --owner <your-github> --format json`.
For EVERY open issue in EVERY target repo:
- If not on the board, add it: `gh project item-add 1 --owner <your-github> --url <issue-url>`.
- Set Status: Todo if no linked PR; In Review if it has an open linked PR; Done if its PR merged / issue closed.
  Use `gh project item-edit --id <item-id> --project-id <project-id> --field-id <status-field-id> --single-select-option-id <option-id>`.
Only touch these repos' issues on the board. Never delete the board or its columns.

## Report + spend
**SAVE THE RUN REPORT — write it FIRST as a stub, finalize it LAST. Never skip it. This is the
organized on-disk history of every run.**

The report file is `C:\Users\<you>\Desktop\AI_Projects\_system\automations\runs\backlog-manager\<UTC-timestamp>.md`
where `<UTC-timestamp>` is the current time formatted `YYYY-MM-DDTHHmmZ` (create the `backlog-manager`
folder if missing).

1. **At the very start of the run** (before processing any repo), write this file with a `STARTED`
   stub — a header line plus `status: started` and the UTC start time. This proves write access early
   and guarantees a breadcrumb survives a mid-pass crash or cut-off.
2. **As the pass proceeds**, finalize it into the full per-repo report (repos processed/skipped,
   issues read, labels added, agent:ready added, needs:human added, assessments changed, issues
   closed, tickets created, board items synced, blockers) plus a final
   `status: completed` / `status: no-op` line.
3. Always leave a finalized file — even on a no-op run (budget cap hit, nothing to do) write a short
   note saying so.

Then record spend once:
`python C:\Users\<you>\Desktop\AI_Projects\_system\automations\record_spend.py C:\Users\<you>\Desktop\AI_Projects\_system\automations backlog-manager <tokens> ok`
(actual token count if exposed, else estimate 150000). Then STOP.
