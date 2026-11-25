#!/usr/bin/env python3
"""Baut einen Herzensgedanken-Pin (1000 x 1500 px, JPEG).

Variante a = Foto (Unsplash) mit weißer Schrift
Variante b = Typografie auf Cremegrund mit Spirale
Variante c = Brief-Optik: Handschrift (Caveat) auf warmem Briefpapier

Beispiele:
  python3 render.py --variant a --photo "https://images.unsplash.com/...&w=1400" \
      --text "Der Kampf hört auf.|Nicht weil ich gewonnen habe.|Sondern weil niemand mehr kämpft." \
      --out pins/2026-12-01-Z02-a.jpg
  python3 render.py --variant b --text "Solange ich Bedingungen stelle, bleibt Liebe begrenzt." --out pins/x.jpg

Zeilenumbrüche: "|" im Text erzwingt einen Umbruch. Ohne "|" wird an Satzgrenzen
und danach nach Breite umbrochen (max. 85 % der Bildbreite). Die Schriftgröße ist
für das ganze Zitat einheitlich und wird nur verkleinert, wenn es sonst nicht passt.
"""
import argparse
import io
import os
import re
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1000, 1500
GOLD = 0.382
MAX_W = int(W * 0.85)

CREAM = (245, 241, 234)
INK = (44, 44, 44)
SAGE = (76, 101, 84)
WHITE = (255, 255, 255)


PAPER = (246, 238, 224)
INK_BLUE = (38, 44, 74)
SEPIA = (120, 98, 72)


def hand(size, weight=500):
    f = ImageFont.truetype(os.path.join(HERE, "fonts", "Caveat[wght].ttf"), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def font(size, italic=False, weight=400):
    name = "CormorantGaramond-Italic[wght].ttf" if italic else "CormorantGaramond[wght].ttf"
    f = ImageFont.truetype(os.path.join(HERE, "fonts", name), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, text, f):
    if "|" in text:
        parts = [p.strip() for p in text.split("|") if p.strip()]
    else:
        parts = [p.strip() for p in re.split(r"(?<=[.!?…:])\s+", text) if p.strip()]
    lines = []
    for p in parts:
        if text_w(draw, p, f) <= MAX_W:
            lines.append(p)
            continue
        cur = ""
        for word in p.split():
            test = (cur + " " + word).strip()
            if text_w(draw, test, f) <= MAX_W:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def layout(draw, text, start=66, minimum=46, max_lines=9, face=None):
    face = face or font
    size = start
    while True:
        f = face(size)
        lines = wrap(draw, text, f)
        forced = [p.strip() for p in text.split("|") if p.strip()] if "|" in text else None
        no_split = forced is None or len(lines) == len(forced)
        no_orphan = all(len(l.split()) > 1 for l in lines) or len(text.split()) <= 2
        fits = (all(text_w(draw, l, f) <= MAX_W for l in lines)
                and len(lines) <= max_lines and no_split and no_orphan)
        if fits or size <= minimum:
            return f, size, lines
        size -= 2


def cover(img):
    s = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * s + 0.5), int(img.height * s + 0.5)), Image.LANCZOS)
    l = (img.width - W) // 2
    t = (img.height - H) // 2
    return img.crop((l, t, l + W, t + H))


def gradient_overlay(img):
    ov = Image.new("RGBA", (W, H))
    px = ov.load()
    for y in range(H):
        p = y / (H - 1)
        if p < 0.6:
            a = 0.30 + (0.15 - 0.30) * (p / 0.6)
        else:
            a = 0.15 + (0.40 - 0.15) * ((p - 0.6) / 0.4)
        for x in range(W):
            px[x, y] = (20, 25, 40, int(a * 255))
    return Image.alpha_composite(img.convert("RGBA"), ov)


def draw_quote(base, text, color, center_y, shadow=False):
    d = ImageDraw.Draw(base)
    f, size, lines = layout(d, text)
    lh = size * 1.45
    top = center_y - (len(lines) - 1) * lh / 2
    top = max(top, 140)
    if shadow:
        sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        for i, l in enumerate(lines):
            sd.text((W / 2, top + i * lh), l, font=f, fill=(0, 0, 0, 110), anchor="mm")
        sh = sh.filter(ImageFilter.GaussianBlur(8))
        base.alpha_composite(sh)
        d = ImageDraw.Draw(base)
    for i, l in enumerate(lines):
        d.text((W / 2, top + i * lh), l, font=f, fill=color, anchor="mm")
    return lines, size


