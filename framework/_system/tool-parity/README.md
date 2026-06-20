# Claude/Codex Tool Parity

This folder keeps Codex honest when Claude dispatches a task that names a tool, skill, plugin, or MCP.

## Rule

Before Codex accepts a Claude-dispatched task that asks for a specific tool, run:

```powershell
python C:/Users/<you>/Desktop/AI_Projects/_system/tool-parity/tool_parity.py check <tool-name>
```

If the tool is missing in Codex, repair in this order:

1. Codex native tool or plugin
2. Mirrored Codex skill
3. Existing CLI on PATH
4. Printing Press CLI
5. MCP bridge
6. Mark Claude-only and hand back

Do not pretend a Claude-only skill or MCP is callable from Codex.

## Full Audit

```powershell
python C:/Users/<you>/Desktop/AI_Projects/_system/tool-parity/tool_parity.py audit --write
```

Generated reports:

- `tool-parity-report.md`
- `tool-parity-report.json`

## Repair

```powershell
python C:/Users/<you>/Desktop/AI_Projects/_system/tool-parity/tool_parity.py repair
```

Repair is conservative. It refreshes the Codex-visible Claude skill catalog when possible and reports missing CLIs/plugins/MCPs. It does not blindly install paid tools or unknown third-party integrations.

## Current Bridges

- Gemini: Codex config launches `bridges/gemini_mcp_bridge.py`, which reads Claude's existing Gemini MCP config at runtime without copying the secret into Codex config.
- Supabase: use the official `npx supabase ...` route unless a standalone/Scoop CLI is installed.
- OpenAI Sites: not currently exposed as a callable Codex plugin/tool in this session. Keep it marked partial until `@Sites` or an equivalent tool is actually available.
