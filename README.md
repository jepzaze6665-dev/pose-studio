# โปรเจกต์เกม — โครงโฟลเดอร์

```
สอน AI/
├─ README.md              ไฟล์นี้
├─ PROMPT_PACK.md         prompt สำหรับเจนภาพ + แผนแบ่งงาน
├─ knowledge/             หลักการที่สกัดจากคลิป (PRINCIPLES.md, _raw_notes.md)
├─ reference/clips/       คลิปสอนต้นฉบับ 7 ไฟล์
├─ rig/rig_lab.html       ทดลองตัวละคร + กระดูก + ท่า + ชุด
├─ rig/pose_studio.html   เครื่องมือแก้ท่าแบบคีย์เฟรม (สร้างจาก rig_lab ด้วย tools/build_pose_studio.py)
├─ vfx/vfx_lab.html       ทดลอง VFX (โล่น้ำแข็ง / พอร์ทัล / โล่เลือด)
├─ vfx/vfx_runtime.js     สกิล VFX ที่ใช้ได้ทุกหน้า (ตอนนี้: ฝูงอสูรเงา) — Pose Studio เรียกผ่านเหตุการณ์คีย์
├─ vfx/dark_lab.html      VFX สีดำ 5 แบบ (หนาม / ระเบิดความว่าง / พายุ / อสูรเงา / สแลช X)
├─ map/map_lab.html      ตัวสร้างแมพเมือง (ใบสั่ง + กฎ + seed) + แสง 4 ช่วงเวลา + ป้ายเกม + ส่งออก JSON
├─ reference/vfx/         คลิปอ้างอิง VFX
├─ tools/
│   ├─ cut_parts.py       ตัดชีทพื้นชมพู -> PNG ทีละชิ้น
│   ├─ snap_pixels.py     แปลงพิกเซลปลอมจาก AI เข้ากริดจริง
│   ├─ cut_black.py       ตัดชีท VFX พื้นดำ (ไม่ลบแกนดำของชิ้น)
│   ├─ cut_grid.py        ตัด sprite sheet แบบกริด -> แถบเฟรม + จัดเฟรมให้ตรงกัน
│   ├─ make_night.py      ชั้นไฟกลางคืน (หน้าต่าง/โคมที่วาดแบบไม่เปิดไฟ)
│   ├─ make_normal.py     สร้าง normal map อัตโนมัติจากภาพ (ทำให้ภาพ 2D รับแสง)
│   └─ make_glow.py       แยกชั้นแสงเรือง (แดง/ม่วง/ฟ้า) ออกจากภาพอัตโนมัติ
└─ assets/
    ├─ characters/<ตัวละคร>/   master + parts_sheet + parts/ + variants/ (+ pieces/ = ผลตัดดิบ)
    │   ├─ knight/             อัศวินฟ้า-ทอง (แขนง A)
    │   └─ adventurer/         นักผจญภัยพิกเซล (ทดลอง)
    ├─ outfits/<ชุด>/          ชุดที่ใช้กระดูกเดียวกับตัวละคร
    │   └─ dark_knight/        เกราะดำม่วง (แขนง C) + *_glow.png
    ├─ helmets/<หมวก>/
    │   └─ dragon_skull/       open_cut.png (เจาะหน้า), closed.png, closed_glow.png
    ├─ vfx/dark/               ชีท VFX ที่เจน + sprites/ (ชิ้นเดี่ยว) + seq/ (แถบเฟรม sprite + json + glow)
    ├─ maps/town/kit/          ชุดของเมือง (TK-1~4: อาคาร ของประดับ พื้น 16 แบบ) + *_n.png + ชั้นไฟ
    └─ weapons/<อาวุธ>/
        └─ greatsword/         greatsword.png + greatsword_glow.png
```

## ส่งภาพใหม่
วางไฟล์ไว้ที่โฟลเดอร์หลักได้เลย แล้วบอกว่าเป็นอะไร ผมจะย้ายเข้าที่ ตัด และตั้งชื่อให้

## เปิดดู
`http://localhost:8765/rig/rig_lab.html` · `http://localhost:8765/vfx/vfx_lab.html`
