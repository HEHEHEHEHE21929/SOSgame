/* Playability bridge: reliable MP recruiting, campaign reports, advisor coaching and target scope. */
(() => {
  'use strict';
  const SAVE_KEY='magyar-politika-save';
  const SCOPE_KEY='magyar-politika-campaign-scope';
  const RESUME_KEY='magyar-politika-resume-tab';
  const $=(selector,root=document)=>root.querySelector(selector);
  const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  let requestBusy=false;
  let meta=null;

  function loadState(){try{return JSON.parse(localStorage.getItem(SAVE_KEY)||'null');}catch(_){return null;}}
  function countyIndex(){
    const text=$('#info')?.textContent?.trim()||'';
    if(!meta)return null;
    const match=meta.counties.findIndex(([name])=>text.startsWith(name));
    return match<0?null:match;
  }
  async function perform(op,data,button,{reload=false}={}){
    if(requestBusy)return;
    const state=loadState();if(!state){alert('Start or load a campaign first.');return;}
    requestBusy=true;if(button){button.disabled=true;button.classList.add('is-working');}
    try{
      const response=await fetch(`/api/${op}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...data,state})});
      const next=await response.json();if(!response.ok)throw new Error(next.error||'That action did not work.');
      localStorage.setItem(SAVE_KEY,JSON.stringify(next));
      if(reload){sessionStorage.setItem(RESUME_KEY,'Campaign');window.location.reload();return;}
      // Let the existing game renderer consume the updated state without a page reload.
      window.dispatchEvent(new CustomEvent('magyar:state-updated',{detail:{state:next,action:op}}));
      requestBusy=false;if(button){button.disabled=false;button.classList.remove('is-working');}
    }catch(error){alert(error.message);requestBusy=false;if(button){button.disabled=false;button.classList.remove('is-working');}}
  }
  function bindCandidateForm(){
    const form=$('#mp-form');if(!form||form.dataset.playabilityBound)return;
    form.dataset.playabilityBound='true';
    const submit=event=>{
      event.preventDefault();event.stopImmediatePropagation();
      const select=$('select[name="historic-mp"]',form),input=$('#mp-name',form);
      const name=(select?.value||input?.value||'').trim();
      if(!name){select?.focus();alert('Choose a public figure from the candidate list.');return;}
      const county=countyIndex();
      if(county===null){alert('Click a county on the map first, then recruit its local candidate.');return;}
      perform('appoint',{county,name},form.querySelector('button'),{reload:true});
    };
    form.addEventListener('submit',submit,true);
    form.addEventListener('click',event=>{
      const button=event.target.closest('button');if(!button)return;
      event.preventDefault();event.stopImmediatePropagation();submit(event);
    },true);
  }
  const actionHelp={
    posters:'Put campaign posters across the selected county. Choose Nationwide to reach the whole country.',
    tv:'Run a television-ad flight. Expensive, but one of the strongest ways to lift national awareness.',
    social:'Publish a digital campaign. Its reach improves in the modern era.',
    rally:'Hold a public rally in the selected county to energize local supporters.',
    vol:'Organize a volunteer canvass. Volunteers build durable local support.',
    reg:'Register candidates for the next election; this avoids the unregistered-ballot penalty.',
    poll:'Commission accurate polling for six months; it reduces uncertainty in the displayed poll.'
  };
  function addActionDescriptions(){
    document.querySelectorAll('[data-campaign]').forEach(button=>{
      const action=button.dataset.campaign,help=actionHelp[action];if(!help)return;
      button.title=help;button.setAttribute('aria-label',`${button.textContent.trim()}. ${help}`);
      if(!button.parentElement?.querySelector(`[data-action-help="${action}"]`)){
        const note=document.createElement('span');note.className='action-help';note.dataset.actionHelp=action;note.textContent=help;button.insertAdjacentElement('afterend',note);
      }
    });
  }
  function bindCampaignActions(){
    // Capture only when Nationwide is explicitly selected. Normal county campaigns use game.js's
    // existing state/render path and therefore do not reload the page or lose the Campaign tab.
    document.addEventListener('click',event=>{
      const button=event.target.closest('[data-campaign]');if(!button)return;
      if(localStorage.getItem(SCOPE_KEY)!=='nationwide')return;
      event.preventDefault();event.stopImmediatePropagation();
      const action=button.dataset.campaign;
      perform('campaign',{action},button,{reload:true});
    },true);
  }
  function addTargetControl(){
    const form=$('#mp-form');if(!form)return;
    let control=$('#campaign-target-scope');
    if(!control){
      control=document.createElement('label');control.id='campaign-target-scope';control.className='campaign-target-scope';
      control.innerHTML='<input type="checkbox"><span><b>Nationwide campaign</b><small>Apply this action across all counties instead of only the selected county.</small></span>';
      form.insertAdjacentElement('beforebegin',control);
      control.querySelector('input').addEventListener('change',event=>localStorage.setItem(SCOPE_KEY,event.target.checked?'nationwide':'county'));
    }
    const checkbox=control.querySelector('input');if(checkbox)checkbox.checked=localStorage.getItem(SCOPE_KEY)==='nationwide';
  }
  function advisorCoach(){
    const select=$('#mentor-select');if(!select)return;
    const mentor=meta?.mentors?.[select.value];if(!mentor)return;
    const holder=select.closest('label')||select.parentElement;if(!holder)return;
    let card=$('.advisor-coach',holder.parentElement||holder);
    if(!card){card=document.createElement('section');card.className='advisor-coach';holder.insertAdjacentElement('afterend',card);}
    const bonuses=Object.entries(mentor.bonus||{}).map(([key,value])=>{
      const labels={anti:'Anti-corruption policy',vol:'Volunteer drives',tv:'TV and social media',cap:'Monthly political capital'};
      const percent=Math.round(Number(value)*100);
      return `<li><b>${escapeHtml(labels[key]||key)}:</b> ${percent>0?'+':''}${percent}% effectiveness</li>`;
    }).join('');
    const facts=(mentor.facts||[]).slice(0,3).map(fact=>`<li>${escapeHtml(fact)}</li>`).join('');
    const advice=select.value==='antall'?'Build a broad coalition and protect your political capital.':select.value==='horn'?'Use media strategically; make sure your budget can sustain promises.':select.value==='orban'?'Pair volunteer organizing with a strong county ground game.':'Pair anti-corruption policy with volunteer organizing; track the costs.';
    const html=`<h4>Advisor briefing · ${escapeHtml(mentor.n)}</h4><p>${escapeHtml(mentor.learn||advice)}</p><p><b>Practical tip:</b> ${escapeHtml(advice)}</p>${bonuses?`<ul class="advisor-bonuses">${bonuses}</ul>`:''}${facts?`<details><summary>Historical context</summary><ul>${facts}</ul></details>`:''}`;
    if(card.dataset.rendered!==html){card.innerHTML=html;card.dataset.rendered=html;}
    select.onchange=()=>{
      const current=loadState();if(!current)return;
      fetch('/api/mentor',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mentor:select.value,state:current})})
        .then(async response=>{const next=await response.json();if(!response.ok)throw new Error(next.error||'Could not select advisor.');localStorage.setItem(SAVE_KEY,JSON.stringify(next));window.location.reload();})
        .catch(error=>alert(error.message));
    };
  }
  function addCampaignReport(){
    const panel=$('#panel');if(!panel)return;
    const flash=loadState()?.flash;if(!flash||!/(campaign|rally|volunteer|posters|ads|polling|candidates registered)/i.test(flash))return;
    let report=$('.campaign-report',panel);if(!report){report=document.createElement('div');report.className='campaign-report';panel.prepend(report);}
    const html=`<span class="report-icon" aria-hidden="true">✦</span><span><b>Field report</b><br>${escapeHtml(flash)}</span>`;
    if(report.dataset.rendered!==html){report.innerHTML=html;report.dataset.rendered=html;}
  }
  function restoreCampaignTab(){
    if(sessionStorage.getItem(RESUME_KEY)!=='Campaign')return;
    const button=[...document.querySelectorAll('#top button')].find(item=>item.textContent.trim()==='Campaign');
    if(button){sessionStorage.removeItem(RESUME_KEY);button.click();}
  }
  function refresh(){bindCandidateForm();addActionDescriptions();addTargetControl();advisorCoach();addCampaignReport();restoreCampaignTab();}
  fetch('/api/meta').then(response=>response.json()).then(data=>{meta=data;refresh();}).catch(error=>console.error('Could not load playability metadata:',error));
  new MutationObserver(refresh).observe(document.documentElement,{childList:true,subtree:true});
  bindCampaignActions();
})();
