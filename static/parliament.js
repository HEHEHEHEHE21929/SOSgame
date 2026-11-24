/* Interactive 199-seat assembly view with party key and coalition summary. */
(() => {
  'use strict';
  const SAVE_KEY='magyar-politika-save';
  const CHAMBER_KEY='magyar-politika-parliament';
  const root=document.createElement('div');root.id='parliament-modal';root.className='parliament-backdrop';root.hidden=true;
  root.setAttribute('role','dialog');root.setAttribute('aria-modal','true');root.setAttribute('aria-labelledby','parliament-title');
  root.innerHTML='<section class="parliament-dialog"><header class="parliament-header"><div><p class="eyebrow">NATIONAL ASSEMBLY</p><h2 id="parliament-title">Parliament</h2></div><button type="button" class="parliament-close" aria-label="Close parliament">✕</button></header><div class="parliament-content"></div></section>';
  document.body.append(root);
  const content=root.querySelector('.parliament-content');
  const close=()=>{root.hidden=true;};
  root.querySelector('.parliament-close').addEventListener('click',close);
  root.addEventListener('click',event=>{if(event.target===root)close();});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!root.hidden)close();});

  function safe(value){return String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
  function seatProjection(state,meta){
    const result=state.result;
    if(result?.seats&&Object.values(result.seats).reduce((a,b)=>a+Number(b||0),0)===199)return {seats:result.seats,year:result.year,projection:false,result};
    try{const saved=JSON.parse(localStorage.getItem(CHAMBER_KEY)||'null');if(saved?.seats&&Object.values(saved.seats).reduce((a,b)=>a+Number(b||0),0)===199)return {...saved,projection:false};}catch(_){}
    const shares=state.poll||{};
    const eligible=Object.entries(shares).filter(([party,value])=>party!=='CUSTOM'&&Number(value)>=5);
    if(!eligible.length)return {seats:{},projection:true,result:null};
    const total=eligible.reduce((sum,[,share])=>sum+Number(share),0)||1;
    const exact=eligible.map(([party,share])=>[party,199*Number(share)/total]);
    const allocation=Object.fromEntries(exact.map(([party,value])=>[party,Math.floor(value)]));
    let left=199-Object.values(allocation).reduce((sum,value)=>sum+value,0);
    exact.slice().sort((a,b)=>(b[1]-Math.floor(b[1]))-(a[1]-Math.floor(a[1]))).slice(0,left).forEach(([party])=>allocation[party]++);
    return {seats:allocation,projection:true,result:null};
  }
  function partyLabel(key,state,meta){return key===state.party?(state.pname||meta.parties[key]?.n||key):(meta.parties[key]?.n||key);}
  function chamberSvg(entries){
    // Eight curved rows total exactly 199 seat dots.
    const counts=[17,21,25,29,33,35,23,16];let index=0;
    const circles=[];
    counts.forEach((count,row)=>{
      const y=290-row*31,span=95+row*27;
      for(let col=0;col<count;col++){
        const x=320-span+(count===1?0:(2*span*col/(count-1)));
        const party=entries[index++]||'VACANT';
        circles.push(`<circle cx="${x.toFixed(1)}" cy="${y}" r="7.2" class="seat-dot" fill="${party==='VACANT'?'#52627b':'var(--party-color)'}" data-party="${safe(party)}"><title>${safe(party)}</title></circle>`);
      }
    });
    return `<svg class="chamber-svg" viewBox="0 0 640 330" role="img" aria-label="199 parliamentary seats shown as party-colored dots"><path class="chamber-floor" d="M80 306 Q320 12 560 306"/><path class="chamber-ring" d="M105 306 Q320 40 535 306"/>${circles.join('')}<text x="320" y="323" text-anchor="middle" class="chamber-label">SPEAKER</text></svg>`;
  }
  function render(){
    let state;try{state=JSON.parse(localStorage.getItem(SAVE_KEY)||'null');}catch(_){state=null;}
    if(!state)return;
    fetch('/api/meta').then(response=>response.json()).then(meta=>{
      const view=seatProjection(state,meta),seats=view.seats||{};
      const parties=Object.entries(seats).filter(([,n])=>Number(n)>0).sort((a,b)=>b[1]-a[1]);
      const entries=[];parties.forEach(([party,count])=>{for(let i=0;i<Number(count);i++)entries.push(party);});
      while(entries.length<199)entries.push('VACANT');
      entries.length=199;
      // Set an explicit CSS variable per dot; data stays text-escaped and colors come only from metadata.
      const svg=chamberSvg(entries).replace(/fill="var\(--party-color\)" data-party="([^"]+)"/g,(_match,party)=>`fill="${safe(meta.parties[party]?.c||'#65738b')}" data-party="${party}"`);
      const coalition=view.result?.coalition||state.coalition||null;
      const government=view.result?.gov||state.government||state.party;
      const govSeats=Number(seats[government]||0),coalitionSeats=coalition?govSeats+Number(seats[coalition]||0):govSeats;
      const governmentName=partyLabel(government,state,meta);
      const coalitionLine=coalition
        ? `<div class="coalition-status formed"><b>Coalition government:</b> ${safe(governmentName)} + ${safe(partyLabel(coalition,state,meta))}<span>${coalitionSeats} / 199 seats · ${coalitionSeats>=100?'majority reached':'short of a majority'}</span></div>`
        : `<div class="coalition-status"><b>${govSeats>=100?'Single-party majority':'No majority coalition formed'}</b><span>${safe(governmentName)}: ${govSeats} / 199 seats · 100 seats needed to govern</span></div>`;
      const key=parties.map(([party,count])=>`<div class="party-key-item"><i style="--key-color:${safe(meta.parties[party]?.c||'#65738b')}"></i><span>${safe(partyLabel(party,state,meta))}</span><b>${count}</b></div>`).join('')||'<p>No elected seats yet.</p>';
      content.innerHTML=`<div class="chamber-meta"><span>${view.projection?'POLL-BASED PROJECTION · NOT AN ELECTION RESULT':`SIMULATED ELECTION · ${safe(view.year||'Latest')}`}</span><b>199 seats</b></div>${svg}<div class="parliament-summary"><section><h3>Party key · seats</h3><div class="party-key">${key}</div></section><section><h3>Government &amp; coalitions</h3>${coalitionLine}<p class="coalition-note">A coalition combines parties that agree to govern together. A majority requires at least 100 of 199 seats. This is a simplified classroom simulation, not an official seat projection.</p></section></div><p class="seat-lesson">Each dot is one simulated MP seat. County constituencies and proportional list seats combine to make the 199-seat chamber.</p>`;
      if(!root.hidden)requestAnimationFrame(()=>root.querySelectorAll('.seat-dot').forEach(dot=>dot.setAttribute('aria-label',`${meta.parties[dot.dataset.party]?.n||dot.dataset.party} seat`)));
    }).catch(()=>{content.innerHTML='<p>Parliament data could not be loaded. Please try again.</p>';});
  }
  function addButton(){
    const top=document.querySelector('#top');if(!top)return;
    let button=top.querySelector('#open-parliament');
    if(!button){button=document.createElement('button');button.type='button';button.id='open-parliament';button.textContent='Parliament · 199 seats';button.setAttribute('aria-haspopup','dialog');top.append(button);button.addEventListener('click',()=>{render();root.hidden=false;});}
  }
  const observer=new MutationObserver(addButton);observer.observe(document.querySelector('#top'),{childList:true});addButton();
  window.addEventListener('storage',event=>{if(event.key===SAVE_KEY&&!root.hidden)render();});
})();
