---
name: loop-engineering
description: Owain Lewis's two-loop autonomous coding system, adapted for AI_Projects. A manager loop triages a GitHub backlog (classify risk/type, mark agent-ready, file evidence-backed tickets) and a worker loop turns agent-ready tickets into draft PRs (plan → fix → reviewer subagent → draft PR, never merge). Both run on Codex via Codex Automations (subscription only), gated by the `_system/automations` budget circuit breaker. GitHub Issues is the control plane; labels are the protocol. Trigger phrases include "loop engineering", "agent loop", "agent loops", "backlog manager", "autonomous coding loop", "triage the backlog", "issue to PR loop", "set up the agent loops", "run the manager loop", "run the worker loop".
---

# loop-engineering — two-loop autonomous coding system

Adapted from Owain Lewis, *"Agent Loops: Complete Guide (Claude Code + Codex)"*
(https://youtu.be/RVEaDvh6f5A). Original source vendored verbatim under `vendor/`.

Two agent loops that **never talk to each other**. They coordinate only through **GitHub Issues
as a shared control plane** — labels are the protocol. The engineering is in the boundaries, not
the agents.

```
messy backlog       →  manager  →  labelled, routed queue
agent-ready ticket  →  worker   →  draft pull request
draft pull request  →  the user  →  merged code
```

## The two loops

| Loop | Wrench | Job | Lane |
|---|---|---|---|
| **Manager** | `wrenches/backlog-manager.md` | Read every open issue + board + linked PRs, classify `risk:*`/`type:*`, mark safe low-risk work `agent:ready`, route judgment to `needs:human`, sync issue state from merged-PR evidence, sweep the repo and **file evidence-backed tickets**. Never writes code. | **Codex** |
| **Worker** | `wrenches/issue-to-pr.md` | Pick ONE `risk:low`+`agent:ready` issue → plan → worktree → smallest fix → tests → **separate Codex reviewer pass (maker ≠ checker)** → **draft PR** → link issue → **stop before merge**. | **Codex** |

## Control plane = GitHub Issues

Every piece of work is a ticket. Agents and humans collaborate on the same items, and the issue
history is the audit trail. The loops never call each other — the manager *writes* labels, the
worker *queries* them. Label set + colors live in `reference/labels.md`. `agent:ready` is a
**permission grant**, not a tag: an agent may only work a ticket that carries it.

## How it runs (subscription only)

- Both loops are **dispatched to Codex** (`router` → codex wrench / a Codex session), scheduled
  via **Codex Automations** on the user's Codex Pro subscription. **Never metered API credits.**
- **Every automation run obeys the budget contract** (`_system/automations/README.md`):
  1. `python _system/automations/preflight.py` first — if exit ≠ 0 (budget reached or `HALT`), STOP, do no work.
  2. Do the loop's job.
  3. `python _system/automations/record_spend.py <base> <name> <tokens> <status>` after.
- The automation definitions live in `automations/` (manager every ~12h, worker daily).

## Safety rules (encoded in both wrenches)

- **Dry-run by default during bring-up.** Apply mode only after the user enables it (see `runbook.md`).
- Manager **never writes code**; worker **never picks its own work** (only `agent:ready`).
- Every worker diff is reviewed by a **separate** Codex pass — maker ≠ checker.
- Worker opens **draft PRs only** and **never merges**. The user owns every merge.
- Worker branch pushes / PRs on a public repo **defer to the guard public-push gate** (gitleaks +
  denylist, fail-closed). Never bypass it.
- Budget circuit breaker (10M tokens/day) + `_system/automations/HALT` kill-switch are the brakes.

## When to fire which surface

- "Set up / build the agent loops" → this mechanic (reads `runbook.md`, dispatches the build).
- "Run the manager loop / triage the backlog" → `wrenches/backlog-manager.md` direct.
- "Run the worker loop / issue to PR" → `wrenches/issue-to-pr.md` direct.
- Pilot repo is `<your-github>/agentic-os-97`.

## See also

- `runbook.md` — the bring-up ramp (dry-run → apply → enable worker) + kill instructions.
- `reference/labels.md` · `reference/job-card.md` — the protocol + governance card.
- `_system/automations/` — the budget safeguard that replaces AGENTS.md rule #1's blanket ban.
- `vendor/` — Owain's original skill + prompts, verbatim.
