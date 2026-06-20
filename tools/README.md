# tools/ — how this repo stays in sync

These scripts re-derive the shared kit from the live machine. **Recipients can ignore
this folder** — it's the maintainer's plumbing, not part of the framework you adopt.

## What runs

- **`sync-kit.ps1`** — the orchestrator. Copies the live skills/hooks/scripts from their
  real locations into `framework/`, runs the scrub, rebuilds the `dist/` zips, and shows
  what changed. Commits/pushes only when told to.
- **`scrub.py`** — the privacy scrub + safety guard. Rewrites real machine paths to
  placeholders, reports operator-name residues for human review, and **aborts** the whole
  sync if it finds a real credential or a forbidden private path. Exit code 2 = blocked.

Neither script contains the real username or any path literal — both derive identity from
`$env:USERPROFILE` / `~` at runtime, so the committed tooling can't leak it.

## Live sources (where the kit comes from)

| Repo path                                   | Live source                                  |
|---------------------------------------------|----------------------------------------------|
| `framework/_system/skills/`                 | `~/Desktop/AI_Projects/_system/skills/`       |
| `framework/_system/tool-parity/`            | `~/Desktop/AI_Projects/_system/tool-parity/`  |
| `framework/_system/verify-bridge.py`        | `~/Desktop/AI_Projects/_system/verify-bridge.py` |
| `framework/{AGENTS,CLAUDE,DECISION_MAP,SKILLS_INDEX,RELIABILITY_STANDARD}.md` | `~/Desktop/AI_Projects/*` |
| `framework/harness/CLAUDE.global.md`        | `~/.claude/CLAUDE.md`                          |
| `framework/harness/settings.reference.json` | `~/.claude/settings.json`                      |
| `framework/harness/hooks/`                  | `~/.claude/hooks/`                             |
| `framework/harness/scripts/`                | `~/.claude/scripts/`                           |
| `framework/harness/skills/codex-goal-dispatcher/` | `~/.claude/skills/codex-goal-dispatcher/` |
| `framework/agentic-os/aos_lock.py`          | `~/agentic-os/bin/aos_lock.py`                 |
| `framework/MANIFEST.md`, `framework/agentic-os/spawn-args.ts` | *no live source — preserved as-is* |

Mirrored subtrees exclude: `__pycache__`, `node_modules`, `logs`, `state`, `pipeline`,
`tests`, `secrets`, and log files.

## Honest limits

- **Path scrub is automatic. Operator-name generalization is NOT.** Project/skill names
  legitimately contain "phoenix" (e.g. `phoenix-web-ai`), so the scrub *reports* leftover
  operator-name mentions instead of blindly replacing them. The maintainer resolves those
  by hand before committing — which is exactly the "on command + I flag it" model.
- **The safety guard fails loud.** If a real secret pattern or a forbidden path
  (`second-brain/`, `.env`, `.secrets`, `voice-corpus/`, `secret-store/secrets`, `.codex/`)
  reaches the staged tree, the sync aborts with exit 2 and nothing is committed.

## Run it

```powershell
pwsh tools/sync-kit.ps1                                  # dry review (no commit)
pwsh tools/sync-kit.ps1 -Commit -Message "add X skill"   # commit locally
pwsh tools/sync-kit.ps1 -Commit -Push -Message "add X"   # commit + push
```
