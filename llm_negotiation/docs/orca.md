# ORCA: what was implemented, from where, and where it departs

The avoidance layer of issue #26 steers agents with ORCA, Optimal Reciprocal Collision
Avoidance. This file says what the algorithm is, which section of the paper each part of
the code comes from, how the code was checked against the reference library, and every
place where it does something the paper or the library does not. Decisions are marked as
decisions; `architecture.md` numbers them.

Locators: `orca:LINE` is a line of `refs/si1_orca_vandenberg2011.txt`, the text of the
paper. `Agent.cc:LINE` and the like are lines of the RVO2 library at the commit given in
section 2, cached in `refs/si1_rvo2_75822bb_excerpts.txt` with their original numbers.

## 1. The source

> J. van den Berg, S. J. Guy, M. Lin and D. Manocha, "Reciprocal n-body collision
> avoidance", in *Robotics Research: The 14th International Symposium ISRR*, pp. 3–19,
> Springer, 2011. DOI 10.1007/978-3-642-19457-3_1.

**The citation is confirmed for one version of the GameChat paper.** It is reference [22]
of arXiv:2503.12333v1 (`refs/ln_gamechat_arxiv_v1.txt:596-598`), which says of it: "ORCA
adds collision avoidance constraints in the form of half-planes in the space of velocities
... However, deadlocks often result due to the structure of the half-planes" (line 73). In
version 2 of that paper the numbering changed and [22] is another work
(`refs/mahadevan2025_gamechat.txt:558`). 2011 is the year the proceedings were published;
the copy read is the authors' own, from `gamma.cs.unc.edu/ORCA/publications/ORCA.pdf`.

Sections of the paper the code is built from:

| Paper | What it gives | Where it is here |
|---|---|---|
| Sec 3 (`orca:139`) | The problem: discs that see each other's position, velocity and radius, and nothing else | `negsim/avoidance/simulation.py` |
| Sec 4.1, eqs. 1–2 (`orca:172`) | The velocity obstacle of a pair for a time horizon τ | `orca.py`, `agent_half_plane` |
| Sec 4.2, eqs. 5–6 (`orca:227`) | The half-plane each agent is allowed: half of the smallest change, each | `orca.py`, `agent_half_plane` |
| Sec 5.1, eqs. 7–9 (`orca:330`) | Intersect the half-planes, take the velocity nearest the preferred one, move | `lp.py`, `solve`; `core/dynamics.py`, `holonomic_step` |
| Sec 5.1 (`orca:411-420`) | Which neighbours matter, and a spatial index to find them | `neighbours.py` |
| Sec 5.2 (`orca:478`) | Use the *current* velocity as the optimisation velocity | `simulation.py`, step 4 |
| Sec 5.3, eq. 10 (`orca:488`) | The fallback when no velocity satisfies every half-plane | `lp.py`, `linear_program_3` |
| Sec 5.4, eq. 11 (`orca:543`) | Walls | `orca.py`, `wall_half_plane` |

The paper assumes "the robot is holonomic, i.e. it can move in any direction" (`orca:55`)
and names kinematic constraints as future work (`orca:651-663`). That is why the avoidance
scenarios use holonomic dynamics and why the dynamics model is pluggable
(`architecture.md`, DD23).

## 2. The reference library, and what was taken from it

The library is RVO2, `github.com/snape/RVO2`, by the paper's authors and Jamie Snape. It was
read at commit `75822bba14462c2e872ca96423825017ecd24764` (branch `main`, 2026-09-25), by
cloning without a checkout and reading files through `git show`. **It was not built,
installed or run, and it is not a dependency.** The project needs to change two things
inside ORCA, the share of the avoidance each agent takes and the side it passes on, and
the library fixes both in its source (section 9).

**Licence: Apache License 2.0** for the source files (the SPDX header of `src/Agent.cc`,
lines 5–6, and `LICENSE` at the root), copyright "2008 University of North Carolina at
Chapel Hill". Its README and citation file are CC-BY-SA-4.0. It has no `NOTICE` file.

What was done with it, part by part:

