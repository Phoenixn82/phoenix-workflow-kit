"""Read/write .ship-state.json — persistent state across ship pipeline.

Spec: PHASE_5_DISPATCH.md § 5.3
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
DETECT_BRANCH = SCRIPT_DIR / "detect-base-branch.sh"
STATE_FILENAME = ".ship-state.json"
ARCHIVE_DIRNAME = ".ship-state-archive"
ARCHIVE_LIMIT = 50

STAGES = ("tests", "review", "pr", "merge", "deploy", "canary")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _state_path(root: Path) -> Path:
    return root / STATE_FILENAME


def _archive_dir(root: Path) -> Path:
    return root / ARCHIVE_DIRNAME


def _current_branch(root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5.0,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def _detect_base(root: Path) -> str:
    try:
        proc = subprocess.run(
            ["bash", str(DETECT_BRANCH), str(root)],
            capture_output=True,
            text=True,
            timeout=5.0,
        )
        return proc.stdout.strip() or "main"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "main"


def _empty_state(root: Path) -> dict:
    now = _now()
    ts = now.replace(":", "-").replace("+00-00", "Z")
    return {
        "pipeline_id": f"ship-{ts}",
        "started_at": now,
        "branch": _current_branch(root),
        "base": _detect_base(root),
        "stages": {s: {"status": "pending", "at": None} for s in STAGES},
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


def _prune_archive(archive_dir: Path) -> None:
    if not archive_dir.exists():
        return
    files = sorted(archive_dir.glob("*.json"), key=lambda f: f.stat().st_mtime)
    while len(files) > ARCHIVE_LIMIT:
        files[0].unlink(missing_ok=True)
        files = files[1:]


def _merge(base: dict, overlay: dict) -> dict:
    result = dict(base)
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _merge(result[k], v)
        else:
            result[k] = v
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["get", "set", "init", "reset"])
    ap.add_argument("stage", nargs="?", default=None)
    ap.add_argument("--value", default=None, help="JSON for set")
    ap.add_argument("--root", type=Path, default=Path.cwd())
    args = ap.parse_args()

    root = args.root.resolve()

    if args.action == "init":
        state = _empty_state(root)
        _save(root, state)
        print(json.dumps(state, indent=2))
        return 0

    if args.action == "reset":
        state = _load(root)
        if state:
            archive_dir = _archive_dir(root)
            archive_dir.mkdir(parents=True, exist_ok=True)
            pid = state.get("pipeline_id", f"ship-unknown-{_now()}")
            (archive_dir / f"{pid}.json").write_text(
                json.dumps(state, indent=2), encoding="utf-8"
            )
            _state_path(root).unlink(missing_ok=True)
            _prune_archive(archive_dir)
        return 0

    state = _load(root)
    if not state:
        print("no ship-state — run init first", file=sys.stderr)
        return 1

    if args.action == "get":
        if args.stage:
            stage = state.get("stages", {}).get(args.stage, None)
            if stage is None:
                print(f"unknown stage: {args.stage}", file=sys.stderr)
                return 1
            print(json.dumps(stage, indent=2))
        else:
            print(json.dumps(state, indent=2))
        return 0

    if args.action == "set":
        if not args.stage:
            print("stage required for set", file=sys.stderr)
            return 1
        if not args.value:
            print("--value required for set", file=sys.stderr)
            return 1
        try:
            overlay = json.loads(args.value)
        except json.JSONDecodeError as e:
            print(f"invalid JSON: {e}", file=sys.stderr)
            return 1
        if args.stage not in STAGES:
            print(f"unknown stage: {args.stage}", file=sys.stderr)
            return 1
        if "at" not in overlay:
            overlay["at"] = _now()
        state["stages"][args.stage] = _merge(state["stages"][args.stage], overlay)
        _save(root, state)
        print(json.dumps(state["stages"][args.stage], indent=2))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
