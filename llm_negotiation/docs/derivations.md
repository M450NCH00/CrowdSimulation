# Derivations: how fast the follower may go, and how long the conflict region must be

This file derives the speed bound in `negsim/control/strategy1.py` and the conflict zone
in `negsim/conflict/zone.py`. Each result names the test that checks it. Paper locators
(`v1:LINE`) point into `refs/ln_gamechat_arxiv_v1.txt`.

Sections 1 to 8 are issue #24's. Sections 9 to 14 were added for the avoidance layer of
issue #26: what the directive fields do to ORCA's guarantee, the wall rule in discrete
time, the conflict zone at a single-file segment, and why a symmetric meeting stalls.
Section 15 was added by issue #28: when an encounter has passed, which is when a
directive's `speed_scale`, and everything a rule told a pair, stops applying.
Section 16 was added by issue #30: pair exposure, the conflict measure of a pair, and why
it does not depend on the responsibility shares.
Sections 17 and 18 were added by issue #32: what happens when two agents meet *inside* a
single-file passage (the arbiter's own way, and the back-up manoeuvre that a `back_up`
directive starts), and which of the two it is best to back out.
There `orca:LINE` points into `refs/si1_orca_vandenberg2011.txt`, and the notation is that
of `orca.md`, section 3.

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

## 9. Responsibility shares, and the reciprocity condition

ORCA has each agent of a pair make up half of the change `u` in relative velocity that is
needed (`orca.md`, section 3). A directive's `responsibility_share` replaces the half by a
number `α` in [0, 1]. This section finds what the two shares of a pair must satisfy.

