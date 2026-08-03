#!/usr/bin/env python3
"""Dossiers + bilingual intro letters for clinic outreach. DRAFTS ONLY — no sending.

promote(clinic_id):
  1. writes a vault dossier  ~/Vaults/Defiant/Partners/<Name>.md
     (outside Public Links → never reaches the site or Obsidian Publish)
  2. writes a Thai-first letter draft  partners/outreach/drafts/<slug>.md
  3. sets status → drafted

export_batch():
  copies every status=drafted letter into a dated folder on the Desktop for the
  translators, with a checklist. Statuses advance only when a human says so.
"""
import shutil
from datetime import date
from pathlib import Path

from common import DRAFTS, VAULT_PARTNERS, TODAY, connect, slug

VERT_LINE_TH = {
    "gyn": "สูตินรีแพทย์ที่ดูแลอย่างเข้าใจ ใส่ใจ และเป็นมิตรกับผู้รับบริการทุกกลุ่ม",
    "aesthetic": "หัตถการด้านความงามและผิวพรรณที่ปลอดภัยและได้มาตรฐาน",
    "longevity": "บริการเวชศาสตร์ชะลอวัยและการดูแลสุขภาพเชิงป้องกัน",
    "geriatric": "การดูแลผู้สูงอายุอย่างอบอุ่น เป็นระบบ ทั้งระยะสั้นและระยะยาว",
    "other": "บริการทางการแพทย์ที่ได้มาตรฐานในเชียงใหม่",
}
VERT_LINE_EN = {
    "gyn": "attentive, judgment-free OB-GYN care",
    "aesthetic": "safe, well-regarded aesthetic and skin procedures",
    "longevity": "preventive and longevity medicine",
    "geriatric": "warm, well-organized short- and long-term elder care",
    "other": "trustworthy medical care in Chiang Mai",
}

LETTER_TH = """เรื่อง: ขอแนะนำตัวและเรียนปรึกษาความร่วมมือในการดูแลผู้รับบริการชาวต่างชาติ

เรียน ท่านผู้บริหาร {clinic}

ดิฉันชื่อ "แนน" เป็นผู้ร่วมก่อตั้งทีม Defiant (defiant.to) ทีมที่ปรึกษาและประสานงานด้านสุขภาพ
สำหรับชาวอเมริกันและชาวต่างชาติที่พำนักอยู่ในเชียงใหม่ หรือเดินทางมารับการรักษาที่เชียงใหม่ค่ะ

ผู้รับบริการของเราจำนวนมากกำลังมองหา{vert_th} ทีมของเราช่วยคัดกรองความต้องการ
นัดหมาย จัดเตรียมเอกสารและประวัติ ประสานล่าม และติดตามดูแลหลังรับบริการ
เพื่อให้ผู้รับบริการมาถึงคลินิกอย่างพร้อม และรบกวนเวลาของแพทย์และเจ้าหน้าที่ให้น้อยที่สุด

ในเบื้องต้น ดิฉันขออนุญาตเรียนเชิญ {clinic} ร่วมเป็น "คลินิกพันธมิตร" ของเรา
โดยไม่มีค่าใช้จ่ายและไม่มีข้อผูกพันใด ๆ ดังนี้ค่ะ

- เราจะจัดทำหน้าแนะนำคลินิกของท่าน (ภาษาอังกฤษ) บนเว็บไซต์ของเราให้โดยไม่คิดค่าใช้จ่าย
  โดยใช้เฉพาะข้อมูลที่ท่านตรวจสอบและเห็นชอบแล้วเท่านั้น
- เรายินดีแนะนำและส่งต่อผู้รับบริการชาวต่างชาติที่เหมาะสมกับบริการของท่าน พร้อมล่ามประสานงาน
- รูปแบบความร่วมมือหรือค่าแนะนำ (หากมี) ยินดีให้เป็นไปตามที่ท่านเห็นสมควรและสะดวกใจ

หากท่านพอมีเวลา ดิฉันหรือผู้ประสานงานภาษาไทยของเรา ขออนุญาตเข้าพบ หรือโทรเรียนปรึกษาสั้น ๆ
ประมาณ 15 นาที ตามวันและเวลาที่ท่านสะดวกค่ะ

ติดต่อเราได้ทาง LINE ID: defiant.to หรือตอบกลับอีเมลฉบับนี้
ดูข้อมูลเพิ่มเติมได้ที่ https://defiant.to/partners/

ขอขอบพระคุณอย่างสูงที่กรุณาสละเวลาอ่าน และขออภัยหากรบกวนเวลาอันมีค่าของท่าน

ด้วยความเคารพอย่างสูง
แนน (NaN) — ทีม Defiant เชียงใหม่
LINE: defiant.to · https://defiant.to/partners/"""

