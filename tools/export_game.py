"""ส่งออกจากสตูดิโอ (สอน AI) -> โฟลเดอร์เกม (Re-Ask)
usage: python tools/export_game.py [game_dir=../Re-Ask] [--clips path/to/clips.json]
- คัดลอกเฉพาะไฟล์ที่เกมใช้จริง (ไม่มีคลิป/ชีทดิบ)
- ไม่แตะโค้ดเกม (index.html, game/) — เขียนทับแค่ engine/ และ data/
- --clips: ไฟล์ที่ได้จากปุ่ม "ส่งออก JSON" ใน Pose Studio -> data/clips.json
"""
import sys, os, shutil, json

here = os.path.dirname(os.path.abspath(__file__))
studio = os.path.dirname(here)
args = sys.argv[1:]
clips = args[args.index('--clips') + 1] if '--clips' in args else None
pos = [a for a in args if not a.startswith('--') and a != clips]
game = os.path.abspath(pos[0] if pos else os.path.join(studio, '..', 'Re-Ask'))
n = 0
def cp(src, dst):
    global n
    s = os.path.join(studio, src); d = os.path.join(game, dst)
    if not os.path.exists(s): print('  ! ไม่พบ', src); return
    os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copy2(s, d); n += 1

# engine (โค้ดชุดเดียวกับสตูดิโอ)
cp('engine/rig.js', 'engine/rig.js')
cp('vfx/vfx_runtime.js', 'engine/vfx_runtime.js')
# characters / outfits
PARTS = ['head', 'head_hair', 'torso', 'arm_upper', 'arm_lower', 'leg_upper', 'leg_lower', 'shoulder']
for name, src in [('dark_knight', 'assets/outfits/dark_knight'), ('knight', 'assets/characters/knight')]:
    for p in PARTS + [g + '_glow' for g in ['torso', 'shoulder', 'arm_lower', 'leg_upper']]:
        if os.path.exists(os.path.join(studio, src, 'parts', p + '.png')):
            cp(f'{src}/parts/{p}.png', f'data/characters/{name}/{p}.png')
    cp(f'{src}/variants/leg_lower_3.png', f'data/characters/{name}/leg_lower_3.png')
# hero2 (ชีท C2 v2 แบ่งแขน/ขาด้วย tools/split_limbs.py — ขนาดชิ้นอยู่ใน game/main.js เป็น spec ของชุด)
for p in ['head', 'torso', 'armF_u', 'armF_l', 'armB_u', 'armB_l', 'legF_u', 'legF_l', 'legB_u', 'legB_l', 'legF_l_front_toe']:   # ชีท C2 v2
    cp(f'assets/characters/hero2/parts/{p}.png', f'data/characters/hero2/{p}.png')
# แมพเมือง: พื้นอบ + layout (จากปุ่ม "ส่งออกเข้าเกม" ใน Map Lab) + ภาพของที่ใช้จริง
cp('assets/maps/town/export/town_ground.jpg', 'data/maps/town/ground.jpg')
cp('assets/maps/town/export/town_layout.json', 'data/maps/town/layout.json')
lay = os.path.join(studio, 'assets/maps/town/export/town_layout.json')
if os.path.exists(lay):
    kinds = sorted({o['k'] for o in json.load(open(lay, encoding='utf-8'))['objects']})
    for k in kinds + ['waystone_crystal']:
        for suf in ['', '_night', '_glow']:
            if os.path.exists(os.path.join(studio, f'assets/maps/town/kit/{k}{suf}.png')):
                cp(f'assets/maps/town/kit/{k}{suf}.png', f'data/maps/town/kit/{k}{suf}.png')
# gear
cp('assets/weapons/greatsword/greatsword.png', 'data/gear/greatsword.png')
cp('assets/weapons/greatsword/greatsword_glow.png', 'data/gear/greatsword_glow.png')
cp('assets/helmets/dragon_skull/open_cut.png', 'data/gear/helmet_open.png')
cp('assets/helmets/dragon_skull/open.png', 'data/gear/helmet_mask.png')
cp('assets/helmets/dragon_skull/closed.png', 'data/gear/helmet_closed.png')
cp('assets/helmets/dragon_skull/closed_glow.png', 'data/gear/helmet_closed_glow.png')
# vfx
for q in ['beast', 'burst', 'thorns']:
    for ext in ['.png', '_glow.png', '.json']:
        cp(f'assets/vfx/dark/seq/{q}{ext}', f'data/vfx/dark/seq/{q}{ext}')
for k, cnt in [('rock', 8), ('spark', 6), ('smoke', 6)]:
    for i in range(cnt):
        for g in ['', '_glow']:
            cp(f'assets/vfx/dark/sprites/{k}_{i}{g}.png', f'data/vfx/dark/sprites/{k}_{i}{g}.png')
# clips
if clips:
    json.load(open(clips, encoding='utf-8'))
    os.makedirs(os.path.join(game, 'data'), exist_ok=True)
    shutil.copy2(clips, os.path.join(game, 'data', 'clips.json')); n += 1
print(f'exported {n} files -> {game}')
