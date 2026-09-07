#!/usr/bin/env python3
"""Generate the Defiant directory as Obsidian notes inside ~/Vaults/Defiant.

Vault-first: after this runs once, THE VAULT IS CANONICAL. NaN edits
notes in Obsidian; build.py compiles the vault into the defiant.to site; the
same notes can be pushed to Obsidian Publish. This script is additive and
idempotent — it NEVER overwrites an existing non-empty note (re-running after
hand edits is always safe).

Two deliberate curation edits, both directed 2026-07-23:
  * 'Public Links/=Procedures.md' — remove [[Appendectomy]] (not a medical-
    tourism target), append Experimental & Regenerative section if absent.
  * 'Stem Cell Therapy.md' (vault root) — fill NaN's empty stub in place.

Price tables sit inside <!-- defiant:auto:* --> comment markers: invisible in
Obsidian reading view and on Publish, but machine-addressable so future
crawlers (crawl/) can refresh numbers without touching hand-written prose.
"""
from datetime import date
from pathlib import Path

from defiant_content import PROCEDURES, HOSPITALS, DESTINATIONS

VAULT = Path(os.environ.get("DEFIANT_VAULT") or (Path.home() / "Vaults" / "Defiant"))
PUB = VAULT / "Public Links"
ART = PUB / "Articles"
TODAY = "2026-07-23"
DOBBS = date(2022, 6, 24)
DAYS = (date(2026, 7, 23) - DOBBS).days  # static floor; site swaps in live JS

DISCLAIMER = (
    "*Not medical advice. Defiant is a concierge and logistics service, not a "
    "healthcare provider — treatment decisions belong to you and licensed "
    "physicians. Every number on this page is an indicative 2026 range, "
    "confirmed in writing before you book anything.*")

CTA = ("**Ready to price this for real?** [[=Contact|Book a free intake call]] "
       "— no fee, no obligation, no bullshit.")


def slug(name: str) -> str:
    out = []
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


def fm(**kv) -> str:
    lines = ["---"]
    for k, v in kv.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            lines += [f"  - {x}" for x in v]
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def proc_note(name, d):
    desc = f"{name} in Thailand: indicative cost {d['th']} vs {d['us']} in the US. Hospitals, stay length, and the caveats."
    body = fm(title=f"{name} in Thailand — Cost & Where", description=desc[:250],
              type="procedure", category=d["cat"], us_cost=d["us"], th_cost=d["th"],
              updated=TODAY)
    body += d["blurb"] + "\n\n"
    body += "<!-- defiant:auto:prices -->\n"
    body += "| | United States | Thailand |\n|---|---|---|\n"
    body += f"| Indicative 2026 range | {d['us']} | {d['th']} |\n"
    body += "<!-- /defiant:auto:prices -->\n\n"
    if d.get("stay") and d["stay"] != "—":
        body += f"**Typical trip:** {d['stay']}\n\n"
    if d["hosps"]:
        body += "## Where we route this\n\n"
        body += "\n".join(f"- [[{h}]]" for h in d["hosps"]) + "\n\n"
    if d.get("science"):
        body += f"## The science, graded\n\n{d['science']}\n\n"
    body += f"## The Defiant take\n\n{d['notes']}\n\n"
    body += CTA + "\n\n---\n" + DISCLAIMER + "\n"
    return body


def hosp_note(name, d, procs_here):
    jci = ("JCI-accredited (status as of mid-2026 — we re-verify at intake)"
           if d["jci"] else
           "Thai HA accreditation track (not JCI — ask us what that does and doesn't mean)")
    desc = f"{name}, {d['city']}: {d['type']}. What it's good at and which procedures Defiant routes there."
    body = fm(title=f"{name} — {d['city']}", description=desc[:250], type="hospital",
              city=d["city"], accreditation=("JCI" if d["jci"] else "Thai HA"),
              updated=TODAY)
    body += d["blurb"] + "\n\n"
    body += "<!-- defiant:auto:facts -->\n"
    body += f"| | |\n|---|---|\n| City | {d['city']} |\n| Type | {d['type']} |\n"
    body += f"| Scale | {d['beds']} |\n| Accreditation | {jci} |\n"
    body += "<!-- /defiant:auto:facts -->\n\n"
    body += "## Strong suits\n\n" + "\n".join(f"- {s}" for s in d["strengths"]) + "\n\n"
    if procs_here:
        body += ("## Procedures we route here\n\n"
                 + "\n".join(f"- [[{p}]]" for p in procs_here) + "\n\n")
    body += CTA + "\n\n---\n" + DISCLAIMER + "\n"
    return body


def dest_note(name, d):
    desc = (d["blurb"].split(". ")[0] + ".")[:250]
    body = fm(title=f"{name} — Defiant destination guide", description=desc,
              type="destination", updated=TODAY)
    body += d["blurb"] + "\n\n## Know before you plan\n\n"
    body += "\n".join(f"- {x}" for x in d["legal"]) + "\n\n"
    body += "## Practical\n\n" + d["practical"] + "\n\n"
    body += CTA + "\n\n---\n" + DISCLAIMER + "\n"
    return body


