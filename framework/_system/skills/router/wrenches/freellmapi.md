---
name: freellmapi
description: Wrench inside the `router` mechanic. Calls the user's local FreeLLMAPI router (OpenAI-compatible, http://127.0.0.1:3001/v1) for bounded grunt work — bulk classification, per-item transforms, batch translation, low-stakes per-item generation. Fronts ~20 free-tier providers (Qwen, Kimi, GPT-OSS, Gemini Flash, Magistral, MiniMax, Mistral Large, etc.) with health-aware fallback. Auto-fires on grunt signals ("classify these", "tag each", "bulk process", "for each of these N", N > 5 items). Falls through to Codex on junk.
---

# freellmapi — local FreeLLMAPI wrench

The **grunt-work lane.** Bounded, repetitive, low-stakes per-item work that should never burn Claude or Codex tokens.

The user runs a local OpenAI-compatible router at `http://127.0.0.1:3001/v1` (FreeLLMAPI). It fronts ~20 free-tier providers with health-aware strongest-first fallback. Cost per call: **$0**.

---

## When to fire (auto)

The Grunt Rule (from the router mechanic): if the task is a per-item loop of N > 5 bounded, low-stakes operations, this wrench runs the loop. Claude reads the output.

**Fires automatically on:**
- "classify these N items" / "tag each" / "bulk process" / "for each of these"
- N-item simple transforms (regex / format / translation per item)
- Batch translation requests
- Per-item scoring or ranking on bounded criteria
- Pre-classification passes before Claude makes the final judgment call on borderline cases

**Explicit phrases:** "classify these", "tag each", "bulk process", "for each of these N", "grunt work", "low-stakes batch", "use freellm", "use the local router".

---

## When NOT to fire

- Single-task important code generation → `codex` wrench
- Architecture decisions, planning, judgment → Claude
- Long-context reads or multimodal → `gemini` wrench
- Anything the user will commit to a code repo on the first try
- Anything where a wrong answer has real consequences (auth, payments, migrations, prod config)

The free-tier providers are good for bulk, not for one-shot critical output. The auto-fire rule is **"per-item AND bounded AND low-stakes"**, not "this is text-shaped, ship it cheap".

---

## Endpoints

- Dashboard: `http://127.0.0.1:3001/`
- OpenAI-compatible base URL: `http://127.0.0.1:3001/v1`
- Chat endpoint: `http://127.0.0.1:3001/v1/chat/completions`

**Do not** treat this as Claude Code's primary brain. Claude Code's model gateway expects Anthropic-compatible `/v1/messages`; FreeLLMAPI exposes OpenAI-compatible `/v1/chat/completions`. Use this router for side calls and provider-specific work.

---

## Invocation

Use the helper script (fetches the unified local key internally — never prints it):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\Users\<you>\.claude\scripts\freellmapi-chat.ps1" `
  -Task auto -Prompt "Summarize this idea in 5 bullets."
```

**Single-line variant:**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\<you>\.claude\scripts\freellmapi-chat.ps1" -Task code -Prompt "Review this function for edge cases: ..."
```

To pin a specific model ID instead of using a preset:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\<you>\.claude\scripts\freellmapi-chat.ps1" `
  -Model "qwen/qwen3-coder:free" -Prompt "Implement this small helper."
