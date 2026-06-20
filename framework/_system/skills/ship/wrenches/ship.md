---
name: ship-ship
description: Pipeline entry wrench. Detect base branch, run tests, bump VERSION, update CHANGELOG, commit on a topic branch, push, open a PR. Sets the stage for review → land-and-deploy. GitHub-first per AGENTS.md hard rule #2. Trigger phrases include "ship this", "ship it", "commit and push", "open a PR", "ready to ship", "let's deploy", "push to main", "send it up".
---

# ship-ship — commit + PR

The first wrench in the pipeline. Takes uncommitted work and turns it into a reviewable PR on GitHub. Doesn't merge anything — that's `land-and-deploy`'s job. Doesn't review anything — that's `review`'s job. Just gets the work into GitHub in the right shape.

---

## When to fire

- The user has staged or unstaged changes and says "ship this" / "let's push this up"
- End of a build / fix session, before any deploy
- Auto-fires as step 1 of the full pipeline when the user says "ship" / "ready to ship" / "deploy"
- After `python-ci-preflight` passes (when Python)

Don't fire when:
- There are no changes (no-op; tell the user nothing to ship)
- The user only wants a local commit, no PR (just `git commit` direct)
- A PR is already open for this branch (re-use; don't open a new one)
- Working tree is dirty with unrelated changes (push back; ask the user to scope the commit)

---

## Sequence

1. **Detect base branch.** `main` vs `master` vs `develop`. Check `git symbolic-ref refs/remotes/origin/HEAD` first, then fall back to checking which exists.
2. **Run tests.** Detect test runner (`pytest`, `npm test`, `cargo test`, `go test`, etc.) and run. If tests fail, stop and surface — don't try to fix in the ship step.
3. **Bump VERSION** if the project has a VERSION file or semver in `package.json` / `pyproject.toml` / `Cargo.toml`. Default to patch bump; minor or major requires the user's explicit ask.
4. **Update CHANGELOG.md** with a new entry: date + bullet list summarizing the diff. Use a concise voice that matches existing entries (read the latest 2-3 to mirror style).
5. **Commit** with a clear message: imperative mood, one-line subject under 70 chars, optional body for the "why." Use a HEREDOC for the message body to preserve formatting.
6. **Detect or create topic branch.** If currently on the base branch, create a new branch named from the change scope (e.g., `feat/add-search-filter`, `fix/auth-redirect-loop`). If already on a topic branch, push to that.
7. **Push** with `-u` if the branch tracks no upstream.
8. **Open a PR via `gh pr create`** with title (under 70 chars) + body using a HEREDOC. Body includes Summary (1-3 bullets) and Test plan (markdown checklist).
9. **Return the PR URL** to the user.

---

## Commit message conventions

- Subject: imperative mood, under 70 chars. ("Add search filter to product list" not "Added" not "Adding")
- Avoid prefixes like "feat:" / "fix:" / "chore:" unless the project already uses them (check recent log)
- Body (optional, for non-trivial commits): one paragraph on the "why," not the "what" (the diff shows the what)
- Co-author trailer: use the harness's current default trailer rather than pinning a model name here (it drifts every model upgrade). As of this writing that is:
  ```
  Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
  ```
- HEREDOC pattern for clean formatting:
  ```bash
  git commit -m "$(cat <<'EOF'
  Add search filter to product list

  The catalog had grown to 400+ products with no discoverability path.
  Filter by category, price range, and availability solves the most
  common support questions from this week's user interviews.

  Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
  EOF
  )"
  ```

---

## PR creation conventions

```bash
gh pr create --title "<the pr title>" --body "$(cat <<'EOF'
## Summary
- <1-3 bullets — what changed and why>

## Test plan
- [ ] <how to verify item 1>
- [ ] <how to verify item 2>
- [ ] CI passes

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Keep titles under 70 chars. Details go in the body. The PR URL gets returned.

---

## Safety rules (load-bearing per AGENTS.md hard rule #2)

- **Never push to main directly.** Always topic branch → PR.
- **Never force-push to main.** Period. Warn loud if the user asks.
- **Never force-push to a shared branch.** Force-push to a feature branch only when the user is the only one on it.
- **Never skip hooks** (`--no-verify`, `--no-gpg-sign`) unless the user explicitly asks. If a hook fails, investigate and fix the cause.
- **Never amend a pushed commit** without the user's go-ahead (the amend rewrites history).
- **Never commit secrets.** Scan staged files for `.env`, credentials, API keys before commit. Warn loud if found.
- **Stage specific files by name** when possible. Avoid `git add -A` or `git add .` for sensitive areas.

---

## Test runner detection

| Signal | Runner | Command |
|---|---|---|
| `pyproject.toml` with `[tool.pytest]` or `tests/` directory | pytest | `pytest -x` (fail fast) |
| `package.json` with `"test"` script | npm | `npm test` |
| `Cargo.toml` | cargo | `cargo test` |
| `go.mod` | go | `go test ./...` |
| `Gemfile` with rspec | rspec | `bundle exec rspec` |
| `pubspec.yaml` | dart | `dart test` |
| No test setup found | none | Skip test step, warn the user |

If detection is ambiguous, ask the user which to run. Don't guess.

---

## Failure handling

| Failure | What to do |
|---|---|
| Tests fail | Stop pipeline. Surface failure with output. Don't try to fix in ship — push back to investigate/qa |
| Lint fails | Same as tests — stop, surface, don't ship broken |
| Hooks reject the commit | Surface the hook output. Fix the underlying issue, re-stage, NEW commit (NOT --amend per the global CLAUDE.md amend safety note) |
| Push rejected (out of date) | Surface; ask the user whether to rebase or merge base |
| `gh pr create` fails | Check `gh auth status`; surface to the user |
| PR already exists for this branch | Update existing PR body or push new commits to it; don't open duplicate |

---

## Cost shape

- Most steps are local git ops — trivial
- Test run is project-dependent (seconds to minutes)
- PR creation is one `gh` call
- Claude's job is orchestration + commit message + PR body writing; no heavy reasoning
- Don't burn Opus on this; Sonnet handles ship orchestration fine when invoked direct

---

## Helper scripts

The sequence above shells out to scripts at `../scripts/`:

| Sequence step | Script | What it does |
|---|---|---|
| 1. Detect base branch | `../scripts/detect-base-branch.sh <root>` | Returns main/master/trunk/develop. Prefers `origin/HEAD`. Exit 1 on fallback guess. |
| 3. Bump VERSION | `../scripts/version-bump.sh <root> {major\|minor\|patch} [--dry-run]` | Multi-source semver bump (VERSION, package.json, pyproject.toml, Cargo.toml, setup.py). |
| 4. Update CHANGELOG | `../scripts/changelog-update.sh <root> <new-version> [--since <ref>] [--body "<text>"]` | Keep-a-Changelog block prepend with conventional-commit categorization. Dupe-version rejected. |
| Pipeline state | `../scripts/ship-state.py {init\|get\|set\|reset} [stage] [--value <json>]` | Persistent `.ship-state.json` across the pipeline. Atomic writes. Archives on reset. |

All scripts are Codex-buildable per `PHASE_5_DISPATCH.md` § 5 (Phase 5 dispatch spec). All passed acceptance on 2026-05-28.

---

## See also

- [SKILL.md](../SKILL.md) — pipeline mechanic
- [python-ci-preflight.md](python-ci-preflight.md) — fires before ship for Python projects
- [review.md](review.md) — fires after ship, before merge
- [land-and-deploy.md](land-and-deploy.md) — fires after review approves
