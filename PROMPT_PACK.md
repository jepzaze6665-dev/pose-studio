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

## 2. บล็อก Style Lock (แปะท้ายทุก prompt)

```
STYLE: 2D chibi game art, 2.5-head-tall proportions, thick dark navy outline (#1b1830) of even width,
flat cel shading with max 2 shadow tones, soft rim light from top-left, 3/4 view facing right,
clean readable silhouette, no texture noise, no tiny details, no gradients inside shapes,
colors slightly desaturated except glowing elements.
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

## 4.6 ชุดของแมพ: เมืองเริ่มต้น (Town Kit)
กฎร่วมทุกชีท (ล็อกสไตล์ทั้งแมพ — หลักที่ 4 จากคลิปแมพ):
```
TOWN KIT STYLE: 2D game environment asset, same art style as the reference character (chibi HD,
thick dark navy outline, flat cel shading 2 tones, soft light from top-left), 3/4 top-down view
(camera looking down about 35 degrees), scale: a door is as tall as a 2.5-head chibi character,
warm cozy medieval fantasy town, colors slightly desaturated, windows drawn UNLIT (dark blue glass).
Each object separate with wide gaps on a flat pure magenta background (#FF00FF), no shadows on the ground,
no text, no magenta on objects.
```
> แนบภาพตัวละครอัศวินเป็นภาพอ้างอิงทุกครั้ง (ล็อกสเกลและสไตล์) · หน้าต่างให้วาด "ไม่เปิดไฟ" — ผมทำไฟกลางคืนด้วยโค้ดเอง

**TK-1 อาคารหลัก (4 ชิ้น)**
```
4 town buildings: 1 cozy inn/tavern two floors with a hanging mug sign, 2 weapon & armor shop with an anvil
and crossed-swords sign, 3 item/potion shop with round window and bottles sign, 4 small residential house.
[TOWN KIT STYLE]
```
**TK-2 ศูนย์กลางเมือง (4 ชิ้น)**
```
4 town landmarks: 1 Job Guild hall (larger, banners, stone steps), 2 circular stone fountain with water,
3 teleport waystone (tall carved stone with a glowing rune crystal on top), 4 wooden quest notice board with papers.
[TOWN KIT STYLE]
```
**TK-3 ของประดับ (8 ชิ้น)**
```
8 small town props: 1 iron street lamp post, 2 big round shade tree, 3 flower bush, 4 market stall with striped
awning and goods, 5 barrels and crates cluster, 6 wooden fence segment (straight), 7 stone well with roof, 8 wooden bench.
[TOWN KIT STYLE]
```
**TK-4 พื้น (texture ต่อกันได้ 2 แผ่น · แยกเจนทีละแผ่น)**
```
Seamless tileable top-down 3/4 ground texture of [warm cobblestone town path / soft green grass with tiny flowers],
flat cel-shaded cartoon style matching the reference, low detail, no objects, no shadows, fills the whole image.
```

**TK-5 รายละเอียดพื้น (ground decals) — ตัวเชื่อมของกับพื้น**
```
16 small flat ground details for a 2D fantasy MMORPG town, 4x4 grid with wide gaps, seen from the same
3/4 top-down angle, lying FLAT on the ground (no height): 1-4 grass tufts of different sizes,
5-6 clusters of small pebbles, 7-8 soft dirt patches (irregular, faded edges), 9-10 fallen leaves,
11-12 tiny flower patches, 13-14 loose cobblestones and cracks, 15 small puddle, 16 moss patch.
Match the style, outline thickness and colors of the reference town objects.
Flat pure magenta background (#FF00FF), no shadows, no text, no magenta on the objects.
```
> ตัวสร้างจะโรย decals รอบฐานของทุกชิ้น (หญ้าขึ้นชิดผนัง กรวดข้างถนน ใบไม้ใต้ต้นไม้) — ทำให้ของ "งอก" จากพื้นแทนการวางทับ

**ผมจะทำต่อเมื่อได้ภาพ:** ตัดชิ้น → ติดป้ายเกม (ชน/บัง/ส่องแสง) → สร้าง normal map อัตโนมัติ → ชั้นไฟหน้าต่าง/โคมสำหรับกลางคืน → Map Lab (ใบสั่ง + กฎ + seed) → export เข้าเกม

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
