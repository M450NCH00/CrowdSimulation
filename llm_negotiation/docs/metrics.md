# Conflict metrics of the avoidance layer

Later sub-issues will ask of a rule: did it **avoid** a conflict, so that the conflict
never arose, or did it **resolve** one after it had arisen? (Category A and category C in
`literature/simulation-rules/category-summary.md`.) The metrics here are defined so that
the two can be told apart from a run's logs. Each definition is operational: it says what
is counted, on which time steps, against which threshold.

The arithmetic is in `negsim/metrics/avoidance.py` and `negsim/avoidance/simulation.py`.
Where each number is written is in `log-schema.md`. All times are multiples of the time
step, 0.1 s in every shipped scenario.

## 1. The defaults

Every threshold can be set per scenario, under `metrics:` in its config, and every
`outcome.json` repeats the values its run used. The defaults:

| Threshold | Default | Used by |
|---|---|---|
| `near_miss_distance_m` | 0.1 m | `near_miss` |
| `yield_speed_fraction` | 0.5 | `yield_event` |
| `yield_min_duration_s` | 1.0 s | `yield_event` |
| `exposure_eps_mps` | 1e-6 m/s | `conflict_exposure_time` |
| `pair_exposure_eps_mps` | 1e-3 m/s | `pair_exposure_time` (issue #30, section 11) |
| `collision_course_min_s` | 0 s | severity tier T1 (issue #30, section 11) |
| `deadlock.window_s` | 3.0 s | `deadlock` |
| `deadlock.speed_eps_mps` | 0.01 m/s | `deadlock` |

**None of these is a sourced value.** They are definitions chosen for this project
(`parameters.md`, section 4). The two deadlock values are those of issue #24. A count that
depends on a threshold should be reported with the threshold.

## 2. `interaction`

**A neighbour is within R.** An interaction of agent A with neighbour B begins on the
first step on which B is one of A's perceived neighbours, the nearest `max_neighbours`
agents no further away than A's sensing radius `R`. It ends on the first step on which B
is further than `R` from A, or either has arrived, or the run ends. With `max_neighbours`
at least the number of other agents this is exactly "B is within `R` of A".

An interaction is A's: B's interaction with A is a separate one. Each is one line of
`interactions.jsonl`, with the perception record built when it began and the directive A
held for its length.

*Reported:* per agent, `interactions` (how many it had) and `interaction_time_s` (time
with at least one perceived neighbour); in total, `interactions`.

## 3. `conflict_exposure_time`

**The time during which ORCA had to change what an agent wanted because of another
agent.** On each step an agent has a *preferred velocity*: along its desired path, at its
preferred speed times the `speed_scale` of its directives, and no faster than the
arbiter's bound if the arbiter holds it. ORCA builds one half-plane of allowed velocities
per perceived neighbour. The agent is **exposed** on that step if its preferred velocity
is outside at least one of those half-planes by more than `exposure_eps_mps`.
`conflict_exposure_time` is the number of exposed steps times the time step.

Zero exposure over an interaction means the conflict never arose: what the agent wanted
to do was allowed all along.

Three things about what is and is not counted:

- **Only agents count, not walls.** An agent slowed by a wall is not in a conflict with
  anyone. Whether ORCA changed the velocity for any reason at all is reported separately,
  as `orca_altered_time_s`.
- **The preferred velocity is the one the directives leave.** An agent told by a directive
  to walk at half speed, and which then never comes near anyone's half-plane, has no
  exposure. The rule avoided the conflict. What it cost shows in the time to goal and,
  if the agent was slow enough for long enough, as a yield event.
- **Exposure is one agent's.** In a pair with shares (1, 0), only the agent that takes the
  whole share is exposed; the other was never asked to change anything.

**It depends on the responsibility shares** (issue #30). The half-plane an agent is held to
is offset by its own share of the change needed (`derivations.md`, section 9), so the same
state of the world is counted differently under different shares: under shares (1, 0) the
agent with share 0 is not exposed at all on a step on which, under (0.5, 0.5), it would be.
It is kept, unchanged, for continuity with issues #26 and #28. A measure of the *pair* that
does not depend on the shares is section 11's pair exposure; the severity tiers use that one.

*Reported:* per agent and in total, `conflict_exposure_time_s`; per interaction, the
exposure due to that one neighbour; per step, the `exposed` column of the trajectory.

## 4. `yield_event`

**An agent walking at less than `yield_speed_fraction` of its preferred speed for at
least `yield_min_duration_s`.** Precisely: a run of consecutive steps on each of which the
speed the agent moved at was below the fraction times its preferred speed, lasting at
least the minimum duration. The preferred speed is the agent's own, *before* any directive
scales it, so an agent that slows down because a directive told it to is yielding. A run
is closed when the agent speeds up, arrives, or the run ends.

A conflict that is settled by somebody waiting shows up as a yield event; one that is
settled by stepping aside at full speed does not.

*Reported:* per agent and in total, `yield_events` and `yield_time_s`; each event, with
its start, end and lowest speed, in `events.jsonl`.

## 5. `near_miss`

**Two bodies closer than `near_miss_distance_m`.** The separation of two agents is the
distance between the surfaces of their discs: the distance between centres minus the two
radii. A near miss is an episode: it begins on the first step at whose end the separation
is below the threshold and ends on the first at whose end it is not. A pair that comes
close twice has two.

Plain ORCA has two agents pass with their discs just clear of each other, so under plain
ORCA nearly every pass is a near miss at this threshold. A directive with a
`clearance_margin` of at least the threshold removes them.

A collision is also a near miss: the same pair is counted under both.

*Reported:* per agent and in total, `near_misses`; each episode, with its smallest
separation, in `events.jsonl`.

## 6. `collision` and `deadlock`

Both keep the definitions of issue #24.

**`collision`.** Two discs overlap: their centres are closer than the sum of their radii.
Or a disc overlaps a wall. (An overlap of less than a nanometre is rounding, not a
collision.) A directive's clearance margin plays no part: a collision is between bodies.

**`deadlock`.** Every agent that has not arrived stays below `deadlock.speed_eps_mps` for
`deadlock.window_s`. In a crowd this is a strict test: a jam in which a few agents still
shuffle is not a deadlock by it, and shows up instead as a run that reaches its time
limit, with yield events.

**What a run does on a collision is a setting.** `on_collision: stop`, the default, ends
the run there with status `collision`, as every run of issue #24 does. `on_collision:
continue` records the collision and goes on; the status is then whatever the run ends
with, and the collisions are in the outcome. `bidirectional_flow` uses `continue`. The
reason is in `orca.md`, section 7: in a crowd ORCA's fallback can let two discs overlap,
and a run that stopped at the first such overlap would end before it had shown anything.
Whether an overlap matters is for the reader to judge from its depth, which is reported
for every episode. **The overlaps are not all small.** In the committed two-way flow
(`runs/si1_bidirectional_flow`), with the shipped limit of ten neighbours there are 512
episodes, with a median depth of 10 mm and a deepest of 82 mm, a third of a body radius;
with forty neighbours there are 87, with a median of 1.9 mm and a deepest of 23 mm.

*Reported:* `collisions.agent_agent` and `collisions.agent_wall` (numbers of episodes),
`collisions.time_s` (of the first), `collisions.agents`, `collisions.max_overlap_m`;
`deadlock`; each collision episode in `events.jsonl`.

## 7. Also reported

| Metric | Definition | Where |
|---|---|---|
| Minimum separation | The smallest separation (section 5) between an agent and any neighbour it perceived, over the run. Negative means an overlap of that depth. | `min_separation_m`, per agent, per interaction and in total |
| Time to goal | When the agent's progress along its path came within the goal tolerance of the end. `null` if it never did. | `time_to_goal_s`; `makespan_s` is the latest, `null` unless all arrived |
| Path deviation | The distance from the agent's position to its desired path, at the end of each step: its mean and its largest value. An agent pushed back behind its starting point is measured from that point. | `path_deviation_mean_m`, `path_deviation_max_m` |
| Distance walked | The sum of speed times time step. | `distance_m` |
| Fallback | A step on which an agent's linear program was infeasible and ORCA's fallback chose its velocity (`orca.md`, section 7). | `fallback_steps` per agent; `fallback_agent_steps` and `steps_with_fallback` (steps on which at least one agent used it) in total |
| One-sided perception | A step on which an agent was constrained by a neighbour that did not have it among its own perceived neighbours. The pairwise guarantee does not cover such a step. | `one_sided_steps`, `one_sided_agent_steps` |
| Time under the arbiter | Steps on which the agent was in a pair the arbiter held. | `arbiter_time_s` |
| Smallest gap to a wall | The distance from the agent's disc to the nearest wall. | `min_wall_gap_m` |

## 8. Reading them together

A sketch of how the metrics separate the two categories, for one agent in one interaction.
It is a proposal for the evaluation sub-issue, not something this sub-issue applies.

| Exposure | Yield event | Reading |
|---|---|---|
| none | none | The conflict never arose. If a directive was active, the rule avoided it (category A). |
| none | yes | Avoided, at a cost: the agent slowed because a rule told it to, before any conflict. |
| some | none | A conflict arose and was resolved on the move: someone stepped aside. |
| some | yes | A conflict arose and was resolved by waiting (category C). |
| a lot, and the run ends in `deadlock` | yes | Not resolved. |

"Avoided" in this sense needs a reference: the same scenario under plain ORCA, to show
that there was a conflict to avoid.

## 9. The outcome of a pair interaction: `avoided`, `resolved`, `failed` (issue #28)

The question of section 8, asked of every **pair interaction** (two agents, from the first
step on which either perceives the other to the first on which neither does, one arrives, or
the run ends; `log-schema.md`, `pair_interactions.jsonl`). It uses the definitions and
thresholds above, unchanged, and is computed at the end of every avoidance run, with or
without rules.

| Category | Definition |
|---|---|
| `failed` | The two **collided** while the pair was open (a collision episode between them, section 6, overlapping the pair interaction in time), or the run ended in **deadlock** with the pair open |
| `resolved` | Not failed, and **either agent was exposed** to the other (section 3) **or either had a yield event** (section 4) overlapping the pair interaction in time |
| `avoided` | Neither: no exposure on either side, no yield event, no collision, no deadlock |

They are tried in that order, so every pair gets exactly one.

**The issue's words, and the gap in them.** Issue #28 defines `avoided` as "conflict
exposure time zero and no yield event", `resolved` as "exposure greater than zero, ending
without collision or deadlock", and `failed` as "collision or deadlock". A pair with **no
exposure but a yield event** fits none of the three. It is not a rare case: it is the
follower the arbiter holds back at a single-file segment, whose wanted speed is capped
before ORCA ever sees a conflict, and an agent slowed below half its speed by a rule.
**DD57 (decision): such a pair is `resolved`**, settled by somebody waiting, which is how
section 8 already reads a yield. This needs sign-off; each pair records what decided its
category (`outcome_detail`: `exposed`, `yield_events`, `collisions`, `deadlock`), and
`outcome.json` counts each ingredient (`interaction_outcomes.pairs_with`), so another
reading can be computed from the logs without running anything again.

**Yields in a crowd are attributed by time (DD58).** A yield event is an agent's, not a
pair's (section 4). A pair counts one if it overlaps the pair interaction in time. With two
agents that is exact. In a crowd it can blame a pair for a wait that someone else caused,
which can only move a pair from `avoided` to `resolved`, never the other way.

**A run that times out.** A pair still open when the run reaches its time limit is
categorised by the same rules, and flagged (`open_at_timeout`), because "ending without
collision or deadlock" is not the same as having ended.

**With a perturbed baseline** (`baseline.md`), the preferred velocity an agent hands ORCA
includes the perturbation, and exposure (section 3) is measured against that velocity. At
1e-4 m/s it can only matter for a pair that is already within that much of a collision
course.

## 10. Two diagnostics: walking backwards, and being hurried along (issue #28)

Issue #26 found two things an ORCA agent does that are the algorithm's and are not offered
as human behaviour (`WORK_LOG-26.md`, "What the checking turned up"): with shares (1, 0) and
no side, the agent with share 1 walks backwards along its own line; and exactly behind a
slower walker, ORCA pushes the slower one along. Issue #28 asks for both to be counted, in
rule runs against baseline runs, and **not fixed**. They are counted in the run loop on every
step, so that the counts do not depend on how thinly the trajectory is logged.

| Diagnostic | An agent on a step | Counted as |
|---|---|---|
| `backward` | moves against the direction of its own path (at its progress along it) faster than **0.1 m/s** | an episode: a run of such steps lasting at least **1.0 s** |
| `hurried` | moves faster than **1.05 times** the speed it wants (its preferred speed, scaled by its directives and capped by the arbiter), with a neighbour it perceives **behind** it (that neighbour's position more than 90° from the direction of its path) | an episode, likewise |

**The thresholds are definitions with no source**, set to separate the two artefacts from
ordinary ORCA motion: a side-step is not walking backwards, and the brief speed-ups of a
dodge are not being hurried along. Every outcome repeats them.

**What "hurried" can get wrong.** It does not know *why* the agent is fast: with two agents
it is the one behind; in a crowd, a neighbour behind may not be the cause. It can therefore
over-count in a crowd. The overtaking scenario is where it was found and where it is exact.

**Intentional backing is not walking backwards** (issue #32). An agent told to `back_up`
backs out of a single-file passage on purpose, at its own backing speed (`derivations.md`,
section 17). The steps on which it is backing out are never counted as `backward`, though
they meet the definition; they are counted as the manoeuvre's, in `outcome.json`'s `back_up`
block (`backing_time_s`, `backing_distance_m`). Every other backward step counts as before:
the follower that the arbiter's way pushes back at nearly the leader's speed (section 17.1
there), and a backer that ORCA moves backwards while it waits outside the passage for the
other. Since log schema 5 the artefact also has a distance, `backward_distance_m`: how far
the agent moved against the direction of its path **within its backward episodes** (a run
shorter than 1.0 s adds nothing, as it adds no episode). The total distance walked backwards
is the two added: intentional and artefact, each reported on its own.

*Reported:* `outcome.json`, `artefacts`: per agent `backward_episodes`, `backward_time_s`,
`hurried_episodes`, `hurried_time_s`, and (log schema 5) `backward_distance_m`; in total the
same and `agents_backward`, `agents_hurried` (how many agents had any); and the `thresholds`.
The summary has `backward_episodes` and `hurried_episodes`, and (log schema 5)
`backward_distance_m` beside the intentional `backing_distance_m`.

## 11. Pair exposure and severity tiers (issue #30)

Issue #30 asks for one definition of a conflict, used wherever one is classified, that does
not depend on how a rule shares out the avoiding; and for more grades than the three
categories of section 9, which in the two-agent scenarios are almost always `resolved`
(`WORK_LOG-28.md`, Q7 and Q8). The arithmetic is in `negsim/avoidance/exposure.py`,
`negsim/metrics/avoidance.py` and `negsim/avoidance/simulation.py`; the derivation is
`derivations.md`, section 16.

### 11.1 The intended velocity, and where each directive field acts

An agent's **intended velocity** v̂ on a step is the velocity it hands ORCA: along its
desired path at its preferred speed, times the smallest `speed_scale` of its directives,
no faster than the arbiter's bound, plus the baseline's perturbation. It is fixed before
ORCA's projection and is logged as `pref_vx_mps`, `pref_vy_mps` in the trajectory. Checked
in the code, the five directive fields act as follows:

| Field | Acts on | Where | What follows for measuring avoidance |
|---|---|---|---|
| `speed_scale` | v̂ itself, before the projection | `simulation.py`, `_travel_speed` | It can take a pair off a collision course on the step it applies |
| `passage_order` | v̂ of the follower, through the arbiter's speed bound; and, while the arbiter holds the pair, the shares (1 and 0) inside the projection | `coordination.py`; `simulation.py`, steps 3 and 4 | As `speed_scale`, for the follower |
| `side_preference` | Only inside the projection, and only while ORCA finds the pair on a collision course (`derivations.md`, section 10) | `orca.py`, `agent_half_plane` | It cannot change pair exposure on the step it acts: v̂ is the same with it or without it. It can lower it only on later steps, through where the agents have moved meanwhile |
| `responsibility_share` | Only inside the projection, and only on a collision course (`derivations.md`, section 9) | `orca.py`, `_half_plane` | As `side_preference` |
| `clearance_margin` | Only inside the projection, but on every step: it enlarges the obstacle ORCA uses | `simulation.py`, step 4 | It does not enter pair exposure, whose obstacle is the two bodies'. ORCA reacts earlier, which can keep v̂ off a collision course on later steps |

**The consequence.** A rule made of a side and shares only (as `keep_left_head_on` is)
changes nothing until ORCA finds the pair on a collision course, so on the same seed the
pair's first exposed step is the baseline's: such a rule cannot make the pair T0 (below)
where the baseline put it on a collision course. Its effect shows in how long the exposure
lasts and in the higher tiers. A rule can *avoid* a conflict in the sense of section 8 only
through `speed_scale`, `passage_order`, or a clearance margin that makes ORCA act before the
bodies' own obstacle is reached.
*Tested:* `tests/test_pair_exposure.py::test_a_side_and_shares_leave_the_first_exposed_step_as_it_was`.

### 11.2 `pair_exposure_time`

**The time during which the two agents' intended velocities put them on a collision
course.** On each step, for every open pair interaction (section 9) of two agents that have
not arrived: with `p` the second agent's position minus the first's and `w = v̂_i − v̂_j`,
the pair is **exposed** if `w` lies inside the truncated velocity obstacle VO^τ_{i|j} of
the two bodies, the relative velocities that bring them into contact within τ
(`orca.md`, section 3), by more than `pair_exposure_eps_mps`: the relative velocity would
have to change by more than that for them to miss. Bodies that already overlap are exposed.
`pair_exposure_time_s` is the number of exposed steps times the time step.

- **The obstacle is the bodies'**: radius `r_i + r_j`, with no clearance margin, so that the
  measure is the same function in every condition, whatever the directives ask of ORCA.
- **The horizon** is the larger of the two agents' ORCA horizons (`time_horizon`, 3 s in
  every shipped scenario, where the two are always equal).
- **The tolerance**, 1e-3 m/s by default, is five times the most that the primary
  baseline's perturbation can change `w` (2 × 1e-4 m/s), so the perturbation alone never
  decides whether a step counts (Q7 of `WORK_LOG-28.md`).
- **It reads no directive.** The responsibility shares in particular enter only ORCA's
  projection, after v̂ is fixed, so the same state of the world gives the same answer under
  any shares (`derivations.md`, section 16).
- **It is the pair's**, symmetric in the two agents, and measured whether one perceives the
  other or both do.

*Reported:* per pair interaction, `pair_exposure_time_s` and `first_pair_exposed_step`; in
total (`totals.pair_exposure_time_s`), and in the summary.

### 11.3 Severity tiers

Each pair interaction gets the **highest** tier that applies:

| Tier | Name | Applies when |
|---|---|---|
| T4 | deadlock or collision | The two collided while the pair was open, or the run ended in deadlock with the pair open: `failed` of section 9 |
| T3 | near miss | A near miss between the two (section 5) overlapping the pair interaction |
| T2 | yield event | A yield event (section 4) of either agent overlapping the pair interaction |
| T1 | on a collision course | `pair_exposure_time_s` above `collision_course_min_s` |
| T0 | interaction only | None of the above: the two were in range and never on a collision course |

Events are attributed to the pair by overlap in time, as for the categories (DD58): exact
with two agents, and in a crowd able to move a pair only upward. A near miss or a yield can
make a pair T3 or T2 without any pair exposure, for example when ORCA steps two agents that
were never on a collision course closer than 0.1 m.

**What the tiers look like under plain ORCA.** Plain ORCA passes two bodies with their
discs just clear of each other, inside the near-miss distance (section 5), so under the
primary baseline an ordinary pass of two agents on a collision course is T3, not T1. A
count of T3 is therefore not an alarm; a rule that keeps the two further apart than the
near-miss distance is what can bring such a pair down to T1 or T2. `cases.md` gives the
counts in the case-source runs.

**The categories of section 9 are kept as issue #28 defined them**, on the per-agent
exposure, so that every result reported so far stays comparable; the tier is recorded
beside the category (`severity_tier`, with what decided it in `tier_detail`), and
`outcome_detail.pair_exposed` lets the categories be recomputed on pair exposure without
running anything again. **DD65 (decision).** Every conflict classified from issue #30 on
(the eligibility of conflict cases, their strata, the replay of a generated rule) uses the
tiers.

*Reported:* per pair interaction, `severity_tier` and `tier_detail` (`pair_exposure_time_s`,
`yield_events`, `near_misses`, `collisions`, `deadlock`); in `outcome.json`,
`interaction_outcomes.tiers`, the number of pairs in each tier; in the summary,
`pairs_t0` to `pairs_t4`.
