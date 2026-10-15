"""Scenarios for the avoidance layer: any number of holonomic agents steered by ORCA.

These are a second kind of scenario, with their own config schema (``schema_version: 2``)
and their own files under ``configs/scenarios/``. The scenarios of issue #24 (doorway,
intersection, hallway; ``schema_version: 1``; ``negsim.scenarios.base``) are untouched and
load exactly as before.

A scenario class turns the ``geometry`` block of its config into a layout: one
:class:`Placement` per agent (where it starts, where it is going, the path it wants to
take, the agent type it has), the walls, and any single-file segments.
:meth:`CrowdScenario.build` adds what every scenario shares and returns a
:class:`CrowdScenarioSpec`.

Physical parameters and demographic attributes are separate on purpose. Everything here
is physical: sizes, speeds, sensing. An agent's age and gender are attached later, by an
experiment, and nothing in this module can read them, so they cannot change an agent's
speed or size unless an experiment sets both for the same agent explicitly.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Mapping, Optional, Sequence

from ..avoidance.orca import TIE_BRAKE, TIE_BREAKS
from ..configutil import ConfigError, as_choice, as_number, check_keys
from ..core.agent import AgentSpec
from ..core.dynamics import DYNAMICS, HolonomicDynamics, make_dynamics
from ..core.geometry import Polyline, Rect, Vec
from ..core.state import Pose
from ..core.world import ARRIVAL_PATH_END, World
from .base import DeadlockSettings

CROWD_SCHEMA_VERSION = 2

_REQUIRED = ("schema_version", "type", "dt", "max_time", "geometry", "agent_types")
_OPTIONAL = (
    "description",
    "goal_tolerance",
    "dynamics",
    "agents",
    "orca",
    "navigation",
    "neighbour_search",
    "single_file",
    "deadlock",
    "metrics",
    "seed",
    "on_collision",
)
#: What a run does when two bodies overlap. ``stop`` ends it there, as every run of issue
#: #24 does. ``continue`` records the collision and goes on; ORCA then pushes the two
#: apart. It exists for crowds, where ORCA's fallback can let two discs overlap (by
#: millimetres to centimetres; ``docs/metrics.md``, section 6, has the depths measured) and
#: stopping at the first overlap would end the run before it has shown anything.
ON_COLLISION_STOP, ON_COLLISION_CONTINUE = "stop", "continue"
ON_COLLISION = (ON_COLLISION_STOP, ON_COLLISION_CONTINUE)
AGENT_TYPE_KEYS = (
    "radius",
    "preferred_speed",
    "max_speed",
    "sensing_radius",
    "max_neighbours",
    "time_horizon",
    "time_horizon_obst",
)


@dataclass(frozen=True)
class AgentType:
    """The physical parameters of a kind of agent. None of them is demographic."""

    name: str
    radius: float
    preferred_speed: float
    max_speed: float
    sensing_radius: float
    max_neighbours: int
    time_horizon: float
    time_horizon_obst: float

    @classmethod
    def from_mapping(cls, name: str, raw: Any, where: str) -> "AgentType":
        check_keys(raw, where, AGENT_TYPE_KEYS)
        positive = {
            key: as_number(raw[key], f"{where}.{key}", minimum=0.0, strict_minimum=True)
            for key in AGENT_TYPE_KEYS
            if key != "max_neighbours"
        }
        neighbours = raw["max_neighbours"]
        if isinstance(neighbours, bool) or not isinstance(neighbours, int) or neighbours < 0:
            raise ConfigError(f"{where}.max_neighbours: expected a whole number, 0 or more, got {neighbours!r}")
        if positive["preferred_speed"] > positive["max_speed"]:
            raise ConfigError(
                f"{where}: preferred_speed {positive['preferred_speed']} exceeds max_speed {positive['max_speed']}"
            )
        return cls(name=name, max_neighbours=neighbours, **positive)

    def with_overrides(self, overrides: Mapping[str, Any], where: str) -> "AgentType":
        check_keys(overrides, where, (), AGENT_TYPE_KEYS)
        return AgentType.from_mapping(self.name, {**self.as_dict(), **overrides}, where)

    def as_dict(self) -> dict[str, Any]:
        return {key: getattr(self, key) for key in AGENT_TYPE_KEYS}


@dataclass(frozen=True)
class CrowdAgentSpec(AgentSpec):
    """An :class:`AgentSpec` with the parameters the avoidance layer needs.

    ``single_file_stretches`` are the stretches of the agent's path that run through a
    single-file segment, each as ``(index of the segment, arc length at which the path
    enters it, arc length at which it leaves)``. ``max_turn_rate`` is infinite: a
    holonomic agent has no turning limit.
    """

    agent_type: str
    group: str
    preferred_speed: float
    sensing_radius: float
    max_neighbours: int
    time_horizon: float
    time_horizon_obst: float
    single_file_stretches: tuple[tuple[int, float, float], ...]

    def as_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "group": self.group,
            "side": self.side,
            "radius_m": self.radius,
            "preferred_speed_mps": self.preferred_speed,
            "max_speed_mps": self.max_speed,
            "initial_speed_mps": self.initial_speed,
            "sensing_radius_m": self.sensing_radius,
            "max_neighbours": self.max_neighbours,
            "time_horizon_s": self.time_horizon,
            "time_horizon_obst_s": self.time_horizon_obst,
            "start": {"x": self.start.x, "y": self.start.y, "theta_rad": self.start.theta},
            "goal": {"x": self.goal[0], "y": self.goal[1]},
            "path": self.path.as_list(),
            "path_length_m": self.path.length,
            "single_file_stretches": [
                {"segment": index, "entry_s_m": entry, "exit_s_m": exit_}
                for index, entry, exit_ in self.single_file_stretches
            ],
        }


@dataclass(frozen=True)
class SingleFileSegment:
    """A stretch of free space too narrow for two agents to pass in.

    ``rect`` is the free space itself, not its walls. Which pairs of agents it is too
    narrow for is checked per pair against ``width``.
    """

    name: str
    rect: Rect
    width: float

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "width_m": self.width, **self.rect.as_dict()}


@dataclass(frozen=True)
class MetricThresholds:
    """Thresholds of the conflict metrics (``docs/metrics.md``).

    ``pair_exposure_eps`` and ``collision_course_min_s`` were added by issue #30: how deep
    inside the velocity obstacle the two intended velocities must be for a step to count
    as pair exposure, and how much pair exposure makes a pair interaction tier T1
    (``docs/metrics.md``, section 11).
    """

    near_miss_distance: float
    yield_speed_fraction: float
    yield_min_duration: float
    exposure_eps: float
    pair_exposure_eps: float = 1e-3
    collision_course_min_s: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "near_miss_distance_m": self.near_miss_distance,
            "yield_speed_fraction": self.yield_speed_fraction,
            "yield_min_duration_s": self.yield_min_duration,
            "exposure_eps_mps": self.exposure_eps,
            "pair_exposure_eps_mps": self.pair_exposure_eps,
            "collision_course_min_s": self.collision_course_min_s,
        }


#: Defaults of the metric thresholds. Each is this project's choice, not a sourced value;
#: ``docs/metrics.md`` and ``docs/parameters.md`` say so.
DEFAULT_THRESHOLDS = MetricThresholds(
    near_miss_distance=0.1,
    yield_speed_fraction=0.5,
    yield_min_duration=1.0,
    exposure_eps=1e-6,
    pair_exposure_eps=1e-3,
    collision_course_min_s=0.0,
)


@dataclass(frozen=True)
class Placement:
    """Where one agent starts, where it is going, and what kind of agent it is."""

    start: Vec
    goal: Vec
    path: Polyline
    group: str
    agent_type: str = "default"


@dataclass(frozen=True)
class CrowdLayout:
    placements: tuple[Placement, ...]
    obstacles: tuple[Rect, ...]
    single_file_segments: tuple[SingleFileSegment, ...] = ()


@dataclass(frozen=True)
class CrowdScenarioSpec:
    """A fully resolved avoidance scenario: everything needed to build the world and log it."""

    scenario_type: str
    description: str
    dt: float
    max_time: float
    goal_tolerance: float
    dynamics: str
    agents: tuple[CrowdAgentSpec, ...]
    agent_types: Mapping[str, AgentType]
    obstacles: tuple[Rect, ...]
    single_file_segments: tuple[SingleFileSegment, ...]
    single_file_safety_margin: float
    tie_break: str
    lookahead: float
    cell_size: float
    deadlock: DeadlockSettings
    thresholds: MetricThresholds
    geometry: Mapping[str, Any]
    seed: int
    on_collision: str = ON_COLLISION_STOP

    def build_world(self) -> World:
        return World(
            self.agents,
            self.obstacles,
            self.dt,
            self.goal_tolerance,
            dynamics=make_dynamics(self.dynamics),
            arrival=ARRIVAL_PATH_END,
        )

    @property
    def max_steps(self) -> int:
        return int(round(self.max_time / self.dt))

    def as_dict(self) -> dict:
        return {
            "schema_version": CROWD_SCHEMA_VERSION,
            "type": self.scenario_type,
            "description": self.description,
            "dt_s": self.dt,
            "max_time_s": self.max_time,
            "goal_tolerance_m": self.goal_tolerance,
            "arrival": ARRIVAL_PATH_END,
            "dynamics": self.dynamics,
            "seed": self.seed,
            "on_collision": self.on_collision,
            "geometry": dict(self.geometry),
            "agent_types": {name: agent_type.as_dict() for name, agent_type in sorted(self.agent_types.items())},
            "orca": {"tie_break": self.tie_break},
            "navigation": {"lookahead_m": self.lookahead},
            "neighbour_search": {"cell_size_m": self.cell_size},
            "single_file": {
                "safety_margin_m": self.single_file_safety_margin,
                "segments": [segment.as_dict() for segment in self.single_file_segments],
            },
            "deadlock": self.deadlock.as_dict(),
            "metrics": self.thresholds.as_dict(),
            "n_agents": len(self.agents),
            "agents": [agent.as_dict() for agent in self.agents],
            "obstacles": [obstacle.as_dict() for obstacle in self.obstacles],
        }


class CrowdScenario(ABC):
    """Base class: subclasses supply the layout, this class supplies everything else."""

    type_name: ClassVar[str]

    @abstractmethod
    def geometry(self, raw: Mapping[str, Any], where: str) -> dict[str, Any]:
        """Validate the ``geometry`` block and return it with defaults filled in."""

    @abstractmethod
    def layout(self, geometry: Mapping[str, Any], seed: int) -> CrowdLayout:
        """Place the agents and the walls. Agent ``k`` is ``placements[k]``."""

    def check(self, spec: CrowdScenarioSpec) -> None:
        """Scenario-specific sanity checks; raise :class:`ConfigError` on failure."""

    def build(self, cfg: Mapping[str, Any]) -> CrowdScenarioSpec:
        where = f"scenario '{self.type_name}'"
        check_keys(cfg, where, _REQUIRED, _OPTIONAL)
        if cfg["schema_version"] != CROWD_SCHEMA_VERSION:
            raise ConfigError(
                f"{where}: schema_version {cfg['schema_version']!r} is not supported; an avoidance "
                f"scenario has schema_version {CROWD_SCHEMA_VERSION}"
            )
        dt = as_number(cfg["dt"], f"{where}.dt", minimum=0.0, strict_minimum=True)
        max_time = as_number(cfg["max_time"], f"{where}.max_time", minimum=0.0, strict_minimum=True)
        goal_tolerance = as_number(
            cfg.get("goal_tolerance", 0.2), f"{where}.goal_tolerance", minimum=0.0, strict_minimum=True
        )
        dynamics = as_choice(cfg.get("dynamics", HolonomicDynamics.name), f"{where}.dynamics", sorted(DYNAMICS))
        if dynamics != HolonomicDynamics.name:
            raise ConfigError(
                f"{where}.dynamics: the avoidance layer has only been built and tested with "
                f"{HolonomicDynamics.name!r} dynamics; non-holonomic ORCA is out of scope for issue #26"
            )
        seed = cfg.get("seed", 0)
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise ConfigError(f"{where}.seed: expected a whole number, 0 or more, got {seed!r}")

        if not isinstance(cfg["agent_types"], Mapping) or not cfg["agent_types"]:
            raise ConfigError(f"{where}.agent_types: expected a mapping with at least one agent type")
        agent_types = {
            str(name): AgentType.from_mapping(str(name), raw, f"{where}.agent_types.{name}")
            for name, raw in cfg["agent_types"].items()
        }

        geometry = self.geometry(cfg["geometry"], f"{where}.geometry")
        layout = self.layout(geometry, seed)
        agents = self._agents(layout, agent_types, cfg.get("agents") or {}, f"{where}.agents")

        orca = check_keys(cfg.get("orca") or {}, f"{where}.orca", (), ("tie_break",))
        navigation = check_keys(cfg.get("navigation") or {}, f"{where}.navigation", (), ("lookahead",))
        search = check_keys(cfg.get("neighbour_search") or {}, f"{where}.neighbour_search", (), ("cell_size",))
        single_file = check_keys(cfg.get("single_file") or {}, f"{where}.single_file", (), ("safety_margin",))
        deadlock = check_keys(cfg.get("deadlock") or {}, f"{where}.deadlock", (), ("window_s", "speed_eps"))
        metrics = check_keys(
            cfg.get("metrics") or {},
            f"{where}.metrics",
            (),
            (
                "near_miss_distance",
                "yield_speed_fraction",
                "yield_min_duration",
                "exposure_eps",
                "pair_exposure_eps",
                "collision_course_min_s",
            ),
        )
        defaults = DEFAULT_THRESHOLDS
        fraction = as_number(
            metrics.get("yield_speed_fraction", defaults.yield_speed_fraction),
            f"{where}.metrics.yield_speed_fraction",
            minimum=0.0,
        )
        if fraction > 1.0:
            raise ConfigError(f"{where}.metrics.yield_speed_fraction: must be at most 1, got {fraction}")

        spec = CrowdScenarioSpec(
            scenario_type=self.type_name,
            description=" ".join(str(cfg.get("description", "")).split()),
            dt=dt,
            max_time=max_time,
            goal_tolerance=goal_tolerance,
            dynamics=dynamics,
            agents=agents,
            agent_types=agent_types,
            obstacles=layout.obstacles,
            single_file_segments=layout.single_file_segments,
            single_file_safety_margin=as_number(
                single_file.get("safety_margin", 0.1), f"{where}.single_file.safety_margin", minimum=0.0
            ),
            tie_break=as_choice(orca.get("tie_break", TIE_BRAKE), f"{where}.orca.tie_break", TIE_BREAKS),
            lookahead=as_number(
                navigation.get("lookahead", 2.0), f"{where}.navigation.lookahead", minimum=0.0, strict_minimum=True
            ),
            cell_size=as_number(
                search.get("cell_size", 2.0), f"{where}.neighbour_search.cell_size", minimum=0.0, strict_minimum=True
            ),
            deadlock=DeadlockSettings(
                as_number(deadlock.get("window_s", 3.0), f"{where}.deadlock.window_s", minimum=0.0, strict_minimum=True),
                as_number(deadlock.get("speed_eps", 0.01), f"{where}.deadlock.speed_eps", minimum=0.0),
            ),
            thresholds=MetricThresholds(
                near_miss_distance=as_number(
                    metrics.get("near_miss_distance", defaults.near_miss_distance),
                    f"{where}.metrics.near_miss_distance",
                    minimum=0.0,
                ),
                yield_speed_fraction=fraction,
                yield_min_duration=as_number(
                    metrics.get("yield_min_duration", defaults.yield_min_duration),
                    f"{where}.metrics.yield_min_duration",
                    minimum=0.0,
                ),
                exposure_eps=as_number(
                    metrics.get("exposure_eps", defaults.exposure_eps), f"{where}.metrics.exposure_eps", minimum=0.0
                ),
                pair_exposure_eps=as_number(
                    metrics.get("pair_exposure_eps", defaults.pair_exposure_eps),
                    f"{where}.metrics.pair_exposure_eps",
                    minimum=0.0,
                ),
                collision_course_min_s=as_number(
                    metrics.get("collision_course_min_s", defaults.collision_course_min_s),
                    f"{where}.metrics.collision_course_min_s",
                    minimum=0.0,
                ),
            ),
            geometry=geometry,
            seed=seed,
            on_collision=as_choice(
                cfg.get("on_collision", ON_COLLISION_STOP), f"{where}.on_collision", ON_COLLISION
            ),
        )
        self._check_common(spec, where)
        self.check(spec)
        return spec

    @staticmethod
    def _agents(
        layout: CrowdLayout, agent_types: Mapping[str, AgentType], raw: Mapping[str, Any], where: str
    ) -> tuple[CrowdAgentSpec, ...]:
        check_keys(raw, where, (), ("default_type", "groups", "overrides"))
        default_name = raw.get("default_type")
        if default_name is None:
            if len(agent_types) != 1:
                raise ConfigError(f"{where}.default_type: needed when there is more than one agent type")
            default_name = next(iter(agent_types))
        if default_name not in agent_types:
            raise ConfigError(f"{where}.default_type: unknown agent type {default_name!r}; known: {sorted(agent_types)}")

        groups = raw.get("groups") or {}
        known_groups = {placement.group for placement in layout.placements}
        for group, type_name in groups.items():
            if group not in known_groups:
                raise ConfigError(f"{where}.groups: unknown group {group!r}; this scenario has {sorted(known_groups)}")
            if type_name not in agent_types:
                raise ConfigError(f"{where}.groups.{group}: unknown agent type {type_name!r}; known: {sorted(agent_types)}")

        overrides: dict[int, Mapping[str, Any]] = {}
        for key, entry in (raw.get("overrides") or {}).items():
            if isinstance(key, bool) or not isinstance(key, int) or not 0 <= key < len(layout.placements):
                raise ConfigError(
                    f"{where}.overrides: {key!r} is not an agent index; this scenario has agents 0 to "
                    f"{len(layout.placements) - 1}"
                )
            overrides[key] = entry or {}

        agents = []
        for agent_id, placement in enumerate(layout.placements):
            type_name = groups.get(
                placement.group, default_name if placement.agent_type == "default" else placement.agent_type
            )
            if type_name not in agent_types:
                raise ConfigError(f"{where}: agent {agent_id} needs agent type {type_name!r}; known: {sorted(agent_types)}")
            agent_type = agent_types[type_name]
            if agent_id in overrides:
                agent_type = agent_type.with_overrides(overrides[agent_id], f"{where}.overrides.{agent_id}")
            path = placement.path
            agents.append(
                CrowdAgentSpec(
                    agent_id=agent_id,
                    radius=agent_type.radius,
                    max_speed=agent_type.max_speed,
                    max_turn_rate=math.inf,
                    start=Pose(placement.start[0], placement.start[1], path.heading_at(0.0)),
                    goal=placement.goal,
                    path=path,
                    side=placement.group,
                    region_entry_s=path.length,
                    region_exit_s=path.length,
                    initial_speed=agent_type.preferred_speed,
                    agent_type=type_name,
                    group=placement.group,
                    preferred_speed=agent_type.preferred_speed,
                    sensing_radius=agent_type.sensing_radius,
                    max_neighbours=agent_type.max_neighbours,
                    time_horizon=agent_type.time_horizon,
                    time_horizon_obst=agent_type.time_horizon_obst,
                    single_file_stretches=tuple(
                        (index, interval[0], interval[1])
                        for index, interval in (
                            (index, path_interval_in(path, segment.rect))
                            for index, segment in enumerate(layout.single_file_segments)
                        )
                        if interval is not None
                    ),
                )
            )
        return tuple(agents)

    @staticmethod
    def _check_common(spec: CrowdScenarioSpec, where: str) -> None:
        if not spec.agents:
            raise ConfigError(f"{where}: the scenario has no agents")
        for agent in spec.agents:
            if agent.time_horizon_obst < spec.dt:
                raise ConfigError(
                    f"{where}: agent {agent.agent_id} has time_horizon_obst {agent.time_horizon_obst} s, "
                    f"shorter than the time step {spec.dt} s. The wall half-plane only keeps an agent "
                    "off a wall if the horizon is at least one time step (docs/derivations.md, section 12)."
                )
            for wall in spec.obstacles:
                if wall.distance_to(agent.start.xy) < agent.radius:
                    raise ConfigError(f"{where}: agent {agent.agent_id} starts overlapping a wall")
            if not _may_touch_a_wall(agent.path, agent.radius, spec.obstacles):
                continue
            clearance = path_clearance(agent.path, spec.obstacles)
            if clearance < agent.radius:
                raise ConfigError(
                    f"{where}: agent {agent.agent_id} has radius {agent.radius:.2f} m but its path "
                    f"passes {clearance:.2f} m from a wall, so it cannot follow the path"
                )
        widest = max(agent.radius for agent in spec.agents)
        ordered = sorted(spec.agents, key=lambda agent: agent.start.x)
        for index, a in enumerate(ordered):
            for b in ordered[index + 1 :]:
                if b.start.x - a.start.x >= a.radius + widest:
                    break  # sorted by x: nobody further along the list can reach back to a
                if math.hypot(a.start.x - b.start.x, a.start.y - b.start.y) < a.radius + b.radius:
                    raise ConfigError(
                        f"{where}: agents {a.agent_id} and {b.agent_id} overlap at their starting positions"
                    )


def _may_touch_a_wall(path: Polyline, radius: float, obstacles: Sequence[Rect]) -> bool:
    """False if the path's bounding box, grown by ``radius``, misses every wall.

    A cheap test that spares the sampling below for the straight paths of a large crowd.
    """
    xs = [point[0] for point in path.points]
    ys = [point[1] for point in path.points]
    lo_x, hi_x, lo_y, hi_y = min(xs) - radius, max(xs) + radius, min(ys) - radius, max(ys) + radius
    return any(
        wall.xmin < hi_x and wall.xmax > lo_x and wall.ymin < hi_y and wall.ymax > lo_y for wall in obstacles
    )


def path_clearance(path: Polyline, obstacles: Sequence[Rect], spacing: float = 0.05) -> float:
    """Smallest distance between a path and any obstacle, sampled every ``spacing`` metres."""
    if not obstacles:
        return math.inf
    samples = max(1, int(path.length / spacing))
    return min(
        obstacle.distance_to(path.point_at(k * path.length / samples))
        for k in range(samples + 1)
        for obstacle in obstacles
    )


def path_interval_in(path: Polyline, rect: Rect, spacing: float = 0.01, tol: float = 1e-6) -> Optional[tuple[float, float]]:
    """Arc-length interval of ``path`` that lies inside ``rect``, or ``None`` if it never enters.

    Found by sampling and refining both ends by bisection. If the path enters more than
    once the interval spans all of it.
    """

    def inside(s: float) -> bool:
        x, y = path.point_at(s)
        return rect.xmin <= x <= rect.xmax and rect.ymin <= y <= rect.ymax

    n = max(1, math.ceil(path.length / spacing))
    samples = [k * path.length / n for k in range(n + 1)]
    hits = [k for k, s in enumerate(samples) if inside(s)]
    if not hits:
        return None
    first, last = hits[0], hits[-1]

    def refine(lo: float, hi: float, want: bool) -> float:
        while hi - lo > tol:
            mid = 0.5 * (lo + hi)
            if inside(mid) == want:
                hi = mid
            else:
                lo = mid
        return hi

    entry = 0.0 if first == 0 else refine(samples[first - 1], samples[first], True)
    exit_ = path.length if last == n else refine(samples[last], samples[last + 1], False)
    return entry, exit_


def number_list(raw: Any, where: str, length: int, minimum: Optional[float] = None) -> tuple[float, ...]:
    """A list of ``length`` numbers from a config."""
    if not isinstance(raw, (list, tuple)) or len(raw) != length:
        raise ConfigError(f"{where}: expected a list of {length} numbers")
    return tuple(as_number(value, f"{where}[{index}]", minimum=minimum) for index, value in enumerate(raw))


def whole_number(raw: Any, where: str, minimum: int = 0) -> int:
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < minimum:
        raise ConfigError(f"{where}: expected a whole number, {minimum} or more, got {raw!r}")
    return raw
