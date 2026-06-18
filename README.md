# Orange

![Darwin-like machine](darwin_triangle.png)

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

---

## Quark grid examples

Two grids have been built so far (`robot_grid.py`, `factory_happiness.py`). A third suggestion:

### Hospital patient flow

Tracking how patients move through a hospital from arrival to discharge.

- **Row 0**: `loc` — where the patient is right now (the single most critical fact)
- **Row 1**: `problem` ↔ `normal` — is something wrong or is the patient stable
- **Row 2**: `stat`, `time`, `event` — vitals, wait time, trigger events
- **Row 3**: `tool`, `data`, `support` — equipment, records, care support
- **Row 4**: `activity`, `sequence`, `transport` — procedures, treatment order, moving between wards
- **Row 5**: `contract`, `organization`, `group` — staff assignments, protocols, teams
- **Row 6**: `solve`, `waitfor`, `fix` — interventions and bottlenecks
- **Row 7**: `energy`, `food`, `shield` — patient condition basics
- **Row 8**: `channel`, `transducer`, `pattern` — monitoring signals
- **Row 9**: `animate`, `increase`, `compress` — discharge pressure, capacity

The same `solve`/`fix`/`waitfor` quarks that handle a robot's failure modes also handle a hospital bottleneck — a bed waiting for a patient is `waitfor`, a ward at capacity is `compress`.

### Why quarks fit any problem

The 39 quarks describe a climbing robot, a factory floor, and a hospital ward without any changes to the vocabulary. That is not a coincidence — it is the point.

Most domain-specific models fail to transfer because their primitives are too concrete: a "grip strength" variable means nothing outside robotics. Quarks sit one level higher. `force` is grip strength in a robot, workload pressure in a factory, and dosage intensity in a hospital. The word changes; the quark stays the same. This is what makes the same grid template, the same scaffolder, and the same double triangle wiring reusable across every domain.

The test is always: can you describe what went wrong using only the 39 names? If a nurse says "the patient waited too long and the ward ran out of capacity" — that is `waitfor`, `compress`, `problem`. If a factory worker says "the bonus system stopped working and conflicts went up" — that is `reward`, `conflict`, `val`. The quarks do not need to be extended for new domains; they need to be *mapped* to new domains, which is exactly what `quark_overlap.py` and `combinations.csv` do.

---

## A universal Darwin-like machine

The quark system is structured like a Darwin machine — something that can adapt to any environment using a fixed set of primitives.

- **Quarks are the genome** — 39 fixed bases that combine differently for every environment. Just as DNA uses 4 bases to describe every organism, quarks use 39 primitives to describe a robot, a factory, a hospital, without changing the alphabet.

- **The double triangle is the cell** — the same sensor/actuator/control/plan/nav machinery runs on any quark mapping. The "hardware" is universal; only the wiring changes.

- **The scaffolder is development** — it reads the genome (quark mapping from the interview) and grows an organism (Python skeleton) from it.

- **The eval loop is selection pressure** — `outcomes.log` and `weights.json` in the green repo reinforce what worked and penalize what didn't. Wires that solved problems get higher scores; abandoned triangles fade.

- **The random mask is mutation** — a random subset of the model exposed each run, structurally similar to how genetic expression works: not all genes are active at once.

The one missing piece for it to be fully Darwinian is **autonomous variation** — the system generating new quark mappings on its own and testing them, rather than waiting for a human to provide the interview answers. That is the step the green readme calls "the first conversion the machine does without the human."

The architecture is right. It is a Darwin machine with one hand still held by a human.

---

## What if you sent this to another planet?

If you shipped this software on Raspberry Pis inside a robot to another planet, it could partially build itself up — and the breakdown is interesting.

**What it could do without you:**
- Run existing double triangles — the sensor/actuator loop works autonomously on the Pi
- Log what worked and what didn't, update `weights.json`, and gradually shift its wiring preferences toward what the new environment rewards
- Map new sensor readings to quarks via `combinations.csv` if they match known concepts
- Adapt *within* the quark vocabulary — if the planet has force, energy, location, and time (every physical environment does), the 39 quarks still apply

