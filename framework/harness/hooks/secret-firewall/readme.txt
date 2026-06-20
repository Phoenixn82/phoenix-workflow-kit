SECRET FIREWALL  (installed by Claude, 2026-05-30)
==================================================

Purpose: stop any AI running in Claude Code from reading your API keys /
secrets, and stop secrets from leaking into commits.

Files in this folder:
  block-secrets.py   PreToolUse hook. Blocks Read/Edit/Write/Grep/Glob/Bash
                     calls that try to read a secret file, dump environment
                     variables, or decrypt the .secrets store. This is the
                     real guarantee (it runs BEFORE the tool).
  detect-secrets.py  PostToolUse tripwire. If a secret value slips into tool
                     output, it warns the model not to propagate it. (It
                     cannot un-show it -- Claude Code hooks can't rewrite tool
                     output -- so this is defense-in-depth only.)

What counts as "protected":
  - any .env / *.env file (except .env.example/.sample/.template)
  - provider-keys*.json  (e.g. the FreeLLMAPI vault)
  - ~/.secrets/**  (the DPAPI store)
  - ~/.codex/auth.json, ~/.aws/credentials, ~/.netrc, ~/.npmrc
  - SSH private keys, *.pem / *.pfx / *.p12
  - environment-variable dumps (Get-ChildItem Env:, printenv, $env:*KEY*, ...)

Registered in: ~/.claude/settings.json  (permissions.deny + hooks).

To TEMPORARILY disable (e.g. you want Claude to help edit an .env):
  comment out the PreToolUse entry in ~/.claude/settings.json, or rename this
  folder. Re-enable when done.

Fail-safe: if a hook script errors internally it fails OPEN (allows the call)
so it can never brick your workflow. It only blocks on a confirmed match.
