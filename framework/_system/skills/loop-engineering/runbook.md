# Loop-engineering runbook — bring-up ramp

The system is built for unattended operation. This ramp is the trust-building path from "nothing
runs" to "loops run while you sleep." Don't skip the dry-run grading — that's the whole point.

## Step 1 — Bootstrap labels (pilot: `<your-github>/agentic-os-97`)

```powershell
# dry-run: report which of the 11 labels are missing, create nothing
pwsh scripts/bootstrap-labels.ps1 -Repo <your-github>/agentic-os-97
# apply: create the missing labels
pwsh scripts/bootstrap-labels.ps1 -Repo <your-github>/agentic-os-97 -Apply
```

## Step 2 — Manager dry-run ×3 (grade the judgment)

Dispatch the `backlog-manager` **dry-run** prompt to Codex three times. After each, grade:

- Did it keep risky / vague work **away** from agents? (If it marks everything low-risk → broken.)
- Did it ask a **specific question** where judgment is needed? (Not "act as my assistant".)
- Did it only propose **evidence-backed** tickets? (No speculative noise.)

Fix the wrench prompt if the judgment is off. **Only when it's right 3 runs straight** does it earn apply.

## Step 3 — Manager → apply (scheduled)

Flip `automations/manager-automation.md` to apply mode and enable it in Codex Automations
(every ~12h). It now labels, assesses, and files evidence-backed tickets autonomously. Still
**never writes code, never opens PRs, never merges.**

## Step 4 — Enable the worker (scheduled)

Enable `automations/worker-automation.md` in Codex Automations (daily). It picks one
`risk:low`+`agent:ready` issue and opens a **draft PR** while you sleep.

## Step 5 — Your morning loop

Read the Agent Assessments, review the draft PRs, merge the good ones, send back the rest, answer
the `needs:human` questions. Twenty minutes of judgment on top of hours of mechanical work.

## Kill switches (any one halts everything)

- `New-Item _system/automations/HALT` — every automation's next preflight aborts. Delete to resume.
- Set `_system/automations/budget.json` `daily_token_ceiling` to `0`.
- Disable the automation in Codex Automations.

## Reading the spend ledger

`_system/automations/spend-ledger-<UTC-date>.jsonl` — one line per run `{ts, automation, tokens,
status}`. The day's sum vs. `daily_token_ceiling` (default 10,000,000) is the circuit breaker.
