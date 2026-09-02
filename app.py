from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import uuid
import re
from gtts import gTTS

app = Flask(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def clamp(value, low, high):
    return max(low, min(high, value))


def clean_text(text):
    text = re.sub(r'<\s*break[^>]*>', ' ', text, flags=re.I)
    text = re.sub(r'</?[^>]+>', ' ', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def add_natural_punctuation(text, style):
    text = clean_text(text)
    text = re.sub(r'\.{4,}', '...', text)
    text = re.sub(r'([!?।]){2,}', r'\1', text)
    if style == "suspense":
        text = text.replace("।", "...")
    return text


def make_mp3(text, gender, style, filename):
    # gTTS provides reliable Hindi speech without the Edge/Bing WebSocket.
    # Gender is retained in the UI for compatibility; gTTS itself does not
    # expose separate Hindi male/female voices.
    tts = gTTS(text=text, lang="hi", slow=(style == "suspense"))
    tts.save(filename)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    original_text = (data.get("text") or "").strip()
    gender = data.get("gender", "female")
    style = data.get("style", "natural")
    voice_type = data.get("type", "normal")

    if not original_text:
        return jsonify({"ok": False, "error": "Pehle text paste karein."}), 400
    if len(original_text) > 12000:
        return jsonify({"ok": False, "error": "Abhi ek baar me 12,000 characters tak use karein."}), 400

    try:
        speed = float(data.get("speed", 0.94))
        speed = clamp(speed, 0.5, 2.0)
        tone = float(data.get("tone", 0))
        tone = clamp(tone, -35, 35)
        text = add_natural_punctuation(original_text, style)

        filename = "manjeet_natural_{}.mp3".format(uuid.uuid4().hex)
        path = os.path.join(OUTPUT_DIR, filename)
        make_mp3(text, gender, style, path)

        if not os.path.isfile(path):
            return jsonify({"ok": False, "error": "MP3 file create nahi hui."}), 500

        return jsonify({
            "ok": True,
            "url": "/output/" + filename,
            "filename": filename,
            "voice": "Google Hindi TTS",
            "style": style,
            "rate": "UI speed: {:.2f}x (gTTS engine speed fixed)".format(speed),
            "pitch": "UI tone: {} Hz (gTTS engine pitch fixed)".format(int(tone)),
            "notice": "Is cloud version me Edge/Bing ki jagah Google Hindi TTS use ho raha hai."
        })
    except Exception as e:
        return jsonify({"ok": False, "error": "TTS generate nahi hua: " + str(e)}), 500


@app.route("/output/<path:filename>")
def output_file(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(file_path):
        return "MP3 file nahi mili.", 404
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=False)


@app.route("/download/<path:filename>")
def download_file(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(file_path):
        return "MP3 file nahi mili.", 404
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
