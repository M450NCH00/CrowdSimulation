"""One run of the avoidance layer: ORCA under directives, with the arbiter where only one fits.

Once per time step, for every agent that has not arrived:

1. **Perceive.** Find the agent's neighbours: the nearest ``max_neighbours`` agents no
   further away than its sensing radius. A neighbour that was not one on the step before
   starts an *interaction*: a perception record is built and the agent's directive
   provider is asked for a directive, which holds until the neighbour is out of range;
   its ``speed_scale`` only until the encounter has passed (issue #28).
   Two agents with an interaction open either way form a *pair interaction*
   (:class:`PairInteraction`), which is what rules are matched on and what is
   categorised as avoided, resolved or failed. A provider that follows pairs (the rule
   database, ``negsim.rules``) is shown every open pair on every step and may change the
   directives.
2. **Resolve.** Two agents that perceive each other each hold a directive about the
   other. The two are combined (``negsim.avoidance.directives.resolve_pair``); a pair that
   contradicts itself is logged as a reciprocity violation and repaired.
3. **Coordinate.** A pair with a single-file segment ahead of both is handed to the
   arbiter (``negsim.avoidance.coordination``), which decides who goes first and returns
   a speed bound for each. A pair one of whose agents is backing out of a segment on a
   ``back_up`` directive (issue #32) is not: the manoeuvre has it (below).
4. **Choose a velocity.** The preferred velocity points along the agent's desired path at
   its preferred speed, scaled by its directives and capped by the arbiter; a baseline
   may add a tiny random perturbation to it (:class:`Perturbation`). ORCA builds a
   half-plane for every wall in reach and every perceived neighbour, and the linear
   program picks the allowed velocity nearest the preferred one. In a pair the arbiter
   holds, the follower takes all of the avoidance and the leader none.
5. **Move.** All agents move at once, through the world's dynamics model.

Then the bookkeeping: arrivals, collisions, near misses, yields, deadlock. Between 4 and 5
every open pair is also tested for *pair exposure* (issue #30): whether the two intended
velocities of step 4, before ORCA's projection, put the pair on a collision course
(``negsim.avoidance.exposure``). It changes nothing the agents do; at the end of the run it
gives each pair interaction its severity tier (``docs/metrics.md``, section 11).

An agent that reaches the end of its path leaves the scene: it is no longer a neighbour
of anyone and cannot be collided with.

**Backing up** (issue #32; ``docs/derivations.md``, section 17). When a pair's directives tell
one agent to ``back_up`` and that agent is inside a single-file segment the two meet in (one
too narrow for them, on both their paths, with the other ahead of it), it starts a
*manoeuvre*, which runs to its end whatever the directive does meanwhile: it backs along the
segment, away from the other, at its own backing speed, to a point beyond the end behind it by
the two radii and the segment's safety margin (outside the conflict zone); it waits there; and
once the other has come out at that end and as far again (along its own path, as the arbiter's
conflict zone counts it), or has arrived, or the two have lost sight of each other, it goes on
along its path. While it backs out, the other comes on no
faster than the backer backs, and does all of the avoiding (shares 0 and 1); while it waits,
it keeps out of the other's way (1 and 0, as a follower of the arbiter does). The arbiter does
not hold the pair meanwhile. The backing is *intentional*, logged as such, and is never
counted as issue #26's walking-backwards artefact; anything ORCA does to the waiting agent is
ORCA's, and is. One manoeuvre per agent at a time, and one per pair interaction.

**Plans** (issue #59). An optional plan driver (``PlanDriver``, in the Step 1 package of track #55) may set
the preferred velocity of an encounter's agents in step 4, and in ``plan_only`` leave out the
half-plane between the two. Without one, every step runs exactly as before.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping, Optional

from ..conflict.roles import RoleSource
from ..control.strategy1 import AgentDecision
from ..metrics.avoidance import (
    ArtefactThresholds,
    EpisodeTracker,
    ProximityEpisode,
    ProximityTracker,
    YieldEvent,
    YieldTracker,
    severity_tier,
)
from ..metrics.compute import DeadlockMonitor
from .coordination import (
    FOLLOWER_SHARE,
    LEADER_SHARE,
    TO_ARBITER,
    ArbitrationSettings,
    Coordinator,
    Handoff,
)
from .directives import (
    POLICY_PROPORTIONAL,
    SIDE_NONE,
    AvoidanceDirective,
    DirectiveProvider,
    NullProvider,
    PairResolution,
    resolve_pair,
)
from .exposure import pair_exposed
from .lp import solve, violation
from .neighbours import SpatialGrid
from .orca import agent_half_plane, wall_half_plane
from .perception import (
    PairFeatures,
    PerceptionRecord,
    default_visibility,
    encounter_of,
    pair_features,
    perceive,
    segment_position,
)

if TYPE_CHECKING:  # pragma: no cover - the scenario layer imports this package
    from ..scenarios.crowd_base import CrowdScenarioSpec

Pair = tuple[int, int]

STATUS_COMPLETED = "completed"
STATUS_COLLISION = "collision"
STATUS_DEADLOCK = "deadlock"
STATUS_TIMEOUT = "timeout"

MODE_ORCA, MODE_ARBITER, MODE_BACK_UP = "orca", "arbiter", "back_up"
#: An agent carrying out an LLM agent's plan (issue #59; the plan executor of track #55).
MODE_PLAN = "plan"

# A back-up manoeuvre (issue #32): the phases of the one backing up, what the other is doing
# meanwhile (the trajectory's ``back_up`` column), and why it ended.
PHASE_BACKING, PHASE_WAITING = "backing", "waiting"
PHASE_PROCEEDING = "proceeding"
BACK_UP_CLEARED = "other_cleared"  # the other came out at the backer's end, and as far beyond it along its path
BACK_UP_OTHER_ARRIVED = "other_arrived"
BACK_UP_PAIR_ENDED = "pair_ended"  # the two lost sight of each other
BACK_UP_RUN_ENDED = "run_ended"
BACK_UP_END_REASONS = (BACK_UP_CLEARED, BACK_UP_OTHER_ARRIVED, BACK_UP_PAIR_ENDED, BACK_UP_RUN_ENDED)
#: How near the point it backs to (along the segment) an agent must be to be out (m).
BACK_UP_REACHED_M = 1e-3
#: The shares of a pair in a manoeuvre, (the one backing up, the other): while it backs out it is
#: not pushed and the other follows at its pace; while it waits it keeps out of the other's way.
BACKING_SHARES, WAITING_SHARES = (0.0, 1.0), (1.0, 0.0)

END_OUT_OF_RANGE = "out_of_range"
END_OBSERVER_ARRIVED = "observer_arrived"
END_NEIGHBOUR_ARRIVED = "neighbour_arrived"
END_RUN_ENDED = "run_ended"

_CONTACT_EPS = 1e-9
#: A velocity counts as altered by ORCA if it differs from the preferred one by more than this.
ALTERED_EPS = 1e-9


@dataclass
class Interaction:
    """One agent's dealings with one neighbour, from entering its sensing radius to leaving it."""

    interaction_id: int
    observer_id: int
    neighbour_id: int
    start_step: int
    start_time_s: float
    record: PerceptionRecord
    directive: AvoidanceDirective
    end_step: Optional[int] = None
    end_time_s: Optional[float] = None
    end_reason: Optional[str] = None
    perceived_steps: int = 0
    exposure_steps: int = 0
    arbiter_steps: int = 0
    min_separation_m: float = math.inf
    #: What was actually used, each time it changed: the pair's resolution when both
    #: perceive each other, the agent's own directive when only it perceives the other.
    effective: list[dict[str, Any]] = field(default_factory=list)
    _last_effective: Optional[tuple] = None
    _initial: Optional[AvoidanceDirective] = None
    #: Each later change of the directive by a provider that follows pairs (issue #28).
    directive_changes: list[dict[str, Any]] = field(default_factory=list)
    #: When the directive's ``speed_scale`` stopped applying because the encounter had
    #: passed (issue #28, Part 5). Only for a provider that does not follow pairs; one
    #: that does replaces the whole directive itself.
    speed_scale_expired_step: Optional[int] = None
    speed_scale_expired_time_s: Optional[float] = None

    def note_effective(self, step: int, mutual: bool, share: float, side: Optional[str], margin: float) -> None:
        key = (mutual, share, side, margin)
        if key != self._last_effective:
            self._last_effective = key
            self.effective.append(
                {
                    "from_step": step,
                    "mutual": mutual,
                    "responsibility_share": share,
                    "side_preference": SIDE_NONE if side is None else side,
                    "clearance_margin": margin,
                }
            )

    def as_dict(self, dt: float) -> dict[str, Any]:
        separation = None if math.isinf(self.min_separation_m) else round(self.min_separation_m, 6)
        return {
            "interaction_id": self.interaction_id,
            "observer_id": self.observer_id,
            "neighbour_id": self.neighbour_id,
            "start_step": self.start_step,
            "start_time_s": round(self.start_time_s, 6),
            "end_step": self.end_step,
            "end_time_s": None if self.end_time_s is None else round(self.end_time_s, 6),
            "end_reason": self.end_reason,
            "perception": self.record.as_dict(),
            "directive": self.initial_directive.as_dict(),
            "directive_changes": list(self.directive_changes),
            "speed_scale_expired_step": self.speed_scale_expired_step,
            "speed_scale_expired_time_s": None
            if self.speed_scale_expired_time_s is None
            else round(self.speed_scale_expired_time_s, 6),
            "effective": list(self.effective),
            "perceived_time_s": round(self.perceived_steps * dt, 6),
            "conflict_exposure_time_s": round(self.exposure_steps * dt, 6),
            "arbiter_time_s": round(self.arbiter_steps * dt, 6),
            "min_separation_m": separation,
        }

    @property
    def initial_directive(self) -> AvoidanceDirective:
        """The directive the provider gave when the interaction began."""
        return self._initial if self._initial is not None else self.directive

    def change_directive(self, directive: AvoidanceDirective, step: int, time_s: float) -> bool:
        """Replace the directive; False if it is the same one."""
        if directive == self.directive:
            return False
        if self._initial is None:
            self._initial = self.directive
        self.directive = directive
        self.directive_changes.append({"from_step": step, "from_time_s": round(time_s, 6), **directive.as_dict()})
        return True


