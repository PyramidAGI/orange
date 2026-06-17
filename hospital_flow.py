#!/usr/bin/env python3
"""hospital_flow.py

10x10 pandas DataFrame representing hospital patient flow.
Pyramid shape: row 0 = apex (patient location), row 9 = base (raw signals).
Cells outside the pyramid are blank. Quarks are sparsely placed within it.
"""

import random
import pandas as pd

# 10x10 empty grid
df = pd.DataFrame("", index=range(10), columns=range(10))

# Pyramid: row i active from col max(0,4-i) to col min(9,4+i)
def in_pyramid(row, col):
    return max(0, 4 - row) <= col <= min(9, 4 + row)

# Sparse quark placements — semantically layered for hospital patient flow
# Row 0: location         — where the patient is right now
# Row 1: status           — stable or something wrong
# Row 2: vitals & signals — stat, time, trigger events
# Row 3: resources        — equipment, records, care support
# Row 4: procedures       — treatment order, ward transport
# Row 5: structure        — staff, protocols, teams
# Row 6: interventions    — bottlenecks and fixes
# Row 7: patient basics   — energy, food, protection
# Row 8: monitoring       — sensors and recurring patterns
# Row 9: foundation       — discharge pressure, capacity signals

placements = [
    (0, 4, "loc"),
    (1, 3, "problem"),     (1, 5, "normal"),
    (2, 2, "stat"),        (2, 4, "time"),        (2, 6, "event"),
    (3, 1, "tool"),        (3, 4, "data"),        (3, 7, "support"),
    (4, 0, "activity"),    (4, 3, "sequence"),    (4, 6, "transport"),  (4, 8, "own"),
    (5, 1, "contract"),    (5, 4, "organization"),(5, 7, "group"),      (5, 9, "dominate"),
    (6, 0, "solve"),       (6, 3, "waitfor"),     (6, 6, "fix"),        (6, 9, "conflict"),
    (7, 2, "energy"),      (7, 5, "food"),        (7, 8, "shield"),
    (8, 1, "channel"),     (8, 4, "transducer"),  (8, 7, "pattern"),    (8, 9, "val"),
    (9, 0, "animate"),     (9, 3, "increase"),    (9, 6, "compress"),   (9, 9, "reward"),
]

for row, col, quark in placements:
    if in_pyramid(row, col):
        df.at[row, col] = quark

# Column widths derived from the first pyramid so both grids align
col_widths = {c: max(len(str(c)), df[c].map(len).max()) + 2 for c in df.columns}

print("Hospital patient flow — quark grid (10x10, pyramid)\n")
print(df.to_string(col_space=col_widths))

# Second pyramid: random mask over the first — changes every run
mask = pd.DataFrame("", index=range(10), columns=range(10))
populated = [(r, c) for r, c, _ in placements if in_pyramid(r, c)]
chosen = random.sample(populated, k=max(1, len(populated) // 3))
for row, col in chosen:
    mask.at[row, col] = df.at[row, col]

print("\n\nRandom mask (changes every run)\n")
print(mask.to_string(col_space=col_widths))
