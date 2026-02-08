from flask import Flask, request, jsonify
from googletrans import Translator
import speech_recognition as sr
from pydub import AudioSegment
import requests
import os

app = Flask(__name__)
translator = Translator()

NODE_URL = os.getenv("NODE_URL", "http://127.0.0.1:5000")

# ==== Health Check ====
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# ==== Text Search ====
@app.route("/search")
def search_text():
    text = request.args.get("text", "")
    try:
        r = requests.get(f"{NODE_URL}/")
        products = r.json()
    except:
        products = []

    text = text.lower()
    for p in products:
        name_en = p["name"]["en"].lower()
        name_ar = p["name"]["ar"].lower()
        if text in name_en or text in name_ar:
            return jsonify({
                "found": True,
                "product": p,
                "reply_ar": f"المنتج {p['name']['ar']} متوفر في {p['location']['ar']} وسعره {p['price']} جنيه",
                "reply_en": f"{p['name']['en']} is available in {p['location']['en']} and costs {p['price']} pounds"
            })
    return jsonify({"found": False})

# ==== Speech to Text ====
@app.route("/speech-to-text", methods=["POST"])
def speech():
    try:
        audio_b64 = request.json.get("audio")
        audio_path = "temp.wav"

        # حفظ الصوت
        with open(audio_path, "wb") as f:
            f.write(base64.b64decode(audio_b64))

        # تحويل لأي فورمات WAV
        sound = AudioSegment.from_file(audio_path)
        sound.export("converted.wav", format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile("converted.wav") as source:
            audio = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio, language="ar-EG")
        except:
            text = recognizer.recognize_google(audio, language="en-US")

        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)


