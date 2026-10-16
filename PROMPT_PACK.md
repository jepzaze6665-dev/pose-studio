# แผนทำงานร่วม + ชุด Prompt (ตัวละคร & VFX)

> คุณ = ฝ่ายภาพ (เจน AI + คัดเลือก + เกลา) · ผม = ฝ่ายระบบ (rig, shader, โค้ดเกม, เครื่องมือ)
> ทุก prompt เขียนเป็นภาษาอังกฤษ เพราะ AI เจนภาพส่วนใหญ่เข้าใจดีกว่า ส่วนคำอธิบายเป็นไทย
> ทดสอบชิ้นส่วนได้ทันทีโดยลาก PNG ลงใน [rig/rig_lab.html](rig/rig_lab.html)

---

## 1. แบ่งงานกันยังไง

| ขั้น | คุณทำ | ผมทำ | ส่งต่อด้วย |
|---|---|---|---|
| A. ล็อคสไตล์ | เจน 3–5 ภาพตามบล็อก Style Lock เลือก 1 | ปรับบล็อก prompt ตามผล | ภาพที่เลือก → `assets/style/` |
| B. ตัวละครต้นแบบ | เจนตัวละคร 1 ตัว (prompt C1) | ตรวจสัดส่วนว่า rig ได้ไหม | `assets/characters/<ชื่อ>/master.png` |
| C. แยกชิ้นส่วน | เจนชีทชิ้นส่วน (C2) → ตัดพื้นชมพู → ตั้งชื่อไฟล์ | กำหนดจุดหมุน + ลองใน Rig Lab | `.../parts/*.png` |
| D. แก้บุคลิก | เจนขาหน้า 4 แบบ (C3) | ใส่ลองในท่ายืน ให้คะแนน "ความมั่นใจ" | `.../variants/leg_lower_1..4.png` |
| E. ชุด/หมวก/อาวุธ | เจนตามแม่แบบ (C4–C6) | ทำ editor จัดหมวก/อาวุธ | `assets/outfits/...` |
| F. ชั้นแสง | เจนชั้นเรือง (C7) | เขียนโค้ดให้เต้นตามจังหวะ | `*_glow.png` |
| G. VFX | เจนคอนเซ็ปต์ + พาเลต (V1–V3) | แปลงเป็น shader ตามสูตร 8 ขั้น | `assets/vfx/<ชื่อ>/` |
| H. ชิ้นเอฟเฟคเล็ก | เจนสแลช/ประกาย/ควันบนพื้นดำ (V4) | ทำ particle + bloom | `assets/vfx/sprites/` |

**กฎทอง:** เจนหลายแบบ → **ทดสอบในเกมที่ขนาดจริง** → ค่อยตัดสิน (ไม่ตัดสินจากภาพเต็มจอ)

---

## 2. บล็อก Style Lock (แปะท้ายทุก prompt) — v2 ล็อกแล้ว 2026-10-16
ภาพอ้างอิงหลัก: **`assets/style/char_anchor.png`** (ตัวละคร) + **`assets/style/town_anchor.png`** (โลก) — แนบทั้งสองทุกครั้ง

```
STYLE LOCK v2:
- Art: 2D chibi HD game art, anime-style face, same style as the attached reference character.
- Proportions: about 2.7 heads tall, big head, large expressive eyes with one white highlight, small nose and mouth.
- Outline: dark navy #1b1830, even 3px on the outer silhouette, thinner 1.5px on inner lines.
- Shading: flat cel shading, 1 base + 2 shadow tones + 1 hard highlight, no soft gradients, no texture noise.
- Light: single light from TOP-LEFT, rim highlight on the top/left edges.
- View: 3/4 view facing right, full body, feet flat on an invisible ground line.
- Palette: slightly desaturated medieval colors (navy, leather brown, steel, warm gold trims);
  only ONE glowing accent per character (e.g. cyan rune or blade edge).
- Detail level: readable at 120px tall; medium detail on clothes, no tiny patterns.
- Background: flat pure magenta #FF00FF, no ground shadow, no text, no magenta on the character.
```
- ถ้าเครื่องมือรองรับ **ภาพอ้างอิง** ให้แนบภาพสไตล์ที่เลือกไว้ทุกครั้ง (สำคัญกว่าตัวหนังสือ)
**แขนงของ Chibi** (เปลี่ยนแค่บรรทัด VARIANT ต่อท้าย Style Lock หลัก — โครงสร้างเดิม rig เดิม)
| แขนง | VARIANT line |
|---|---|
| A ฮีโร่สดใส (ปัจจุบัน) | `VARIANT: heroic and bright, warm saturated colors, confident expression.` |
| B น่ารักซอฟต์ | `VARIANT: extra cute, 2-head-tall, round soft shapes, pastel palette, sparkly eyes, warm brown outline instead of navy.` |
| C ดาร์กคูล | `VARIANT: edgy dark chibi, sharp angular shapes, cool dark palette with one glowing accent color, narrow serious eyes.` |
| D ตลกฮา | `VARIANT: comedic chibi, exaggerated huge head and tiny body, dot eyes, simple bold shapes, playful colors.` |
| E แฟนตาซีหรู | `VARIANT: premium fantasy chibi, ornate gold trims, gems and capes, rich jewel-tone palette, glossy highlights.` |
| F สัตว์/มอนสเตอร์ | `VARIANT: creature chibi for enemies and pets, same outline and shading rules, animal or monster anatomy.` |
- ใช้ผสมได้: ผู้เล่น = A/E, ศัตรู = C/F, NPC = B/D — เส้นขอบ/แสง/มุมกล้องเหมือนกันทั้งหมด จึงอยู่ในเกมเดียวกันได้ไม่หลุด
- กฎ: **ห้ามเปลี่ยน** มุม 3/4, ทิศแสง, ความหนาเส้น, จำนวนโทนเงา — เปลี่ยนได้แค่ สัดส่วน รูปทรง พาเลต และบุคลิก

**ทางเลือก: Style Lock แบบพิกเซล**
```
STYLE: pixel art game sprite, character about 64 pixels tall, chunky clean pixels on a strict grid,
limited palette of max 24 colors, 1-pixel dark outline, no anti-aliasing, no blur, no gradients,
flat 2-tone shading with light from top-left, 3/4 view facing right, chibi proportions.
```
> AI มัก "ปลอม" พิกเซล (เม็ดไม่เท่ากัน ไม่ตรงกริด) → ส่งมาให้ผมแปลงเข้ากริดจริงก่อนใช้
> หรือใช้ชิ้นส่วน HD เดิม แล้วกดโหมดพิกเซลใน Rig Lab ซึ่งจะแปลงให้อัตโนมัติ

- อย่าแก้บล็อกนี้ทีละ prompt — แก้ที่นี่ที่เดียว แล้วใช้กับทุกงาน

---

## 3. Prompt ตัวละคร

### C1 — ตัวละครต้นแบบ (master)
```
Full-body game character, young adventurer, standing in a relaxed neutral pose facing right,
arms slightly away from the body, legs slightly apart, both hands visible, feet flat on the ground,
holding nothing. Plain solid light gray background. Character centered, full body visible with margin.
[STYLE LOCK]
```
> ทำไมท่าแบบนี้: แขนกาง/ขาแยกเล็กน้อย = แยกชิ้นง่าย ไม่มีส่วนไหนบังกัน · ห้ามถือของ = อาวุธแยกชิ้นทีหลัง
> เปลี่ยนคำว่า `young adventurer` เป็นตัวละครที่อยากได้

### C2 — ชีทชิ้นส่วน (สำคัญที่สุด)
แนบ master.png เป็นภาพอ้างอิง
```
Character parts sheet for 2D skeletal animation, based on the reference character.
Separate pieces laid out in a grid with wide gaps, nothing overlapping, on a flat pure magenta background (#FF00FF):
1 head (with hair, no neck), 2 torso (neck stump to hips, no arms, no legs),
3 upper arm (shoulder to elbow), 4 lower arm with hand (elbow to fingertips, hand in a loose fist),
5 upper leg (hip to knee), 6 lower leg with boot (knee to sole).
Every piece drawn straight vertical, joint end on top. Joint ends drawn ROUNDED and slightly extended
so they can hide under the neighbouring piece. Same scale, colors and outline as the reference.
No magenta anywhere on the character. [STYLE LOCK]
```
**หลังเจน:**
1. ตัดพื้นชมพูออก (magic wand / remove background / ผมเขียนสคริปต์ตัดให้ได้)
2. ครอปแต่ละชิ้นให้ชิดขอบ แล้วบันทึกเป็น PNG พื้นใส
3. ตั้งชื่อไฟล์ **ตามนี้เท่านั้น**: `head.png torso.png arm_upper.png arm_lower.png leg_upper.png leg_lower.png`
4. ลากไฟล์ทั้งหมดลงในกล่องของ Rig Lab → ดูว่าตอนหมุนข้อต่อมีรอยไหม

**จุดหมุนที่ Rig Lab คาดไว้** (ถ้าไม่ตรง บอกผม ผมแก้ค่าให้):
| ไฟล์ | จุดหมุนอยู่ที่ | ตำแหน่งในภาพ |
|---|---|---|
| head | คอ | กลางล่าง (สูง 88%) |
| torso | สะโพก | กลางล่าง (สูง 90%) |
| arm_upper | ไหล่ | กลางบน (15%) |
| arm_lower | ศอก | กลางบน (12%) |
| leg_upper | สะโพก | กลางบน (12%) |
| leg_lower | เข่า | กลางบน (10%) |
| weapon | ด้ามที่มือจับ | กลาง (82% จากบน), ใบดาบชี้ขึ้น |

