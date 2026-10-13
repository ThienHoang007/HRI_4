#!/usr/bin/env python3
"""Tim vi tri robot tren ban do bang cach cham diem 1 scan LiDAR voi maps/map.pgm.

Voi moi ung vien (x, y, yaw) trong luoi, chieu cac diem scan len ban do va tinh khoang cach
trung binh toi o chiem gan nhat (distance transform). Ung vien co sai so nho nhat la vi tri
robot. Dung de dat /initialpose chinh xac va de kiem chung ket qua AMCL.
In ket qua dang:  best x y yaw rmse   (kem top 3).
Dung:  find_pose.py [x_min x_max y_min y_max]   (mac dinh quet toan ban do)
"""
import math
import os
import sys

import numpy as np
import rclpy
from PIL import Image
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img = np.array(Image.open(os.path.join(D, 'maps', 'map.pgm')))
H, W = img.shape
RES, OX, OY = 0.05, -4.9, -2.32
occ = img == 0

# distance transform bang BFS 8 lang gieng xap xi (don vi: pixel) -> met
dist = np.full(occ.shape, 1e3)
dist[occ] = 0
frontier = list(zip(*np.nonzero(occ)))
d = 0
while frontier and d < 80:
    d += 1
    nxt = []
    for y, x in frontier:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and dist[ny, nx] > d:
                    dist[ny, nx] = d
                    nxt.append((ny, nx))
    frontier = nxt
dist *= RES

rclpy.init()
node = rclpy.create_node('find_pose')
box = {}
node.create_subscription(LaserScan, 'scan', lambda m: box.__setitem__('s', m), qos_profile_sensor_data)
for _ in range(60):
    rclpy.spin_once(node, timeout_sec=1.0)
    if 's' in box:
        break
s = box.get('s')
if s is None:
    sys.exit('Khong nhan duoc /scan')
r = np.array(s.ranges)
a = s.angle_min + np.arange(len(r)) * s.angle_increment
ok = np.isfinite(r) & (r > s.range_min) & (r < min(s.range_max, 9.0))
r, a = r[ok], a[ok]
lx, ly = r * np.cos(a), r * np.sin(a)          # diem scan trong khung laser (~ base_link)

if len(sys.argv) == 5 and sys.argv[1] == 'eval':      # eval x y yaw_rad: cham diem 1 tu the
    x, y, yw = (float(v) for v in sys.argv[2:5])
    c, sn = math.cos(yw), math.sin(yw)
    gx, gy = x + c * lx - sn * ly, y + sn * lx + c * ly
    ix = ((gx - OX) / RES).astype(int)
    iy = H - 1 - ((gy - OY) / RES).astype(int)
    m = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
    print(f'eval rmse={np.sqrt(np.mean(dist[iy[m], ix[m]] ** 2)):.3f} m ({m.sum()}/{len(lx)} diem trong map)')
    sys.exit(0)
fine = len(sys.argv) == 5                       # co vung gioi han -> quet min hon
STEP, YSTEP = (0.05, 2) if fine else (0.1, 6)
xs = np.arange(-4.9, -4.9 + W * RES, STEP)
ys = np.arange(-2.32, -2.32 + H * RES, STEP)
if len(sys.argv) == 5:
    x0, x1, y0, y1 = (float(v) for v in sys.argv[1:5])
    xs, ys = xs[(xs >= x0) & (xs <= x1)], ys[(ys >= y0) & (ys <= y1)]
res = []
free = img >= 250
for yaw in np.deg2rad(np.arange(-180, 180, YSTEP)):
    c, sn = math.cos(yaw), math.sin(yaw)
    for y in ys:
        for x in xs:
            px = int((x - OX) / RES)
            py = H - 1 - int((y - OY) / RES)
            if not (0 <= px < W and 0 <= py < H and free[py, px]):
                continue
            gx, gy = x + c * lx - sn * ly, y + sn * lx + c * ly
            ix = ((gx - OX) / RES).astype(int)
            iy = H - 1 - ((gy - OY) / RES).astype(int)
            m = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
            if m.sum() < 0.8 * len(lx):
                continue
            e = np.sqrt(np.mean(dist[iy[m], ix[m]] ** 2))
            res.append((e, x, y, math.degrees(yaw)))
res.sort()
print(f'so diem scan: {len(lx)}')
for e, x, y, yw in res[:3]:
    print(f'ung vien: x={x:.2f} y={y:.2f} yaw={yw:.0f} deg  rmse={e:.3f} m')
e, x, y, yw = res[0]
print(f'best {x:.2f} {y:.2f} {math.radians(yw):.3f} {e:.3f}')
node.destroy_node()
rclpy.shutdown()
