#!/usr/bin/env python3
"""Compile the Defiant vault (~/Documents/Defiant) into the defiant.to site.

Stdlib only. Vault is canonical: edit notes in Obsidian, run `python3 build.py`,
commit docs/. The build fails loudly on unresolved wikilinks or broken internal
hrefs, and hard-fails if the encrypted email address ever appears in emitted
HTML (it is only ever assembled client-side from char codes).

Usage:  python3 build.py            build into docs/
        python3 build.py --check    build + report only (same thing, alias)
"""
import re
import shutil
import sys
import urllib.parse
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VAULT = Path.home() / "Documents" / "Defiant"
PUB = VAULT / "Public Links"
ART = PUB / "Articles"
OUT = ROOT / "docs"

SITE = "https://defiant.to"
WORKER_URL = "https://defiant-leads.wichaa.workers.dev"  # adjust after `wrangler deploy` if different
KOFI = "https://ko-fi.com/defiantchiangmai"
LINE_URL = "https://line.me/ti/p/~defiant.to"
FB_PEACOCKS_LAW = ("https://www.facebook.com/skunkhaus/posts/"
                   "pfbid06spJJ7hDXrwjyFjECpMcXNnmuALnsUmiSpbnWnxHAwQnLEdb9LAYCSWTbSXzPAshl")
PUBLISH_HOME = "https://publish.obsidian.md/defiant"
TODAY = date(2026, 7, 23).isoformat()

# 530kings@proton.me as char codes — the string itself must never appear in output.
EMAIL_CODES = "53,51,48,107,105,110,103,115,64,112,114,111,116,111,110,46,109,101"

MISSING_LINKS: list[str] = []
WARNINGS: list[str] = []


def slug(name: str) -> str:
    out = []
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


# ---------------------------------------------------------------- note loading
def parse_note(path: Path):
    raw = path.read_text(encoding="utf-8")
    meta = {}
    if raw.startswith("---\n"):
        end = raw.find("\n---", 4)
        if end != -1:
            for ln in raw[4:end].splitlines():
                if ":" in ln:
                    k, _, v = ln.partition(":")
                    meta[k.strip()] = v.strip()
            raw = raw[end + 4:]
    return meta, raw.strip("\n")


def collect_notes():
    """route -> (name, meta, body). Also builds the wikilink map."""
    notes = {}

    def add(path: Path, route: str):
        if not path.exists():
            WARNINGS.append(f"note missing: {path}")
            return
        meta, body = parse_note(path)
        notes[route] = (path.stem, meta, body)

    add(PUB / "=Home.md", "/")
    add(PUB / "=Contact.md", "/contact/")
    add(PUB / "=Procedures.md", "/procedures/")
    add(PUB / "=Hospitals.md", "/hospitals/")
    add(PUB / "=Destinations.md", "/destinations/")
    add(PUB / "=Privacy Policy.md", "/privacy/")
    add(PUB / "=Terms of Service.md", "/terms/")
    add(VAULT / "Mozarts-Ghost.md", "/mozarts-ghost/")
    add(VAULT / "Stem Cell Therapy.md", "/procedures/stem-cell-therapy/")
    flags = ART / "Various LGBTQIA+ Community Flags and their meanings.md"
    if flags.exists():
        add(flags, "/articles/community-flags/")
    for sub, prefix in [("Procedures", "/procedures/"), ("Hospitals", "/hospitals/"),
                        ("Destinations", "/destinations/")]:
        d = ART / sub
        for p in sorted(d.glob("*.md")):
            add(p, f"{prefix}{slug(p.stem)}/")
    return notes


# ------------------------------------------------------- per-note pre-transforms
# %%BTN:subject|label%% tokens survive escaping and become reveal buttons inline.
def pre_transform(name: str, body: str) -> str:
    if name == "=Privacy Policy":
        body = body.replace("Email: [privacy@defiant.to](mailto:privacy@defiant.to)",
                            "Contact: [the form](/contact/)")
        body = body.replace("[privacy@defiant.to](mailto:privacy@defiant.to)",
                            "[the contact form](/contact/)")
        body = body.replace("**530kings@proton.me**",
                            "%%BTN:Privacy question|tap to reveal the address%%")
        body = body.replace("Encrypted Mail: 530kings@proton.me",
                            "Encrypted mail: %%BTN:Privacy question|tap to reveal%%")
        body = body.replace("530kings@proton.me", "%%BTN:Privacy question|tap to reveal%%")
    if name == "Mozarts-Ghost":
        body = re.sub(r"\[Email us at [^\]]*\]\(mailto:[^)]*\)",
                      "%%BTN:Mozart's Ghost VIP|tap to reveal the secret address%%", body)
        body = body.replace("530kings@proton.me", "the secret address (tap above)")
    if name == "=Contact":
        body = body.replace(
            "bots can harvest them.",
            "bots can harvest them. %%BTN:Encrypted intake|Tap to reveal the encrypted address%%")
    return body