### C2 v2 — ชีทชิ้นส่วนแบบ Night Camp (แนะนำ · แขน/ขาชิ้นเดียว)
แนบ master + `char_anchor.png`
```
Character parts sheet for 2D skeletal animation, based on the reference character, flat pure magenta background (#FF00FF),
exactly 6 separate pieces in 2 rows with wide gaps, same scale for all pieces as in the reference (do NOT enlarge any piece):
row 1: 1 head with all hair, no neck; 2 torso: neck stub on top, collar, cape/scarf, belt and pouch, and the top of the
shorts/hips at the bottom, shoulders rounded, NO arms, NO legs.
row 2: 3 front arm as ONE piece (rounded sleeve cap at the shoulder -> forearm -> gloved fist), 4 back arm (same as 3),
5 front leg as ONE piece (rounded pants top -> knee -> boot), 6 back leg (same as 5).
Every limb hangs straight down, joint end on top drawn as a smooth rounded capsule so it hides under the torso.
Shoulder armor or pads belong to the ARM piece only (not drawn on the torso). No mannequin pegs, no sockets, no gray stubs.
Arms and legs as wide as in the reference. Simple shapes, thick outline, readable at small size. [STYLE LOCK]
```
> ระบบเดิมตัดแขน/ขาเป็น 2 ท่อน → ใช้ชีทนี้ได้เลย: ผมตัดที่ 45% (ศอก) / 47% (เข่า) ให้อัตโนมัติ (หรือทำงอแบบ mesh ทีหลัง)

### C3 — ขาหน้า 4 แบบ (ทริคเปลี่ยนบุคลิก)
แนบ `leg_lower.png`
```
Four variations of the same lower leg with boot, side by side on magenta background (#FF00FF).
Identical length, width, knee and boot design. ONLY the foot direction changes:
1 toe pointing slightly toward viewer, 2 toe turned halfway toward viewer,
3 toe pointing straight at the viewer, 4 toe pointing outward to the left. [STYLE LOCK]
```
> ผมจะใส่ทีละแบบในท่ายืนให้ดูทั้งตัว แล้วเราเลือกแบบที่ "ยืนมั่นใจ" ที่สุด

### C4 — ชุดใหม่บนแม่แบบเดิม
แนบชีทชิ้นส่วนเดิม (C2) **และ** ภาพคอนเซ็ปต์ชุด (ถ้ามี)
```
Redraw this exact parts sheet wearing a [heavy knight armor / dark berserker armor / wizard robe] outfit.
Keep every piece EXACTLY the same size, position, angle and joint location as the reference sheet,
only change clothing and materials. Magenta background (#FF00FF). [STYLE LOCK]
```
> หัวใจคือ "จุดข้อต่อตรงกันทุกชุด" ถ้าเจนแล้วสัดส่วนเปลี่ยน ให้เจนใหม่ อย่าใช้
> ถ้าเป็นชุดยาว/กระโปรง: ขอ `torso` ที่รวมกระโปรงคลุมหัวขาไว้ (ทริคกระโปรงจกตา)

### C5 — หมวก 2 สถานะ
```
Two versions of the same [dragon-skull helmet], side view facing right, on magenta background:
left = visor OPEN showing where the face would be, right = visor CLOSED with glowing red eye slits.
Same size and position in both. Only the helmet, no head. [STYLE LOCK]
```

### C6 — อาวุธ (หลัก 6 ชั้นแบบศิลปิน)
```
Single [greatsword] game item, vertical, blade pointing up, grip at the bottom, plain black background.
Paint it in layers like an artist: strong form shadow with light from top-left, thick chunky metal with
dark crevices, cool gray-to-black base colors, wavy reflective banding on the blade,
crisp white highlight along the edge, glowing red cracks. Bold thick outline, large simple shapes
readable at small size. [STYLE LOCK]
```
> AI มักให้รายละเอียดมากเกิน → ย่อดูที่ ~80px สูง ถ้ากลายเป็นนอยส์ ให้เกลา: เส้นขอบหนา, ลบลายยิบ, ยกความสว่าง

### C7 — ชั้นแสงเรือง (แยกจากภาพหลัก)
แนบภาพอาวุธ/เกราะที่เสร็จแล้ว
```
Using the reference image, output ONLY the glowing red cracks, in exactly the same positions,
on a pure black background. Everything that does not glow must be black.
Crack color: deep red edges -> orange -> pale yellow core.
```
> ตั้งชื่อ `<ชิ้น>_glow.png` · ผมจะซ้อนแบบ additive + bloom แล้วทำให้เต้นเป็นจังหวะหัวใจ

---

## 3.5 Prompt มอนสเตอร์ (สูตรสไลม์ Night Camp → ดู knowledge/MONSTER_RIG.md)

### MR1 — กระต่ายมอน: ตัวเต็ม (master · เจน 3–4 ภาพ เลือก 1)
```
Game enemy monster: a small horned forest rabbit, chibi creature, round fluffy body,
very long floppy ears, one short curved horn on the forehead, big round eyes, tiny fluffy tail,
big hind feet, short front paws. Cute but slightly mischievous expression.
Fur: cream white with soft brown patches; horn: pale bone color with ONE glowing cyan tip (only glowing accent).
Pose: standing on all fours, side 3/4 view facing right, ears relaxed hanging back, whole body visible.
Size reference: about half the height of the hero character.
[แปะ STYLE LOCK v2 + VARIANT F]
```

