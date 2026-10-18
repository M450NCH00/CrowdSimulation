# Hands-on trial of the shortlist (PT-6, part 1 of 2; issue #40)

This records what was run, what worked, what did not, and what each trial cost in code. The
use-or-build analysis that builds on it is `decision.md`. The step-by-step history, including
the dead ends, is `WORK_LOG-40.md`.

**Status.** Track #34's portable-rule idea, which these trials serve, is **a proposal that needs
the supervisor's sign-off**. The user allowed throwaway trial code for this issue ("Yes, proceed",
`WORK_LOG-40.md` A1). That is the user's answer, not a recorded supervisor approval of the
standing instruction in `README.md`.

**Nothing here is evidence about people.** Every scene uses default model parameters and
placeholder geometry. A result like "alight-first is faster" is a property of a model in one
scene, not a finding about passengers.

## Set-up

| Item | Value |
|---|---|
| Machine | AMD Ryzen 5 7535HS (6 cores, 12 threads), 15.3 GB RAM, Windows 11 Home; on AC power |
| Python | 3.13.3, in a new venv `integration/simulator-survey/spikes/.venv` (gitignored) |
| Install | `pip install --only-binary=:all:`, wheels only, so no setup or build script ran |
| Packages | `jupedsim==1.4.2`, `Mesa==3.5.1`, `networkx==3.7`; the full freeze is `spikes/requirements.txt` |
| Not installed | SUMO (not needed, see trial 2), Vadere and Menge (outside #40's permission) |
| Code | `spikes/*.py`; nothing else in the repository imports it |

**Code size** means lines that are not blank, comments or docstrings. It was counted with a
tokenizer script, not by eye.

### Install findings

- **`import mesa` fails on a clean install of Mesa 3.5.1.** `mesa/__init__.py` imports
  `discrete_space.network`, which imports `networkx`. But the package metadata lists `networkx`
  only under extras (`network`, `all`, ...). Pinning `networkx==3.7` fixes it.
- **Mesa 3.5.1 deprecates `Model(seed=...)`** with a `FutureWarning` ("use `rng` instead"). The
  spikes use `rng=`.
- **The shortlist's API check passes.** `Model.run_for`, `run_until`, `schedule_event` and
  `schedule_recurring` all exist in 3.5.1, not only in a development version.
- **JuPedSim's `Hdf5TrajectoryWriter` is `None`** in this install, because `h5py` is not a
  declared dependency. Only the SQLite writer is available.

## Trial 1: a queue with a newcomer

**The scene:**
- ten people queue at a counter that serves one at a time;
- at 30 s a newcomer arrives beside position 3 and asks to join ahead of it.

### JuPedSim 1.4.2

| Route | What it does | Result | Code |
|---|---|---|---|
| built-in queue, **refuse** | newcomer switched into the queue journey | ✓ joins at the back | `jps_trial1_queue.py`, 95 lines for all four routes |
| built-in queue, **steer in** | newcomer under direct steering to the gap ahead of position 3 | ~ wedges beside the line at (3.19, 3.51); never enqueued, never served | same |
| built-in queue, **admit by switching** | positions ≥3 step out, the newcomer joins, they rejoin | ✗ newcomer ends at the back, both all at once and one by one | same |
| built-in queue, **admit by remove and re-add** | remove positions ≥3, add the newcomer, re-add them | ✗ removed ids stay listed and keep their slots; re-added agents are enqueued nearest first (P10, P9, NEW, P8, ...) | same |
| **own queue** on direct steering | the order is a Python list; each queuer is steered to the slot of its index | ✓ admit: the newcomer is in slot 3 at (3.6, 3.0) within 2 s and served at 60 s; refuse: at the back | `jps_trial1_ownqueue.py`, **47 lines** |

**The root cause.** `jps_probe_queue_switch.py` (27 lines) isolates it:
- `switch_agent_journey` does not remove an agent from a queue's `enqueued()` list;
- the agent walked 2 m away and stayed listed;
- the agents behind it did not move up;
- its entry went only when it was popped.

**What this means:**
- The built-in `NotifiableQueueStage` is **FIFO only**: people join at the back and leave at the
  front.
- Neither insertion ("admit") nor leaving mid-queue (giving up, being sent away) can be expressed
  with it.
- `[inference]` The stale entries look like a defect, not a design choice. I did not check
  JuPedSim's issue tracker.

**What "admit" and "refuse" take.** On the own-queue route, each is a single line:
`line.insert(k, newcomer)` and `line.append(newcomer)`. The queue logic around them is about
15 lines:
- a list;
- a timer that pops the head;
- one steering assignment per queuer per iteration.

In the own-queue run the minimum spacing stayed ≥0.795 m, and the people behind stepped back
to let the newcomer in.

### Mesa 3.5.1

`mesa_trial1_queue.py`, **69 lines**, which include trial 3's adapters and the determinism check.

**The scene:**
- the line is a list owned by the model;
- service is a random exponential time (mean 10 s), from the model's seeded rng;
- background arrivals join at random intervals;
- the newcomer is `schedule_event(at=30)`.

**Results:**
- **Admit** puts the newcomer at position 3; they are served at 61.95 s.
- **Refuse** puts them at position 12.
- **One decision point:** a `decider(situation) -> decision` function, called once.
- **Paired runs come free:** the admit and refuse runs draw the same random numbers in the same
  order, because the decision consumes no randomness. So the policies are compared on identical
  arrivals and service times.

### Comparison

| | JuPedSim | Mesa |
|---|---|---|
| Express the line | ✓ built-in, but FIFO only; or our own list | our own list (Mesa supplies nothing queue-specific) |
| Express the service | `pop(1)` on a timer in our loop | `schedule_event`, random service from `model.rng` |
| Express the attempt | spawn + direct steering | `schedule_event(at=30)` |
| Admit | ✗ built-in; ✓ own queue | ✓ |
| Refuse | ✓ built-in and own queue | ✓ |
| Code | 47 lines (own queue) | 69 lines (with adapters and determinism check) |

## Trial 2: a bus or train door

### JuPedSim (`jps_trial2_door.py`, 72 lines)

**The scene:**
- a platform and a vehicle interior, joined by one 1.0 m opening;
- 8 boarders in a waiting set; 8 alighters spawned inside at "arrival" (2 s);
- boarders are "seated" at an exit stage on the vehicle's back wall;
- a stall detector stops the run if nobody moves 5 cm in 10 s.

Seconds from arrival until everyone is through (one deterministic run each):

| Policy | CFS | Social force |
|---|---|---|
| alight first (boarders released at 13.7 / 13.9 s) | 22.1 | 27.0 |
| simultaneous, boarders waiting beside the door | 30.0 | 54.3 |
| simultaneous, boarders waiting in front of the door | 35.2 | 56.0 |

**What worked:**
- waiting (waiting set);
- release (`state = WaitingSetState.INACTIVE`);
- two-way flow through one door: built-in geometry and journeys, with routing through the door
  done by JuPedSim.

**What was missing:**
- **Deadlock:** none in any of the six runs.
- **No vehicle object.** "Arrival" is a scripted spawn. Capacity and dwell time would be a
  counter and a timer in our loop.

### Mesa (`mesa_trial2_door.py`, 37 lines)

**The scene:**
- the door is a capacity-one resource with a line on each side;
- a priority rule picks the side each time the door frees;
- **alight first:** 17.8 s median (16.2 to 19.0, 30 seeds);
- **random side:** 26.7 s (19.2 to 31.5).

**The difference is assumed, not found.** The 1.0 s passage and the 1.5 s cost of a change of
direction are inputs. In a discrete model the cost of the door conflict must be given; it cannot
emerge from motion as it does in JuPedSim. What this trial shows is that the discrete form of a
boarding rule ("alighters first") is expressible, as a priority function of a few lines.

### SUMO: not tried

The shortlist made SUMO conditional: try it only if JuPedSim's door lacked what a vehicle model
provides (arrival times, capacity, dwell time). It does lack them, but each is a timer or a counter
in our loop, and the door conflict itself runs in JuPedSim. `[inference]` SUMO would add value
only for a network-level scenario, with timetables, several vehicles and routes.

## Trial 3: the two adapters, in miniature

### JuPedSim (`jps_trial3_adapters.py`, 83 lines)

**The scene:**
- 40 agents in a corridor;
- a perception pass after every iteration;
- four actions at 5 s;
- run under CFS and under social force.

**Perception** (read every agent's position, velocity and place in a queue): ✓.

| Field | How | Note |
|---|---|---|
| position | `agent.position` | |
| velocity | CFS: difference of positions; social force: `agent.model.velocity` | the two agree to 1.8e-13 m/s over 59,642 samples |
| place in a queue | built-in: `enqueued()`; own queue: the list index | the built-in list goes stale (trial 1) |

**Action** (change one agent's target or route mid-run): ✓. Effect delay, CFS / social force:

| Action | CFS | Social force |
|---|---|---|
| A. `agent.target` on an agent whose journey is not direct steering | **silently ignored**: the run is bit-identical to one with no action, and no error is raised | the same |
| B. `switch_agent_journey` to an exit at the other end | +1 iteration (0.01 s) | 0.33 s |
| C. `model.desired_speed` 1.2 → 0.4 | +0.01 s | 1.5 s |
| D. new target on a direct-steering agent | +0.01 s | 0.16 s |

**What the delays mean.** The social-force delays come from the model's reaction time, not from
the API.

**Row A is a trap for an action adapter.** A decision sent the wrong way is dropped without a
trace. The adapter has to know each agent's journey type, and log a decision as applied only when
the simulator accepts it.

**Per-step callback:** none, as the desk survey found. The adapters live in our loop around
`iterate()`.

### Mesa (in `mesa_trial1_queue.py`)

**Perception** is `situation()`. It returns a plain dict:
- the conflict type;
- the queue order;
- each person's time waited;
- each person's features (age).

**Action** is `apply(decision)`. It inserts or appends.

**Where the decision is applied:**
- **Inside a scheduled event:** at 30.0 s, the moment of arrival.
- **Inside `Model.step()`** (with `--in-step`): at 31.0 s. `step()` runs every 1.0 time unit,
  so a decision there can wait up to one unit. Otherwise the same.

**A gotcha (found in trial 4).** Mesa holds scheduled callbacks by **weak reference**, and
`schedule_event` passes no arguments. So a lambda or `functools.partial` is collected at once
and raises "function must be alive at Event creation". The callback must be a bound method of a
live object.

## Trial 4: scale

### JuPedSim (`jps_trial4_scale.py`, 50 lines)

**Method:**
- CFS, dt 0.01 s;
- a fresh `Simulation` per repetition;
- 10 warm-up iterations, then 100 timed iterations (= 1 simulated second);
- median of 3 repetitions;
- a corridor 30 m wide, with agents on a grid.

| Scene | N | ms per iteration | s per simulated s | Perception pass (Python) |
|---|---|---|---|---|
| one-way, ~0.5 /m², batch 1 | 1,000 | 3.06 | 0.31 | 3.24 ms |
| | 10,000 | 38.58 (min 32.03) | 3.86 | 33.94 ms |
| one-way, ~0.5 /m², batch 2 | 1,000 | 2.89 | 0.29 | 3.26 ms |
| | 10,000 | 29.58 | 2.96 | 32.01 ms |
| two-way, ~1 /m² | 1,000 | 3.95 | 0.40 | 3.32 ms |
| | 10,000 | 40.77 | 4.08 | 31.88 ms |

**Batch variation.** The two one-way batches differ by about 25 % at 10,000; both are reported.

**Against negsim** (one run):
- **The scene:** the two-way 10,000 scene, run for negsim's timed span of 10 simulated
  seconds.
- **JuPedSim:** **46.9 s of computing** (4.2 to 5.6 s per simulated second), i.e.
  **0.21 simulated seconds per computing second**.
- **negsim:** 0.062 to 0.073 under plain ORCA, on the same laptop model: two runs of its
  benchmark, 1,602 and 1,364 ms mean per 0.1 s step (`WORK_LOG-26.md`, 2026-10-14 benchmark
  table).
- **About 2.9 to 3.4× faster** `[inference]`. The scenes are similar, not the same, and neither run
  has a rule layer.

**The perception pass costs as much as an iteration** (about 32 ms at 10,000, reading every
agent from Python). A perception adapter should therefore run every 10th iteration (0.1 s,
negsim's step), not every iteration.

### Mesa (`mesa_trial4_scale.py`, 80 lines)

**Two set-ups:**
- **(a) event-driven:** N people arrive and queue at 10 counters;
- **(b) step-based:** each of N agents reads its place and calls a decider on every step.

Median of 3:

| N | (a) µs per event | (a) whole run | (b) ms per step, place stored | (b) ms per step, `list.index` |
|---|---|---|---|---|
| 1,000 | 15.8 | 0.032 s (2,000 events) | 1.14 | 2.12 |
| 10,000 | 15.5 | 0.310 s (20,000 events) | 13.99 | 104.49 |

**What the numbers show:**
- **Events:** the cost per event does not grow with N.
- **Steps:** a step pass grows linearly with N.
- **Queue places:** looking a place up with `list.index` is quadratic, so the perception adapter
  must store queue places, not search for them.

**My dead end, logged.** The first attempt called `run_until(1e9)`. That also fires Mesa's
default `step()` every time unit, a billion no-op steps; it ran past ten minutes and was
stopped.

### Sleep check

- **Kernel-Power events:** no 506, 507, 42 or 107 events in the System log between 21:00 and
  the last timing (22:43:33).
- **Power:** the laptop was on AC power before and after.

## Determinism

| | Result | How checked |
|---|---|---|
| JuPedSim | ✓ identical trajectories, bit for bit, in one process and across two processes (digest `5e3a375fa04a`), CFS and social force | SHA-256 of every position at every iteration, keyed by spawn index |
| Mesa | ✓ the same seed gives the same event log; another seed gives a different one | log comparison in `mesa_trial1_queue.py` |

**Two JuPedSim notes:**
- **No seed exists, and none is needed** for a scene without randomness. `Simulation` takes no
  seed; the `distribute_*` helpers do.
- **Agent, journey and stage ids come from a process-wide counter.** A second `Simulation` in
  the same process starts at agent id 4, not 1. Comparing runs by id fails; compare by spawn
  order. My first determinism check failed for exactly this reason.

## Logging (`logging_probe.py`)

**JuPedSim**, `SqliteTrajectoryWriter`:
- **Tables:** `trajectory_data` (`frame, id, pos_x, pos_y, ori_x, ori_y`), `frame_data`,
  `geometry` (WKT) and `metadata`.
- **Not recorded:** velocity, stage, journey, queue state or events.
- **Short runs are lost without `writer.close()`.** The writer commits every 100 writes by
  default. The first probe run wrote 20 frames and got 0 rows.

**Mesa**, `DataCollector`:
- **What it gives:** model- and agent-level reporters (any function), as pandas DataFrames
  indexed by step and agent;
- **Logging module:** `mesa.mesa_logging`, for debug logs.

**In both**, a log of conflict events (who asked, who decided, what was applied) is ours to
write. negsim already has one (`llm_negotiation/docs/log-schema.md`).

## Summary of what each simulator can do

| | JuPedSim 1.4.2 | Mesa 3.5.1 |
|---|---|---|
| Queue with admit / refuse | refuse ✓; admit ✗ with the built-in queue, ✓ with our own list on direct steering | ✓ (our own list) |
| Door, two-way, waiting and release | ✓ built-in; cost emerges from motion | ✓ as a resource; cost is an input |
| Perception hook | ✓ in our loop; velocity by difference under CFS | ✓ plain Python |
| Action hook | ✓; `target` ignored silently outside direct steering | ✓ in an event or in `step()` |
| Same seed → same result | ✓ (no seed needed) | ✓ |
| 10,000 agents | 0.21 simulated s per computing s (two-way) | 15.5 µs per event; 14 ms per step |
| Logging | positions and orientations to SQLite (call `close()`) | DataCollector |
| Surprises | stale queue entries; silent `target`; process-wide ids | missing `networkx` dependency; `seed=` deprecated; weakly held callbacks |
