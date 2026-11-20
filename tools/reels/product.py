"""FTS original reel, light 'product showcase' style: isometric lift drawings on a light background.
Scenes: intro, traction, doors, electrical, cabin, spare parts, end card.
Run from tools/reels:  python3 product.py [frames]
"""
import os, sys, math
from PIL import Image, ImageDraw, ImageFont
from common import (W, H, FPS, NAVY, GOLD, BLUE, GREEN, RED, REPO, clamp, ease, prog, mix,
                    Encoder, music, mux)

BG1, BG2 = (246, 247, 249), (226, 229, 234)
INK = (52, 58, 70)          # caption text
STEEL = (150, 156, 166)
STEEL_D = (96, 102, 112)
STEEL_L = (205, 209, 216)
DARKBLUE = (38, 56, 104)
YELLOW = (222, 184, 46)

FONTS = REPO + '/assets/fonts/'
_fc = {}
def P(size, w='Light'):
    k = (size, w)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FONTS + f'Poppins-{w}.ttf', size)
    return _fc[k]

LOGO = Image.open(REPO + '/assets/logo/fts-logo-color.png').convert('RGBA')

INTRO, SCN, N = 4.0, 4.5, 5
END = INTRO + SCN * N          # 26.5
DUR = END + 3.5                # 30.0

_bg = None
def background():
    global _bg
    if _bg is None:
        im = Image.new('RGB', (W, H), BG1)
        d = ImageDraw.Draw(im)
        for y in range(H):
            k = (y / H) ** 1.6
            d.line([(0, y), (W, y)], fill=mix(BG1, BG2, k * 0.8))
        # soft floor shadow band
        _bg = im
    return _bg.copy()

def blend(c, a):
    """fade colour c towards background by alpha a"""
    return mix(BG1, c, a)

# ---------- isometric helpers ----------
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
class Iso:
    def __init__(self, cx, cy, s):
        self.cx, self.cy, self.s = cx, cy, s
    def p(self, x, y, z):
        return (self.cx + (x - y) * C30 * self.s, self.cy + (x + y) * S30 * self.s - z * self.s)

def box(d, iso, x, y, z, dx, dy, dz, col, a=1.0, outline=None):
    P_ = iso.p
    top = [P_(x, y, z + dz), P_(x + dx, y, z + dz), P_(x + dx, y + dy, z + dz), P_(x, y + dy, z + dz)]
    left = [P_(x, y + dy, z), P_(x + dx, y + dy, z), P_(x + dx, y + dy, z + dz), P_(x, y + dy, z + dz)]
    right = [P_(x + dx, y, z), P_(x + dx, y + dy, z), P_(x + dx, y + dy, z + dz), P_(x + dx, y, z + dz)]
    oc = blend(outline, a) if outline else None
    d.polygon(left, fill=blend(mix(col, (0, 0, 0), 0.18), a), outline=oc)
    d.polygon(right, fill=blend(mix(col, (0, 0, 0), 0.32), a), outline=oc)
    d.polygon(top, fill=blend(mix(col, (255, 255, 255), 0.15), a), outline=oc)

def bar(d, iso, p1, p2, col, w, a=1.0):
    d.line([iso.p(*p1), iso.p(*p2)], fill=blend(col, a), width=w)

def shaft_frame(d, iso, wx, wy, hz, a, levels=5, rail=True):
    # 4 posts
    for (x, y) in [(0, 0), (wx, 0), (0, wy), (wx, wy)]:
        bar(d, iso, (x, y, 0), (x, y, hz), STEEL_D, 7, a)
    # horizontal rings
    for k in range(levels + 1):
        z = hz * k / levels
        for p1, p2 in [((0, 0), (wx, 0)), ((wx, 0), (wx, wy)), ((wx, wy), (0, wy)), ((0, wy), (0, 0))]:
            bar(d, iso, (*p1, z), (*p2, z), STEEL, 4, a)
    if rail:
        # guide rails (front-left side)
        bar(d, iso, (wx * 0.5 - 6, wy, 0), (wx * 0.5 - 6, wy, hz), STEEL_D, 5, a)

def handrail(d, iso, wx, wy, hz, a):
    h = 34
    for p1, p2 in [((0, 0), (wx, 0)), ((wx, 0), (wx, wy)), ((0, 0), (0, wy))]:
        bar(d, iso, (*p1, hz + h), (*p2, hz + h), YELLOW, 6, a)
        bar(d, iso, (*p1, hz + h / 2), (*p2, hz + h / 2), YELLOW, 4, a)
    for (x, y) in [(0, 0), (wx, 0), (wx, wy), (0, wy), (wx / 2, 0), (wx, wy / 2), (0, wy / 2)]:
        bar(d, iso, (x, y, hz), (x, y, hz + h), YELLOW, 5, a)

