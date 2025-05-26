import os
import requests
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경변수 로드

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

import requests

def send_telegram_result(name, phone, summary_text, image_url):

    message = f"""📬 *분석 결과 도착!*

👤 이름: {name}
📱 전화번호: {phone}

💬 *요약 분석 결과:*
{summary_text}

🔗 이미지 보기: [여기]({image_url})
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }

    response = requests.post(url, data=payload)
    print("Telegram 응답:", response.status_code, response.text)


