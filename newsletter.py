#!/usr/bin/env python3
"""Defiant dispatch — generate the newsletter FROM the site's own content.

Reads the same notes build.py publishes, gathers what changed in a window (1 day
for the daily, 7 for the weekly digest), and renders a ready-to-send issue: subject
+ inline-styled HTML email + plain-text version. Writes both to the Desktop for you
to read before anything sends — nothing here auto-sends.

Sending is wired but gated: set RESEND_API_KEY (+ a verified from-address) and the
menu's send options light up. Recipients come from your own D1 list via the worker.

Numbered-menu CLI (low-vision friendly). Run: python3 newsletter.py  — or the
Desktop "Defiant Newsletter.command".
"""
import json
import os
import re
import ssl
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

from build import collect_notes, PAGE_OVERRIDES, build_catalog, savings_line, _prices, SITE, BLESSING

ROOT = Path(__file__).resolve().parent
DESKTOP = Path.home() / "Desktop"
CONFIG = Path.home() / ".config" / "defiant" / "leads.json"   # {url, token} from the leads setup
FROM = "Defiant <dispatch@defiant.to>"                          # change to your verified sender
MAGENTA, CYAN, INK, GREY = "#ff179e", "#00d6d6", "#0b0b0b", "#666"


def cfg():
    try:
        return json.loads(CONFIG.read_text())
    except Exception:
        return {}


def changed_within(days):
    """Pages whose `updated` date is within `days` of today, newest first."""
    cutoff = date.today() - timedelta(days=days)
    notes = collect_notes()
    rows = []
    for route, (name, meta, _b) in notes.items():
        ov = PAGE_OVERRIDES.get(name, {})
        if ov.get("noindex"):
            continue
        u = meta.get("updated", "")
        try:
            d = datetime.strptime(u[:10], "%Y-%m-%d").date()
        except Exception:
            continue
        if d >= cutoff:
            title = ov.get("title") or meta.get("title") or name.lstrip("=")
            desc = ov.get("description") or meta.get("description") or ""
            rows.append((d, route, title.split(" — ")[0].split(" | ")[0], desc, meta))
    rows.sort(key=lambda r: r[0], reverse=True)
    return rows


def _unit(s):
    """The trailing unit phrase of a price string ('per eye', 'per year', '') — used
    to reject apples-to-oranges comparisons (US 'per year' vs TH 'per course')."""
    return re.sub(r"[\d,.$+–—-]", " ", s or "").replace("per", "").strip().lower()


def biggest_saving(rows):
    """The featured number — widest credible gap, only where US/TH units MATCH so the
    percentage is always defensible."""
    best = None
    for _d, route, title, _desc, meta in rows:
        if meta.get("type") != "procedure":
            continue
        us, th = meta.get("us_cost", ""), meta.get("th_cost", "")
        if _unit(us) != _unit(th):          # course-vs-year, session-vs-cycle → skip
            continue
        un, tn = _prices(us), _prices(th)
        if un and tn and max(un):
            pct = round((1 - max(tn) / max(un)) * 100)
            if 15 <= pct <= 95 and (not best or pct > best[0]):
                best = (pct, title, route, us, th)
    return best


def build_issue(days, kind):
    rows = changed_within(days)
    iso = date.today().isoformat()
    n = len(rows)
    subject = (f"Defiant daily — {n} new on the site" if kind == "daily"
               else f"Defiant weekly — {n} new & updated")
    feat = biggest_saving(rows)

    # ---- plain text ----
    tl = [f"DEFIANT DISPATCH — {kind.upper()} · {iso}", ""]
    if feat:
        pct, title, route, us, th = feat
        tl += [f"★ Biggest saving this {kind}: {title} — save ~{pct}% "
               f"(US {us} vs Thailand {th})", f"  {SITE}{route}", ""]
    tl.append("New & updated on defiant.to:")
    for _d, route, title, desc, _m in rows[:24]:
        tl += [f"- {title} — {desc}".rstrip(" —"), f"  {SITE}{route}"]
    tl += ["", "Pay what the locals pay. Plan your escape.",
           "Unsubscribe: reply UNSUBSCRIBE. Your email lives in our own database, not a third party's.",
           "", BLESSING]
    text = "\n".join(tl)

    # ---- HTML (inline styles; email clients strip <style>) ----
    def esc(s):
        return (s or "").replace("&", "&amp;").replace("<", "&lt;")
    items = ""
    for _d, route, title, desc, _m in rows[:24]:
        items += (f'<tr><td style="padding:10px 0;border-bottom:1px solid #eee">'
                  f'<a href="{SITE}{route}" style="color:{INK};font-weight:700;text-decoration:none;'
                  f'font-size:17px">{esc(title)}</a><br>'
                  f'<span style="color:{GREY};font-size:14px;line-height:1.5">{esc(desc)}</span></td></tr>')
    feat_html = ""
    if feat:
        pct, title, route, us, th = feat
        feat_html = (f'<div style="border:3px solid {INK};background:#fffbe6;padding:16px;margin:0 0 22px">'
                     f'<div style="font:700 13px/1 Menlo,monospace;color:{MAGENTA};letter-spacing:.1em">'
                     f'★ BIGGEST SAVING THIS {kind.upper()}</div>'
                     f'<div style="font:800 26px/1.2 Arial,sans-serif;margin:8px 0 4px">'
                     f'<a href="{SITE}{route}" style="color:{INK};text-decoration:none">{esc(title)} '
                     f'— save ~{pct}%</a></div>'
                     f'<div style="color:{GREY};font-size:14px"><s>US {esc(us)}</s> &rarr; '
                     f'<b style="color:{MAGENTA}">Thailand {esc(th)}</b></div></div>')
    html = (f'<!doctype html><html><body style="margin:0;background:#fff;'
            f'font-family:Arial,Helvetica,sans-serif;color:{INK}">'
            f'<!-- {esc(BLESSING)} -->'
            f'<div style="max-width:600px;margin:0 auto;padding:24px">'
            f'<div style="font:800 34px/1 Impact,Arial;letter-spacing:.02em;'
            f'text-shadow:2px 0 {CYAN},-2px 0 {MAGENTA}">DEFIANT</div>'
            f'<div style="font:700 12px/1 Menlo,monospace;color:{MAGENTA};letter-spacing:.14em;'
            f'text-transform:uppercase;margin:6px 0 20px">The Dispatch · {kind} · {iso}</div>'
            f'{feat_html}'
            f'<div style="font:700 13px/1 Menlo,monospace;color:{GREY};letter-spacing:.1em;'
            f'text-transform:uppercase;margin:0 0 6px">New &amp; updated on defiant.to</div>'
            f'<table style="width:100%;border-collapse:collapse">{items}</table>'
            f'<p style="margin:26px 0 6px"><a href="{SITE}/procedures/" '
            f'style="background:{MAGENTA};color:#fff;padding:12px 20px;text-decoration:none;'
            f'font-weight:700;display:inline-block">See what it costs &rarr;</a></p>'
            f'<p style="color:{GREY};font-size:12px;line-height:1.6;margin-top:24px;'
            f'border-top:1px solid #eee;padding-top:14px">Pay what the locals pay. '
            f'You\'re getting this because you joined the Defiant list — your email lives in '
            f'our own database, not a third party\'s. Reply UNSUBSCRIBE to leave.<br>'
            f'<span lang="th">สาธุ</span> 🙏</p>'
            f'</div></body></html>')
    return subject, html, text


