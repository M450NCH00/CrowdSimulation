# llm_negotiation

A small simulator in which two agents that are about to get in each other's way talk it
over through an LLM, and the outcome of that conversation decides who goes first.

It reimplements GameChat (Mahadevan, Zhang and Chandra, arXiv:2503.12333) and adds three
things: personas with an age and a gender, situational information the agents can see
while they talk (speed, size, distance), and a complete log of every conversation. The
logs are the point: later work will look in them for reusable rules.

Since issue #26 it also has an **avoidance layer**: any number of agents that step round
each other under ORCA, with the manner of avoiding set by a directive, and the same
arbiter taking over where only one agent fits. That layer calls no model. It has its own
section below, "The avoidance layer".

Since issue #28 the directives can come from a **rule database**: stored rules, each a
condition on what two agents can both see, a role for each, and a directive per role,
followed by a rule provider. That calls no model either; see "The rule layer" below.

Built for issues #24, #26 and #28. Nothing here uses the Phase 1 folders `pipeline/` and
`dataset/`.

## How it works, in one list

1. **A scenario** (`configs/scenarios/`) places two agents: a doorway and an intersection
   from the paper, and a head-on hallway only one of them can use at a time.
2. **When the agents see each other they negotiate** (`negsim/negotiation/`). Each turn an
   agent is shown a short report of the situation and what the other said, and replies
   with a message and a stance: `I_GO_FIRST`, `YOU_GO_FIRST` or `UNDECIDED`. Two
   complementary stances in a row are an agreement. Four messages each without one is not.
3. **The agreement decides the motion** (`negsim/conflict/`, `negsim/control/`). The leader
   walks at full speed; the follower is slowed just enough to arrive as the leader clears.
   With no agreement, whoever would get there sooner leads ("Strategy 1").
4. **Everything is logged** (`negsim/runlog/`): the exact prompts, the raw replies, the
   stances, the trajectories, the outcome, and a transcript to read.

The LLM sits behind one interface (`negsim/llm/`) with two implementations: DeepSeek, which
costs money and is held under a hard budget cap, and a deterministic mock, which every
test uses. `docs/architecture.md` has the diagram and the design decisions.

## Install

Developed and tested on Python 3.13.3 and 3.12.3. It should work on 3.10 and 3.11, which were not tested.

```
cd llm_negotiation
pip install -r requirements.txt
```

That is PyYAML, matplotlib (only for the optional trajectory plot) and pytest. The
simulator and both LLM clients use the standard library alone.

## Run the tests

```
cd llm_negotiation
python -m pytest
```

