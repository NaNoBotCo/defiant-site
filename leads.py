#!/usr/bin/env python3
"""Defiant leads inbox — numbered-menu CLI over the defiant-leads Worker.

First run asks for the Worker URL and token, then remembers them in
~/.config/defiant/leads.json. New leads (since your last check) show first.
"""
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


def fetch(cfg):
    req = urllib.request.Request(cfg["url"] + "/leads",
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
        import datetime
        when = datetime.datetime.fromtimestamp(l["ts"] / 1000).strftime("%Y-%m-%d %H:%M")
        flag = "★ NEW " if l["ts"] > last else "      "
        print(f"\n{flag}[{when}]  {l.get('name') or '(no name)'}")
        print(f"      contact: {l['contact']}")
        print(f"      {l['message']}")
    if leads:
        cfg["last_seen_ts"] = max(l["ts"] for l in leads)
        save_cfg(cfg)


def main():
    cfg = load_cfg()
    if not cfg.get("url"):
        cfg = setup(cfg)
        if not cfg.get("url"):
            sys.exit("No config; bye.")
    while True:
        print("\n===== DEFIANT LEADS ✊ =====")
        print(" [1] Show leads (new first)")
        print(" [2] Open table view in browser")
        print(" [3] Setup / change URL + token")
        print(" [0] Quit")
        c = input("> ").strip()
        if c == "1":
            show(cfg)
        elif c == "2":
            webbrowser.open(f"{cfg['url']}/leads?format=html&token={cfg['token']}")
        elif c == "3":
            cfg = setup(cfg)
        elif c == "0":
            return
        input("\n(Enter to continue)")


if __name__ == "__main__":
    main()
