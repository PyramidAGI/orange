#!/usr/bin/env python3
"""rl_matcher_svg.py — generates rl_matcher.svg"""

W, H = 860, 520

lines = []
lines.append(f'<rect width="{W}" height="{H}" fill="#0d1117"/>')

# Arrow marker
lines.insert(0,
    '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
    '<path d="M0,0 L0,6 L8,3 z" fill="#6b7280"/></marker>'
    '<marker id="arr2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
    '<path d="M0,0 L0,6 L8,3 z" fill="#fbbf24"/></marker></defs>'
)

def box(x, y, w, h, fill, stroke, label, sublabel=None, label_color="#e5e7eb"):
    lines.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    )
    ty = y + h // 2 + (0 if not sublabel else -7)
    lines.append(
        f'<text x="{x + w//2}" y="{ty}" text-anchor="middle" font-family="monospace" '
        f'font-size="11" font-weight="bold" fill="{label_color}">{label}</text>'
    )
    if sublabel:
        lines.append(
            f'<text x="{x + w//2}" y="{y + h//2 + 10}" text-anchor="middle" '
            f'font-family="monospace" font-size="9" fill="#9ca3af">{sublabel}</text>'
        )

def arrow(x1, y1, x2, y2, color="#6b7280", dash=None):
    da = f'stroke-dasharray="{dash}"' if dash else ""
    lines.append(
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="1.5" {da} marker-end="url(#arr)"/>'
    )

def label(x, y, text, color="#9ca3af", size=9, anchor="middle"):
    lines.append(
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="monospace" '
        f'font-size="{size}" fill="{color}">{text}</text>'
    )

# Title
label(W//2, 30, "rl_matcher.py — flow", "#ffffff", 14)

# ── Row 1: input ─────────────────────────────────────────────────────────────
box(30,  70, 160, 44, "#1f2937", "#6b7280", "quark input", "comma-separated CLI")
arrow(190, 92, 240, 92)

# ── Row 1: overlap filter ────────────────────────────────────────────────────
box(240, 70, 160, 44, "#1e3a8a", "#93c5fd", "overlap filter", "input ∩ rule keys")
arrow(400, 92, 450, 92)

# ── Row 1: candidates ────────────────────────────────────────────────────────
box(450, 70, 160, 44, "#134e4a", "#6ee7b7", "candidates", "triangles with match")
arrow(610, 92, 660, 92)

# ── Row 1: epsilon-greedy ────────────────────────────────────────────────────
box(660, 70, 170, 44, "#3b0764", "#c4b5fd", "ε-greedy select", "explore / exploit")

# ── Row 2: chosen triangle ───────────────────────────────────────────────────
arrow(745, 114, 745, 180)
label(760, 150, "chosen", "#9ca3af", 9, "start")
box(660, 180, 170, 44, "#78350f", "#fbbf24", "run triangle", "fire matching rules")

# ── Row 2: reward ────────────────────────────────────────────────────────────
arrow(660, 202, 610, 202)
box(450, 180, 160, 44, "#1f2937", "#6b7280", "reward", "coverage + goal bonus")

# ── Row 2: Q-update ──────────────────────────────────────────────────────────
arrow(450, 202, 400, 202)
box(240, 180, 160, 44, "#1e3a8a", "#93c5fd", "Q-update", "Q = Q + α(r - Q)")

# ── Row 2: Q-table ───────────────────────────────────────────────────────────
arrow(240, 202, 190, 202)
box(30, 180, 160, 44, "#134e4a", "#6ee7b7", "Q-table", "state → triangle → score")

# ── Feedback: Q-table feeds back into epsilon-greedy ────────────────────────
# Down from Q-table, across bottom, up to epsilon-greedy
lines.append(
    f'<path d="M 110 224 Q 110 290 745 290 Q 745 224 745 224" '
    f'fill="none" stroke="#6b7280" stroke-width="1.5" stroke-dasharray="4,3" '
    f'marker-end="url(#arr)"/>'
)
label(430, 308, "Q-values inform next selection", "#4b5563", 9)

# ── No candidates path ───────────────────────────────────────────────────────
arrow(530, 70, 530, 330, "#4b5563", "3,3")
box(450, 330, 160, 36, "#1f2937", "#4b5563", "no match", "print + skip")
label(560, 320, "no overlap", "#4b5563", 9, "start")

# ── Triangle files annotation ────────────────────────────────────────────────
box(30, 380, 780, 100, "#111827", "#374151", "", None)
label(430, 400, "triangles/", "#fde68a", 10)
tri_names = [
    ("triangle_grip1", "bond+force"),
    ("triangle_nav1", "loc+sequence"),
    ("triangle_energy1", "energy+stat full"),
    ("triangle_balance1", "normal+support"),
    ("triangle_obstacle1", "loc+normal"),
]
for i, (name, goal) in enumerate(tri_names):
    tx = 50 + i * 158
    lines.append(
        f'<rect x="{tx}" y="410" width="148" height="52" rx="5" '
        f'fill="#1f2937" stroke="#374151" stroke-width="1"/>'
    )
    label(tx + 74, 426, name, "#e5e7eb", 8)
    label(tx + 74, 442, f"goal: {goal}", "#6ee7b7", 8)
    # Arrow from overlap filter down to triangle box
    lines.append(
        f'<line x1="{tx + 74}" y1="114" x2="{tx + 74}" y2="410" '
        f'stroke="#1f2937" stroke-width="0"/>'
    )

# Arrow from overlap filter down to triangle library
arrow(320, 114, 320, 375, "#374151", "3,3")
label(328, 260, "loads from", "#374151", 9, "start")

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">\n'
    + "\n".join(f"  {l}" for l in lines)
    + "\n</svg>\n"
)

with open("rl_matcher.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("Saved rl_matcher.svg")
