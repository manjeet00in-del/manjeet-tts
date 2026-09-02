from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import uuid
import re
import subprocess
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


def prepare_text(text, style):
    text = clean_text(text)
    text = re.sub(r'\.{4,}', '...', text)
    text = re.sub(r'([!?।]){2,}', r'\1', text)
    if style == "suspense":
        text = text.replace("।", "...")
    elif style == "story":
        text = text.replace("।", "। ")
    return text


def render_audio(text, speed, pitch, slow_gtts, outfile):
    temp = os.path.join(OUTPUT_DIR, "tmp_" + uuid.uuid4().hex + ".mp3")
    try:
        gTTS(text=text, lang="hi", slow=slow_gtts).save(temp)

        # FFmpeg applies actual speed and pitch changes to the generated MP3.
        # Pitch is expressed as a multiplier around 1.0.
        filters = []
        if abs(speed - 1.0) > 0.01:
            # atempo supports 0.5-2.0, which matches our UI.
            filters.append("atempo={:.3f}".format(speed))
        if abs(pitch - 1.0) > 0.005:
            filters.append("asetrate=44100*{:.4f},aresample=44100".format(pitch))

        if filters:
            cmd = [
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", temp,
                "-filter:a", ",".join(filters),
                "-codec:a", "libmp3lame", "-q:a", "3",
                outfile
            ]
        else:
            shutil.copyfile(temp, outfile)

        if filters:
            subprocess.run(cmd, check=True, timeout=180)
    finally:
        try:
            os.remove(temp)
        except OSError:
            pass


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    original_text = (data.get("text") or "").strip()
    voice = data.get("voice", "aarav")
    style = data.get("style", "natural")

    if not original_text:
        return jsonify({"ok": False, "error": "Pehle text paste karein."}), 400
    if len(original_text) > 12000:
        return jsonify({"ok": False, "error": "Abhi ek baar me 12,000 characters tak use karein."}), 400

    presets = {
        "aarav":  {"name": "Aarav",  "speed": 0.98, "pitch": 0.90},
        "kabir":  {"name": "Kabir",  "speed": 0.92, "pitch": 0.86},
        "rohan":  {"name": "Rohan",  "speed": 1.04, "pitch": 0.94},
        "vikram": {"name": "Vikram", "speed": 0.88, "pitch": 0.82},
        "meera":  {"name": "Meera",  "speed": 1.00, "pitch": 1.10},
        "kavya":  {"name": "Kavya",  "speed": 0.96, "pitch": 1.06},
        "ananya": {"name": "Ananya", "speed": 1.05, "pitch": 1.14},
    }

    try:
        preset = presets.get(voice, presets["aarav"])
        speed = clamp(float(data.get("speed", preset["speed"])), 0.5, 2.0)
        pitch = clamp(float(data.get("pitch", preset["pitch"])), 0.75, 1.25)

        style_defaults = {
            "natural": (1.00, 1.00, False),
            "story": (0.94, 0.98, False),
            "suspense": (0.82, 0.92, True),
            "emotional": (0.88, 0.96, False),
            "fast": (1.18, 1.00, False),
        }
        sm, sp, slow_gtts = style_defaults.get(style, style_defaults["natural"])
        speed = clamp(speed * sm, 0.5, 2.0)
        pitch = clamp(pitch * sp, 0.75, 1.25)

        text = prepare_text(original_text, style)
        filename = "manjeet_{}_{}.mp3".format(preset["name"].lower(), uuid.uuid4().hex[:12])
        path = os.path.join(OUTPUT_DIR, filename)

        render_audio(text, speed, pitch, slow_gtts, path)

        if not os.path.isfile(path):
            return jsonify({"ok": False, "error": "MP3 file create nahi hui."}), 500

        return jsonify({
            "ok": True,
            "url": "/output/" + filename,
            "filename": filename,
            "voice": preset["name"],
            "style": style,
            "speed": round(speed, 2),
            "notice": "Voice preset gTTS Hindi + audio processing se banaya gaya hai."
        })
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "error": "Audio processing me zyada time lag gaya. Chhoti script try karein."}), 500
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