@dataclass
class BackUp:
    """One agent backing out of a single-file segment for another (issue #32).

    ``axis`` is the segment's long axis (0 for x, 1 for y) and ``direction`` the way along it
    the agent backs, away from the other (+1 or -1). ``end_m`` is where along the axis the
    segment's end behind the agent is, and ``target`` the point it backs to: ``runout_m``
    beyond that end, on the segment's centre line.
    """

    backer: int
    other: int
    pair_id: int
    segment: str
    axis: int
    direction: float
    end_m: float
    target: tuple[float, float]
    runout_m: float
    speed_mps: float
    travelled_m: Optional[float]
    start_step: int
    start_time_s: float
    phase: str = PHASE_BACKING
    out_step: Optional[int] = None
    out_time_s: Optional[float] = None
    end_step: Optional[int] = None
    end_time_s: Optional[float] = None
    end_reason: Optional[str] = None
    backing_steps: int = 0
    waiting_steps: int = 0
    #: How far it moved back, against the direction of its path, while backing out.
    backing_distance_m: float = 0.0

    def shares(self, agent_id: int) -> float:
        """The responsibility share of ``agent_id`` toward the other agent of the manoeuvre."""
        shares = BACKING_SHARES if self.phase == PHASE_BACKING else WAITING_SHARES
        return shares[0] if agent_id == self.backer else shares[1]

    def as_dict(self, dt: float) -> dict[str, Any]:
        return {
            "backer": self.backer,
            "other": self.other,
            "pair_id": self.pair_id,
            "segment": self.segment,
            "travelled_m": None if self.travelled_m is None else round(self.travelled_m, 6),
            "speed_mps": round(self.speed_mps, 6),
            "runout_m": round(self.runout_m, 6),
            "target_m": [round(self.target[0], 6), round(self.target[1], 6)],
            "start_step": self.start_step,
            "start_time_s": round(self.start_time_s, 6),
            "out_step": self.out_step,
            "out_time_s": None if self.out_time_s is None else round(self.out_time_s, 6),
            "end_step": self.end_step,
            "end_time_s": None if self.end_time_s is None else round(self.end_time_s, 6),
            "end_reason": self.end_reason,
            "backing_time_s": round(self.backing_steps * dt, 6),
            "waiting_time_s": round(self.waiting_steps * dt, 6),
            "backing_distance_m": round(self.backing_distance_m, 6),
        }


PAIR_END_OUT_OF_RANGE = "out_of_range"
PAIR_END_AGENT_ARRIVED = "agent_arrived"
PAIR_END_RUN_ENDED = "run_ended"

# How a pair interaction ended up (``docs/metrics.md``, section 9).
OUTCOME_AVOIDED = "avoided"
OUTCOME_RESOLVED = "resolved"
OUTCOME_FAILED = "failed"
INTERACTION_OUTCOMES = (OUTCOME_AVOIDED, OUTCOME_RESOLVED, OUTCOME_FAILED)


@dataclass
class PairInteraction:
    """Two agents, from the first step on which either perceives the other to the first on
    which neither does, one of them has arrived, or the run has ended.

    This is the unit rules are matched on, and the unit whose outcome is categorised as
    ``avoided``, ``resolved`` or ``failed`` (``docs/metrics.md``, section 9). It exists in
    every avoidance run, with any provider. Since issue #30 it also counts the pair's own
    exposure and gets a severity tier, T0 to T4 (``docs/metrics.md``, section 11).
    """

    pair_id: int
    agents: tuple[int, int]
    start_step: int
    start_time_s: float
    encounter_class_at_start: Optional[str] = None
    end_step: Optional[int] = None
    end_time_s: Optional[float] = None
    end_reason: Optional[str] = None
    #: The first step on which the encounter had passed: separating, and clear of each
    #: other by more than the pair's clearance margin.
    passed_step: Optional[int] = None
    passed_time_s: Optional[float] = None
    exposure_steps: dict[int, int] = field(default_factory=dict)
    #: Steps on which the two intended velocities put the pair on a collision course
    #: (issue #30); the first of them.
    pair_exposure_steps: int = 0
    first_pair_exposed_step: Optional[int] = None
    min_separation_m: float = math.inf
    outcome: Optional[str] = None
    outcome_detail: dict[str, Any] = field(default_factory=dict)
    severity_tier: Optional[str] = None
    tier_detail: dict[str, Any] = field(default_factory=dict)
    #: What the directive provider recorded about the pair, if it follows pairs.
    provider_record: Any = None

    def as_dict(self, dt: float) -> dict[str, Any]:
        separation = None if math.isinf(self.min_separation_m) else round(self.min_separation_m, 6)
        record = self.provider_record
        return {
            "pair_id": self.pair_id,
            "agents": list(self.agents),
            "start_step": self.start_step,
            "start_time_s": round(self.start_time_s, 6),
            "encounter_class_at_start": self.encounter_class_at_start,
            "end_step": self.end_step,
            "end_time_s": None if self.end_time_s is None else round(self.end_time_s, 6),
            "end_reason": self.end_reason,
            "passed_step": self.passed_step,
            "passed_time_s": None if self.passed_time_s is None else round(self.passed_time_s, 6),
            "conflict_exposure_time_s": {
                str(agent): round(self.exposure_steps.get(agent, 0) * dt, 6) for agent in self.agents
            },
            "pair_exposure_time_s": round(self.pair_exposure_steps * dt, 6),
            "first_pair_exposed_step": self.first_pair_exposed_step,
            "min_separation_m": separation,
            "outcome": self.outcome,
            "outcome_detail": dict(self.outcome_detail),
            "severity_tier": self.severity_tier,
            "tier_detail": dict(self.tier_detail),
            "rules": None if record is None else record.as_dict(),
        }


