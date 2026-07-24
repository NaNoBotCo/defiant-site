#!/usr/bin/env python3
"""Harvest Chiang Mai clinics from OpenStreetMap (Overpass) into partners.db.

One polite query over ISO3166-2 = TH-50 (Chiang Mai province): clinics, doctors,
nursing homes, assisted living. Classification into verticals is name-keyword
based (Thai + English) — imperfect on purpose; the review board exists to sort
the rest. Re-running refreshes last_seen and fills gaps without clobbering
statuses or notes.
"""
import json
import urllib.parse
import urllib.request

from common import connect, upsert

ENDPOINTS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.osm.jp/api/interpreter",
]
# Greater Chiang Mai bbox (Mueang + Hang Dong, San Sai, Mae Rim, Saraphi, Doi
# Saket). Exact tag matches over a bbox are far cheaper for Overpass than a
# province-area regex — the mirrors 504 on the fancy version when busy.
# ALL OF THAILAND, province by province (ISO 3166-2 TH-xx), Isaan included.
# Each province crawled inside its own admin area — bounded, resumable, politer
# to Overpass than one country firehose. Full verticals everywhere.
TH_PROVINCES = {
    "TH-10": "Bangkok", "TH-11": "Samut Prakan", "TH-12": "Nonthaburi",
    "TH-13": "Pathum Thani", "TH-14": "Ayutthaya", "TH-15": "Ang Thong",
    "TH-16": "Lopburi", "TH-17": "Sing Buri", "TH-18": "Chai Nat",
    "TH-19": "Saraburi", "TH-20": "Chonburi", "TH-21": "Rayong",
    "TH-22": "Chanthaburi", "TH-23": "Trat", "TH-24": "Chachoengsao",
    "TH-25": "Prachinburi", "TH-26": "Nakhon Nayok", "TH-27": "Sa Kaeo",
    "TH-30": "Nakhon Ratchasima", "TH-31": "Buriram", "TH-32": "Surin",
    "TH-33": "Sisaket", "TH-34": "Ubon Ratchathani", "TH-35": "Yasothon",
    "TH-36": "Chaiyaphum", "TH-37": "Amnat Charoen", "TH-38": "Bueng Kan",
    "TH-39": "Nong Bua Lamphu", "TH-40": "Khon Kaen", "TH-41": "Udon Thani",
    "TH-42": "Loei", "TH-43": "Nong Khai", "TH-44": "Maha Sarakham",
    "TH-45": "Roi Et", "TH-46": "Kalasin", "TH-47": "Sakon Nakhon",
    "TH-48": "Nakhon Phanom", "TH-49": "Mukdahan", "TH-50": "Chiang Mai",
    "TH-51": "Lamphun", "TH-52": "Lampang", "TH-53": "Uttaradit",
    "TH-54": "Phrae", "TH-55": "Nan", "TH-56": "Phayao", "TH-57": "Chiang Rai",
    "TH-58": "Mae Hong Son", "TH-60": "Nakhon Sawan", "TH-61": "Uthai Thani",
    "TH-62": "Kamphaeng Phet", "TH-63": "Tak", "TH-64": "Sukhothai",
    "TH-65": "Phitsanulok", "TH-66": "Phichit", "TH-67": "Phetchabun",
    "TH-70": "Ratchaburi", "TH-71": "Kanchanaburi", "TH-72": "Suphan Buri",
    "TH-73": "Nakhon Pathom", "TH-74": "Samut Sakhon", "TH-75": "Samut Songkhram",
    "TH-76": "Phetchaburi", "TH-77": "Prachuap Khiri Khan", "TH-80": "Nakhon Si Thammarat",
    "TH-81": "Krabi", "TH-82": "Phang Nga", "TH-83": "Phuket", "TH-84": "Surat Thani",
    "TH-85": "Ranong", "TH-86": "Chumphon", "TH-90": "Songkhla", "TH-91": "Satun",
    "TH-92": "Trang", "TH-93": "Phatthalung", "TH-94": "Pattani", "TH-95": "Yala",
    "TH-96": "Narathiwat",
}


def _area(iso):
    return f'area["ISO3166-2"="{iso}"]->.a;'


def clinic_query(iso):
    return (f'[out:json][timeout:180];{_area(iso)}('
            f'nwr["healthcare"="clinic"](area.a);'
            f'nwr["healthcare"="doctor"](area.a);'
            f'nwr["healthcare"="nursing_home"](area.a);'
            f'nwr["healthcare"="rehabilitation"](area.a);'
            f'nwr["healthcare"="hospice"](area.a);'
            f'nwr["amenity"="clinic"](area.a);'
            f'nwr["amenity"="nursing_home"](area.a);'
            f'nwr["social_facility"="nursing_home"](area.a);'
            f'nwr["social_facility"="assisted_living"](area.a););out center tags;')


def pharmacy_query(iso):
    return (f'[out:json][timeout:180];{_area(iso)}('
            f'nwr["amenity"="pharmacy"](area.a);'
            f'nwr["healthcare"="pharmacy"](area.a);'
            f'nwr["shop"="chemist"](area.a););out center tags;')


def addr_from(tags):
    bits = [tags.get(k) for k in ("addr:housenumber", "addr:street", "addr:subdistrict",
                                  "addr:district", "addr:city", "addr:postcode")]
    return " ".join(b for b in bits if b)