LETTER_EN = """Subject: Introduction & partnership inquiry — caring for foreign patients in Chiang Mai

Dear Director of {clinic_en},

My name is NaN, co-founder of Defiant (defiant.to), a Chiang Mai–based health
concierge for Americans and other foreigners who live here or travel here for care.

Many of our clients are looking for {vert_en}. Our team screens needs, books
appointments, prepares records, coordinates interpreters, and follows up after
care — so patients arrive prepared and take as little of your staff's time as possible.

We would like to invite {clinic_en} to become one of our partner clinics — free,
with no obligation:

- A free English-language profile of your clinic on our site, using only
  information you have reviewed and approved.
- Referrals of suitable foreign patients, with interpreter coordination included.
- Any cooperation or referral-fee structure entirely at your discretion.

If you have time, we (or our Thai-speaking coordinator) would be grateful for a
short 15-minute visit or call at your convenience.

Reach us on LINE (ID: defiant.to), by replying to this email, or see
https://defiant.to/partners/

With respect and thanks for your time,
NaN — Defiant, Chiang Mai
LINE: defiant.to · https://defiant.to/partners/"""

# Northern (Lanna) provinces — recipients here get the downhome Kham Mueang
# register; everyone else stays Central-Thai polite. Kham Mueang aimed at an
# Isaan or Bangkok clinic reads as out of place, so it is region-scoped.
NORTHERN = {"Chiang Mai", "Chiang Rai", "Lamphun", "Lampang", "Nan", "Phrae",
            "Phayao", "Mae Hong Son", "San Kamphaeng", "Uttaradit", "Tak", "Sukhothai"}

REGISTER_NOTE = {
    "lanna": """[ ] REGISTER — this is a NORTHERN (Lanna) recipient. Render the Thai in
    warm, downhome **Kham Mueang / คำเมือง**: the polite particle is **เจ้า**
    (not Central ค่ะ/ครับ), "we" leans **เฮา**, soften with **เน้อ/น่อ**. Keep it
    sincere, unhurried, a touch old-country — the way a Northern clinic owner
    actually talks. A wrong note costs credibility, so a native Northern hand
    should do the final pass. Address respectfully (ป้อ/แม่ + name, or คุณหมอ).""",
    "central": """[ ] REGISTER — Central-Thai polite (ค่ะ; ครับ if a male coordinator sends).
    Warm and courteous; match any regional register the recipient uses.""",
}

TRANSLATOR_NOTES = """--- SEND NOTES (for NaN + translators — do not include in the email) ---
Clinic record: {name} / {name_en} · {city}, {country} · vertical: {vertical}
Phone: {phone}   Website: {website}   Hours: {hours}
Source: {source} ({ext_id})

Translator checklist:
[ ] Confirm clinic's formal Thai name and honorific for the addressee
    (ผู้อำนวยการ/คุณหมอ + name if known — a named doctor beats a title).
{register_note}
[ ] Verify the vertical line matches what the clinic actually does.
[ ] Channel: email if they have one; otherwise LINE OA or a printed letter
    delivered in person works better with many Thai clinics — same text.
[ ] Nothing sends until a human sends it. อย่าส่งแบบหว่าน — one clinic at a time.
"""


