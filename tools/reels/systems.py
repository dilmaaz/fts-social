"""FTS original reel: 'Inside every FTS lift' — traction, doors, electrical, cabin, spare parts.
Run from tools/reels:  python3 systems.py [frames]
"""
import os, sys, math
from PIL import Image, ImageDraw
from common import *

INTRO = 3.0
SCN = 4.5
SCENES = 5
END = INTRO + SCN * SCENES          # 25.5
DUR = END + 3.6                     # 29.1


def scene_alpha(t, s0, dur):
    return prog(t, s0, 0.45) * (1 - prog(t, s0 + dur - 0.45, 0.45))


def scene_title(d, t, s0, num, txt, a):
    k = prog(t, s0, 0.5)
    y = 300 - 25 * (1 - k)
    text_c(d, y, f'0{num}', F(40), GOLD, a)
    text_c(d, y + 55, txt, F(84, 'serif'), WHITE, a)
    d.line([(W / 2 - 140 * a, y + 165), (W / 2 + 140 * a, y + 165)], fill=mix(NAVY, GOLD, a), width=5)


def label(d, t, start, x, y, txt, a, col=WHITE, size=42, anchor_dot=None):
    k = prog(t, start, 0.4) * a
    if k <= 0:
        return
    if anchor_dot:
        ax, ay = anchor_dot
        d.line([(ax, ay), (x - 14, y + size // 2)], fill=mix(NAVY, GOLD, k), width=3)
        d.ellipse([ax - 8, ay - 8, ax + 8, ay + 8], fill=mix(NAVY, GOLD, k))
    d.text((x + 20 * (1 - k), y), txt, font=F(size), fill=mix(NAVY, col, k))


def bullets(d, t, start, items, a, y0=1500):
    for i, s in enumerate(items):
        k = prog(t, start + i * 0.45, 0.4) * a
        if k <= 0:
            continue
        y = y0 + i * 92
        d.ellipse([150, y + 16, 170, y + 36], fill=mix(NAVY, GOLD, k))
        d.text((195 + 25 * (1 - k), y), s, font=F(46), fill=mix(NAVY, WHITE, k))


# ---------- intro ----------
def intro(img, d, t):
    a = 1 - prog(t, INTRO - 0.45, 0.45)
    k = prog(t, 0.2, 0.6) * a
    text_c(d, 640 - 30 * (1 - k), 'Inside every', F(70, 'sans'), GREY, k)
    text_c(d, 730 - 30 * (1 - k), 'FTS lift', F(130, 'serif'), WHITE, k)
    k2 = prog(t, 0.8, 0.6) * a
    d.line([(W / 2 - 200 * k2, 900), (W / 2 + 200 * k2, 900)], fill=mix(NAVY, GOLD, k2), width=6)
    text_c(d, 940, '5 systems. One team.', F(54), GOLD, k2)
    names = ['Traction', 'Doors', 'Electrical', 'Cabin', 'Spare parts']
    for i, n in enumerate(names):
        k3 = prog(t, 1.2 + i * 0.18, 0.4) * a
        text_c(d, 1080 + i * 80, n, F(46, 'sans'), WHITE, k3)


# ---------- 1 traction ----------
def traction(img, d, t, s0, a):
    lt = t - s0
    scene_title(d, t, s0, 1, 'Traction System', a)
    c = lambda col, k=1.0: mix(NAVY, col, a * k)
    sx0, sx1, top, bot = 150, 570, 560, 1420
    d.rectangle([sx0, top, sx1, bot], outline=c(GREY, 0.7), width=4)
    # machine
    mx, my = 360, top + 70
    d.rounded_rectangle([mx - 120, my - 50, mx + 120, my + 40], radius=12, fill=c(NAVY2), outline=c(WHITE), width=4)
    r = 46
    d.ellipse([mx - r, my - r + 10, mx + r, my + r + 10], outline=c(GOLD), width=6)
    ang = lt * 3.0
    for k in range(4):
        aa = ang + k * math.pi / 2
        d.line([(mx, my + 10), (mx + r * math.cos(aa), my + 10 + r * math.sin(aa))], fill=c(GOLD), width=4)
    # car / counterweight positions (opposite motion)
    u = 0.5 - 0.5 * math.cos(lt * 1.3)
    car_y = 900 + 300 * u
    cw_y = 1150 - 300 * u
    carx0, carx1 = 180, 380
    d.line([(mx - r + 6, my + 10), (carx0 + 100, car_y)], fill=c(GREY), width=4)
    d.line([(mx + r - 6, my + 10), (500, cw_y)], fill=c(GREY), width=4)
    d.rounded_rectangle([carx0, car_y, carx1, car_y + 230], radius=8, fill=c(NAVY2), outline=c(WHITE), width=4)
    d.line([(carx0 + 100, car_y + 15), (carx0 + 100, car_y + 215)], fill=c(GREY), width=3)
    d.rectangle([460, cw_y, 540, cw_y + 160], fill=c(GOLD, 0.85))
    for k in range(1, 4):
        d.line([(460, cw_y + k * 40), (540, cw_y + k * 40)], fill=c(NAVY), width=3)
    label(d, t, s0 + 0.8, 630, my - 30, 'Gearless machine', a, anchor_dot=(mx + 120, my))
    label(d, t, s0 + 1.2, 630, 800, 'Steel ropes', a, anchor_dot=(mx + r + 20, 760))
    label(d, t, s0 + 1.6, 630, 1230, 'Counterweight', a, anchor_dot=(540, cw_y + 80))
    bullets(d, t, s0 + 2.0, ['Smooth, efficient ride', 'Machine-room or MRL designs'], a)


# ---------- 2 doors ----------
def doors(img, d, t, s0, a):
    lt = t - s0
    scene_title(d, t, s0, 2, 'Door System', a)
    c = lambda col, k=1.0: mix(NAVY, col, a * k)
    fx0, fx1, fy0, fy1 = 170, 670, 720, 1420
    d.rectangle([fx0 - 30, fy0 - 30, fx1 + 30, fy1], fill=c(NAVY2), outline=c(WHITE), width=5)
    # cabin interior glimpse
    d.rectangle([fx0, fy0, fx1, fy1], fill=c(GOLD, 0.35))
    d.rectangle([fx0 + 60, fy0 + 40, fx1 - 60, fy0 + 70], fill=c(WHITE, 0.6))   # ceiling light
    # open / close cycle
    cyc = lt % 4.5
    op = ease(clamp((cyc - 0.6) / 0.9)) * (1 - ease(clamp((cyc - 2.9) / 0.9)))
    half = (fx1 - fx0) / 2
    gap = half * 0.92 * op
    mid = (fx0 + fx1) / 2
    for side in (-1, 1):
        inner = mid + side * gap
        outer = fx0 if side < 0 else fx1
        x0, x1 = sorted([inner, outer])
        if x1 - x0 > 2:
            d.rectangle([x0, fy0, x1, fy1], fill=c(GREY, 0.9), outline=c(WHITE), width=3)
            d.line([(x0 + 10, fy0 + 10), (x0 + 10, fy1 - 10)], fill=c(WHITE, 0.4), width=2)
    # light curtain beams
    blink = 0.6 + 0.4 * math.sin(lt * 10)
    if op > 0.3:
        for i in range(9):
            yy = fy0 + 80 + i * 75
            for x in range(int(fx0 + 6), int(fx1 - 6), 28):
                d.line([(x, yy), (x + 14, yy)], fill=c(RED, (0.6 + 0.4 * blink) * op), width=4)
    # operator on top
    d.rounded_rectangle([fx0 + 80, fy0 - 90, fx1 - 80, fy0 - 45], radius=8, fill=c(GOLD), outline=c(WHITE), width=3)
    label(d, t, s0 + 0.8, 700, fy0 - 95, 'Door operator', a, size=40)
    label(d, t, s0 + 1.4, 720, 1060, 'Light curtain', a, anchor_dot=(fx1, 1060))
    bullets(d, t, s0 + 2.0, ['Quiet, smooth opening', 'Stops doors closing on people'], a, y0=1530)


# ---------- 3 electrical ----------
def electrical(img, d, t, s0, a):
    lt = t - s0
    scene_title(d, t, s0, 3, 'Electrical System', a)
    c = lambda col, k=1.0: mix(NAVY, col, a * k)
    # control cabinet
    x0, y0, x1, y1 = 170, 600, 540, 1300
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=c(NAVY2), outline=c(WHITE), width=5)
    d.rectangle([x0 + 30, y0 + 40, x1 - 30, y0 + 200], outline=c(GREY), width=3)
    for i in range(6):
        on = (int(lt * 6) + i) % 3 == 0
        cx = x0 + 70 + i * 45
        d.ellipse([cx - 12, y0 + 100, cx + 12, y0 + 124], fill=c(GREEN if on else GREY, 1 if on else 0.5))
    d.text((x0 + 40, y0 + 230), 'CPU', font=F(44), fill=c(WHITE))
    # VVVF bar
    lvl = 0.35 + 0.6 * (0.5 + 0.5 * math.sin(lt * 2.4))
    d.rounded_rectangle([x0 + 30, y0 + 320, x1 - 30, y0 + 380], radius=10, outline=c(GREEN), width=4)
    d.rounded_rectangle([x0 + 38, y0 + 328, x0 + 38 + (x1 - x0 - 76) * lvl, y0 + 372], radius=8, fill=c(GREEN))
    d.text((x0 + 40, y0 + 400), 'VVVF', font=F(44), fill=c(GREEN))
    for i in range(4):
        d.rectangle([x0 + 40 + i * 80, y0 + 500, x0 + 90 + i * 80, y0 + 620], outline=c(GREY), width=3)
    # wires to COP
    px0, py0, px1, py1 = 700, 700, 860, 1180
    for i, col in enumerate([BLUE, GOLD, GREEN]):
        yy = y0 + 250 + i * 40
        d.line([(x1, yy), (620, yy), (620, py0 + 120 + i * 40), (px0, py0 + 120 + i * 40)], fill=c(col, 0.8), width=4)
        # travelling pulse
        p = (lt * 0.6 + i * 0.3) % 1
        xx = x1 + (px0 - x1) * p
        d.ellipse([xx - 8, (yy if xx < 620 else py0 + 120 + i * 40) - 8, xx + 8, (yy if xx < 620 else py0 + 120 + i * 40) + 8], fill=c(WHITE))
    d.rounded_rectangle([px0, py0, px1, py1], radius=16, fill=c(GREY, 0.35), outline=c(WHITE), width=4)
    d.rectangle([px0 + 25, py0 + 30, px1 - 25, py0 + 90], fill=c(BLUE, 0.7))
    for i in range(5):
        cy = py0 + 150 + i * 62
        lit = int(lt * 2) % 5 == i
        d.ellipse([px0 + 55, cy, px0 + 105, cy + 50], outline=c(GOLD if lit else WHITE), width=4, fill=c(GOLD, 0.6) if lit else None)
    label(d, t, s0 + 0.8, 560, 560, 'Controller', a, size=40)
    label(d, t, s0 + 1.2, 690, 1200, 'COP panel', a, size=40)
    bullets(d, t, s0 + 1.8, ['Microprocessor control + VVVF', 'Energy-efficient, accurate levelling'], a)


# ---------- 4 cabin ----------
FINISHES = [('Stainless steel', (170, 178, 190)), ('Champagne gold', (201, 162, 74)),
            ('Warm wood', (139, 94, 60)), ('Glass', (120, 190, 215))]

def cabin(img, d, t, s0, a):
    lt = t - s0
    scene_title(d, t, s0, 4, 'Custom Cabin', a)
    c = lambda col, k=1.0: mix(NAVY, col, a * k)
    idx = min(int(lt / 1.05), 3)
    fr = clamp((lt - idx * 1.05) / 0.35)
    prev = FINISHES[max(idx - 1, 0)][1]
    cur = mix(prev, FINISHES[idx][1], fr if idx > 0 else 1)
    # perspective cabin
    bx0, by0, bx1, by1 = 260, 620, 820, 1340   # front opening
    ix0, iy0, ix1, iy1 = 380, 720, 700, 1220   # back wall
    wall = mix(NAVY, cur, a)
    side = mix(NAVY, mix(cur, NAVY, 0.25), a)
    d.polygon([(bx0, by0), (ix0, iy0), (ix0, iy1), (bx0, by1)], fill=side)
    d.polygon([(bx1, by0), (ix1, iy0), (ix1, iy1), (bx1, by1)], fill=side)
    d.rectangle([ix0, iy0, ix1, iy1], fill=wall)
    d.polygon([(bx0, by0), (bx1, by0), (ix1, iy0), (ix0, iy0)], fill=c(NAVY2))
    d.polygon([(bx0, by1), (bx1, by1), (ix1, iy1), (ix0, iy1)], fill=c(GREY, 0.45))
    # LED ceiling
    glow = 0.7 + 0.3 * math.sin(lt * 3)
    d.polygon([(bx0 + 90, by0 + 20), (bx1 - 90, by0 + 20), (ix1 - 30, iy0 - 10), (ix0 + 30, iy0 - 10)], fill=c(WHITE, 0.55 * glow))
    # panels on back wall + handrail
    for k in range(1, 3):
        xx = ix0 + k * (ix1 - ix0) / 3
        d.line([(xx, iy0 + 10), (xx, iy1 - 10)], fill=mix(NAVY, mix(cur, WHITE, 0.4), a), width=3)
    d.line([(ix0 + 10, iy0 + 300), (ix1 - 10, iy0 + 300)], fill=c(WHITE, 0.8), width=6)
    d.rectangle([bx0 - 20, by0 - 20, bx1 + 20, by1], outline=c(WHITE), width=6)
    name = FINISHES[idx][0]
    text_c(d, 1385, name, F(52), GOLD, a)
    bullets(d, t, s0 + 1.0, ['Walls, ceiling, floor & handrails', 'Matched to your interior'], a, y0=1520)


# ---------- 5 spare parts ----------
def ico_cabinet(d, x, y, c):
    d.rounded_rectangle([x - 40, y - 60, x + 40, y + 60], radius=6, outline=c, width=4)
    d.line([(x - 25, y - 30), (x + 25, y - 30)], fill=c, width=3)
    d.line([(x - 25, y), (x + 25, y)], fill=c, width=3)

def ico_governor(d, x, y, c):
    d.ellipse([x - 45, y - 45, x + 45, y + 45], outline=c, width=5)
    d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=c)
    d.line([(x, y + 45), (x, y + 70)], fill=c, width=4)

def ico_buttons(d, x, y, c):
    d.rounded_rectangle([x - 30, y - 60, x + 30, y + 60], radius=10, outline=c, width=4)
    for k in range(3):
        d.ellipse([x - 12, y - 42 + k * 32, x + 12, y - 18 + k * 32], outline=c, width=3)

def ico_door(d, x, y, c):
    d.rectangle([x - 50, y - 55, x + 50, y + 55], outline=c, width=4)
    d.line([(x, y - 55), (x, y + 55)], fill=c, width=4)
    d.rectangle([x - 50, y - 75, x + 50, y - 60], fill=c)

def ico_sensor(d, x, y, c):
    d.polygon([(x - 45, y - 30), (x + 45, y - 30), (x + 45, y + 30), (x + 15, y + 30), (x + 15, y - 5), (x - 15, y - 5), (x - 15, y + 30), (x - 45, y + 30)], outline=c, fill=None)
    d.line([(x - 45, y - 30), (x + 45, y - 30)], fill=c, width=4)

def ico_sheave(d, x, y, c):
    d.ellipse([x - 50, y - 50, x + 50, y + 50], outline=c, width=5)
    d.ellipse([x - 30, y - 30, x + 30, y + 30], outline=c, width=3)
    d.line([(x - 50, y), (x - 50, y + 70)], fill=c, width=3)
    d.line([(x + 50, y), (x + 50, y + 70)], fill=c, width=3)

PARTS = [('Control cabinet', ico_cabinet), ('Governor', ico_governor), ('COP / HOP', ico_buttons),
         ('Door operator', ico_door), ('Levelling sensor', ico_sensor), ('Ropes & sheaves', ico_sheave)]

def parts(img, d, t, s0, a):
    scene_title(d, t, s0, 5, 'Spare Parts', a)
    for i, (name, fn) in enumerate(PARTS):
        k = prog(t, s0 + 0.5 + i * 0.25, 0.4) * a
        if k <= 0:
            continue
        col, row = i % 2, i // 2
        cx = 300 + col * 480
        cy = 680 + row * 280
        d.rounded_rectangle([cx - 200, cy - 110, cx + 200, cy + 150], radius=22, fill=mix(NAVY, NAVY2, k), outline=mix(NAVY, GOLD, k * 0.8), width=3)
        fn(d, cx, cy - 10 + 15 * (1 - k), mix(NAVY, WHITE, k))
        tw = d.textlength(name, font=F(38))
        d.text((cx - tw / 2, cy + 90), name, font=F(38), fill=mix(NAVY, GOLD, k))
    k = prog(t, s0 + 2.3, 0.5) * a
    text_c(d, 1530, 'For all major lift brands', F(54), WHITE, k)
    text_c(d, 1610, 'Supply · Repair · Modernization', F(44, 'sans'), GOLD, k)


SCENE_FNS = [traction, doors, electrical, cabin, parts]

def draw(img, t):
    d = ImageDraw.Draw(img)
    if t >= END:
        end_card(img, t - END)
        return
    hdr = 1 - prog(t, END - 0.4, 0.4)
    header(img, hdr)
    if t < INTRO:
        intro(img, d, t)
        return
    i = min(int((t - INTRO) / SCN), SCENES - 1)
    s0 = INTRO + i * SCN
    SCENE_FNS[i](img, d, t, s0, scene_alpha(t, s0, SCN))


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
    if mode == 'frames':
        for tt in [1.8, 5.5, 9.6, 14.5, 19.0, 21.4, 24.0, 28.0]:
            img = background(); draw(img, tt); img.save(f'/tmp/sys_{tt}.png')
    else:
        tmp = '/tmp/fts-reels'; os.makedirs(tmp, exist_ok=True)
        out = os.path.join(REPO, 'reels'); os.makedirs(out, exist_ok=True)
        render(f'{tmp}/systems_v.mp4', DUR, draw)
        music(f'{tmp}/systems.wav', DUR, seed=2)
        mux(f'{tmp}/systems_v.mp4', f'{tmp}/systems.wav', f'{out}/FTS-reel-systems.mp4')
        print('done')
