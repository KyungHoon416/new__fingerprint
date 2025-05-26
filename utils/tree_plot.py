
import matplotlib.pyplot as plt
import numpy as np
import os

from flask import url_for

def draw_tree_rings_combined(left_density, right_density, filename="tree.png"):
    import matplotlib.pyplot as plt
    import os

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.set_facecolor("#fdf9f0")
    ax.axis("off")

    total_rings = max(len(left_density), len(right_density))
    for i in range(total_rings):
        radius = 0.2 + i * 0.15
        lw = 10 * ((left_density[i] if i < len(left_density) else 0) +
                   (right_density[i] if i < len(right_density) else 0)) / 2
        color = "#815B3A" if lw > 0.3 else "#C9B8A0"
        circle = plt.Circle((0.5, 0.5), radius, color=color, fill=False, lw=lw)
        ax.add_artist(circle)

    # 저장 경로
    save_dir = os.path.join("static", "images")
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, filename)

    plt.savefig(path, dpi=150, bbox_inches="tight", transparent=True)
    plt.close()

    # Render에서 공개되는 정적 파일 경로로 URL 반환
    return f"https://fingerprint-jbdj.onrender.com/static/images/{filename}"


