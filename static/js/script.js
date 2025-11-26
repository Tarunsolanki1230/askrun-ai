// ASKRUN client script — premium UX + voice + mic + avatar animation
// Designed to integrate with backend endpoints: /frames_list and /ask

const chatArea = document.querySelector('.chat-area');
const inputEl = document.querySelector('#user-input');
const sendBtn = document.querySelector('#send-btn');
const micBtn = document.querySelector('#mic-btn');
const micIcon = document.querySelector('#mic-icon');
const avatarImg = document.querySelector('#avatar');
const statusEl = document.querySelector('#status');

let frames = [];
let animInterval = null; let animIndex = 0;
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

async function loadFrames(){
  try{
    const res = await fetch('/frames_list');
    const data = await res.json();
    frames = data.frames || [];
    if(frames.length) avatarImg.src = '/frames/' + frames[0];
  }catch(e){ console.warn('Failed to load frames', e); }
}

function startAvatar(){ if(!frames.length) return; stopAvatar(); animIndex = 0; animInterval = setInterval(()=>{ avatarImg.src = '/frames/' + frames[animIndex % frames.length]; animIndex++; }, 75); }
function stopAvatar(){ if(animInterval){ clearInterval(animInterval); animInterval = null; } }

// Speech & TTS
function loadVoices(){ voices = window.speechSynthesis.getVoices() || []; }
window.speechSynthesis.onvoiceschanged = loadVoices; loadVoices();

function pickVoice(){ if(!voices.length) return null; const preference=['zira','samantha','amy','kendra','aria','female','google'];
  for(const p of preference){ const v = voices.find(x=>x.name && x.name.toLowerCase().includes(p)); if(v) return v; }
  return voices.find(v=>v.lang && v.lang.startsWith('en')) || voices[0];
}

function speak(text){ if(!('speechSynthesis' in window)) return; const utter = new SpeechSynthesisUtterance(text); const v = pickVoice(); if(v) utter.voice = v; utter.rate=1; utter.pitch=1; utter.onstart = ()=>startAvatar(); utter.onend=()=>stopAvatar(); utter.onerror=()=>stopAvatar(); window.speechSynthesis.cancel(); window.speechSynthesis.speak(utter); }

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
  if(pending) return; const msg = inputEl.value.trim(); if(!msg) return; pending=true; pushMessage('you', msg, new Date().toLocaleTimeString()); inputEl.value=''; setStatus('Sending…'); startAvatar();
  try{
    // Add light pre-processing to make the assistant more helpful — we include a small user-intent hint
    const response = await fetch('/ask', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message: msg}) });
    const data = await response.json();
    let text = data.response || (data.error ? ('Error: '+data.error) : 'No response');
    text = cleanupModelText(text);
    // speed & personality post-processing: ensure short voice-friendly intro
    pushMessage('askrun', text, 'ASKRUN • ' + new Date().toLocaleTimeString());
    speak(text);
  }catch(err){ console.error('send failed',err); pushMessage('askrun','There was a problem contacting the assistant. Try again.'); }
  finally{ pending=false; setStatus(''); stopAvatar(); }
}

// keyboard
inputEl.addEventListener('keypress', (e)=>{ if(e.key === 'Enter') sendMessage(); }); sendBtn.addEventListener('click', sendMessage);

// Init
(function(){ loadFrames(); setupMic(); })();
