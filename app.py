
from flask import Flask, request, jsonify
from utils.image_decode import decode_image
from utils.fingerprint_features import summarize_fingerprint
from utils.tree_plot import draw_tree_rings_combined
from gpt import build_prompt, call_gpt_mini
import uuid

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    img1 = decode_image(data["image1"])
    img2 = decode_image(data["image2"])

    left_txt, left_density = summarize_fingerprint(img1)
    right_txt, right_density = summarize_fingerprint(img2)

    prompt = build_prompt(left_txt, right_txt)
    result = call_gpt_mini(prompt)

    img_path = draw_tree_rings_combined(left_density, right_density, f"tree_{uuid.uuid4().hex}.png")


    return jsonify({"result": result})