def _fetch(query):
    last_err = None
    for ep in ENDPOINTS:
        try:
            req = urllib.request.Request(
                ep, data=("data=" + urllib.parse.quote(query)).encode(),
                headers={"User-Agent": "defiant-partners/1.0 (+https://defiant.to; contact via site form)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                print(f"(via {ep.split('/')[2]})")
                return json.loads(r.read())
        except Exception as e:
            last_err = e
            print(f"  {ep.split('/')[2]}: {e} — trying next mirror")
    raise SystemExit(f"all Overpass mirrors failed; last error: {last_err}")


# ---- worldwide medical-tourism HUBS -----------------------------------------
# Deep-local (Chiang Mai) gets every vertical; the global hubs get a HOSPITAL
# sweep — a hospital is a hospital in any language, so it classifies cleanly
# where name-keywords wouldn't. bbox = "S,W,N,E". Starting point, grows nightly.
HUBS = [
    ("Chiang Mai", "Thailand", "18.55,98.75,19.05,99.15"),
    ("Bangkok", "Thailand", "13.55,100.35,13.95,100.75"),
    ("Phuket", "Thailand", "7.80,98.25,8.20,98.45"),
    ("Delhi NCR", "India", "28.40,76.90,28.90,77.40"),
    ("Mumbai", "India", "18.90,72.75,19.30,72.99"),
    ("Chennai", "India", "12.90,80.10,13.15,80.30"),
    ("Bengaluru", "India", "12.85,77.45,13.10,77.75"),
    ("Istanbul", "Turkey", "40.90,28.70,41.20,29.30"),
    ("Antalya", "Turkey", "36.80,30.55,36.95,30.80"),
    ("Tijuana", "Mexico", "32.45,-117.10,32.55,-116.90"),
    ("Cancún", "Mexico", "21.05,-86.90,21.25,-86.75"),
    ("Mexico City", "Mexico", "19.30,-99.25,19.55,-99.05"),
    ("Kuala Lumpur", "Malaysia", "3.05,101.60,3.25,101.80"),
    ("Penang", "Malaysia", "5.28,100.25,5.45,100.35"),
    ("Singapore", "Singapore", "1.24,103.60,1.47,104.02"),
    ("Seoul", "South Korea", "37.45,126.85,37.65,127.15"),
    ("San José", "Costa Rica", "9.87,-84.15,10.00,-84.02"),
    ("Medellín", "Colombia", "6.17,-75.63,6.32,-75.53"),
    ("Bogotá", "Colombia", "4.55,-74.15,4.80,-74.03"),
    ("Budapest", "Hungary", "47.40,19.00,47.58,19.18"),
    ("Dubai", "UAE", "25.05,55.10,25.30,55.40"),
    ("Barcelona", "Spain", "41.34,2.10,41.47,2.23"),
    ("San José del Cabo", "Mexico", "22.88,-109.95,23.07,-109.68"),
]


def hospital_query(bbox):
    return (f'[out:json][timeout:90];('
            f'nwr["amenity"="hospital"]({bbox});'
            f'nwr["healthcare"="hospital"]({bbox}););out center tags;')


def _ingest(con, els, force_vertical=None, city="", country=""):
    n = 0
    for el in els:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:en") or tags.get("name:th") or ""
        if not name:
            continue
        upsert(con,
               ext_id=f"osm:{el['type']}/{el['id']}",
               name=name,
               name_en=tags.get("name:en") or "",
               lat=el.get("lat") or (el.get("center") or {}).get("lat"),
               lon=el.get("lon") or (el.get("center") or {}).get("lon"),
               phone=tags.get("phone") or tags.get("contact:phone") or "",
               website=tags.get("website") or tags.get("contact:website") or "",
               hours=tags.get("opening_hours") or "",
               addr=addr_from(tags),
               tags=tags, source="overpass", force_vertical=force_vertical,
               city=city, country=country)
        n += 1
    return n


def crawl_thailand(con, only=None):
    """Full verticals across every Thai province (Isaan included). Resumable:
    `only` = set of province names to (re)crawl this pass; None = all 77."""
    total = 0
    for iso, prov in TH_PROVINCES.items():
        if only and prov not in only:
            continue
        try:
            got = _ingest(con, _fetch(clinic_query(iso)).get("elements", []),
                          city=prov, country="Thailand")
            got += _ingest(con, _fetch(pharmacy_query(iso)).get("elements", []),
                           force_vertical="pharmacy", city=prov, country="Thailand")
            con.commit()
            print(f"{prov}: {got}")
            total += got
        except SystemExit as e:
            print(f"{prov}: SKIPPED ({e})")
    return total


def crawl_hubs(con):
    total = 0
    for city, country, bbox in HUBS:
        try:
            got = _ingest(con, _fetch(hospital_query(bbox)).get("elements", []),
                          force_vertical="hospital", city=city, country=country)
            con.commit()
            print(f"{city}, {country}: {got} hospitals.")
            total += got
        except SystemExit as e:
            print(f"{city}, {country}: SKIPPED ({e})")
    return total


# Nightly keeps it light: refresh the North + the worldwide hospital hubs.
NIGHTLY_NORTH = {"Chiang Mai", "Chiang Rai", "Lamphun", "Lampang", "Nan", "Phrae",
                 "Phayao", "Mae Hong Son", "Tak", "Sukhothai", "Phitsanulok"}


def run(mode="nightly"):
    con = connect()
    total = 0
    if mode == "thailand":
        total += crawl_thailand(con)          # all 77 provinces, full verticals
    else:
        total += crawl_thailand(con, only=NIGHTLY_NORTH)
    total += crawl_hubs(con)                   # worldwide hospitals
    print(f"TOTAL upserted this run: {total}")
    return total


if __name__ == "__main__":
    import sys
    run(mode="thailand" if "--thailand" in sys.argv else "nightly")
