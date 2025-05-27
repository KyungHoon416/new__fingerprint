# utils/fingerprint_features.py
import cv2
import numpy as np
from utils.image_decode import decode_image  # ✅ 여기로부터 가져옴

def radial_density(gray_img, num_rings=5):
    h, w = gray_img.shape
    center = (w // 2, h // 2)
    max_radius = int(np.hypot(w, h) / 2)
    edges = cv2.Canny(gray_img, 100, 200)
    results = []
    for i in range(num_rings):
        r1 = int(i * max_radius / num_rings)
        r2 = int((i + 1) * max_radius / num_rings)
        mask = np.zeros_like(gray_img)
        cv2.circle(mask, center, r2, 255, -1)
        cv2.circle(mask, center, r1, 0, -1)
        ring = cv2.bitwise_and(edges, edges, mask=mask)
        density = np.count_nonzero(ring) / (np.count_nonzero(mask) + 1e-5)
        results.append(round(density, 4))
    return results

def curve_direction_label(edges):
    sobelx = cv2.Sobel(edges, cv2.CV_64F, 1, 0, ksize=3)
    avg_grad = np.mean(sobelx)
    if avg_grad > 10:
        return "↗️ 우상향 흐름 (도전적 성향)"
    elif avg_grad < -10:
        return "↙️ 좌하향 흐름 (내면 성찰형)"
    else:
        return "⏺ 중심 수렴 흐름 (감정 통제형)"

def interpret_densities(densities):
    if densities[0] > 0.08 and sum(densities[1:]) < 0.15:
        return "📍 손끝 중심에서 바깥쪽으로 갈수록 선의 농도가 점차 옅어졌습니다. 이는 깊은 내면의 집중력과 자기 통제력이 강하다는 신호일 수 있습니다."
    elif sum(densities[:2]) < 0.05:
        return "📍 중심의 선이 흐릿해 감정 표현이 자유롭고 외부 지향적일 수 있습니다."
    else:
        return "📍 선의 밀도가 전체적으로 일정해, 감정 균형과 조절력이 뛰어난 사람일 수 있습니다."

def interpret_texture(gray_img):
    gabor_k = cv2.getGaborKernel((21, 21), 4.0, 0, 10.0, 0.5, 0, ktype=cv2.CV_32F)
    filtered = cv2.filter2D(gray_img, cv2.CV_8UC3, gabor_k)
    std = np.std(filtered)
    if std > 12:
        return "📍 지문의 결(질감)은 매우 다채롭고 섬세하게 나타났습니다. 감정의 폭이 넓고, 다양한 상황에 감각적으로 반응할 줄 아는 성향을 보여줍니다."
    else:
        return "📍 지문의 결은 단순하고 균일하며, 감정을 일정하게 유지하려는 성향이 엿보입니다."

def summarize_fingerprint(base64_str):
    try:
        img = decode_image(base64_str)  # ✅ PIL → np.ndarray 변환 완료된 이미지
        if img is None:
            raise ValueError("이미지 디코딩 실패 (None 반환됨)")

        edges = cv2.Canny(img, 100, 200)
        summary = "지문 윤곽 분석 완료"
        return summary, edges

    except Exception as e:
        print(f"❌ 이미지 처리 중 오류: {e}")
        raise e
