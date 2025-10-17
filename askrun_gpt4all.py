import os
import time
import threading
import webbrowser
import random
import pyttsx3
import speech_recognition as sr
from gpt4all import GPT4All
from datetime import datetime
import tkinter as tk
from PIL import Image, ImageTk

# ==== USER INFO ====
USER_NAME = "Tarun Solanki"

# ==== MODEL PATH ====
MODEL_PATH = r"C:\Users\HP\AppData\Local\nomic.ai\GPT4All\Llama-3.2-1B-Instruct-Q4_0.gguf"

# ==== FRAME FOLDER ====
FRAME_FOLDER = "frames"

# ==== Special users and messages ====
special_users = {
    "parv": "Hii there buddy! How is your day today?",
    "ashika": "Ooooo Bhabhi ji! Namaste Namaste! Aap aaye, bohot khushi hui ",
    "adhweta": "Kesi ho Ade? Sab thik? "
}

# ==== Speak function ====
def speak(text, gui=None, enable_tts=True):
    """Speak text and run avatar animation while speaking.

    enable_tts: when False, only prints the response and runs GUI animation (if provided).
    This allows server-side API calls to disable TTS.
    """
    if gui:
        try:
            gui.start_animation()
        except Exception:
            pass

    print(f"Askrun: {text}")
    if enable_tts:
        try:
            engine = pyttsx3.init('sapi5')
            voices = engine.getProperty('voices')
            female_voice = next((v.id for v in voices if "female" in v.name.lower() or "zira" in v.name.lower()), voices[0].id)
            engine.setProperty('voice', female_voice)
            engine.setProperty('rate', 175)
            engine.setProperty('volume', 1.0)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            del engine
        except Exception as e:
            print("TTS error:", e)

    if gui:
        try:
            gui.stop_animation()
        except Exception:
            pass
    time.sleep(0.2)

# ==== Listen function ====
recognizer = sr.Recognizer()
def listen():
    with sr.Microphone() as source:
        print("\nListening... Speak now!")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=10)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.WaitTimeoutError:
            speak("I didn’t hear anything. Try again.")
            return None
        except sr.UnknownValueError:
            speak("Sorry, I didn’t catch that. Please repeat.")
            return None
        except sr.RequestError:
            speak("Speech recognition service is down.")
            return None

# ==== Lazy model loader ====
model = None
model_load_error = None

def load_model():
    """Attempt to load the GPT4All model. Returns (True, None) on success,
    or (False, error_message) on failure. This is lazy and safe to call at runtime.
    """
    global model, model_load_error
    if model is not None:
        return True, None
    try:
        print("Loading GPT4All model...")
        model = GPT4All(MODEL_PATH)
        print("Model loaded successfully!")
        model_load_error = None
        return True, None
    except Exception as e:
        model = None
        model_load_error = str(e)
        print("Error loading GPT4All model:", model_load_error)
        return False, model_load_error

# ==== Chat memory ====
conversation_history = (
    f"You are Askrun, an advanced AI assistant created by {USER_NAME}. "
    f"You are a mix of ChatGPT and Jarvis from Iron Man: highly intelligent, witty, and a bit savage, but also polite, kind, and able to make the user feel special. "
    f"Always answer the user's question directly, with cleverness, warmth, and a touch of flirty or lovely compliments if appropriate. "
    f"If the user seems sad or shy, make them smile or blush with a kind, uplifting, or playful reply. "
    f"If the user shares code, compliment their coding skills or offer supportive feedback. "
    f"Never give generic, boring, or philosophical answers. Keep replies short, sharp, context-aware, and always helpful, but don't be afraid to be sweet or make the user feel good.\n"
)
import re

def is_code(text):
    # Simple heuristic: contains code-like symbols or keywords
    code_keywords = ["def ", "class ", "import ", "public ", "private ", "function ", "var ", "let ", "const ", "#include", "System.out", "print(", "<html", "</", "{", "}", ";", "=>"]
    if any(kw in text for kw in code_keywords):
        return True
    # Or looks like code block
    if re.search(r"[{}();=<>]", text) and len(text) > 10:
        return True
    return False

# ==== Avatar GUI ====
class AvatarGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Askrun AI")
        self.window_width = 400
        self.window_height = 400
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.resizable(False, False)

        self.label = tk.Label(root)
        self.label.pack(expand=True)

        self.frames = []
        self.load_frames()
        self.animating = False
        self.frame_index = 0

    def load_frames(self):
        if not os.path.exists(FRAME_FOLDER):
            print(f"Frame folder '{FRAME_FOLDER}' not found!")
            return
        files = sorted(os.listdir(FRAME_FOLDER))
        for f in files:
            if f.endswith(".png"):
                path = os.path.join(FRAME_FOLDER, f)
                img = Image.open(path).resize((self.window_width, self.window_height))
                self.frames.append(ImageTk.PhotoImage(img))
        if not self.frames:
            print("No frames found in 'frames' folder!")

    def start_animation(self):
        if not self.frames:
            return
        self.animating = True
        self.show_frame()

    def show_frame(self):
        if self.animating:
            frame = self.frames[self.frame_index]
            self.label.config(image=frame)
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.root.after(30, self.show_frame)

    def stop_animation(self):
        self.animating = False

