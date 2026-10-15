"""ตัด sprite sheet แบบกริด (พื้นดำ) -> แถบเฟรมเดียว (strip) + json
usage: python tools/cut_grid.py <sheet> <out_prefix> <cols> <rows> [--frames N] [--align none|center|eye] [--crop-bottom 0.12] [--inset 0.02]
- ตัดตามช่องกริด, เว้นขอบ (inset) กันเส้นกริดสีเทา, --crop-bottom ตัดตัวเลขกำกับใต้ภาพ
- ลบพื้นดำแบบ flood fill จากขอบช่อง (แกนดำของชิ้นไม่หาย)
- --align: center = จัดให้จุดศูนย์ถ่วงตรงกันทุกเฟรม, eye = จัดให้จุดสว่างที่สุด (ตา) ตรงกัน -> AI วาดเยื้องก็ไม่สั่น
ผลลัพธ์: <out_prefix>.png (เฟรมเรียงแนวนอน) + <out_prefix>.json
"""
import sys, json
import numpy as np, cv2
from PIL import Image

a = sys.argv[1:]
src, outp, cols, rows = a[0], a[1], int(a[2]), int(a[3])
opt = lambda k, d: a[a.index(k) + 1] if k in a else d
nframes = int(opt('--frames', cols * rows)); align = opt('--align', 'none')
cropb = float(opt('--crop-bottom', 0)); inset = float(opt('--inset', .02)); tol = 12

img = np.array(Image.open(src).convert('RGB'))
H, W = img.shape[:2]; cw, ch = W / cols, H / rows
frames = []
for r in range(rows):
    for c in range(cols):
        if len(frames) >= nframes: break
        x0, y0 = int(c * cw + cw * inset), int(r * ch + ch * inset)
        x1, y1 = int((c + 1) * cw - cw * inset), int((r + 1) * ch - ch * inset - ch * cropb)
        cell = img[y0:y1, x0:x1]
        mx = cell.max(-1).astype(np.float32)
        # grid lines are low-saturation gray: treat as background too
        sat = cell.max(-1).astype(int) - cell.min(-1).astype(int)
        bgish = ((mx < tol) | ((sat < 14) & (mx < 90))).astype(np.uint8)
        n, lab = cv2.connectedComponents(bgish, connectivity=4)
        b = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]); b = b[b > 0]
        bg = np.isin(lab, b)
        al = (~bg).astype(np.float32)
        near = cv2.dilate(bg.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~bg
        al[near] = np.clip((mx[near] - tol * .5) / (tol * 3.), .15, 1.)
        al = cv2.GaussianBlur(al, (3, 3), 0)
        frames.append(np.dstack([cell, (al * 255).astype(np.uint8)]))

fh = min(f.shape[0] for f in frames); fw = min(f.shape[1] for f in frames)
frames = [f[:fh, :fw] for f in frames]
def anchor(f):
    al = f[..., 3].astype(np.float32) / 255
    if align == 'eye':
        lum = f[..., :3].astype(np.float32).mean(-1) * al
        thr = np.percentile(lum[al > .5], 99.5) if (al > .5).any() else 255
        ys, xs = np.where(lum >= thr)
        return (xs.mean(), ys.mean()) if len(xs) else (fw / 2, fh / 2)
    ys, xs = np.nonzero(al > .3)
    return (xs.mean(), ys.mean()) if len(xs) else (fw / 2, fh / 2)
if align != 'none':
    ref = np.median([anchor(f) for f in frames if f[..., 3].any()], axis=0)
    out = []
    for f in frames:
        ax, ay = anchor(f); dx, dy = ref[0] - ax, ref[1] - ay
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        out.append(cv2.warpAffine(f, M, (fw, fh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0)))
    frames = out
strip = np.concatenate(frames, axis=1)
Image.fromarray(strip).save(outp + '.png')
json.dump(dict(frames=len(frames), w=fw, h=fh, align=align), open(outp + '.json', 'w'))
print(outp, len(frames), 'frames', fw, 'x', fh)
