import requests

def send_tree_info_to_sheet(name, phone, tree_info):
    webhook_url = "https://script.google.com/macros/s/AKfycbz41rbng__uK7ZEFTX7qMGi00EDmCmjNEaLYd5Mevh66K2dP9U0MqRNedjTzQ3h17uK/exec"

    payload = {
        "name": name,
        "phone": phone,
        "tree_desc": tree_info["desc"],
        "tree_image_hint": tree_info["image_hint"]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        print("📤 구글시트 응답:", response.status_code, response.text)
    except Exception as e:
        print("❌ 구글시트 전송 실패:", str(e))
