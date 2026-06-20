---
name: ship
description: Pipeline mechanic for shipping code. Commit → tests → review → PR → merge → deploy → canary → benchmark → pay-for-this verdict → document the release. GitHub-first per AGENTS.md hard rule #2. Codex runs diff-quality review; Claude runs spec-compliance. Codex is the fix lane when QA finds bugs. No auto-scheduled monitoring. Fires on "ship", "ship it", "deploy", "push to main", "create a PR", "merge", "land it", "ready to ship", "let's deploy", "does CI pass", "run a canary", "QA this app", "would I pay for this", "post-deploy check", "document the release".
---

# ship — the shipping pipeline

The wrench at the front of the pipeline (`ship` itself) commits, pushes, and opens a PR. Everything downstream — review, merge, deploy, canary, benchmark, paying-user audit, doc sync — fires in sequence or on demand. The user can call individual wrenches direct; the SKILL.md dispatcher walks the full pipeline by default.

This mechanic is the last gate between the user's code and production. It's load-bearing on safety (review + canary + QA) and on hygiene (CHANGELOG, docs, version bumps). Don't shortcut it.

---

## Cardinals

1. **Pipeline order, not menu order.** The wrenches form a sequence: `python-ci-preflight` (if Python) → `ship` (commit + PR) → `review` (Codex + Claude) → wait for the user's yes → `land-and-deploy` (merge + wait CI + wait deploy) → parallel `canary` + `benchmark` + `pay-for-this` post-deploy → `qa` if bugs surface → `document-release` to close the loop. Direct wrench invocations are fine, but the dispatcher walks the pipeline by default.

2. **GitHub-first per AGENTS.md hard rule #2.** Branches live on GitHub, not as local folder copies. `ship` pushes to a test branch and opens a PR. `land-and-deploy` waits for the user's explicit yes before merging to main. No silent merges. No force-pushes to main, ever. Force-push to a feature branch only when the user explicitly approves it and the branch isn't shared.

3. **Codex does diff-quality, Claude does spec-compliance.** `review` runs both halves. Codex's `codex review --plain` catches SQL safety, race conditions, off-by-one, leak patterns, untested edge cases — the structural diff bugs Codex is best at finding. Claude reads the diff against the original spec/plan and checks "does this match what we agreed to build" — the comparison-against-intent bugs. Both verdicts land in one report; both must pass before `land-and-deploy` proceeds (or the user explicitly overrides).

4. **Codex is the fix lane.** When `qa` surfaces bugs, fixes route through Codex per the code-routing rule in AGENTS.md hard rule #5. Default `qa` mode dispatches Codex `/goal` for sustained bug-bashing (per `DECISION_MAP.md`). `qa --report-only` skips the fix loop and emits a report only. Claude can author small patches when Codex is unavailable or the patch is tiny (under ~20 lines, one file), at Sonnet/Haiku tier.

5. **No auto-scheduled monitoring.** Per AGENTS.md hard rule #1, `canary` is a finite monitoring window the user triggers — not a recurring schedule. Window length is configurable (`--window 30m`, `--window 24h`) but it always ends. "Watch production forever" is not an option. If the user wants ongoing monitoring, that's a separate platform decision (Sentry, Datadog) outside this mechanic.

