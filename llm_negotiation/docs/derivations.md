# Derivations: how fast the follower may go, and how long the conflict region must be

This file derives the speed bound in `negsim/control/strategy1.py` and the conflict zone
in `negsim/conflict/zone.py`. Each result names the test that checks it. Paper locators
(`v1:LINE`) point into `refs/ln_gamechat_arxiv_v1.txt`.

## 1. The paper's rule

GameChat models two agents as "thin, car-like objects of length `l` and zero width"
(`v1:216`) whose straight paths cross at a point Q. Agent `i` is a distance `d_i` from Q
and both travel at up to `v_max`. The leader `j` keeps `v_max`. The follower `i`

> selects a velocity so it reaches Q at the instant that agent j completely clears Q. For
> our environment, this means agent i will choose a linear velocity of
> `d_i v_max / (l + d_j)` until reaching Q (`v1:300`).

The reasoning is one line. Measure `d` from each agent's front. The leader's rear passes Q
once the leader has moved `d_j + l`, at time `(d_j + l) / v_max`. The follower's front
must not be at Q before then: `d_i / v_i >= (d_j + l) / v_max`.

## 2. Generalised bound

Three things change in this project. Agents may have different maximum speeds. Agents may
have different sizes. And the thing they cannot share may be a stretch of path of length
`L`, such as a hallway, instead of a point.

Let the conflict region have length `L` along the leader's path. Let

- `d_i`, `d_j` be the distances from the **leading edge** of the follower `i` and of the
  leader `j` to the **entry** of the region, each along its own path [m];
- `v_j` be the leader's speed [m/s];
- `l_j` be the leader's body length [m];
- `v_i_max` be the follower's own maximum speed [m/s].

The leader's leading edge covers `d_j` to reach the region, `L` to cross it, and `l_j`
more before its trailing edge is out:

    t_clear = (d_j + L + l_j) / v_j

The follower's leading edge reaches the region at `d_i / v_i`, which must not be sooner:

    v_i  <=  d_i * v_j / (d_j + L + l_j),        and        v_i <= v_i_max

That is `follower_speed_bound(d_i, d_j, v_j, l_j, L, v_i_max)`.

**Reduction to the paper.** With `L = 0`, `l_j = l` and `v_j = v_max` the bound is
`d_i v_max / (l + d_j)`.
*Tested:* `test_conflict.py::test_follower_speed_reduces_to_the_papers_formula`, and
`::test_follower_arrives_exactly_when_the_leader_has_cleared` for the general case.

**Edge cases.** If `d_j + L + l_j <= 0` the leader is already clear and the bound is
`v_i_max`. Otherwise, if `d_i <= 0` the follower is at the entry and must wait: the bound
is 0. *Tested:* `::test_follower_waits_at_the_entry_and_is_released_once_the_leader_is_clear`.

**Which speed is `v_j`?** The leader's maximum speed, since "the leader will move at
`v_max`" (`v1:224`). If the leader turns out slower, the follower is still safe: see
section 6.

## 3. Body length for circular agents

The simulator's agents are discs. A disc of radius `r` extends `r` ahead of its centre and
`r` behind it, so along its direction of travel:

- **body length** `l = 2r`, the diameter;
- **leading edge** at the centre's position plus `r`; trailing edge at minus `r`.

The simulator tracks centres, so it is convenient to restate the region in terms of where
a *centre* may be. Call the stretch of path in which the centre lies while any part of the
body is in the region the agent's **zone**, running from `d_in` to `d_out` ahead of the
centre. The leading edge enters the region when the centre enters the zone, and the
trailing edge leaves the region when the centre leaves the zone. Therefore

    d = d_in            L = (d_out - d_in) - 2r            l = 2r

and `d + L + l = d_out`. In centre terms the bound is simply

    v_i  <=  d_in_i * v_j / d_out_j

`negsim.conflict.zone.edge_quantities` does this translation, and the code calls the
`(d, L, l)` form so that it reads like the formula above.
*Tested:* `::test_edge_quantities_restate_a_centre_zone_as_d_L_l`,
`::test_bound_from_zone_views_equals_the_formula_on_edge_quantities`.

## 4. How long must the region be?

The paper's cars have no width, so a point is enough for them. Discs have width, and the
region has to be long enough that two discs obeying the rule cannot touch. This section
finds that length.

