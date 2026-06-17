# Orange

## Tree climbing robot simulator — options

Four options for a CLI-based simulator, using the ideas from this directory.

---

### Option A: Log-driven state machine

The robot's state (position on trunk, grip, energy) is a set of log.csv rows written each tick. The CLI reads the tail of the log to display current state. Every action appends a new record. Fully faithful to the existing format — the simulator *is* the log.

### Option B: Quark-state simulator

The robot's state is a dict of active quarks with numeric values — `loc=40`, `force=60`, `energy=80`, etc. CLI commands (e.g. `grip`, `climb`, `rest`) map to quarks via combinations.csv, which then update the state values. Closest to the quark vocabulary already built.

### Option C: Double-triangle control loop

Implement the sensor/actuator/control/plan/nav skeleton from the green readme. The robot has live sensor readings (`force`, `loc`, `energy`) and actuators (`drive`, `animate`). The CLI runs the loop step by step and prints each phase. This is the most architecturally correct version — a robot running a double triangle.

### Option D: Natural language → quark → action

User types free text (`"tighten grip on trunk"`), it gets mapped to quarks via `quark_overlap.py`, and the matched quarks drive the simulation step. Slowest (API call per command) but the most integrated with the existing toolchain.

---

The most coherent with the existing system would be **B + A together**: quark-state values as the simulation engine, log.csv as the output record. Option C is the right architecture if you want to eventually run this on a real robot. Option D is the most experimental.

---

## Motor control via double triangle *(ptd: this is an example of emergent intelligence of the LLM)*

A double triangle fits well for controlling the robot's motors. The quarks already mapped in combinations.csv give us the sensor and actuator sides directly — `grasper→force/animate`, `leg→support/animate/force`, `servo→drive/force`, `arm→support/force`.

Natural wiring for a tree climbing robot:

- `force → animate` — grip force on bark drives leg movement
- `loc → drive` — position on the tree drives the servo
- `stat → sequence` — surface condition (wet bark) drives the movement sequence
- `energy → waitfor` — battery level gates whether to continue climbing ("gates" means it acts as a condition that blocks or allows the next action: when battery drops below a threshold, the robot stops and waits rather than continuing — like a traffic light that permits or blocks movement)

The sensor side already has candidates: `battery`, `servo`, `grasper` all have transducer quarks. The actuator side: `leg`, `arm`, `servo` all have drive/animate quarks. The double triangle ties these into a control skeleton — sensor → control → actuator → nav → plan — bridging from "quarks mapped" to "robot controlled."

**One triangle or three?** The problem tree has three failure branches: grip, navigation, energy. These map cleanly to three separate triangles coordinated by an orchestrator, rather than one triangle for the whole robot. Each subsystem gets its own sensor/actuator loop, and the orchestrator decides which triangle's diagnosis is active.

---

## CLI project scaffolder — concept

A general-purpose CLI tool that interviews you about any project, maps it to quarks, and generates a Python skeleton. Quarks make this project-agnostic: the same tool works for a tree climbing robot, a repair café, or a greenhouse.

### Stage 1: Interview

The CLI asks a fixed set of structured questions:

- *What is the goal?* — one sentence
- *What are the entities?* — the ontology (things that exist in the project)
- *What can be sensed/measured?* — inputs
- *What actions does it take?* — outputs
- *What are the failure modes?* — problems to handle

Each answer is a comma-separated list of words, saved as a project file (e.g. `project.csv`).

### Stage 2: Quark mapping

Each word from the interview gets matched to quarks — first checking combinations.csv (instant), then calling `quark_overlap.py` for unknowns. The quarks are then sorted by role:

- **O quarks** (observable: `force`, `loc`, `energy`) → sensor variables
- **A quarks** (action: `animate`, `drive`, `waitfor`) → actuator functions
- **T quarks** (thing: `container`, `support`, `tool`) → data structures
- **S quarks** (state: `conflict`, `val`, `organization`) → state variables

### Stage 3: Model → code

The sorted quarks map directly to a Python skeleton:

- One double triangle per failure mode from the problem tree
- Sensor quarks → `read_*()` functions
- Actuator quarks → `act_*()` functions
- The control loop skeleton is always the same five rows: sensor, actuator, control, plan, nav

The quarks are the intermediate representation — they decouple "what the project is about" from "what code to generate." The same code generator works for any project because the quark roles (O/A/T/S) always map to the same code shapes.
