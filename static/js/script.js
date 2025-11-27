// ASKRUN client script — premium UX + voice + mic + waveform visualizer
// Integrates with backend endpoint: /ask (frontend no longer animates frames)

const chatArea = document.querySelector('.chat-area');
const inputEl = document.querySelector('#user-input');
const sendBtn = document.querySelector('#send-btn');
const micBtn = document.querySelector('#mic-btn');
const micIcon = document.querySelector('#mic-icon');
const avatarImg = document.querySelector('#avatar');
const statusEl = document.querySelector('#status');

let animInterval = null; let animIndex = 0;
// waveform indicator element (visual sound-line while ASKRUN speaks)
const waveformEl = document.createElement('div'); waveformEl.id = 'waveform';
for (let i=0;i<10;i++){ const b=document.createElement('span'); b.className='wf-bar'; waveformEl.appendChild(b); }
let voices = [];

function pushMessage(kind, text, meta) {
  const row = document.createElement('div');
  row.className = 'msg ' + (kind === 'you' ? 'you': 'askrun');
  const bubble = document.createElement('div');
  bubble.className = 'bubble ' + (kind === 'you' ? 'you' : 'askrun');
  if (meta) {
    const metaEl = document.createElement('div'); metaEl.className = 'meta'; metaEl.innerText = meta; bubble.appendChild(metaEl);
  }
  bubble.appendChild(document.createTextNode(text));
  row.appendChild(bubble);
  chatArea.appendChild(row);
  chatArea.scrollTop = chatArea.scrollHeight - chatArea.clientHeight + 40;
}

function setStatus(text){ if(statusEl) statusEl.innerText = text; }

// removed: no frames loading; avatar uses a static image and waveform is used for speech activity

function startWaveform(){
  const wf = document.getElementById('waveform');
  if(wf) wf.classList.add('speaking');
}
function stopWaveform(){
  const wf = document.getElementById('waveform');
  if(wf) wf.classList.remove('speaking');
}

// Speech & TTS
function loadVoices(){ voices = window.speechSynthesis.getVoices() || []; }
window.speechSynthesis.onvoiceschanged = loadVoices; loadVoices();

function pickVoice(){ if(!voices.length) return null; const preference=['zira','samantha','amy','kendra','aria','female','google'];
  for(const p of preference){ const v = voices.find(x=>x.name && x.name.toLowerCase().includes(p)); if(v) return v; }
  return voices.find(v=>v.lang && v.lang.startsWith('en')) || voices[0];
}

// speak returns a Promise that resolves when speaking finishes (or immediately if no TTS available)
function speak(text){
  return new Promise((resolve)=>{
    if(!('speechSynthesis' in window)) return resolve(false);
    const utter = new SpeechSynthesisUtterance(text);
    const v = pickVoice(); if(v) utter.voice = v;
    utter.rate = 1;
    utter.pitch = 1;
    utter.onstart = ()=> { startWaveform(); playChime(); }; // animate waveform while speaking
    utter.onend = ()=> { stopWaveform(); resolve(true); };
    utter.onerror = ()=> { stopWaveform(); resolve(false); };
    try{
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utter);
    } catch(e){ console.warn('TTS failed', e); resolve(false); }
  });
}

