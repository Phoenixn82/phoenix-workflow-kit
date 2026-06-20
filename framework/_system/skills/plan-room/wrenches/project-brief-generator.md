---
name: plan-room-project-brief-generator
description: Emits the project's CLAUDE.md operating manual from a brief (output of process-interviewer or office-hours or direct brain-dump). Sub-200-line CLAUDE.md with the B.L.A.S.T. spine (Brief / Loop / Architect / Ship / Tune) and 4 operating principles. Scaffolds memory/ folder. Reads `_system/second-brain/Mechanics/<mechanic>/state.md` to pull current mechanic info into the brief's operating section. Trigger phrases include "generate CLAUDE.md", "scaffold this project", "set up project context", "new project brief", "/brief", "emit the project brain file".
---

# plan-room-project-brief-generator — CLAUDE.md emitter

Turns a brief (the PRD-style output of process-interviewer / office-hours) into the project's own CLAUDE.md. This file becomes the project's operating manual — every future Claude / Codex / Gemini session in this project reads it first.

The output is sub-200 lines by default. CLAUDE.md is read every session in every conversation in this project; bloating it costs tokens forever.

---

## When to fire

- After `process-interviewer` or `office-hours` emit a brief
- Direct: "/brief" / "generate CLAUDE.md" / "scaffold this project"
- When starting a new project and the user has enough context in conversation
- When an existing project lacks a CLAUDE.md (rare; flag and confirm before generating)

Don't fire when:
- Project already has a working CLAUDE.md (surface it, ask the user what to change)
- Brief is too thin (push back to process-interviewer for 2-3 more answers)
- The user is mid-debug or mid-build (intake is upstream)

---

## The B.L.A.S.T. spine

Every project CLAUDE.md follows the same 5-section spine. Within a section, content adapts to the project.

### B — Brief

```markdown
## Brief

**North star:** <one sentence — the why>
**Target user:** <who this serves>
**Success criteria:** <how we know it worked>
**Out of scope:** <bounded explicitly>
**Done condition (v1):** <specific>
```

### L — Loop

```markdown
## Loop

How work happens in this project:

1. <intake pattern for new work — e.g., issues land in GitHub Project board>
2. <planning pattern — e.g., plan-room autoplan before any non-trivial work>
3. <execution pattern — e.g., Codex via router writes; Claude reviews>
4. <ship pattern — e.g., ship pipeline auto-fires; canary windows are 30m>
5. <feedback pattern — e.g., users / the user / metrics; what triggers the next loop>
```

### A — Architect

```markdown
## Architect

**Stack:** <core stack — frontend, backend, data, infra>
**Key decisions:** <decisions already locked, linked to decisions.md>
**Architecture style:** <e.g., monolith, microservices, serverless, edge>
**Data flow:** <one-paragraph description>
**Security stance:** <e.g., cso runs inline during build; authn = X; secrets in env>
```

### S — Ship

```markdown
## Ship

**Deploy platform:** <e.g., Vercel; or "see Deploy configuration block below">
**Deploy trigger:** <e.g., auto on merge to main>
**Production URL:** <https://...>
**CI:** <e.g., GitHub Actions running ruff + pytest>
**Release cadence:** <e.g., continuous; or weekly batches>

## Deploy configuration
<the block written by setup-deploy, if it exists>
```

### T — Tune

```markdown
## Tune

**What to optimize over time:**
- <metric or quality bar that drives iteration>
- <observability hook — perf trend, error rate, user feedback>

**Known tech debt:** <linked to tech-debt.md if it exists>
**Open loops:** <linked to open-loops.md>
```

---

## The 4 operating principles

Every CLAUDE.md also includes 4 operating principles tailored to the project. These are the project-level equivalent of the global `~/.claude/CLAUDE.md` defaults — they tell future sessions how to behave in this specific project.

Common project-level principles:

```markdown
## Operating principles for this project

1. **<Discipline 1>** — e.g., "Every change touches a test. No exceptions."
2. **<Discipline 2>** — e.g., "Database migrations need migration-safety review (cso); never deploy raw SQL changes."
3. **<Discipline 3>** — e.g., "User-facing copy goes through humanizer before ship."
4. **<Discipline 4>** — e.g., "Mobile UX > desktop. Test mobile first."
```

