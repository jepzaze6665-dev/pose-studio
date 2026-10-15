"""สร้าง head_hair.png = มาสก์เฉพาะ "ผม" (+ เส้นขอบผม) จากภาพหัว
ใช้ตอนใส่หมวก: ซ่อนเฉพาะผมที่โผล่นอกหมวก หน้า/คาง/หู ไม่โดนตัด
usage: python tools/hair_mask.py <head.png> <out_hair.png>
"""
import sys, colorsys
import numpy as np, cv2
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
a = np.array(Image.open(src).convert('RGBA')).astype(np.float32) / 255
rgb, al = a[..., :3], a[..., 3]
hsv = cv2.cvtColor((rgb * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
H, S, V = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
skin = (H >= 10) & (H <= 40) & (S < 0.42) & (V > 0.62)            # ผิวสว่าง อิ่มตัวน้อย
eyes = (H >= 190) & (H <= 250) & (S > 0.35)                        # ตาสีฟ้า
white = (S < 0.12) & (V > 0.8)
hair = (H >= 8) & (H <= 45) & (S >= 0.42) & (V > 0.18) & (al > 0.5) & ~skin
hair = cv2.morphologyEx(hair.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
# keep only big hair blobs (drop eyebrows/blush specks)
n, lab, st, _ = cv2.connectedComponentsWithStats(hair, 8)
keep = np.zeros_like(hair)
for i in range(1, n):
    if st[i, 4] > 0.02 * hair.sum(): keep[lab == i] = 1
# grow into the dark outline around the hair, but never into skin/eyes/white
k = max(3, int(round(min(a.shape[:2]) * 0.03)) | 1)
grown = cv2.dilate(keep, np.ones((k, k), np.uint8)).astype(bool)
dark = V < 0.35
mask = (keep.astype(bool) | (grown & dark)) & ~skin & ~eyes & ~white & (al > 0.05)
outa = (mask * 255).astype(np.uint8)
Image.fromarray(np.dstack([np.zeros_like(outa)] * 3 + [outa])).save(out)
print(out, 'hair px', int(mask.sum()), 'of', int((al > 0.5).sum()))
