/* Historic Hungarian public-figure roster and freely licensed, pixelated Commons portraits. */
(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const roster = [
    {name:'Antall József',party:'MDF',period:'National Assembly member, 1990–1993'},
    {name:'Horn Gyula',party:'MSZP',period:'National Assembly member, 1990–2010'},
    {name:'József Torgyán',party:'FKGP',period:'National Assembly member, 1990–2001'},
    {name:'László Kövér',party:'Fidesz',period:'National Assembly member'},
    {name:'Viktor Orbán',party:'Fidesz',period:'National Assembly member'},
    {name:'Gergely Gulyás',party:'Fidesz',period:'National Assembly member'},
    {name:'Katalin Novák',party:'Fidesz',period:'Former National Assembly member'},
    {name:'László Surján',party:'KDNP',period:'National Assembly member'},
    {name:'Péter Magyar',party:'Tisza',period:'National Assembly member in the game’s 2026 scenario'}
  ];
  const mentors = {'antall':'Antall József','horn':'Horn Gyula','orban':'Viktor Orbán','magyar':'Péter Magyar'};
  const cache = new Map();
  function clean(value) {
    const node = document.createElement('span'); node.innerHTML = value || '';
    return (node.textContent || '').replace(/\s+/g,' ').trim().slice(0,160);
  }
  async function commonsPhoto(name) {
    if (!cache.has(name)) cache.set(name, (async () => {
      const query = encodeURIComponent(`${name} portrait`);
      const url = `https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=${query}&gsrnamespace=6&gsrlimit=8&prop=imageinfo&iiprop=url%7Cextmetadata&iiurlwidth=160&format=json&origin=*`;
      try {
        const response = await fetch(url);
        if (!response.ok) return null;
        const data = await response.json();
        const pages = Object.values(data.query?.pages || {});
        const page = pages.find(item => item.imageinfo?.[0]?.thumburl && !/\.svg(?:$|\?)/i.test(item.imageinfo[0].thumburl));
        if (!page) return null;
        const info = page.imageinfo[0], meta = info.extmetadata || {};
        const license = clean(meta.LicenseShortName?.value) || 'Wikimedia Commons';
        const artist = clean(meta.Artist?.value) || clean(meta.Credit?.value) || 'Contributor listed on Commons';
        return {url:info.thumburl,source:info.descriptionurl || info.url,license,artist,file:page.title};
      } catch (_) { return null; }
    })());
    return cache.get(name);
  }
  function portraitCard(name, className='historic-portrait') {
    const card = document.createElement('div'); card.className=`${className} portrait-card`;
    card.innerHTML=`<div class="portrait-frame"><span class="portrait-placeholder" aria-hidden="true">${esc(name.split(/\s+/).map(part=>part[0]).slice(0,2).join(''))}</span></div><div class="portrait-caption"><b>${esc(name)}</b><span class="portrait-credit">Searching Wikimedia Commons…</span></div>`;
    commonsPhoto(name).then(image=>{
      if(!card.isConnected)return;
      const frame=$('.portrait-frame',card),credit=$('.portrait-credit',card);
      if(!image){credit.textContent='Photo unavailable; portrait search can be retried later.';return;}
      const img=document.createElement('img');img.src=image.url;img.alt=`Photograph of ${name}, displayed with a 16-bit pixel effect`;img.loading='lazy';img.crossOrigin='anonymous';
      img.onerror=()=>{img.remove();credit.textContent='Photo unavailable from Commons.'};
      frame.prepend(img);frame.classList.add('has-photo');
      const link=document.createElement('a');link.href=image.source;link.target='_blank';link.rel='noopener noreferrer';link.textContent=`${image.artist} · ${image.license} · source`;
      credit.replaceChildren(link);
    });
    return card;
  }
  function installCandidatePicker() {
    const form=$('#mp-form');
    if(!form || $('select[name="historic-mp"]',form))return;
    const current=$('#mp-name',form)?.value || '';
    const input=$('#mp-name',form);
    const select=document.createElement('select');select.name='historic-mp';select.setAttribute('aria-label','Select a historical Hungarian parliament member');
    select.innerHTML=`<option value="">Choose a public figure…</option>${roster.map(person=>`<option value="${esc(person.name)}" ${person.name===current?'selected':''}>${esc(person.name)} — ${esc(person.party)}</option>`).join('')}`;
    input?.replaceWith(select);
    const help=document.createElement('p');help.className='roster-note';help.textContent='Select an actual Hungarian parliament member. County placement is your game appointment, not a claim about their historical constituency.';
    form.insertAdjacentElement('beforebegin',help);
    const preview=portraitCard(select.value || roster[0].name,'candidate-preview');
    form.insertAdjacentElement('beforebegin',preview);
    select.addEventListener('change',()=>{
      const person=roster.find(item=>item.name===select.value);
      if(!person)return;
      const replacement=portraitCard(person.name,'candidate-preview');
      preview.replaceWith(replacement);
    });
    form.addEventListener('submit',event=>{
      event.preventDefault();
      if(!select.value){select.focus();return;}
      const submit=form.querySelector('button');
      if(submit)submit.dataset.historicMpName=select.value;
      // Existing game handler reads #mp-name. A hidden compatibility field keeps its request shape.
      let hidden=$('#mp-name',form);
      if(!hidden){hidden=document.createElement('input');hidden.type='hidden';hidden.id='mp-name';form.appendChild(hidden);}
      hidden.value=select.value;
    },true);
    // Existing game.js reads #mp-name before submitting, so mirror selection continuously.
    select.addEventListener('change',()=>{
      let hidden=$('#mp-name',form);if(!hidden){hidden=document.createElement('input');hidden.type='hidden';hidden.id='mp-name';form.appendChild(hidden);}hidden.value=select.value;
    });
    if(select.value){let hidden=document.createElement('input');hidden.type='hidden';hidden.id='mp-name';hidden.value=select.value;form.appendChild(hidden);}
  }
  function installMentorPortrait() {
    const select=$('#mentor-select');
    if(!select)return;
    const holder=select.parentElement;
    if(!holder)return;
    let card=$('.mentor-photo',holder);
    const name=mentors[select.value];
    if(!name)return;
    if(card?.dataset.person===name)return;
    const next=portraitCard(name,'mentor-photo');next.dataset.person=name;
    if(card)card.replaceWith(next);else select.insertAdjacentElement('afterend',next);
  }
  function installLeaderPhotos() {
    document.querySelectorAll('[data-portrait-party] img').forEach(img=>{
      const button=img.closest('[data-portrait-party]');
      const person=roster.find(item=>item.party.toUpperCase()===button?.dataset.portraitParty?.toUpperCase());
      if(!person || img.dataset.commonsLookup)return;
      img.dataset.commonsLookup='true';
      commonsPhoto(person.name).then(image=>{
        if(!image || !img.isConnected)return;
        img.src=image.url;img.alt=`Photograph of ${person.name}, pixelated for the 16-bit game style`;
        const credit=document.createElement('a');credit.className='portrait-source';credit.href=image.source;credit.target='_blank';credit.rel='noopener noreferrer';credit.textContent=`Photo: ${image.artist} · ${image.license}`;
        button.appendChild(credit);
      });
    });
  }
  function refresh(){installCandidatePicker();installMentorPortrait();installLeaderPhotos();}
  const observer=new MutationObserver(refresh);
  observer.observe(document.documentElement,{childList:true,subtree:true});
  refresh();
})();
