import os
import sys, math
from PIL import Image, ImageDraw
from common import *

DUR = 15.0
END = 12.0

def fade_content(t):
    return 1 - prog(t, END - 0.5, 0.5)

def title(d, t, l1, l2, a_mul):
    a = prog(t, 0.2, 0.6) * a_mul
    y = 330 - 30 * (1 - prog(t, 0.2, 0.6))
    text_c(d, y, l1, F(96, 'serif'), WHITE, a)
    d.line([(W / 2 - 160 * a, y + 125), (W / 2 + 160 * a, y + 125)], fill=mix(NAVY, GOLD, a), width=5)
    text_c(d, y + 150, l2, F(44, 'sans'), GREY, prog(t, 0.6, 0.6) * a_mul)

def step_row(d, t, start, y, num, txt, a_mul, x=150):
    a = prog(t, start, 0.45) * a_mul
    if a <= 0: return
    off = 40 * (1 - a)
    r = 42
    cx, cy = x + off, y + 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mix(NAVY, GOLD, a))
    f = F(46)
    tw = d.textlength(str(num), font=f)
    d.text((cx - tw / 2, cy - 27), str(num), font=f, fill=NAVY)
    d.text((cx + 70, cy - 28), txt, font=F(46), fill=mix(NAVY, WHITE, a))

def check_row(d, t, start, y, txt, a_mul, x=210):
    a = prog(t, start - 0.3, 0.4) * a_mul
    if a <= 0: return
    d.rounded_rectangle([x, y, x + 64, y + 64], radius=12, outline=mix(NAVY2, BLUE, a), width=5)
    k = prog(t, start, 0.35) * a_mul
    if k > 0:
        p1, p2, p3 = (x + 14, y + 34), (x + 28, y + 50), (x + 54, y + 16)
        if k < 0.5:
            q = k / 0.5
            pts = [p1, (p1[0] + (p2[0] - p1[0]) * q, p1[1] + (p2[1] - p1[1]) * q)]
        else:
            q = (k - 0.5) / 0.5
            pts = [p1, p2, (p2[0] + (p3[0] - p2[0]) * q, p2[1] + (p3[1] - p2[1]) * q)]
        d.line(pts, fill=GREEN, width=10, joint='curve')
    d.text((x + 95, y + 6), txt, font=F(44), fill=mix(NAVY, WHITE, a))

# ---------------- 1. Stuck in a lift ----------------
def v_stuck(img, t):
    d = ImageDraw.Draw(img)
    if t >= END:
        end_card(img, t - END); return
    m = fade_content(t)
    header(img, m)
    title(d, t, 'Stuck in a lift?', "Stay calm. Here's what to do.", m)
    # shaft + car
    a = prog(t, 0.5, 0.6) * m
    sx0, sx1, sy0, sy1 = 400, 680, 570, 1030
    d.rectangle([sx0, sy0, sx1, sy1], outline=mix(NAVY, GREY, a), width=6)
    for i in range(1, 4):
        yy = sy0 + i * (sy1 - sy0) / 4
        d.line([(sx0 - 30, yy), (sx0, yy)], fill=mix(NAVY, GREY, a * 0.6), width=4)
    shake = 6 * math.sin(t * 40) * (1 - prog(t, 1.2, 0.4)) if t > 0.6 else 0
    cx0, cy0 = sx0 + 30 + shake, 700
    d.rounded_rectangle([cx0, cy0, cx0 + 220, cy0 + 260], radius=10, fill=mix(NAVY, NAVY2, a), outline=mix(NAVY, WHITE, a), width=5)
    d.line([(cx0 + 110, cy0 + 20), (cx0 + 110, cy0 + 245)], fill=mix(NAVY, GREY, a), width=4)
    d.line([(cx0 + 110, sy0), (cx0 + 110, cy0)], fill=mix(NAVY, GREY, a), width=3)
    # alert badge
    pulse = 0.5 + 0.5 * math.sin(t * 6)
    bx, by = 760, 660
    r = 48 + 6 * pulse
    d.ellipse([bx - r, by - r, bx + r, by + r], fill=mix(NAVY, RED, a * (0.75 + 0.25 * pulse)))
    f = F(64); tw = d.textlength('!', font=f)
    d.text((bx - tw / 2, by - 38), '!', font=f, fill=mix(NAVY, WHITE, a))
    steps = ['Stay calm. The car holds safely', 'Press the alarm button', 'Use the intercom or call for help',
             "Don't force the doors open", 'Wait for trained technicians']
    for i, s in enumerate(steps):
        step_row(d, t, 2.2 + i * 1.5, 1100 + i * 130, i + 1, s, m, x=130)
    a5 = prog(t, 9.8, 0.5) * m
    text_c(d, 1780, 'FTS 24/7 repair & callouts', F(52), GOLD, a5)

