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
print("enter a quark, or a comma-separated quark set (tick output). 'quit' to exit.\n")

while True:
    try:
        raw = input("quark> ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if raw in {"q", "quit", "exit"}:
        break

    quarks = [q.strip() for q in raw.split(",") if q.strip()]
    if not quarks:
        continue

    if len(quarks) == 1:
        # single-quark: original behaviour
        q = quarks[0]
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

    else:
        # quark set (tick output): score triangles by overlap, fire best matches first
        qset = set(quarks)
        print(f"  tick: {sorted(qset)}")
        scored = sorted(
            ((len(qset & r.keys()), name, qset & r.keys()) for name, r in rules.items() if qset & r.keys()),
            reverse=True
        )
        if not scored:
            print("  (no triangle matches this quark set)")
        else:
            for _, name, overlap in scored:
                for q in sorted(overlap):
                    seen[name].add(q)
                    print(f"  [{name}] {q} -> {rules[name][q]}")
                if goals.get(name, set()).issubset(seen[name]):
                    print(f"  [{name}] GOAL REACHED: {goals[name]}")
                    seen[name].clear()
        targets = [t for t in orcs if qset & rules.get(t, {}).keys()]
        if targets:
            print(f"  [orchestrator] handoff -> {targets}")
