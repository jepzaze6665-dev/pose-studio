"""สร้าง rig/pose_studio.html จาก rig/rig_lab.html (ใช้ rig + ชุด + ระบบวาดเดียวกัน — หลักที่ 13: เครื่องมือใช้โค้ดเดียวกับเกม)
usage: python tools/build_pose_studio.py
"""
import os
here = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(here, '..', 'rig', 'rig_lab.html')
dst = os.path.join(here, '..', 'rig', 'pose_studio.html')
s = open(src, encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)

# ---------- layout ----------
css_start = s.index('<style>'); css_end = s.index('</style>') + len('</style>')
s = s[:css_start] + r'''<style>
:root{--bg:#121019;--panel:#1b1828;--panel2:#221f33;--line:#2e2a45;--text:#ece8ff;--dim:#8f88b3;--acc:#ffb347;--key:#ffd166;--sel:#ff5a7a}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,"Segoe UI",Tahoma,sans-serif;font-size:13px}
.app{display:grid;grid-template-columns:230px 1fr 290px;grid-template-rows:44px 1fr;height:100vh;gap:1px;background:var(--line)}
.top{grid-column:1/4;background:var(--panel);display:flex;align-items:center;gap:12px;padding:0 14px}
.top h1{font-size:15px;margin:0}.top .sub{color:var(--dim)}
.top .sp{flex:1}
.col{background:var(--panel);overflow:auto;padding:10px;display:flex;flex-direction:column;gap:10px}
.mid{background:var(--bg);display:flex;flex-direction:column;min-width:0}
.sec{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:10px}
.sec h3{margin:0 0 8px;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--dim)}
.list button{display:block;width:100%;text-align:left;margin-bottom:4px}
.list .tag{float:right;font-size:10px;color:var(--dim)}
.row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
button{background:#2a2640;color:var(--text);border:1px solid var(--line);border-radius:7px;padding:5px 9px;cursor:pointer;font:inherit}
button:hover{border-color:#4a4470}
button.on{background:var(--acc);border-color:var(--acc);color:#1a1200}
button.pri{background:#3b6cff;border-color:#3b6cff}
label{color:var(--dim);display:flex;justify-content:space-between;gap:8px;align-items:center;margin:3px 0}
input[type=range]{width:120px}
input[type=number],input[type=text],select{background:#14121f;color:var(--text);border:1px solid var(--line);border-radius:6px;padding:3px 6px;font:inherit;width:90px}
.toolbar{display:flex;gap:6px;align-items:center;padding:8px 10px;background:var(--panel);border-bottom:1px solid var(--line);flex-wrap:wrap}
.toolbar label{margin:0}
.stage{flex:1;display:flex;align-items:center;justify-content:center;min-height:0;padding:8px}
canvas#view{background:#0d0c16;border-radius:10px;max-width:100%;max-height:100%;border:1px solid var(--line)}
.tl{background:var(--panel);border-top:1px solid var(--line);padding:8px 12px}
.tlbar{position:relative;height:46px;background:#14121f;border:1px solid var(--line);border-radius:8px;cursor:pointer;margin-top:6px}
.tick{position:absolute;top:0;bottom:0;width:1px;background:#2a2640}
.tick span{position:absolute;bottom:2px;left:3px;font-size:9px;color:#5c5680}
.kf{position:absolute;top:11px;width:14px;height:14px;margin-left:-7px;background:var(--key);transform:rotate(45deg);border:2px solid #14121f;cursor:grab}
.kf.sel{background:var(--sel)}
.head{position:absolute;top:-4px;bottom:-4px;width:2px;background:#fff;pointer-events:none}
.head::before{content:'';position:absolute;top:-2px;left:-5px;border:6px solid transparent;border-top-color:#fff}
.sl{display:flex;flex-direction:column}
.sl label b{width:32px;text-align:right;color:var(--text)}
.drop{border:2px dashed #4a4470;border-radius:8px;padding:8px;font-size:11px;color:var(--dim);text-align:center}
.drop.hot{border-color:var(--acc);color:var(--text)}
.status{font-size:11px;padding:2px 8px;border-radius:99px}
.status.dirty{background:#5a4a10;color:#ffd166}.status.saved{background:#163a24;color:#7be39b}
code{color:#ffd28a}
.hint{color:var(--dim);font-size:11px;line-height:1.5}
@media (max-width:900px){.app{grid-template-columns:1fr;grid-template-rows:auto}.top{grid-column:1}}
</style>''' + s[css_end:]

