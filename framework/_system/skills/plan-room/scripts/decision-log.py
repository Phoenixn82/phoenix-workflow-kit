"""Append a decision to Projects/<slug>/decisions.md per capture wrench format.

Spec: _archive/claude_projects_2026-05-pre-rebuild/Rebuild/PHASE_5_DISPATCH.md § 6.2 (archive only)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_VAULT_ROOT = Path(
    os.environ.get(
        "AI_PROJECTS_ROOT", r"C:\Users\<you>\Desktop\AI_Projects"
    )
) / "_system" / "second-brain"


def _decisions_path(vault: Path, slug: str) -> Path:
    return vault / "Projects" / slug / "decisions.md"


def _is_recent_duplicate(content: str, title: str) -> bool:
    pattern = re.compile(
        rf"^## (\d{{4}}-\d{{2}}-\d{{2}}( \d{{2}}:\d{{2}})?)\s*—\s*{re.escape(title)}\s*$",
        re.MULTILINE,
    )
    now = datetime.now()
    for m in pattern.finditer(content):
        raw = m.group(1)
        fmt = "%Y-%m-%d %H:%M" if " " in raw else "%Y-%m-%d"
        try:
            ts = datetime.strptime(raw, fmt)
            if now - ts < timedelta(seconds=60):
                return True
        except ValueError:
            continue
    return False


def _format(
    title: str,
    decision: str,
    reasoning: str,
    alternatives: str | None,
    confidence: str,
    links: str | None,
) -> str:
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    body = [f"\n## {today} — {title}\n"]
    body.append(f"**Decision:** {decision}")
    body.append(f"**Reasoning:** {reasoning}")
    if alternatives:
        body.append(f"**Alternatives considered:** {alternatives}")
    body.append(f"**Confidence:** {confidence}")
    if links:
        body.append(f"**Links:** {links}")
    return "\n\n".join(body) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--decision", required=True)
    ap.add_argument("--reasoning", required=True)
    ap.add_argument("--alternatives", default=None)
    ap.add_argument(
        "--confidence",
        default="stated",
        choices=["stated", "high", "medium", "speculation"],
    )
    ap.add_argument("--links", default=None)
    ap.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)
    args = ap.parse_args()

    target = _decisions_path(args.vault_root, args.project)
    existing = target.read_text(encoding="utf-8") if target.exists() else ""

    if _is_recent_duplicate(existing, args.title):
        print("recent duplicate within 60s, skipping", file=sys.stderr)
        return 0

    entry = _format(
        args.title,
        args.decision,
        args.reasoning,
        args.alternatives,
        args.confidence,
        args.links,
    )

    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            f"---\ntype: decisions-log\nproject: {args.project}\nai-first: true\n---\n\n"
            f"# {args.project} — decisions log\n{entry}",
            encoding="utf-8",
        )
    else:
        target.write_text(existing + entry, encoding="utf-8")

    print(str(target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
