#!/usr/bin/env python3
"""rl_matcher.py — RL-based triangle selector using quark overlap"""
from pathlib import Path
from collections import defaultdict
import random

TRIANGLES_DIR = Path(__file__).with_name("triangles")
ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.3


def parse_triangle(path):
    rules, goal, name = {}, set(), None
    pending = None
    for row in path.read_text(encoding="utf-8").splitlines():
        if not row or row == ";;;;;;;;":
            continue
        p = (row + ";;;;;").split(";")
        sent, role, typ, e1, e2, rel = p[0], p[1], p[2], p[3], p[4], p[5]
        if role == "c" and typ == "activity":
            if rel.startswith("goal"):
                goal = {q.strip() for q in rel[4:].split("+")}
            else:
                name = e1 or sent
        elif role == "a" and typ == "stat":
            pending = rel.strip()
        elif role == "c" and typ == "mode" and pending:
            rules[pending] = rel.strip()
            pending = None
    return name, rules, goal


def load_triangles():
    triangles = {}
    for f in sorted(TRIANGLES_DIR.glob("*.csv")):
        _, rules, goal = parse_triangle(f)
        name = f.stem
        triangles[name] = {"rules": rules, "goal": goal}
    return triangles


def overlap(input_quarks, rules):
    return input_quarks & set(rules.keys())


def simulate(input_quarks, rules, goal):
    matched = overlap(input_quarks, rules)
    if not matched:
        return -5
    coverage = len(matched) / max(len(input_quarks), 1)
    goal_bonus = 5 if input_quarks & goal else 0
    return round(coverage * 10 + goal_bonus - 1)


# Q-table: state (frozenset of quarks) -> triangle name -> q-value
q_table = defaultdict(lambda: defaultdict(float))

triangles = load_triangles()
names = list(triangles)

print(f"Loaded {len(triangles)} triangles: {names}")
print("Enter quarks (comma-separated) to match. 'quit' to exit.\n")

while True:
    try:
        raw = input("quarks> ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if raw in {"q", "quit", "exit"}:
        break

    input_quarks = frozenset(q.strip() for q in raw.split(","))
    candidates = [n for n in names if overlap(input_quarks, triangles[n]["rules"])]

    if not candidates:
        print("  no triangle overlaps with this quark set\n")
        continue

    print(f"  candidates: {candidates}")
    sk = frozenset(input_quarks)

    # Epsilon-greedy selection
    if random.random() < EPSILON or not any(q_table[sk][n] for n in candidates):
        chosen = random.choice(candidates)
        print(f"  [explore]  -> {chosen}")
    else:
        chosen = max(candidates, key=lambda n: q_table[sk][n])
        print(f"  [exploit]  -> {chosen}")

    # Simulate
    t = triangles[chosen]
    reward = simulate(input_quarks, t["rules"], t["goal"])
    print(f"  reward: {reward:+d}")

    for q in overlap(input_quarks, t["rules"]):
        print(f"    {q} -> {t['rules'][q]}")

    # Q-update
    old_q = q_table[sk][chosen]
    q_table[sk][chosen] = old_q + ALPHA * (reward - old_q)
    print(f"  Q update: {old_q:.3f} -> {q_table[sk][chosen]:.3f}")

    # Show all candidate Q-values
    print(f"  Q-table for {set(input_quarks)}:")
    for n in candidates:
        bar = "=" * max(0, int(q_table[sk][n] * 3))
        print(f"    {n:<30} {q_table[sk][n]:+.3f}  {bar}")
    print()
