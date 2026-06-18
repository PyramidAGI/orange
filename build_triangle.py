#!/usr/bin/env python3
"""build_triangle.py

Autonomous triangle builder. Builds incrementally — one step at a time.

Current: Step 1 — MAP observation -> quarks
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from collections import defaultdict

COMBINATIONS_CSV = Path(__file__).with_name("combinations.csv")
QUIT_WORDS = {"quit", "exit", "q"}


# ── Step 1: MAP observation -> quarks ────────────────────────────────────────

def load_combinations() -> dict[str, list[str]]:
    data: dict[str, list[str]] = defaultdict(list)
    for line in COMBINATIONS_CSV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or ";" not in line:
            continue
        concept, _, quark = line.partition(";")
        concept, quark = concept.strip(), quark.strip()
        if concept and quark:
            data[concept].append(quark)
    return dict(data)


def map_to_quarks(observation: str,
                  combinations: dict[str, list[str]],
                  use_api: bool = True) -> dict[str, list[str]]:
    """
    Split observation into words, look each up in combinations.csv.
    For words not found, optionally call quark_overlap via the OpenAI API.
    Returns {word: [quarks]} for every word that matched something.
    """
    words = [w.strip(".,!?;:").lower() for w in observation.split()]
    result: dict[str, list[str]] = {}
    unknown: list[str] = []

    for word in words:
        if word in combinations:
            result[word] = combinations[word]
        else:
            unknown.append(word)

    if unknown and use_api and os.environ.get("OPENAI_API_KEY"):
        try:
            from openai import OpenAI
            from quark_overlap import load_quarks, score_and_suggest
            quarks_list = load_quarks(Path(__file__).with_name("numbered quarks.csv"))
            if Path(__file__).with_name("complement quarks.csv").exists():
                quarks_list += load_quarks(
                    Path(__file__).with_name("complement quarks.csv"))
            client = OpenAI()
            for word in unknown:
                r = score_and_suggest(client, word, quarks_list)
                scores = r.get("scores", {})
                top2 = sorted(scores.items(), key=lambda x: -x[1])[:2]
                if top2 and top2[0][1] >= 40:
                    result[word] = [q for q, _ in top2]
        except Exception as exc:
            print(f"  (API lookup failed: {exc})")

    return result


def quark_set(mapped: dict[str, list[str]]) -> set[str]:
    """Flatten mapped result to a single set of unique quarks."""
    return {q for quarks in mapped.values() for q in quarks}


# ── Main (step 1 demo) ───────────────────────────────────────────────────────

def main() -> None:
    combinations = load_combinations()
    print(f"Loaded {len(combinations)} concepts from combinations.csv.")
    print("Enter an observation to map to quarks. Type 'quit' to exit.\n")

    while True:
        try:
            obs = input("Observation> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not obs or obs.lower() in QUIT_WORDS:
            break

        mapped = map_to_quarks(obs, combinations)
        if not mapped:
            print("  No quarks found.")
            continue

        print("  Mapped:")
        for word, quarks in mapped.items():
            print(f"    {word:<20} -> {', '.join(quarks)}")
        print(f"  Quark set: {{{', '.join(sorted(quark_set(mapped)))}}}")


if __name__ == "__main__":
    main()
