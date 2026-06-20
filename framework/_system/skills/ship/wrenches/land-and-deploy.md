---
name: ship-land-and-deploy
description: The atomic land-it step. Merges the PR, waits for CI to pass, waits for deploy to complete, verifies production health, then kicks off post-deploy wrenches (canary, benchmark, pay-for-this). Reads project deploy config from CLAUDE.md (set up via setup-deploy). Trigger phrases include "land it", "merge and deploy", "merge this PR", "deploy this", "ship it to production", "merge and verify", "land and watch".
---

# ship-land-and-deploy — merge + wait + verify

After `review` approves and the user says go, this wrench handles the actual merge-to-production atomically: merge the PR, wait for CI, wait for the deploy pipeline, verify the live URL responds, kick off post-deploy monitoring.

Reads deploy platform config from the project's CLAUDE.md (written by `setup-deploy` on first run). Without that config, falls back to detection heuristics.

---

## When to fire

- After `review` passes and the user gives explicit go-ahead
- Direct: "land it" / "merge and deploy" / "ship it to production"
- Resume case: if a previous `land-and-deploy` started but didn't finish (PR merged but deploy still pending), pick up at the wait step

Don't fire when:
- `review` hasn't passed (push back; run review first)
- The user hasn't given the explicit yes to merge to main (per AGENTS.md hard rule #2)
- The PR has unresolved review comments from a human reviewer
- CI is currently red on the PR (wait for it to go green first, or have the user override)

---

## Sequence

```
1. Verify go conditions
   - PR exists and is open
   - review wrench verdict was LAND or the user override
   - The user has said yes to merge
   - CI on the PR is green (or the user said override)

2. Merge the PR
   - `gh pr merge <num> --squash` (default; or --merge / --rebase per project convention)
   - The user can specify merge strategy; default to project's existing pattern

3. Wait for CI on main
   - Poll `gh run list --branch main --limit 1`
   - Timeout after platform-specific window (default 15 min)

4. Wait for deploy
   - Platform-specific: Vercel deployment URL polling, Fly machine status, GHA workflow, etc.
   - Surface deploy progress every 30s (don't spam every 5s)

5. Verify production health
   - HTTP HEAD on the production URL → expect 200
   - Hit the project's health endpoint if defined (/health, /api/health, /_status)
   - One sanity page-render check (production responds with expected content marker)

6. Kick off post-deploy wrenches
   - Trigger canary (monitoring window)
   - Trigger benchmark (perf regression check)
   - Trigger pay-for-this (paying-user audit)
   - Run in parallel via the Agent tool

7. Surface result to the user
   - Merge commit SHA
   - Deploy URL
   - Post-deploy status (canary running, benchmark scheduled, pay-for-this dispatched)
```

---

## Deploy platform detection

Reads project CLAUDE.md for the block written by `setup-deploy`:

```markdown
## Deploy configuration
- **Platform:** Vercel
- **Production URL:** https://example.app
- **Health endpoint:** /api/health
- **Deploy status command:** `vercel inspect <deployment-url>`
- **Default merge strategy:** squash
```

If CLAUDE.md has no such block, fall back to detection:

| Signal | Platform | How to check status |
|---|---|---|
| `vercel.json` | Vercel | `vercel deployments list --limit 1` |
| `netlify.toml` | Netlify | `netlify status` |
| `fly.toml` | Fly | `fly status` |
| `Procfile` + `app.json` | Heroku | `heroku releases:info` |
| `render.yaml` | Render | Webhook poll or dashboard |
| `.github/workflows/deploy.yml` | GHA | `gh run list --workflow deploy.yml --limit 1` |
| Custom | Custom | Push back to the user; ask for status command |

If detection fails and CLAUDE.md isn't configured, run `setup-deploy` first.

---

## Wait-and-verify discipline

**Don't claim "deployed" without evidence.** Per the global CLAUDE.md full-stack verification rule:

1. Merge commit visible on main: `git log origin/main --oneline -1`
2. Deploy platform reports SUCCESS (not PENDING, not BUILDING)
3. Production URL returns 200 with expected content
4. (Optional) DB / API health check passes if the project defines one

