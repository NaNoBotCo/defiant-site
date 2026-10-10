#!/usr/bin/env python3
"""Frontier — articles on new medicine reachable in Thailand, staged for Nan's word.

  harvest [goal]   ClinicalTrials.gov v2: studies with a Thai site, by health goal
  pick             the goal to write next (least recently written, most to say)
  brief <goal>     staging folder + brief.json for the writer
  qa <slug>        checks a staged article (front matter, tags, NCT IDs, words, doodle)
  ship <slug>      staged note → vault Articles/, topics.json, card, doodle; nightly deploys it
  board            staged and shipped

Staging lives in frontier/staging/<slug>/ — outside the vault, so the nightly
build cannot publish a staged article.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FR = ROOT / "frontier"
STAGE = FR / "staging"
DATA = ROOT / "data" / "frontier"
GOALS = DATA / "goals.json"
TRIALS = DATA / "trials.json"
LEDGER = DATA / "ledger.tsv"
DOODLE = FR / "doodle"
VAULT_ART = Path(os.environ.get("DEFIANT_VAULT") or (Path.home() / "Vaults" / "Defiant")) / "Public Links" / "Articles"
TODAY = date.today().isoformat()
API = "https://clinicaltrials.gov/api/v2/studies"
STATUSES = "RECRUITING,NOT_YET_RECRUITING,ENROLLING_BY_INVITATION,ACTIVE_NOT_RECRUITING"


def jload(p, default=None):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else default


def jsave(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- harvest
def _get(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "defiant-frontier/1 (+https://defiant.to)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def _study(s):
    ps = s["protocolSection"]
    idm, st, dm = ps["identificationModule"], ps["statusModule"], ps.get("designModule", {})
    el, sp = ps.get("eligibilityModule", {}), ps.get("sponsorCollaboratorsModule", {})
    locs = ps.get("contactsLocationsModule", {}).get("locations", []) or []
    th = [l for l in locs if l.get("country") == "Thailand"]
    return {
        "nct": idm["nctId"],
        "title": idm.get("briefTitle", ""),
        "status": st.get("overallStatus", ""),
        "phase": dm.get("phases", []) or ["NA"],
        "type": dm.get("studyType", ""),
        "conditions": ps.get("conditionsModule", {}).get("conditions", []),
        "interventions": [{"type": i.get("type"), "name": i.get("name")}
                          for i in ps.get("armsInterventionsModule", {}).get("interventions", []) or []],
        "sponsor": sp.get("leadSponsor", {}).get("name", ""),
        "sponsor_class": sp.get("leadSponsor", {}).get("class", ""),
        "start": st.get("startDateStruct", {}).get("date", ""),
        "primary_completion": st.get("primaryCompletionDateStruct", {}).get("date", ""),
        "updated": st.get("lastUpdatePostDateStruct", {}).get("date", ""),
        "enrollment": dm.get("enrollmentInfo", {}).get("count"),
        "ages": [el.get("minimumAge", ""), el.get("maximumAge", "")],
        "sex": el.get("sex", ""),
        "healthy_ok": el.get("healthyVolunteers", False),
        "thai_sites": [{"facility": l.get("facility", ""), "city": l.get("city", ""),
                        "status": l.get("status", "")} for l in th],
        "countries": sorted({l.get("country", "") for l in locs if l.get("country")}),
        "summary": (ps.get("descriptionModule", {}).get("briefSummary", "") or "")[:1200],
        "url": f"https://clinicaltrials.gov/study/{idm['nctId']}",
    }


def harvest_goal(goal):
    seen, out = set(), []
    for term in goal["terms"]:
        params = {"query.cond": term, "query.locn": "Thailand", "filter.overallStatus": STATUSES,
                  "pageSize": 100}
        token = None
        for _ in range(5):
            if token:
                params["pageToken"] = token
            d = _get(params)
            for s in d.get("studies", []):
                rec = _study(s)
                if rec["nct"] not in seen and rec["thai_sites"]:
                    seen.add(rec["nct"])
                    out.append(rec)
            token = d.get("nextPageToken")
            if not token:
                break
    return out


def harvest(only=None):
    goals = jload(GOALS)["goals"]
    db = jload(TRIALS, {"harvested": None, "goals": {}})
    for g in goals:
        if only and g["id"] != only:
            continue
        try:
            recs = harvest_goal(g)
        except Exception as e:  # one goal down keeps the last good data
            print(f"  {g['id']}: harvest failed ({e}); kept last data")
            continue
        db["goals"][g["id"]] = {"harvested": TODAY, "trials": recs}
        print(f"  {g['id']:22} {len(recs):4} trials with a Thai site")
    db["harvested"] = TODAY
    jsave(TRIALS, db)


# ---------------------------------------------------------------- pick / brief
def ledger():
    rows = []
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines()[1:]:
            if line.strip():
                d, slug, goal, state = (line.split("\t") + ["", "", "", ""])[:4]
                rows.append({"date": d, "slug": slug, "goal": goal, "state": state})
    return rows


def log(slug, goal, state):
    if not LEDGER.exists():
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text("date\tslug\tgoal\tstate\n")
    with LEDGER.open("a") as f:
        f.write(f"{TODAY}\t{slug}\t{goal}\t{state}\n")


def _late_phase(t):
    return any(p in ("PHASE2", "PHASE3", "PHASE4") for p in t["phase"])


def pick():
    goals = jload(GOALS)["goals"]
    db = jload(TRIALS, {"goals": {}})["goals"]
    last = {}
    for r in ledger():
        last[r["goal"]] = max(last.get(r["goal"], ""), r["date"])
    def score(g):
        ts = db.get(g["id"], {}).get("trials", [])
        # never written beats written; then oldest write; then most trial material
        return (g["id"] in last, last.get(g["id"], ""), -sum(1 + _late_phase(t) for t in ts))
    ranked = sorted(((score(g), i, g) for i, g in enumerate(goals)), key=lambda x: (x[0], x[1]))
    if not ranked:
        sys.exit("no goal has trial data — run harvest")
    g = ranked[0][2]
    print(g["id"])
    return g


def brief(goal_id):
    goals = {g["id"]: g for g in jload(GOALS)["goals"]}
    g = goals[goal_id]
    ts = jload(TRIALS)["goals"].get(goal_id, {}).get("trials", [])
    ts = sorted(ts, key=lambda t: (not _late_phase(t), t["status"] != "RECRUITING", t["start"] or "9"), reverse=False)
    slug = f"{TODAY}-{goal_id}"
    d = STAGE / slug
    d.mkdir(parents=True, exist_ok=True)
    jsave(d / "brief.json", {"slug": slug, "goal": g, "made": TODAY, "trial_count": len(ts), "trials": ts})
    log(slug, goal_id, "briefed")
    print(d)
    return d


# ---------------------------------------------------------------- qa
NCT = re.compile(r"\bNCT\d{8}\b")
CURE_WORDS = re.compile(r"\b(cures?|cured|miracle|guaranteed?|reverses aging|100% effective)\b", re.I)


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, text[m.end():]


def _api_has(nct):
    try:
        d = _get({"filter.ids": nct, "pageSize": 1})
        return bool(d.get("studies"))
    except Exception:
        return None


def qa(slug, verbose=True):
    d = STAGE / slug
    errs = []
    notes = [n for n in d.glob("*.md") if n.name != "research.md"]
    if len(notes) != 1:
        errs.append(f"want one .md note in {d}, found {len(notes)}")
        return _report(errs, verbose)
    text = notes[0].read_text()
    meta, body = front_matter(text)
    if meta is None:
        errs.append("no front matter")
        return _report(errs, verbose)
    for k in ("title", "description", "type", "updated", "keyword", "tags"):
        if not meta.get(k):
            errs.append(f"front matter missing {k}")
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    reg = jload(ROOT / "tags.json", {})
    known = set()
    for k, v in reg.items():
        if isinstance(v, dict):
            known |= {kk for kk in v if "/" in kk}
    unknown = [t for t in tags if known and t not in known]
    if unknown:
        errs.append(f"tags not in tags.json: {', '.join(unknown)}")
    if not any(t.startswith("evidence/") for t in tags):
        errs.append("no evidence/ tag")
    if "prose pending" in text:
        errs.append("still says prose pending")
    if len(body.split()) < 900:
        errs.append(f"body is {len(body.split())} words; under 900")
    b = jload(d / "brief.json", {"trials": []})
    known_nct = {t["nct"] for t in b["trials"]}
    for n in sorted(set(NCT.findall(body))):
        if n not in known_nct and not _api_has(n):
            errs.append(f"{n} cited but not in the brief or the registry")
    for m in CURE_WORDS.finditer(body):
        line = body[:m.start()].count("\n") + 1
        errs.append(f"line {line}: cure-word '{m.group(0)}'")
    if "## Sources" not in body:
        errs.append("no ## Sources section")
    sc = subprocess.run([sys.executable, str(Path.home() / ".claude/bin/stylecheck.py"), str(notes[0])],
                        capture_output=True, text=True)
    if sc.returncode != 0:
        errs.append("stylecheck:\n" + (sc.stdout + sc.stderr).strip())
    piece = (d / "piece.txt").read_text().strip() if (d / "piece.txt").exists() else ""
    if not piece:
        errs.append("no piece.txt (the doodle's piece name)")
    if not (d / "card.png").exists():
        errs.append("no card.png (doodle still, 1200x630)")
    return _report(errs, verbose)


def _report(errs, verbose):
    if verbose:
        print("QA green" if not errs else "QA red:\n  " + "\n  ".join(errs))
    return not errs


# ---------------------------------------------------------------- ship
def ship(slug):
    d = STAGE / slug
    if not qa(slug):
        sys.exit("not shipped: QA red")
    note = next(n for n in d.glob("*.md") if n.name != "research.md")
    meta, _ = front_matter(note.read_text())
    art_slug = (d / "route.txt").read_text().strip() if (d / "route.txt").exists() else re.sub(r"[^a-z0-9]+", "-", note.stem.lower()).strip("-")
    piece = (d / "piece.txt").read_text().strip()
    VAULT_ART.mkdir(parents=True, exist_ok=True)
    shutil.copy2(note, VAULT_ART / note.name)
    shutil.copy2(d / "card.png", ROOT / "assets" / "cards" / f"articles-{art_slug}.png")
    topics = jload(ROOT / "topics.json")
    topics["topics"] = [t for t in topics["topics"] if t["slug"] != art_slug]
    topics["topics"].append({
        "slug": art_slug, "note": note.stem, "keyword": meta["keyword"], "alt_keywords": [],
        "competition": "low", "intent": "informational", "title": meta["title"], "desc": meta["description"],
        "status": "drafted", "card": "doodle", "doodle": piece, "blocks": [], "refresh_days": 90,
        "tags": [t.strip() for t in meta["tags"].split(",")], "frontier": slug,
    })
    jsave(ROOT / "topics.json", topics)
    subprocess.run(["node", "tools/build-defiant.mjs"], cwd=DOODLE, check=True)
    log(slug, slug.split("-", 3)[-1], "shipped")
    print(f"shipped {slug} → /articles/{art_slug}/ (the 03:30 nightly builds and deploys it)")


def board():
    for p in sorted(STAGE.glob("*")):
        if p.is_dir():
            ok = qa(p.name, verbose=False)
            notes = [n for n in p.glob("*.md") if n.name != "research.md"]
            print(f"{p.name:44} {'green' if ok else 'red  '}  {notes[0].stem if notes else '(no note)'}")
    shipped = [r for r in ledger() if r["state"] == "shipped"]
    if shipped:
        print("\nshipped:")
        for r in shipped:
            print(f"  {r['date']}  {r['slug']}")


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    cmd = a[0]
    if cmd == "harvest":
        harvest(a[1] if len(a) > 1 else None)
    elif cmd == "pick":
        pick()
    elif cmd == "brief":
        brief(a[1] if len(a) > 1 else pick()["id"])
    elif cmd == "qa":
        sys.exit(0 if qa(a[1]) else 1)
    elif cmd == "ship":
        ship(a[1])
    elif cmd == "board":
        board()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
