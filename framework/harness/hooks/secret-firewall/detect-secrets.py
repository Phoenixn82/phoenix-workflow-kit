#!/usr/bin/env python3
"""Secret Firewall - PostToolUse tripwire for Claude Code.

PostToolUse CANNOT rewrite output the model already saw (confirmed via docs),
so this is a behavioral tripwire, NOT a redactor: if a secret-looking value
appears anywhere in the tool result, it appends a warning telling the model
not to propagate it. Defense-in-depth only; the real protection is the
PreToolUse blocker. Field-name-agnostic: scans the entire hook input.

Always exits 0 (never disrupts the run).
"""
import sys, json, re

PATTERNS = [
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"sk-(?:proj|svcacct|admin)-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{60,}\b"),
    re.compile(r"\bsbp_[a-f0-9]{40,}\b"),
    re.compile(r"\bfc-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgsk_[A-Za-z0-9]{40,}\b"),
    re.compile(r"\bhf_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bxai-[A-Za-z0-9]{40,}\b"),
    re.compile(r"\bpplx-[A-Za-z0-9]{32,}\b"),
    re.compile(r"\bre_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bcsk-[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bnvapi-[A-Za-z0-9_\-]{30,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
]

def main():
    raw = sys.stdin.buffer.read().decode("utf-8-sig", errors="replace").strip()
    if not raw:
        sys.exit(0)
    # scan the ENTIRE input so we don't depend on the exact result field name
    blob = raw
    for rx in PATTERNS:
        if rx.search(blob):
            out = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        "SECURITY: a secret-looking value (API key / token / private "
                        "key) appeared in this tool output. Do NOT echo it back, write "
                        "it to any file, include it in a commit, or transmit it. Refer "
                        "to it only by description, and consider telling the user that "
                        "secret was exposed in output and may need rotation."
                    ),
                }
            }
            print(json.dumps(out))
            break
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
