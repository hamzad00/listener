import os
import re
import time
import threading
import requests
from flask import Flask
from instagrapi import Client

app = Flask(__name__)

@app.route("/")
def health():
    return {"status": "Listener is running"}, 200

# گرفتن متغیرهای محیطی
SESSIONID = os.getenv("IG_SESSIONID")
DS_USER_ID = os.getenv("IG_USERID")
CSRFTOKEN = os.getenv("IG_CSRFTOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://install.liara.run/webhook")

# بررسی معتبر بودن SESSIONID
match = re.search(r"\d+", SESSIONID or "")
if match:
    user_id = match.group()
else:
    print("SESSIONID format is invalid.")
    exit(1)

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

# شروع بررسی پیام‌ها
def loop():
    while True:
        check_messages()
        time.sleep(10)

# اجرای Thread مستقل برای پیام‌ها
threading.Thread(target=loop).start()

# اجرای Flask روی 0.0.0.0:5000
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)