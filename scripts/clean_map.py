#!/usr/bin/env python3
"""Loc nhieu ngoai tuong cua ban do SLAM (hau xu ly), giu nguyen cau truc ben trong.

Y tuong: o trong (free) that su la vung lien thong lon nhat; nhung diem trong/co vat le tre
ben ngoai tuong do tia LiDAR lot qua khe nen khong thuoc vung nay.
  1. free = pixel 254, occ = pixel 0, unknown = 205 (gia tri map_saver ghi o che do trinary).
  2. Co (erode) vung free de cat cac "ong dan" mong noi ra ngoai, lay thanh phan lien thong lon nhat,
     roi no (dilate) lai trong pham vi free ban dau.
  3. Giu o chiem (occ) chi khi nam sat vung free do (<= 2 pixel); phan con lai dat unknown.
Ban goc duoc luu thanh map_raw.pgm / map_raw.yaml.

Dung:  clean_map.py [thu_muc_maps]
"""
import os
import shutil
import sys
from collections import deque

import numpy as np
from PIL import Image

FREE, OCC, UNK = 254, 0, 205
d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'maps')
pgm, yaml = os.path.join(d, 'map.pgm'), os.path.join(d, 'map.yaml')
raw_pgm, raw_yaml = os.path.join(d, 'map_raw.pgm'), os.path.join(d, 'map_raw.yaml')

if not os.path.exists(raw_pgm):               # chi sao luu lan dau, khong ghi de ban goc
    shutil.copy(pgm, raw_pgm)
    with open(yaml) as f:
        txt = f.read().replace('image: map.pgm', 'image: map_raw.pgm')
    with open(raw_yaml, 'w') as f:
        f.write(txt)

img = np.array(Image.open(raw_pgm))
free = img >= 250
occ = img == OCC


def shift(a, dy, dx):
    out = np.zeros_like(a)
    h, w = a.shape
    ys, yd = (slice(dy, h), slice(0, h - dy)) if dy >= 0 else (slice(0, h + dy), slice(-dy, h))
    xs, xd = (slice(dx, w), slice(0, w - dx)) if dx >= 0 else (slice(0, w + dx), slice(-dx, w))
    out[ys, xs] = a[yd, xd]
    return out


def erode(a, r):
    out = a.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out &= shift(a, dy, dx)
    return out


def dilate(a, r):
    out = a.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= shift(a, dy, dx)
    return out


def largest_component(mask):
    h, w = mask.shape
    seen = np.zeros_like(mask)
    best = []
    for sy, sx in zip(*np.nonzero(mask)):
        if seen[sy, sx]:
            continue
        comp, q = [], deque([(sy, sx)])
        seen[sy, sx] = True
        while q:
            y, x = q.popleft()
            comp.append((y, x))
            for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        if len(comp) > len(best):
            best = comp
    out = np.zeros_like(mask)
    for y, x in best:
        out[y, x] = True
    return out


core = largest_component(erode(free, 2))
room = dilate(core, 2) & free                 # vung free that su cua arena
keep_occ = occ & dilate(room, 2)              # tuong sat vung free
out = np.full_like(img, UNK)
out[room] = FREE
out[keep_occ] = OCC
Image.fromarray(out).save(pgm)
print(f'free {free.sum()} -> {room.sum()} ; occ {occ.sum()} -> {keep_occ.sum()} (cell 0.05 m)')
Image.fromarray(out).transpose(Image.FLIP_TOP_BOTTOM).resize(
    (out.shape[1] * 4, out.shape[0] * 4), Image.NEAREST).save(os.path.join(d, 'map_preview.png'))
