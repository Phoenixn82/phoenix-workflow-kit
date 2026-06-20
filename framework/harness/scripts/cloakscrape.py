"""
cloakscrape.py - stealth Chromium scrape via CloakBrowser.

Returns rendered HTML for a URL after bot-detection bypass. Use when:
- Target is known to use Cloudflare / reCAPTCHA / FingerprintJS / BrowserScan
- Firecrawl returned 403 or a challenge page
- The page is JS-rendered and shows a bot challenge before content loads

Usage:
    python cloakscrape.py <url> [--profile NAME] [--humanize] [--out FILE]
                          [--wait-for SELECTOR] [--timeout SECONDS]
                          [--timezone TZ] [--locale LOC] [--no-headless]

Output: HTML to stdout (or --out FILE). Cookies for the session printed to stderr.
"""
import argparse
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Stealth Chromium scrape via CloakBrowser")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("--profile", help="Persistent profile name (cookies/storage kept across runs)")
    parser.add_argument("--humanize", action="store_true", help="Enable human-like mouse/keyboard")
    parser.add_argument("--out", help="Write HTML to file instead of stdout")
    parser.add_argument("--wait-for", help="CSS selector to wait for before capturing HTML")
    parser.add_argument("--timeout", type=int, default=30, help="Navigation timeout in seconds (default 30)")
    parser.add_argument("--timezone", help="Override timezone (e.g. America/New_York)")
    parser.add_argument("--locale", help="Override locale (e.g. en-US)")
    parser.add_argument("--no-headless", action="store_true", help="Render visible browser window")
    parser.add_argument("--proxy", help="Proxy URL (e.g. http://user:pass@host:port)")
    args = parser.parse_args()

    from cloakbrowser import launch, launch_persistent_context

    launch_kwargs = {
        "headless": not args.no_headless,
        "humanize": args.humanize,
    }
    if args.timezone:
        launch_kwargs["timezone"] = args.timezone
    if args.locale:
        launch_kwargs["locale"] = args.locale
    if args.proxy:
        launch_kwargs["proxy"] = args.proxy

    if args.profile:
        profile_dir = Path.home() / ".cloakbrowser" / "profiles" / args.profile
        profile_dir.mkdir(parents=True, exist_ok=True)
        ctx = launch_persistent_context(str(profile_dir), **launch_kwargs)
        page = ctx.new_page()
        owner = ctx
    else:
        browser = launch(**launch_kwargs)
        page = browser.new_page()
        owner = browser

    try:
        page.goto(args.url, timeout=args.timeout * 1000, wait_until="domcontentloaded")
        if args.wait_for:
            page.wait_for_selector(args.wait_for, timeout=args.timeout * 1000)
        html = page.content()

        cookies = page.context.cookies()
        print(f"[cloakscrape] {len(cookies)} cookies captured", file=sys.stderr)

        if args.out:
            Path(args.out).write_text(html, encoding="utf-8")
            print(f"[cloakscrape] wrote {len(html)} chars to {args.out}", file=sys.stderr)
        else:
            sys.stdout.write(html)
    finally:
        owner.close()


if __name__ == "__main__":
    main()
