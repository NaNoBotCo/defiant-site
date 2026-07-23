#!/usr/bin/env python3
"""archive_defiant — snapshot defiant.to into the Wayback Machine, politely.

defiant.to is small (~110 URLs), so one gentle Save-Page-Now pass finishes in
minutes. This reads the live sitemap + machine surfaces, skips anything Wayback
already captured recently (so a weekly cron never re-hits unchanged pages), and
drips submissions at a polite rate. Nothing here deletes or overwrites; --plan,
--dry-run and --coverage make zero submissions.

USAGE
  python3 archive_defiant.py --plan            # what would be sent, touch nothing
  python3 archive_defiant.py --dry-run         # same, but resolves skip-recent
  python3 archive_defiant.py                    # submit (skips pages <7 days old)
  python3 archive_defiant.py --skip-recent 0    # force re-capture everything
  python3 archive_defiant.py --coverage         # ask Wayback what it holds
"""
import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SITE = "https://defiant.to"
SITEMAP = f"{SITE}/sitemap.xml"
UA = "DefiantArchiver/1.0 (+https://defiant.to; archival)"
LEDGER = Path.home() / "Library" / "Logs" / "defiant-archive.jsonl"
EXTRAS = [f"{SITE}/robots.txt", f"{SITE}/llms.txt", f"{SITE}/llms-full.txt",
          f"{SITE}/feed.xml", f"{SITE}/sitemap.xml",
          f"{SITE}/data/catalog.json", f"{SITE}/data/directory.json"]


def get(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def urls_from_sitemap():
    try:
        xml = get(SITEMAP)
    except Exception as e:
        print(f"  (sitemap unreachable: {e})")
        return []
    return re.findall(r"<loc>([^<]+)</loc>", xml)


def last_capture(url):
    """Most recent Wayback timestamp for url, or None."""
    api = ("http://web.archive.org/cdx/search/cdx?url="
           + urllib.parse.quote(url, safe="") + "&output=json&fl=timestamp&limit=-1")
    try:
        rows = json.loads(get(api, timeout=40))
        if len(rows) > 1:
            return datetime.strptime(rows[-1][0], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    except Exception:
        pass
    return None


def save(url, timeout=120):
    req = urllib.request.Request("https://web.archive.org/save/" + url,
                                 headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status in (200, 302)
    except Exception as e:
        print(f"    ! {e}")
        return False


def log(url, ok):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as f:
        f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(),
                            "url": url, "ok": ok}) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--coverage", action="store_true")
    ap.add_argument("--skip-recent", type=int, default=7, help="skip URLs captured within N days")
    ap.add_argument("--rate", type=float, default=6.0, help="seconds between submissions")
    args = ap.parse_args()

    urls = list(dict.fromkeys(urls_from_sitemap() + EXTRAS))
    print(f"defiant.to archive — {len(urls)} URLs (sitemap + machine surfaces)")

    if args.coverage:
        held = sum(1 for u in urls if last_capture(u))
        print(f"Wayback already holds a capture of {held}/{len(urls)} URLs.")
        return
    if args.plan:
        for u in urls:
            print("  ", u)
        return

    now = datetime.now(timezone.utc)
    sent = skipped = failed = 0
    for u in urls:
        if args.skip_recent:
            lc = last_capture(u)
            if lc and (now - lc).days < args.skip_recent:
                skipped += 1
                continue
        if args.dry_run:
            print("  would send", u)
            sent += 1
            continue
        ok = save(u)
        log(u, ok)
        print(f"  {'✓' if ok else '✗'} {u}")
        sent += 1 if ok else 0
        failed += 0 if ok else 1
        time.sleep(args.rate)
    tag = "would send" if args.dry_run else "sent"
    print(f"\n{tag} {sent} · skipped {skipped} (recent) · failed {failed}")


if __name__ == "__main__":
    main()
