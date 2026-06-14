#!/usr/bin/env python3
"""quark_overlap.py

Interactive CLI that maps a new concept against the existing "quarks"
(semantic primitives in "numbered quarks.csv") and measures how well the
concept is already covered.

For each new concept it:
  1. Asks the LLM to score every quark 0-100 for relevance to the concept.
  2. Reports an overall overlap % (the top score) and a ranked quark list.
  3. Suggests new physics/nature primitives (e.g. 'material') for gaps.

Requires the OPENAI_API_KEY environment variable.

Usage:
    python quark_overlap.py                 # interactive loop
    python quark_overlap.py dirt plant      # one-shot for given concepts
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    sys.exit("The 'openai' package is required: pip install openai")

QUARKS_CSV = Path(__file__).with_name("numbered quarks.csv")
COMPLEMENT_CSV = Path(__file__).with_name("complement quarks.csv")
COMBINATIONS_CSV = Path(__file__).with_name("combinations.csv")
CHAT_MODEL = os.environ.get("QUARK_CHAT_MODEL", "gpt-4o-mini")
TOP_N = 8
QUIT_WORDS = {"quit", "exit", "q"}


def load_quarks(path: Path) -> list[tuple[int, str]]:
    quarks: list[tuple[int, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or ";" not in line:
            continue
        num, _, name = line.partition(";")
        name = name.strip()
        if not name:
            continue
        try:
            quarks.append((int(num.strip()), name))
        except ValueError:
            continue
    return quarks


def next_number(quarks: list[tuple[int, str]]) -> int:
    return max((n for n, _ in quarks), default=0) + 1


def append_complement(number: int, concept: str) -> None:
    with COMPLEMENT_CSV.open("a", encoding="utf-8") as fh:
        fh.write(f"{number};{concept}\n")


def append_combination(input_concept: str, added_concept: str) -> None:
    with COMBINATIONS_CSV.open("a", encoding="utf-8") as fh:
        fh.write(f"{input_concept};{added_concept}\n")


def load_combinations() -> dict[str, list[str]]:
    """Return {concept: [quark, ...]} from combinations.csv."""
    result: dict[str, list[str]] = {}
    if not COMBINATIONS_CSV.exists():
        return result
    for line in COMBINATIONS_CSV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or ";" not in line:
            continue
        concept, _, quark = line.partition(";")
        result.setdefault(concept.strip(), []).append(quark.strip())
    return result


def score_and_suggest(client: OpenAI, concept: str,
                      quarks: list[tuple[int, str]]) -> dict:
    """Single LLM call: score all quarks 0-100 + suggest new primitives."""
    quark_list = ", ".join(name for _, name in quarks)
    prompt = (
        f"We maintain a small set of semantic primitives called 'quarks':\n"
        f"{quark_list}\n\n"
        f"Task: analyze the concept '{concept}'.\n\n"
        "Return a JSON object with exactly two keys:\n"
        "1. \"scores\": an object mapping every quark name to an integer 0-100 "
        "representing how strongly that quark captures or is needed to express "
        f"'{concept}'. Be generous — if a quark is clearly relevant, score it "
        "high (e.g. nature->plant should be 85+).\n"
        "2. \"suggestions\": an array of 3-5 objects, each with \"word\" (a "
        "single new primitive from physics or nature, NOT already in the quark "
        "list) and \"reason\" (one short line). Only suggest primitives that "
        f"would genuinely help map '{concept}' and similar concepts.\n\n"
        "Return ONLY the JSON object, no other text."
    )
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": "You are a concise ontology assistant. "
             "Always respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


def analyze(client: OpenAI, concept: str, quarks: list[tuple[int, str]],
            combinations: dict[str, list[str]]) -> None:
    cached = combinations.get(concept)
    if cached:
        print(f"\nConcept: '{concept}' (cached)")
        for quark in cached:
            print(f"  {quark}")
        return

    result = score_and_suggest(client, concept, quarks)

    raw_scores: dict = result.get("scores", {})
    suggestions: list = result.get("suggestions", [])

    # Build ranked list, tolerating minor name mismatches
    name_map = {name.lower(): (num, name) for num, name in quarks}
    scored: list[tuple[int, int, str]] = []
    for raw_name, score in raw_scores.items():
        key = raw_name.strip().lower()
        if key in name_map:
            num, name = name_map[key]
            scored.append((int(score), num, name))
    scored.sort(reverse=True)

    if not scored:
        print(f"\nConcept: '{concept}'\n  (no scores returned)")
        return

    best = scored[0][0]
    print(f"\nConcept: '{concept}'")
    print(f"Overall overlap with existing quarks: {best}% "
          f"(closest quark: '{scored[0][2]}')")

    if best >= 70:
        print("=> Well covered by an existing quark.")
        weak = False
    elif best >= 40:
        print("=> Partially covered -- a new primitive might sharpen it.")
        weak = True
    else:
        print("=> Poorly covered -- this concept needs a new primitive.")
        weak = True

    for _, _, name in scored[:2]:
        append_combination(concept, name)
        combinations.setdefault(concept, []).append(name)

    print(f"\nTop {TOP_N} closest quarks:")
    for score, num, name in scored[:TOP_N]:
        print(f"  {score:3d}%  #{num:<2} {name}")

    if suggestions:
        print("\nSuggested new physics/nature primitives:")
        for s in suggestions:
            word = s.get("word", "?")
            reason = s.get("reason", "")
            print(f"  {word} -- {reason}")
    _ = weak  # used implicitly via prompt context


def prompt_add(input_concept: str, quarks: list[tuple[int, str]]) -> None:
    try:
        word = input("\nAdd a grounding primitive? (word, or blank to skip)> ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return
    if not word or word.lower() in QUIT_WORDS:
        return

    if word.lower() in {name.lower() for _, name in quarks}:
        append_combination(input_concept, word)
        print(f"  '{word}' is already a primitive -- recorded '{input_concept};{word}' "
              f"in '{COMBINATIONS_CSV.name}'.")
        return

    num = next_number(quarks)
    append_complement(num, word)
    append_combination(input_concept, word)
    quarks.append((num, word))
    print(f"  Added #{num} '{word}' to '{COMPLEMENT_CSV.name}' "
          f"and recorded '{input_concept};{word}' in '{COMBINATIONS_CSV.name}'.")


def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set the OPENAI_API_KEY environment variable first.")
    if not QUARKS_CSV.exists():
        sys.exit(f"Cannot find quarks file: {QUARKS_CSV}")

    quarks = load_quarks(QUARKS_CSV)
    if not quarks:
        sys.exit("No quarks loaded from CSV.")
    if COMPLEMENT_CSV.exists():
        added = load_quarks(COMPLEMENT_CSV)
        quarks += added
        if added:
            print(f"Loaded {len(added)} extra concepts from '{COMPLEMENT_CSV.name}'.")

    combinations = load_combinations()
    client = OpenAI()
    print(f"Loaded {len(quarks)} quarks, {len(combinations)} cached concepts. "
          f"Model: {CHAT_MODEL}")

    args = [a for a in sys.argv[1:] if a.strip()]
    if args:
        for concept in args:
            analyze(client, concept.strip(), quarks, combinations)
        return

    print("Enter a concept to map. Type 'quit' to exit.")
    while True:
        try:
            concept = input("\nNew concept> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not concept or concept.lower() in QUIT_WORDS:
            break
        cached = concept in combinations
        analyze(client, concept, quarks, combinations)
        if not cached:
            prompt_add(concept, quarks)


if __name__ == "__main__":
    main()
