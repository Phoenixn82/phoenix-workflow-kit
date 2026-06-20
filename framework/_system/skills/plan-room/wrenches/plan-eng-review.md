---
name: plan-room-plan-eng-review
description: Engineering manager mode plan review lens. Locks in architecture, data flow, edge cases, test coverage, performance. Catches issues before implementation. Lens 2 of autoplan's 4-lens pipeline. Routes specific implementation questions to Codex when a second opinion is needed (per AGENTS.md hard rule #5). Also fires direct on "eng review", "architecture review", "lock in the plan", "review the architecture", "is this architecturally sound", "engineering review", "data flow review".
---

# plan-room-plan-eng-review — architecture / execution lens

The eng lens asks: will this actually work as designed? Walks the plan as if the implementation were starting tomorrow. Identifies architecture issues, missing edge cases, undefined data flows, untested assumptions, performance landmines.

Not about whether the product is right (CEO lens). Not about visual UX (design). About the implementation plan being technically sound.

---

## When to fire

- Auto-fires as lens 2 of autoplan's 4-lens pipeline
- Direct: "eng review" / "architecture review" / "lock in the plan" / "is this sound"
- Before implementation when the user wants the architecture stress-tested

Don't fire when:
- No plan exists (push back to brief generation)
- Change is mechanical (no architecture surface; just code)
- The user specifically wants CEO or design or DX lens

---

## Dimensions scored (0-10)

| Dimension | What a 10 looks like |
|---|---|
| **Architecture clarity** | Component boundaries clear, responsibilities sharp, no god-object risk |
| **Data flow** | Inputs / transforms / outputs explicit at each boundary; no hidden state |
| **Edge case coverage** | Plan names the obvious edges + at least 2 non-obvious ones (concurrency, partial failure, etc.) |
| **Test strategy** | Plan names what gets unit / integration / E2E tested + what doesn't and why |
| **Performance budget** | Plan has a target (LCP, latency, throughput) and an approach to hit it |
| **Failure modes** | Plan names how each layer can fail + what happens when it does |
| **Security** | Plan respects trust boundaries; user input validated; secrets in env; no obvious OWASP issues (deep audit is `cso`, not here) |
| **Reversibility** | Plan can be backed out cleanly if v1 fails (Bezos type-2 door) |
| **Implementation simplicity** | Plan picks established tech over novel; fewer dependencies; no premature abstractions |

Composite weighted toward architecture clarity, data flow, and edge case coverage (the three that cause the most production pain).

---

## What the lens checks (concrete)

For every component in the plan:

1. **Responsibility check.** What does this component own? What doesn't it own? Is the boundary sharp?
2. **Interface check.** What does it expose? Inputs (types, validation), outputs (types, errors)?
3. **State check.** What state does it hold? Where does that state live (memory, DB, cache)?
4. **Concurrency check.** Can multiple requests hit it simultaneously? What happens if they do?
5. **Failure check.** What can go wrong? What's the user-visible behavior on failure? Is it retryable?
6. **Cost check.** Per-request resource cost? Bottleneck under load? Scaling story?
7. **Test check.** How is this verified? Unit + integration + E2E coverage plan?

For every data flow:

1. **Source.** Where does data come from? Trusted or untrusted?
2. **Validation.** Where does input validation happen? Once, or layered?
3. **Transformation.** What changes shape? Is the shape change documented?
4. **Persistence.** Where does it land? What's the schema?
5. **Egress.** Where does it leave the system? Are output guarantees stated?

For edge cases:

1. Empty inputs (empty list, empty string, null, undefined)
2. Maximum-size inputs (10x expected, 100x expected)
3. Partial failures (some succeed, some fail)
4. Concurrent modifications
5. Network failures (timeout, retry, partial response)
6. Out-of-order events
7. Time-related edges (DST, leap year, expired tokens, clock skew)

The lens doesn't enumerate every possible edge case for every component — it picks the ones likely to bite this specific plan.

---

## Codex consultation pattern

When the eng lens needs an implementation-level second opinion on a specific question, it routes through `router` → `codex` for that ONE question:

```bash
codex exec --plain "$(cat <<'EOF'
[FILESYSTEM BOUNDARY]
Architectural question: <specific question>

Context: <one paragraph>

What I'm thinking: <option A or option B>

Be opinionated. Pick one, explain why.
EOF
)"
```