def machine(d, iso, x, y, z, a, ang):
    box(d, iso, x, y, z, 70, 60, 34, DARKBLUE, a, outline=None)
    # sheave on the front (y = y+60) face as an ellipse
    cx, cy = iso.p(x + 35, y + 60, z + 17)
    r = 26 * iso.s / 1.0
    d.ellipse([cx - r * 0.9, cy - r, cx + r * 0.9, cy + r], fill=blend(STEEL_L, a), outline=blend(STEEL_D, a), width=3)
    for k in range(3):
        aa = ang + k * 2 * math.pi / 3
        d.line([(cx, cy), (cx + r * 0.8 * math.cos(aa), cy + r * 0.9 * math.sin(aa))], fill=blend(STEEL_D, a), width=3)
    return (cx, cy, r)

def car(d, iso, x, y, z, dx, dy, dz, a):
    box(d, iso, x, y, z, dx, dy, dz, (196, 200, 207), a, outline=blend(STEEL_D, a))
    # door split line on front (y+dy) face
    p1, p2 = iso.p(x + dx / 2, y + dy, z + 4), iso.p(x + dx / 2, y + dy, z + dz - 6)
    d.line([p1, p2], fill=blend(STEEL_D, a), width=3)
    # car frame (sling)
    bar(d, iso, (x - 4, y + dy / 2, z - 6), (x - 4, y + dy / 2, z + dz + 10), STEEL_D, 5, a)
    bar(d, iso, (x + dx + 4, y + dy / 2, z - 6), (x + dx + 4, y + dy / 2, z + dz + 10), STEEL_D, 5, a)
    bar(d, iso, (x - 4, y + dy / 2, z + dz + 10), (x + dx + 4, y + dy / 2, z + dz + 10), STEEL_D, 6, a)

# ---------- text ----------
def caption(d, t, start, x, y, lines, a, size=64, col=INK, spacing=8):
    k = prog(t, start, 0.6) * a
    if k <= 0:
        return
    f = P(size)
    for i, ln in enumerate(lines):
        d.text((x + 30 * (1 - k), y + i * (size + spacing)), ln, font=f, fill=blend(col, k))

def ctext(d, y, s, font, col, a):
    tw = d.textlength(s, font=font)
    d.text(((W - tw) / 2, y), s, font=font, fill=blend(col, a))

def logo_corner(img, a):
    lg = LOGO.copy()
    lg.thumbnail((330, 60))
    if a < 1:
        lg.putalpha(lg.split()[3].point(lambda v: int(v * a)))
    img.paste(lg, (W - lg.width - 60, 80), lg)

def scene_a(t, s0, dur):
    return prog(t, s0, 0.5) * (1 - prog(t, s0 + dur - 0.5, 0.5))

# ---------- scenes ----------
def full_lift(d, t, a, cx=640, cy=1480, s=2.2, car_z=None):
    iso = Iso(cx, cy, s)
    wx, wy, hz = 140, 120, 330
    shaft_frame(d, iso, wx, wy, hz, a)
    # counterweight at back
    u = 0.5 - 0.5 * math.cos(t * 0.9)
    cz = car_z if car_z is not None else 30 + 190 * u
    cwz = 230 - 190 * u
    box(d, iso, wx - 30, 8, cwz, 22, 14, 70, (120, 126, 136), a)
    car(d, iso, 22, 22, cz, 92, 84, 100, a)
    # ropes from machine
    mx, my, mz = 35, 25, hz
    sx, sy, r = machine(d, iso, mx, my, mz, a, t * 2.4)
    d.line([(sx, sy), iso.p(68, 64, cz + 110)], fill=blend(STEEL_D, a), width=2)
    handrail(d, iso, wx, wy, hz, a)
    return iso

def intro(img, d, t):
    a = 1 - prog(t, INTRO - 0.5, 0.5)
    full_lift(d, t, prog(t, 0.1, 0.8) * a)
    caption(d, t, 0.5, 70, 300, ['Choose', 'FTS'], a, size=76)
    caption(d, t, 1.0, 600, 470, ['Elevator', 'specialists'], a, size=60)
    caption(d, t, 1.6, 70, 1050, ['Supply'], a, size=56)
    caption(d, t, 1.9, 70, 1130, ['Install'], a, size=56)
    caption(d, t, 2.2, 70, 1210, ['Maintain'], a, size=56)