- **The half-planes** (`orca.py`) were written from the paper. The geometry in section 3
  below was worked out here and then compared with `Agent.cc:542-609` line by line; the two
  agree except where section 9 says otherwise.
- **The linear programs** (`lp.py`) are **adapted from** `linearProgram1`, `linearProgram2`
  and `linearProgram3` (`Agent.cc:63-242`). The paper names the algorithm (it cites a
  textbook for the two-dimensional program and says the fallback "can project the problem
  down on the v-plane", `orca:488`), and the issue asks for the reference algorithm to be
  followed for the fallback. The file carries the library's copyright and licence notice
  and a list of the changes; the licence text is in `LICENSES/Apache-2.0.txt`; see
  `THIRD_PARTY_NOTICES.md`.
- **The neighbour search** (`neighbours.py`) is this project's own: a grid, where the
  library has a k-d tree.
- **The walls** follow the paper, not the library (section 5).

## 3. The half-plane for a pair of agents

Agent A is at `p_A` with velocity `v_A` and radius `r_A`; B likewise. Write

    p = p_B - p_A        v = v_A - v_B        R = r_A + r_B (+ a clearance margin)

The **velocity obstacle** is the set of relative velocities `v` for which the two come
within `R` of each other at some time up to τ (eq. 2):

    VO = { v : t v is inside the disc of radius R around p, for some t in (0, τ] }

Dividing by `t`: `v` is in the disc of radius `R / t` around `p / t`. As `t` runs from τ
down to 0 those discs sweep out a cone with its tip at the origin, cut off near the tip by
the disc for `t = τ`, which has centre `p / τ` and radius `R / τ` (the paper's Fig. 1b).
The boundary therefore has three parts: the **arc** of that disc that faces the origin,
and the two straight **legs**, tangent to it. The legs make an angle θ with the axis `p`,
with `sin θ = R / |p|`. "Left" and "right" are as A sees them, looking at B.

ORCA takes the point of the boundary nearest to `v` (eq. 5). Call the vector from `v` to
that point `u` and the outward normal there `n`. Which part of the boundary is nearest is
decided by `w = v - p / τ`, the position of `v` as seen from the centre of the cut-off
disc:

- **The arc**, if `w` points back toward the origin within the angle the arc spans:
  `w · p < 0` and `(w · p)² > R² |w|²`. Then `n = w / |w|` and `u = (R / τ - |w|) n`.
- **A leg** otherwise: the left one if `v` is to the left of the axis (`p × w > 0`), the
  right one if it is to the right. With the leg's unit direction `l`, the foot of the
  perpendicular from `v` is `(v · l) l`, and `u` is the vector from `v` to it.

The pair is **on a collision course** when `v` is inside the obstacle, which is when `u`
and `n` point the same way; then `u` is the smallest change of relative velocity that
avoids the collision. Otherwise `u` points toward the obstacle and `|u|` is the room that
is left.

The paper gives A the half-plane (eq. 6)

    ORCA_A|B = { v' : (v' - (v_A + u / 2)) · n >= 0 }

"robot A adapts its velocity by (at least) ½ u and assumes that B takes care of the other
half" (`orca:280`), and "the above equations also apply if A and B are not on a collision
course" (`orca:308`).

`agent_half_plane` returns that half-plane, the normal, the signed size of `u` along `n`
(`margin`: positive on a collision course) and which part of the boundary it was built on.
*Tested against hand-computed cases:* `tests/test_orca.py`, from
`test_arc_when_the_pair_is_not_on_a_collision_course` to
`test_overlapping_agents_are_asked_to_separate_within_one_step`.

**Already too close.** If the two are nearer than `R` there is no cone. The library asks
for them to be `R` apart after one time step: it uses the cut-off disc for `t = dt`
(`Agent.cc:593-605`). This does the same. Without a clearance margin it only matters after
a collision; with one, it is what restores a margin that was intruded on.

## 4. An exact tie between the two sides

When `v` lies exactly on the axis of the cone, beyond the centre of the cut-off disc, the
two legs are equally near and eq. 5 has two answers. The paper does not say which to take.

**The library takes the right-hand leg.** Its test is `det(relativePosition, w) > 0.0F` for
the left leg and anything else for the right (`Agent.cc:574-588`). Two agents meeting in
this exact tie would both step to their own right and pass. That is a convention, "keep
right", written into the solver.

**DD26 (decision). This implementation does not break the tie.** A study of which side
people pass on cannot have one side built in where nobody chose it. When neither leg is
nearer, the half-plane is taken at the tip of the arc instead. Its tangent there is at
right angles to the axis, so it limits only how fast the two may close and favours no
side. It is still a tangent to the obstacle, so the half-plane is still safe.

The library's behaviour is available as `orca.tie_break: right` in a scenario config (and
`left` for its mirror image), so that a comparison with RVO2 as published can be made.
*Tested:* `test_an_exact_tie_between_the_legs_is_not_broken_by_default`,
`test_the_rvo2_tie_break_takes_the_right_leg`.

