#!/usr/bin/env python3
"""Render an FTS social poster (1080x1350 JPG) in the house grid style.

Usage:
  python3 tools/make_poster.py spec.json out.jpg

spec.json:
  {"photo": "assets/photos/card-villa.webp",      # any file in assets/photos
   "headline": ["Luxury", "Elevators"],           # 1-3 short lines
   "sub": ["Premium finishes for", "premium spaces."],
   "cta": "Get quote now",                        # optional, default Get quote now
   "dark": false,                                 # navy overlay + reverse logo
   "top": 360}                                    # optional headline baseline

Contact details are fixed: WhatsApp +971 50 528 4597, www.getfixable.com.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, BAR = 1080, 1350, 110
NAVY, GOLD = (15, 31, 61), (201, 162, 74)
PHONE = "+971 50 528 4597"
SITE = "www.getfixable.com"


def font(name, size):
    for p in (os.path.join(ROOT, "assets/fonts", name), f"/usr/share/fonts/truetype/liberation/{name}"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render(spec, out):
    dark = bool(spec.get("dark"))
    img = Image.new("RGB", (W, H), "white")
    ph = Image.open(os.path.join(ROOT, spec["photo"])).convert("RGB")
    area_h = H - BAR
    sc = max(W / ph.width, area_h / ph.height)
    ph = ph.resize((int(ph.width * sc + 1), int(ph.height * sc + 1)), Image.LANCZOS)
    img.paste(ph, (W - ph.width, (area_h - ph.height) // 2))

    # left-to-right fade so text sits on a clean background
    base = NAVY if dark else (255, 255, 255)
    ov = Image.new("RGBA", (W, area_h), base + (0,))
    stops = [(0, .96), (380, .88), (593, .35), (760, 0)]
    px = ov.load()
    for x in range(760):
        for (x0, a0), (x1, a1) in zip(stops, stops[1:]):
            if x0 <= x <= x1:
                a = a0 + (a1 - a0) * (x - x0) / (x1 - x0)
                break
        col = base + (int(a * 255),)
        for y in range(area_h):
            px[x, y] = col
    img.paste(ov, (0, 0), ov)

    d = ImageDraw.Draw(img)
    logo = Image.open(os.path.join(ROOT, "assets/logo", "fts-logo-reverse.png" if dark else "fts-logo-color.png"))
    lw = 300 if dark else 410
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.paste(logo, (56, 56), logo)

    head = spec["headline"]
    hs = 84
    f = font("LiberationSerif-Bold.ttf", hs)
    widest = max(d.textlength(l, font=f) for l in head)
    if widest > 590:
        hs = int(84 * 590 / widest)
        f = font("LiberationSerif-Bold.ttf", hs)
    y = spec.get("top", 360)
    for l in head:
        d.text((60, y), l, font=f, fill="white" if dark else NAVY, anchor="ls")
        y += int(hs * 1.12)
    d.rectangle([62, y - 46, 182, y - 41], fill=GOLD)
    y += 24
    fs = font("LiberationSans-Regular.ttf", 34)
    for l in spec.get("sub", []):
        d.text((62, y), l, font=fs, fill=(232, 237, 245) if dark else (43, 47, 54), anchor="ls")
        y += 46
    y += 34
    fb = font("LiberationSans-Bold.ttf", 27)
    t = spec.get("cta", "Get quote now").upper() + "  →"
    bw = d.textlength(t, font=fb) + 80
    d.rounded_rectangle([60, y, 60 + bw, y + 72], radius=36, fill="white" if dark else NAVY, outline=GOLD, width=3)
    d.text((100, y + 46), t, font=fb, fill=NAVY if dark else "white", anchor="ls")

    # contact bar
    d.rectangle([0, H - BAR, W, H], fill=NAVY)
    d.rectangle([0, H - BAR - 4, W, H - BAR], fill=GOLD)
    cy = H - 55
    d.ellipse([62, cy - 30, 122, cy + 30], fill=(37, 211, 102))
    d.arc([75, cy - 17, 109, cy + 17], 135, 425, fill="white", width=4)
    d.polygon([(80, cy + 14), (76, cy + 22), (85, cy + 18)], fill="white")
    d.text((138, cy + 13), PHONE, font=font("LiberationSans-Bold.ttf", 38), fill="white", anchor="ls")
    d.rectangle([548, cy - 30, 551, cy + 30], fill=GOLD)
    d.ellipse([586, cy - 26, 638, cy + 26], outline=GOLD, width=4)
    d.ellipse([601, cy - 26, 623, cy + 26], outline=GOLD, width=3)
    d.line([586, cy, 638, cy], fill=GOLD, width=3)
    d.line([590, cy - 13, 634, cy - 13], fill=GOLD, width=3)
    d.line([590, cy + 13, 634, cy + 13], fill=GOLD, width=3)
    d.text((656, cy + 12), SITE, font=font("LiberationSans-Bold.ttf", 36), fill="white", anchor="ls")
    img.save(out, "JPEG", quality=92)


if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
