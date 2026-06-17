#!/usr/bin/env python3
"""factory_happiness.py

10x10 pandas DataFrame representing employee happiness measurement in a factory.
Pyramid shape: row 0 = apex (overall happiness score), row 9 = base (raw signals).
Cells outside the pyramid are blank. Quarks are sparsely placed within it.
"""

import random
import pandas as pd

# 10x10 empty grid
df = pd.DataFrame("", index=range(10), columns=range(10))

# Pyramid: row i active from col max(0,4-i) to col min(9,4+i)
def in_pyramid(row, col):
    return max(0, 4 - row) <= col <= min(9, 4 + row)

# Sparse quark placements — semantically layered for employee happiness
# Row 0: goal             — overall happiness / val score
# Row 1: key drivers      — reward and conflict are the two poles
# Row 2: social dynamics  — group, ownership, preference
# Row 3: work metrics     — activity, transactions, dominance
# Row 4: patterns         — recurring signals and norms
# Row 5: structure        — organization, contracts, roles
# Row 6: interventions    — what to do when something trips
# Row 7: basic needs      — food, tools, support
# Row 8: operational      — time, energy, data flow
# Row 9: foundation       — raw sensor readings and events

placements = [
    (0, 4, "val"),
    (1, 3, "reward"),      (1, 5, "conflict"),
    (2, 2, "group"),       (2, 4, "own"),         (2, 6, "pref"),
    (3, 1, "activity"),    (3, 4, "dominate"),    (3, 7, "transaction"),
    (4, 0, "pattern"),     (4, 3, "normal"),      (4, 6, "stat"),       (4, 8, "event"),
    (5, 1, "organization"),(5, 4, "contract"),    (5, 7, "sequence"),   (5, 9, "time"),
    (6, 0, "solve"),       (6, 3, "fix"),         (6, 6, "increase"),   (6, 9, "waitfor"),
    (7, 2, "food"),        (7, 5, "tool"),        (7, 8, "support"),
    (8, 1, "energy"),      (8, 4, "data"),        (8, 7, "transport"),  (8, 9, "channel"),
    (9, 0, "animate"),     (9, 3, "compress"),    (9, 6, "problem"),    (9, 9, "shield"),
]

for row, col, quark in placements:
    if in_pyramid(row, col):
        df.at[row, col] = quark

# Column widths derived from the first pyramid so both grids align
col_widths = {c: max(len(str(c)), df[c].map(len).max()) + 2 for c in df.columns}

print("Employee happiness in a factory — quark grid (10x10, pyramid)\n")
print(df.to_string(col_space=col_widths))

# Second pyramid: random mask over the first — changes every run
mask = pd.DataFrame("", index=range(10), columns=range(10))
populated = [(r, c) for r, c, _ in placements if in_pyramid(r, c)]
chosen = random.sample(populated, k=max(1, len(populated) // 3))
for row, col in chosen:
    mask.at[row, col] = df.at[row, col]

print("\n\nRandom mask (changes every run)\n")
print(mask.to_string(col_space=col_widths))
