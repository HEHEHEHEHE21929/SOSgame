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

  let step = 0;
  let layer = null;
  let completed = false;
  let observeTimer = null;

  const steps = [
    {title:'Welcome, campaign manager!',body:'Choose the <b>Party</b> tab and select a party. This is a clickable step—try it now.',tip:'The highlighted control is the next thing to use.',target:'[data-tab="Party"]',action:'click',advance:()=>$('.dialog [data-party]')?.closest('.dialog') || false},
    {title:'Choose a county',body:'Click a county on the map to inspect its seats and local candidate.',tip:'Budapest is a good place to start.',target:'#map',action:'click',advance:()=>localStorage.getItem('magyar-politika-save')!==null},
    {title:'Open Campaign',body:'Select the <b>Campaign</b> tab. Campaign actions cost money and improve support.',tip:'The Campaign tab stays open after nationwide actions.',target:'[data-tab="Campaign"]',action:'click',advance:()=>$('.tabs [data-tab="Campaign"]')?.classList.contains('active')},
    {title:'Try a campaign action',body:'Choose either a local campaign button or enable <b>Nationwide campaign</b>.',tip:'You do not need to spend money to continue if funds are low.',target:'#panel [data-campaign], #campaign-target-scope',action:'click',advance:()=>true},
    {title:'Read Policy and Advisors',body:'Open <b>Policy</b> or <b>Advisors</b> to see trade-offs and historical advice.',tip:'Policies require government status.',target:'[data-tab="Policy"], [data-tab="Advisors"]',action:'click',advance:()=>true},
    {title:'Save your campaign',body:'Open <b>Game</b>, then use <b>Copy save code</b>. You can also load a save code later.',tip:'Your campaign is also stored in this browser.',target:'[data-tab="Game"]',action:'click',advance:()=>true}
  ];

  function removeHighlights() {
    document.querySelectorAll('.tutorial-highlight').forEach(el=>el.classList.remove('tutorial-highlight'));
  }
  function highlightTarget() {
    removeHighlights();
    const item = steps[step];
    if (!item?.target) return;
    const candidates = [...document.querySelectorAll(item.target)].filter(el=>el.offsetParent!==null);
    candidates.forEach(el=>el.classList.add('tutorial-highlight'));
  }
  function showTutorial() {
    step = 0;
    completed = false;
    drawTutorial();
  }
  function closeTutorial() {
    removeHighlights();
    if (layer) layer.remove();
    layer = null;
  }
  function drawTutorial() {
    if (!layer) {
      layer = document.createElement('div');
      layer.id = 'tutorial-layer';
      layer.setAttribute('role','dialog');
      layer.setAttribute('aria-modal','true');
      layer.setAttribute('aria-label','Interactive game tutorial');
      document.body.appendChild(layer);
    }
    const item = steps[step];
    layer.innerHTML = `<section class="tutorial-card"><div class="tutorial-progress">Interactive guide · Step ${step+1} of ${steps.length}</div><h2>${esc(item.title)}</h2><p>${item.body}</p><p><b>Tip:</b> ${esc(item.tip)}</p><div class="tutorial-actions"><button type="button" id="tutorial-back" ${step===0?'disabled':''}>Back</button><button type="button" id="tutorial-skip">Close guide</button><button type="button" id="tutorial-next">${step===steps.length-1?'Finish':'Next'}</button></div></section>`;
    $('#tutorial-skip',layer).onclick=closeTutorial;
    $('#tutorial-back',layer).onclick=()=>{if(step>0){step--;drawTutorial();}};
    $('#tutorial-next',layer).onclick=()=>advanceManual();
    $('#tutorial-next',layer).focus();
    highlightTarget();
  }
  function advanceManual() {
    if (step < steps.length-1) {
      step++;
      drawTutorial();
    } else {
      completed = true;
      closeTutorial();
      localStorage.setItem('magyar-politika-tutorial-complete','true');
    }
  }
  function checkInteractiveStep() {
    if (!layer) return;
    const item = steps[step];
    if (!item?.advance) return;
    try {
      if (item.advance()) {
        clearTimeout(observeTimer);
        observeTimer=setTimeout(()=>{
          if (layer && step===0 && $('.dialog [data-party].selected')) advanceManual();
          else if (layer && step===1) advanceManual();
          else if (layer && step===2 && $('.tabs [data-tab="Campaign"]')?.classList.contains('active')) advanceManual();
          else if (layer && step===3) advanceManual();
          else if (layer && step===4) advanceManual();
          else if (layer && step===5) advanceManual();
        },350);
      }
    } catch (_) {}
  }

  document.addEventListener('click',event=>{
    if (!layer) return;
    if (observeTimer) clearTimeout(observeTimer);
    observeTimer=setTimeout(checkInteractiveStep,500);
  },true);

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
      if (layer) setTimeout(checkInteractiveStep,300);
    });
    dialog.addEventListener('click',event=>{
      const partyButton=event.target.closest('[data-party]');if(!partyButton)return;
      const person=roster.find(item=>item.party===partyButton.dataset.party);
      if(person){leader.value=person.name;gallery.innerHTML=galleryMarkup(person.party)}
    });
  }
  function addTutorialButton() {
    const top = $('#top');
    if (top && !$('#tutorial-open',top)) {
      const button = document.createElement('button'); button.id='tutorial-open'; button.type='button'; button.textContent='Tutorial'; button.title='Open the interactive game tutorial'; button.onclick=showTutorial; top.appendChild(button);
    }
    const dialog = $('.dialog');
    if(dialog && !$('#tutorial-start',dialog)) {
      const button=document.createElement('button');button.id='tutorial-start';button.type='button';button.textContent='How to play';button.onclick=showTutorial;
      const heading=$('h2',dialog); if(heading) heading.insertAdjacentElement('afterend',button);
    }
  }

  const observer = new MutationObserver(()=>{addTutorialButton();installGallery();highlightTarget();});
  observer.observe(document.documentElement,{childList:true,subtree:true});
  addTutorialButton();installGallery();
})();
