/* Adds fictional ethics choices, accessible walkthrough and sound control. */
(() => {
  'use strict';
  const SAVE_KEY = 'magyar-politika-save';
  const SOUND_KEY = 'magyar-politika-sounds';
  const $ = (selector, root = document) => root.querySelector(selector);
  let muted = localStorage.getItem(SOUND_KEY) === 'off';
  let audio;
  const safe = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

  function tone(frequency, duration = .09, type = 'sine', volume = .035, delay = 0) {
    if (muted) return;
    try {
      audio ||= new (window.AudioContext || window.webkitAudioContext)();
      if (audio.state === 'suspended') audio.resume();
      const oscillator = audio.createOscillator(), gain = audio.createGain();
      oscillator.type = type; oscillator.frequency.value = frequency;
      gain.gain.setValueAtTime(volume, audio.currentTime + delay);
      gain.gain.exponentialRampToValueAtTime(.001, audio.currentTime + delay + duration);
      oscillator.connect(gain); gain.connect(audio.destination);
      oscillator.start(audio.currentTime + delay); oscillator.stop(audio.currentTime + delay + duration);
    } catch (_) {}
  }
  function chime(kind = 'click') {
    const notes = kind === 'success' ? [523, 659, 784] : kind === 'emergency' ? [392, 330] : [440];
    notes.forEach((note, index) => tone(note, .12, 'sine', .025, index * .085));
  }
  const steps = [
    ['Welcome to your campaign', 'You lead a party in a simplified classroom simulation. Your goal is to build support, win seats, and make choices. This is not a forecast of real politics.'],
    ['Your dashboard', 'The top bar shows the date, funds and political capital. Use Pause or the speed buttons to control time. You can pause before making a decision.'],
    ['Map and campaign', 'Select a county on the map to inspect it. In Campaign, choose an action and decide whether to focus locally or nationwide. Every action has a cost.'],
    ['Elections and government', 'Register candidates before an election to avoid a ballot penalty. Polls are estimates; seat outcomes are simulated. Government status unlocks policies and fictional ethics scenarios.'],
    ['Events, emergencies and saving', 'Pause at event prompts and consider the trade-offs. Emergency situations are fictional scenarios focused on civic and humanitarian responses. The Game tab contains save/load options.']
  ];
  let step = 0;
  function openGuide() { step = 0; drawGuide(); chime('success'); }
  function drawGuide() {
    let layer = $('#friendly-guide');
    if (!layer) {
      layer = document.createElement('div'); layer.id = 'friendly-guide'; layer.className = 'guide-backdrop';
      layer.setAttribute('role', 'dialog'); layer.setAttribute('aria-modal', 'true'); layer.setAttribute('aria-label', 'Interactive game tutorial');
      document.body.appendChild(layer);
    }
    const [title, body] = steps[step];
    layer.innerHTML = `<section class="guide-card"><div class="guide-progress">Step ${step + 1} of ${steps.length}</div><h2>${safe(title)}</h2><p>${safe(body)}</p><div class="guide-actions"><button type="button" id="guide-exit">Exit tutorial</button><button type="button" id="guide-next">${step === steps.length - 1 ? 'Finish' : 'Next'}</button></div></section>`;
    $('#guide-exit', layer).onclick = () => layer.remove();
    $('#guide-next', layer).onclick = () => { if (step < steps.length - 1) { step++; drawGuide(); chime(); } else layer.remove(); };
    $('#guide-next', layer).focus();
    layer.onkeydown = event => { if (event.key === 'Escape') layer.remove(); };
  }
  function state() { try { return JSON.parse(localStorage.getItem(SAVE_KEY) || 'null'); } catch (_) { return null; } }
  function addControls() {
    const top = $('#top');
    if (top && !$('#easy-guide')) {
      const guide = document.createElement('button'); guide.id = 'easy-guide'; guide.type = 'button'; guide.textContent = 'How to play'; guide.onclick = openGuide; top.appendChild(guide);
    }
    if (top && !$('#sound-toggle')) {
      const sound = document.createElement('button'); sound.id = 'sound-toggle'; sound.className = 'sound-toggle'; sound.type = 'button';
      sound.setAttribute('aria-pressed', String(!muted));
      const label = () => { sound.textContent = muted ? 'Sound: off' : 'Sound: on'; sound.setAttribute('aria-pressed', String(!muted)); };
      label(); sound.onclick = () => { muted = !muted; localStorage.setItem(SOUND_KEY, muted ? 'off' : 'on'); label(); if (!muted) chime('success'); };
      top.appendChild(sound);
    }
    addActions();
  }
  async function doAction(operation, payload, button) {
    const current = state();
    if (!current) { alert('Start or load a campaign first.'); return; }
    button.disabled = true;
    try {
      const response = await fetch(`/api/expansion/${operation}`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({...payload, state:current}) });
      const next = await response.json();
      if (!response.ok) throw new Error(next.error || 'That choice could not be applied.');
      localStorage.setItem(SAVE_KEY, JSON.stringify(next));
      chime('success');
      window.location.reload();
    } catch (error) { alert(error.message); button.disabled = false; }
  }
  function addActions() {
    const panel = $('#panel');
    if (!panel || $('#fictional-actions', panel)) return;
    const current = state();
    const section = document.createElement('section'); section.id = 'fictional-actions'; section.className = 'extra-actions';
    const inGovernment = Boolean(current?.inpower);
    section.innerHTML = `<h3>Ethics &amp; public trust</h3><p>Optional fictional choices illustrate how misuse of office can bring short-term political gain and lasting damage to trust.</p><div class="ethics-warning"><b>Classroom simulation:</b> These are unethical choices, not recommendations. Actions use public funds and reduce the trust meter.</div><div class="action-card"><b>Government-only choices</b><p>${inGovernment ? 'Your party leads government. Choose carefully.' : 'Lead government to unlock these choices.'}</p><button type="button" data-fictional="holiday" ${inGovernment ? '' : 'disabled'}>Luxury holiday on public funds · 12 M Ft</button><button type="button" data-fictional="bias_media" ${inGovernment ? '' : 'disabled'}>Bias public media · 7 M Ft</button><button type="button" data-fictional="nepotism" ${inGovernment ? '' : 'disabled'}>Favor an ally · 9 M Ft</button><p><b>Public trust:</b> ${Math.round(current?.trust ?? 100)}/100 · <b>Ethics breaches:</b> ${current?.corruption ?? 0}</p></div>`;
    panel.appendChild(section);
    section.querySelectorAll('[data-fictional]').forEach(button => button.onclick = () => {
      if (confirm('This is an unethical fictional action that misuses public resources and lowers public trust. Continue?')) doAction('corrupt', {action:button.dataset.fictional}, button);
    });
  }
  document.addEventListener('click', event => {
    const button = event.target.closest('.topbar button, #panel button');
    if (button && !button.matches('#sound-toggle, #easy-guide')) chime();
  });
  const observer = new MutationObserver(addControls);
  observer.observe(document.documentElement, {childList:true, subtree:true});
  addControls();
})();
