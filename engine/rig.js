// =====================================================================
//  RIG engine — ตัวละคร 2D แบบกระดูก (ใช้ร่วมกันระหว่างสตูดิโอกับเกม)
//  RIG.loadOutfit(base)            โหลดชิ้นส่วนชุด
//  RIG.makeChar({...})             สร้างตัวละคร
//  RIG.play(ch, clip)              เล่นท่า (clip จาก Pose Studio)
//  RIG.update(ch, dt, moving)      อัปเดตท่า + ยิงเหตุการณ์คีย์ (ch.onEvent)
//  RIG.draw(ctx, ch, t)            วาด
//  ch.springs={bone:{k,damp,amt,max}}  กระดูกปลายโซ่ดีดตามเอง (physics) — เช่น RIG.SPRINGS.hero
//  --- เพิ่มจากการแกะ Night Camp (knowledge/NIGHTCAMP_TEARDOWN.md) ---
//  clip.hit / clip.lunge / clip.aim   เวลาดาเมจลง · พุ่งไปหน้ากี่ px · หันตามเป้า (ch.aim องศา ลบ=เป้าอยู่สูง)
//  clip.shot                          ท่าค้างภาพเดียว → RIG.alive() เติมหายใจ/หัวตามช้า/แขนลอยเอง
//  outfit.fist (ค่าเริ่ม true)          วาดแขนหน้า 3 ชั้น: ปลายแขน → อาวุธ → กำปั้น (ดาบอยู่ในกำมือ)
//  ch.footIK=true                     เท้าปักพื้น ย่อตัวแล้วเข่างอเอง (IK 2 ท่อน: RIG.ik2)
//  ch.chains=[{at,off,n,len,visc,stiff,damp,...}]  ผม/ผ้า = โซ่สปริง 3 ค่า (ความหนืด ความแข็ง การหน่วง)
//  ch.family='spear'                  ตระกูลการถืออาวุธ: ยืน/เดิน/วิ่ง/ตี 1-3 ของตระกูลนั้น (RIG.FAMILY)
// =====================================================================
(function(){
const B={root:{p:null,off:[0,0]},torso:{p:'root',off:[0,0]},sheath:{p:'torso',off:[-8,-28]},head:{p:'torso',off:[2,-47]},
  armB_u:{p:'torso',off:[-11,-34]},armB_l:{p:'armB_u',off:[0,28]},armF_u:{p:'torso',off:[11,-34]},armF_l:{p:'armF_u',off:[0,28]},
  weapon:{p:'armF_l',off:[0,27]},shB:{p:'armB_u',off:[0,0]},shF:{p:'armF_u',off:[0,0]},
  legB_u:{p:'root',off:[-8,-2]},legB_l:{p:'legB_u',off:[0,22]},legF_u:{p:'root',off:[8,-2]},legF_l:{p:'legF_u',off:[0,22]},
  fist:{p:'armF_u',off:[0,28],as:'armF_l'}}; // fist = ภาพปลายแขนหน้าซ้ำ ตัดเหลือแค่มือ วาดทับด้ามอาวุธ
const FOOT=48, WOFF={weapon:90};
const ORDER=['sheath','armB_l','armB_u','shB','legB_u','legB_l','legF_u','legF_l','torso','weapon','armF_l','armF_u','shF','head'];
// ถืออาวุธ + มีชั้นกำปั้น: ปลายแขน (ฝ่ามือ) อยู่ใต้ด้าม → อาวุธ → นิ้วที่กำทับด้าม (Night Camp: arm_F_up / sword_front / fist_F / arm_F_lo)
const ORDER_FIST=['sheath','armB_l','armB_u','shB','legB_u','legB_l','legF_u','legF_l','torso','armF_l','weapon','fist','armF_u','shF','head'];
const PART_OF={head:'head',torso:'torso',armF_u:'arm_upper',armB_u:'arm_upper',armF_l:'arm_lower',armB_l:'arm_lower',
  legF_u:'leg_upper',legB_u:'leg_upper',legF_l:'leg_lower',legB_l:'leg_lower',shF:'shoulder',shB:'shoulder'};
const SPEC={head:{h:54,px:.6,py:.93},torso:{h:81,px:.5,py:.63},arm_upper:{h:39,px:.5,py:.12},arm_lower:{h:36,px:.5,py:.08},
  leg_upper:{h:29,px:.5,py:.1},leg_lower:{h:28,px:.5,py:.06},shoulder:{h:28,px:.5,py:.3}};
const SHEATH={a:-40,s:.8}; // มุมดาบบนหลัง (องศา) + ย่อเล็กน้อย — เลือกจากภาพลอง 6 แบบ: ใบดาบโผล่เหนือไหล่ฝั่งหลัง
const GEAR={sword:{h:84,px:.5,py:.86},helm:{h:92,px:.5,py:.84,dx:-3,dy:2}};
const READY={root:0,torso:4,head:-3,armF_u:-20,armF_l:-55,weapon:-15,armB_u:15,armB_l:-30,legF_u:-14,legF_l:12,legB_u:16,legB_l:10};
const BONES=['legB_u','legB_l','legF_u','legF_l','torso','head','armF_u','armF_l','armB_u','armB_l','weapon','rootY'];
const E={hold:s=>0,lin:s=>s,inout:s=>s<.5?2*s*s:1-((-2*s+2)**2)/2,exp:s=>1-Math.pow(1-s,4),out:s=>1-(1-s)**3};

function img(src){const i=new Image();i.src=src;return i;}
// spec/bones/foot = ค่าเฉพาะชุด (ชีทจาก AI สเกลไม่เท่ากัน) เช่น hero2 — ค่าเดียวกับ SPEC_SET/BODY ใน rig_lab
function loadOutfit(base,{gear='data/gear/',parts=['head','torso','arm_upper','arm_lower','leg_upper','leg_lower','shoulder'],glows=[],helmet=false,sword=true,leg='leg_lower_3',hair=true,spec=null,bones=null,foot=null,swordImg='greatsword',boneParts=[],idleParts={}}={}){
  const O={img:{},glow:{},hair:hair?img(base+'head_hair.png'):null,helmet,sword,spec,bones,foot};
  for(const p of parts)O.img[p]=img(base+p+'.png');
  for(const b of boneParts)O.img[b]=img(base+b+'.png');
  O.idleImg={};for(const b in idleParts)O.idleImg[b]=img(base+idleParts[b]+'.png');   // ทริคขาหน้า (c4): ยืน = ปลายเท้าหันหาคนดู (มั่นใจสุด) · เดิน/วิ่ง = หันไปทางที่ไป   // แขน/ขาหน้า-หลังคนละภาพ (ชีท C2 v2)
  for(const g of glows)O.glow[g]=img(base+g+'_glow.png');
  if(leg)O.leg=img(base+leg+'.png');
  if(sword){O.sword=img(gear+swordImg+'.png');O.swordGlow=img(gear+swordImg+'_glow.png');}
  if(helmet){O.helmOpen=img(gear+'helmet_open.png');O.helmClosed=img(gear+'helmet_closed.png');O.helmGlow=img(gear+'helmet_closed_glow.png');O.helmMask=img(gear+'helmet_mask.png');}
  return O;}
const ok=i=>i&&i.complete&&i.naturalWidth>0;

// ---------- ท่า ----------
function lerpPose(a,b,s){const r={};for(const k of BONES)r[k]=(a[k]??READY[k]??0)+((b[k]??READY[k]??0)-(a[k]??READY[k]??0))*s;return r;}
// ยืนพร้อมสู้ = ค่า "ท่าพร้อมสู้" จาก Pose Studio ของ Night Camp (knowledge/_raw_notes.md c2-ละเอียด)
//   ค่าเขา: ขาหลัง 17 เข่าหลัง 33 · ขาหน้า -16 เข่าหน้า 26 · โน้มตัว 7 · หัว 0 · ต้นแขนหน้า 49 ศอกหน้า 54 · ต้นแขนหลัง 75 ศอกหลัง 18
//   แปลงเป็นระบบเรา: ต้นแขน = ค่าเขา-90, ศอก = -ค่าเขา, ขา/เข่า/ตัว ใช้ตรงๆ
//   ปรับหลังลองจริง (ภาพเทียบ knowledge/compare_stance.png): เข่าหลังของเรางอกลับทิศกับของเขา -> ใช้ค่าลบ ไม่งั้นแข้งไขว้กัน;
//   แขนหน้ายื่นออก + ดาบเอียงไปหน้า ~45° ให้เหมือนภาพเขา (ค่าแปลงตรงๆ ดาบหันหลัง)
const STANCE={legB_u:6,legB_l:3,legF_u:-6,legF_l:3,torso:4,head:0,armF_u:6,armF_l:-14,armB_u:6,armB_l:-12,weapon:60,rootY:0}; // ถือแบบภาพต้นฉบับ: มือห้อยข้างสะโพก ใบดาบชี้ลงไปข้างหน้า
// ทับด้วยชีวิต (หลัก 4/5): หายใจแบบ ease · หัว/แขนหลังตามช้ากว่าลำตัว (overlap) · ถ่ายน้ำหนักช้าๆ · ทุก ~7 วิ เหลียว/ขยับดาบ 1 ครั้ง
function idle(t){const sm=x=>x*x*(3-2*x),br=Math.sin(t*2.2),brL=Math.sin(t*2.2-.7),ws=Math.sin(t*.7),S=STANCE;
  const ph=t%7,fid=ph<1.4?sm(Math.min(1,ph/.35))*sm(Math.min(1,(1.4-ph)/.35)):0;
  return {...READY,
    legB_u:S.legB_u+ws*1.5,legB_l:S.legB_l+ws*2+br*1.5,legF_u:S.legF_u+ws*1.5,legF_l:S.legF_l-ws*2+br*1.5,   // เข่าย่อตามจังหวะหายใจ
    torso:S.torso+br*1.4+ws*1,head:S.head-brL*1.6-fid*8,
    armF_u:S.armF_u+br*2-fid*5,armF_l:S.armF_l+br*1.5,weapon:S.weapon+brL*3-fid*8,
    armB_u:S.armB_u-brL*2.5,armB_l:S.armB_l-brL*2,
    rootY:S.rootY+br*1.3,sq:.014*br};}
// นอกการต่อสู้ (ดาบสะพายหลัง) — ยืนผ่อนคลาย: แขนห้อยข้างตัว กำหมัดหลวมๆ ศอกงอนิด (ค่า "ยืนเก็บดาบ" ของ Night Camp)
const REST={legB_u:5,legB_l:3,legF_u:-5,legF_l:3,torso:2,head:0,armF_u:14,armF_l:-16,armB_u:-12,armB_l:-14,rootY:0};
function rest(t){const br=Math.sin(t*2),brL=Math.sin(t*2-.7),R=REST,ph=t%8,sm=x=>x*x*(3-2*x),fid=ph<1.6?sm(Math.min(1,ph/.4))*sm(Math.min(1,(1.6-ph)/.4)):0;
  return {...READY,...R,torso:R.torso+br*1.2,head:R.head-brL*1.5-fid*7,armF_u:R.armF_u+brL*2,armF_l:R.armF_l-brL*2,armB_u:R.armB_u-brL*2,armB_l:R.armB_l+brL*1.5,
    legF_l:R.legF_l+br*.8,legB_l:R.legB_l+br*.8,rootY:br*1.1,sq:.012*br};}
// วิ่งมือเปล่า: หมัดระดับอก ศอกงอ ~90° แกว่งสวนขาแรงกว่าตอนถือดาบ
function runFree(t){const p=walk(t),ph=((t*RUN_HZ)%1)*Math.PI*2,s=Math.sin(ph);
  return {...p,armF_u:-22+34*s,armF_l:-88+10*s,armB_u:14-34*s,armB_l:-90-10*s};}
// วิ่ง (คลิป c4 ช่วง 1:29 นับทีละเฟรม): 1 รอบ = 2 ก้าว = 0.67 วิ (1.5 รอบ/วิ ≈ 3 ก้าว/วิ)
// · ตัวโน้มไปหน้าตลอด หัวนิ่ง · ขาที่ตามหลังเตะส้นขึ้น เข่างอมาก · ตัวเด้ง 2 ครั้ง/รอบ
// · เข่า "ทั้งสองขา" งอทิศเดียวกัน (ค่าบวก = แข้งไปข้างหลัง) — ค่าลบ = เข่าหักไปหน้าแบบขานก (ผิด)
// · แขน: หมัดหน้ายื่นระดับอก, ศอกหลังดึงไปข้างหลังจนหมัดหลบหลังตัว, แกว่งสวนขา (ไม่ให้หมัดสองข้างมาชนกันกลางพุง)
// · ดาบหมุนสวนแขน ให้มุมดาบในโลกคงที่ ไม่เหวี่ยงขึ้นตามแขน
const RUN_HZ=1.5;
// วงรอบขา: hz = รอบ/วิ, amp 1 = วิ่ง (คลิป c4), ~.45 = เดิน (ก้าวสั้น ตัวตั้งตรง เด้งน้อย)
function gait(t,hz,amp){const ph=((t*hz)%1)*Math.PI*2,s=Math.sin(ph),c=Math.cos(ph),c2=Math.cos(2*ph);
  const lift=x=>{x=Math.max(0,x);return x*x*(3-2*x);};
  return {...READY,
    legF_u:(-30*s-4)*amp,legB_u:(30*s+4)*amp,legF_l:8+65*amp*lift(c),legB_l:8+65*amp*lift(-c),
    armF_u:-28+28*s,armF_l:-75+8*s,armB_u:20-28*s,armB_l:-85-8*s,
    weapon:150-36*s,torso:11*amp+1.5*c2,head:-6*amp-1.5*c2,
    rootY:(-5*Math.abs(c2)+2)*amp,sq:.03*c2*amp};}
function walk(t){return gait(t,RUN_HZ,1);}
const ATK=[
 {wind:{...READY,armF_u:-195,armF_l:-25,weapon:-15,torso:-10,head:-8,legF_u:-20,legB_u:22,armB_u:-30,rootY:-3},
  hit:{...READY,armF_u:-35,armF_l:-15,weapon:15,torso:18,head:8,legF_u:-30,legF_l:22,legB_u:30,armB_u:35,rootY:5},lunge:12},
 {wind:{...READY,armF_u:-10,armF_l:-40,weapon:70,torso:10,head:4,legF_u:-26,legB_u:24,armB_u:20,rootY:4},
  hit:{...READY,armF_u:-160,armF_l:-15,weapon:-10,torso:-12,head:-10,legF_u:-14,legB_u:18,armB_u:-40,rootY:-6},lunge:8},
 {wind:{...READY,armF_u:-185,armF_l:-10,weapon:-35,torso:-16,head:-12,legF_u:-32,legF_l:30,legB_u:30,rootY:-10,armB_u:-60},
  hit:{...READY,armF_u:-15,armF_l:-5,weapon:25,torso:28,head:12,legF_u:-42,legF_l:34,legB_u:36,legB_l:20,armB_u:40,rootY:9},big:true,lunge:26}];
const TM={wind:.32,strike:.07,stop:.07,follow:.16,rec:.28};
const clean=p=>{const r={};for(const k of BONES)r[k]=Math.round((p[k]||0)*10)/10;return r;};
// ท่าตี 4 จังหวะ + ข้อมูลที่เกมใช้ (แบบ Night Camp): hit = วินาทีที่ดาเมจลง, lunge = พุ่งไปหน้ากี่ px, aim = หันตามเป้า
// aw ของแต่ละคีย์ = หันตามเป้าแค่ไหน: ง้าง .35 (AW) · ฟัน/ค้าง 1 (AS) · ท่าเริ่ม/จบ 0 (ไม่กระตุกตอนจบท่า)
function atkClip(i,set=ATK,o={}){const k=set[i],sp=o.tempo||1,R=o.ready||READY,st=(k.big?TM.stop*1.8:TM.stop)*sp;let t=0;const keys=[{t:0,pose:clean(R),ease:'inout',aw:0}];
  t+=TM.wind*sp;keys.push({t,pose:clean(k.wind),ease:'inout',aw:.35});t+=TM.strike*sp;const hit=t;keys.push({t,pose:clean(k.hit),ease:'exp',evt:'hit',aw:1});
  t+=st+TM.follow*sp;keys.push({t,pose:clean(k.hit),ease:'hold',aw:1});t+=TM.rec*sp;keys.push({t,pose:clean(R),ease:'out',aw:0});
  return {name:(o.name||'โจมตี ')+(i+1)+(k.big?' (ปิดคอมโบ)':''),len:+t.toFixed(3),speed:1,fps:0,loop:false,big:!!k.big,keys,
    hit:+hit.toFixed(3),lunge:k.lunge??(k.big?26:10),aim:true};}
function swarmClip(){const cast={...READY,armF_u:-150,armF_l:-20,weapon:-10,torso:-6,head:-8,armB_u:-40,legF_u:-20,legB_u:18,rootY:-2};
  return {name:'สกิล: ฝูงอสูรเงา',len:3.0,speed:1,fps:0,loop:false,hit:.35,aim:true,keys:[{t:0,pose:clean(READY),ease:'inout',aw:0},{t:.35,pose:clean(cast),ease:'exp',evt:'swarm',aw:1},{t:2.4,pose:clean(cast),ease:'hold',aw:1},{t:3.0,pose:clean(READY),ease:'inout',aw:0}]};}
// ท่าค้างภาพเดียว (shot): จัดท่าเดียวใน Pose Studio แล้วเกมเติมชีวิตให้ (alive)
const SHOT_RAISE={...READY,armF_u:-170,armF_l:-15,weapon:-5,armB_u:-20,armB_l:-40,torso:-4,head:-10,legF_u:-14,legF_l:8,legB_u:12,legB_l:6,rootY:0};
const CLIPS={'โจมตี 1':atkClip(0),'โจมตี 2':atkClip(1),'โจมตี 3 (ปิดคอมโบ)':atkClip(2),'สกิล: ฝูงอสูรเงา':swarmClip(),
  'ท่าค้าง: ชูดาบ':{name:'ท่าค้าง: ชูดาบ',len:.35,speed:1,fps:0,loop:false,shot:true,keys:[{t:0,pose:clean(READY),ease:'inout'},{t:.35,pose:clean(SHOT_RAISE),ease:'out'}]}};
// ท่าที่ส่งออกจาก Pose Studio ทับค่าเริ่มต้น (data/clips.json) · คีย์เดียว = ท่าค้าง
function loadClips(url){return fetch(url).then(r=>r.ok?r.json():null).then(j=>{if(j&&j.clips)for(const c of j.clips){if(c.keys&&c.keys.length===1&&c.shot==null)c.shot=true;CLIPS[c.name]=c;}}).catch(()=>{});}
function seg(c,t){const K=c.keys;if(t<=K[0].t)return [K[0],K[0],0];if(t>=K[K.length-1].t){const L=K[K.length-1];return [L,L,1];}
  for(let i=0;i<K.length-1;i++){const a=K[i],b=K[i+1];if(t>=a.t&&t<=b.t)return [a,b,(E[b.ease]||E.inout)((t-a.t)/Math.max(1e-6,b.t-a.t))];}
  const L=K[K.length-1];return [L,L,1];}
function sample(c,t){if(c.fps>0)t=Math.floor(t*c.fps)/c.fps;const [a,b,s]=seg(c,t);return a===b?a.pose:lerpPose(a.pose,b.pose,s);}
function aimW(c,t){const [a,b,s]=seg(c,t),w=k=>k.aw??(k.evt?1:.35);return w(a)+(w(b)-w(a))*s;}

// ---------- หันตามเป้า (กฎจาก Night Camp anim.js) ----------
// AS ฟัน: หันเต็มมุมแต่แขนไม่จบหลังลำตัว · AW ง้าง/ตามแรง: หันบางส่วน · LU เล็งสูง = เอนหลังนิด · UP แขนชูไม่เลยหัวไปข้างหลัง
// กันจม: ปลายอาวุธยาวห้ามลงต่ำกว่าพื้นเกิน GROUND_DIP
const AIM_MAX=70,UP_MAX=-205,GROUND_DIP=14;
function applyAim(p,aim,w){if(!aim||!w)return p;const a=Math.max(-AIM_MAX,Math.min(AIM_MAX,aim))*w,r={...p};
  r.armF_u+=a*.75;r.weapon+=a*.25;r.armB_u+=a*.3;r.head+=a*.25;
  if(a<0)r.torso+=a*.12;                                        // LU
  if(w>.5)r.armF_u=Math.min(r.armF_u,12);                        // AS: ไม่ฟันไปจบหลังส้นเท้าตัวเอง
  r.armF_u=Math.max(r.armF_u,UP_MAX);return r;}                  // UP
function tipLen(ch){const F=famOf(ch);return F&&!F.img?F.len*F.grip:GEAR.sword.h*GEAR.sword.py;}
function keepOffGround(ch,p){const FT=(ch.outfit&&ch.outfit.foot)||FOOT,g=FT-(p.rootY||0)*.5+GROUND_DIP,L=tipLen(ch);
  const tipY=q=>{const m=world(q,ch.outfit&&ch.outfit.bones).weapon;return m.y-L*Math.cos(m.a);};
  if(tipY(p)<=g)return p;const r={...p};
  for(let i=0;i<36&&tipY(r)>g;i++){const up={...r,weapon:r.weapon-4},dn={...r,weapon:r.weapon+4};r.weapon=tipY(up)<tipY(dn)?up.weapon:dn.weapon;}
  return r;}

// ---------- ท่าค้างมีชีวิต: หายใจ · หัวตามช้ากว่าตัวครึ่งจังหวะ · น้ำหนักโยกช้า · แขน+อาวุธลอยขึ้นลงนิดๆ ----------
function alive(p,t,k=1){const br=Math.sin(t*2.2),lag=Math.sin(t*2.2-1.1),sw=Math.sin(t*.6);
  return {...p,torso:(p.torso||0)+(br*1.3+sw*.8)*k,head:(p.head||0)-lag*1.8*k,
    armF_u:(p.armF_u||0)+lag*2.2*k,armF_l:(p.armF_l||0)+lag*1.2*k,weapon:(p.weapon||0)+lag*2.5*k,
    armB_u:(p.armB_u||0)-lag*2*k,armB_l:(p.armB_l||0)-lag*1.5*k,
    legF_u:(p.legF_u||0)+sw*1.2*k,legB_u:(p.legB_u||0)+sw*1.2*k,legF_l:(p.legF_l||0)+br*1.2*k,legB_l:(p.legB_l||0)+br*1.2*k,
    rootY:(p.rootY||0)+br*1.2*k,sq:.014*br*k};}

// ---------- ตระกูลการถืออาวุธ (Night Camp: อาวุธ 1,251 ชิ้นแค่บอกว่าอยู่ตระกูลไหน) ----------
// ค่าท่าเขียนเป็น "blade" = มุมใบอาวุธในโลก (0 ชี้ขึ้น · 90 ชี้หน้า · 180 ชี้ลง) แล้วแปลงเป็นมุม weapon ให้เอง
// len/grip = ความยาวอาวุธ + จุดจับ (สัดส่วนจากปลาย) · tempo = คูณเวลาท่าตี (หนัก >1 เบา <1) · img = ใช้ภาพดาบของชุด
const FAMILY={
 greatsword:{name:'ดาบใหญ่',img:true,len:84,grip:.86,tempo:1},
 sword:{name:'ดาบมือเดียว',len:58,grip:.8,tempo:.85,shape:'sword',col:'#cfd8e6',
  ready:{torso:5,armF_u:-35,armF_l:-40,blade:40,armB_u:15,armB_l:-30,legF_u:-12,legF_l:12,legB_u:14,legB_l:10},
  stance:{armF_u:-10,armF_l:-35,blade:55,torso:4,legF_u:-6,legF_l:3,legB_u:6,legB_l:3,armB_u:6,armB_l:-12},carry:{armF_u:-20,armF_l:-60,blade:30},
  atk:[{wind:{armF_u:-170,armF_l:-30,blade:-40,torso:-8,head:-6,legF_u:-18,legB_u:20,armB_u:-20,rootY:-2},hit:{armF_u:-40,armF_l:-10,blade:150,torso:16,head:6,legF_u:-28,legF_l:20,legB_u:28,armB_u:30,rootY:4},lunge:10},
       {wind:{armF_u:-20,armF_l:-30,blade:150,torso:8,armB_u:10},hit:{armF_u:-150,armF_l:-20,blade:20,torso:-10,head:-8,armB_u:-30,rootY:-4},lunge:8},
       {wind:{armF_u:-10,armF_l:-90,blade:90,torso:-6,legF_u:-10,legB_u:24,rootY:2},hit:{armF_u:-90,armF_l:-5,blade:90,torso:22,head:10,legF_u:-44,legF_l:30,legB_u:36,legB_l:18,rootY:9},lunge:30,big:true}]},
 spear:{name:'หอก',len:112,grip:.62,tempo:1,shape:'spear',col:'#d9dfe8',
  ready:{torso:6,armF_u:-55,armF_l:-30,blade:75,armB_u:-30,armB_l:-50,legF_u:-14,legF_l:14,legB_u:16,legB_l:12,rootY:2},
  stance:{armF_u:-40,armF_l:-45,blade:62,torso:5,armB_u:-20,armB_l:-50,legF_u:-8,legF_l:5,legB_u:8,legB_l:4},carry:{armF_u:-30,armF_l:-55,blade:60},
  atk:[{wind:{armF_u:-20,armF_l:-95,blade:88,torso:-4,legB_u:20,legF_u:-14},hit:{armF_u:-88,armF_l:-4,blade:90,torso:18,legF_u:-36,legF_l:24,legB_u:32,rootY:6},lunge:20},
       {wind:{armF_u:-10,armF_l:-30,blade:150,torso:6},hit:{armF_u:-140,armF_l:-20,blade:20,torso:-8,head:-6},lunge:8},
       {wind:{armF_u:-160,armF_l:-40,blade:110,torso:-12,rootY:-12,legF_u:-30,legF_l:40,legB_u:10,legB_l:50},hit:{armF_u:-60,armF_l:-10,blade:125,torso:26,legF_u:-44,legF_l:34,legB_u:36,legB_l:20,rootY:10},lunge:34,big:true}]},
 dagger:{name:'มีดสั้น',len:32,grip:.72,tempo:.7,shape:'dagger',col:'#e3e7ef',
  ready:{torso:10,armF_u:-50,armF_l:-70,blade:80,armB_u:-40,armB_l:-80,legF_u:-18,legF_l:18,legB_u:20,legB_l:14,rootY:3},
  stance:{armF_u:-30,armF_l:-75,blade:75,torso:8,armB_u:-25,armB_l:-80,legF_u:-10,legF_l:8,legB_u:10,legB_l:6,rootY:2},carry:{armF_u:-25,armF_l:-80,blade:70},
  atk:[{wind:{armF_u:-10,armF_l:-110,blade:90},hit:{armF_u:-90,armF_l:-10,blade:95,torso:18},lunge:14},
       {wind:{armF_u:-120,armF_l:-30,blade:30,torso:-6},hit:{armF_u:-20,armF_l:-60,blade:160,torso:14},lunge:10},
       {wind:{armF_u:-30,armF_l:-100,blade:60,torso:20,rootY:8},hit:{armF_u:-100,armF_l:-5,blade:100,torso:30,legF_u:-46,legB_u:40,rootY:10},lunge:40,big:true}]},
 staff:{name:'ไม้เท้า',len:104,grip:.58,tempo:1.1,shape:'staff',col:'#8a5a36',gem:'#7fd8ff',
  ready:{armF_u:-25,armF_l:-25,blade:5,torso:2},
  stance:{armF_u:-12,armF_l:-20,blade:0,torso:2,legF_u:-5,legF_l:3,legB_u:5,legB_l:3,armB_u:-10,armB_l:-14},carry:{armF_u:-20,armF_l:-30,blade:10},
  atk:[{wind:{armF_u:-170,armF_l:-10,blade:-20,torso:-8,head:-8},hit:{armF_u:-95,armF_l:-5,blade:90,torso:10},lunge:4},
       {wind:{armF_u:-160,armF_l:-30,blade:-60},hit:{armF_u:-40,armF_l:-10,blade:140,torso:16},lunge:8},
       {wind:{armF_u:-185,armF_l:-5,blade:0,torso:-14,rootY:-6,head:-12},hit:{armF_u:-60,armF_l:-5,blade:170,torso:22,rootY:9,legF_u:-30,legF_l:30,legB_u:30},lunge:6,big:true}]},
 axe:{name:'ขวาน/ค้อน',len:74,grip:.82,tempo:1.3,shape:'axe',col:'#c9ced8',
  ready:{armF_u:-35,armF_l:-55,blade:20,armB_u:-30,armB_l:-60,torso:6,legF_u:-14,legF_l:12,legB_u:16,legB_l:10,rootY:2},
  stance:{armF_u:-5,armF_l:-30,blade:125,torso:4,legF_u:-8,legF_l:5,legB_u:8,legB_l:4,armB_u:-6,armB_l:-14},carry:{armF_u:-150,armF_l:-70,blade:-60},
  atk:[{wind:{armF_u:-200,armF_l:-20,blade:-50,torso:-12,head:-10,rootY:-4,armB_u:-150},hit:{armF_u:-50,armF_l:-5,blade:150,torso:24,head:10,rootY:8,legF_u:-34,legF_l:28,legB_u:32,armB_u:-40},lunge:12},
       {wind:{armF_u:-40,armF_l:-80,blade:-80,torso:-6},hit:{armF_u:-100,armF_l:-10,blade:120,torso:18},lunge:10},
       {wind:{armF_u:-195,armF_l:-10,blade:-20,torso:-18,rootY:-14,legF_l:40,legB_l:40},hit:{armF_u:-40,armF_l:-5,blade:175,torso:30,rootY:10,legF_u:-44,legF_l:34,legB_u:38,legB_l:20},lunge:22,big:true}]}};
function famPose(F,o){const p={...READY,...(F.ready||{}),...o};if(o.blade!=null)p.weapon=o.blade-90-p.armF_u-p.armF_l-p.torso;delete p.blade;return p;}
for(const id in FAMILY){const F=FAMILY[id];F.id=id;
  if(id==='greatsword'){F.clips={atk1:CLIPS['โจมตี 1'],atk2:CLIPS['โจมตี 2'],atk3:CLIPS['โจมตี 3 (ปิดคอมโบ)']};continue;}
  F.readyP=famPose(F,F.ready);F.stanceP=famPose(F,F.stance);
  const set=F.atk.map(a=>({...a,wind:famPose(F,a.wind),hit:famPose(F,a.hit)}));
  F.clips={};for(let i=0;i<3;i++)F.clips['atk'+(i+1)]=atkClip(i,set,{tempo:F.tempo,ready:F.readyP,name:F.name+' ตี '});}
const famOf=ch=>ch.family&&FAMILY[ch.family]||null;
// ถืออาวุธเดิน/วิ่ง: ขาตามวงรอบ แขนหน้าถือท่า carry ของตระกูล (ตัวบนนิ่ง ขาวิ่ง — Night Camp ผสมแบบเดียวกัน)
function famMove(F,t,run){const p=gait(t,run?RUN_HZ:1,run?1:.45),C=F.carry,s=Math.sin(((t*(run?RUN_HZ:1))%1)*Math.PI*2);
  p.armF_u=C.armF_u+4*s;p.armF_l=C.armF_l;p.weapon=C.blade-90-p.armF_u-p.armF_l-p.torso;return p;}
function famBase(ch,moving,armed){const F=famOf(ch),run=moving&&moving!=='walk';
  if(!F||F.id==='greatsword'){if(!moving)return armed?idle(ch.t):rest(ch.t);if(!armed)return runFree(ch.t);
    if(run)return walk(ch.t);const p=gait(ch.t,1,.45);return p;}
  if(!armed)return moving?runFree(ch.t):rest(ch.t);
  return moving?famMove(F,ch.t,run):alive(F.stanceP,ch.t);}

function makeChar(o){return Object.assign({x:0,y:0,dir:1,scale:1,t:0,act:null,hitstop:0,flash:0,visor:false,aim:0,pose:{...READY},onEvent:()=>{}},o);}
const ARMED_SEC=5;
function play(ch,clip){const F=famOf(ch);if(typeof clip==='string')clip=(F&&F.clips[clip])||CLIPS[clip];if(!clip)return false;ch.act={clip,t:0,last:-1,lx:0};ch.armed=ARMED_SEC;return true;}
function update(ch,dt,moving){step(ch,dt,moving);if(ch.add){const q={...ch.pose};for(const k in ch.add)q[k]=(q[k]||0)+ch.add[k];ch.pose=q;} /* ch.add = บวกท่าทับ เช่น ย่อตัว/สะดุ้งโดนตี */
  if(ch.footIK)plantFeet(ch);if(!(ch.hitstop>0))spring(ch,dt);if(ch.chains)chains(ch,dt);}
function step(ch,dt,moving){
  ch.t+=dt;ch.moving=moving; ch.flash=Math.max(0,ch.flash-dt*2.2);
  if(!ch.act||ch.act.held)ch.armed=moving&&!ch.keepArmed?0:Math.max(ch.act&&ch.act.held?ARMED_SEC:0,(ch.armed||0)-dt);   // เดิน/วิ่ง = เก็บดาบเข้าหลังทันที (เว้นแต่ keepArmed)
  if(ch.act&&ch.act.held&&moving)ch.act=null;            // ท่าค้าง: ขยับเมื่อไหร่ก็เลิกค้าง
  const armed=ch.armed>0,base=famBase(ch,moving,armed);
  if(!ch.act){ch.pose=base;return;}
  if(ch.hitstop>0){ch.hitstop-=dt;return;}            // หยุดภาพ: ค้างท่าเดิม
  const a=ch.act,c=a.clip;a.t+=dt*(c.speed||1);
  for(const k of c.keys)if(k.evt&&a.last<k.t&&a.t>=k.t)ch.onEvent(k.evt,c,ch);
  if(c.hit!=null&&!c.keys.some(k=>k.evt==='hit')&&a.last<c.hit&&a.t>=c.hit)ch.onEvent('hit',c,ch);
  if(c.lunge&&c.hit&&ch.lunge!==false){const lx=c.lunge*E.out(Math.min(1,a.t/c.hit));ch.x+=(lx-a.lx)*ch.dir*(ch.scale||1);a.lx=lx;}
  a.last=a.t;
  if(a.t>=c.len&&!c.loop){if(!c.shot){ch.act=null;ch.pose=base;return;}a.held=true;
    ch.pose=alive(c.keys[c.keys.length-1].pose,ch.t,ch.alive===false?0:1);return;}
  const tt=c.loop?a.t%c.len:a.t;let p=sample(c,tt);
  if(c.aim&&ch.aim&&ch.useAim!==false)p=applyAim(p,ch.aim,aimW(c,tt));
  ch.pose=ch.groundClamp===false?p:keepOffGround(ch,p);}

// ---------- IK 2 ท่อน (เท้าปักพื้น) ----------
// มุมระบบเรา: 0 = ชี้ลง · ลบ = หมุนไปหน้า · เข่าบวก = แข้งไปข้างหลัง → คืน [มุมต้นขา, มุมเข่า] (องศา) ที่ทำให้ปลายเท้าไปถึง (dx,dy)
function ik2(l1,l2,dx,dy){const d=Math.min(l1+l2-1e-3,Math.max(Math.abs(l1-l2)+1e-3,Math.hypot(dx,dy))),base=Math.atan2(-dx,dy);
  const al=Math.acos(Math.max(-1,Math.min(1,(l1*l1+d*d-l2*l2)/(2*l1*d)))),be=Math.acos(Math.max(-1,Math.min(1,(l1*l1+l2*l2-d*d)/(2*l1*l2))));
  return [(base-al)*180/Math.PI,(Math.PI-be)*180/Math.PI];}
function legDims(ch,side){const O=ch.outfit||{},bo=O.bones||{},FT=O.foot||FOOT,hip=bo['leg'+side+'_u']||B['leg'+side+'_u'].off,L1=(bo['leg'+side+'_l']||B['leg'+side+'_l'].off)[1];
  return {hip,L1,L2:(O.legLen||FT-hip[1]-L1)};}
// เท้าที่ "ควรแตะพื้น" (FK อยู่ใกล้พื้น) ถูกดึงลงพื้นพอดี: ย่อตัว → เข่างอเอง ไม่จมดิน · เท้าที่ยกอยู่ (ก้าว/กระโดด) ปล่อยตาม FK
function plantFeet(ch){if(ch.moving)return;const p={...ch.pose},O=ch.outfit||{},FT=O.foot||FOOT,g=FT-(p.rootY||0)*.5,M=world(p,O.bones);
  for(const sd of['F','B']){const {hip,L1,L2}=legDims(ch,sd),m=M['leg'+sd+'_l'],fy=m.y+L2*Math.cos(m.a),fx=m.x-L2*Math.sin(m.a);
    if(fy<g-8)continue;const [a1,a2]=ik2(L1,L2,fx-hip[0],g-hip[1]);p['leg'+sd+'_u']=a1-(p.root||0);p['leg'+sd+'_l']=a2;}
  ch.pose=p;}

// ---------- spring bone: ปลายโซ่ตามหลังช้ากว่านิด (ใส่เฉพาะปลาย ไม่ใส่ที่ราก) ----------
// k=ความแข็งสปริง damp=หน่วง amt=แรงเหวี่ยงจากการเร่งของจุดหมุน max=มุมเบี่ยงสูงสุด(องศา) len=ความยาวชิ้น
const SPRINGS={hero:{sheath:{k:90,damp:9,amt:1,max:14,len:60},shF:{k:160,damp:12,amt:.6,max:8,len:25},shB:{k:160,damp:12,amt:.6,max:8,len:25}}};
const SP_DEF={k:120,damp:10,amt:1,max:30,len:30};
function spring(ch,dt){const S=ch.springs;if(!S||dt<=0)return;
  if(dt>.1){ch._sp=null;return;}                                   // แท็บค้าง/วาร์ป = รีเซ็ต
  const st=ch._sp||(ch._sp={}),M=world(ch.pose,ch.outfit&&ch.outfit.bones),sc=ch.scale||1,D=Math.PI/180;
  let out=null;
  for(const n in S){const m=M[n];if(!m)continue;const c={...SP_DEF,...S[n]},tgt=m.a,
      px=ch.x/(ch.dir*sc)+m.x,py=ch.y/sc+m.y+(ch.pose.rootY||0)*.5;   // จุดหมุนในพิกัดตัวละคร (ฝั่งที่หันอยู่)
    let s=st[n];if(!s){st[n]={a:tgt,v:0,px,py,vx:0,vy:0};continue;}
    const vx=(px-s.px)/dt,vy=(py-s.py)/dt,ax=(vx-s.vx)/dt,ay=(vy-s.vy)/dt;s.px=px;s.py=py;s.vx=vx;s.vy=vy;
    const n2=Math.max(1,Math.ceil(dt/(1/120))),h=dt/n2,lim=c.max*D;
    for(let i=0;i<n2;i++){const acc=c.k*(tgt-s.a)-c.damp*s.v-c.amt*(ax*Math.cos(s.a)+ay*Math.sin(s.a))/c.len;
      s.v+=acc*h;s.a+=s.v*h;
      if(s.a-tgt>lim){s.a=tgt+lim;s.v=Math.min(0,s.v);}else if(tgt-s.a>lim){s.a=tgt-lim;s.v=Math.max(0,s.v);}}
    (out||(out={...ch.pose}))[n]=(ch.pose[n]||0)+(s.a-tgt)/D;}
  if(out)ch.pose=out;}

// ---------- ผม/ผ้า = โซ่สปริง 3 ค่า (Night Camp phys: [กระดูก, ความหนืด, ความแข็ง, การหน่วง]) ----------
// chain: {at:กระดูกที่ผูก, off:[x,y] จุดผูกบนกระดูก, rest:มุมห้อย (องศา 0=ลง 90=ไปหลัง), n:จำนวนข้อ, len:ยาว/ข้อ (หน่วย rig)
//   visc ความหนืด 0..1 (มาก = ไหลตามช้า ลากหาง), stiff ความแข็ง (ดึงกลับรูปเดิม), damp การหน่วง 0..1 (เหลือความเร็วกี่ส่วน/เฟรม 60fps)
//   w0,w1 ความกว้างโคน/ปลาย, col สี, line สีเส้นขอบ, front วาดหน้าตัว}
const CHAIN_DEF={rest:70,n:5,len:9,visc:.5,stiff:140,damp:.85,w0:10,w1:3,col:'#c0392b',line:'#2a1418',grav:120};
function anchor(ch,M,C){const m=M[C.at],sc=ch.scale||1,FT=(ch.outfit&&ch.outfit.foot)||FOOT,o=C.off||[0,0],c=Math.cos(m.a),s=Math.sin(m.a),
    x=m.x+o[0]*c-o[1]*s,y=m.y+o[0]*s+o[1]*c;
  return {x:ch.x+ch.dir*sc*x,y:ch.y-FT*sc+(ch.pose.rootY||0)*sc*.5+sc*y,a:m.a};}
function chains(ch,dt){if(dt<=0)return;const M=world(ch.pose,ch.outfit&&ch.outfit.bones),sc=ch.scale||1,reset=dt>.1;
  for(const C0 of ch.chains){const C={...CHAIN_DEF,...C0},A=anchor(ch,M,C),L=C.len*sc,D=Math.PI/180;
    // ทิศห้อยตอนนิ่ง: หมุนตามกระดูกที่ผูก (หันซ้าย = กลับด้าน)
    const ra=(C.rest*D+A.a*(C.follow??.5))*ch.dir,rx=Math.sin(-ra),ry=Math.cos(ra);
    let P=C0._p;if(!P||reset||P.length!==C.n+1){P=C0._p=[];for(let i=0;i<=C.n;i++)P.push({x:A.x+rx*L*i,y:A.y+ry*L*i,vx:0,vy:0});}
    const prev={x:P[0].x,y:P[0].y};P[0].x=A.x;P[0].y=A.y;
    const mvx=(A.x-prev.x),mvy=(A.y-prev.y),h=Math.min(dt,1/30),dmp=Math.pow(C.damp,h*60);
    for(let i=1;i<=C.n;i++){const q=P[i],par=P[i-1],tx=par.x+rx*L,ty=par.y+ry*L;
      q.x+=mvx*(1-C.visc);q.y+=mvy*(1-C.visc);                               // ความหนืด: ตามจุดผูกแค่บางส่วน ที่เหลือลากตามหลัง
      q.vx=(q.vx+C.stiff*(tx-q.x)*h)*dmp;q.vy=(q.vy+(C.stiff*(ty-q.y)+C.grav*sc)*h)*dmp;
      q.x+=q.vx*h;q.y+=q.vy*h;
      const ex=q.x-par.x,ey=q.y-par.y,d=Math.hypot(ex,ey)||1;q.x=par.x+ex/d*L;q.y=par.y+ey/d*L;}}}
function drawChains(c,ch,front){if(!ch.chains)return;const sc=ch.scale||1;
  for(const C0 of ch.chains){const C={...CHAIN_DEF,...C0},P=C0._p;if(!P||!!C.front!==front)continue;
    const n=P.length,L=[],R=[];for(let i=0;i<n;i++){const a=P[Math.max(0,i-1)],b=P[Math.min(n-1,i+1)],dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy)||1,
      w=(C.w0+(C.w1-C.w0)*i/(n-1))*sc*.5;L.push([P[i].x-dy/d*w,P[i].y+dx/d*w]);R.push([P[i].x+dy/d*w,P[i].y-dx/d*w]);}
    c.save();c.beginPath();c.moveTo(L[0][0],L[0][1]);for(let i=1;i<n;i++){const m=[(L[i-1][0]+L[i][0])/2,(L[i-1][1]+L[i][1])/2];c.quadraticCurveTo(L[i-1][0],L[i-1][1],m[0],m[1]);}
    c.lineTo(L[n-1][0],L[n-1][1]);c.lineTo(R[n-1][0],R[n-1][1]);for(let i=n-2;i>=0;i--){const m=[(R[i+1][0]+R[i][0])/2,(R[i+1][1]+R[i][1])/2];c.quadraticCurveTo(R[i+1][0],R[i+1][1],m[0],m[1]);}
    c.closePath();c.fillStyle=C.col;c.fill();c.lineJoin='round';c.lineWidth=2*sc;c.strokeStyle=C.line;c.stroke();c.restore();}}

// ---------- วาด ----------
function world(pose,bo){const M={};for(const n in B){const b=B[n],q=b.as||n,off=(bo&&bo[q])||b.off,P=b.p?M[b.p]:{x:0,y:0,a:0},c=Math.cos(P.a),s=Math.sin(P.a);
  M[n]={x:P.x+off[0]*c-off[1]*s,y:P.y+off[0]*s+off[1]*c,a:P.a+((pose[q]||0)+(WOFF[q]||0))*Math.PI/180};}return M;}
function pulse(t){const x=t%1.3;return Math.max(Math.exp(-((x-.15)**2)/.004),.7*Math.exp(-((x-.38)**2)/.004));}
function glowDraw(c,g,x,y,w,h,amt){if(!ok(g)||amt<=0)return;c.save();c.globalCompositeOperation='lighter';c.globalAlpha=Math.min(1,amt);c.drawImage(g,x,y,w,h);
  c.filter='blur(3px)';c.globalAlpha=Math.min(1,amt*.9);c.drawImage(g,x,y,w,h);c.filter='blur(9px)';c.globalAlpha=Math.min(1,amt*.7);c.drawImage(g,x,y,w,h);c.restore();}
const OFF={};function off(cv,id){const k=cv.width+'x'+cv.height+id;if(!OFF[k]){OFF[k]=document.createElement('canvas');OFF[k].width=cv.width;OFF[k].height=cv.height;}return OFF[k];}
// อาวุธของตระกูลที่ยังไม่มีภาพ: วาดด้วยรูปทรงง่ายๆ (จุดจับที่ 0,0 ใบชี้ขึ้น -y) — เส้นขอบหนาตาม STYLE LOCK
function drawWeapon(c,F,sc){const L=F.len,up=L*F.grip,dn=L-up,ol='#1b1420';c.save();c.lineJoin=c.lineCap='round';c.lineWidth=2.4;c.strokeStyle=ol;
  const poly=(pts,f)=>{c.beginPath();pts.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fillStyle=f;c.fill();c.stroke();};
  const shaft=(y0,y1,w,f)=>poly([[-w,y0],[w,y0],[w,y1],[-w,y1]],f);
  if(F.shape==='sword'||F.shape==='dagger'){const bw=F.shape==='dagger'?3.2:4.2;shaft(dn,-2,2,'#5a3a24');poly([[-bw,-4],[bw,-4],[bw*.8,-up+bw*2.4],[0,-up],[-bw*.8,-up+bw*2.4]],F.col);
    c.beginPath();c.moveTo(0,-6);c.lineTo(0,-up+bw*3);c.lineWidth=1;c.strokeStyle='rgba(255,255,255,.7)';c.stroke();c.lineWidth=2.4;c.strokeStyle=ol;
    poly([[-bw*2.6,-6],[bw*2.6,-6],[bw*2.6,-2],[-bw*2.6,-2]],'#c9a24a');c.beginPath();c.arc(0,dn+1.5,2.6,0,7);c.fillStyle='#c9a24a';c.fill();c.stroke();}
  else if(F.shape==='spear'){shaft(dn,-up+16,1.8,'#7a5232');poly([[0,-up],[5,-up+10],[2.4,-up+19],[-2.4,-up+19],[-5,-up+10]],F.col);poly([[-4,-up+19],[4,-up+19],[3,-up+23],[-3,-up+23]],'#c9a24a');}
  else if(F.shape==='staff'){shaft(dn,-up+8,2.2,F.col);c.beginPath();c.arc(0,-up+2,7,0,7);c.fillStyle=F.gem;c.fill();c.stroke();
    c.globalCompositeOperation='lighter';const g=c.createRadialGradient(0,-up+2,1,0,-up+2,20);g.addColorStop(0,'rgba(140,220,255,.8)');g.addColorStop(1,'rgba(0,0,0,0)');c.fillStyle=g;c.beginPath();c.arc(0,-up+2,20,0,7);c.fill();}
  else if(F.shape==='axe'){shaft(dn,-up+2,2.2,'#6b4428');poly([[1.5,-up+4],[18,-up-2],[22,-up+12],[18,-up+26],[1.5,-up+20]],F.col);poly([[-2.5,-up],[2.5,-up],[2.5,-up+24],[-2.5,-up+24]],'#8d939e');}
  c.restore();}
function drawPart(c,ch,bone,back){const O=ch.outfit,t=ch.t,ga=.35+.65*pulse(t)+ch.flash,F=famOf(ch);
  const inHand=ch.act||(ch.armed>0);
  if(F&&!F.img&&(bone==='sheath'||bone==='weapon')){if((bone==='weapon')!==!!inHand)return;
    if(bone==='sheath'){c.rotate((SHEATH.a+(F.len>90?-10:0))*Math.PI/180);c.scale(.85,.85);c.filter='brightness(.8)';}drawWeapon(c,F);c.filter='none';return;}
  if(bone==='fist'){if(!inHand||O.fist===false)return;const im=O.img.armF_l||O.img.arm_lower;if(!ok(im))return;
    const s=(O.spec&&O.spec.arm_lower)||SPEC.arm_lower,w=im.width*s.h/im.height*(s.sx||1),x=-s.px*w,y=-s.py*s.h,cut=O.fistCut??.74;
    c.save();c.beginPath();c.rect(x-2,y+cut*s.h,w+4,s.h*(1-cut)+2);c.clip();c.drawImage(im,x,y,w,s.h);c.restore();return;}
  if(bone==='sheath'){if(inHand||!O.sword||!ok(O.sword))return;const ws=GEAR.sword,ww=O.sword.width*ws.h/O.sword.height;c.rotate(SHEATH.a*Math.PI/180);c.scale(SHEATH.s,SHEATH.s);
    c.filter='brightness(.8)';c.drawImage(O.sword,-ws.px*ww,-ws.py*ws.h,ww,ws.h);c.filter='none';return;}
  if(bone==='weapon'){if(!inHand||!O.sword||!ok(O.sword))return;const ws=GEAR.sword,ww=O.sword.width*ws.h/O.sword.height;c.scale(-1,1);
    c.drawImage(O.sword,-ws.px*ww,-ws.py*ws.h,ww,ws.h);glowDraw(c,O.swordGlow,-ws.px*ww,-ws.py*ws.h,ww,ws.h,ga);return;}
  const key=PART_OF[bone];let im=(!ch.moving&&!ch.act&&O.idleImg&&ok(O.idleImg[bone])&&O.idleImg[bone])||O.img[bone]||O.img[key];if((bone==='legF_l'||bone==='legB_l')&&ok(O.leg))im=O.leg;if(!ok(im))return;
  const s=(O.spec&&O.spec[key])||SPEC[key],w=im.width*s.h/im.height*(s.sx||1),sc=back?.92:1,sq=(bone==='torso'||bone==='head')?1+(ch.pose.sq||0):1,x=-s.px*w,y=-s.py*s.h;
  c.scale(sc/Math.sqrt(sq),sc*sq);if(back)c.filter='brightness(.68) saturate(.85)';
  if(bone==='head'&&O.helmet&&ok(O.helmMask)&&ok(O.hair)){ // ซ่อนเฉพาะผมที่โผล่นอกหมวก
    const hs=GEAR.helm,hw=O.helmMask.width*hs.h/O.helmMask.height,hx=-hs.px*hw+hs.dx,hy=-hs.py*hs.h+hs.dy,T=c.getTransform();
    const A=off(c.canvas,'a'),a=A.getContext('2d'),Bc=off(c.canvas,'b'),b=Bc.getContext('2d');
    for(const z of [a,b]){z.setTransform(1,0,0,1,0,0);z.clearRect(0,0,A.width,A.height);z.setTransform(T);}
    b.drawImage(O.hair,x,y,w,s.h);b.globalCompositeOperation='destination-out';b.drawImage(O.helmMask,hx,hy,hw,hs.h);b.globalCompositeOperation='source-over';
    a.drawImage(im,x,y,w,s.h);a.setTransform(1,0,0,1,0,0);a.globalCompositeOperation='destination-out';a.drawImage(Bc,0,0);a.globalCompositeOperation='source-over';
    c.save();c.setTransform(1,0,0,1,0,0);c.drawImage(A,0,0);c.restore();
  } else c.drawImage(im,x,y,w,s.h);
  c.filter='none';
  if(O.glow[key])glowDraw(c,O.glow[key],x,y,w,s.h,ga*(back?.5:1));
  if(bone==='head'&&O.helmet){const hi=ch.visor?O.helmClosed:O.helmOpen;if(ok(hi)){const hs=GEAR.helm,hw=hi.width*hs.h/hi.height,hx=-hs.px*hw+hs.dx,hy=-hs.py*hs.h+hs.dy;
    c.drawImage(hi,hx,hy,hw,hs.h);if(ch.visor)glowDraw(c,O.helmGlow,hx,hy,hw,hs.h,ga*1.3);}}}
function draw(c,ch){const s=ch.scale,p=ch.pose,O=ch.outfit,M=world(p,O.bones),FT=O.foot||FOOT;
  c.save();c.translate(ch.x,ch.y);c.fillStyle='rgba(0,0,0,.35)';c.beginPath();c.ellipse(0,0,30*s,7*s,0,0,7);c.fill();c.restore();
  const inHand=ch.act||(ch.armed>0),ord=inHand&&O.fist!==false?ORDER_FIST:ORDER;
  drawChains(c,ch,false);
  c.save();c.translate(ch.x,ch.y-FT*s+(p.rootY||0)*s*.5);c.scale(ch.dir*s,s);
  for(const n of ord){const m=M[n];c.save();c.translate(m.x,m.y);c.rotate(m.a);drawPart(c,ch,n,n.includes('B_')||n==='shB');c.restore();}
  c.restore();drawChains(c,ch,true);
  return {head:{x:ch.x,y:ch.y-(FT+60)*s}};}
window.RIG={loadOutfit,makeChar,play,update,SPRINGS,draw,loadClips,CLIPS,READY,idle,walk,gait,FOOT,world,B,SHEATH,
  alive,ik2,FAMILY,applyAim,atkClip}; // world/B/SHEATH = ใช้ตรวจ/จูนท่า
})();