def traction(img, d, t, s0, a):
    lt = t - s0
    iso = Iso(540, 1060, 4.2)
    # zoomed top of shaft
    wx, wy = 140, 120
    for (x, y) in [(0, 0), (wx, 0), (0, wy), (wx, wy)]:
        bar(d, iso, (x, y, -15), (x, y, 60), STEEL_D, 9, a)
    for p1, p2 in [((0, 0), (wx, 0)), ((wx, 0), (wx, wy)), ((wx, wy), (0, wy)), ((0, wy), (0, 0))]:
        bar(d, iso, (*p1, 0), (*p2, 0), STEEL, 6, a)
    box(d, iso, 20, 20, 0, 100, 8, 6, STEEL_D, a)        # machine base beam
    sx, sy, r = machine(d, iso, 35, 25, 6, a, lt * 3)
    # ropes going down
    for k in range(4):
        d.line([(sx - r * 0.6 + k * r * 0.4, sy + r * 0.6), (sx - r * 0.6 + k * r * 0.4, 1480)], fill=blend(STEEL_D, a), width=3)
    handrail(d, iso, wx, wy, 6, a)
    caption(d, t, s0 + 0.4, 80, 360, ['Traction', 'System'], a, size=72)
    caption(d, t, s0 + 1.2, 80, 1640, ['Gearless machine · steel ropes', 'smooth, efficient ride'], a, size=40, col=STEEL_D)

def doors(img, d, t, s0, a):
    lt = t - s0
    # front elevation of landing door, light style
    x0, x1, y0, y1 = 300, 780, 720, 1440
    d.rectangle([x0 - 40, y0 - 40, x1 + 40, y1], fill=blend((214, 218, 224), a), outline=blend(STEEL_D, a), width=4)
    d.rectangle([x0, y0, x1, y1], fill=blend((190, 168, 120), a))  # warm cabin interior
    d.rectangle([x0 + 50, y0 + 30, x1 - 50, y0 + 55], fill=blend((255, 250, 235), a))
    cyc = lt % 4.5
    op = ease(clamp((cyc - 0.7) / 1.0)) * (1 - ease(clamp((cyc - 3.0) / 0.9)))
    mid, half = (x0 + x1) / 2, (x1 - x0) / 2
    gap = half * 0.92 * op
    for side in (-1, 1):
        inner = mid + side * gap
        outer = x0 if side < 0 else x1
        a0, a1 = sorted([inner, outer])
        if a1 - a0 > 2:
            d.rectangle([a0, y0, a1, y1], fill=blend((206, 210, 217), a), outline=blend(STEEL_D, a), width=2)
            d.line([(a0 + 8, y0 + 8), (a0 + 8, y1 - 8)], fill=blend((240, 242, 246), a), width=3)
    if op > 0.3:
        for i in range(10):
            yy = y0 + 70 + i * 68
            d.line([(x0 + 4, yy), (x1 - 4, yy)], fill=blend(RED, 0.45 * op * a), width=2)
    # header / operator
    d.rectangle([x0 - 40, y0 - 110, x1 + 40, y0 - 50], fill=blend(DARKBLUE, a))
    caption(d, t, s0 + 0.4, 80, 360, ['Door', 'System'], a, size=72)
    caption(d, t, s0 + 1.2, 80, 1560, ['Quiet door operator', 'light-curtain safety'], a, size=40, col=STEEL_D)

def electrical(img, d, t, s0, a):
    lt = t - s0
    iso = Iso(460, 1330, 4.4)
    box(d, iso, 0, 0, 0, 60, 34, 150, (214, 218, 224), a, outline=blend(STEEL_D, a))   # cabinet
    # front panel details on y=34 face
    for i in range(5):
        on = (int(lt * 5) + i) % 3 == 0
        cx, cy = iso.p(10 + i * 10, 34, 130)
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=blend(GREEN if on else STEEL, a))
    for k in range(3):
        p1, p2 = iso.p(8, 34, 100 - k * 30), iso.p(52, 34, 100 - k * 30)
        d.line([p1, p2], fill=blend(STEEL_D, a), width=3)
    # COP panel
    px, py = 820, 760
    d.rounded_rectangle([px, py, px + 130, py + 460], radius=14, fill=blend((222, 225, 230), a), outline=blend(STEEL_D, a), width=3)
    d.rectangle([px + 20, py + 25, px + 110, py + 80], fill=blend(DARKBLUE, a))
    for i in range(5):
        cy = py + 120 + i * 62
        lit = int(lt * 2) % 5 == i
        d.ellipse([px + 40, cy, px + 90, cy + 50], outline=blend(STEEL_D, a), width=3, fill=blend(GOLD, a) if lit else None)
    # cable
    sx, sy = iso.p(60, 17, 120)
    d.line([(sx, sy), (px - 40, sy), (px - 40, py + 200), (px, py + 200)], fill=blend(DARKBLUE, a * 0.8), width=4)
    p = (lt * 0.7) % 1
    xx = sx + (px - 40 - sx) * p
    d.ellipse([xx - 7, sy - 7, xx + 7, sy + 7], fill=blend(GOLD, a))
    caption(d, t, s0 + 0.4, 80, 360, ['Electrical', 'System'], a, size=72)
    caption(d, t, s0 + 1.2, 80, 1560, ['Microprocessor control · VVVF', 'COP & landing buttons'], a, size=40, col=STEEL_D)

