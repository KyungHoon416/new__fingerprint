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

def visualize_tree_like_image(skeleton):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_facecolor("white")
    ax.axis("off")
    ax.imshow(skeleton, cmap='gray')

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf
