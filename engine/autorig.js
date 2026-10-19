// =====================================================================
//  AUTO RIG — ภาพเดียวขยับด้วยกระดูก โดยไม่ต้องตัดชิ้น (สำหรับมอน/บอส)
//  แนวคิดจากการแกะ Night Camp (meshrig.js): mesh ตาราง + น้ำหนักกระดูกจาก "ระยะเดินบนเนื้อภาพ"
//  AUTORIG.build(img, bones, {grid})   bones=[{n, p:ชื่อพ่อ|null, h:[x,y] หัว, t:[x,y] ปลาย}] พิกัดพิกเซลของภาพ (พ่อมาก่อนลูก)
//  AUTORIG.draw(ctx, rig, pose, x, y, {scale, flip, debug})   pose={กระดูก:{r:องศา, x, y, s}}
// =====================================================================
(function(){
// ระยะเดินบนเนื้อภาพ (geodesic): หูซ้ายกับหัวอยู่ใกล้กันบนจอ แต่ต้องเดินผ่านโคนหู → ขยับหูแล้วหัวไม่ยืดตาม
function geodesic(mask,W,H,seeds){const D=new Float32Array(W*H).fill(1e9),heap=[];
  const push=(d,i)=>{heap.push([d,i]);let k=heap.length-1;while(k>0){const p=(k-1)>>1;if(heap[p][0]<=heap[k][0])break;[heap[p],heap[k]]=[heap[k],heap[p]];k=p;}};
  const pop=()=>{const top=heap[0],last=heap.pop();if(heap.length){heap[0]=last;let k=0;for(;;){const l=2*k+1,r=l+1;let m=k;if(l<heap.length&&heap[l][0]<heap[m][0])m=l;if(r<heap.length&&heap[r][0]<heap[m][0])m=r;if(m===k)break;[heap[m],heap[k]]=[heap[k],heap[m]];k=m;}}return top;};
  for(const i of seeds){D[i]=0;push(0,i);}
  const N=[[1,0,1],[-1,0,1],[0,1,1],[0,-1,1],[1,1,1.414],[1,-1,1.414],[-1,1,1.414],[-1,-1,1.414]];
  while(heap.length){const [d,i]=pop();if(d>D[i])continue;const x=i%W,y=(i/W)|0;
    for(const [dx,dy,c] of N){const X=x+dx,Y=y+dy;if(X<0||Y<0||X>=W||Y>=H)continue;const j=Y*W+X;if(!mask[j])continue;const nd=d+c;if(nd<D[j]){D[j]=nd;push(nd,j);}}}
  return D;}
function build(img,bones,o={}){const G=o.grid||12,iw=img.naturalWidth||img.width,ih=img.naturalHeight||img.height,cv=document.createElement('canvas');cv.width=iw;cv.height=ih;
  const cx=cv.getContext('2d');cx.drawImage(img,0,0);const px=cx.getImageData(0,0,iw,ih).data,W=Math.ceil(iw/G),H=Math.ceil(ih/G);
  // 1) เซลล์ที่มีสี (+ขยาย 1 เซลล์กันขอบแหว่ง)
  const paint=new Uint8Array(W*H);for(let y=0;y<H;y++)for(let x=0;x<W;x++){let a=0;for(let yy=y*G;yy<Math.min(ih,(y+1)*G)&&!a;yy+=2)for(let xx=x*G;xx<Math.min(iw,(x+1)*G);xx+=2)if(px[(yy*iw+xx)*4+3]>30){a=1;break;}paint[y*W+x]=a;}
  const mask=new Uint8Array(W*H);for(let y=0;y<H;y++)for(let x=0;x<W;x++){let a=0;for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const X=x+dx,Y=y+dy;if(X>=0&&Y>=0&&X<W&&Y<H&&paint[Y*W+X])a=1;}mask[y*W+x]=a;}
  // 2) ระยะเดินจากกระดูกแต่ละท่อน (ทุกเซลล์ที่เส้นกระดูกผ่าน = จุดเริ่ม)
  const cellOf=(x,y)=>Math.min(H-1,Math.max(0,(y/G)|0))*W+Math.min(W-1,Math.max(0,(x/G)|0));
  const dist=bones.map(b=>{const s=new Set(),L=Math.hypot(b.t[0]-b.h[0],b.t[1]-b.h[1]);for(let k=0;k<=Math.ceil(L/(G/2));k++){const u=k/Math.max(1,Math.ceil(L/(G/2))),c=cellOf(b.h[0]+(b.t[0]-b.h[0])*u,b.h[1]+(b.t[1]-b.h[1])*u);if(mask[c])s.add(c);}
    return geodesic(mask,W,H,[...s]);});
  // 3) จุดยอดที่มุมเซลล์ + สามเหลี่ยม · น้ำหนัก = 3 กระดูกที่ "เดินถึง" ใกล้สุด
  const vid=new Int32Array((W+1)*(H+1)).fill(-1),verts=[],tris=[];
  const vert=(X,Y)=>{const k=Y*(W+1)+X;if(vid[k]>=0)return vid[k];let best=null;
    for(const [dx,dy] of [[0,0],[-1,0],[0,-1],[-1,-1]]){const cx=X+dx,cy=Y+dy;if(cx>=0&&cy>=0&&cx<W&&cy<H&&mask[cy*W+cx]){best=cy*W+cx;break;}}
    const ds=dist.map((D,i)=>[i,D[best]]).sort((a,b)=>a[1]-b[1]).slice(0,3);let ws=ds.map(([i,d])=>[i,1/Math.pow(d+.6,3)]);const sm=ws.reduce((a,b)=>a+b[1],0);ws=ws.map(([i,w])=>[i,w/sm]).filter(w=>w[1]>.02);
    const sm2=ws.reduce((a,b)=>a+b[1],0);ws.forEach(w=>w[1]/=sm2);
    verts.push({x:X*G,y:Y*G,w:ws});return vid[k]=verts.length-1;};
  for(let y=0;y<H;y++)for(let x=0;x<W;x++){if(!mask[y*W+x])continue;const a=vert(x,y),b=vert(x+1,y),c=vert(x+1,y+1),d=vert(x,y+1);tris.push([a,b,c],[a,c,d]);}
  const idx={};bones.forEach((b,i)=>idx[b.n]=i);
  return {img,iw,ih,G,verts,tris,bones:bones.map(b=>({...b,pi:b.p?idx[b.p]:-1}))};}
// กระดูก = หมุนรอบหัว + เลื่อน + ย่อขยาย · ลูกขี่พ่อ → เมทริกซ์ [a,b,c,d,e,f]
const mul=(A,B)=>[A[0]*B[0]+A[2]*B[1],A[1]*B[0]+A[3]*B[1],A[0]*B[2]+A[2]*B[3],A[1]*B[2]+A[3]*B[3],A[0]*B[4]+A[2]*B[5]+A[4],A[1]*B[4]+A[3]*B[5]+A[5]];
function mats(rig,pose){const M=[];for(const b of rig.bones){const q=pose[b.n]||{},r=(q.r||0)*Math.PI/180,s=q.s??1,sy=q.sy??s,c=Math.cos(r),n=Math.sin(r),[hx,hy]=b.h;
    // T(h+move) · R · S · T(-h)
    const L=[c*s,n*s,-n*sy,c*sy,0,0];L[4]=hx+(q.x||0)-(L[0]*hx+L[2]*hy);L[5]=hy+(q.y||0)-(L[1]*hx+L[3]*hy);
    M.push(b.pi>=0?mul(M[b.pi],L):L);}return M;}
function deform(rig,pose){const M=mats(rig,pose);return rig.verts.map(v=>{let x=0,y=0;for(const [i,w] of v.w){const m=M[i];x+=w*(m[0]*v.x+m[2]*v.y+m[4]);y+=w*(m[1]*v.x+m[3]*v.y+m[5]);}return [x,y];});}
// วาดทีละสามเหลี่ยม: affine จาก (u,v) ในภาพ → จุดที่บิดแล้ว · ขยายขอบสามเหลี่ยมนิดกันรอยต่อ
function draw(c,rig,pose,x,y,o={}){const P=deform(rig,pose),sc=o.scale||1,V=rig.verts;
  c.save();c.translate(x,y);c.scale(sc*(o.flip?-1:1),sc);if(o.anchor)c.translate(-o.anchor[0],-o.anchor[1]);
  for(const [a,b,d] of rig.tris){const [x0,y0]=P[a],[x1,y1]=P[b],[x2,y2]=P[d],u0=V[a].x,v0=V[a].y,u1=V[b].x,v1=V[b].y,u2=V[d].x,v2=V[d].y;
    const den=(u1-u0)*(v2-v0)-(u2-u0)*(v1-v0);if(!den)continue;
    const A=((x1-x0)*(v2-v0)-(x2-x0)*(v1-v0))/den,B=((y1-y0)*(v2-v0)-(y2-y0)*(v1-v0))/den,C=((x2-x0)*(u1-u0)-(x1-x0)*(u2-u0))/den,D=((y2-y0)*(u1-u0)-(y1-y0)*(u2-u0))/den;
    const cxm=(x0+x1+x2)/3,cym=(y0+y1+y2)/3,g=k=>[k[0]+(k[0]-cxm)*.04+(k[0]>cxm?.4:-.4),k[1]+(k[1]-cym)*.04+(k[1]>cym?.4:-.4)];
    const q0=g([x0,y0]),q1=g([x1,y1]),q2=g([x2,y2]);
    c.save();c.beginPath();c.moveTo(q0[0],q0[1]);c.lineTo(q1[0],q1[1]);c.lineTo(q2[0],q2[1]);c.closePath();c.clip();
    c.transform(A,B,C,D,x0-A*u0-C*v0,y0-B*u0-D*v0);c.drawImage(rig.img,0,0);c.restore();}
  if(o.debug){c.lineWidth=.6/sc;c.strokeStyle='rgba(120,255,200,.35)';c.beginPath();for(const [a,b,d] of rig.tris){c.moveTo(...P[a]);c.lineTo(...P[b]);c.lineTo(...P[d]);c.closePath();}c.stroke();
    const M=mats(rig,pose);c.lineWidth=3/sc;for(const b of rig.bones){const m=M[b.bi??rig.bones.indexOf(b)],h=[m[0]*b.h[0]+m[2]*b.h[1]+m[4],m[1]*b.h[0]+m[3]*b.h[1]+m[5]],t=[m[0]*b.t[0]+m[2]*b.t[1]+m[4],m[1]*b.t[0]+m[3]*b.t[1]+m[5]];
      c.strokeStyle='#ffd166';c.beginPath();c.moveTo(...h);c.lineTo(...t);c.stroke();c.fillStyle='#ff5a6a';c.beginPath();c.arc(h[0],h[1],4/sc,0,7);c.fill();}}
  c.restore();}
// น้ำหนักของกระดูกหนึ่งบนทุกจุด (ไว้ระบายสีดูว่าน้ำหนักไปตกตรงไหน)
function weightOf(rig,name){const i=rig.bones.findIndex(b=>b.n===name);return rig.verts.map(v=>(v.w.find(w=>w[0]===i)||[0,0])[1]);}
window.AUTORIG={build,draw,deform,weightOf};
})();
