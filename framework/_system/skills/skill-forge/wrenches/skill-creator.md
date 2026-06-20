---
name: skill-forge-skill-creator
description: Skill scaffolder. Called ONLY after aos-add-a-skill critique gate passes. Generates SKILL.md (or wrench .md) following the AI-first format, right frontmatter, trigger phrases, and correct placement under _system/skills/. Wires into parent mechanic's wrench table when folding in. Trigger phrases include "scaffold this skill", "create the skill files", "skill-creator", "build the skill" (after critique).
---

# skill-forge-skill-creator — skill file scaffolder

The phase 2 of skill creation. Writes the actual files in the right format at the right path.

---

## When to fire

- After `aos-add-a-skill` critique passes AND the user approves
- Direct: "scaffold this skill" (only after critique)

Don't fire when:
- Critique hasn't passed (route to aos-add-a-skill first)
- The user is just exploring the idea (also route to critique gate)

---

## Output format (AI-first)

Every skill file follows the same frontmatter + body shape:

```markdown
---
name: <skill-name>
description: <concise description with trigger phrases inline>
---

# <Skill name> — <one-line tagline>

<Opening paragraph: what this does + when to use it>

---

## When to fire
- <trigger 1>
- <trigger 2>
...

Don't fire when:
- <anti-trigger 1>
- <anti-trigger 2>

---

## <Body sections specific to the skill>

---

## See also
- [related skill 1](path)
- [related skill 2](path)
```

---

## Placement rules

| Shape | Path |
|---|---|
| New wrench in existing mechanic | `_system/skills/<mechanic>/wrenches/<name>.md` |
| New mechanic | `_system/skills/<mechanic>/SKILL.md` (+ folder + wrenches/) |
| New standalone keeper | `_system/skills/<name>/SKILL.md` |

---

## Integration steps

After file is written:

1. Update parent mechanic's `SKILL.md` wrenches table
2. Update parent mechanic's `_system/second-brain/Mechanics/<mechanic>/state.md`
3. Update root `SKILLS_INDEX.md`
4. If routing changes: update `DECISION_MAP.md`
5. Run `skill-scout` to verify trigger phrase routing works

---

## See also

- [SKILL.md](../SKILL.md)
- [aos-add-a-skill.md](aos-add-a-skill.md) — must run before this
- [skill-scout.md](skill-scout.md) — verifies trigger phrases route correctly
- [mirror-skills-to-codex.md](mirror-skills-to-codex.md) — Codex sync after creation
