# Codex Automation — manager loop

**Cadence:** every ~12 hours. **Lane:** Codex Automation (Codex Pro subscription — never API credits).
**Job:** run `backlog-manager` on `<your-github>/agentic-os-97`.

During bring-up this runs in **dry-run** (report only). Flip to **apply** only after the user
approves (see `../runbook.md`). Add/update its row in `_system/automations/REGISTRY.md`.

## Run wrapper (the automation executes this)

```bash
AUTO=_system/automations
# 1. Budget circuit breaker — abort if over budget or HALT present
python "$AUTO/preflight.py" || { echo "[manager] halted by preflight"; exit 0; }

# 2. The job — dispatch the backlog-manager prompt to Codex (dry-run during bring-up; apply once enabled)
#    Prompt body: see wrenches/backlog-manager.md (self-contained: repo, source-of-truth rule,
#    allowed-mutation policy, create-issues=yes-with-evidence, verification, delivery target).
codex run "<backlog-manager dry-run|apply prompt for <your-github>/agentic-os-97>"

# 3. Record spend (tokens read from the Codex run usage output)
python "$AUTO/record_spend.py" "$AUTO" backlog-manager "$RUN_TOKENS" ok
```

## Self-contained cron prompt must include

repo/tracker name · source-of-truth rule (GitHub Issues for this repo) · allowed-mutation policy ·
create-issues-with-evidence vs propose-only · verification requirement · delivery target (run report).
Default scheduled behavior never merges PRs, never deletes branches, never spends past the ceiling.

## Enable / disable

Enable in Codex Automations once the runbook ramp is passed. Kill via: disable in Codex
Automations · create `_system/automations/HALT` · set `budget.json` ceiling to 0.