Codex's answer feeds into autoplan's auto-decision logic. If Codex agrees with the lens's auto-lean, autoplan auto-decides. If Codex disagrees, autoplan surfaces both opinions for the user.

This is the only place Codex enters the plan-room — for specific implementation-level second opinions on tricky calls. The plan itself is still Claude's reasoning.

---

## Output format

```markdown
## Engineering review — <project>

**Composite score:** 7.8/10

### Per-dimension
| Dimension | Score | Notes |
|---|---|---|
| Architecture clarity | 8 | Component boundaries clear; one ambiguity around X (see finding 1) |
| Data flow | 7 | Inputs/outputs typed; missing validation at boundary Y |
| Edge case coverage | 6 | Names obvious edges; misses concurrent-write edge in cache layer |
| Test strategy | 8 | Unit + integration coverage planned; E2E not specified |
| Performance budget | 9 | Targets stated, approach realistic |
| Failure modes | 6 | Names happy path well; failure recovery underspecified |
| Security | 9 | Trust boundaries clear; auth + secrets handled |
| Reversibility | 8 | Migration is reversible; cache layer is throwaway |
| Implementation simplicity | 7 | Picks boring tech; one premature abstraction (finding 3) |

### Key findings (sorted by severity)

**HIGH — Concurrent write to cache layer (edge case coverage)**
- The plan has two pages writing to the same cache key. Under load, this races.
- Fix options:
  - A) Lock around cache writes (simpler, lower throughput)
  - B) Per-page namespacing (complex, higher throughput)
  - Codex consulted: prefers A for v1, B for v2 if throughput matters
- Auto-lean: A (smallest reasonable scope)

**MEDIUM — Validation only at outer boundary (data flow)**
- Plan validates HTTP input but trusts internal calls.
- Recommendation: layered validation at each boundary; small cost, big resilience win.

**MEDIUM — Premature abstraction in service layer (implementation simplicity)**
- Plan introduces ServiceBase / RepositoryBase before any concrete service exists.
- Recommendation: write the first concrete service first; extract base only when 2+ concrete impls justify it.

**LOW — E2E test strategy unspecified (test strategy)**
- Unit + integration good; E2E ("does the user signup actually work") missing.
- Recommendation: 1-2 happy-path E2Es covering the critical user paths.

### What would make this a 10
- Edge case coverage for concurrent writes
- Layered validation at internal boundaries
- Drop the premature abstraction

### What I would NOT change
- Architecture style (monolith is right for this scope)
- Stack choice (established for the user; new tech adds risk)
- Performance targets (realistic)
```

---

## Cost shape

- One Claude reasoning pass on the plan
- 1-3 Codex consultations on specific tricky questions (cheap on the user's Pro subscription)
- One pass to draft findings + recommendations
- Total: medium-high. The deepest of the 4 lenses (most analysis).

---

## When the lens punts to investigate

The eng lens doesn't root-cause bugs (that's `investigate`). If a finding requires "this could be wrong but I'd need to read the existing code to know" — the lens flags it and recommends `investigate` for the deeper dive. Doesn't try to do investigate's job inline.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Findings feel academic | Lens analyzing the plan in isolation, not against project reality | Read project's existing code more before reviewing the plan |
| Misses obvious edge case | Inference gap | Add to project's plan-state.json so future reviews remember |
| Codex consultation gives unhelpful answer | Question too vague | Tighten the Codex prompt; ask one focused question, not "review the architecture" |
| Score wildly disagrees with the user's gut | Reviewer weights wrong for this project | Tune dimension weights; record in second-brain |

---

## See also

- [SKILL.md](../SKILL.md) — plan-room mechanic
- [autoplan.md](autoplan.md) — pipeline driver
- [plan-ceo-review.md](plan-ceo-review.md) — lens 1
- [plan-devex-review.md](plan-devex-review.md) — lens 4
- [`router/wrenches/codex.md`](../../router/wrenches/codex.md) — Codex consultation pattern
- [`investigate`](../../investigate/) — when a finding requires root-cause work
- [`cso`](../../cso/) — when security review needs to be deeper than this lens covers
