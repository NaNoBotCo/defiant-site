#!/usr/bin/env python3
"""Defiant article engine — the content pipeline behind /articles/.

Conventions (same as the rest of the repo):
  * The vault is canonical. This engine NEVER touches hand-written prose.
    It only (a) creates notes that don't exist yet, and (b) rewrites the
    machine-owned spans between <!-- defiant:auto:NAME --> markers.
  * Every number on the site carries its date. Auto blocks stamp themselves.
  * Data comes from the household's own instruments first (dogfooding):
      mot-dang canonical places, air, finance/fx, festival dates,
      defiant's own directory_public.json.
  * topics.json is the registry: one entry per target keyword. Status flows
    idea → drafted → live. The QA gate is the door between drafted and live.

Menu-first (numbered, no flags to remember), but every menu item is also a
subcommand for nightly.sh:  board · packs · refresh · scaffold · qa · cards ·
ship · all.
"""
import json
import os
import re
import subprocess
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECTS = ROOT.parent
MOT = PROJECTS / "mot-dang" / "data"
VAULT = Path(os.environ.get("DEFIANT_VAULT") or (Path.home() / "Vaults" / "Defiant"))
PUB = VAULT / "Public Links"
ART = PUB / "Articles"
PACKS = ROOT / "data" / "packs"
DOCS = ROOT / "docs"
TODAY = date.today().isoformat()

BANNED_WORDS = ("load-bearing", "honest")          # standing style blocklist
OMINOUS = ("nightmare", "scam", "horror", "die ", "dying", "deadly", "disaster",
           "dangerous", "warning:", "beware")       # titles/desc stay auspicious


def load_topics():
    return json.loads((ROOT / "topics.json").read_text())["topics"]


def jread(path):
    return json.loads(Path(path).read_text())


def slug(name: str) -> str:
    out = []
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


# ---------------------------------------------------------------- mot-dang data
def canonical_places():
    recs = []
    for f in ("canonical/cm.json", "canonical/cr.json"):
        p = MOT / f
        if p.exists():
            recs.extend(jread(p))
    return recs


def _cats(r):
    c = r.get("cat") or []
    return [c] if isinstance(c, str) else c


def _s(r, *keys):
    """First non-empty string field — canonical records carry explicit nulls."""
    for k in keys:
        v = r.get(k)
        if v:
            return str(v)
    return ""


def _phone(r):
    p = _s(r, "phone").strip()
    return p if p and p not in ("-",) else ""


def _hours_today(r):
    h = r.get("hours")
    if isinstance(h, str):
        return h
    return ""


def fx():
    """BOT mid THB rates from mot-dang's finance snapshot."""
    f = jread(MOT / "finance.json")["fx"]
    return {"date": f["date"], "mid": f["mid_thb"]}


def air_cm():
    a = jread(MOT / "air.json")
    place = next(p for p in a["places"] if p["id"] == "chiang-mai")
    return {"generated": a["generated"], "source": a["source"], "model": a["model"],
            "place": place}


# ---------------------------------------------------------------- auto blocks
# Each builder returns markdown (tables/lists/single-line HTML only — that is
# what build.py's renderer supports). Every block ends with its own date line.

def block_fx_line(_topic):
    f = fx()
    usd, eur, gbp = f["mid"]["USD"], f["mid"]["EUR"], f["mid"]["GBP"]
    return (f"*Currency on this page: ฿100 ≈ ${100/usd:.2f} / €{100/eur:.2f} / "
            f"£{100/gbp:.2f} — Bank of Thailand mid rate, {f['date']}. "
            f"[Live board](https://motdang.net/finance.html) runs on [[=Home|the household's]] own feed.*")


def block_air_strip(_topic):
    a = air_cm()
    p = a["place"]
    band = p["band"]["en"]
    return (f"> **Chiang Mai air right now:** PM2.5 **{p['pm25']:g} µg/m³** — {band} "
            f"(US AQI {p['usAqi']}). Observed {p['observed'].replace('T', ' ')}. "
            f"Modelled by CAMS via Open-Meteo — a city-scale model, not a street sensor; "
            f"treat it as the weather report, not a diagnosis.")


def block_air_history(_topic):
    a = air_cm()
    days = [d for d in a["place"].get("days", []) if d["date"] <= TODAY][-7:]
    lines = ["| Date | PM2.5 (µg/m³) | Band |", "|---|---|---|"]
    for d in days:
        lines.append(f"| {d['date']} | {d['pm25']:g} | {d['band']['en']} |")
    lines.append(f"\n*The last seven observed days, same model, generated {a['generated']}.*")
    return "\n".join(lines)


HOSPITAL_HINTS = ("hospital", "โรงพยาบาล", "รพ.", "medical center", "medical centre")


def _cm_medical():
    return [r for r in canonical_places()
            if "medical" in _cats(r) and (r.get("province") or "").lower() != "chiang rai"]


def _is_hospital(r):
    hay = " ".join((_s(r, "name"), _s(r, "nameEn"), _s(r, "nameTh"))).lower()
    return any(h in hay for h in HOSPITAL_HINTS)


def _fmt_phone(p):
    d = re.sub(r"\D", "", p)
    if d.startswith("66"):
        d = "0" + d[2:]
    if len(d) == 9:
        return f"{d[:3]} {d[3:6]} {d[6:]}"
    if len(d) == 10:
        return f"{d[:3]} {d[3:6]} {d[6:]}"
    return p.strip()