@dataclass
class AgentStats:
    interactions: int = 0
    interaction_steps: int = 0
    exposure_steps: int = 0
    altered_steps: int = 0
    fallback_steps: int = 0
    one_sided_steps: int = 0
    arbiter_steps: int = 0
    distance_m: float = 0.0
    deviation_sum: float = 0.0
    deviation_max: float = 0.0
    samples: int = 0
    min_separation_m: float = math.inf
    min_wall_gap_m: float = math.inf


@dataclass
class SimulationResult:
    status: str
    steps: int
    sim_time_s: float
    collisions: dict[str, Any]
    deadlock: bool
    goal_times: dict[int, Optional[float]]
    stats: dict[int, AgentStats]
    yields: list[YieldEvent]
    near_misses: list[ProximityEpisode]
    collision_episodes: list[ProximityEpisode]
    wall_collision_episodes: list[dict[str, Any]]
    interactions: list[Interaction]
    violations: list[dict[str, Any]]
    handoffs: list[Handoff]
    trajectory: list[dict[str, Any]]
    steps_with_fallback: int
    segment_entry_times: dict[int, dict[int, float]]
    pairs: list[PairInteraction] = field(default_factory=list)
    provider_summary: Optional[dict[str, Any]] = None
    #: The counts of issue #26's two ORCA artefacts (``docs/metrics.md``, section 10).
    artefacts: Optional[dict[str, Any]] = None
    #: Every back-up manoeuvre, in the order they started (issue #32).
    back_ups: list[BackUp] = field(default_factory=list)
    #: When each agent's path left each single-file segment it runs through, at the far end
    #: (issue #32): by agent, then by segment index.
    segment_exit_times: dict[int, dict[int, float]] = field(default_factory=dict)

    @property
    def min_separation_m(self) -> Optional[float]:
        value = min((stats.min_separation_m for stats in self.stats.values()), default=math.inf)
        return None if math.isinf(value) else value


@dataclass(frozen=True)
class Perturbation:
    """A small random change to every preferred velocity, on every step, to break exact symmetry.

    Made as the RVO2 library's examples make it ("Perturb a little to avoid deadlocks due to
    perfect symmetry"): a vector whose direction is uniform on the circle and whose length
    is uniform on [0, ``magnitude_mps``], drawn anew for every agent on every step and added
    to its preferred velocity. ``docs/baseline.md`` gives the magnitude and the reasons. A
    magnitude of 0 is no perturbation.
    """

    magnitude_mps: float = 0.0

    def __post_init__(self) -> None:
        if not (math.isfinite(self.magnitude_mps) and self.magnitude_mps >= 0.0):
            raise ValueError(f"the perturbation's magnitude must be a number, 0 or more, got {self.magnitude_mps!r}")

    @property
    def active(self) -> bool:
        return self.magnitude_mps > 0.0

    def as_dict(self) -> dict[str, Any]:
        return {"kind": "rvo2_uniform", "magnitude_mps": self.magnitude_mps}


