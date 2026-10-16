"""ประกอบชุดของเมือง v2 จากชีทที่ตัดแล้ว -> assets/maps/town/kit/<ชื่อ>.png
usage: python tools/build_town_kit.py
ต้องรัน cut_parts.py กับ tk1/tk2/tk2b/tk3 ก่อน (pieces_tkX/) · tk5 กับพื้น tk4 ทำในนี้เลย
"""
import json, os, shutil
import numpy as np, cv2
from PIL import Image

T = 'assets/maps/town'
KIT = f'{T}/kit'
os.makedirs(KIT, exist_ok=True)

def pieces(k):
    ps = json.load(open(f'{T}/pieces_{k}/pieces.json'))
    return sorted(ps, key=lambda p: (round((p['y'] + p['h'] / 2) / 400), p['x']))  # เรียงตามแถว แล้วซ้าย->ขวา

NAMES = {
    'tk1': ['inn', 'weapon_shop', 'item_shop', 'house'],
    'tk2': ['guild_hall', 'fountain', 'waystone', 'quest_board'],
    'tk3': ['lamp', 'tree', 'pine', 'bush', 'stall', 'barrels', 'fence', 'well', 'bench'],
}
for k, names in NAMES.items():
    ps = pieces(k)
    assert len(ps) == len(names), (k, len(ps))
    for p, n in zip(ps, names):
        shutil.copy(f"{T}/pieces_{k}/{p['file']}", f'{KIT}/{n}.png')

# TK-2b: ภาพมีคริสตัลวางบนน้ำพุ -> ตัดเอาเฉพาะคริสตัล (แถวโปร่งใสแถวแรกที่คั่นระหว่างสองส่วน)
c = np.array(Image.open(f"{T}/pieces_tk2b/{pieces('tk2b')[0]['file']}").convert('RGBA'))
rows = (c[..., 3] > 128).sum(1)
lo, hi = int(len(rows) * .3), int(len(rows) * .75)
cut = lo + int(np.argmin(rows[lo:hi]))  # ปลายล่างคริสตัล = แถวที่แคบที่สุด (ภาพที่ได้คริสตัลแตะน้ำพุ)
cr = c[:cut].copy(); cr[-6:, ..., 3] = 0; ys, xs = np.where(cr[..., 3] > 0)
Image.fromarray(cr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]).save(f'{KIT}/waystone_crystal.png')

# TK-5: ชิ้นเล็กแตกเป็นหลายก้อน -> รวมตามช่องกริด 4x4
names5 = ['tuft_0', 'tuft_1', 'tuft_2', 'tuft_3', 'pebbles_0', 'pebbles_1', 'dirt_0', 'dirt_1',
          'leaves_0', 'leaves_1', 'flowers_0', 'flowers_1', 'stones_0', 'stones_1', 'puddle', 'moss']
im = np.array(Image.open(f'{T}/sheets/tk5_sheet.png').convert('RGB')).astype(np.float32)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
alpha = np.clip((0.62 - np.clip(((r + b) / 2 - g) / 255, 0, 1)) / .25, 0, 1)
fix = np.clip(np.minimum(r, b) - g, 0, None) * (1 - alpha); im[..., 0] -= fix; im[..., 2] -= fix
rgba = np.dstack([np.clip(im, 0, 255), alpha * 255]).astype(np.uint8)
H, W = alpha.shape
for i, n in enumerate(names5):
    gx, gy = i % 4, i // 4
    cell = rgba[gy * H // 4:(gy + 1) * H // 4, gx * W // 4:(gx + 1) * W // 4]
    ys, xs = np.where(cell[..., 3] > 128)
    Image.fromarray(cell[max(0, ys.min() - 3):ys.max() + 4, max(0, xs.min() - 3):xs.max() + 4]).save(f'{KIT}/decal_{n}.png')

# TK-4: ชีท 3x3 พื้น 9 แบบ (sheets/tk4_grid.png) -> หาช่องจากร่องชมพู ครอปเข้าใน แล้วทำให้ต่อกันไร้รอย
GROUNDS = ['grass', 'grass_dark', 'cobble', 'plaza', 'dirt', 'sand', 'forest', 'water', 'dock']
def seamless(t, f=.18):
    """เลื่อนครึ่งภาพให้รอยต่อมาอยู่กลาง แล้วผสมกับภาพเดิมด้วยมาสก์กากบาท -> ขอบซ้าย/ขวา บน/ล่าง ต่อกันสนิท"""
    t = t.astype(np.float32); h, w = t.shape[:2]
    sh = np.roll(t, (h // 2, w // 2), (0, 1))
    wx = np.clip(np.abs(np.arange(w) - w / 2) / (w * f), 0, 1); wy = np.clip(np.abs(np.arange(h) - h / 2) / (h * f), 0, 1)
    m = np.minimum(wy[:, None], wx[None, :])[..., None]          # 0 = ใกล้รอยต่อกลาง -> ใช้ภาพเดิม
    return (t * (1 - m) + sh * m).clip(0, 255).astype(np.uint8)
g4p = f'{T}/sheets/tk4_grid.png'
if os.path.exists(g4p):
    g4 = np.array(Image.open(g4p).convert('RGB')).astype(np.float32)
    notmag = ((g4[..., 0] + g4[..., 2]) / 2 - g4[..., 1] < 90).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.morphologyEx(notmag, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8)), 8)
    sw = sorted([st[i] for i in range(1, n) if st[i][4] > g4.shape[0] * g4.shape[1] * .03], key=lambda q: (round(q[1] / (g4.shape[0] / 4)), q[0]))
    assert len(sw) == len(GROUNDS), f'เจอ {len(sw)} ช่อง ต้องได้ {len(GROUNDS)}'
    for (x, y, w, h, _), name in zip(sw, GROUNDS):
        i = int(min(w, h) * .04); t = g4[y + i:y + h - i, x + i:x + w - i].astype(np.uint8)
        out = t if name == 'plaza' else seamless(t)  # ลานเป็นลายวงกลมชิ้นเดียว -> ไม่ทำต่อกัน (เกมยืดวางทั้งลาน)
        Image.fromarray(out).save(f'{KIT}/ground_{name}.png'); print('ground', name, t.shape[:2])
print('kit:', len(os.listdir(KIT)), 'files')