b0 = s.index('<body>') + len('<body>'); b1 = s.index('<script>')
s = s[:b0] + r'''
<div class="app">
  <div class="top"><h1>Pose Studio</h1><span class="sub">ใช้ตัวละคร + โค้ดเดียวกับเกม · บันทึกแล้วเข้าเกมทันที</span>
    <span class="sp"></span><span id="status" class="status saved">บันทึกแล้ว</span>
    <button id="btnSave" class="pri">บันทึก (Ctrl+S)</button><button id="btnExport">ส่งออก JSON</button></div>

  <div class="col">
    <div class="sec"><h3>ท่าทาง (Clips)</h3><div class="list" id="clipList"></div>
      <div class="row"><button id="btnNew">+ ท่าใหม่</button><button id="btnDup">ทำสำเนา</button><button id="btnDel">ลบ</button></div></div>
    <div class="sec"><h3>เทมเพลตจากเกม</h3><div class="list" id="tplList"></div>
      <div class="hint">กดเพื่อเล่น · "แปลงเป็นคีย์" เพื่อแก้ทีละคีย์</div></div>
    <div class="sec"><h3>ชุด (Outfit)</h3><div class="row" id="outfits"></div></div>
    <div class="sec"><h3>ขาหน้า</h3><div class="row" id="legs">
      <button data-l="leg_lower_1">หันหาจอ</button><button data-l="leg_lower_2">เฉียง</button><button data-l="leg_lower_3" class="on">หันขวา</button></div></div>
  </div>

  <div class="mid">
    <div class="toolbar">
      <button id="btnPlay">⏸</button>
      <label><input type="checkbox" id="bones" checked> Bone</label>
      <label><input type="checkbox" id="onion"> Onion</label>
      <label><input type="checkbox" id="flip"> Flip</label>
      <label><input type="checkbox" id="slow"> ช้า ×5</label>
      <label><input type="checkbox" id="pixel"> พิกเซล</label>
      <label><input type="checkbox" id="hidehair" checked> ซ่อนผมใต้หมวก</label>
      <span class="sp" style="flex:1"></span>
      <button id="atk">⚔ ทดสอบฟัน (J)</button>
    </div>
    <div class="stage"><canvas id="view" width="760" height="520"></canvas></div>
    <div class="tl">
      <div class="row"><b id="clipName">-</b><span class="hint" id="tinfo"></span><span style="flex:1"></span>
        <button id="btnKey">◆ ใส่คีย์ (K)</button><button id="btnDelKey">ลบคีย์ (Del)</button>
        <button id="btnPrev">◀ คีย์ก่อน</button><button id="btnNext">คีย์ถัดไป ▶</button></div>
      <div class="tlbar" id="tlbar"></div>
    </div>
  </div>

  <div class="col">
    <div class="sec"><h3>Clip</h3>
      <label>ชื่อ <input type="text" id="cName"></label>
      <label>ความยาว (วินาที) <input type="number" id="cLen" step="0.05" min="0.1"></label>
      <label>ความเร็ว <input type="number" id="cSpeed" step="0.1" min="0.1" value="1"></label>
      <label>FPS (0 = ลื่น) <input type="number" id="cFps" step="1" min="0" value="0"></label>
      <label>วนซ้ำ <input type="checkbox" id="cLoop" checked></label></div>
    <div class="sec"><h3>Keyframe ที่เลือก</h3>
      <label>เวลา <input type="number" id="kTime" step="0.01"></label>
      <label>เส้นโค้งเข้าคีย์นี้ <select id="ease"><option value="exp">ระเบิด (ease-out)</option><option value="inout" selected>นุ่ม เข้า-ออก</option><option value="lin">เส้นตรง</option><option value="hold">ค้าง (step)</option></select></label>
      <label>เหตุการณ์ <select id="kEvt"><option value="">-</option><option value="hit">โดน (ดาเมจ+สั่น)</option></select></label></div>
    <div class="sec"><h3>กระดูก (องศา)</h3><div class="sl" id="sliders"></div>
      <div class="row" style="margin-top:6px"><button id="btnReady">ท่าพร้อมสู้</button><button id="btnMirror">สลับซ้าย-ขวา</button></div></div>
    <div class="sec"><h3>คีย์ลัด</h3><div class="hint">Space เล่น/หยุด · K ใส่คีย์ · Del ลบคีย์ · , . คีย์ก่อน/ถัดไป · ← → เลื่อนทีละเฟรม · Ctrl+S บันทึก · Ctrl+Z ย้อน · J ทดสอบฟัน · U หน้ากาก</div></div>
    <div class="sec"><div class="drop" id="drop">ลาก PNG ชิ้นส่วนมาวาง<br><code>head torso arm_upper arm_lower leg_upper leg_lower</code></div></div>
    <div style="display:none"><input type="checkbox" id="badorder"><input type="checkbox" id="badpivot"><input type="checkbox" id="hybrid" checked><input type="checkbox" id="pquant" checked><input type="range" id="psize" value="4"><div id="anims"></div></div>
  </div>
</div>
''' + s[b1:]

