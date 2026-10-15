"""สร้าง normal map อัตโนมัติจากภาพชิ้นเดี่ยว (หลักที่ 12 จากคลิปแมพ: ความหนาจากขอบ + เส้นแบ่งส่วน)
usage: python tools/make_normal.py <in.png> [<in2.png> ...]   -> <name>_n.png ข้างไฟล์เดิม
- ความสูง = ระยะจากขอบ (ทำให้ทรงพองกลาง) + ความสว่างเล็กน้อย - เส้นขอบดำ (ร่องแบ่งส่วน)
- สี: R = ทิศซ้าย-ขวา, G = ทิศขึ้น-ลง, B = หันเข้าหากล้อง (มาตรฐาน normal map)
"""
import sys, os
import numpy as np, cv2
from PIL import Image

for src in sys.argv[1:]:
    a = np.array(Image.open(src).convert('RGBA')).astype(np.float32) / 255
    al = (a[..., 3] > .5).astype(np.uint8)
    lum = a[..., :3] @ np.array([.3, .59, .11], np.float32)
    d = cv2.distanceTransform(al, cv2.DIST_L2, 5)
    span = max(6.0, min(al.shape) * .06)
    h = np.sqrt(np.clip(d / span, 0, 1))                    # พองกลางแบบหมอน
    groove = (lum < .18).astype(np.float32) * al             # เส้นขอบดำ = ร่อง
    h = h + .15 * cv2.GaussianBlur(lum, (0, 0), 2) - .35 * cv2.GaussianBlur(groove, (0, 0), 1.2)
    h = cv2.GaussianBlur(h, (0, 0), 1.5)
    gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3)
    k = 4.0
    n = np.dstack([-gx * k, gy * k, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    rgb = ((n * .5 + .5) * 255).astype(np.uint8)
    out = np.dstack([rgb, (a[..., 3] * 255).astype(np.uint8)])
    dst = os.path.splitext(src)[0] + '_n.png'
    Image.fromarray(out).save(dst); print(dst)
