# Claude/Codex Tool Parity Report

- Total tools tracked: 10
- Codex ready: 9
- Codex partial: 1
- Missing Codex capability: 0
- Claude skills discovered: 136
- Codex skills discovered: 143

## Codex Plugins

browser@openai-bundled, cloudflare@openai-curated, codex-security@openai-curated, documents@openai-primary-runtime, github@openai-curated, hugging-face@openai-curated, openai-developers@openai-curated, presentations@openai-primary-runtime, remotion@openai-curated, spreadsheets@openai-primary-runtime, stripe@openai-curated, superpowers@openai-curated, test-android-apps@openai-curated, vercel-plugin@plugins-cli, vercel@openai-curated

## MCP Servers

- Claude: gemini
- Codex: codegraph, gemini, node_repl

## Priority Tool Routes

| Tool | Status | Codex Ready | Missing | Next Action |
|---|---|---|---|---|
| firecrawl | codex_ready | codex skill, cli: firecrawl | codex mcp: firecrawl | Use Firecrawl CLI if present. If missing, install/configure CLI or route through web-scrape mechanic. |
| printing-press | codex_ready | codex skill, cli: printing-press | - | Go is required for Printing Press Go CLIs. Install Go or configure a bundled Go path, then install/generate PP CLIs. |
| browser | codex_ready | codex plugin: browser@openai-bundled, codex mcp | codex skill prefix: browser:control-in-app-browser, cli: chrome, msedge | Prefer Codex Browser plugin and node_repl browser control. Keep chrome-devtools MCP as Claude-side fallback. |
| github | codex_ready | codex plugin: github@openai-curated, cli: gh | codex skill prefix: github:, codex mcp: github | Use Codex GitHub plugin when exposed, otherwise GitHub CLI. |
| vercel | codex_ready | codex plugin: vercel-plugin@plugins-cli, codex plugin: vercel@openai-curated, cli: vercel | codex skill prefix: vercel-plugin:, codex mcp: vercel | Use Vercel plugin skills and Vercel CLI. Re-auth Vercel MCP if plugin logs invalid_token. |
| supabase | codex_ready | npx: supabase | cli: supabase, codex mcp: supabase | Use the official npx route (`npx supabase ...`) or install the standalone/Scoop CLI. Do not use unsupported global npm install. |
| obsidian | codex_ready | codex skill | codex mcp: obsidian, obsidian-vault | Codex can write the local markdown vault directly. MCP parity is optional; do not dump non-durable session logs. |
| gemini | codex_ready | codex mcp | - | Codex should use the local Gemini MCP bridge when configured; otherwise hand back Gemini-only long-context tasks. |
| google-workspace | codex_ready | codex plugin: documents@openai-primary-runtime, codex plugin: spreadsheets@openai-primary-runtime | codex skill prefix: spreadsheets:, documents:, codex mcp: gmail, google-drive, google-calendar | Use Codex document/spreadsheet plugins for local artifacts. Install Google connectors only when explicitly needed. |
| openai-sites | codex_partial | - | - | OpenAI Sites plugin was not exposed in the checked Codex session. Use @Sites only when the plugin/tool is actually available. |
