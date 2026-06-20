#!/usr/bin/env python3
"""Compatibility entrypoint for archived phase gate registration."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ARCHIVED = Path(
    "C:/Users/<you>/Desktop/AI_Projects/_archive/claude_projects_2026-05-pre-rebuild/skills/codex-goal-dispatcher/scripts/phase_gate_register.py"
)

if not ARCHIVED.exists():
    print(f"Archived phase gate register not found: {ARCHIVED}", file=sys.stderr)
    raise SystemExit(1)

runpy.run_path(str(ARCHIVED), run_name="__main__")
