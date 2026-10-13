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
