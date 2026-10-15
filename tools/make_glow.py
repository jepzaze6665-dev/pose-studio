"""หลักที่ 6: แยกชั้นแสงเรืองออกจากภาพอัตโนมัติ (ไม่ต้องเจน C7 แยก)
usage: python tools/make_glow.py <in.png> <out_glow.png> [red|purple|blue]
เก็บเฉพาะพิกเซลสีสดตามโทนที่เลือก ที่เหลือเป็นโปร่งใส -> เกมซ้อนแบบ additive + bloom + เต้นตามจังหวะ
"""
import sys, colorsys
import numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
tone = sys.argv[3] if len(sys.argv) > 3 else 'red'
HUE = {'red': (0.94, 0.05), 'purple': (0.72, 0.86), 'blue': (0.52, 0.66)}[tone]
a = np.array(Image.open(src).convert('RGBA')).astype(np.float32) / 255
rgb = a[..., :3]
mx, mn = rgb.max(-1), rgb.min(-1)
sat = (mx - mn) / np.maximum(mx, 1e-5)
r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
h = np.vectorize(lambda r, g, b: colorsys.rgb_to_hsv(r, g, b)[0], otypes=[np.float32])(r, g, b)
lo, hi = HUE
inhue = ((h >= lo) | (h <= hi)) if lo > hi else ((h >= lo) & (h <= hi))
m = inhue & (sat > 0.55) & (mx > 0.45) & (a[..., 3] > 0.5)
o = np.zeros_like(a); o[..., :3] = rgb; o[..., 3] = m * a[..., 3]
Image.fromarray((o * 255).astype(np.uint8)).save(out)
print(out, 'glow px:', int(m.sum()))
