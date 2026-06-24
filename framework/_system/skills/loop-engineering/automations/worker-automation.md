# Codex Automation — worker loop

**Cadence:** daily. **Lane:** Codex Automation (Codex Pro subscription — never API credits).
**Job:** run `issue-to-pr` for ONE `risk:low`+`agent:ready` issue on `<your-github>/agentic-os-97`.

Enable only AFTER the manager loop is trusted in apply mode (see `../runbook.md`). Add/update its
row in `_system/automations/REGISTRY.md`.

## Run wrapper (the automation executes this)

```bash
AUTO=_system/automations
# 1. Budget circuit breaker
python "$AUTO/preflight.py" || { echo "[worker] halted by preflight"; exit 0; }

# 2. The job — dispatch the issue-to-pr prompt to Codex (one ticket, draft PR, never merge)
#    Prompt body: see wrenches/issue-to-pr.md. Includes the separate reviewer pass (maker != checker).
codex run "<issue-to-pr one-ticket prompt for <your-github>/agentic-os-97, base branch main>"

# 3. Record spend
python "$AUTO/record_spend.py" "$AUTO" issue-to-pr "$RUN_TOKENS" ok
```

## Hard reminders for this automation

- Opens a **draft PR** and **stops before merge** — always.
- Branch push / PR passes the **guard public-push gate** (agentic-os-97 is public). Never bypass.
- One issue per run, linear, until the user promotes it to the parallel variant.

## Enable / disable

Enable in Codex Automations after manager apply is trusted. Kill via: disable in Codex
Automations · create `_system/automations/HALT` · set `budget.json` ceiling to 0.
