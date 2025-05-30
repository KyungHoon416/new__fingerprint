# utils/fingerprint_features.py
import cv2
import numpy as np
from utils.image_decode import decode_image  # ✅ 여기로부터 가져옴
from skimage.filters import meijering, frangi, sato
from skimage.feature import hessian_matrix, hessian_matrix_eigvals
from skimage.filters.rank import entropy
from skimage.morphology import disk
from .preprocessor import correct_shadow  # 그림자 제거 (있다면)
import matplotlib.pyplot as plt

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

def summarize_fingerprint(gray_img):  # 이미 디코딩된 numpy 이미지가 들어옴
    try:
        if gray_img is None:
            raise ValueError("입력된 이미지가 None입니다.")

        edges = cv2.Canny(gray_img, 100, 200)
        summary = "지문 윤곽 분석 완료"
        return summary, edges

    except Exception as e:
        print(f"❌ 이미지 처리 중 오류: {e}")
        raise e


def deep_summarize_fingerprint(gray_img):
    try:
        # 대비 & 명암 보정
        gray = correct_shadow(gray_img)

        # ⭕ 윤곽 추출
        edges = cv2.Canny(gray, 50, 150)

        # 📊 선 밀도 분석
        radial = radial_density(gray)
        density_text = interpret_densities(radial)

        # 🔍 질감 분석
        texture_text = interpret_texture(gray)
        texture_std = round(np.std(gray), 3)

        # 🌱 Ridge 강조 필터
        frangi_img = frangi(gray / 255.0)
        sato_img = sato(gray / 255.0)
        ridge_mean = {
            "Frangi": round(np.mean(frangi_img), 4),
            "Sato": round(np.mean(sato_img), 4)
        }

        # ↗️ 방향 분석
        orientation = np.degrees(np.arctan2(
            cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5),
            cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        ))
        avg_angle = round(np.nanmean(orientation), 2)

        # 🎨 시각화
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 4, 1)
        plt.imshow(gray, cmap='gray')
        plt.title("1. 원본 (보정 후)")
        plt.axis('off')

        plt.subplot(1, 4, 2)
        plt.imshow(edges, cmap='gray')
        plt.title("2. Canny 윤곽선")
        plt.axis('off')

        plt.subplot(1, 4, 3)
        plt.imshow(frangi_img, cmap='gray')
        plt.title("3. Frangi Ridge")
        plt.axis('off')

        plt.subplot(1, 4, 4)
        plt.imshow(sato_img, cmap='gray')
        plt.title("4. Sato Ridge")
        plt.axis('off')

        plt.tight_layout()
        plt.show()

        # 최종 텍스트 요약
        summary_text = f"{density_text}\n{texture_text}\n📐 평균 방향 각도: {avg_angle}도"

        return summary_text, {
            "radial": radial,
            "texture_std": texture_std,
            "ridge_mean": ridge_mean,
            "avg_angle": avg_angle
        }

    except Exception as e:
        print(f"❌ [deep_summarize_fingerprint] 오류: {e}")
        raise e
