#!/usr/bin/env python3
"""Extract a PUBLIC directory dataset from the private partners CRM.

partners/partners.db is private (crawl + outreach status/notes). This pulls out
ONLY the public facts (name, category, coordinates) for classified facilities and
writes directory_public.json — which IS committed and feeds the site's structured
data layer (footer index, /data/directory.json, schema.org). Never emits phone,
status, notes, or any outreach/CRM field.

Run nightly (via nightly.sh) after the crawl refreshes partners.db.
"""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / "partners" / "partners.db"
OUT = ROOT / "directory_public.json"

# Which crawled verticals become public directory categories, and their labels.
PUBLIC = {
    "geriatric": "Care homes & elder care",
    "rehab": "Rehab & recovery",
    "gyn": "Women's health & fertility",
    "aesthetic": "Aesthetic & skin",
    "longevity": "Longevity & wellness",
    "pharmacy": "Pharmacies",
}
CITY = "Chiang Mai"  # crawl is bbox-scoped to greater Chiang Mai for now


def run():
    if not DB.exists():
        print(f"no partners.db at {DB} — run the crawl first (partners/board.py → refresh)")
        # still write an empty structure so the build never breaks
        OUT.write_text(json.dumps({"generated_from": "none", "city": CITY, "categories": {}}, indent=2))
        return
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cats = {}
    for vert, label in PUBLIC.items():
        rows = con.execute(
            "SELECT name, name_en, lat, lon FROM clinics "
            "WHERE vertical=? AND status!='pass' AND name!='' ORDER BY name",
            (vert,)).fetchall()
        items = []
        seen = set()
        for r in rows:
            key = (r["name"] or r["name_en"] or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            items.append({
                "name": r["name"] or r["name_en"],
                "name_en": r["name_en"] or "",
                "lat": r["lat"], "lon": r["lon"],
            })
        if items:
            cats[vert] = {"label": label, "count": len(items), "items": items}
    OUT.write_text(json.dumps(
        {"generated_from": "partners.db (OSM crawl)", "city": CITY, "categories": cats},
        ensure_ascii=False, indent=2))
    total = sum(c["count"] for c in cats.values())
    print(f"directory_public.json: {total} facilities across {len(cats)} categories → {OUT.name}")


if __name__ == "__main__":
    run()
