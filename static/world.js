/* Single-source county atlas renderer and rewarding campaign challenges. */
(() => {
  'use strict';
  const canvas=document.querySelector('#map');
  if(!canvas)return;
  const ctx=canvas.getContext('2d');
  const outline=[[88,75],[127,60],[154,52],[181,58],[198,43],[225,50],[250,48],[273,59],[302,55],[322,70],[350,69],[360,83],[376,91],[369,110],[381,123],[365,137],[374,153],[357,167],[354,184],[337,191],[329,208],[308,214],[292,228],[269,226],[251,242],[230,238],[218,249],[197,237],[175,240],[157,224],[137,218],[125,201],[105,194],[101,178],[81,170],[79,153],[65,143],[75,125],[64,108],[79,94]];
  const centres=[[226,139],[237,151],[139,83],[177,98],[205,139],[164,157],[100,108],[107,162],[137,191],[183,181],[197,216],[233,201],[268,202],[308,183],[269,157],[282,123],[249,101],[310,104],[328,151],[354,122]];
  const labels=['Budapest','Pest','Győr-M-S.','Komárom-E.','Fejér','Veszprém','Vas','Zala','Somogy','Tolna','Baranya','Bács-K.','Csongrád-C.','Békés','Jász-N-Sz.','Heves','Nógrád','Borsod-A-Z.','Hajdú-B.','Szabolcs-Sz-B.'];
  const types=['U','U','M','M','M','M','R','R','R','R','M','R','M','R','R','M','R','R','M','R'];
  const contains=(x,y)=>{let inside=false;for(let i=0,j=outline.length-1;i<outline.length;j=i++){const [xi,yi]=outline[i],[xj,yj]=outline[j];if((yi>y)!==(yj>y)&&x<(xj-xi)*(y-yi)/(yj-yi)+xi)inside=!inside;}return inside;};
  function cellFor(index){let poly=[[45,30],[395,30],[395,265],[45,265]];const [cx,cy]=centres[index];for(let j=0;j<centres.length;j++){if(j===index)continue;const [ox,oy]=centres[j],a=2*(ox-cx),b=2*(oy-cy),c=ox*ox+oy*oy-cx*cx-cy*cy,out=[];for(let k=0;k<poly.length;k++){const p=poly[k],q=poly[(k+1)%poly.length],dp=a*p[0]+b*p[1]-c,dq=a*q[0]+b*q[1]-c;if(dp<=0)out.push(p);if((dp<0&&dq>0)||(dp>0&&dq<0)){const t=dp/(dp-dq);out.push([p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t]);}}poly=out;if(!poly.length)break;}return poly;}
  const cells=centres.map((_,i)=>cellFor(i));
  function draw(){
    if(!M||!S)return;
    const w=canvas.width,h=canvas.height;ctx.clearRect(0,0,w,h);
    const bg=ctx.createLinearGradient(0,0,w,h);bg.addColorStop(0,'#1c5073');bg.addColorStop(1,'#102945');ctx.fillStyle=bg;ctx.fillRect(0,0,w,h);
    ctx.strokeStyle='#c1e0e01a';ctx.lineWidth=1;for(let x=20;x<w;x+=28){ctx.beginPath();ctx.moveTo(x,18);ctx.lineTo(x,h-16);ctx.stroke();}for(let y=22;y<h;y+=28){ctx.beginPath();ctx.moveTo(15,y);ctx.lineTo(w-15,y);ctx.stroke();}
    ctx.save();ctx.shadowColor='#061321';ctx.shadowBlur=14;ctx.shadowOffsetY=7;ctx.beginPath();outline.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();ctx.fillStyle='#b9a875';ctx.fill();ctx.restore();
    ctx.save();ctx.beginPath();outline.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();ctx.clip();
    centres.forEach(([cx,cy],i)=>{const poly=cells[i];if(!poly.length)return;ctx.beginPath();poly.forEach(([x,y],j)=>j?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();const winner=S.wins?.[i],fallback=types[i]==='U'?'#47759a':types[i]==='R'?'#728453':'#9a8958';ctx.fillStyle=winner?(M.parties[winner]?.c||'#65738b'):fallback;ctx.fill();ctx.strokeStyle=i===selected?'#ffe279':'#e3d8b8';ctx.lineWidth=i===selected?3:1.6;ctx.stroke();ctx.fillStyle='#fff2';for(let yy=cy-12;yy<cy+12;yy+=7)for(let xx=cx-17;xx<cx+17;xx+=8)ctx.fillRect(xx,yy,2,2);});
    ctx.restore();ctx.fillStyle='#4ab5c5';ctx.beginPath();ctx.ellipse(145,188,23,5,-.2,0,Math.PI*2);ctx.fill();ctx.font='7px monospace';ctx.textAlign='center';ctx.fillStyle='#d9eef0';ctx.fillText('BALATON',145,201);
    centres.forEach(([x,y],i)=>{ctx.textAlign='center';ctx.textBaseline='middle';ctx.font=i===0?'bold 8px monospace':'7px monospace';ctx.lineWidth=3;ctx.strokeStyle='#14223a';ctx.strokeText(labels[i],x,y,46);ctx.fillStyle='#fff4d7';ctx.fillText(labels[i],x,y,46);if(i===0){ctx.fillStyle='#ffe279';ctx.fillRect(x-2,y-8,4,4);}});
    ctx.textAlign='left';ctx.textBaseline='alphabetic';ctx.font='bold 10px monospace';ctx.fillStyle='#fff2d6';ctx.fillText('HUNGARY · COUNTY CAMPAIGN MAP',14,286);ctx.font='8px monospace';ctx.fillStyle='#c3d6e5';ctx.textAlign='right';ctx.fillText('N ↑',405,28);
  }
  // game.js redraws its legacy canvas after state actions; repaint this one atlas on the next frame.
  window.drawMap=draw;
  canvas.addEventListener('click',event=>{event.stopImmediatePropagation();const r=canvas.getBoundingClientRect(),x=(event.clientX-r.left)*canvas.width/r.width,y=(event.clientY-r.top)*canvas.height/r.height;if(!contains(x,y))return;let best=0,dist=Infinity;centres.forEach(([cx,cy],i)=>{const d=(x-cx)**2+(y-cy)**2;if(d<dist){dist=d;best=i;}});selected=best;render();},true);
  canvas.setAttribute('aria-label','Clickable stylized map of Hungary and its counties. The county subdivisions are illustrative, not official boundary geometry.');
  const missions=[
    {id:'field',title:'Build a local network',text:'Recruit candidates in three counties.',progress:()=>Object.keys(S.county_mps||{}).length,goal:3,reward:8},
    {id:'poll',title:'Become a national contender',text:'Reach at least 20% in the current poll.',progress:()=>Number(S.poll?.[S.party]||0),goal:20,reward:10,percent:true},
    {id:'policy',title:'Turn votes into policy',text:'Enact your first government policy.',progress:()=>S.policy_history?.length||0,goal:1,reward:12},
    {id:'government',title:'Win the government',text:'Lead government after an election.',progress:()=>S.hist?.some(x=>x.gov===S.party)?1:0,goal:1,reward:20}
  ];
  let lastMessage='';
  function updateMissions(){
    if(!S||!M)return;
    S.challenge_rewards ||= [];
    let completed=null;
    for(const m of missions){const n=Number(m.progress());if(n>=m.goal&&!S.challenge_rewards.includes(m.id)){S.challenge_rewards.push(m.id);S.money+=m.reward;S.flash=`Challenge complete: ${m.title} — reward +${m.reward} M Ft.`;S.log||=[];S.log.push(S.flash);completed=m;}}
    if(completed&&typeof render==='function')render();
    const panel=document.querySelector('#panel');if(!panel)return;
    let board=panel.querySelector('.mission-board');if(!board){board=document.createElement('section');board.className='mission-board';panel.appendChild(board);}
    const html=`<h3>Campaign challenges · ${S.challenge_rewards.length}/${missions.length}</h3><p class="mission-intro">Finish objectives to earn campaign funds.</p>${missions.map(m=>{const n=Number(m.progress()),done=S.challenge_rewards.includes(m.id),pct=Math.max(0,Math.min(100,n/m.goal*100));return `<article class="mission-card ${done?'complete':''}"><div class="mission-heading"><b>${done?'✦':'◇'} ${m.title}</b><span>${done?'REWARDED':`${m.percent?n.toFixed(1):n}/${m.goal} · +${m.reward} Ft`}</span></div><p>${m.text}</p><div class="mission-track"><i style="width:${pct}%"></i></div></article>`;}).join('')}`;
    if(board.dataset.content!==html){board.innerHTML=html;board.dataset.content=html;}
  }
  const panel=document.querySelector('#panel');if(panel)new MutationObserver(()=>{const board=panel.querySelector('.mission-board');if(!board)updateMissions();}).observe(panel,{childList:true});
  // One stable renderer wins after the UI's legacy draw; RAF avoids the visible old/new map blink.
  let dirty=true;const originalSet=window.setTimeout;function animate(){draw();requestAnimationFrame(animate);}requestAnimationFrame(animate);
  setInterval(updateMissions,500);
})();
