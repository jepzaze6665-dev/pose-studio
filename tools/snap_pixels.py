"""แปลง "พิกเซลปลอม" จาก AI (เม็ดไม่เท่ากัน, ขอบเบลอ) เข้ากริดพิกเซลจริง
usage: python tools/snap_pixels.py <in_dir> <out_dir> [block]
- เดาขนาดเม็ด (block) จากความยาวช่วงสีที่พบบ่อยที่สุด ถ้าไม่ระบุ
- ย่อทีละบล็อกด้วยสีที่พบบ่อยที่สุดในบล็อก (mode) ไม่ใช่ค่าเฉลี่ย -> สีไม่เละ
- alpha เป็น 0/255 เท่านั้น, ผลลัพธ์เป็น PNG ขนาดพิกเซลจริง (เกมขยายแบบ nearest)
"""
import sys, os, glob
import numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
files = sorted(glob.glob(os.path.join(src, '*.png')))

def guess_block(paths):
    counts = np.zeros(80, int)
    for p in paths:
        a = np.array(Image.open(p).convert('RGBA')).astype(int)
        for arr in (a, a.transpose(1, 0, 2)):
            for row in arr[::7]:
                ch = np.abs(np.diff(row[:, :3], axis=0)).sum(1) > 60
                idx = np.where(ch)[0]
                r = np.diff(idx); r = r[(r >= 6) & (r < 80)]
                counts += np.bincount(r, minlength=80)[:80]
    # runs are multiples of the block: score each candidate by how many runs it divides
    best, bs = 0, 0
    for b in range(6, 30):
        m = np.arange(80)
        ok = (m % b <= 1) | (m % b >= b - 1)
        s = counts[ok & (m >= b)].sum() / (1 + 0.02 * b)
        if s > bs: best, bs = b, s
    return best

block = int(sys.argv[3]) if len(sys.argv) > 3 else guess_block(files)
print('block size =', block)
for p in files:
    a = np.array(Image.open(p).convert('RGBA'))
    H, W = a.shape[0] // block, a.shape[1] // block
    o = np.zeros((H, W, 4), np.uint8)
    for y in range(H):
        for x in range(W):
            b = a[y*block:(y+1)*block, x*block:(x+1)*block].reshape(-1, 4)
            if (b[:, 3] > 128).mean() < 0.5: continue
            c = b[b[:, 3] > 128][:, :3] // 12          # bucket colours, take most common
            keys, cnt = np.unique(c, axis=0, return_counts=True)
            k = keys[cnt.argmax()]
            sel = b[b[:, 3] > 128][:, :3][(c == k).all(1)]
            o[y, x, :3] = sel.mean(0); o[y, x, 3] = 255
    Image.fromarray(o).save(os.path.join(out, os.path.basename(p)))
print('done', len(files))
