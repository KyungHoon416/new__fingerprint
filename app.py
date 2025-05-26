from flask import Flask, request, jsonify
from utils.image_decode import decode_image
from utils.fingerprint_features import summarize_fingerprint
from utils.tree_plot import draw_tree_rings_combined
from gpt import build_prompt, call_gpt_mini
from utils.telegram_bot import send_telegram_result
import uuid
import traceback

app = Flask(__name__)

@app.route("/analyze/thumb", methods=["POST"])
def analyze_thumb():
    try:
        data = request.get_json()

        image = data.get("image")
        name = data.get("name", "이름 없음")
        phone = data.get("phone", "번호 없음")

        if not image:
            return jsonify({"result": "❌ 엄지 이미지 누락됨"}), 400

        img = decode_image(image)
        summary, density = summarize_fingerprint(img)
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

        image = data.get("image")
        name = data.get("name", "이름 없음")
        phone = data.get("phone", "번호 없음")

        if not image:
            return jsonify({"result": "❌ 검지 이미지 누락됨"}), 400

        img = decode_image(image)
        summary, density = summarize_fingerprint(img)
        prompt = build_prompt("", summary)
        result = call_gpt_mini(prompt)

        return jsonify({"result_index": result})

    except Exception as e:
        print("❌ 서버 내부 오류 (검지):", str(e))
        print(traceback.format_exc())
        return jsonify({"result": f"❌ 서버 오류: {str(e)}"}), 500
