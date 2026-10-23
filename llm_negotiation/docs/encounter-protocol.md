# The Step 1 encounter protocol and the resolution experiment (issue #58, RF-3)

How LLM agents are put into a conflict case and asked what they do: when they are first asked,
when they are asked again, what they may do in each condition, when the encounter ends, how
they are debriefed, what is stored, and what a session could cost. It builds `resolution.md`'s
D3 to D6, D8 and D13 on RF-2's templates and parser (#57), RF-17's perception (#73) and RF-4's
plan executor (#59). Everything here runs on the mock client; **no paid call has been made**,
and none may be until `CLAUDE.md` records the supervisor's approval of paid runs and the cap.

Code: `negsim/resolution/protocol.py` (one session), `design.py` (the session list),
`experiment.py` (the `resolution` layer), `transcript.py`, `mock.py`
(`resolution_rehearsal_v1`), and the scenario interface (`scenario.py`, `scenarios/`).
Tests: `tests/test_encounter_protocol.py`.

Values are tagged as in `parameters.md`: section 8.6 lists the protocol's. Where something
below is **an assumption** (mine, not sourced and not the issue's words), it says so; the
decisions to review are also in `WORK_LOG-58.md`.

## 1. A session

A session is one case, one design cell (two people), one condition and one repeat. It runs the
case's **own source run**, rebuilt from its config on its seed (`rulegen.replay.source_plan`, as
`cases.md`, section 7, re-steps a case), as plain ORCA until the trigger fires. From then on the
encounter's members follow their plans in `plan_only` (RF-4): ORCA does not steer them apart,
and still handles walls and everyone else. A session ends `completed` (an encounter was recorded
to its end), `no_encounter` (the trigger never fired, so nobody was asked) or `aborted` (the
budget guard refused, or the model could not be used).

## 2. The trigger (D4) and who is in the encounter (D11, D16)

For each of the case's two people, at the start of every step, the protocol checks D4 toward
the other:

- it **sees** the other (RF-17: within 75° of where it faces and 10 m, with nobody nearer and no
  wall on the line between their centres) or **hears** them speak to it;
- the distance between them is **shrinking** (relative position · relative velocity < 0);
- the scenario **predicts a conflict** between them (`Scenario.conflict_predicted`).

Seeing someone is not enough. The frozen head-on cases start 12.4 m apart, out of view, so the
run is re-stepped until the other is within 10 m.

**The passing scenarios' prediction** (`scenarios/passing.py`; an assumption): a conflict is
predicted when neither has arrived and either (a) both paths run through a single-file segment
too narrow for them to pass in, and the arbiter's zone there is still live; or (b) they have not
passed each other, and at their present velocities **or at their desired ones** (along the path
where each is, at its preferred speed) their closest approach still to come is nearer than the
two radii and the safety margin, the safety distance the time-to-meet line uses. The desired
velocities keep two people who have both stopped face to face in conflict, which the present
ones alone would not.

**Members.** The scenario says who is in the encounter the two started
(`Scenario.encounter_members`): the two, or more. `passing_crowd` (bidirectional flow) adds
everyone still walking within 10 m of either of the two and predicted to be in conflict with
either, nearest first (an assumption; it exists to rehearse more than two prompted people
before rounds 4 and 6 need it). **The cap** (`protocol.max_prompted`, D12: a cost limit, not a
human number) keeps the first N members; the rest stay plain ORCA, and the session records whom
it left out. The **conflict pairs** are the two who started it and every other pair of members
predicted to be in conflict at the start; the outcome counts only them (section 7).

## 3. Decision points (D5)

**The first prompt of each member** needs D4 to hold for it, toward any other member (an
assumption: the issue says every agent in the encounter is prompted at the first decision point,
D4 says one is prompted only if it perceives the other; both hold if a member who perceives
nobody yet, such as the person ahead in an overtaking case, is first asked when it does). At the
encounter's first decision point every member for whom D4 holds is asked, all on the same world
state. Its partner (the person its events and its `at_distance_m` are read against) is the
nearest member for whom D4 holds.

**Later prompts** need (a) and (b):

- (a) **the conflict still matters**: a conflict is still predicted with another member, or the
  agent's plan has ended;
- (b) **something new happened**, since the agent last looked:
  - `other_<change>:<id>`: a member it saw then and sees now changed noticeably
    (`perceive.changes_since`: slowed down, sped up, stopped, started walking, started backing
    up, moved over, turned; RF-17's thresholds, 7% of speed and 2°);
  - `signalled:<id>`: someone made a signal it could see;
  - `heard:<id>`: it heard someone speak;
  - `came_into_view:<id>`: someone it did not see then is in view now (anyone, as D5 says);
  - `plan_failing`: the closest approach to its partner at the present velocities is below the
    safety distance again, after being clear at some step since it decided;
  - `plan_ended`: its latest plan had steps and has all been carried out. **A plan with no
    steps (`[]`, "carry on") never ends in this sense** (an assumption: otherwise an agent who
    said "carry on" would be asked again a second later).

**Guards:** only the agent who noticed is asked; at least `min_gap_s` (1 s) between two prompts
of one agent; at most `max_decision_points` (3) per agent, 1 in the independent condition;
every decision point records its reasons (`trigger_reasons`).

**A prompt** is a fresh request of two messages: the condition's fixed text, then the view
(`perceive.view_in`) and the wrapper (`prompt.render`, template `resolve_v2`). **History is
compact**: an earlier decision point reappears only as its lines in WHAT YOU HAVE DONE SO FAR,
never as the transcript. The reply is read by RF-2's parser, retried once if unreadable
(`request_with_retry`).

**What a reply does.** A readable reply's steps are given to the plan driver at once
(`PlanDriver.give`), so the next simulation step carries them out, replacing what was left of
the agent's plan. Its signal is made during that next step, after everyone looked at this
decision point, and is seen by whoever sees the agent then. Its message (talk only) takes time
to say, `len(words) / speech_words_per_second` (2.5 words a second **[placeholder]**), and is
heard, when it has been said, by everyone within the hearing range (3.2 m) from any direction.
**An unreadable reply** (after its retry) uses up the decision point: the agent carries on with
its plan, or with none (`[]`) if it had none, so that ORCA never steps in, and its look is
dropped from its perception, so that its history shows no decision it did not make (an
assumption).

## 4. The conditions (D3)

| Condition | Decision points per agent | What the agent can do |
| --- | --- | --- |
| `independent` | 1 | move; a message or signal in the reply is ignored and flagged |
| `non_verbal` | up to 3 | move and signal |
| `talk` | up to 3 | move, signal and speak: one message per decision point |

Speaking order is not a factor: everyone due at a step is asked on the same state.

## 5. The end, the hand-over to ORCA, and the debrief (D6, D8)

The encounter ends, checked at the start of every step, on the first of:

| End | When |
| --- | --- |
| `passed` | every conflict pair has passed each other (separating, further apart than the two radii and the margin, **and** no conflict predicted between them, since two people standing still can read as separating by a rounding error) or one of them has arrived |
| `no_conflict` | no conflict between any two members has been predicted for `no_conflict_end_s` (1 s **[placeholder]**) |
| `deadlock` | the run's deadlock monitor stopped it |
| `collision` | the run stopped on a collision (a scenario with `on_collision: stop`) |
| `time_limit` | the run's time limit |
| `orca_took_over` | every prompted member has used its decision points (or arrived) and has no plan left to carry out, and a conflict is still predicted: **not resolved by the LLM** (D6). The encounter is released to ORCA (`PlanDriver.release`, reason `not_resolved_by_llm`), and what ORCA does after that is in the `plan_only` replay |

`not_resolved_by_llm` is true for `orca_took_over`, `deadlock`, `collision`, and `time_limit`
with a conflict still predicted. This is when "the last decision point" (D6) has played out (an
assumption).

**The debrief** (D8): after the end, one `resolve_debrief_v1` call per member that made at least
one readable decision: its last readable prompt, its reply word for word, and the debrief
question with every decision it made. Every source is stored `unchecked`.

## 6. The cost preview

`--plan` prints, and every run writes to `preview.json` before any call, the most the sessions
could cost, per condition and in total, in the way issue #30 did (`rule-generation.md`, section
9). Every text's tokens are estimated high, as the budget guard does (`estimate_prompt_tokens`:
0.3 token a character, times 1.5, plus 8 a message). For one session, with:

- c, the reply cap (`llm.max_tokens`, 400 **[placeholder]**);
- k, the most people prompted: the scenario's `MAX_MEMBERS` (2 for `passing`; the case's size
  for `passing_crowd`), capped by `max_prompted`;
