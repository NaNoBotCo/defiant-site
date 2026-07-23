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
BBOX = "18.55,98.75,19.05,99.15"
QUERY = f"""
[out:json][timeout:60];
(
  nwr["healthcare"="clinic"]({BBOX});
  nwr["healthcare"="doctor"]({BBOX});
  nwr["healthcare"="nursing_home"]({BBOX});
  nwr["healthcare"="rehabilitation"]({BBOX});
  nwr["healthcare"="hospice"]({BBOX});
  nwr["amenity"="clinic"]({BBOX});
  nwr["amenity"="nursing_home"]({BBOX});
  nwr["social_facility"="nursing_home"]({BBOX});
  nwr["social_facility"="assisted_living"]({BBOX});
);
out center tags;
"""

# Pharmacies get their own query + forced vertical — they are a fulfilment
# channel (where clients actually pick up HRT), not a referral clinic.
PHARMACY_QUERY = f"""
[out:json][timeout:60];
(
  nwr["amenity"="pharmacy"]({BBOX});
  nwr["healthcare"="pharmacy"]({BBOX});
  nwr["shop"="chemist"]({BBOX});
);
out center tags;
"""


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


def run(hubs_only=False):
    con = connect()
    total = 0
    if not hubs_only:
        # Chiang Mai depth: every vertical.
        total += _ingest(con, _fetch(QUERY).get("elements", []), city="Chiang Mai", country="Thailand")
        total += _ingest(con, _fetch(PHARMACY_QUERY).get("elements", []),
                         force_vertical="pharmacy", city="Chiang Mai", country="Thailand")
        con.commit()
        print(f"Chiang Mai: {total} facilities.")
    # Worldwide hospital sweep.
    for city, country, bbox in HUBS:
        try:
            got = _ingest(con, _fetch(hospital_query(bbox)).get("elements", []),
                          force_vertical="hospital", city=city, country=country)
            con.commit()
            print(f"{city}, {country}: {got} hospitals.")
            total += got
        except SystemExit as e:
            print(f"{city}, {country}: SKIPPED ({e})")
    print(f"TOTAL upserted this run: {total}")
    return total


if __name__ == "__main__":
    import sys
    run(hubs_only="--hubs-only" in sys.argv)
