---
name: project-orchestrator-dispatch
description: Phases 2 through 5 of the apex pipeline. Coordinates design (if UI), build (Codex-dispatched), QA, and ship phases. Parallel sub-agent execution where possible; sequential gates at phase boundaries. The execution engine of the apex. Trigger phrases include "dispatch", "execute phases 2-5", "run the build pipeline", routes from scope.
---

# project-orchestrator-dispatch — phases 2-5 execution

The execution engine. Coordinates design + build + QA + ship. Parallel within a phase where possible, sequential between phases with the user gates at major boundaries.

---

## Phase 2: Design (conditional on UI)

If the plan has UI surface:

```
- design-consultation (if no DESIGN.md) OR
- awesome-design (if the user picked a brand) OR
- design-shotgun (if variants wanted) → the user picks
- design-html for production HTML
- Hand off to build (Codex implements component-level)
```

Skip Phase 2 if no UI.

---

## Phase 3: Build

Parallel sub-agent dispatch via router:

```
For each major component:
  Agent (parallel):
    dispatch Codex to implement <component>
    Claude monitors heartbeat

If backend involved:
  Run cso inline (security audit during build, not after)

Wait for all sub-agents complete
Claude reviews collective output
Integrate
```

Per AGENTS.md hard rule #5, Codex writes; Claude orchestrates + reviews.

**GATE:** the user go/no-go before QA.

---

## Phase 4: QA

Dispatch to ship/qa with --tier=standard by default:

```
ship/qa runs test+fix loop:
  - chrome-devtools-mcp walks critical paths
  - Surfaces bugs to bug-list.json
  - Dispatches Codex /goal to fix each
  - Re-verifies
  - Returns final bug-fix report

Claude reviews report.
If clean → Phase 5
If bugs deferred → the user decides
```

---

## Phase 5: Ship

```
1. ship/ship — commit + PR
2. ship/review — Codex diff-quality + Claude spec-compliance
3. GATE: the user go/no-go
4. ship/land-and-deploy — merge + wait + deploy + verify
5. Parallel post-deploy via Agent:
   - ship/canary
   - ship/benchmark
   - ship/pay-for-this
6. Synthesize results
```

---

## Failure handling between phases

If any phase surfaces a critical failure:
- Stop the pipeline (don't barrel forward to next phase)
- Surface to the user
- Decide: fix and retry, escalate to `investigate`, or abort

---

## Heartbeat updates

dispatch writes heartbeat updates after every major sub-agent completion or phase boundary. See [heartbeat.md](heartbeat.md) for the format.

---

## See also

- [SKILL.md](../SKILL.md)
- [scope.md](scope.md) — previous phase
- [heartbeat.md](heartbeat.md) — progress logging
- [completion.md](completion.md) — what runs after Phase 5
- All consumed mechanics: design-studio / build / ship / cso / investigate
