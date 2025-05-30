def select_tree_from_text(thumb_text, index_text):
    text_combined = (thumb_text + " " + index_text).lower()

    keyword_map = {
        "느티나무": [("감정 조절", 0.5), ("균형", 0.5), ("조화", 0.5), ("안정", 0.5), ("중심", 0.5)],
        "버드나무": [("유연", 1.0), ("흐름", 1.0), ("공감", 1.0), ("수용", 1.0), ("순응", 1.0)],
        "소나무": [("분출", 1.2), ("직진", 1.2), ("표현", 1.0), ("에너지", 1.0), ("명확", 1.0)],
        "자작나무": [("억제", 1.5), ("내면", 1.0), ("은둔", 1.5), ("섬세", 1.2), ("조용", 1.0), ("회피", 1.5)],
        "플라타너스": [("복잡", 1.5), ("얽힘", 1.5), ("다층", 1.5), ("관계", 1.0), ("풍부", 1.0), ("과거", 1.2), ("갈등", 1.5)],
    }

    tree_profiles = get_tree_profiles()
    score = {tree: 0.0 for tree in keyword_map}

    for tree, weighted_keywords in keyword_map.items():
        for keyword, weight in weighted_keywords:
            if keyword in text_combined:
                score[tree] += weight

    best_tree = max(score, key=score.get)
    return best_tree, score[best_tree]


def select_tree_from_metrics(radial, texture_std, ridge_mean, avg_angle):
    tree_profiles = get_tree_profiles()

    score = {
        "느티나무": 0.0,
        "자작나무": 0.0,
        "소나무": 0.0,
        "버드나무": 0.0,
        "플라타너스": 0.0,
    }

    center_density = radial[0]
    outer_density = sum(radial[1:]) / (len(radial) - 1)

    # ✅ 느티나무 조건 복원
    if center_density > 0.08 and texture_std > 12 and abs(avg_angle) < 10:
        score["느티나무"] += 1.0

    if texture_std < 10 and center_density < 0.05 and ridge_mean["Frangi"] < 0.05:
        score["자작나무"] += 1.0

    if avg_angle > 15 and ridge_mean["Sato"] > 0.07:
        score["소나무"] += 1.0

    if outer_density > center_density and texture_std > 13:
        score["버드나무"] += 1.0

    if ridge_mean["Frangi"] > 0.09 or abs(avg_angle) > 25:
        score["플라타너스"] += 1.0

    best_tree = max(score, key=score.get)
    return best_tree, score[best_tree]



def hybrid_select_tree(thumb_text, index_text, radial, texture_std, ridge_mean, avg_angle, weight_text=0.6, weight_metric=0.4):
    """
    텍스트 기반 분석과 이미지 기반 분석을 혼합하여 가장 적합한 트리 유형 반환
    """
    tree_profiles = get_tree_profiles()

    # 텍스트 기반 분석
    text_tree, text_score = select_tree_from_text(thumb_text, index_text)

    # 이미지 기반 분석
    metric_tree, metric_score = select_tree_from_metrics(
        radial=radial,
        texture_std=texture_std,
        ridge_mean=ridge_mean,
        avg_angle=avg_angle
    )

    # 점수 통합
    score = {tree: 0.0 for tree in tree_profiles}

    for tree in tree_profiles:
        if tree == text_tree:
            score[tree] += weight_text * text_score
        if tree == metric_tree:
            score[tree] += weight_metric * metric_score

    # 최고 점수의 트리 선택
    best_tree = max(score, key=score.get)
    return tree_profiles[best_tree]



def get_tree_profiles():
    return {
        "느티나무": {
            "name": "느티나무",
            "desc": "감정을 잘 조절하고 내면의 중심이 단단한 사람입니다.",
            "image_hint": "넓게 퍼진 가지와 깊은 뿌리, 안정된 중심 구조",
        },
        "버드나무": {
            "name": "버드나무",
            "desc": "감정을 유연하게 표현하고 주변과 자연스럽게 어울립니다.",
            "image_hint": "바람에 흔들리는 길고 가는 가지, 부드러운 선",
        },
        "소나무": {
            "name": "소나무",
            "desc": "자신의 감정을 분명히 표현하며 강한 추진력을 가졌습니다.",
            "image_hint": "수직으로 곧게 뻗은 줄기, 선명한 방향성",
        },
        "자작나무": {
            "name": "자작나무",
            "desc": "섬세하고 내면을 깊이 들여다보는 조용한 성찰자입니다.",
            "image_hint": "얇고 하얀 껍질, 정돈된 선과 비대칭 가지 구조",
        },
        "플라타너스": {
            "name": "플라타너스",
            "desc": "다층적인 감정과 풍부한 관계망을 가진 복합적 성향입니다.",
            "image_hint": "넓고 복잡하게 뻗은 가지, 서로 엮인 관계 구조",
        }
    }