All tests run on the mock client, with the network blocked and the real `.env` out of
reach. They cost nothing. There are 984: the 432 of issue #24, 345 for the avoidance
layer, 18 for the plot and the viewer, and 189 for the rule layer (issue #28).

## Run an experiment

From the `llm_negotiation` folder:

```
python run_experiment.py configs/experiments/c0_no_llm.yaml              # no LLM at all
python run_experiment.py configs/experiments/c1_smoke.yaml --plan        # list the runs and the worst-case cost
python run_experiment.py configs/experiments/c1_smoke.yaml --client mock # rehearse, free
python run_experiment.py configs/experiments/c1_smoke.yaml --client deepseek   # paid
```

Other options: `--limit N` runs only the first N runs; `--overwrite` redoes finished runs;
`--out DIR` writes somewhere else. A run that has already finished is skipped, so an
interrupted experiment can simply be started again.

### Mock or DeepSeek

| | `--client mock` | `--client deepseek` |
|---|---|---|
| What answers | a fixed rule (`llm.mock_policy` in the config) | DeepSeek's API, model `deepseek-flash` |
| Cost | nothing | real money, checked call by call against `budget.cap_usd` |
| Needs | nothing | `DEEPSEEK_API_KEY` in the repository's `.env` (see `.env.example`) |
| Output goes to | `runs_mock/` (git-ignored) | `runs/` (committed) |
| Use it for | checking that a config does what you meant | the experiment itself |

Every shipped config names the mock client, so nothing is spent unless `--client deepseek`
is typed. Before the first paid run of a session, open DeepSeek's pricing page and compare
it with `configs/llm/deepseek_pricing.yaml`; `docs/llm-backend.md` explains why.

The budget guard refuses a call that *could* take the total in `spend_ledger.jsonl` past
the cap, and the experiment stops there. Raise `budget.cap_usd` in the config to go on.

## Where the logs go

```
runs/<experiment_name>/summary.csv              one row per run
runs/<experiment_name>/<run_id>/config.json     everything that defines the run
                                conversation.jsonl   one line per turn: prompt, raw reply, message, stance, tokens, cost
                                trajectory.csv       one row per agent per time step
                                outcome.json         consensus, roles, collisions, times, ...
                                transcript.md        the conversation and the outcome, for reading
spend_ledger.jsonl                              one line per paid call
```

`docs/log-schema.md` describes every field. To see a run rather than read it, see the next
section.

## Watch a run

There is no window that opens while a run is simulated. A run is written to its folder, and
then it can be watched or drawn from there, as often as you like and at no cost.

**The animated viewer** opens a run in your web browser and plays it:

```
python -m negsim.viz.viewer runs\si1_head_on_side_preference                         # every run of an experiment
python -m negsim.viz.viewer runs\si1_bottleneck_handoff\001_opposing_no_directive     # one run
python -m negsim.viz.viewer runs_mock\c1_smoke                                        # your own mock runs
```

It writes one HTML file to `views\` (git ignores the folder; `--out FILE` puts it somewhere
else) and opens it in the default browser (`--no-open` does not). The file holds the run
data and needs nothing else: no server, no internet, no install. It can be sent to someone
and opened on their machine. It shows both kinds of run, the negotiation runs of issue #24
and the avoidance runs of issue #26.

| In the viewer | What it does |
|---|---|
| ▶ Play, ◀ ▶, the slider | play, step one time step, jump to any moment. Keys: space, ← →, Shift+← → for a second, Home, End |
| Speed | 0.1× to 16× real time |
| Run | choose a run, when the file holds an experiment |
| Click an agent | its details: persona, directive, speed, what ORCA or the arbiter is doing to it |
| Drag, wheel, double-click | pan, zoom, fit the scene |
| Events | collisions, near misses, yields, handoffs, violations, arrivals; click one to jump to it |
| Conversation | for a negotiation run, what each agent said and the stance it took |
| Check boxes | trails, intended paths, labels, velocity arrows, the velocity an agent *wanted* (dashed), its sensing radius |

A ring round an agent says what is happening to it: amber, ORCA is changing the velocity it
wants; pink dashed, no velocity was allowed and ORCA's fallback chose; dark, the arbiter
holds it (L leader, F follower); red dashed, its body overlaps another. The legend in the
viewer repeats this. Everything shown is read from the logs. Where a run logged only every
n-th step (the two-way flow logs every tenth), positions in between are drawn in a straight
line, and the viewer says so on screen.

**A still picture** of the paths taken, for a report:

```
python -m negsim.viz.trajectory_plot runs\si1_bottleneck_handoff\001_opposing_no_directive plot.png
```

Without `plot.png` the image goes into the run folder as `trajectory.png`, which git
ignores. It draws both kinds of run; a crowd is coloured by group.

## The conditions

| | What | Config | Scored against hospital > airport > grocery? |
|---|---|---|---|
| C0 | No LLM, Strategy 1 only | `c0_no_llm.yaml` (doorway), `c0_no_llm_intersection.yaml`, `c0_no_llm_hallway.yaml` | yes |
| C1 | GameChat replication: a task, no persona | `c1_smoke.yaml` (6 runs), `c1_gamechat_replication.yaml` (36) | yes |
| C2 | A task and a persona with age and gender | `c2_smoke.yaml` (6 runs), `c2_task_plus_persona.yaml` (16) | no |
| C3 | Same task, personas differing only in age, or only in gender | `c3_age_only.yaml`, `c3_gender_only.yaml` | no |
| C4 | C3 with situational information on, off, or partly on | `c4_info_ablation.yaml` | no |

Persona conditions have no ground truth. Their outcomes are recorded and never marked
correct or incorrect; the config loader refuses to score them.

Each config says in its header what it balances. The factors that could be mistaken for a
persona effect are separate settings, each recorded in every run: who speaks first, which
participant is agent 0, and which side agent 0 starts on.

## Results so far (2026-10-13)

These are smoke runs: they show that the platform works end to end. **Six runs per
condition are not an estimate of any rate**, and the model's replies vary from call to call
even at fixed settings. Every number below can be recomputed from `runs/*/summary.csv`.

### No LLM (C0), 18 runs per scenario

Mean ± population standard deviation. Paper rows are arXiv:2503.12333v1, Table II, method
"GameChat (no LLM)".

| Scenario | Collisions | Deadlocks | Higher-priority agent first | Its time to goal (s) | Makespan (s) | Follower's minimum speed (m/s) |
|---|---|---|---|---|---|---|
| Doorway | 0 | 0 | 9 of 18 | 10.900 ± 0.900 | 11.800 ± 0.000 | 0.257 ± 0.015 |
| *Paper, doorway* | 0 | 0 | 50% | 10.733 ± 0.566 | 11.267 ± 0.194 | 0.200 ± 0.088 |
| Intersection | 0 | 0 | 9 of 18 | 10.600 ± 0.800 | 11.400 ± 0.000 | 0.256 ± 0.016 |
| *Paper, intersection* | 0 | 0 | 50% | 10.800 ± 0.823 | 11.600 ± 0.000 | 0.249 ± 0.013 |
| Hallway (not in the paper) | 0 | 0 | 9 of 18 | 9.750 ± 2.850 | 12.600 ± 0.000 | 0.202 ± 0.037 |

The 9 of 18 is built into the design: Strategy 1 does not look at the tasks, and each agent
index is the higher-priority one equally often. The doorway differs from the paper more
than the intersection does, for the reason given in `docs/gamechat-notes.md` (D4): this
simulator breaks a symmetric tie on the first step, where GameChat's takes a while.

### C1 smoke: GameChat replication, doorway, 6 paid runs

`deepseek-flash`, thinking off, temperature 1.0, template `gamechat_task_v1`,
dialogue before motion.

| Run | Agent 0 is taking someone to | Agent 1 is taking someone to | Speaks first | Turns | Agreed to go first | Higher-priority agent went first |
|---|---|---|---|---|---|---|
| 001 | the emergency room | the airport | 0 | 3 | 0 | yes |
| 002 | catch a flight | the operating room | 0 | 6 | 1 | yes |
| 003 | buy groceries | the operating room | 1 | 4 | 1 | yes |
| 004 | the operating room | the store | 1 | 4 | 0 | yes |
| 005 | go to the airport | the grocery store | 0 | 4 | 0 | yes |
| 006 | the supermarket | catch a flight | 0 | 4 | 1 | yes |

- **Correct-priority rate: 6 of 6.** The paper reports 100% for its communicating
  variants (Table II). This run used a different model and a different turn format
  (`docs/gamechat-notes.md`, section 5), and six runs.
- Consensus in all six; no malformed reply, no retry, no fallback, no collision. Makespan
  11.8 s in every run.
- Time spent waiting for the model: 3.36 s per dialogue on average (SD 0.73 s), 0.81 s per
  call. The paper measured 2.767 s (SD 0.441 s) per dialogue.

Things seen in the transcripts that someone analysing them should know about. They are
my reading of six conversations, not measurements:

- **An agent can concede, or claim the way, without saying so.** In runs 001, 003 and
  004, one of the two stances that made up the consensus came with a message that only
  named the agent's own task ("I am taking someone to the store."). The agreement is
  between the stances, as issue #24 defines it; the spoken exchange does not always
  contain it.
- **Details drift.** In run 003 one agent asked "Where are you taking your patient?" and
  the grocery agent answered "I am taking my patient to buy groceries." The priority came
  out right all the same.

### C2 smoke: task plus persona, hallway, 6 paid runs

Same model and settings, template `persona_v1`, every situation-report field on. **No
ground truth: nothing here is correct or incorrect.**

| Run | Agent 0 (west end) | Agent 1 (east end) | Speaks first | First speaker's stance | Went first |
|---|---|---|---|---|---|
| 001 | woman, 70, to the supermarket | man, 25, to the airport | 0 | gives way | 1 (man, 25) |
| 002 | man, 25, to the airport | woman, 70, to the supermarket | 0 | gives way | 1 (woman, 70) |
| 003 | woman, 25, to the supermarket | man, 70, to the emergency room | 1 | claims the way | 1 (man, 70) |
| 004 | man, 70, to the emergency room | woman, 25, to the supermarket | 1 | gives way | 0 (man, 70) |
| 005 | woman, 25, to the airport | man, 70, to the airport | 0 | gives way | 1 (man, 70) |
| 006 | man, 70, to the airport | woman, 25, to the airport | 0 | gives way | 1 (woman, 25) |

- Consensus in all six, each in two turns; no malformed reply, no fallback, no collision.
  Makespan 12.6 s in every run; 1.67 s per dialogue waiting for the model.
- **In five of the six runs the first speaker opened by giving way and the other
  accepted.** The exception is the 70-year-old man on his way to the emergency room, who
  asked to go first. Who went first therefore tracked who spoke *second* far more closely
  than it tracked age, gender or task. With six runs this is an observation, not a result,
  but it is the confound the design factors exist for: an experiment on personas has to
  counterbalance speaking order, as `c2_task_plus_persona.yaml` and the C3 and C4 configs
  do.
- The personas show in the wording: "You go ahead, dear, I'll wait.", "Thank you,
  ma'am.", "young man", "young lady".

### Spend

37 paid calls, all between 08:15 and 08:17 UTC on 2026-10-13 and so at the peak rate.
**Estimated cost USD 0.0043** (C1 USD 0.00246, C2 USD 0.00182), from the token counts the
API returned and the prices in `configs/llm/deepseek_pricing.yaml`. That is under 1% of
this issue's USD 0.50 cap. The provider's own bill is the authoritative figure.

`spend_ledger.jsonl` records every call. Phase 1's spend is tracked separately, in
`pipeline/config.py`, which this work did not touch.

## The avoidance layer (issue #26)

Everything above settles a conflict in one way: it decides who goes first. This layer adds
the other way, agents that step round each other. Any number of agents are steered by ORCA
(van den Berg, Guy, Lin and Manocha, "Reciprocal n-body collision avoidance"), a
*directive* says how each pair goes about it, and the arbiter above takes over where only
one agent fits. It is the first of six sub-issues. It holds no rule, no rule database and
no call to a model: directives come from a config, and **every run is free**.

1. **Perceive.** Each step an agent attends to its nearest neighbours within a sensing
   radius. When one comes into range the agent builds a *perception record* of it
   (`docs/perception.md`) and asks a *directive provider* for a directive.
2. **Direct.** An `AvoidanceDirective` has five fields: `side_preference` (`left`, `right`,
   `none`), `responsibility_share` (0 to 1; ORCA's own is 0.5), `speed_scale`,
   `clearance_margin` (metres) and `passage_order` (`leader`, `follower`, `none`). The two
   directives of a pair are combined before they are used. A pair that contradicts itself
   is logged as a `reciprocity_violation` and repaired by a fixed policy
   (`docs/derivations.md`, sections 9 to 11).
3. **Avoid.** ORCA picks each agent's velocity: the one nearest what the agent wants that
   every neighbour and every wall allows (`negsim/avoidance/`). Where a single-file segment
   lies ahead of two agents the arbiter decides the order, and ORCA goes on keeping the
   bodies apart (`docs/architecture.md`, section 6.4).
4. **Log.** An avoidance run has its own files, under log schema version 2 (version 3
   since issue #28, which adds the pair interactions and the rules).

ORCA was written from the paper and checked against the source of the RVO2 library, which
was read and not run. The linear-program solver is adapted from that library (Apache-2.0;
`THIRD_PARTY_NOTICES.md`). `docs/orca.md` lists every place where this implementation
departs from the paper or from the library, and why.

### Run it

```
python run_experiment.py configs/avoidance/si1_head_on_side_preference.yaml --plan   # list the runs
python run_experiment.py configs/avoidance/si1_head_on_side_preference.yaml          # run them
python -m negsim.avoidance.benchmark --agents 100 1000                               # time per step
```

`--client` does not apply: no model is called and nothing is added to the spend ledger. A
run is deterministic, so running an experiment again writes the same folder, time stamp
apart.

| Config in `configs/avoidance/` | Scenario | Runs | What it varies |
|---|---|---|---|
| `si1_head_on_side_preference.yaml` | `wide_corridor_head_on` | 14 | exactly head-on or 10 cm off it; plain ORCA, a shared side, opposite sides, extra clearance, reduced speed |
| `si1_head_on_responsibility.yaml` | `wide_corridor_head_on` | 12 | the same two layouts; no side or keep left; shares (0.5, 0.5), (1.0, 0.0) and (0.3, 0.3) |
| `si1_bottleneck_handoff.yaml` | `corridor_to_bottleneck` | 8 | opposing or merging; who the directives say goes first; the arbiter on or off |
| `si1_open_crossing.yaml` | `open_crossing` | 4 | arriving together or half a metre apart; plain ORCA or keep left |
| `si1_overtaking.yaml` | `overtaking` | 6 | exactly behind or 5 cm off; plain ORCA, keep left, or the overtaker keeps clear |
| `si1_bidirectional_flow.yaml` | `bidirectional_flow` | 2 | ten or forty neighbours attended to |

```
runs/<experiment_name>/summary.csv              one row per run
runs/<experiment_name>/<run_id>/config.json     everything that defines the run
                                trajectory.csv       one row per agent per step: where it was, what it wanted, what it did, ORCA or arbiter
                                interactions.jsonl   one line per interaction: the perception record, the directive, what was used
                                events.jsonl         violations, handoffs, yields, near misses, collisions
                                outcome.json         every metric, per agent and in total
```

### Results of the avoidance layer (2026-10-14)

From the 46 committed runs in `runs/si1_*`, made from a clean tree at commit `ac1f0b4` and
run again since with the same output. **Each row is one deterministic run, not a sample**:
there is no randomness to average over and no model. These are statements about what this
algorithm does with these parameters. None of them is evidence about how people walk.
Every number can be recomputed from the `summary.csv` and `outcome.json` files.

Every agent is the same disc: radius 0.25 m, preferred speed 1.3 m/s (except in
`overtaking`), at most 2.0 m/s, looking 3 s ahead. `docs/parameters.md` gives the source
of each number, or says that it has none. *Exposure* is the time during which ORCA had to
change the velocity an agent wanted because of another agent. *Deviation* is the largest
distance an agent got from the line it meant to walk (`docs/metrics.md`).

#### Head-on in a corridor wide enough to pass: plain ORCA against a side preference

Two agents start 16 m apart in a corridor 1.75 m wide. Alone, each would arrive in 12.2 s.

| Layout | Condition | Outcome | Time to goal (s) | Exposure, each (s) | Deviation, each (m) | Smallest gap between the bodies (m) |
|---|---|---|---|---|---|---|
| Exactly head-on | plain ORCA | **deadlock** at 20.4 s | – | 17.4 | 0 | 0.021 |
| | plain ORCA, RVO2's tie-break | **deadlock** at 20.4 s | – | 17.4 | 0 | 0.021 |
| | both keep left | both arrive | 12.2 | 3.2 | 0.251 | 0.004 |
| | both keep right | both arrive | 12.2 | 3.2 | 0.251 | 0.004 |
| | one left, one right | **deadlock** at 20.4 s | – | 17.4 | 0 | 0.021 |
| | both keep left, 0.2 m clearance | both arrive | 12.3 | 3.4 | 0.356 | 0.200 |
| | both keep left, 60% speed | both arrive | 18.7 | 3.3 | 0.252 | 0.005 |
| 10 cm off | plain ORCA | both arrive | 12.2 | 3.2 | 0.202 | 0.005 |
| | plain ORCA, RVO2's tie-break | both arrive | 12.2 | 3.2 | 0.202 | 0.005 |
| | both keep left | both arrive | 12.2 | 3.2 | 0.202 | 0.008 |
| | both keep right | both arrive | 12.3 | 3.3 | 0.301 | 0.001 |
| | one left, one right | both arrive | 12.2 | 3.2 | 0.202 | 0.005 |
| | both keep left, 0.2 m clearance | both arrive | 12.3 | 3.4 | 0.301 | 0.201 |
| | both keep left, 60% speed | both arrive | 18.6 | 3.3 | 0.203 | 0.003 |

- **Exactly head-on, plain ORCA deadlocks.** Both agents are told to brake and neither to
  turn, and they come to rest 2 cm apart. How an exact tie between the two sides is broken
  makes no difference, because the tie is never reached (`docs/orca.md`, section 6). The
  time, 20.4 s, follows from the parameters (`docs/derivations.md`, section 14). RVO2's own
  examples shift every agent's preferred velocity by a random amount "to avoid deadlocks
  due to perfect symmetry".
- **A side that both agree on removes the deadlock, at no cost in time.** Each steps
  0.25 m aside, which together is the half metre two such bodies need, and both arrive at
  12.2 s, as if alone. Keeping left means each steps to its own left, and the two pass
  right shoulder to right shoulder.
- **So does ten centimetres.** In the offset layout plain ORCA passes on the nearer side
  with no directive at all. The deadlock belongs to exact symmetry, which a simulator
  produces easily and which should not be assumed of a real corridor.
- **Opposite sides are logged as a `reciprocity_violation` and then neither is used.** The
  pair behaves as under plain ORCA: a deadlock when exactly head-on, an ordinary pass when
  offset.
- **Without a clearance margin every pass is a near miss** at the default threshold of
  0.1 m: ORCA has two bodies pass a few millimetres apart. A `clearance_margin` of 0.2 m
  gives a gap of 0.200 m.
- **`speed_scale` lasts as long as the other agent is in range**, and the range is the
  12.5 m sensing radius, so the two walk at 60% speed from 1.4 s until 17.5 s, long after
  they have passed. A rule that means "slow down until you are past" will need more than
  this field. *(Issue #28 changed this: `speed_scale` now ends when the encounter has
  passed, `docs/derivations.md`, section 15. Run again with that code, the two "60% speed"
  runs arrive at 15.4 s instead of 18.7 s and 18.6 s; the committed folders are the record
  of the code that wrote them.)*

#### The same corridor: who does the avoiding

| Layout | Side | Shares (agent 0, agent 1) | Outcome | Time to goal 0 / 1 (s) | Deviation 0 / 1 (m) | Exposure 0 / 1 (s) |
|---|---|---|---|---|---|---|
| Exactly head-on | none | (0.5, 0.5) | **deadlock** at 20.4 s | – | 0 / 0 | 17.4 / 17.4 |
| | none | (1.0, 0.0) | both arrive | 24.9 / 12.2 | 0.700 / 0 (a retreat, see below) | 9.2 / 0 |
| | none | (0.3, 0.3), repaired to (0.5, 0.5) | **deadlock** at 20.4 s | – | 0 / 0 | 17.4 / 17.4 |
| | keep left | (0.5, 0.5) | both arrive | 12.2 / 12.2 | 0.251 / 0.251 | 3.2 / 3.2 |
| | keep left | (1.0, 0.0) | both arrive | 12.3 / 12.2 | 0.502 / 0 | 3.3 / 0 |
| | keep left | (0.3, 0.3), repaired to (0.5, 0.5) | both arrive | 12.2 / 12.2 | 0.251 / 0.251 | 3.2 / 3.2 |
| 10 cm off | none | (0.5, 0.5) | both arrive | 12.2 / 12.2 | 0.202 / 0.202 | 3.2 / 3.2 |
| | none | (1.0, 0.0) | both arrive | 12.3 / 12.2 | 0.402 / 0 | 3.3 / 0 |
| | none | (0.3, 0.3), repaired to (0.5, 0.5) | both arrive | 12.2 / 12.2 | 0.202 / 0.202 | 3.2 / 3.2 |
| | keep left | (0.5, 0.5) | both arrive | 12.2 / 12.2 | 0.202 / 0.202 | 3.2 / 3.2 |
| | keep left | (1.0, 0.0) | both arrive | 12.3 / 12.2 | 0.403 / 0 | 3.2 / 0 |
| | keep left | (0.3, 0.3), repaired to (0.5, 0.5) | both arrive | 12.2 / 12.2 | 0.202 / 0.202 | 3.2 / 3.2 |

- **With (0.5, 0.5) the two deviate equally. With (1.0, 0.0) agent 0 does all of it and
  agent 1 none.** 0.251 m each becomes 0.502 m and nothing; when offset, 0.202 m each
  becomes 0.402 m and nothing. The total sideways movement is the same, and the shares
  decide how it is divided. Agent 1 walks its line exactly and is never exposed: ORCA
  never changes what it wants.
- **A share is not a substitute for a side.** Exactly head-on with no side, (1.0, 0.0)
  does prevent the deadlock, but not by a sidestep. Agent 0 **backs away along its own
  line** for 7 s, from 2.9 m short of the middle to 0.70 m behind where it started, while
  agent 1 walks through at full speed. Only when agent 1 has arrived does agent 0 walk the
  corridor, arriving at 24.9 s. The 0.700 m in the table is that retreat. A holonomic
  agent may walk backwards, which is ORCA as published and is not offered as something a
  person does.
- **Shares that sum to less than 1 are logged and repaired.** (0.3, 0.3) is a
  `reciprocity_violation`; it is scaled up to (0.5, 0.5), and the run is then the
  (0.5, 0.5) run exactly.

#### Into a single-file segment: the handoff to the arbiter

A corridor 1.75 m wide narrows to 0.8 m for 4 m, so that only one agent fits. Alone, each
would arrive in 13.8 s.

| Flow | The directives say | To the arbiter at | Leader, and where the order came from | Back to ORCA at | First through | Time to goal 0 / 1 (s) |
|---|---|---|---|---|---|---|
| Opposing | nothing | 2.2 s | agent 0; the arbiter's own rule (`strategy1`) | 9.0 s | agent 0 | 13.8 / 18.0 |
| | agent 1 first | 2.2 s | agent 1; the directives (`negotiated`) | 9.0 s | agent 1 | 18.0 / 13.8 |
| | both "me first" | 2.2 s | agent 0; the arbiter's own rule, and a violation is logged | 9.0 s | agent 0 | 13.8 / 18.0 |
| | nothing, arbiter off | – | – | – | nobody: **deadlock** at 15.2 s | – |
| Merging | nothing | 0.0 s | agent 0; the arbiter's own rule (`strategy1`) | 9.0 s | agent 0 | 13.8 / 17.8 |
| | agent 1 first | 0.0 s | agent 1; the directives (`negotiated`) | 9.0 s | agent 1 | 17.8 / 13.8 |
| | both "me first" | 0.0 s | agent 0; the arbiter's own rule, and a violation is logged | 9.0 s | agent 0 | 13.8 / 17.8 |
| | nothing, arbiter off | – | – | – | nobody: **deadlock** at 8.9 s | – |

- **The handoff occurs and the arbiter's decision is followed** in all six runs with the
  arbiter on. Control passes once each way, the agent named leader is the first into the
  segment, and the leader is not delayed: 13.8 s is its time alone.
- **A `passage_order` in the directives is honoured.** The log calls its source
  `negotiated`, the arbiter's word for an order it was given from outside. Two claims to
  go first are a logged violation, and the arbiter falls back on its own rule, which gives
  an exact tie to the lower index.
- **Without the arbiter, ORCA deadlocks in both layouts.** That is the negative control:
  avoidance alone does not settle who uses a segment only one can use.
- **ORCA is never switched off.** In the opposing runs the follower holds back, 6.5 s at
  under half its preferred speed, and as the leader comes out it steps 0.51 m aside. That
  step is ORCA's, with the follower taking the whole share. The smallest gap between the
  bodies is 7 mm.
- In the merging runs the second agent waits until the first is out of the segment. The
  arbiter was built for agents going opposite ways and does not let one follow another
  through (`docs/architecture.md`, section 6.5).

#### Crossing and overtaking

`open_crossing`: two paths at a right angle with no walls. Alone, each agent would arrive
in 12.2 s.

| Layout | Condition | Outcome | Time to goal 0 / 1 (s) | Deviation 0 / 1 (m) | Exposure, each (s) |
|---|---|---|---|---|---|
| Both would be at the crossing together | plain ORCA | **deadlock** at 28.0 s | – | 1.984 / 1.984 | 25.1 |
| | both keep left | both arrive | 12.0 / 12.4 | 0.134 / 0.092 | 3.3 |
| Agent 1 half a metre later | plain ORCA | both arrive | 12.1 / 12.6 | 0.036 / 0.031 | 3.2 |
| | both keep left | both arrive | 12.1 / 12.6 | 0.035 / 0.031 | 3.2 |

`overtaking`: agent 0 prefers 1.48 m/s and starts 4 m behind agent 1, which prefers
1.10 m/s. Alone they would arrive in 26.9 s and 32.6 s.

| Layout | Condition | Outcome | Time to goal 0 / 1 (s) | Deviation 0 / 1 (m) | Exposure 0 / 1 (s) |
|---|---|---|---|---|---|
| Exactly behind | plain ORCA | both arrive; **no overtaking** | 29.5 / 29.2 | 0 / 0 | 22.9 / 22.9 |
| | both keep left | agent 0 overtakes | 27.1 / 32.4 | 0.231 / 0.269 | 6.3 / 6.3 |
| | keep left, agent 0 takes the whole share | agent 0 overtakes | 27.4 / 32.6 | 0.502 / 0 | 7.0 / 0 |
| 5 cm off | plain ORCA | agent 0 overtakes | 27.2 / 32.4 | 0.211 / 0.239 | 6.4 / 6.4 |
| | both keep left | agent 0 overtakes | 27.1 / 32.4 | 0.211 / 0.239 | 5.9 / 5.9 |
| | keep left, agent 0 takes the whole share | agent 0 overtakes | 27.3 / 32.6 | 0.452 / 0 | 6.4 / 0 |

- **The symmetric crossing deadlocks too, for the same reason.** Seen from either agent
  the other is coming straight at it, so the pair is exactly head-on in relative velocity.
  The two drift diagonally together, 1.98 m off their paths, and stop.
- **At a crossing a side preference acts as a priority rule.** With both keeping left, the
  agent that has the other on its right goes in front (12.0 s) and the other goes behind
  (12.4 s).
- **Exactly behind, the faster agent never overtakes under plain ORCA, and the slower one
  is hurried along.** Both settle at 1.29 m/s: one held back from 1.48, the other pushed
  up from 1.10, because ORCA has the agent in front take half of the avoiding of an agent
  behind it. Neither stops, so this is neither a deadlock nor a yield, and it shows only
  as 22.9 s of exposure. When the overtaker takes the whole share, the slower agent walks
  at its own 1.10 m/s throughout and is never exposed.

#### Fifty each way

`bidirectional_flow`: fifty agents walk each way along a corridor 4 m wide and 50 m long.
They start on a lattice 1 m apart, each moved by up to 0.1 m. Alone, the mean time to goal
would be 33.5 s and the last agent would arrive at 38.4 s.

| Neighbours attended to | Arrived | Mean time to goal (s) | Last arrival (s) | Episodes of two bodies overlapping | Depth of overlap: median / 90th percentile / deepest (mm) | Episodes deeper than 1 cm | Agent-steps with no allowed velocity |
|---|---|---|---|---|---|---|---|
| 10 (the shipped default) | 100 of 100 | 41.0 | 87.7 | 512 | 10.5 / 41.0 / 81.7 | 264 | 13.9% |
| 40 `[placeholder]` | 100 of 100 | 35.3 | 78.6 | 87 | 1.9 / 9.1 / 23.1 | 5 | 8.4% |

- **Everyone arrives, nobody touches a wall, and bodies overlap.** With ten neighbours
  there are 512 episodes of two discs overlapping, the deepest by 82 mm, a third of a body
  radius. The overlaps come from one place. When no velocity satisfies every neighbour,
  ORCA takes the least bad one, and the paper says that this case carries no guarantee.
  All 512 episodes begin on a step on which one of the two agents was in that case. And
  on every step, every pair of agents that perceive each other and both have an allowed
  velocity choose velocities that keep them apart for the next 3 s: 126,621 such
  pair-steps in this run, with no exception (`WORK_LOG-26.md`; the same two checks, on a
  smaller crowd, are tests). **What has not been done is to compare with RVO2's output**,
  because RVO2 was not run, so whether the reference library overlaps as often here is
  not known.
- **The neighbour limit matters a great deal.** With forty in place of ten the episodes
  fall to 87 and the deepest to 23 mm. Ten is what the examples of Menge and of RVO2 use,
  and RVO2's documentation warns that "if the number is too low, the simulation will not
  be safe". Forty has no source.
- **It is a hard case.** Two blocks four abreast in a 4 m corridor leave gaps one body
  wide for the other block to come through.
- **A jam does not register as a deadlock.** The deadlock test asks for every agent to be
  nearly still for 3 s, which a crowd never is. A jam shows as late arrivals: seven agents
  take more than 60 s with ten neighbours, and two with forty.

#### Speed

`python -m negsim.avoidance.benchmark --agents 100 1000 10000` times the first 100 steps
of the same flow at the same starting density, under plain ORCA, with nothing logged. One
process, one thread, pure Python 3.13.3 with no compiled extension, on a laptop: AMD
Ryzen 5 7535HS (6 cores, 12 threads), 16 GB of memory, Windows 11, on mains power.

| Agents | Milliseconds per step: mean | Median | 90th percentile | Microseconds per agent per step | Simulated seconds per second of computing |
|---|---|---|---|---|---|
| 100 | 12.5 | 12.2 | 14.8 | 125 | 8.0 |
| 1,000 | 148.3 | 144.4 | 175.8 | 148 | 0.67 |
| 10,000 | 1,602 | 1,512 | 1,961 | 160 | 0.062 |

That is `runs/si1_benchmark/benchmark.json`, measured on 2026-10-13. A second measurement
the next day, in `benchmark_repeat.json`, gave means of 15.6, 143.3 and 1,364 ms: the same
to within about 25%, which is how far to trust any one of these numbers.

- **The cost per agent hardly grows with the crowd**: 125 to 160 microseconds across a
  hundredfold increase. That is what the neighbour grid is for.
- **Ten thousand agents run, about fifteen times slower than the clock**: some 1.5 s of
  computing for each 0.1 s step. The project's target is 10,000 agents. This layer, in
  pure Python and not optimised, does not reach that at a usable speed. The number is a
  measurement, not a pass mark.
- The 100 steps timed include the two crowds meeting, about two seconds in, so they are
  not the quiet part of a run. `status_when_stopped: timeout` in the file means only that
  the benchmark stopped the run after its 100 steps.

### What is still a placeholder

Four values have no source and are tagged `[placeholder]` where they are set and in
`docs/parameters.md`, section 3:

| Where | Value | |
|---|---|---|
| `corridor_to_bottleneck`, `bottleneck_width` | 0.8 m | Narrow enough that two discs cannot pass. People have been observed to pass at this width by turning their bodies, which a disc cannot do. |
| `corridor_to_bottleneck`, `bottleneck_length` | 4.0 m | The hallway length of issue #24, itself a placeholder. |
| `bidirectional_flow`, `spawn_spacing` | 1.0 m | Sets the starting density, about one person per square metre. |
| `si1_bidirectional_flow.yaml`, `max_neighbours` of the second run | 40 | There to show the effect of the limit. |

The metric thresholds (what counts as a near miss or a yield) are definitions, not
measurements. And of the values that *are* cited, none is from Singapore: the walking
speed and the corridor come from forty people in France, the body radius from four young
men in Japan (`docs/parameters.md`, section 7).

## The rule layer (issue #28)

The avoidance layer took its directives from a config. Here they come from **stored
rules**. A rule says: when two agents meet in a certain way, give them roles, and tell each
role what to do. It is data, never code; it lives in a rule database that records where it
came from; and the `RuleDatabaseProvider` follows it behind the same interface as before.
ORCA and the arbiter are unchanged, and the run loop changed only where
`docs/architecture.md`, section 7.3, lists. This is the second of six sub-issues. It calls
no model, and **every run is free**.

1. **A rule** (`docs/rule-format.md`) has a condition built from a fixed list of fields,
   seven comparison operators with units, and `all`/`any` groups; one directive for both
   agents (`symmetric`), or two roles assigned by ordering the two agents on a field, with a
   tie policy; a directive per role; a priority; a status; and its provenance. A rule may
   read only what both agents of a pair compute identically: pair-level quantities, and
   attributes of either agent that the other can see. A rule that reads anything else, such
   as an agent's task, is refused when it is loaded: it could only be followed after the
   two had talked, which is SI-3's subject.
2. **The rule database** (`rule_db/`) holds one YAML file per version of each rule. A
   SHA-256 manifest freezes every file, so a version is never edited; a change is a new
   version. Rule sets name the versions an experiment switches on. The five seed rules are
   all `test_seed`: they exercise the machinery and make no claim about people.
3. **Matching** (`docs/rule-matching.md`). Rules are evaluated once per pair, on one
   snapshot both agents share, and each agent gets its role's directive; that equals each
   agent deciding alone because perception here is perfect and simultaneous, an assumption
   stated there. The highest priority wins; a match holds, with hysteresis, until the
   encounter has passed; with no match the pair follows plain ORCA.
4. **Plain ORCA is two frozen baselines** (`docs/baseline.md`): `orca_perturbed_v1`, the
   primary, adds the RVO2 library's own perturbation of 1e-4 m/s to every preferred velocity
   to break exact symmetry; `orca_unperturbed_v1` does not.
5. **`speed_scale`, and anything else a rule sets, ends when the encounter has passed**: the
   two are separating and clear of each other (`docs/derivations.md`, section 15).
6. **Logs.** Log schema version 3 adds `pair_interactions.jsonl` (per pair: every
   evaluation with its snapshot, every match with its rule and version, when and why it
   ended, and the outcome, `avoided`, `resolved` or `failed`), the rules each run followed,
   and counts of issue #26's two artefacts.

### Run it

```
python ruledb.py list                                                  # the rules, their status, the rule sets
python ruledb.py validate                                              # load and check everything; writes nothing
python ruledb.py history keep_left_head_on                             # every version of a rule
python run_experiment.py configs/rule_following/si2_head_on.yaml       # one of the behaviour checks
python -m negsim.rules.report                                          # their tables, from the committed logs
python -m negsim.rules.benchmark                                       # what following rules costs per step
```

| Config in `configs/rule_following/` | Scenario | Runs | What it varies |
|---|---|---|---|
| `si2_head_on.yaml` | `wide_corridor_head_on` | 320 | exactly head-on or 10 cm off; no personas, or a woman of 25 and a man of 70; baseline; plain or rules |
| `si2_keep_left_vs_right.yaml` | `wide_corridor_head_on` | 80 | baseline; `keep_left_head_on` or `keep_right_head_on` |
| `si2_open_crossing.yaml` | `open_crossing` | 160 | arriving together or half a metre apart; baseline; plain or rules |
| `si2_overtaking.yaml` | `overtaking` | 160 | exactly behind or 5 cm off; baseline; plain or rules |
| `si2_bottleneck.yaml` | `corridor_to_bottleneck` | 320 | opposing or merging; equal speeds or agent 0 slower; baseline; plain or rules |
| `si2_bidirectional_flow.yaml` | `bidirectional_flow` | 80 | baseline; plain or rules |
| `si2_head_on_r5.yaml`, `si2_overtaking_r5.yaml` | as above | 320, 160 | the same, with a sensing radius of 5 m |
| `si2_bidirectional_flow_ablation.yaml` | `bidirectional_flow` | 40 | a follow-up the issue did not ask for: the primary baseline with `default` minus one of its two rules that act in the flow |

Every condition has 20 seeds.

### Results of the rule layer (2026-10-15)

From the 1,600 committed runs of the behaviour checks in `runs/si2_*`, all written from a
clean tree at commit `a4e1ead`, and the 40 of a follow-up (at `3a9bdff`).
`docs/behaviour-checks.md` has every table and the reasoning; these are the main points.
**They are statements about this algorithm and these test rules, not evidence about
people.** A spread is the mean ± standard deviation over 20 seeds.

- **A shared side removes the symmetric deadlock, and against the primary baseline it makes
  the pass predictable.** Exactly head-on, unperturbed ORCA deadlocks in 20 of 20 runs; with
  `keep_left_head_on` both arrive in 12.2 s, as if alone. The perturbed baseline does not
  deadlock: plain ORCA passes on a side the noise picks (left 9, right 11) in 12.32 ± 0.04 s,
  and the rule makes it left in 20 of 20, in 12.20 s.
- **`keep_left_head_on` and `keep_right_head_on` differ only in the side.** Every other number
  is the same to the precision of the logs.
- **A share without a side is underspecified.** `younger_yields_head_on` gives the woman of 25
  the whole share and no side. Under the perturbed baseline she steps aside half a metre;
  under the unperturbed one, exactly head-on, she walks backwards in 20 of 20 runs and arrives
  at 24.9 s, issue #26's artefact, now produced by a rule.
- **`overtaker_keeps_clear` stops the slower walker being hurried along.** It arrives at its
  own pace, 32.6 s, in all 80 rule runs, against 120 "hurried" episodes in the 80 plain runs;
  the overtaker does all the stepping aside (up to 0.50 m).
- **At the single-file segment the rule never changes who goes first**, because it says what
  the arbiter already does. With equal speeds it "fires" one step after the arbiter has
  decided, on times that the arbiter's slowdown has changed, and so ratifies that decision.
- **The default rule set has no crossing rule**, so the crossing's rule runs follow plain
  ORCA, deadlock included; their differences from the plain runs show the size of the seed
  noise.
- **A sensing radius of 5 m changes no outcome count.** It changes when ORCA starts steering
  and how hard (exposure 3.8 s instead of 6.4 s, head-on with `keep_left_head_on`).
- **Fifty each way, the rules let the crowd clear far sooner, with fewer but much deeper
  overlaps.** Under the primary baseline the last agent arrives at 46.9 s instead of 83.4 s,
  and the mean time to goal is 35.9 ± 0.7 s against 38.7 ± 6.0 s (33.5 s alone); overlap
  episodes per run fall from 234 to 107. But the deepest overlap of a run goes from 32 mm to
  201 mm, up to 456 mm. **A follow-up the issue did not ask for** (leaving one rule out at a
  time) puts the depth on `overtaker_keeps_clear`, which gives the agent in front a share of
  0: with `keep_left_head_on` alone the crowd clears as fast and the deepest overlap is 54 mm;
  with `overtaker_keeps_clear` alone the flow gridlocks in 15 of 20 runs (Q10).
- **Following the rules makes a step 2.3 times as long at 100 agents and 3.0 times at
  1,000** (120.6 against 52.1 ms; 1,531 against 514 ms; `runs/si2_benchmark/benchmark.json`).
  Almost all of the extra goes into re-measuring the corridor width between pairs that tie
  and are therefore evaluated again on every step (Q11).
- **Two measures need care.** Almost no pair is ever `avoided` (two agents on a collision
  course always register exposure), so the categories mainly separate deadlocks from the
  rest. And under the perturbed baseline, exposure counts changes of velocity the size of the
  perturbation for an agent with a share of 0. Both are open questions in `WORK_LOG-28.md`.

### What is still a placeholder (issue #28)

| Where | Value | |
|---|---|---|
| Baselines | 40 neighbours; sensing radius 12.5 m, and 5 m in the sensitivity check | Set by the user in the issue; supervisor sign-off pending (`docs/baseline.md`) |
| Encounter classes (DD43) | heading differences of 60° and 120° | 0–180° cut in three equal parts |
| Matching hysteresis (DD54) | 3 steps | A definition |
| `keep_left_head_on`, `keep_right_head_on` | a corridor of at least 1.0 m | Two effective shoulder widths (Yamamoto et al. 2019), rounded: derived, not a measured passing width |
| `overtaker_keeps_clear` | speeds within 0.05 m/s tie | A definition |
| `single_file_first_arrival` | times within 0.5 s tie | A definition |
| `younger_yields_head_on` | time to collision 6 s; age difference 20 years | The issue's example values |
| The artefact counts (`docs/metrics.md`, section 10) | 0.1 m/s backwards; 1.05 times the wanted speed; 1 s | Definitions |
| The outcome categories (DD57) | no exposure but a yield counts as `resolved` | A decision: the issue's definitions leave that case out |

## Changing things

| To | Edit |
|---|---|
| change a scenario's sizes, or give the two agents different speeds or sizes | `configs/scenarios/*.yaml` (`agents:` takes per-agent overrides), or `scenario_overrides:` in an experiment |
| give agents an avoidance directive | `directives:` in a config under `configs/avoidance/`: `provider: static`, then `default`, `agents` (by index) or `pairs` (observer and neighbour) |
| give avoidance agents an age and a gender | `population:` in the same config. It changes what a neighbour perceives and nothing physical. To make an agent slower as well, set its speed under `scenario_overrides`, in the same file. |
| change how single-file segments are handled | `arbitration:` in the same config (`enabled`, `policy`, `tie_break`) |
| change a threshold of the conflict metrics | `metrics:` in an avoidance scenario. Every `outcome.json` records the values used. |
| add a source of directives (a negotiation, say) | a subclass of `DirectiveProvider` with one method, `directive(record)` (`negsim/avoidance/directives.py`); optional hooks let it follow pairs from step to step, as the rule provider does (DD56) |
| choose which stored rules an experiment follows | `directives: {provider: rules, ruleset: default}` in an avoidance config, then `disable: [...]` and `enable: {rule_id: version}` (`docs/rule-format.md`, section 10) |
| write a rule, or a new version of one | a new file `rule_db/rules/<rule_id>.v<n>.yaml` in the format of `docs/rule-format.md`, its SHA-256 added to `rule_db/MANIFEST.json`, then `python ruledb.py validate`. **Never edit a version that exists**: a change is the next version (`rule_db/README.md`) |
| change what "plain ORCA" means | never edit a baseline: write `configs/baselines/<name>_v2.yaml` and add it to that folder's `MANIFEST.json` (`docs/baseline.md`, section 4) |
| add a dynamics model | a subclass of `DynamicsModel` (`negsim/core/dynamics.py`). The avoidance scenarios accept only `holonomic` for now. |
| add or change a persona | `configs/personas/personas.yaml`. No personal names: the loader rejects them. |
| vary one persona attribute for one run | `{persona: f25, age: 70}` in an experiment's design |
| choose what an agent is told about the situation | `negotiation.info_fields` (`all`, `none`, or a list of field names) |
| choose what an agent can see of the other | `negotiation.visibility` (age, gender, task, backstory, speed, size) |
| let the agents move while they talk | `negotiation.timing.mode: concurrent` |
| change any wording an agent sees | **a new template version.** Copy `negsim/negotiation/templates/<name>_v1.yaml` to `_v2`, edit it, run `python -m negsim.negotiation.freeze <name>_v2 "<why>"`, and record the reason in the work log. A frozen template that has been edited will not load. |
| add a persona attribute | one entry in `negsim/personas/schema.py`, one line in a new template version |
| add a controller | a class with `compute(agent, speed_bound, world)`, registered with `@register_controller("name")` |

## Documents

- `docs/architecture.md`: the modules, one run step by step, and every design decision,
  marked as a decision.
- `docs/gamechat-notes.md`: what the paper and its repository say, where they disagree,
  and where this platform departs from both.
- `docs/derivations.md`: the follower's speed bound and the conflict zone; and, for the
  avoidance layer, the reciprocity condition on the shares, the side preference, walls in
  discrete time, how long a symmetric meeting takes to stall, and when an encounter has
  passed (issue #28).
- `docs/orca.md`: ORCA as implemented, section by section of the paper; what was checked
  against RVO2; every departure from either.
- `docs/perception.md`: the perception record, version 2, field by field, with the
  pair-level fields that rules read (issue #28).
- `docs/rule-format.md`: the rule format, schema version 1, in full: what a rule may read,
  and every check made when one is loaded. SI-3 will have a model write rules in it.
- `docs/rule-matching.md`: which rule a pair follows, step by step, and why one shared
  snapshot stands for each agent deciding alone.
- `docs/baseline.md`: the two frozen baselines that "plain ORCA" means.
- `docs/behaviour-checks.md`: the behaviour checks of issue #28, every number from the
  committed logs, and what they show.
- `docs/parameters.md`: every physical parameter of the avoidance scenarios with its
  source and locator, or the word placeholder.
- `docs/metrics.md`: the conflict metrics, defined operationally, with their thresholds;
  since issue #28 also the outcome of a pair interaction and the two artefact counts.
- `docs/llm-backend.md`: DeepSeek's API as documented on 2026-10-13, the client, the
  budget guard.
- `docs/log-schema.md`: every log file and field.
- `THIRD_PARTY_NOTICES.md`: what is quoted from GameChat and what is adapted from RVO2,
  with their licences.
- `negsim/viz/viewer.py` and `viewer.html`: the animated viewer (section "Watch a run").
