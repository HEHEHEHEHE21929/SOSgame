/* Interactive, in-context walkthrough plus original 16-bit-style politician sprites. */
(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const SAVE_KEY = 'magyar-politika-save';
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
    {id:'start', title:'Start a campaign', body:'First, create a campaign. Click the highlighted <b>Start in 1991</b> button in the game setup window.', tip:'Choose any party and difficulty you like; your choice will not affect the tutorial.', target:'#start-game', selector:'#start-game', complete:()=>Boolean(readSave())},
    {id:'map', title:'Pick a county', body:'Click a highlighted county on the map. The information card below the map will show its profile.', tip:'Click any county shape—Budapest is the first shape near the middle.', target:'#map', selector:'#map', complete:()=>!$('#info')?.textContent.includes('Select a county to inspect')},
    {id:'campaign-tab', title:'Open Campaign', body:'Now click the highlighted <b>Campaign</b> tab. The panel will change to your campaign office.', tip:'The tab is in the top navigation bar.', target:'[data-tab="Campaign"]', selector:'[data-tab="Campaign"]', complete:()=>$('.tabs [data-tab="Campaign"]')?.classList.contains('active')},
    {id:'campaign-action', title:'Run a campaign action', body:'Click one of the highlighted campaign actions, such as posters, a rally, or polling. Watch the funds and campaign journal update.', tip:'If the action cannot run because funds are low, the game will explain why; you can still continue.', target:'#panel [data-campaign]', selector:'#panel [data-campaign]', complete:()=>{const state=readSave();return Boolean(state?.flash && state.flash!==stepBaseline);}},
    {id:'learning-tab', title:'Explore the learning tabs', body:'Click <b>Policy</b> or <b>Advisors</b> to see how policies and mentor choices work.', tip:'Some policy actions are available only when your party leads government.', target:'[data-tab="Policy"], [data-tab="Advisors"]', selector:'[data-tab="Policy"], [data-tab="Advisors"]', complete:()=>['Policy','Advisors'].some(name=>$(`.tabs [data-tab="${name}"]`)?.classList.contains('active'))},
    {id:'save-tab', title:'Save your campaign', body:'Click the <b>Game</b> tab, then press <b>Copy save code</b>. This gives you a portable backup of your campaign.', tip:'Progress is also saved automatically in this browser.', target:'[data-tab="Game"]', selector:'[data-tab="Game"]', complete:()=>$('.tabs [data-tab="Game"]')?.classList.contains('active')},
    {id:'save-code', title:'That’s it—you’re ready!', body:'Your save code is ready in the text box. Keep it somewhere safe if you want to move the campaign to another browser.', tip:'You can reopen this guide any time from the Tutorial button.', target:'#copy-save', selector:'#copy-save', complete:()=>Boolean($('#save-box')?.value)}
  ];
  let step = 0;
  let layer = null;
  let activeTarget = null;
  let stepBaseline = null;
  let pollTimer = null;
  let resizeFrame = 0;

  function readSave() { try { return JSON.parse(localStorage.getItem(SAVE_KEY) || 'null'); } catch (_) { return null; } }
  function visibleTarget(selector) { return [...document.querySelectorAll(selector)].find(el=>el.getClientRects().length); }
  function clearTarget() { activeTarget?.classList.remove('tutorial-highlight'); activeTarget=null; }
  function positionCard() {
    if (!layer) return;
    const card=$('.tutorial-card',layer);
    if (!card) return;
    const margin=14, gap=16, rect=activeTarget?.getBoundingClientRect();
    const width=Math.min(410,window.innerWidth-margin*2);
    card.style.width=`${width}px`;
    const height=card.offsetHeight;
    let left=Math.max(margin,(window.innerWidth-width)/2), top=margin;
    if (rect) {
      const below=window.innerHeight-rect.bottom-gap-margin;
      const above=rect.top-gap-margin;
      if (below>=Math.min(height,190)) top=rect.bottom+gap;
      else if (above>=Math.min(height,190)) top=rect.top-height-gap;
      else top=Math.max(margin,Math.min(window.innerHeight-height-margin,(window.innerHeight-height)/2));
      if (window.innerWidth>760) {
        const right=window.innerWidth-rect.right-gap-width;
        const leftSpace=rect.left-gap-width;
        if (right>=margin) left=rect.right+gap;
        else if (leftSpace>=margin) left=leftSpace;
      }
    }
    top=Math.max(margin,Math.min(top,window.innerHeight-height-margin));
    left=Math.max(margin,Math.min(left,window.innerWidth-width-margin));
    card.style.left=`${left}px`; card.style.top=`${top}px`;
  }
  function attachTarget() {
    clearTarget();
    const current=steps[step];
    activeTarget=visibleTarget(current.target);
    if (activeTarget) {
      activeTarget.classList.add('tutorial-highlight');
      activeTarget.scrollIntoView({block:'nearest',inline:'nearest',behavior:'smooth'});
    }
    requestAnimationFrame(positionCard);
  }
  function closeTutorial() {
    clearInterval(pollTimer); pollTimer=null; clearTarget();
    if(layer) layer.remove();
    layer=null;
  }
  function finishStep() {
    if (!layer) return;
    if (step < steps.length-1) { step++; drawTutorial(); }
    else { localStorage.setItem('magyar-politika-tutorial-complete','true'); closeTutorial(); }
  }
  function drawTutorial() {
    if (!layer) {
      layer=document.createElement('div'); layer.id='tutorial-layer';
      layer.setAttribute('role','region'); layer.setAttribute('aria-label','Interactive game tutorial');
      document.body.appendChild(layer);
    }
    stepBaseline=readSave()?.flash ?? null;
    const item=steps[step];
    layer.innerHTML=`<section class="tutorial-card" role="dialog" aria-modal="false" aria-labelledby="tutorial-title"><div class="tutorial-progress">STEP ${step+1} OF ${steps.length}</div><h2 id="tutorial-title">${esc(item.title)}</h2><p>${item.body}</p><p class="tutorial-tip"><b>TIP</b> ${esc(item.tip)}</p><p class="tutorial-hint">Click the glowing control to complete this step.</p><div class="tutorial-actions"><button type="button" id="tutorial-back" ${step===0?'disabled':''}>Back</button><button type="button" id="tutorial-close">Exit</button><button type="button" id="tutorial-next">Skip step →</button></div></section>`;
    $('#tutorial-close',layer).onclick=closeTutorial;
    $('#tutorial-back',layer).onclick=()=>{if(step>0){step--;drawTutorial();}};
    $('#tutorial-next',layer).onclick=finishStep;
    attachTarget();
    clearInterval(pollTimer);
    pollTimer=setInterval(()=>{
      if (layer && steps[step].complete()) finishStep();
    },300);
  }
  function showTutorial() {
    if (layer) closeTutorial();
    // Skip campaign creation when a save already exists; continue at the map step.
    step=readSave()?1:0;
    drawTutorial();
  }
  window.addEventListener('resize',()=>{cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(positionCard);});
  window.addEventListener('scroll',()=>{cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(positionCard);},true);

  function galleryMarkup(selected) {
    return `<section aria-label="Choose a historical party leader"><h3>Choose a leader</h3><div class="politician-gallery">${roster.map((person,index)=>`<button type="button" class="politician-option ${person.party===selected?'selected':''}" data-portrait-party="${person.party}" aria-pressed="${person.party===selected}"><img src="${sprite(person.colors,index)}" alt="Original 16-bit-style pixel-art avatar for ${esc(person.name)}; not a photograph"><b>${esc(person.name)}</b><span>${esc(person.title)}</span></button>`).join('')}<p class="portrait-note">Original retro pixel-art avatars, not archival photographs. Selecting a portrait also selects that party.</p></div></section>`;
  }
  function installGallery() {
    const dialog=$('.dialog');
    if(!dialog || !$('#leader-name',dialog) || $('#politician-gallery',dialog)) return;
    const leader=$('#leader-name',dialog);
    const gallery=document.createElement('div'); gallery.id='politician-gallery'; gallery.innerHTML=galleryMarkup('MDF');
    leader.closest('label')?.insertAdjacentElement('beforebegin',gallery);
    gallery.addEventListener('click',event=>{
      const button=event.target.closest('[data-portrait-party]'); if(!button)return;
      const person=roster.find(item=>item.party===button.dataset.portraitParty); if(!person)return;
      $(`[data-party="${person.party}"]`,dialog)?.click();
      leader.value=person.name; gallery.innerHTML=galleryMarkup(person.party);
    });
    dialog.addEventListener('click',event=>{
      const button=event.target.closest('[data-party]'); if(!button)return;
      const person=roster.find(item=>item.party===button.dataset.party);
      if(person){leader.value=person.name;gallery.innerHTML=galleryMarkup(person.party);}
    });
  }
  function addTutorialButton() {
    const top=$('#top');
    if(top && !$('#tutorial-open',top)) {
      const button=document.createElement('button'); button.id='tutorial-open'; button.type='button'; button.textContent='Tutorial'; button.title='Open the interactive game walkthrough'; button.onclick=showTutorial; top.appendChild(button);
    }
    const dialog=$('.dialog');
    if(dialog && !$('#tutorial-start',dialog)) {
      const button=document.createElement('button'); button.id='tutorial-start'; button.type='button'; button.textContent='How to play'; button.onclick=showTutorial;
      const heading=$('h2',dialog); if(heading) heading.insertAdjacentElement('afterend',button);
    }
  }
  const observer=new MutationObserver(()=>{addTutorialButton();installGallery();if(layer){const target=visibleTarget(steps[step].target);if(target!==activeTarget)attachTarget();else requestAnimationFrame(positionCard);}});
  observer.observe(document.documentElement,{childList:true,subtree:true});
  addTutorialButton(); installGallery();
})();