A green CI checkmark alone is NOT "deployed." Walk the chain. Same discipline as full-stack verification when answering "how do I know it worked?" — DB → API → DOM → screenshot. For deploys: merge → build → deploy → URL response.

---

## Merge strategy

Default to the project's existing pattern (read `gh pr list --json mergeStateStatus --limit 5` to see how prior PRs were merged). If no clear convention:

- **Squash** — feature branch merges, default for most projects
- **Merge commit** — when keeping individual commits matters (open-source projects, audit trails)
- **Rebase** — when projects use a linear history convention

The user can override with `--strategy=squash|merge|rebase`.

---

## Post-deploy parallel dispatch

After health verification, three wrenches fire in parallel via the Agent tool:

```
Agent: canary --url <prod-url> --window 30m
Agent: benchmark --url <prod-url> --baseline <pre-deploy-baseline>
Agent: pay-for-this --url <prod-url>
```

They run independently. Their results return separately. The user sees three deltas: monitoring status, perf delta, paying-user verdict.

---

## Resume across sessions

If `land-and-deploy` started but didn't finish (the user closed the session mid-deploy), the wrench can resume. State is written to `.ship-state.json` (dot-prefixed) in the project root by `../scripts/ship-state.py`:

```json
{
  "pipeline_id": "ship-2026-05-28T14-23-00Z",
  "started_at": "2026-05-28T14:23:00+00:00",
  "branch": "feat/some-work",
  "base": "main",
  "stages": {
    "tests":  { "status": "passed",  "at": "2026-05-28T14:10:00+00:00" },
    "review": { "status": "passed",  "at": "2026-05-28T14:15:00+00:00" },
    "pr":     { "status": "passed",  "at": "2026-05-28T14:20:00+00:00" },
    "merge":  { "status": "passed",  "at": "2026-05-28T14:23:00+00:00" },
    "deploy": { "status": "pending", "at": null },
    "canary": { "status": "pending", "at": null }
  }
}
```

On next invocation, read this file (`ship-state.py get`) and resume at the first stage still `pending`. The Helper-scripts table below has the exact read/advance/close commands.

---

## Failure handling

| Failure | What to do |
|---|---|
| CI goes red after merge | Surface; offer to revert the merge (the user decides) |
| Deploy fails / times out | Surface deploy logs (`gh run view`, `vercel inspect`, etc.) |
| Production URL returns 5xx after deploy | Stop. Don't fire post-deploy wrenches. Surface to the user immediately |
| Production health check fails | Same — stop, surface, don't run canary on a broken deploy |
| Post-deploy wrench dispatch fails | Continue and surface partial result — don't block on a benchmark failure |

---

## Cost shape

- Merge + wait = mostly polling, very cheap
- Health verification = small number of HTTP requests
- Parallel post-deploy = each wrench's cost (canary medium, benchmark medium, pay-for-this medium)
- Total cost is dominated by what fires after the land, not the land itself

---

## Safety rules (load-bearing)

- Never merge without the user's explicit yes (per AGENTS.md hard rule #2)
- Never force-merge over a red CI without the user's override
- Never skip post-deploy verification — a "deploy succeeded" without URL check is not proven
- Never auto-revert on deploy failure — surface and let the user decide

---

## Helper scripts

| Stage | Script | What it does |
|---|---|---|
| Pipeline state read | `../scripts/ship-state.py get` | Returns the current `.ship-state.json` so land-and-deploy knows which stage advanced. |
| Stage advance | `../scripts/ship-state.py set <stage> --value '<json>'` | Updates `merge`, `deploy`, `canary` stage entries atomically as land-and-deploy progresses. |
| Pipeline close | `../scripts/ship-state.py reset` | Archives the state to `.ship-state-archive/<pipeline_id>.json` after canary passes. |

Acceptance-tested on 2026-05-28. Spec: `PHASE_5_DISPATCH.md` § 5.3.

---

## See also

- [SKILL.md](../SKILL.md) — pipeline mechanic
- [ship.md](ship.md) — what fed the PR
- [review.md](review.md) — what must pass first
- [setup-deploy.md](setup-deploy.md) — one-time platform config that land-and-deploy reads
- [canary.md](canary.md) / [benchmark.md](benchmark.md) / [pay-for-this.md](pay-for-this.md) — post-deploy parallel dispatch targets
