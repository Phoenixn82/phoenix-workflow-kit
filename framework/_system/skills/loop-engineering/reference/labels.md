# Label protocol (the control plane's language)

A small fixed set. Do not invent extra labels. `agent:ready` is a **permission grant**, not a tag —
an agent may only work a ticket that carries it.

## Risk

| Label | Color | Meaning |
|---|---|---|
| `risk:low` | `0E8A16` | Safe for agent execution when also `agent:ready`. |
| `risk:medium` | `FBCA04` | Maybe agent-suitable later; not unattended by default. |
| `risk:high` | `B60205` | Human-led. Agents may investigate/plan, not execute unattended. |

## Type

| Label | Color | Meaning |
|---|---|---|
| `type:bug` | `5319E7` | Incorrect behavior or regression. |
| `type:feature` | `5319E7` | New user- or developer-facing capability. |
| `type:docs` | `5319E7` | Docs, examples, README, comments, links. |
| `type:test` | `5319E7` | Test additions/fixes/coverage/fixtures. |
| `type:refactor` | `5319E7` | Internal restructuring, no behavior change. |
| `type:chore` | `5319E7` | Deps, build, CI config, formatting, cleanup. |

## Routing

| Label | Color | Meaning |
|---|---|---|
| `agent:ready` | `1D76DB` | Permission for the worker loop to pick up the issue. |
| `needs:human` | `D93F0B` | A human decision/clarification/judgment is required. |

**11 labels total.** We do **not** create `agent:blocked` or `agent:complete` — completion and
blocked state live in GitHub issue/PR state. The worker skips `needs:human` + `risk:medium` +
`risk:high`, and honors a pre-existing `agent:blocked` if the repo already has one but never
creates it.

Bootstrap them with `../scripts/bootstrap-labels.ps1` (dry-run by default).
