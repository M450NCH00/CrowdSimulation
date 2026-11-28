# A beginner's guide to this code

This guide explains, in plain words, what every part of this repository does and how the
parts fit together. It assumes you know a little Python (what a function, a dictionary and
a file are) and nothing about crowd simulation or language models.

Sections 4 to 14 are about the code: the simulator, negsim, built in issues #24 to #32. Sections
15 to 23 are about a research track, issues #34 to #41, which asked whether negsim's rules could
be used in other simulators, and in situations they were never written for. That track wrote
documents and ran a few throwaway trials. It changed no code in `llm_negotiation/`.

Every example was run, and the output printed under each is what came out. The first ones were run
on 2026-10-16, and again on 2026-10-17 after issue #32. Examples 10 to 15 were added on 2026-10-19,
after issues #35 to #41, and all fifteen were run that day (the earlier ones still print exactly
the same). To run one yourself, save the code as a file **inside the `llm_negotiation` folder** (for
example `llm_negotiation/try_it.py`), open a terminal in that folder, and type
`python try_it.py`. Examples 12 to 14 instead run the trial programs of issue #40, which need a
Python environment of their own; section 21 says how.

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
15. [Beyond negsim: the portable-rules track (issues #34 to #41)](#15-beyond-negsim-the-portable-rules-track-issues-34-to-41)
16. [Writing a rule once (PT-1, issue #35)](#16-writing-a-rule-once-pt-1-issue-35)
17. [Testing a rule where it was never extracted (PT-2, issue #36)](#17-testing-a-rule-where-it-was-never-extracted-pt-2-issue-36)
18. [What people actually do: the human evidence (PT-3, issue #37)](#18-what-people-actually-do-the-human-evidence-pt-3-issue-37)
19. [Trained models instead of rules? (PT-4, issue #38)](#19-trained-models-instead-of-rules-pt-4-issue-38)
20. [Other simulators on paper (PT-5, issue #39)](#20-other-simulators-on-paper-pt-5-issue-39)
21. [Other simulators by hand, and the use-or-build decision (PT-6, issue #40)](#21-other-simulators-by-hand-and-the-use-or-build-decision-pt-6-issue-40)
22. [The verdict, the corrected idea and the decisions (PT-7, issue #41)](#22-the-verdict-the-corrected-idea-and-the-decisions-pt-7-issue-41)
23. [Concepts from elsewhere: used, tried, proposed, not used, and why](#23-concepts-from-elsewhere-used-tried-proposed-not-used-and-why)
24. [Glossary](#24-glossary)
25. [Where to read more](#25-where-to-read-more)

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

  Track #34: portable rules  (documents and throwaway trials; nothing in llm_negotiation/ changed)
  ────────────────────────────────────────────────────────────────────────────────────────
  PT-7  issue #41  portable_rules/docs/                  the verdict, the idea corrected, the brief
  PT-6  issue #40  integration/simulator-survey/         JuPedSim and Mesa tried by hand: use or build?
  PT-5  issue #39  integration/simulator-survey/         other crowd simulators, surveyed from the desk
  PT-4  issue #38  literature/trained-deciders/          could a trained model stand in for the rules?
  PT-3  issue #37  literature/unseen-scenario-evidence/  what people do in queues, at doors, in lifts
  PT-2  issue #36  literature/unseen-scenarios/          how to test a rule where it was never extracted
  PT-1  issue #35  literature/portable-rules/            can a rule be written once, for any simulator?
```

Issue #32 does not add a layer of its own. It adds two things that run through several layers
at once (section 9). Track #34 does not add a layer either. It asks whether the rules of layers 3
and 4 can leave negsim at all, and answers with documents, not code (sections 15 to 23).

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
| `literature/` | Literature reviews (no code). Track #34 added four: `portable-rules/`, `unseen-scenarios/`, `unseen-scenario-evidence/` and `trained-deciders/` (sections 16 to 19) |
| `refs/` | Saved copies of papers and web pages the code and documents cite. Copies with no open licence are kept on disk only, because the repository is public |
| `pipeline/`, `dataset/` | Phase 1: the dataset generator and its output (section 13) |
| `integration/` | How this work maps onto CrowdGym, the senior's project; and `simulator-survey/`, other simulators surveyed and tried, with the trial code in `spikes/` (sections 20 and 21) |
| `portable_rules/` | Track #34's synthesis: the verdict, the idea restated, a brief for the supervisor, and a plan (section 22) |
| `llm_negotiation/` | **Phase 2: the simulator.** Almost all the code |

**Which branch?** On 2026-10-19, `main` was still at the early literature reviews: it had neither
`llm_negotiation/` nor this guide. Each issue's branch was cut from the one before it, so the
newest, `docs/41-portable-rules-synthesis-brief`, holds everything this guide describes.

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

It takes a few minutes (212 s at the end of issue #32; 617 s on 2026-10-18, in a fresh
environment). A file called `conftest.py` makes sure that **no test can reach
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

## 15. Beyond negsim: the portable-rules track (issues #34 to #41)

Everything in sections 4 to 14 happens inside one simulator, negsim. Issues #35 to #41 ask
whether a rule can leave it. They form a **track**: seven issues under one tracking issue, #34,
called PT-1 to PT-7 ("PT" for *portable rules*). They wrote documents and ran a few throwaway
trials. They changed nothing in `llm_negotiation/`, made no paid call and spent nothing.

**Nothing in sections 15 to 23 is agreed.** The idea (issue #34) is a proposal from a Claude Code
discussion of 2026-10-18. Every verdict, weight and recommendation in the track is a proposal
waiting for the supervisor. Three older things are still pending too:
- the supervisor's standing instruction (no new simulation code until the literature review has
  been discussed) is recorded as unconfirmed;
- the paid pilot is held (section 8);
- the ethics sign-off for fictional groups has not been given, so nothing in the track switches
  the group on (section 9).

### Why the track exists

Two people asked for more than negsim gives:

- **The supervisor** asked that a rule "should not be tied to spatial conflict; ideally it applies
  to any generic simulator" (issue #20).
- **The user** (2026-10-18): extracted rules should work in different kinds of simulator, and be
  tested on **unseen scenarios** such as queue cutting and bus boarding. Simulating queue cutting
  in negsim itself is deferred.

But every rule in `rule_db/` is written in negsim's own terms, as this example shows.

**Example 10: what today's six rules are written in.**

```python
from negsim.rules.database import RuleDatabase

for rule in RuleDatabase.load().rules:
    reads = sorted({ref.written for ref in rule.field_refs()})
    knobs = sorted({knob for role in rule.set_fields.values() for knob in role})
    print(f"{rule.key}: {rule.provenance['source_type']}, {rule.status}, encounter {rule.encounter}")
    print(f"    reads {reads}, sets {knobs}")
```

```
keep_left_head_on@1: hand_written, test_seed, encounter head_on
    reads ['pair.min_corridor_width_m'], sets ['side_preference']
keep_right_head_on@1: hand_written, test_seed, encounter head_on
    reads ['pair.min_corridor_width_m'], sets ['side_preference']
overtaker_keeps_clear@1: hand_written, test_seed, encounter overtaking
    reads ['agent.speed_mps'], sets ['responsibility_share', 'side_preference']
passage_shorter_backs_out@1: hand_written, test_seed, encounter single_file_segment
    reads ['agent.segment_distance_travelled', 'both.in_segment'], sets ['back_up']
single_file_first_arrival@1: hand_written, test_seed, encounter single_file_segment
    reads ['agent.time_to_segment_s'], sets ['passage_order']
younger_yields_head_on@1: hand_written, test_seed, encounter head_on
    reads ['agent.age', 'pair.age_difference_years', 'pair.time_to_collision_s'], sets ['responsibility_share']
```

Read it like this:

- **Who wrote them.** All six are `hand_written` test seeds (section 7). No rule has yet come from
  an LLM: the paid pilot that would produce the first ones is held (section 8). So any result in
  this track speaks for hand-written rules only, and has to say so.
- **What they read.** Corridor width, walking speed, the predicted time to reach a passage, whether
  both are inside one and how far each has walked in, time to collision, and age. Apart from age,
  every one is a
  measurement negsim makes from positions, velocities and the map (the perception record, section
  6). A queue has no corridor width, and "time to collision" means nothing to people standing in
  line.
- **What they set.** `side_preference`, `responsibility_share`, `passage_order` and `back_up`:
  knobs on ORCA (section 6). Even the loader's check that two shares add up to at least 1 exists
  only because of ORCA's guarantee.
- **What they cannot say.** A rule has at most two roles, given by ranking a number. "People getting
  off go first" (a role given by a category) and "the person directly behind a queue-cutter
  decides" (a third person) both come out as `format_limit` (section 8).

So no rule in `rule_db/` can be used in another simulator, or in a conflict that is not about
space.

### The idea, in six parts (a proposal)

1. **A portable rule core.** A rule states its decision only in a small, fixed, versioned
   **vocabulary** of four lists:
   - **conflict types**, by what is contested: `passing_room` (both can get through if someone
     adjusts: head-on, crossing, overtaking); `exclusive_access`, one at a time, with the
     sub-types `.passage` (a narrow passage or doorway), `.queue` (a line for a service) and
     `.vehicle_door` (getting off against getting on); and `capacity` (not everyone fits: a lift,
     a bus);
   - **roles**, for any number of people: by position (`newcomer`, `directly_behind`,
     `alighting`, `boarding`) or by ranking a feature (the younger, the first to arrive);
   - **features**, each with a definition every simulator can follow and a note of who can know
     it: `arrival_order`, `time_waited`, `progress_into_resource`, `age`, `mobility_aid`, and so
     on. `ethnic_group` stays unreadable by any rule;
   - **actions**, stated as intentions: `proceed`, `wait`, `give_way_aside`, `keep_side`,
     `back_out`, `slow`, `keep_distance`, `admit`, `refuse`, `join_tail`.
2. **Two adapters per simulator.** A *perception adapter* turns the simulator's state into a
   **Situation**: the conflict type, who holds which role, the feature values. An *action adapter*
   turns a **Decision** (one action per person) into the simulator's own controls. The "how much"
   (how far to step aside, which ORCA share) lives in the adapter, or in a per-rule **binding**.
3. **A standalone rule engine** that matches cores to a Situation and imports nothing from any
   simulator, with two sets of **conformance tests**: Situation → expected Decision, and scene →
   expected Situation.
4. **Trained models** as other deciders, behind the same Situation → Decision interface.
5. **Tests on unseen scenarios**, written as simulator-independent **scenario cards**, at levels
   from L0 to L4, with whole conflict types held out and human evidence as the reference.
6. **Testbeds chosen to differ:** negsim, a second continuous simulator with queues, and a
   discrete queue model. CrowdGym is the target.

In a picture, with one simulator on each side:

```
   negsim (ORCA, continuous, 0.1 s steps)         a queue model (discrete events)
   positions, velocities, walls                   a list of who is where: P4, P5, P6, ...
                │                                              │
        perception adapter                             perception adapter
                ▼                                              ▼
   Situation: one-at-a-time passage               Situation: one-at-a-time queue
   roles: claimant A, claimant B                  roles: newcomer, directly_behind, ...
   features: arrives in 3.0 s / 4.2 s             features: arrived at, time waited, ...
                └──────────────────────┬───────────────────────┘
                      rule engine (imports no simulator)
                                       ▼
             Decision: one action per person (proceed, wait, ...)
                ┌──────────────────────┴───────────────────────┐
        action adapter                                 action adapter
   passage order leader / follower,               line.append(newcomer)       refuse
   through an ORCA binding (how much)             line.insert(2, newcomer)    admit
```

**The claim to test** is "the same kind of conflict, in any simulator", not "any conflict". The
game-theory review (issue #20) found no evidence that conventions carry over between structurally
different games, so a rule has to stay within its kind of conflict.

**#34's worked example, and what was wrong with it.** Today's `single_file_first_arrival` would
become the core "in `exclusive_access`, the claimant with the earliest `arrival_order` proceeds and
the others wait". In negsim that is a passage order for the arbiter, exactly as now. In a queue, a
newcomer who tries to join part-way has the latest arrival, so the same core says they wait, which
in a queue means joining the back. It sounds neat, but PT-1 found three problems in this one
example (section 16):
- "arrival order" means a *predicted* arrival in negsim and a *recorded* one in a queue;
- "wait" and `join_tail` are not the same action;
- a passage and a queue are different sub-types: one is held by walls, the other by a social norm
  that someone can break.

The corrected version is in section 22.

### The seven issues

| PT | Issue | Question | Answer, in one line | Section |
|---|---|---|---|---|
| PT-1 | #35 | Can a rule be written once and carried out by several simulators? | Written once: yes, long done for norms. Carried out identically: never shown. Promise the same *decision*; measure the behaviour | 16 |
| PT-2 | #36 | How do you test a rule on scenarios it was not extracted from? | No field holds out a whole type of situation, so the protocol is partly the FYP's own; a scenario card must be assembled from seven formats | 17 |
| PT-3 | #37 | Is there human evidence to test against? | Queue cutting: yes, for the pattern (old, Western). Train doors: partly. Lifts: priority only. Bus boarding: none. No Singapore observation | 18 |
| PT-4 | #38 | Which trained models are worth adding? | The rules stay the reference; try small decision trees against an LLM-filled lookup table; no reinforcement learning now | 19 |
| PT-5 | #39 | Which simulators should be tried? (from the desk) | JuPedSim, Mesa, and SUMO only if needed | 20 |
| PT-6 | #40 | Use one, build one, or both? (by hand) | Both: JuPedSim with our own queue order, plus Mesa; SUMO not needed | 21 |
| PT-7 | #41 | The overall verdict, the corrected idea, a brief for the supervisor | Every part feasible with changes; five sub-claims not supported; ten decisions for the supervisor | 22 |

PT-8 (issue #42: vocabulary version 0, the core's format and a "paper test") exists, but waits for
the supervisor's answers.

**How to read the literature folders.** Each has a one-page `verdict.md`: read that first. Every
claim in them cites a section, table or page of a source saved in `refs/` (one prefix per issue:
`pr_`, `us_`, `he_`, `td_`, `sim_`), or is marked `[inference]` (the writer's own reasoning),
`[unverified]` or "(proposal)". A source that could not be opened is a **stub**: six lines saying
what it is and why it could not be read, listed in `missing-papers.md`.

## 16. Writing a rule once (PT-1, issue #35)

**The question:** can a conflict rule be written down once, independently of any simulator, and
still be carried out faithfully by several different simulators?

**The answer: feasible with changes.** Writing a rule down independently of whatever runs it has
been done for decades with norms. Carrying it out *faithfully* has never been shown for behaviour
rules in crowd, pedestrian, game or robot-navigation studies, and where it was tried elsewhere,
the behaviour came out different.

### How other fields write rules down

**Institutional grammar: ADICO, then IG 2.0.** Political scientists code the rules written in laws
and policies into five parts (Crawford and Ostrom, 1995; read here as quoted by Frantz and Siddiki,
since the 1995 paper could not be obtained): **A**ttribute (who it applies to),
**D**eontic (must, may or must not), a**I**m (the action), **C**ondition (when, where and how) and
**O**r else (what follows a breach). A statement with only A, I and C is a *strategy*; add D and it
is a *norm*; with all five it is a *rule*. IG 2.0 (Frantz and Siddiki, 2021) splits the Condition in
two, an **Activation Condition** (when the statement applies at all) and an **Execution
Constraint** (how the action is to be done), and turns the Or else into a whole statement of its
own.

A train-door rule coded in IG 2.0 (an illustration written for this guide), beside today's
`younger_yields_head_on`:

| IG 2.0 part | A train-door rule | `younger_yields_head_on` (section 7) |
|---|---|---|
| Attribute | passengers waiting to board | the younger of the two (role `yielder`) |
| Deontic | must | must (every directive today is an unstated "must") |
| Aim | let alighting passengers off first | do all of the avoiding (`responsibility_share: 1.0`) |
| Activation condition | when the doors open | head-on, touching within 6 s, at least 20 years apart |
| Execution constraint | waiting beside the door, not in front of it | (none) |
| Or else | another statement: "staff may ask a passenger who blocks the door to step aside" | (none: today's format cannot say what happens on a breach) |

- **Status: proposed, as an adaptation.** The core's shape would follow IG 2.0: role;
  must / may / must not; action; activation (the conflict type and features); qualifiers that stay
  portable; breach handling. A simulator's "how much", its binding, sits below the Execution
  Constraint.
- **Why not adopt IG 2.0 as it stands:** it is a coding scheme for text. Nothing in it says how a
  program carries a statement out (it has no *execution semantics*), its lists of terms are open by
  design, and its finer levels cost coders a lot of effort.
- **What is added from elsewhere.** From Mellema and Dignum's work on norms and sanctions: a
  *deactivation* (today's `expiry`), a *deadline*, and *violation handling*, with roles for the
  people who see a breach. Queue cutting is a breach, and most of the evidence about it is about
  bystanders (section 18). From IG's codebook: *profiles*, so that a set of rules declares which
  vocabulary version and which features it uses.

**Normative multi-agent systems.** Computer scientists have written norms as deontic logic, as
condition-action pairs, or as game strategies. Each runs only inside the system that defines it,
and a 2011 survey still called the question of how norms travel between systems open. **Not used.**

**FMI, the Functional Mock-up Interface.** An engineering standard that achieves "write once, run
in many tools". It works because the *compiled model itself* travels (as a file called an FMU)
behind a small typed interface, rather than a description of it: "To be simulator independent, the
FMU must export its implementation in self-contained binary form". Units are written as powers of SI
units, because tools spell unit names differently. Even so, implementations drift: run against
reference test models, five of ten importing tools showed errors.

- **Status: its shape is borrowed; FMI itself is not used.** #34's standalone rule engine is FMI's
  idea: one implementation that every simulator calls. The adapters are FMI's "wrappers", and the
  wrappers are where the evidence says tools drift apart.
- FMI moves models and data, not rules, so it is an analogy here, not a tool.

**HLA and LCIM.** HLA (the High Level Architecture) lets running simulations exchange data. LCIM
(the Levels of Conceptual Interoperability Model) grades how far two systems understand each other:
*technical* (they can connect), *syntactic* (they agree on the format), *semantic* (they agree on
what the data mean), and above that pragmatic, dynamic and conceptual. A shared schema plus an API
reaches only the syntactic level. Turning two different simulators' states into the *same*
Situation is semantic work, which is exactly the adapters' job. **LCIM is used as a lens; HLA only
as an analogy.**

**Behaviour layers in crowd simulators.** Three systems keep behaviour apart from motion (section 20
describes them):
- **Menge** runs one behaviour specification over swappable motion models. Under three motion models
  it gave three different sets of trajectories, and each model needed its own time step.
- **Vadere**'s "psychology layer" (perception → cognition → behaviour) is said to be "easily
  implemented in different pedestrian simulation programs": claimed, not done.
- **HuNavSim 2.0** runs one behaviour-tree engine in four robot simulators, but compares nothing
  across them.

All three are portable *by design intent* only. **Design precedents; not used as code.**

### Has anyone run one rule in two simulators? Docking

**No crowd, pedestrian, game or robot-navigation study read here ran the same behaviour rule in two
simulators and compared the behaviour.** The nearest cases come from social simulation, where
re-implementing a model in a second system, to see whether it gives the same results, is called
**docking**. Every study read found differences hidden in details nobody had counted as part of the
rule:

| Study | The rule carried across | What came out different, and why |
|---|---|---|
| Axtell et al. 1996 | Axelrod's rule of cultural change, rebuilt inside Sugarscape | matched in 11 of 12 comparisons; the 12th failed because the two models picked the next agent to act differently (with or without replacement) |
| Edmonds and Hales 2003 | Riolo et al.'s rule "donate when your tags differ by no more than your tolerance" | the two re-implementations agreed with each other but not with the original, because of an unstated tie-break; and writing "<" for "≤" made donation vanish (0.0% in every setting) |
| Wilensky and Rand 2007 | the ethnocentrism model, moved from Ascape to NetLogo | four rounds of hidden differences: when a value resets, a misread measure, the order of events, an unshuffled list of agents |
| Galán and Izquierdo 2005 | Axelrod's norms game | short runs matched; long runs reversed the result |

**Example 11: one comparison sign, two decisions.**

```python
# single_file_first_arrival: two predicted arrivals within 0.5 s of each other are a tie.
tie_within = 0.5
a, b = 3.0, 3.5          # seconds until each person would reach the passage

negsim_tie = abs(a - b) <= tie_within      # how negsim's RoleAssignment.roles() tests it
other_tie = abs(a - b) < tie_within        # the same words, coded with < instead of <=
print("negsim:         ", "tie, the rule does not apply" if negsim_tie else "the first to arrive leads")
print("other simulator:", "tie, the rule does not apply" if other_tie else "the first to arrive leads")
```

```
negsim:          tie, the rule does not apply
other simulator: the first to arrive leads
```

Read it like this: both programs carry out the same sentence, "two arrivals within 0.5 s of each
other are a tie". negsim's code says `<=` (`RoleAssignment.roles` in `negsim/rules/model.py`), so
arrivals exactly 0.5 s apart are a tie: the rule does not apply, and the arbiter decides. A second
simulator whose programmer wrote `<` gives the first arrival the lead. Same rule, same situation,
different decisions. This is Edmonds and Hales's "≤ against <", and it is why PT-1 asks for every
term to be defined operationally: its unit, whether a comparison is strict, what happens on a tie,
who can know it, and worked reference cases.

### What PT-1 concluded

1. **Claim decision conformance**: the same Situation gives the same Decision, which can be tested
   exactly. **Measure the behaviour** against an equivalence standard fixed in advance. Axtell et
   al. name three: numerical identity, the same distribution, or the same relationships.
2. **Declare every simulator-dependent quantity in bindings**: thresholds, timing in seconds (never
   in steps), how often the engine is called, and the order in which agents are updated.
3. **Define each term operationally** (example 11).
4. **Own the conformance tests centrally**, one feature at a time first, with tolerances, plus long
   closed-loop runs. And remember that a passed test means "no fault found", never "conforms": "If
   the FMU compliance checker does not find a problem, it is not guaranteed that the FMU is error
   free".

PT-1 also flagged eleven unclear points in #34's idea, F1 to F11
(`literature/portable-rules/feasibility.md`, section 2). The ones to know:

| Flag | The point |
|---|---|
| F1 | "Today's rules become the ORCA binding, unchanged" clashes with "a rule speaks only in the vocabulary": their *when* conditions (time to collision, encounter class) are negsim measurements |
| F2 | #34's own example crosses from a passage (held by walls) to a queue (held by a norm that can be broken) |
| F3 | Is a newcomer who "waits" in a queue doing `wait`, or `join_tail`? |
| F4 | `arrival_order` is a *predicted* arrival in today's rule (`agent.time_to_segment_s`) and a *recorded* one in a queue |
| F6 | The idea does not say in what unit a core states time, or how often the engine is called |
| F7 | Ties and strict comparisons are not mentioned (example 11) |
| F9 | The "Or else" has nothing to attach to: no action reacts to a breach, and no role is "the one who saw it" |
| F11 | "A simulator supports the rules when its adapters pass the tests" overstates what tests can show |

### Novelty: has someone done this already?

Issue #20 had left one paper unread, arXiv:2409.00993 (Horiguchi et al., 2024), and PT-1 read it in
full. LLM agents play Axelrod's norms game and form norms through dialogue, which is the FYP's
*method*. But nothing is written down as a rule, nothing is run by another system, there is one
game, and transfer is left for future work. The other near neighbours:

- **CRSEC** (2024) stores norms made by LLMs, but their core is natural language, read only by LLM
  agents, in one environment.
- **TR2MTL** (2024) has an LLM turn *human-written* traffic law into temporal logic, checked in one
  simulator. Its commonest error, wrong logical connectives, is a warning for anyone who lets an LLM
  write cores.
- **Zhang et al. 2026** (NTU), the repository's closest prior work, distil an LLM-driven crowd into
  code that plain agents run, in one simulator.

**The new part is the combination:** conflict rules elicited from LLM agents, written as
simulator-independent artefacts, carried out by non-LLM agents in more than one structurally
different simulator, and tested on conflict types held out from extraction, against human
evidence. No single ingredient is new, and the vocabulary is the least new part of all. And this is
"none found in this review" (English-language sources, one session), not "none exists".

## 17. Testing a rule where it was never extracted (PT-2, issue #36)

**The answer:** testable, but the literature supplies only parts of the method.

### What "unseen" means in other fields

| Meaning of "unseen" | Example | What it cannot tell us |
|---|---|---|
| New partners in a familiar world | **Melting Pot** (Leibo et al., 2021), a test suite for multi-agent reinforcement learning: a test scenario is a *substrate* (a game world) plus a *background population* of agents trained separately | it never holds out a world: "Policies are not transferable between substrates" |
| A new layout of the same task | Zhang et al.'s out-of-domain set, a different evacuation layout with 3 seeds; Tordeux et al., who train on data from a ring and test on a bottleneck, and the other way round | a new layout is not a new kind of conflict |
| A new test in a catalogue | RiMEA's tests (below), which warn that a parameter calibrated in one test may be meaningless in another | it says when *not* to reuse a calibration, not how to test transfer |

None holds out a whole *type* of situation. So the track's design, holding out whole conflict
types, is **the FYP's own and has to be presented as such** (a proposal).

Melting Pot has one idea worth keeping. In its **resident** mode the agents under test are the
majority; in its **visitor** mode one agent under test arrives among others who already keep their
own norm. For queue cutting, visitor mode is the realistic test: one newcomer arriving at a line of
people who already queue. **Borrowed** (level L0b, below).

### Do people carry a habit from one situation to another?

Issue #20 found no evidence that conventions carry over between structurally different games. PT-2
read five of the six studies issue #20 could not obtain, and the picture is more positive, with
conditions:

- **It happens, but within one class of games.** Cooper and Van Huyck found transfer "even when
  games are not structurally similar", but every game they used had the same two kinds of
  equilibrium.
- **It is directional.** Cason et al.: a habit learned in one game carried into a second, but not
  from the second back into the first.
- **It can do harm**: the habit carried over can be the wrong one.
- **It depends on telling situations apart** (Huck et al.; Grimm and Mengel), and on **meaningful
  context** (Cooper and Kagel).

In plain words: a rule for "who goes first through a narrow passage" might well carry to a doorway,
which is the same kind of conflict. There is no evidence that it carries to "who gets the last
place in a lift", and if it does, it may carry badly. That is why rules are scoped by conflict
type, and why crossing a type is a test, run on purpose and logged.

### The transfer levels, with an example

Take a rule extracted in the narrow hallway of section 5:

| Level | What is new | Example |
|---|---|---|
| **L0a** | new seeds | the same hallway meeting drawn again: at least 10 random populations × 5 runs each (IMO's rule, below) |
| **L0b** | new co-players | the same hallway, but the other person keeps a different, settled habit (Melting Pot's visitor mode) |
| **L1** | new parameters | the hallway 1.2 m wide instead of 0.8 m (as RiMEA's test 12d varies a passage from 0.8 to 1.2 m) |
| **L2** | a new layout, same conflict type | a doorway, or a bent passage, instead of the straight hallway |
| **L3** | a new conflict type in the vocabulary | the hallway rule tried on a queue; and, where rules exist on both sides, a queue rule tried in the hallway |
| **L4** | a conflict type outside the vocabulary | a signalised crossing, run by a traffic light and involving vehicles: the right answer is "none of my rules applies" (abstain) |
| axis **W** | the wording, at the LLM stage | the hallway described as a "narrow walkway", or with one fact changed |
| axis **C** | the convention | a world in which "everyone keeps right" is stated as the custom |

PT-2 made four changes to #34's levels:
1. it split L0 into L0a and L0b;
2. it runs L3 in **both** directions, because transfer is directional;
3. it added the W and C axes, because a reworded familiar conflict is never L3;
4. it freezes the bindings as well as the cores.

L4 stays, but no source tests a rule that should decline to act, so it is a proposal with nothing
behind it.

**The first split (a proposal).**
- *Seen*, where rules come from: `passing_room` (head-on, crossing, overtaking) and
  `exclusive_access.passage` (the single-file segments). These are today's encounter classes.
- *Held out*: `exclusive_access.queue` (queue cutting), `.vehicle_door` (bus and MRT boarding) and
  `capacity` (the lift).

With only five conflict types, "leave one type out" gives case studies, not statistics.

### Freezing, baselines and metrics

- **Frozen before any held-out run:** the cores and the vocabulary version; the bindings; each
  card's pass criteria; and the list of patterns the rule is expected to reproduce, *including the
  ones it is expected to miss* (from ODD, below). The proposal is to record the git commit of all of
  them in every run's log.
- **Baselines:**
  - no rule at all (the floor);
  - a simple stated convention, such as first come, first served;
  - the LLM deciding directly (paid, so off by default);
  - trained deciders (section 19);
  - a rule extracted from the held-out type itself, Melting Pot's "exploiter" (the ceiling).
- **Three things are tested apart:** the **decision** (is it what people choose?), the
  **perception** (did the adapter recognise the conflict type?), and the **outcome in motion** (did
  the crowd clear, without deadlock or collision?).

### Scenario standards, and why none can be used as it is

A test scenario has to be written so that several simulators can run it. PT-2 read eight formats:

| Format | What it is | Taken for the card | Why it cannot be used as it is |
|---|---|---|---|
| **RiMEA 4.1.1** | a guideline for evacuation analysis, from a German association; tests in prose plus a figure. Test 1: a 2 m × 40 m corridor, one person at 1.33 m/s, and "the travel time should lie in the range of 26 to 34 seconds" | the headings Background / Aim / Setup; a stated acceptance band | every vendor rebuilds each test by hand; no queues, no vehicles, no "who goes first" |
| **IMO MSC.1/Circ.1533** | evacuation guidelines for passenger ships (it supersedes Circ.1238) | the population mix by age, gender and mobility; at least 50 runs, from 10 random populations × 5 repeats | maritime; queues only in a hand calculation, no boarding |
| **NIST TN 1822**, on the road to **ISO 20414** | how to verify and validate building evacuation models | the four parts of a test: geometry, scenario, expected result, test method; and saying where a test should *not* be reused | ISO 20414 itself is paywalled and was not read |
| **OpenSCENARIO 1.4** | the scenario standard of driving simulation | a starting state with no conditional logic, then events fired by triggers, then a stop condition: "a newcomer arrives at t = 30 s", "the door opens when the bus has stopped" | built for road users; a pedestrian has only a category, no persona |
| **ODD** (Grimm et al.) | a protocol for *describing* agent-based models | the "patterns" a model should reproduce, including those it fails to; keeping experiments apart from models | describes models, not tests, and is read by people, not run |
| **SteerBench** | 56 test cases for steering, such as two people meeting in a doorway | each agent's start, heading, speed and goal; pass/fail written into the case; scoring from logged trajectories only, blind to the algorithm | uniform 1 m discs, no personas; no queues or vehicles |
| **JuPedSim's journeys** | one simulator's routing (section 20) | a journey of stages: waypoint, queue, waiting area, exit | a vocabulary inside one simulator; its queue is first in, first out |

**What no format covers:** who should go first, and why, in a contested resource, which is exactly
what a conflict rule decides; talk between people; and joining a queue part-way. A card has to add
those fields itself.

Here is what a card might look like. **It is an illustration written for this guide; no card
exists yet** (cards are a later issue):

```yaml
id: queue_cut_counter
version: 0
context_of_use: one line at a counter that serves one person at a time; not for boarding or lifts
background: a newcomer tries to join part-way along a queue
aim: does a transferred rule decide who goes ahead as people do, and does the line still clear?
conflict_type: exclusive_access.queue
level: L3                      # the rules were extracted in passages, not in queues
held_out: true
geometry: a counter, a queue area 1 m wide, an entrance and an exit
journeys: [entrance, queue, service point, exit]
population: the Singapore persona mix by age band and gender (dataset/personas.yaml)
roles: [newcomer, directly_behind, others_in_line]
initial_state: ten people in line, standing
events:
  - every 10 s, the person at the front is served and leaves
  - at t = 30 s, a newcomer arrives beside place 3 and heads for the gap ahead of it
stop_condition: everyone served, or t = 300 s
background_norm: everyone else keeps first come, first served (visitor mode)
communication: none            # or: the newcomer may give a reason (decision 4, section 22)
patterns: objection comes mostly from the person directly behind (QC-1), once the vocabulary has observer roles
reference_evidence: QC-1, QC-3, QC-4 (New York, 1978; grade B, old, W, repro)
acceptance_band: fixed before any run
metrics: [decision agreement, deadlock rate, time to clear, effect on the others]
repetitions: 10 populations x 5 seeds
required_capabilities: [a queue whose order can change, timed events]
```

### Leakage: did the LLM just remember?

LLMs have read about famous situations, so a rule that matches people may only show that the LLM
remembered. That can be **graded, never ruled out**, in three ways:

1. **Counterfactual variants** (Wu et al.): change a rule of the world, such as "in this city,
   people board before others alight", and check that the answer follows the change.
2. **New variants** of famous set-ups (Aher et al.). Their own "new" obedience scenario was still,
   they admit, "at its core ... reminiscent of Milgram's". That is why a reworded familiar conflict
   counts as W, never as L3.
3. **Small perturbations** of a familiar story (Binz and Schulz): change one fact, and see whether
   the answer changes with it.

So the claim stays modest: the tests check **the extracted rules**, not whether an LLM
"understands" people.

## 18. What people actually do: the human evidence (PT-3, issue #37)

A held-out test needs a reference: what people really do in that situation. PT-3 looked for it in
five scenarios, Singapore first.

### How the evidence is graded (a proposal)

| Grade | Means |
|---|---|
| **A** | two or more independent research groups report numbers pointing the same way |
| **B** | one field study or controlled experiment, with numbers |
| **C** | an observation without numbers; data cited inside a simulation or a review; or a statistic about a related outcome |
| **D** | theory, an official statement of a norm, or anecdote |

Flags follow the grade: `old` (data from before 2001), `W` (a Western setting), `EA` (East Asian),
`SG` (Singapore), `lab` (the people knew they were being observed), `repro` (numbers read through a
verbatim reproduction of the original table, never graded above B) and `off` (an official report).
A statement on which two sources disagree is **CONTESTED**, and a test should not require a rule to
reproduce either side.

**Reading one statement.** QC-1: *"When one person cuts into a queue, objection comes mostly from
the person directly behind the cut, and falls off steeply with distance: 36% directly behind, 14%
two places back, 0% three places back."* Its grade, **B `old` `W` `repro`**, says: one field
experiment with numbers (B), run in 1978 (`old`), in New York (`W`), and read through a
reproduction of its table (`repro`).

### Queue cutting: the best evidence, and it is old

- **The experiment** (Milgram et al.). In spring 1978, graduate students cut into 129 queues at 17
  places in New York: a bank, a post office, Grand Central's ticket counter, bus boarding queues and
  more. Sometimes one person cut in, sometimes two, sometimes with silent helpers ("buffers") in
  between. It was published in 1986, after Milgram's death, which settles the old "1978 or 1986?"
  question: run in 1978, published in 1986. The paper itself could not be obtained. Its numbers
  were read from tables reproduced, with the publisher's permission, in an open chapter
  (Brintzenhofe, 2023): hence `repro`.
- **What people did.** Directly behind a single cutter, 8 of 22 objected (36%); two places back, 2
  of 14; three places back, 0 of 9. Two cutters together drew objection from 20 of 23 people
  directly behind (87%). Most people did nothing at all. A cutter who seemed to be joining a friend
  drew far less objection (10 to 13%) than a stranger (37 to 60%) (Schmitt et al.; QC-4).
- **Asking first, with a reason** (Langer et al., 1978, at a photocopier). With a small favour (5
  pages), 60% let the asker go first when no reason was given, and 93 to 94% with any reason, even
  an empty one ("because I have to make copies"). With a big favour (20 pages), only a real reason
  helped (42% against 24%). But Folkes (1985) did not replicate "any reason works", so that is
  **CONTESTED** (QC-8). What holds up is that the *kind* of reason and the *size* of the favour
  matter (QC-6, QC-7).

### Doors, lifts and escalators

| ID | What people do | Where, when | Grade |
|---|---|---|---|
| BA-1 | at a train door, alighting mostly starts before boarding: boarders give way or wait for a gap | London (a lab mock-up, and Underground video of 2014 to 2015) | B `W` `lab` |
| BA-5 | at peak times some passengers let a train go and wait for the next (after 22% of trains, at one door) | Green Park, London, 2015 | B `W` |
| BA-8 | **a gap:** how often boarders start before alighting has finished. The two studies that measure it could not be opened | — | none |
| LE-1 | when a wheelchair, pram or walking-frame user waits for a lift, everyone lets them in first in 24% of cases, some do in 27%, and nobody in 49% | Taipei MRT, 2018 (89 trips needing priority, of 604) | B `EA` |
| LE-3 | asked to stand on both sides of a long escalator, people comply only while staff are there asking | Holborn, London, 2015 | B `W` `off` |

Bus boarding has **no** usable evidence, and escalator merging only weak evidence.

### Singapore: norms, but no observations

No Singapore study observing any of the five behaviours was found. What Singapore does supply:
- the norms it promotes (give way to alighting passengers; priority queues; hold the handrail), grade
  D, because they are statements, not observations;
- one platform study (SG-1): by Wi-Fi tracking, 44% of passengers at Serangoon and 37% at Bishan
  moved between waiting spots before boarding;
- escalator incident counts (SG-3).

**So every reference behaviour for a Singapore scenario has to be borrowed from London, New York or
Taipei, and labelled with its city and year.** One flag for the supervisor: `dataset/scenarios.yaml`
mentions a Singapore "stand on both sides" escalator campaign, and no source for it was found. The
official advice found is "hold the handrail".

**Age and gender:** almost nothing has been measured in these scenarios, so an age or gender
difference shown by the LLM personas here cannot be checked against human data.

**Why this matters for the vocabulary.** The best queue evidence is about **bystanders objecting**
(QC-1 to QC-5) and **asking with a reason** (QC-6 to QC-8). The first needs breach handling and
observer roles, which #34's vocabulary lacks (F9). The second is exactly what today's pipeline
rejects as `needs_communication` (section 8). And "alighting first" (BA-1) needs roles given by a
category. So what the unseen tests can check against people depends on decisions 3 and 4 (section
22), not only on the evidence.

Fourteen sources could not be downloaded automatically (`missing-papers.md`); most should open in a
browser, or through the library.

## 19. Trained models instead of rules? (PT-4, issue #38)

Part 4 of the idea puts trained models behind the same Situation → Decision interface as the rule
engine. Before anything is trained, PT-4 asked what the literature says. Nothing was trained.

### The options

| Option | What it is | Status | Why |
|---|---|---|---|
| **R. The rule engine** | the rules themselves | **the reference** | already cheap (arbitration rules have run at 10,000 agents) and fully readable |
| **T. An LLM-filled lookup table** | for every combination of binned Situation features, ask an LLM several times in advance; at run time, look the answer up | **proposed, as the baseline** | the only approach in the sources that reached large populations: 400 LLM queries covered 8.4 million agents for one weekly decision (Chopra et al.), and a lookup takes 0.54 µs (GenWorld). But its agreement with fresh LLM calls was never measured, and a combination never seen needs a fall-back rule |
| **D. A small decision tree or rule list** | learned from labelled decisions, reading the same Situation features | **proposed, to train first** | as portable as the rules, since it reads the same inputs. Small trees can be read, and checked exhaustively: in VIPER the distilled trees had 3 to 769 nodes, the small ones were verified in seconds, and verification found a failure that 50 perfect test runs had hidden |
| **N. Gradient boosting or a small neural network** | the same inputs, a bigger model | **only if trees miss by a stated margin** | on structured features, simple models usually do as well as complex ones (Rudin); a small network took 8.7 ms per decision, about 87 s for a round of 10,000 on one core |
| **L. A small language model at run time** | a smaller LLM, fine-tuned on a larger one's decisions | **not used** | 0.5 to 2 s per call: 1.4 to 5.6 hours for a round of 10,000 decisions made one after another, and tested on 500 agents at most. Perhaps a cheaper *teacher* |
| **P. Reinforcement learning with rule rewards** | a policy learned by trial and error, rewarded for keeping the rules (for example through a *reward machine*, a small state machine that hands out the reward) | **not used now** | one policy per simulator, and no transfer between simulators tested anywhere; hours to days of training; a norm given as a reward was kept about 85% of the time, not always (SA-CADRL) |
| *A live LLM for every decision* | the LLM decides each conflict as it happens | **not used** | far too many calls at 10,000 agents |

**The shield (proposed).** Instead of trusting a trained model, let it *propose* a decision, and
let the rule engine **block** any proposal that breaks a hard rule (Alshiekh et al.'s *shielding*).
The guarantee then comes from the rules, whatever the model does.

**A warning from the sources.** Training on lopsided labels exaggerates the majority. In Amano and
Yamaguchi's study, a choice that made up 74% of the training labels became more than 94% of the
trained model's choices. A decider trained on rule labels could do the same.

### Where the labels would come from (the teachers)

- **LLM decisions on Situations written as text, from several models**, with their disagreements
  *reported*, not voted away, because demographic effects reverse between models (issue #16). These
  are paid calls, so they would need a budget of their own.
- **The rules, combined with those labels.** Rules helped most where other labels were scarce (Hu
  et al.). A student trained on rule labels alone can only copy the rules, so it serves as a check
  of the pipeline: it must reproduce them exactly.
- **Session outcomes** (`outcomes.jsonl`, section 9): few, made by LLMs, and recording each
  person's `ethnic_group`, so they are held-out comparison data, not labels.
- **Human data**: the yardstick of the evaluation, not a teacher, since the evidence of section 18
  is published rates, not labelled individual decisions.

### Checking a trained model for bias

Today's rule "no rule may read `ethnic_group`" (section 9) is what the fairness literature calls
**fairness through unawareness**: the model never sees the attribute. Kusner et al. show that this
is not enough on its own, because other inputs can carry the attribute. Suppose that in some
scenario every Kestrop person entered by the left-hand gate: a model that reads "which gate" would
be reading the group without ever seeing it. Hence PT-4's checks, all proposals:

| Check | What it asks |
|---|---|
| B1 | Is `ethnic_group` absent from the model's inputs, and from any prompt it is given? |
| B2 | Is any Situation feature *caused* by the group (the spawn gate, a speed, a role)? In a simulator this can be checked by construction, because we write the scenario generator |
| B3 | **The counterfactual test**: change only an attribute that must not matter, keep everything else, and check that the decision does not change |
| B4 | Leave out the attributes a rule says *should* matter (a mobility aid, if a rule gives it priority): forcing those to make no difference would be wrong |
| B5 | For a small tree, check that no branch tests a must-not-matter attribute. That proves B3 for every Situation at once |
| B6 | Test the LLM *teacher* first: every Situation × every combination of persona attributes, then estimate each attribute's effect (Tamkin et al.'s design) |
| B7 | If session outcomes are used, compare their rates across the values of each must-not-matter attribute |

The counterfactual test (B3), on one Situation:

| | Situation | Gender | Decision |
|---|---|---|---|
| original | a newcomer with no mobility aid asks to go ahead of one person | woman | admit |
| counterfactual | exactly the same, with only the gender changed | man | must also be admit: a gap of 0 |

B6 and B7 for `ethnic_group` would need the fictional group switched on, so they wait for the ethics
sign-off. (Tamkin et al.'s study is by Anthropic, about Anthropic's own model. PT-4's review was
written with an Anthropic model, so it flags the conflict of interest and uses only the study's
design.)

**The limits.** Only two of the sources are about pedestrian conflicts. None compares a learned,
readable model with hand-written rules, and none tests a trained decider in more than one
simulator. "Try small trees first" is the cheapest experiment, not a proven one.

## 20. Other simulators on paper (PT-5, issue #39)

### What to look for in a simulator

The testbeds have to differ from negsim in the ways portability can break:

- **space**: continuous (people anywhere on the floor) or discrete (cells, or places in a line);
- **time**: fixed steps (everyone moves every 0.1 s) or events (time jumps to the next thing that
  happens);
- **the motion model**: ORCA, or something else;
- **infrastructure**: queues, waiting areas, service points, vehicles.

For each candidate PT-5 also asked where the two adapters would attach. Can outside code **read**
every agent's state on every step (perception)? Can it **change** an agent's target, speed or route
during a run (action)? Nothing was installed or run: everything came from documentation, papers,
and single source files read on GitHub.

One finding applies to all of them: **no open-source candidate offers a per-step callback.** In
every case the adapters would live in a loop that this project writes around the simulator's own
"advance one step" call (`iterate()`, `simulationStep`, `nextStep`, `doStep`), just as negsim's
loop is our own. The one built-in per-step decision hook is CrowdGym's `RL_take_action`.

### negsim (this repository)

ORCA in continuous 2D space; fixed steps (0.1 s in the crowd, 0.2 s in the doorway); YAML
scenarios. No queues, waiting areas, service points or vehicles. 10,000 agents take 1.36 to 1.60 s
per step, on one thread of this laptop: about 0.06 to 0.07 of real time.

**Verdict: kept**, as the ORCA testbed and the reference. In #34's terms, today's rules already are
its "ORCA binding".

### CrowdGym (the senior's FYP, and the target)

Described only from this repository's two notes, `integration/crowdgym_mapping.md` and
`dataset/schema/README.md`, because the report and code could not be shared ("Can't share now",
2026-10-18). What is known:
- a Python API, with a C++ port in progress;
- an overridable `RL_take_action` that returns, for every agent, `[move_x, move_y, delta_facing]`;
- route choice by an `AgentJourneyDirector`;
- a movement model called "CFS", which the senior found "less jittery at exits";
- agent types with `Speed`, `Tau`, `Mass`, and a side and a front radius.

**Is CrowdGym built on JuPedSim? Left open.** Its "journeys" and its "CFS" point that way. But:
- the 0.8 m/s it calls "a JuPedSim default" is, in JuPedSim 1.4.x, the default of the social force
  model (CFS's default is 1.2 m/s);
- `Tau` and `Mass` belong to other JuPedSim models, not to CFS;
- JuPedSim has nothing like the RL action interface.

CrowdGym's dependency list would settle it in minutes. A public repository called
`ntu-fyp-25/crowdgym` turned up in a search; by the user's choice it was **left unopened**, since
the code had not been offered.

**Verdict: the target, but conditional.** No CrowdGym binding is planned until its code, or at least
its dependency list, is available.

### JuPedSim (Forschungszentrum Jülich)

- **What it is:** a pedestrian simulator with a C++ core and a Python API; LGPL-3.0; version 1.4.2
  (2026-05-21), with a Windows wheel on PyPI.
- **One step.** Each `iterate()` advances 0.01 s and runs three levels of decision in turn:
  *strategic* (which journey: where am I going overall?), *tactical* (which route to the next
  stage?) and *operational* (the motion model: which velocity now?).
- **Journeys and stages.** A route is a **journey**: a network of **stages** joined by
  **transitions**. The stages are:
  - a *waypoint* (reach a spot);
  - an *exit* (leave the simulation);
  - a *waiting queue* (wait at fixed spots, move up as the front leaves; a script releases the
    first n with `pop(n)`);
  - a *waiting set* (fixed spots, released all at once);
  - *direct steering* (a script sets the target).
- **Motion models.** Five; the two that matter here:
  - the **collision-free speed model (CFS)**, the default. In JuPedSim's words, a person's direction
    comes from "exponential repulsion from nearby agents", and "Agents adjust their speed according
    to the nearest neighbor in their headway": the less room ahead, the slower. Nobody is ever
    pushed;
  - the **social force model**: a "driving force" towards where the person wants to go, a "repulsive
    force" from other people and an "obstacle force" from walls. Velocity changes gradually, which
    is why its reactions in section 21 lag by up to 1.5 s.
- **Traps found on paper:** CFS stores no current velocity, so a perception adapter must work it
  out from two positions; and `agent.target` works only for someone on a direct-steering journey.
  Otherwise "any change will be ignored".
- **Verdict: shortlisted, tried (section 21), and proposed** as the second continuous testbed and
  the host for boarding. It differs from negsim in its motion models, its step (0.01 s against
  0.1 s) and its infrastructure, and it may be CrowdGym's engine.

### SUMO, with its JuPedSim coupling

- **What it is:** a traffic simulator for whole road networks, in C++ (EPL-2.0), from DLR. A person
  has a **plan** of stages, *walk*, *ride* and *stop*; a bus has a `personCapacity` and a
  `boardingDuration`, 0.5 s per person by default. An outside program steps the simulation and reads
  or changes people through **TraCI**, a remote-control protocol.
- **With JuPedSim coupled in**, people walk in a continuous 2D area, in sub-steps of about 0.01 s
  inside each SUMO step.
- **But** SUMO's own boarding is a time per person, not a crowd at a door ("Traditional SUMO
  workflows teleport passengers onto the bus", Lindner et al. 2025); the coupling's waiting
  positions are static; and "pedestrians currently do not react to vehicles".
- **Verdict: shortlisted on a condition, then not tried.** The door conflict ran in JuPedSim alone,
  with a timer and a counter standing in for the bus (section 21). SUMO would earn its place only in
  a boarding scenario at the scale of a network, with timetables, several vehicles and routes.

### Vadere

- **What it is:** a pedestrian simulator in Java 17 (LGPL; version 4.0). Its main model is the
  **optimal steps model**, in which people take steps rather than glide. It is **event-driven**:
  "each step of an agent is an event. Stepping events of multiple agents are ordered in an event
  queue and executed accordingly". So people do not all move together every 0.1 s: whoever's next
  step is due soonest moves next.
- Its **psychology layer** (perception → cognition → behaviour) is the nearest thing in any
  simulator to #34's perception adapter → rule engine → action adapter. It also has waiting
  targets, walking groups and a TraCI server.
- **But** its Python access is marked "Work in Progress"; it has no queues and no vehicles; and
  "simulating thousands of agents in real-time using the OSM with Vadere is not yet possible".
- **Verdict: not shortlisted; kept as the alternate.** #40 could install only PyPI packages, and
  Vadere needs Java. It is the one to add if the supervisor wants a testbed that differs from negsim
  in *time* as well as in motion.

### Menge (University of North Carolina)

- **What it is:** a C++ crowd framework (Apache-2.0) in which every part is a plug-in. Behaviour is a
  **behavioural finite state machine**: each agent is in a state (say "walk to the queue", "wait",
  "board"), and a transition fires when its *Condition* holds (a timer runs out, a region is
  reached) and moves the agent to its *Target* state. The state gives a goal and a preferred
  velocity, and a swappable pedestrian model (social force variants, ORCA and others) turns it into
  an actual velocity. It also has an event system, an `ExternalEvtTrigger`, "the mechanism through
  which larger systems can influence the simulation", and a plug-in for boarding and leaving an
  aircraft.
- **But** it has been dormant since 2019, and needs a C++ build with Visual Studio.
- **Verdict: not shortlisted; a design reference.** Its external triggers and its boarding plug-in
  are worth reading when the adapters are designed.

### Mesa

- **What it is:** a general agent-based modelling framework in pure Python (3.12 or later;
  Apache-2.0; version 3.5.1). It has **no walking at all**: you write what each agent does. Space can
  be discrete (grids, hexagons, networks) or continuous. Time passes in steps (`step()` every 1.0
  time unit) or by **events**: `schedule_event(self.newcomer_arrives, at=30.0)` runs a function at
  t = 30.
- **Why it suits a queue:** queue cutting is a conflict about *order*, not space. In a discrete
  model, arrival order and time waited are plain values, which a continuous simulator can only
  approximate.
- **Verdict: shortlisted, tried, and proposed** as the discrete queue testbed.

### The rest, briefly

| Simulator | What it is | Verdict, and why |
|---|---|---|
| **RVO2** | ORCA's reference C++ library | **not a testbed**: it is the very model negsim uses (negsim's linear program is adapted from it, with its notice), so it cannot show a portability problem |
| **pedsim_ros** | social-force pedestrians for ROS, the robotics framework | **not used**: ROS is outside this project's tools, and nothing has been committed since 2020 |
| **SteerSuite** | SteerBench's test cases, plus a C++ steering library | **its test cases are borrowed** for the cards (section 17); dormant since 2018, so not a host |
| **Sumonity** | SUMO joined to the Unity game engine, with a model of boarding a city bus (4 door layouts × 1 to 50 passengers = 200 scenarios) | **cited only**: Unity is too heavy for a testbed, but its door layouts are useful for a boarding card |
| **MassMotion** | commercial pedestrian software (Oasys), with an SDK | **reference only**: paid and closed |
| **AnyLogic Pedestrian Library**, **Pathfinder** | commercial tools | **could not be read** (refused, and timed out), so nothing is claimed about them |

### The shortlist

The trial of #40 was allowed to install only released, pinned PyPI packages, in a new environment:
no Java, no C++ builds, no running a cloned repository. With that, and what each candidate offers:

| Candidate | Installable? | Role |
|---|---|---|
| JuPedSim 1.4.2 | yes (`jupedsim`) | 1st: the second continuous testbed, and the host for queues and waiting |
| Mesa 3.5.1 | yes (`Mesa`) | 2nd: the discrete queue model |
| SUMO 1.28.0 with JuPedSim | yes (`eclipse-sumo`) | 3rd, and only if JuPedSim's door trial lacked something a vehicle model gives |
| Vadere | no (Java) | the alternate |
| Menge | no (C++) | a design reference |
| CrowdGym | no (code not shared) | the target, not a trial candidate |

## 21. Other simulators by hand, and the use-or-build decision (PT-6, issue #40)

The user allowed throwaway trial code for this issue ("Yes, proceed"). That is the user's answer,
not a recorded approval by the supervisor: the standing instruction stays unconfirmed.

- **Set-up:** a new virtual environment, `integration/simulator-survey/spikes/.venv`, with
  `jupedsim==1.4.2`, `Mesa==3.5.1` and `networkx==3.7`, installed as wheels only
  (`--only-binary=:all:`), so that no setup or build script could run. It is git-ignored, and takes
  about 1.3 GB, because JuPedSim brings the libraries of its viewer.
- **The code:** ten small scripts in `integration/simulator-survey/spikes/`, 27 to 95 lines of code
  each. Nothing else in the repository imports them.
- **Nothing here is evidence about people.** Every scene uses the models' default parameters and
  made-up geometry.

**To run examples 12 to 14 yourself,** open a terminal in `integration\simulator-survey\spikes` and
use that environment's Python, as in `.venv\Scripts\python mesa_trial1_queue.py admit`. If the
`.venv` folder is missing (it is not in git), make it first, in the same folder:

```
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install --only-binary=:all: -r requirements.txt
```

### Trial 1: a queue with a newcomer

Ten people queue at a counter that serves one person at a time. At 30 s a newcomer arrives beside
place 3 and asks to join ahead of it. Can each simulator *admit* them (let them in at place 3) and
*refuse* them (send them to the back)?

**Example 12: JuPedSim's built-in queue keeps someone who has left.**

```
.venv\Scripts\python jps_probe_queue_switch.py
```

```
before switch       [1, 2, 3, 4, 5] targeting 5
right after switch  [1, 2, 3, 4, 5] journey of id 3 = 2
after 1 iteration   [1, 2, 3, 4, 5] targeting 4
after 5 s           [1, 2, 3, 4, 5] pos (3.6, 5.0)
after pop + 5 s     [2, 3, 4, 5] agents left 4
```

Read it like this:

- Five people (ids 1 to 5) stand in JuPedSim's built-in queue, a `NotifiableQueueStage`.
  `enqueued()` lists them in order.
- Person 3 is switched to another journey and walks 2 m away, to (3.6, 5.0). The queue even
  notices that only 4 people are now heading for it ("targeting 4"). Yet `enqueued()` still lists
  person 3, and the people behind do not move up.
- Only `pop(1)`, serving the person at the front, removes an entry. Person 1 is served and leaves
  ("agents left 4"), and person 3 is *still* listed.
- The other ways of admitting someone through the built-in queue (`jps_trial1_queue.py`) failed
  too. Steered into the gap, the newcomer wedged in beside the line and was never served. Removing
  people and adding them back left the removed ids listed, and queued the re-added people in the
  order they reached the queue (P10, P9, NEW, P8, ...), not the order they were added.

So the built-in queue is **first in, first out only**: join at the back, leave at the front.
"Admit" cannot be built on it, and nor can leaving the line part-way. The stale entries look like a
defect, but JuPedSim's issue tracker was not checked. **Status: not used wherever the order can
change.**

**Example 13: our own queue order, with JuPedSim moving the people.**

Here the order lives in a Python list that our script owns. Every queuer is on a direct-steering
journey, and on every iteration each is steered to the slot of its place in the list. The scene,
from `jps_trial1_ownqueue.py`:

```python
sim = jps.Simulation(model=jps.CollisionFreeSpeedModel(),
                     geometry=shapely.Polygon([(0, 0), (20, 0), (20, 8), (0, 8)]), dt=DT)
steer_id = sim.add_direct_steering_stage()
steer_journey = sim.add_journey(jps.JourneyDescription([steer_id]))
exit_id = sim.add_exit_stage(shapely.Polygon([(0, 2), (1, 2), (1, 4), (0, 4)]))
exit_journey = sim.add_journey(jps.JourneyDescription([exit_id]))

def spawn(pos):
    return sim.add_agent(jps.CollisionFreeSpeedModelAgentParameters(
        position=pos, journey_id=steer_journey, stage_id=steer_id))
```

And the decision point, inside the script's time loop:

```python
if newcomer is None and t >= NEWCOMER_AT_S - 1e-9:
    newcomer = spawn((slots[2][0], 5.0))
    names[newcomer] = "NEW"
    print(t, "newcomer arrives; line", [names[a] for a in line])
    # --- the decision point an action adapter would fill ---
    if decision == "admit":
        line.insert(2, newcomer)
    else:
        line.append(newcomer)
for i, aid in enumerate(line):                     # perception -> action, every step
    sim.agent(aid).target = slots[i]
sim.iterate()
```

`.venv\Scripts\python jps_trial1_ownqueue.py admit` printed:

```
10.0 ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10']
20.0 ['P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10']
30.0 ['P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10']
30.0 newcomer arrives; line ['P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10']
40.0 ['P4', 'P5', 'NEW', 'P6', 'P7', 'P8', 'P9', 'P10']
50.0 ['P5', 'NEW', 'P6', 'P7', 'P8', 'P9', 'P10']
60.0 ['NEW', 'P6', 'P7', 'P8', 'P9', 'P10']
60.0 newcomer served
70.0 ['P6', 'P7', 'P8', 'P9', 'P10']
80.0 ['P7', 'P8', 'P9', 'P10']
```

and with `refuse`:

```
10.0 ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10']
20.0 ['P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10']
30.0 ['P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10']
30.0 newcomer arrives; line ['P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10']
40.0 ['P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'NEW']
50.0 ['P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'NEW']
60.0 ['P6', 'P7', 'P8', 'P9', 'P10', 'NEW']
70.0 ['P7', 'P8', 'P9', 'P10', 'NEW']
80.0 ['P8', 'P9', 'P10', 'NEW']
newcomer final position (4.4, 3.0) index 3
```

Read it like this: one person is served every 10 s. Admitted, the newcomer is third in line from
the moment they arrive, and is served at 60 s. Refused, they join the back, and at 80 s they are
still fourth, standing at (4.4, 3.0). The people behind stepped back to let the newcomer in, and in
the trial nobody came closer than 0.795 m to anyone. Admit and refuse are one line each
(`line.insert`, `line.append`); the queue logic around them is about 15 lines, and the whole script
is 47. **Status: proposed**, as "our own queue-order layer": JuPedSim moves the people, and we own
the order.

**Example 14: the same newcomer in Mesa.**

Mesa supplies nothing queue-specific, so here too the line is a Python list. Service takes a random
time (exponential, mean 10 s) drawn from the model's seeded random generator; other people join the
back at random intervals; and the newcomer is an event scheduled for t = 30. From
`mesa_trial1_queue.py`:

```python
self.schedule_event(self.serve, after=float(self.rng.exponential(10.0)))
self.schedule_event(self.background_arrival, after=float(self.rng.exponential(12.0)))
self.schedule_event(self.newcomer_arrives, at=30.0)
```

```python
# ---- action adapter ----
def apply(self, decision, newcomer, asks_position):
    if decision["action"] == "admit":
        self.line.insert(asks_position - 1, newcomer)
    else:
        self.line.append(newcomer)
```

`.venv\Scripts\python mesa_trial1_queue.py admit` printed:

```
14.527 served P1
16.92 joined back B1
29.478 joined back B2
30.0 admit NEW now at 3
30.323 joined back B4
45.77 served P2
49.639 served P3
51.099 joined back B7
52.945 joined back B8
56.727 joined back B9
61.954 served NEW
66.084 served P4
67.541 joined back B12
78.558 served P5
same seed, same log: True
other seed, different log: True
```

With `refuse`, four lines change: `30.0 refuse NEW now at 12`, `61.954 served P4`,
`66.084 served P5` and `78.558 served P6`. Every other line is the same.

Read it like this:

- Admitted, the newcomer is third and is served at 61.954 s; refused, they are twelfth.
- **Every arrival and every service time is the same in both runs.** The decision uses no random
  numbers, so the two policies are compared on identical days: the paired seeds of section 11, for
  free.
- The last two lines are the determinism check: the same seed gives the same log, and another seed
  a different one.
- The script holds the two adapters in miniature: `situation()` builds a plain dictionary (the
  conflict type, the order, each person's time waited and age), `decider()` stands in for the rule
  engine, and `apply()` inserts or appends.

### Trial 2: a bus or train door

In JuPedSim: a platform and a vehicle joined by one 1.0 m opening; 8 boarders in a waiting set; 8
alighters who appear inside at "arrival". Seconds from arrival until everyone is through, one
deterministic run each:

| Policy | CFS | Social force |
|---|---|---|
| alight first (boarders released at 13.7 / 13.9 s) | 22.1 | 27.0 |
| at the same time, boarders waiting beside the door | 30.0 | 54.3 |
| at the same time, boarders waiting in front of the door | 35.2 | 56.0 |

- **What worked:** waiting (a waiting set), release (setting it inactive), and two-way flow through
  one door. No deadlock in any of the six runs.
- **What was missing:** a vehicle. "Arrival" is a scripted appearance, and capacity and dwell time
  would be a counter and a timer in our loop.
- **Mesa** made the door a resource that one person can use at a time, with a priority rule:
  alighting first took 17.8 s (the median of 30 seeds), against 26.7 s for a random side. But the
  cost of a change of direction (1.5 s) was an *input*, so that difference was assumed, not found.
  In a discrete model the cost of a door conflict has to be given; in JuPedSim it comes out of the
  motion.
- Either way, "alighting first is faster" is a property of a model in one scene, not a finding
  about passengers.
- **Why SUMO was not tried:** all it would have added here (arrival times, capacity, dwell time) is
  a timer and a counter in our loop.

### Trial 3: the two adapters, in miniature

- **Perception works:** positions; velocity (the social force model stores it; under CFS it is the
  difference of two positions, and the two agree to 1.8 × 10⁻¹³ m/s over 59,642 samples); and each
  person's place in the queue.
- **Action works**, with these delays before the effect shows:

| Action | CFS | Social force |
|---|---|---|
| switch an agent's journey | 0.01 s (one iteration) | 0.33 s |
| lower `desired_speed` from 1.2 to 0.4 m/s | 0.01 s | 1.5 s |
| a new target for a direct-steering agent | 0.01 s | 0.16 s |
| `agent.target` for an agent *not* on direct steering | **silently ignored** | **silently ignored** |

The social force delays come from the model's reaction time, not from the API. The last row is a
trap: the run is bit-identical to one with no action, and no error or warning appears. An action
adapter that did not know each agent's journey type would drop decisions without anyone noticing.

### Trial 4: scale

| What was timed | At 10,000 agents | What it means |
|---|---|---|
| JuPedSim, two-way flow, CFS | 40.77 ms per 0.01 s iteration; 10 simulated seconds took 46.9 s: **0.21 simulated s per computing s** | negsim manages 0.062 to 0.073, so JuPedSim is about **2.9 to 3.4 × faster**: on a similar, not identical, scene, with no rule layer in either, and still slower than real time |
| JuPedSim, one perception pass in Python | about 32 ms, as long as an iteration | perception should sample every 10th iteration (every 0.1 s, negsim's step) |
| Mesa, a queue driven by events | 15.5 µs per event, whatever the number of agents | events stay cheap as the crowd grows |
| Mesa, every agent deciding on every step | 14 ms per step with stored queue places; 104 ms when each place is looked up with `list.index` | queue places must be stored, never searched for |

### Determinism, logging and surprises

- **Both simulators are deterministic.** JuPedSim gave bit-identical trajectories in one process
  and in two, and needs no seed for a scene without randomness. Mesa: example 14.
- **JuPedSim's ids come from a counter shared by the whole process**: a second simulation in the
  same program starts at agent id 4, not 1. So runs must be compared by the order in which people
  were added, not by id. (#40's first determinism check failed for exactly this reason.)
- **Logging.** JuPedSim's SQLite writer records positions and orientations only, and loses a short
  run unless `close()` is called (it commits every 100 writes). Mesa's `DataCollector` gives tables
  of whatever you ask for. In both, the log of conflict decisions (who asked, who decided, what was
  applied) would be ours to write, as negsim's is.
- **Mesa's surprises.** `import mesa` failed on a clean install of 3.5.1 until `networkx` was added
  by hand (it is listed only as an optional extra). `Model(seed=...)` is deprecated in favour of
  `rng=`. Scheduled callbacks are held by *weak reference*, so a `lambda` disappears at once
  ("function must be alive at Event creation"). And `run_until(1e9)` also runs the default `step()`
  every time unit: a billion empty steps.

### The decision: use, build, or both

There are three roles to fill: **R1**, a second continuous testbed; **R2**, a discrete testbed
(queue cutting); **R3**, a host for boarding. negsim stays as it is in every option.

| Option | R1, continuous | R2, discrete | R3, boarding |
|---|---|---|---|
| **(a) use** | JuPedSim, built-in stages only | Mesa | JuPedSim's door |
| **(b) refer and build** | negsim, extended with a second motion model, queues and vehicles | our own discrete queue model | negsim, extended |
| **(c) hybrid** | JuPedSim for the motion, with **our own queue-order layer** | Mesa | JuPedSim's door, with our vehicle timer and counter |

Each option was scored from 1 to 5 on seven criteria, with **proposed** weights: what the FYP's
claim needs, namely each unseen conflict type in at least two structurally different testbeds
(weight 25); effort (20); risk (15); credibility in a report (15); speed at 10,000 agents (10); fit
with CrowdGym (10, and conditional); and reproducibility (5).

**Example 15: how the totals are worked out.**

```python
# The weights and scores of integration/simulator-survey/decision.md (all proposals).
weights = {"claim": 25, "effort": 20, "risk": 15, "credibility": 15,
           "speed": 10, "crowdgym": 10, "reproducibility": 5}
scores = {
    "(a) use":             [2, 4, 2, 4, 4, 4, 4],
    "(b) refer and build": [2, 1, 2, 2, 2, 2, 4],
    "(c) hybrid":          [5, 3, 3, 4, 4, 4, 4],
}

def total(option, drop=None):
    pairs = [(w, s) for (name, w), s in zip(weights.items(), scores[option]) if name != drop]
    return sum(w * s for w, s in pairs) / sum(w for w, _ in pairs)

for option in scores:
    print(f"{option:20} {total(option):.2f}   without the claim criterion: {total(option, 'claim'):.2f}")
```

```
(a) use              3.20   without the claim criterion: 3.60
(b) refer and build  1.90   without the claim criterion: 1.87
(c) hybrid           3.90   without the claim criterion: 3.53
```

Read it like this: each total is the sum of weight × score, divided by the sum of the weights.
(c) leads with 3.90. Dropping any other single criterion leaves (c) ahead (`decision.md`,
"Sensitivity"), but without "each unseen conflict type in two testbeds", (a) edges ahead, 3.60
against 3.53. So **one question decides the answer**, and it is the supervisor's: must each
held-out conflict type run in two different testbeds? (Decision 8, section 22.) (b) comes last
under every weighting tried.

**The recommendation (a proposal): option (c).**
- **R1: JuPedSim 1.4.2**, CFS by default, social force as a second motion model.
- **R3: JuPedSim**, the door with a scripted vehicle.
- **R2: Mesa 3.5.1**, with `networkx` pinned, keeping the queue logic to plain lists and
  `schedule_event`, in case Mesa's API keeps changing.
- **Not now:** SUMO, Vadere, Menge.

**Five rules for any adapter**, learnt in the trials:
1. know each agent's journey type before setting a target, and log a decision as applied only once
   it took effect (trial 3);
2. sample perception every 0.1 s, not every 0.01 s iteration (trial 4);
3. store queue places; never search for them (trial 4);
4. compare runs by the order people were added, not by id;
5. write the conflict-event log ourselves, and close JuPedSim's writer.

## 22. The verdict, the corrected idea and the decisions (PT-7, issue #41)

PT-7 read PT-1 to PT-6 together and wrote four documents, in `portable_rules/docs/`. It searched no
new literature.

### A verdict for each part

| Part of the idea | Verdict | The change it needs |
|---|---|---|
| 1. Core and vocabulary | feasible with changes | adapt IG 2.0; define every term operationally; add breach handling and observer roles |
| 2. Adapters and bindings | feasible with changes | today's rules cannot become the ORCA binding "unchanged": their *when* conditions must move |
| 3. Engine and conformance tests | feasible with changes | promise the same decision, not the same behaviour; tests find faults, they do not prove conformance |
| 4. Trained deciders | feasible with changes, narrowed | optional and secondary: small trees against a lookup table only; no reinforcement learning |
| 5. Testing on unseen scenarios | feasible with changes; human fidelity not supported for two of the five scenarios | score "is it what people do?" only where graded evidence exists, and elsewhere only "does it clear?"; results are case studies |
| 6. Testbeds | feasible with changes | JuPedSim needs our own queue-order layer; CrowdGym stays conditional |

**No part is rejected outright. Five sub-claims are not supported**, and must be dropped or
narrowed:
- the same behaviour in every simulator;
- conformance proved by passing tests;
- today's rules as an unchanged ORCA binding;
- human fidelity for bus boarding and escalators;
- reinforcement-learning policies, or an LLM at run time, as portable deciders.

**Two findings that only show when the PT files are read together:**
- **S1. No LLM-elicited rule exists yet** (example 10). Everything can be built and checked on the
  six seed rules, for free, but a result about LLM-elicited rules needs the pilot first.
- **S2. The best human evidence is about behaviour the vocabulary cannot yet express** (section
  18): bystanders objecting, asking with a reason, roles given by a category.

### The idea, corrected

In PT-7's own words: "A rule states *who must, may or must not do what, in which kind of conflict*,
using a small, fixed list of words that any simulator can be taught to read. Each simulator gets two
small translators: one describes its scene in those words, the other carries out the decision. A
separate rule engine makes the decision." The claim is narrow: in the same kind of conflict, a rule
gives the same *decision* in any simulator that passes the shared tests, and how people then move
is measured, not promised.

The ten changes from #34:

| | Change | Why |
|---|---|---|
| C1 | promise decision conformance; measure behaviour | identical rules gave different trajectories; every docking study found differences |
| C2 | a rule applies to one *sub-type*; crossing sub-types is a logged test | #34's own example crossed from passage to queue |
| C3 | IG 2.0's shape, adapted; terms defined operationally; breach handling and observer roles; arrival order split into predicted and recorded; time in seconds | the terms already disagree inside #34 (F4); queue cutting is a breach (F9) |
| C4 | today's rules are **not** the ORCA binding unchanged: their *when* conditions move into negsim's perception adapter, which is then tested as a decision, and an identity check shows nothing changed | those conditions are negsim measurements |
| C5 | tests show faults, not conformance; scene tests written per simulator; long closed-loop runs | reference tests miss what they do not test |
| C6 | trained deciders narrowed to small trees against a lookup table, with the engine as reference and shield | reinforcement learning needs a policy per simulator; an LLM at run time is too slow |
| C7 | PT-2's protocol changes; fidelity scored only where evidence exists; borrowed evidence labelled with city and year; results as case studies | queue B, doors B/C, lifts B, bus none, escalators weak; no Singapore data |
| C8 | JuPedSim with our own queue layer, plus Mesa; no SUMO; CrowdGym only once its code is available | JuPedSim's queue cannot admit anyone part-way |
| C9 | **new:** every result says whether its rules were hand-written seeds or LLM-elicited | S1 |
| C10 | **new:** the vocabulary must reach the evidence (observer roles, roles by category) | S2 |

**The worked example, corrected.** `single_file_first_arrival` becomes: "in a one-at-a-time
*passage*, the claimant with the earliest *predicted* arrival proceeds; the others wait." Applying it
to a queue, where arrival is *recorded* and "wait" means joining the back, is no longer "the same
rule". It is an **L3 transfer test**, run on purpose and reported either way.

### What is new, and what the evidence does not support

The closest prior work, **Zhang et al. 2026** (NTU), distils an LLM-driven crowd into code that plain
agents run. But it works in one simulator, with that simulator's own features; its "out-of-domain"
test is a new layout of the same evacuation task (level L2, not a new conflict type); and it is
checked against the LLM, not against people. The track's new part is the combination of section 16.

The evidence does **not** support any of these:
- the same behaviour in every simulator, or passing tests as proof of conformance;
- transfer to unrelated kinds of conflict, or statistical generality (only five conflict types);
- Singapore-, age- or gender-specific realism in these scenarios;
- trained models beating the rules;
- the portable pipeline running 10,000 agents in real time (no end-to-end run exists);
- any claim that the tests show LLMs "understand" people: they test the extracted rules.

### The ten decisions for the supervisor

`portable_rules/docs/supervisor-brief.md` (two pages, no jargon) asks:

| # | Decision | Recommended |
|---|---|---|
| 1 | the claim | "the same kind of conflict, in any simulator", with behaviour measured against a standard set in advance |
| 2 | the vocabulary | freeze its first version before any unseen test; define each term precisely, including rule breaking and who reacts |
| 3 | more than two people, and roles by category | allow both |
| 4 | may a rule depend on a stated reason? | allow the *kind* of reason (none, self-serving, genuine) as an observable feature |
| 5 | the testbeds | the hybrid: negsim; JuPedSim with our queue-order layer; Mesa |
| 6 | seen and held-out conflicts | fix the split before extracting any rule. Seen: passing and narrow passages. Held out: queues, vehicle doors, lift capacity |
| 7 | trained models | optional and secondary: small trees against a lookup table, with the rule engine as the reference; plus a list of which personal attributes must **not** change each decision |
| 8 (new) | must each held-out conflict run in two different simulators? | yes: the claim needs it, and it is the only choice that changes the simulator recommendation |
| 9 (new) | what counts as human evidence? | foreign evidence labelled with its city and year, and tables reproduced verbatim in later work; obtain fourteen papers through the library |
| 10 (new) | the go-ahead and the order of work | confirm the "no new simulation code" instruction is lifted for this track; approve a small, capped pilot *after* the vocabulary is frozen; obtain CrowdGym's code or its dependency list |

### What happens next (a proposal)

```
gate (supervisor) → PT-8 → engine + negsim adapters ─┬→ evaluation harness → prompt v3 + pilot → trained deciders (if in scope)
                                                      └→ cards + testbeds ──┘
CrowdGym binding: blocked until CrowdGym's code or dependency list is available
```

- **A gate first.** The supervisor answers decisions 1 to 10, and confirms that the standing
  instruction is lifted, because PT-8 writes code.
- **PT-8** writes vocabulary version 0 and the core's format, and runs a **paper test**:
  - hand-convert the six seed rules into cores;
  - try to write a core, or a pass criterion, for each graded behaviour (QC-1 to QC-8, BA-1, BA-2,
    BA-4, LE-1, LE-2), and record which cannot be written, and why;
  - confirm that the L4 candidate, a signalised crossing, falls outside the vocabulary.
- **The rule engine and negsim's two adapters**, with an **identity check** as the acceptance test:
  the six seed rules, run through the new engine on the seeds and configurations of issue #28's free
  runs, must give identical decisions *and* identical trajectories. The adapters must wrap negsim
  from outside, because the track may not change `llm_negotiation/` without saying so first.
- **Then the scenario cards and testbeds, and the evaluation harness**, all rehearsed on the seed
  rules, for free.
- **Only then the first paid step:** prompt version 3 and the pilot, which would produce the first
  LLM-elicited rules, already in the portable form.

## 23. Concepts from elsewhere: used, tried, proposed, not used, and why

This section gathers in one place every idea from another simulator, or from the literature, that
sections 15 to 22 mention, and says what this project does with it.

| Status | Means |
|---|---|
| **Used** | in negsim's code today (issues #24 to #32) |
| **Tried** | run in the throwaway trials of issue #40; nothing in the project imports them |
| **Proposed** | recommended by track #34 and waiting for the supervisor; not built |
| **Borrowed** | one part taken into a proposal (a field of the scenario card, say) |
| **Reference** | read for design ideas; not run |
| **Not used** | considered and set aside, for the reason given |
| **Open** | cannot be decided yet |

### Simulators

| Simulator | Status | Why |
|---|---|---|
| negsim (ours) | **Used** | the reference, and the ORCA testbed |
| CrowdGym | **Open** | the target, but its code is not available, so even its engine is unknown |
| JuPedSim 1.4.2 | **Tried**; **Proposed** | other motion models and a 0.01 s step; both adapter hooks work; deterministic; about 3 × negsim's speed at 10,000 agents |
| Mesa 3.5.1 | **Tried**; **Proposed** | discrete events; order and time waited are plain values; seeded |
| SUMO 1.28.0, with JuPedSim | **Not used** | boarding is a time per person; the door conflict ran in JuPedSim with a timer and a counter |
| Vadere 4.0 | **Not used**; the alternate | needs Java (outside #40's permission); no queues or vehicles; its Python access is unfinished |
| Menge | **Reference** | dormant since 2019, C++ only; its triggers and boarding plug-in are worth reading |
| RVO2 | **Used** (its linear program and its random nudge); not a testbed | it is the same model as negsim |
| pedsim_ros | **Not used** | ROS; dormant |
| SteerSuite | **Borrowed** (its test cases) | dormant; not a host |
| Sumonity | **Reference** | Unity is too heavy; its door layouts are useful for a boarding card |
| MassMotion | **Reference** | paid and closed |
| AnyLogic, Pathfinder | **Not read** | their pages refused automated reading |

### Ideas from simulators

| Concept | From | Status | Why |
|---|---|---|---|
| ORCA: velocity obstacles, half-planes and a linear program | van den Berg et al.; RVO2 | **Used** | section 6 |
| a tiny random nudge to break exact ties | RVO2 | **Used** (`orca_perturbed_v1`) | section 7 |
| the collision-free speed model (CFS) | JuPedSim | **Tried**; **Proposed** as the second testbed's default | differs from ORCA, and may be CrowdGym's model; but stores no velocity |
| the social force model | JuPedSim, Vadere, Menge, pedsim_ros | **Tried**; **Proposed** as a second motion model | different dynamics, and it stores velocity; but reacts with a lag of up to 1.5 s |
| generalised centrifugal force, anticipation velocity, WarpDriver | JuPedSim | **Not tried** | not needed for the trials |
| the optimal steps model; event-driven steps | Vadere | **Not used** | needs Java; slower than real time for thousands of people |
| strategic, tactical and operational decisions | JuPedSim's `iterate()` | **Reference** | the usual three levels at which a pedestrian decides |
| journeys of stages and transitions | JuPedSim | **Tried**; **Borrowed** for the card's `journeys` field | the one format that names queues and waiting areas |
| the built-in queue, `NotifiableQueueStage` | JuPedSim | **Not used** where the order can change | first in, first out only, with stale entries (example 12) |
| our own queue-order layer on direct steering | this project (#40) | **Proposed** | admit and refuse are one line each (example 13) |
| the waiting set | JuPedSim | **Tried** (the door) | waiting and release both work |
| `agent.target` and direct steering | JuPedSim | **Tried** | silently ignored outside direct steering: adapter rule 1 |
| the psychology layer: perception → cognition → behaviour | Vadere | **Reference** | the nearest precedent for the adapter → engine → adapter split, but inside one simulator |
| a behavioural state machine over plug-in motion models; external triggers | Menge | **Reference** | one behaviour layer over three motion models gave three sets of trajectories |
| an aircraft-boarding plug-in | Menge | **Reference** | a boarding precedent; not runnable here |
| person plans, `personCapacity`, `boardingDuration` | SUMO | **Not used** | boarding as a time per person |
| TraCI remote control | SUMO, Vadere | **Not used** | neither simulator is used |
| event scheduling: `schedule_event`, `schedule_recurring` | Mesa | **Tried**; **Proposed** | the queue model's clock |
| discrete spaces: grids, networks | Mesa | **Proposed**, if needed | a queue is an order, not a floor |
| `DataCollector`; JuPedSim's SQLite writer | Mesa; JuPedSim | **Tried** | neither records decisions, so the conflict log is ours |
| the per-step hook `RL_take_action` | CrowdGym | **Open** | the natural place for CrowdGym's action adapter |
| one behaviour engine inside several host simulators | HuNavSim 2.0 | **Reference** | runs in four simulators, compares nothing |

### Ideas for writing a rule down

| Concept | From | Status | Why |
|---|---|---|---|
| ADICO; IG 2.0 | Crawford and Ostrom; Frantz and Siddiki | **Proposed**, adapted | its parts map onto the core; but it has no execution semantics, and its term lists are open |
| activation condition against execution constraint | IG 2.0 | **Proposed** | keeps *when* a rule applies apart from *how* the action is qualified |
| the Or else as a nested rule | IG 2.0, from nADICO | **Proposed** | needed for breaches such as queue cutting |
| profiles | the IG 2.0 codebook | **Proposed** | a rule set declares its vocabulary version and features |
| deactivation, deadline, violation handling, roles for observers | Mellema and Dignum | **Proposed** | queue cutting is a breach that bystanders react to |
| deontic logic, condition-action pairs, strategies | normative multi-agent systems | **Not used** | each runs only inside one system |
| norm records in natural language | CRSEC | **Not used** | readable only by an LLM |
| temporal logic over a fixed list of predicates | TR2MTL | **Reference** | the closest *shape*; its commonest error, wrong connectives, becomes a validator for prompt version 3 |
| one compiled implementation behind a small typed interface; units as SI powers; semantic versioning | FMI | **Borrowed** (the shape) | the rule engine's idea; FMI itself moves models, not rules |
| HLA | simulation interoperability | **Not used** (an analogy) | exchanges data, and reaches only the syntactic level |
| LCIM's levels | Wang, Tolk and Wang | **Used as a lens** | the adapters' job is semantic |
| docking, and its three standards of equivalence | Axtell et al. | **Proposed** | choose numerical, distributional or relational equivalence before testing |
| physical against knowledge conflicts | Tessier et al. | **Borrowed** (the top level of the conflict types) | a passage is a physical constraint; a queue is a norm that can be broken |
| scenario names from robot navigation | Francis et al. | **Reference** | geometric names only; no queue and no boarding |

### Ideas for testing on unseen scenarios

| Concept | From | Status | Why |
|---|---|---|---|
| substrate plus background population; resident and visitor modes; the "exploiter" ceiling | Melting Pot | **Borrowed** (L0b, and the ceiling baseline) | but it never holds out a world |
| holding out a whole conflict type | this project | **Proposed** | no precedent: the FYP's own design |
| levels L0 to L4, with the W and C axes | #34, changed by PT-2 | **Proposed** | L4 (abstain) has no source behind it |
| Background / Aim / Setup; acceptance bands | RiMEA 4.1.1 | **Borrowed** | its tests are rebuilt by hand; no queues or vehicles |
| population by age, gender and mobility; 10 populations × 5 repeats | IMO MSC.1/Circ.1533 | **Borrowed** | the nearest precedent for the persona axes; Circ.1238 is superseded |
| geometry / scenario / expected result / test method; context of use | NIST TN 1822 | **Borrowed** | an open precursor of ISO 20414 |
| ISO 20414 | ISO | **Not read** | paywalled |
| a starting state, events fired by triggers, a stop condition | OpenSCENARIO 1.4 | **Borrowed** | built for road users |
| patterns, including those expected to fail; experiments kept apart from models | ODD | **Borrowed** | describes models, not tests |
| each agent's start, goal and pass/fail; scoring from trajectories only | SteerBench | **Borrowed** | no personas |
| counterfactual variants; new variants; small perturbations | Wu et al.; Aher et al.; Binz and Schulz | **Proposed** (the W and C axes) | leakage can be graded, never ruled out |

### Ideas for trained deciders

| Concept | From | Status | Why |
|---|---|---|---|
| the rule engine as the reference decider | PT-4 | **Proposed** | cheap and readable |
| an LLM-filled lookup table | Chopra et al.; GenWorld | **Proposed** (the baseline) | reached millions of agents |
| small decision trees and rule lists | VIPER; Rudin | **Proposed** (first to train) | readable, checkable, and as portable as the rules |
| gradient boosting; small neural networks | PT-4, after Rudin | **Proposed** only if trees miss by a stated margin | usually no gain on structured features |
| LLM decisions distilled into code | Zhang et al. 2026 | **Reference** (the closest prior work) | one simulator; checked against the LLM, not against people |
| a small language model at run time | Amano and Yamaguchi; GenWorld | **Not used** | 0.5 to 2 s per call |
| reinforcement learning with rule rewards; reward machines | SA-CADRL; Icarte et al. | **Not used** now | a policy per simulator; a rewarded norm was kept about 85% of the time |
| shielding | Alshiekh et al. | **Proposed** | the engine blocks whatever breaks a hard rule |
| fairness through unawareness | Kusner et al. | **Used** ("no rule may read `ethnic_group`", issue #32), but not enough on its own | other inputs can carry the attribute |
| counterfactual fairness; the counterfactual gap; asymmetric counterfactuals | Kusner et al.; Garg et al. | **Proposed** (B2 to B5) | the decision must not change with an attribute that must not matter |
| a factorial test of the teacher | Tamkin et al. | **Proposed** (B6) | for `ethnic_group`, waits for the ethics sign-off |
| several LLMs as teachers | Plaza-del-Arco et al. | **Proposed**, with disagreements reported | demographic effects reverse between models |
| rules distilled together with labels | Hu et al. | **Proposed** | helps most when labels are scarce |

## 24. Glossary

| Word | Meaning |
|---|---|
| adapter | in track #34's idea, a small translator between one simulator and the rule engine: the *perception adapter* turns the simulator's state into a Situation, and the *action adapter* turns a Decision into the simulator's own controls (a proposal) |
| ADICO, IG 2.0 | institutional grammar: a way of coding a written rule into who (Attribute), must, may or must not (Deontic), the action (aIm), when (Condition) and what follows a breach (Or else). IG 2.0 is its 2021 revision, whose shape track #34 proposes to adapt |
| agent | one simulated person: a disc with a position, a velocity and a goal |
| arbiter | the part from layer 1 that decides who goes first at a place only one fits |
| back up, back-up manoeuvre | backing out of a passage for the other person, at one's own backing speed, waiting outside, then going on (issue #32) |
| backing speed | how fast a person walks backwards: 0.92 m/s at a normal pace, 0.43 m/s slowly (from one study of ten young adults) |
| baseline | a frozen definition of "plain ORCA", to compare rules against |
| behavioural equivalence | whether two simulators move people the same way after making the same decisions: measured against a standard fixed in advance, never assumed |
| binding | the simulator-specific "how much" of a rule (an ORCA share, how far to step aside, thresholds, timing), declared and frozen for each simulator (a proposal) |
| case | a conflict taken from a finished run and frozen, for LLMs to write rules from |
| CFS | the collision-free speed model, JuPedSim's default: each person steers away from neighbours and slows to keep room to whoever is ahead; nobody is pushed |
| collision | two discs overlapping; its depth is how far they overlap |
| condition A / B | rules negotiated by two LLM agents / stated by one LLM |
| config | a YAML file describing a scenario or an experiment |
| conformance test | a test that a simulator's adapters, or the rule engine, give the expected Situation or Decision. Passing means "no fault found", not "conforms" |
| core, rule core | the part of a rule that no simulator owns: roles, must, may or must not, the action, and when it applies (a proposal) |
| counterfactual test | change only an attribute that must not matter (gender, say), keep everything else the same, and check that the decision does not change |
| decision conformance | the same Situation gives the same Decision in every simulator: track #34's narrowed claim |
| direct steering | JuPedSim's stage in which a script sets each person's target; the only stage in which `agent.target` has any effect |
| directive | an instruction one agent follows for one neighbour (six knobs) |
| docking | re-implementing a model in a second system, to check that it gives the same results |
| `dt` | the length of one time step, 0.1 s |
| encounter class | the kind of meeting: head-on, crossing, overtaking, single-file |
| event-driven | time jumps from one scheduled event to the next, instead of moving in fixed steps (Vadere's optimal steps model; Mesa's `schedule_event`) |
| evidence grade | how strong the human evidence for a reference behaviour is, from A (replicated) to D (theory, or an official norm), with flags such as `old`, `W` (Western) and `repro` (a proposal) |
| fairness through unawareness | never showing a model the protected attribute, which is what "no rule may read `ethnic_group`" does; not enough on its own, since other inputs can carry the attribute |
| fictional group | an invented label (Kestrop, Dremmik, Pellund) a person may belong to; agents may see it, no rule may read it |
| FMI | an engineering standard that lets one compiled model run inside many tools, behind a small typed interface; the shape of #34's rule engine |
| framing word | the words that introduce the group in a prompt ("ethnic group"), a setting of each experiment |
| hash (SHA-256) | a fingerprint of a piece of text: change one character and it changes completely |
| held out | a conflict type kept away from rule extraction and used only for testing (queues, vehicle doors and lift capacity, in the proposed first split) |
| holonomic | able to step in any direction, as a person can |
| journey, stage | JuPedSim's routes: a journey is a network of stages (waypoint, queue, waiting set, direct steering, exit) joined by transitions |
| JSON, JSONL | a text format for data; JSONL is one JSON object per line |
| leakage | an LLM answering from what it has read about a famous situation, instead of reasoning about the one in front of it; it can be graded, not ruled out |
| LLM | large language model, such as DeepSeek |
| lookup table (LLM-filled) | a table from binned Situation features to a decision, filled in advance by asking an LLM many times; PT-4's proposed baseline |
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
| PT-1 to PT-8 | the issues of track #34, #35 to #42; "PT" stands for portable rules |
| re-stepping | making a case's next version by running its source run again to the same moment, checking that every old value comes out the same |
| reference behaviour | a short, testable statement of what people do, with its source, place, year and grade (QC-1, BA-1, LE-1, ...) |
| replay | rerunning a case's own run with one rule switched on |
| rule format version | 1, 2 or 3: what a rule may use; every rule says its version. Version 3 (issue #32) added `back_up` |
| run / experiment | one simulation / many runs from one config |
| scenario | a map plus where each agent starts and wants to go |
| scenario card | a description of one test scenario that no simulator owns, assembled from seven existing formats (a proposal; none exists yet) |
| screening | testing a generated rule in a 100-person crowd |
| seed | a number that fixes the "random" choices, so a run can be repeated exactly |
| session | one case plus two people, for one LLM conversation or statement |
| severity tier | how bad a meeting was, from T0 (nothing happened) to T4 (collision or stuck) |
| shield | a check that blocks any decision that breaks a hard rule: the rule engine over a trained decider (a proposal) |
| Situation, Decision | what the rule engine would read (the conflict type, who holds which role, the feature values) and return (one action per person) |
| social force model | a motion model in which people are pulled towards their goal and pushed away from other people and from walls; in JuPedSim, Vadere and Menge |
| spike | throwaway trial code, here `integration/simulator-survey/spikes/`; nothing imports it |
| staging database | the inbox where generated rules are stored before any promotion |
| Strategy 1 | the fallback "whoever would get there sooner goes first" |
| sub-type | a finer conflict type, such as `exclusive_access.passage`, `.queue` or `.vehicle_door`; PT-7 proposes that each rule applies to one |
| testbed | a simulator the rules are tested in: negsim, and in the proposal also JuPedSim and Mesa |
| token | a piece of text, about 3 characters; what LLM providers charge by |
| track | a group of issues under one tracking issue; track #34 is portable rules |
| transfer level | how far a test is from where its rule was extracted: L0 (new seeds or co-players) to L4 (outside the vocabulary: abstain), plus the wording (W) and convention (C) axes |
| velocity obstacle | the velocities that would lead to a bump within the next few seconds |
| vocabulary | the fixed, versioned lists of conflict types, roles, features and actions that a core may use (a proposal; version 0 is PT-8's job) |
| waiting set | JuPedSim's stage that holds people at fixed spots until a script releases them all at once |
| walking-backwards artefact | ORCA pushing someone backwards when nobody chose it; counted apart from intentional backing |

## 25. Where to read more

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

For track #34 (sections 15 to 23), start with the two-page brief, then each folder's one-page
`verdict.md`:

| Document | Read it for |
|---|---|
| `portable_rules/docs/supervisor-brief.md` | two pages, no jargon: what the track found, and the ten decisions for the supervisor |
| `portable_rules/docs/feasibility.md` | a verdict on each part of the idea, with its evidence and main risk; what is new; what the evidence does not support |
| `portable_rules/docs/idea.md` | the idea restated on one page, with the ten changes from #34 marked |
| `portable_rules/docs/implementation-plan.md` | the proposed order of the next issues (none created yet) |
| `literature/portable-rules/` (`verdict.md`, then `feasibility.md`) | PT-1: how other fields write rules down; docking; the flags F1 to F11 |
| `literature/unseen-scenarios/` (`verdict.md`, `test-protocol-draft.md`, `scenario-standards.md`) | PT-2: the levels, the hold-out, freezing, baselines, metrics and the card's fields |
| `literature/unseen-scenario-evidence/` (`verdict.md`, `reference-behaviours.md`) | PT-3: the 23 graded statements and the grading scale |
| `literature/trained-deciders/` (`verdict.md`, `options.md`, `evaluation.md`) | PT-4: the options table, and the checks E1 to E10 and B1 to B7 |
| `integration/simulator-survey/` (`shortlist.md`, `survey.md`, `comparison.md`) | PT-5: a section per simulator, and the sourced comparison matrix |
| `integration/simulator-survey/` (`hands-on.md`, `decision.md`) | PT-6: every trial, and the use-or-build matrix with its sensitivity table |
| `WORK_LOG-35.md` to `WORK_LOG-41.md` | how each issue was done, with its dead ends, corrections and open questions |
