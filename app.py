from flask import Flask, render_template, request, jsonify, send_from_directory
import importlib
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json() or {}
    message = data.get('message') or data.get('text') or ''
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    # Lazily import the askrun module to avoid loading the model on startup
    try:
        askrun = importlib.import_module('askrun_gpt4all')
    except Exception as e:
        return jsonify({'error': f'Failed to import model module: {e}'}), 500

    # Call the ask helper without TTS
    try:
        response = askrun.ask(message, use_tts=False)
    except Exception as e:
        return jsonify({'error': f'Error while generating response: {e}'}), 500
    return jsonify({'response': response})


@app.route('/frames/<path:filename>')
def frames_file(filename):
    # Serve image frames from the frames folder
    frames_dir = os.path.join(app.root_path, 'frames')
    return send_from_directory(frames_dir, filename)


@app.route('/frames_list')
def frames_list():
    frames_dir = os.path.join(app.root_path, 'frames')
    try:
        files = sorted([f for f in os.listdir(frames_dir) if f.lower().endswith('.png')])
    except Exception:
        files = []
    return jsonify({'frames': files})

if __name__ == "__main__":
    app.run(debug=True)
