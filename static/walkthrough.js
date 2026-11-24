/* Guided, in-game tasks: the card stays out of the way and advances on real actions. */
(() => {
  'use strict';
  const $=(selector,root=document)=>root.querySelector(selector);
  const SAVE_KEY='magyar-politika-save';
  let card=null,step=0,timer=null,active=null,lastFlash=null,mapSelections=0;
  const steps=[
    {title:'Start your campaign',text:'Choose a party and press <b>Start in 1991</b>. The guide will wait while your campaign loads.',selector:'#start-game',done:()=>save()!==null},
    {title:'Select a county',text:'Click a county shape on the map. A county name and profile will appear beneath it.',selector:'#map',done:()=>mapSelections>0},
    {title:'Open Campaign',text:'Click the Campaign tab. You’ll find campaign actions in the side panel.',selector:'[data-tab="Campaign"]',done:()=>tabIs('Campaign')},
    {title:'Try an action',text:'Click one of the highlighted actions—posters, rally, volunteer drive, or polling. Watch the funds and journal change.',selector:'#panel [data-campaign]',done:()=>Boolean(save()?.flash&&save().flash!==lastFlash)},
    {title:'Explore advice',text:'Open Advisors to read your mentor’s tips. Policy is there too; some policies unlock only when you lead government.',selector:'[data-tab="Advisors"]',done:()=>tabIs('Advisors')},
    {title:'Save your progress',text:'Open Game and click Copy save code. Your code appears in the box and can be copied to another browser.',selector:'[data-tab="Game"]',done:()=>tabIs('Game')},
    {title:'You’re ready to play!',text:'Your campaign autosaves in this browser. You can reopen this walkthrough from the Tutorial button whenever you need a reminder.',selector:'#tutorial-open',done:()=>true}
  ];
  function save(){try{return JSON.parse(localStorage.getItem(SAVE_KEY)||'null');}catch(_){return null;}}
  function tabIs(name){return $(`.tabs [data-tab="${name}"]`)?.classList.contains('active')||false;}
  function visible(selector){return [...document.querySelectorAll(selector)].find(el=>el.getClientRects().length);}
  function clearHighlight(){active?.classList.remove('tutorial-highlight');active=null;}
  function close(){clearInterval(timer);timer=null;clearHighlight();card?.remove();card=null;}
  function place(){if(!card)return;const box=$('.walkthrough-card',card);if(!box)return;const gap=14,margin=12,rect=active?.getBoundingClientRect(),width=Math.min(380,innerWidth-margin*2);box.style.width=`${width}px`;const h=box.offsetHeight;let x=(innerWidth-width)/2,y=margin;if(rect){const right=innerWidth-rect.right-gap-width,left=rect.left-gap-width;if(innerWidth>720&&right>=margin)x=rect.right+gap;else if(innerWidth>720&&left>=margin)x=left;else if(innerHeight-rect.bottom>h+gap)y=rect.bottom+gap;else if(rect.top>h+gap)y=rect.top-h-gap;else y=(innerHeight-h)/2;}box.style.left=`${Math.max(margin,Math.min(x,innerWidth-width-margin))}px`;box.style.top=`${Math.max(margin,Math.min(y,innerHeight-h-margin))}px`;}
  function draw(){
    clearHighlight();const item=steps[step];lastFlash=save()?.flash||null;
    if(!card){card=document.createElement('div');card.id='walkthrough';document.body.appendChild(card);}
    card.innerHTML=`<section class="walkthrough-card" role="dialog" aria-labelledby="walkthrough-title"><div class="walkthrough-count">YOUR FIRST CAMPAIGN · ${step+1}/${steps.length}</div><h2 id="walkthrough-title">${item.title}</h2><p>${item.text}</p><p class="walkthrough-instruction">Follow the glowing highlight; this panel won’t block the game.</p><div class="walkthrough-actions"><button type="button" data-walk="back" ${step===0?'disabled':''}>Back</button><button type="button" data-walk="close">Exit</button><button type="button" data-walk="skip">Skip</button></div></section>`;
    $('[data-walk="back"]',card).onclick=()=>{if(step){step--;draw();}};
    $('[data-walk="close"]',card).onclick=close;
    $('[data-walk="skip"]',card).onclick=next;
    active=visible(item.selector);
    if(active){active.classList.add('tutorial-highlight');active.scrollIntoView({block:'nearest',inline:'nearest',behavior:'smooth'});}
    requestAnimationFrame(place);
    clearInterval(timer);timer=setInterval(()=>{if(card&&steps[step].done())next();},250);
  }
  function next(){if(!card)return;if(step<steps.length-1){step++;draw();}else close();}
  function start(){if(card)close();mapSelections=0;step=save()?1:0;draw();}
  window.addEventListener('sos:county-selected',()=>{mapSelections++;});
  window.addEventListener('resize',place);window.addEventListener('scroll',place,true);
  // The original guide creates these buttons first; replace their handler with this guided flow.
  function wire(){const open=$('#tutorial-open');if(open&&open.dataset.walkBound!=='true'){open.dataset.walkBound='true';open.onclick=start;}
    const setup=$('#tutorial-start');if(setup&&setup.dataset.walkBound!=='true'){setup.dataset.walkBound='true';setup.onclick=start;}}
  const observer=new MutationObserver(wire);observer.observe(document.documentElement,{childList:true,subtree:true});wire();
})();
