---
name: skill-forge
description: Skill stack maintenance mechanic. Scaffolds new skills, builds MCPs, searches existing skills for matches, mirrors Claude skills to Codex (junction-based sync), runs critique gate before any new skill is created. Owns the skill-intake flow per AGENTS.md Future-Claude skill intake. NOT printing-press-router (that's standalone per DECISIONS_LOCKED). Trigger phrases include "build a skill", "create a skill", "find a skill", "make an MCP", "MCP for X", "scaffold MCP", "mirror skills", "search my skills", "is there a skill that", "what skills do I have", "critique this skill idea".
---

# skill-forge — skill stack maintenance

The lane where new skills get scaffolded (critique-then-build), existing skills get searched, and the Claude → Codex skill mirror gets maintained.

Per AGENTS.md Future-Claude skill intake (Step 0): always read `_system/second-brain/Mechanics/<mechanic>/state.md` before proposing a new skill. The mechanic-state axis exists to prevent skill duplication and overlap.

---

## Cardinals

1. **Critique BEFORE scaffold.** New skills must justify themselves via `aos-add-a-skill` first. If it overlaps an existing wrench / mechanic, fold in. If it's not solving a real recurring need, kill it. Only after critique passes does `skill-creator` actually write files.

2. **Find-before-build.** Run `skill-scout` before creating anything new. If a similar skill exists, use it / extend it. Only when nothing fits does scaffolding happen.

3. **Mirror to Codex via junctions.** the user's Codex skill directory mirrors Claude's via Windows junction points. PostToolUse hook auto-creates junctions when new skills land. Audit / bulk re-sync available via `mirror-skills-to-codex` direct.

4. **State files stay current.** When a wrench is added / removed / its trigger phrases change, `skill-forge` updates `_system/second-brain/Mechanics/<mechanic>/state.md`. Future-Claude reads these on Step 0.

5. **NOT printing-press-router.** That's a standalone keeper per the user's lock. It fires whenever a task touches a third-party service (CLI > API > MCP ladder). It's not inside skill-forge.

---

## When this fires

- "Build a skill for X" / "create a skill"
- "Find a skill for X" / "is there a skill that"
- "Make an MCP for X" / "scaffold an MCP"
- "Mirror skills to Codex" / "audit skill drift"
- "Critique this skill idea" / "should I add a skill for"
- A recurring pattern the user has been hand-grinding 3+ times across sessions

---

## Picking the wrench

| Shape of the ask | Wrench |
|---|---|
| Critique gate before any scaffold | `aos-add-a-skill` |
| Scaffold a new skill (after critique passes) | `skill-creator` |
| Build a Model Context Protocol server | `mcp-builder` |
| Search for existing skill matches | `skill-scout` |
| Mirror Claude skills to Codex | `mirror-skills-to-codex` |

---

## Cross-mechanic dependencies

- **`second-brain`** for mechanic-state files + skill intake history
- **`router`** for any Codex code-writing when scaffold needs implementation
- **`printing-press-router`** (standalone keeper) for any third-party service in the new skill — fires first on any "build X integration" intent

---

## What skill-forge does NOT do

- Does not fire `printing-press-router` (separate standalone)
- Does not auto-create skills without critique gate passing
- Does not silently mirror without a clear delta — surfaces what changed
- Does not replace user judgement — skills get created only when the user says go

---

## Wrenches

| Wrench | Path | What it does |
|---|---|---|
| **aos-add-a-skill** | `wrenches/aos-add-a-skill.md` | Critique gate. Brutally honest "should this skill exist" review |
| **skill-creator** | `wrenches/skill-creator.md` | Scaffolds the actual files after critique passes |
| **mcp-builder** | `wrenches/mcp-builder.md` | FastMCP / TypeScript SDK scaffold for MCP servers |
| **skill-scout** | `wrenches/skill-scout.md` | TF-IDF search across installed skills + external registries |
| **mirror-skills-to-codex** | `wrenches/mirror-skills-to-codex.md` | Junction-based Claude → Codex skill sync |

---

## See also

- [wrenches/aos-add-a-skill.md](wrenches/aos-add-a-skill.md) — critique gate
- [wrenches/skill-creator.md](wrenches/skill-creator.md) — scaffold
- [wrenches/mcp-builder.md](wrenches/mcp-builder.md) — MCP server scaffold
- [wrenches/skill-scout.md](wrenches/skill-scout.md) — find existing skills
- [wrenches/mirror-skills-to-codex.md](wrenches/mirror-skills-to-codex.md) — Codex mirror
- [`AGENTS.md`](../../../AGENTS.md) — Future-Claude skill intake flow (Step 0 reads mechanic state)
- [`printing-press-router`](../printing-press-router/) — separate standalone (NOT in skill-forge)
