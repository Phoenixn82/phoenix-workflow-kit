#!/usr/bin/env python3
r"""verify-bridge.py - re-runnable regression gate for the Claude<->Codex bridge.

user-triggered ONLY. Per AGENTS hard rule #1 there is NO cron and NO scheduled
task behind this - run it by hand:

    python C:\Users\<you>\Desktop\AI_Projects\_system\verify-bridge.py

It re-runs the deterministic E2E checks the 2026-06-12 audit proved, READ-ONLY against
real state. Every round-trip (shared log append/tail, relay check/relay, aos_lock
contention, dispatch smoke) happens inside throwaway temp dirs / unique session ids so
nothing real is mutated and no running codex.exe is disturbed (dispatch runs --no-spawn /
--smoke-test, which never launches Codex).

Drift resilience: the codex binary is resolved DYNAMICALLY (config CODEX_CLI_PATH ->
newest build under %LOCALAPPDATA%\OpenAI\Codex\bin). No build hash is ever hardcoded here.

Output: one PASS / FAIL / INCONCLUSIVE line per check, then a summary.
Exit code: non-zero if any HARD check FAILS. INCONCLUSIVE (an environment dependency is
absent, e.g. the FreeLLMAPI router is not running) never fails the gate - it is reported
honestly and the gate still passes, because the bridge code itself is sound.
"""

from __future__ import annotations

import importlib.util
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

# ---- Fixed, hardcoded real roots (never use OneDrive / GetFolderPath). ----
AI_PROJECTS = Path(r"C:\Users\<you>\Desktop\AI_Projects")
HOME = Path(r"C:\Users\<you>")
CLAUDE_HOME = HOME / ".claude"
CODEX_HOME = HOME / ".codex"

DISPATCH_PY = CLAUDE_HOME / "skills" / "codex-goal-dispatcher" / "scripts" / "dispatch.py"
SHARED_LOG_PY = CLAUDE_HOME / "skills" / "codex-goal-dispatcher" / "scripts" / "shared_log.py"
RELAY_PY = CLAUDE_HOME / "skills" / "codex-goal-dispatcher" / "scripts" / "relay_changes.py"
TOOL_PARITY_PY = AI_PROJECTS / "_system" / "tool-parity" / "tool_parity.py"
PORT_REGISTRY_PY = AI_PROJECTS / "_system" / "skills" / "second-brain" / "scripts" / "port-registry-assign.py"
VAULT_SYNC_PY = AI_PROJECTS / "_system" / "skills" / "second-brain" / "scripts" / "vault-sync.py"
PORTS_MD = AI_PROJECTS / "_system" / "second-brain" / "dev-registry" / "ports.md"
AOS_LOCK_PY = HOME / "agentic-os" / "bin" / "aos_lock.py"
GUARD_CAREFUL_SH = AI_PROJECTS / "_system" / "skills" / "guard" / "scripts" / "check-careful.sh"
GUARD_FREEZE_SH = AI_PROJECTS / "_system" / "skills" / "guard" / "scripts" / "check-freeze.sh"
HOOKS_DIR = CLAUDE_HOME / "hooks"

FREELLM_URL = "http://127.0.0.1:3001/"

# Build-hash drift traps: if these literals show up in LIVE (non-archive, non-doc) bridge
# code, the dispatcher is no longer resolving dynamically. Doc/markdown/audit files are
# allowed to mention them as provenance.
KNOWN_STALE_HASHES = ("f1c7ee7a13db5fed", "fb2111b91430cb17")

PASS, FAIL, INC = "PASS", "FAIL", "INCONCLUSIVE"
results: list[tuple[str, str, str]] = []


def record(name: str, status: str, detail: str = "") -> None:
    results.append((name, status, detail))
    print(f"[{status:^12}] {name}" + (f" -- {detail}" if detail else ""))


