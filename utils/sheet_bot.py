import requests

GAS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzKSNf2sRA8WG7YrvaYkYWrPjhnnAsnzdwAHBe8uDTRocqAdAY-CkMDVpkqw1mKN-sI/exec"  # 실제 Web App URL로 교체

def send_image_url_to_sheet(phone, image_url):
    payload = {
        "phone": phone,
        "imageUrl": image_url
    }

    try:
        response = requests.post(GAS_WEBHOOK_URL, json=payload)
        print("✅ Google Sheet 응답:", response.text)
        return response.text
    except Exception as e:
        print("❌ Google Sheet 전송 실패:", str(e))