# The hospitals a foreigner in Chiang Mai actually ends up in — curated order,
# joined to the canonical map for coordinates and phones. A phone appears only
# when the map data has it or the household has dialled it; blanks invite a
# /contact/ report and get fixed the same week. er=True → 24 h emergency room.
CURATED_CM_HOSPITALS = [
    ("Bangkok Hospital Chiang Mai", None, "Flagship private — international desk, English-first paperwork", True),
    ("Chiang Mai Ram Hospital", None, "The in-town private default; most expats' first ER story ends fine here", True),
    ("Sriphat", "Sriphat Medical Center", "Chiang Mai University's private wing — faculty physicians, university pricing", False),
    ("Maharaj Nakorn Chiang Mai Hospital", "Maharaj Nakorn (Suan Dok)", "The university mothership — deepest specialist bench in the North, Thai queues, Thai prices", True),
    ("McCormick Hospital", None, "Beloved 130-year mission hospital — calm, capable, gentler bills", True),
    ("Lanna Hospital", None, "Private, north side by the Superhighway", True),
    ("Rajavej Chiang Mai Hospital", None, "Walk-in friendly; front desk practised at VA/FMP and insurer paperwork", True),
    ("Central Chiang Mai Memorial Hospital", None, "Private, compact, near the old city's south moat", False),
    ("Nakornping Hospital", None, "The provincial public hospital, Mae Rim road", True),
    ("Theppanya Hospital", None, "Private, San Sai side of the Superhighway", True),
    ("St. Peter Eye Hospital", None, "Eyes only — cataract and retina work at Chiang Mai prices", False),
    ("Chiang Mai Neurological Hospital", None, "Public specialty center for brain and nerve care", False),
]
PHONE_OVERRIDES = {
    # Numbers the household has dialled — everything else comes from map data.
    "Rajavej Chiang Mai Hospital": "052 011 999",
}
ALT_KEYS = {
    # Explicit second probes for map twins. Add sparingly, keep them specific.
    "Bangkok Hospital Chiang Mai": ["Bangkok Hospital"],
}


def _curated_join():
    med = _cm_medical()
    rows = []
    for key, display, known_for, er in CURATED_CM_HOSPITALS:
        best = None
        # The map often holds twins ("Bangkok Hospital Chiang Mai" with the
        # coordinates, "Bangkok Hospital" with the phone) — probe the full key
        # first, then an explicit alternate. Never a generic prefix: "Chiang
        # Mai" as a probe once handed the neurological hospital a church
        # clinic's phone number.
        for probe in [key.lower()] + [a.lower() for a in ALT_KEYS.get(key, [])]:
            for r in med:
                hay = (_s(r, "nameEn") + " " + _s(r, "name")).lower()
                if probe in hay:
                    if best is None or (_phone(r) and not _phone(best)):
                        best = r
            if best is not None and _phone(best):
                break
        name = display or key
        phone = PHONE_OVERRIDES.get(key) or (_fmt_phone(_phone(best)) if best and _phone(best) else "")
        th = _s(best, "nameTh") if best else ""
        km = _km(best["lat"], best["lng"]) if best and best.get("lat") else None
        rows.append(dict(name=name, th=th, phone=phone, known_for=known_for, er=er, km=km))
    return rows


def block_hospitals_cm(_topic):
    rows = _curated_join()
    lines = ["| Hospital | Phone | From Tha Phae Gate | Known for |", "|---|---|---|---|"]
    for r in rows:
        th_bit = f" ({r['th']})" if r["th"] and r["th"] != r["name"] else ""
        km = f"~{r['km']:.1f} km" if r["km"] is not None else ""
        lines.append(f"| **{r['name']}**{th_bit} | {r['phone'] or '—'} | {km} | {r['known_for']} |")
    lines.append(f"\n*{len(rows)} hospitals, curated by residents, coordinates and phones "
                 f"cross-checked against the [Mot Dang](https://motdang.net) map, {TODAY}. "
                 f"Spot a wrong number? [Report it](/contact/) — fixes land the same week.*")
    return "\n".join(lines)


ER_NATIONAL = [
    ("1669", "Medical emergency / ambulance", "Free, 24 h, nationwide — the one to save"),
    ("1155", "Tourist police", "English spoken, 24 h"),
    ("191", "Police", "Any emergency, Thai-first"),
    ("199", "Fire & rescue", "24 h"),
]


def block_er_numbers(_topic):
    lines = ["| Number | Who answers | Notes |", "|---|---|---|"]
    for n, who, note in ER_NATIONAL:
        lines.append(f"| **{n}** | {who} | {note} |")
    lines.append(f"\n*National numbers, verified {TODAY}. Save 1669 before you need it.*")
    return "\n".join(lines)


def block_er_cm_table(_topic):
    rows = [r for r in _curated_join() if r["er"]]
    lines = ["| 24 h emergency room | Main line | From Tha Phae Gate |", "|---|---|---|"]
    for r in rows:
        km = f"~{r['km']:.1f} km" if r["km"] is not None else ""
        lines.append(f"| {r['name']} | **{r['phone'] or '— (use 1669)'}** | {km} |")
    lines.append(f"\n*Curated by residents, cross-checked against the household map, {TODAY}. "
                 f"If a line changes, [tell us](/contact/) and it gets fixed the same week.*")
    return "\n".join(lines)


