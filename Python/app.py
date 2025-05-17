import threading
from flask import Flask, jsonify
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app) 

data_list = [
    "🦊 Fox spotted!",
    "🐻 Bear detected!",
    "🐰 Rabbit nearby!",
    "🦁 Lion roaring!",
    "🐍 Snake warning!"
]

#bekleyen clientsler için liste
waiting_clients = []

#SHORT POLLİNG
@app.route("/short")
def short_poll():
    return jsonify({
        "message": random.choice(data_list)
    })

#LONG POLLİNG

@app.route("/long")
def long_poll():
    print("long polling isteği alındı")
    # Event ve veri saklayıcısı
    event = threading.Event()
    result = {}

    #30 SANİYELİK BEKLEME SÜRESİ
    #EVENT.WAİTİN SONSUZ BEKLEMESİ İYİ DEĞİLDİR.
    def wait_for_data():
        event.wait(timeout=30)
        if not result:
            result["message"] = "⏳ Zaman aşımı (veri tetiklenmedi)"
            try:
                waiting_clients.remove((event, result))  # ❗ Listeden çıkar
            except ValueError:
                pass
            event.set()
    threading.Thread(target=wait_for_data).start()

    waiting_clients.append((event, result))

    event.wait()

    return jsonify(result)

@app.route("/trigger", methods=["POST"])
def trigger_event():
    print(f"[TRIGGER] Bekleyen istemci sayısı: {len(waiting_clients)}")

    if waiting_clients:
        event, result = waiting_clients.pop(0)
        msg = f"🚨 Yeni veri geldi! (Hayvan: {random.choice(data_list)})"
        result["message"] = msg
        event.set()
        return jsonify({"message": msg})
    else:
        return jsonify({"message": "❌ Bekleyen istemci yok."})

if __name__ == "__main__":
    app.run(debug=True)
