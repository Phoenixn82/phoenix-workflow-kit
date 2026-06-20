"""Log a scraping lesson to Projects/<slug>/tokens.md when a cheaper tier exists.

Spec: PHASE_5_DISPATCH.md § 4.2
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

TIER_NAMES = {1: "firecrawl", 2: "cloak", 3: "local driver"}


def _tokens_path(vault: Path, slug: str) -> Path:
    return vault / "Projects" / slug / "tokens.md"


def _is_recent_duplicate(content: str, url: str, tier_used: int) -> bool:
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    pattern = re.compile(
        rf"^## (\d{{4}}-\d{{2}}-\d{{2}}) — Scraping fell through to .* on {re.escape(url)} \(tier {tier_used}\)",
        re.MULTILINE,
    )
    for m in pattern.finditer(content):
        try:
            entry_date = datetime.strptime(m.group(1), "%Y-%m-%d").date()
            if entry_date >= yesterday:
                return True
        except ValueError:
            continue
    return False


def _format_entry(
    url: str, tier_used: int, tier_cheaper: int, tokens_burned: int, notes: str
) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    used_name = TIER_NAMES.get(tier_used, f"tier {tier_used}")
    cheaper_name = TIER_NAMES.get(tier_cheaper, f"tier {tier_cheaper}")
    return f"""
## {today} — Scraping fell through to {used_name} on {url} (tier {tier_used})

**Expensive:** Used {used_name} (tier {tier_used}) for {url}. Burned ~{tokens_burned} tokens.

**Cheaper:** Could have used {cheaper_name} (tier {tier_cheaper}) had the lower tier been verified first.

**When to apply:** Probe with `cost-tier-check.py --url <url>` before launching the scrape so the right tier is picked the first time.

**Token saved per call:** estimated {tokens_burned // max(tier_used - tier_cheaper, 1)}

**Confidence:** medium (observed once)
{f'**Notes:** {notes}' if notes else ''}
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--tier-used", type=int, required=True, choices=[1, 2, 3])
    ap.add_argument("--tier-cheaper", type=int, required=True, choices=[1, 2])
    ap.add_argument("--tokens-burned", type=int, required=True)
    ap.add_argument("--notes", default="")
    ap.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)
    args = ap.parse_args()

    if args.tier_cheaper >= args.tier_used:
        print("tier-cheaper must be < tier-used", file=sys.stderr)
        return 1

    target = _tokens_path(args.vault_root, args.project)
    existing = target.read_text(encoding="utf-8") if target.exists() else ""

    if _is_recent_duplicate(existing, args.url, args.tier_used):
        print("recent duplicate within 24h, skipping", file=sys.stderr)
        return 0

    entry = _format_entry(
        args.url, args.tier_used, args.tier_cheaper, args.tokens_burned, args.notes
    )

    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            f"---\ntype: tokens-log\nproject: {args.project}\nai-first: true\n---\n\n"
            f"# {args.project} — token-expense lessons\n{entry}",
            encoding="utf-8",
        )
    else:
        target.write_text(existing + entry, encoding="utf-8")

    print(str(target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
