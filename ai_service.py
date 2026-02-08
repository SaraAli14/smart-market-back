from flask import Flask, request, jsonify
from googletrans import Translator
import speech_recognition as sr
from pydub import AudioSegment
import os
import requests

app = Flask(__name__)
translator = Translator()

NODE_URL = "http://127.0.0.1:5000"   # سيرفر النود بتاعك

# ==========================
# اختبار إن السيرفر شغال
# ==========================
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ==========================
# البحث النصي
# ==========================
@app.route("/search")
def search_text():
    text = request.args.get("text", "")

    # نجيب كل المنتجات من node
    r = requests.get(NODE_URL + "/")
    products = r.json()

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


# ==========================
# استقبال صوت وتحويله لنص
# ==========================
@app.route("/speech", methods=["POST"])
def speech():

    file = request.files["file"]
    path = "temp.wav"
    file.save(path)

    # تحويل لأي فورمات مناسب
    sound = AudioSegment.from_file(path)
    sound.export("converted.wav", format="wav")

    recognizer = sr.Recognizer()

    with sr.AudioFile("converted.wav") as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language="ar-EG")
    except:
        try:
            text = recognizer.recognize_google(audio, language="en-US")
        except:
            return jsonify({"error": "مش قادر أفهم الصوت"})

    # بعد ما حولناه لنص → نعمل بحث
    r = requests.get(NODE_URL + "/")
    products = r.json()

    text_low = text.lower()

    for p in products:
        if text_low in p["name"]["en"].lower() or text_low in p["name"]["ar"].lower():
            return jsonify({
                "found": True,
                "text": text,
                "product": p,
                "reply_ar": f"المنتج {p['name']['ar']} متوفر في {p['location']['ar']} وسعره {p['price']} جنيه",
                "reply_en": f"{p['name']['en']} is available in {p['location']['en']} and costs {p['price']} pounds"
            })

    return jsonify({
        "found": False,
        "text": text
    })


if __name__ == "__main__":
    app.run(port=5001)

