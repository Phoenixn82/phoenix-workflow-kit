---
name: loop-engineering-backlog-manager
description: The manager loop. Codex reviews a GitHub backlog via `gh`, classifies issues by risk/type, marks safe low-risk work `agent:ready`, routes judgment calls to `needs:human`, writes Agent Assessment comments, syncs issue state from merged-PR evidence, and files evidence-backed maintenance tickets. Dry-run by default; never writes code. Trigger phrases include "backlog manager", "triage the backlog", "run the manager loop", "classify the backlog", "label the issues".
---

# backlog-manager — the manager loop (outer loop)

Codex acts as a lightweight engineering manager for the backlog: keep work clear, classified,
and safe to route to humans or agents. **This wrench labels and assesses — it never implements.**
Full upstream spec is vendored at `../vendor/backlog-manager-SKILL.md`.

**Lane:** Codex (via `gh`). **Default mode:** `dry-run`. **Pilot repo:** `<your-github>/agentic-os-97`.

## Budget contract (every scheduled run)

1. `python _system/automations/preflight.py` → if exit ≠ 0 (budget reached or `HALT`), STOP. Do nothing.
2. Run the manager job below.
3. `python _system/automations/record_spend.py <automations-dir> backlog-manager <tokens> <status>`.

## The three phases (run the whole loop each time)

1. **Triage** — read `AGENTS.md`/`CLAUDE.md`/README for project policy, then fetch open issues
   with title, body, labels, comments, status, and linked PRs.
2. **Prepare the queue** — classify each issue (`risk:*` + `type:*`), mark safe work `agent:ready`,
   route judgment-heavy work to `needs:human` with a *specific question*, add/update Agent Assessments.
3. **Maintain + report** — sync clearly completed issues from merged-PR evidence, sweep the repo
   for evidence-backed drift and file tickets, report branch-cleanup candidates, verify, summarize.

## Classification rules

Mark `agent:ready` only when ALL hold: `risk:low`, scope is clear, one-PR-sized, expected output
clear, verification known, no product/UX/architecture/security/data/billing/auth/deploy judgment,
not already linked to active work.

Mark `needs:human` when ANY hold: ambiguous requirements, unclear expected behavior, missing repro
for a real bug, too large for one PR, needs judgment, can't classify with confidence, a prior agent
attempt failed.

Never mark `risk:medium`/`risk:high` as `agent:ready`. Classification only **fills gaps** — never
remove or change an existing managed label; if you disagree, keep it and note it in the report.

## Agent Assessment (comment on each classified issue, only when it changed)

```md
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
If a human is needed, add a `Human needed: <specific question>` line.

## Filing tickets (the "auto agents create tickets" behavior)

On the repo sweep, look for **evidence-backed** problems only: stale docs, broken local links,
README/setup commands that don't exist, skipped tests, recent failed CI on the default branch,
bounded TODO/FIXME, simple config drift. Do NOT file vague improvements, speculative refactors,
architecture rewrites, or anything needing business/security/data judgment. Deduplicate against
open + recently-closed issues. Every agent-created issue includes evidence (paths/commands/links),
why it matters, a small suggested fix, and an Agent Assessment.

## Ready-to-run prompts (dispatch to Codex)

### Dry-run (default — change nothing)

```text
$backlog-manager dry-run GitHub backlog for <your-github>/agentic-os-97

Repository path: <local path to agentic-os-97 if available>

Review the repository and issue tracker. Do NOT mutate GitHub in dry-run mode.

Report:
- labels that are missing
- open issues needing risk labels / type labels
- issues that should be agent:ready (and why)
- issues that need a human decision (and the specific question)
- stale tickets where linked PRs are already merged
- evidence-backed maintenance issues you would create (with evidence)
- anything unsafe or blocked

Only suggest new issues with clear evidence of a real problem. End with the exact actions you
would take in apply mode.
```

### Apply (only after the user enables it — see runbook)

```text
$backlog-manager apply GitHub backlog for <your-github>/agentic-os-97

Apply the backlog-manager workflow. Allowed actions:
- create the 11 managed labels if missing
- apply risk/type/agent labels (fill gaps only; never remove existing managed labels)
- add/update Agent Assessment comments
- create evidence-backed maintenance issues
- update issue status when a linked merged PR proves completion

Do NOT: write code, open PRs, merge anything, create speculative tickets, or mark vague/risky
work agent:ready. End with a concise run report.
```

## Forbidden

Writing code · opening PRs · merging · closing issues without merged-PR evidence · creating
speculative tickets · removing/downgrading existing managed labels · marking medium/high-risk
work `agent:ready` · deleting branches (report candidates only).

## See also

`../SKILL.md` · `../reference/labels.md` · `../automations/manager-automation.md` · `issue-to-pr.md`
