---
name: ship-document-release
description: Post-merge documentation sync. Reads all project docs (README, ARCHITECTURE, CONTRIBUTING, CLAUDE.md, CHANGELOG), cross-references the diff that just landed, and updates anything that drifted. Polishes CHANGELOG voice. Cleans stale TODOs in docs. Optionally bumps VERSION. Trigger phrases include "document the release", "update the docs", "sync documentation", "post-ship docs", "docs to match what shipped", "release notes".
---

# ship-document-release — sync docs to what shipped

After a merge lands, the codebase has moved but the docs haven't. README still describes the old behavior, ARCHITECTURE.md still shows the old data flow, CONTRIBUTING.md still references the deprecated setup step. This wrench reconciles.

Fires after `land-and-deploy` succeeds — the docs sync makes sense once the change is actually in main, not before.

---

## When to fire

- Auto-fires after `land-and-deploy` completes successfully (terminal step in the pipeline)
- Direct: "update the docs to match" / "document this release" / "sync the docs"
- After a feature lands that changes user-facing behavior
- Before publishing a release (release notes derive from this work)

Don't fire when:
- Change is config / dependency / internal-refactor with no user-visible diff (docs unaffected)
- The user explicitly says "skip docs"
- The merge introduced a breaking change the user hasn't decided how to communicate yet (push back: docs need direction)

---

## What gets reviewed

| File | What to check |
|---|---|
| `README.md` | Setup instructions, usage examples, feature list — does it match current code? |
| `ARCHITECTURE.md` (or `docs/architecture.md`) | Data flow, component diagrams, key decisions — still accurate? |
| `CONTRIBUTING.md` | Dev setup, test commands, conventions — still working? |
| `CLAUDE.md` (project-level) | Brain file for the project — does it reference deprecated patterns or files? |
| `CHANGELOG.md` | Latest entry voice — match existing style; add details `ship` may have left brief |
| `docs/` directory tree | Any deeper docs touching changed areas |
| `package.json` / `pyproject.toml` description fields | Does the project description still match? |
| Inline `// TODO` and `// FIXME` comments in code | If the merge resolved one, remove the marker |

---

## Sequence

```
1. Read the merge commit's diff: `git diff <merge-base>..<merge-commit>`
2. For each doc file, read current content
3. For each doc file, cross-reference:
   a. Are any code paths referenced by name that the diff renamed/removed?
   b. Are any setup steps documented that the diff changed?
   c. Are any features described that the diff added/removed?
   d. Are any commands shown that the diff updated?
4. For each finding, draft an update
5. Show drafts to the user in one batched message
6. Apply approved updates
7. Bump VERSION if appropriate (per project's versioning policy)
8. Surface final state
```

---

## CHANGELOG polish

`ship` wrote a CHANGELOG entry at commit time. It's often terse — built for speed, not for the audience. `document-release` polishes it:

- Match the voice of the existing top entries (read the latest 3-5)
- Group bullets by category if the change is multi-faceted (Added / Changed / Fixed / Deprecated / Removed)
- Add the "why" if the original entry was only the "what"
- Add migration notes if the user's users need to do anything
- Add a link to the PR for the audit trail
- Remove any auto-generated marker like "🤖 Generated with Claude Code" if it's not the project's convention

Example before/after:

```markdown
# Before (from ship)
## v0.4.2 — 2026-05-28
- Add search filter to product list

# After (from document-release)
## v0.4.2 — 2026-05-28

### Added
- **Product search filtering** — filter the catalog by category, price range,
  and availability. Solves the most common support questions from this
  week's user interviews. ([PR #42](https://github.com/.../pull/42))
```

---

## VERSION bump (optional)

If `ship` did a patch bump and `document-release` finds the change was actually minor (new feature) or major (breaking), it can flag the mismatch for the user. Doesn't auto-rewrite — surfaces for the user's call.

Versioning policy detection:

| Signal | Policy |
|---|---|
| `VERSION` file with semver | semver — diff scale dictates major / minor / patch |
| `package.json` with semver | same |
| `pyproject.toml` with semver | same |
| Date-based versioning (calver) | bump to today's date |
| No version file | skip; nothing to bump |

---

## TODO cleanup

If a TODO comment in code references "fix this when X is done" and the merge did X, remove the TODO. Don't remove other TODOs (out of scope).

```python
# Before
def parse_payload(data):
    # TODO: handle the v2 format once the migration ships
    return v1_parser(data)

# After (if the migration is the merged change)
def parse_payload(data):
    return v2_parser(data) if data.get('version') == 2 else v1_parser(data)
```

The fix itself is in the source code (Codex wrote it during build); document-release just removes the TODO marker.

---

## Don't-create rules (load-bearing per the global CLAUDE.md)

- **Don't create new docs that didn't exist.** If the project has no ARCHITECTURE.md, don't add one. document-release syncs existing docs, doesn't invent doc structure.
- **Don't write multi-paragraph docstrings or comment blocks** in code as part of the doc sync. Inline doc work is separate.
- **Don't generate release notes for unreleased internal work.** If the user hasn't published a release, the CHANGELOG entry is enough.
- **Don't auto-publish.** If the project has a release process (GitHub Release, npm publish, PyPI push), surface it for the user's go-ahead but don't run it.

---

## Sequence handling

document-release fires last in the pipeline. By the time it runs:
- The PR is merged
- The deploy is verified
- canary, benchmark, pay-for-this have surfaced or completed

If any of those surfaced critical issues, document-release should NOT fire — the priority is fixing the issue, not documenting a broken release. Check post-deploy wrench state first; skip if anything is RED.

---

## Cost shape

- Read N doc files + diff = small token cost
- Per-doc reasoning to detect drift = medium
- Draft generation + the user review batch = medium
- Apply approved edits = small
- Total: cheap for small diffs; medium for cross-cutting changes affecting many docs

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Detects drift that isn't really drift | False positive on doc/code semantic match | Surface for the user; let him override |
| Misses drift | Doc uses different terms than code | Improve cross-reference patterns over time |
| CHANGELOG polish overwrites the user's intentional terse style | Style mismatch | Read 3-5 prior entries first; mirror tone |
| Suggests version bump the user doesn't want | Versioning policy mismatch | the user overrides; document the project's policy in CLAUDE.md |

---

## Pairing patterns

- Auto-fires after `land-and-deploy` completes (as long as post-deploy didn't surface critical issues)
- Pair with second-brain: shipping lessons get captured at `Actions/shipping.md`
- After major release, pair with the project's release publish step (the user decides)

---

## See also

- [SKILL.md](../SKILL.md) — pipeline mechanic (final wrench in the pipeline)
- [ship.md](ship.md) — wrote the initial CHANGELOG entry that gets polished here
- [land-and-deploy.md](land-and-deploy.md) — completes before document-release fires
- [`second-brain/wrenches/capture.md`](../../second-brain/wrenches/capture.md) — where shipping lessons land
