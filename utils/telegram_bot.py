import os
import requests
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경변수 로드

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(caption, image_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as photo:
        payload = {
            "chat_id": CHAT_ID,
            "caption": caption
        }
        files = {"photo": photo}
        response = requests.post(url, data=payload, files=files)
        return response.status_code == 200
