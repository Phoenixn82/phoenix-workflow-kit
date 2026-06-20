#!/usr/bin/env python3
"""
codex_fleet_reconciler.py — OS-level babysitter for every Codex /goal run on the box.

What it does (every fire):
  1. Walks <AI_Projects>/**/pipeline/goal-runs/*/status.json
  2. Cross-references each in-progress goal's recorded node_pid (and parent pid)
     against the live process list — node.exe with codex.js in its command line.
  3. If node_pid is dead AND status.json still reads in-progress/spawned/spawning:
       - writes status.reconciler_note = "process died: detected at <iso>"
       - if attempts.log shows recent progress (<10 min) the run likely completed
         and status.json was just never finalized → mark status "complete-inferred"
       - else mark status "process-died-no-final-status"
  4. If node_pid is alive but status.json untouched for >30 min AND attempts.log
     also stale: mark status.reconciler_note = "possibly stalled — no progress
     since <iso>". Iron rule: NEVER kill or restart anything.
  5. Writes a single summary file at ~/.claude/codex-fleet-status.json that
     enumerates every known goal-run, alive/dead state, and any reconciliation
     applied this fire. The agentic_os dashboard reads this file.

Triggered/manual only — run on demand when reconciling the fleet (e.g. from the
agentic_os dashboard action or a user-initiated check). Do NOT register this as
a recurring Scheduled Task: AGENTS.md hard rule #1 forbids anything that polls/runs
on its own while the user is away. The turn-based codex-activity bridge is the
standing awareness mechanism; this reconciler is the explicit, on-demand sweep.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECTS_ROOT = Path(os.environ.get("AI_PROJECTS_ROOT", r"C:\Users\<you>\Desktop\AI_Projects"))
FLEET_STATUS = Path(r"C:\Users\<you>\.claude\codex-fleet-status.json")
LOG_FILE = Path(r"C:\Users\<you>\.claude\logs\codex-fleet-reconciler.log")

IN_FLIGHT_STATES = {"spawning", "spawned", "in-progress", "in_progress", "watching", "paused-budget"}
STALL_THRESHOLD_MIN = 30
COMPLETE_INFER_THRESHOLD_MIN = 10


def iso_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def log(msg: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{iso_now()}] {msg}\n")


def list_codex_node_pids() -> dict[int, dict]:
    """Return {pid: {started_iso, cpu_seconds, working_set_mb}} for live codex node procs."""
    out: dict[int, dict] = {}
    if os.name != "nt":
        return out
    try:
        raw = subprocess.check_output(
            [
                "powershell", "-NoProfile", "-Command",
                "Get-CimInstance Win32_Process -Filter \"Name='node.exe'\" | "
                "Where-Object { $_.CommandLine -match 'codex' -and $_.CommandLine -match 'enable goals' } | "
                "ForEach-Object { "
                "  $p = Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue; "
                "  \"$($_.ProcessId)|$($_.CreationDate.ToString('o'))|$($p.CPU)|$($p.WorkingSet64)\" "
                "}"
            ],
            text=True, stderr=subprocess.DEVNULL, timeout=10,
        )
    except Exception as e:
        log(f"list_codex_node_pids failed: {e}")
        return out
    for line in raw.splitlines():
        line = line.strip()
        if "|" not in line:
            continue
        parts = line.split("|")
        if len(parts) < 4:
            continue
        try:
            pid_i = int(parts[0])
            started = parts[1].strip()
            cpu = float(parts[2]) if parts[2] else 0.0
            ws = int(parts[3]) if parts[3] else 0
        except Exception:
            continue
        out[pid_i] = {
            "started_iso": started,
            "cpu_seconds": cpu,
            "working_set_mb": round(ws / (1024 * 1024), 1),
        }
    return out


def discover_goal_runs() -> list[Path]:
    runs: list[Path] = []
    if not PROJECTS_ROOT.exists():
        return runs
    for status in PROJECTS_ROOT.glob("*/pipeline/goal-runs/*/status.json"):
        runs.append(status)
    # Some projects nest one level deeper (e.g. example_scraper/example-scraper/).
    for status in PROJECTS_ROOT.glob("*/*/pipeline/goal-runs/*/status.json"):
        runs.append(status)
    return runs


def load_status(p: Path) -> dict | None:
    try:
        # utf-8-sig transparently strips a BOM if present; some Codex writes use
        # PowerShell's Set-Content -Encoding utf8 which prepends one.
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception as e:
        log(f"load_status failed {p}: {e}")
        return None


def save_status_text(p: Path, text: str) -> None:
    # Always write plain utf-8 (no BOM) so future readers don't need utf-8-sig.
    p.write_text(text, encoding="utf-8")


def save_status(p: Path, data: dict) -> None:
    try:
        save_status_text(p, json.dumps(data, indent=2))
    except Exception as e:
        log(f"save_status failed {p}: {e}")


def attempts_log_mtime(run_dir: Path) -> _dt.datetime | None:
    log_p = run_dir / "attempts.log"
    if not log_p.exists():
        return None
    try:
        return _dt.datetime.fromtimestamp(log_p.stat().st_mtime, tz=_dt.timezone.utc)
    except Exception:
        return None


def status_mtime(p: Path) -> _dt.datetime:
    return _dt.datetime.fromtimestamp(p.stat().st_mtime, tz=_dt.timezone.utc)


def reconcile_one(status_path: Path, live_node_pids: dict[int, dict]) -> dict:
    """Reconcile a single goal-run. Returns a fleet-summary entry."""
    data = load_status(status_path)
    if data is None:
        return {"status_path": str(status_path), "error": "unreadable"}

    run_dir = status_path.parent
    cur_status = (data.get("status") or "").strip()
    node_pid = data.get("node_pid")
    parent_pid = data.get("pid")
    goal_id = data.get("goal_id", run_dir.name)
    project_dir = data.get("project_dir") or str(run_dir.parents[2])

    summary = {
        "goal_id": goal_id,
        "project_dir": project_dir,
        "status_path": str(status_path),
        "status": cur_status,
        "node_pid": node_pid,
        "parent_pid": parent_pid,
        "node_alive": False,
        "node_cpu_seconds": None,
        "attempts_log_age_min": None,
        "status_age_min": round((_dt.datetime.now(_dt.timezone.utc) - status_mtime(status_path)).total_seconds() / 60, 1),
        "reconciler_action": None,
        "reconciler_note": None,
    }

    if node_pid and node_pid in live_node_pids:
        summary["node_alive"] = True
        summary["node_cpu_seconds"] = live_node_pids[node_pid]["cpu_seconds"]

    ats = attempts_log_mtime(run_dir)
    if ats is not None:
        summary["attempts_log_age_min"] = round(
            (_dt.datetime.now(_dt.timezone.utc) - ats).total_seconds() / 60, 1
        )

    if cur_status not in IN_FLIGHT_STATES:
        return summary

    # In-flight goal — apply reconciliation rules.
    if not summary["node_alive"]:
        # Node is dead. Decide: completed-but-unfinalized vs died-without-status.
        if summary["attempts_log_age_min"] is not None and summary["attempts_log_age_min"] <= COMPLETE_INFER_THRESHOLD_MIN:
            new_status = "complete-inferred"
            note = (
                f"Codex node {node_pid} died but attempts.log shows progress "
                f"within {COMPLETE_INFER_THRESHOLD_MIN} min. Likely completed without "
                f"writing final status. Reviewed by reconciler at {iso_now()}."
            )
        else:
            new_status = "process-died-no-final-status"
            note = (
                f"Codex node {node_pid} not alive. attempts.log age: "
                f"{summary['attempts_log_age_min']} min. Status frozen at "
                f"'{cur_status}'. Recorded by reconciler at {iso_now()}."
            )
        data["status"] = new_status
        data.setdefault("reconciler_history", []).append({
            "at": iso_now(),
            "from_status": cur_status,
            "to_status": new_status,
            "note": note,
        })
        data["reconciler_note"] = note
        data["reconciler_last_check"] = iso_now()
        save_status(status_path, data)
        summary["status"] = new_status
        summary["reconciler_action"] = "marked-dead"
        summary["reconciler_note"] = note
        log(f"reconciled DEAD {goal_id}: {cur_status} -> {new_status}")
        return summary

    # Node alive — check for stall (untouched status + stale attempts).
    if summary["status_age_min"] > STALL_THRESHOLD_MIN:
        stale_attempts = (
            summary["attempts_log_age_min"] is None
            or summary["attempts_log_age_min"] > STALL_THRESHOLD_MIN
        )
        if stale_attempts:
            note = (
                f"Possibly stalled — status.json untouched for "
                f"{summary['status_age_min']} min, attempts.log age "
                f"{summary['attempts_log_age_min']} min. Iron rule: NOT killing. "
                f"Surface to the user to decide. Recorded at {iso_now()}."
            )
            data["reconciler_note"] = note
            data["reconciler_last_check"] = iso_now()
            save_status(status_path, data)
            summary["reconciler_action"] = "flagged-stall"
            summary["reconciler_note"] = note
            log(f"flagged STALL {goal_id}: {summary['status_age_min']} min idle")
            return summary

    # Healthy in-flight — just record the heartbeat.
    data["reconciler_last_check"] = iso_now()
    save_status(status_path, data)
    summary["reconciler_action"] = "healthy"
    return summary


def main() -> int:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log("--- reconciler fire ---")

    live = list_codex_node_pids()
    log(f"live codex node procs: {len(live)} pids={list(live.keys())}")

    runs = discover_goal_runs()
    log(f"discovered {len(runs)} goal-runs")

    entries = []
    for r in runs:
        entries.append(reconcile_one(r, live))

    fleet = {
        "generated_at": iso_now(),
        "live_codex_nodes": [
            {"pid": pid, **info} for pid, info in live.items()
        ],
        "total_goal_runs": len(runs),
        "in_flight": sum(1 for e in entries if e.get("status") in IN_FLIGHT_STATES),
        "alive": sum(1 for e in entries if e.get("node_alive")),
        "newly_dead_this_fire": sum(1 for e in entries if e.get("reconciler_action") == "marked-dead"),
        "stall_flags_this_fire": sum(1 for e in entries if e.get("reconciler_action") == "flagged-stall"),
        "stale_pids": [pid for pid in live if not any(e.get("node_pid") == pid for e in entries)],
        "entries": entries,
    }

    FLEET_STATUS.parent.mkdir(parents=True, exist_ok=True)
    FLEET_STATUS.write_text(json.dumps(fleet, indent=2), encoding="utf-8")
    log(
        f"fleet summary: in_flight={fleet['in_flight']} alive={fleet['alive']} "
        f"newly_dead={fleet['newly_dead_this_fire']} stalls={fleet['stall_flags_this_fire']}"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log(f"FATAL: {e}")
        sys.exit(1)
