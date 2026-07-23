#!/usr/bin/env python3
"""Defiant Partners — numbered-menu pipeline board over partners.db.

Everything is keystrokes-and-Enter; nothing sends anything, ever.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import VERTICALS, connect, counts  # noqa: E402
import outreach  # noqa: E402

STATUSES = ["shortlist", "drafted", "translated", "sent", "replied", "meeting", "partner", "pass"]


def show_counts(con):
    by_status, by_vert = counts(con)
    print("\n Pipeline:", " · ".join(f"{s} {by_status.get(s, 0)}"
          for s in ["new"] + STATUSES if by_status.get(s)))
    print(" Verticals:", " · ".join(f"{v} {by_vert.get(v, 0)}" for v in VERTICALS if by_vert.get(v)))


def pick_vertical():
    print("\n Which vertical?")
    for i, v in enumerate(VERTICALS, 1):
        print(f"  [{i}] {v}")
    c = input(" > ").strip()
    if c.isdigit() and 1 <= int(c) <= len(VERTICALS):
        return VERTICALS[int(c) - 1]
    return None


def detail(con, row):
    print(f"""
 ───────────────────────────────────────────
 {row['name']}   {('/ ' + row['name_en']) if row['name_en'] else ''}
 vertical: {row['vertical']}   status: {row['status']}
 phone: {row['phone'] or '—'}   web: {row['website'] or '—'}
 hours: {row['hours'] or '—'}
 addr:  {row['addr'] or '—'}
 map:   https://www.openstreetmap.org/?mlat={row['lat']}&mlon={row['lon']}#map=18/{row['lat']}/{row['lon']}
 note:  {row['note'] or '—'}
 ───────────────────────────────────────────
  [s] shortlist   [d] dossier+letter now   [x] pass   [v] change vertical
  [n] add note    [Enter] skip""")
    c = input("  > ").strip().lower()
    if c == "s":
        con.execute("UPDATE clinics SET status='shortlist' WHERE id=?", (row["id"],))
    elif c == "d":
        draft = outreach.promote(row["id"])
        print(f"  ✊ dossier in vault + letter at {draft.name}")
    elif c == "x":
        con.execute("UPDATE clinics SET status='pass' WHERE id=?", (row["id"],))
    elif c == "v":
        v = pick_vertical()
        if v:
            con.execute("UPDATE clinics SET vertical=? WHERE id=?", (v, row["id"]))
    elif c == "n":
        con.execute("UPDATE clinics SET note=? WHERE id=?", (input("  note: ").strip(), row["id"]))
    con.commit()


def review(con, status="new"):
    v = pick_vertical()
    if not v:
        return
    rows = con.execute(
        "SELECT * FROM clinics WHERE status=? AND vertical=? ORDER BY (phone='') , name LIMIT 200",
        (status, v)).fetchall()
    if not rows:
        print(" (nothing here)")
        return
    page = 0
    while page * 15 < len(rows):
        chunk = rows[page * 15:(page + 1) * 15]
        print(f"\n {v} — {status} — {len(rows)} total (showing {page*15+1}–{page*15+len(chunk)})")
        for i, r in enumerate(chunk, 1):
            ph = "☎" if r["phone"] else " "
            print(f"  [{i:2}] {ph} {r['name'][:48]}{('  / ' + r['name_en'][:30]) if r['name_en'] else ''}")
        c = input("  number to open, [m]ore, [Enter] back > ").strip().lower()
        if c == "m":
            page += 1
        elif c.isdigit() and 1 <= int(c) <= len(chunk):
            detail(con, chunk[int(c) - 1])
        else:
            return


def mark(con):
    print("\n Which list?  [1] drafted  [2] translated  [3] sent  [4] replied  [5] meeting")
    src = {"1": "drafted", "2": "translated", "3": "sent", "4": "replied", "5": "meeting"}.get(input(" > ").strip())
    if not src:
        return
    rows = con.execute("SELECT * FROM clinics WHERE status=? ORDER BY name", (src,)).fetchall()
    if not rows:
        print(" (empty)")
        return
    for i, r in enumerate(rows, 1):
        print(f"  [{i:2}] {r['name'][:50]}")
    c = input("  number > ").strip()
    if not (c.isdigit() and 1 <= int(c) <= len(rows)):
        return
    row = rows[int(c) - 1]
    nxt = {"drafted": "translated", "translated": "sent", "sent": "replied",
           "replied": "meeting", "meeting": "partner"}[src]
    print(f"  [1] advance → {nxt}   [2] back to shortlist   [3] pass")
    a = input("  > ").strip()
    new = {"1": nxt, "2": "shortlist", "3": "pass"}.get(a)
    if new:
        con.execute("UPDATE clinics SET status=? WHERE id=?", (new, row["id"]))
        con.commit()
        print(f"  {row['name'][:40]} → {new} ✊")


def main():
    con = connect()
    while True:
        print("\n═══════════ DEFIANT PARTNERS ✊ ═══════════")
        show_counts(con)
        print("""
  [1] Review NEW clinics (sort into shortlist/pass)
  [2] Work the SHORTLIST (promote → dossier + letter)
  [3] Export drafted letters → Desktop batch for translators
  [4] Mark statuses (translated / sent / replied / meeting / partner)
  [5] Refresh crawl (OpenStreetMap) + re-import gyn dataset
  [6] Search by name
  [0] Quit""")
        c = input(" > ").strip()
        if c == "1":
            review(con, "new")
        elif c == "2":
            review(con, "shortlist")
        elif c == "3":
            outreach.export_batch()
        elif c == "4":
            mark(con)
        elif c == "5":
            import crawl, import_cmwh
            try:
                crawl.run()
            except Exception as e:
                print(" Overpass unhappy:", e)
            try:
                import_cmwh.run()
            except Exception as e:
                print(" cmwh import:", e)
        elif c == "6":
            q = input(" name contains: ").strip()
            for r in con.execute(
                    "SELECT * FROM clinics WHERE name LIKE ? OR name_en LIKE ? LIMIT 30",
                    (f"%{q}%", f"%{q}%")).fetchall():
                print(f"  #{r['id']} [{r['status']}/{r['vertical']}] {r['name']} {r['name_en'] or ''}")
            i = input(" open id (or Enter): ").strip()
            if i.isdigit():
                row = con.execute("SELECT * FROM clinics WHERE id=?", (i,)).fetchone()
                if row:
                    detail(con, row)
        elif c == "0":
            return
        input("\n (Enter to continue)")


if __name__ == "__main__":
    main()
