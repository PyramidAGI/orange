#!/usr/bin/env python3
"""minimal_triangle_svg.py — generates minimal_triangle.svg"""

W, H = 500, 420

cx, apex_y, base_y = 250, 80, 340
bl_x, br_x = 80, 420

lines = []
lines.append(f'<rect width="{W}" height="{H}" fill="#0d1117"/>')

# Triangle
lines.append(
    f'<polygon points="{cx},{apex_y} {bl_x},{base_y} {br_x},{base_y}" '
    f'fill="#1a1f2e" stroke="#6b7280" stroke-width="2"/>'
)

# Title
lines.append(
    f'<text x="{W//2}" y="36" text-anchor="middle" font-family="monospace" '
    f'font-size="14" font-weight="bold" fill="#ffffff">minimal triangle</text>'
)

# GOAL apex
lines.append(
    f'<text x="{cx}" y="{apex_y - 18}" text-anchor="middle" font-family="monospace" '
    f'font-size="11" fill="#9ca3af">goal</text>'
)
lines.append(
    f'<text x="{cx}" y="{apex_y + 20}" text-anchor="middle" font-family="monospace" '
    f'font-size="16" font-weight="bold" fill="#fde68a">normal</text>'
)

# SENSOR bottom-left
lines.append(
    f'<text x="{bl_x}" y="{base_y + 22}" text-anchor="middle" font-family="monospace" '
    f'font-size="11" fill="#9ca3af">sensor</text>'
)
lines.append(
    f'<text x="{bl_x}" y="{base_y + 40}" text-anchor="middle" font-family="monospace" '
    f'font-size="16" font-weight="bold" fill="#6ee7b7">problem</text>'
)

# ACTUATOR bottom-right
lines.append(
    f'<text x="{br_x}" y="{base_y + 22}" text-anchor="middle" font-family="monospace" '
    f'font-size="11" fill="#9ca3af">actuator</text>'
)
lines.append(
    f'<text x="{br_x}" y="{base_y + 40}" text-anchor="middle" font-family="monospace" '
    f'font-size="16" font-weight="bold" fill="#93c5fd">solve</text>'
)

# Wire label inside triangle
mid_y = (apex_y + base_y) // 2 + 20
lines.append(
    f'<text x="{cx}" y="{mid_y}" text-anchor="middle" font-family="monospace" '
    f'font-size="12" fill="#d1d5db">problem -> solve</text>'
)

# Loop arrow at base
lines.append(
    f'<path d="M {bl_x + 20} {base_y + 8} Q {cx} {base_y + 60} {br_x - 20} {base_y + 8}" '
    f'fill="none" stroke="#4b5563" stroke-width="1.5" stroke-dasharray="4,3" '
    f'marker-end="url(#arr)"/>'
)
lines.insert(1,
    '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
    '<path d="M0,0 L0,6 L8,3 z" fill="#4b5563"/></marker></defs>'
)

# Footer
lines.append(
    f'<text x="{W//2}" y="{H - 12}" text-anchor="middle" font-family="monospace" '
    f'font-size="9" fill="#4b5563">3 quarks: normal · problem · solve</text>'
)

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">\n'
    + "\n".join(f"  {l}" for l in lines)
    + "\n</svg>\n"
)

with open("minimal_triangle.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("Saved minimal_triangle.svg")
