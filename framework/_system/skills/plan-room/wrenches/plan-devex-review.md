---
name: plan-room-plan-devex-review
description: Developer experience lens for dev-facing projects (APIs, CLIs, SDKs, libraries, platforms, docs). Stress-tests onboarding, error messages, time-to-hello-world, API design, documentation, examples. Lens 4 of autoplan's 4-lens pipeline. SKIPPED automatically for non-dev-facing projects. 3 modes — DX EXPANSION (competitive advantage), DX POLISH (bulletproof every touchpoint), DX TRIAGE (critical gaps only). Trigger phrases include "DX review", "developer experience audit", "devex review", "API design review", "is the API good".
---

# plan-room-plan-devex-review — DX lens for dev-facing projects

When the project's user is a developer (consuming an API, calling a CLI, importing an SDK, reading docs), the DX lens stress-tests the developer's path from "I just heard about this" to "I just used it." Catches DX issues at plan time, before they become "users tried it once and bounced."

SKIPPED automatically for non-dev-facing projects (consumer apps, internal tools without external dev users, content sites). autoplan checks the brief; if no dev-facing surface, skips this lens.

---

## When to fire

- Auto-fires as lens 4 of autoplan's 4-lens pipeline IF project is dev-facing
- Direct: "DX review" / "developer experience audit" / "API design review"
- Before publishing an API / library / SDK / CLI

Don't fire when:
- Project has no dev-facing surface (consumer app, internal tool, content)
- The user only wants the DX runtime audit (that's the live `devex-review` skill — but that skill was CUT per DECISIONS_LOCKED, so this plan-time lens is the lens that survives)
- Documentation-only change (lower bar; quick check, not full lens)

---

## What "dev-facing" means

This lens fires when the project's primary user is a developer who will:

- Call an API endpoint
- Install a library / SDK
- Run a CLI command
- Read docs to integrate something
- Follow a tutorial
- Extend a platform via plugins / extensions

If the user is building for himself + his code, that's NOT dev-facing (it's internal). If the user is building for other developers (including future-user-as-API-consumer), that IS dev-facing.

The lens checks the brief's target user field; if "developers" / "dev teams" / "engineers" appear, lens fires.

---

## The 3 modes

### Mode 1: DX EXPANSION (competitive advantage)

Fires when:
- Project competes against incumbents that have DX gaps
- The user says "make DX the differentiator" / "what would beat the competition on DX"

Mode behavior:
- Benchmark against 2-3 competitors' DX
- Identify magical-moments opportunities (zero-config, instant value, surprising quality)
- Propose DX features that would create lock-in
- Output: DX moments + specific competitive gaps

### Mode 2: DX POLISH (bulletproof every touchpoint)

Fires when:
- Project is past v1 and DX is the differentiator
- Every touchpoint should feel finished

Mode behavior:
- Walk every developer touchpoint: install, hello-world, error messages, docs, examples
- Score each on polish (0-10)
- Identify rough edges with specific fixes
- Output: polished-or-not verdict per touchpoint

### Mode 3: DX TRIAGE (critical gaps only)

Default mode for early projects.

Mode behavior:
- Focus on what would prevent any developer from succeeding
- Install / first-call / first-error / docs-finding (the critical path only)
- Ignore polish; surface BREAKERS
- Output: critical gaps list

---

## Dimensions scored (0-10)

| Dimension | What a 10 looks like |
|---|---|
| **Onboarding** | Install + hello world in under 5 minutes from zero context |
| **Error messages** | Every error names what's wrong + how to fix; no stack traces without explanation |
| **Time to hello-world** | First useful result in under 5 minutes (literal minutes, not "5 commands") |
| **API design** | Predictable, consistent naming; sensible defaults; minimal required args |
| **Documentation** | Quickstart works, every API path documented with example, common errors explained |
| **Examples** | Copy-paste-runnable; cover happy path + 2-3 useful variations |
| **Failure recovery** | When something breaks, dev knows what to do; clear path to support |
| **CLI ergonomics** (if CLI) | Help text complete, subcommands intuitive, flags consistent, output greppable |

---

## The benchmarks

For comparison reviews, the lens compares against established DX leaders in adjacent spaces:

| Domain | Benchmark |
|---|---|
| HTTP API | Stripe (error messages), Linear (auth flow) |
| CLI | gh (consistency), vercel (zero-config), railway (auth flow) |
| SDK | OpenAI Python SDK (ergonomics), Vercel AI SDK (composability) |
| Library | React (mental model), Tailwind (defaults) |
| Platform | Vercel (deploy DX), Supabase (zero-config) |
| Docs | Stripe, Tailwind, Vercel (structure + searchability) |

