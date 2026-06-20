---
name: content-forge-prompt-master
description: Turn rough brain-dump into production-grade prompt. Detects multiple intents, routes to right framework (RACE / RISEN / CRISPE / RTF), lints for missing fields, lays out zones for primacy / recency attention, runs TextGrad-style self-critique, emits provider-aware output (XML for Claude, Markdown for OpenAI). Trigger phrases include "write me a prompt", "optimize this prompt", "prompt master", "make a prompt for X", "improve my prompt", "turn this into a prompt", "prompt this".
---

# content-forge-prompt-master — production prompt engineering

The user's rough "I want a prompt that does X" turns into a production-grade structured prompt with attention-zones tuned and provider-specific formatting.

---

## When to fire

- "Write me a prompt for X"
- "Turn this into a production prompt"
- "Optimize this prompt"
- "Make this prompt better"

Don't fire when:
- The prompt is a one-off conversational ask (don't over-engineer)
- The user wants Claude to do the task directly, not engineer a prompt for it

---

## Framework routing

| Framework | When | Shape |
|---|---|---|
| **RACE** | Role / Action / Context / Expectation | Default for most tasks |
| **RISEN** | Role / Instructions / Steps / End-goal / Narrowing | When task is multi-step |
| **CRISPE** | Capacity-role / Insight / Statement / Personality / Experiment | When persona matters |
| **RTF** | Role / Task / Format | Quick one-shot |

The wrench detects intent and picks. Multi-intent prompts get split or sequenced.

---

## Attention zones

Prompts have primacy + recency zones — content at the start and end gets more attention from the model than the middle. The wrench lays out:

- **Top zone:** role + key constraint
- **Middle zone:** context / examples / details
- **Bottom zone:** the actual task + output format

---

## Provider-aware output

| Provider | Format |
|---|---|
| Claude | XML tags (`<context>`, `<task>`, `<output_format>`) |
| OpenAI / Codex | Markdown headers (`## Context`, `## Task`, `## Format`) |
| Gemini | Similar to OpenAI; supports both |
| Anthropic Workbench / SDK | XML preferred |

The wrench asks the user which target (or infers from context) and formats accordingly.

---

## Lint pass

Before output, lint for missing fields:

- Role specified?
- Task clear?
- Output format defined?
- Constraints stated?
- Examples (if few-shot)?
- Failure modes addressed?

Flag missing fields; ask the user or fill with reasonable defaults.

---

## TextGrad-style self-critique

After draft, the wrench critiques itself:

1. Read its own output
2. Ask: where could this prompt fail? What's ambiguous? What's over-specified?
3. Revise based on the critique
4. Surface to the user with revisions noted

One pass. Don't loop forever.

---

## See also

- [SKILL.md](../SKILL.md)
- [marketing.md](marketing.md) — different lane: copy not prompts
- [`router/wrenches/codex.md`](../../router/wrenches/codex.md) — filesystem boundary prompt pattern (Codex)