def hospitals_index():
    body = fm(title="Hospitals & Clinics — the Defiant shortlist",
              description="The Thai hospitals and specialist clinics Defiant actually routes clients to, by city — with accreditation flags and no advertorial.",
              type="index", updated=TODAY)
    body += ("The shortlist, not the phone book. Every facility here is one we "
             "would send a friend to — which is the entire methodology.\n")
    for city in ["Bangkok", "Chonburi", "Chiang Mai", "Phuket"]:
        rows = [(n, d) for n, d in HOSPITALS.items() if d["city"] == city]
        if not rows:
            continue
        body += f"\n## {city}\n\n"
        for n, d in rows:
            tag = "JCI" if d["jci"] else "Thai HA"
            body += f"- [[{n}]] — {d['type']} · {tag}\n"
    body += "\n" + CTA + "\n"
    return body


def destinations_index():
    body = fm(title="Destinations", description="Where Defiant works: Thailand overview plus Chiang Mai, Bangkok and Phuket — what each city is actually good at.",
              type="index", updated=TODAY)
    body += "Same country, different superpowers. Pick by procedure, not by postcard.\n\n"
    for n, d in DESTINATIONS.items():
        first = d["blurb"].split(". ")[0] + "."
        body += f"- [[{n}]] — {first}\n"
    body += "\n" + CTA + "\n"
    return body


HOME = fm(
    title="Defiant — US Expat Services & Medical Tourism Concierge in Chiang Mai",
    description="Your Overseas Survival Kit: Fixers, Translation, Medical Tourism, Visas, Insurance, Courier, and More.",
    type="home", updated=TODAY) + f"""# DEFIANT

## US Expat Services & Medical Tourism — Chiang Mai, Thailand

ดิงด่อง เฮลโล เวลคัม

# American healthcare is BULLSHIT

ระบบหมออเมริกันแม่งตลกชิบหาย

American healthcare isn't broken, bestie. It never has been.

It's working exactly as the Man designed it--to bleed you dry, keep you sick, watch you die, and stick your family with the bill when you can't fight anymore.

Insurance is a mob racket, HMOs trap you with no specialists, the FDA sits on treatments until Big Pharma cashes in, the CDC is in full revolt, and politicians are actively criminalizing women's health, routine vaccinations, and gender-affirming therapies.

This isn't healthcare. It's a hostage situation.

Anyhooo, that's what Defiant Health is doing and why we're doing it. Get access to world-class treatment in Thailand, up to 80% less costly than the overpriced bullshit you'd get back home, and access to cutting-edge therapies the U.S. would never in a million years approve.

**Plan your escape. Defy the system. Survive the bullshit.**

> **{DAYS:,}+ days** [since U.S. women lost their most basic healthcare rights](https://www.healthaffairs.org/content/forefront/year-after-i-dobbs-i-diminishing-access-obstetric-gynecologic-and-maternal-fetal-care)

## Medical tourism, planned by people who live here

ดีไฟแอนท์

World-class treatment at 20–50% of the US sticker price. We are the fixers: we
shortlist the surgeon, get the quote in writing, move your records, book the
recovery housing, and hand you back to a provider at home who knows what
happened. You get a plan, not a brochure.

- [[=Procedures|Procedures & Prices →]]
- [[=Hospitals|Hospitals & clinics we trust →]]
- [[=Destinations|Chiang Mai · Bangkok · Phuket →]]

## US expat services

ฝรั่งใจเย็นเป็นกลุ่ม

Escape is a logistics problem. We do logistics.

- Digital nomads
- Retirement Visas
- Smart-S business formation/incubator assistance
- Education Visas (learn Thai Language, Muay Thai, traditional arts)
- Banking assistance (opening Thai bank accounts, using international banking)
- Driving license assistance (motorbike, car)
- Referral to trusted real estate agents (rentals, property purchase)
- Relocation concierge
- Latest information on coworking and community spaces / expat networking (Chiang Mai Expats Club, Chiang Mai Digital Expats)
- Household services via Ayasan (cleaning, babysitting, pet care, drivers, senior care)
- International schools (e.g. Grace International School)
- Artificial Intelligence/IT/Web Design
- Charitable engagement or volunteer coordination (e.g. Samsara Foundation)

## Who we are

ก๊วนนี้โหดนะ

**DEFIANT** was founded in June, 2025 by three truly ferocious American expat
patriots* in response to the rapid deterioration we observed in the U.S.
healthcare system. We see what's going on there, guys, and we are so concerned
for you! (Blink twice if you need help--or better yet, [[=Contact|message us!]])

### 'NaN' (she/her)

'NaN' is a former U.S. government employee who spent years assisting citizens
with medical travel across Asia. Her first taste of 'medical tourism' came 15
years ago in Chiang Mai, fixing bad military dental work she couldn't afford to
get done in the States--and she's been a believer ever since.

### 'KAI' (he/him)

'KAI' is a former IT program manager for a U.S. urgent care chain. In 2022 KAI
relocated full-time overseas for their own ongoing treatment and remote work.
They use FSA/HSA and Thai medical facilities for HRT as well as a chronic
health condition.

### 'ROBIN' (she/her)

'ROBIN', born to U.S. missionaries in Nairobi, is a lifelong overseas resident,
semi-retired management consultant and 'dog mom' based in Mauritius. She
recently helped her cousin get a hip replacement in Phuket. 'It was more fun
for everyone than it sounds.'

**TL/DR:** We're disabled queer motherfuckers. We're woke as fuck. We're DEIA
as fuck. We have a ton of organizational skills and a lot of fucking empathy.
And if that offends you--fuck the hell off.

*names changed for privacy

## Find us in Chiang Mai

แถวหลังมอ

Chiang Mai, Thailand — behind the university, where the good coffee is.
Working with clients across every US time zone.

[[=Contact|ส่งซิกหน่อยถ้าลำบาก — blink twice, message us]]
"""

