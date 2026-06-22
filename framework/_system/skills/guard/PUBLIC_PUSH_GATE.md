# Public Push Gate

The guard mechanic installs a global Git `pre-push` hook that blocks pushes to public GitHub repositories unless the public safety gate passes.

## What Is Gated

- Public GitHub push targets: gated fail-closed.
- Private GitHub repos: skipped, including missing repos that have not been created yet.
- Non-GitHub remotes: skipped.
- Private-to-public visibility flips: use `scripts/gh-publicize.ps1`, which runs the same gate before calling `gh repo edit --visibility public`.

The gate is trigger-based. It runs only when a human pushes or asks the wrapper to flip visibility; it is not a background job.

## What It Checks

- `gitleaks` over the commit range being pushed.
- Denylisted personal data in changed file paths, changed file contents, and reachable commit metadata.
- Codex non-interactive review for fuzzy PII or safety concerns that deterministic scans may miss.

Any deterministic secret or denylist hit is an automatic failure. Codex prose cannot override those findings.

## Override

For a single deliberate push or publicize operation:

```powershell
$env:GUARD_ALLOW_PUBLIC_PUSH = "1"
git push origin main
Remove-Item Env:\GUARD_ALLOW_PUBLIC_PUSH
```

The hook prints a loud bypass banner. Do not set this variable globally.

## Disable

To disable the global hook path:

```powershell
git config --global --unset core.hooksPath
```

To re-enable:

```powershell
git config --global core.hooksPath "C:/Users/<you>/Desktop/AI_Projects/_system/skills/guard/githooks"
```

## Local Hook Chaining

Because `core.hooksPath` overrides each repo's `.git/hooks`, the global hook chains the repo-local `.git/hooks/pre-push` after the public gate passes. If the local hook exits non-zero, the push still fails.

## Test Hooks

The gate accepts test-only controls:

- `GUARD_FORCE_VISIBILITY=PUBLIC|PRIVATE|MISSING`
- `GUARD_FORCE_OWNER_REPO=owner/repo`

Use them only with local bare repositories or wrapper stubs. Never push planted secrets or PII to a real GitHub repository.
