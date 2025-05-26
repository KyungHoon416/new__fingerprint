
from flask import Flask, request, jsonify
from utils.image_decode import decode_image
from utils.fingerprint_features import summarize_fingerprint
from utils.tree_plot import draw_tree_rings_combined
from gpt import build_prompt, call_gpt_mini
from utils.telegram_bot import send_telegram_result
import uuid
import traceback

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()

        image1 = data.get("image1")
        image2 = data.get("image2")
        name = data.get("name", "이름 없음")
        phone = data.get("phone", "번호 없음")

        if not image1 or not image2:
            return jsonify({"result": "❌ 이미지 데이터 누락됨"}), 400

        img1 = decode_image(image1)
        img2 = decode_image(image2)

        left_txt, left_density = summarize_fingerprint(img1)
        right_txt, right_density = summarize_fingerprint(img2)

        prompt = build_prompt(left_txt, right_txt)
        result = call_gpt_mini(prompt)

        filename = f"tree_{uuid.uuid4().hex}.png"
        img_path = draw_tree_rings_combined(left_density, right_density, filename)

        message = f"이름: {name}\n전화번호: {phone}\n\n{result}"

        try:
            send_telegram_result(message, img_path)
        except Exception as e:
            print("❌ 텔레그램 전송 중 예외:", str(e))

        return jsonify({"result": result})

    except Exception as e:
        print("❌ 서버 내부 오류:", str(e))
        print(traceback.format_exc())
        return jsonify({"result": f"❌ 서버 오류: {str(e)}"}), 500