def run(args: list[str], timeout: int = 30, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run a child process, capturing bytes and decoding utf-8/replace (Codex emits non-cp1252)."""
    proc = subprocess.run(args, capture_output=True, timeout=timeout, cwd=cwd)
    proc.stdout = (proc.stdout or b"").decode("utf-8", "replace")  # type: ignore[assignment]
    proc.stderr = (proc.stderr or b"").decode("utf-8", "replace")  # type: ignore[assignment]
    return proc


def py(args: list[str], timeout: int = 30, cwd: str | None = None) -> subprocess.CompletedProcess:
    return run([sys.executable, *args], timeout=timeout, cwd=cwd)


# --------------------------------------------------------------------------------------
# Check 1: dispatch.py resolves a real codex.exe + parses config (dynamic, no spawn)
# --------------------------------------------------------------------------------------
def check_dispatch() -> None:
    name = "dispatch.py: resolves real codex.exe + parses config (smoke, no spawn)"
    if not DISPATCH_PY.exists():
        record(name, FAIL, f"missing {DISPATCH_PY}")
        return
    proc = py([str(DISPATCH_PY), "--smoke-test"], timeout=60)
    out = proc.stdout + proc.stderr
    m = re.search(r"\[dispatch\] codex binary:\s*(.+?)\s*\((.+?)\)", out)
    parsed_ok = "parsed config OK" in out or "features list parsed config OK" in out
    if proc.returncode == 0 and m and parsed_ok:
        binpath = m.group(1).strip()
        how = m.group(2).strip()
        is_real = binpath.lower().endswith("codex.exe") and Path(binpath).exists()
        if is_real:
            record(name, PASS, f"resolved {how}; config parsed OK; binary exists")
        else:
            record(name, FAIL, f"resolved binary does not exist or is not codex.exe: {binpath}")
    else:
        record(name, FAIL, f"rc={proc.returncode} parsed_ok={parsed_ok} bin_line={'yes' if m else 'no'}")


# --------------------------------------------------------------------------------------
# Check 2: tool_parity check - no false positives, real tools resolve
# --------------------------------------------------------------------------------------
def check_tool_parity() -> None:
    name = "tool_parity check: real tools resolve, bogus tool is unknown (no false positive)"
    if not TOOL_PARITY_PY.exists():
        record(name, FAIL, f"missing {TOOL_PARITY_PY}")
        return
    # Real tool that must resolve to a Codex-ready route.
    real = py([str(TOOL_PARITY_PY), "check", "node", "--json"], timeout=40)
    # Bogus tool that must NOT be claimed ready (guards against substring false positives).
    bogus_name = "zzz-not-a-real-tool-" + uuid.uuid4().hex[:8]
    bogus = py([str(TOOL_PARITY_PY), "check", bogus_name, "--json"], timeout=40)
    try:
        real_j = json.loads(real.stdout)
        bogus_j = json.loads(bogus.stdout)
    except json.JSONDecodeError as exc:
        record(name, FAIL, f"non-JSON output: {exc}")
        return
    real_ready = real_j.get("status") == "codex_ready"  # exit 0
    bogus_unknown = bogus_j.get("status") == "unknown_tool"  # exit 2, NOT a false match
    if real_ready and bogus_unknown:
        record(name, PASS, f"node->codex_ready; {bogus_name}->unknown_tool")
    else:
        record(name, FAIL, f"node.status={real_j.get('status')} bogus.status={bogus_j.get('status')}")


# --------------------------------------------------------------------------------------
# Check 3: shared_log append/tail round-trip (throwaway temp project)
# --------------------------------------------------------------------------------------
def check_shared_log() -> None:
    name = "shared_log: append/tail round-trip (throwaway temp project)"
    if not SHARED_LOG_PY.exists():
        record(name, FAIL, f"missing {SHARED_LOG_PY}")
        return
    tmp = Path(tempfile.mkdtemp(prefix="vb-sharedlog-"))
    try:
        (tmp / "AGENTS.md").write_text("# temp project for verify-bridge\n", encoding="utf-8")
        token = "vb-marker-" + uuid.uuid4().hex[:10]
        ap = py([str(SHARED_LOG_PY), "append", "--project", str(tmp),
                 "--actor", "claude", "--action", "verify", "--summary", token], timeout=20)
        tl = py([str(SHARED_LOG_PY), "tail", "--project", str(tmp), "--lines", "10"], timeout=20)
        if ap.returncode == 0 and tl.returncode == 0 and token in tl.stdout:
            record(name, PASS, "appended line round-trips through tail")
        else:
            record(name, FAIL, f"append_rc={ap.returncode} tail_rc={tl.returncode} found={token in tl.stdout}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------------------
# Check 4: relay_changes check/relay round-trip (throwaway temp run dir)
# --------------------------------------------------------------------------------------
def check_relay() -> None:
    name = "relay_changes: check->relay->check round-trip flips relayed flag (temp)"
    if not RELAY_PY.exists():
        record(name, FAIL, f"missing {RELAY_PY}")
        return
    tmp = Path(tempfile.mkdtemp(prefix="vb-relay-"))
    try:
        (tmp / "changes.md").write_text(
            "---\noutcome: completed\nrelayed: false\n---\n\n**Outcome:** verify-bridge synthetic manifest.\n",
            encoding="utf-8",
        )
        c1 = py([str(RELAY_PY), "--check", str(tmp)], timeout=15)        # expect rc 0 (unrelayed)
        rl = py([str(RELAY_PY), "--relay", str(tmp)], timeout=15)        # prints outcome, flips flag
        c2 = py([str(RELAY_PY), "--check", str(tmp)], timeout=15)        # expect rc 2 (now relayed)
        flag_now = (tmp / "changes.md").read_text(encoding="utf-8")
        ok = (c1.returncode == 0 and rl.returncode == 0
              and "[OK]" in rl.stdout and c2.returncode == 2
              and re.search(r"(?m)^relayed:\s*true", flag_now))
        if ok:
            record(name, PASS, "check=0 (unrelayed) -> relay prints [OK] -> check=2 (relayed)")
        else:
            record(name, FAIL, f"check1={c1.returncode} relay={rl.returncode} check2={c2.returncode}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------------------
# Check 5: guard check-careful opt-in gate + check-freeze scope (read-only behavior)
# --------------------------------------------------------------------------------------
def _have_bash() -> str | None:
    return shutil.which("bash")


def _permission_decision(raw: str) -> str | None:
    """Extract the permissionDecision verdict from a guard hook's stdout.

    The guard hooks emit strict JSON when `jq` is present, but fall back to a raw
    printf when it is not - and that fallback does NOT escape Windows backslashes in
    the `reason` path, so json.loads chokes on the (otherwise-correct) output. We are
    verifying the VERDICT, not JSON well-formedness, so pull the token directly.
    """
    try:
        return json.loads(raw.strip() or "{}").get("permissionDecision")
    except json.JSONDecodeError:
        m = re.search(r'"permissionDecision"\s*:\s*"(allow|deny|ask)"', raw)
        return m.group(1) if m else None


def check_guard_careful() -> None:
    name = "guard check-careful: opt-in gate (no flag => allow, never 'ask')"
    bash = _have_bash()
    if not bash:
        record(name, INC, "bash not on PATH")
        return
    if not GUARD_CAREFUL_SH.exists():
        record(name, FAIL, f"missing {GUARD_CAREFUL_SH}")
        return
    # We must NOT touch the real flag file. Point HOME at a throwaway dir so the flag is
    # guaranteed-absent => the hook must 'allow' (hard rule #10: default-on never 'ask').
    tmp_home = Path(tempfile.mkdtemp(prefix="vb-guard-home-"))
    try:
        env = dict(os.environ)
        env["HOME"] = str(tmp_home)
        payload = json.dumps({"tool_input": {"command": "rm -rf /"}})
        proc = subprocess.run([bash, str(GUARD_CAREFUL_SH)], input=payload.encode("utf-8"),
                              capture_output=True, timeout=20, env=env)
        out = (proc.stdout or b"").decode("utf-8", "replace")
        verdict = _permission_decision(out)
        if verdict == "allow":
            record(name, PASS, "destructive cmd with no careful flag => allow (correct opt-in gate)")
        else:
            record(name, FAIL, f"expected allow with flag absent, got permissionDecision={verdict!r}")
    finally:
        shutil.rmtree(tmp_home, ignore_errors=True)


def check_guard_freeze() -> None:
    name = "guard check-freeze: scope gate (in-scope=allow, out-of-scope=deny)"
    bash = _have_bash()
    if not bash:
        record(name, INC, "bash not on PATH")
        return
    if not GUARD_FREEZE_SH.exists():
        record(name, FAIL, f"missing {GUARD_FREEZE_SH}")
        return
    tmp_home = Path(tempfile.mkdtemp(prefix="vb-freeze-home-"))
    scope_dir = Path(tempfile.mkdtemp(prefix="vb-freeze-scope-"))
    out_dir = Path(tempfile.mkdtemp(prefix="vb-freeze-out-"))
    try:
        gs = tmp_home / ".claude" / "guard-state"
        gs.mkdir(parents=True, exist_ok=True)
        (gs / "freeze-dir.txt").write_text(str(scope_dir) + "\n", encoding="utf-8")
        env = dict(os.environ)
        env["HOME"] = str(tmp_home)

        def verdict_for(fp: Path) -> str | None:
            payload = json.dumps({"tool_input": {"file_path": str(fp)}})
            proc = subprocess.run([bash, str(GUARD_FREEZE_SH)], input=payload.encode("utf-8"),
                                  capture_output=True, timeout=20, env=env)
            out = (proc.stdout or b"").decode("utf-8", "replace")
            return _permission_decision(out)

        in_scope = verdict_for(scope_dir / "inside.txt")
        out_scope = verdict_for(out_dir / "outside.txt")
        if in_scope == "allow" and out_scope == "deny":
            record(name, PASS, "in-scope edit=allow; out-of-scope edit=deny")
        else:
            record(name, FAIL, f"in_scope={in_scope!r} out_scope={out_scope!r}")
    finally:
        for d in (tmp_home, scope_dir, out_dir):
            shutil.rmtree(d, ignore_errors=True)


# --------------------------------------------------------------------------------------
# Check 6: aos_lock concurrent-write stress (throwaway temp file + unique sessions)
# --------------------------------------------------------------------------------------
def check_aos_lock() -> None:
    name = "aos_lock: concurrent-write stress (one wins, contender BLOCKED, release frees)"
    if not AOS_LOCK_PY.exists():
        record(name, FAIL, f"missing {AOS_LOCK_PY}")
        return
    tmp = Path(tempfile.mkdtemp(prefix="vb-aoslock-"))
    sess_a = "vb-" + uuid.uuid4().hex[:10]
    sess_b = "vb-" + uuid.uuid4().hex[:10]
    target = tmp / "contended.txt"
    try:
        target.write_text("x\n", encoding="utf-8")

        def lock(*a: str, sess: str | None = None) -> subprocess.CompletedProcess:
            return py([str(AOS_LOCK_PY), *a], timeout=25)

        # Seed read fingerprints so acquire passes the stale-read gate (the gate is the
        # reason a naive acquire exits 2; we are testing CONTENTION, not the read gate).
        py([str(AOS_LOCK_PY), "rescue", "fingerprint", "--session", sess_a, "--paths", str(target)], timeout=25)
        py([str(AOS_LOCK_PY), "rescue", "fingerprint", "--session", sess_b, "--paths", str(target)], timeout=25)

        a_acq = py([str(AOS_LOCK_PY), "acquire", str(target), "--session", sess_a,
                    "--agent", "verify-bridge", "--intent", "stress"], timeout=25)
        b_acq = py([str(AOS_LOCK_PY), "acquire", str(target), "--session", sess_b,
                    "--agent", "verify-bridge", "--intent", "stress2"], timeout=25)
        chk = py([str(AOS_LOCK_PY), "check", str(target)], timeout=25)
        try:
            held = json.loads(chk.stdout)
        except json.JSONDecodeError:
            held = {}
        rel = py([str(AOS_LOCK_PY), "release", str(target), "--session", sess_a], timeout=25)

        ok = (a_acq.returncode == 0          # winner acquires
              and b_acq.returncode == 2       # contender denied (mutual exclusion proven)
              and held.get("held") is True
              and held.get("session_id") == sess_a
              and rel.returncode == 0)        # owner releases cleanly
        if ok:
            record(name, PASS, "A acquired, B BLOCKED (rc2), check held by A, A released")
        else:
            record(name, FAIL,
                   f"a_acq={a_acq.returncode} b_acq={b_acq.returncode} "
                   f"held={held.get('held')} owner={held.get('session_id')} rel={rel.returncode}")
    finally:
        # Best-effort cleanup so we never leave a stray lock behind.
        py([str(AOS_LOCK_PY), "release", str(target), "--session", sess_a], timeout=15)
        py([str(AOS_LOCK_PY), "release", str(target), "--session", sess_b], timeout=15)
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------------------
# Check 7: port-registry parses 15 rows / next-free 3090 (READ-ONLY, no --commit)
# --------------------------------------------------------------------------------------
def check_port_registry() -> None:
    name = "port-registry: parses 15 rows / next-free frontend 3090 (read-only, no commit)"
    if not PORT_REGISTRY_PY.exists() or not PORTS_MD.exists():
        record(name, FAIL, f"missing {PORT_REGISTRY_PY if not PORT_REGISTRY_PY.exists() else PORTS_MD}")
        return
    # Row count straight from the source-of-truth file (numeric first cell == a port row).
    text = PORTS_MD.read_text(encoding="utf-8")
    rows = [ln for ln in text.splitlines() if ln.startswith("|") and ln.split("|")[1].strip().isdigit()]
    # Dry-run the assigner with a never-registered probe slug -> prints the next-free port.
    probe = "vb-probe-" + uuid.uuid4().hex[:8]
    proc = py([str(PORT_REGISTRY_PY), "--project", probe, "--service", "frontend"], timeout=25)
    next_free = proc.stdout.strip()
    if len(rows) == 15 and proc.returncode == 0 and next_free == "3090":
        record(name, PASS, "15 table rows; next-free frontend = 3090 (no write)")
    else:
        record(name, FAIL, f"rows={len(rows)} (want 15) next_free={next_free!r} (want 3090) rc={proc.returncode}")


# --------------------------------------------------------------------------------------
# Check 8: vault-sync targets the ONE canonical harness dir only (dry-run)
# --------------------------------------------------------------------------------------
def check_vault_sync() -> None:
    name = "vault-sync: canonical-dir-only, dry-run plans without writing"
    if not VAULT_SYNC_PY.exists():
        record(name, FAIL, f"missing {VAULT_SYNC_PY}")
        return
    # Default (no --commit) is dry-run. Every printed plan line must target the single
    # canonical harness memory dir, never a stale/foreign one.
    proc = py([str(VAULT_SYNC_PY), "--direction", "both", "--project", "workflow-system"], timeout=40)
    out = proc.stdout
    if proc.returncode != 0:
        record(name, FAIL, f"rc={proc.returncode}: {(proc.stderr or out).strip()[:160]}")
        return
    canonical = r"C--Users-<you>-Desktop-AI-Projects\memory"
    plan_lines = [ln for ln in out.splitlines() if ln.startswith("[WOULD]") or ln.startswith("[DO]")]
    committed = any(ln.startswith("[DO]") for ln in plan_lines)
    # h2v plans write into the vault (src is harness); v2h plans write into the harness dir.
    # Confirm no plan references any harness dir other than the canonical one.
    foreign = [ln for ln in plan_lines if "memory" in ln and canonical not in ln and "\\projects\\" in ln.lower()]
    if not committed and not foreign:
        record(name, PASS, f"{len(plan_lines)} dry-run plan(s), canonical-only, nothing written")
    elif committed:
        record(name, FAIL, "dry-run produced [DO] lines (would have written)")
    else:
        record(name, FAIL, f"plan references a non-canonical harness dir: {foreign[:1]}")


# --------------------------------------------------------------------------------------
# Check 9: FreeLLMAPI :3001 health (INCONCLUSIVE if router is not running)
# --------------------------------------------------------------------------------------
def check_freellm() -> None:
    name = "FreeLLMAPI :3001 health (router reachable)"
    try:
        req = urllib.request.Request(FREELLM_URL, method="GET")
        with urllib.request.urlopen(req, timeout=6) as resp:
            code = resp.getcode()
        if 200 <= code < 400:
            record(name, PASS, f"HTTP {code} from {FREELLM_URL}")
        else:
            record(name, INC, f"HTTP {code} from {FREELLM_URL}")
    except (urllib.error.URLError, OSError) as exc:
        # Router not running is an environment state, not a bridge-code defect -> INCONCLUSIVE.
        record(name, INC, f"router not reachable ({exc.__class__.__name__}); start it to fully verify")


# --------------------------------------------------------------------------------------
# Check 10: all hooks + bridge scripts ParseFile / py_compile / bash -n clean
# --------------------------------------------------------------------------------------
def check_hooks_parse() -> None:
    # 10a: python files compile
    name_py = "syntax: bridge + hook .py files py_compile clean"
    py_targets = [
        DISPATCH_PY, SHARED_LOG_PY, RELAY_PY, TOOL_PARITY_PY,
        PORT_REGISTRY_PY, VAULT_SYNC_PY, AOS_LOCK_PY,
        HOOKS_DIR / "secret-firewall" / "block-secrets.py",
        HOOKS_DIR / "secret-firewall" / "detect-secrets.py",
    ]
    py_targets += sorted(HOOKS_DIR.glob("*.py"))
    py_targets = [p for p in dict.fromkeys(py_targets) if p.exists()]  # de-dup, keep existing
    py_fail = []
    for p in py_targets:
        try:
            py_compile.compile(str(p), doraise=True)
        except py_compile.PyCompileError as exc:
            py_fail.append(f"{p.name}: {exc.msg.splitlines()[0] if exc.msg else 'error'}")
    if not py_fail:
        record(name_py, PASS, f"{len(py_targets)} python files compile")
    else:
        record(name_py, FAIL, "; ".join(py_fail))

    # 10b: PowerShell hooks ParseFile clean
    name_ps = "syntax: PowerShell hooks ParseFile clean"
    ps_targets = sorted(HOOKS_DIR.glob("*.ps1"))
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        record(name_ps, INC, "powershell not on PATH")
    elif not ps_targets:
        record(name_ps, INC, "no .ps1 hooks found")
    else:
        # One ParseFile per file; collect parse errors.
        script = (
            "$ErrorActionPreference='Stop'; $bad=@(); "
            "foreach ($f in $args) { $e=$null; $t=$null; "
            "[System.Management.Automation.Language.Parser]::ParseFile($f,[ref]$t,[ref]$e) | Out-Null; "
            "if ($e -and $e.Count -gt 0) { $bad += ($f + ': ' + $e[0].Message) } } "
            "if ($bad.Count -gt 0) { $bad -join ' || ' | Write-Output; exit 1 } else { Write-Output 'ok'; exit 0 }"
        )
        proc = run([powershell, "-NoProfile", "-NonInteractive", "-Command", script, *[str(p) for p in ps_targets]],
                   timeout=60)
        if proc.returncode == 0 and "ok" in proc.stdout:
            record(name_ps, PASS, f"{len(ps_targets)} .ps1 hooks parse")
        else:
            record(name_ps, FAIL, (proc.stdout + proc.stderr).strip()[:200])

    # 10c: guard bash hooks `bash -n` clean
    name_sh = "syntax: guard .sh hooks bash -n clean"
    bash = _have_bash()
    sh_targets = [p for p in (GUARD_CAREFUL_SH, GUARD_FREEZE_SH) if p.exists()]
    if not bash:
        record(name_sh, INC, "bash not on PATH")
    elif not sh_targets:
        record(name_sh, FAIL, "guard .sh hooks not found")
    else:
        sh_fail = []
        for p in sh_targets:
            proc = run([bash, "-n", str(p)], timeout=20)
            if proc.returncode != 0:
                sh_fail.append(f"{p.name}: {(proc.stderr or proc.stdout).strip()[:80]}")
        if not sh_fail:
            record(name_sh, PASS, f"{len(sh_targets)} guard .sh hooks parse")
        else:
            record(name_sh, FAIL, "; ".join(sh_fail))


# --------------------------------------------------------------------------------------
# Check 11: drift trap - no hardcoded codex build hash in LIVE bridge code
# --------------------------------------------------------------------------------------
def check_no_hardcoded_hash() -> None:
    name = "drift-trap: no hardcoded codex build hash in live bridge code"
    live_code = [DISPATCH_PY, SHARED_LOG_PY, RELAY_PY, TOOL_PARITY_PY,
                 PORT_REGISTRY_PY, VAULT_SYNC_PY, AOS_LOCK_PY]
    live_code += sorted(HOOKS_DIR.glob("*.ps1"))
    live_code += sorted(HOOKS_DIR.glob("*.py"))
    hits = []
    for p in live_code:
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for h in KNOWN_STALE_HASHES:
            if h in text:
                hits.append(f"{p}: {h}")
    if not hits:
        record(name, PASS, "dispatcher resolves dynamically; no build hash in executable code")
    else:
        record(name, FAIL, "hardcoded hash in live code: " + "; ".join(hits))


def main() -> int:
    print("=" * 78)
    print("verify-bridge.py  -  Claude<->Codex bridge regression gate (user-triggered)")
    print(f"  AI_Projects: {AI_PROJECTS}")
    print(f"  started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 78)

    checks = [
        check_dispatch,
        check_tool_parity,
        check_shared_log,
        check_relay,
        check_guard_careful,
        check_guard_freeze,
        check_aos_lock,
        check_port_registry,
        check_vault_sync,
        check_freellm,
        check_hooks_parse,
        check_no_hardcoded_hash,
    ]
    for fn in checks:
        try:
            fn()
        except Exception as exc:  # a crashing check is itself a regression -> FAIL
            record(fn.__name__, FAIL, f"check raised {exc.__class__.__name__}: {exc}")

    n_pass = sum(1 for _, s, _ in results if s == PASS)
    n_fail = sum(1 for _, s, _ in results if s == FAIL)
    n_inc = sum(1 for _, s, _ in results if s == INC)
    print("-" * 78)
    print(f"SUMMARY: {n_pass} PASS / {n_fail} FAIL / {n_inc} INCONCLUSIVE  (of {len(results)} checks)")
    if n_fail:
        print("RESULT: FAIL - the bridge has drifted; see FAIL lines above.")
    elif n_inc:
        print("RESULT: PASS (with INCONCLUSIVE) - bridge code is sound; "
              "some env dependency was absent (e.g. router off, bash/powershell missing).")
    else:
        print("RESULT: PASS - all bridge checks green.")
    print("=" * 78)
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
