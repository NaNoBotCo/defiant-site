#!/usr/bin/env python3
"""Generate a rich per-page OpenGraph share card (1200×630 PNG) for every page.

The card IS the marketing: for a procedure it renders the price comparison as the
hero — US price struck through, Thailand price large, a big SAVE ~X% badge — because
people share the number, not the logo. Hospitals show city + accreditation; the
concierge card shows both fee tiers; guides show the title + hook. Zine aesthetic to
match the site (white ground, glitch DEFIANT wordmark, halftone dots, magenta/cyan).

Writes assets/cards/<slug>.png (committed source); build.py copies them into docs/
and points each page's og:image at its own card. Run before build.py (nightly does).

Needs Pillow. Fonts: Impact + Menlo (macOS system). Falls back gracefully.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from build import collect_notes, PAGE_OVERRIDES, FOR_AGENTS_MD, _prices

ROOT = Path(__file__).resolve().parent
CARDS = ROOT / "assets" / "cards"
W, H = 1200, 630
INK = (11, 11, 11)
MAGENTA = (255, 23, 158)
CYAN = (0, 214, 214)
PURPLE = (122, 31, 214)
GREY = (110, 110, 110)
MARK = (255, 229, 102)       # highlighter yellow for the savings badge
PAPER = (255, 255, 255)

IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
MENLO = "/System/Library/Fonts/Menlo.ttc"


def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def savings_pct(us, th):
    """Credible savings band, or None — mirrors build.savings_line's 15–95 clamp so
    the card never overstates (course-vs-cycle unit mismatches drop out)."""
    un, tn = _prices(us), _prices(th)
    if un and tn and max(un) and max(tn):
        lo = round((1 - max(tn) / max(un)) * 100)
        hi = round((1 - min(tn) / min(un)) * 100)
        lo, hi = sorted((lo, hi))
        if 15 <= lo and hi <= 95:
            return (lo, hi)
    return None


def base(draw):
    """Halftone field + top colour bar + glitch wordmark. Shared chrome."""
    for y in range(0, H, 24):
        for x in range(0, W, 24):
            draw.ellipse([x, y, x + 2, y + 2], fill=(234, 234, 234))
    draw.rectangle([0, 0, W, 12], fill=MAGENTA)
    draw.rectangle([W // 3, 0, 2 * W // 3, 12], fill=CYAN)
    draw.rectangle([2 * W // 3, 0, W, 12], fill=PURPLE)
    mark = font(IMPACT, 54)
    draw.text((68, 46), "DEFIANT", font=mark, fill=CYAN)
    draw.text((72, 46), "DEFIANT", font=mark, fill=MAGENTA)
    draw.text((70, 46), "DEFIANT", font=mark, fill=INK)


def footer(draw, stamp=True):
    draw.text((65, H - 58), "defiant.to", font=font(MENLO, 26, index=1), fill=INK)
    if stamp:
        draw.text((W - 275, H - 58), "survive the bs", font=font(MENLO, 24), fill=MAGENTA)


def title_block(draw, eyebrow, title, y=132, max_lines=2, top=95):
    draw.text((65, y - 40), eyebrow[:64], font=font(MENLO, 28, index=1), fill=MAGENTA)
    size = top
    while size > 46:
        tf = font(IMPACT, size)
        if len(wrap(draw, title, tf, W - 130)) <= max_lines:
            break
        size -= 6
    tf = font(IMPACT, size)
    for ln in wrap(draw, title, tf, W - 130)[:max_lines]:
        draw.text((69, y + 3), ln, font=tf, fill=CYAN)
        draw.text((65, y), ln, font=tf, fill=INK)
        y += int(size * 1.02)
    return y


def strike(draw, x, y, text, fnt, fill):
    draw.text((x, y), text, font=fnt, fill=fill)
    w = draw.textlength(text, font=fnt)
    cy = y + fnt.size * 0.55
    draw.line([(x - 3, cy), (x + w + 3, cy)], fill=MAGENTA, width=5)


def render_procedure(slug, name, category, us, th, pct):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    base(d)
    y = title_block(d, ("PROCEDURE · " + (category or "")).strip(" ·").upper(), name, y=150, top=88)
    py = max(y + 26, 350)
    lab, big = font(MENLO, 26, index=1), font(MENLO, 52, index=1)
    d.text((65, py), "UNITED STATES", font=lab, fill=GREY)
    strike(d, 65, py + 34, us or "—", font(MENLO, 40, index=1), GREY)
    d.text((560, py), "THAILAND", font=lab, fill=CYAN)
    d.text((560, py + 30), (th or "—"), font=big, fill=MAGENTA)
    if pct:
        lo, hi = pct
        txt = f"SAVE ~{lo}%" if lo == hi else f"SAVE ~{lo}-{hi}%"
        bf = font(IMPACT, 62)
        tw = d.textlength(txt, font=bf)
        bx, by = W - tw - 130, py + 150
        d.rectangle([bx - 26, by - 14, bx + tw + 26, by + 78], fill=MARK, outline=INK, width=4)
        d.text((bx, by), txt, font=bf, fill=INK)
    else:
        d.text((65, py + 150), "A fraction of the US price — confirmed in writing.",
               font=font(MENLO, 28), fill=GREY)
    footer(d)
    img.save(CARDS / f"{slug}.png", "PNG")


def render_hospital(slug, name, city, acc):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    base(d)
    y = title_block(d, ("HOSPITAL · " + (city or "")).strip(" ·").upper(), name, y=150, top=84)
    if acc:
        bf = font(IMPACT, 46)
        txt = f"{acc}-ACCREDITED"
        tw = d.textlength(txt, font=bf)
        by = max(y + 40, 430)
        col = CYAN if acc.upper() == "JCI" else MAGENTA
        d.rectangle([61, by - 10, 61 + tw + 40, by + 60], fill=col, outline=INK, width=4)
        d.text((81, by), txt, font=bf, fill=INK)
    footer(d)
    img.save(CARDS / f"{slug}.png", "PNG")


def render_concierge(slug):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    base(d)
    title_block(d, "WHAT IT COSTS · ALL OF IT", "The receipt America never gives you", y=150, top=72)
    py = 360
    big = font(IMPACT, 92)
    d.text((65, py), "$999", font=big, fill=MAGENTA)
    d.text((65, py + 108), "full concierge", font=font(MENLO, 30), fill=INK)
    d.text((640, py), "$99", font=big, fill=INK)
    d.text((640, py + 108), "DIY virtual pack", font=font(MENLO, 30), fill=INK)
    d.text((640, py + 150), "pay in Bitcoin, save 3%", font=font(MENLO, 24), fill=PURPLE)
    footer(d)
    img.save(CARDS / f"{slug}.png", "PNG")


def render_generic(slug, eyebrow, title, subtitle):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    base(d)
    y = title_block(d, eyebrow.upper(), title, y=170, max_lines=3, top=92)
    if subtitle:
        sf = font(MENLO, 30)
        for ln in wrap(d, subtitle, sf, W - 130)[:2]:
            d.text((65, y + 16), ln, font=sf, fill=GREY)
            y += 40
    footer(d)
    img.save(CARDS / f"{slug}.png", "PNG")


def card_slug(route):
    return route.strip("/").replace("/", "-") or "home"


def build_one(route, name, meta):
    slug = card_slug(route)
    t = meta.get("type", "")
    nm = name.lstrip("=")
    if route == "/":
        render_generic(slug, "US expat services · medical tourism",
                       "Pay what the locals pay", "Chiang Mai, Thailand — plan your escape.")
    elif t == "procedure":
        render_procedure(slug, nm, meta.get("category", ""),
                         meta.get("us_cost", ""), meta.get("th_cost", ""),
                         savings_pct(meta.get("us_cost", ""), meta.get("th_cost", "")))
    elif t == "hospital":
        render_hospital(slug, nm, meta.get("city", ""), meta.get("accreditation", ""))
    elif t == "pricing" or route == "/concierge/":
        render_concierge(slug)
    else:
        title = (meta.get("title", nm)).split(" — ")[0].split(" | ")[0]
        eb = {"guide": "GUIDE", "destination": "DESTINATION", "agents": "FOR AGENTS & BOTS",
              "subscribe": "THE DISPATCH", "partners": "FOR CLINIC PARTNERS"}.get(t, "DEFIANT")
        render_generic(slug, eb, title, (meta.get("description", "") or "")[:90])


def main():
    notes = dict(collect_notes())
    notes["/for-agents/"] = ("For Agents & Bots", {"type": "agents",
                             "title": "For Agents & Bots", "description":
                             "Machine-readable surfaces and a documented lead endpoint."}, FOR_AGENTS_MD)
    n = 0
    for route, (name, meta, _b) in notes.items():
        ov = PAGE_OVERRIDES.get(name, {})
        m = dict(meta)
        if "title" in ov:
            m["title"] = ov["title"]
        m.setdefault("title", name)
        build_one(route, name, m)
        n += 1
    print(f"{n} rich share cards → {CARDS}")


if __name__ == "__main__":
    main()
