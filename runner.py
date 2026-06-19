#!/usr/bin/env python3
"""runner.py — load triangles + orchestrators from log.csv and drive with quarks"""
from pathlib import Path
from collections import defaultdict

LOG = Path(__file__).with_name("log.csv")


def parse():
    rules, goals, orcs = defaultdict(dict), {}, {}
    name = pending = None
    for row in LOG.read_text(encoding="utf-8").splitlines():
        if not row or row == ";;;;;;;;":
            continue
        p = (row + ";;;;;").split(";")
        sent, role, typ, e1, e2, rel = p[0], p[1], p[2], p[3], p[4], p[5]
        if role == "c" and typ == "activity":
            if rel.startswith("goal"):
                goals[name] = {q.strip() for q in rel[4:].split("+")}
            else:
                name = e1 or sent
        elif role == "a" and typ == "stat":
            pending = rel.strip()
        elif role == "c" and typ == "mode":
            if e1 == "orchestrator":
                orcs[e2] = rel
            elif pending and name:
                rules[name][pending] = rel.strip()
                pending = None
    return rules, goals, orcs


rules, goals, orcs = parse()
seen = defaultdict(set)

print("triangles :", list(rules))
print("goals     :", {k: v for k, v in goals.items()})
print("enter a quark to drive the system. 'quit' to exit.\n")

while True:
    try:
        q = input("quark> ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if q in {"q", "quit", "exit"}:
        break

    hit = False
    for name, r in rules.items():
        seen[name].add(q)
        if q in r:
            print(f"  [{name}] actuate -> {r[q]}")
            hit = True
        if goals.get(name, set()).issubset(seen[name]):
            print(f"  [{name}] GOAL REACHED: {goals[name]}")
            seen[name].clear()

    if not hit:
        print(f"  (no rule for '{q}')")

    targets = [t for t in orcs if q in rules.get(t, {})]
    if targets:
        print(f"  [orchestrator] handoff -> {targets}")