The wrench picks 4 from the brief + project shape. The user can edit before committing.

---

## Sub-200-line constraint

The point of CLAUDE.md is to load fast every session. Bloat compounds. Constraints:

- Hard cap: 250 lines (warn at 200)
- B.L.A.S.T. sections: ~30 lines each, less if the project's small
- Operating principles: ~5-10 lines per principle, 4 principles max
- No multi-paragraph rationale — link to decisions.md for the "why"
- No code samples — link to source
- No long lists — bullet points should be one line each

If a section needs more space, write it as a linked doc:

```markdown
## Architect

**Stack:** Next.js / Postgres / Vercel
**See:** [docs/architecture.md](docs/architecture.md) for diagrams and data flow detail
**Key decisions:** [decisions.md](decisions.md)
```

Linked docs aren't subject to the 200-line cap. CLAUDE.md is the index, not the encyclopedia.

---

## Memory folder scaffold

Alongside CLAUDE.md, the wrench scaffolds:

```
<project>/
  CLAUDE.md                  ← emitted by this wrench
  memory/
    decisions.md             ← linked from CLAUDE.md "Architect"
    open-loops.md            ← linked from CLAUDE.md "Tune"
    tech-debt.md             ← (created lazily on first entry)
    status.md                ← linked from CLAUDE.md "Tune"
```

Each starts with the AI-first frontmatter + an empty body. Future captures (via second-brain mechanic) populate them.

---

## Mechanic state read

Per AGENTS.md skill-intake Step 0, this wrench reads `_system/second-brain/Mechanics/*/state.md` to pull current mechanic info into the CLAUDE.md "Loop" section. So if the user's project will use `web-scrape`, the Loop section can reference what web-scrape currently does + which wrenches.

This keeps project CLAUDE.md docs from referencing stale or imagined skill structures.

---

## Detection from brain-dump

If the user did NOT run process-interviewer and instead just brain-dumped, this wrench can extract the brief inline from the dump:

```
1. Parse dump for the 10 standard answers (north star, user, JTBD, stack, ...)
2. For each answer found in the dump, accept
3. For each answer NOT in the dump, generate a recommended answer + ASK the user one at a time
4. Emit the CLAUDE.md when all 10 are answered (fully or partially)
```

This is the "5-question interview" referenced in the legacy `project-brief-generator` skill: it asks only what's missing, not the full list.

---

## Verification before write

Show the user a draft of the full CLAUDE.md before writing. The user edits inline. Only on his approve does the file land.

```
[Claude shows full draft]
"Approve as-is? Or what would you change?"
[the user: approve / edit lines X-Y / cut section Z / etc.]
[Claude applies edits, asks for re-approval if substantial]
[Claude writes CLAUDE.md + scaffolds memory/]
```

Never write CLAUDE.md silently. It's the project's operating manual; the user should always read it before it lands.

---

## Cost shape

- Read brief + the user's preferences + mechanic state = small
- Generate CLAUDE.md draft = medium (one Claude pass, opinionated)
- The user review + edits = conversational
- Write files = small

Total: low-medium per project. One-time cost; the file lives forever.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Generated CLAUDE.md is too long | Captured too much rationale inline | Move sections to linked docs; cut to bullet points |
| Operating principles feel generic | Brief was thin on specifics | Push back to process-interviewer for one more question on constraints/risks |
| the user wants to edit every section | Recommendations were too soft | Make B.L.A.S.T. fills more opinionated |
| Existing CLAUDE.md overwritten by mistake | Silent generate | Always show draft + ask explicit approval; never silent-write |

---

## See also

- [SKILL.md](../SKILL.md) — plan-room mechanic
- [process-interviewer.md](process-interviewer.md) — primary upstream wrench
- [office-hours.md](office-hours.md) — secondary upstream (when intake came via pressure-test)
- [project-loadout.md](project-loadout.md) — runs after this wrench
- [`AGENTS.md`](../../../../AGENTS.md) — skill-intake Step 0 (read mechanic state before scaffolding)
