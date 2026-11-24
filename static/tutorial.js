/* Optional guided tutorial and original 16-bit-style politician sprites. */
(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const roster = [
    {party:'MDF',name:'Antall József',title:'MDF · founding-era leader',colors:['#d4a875','#49352c','#e5c4a0','#314c50']},
    {party:'SZDSZ',name:'Kis János',title:'SZDSZ · founding leader',colors:['#c9b193','#554b43','#e4cbb0','#35465b']},
    {party:'MSZP',name:'Horn Gyula',title:'MSZP · party leader',colors:['#c8a07b','#8b8b83','#e5c2a1','#6b373c']},
    {party:'FKGP',name:'Torgyán József',title:'FKGP · party leader',colors:['#d0a478','#514239','#edc7a2','#526047']},
    {party:'KDNP',name:'Surján László',title:'KDNP · party leader',colors:['#c7a784','#6b655a','#e4c7a6','#46516c']},
    {party:'FIDESZ',name:'Orbán Viktor',title:'Fidesz · founding-generation leader',colors:['#c89b73','#3f3028','#e7c2a0','#3d5a68']}
  ];
  const sprite = (colors, seed) => {
    const [skin,hair,light,suit] = colors;
    const variation = seed % 2 ? '<rect x="22" y="39" width="4" height="3" fill="#69483b"/><rect x="38" y="39" width="4" height="3" fill="#69483b"/>' : '<rect x="23" y="39" width="4" height="2" fill="#49352c"/><rect x="37" y="39" width="4" height="2" fill="#49352c"/>';
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="64" height="80" viewBox="0 0 64 80" shape-rendering="crispEdges"><rect width="64" height="80" fill="#192b49"/><path fill="#d9b866" d="M4 8h56v4H4zM4 68h56v4H4z"/><path fill="#263f62" d="M8 16h48v48H8z"/><path fill="${hair}" d="M18 22h28v8h4v22h-6v8H20v-8h-6V30h4z"/><path fill="${skin}" d="M20 28h24v22H20z"/><path fill="${light}" d="M22 30h5v4h-5zm15 0h5v4h-5z"/><path fill="#222534" d="M23 32h3v3h-3zm15 0h3v3h-3z"/>${variation}<path fill="#f0d4b8" d="M28 45h8v3h-8z"/><path fill="${suit}" d="M12 64h40v12H12zM18 55h28v10H18z"/><path fill="#e9ddc0" d="M29 56h6v11h-6z"/><path fill="#bd554d" d="M30 58h4v9h-4z"/></svg>`;
    return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
  };
  const steps = [
    {title:'Welcome, campaign manager!',body:'Your goal is to build support, win seats, and govern. The game is a simplified classroom simulation, not a forecast or a record of actual election results.',tip:'Choose a party and leader to begin. You can reopen this guide from the Tutorial button.'},
    {title:'Read the map',body:'Click a county to inspect its type, constituency seats, recent winner, and local candidate. The map is a stylized county layout; colors show the last simulated constituency winner.',tip:'Try Budapest or a neighboring county. Select a county before running a local campaign or recruiting an MP.'},
    {title:'Campaign strategically',body:'Campaigns cost money and can improve support. Register candidates before election day to avoid a ballot penalty. Polling is more reliable while an accuracy-polling action is active.',tip:'Watch your funds and the election countdown at the top. Time advances only when you choose a speed.'},
    {title:'Win seats and learn policy',body:'Elections happen every three years. Parties under the 5% threshold normally miss out on list seats. Leading government unlocks policy choices, each with a cost and a voter-group trade-off.',tip:'Use the Policy and Advisors tabs to see what changed and why. Enacted policies are recorded in the policy list.'},
    {title:'Save your campaign',body:'The Game tab lets you copy a save code and load it later. Your current progress is also saved in this browser.',tip:'Have fun experimenting—different campaign plans and policy choices can lead to different outcomes.'}
  ];
  let step = 0;
  function showTutorial() {
    step = 0;
    drawTutorial();
  }
  function drawTutorial() {
    let layer = $('#tutorial-layer');
    if (!layer) {
      layer = document.createElement('div'); layer.id = 'tutorial-layer'; layer.setAttribute('role','dialog'); layer.setAttribute('aria-modal','true'); layer.setAttribute('aria-label','Game tutorial');
      document.body.appendChild(layer);
    }
    const item = steps[step];
    layer.innerHTML = `<section class="tutorial-card"><h2>${esc(item.title)}</h2><p>${esc(item.body)}</p><p><b>Tip:</b> ${esc(item.tip)}</p><div class="tutorial-actions"><button id="tutorial-skip">Close guide</button><span>Step ${step+1} of ${steps.length}</span><button id="tutorial-next">${step===steps.length-1?'Finish':'Next'}</button></div></section>`;
    $('#tutorial-skip',layer).onclick=()=>layer.remove();
    $('#tutorial-next',layer).onclick=()=>{if(step<steps.length-1){step++;drawTutorial()}else layer.remove()};
  }
  function addTutorialButton() {
    const top = $('#top');
    if (top && !$('#tutorial-open',top)) {
      const button = document.createElement('button'); button.id='tutorial-open'; button.type='button'; button.textContent='Tutorial'; button.title='Open the quick game tutorial'; button.onclick=showTutorial; top.appendChild(button);
    }
    const dialog = $('.dialog');
    if(dialog && !$('#tutorial-start',dialog)) {
      const button=document.createElement('button');button.id='tutorial-start';button.type='button';button.textContent='How to play';button.onclick=showTutorial;
      const heading=$('h2',dialog); if(heading) heading.insertAdjacentElement('afterend',button);
    }
  }
  function galleryMarkup(selected) {
    return `<section aria-label="Choose a historical party leader"><h3>Choose a leader</h3><div class="politician-gallery">${roster.map((person,index)=>`<button type="button" class="politician-option ${person.party===selected?'selected':''}" data-portrait-party="${person.party}" aria-pressed="${person.party===selected}"><img src="${sprite(person.colors,index)}" alt="Original 16-bit-style pixel-art avatar for ${esc(person.name)}; not a photograph"><b>${esc(person.name)}</b><span>${esc(person.title)}</span></button>`).join('')}<p class="portrait-note">Original retro pixel-art avatars, not archival photographs. Selecting a portrait also selects that party.</p></div></section>`;
  }
  function installGallery() {
    const dialog=$('.dialog');
    if(!dialog || !$('#leader-name',dialog) || $('#politician-gallery',dialog)) return;
    const leader=$('#leader-name',dialog);
    const gallery=document.createElement('div');gallery.id='politician-gallery';gallery.innerHTML=galleryMarkup('MDF');
    leader.closest('label')?.insertAdjacentElement('beforebegin',gallery);
    gallery.addEventListener('click',event=>{
      const button=event.target.closest('[data-portrait-party]'); if(!button)return;
      const person=roster.find(item=>item.party===button.dataset.portraitParty);if(!person)return;
      const partyButton=$(`[data-party="${person.party}"]`,dialog);partyButton?.click();
      leader.value=person.name;
      gallery.innerHTML=galleryMarkup(person.party);
    });
    dialog.addEventListener('click',event=>{
      const partyButton=event.target.closest('[data-party]');if(!partyButton)return;
      const person=roster.find(item=>item.party===partyButton.dataset.party);
      if(person){leader.value=person.name;gallery.innerHTML=galleryMarkup(person.party)}
    });
  }
  const observer = new MutationObserver(()=>{addTutorialButton();installGallery()});
  observer.observe(document.documentElement,{childList:true,subtree:true});
  addTutorialButton();installGallery();
})();
