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

@app.route("/analyze/tree", methods=["POST"])
def analyze_tree():
    try:
        data = request.get_json()
        thumb_result = data.get("thumb_result", "")
        index_result = data.get("index_result", "")

        tree_info = select_tree_from_text(thumb_result, index_result)

        # 선택적으로 텔레그램으로 간단 메시지만 전송 (원할 경우)
        message = f"""
🌲 *당신을 담은 나무: {tree_info['name']}*
{tree_info['desc']}

🖼️ *나무 이미지 힌트*
{tree_info['image_hint']}
"""
        send_telegram_result(message)

        # 응답에 필요한 최소 정보만 전달
        return jsonify({
            "tree_name": tree_info["name"],
            "tree_desc": tree_info["desc"],
            "image_hint": tree_info["image_hint"],
            "result": "✅ 요약 분석 완료"
        })

    except Exception as e:
        print("❌ 서버 내부 오류 (요약):", str(e))
        print(traceback.format_exc())
        return jsonify({"result": f"❌ 서버 오류: {str(e)}"}), 500
