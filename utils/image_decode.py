import base64
import numpy as np
import cv2
from PIL import Image
import io

def decode_image(b64_string):
    try:
        image_data = base64.b64decode(b64_string)
        pil_image = Image.open(io.BytesIO(image_data)).convert("RGB")  # RGB 변환 필수
        open_cv_image = np.array(pil_image)
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
        return open_cv_image
    except Exception as e:
        print("이미지 디코딩 오류:", e)
        return None
