
import matplotlib.pyplot as plt
import numpy as np
import os

def draw_tree_rings_combined(left_density, right_density, filename="tree.png"):
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

    path = os.path.join("static", filename)
    os.makedirs("static", exist_ok=True)
    plt.savefig(path, dpi=150, bbox_inches="tight", transparent=True)
    plt.close()
    return path