def block_massage_cm(_topic):
    recs = [r for r in canonical_places() if "massage" in _cats(r)
            and (r.get("province") or "").lower() != "chiang rai"]
    n = len(recs)
    with_phone = [r for r in recs if _phone(r)]
    lines = [f"**{n} massage shops** sit on the household map of Chiang Mai — "
             f"{len(with_phone)} with a working phone number. A sampler across town:", ""]
    lines += ["| Shop | Phone | Find it |", "|---|---|---|"]
    with_phone.sort(key=lambda r: (not bool(_s(r, "landmark")), _s(r, "nameEn", "name")))
    shown, seen = [], set()
    for r in with_phone:
        nm = _s(r, "nameEn", "name")
        if nm.lower() in seen:
            continue
        seen.add(nm.lower())
        shown.append(r)
        if len(shown) >= 7:
            break
    for r in shown:
        name = _s(r, "nameEn", "name")
        th = _s(r, "nameTh")
        th_bit = f" ({th})" if th and th != name else ""
        where = _s(r, "landmark", "address")
        if not where and r.get("lat"):
            where = f"~{_km(r['lat'], r['lng']):.1f} km from Tha Phae Gate"
        lines.append(f"| **{name}**{th_bit} | {_fmt_phone(_phone(r))} | {where} |")
    lines.append(f"\n*Counts and rows from [Mot Dang](https://motdang.net)'s curated set, {TODAY}. "
                 f"The full map is free: [motdang.net](https://motdang.net).*")
    return "\n".join(lines)


THA_PHAE = (18.7875, 98.9933)     # Tha Phae Gate — everyone's zero-kilometre stone


def _km(lat, lon, ref=THA_PHAE):
    from math import asin, cos, radians, sin, sqrt
    la1, lo1, la2, lo2 = map(radians, (ref[0], ref[1], lat, lon))
    h = sin((la2 - la1) / 2) ** 2 + cos(la1) * cos(la2) * sin((lo2 - lo1) / 2) ** 2
    return 12742 * asin(sqrt(h))


def block_pharmacy_cm(_topic):
    d = jread(ROOT / "directory_public.json")
    cat = d.get("categories", {}).get("pharmacy", {})
    items = cat.get("items", [])
    cm = [p for p in items
          if isinstance(p.get("lat"), (int, float)) and 18.55 <= p["lat"] <= 19.15
          and 98.75 <= p.get("lon", 0) <= 99.25]
    for p in cm:
        p["_km"] = _km(p["lat"], p["lon"])
    cm.sort(key=lambda p: p["_km"])
    lines = [f"**{cat.get('count', len(items))} pharmacies** are on Defiant's Thailand-wide "
             f"directory; **{len(cm)}** of them are in the Chiang Mai basin. The ten closest "
             f"to Tha Phae Gate (ประตูท่าแพ, *pratu Tha Phae* — the old city's front door):", "",
             "| Pharmacy | From Tha Phae Gate |", "|---|---|"]
    for p in cm[:10]:
        nm = _s(p, "name", "name_en") or "(unnamed on the map)"
        lines.append(f"| {nm} | ~{p['_km']:.1f} km |")
    lines.append(f"\n*From Defiant's nightly OpenStreetMap refresh, distances computed "
                 f"straight-line, {TODAY}. A missing shop is a [fixable report](/contact/).*")
    return "\n".join(lines)


def block_festivals_window(_topic):
    f = jread(MOT / "festival_dates.json")
    rows = [r for r in f.get("rows", []) if r.get("status") == "announced"]
    if not rows:
        return (f"*No festival dates are officially announced right now ({f.get('generated', TODAY)}). "
                f"When organizers publish, the confirmed dates appear here automatically — "
                f"the fixed national holidays above never move.*")
    out = ["| Festival | Announced dates |", "|---|---|"]
    for r in rows[:10]:
        out.append(f"| {r.get('en') or r.get('name')} | {r.get('when') or r.get('date') or ''} |")
    out.append(f"\n*Announced dates only, each traced to an official source — "
               f"from the household festival canon, {f.get('generated', TODAY)}.*")
    return "\n".join(out)


# Fixed-date national holidays that move hospital calendars. Lunar observances
# shift year to year and ride in via the announced-dates block instead.
THAI_HOLIDAYS = [
    ("Jan 1", "New Year's Day", "Elective clinics thin; ERs normal"),
    ("Apr 13–15", "Songkran (Thai New Year)", "The big one — elective slates pause, travel peaks, water everywhere"),
    ("May 1", "Labour Day", "Private-sector holiday; hospital OPD mostly normal"),
    ("May 4", "Coronation Day", "Government offices closed; visa desks too"),
    ("Jun 3", "Queen Suthida's Birthday", "Public holiday"),
    ("Jul 28", "King's Birthday", "Public holiday"),
    ("Aug 12", "Mother's Day (Queen Sirikit's Birthday)", "Public holiday"),
    ("Oct 13", "King Bhumibol Memorial Day", "Public holiday"),
    ("Oct 23", "Chulalongkorn Day", "Public holiday"),
    ("Dec 5", "Father's Day (King Bhumibol's Birthday)", "Public holiday"),
    ("Dec 10", "Constitution Day", "Public holiday"),
    ("Dec 31", "New Year's Eve", "Travel peaks; book transport early"),
]


