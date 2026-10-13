#!/usr/bin/env python3
"""Tao hinh cho bao cao tu du lieu that (khong can GUI): ban do, ban do tho vs sau loc, quy dao Nav2.

Dau vao : maps/map.pgm, maps/map_raw.pgm, logs/nav_trajectory_run1.csv, logs/nav_trajectory.csv
Dau ra  : figures/fig_map_final.png, fig_map_raw_vs_clean.png, fig_nav_trajectory.png
"""
import csv
import os

from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, 'figures')
os.makedirs(OUT, exist_ok=True)
RES, OX, OY, S = 0.05, -4.9, -2.32, 4          # S: so pixel anh tren mot o luoi
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
COL = {1: (230, 50, 50), 2: (30, 110, 220), 3: (30, 160, 70), 4: (230, 140, 0)}


def font(n):
    try:
        return ImageFont.truetype(FONT, n)
    except OSError:
        return ImageFont.load_default()


def load(name):
    g = Image.open(os.path.join(D, 'maps', name)).convert('L')
    return g, Image.merge('RGB', (g, g, g)).resize((g.width * S, g.height * S), Image.NEAREST)


def to_px(x, y, h):
    return ((x - OX) / RES + 0.5) * S, (h - 1 - (y - OY) / RES + 0.5) * S


def grid(img, h):
    d = ImageDraw.Draw(img)
    f = font(14)
    for m in range(-4, 8):
        for (x, y) in ((m, OY), ):
            px, _ = to_px(m, 0, h)
            d.line([(px, 0), (px, img.height)], fill=(215, 225, 245), width=1)
            d.text((px + 2, img.height - 16), f'{m}', fill=(60, 60, 160), font=f)
    for m in range(-2, 9):
        _, py = to_px(0, m, h)
        d.line([(0, py), (img.width, py)], fill=(215, 225, 245), width=1)
        d.text((2, py - 16), f'{m}', fill=(60, 60, 160), font=f)


def paste_title(img, text):
    f = font(22)
    canvas = Image.new('RGB', (img.width, img.height + 36), 'white')
    canvas.paste(img, (0, 36))
    ImageDraw.Draw(canvas).text((10, 6), text, fill='black', font=f)
    return canvas


# 1. ban do cuoi (da loc)
g, big = load('map.pgm')
h = g.height
grid(big, h)
d = ImageDraw.Draw(big)
x0, y0 = to_px(0, 0, h)
d.ellipse([x0 - 7, y0 - 7, x0 + 7, y0 + 7], outline=(200, 0, 0), width=3)
d.text((x0 + 10, y0 - 8), 'goc map (sau undock)', fill=(200, 0, 0), font=font(15))
paste_title(big, 'Ban do cuoi cung maps/map.pgm (0.05 m/o, truc: met, frame map)').save(
    os.path.join(OUT, 'fig_map_final.png'))

# 2. tho vs da loc
_, a = load('map_raw.pgm')
_, b = load('map.pgm')
w = Image.new('RGB', (a.width * 2 + 10, a.height + 36), 'white')
w.paste(a, (0, 36))
w.paste(b, (a.width + 10, 36))
dd = ImageDraw.Draw(w)
dd.text((10, 6), 'Ban do tho tu SLAM Toolbox (map_raw.pgm)', fill='black', font=font(22))
dd.text((a.width + 20, 6), 'Sau hau xu ly (map.pgm)', fill='black', font=font(22))
w.save(os.path.join(OUT, 'fig_map_raw_vs_clean.png'))

# 3. quy dao Nav2
_, img = load('map.pgm')
grid(img, h)
d = ImageDraw.Draw(img)
# run1: 4 goal lien tiep (goal 1 ABORTED); run2: gui lai goal 1 (SUCCEEDED). File run2 da bi mot lan chay sau
# ghi de (send_goals.py luon ghi logs/nav_trajectory.csv) nen hinh goal 1 chi tao lai duoc neu con file nay.
runs = [('nav_trajectory_run1.csv', {2, 3, 4}), ('nav_trajectory_run2_goal1.csv', {1})]
stats = {}
for fn, keep in runs:
    pts = {}
    path = os.path.join(D, 'logs', fn)
    if not os.path.exists(path):
        print('bo qua (khong co):', fn)
        continue
    with open(path) as f:
        for r in csv.DictReader(f):
            k = int(r['goal'])
            if k in keep:
                pts.setdefault(k, []).append(to_px(float(r['x']), float(r['y']), h))
    for k, p in pts.items():
        # bo cac diem trung lien tiep cho nhe
        q = [p[0]] + [b for a_, b in zip(p, p[1:]) if a_ != b]
        d.line(q, fill=COL[k], width=4, joint='curve')
        stats[k] = q[-1]
goals = {1: (3.0, 2.0), 2: (2.5, 5.6), 3: (-0.4, 5.6), 4: (3.5, 0.2)}
for k, (gx, gy) in goals.items():
    px, py = to_px(gx, gy, h)
    d.ellipse([px - 11, py - 11, px + 11, py + 11], outline=COL[k], width=4, fill='white')
    d.text((px - 5, py - 9), str(k), fill=COL[k], font=font(17))
sx, sy = to_px(-0.1, -0.17, h)
d.polygon([(sx, sy - 12), (sx + 11, sy + 9), (sx - 11, sy + 9)], fill=(0, 0, 0))
d.text((sx + 14, sy - 6), 'Start', fill='black', font=font(16))
# chu thich
lx, ly = 20, 20
for k, c in COL.items():
    d.rectangle([lx, ly, lx + 26, ly + 10], fill=c)
    d.text((lx + 34, ly - 5), f'Goal {k} ({goals[k][0]}, {goals[k][1]})', fill='black', font=font(15))
    ly += 22
paste_title(img, 'Quy dao thuc te cua robot khi Nav2 di toi 4 goal (vi tri AMCL trong frame map)').save(
    os.path.join(OUT, 'fig_nav_trajectory.png'))
print('Da tao:', sorted(os.listdir(OUT)))