**Setting.** Two agents with radii `r_i`, `r_j` move along paths `P_i`, `P_j`. Choose a
clearance `c = r_i + r_j + margin`, with `margin >= 0`. Define agent `i`'s zone as the part
of its path closer than `c` to the other agent's path:

    Z_i = { s : dist(P_i(s), path_j) < c }

and `Z_j` likewise.

**Claim.** If the two centres are never inside their zones at the same time, the centres
are never closer than `c`, so the discs are never closer than `margin`.

**Proof.** Suppose at some instant the centres, at `P_i(s_i)` and `P_j(s_j)`, are closer
than `c`. The point `P_j(s_j)` lies on path `j`, so the distance from `P_i(s_i)` to path
`j` is no more than the distance between the two centres, which is less than `c`. Hence
`s_i` is in `Z_i`. By the same argument `s_j` is in `Z_j`. So both centres are in their
zones at once. The claim is the contrapositive. ∎

The claim needs no assumption about the shape of the paths, the speeds, or the sizes. It
does assume that each centre stays on its path; `margin` is there to absorb tracking
error, which the tests measure
(`test_scenarios.py::test_agents_stay_on_their_desired_paths`).

The speed bound of section 2 enforces exactly this exclusion: the follower's centre does
not pass `d_in` until the leader's centre has passed `d_out`.
*Tested end to end:* in every scenario, for every start variant and either agent as
leader, the smallest gap between the two bodies is at least `margin`
(`test_scenarios.py::test_a_negotiated_leader_goes_first_whatever_the_geometry`).

### 4.1 Straight paths crossing at an angle

Two straight lines cross at Q at an angle `phi`. A point on one line at distance `s` from
Q is `s sin(phi)` from the other line. So the zone is the stretch within

    h = c / sin(phi) = (r_i + r_j + margin) / sin(phi)

of Q, on each line. This is `crossing_zone_views`, used by the `heading_ray` predictor,
which predicts that each agent keeps going straight along its heading as GameChat does
(`v1:224`).

In the edge-based terms of section 2 the region has length `L = 2h - 2r` on each path. At
a right angle with equal radii and no margin, `L = 2r`: the region is as long as the other
agent is wide, which is what one would draw.

This length is not slack. A follower that arrives early and waits at its zone entry is
exactly `h sin(phi) = c` from the leader's line, so a leader passing by clears it by
exactly the margin. A shorter zone would let that leader hit it.
*Tested:* `test_conflict.py::test_auto_zone_keeps_a_waiting_agent_clear_of_the_other_path`
for six angles from 15 to 160 degrees.

### 4.2 Paths that are not straight, or that meet head-on

In the hallway the two agents face each other on the same line. Their heading rays are
collinear and "intersect" nowhere, and in any case the two are in each other's way not
only in the hallway but for some distance beyond each mouth, until their paths have
separated by `c`. The `desired_path` predictor therefore computes `Z_i` directly from the
two desired paths: it samples path `i` every centimetre, keeps the samples closer than `c`
to path `j`, and refines both ends by bisection (`path_zone_interval`). If the path comes
close more than once it takes the whole span, which can only lengthen the zone.

*Tested:* the numerical zone equals the closed form of 4.1 for straight crossing paths at
four angles (`::test_path_zone_agrees_with_the_closed_form_for_straight_crossing_paths`),
and has the expected length for a corridor with run-outs
(`::test_path_zone_of_a_head_on_corridor_covers_the_shared_stretch_and_the_run_out`).

For the default hallway (`configs/scenarios/hallway.yaml`) the zone is the 4 m hallway,
0.6 m of centre line beyond each mouth, and a further stretch of each slanted leg, until
the two legs are 0.6 m apart. That is why each agent's path leaves the centre line in the
waiting areas: a follower waiting *on* the centre line would be standing where the leader
has to come out.

## 5. What goes wrong with a shorter region

**The paper's model, taken literally.** Set `L = 0` and `l = 2r` for two discs of radius
`r` crossing at a right angle. When the leader's trailing edge is at Q its centre is `r`
past Q; the follower's leading edge is at Q, so its centre is `r` short of Q, on the
perpendicular line. The centres are `sqrt(2) r = 1.41 r` apart and the discs, which need
`2r`, overlap. With `r = 0.1 m` that is 0.14 m against 0.20 m.
*Tested:* `test_scenarios.py::test_the_papers_zero_width_model_collides_at_the_intersection`
runs the intersection with the zone half-length set to `r` and no margin, and it ends in
a collision; with the automatic zone it completes.

