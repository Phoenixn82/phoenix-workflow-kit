---
name: skill-forge-mcp-builder
description: MCP server scaffolder. Interviews the user about tools / inputs / outputs / transport / auth, picks FastMCP (Python, default) or TypeScript SDK, emits complete runnable MCP server project — pyproject.toml or package.json, server entrypoint, tests, README, ready-to-paste client config for Claude Desktop / Claude Code / Cursor. Routes through printing-press-router first if it's wrapping a third-party API (CLI > API > MCP ladder). Trigger phrases include "build an MCP", "make an MCP server", "scaffold MCP", "MCP for X", "I need a custom MCP", "create MCP tools", "new MCP server".
---

# skill-forge-mcp-builder — MCP server scaffolder

For when the user needs a new MCP server. Interviews → picks framework → emits a runnable project.

Per AGENTS.md routing: if the MCP wraps a third-party service (API, scraping target, etc.), `printing-press-router` fires FIRST to enforce the CLI > API > MCP ladder. If a CLI exists for the target, the right answer might be a CLI wrapper, not an MCP.

---

## When to fire

- "Build an MCP for X" (after printing-press-router has confirmed MCP is the right tier)
- "Scaffold an MCP server"
- "Custom MCP for our internal API"

Don't fire when:
- Target service has a CLI → printing-press-router picks CLI tier instead
- The user wants to USE an existing MCP, not build one

---

## Sequence

1. **Interview.**
   - What's the MCP for? (purpose / domain)
   - What tools should it expose? (list)
   - Inputs / outputs per tool? (signatures)
   - Transport? (stdio default; HTTP / SSE if remote)
   - Auth? (none / API key / OAuth)
2. **Pick framework.**
   - **FastMCP (Python)** — default. The user's preferred. Faster scaffold.
   - **TypeScript SDK** — when target stack is JS / Node already, or the user specifically wants it.
3. **Generate project.**
   - `pyproject.toml` / `package.json`
   - Server entrypoint with tool definitions
   - Tests for each tool
   - README with install + run + client config snippet
   - `.gitignore`, `.env.example`
4. **Emit client config snippets** for:
   - Claude Code (`~/.claude/mcp.json`)
   - Claude Desktop (`claude_desktop_config.json`)
   - Cursor
   - Anthropic Workbench (if applicable)
5. **Test.** Run the server locally; verify each tool responds.

---

## Per-framework template shape

### FastMCP (Python)

```python
from fastmcp import FastMCP

mcp = FastMCP("<server-name>")

@mcp.tool()
def <tool_name>(<args>) -> <return-type>:
    """<docstring describing the tool>"""
    # implementation
    return <result>

if __name__ == "__main__":
    mcp.run()
```

### TypeScript SDK

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({ name: "<server-name>", version: "1.0.0" });

server.setRequestHandler(...);

const transport = new StdioServerTransport();
await server.connect(transport);
```

---

## Codex writes the implementation

Per AGENTS.md hard rule #5, when the scaffold needs ACTUAL implementation (tool bodies, business logic), Claude specs and Codex writes. The scaffold itself is small and Claude can author.

---

## See also

- [SKILL.md](../SKILL.md)
- [`printing-press-router`](../../printing-press-router/) — must check tier first
- [`AGENTS.md`](../../../../AGENTS.md) — hard rule #5
- [skill-creator.md](skill-creator.md) — different lane: skills not MCPs