- d, the most decision points per agent: 1 (independent) or `max_decision_points` (3);
- P + D, the fixed text and the longest description: `worst_view` renders a view with every line
  a description can have, for everyone the case could put in view (n − 1 people, or the
  view's `max_people`), each in full detail with every change, a signal and both
  demographics, plus h = (k − 1)·d voices heard in the talk condition (0 otherwise) and d − 1
  earlier decisions, each free text (a message, an intent) counted at c;
- R, the retry instruction; B, the debrief text with no decision in it; R_B, its retry;

a decision call's prompt is at most **S = P + D + c + R** (room for a failed reply and the retry
instruction), and a debrief's at most **S_B = (P + D) + c + B + d·c + c + R_B** (the last prompt,
the reply to it, the question with up to d decisions of at most c each, and room for a retry).
Per session:

  **input ≤ k·d·S + k·S_B** and **output ≤ (k·d + k)·c**,

each multiplied by the most sends a call can make, **2 × (1 + transport_retries)** (6 by
default), at the peak cache-miss input price and the peak output price. As in #30, the bound
takes a message or intent to be no longer when it reappears than when it was written (c).
`summary.json` reports the largest share of a session's preview its tokens used.

**For the mock rehearsal** (`--plan`): a two-person session is bounded at USD 0.029 to 0.030
(independent), 0.074 to 0.076 (non-verbal) and 0.094 to 0.096 (talk). The crowd case is bounded
far higher (USD 0.38 to 0.91 a session), because with `max_people` off every one of its 99 others
could be in view in full detail. That is a true bound but a loose one; a paid crowd run would set
`llm_view.max_people` (a new `llm_view_v2.yaml`) to tighten it.

