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
   a speed bound for each.
4. **Choose a velocity.** The preferred velocity points along the agent's desired path at
   its preferred speed, scaled by its directives and capped by the arbiter; a baseline
   may add a tiny random perturbation to it (:class:`Perturbation`). ORCA builds a
   half-plane for every wall in reach and every perceived neighbour, and the linear
   program picks the allowed velocity nearest the preferred one. In a pair the arbiter
   holds, the follower takes all of the avoidance and the leader none.
5. **Move.** All agents move at once, through the world's dynamics model.

Then the bookkeeping: arrivals, collisions, near misses, yields, deadlock.

An agent that reaches the end of its path leaves the scene: it is no longer a neighbour
of anyone and cannot be collided with.
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
)

if TYPE_CHECKING:  # pragma: no cover - the scenario layer imports this package
    from ..scenarios.crowd_base import CrowdScenarioSpec

Pair = tuple[int, int]

STATUS_COMPLETED = "completed"
STATUS_COLLISION = "collision"
STATUS_DEADLOCK = "deadlock"
STATUS_TIMEOUT = "timeout"

MODE_ORCA, MODE_ARBITER = "orca", "arbiter"

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
    every avoidance run, with any provider.
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
    min_separation_m: float = math.inf
    outcome: Optional[str] = None
    outcome_detail: dict[str, Any] = field(default_factory=dict)
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
            "min_separation_m": separation,
            "outcome": self.outcome,
            "outcome_detail": dict(self.outcome_detail),
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
    ):
        self.spec = spec
        self.world = spec.build_world()
        self.provider = provider or NullProvider()
        self.attributes = dict(attributes or {})
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
        for mine in self.open.values():
            for interaction in list(mine.values()):
                self._end_interaction(interaction, END_RUN_ENDED)
        for key in sorted(self.open_pairs):
            self._close_pair(self.open_pairs.pop(key), PAIR_END_RUN_ENDED)
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
            pairs=self.pairs,
            provider_summary=self.provider.summary(),
            artefacts=self._artefacts(),
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
            }
        totals = {
            name: (round(sum(entry[name] for entry in agents.values()), 6) if name.endswith("_s") else sum(entry[name] for entry in agents.values()))
            for name in ("backward_episodes", "backward_time_s", "hurried_episodes", "hurried_time_s")
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

        # 3. Coordinate with the arbiter.
        travel_speed = {a.agent_id: self._travel_speed(a, perceived[a.agent_id]) for a in active}
        decisions: dict[int, AgentDecision] = {}
        roles: dict[Pair, tuple[int, int]] = {}
        held: set[Pair] = set()
        if self.coordinator is not None:
            leaders = {pair: resolutions[pair].leader for pair in resolutions if resolutions[pair].leader is not None}
            decisions, roles, handoffs = self.coordinator.step(world, travel_speed, resolutions, leaders)
            self.handoffs.extend(handoffs)
            held = self.coordinator.arbitrated

        # 4. Choose a velocity for every agent, all from the same state of the world.
        commands: dict[int, tuple[float, float]] = {}
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
            along = a_spec.path.heading_at(a.path_s)
            cx, cy = math.cos(along), math.sin(along)
            behind = any((agents[j].pose.x - x) * cx + (agents[j].pose.y - y) * cy < 0.0 for _, j in neighbours[i])
            course[i] = (cx, cy, speed, behind)
            preferred = self._preferred_velocity(a, speed)
            if self.perturbation.active:
                angle = self._perturbation_rng.random() * 2.0 * math.pi
                length = self._perturbation_rng.random() * self.perturbation.magnitude_mps
                preferred = (preferred[0] + length * math.cos(angle), preferred[1] + length * math.sin(angle))

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
                )
        self.fallback_agents = fallback_agents
        self.steps_with_fallback += bool(fallback_agents)

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
            self.backward[i].update(now, end, vx * cx + vy * cy < -limits.backward_speed_mps)
            self.hurried[i].update(now, end, behind and speed > (1.0 + limits.hurried_fraction) * wanted)
            for index, entry_s, _ in a.spec.single_file_stretches:
                if index not in self.segment_entry_times[i] and a.path_s >= entry_s:
                    self.segment_entry_times[i][index] = end
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

    def _close_pair(self, pair: PairInteraction, reason: str) -> None:
        pair.end_step, pair.end_time_s, pair.end_reason = self.world.step_index, self.world.time, reason
        if self.provider.follows_pairs:
            self.provider.close_pair(pair, pair.end_step, pair.end_time_s, reason)

    def _categorise(self, pair: PairInteraction, yields: list[YieldEvent]) -> None:
        """``avoided``, ``resolved`` or ``failed`` (``docs/metrics.md``, section 9).

        ``failed``: the two collided while the pair was open, or the run ended in deadlock
        with it open. Otherwise ``resolved``: one of them was exposed to the other, or one
        of them yielded while the pair was open. Otherwise ``avoided``.
        """
        start, end = pair.start_time_s, pair.end_time_s
        yielded = [
            event for event in yields
            if event.agent_id in pair.agents and event.start_time_s <= end and event.end_time_s >= start
        ]
        collided = [
            episode for episode in self.overlaps.events
            if tuple(sorted(episode.pair)) == pair.agents and episode.start_time_s <= end and episode.end_time_s >= start
        ]
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
            "yield_events": len(yielded),
            "collisions": len(collided),
            "deadlock": deadlocked,
            "open_at_timeout": self.status == STATUS_TIMEOUT and pair.end_reason == PAIR_END_RUN_ENDED,
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
    def _row(step, now, agent, preferred, decision, under_arbiter, n_neighbours, speed_scale, exposed, fallback, ids):
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
            "control_mode": MODE_ARBITER if under_arbiter else MODE_ORCA,
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
        }

    def _final_row(self, agent) -> dict[str, Any]:
        row = dict.fromkeys(
            (
                "vx_mps", "vy_mps", "speed_mps", "pref_vx_mps", "pref_vy_mps", "control_mode",
                "speed_bound_mps", "role", "role_source", "in_conflict", "zone_d_in_m", "zone_d_out_m",
                "n_neighbours", "speed_scale", "exposed", "fallback", "interactions",
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
