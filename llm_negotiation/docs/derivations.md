# Derivations: how fast the follower may go, and how long the conflict region must be

This file derives the speed bound in `negsim/control/strategy1.py` and the conflict zone
in `negsim/conflict/zone.py`. Each result names the test that checks it. Paper locators
(`v1:LINE`) point into `refs/ln_gamechat_arxiv_v1.txt`.

Sections 1 to 8 are issue #24's. Sections 9 to 14 were added for the avoidance layer of
issue #26: what the directive fields do to ORCA's guarantee, the wall rule in discrete
time, the conflict zone at a single-file segment, and why a symmetric meeting stalls.
Section 15 was added by issue #28: when an encounter has passed, which is when a
directive's `speed_scale`, and everything a rule told a pair, stops applying.
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
