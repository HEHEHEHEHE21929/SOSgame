/* Playable Civ-style interface and interactive schematic county map. */
'use strict';
const $ = (selector) => document.querySelector(selector);
const api = (op, data) => fetch(`/api/${op}`, {
  method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
}).then(async response => {
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || 'Game request failed');
  return payload;
});
let M = null, S = null, speed = 0, resumeSpeed = 1, lang = 'en', tab = 'Party';
let selected = -1, muted = false, modalOpen = false, seenElectionYear = null, busy = false;
const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const tilePositions = [[2,2],[3,2],[0,1],[1,1],[2,1],[2,2],[0,2],[1,3],[2,3],[3,4],[4,4],[4,3],[5,3],[5,4],[4,2],[3,0],[2,0],[4,0],[5,1],[5,0]];
const $canvas = $('#map');
const ctx = $canvas.getContext('2d');
let audio = null;

function sound(note=440, duration=.08) {
  if (muted) return;
  try {
    audio ||= new (window.AudioContext || window.webkitAudioContext)();
    if (audio.state === 'suspended') audio.resume();
    const osc = audio.createOscillator(), gain = audio.createGain();
    osc.type = 'triangle'; osc.frequency.value = note;
    gain.gain.setValueAtTime(.035, audio.currentTime);
    gain.gain.exponentialRampToValueAtTime(.001, audio.currentTime + duration);
    osc.connect(gain); gain.connect(audio.destination); osc.start(); osc.stop(audio.currentTime + duration);
  } catch (_) { /* Audio is optional. */ }
}
function partyName(key) { return key === S?.party ? S.pname : (M.parties[key]?.n || key); }
function partyColor(key) { return M.parties[key]?.c || '#777777'; }
function calendar() { const n = S.m; return {year: 1991 + Math.floor(n / 12), month: n % 12}; }
function electionCountdown() { let next = 39; while (next <= S.m) next += 36; return next - S.m; }
function setSpeed(value) {
  speed = Number(value); if (speed) resumeSpeed = speed;
  renderTop();
}

function drawMap() {
  if (!M || !$canvas) return;
  const w = $canvas.width, h = $canvas.height;
  ctx.fillStyle = '#000080'; ctx.fillRect(0, 0, w, h);
  // Water and a tiny animated Balaton shimmer.
  ctx.fillStyle = '#123b75'; ctx.fillRect(112, 204, 100, 8);
  ctx.fillStyle = '#00aaaa'; ctx.fillRect(119 + (Math.floor(Date.now()/450)%8), 206, 35, 2);
  const tileW = 62, tileH = 42, gapX = 4, gapY = 4, left = 18, top = 14;
  M.counties.forEach((county, i) => {
    const [gx, gy] = tilePositions[i] || [i % 6, Math.floor(i / 6)];
    const x = left + gx * (tileW + gapX), y = top + gy * (tileH + gapY);
    const winner = S?.wins?.[i];
    ctx.fillStyle = winner ? partyColor(winner) : (county[1] === 'U' ? '#5555aa' : county[1] === 'R' ? '#557744' : '#887744');
    ctx.fillRect(x, y, tileW, tileH);
    // EGA-like dither texture and crisp county edges.
    ctx.fillStyle = '#ffffff22';
    for (let py = 3; py < tileH - 2; py += 6) for (let px = ((py/6|0)%2)*3 + 3; px < tileW - 2; px += 7) ctx.fillRect(x+px, y+py, 2, 2);
    ctx.strokeStyle = i === selected ? '#ffff55' : '#eee'; ctx.lineWidth = i === selected ? 3 : 1;
    ctx.strokeRect(x+.5, y+.5, tileW-1, tileH-1);
    ctx.fillStyle = '#fff'; ctx.font = '8px monospace'; ctx.textAlign = 'center';
    const label = county[0].length > 11 ? county[0].slice(0, 10) : county[0];
    ctx.fillText(label, x + tileW/2, y + 23, tileW - 3);
  });
}
$canvas.addEventListener('click', event => {
  if (!M) return;
  const rect = $canvas.getBoundingClientRect();
  const px = (event.clientX - rect.left) * $canvas.width / rect.width;
  const py = (event.clientY - rect.top) * $canvas.height / rect.height;
  const tileW=62,tileH=42,gapX=4,gapY=4,left=18,top=14;
  selected = M.counties.findIndex((county,i) => {
    const [gx,gy]=tilePositions[i]||[i%6,Math.floor(i/6)];
    const x=left+gx*(tileW+gapX),y=top+gy*(tileH+gapY);
    return px>=x&&px<=x+tileW&&py>=y&&py<=y+tileH;
  });
  render(); sound(550);
});