# ---------------- 2. Villa lift ----------------
def v_villa(img, t):
    d = ImageDraw.Draw(img)
    if t >= END:
        end_card(img, t - END); return
    m = fade_content(t)
    header(img, m)
    title(d, t, 'A lift for your villa', 'Every floor, within easy reach', m)
    a = prog(t, 0.6, 0.7) * m
    x0, x1 = 170, 910
    floors = [1280, 1040, 800]  # floor lines (G, 1, 2) - y of floor surface
    top = 570
    lc = mix(NAVY, WHITE, a)
    # roof
    d.polygon([(x0 - 30, top + 40), ((x0 + x1) / 2, top - 60 + 20), (x1 + 30, top + 40)], outline=lc, fill=mix(NAVY, NAVY2, a))
    d.rectangle([x0, top + 40, x1, floors[0]], outline=lc, width=6)
    for fy in floors[1:]:
        d.line([(x0, fy), (x1, fy)], fill=lc, width=6)
    d.line([(x0 - 60, floors[0]), (x1 + 60, floors[0])], fill=lc, width=6)
    # furniture hints
    fc = mix(NAVY, GREY, a * 0.7)
    d.rounded_rectangle([x0 + 40, floors[0] - 70, x0 + 260, floors[0]], radius=14, outline=fc, width=4)   # sofa
    d.rectangle([x0 + 60, floors[1] - 90, x0 + 240, floors[1] - 40], outline=fc, width=4)               # bed
    d.rectangle([x0 + 70, floors[2] - 150, x0 + 130, floors[2]], outline=fc, width=4)                  # plant/shelf
    # glass shaft
    sx0, sx1 = 640, 820
    gl = mix(NAVY, BLUE, a)
    d.rectangle([sx0, top + 40, sx1, floors[0]], outline=gl, width=5)
    for k in range(1, 4):
        xx = sx0 + k * (sx1 - sx0) / 4
        d.line([(xx, top + 40), (xx, floors[0])], fill=mix(NAVY, BLUE, a * 0.35), width=2)
    # car motion G -> 1 -> 2
    def fy_at(t):
        if t < 2.6: return floors[0]
        if t < 3.6: return floors[0] + (floors[1] - floors[0]) * ease((t - 2.6) / 1.0)
        if t < 5.2: return floors[1]
        if t < 6.2: return floors[1] + (floors[2] - floors[1]) * ease((t - 5.2) / 1.0)
        return floors[2]
    cy = fy_at(t)
    ch = 200
    d.rounded_rectangle([sx0 + 14, cy - ch, sx1 - 14, cy - 6], radius=8, fill=mix(NAVY, GOLD, a), outline=mix(NAVY, WHITE, a), width=3)
    d.rectangle([sx0 + 40, cy - ch + 30, sx1 - 40, cy - 30], outline=mix(GOLD, WHITE, 0.5), width=3)
    # floor labels
    labels = ['G', '1', '2']
    for i, fy in enumerate(floors):
        on = abs(cy - fy) < 4
        col = GOLD if on else GREY
        f = F(44)
        d.text((sx1 + 30, fy - 70), labels[i], font=f, fill=mix(NAVY, col, a))
    items = ['Compact shaft, 260–400 kg', 'Cabin matched to your interior', 'Supply, install & maintain: one team']
    for i, s in enumerate(items):
        step_row(d, t, 6.6 + i * 1.3, 1370 + i * 130, i + 1, s, m, x=110)
    a5 = prog(t, 10.2, 0.5) * m
    text_c(d, 1790, 'Free site survey', F(52), GOLD, a5)

# ---------------- 3. AMC ----------------
def v_amc(img, t):
    d = ImageDraw.Draw(img)
    if t >= END:
        end_card(img, t - END); return
    m = fade_content(t)
    header(img, m)
    title(d, t, 'Why choose an AMC?', 'Preventive care for your lifts', m)
    a = prog(t, 0.6, 0.6) * m
    bx0, by0, bx1, by1 = 140, 620, 940, 1520
    d.rounded_rectangle([bx0, by0 + 30 * (1 - a), bx1, by1], radius=30, fill=mix(NAVY, NAVY2, a), outline=mix(NAVY, GREY, a * 0.5), width=3)
    d.rounded_rectangle([W / 2 - 120, by0 - 30, W / 2 + 120, by0 + 40], radius=18, fill=mix(NAVY, GOLD, a))
    text_c(d, by0 + 70, 'FTS AMC includes', F(46), mix(NAVY, GOLD, 1), a)
    items = ['Scheduled preventive visits', 'Safety inspections', 'Lubrication & adjustment',
             'Genuine spare parts', 'Priority breakdown callouts', 'A report after every visit']
    for i, s in enumerate(items):
        check_row(d, t, 2.2 + i * 1.25, 790 + i * 115, s, m, x=200)
    a5 = prog(t, 9.9, 0.5) * m
    text_c(d, 1630, 'All major lift brands', F(54), WHITE, a5)
    text_c(d, 1710, 'English / Arabic contracts', F(42, 'sans'), GREY, a5)

# ---------------- 4. Modernization ----------------
def panel(d, x0, y0, w, h, a, label, col):
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=24, fill=mix(NAVY, NAVY2, a), outline=mix(NAVY, col, a), width=5)
    f = F(40)
    tw = d.textlength(label, font=f)
    d.rounded_rectangle([x0 + w / 2 - tw / 2 - 24, y0 - 30, x0 + w / 2 + tw / 2 + 24, y0 + 30], radius=30, fill=mix(NAVY, col, a))
    d.text((x0 + w / 2 - tw / 2, y0 - 22), label, font=f, fill=mix(NAVY, WHITE, a))