// Microphone (SpeechRecognition) with permission flow
let recognition = null; let recognizing = false;
function setupMic(){ const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition; if(!SpeechRecognition){ micBtn.disabled=true; setStatus('Microphone: not supported in this browser'); return; }
  // request permission once
  if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){ navigator.mediaDevices.getUserMedia({audio:true}).then(stream=>{ stream.getTracks().forEach(t=>t.stop()); recognition = new SpeechRecognition(); recognition.lang='en-US'; recognition.interimResults=false; recognition.maxAlternatives=1; recognition.onstart=()=>{recognizing=true; micIcon.textContent='🔴'; setStatus('Listening...');}; recognition.onend=()=>{recognizing=false; micIcon.textContent='🎤'; setStatus('');}; recognition.onerror=(ev)=>{ recognizing=false; micIcon.textContent='🎤'; setStatus('Mic error: '+(ev.error||ev.message||'unknown')); console.error('rec error',ev); };
    recognition.onresult=(e)=>{ const t = e.results[0][0].transcript; inputEl.value = t; sendMessage(); };
    micBtn.addEventListener('click', ()=>{ try{ if(!recognizing) recognition.start(); else recognition.stop(); }catch(err){ console.error(err); setStatus('Microphone problem: '+err.message); } }); micBtn.disabled=false; micBtn.title='Speak';
  }).catch(err=>{ micBtn.disabled=true; setStatus('Mic disabled or not allowed. Enable mic access for localhost.'); console.warn('getUserMedia',err); }); }
  else { micBtn.disabled=true; setStatus('Microphone APIs missing in this browser.'); }
}

// Human-like assistant pre & post processing
function cleanupModelText(t){ // remove stray bracket/meta lines
  return t.split('\n').filter(l=>{ const s=l.trim(); if(!s) return false; if((s.startsWith('[')&&s.endsWith(']')) || (s.startsWith('(') && s.endsWith(')'))) return false; return true; }).join('\n'); }

// primary send function
let pending = false;
async function sendMessage(){
  if(pending) return; const msg = inputEl.value.trim(); if(!msg) return; pending=true; pushMessage('you', msg, new Date().toLocaleTimeString()); inputEl.value = ''; setStatus('Sending…');
  try{
    // Add light pre-processing to make the assistant more helpful — we include a small user-intent hint
    // show 'thinking' state (do NOT animate frames yet) while the model is generating
    setStatus('Thinking...');
    avatarImg && avatarImg.classList.add('thinking');
    const response = await fetch('/ask', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message: msg}) });
    const data = await response.json();
    let text = data.response || (data.error ? ('Error: '+data.error) : 'No response');
    // model returned — clear thinking indicator
    avatarImg && avatarImg.classList.remove('thinking');
    setStatus('');
    text = cleanupModelText(text);
    // speed & personality post-processing: ensure short voice-friendly intro
    pushMessage('askrun', text, 'ASKRUN • ' + new Date().toLocaleTimeString());
    // speak and await TTS so avatar will animate only during speech
    const hadSpeech = await speak(text);
    if (!hadSpeech) {
      // if TTS isn't available, show waveform animation for an estimated duration
      const wpm = 160; const words = text.split(/\s+/).filter(Boolean).length;
      const estMs = Math.min(12000, Math.max(800, Math.round(words / wpm * 60 * 1000)));
      startWaveform(); await new Promise(r => setTimeout(r, estMs)); stopWaveform();
    }
  }catch(err){ console.error('send failed',err); pushMessage('askrun','There was a problem contacting the assistant. Try again.'); stopWaveform(); }
  finally{ pending=false; setStatus(''); }
}

// keyboard
inputEl.addEventListener('keypress', (e)=>{ if(e.key === 'Enter') sendMessage(); }); sendBtn.addEventListener('click', sendMessage);

// Init
(function(){ /* attach waveform to avatar area */
  const avatarEl = document.querySelector('.avatar');
  if(avatarEl && !document.getElementById('waveform')) avatarEl.appendChild(waveformEl);
  setupMic();
})();

// tiny chime using WebAudio to give feedback when assistant begins speaking
function playChime(){
  try{
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const o = ctx.createOscillator(); const g = ctx.createGain();
    o.type = 'sine'; o.frequency.value = 880; g.gain.value = 0.06;
    o.connect(g); g.connect(ctx.destination);
    o.start();
    setTimeout(()=>{ o.frequency.value = 520; g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.18); o.stop(ctx.currentTime + 0.18); ctx.close().catch(()=>{}); }, 80);
  }catch(e){/* ignore audio errors */}
}
