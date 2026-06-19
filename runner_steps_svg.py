#!/usr/bin/env python3
"""runner_steps_svg.py — generates runner_steps.svg"""

W, H = 860, 580

lines = []
lines.append(f'<rect width="{W}" height="{H}" fill="#0d1117"/>')

# Title
lines.append(
    f'<text x="{W//2}" y="32" text-anchor="middle" font-family="monospace" '
    f'font-size="15" font-weight="bold" fill="#ffffff">runner.py — improvement steps</text>'
)

# ── Central pipeline ─────────────────────────────────────────────────────────
CX = 430
pipe = [
    ("quark in",    80,  "#4b5563"),
    ("route",      160,  "#4b5563"),
    ("rule match", 240,  "#4b5563"),
    ("actuate",    320,  "#4b5563"),
    ("goal check", 400,  "#4b5563"),
    ("reset / loop", 480, "#374151"),
]
BW, BH = 140, 32

for label, y, col in pipe:
    lines.append(
        f'<rect x="{CX - BW//2}" y="{y}" width="{BW}" height="{BH}" '
        f'rx="6" fill="{col}" stroke="#6b7280" stroke-width="1"/>'
    )
    lines.append(
        f'<text x="{CX}" y="{y + 21}" text-anchor="middle" font-family="monospace" '
        f'font-size="11" fill="#e5e7eb">{label}</text>'
    )

# Arrows between pipeline boxes
for _, y, _ in pipe[:-1]:
    ay = y + BH
    lines.append(
        f'<line x1="{CX}" y1="{ay}" x2="{CX}" y2="{ay + 28}" '
        f'stroke="#6b7280" stroke-width="1.5" marker-end="url(#arr)"/>'
    )

# Loop-back arrow from reset to quark in
lines.append(
    f'<path d="M {CX - BW//2} 496 Q 60 496 60 80 Q 60 64 {CX - BW//2} 64" '
    f'fill="none" stroke="#4b5563" stroke-width="1.5" stroke-dasharray="4,3"/>'
)

# ── Enhancement callouts ─────────────────────────────────────────────────────
# Each: (step, title, detail, color, x, y, arrow_target_x, arrow_target_y)
EW, EH = 190, 48

enhancements = [
    (1, "multi-triangle routing",   "sense(quark) -> triangle",       "#1e3a8a", 170, 148, CX - BW//2, 176),
    (4, "actuator confirmation",    "wait for quark back",             "#78350f", 620, 308, CX + BW//2, 336),
    (2, "escalation",               "stat broken -> orchestrator",     "#7f1d1d", 620, 388, CX + BW//2, 416),
    (3, "memory",                   "last N quarks buffer",            "#134e4a", 170, 388, CX - BW//2, 416),
    (5, "unknown fallback",         "-> quark_overlap + combinations", "#3b0764", 170, 468, CX - BW//2, 496),
]

for step, title, detail, color, ex, ey, ax, ay in enhancements:
    # Box
    lines.append(
        f'<rect x="{ex}" y="{ey}" width="{EW}" height="{EH}" '
        f'rx="6" fill="{color}" stroke="#9ca3af" stroke-width="1"/>'
    )
    # Step number
    lines.append(
        f'<text x="{ex + 10}" y="{ey + 16}" font-family="monospace" '
        f'font-size="10" font-weight="bold" fill="#fde68a">{step}</text>'
    )
    # Title
    lines.append(
        f'<text x="{ex + 24}" y="{ey + 16}" font-family="monospace" '
        f'font-size="10" font-weight="bold" fill="#ffffff">{title}</text>'
    )
    # Detail
    lines.append(
        f'<text x="{ex + 10}" y="{ey + 34}" font-family="monospace" '
        f'font-size="9" fill="#d1d5db">{detail}</text>'
    )
    # Connector line to pipeline
    bx = ex + EW if ex < CX else ex
    lines.append(
        f'<line x1="{bx}" y1="{ey + EH//2}" x2="{ax}" y2="{ay}" '
        f'stroke="#9ca3af" stroke-width="1" stroke-dasharray="3,3"/>'
    )

# Arrow marker
lines.insert(1,
    '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
    '<path d="M0,0 L0,6 L8,3 z" fill="#6b7280"/></marker></defs>'
)

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">\n'
    + "\n".join(f"  {l}" for l in lines)
    + "\n</svg>\n"
)

with open("runner_steps.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("Saved runner_steps.svg")
