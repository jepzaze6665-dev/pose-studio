"""แขน/ขาชิ้นเดียว (ชีท C2 v2) -> 2 ท่อนสำหรับกระดูก บน/ล่าง แบบไม่เห็นรอยต่อ
usage: python tools/split_limbs.py <part_dir> [--arm 0.45] [--leg 0.47] [--side-boot]
อ่าน  <part_dir>/arm_front.png arm_back.png leg_front.png leg_back.png
เขียน <part_dir>/armF_u.png armF_l.png armB_u.png armB_l.png legF_u.png legF_l.png legB_u.png legB_l.png + split.json
หลัก (จากคลิป rig): ศอก ≈ 45% ของแขน, เข่า ≈ 47% ของขา
- ท่อนล่างเริ่มก่อนจุดข้อต่อ (overlap) เพื่อให้ตอนงอยังมีเนื้อซ้อนกัน
- ท่อนที่ "วาดทับ" ได้ขอบจางนุ่ม: แขน = ท่อนบนทับท่อนล่าง, ขา = ท่อนล่างทับท่อนบน (ตามลำดับวาดของ rig)
split.json เก็บความสูงจริงของแต่ละท่อน + ตำแหน่งข้อต่อ (สัดส่วน) ให้คำนวณขนาด/จุดหมุนใน rig
"""
import sys, os, json
import numpy as np
from PIL import Image

args = sys.argv[1:]
d = args[0]
ARM = float(args[args.index('--arm') + 1]) if '--arm' in args else .45
LEG = float(args[args.index('--leg') + 1]) if '--leg' in args else .47
OV, FE = .07, .05            # overlap ใต้ข้อต่อ, ความยาวขอบจาง (สัดส่วนความยาวทั้งชิ้น)

def feather(a, top):
    h = a.shape[0]; n = max(2, int(FE * H))
    ramp = np.linspace(0, 1, n)
    al = a[..., 3].astype(np.float32)
    if top: al[:n] *= ramp[:, None]
    else: al[h - n:] *= ramp[::-1][:, None]
    a[..., 3] = al.astype(np.uint8); return a

out = {}
for limb, j, upper_on_top in [('arm', ARM, True), ('leg', LEG, False)]:
    for side, tag in [('front', 'F'), ('back', 'B')]:
        a = np.array(Image.open(os.path.join(d, f'{limb}_{side}.png')).convert('RGBA'))
        H = a.shape[0]; jy = int(H * j)
        up = a[:jy + int(FE * H)].copy()                  # ท่อนบนยาวเลยข้อต่อนิดหน่อย (ให้มีที่จาง)
        lo = a[jy - int(OV * H):].copy()                  # ท่อนล่างเริ่มก่อนข้อต่อ
        if upper_on_top: up = feather(up, top=False)
        else: lo = feather(lo, top=True)
        Image.fromarray(up).save(os.path.join(d, f'{limb}{tag}_u.png'))
        Image.fromarray(lo).save(os.path.join(d, f'{limb}{tag}_l.png'))
        out[f'{limb}{tag}'] = {'full': H, 'joint': jy, 'up_h': up.shape[0], 'lo_h': lo.shape[0], 'lo_joint': int(OV * H)}
# ทริคขาหน้า (คลิป c4): ถ้าบูทขาหน้าวาดหันเข้าจอ ให้ใช้แข้งขาหลัง (บูทหันข้าง = หันไปทางที่เดิน) แทน — เก็บของเดิมไว้ legF_l_front_toe.png
if '--side-boot' in args:
    import shutil
    shutil.copy(os.path.join(d, 'legF_l.png'), os.path.join(d, 'legF_l_front_toe.png'))
    shutil.copy(os.path.join(d, 'legB_l.png'), os.path.join(d, 'legF_l.png'))
json.dump(out, open(os.path.join(d, 'split.json'), 'w'), indent=1)
print(json.dumps(out))
