#!/usr/bin/env python3
"""grounding.py — inward layer: sensor readings → quarks

Architecture:
  sensors → grounding.py → quarks → runner.py / rl_matcher.py

Usage:
  python grounding.py              interactive: set sensor values, tick, see quarks
  python grounding.py --demo       run preset robot + social scenarios
  python grounding.py --pipe       emit quarks to stdout (pipe into runner.py)

Pipe example:
  python grounding.py --pipe | python runner.py
"""

import sys

# Sensor catalog.
# Each entry: signal_name -> {value, unit, rules: [(op, threshold, quark)]}
# op: "<" below threshold  |  ">" above threshold
#
# Threshold values are tunable — these are reasonable starting defaults.
# To ground a new domain: add sensors here, rules stay the same format.

SENSORS = {

    # ── physical robot ───────────────────────────────────────────────────────

    "battery_%": {
        "value": 75.0, "unit": "%",
        "rules": [
            ("<", 10,  "stat empty"),   # critical — enter sleep mode
            ("<", 30,  "stat low"),     # low — reduce speed
            (">", 80,  "stat full"),    # healthy
        ],
    },
    "motor_temp_c": {
        "value": 35.0, "unit": "C",
        "rules": [
            (">", 70,  "stat hot"),     # overheating — cool motor
        ],
    },
    "branch_osc_hz": {
        "value": 0.5, "unit": "Hz",
        "rules": [
            (">", 2.0, "stat fast"),    # branch still swinging — waitfor
        ],
    },
    "grip_force_n": {
        "value": 40.0, "unit": "N",
        "rules": [
            ("<", 20,  "stat soft"),    # surface too smooth — switch to claw
            (">", 60,  "stat rough"),   # rough surface — increase pressure
        ],
    },
    "lateral_g": {
        "value": 0.05, "unit": "g",
        "rules": [
            (">", 0.3, "stat heavy"),   # weight shift — redistribute
            (">", 0.6, "force"),        # severe imbalance — adjust stance
        ],
    },
    "branch_integrity": {
        "value": 1.0, "unit": "0-1",
        "rules": [
            ("<", 0.3, "stat broken"),  # branch may snap — abort
        ],
    },
    "path_density": {
        "value": 0.7, "unit": "0-1",
        "rules": [
            ("<", 0.1, "stat empty"),   # no branch ahead — extend sensor arm
            (">", 0.5, "pattern"),      # clear path structure — follow branch
        ],
    },
    "grip_success": {
        "value": 1.0, "unit": "0/1",
        "rules": [
            ("<", 0.5, "problem"),      # grip failed — engage suction / retry
        ],
    },

    # ── social room ──────────────────────────────────────────────────────────

    "voice_pitch_hz": {
        "value": 200.0, "unit": "Hz",
        "rules": [
            (">", 280,  "stat hot"),    # raised voices — slow down
            ("<", 140,  "stat cold"),   # withdrawal / flat affect — invite speaker
        ],
    },
    "speech_rate_wpm": {
        "value": 120.0, "unit": "wpm",
        "rules": [
            (">", 200, "stat fast"),    # rapid speech — tension rising
            ("<", 20,  "stat empty"),   # silence — reframe question
        ],
    },
    "interruption_min": {
        "value": 0.5, "unit": "/min",
        "rules": [
            (">", 3,   "stat rough"),   # frequent interruptions — set ground rules
        ],
    },
    "silence_ratio": {
        "value": 0.1, "unit": "0-1",
        "rules": [
            (">", 0.6, "stat cold"),    # prolonged silence — invite speaker
        ],
    },
    "participant_count": {
        "value": 4.0, "unit": "people",
        "rules": [
            (">", 0,   "stat size"),    # room is occupied — atmosphere active
        ],
    },
    "trust_score": {
        "value": 0.8, "unit": "0-1",
        "rules": [
            ("<", 0.3, "stat broken"),  # trust damaged — acknowledge harm
        ],
    },
    "fatigue_score": {
        "value": 0.2, "unit": "0-1",
        "rules": [
            (">", 0.7, "stat heavy"),   # overwhelm / exhaustion — call break
        ],
    },
}


def evaluate(sensors):
    """Apply threshold rules, return set of active quarks."""
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
        # label, sensor overrides
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

    # reset to defaults between scenarios
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
    """
    Pipe mode: read 'sensor=value' lines from stdin, emit quarks to stdout.
    Blank line or 'tick' emits current active quarks (one per line).
    Designed to feed runner.py via: python grounding.py --pipe | python runner.py
    """
    import fileinput
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
    print("grounding.py — sensor → quark mapping")
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
                rules_str = "  ".join(f"{op}{t}→{q}" for op, t, q in cfg["rules"])
                print(f"  {name:<22} = {cfg['value']:>8.1f} {cfg['unit']:<10}  {rules_str}")
            print()
            continue
        if raw in {"status", "tick", ""}:
            active = print_status(SENSORS)
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
