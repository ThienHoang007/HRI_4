#!/usr/bin/env python3
"""Doc file XWD (xwd -id <window>) -> PNG. Dung: xwd2png.py in.xwd out.png"""
import struct
import sys

from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
raw = open(src, 'rb').read()
hdr = struct.unpack('>25I', raw[:100])
header_size, width, height = hdr[0], hdr[4], hdr[5]
bits_per_pixel, bytes_per_line = hdr[11], hdr[12]
ncolors = hdr[19]
off = header_size + ncolors * 12          # sau header + bang mau
im = Image.frombuffer('RGBX' if bits_per_pixel == 32 else 'RGB', (width, height),
                      raw[off:], 'raw', 'BGRX' if bits_per_pixel == 32 else 'BGR',
                      bytes_per_line, 1).convert('RGB')
im.save(dst)
print(dst, im.size)
