---
name: ship-python-ci-preflight
description: Python CI safety net. Runs ruff lint, isort import ordering, missing-dependency detection, and pytest before any push. Catches CI breakers locally so the user doesn't end up with a red CI he could have prevented. Auto-fires as pipeline step 1 when the project has a Python backend. Trigger phrases include "preflight", "before I push this", "does CI pass", "lint and test before ship", "python preflight".
---

# ship-python-ci-preflight — local CI dry-run for Python projects

CI fails are predictable. Ruff complains about imports, isort wants them sorted, a missing import in requirements.txt blows up in CI, pytest finds a typo. This wrench runs all four checks locally — the same way CI will — and reports what would break, before push.

Only fires when the project is Python.

---

## When to fire

- Auto-fires as pipeline step 1 when the user says "ship" and the project is Python
- Direct call: "run preflight" / "does CI pass" / "lint and test before ship"
- After major Python edits, before commit, when the user wants the safety net

Don't fire when:
- Project isn't Python (no `pyproject.toml`, `requirements.txt`, `setup.py`, `Pipfile`)
- The user wants a partial check (call ruff / pytest directly)
- CI configuration is dramatically different from defaults (e.g., custom linter set) — check `.github/workflows/` and match what CI actually runs

---

## What it checks

| Check | Tool | Why it matters |
|---|---|---|
| Lint errors | `ruff check .` | Will fail CI |
| Import order | `ruff check . --select I` or `isort --check-only .` | Often configured as CI gate |
| Missing dependencies | parse imports vs requirements.txt / pyproject.toml | CI will fail on import error |
| Test failures | `pytest -x` | Obvious CI fail |
| Type errors (if mypy/pyright in CI) | `mypy .` or `pyright` | CI gate when configured |

---

## Sequence

```bash
# 1. Detect Python project shape
if [ -f pyproject.toml ]; then
  echo "[preflight] Found pyproject.toml"
elif [ -f requirements.txt ]; then
  echo "[preflight] Found requirements.txt"
else
  echo "[preflight] Not a Python project, skipping"; exit 0
fi

# 2. Lint
ruff check . || { echo "[preflight] ruff lint failed"; exit 1; }

# 3. Import order (separate ruff selector or isort)
ruff check . --select I || { echo "[preflight] import order failed"; exit 1; }

# 4. Missing deps — diff `pip freeze` against requirements.txt (rough check)
#    For pyproject, use `pip check`
pip check 2>&1 | grep -v "^$" && echo "[preflight] dep issues found" && exit 1 || true

# 5. Tests
pytest -x --tb=short || { echo "[preflight] pytest failed"; exit 1; }

# 6. Optional: type check if mypy/pyright is in dev deps
if command -v mypy >/dev/null && grep -q "mypy" pyproject.toml requirements*.txt 2>/dev/null; then
  mypy . || { echo "[preflight] mypy failed"; exit 1; }
fi

echo "[preflight] All checks passed"
```

---

## Missing dependency detection

The clever bit. Scan `import` statements across the project, compare against declared deps, surface gaps.

```python
# Rough sketch — Codex authors the full script per AGENTS.md hard rule #5
import ast, pathlib
imports = set()
for path in pathlib.Path('.').rglob('*.py'):
    if 'venv' in path.parts or '.tox' in path.parts:
        continue
    try:
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split('.')[0])
    except SyntaxError:
        continue
# Filter stdlib; check rest against requirements
```

Catches the classic "added `import httpx` but forgot to add `httpx` to requirements.txt" mistake.

---

## CI alignment

Check `.github/workflows/` for what CI actually runs. Preflight should mirror it.

```bash
# Look for CI config to align with
ls .github/workflows/*.yml 2>/dev/null | head -1
```

If CI uses `tox`, `nox`, `make test`, or a custom script, preflight should run that instead of raw pytest. Match what CI does, not what's "standard." Otherwise preflight passes and CI fails — defeating the point.

---

## Failure handling

When a check fails, surface the exact output and stop. Don't try to auto-fix in preflight — that's `qa`'s job (and routes through Codex). The user decides:

- Fix manually
- Dispatch fix to Codex
- Override and push anyway (rare; the user should have a reason)

Don't ship past a failed preflight by default. The whole point is to catch CI fails early.

---

## Cost shape

- Fully local commands — trivial cost
- Time is dominated by pytest runtime (project-dependent, seconds to minutes)
- Zero AI inference unless dispatching a fix afterward
- Cache friendly — re-running after a small edit is fast

---

## Pairing patterns

- Always paired with `ship` (auto-fires before it for Python)
- Pairs with `review` — preflight catches lint/test issues, review catches logic/security issues. Different layers.
- Doesn't pair with `qa` directly — qa runs on the deployed app, preflight runs on the local code

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| ruff complains about rules CI doesn't check | Ruff config out of sync with CI | Align pyproject.toml's ruff config with what CI runs |
| pytest passes locally, fails in CI | Environment difference (Python version, OS, env vars) | Check CI matrix; replicate locally with same Python version |
| pip check finds issues that don't break CI | False positive on a dev-only dep | Move to dev extras in pyproject.toml |
| Preflight slow | Whole-project pytest | Add `--lf` (last failed) flag for incremental runs |

---

## See also

- [SKILL.md](../SKILL.md) — pipeline mechanic
- [ship.md](ship.md) — what runs after preflight passes
- [review.md](review.md) — separate review layer (logic + security, vs preflight's lint + tests)