def write_preview(kind, subject, html, text):
    stamp = date.today().isoformat()
    hp = DESKTOP / f"Defiant Dispatch — {kind} {stamp}.html"
    tp = DESKTOP / f"Defiant Dispatch — {kind} {stamp}.txt"
    hp.write_text(html, encoding="utf-8")
    tp.write_text(f"SUBJECT: {subject}\n\n{text}", encoding="utf-8")
    return hp, tp


def fetch_recipients(kind):
    c = cfg()
    if not c.get("url") or not c.get("token"):
        raise RuntimeError("No worker url/token in ~/.config/defiant/leads.json")
    req = urllib.request.Request(c["url"].rstrip("/") + "/subscribers",
                                 headers={"Authorization": "Bearer " + c["token"]})
    ctx = ssl.create_default_context()
    data = json.loads(urllib.request.urlopen(req, context=ctx, timeout=30).read())
    subs = data.get("subscribers", [])
    # Weekly is the default; daily only those who opted in. (frequency present once the
    # worker column is deployed; absent = weekly.)
    if kind == "daily":
        return [s["email"] for s in subs if (s.get("frequency") == "daily")]
    return [s["email"] for s in subs if (s.get("frequency", "weekly") != "daily")]


def send_via_resend(subject, html, text, recipients):
    key = os.environ.get("RESEND_API_KEY") or cfg().get("resend_key")
    if not key:
        raise RuntimeError("No RESEND_API_KEY (env or leads.json). Sending is not wired yet.")
    ok = 0
    ctx = ssl.create_default_context()
    for to in recipients:
        body = json.dumps({"from": FROM, "to": [to], "subject": subject,
                           "html": html, "text": text}).encode()
        req = urllib.request.Request("https://api.resend.com/emails", data=body,
                                     headers={"Authorization": "Bearer " + key,
                                              "Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req, context=ctx, timeout=30)
            ok += 1
        except Exception as e:
            print(f"  ! failed {to}: {e}")
    return ok


def menu():
    print("\n\033[1m✊ DEFIANT NEWSLETTER\033[0m — generate from the site, review, then send\n")
    print("  1) Preview WEEKLY digest  (last 7 days → Desktop)")
    print("  2) Preview DAILY issue    (last 1 day → Desktop)")
    print("  3) Send WEEKLY   (needs RESEND_API_KEY + verified sender)")
    print("  4) Send DAILY    (needs RESEND_API_KEY + verified sender)")
    print("  q) quit\n")
    ch = input("  choose: ").strip().lower()
    if ch in ("1", "2"):
        kind, days = ("weekly", 7) if ch == "1" else ("daily", 1)
        subject, html, text = build_issue(days, kind)
        hp, tp = write_preview(kind, subject, html, text)
        print(f"\n  SUBJECT: {subject}")
        print(f"  ✓ wrote {hp.name}")
        print(f"  ✓ wrote {tp.name}\n  Open the .html to read it. Nothing was sent.\n")
    elif ch in ("3", "4"):
        kind, days = ("weekly", 7) if ch == "3" else ("daily", 1)
        subject, html, text = build_issue(days, kind)
        try:
            rec = fetch_recipients(kind)
        except Exception as e:
            print(f"\n  ✗ couldn't read the list: {e}\n"); return
        if not rec:
            print(f"\n  (no {kind} subscribers yet)\n"); return
        print(f"\n  {kind}: {len(rec)} recipients. SUBJECT: {subject}")
        if input(f"  Type SEND to email all {len(rec)}: ").strip() == "SEND":
            try:
                ok = send_via_resend(subject, html, text, rec)
                print(f"\n  ✓ sent {ok}/{len(rec)}\n")
            except Exception as e:
                print(f"\n  ✗ {e}\n")
        else:
            print("  cancelled.\n")


if __name__ == "__main__":
    menu()
