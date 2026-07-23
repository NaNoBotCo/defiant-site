#!/usr/bin/env python3
"""Generate a per-page OpenGraph share card (1200×630 PNG) for every page.

Zine aesthetic to match the site: white ground, glitch DEFIANT wordmark, magenta
eyebrow, big Impact title, halftone dots. Writes to assets/cards/<slug>.png
(committed source); build.py copies them into docs/ and points each page's
og:image at its own card. Run before build.py (nightly does this).

Needs Pillow. Fonts: Impact + Menlo (macOS system). Falls back gracefully.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from build import collect_notes, PAGE_OVERRIDES

ROOT = Path(__file__).resolve().parent
CARDS = ROOT / "assets" / "cards"
W, H = 1200, 630
INK = (11, 11, 11)
MAGENTA = (255, 23, 158)
CYAN = (0, 214, 214)
PURPLE = (122, 31, 214)
GREY = (90, 90, 90)

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


def card_fields(route, name, meta):
    t = meta.get("type", "")
    if route == "/":
        return ("US EXPAT SERVICES · MEDICAL TOURISM", "DEFIANT",
                "Chiang Mai, Thailand — plan your escape.")
    if t == "procedure":
        eb = "PROCEDURE · " + (meta.get("category", "") or "").upper()
        sub = f"Thailand {meta.get('th_cost', '')}  vs  US {meta.get('us_cost', '')}".strip()
        return (eb.strip(" ·"), name, sub)
    if t == "hospital":
        acc = meta.get("accreditation", "")
        return (f"HOSPITAL · {meta.get('city', '')}".strip(" ·"), name,
                f"{acc}-accredited" if acc else "")
    if t == "destination":
        return ("DESTINATION", name, "Where Defiant works.")
    if t == "guide":
        return ("GUIDE", meta.get("title", name), "")
    if t == "subscribe":
        return ("THE DISPATCH", "Get on the list", "Occasional email. Your data, not a third party's.")
    if t == "partners":
        return ("FOR CLINIC PARTNERS", "Partner with Defiant", "Free listing · interpreter · referrals")
    title = meta.get("title", name).split(" — ")[0].split(" | ")[0]
    return (t.upper() or "DEFIANT", title, meta.get("description", "")[:70])


def card_slug(route):
    s = route.strip("/").replace("/", "-")
    return s or "home"


def render(slug, eyebrow, title, subtitle):
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    for y in range(0, H, 24):
        for x in range(0, W, 24):
            d.ellipse([x, y, x + 2, y + 2], fill=(233, 233, 233))
    d.rectangle([0, 0, W, 12], fill=MAGENTA)
    d.rectangle([W // 3, 0, 2 * W // 3, 12], fill=CYAN)
    d.rectangle([2 * W // 3, 0, W, 12], fill=PURPLE)

    mark = font(IMPACT, 60)
    d.text((62, 55), "DEFIANT", font=mark, fill=CYAN)
    d.text((68, 55), "DEFIANT", font=mark, fill=MAGENTA)
    d.text((65, 55), "DEFIANT", font=mark, fill=INK)

    eb = font(MENLO, 30, index=1)
    d.text((65, 165), eyebrow[:60], font=eb, fill=MAGENTA)

    size = 96
    while size > 52:
        tf = font(IMPACT, size)
        if len(wrap(d, title, tf, W - 130)) <= 3:
            break
        size -= 8
    tf = font(IMPACT, size)
    lines = wrap(d, title, tf, W - 130)[:3]
    y = 215
    for ln in lines:
        d.text((69, y + 3), ln, font=tf, fill=CYAN)
        d.text((65, y), ln, font=tf, fill=INK)
        y += int(size * 1.02)

    if subtitle:
        sf = font(MENLO, 30)
        for ln in wrap(d, subtitle, sf, W - 130)[:2]:
            d.text((65, y + 14), ln, font=sf, fill=GREY)
            y += 40

    d.text((65, H - 60), "defiant.to", font=font(MENLO, 28, index=1), fill=INK)
    d.text((W - 250, H - 60), "survive the bs", font=font(MENLO, 24), fill=MAGENTA)

    CARDS.mkdir(parents=True, exist_ok=True)
    img.save(CARDS / f"{slug}.png", "PNG")


def main():
    notes = collect_notes()
    n = 0
    for route, (name, meta, _b) in notes.items():
        ov = PAGE_OVERRIDES.get(name, {})
        m = dict(meta)
        if "title" in ov:
            m["title"] = ov["title"]
        m.setdefault("title", name)
        eyebrow, title, subtitle = card_fields(route, name.lstrip("="), m)
        render(card_slug(route), eyebrow, title, subtitle)
        n += 1
    print(f"{n} share cards → {CARDS}")


if __name__ == "__main__":
    main()
