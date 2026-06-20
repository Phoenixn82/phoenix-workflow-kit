---
name: project-orchestrator-audit-everything
description: Alternative apex mode. Comprehensive project sweep bundling cso (security) + ship/review (diff quality) + investigate (root-cause on flagged) + angry-code-auditor (the legacy "everything is wrong" sweep, dispatched via Codex). Per DECISIONS_LOCKED, this is the audit-mode replacement for the cut angry-code-auditor standalone. Trigger phrases include "audit everything", "audit the whole project", "what's wrong with this", "comprehensive audit", "roast my code", "find tech debt", "clean this up".
---

# project-orchestrator-audit-everything — comprehensive sweep

When the user says "audit everything" or "what's wrong with this project," the apex pivots from build-mode to audit-mode. Parallel dispatch of all major audit lenses + synthesis.

---

## When to fire

- "Audit everything" / "comprehensive audit"
- "What's wrong with this project"
- "Roast my code" / "find tech debt"
- "Clean this up" (large refactor signal)

Don't fire when:
- Single dimension audit (use the specific wrench directly — cso for security, ship/review for diff)
- The user wants the apex build pipeline (different mode)

---

## Parallel dispatch via router

```
Agent (parallel):
  cso — security audit (infrastructure + OWASP + STRIDE + LLM trust boundaries)
  ship/review — diff against base branch
  investigate — root cause on any recently-flagged bugs
  angry-code-auditor — comprehensive code roast (via Codex /goal)
  cso — supply chain check (npm audit / pip-audit / etc.)
  context-audit — harness hygiene if the user's setup also needs review
```

All 4-6 dispatched in parallel. This wrench caps at 6 concurrent agents (its own policy — diminishing returns past that).

---

## angry-code-auditor mode

Per DECISIONS_LOCKED, the legacy `angry-code-auditor` skill is folded into this wrench. It's a Codex /goal that:

1. Reads the whole codebase
2. Finds dead code, anti-patterns, security holes, performance landmines, architectural rot
3. Returns a brutally honest severity-ranked report

Codex runs this autonomously; Claude synthesizes with the other audit results.

---

## Synthesis

After all dispatched audits return:

1. **Deduplicate** — same root cause may appear in multiple lenses
2. **Cross-reference** — a security finding + a performance finding might be the same underlying issue
3. **Severity-rank** — HIGH / MEDIUM / LOW, with HIGH at top
4. **Group by surface** — backend / frontend / infra / docs
5. **Effort estimate** per finding — small / medium / large

Output:

```markdown
## Comprehensive audit — <project> — 2026-05-28

### Headline
[2-sentence: how healthy is this project, top concern]

### HIGH severity (3)
1. [security + perf] SQL N+1 on user lookup endpoint
   - Source: cso + investigate
   - Effort: medium
   - Recommendation: refactor with JOIN or eager-load
2. ...

### MEDIUM severity (12)
[list]

### LOW severity (34)
[list, brief]

### Tech debt patterns
- 23 callsites of deprecated <pattern>
- ...

### Recommended next actions
1. The user decides which HIGH to fix; apex dispatches Codex /goal for each
2. ...
```

---

## Fix dispatch (user-approved)

After the user approves which findings to fix:

```
For each approved finding:
  Codex /goal dispatched to fix + verify
  Heartbeat tracks progress
  Apex reviews fix when complete
  Re-runs targeted lens to verify fix
```

This is the "fix everything the user approves" mode.

---

## See also

- [SKILL.md](../SKILL.md)
- [`cso`](../../cso/) — security audit (standalone keeper)
- [`ship/wrenches/review.md`](../../ship/wrenches/review.md) — diff review
- [`investigate`](../../investigate/) — root-cause work
- [`context-audit`](../../context-audit/) — harness hygiene
- [`router/wrenches/codex-goal.md`](../../router/wrenches/codex-goal.md) — fix-loop dispatch
