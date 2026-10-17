# A beginner's guide to this code

This guide explains, in plain words, what every part of this repository does and how the
parts fit together. It assumes you know a little Python (what a function, a dictionary and
a file are) and nothing about crowd simulation or language models.

Every example in it was run on 2026-10-16, and all of them again on 2026-10-17 after issue
#32 (the earlier ones still print exactly the same), and the output printed under each is what
came out. To run one yourself, save the code as a file **inside the `llm_negotiation` folder** (for
example `llm_negotiation/try_it.py`), open a terminal in that folder, and type
`python try_it.py`.

**Contents**

1. [The whole project in one picture](#1-the-whole-project-in-one-picture)
2. [Five ideas you need first](#2-five-ideas-you-need-first)
3. [Where everything is](#3-where-everything-is)
4. [Layer 0: dots that move (the core)](#4-layer-0-dots-that-move-the-core)
5. [Layer 1: two people who talk before they walk (issue #24)](#5-layer-1-two-people-who-talk-before-they-walk-issue-24)
6. [Layer 2: a crowd that steps around each other (issue #26)](#6-layer-2-a-crowd-that-steps-around-each-other-issue-26)
7. [Layer 3: rules written down as data (issue #28)](#7-layer-3-rules-written-down-as-data-issue-28)
8. [Layer 4: language models that write new rules (issue #30)](#8-layer-4-language-models-that-write-new-rules-issue-30)
9. [Across the layers: fictional groups and meetings inside a passage (issue #32)](#9-across-the-layers-fictional-groups-and-meetings-inside-a-passage-issue-32)
10. [Talking to DeepSeek safely: the LLM layer](#10-talking-to-deepseek-safely-the-llm-layer)
11. [Experiments, logs and watching a run](#11-experiments-logs-and-watching-a-run)
12. [Tests: how you know it works](#12-tests-how-you-know-it-works)
13. [Phase 1: the dataset pipeline (retired)](#13-phase-1-the-dataset-pipeline-retired)
14. [Follow one run from start to finish](#14-follow-one-run-from-start-to-finish)
15. [Glossary](#15-glossary)
16. [Where to read more](#16-where-to-read-more)

---

## 1. The whole project in one picture

**The question behind the project:** when two people (or two hundred) are about to get in
each other's way, how do they sort it out? And can a large language model (an LLM, such as
DeepSeek) describe or invent sensible ways of sorting it out, which a crowd simulation could
then use?

The code was built in stages. Each stage is a GitHub issue, and each one adds a layer on top
of the one before:

```
  Phase 1 (finished, retired)
  ────────────────────────────
  pipeline/  ──asks DeepSeek──>  dataset/generated/   140 descriptions of how people behave
                                                      (by scenario, age group and gender)

  Phase 2: llm_negotiation/  (the simulator; everything below lives in llm_negotiation/negsim/)
  ────────────────────────────────────────────────────────────────────────────────────────
  Across   issue #32               a fictional GROUP no rule may read; BACKING OUT of a passage
  Layer 4  issue #30  rulegen/     LLMs turn a conflict into a new RULE, which is then tested
  Layer 3  issue #28  rules/       RULES stored as data tell the avoidance layer what to do
  Layer 2  issue #26  avoidance/   a CROWD of agents steps around each other (ORCA)
  Layer 1  issue #24  negotiation/ TWO agents talk through an LLM, then one goes first
  Layer 0             core/        agents are discs that move, one time step at a time
```

Issue #32 does not add a layer of its own. It adds two things that run through several layers
at once (section 9).

You can read the guide top to bottom: each section only needs the ones before it.

## 2. Five ideas you need first

**1. An agent is a moving disc.** Every person in the simulation is a circle on a flat floor,
seen from above. A circle of radius 0.25 m is a body 50 cm wide. It has a position
`(x, y)` in metres, a direction it faces, and a velocity: which way it is walking and how
fast, in metres per second (m/s). 1.3 m/s is a normal walking speed.

**2. Time moves in small steps.** The simulation does not run continuously. It jumps forward
`dt = 0.1` seconds at a time. On every step, every agent decides how to move, and then all of
them move at once. A 30-second run is 300 steps.

**3. A scenario is a map plus a job for each agent.** Where the walls are, where each agent
starts, and where it is trying to go. Examples: a doorway, a narrow hallway only one person
fits through, a wide corridor, two crowds walking through each other.

**4. A run is one simulation; an experiment is many runs.** An experiment is described by a
config file (YAML, an easy-to-read text format). The config can say "try every combination
of these settings, 20 times each", and the code turns that into a list of runs.

**5. Everything is logged.** Every run writes a folder of files: where every agent was on
every step, what every agent said, what went wrong. Nothing is thrown away. Later stages
(and your report) read these folders.

## 3. Where everything is

At the top of the repository:

| Folder or file | What it holds |
|---|---|
| `README.md` | The project's status page: what each roadmap step is and how far it got |
| `CLAUDE.md` | Instructions for the AI assistant working in this repository |
| `WORK_LOG-<n>.md` | A diary of how each issue was done, decisions and mistakes included |
| `literature/` | Literature reviews (no code) |
| `refs/` | Saved copies of papers and web pages the code and documents cite |
| `pipeline/`, `dataset/` | Phase 1: the dataset generator and its output (section 13) |
| `integration/` | How this work maps onto CrowdGym, the senior's project |
| `llm_negotiation/` | **Phase 2: the simulator.** Almost all the code |

Inside `llm_negotiation/`:

| Folder or file | What it holds |
|---|---|
| `run_experiment.py` | The one command that runs any experiment |
| `ruledb.py` | A command to list and check the stored rules |
| `configs/` | Every YAML config: scenarios, experiments, baselines, cases, prices |
| `negsim/` | The Python package: the actual code (below) |
| `rule_db/` | The rule database: one file per rule version, plus a "fingerprint" list |
| `cases/` | Frozen conflicts that LLMs write rules from: 18 (issue #30), a second version of each, and 8 meetings inside a passage (issue #32) |
| `runs/` | Logs of experiments that are kept (committed to git) |
| `runs_mock/` | Logs of free practice runs (git ignores this folder) |
| `views/` | Animated viewer pages you have generated (git ignores this too) |
| `docs/` | Detailed documents, one per topic |
| `tests/` | About 1,380 automatic tests |
| `spend_ledger.jsonl` | One line for every paid call to DeepSeek, with its cost |

Inside `llm_negotiation/negsim/` (the package), one folder per job:

| Folder | Job | Layer |
|---|---|---|
| `core/` | agents, the world, motion, geometry | 0 |
| `scenarios/` | building maps and starting positions from YAML | 0 |
| `conflict/`, `control/` | finding where two paths clash; who goes first; speed limits | 1 |
| `negotiation/` | the conversation between two agents; prompt templates | 1 |
| `personas/` | who an agent is: age, gender, perhaps a fictional group (never a name) | 1 |
| `avoidance/` | ORCA, perception, directives, the crowd simulation | 2 |
| `metrics/` | measuring what happened: collisions, near misses, yields | 2 |
| `rules/` | the rule format, the rule database, matching rules to pairs | 3 |
| `rulegen/` | turning conflicts into new rules with LLMs | 4 |
| `llm/` | talking to DeepSeek (or a free stand-in), prices, the budget | all |
| `experiment/` | reading configs, running experiments, the command line | all |
| `runlog/` | what files a run writes, and checking them | all |
| `viz/` | the animated viewer, plots, readable transcripts | all |

## 4. Layer 0: dots that move (the core)

**Files:** `negsim/core/` (`state.py`, `agent.py`, `world.py`, `dynamics.py`, `geometry.py`)
and `negsim/scenarios/`.

- `AgentSpec` (in `agent.py`) is everything about an agent that never changes during a run:
  its radius, its top speed, where it starts, its goal, and its **desired path** (a line of
  points to follow, called a polyline).
- `AgentRuntime` is what does change: its current pose (position and heading), its speed,
  whether it has arrived.
- `World` (in `world.py`) holds all the agents, the walls, and the clock.
- `dynamics.py` turns a command into motion. There are two models:
  - the **unicycle** (used by the two-agent scenarios of issue #24): the command is "walk
    at speed `v` and turn at rate `omega`", like steering a bicycle;
  - the **holonomic** model (used by the crowd, issue #26): the command is simply a velocity
    arrow `(vx, vy)`; the agent can step in any direction.

**Example 1: one agent walks for three time steps.**

```python
from negsim.core.dynamics import unicycle_step
from negsim.core.state import Control, Pose

pose = Pose(x=0.0, y=0.0, theta=0.0)           # standing at the origin, facing east
control = Control(v=1.3, omega=0.0)            # walk at 1.3 m/s, do not turn
for step in range(3):
    pose = unicycle_step(pose, control, dt=0.1)  # one time step of 0.1 s
    print(f"after step {step + 1}: x = {pose.x:.2f} m, y = {pose.y:.2f} m")
```

```
after step 1: x = 0.13 m, y = 0.00 m
after step 2: x = 0.26 m, y = 0.00 m
after step 3: x = 0.39 m, y = 0.00 m
```

1.3 m/s for 0.1 s is 0.13 m, so each step moves the agent 13 cm. That is all "motion" is:
`new position = old position + velocity × dt`, repeated.

**Scenarios** are built from YAML files in `configs/scenarios/`. For example
`hallway.yaml` says the hallway is 4 m long and 0.8 m wide (too narrow for two 0.5 m bodies
side by side) and that both agents walk at up to 1.3 m/s. `negsim/scenarios/hallway.py` reads
those numbers and works out the walls, the start points and the paths. The registry
(`scenarios/registry.py`) picks the right builder from the file's `type:` line. Many numbers
in these files are marked `[placeholder]`: round, plausible values not yet taken from a source.

## 5. Layer 1: two people who talk before they walk (issue #24)

This layer re-builds **GameChat**, a published method (Mahadevan et al., 2025): when two
robots are about to clash, they talk through an LLM about who should go first.

### The situation

Two agents walk towards a place only one can use at a time, such as a doorway or the
narrow hallway. `negsim/conflict/` finds the **conflict zone**: the stretch of each path
where the two would touch if both were in it at once. One agent must be the **leader** (goes
first, full speed) and the other the **follower** (slows down so it arrives just as the
leader has left).

### The conversation

As soon as the two can see each other, they talk (`negsim/negotiation/protocol.py`). Each
agent has its own **system prompt**, a text telling the LLM who it is (for example "You are
taking someone to the emergency room"). Then they take turns. On each turn the LLM must reply
with a small piece of JSON:

```json
{"message": "what I say to the other agent", "stance": "I_GO_FIRST"}
```

`stance` is one of `I_GO_FIRST`, `YOU_GO_FIRST` or `UNDECIDED`. Only `message` is passed to
the other agent. The stance is the agent's private position.

**They have agreed** (`negotiation/consensus.py`) when, on two turns in a row, one says
`I_GO_FIRST` and the other says `YOU_GO_FIRST`. If four messages each go by without that, they
have not agreed, and a fixed fallback rule decides instead: **Strategy 1**, "whoever would reach
the conflict zone sooner goes first".

**A real conversation.** This is from a paid DeepSeek run of 2026-10-13
(`runs/c1_smoke/001_hospital-vs-airport_fs0/transcript.md`), in a doorway:

| Turn | Speaker | Said | Stance |
|---|---|---|---|
| 1 | agent 0 (emergency room) | "I am taking someone to the emergency room. What is your task and destination?" | UNDECIDED |
| 2 | agent 1 (airport) | "I am taking someone to the airport. What is your destination?" | YOU_GO_FIRST |
| 3 | agent 0 | "I am taking someone to the emergency room. Medical emergencies have priority over airport trips. I go first." | I_GO_FIRST |

Turns 2 and 3 are complementary, so they agreed after 3 turns: agent 0 leads. In the
simulation, agent 0 then went through the doorway first.

### The follower's speed limit

Once the leader is chosen, `negsim/control/strategy1.py` limits the follower's speed so that it
reaches the conflict zone exactly when the leader has completely left it.

**Example 2: how slowly must the follower walk?**

```python
from negsim.control.strategy1 import follower_speed_bound

# The leader is 1 m from the hallway entrance, walks 1.3 m/s, and its body is 0.5 m long.
# The hallway is 4 m long. The follower is 2 m from the entrance.
limit = follower_speed_bound(d_i=2.0, d_j=1.0, v_j=1.3, l_j=0.5, L=4.0, v_i_max=1.3)
print(f"the follower may walk at most {limit:.2f} m/s")
print(f"the leader is out of the hallway after {(1.0 + 4.0 + 0.5) / 1.3:.2f} s")
print(f"at {limit:.2f} m/s the follower reaches the entrance after {2.0 / limit:.2f} s")
```

```
the follower may walk at most 0.47 m/s
the leader is out of the hallway after 4.23 s
at 0.47 m/s the follower reaches the entrance after 4.23 s
```

The leader has 1 + 4 + 0.5 = 5.5 m to go before its back has left the hallway, which takes
4.23 s. The follower is 2 m away, so 2 / 4.23 = 0.47 m/s gets it there at the same moment.

### Two more pieces

- **Prompt templates are frozen** (`negsim/negotiation/templates/`). All wording an LLM ever
  sees is in YAML files, and a "fingerprint" of each (a SHA-256 hash, see the glossary) is
  stored in `MANIFEST.json`. If anyone edits a template, the fingerprint no longer matches and
  the code refuses to load it. New wording means a new version (`_v2`). So nobody can quietly
  tune a prompt. Issue #32 did exactly that for the rule-generation prompts (section 9).
- **Personas** (`negsim/personas/`) give an agent an age, a gender and so on, from
  `configs/personas/personas.yaml`. The loader refuses anything that looks like a personal
  name. An experiment decides which attributes the other agent may see. Since issue #32 a
  persona may also belong to a fictional group (section 9).

**Try it** (free, using the stand-in model described in section 10):

```
python run_experiment.py configs/experiments/c1_smoke.yaml --client mock
python -m negsim.viz.viewer runs_mock\c1_smoke
```

## 6. Layer 2: a crowd that steps around each other (issue #26)

Layer 1 only handles two agents and one narrow place. Real crowds are many people stepping
around each other in open space. For that the project uses **ORCA** ("Optimal Reciprocal
Collision Avoidance", van den Berg et al.), a well-known method for crowds and robots.

### ORCA in plain words

On every time step, each agent does this, for each neighbour it can see:

1. **"Which velocities would make me bump into you soon?"** It works out every velocity that
   would bring the two bodies into contact within the next 3 seconds. That set is called the
   **velocity obstacle**. If its current velocity is inside it, the two are on a
   **collision course**.
2. **"I will do my share of the dodging."** The change needed to get out of the velocity
   obstacle is split between the two. In standard ORCA each does half (its
   **responsibility share** is 0.5). The agent turns this into a rule of the form "my velocity
   must be on this side of this line". That is a **half-plane**.
3. **"Of everything still allowed, what is closest to what I want?"** Each agent wants to walk
   along its path at its preferred speed. A small optimisation, a **linear program**
   (`avoidance/lp.py`), picks the allowed velocity closest to that wish.

Because both agents follow the same recipe and each does its share, the pair is guaranteed to
miss, as long as the maths has a solution. In a very dense crowd it sometimes has none.
Then a fallback picks the velocity that breaks the rules least, and bodies can overlap
(see "Collisions" below).

**Example 3: two people walking straight at each other.**

```python
from negsim.avoidance.lp import solve
from negsim.avoidance.orca import agent_half_plane

# Person A walks east at 1.3 m/s. Person B is 4 m ahead, walking west at 1.3 m/s.
# Both bodies have a radius of 0.25 m, so their centres must stay 0.5 m apart.
for side in (None, "left"):
    half_plane = agent_half_plane(
        rel_pos=(4.0, 0.0),        # where B is, seen from A
        rel_vel=(2.6, 0.0),        # A's velocity minus B's velocity
        own_velocity=(1.3, 0.0),   # A's velocity now
        combined_radius=0.5,       # 0.25 + 0.25
        tau=3.0,                   # look 3 s ahead
        dt=0.1,
        share=0.5,                 # A does half of the avoiding
        side=side,                 # None: plain ORCA; "left": a rule says pass on the left
    )
    chosen = solve([half_plane.line], n_hard=0, max_speed=2.0, preferred=(1.3, 0.0))
    vx, vy = chosen.velocity
    print(f"side={side}: collision course={half_plane.on_collision_course}, boundary={half_plane.region}, "
          f"A walks with vx={vx:.3f} m/s, vy={vy:.3f} m/s")
```

```
side=None: collision course=True, boundary=apex, A walks with vx=0.583 m/s, vy=0.000 m/s
side=left: collision course=True, boundary=left_leg, A walks with vx=1.280 m/s, vy=0.161 m/s
```

Read it like this:

- **Plain ORCA, exactly head-on:** the situation is perfectly symmetric. Going left and going
  right are equally good, so ORCA picks neither. A just slows down (from 1.3 to 0.58 m/s)
  and keeps walking straight. B does the same. They creep towards each other: this is the
  famous **symmetric deadlock**.
- **With a "pass on the left" instruction:** A keeps almost its full speed (1.28 m/s) and
  drifts to its left (`vy` is positive, and left of east is north). B gets the same
  instruction and drifts to *its* left, so they pass. One small instruction breaks the tie.
  That is why layers 3 and 4 exist: rules are instructions of exactly this kind.

In the real simulation a tiny random nudge (the **perturbed baseline**, see section 7) also
breaks exact ties, but then *which* way they pass is down to chance.

### What an agent can see: the perception record

When a neighbour comes within an agent's sensing radius (12.5 m in the shipped scenarios),
the agent builds a **perception record** (`avoidance/perception.py`): what it can tell about
that neighbour. These values are from a real case, the moment two agents first saw each other
in the wide corridor:

```
distance_m             12.36       how far apart the two centres are
bearing_rad            -0.000002   which direction the other is in (0 = straight ahead)
neighbour_speed_mps    1.30        how fast the other walks
closing_speed_mps      2.60        how fast the gap is shrinking (1.3 + 1.3)
time_to_collision_s    4.56        when they would touch if nothing changed
neighbour_radius_m     0.25
pair: encounter_class "head_on", min_corridor_width_m 1.75, age_difference_years (hidden)
```

It holds only what one person could see of another: never the other's goal, path, or
errand. The `pair` part is the same whichever of the two computes it, which matters for rules
(section 7). Since issue #32 (record version 3) it also says, when the two are inside a
passage only one can use, how far each has walked in and how far each end is; and, only if the
experiment shows it, the other's fictional group (section 9).

### Directives: six knobs on ORCA

A **directive** (`avoidance/directives.py`) is an instruction one agent follows for one
neighbour. It has six knobs (the sixth came with issue #32). Leaving them all at their
defaults is plain ORCA:

| Knob | Default | What it does |
|---|---|---|
| `side_preference` | `none` | pass the other on the `left` or the `right` |
| `responsibility_share` | 0.5 | how much of the dodging this agent does (1.0 = all of it) |
| `speed_scale` | 1.0 | multiply walking speed (0.5 = half speed) |
| `clearance_margin` | 0 m | keep this much extra room between the two bodies |
| `passage_order` | `none` | at a single-file stretch, go first (`leader`) or wait (`follower`) |
| `back_up` | `false` | inside a single-file stretch the two have met in: back out, wait for the other, go on (section 9) |

Where directives come from is swappable: written in a config (issue #26), or chosen by stored
rules (issue #28). The two agents' directives are checked against each other
(`resolve_pair`): for example, if their shares add up to less than 1, ORCA's guarantee would
fail, so this is recorded as a **reciprocity violation** and repaired.

### One step of the crowd, in order

`avoidance/simulation.py` runs this loop on every step, for every agent still walking:

1. **Perceive** the nearest neighbours in range; a new neighbour gets a perception record and
   a directive.
2. **Resolve** each pair's two directives into one consistent pair.
3. **Coordinate:** if the two are heading into a single-file stretch, hand them to the
   **arbiter** from layer 1, which picks who goes first. If they are already inside one and a
   directive says `back_up`, start a **back-up manoeuvre** instead, and the arbiter lets go of
   the pair (section 9).
4. **Choose a velocity:** ORCA half-planes for every wall and neighbour, then the linear
   program.
5. **Move** everyone at once.

Then the bookkeeping: arrivals, collisions, near misses, yields, deadlocks.

### Collisions, and what "2.3 cm deep" means

Bodies in this model cannot push each other: nothing physical happens when two discs touch.
ORCA only *chooses velocities* to avoid touching. A **collision** is recorded whenever two
discs overlap (their centres are closer than the sum of their radii), and its **depth** is
how far they overlap. "Deepest 2.3 cm" means that at the worst moment, two people's centres
were 47.7 cm apart instead of at least 50 cm. In a real crowd that would be shoulders
brushing; it is counted as a failure of avoidance, not as something physical. The metrics
are in `negsim/metrics/avoidance.py`.

### The crowd scenario

`bidirectional_flow` puts 50 people at each end of a 4 m by 50 m corridor and has them walk
through each other. By default they start on a neat grid (1 m apart, nudged up to 10 cm). Set
`spawn_pattern: random` and each group is scattered at random over the same area, no two closer
than 0.6 m (added on 2026-10-16, at the end of issue #30). Starting from random places, plain
ORCA collides far more often than from the grid (354 collision episodes against 75, in one
run each).

## 7. Layer 3: rules written down as data (issue #28)

In layer 2, directives came from configs typed by hand. Layer 3 stores **rules**: reusable
"when this happens, do that" instructions, written as data, not as code. A rule can never run
code, which makes it safe for an LLM to write one later.

### What a rule looks like

This is `rule_db/rules/keep_left_head_on.v1.yaml`, without its comments and provenance:

```yaml
rule_id: keep_left_head_on
version: 1
status: test_seed
encounter: head_on                     # 1. what kind of meeting it is for
when:                                  # 2. when it applies
  all:
    - {field: pair.min_corridor_width_m, op: ">=", value: 1.0, unit: m}
roles: symmetric                       # 3. both people get the same instruction...
directive:
  both: {side_preference: left}        # 4. ...which is: pass on the left
priority: 10                           # 5. if two rules match, the higher number wins
```

In words: *"When two people meet head-on in a passage at least 1 m wide, both pass on their
left."*

Rules can also give the two people **different roles**. This is
`younger_yields_head_on`:

```yaml
encounter: head_on
when:
  all:
    - {field: pair.time_to_collision_s, op: "<=", value: 6.0, unit: s}
    - {field: pair.age_difference_years, op: ">=", value: 20, unit: years}
roles:
  by: {field: agent.age, order: ascending, assign: [yielder, other], tie: no_match}
directive:
  yielder: {responsibility_share: 1.0}   # the younger one does all the dodging
  other: {responsibility_share: 0.0}     # the older one does none
priority: 20
```

In words: *"When two people meet head-on, will touch within 6 s, and are at least 20 years
apart in age, the younger one does all the avoiding."* `roles: by` sorts the two by a number
(here age, smallest first), and gives the first role to the first person. `tie: no_match`
means that if their ages are equal, the rule does not apply.

**Why so strict?** A rule may only read fields that *both* people can see and would compute the
same way (`rules/fields.py`): the distance between them, their speeds, the corridor width, and
ages and genders when those are visible. A rule that reads someone's errand ("whoever is going
to the hospital") is **refused**: only that person knows it, so the other could not follow the
rule without asking. The loader also refuses rules that would break ORCA: shares adding up to
less than 1, or the two people told to pass on opposite sides. And since issue #32 a rule may
never read a person's fictional group, even when both can see it (section 9).

All six stored rules are **test seeds**: written by hand to exercise the machinery, not claims
about how people really behave. The sixth, `passage_shorter_backs_out`, came with issue #32.

### The rule database

`rule_db/` is like a small library:

- `rules/<rule_id>.v<version>.yaml`: one file per version of each rule. **A version is never
  edited.** A change is a new file with the next version number.
- `MANIFEST.json`: the fingerprint (SHA-256) of every file. If a file is edited, its
  fingerprint no longer matches and loading fails.
- `rulesets/default.yaml`: a named set of rule versions to switch on together.
- `schema/`: the rule format itself, in versions 1, 2 and 3, each frozen. Every rule says which
  version it is written in. Version 3 (issue #32) added `back_up`, true-or-false values and the
  passage fields; rules of versions 1 and 2 load exactly as before.

```
python ruledb.py list
```

```
rule                               status     encounter            priority expiry       source       created    rule sets
keep_left_head_on@1                test_seed  head_on                    10 passed       hand_written 2026-10-14 default
keep_right_head_on@1               test_seed  head_on                    10 passed       hand_written 2026-10-14 -
overtaker_keeps_clear@1            test_seed  overtaking                 10 passed       hand_written 2026-10-14 default
passage_shorter_backs_out@1        test_seed  single_file_segment        30 out_of_range hand_written 2026-10-16 -
single_file_first_arrival@1        test_seed  single_file_segment        10 out_of_range hand_written 2026-10-14 default
younger_yields_head_on@1           test_seed  head_on                    20 passed       hand_written 2026-10-14 default

rule set default: keep_left_head_on@1, overtaker_keeps_clear@1, single_file_first_arrival@1, younger_yields_head_on@1
cannot be switched on together: keep_left_head_on@1 and keep_right_head_on@1 are both priority 10 and both match the situation (pair.encounter_class='head_on', pair.min_corridor_width_m=1) with different directives
```

### Matching: which rule does a pair follow?

`rules/matching.py` decides, pair by pair:

- The rules are checked **once for the pair**, on one shared set of values (a **snapshot**),
  and each person gets the instruction for their role.
- **The highest priority wins.** Two rules at the same priority that would tell the pair
  different things are refused before the run starts: that is why `keep_left_head_on` and
  `keep_right_head_on` cannot both be on.
- **A match holds** until the encounter has passed (the two are moving apart and clear of each
  other). Then the pair goes back to plain ORCA.
- **No rule matches?** The pair simply follows plain ORCA.

### "Plain ORCA", frozen

To say "a rule helped", you need something fixed to compare with. `configs/baselines/` holds
two frozen definitions of "plain ORCA": `orca_perturbed_v1` (the main one), which adds a
tiny random nudge of 0.0001 m/s to break exact ties, as the reference ORCA library does; and
`orca_unperturbed_v1`, which does not.

### An experiment that compares two rules

`configs/rule_following/si2_keep_left_vs_right.yaml`, shortened:

```yaml
layer: avoidance
experiment_name: si2_keep_left_vs_right
scenario: configs/scenarios/wide_corridor_head_on.yaml
design:
  seed: 28200
  repeats: 20
  factors:
    baseline:
      - name: perturbed
        baseline: orca_perturbed_v1
      - name: unperturbed
        baseline: orca_unperturbed_v1
    rule:
      - name: keep_left
        directives: {provider: rules, enable: {keep_left_head_on: 1}}
      - name: keep_right
        directives: {provider: rules, enable: {keep_right_head_on: 1}}
```

The **design** has two **factors** of two **levels** each, so 2 × 2 = 4 combinations, each
repeated 20 times with different seeds: 80 runs. One command runs all of them:
`python run_experiment.py configs/rule_following/si2_keep_left_vs_right.yaml`.

## 8. Layer 4: language models that write new rules (issue #30)

Layer 3 follows rules a person wrote. Layer 4 asks: **can LLMs write them?** And does a rule
that two LLM agents *negotiate* differ from one a single LLM simply *states*?

The whole pipeline, which lives in `negsim/rulegen/`:

```
 a conflict from a finished run      cases.py      frozen as a "case"
          │
 two people put into it              design.py     a "session": ages, genders, errands
          │
 the situation in words              describe.py   first-person (A) or third-person (B)
          │
     ┌────┴─────────────────┐
 condition A: negotiate     condition B: state       protocol.py
 two LLM agents take turns  one LLM, one reply
     └────┬─────────────────┘
          │
 every proposed rule gets a category   validate.py
          │
 valid rules stored in an "inbox"      writer.py     (never in rule_db/ directly)
          │
 each rule tested alone                replay.py     on its own conflict, and in a crowd
          │
 a report                              experiment.py
```

### Cases: conflicts frozen as data

A **case** (`rulegen/cases.py`, files in `cases/`) is one moment from a finished run of plain
ORCA: two agents, at the instant they first saw each other, with everything each could
perceive. There are 18, from five scenarios; issue #32 gave each a second version and added 8
more (section 9). Each case is graded by a **severity tier**:

| Tier | Means |
|---|---|
| T0 | they were near each other, nothing more |
| T1 | they were on a collision course for a while |
| T2 | one of them slowed right down (a yield) |
| T3 | they passed closer than 10 cm (a near miss) |
| T4 | they collided, or got stuck for good |

Like rules, cases are frozen with fingerprints, so a case can never change after rules have
been generated from it.

### Sessions: who the two people are

A **session** (`rulegen/design.py`) puts two people into a case. Their age (25 or 70),
gender, and errand (urgent: "the emergency room"; routine: "the supermarket"; or none) are
varied systematically, as is whether age and gender are shown at all (a control: does the
LLM use them only because it was told them?). No names, ever. Since issue #32 a session may
also give each person a fictional group (section 9).

### What the LLM is told

`rulegen/describe.py` turns a case into text, using frozen templates. In **condition A**
each agent is told the situation from its own point of view, with its own errand only:

```
ABOUT YOU
- You are 70 years old.
- You are a woman.
- You are on your way to the emergency room.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- Your body is 0.50 m wide.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.

THE OTHER PERSON
- They are 12.4 m away, straight ahead of you.
- They are walking at 1.30 m/s, in the opposite direction to you, and the distance between you is shrinking.
- Their body is 0.50 m wide.
- They look about 25 years old.
- They look like a man.
- You do not know where they are going, unless they tell you.
```

After that comes the rule format and the list of fields a rule may use. In **condition B**
one LLM is told both people's details, including both errands, as "Person 1" and
"Person 2". The wording never hints at an answer (it never mentions keeping to a side). This
is prompt version 1; issue #32 froze a version 2 beside it (section 9).

### Condition A: two agents negotiate

Each turn is JSON with four keys:

```json
{"message": "...", "proposal": {a rule, or null}, "accept": "a proposal id, or null", "no_rule_possible": false}
```

Each proposed rule gets a **proposal id**: the first 12 characters of the fingerprint of what
the rule *does*. The two have **agreed** when one accepts the other's latest proposal by its id.
If an agent "accepts" but changes the rule, that counts as a new proposal, not an acceptance.

**Example 4: the same rule written differently has the same id.**

```python
from negsim.rules.canonical import proposal_id

keep_left = {"encounter": "head_on", "when": {"all": []}, "roles": "symmetric",
             "directive": {"both": {"side_preference": "left"}}, "priority": 10}
# The same rule, keys in another order, a different priority and a note: the same rule.
reordered = {"directive": {"both": {"side_preference": "left"}}, "roles": "symmetric",
             "when": {"all": []}, "encounter": "head_on", "priority": 50, "intent": "keep left"}
keep_right = {**keep_left, "directive": {"both": {"side_preference": "right"}}}

print("keep_left :", proposal_id(keep_left))
print("reordered :", proposal_id(reordered))
print("keep_right:", proposal_id(keep_right))
```

```
keep_left : 3cd1c2ec6fde
reordered : 3cd1c2ec6fde
keep_right: c2d34fda179f
```

The id ignores key order and anything that does not change behaviour (priority, notes), but
any real change (left to right) gives a different id. So "I accept 3cd1c2ec6fde" means
exactly one rule, however it was typed.

A negotiation ends when they agree, when both say no rule is possible without talking, when
they run out of messages (4 each), or when a reply cannot be read even after one retry.

### Condition B: one LLM states a rule

One call: the reply is `{"rule": ..., "reason": "..."}`. Each setting is repeated (3 times by
default) to measure **stability**: how often the LLM gives the same rule again.

### Every proposal gets a category

`rulegen/validate.py` checks every rule any LLM proposes. None is thrown away. Each gets
exactly one category:

| Category | Means |
|---|---|
| `valid` | it loads, and both people can see everything it reads |
| `needs_communication` | it reads private information (an errand), so it could only work if they talked |
| `inconsistent` | it breaks ORCA's guarantee (shares adding to less than 1, opposite sides), or, since issue #32, has both people back out |
| `schema_error` | it is malformed (unknown keys, wrong types, missing pieces) |
| `format_limit` | it asks for something the format cannot say (a share that grows with age) |
| `protected_attribute` | issue #32: it reads a person's fictional group, which no rule may (section 9) |

**Example 5: four proposals, four categories.**

```python
from negsim.avoidance.perception import default_visibility
from negsim.rulegen.validate import validate_proposal

base = {"encounter": "head_on", "when": {"all": []}, "roles": "symmetric", "priority": 100}
proposals = {
    "keep left": {**base, "directive": {"both": {"side_preference": "left"}}},
    "the one in a hurry goes first": {**base, "when": {"all": [
        {"field": "either.task", "op": "==", "value": "the emergency room"}]},
        "directive": {"both": {"side_preference": "left"}}},
    "each does 30% of the avoiding": {**base, "directive": {"both": {"responsibility_share": 0.3}}},
    "share grows with the age gap": {**base, "directive": {"both": {
        "responsibility_share": "0.5 + 0.01 * pair.age_difference_years"}}},
}
for name, proposal in proposals.items():
    result = validate_proposal(proposal, default_visibility())
    print(f"{name:32} -> {result.category}")
```

```
keep left                        -> valid
the one in a hurry goes first    -> needs_communication
each does 30% of the avoiding    -> inconsistent
share grows with the age gap     -> format_limit
```

### The inbox and the library

Valid rules that were agreed (A) or stated (B) go into a **staging database**
(`rulegen/writer.py`), an inbox inside the experiment's own folder:
`runs/<experiment>/rule_db_staging/`. The real library, `rule_db/`, is never touched. The
writer, not the LLM, gives each rule its id and records where it came from: which sessions,
which model, which prompt. If an LLM writes its own id or history into a rule, that part is
ignored. Moving a rule into `rule_db/` is called **promotion**, and only a person can do it,
with a written reason:

```
python -m negsim.rulegen promote <staging folder> <rule_id> --reason "why"
```

### Testing each new rule

`rulegen/replay.py` tests every stored rule **alone**:

- **Replay:** rerun the exact run the case came from, once without and once with the rule,
  on the same random seed, and compare.
- **Crowd screening:** run the rule in the 100-person two-way flow. A rule that jams the crowd
  **fails screening**. It is marked, never deleted.

In the demo you ran (`runs_mock/demo_crowd_rule.yaml`), the rule "both keep 15 cm more room"
stopped the two people of its own case from colliding, but in the full crowd everyone took
longer (a mean of 58.7 s against 35.0 s) and collided more (187 episodes against 75). A rule
that solves one conflict can still make a crowd worse, which is exactly what screening is for.

### The mock: practice without paying

Every part of layer 4 can run on the **mock client** (`rulegen/mock.py`), a free stand-in that
replies from a script instead of calling DeepSeek. This is part of the transcript of your demo
session (`runs_mock/demo_one_rule/sessions/A_head_on_de176842_ee93b15e_r1.md`):

```
### Turn 1: agent 0
Shown to this agent:  You speak first.
Said:                 I propose this.
Proposed, proposal id 11c9d9f766c2:  {"encounter": "any", "when": {"all": []}, "roles": "symmetric",
                                      "directive": {"both": {"clearance_margin": 0.15}}, ...}

### Turn 2: agent 1
Shown to this agent:  The other person's turn: - They say: "I propose this."
                      - They propose this rule, proposal id 11c9d9f766c2: {...}  Your turn.
Said:                 Agreed.
Accepted: 11c9d9f766c2, read as agreed.
```

The mock is scripted, so its rules say nothing about real LLMs. It only proves the pipeline
works. The paid pilot with the real model is on hold until your supervisor's approval is
recorded, and because, as specified, its worst-case cost exceeds its USD 0.05 cap: USD 0.62,
and USD 0.65 since issue #32 moved the pilot to prompt version 2 (`WORK_LOG-30.md`, question
Q5; the options for it are in `docs/rule-generation.md`, section 10.1).

## 9. Across the layers: fictional groups and meetings inside a passage (issue #32)

Issue #32 adds two things, each of which touches several layers at once. Both were built and
tried out on the free mock; no model was called.

### A fictional group that no rule may read

A person may now belong to a **fictional group** (`ethnic_group`, in
`negsim/personas/groups.py`): one of three invented labels, **Kestrop**, **Dremmik** and
**Pellund**. Each was searched on the web to make sure it is not the name of a real people,
place, language or word in English, Malay, Chinese or Tamil, and every search is written down
in `docs/fictional-groups.md` (one first choice, *Zorvel*, was dropped because it ends like the
Tamil word *vel*). A label is one word and nothing more: no history, looks or customs, and
still no personal names.

**Why invented groups?** Psychologists have found that people favour "their own group" even
when the groups are made up on the spot (the *minimal group* experiments). Invented labels let
the project ask whether an LLM does the same, without bringing in any real group's
stereotypes. The price: they cannot show how a model treats real ethnic groups. That would be
a different experiment.

**Seeing is allowed, reading is not.** If an experiment shows the groups, each person is told
both: "You belong to the Dremmik ethnic group." and "They belong to the Kestrop ethnic group."
But **no rule may read a group**. A rule that tries is refused and put in a category of its own,
`protected_attribute`. It is kept, never deleted, because an LLM trying to make a rule depend
on someone's group is itself a finding.

**Example 6: three proposals, three categories.**

```python
from negsim.avoidance.perception import default_visibility
from negsim.rulegen.validate import validate_proposal

base = {"encounter": "any", "when": {"all": []}, "roles": "symmetric", "priority": 100,
        "directive": {"both": {"clearance_margin": 0.2}}}
reads_group = {**base, "when": {"all": [{"field": "either.ethnic_group", "op": "==", "value": "Kestrop"}]}}
both_back_up = {
    "encounter": "single_file_segment",
    "when": {"all": [{"field": "both.in_segment", "op": "==", "value": True}]},
    "roles": {"by": {"field": "agent.segment_distance_travelled", "order": "ascending",
                     "assign": ["backer", "goer"], "tie": "no_match", "tie_within": 0.1, "unit": "m"}},
    "directive": {"backer": {"back_up": True}, "goer": {"back_up": True}},   # both back out
    "priority": 100,
}
one_backs_up = {**both_back_up, "directive": {"backer": {"back_up": True}, "goer": {}}}
for name, proposal in (("reads a group", reads_group), ("both back out", both_back_up), ("one backs out", one_backs_up)):
    result = validate_proposal(proposal, default_visibility(), schema_version=3)
    print(f"{name:14} -> {result.category}: {result.message}")
```

```
reads a group  -> protected_attribute: when.all[0].field: 'either.ethnic_group' refers to a person's group ('ethnic'), which no rule may read
both back out  -> inconsistent: [back_up] proposal.directive: 'backer' and 'goer' both back up. Inside a single-file passage exactly one backs out and the other goes on; with both backing out, neither gets through (docs/derivations.md, section 17).
one backs out  -> valid: loads, and both people can see everything it reads
```

The first rule reads a group. The second has both people back out of a passage (more on that
below), so neither would ever get through. The third is the same rule with only one backing
out. `schema_version=3` says the rules are written in rule format 3, the one that has
`back_up`.

**In an experiment** the group is a design factor (`design.ethnicity` in a rule-generation
config): the two people in the same group or in different ones; which label goes to whom
(rotated, so that no result can be pinned on one label); and whether the groups are shown at
all, separately from age and gender. It is **off unless a config says `enabled: true`**, and a
paid run with it switched on is refused until the supervisor's ethics sign-off is written into
`CLAUDE.md`. **That sign-off has not been given.** Every session also gets a line in
`outcomes.jsonl` saying who proposed, who gave in, whose rule was accepted and who got the
larger share of the avoiding, so that the results can later be compared group pair by group
pair. The words that introduce the group ("ethnic group") are a setting too, waiting for the
supervisor's review.

### Two people who meet inside a passage

Picture the narrow passage of section 5 (0.8 m wide, 4 m long), with two people *already
inside* it, face to face. They cannot pass, so one has to back out. Before issue #32 nobody
could be told to: the arbiter named a leader and held the follower to speed 0, and ORCA did
the rest.

**What each can see.** Perception record version 3 adds four values, worked out the same
whichever of the two works them out: whether each is inside (`in_segment`), how far it has
walked in (`segment_distance_travelled`), and how far each end of the passage is
(`segment_distance_ahead`, `segment_distance_behind`). Outside a passage the three distances
are empty (`null`), and a rule that compares an empty value does not apply.

**Example 7: what two people inside a passage see.**

```python
from negsim.rulegen.cases import CaseStore

case = CaseStore().get("passage_f89f5745")      # passage_meet_with_speeds_v1, the two at rest
print(case["scenario"]["file"], case["scenario"]["variant"])
for agent, record in case["observations"].items():
    me = record["observer"]
    print(f"agent {agent}: inside={me['in_segment']}, walked in {me['segment_distance_travelled']:.1f} m, "
          f"end ahead {me['segment_distance_ahead']:.1f} m, end behind {me['segment_distance_behind']:.1f} m, "
          f"the other walked in {record['neighbour_segment_distance_travelled']:.1f} m")
```

```
configs/scenarios/passage_meet_with_speeds_v1.yaml {'travelled': 'asymmetric', 'start': 'rest'}
agent 0: inside=True, walked in 2.0 m, end ahead 2.0 m, end behind 2.0 m, the other walked in 1.4 m
agent 1: inside=True, walked in 1.4 m, end ahead 2.6 m, end behind 1.4 m, the other walked in 2.0 m
```

The two distances walked in (2.0 and 1.4 m) and the 0.6 m between the two people's centres add
up to the 4 m passage. "Ahead" is the end on the other person's side, beyond them.

**The new knob, `back_up`.** A person told to back up walks back out of the passage at its own
**backing speed** (0.92 m/s, the normal pace of ten young adults walking backwards in one
study; 0.43 m/s, their slow pace: Nakahara et al. 2005), to just beyond the end, far enough
for the other to come out. It waits there until the other is out, and then goes on along its
own path. While it backs out, the other follows at the same pace and does all of the
avoiding, and the arbiter lets go of the pair until the manoeuvre is over. This backing is
**intentional**, and is logged on its own. It is never counted as issue #26's "walking
backwards" artefact, which is ORCA pushing someone backwards when nobody chose it.

**A rule can now say who backs out.** Rule format version 3 allows `back_up` and true-or-false
values, and the new seed rule `passage_shorter_backs_out` uses both:

```yaml
encounter: single_file_segment
when:
  all:
    - {field: both.in_segment, op: "==", value: true}
roles:
  by: {field: agent.segment_distance_travelled, order: ascending, assign: [backs_out, goes_on], tie: no_match, tie_within: 0.1, unit: m}
directive:
  backs_out: {back_up: true}
  goes_on: {}
priority: 30
```

In words: *"When both are inside, the one who has walked less far in backs out. If they have
walked in within 10 cm of each other, the rule does not say."* A rule that says who backs up
must make exactly one person back up: one in which both do is refused as `inconsistent`
(example 6, second line).

**Example 8: the arbiter alone against the seed rule.**

```python
from negsim.avoidance.perception import default_visibility
from negsim.avoidance.simulation import AvoidanceSimulation
from negsim.experiment.avoidance import build_provider
from negsim.scenarios import load_crowd_scenario

# Agent 0 has walked 2.7 m into the 4 m passage, agent 1 only 0.7 m; they stand face to face.
scenario = "configs/scenarios/passage_meet_middle_v1.yaml"
overrides = {"geometry": {"travelled": [2.7, 0.7]}}
seed_rule = {"provider": "rules", "enable": {"passage_shorter_backs_out": 1}}

for name, directives in (("the arbiter alone", None), ("the seed rule", seed_rule)):
    provider = None if directives is None else build_provider(directives, default_visibility(), "guide")
    result = AvoidanceSimulation(load_crowd_scenario(scenario, overrides), provider).run()
    print(f"{name}: {result.status} after {result.sim_time_s:.1f} s")
    for m in result.back_ups:
        print(f"  agent {m.backer} backed out {m.backing_distance_m:.2f} m at {m.speed_mps} m/s, "
              f"waited {m.waiting_steps * 0.1:.1f} s, then went on ({m.end_reason})")
    print(f"  walking backwards by accident (the artefact): {result.artefacts['totals']['backward_distance_m']:.2f} m")
```

```
the arbiter alone: completed after 58.7 s
  walking backwards by accident (the artefact): 0.00 m
the seed rule: completed after 11.8 s
  agent 1 backed out 1.38 m at 0.92 m/s, waited 0.7 s, then went on (other_cleared)
  walking backwards by accident (the artefact): 0.00 m
```

Read it like this:

- **The arbiter alone** gets them through only just inside the one-minute time limit. Its
  leader, agent 0, creeps forward at 3 cm/s and pushes agent 1 back out of the passage, which
  takes nearly 50 s. That is too slow to count as walking backwards, which starts at 0.1 m/s.
  With the primary baseline's tiny random nudge (section 7), the same meeting does not even get
  that far: of 40 runs from standing still, 28 ended stuck for good and 12 at the time limit.
- **The seed rule** has agent 1, who had walked only 0.7 m in, back out 1.38 m: the 0.7 m back
  to the end, 0.6 m beyond it (the two body radii and a 10 cm margin), and a few centimetres
  more, because agent 0 was still coming on at the same pace when it got there. Both have
  arrived after 11.8 s.

**What the behaviour checks found** (560 runs, 20 seeds per setting; `docs/behaviour-checks.md`,
section 6):

- When the two meet **standing still**, the arbiter's fallback gets neither through in any of
  its 80 runs, and nor does plain ORCA without the arbiter.
- When they meet **walking**, the arbiter gets them through, but only by ORCA pushing the
  follower backwards at about 1 m/s, more than twice the slow person's cited backing speed.
- The seed rule gets them through in all 160 of its runs, at the cited backing speeds.
- **Fewest metres is not fastest.** In the second scenario agent 0 has walked 2.0 m in and backs
  at 0.92 m/s, while agent 1, a slower person, has walked 1.4 m and backs at 0.43 m/s. Backing
  out agent 1, as the seed rule does, adds the least walking. Backing out agent 0 empties the
  passage sooner (2.0 / 0.92 = 2.2 s, against 1.4 / 0.43 = 3.3 s), and everyone is through about
  3 s sooner (13.68 s against 16.70 s, over 20 seeds). No rule can say that, because nobody can
  see another person's backing speed (`docs/derivations.md`, section 18).

### New prompts, new case versions, and the pilot

- **Prompt version 2** (`negotiation/templates/rulegen_*_v2.yaml`) is version 1 with a few lines
  added and nothing else changed: the rule format of version 3, a line for someone standing
  still, lines for being inside a passage, and each person's group, only when the experiment
  shows it. This is what agent 1 of example 7's case is told in condition A, with the groups
  shown:

  ```
  ABOUT YOU
  - You are 25 years old.
  - You are a man.
  - You belong to the Dremmik ethnic group.
  - You are standing still. Your usual walking speed is 1.10 m/s.
  - Your body is 0.50 m wide.

  WHERE YOU ARE
  - You are in a passage 0.80 m wide. The wall on your left is 0.40 m from you, the wall on your right 0.40 m.
  - You are inside a stretch of the passage 0.80 m wide and 4.0 m long.
  - You have walked 1.4 m into this stretch. Its end ahead of you is 2.6 m away, and the end behind you 1.4 m.

  THE OTHER PERSON
  - They are 0.6 m away, straight ahead of you.
  - They are standing still, facing in the opposite direction to you.
  - They are inside the stretch too, and have walked 2.0 m into it from its other end.
  - Their body is 0.50 m wide.
  - They look about 70 years old.
  - They look like a woman.
  - They belong to the Kestrop ethnic group.
  ```

  Nobody is told the other's backing speed: it cannot be seen. Version 1 is untouched, so issue
  #30's experiments still mean what they meant.
- **Cases are never edited**, so a case with the new values is its next version. Each of the 18
  cases got a version 2 by **re-stepping**: running its source run again up to the same moment
  and checking that every value of version 1 came out the same (all of them did). With 8 new
  cases of people meeting inside a passage, that makes 26 new case files.
- **The pilot** now uses prompt version 2. Its worst case is USD 0.65, against the same
  USD 0.05 cap; the options are in `docs/rule-generation.md`, section 10.1, and the choice is
  yours and your supervisor's.

**Try it** (free; the first command writes its runs to `runs_mock/`):

```
python run_experiment.py configs/rule_following/si32_passage_meet_middle.yaml --out runs_mock
python -m negsim.viz.viewer runs_mock\si32_passage_meet_middle
python -m negsim.rules.report si32_passage_meet_middle
python run_experiment.py configs/rule_generation/si32_mock_groups_on.yaml
```

The viewer marks who is backing out, who is waiting and who is coming through; the report
prints the tables of `docs/behaviour-checks.md` from the committed runs.

## 10. Talking to DeepSeek safely: the LLM layer

**Files:** `negsim/llm/`.

Everything that talks to a language model goes through one small interface, `LLMClient`
(`llm/base.py`), with one method: `complete(request) -> response`. Two classes provide it:

- `DeepSeekClient` (`llm/deepseek.py`) sends the request over the internet, using only the
  Python standard library. The API key is read from the `.env` file, kept in a private
  attribute, sent only in a request header, and removed from any error message. It is never
  printed or logged.
- `MockClient` (`llm/mock.py`) answers from a script or a simple fixed policy, instantly and
  for free. Every test uses it.

Every request asks for **JSON mode** (the reply must be a JSON object). If a reply cannot be
read, the agent is shown what it sent and asked once more (`request_with_retry`).

**Money.** Three pieces stop overspending:

- `configs/llm/deepseek_pricing.yaml`: the price per million tokens (pieces of text), copied
  from DeepSeek's pricing page with the date it was checked.
- `spend_ledger.jsonl`: one line for every paid call, with its tokens and cost. It is the
  record of what was spent.
- `BudgetGuard` (`llm/budget.py`): before every call, it works out the **most** the call could
  cost (every token at the highest rate, the longest possible reply) and refuses the call if
  that could push the total over the cap.

**Example 9: the budget guard refuses a call.**

```python
import tempfile
from pathlib import Path

from negsim.llm import BudgetExceededError, BudgetGuard, LLMRequest, PriceTable, SpendLedger

ledger = SpendLedger(Path(tempfile.mkdtemp()) / "ledger.jsonl")
ledger.append({"experiment": "pilot", "cost_usd": 0.049})          # already spent: USD 0.049
guard = BudgetGuard(ledger, cap_usd=0.05, prices=PriceTable.from_yaml(), scope="pilot")

request = LLMRequest(messages=[{"role": "user", "content": "x" * 4000}],
                     model="deepseek-flash", temperature=1.0, max_tokens=600,
                     metadata={"experiment": "pilot"})
print(f"the most this call could cost: USD {guard.worst_case(request):.6f}")
try:
    guard.authorise(request)
except BudgetExceededError as refusal:
    print("refused:", refusal)
```

```
the most this call could cost: USD 0.001262
refused: call refused: USD 0.049000 is already recorded in ledger.jsonl for pilot, this call could cost up to USD 0.001262, and the cap is USD 0.05
```

0.049 + 0.001262 would be more than 0.05, so the call is refused before anything is sent.
The guard errs on the side of caution: the call might really have cost less.

Rule-generation experiments add one more safety step: before any paid call they print a
**worst-case cost preview** for the whole experiment, and send nothing unless you add
`--confirm`.

## 11. Experiments, logs and watching a run

### One command for everything

`run_experiment.py` reads the config's `layer:` line and hands it to the right runner:

| `layer:` | Runner | What it does | Costs money? |
|---|---|---|---|
| (none) | `experiment/batch.py`, `runner.py` | two agents negotiate, then move (layer 1) | only with `--client deepseek` |
| `avoidance` | `experiment/avoidance.py` | a crowd under ORCA, with or without rules (layers 2 and 3) | never |
| `rule_generation` | `rulegen/experiment.py` | LLMs write rules, which are then tested (layer 4) | only with `--client deepseek --confirm` |

Useful options: `--limit N` (run only N runs), `--plan` (list the runs and the worst-case
cost, then stop), `--out FOLDER` (write somewhere else), `--client mock` (practice for free).
Every shipped config names the mock, so nothing is spent by accident.

**Seeds.** A seed fixes the "random" numbers, so a run can be repeated exactly. With
**paired seeds**, the run with a rule and the run without it use the same seed, so the only
difference between them is the rule.

### What a run writes

An avoidance run's folder holds:

| File | What it holds |
|---|---|
| `config.json` | every setting the run used, the git commit, the seed |
| `trajectory.csv` | one row per agent per time step: position, velocity, speed |
| `interactions.jsonl` | one line each time one agent noticed another, with its perception record |
| `pair_interactions.jsonl` | one line per pair that met: which rule matched, the tier |
| `events.jsonl` | collisions, near misses, yields, in time order |
| `outcome.json` | the summary: who arrived when, how many collisions, how deep |

Since issue #32 (log format version 5) `outcome.json` also says who backed out of a passage,
how far and for how long, and who came out of a single-file stretch first. A negotiation run
(layer 1) also has `conversation.jsonl` (every prompt and reply) and `transcript.md` (the same,
for reading). `docs/log-schema.md` lists every field.

### Watching a run

```
python -m negsim.viz.viewer runs_mock\demo_crowd_random
```

This writes one web page to `views/` and opens it in your browser: press play, scrub through
time, click an agent to see what it is doing, and pick a run from the **Run** menu. A still
picture of everyone's path, for a report:

```
python -m negsim.viz.trajectory_plot runs\si1_bottleneck_handoff\001_opposing_no_directive plot.png
```

## 12. Tests: how you know it works

`llm_negotiation/tests/` holds about 1,380 small automatic checks. Each is a Python function
whose name says what it checks, for example
`test_a_changed_rule_is_a_counter_proposal_not_an_acceptance`. Run them all with:

```
cd llm_negotiation
python -m pytest
```

It takes about four minutes. A file called `conftest.py` makes sure that **no test can reach
the internet or read the real API key**, so the tests never cost anything. A test looks like
this (from `tests/test_rulegen_protocol.py`, simplified):

```python
def test_agreement_is_accepting_the_others_latest_proposal_by_its_id():
    talk, client = negotiate(
        turn("This?", KEEP_ROOM),                          # agent 0 proposes a rule
        turn("Yes.", accept=proposal_id(KEEP_ROOM)),       # agent 1 accepts it by its id
    )
    assert talk.outcome == "agreed"
    assert talk.agreement["proposed_by"] == 0 and talk.agreement["accepted_by"] == 1
```

`turn(...)` writes a scripted reply for the mock client; `assert` says what must be true. If
any `assert` is false, pytest reports that test as failed and says why.

## 13. Phase 1: the dataset pipeline (retired)

Before the simulator, the project asked DeepSeek directly how people of different ages and
genders in Singapore behave in everyday and conflict situations. That code is in `pipeline/`
and its output in `dataset/`. It is finished, frozen, and nothing in `llm_negotiation/` uses it.

| File | Step |
|---|---|
| `dataset/scenarios.yaml`, `personas.yaml`, `action_space.yaml` | what to ask about: situations, people, allowed actions |
| `pipeline/estimate_cost.py` | count tokens and estimate the cost first, without calling the API |
| `pipeline/generate.py` | ask DeepSeek, 3 times per cell, saving every raw reply |
| `pipeline/aggregate.py` | combine the 3 replies of each cell into one record |
| `pipeline/validate.py` | check the records: format, coverage, agreement between repeats, speeds against published figures |

The result is 140 **behaviour records** (`dataset/generated/behaviour_records.jsonl`), one per
scenario, age group and gender. Part of one:

```json
{
  "record_id": "sg__bottleneck_doorway_bidirectional__child__female",
  "movement_profile": {"walking_speed_mps": {"estimate": 1.0, "low": 0.7, "high": 1.3}},
  "conflict_behaviour": {
    "primary_action": "halt",
    "yield_likelihood": 0.8,
    "narrative": "A young girl typically halts at the doorway when she sees someone approaching from the other side. ..."
  },
  "aggregation": {"n_repeats": 3, "primary_action_agreement": 1.0}
}
```

The whole run cost USD 0.097.

## 14. Follow one run from start to finish

Here is what happens, function by function, when you type
`python run_experiment.py runs_mock/demo_crowd_random.yaml --out runs_mock`:

1. **`experiment/cli.py` `main()`** reads the YAML, sees `layer: avoidance`, and calls the
   avoidance runner.
2. **`AvoidanceExperiment`** (`experiment/avoidance.py`) checks every key of the config,
   loads the baseline `orca_perturbed_v1`, and expands the design: one factor (`rule`) with
   two levels (`plain`, `generated`) gives two **run plans**, both on the same seed.
3. For each plan, **`execute_avoidance_run()`**:
   - **`build_crowd_scenario()`** (`scenarios/registry.py`) reads
     `configs/scenarios/bidirectional_flow.yaml` with the override `spawn_pattern: random`, and
     **`BidirectionalFlowScenario.layout()`** scatters 50 agents at each end;
   - **`plan.provider()`** builds the source of directives: nothing (plain ORCA) for the first
     run; for the second, a **`RuleDatabaseProvider`** that loads the staging database and
     switches on the one generated rule;
   - **`AvoidanceSimulation.run()`** (`avoidance/simulation.py`) loops over time steps:
     perceive, resolve, coordinate, ORCA plus the linear program, move, bookkeeping;
   - **`AvoidanceRunLogger`** (`runlog/writer.py`) writes `config.json`, `trajectory.csv`,
     `events.jsonl` and `outcome.json`, and **`validate_run_dir()`** checks the folder.
4. **`write_avoidance_summary()`** writes `summary.csv`, one row per run.
5. You open it with **`python -m negsim.viz.viewer runs_mock\demo_crowd_random`**, which reads
   those files and builds the page.

## 15. Glossary

| Word | Meaning |
|---|---|
| agent | one simulated person: a disc with a position, a velocity and a goal |
| arbiter | the part from layer 1 that decides who goes first at a place only one fits |
| back up, back-up manoeuvre | backing out of a passage for the other person, at one's own backing speed, waiting outside, then going on (issue #32) |
| backing speed | how fast a person walks backwards: 0.92 m/s at a normal pace, 0.43 m/s slowly (from one study of ten young adults) |
| baseline | a frozen definition of "plain ORCA", to compare rules against |
| case | a conflict taken from a finished run and frozen, for LLMs to write rules from |
| collision | two discs overlapping; its depth is how far they overlap |
| condition A / B | rules negotiated by two LLM agents / stated by one LLM |
| config | a YAML file describing a scenario or an experiment |
| directive | an instruction one agent follows for one neighbour (six knobs) |
| `dt` | the length of one time step, 0.1 s |
| encounter class | the kind of meeting: head-on, crossing, overtaking, single-file |
| fictional group | an invented label (Kestrop, Dremmik, Pellund) a person may belong to; agents may see it, no rule may read it |
| framing word | the words that introduce the group in a prompt ("ethnic group"), a setting of each experiment |
| hash (SHA-256) | a fingerprint of a piece of text: change one character and it changes completely |
| holonomic | able to step in any direction, as a person can |
| JSON, JSONL | a text format for data; JSONL is one JSON object per line |
| LLM | large language model, such as DeepSeek |
| manifest | a list of fingerprints of frozen files, so any edit is noticed |
| mock client | a free stand-in for the LLM that replies from a script |
| ORCA | the collision-avoidance method of the crowd: each agent does its share of the dodging |
| passage fields | how far each person has walked into a single-file passage, and how far each end is (issue #32) |
| persona | who an agent is: age, gender, and so on (never a name) |
| perturbation | a tiny random nudge to an agent's wished velocity, to break exact ties |
| priority | which rule wins when two match: the higher number |
| promotion | moving a generated rule into the real rule database; only by a person, with a reason |
| prompt version | a frozen set of prompt templates; new wording is a new version (rule generation has versions 1 and 2) |
| proposal id | the first 12 characters of a rule's fingerprint, used to accept it |
| protected attribute | something no rule may read: a person's group. A rule that tries is refused as `protected_attribute`, and kept as data |
| provider | where directives come from: none, a config, or the rule database |
| re-stepping | making a case's next version by running its source run again to the same moment, checking that every old value comes out the same |
| replay | rerunning a case's own run with one rule switched on |
| rule format version | 1, 2 or 3: what a rule may use; every rule says its version. Version 3 (issue #32) added `back_up` |
| run / experiment | one simulation / many runs from one config |
| scenario | a map plus where each agent starts and wants to go |
| screening | testing a generated rule in a 100-person crowd |
| seed | a number that fixes the "random" choices, so a run can be repeated exactly |
| session | one case plus two people, for one LLM conversation or statement |
| severity tier | how bad a meeting was, from T0 (nothing happened) to T4 (collision or stuck) |
| staging database | the inbox where generated rules are stored before any promotion |
| Strategy 1 | the fallback "whoever would get there sooner goes first" |
| token | a piece of text, about 3 characters; what LLM providers charge by |
| velocity obstacle | the velocities that would lead to a bump within the next few seconds |
| walking-backwards artefact | ORCA pushing someone backwards when nobody chose it; counted apart from intentional backing |

## 16. Where to read more

The `llm_negotiation/docs/` folder has one detailed document per topic:

| Document | Read it for |
|---|---|
| `architecture.md` | every module, one run step by step, and every design decision (DD1 to DD119) |
| `orca.md`, `derivations.md` | the maths of ORCA, of the speed limits, and of backing out of a passage |
| `perception.md` | every field of a perception record |
| `metrics.md` | exact definitions of collisions, near misses, yields, tiers |
| `rule-format.md`, `rule-matching.md` | rules in full, and how they are matched |
| `baseline.md` | what "plain ORCA" means, and paired seeds |
| `behaviour-checks.md` | the numbers of every behaviour check, read from the committed runs (issues #28 and #32) |
| `cases.md`, `rule-generation.md` | layer 4 in full |
| `fictional-groups.md` | the fictional group: its labels and every search that checked them, why no rule may read it, the sign-off |
| `llm-backend.md`, `pricing-check.md` | DeepSeek, prices, the budget |
| `log-schema.md` | every log file and field |
| `parameters.md` | every physical number, with its source or the word "placeholder" |

And `llm_negotiation/README.md` has every command, with the results of every experiment so far.
