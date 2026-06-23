#!/usr/bin/env python3
"""grounding.py — inward layer: sensor readings -> quarks

Rules are loaded from log.csv (role=g, typ=lt/gt).
Row format: description;g;lt|gt;sensor_name;unit;quark;threshold;default

Architecture:
  sensors -> grounding.py -> quarks -> runner.py / rl_matcher.py

Usage:
  python grounding.py              interactive: set sensor values, tick, see quarks
  python grounding.py --demo       run preset robot + social scenarios
  python grounding.py --pipe       emit quarks to stdout (pipe into runner.py)

Pipe example:
  python grounding.py --pipe | python runner.py
"""

import sys
from pathlib import Path
from collections import defaultdict

LOG = Path(__file__).with_name("log.csv")


def load_sensors(path):
    sensors = defaultdict(lambda: {"value": 0.0, "unit": "", "rules": []})
    for row in path.read_text(encoding="utf-8").splitlines():
        if not row or row == ";;;;;;;;":
            continue
        p = (row + ";;;;;;;").split(";")
        role, typ, name, unit, quark = p[1], p[2], p[3], p[4], p[5]
        if role != "i" or typ not in ("lt", "gt"):
            continue
        try:
            threshold = float(p[6])
            default   = float(p[7])
        except ValueError:
            continue
        op = "<" if typ == "lt" else ">"
        s = sensors[name]
        s["unit"] = unit
        s["value"] = default          # initialise to default; overwritten once per sensor
        s["rules"].append((op, threshold, quark))
    return dict(sensors)


SENSORS = load_sensors(LOG)


def evaluate(sensors):
    active = set()
    for cfg in sensors.values():
        v = cfg["value"]
        for op, threshold, quark in cfg["rules"]:
            if (op == "<" and v < threshold) or (op == ">" and v > threshold):
                active.add(quark)
    return active


def quark_for(sensor_name, sensors):
    cfg = sensors[sensor_name]
    v = cfg["value"]
    return [q for op, t, q in cfg["rules"]
            if (op == "<" and v < t) or (op == ">" and v > t)]


def print_status(sensors):
    active = evaluate(sensors)
    print("\n  sensor                   value    unit       -> quarks")
    print("  " + "-" * 62)
    for name, cfg in sensors.items():
        fired = quark_for(name, sensors)
        marker = "  -> " + ", ".join(fired) if fired else ""
        print(f"  {name:<22}  {cfg['value']:>8.1f}  {cfg['unit']:<10}{marker}")
    print(f"\n  active: {sorted(active) if active else '(none)'}\n")
    return active


def run_demo():
    scenarios = [
        ("normal climb",      {}),
        ("branch oscillating + low battery",
                              {"branch_osc_hz": 2.8, "battery_%": 22}),
        ("grip failure on smooth bark",
                              {"branch_osc_hz": 0.3, "grip_force_n": 12,
                               "grip_success": 0.0}),
        ("branch may snap",   {"branch_integrity": 0.2, "lateral_g": 0.4}),
        ("tense meeting",     {"voice_pitch_hz": 310, "interruption_min": 4.5,
                               "trust_score": 0.25}),
        ("silent withdrawal", {"voice_pitch_hz": 130, "silence_ratio": 0.75,
                               "fatigue_score": 0.8}),
    ]

    defaults = {name: cfg["value"] for name, cfg in SENSORS.items()}

    for label, overrides in scenarios:
        for k in SENSORS:
            SENSORS[k]["value"] = defaults[k]
        for k, v in overrides.items():
            SENSORS[k]["value"] = v
        print(f"\n{'='*64}")
        print(f"  scenario: {label}")
        active = print_status(SENSORS)
        print(f"  -> feed these quarks into runner.py: {sorted(active)}")

    for k in SENSORS:
        SENSORS[k]["value"] = defaults[k]


def run_pipe():
    for line in sys.stdin:
        line = line.strip()
        if not line or line == "tick":
            for q in sorted(evaluate(SENSORS)):
                print(q, flush=True)
        elif "=" in line:
            name, _, val = line.partition("=")
            name = name.strip()
            if name in SENSORS:
                try:
                    SENSORS[name]["value"] = float(val.strip())
                except ValueError:
                    pass


def run_interactive():
    print(f"grounding.py — {len(SENSORS)} sensors loaded from log.csv")
    print("commands: <sensor>=<value>  tick  status  list  quit\n")

    while True:
        try:
            raw = input("sensor> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if raw in {"q", "quit", "exit"}:
            break
        if raw == "list":
            for name, cfg in SENSORS.items():
                rules_str = "  ".join(f"{op}{t}->{q}" for op, t, q in cfg["rules"])
                print(f"  {name:<22} = {cfg['value']:>8.1f} {cfg['unit']:<10}  {rules_str}")
            print()
            continue
        if raw in {"status", "tick", ""}:
            print_status(SENSORS)
            continue
        if "=" in raw:
            name, _, val = raw.partition("=")
            name = name.strip()
            if name not in SENSORS:
                print(f"  unknown sensor '{name}' — type 'list' to see all\n")
                continue
            try:
                SENSORS[name]["value"] = float(val.strip())
                fired = quark_for(name, SENSORS)
                tag = f"-> {fired}" if fired else "-> (no quark fired)"
                print(f"  {name} = {SENSORS[name]['value']} {SENSORS[name]['unit']}  {tag}\n")
            except ValueError:
                print(f"  not a number: '{val}'\n")
            continue
        print("  ? — try: battery_%=15  or  tick  or  list\n")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    elif "--pipe" in sys.argv:
        run_pipe()
    else:
        run_interactive()
