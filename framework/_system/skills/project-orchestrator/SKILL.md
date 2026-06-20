---
name: project-orchestrator
description: APEX skill. One prompt → interview → scope into deliverables → parallel sub-agent execution via router → covers full stack (backend, security, networking, MCP/CLI wiring, correct runtime per target). Hard completion logic — when scope is done, declares session done, auto-runs end-session ritual, emits handoff + next-session prompt. Audit-everything mode bundles cso + review + investigate + angry-code-auditor via Codex. The only thing in the system that fires multiple mechanics in sequence. Trigger phrases include "build me X", "spin up X", "execute this", "execute this idea", "orchestrate this", "run this project", "run the full pipeline", "take this from brief to launch", "walk me through building X", "I want a full X", "new project:", "braindump:", "/project", "audit everything".
---

# project-orchestrator — APEX

The only skill in the system that fires multiple MECHANICS in sequence. One prompt → ~80-90% done project. Coordinates plan-room → build → design-studio → ship → second-brain via parallel sub-agent execution.

Per AGENTS.md, this is the apex. Above mechanics. Reserved for full projects, not for single tasks.

---

## Cardinals

1. **Scope-then-go.** Even apex requires the plan-room intake first. No build-without-plan. The user's brain-dump goes through process-interviewer → project-brief-generator → project-loadout → autoplan BEFORE any code touches disk.

2. **Parallel where possible.** Per the orchestration shape: independent sub-tasks dispatch in parallel via the Agent tool. Sequential only when downstream needs upstream output. Heartbeat log shows the user what's running.

3. **Hard completion logic.** When scope is genuinely done (success criteria met, ship verdict positive, post-deploy clean), the orchestrator declares done. Auto-runs end-session ritual via second-brain. Emits handoff + next-session prompt. Doesn't grind past completion.

4. **Codex for code-writing, Claude for orchestration.** Per AGENTS.md hard rule #5, every code-writing sub-task dispatches to Codex through router. Claude's job in this mechanic is the orchestration — sequencing, gates, judgment, synthesis.

5. **Audit-everything mode is opt-in.** the user says "audit everything" → bundles cso + review + investigate + angry-code-auditor via Codex. Different from normal build → ship pipeline; this is the comprehensive sweep.

6. **the user gates between major phases.** Even with autoplan auto-decisions, the apex pauses at phase boundaries (after plan, after build, after deploy) for the user's go/no-go. Per AGENTS.md hard rule #2 (GitHub-first) + the user's stated preference (phase by phase with explicit go/no-go).

---

## The 8 phases

```
                ┌─────────────────────────────────────┐
                │ Phase 0: Intake                     │
                │  - process-interviewer (plan-room)  │
                │  - or office-hours if fuzzy idea    │
                └─────────────────┬───────────────────┘
                                  │
                ┌─────────────────▼───────────────────┐
                │ Phase 0.5: Brief                    │
                │  - project-brief-generator          │
                │  - emits CLAUDE.md                  │
                └─────────────────┬───────────────────┘
                                  │
                ┌─────────────────▼───────────────────┐
                │ Phase 1: Plan                       │
                │  - project-loadout                  │
                │  - autoplan (4-lens)                │
                │  - the user approves borderlines     │
                └─────────────────┬───────────────────┘
                                  │
                       GATE: the user go/no-go
                                  │
                ┌─────────────────▼───────────────────┐
                │ Phase 2: Design (if UI)             │
                │  - design-consultation OR           │
                │    awesome-design                   │
                │  - design-html for production       │
                └─────────────────┬───────────────────┘
                                  │
                ┌─────────────────▼───────────────────┐
                │ Phase 3: Build                      │
                │  - dispatch to Codex via router     │
                │  - cso inline during backend build  │
                │  - parallel sub-agents per file     │
                └─────────────────┬───────────────────┘
                                  │
                       GATE: the user go/no-go
                                  │
                ┌─────────────────▼───────────────────┐
                │ Phase 4: QA                         │
                │  - ship/qa for systematic test+fix  │
                │  - codex-goal-dispatcher for bugs   │
                └─────────────────┬───────────────────┘
                                  │
                ┌─────────────────▼───────────────────┐
                │ Phase 5: Ship                       │
                │  - ship/ship → review → land-deploy │
                │  - parallel canary + benchmark +    │
                │    pay-for-this post-deploy         │
                └─────────────────┬───────────────────┘
                                  │
                       GATE: the user go/no-go
                                  │
                ┌─────────────────▼───────────────────┐
                │ Phase 6: Document + Close           │
                │  - document-release                 │
                │  - second-brain end-session ritual  │
                │  - emit handoff + next-prompt       │
                └─────────────────────────────────────┘
```

---

## When this fires

- "Build me X" / "spin up X" / "execute this idea"
- "Take this from brief to launch"
- "Run the full pipeline"
- "New project: <brain dump>"
- "/project <description>"
- "Audit everything" → audit-everything mode
- The user wants ~80-90% of a project completed in one prompt

Don't fire when:
- Single task (just invoke the right mechanic / wrench)
- The user is mid-project and wants a specific phase (route to that mechanic)
- The user is debugging (investigate, then maybe come back)
- Audit single project area (use specific audit wrench)

---

## Picking the wrench

The apex's wrenches are PHASE wrenches, not tool wrenches. Each manages one phase of the pipeline.

