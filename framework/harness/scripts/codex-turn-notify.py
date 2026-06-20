#!/usr/bin/env python3
"""Codex notify wrapper -> shared Claude/Codex activity log.

Codex invokes its `notify` program with the configured array as the leading
argv, then appends ONE final argument: a JSON string describing the event
(turn completion). This wrapper is inserted IN FRONT of the original notify
program so the chain is:

    notify = [ "python", "<this script>", "<ORIGINAL_EXE>", <ORIGINAL_ARGS...>, <CODEX_JSON> ]

Behavior:
  1. Re-invoke the ORIGINAL notify program with the EXACT same args Codex
     passed (everything after this script's path, i.e. original exe + its
     leading args + the JSON payload). This preserves Codex's existing
     computer-use turn-ended behavior byte-for-byte.
  2. Best-effort: parse the JSON payload, resolve a project root, and append a
     one-line `codex turn` entry to that project's .claude-codex-log.md via
     shared_log.py. This is the deterministic Codex side of the bridge.

Hard rule: NEVER break Codex's turn. Any failure in the logging step is
swallowed; the original notify is always launched and the process exits 0.
No secrets are ever read from config or printed.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

# Absolute paths only (no stale shell-folder redirects, no C:\Users\<other-user>).
SHARED_LOG = r"C:\Users\<you>\.claude\skills\codex-goal-dispatcher\scripts\shared_log.py"
FALLBACK_PROJECT = r"C:\Users\<you>\Desktop\AI_Projects"
ERR_LOG = r"C:\Users\<you>\.claude\hooks\logs\codex-turn-notify.err.log"


def _log_err(msg: str) -> None:
    """Best-effort diagnostic; never raises."""
    try:
        os.makedirs(os.path.dirname(ERR_LOG), exist_ok=True)
        import datetime as _dt

        stamp = _dt.datetime.now(_dt.timezone.utc).isoformat()
        with open(ERR_LOG, "a", encoding="utf-8") as fh:
            fh.write(f"[{stamp}] {msg}\n")
    except Exception:
        pass


def _launch_original(original_argv: list[str]) -> None:
    """Run the original notify program with the args Codex passed. Non-blocking.

    original_argv[0] is the original program; the rest are its args (the
    configured leading args plus the appended JSON payload).
    """
    if not original_argv:
        return
    try:
        # Fire-and-forget so we never delay Codex's turn handler. The original
        # program (computer-use turn-ended) manages its own lifecycle.
        subprocess.Popen(original_argv, close_fds=True)
    except Exception as exc:
        _log_err(f"failed to launch original notify: {exc!r}")


def _extract_payload(argv_tail: list[str]) -> dict | None:
    """The Codex JSON payload is the LAST argv element. Fall back to stdin."""
    candidate = None
    if argv_tail:
        candidate = argv_tail[-1]
    if candidate:
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
    # Some notify contracts deliver JSON on stdin instead of argv.
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read()
            if raw and raw.strip():
                obj = json.loads(raw)
                if isinstance(obj, dict):
                    return obj
    except Exception:
        pass
    return None


def _pick(payload: dict, *keys: str) -> str:
    for key in keys:
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
        if val not in (None, "", [], {}):
            return str(val)
    return ""


def _resolve_project(cwd: str) -> str:
    """Use shared_log.py find-project; fall back to the AI_Projects root."""
    if cwd and os.path.isdir(cwd):
        try:
            res = subprocess.run(
                [sys.executable, SHARED_LOG, "find-project", "--cwd", cwd],
                capture_output=True,
                text=True,
                timeout=15,
            )
            root = res.stdout.strip()
            if res.returncode == 0 and root and os.path.isdir(root):
                return root
        except Exception as exc:
            _log_err(f"find-project failed: {exc!r}")
    return FALLBACK_PROJECT


def _append_log(payload: dict) -> None:
    """Append a single `codex turn` line. Best-effort."""
    try:
        if not os.path.isfile(SHARED_LOG):
            _log_err("shared_log.py not found")
            return

        cwd = _pick(payload, "cwd", "workdir", "working_directory", "project")
        project = _resolve_project(cwd)

        # Summary: prefer the model's last message, then a turn id, then type.
        summary = _pick(
            payload,
            "last-assistant-message",
            "last_assistant_message",
            "last-agent-message",
            "message",
            "turn-id",
            "turn_id",
            "turn",
            "type",
        )
        if not summary:
            summary = "turn-ended"

        subprocess.run(
            [
                sys.executable,
                SHARED_LOG,
                "append",
                "--project",
                project,
                "--actor",
                "codex",
                "--action",
                "turn",
                "--summary",
                summary,
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception as exc:
        _log_err(f"append failed: {exc!r}")


def main() -> int:
    # argv[1] = original program, argv[2:] = original args + appended JSON.
    original_argv = sys.argv[1:]

    # 1) Preserve original notify behavior FIRST and unconditionally.
    _launch_original(original_argv)

    # 2) Best-effort shared-log append. Everything below is wrapped so a
    #    failure can never break the turn.
    try:
        payload = _extract_payload(original_argv)
        if payload is not None:
            _append_log(payload)
        else:
            _log_err("no JSON payload parsed from argv/stdin")
    except Exception as exc:
        _log_err(f"main append block failed: {exc!r}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # absolute last resort
        _log_err(f"fatal: {exc!r}")
        sys.exit(0)
