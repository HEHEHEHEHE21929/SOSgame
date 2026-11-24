/* Make canvas county selection forgiving at borders and keyboard accessible. */
(() => {
  'use strict';
  const canvas=document.querySelector('#map');
  if(!canvas)return;
  canvas.setAttribute('role','application');
  canvas.setAttribute('aria-label','Interactive map of Hungary. Click a county, or focus the map and use arrow keys to move between counties.');
  canvas.title='Click a county. Near-border clicks snap to the closest county; use arrow keys to move.';
  let shapes=[];
  let keyboardIndex=0;
  const sourceUrl=document.querySelector('script[src*="/static/game.js"]')?.src;

  function inside(point,poly){let hit=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const [xi,yi]=poly[i],[xj,yj]=poly[j];if(((yi>point.y)!==(yj>point.y))&&(point.x<(xj-xi)*(point.y-yi)/(yj-yi)+xi))hit=!hit;}return hit;}
  function closestOnSegment(p,a,b){const dx=b[0]-a[0],dy=b[1]-a[1],length=dx*dx+dy*dy;const t=length?Math.max(0,Math.min(1,((p.x-a[0])*dx+(p.y-a[1])*dy)/length)):0;return{x:a[0]+t*dx,y:a[1]+t*dy};}
  function snap(point){
    let best=null;
    for(let i=0;i<shapes.length;i++){
      const poly=shapes[i];
      if(inside(point,poly))return null;
      for(let j=0;j<poly.length;j++){
        const edge=closestOnSegment(point,poly[j],poly[(j+1)%poly.length]);
        const distance=Math.hypot(point.x-edge.x,point.y-edge.y);
        if(!best||distance<best.distance)best={distance,edge,poly,index:i};
      }
    }
    if(!best||best.distance>10)return null;
    const center=best.poly.reduce((sum,p)=>({x:sum.x+p[0]/best.poly.length,y:sum.y+p[1]/best.poly.length}),{x:0,y:0});
    const dx=center.x-best.edge.x,dy=center.y-best.edge.y,length=Math.hypot(dx,dy)||1;
    return{x:best.edge.x+dx/length*1.5,y:best.edge.y+dy/length*1.5,index:best.index};
  }
  function pointFromEvent(event){const r=canvas.getBoundingClientRect();return{x:(event.clientX-r.left)*canvas.width/r.width,y:(event.clientY-r.top)*canvas.height/r.height};}
  function setEventPoint(event,p){const r=canvas.getBoundingClientRect();try{Object.defineProperty(event,'clientX',{configurable:true,value:r.left+p.x/canvas.width*r.width});Object.defineProperty(event,'clientY',{configurable:true,value:r.top+p.y/canvas.height*r.height});}catch(_){}}
  canvas.addEventListener('click',event=>{
    const p=pointFromEvent(event),adjusted=snap(p);
    if(adjusted)setEventPoint(event,adjusted);
    window.dispatchEvent(new CustomEvent('sos:county-selected',{detail:{point:adjusted||p}}));
  },true);
  function clickAt(index){const poly=shapes[index];if(!poly)return;const center=poly.reduce((sum,p)=>({x:sum.x+p[0]/poly.length,y:sum.y+p[1]/poly.length}),{x:0,y:0});const r=canvas.getBoundingClientRect();canvas.dispatchEvent(new MouseEvent('click',{bubbles:true,clientX:r.left+center.x/canvas.width*r.width,clientY:r.top+center.y/canvas.height*r.height}));}
  canvas.addEventListener('keydown',event=>{
    if(!shapes.length)return;
    if(event.key==='Enter'||event.key===' '){event.preventDefault();clickAt(keyboardIndex);return;}
    const moves={ArrowRight:1,ArrowDown:1,ArrowLeft:-1,ArrowUp:-1};
    if(moves[event.key]){event.preventDefault();keyboardIndex=(keyboardIndex+moves[event.key]+shapes.length)%shapes.length;canvas.setAttribute('aria-label',`Interactive map of Hungary. County ${keyboardIndex+1} of ${shapes.length} focused; press Enter to select.`);canvas.focus();}
  });
  if(sourceUrl)fetch(sourceUrl).then(r=>r.text()).then(source=>{
    const match=source.match(/const\s+shapes\s*=\s*(\[[\s\S]*?\])\s*;/);
    if(match)shapes=JSON.parse(match[1]);
    if(shapes.length){const note=document.createElement('p');note.className='map-interaction-hint';note.textContent='Tip: county borders are forgiving—click near an edge, or focus the map and use arrow keys + Enter.';canvas.insertAdjacentElement('afterend',note);}
  }).catch(error=>console.warn('County map enhancements could not load:',error));
})();
