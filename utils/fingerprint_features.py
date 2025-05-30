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


def interpret_texture_segmented(gray_img, num_segments=8):
    h, w = gray_img.shape
    segment_w = w // num_segments
    stds = []

    for i in range(num_segments):
        segment = gray_img[:, i * segment_w:(i + 1) * segment_w]
        stds.append(np.std(segment))

    avg_std = np.mean(stds)
    diversity = np.std(stds)

    if avg_std > 14 and diversity > 3:
        return "📍 지문 전체적으로 질감이 풍부하며, 구역 간 차이도 큽니다. 감정이 섬세하고 복합적이며, 상황에 따라 다양한 얼굴을 가집니다."
    elif avg_std > 10:
        return "📍 질감이 일정하면서도 적절한 다양성이 있습니다. 감정 표현이 안정적이면서 유연합니다."
    else:
        return "📍 전반적으로 질감이 균일하고 단순합니다. 감정을 일정하게 유지하며, 변화에 조심스럽게 반응합니다."

def deep_summarize_fingerprint(gray_img):
    try:
        # 대비 & 명암 보정
        gray = correct_shadow(gray_img)

        # ⭕ 윤곽 추출
        edges = cv2.Canny(gray, 50, 150)

        # 📊 선 밀도 분석
        radial = radial_density(gray, num_bins=8)
        density_text = interpret_densities(radial)

        # 🔍 질감 분석
        texture_text = interpret_texture_segmented(gray, num_bins=8)
        texture_std = round(np.std(gray), 3)

        # 🌱 Ridge 강조 필터
        if gray.shape[0] > 512 or gray.shape[1] > 512:
            gray_resized = cv2.resize(gray, (512, 512))
        else:
            gray_resized = gray
        gray_norm = gray_resized.astype(np.float32) / 255.0

        frangi_img = frangi(gray_norm)
        sato_img = sato(gray_norm)

        frangi_mean = np.mean(frangi_img[frangi_img > 0.01])
        sato_mean = np.mean(sato_img[sato_img > 0.01])
        ridge_mean = {
            "Frangi": round(frangi_mean, 4),
            "Sato": round(sato_mean, 4)
        }

        # ↗️ 방향 분석
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        orientation = np.degrees(np.arctan2(sobely, sobelx))
        avg_angle = round(np.nanmean(orientation), 2)

        # 최종 요약 텍스트
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
