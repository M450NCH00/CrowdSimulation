# RF-29: round 1 (head-on), a sidestep in metres (`resolve_v8`), and the executor rule it exposed

Issue #101, track #55. Paid run of 2026-10-25 (Sunday, off-peak), approved by the user for this
issue only with a cap of USD 0.08 (`CLAUDE.md`, pending item 1). Every number below comes from a
file named with it; the process is in `WORK_LOG-101.md`.

## In short

- **The run as made: the sidestep option made things worse.** 4 of 64 resolved in `plan_only`
  against RF-10's 22 (McNemar p = 0.0003). The agents used the option (117 of 127 first plans) and
  the executor moved them exactly as far as asked (median 0.4 m).
- **The cause was the executor, not the agents.** Under `protocol.execution: as_prompted` (issue
  #64), a step with no `turn` steers back to the path the agent started on. So a sidestep followed
  by "walk on until the other passes" was undone before the meeting: 53 of 108 colliding agents
  kept less than half their sidestep by the time the two were level. The prompt says they keep
  the new line. **This rule was in force in RF-10, RF-27 and RF-28 too**, where it did less harm
  only because their turns ran longer.
- **With the rule fixed** (`keep_line`, the user's decision, off for every earlier config), the
  four runs' independent sessions were carried out again from their recorded plans, with no LLM
  call. That is exact, because every independent decision came at the trigger, before anyone
  moved (checked: 0 of 192 decision points after it, in each run).

  | The same 64 sessions under `keep_line` | Resolved in `plan_only` | Paired against the first row |
  | --- | --- | --- |
  | RF-10: `deepseek-flash`, `resolve_v6` | **35 / 64: 0.55** (0.43 to 0.66) | (22 under `as_prompted`: p = 0.0002) |
  | RF-27: flash, `resolve_v7` (the line offset) | 27 / 64: 0.42 | p = 0.22 |
  | RF-28: `deepseek-v4-pro`, `resolve_v6` | 21 / 64: 0.33 | **p = 0.024, worse** |
  | RF-29: flash, `resolve_v8` (the sidestep) | 27 / 64: 0.42 | p = 0.22 |

- **What fails once the line is kept is coordination, not size.** Under `keep_line` the sidestep
  run's collisions are mostly the "pavement dance": 25 of 32 have the two stepping towards the
  same wall, and only 4 made room too narrowly. RF-10's plans: 16 of 27. The agents size their
  move well enough when it is carried out as they said; they do not agree on a side.
- **For Step 1:** in the independent condition, RF-10's own plans, carried out as the prompt
  describes, resolve 0.55 of head-on meetings, above the 0.50 gate though the interval includes
  it. The gate was fixed over all three conditions. Non-verbal and talk cannot be carried out
  again without new calls (their later decisions saw the old execution), so the gate is not
  re-decided here.

## 1. The run (`cost.json`, `../../spend_ledger.jsonl`)

| | |
| --- | --- |
| Sessions | 96 of 96, independent: RF-10's same sessions (ids, cells, people, seeds); every first user message identical to RF-10's; the system message differs only by the sidestep line and the `until` exception |
| Template | `resolve_v8` = `resolve_v6` + `"sidestep": {"to", "metres"}` (the user's five decisions of 2026-10-25); turning by degrees unchanged |
| Cost | **USD 0.048995** (384 calls, off-peak, no error) of the USD 0.08 cap; balance USD 0.91 → **0.86** |
| Unreadable | 2 of 192 decision points (RF-10: 5) |
| Model | `deepseek-flash`, fingerprint `e72d3c7f663d3e1383b00b3884cb4501`, as RF-10's |

## 2. How the agents used the sidestep (design sessions, first readable plans)

- 117 of 127 plans sidestep, 5 more sidestep and also turn in another step, 2 only turn, 3 neither.
- Metres asked: median 0.4 (IQR 0.4 to 0.5); 0.4 m 49 times, 0.5 m 32, 0.3 m 14, 0.6 m 11.
- 107 sidestep steps ended at their distance; the rest at their `until` (7: 6 at a distance, 1
  when the other passed), at the run's end (9), or never started (2). Reached aside: median 0.4 m.
- Pairs' first-plan sides: 34 the same own side (they make room), 26 opposite (towards the same
  wall), 4 with one without a side.

## 3. The run as made, under `as_prompted` (`analysis/compare_rf10_round1_head_on*.md`)

4 of 64 resolved (0.06, 0.02 to 0.15) against RF-10's 22; paired 1 / 21 / 3 / 39, p = 0.0003;
readable only p = 0.0005. Collisions 54: compatible but narrow 20, towards the same wall 17, one
or both not aside 17. Colliding pairs were a median 0.18 m apart sideways when level, though each
had sidestepped about 0.4 m: the following step had steered them back.

## 4. The executor rule, and `keep_line`

- `execute.py` under `as_prompted`: a turn walks at its angle off the step's start direction, and
  between steps and after the last the agent keeps its line; **but a step with no turn steers
  towards the path's lookahead point**, as RF-4 had it. The prompt says of a sidestep "then walk
  on parallel to it", and of the plan "after the last step ends, you walk on towards where you
  are going".
- Traced: agent 1 of `I_head_on_de176842_0f57f8a5_r1` sidestepped 0.37 m to its right, then "walk
  at 1.3 m/s until 0.9 m away" took it back to 0.06 m by the meeting.
- `protocol.execution: keep_line` (new, the user's decision): `as_prompted`, and a step with no
  turn walks parallel to the path from where the agent is. Tests: a sidestep or a turn followed
  by a plain step keeps its line under `keep_line` and is pulled back under `as_prompted`; a plan
  with no move aside runs the same under both.
- `python -m negsim.resolution.reexecute`: carries an experiment's sessions out again under
  another execution, refusing any session with a decision after the trigger. Under the source's
  own execution it reproduced RF-29 exactly (96 sessions, 66 physical columns, no difference).
  Re-executions: `runs/rf10_round1_head_on_keep_line/`, `rf27_round1_head_on_v7_keep_line/`,
  `rf28_round1_head_on_v4pro_cap600_keep_line/`, `rf29_round1_head_on_sidestep_keep_line/`, each
  with its `NOTE.md`, gate, lateral and comparison files.

## 5. Under `keep_line` (`runs/*_keep_line/analysis/`)

| Run | Resolved | aligned / 20 cm apart | Collisions: same own side / same wall / not aside |
| --- | --- | --- | --- |
| RF-10 (flash, v6) | 35 / 64: 0.55 (0.43 to 0.66) | 19 / 16 of 32 | 3 / 16 / 8 |
| RF-27 (flash, v7) | 27 / 64: 0.42 (0.31 to 0.54) | 15 / 12 | 9 / 17 / 6 |
| RF-28 (v4-pro, v6) | 21 / 64: 0.33 (0.23 to 0.45) | 13 / 8 | 0 / 1 / 18 |
| RF-29 (flash, v8) | 27 / 64: 0.42 (0.31 to 0.54) | 18 / 9 | 4 / 25 / 3 |

Readable only (sessions with every reply readable in both runs), against RF-10 under
`keep_line`: RF-27 24 / 59 against 34 / 59 (p = 0.087); RF-28 17 / 48 against 28 / 48
(p = 0.052); RF-29 27 / 58 against 33 / 58 (p = 0.36).

- **RF-10's plans gain 13 sessions and lose none** when the line is kept (p = 0.0002).
- **`resolve_v7` and the sidestep do not beat RF-10's plain `resolve_v6`.** With the sidestep,
  the 20 cm layout does worst (9 of 32): each agent sees the other a little to one side, and they
  split between stepping away from it and keeping right.
- **v4-pro is worse**, as in RF-28 its collisions are "one holds the line" (18 of 19 with one or
  both not aside): a lone sidestep has to give the whole clearance.

## 6. What it means

- **RF-10, RF-27 and RF-28's conclusion that the sidesteps were too small was largely the
  executor.** Their reports carry an addendum pointing here.
- **Once plans are carried out as described, the main failure is the pavement dance**, a
  coordination problem: both agents step aside, but towards the same wall. That is what a
  convention ("keep right"), a signal or a word would solve, and so what the non-verbal and talk
  conditions are for. They were not better in RF-10, but RF-10 ran under the rule that undid
  sidesteps, so that comparison should be redone under `keep_line`. That needs new paid runs.
- **Suggestions for the user (none done here):** run later rounds with `protocol.execution:
  keep_line`; redo the three conditions of head-on under `keep_line` (a lean round, about USD
  0.05 to 0.15); and keep `resolve_v6`, which did at least as well as `resolve_v7` and
  `resolve_v8`. Whether head-on passes the gate is for that run and the supervisor.

## 7. Caveats

- `keep_line` is one reading of the prompt ("walk on towards where you are going" as keeping the
  line, not returning to it). It is the user's decision, not a sourced fact about walking.
- The re-executions cover the independent condition only (exact because every decision came at
  the trigger).
- The 30° default angle and the 3 m limit of `resolve_v8` are placeholders.
- One model at temperature 1.0 (and v4-pro once); 64 paired design sessions show large effects only.
