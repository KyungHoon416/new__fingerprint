
import matplotlib.pyplot as plt
import numpy as np

def draw_tree_rings_combined(left, right, filename="tree.png"):
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={'projection': 'polar'})
    ax.set_facecolor('white')
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    all_rings = max(len(left), len(right))
    for i in range(all_rings):
        r = i + 1
        d_left = left[i] if i < len(left) else 0
        d_right = right[i] if i < len(right) else 0
        color_l = '#A3D977' if d_left > 0.05 else '#F7DC6F' if d_left > 0.02 else '#E6E6E6'
        color_r = '#A3D977' if d_right > 0.05 else '#F7DC6F' if d_right > 0.02 else '#E6E6E6'
        ax.fill_between(np.linspace(0, np.pi, 100), r-0.5, r+0.5, color=color_l, alpha=0.7)
        ax.fill_between(np.linspace(np.pi, 2*np.pi, 100), r-0.5, r+0.5, color=color_r, alpha=0.7)
    ax.set_rticks([])
    ax.set_xticks([])
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    return filename