# ---------- keyframe clip system ----------
rep("const E={lin:s=>s,", "const E={hold:s=>0,lin:s=>s,")
rep("const pose=base; curPose=pose;", "const pose=studioPose(base); curPose=pose;")
rep("  if(anim==='pose'||!attack) syncSliders(pose);", "  if(!attack) syncSliders(pose);")
rep("ctx.scale(dir*2,2);", "ctx.scale(dir*(document.getElementById('flip').checked?-2:2),2);\n  if(document.getElementById('onion').checked&&clip&&!attack) drawOnion();")
rep("  // hud\n  ctx.fillStyle='#9a93bd';ctx.font='13px system-ui';\n  ctx.fillText(attack?['ง้าง','ฟัน','หยุดภาพ (hitstop)','ตามแรง','คืนท่า'][phaseName()]+'  · คอมโบ '+(attack.i+1)+'/3':'J = โจมตี',16,24);",
    "  updateTimeline();")
rep("  const moving=keys.ArrowLeft||keys.ArrowRight;", "  const moving=false; if(playing&&clip) playT+=dt*(clip.speed||1);")

ui_start = s.index('// ---------- UI ----------'); ui_end = s.index('</script>')
s = s[:ui_start] + r'''// ---------- POSE STUDIO ----------
const BONES=SL.map(x=>x[0]).concat(['rootY']);
SL.push(['rootY','ยกตัว (rootY)']);
let clips=[], clip=null, playing=true, playT=0, selKey=-1, undoStack=[], dirty=false;
const TPL={ 'ยืนหายใจ':t=>idle(t), 'เดิน':t=>walk(t) };
function cleanPose(p){const r={};for(const k of BONES)r[k]=Math.round((p[k]||0)*10)/10;return r;}
function atkClip(i){const k=ATK[i],st=k.big?TM.stop*1.8:TM.stop;let t=0;const keys=[{t:0,pose:cleanPose(READY),ease:'inout'}];
  t+=TM.wind;keys.push({t,pose:cleanPose(k.wind),ease:'inout'});t+=TM.strike;keys.push({t,pose:cleanPose(k.hit),ease:'exp',evt:'hit'});
  t+=st+TM.follow;keys.push({t,pose:cleanPose(k.hit),ease:'hold'});t+=TM.rec;keys.push({t,pose:cleanPose(READY),ease:'out'});
  return {name:'โจมตี '+(i+1)+(k.big?' (ปิดคอมโบ)':''),len:+t.toFixed(2),speed:1,fps:0,loop:false,keys:keys.map(x=>({...x,t:+x.t.toFixed(3)}))};}
function defaultClips(){return [atkClip(0),atkClip(1),atkClip(2),
  {name:'ท่าพร้อมสู้',len:1,speed:1,fps:0,loop:true,keys:[{t:0,pose:cleanPose(READY),ease:'inout'}]}];}
function load(){try{const j=JSON.parse(localStorage.getItem('poseStudio.clips')||'null');if(j&&j.length)return j;}catch(e){}return defaultClips();}
clips=load();
function easeOf(n){return E[n]||E.inout;}
function samplePose(c,t){const K=c.keys;if(!K.length)return cleanPose(READY);
  if(c.fps>0)t=Math.floor(t*c.fps)/c.fps;
  if(t<=K[0].t)return K[0].pose; if(t>=K[K.length-1].t)return K[K.length-1].pose;
  for(let i=0;i<K.length-1;i++){const a=K[i],b=K[i+1];if(t>=a.t&&t<=b.t){const s=(t-a.t)/Math.max(1e-6,b.t-a.t);return lerpPose(a.pose,b.pose,easeOf(b.ease)(s));}}
  return K[K.length-1].pose;}
let tplName=null, lastEvtT=-1;
function studioPose(base){
  if(attack) return base;
  if(tplName) return TPL[tplName](simT);
  if(!clip) return base;
  if(clip.loop) playT=((playT%clip.len)+clip.len)%clip.len; else if(playT>clip.len){playT=playing?0:clip.len;}
  // events: เฟรมโดน -> ดาเมจ + เสียง + FX พร้อมกัน
  if(playing){for(const k of clip.keys){if(k.evt==='hit'&&lastEvtT<k.t&&playT>=k.t){onHit({big:/ปิด/.test(clip.name)},simT);}} }
  lastEvtT=playT;
  return samplePose(clip,playT);
}
function drawOnion(){const K=clip.keys;let i=K.findIndex(k=>k.t>playT+1e-4);const prev=i<0?K[K.length-1]:K[i-1],next=i<0?null:K[i];
  for(const [k,col] of [[prev,'rgba(120,200,255,.55)'],[next,'rgba(255,140,120,.55)']]){if(!k)continue;const M=world(k.pose);
    ctx.save();ctx.lineWidth=3;ctx.strokeStyle=col;for(const n in B){const b=B[n];if(!b.p||n==='shB'||n==='shF')continue;ctx.beginPath();ctx.moveTo(M[b.p].x,M[b.p].y+(k.pose.rootY||0)/2);ctx.lineTo(M[n].x,M[n].y+(k.pose.rootY||0)/2);ctx.stroke();}ctx.restore();}}
// ---- UI ----
const $=id=>document.getElementById(id);
function markDirty(){dirty=true;$('status').className='status dirty';$('status').textContent='ยังไม่บันทึก';}
function save(){localStorage.setItem('poseStudio.clips',JSON.stringify(clips));dirty=false;$('status').className='status saved';$('status').textContent='บันทึกแล้ว';}
function pushUndo(){undoStack.push(JSON.stringify(clips));if(undoStack.length>60)undoStack.shift();}
function undo(){if(!undoStack.length)return;const ci=clips.indexOf(clip);clips=JSON.parse(undoStack.pop());clip=clips[Math.max(0,ci)];selKey=-1;renderLists();renderClip();markDirty();}
function renderLists(){
  const cl=$('clipList');cl.innerHTML='';clips.forEach((c,i)=>{const b=document.createElement('button');b.innerHTML=c.name+`<span class="tag">${c.keys.length} คีย์</span>`;b.className=c===clip?'on':'';b.onclick=()=>selectClip(c);cl.append(b);});
  const tl=$('tplList');tl.innerHTML='';for(const n in TPL){const b=document.createElement('button');b.innerHTML=n+'<span class="tag">procedural</span>';b.className=tplName===n?'on':'';
    b.onclick=()=>{tplName=n;clip=null;renderLists();renderClip();};tl.append(b);}
  const conv=document.createElement('button');conv.textContent='แปลงเดินเป็นคีย์ (8 คีย์)';conv.onclick=()=>{pushUndo();const keys=[];for(let i=0;i<=8;i++){const t=i/8/1.15;keys.push({t:+t.toFixed(3),pose:cleanPose(walk(t)),ease:'lin'});}
    const c={name:'เดิน (คีย์)',len:+(1/1.15).toFixed(3),speed:1,fps:0,loop:true,keys};clips.push(c);selectClip(c);markDirty();};tl.append(conv);}
function selectClip(c){clip=c;tplName=null;playT=0;selKey=-1;renderLists();renderClip();}
function renderClip(){
  $('clipName').textContent=clip?clip.name:(tplName?tplName+' (procedural — แก้ไม่ได้)':'-');
  for(const id of ['cName','cLen','cSpeed','cFps','cLoop','kTime','ease','kEvt'])$(id).disabled=!clip;
  if(clip){$('cName').value=clip.name;$('cLen').value=clip.len;$('cSpeed').value=clip.speed||1;$('cFps').value=clip.fps||0;$('cLoop').checked=!!clip.loop;}
  const k=clip&&clip.keys[selKey];$('kTime').value=k?k.t:'';$('ease').value=k?(k.ease||'inout'):'inout';$('kEvt').value=k?(k.evt||''):'';
  const bar=$('tlbar');bar.innerHTML='';if(!clip)return;
  const L=clip.len;for(let i=0;i<=10;i++){const d=document.createElement('div');d.className='tick';d.style.left=(i*10)+'%';d.innerHTML=`<span>${(L*i/10).toFixed(2)}</span>`;bar.append(d);}
  clip.keys.forEach((k,i)=>{const d=document.createElement('div');d.className='kf'+(i===selKey?' sel':'');d.style.left=(k.t/L*100)+'%';d.title=k.t+'s · '+(k.ease||'');
    d.onmousedown=e=>{e.stopPropagation();selKey=i;playing=false;playT=k.t;$('btnPlay').textContent='▶';renderClip();dragKey(e,i);};bar.append(d);});
  const h=document.createElement('div');h.className='head';h.id='phead';bar.append(h);
}
function dragKey(e,i){const bar=$('tlbar'),r=bar.getBoundingClientRect();let moved=false;pushUndo();
  const mv=ev=>{moved=true;const k=clip.keys[i];k.t=+Math.max(0,Math.min(clip.len,(ev.clientX-r.left)/r.width*clip.len)).toFixed(3);playT=k.t;
    sortKeys(k);renderClip();markDirty();};
  const up=()=>{removeEventListener('mousemove',mv);removeEventListener('mouseup',up);if(!moved)undoStack.pop();};
  addEventListener('mousemove',mv);addEventListener('mouseup',up);}
function sortKeys(keep){clip.keys.sort((a,b)=>a.t-b.t);selKey=clip.keys.indexOf(keep);}
$('tlbar').onmousedown=e=>{if(!clip)return;const r=$('tlbar').getBoundingClientRect();const sc=ev=>{playT=Math.max(0,Math.min(clip.len,(ev.clientX-r.left)/r.width*clip.len));selKey=clip.keys.findIndex(k=>Math.abs(k.t-playT)<clip.len*.015);};
  playing=false;$('btnPlay').textContent='▶';sc(e);renderClip();const mv=ev=>{sc(ev);};const up=()=>{removeEventListener('mousemove',mv);removeEventListener('mouseup',up);renderClip();};addEventListener('mousemove',mv);addEventListener('mouseup',up);};
function updateTimeline(){const h=$('phead');if(h&&clip)h.style.left=(Math.min(playT,clip.len)/clip.len*100)+'%';
  $('tinfo').textContent=clip?`  ${playT.toFixed(2)} / ${clip.len}s`+(clip.fps?` · ${clip.fps} fps`:''):'';}
function setKeyAtPlayhead(fromPose){if(!clip)return;pushUndo();const t=+playT.toFixed(3);let i=clip.keys.findIndex(k=>Math.abs(k.t-t)<1e-3);
  const pose=cleanPose(fromPose||samplePose(clip,t));if(i<0){const k={t,pose,ease:'inout'};clip.keys.push(k);sortKeys(k);}else{clip.keys[i].pose=pose;selKey=i;}renderClip();renderLists();markDirty();}
// sliders edit the selected key (หรือสร้างคีย์ใหม่ที่หัวอ่าน)
const slBox=$('sliders'),SLI={};
for(const [k,n] of SL){const l=document.createElement('label');l.innerHTML=`<span>${n}</span>`;const r=document.createElement('input');r.type='range';r.min=k==='rootY'?-30:-270;r.max=k==='rootY'?30:270;r.step=1;
  const v=document.createElement('b');v.textContent='0';
  r.onpointerdown=()=>{if(!clip)return;playing=false;$('btnPlay').textContent='▶';};
  r.oninput=()=>{if(!clip)return;const t=+playT.toFixed(3);let i=clip.keys.findIndex(x=>Math.abs(x.t-t)<1e-3);
    if(i<0){setKeyAtPlayhead();i=selKey;} else if(selKey!==i){selKey=i;renderClip();}
    clip.keys[i].pose[k]=+r.value;v.textContent=r.value;markDirty();};
  r.onchange=()=>pushUndo();
  l.append(r,v);slBox.append(l);SLI[k]=[r,v];}
function syncSliders(p){for(const k in SLI){const val=Math.round(p[k]||0);if(document.activeElement!==SLI[k][0]&&+SLI[k][0].value!==val){SLI[k][0].value=val;SLI[k][1].textContent=val;}}}
function setAnim(){} // compat
$('cName').oninput=e=>{clip.name=e.target.value;renderLists();$('clipName').textContent=clip.name;markDirty();};
$('cLen').onchange=e=>{pushUndo();clip.len=Math.max(.1,+e.target.value);renderClip();markDirty();};
$('cSpeed').onchange=e=>{clip.speed=Math.max(.1,+e.target.value);markDirty();};
$('cFps').onchange=e=>{clip.fps=Math.max(0,+e.target.value|0);markDirty();};
$('cLoop').onchange=e=>{clip.loop=e.target.checked;markDirty();};
$('kTime').onchange=e=>{const k=clip.keys[selKey];if(!k)return;pushUndo();k.t=Math.max(0,Math.min(clip.len,+e.target.value));sortKeys(k);playT=k.t;renderClip();markDirty();};
$('ease').onchange=e=>{const k=clip&&clip.keys[selKey];if(!k)return;pushUndo();k.ease=e.target.value;renderClip();markDirty();};
$('kEvt').onchange=e=>{const k=clip&&clip.keys[selKey];if(!k)return;pushUndo();k.evt=e.target.value||undefined;markDirty();};
$('btnKey').onclick=()=>setKeyAtPlayhead(curPose);
function delKey(){if(!clip||selKey<0||clip.keys.length<2)return;pushUndo();clip.keys.splice(selKey,1);selKey=-1;renderClip();renderLists();markDirty();}
$('btnDelKey').onclick=delKey;
function jump(d){if(!clip)return;const K=clip.keys;let i=d>0?K.findIndex(k=>k.t>playT+1e-4):K.map(k=>k.t<playT-1e-4).lastIndexOf(true);if(i<0)return;playing=false;$('btnPlay').textContent='▶';playT=K[i].t;selKey=i;renderClip();}
$('btnPrev').onclick=()=>jump(-1);$('btnNext').onclick=()=>jump(1);
$('btnPlay').onclick=()=>{playing=!playing;$('btnPlay').textContent=playing?'⏸':'▶';if(playing&&clip&&!clip.loop&&playT>=clip.len)playT=0;lastEvtT=playT;};
$('btnNew').onclick=()=>{pushUndo();const c={name:'ท่าใหม่ '+(clips.length+1),len:1,speed:1,fps:0,loop:true,keys:[{t:0,pose:cleanPose(READY),ease:'inout'},{t:1,pose:cleanPose(READY),ease:'inout'}]};clips.push(c);selectClip(c);markDirty();};
$('btnDup').onclick=()=>{if(!clip)return;pushUndo();const c=JSON.parse(JSON.stringify(clip));c.name+=' (สำเนา)';clips.push(c);selectClip(c);markDirty();};
$('btnDel').onclick=()=>{if(!clip||!confirm('ลบท่า "'+clip.name+'" ?'))return;pushUndo();clips.splice(clips.indexOf(clip),1);clip=clips[0]||null;selKey=-1;renderLists();renderClip();markDirty();};
$('btnReady').onclick=()=>{if(!clip)return;setKeyAtPlayhead(READY);};
$('btnMirror').onclick=()=>{if(!clip||selKey<0)return;pushUndo();const p=clip.keys[selKey].pose;for(const [a,b] of [['armF_u','armB_u'],['armF_l','armB_l'],['legF_u','legB_u'],['legF_l','legB_l']]){const t=p[a];p[a]=p[b];p[b]=t;}markDirty();};
$('btnSave').onclick=save;
$('btnExport').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify({rig:'chibi-v1',clips},null,1)],{type:'application/json'}));a.download='clips.json';a.click();};
$('atk').onclick=()=>startAttack(simT);
const ob=$('outfits');for(const n in OUT){const b=document.createElement('button');b.textContent=n;b.className=n===outfit?'on':'';b.onclick=()=>{outfit=n;applyBody(OUT[n].body||'doodle');ob.querySelectorAll('button').forEach(x=>x.classList.toggle('on',x===b));};ob.append(b);}
document.querySelectorAll('#legs button').forEach(b=>b.onclick=()=>{frontLeg=b.dataset.l;document.querySelectorAll('#legs button').forEach(x=>x.classList.toggle('on',x===b));});
addEventListener('keydown',e=>{const tag=(e.target.tagName||'');if(tag==='INPUT'&&e.target.type!=='range'&&e.target.type!=='checkbox'||tag==='SELECT')return;
  if(e.ctrlKey&&e.key.toLowerCase()==='s'){e.preventDefault();save();return;}
  if(e.ctrlKey&&e.key.toLowerCase()==='z'){e.preventDefault();undo();return;}
  if(e.key===' '){e.preventDefault();$('btnPlay').click();}
  else if(e.key==='k'||e.key==='K')setKeyAtPlayhead(curPose);
  else if(e.key==='Delete')delKey();
  else if(e.key===',')jump(-1); else if(e.key==='.')jump(1);
  else if((e.key==='ArrowLeft'||e.key==='ArrowRight')&&clip&&e.target.type!=='range'){e.preventDefault();playing=false;$('btnPlay').textContent='▶';playT=Math.max(0,Math.min(clip.len,playT+(e.key==='ArrowLeft'?-1:1)/(clip.fps||30)));selKey=clip.keys.findIndex(k=>Math.abs(k.t-playT)<1e-3);renderClip();}
  else if(e.key==='j'||e.key==='J')startAttack(simT);});
addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
const drop=$('drop');
drop.ondragover=e=>{e.preventDefault();drop.classList.add('hot');};drop.ondragleave=()=>drop.classList.remove('hot');
drop.ondrop=e=>{e.preventDefault();drop.classList.remove('hot');let n=0;
  for(const f of e.dataTransfer.files){const key=f.name.replace(/\.png$/i,'').toLowerCase();if(!SPEC[key])continue;
    const im=new Image();im.onload=()=>IMG[key]=im;im.src=URL.createObjectURL(f);n++;}
  drop.innerHTML=`โหลดแล้ว ${n} ชิ้น`;};
applyBody(OUT[outfit].body||'doodle');
selectClip(clips[0]);
requestAnimationFrame(frame);
''' + s[ui_end:]

