from flask import Flask, request, jsonify
from utils.image_decode import decode_image
from utils.fingerprint_features import summarize_fingerprint
from utils.tree_plot import draw_tree_rings_combined
from gpt import build_prompt, call_gpt_mini
from utils.telegram_bot import send_telegram_image_and_full_result
import uuid
import traceback
from utils.tree_render import fingerprint_to_tree_lines, visualize_tree_black_lines_on_white_final
from utils.sheet_bot import send_image_url_to_sheet
import os

app = Flask(__name__)
SAVE_DIR = "static/nft_trees"
os.makedirs(SAVE_DIR, exist_ok=True)

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

        message = f"[엄지 분석 결과]\n이름: {name}\n전화번호: {phone}\n\n{result}"

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

        message = f"[검지 분석 결과]\n이름: {name}\n전화번호: {phone}\n\n{result}"

        return jsonify({"result_index": result})

    except Exception as e:
        print("❌ 서버 내부 오류 (검지):", str(e))
        print(traceback.format_exc())
        return jsonify({"result": f"❌ 서버 오류: {str(e)}"}), 500
    
    
@app.route("/analyze/tree", methods=["POST"])
def analyze_tree():
    try:
        data = request.get_json()

        image = data.get("image")
        name = data.get("name", "이름 없음")
        phone = data.get("phone", "번호 없음")
        # GPT 분석 결과 (엄지/검지)
        thumb_analysis = data.get("thumb_result", "")
        index_analysis = data.get("index_result", "")


        if not image:
            return jsonify({"result": "❌ 지문 이미지 누락됨"}), 400

        # 이미지 처리 및 나무 형태로 변환
        img = decode_image(image)
        skel = fingerprint_to_tree_lines(img)
        buf = visualize_tree_black_lines_on_white_final(skel)

        # 이미지 저장
        filename = f"{uuid.uuid4().hex}_tree.png"
        filepath = os.path.join(SAVE_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(buf.read())
            
            # ✅ image_url 정의
        image_url = f"https://fingerprint-jbdj.onrender.com/static/nft_trees/{filename}"
        
        # 시트에 이미지 삽입 요청
        send_image_url_to_sheet(phone, image_url)

        # 텔레그램 전송
        caption = f"🌳 [나의 나무 NFT]\n이름: {name}\n전화번호: {phone}"
        send_telegram_image_and_full_result(
            image_path=filepath,
            name=name,
            phone=phone,
            thumb_analysis=thumb_analysis,
            index_analysis=index_analysis,
            image_url=image_url
        )


        return jsonify({
            "result_tree": "✅ 나무 이미지 생성 및 텔레그램 전송 완료",
            "image_filename": filename
        })

    except Exception as e:
        print("❌ 서버 내부 오류 (나무):", str(e))
        print(traceback.format_exc())
        return jsonify({"result": f"❌ 서버 오류: {str(e)}"}), 500