function renderTop() {
  if (!S) return;
  const date = calendar();
  const locale = lang === 'hu' ? 'hu-HU' : 'en-US';
  const dateLabel = new Intl.DateTimeFormat(locale,{month:'long',year:'numeric'}).format(new Date(date.year,date.month,1));
  $('#top').innerHTML = `<span class="readout"><b>${dateLabel}</b></span><span class="readout">Funds: ${Math.floor(S.money)} M Ft</span><span class="readout">Capital: ${S.cap.toFixed(1)}</span><span class="readout">Election in ${electionCountdown()} months</span><span class="spacer"></span>${[[0,'PAUSE'],[1,'1x'],[2,'2x'],[4,'4x']].map(([n,label])=>`<button data-speed="${n}" class="${speed===n?'active':''}">${label}</button>`).join('')}<span class="tabs">${['Game','Party','Campaign','Policy','Advisors','World'].map(name=>`<button data-tab="${name}" class="${tab===name?'active':''}">${name}</button>`).join('')}</span><button id="language">${lang==='en'?'English / Magyar':'Magyar / English'}</button><button id="mute">Sound: ${muted?'off':'on'}</button>`;
  document.querySelectorAll('[data-speed]').forEach(button=>button.onclick=()=>setSpeed(button.dataset.speed));
  document.querySelectorAll('[data-tab]').forEach(button=>button.onclick=()=>{tab=button.dataset.tab;render();});
  $('#language').onclick=()=>{lang=lang==='en'?'hu':'en';render();};
  $('#mute').onclick=()=>{muted=!muted;renderTop();};
}
function partyRows() {
  return Object.entries(S.poll).sort((a,b)=>b[1]-a[1]).map(([party,share])=>`<div class="row"><span class="swatch" style="background:${partyColor(party)}"></span><b>${esc(partyName(party))}</b><span class="bar"><i style="width:${Math.min(100,share)}%;background:${partyColor(party)}"></i></span><span>${share.toFixed(1)}%</span></div>`).join('');
}
function mentorPanel() {
  const mentor = M.mentors[S.mentor];
  return `<h3>Mentor</h3><div class="advisor"><canvas class="portrait" width="56" height="56"></canvas><div><b>${esc(mentor.n)}</b><br><span class="small">${esc(mentor.facts.join(' · '))}</span></div></div><select id="mentor-select">${Object.entries(M.mentors).map(([id,item])=>`<option value="${esc(id)}" ${id===S.mentor?'selected':''}>${esc(item.n)}</option>`).join('')}</select><p class="small">${esc(mentor.learn)}</p>`;
}
function renderPanel() {
  let html = '';
  if (tab==='Party') html=`<h3>${esc(S.pname)} · ${esc(S.leader)}</h3><p>Difficulty: <b>${esc(M.difficulties[S.difficulty]?.name || 'Normal')}</b> · Support &amp; polls (simplified)</p>${partyRows()}<p><b>${S.seats}</b> seats · ${S.inpower?'Leading the government':'Opposition'} · 5% threshold</p>${mentorPanel()}`;
  if (tab==='Campaign') html=`<h3>Campaign office</h3><p>${S.reg?'Candidates registered.':'Register candidates before the next election for full ballot access.'}</p><p>Choose an action. County selection applies campaign effort to that county.</p>${Object.entries(M.campaign).map(([id,[label,cost,gain]])=>`<button data-campaign="${esc(id)}">${esc(label)} · ${cost} M Ft</button> `).join('')}<p class="small">Repeated campaign actions have diminishing returns. County focus and party support are simplified game figures.</p>`;
  if (tab==='Policy') html=`<h3>Government policy</h3>${S.inpower?M.policies.map(p=>`<div><button data-policy="${esc(p.id)}">${esc(p.label)} · ${p.cap} capital / ${p.cost} M Ft</button><p class="small">Helps: ${esc(p.win)}. Trade-off: ${esc(p.lose)}.</p></div>`).join(''):'<p>Your party must lead the government to enact policy.</p>'}`;
  if (tab==='Advisors') html=`<h3>Advisors</h3><p>Mentor bonuses are small and situational; you can switch at any time.</p>${mentorPanel()}<button id="learn">Learn more</button><p class="small">Supporters and critics are summarized neutrally in the mentor card.</p>`;
  if (tab==='World') html=`<h3>Election history</h3>${S.hist.length?S.hist.map(item=>`<p>${item.year}: ${item.share}% · ${item.seats} seats · government: ${esc(partyName(item.gov))}</p>`).join(''):'<p>First election is April 1994.</p>'}<p class="small">199 seats total: 106 constituency and 93 list seats. Threshold: 5%. All game results are simplified.</p>`;
  if (tab==='Game') html=`<h3>Game options</h3><p>Time starts in January 1991 and ends in December 2030.</p><div class="file-controls"><button id="copy-save">Copy save code</button><button id="load-save">Paste save code</button><textarea id="save-box" rows="3" placeholder="Save code"></textarea></div><p><button id="new-game">New game</button></p><p class="small">The save is held in this browser. Copy it to keep a backup.</p>`;
  $('#panel').innerHTML=html;
  $('#mentor-select')?.addEventListener('change',()=>act('mentor',{mentor:$('#mentor-select').value}));
  $('#learn')?.addEventListener('click',()=>alert(M.mentors[S.mentor].learn));
  document.querySelectorAll('[data-campaign]').forEach(button=>button.onclick=()=>act('campaign',{action:button.dataset.campaign}));
  document.querySelectorAll('[data-policy]').forEach(button=>button.onclick=()=>act('policy',{id:button.dataset.policy}));
  $('#copy-save')?.addEventListener('click',copySave);
  $('#load-save')?.addEventListener('click',loadSave);
  $('#new-game')?.addEventListener('click',startMenu);
  drawPortraits();
}
function drawPortraits(){document.querySelectorAll('.portrait').forEach(canvas=>{const c=canvas.getContext('2d');c.fillStyle='#55ffff';c.fillRect(0,0,56,56);c.fillStyle='#ffaa77';c.fillRect(18,9,20,22);c.fillStyle='#222';c.fillRect(18,6,20,7);c.fillRect(22,20,3,3);c.fillRect(32,20,3,3);c.fillStyle='#333399';c.fillRect(11,34,34,18);});}
function render() {
  if (!S) return;
  renderTop(); renderPanel();
  if (selected>=0) {
    const [name,type,seats]=M.counties[selected];
    const winner=S.wins?.[selected];
    const support=S.poll[S.party] ?? 0;
    $('#info').innerHTML=`<b>${esc(name)}</b> · ${{U:'city',R:'rural',M:'mixed'}[type]} county · ${seats} constituency seats<br>Player polling: ${support.toFixed(1)}% · ${winner?`Last simulated winner: ${esc(partyName(winner))}`:'No election held yet.'}`;
  }
  $('#log').innerHTML=`<b>${esc(S.flash||'Campaign journal')}</b><br>${S.log.slice(-4).map(esc).join('<br>')}`;
  drawMap(); localStorage.setItem('magyar-politika-save',JSON.stringify(S));
}
async function act(op,data) {
  try { S=await api(op,{...data,state:S}); sound(720); render(); checkOverlays(); }
  catch(error) { alert(error.message); }
}
function openModal(html) { if(speed){resumeSpeed=speed;speed=0;} modalOpen=true; $('#modal').innerHTML=`<section class="dialog">${html}</section>`; $('#modal').style.display='flex'; renderTop(); }
function closeModal() { $('#modal').style.display='none'; modalOpen=false; if(S){render(); if(resumeSpeed) setSpeed(resumeSpeed); checkOverlays();} }
function startMenu() {
  if (!M) return;
  const startingParties=Object.entries(M.parties).filter(([,p])=>p.f<=1991);
  openModal(`<h2>MAGYAR POLITIKA</h2><p>Lead a party from January 1991 to December 2030. Choose a difficulty and starting party.</p><label>Difficulty <select id="difficulty">${Object.entries(M.difficulties).map(([key,item])=>`<option value="${key}" ${key==='normal'?'selected':''}>${esc(item.name)} — ${key==='easy'?'more starting funds and a modest election boost':key==='hard'?'fewer funds and tougher elections':'balanced starting conditions'}</option>`).join('')}</select></label><p>Starting party</p><div class="choices">${startingParties.map(([key,item])=>`<button data-start-party="${esc(key)}" style="border-left:8px solid ${item.c}">${esc(item.n)}</button>`).join('')}<button data-start-party="CUSTOM">Found a custom party</button></div><label>Leader <select id="leader-choice"></select></label><label id="custom-label" hidden>Custom party name <input id="custom-name" maxlength="40" value="My Party"></label><label>Mentor <select id="start-mentor">${Object.entries(M.mentors).map(([key,item])=>`<option value="${key}" ${key==='magyar'?'selected':''}>${esc(item.n)}</option>`).join('')}</select></label><div class="choices"><button id="start-game">Start in 1991</button></div>`);
  let choice='MDF';
  const setChoice=key=>{choice=key;const opts=M.leaders[key]||['Party founder'];$('#leader-choice').innerHTML=opts.map(value=>`<option>${esc(value)}</option>`).join('');$('#custom-label').hidden=key!=='CUSTOM';document.querySelectorAll('[data-start-party]').forEach(b=>b.classList.toggle('selected',b.dataset.startParty===key));};
  document.querySelectorAll('[data-start-party]').forEach(button=>button.onclick=()=>setChoice(button.dataset.startParty));
  setChoice(choice);
  $('#start-game').onclick=async()=>{
    try {
      S=await api('new',{party:choice,difficulty:$('#difficulty').value,leader:$('#leader-choice').value,pname:choice==='CUSTOM'?$('#custom-name').value:'',mentor:$('#start-mentor').value});
      tab='Party';selected=0;resumeSpeed=1;closeModal();
    } catch(error){alert(error.message);}
  };
}
async function copySave() {
  const code=btoa(unescape(encodeURIComponent(JSON.stringify(S))));
  $('#save-box').value=code;
  try { await navigator.clipboard.writeText(code); S.flash='Save code copied.';render(); } catch (_) { $('#save-box').select();document.execCommand('copy'); }
}
function loadSave() {
  try { const code=$('#save-box').value.trim();const decoded=decodeURIComponent(escape(atob(code)));const next=JSON.parse(decoded);if(typeof next.m!=='number'||!M.parties[next.party])throw new Error();S=next;selected=0;render();checkOverlays(); }
  catch(_){alert('That save code could not be loaded.');}
}
function checkOverlays() {
  if(modalOpen||!S)return;
  if(S.over){openModal(`<h2>${S.over==='dissolved'?'Party dissolved':'End of 2030'}</h2><p>Final score: ${S.score}</p><p>The simplified simulation has ended.</p><div class="choices"><button id="restart">New game</button></div>`);$('#restart').onclick=startMenu;return;}
  if(S.event){
    const ev=S.event;
    openModal(`<h2>${esc(ev.title)}</h2><p>${esc(ev.text)}</p><div class="choices">${ev.choices.map((choice,index)=>`<button data-choice="${index}">${esc(choice[0])}</button>`).join('')}</div>`);
    document.querySelectorAll('[data-choice]').forEach(button=>button.onclick=async()=>{try{S=await api('choice',{state:S,i:Number(button.dataset.choice)});closeModal();}catch(error){alert(error.message);}});
    return;
  }
  if(S.result&&seenElectionYear!==S.result.year){
    seenElectionYear=S.result.year;
    const result=S.result;
    const rows=Object.entries(result.seats).sort((a,b)=>b[1]-a[1]).map(([party,count])=>`<div class="seat-row"><b>${esc(partyName(party))}</b><span class="bar"><i data-width="${count/199*100}" style="background:${partyColor(party)}"></i></span><b>${count}</b></div>`).join('');
    openModal(`<h2>Election night · ${result.year}</h2>${rows}<div class="result-banner">Government: ${esc(partyName(result.gov))}${result.coalition?` + ${esc(partyName(result.coalition))}`:''} · ${result.maj} seats needed for a majority${result.supermaj?' · two-thirds majority':''}</div><p>Your party: ${result.shares[S.party]||0}% · ${S.seats} seats. Figures are simplified.</p><div class="choices"><button id="election-ok">Continue</button></div>`);
    setTimeout(()=>document.querySelectorAll('[data-width]').forEach(bar=>bar.style.width=`${bar.dataset.width}%`),40);
    $('#election-ok').onclick=closeModal; return;
  }
}
async function tick() {
  if(S&&speed&&!busy&&!modalOpen&&!S.over&&!S.event){
    busy=true;
    try { S=await api('tick',{state:S});render();checkOverlays(); }
    catch(error){console.error(error);S.flash='Could not advance the game. Check your connection.';render();}
    finally{busy=false;}
  }
  setTimeout(tick,700/Math.max(1,speed));
}
document.addEventListener('keydown',event=>{
  if(!S||/INPUT|TEXTAREA|SELECT/.test(event.target.tagName))return;
  if(event.code==='Space'){event.preventDefault();setSpeed(speed?0:resumeSpeed||1);}
  if(event.key==='1')setSpeed(1);if(event.key==='2')setSpeed(2);if(event.key==='3')setSpeed(4);
});
fetch('/api/meta').then(response=>{if(!response.ok)throw new Error();return response.json();}).then(data=>{
  M=data;
  const saved=localStorage.getItem('magyar-politika-save');
  if(saved){try{S=JSON.parse(saved);}catch(_){localStorage.removeItem('magyar-politika-save');}}
  if(S){selected=0;render();checkOverlays();}else startMenu();
  drawMap();setInterval(()=>{if(!matchMedia('(prefers-reduced-motion: reduce)').matches)drawMap();},350);
  tick();
}).catch(error=>{console.error(error);$('#panel').textContent='Game data could not load. Check that the Render service is running the latest deployment.';});
