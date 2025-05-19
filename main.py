import time
import threading
import requests
from flask import Flask
from instagrapi import Client

# Flask app
app = Flask(__name__)

@app.route("/")
def health():
    return {"status": "Listener is running"}, 200

# مقادیر ثابت کوکی
SESSIONID = "5813075928%3ArncCPvoeRflkXL63A4lK%3A3AiAYcHk"
DS_USER_ID = "5813075928"
CSRFTOKEN = "NmIGD2ArXvRCKk48DdRg8"
WEBHOOK_URL = "https://install.liara.run/webhook"

# ورود به اینستاگرام
cl = Client()
cl.set_settings({})
cl.login_by_sessionid(SESSIONID)
print("[*] Listener started...")

last_checked = time.time()

def check_messages():
    global last_checked
    threads = cl.direct_threads(amount=20)
    for thread in threads:
        for msg in thread.messages:
            if msg.timestamp.timestamp() > last_checked:
                if msg.user_id != cl.user_id and msg.text:
                    payload = {
                        "user_id": str(msg.user_id),
                        "message": msg.text
                    }
                    try:
                        r = requests.post(WEBHOOK_URL, json=payload)
                        print(f"[+] Sent to webhook {payload} | Status: {r.status_code}")
                    except Exception as e:
                        print(f"[!] Webhook error: {e}")
    last_checked = time.time()

def loop():
    while True:
        check_messages()
        time.sleep(10)

# اجرای هم‌زمان سرور و لیستنر
from threading import Thread
Thread(target=loop).start()
app.run(host="0.0.0.0", port=5000)