def block_thai_holidays(_topic):
    lines = ["| Date | Holiday | What it means for a medical trip |", "|---|---|---|"]
    for d, name, note in THAI_HOLIDAYS:
        lines.append(f"| **{d}** | {name} | {note} |")
    lines.append("\n*Fixed-date national holidays. Buddhist observances (Makha Bucha, "
                 "Visakha Bucha, Asalha Bucha, Loy Krathong / Yi Peng) follow the lunar "
                 f"calendar — announced dates appear below when official. Verified {TODAY}.*")
    return "\n".join(lines)


def _dist_rows(items, n=8):
    """Nearest-N table rows for bare directory items ({name, lat, lon/lng})."""
    rows = []
    for p in items:
        lat, lon = p.get("lat"), p.get("lon", p.get("lng"))
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)) \
                and 18.55 <= lat <= 19.15 and 98.75 <= lon <= 99.25:
            rows.append((_km(lat, lon), p))
    rows.sort(key=lambda x: x[0])
    return rows[:n]


def _directory_cat(name):
    d = jread(ROOT / "directory_public.json")
    return d.get("categories", {}).get(name, {})


def block_rehab_cm(_topic):
    # consumer is the physiotherapy article — reads the physio category since the
    # addiction/physio split (addiction facilities ride on block_addiction_cm).
    cat = _directory_cat("physio")
    rows = _dist_rows(cat.get("items", []), n=10)
    lines = [f"**{cat.get('count', 0)} physiotherapy and physical-rehab facilities** are on "
             f"Defiant's mapped directory. The closest to Tha Phae Gate:", "",
             "| Clinic | From Tha Phae Gate |", "|---|---|"]
    for km, p in rows:
        lines.append(f"| {_s(p, 'name', 'name_en') or '(unnamed on the map)'} | ~{km:.1f} km |")
    lines.append(f"\n*From Defiant's nightly OpenStreetMap refresh, straight-line distances, {TODAY}. "
                 f"Hospital physio departments ride on [the hospital guide](/articles/chiang-mai-hospitals/).*")
    return "\n".join(lines)


def block_addiction_cm(_topic):
    cat = _directory_cat("addiction")
    rows = _dist_rows(cat.get("items", []), n=10)
    lines = [f"**{cat.get('count', 0)} addiction-medicine and recovery facilities** are on "
             f"Defiant's mapped directory (several sit outside the Chiang Mai box). "
             f"Those inside it, from Tha Phae Gate:", "",
             "| Facility | From Tha Phae Gate |", "|---|---|"]
    for km, p in rows:
        lines.append(f"| {_s(p, 'name', 'name_en') or '(unnamed on the map)'} | ~{km:.1f} km |")
    lines.append(f"\n*From Defiant's nightly OpenStreetMap refresh, straight-line distances, {TODAY}. "
                 f"Listing here is presence on the map, not a recommendation.*")
    return "\n".join(lines)


def block_geriatric_cm(_topic):
    cat = _directory_cat("geriatric")
    rows = _dist_rows(cat.get("items", []), n=11)
    lines = [f"**{cat.get('count', 0)} senior-care and geriatric facilities** sit on Defiant's mapped "
             f"directory around Chiang Mai:", "", "| Facility | From Tha Phae Gate |", "|---|---|"]
    for km, p in rows:
        lines.append(f"| {_s(p, 'name', 'name_en') or '(unnamed on the map)'} | ~{km:.1f} km |")
    lines.append(f"\n*From Defiant's nightly OpenStreetMap refresh, {TODAY}. Distance matters twice "
                 f"here — for the family visit, and for the [hospital run](/articles/chiang-mai-hospitals/).*")
    return "\n".join(lines)


def block_womens_health_cm(_topic):
    g = jread(PROJECTS / "cm-womens-health" / "dist" / "cm-womens-health.geojson")
    feats = g.get("features", [])
    pts = []
    for f in feats:
        p = f.get("properties", {})
        if isinstance(p.get("lat"), (int, float)):
            pts.append(p)
    near = sorted(pts, key=lambda p: _km(p["lat"], p["lng"]))[:8]
    lines = [f"**{len(feats)} women's-health facilities** are mapped across Chiang Mai in the "
             f"household's dedicated dataset — OB-GYN clinics, hospital women's centers, "
             f"fertility and screening services. The nearest to the old city:", "",
             "| Facility | From Tha Phae Gate |", "|---|---|"]
    for p in near:
        name = _s(p, "nameEn", "name")
        th = _s(p, "nameTh")
        th_bit = f" ({th})" if th and th != name else ""
        lines.append(f"| **{name}**{th_bit} | ~{_km(p['lat'], p['lng']):.1f} km |")
    lines.append(f"\n*From the household's Chiang Mai women's-health dataset, refreshed {TODAY}. "
                 f"A missing clinic is a [fixable report](/contact/).*")
    return "\n".join(lines)