def v_modern(img, t):
    d = ImageDraw.Draw(img)
    if t >= END:
        end_card(img, t - END); return
    m = fade_content(t)
    header(img, m)
    title(d, t, 'Old lift. New brain.', 'Modernize without rebuilding the shaft', m)
    w, h, y0 = 380, 520, 660
    a1 = prog(t, 0.8, 0.6) * m
    panel(d, 110, y0, w, h, a1, 'BEFORE', RED)
    # relays flicker
    for r in range(5):
        for c in range(3):
            xx, yy = 160 + c * 105, y0 + 70 + r * 85
            on = (math.sin(t * 9 + r * 1.7 + c * 2.3) > 0.4) and t < 6
            col = mix(GREY, RED, 0.8 if on else 0.0)
            d.rectangle([xx, yy, xx + 80, yy + 55], outline=mix(NAVY, col, a1), width=4)
            d.ellipse([xx + 30, yy + 18, xx + 50, yy + 38], fill=mix(NAVY, col, a1))
    d.text((150, y0 + h + 40), 'Relay controls', font=F(38), fill=mix(NAVY, GREY, a1))
    d.text((150, y0 + h + 90), 'More faults, more energy', font=F(32, 'sans'), fill=mix(NAVY, GREY, a1))
    # arrow
    ka = prog(t, 3.0, 0.8) * m
    if ka > 0:
        ax0, ax1, ay = 505, 505 + 70 * ka, y0 + h / 2
        d.line([(ax0, ay), (ax1, ay)], fill=GOLD, width=10)
        if ka > 0.9:
            d.polygon([(ax1 + 25, ay), (ax1 - 5, ay - 22), (ax1 - 5, ay + 22)], fill=GOLD)
    a2 = prog(t, 3.8, 0.6) * m
    x2 = 590
    panel(d, x2, y0, w, h, a2, 'AFTER', GREEN)
    if a2 > 0:
        # chip
        cx, cy = x2 + w / 2, y0 + 210
        glow = 0.6 + 0.4 * math.sin(t * 4)
        d.rounded_rectangle([cx - 90, cy - 90, cx + 90, cy + 90], radius=16, fill=mix(NAVY, BLUE, a2 * 0.8), outline=mix(NAVY, WHITE, a2), width=4)
        for k in range(5):
            o = -70 + k * 35
            for (p, q, r2, s2) in [(cx + o, cy - 90, cx + o, cy - 120), (cx + o, cy + 90, cx + o, cy + 120),
                                   (cx - 90, cy + o, cx - 120, cy + o), (cx + 90, cy + o, cx + 120, cy + o)]:
                d.line([(p, q), (r2, s2)], fill=mix(NAVY, GREY, a2), width=5)
        f = F(44); tw = d.textlength('CPU', font=f)
        d.text((cx - tw / 2, cy - 26), 'CPU', font=f, fill=mix(NAVY, WHITE, a2))
        # VVVF bar
        d.rounded_rectangle([x2 + 50, y0 + 380, x2 + w - 50, y0 + 460], radius=16, outline=mix(NAVY, GREEN, a2), width=4)
        lvl = (math.sin(t * 2.5) * 0.5 + 0.5) * 0.6 + 0.35
        d.rounded_rectangle([x2 + 60, y0 + 390, x2 + 60 + (w - 120) * lvl, y0 + 450], radius=12, fill=mix(NAVY, GREEN, a2 * glow))
        d.text((x2 + 40, y0 + h + 40), 'Microprocessor', font=F(38), fill=mix(NAVY, WHITE, a2))
        d.text((x2 + 40, y0 + h + 90), '+ VVVF drive', font=F(32, 'sans'), fill=mix(NAVY, GREEN, a2))
    items = ['Smoother, quieter ride', 'Lower energy use', 'Upgraded safety systems', 'All major lift brands']
    for i, s in enumerate(items):
        check_row(d, t, 6.0 + i * 1.1, 1400 + i * 105, s, m, x=200)

VIDEOS = {'stuck': v_stuck, 'villa': v_villa, 'amc': v_amc, 'modern': v_modern}

if __name__ == '__main__':
    name = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'full'
    fn = VIDEOS[name]
    if mode == 'frames':
        for tt in [1.0, 5.0, 11.0, 14.0]:
            img = background(); fn(img, tt); img.save(f'/tmp/{name}_{tt}.png')
    else:
        tmp = '/tmp/fts-reels'; os.makedirs(tmp, exist_ok=True)
        out = os.path.join(REPO, 'reels'); os.makedirs(out, exist_ok=True)
        render(f'{tmp}/{name}_v.mp4', DUR, fn)
        music(f'{tmp}/{name}.wav', DUR, seed=list(VIDEOS).index(name))
        mux(f'{tmp}/{name}_v.mp4', f'{tmp}/{name}.wav', f'{out}/FTS-reel-{name}.mp4')
        print('done', name)
