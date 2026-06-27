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

### Scanning repo content for ticket evidence — use a LOCAL CLONE, never the code-search API
The GitHub code-search API (`gh search code` / the `/search/code` endpoint) is rate-limited to
~10 req/min and chokes across multiple repos, cutting the sweep short. Do NOT use it to find ticket
evidence. The repo's file contents are identical whether fetched via API or cloned — so grep them
locally, which has no rate limit:
- For `agentic-os-97`, reuse the existing clone at
  `C:\Users\<you>\Desktop\AI_Projects\projects\agentic_os_97` if present (fetch + checkout its
  default branch first so it is current). For every OTHER target repo, shallow-clone its default
  branch into a temp work area, e.g. `gh repo clone <repo> <tmp> -- --depth 1`, then remove the temp
  clone when the per-repo scan is done.
- Gather evidence with local `git grep` over the checked-out working tree — bounded TODO/FIXME,
  skipped tests (`describe.skip` / `it.skip` / `xit` / `test.skip` / `@pytest.mark.skip`), stale
  setup commands, broken relative doc links, simple config drift. Read surrounding file context from
  the local checkout. Grep is free, so scan thoroughly rather than rationing requests.

Keep using `gh` (the REST issues API, well under its 5,000 req/hr authenticated limit) for everything
issue-side — reading issues, labels, comments, creating tickets, and the board sync below — and for
CI status (`recent failed CI on default branch`), which is GitHub-side state with no local
equivalent. Only the code-CONTENT search moves local; issue/label/board/CI operations stay on `gh`.

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