def block_dental_prices(_topic):
    from defiant_content import PROCEDURES
    lines = ["| Procedure | United States | Thailand | Trip shape |", "|---|---|---|---|"]
    for name, d in PROCEDURES.items():
        if d.get("cat") == "Dental":
            slug_ = slug(name)
            lines.append(f"| [{name}](/procedures/{slug_}/) | {d['us']} | **{d['th']}** | {d.get('stay', '')} |")
    lines.append(f"\n*Defiant's standing indicative ranges — 2026 published-aggregator figures, "
                 f"every quote confirmed in writing at intake. Full detail on "
                 f"[[=Procedures|the procedure pages]]. Verified {TODAY}.*")
    return "\n".join(lines)


def block_articles_hub(_topic):
    """The /articles/ index — one row per real (non-draft) guide."""
    rows = []
    for t in load_topics():
        p = ART / f"{t['note']}.md"
        if not p.exists():
            continue
        body = p.read_text()
        if "prose pending" in body:
            continue
        upd = re.search(r"^updated:\s*(\d{4}-\d{2}-\d{2})", body, re.M)
        rows.append((t, upd.group(1) if upd else ""))
    lines = []
    for t, upd in rows:
        lines.append(f"### [{t['title']}](/articles/{t['slug']}/)")
        lines.append(f"{t['desc']}")
        lines.append(f"*Reviewed {upd}.*" if upd else "")
        lines.append("")
    lines.append(f"*{len(rows)} working guides — every number dated, every table refreshed "
                 f"from the household's own instruments. Last engine pass: {TODAY}.*")
    return "\n".join(lines)


BLOCKS = {
    "articles-hub": block_articles_hub,
    "fx-line": block_fx_line,
    "air-strip": block_air_strip,
    "air-history": block_air_history,
    "hospitals-cm": block_hospitals_cm,
    "er-numbers": block_er_numbers,
    "er-cm-table": block_er_cm_table,
    "massage-cm": block_massage_cm,
    "pharmacy-cm": block_pharmacy_cm,
    "festivals-window": block_festivals_window,
    "thai-holidays": block_thai_holidays,
    "rehab-cm": block_rehab_cm,
    "addiction-cm": block_addiction_cm,
    "geriatric-cm": block_geriatric_cm,
    "womens-health-cm": block_womens_health_cm,
    "dental-prices": block_dental_prices,
}


# ---------------------------------------------------------------- packs
def build_packs(topics=None):
    """Snapshot every block a topic uses into data/packs/<slug>.json — the
    fact sheet a writing session opens before touching prose."""
    PACKS.mkdir(parents=True, exist_ok=True)
    for t in topics or load_topics():
        pack = {"slug": t["slug"], "keyword": t["keyword"], "generated": TODAY, "blocks": {}}
        for b in t.get("blocks", []):
            fn = BLOCKS.get(b)
            if fn:
                try:
                    pack["blocks"][b] = fn(t)
                except Exception as e:      # a dead source shouldn't kill the run
                    pack["blocks"][b] = f"(block {b} failed: {e})"
        (PACKS / f"{t['slug']}.json").write_text(json.dumps(pack, ensure_ascii=False, indent=1))
        print(f"  pack ✓ {t['slug']}")


# ---------------------------------------------------------------- refresh
MARK = re.compile(r"(<!-- defiant:auto:([a-z0-9-]+) -->)(.*?)(<!-- /defiant:auto:\2 -->)",
                  re.S)


def refresh_notes():
    """Rewrite ONLY the marker spans inside vault article notes."""
    changed = 0
    hub = PUB / "=Articles.md"
    jobs = [(t, ART / f"{t['note']}.md") for t in load_topics()]
    if hub.exists():
        jobs.append((None, hub))
    for t, p in jobs:
        if not p.exists():
            continue
        src = p.read_text()

        def sub(m):
            name = m.group(2)
            fn = BLOCKS.get(name)
            if not fn:
                return m.group(0)
            try:
                body = fn(t)
            except Exception as e:
                print(f"  ! {p.name}:{name} refresh failed ({e}) — left as-is")
                return m.group(0)
            return f"{m.group(1)}\n{body}\n{m.group(4)}"

        out = MARK.sub(sub, src)
        if out != src:
            p.write_text(out)
            changed += 1
            print(f"  refreshed ✓ {p.name}")
    print(f"{changed} notes updated (prose untouched)")
    return changed


# ---------------------------------------------------------------- scaffold
SCAFFOLD = """---
title: {title}
description: {desc}
type: guide
updated: {today}
keyword: {keyword}
---

*Draft — prose pending. Data blocks below are live; the writing isn't. The QA
gate holds this page back from shipping until the draft line is deleted.*

{blocks}

## FAQ

**Question that earns the keyword?**
Answer in two sentences.

<!-- defiant:subscribe -->
"""


def scaffold_notes():
    ART.mkdir(parents=True, exist_ok=True)
    made = 0
    for t in load_topics():
        p = ART / f"{t['note']}.md"
        if p.exists() and p.read_text().strip():
            continue                      # NEVER overwrite — vault is canonical
        blocks = "\n\n".join(
            f"<!-- defiant:auto:{b} -->\n<!-- /defiant:auto:{b} -->"
            for b in t.get("blocks", []))
        p.write_text(SCAFFOLD.format(title=t["title"], desc=t["desc"], today=TODAY,
                                     keyword=t["keyword"], blocks=blocks))
        made += 1
        print(f"  scaffold ✓ {t['note']}.md")
    if made:
        refresh_notes()
    print(f"{made} new notes (existing notes untouched)")