| Phase wrench | What |
|---|---|
| `intake` | Phase 0 — interview, route to plan-room |
| `scope` | Phase 0.5 + 1 — brief, loadout, autoplan |
| `dispatch` | Phase 2-5 — coordinate mechanic invocations + Codex dispatch |
| `heartbeat` | Cross-cutting — progress log the user can check |
| `completion` | Phase 6 — hard completion detection + end-session ritual |
| `handoff-emit` | Phase 6 — produces the handoff file + next-prompt |
| `audit-everything` | Alternative mode — comprehensive audit (cso + review + investigate + angry-code-auditor) |

---

## Hard completion logic

When does the apex declare "done"?

Conditions checked sequentially:

1. **Success criteria met.** Read brief's success criteria; verify each is observable + observed.
2. **Ship verdict positive.** ship pipeline completed; review passed; deploy verified; canary clean; pay-for-this score above threshold.
3. **No critical open loops.** Scan open-loops.md for HIGH severity items related to this scope.
4. **user-approved.** Even with the above three green, the user explicitly says "yes, done."

When all four pass → orchestrator transitions to Phase 6 closure. Doesn't grind on adjacent improvements that weren't in scope.

---

## Audit-everything mode

When the user says "audit everything," the apex skips the build pipeline and runs a comprehensive sweep:

```
Parallel dispatch via router:
- cso (security audit, infrastructure-first)
- ship/review on current diff
- investigate on any flagged-recent bugs
- angry-code-auditor (the legacy "audit everything" — bundled in here per DECISIONS_LOCKED)

Synthesis:
- All findings into one severity-ranked report
- Cross-references between findings (security finding X + perf finding Y might be same root cause)
- The user decides what to fix; orchestrator dispatches fixes to Codex /goal
```

This mode is the "I just want to know what's wrong with this project" entry point.

---

## Parallel sub-agent execution pattern

For the build phase, the orchestrator dispatches multiple sub-agents in parallel:

```
Agent (parallel):
- Backend implementation → Codex
- Frontend implementation → Codex
- Schema generation → Codex
- Test scaffolding → Codex

Wait for all → review collective → integrate → continue.
```

Sub-agent results return; Claude orchestrates the integration. Per AGENTS.md, dispatching Codex for code-writing is the right pattern; Claude doesn't author production code in this orchestration.

---

## Heartbeat progress logs

The user can check progress between sessions or while the orchestrator runs:

```markdown
## Project: <slug> — heartbeat 2026-05-28 14:32

### Current phase: Phase 3 (Build)
### Started: 14:00
### Sub-agents active
- Codex implementing src/auth/middleware.ts (3 min in)
- Codex implementing src/api/users.ts (1 min in)
- Claude reviewing scaffolded src/db/schema.sql

### Completed
- Phase 0: Intake ✓ (10 min)
- Phase 0.5: Brief ✓ (5 min)
- Phase 1: Plan ✓ (20 min, 2 borderlines surfaced + resolved)
- Phase 2: Design ✓ (15 min, used awesome-design Anthropic brand)

### Up next
- Phase 3 completion (est. 30 min remaining)
- Phase 4 QA (the user gate)
```

Heartbeat lives at `_system/second-brain/Projects/<slug>/heartbeat.md`. Updated by orchestrator throughout.

---

## Cross-mechanic dependencies

This mechanic is the union of all others:

- `plan-room` for intake + brief + plan
- `design-studio` for design phase (if UI)
- `build` for implementation (Codex-dispatched)
- `ship` for QA + deploy + post-deploy
- `second-brain` for decisions / status / open loops / end-session ritual
- `router` for Codex dispatch on code work, Gemini for long-context analysis
- `cso` inline during build phase, full sweep in audit-everything mode
- `investigate` when a phase surfaces a bug needing root cause
- `web-scrape` if the project needs scraped data
- `content-forge` if the project produces content
- `seo` if the project is SEO-critical
- `printing-press-router` if any phase involves integrating a third-party service

---

## What project-orchestrator does NOT do

- Does not implement code itself (Codex via router)
- Does not skip phases without the user's override
- Does not auto-fire post-completion (the user decides next steps after handoff)
- Does not bypass the GitHub-first rule (hard rule #2)
- Does not override second-brain's end-session ritual (apex calls it; second-brain runs it)
- Does not exist for single tasks — use the right mechanic / wrench direct

---

## Wrenches

| Wrench | Path | What it does |
|---|---|---|
| **intake** | `wrenches/intake.md` | Phase 0 — routes brain-dump to right plan-room intake (process-interviewer / office-hours / decision-toolkit) |
| **scope** | `wrenches/scope.md` | Phase 0.5 + 1 — brief, loadout, autoplan; produces approved plan |
| **dispatch** | `wrenches/dispatch.md` | Phases 2-5 — coordinates mechanic invocations + parallel Codex dispatch |
| **heartbeat** | `wrenches/heartbeat.md` | Cross-cutting — progress log the user can check |
| **completion** | `wrenches/completion.md` | Phase 6 — hard completion detection + end-session ritual dispatch |
| **handoff-emit** | `wrenches/handoff-emit.md` | Produces handoff file + exact next-session prompt |
| **audit-everything** | `wrenches/audit-everything.md` | Alternative mode — cso + review + investigate + angry-code-auditor sweep |

---

## See also

- All other mechanic SKILL.mds (this apex calls all of them)
- [`AGENTS.md`](../../../AGENTS.md) — full operating manual
- [`SKILLS_INDEX.md`](../../../SKILLS_INDEX.md) — the mechanic catalog
- [`DECISION_MAP.md`](../../../DECISION_MAP.md) — task → tool routing