### MR2 — กระต่ายมอน: ชีทชิ้นส่วน (สำหรับริก · ชีท 4x3)
```
Character parts sheet of THE SAME rabbit monster as the attached reference image (same colors, same outline, same scale).
Grid 4 columns x 3 rows, each part centered in its own cell, wide flat magenta #FF00FF gutters between cells,
no part touching another, every part complete (nothing cut off), all parts at the SAME scale as the reference.
Row 1: (1) body WITHOUT head, ears, legs and tail — fill the areas where they attach with fur, smooth rounded joints
       (2) head WITHOUT ears and WITHOUT eyes — fill the eye area with plain fur/skin, keep nose and mouth
       (3) front ear, long and floppy, straight, attach end rounded
       (4) back ear, same as front ear but slightly darker (in shadow)
Row 2: (5) eyes OPEN (pair of eyes only, no head)  (6) eyes CLOSED/hurt (curved lines)
       (7) eyes ANGRY (sharp, glaring)  (8) horn alone with its glowing tip
Row 3: (9) front paw (front leg), straight, rounded top  (10) back front paw, slightly darker
       (11) big hind leg with foot, straight, rounded top  (12) fluffy round tail
Side view facing right for every part. No shadows on the ground, no text, no numbers.
[แปะ STYLE LOCK v2 + VARIANT F]
```

**ทำไมแยกแบบนี้** (สูตรเดียวกับสไลม์)
- หู 2 ข้าง + หาง = ปลายโซ่ → ใส่ **spring bone** ให้หูดีดตามตอนกระโดด (เหมือนปลายหยดน้ำ/ใบบัว)
- ตา 3 แบบ = สลับภาพตามท่า: ลืม (idle) · หลับ (hit/die) · โกรธ (attack)
- ลำตัว/หัว "แบบไม่มีชิ้นบน" = เนื้อเติมใต้ชิ้น ขยับแล้วไม่เห็นรู
- ท่า 5 ท่า: idle (หายใจ จมูกกระดิก หูแกว่ง) · hop (ย่อ → กระโดด หูสะบัด) · attack (ก้มหัวพุ่งเอาเขาขวิด) · hit · die (ล้มตะแคง จางหาย)

**เช็คก่อนส่ง:** ครบ 12 ช่อง · ชิ้นไม่ติดกัน · หูยาวตรงไม่งอ · ลำตัวไม่มีหัว/ขาติดมา · สีตรงกับ MR1 · ตั้งชื่อไฟล์ `image-rabbit-master.png` / `image-rabbit-parts.png` วางที่ราก repo

## 4. Prompt VFX

VFX ส่วนใหญ่ **ผมสร้างด้วยโค้ด** (สูตร 8 ขั้น ดู [vfx/vfx_lab.html](vfx/vfx_lab.html)) คุณช่วยได้ 3 แบบ: ให้ทิศทางภาพ, ล็อคสี, และวาดชิ้นเล็กที่โค้ดทำยาก

### V1 — คอนเซ็ปต์ 3 จังหวะ (เกิด → ยืน → ระเบิด)
```
VFX concept sheet for a 2D game, three panels left to right on dark background:
[poison bubble shield] around a small chibi character -
1 forming (appearing), 2 stable idle state, 3 bursting / breaking apart.
Anime-style hand-drawn effect, flat color bands (no smooth gradients), bold shapes,
glow only on the brightest edges. Top-down 3/4 camera at 20 degrees.
```
> ส่งมาแค่ภาพเดียว ผมจะ "แกะ" ว่าใช้ตัวต่อไหน (noise / voronoi / dissolve / rim) แล้วทำเป็น shader

### V2 — พาเลต 5 สี
```
A single horizontal color palette strip of exactly 5 flat color swatches for a [poison] magic effect,
ordered darkest to lightest, high saturation in the middle swatches, no gradients, no text.
```
> หรือส่งรหัสสีมาเลย 5 ค่า — นี่คือ "สีเรียบ 5 ขั้น" ที่ทำให้ดูวาดมือ

### V3 — ภาพอ้างอิงลวดลาย (ถ้าอยากได้ลายเฉพาะ)
```
Seamless tileable pattern texture of [swirling poison smoke / cracked ice crystals / runic circle],
black and white only, high contrast, flat shapes, no shading.
```

### V4 — ชิ้นเอฟเฟคเล็ก (สำหรับ particle)
```
2D game VFX sprite sheet on pure black background, separated with wide gaps:
6 sword slash arcs (thin to thick), 6 hit spark bursts, 4 dust puffs, 4 small flame wisps.
White and pale-yellow core with colored edges, anime style, flat bands, no background.
```
> พื้น **ดำ** (ไม่ใช่ชมพู) เพราะเอฟเฟคจะซ้อนแบบ additive — สีดำ = โปร่งใสอัตโนมัติ