In the scenarios shipped here the tie-break turns out not to be what matters: see section
6 and the two head-on runs in the README, which come out the same with either setting.

## 5. Walls

The paper models walls as line segments and treats them like agents that do not move, "so
the robots should take full responsibility of avoiding collisions with them"
(`orca:549`). It defines the half-plane as the one "whose delimiting line is the tangent line to
[the wall's velocity obstacle] at the closest point to [the optimisation velocity]", and
then: "In case of obstacles, we choose [the optimisation velocity] = 0" (`orca:577`).

For a convex wall block and an agent at `p` with radius `r`, the obstacle's point nearest
the origin of velocity space lies straight toward the wall's nearest point `q`, at
distance `(|q - p| - r) / τ_obst`, and the tangent there is at right angles to that
direction. So the half-plane is

    v · (q - p) / |q - p|  <=  (|q - p| - r) / τ_obst

in words: do not approach the nearest point of the wall faster than the gap divided by the
horizon. That is `wall_half_plane`. A wall further away than `τ_obst` times the agent's
maximum speed cannot exclude any velocity the agent could have and is skipped, which is
the range the library uses too (`Agent.cc:258`).

**DD27 (decision). Walls follow the paper; the library does something else.** RVO2
projects the agent's *current* velocity onto the wall's obstacle (`Agent.cc:455-535`), not
zero. That lets an agent whose path just clears the end of a wall keep its speed, where
the rule above slows it as it comes up to the corner. The paper's rule was kept because it
is one line, can be checked by hand, and comes with a proof that holds in discrete time
(`derivations.md`, section 12): an agent that obeys it never touches a wall, provided the
horizon is at least one time step. The config loader refuses a shorter horizon. The cost
is the slowing at corners, which is why the horizon for walls is short (0.15 s,
`parameters.md`), as the paper suggests: "we can typically use a smaller value of τ with
respect to obstacles" (`orca:579`).

Every wall half-plane contains the zero velocity, so the walls alone can never be
infeasible. That is what allows the fallback to keep them hard.
*Tested:* `test_wall_half_plane_limits_the_approach_speed`,
`test_obeying_the_wall_half_plane_never_reaches_the_wall`,
`test_wall_half_planes_of_a_corridor_always_allow_standing_still`.

The paper also says what walls do not do: "they do not make the robot move around them"
(`orca:592-594`). Getting round a wall is the job of the preferred velocity, which here points
along the agent's desired path.

## 6. Why an exactly symmetric encounter is never resolved

Two agents walk straight at each other, exactly head-on. By symmetry `v` is on the axis,
always. Far apart, `v` is outside the obstacle, in front of the arc. As they close, the
obstacle grows toward `v`, and `v` meets it **at the tip of the arc**, not at a leg. The
nearest boundary point is then unique, there is no tie, and its normal points straight
back along the axis. Both agents are told to slow down and neither is told to turn. They
stay exactly head-on, so the same thing happens on the next step. The closing speed is
held at `(distance - R) / τ`, which goes to zero as the distance goes to `R`: they come to
rest facing each other, and the run ends in a deadlock.

So the deadlock does not come from how a tie is broken. A leg is only the nearest part of
the boundary when the two are already within about τ seconds of meeting at the moment they
first notice each other; with a sensing radius as long as the paper recommends, they
notice earlier and the arc is always reached first.

The library's own examples say as much. Two of the three add a random vector of length up
to 0.0001 to every preferred velocity, under the comment "Perturb a little to avoid
deadlocks due to perfect symmetry" (`examples/Blocks.cc:178`, `examples/Roadmap.cc:322`).
This implementation adds no such perturbation, so that when symmetry is broken in a run it
is broken by something the config states: a starting offset, or a directive.

*Tested:* an exactly symmetric start stays exactly symmetric, to the last bit, and nobody
moves sideways (`tests/test_avoidance_sim.py::test_an_exactly_symmetric_start_stays_exactly_symmetric_under_plain_orca`).
What happens in each scenario is a result, reported in the README from the committed runs.

## 7. The linear programs, and the infeasible case

Each agent has one half-plane per wall in reach and one per perceived neighbour, and a
disc: its speed may not exceed its maximum. It takes the velocity inside all of them
nearest its preferred velocity (eqs. 7–8). `linear_program_2` does this the way the paper
describes and the library implements: the half-planes are added one at a time, and when
the current optimum violates the new one, the new optimum is found on the new half-plane's
boundary line by a one-dimensional program.

**When no velocity satisfies them all** the paper says: "choosing a collision-free
velocity cannot be guaranteed. Instead, we select the 'safest possible' velocity for the
robot, i.e. the velocity that minimally 'penetrates' the constraints" (`orca:493-497`).
Formally (eq. 10) it minimises, over the disc, the largest signed distance to any agent
half-plane. `linear_program_3` solves that as the library does: starting where the
two-dimensional program stopped, for each further half-plane that is violated by more
than the worst so far, it re-optimises on the locus where the new violation equals each
earlier one.

Three properties of the fallback, each from the paper and each tested:

- **Walls are not relaxed.** "The constraints of the obstacles are not relaxed"
  (`orca:589`). The wall half-planes come first in the list and stay hard.
  *Tested:* `test_fallback_never_relaxes_a_wall`.
- **The preferred velocity plays no part.** "The new velocity selected for the robot does
  not depend on the robot's preferred velocity" (`orca:539`).
  *Tested:* `test_fallback_does_not_depend_on_the_preferred_velocity`.
- **It always returns something**, and what it returns is the least bad.
  *Tested against a dense search:* `test_fallback_minimises_the_worst_violation`.

**What it does not give is safety.** A velocity that violates a half-plane may lead to an
overlap, and in a dense crowd it does. Every use of the fallback is counted
(`steps_with_fallback`, `fallback_agent_steps` in the outcome, and the `fallback` column of
the trajectory), and a test checks the converse: in a dense two-way flow no collision ever
begins on a step on which both agents had a feasible program
(`test_a_collision_only_ever_begins_right_after_a_fallback`). A second test checks the
guarantee itself in the same flow, from positions and velocities alone and without the
half-plane code: on every step, for every pair that perceive each other and are both
feasible, the velocities chosen keep the two at least the sum of their radii apart for τ
(`test_two_feasible_agents_that_perceive_each_other_never_choose_velocities_that_collide_within_tau`;
over 40,000 such pair-steps in the test, with no exception. `WORK_LOG-26.md` records the
same check made once on the two committed 100-agent runs).

**One tie is resolved differently from the library.** Inside the fallback, a program
maximises along a direction. When that direction is exactly at right angles to a
half-plane's boundary line every point of the line is equally good. The library returns
the line's left end, which is a velocity at the maximum speed (`Agent.cc:108-116`, where a
zero dot product falls to the `else`). With walls that are parallel to the axes this
arises in practice, and an agent squeezed between a wall and a neighbour would leave
sideways at full speed. This implementation returns the slowest of the equally good
velocities. The value of the optimum is the same.
*Tested:* `test_fallback_splits_the_difference_between_opposed_half_planes`.