## 7. One row per session

`outcomes.jsonl` and `outcomes.csv` (the same rows; `others` only in the JSON) hold, per session:

- **design:** session id, outcome, case and version, case geometry (its variant), encounter
  type, scenario plug-in, condition, mapping, repeat, `exact_repeat_set`, model, temperature,
  and the cell's factors;
- **per person** (`p1_`, `p2_`: the design's two people; `others` for further members): agent,
  age, gender, urgency, errand, and the person's level of each core factor the design varies
  (issue #60: `p1_mobility_aid`, `p2_load`, ...); how the person sees the other, as 0 or 1, and at
  how many of its decision points it was told so (issue #61: `p1_finds_other_attractive`,
  `p1_knows_other`, `p1_pairwise_lines_shown`; `pairwise-factors.md`, section 5); the number of decision points and their reasons; unreadable
  replies; the first and the final plan coded mechanically (`side`: the sign of the turns, or
  `none` or `both`; `slowed`: a speed below the speed at the decision; `stopped`; `backed_up`;
  `start_distance_m`); signals used; messages; the debrief's `kind` and `source`;
- **the encounter:** size, how many were prompted, how many the cap left out, start, end and
  why, `not_resolved_by_llm`, when ORCA took over;
- **physical outcomes**, RF-4's columns and the scenario's own, once per mode with the mode as
  suffix: `_plan_only`, `_plan_orca`, and `_plain_orca` (the case's run with no plan, same seed).
  `resolved_plan_only` is the physical result in the Step 1 measure; **`resolved_by_llm`** is
  `resolved_plan_only` and not `not_resolved_by_llm`, so that a pass ORCA made after taking over
  is not counted for the LLM;
- tokens and USD.

An encounter of more than two people has, in each mode, the first two members' columns plus
`encounter_size`, `conflict_pairs` and `conflict_pairs_resolved`; it is resolved only if every
conflict pair is (`outcomes.py`).

## 8. The experiment layer

```
python run_experiment.py configs/resolution/resolve_mock_rehearsal.yaml --plan
python run_experiment.py configs/resolution/resolve_mock_rehearsal.yaml            # mock: runs_mock/
python run_experiment.py configs/resolution/<config>.yaml --client deepseek        # preview only
python run_experiment.py configs/resolution/<config>.yaml --client deepseek --confirm
```

| Key | What it sets |
| --- | --- |
| `experiment_name` | the folder, `runs/<name>/` or `runs_mock/<name>/`, and the budget scope |
| `cases` | `store`, `set` and/or `ids` (each `id` or `id@version`) |
| `scenarios` | optional: case id → plug-in; otherwise the plug-in whose `CASE_TYPES` holds the case's type |
| `conditions` | any of `independent`, `non_verbal`, `talk` |
| `design` | `seed`, `factors` (`age_pair`, `gender_pair`, `task`, `demographics_visible`, `mapping`), `repeats`, `base_age`, `age_difference`, `tasks` |
| `protocol` | `max_decision_points` (3), `min_gap_s` (1), `no_conflict_end_s` (1), `max_prompted` (none), `speech_words_per_second` (2.5) |
| `templates` | `core` (`resolve_v2`), `debrief` (`resolve_debrief_v1`) |
| `llm_view` | the perception config (`configs/resolution/llm_view_v1.yaml`) |
| `llm` | `client`, `mock_policy` (`resolution_rehearsal_v1`), `model`, `temperature`, `max_tokens` (400), `thinking` (disabled), `transport_retries` |
| `budget` | `cap_usd` (on this experiment's own calls), `ledger` |

The design is issue #30's, less speaking order (`design.py`). The fictional group is not a
factor of this layer. A cell run more than once (`repeats` > 1) is in the exact-repeat set
(D14); RF-7 builds the screening designs. **Resume:** a session with a record is read back,
never run or written again (tested byte for byte); an aborted one is kept as
`<id>.aborted<n>.json` and runs again; the replays and the tables are rebuilt from the records.
`log-schema.md`, "Resolution experiments", lists every file and field.

## 9. What is not here

**The core and situational factors** (issue #60, RF-5) are not part of the protocol: a session
hands their lines (`factors.SessionFactors`) to every view it builds, and the experiment layer
sets the wider body of `load` for the run and the hearing range of `surroundings`
(`parameters.md`, section 8.7; `log-schema.md`, "Resolution experiments").

**The pairwise perception factors** (issue #61, RF-6) are not part of the protocol either: a
session hands each agent's own lines (`pairwise.PairwiseFactors.lines_for`) to that agent's views
only, and the perception of RF-17 attaches them to the people it sees (`pairwise-factors.md`).

Screening designs (RF-7), the analysis (RF-8), any paid call, and the scenarios of rounds 4 to 6
(RF-23 to RF-25). `passing_crowd` only rehearses more than two
prompted people; it is not a round's scenario.
