import cv2
import numpy as np
import io
import matplotlib.pyplot as plt

def fingerprint_to_tree_lines(img_pil):
    img = np.array(img_pil.convert("L"))
    img = cv2.resize(img, (512, 512))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img)
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    binary_inv = cv2.bitwise_not(binary)

    skel = np.zeros(binary_inv.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    while cv2.countNonZero(binary_inv):
        eroded = cv2.erode(binary_inv, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(binary_inv, temp)
        skel = cv2.bitwise_or(skel, temp)
        binary_inv = eroded.copy()
    return skel


def visualize_tree_black_lines_on_white_final(skeleton):
    """
    skeleton: [(x1_list, y1_list), (x2_list, y2_list), ...] 형태의 리스트
    각 튜플은 하나의 선(곡선)을 의미합니다.
    """
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_facecolor("white")
    ax.axis("off")

    for x, y in skeleton:
        ax.plot(x, y, color="black", linewidth=1.2)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf