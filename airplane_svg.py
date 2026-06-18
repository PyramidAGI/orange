#!/usr/bin/env python3
"""airplane_svg.py — generates airplane_triangles.svg"""

W, H = 820, 480

triangles = [
    ("triangle_flight1", "force → animate\nenergy → drive",   "#3b0764", 130, 290),
    ("triangle_nav1",    "loc → sequence\npattern → transport","#1e3a8a", 310, 290),
    ("triangle_fuel1",   "energy → waitfor\nstat → normal",   "#134e4a", 490, 290),
    ("triangle_safety1", "problem → solve\nevent → shield",   "#7f1d1d", 670, 290),
]

TW, TH = 130, 90   # triangle half-width, height

def tri_points(cx, cy):
    return f"{cx},{cy - TH} {cx - TW},{cy + TH//2} {cx + TW},{cy + TH//2}"

orch_x, orch_y, orch_w, orch_h = 310, 40, 200, 52
orch_cx = orch_x + orch_w // 2
orch_cy = orch_y + orch_h

lines = []

# Background
lines.append(f'<rect width="{W}" height="{H}" fill="#0d1117"/>')

# Orchestrator box
lines.append(
    f'<rect x="{orch_x}" y="{orch_y}" width="{orch_w}" height="{orch_h}" '
    f'rx="8" fill="#78350f" stroke="#fbbf24" stroke-width="2"/>'
)
lines.append(
    f'<text x="{orch_cx}" y="{orch_y + 22}" text-anchor="middle" '
    f'font-family="monospace" font-size="13" font-weight="bold" fill="#fbbf24">orchestrator</text>'
)
lines.append(
    f'<text x="{orch_cx}" y="{orch_y + 40}" text-anchor="middle" '
    f'font-family="monospace" font-size="10" fill="#fde68a">airplane1</text>'
)

# Triangles
for name, wires, color, cx, cy in triangles:
    apex_y = cy - TH
    # Connector line from orchestrator to triangle apex
    lines.append(
        f'<line x1="{orch_cx}" y1="{orch_cy}" x2="{cx}" y2="{apex_y}" '
        f'stroke="#6b7280" stroke-width="1.5" stroke-dasharray="5,3"/>'
    )
    # Triangle fill
    lines.append(
        f'<polygon points="{tri_points(cx, cy)}" '
        f'fill="{color}" stroke="#9ca3af" stroke-width="1.5" opacity="0.92"/>'
    )
    # Name above apex
    lines.append(
        f'<text x="{cx}" y="{apex_y - 8}" text-anchor="middle" '
        f'font-family="monospace" font-size="10" font-weight="bold" fill="#e5e7eb">{name}</text>'
    )
    # Wire labels inside triangle
    for k, wire in enumerate(wires.split("\n")):
        wy = cy - 12 + k * 18
        lines.append(
            f'<text x="{cx}" y="{wy}" text-anchor="middle" '
            f'font-family="monospace" font-size="9" fill="#ffffff">{wire}</text>'
        )
    # sensor / actuator labels at base corners
    base_y = cy + TH // 2
    lines.append(
        f'<text x="{cx - TW + 4}" y="{base_y + 14}" text-anchor="start" '
        f'font-family="monospace" font-size="8" fill="#6ee7b7">sensor</text>'
    )
    lines.append(
        f'<text x="{cx + TW - 4}" y="{base_y + 14}" text-anchor="end" '
        f'font-family="monospace" font-size="8" fill="#93c5fd">actuator</text>'
    )

# Title
lines.append(
    f'<text x="{W//2}" y="24" text-anchor="middle" '
    f'font-family="monospace" font-size="15" font-weight="bold" fill="#ffffff">Airplane — triangles + orchestrator</text>'
)

# Footer
lines.append(
    f'<text x="{W//2}" y="{H - 10}" text-anchor="middle" '
    f'font-family="monospace" font-size="9" fill="#4b5563">ctrl / plan / nav runs inside each triangle</text>'
)

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">\n'
    + "\n".join(f"  {l}" for l in lines)
    + "\n</svg>\n"
)

with open("airplane_triangles.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("Saved airplane_triangles.svg")
