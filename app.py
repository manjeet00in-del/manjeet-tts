import os
import asyncio
from flask import Flask, render_template, request, send_file, jsonify
import edge_tts

app = Flask(__name__)

OUTPUT_FILE = "output.mp3"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_audio():
    try:
        data = request.json
        text = data.get('text', '')
        voice = data.get('voice', 'hi-IN-SwaraNeural')
        
        # Valid edge-tts voices fallback check
        if not voice or 'Neural' not in voice:
            voice = 'hi-IN-SwaraNeural'

        if not text:
            return jsonify({'error': 'Text is required'}), 400

        async def generate():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(OUTPUT_FILE)

        asyncio.run(generate())

        return send_file(OUTPUT_FILE, mimetype="audio/mp3", as_attachment=True, download_name="speech.mp3")
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)