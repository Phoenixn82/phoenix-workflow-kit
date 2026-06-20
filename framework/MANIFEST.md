# The user's AI Workflow Framework -- package contents

A portable copy of the mechanic/wrench skill system + the Claude<->Codex bridge.
PRIVATE DATA IS EXCLUDED: the second-brain vault content (projects, decisions, business
data), all secrets/keys, ~/.codex auth+config, .env files, and runtime logs/state are NOT here.

## Layout
- AGENTS.md ............. operating manual (hard rules, mechanic/wrench philosophy, brain-lane split)
- SKILLS_INDEX.md ....... one line per callable surface (the menu)
- DECISION_MAP.md ....... task -> tool routing
- CLAUDE.md ............. per-project session loader
- RELIABILITY_STANDARD.md  the "works every time" build standard
- _system/skills/ ...... every mechanic (SKILL.md) + its wrenches/ + scripts/   <-- the core
- _system/tool-parity/ . the Claude<->Codex tool 1:1 parity checker
- _system/verify-bridge.py  read-only regression gate for the bridge
- harness/CLAUDE.global.md  cross-project rules (the philosophy)
- harness/settings.reference.json  hook wiring + permission model (adapt paths to your machine)
- harness/skills/codex-goal-dispatcher/  autonomous /goal dispatcher (incl. hands-free `codex exec` --headless mode)
- harness/hooks/ ....... the Claude<->Codex bridge hooks + secret-firewall
- harness/scripts/ ..... helper scripts (freellmapi router, cloak scraper, skill mirror, codex turn-notify, ...)
- agentic-os/aos_lock.py  cross-session file-lock (so two AIs don't clobber each other)
- agentic-os/spawn-args.ts  how the desktop OS spawns Claude/Codex/FreeLLMAPI headless

## Note on paths
Scripts hardcode C:\Users\<you>\... -- that's the original author's machine. Your AI should
rewrite paths for your environment (the pamphlet's setup prompt walks through this).

## How to use this
Open phoenix-workflow-pamphlet.html, read the philosophy, then paste the "implementation
prompt" from the pamphlet into your Claude or Codex along with this zip.