class AvoidanceSimulation:
    """Runs one avoidance scenario. Build it, then call :meth:`run` (or :meth:`step`)."""

    def __init__(
        self,
        spec: "CrowdScenarioSpec",
        provider: Optional[DirectiveProvider] = None,
        attributes: Optional[Mapping[int, Mapping[str, Any]]] = None,
        visibility: Optional[Mapping[str, bool]] = None,
        arbitration: Optional[ArbitrationSettings] = None,
        share_policy: str = POLICY_PROPORTIONAL,
        seed: int = 0,
        record_trajectory: bool = True,
        trajectory_stride: int = 1,
        perturbation: Optional[Perturbation] = None,
        plans: Optional[Any] = None,
        pairwise: Optional[Mapping[tuple[int, int], Mapping[str, Any]]] = None,
    ):
        self.spec = spec
        #: A plan driver (issue #59: ``PlanDriver``, the plan executor of track #55), or ``None``: then
        #: every step runs exactly as it did before plans existed.
        self.plans = plans
        self.world = spec.build_world()
        self.provider = provider or NullProvider()
        self.attributes = dict(attributes or {})
        #: Issue #108: each person's own view of another, by (observer, neighbour): whether they know
        #: them, whether they find them attractive. Only a version 4 rule's own-only condition reads it.
        self.pairwise = dict(pairwise or {})
        # Issue #108: a rule provider whose rules give plans brings a driver for them; it joins the
        # run's own driver, if any. A provider without one leaves every step as it was.
        steps = getattr(self.provider, "step_driver", None)
        if steps is not None:
            from ..rules.plans import Drivers

            self.plans = steps if plans is None else Drivers(plans, steps)
        if hasattr(self.provider, "pairwise"):
            self.provider.pairwise = self.pairwise
        self.visibility = dict(visibility) if visibility is not None else default_visibility()
        self.arbitration = arbitration or ArbitrationSettings()
        self.share_policy = share_policy
        self.record_trajectory = record_trajectory
        self.trajectory_stride = max(1, trajectory_stride)
        self.perturbation = perturbation or Perturbation()
        # A stream of its own, so that it does not share draws with the arbiter's tie-break.
        self._perturbation_rng = random.Random(f"perturbation:{seed}")

        agents = self.world.agents
        self.coordinator: Optional[Coordinator] = None
        if spec.single_file_segments and self.arbitration.enabled:
            self.coordinator = Coordinator(
                self.arbitration,
                spec.single_file_safety_margin,
                {a.agent_id: a.spec.single_file_stretches for a in agents},
                [segment.width for segment in spec.single_file_segments],
                seed,
            )

        self.grid = SpatialGrid(spec.cell_size)
        self.grid.rebuild((a.agent_id, a.pose.x, a.pose.y) for a in agents)
        self.max_radius = max(a.spec.radius for a in agents)
        self.environment_range = max(a.spec.sensing_radius for a in agents)

        self.open: dict[int, dict[int, Interaction]] = {a.agent_id: {} for a in agents}
        self.interactions: list[Interaction] = []
        self.pair_cache: dict[Pair, PairResolution] = {}
        self._features: dict[Pair, PairFeatures] = {}
        self._features_step = -1
        self.pairs: list[PairInteraction] = []
        self.open_pairs: dict[Pair, PairInteraction] = {}
        self.stats: dict[int, AgentStats] = {a.agent_id: AgentStats() for a in agents}
        thresholds = spec.thresholds
        self.yield_trackers = {
            a.agent_id: YieldTracker(
                a.agent_id, a.spec.preferred_speed, thresholds.yield_speed_fraction, thresholds.yield_min_duration
            )
            for a in agents
        }
        self.artefact_thresholds = ArtefactThresholds()
        self.backward = {a.agent_id: EpisodeTracker(self.artefact_thresholds.min_duration_s) for a in agents}
        self.hurried = {a.agent_id: EpisodeTracker(self.artefact_thresholds.min_duration_s) for a in agents}
        # Back-up manoeuvres (issue #32): all of them, those running by the agent backing up,
        # and the pair interactions that have had one.
        self.back_ups: list[BackUp] = []
        self.backing: dict[int, BackUp] = {}
        self._backed_pairs: set[int] = set()
        self.near_misses = ProximityTracker(thresholds.near_miss_distance)
        self.overlaps = ProximityTracker(-_CONTACT_EPS)
        self.wall_overlaps: dict[int, dict[str, Any]] = {}
        self.wall_collision_episodes: list[dict[str, Any]] = []
        self.first_collision_time: Optional[float] = None
        self.stop_on_collision = spec.on_collision == "stop"
        self.monitor = DeadlockMonitor(spec.deadlock.window_s, spec.deadlock.speed_eps)
        self.violations: list[dict[str, Any]] = []
        self.handoffs: list[Handoff] = []
        self.trajectory: list[dict[str, Any]] = []
        self.steps_with_fallback = 0
        #: Agents whose linear program was infeasible on the most recent step.
        self.fallback_agents: set[int] = set()
        self.segment_entry_times: dict[int, dict[int, float]] = {a.agent_id: {} for a in agents}
        self.segment_exit_times: dict[int, dict[int, float]] = {a.agent_id: {} for a in agents}
        self.status: Optional[str] = None
        self.deadlock = False

    # --- the run --------------------------------------------------------------------------------

    def run(self) -> SimulationResult:
        while self.status is None and self.world.step_index < self.spec.max_steps:
            self.step()
        return self.finish()

    def finish(self) -> SimulationResult:
        """Close everything still open and return the result. The run may have ended early."""
        world = self.world
        if self.status is None:
            self.status = STATUS_COMPLETED if world.all_done else STATUS_TIMEOUT
        if self.plans is not None:
            self.plans.finish(self)
        for mine in self.open.values():
            for interaction in list(mine.values()):
                self._end_interaction(interaction, END_RUN_ENDED)
        for key in sorted(self.open_pairs):
            self._close_pair(self.open_pairs.pop(key), PAIR_END_RUN_ENDED)
        for backer in sorted(self.backing):
            self._end_back_up(self.backing[backer], BACK_UP_RUN_ENDED)
        for tracker in [*self.yield_trackers.values(), *self.backward.values(), *self.hurried.values()]:
            tracker.close()
        self.near_misses.close()
        self.overlaps.close()
        for agent_id in sorted(self.wall_overlaps):
            self.wall_collision_episodes.append(self.wall_overlaps.pop(agent_id))
        yields = [event for tracker in self.yield_trackers.values() for event in tracker.events]
        for pair in self.pairs:
            self._categorise(pair, yields)
        if self.record_trajectory:
            for agent in world.agents:
                self.trajectory.append(self._final_row(agent))
        worst = [-episode.min_separation_m for episode in self.overlaps.events]
        worst += [episode["max_overlap_m"] for episode in self.wall_collision_episodes]
        collisions = {
            "agent_agent": len(self.overlaps.events),
            "agent_wall": len(self.wall_collision_episodes),
            "time_s": None if self.first_collision_time is None else round(self.first_collision_time, 4),
            "agents": sorted(
                {agent_id for episode in self.overlaps.events for agent_id in episode.pair}
                | {episode["agent_id"] for episode in self.wall_collision_episodes}
            ),
            "max_overlap_m": round(max(worst), 6) if worst else None,
        }
        return SimulationResult(
            status=self.status,
            steps=world.step_index,
            sim_time_s=world.time,
            collisions=collisions,
            deadlock=self.deadlock,
            goal_times={a.agent_id: a.goal_time for a in world.agents},
            stats=self.stats,
            yields=yields,
            near_misses=list(self.near_misses.events),
            collision_episodes=list(self.overlaps.events),
            wall_collision_episodes=list(self.wall_collision_episodes),
            interactions=self.interactions,
            violations=self.violations,
            handoffs=self.handoffs,
            trajectory=self.trajectory,
            steps_with_fallback=self.steps_with_fallback,
            segment_entry_times=self.segment_entry_times,
            segment_exit_times=self.segment_exit_times,
            pairs=self.pairs,
            provider_summary=self.provider.summary(),
            artefacts=self._artefacts(),
            back_ups=list(self.back_ups),
        )

    def _artefacts(self) -> dict[str, Any]:
        """Walking backwards and being hurried along, per agent and in total (``metrics.md``, section 10)."""
        agents = {}
        for agent_id in sorted(self.backward):
            backward, hurried = self.backward[agent_id], self.hurried[agent_id]
            agents[str(agent_id)] = {
                "backward_episodes": len(backward.episodes),
                "backward_time_s": round(backward.total_time_s, 6),
                "hurried_episodes": len(hurried.episodes),
                "hurried_time_s": round(hurried.total_time_s, 6),
                "backward_distance_m": round(backward.total_amount, 6),
            }
        totals = {
            name: (round(sum(entry[name] for entry in agents.values()), 6) if name.endswith(("_s", "_m")) else sum(entry[name] for entry in agents.values()))
            for name in ("backward_episodes", "backward_time_s", "hurried_episodes", "hurried_time_s", "backward_distance_m")
        }
        totals["agents_backward"] = sum(1 for entry in agents.values() if entry["backward_episodes"])
        totals["agents_hurried"] = sum(1 for entry in agents.values() if entry["hurried_episodes"])
        return {"thresholds": self.artefact_thresholds.as_dict(), "agents": agents, "totals": totals}

    def step(self) -> None:
        world, spec = self.world, self.spec
        agents = world.agents
        step, now, dt = world.step_index, world.time, world.dt
        active = [a for a in agents if a.goal_time is None]

        # 1. Perceive.
        neighbours: dict[int, list[tuple[float, int]]] = {}
        perceived: dict[int, set[int]] = {}
        for a in active:
            found = self.grid.nearest(a.agent_id, a.pose.x, a.pose.y, a.spec.sensing_radius, a.spec.max_neighbours)
            neighbours[a.agent_id] = found
            perceived[a.agent_id] = {other_id for _, other_id in found}
        self._update_interactions(active, neighbours, step, now)
        self._update_pairs(step, now)
        if self.provider.follows_pairs:
            # The provider sees every open pair and may change directives (issue #28).
            changes = self.provider.update(_StepView(self, step, now))
            for (observer, neighbour), directive in sorted(changes.items()):
                if self.open[observer][neighbour].change_directive(directive, step, now):
                    self.pair_cache.pop((observer, neighbour) if observer < neighbour else (neighbour, observer), None)

        # 2. Resolve the pairs that perceive each other.
        resolutions: dict[Pair, PairResolution] = {}
        for a in active:
            i = a.agent_id
            for j in perceived[i]:
                if i < j and i in perceived[j]:
                    resolutions[(i, j)] = self._resolution(i, j, step, now)

        # 2b. Back-up manoeuvres (issue #32): end those that are over, start new ones.
        self._update_back_ups(resolutions, step, now)
        manoeuvres = {(min(m.backer, m.other), max(m.backer, m.other)): m for m in self.backing.values()}
        proceeding = {m.other: m for m in self.backing.values()}

        # 3. Coordinate with the arbiter.
        travel_speed = {a.agent_id: self._travel_speed(a, perceived[a.agent_id]) for a in active}
        decisions: dict[int, AgentDecision] = {}
        roles: dict[Pair, tuple[int, int]] = {}
        held: set[Pair] = set()
        if self.coordinator is not None:
            leaders = {pair: resolutions[pair].leader for pair in resolutions if resolutions[pair].leader is not None}
            decisions, roles, handoffs = self.coordinator.step(world, travel_speed, resolutions, leaders, released=manoeuvres)
            self.handoffs.extend(handoffs)
            held = self.coordinator.arbitrated

        # 4. Choose a velocity for every agent, all from the same state of the world.
        driver = self.plans
        if driver is not None:
            driver.prepare(self)
        commands: dict[int, tuple[float, float]] = {}
        #: Each agent's intended velocity: what it hands ORCA, after its directives.
        intended: dict[int, tuple[float, float]] = {}
        rows: dict[int, dict[str, Any]] = {}
        #: For the artefact counts: the direction of the agent's path, the speed it wants,
        #: and whether a neighbour it perceives is behind it (``docs/metrics.md``, section 10).
        course: dict[int, tuple[float, float, float, bool]] = {}
        fallback_agents: set[int] = set()
        exposure_eps, tie_break = spec.thresholds.exposure_eps, spec.tie_break
        obstacles = world.obstacles
        recording = self.record_trajectory and step % self.trajectory_stride == 0
        for a in active:
            i, a_spec, stats = a.agent_id, a.spec, self.stats[a.agent_id]
            x, y = a.pose.x, a.pose.y
            own_velocity = a.velocity
            decision = decisions.get(i)
            speed, max_speed = travel_speed[i], a_spec.max_speed
            if decision is not None:
                # The arbiter's bound caps the speed the agent wants to walk at. Its
                # maximum speed is untouched, so that it can still get out of the way.
                speed = min(speed, decision.speed_bound)
            manoeuvre = self.backing.get(i)
            along = a_spec.path.heading_at(a.path_s)
            cx, cy = math.cos(along), math.sin(along)
            behind = any((agents[j].pose.x - x) * cx + (agents[j].pose.y - y) * cy < 0.0 for _, j in neighbours[i])
            phase = None
            override = None
            if driver is not None:
                override = driver.velocity(self, a, travel_speed[i], None if decision is None else decision.speed_bound)
            if override is not None:
                # Carrying out a plan (issue #59): the plan sets the preferred velocity.
                preferred = override
                speed = math.hypot(*preferred)
            elif manoeuvre is not None:
                # Backing out, at its own backing speed, or waiting.
                preferred = self._back_up_velocity(a, manoeuvre, dt)
                speed, phase = math.hypot(*preferred), manoeuvre.phase
            else:
                if i in proceeding:
                    # The other comes on no faster than the one backing out backs.
                    phase = PHASE_PROCEEDING
                    if proceeding[i].phase == PHASE_BACKING:
                        speed = min(speed, proceeding[i].speed_mps)
                preferred = self._preferred_velocity(a, speed)
            course[i] = (cx, cy, speed, behind)
            if self.perturbation.active:
                angle = self._perturbation_rng.random() * 2.0 * math.pi
                length = self._perturbation_rng.random() * self.perturbation.magnitude_mps
                preferred = (preferred[0] + length * math.cos(angle), preferred[1] + length * math.sin(angle))
            intended[i] = preferred

            lines = []
            for wall in obstacles:
                line = wall_half_plane((x, y), a_spec.radius, wall, a_spec.time_horizon_obst, a_spec.max_speed)
                if line is not None:
                    lines.append(line)
            n_hard = len(lines)

            mine = self.open[i]
            exposed = one_sided = under_arbiter = False
            for dist_sq, j in neighbours[i]:
                other = agents[j]
                interaction = mine[j]
                interaction.perceived_steps += 1
                separation = math.sqrt(dist_sq) - a_spec.radius - other.spec.radius
                if separation < interaction.min_separation_m:
                    interaction.min_separation_m = separation
                if separation < stats.min_separation_m:
                    stats.min_separation_m = separation

                pair = (i, j) if i < j else (j, i)
                pair_record = self.open_pairs[pair]
                if separation < pair_record.min_separation_m:
                    pair_record.min_separation_m = separation
                if driver is not None and driver.ignores(i, j):
                    continue  # plan_only (issue #59): ORCA does not steer the encounter's two apart
                resolution = resolutions.get(pair)
                if resolution is not None:
                    share, side, margin = resolution.share_of(i), resolution.side, resolution.clearance_margin
                else:
                    one_sided = True
                    directive = interaction.directive
                    share, margin = directive.responsibility_share, directive.clearance_margin
                    side = None if directive.side_preference == SIDE_NONE else directive.side_preference
                if pair in held:
                    under_arbiter = True
                    interaction.arbiter_steps += 1
                    if pair in roles:
                        # The one who waits keeps out of the way of the one who goes.
                        share = LEADER_SHARE if roles[pair][0] == i else FOLLOWER_SHARE
                elif pair in manoeuvres:
                    share = manoeuvres[pair].shares(i)
                interaction.note_effective(step, resolution is not None, share, side, margin)

                half_plane = agent_half_plane(
                    (other.pose.x - x, other.pose.y - y),
                    (own_velocity[0] - other.velocity[0], own_velocity[1] - other.velocity[1]),
                    own_velocity,
                    a_spec.radius + other.spec.radius + margin,
                    a_spec.time_horizon,
                    dt,
                    share,
                    side,
                    tie_break,
                )
                lines.append(half_plane.line)
                if violation(half_plane.line, preferred) > exposure_eps:
                    exposed = True
                    interaction.exposure_steps += 1
                    pair_record.exposure_steps[i] = pair_record.exposure_steps.get(i, 0) + 1

            result = solve(lines, n_hard, max_speed, preferred)
            velocity = result.velocity
            commands[i] = velocity

            stats.interaction_steps += 1 if neighbours[i] else 0
            stats.exposure_steps += exposed
            stats.one_sided_steps += one_sided
            stats.arbiter_steps += under_arbiter
            if not result.feasible:
                stats.fallback_steps += 1
                fallback_agents.add(i)
            if math.hypot(velocity[0] - preferred[0], velocity[1] - preferred[1]) > ALTERED_EPS:
                stats.altered_steps += 1
            if recording:
                rows[i] = self._row(
                    step, now, a, preferred, decision, under_arbiter, len(neighbours[i]),
                    travel_speed[i] / a_spec.preferred_speed, exposed, not result.feasible,
                    sorted(mine[j].interaction_id for _, j in neighbours[i]),
                    phase,
                    override is not None,
                )
        self.fallback_agents = fallback_agents
        self.steps_with_fallback += bool(fallback_agents)
        self._measure_pair_exposure(intended, step)

        # 5. Move.
        applied = world.step(commands)

        # Bookkeeping.
        end = world.time
        speeds = []
        for a in active:
            i, stats = a.agent_id, self.stats[a.agent_id]
            vx, vy = applied[i]
            speed = math.hypot(vx, vy)
            stats.distance_m += speed * dt
            deviation = a.spec.path.distance_to(a.pose.xy)
            stats.deviation_sum += deviation
            stats.samples += 1
            if deviation > stats.deviation_max:
                stats.deviation_max = deviation
            self.yield_trackers[i].update(now, end, speed)
            cx, cy, wanted, behind = course[i]
            limits = self.artefact_thresholds
            forward = vx * cx + vy * cy
            manoeuvre = self.backing.get(i)
            backing_out = manoeuvre is not None and manoeuvre.phase == PHASE_BACKING
            if manoeuvre is not None:
                # Intentional backing (issue #32) is the manoeuvre's, never the artefact's.
                if backing_out:
                    manoeuvre.backing_steps += 1
                    manoeuvre.backing_distance_m += max(0.0, -forward) * dt
                else:
                    manoeuvre.waiting_steps += 1
            # Backing up in a plan (issue #59) is intentional too.
            planned_back = driver is not None and driver.backing(i)
            walking_backwards = not backing_out and not planned_back and forward < -limits.backward_speed_mps
            self.backward[i].update(now, end, walking_backwards, -forward * dt if walking_backwards else 0.0)
            self.hurried[i].update(now, end, behind and speed > (1.0 + limits.hurried_fraction) * wanted)
            for index, entry_s, exit_s in a.spec.single_file_stretches:
                if index not in self.segment_entry_times[i] and a.path_s >= entry_s:
                    self.segment_entry_times[i][index] = end
                if index not in self.segment_exit_times[i] and a.path_s >= exit_s:
                    self.segment_exit_times[i][index] = end
            if recording:
                row = rows[i]
                row["vx_mps"], row["vy_mps"], row["speed_mps"] = round(vx, 6), round(vy, 6), round(speed, 6)
                self.trajectory.append(row)
            if a.goal_time is None:
                speeds.append(speed)
            else:
                self.yield_trackers[i].close()
                self.backward[i].close()
                self.hurried[i].close()
                for interaction in list(self.open[i].values()):
                    self._end_interaction(interaction, END_OBSERVER_ARRIVED)

        remaining = [a for a in active if a.goal_time is None]
        self.grid.rebuild((a.agent_id, a.pose.x, a.pose.y) for a in remaining)
        self._check_contacts(remaining, end)
        if self.status is None:
            if not remaining:
                self.status = STATUS_COMPLETED
            elif self.monitor.update(now, end, speeds):
                self.status, self.deadlock = STATUS_DEADLOCK, True
        if driver is not None:
            driver.after_step(self)

    # --- interactions ---------------------------------------------------------------------------

    def _update_interactions(self, active, neighbours, step: int, now: float) -> None:
        agents = self.world.agents
        for a in active:
            i = a.agent_id
            mine = self.open[i]
            if mine:
                radius_sq = a.spec.sensing_radius ** 2
                x, y = a.pose.x, a.pose.y
                for j, interaction in list(mine.items()):
                    other = agents[j]
                    if other.goal_time is not None:
                        self._end_interaction(interaction, END_NEIGHBOUR_ARRIVED)
                    elif (other.pose.x - x) ** 2 + (other.pose.y - y) ** 2 > radius_sq:
                        self._end_interaction(interaction, END_OUT_OF_RANGE)
            for _, j in neighbours[i]:
                if j not in mine:
                    self._start_interaction(a, agents[j], step, now)

    def pair_features(self, i: int, j: int) -> PairFeatures:
        """The pair-level fields of agents ``i`` and ``j`` on the current step, computed once.

        Both agents' perception records, and a rule provider's shared snapshot, take them
        from here, so the two agents of a pair always see the same values.
        """
        step = self.world.step_index
        if self._features_step != step:
            self._features, self._features_step = {}, step
        pair = (i, j) if i < j else (j, i)
        features = self._features.get(pair)
        if features is None:
            agents = self.world.agents
            features = pair_features(
                agents[pair[0]],
                agents[pair[1]],
                self.world.obstacles,
                self.visibility,
                self.attributes,
                self.environment_range,
                self.spec.single_file_segments,
            )
            self._features[pair] = features
        return features

    def _start_interaction(self, observer, neighbour, step: int, now: float) -> None:
        record = perceive(
            step,
            now,
            observer,
            neighbour,
            self.world.obstacles,
            self.visibility,
            self.attributes,
            observer.spec.preferred_speed,
            [(entry_s, exit_s) for _, entry_s, exit_s in observer.spec.single_file_stretches],
            self.environment_range,
            pair=self.pair_features(observer.agent_id, neighbour.agent_id),
        )
        directive = self.provider.directive(record)
        if not isinstance(directive, AvoidanceDirective):
            raise TypeError(
                f"directive provider {self.provider.name!r} returned {type(directive).__name__}, "
                "not an AvoidanceDirective"
            )
        interaction = Interaction(
            len(self.interactions), observer.agent_id, neighbour.agent_id, step, now, record, directive
        )
        self.interactions.append(interaction)
        self.open[observer.agent_id][neighbour.agent_id] = interaction
        self.stats[observer.agent_id].interactions += 1

    def _end_interaction(self, interaction: Interaction, reason: str) -> None:
        interaction.end_step, interaction.end_time_s = self.world.step_index, self.world.time
        interaction.end_reason = reason
        i, j = interaction.observer_id, interaction.neighbour_id
        self.open[i].pop(j, None)
        self.pair_cache.pop((i, j) if i < j else (j, i), None)

    # --- pair interactions (issue #28) ----------------------------------------------------------

    def _update_pairs(self, step: int, now: float) -> None:
        """Open and close the pair interactions, and note when each encounter has passed.

        A pair interaction is open while at least one of the two has an interaction open
        with the other. For a provider that does not follow pairs, this is also where a
        directive's ``speed_scale`` expires: on the first step on which the encounter has
        passed (``docs/derivations.md``, section 15).
        """
        agents = self.world.agents
        open_now: set[Pair] = set()
        for i, mine in self.open.items():
            for j in mine:
                open_now.add((i, j) if i < j else (j, i))
        for key in sorted(set(self.open_pairs) - open_now):
            arrived = agents[key[0]].goal_time is not None or agents[key[1]].goal_time is not None
            self._close_pair(self.open_pairs.pop(key), PAIR_END_AGENT_ARRIVED if arrived else PAIR_END_OUT_OF_RANGE)
        for key in sorted(open_now - set(self.open_pairs)):
            pair = PairInteraction(len(self.pairs), key, step, now)
            pair.encounter_class_at_start = self.pair_features(*key).encounter_class
            self.pairs.append(pair)
            self.open_pairs[key] = pair

        generic = not self.provider.follows_pairs
        for (i, j), pair in self.open_pairs.items():
            held = [self.open[o][n] for o, n in ((i, j), (j, i)) if n in self.open[o]]
            if not self._passed(i, j, max(interaction.directive.clearance_margin for interaction in held)):
                continue
            if pair.passed_step is None:
                pair.passed_step, pair.passed_time_s = step, now
            if generic:
                for interaction in held:
                    if interaction.speed_scale_expired_step is None and interaction.directive.speed_scale != 1.0:
                        interaction.speed_scale_expired_step = step
                        interaction.speed_scale_expired_time_s = now

    def _passed(self, i: int, j: int, clearance: float) -> bool:
        """Whether the encounter of agents ``i`` and ``j`` has passed, on the present state.

        The two are separating, ``p · v > 0`` with ``p`` and ``v`` their relative position
        and velocity (``d/dt |p|² = 2 p · v``, so closest approach is where ``p · v = 0``),
        and their centres are further apart than the two radii and ``clearance``.
        """
        a, b = self.world.agents[i], self.world.agents[j]
        px, py = b.pose.x - a.pose.x, b.pose.y - a.pose.y
        vx, vy = b.velocity[0] - a.velocity[0], b.velocity[1] - a.velocity[1]
        return px * vx + py * vy > 0.0 and math.hypot(px, py) > a.spec.radius + b.spec.radius + clearance

    def _measure_pair_exposure(self, intended: Mapping[int, tuple[float, float]], step: int) -> None:
        """Count the step for every open pair whose intended velocities are on a collision course.

        ``intended`` holds each active agent's velocity as handed to ORCA on this step, after
        its directives and before the projection. The obstacle is the two bodies' alone and
        the horizon the larger of the two agents' (``negsim.avoidance.exposure``); no
        directive is read, so the count is the same whatever the responsibility shares.
        """
        agents, eps = self.world.agents, self.spec.thresholds.pair_exposure_eps
        for (i, j), pair in self.open_pairs.items():
            if i not in intended or j not in intended:
                continue
            a, b = agents[i], agents[j]
            if pair_exposed(
                (a.pose.x, a.pose.y),
                (b.pose.x, b.pose.y),
                intended[i],
                intended[j],
                a.spec.radius + b.spec.radius,
                max(a.spec.time_horizon, b.spec.time_horizon),
                eps,
            ):
                pair.pair_exposure_steps += 1
                if pair.first_pair_exposed_step is None:
                    pair.first_pair_exposed_step = step

    def _close_pair(self, pair: PairInteraction, reason: str) -> None:
        pair.end_step, pair.end_time_s, pair.end_reason = self.world.step_index, self.world.time, reason
        if self.provider.follows_pairs:
            self.provider.close_pair(pair, pair.end_step, pair.end_time_s, reason)

    def _categorise(self, pair: PairInteraction, yields: list[YieldEvent]) -> None:
        """``avoided``, ``resolved`` or ``failed`` (``docs/metrics.md``, section 9), and the
        severity tier (section 11).

        ``failed``: the two collided while the pair was open, or the run ended in deadlock
        with it open. Otherwise ``resolved``: one of them was exposed to the other, or one
        of them yielded while the pair was open. Otherwise ``avoided``. The category keeps
        issue #28's definition, on the per-agent exposure; ``pair_exposed`` in the detail
        lets it be recomputed on the pair's own.

        The tier is the highest that applies: T4 failed, T3 a near miss between the two, T2 a
        yield of either, T1 pair exposure above the threshold, else T0. Events count if
        they overlap the pair interaction in time (DD58).
        """
        start, end = pair.start_time_s, pair.end_time_s

        def overlapping(episodes):
            return [
                episode for episode in episodes
                if tuple(sorted(episode.pair)) == pair.agents and episode.start_time_s <= end and episode.end_time_s >= start
            ]

        yielded = [
            event for event in yields
            if event.agent_id in pair.agents and event.start_time_s <= end and event.end_time_s >= start
        ]
        collided = overlapping(self.overlaps.events)
        near = overlapping(self.near_misses.events)
        deadlocked = self.deadlock and pair.end_reason == PAIR_END_RUN_ENDED
        exposed = any(steps > 0 for steps in pair.exposure_steps.values())
        if collided or deadlocked:
            pair.outcome = OUTCOME_FAILED
        elif exposed or yielded:
            pair.outcome = OUTCOME_RESOLVED
        else:
            pair.outcome = OUTCOME_AVOIDED
        pair.outcome_detail = {
            "exposed": exposed,
            "pair_exposed": pair.pair_exposure_steps > 0,
            "yield_events": len(yielded),
            "collisions": len(collided),
            "deadlock": deadlocked,
            "open_at_timeout": self.status == STATUS_TIMEOUT and pair.end_reason == PAIR_END_RUN_ENDED,
        }
        exposure_s = pair.pair_exposure_steps * self.world.dt
        pair.severity_tier = severity_tier(
            exposure_s, self.spec.thresholds.collision_course_min_s, len(yielded), len(near), len(collided), deadlocked
        )
        pair.tier_detail = {
            "pair_exposure_time_s": round(exposure_s, 6),
            "yield_events": len(yielded),
            "near_misses": len(near),
            "collisions": len(collided),
            "deadlock": deadlocked,
        }

    def _resolution(self, i: int, j: int, step: int, now: float) -> PairResolution:
        """The combined directives of a pair that perceive each other (``i < j``)."""
        pair = (i, j)
        resolution = self.pair_cache.get(pair)
        if resolution is None:
            resolution = resolve_pair(
                i, self.open[i][j].directive, j, self.open[j][i].directive, self.share_policy
            )
            self.pair_cache[pair] = resolution
            for item in resolution.violations:
                self.violations.append({"step": step, "time_s": round(now, 6), **item.as_dict()})
        return resolution

    # --- back-up manoeuvres (issue #32) ---------------------------------------------------------

    def _meeting_segment(self, backer: int, other: int) -> Optional[tuple[Any, float]]:
        """The single-file segment ``backer`` would back out of for ``other``, and the way it would
        back along the segment's long axis (+1 or -1, away from the other); ``None`` if none.

        A segment the scenario declares that is too narrow for the two to pass in, that both their
        paths run through and that the other has not yet left, with the backer's centre inside it
        and the other ahead of the backer along the backer's path: the two meet in it. Read from
        the geometry alone, so that what the agents may see (the run's visibility settings) cannot
        change what a directive makes one of them do.
        """
        agents = self.world.agents
        a, b = agents[backer], agents[other]
        heading = a.spec.path.heading_at(a.path_s)
        if (b.pose.x - a.pose.x) * math.cos(heading) + (b.pose.y - a.pose.y) * math.sin(heading) <= 0.0:
            return None  # the other is not ahead of it: no end is behind it to back out by
        diameters = 2.0 * (a.spec.radius + b.spec.radius)
        leaves = {index: exit_s for index, _, exit_s in b.spec.single_file_stretches}
        for index, _, _ in a.spec.single_file_stretches:
            segment = self.spec.single_file_segments[index]
            if index not in leaves or segment.width >= diameters or b.path_s >= leaves[index]:
                continue
            inside = segment_position(a.pose.xy, b.pose.xy, segment.rect)[0]
            rect = segment.rect
            axis = 0 if rect.xmax - rect.xmin >= rect.ymax - rect.ymin else 1
            mine, theirs = a.pose.xy[axis], b.pose.xy[axis]
            if inside and mine != theirs:
                return segment, (1.0 if mine > theirs else -1.0)
        return None

    def _update_back_ups(self, resolutions: Mapping[Pair, PairResolution], step: int, now: float) -> None:
        """End the manoeuvres that are over and move on those that are out; then start one for
        every pair whose directives tell an agent inside a single-file segment the two meet in to
        back up (:meth:`_meeting_segment`).

        Read from the state at the start of the step, as everything else is.
        """
        agents = self.world.agents
        for backer, manoeuvre in sorted(self.backing.items()):
            other = agents[manoeuvre.other]
            pair = (min(backer, manoeuvre.other), max(backer, manoeuvre.other))
            if other.goal_time is not None:
                self._end_back_up(manoeuvre, BACK_UP_OTHER_ARRIVED)
            elif pair not in self.open_pairs:
                self._end_back_up(manoeuvre, BACK_UP_PAIR_ENDED)
            elif other.path_s >= self._exit_along_path(other, manoeuvre.segment) + manoeuvre.runout_m:
                # Out of the conflict zone exactly as the arbiter counts it (SingleFileDetector:
                # its progress along its own path past the segment's end by the run-out), so
                # that the arbiter never finds the pair's conflict live as the manoeuvre ends.
                self._end_back_up(manoeuvre, BACK_UP_CLEARED)
            elif manoeuvre.phase == PHASE_BACKING:
                me = agents[backer].pose.xy[manoeuvre.axis]
                if manoeuvre.direction * (me - manoeuvre.target[manoeuvre.axis]) >= -BACK_UP_REACHED_M:
                    manoeuvre.phase, manoeuvre.out_step, manoeuvre.out_time_s = PHASE_WAITING, step, now
        busy = set(self.backing) | {manoeuvre.other for manoeuvre in self.backing.values()}
        for pair, resolution in sorted(resolutions.items()):
            backer = resolution.backer
            if backer is None:
                continue
            other = pair[1] if backer == pair[0] else pair[0]
            record = self.open_pairs.get(pair)
            if record is None or record.pair_id in self._backed_pairs or backer in busy or other in busy:
                continue
            found = self._meeting_segment(backer, other)
            if found is None:
                continue  # back_up acts only from inside a single-file segment the two meet in
            segment, direction = found
            rect = segment.rect
            axis = 0 if rect.xmax - rect.xmin >= rect.ymax - rect.ymin else 1
            low, high = (rect.xmin, rect.xmax) if axis == 0 else (rect.ymin, rect.ymax)
            end_m = high if direction > 0.0 else low
            runout = agents[backer].spec.radius + agents[other].spec.radius + self.spec.single_file_safety_margin
            middle = (rect.ymin + rect.ymax) / 2.0 if axis == 0 else (rect.xmin + rect.xmax) / 2.0
            reach = end_m + direction * runout
            manoeuvre = BackUp(
                backer=backer, other=other, pair_id=record.pair_id, segment=segment.name, axis=axis, direction=direction,
                end_m=end_m, target=(reach, middle) if axis == 0 else (middle, reach), runout_m=runout,
                speed_mps=agents[backer].spec.backing_speed_mps,
                travelled_m=segment_position(agents[backer].pose.xy, agents[other].pose.xy, rect)[1],
                start_step=step, start_time_s=now,
            )
            self.back_ups.append(manoeuvre)
            self.backing[backer] = manoeuvre
            self._backed_pairs.add(record.pair_id)
            busy.update((backer, other))

    def _exit_along_path(self, agent, segment: str) -> float:
        """Where ``agent``'s path leaves the single-file segment named ``segment`` (arc length)."""
        names = [item.name for item in self.spec.single_file_segments]
        return next(exit_s for index, _, exit_s in agent.spec.single_file_stretches if names[index] == segment)

    def _end_back_up(self, manoeuvre: BackUp, reason: str) -> None:
        manoeuvre.end_step, manoeuvre.end_time_s, manoeuvre.end_reason = self.world.step_index, self.world.time, reason
        self.backing.pop(manoeuvre.backer, None)

    def _back_up_velocity(self, agent, manoeuvre: BackUp, dt: float) -> tuple[float, float]:
        """Toward the point it backs to, at its backing speed, not past it; nothing while it waits."""
        if manoeuvre.phase != PHASE_BACKING:
            return (0.0, 0.0)
        dx, dy = manoeuvre.target[0] - agent.pose.x, manoeuvre.target[1] - agent.pose.y
        distance = math.hypot(dx, dy)
        if distance < 1e-9:
            return (0.0, 0.0)
        speed = min(manoeuvre.speed_mps, distance / dt)
        return (speed * dx / distance, speed * dy / distance)

    # --- motion ---------------------------------------------------------------------------------

    def _travel_speed(self, agent, perceived: set[int]) -> float:
        """The speed the agent would walk at if nothing were in its way.

        Its preferred speed, times the smallest ``speed_scale`` among the directives it
        holds toward the neighbours it perceives now and has not yet passed, and never
        above its maximum speed.
        """
        mine = self.open[agent.agent_id]
        scale = min(
            (mine[j].directive.speed_scale for j in perceived if mine[j].speed_scale_expired_step is None),
            default=1.0,
        )
        return min(agent.spec.preferred_speed * scale, agent.spec.max_speed)

    def _preferred_velocity(self, agent, speed: float) -> tuple[float, float]:
        """Toward a point ``lookahead`` metres further along the desired path, at ``speed``."""
        if speed <= 0.0:
            return (0.0, 0.0)
        path = agent.spec.path
        tx, ty = path.point_at(min(path.length, agent.path_s + self.spec.lookahead))
        dx, dy = tx - agent.pose.x, ty - agent.pose.y
        distance = math.hypot(dx, dy)
        if distance < 1e-9:
            heading = path.heading_at(agent.path_s)
            return (speed * math.cos(heading), speed * math.sin(heading))
        return (speed * dx / distance, speed * dy / distance)

    # --- collisions and near misses -------------------------------------------------------------

    def _check_contacts(self, remaining, time_s: float) -> None:
        agents = self.world.agents
        watch = self.near_misses.distance
        hits, near = {}, {}
        for i, j, dist_sq in self.grid.pairs_within(2.0 * self.max_radius + max(watch, 0.0)):
            separation = math.sqrt(dist_sq) - agents[i].spec.radius - agents[j].spec.radius
            if separation < -_CONTACT_EPS:
                hits[(i, j)] = separation
            if separation < watch:
                near[(i, j)] = separation
            for agent_id in (i, j):
                if separation < self.stats[agent_id].min_separation_m:
                    self.stats[agent_id].min_separation_m = separation
        self.near_misses.update(time_s, near)
        self.overlaps.update(time_s, hits)

        hit_walls = set()
        if self.world.obstacles:
            for a in remaining:
                gap = min(wall.distance_to(a.pose.xy) for wall in self.world.obstacles) - a.spec.radius
                stats = self.stats[a.agent_id]
                if gap < stats.min_wall_gap_m:
                    stats.min_wall_gap_m = gap
                if gap < -_CONTACT_EPS:
                    hit_walls.add(a.agent_id)
                    episode = self.wall_overlaps.setdefault(
                        a.agent_id,
                        {"agent_id": a.agent_id, "start_time_s": round(time_s, 6), "end_time_s": None, "max_overlap_m": 0.0},
                    )
                    episode["end_time_s"] = round(time_s, 6)
                    episode["max_overlap_m"] = round(max(episode["max_overlap_m"], -gap), 6)
        for agent_id in [agent_id for agent_id in self.wall_overlaps if agent_id not in hit_walls]:
            self.wall_collision_episodes.append(self.wall_overlaps.pop(agent_id))

        if hits or hit_walls:
            if self.first_collision_time is None:
                self.first_collision_time = time_s
            if self.stop_on_collision:
                self.status = STATUS_COLLISION

    # --- trajectory rows ------------------------------------------------------------------------

    @staticmethod
    def _row(step, now, agent, preferred, decision, under_arbiter, n_neighbours, speed_scale, exposed, fallback, ids, back_up=None, planned=False):
        role = None if decision is None or decision.role is None else decision.role.value
        source = None if decision is None or decision.role_source is None else decision.role_source.value
        return {
            "step": step,
            "time_s": round(now, 6),
            "agent_id": agent.agent_id,
            "x_m": round(agent.pose.x, 6),
            "y_m": round(agent.pose.y, 6),
            "theta_rad": round(agent.pose.theta, 6),
            "path_s_m": round(agent.path_s, 6),
            "vx_mps": None,
            "vy_mps": None,
            "speed_mps": None,
            "pref_vx_mps": round(preferred[0], 6),
            "pref_vy_mps": round(preferred[1], 6),
            "control_mode": MODE_PLAN if planned else MODE_BACK_UP if back_up is not None else MODE_ARBITER if under_arbiter else MODE_ORCA,
            "speed_bound_mps": None if decision is None else round(decision.speed_bound, 6),
            "role": role,
            "role_source": source,
            "in_conflict": None if decision is None else decision.in_conflict,
            "zone_d_in_m": None if decision is None or decision.zone_d_in is None else round(decision.zone_d_in, 6),
            "zone_d_out_m": None if decision is None or decision.zone_d_out is None else round(decision.zone_d_out, 6),
            "n_neighbours": n_neighbours,
            "speed_scale": round(speed_scale, 6),
            "exposed": exposed,
            "fallback": fallback,
            "interactions": ";".join(str(value) for value in ids),
            "back_up": back_up,
        }

    def _final_row(self, agent) -> dict[str, Any]:
        row = dict.fromkeys(
            (
                "vx_mps", "vy_mps", "speed_mps", "pref_vx_mps", "pref_vy_mps", "control_mode",
                "speed_bound_mps", "role", "role_source", "in_conflict", "zone_d_in_m", "zone_d_out_m",
                "n_neighbours", "speed_scale", "exposed", "fallback", "interactions", "back_up",
            )
        )
        row.update(
            {
                "step": self.world.step_index,
                "time_s": round(self.world.time, 6),
                "agent_id": agent.agent_id,
                "x_m": round(agent.pose.x, 6),
                "y_m": round(agent.pose.y, 6),
                "theta_rad": round(agent.pose.theta, 6),
                "path_s_m": round(agent.path_s, 6),
            }
        )
        return row


