from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
import requests
from gtts import gTTS
import uuid
import base64
import io
import os
import time

app = Flask(__name__, template_folder="templates")

# -------------------------------
# PATHS
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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


    res = requests.get(TRANSLATE_API, params=params, timeout=20)
    result = res.json()
    translated_text = "".join([item[0] for item in result[0]])

    return jsonify({"translated_text": translated_text})


# -------------------------------
# CHATBOT (no key needed from the visitor)
# 1) OPENROUTER_API_KEY env var (optional, set by the site owner) -> OpenRouter
# 2) otherwise a free keyless public text API
# -------------------------------
SYSTEM_PROMPT = ("You are Wander Hub AI, a friendly travel assistant for a Pakistan-focused travel platform. "
                 "Give short, practical answers (under 120 words) about destinations, itineraries, budgets, "
                 "seasons, transport, food and local tips. If unsure, say so.")

def ask_ai(user_text):
    user_text = (user_text or "").strip()[:1500]
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                         "X-Title": "Wander Hub AI"},
                json={"model": os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
                      "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                   {"role": "user", "content": user_text}]},
                timeout=25)
            txt = r.json()["choices"][0]["message"]["content"].strip()
            if txt:
                return txt, "openrouter"
        except Exception as e:
            print("openrouter failed:", e)
    # keyless public endpoint (tried up to 3 times - the free service is sometimes busy)
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_text}]
    deadline = time.time() + 8.5
    for attempt in range(3):
        for model in ("openai", "openai-fast", "mistral"):
            if time.time() > deadline:
                break
            try:
                r = requests.post("https://text.pollinations.ai/openai",
                                  json={"model": model, "messages": msgs}, timeout=max(2, min(7, deadline - time.time())))
                txt = r.json()["choices"][0]["message"]["content"].strip()
                if txt:
                    return txt, "pollinations"
            except Exception as e:
                print("pollinations", model, "failed:", e)
        if time.time() > deadline:
            break
        try:
            r = requests.get("https://text.pollinations.ai/" + requests.utils.quote(user_text),
                             params={"system": SYSTEM_PROMPT}, timeout=max(2, min(7, deadline - time.time())))
            if r.status_code == 200 and r.text.strip():
                return r.text.strip(), "pollinations-get"
        except Exception as e:
            print("pollinations get failed:", e)
    return None, "none"

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        text = (request.get_json(silent=True) or {}).get("message", "")
    else:
        text = request.args.get("q", "")
    if not text.strip():
        return jsonify({"error": "Empty message"}), 400
    reply, source = ask_ai(text)
    if not reply:
        return jsonify({"reply": None, "source": source}), 200
    return jsonify({"reply": reply, "source": source})

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

    buf = io.BytesIO()
    gTTS(text=text, lang=lang).write_to_fp(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return jsonify({"audio_url": "data:audio/mpeg;base64," + b64})

# -------------------------------
# SERVE SAVED AUDIO FILES
# -------------------------------
@app.route("/tts_audio/<filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename, mimetype="audio/mpeg")

# -------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)

