"""ตัดชีท VFX พื้นดำ -> PNG ทีละชิ้น โดยไม่ลบ "แกนดำ" ของชิ้น
usage: python tools/cut_black.py <sheet> <out_dir> [--one] [--tol 10]
- พื้นหลัง = พิกเซลมืด (max<tol) ที่ต่อถึงขอบภาพ (flood fill) -> แกนดำที่มีขอบสว่างล้อมไว้จะไม่หาย
- ขอบนุ่ม: ไล่ alpha ตามความสว่างในแถบรอยต่อ เพื่อให้ควันจางๆ ยังฟุ้งได้
- --one = ทั้งภาพเป็นชิ้นเดียว (เช่น หัวอสูร)
"""
import sys, os, json
import numpy as np, cv2
from PIL import Image

args = sys.argv[1:]
src, out = args[0], args[1]
one = '--one' in args
tol = int(args[args.index('--tol') + 1]) if '--tol' in args else 10
os.makedirs(out, exist_ok=True)
rgb = np.array(Image.open(src).convert('RGB'))
mx = rgb.max(-1).astype(np.float32)
dark = (mx < tol).astype(np.uint8)
n, lab = cv2.connectedComponents(dark, connectivity=4)
border = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]); border = border[border > 0]
bg = np.isin(lab, border)
alpha = (~bg).astype(np.float32)
# soft edge: pixels near background fade by brightness (smoke wisps)
near = cv2.dilate(bg.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~bg
alpha[near] = np.clip((mx[near] - tol * .5) / (tol * 3.0), 0.15, 1.0)
alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
rgba = np.dstack([rgb, (alpha * 255).astype(np.uint8)])

def save(arr, name):
    Image.fromarray(arr).save(os.path.join(out, name)); return name

meta = []
if one:
    ys, xs = np.where(alpha > .05); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    meta.append(dict(file=save(rgba[y0:y1, x0:x1], 'piece_00.png'), x=int(x0), y=int(y0), w=int(x1 - x0), h=int(y1 - y0)))
else:
    m = (alpha > .05).astype(np.uint8)
    m = cv2.dilate(m, np.ones((9, 9), np.uint8))           # join tiny sparks/tips to their piece
    k, lab2, st, _ = cv2.connectedComponentsWithStats(m, 8)
    items = []
    for i in range(1, k):
        x, y, w, h, area = st[i]
        if area < 400: continue
        sub = rgba[y:y + h, x:x + w].copy(); sub[..., 3] = sub[..., 3] * (lab2[y:y + h, x:x + w] == i)
        items.append((x, y, w, h, sub))
    rowh = np.median([it[3] for it in items]) if items else 1
    items.sort(key=lambda it: (round(it[1] / rowh), it[0]))
    for j, (x, y, w, h, sub) in enumerate(items):
        meta.append(dict(file=save(sub, f'piece_{j:02d}.png'), x=int(x), y=int(y), w=int(w), h=int(h)))
json.dump(meta, open(os.path.join(out, 'pieces.json'), 'w'), indent=1)
print(len(meta), 'pieces')
