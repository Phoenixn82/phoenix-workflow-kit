#!/usr/bin/env bash
# Sniff project root for deploy platform fingerprints.
# Spec: PHASE_5_DISPATCH.md § 5.1

set -uo pipefail

root="${1:-.}"

if [ ! -d "$root" ]; then
  echo "unknown"
  exit 0
fi

if [ -f "$root/fly.toml" ]; then echo "fly.io"; exit 0; fi
if [ -f "$root/vercel.json" ] || ls "$root"/next.config.* >/dev/null 2>&1; then echo "vercel"; exit 0; fi
if [ -f "$root/netlify.toml" ] || [ -f "$root/_redirects" ]; then echo "netlify"; exit 0; fi
if [ -f "$root/render.yaml" ]; then echo "render"; exit 0; fi
if [ -f "$root/Procfile" ] && [ -f "$root/app.json" ]; then echo "heroku"; exit 0; fi
if ls "$root"/.github/workflows/*deploy*.yml >/dev/null 2>&1 || ls "$root"/.github/workflows/*deploy*.yaml >/dev/null 2>&1; then echo "github-actions"; exit 0; fi
if [ -f "$root/Dockerfile" ] && [ -f "$root/docker-compose.yml" ]; then echo "docker-self-host"; exit 0; fi

echo "unknown"
exit 0
