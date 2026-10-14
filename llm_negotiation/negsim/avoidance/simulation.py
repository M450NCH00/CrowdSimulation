"""One run of the avoidance layer: ORCA under directives, with the arbiter where only one fits.

Once per time step, for every agent that has not arrived:

1. **Perceive.** Find the agent's neighbours: the nearest ``max_neighbours`` agents no
   further away than its sensing radius. A neighbour that was not one on the step before
   starts an *interaction*: a perception record is built and the agent's directive
   provider is asked for a directive, which holds until the neighbour is out of range.
2. **Resolve.** Two agents that perceive each other each hold a directive about the
   other. The two are combined (``negsim.avoidance.directives.resolve_pair``); a pair that
   contradicts itself is logged as a reciprocity violation and repaired.
3. **Coordinate.** A pair with a single-file segment ahead of both is handed to the
   arbiter (``negsim.avoidance.coordination``), which decides who goes first and returns
   a speed bound for each.
4. **Choose a velocity.** The preferred velocity points along the agent's desired path at
   its preferred speed, scaled by its directives and capped by the arbiter. ORCA builds a
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
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping, Optional

from ..conflict.roles import RoleSource
from ..control.strategy1 import AgentDecision
from ..metrics.avoidance import ProximityEpisode, ProximityTracker, YieldEvent, YieldTracker
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
from .perception import PairFeatures, PerceptionRecord, default_visibility, pair_features, perceive

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
            "directive": self.directive.as_dict(),
            "effective": list(self.effective),
            "perceived_time_s": round(self.perceived_steps * dt, 6),
            "conflict_exposure_time_s": round(self.exposure_steps * dt, 6),
            "arbiter_time_s": round(self.arbiter_steps * dt, 6),
            "min_separation_m": separation,
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

    @property
    def min_separation_m(self) -> Optional[float]:
        value = min((stats.min_separation_m for stats in self.stats.values()), default=math.inf)
        return None if math.isinf(value) else value


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
        self.stats: dict[int, AgentStats] = {a.agent_id: AgentStats() for a in agents}
        thresholds = spec.thresholds
        self.yield_trackers = {
            a.agent_id: YieldTracker(
                a.agent_id, a.spec.preferred_speed, thresholds.yield_speed_fraction, thresholds.yield_min_duration
            )
            for a in agents
        }
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
        for tracker in self.yield_trackers.values():
            tracker.close()
        self.near_misses.close()
        self.overlaps.close()
        for agent_id in sorted(self.wall_overlaps):
            self.wall_collision_episodes.append(self.wall_overlaps.pop(agent_id))
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
            yields=[event for tracker in self.yield_trackers.values() for event in tracker.events],
            near_misses=list(self.near_misses.events),
            collision_episodes=list(self.overlaps.events),
            wall_collision_episodes=list(self.wall_collision_episodes),
            interactions=self.interactions,
            violations=self.violations,
            handoffs=self.handoffs,
            trajectory=self.trajectory,
            steps_with_fallback=self.steps_with_fallback,
            segment_entry_times=self.segment_entry_times,
        )

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
            preferred = self._preferred_velocity(a, speed)

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
        holds toward the neighbours it perceives now, and never above its maximum speed.
        """
        mine = self.open[agent.agent_id]
        scale = min((mine[j].directive.speed_scale for j in perceived), default=1.0)
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


def role_source_counts(result: SimulationResult) -> dict[str, int]:
    """How many handoffs to the arbiter took their leader from each source."""
    counts = {source.value: 0 for source in RoleSource}
    for handoff in result.handoffs:
        if handoff.to == TO_ARBITER and handoff.role_source is not None:
            counts[handoff.role_source] += 1
    return counts
