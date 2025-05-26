import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_image_and_full_result(image_path, name, phone, thumb_analysis, index_analysis, image_url):
    # 1. 이미지 전송
    url_photo = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as photo:
        files = {"photo": photo}
        data = {
            "chat_id": CHAT_ID,
            "caption": f"🌳 [나의 나무 NFT 도착]\n이름: {name}\n전화번호: {phone}"
        }
        requests.post(url_photo, files=files, data=data)

    # 2. 분석 결과 전송 (엄지 + 검지 전체 텍스트)
    url_msg = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    message = f"""📬 *지문 기반 심층 분석 결과*

👤 이름: {name}  
📱 전화번호: {phone}  

🧠 *엄지 분석 (자기 내면, 감정 기반)*  
{thumb_analysis}

🤲 *검지 분석 (대인 관계, 행동 경향)*  
{index_analysis}

🖼 *NFT 이미지 보기:* [이미지 링크]({image_url})
"""
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url_msg, data=payload)