The lens doesn't grade against "the best one across all" — it grades against the best in the adjacent domain.

---

## What gets stress-tested (concrete)

1. **The install command.** Is it one command? Does it require sudo / config files / env vars before it works?
2. **The hello-world example.** Copy-paste from docs to terminal — does it work first time, or does it require obvious-once-you-know fixes?
3. **The first error.** Deliberately break something (wrong arg, missing dep, bad input). Is the error message helpful or cryptic?
4. **The docs find.** Hunt for one specific thing in the docs (e.g., "how do I authenticate"). Can a stranger find it in under 60 seconds?
5. **The second example.** Try something one step beyond hello-world. Is there a guide for it, or is it left as exercise?
6. **The integration path.** From "I want to add this to my project" to "it's added and tested" — count steps. Under 5 = good.
7. **The CLI help text.** Run `<cli> --help` and `<cli> <subcommand> --help`. Is it clear or auto-generated mush?

For plan-time review, the lens walks the PLAN's proposed answers to these questions, not the live build. Live DX testing is its own thing (cut per DECISIONS_LOCKED).

---

## Output format

```markdown
## DevEx review — <project>

**Mode:** DX TRIAGE (early project, critical gaps focus)
**Composite score:** 6.5/10
**Status:** Will likely lose developers at first install + first error if shipped as planned

### Per-dimension
| Dimension | Score | Notes |
|---|---|---|
| Onboarding | 7 | npm install + 3 config steps; could be 1 command |
| Error messages | 4 | Plan doesn't specify error message strategy |
| Time to hello-world | 6 | 8 steps in quickstart; doable but slow |
| API design | 8 | Consistent naming; sensible defaults |
| Documentation | 5 | Quickstart planned; no error guide, no second example |
| Examples | 6 | One example planned; need 2-3 more |
| Failure recovery | 5 | No support path; no Discord / GitHub Discussions |
| CLI ergonomics | N/A | No CLI in this project |

### Critical gaps (would lose developers)
1. **Error messages are a blind spot.** Plan doesn't address what errors look like. Most projects ship cryptic Node stack traces. Fix: define error format in eng review (structured, with `code` + `message` + `docs_url`).
2. **3-step install in 2026 is too many.** Plan needs to consolidate to 1 step or add an installer wrapper.
3. **No "first error" recovery path.** A dev hitting an error has nowhere to go. Fix: add error code → docs URL convention.

### Magical moments missing (would create competitive advantage)
- Zero-config mode for the 80% case
- "How to install" page with a working iframe demo
- AI assistant in docs (claude-as-docs-bot)

### What I would NOT change
- API surface (well-designed)
- Quickstart structure
- Project naming
```

---

## Cost shape

- One Claude reasoning pass on the plan + brief
- Optional benchmark research (Gemini lane for "what does Stripe's error API look like in 2026") — adds medium cost if used
- One pass to draft findings + recommendations
- Total: medium. Cheaper than eng (less architecture analysis) but more involved than CEO (more empirical research).

---

## When the lens DOESN'T apply

If autoplan calls this lens and the brief shows no dev-facing surface:

```
[Lens skips]
"plan-devex-review skipped: project is not dev-facing (target user: the user himself + 50 paying customers, none developers)."
```

This is the normal path. Many projects have no DX surface to review. Skipping is the right answer.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Lens fires on non-dev project | Bad signal in brief target user field | Tune signal detection; explicit skip if the user says "not dev-facing" |
| Benchmarks feel stale | Stripe / Vercel / etc. evolve | Use Gemini lane to fetch current state of benchmark DX |
| Findings feel hypothetical | Plan-time review can't actually test errors | Note as borderline; flag for runtime testing in `qa` after ship |
| Score doesn't differentiate good vs great | Weights too even | Weight onboarding + error messages + hello-world highest |

---

## See also

- [SKILL.md](../SKILL.md) — plan-room mechanic
- [autoplan.md](autoplan.md) — pipeline driver
- [plan-ceo-review.md](plan-ceo-review.md) — lens 1
- [plan-eng-review.md](plan-eng-review.md) — lens 2
- [`design-studio/wrenches/plan-design-review`](../../design-studio/wrenches/plan-design-review.md) — lens 3 (visual / UX)
- [`ship/wrenches/qa.md`](../../ship/wrenches/qa.md) — runtime DX testing (after ship lands)