def promote(clinic_id: int) -> Path:
    con = connect()
    c = con.execute("SELECT * FROM clinics WHERE id=?", (clinic_id,)).fetchone()
    if not c:
        raise SystemExit(f"no clinic id {clinic_id}")
    name = c["name"] or c["name_en"]
    name_en = c["name_en"] or c["name"]
    s = slug(name_en or name) or f"clinic-{clinic_id}"

    # 1. vault dossier (private side of the vault — never published)
    VAULT_PARTNERS.mkdir(parents=True, exist_ok=True)
    dossier = VAULT_PARTNERS / f"{(name_en or name).replace('/', '-')}.md"
    if not dossier.exists():
        dossier.write_text(f"""---
name: {name}
name_en: {name_en}
vertical: {c['vertical']}
phone: {c['phone']}
website: {c['website']}
status: drafted
publish: false
updated: {TODAY}
---
<!-- PRIVATE CRM note. publish:false keeps it off Obsidian Publish. Do not publish. -->


<!-- defiant:auto:facts -->
| | |
|---|---|
| Thai name | {name} |
| Vertical | {c['vertical']} |
| Phone | {c['phone'] or '—'} |
| Website | {c['website'] or '—'} |
| Hours | {c['hours'] or '—'} |
| Address | {c['addr'] or '—'} |
| Map | https://www.openstreetmap.org/?mlat={c['lat']}&mlon={c['lon']}#map=18/{c['lat']}/{c['lon']} |
| Source | {c['source']} ({c['ext_id']}) |
<!-- /defiant:auto:facts -->

## Relationship log

- {TODAY} — promoted from crawl; intro letter drafted.

## Terms discussed

*(nothing yet)*
""", encoding="utf-8")

    # 2. letter draft
    DRAFTS.mkdir(parents=True, exist_ok=True)
    draft = DRAFTS / f"{s}.md"
    vert = c["vertical"] if c["vertical"] in VERT_LINE_TH else "other"
    ck = c.keys()
    city = (c["city"] if "city" in ck else "") or ""
    country = (c["country"] if "country" in ck else "") or "Thailand"
    register = "lanna" if city in NORTHERN else "central"
    notes_fields = {k: (c[k] if k in ck else "") or "—" for k in
                    ("name", "name_en", "vertical", "phone", "website", "hours", "source", "ext_id")}
    notes_fields.update(city=city or "—", country=country or "—",
                        register_note=REGISTER_NOTE[register])
    draft.write_text(
        LETTER_TH.format(clinic=name, vert_th=VERT_LINE_TH[vert])
        + "\n\n\n═══════════ ENGLISH MIRROR ═══════════\n\n"
        + LETTER_EN.format(clinic_en=name_en or name, vert_en=VERT_LINE_EN[vert])
        + "\n\n\n" + TRANSLATOR_NOTES.format(**notes_fields),
        encoding="utf-8")

    con.execute("UPDATE clinics SET status='drafted' WHERE id=?", (clinic_id,))
    con.commit()
    return draft


def export_batch() -> Path:
    con = connect()
    rows = con.execute("SELECT * FROM clinics WHERE status='drafted'").fetchall()
    out = Path.home() / "Desktop" / f"Defiant Outreach Batch {date.today().isoformat()}"
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for c in rows:
        s = slug(c["name_en"] or c["name"]) or f"clinic-{c['id']}"
        src = DRAFTS / f"{s}.md"
        if src.exists():
            shutil.copy2(src, out / src.name)
            n += 1
    (out / "READ ME FIRST — translators.md").write_text(
        f"""# Defiant outreach batch — {date.today().isoformat()}

{n} draft letters, Thai first, English mirror below each. For each file:

1. Polish the Thai for the specific clinic (names, honorifics, ครับ/ค่ะ).
2. Confirm the best channel (email / LINE OA / printed letter in person).
3. Send ONE AT A TIME from the agreed address or LINE — never a mass blast.
4. Tell NaN which were sent so she can mark them in the board
   (Desktop → "Defiant Partners.command" → mark status).

Tone rule, absolute: สุภาพ อ่อนน้อม ไม่เร่งรัด — we are guests asking for a
relationship, not vendors closing a deal. If a letter feels pushy, soften it.
""", encoding="utf-8")
    print(f"Exported {n} drafts → {out}")
    return out
