---
name: plan-room-project-loadout
description: Right-sizes plugins / MCPs / skills for the project's stated scope. Minimum set, not maximum. Reads the project brief, proposes the MINIMUM capabilities needed, asks the user to confirm before disabling anything. Re-invoke when scope materially shifts (new feature area, new technology, pivot). Never silently removes capability mid-project. Trigger phrases include "loadout", "right-size capabilities", "what plugins do I need", "/loadout", "trim my MCPs", "starting fresh", "new project", "scope changed".
---

# plan-room-project-loadout — capability right-sizing

The user's harness has dozens of plugins, MCPs, and skills installed. Most projects need a fraction. This wrench reads the project brief and proposes the minimum set needed for the scope, then asks the user to confirm before disabling anything.

This is the cost-control discipline. Loading everything every session is the bloat path. Right-sizing per project is the avoidance.

---

## When to fire

- After `project-brief-generator` emits the project's CLAUDE.md
- When scope changes materially (new feature area, new technology, pivot)
- Direct: "/loadout" / "right-size capabilities" / "what plugins do I need"
- After the user installs new tools and wants to know which apply

Don't fire when:
- Mid-project mid-feature (don't reshuffle capabilities while the user is debugging)
- The project is so small that loadout is over-engineering
- The user explicitly says "load everything" (override allowed, but flag it)

---

## The proposal rule (load-bearing)

The wrench PROPOSES; the user confirms. Never silently removes capability mid-project.

Format:

```markdown
## Loadout proposal for <project>

### Minimum capabilities needed
- <plugin / MCP / skill> — <why it's in the set>
- ...

### Currently enabled but NOT needed
- <plugin / MCP / skill> — <why it's not needed for this scope>
- ...

### Proposed action
Disable [list of currently-enabled-but-not-needed]
Keep [list of minimum capabilities]

The user: approve / edit / override
```

If the user approves, the wrench writes the changes. If he edits, the proposal updates and re-asks. If he overrides, the wrench logs the override reason in second-brain.

---

## Capability detection per scope signal

| Scope signal | Required capabilities |
|---|---|
| Python backend | `python-ci-preflight` wrench, Python plugins, `pytest` |
| Web frontend | `chrome-devtools-mcp`, `vercel:*` if Vercel deploy, `design-studio` |
| Mobile build | `build/wrenches/mobile`, possibly `windows-launcher` if the user uses Windows |
| Scraping | `web-scrape` mechanic, Firecrawl auth, Cloak Browser auth |
| Long-context reading | `router/wrenches/gemini`, Gemini CLI |
| Bulk grunt work | `router/wrenches/freellmapi`, FreeLLMAPI local |
| Deep research | `router/wrenches/gemini` + Deep Research path |
| Security-critical | `cso` standalone keeper |
| SEO work | `seo` mechanic |
| Design work | `design-studio` mechanic |
| Content production | `content-forge` mechanic |
| Vault / second brain | `second-brain` mechanic (always-core; no choice) |
| Browser-driven QA | `chrome-devtools-mcp`, possibly Playwright |

The wrench reads the project brief and the source files (existing CLAUDE.md, package.json, etc.) to detect scope signals, then maps to the minimum set.

---

## Always-core vs on-demand

Some skills are always loaded (per AGENTS.md): `router`, `second-brain`, `guard`. The loadout never touches these.

Everything else is on-demand. Loadout proposes which on-demand mechanics to leave enabled in this project's settings vs. which to disable for this project.

```
Always-core (never touched by loadout):
- router, second-brain, guard

On-demand (loadout proposes which are needed):
- build, web-scrape, ship, plan-room, design-studio,
  content-forge, seo, morning-briefing, video-scan,
  skill-forge, project-orchestrator (apex)

Standalone keepers (loadout proposes which are needed):
- investigate, cso, context-audit,
  windows-launcher, printing-press-router
```

---

## Re-invocation rules

Re-invoke loadout when:

- New feature area added that crosses into a new capability domain (e.g., adding scraping to a project that didn't have it)
- New technology introduced (e.g., adding mobile to a web-only project)
- Pivot in scope (e.g., the project became a different thing)
- After the user installs new plugins / MCPs / skills that might apply

DON'T re-invoke for:
- Small features within the existing scope
- Performance work on existing capabilities
- Bug fixes
- Mid-debugging or mid-build phases

Loadout is a project-shape decision, not a feature-shape decision.

---

## Override and re-enable

If the user needs a capability temporarily disabled, the wrench surfaces a one-line re-enable later: *"Disabled SEO mechanic for this project. To re-enable later: /loadout — add seo."*

If the user wants to keep a capability loaded that loadout would disable, that's a manual override. Loadout records the override + reason in second-brain so future loadouts respect it.

---

## Output: the action plan

```markdown
## Loadout for <project>

### Enabled in this project's .claude/settings.local.json
- always-core: router, second-brain, guard
- on-demand: build, ship, web-scrape, plan-room
- standalone: investigate, cso

### Disabled in this project (vs harness defaults)
- seo (not in scope)
- design-studio (no UI work for v1)
- content-forge (no content production)
- morning-briefing (project doesn't need synthesis)
- video-scan, skill-forge, project-orchestrator (no use case yet)

### Files to update
- `<project>/.claude/settings.local.json`: disabledMechanics list
- `<project>/CLAUDE.md`: update Loop section to reference enabled mechanics
- `_system/second-brain/Projects/<slug>/loadout.md`: record proposal + the user's decision

Apply? [y/n/edit]
```

---

## settings.local.json shape

The project's `.claude/settings.local.json` gets a `disabledMechanics` entry that the always-core loader respects:

```json
{
  "disabledMechanics": [
    "seo",
    "design-studio",
    "content-forge",
    "morning-briefing",
    "video-scan",
    "skill-forge",
    "project-orchestrator"
  ]
}
```

Future sessions in this project skip loading those mechanics' SKILL.md files. Re-enabling means re-running loadout (or manually editing the file).

---

## Cost shape

- Scope signal detection from project files + brief: small
- Proposal generation: small (mostly mapping)
- The user review + apply: small
- Total: very low. One-time per project (re-runs are rare).

The PAYOFF is large: every future session in the project loads fewer mechanic SKILL.mds. Cumulative savings over the project's lifetime.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Proposed loadout too tight (the user needs something disabled) | Scope signal missed | the user re-runs loadout with the new feature in scope |
| Proposed loadout too loose (still bloated) | Conservative detection | Lower the threshold for "needs this capability" |
| Settings change broke something | Wrong mechanic disabled | Re-enable + the user flags the missed dependency |
| Always-core mechanic somehow ended up in disabled list | Bug | Hard guard: never put router/second-brain/guard in disabledMechanics |

---

## Helper scripts

| Script | What it does |
|---|---|
| `../scripts/loadout-detect.sh [--json] [--scope user\|project]` | Snapshots current plugin / MCP / skill state via `claude` CLI with filesystem fallback. Compute delta against required scope to find what to enable / disable. |

Spec: `_archive/claude_projects_2026-05-pre-rebuild/Rebuild/PHASE_5_DISPATCH.md` § 6.3 (archive only). Note: output is verbose (claude CLI output not parsed tightly) — `Mechanics/plan-room/state.md` flags a polish TODO.

---

## See also

- [SKILL.md](../SKILL.md) — plan-room mechanic
- [project-brief-generator.md](project-brief-generator.md) — runs before loadout (brief informs scope)
- [autoplan.md](autoplan.md) — runs after loadout (reviews against scope + capabilities)
- [`AGENTS.md`](../../../../AGENTS.md) — always-core vs on-demand rule
- [`context-audit`](../../context-audit/) — standalone keeper for ongoing harness hygiene (different lane: audits the global setup, not per-project loadout)
