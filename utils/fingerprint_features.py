# utils/fingerprint_features.py
# import cv2
# import numpy as np
# from utils.image_decode import decode_image  # ✅ 여기로부터 가져옴
# from skimage.filters import meijering, frangi, sato
# from skimage.feature import hessian_matrix, hessian_matrix_eigvals
# from skimage.filters.rank import entropy
# from skimage.morphology import disk
import cv2
import numpy as np
from skimage.filters import frangi, sato
from .preprocessor import correct_shadow  # 그림자 제거 (있다면)

def radial_density(gray_img, num_bins=8):
    """
    중심으로부터의 방사형 밀도를 분석하는 함수

    Parameters:
        gray_img: 2D numpy array (흑백 이미지)
        num_bins: 방사 구간 수 (기본값 8)

    Returns:
        List[float] – 중심에서 외곽까지 각 구간의 픽셀 밀도 비율
    """
    # 이미지 크기
    h, w = gray_img.shape

    # 중심 좌표
    cx, cy = w // 2, h // 2

    # 최대 반지름 (가장 먼 코너까지의 거리)
    max_radius = np.sqrt(cx**2 + cy**2)

    # 각 픽셀에 대해 중심으로부터의 거리 계산
    Y, X = np.indices((h, w))
    distances = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)

    # 이진화: 선이 있는 영역만 분석
    _, binary = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    densities = []
    total_pixels = np.sum(binary > 0)

    for i in range(num_bins):
        r_min = (i / num_bins) * max_radius
        r_max = ((i + 1) / num_bins) * max_radius

        # 구간 마스크
        mask = (distances >= r_min) & (distances < r_max)
        count = np.sum((binary > 0) & mask)

        # 밀도 = 해당 구간 선 픽셀 수 / 전체 선 픽셀 수
        density = count / total_pixels if total_pixels > 0 else 0
        densities.append(round(density, 5))

    return densities



def curve_direction_label(edges):
    sobelx = cv2.Sobel(edges, cv2.CV_64F, 1, 0, ksize=3)
    avg_grad = np.mean(sobelx)
    if avg_grad > 10:
        return "↗️ 우상향 흐름 (도전적 성향)"
    elif avg_grad < -10:
        return "↙️ 좌하향 흐름 (내면 성찰형)"
    else:
        return "⏺ 중심 수렴 흐름 (감정 통제형)"

def interpret_densities(radial):
    """
    중심에서 외곽까지의 밀도 분포를 기반으로 감정의 구조적 흐름 해석

    Parameters:
        radial: List[float] – 중심~외곽 순서의 밀도 값 (ex: 8개)

    Returns:
        str – 해석된 감정 경향 설명
    """
    if not radial or len(radial) < 3:
        return "지문 데이터가 부족하여 선 밀도 분석이 어렵습니다."

    # 중심, 중간, 외곽 세 구간으로 요약
    n = len(radial)
    center = sum(radial[:n//3])
    mid = sum(radial[n//3:2*n//3])
    outer = sum(radial[2*n//3:])

    # 가장 높은 영역 찾기
    dominant = max(center, mid, outer)

    if dominant == center:
        return "당신은 감정의 중심을 내면에 잘 간직하고 있으며, 자기 통제력과 감정의 응축력이 뛰어난 사람입니다."
    elif dominant == mid:
        return "감정의 흐름이 일정하게 분포되어 있어, 내면과 외부 세계 사이에서 균형 잡힌 감정 표현을 보입니다."
    elif dominant == outer:
        return "당신은 감정을 자유롭게 표현하며, 외부 자극에 반응이 빠르고 개방적인 성향을 보입니다."
    else:
        return "감정 밀도 해석이 불가능합니다."


def interpret_texture_segmented(gray_img, num_bins=8):
    h, w = gray_img.shape
    bin_h, bin_w = h // num_bins, w // num_bins

    texture_map = []
    for i in range(num_bins):
        for j in range(num_bins):
            patch = gray_img[i * bin_h:(i + 1) * bin_h, j * bin_w:(j + 1) * bin_w]
            gabor_k = cv2.getGaborKernel((21, 21), 4.0, 0, 10.0, 0.5, 0, ktype=cv2.CV_32F)
            filtered = cv2.filter2D(patch, cv2.CV_8UC3, gabor_k)
            std = np.std(filtered)
            texture_map.append(std)

    avg_texture = np.mean(texture_map)

    if avg_texture > 12:
        return "📍 지문의 결은 영역만능 풍보하고 다양한 편입니다. 감각이 설명하며 다면적인 감정 반응을 보이는 건호가 있습니다."
    else:
        return "📍 지문의 결이 전망적으로 긴일하며 일관된 성향을 보여줍니다. 감정을 일정하게 유지하려는 건호가 있습니다."

def deep_summarize_fingerprint(gray_img):
    try:
        # 대비 & 명암 보정
        gray = correct_shadow(gray_img)

        # ⭕ 유가 추출
        edges = cv2.Canny(gray, 50, 150)

        # 파이드 물분률
        radial = radial_density(gray, num_bins=8)
        density_text = interpret_densities(radial)

        # 지문 결(진홍) 분석
        texture_text = interpret_texture_segmented(gray, num_bins=8)
        texture_std = round(np.std(gray), 3)

        # Ridge 강조
        if gray.shape[0] > 512 or gray.shape[1] > 512:
            gray_resized = cv2.resize(gray, (512, 512))
        else:
            gray_resized = gray

        frangi_img = frangi(gray_resized / 255.0)
        sato_img = sato(gray_resized / 255.0)
        ridge_mean = {
            "Frangi": round(np.mean(frangi_img), 4),
            "Sato": round(np.mean(sato_img), 4)
        }

        # 향 범지 분석
        orientation = np.degrees(np.arctan2(
            cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5),
            cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        ))
        avg_angle = round(np.nanmean(orientation), 2)

        # 요약 문장
        summary_text = f"{density_text}\n{texture_text}\n🖐️ 평균 방향 각도: {avg_angle}도"

        return summary_text, {
            "radial": radial,
            "texture_std": texture_std,
            "ridge_mean": ridge_mean,
            "avg_angle": avg_angle
        }

    except Exception as e:
        print(f"❌ [deep_summarize_fingerprint] 오류: {e}")
        raise e