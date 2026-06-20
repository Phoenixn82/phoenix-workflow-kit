---
name: morning-briefing-retro
description: Weekly engineering retrospective wrench. Analyzes commit history, work patterns, code quality metrics with persistent history and trend tracking across weeks. Team-aware (per-person breakdowns with praise + growth areas if multi-contributor). Fires on the user's command — NO schedule. Variant of briefing-compiler with weekly cadence + engineering focus. Trigger phrases include "weekly retro", "engineering retro", "what did we ship this week", "weekly summary", "retro this week", "shipping log".
---

# morning-briefing-retro — weekly engineering retrospective

Different from briefing-compiler (daily, signals-broad) — retro is weekly and engineering-focused. Reads git history + commit messages + project shipping logs.

---

## When to fire

- "Weekly retro" / "engineering retro" / "what did we ship"
- End of work week
- After a sprint / milestone closes

Don't fire when:
- Daily synthesis wanted → briefing-compiler
- Single-project status → second-brain recall on that project
- The user wants a project-level retro on a specific feature → use this with `--project <slug>` flag

---

## What gets analyzed

| Source | Period | Used for |
|---|---|---|
| `git log --since="7 days ago"` per project | last 7 days | What shipped |
| Commit message themes | last 7 days | Where the user focused |
| PR merge history | last 7 days | Cycle time, batch size |
| Issues closed | last 7 days | Bug rate, feature throughput |
| Lines added / removed | last 7 days | Churn pattern |
| Tests added | last 7 days | Coverage delta |
| Quality metrics (lint, type errors) | current vs 7 days ago | Quality trend |
| Open loops resolved / opened | last 7 days | Backlog motion |

---

## Output shape

```markdown
# Weekly retro — week of 2026-05-22 to 2026-05-28

## Shipped
- <project 1>: <feature / fix list, brief>
- <project 2>: <...>

## By the numbers
- Commits: <N> (vs <M> last week)
- PRs merged: <N>
- Issues closed: <N>
- Tests added: <N>
- Lines: +<X> / -<Y>

## Where focus went
- <theme 1 — e.g., AI_Projects rebuild>: <N> commits
- <theme 2 — e.g., bug fixing>: <N> commits

## Cycle patterns
- Average PR cycle time: <hh:mm>
- Largest PR: <PR # — N lines>
- Smallest PR: <PR # — N lines>

## Quality trend
- Lint errors: <current> (vs <last week>)
- Type errors: <current> (vs <last week>)
- Test pass rate: <current> (vs <last week>)

## What went well
[opinionated assessment]

## What could be better
[opinionated assessment]

## What I'd focus on next week
[1-2 concrete suggestions]
```

---

## Trend tracking

Each retro appends to `Actions/retro-trends.md` so multi-week patterns surface:

```markdown
## Week of 2026-05-22 to 2026-05-28
- 23 commits, 5 PRs merged, focus on AI_Projects rebuild Phase 3
- Quality trend: stable (lint clean, no type regressions)
- Cycle pattern: small frequent PRs (median 47 lines)
```

After 4+ weeks of trends, the wrench surfaces patterns: "cycle times trending up — was 4hr median 4 weeks ago, now 12hr" / "you've been doing bigger PRs lately."

---

## Team mode

If `--multi-contributor`, breaks down per-person:

- What each person shipped (commits, PRs, lines)
- Per-person praise (what went well)
- Per-person growth area (concrete suggestion)
- Team patterns (review velocity, blocking PRs)

For solo the user work, skip team mode.

---

## See also

- [SKILL.md](../SKILL.md)
- [briefing-compiler.md](briefing-compiler.md) — daily variant
- [`second-brain/SKILL.md`](../../second-brain/SKILL.md) — where trends accumulate
