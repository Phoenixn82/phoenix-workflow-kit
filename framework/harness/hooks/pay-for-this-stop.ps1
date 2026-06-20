# Stop hook — NEUTERED 2026-05-12.
#
# The previous implementation auto-injected an "AUTONOMOUS MODE — invoke
# pay-for-this skill" prompt back into the session when it detected deploy
# keywords + a recent .git/HEAD change. This worked for interactive the user
# sessions on a real deploy, but caused recurring "stop hook errors" in
# every Claude session that coordinated with Codex (babysitters, /goal
# dispatchers, subagents that happened to have deploy-keyword strings in
# transcript). The injected prompt assumed a project context that didn't
# exist for those sessions, and the resulting tool-call failures surfaced
# as visible stop-hook errors.
#
# Until we have a reliable way to distinguish "the user just deployed" from
# "a Claude agent was coordinating with Codex", this hook is a no-op.
# The original auto-inject implementation was deleted (no .archived-* copy was
# kept; it survives only in ~/.claude/file-history). There is no /pay-for-this
# skill or command anymore — the pay-for-this capability is now a `ship` wrench
# (_system/skills/ship/wrenches/pay-for-this.md), fired by land-and-deploy's
# post-deploy dispatch, not by this hook.

exit 0
