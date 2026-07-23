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
  nwr["amenity"="clinic"]({BBOX});
  nwr["amenity"="nursing_home"]({BBOX});
  nwr["social_facility"="nursing_home"]({BBOX});
  nwr["social_facility"="assisted_living"]({BBOX});
);
out center tags;
"""


def addr_from(tags):
    bits = [tags.get(k) for k in ("addr:housenumber", "addr:street", "addr:subdistrict",
                                  "addr:district", "addr:city", "addr:postcode")]
    return " ".join(b for b in bits if b)


def run():
    data, last_err = None, None
    for ep in ENDPOINTS:
        try:
            req = urllib.request.Request(
                ep, data=("data=" + urllib.parse.quote(QUERY)).encode(),
                headers={"User-Agent": "defiant-partners/1.0 (+https://defiant.to; contact via site form)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read())
            print(f"(via {ep.split('/')[2]})")
            break
        except Exception as e:
            last_err = e
            print(f"  {ep.split('/')[2]}: {e} — trying next mirror")
    if data is None:
        raise SystemExit(f"all Overpass mirrors failed; last error: {last_err}")
    els = data.get("elements", [])
    con = connect()
    n = 0
    for el in els:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:th") or tags.get("name:en") or ""
        if not name:
            continue
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        upsert(con,
               ext_id=f"osm:{el['type']}/{el['id']}",
               name=name,
               name_en=tags.get("name:en") or "",
               lat=lat, lon=lon,
               phone=tags.get("phone") or tags.get("contact:phone") or "",
               website=tags.get("website") or tags.get("contact:website") or "",
               hours=tags.get("opening_hours") or "",
               addr=addr_from(tags),
               tags=tags, source="overpass")
        n += 1
    con.commit()
    print(f"Overpass: {len(els)} elements, {n} named clinics upserted.")
    return n


if __name__ == "__main__":
    run()
