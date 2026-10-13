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
typically by millimetres, and a run that stopped at the first such overlap would end
before it had shown anything. Whether such an overlap matters is for the reader to judge
from its depth, which is reported.

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
