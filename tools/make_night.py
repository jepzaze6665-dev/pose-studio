"""ชั้นไฟกลางคืน: หาหน้าต่าง/โคมที่วาดแบบ "ไม่เปิดไฟ" (กระจกน้ำเงินเข้ม) แล้วทำเป็นแสงส้มอุ่น
usage: python tools/make_night.py <in.png> [...]  -> <name>_night.png
"""
import sys, os
import numpy as np, cv2
from PIL import Image

for src in sys.argv[1:]:
    a = np.array(Image.open(src).convert('RGBA')).astype(int)
    hsv = cv2.cvtColor(a[..., :3].astype(np.uint8), cv2.COLOR_RGB2HSV).astype(int)
    H, S, V = hsv[..., 0] * 2, hsv[..., 1], hsv[..., 2]
    m = ((H > 195) & (H < 255) & (S > 60) & (V > 35) & (V < 175) & (a[..., 3] > 200)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros_like(m); area = a.shape[0] * a.shape[1]
    cand = [i for i in range(1, n) if 30 < st[i][4] < area * .02 and st[i][4] / max(1, st[i][2] * st[i][3]) > .6 and .7 < st[i][3] / max(1, st[i][2]) < 3]
    med = np.median([st[i][4] for i in cand]) if cand else 0
    for i in cand:
        if st[i][4] < med * 3: keep[lab == i] = 1   # ช่องกระจกขนาดใกล้กัน (ไม่เอาหลังคา/ธงผืนใหญ่)
    if 'lamp' in os.path.basename(src):          # โคม: กระจกโคมสีเทาอ่อนในกรอบโคม
        Hh, Ww = m.shape; box = np.zeros_like(m); box[int(Hh*.36):int(Hh*.62), int(Ww*.62):] = 1
        keep = (box & (a[..., 3] > 200) & (S < 90) & (V > 70)).astype(np.uint8)
    o = np.zeros((*m.shape, 4), np.uint8); o[..., 0] = 255; o[..., 1] = 190; o[..., 2] = 95; o[..., 3] = keep * 255
    dst = os.path.splitext(src)[0] + '_night.png'
    Image.fromarray(o).save(dst); print(dst, int(keep.sum()))
