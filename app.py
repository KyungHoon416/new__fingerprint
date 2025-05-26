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

        image1 = data.get("image1")  # 엄지
        image2 = data.get("image2")  # 검지
        name = data.get("name", "이름 없음")
        phone = data.get("phone", "번호 없음")

        if not image1 or not image2:
            return jsonify({"result": "❌ 이미지 데이터 누락됨"}), 400

        img1 = decode_image(image1)
        left_summary, left_density = summarize_fingerprint(img1)
        prompt1 = build_prompt(left_summary, "")
        result1 = call_gpt_mini(prompt1)

        img2 = decode_image(image2)
        right_summary, right_density = summarize_fingerprint(img2)
        prompt2 = build_prompt("", right_summary)
        result2 = call_gpt_mini(prompt2)

        filename = f"tree_{uuid.uuid4().hex}.png"
        img_path = draw_tree_rings_combined(left_density, right_density, filename)
        tree_image_url = f"https://fingerprint-jbdj.onrender.com/static/{filename}"  # Render 기준

        message = f"이름: {name}\n전화번호: {phone}\n\n[엄지 분석]\n{result1}\n\n[검지 분석]\n{result2}"

        try:
            send_telegram_result(message, img_path)
        except Exception as e:
            print("❌ 텔레그램 전송 중 예외:", str(e))

        return jsonify({
            "result_thumb": result1,
            "result_index": result2,
            "tree_image_url": tree_image_url
        })

    except Exception as e:
        print("❌ 서버 내부 오류:", str(e))
        print(traceback.format_exc())
        return jsonify({"result": f"❌ 서버 오류: {str(e)}"}), 500