CONTACT = fm(
    title="Contact Defiant — blink twice if you need help",
    description="Reach Defiant in Chiang Mai: the intake form is the fast lane; LINE and encrypted mail also available. A human reads everything.",
    type="contact", updated=TODAY) + """# Blink Twice if You Need Help

ส่งซิกหน่อยถ้าลำบาก

**The form is the fast lane.** A human — usually NaN — reads every submission,
and the first consult is free: you tell us what you're trying to fix, we tell
you straightly whether Thailand is the answer (sometimes it isn't, and we say so).

<!-- defiant:form -->

**LINE:** ID `defiant.to` — [add us on LINE](https://line.me/ti/p/~defiant.to)
(the default channel once you're a client; all of Thailand runs on LINE).

**Encrypted mail:** available — ask in the form, or use the reveal button on
this page. We don't print addresses where bots can harvest them.

**Slow lane:** we're in Chiang Mai (ICT, UTC+7). You'll hear back within a day,
usually much faster. If it's 3am your time, that's our lunch — lucky you.
"""


def write_if_absent(path: Path, text: str, filled=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        print(f"  SKIP (exists) {path.relative_to(VAULT)}")
        return 0
    path.write_text(text, encoding="utf-8")
    print(f"  {'FILL' if filled else 'WRITE'} {path.relative_to(VAULT)}")
    return 1


def curate_procedures_index():
    p = PUB / "=Procedures.md"
    raw = p.read_text(encoding="utf-8")
    orig = raw
    if "[[Appendectomy]]" in raw:
        lines, out, skipping = raw.splitlines(True), [], False
        for ln in lines:
            if "[[Appendectomy]]" in ln:
                skipping = True          # drop bullet line
                continue
            if skipping and ln.strip() == "":
                skipping = False         # and its trailing blank
                continue
            skipping = False
            out.append(ln)
        raw = "".join(out)
    # "/" in a note name creates a folder in Obsidian — flatten to a clean name
    raw = raw.replace("[[Top Surgery (Mastectomy/Augmentation)]]",
                      "[[Top Surgery]] (mastectomy / augmentation)")
    # earlier session appended a duplicate section before we saw NaN's own
    # Futuristic index already lists Stem Cell — remove it
    raw = raw.replace("\n\n## Experimental & Regenerative\n\n- [[Stem Cell Therapy]]\n", "\n")
    if raw != orig:
        p.write_text(raw, encoding="utf-8")
        print("  CURATED Public Links/=Procedures.md")


def main():
    # integrity: every hospital referenced by a procedure must exist
    for n, d in PROCEDURES.items():
        for h in d["hosps"]:
            assert h in HOSPITALS, f"{n} references unknown hospital {h!r}"
    reverse = {h: [] for h in HOSPITALS}
    for n, d in PROCEDURES.items():
        for h in d["hosps"]:
            reverse[h].append(n)

    made = 0
    print("Procedures:")
    for n, d in PROCEDURES.items():
        if n == "Stem Cell Therapy":     # NaN's root-level stub, filled in place
            made += write_if_absent(VAULT / "Stem Cell Therapy.md", proc_note(n, d), filled=True)
        else:
            made += write_if_absent(ART / "Procedures" / f"{n}.md", proc_note(n, d))
    print("Hospitals:")
    for n, d in HOSPITALS.items():
        made += write_if_absent(ART / "Hospitals" / f"{n}.md", hosp_note(n, d, reverse[n]))
    print("Destinations:")
    for n, d in DESTINATIONS.items():
        made += write_if_absent(ART / "Destinations" / f"{n}.md", dest_note(n, d))
    print("Indexes & pages:")
    made += write_if_absent(PUB / "=Hospitals.md", hospitals_index())
    made += write_if_absent(PUB / "=Destinations.md", destinations_index())
    made += write_if_absent(PUB / "=Home.md", HOME)
    made += write_if_absent(PUB / "=Contact.md", CONTACT)
    curate_procedures_index()
    print(f"\n{made} notes written into {VAULT}")


if __name__ == "__main__":
    main()
