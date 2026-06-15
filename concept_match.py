#!/usr/bin/env python3
"""concept_match.py

Find concepts in combinations.csv that share quarks with a given concept.

Scoring:
  1 shared quark  = 33
  2 shared quarks = 66
  3 shared quarks = 99

Usage:
    python concept_match.py           # interactive loop
    python concept_match.py plant dog # one-shot
"""

from __future__ import annotations

import sys
from pathlib import Path
from collections import defaultdict

COMBINATIONS_CSV = Path(__file__).with_name("combinations.csv")
QUIT_WORDS = {"quit", "exit", "q"}
TOP_N = 3


def load(path: Path) -> dict[str, list[str]]:
    data: dict[str, list[str]] = defaultdict(list)
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or ";" not in line:
            continue
        concept, _, quark = line.partition(";")
        concept, quark = concept.strip(), quark.strip()
        if concept and quark:
            data[concept].append(quark)
    return dict(data)


def score(shared: int) -> int:
    return min(shared, 3) * 33


def find_matches(concept: str, data: dict[str, list[str]]) -> None:
    quarks = data.get(concept)
    if not quarks:
        print(f"  '{concept}' not found in combinations.csv")
        return

    quark_set = set(quarks)
    print(f"\nConcept: '{concept}'  quarks: {', '.join(quarks)}")

    results: list[tuple[int, str, list[str]]] = []
    for other, other_quarks in data.items():
        if other == concept:
            continue
        shared = quark_set & set(other_quarks)
        if shared:
            results.append((score(len(shared)), other, sorted(shared)))

    results.sort(key=lambda x: -x[0])

    if not results:
        print("  No matches found.")
        return

    print(f"Top {TOP_N} matches:")
    for s, other, shared in results[:TOP_N]:
        print(f"  {s:3d}  {other:<20} shared: {', '.join(shared)}")


def main() -> None:
    if not COMBINATIONS_CSV.exists():
        sys.exit(f"Cannot find: {COMBINATIONS_CSV}")

    data = load(COMBINATIONS_CSV)
    print(f"Loaded {len(data)} concepts from '{COMBINATIONS_CSV.name}'.")

    args = [a for a in sys.argv[1:] if a.strip()]
    if args:
        for concept in args:
            find_matches(concept.strip(), data)
        return

    print("Enter a concept to match. Type 'quit' to exit.")
    while True:
        try:
            concept = input("\nConcept> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not concept or concept.lower() in QUIT_WORDS:
            break
        find_matches(concept, data)


if __name__ == "__main__":
    main()