**On a collision course.** The relative velocity `v = v_A - v_B` is inside the velocity
obstacle. `u` is the smallest change of `v` that takes it out, and `n` the outward normal
where it comes out, so `u = |u| n`. Give A the half-plane

    (v_A' - v_A) · n  >=  α_A |u|

and B, for whom everything is mirrored (`u` and `n` change sign),

    (v_B' - v_B) · (-n)  >=  α_B |u|

Subtracting the second from the first, the new relative velocity `v'` satisfies

    (v' - v) · n  >=  (α_A + α_B) |u|

The obstacle is convex and `n` is its outward normal at `v + u`, so every `v'` with
`(v' - v) · n >= |u|` is outside it. Hence:

> **If α_A + α_B >= 1, the pair has no collision for τ.** A changes its velocity by at
> least `α_A |u|` along `n`, B by at least `α_B |u|` the other way, the two together by at
> least `(α_A + α_B) |u|`, and `|u|` is enough.

That is the condition issue #26 states. If the sum is less than 1 the two together may
stop short of `|u|` and stay on a collision course.
*Tested:* `tests/test_orca.py::test_shares_that_sum_to_at_least_one_keep_a_pair_collision_free_for_tau`
(2,000 random configurations for each of 15 combinations of shares and sides) and
`::test_shares_that_sum_to_less_than_one_do_not`.

**Not on a collision course: the part the condition does not cover.** Now `v` is outside
the obstacle and `u` points *toward* it: `u = -|u| n`, and `|u|` is the room that is left.
The paper applies the same formula here (`orca:308`): each agent may move toward the
obstacle by half of the room. If the share simply replaced the half, A could use
`α_A |u|` of the room and B `α_B |u|`, and with `α_A + α_B > 1` the two together could use
more room than there is. A pair with shares (1, 1), which is safe on a collision course,
would be able to steer itself onto one. Standard ORCA never meets this, because its
shares sum to exactly 1.

So the share cannot multiply `u` in both cases.

**DD29 (decision). The share divides the avoidance, and the room is always split in
half.** In code (`orca.py`, `_half_plane`), with `m = u · n`:

    m > 0   (on a collision course):   (v_A' - v_A) · n  >=  α_A m
    m <= 0  (not on one):              (v_A' - v_A) · n  >=  m / 2

Outside the obstacle the two then use at most `|u|/2 + |u|/2 = |u|` whatever their shares,
and stay outside. The two cases meet at `m = 0`, so nothing jumps as a pair moves onto a
collision course. With `α = 1/2` both lines are the paper's. And a share has no effect at
all unless there is something to avoid.

Together with the box above: **shares that sum to at least 1 are sufficient in both
cases.**
*Tested:* `::test_outside_the_cone_the_room_is_split_in_half_whatever_the_share`,
`::test_using_the_room_that_is_left_never_puts_a_pair_on_a_collision_course` (shares (1, 1),
2,000 configurations).

(The alternative considered: give the agent with share `α` the fraction `1 - α` of the
room. It is also safe when the shares sum to at least 1. It was not chosen because an
agent with share 1 would then be forbidden to turn toward a neighbour at all, even one it
is nowhere near meeting.)

**What a share of 0 means.** On a collision course its half-plane is
`(v' - v) · n >= 0`: the agent need do nothing, but may not make things worse. An agent
walking at the velocity it wants is not affected at all, and is not counted as exposed
(`metrics.md`, section 3). That is the counterpart of the other agent's assumption: A,
with share 1, plans as if B's velocity will stay as it is.

**When a pair's shares sum to less than 1.** Each directive is given by its own provider,
so the two may not fit. The layer checks every pair that perceive each other
(`directives.py`, `resolve_pair`), and on a shortfall it logs a `reciprocity_violation`
and repairs the shares before they are used. **DD29, continued (decision): the repair is
proportional.** Both are scaled by `1 / (α_A + α_B)`, which keeps their ratio:
(0.2, 0.3) becomes (0.4, 0.6). If both are 0 there is no ratio to keep and each gets 1/2,
which is plain ORCA. `share_policy: equal_split` adds half of the shortfall to each
instead. A sum above 1 is left alone: taking more than one's share is safe.
*Tested:* `tests/test_directives.py`, `test_proportional_policy_keeps_the_ratio` and
those after it; `tests/test_avoidance_sim.py::test_shares_short_of_one_are_logged_once_and_repaired`.

## 10. Side preference

On a collision course `v` is inside the cone and can leave it across either leg. ORCA
takes the nearer (eq. 5). A `side_preference` of `left` or `right` takes that leg instead,
whichever is nearer: `u` becomes the vector from `v` to the foot of the perpendicular on
that leg's line, and `n` that leg's outward normal.

**It is safe.** A leg's line is tangent to the whole cone, cut off or not, so the
half-plane beyond it contains no point of the obstacle. This holds even where the foot of
the perpendicular falls short of the arc.

**It is reciprocal if both use the same side.** "Left" is as each agent sees it, looking
at the other. B's obstacle is A's turned through a half turn, and a half turn keeps
handedness: A's left leg, turned, is B's left leg. So if both take `left`, B's `u` and `n`
are minus A's, the argument of section 9 goes through unchanged, and the pair is
collision-free for τ. Both keeping left means each steps to its own left and they pass
right shoulder to right shoulder.
*Tested:* `tests/test_orca.py::test_the_two_agents_of_a_pair_build_mirrored_half_planes`
(for no side, left and right);
`tests/test_avoidance_sim.py::test_side_preference_decides_the_side_the_two_pass_on`.

**It is not reciprocal if they differ.** With A on `left` and B on `right`, the two step
to the same side of the corridor, the relative velocity does not change, and they stay on
a collision course: the familiar sidewalk dance. Nothing in section 9 covers it.

**DD30 (decision). A pair has one side.** `resolve_pair` gives it:

| A says | B says | The pair uses |
|---|---|---|
| nothing | nothing | the nearer side: plain ORCA |
| a side | the same side | that side |
| a side | nothing | that side, for both |
| a side | the other side | the nearer side, and a `reciprocity_violation` is logged |

"Nothing" is read as having no preference, so the one stated preference stands for the
pair. This is the layer deciding with knowledge of both directives, as it does for the
shares. It models a convention, which only works if both follow it; a rule database that
every agent reads from will give both the same side.

**Only on a collision course.** A side preference does nothing while `v` is outside the
obstacle. Otherwise an agent already going by on the right would be told to cross over
and go by on the left. The preference picks between two ways out of a conflict; it does
not create one.
*Tested:* `tests/test_orca.py::test_a_side_preference_does_nothing_when_not_on_a_collision_course`.

Once the pair is out of the cone on the chosen side, plain ORCA keeps it there: the
nearest boundary point is then on that side. So the preference acts on the first step of
a conflict and its effect lasts.

## 11. Clearance margin and passage order

**Clearance.** A `clearance_margin` of `c` is used as a larger combined radius,
`r_A + r_B + c`: the obstacle grows and the two pass `c` further apart. The two agents of
a pair may ask for different margins. If each used its own, they would build obstacles of
different sizes, and the two half-planes would no longer be mirror images: A would rely on
B doing its share against an obstacle B is not using.

**DD31 (decision). The pair uses the larger of the two margins.** Each agent then gets at
least the space it asked for, both use the same obstacle, and section 9 applies as it
stands. Nothing is lost, so there is nothing to log.
*Tested:* `tests/test_avoidance_sim.py::test_clearance_margin_is_the_gap_the_two_keep`
(the smallest separation in a run equals the margin, for four margins),
`::test_the_larger_of_two_clearance_margins_is_kept_by_both`.

A collision is still judged on the bodies, without the margin (`metrics.md`, section 6).

**Passage order.** `passage_order` says who goes first through a single-file segment. It
is handed to the arbiter of issue #24 as its "agreed leader", the input it already has for
a negotiated agreement (`negsim/conflict/roles.py`, `decide_roles`).

| A says | B says | Leader handed to the arbiter |
|---|---|---|
| `leader` | `follower` or nothing | A |
| nothing | `follower` | A |
| `follower` | `leader` or nothing | B |
| nothing | `leader` | B |
| nothing | nothing | none: the arbiter's own rule decides |
| `leader` | `leader` | none, and a `reciprocity_violation` is logged |
| `follower` | `follower` | none, and a `reciprocity_violation` is logged |

*Tested:* `tests/test_directives.py::test_passage_orders_of_a_pair`.

## 12. Walls in discrete time

`orca.md`, section 5, gives the wall half-plane: with `q` the wall's nearest point to an
agent at `p` with radius `r`, and `e = (q - p) / |q - p|`,

    v · e  <=  (|q - p| - r) / τ_obst

**Where it comes from.** The wall's velocity obstacle (the paper's eq. 11) is the set of
velocities that bring the agent's disc onto the wall within `τ_obst`. Its point nearest
the origin of velocity space is `((|q - p| - r) / τ_obst) e`: the slowest way to reach the
wall in the time allowed is straight at its nearest point. The obstacle is convex, so the
tangent there is at right angles to `e`, and the half-plane on the origin's side of it is
the one above. The paper takes exactly that half-plane for a wall (`orca:577`).

**Claim.** An agent that obeys the half-plane at every step never touches a convex wall,
provided `τ_obst >= dt`.

**Proof.** Let `g = |q - p| - r` be the gap. The wall is convex and `q` is its nearest
point to `p`, so the whole wall lies on the far side of the line through `q` at right
angles to `e`. After a step the agent is at `p' = p + v dt`, and its distance to that line
is `|q - p| - v · e dt`, which is at least `|q - p| - g dt / τ_obst`. Its gap to the wall
is therefore at least

    g' >= g (1 - dt / τ_obst)

which is not negative when `dt <= τ_obst`, and is positive, by the same fraction of `g`
every step, when `dt < τ_obst`. ∎

The proof needs no assumption about the other half-planes, because the fallback never
relaxes a wall (`orca.md`, section 7). With a horizon shorter than the time step the bound
is too loose and an agent can step through a wall, so a scenario with
`time_horizon_obst < dt` is refused when it is loaded.
*Tested:* `tests/test_orca.py::test_obeying_the_wall_half_plane_never_reaches_the_wall`
(including the failure for a horizon shorter than the step); in every committed run and
every test run the number of agent-wall collisions is zero.

**Standing still is always allowed.** With `g >= 0` the right-hand side is not negative,
so `v = 0` satisfies every wall half-plane. The walls alone are never infeasible.

## 13. The conflict zone at a single-file segment

For the hallway of issue #24 the conflict zone of a pair is the stretch of each path that
comes within `r_i + r_j + margin` of the other's path (section 4). That zone is as long as
the two paths stay close, which in a corridor is most of the way. It suits a pair the
arbiter holds from the first step. It does not suit a pair that ORCA holds until the two
perceive each other: by then one of them may already be inside it. That happened in the
first version of the bottleneck scenario, and the run ended in a collision
(`WORK_LOG-26.md`).

For the avoidance layer the zone is therefore tied to the segment
(`coordination.py`, `SingleFileDetector`). On each agent's path it is the stretch inside
the segment, plus a run-out of length `c = r_i + r_j + margin` at each end.

**Claim.** If the two centres are never inside their zones at the same time, the two are
never both inside the segment, and an agent waiting at the edge of its zone is at least
`margin` clear of an agent at the mouth of the segment.

**Proof.** A centre inside the segment is inside its zone, so the first part is
immediate. For the second: the follower's centre is at least `c` along its path before
the mouth, and its path into the segment ends at the mouth, so, where that last stretch
of path is straight, it is at least `c` from the mouth and from the leader's centre
there. The bodies are then at least `c - r_i - r_j = margin` apart. ∎

That is all the zone guarantees. It says nothing about the two once the leader is out in
the wide part with the follower in front of it: there they have to pass each other, and
that is ORCA's job, not the arbiter's.

**DD32 (decision). ORCA is never switched off for a pair the arbiter holds.** While the
arbiter holds a pair the follower takes all of the avoidance and the leader none (shares 1
and 0, which sum to 1, so section 9 applies). The leader, which cannot step aside inside
the segment, is not slowed by a follower standing near its way out; the follower, which
has room, gets out of the way. The arbiter's speed bound caps what the follower *wants*,
so that it does not walk into the segment, and leaves its maximum speed alone, so that it
can still move aside.

This is a weaker statement than issue #24's, where the bound capped the speed itself. An
agent that ORCA moves is not on its path any more, and one that is pushed, by a third
agent in a crowd, could be moved past the edge of its zone. With two agents nothing pushes
the follower; the first test below checks, on the trajectory, that the two are never in
their zones at once.
*Tested:* `tests/test_avoidance_sim.py::test_the_follower_stays_out_of_the_segment_until_the_leader_has_left_it`,
`::test_the_leader_is_not_slowed_and_the_follower_does_the_avoiding`,
`::test_the_arbiters_speed_bound_caps_what_the_follower_wants_not_what_it_may_do`.

The follower's bound is section 2's, `d_in * v_leader / d_out`, with the zone above and
with the leader's *preferred* speed as `v_leader`. The arbiter was written for agents that
walk at their maximum speed; an ORCA agent walks at its preferred speed and reaches its
maximum only when dodging. So the arbiter is shown each agent with its preferred speed in
the place of the maximum (`coordination.py`, `_AgentView`). Section 6 covers the case of a
leader that turns out slower still.

## 14. A number to check: how long a symmetric meeting takes to stall

`orca.md`, section 6, argues that two agents exactly head-on only ever brake. The
argument gives a time, which can be set against a run.

Let `g` be the gap between the two bodies. On a step where the closing speed exceeds
`g / τ`, each agent gives up half of the excess, so the closing speed after the step is
exactly `g / τ`, and

    g_next = g (1 - dt / τ)

Braking starts on the first step at whose start `g` is below `2 v τ`, with `v` the walking
speed. From then on each agent's speed is `g / (2 τ)`.

For the shipped head-on scenario: `v = 1.3 m/s`, `τ = 3 s`, `dt = 0.1 s`, the two start
16 m apart with radius 0.25 m, so the gap starts at 15.5 m and, while both walk freely, is
`15.5 - 2.6 t`.

- Braking starts below a gap of `2 × 1.3 × 3 = 7.8 m`, which is crossed after
  `(15.5 - 7.8) / 2.6 = 2.96 s`. The state is only looked at every 0.1 s, so the first
  step that brakes is the one that begins at 3.0 s, where the gap is
  `15.5 - 2.6 × 3.0 = 7.7 m`. After `k` more steps the gap is `7.7 × (1 - 0.1/3)^k`.
- An agent's speed is below the yield threshold of 0.65 m/s (half of 1.3) once
  `g < 3.9 m`: from `k = 21`, at 5.1 s.
- It is below the deadlock threshold of 0.01 m/s once `g < 0.06 m`. That takes
  `ln(0.06 / 7.7) / ln(1 - 0.1/3) = 143.2` steps, so from `k = 144`, at 17.4 s.
- A deadlock is declared after 3 s below the threshold: **at 20.4 s**, `k = 174`, with a
  gap of `7.7 × (1 - 0.1/3)^174 = 0.0211 m`.

The committed run `runs/si1_head_on_side_preference/001_symmetric_plain` ends in a
deadlock at 20.4 s with a smallest separation of 0.021118 m, each agent exposed for
17.4 s (from 3.0 s to the end) and yielding for 15.3 s (from 5.1 s to the end). All four
numbers are the ones above.
*Tested:* the symmetry the argument rests on, in
`tests/test_avoidance_sim.py::test_an_exactly_symmetric_start_stays_exactly_symmetric_under_plain_orca`.
The time itself is a result, read from the run.

## 15. When an encounter has passed

Issue #26 had a directive's `speed_scale` hold while the neighbour stayed within the sensing
radius. At 12.5 m that is long after the encounter is over: in issue #26's run with a scale
of 0.6 the two walked slowly from 1.4 s to 17.5 s, though they had passed each other at
9.4 s. Issue #28 makes it stop when the encounter has passed, and has everything a rule
tells a pair stop then too, unless the rule says otherwise (`rule-format.md`, section 7).
**DD55 (decision, the issue's): the definition below, applied to `speed_scale` for every
provider and to every field of a rule match.**

**Setting.** Two agents A and B; `p = x_B - x_A` their relative position and
`v = v_B - v_A` their relative velocity. Then

    d/dt |p|² = 2 p · v

so the distance between them shrinks while `p · v < 0`, is smallest where `p · v = 0`
(their closest approach), and grows while `p · v > 0`.

**Definition.** The encounter of A and B **has passed** on the first step at whose start

1. they are separating: `p · v > 0`, and
2. they are clear of each other: `|p| > r_A + r_B + c`, with `c` the pair's clearance
   margin (the larger of the two agents' margins, DD31);

or, whichever comes first, the neighbour leaves the sensing radius or the pair interaction
ends for another reason. "The separation exceeds the summed radii plus any clearance
margin", in the issue's words, is read as the distance between the two centres.

**Why both conditions.** (1) alone would end a directive while two bodies still touch:
ORCA pushes two overlapping discs apart (`orca.md`, section 7), and they separate while
still in contact. (2) alone would end it at the start of every encounter, when the two are
still far apart.

**Claim.** If the velocities stay as they are, two agents for which the encounter has
passed never come closer again.

**Proof.** With constant velocities, `p(t) = p_0 + v (t - t_0)` and

    |p(t)|² = |p_0|² + 2 (p_0 · v)(t - t_0) + |v|² (t - t_0)²

With `p_0 · v > 0` both terms after the first are positive for every `t > t_0`, so
`|p(t)| > |p_0|`, which already exceeds `r_A + r_B + c`. ∎

**In discrete time.** The state is read at the start of each step, with the velocities
realised on the step before, as perception reads it. So "passed" is first true on the
first step that starts after the distance has begun to grow: no later than one step after
closest approach, and never before it.

**What it does not guarantee.** Velocities do not stay constant: ORCA, the path and other
agents change them, and two agents that have passed can approach again (one turning back,
or jostling in a crowd). For a rule, a genuinely new encounter is matched afresh once the
pair's encounter class has changed (`rule-matching.md`, section 3); the hysteresis there is
what keeps a jostle from re-arming a rule. A static directive's `speed_scale`, once expired,
stays expired for the rest of the interaction.

**The effect.** In issue #26's two runs with a scale of 0.6 (`both_left_slow`), the
makespan goes from 18.7 s and 18.6 s to 15.4 s, and the conflict exposure stays 6.6 s: the
encounter is the same, only the slow walk after it is gone. The other 44 runs of issue #26
reproduce exactly (`WORK_LOG-28.md`).

*Tested:* `tests/test_rules_matching.py::test_passed_means_separating_and_clear`
(abreast is not passed, one step past is, a clearance margin delays it, still approaching
is not), `::test_a_rules_speed_scale_applies_until_closest_approach_and_not_after`,
`::test_a_match_expires_when_the_encounter_has_passed_and_every_field_reverts`;
`tests/test_avoidance_sim.py::test_speed_scale_slows_the_agent_only_until_the_encounter_has_passed`.

## 16. Pair exposure, and why it does not depend on the shares (issue #30)

Issue #30 defines a conflict for a *pair* (`metrics.md`, section 11): the pair is exposed on
a step if the two intended velocities put it inside the two bodies' truncated velocity
obstacle. This section shows what the measure reads, why the responsibility shares are not
among it, what that does and does not imply for whole runs, and why the tolerance is what
it is. The notation is `orca.md`'s, section 3.

**The intended velocity.** On step `k` the run loop (`simulation.py`, step 4) gives every
agent `A` that has not arrived

    v̂_A = s_A · d_A + δ_A,        s_A = min(b_A, min(σ_A · v_A^pref, v_A^max))

with `d_A` the unit vector from `A`'s position toward the point `navigation.lookahead`
metres further along its path, `v_A^pref` and `v_A^max` its preferred and maximum speeds,
`σ_A` the smallest `speed_scale` of its unexpired directives toward the neighbours it
perceives, `b_A` the arbiter's bound if the arbiter holds `A` (no bound otherwise), and
`δ_A` the baseline's perturbation draw. What goes in: positions, paths, speeds, the
`speed_scale` fields, the arbiter's bound (which reads positions, preferred speeds, and the
leader named by the `passage_order` fields), and the perturbation stream.

**Where the shares enter.** In exactly two places, both after every `v̂` of the step is
fixed: `resolve_pair` combines the two directives of a pair into its shares, and the share
is handed to `agent_half_plane`, which offsets the agent's half-plane (section 9). The
half-planes go to the linear program, whose answer is the velocity the agent *moves* at.
The shares never reach `v̂`.

**The measure.** With `p = x_j − x_i`, `w = v̂_i − v̂_j` and `R = r_i + r_j`, the pair is
exposed on step `k` if

    |p| ≤ R    or    depth_τ(p, w, R) > ε

where `depth_τ` is the signed distance from `w` to the boundary of the truncated obstacle
VO^τ (positive inside), computed with ORCA's own geometry (`exposure.py` calls
`agent_half_plane` with no share, side or clearance and reads its `margin`), and
`τ = max(τ_i, τ_j)`. It is a function of `x_i, x_j, v̂_i, v̂_j, r_i, r_j, τ_i, τ_j` and `ε`.

**Claim 1.** On any given state, the pair exposure of the step does not depend on the
responsibility shares, nor on the sides or the clearance margins.
**Proof.** None of its arguments is a share, a side or a margin, and `v̂` is computed
before any of them is read. ∎

**What it does not say.** The shares do change the velocity the agents move at on a step
on which ORCA finds them on a collision course, and so where they are on every step after.
Two runs that differ only in their shares are therefore different runs from that step on,
and their total pair exposure can differ, because the states differ, not because the
measure reads the shares. Two consequences, each tested:

1. *Until the shares first act, the runs are the same.* A share or a side acts only on a
   collision course in ORCA's own sense (sections 9 and 10; off one, the room is split in
   half whatever the share, and the side does nothing). So two runs on the same seed that
   differ only in shares and sides are identical up to that step, and their first exposed
   step is the same.
   *Tested:* `tests/test_pair_exposure.py::test_a_side_and_shares_leave_the_first_exposed_step_as_it_was`.
2. *The same state gives the same answer under any shares.* One step taken from one state
   under shares (0.5, 0.5), (1, 0), (0, 1) and (0.8, 0.2) counts the same pair exposure,
   while the per-agent exposure of section 3 differs between them.
   *Tested:* `::test_one_state_gives_the_same_pair_exposure_under_any_shares`, and
   `::test_pair_exposure_can_be_recomputed_from_the_trajectory_alone`, which recomputes it
   from the positions and intended velocities in `trajectory.csv` with no directive at hand.

**The contrast with the per-agent measure.** Agent `A` is exposed (`metrics.md`, section 3)
if its intended velocity violates its own half-plane, which on a collision course is
`(v − (v_A + α_A |u| n)) · n ≥ 0`. For an agent walking as it intends (`v_A = v̂_A`) the
violation is `α_A |u|`: zero for a share of 0, positive otherwise. The per-agent measure
reads the share directly, on one and the same state.

**Symmetry.** Swapping the two agents maps `(p, w)` to `(−p, −w)`. Since
`|t(−w) − (−p)| = |t w − p|`, the obstacle of the swapped pair is the reflection of the
original through the origin, and `depth_τ` is unchanged: the measure is the pair's, not
either agent's.
*Tested:* `::test_the_measure_is_symmetric_in_the_two_agents`.

**The tolerance.** The obstacle is convex (section 9), so its signed distance function is
1-Lipschitz: moving `w` by `δ` moves the depth by at most `|δ|`. Outside the obstacle,
ORCA's `margin` is that distance (to the arc or a leg, whichever is nearer). The primary
baseline perturbs each intended velocity by at most 1e-4 m/s (`baseline.md`), so `w` by at
most 2e-4 m/s. A pair that is not on a collision course without the perturbation
(depth ≤ 0) therefore has a depth of at most 2e-4 m/s with it, below the default
`ε = 1e-3` m/s: **the perturbation alone never makes a step count**. (The one place
`margin` is not the exact distance is ORCA's tie between the legs, `orca.md`, section 4,
which lies inside the obstacle and on its axis exactly; a random perturbation lands there
with probability zero.) A depth of `ε` means that, had neither changed velocity, the two
bodies would have overlapped: on the axis, by about `ε τ` = 3 mm.
*Tested:* `::test_the_obstacle_depth_matches_hand_computed_cases`.

## 17. Meeting inside a single-file passage: the arbiter's way, and backing up (issue #32)

Two agents that meet *inside* a passage only one of them can use at a time cannot pass: one
has to back out. The arbiter normally keeps such a meeting from happening (the follower waits
at the mouth, section 13); this section is about a meeting it did not prevent, or that a
scenario starts with (`passage_meeting`, `parameters.md`). Section 17.1 is what the code did
before issue #32 added anything, as Part 2.1 of the issue asked; 17.2 and 17.3 are what
issue #32 added.

### 17.1 What the arbiter does

From the code (`coordination.py`, `control/strategy1.py`, `conflict/roles.py`,
`conflict/timing.py`), for two agents both inside a segment:

1. **Trigger.** The arbiter takes the pair on the first step on which the two perceive each
   other: a single-file segment lies on both paths, neither has cleared it, and their
   occupancy intervals of the conflict zone overlap. Both being inside, both intervals start
   at 0.
2. **Who goes first** (`decide_roles`). A leader the directives name, if there is one
   (`passage_order`, or since issue #32 `back_up`, which names the other); otherwise
   Strategy 1. Its first measure, the time to reach the zone, ties at 0; its second decides:
   the time to *clear* the zone going forward, `d_out / v`. At equal speeds the one that has
   walked further in is out sooner, and leads. An exact tie goes to the lower index (or a
   seeded draw).
3. **The follower** gets a speed bound of 0 (it is past the zone's entry and the leader has
   not cleared it): the speed it wants is 0. ORCA stays on, the follower taking all of the
   avoidance and the leader none (shares 1 and 0, DD32, section 13).
4. **Nobody decides to back up.** The arbiter has no backing of its own. What happens next
   depends on how the two meet:
   - **Walking into each other** (`start_speed: preferred`). The leader walks on at its full
     speed. In a passage too narrow to step aside, the only velocities ORCA allows the
     follower are backward ones, so it is pushed back at nearly the leader's speed until the
     leader has cleared the zone: issue #26's walking-backwards artefact (`metrics.md`,
     section 10), and counted as one. In `passage_meet_middle_v1` (1.7 m in each),
     unperturbed, the follower walks backwards for 2.5 s and 2.96 m, and the two are through
     at 12.3 s. A follower slower than the leader can push collides with it (the scratchpad
     measurement of `WORK_LOG-32.md`, 2026-10-16 20:40: a follower of 0.5 m/s, maximum
     0.8 m/s, hit at 0.3 s).
   - **At rest, face to face** (the passage scenarios' default start). The arbiter does not
     get them through. A leader with share 0 may not close in faster than its own velocity
     already does (its half-plane passes through its current velocity, section 9), and a
     follower standing in front of a standing leader is on no collision course, so nothing
     pushes it back. Unperturbed, the leader pushes the touching follower back at
     0.030 m/s for the whole 60 s of the run, which ends at its time limit with neither
     through (above the deadlock threshold of 0.01 m/s, so not declared a deadlock); under
     the primary baseline's perturbation the pair stalls, and the run ends in a deadlock
     at about 4 s.

So the arbiter's fallback gets the one that has walked less far in out of the way (at equal
speeds) only by an ORCA artefact, at a speed nobody chose, only while the follower can be
pushed faster than the leader advances, and only if the leader is already moving. There was
nothing in the arbiter to expose as a directive: `back_up` is new. The 20-seed numbers of
both starts are in `behaviour-checks.md`, section 6.
*Tested:* `tests/test_passage.py::test_intentional_backing_is_never_the_artefact_and_the_artefact_is_still_counted`
(the walking start).

### 17.2 The back-up manoeuvre

A `back_up` directive (`rule-format.md`, section 14) is carried out by the run loop
(`simulation.py`), not by ORCA and not by the arbiter.

**When it starts.** On the first step on which (a) the pair's combined directives name a
backer (exactly one of the two says `back_up: true`; two that do are a reciprocity violation,
and neither backs up, `directives.py`); (b) the backer is inside a single-file segment the
two meet in: one the scenario declares, narrower than the two diameters together, that both
their paths run through and that the other has not yet left, with the backer's centre inside
it and the other ahead of it along its path; and (c) neither is in another manoeuvre, and the
pair interaction has had none. (b) is read from the geometry alone, not from the perception
records, so that what the agents may see cannot change what a directive makes one of them do
(`_meeting_segment`). A `back_up` that does not meet (b) has no effect of its own, as a
`passage_order` has none in open space; before a segment it still names the other as the one
to go first, so the arbiter holds the one told to back up at the mouth.

**Backing.** The backer moves along the segment's long axis, away from the other, to a point
on the centre line beyond the end behind it by the run-out `c = r_i + r_j + margin` (the
segment's safety margin): the edge of the conflict zone of section 13, the first place along
the passage where its centre is out of the other's way. Its preferred velocity points at that
point at its **backing speed** (its agent type's `backing_speed`, 0.92 m/s if the type sets
none, never above its maximum speed; `parameters.md`), and never overshoots it. The backing
ends when its centre has reached the point along the axis (to within 1 mm).

**Waiting.** Its preferred velocity is 0 until the other has come out at that end and as far
beyond it (`c`), has arrived, or the two have lost sight of each other; then the backer goes
on along its own path, back into the segment. "As far beyond it" is measured as the arbiter's
conflict zone measures it (section 13): the other's progress along its own path past where its
path leaves the segment, at least `c`. Measured along the segment's axis with a 1 mm tolerance,
as at first, the manoeuvre could end a step before the zone was clear, and the arbiter then
held the pair for that one step: in a trial of the behaviour checks before the change, in 11 of
the 80 seed-rule runs with the slow backer, and in none of the 480 others.

**What each does meanwhile, with ORCA** (DD95). ORCA stays on for both:

| Phase | The backer | The other |
|---|---|---|
| backing | share 0: it is not pushed, and backs at its own backing speed | share 1: it does all of the avoiding, and its preferred speed is capped at the backer's backing speed, so that it comes on behind it at its pace |
| waiting | share 1: it keeps out of the other's way, as a follower of the arbiter does | share 0, at its own speed again |

The cap is part of the manoeuvre. Without it the other presses on at its own speed, and ORCA,
with share 0, does not let the backer slow down below the backward speed it already has while
the other closes in: a backer that was already being pushed back faster (the arbiter's way,
17.1) kept that speed, 1.27 m/s instead of its 0.92 m/s, in a measured run. With the cap the
backer backs at its backing speed and the two move as one. While it waits, the backer stands on
the centre line just outside the passage, where the other comes out, and ORCA moves it aside;
any backward motion that takes is ORCA's, not the directive's (17.3).

**The arbiter** (DD93). A pair in a manoeuvre is not the arbiter's: on the step the manoeuvre
starts, a pair the arbiter held is taken from it (a handoff `to: back_up`), and the arbiter
does not take it while the manoeuvre lasts. When the manoeuvre ends the other has cleared the
zone, so the conflict is no longer live and there is nothing for the arbiter to take.

**One at a time.** An agent is in at most one manoeuvre, as the backer or as the other, and a
pair interaction has at most one: a `back_up` that still holds after the other has cleared
does not start another. Three or more agents in a passage, and agents queued behind a backing
agent, are out of the scope of issue #32.

### 17.3 Intentional backing is not the artefact

Issue #26's diagnostic counts an agent that moves against the direction of its own path
faster than 0.1 m/s for at least 1 s (`metrics.md`, section 10). A backer in its backing phase
does exactly that, on purpose. The steps of the backing phase are therefore never counted
toward the artefact (DD98); they are the manoeuvre's, logged as `backing_time_s` and
`backing_distance_m` (how far it moved against the direction of its path while backing).
Every other backward step is counted as before, a waiting backer's included. Both distances
are reported, so that the total distance walked backwards can be read whole or apart.
*Tested:* `tests/test_passage.py` (the manoeuvre, its phases and speeds, the arbiter, the
visibility settings, the artefact, the logs) and `tests/test_directives.py` (the backer and
the leader of a pair).

## 18. Which of the two to back out (issue #32)

**Setting.** A passage of length `L`. Agent A has walked `x_A` into it from its end and B has
walked `x_B` from the other; they face each other. One of them backs out by the manoeuvre of
section 17: to the run-out `c` beyond its end, waits, and goes on along its path.

**Distance.** If B backs out, it walks `x_B + c` back and the same `x_B + c` forward again to
where it was; A walks no further than it would have. The extra walking is `2 (x_B + c)`; if A
backs out, `2 (x_A + c)`. `c` is the same for both (the two radii and the segment's margin),
so **the extra distance is least when the one that has walked less far in backs out**. Equal
distances are a tie, with nothing to choose between them. Backing out only to the end
(`c = 0`), as the issue states it, gives `2 x_B` against `2 x_A`: the same choice.

**Time.** The other cannot go on through until the backer is out, which takes
`(x + c) / v_back`, with `v_back` the backer's backing speed. The passage is free soonest when
the one with the smaller `(x + c) / v_back` backs out; with `c = 0`, the issue's criterion:
`x_A / v_back,A` against `x_B / v_back,B`. The two criteria agree when the backing speeds are
equal, and can differ when they are not: the one that has walked less far in may back out so
slowly that backing out the other frees the passage sooner.

In `passage_meet_with_speeds_v1`, A (agent 0) has walked `x_A = 2.0 m` and backs at 0.92 m/s,
B (agent 1) `x_B = 1.4 m` at 0.43 m/s, and `c = 0.6 m`. By distance, back out B: 4.0 m extra
against 5.2 m. By time, back out A: 2.6 / 0.92 = 2.8 s against 2.0 / 0.43 = 4.7 s (with
`c = 0`, 2.2 s against 3.3 s). Measured, unperturbed: backing A out takes 2.9 s and the two
are through at 13.6 s; backing B out takes 4.7 s and they are through at 16.7 s. The time to
completion adds the backer's walk back in and through the passage at its walking speed, which
here favours backing out the faster walker too. Over 20 perturbed seeds (`behaviour-checks.md`,
section 6, `time_optimal` against `seed_rule`): makespan 13.68 ± 0.11 s backing out A against
16.70 ± 0.11 s backing out B, from rest; 13.87 and 16.74 s when they meet walking.

**What a rule can say.** The distance criterion orders the two on one field both can see,
`agent.segment_distance_travelled`, and is the seed rule `passage_shorter_backs_out` (ties
within 0.1 m: `no_match`). The time criterion cannot be written: it needs each person's backing
speed, which nobody can see of another (a physical parameter, like the maximum speed;
`rule-format.md`, section 5), and the ratio of two values, which the format has no way to
state. The seed rule is a **test fixture, not a claim about how people choose** (its
provenance says so); which criterion people use, if either, is for the validation sub-issue
(SI-6).
*Tested:* `tests/test_passage.py::test_each_backs_at_its_own_backing_speed`,
`::test_backing_out_the_one_that_is_out_sooner_is_quicker_than_backing_out_the_one_that_walked_less`,
`::test_the_seed_rule_backs_out_the_one_that_has_walked_less_far_in`;
`tests/test_rules_schema_v3.py::test_the_seed_rule_matches_two_people_both_inside_and_no_one_else`.