# ---------------------------------------------------------------- md renderer
def setext_to_atx(lines):
    out, i = [], 0
    while i < len(lines):
        cur = lines[i]
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if (cur.strip() and not re.match(r"^(#|-\s|\*\s|\||>|<|!\[)", cur.strip())
                and re.fullmatch(r"-{3,}", nxt.strip() or "x") ):
            out.append("## " + cur.strip()); i += 2; continue
        if cur.strip() and re.fullmatch(r"={3,}", nxt.strip() or "x"):
            out.append("# " + cur.strip()); i += 2; continue
        out.append(cur); i += 1
    return out


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_inline(links: dict):
    def wikilink(m):
        name = m.group(1).strip()
        alias = (m.group(2) or name).strip()
        target = links.get(name) or links.get("=" + name)
        if target is None:
            MISSING_LINKS.append(name)
            return alias
        return f'<a href="{target}">{alias}</a>'

    def mdlink(m):
        text, href = m.group(1), m.group(2)
        raw = urllib.parse.unquote(href)
        if raw.endswith(".md"):
            stem = Path(raw).stem
            target = links.get(stem) or links.get("=" + stem)
            if target:
                href = target
            else:
                MISSING_LINKS.append(stem)
        return f'<a href="{href}"{" rel=noopener target=_blank" if href.startswith("http") else ""}>{text}</a>'

    def inline(t: str) -> str:
        t = esc(t)
        t = re.sub(r"%%BTN:([^|%]+)\|([^%]+)%%",
                   r'<button class="reveal" type="button" data-subject="\1">\2</button>', t)
        t = re.sub(r"\[\[([^\]|]+?)(?:\|([^\]]*?))?\]\]", wikilink, t)
        t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", mdlink, t)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
        return t
    return inline


def md_to_html(body: str, inline, note_name: str) -> str:
    lines = setext_to_atx(body.split("\n"))
    html, para, table, lst, raw_mode = [], [], [], None, False

    def flush_para():
        if para:
            html.append("<p>" + inline(" ".join(x.strip() for x in para)) + "</p>")
            para.clear()

    def flush_table():
        nonlocal table
        if not table:
            return
        head, rows = table[0], table[1:]
        use_head = any(c.strip() for c in head)
        t = ['<div class="tablewrap"><table>']
        if use_head:
            t.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr>")
        else:
            rows = table[1:]
        for r in rows:
            t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
        t.append("</table></div>")
        html.append("".join(t))
        table = []

    def close_list():
        nonlocal lst
        if lst:
            html.append(f"</{lst}>")
            lst = None

    i = 0
    while i < len(lines):
        line = lines[i]; s = line.strip(); i += 1

        if raw_mode:
            html.append(line)
            if "</a>" in s:
                raw_mode = False
            continue
        if s.startswith("<a ") and "</a>" not in s:
            flush_para(); flush_table(); close_list()
            html.append(line); raw_mode = True; continue
        if s.startswith("<") and s.endswith(">"):
            flush_para(); flush_table(); close_list()
            html.append(line); continue

        if not s:
            # blank inside a list is ignorable if the list continues
            if lst and i < len(lines):
                j = i
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and re.match(r"^\s*[-*]\s+", lines[j]):
                    continue
            flush_para(); flush_table(); close_list(); continue

        if s.startswith("|"):
            flush_para(); close_list()
            if re.fullmatch(r"\|[\s:|-]+\|?", s):
                continue
            table.append([c.strip() for c in s.strip("|").split("|")])
            continue
        flush_table()

        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            flush_para(); close_list()
            lvl = len(m.group(1))
            txt = inline(m.group(2))
            html.append(f'<h{lvl} id="{slug(m.group(2))}">{txt}</h{lvl}>')
            continue
        if re.fullmatch(r"-{3,}", s) or re.fullmatch(r"\*{3,}", s):
            flush_para(); close_list(); html.append("<hr>"); continue
        if s.startswith("> "):
            flush_para(); close_list()
            html.append(f"<blockquote><p>{inline(s[2:])}</p></blockquote>"); continue
        m = re.match(r"^[-*]\s+(.*)$", s)
        if m:
            flush_para(); flush_table()
            if lst != "ul":
                close_list(); html.append("<ul>"); lst = "ul"
            html.append(f"<li>{inline(m.group(1))}</li>"); continue
        m = re.match(r"^!\[\[([^\]]+)\]\]$", s)
        if m:
            flush_para(); close_list()
            fname = m.group(1)
            src = next(iter(VAULT.glob(f"**/{fname}")), None)
            if src:
                dest = OUT / "assets" / "vault" / (slug(Path(fname).stem) + src.suffix)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                html.append(f'<img src="/assets/vault/{dest.name}" alt="{esc(Path(fname).stem)}" loading="lazy">')
            else:
                WARNINGS.append(f"{note_name}: embedded file not found: {fname}")
            continue
        para.append(line)

    flush_para(); flush_table(); close_list()
    return "\n".join(html)


