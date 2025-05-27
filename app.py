from flask import Flask, request, jsonify
from utils.image_decode import decode_image
from utils.fingerprint_features import summarize_fingerprint
from gpt import build_prompt, call_gpt_mini
from utils.telegram_bot import send_telegram_result
from utils.select_tree_from_text import select_tree_from_text
from utils.send_to_sheet import send_tree_info_to_sheet  # ✅ 구글 시트 연동 함수 추가
import traceback
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
import json
from flask import render_template

# ✅ .env 파일 로딩
load_dotenv()

app = Flask(__name__)

SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# 환경변수에서 JSON 문자열 가져오기
json_creds_str = os.getenv("GOOGLE_SHEET_CREDENTIALS")

if not json_creds_str:
    raise ValueError("환경변수 GOOGLE_SHEET_CREDENTIALS가 누락됨")

# 문자열 → JSON으로 파싱
json_creds = json.loads(json_creds_str)

# private_key의 줄바꿈 복원
if "private_key" in json_creds:
    json_creds["private_key"] = json_creds["private_key"].replace("\\n", "\n")

CREDS = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, SCOPE)

GSPREAD_CLIENT = gspread.authorize(CREDS)
SHEET = GSPREAD_CLIENT.open("Code Lab 지문(응답)").worksheet("설문지 응답 시트1")

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

# # ✅ Vercel이 호출할 수 있는 GET 기반 결과 API
# @app.route("/analyze", methods=["GET"])
# def get_analysis_result():
#     try:
#         name = request.args.get("name")
#         phone = request.args.get("phone")

#         records = SHEET.get_all_values()
#         headers = records[0]
#         rows = records[1:]

#         for row in rows:
#             if row[2] == name and row[3] == phone:
#                 return jsonify({
#                     "thumb": row[8],
#                     "index": row[9],
#                     "tree_desc": row[10],
#                     "tree_image": row[11]
#                 })

#         return jsonify({"error": "❌ 일치하는 정보를 찾을 수 없습니다."}), 404

#     except Exception as e:
#         print("❌ 결과 조회 오류:", str(e))
#         return jsonify({"error": f"❌ 서버 오류: {str(e)}"}), 500
    
    
    
@app.route("/")
def search_form():
    return render_template("search_form.html")



@app.route("/view_result", methods=["GET"])
def view_result():
    try:
        name = request.args.get("name")
        phone_suffix = request.args.get("phone")  # 사용자가 입력한 뒷자리 4글자

        records = SHEET.get_all_values()
        rows = records[1:]

        for row in rows:
            sheet_name = row[2]  # C열
            sheet_phone = row[3]  # D열 (예: "010-1111-1111")

            if sheet_name == name and sheet_phone[-4:] == phone_suffix:
                return render_template("result.html", 
                    name=sheet_name,
                    phone=sheet_phone,
                    thumb=row[8] if len(row) > 8 else "없음",
                    index=row[9] if len(row) > 9 else "없음",
                    tree_desc=row[10] if len(row) > 10 else "없음"
                    tree_image=row[11] if len(row) > 11 else "없음"
                )

        return "❌ 일치하는 정보를 찾을 수 없습니다.", 404

    except Exception as e:
        return f"❌ 서버 오류: {str(e)}", 500

# @app.route("/view_result_test")
# def view_result_test():
    
#     return render_template("result.html", 
#     name="김경훈",
#     phone="010-1111-1111",
#     thumb="엄지 분석 결과 전체 텍스트",
#     index="검지 분석 결과 전체 텍스트",
#     tree_name="느티나무",
#     tree_desc="감정을 잘 조절하고 내면의 중심이 단단한 사람입니다.",
#     tree_image="넓게 퍼진 가지와 깊은 뿌리, 안정된 중심 구조"
# )
    
if __name__ == "__main__":
    app.run(debug=True)