This is a property of applying a zero-width model to discs, not an error in the paper. The
GameChat repository does not use the paper's formula either (`gamechat-notes.md`, D1).

**The repository's fixed 0.25 m.** The repository keeps the follower's centre 0.25 m short
of Q until the leader's centre is 0.25 m past it, whatever the crossing angle
(`mpc_cbf.py:237-239`). For its 0.1 m agents:

- At the intersection (`phi = 90` degrees) section 4.1 asks for `h = 0.2 m + margin`. The
  repository's value is this project's zone with a 0.05 m margin. They agree.
- At the doorway the paths cross at about 26 degrees and section 4.1 asks for
  `h = 0.25 / sin(26.3 degrees) = 0.56 m`. With 0.25 m, a follower waiting at its entry is
  only `0.25 sin(26.3 degrees) = 0.11 m` from the leader's line, and a leader passing it
  would hit it. *Tested:*
  `test_conflict.py::test_a_fixed_quarter_metre_zone_is_too_short_for_the_doorways_shallow_crossing`.

That waiting case does not arise in the paper's 18 doorway variants. Both agents have the
same speed and start within 0.25 m of each other, so the follower is never slowed below
about 0.2 m/s and trails the leader through the door instead of standing beside its path.
*Tested:* all nine combinations of start variant and leader complete with more than 0.1 m
between the bodies
(`test_scenarios.py::test_doorway_with_the_repositorys_fixed_margin_is_safe_for_the_papers_agents`).

**What this project does about it.**

- The scenarios default to the automatic zone of section 4, which is safe for any sizes
  and speeds. The cost is a later follower at shallow crossings: in the symmetric doorway
  the follower reaches its goal 3.8 s after the leader, against 1.8 s with the fixed
  0.25 m.
- The replication experiments (conditions C0 and C1 in the doorway) set
  `conflict.zone_half_length: 0.25`, the repository's value, so that their timings can be
  set beside the paper's. This is safe for those agents, as tested, and should not be
  carried over to agents of other sizes or speeds.

Both are design decisions (`architecture.md`, DD3).

## 6. Discrete time, and a leader slower than assumed

The bound is recomputed every step from the current distances. Write `D_j` for the
distance the leader still has to cover to be clear. In one step of length `dt` the leader
covers the fraction `v_j dt / D_j` of `D_j`, and the follower, moving at the bound,
covers `v_i dt / d_i = v_j dt / D_j` of its own remaining distance: the same fraction. The
two remaining distances therefore shrink in proportion and reach zero together, on the
step in which the leader clears. There is no overshoot from discretisation.

If the leader moves more slowly than the `v_j` assumed, the follower's fraction per step
is still `v_j dt / D_j`, which is less than 1 for as long as the leader cannot clear
within the step. The follower approaches its entry and never crosses it early. It arrives
sooner than it needed to and then waits, which is the case section 4.1 shows to be safe.

## 7. Who leads when speeds differ

The paper's Strategy 1 gives the lead to the agent with the shorter time to Q, and notes
that with a shared `v_max` this is the shorter distance (`v1:296`). Here the time is
`d_in / v_max` with each agent's own maximum speed (`time_to_region`), so a fast agent
further away can lead a slow one nearby.
*Tested:* `test_conflict.py::test_strategy1_compares_times_not_distances`.

A conflict is acted on only while the two agents would be in their zones at overlapping
times if both went at full speed (`is_social_minigame`), the paper's condition that "the
time intervals when the agents will occupy Q overlap" (`v1:224`). If one agent would be
through before the other arrives, neither slows, even if they had agreed that the later
one should go first: slowing down would serve no purpose.

## 8. A number to check against the paper

In the symmetric intersection both centres start 2 m from Q, and the zone is 0.25 m either
side of it, so `d_in = 1.75 m` and `d_out = 2.25 m`:

    v_follower = 1.75 * 0.3 / 2.25 = 0.2333 m/s

The paper's Table II gives the follower's minimum speed in the intersection as 0.233 m/s
when the roles are known in advance (`v1:329`, row "GameChat Ground Truth"; a mean over
its 18 variants).
*Tested:* `test_scenarios.py::test_follower_speed_in_the_symmetric_intersection_matches_the_formula`.