# ---------------------------------------------------------------- page chrome
PAGE_OVERRIDES = {
    "=Procedures": dict(
        title="Procedures & Honest Prices — Thailand Medical Tourism",
        description="Every procedure Defiant routes, with indicative US-vs-Thailand price ranges and the honest caveats: orthopedic, cardiac, dental, fertility, bariatric, gender affirmation, eyes, oncology and more.",
        intro=("Every number is an indicative range, every quote gets confirmed in writing "
               "before you book, and the pages below say so out loud when something is a bad "
               "idea. That's the whole editorial policy.")),
    "=Privacy Policy": dict(title="Privacy Policy",
                            description="How Defiant handles your data: minimal collection, no selling, and a flat refusal to hand personal information to US government agencies."),
    "=Terms of Service": dict(title="Terms of Service",
                              description="The deal, in plain words: Defiant is a medical-tourism concierge and information service — not a healthcare provider."),
    "Mozarts-Ghost": dict(title="Mozart's Ghost", description="The best band on the internet.", noindex=True),
    "Various LGBTQIA+ Community Flags and their meanings": dict(
        title="LGBTQIA+ Community Flags and Their Meanings",
        description="A field guide to community flags — colors, history, and meanings."),
}

COUNTER_JS = """<script>(function(){var el=document.getElementById('dobbs-days');if(!el)return;
var d=Math.floor((Date.now()-Date.parse('2022-06-24T00:00:00Z'))/864e5);
el.textContent=d.toLocaleString('en-US');})();</script>"""

REVEAL_JS = ("<script>(function(){var a=[" + EMAIL_CODES + "].map(function(c){return "
             "String.fromCharCode(c)}).join('');document.querySelectorAll('button.reveal')"
             ".forEach(function(b){b.addEventListener('click',function(){var l=document.createElement('a');"
             "l.href='mailto:'+a+(b.dataset.subject?'?subject='+encodeURIComponent(b.dataset.subject):'');"
             "l.textContent=a;b.replaceWith(l)})})})();</script>")

FORM_HTML = """<form id="lead-form" class="lead-form">
<label>Name<br><input name="name" autocomplete="name" maxlength="200"></label>
<label>How do we reach you? (email / LINE / Signal) <span class="req">*</span><br>
<input name="contact" required maxlength="300"></label>
<label>What are you trying to fix? <span class="req">*</span><br>
<textarea name="message" required rows="7" maxlength="5000" placeholder="Blink twice if you need help."></textarea></label>
<div class="hp" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>
<button type="submit" class="send">SEND IT ✊</button>
<p id="form-ok" hidden><strong>Got it.</strong> A human — probably NaN — reads every one of these. You'll hear back within a day.</p>
<p id="form-err" hidden><strong>That didn't go through.</strong> The backup channels below still work — LINE us, or reveal the encrypted address.</p>
</form>"""

FORM_JS = ("<script>(function(){var f=document.getElementById('lead-form');if(!f)return;"
           "var t0=Date.now();f.addEventListener('submit',function(e){e.preventDefault();"
           "if(!f.reportValidity())return;var b=f.querySelector('.send');b.disabled=true;b.textContent='SENDING…';"
           f"fetch('{WORKER_URL}/lead'" + ",{method:'POST',headers:{'Content-Type':'application/json'},"
           "body:JSON.stringify({name:f.name.value,contact:f.contact.value,message:f.message.value,"
           "website:f.website.value,t0:t0})}).then(function(r){return r.json()}).then(function(j){"
           "if(j.ok){f.querySelector('#form-ok').hidden=false;b.textContent='SENT ✊';}"
           "else{throw 0}}).catch(function(){f.querySelector('#form-err').hidden=false;"
           "b.disabled=false;b.textContent='SEND IT ✊';})});})();</script>")

