# utils/image_decode.py
import base64
from PIL import Image
import io

def decode_image(b64_string):
    image_data = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_data)).convert("L")