---

## 4.5 Sprite VFX (เฟรมต่อเนื่อง) — ชุด Dark
กฎร่วมทุก prompt (ช่วยให้เฟรมไม่เพี้ยน):
- **กริดตายตัว** บอกจำนวนแถว×คอลัมน์ + "each frame in its own equal square cell"
- **จุดยึดเดียวกันทุกเฟรม** เช่น "ground line at the bottom of every cell, centered"
- **ขนาดและสีเดียวกัน** "same scale, same palette in every frame"
- **บอกเรื่องราวทีละเฟรม** เพื่อให้มีจังหวะ ง้าง → ปะทุ → ค้าง → สลาย
- แนบภาพเดี่ยวเดิมเป็น **ภาพอ้างอิง** ทุกครั้ง

**VS-1 หนามทมิฬปะทุ (8 เฟรม)**
```
2D game VFX sprite sheet, 4 columns x 2 rows, 8 frames, each frame in its own equal square cell,
pure black background, same scale and palette in every frame, ground line at the bottom of every cell, centered.
Animation of dark thorns erupting from the ground:
1 ground cracks with faint violet glow, 2 cracks widen and glow brighter, 3 thorn tips break through,
4 a cluster of thorns shoots up halfway, 5 full height with brightest violet rim and flying rock bits,
6 hold full height, 7 thorns crumble from the tips into black dust, 8 only fading cracks remain.
Thorns: solid near-black purple body, thin glowing violet rim, sharp jagged tips. Anime hand-drawn style, flat color bands.
```

**VS-2 อสูรเงาพุ่ง (6 เฟรม · ท่าหลัก)**
```
2D game VFX sprite sheet, 3 columns x 2 rows, 6 frames, equal square cells, pure black background,
the SAME shadow dragon head made of black smoke in every frame (use the reference image), facing right,
same size and colors, head anchored at the same point in each cell.
1 coiled back, mouth closed, eye glowing, 2 pulling back further, smoke tendrils curling forward,
3 lunging forward stretched long, mouth wide open, tendrils streaming behind,
4 jaws snapping shut, brightest violet rim, white-hot eye, 5 smoke bursting apart at the edges,
6 dissolving into black smoke wisps.
Solid near-black body, glowing violet rim, anime style, flat shading.
```

**VS-3 สแลช X ม่วง (6 เฟรม)**
```
2D game VFX sprite sheet, 3 columns x 2 rows, 6 frames, equal square cells, pure black background,
same scale in every frame, slash centered in each cell.
Animation of an X-shaped double sword slash:
1 thin white line starts at the top left, 2 first crescent slash sweeps diagonally, white-hot core,
3 first slash full, second crescent begins crossing it, 4 both slashes form a bright X with violet sparks,
5 X fades to violet with breaking edges, 6 thin violet afterglow wisps.
White-hot core fading to violet then dark purple edge, anime brush stroke, flat color bands, tapered ends.
```

**VS-4 ระเบิดความว่าง (8 เฟรม)**
```
2D game VFX sprite sheet, 4 columns x 2 rows, 8 frames, equal square cells, pure black background,
same scale and palette, burst centered in each cell.
Animation of a dark void explosion on hit:
1 tiny white-hot spark, 2 bright white-violet flash with a thin shock ring,
3 black smoke ball bursts out with a violet rim, 4 smoke ball at full size with ragged edges and flying dark shards,
5 holes start tearing through the smoke, 6 smoke breaks into chunks,
7 scattered black wisps and violet sparks, 8 almost gone, faint wisps.
Solid near-black smoke, glowing violet rim, white core only in early frames, anime style, flat shading.
```

**VS-5 พายุหมุนเงา (8 เฟรม · วนลูป)**
```
2D game VFX sprite sheet, 4 columns x 2 rows, 8 frames, equal square cells, pure black background,
same scale and position, LOOPING animation (frame 8 flows back into frame 1).
A dark whirlwind tornado: funnel of swirling gray-white wind bands with dark gaps, violet glow at the base,
small black rock shards orbiting. Each frame rotates the bands slightly further.
Flat 3-tone gray-white bands, anime style, no gradients.
```

**VS-7 อสูรเงาท่าบิน (4 เฟรม · วนลูป · สำหรับ Sprite + Code)**
แนบเฟรมจาก VS-2 เป็นภาพอ้างอิง
```
2D game VFX sprite sheet, 4 columns x 1 row, 4 frames, equal square cells, pure black background,
the SAME shadow dragon head made of black smoke as the reference, facing right, mouth closed,
head CENTERED in every cell at the same size and position, LOOPING animation (frame 4 flows into frame 1):
smoke tendrils and mane ripple backward in a wave, head bobs slightly up and down, eye glows steadily.
Solid near-black body, glowing violet rim light, anime style, flat shading. No numbers or labels.
```
> สำคัญ: หัวต้องอยู่กลางช่องทุกเฟรม เพราะโค้ดจะหมุนและพาบินตามเส้นโค้ง

