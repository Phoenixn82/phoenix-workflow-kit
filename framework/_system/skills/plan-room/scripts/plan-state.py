"""Persistent state across plan-room sessions.

Spec: _archive/claude_projects_2026-05-pre-rebuild/Rebuild/PHASE_5_DISPATCH.md § 6.1 (archive only)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_FILENAME = ".plan-state.json"
ARCHIVE_DIRNAME = ".plan-state-archive"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _state_path(root: Path) -> Path:
    return root / STATE_FILENAME


def _empty_state(project: str) -> dict:
    now = _now_iso()
    ts = now.replace(":", "-").replace("+00-00", "Z")
    return {
        "session_id": f"plan-{ts}",
        "project": project,
        "started_at": now,
        "phase": "intake",
        "intake": {"questions_answered": [], "brief_emitted": False},
        "loadout": {"plugins": [], "mcps": [], "skills": []},
        "autoplan": {
            "lenses_run": [],
            "auto_decisions": [],
            "judgment_calls_surfaced": [],
            "approval_gate_passed": False,
        },
    }


def _load(root: Path) -> dict:
    p = _state_path(root)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save(root: Path, data: dict) -> None:
    p = _state_path(root)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(p)


def _get_field(data: dict, dot_path: str):
    parts = dot_path.split(".")
    cur = data
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur


def _set_field(data: dict, dot_path: str, value) -> None:
    parts = dot_path.split(".")
    cur = data
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["get", "set", "init", "complete"])
    ap.add_argument("--project", default=None)
    ap.add_argument("--field", default=None, help="dot-path, e.g. intake.brief_emitted")
    ap.add_argument("--value", default=None, help="JSON value for set")
    ap.add_argument("--root", type=Path, default=Path.cwd())
    args = ap.parse_args()

    root = args.root.resolve()

    if args.action == "init":
        if not args.project:
            print("--project required for init", file=sys.stderr)
            return 1
        state = _empty_state(args.project)
        _save(root, state)
        print(json.dumps(state, indent=2))
        return 0

    if args.action == "complete":
        state = _load(root)
        if not state:
            return 0
        archive_dir = root / ARCHIVE_DIRNAME
        archive_dir.mkdir(parents=True, exist_ok=True)
        sid = state.get("session_id", f"plan-unknown-{_now_iso()}")
        (archive_dir / f"{sid}.json").write_text(
            json.dumps(state, indent=2), encoding="utf-8"
        )
        _state_path(root).unlink(missing_ok=True)
        return 0

    state = _load(root)
    if not state:
        print("no plan-state — run init first", file=sys.stderr)
        return 1

    if args.action == "get":
        if args.field:
            print(json.dumps(_get_field(state, args.field), indent=2, default=str))
        else:
            print(json.dumps(state, indent=2))
        return 0

    if args.action == "set":
        if not args.field or args.value is None:
            print("--field and --value required for set", file=sys.stderr)
            return 1
        try:
            v = json.loads(args.value)
        except json.JSONDecodeError:
            v = args.value
        _set_field(state, args.field, v)
        _save(root, state)
        print(json.dumps(_get_field(state, args.field), indent=2, default=str))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