class _StepView:
    """What the run loop shows a provider that follows pairs on one step.

    The shape is ``negsim.rules.matching.StepView``. Everything is read from the state at
    the start of the step, the same state the perception records are built from.
    """

    def __init__(self, simulation: AvoidanceSimulation, step: int, time_s: float):
        self._simulation = simulation
        self.step, self.time_s = step, time_s
        self.visibility, self.attributes = simulation.visibility, simulation.attributes
        self.pairwise = simulation.pairwise
        self.pairs = [simulation.open_pairs[key] for key in sorted(simulation.open_pairs)]

    def agent(self, agent_id: int):
        return self._simulation.world.agents[agent_id]

    def directions(self, pair: PairInteraction) -> list[tuple[int, int]]:
        """The (observer, neighbour) of each interaction open between the two."""
        i, j = pair.agents
        opened = self._simulation.open
        return [(observer, neighbour) for observer, neighbour in ((i, j), (j, i)) if neighbour in opened[observer]]

    def current_directive(self, observer: int, neighbour: int) -> AvoidanceDirective:
        return self._simulation.open[observer][neighbour].directive

    def encounter_class(self, i: int, j: int) -> Optional[str]:
        segments = self._simulation.spec.single_file_segments
        return encounter_of(self.agent(i), self.agent(j), self.visibility, segments)[0]

    def features(self, i: int, j: int) -> PairFeatures:
        return self._simulation.pair_features(i, j)

    def passed(self, i: int, j: int, clearance: float) -> bool:
        return self._simulation._passed(i, j, clearance)


def role_source_counts(result: SimulationResult) -> dict[str, int]:
    """How many handoffs to the arbiter took their leader from each source."""
    counts = {source.value: 0 for source in RoleSource}
    for handoff in result.handoffs:
        if handoff.to == TO_ARBITER and handoff.role_source is not None:
            counts[handoff.role_source] += 1
    return counts
