/* Curated Commons portraits only: reject unrelated search matches and show clean photo crops. */
(() => {
  'use strict';
  const $=(selector,root=document)=>root.querySelector(selector);
  const esc=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const roster=[
    {name:'Antall József',party:'MDF',period:'National Assembly member, 1990–1993'},
    {name:'Horn Gyula',party:'MSZP',period:'National Assembly member, 1990–2010'},
    {name:'József Torgyán',party:'FKGP',period:'National Assembly member, 1990–2001'},
    {name:'László Kövér',party:'Fidesz',period:'National Assembly member'},
    {name:'Viktor Orbán',party:'Fidesz',period:'National Assembly member'},
    {name:'Gergely Gulyás',party:'Fidesz',period:'National Assembly member'},
    {name:'Katalin Novák',party:'Fidesz',period:'Former National Assembly member'},
    {name:'László Surján',party:'KDNP',period:'National Assembly member'},
    {name:'Péter Magyar',party:'Tisza',period:'National Assembly member in the game scenario'}
  ];
  const mentors={antall:'Antall József',horn:'Horn Gyula',orban:'Viktor Orbán',magyar:'Péter Magyar'}, cache=new Map();
  const text=value=>{const node=document.createElement('span');node.innerHTML=value||'';return(node.textContent||'').replace(/\s+/g,' ').trim().slice(0,150);};
  const tokens=name=>name.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
  async function commonsPhoto(name){
    if(!cache.has(name))cache.set(name,(async()=>{
      const query=encodeURIComponent(`"${name}"`);
      const url=`https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=${query}&gsrnamespace=6&gsrlimit=12&prop=imageinfo&iiprop=url%7Cextmetadata%7Csize&iiurlwidth=240&format=json&origin=*`;
      try{
        const response=await fetch(url);if(!response.ok)return null;const data=await response.json();
        const candidates=Object.values(data.query?.pages||{}).map(page=>({page,info:page.imageinfo?.[0]})).filter(x=>x.info?.thumburl&&!/\.(svg|gif)(?:$|\?)/i.test(x.info.thumburl));
        const wanted=tokens(name).filter(x=>x.length>2);
        const relevant=candidates.filter(({page,info})=>{const title=tokens(page.title);return wanted.every(token=>title.includes(token))&&Number(info.width)>=300&&Number(info.height)>=300;});
        // Never show a vaguely related Commons result as if it were the named politician.
        const pick=relevant.sort((a,b)=>Number(b.info.width*b.info.height)-Number(a.info.width*a.info.height))[0];if(!pick)return null;
        const info=pick.info,meta=info.extmetadata||{};
        return{url:info.thumburl,source:info.descriptionurl||info.url,license:text(meta.LicenseShortName?.value)||'Wikimedia Commons',artist:text(meta.Artist?.value)||text(meta.Credit?.value)||'Photographer credited on Commons',file:pick.page.title};
      }catch(_){return null;}
    })());return cache.get(name);
  }
  function portraitCard(name,className='historic-portrait'){
    const card=document.createElement('div');card.className=`${className} portrait-card`;
    card.innerHTML=`<div class="portrait-frame"><span class="portrait-placeholder" aria-hidden="true">${esc(name.split(/\s+/).map(x=>x[0]).slice(0,2).join(''))}</span></div><div class="portrait-caption"><b>${esc(name)}</b><span class="portrait-credit">Looking for a verified Commons portrait…</span></div>`;
    commonsPhoto(name).then(image=>{if(!card.isConnected)return;const frame=$('.portrait-frame',card),credit=$('.portrait-credit',card);if(!image){credit.textContent='No clearly matched, sufficiently large portrait found; showing initials instead.';return;}const img=document.createElement('img');img.src=image.url;img.alt=`Portrait photograph of ${name}`;img.loading='lazy';img.referrerPolicy='no-referrer';img.onerror=()=>{img.remove();credit.textContent='Portrait image unavailable; initials shown.'};frame.prepend(img);frame.classList.add('has-photo');const link=document.createElement('a');link.href=image.source;link.target='_blank';link.rel='noopener noreferrer';link.textContent=`${image.artist} · ${image.license} · source`;credit.replaceChildren(link);});return card;
  }
  function installCandidatePicker(){const form=$('#mp-form');if(!form||$('select[name="historic-mp"]',form))return;const old=$('#mp-name',form),current=old?.value||'',select=document.createElement('select');select.name='historic-mp';select.setAttribute('aria-label','Choose a Hungarian parliament member');select.innerHTML=`<option value="">Choose a public figure…</option>${roster.map(p=>`<option value="${esc(p.name)}" ${p.name===current?'selected':''}>${esc(p.name)} — ${esc(p.party)}</option>`).join('')}`;old?.replaceWith(select);const note=document.createElement('p');note.className='roster-note';note.textContent='Historical public figures are offered as game candidates; county assignment is a fictional game appointment, not a claim about their actual constituency.';form.before(note);const preview=portraitCard(select.value||roster[0].name,'candidate-preview');form.before(preview);const ensureHidden=()=>{let input=$('#mp-name',form);if(!input){input=document.createElement('input');input.type='hidden';input.id='mp-name';form.append(input);}input.value=select.value;};select.addEventListener('change',()=>{ensureHidden();const person=roster.find(p=>p.name===select.value);if(person)preview.replaceWith(portraitCard(person.name,'candidate-preview'));});if(select.value)ensureHidden();}
  function installMentorPortrait(){const select=$('#mentor-select');if(!select)return;const name=mentors[select.value];if(!name)return;const holder=select.parentElement;if(!holder)return;const old=$('.mentor-photo',holder);if(old?.dataset.person===name)return;const card=portraitCard(name,'mentor-photo');card.dataset.person=name;if(old)old.replaceWith(card);else select.after(card);}
  function installLeaderPhotos(){document.querySelectorAll('[data-portrait-party] img').forEach(img=>{const button=img.closest('[data-portrait-party]'),person=roster.find(p=>p.party.toUpperCase()===button?.dataset.portraitParty?.toUpperCase());if(!person||img.dataset.commonsLookup)return;img.dataset.commonsLookup='1';commonsPhoto(person.name).then(image=>{if(!image||!img.isConnected)return;img.src=image.url;img.alt=`Portrait photograph of ${person.name}`;img.style.imageRendering='auto';const source=document.createElement('a');source.className='portrait-source';source.href=image.source;source.target='_blank';source.rel='noopener noreferrer';source.textContent=`${image.artist} · ${image.license} · source`;button.append(source);});});}
  function refresh(){installCandidatePicker();installMentorPortrait();installLeaderPhotos();}
  new MutationObserver(refresh).observe(document.documentElement,{childList:true,subtree:true});refresh();
})();