The two-dimensional program as a whole is checked against a brute-force solver on 3,000
random cases, about half of them infeasible
(`test_the_program_agrees_with_a_brute_force_solver`).

## 8. Neighbours

An agent takes into account the nearest `max_neighbours` agents no further away than its
sensing radius `R`, nearest first, which is what the library does (`Agent.cc:619-642`).
The paper's reason for a radius: agents "farther away from robot A than
(v_A^max + v_B^max) τ will never collide with robot A within τ time, so they can safely be
left out" (`orca:411`). The default `R` here is that bound plus the two radii, which the
paper's sentence leaves out (`parameters.md`).

They are found with a uniform grid (`neighbours.py`), searched ring by ring outward from
the agent's cell until no cell further out could hold a neighbour that would be kept. The
cost of a query depends on the local density and not on the size of the crowd.
*Tested against looking at every agent:* `tests/test_neighbours.py`.

The library's documentation warns about both settings: "If the number is too low, the
simulation will not be safe" (`RVOSimulator.h:77-88`). The bidirectional flow shows what
that means with ten neighbours (README).

## 9. Departures, in one table

| | The paper | RVO2 | This implementation | Why |
|---|---|---|---|---|
| Share of `u` each agent takes | one half (eq. 6) | 0.5, a constant (`Agent.cc:607`) | a per-pair number in [0, 1] on a collision course; one half of the room otherwise | The directive's `responsibility_share`. The split of the room is what keeps shares that sum to more than 1 safe (`derivations.md`, section 9). |
| Which boundary point | the nearest (eq. 5) | the nearest | the nearest; on a collision course with a side preference, the point on that leg | The directive's `side_preference` (`derivations.md`, section 10). |
| An exact tie between the legs | not stated | the right leg | neither: the tip of the arc | Section 4. `orca.tie_break: right` gives the library's behaviour. |
| Combined radius | `r_A + r_B` | `r_A + r_B` | `r_A + r_B +` the pair's clearance margin | The directive's `clearance_margin`. |
| Walls | tangent at the point nearest zero velocity (Sec 5.4) | the current velocity projected (`Agent.cc:455-535`) | the paper's | Section 5. |
| A tie inside the fallback | not stated | the end of the line, at maximum speed | the slowest of the equally good | Section 7. |
| Symmetry | not discussed | examples perturb the preferred velocity | no perturbation | Section 6. |
| Neighbour search | "a kD-tree" (Sec 5.1) | a k-d tree | a grid | Either is allowed by the issue; the grid is simpler to check. |
| Arithmetic | — | single precision, tolerance 1e-5 (`Vector2.cc:45`) | double precision, tolerance 1e-9 | Python's floats. |

