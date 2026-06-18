#!/usr/bin/env python3
"""darwin_triangle.py

Generates a stylized layered triangle image representing the Darwin-like machine.
Saves to darwin_triangle.png.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

fig, ax = plt.subplots(figsize=(7, 9))
ax.set_xlim(0, 1)
ax.set_ylim(-0.05, 1.05)
ax.axis("off")
fig.patch.set_facecolor("#0d1117")
ax.set_facecolor("#0d1117")

# Triangle geometry: apex at top, base at bottom
apex_x, apex_y = 0.5, 0.90
base_y = 0.08
base_lx, base_rx = 0.05, 0.95

def edges(t):
    """At t=0 apex, t=1 base: return (y, left_x, right_x)."""
    y  = apex_y - t * (apex_y - base_y)
    lx = apex_x - t * (apex_x - base_lx)
    rx = apex_x + t * (base_rx - apex_x)
    return y, lx, rx

# Layer colours: deep purple → blue-teal toward base
layer_colors = ["#3b0764", "#4c1d95", "#1e3a8a", "#1e40af", "#155e75", "#134e4a"]

# Quark labels per layer (top → bottom)
layers = [
    ["loc"],
    ["fork", "mode"],
    ["animate", "grasper", "support"],
    ["drive", "force", "sequence"],
    ["transducer", "stat", "pattern", "energy"],
    ["problem", "solve", "waitfor", "normal", "data"],
]

n = len(layers)

# Draw filled trapezoid bands
for i in range(n):
    t0, t1 = i / n, (i + 1) / n
    y0, lx0, rx0 = edges(t0)
    y1, lx1, rx1 = edges(t1)
    pts = [(lx0, y0), (rx0, y0), (rx1, y1), (lx1, y1)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=layer_colors[i],
                         edgecolor="#cccccc", linewidth=0.6, alpha=0.9))

# Quark text in each band
for i, quarks in enumerate(layers):
    t_mid = (i + 0.5) / n
    y_mid, lx, rx = edges(t_mid)
    w = rx - lx
    for j, q in enumerate(quarks):
        x = lx + (j + 0.5) / len(quarks) * w
        fs = 7.5 if len(quarks) > 3 else 8.5
        ax.text(x, y_mid, q, ha="center", va="center",
                color="white", fontsize=fs, fontfamily="monospace",
                fontweight="bold")

# "goal" label at apex
ax.text(apex_x, apex_y + 0.025, "goal", ha="center", va="bottom",
        color="#f0abfc", fontsize=12, fontweight="bold", fontfamily="monospace")

# "sensor" and "actuator" at base corners
ax.text(base_lx + 0.01, base_y - 0.025, "sensor", ha="center", va="top",
        color="#6ee7b7", fontsize=10, fontweight="bold", fontfamily="monospace")
ax.text(base_rx - 0.01, base_y - 0.025, "actuator", ha="center", va="top",
        color="#93c5fd", fontsize=10, fontweight="bold", fontfamily="monospace")

# "ctrl / plan / nav" centred below the base
ax.text(0.5, base_y - 0.025, "ctrl / plan / nav", ha="center", va="top",
        color="#fde68a", fontsize=9, fontfamily="monospace", style="italic")

# Title
ax.text(0.5, 1.02, "Darwin-like machine", ha="center", va="bottom",
        color="white", fontsize=15, fontweight="bold")

plt.tight_layout(pad=0)
plt.savefig("darwin_triangle.png", dpi=150, bbox_inches="tight",
            facecolor="#0d1117")
print("Saved darwin_triangle.png")

# White background version
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
# Swap text colours for visibility on white
for txt in ax.texts:
    if txt.get_color() == "white":
        txt.set_color("#1a1a1a")
plt.savefig("darwin_triangle_light.png", dpi=150, bbox_inches="tight",
            facecolor="white")
print("Saved darwin_triangle_light.png")
