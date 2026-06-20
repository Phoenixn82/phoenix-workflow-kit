#!/usr/bin/env python3
"""
scrub.py - privacy scrub + identity generalization + safety gate for the workflow kit.

Run AFTER sync-kit.ps1 copies live sources into framework/. Operates in-place on a
target dir (default: ../framework relative to this file).

Pipeline (in order):
  1. PATH SCRUB        (deterministic): rewrite real machine paths -> placeholders.
  2. GENERALIZE        (rules-driven): auto-replace operator/personal-identity references
                       with generic forms, per tools/scrub-rules.json. Allowlisted brand/
                       project tokens are sentinel-protected first, so a broad rule can
                       never mangle them.
  3. USERNAME GUARD    (abort): real OS username must not survive the path scrub.
  4. SECRET GUARD      (abort): refuse on a real credential pattern.
  5. PATH GUARD        (abort): refuse if a forbidden private path is staged.
  6. VERIFY GATE       (abort): refuse if any tools/scrub-rules.json verifyDenylist pattern
                       still appears after generalization. THIS is "make all future
                       instances generic via verification when pushing".

The real username is read from the environment at runtime and is NEVER written into this
file, so the committed tooling can't leak it. The generalization ruleset lives in the
separate, reviewable tools/scrub-rules.json.

Exit codes: 0 = clean. 2 = blocked (any guard/gate tripped). The orchestrator must NOT
commit on a non-zero exit.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.path.join(HERE, "scrub-rules.json")

# --- real identity, derived at runtime (no literal username in this file) ---
HOME = os.path.expanduser("~")
USER = os.path.basename(HOME.rstrip("\\/"))
PLACEHOLDER_USER = "<you>"

TEXT_EXT = {
    ".md", ".py", ".ps1", ".ts", ".js", ".mjs", ".json", ".txt", ".sh",
    ".bat", ".html", ".css", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".env",
}


def path_rewrites(user):
    drive = HOME[:2] if len(HOME) > 1 and HOME[1] == ":" else "C:"
    return [
        (f"{drive}\\Users\\{user}", f"{drive}\\Users\\{PLACEHOLDER_USER}"),
        (f"{drive}/Users/{user}",   f"{drive}/Users/{PLACEHOLDER_USER}"),
        (f"/{drive[0].lower()}/Users/{user}", f"/{drive[0].lower()}/Users/{PLACEHOLDER_USER}"),
        (f"\\Users\\{user}", f"\\Users\\{PLACEHOLDER_USER}"),
        (f"/Users/{user}",   f"/Users/{PLACEHOLDER_USER}"),
    ]


# Real-credential signatures (tuned long/high-entropy so the secret-firewall's own
# detection regexes and short doc examples don't false-positive).
SECRET_PATTERNS = [
    re.compile(r"gh[oprs]_[A-Za-z0-9]{36,}"),
    re.compile(r"sk-ant-api\d{2}-[A-Za-z0-9_\-]{80,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"xox[bp]-\d{10,}-\d{10,}-[A-Za-z0-9]{24,}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"AIza[0-9A-Za-z_\-]{35}"),
]

# Private paths that must NEVER appear as files in the shared tree.
# NOTE: the second-brain *skill* (_system/skills/second-brain/) is shippable machinery.
# What's forbidden is the vault *content* at _system/second-brain/ (a different path).
FORBIDDEN_SEGMENTS = {".secrets", "voice-corpus", "claude_vault", ".codex"}


def forbidden_path(rel):
    parts = [p.lower() for p in re.split(r"[\\/]", rel) if p]
    if any(seg in FORBIDDEN_SEGMENTS for seg in parts):
        return True
    if any(p == ".env" or p.startswith(".env.") for p in parts):
        return True
    for i in range(len(parts) - 1):
        a, b = parts[i], parts[i + 1]
        if a == "_system" and b == "second-brain":   # vault CONTENT, not the skill
            return True
        if a == "secret-store" and b == "secrets":    # secret store DATA, not secret.ps1
            return True
    return False


def load_rules():
    if not os.path.isfile(RULES_PATH):
        return {"replacements": [], "allowlist": [], "verifyDenylist": []}, []
    with open(RULES_PATH, "r", encoding="utf-8") as fh:
        rules = json.load(fh)
    warnings = []
    compiled_repl = []
    for r in rules.get("replacements", []):
        flags = 0 if r.get("caseSensitive", True) else re.IGNORECASE
        pat = r["find"] if r.get("isRegex") else re.escape(r["find"])
        try:
            compiled_repl.append((re.compile(pat, flags), r["replace"], r.get("note", "")))
        except re.error as e:
            warnings.append(f"bad replacement regex {r['find']!r}: {e}")
    compiled_deny = []
    for d in rules.get("verifyDenylist", []):
        try:
            compiled_deny.append((re.compile(d["pattern"]), d.get("label", d["pattern"])))
        except re.error as e:
            warnings.append(f"bad denylist regex {d['pattern']!r}: {e}")
    allow = sorted({a["token"] for a in rules.get("allowlist", [])}, key=len, reverse=True)
    return {"replacements": compiled_repl, "allowlist": allow, "verifyDenylist": compiled_deny}, warnings


def generalize(text, rules):
    """Apply path scrub + ruleset replacements, protecting allowlisted tokens with sentinels."""
    # protect allowlisted tokens
    sentinels = {}
    for i, tok in enumerate(rules["allowlist"]):
        s = f"\x00AL{i}\x00"
        if tok in text:
            text = text.replace(tok, s)
            sentinels[s] = tok
    # ruleset replacements
    for pat, repl, _note in rules["replacements"]:
        text = pat.sub(repl, text)
    # restore allowlisted tokens
    for s, tok in sentinels.items():
        text = text.replace(s, tok)
    return text


def iter_text_files(root):
    for dirpath, _dirs, filenames in os.walk(root):
        if ".git" in dirpath.split(os.sep):
            continue
        for name in filenames:
            if os.path.splitext(name)[1].lower() in TEXT_EXT:
                yield os.path.join(dirpath, name)


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "framework")
    target = os.path.abspath(target)
    if not os.path.isdir(target):
        print(f"[scrub] ERROR: target dir not found: {target}")
        return 2

    rules, warnings = load_rules()
    for w in warnings:
        print(f"[scrub] WARN: {w}")
    pathsubs = path_rewrites(USER)
    user_residue = re.compile(rf"\b{re.escape(USER)}\b", re.IGNORECASE) if USER else None

    changed = 0
    residue_hits, secret_hits, path_hits, deny_hits = [], [], [], []

    # Path guard runs over ALL files (even binary) by filename.
    for dirpath, _dirs, files in os.walk(target):
        for name in files:
            rel = os.path.relpath(os.path.join(dirpath, name), target)
            if forbidden_path(rel):
                path_hits.append(rel)

    for f in iter_text_files(target):
        try:
            text = open(f, "r", encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        rel = os.path.relpath(f, target)
        original = text
        for old, new in pathsubs:
            text = text.replace(old, new)
        # Runtime username generalization (portable — tracks the machine, no hardcoded name).
        # Catches forms the path rewrites miss: the slugified project dir (C--Users-<user>-...)
        # and bare prose mentions. The residue guard below verifies none survive.
        if USER and len(USER) >= 4:
            text = re.sub(rf"\b{re.escape(USER)}\b", PLACEHOLDER_USER, text, flags=re.IGNORECASE)
        text = generalize(text, rules)
        if text != original:
            open(f, "w", encoding="utf-8", newline="").write(text)
            changed += 1
        # post-scrub guards (on the rewritten text)
        if user_residue and user_residue.search(text):
            residue_hits.append(rel)
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                secret_hits.append((rel, pat.pattern))
                break
        for pat, label in rules["verifyDenylist"]:
            m = pat.search(text)
            if m:
                deny_hits.append((rel, label, m.group(0)[:60]))

    print(f"[scrub] path scrub + generalization applied to {changed} file(s).")
    if not rules["replacements"]:
        print("[scrub] NOTE: no generalization ruleset loaded (tools/scrub-rules.json missing).")

    blocked = False
    if residue_hits:
        blocked = True
        print("\n[scrub] BLOCK - real username still present after scrub in:")
        for r in sorted(set(residue_hits)):
            print(f"    {r}")
    if secret_hits:
        blocked = True
        print("\n[scrub] BLOCK - possible real credential:")
        for r, p in secret_hits:
            print(f"    {r}   (pattern: {p})")
    if path_hits:
        blocked = True
        print("\n[scrub] BLOCK - forbidden private path staged:")
        for r in sorted(set(path_hits)):
            print(f"    {r}")
    if deny_hits:
        blocked = True
        print("\n[scrub] BLOCK - identity residue survived generalization (verify gate):")
        for r, label, sample in sorted(set(deny_hits)):
            print(f"    {r}   [{label}]  e.g. {sample!r}")

    if blocked:
        print("\n[scrub] RESULT: BLOCKED - do not commit. Resolve the items above.")
        return 2
    print("\n[scrub] RESULT: clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
