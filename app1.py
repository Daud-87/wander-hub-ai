from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
import requests
from gtts import gTTS
import uuid
import os

app = Flask(__name__, template_folder="templates")

# -------------------------------
# PATHS
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "tts_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

TRANSLATE_API = "https://translate.googleapis.com/translate_a/single"

# -------------------------------
# SERVE MAIN PAGE
# -------------------------------
@app.route("/")
@app.route("/helper")
def helper_page():
    return render_template("translation-helper.html")

# -------------------------------
# TRANSLATION API
# -------------------------------
@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    text = data.get("text")
    source = data.get("source_lang")
    target = data.get("target_lang")

    if not text or not source or not target:
        return jsonify({"error": "Missing fields"}), 400

    params = {
        "client": "gtx",
        "sl": source,
        "tl": target,
        "dt": "t",
        "q": text
    }


    res = requests.get(TRANSLATE_API, params=params)
    result = res.json()
    translated_text = "".join([item[0] for item in result[0]])

    return jsonify({"translated_text": translated_text})

# -------------------------------
# TEXT TO SPEECH (SAVE + RETURN URL)
# -------------------------------
@app.route("/tts", methods=["POST"])
def tts():
    data = request.json
    text = data.get("text")
    lang = data.get("lang", "en")

    if not text:
        return jsonify({"error": "No text"}), 400

    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    gTTS(text=text, lang=lang).save(filepath)

    return jsonify({
        "audio_url": f"/tts_audio/{filename}"
    })

# -------------------------------
# SERVE SAVED AUDIO FILES
# -------------------------------
@app.route("/tts_audio/<filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename, mimetype="audio/mpeg")

# -------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)