```

---

## Task presets

Pass via `-Task`. The router picks the strongest healthy provider for the preset, with fallback within the preset's class.

| Preset | Lead model | Use for |
|---|---|---|
| `auto` | router picks | Default — let the router choose strongest healthy provider |
| `code` | Qwen3 Coder 480B | Code-shaped grunt work (boilerplate, regex, small transforms) |
| `agent` | Kimi K2.6 | Multi-step grunt loops where the model needs to plan one or two hops |
| `fast` | GPT-OSS 120B (Groq / Cerebras) | Latency-sensitive bulk runs |
| `long` | Gemini 2.5 Flash | Longish per-item context (~50K tokens), still grunt-scale |
| `reason` | Magistral Medium | Classification with non-trivial reasoning per item |
| `creative` | MiniMax M2.5 | Per-item creative generation at scale (taglines, alt copy) |
| `multilingual` | Mistral Large | Bulk translation, multilingual rewrites, cross-lingual summaries |
| `cheap` | Gemini 2.5 Flash Lite | The cheapest tier — high volume, lowest stakes |

---

## Auto-fire + Codex fallback chain

Per the user's directive (2026-05-26), the router fires this wrench **without asking** on grunt signals. If FreeLLMAPI returns junk, errors, or empty content, **automatically fall through to Codex** before bothering the user:

```powershell
try {
  $r = powershell -NoProfile -ExecutionPolicy Bypass `
    -File "C:\Users\<you>\.claude\scripts\freellmapi-chat.ps1" `
    -Task $task -Prompt $prompt
  if (-not $r.content -or $r.content.Trim().Length -lt 1) {
    throw "FreeLLMAPI returned empty content"
  }
  $output = $r.content
} catch {
  # Announce the fallback in one sentence, then dispatch Codex
  # NOTE: pipe $null to close Codex's stdin, or `codex exec` hangs on "Reading additional input from stdin..."
  # NOTE: no --plain flag in codex-cli 0.128 (it errors); plain output is the default
  Write-Host "[router] freellmapi failed ($_); falling through to Codex"
  $output = $null | codex exec --skip-git-repo-check $prompt
}
```

### What counts as "junk" worth retrying on Codex

- Empty content / whitespace only
- Content that clearly doesn't follow the requested format (asked for JSON, got prose; asked for one-line summary, got 20 paragraphs)
- A refusal or "I cannot" response on a benign request
- Provider-level error in the response wrapper

### What DOES NOT trigger fallback

Do not silently fall through on a Codex/Claude-grade task that was **misrouted** to freellmapi in the first place. If the prompt was wrong-tier, fix the routing — don't paper over with retries. Look at the symptom: if the prompt was inherently above grunt-grade, the routing decision was wrong, not the provider.

---

## Provider setup

Open the dashboard at `http://127.0.0.1:3001/`, add provider keys on the Keys page, then use the fallback chain already configured. Priority order for adding keys:

1. OpenRouter
2. Cloudflare Workers AI
3. Google Gemini
4. Groq or Cerebras
5. Mistral
6. SambaNova or Z.ai
7. GitHub Models
8. Ollama Cloud, HuggingFace, or NVIDIA only for explicit experiments

**Keep it single-user and localhost-only.** Do not paste provider keys or the unified key into chat. Avoid Cohere for personal use unless the user has separately confirmed the terms.

### First-time key import

If provider keys aren't imported yet, fill this local ignored file:

```
C:\Users\<you>\Documents\Codex\2026-05-25\tashfeenahmed-freellmapi-https-github-com-tashfeenahmed\provider-keys.local.json
```

Then import:

```powershell
cd "C:\Users\<you>\Documents\Codex\2026-05-25\tashfeenahmed-freellmapi-https-github-com-tashfeenahmed"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\import-provider-keys.ps1"
```

---

## Health check

Before any cross-vendor dispatch, verify the local router is alive:

```bash
curl -s http://127.0.0.1:3001/v1/models 2>/dev/null | head -c 100
```

If it doesn't respond, the router mechanic refuses cross-vendor routing and either asks the user to restart freellmapi or stays on Codex/Claude. **Never silently degrade** — a downed local router should fail loud, not silently fall back to a Claude loop that drains the quota.

---

## Example tasks

**Classify 200 inbound tickets** (one item per call, loop N times):
```powershell
freellmapi-chat.ps1 -Task auto -Prompt "Classify this ticket into one of: bug, feature, support, billing. Return only the category. Ticket: <text>"
```

**Translate 500 short marketing strings to 5 languages** — `multilingual` preset:
```powershell
freellmapi-chat.ps1 -Task multilingual -Prompt "Translate to French. Return only the translation. Source: <string>"
```

**Tag 1,000 vault notes with topic labels** — `reason` preset:
```powershell
freellmapi-chat.ps1 -Task reason -Prompt "Read this note and assign 1-3 topic tags from: <tag list>. Return tags as JSON array. Note: <text>"
```

**Generate alt text for 100 images from filenames + context** — `creative` preset:
```powershell
freellmapi-chat.ps1 -Task creative -Prompt "Write short alt text for this image. Filename: <name>. Context: <page>. Return only the alt text."
```

**Score 50 SERP titles for clickability** — `fast` preset:
```powershell
freellmapi-chat.ps1 -Task fast -Prompt "Score this SERP title 1-10 for clickability. Return only the integer. Title: <text>"
```

**Pre-classify items before Claude makes the final call on borderline ones** — `auto` preset, then Claude reviews the borderline scores.

---

## See also

- [../SKILL.md](../SKILL.md) — the router mechanic (Grunt Rule lives there)
- [codex.md](codex.md) — fallback lane when freellmapi returns junk
- Helper script: `C:\Users\<you>\.claude\scripts\freellmapi-chat.ps1`
- Install dir: `C:\Users\<you>\Documents\Codex\2026-05-25\tashfeenahmed-freellmapi-https-github-com-tashfeenahmed`
