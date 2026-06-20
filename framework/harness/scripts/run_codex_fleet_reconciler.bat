@echo off
REM On-demand / triggered entry point for the codex fleet reconciler (one sweep per run).
REM Do NOT register as a recurring Scheduled Task — AGENTS.md hard rule #1 forbids background polling.
REM Run manually or from a user-initiated dashboard action only.
REM Output goes to ~/.claude/logs/codex-fleet-reconciler.log (the script handles its own logging).
python "C:\Users\<you>\.claude\scripts\codex_fleet_reconciler.py" 1>nul 2>>"C:\Users\<you>\.claude\logs\codex-fleet-reconciler.stderr.log"
