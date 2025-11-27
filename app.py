from flask import Flask, render_template, request, jsonify, send_from_directory
import importlib
import os

app = Flask(__name__)


# Ensure model warmup starts once (some Flask versions lack before_first_request)
_warmup_started = False

@app.before_request
def background_model_warmup():
    global _warmup_started
    if _warmup_started:
        return
    _warmup_started = True
    def _warm():
        try:
            # import module lazily and try to load the model (safe to fail)
            m = importlib.import_module('askrun_gpt4all')
            ok, err = m.load_model()
            if ok:
                app.logger.info('ASKRUN model warmup successful.')
            else:
                app.logger.warning('ASKRUN model warmup failed: %s', err)
        except Exception as e:
            app.logger.exception('Warmup import/load failed: %s', e)

    import threading
    threading.Thread(target=_warm, daemon=True).start()

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

    # Call the ask helper without TTS and measure time to help debug latency
    try:
        import time
        start = time.time()
        response = askrun.ask(message, use_tts=False)
        duration = time.time() - start
        app.logger.info('Generated reply in %.2f sec for message length %d', duration, len(message))
    except Exception as e:
        app.logger.exception('Error generating response: %s', e)
        return jsonify({'error': f'Error while generating response: {e}'}), 500
    return jsonify({'response': response, 'duration_seconds': round(duration, 3)})


# the frames endpoints were removed (UI now uses waveform visualizer)

if __name__ == "__main__":
    app.run(debug=True)
