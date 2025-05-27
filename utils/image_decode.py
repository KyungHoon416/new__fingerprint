import base64
import numpy as np
from PIL import Image
import io

def decode_image(b64_string):
    image_data = base64.b64decode(b64_string)
    pil_img = Image.open(io.BytesIO(image_data)).convert("L")  # 흑백 변환
    return np.array(pil_img)  # ✅ NumPy 배열로 변환
