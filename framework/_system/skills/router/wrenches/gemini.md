---
name: gemini
description: Wrench inside the `router` mechanic. Delegates to Google Gemini for READ + ANALYSIS tasks Claude is the wrong tool for — 1M-token context window, native multimodal (one CLI call sees frames AND hears audio AND reads embedded text), grounded research with citations. Uses the user's $20/mo Gemini Advanced subscription (Gemini 2.5 Pro, 5TB storage). **Gemini does NOT write code to files.** For multi-file code work, Gemini reads + analyses + outputs a written spec; Codex (per-file) writes. Fires on "analyse this video", "huge PDF", "200 pages", "1M tokens", "deep research", "@gemini", or auto when the router detects multimodal source > 3 MB or single-task context > 300K tokens.
---

# gemini — Gemini READ + ANALYSIS wrench

Hand off to Google Gemini when the task is too big or too visual for Claude. Gemini is the **long-context, multimodal, grounded-research** lane — **read and analyse, never author code files.**

The user's $20/mo Gemini Advanced subscription unlocks Gemini 2.5 Pro with the larger paid quota and 5TB Google storage. The `gemini` CLI authenticated against his Google account uses that quota automatically — OAuth, no API key needed for the CLI path.

---

## What Gemini does NOT do

**Gemini does not write code to files.** Per the user's directive: even if Codex fails twice on a code spec, the router does NOT escalate to Gemini for the rewrite. Instead, Sonnet re-specs tighter and re-dispatches to Codex. See the router's § Reverse rescue section.

**When multi-file code work needs Gemini's 1M-token window:**
1. **Gemini reads** the whole codebase
2. **Gemini outputs a written spec** — numbered list of files + the exact change needed per file as prose (NOT a diff, NOT code)
3. **Claude reviews** the spec
4. **Codex writes** per-file, one file at a time, working from Gemini's spec

Gemini surfaces what needs to change; Codex writes the change. Always.

---

## Use cases (READ + ANALYSIS only)

| Task | Why Gemini |
|---|---|
| Analyse a video / audio file / PDF | Native multimodal — one call sees frames AND hears audio AND reads embedded text |
| Read a 200-page document or 50,000-line log | 1M-token context window — fits in one shot |
| Audit a 200K-token codebase for a specific code smell | Sonnet would need 20 Read cycles; Gemini surfaces it in one (output: written report, NOT a diff) |
| Identify all callers of a function across the codebase | Outputs the list + per-caller change spec; Codex implements per-file |
| Plan a multi-file refactor | Outputs the file list + the per-file spec; Codex executes per-file |
| Deep research dossier with citations | Gemini Deep Research (via gemini.google.com) returns grounded multi-source synthesis |
| Bulk image analysis (alt text, OCR, scene description) | Multimodal at scale |
| Summarise a 200-page PDF with citations to page numbers | Long-context + grounded |

The router auto-fires Gemini when:
- A `.mp4 .mov .mkv .webm .mp3 .wav .m4a .pdf` over 3 MB is involved
- A single-task context estimate exceeds 300K tokens
- Multi-file code work needs to be SCOPED (Gemini outputs the spec; Codex implements)

---

## Two invocation paths

### Path A: CLI (default)

```bash
# Analyse a video — native multimodal: visual + transcript + embedded text in ONE call
gemini --skip-trust -p "Analyse the video at <PATH>. Return: (1) scene-by-scene visual notes with timestamps, (2) full transcript, (3) any on-screen text or captions you can read. Combine all three into one timestamped report."

# Hand off a giant PDF / log
gemini --skip-trust -p "Summarise this 200-page document at <PATH>: <what you want extracted>. Cite page numbers for every claim."

# Multi-file code SCOPING (NOT writing) — Gemini reads + identifies, Codex writes
gemini --skip-trust -p "Read every file under src/ and identify where X should change to Y. Output a numbered list: filename, line range, and the change as PROSE. DO NOT output code or a diff — this is a planning spec for Codex to implement per-file."
```

The `--skip-trust` flag is required for headless calls — Gemini CLI otherwise blocks on a trusted-folder prompt. Either pass the flag every call (preferred) or set `GEMINI_CLI_TRUST_WORKSPACE=true` as a user env var.

---

## Video + audio: native multimodal in one call

Google Gemini's multimodal is native — **one CLI call ingests visual frames, audio transcript, and any on-screen text simultaneously.** No separate steps for "first get transcript, then analyse frames" — Gemini does it all in one pass.

```bash
gemini --skip-trust -p "Analyse the video at <PATH>. Return:
  1. Scene-by-scene visual notes (what's on screen, timestamps)
  2. Full audio transcript (timestamped, speaker-tagged if possible)
  3. Any on-screen text, captions, or UI elements you can read
  4. A 3-sentence executive summary

Combine all four into one timestamped report."
```

This makes Gemini the right tool for: video summarization, podcast transcription with visual context, screen-recording analysis (UI + narration together), tutorial parsing (steps + spoken explanation), interview transcription with body-language notes.

For raw text-only transcription where visual doesn't matter, the `video-scan` mechanic (yt-dlp + native YouTube captions + Whisper fallback) is cheaper. Use Gemini when visual + audio together matter.

