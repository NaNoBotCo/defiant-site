#!/usr/bin/env python3
"""Shared bits for the Defiant clinic-partners pipeline.

Pipeline statuses (one word, one meaning):
  new → shortlist | pass → drafted (dossier + letter exist) → translated →
  sent → replied → meeting → partner

Nothing in this package ever sends anything. Drafts are files; humans send.
"""
import json
import sqlite3
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / "partners.db"
DRAFTS = ROOT / "outreach" / "drafts"
VAULT_PARTNERS = Path.home() / "Documents" / "Defiant" / "Partners"  # NOT under Public Links → never published
TODAY = date.today().isoformat()

VERTICALS = ["hospital", "geriatric", "physio", "addiction", "rehab", "gyn", "longevity",
             "aesthetic", "pharmacy", "other"]

# Big chains are the anti-counterfeit answer for hormones; flag them so they
# rise to the top of the pharmacy list.
CHAIN_HINTS = ["boots", "watsons", "fascino", "pharmax", "save drug", "icare",
               "exta", "pure", "bignet", "แม็คโคร", "เซฟดรัก", "ฟาสซิโน"]

# Facilities whose names alone don't say "addiction" but which are known addiction-
# medicine residentials (from the crawl itself); name-matched so they classify right.
KNOWN_ADDICTION = ["dawn rehab", "the river rehab", "siam rehab", "rehab scandinavia",
                   "the cabin"]

KEYWORDS = {
    "geriatric": ["ผู้สูงอายุ", "คนชรา", "บ้านพักคนชรา", "เนอร์สซิ่ง", "ดูแลผู้ป่วย", "อัลไซเมอร์",
                  "nursing home", "nursing", "elderly", "senior", "geriatr", "memory care",
                  "dementia", "assisted living", "home care"],
    # physio must be checked before the generic rehab fallback: กายภาพบำบัด contains บำบัด.
    "physio": ["กายภาพบำบัด", "physiotherap", "physical therapy"],
    "addiction": ["เลิกเหล้า", "เลิกยา", "ยาเสพติด", "ศูนย์บำบัดยาเสพติด", "detox", "addiction",
                  "sober", "substance"],
    # generic fallback ONLY — ambiguous ฟื้นฟู/บำบัด/rehabilitation names that state
    # neither physio nor addiction; keeps state/medical rehab centres from orphaning.
    "rehab": ["บำบัด", "ฟื้นฟู", "ศูนย์บำบัด", "rehab", "rehabilitation"],
    "gyn": ["สูติ", "นรีเวช", "นรีแพทย์", "ผดุงครรภ์", "มีบุตรยาก", "สตรี",
            "gynec", "obstet", "ob-gyn", "obgyn", "women", "fertility", "ivf"],
    "longevity": ["ชะลอวัย", "เวชศาสตร์ฟื้นฟู", "เวลเนส", "ฮอร์โมน", "ดริป", "เซลล์บำบัด",
                  "anti-aging", "antiaging", "longevity", "wellness", "regenerat",
                  "hormone", "iv drip", "vitamin drip", "hyperbaric", "chelation", "stem cell"],
    "aesthetic": ["ความงาม", "เสริมความงาม", "ผิวหนัง", "ผิวพรรณ", "เลเซอร์", "ศัลยกรรม", "ปลูกผม",
                  "aesthetic", "beauty", "skin", "derma", "laser", "botox", "filler",
                  "glow", "slim", "hair transplant", "cosmetic"],
}


def classify(name: str, name_en: str = "") -> str:
    hay = f"{name} {name_en}".lower()
    if any(k in hay for k in KNOWN_ADDICTION):
        return "addiction"
    # order matters: physio and addiction before the generic rehab fallback
    for vert in ["physio", "addiction", "geriatric", "gyn", "longevity", "aesthetic", "rehab"]:
        if any(k in hay for k in KEYWORDS[vert]):
            return vert
    return "other"


def slug(name: str) -> str:
    out = []
    for ch in (name or "clinic").lower():
        if ch.isascii() and ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    s = "".join(out).strip("-")
    return s or "clinic"


def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS clinics(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ext_id TEXT UNIQUE,
        name TEXT, name_en TEXT,
        vertical TEXT, lat REAL, lon REAL,
        phone TEXT, website TEXT, hours TEXT, addr TEXT,
        tags TEXT, source TEXT,
        status TEXT DEFAULT 'new', note TEXT DEFAULT '',
        first_seen TEXT, last_seen TEXT)""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_clinics_status ON clinics(status)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_clinics_vertical ON clinics(vertical)")
    # migrations for the worldwide (city/country) dimension
    for col in ("city TEXT DEFAULT ''", "country TEXT DEFAULT ''"):
        try:
            con.execute(f"ALTER TABLE clinics ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass
    return con


def upsert(con, ext_id, name, name_en, lat, lon, phone, website, hours, addr, tags, source,
           force_vertical=None, city="", country=""):
    vert = force_vertical or classify(name or "", name_en or "")
    con.execute("""INSERT INTO clinics(ext_id,name,name_en,vertical,lat,lon,phone,website,hours,addr,tags,source,city,country,first_seen,last_seen)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(ext_id) DO UPDATE SET
          name=excluded.name, name_en=excluded.name_en,
          lat=excluded.lat, lon=excluded.lon,
          phone=COALESCE(NULLIF(excluded.phone,''), clinics.phone),
          website=COALESCE(NULLIF(excluded.website,''), clinics.website),
          hours=COALESCE(NULLIF(excluded.hours,''), clinics.hours),
          addr=COALESCE(NULLIF(excluded.addr,''), clinics.addr),
          city=COALESCE(NULLIF(excluded.city,''), clinics.city),
          country=COALESCE(NULLIF(excluded.country,''), clinics.country),
          tags=excluded.tags, last_seen=excluded.last_seen""",
        (ext_id, name, name_en, vert, lat, lon, phone or "", website or "", hours or "",
         addr or "", json.dumps(tags, ensure_ascii=False), source, city, country, TODAY, TODAY))


def counts(con):
    by_status = {r["status"]: r["n"] for r in con.execute(
        "SELECT status, COUNT(*) n FROM clinics GROUP BY status")}
    by_vert = {r["vertical"]: r["n"] for r in con.execute(
        "SELECT vertical, COUNT(*) n FROM clinics WHERE status NOT IN ('pass') GROUP BY vertical")}
    return by_status, by_vert