**What it cannot do yet:**
- Generate new double triangles without a human running the scaffolder interview
- Write new Python code for genuinely new situations
- Understand phenomena that don't map to any of the 39 quarks — if the planet has something truly alien, the vocabulary has no slot for it
- Physically repair itself if hardware breaks

**The deep point:**
The quarks were chosen to be universal physical primitives, not Earth-specific ones. `force`, `energy`, `loc`, `radiation`, `time` describe any physical environment in the universe — the vocabulary would survive the trip. What wouldn't survive is the human who currently does the interview and writes the problem trees.

The missing piece is one function: `build_triangle(observation)` — the system noticing something isn't working, generating a new hypothesis, and testing it without asking anyone. The eval loop and the weights are already the scaffolding for that. It is the last hand to let go of.

---

## Triangle vs orchestrator — where does a record belong?

**It belongs in a triangle if** the mode switch is a direct response to a sensor reading — "battery drops below 40, nav fires recharge mode" is a wire: `energy → waitfor`. That's the nav row of the triangle doing its job. The triangle handles it autonomously within its own loop.

**It belongs in the orchestrator if** the mode switch involves choosing between triangles — "grip triangle is failing, hand control to the energy triangle." The orchestrator's job is coordination across triangles, not running a single loop. It decides which triangle is active, not what happens inside one.

A record that belongs in the orchestrator:
```
grip failure unresolved, orchestrator activates energy recovery triangle;c;mode;orchestrator;triangle_energy1;handoff;30;50;
```
That's a handoff between triangles — which is the orchestrator's actual job.

### orchestrator1.csv

```
;;;;;;;;
grip failure unresolved, orchestrator activates energy recovery triangle;c;mode;orchestrator;triangle_energy1;handoff;30;50;
;;;;;;;;
navigation dead end detected, orchestrator activates grip triangle to backtrack;c;mode;orchestrator;triangle_grip1;handoff;60;70;
;;;;;;;;
```

Two cross-triangle handoffs: energy failure hands off to `triangle_energy1`, navigation dead end hands off to `triangle_grip1` to backtrack. Each record is wrapped in `;;;;;;;;` separators matching the log format.

---

## Pseudocode for `build_triangle(observation)`

```
build_triangle(observation):

    1. MAP observation → quarks
       - check combinations.csv (instant, no API)
       - if not found → call quark_overlap(observation)
       - result: quark_set = {force, loc, problem, ...}

    2. CHECK if existing triangles already cover this
       - for each running doubletriangle:
           if quark_set ∩ triangle.sensor_quarks is not empty:
               return  # already handled, no new triangle needed

    3. DIAGNOSE — classify each quark by role
       - O quarks (observable) → candidate sensor sides
       - A quarks (action)     → candidate actuator sides
       - T/S quarks            → context, logged but not wired

    4. RANK wire candidates
       - for each O quark in quark_set:
           score all (O_quark → A_quark) pairs using weights.json
           skip pairs already used in existing triangles
           pick highest scoring unseen pair

    5. ASSEMBLE triangle draft
       - take top 4-5 wires
       - compute triangle_score (coverage × pair quality × no redundancy)
       - if triangle_score too low → widen search, try next-best wires
       - write to doubletriangle_draft.csv

    6. RUN draft triangle for N cycles
       - activate sensor loop (read O quarks)
       - apply control logic
       - fire actuator loop (push A quarks)
       - log each cycle to log.csv

    7. EVALUATE against criterion
       - was the triggering observation resolved?
       - YES → record_outcome(solved)
                update_weights(wires, +)
                promote draft → doubletriangle_N.csv
       - NO  → record_outcome(abandoned)
                update_weights(wires, -)
                go back to step 4 with updated weights
                (next iteration picks different wires)
```

The loop between steps 4 and 7 is the Darwinian part — each failed triangle nudges the weights, so the next candidate is different. Over many cycles the weight matrix converges toward wire combinations that actually work in this environment, without any human involved.

The only external dependency is step 1 for truly unknown observations — `quark_overlap` needs the API. Everything else runs locally on the Pi.