**VS-6 เศษชิ้นเล็ก (เฟรมสั้น 4 เฟรม × 3 แบบ)**
```
2D game VFX sprite sheet, 4 columns x 3 rows, equal square cells, pure black background.
Row 1: a black smoke puff appearing, growing, breaking, vanishing (4 frames).
Row 2: a violet star spark flashing in and fading (4 frames).
Row 3: a dark rock shard spinning (4 rotation frames).
Near-black fill with thin violet rim, anime style, flat color.
```

## 4.6 ชุดของแมพ: เมืองแรก v2 (ล็อกสไตล์เข้ม)
ขั้นตอน: **M0 เจนภาพตั้งต้น (Style Anchor) → เลือก 1 ภาพ → แนบภาพนั้นทุก prompt ที่เหลือ** (ภาพอ้างอิงสำคัญกว่าตัวหนังสือ)
แนบภาพตัวละครอัศวินด้วยทุกครั้ง เพื่อล็อกสเกล · ชื่อไฟล์ชิ้นส่วนใช้ชื่อเดิม (guild_hall, inn, ...) ระบบตัด/normal/ไฟกลางคืนจะทำงานต่อได้ทันที

### บล็อกล็อกสไตล์ (แปะท้ายทุก prompt ในหมวดนี้ · ห้ามแก้ทีละ prompt)
```
TOWN STYLE LOCK:
- Art: 2D hand-painted chibi HD game art, same style as the attached reference images.
- Outline: dark navy #1b1830, even 3px weight on outer silhouette, 1.5px on inner lines.
- Shading: flat cel shading, exactly 1 base + 2 shadow tones + 1 highlight, no gradients, no texture noise.
- Light: single sun from TOP-LEFT, highlights on top/left faces, shadows on bottom/right faces.
- Camera: 3/4 top-down, looking down 35 degrees, NO perspective (parallel / isometric-like), front faces visible.
- Scale: a door is exactly as tall as the 2.5-head chibi knight; a 2-floor building = 2.5 doors tall.
- Palette (stay inside it): roofs terracotta #b5543c / slate teal #3f6b73 / moss green #5f7d3a,
  walls cream plaster #efe1c4 with timber #6b4a32, stone #a39a8c, wood #8a5a36, metal iron #4a4f5c,
  foliage #6f9a52 / #4e7a3c, water #4fb3c9, accent gold #e0b04a. Overall slightly desaturated, warm and cozy.
- Windows UNLIT (dark blue glass #2c3a5c), no fire or glow unless asked.
- Output: every object separate with wide gaps, flat pure magenta background #FF00FF,
  no ground shadow, no ground under objects, no text, no watermark, no magenta inside objects.
```

### M0 — ภาพตั้งต้นล็อกสไตล์ (เจน 3–5 ภาพ เลือก 1 · ไม่ได้ใช้ในเกม ใช้เป็นภาพอ้างอิงเท่านั้น)
```
Concept view of a small cozy medieval fantasy starting town for a 2D MMORPG: a round cobblestone plaza with a
stone fountain in the center, a large Job Guild hall behind it, an inn, a weapon shop and a potion shop around the plaza,
market stalls, street lamps, trees and flower bushes, four cobblestone roads leaving the plaza.
The chibi knight from the reference stands in the plaza for scale.
Use TOWN STYLE LOCK rules for art, outline, light, camera, scale and palette, but draw a full scene on grass (ignore the magenta rule).
```
> บันทึกภาพที่เลือกไว้ที่ `assets/style/town_anchor.png` แล้วแนบทุก prompt ด้านล่าง

### M1 — ภาพรวมทั้งเมือง (แผนผัง · ใช้เป็นเป้าหมายให้ Map Lab วางตาม)
```
Full overview of the whole starting town for a 2D MMORPG, wide 3:2 image, the entire map visible edge to edge,
same 3/4 top-down 35-degree camera (zoomed out, no perspective). Layout:
- Center: round cobblestone plaza with the three-tier fountain; Job Guild hall directly north of the plaza;
  teleport waystone south-east of the fountain; quest board north-west of the fountain.
- Around the plaza: inn (west-north), weapon shop (east-north), potion shop (west-south), red-white market stalls and benches.
- Four cobblestone roads leave the plaza: north, east, south, west, each lined with small houses on both sides
  and street lamps alternating sides.
- Exits at the map edges glowing with a soft blue circle: east road -> grassland, south road -> dark forest, west road -> harbor.
- Grass everywhere else with clusters of big round trees, flower bushes, two stone wells; wooden fence along
  the top and bottom edges with gaps where roads pass.
- Small chibi knight standing in the plaza for scale.
Use TOWN STYLE LOCK rules for art, outline, light, camera, scale and palette, but draw a full scene on grass (ignore the magenta rule).
```
> ภาพนี้ไม่ได้ตัดใช้ในเกม แต่ใช้ 2 อย่าง: (1) ล็อกโทนสีรวมของทั้งเมือง (2) ผมจะปรับใบสั่ง (RECIPE) ใน Map Lab ให้ผังตรงกับภาพนี้
> เซฟไว้ที่ `assets/style/town_overview.png`

