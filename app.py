from flask import Flask, request, jsonify
from utils.image_decode import decode_image
from utils.fingerprint_features import summarize_fingerprint
from gpt import build_prompt, call_gpt_mini
from utils.telegram_bot import send_telegram_result
from utils.select_tree_from_text import select_tree_from_text
from utils.send_to_sheet import send_tree_info_to_sheet  # ✅ 구글 시트 연동 함수 추가
import traceback

app = Flask(__name__)

@app.route("/analyze/thumb", methods=["POST"])
def analyze_thumb():
    try:
        data = request.get_json()
        base64_str = data.get("image")

        gray_img = decode_image(base64_str)
        summary, _ = summarize_fingerprint(gray_img)

        prompt = build_prompt(summary, "")
        result = call_gpt_mini(prompt)

        return jsonify({"result_thumb": result})

    except Exception as e:
        print("❌ 서버 내부 오류 (엄지):", str(e))
        print(traceback.format_exc())
        return jsonify({"result": f"❌ 서버 오류: {str(e)}"}), 500

@app.route("/analyze/index", methods=["POST"])
def analyze_index():
    try:
        data = request.get_json()
        base64_str = data.get("image")

        gray_img = decode_image(base64_str)
        summary, _ = summarize_fingerprint(gray_img)

        prompt = build_prompt("", summary)
        result = call_gpt_mini(prompt)

        return jsonify({"result_index": result})

    except Exception as e:
        print("❌ 서버 내부 오류 (검지):", str(e))
        print(traceback.format_exc())
        return jsonify({"result": f"❌ 서버 오류: {str(e)}"}), 500

@app.route("/analyze/final", methods=["POST"])
def analyze_final():
    try:
        data = request.get_json()
        name = data.get("name", "이름 없음")
        phone = data.get("phone", "번호 없음")
        thumb_result = data.get("thumb_result", "")
        index_result = data.get("index_result", "")

        tree_info = select_tree_from_text(thumb_result, index_result)

        full_text = f"""
🌳 *나의 지문 심청 분석 결과* 🌳

👤 이름: {name}
📞 연락처: {phone}

👐 *엄지 분석*
{thumb_result}

☝️ *검지 분석*
{index_result}

🌲 *당신을 담은 나무: {tree_info['name']}*
{tree_info['desc']}

🖼️ *나무 이미지 힌트*
{tree_info['image_hint']}
"""

        # send_telegram_result(full_text)

        # ✅ 구글시트로 전송
        send_tree_info_to_sheet(name, phone, tree_info)

        return jsonify({"result": "✅ 분석 및 텔레그램 전송 완료", "tree": tree_info})

    except Exception as e:
        print("❌ 서버 내부 오류 (최종):", str(e))
        print(traceback.format_exc())
        return jsonify({"result": f"❌ 서버 오류: {str(e)}"}), 500