# ---------- VFX skills bound to keyframe events ----------
def rep2(a,b):
    global s
    assert a in s, a[:80]
    s=s.replace(a,b,1)
rep2('<script>','<script src="../vfx/vfx_runtime.js"></script>\n<script>')
rep2('const dummy={x:540,','const dummy={x:640,')
rep2('posX=420,','posX=330,')
rep2('<option value="hit">','<option value="swarm">สกิล: ฝูงอสูรเงา</option><option value="hit">')
rep2("  drawDummy(simT);\n","  VFX.tick(dt); if(VFX.shakeReq){shake=Math.max(shake,VFX.shakeReq);VFX.shakeReq=0;}\n  VFX.draw(ctx,0,view.width,view.height);\n  drawDummy(simT);\n")
rep2("  if(!hdfx) drawFx(simT);","  VFX.draw(ctx,1,view.width,view.height);\n  if(!hdfx) drawFx(simT);")
rep2("  updateTimeline();","  VFX.draw(mctx,2,view.width,view.height);\n  updateTimeline();")
rep2("if(k.evt==='hit'&&lastEvtT<k.t&&playT>=k.t){","if(k.evt==='swarm'&&lastEvtT<k.t&&playT>=k.t){VFX.play('swarm',{x:posX,y:440,tx:dummy.x,ty:dummy.y-70});}\n    if(k.evt==='hit'&&lastEvtT<k.t&&playT>=k.t){")
# default clip: cast pose that fires the swarm skill
rep2("function defaultClips(){return [atkClip(0),atkClip(1),atkClip(2),",
 "function swarmClip(){const cast={...READY,armF_u:-150,armF_l:-20,weapon:-10,torso:-6,head:-8,armB_u:-40,legF_u:-20,legB_u:18,rootY:-2};\n"
 "  return {name:'สกิล: ฝูงอสูรเงา',len:3.6,speed:1,fps:0,loop:false,keys:[{t:0,pose:cleanPose(READY),ease:'inout'},{t:.35,pose:cleanPose(cast),ease:'exp',evt:'swarm'},{t:2.4,pose:cleanPose(cast),ease:'hold'},{t:3.0,pose:cleanPose(READY),ease:'inout'}]};}\n"
 "function defaultClips(){return [swarmClip(),atkClip(0),atkClip(1),atkClip(2),")
rep2("clips=load();","clips=load(); if(!clips.some(c=>c.keys.some(k=>k.evt==='swarm')))clips.unshift(swarmClip());")
s = s.replace('<title>Rig Lab</title>', '<title>Pose Studio</title>')
open(dst, 'w', encoding='utf-8').write(s)
print('wrote', dst)
