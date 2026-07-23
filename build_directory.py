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

    # Chiang Mai depth: the local verticals (care homes, rehab, gyn, etc.)
    cats = {}
    for vert, label in PUBLIC.items():
        rows = con.execute(
            "SELECT name, name_en, lat, lon FROM clinics "
            "WHERE vertical=? AND status!='pass' AND name!='' ORDER BY name", (vert,)).fetchall()
        items, seen = [], set()
        for r in rows:
            key = (r["name"] or r["name_en"] or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            items.append({"name": r["name"] or r["name_en"], "name_en": r["name_en"] or "",
                          "lat": r["lat"], "lon": r["lon"]})
        if items:
            cats[vert] = {"label": label, "count": len(items), "items": items}

    # Worldwide breadth: hospitals grouped by country → city.
    by_country = {}
    for r in con.execute(
            "SELECT name, name_en, city, country, lat, lon FROM clinics "
            "WHERE vertical='hospital' AND status!='pass' AND name!='' ORDER BY country, city, name"):
        country = r["country"] or "Other"
        by_country.setdefault(country, {"count": 0, "cities": {}})
        city = r["city"] or "—"
        by_country[country]["cities"].setdefault(city, [])
        names = {i["name"].lower() for i in by_country[country]["cities"][city]}
        nm = r["name"] or r["name_en"]
        if nm.lower() not in names:
            by_country[country]["cities"][city].append(
                {"name": nm, "lat": r["lat"], "lon": r["lon"]})
            by_country[country]["count"] += 1

    OUT.write_text(json.dumps(
        {"generated_from": "partners.db (OSM crawl)", "local_city": CITY,
         "categories": cats, "hospitals_by_country": by_country},
        ensure_ascii=False, indent=2))
    loc = sum(c["count"] for c in cats.values())
    hosp = sum(c["count"] for c in by_country.values())
    print(f"directory_public.json: {loc} CM facilities + {hosp} hospitals across "
          f"{len(by_country)} countries → {OUT.name}")


if __name__ == "__main__":
    run()