ORG_JSONLD = ("""<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization",
"name":"Defiant","alternateName":"Defiant Health","url":"https://defiant.to",
"logo":"https://defiant.to/assets/images/favicon.png",
"description":"US expat services and medical tourism concierge in Chiang Mai, Thailand.",
"address":{"@type":"PostalAddress","addressLocality":"Chiang Mai","addressCountry":"TH"},
"contactPoint":{"@type":"ContactPoint","contactType":"intake","url":"https://defiant.to/contact/"},
"sameAs":["""
              + f'"{KOFI}","{PUBLISH_HOME}"' + "]}</script>")

NAV = ('<nav><a href="/procedures/">Procedures</a><a href="/hospitals/">Hospitals</a>'
       '<a href="/destinations/">Destinations</a><a class="cta" href="/contact/">Blink Twice</a></nav>')

FOOTER = f"""<footer>
<p class="foot-shout">Plan your escape. Defy the system. Survive the bullshit.</p>
<p><a href="/privacy/">Privacy Policy</a> · <a href="/terms/">Terms of Service</a> ·
<a href="{FB_PEACOCKS_LAW}" rel="noopener" target="_blank">Peacock's Law</a> ·
<a href="{KOFI}" rel="noopener" target="_blank">Fund the resistance ☕</a> ·
<a href="{LINE_URL}" rel="noopener" target="_blank">LINE: defiant.to</a> ·
<a href="{PUBLISH_HOME}" rel="noopener" target="_blank">The Notebook</a></p>
<p class="peacock">This site allows AI crawlers and automated agents to index, summarize, and train on its public content.
<a class="pi" href="/mozarts-ghost/" aria-label="secret">π</a></p>
<p>© 2025–2026 Defiant · Chiang Mai, Thailand · <span lang="th">ดีไฟแอนท์</span></p>
</footer>"""


def page(name, meta, body_html, route):
    ov = PAGE_OVERRIDES.get(name, {})
    title = ov.get("title") or meta.get("title") or name.lstrip("=")
    desc = ov.get("description") or meta.get("description") or "Defiant — US expat services and medical tourism concierge in Chiang Mai, Thailand."
    noindex = ov.get("noindex", False)
    full_title = title if route == "/" else f"{title} | Defiant"
    if "<h1" not in body_html:
        body_html = f"<h1>{esc(title)}</h1>\n" + body_html
    if ov.get("intro"):
        body_html = body_html.replace("</h1>", "</h1>\n<p class=\"lead\">" + ov["intro"] + "</p>", 1)

    scripts = []
    if route == "/":
        scripts.append(COUNTER_JS)
    if 'class="reveal"' in body_html:
        scripts.append(REVEAL_JS)
    if "<!-- defiant:form -->" in body_html:
        body_html = body_html.replace("<!-- defiant:form -->", FORM_HTML)
        scripts.append(FORM_JS)

    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light only">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="canonical" href="{SITE}{route}">