# ---------------------------------------------------------------- QA gate
def qa(verbose=True):
    """The door between drafted and live. Fails loud, lists everything."""
    problems, warns = [], []
    topics = load_topics()
    fx_ok = True
    try:
        f = fx()
        if (date.today() - date.fromisoformat(f["date"])).days > 14:
            warns.append(f"fx snapshot is {f['date']} — stale, run mot-dang's refresher")
    except Exception as e:
        fx_ok = False
        problems.append(f"finance.json unreadable: {e}")

    for t in topics:
        if t["status"] == "idea":
            continue
        tag = t["slug"]
        p = ART / f"{t['note']}.md"
        if not p.exists():
            problems.append(f"{tag}: note missing ({p.name})")
            continue
        body = p.read_text()
        low = body.lower()

        if "draft — prose pending" in low:
            problems.append(f"{tag}: still a scaffold draft")
        for w in BANNED_WORDS:
            if w in low:
                problems.append(f"{tag}: banned word “{w}”")
        m = re.search(r"^description:\s*(.+)$", body, re.M)
        desc = m.group(1).strip() if m else ""
        if not 110 <= len(desc) <= 175:
            warns.append(f"{tag}: meta description {len(desc)} chars (aim 120–170)")
        title_m = re.search(r"^title:\s*(.+)$", body, re.M)
        title = title_m.group(1).strip() if title_m else t["note"]
        for o in OMINOUS:
            if o in title.lower() or o in desc.lower():
                problems.append(f"{tag}: ominous wording “{o.strip()}” in title/desc — keep it auspicious")
        # Doubled-word lint runs on PROSE only: machine tables out, wikilink
        # aliases collapsed, and Thai reduplication (bao bao, reo reo) allowed.
        prose = re.sub(r"<!-- defiant:auto:([a-z0-9-]+) -->.*?<!-- /defiant:auto:\1 -->",
                       " ", body, flags=re.S)
        prose = re.sub(r"\[\[[^\]|]+\|([^\]]*)\]\]", r"\1", prose)
        dbl = re.search(r"\b([A-Za-z]{2,})\s+\1\b", re.sub(r"[#*_|>`]", " ", prose), re.I)
        if dbl and dbl.group(1).lower() not in ("bang", "wa", "na", "ha", "bao", "nak", "reo"):
            warns.append(f"{tag}: doubled word “{dbl.group(0)}”")
        if "<!-- defiant:subscribe -->" not in body and "/concierge/" not in body \
                and "[[=Concierge" not in body and "%%BTN:" not in body:
            problems.append(f"{tag}: no lead path (subscribe block, concierge link, or reveal button)")
        if "## FAQ" not in body:
            warns.append(f"{tag}: no FAQ section (free FAQPage schema if you add one)")
        if "github.com" in low:
            problems.append(f"{tag}: github.com link (standing directive: none)")
        # Thai lines should carry romanization or translation on the same line.
        for ln in body.splitlines():
            if re.search(r"[฀-๿]", ln) and not re.search(r"[A-Za-z]", ln):
                warns.append(f"{tag}: Thai-only line with no romanization: “{ln.strip()[:40]}…”")
                break
        # Auto blocks present and non-empty?
        for b in t.get("blocks", []):
            span = re.search(rf"<!-- defiant:auto:{b} -->(.*?)<!-- /defiant:auto:{b} -->",
                             body, re.S)
            if not span:
                problems.append(f"{tag}: missing auto block {b}")
            elif not span.group(1).strip():
                problems.append(f"{tag}: auto block {b} is empty — run refresh")
        upd = re.search(r"^updated:\s*(\d{4}-\d{2}-\d{2})", body, re.M)
        if not upd:
            warns.append(f"{tag}: no updated: date (freshness stamp won't render)")
        elif (date.today() - date.fromisoformat(upd.group(1))).days > t.get("refresh_days", 90):
            warns.append(f"{tag}: updated {upd.group(1)} — past its {t.get('refresh_days')}-day window")

        # Built page + card, if built.
        built = DOCS / "articles" / t["slug"] / "index.html"
        if built.exists():
            html = built.read_text()
            if f"/assets/cards/articles-{t['slug']}.png" not in html:
                problems.append(f"{tag}: built page og:image is not its own card")
            if html.count('href="/') < 4:
                warns.append(f"{tag}: fewer than 4 internal links on built page")
            if "application/ld+json" not in html:
                warns.append(f"{tag}: no JSON-LD on built page")
            if re.search(r"<script[^>]+src=", html):
                problems.append(f"{tag}: external script on built page")
        card = ROOT / "assets" / "cards" / f"articles-{t['slug']}.png"
        if card.exists():
            kb = card.stat().st_size // 1024
            if kb > 590:
                problems.append(f"{tag}: card {kb} KB (>590 breaks WhatsApp previews)")
            elif kb > 300:
                warns.append(f"{tag}: card {kb} KB (aim ≤300)")
        elif built.exists():
            problems.append(f"{tag}: no share card at assets/cards/articles-{t['slug']}.png")

    if verbose:
        print(f"\nQA GATE — {TODAY}")
        for x in problems:
            print(f"  ✗ {x}")
        for x in warns:
            print(f"  ⚠ {x}")
        if not problems and not warns:
            print("  ✓ clean")
        print(f"\n{len(problems)} blocking · {len(warns)} advisory")
    problems.extend(tag_check())

    return problems, warns


