import time
import os
import requests
from instagrapi import Client

# کوکی‌ها از .env خوانده می‌شوند
SESSIONID = os.getenv("IG_SESSIONID")
DS_USER_ID = os.getenv("IG_DS_USER_ID")
CSRFTOKEN = os.getenv("IG_CSRFTOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://install.liara.run/webhook")

cl = Client()
cl.set_settings({})  # اختیاری برای پاک کردن کش
cl.login_by_sessionid(SESSIONID, DS_USER_ID, CSRFTOKEN)

print("[*] Listener started...")

last_checked = time.time()

while True:
    inbox = cl.direct_threads(amount=10)
    for thread in inbox:
        for msg in thread.messages:
            if msg.timestamp.timestamp() > last_checked:
                if msg.user_id != cl.user_id and msg.text:
                    payload = {
                        "user_id": str(msg.user_id),
                        "message": msg.text
                    }
                    try:
                        r = requests.post(WEBHOOK_URL, json=payload)
                        print(f"[+] Sent to webhook: {payload} | Status: {r.status_code}")
                    except Exception as e:
                        print(f"[!] Webhook error: {e}")
    last_checked = time.time()
    time.sleep(10)