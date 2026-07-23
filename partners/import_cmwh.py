#!/usr/bin/env python3
"""Import the cm-womens-health dataset (258 verified CM facilities) as gyn seeds.

Reuses the sibling project's built geojson — those facilities already carry
OB-GYN tagging, phones and hours. OB-GYN-tagged entries land as vertical=gyn;
the rest classify by name like everything else.
"""
import json
from pathlib import Path

from common import connect, upsert, classify

GEOJSON = (Path.home() / "Developer" / "claude code projects" / "cm-womens-health"
           / "dist" / "cm-womens-health.geojson")


def run():
    feats = json.load(open(GEOJSON))["features"]
    con = connect()
    n = 0
    for f in feats:
        p = f["properties"]
        attrs = p.get("attrs", {})
        name = p.get("nameTh") or p.get("name") or ""
        name_en = p.get("nameEn") or ""
        if not name and not name_en:
            continue
        vert = "gyn" if attrs.get("obgyn") else classify(name, name_en)
        ext = "cmwh:" + p["id"]
        upsert(con, ext_id=ext, name=name or name_en, name_en=name_en,
               lat=p.get("lat"), lon=p.get("lng"),
               phone=attrs.get("phone") or "", website=attrs.get("website") or "",
               hours=attrs.get("openingHours") or "", addr="",
               tags={"cmwh": True, "facilityType": attrs.get("facilityType"),
                     "obgyn": attrs.get("obgyn"), "accreditation": attrs.get("accreditation")},
               source="cmwh")
        if vert == "gyn":
            con.execute("UPDATE clinics SET vertical='gyn' WHERE ext_id=?", (ext,))
        n += 1
    con.commit()
    print(f"cm-womens-health: {n} facilities imported/refreshed.")
    return n


if __name__ == "__main__":
    run()
