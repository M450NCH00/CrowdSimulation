# llm_negotiation

A small simulator in which two agents that are about to get in each other's way talk it
over through an LLM, and the outcome of that conversation decides who goes first.

It reimplements GameChat (Mahadevan, Zhang and Chandra, arXiv:2503.12333) and adds three
things: personas with an age and a gender, situational information the agents can see
while they talk (speed, size, distance), and a complete log of every conversation. The
logs are the point: later work will look in them for reusable rules.

Built for issue #24. Nothing here uses the Phase 1 folders `pipeline/` and `dataset/`.

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
reach. They cost nothing.

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

`docs/log-schema.md` describes every field. To draw a run:
`python -m negsim.viz.trajectory_plot runs/<experiment_name>/<run_id>`.

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

## Changing things

| To | Edit |
|---|---|
| change a scenario's sizes, or give the two agents different speeds or sizes | `configs/scenarios/*.yaml` (`agents:` takes per-agent overrides), or `scenario_overrides:` in an experiment |
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
- `docs/derivations.md`: the follower's speed bound and the conflict zone.
- `docs/llm-backend.md`: DeepSeek's API as documented on 2026-10-13, the client, the
  budget guard.
- `docs/log-schema.md`: every log file and field.
- `THIRD_PARTY_NOTICES.md`: what is quoted from GameChat, and its licence.
