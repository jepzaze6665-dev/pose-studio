"""ตัดชีทชิ้นส่วนพื้นชมพู (#FF00FF) เป็น PNG พื้นใสทีละชิ้น
usage: python tools/cut_parts.py <sheet image> <out dir>
- ลบสีชมพู + ขอบชมพูจางๆ (despill)
- แยกชิ้นด้วย connected components, ครอปชิดขอบ
- บันทึก piece_XX.png + pieces.json (ตำแหน่ง/ขนาดในชีท) เพื่อให้ตั้งชื่อชิ้นทีหลัง
"""
import sys, json, os
import numpy as np, cv2
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
im = np.array(Image.open(src).convert('RGB')).astype(np.float32)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
# "magenta-ness": strong R and B, weak G
mag = np.clip(((r + b) / 2 - g) / 255.0, 0, 1)
alpha = np.clip((0.62 - mag) / 0.25, 0, 1)            # soft key
# despill: pull magenta out of edge pixels
spill = np.minimum(r, b) - g
fix = np.clip(spill, 0, None) * (1 - alpha)
im[..., 0] -= fix; im[..., 2] -= fix
mask = (alpha > 0.5).astype(np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
pieces = []
for i in range(1, n):
    x, y, w, h, area = stats[i]
    if area < 2000: continue
    pad = 4
    x0, y0, x1, y1 = max(0, x - pad), max(0, y - pad), min(im.shape[1], x + w + pad), min(im.shape[0], y + h + pad)
    a = alpha[y0:y1, x0:x1] * (lab[y0:y1, x0:x1] == i).astype(np.float32)
    a = cv2.dilate(a, np.ones((3, 3), np.uint8))       # keep soft edge
    a = np.minimum(a, alpha[y0:y1, x0:x1])
    rgba = np.dstack([np.clip(im[y0:y1, x0:x1], 0, 255), a * 255]).astype(np.uint8)
    pieces.append(dict(x=int(x), y=int(y), w=int(w), h=int(h), rgba=rgba))
pieces.sort(key=lambda p: (round(p['y'] / 150), p['x']))   # row-major
meta = []
for k, p in enumerate(pieces):
    name = f'piece_{k:02d}.png'
    Image.fromarray(p.pop('rgba')).save(os.path.join(out, name))
    meta.append(dict(file=name, **p))
json.dump(meta, open(os.path.join(out, 'pieces.json'), 'w'), indent=1)
for m in meta: print(m)