### TK-1 อาคาร (4 ชิ้น · ชีท 2x2)
```
4 town buildings in a 2x2 grid: 1 inn / tavern, two floors, hanging wooden mug sign;
2 weapon & armor shop, one floor plus attic, anvil by the door, crossed-swords sign;
3 potion / item shop, round window, hanging bottle sign;
4 small residential house, one floor. All doors face the viewer.
[TOWN STYLE LOCK]
```
### TK-2 จุดสำคัญ (4 ชิ้น · ชีท 2x2)
```
4 town landmarks in a 2x2 grid: 1 Job Guild hall, the largest building, stone steps, two hanging banners;
2 round three-tier stone fountain with water; 3 teleport waystone: tall carved stone pillar with an empty socket on top
(NO crystal, crystal is a separate item); 4 wooden quest notice board with pinned papers.
[TOWN STYLE LOCK]
```
### TK-2b คริสตัลหินวาร์ป (1 ชิ้น)
```
1 floating rune crystal, pale blue, faceted, carved glowing rune line in the middle, sized to sit on top of the waystone.
[TOWN STYLE LOCK]
```
### TK-3 ของประดับ (8 ชิ้น · ชีท 4x2)
```
8 town props in a 4x2 grid: 1 iron street lamp post (lamp glass unlit), 2 big round shade tree,
3 flower bush, 4 market stall with red-white striped awning and goods, 5 barrels and crates cluster,
6 straight wooden fence segment (tileable left-right), 7 stone well with small wooden roof, 8 wooden bench.
[TOWN STYLE LOCK]
```
### TK-4 พื้นหลายแบบในภาพเดียว (ชีท 3x3 · 9 แบบ)
```
Ground texture sheet for a 2D fantasy MMORPG: a 3x3 grid of 9 separate SQUARE ground swatches,
each swatch the same size, separated by thick pure magenta (#FF00FF) gutters, with a magenta border around the whole sheet.
Each swatch is an independent SEAMLESS TILEABLE texture filling its square edge to edge (left edge continues into
right edge, top into bottom), seen from 3/4 top-down 35 degrees, no objects, no shadows, no lighting direction, even detail:
1 soft green grass with very few tiny flowers, 2 short darker grass, 3 warm cobblestone road (medium stones),
4 large flat plaza paving stones in a loose circular pattern, 5 packed dirt path, 6 sand,
7 dark forest floor with moss and needles, 8 shallow clear water, 9 wooden dock planks running left to right.
Stones and planks must be large and readable (about 6-8 stones across a swatch), not tiny noise.
[TOWN STYLE LOCK] (ignore its "separate objects" rule; magenta only in the gutters, never inside a swatch)
```
> ผมจะตัด 9 ช่องตามกริดเอง แล้วปรับขอบให้ต่อกันไร้รอยอีกชั้น (เผื่อ AI ทำไม่สนิท) → `ground_<ชื่อ>.png`
> ถ้าอยากได้มากกว่า 9 แบบ เปลี่ยนเป็น 4x4 แล้วเพิ่มรายการ (เช่น หิมะ ทุ่งดอกไม้ หินภูเขา) — ใช้ prompt เดิม

### TK-5 รายละเอียดพื้น (16 ชิ้น · ชีท 4x4)
```
16 small flat ground decals in a 4x4 grid, lying FLAT on the ground (no height), same 3/4 angle:
1-4 grass tufts of different sizes, 5-6 small pebble clusters, 7-8 soft dirt patches with irregular faded edges,
9-10 fallen leaves, 11-12 tiny flower patches, 13-14 loose cobblestones and cracks, 15 small puddle, 16 moss patch.
[TOWN STYLE LOCK]
```

### เช็คก่อนส่งให้ผม (ถ้าไม่ผ่าน เจนใหม่ อย่าแก้มือ)
- [ ] แสงมาจากซ้ายบนทุกชิ้น · เส้นขอบหนาเท่ากันทุกชีท
- [ ] มุมกล้องเท่ากัน (เห็นหลังคาและผนังหน้าในสัดส่วนเดียวกัน)
- [ ] วางอัศวินข้างประตูแล้วสูงเท่าประตูพอดี
- [ ] สีอยู่ในพาเลต · หน้าต่างไม่เปิดไฟ · พื้นหลังเป็น magenta ล้วน ไม่มีเงาบนพื้น

**ผมจะทำต่อเมื่อได้ภาพ:** ตัดชิ้น → ติดป้ายเกม (ชน/บัง/ส่องแสง) → normal map → ชั้นไฟกลางคืน → Map Lab (ใบสั่ง + กฎ + seed) → export เข้าเกม

---
## 4.7 หาสไตล์ตัวละครใหม่ (ก่อนทำ NPC / มอน)
ขั้นตอน: **S1 เทียบ 6 สไตล์ → เลือก 1 → S2 ทดสอบกับฉากเมือง → S3 เทียบทั้งครอบครัว (ฮีโร่+NPC+มอน) → ล็อก → ค่อยทำชีทชิ้นส่วน (C2)**
แนบ `assets/style/town_anchor.png` ทุกครั้ง เพื่อให้ตัวละครอยู่ในโลกเดียวกับเมือง

