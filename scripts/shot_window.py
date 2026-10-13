#!/usr/bin/env python3
"""Chup anh mot cua so X11 (RViz2/Gazebo chay qua XWayland) ma khong can GNOME Screenshot.

Dung: shot_window.py <ten-cua-so-chua-chuoi> <out.png>
Vi du: shot_window.py RViz figures/fig_rviz.png
Nang cua so len tren (XRaiseWindow), cho ve lai, roi xwd -id + doi sang PNG.
"""
import ctypes
import ctypes.util
import os
import subprocess
import sys
import time

name_part, out = sys.argv[1], sys.argv[2]
tree = subprocess.run(['xwininfo', '-root', '-tree'], capture_output=True, text=True).stdout
wid = None
for line in tree.splitlines():
    if name_part.lower() in line.lower() and '1x1' not in line and '3x3' not in line:
        wid = line.split()[0]
        break
if wid is None:
    sys.exit(f'khong thay cua so chua "{name_part}"')

x11 = ctypes.CDLL(ctypes.util.find_library('X11'))
x11.XOpenDisplay.restype = ctypes.c_void_p
dpy = x11.XOpenDisplay(None)
w = int(wid, 16)
x11.XMapRaised(ctypes.c_void_p(dpy), ctypes.c_ulong(w))
x11.XRaiseWindow(ctypes.c_void_p(dpy), ctypes.c_ulong(w))
x11.XFlush(ctypes.c_void_p(dpy))
time.sleep(1.5)

xwd = out + '.xwd'
with open(xwd, 'wb') as f:
    subprocess.run(['xwd', '-id', wid, '-silent'], stdout=f, check=True)
here = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, '-I', os.path.join(here, 'xwd2png.py'), xwd, out], check=True)
os.remove(xwd)
