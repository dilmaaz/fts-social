import math, subprocess, os
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
NAVY = (16, 31, 62)
NAVY2 = (24, 44, 84)
GOLD = (201, 162, 74)
BLUE = (0, 142, 188)
GREEN = (0, 160, 56)
RED = (223, 17, 26)
WHITE = (255, 255, 255)
GREY = (150, 165, 190)
REPO = '/home/claude/fts-social'
FONTS = REPO + '/assets/fonts/'

_fc = {}
def F(size, kind='sansb'):
    k = (size, kind)
    if k not in _fc:
        name = {'sansb': 'LiberationSans-Bold.ttf', 'sans': 'LiberationSans-Regular.ttf',
                'serif': 'LiberationSerif-Bold.ttf'}[kind]
        _fc[k] = ImageFont.truetype(FONTS + name, size)
    return _fc[k]

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def prog(t, start, dur):
    return ease((t - start) / dur)

def mix(c1, c2, a):
    a = clamp(a)
    return tuple(int(c1[i] + (c2[i] - c1[i]) * a) for i in range(3))

LOGO_REV = Image.open(REPO + '/assets/logo/fts-logo-reverse.png').convert('RGBA')

def background():
    img = Image.new('RGB', (W, H), NAVY)
    d = ImageDraw.Draw(img)
    # brand "rising bars" bleeding off the bottom-right edge, subtle
    ang = math.radians(40)
    for i, col in enumerate([BLUE, GREEN, RED]):
        cx, cy = W - 40 + i * 70, H - 120 + i * 70
        L, T = 520, 34
        dx, dy = math.cos(ang) * L / 2, -math.sin(ang) * L / 2
        nx, ny = math.sin(ang) * T / 2, math.cos(ang) * T / 2
        pts = [(cx - dx - nx, cy - dy - ny), (cx + dx - nx, cy + dy - ny),
               (cx + dx + nx, cy + dy + ny), (cx - dx + nx, cy - dy + ny)]
        d.polygon(pts, fill=mix(NAVY, col, 0.55))
    return img

def text_c(d, y, s, font, col, a=1.0, x=None):
    col = mix(NAVY, col, a)
    tw = d.textlength(s, font=font)
    d.text(((W - tw) / 2 if x is None else x, y), s, font=font, fill=col)

def header(img, a=1.0):
    lg = LOGO_REV.copy()
    lg.thumbnail((240, 150))
    if a < 1:
        al = lg.split()[3].point(lambda v: int(v * a))
        lg.putalpha(al)
    img.paste(lg, (60, 70), lg)

def end_card(img, tl):
    """tl: seconds since end card start (0..3)."""
    d = ImageDraw.Draw(img)
    a = prog(tl, 0, 0.6)
    lg = LOGO_REV.copy()
    lg.thumbnail((620, 340))
    al = lg.split()[3].point(lambda v: int(v * a))
    lg.putalpha(al)
    y0 = int(470 - 40 * (1 - a))
    img.paste(lg, ((W - lg.width) // 2, y0), lg)
    a2 = prog(tl, 0.4, 0.6)
    text_c(d, 900, 'Complete vertical transport solutions', F(40, 'sans'), WHITE, a2)
    # pill
    a3 = prog(tl, 0.7, 0.5)
    pw, ph = 620, 120
    px, py = (W - pw) // 2, 1040
    s = 0.9 + 0.1 * a3 + 0.03 * math.sin(tl * 6) * a3
    w2, h2 = pw * s, ph * s
    box = [W / 2 - w2 / 2, py + ph / 2 - h2 / 2, W / 2 + w2 / 2, py + ph / 2 + h2 / 2]
    d.rounded_rectangle(box, radius=h2 / 2, fill=mix(NAVY, GOLD, a3))
    f = F(int(54 * s))
    tw = d.textlength('GET QUOTE NOW', font=f)
    d.text((W / 2 - tw / 2, py + ph / 2 - 30 * s), 'GET QUOTE NOW', font=f, fill=mix(GOLD, NAVY, 1) if a3 > 0.01 else NAVY)
    a4 = prog(tl, 1.0, 0.5)
    text_c(d, 1230, 'WhatsApp +971 50 528 4597', F(58), WHITE, a4)
    text_c(d, 1320, 'www.ftselevators.com', F(48, 'sans'), GOLD, a4)
    text_c(d, 1440, 'Dubai · Sharjah · Ajman · all UAE', F(38, 'sans'), GREY, a4)

class Encoder:
    def __init__(self, path):
        self.tmp = path[:-4] + '.part.mp4'
        self.path = path
        self.p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                                   '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '20',
                                   '-preset', 'veryfast', '-pix_fmt', 'yuv420p', self.tmp], stdin=subprocess.PIPE)
    def add(self, img):
        self.p.stdin.write(img.tobytes())
    def close(self):
        self.p.stdin.close()
        if self.p.wait() == 0:
            os.replace(self.tmp, self.path)
        else:
            raise SystemExit('ffmpeg failed')

def render(path, dur, draw):
    enc = Encoder(path)
    n = int(dur * FPS)
    for i in range(n):
        t = i / FPS
        img = background()
        draw(img, t)
        # global fade in/out
        if t < 0.4 or t > dur - 0.4:
            k = clamp(t / 0.4) if t < 0.4 else clamp((dur - t) / 0.4)
            img = Image.blend(Image.new('RGB', (W, H), NAVY), img, k)
        enc.add(img)
    enc.close()

def music(path, dur, seed=0):
    import numpy as np, wave
    sr = 44100
    t = np.arange(int(sr * dur)) / sr
    chords = [[220.0, 277.18, 329.63], [196.0, 246.94, 293.66], [174.61, 220.0, 261.63], [196.0, 246.94, 329.63]]
    chords = chords[seed % 4:] + chords[:seed % 4]
    sig = np.zeros_like(t)
    seg = dur / 4
    for k, ch in enumerate(chords):
        m = (t >= k * seg) & (t < (k + 1) * seg + 0.5)
        env = np.clip((t - k * seg) / 0.5, 0, 1) * np.clip(((k + 1) * seg + 0.5 - t) / 0.8, 0, 1)
        for f in ch:
            sig += m * env * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * 0.12
    # soft pulse
    beat = (np.sin(2 * np.pi * 2 * t) > 0.97).astype(float)
    sig += np.convolve(beat, np.exp(-np.arange(2000) / 300), 'same')[:len(t)] * np.sin(2 * np.pi * 110 * t) * 0.15
    fade = np.clip(t / 1.0, 0, 1) * np.clip((dur - t) / 1.5, 0, 1)
    sig = sig * fade
    sig = sig / (np.abs(sig).max() + 1e-9) * 0.6
    data = (sig * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(data.tobytes())

def mux(video, audio, out):
    tmp = out[:-4] + '.part.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-i', audio, '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', tmp], check=True)
    os.replace(tmp, out)
