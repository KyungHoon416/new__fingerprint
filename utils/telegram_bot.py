import os
import requests
from dotenv import load_dotenv
load_dotenv()

def send_telegram_result(text):
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }

    response = requests.post(url, data=payload)
    print("텔레그램 응답:", response.status_code, response.text)
