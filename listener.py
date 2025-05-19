import time
import os
import requests
from instagrapi import Client
from flask import Flask

# تنظیمات Flask برای لیارا
app = Flask(__name__)

@app.route('/')
def health():
    return "Listener is running", 200

# بارگذاری کوکی‌ها از محیط
SESSIONID = os.getenv("IG_SESSIONID")
DS_USER_ID = os.getenv("IG_DS_USER_ID")
CSRFTOKEN = os.getenv("IG_CSRFTOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://install.liara.run/webhook")

cl = Client()
cl.set_settings({})
cl.login_by_sessionid(SESSIONID)

print("[+] Listener started...")

last_checked = time.time()

def check_messages():
    global last_checked
    threads = cl.direct_threads(amount=10)
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

# اجرای دائم با sleep
def loop():
    while True:
        check_messages()
        time.sleep(10)

# اجرای همزمان Flask و حلقه لیستنر
if __name__ == '__main__':
    from threading import Thread
    Thread(target=loop).start()
    app.run(host='0.0.0.0', port=5000)