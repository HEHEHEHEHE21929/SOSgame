/* Geographic Hungary map layer and campaign achievement board. */
(() => {
  'use strict';
  const canvas = document.querySelector('#map');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const outline = [[88,75],[127,60],[154,52],[181,58],[198,43],[225,50],[250,48],[273,59],[302,55],[322,70],[350,69],[360,83],[376,91],[369,110],[381,123],[365,137],[374,153],[357,167],[354,184],[337,191],[329,208],[308,214],[292,228],[269,226],[251,242],[230,238],[218,249],[197,237],[175,240],[157,224],[137,218],[125,201],[105,194],[101,178],[81,170],[79,153],[65,143],[75,125],[64,108],[79,94]];
  // County centres ordered to match the engine's COUNTIES table.
  const centres = [[226,139],[237,151],[139,83],[177,98],[205,139],[164,157],[100,108],[107,162],[137,191],[183,181],[197,216],[233,201],[268,202],[308,183],[269,157],[282,123],[249,101],[310,104],[328,151],[354,122]];
  const names = ['Budapest','Pest','Győr-M-S.','Komárom-E.','Fejér','Veszprém','Vas','Zala','Somogy','Tolna','Baranya','Bács-K.','Csongrád-C.','Békés','Jász-N-Sz.','Heves','Nógrád','Borsod-A-Z.','Hajdú-B.','Szabolcs-Sz-B.'];
  const types = ['U','U','M','M','M','M','R','R','R','R','M','R','M','R','R','M','R','R','M','R'];
  const inside = (x,y) => {
    let hit=false;
    for(let i=0,j=outline.length-1;i<outline.length;j=i++){
      const [xi,yi]=outline[i],[xj,yj]=outline[j];
      if(((yi>y)!==(yj>y)) && x<(xj-xi)*(y-yi)/(yj-yi)+xi) hit=!hit;
    }
    return hit;
  };
  function voronoiCell(index){
    let poly=[[50,30],[395,30],[395,265],[50,265]];
    const [cx,cy]=centres[index];
    for(let j=0;j<centres.length;j++){
      if(j===index)continue;
      const [ox,oy]=centres[j], a=2*(ox-cx), b=2*(oy-cy), c=ox*ox+oy*oy-cx*cx-cy*cy;
      const out=[];
      for(let k=0;k<poly.length;k++){
        const p=poly[k],q=poly[(k+1)%poly.length], dp=a*p[0]+b*p[1]-c,dq=a*q[0]+b*q[1]-c;
        if(dp<=0)out.push(p);
        if((dp<0&&dq>0)||(dp>0&&dq<0)){const t=dp/(dp-dq);out.push([p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t]);}
      }
      poly=out;if(!poly.length)break;
    }
    return poly;
  }
  const cells=centres.map((_,i)=>voronoiCell(i));
  function draw(){
    if(!M||!S)return;
    const w=canvas.width,h=canvas.height;
    ctx.clearRect(0,0,w,h);
    const bg=ctx.createLinearGradient(0,0,w,h);bg.addColorStop(0,'#1c5073');bg.addColorStop(1,'#102945');ctx.fillStyle=bg;ctx.fillRect(0,0,w,h);
    // Quiet lake speckles and map grid establish a readable atlas background.
    ctx.strokeStyle='#c1e0e01a';ctx.lineWidth=1;
    for(let x=20;x<w;x+=28){ctx.beginPath();ctx.moveTo(x,18);ctx.lineTo(x,h-16);ctx.stroke();}
    for(let y=22;y<h;y+=28){ctx.beginPath();ctx.moveTo(15,y);ctx.lineTo(w-15,y);ctx.stroke();}
    ctx.save();ctx.shadowColor='#061321';ctx.shadowBlur=14;ctx.shadowOffsetY=7;
    ctx.beginPath();outline.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();ctx.fillStyle='#b9a875';ctx.fill();ctx.restore();
    ctx.save();ctx.beginPath();outline.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();ctx.clip();
    centres.forEach(([cx,cy],i)=>{
      const cell=cells[i];if(!cell.length)return;
      ctx.beginPath();cell.forEach(([x,y],j)=>j?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();
      const winner=S.wins?.[i];
      const terrain=types[i]==='U'?'#47759a':types[i]==='R'?'#728453':'#9a8958';
      ctx.fillStyle=winner?(M.parties[winner]?.c||'#65738b'):terrain;ctx.fill();
      ctx.strokeStyle='#e3d8b8';ctx.lineWidth=1.6;ctx.stroke();
      if(i===selected){ctx.strokeStyle='#ffe279';ctx.lineWidth=3;ctx.stroke();}
      // Low-contrast pixel dither, intentionally sparse so labels remain legible.
      ctx.fillStyle='#fff2';for(let yy=cy-12;yy<cy+12;yy+=7)for(let xx=cx-17;xx<cx+17;xx+=8)ctx.fillRect(xx,yy,2,2);
    });
    ctx.restore();
    // Lake Balaton, Budapest marker, orientation and county labels.
    ctx.save();ctx.fillStyle='#4ab5c5';ctx.beginPath();ctx.ellipse(145,188,23,5,-.2,0,Math.PI*2);ctx.fill();ctx.fillStyle='#d9eef0';ctx.font='7px monospace';ctx.textAlign='center';ctx.fillText('BALATON',145,201);ctx.restore();
    centres.forEach(([x,y],i)=>{
      ctx.textAlign='center';ctx.textBaseline='middle';ctx.font=i===0?'bold 8px monospace':'7px monospace';
      ctx.lineWidth=3;ctx.strokeStyle='#14223a';ctx.strokeText(names[i],x,y,46);ctx.fillStyle='#fff4d7';ctx.fillText(names[i],x,y,46);
      if(i===0){ctx.fillStyle='#ffe279';ctx.fillRect(x-2,y-8,4,4);}
    });
    ctx.textAlign='left';ctx.textBaseline='alphabetic';ctx.font='bold 10px monospace';ctx.fillStyle='#fff2d6';ctx.fillText('HUNGARY · COUNTY CAMPAIGN MAP',14,286);
    ctx.font='8px monospace';ctx.fillStyle='#c3d6e5';ctx.textAlign='right';ctx.fillText('N ↑',405,28);
  }
  // Replace the previous approximate map's click handler with geographic county selection.
  canvas.addEventListener('click',event=>{
    event.stopImmediatePropagation();
    const rect=canvas.getBoundingClientRect(),x=(event.clientX-rect.left)*canvas.width/rect.width,y=(event.clientY-rect.top)*canvas.height/rect.height;
    if(!inside(x,y))return;
    let best=0,distance=Infinity;
    centres.forEach(([cx,cy],i)=>{const d=(x-cx)**2+(y-cy)**2;if(d<distance){distance=d;best=i;}});
    selected=best;render();
  },true);
  canvas.setAttribute('aria-label','Geographic-style clickable Hungary county map; select a county region to manage its campaign.');
  window.setInterval(draw,250);

  const missions=[
    {id:'field',title:'Build a local network',text:'Recruit candidates in three counties.',progress:()=>Object.keys(S.county_mps||{}).length,goal:3,done:n=>n>=3},
    {id:'poll',title:'Become a national contender',text:'Reach at least 20% in the current poll.',progress:()=>Number(S.poll?.[S.party]||0),goal:20,done:n=>n>=20,percent:true},
    {id:'policy',title:'Turn votes into policy',text:'Enact your first government policy.',progress:()=>S.policy_history?.length||0,goal:1,done:n=>n>=1},
    {id:'government',title:'Win the government',text:'Lead government after an election.',progress:()=>S.hist?.some(item=>item.gov===S.party)?1:0,goal:1,done:n=>n>=1}
  ];
  function addMissions(){
    if(!S||!M)return;
    const panel=document.querySelector('#panel');if(!panel)return;
    let board=panel.querySelector('.mission-board');
    if(!board){board=document.createElement('section');board.className='mission-board';panel.appendChild(board);}
    const cards=missions.map(m=>{
      const raw=Number(m.progress());const value=m.percent?Math.min(raw,m.goal):Math.min(raw,m.goal);const percent=Math.max(0,Math.min(100,value/m.goal*100));
      return `<article class="mission-card ${m.done(raw)?'complete':''}"><div class="mission-heading"><b>${m.done(raw)?'✦':'◇'} ${m.title}</b><span>${m.done(raw)?'COMPLETE':`${m.percent?raw.toFixed(1):raw}/${m.goal}`}</span></div><p>${m.text}</p><div class="mission-track"><i style="width:${percent}%"></i></div></article>`;
    }).join('');
    board.innerHTML=`<h3>Campaign challenges</h3><p class="mission-intro">Optional goals add a reason to plan beyond the next button.</p>${cards}`;
  }
  const observer=new MutationObserver(()=>{if(!document.querySelector('.mission-board'))addMissions();});
  observer.observe(document.querySelector('#panel'),{childList:true,subtree:true});
  window.setInterval(addMissions,600);
})();
