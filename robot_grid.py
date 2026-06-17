#!/usr/bin/env python3
"""robot_grid.py

10x10 pandas DataFrame representing a tree climbing robot.
Pyramid shape: row 0 = apex (top of tree, narrow), row 9 = base (wide).
Cells outside the pyramid are blank. Quarks are sparsely placed within it.
"""

import random
import pandas as pd

# 10x10 empty grid
df = pd.DataFrame("", index=range(10), columns=range(10))

# Pyramid: row i active from col max(0,4-i) to col min(9,4+i)
def in_pyramid(row, col):
    return max(0, 4 - row) <= col <= min(9, 4 + row)

# Sparse quark placements — semantically layered for a tree climbing robot
# Row 0: goal             — where the robot aims to be
# Row 1: navigation       — branch and path decisions
# Row 2: body control     — limb coordination
# Row 3: actuators        — motors and drives
# Row 4: sensors          — reading the environment
# Row 5: energy & timing  — power and sequencing
# Row 6: failure handling — problems and fixes
# Row 7: physical contact — grip and surface
# Row 8: environment      — bark, nature, wetness
# Row 9: foundation       — raw data and state

placements = [
    (0, 4, "loc"),
    (1, 3, "fork"),       (1, 5, "trunk"),
    (2, 2, "animate"),    (2, 4, "grasper"),   (2, 6, "support"),
    (3, 1, "drive"),      (3, 4, "force"),      (3, 7, "sequence"),
    (4, 0, "transducer"), (4, 3, "stat"),       (4, 6, "pattern"),  (4, 8, "energy"),
    (5, 1, "waitfor"),    (5, 4, "transport"),  (5, 7, "leg"),      (5, 9, "arm"),
    (6, 0, "problem"),    (6, 3, "solve"),      (6, 6, "fix"),      (6, 9, "shield"),
    (7, 2, "channel"),    (7, 5, "compress"),   (7, 8, "expand"),
    (8, 1, "nature"),     (8, 4, "activity"),   (8, 7, "battery"),  (8, 9, "tool"),
    (9, 0, "data"),       (9, 3, "normal"),     (9, 6, "container"),(9, 9, "animate"),
]

for row, col, quark in placements:
    if in_pyramid(row, col):
        df.at[row, col] = quark

# Print with fixed column width
pd.set_option("display.max_columns", 10)
pd.set_option("display.width", 120)
pd.set_option("display.max_colwidth", 12)

# Column widths derived from the first pyramid so both grids align
col_widths = {c: max(len(str(c)), df[c].map(len).max()) + 2 for c in df.columns}

print("Tree climbing robot — quark grid (10x10, pyramid)\n")
print(df.to_string(col_space=col_widths))

# Second pyramid: random mask over the first — changes every run
mask = pd.DataFrame("", index=range(10), columns=range(10))
populated = [(r, c) for r, c, _ in placements if in_pyramid(r, c)]
chosen = random.sample(populated, k=max(1, len(populated) // 3))
for row, col in chosen:
    mask.at[row, col] = df.at[row, col]

print("\n\nRandom mask (changes every run)\n")
print(mask.to_string(col_space=col_widths))