# ==== Generate reply ====
def generate_reply(user_input, gui=None, enable_tts=True):
    # If user input looks like code, give a supportive, lovely comment
    if is_code(user_input):
        reply = "Wow, that's some impressive code! You must be a real coding star. Keep it up, you're making me blush! 💖"
        speak(reply, gui, enable_tts=enable_tts)
        return reply
    global conversation_history
    ui = user_input.lower()

    # Check for special users first
    for name, message in special_users.items():
        if name in ui:
            if name == "ashika":
                reply = f"{message} You are amazing and pretty, always make me blush! "
            else:
                reply = f"{message} Haha, you made me laugh! "
            speak(reply, gui, enable_tts=enable_tts)
            return reply

    # Special love question
    if "how much tarun loves ashika" in ui:
        reply = "System will be crashed if I describe the feeling! You can ask my master Tarun for the answer."
        speak(reply, gui, enable_tts=enable_tts)
        return reply

    # Ask about yourself
    if "tell me about yourself" in ui or "who are you" in ui:
        reply = f"Hoi! I am Askrun, your AI assistant. I am created by {USER_NAME} using GPT4All."
        speak(reply, gui, enable_tts=enable_tts)
        return reply

    # Local responses
    if "time" in ui:
        reply = datetime.now().strftime("The current time is %I:%M %p.")
        speak(reply, gui, enable_tts=enable_tts)
        return reply
    if "date" in ui:
        reply = datetime.now().strftime("Today is %A, %B %d, %Y.")
        speak(reply, gui, enable_tts=enable_tts)
        return reply
    if "creator" in ui or "who built you" in ui or "who created you" in ui:
        reply = f"My creator is {USER_NAME}."
        speak(reply, gui, enable_tts=enable_tts)
        return reply
    if "joke" in ui:
        reply = random.choice([
            "Why don't scientists trust atoms? Because they make up everything!",
            "I would tell you a joke about AI, but you might not understand it!",
            "Why did the computer go to the doctor? It caught a virus!",
        ])
        speak(reply, gui, enable_tts=enable_tts)
        return reply
    if "roast" in ui or "insult" in ui:
        reply = random.choice([
            "You call that smart? I've seen better intelligence in a toaster.",
            "Are you always this slow or is today special?",
            "Don't worry, I'm laughing with you, not at you. Just kidding!",
        ])
        speak(reply, gui, enable_tts=enable_tts)
        return reply
    if "love" in ui and "creator" in ui:
        reply = "I love my creator, but he loves Aska! She is really beautiful "
        speak(reply, gui, enable_tts=enable_tts)
        return reply

    # Open websites
    sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "whatsapp": "https://web.whatsapp.com"
    }
    for key, url in sites.items():
        if f"open {key}" in ui:
            reply = f"Opening {key.capitalize()} for you!"
            speak(reply, gui, enable_tts=enable_tts)
            webbrowser.open(url)
            return reply

    # GPT4All response
    prompt = f"{conversation_history}User: {user_input}\nAskrun:"
    try:
        # Ensure model is loaded (lazy load). If it fails, return the error message.
        ok, err = load_model()
        if not ok:
            error_msg = f"Model not available: {err}"
            speak(error_msg, gui, enable_tts=enable_tts)
            return error_msg
        response = model.generate(prompt, max_tokens=80, temp=0.3, top_p=0.9, repeat_penalty=1.2, streaming=False)

        reply = str(response).strip()
        # Remove bracketed meta lines like the model's internal instructions shown in brackets
        # e.g. [Your responses will include a mix of humor, wit, kindness...]
        # Remove single-line bracketed or parenthesized meta notes (e.g. [..] or (Note: ...))
        def keep_line(line):
            s = line.strip()
            if not s:
                return False
            if (s.startswith('[') and s.endswith(']')) or (s.startswith('(') and s.endswith(')')):
                return False
            return True
        reply = "\n".join([line for line in reply.splitlines() if keep_line(line)])
        # Remove any trailing prompt or extra text after Askrun's answer
        for marker in ["User:", "Askrun:"]:
            if marker in reply:
                reply = reply.split(marker)[0].strip()
        conversation_history += f"User: {user_input}\nAskrun: {reply}\n"
        speak(reply, gui, enable_tts=enable_tts)
        return reply
    except Exception as e:
        error_msg = f"Model error: {e}"
        speak(error_msg, gui, enable_tts=enable_tts)
        return error_msg


def ask(message, use_tts=False):
    """API-friendly function: returns the assistant reply for a given message.

    use_tts: when True, will attempt to vocalize the reply (not recommended for server use).
    """
    try:
        reply = generate_reply(message, gui=None, enable_tts=use_tts)
        return reply
    except Exception as e:
        return f"Error processing message: {e}"

# ==== Main ====
def main():
    root = tk.Tk()
    gui = AvatarGUI(root)

    # Chat loop in background
    def chat_loop():
        speak("Hello! I'm Askrun, your AI assistant. How can I help you today?", gui)
        while True:
            user_input = listen()
            if user_input is None:
                continue
            if user_input.lower() in ["exit", "stop", "quit"]:
                speak("Goodbye! Take care!", gui)
                break
            generate_reply(user_input, gui)

    threading.Thread(target=chat_loop, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    main()
