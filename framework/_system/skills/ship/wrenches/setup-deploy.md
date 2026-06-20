---
name: ship-setup-deploy
description: One-time deploy platform detection and configuration. Detects Fly.io / Render / Vercel / Netlify / Heroku / GitHub Actions / custom, gathers production URL + health endpoint + status command, writes a ## Deploy configuration block to the project's CLAUDE.md. Read by land-and-deploy on every subsequent ship. Trigger phrases include "setup deploy", "configure deploy", "how do I deploy with ship", "set up land-and-deploy", "add deploy config", "first time deploying this project".
---

# ship-setup-deploy — one-time platform config

The wrench that turns `land-and-deploy` from "guess and detect every time" into "read CLAUDE.md and act." Runs once per project. After it writes the deploy block, every future ship reads from that block.

---

## When to fire

- First time shipping a new project (`land-and-deploy` finds no Deploy configuration block)
- The user changes deploy platforms and needs to reconfigure
- Direct: "setup deploy" / "configure deployment for this project" / "set up land-and-deploy"

Don't fire when:
- CLAUDE.md already has a working Deploy configuration block (use it)
- The user wants to deploy without configuring (push back; this saves time on every future ship)

---

## Sequence

1. **Detect signals.** Scan the project root for platform indicators:
   - `vercel.json` → Vercel
   - `netlify.toml` or `_redirects` + `.netlify` → Netlify
   - `fly.toml` → Fly.io
   - `render.yaml` → Render
   - `Procfile` + `app.json` (no fly.toml) → Heroku (this is the exact fingerprint `detect-deploy-platform.sh` matches; a lone `Procfile` or `app.yaml` is a weaker manual signal — confirm with the user)
   - `.github/workflows/deploy.yml` → GitHub Actions
   - `Dockerfile` + nothing else → Custom (ask the user what's the target)
   - Nothing → the user is on a custom or new platform; ask
2. **Confirm with the user.** Even with strong signals, surface the detection: *"Detected Vercel via vercel.json. Confirm?"* If wrong, ask which platform.
3. **Gather config.** Ask the user (or detect):
   - Production URL
   - Health endpoint (`/health`, `/api/health`, `/_status`, etc.)
   - Status command (platform-specific CLI invocation)
   - Default merge strategy for this project's PRs
   - Default branch
4. **Write the block to CLAUDE.md.** Append a `## Deploy configuration` section using a consistent template.
5. **Verify.** Run the status command once to confirm it works on the user's machine.

---

## The block written to CLAUDE.md

```markdown
## Deploy configuration

- **Platform:** Vercel
- **Production URL:** https://example.app
- **Production branch:** main
- **Health endpoint:** /api/health
- **Status command:** `vercel inspect $(vercel deployments list --limit 1 --json | jq -r '.[0].url')`
- **Default merge strategy:** squash
- **Deploy trigger:** auto on merge to main (no manual step)
- **Notes:** Preview deploys per PR; production gated by main merge
```

This block is the contract between ship and the deploy platform. `land-and-deploy` reads it; `canary` reads it for the URL to poll; `pay-for-this` reads it for the URL to walk; `benchmark` reads it for the URL to baseline.

---

## Per-platform notes

### Vercel
- Detect: `vercel.json` exists
- Status: `vercel inspect <deployment-url>` shows BUILDING / READY / ERROR
- Deploy URL: each PR gets a preview URL; production at the configured domain
- Health: typical patterns are `/api/health` for Next.js apps

### Netlify
- Detect: `netlify.toml`
- Status: `netlify status` after `netlify link`
- Deploy URL: preview URLs per PR, production at configured domain
- Health: project-specific; ask the user

### Fly.io
- Detect: `fly.toml`
- Status: `fly status` (cwd-bound to project) or `fly status -a <app-name>`
- Health: configured in fly.toml under `[checks]`
- Notes: machines reach steady-state, not deployment-per-PR

### Render
- Detect: `render.yaml`
- Status: webhook or dashboard (no first-class CLI)
- Health: configured per-service

### Heroku-like
- Detect: `Procfile` + `app.json` without fly.toml (the exact fingerprint `detect-deploy-platform.sh` matches; a lone `Procfile` or `app.yaml` is a weaker manual signal)
- Status: `heroku releases:info` for current; `heroku ps` for instances
- Health: configured per dyno

### GitHub Actions
- Detect: `.github/workflows/deploy.yml` (or similar name)
- Status: `gh run list --workflow deploy.yml --limit 1`
- Variable: the workflow's job determines actual deploy target

### Custom
- Push back to the user: "What's the deploy command? What's the status check? What's the production URL?"
- Write whatever he specifies into the block

---

## Failure handling

| Issue | Resolution |
|---|---|
| Multiple platforms detected (e.g., both `vercel.json` and `fly.toml`) | Ask the user which is the actual production target |
| Status command fails | Surface the error; ask the user to either fix auth or specify a different command |
| Health endpoint returns 404 | Ask the user for the correct endpoint or skip health check |
| Custom platform with no clear pattern | Write minimal block (URL + manual confirmation); flag for the user to fill in later |

---

## Cost shape

- Local file detection — trivial
- Status command run once for verification — platform CLI overhead
- File write to CLAUDE.md — trivial
- Total: a one-time minute of setup that saves time on every future ship

---

## Safety rules

- Never overwrite an existing Deploy configuration block silently. If one exists, surface it and ask the user to confirm before changing.
- Never write deploy secrets / API tokens into CLAUDE.md. Only command shapes that read from env vars.
- Never assume a platform — confirm with the user even when detection signal is strong.

---

## Helper scripts

| Step | Script | What it does |
|---|---|---|
| 1. Detect signals | `../scripts/detect-deploy-platform.sh <root>` | One-word output: `fly.io`, `vercel`, `netlify`, `render`, `heroku`, `github-actions`, `docker-self-host`, or `unknown`. First-match-wins fingerprint scan. |
| (optional helper) | `../scripts/detect-base-branch.sh <root>` | Used when the deploy block needs the project's default branch baked in. |

Acceptance-tested on 2026-05-28. Spec: `PHASE_5_DISPATCH.md` § 5.1 + § 5.2.

---

## See also

- [SKILL.md](../SKILL.md) — pipeline mechanic
- [land-and-deploy.md](land-and-deploy.md) — primary reader of the Deploy block
- [canary.md](canary.md) / [benchmark.md](benchmark.md) / [pay-for-this.md](pay-for-this.md) — also read the block for URL + health endpoint