With `responsibility_share` 0.5, no side preference, no clearance margin and
`tie_break: right`, an agent that meets no wall computes what the library computes, up to
the precision of the arithmetic. That statement rests on reading the two side by side; the
library was not run, so it has not been confirmed by comparing outputs.

## 10. What is guaranteed, and what is not

For two agents that perceive each other, whose directives have been combined
(`negsim.avoidance.directives.resolve_pair`) and whose programs are both feasible: no
collision for τ seconds if both kept their new velocities, and so none before the next
step. *Tested* on random configurations (`test_shares_that_sum_to_at_least_one_keep_a_pair_collision_free_for_tau`),
on 500 seeded two-agent runs (`test_no_collision_in_random_two_agent_encounters_when_the_shares_sum_to_at_least_one`),
and pair by pair inside a crowd (section 7).

It does not cover:

- **The fallback.** With several neighbours the program can be infeasible (section 7).
- **A neighbour that is left out.** With more agents in range than `max_neighbours`, an
  agent may be constrained by a neighbour that is not constrained by it. The agent-steps
  on which that was so are counted (`one_sided_steps`).
- **Different horizons.** Each agent uses its own τ, as in the library. Two agents with
  different τ build different obstacles, and their half-planes are no longer exact mirror
  images. The shipped agent type has one τ.
- **A dynamics model that does not do as it is told.** The guarantee assumes the velocity
  chosen is the velocity realised.
- **Progress.** ORCA guarantees no collision. It guarantees nothing about anyone getting
  anywhere (section 6).
