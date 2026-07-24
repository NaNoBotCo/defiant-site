#!/usr/bin/env python3
"""Defiant inbox — numbered-menu CLI over the defiant-leads Worker.

Leads (people who want help) AND subscribers (your newsletter list — YOUR data,
in YOUR database, no third party). First run asks for the Worker URL and token,
then remembers them in ~/.config/defiant/leads.json.
"""
import datetime
import json
import sys
import urllib.request
import webbrowser
from pathlib import Path

CFG = Path.home() / ".config" / "defiant" / "leads.json"


def load_cfg():
    if CFG.exists():
        return json.loads(CFG.read_text())
    return {}


def save_cfg(cfg):
    CFG.parent.mkdir(parents=True, exist_ok=True)
    CFG.write_text(json.dumps(cfg, indent=2))


def setup(cfg):
    print("\n-- One-time setup --")
    print("Worker URL (from `wrangler deploy`, e.g. https://defiant-leads.wichaa.workers.dev)")
    url = input("URL: ").strip().rstrip("/")
    tok = input("LEADS_TOKEN (the secret you set with `wrangler secret put LEADS_TOKEN`): ").strip()
    if url and tok:
        cfg.update(url=url, token=tok)
        save_cfg(cfg)
        print("Saved to", CFG)
    return cfg


def fetch(cfg, path="/leads"):
    req = urllib.request.Request(cfg["url"] + path,
                                 headers={"Authorization": "Bearer " + cfg["token"]})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def show(cfg):
    try:
        data = fetch(cfg)
    except Exception as e:
        print("\n!! Could not reach the Worker:", e)
        print("   (Is it deployed? Is the token right? Option 3 re-runs setup.)")
        return
    leads = data.get("leads", [])
    last = cfg.get("last_seen_ts", 0)
    new = [l for l in leads if l["ts"] > last]
    print(f"\n===== {len(leads)} leads — {len(new)} NEW =====")
    for l in leads[:50]:
        when = datetime.datetime.fromtimestamp(l["ts"] / 1000).strftime("%Y-%m-%d %H:%M")
        flag = "★ NEW " if l["ts"] > last else "      "
        print(f"\n{flag}[{when}]  {l.get('name') or '(no name)'}")
        print(f"      contact: {l['contact']}")
        print(f"      {l['message']}")
    if leads:
        cfg["last_seen_ts"] = max(l["ts"] for l in leads)
        save_cfg(cfg)


def show_subscribers(cfg):
    try:
        data = fetch(cfg, "/subscribers")
    except Exception as e:
        print("\n!! Could not reach the Worker:", e)
        return
    subs = data.get("subscribers", [])
    last = cfg.get("subs_seen_ts", 0)
    new = [s for s in subs if s["ts"] > last]
    print(f"\n===== {len(subs)} subscribers — {len(new)} NEW =====")
    for s in subs[:100]:
        when = datetime.datetime.fromtimestamp(s["ts"] / 1000).strftime("%Y-%m-%d %H:%M")
        flag = "★ " if s["ts"] > last else "  "
        nm = f"  ({s['name']})" if s.get("name") else ""
        print(f"  {flag}[{when}]  {s['email']}{nm}")
    if subs:
        cfg["subs_seen_ts"] = max(s["ts"] for s in subs)
        save_cfg(cfg)


def export_subscribers(cfg):
    out = Path.home() / "Desktop" / f"Defiant subscribers {datetime.date.today().isoformat()}.csv"
    try:
        req = urllib.request.Request(
            cfg["url"] + "/subscribers?format=csv",
            headers={"Authorization": "Bearer " + cfg["token"]})
        with urllib.request.urlopen(req, timeout=30) as r:
            out.write_bytes(r.read())
    except Exception as e:
        print("\n!! Export failed:", e)
        return
    print(f"\n✓ Exported to {out}")
    print("  (email,name,subscribed_utc,source — ready to import into any sender.)")


def show_clinics(cfg):
    try:
        data = fetch(cfg, "/clinics-submitted")
    except Exception as e:
        print("\n!! Could not reach the Worker:", e)
        return
    cl = data.get("clinics", [])
    last = cfg.get("clinics_seen_ts", 0)
    new = [c for c in cl if c["ts"] > last]
    print(f"\n===== {len(cl)} clinic submissions — {len(new)} NEW =====")
    for c in cl[:50]:
        when = datetime.datetime.fromtimestamp(c["ts"] / 1000).strftime("%Y-%m-%d %H:%M")
        flag = "★ NEW " if c["ts"] > last else "      "
        print(f"\n{flag}[{when}]  {c['name']}   {c.get('area') or ''}")
        if c.get("services"):
            print(f"      services: {c['services']}")
        if c.get("promotions"):
            print(f"      promos:   {c['promotions']}")
        contacts = " · ".join(x for x in (
            (f"LINE {c['line']}" if c.get("line") else ""),
            (f"tel {c['phone']}" if c.get("phone") else ""),
            (c.get("website") or "")) if x)
        if contacts:
            print(f"      contact:  {contacts}")
        if c.get("pitch"):
            print(f"      pitch:    {c['pitch']}")
    if cl:
        cfg["clinics_seen_ts"] = max(c["ts"] for c in cl)
        save_cfg(cfg)


def main():
    cfg = load_cfg()
    if not cfg.get("url"):
        cfg = setup(cfg)
        if not cfg.get("url"):
            sys.exit("No config; bye.")
    while True:
        print("\n===== DEFIANT INBOX ✊ =====")
        print(" [1] Show leads (new first)")
        print(" [2] Leads — table view in browser")
        print(" [3] Show subscribers (the list)")
        print(" [4] Export subscribers → CSV on Desktop")
        print(" [5] Show clinic submissions (partner sign-ups)")
        print(" [6] Setup / change URL + token")
        print(" [0] Quit")
        c = input("> ").strip()
        if c == "1":
            show(cfg)
        elif c == "2":
            webbrowser.open(f"{cfg['url']}/leads?format=html&token={cfg['token']}")
        elif c == "3":
            show_subscribers(cfg)
        elif c == "4":
            export_subscribers(cfg)
        elif c == "5":
            show_clinics(cfg)
        elif c == "6":
            cfg = setup(cfg)
        elif c == "0":
            return
        input("\n(Enter to continue)")


if __name__ == "__main__":
    main()