6. **All browse-daemon refs repointed to chrome-devtools-mcp / Playwright.** Per DECISIONS_LOCKED, the cut gstack browse daemon is replaced across `qa`, `canary`, `benchmark`, `pay-for-this`. Cheap one-off audits run through chrome-devtools-mcp MCP tools. Repeatable / scheduled monitoring runs through Codex-authored Playwright scripts (Codex writes per AGENTS.md hard rule #5; Claude specs).

7. **Verification beats assertion.** Per the global CLAUDE.md "Full-stack verification" rule: never claim "shipped" without evidence — `git log` on main showing the merge commit, deploy status check from the platform, live URL responding 200, the actual user-visible feature working. A green CI checkmark alone is not "shipped." Walk the chain.

8. **Continuity gate for desktop/local apps (AGENTS.md hard rule #12).** For any app the user launches locally (desktop/Windows/launcher), "done" includes a continuity check against `RELIABILITY_STANDARD.md`, not just "it ran once for me." Before the `pay-for-this` verdict, confirm: it carries its own runtime + pinned deps (Pillar A); the launcher is idempotent + readiness-gated + leaves a log trail and self-heals (Pillar B); it opens cold (kill all instances, double-click the real shortcut, verify it paints — the way the Agentic OS GPU regression was caught) with the network off. A web/cloud-only project skips this gate. If continuity fails, it's a `qa` item, not a ship.

---

## The pipeline, spelled out

```
                                    ┌──────────────────────┐
                                    │  the user says "ship" │
                                    └──────────┬───────────┘
                                               │
                              ┌────────────────┴────────────────┐
                              │                                 │
                  ┌───────────▼──────────┐         ┌────────────▼────────────┐
                  │ python-ci-preflight  │         │  (skip if not Python)   │
                  │ (if Python project)  │         └────────────┬────────────┘
                  └───────────┬──────────┘                      │
                              └────────────────┬────────────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │ ship                 │
                                    │ - detect base branch │
                                    │ - run tests          │
                                    │ - bump VERSION       │
                                    │ - update CHANGELOG   │
                                    │ - commit + push      │
                                    │ - open PR            │
                                    └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │ review               │
                                    │ - Codex diff-quality │
                                    │ - Claude spec-comp.  │
                                    │ - both verdicts → PR │
                                    └──────────┬───────────┘
                                               │
                                       The user │ yes/no
                                               │
                                          yes  │  no → fix, re-review
                                               ▼
                                    ┌──────────────────────┐
                                    │ land-and-deploy      │
                                    │ - merge PR           │
                                    │ - wait CI            │
                                    │ - wait deploy        │
                                    │ - kick post-deploy   │
                                    └──────────┬───────────┘
                                               │
                              ┌────────────────┼────────────────┐
                              │                │                │
                  ┌───────────▼──────────┐   ┌─▼──────────────┐ │
                  │ canary               │   │ benchmark      │ │
                  │ (monitoring window)  │   │ (perf compare) │ │
                  └───────────┬──────────┘   └─┬──────────────┘ │
                              │                │                │
                              └────────────────┼────────────────┘
                                               │
                                  ┌────────────▼─────────────┐
                                  │ pay-for-this             │
                                  │ ("would I pay?" verdict) │
                                  └────────────┬─────────────┘
                                               │
                                  bugs surfaced │  no bugs
                                               │
                                          yes  │   no → document-release
                                               ▼
                                    ┌──────────────────────┐
                                    │ qa                   │
                                    │ - test + fix via Cdx │
                                    │ - or --report-only   │
                                    └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │ document-release     │
                                    │ - sync README        │
                                    │ - update CHANGELOG   │
                                    │ - polish docs        │
                                    └──────────────────────┘
```

---

## When this mechanic fires (auto-detect)

- "Ship it" / "ship this" / "ready to ship" / "let's deploy"
- "Push to main" / "merge this" / "land it"
- "Create a PR" / "open a PR for this"
- "Run a canary on production"
- "QA this app" / "find bugs" / "test this and fix"
- "Would I pay for this" / "post-deploy check" / "audit the live app"
- "Document the release" / "update the docs to match what shipped"
- "Does CI pass" / "is this ready"

When it does NOT fire — even though it sounds like it might:
- "Run the tests locally" → just run them, no need for the ship pipeline
- "Lint this file" → not ship; that's a one-off tool call
- "Audit security" → that's `cso`, not ship's `review`
- "Find root cause of this bug" → that's `investigate`, escalated FROM qa
- "Plan the architecture" → that's `plan-room`, way upstream of ship

---

## Picking the wrench

| Shape of the ask | Wrench | Why |
|---|---|---|
| "Ship this" / "let's deploy" / "ready to push" | Full pipeline | Walk start to finish |
| "Just commit and PR, I'll review myself" | `ship` direct | Skip review/deploy stages |
| "Review my diff before I merge" | `review` direct | Both Codex + Claude halves |
| "Land it now" / "merge this PR" | `land-and-deploy` direct | Pre-reviewed, just need merge + deploy |
| "Run a canary after the deploy" | `canary` direct | Standalone post-deploy monitoring |
| "Check if this regressed perf" | `benchmark` direct | Standalone perf compare |
| "Would I pay for this?" | `pay-for-this` direct | Standalone live-app audit |
| "QA this and fix what you find" | `qa` direct | Test + fix loop |
| "QA this but don't fix" | `qa --report-only` direct | Report only |
| "Set up deployment for this project" | `setup-deploy` direct | One-time platform config |
| "Update docs to match what shipped" | `document-release` direct | Post-merge doc sync |
| Python project, before any push | `python-ci-preflight` auto-fires | CI safety net |

---

## Cross-mechanic dependencies

- **`router`** dispatches: Codex for diff-quality review, Codex for fix loops in qa, Codex `/goal` for sustained bug-bashing, Claude for spec-compliance review and pipeline orchestration
- **`cso`** runs inline DURING build per DECISION_MAP, so cso is NOT chained into ship's review. By the time ship fires, cso has already vetted security.
- **`investigate`** is what `qa` escalates to when a bug isn't surface-level. ship doesn't own root-cause work — it dispatches to investigate when needed.
- **`second-brain`** captures ship lessons at `Actions/shipping.md`: what broke deploys, what canary caught, perf regression patterns, deploy-platform quirks. So future ships are smarter.
- **`build`** is upstream of ship. `build` builds; `ship` ships. The handoff is the moment the user says "I want this deployed."

---

## What ship does NOT do

- Does not architect or design (that's `plan-room` + `design-studio`)
- Does not implement the project (that's `build`)
- Does not run security audits (that's `cso`, inline during `build`)
- Does not root-cause bugs at depth (that's `investigate`, escalated from `qa`)
- Does not write production code (that's Codex via `router`; Claude integrates per AGENTS.md hard rule #5)
- Does not schedule recurring monitoring (per hard rule #1; canary runs a finite window)
- Does not skip the user's go/no-go gate before merging to main (per hard rule #2)
- Does not write feature flag wrappers, backwards-compat shims, or "just in case" rollback hooks (per the global CLAUDE.md no-half-measures rule — ship clean changes, not safety blankets)

---

## Wrenches

| Wrench | Path | What it does |
|---|---|---|
| **ship** | `wrenches/ship.md` | The entry: detect base branch, run tests, bump VERSION, update CHANGELOG, commit, push, open PR. Skips trivial diffs from pre-review steps |
| **python-ci-preflight** | `wrenches/python-ci-preflight.md` | Python-only: ruff lint, isort, missing deps, pytest. Catches CI breakers before push |
| **review** | `wrenches/review.md` | Pre-landing diff review. Codex diff-quality + Claude spec-compliance, both halves report into PR |
| **land-and-deploy** | `wrenches/land-and-deploy.md` | Merge PR, wait CI, wait deploy, trigger post-deploy wrenches. The atomic "land it" step |
| **setup-deploy** | `wrenches/setup-deploy.md` | One-time platform detection + config write to project CLAUDE.md. Detects Fly / Render / Vercel / Netlify / Heroku / GHA / custom |
| **canary** | `wrenches/canary.md` | Finite monitoring window post-deploy. Console errors, perf regressions, page failures via chrome-devtools-mcp |
| **benchmark** | `wrenches/benchmark.md` | Performance regression detection. Baselines page-load / CWV / bundle size; compares before/after |
| **qa** | `wrenches/qa.md` | Systematic QA + fix loop. Codex `/goal` does the iteration. `--report-only` flag skips fixes (qa-only collapsed in) |
| **pay-for-this** | `wrenches/pay-for-this.md` | Post-deploy paying-user audit via chrome-devtools-mcp. Returns "would I pay $20/mo?" verdict with evidence |
| **document-release** | `wrenches/document-release.md` | Syncs README, ARCHITECTURE, CONTRIBUTING, CLAUDE.md, CHANGELOG against what actually shipped |

---

## Cost shape

| Wrench | Lane | Cost ballpark |
|---|---|---|
| `python-ci-preflight` | local commands | trivial |
| `ship` | Claude orchestration + git ops | low |
| `review` | Codex CLI call + Claude reasoning | medium (one Codex review per diff) |
| `land-and-deploy` | platform CLI + git ops | low |
| `setup-deploy` | one-time, file detection | low (rarely fires after initial setup) |
| `canary` | chrome-devtools-mcp polling | medium-high (model call per check; window-length-dependent) |
| `benchmark` | chrome-devtools-mcp baselining | medium (couple of runs) |
| `qa` | chrome-devtools-mcp + Codex `/goal` fix loop | HIGH (longest-running wrench; many iterations) |
| `pay-for-this` | chrome-devtools-mcp walkthrough | medium (~10-20 actions) |
| `document-release` | file reads + Claude reasoning | low-medium |

Total full-pipeline cost is dominated by `qa` if bugs are found. Without bugs, ship is cheap end-to-end. Budget for qa specifically when expecting issues.

---

## Helper scripts (live at `scripts/`, acceptance-tested 2026-05-28)

- `detect-deploy-platform.sh` — sniffs the project root and echoes one platform name: `fly.io` (`fly.toml`), `vercel` (`vercel.json` / `next.config.*`), `netlify` (`netlify.toml` / `_redirects`), `render` (`render.yaml`), `heroku` (`Procfile` **and** `app.json`), `github-actions` (`.github/workflows/*deploy*.{yml,yaml}`), `docker-self-host` (`Dockerfile` **and** `docker-compose.yml`), else `unknown`. Note: does not check `app.yaml`. Used by `setup-deploy` and `land-and-deploy`.
- `detect-base-branch.sh` — detects the base branch (`main` / `master` / `trunk` / `develop`), outputs the branch name only. No upstream-remote output, no caching.
- `ship-state.py` — reader/writer for `.ship-state.json` (dot-prefixed). Tracks pipeline state across the six stages (`tests`, `review`, `pr`, `merge`, `deploy`, `canary`) so `land-and-deploy` can resume across sessions without re-querying GitHub. Actions: `init` / `get` / `set` / `reset`.
- `version-bump.sh` — semver bump (major / minor / patch); reads existing VERSION / package.json / pyproject.toml / Cargo.toml; writes the new version.
- `changelog-update.sh` — appends a new entry to CHANGELOG.md with date + bullet list from the diff summary.

All five live at `scripts/` and passed acceptance on 2026-05-28. ship wrenches work without them (with more manual orchestration); the scripts make the pipeline tighter. (The `Spec: PHASE_5_DISPATCH.md` / `DECISIONS_LOCKED` headers in the scripts and wrenches are provenance only — both files now live solely at `_archive\claude_projects_2026-05-pre-rebuild\Rebuild\`; the shipped scripts are self-documenting.)

---

## See also

- [wrenches/ship.md](wrenches/ship.md) — pipeline entry, commit + PR
- [wrenches/python-ci-preflight.md](wrenches/python-ci-preflight.md) — Python CI safety net
- [wrenches/review.md](wrenches/review.md) — Codex + Claude two-half review
- [wrenches/land-and-deploy.md](wrenches/land-and-deploy.md) — merge + wait + deploy
- [wrenches/setup-deploy.md](wrenches/setup-deploy.md) — one-time platform config
- [wrenches/canary.md](wrenches/canary.md) — post-deploy monitoring window
- [wrenches/benchmark.md](wrenches/benchmark.md) — performance regression detection
- [wrenches/qa.md](wrenches/qa.md) — test + fix loop (and --report-only mode)
- [wrenches/pay-for-this.md](wrenches/pay-for-this.md) — paying-user audit
- [wrenches/document-release.md](wrenches/document-release.md) — post-merge doc sync
- [`AGENTS.md`](../../../AGENTS.md) — hard rule #2 (GitHub-first) + hard rule #5 (code routing)
- [`DECISION_MAP.md`](../../../DECISION_MAP.md) — UI/bug testing → chrome-devtools-mcp + codex-goal-dispatcher
- [`router/SKILL.md`](../router/SKILL.md) — Codex/Claude/Gemini dispatch
- [`second-brain/SKILL.md`](../second-brain/SKILL.md) — where shipping lessons land
