"""ลบ "หมุดหุ่น" (ทรงกระบอกแคบๆ ที่ AI ชอบวาดบนหัวชิ้นส่วน) ออกจากชิ้น rig
usage: python tools/strip_pegs.py <part.png> [...]   (เขียนทับไฟล์เดิม · เก็บของเดิมไว้ที่ <name>_peg.png)
หลัก: ไล่แถวจากบนลงล่าง แถวที่ความกว้างเนื้อภาพ < 45% ของความกว้างสูงสุด = หมุด -> ตัดทิ้งจนถึงแถวแรกที่กว้างพอ
"""
import sys, os, shutil
import numpy as np
from PIL import Image

def peg_rows(a):
    """แถวบนที่ยังมีสีหมุด (น้ำตาลเทาหม่น ไม่ใช่ทอง/ผ้าน้ำเงิน) เกิน 20% ของเนื้อแถว"""
    rgb = a[..., :3].astype(int); r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    peg = (a[..., 3] > 128) & (r >= g) & (g >= b - 5) & (r - b > 8) & (r - b < 70) & (r > 55) & (r < 170)
    op = (a[..., 3] > 128).sum(1)
    return peg.sum(1) / np.maximum(op, 1)

for src in sys.argv[1:]:
    a = np.array(Image.open(src).convert('RGBA'))
    base, ext = os.path.splitext(src)
    if os.path.exists(base + '_peg' + ext): a = np.array(Image.open(base + '_peg' + ext).convert('RGBA'))  # เริ่มจากต้นฉบับเสมอ
    op = a[..., 3] > 128
    width = op.sum(1)
    full = width.max()
    top = int(np.argmax(width > 0))
    y = top
    while y < len(width) * .3 and width[y] < full * .45:   # 1) ส่วนแคบ = ตัวหมุด
        y += 1
    fr = peg_rows(a)
    while y < len(width) * .3 and fr[y] > .2:              # 2) ฐานหมุดที่บานออก (ยังเป็นสีหมุด)
        y += 1
    y += 3                                                  # เผื่อเส้นขอบใต้หมุด
    if y - top < 6:
        print(src, 'no peg'); continue
    if not os.path.exists(base + '_peg' + ext): shutil.copy(src, base + '_peg' + ext)
    Image.fromarray(a[y:]).save(src)
    print(src, f'cut {y - top}px of {a.shape[0]} ({(y - top) / a.shape[0]:.0%})')
