# utils/select_tree_from_text.py
def select_tree_from_text(thumb_text, index_text):
    text = (thumb_text + " " + index_text).lower()

    if any(kw in text for kw in ["감정 조절", "수용", "균형", "조화"]):
        return {
            "name": "느티나무",
            "desc": "감정을 잘 조절하고 내면의 중심이 단단한 사람입니다.",
            "image_hint": "넓게 퍼진 가지와 깊은 뿌리, 안정된 중심 구조",
        }

    elif any(kw in text for kw in ["유연", "흐름", "공감", "순응"]):
        return {
            "name": "버드나무",
            "desc": "감정을 유연하게 표현하고 주변과 자연스럽게 어울립니다.",
            "image_hint": "바람에 흔들리는 길고 가는 가지, 부드러운 선",
        }

    elif any(kw in text for kw in ["분출", "직진", "표현", "에너지"]):
        return {
            "name": "소나무",
            "desc": "자신의 감정을 분명히 표현하며 강한 추진력을 가졌습니다.",
            "image_hint": "수직으로 곧게 뻗은 줄기, 선명한 방향성",
        }

    elif any(kw in text for kw in ["억제", "내면", "은둔", "섬세"]) or "조용" in text:
        return {
            "name": "자작나무",
            "desc": "섬세하고 내면을 깊이 들여다보는 조용한 성찰자입니다.",
            "image_hint": "얇고 하얀 껍질, 정돈된 선과 비대칭 가지 구조",
        }

    else:
        return {
            "name": "플라타너스",
            "desc": "다층적인 감정과 풍부한 관계망을 가진 복합적 성향입니다.",
            "image_hint": "넓고 복잡하게 뻗은 가지, 서로 엮인 관계 구조",
        }