<meta property="og:site_name" content="Defiant"><meta property="og:type" content="website">
<meta property="og:title" content="{esc(full_title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE}{route}"><meta property="og:image" content="{SITE}/assets/images/share.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/assets/images/favicon.png">
<link rel="apple-touch-icon" href="/assets/images/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?display=swap&family=Alfa+Slab+One&family=Martian+Mono:wght@300;400;700" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css">
{ORG_JSONLD if route == "/" else ""}
</head><body>
<header><a class="logo" href="/">DEFIANT<span class="fist">✊</span></a>{NAV}</header>
<main>
{body_html}
</main>
{FOOTER}
{"".join(scripts)}
</body></html>"""


def home_post(html_body: str) -> str:
    html_body = html_body.replace(
        '<h1 id="defiant">DEFIANT</h1>',
        '<div class="hero"><div class="hero-text"><h1 id="defiant">DEFIANT</h1>', 1)
    html_body = html_body.replace(
        "<p>ดิงด่อง เฮลโล เวลคัม</p>",
        '<p class="thai-garnish">ดิงด่อง เฮลโล เวลคัม</p></div>'
        '<img class="hero-fist" src="/assets/images/image01.jpg" '
        'alt="DEFIANT — raised fist artwork in teal and pink halftone">'
        "</div>", 1)
    html_body = re.sub(
        r'<h1 id="american-healthcare-is-bullshit">(.*?)</h1>',
        r'<h2 class="shout" id="american-healthcare-is-bullshit">\1</h2>', html_body)
    html_body = re.sub(r"([\d,]+)\+ days", r'<span id="dobbs-days">\1+</span> days', html_body, count=1)
    for who, img, alt in [
            ("NaN", "image04.png", "Pixel-art portrait of NaN — rainbow sunglasses, a Chiang Mai wat behind her"),
            ("KAI", "image05.png", "Pixel-art portrait of KAI — dark hair and stubble"),
            ("ROBIN", "image02.png", "Pixel-art portrait of ROBIN — pink hair, purple glasses, consultant blazer")]:
        html_body = re.sub(
            rf"<h3 ([^>]*)>('|&#39;)?{who}",
            f'<img class="portrait" src="/assets/images/{img}" alt="{alt}" loading="lazy"><h3 \\1>\\2{who}',
            html_body, count=1)
    html_body = html_body.replace(
        "<p>*names changed for privacy</p>",
        '<p>*names changed for privacy</p>\n<a class="flags" href="/articles/community-flags/">'
        '<img src="/assets/images/image06.png" alt="Strip of LGBTQIA+ pride flags" loading="lazy"></a>')
    return html_body


# ---------------------------------------------------------------- build
def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    shutil.copytree(ROOT / "assets" / "images", OUT / "assets" / "images")
    shutil.copy2(ROOT / "assets" / "styles.css", OUT / "assets" / "styles.css")

    notes = collect_notes()
    links = {name: route for route, (name, _, _) in notes.items()}

    inline = make_inline(links)
    emitted = {}
    for route, (name, meta, body) in notes.items():
        body = pre_transform(name, body)
        html_body = md_to_html(body, inline, name)
        if route == "/":
            html_body = home_post(html_body)
        emitted[route] = page(name, meta, html_body, route)

    for route, html in emitted.items():
        dest = OUT / route.strip("/") / "index.html" if route != "/" else OUT / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")

    # 404, robots, llms, sitemap, CNAME
    notfound = page("404", {"title": "404 — Not Found"},
                    "<h1>404</h1><p>That page escaped. Honestly? Respect.</p>"
                    '<p><a href="/">Back to the manifesto</a> · <a href="/procedures/">Browse procedures</a> · '
                    '<a href="/contact/">Blink twice</a></p>', "/404.html")
    (OUT / "404.html").write_text(notfound, encoding="utf-8")

    (OUT / "robots.txt").write_text(
        "# Peacock's Law: AI crawlers and automated agents are welcome to index,\n"
        "# summarize, and train on this site's public content.\n"
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {SITE}/sitemap.xml\n", encoding="utf-8")

    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for route, (name, meta, _) in sorted(notes.items()):
        if PAGE_OVERRIDES.get(name, {}).get("noindex"):
            continue
        pri = "1.0" if route == "/" else ("0.8" if route.count("/") == 2 else "0.6")
        lm = meta.get("updated", TODAY)
        sm.append(f"  <url><loc>{SITE}{route}</loc><lastmod>{lm}</lastmod><priority>{pri}</priority></url>")
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")

    lt = ["# Defiant — defiant.to",
          "> US expat services & medical-tourism concierge in Chiang Mai, Thailand.",
          "> American healthcare is bullshit; we are the exit ramp. AI agents welcome (Peacock's Law).",
          "", "## Pages"]
    for route, (name, meta, _) in sorted(notes.items()):
        ov = PAGE_OVERRIDES.get(name, {})
        if ov.get("noindex"):
            continue
        t = ov.get("title") or meta.get("title") or name.lstrip("=")
        d = ov.get("description") or meta.get("description") or ""
        lt.append(f"- [{t}]({SITE}{route}): {d}")
    lt += ["", "## Contact", f"- Intake form: {SITE}/contact/", f"- LINE: defiant.to ({LINE_URL})"]
    (OUT / "llms.txt").write_text("\n".join(lt) + "\n", encoding="utf-8")

    (OUT / "CNAME").write_text("defiant.to\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    # ---------------- checks
    problems = []
    if MISSING_LINKS:
        problems.append(f"unresolved wikilinks: {sorted(set(MISSING_LINKS))}")
    valid = set(emitted) | {"/404.html"}
    for route, html in emitted.items():
        for href in re.findall(r'(?:href|src)="(/[^"]*)"', html):
            path = href.split("#")[0]
            if path in valid:
                continue
            f = OUT / path.lstrip("/")
            if not (f.exists() or (f / "index.html").exists()):
                problems.append(f"{route}: broken internal ref {href}")
        if "530kings" in html:
            problems.append(f"{route}: EMAIL LEAKED IN PLAINTEXT")
    for w in WARNINGS:
        print("  warn:", w)
    if problems:
        print("\nBUILD FAILED:")
        for p in problems:
            print("  ✗", p)
        sys.exit(1)
    pages = len(emitted) + 1
    print(f"OK: {pages} pages → docs/ · sitemap {sum(1 for l in sm if '<url>' in l)} urls · email never in plaintext ✓")


if __name__ == "__main__":
    build()
