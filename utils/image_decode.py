
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np

def decode_image(base64_str):
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data)).convert("RGB")
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