### S1 — ตัวละครเดียว 6 สไตล์ (ชีท 3x2)
```
Character style exploration sheet for a 2D fantasy MMORPG, 3x2 grid, the SAME young adventurer
(short messy brown hair, blue tunic, leather belt and boots, short sword) drawn in 6 different chibi art styles,
full body, 3/4 view facing right, standing idle pose, each on a flat pure magenta (#FF00FF) background:
1 bright heroic chibi, 2.5 heads tall, thick dark navy outline, flat 2-tone cel shading;
2 soft cute chibi, 2 heads tall, rounded shapes, pastel colors, warm brown outline;
3 sharp cool chibi, 3 heads tall, angular shapes, darker palette with one glowing accent;
4 painterly chibi, 2.5 heads tall, thin outline, soft painted shading like a storybook;
5 bold comic chibi, 2.5 heads tall, very thick outline, flat colors, strong silhouette;
6 premium fantasy chibi, 3 heads tall, ornate gold trims, glossy highlights, rich jewel colors.
Same character design, pose and size in all 6, so only the art style differs. Number each style small under it.
Light from top-left in all. Must fit the cozy medieval town in the reference image.
```

### S2 — ทดสอบในฉาก (สไตล์ที่เลือก)
```
The chosen character from the reference (style #N) standing in the town plaza from the second reference,
next to the fountain and a shop door, same 3/4 top-down camera. The door must be as tall as the character.
Check: outline weight, shading and colors of the character match the buildings.
```
> ถ้าตัวละคร "หลุด" จากฉาก (เส้นหนา/บางกว่า, สีสดกว่า) → ปรับบรรทัด STYLE ใน §2 แล้วเจน S1 ใหม่เฉพาะสไตล์นั้น

### S3 — ครอบครัวตัวละคร (ฮีโร่ + NPC + มอน ในสไตล์เดียว · ชีท 4x2)
```
Character lineup in the exact art style of the reference character, 4x2 grid, each full body on flat pure magenta (#FF00FF),
same 3/4 view facing right, same outline, shading and light from top-left, sizes relative to each other:
1 the hero (reference), 2 friendly shopkeeper NPC with apron, 3 old guild master NPC with staff and robe,
4 town guard NPC with spear and helmet, 5 small round slime monster (knee height), 6 forest wolf monster (waist height),
7 mushroom creature monster (knee height), 8 armored goblin miniboss (slightly taller than the hero).
Monsters use the same outline and shading rules but simpler shapes and one clear color theme each.
```
> ผ่านเมื่อ: ทั้ง 8 ตัววางรวมกันแล้วดูเป็นเกมเดียว · มอนอ่านออกจากเงาดำล้วน · ฮีโร่เด่นสุด
> ล็อกแล้ว: เซฟ `assets/style/char_anchor.png` + แก้บรรทัด STYLE ใน §2 ให้ตรงสไตล์ที่เลือก → ใช้กับ C1–C7 ต่อ

---
## 5. Checklist ก่อนส่งงานให้ผม
- [ ] PNG พื้นใส (ชิ้นส่วน) / พื้นดำ (เอฟเฟค, ชั้นแสง)
- [ ] ชื่อไฟล์ตรงตามตาราง ตัวพิมพ์เล็ก
- [ ] ทุกชิ้นของตัวเดียวกันมาจากเจนรอบเดียวกัน (สเกลเท่ากัน)
- [ ] ปลายข้อต่อโค้งมน ไม่มีรอยตัดแหว่ง
- [ ] ย่อดูขนาดในเกมแล้วยังอ่านออก
- [ ] ไม่มีสีชมพู #FF00FF หลงเหลือที่ขอบ (ขอบสีชมพูจางๆ = ต้องตัดใหม่)

## 6. โครงโฟลเดอร์
```
assets/
  style/                      ภาพล็อคสไตล์
  characters/<ชื่อ>/master.png
  characters/<ชื่อ>/parts/    head.png torso.png arm_upper.png ...
  characters/<ชื่อ>/variants/ leg_lower_1.png ...
  outfits/<ชุด>/parts/        (ชื่อไฟล์เหมือน parts เดิม)
  weapons/<อาวุธ>.png + <อาวุธ>_glow.png
  vfx/<ชื่อ>/concept.png, palette.png
  vfx/sprites/
```

## 7. ลำดับที่แนะนำให้เริ่ม
1. Style Lock (A) → 2. ตัวต้นแบบ (C1) → 3. ชีทชิ้นส่วน (C2) → ลากลง Rig Lab ด้วยกัน → แก้จุดหมุน
4. ขาหน้า 4 แบบ (C3) → 5. ดาบ + ชั้นแสง (C6, C7) → 6. VFX ตัวแรก (V1, V2)