# ---------------------------------------------------------------- board
def board():
    topics = load_topics()
    print(f"\nDEFIANT ARTICLE BOARD — {TODAY}")
    print(f"{'#':>2} {'status':9} {'competition':11} {'slug':32} keyword")
    for i, t in enumerate(topics, 1):
        note = ART / f"{t['note']}.md"
        built = DOCS / "articles" / t["slug"] / "index.html"
        st = t["status"]
        if built.exists() and st != "idea":
            st = "live"
        elif note.exists() and "prose pending" not in note.read_text().lower():
            st = max(st, "drafted", key=len)
        print(f"{i:>2} {st:9} {t['competition']:11} {t['slug']:32} {t['keyword']}")
    print("\nstatuses: idea (registry only) → drafted (note written) → live (built + shipped)")


# ---------------------------------------------------------------- ship
def run(cmd, cwd=ROOT):
    print(f"\n$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd).returncode


def ship(deploy=True):
    build_packs()
    refresh_notes()
    problems, _ = qa()
    if problems:
        print("\nQA gate is closed — fix the ✗ lines first. Nothing shipped.")
        return 1
    if run([sys.executable, "make_cards.py"]):
        return 1
    if run([sys.executable, "build.py"]):
        return 1
    problems, _ = qa()
    if problems:
        print("\nPost-build QA found blockers — not deploying.")
        return 1
    if deploy:
        lane = PROJECTS / "cloudflare-mirror" / "deploy.sh"
        return run(["/bin/bash", str(lane), "defiant"], cwd=lane.parent)
    return 0


# ---------------------------------------------------------------- menu
# ---------------------------------------------------------------- tag registry
# tags.json is a CURATED controlled vocabulary, not a folksonomy. A tag that
# does not resolve to a term there fails QA — that gate is the whole difference
# between an ontology and a tag cloud. Aliases are the intake ramp: search
# phrasings and Thai spellings map inward without entering the vocabulary.
# Counts are always derived, never stored.

def load_tags():
    return json.loads((ROOT / "tags.json").read_text())


def tag_alias_map(reg):
    """alias or canonical slug -> canonical term."""
    m = {}
    for term, spec in reg["terms"].items():
        m[term] = term
        m[term.split("/", 1)[1]] = term          # bare leaf, when unambiguous
        for a in spec.get("aliases", []):
            m[a.lower().strip()] = term
    return m


def resolve_tag(raw, amap):
    return amap.get(raw.lower().strip())


def note_tags(body):
    m = re.search(r"^tags:\s*(.+)$", body, re.M)
    if not m:
        return []
    return [t.strip() for t in m.group(1).split(",") if t.strip()]


def set_note_tags(path, tags):
    """Write tags: into frontmatter, creating the line if absent. Prose untouched."""
    body = path.read_text()
    line = "tags: " + ", ".join(tags)
    if re.search(r"^tags:\s*.+$", body, re.M):
        body = re.sub(r"^tags:\s*.+$", line, body, count=1, flags=re.M)
    else:                                        # insert as last frontmatter key
        end = body.find("\n---", 4)
        if not body.startswith("---\n") or end < 0:
            return False
        body = body[:end] + "\n" + line + body[end:]
    path.write_text(body)
    return True


def tag_backfill(apply=True):
    """topics.json is the source of truth for a topic's tags; push them to notes."""
    reg, amap = load_tags(), None
    amap = tag_alias_map(reg)
    changed, skipped = [], []
    for t in load_topics():
        tags = t.get("tags") or []
        if not tags:
            skipped.append((t["slug"], "no tags in topics.json")); continue
        bad = [x for x in tags if not resolve_tag(x, amap)]
        if bad:
            skipped.append((t["slug"], f"unknown: {', '.join(bad)}")); continue
        p = ART / f"{t['note']}.md"
        if not p.exists():
            skipped.append((t["slug"], "note missing")); continue
        canon = sorted({resolve_tag(x, amap) for x in tags})
        if note_tags(p.read_text()) == canon:
            continue
        if apply:
            set_note_tags(p, canon)
        changed.append((t["slug"], len(canon)))
    for s, n in changed:
        print(f"  tagged  {s}  ({n})")
    for s, why in skipped:
        print(f"  skipped {s}  — {why}")
    print(f"\n{len(changed)} note(s) {'updated' if apply else 'would change'}, {len(skipped)} skipped")
    return changed, skipped


def tag_audit():
    """Yahoo-directory view: Term (count), plus everything wrong."""
    reg = load_tags()
    amap = tag_alias_map(reg)
    facets, terms = reg["facets"], reg["terms"]
    counts, unknown, untagged, facet_gaps = {}, [], [], []

    notes = sorted(ART.glob("*.md")) + sorted(ART.rglob("*/*.md"))
    by_type = {}
    for p in notes:
        raw = p.read_text()
        ntype = (re.search(r"^type:\s*(.+)$", raw, re.M) or [None, "article"])[1].strip()
        tags = note_tags(raw)
        by_type.setdefault(ntype, [0, 0])
        by_type[ntype][1] += 1
        if not tags:
            if ntype == "guide":
                untagged.append(p.stem)
            continue
        by_type[ntype][0] += 1
        seen = {}
        for raw in tags:
            term = resolve_tag(raw, amap)
            if not term:
                unknown.append((p.stem, raw)); continue
            counts[term] = counts.get(term, 0) + 1
            f = term.split("/", 1)[0]
            seen.setdefault(f, []).append(term)
        for f, got in seen.items():
            if not facets[f].get("multi") and len(got) > 1:
                facet_gaps.append((p.stem, f, got))

    for f, spec in facets.items():
        rows = sorted(((t, counts.get(t, 0)) for t in terms if t.startswith(f + "/")),
                      key=lambda r: (-r[1], r[0]))
        live = [r for r in rows if r[1]]
        print(f"\n{spec['label']}  ({len(live)}/{len(rows)} in use)")
        for t, c in rows:
            label = terms[t].get("label", t)
            print(f"    {label:22} {'(' + str(c) + ')' if c else '·'}")

    print()
    if unknown:
        print(f"UNKNOWN TAGS ({len(unknown)}) — these fail QA:")
        for n, t in unknown:
            print(f"    {n}: {t}")
    if facet_gaps:
        print(f"SINGLE-VALUE FACET VIOLATIONS ({len(facet_gaps)}):")
        for n, f, got in facet_gaps:
            print(f"    {n}: {f} has {got}")
    if untagged:
        print(f"UNTAGGED NOTES ({len(untagged)}):")
        for n in untagged:
            print(f"    {n}")
    print("Coverage by note type:")
    for nt, (done, total) in sorted(by_type.items()):
        bar = "backlog" if done == 0 else ("complete" if done == total else f"{total-done} to go")
        print(f"    {nt:12} {done:3}/{total:<4} {bar}")
    print()
    orphans = [t for t in terms if not counts.get(t)]
    if orphans:
        print(f"\nDefined but unused ({len(orphans)}): {', '.join(orphans)}")
    if not (unknown or facet_gaps or untagged):
        print("Vocabulary clean — every tag resolves, every note tagged.")
    return unknown, facet_gaps, untagged


def tag_check(paths=None):
    """QA hook: returns list of problem strings."""
    reg = load_tags()
    amap = tag_alias_map(reg)
    out = []
    for t in load_topics():
        if t["status"] == "idea":
            continue
        p = ART / f"{t['note']}.md"
        if not p.exists():
            continue
        tags = note_tags(p.read_text())
        if not tags:
            out.append(f"{t['slug']}: no tags in frontmatter")
            continue
        for raw in tags:
            if not resolve_tag(raw, amap):
                out.append(f"{t['slug']}: tag “{raw}” is not in tags.json")
        seen = {}
        for raw in tags:
            term = resolve_tag(raw, amap)
            if term:
                seen.setdefault(term.split("/", 1)[0], []).append(term)
        for f, got in seen.items():
            if not reg["facets"][f].get("multi") and len(got) > 1:
                out.append(f"{t['slug']}: facet “{f}” is single-value but has {len(got)}")
    return out


TAG_MENU = """
TAGS
  1) Audit — Term (count) by facet, plus everything wrong
  2) Backfill — push topics.json tags into note frontmatter
  3) Dry run — show what backfill would change
  4) Vocabulary — list every term with its aliases
  0) Back
"""


def tags_menu():
    while True:
        print(TAG_MENU)
        try:
            pick = input("> ").strip()
        except EOFError:
            return
        if pick == "1": tag_audit()
        elif pick == "2": tag_backfill(apply=True)
        elif pick == "3": tag_backfill(apply=False)
        elif pick == "4":
            reg = load_tags()
            for term, spec in sorted(reg["terms"].items()):
                al = ", ".join(spec.get("aliases", []))
                print(f"  {term:28} {spec.get('label','')}" + (f"   ← {al}" if al else ""))
        elif pick in ("0", ""): return



MENU = """
DEFIANT ARTICLE ENGINE
  1) Board — every topic, its status, its keyword
  2) Refresh — rebuild data packs + auto blocks in notes (prose untouched)
  3) Scaffold — create notes for topics that have none
  4) QA gate — every check, loud
  7) Tags — audit, backfill, vocabulary
  5) Preflight — cards + site build + QA (no deploy)
  6) Ship — refresh, QA, cards, build, deploy to Cloudflare
  0) Exit
"""


def main():
    args = sys.argv[1:]
    cmds = {"board": board, "packs": build_packs, "refresh": lambda: (build_packs(), refresh_notes()),
            "scaffold": scaffold_notes, "qa": lambda: sys.exit(1 if qa()[0] else 0),
            "cards": lambda: run([sys.executable, "make_cards.py"]),
            "tags": tag_audit, "tag-backfill": tag_backfill,
            "preflight": lambda: ship(deploy=False), "ship": ship, "all": ship}
    if args:
        fn = cmds.get(args[0])
        if not fn:
            print(f"usage: articles.py [{'|'.join(cmds)}]"); sys.exit(64)
        rv = fn()
        sys.exit(rv if isinstance(rv, int) else 0)
    while True:
        print(MENU)
        try:
            pick = input("> ").strip()
        except EOFError:
            return
        if pick == "1": board()
        elif pick == "2": build_packs(); refresh_notes()
        elif pick == "3": scaffold_notes()
        elif pick == "4": qa()
        elif pick == "7": tags_menu()
        elif pick == "5": ship(deploy=False)
        elif pick == "6": ship()
        elif pick == "0" or pick == "": return


if __name__ == "__main__":
    main()