### Path B: MCP `@gemini` syntax

If `~/.claude/mcp.json` has the gemini MCP server wired, Claude can delegate mid-session by addressing Gemini directly:

```
@gemini Review this codebase for performance issues
@gemini Summarize this 50,000 line log file
@gemini Analyze these files and suggest refactors
```

The MCP config:

```json
{
  "mcpServers": {
    "gemini": {
      "command": "npx",
      "args": ["-y", "https://github.com/RLabs-Inc/gemini-mcp.git"],
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY}"
      }
    }
  }
}
```

Restart Claude Code after wiring. Verify with `claude mcp list`. Both paths (CLI + MCP) inherit the user's paid quota.

---

## Models available

| Model ID | When |
|---|---|
| `gemini-2.5-pro` | Default. Best quality + 1M context window. The user's Advanced subscription tier |
| `gemini-2.5-flash` | Fast, lighter quality. Use for bulk passes that don't need Pro depth |
| `gemini-2.0-flash` | Lightest, background tasks (heartbeat summarization, batch tag generation) |

CLI defaults to Pro for Advanced subscribers. Override with `-m gemini-2.5-flash` when speed matters more than depth.

---

## Deep Research sub-path

Deep Research returns grounded multi-source dossiers with inline citations. It's the right tool for "research X and tell me what you find with sources" — but it's **only exposed via gemini.google.com** (the web app), not the CLI.

Drive it via chrome-devtools-mcp:

```
1. mcp__plugin_chrome-devtools-mcp__new_page  → https://gemini.google.com/app
2. mcp__plugin_chrome-devtools-mcp__click  on the "Deep Research" mode toggle
3. mcp__plugin_chrome-devtools-mcp__type_text  the research question
4. mcp__plugin_chrome-devtools-mcp__click  submit
5. Poll with mcp__plugin_chrome-devtools-mcp__wait_for  until the report renders
6. mcp__plugin_chrome-devtools-mcp__get_page_text  → return the dossier
```

**Use the chrome-devtools-mcp browser path sparingly** — every interaction costs Claude tokens (per the cost-first rule, browser drivers are the most expensive scraping tier). For most research, the CLI path is enough.

**Fires on:** "deep research", "research dossier", "grounded synthesis", "multi-source synthesis", "research X with citations".

---

## Output handling

Gemini returns prose. For long-context tasks the output can itself be long. Two patterns:

**Pattern 1: Output to file.** If Gemini's output is > 5KB (full transcripts, long analyses, multi-file change specs), pipe to disk:

```bash
gemini --skip-trust -p "<spec>" > /tmp/gemini-output.txt
```

Then Claude reads the file, extracts what's needed, and acts.

**Pattern 2: Inline (small output).** For one-paragraph summaries, status checks, simple verdicts — let it come back inline.

**Never ask Gemini to return code or a unified diff.** If the deliverable involves writing code, Gemini's job is the SPEC (prose: "in `src/auth.ts` line 47, change the token check from X to Y because Z"). Claude reads the spec, and Codex executes the per-file write. Gemini's output should always be human-readable prose, not source code.

---

## Cost discipline

Gemini Advanced is **$20/mo** with a very generous Pro quota (the user's plan also includes 5TB Google storage). OAuth-based via `gemini` CLI first-run — no API key needed for the CLI path. **Use Pro for anything multimodal or > 100K tokens.** The free Flash fallback exists if Pro quota gets hit (rare).

**Deep Research has its own per-day allowance** via the web UI — don't burn it on questions you can answer with regular Gemini Pro or Claude.

Per the router's cost ordering: **freellm → Gemini → Codex → Claude.** Use Gemini before Codex/Claude on long-context READ or multimodal work. Don't burn Codex on whole-repo reads when Gemini's 1M window fits it in one shot — but remember the output stays as prose/spec for Codex to implement, never as code from Gemini.

---

## Lane fallback

When Gemini fails (quota, timeout, auth blip), the router falls through to Codex (~100K context, supports image input via `-i <FILE>`):

```bash
if ! gemini --skip-trust -p "$PROMPT" < "$INPUT" > "$OUTPUT"; then
  echo "[router] Gemini failed; falling back to Codex"
  codex exec -m gpt-5-codex "$PROMPT" < "$INPUT" > "$OUTPUT" || {
    echo "[router] Codex also failed; falling to Claude"
    claude -p "$PROMPT" < "$INPUT" > "$OUTPUT"
  }
fi
```

This fallback chain is the router mechanic's job to orchestrate, not this wrench's.

---

## Setup checklist

```bash
# Install
npm install -g @google/gemini-cli

# Auth via the user's Google account (the one with $20/mo Gemini Advanced subscription)
gemini

# Verify the user's paid quota is active
gemini --version
```

**The OAuth CLI path is the user's primary access** — no API key needed, the subscription is billed via the Google account login. API keys are only required if also using the MCP `@gemini` delegation path; in that case, get one from Google AI Studio → https://aistudio.google.com/apikey.

---

## See also

- [../SKILL.md](../SKILL.md) — the router mechanic
- [codex.md](codex.md) — escalation lane when Gemini fails
- [freellmapi.md](freellmapi.md) — the cheap bulk lane (when Gemini Flash is overkill)