FIN = [('Stainless steel', (178, 184, 194)), ('Champagne gold', (206, 172, 102)), ('Warm wood', (150, 108, 72)), ('Mirror glass', (150, 196, 214))]
def cabin(img, d, t, s0, a):
    lt = t - s0
    idx = min(int(lt / 1.05), 3)
    fr = clamp((lt - idx * 1.05) / 0.35)
    cur = mix(FIN[max(idx - 1, 0)][1], FIN[idx][1], fr if idx else 1)
    bx0, by0, bx1, by1 = 240, 640, 840, 1380
    ix0, iy0, ix1, iy1 = 380, 760, 700, 1250
    d.rectangle([bx0 - 30, by0 - 60, bx1 + 30, by1 + 10], fill=blend((206, 210, 217), a), outline=blend(STEEL_D, a), width=3)
    d.polygon([(bx0, by0), (ix0, iy0), (ix0, iy1), (bx0, by1)], fill=blend(mix(cur, (0, 0, 0), 0.15), a))
    d.polygon([(bx1, by0), (ix1, iy0), (ix1, iy1), (bx1, by1)], fill=blend(mix(cur, (0, 0, 0), 0.15), a))
    d.rectangle([ix0, iy0, ix1, iy1], fill=blend(cur, a))
    d.polygon([(bx0, by0), (bx1, by0), (ix1, iy0), (ix0, iy0)], fill=blend((236, 236, 232), a))
    d.polygon([(bx0 + 110, by0 + 25), (bx1 - 110, by0 + 25), (ix1 - 40, iy0 - 15), (ix0 + 40, iy0 - 15)], fill=blend((255, 252, 240), a))
    d.polygon([(bx0, by1), (bx1, by1), (ix1, iy1), (ix0, iy1)], fill=blend((120, 124, 132), a))
    for k in range(1, 3):
        xx = ix0 + k * (ix1 - ix0) / 3
        d.line([(xx, iy0 + 10), (xx, iy1 - 10)], fill=blend(mix(cur, (255, 255, 255), 0.35), a), width=3)
    d.line([(ix0 + 10, iy0 + 300), (ix1 - 10, iy0 + 300)], fill=blend((240, 240, 240), a), width=6)
    caption(d, t, s0 + 0.4, 80, 360, ['Custom Cabin', 'Design'], a, size=72)
    ctext(d, 1420, FIN[idx][0], P(48, 'Regular'), GOLD, a)
    caption(d, t, s0 + 1.2, 80, 1520, ['Walls, ceiling, floor & handrails', 'matched to your interior'], a, size=40, col=STEEL_D)

