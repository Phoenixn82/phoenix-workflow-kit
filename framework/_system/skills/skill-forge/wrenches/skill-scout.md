---
name: skill-forge-skill-scout
description: Skill search wrench. Indexes every SKILL.md under _system/skills/, ranks local matches against query via TF-IDF over name / description / trigger phrases. Flags trigger-phrase conflicts between installed skills. Falls back to curated external registries (anthropics/skills, superpowers, findskills.org, awesome-claude-skills, SkillsMP) when nothing local fits. Trigger phrases include "find a skill for", "what skills do I have", "is there a skill that", "install a skill for", "skill for X", "skill scout", "recommend a skill", "do I already have a skill", "browse my skills".
---

# skill-forge-skill-scout — skill search

When the user is about to ask "do I have a skill for X" or "should I add a skill for Y," this wrench answers. Fast TF-IDF over the installed stack.

---

## When to fire

- "Find a skill for X" / "is there a skill that"
- "What skills do I have for [domain]"
- Before `aos-add-a-skill` to check for overlap
- When `skill-creator` runs to verify trigger phrases don't conflict with existing

Don't fire when:
- The user knows the skill name (just invoke it)
- The user is asking conceptually ("how should I X") — that's planning, not skill search

---

## TF-IDF ranking

For a query, the wrench ranks installed skills by:

1. Match against skill `name` (highest weight)
2. Match against skill `description`
3. Match against trigger phrases in description
4. Match against body content (lowest weight, expensive to load)

Returns top 3-5 with scores. Format:

```markdown
## skill-scout results for "<query>"

1. **<skill name>** (score: 0.87) — <description excerpt>
2. **<skill name>** (score: 0.64) — <description excerpt>
3. **<skill name>** (score: 0.41) — <description excerpt>

### Conflicts detected
- "<phrase>" triggers both skill A and skill B — flag for resolution
```

---

## Conflict detection

Two skills shouldn't fire on the same trigger phrase. The wrench scans all installed skills and flags overlapping trigger phrases:

```
Conflict: "audit my code"
- skill-forge-skill-scout matches via "audit"
- angry-code-auditor matches via "audit my code"
- Recommend: skill-scout's trigger phrase should be more specific
```

These conflicts get logged to `_system/second-brain/Actions/skill-conflicts.md` so the user sees the pattern over time.

---

## External fallback

When local search returns nothing relevant (top score < 0.3), the wrench falls back to a curated list of external registries:

- `anthropics/skills` GitHub
- `superpowers` plugin
- `findskills.org`
- `awesome-claude-skills` lists
- `SkillsMP`

External results don't auto-install; they're surfaced for the user to consider.

---

## See also

- [SKILL.md](../SKILL.md)
- [aos-add-a-skill.md](aos-add-a-skill.md) — uses skill-scout for overlap check
- [skill-creator.md](skill-creator.md) — uses skill-scout to verify routing
- [mirror-skills-to-codex.md](mirror-skills-to-codex.md) — keeps Codex side searchable too
