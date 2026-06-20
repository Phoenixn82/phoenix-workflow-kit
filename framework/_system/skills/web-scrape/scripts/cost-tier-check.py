"""Probe which tier of the cost-first scraping ladder will serve a URL.

Spec: PHASE_5_DISPATCH.md § 4.1
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request


BLOCKED_MARKERS = (
    "captcha",
    "please verify you are human",
    "access denied",
    "cloudflare",
    "are you a robot",
    "verify you are human",
)


def _is_blocked_signal(body: str, status: int) -> bool:
    if status in (403, 429):
        return True
    if len(body) < 200 and any(m in body.lower() for m in BLOCKED_MARKERS):
        return True
    return False


def _probe_firecrawl(url: str, timeout: float) -> tuple[bool, str]:
    if not shutil.which("firecrawl"):
        return False, "firecrawl CLI not found"
    t0 = time.time()
    try:
        proc = subprocess.run(
            ["firecrawl", "scrape", url],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        latency = int((time.time() - t0) * 1000)
        if proc.returncode != 0:
            return False, f"rc={proc.returncode} {proc.stderr.strip()[:80]}"
        body = proc.stdout
        if _is_blocked_signal(body, 200):
            return False, "blocked signal in body"
        return True, f"{latency}ms"
    except subprocess.TimeoutExpired:
        return False, f"timeout {timeout}s"
    except FileNotFoundError:
        return False, "firecrawl not found"


def _probe_cloak(url: str, timeout: float) -> tuple[bool, str]:
    # Tier 2 of the cost ladder is CloakBrowser, invoked via the cloakscrape.py
    # helper (NOT a `cloak` CLI, which does not exist).
    from pathlib import Path

    script = Path.home() / ".claude" / "scripts" / "cloakscrape.py"
    if not script.exists():
        return False, f"cloakscrape.py not found at {script}"
    t0 = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, str(script), url],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        latency = int((time.time() - t0) * 1000)
        if proc.returncode != 0:
            return False, f"rc={proc.returncode} {proc.stderr.strip()[:80]}"
        if _is_blocked_signal(proc.stdout, 200):
            return False, "blocked signal in body"
        return True, f"{latency}ms"
    except subprocess.TimeoutExpired:
        return False, f"timeout {timeout}s"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True)
    ap.add_argument("--json", dest="emit_json", action="store_true")
    ap.add_argument("--firecrawl-timeout", type=float, default=8.0)
    ap.add_argument("--cloak-timeout", type=float, default=40.0)
    args = ap.parse_args()

    t_start = time.time()

    tier1_ok, tier1_note = _probe_firecrawl(args.url, args.firecrawl_timeout)
    if tier1_ok:
        result = {"tier": 1, "verified": True, "reason": tier1_note, "latency_ms": int((time.time() - t_start) * 1000)}
    else:
        tier2_ok, tier2_note = _probe_cloak(args.url, args.cloak_timeout)
        if tier2_ok:
            result = {"tier": 2, "verified": True, "reason": f"tier1 failed ({tier1_note}); tier2 ok ({tier2_note})", "latency_ms": int((time.time() - t_start) * 1000)}
        else:
            result = {
                "tier": 3,
                "verified": False,
                "reason": f"tier1 failed ({tier1_note}); tier2 failed ({tier2_note}); falling back to local driver",
                "latency_ms": int((time.time() - t_start) * 1000),
            }

    if args.emit_json:
        print(json.dumps(result, indent=2))
    else:
        tier_name = {1: "firecrawl", 2: "cloakbrowser", 3: "local"}[result["tier"]]
        verified = "verified" if result["verified"] else "fallback"
        print(f"tier {result['tier']} ({tier_name}) — {verified}")
        print(f"  reason: {result['reason']}")
        print(f"  latency: {result['latency_ms']}ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
