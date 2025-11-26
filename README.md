# Askrun AI — Premium Assistant UI

This project is a local/hosted assistant named *ASKRUN* — a Jarvis-inspired, emotionally aware, helpful personal assistant. The repo includes a Flask backend (`app.py`) and a modern, responsive frontend (templates + static files).

## What I changed (overview)
- Reworked the frontend to a premium glassmorphism UI (mobile-friendly, animated avatar).
  - `templates/index.html` — main UI template (integrates with backend)
  - `static/css/style.css` — premium layout + animations
  - `static/js/script.js` — client-side logic: frames, TTS, mic, avatar sync, assistant UX
- Improved assistant personality & prompts in `askrun_gpt4all.py` to be Jarvis-like: calm, confident, emotive, helpful, and step-focused.
- Kept backend endpoints: `/` (UI), `/ask` (POST), `/frames_list` and `/frames/<file>` for avatars.

## How to run locally (Windows PowerShell)
1. Activate your virtualenv (recommended):
```powershell
cd 'C:\Users\HP\Downloads\Askrun AI'
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. Install the Python dependencies:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```
3. Start the server (dev):
```powershell
python -u app.py
```
4. Open the UI in a browser:
```
http://127.0.0.1:5000
```

## Running on Render (production)
- Ensure `requirements.txt` includes `gunicorn`.
- Render Start Command: `gunicorn app:app` (already configured in this repo).
- Notes: GPT4All models may require native libraries; check logs and use CPU-only wheels if necessary.

## Frontend files and how they connect
- `templates/index.html` — referenced static files and defines layout
- `static/css/style.css` — the responsive, glass-morphism CSS design
- `static/js/script.js` — main client code that:
  - loads frame PNGs from `/frames_list`
  - animates the avatar while playing speech
  - posts messages to `/ask`
  - uses Web Speech API for TTS and microphone (browser-dependent)

## Making the assistant perform local/system tasks (safe approach)
To perform system-level tasks you must always ask explicit user permission. Here are safe, real-world options:
- Provide a small Electron wrapper that lets ASKRUN run local scripts (file reads, searches) after the user grants permission.
- Provide downloadable helper scripts (PowerShell or Python) that the user runs locally to allow ASKRUN to access certain folders.
- Always make safety clear — do not execute arbitrary commands remotely.

If you want, I can scaffold a minimal Electron wrapper or safe helper scripts to allow file access and local searches when run on your machine.

## Next suggestions & improvements (optional)
- Add a `README` snippet describing how to configure a remote LLM or OpenAI API key when local GPT4All is not available.
- Add a "voice profile" selection UI for different speaking styles.
- Add conversation history saving (local storage or server DB) and session replay.

---
If you want I can now:
- Add a `.gitignore` to keep `.venv` and `__pycache__` out of your git repo.
- Scaffold an Electron helper to allow safe local file access.
- Improve the assistant's prompt further to prefer short/long answers based on user preference.

Tell me which one you prefer and I’ll implement it next.