def footer(base, c_title, c_line, c_url):
    d = ImageDraw.Draw(base)
    d.text((W / 2, H - 150), "Herzensgedanken", font=font(32, italic=True), fill=c_title, anchor="ms")
    d.line([(W / 2 - 40, H - 118), (W / 2 + 40, H - 118)], fill=c_line, width=2)
    d.text((W / 2, H - 72), "johannesfies.de", font=font(32), fill=c_url, anchor="ms")


def render_a(text, photo_url):
    req = urllib.request.Request(photo_url, headers={"User-Agent": "herzensgedanken-pins"})
    raw = urllib.request.urlopen(req, timeout=60).read()
    img = cover(Image.open(io.BytesIO(raw)).convert("RGB"))
    base = gradient_overlay(img)
    draw_quote(base, text, WHITE, H * GOLD, shadow=True)
    footer(base, (255, 255, 255, 230), (255, 255, 255, 205), WHITE)
    return base


def render_b(text):
    base = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(base)
    f, size, lines = layout(d, text)
    lh = size * 1.45
    center = H * GOLD + 40
    top = center - (len(lines) - 1) * lh / 2
    logo = Image.open(os.path.join(HERE, "assets", "spirale.png")).convert("RGBA")
    lw = 108
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    a = logo.split()[3].point(lambda v: int(v * 0.55))
    logo.putalpha(a)
    ly = int(top - size * 0.6 - 60 - logo.height)
    base.alpha_composite(logo, (W // 2 - lw // 2, max(ly, 60)))
    draw_quote(base, text, INK, center)
    footer(base, SAGE, (44, 44, 44, 90), INK)
    return base


def paper():
    import random
    rnd = random.Random(7)
    base = Image.new("RGB", (W, H), PAPER)
    noise = Image.effect_noise((W, H), 14).convert("L")
    tint = Image.merge("RGB", [noise.point(lambda v: v * 0.06 + 236)] * 3)
    base = Image.blend(base, tint, 0.18)
    # sanfte Vignette, wie altes Papier
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    for i in range(60):
        vd.rectangle([i * 3, i * 3, W - i * 3, H - i * 3], outline=int(60 - i))
    vig = vig.filter(ImageFilter.GaussianBlur(30))
    shade = Image.new("RGB", (W, H), (205, 188, 160))
    base = Image.composite(shade, base, vig.point(lambda v: v // 2))
    base = base.convert("RGBA")
    return base


def render_c(text):
    global MAX_W
    base = paper()
    d = ImageDraw.Draw(base)
    old = MAX_W
    MAX_W = W - 250
    f, size, lines = layout(d, text, start=90, minimum=48, max_lines=10, face=hand)
    MAX_W = old
    lh = int(size * 1.28)
    n = len(lines)
    first = int(H * GOLD + 40 - (n - 1) * lh / 2)
    first = max(first, 230)
    # feine Linien nur unter den Zeilen, eine Linie Luft darüber und darunter
    for i in range(-1, n + 1):
        y = first + i * lh + int(size * 0.18)
        d.line([(110, y), (W - 110, y)], fill=(150, 128, 100, 70), width=2)
    for i, l in enumerate(lines):
        d.text((125, first + i * lh), l, font=f, fill=INK_BLUE, anchor="ls")
    footer(base, SEPIA, (120, 98, 72, 120), INK)
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["a", "b", "c"], required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--photo", help="Unsplash-URL (nur Variante a)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.variant == "a":
        if not a.photo:
            raise SystemExit("Variante a braucht --photo")
        img = render_a(a.text, a.photo)
    elif a.variant == "c":
        img = render_c(a.text)
    else:
        img = render_b(a.text)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    img.convert("RGB").save(a.out, "JPEG", quality=90, optimize=True)
    print(a.out)


if __name__ == "__main__":
    main()
