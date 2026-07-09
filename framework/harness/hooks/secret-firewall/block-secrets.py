#!/usr/bin/env python3
"""Secret Firewall - PreToolUse hook for Claude Code.

Blocks the model from reading secret files / dumping env / decrypting the
DPAPI store. PREVENTION is the guarantee (PostToolUse cannot scrub output),
so this runs BEFORE the tool and DENIES via the documented JSON method
(hookSpecificOutput.permissionDecision = "deny", exit 0). Also emits the
legacy {"decision":"block"} key for older CLI builds, and a stderr reason.

Fail-OPEN on internal error (never bricks the workflow); fail-CLOSED on a
confirmed match.

Registered for tools: Read, Edit, MultiEdit, Write, Grep, Glob, Bash, PowerShell, NotebookEdit.
"""
import sys, os, json, re, fnmatch, posixpath

def norm(p):
    if not p:
        return ""
    return str(p).replace("\\", "/").lower()

def basename(p):
    return posixpath.basename(norm(p).rstrip("/"))

ENV_OK_SUFFIX = (".example", ".sample", ".template", ".dist", ".md")

def is_protected_path(p):
    n = norm(p)
    if not n:
        return None
    b = basename(n)
    if "/.secrets/" in n or n.endswith("/.secrets"):
        return "the encrypted secret store (.secrets)"
    if b == ".env" or (b.startswith(".env.") and not b.endswith(ENV_OK_SUFFIX)):
        return "an environment/secrets file (.env)"
    if b.endswith(".env") and b != ".env" and not b.endswith(ENV_OK_SUFFIX):
        return "an environment/secrets file (*.env)"
    if fnmatch.fnmatch(b, "provider-keys*.json") or fnmatch.fnmatch(b, "*secrets*.local.json"):
        return "a provider-key vault file"
    if n.endswith("/.codex/auth.json") or (b == "auth.json" and "/.codex/" in n):
        return "the Codex auth/session file"
    if n.endswith("/.claude/mcp.json"):
        return "the user-level MCP config (embeds API keys)"
    if n.endswith("/.aws/credentials") or b == ".netrc" or n.endswith("/.npmrc"):
        return "a cloud/registry credential file"
    if b in ("id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"):
        return "an SSH private key"
    if b.endswith((".pem", ".pfx", ".p12")):
        return "a private key / certificate file"
    return None

# ---- Bash command screening ------------------------------------------------
# Verbs that actually READ a file's contents (into context) or move it off-box.
# Pure output verbs (echo / write-output / write-host / out-string) are NOT here:
# they can't read a file, so including them only causes false positives on
# scripts that merely mention ".env" in a message. Env-var exfil via echo is
# caught separately by ENV_DUMP ($env:*token*).
READ_VERBS = r"(?:cat|type|gc|get-content|more|bat|head|tail|sed|awk|strings|" \
             r"select-string|format-hex|python|python3|node|deno|bun|rg|grep|" \
             r"findstr|copy|cp|move|mv)"
SECRET_FILE_HINT = r"(?:\.env(?![\w.])|\.env\.(?!example|sample|template|dist)" \
                   r"|provider-keys|/\.secrets/|\\\.secrets\\|\.codex[\\/]auth\.json" \
                   r"|\.claude[\\/]mcp\.json" \
                   r"|\.aws[\\/]credentials|\.netrc|id_rsa|id_ed25519|\.pem\b|\.pfx\b)"
ENV_DUMP = re.compile(
    r"(?ix)(?:"
    r"(?:get-childitem|gci|ls|dir|get-item)\s+env:"
    r"|\bprintenv\b|\bgenv\b"
    r"|^\s*env\s*$|^\s*set\s*$"
    r"|\$env:\w*(?:key|token|secret|password|passwd|cred)\w*"
    r")"
)
DECRYPT_HINT = re.compile(
    r"(?ix)(?:"
    r"unprotect-?data|protecteddata|unprotect-secret"
    # The `secret` helper invocation: the verb must be the next token after the
    # `secret`/`secret.ps1` command (e.g. `secret run ...`, `secret get ...`).
    # Requiring adjacency stops benign commands that merely mention a path like
    # `secret-firewall` and contain an unrelated later word ("run", "get") from
    # tripping the firewall (the hyphen in `secret-firewall` is a word boundary).
    r"|\bsecret(?:\.ps1)?\s+(?:get|show|reveal|export|run|decrypt|dump)\b"
    r")"
)

def screen_bash(cmd):
    if re.search(r"(?is)" + READ_VERBS + r"[^\n|;]*" + SECRET_FILE_HINT, cmd):
        return "reads a protected secret file"
    if re.search(r"(?i)[/\\]\.secrets([/\\]|\b)", cmd):
        return "accesses the encrypted secret store (.secrets)"
    if ENV_DUMP.search(cmd):
        return "enumerates environment variables (may contain secret tokens)"
    if DECRYPT_HINT.search(cmd):
        return "attempts to decrypt secrets via DPAPI / the secret helper"
    return None

def deny(reason):
    msg = ("BLOCKED by secret-firewall: this call " + reason + ". API keys/"
           "secrets must never be read into the model context. If a secret "
           "value is genuinely needed, ask the user to provide/rotate it "
           "directly, or have them run `secret run <scope> -- <cmd>` (injected "
           "into the child process, never shown to the model).")
    out = {
        "decision": "block",          # legacy key (older CLI builds)
        "reason": msg,
        "hookSpecificOutput": {       # current documented key
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": msg,
        },
    }
    sys.stdout.write(json.dumps(out))
    sys.stdout.flush()
    sys.stderr.write(msg)            # belt-and-suspenders for exit-2 builds
    sys.exit(0)

def main():
    raw = sys.stdin.buffer.read().decode("utf-8-sig", errors="replace").strip()
    if not raw:
        sys.exit(0)
    data = json.loads(raw)
    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}

    if tool in ("Bash", "PowerShell"):
        r = screen_bash(str(ti.get("command", "")))
        if r:
            deny(r)
    else:
        for key in ("file_path", "path", "notebook_path"):
            val = ti.get(key)
            if val:
                hit = is_protected_path(val)
                if hit:
                    deny("targets " + hit)
        if tool in ("Grep", "Glob"):
            if is_protected_path(ti.get("pattern", "")):
                deny("targets a protected secret file")
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)  # fail-open: never brick the workflow on a hook error