def parts(img, d, t, s0, a):
    lt = t - s0
    caption(d, t, s0 + 0.3, 80, 300, ['Modernization &', 'Spare Parts'], a, size=66)
    names = ['Control cabinet', 'Governor', 'COP / HOP', 'Door operator', 'Levelling sensor', 'Ropes & sheaves']
    for i, nm in enumerate(names):
        k = prog(t, s0 + 0.6 + i * 0.25, 0.4) * a
        if k <= 0:
            continue
        col, row = i % 2, i // 2
        cx, cy = 300 + col * 480, 700 + row * 300
        iso = Iso(cx, cy + 60, 2.6)
        c = (190, 194, 202)
        if i == 0:
            box(d, iso, -20, -12, 0, 40, 24, 60, c, k, outline=blend(STEEL_D, k))
        elif i == 1:
            box(d, iso, -22, -10, 0, 44, 20, 14, (40, 120, 90), k)
            d.ellipse([cx - 40, cy - 70, cx + 40, cy + 10], fill=blend(STEEL_L, k), outline=blend(STEEL_D, k), width=4)
        elif i == 2:
            for j in range(3):
                d.rounded_rectangle([cx - 80 + j * 60, cy - 70, cx - 40 + j * 60, cy + 50], radius=8, fill=blend((222, 225, 230), k), outline=blend(STEEL_D, k), width=3)
                d.ellipse([cx - 70 + j * 60, cy - 40, cx - 50 + j * 60, cy - 20], outline=blend(DARKBLUE, k), width=3)
        elif i == 3:
            d.rectangle([cx - 70, cy - 80, cx + 70, cy - 55], fill=blend(DARKBLUE, k))
            d.rectangle([cx - 66, cy - 50, cx - 4, cy + 50], fill=blend((206, 210, 217), k), outline=blend(STEEL_D, k), width=3)
            d.rectangle([cx + 4, cy - 50, cx + 66, cy + 50], fill=blend((206, 210, 217), k), outline=blend(STEEL_D, k), width=3)
        elif i == 4:
            box(d, iso, -20, -8, 0, 40, 16, 22, (232, 120, 40), k)
        else:
            d.ellipse([cx - 55, cy - 75, cx + 55, cy + 35], fill=blend(STEEL_L, k), outline=blend(STEEL_D, k), width=5)
            d.ellipse([cx - 25, cy - 45, cx + 25, cy + 5], outline=blend(STEEL_D, k), width=3)
        tw = d.textlength(nm, font=P(36, 'Regular'))
        d.text((cx - tw / 2, cy + 100), nm, font=P(36, 'Regular'), fill=blend(INK, k))
    k = prog(t, s0 + 2.3, 0.5) * a
    ctext(d, 1600, 'For all major lift brands', P(46, 'Regular'), GOLD, k)

def end_card(img, d, tl):
    a = prog(tl, 0, 0.6)
    lg = LOGO.copy()
    lg.thumbnail((800, 160))
    lg.putalpha(lg.split()[3].point(lambda v: int(v * a)))
    img.paste(lg, ((W - lg.width) // 2, int(640 - 30 * (1 - a))), lg)
    a2 = prog(tl, 0.4, 0.6)
    ctext(d, 860, 'Complete vertical transport solutions', P(42), INK, a2)
    a3 = prog(tl, 0.7, 0.5)
    pw, ph = 600, 116
    px, py = (W - pw) // 2, 1000
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=ph // 2, fill=blend(GOLD, a3))
    f = P(52, 'Medium')
    tw = d.textlength('GET QUOTE NOW', font=f)
    d.text(((W - tw) / 2, py + 26), 'GET QUOTE NOW', font=f, fill=blend((255, 255, 255), a3))
    a4 = prog(tl, 1.0, 0.5)
    ctext(d, 1190, 'WhatsApp +971 50 528 4597', P(56, 'Medium'), NAVY, a4)
    ctext(d, 1280, 'www.ftselevators.com', P(46, 'Regular'), GOLD, a4)
    ctext(d, 1390, 'Dubai · Sharjah · Ajman · all UAE', P(38), STEEL_D, a4)

SC = [traction, doors, electrical, cabin, parts]

def draw(img, t):
    d = ImageDraw.Draw(img)
    if t >= END:
        end_card(img, d, t - END)
        return
    logo_corner(img, 1 - prog(t, END - 0.4, 0.4))
    if t < INTRO:
        intro(img, d, t)
        return
    i = min(int((t - INTRO) / SCN), N - 1)
    s0 = INTRO + i * SCN
    SC[i](img, d, t, s0, scene_a(t, s0, SCN))

def render(path, dur):
    enc = Encoder(path)
    for n in range(int(dur * FPS)):
        t = n / FPS
        img = background()
        draw(img, t)
        if t < 0.3 or t > dur - 0.4:
            k = clamp(t / 0.3) if t < 0.3 else clamp((dur - t) / 0.4)
            img = Image.blend(Image.new('RGB', (W, H), BG1), img, k)
        enc.add(img)
    enc.close()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'frames':
        for tt in [2.6, 6.5, 10.5, 15.0, 20.5, 25.0, 29.0]:
            img = background(); draw(img, tt); img.save(f'/tmp/prd_{tt}.png')
    else:
        tmp = '/tmp/fts-reels'; os.makedirs(tmp, exist_ok=True)
        out = os.path.join(REPO, 'reels')
        render(f'{tmp}/product_v.mp4', DUR)
        music(f'{tmp}/product.wav', DUR, seed=3)
        mux(f'{tmp}/product_v.mp4', f'{tmp}/product.wav', f'{out}/FTS-reel-product.mp4')
        print('done')
