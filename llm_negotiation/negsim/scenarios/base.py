"""Scenario base class and the resolved scenario description.

A scenario class turns the ``geometry`` block of a scenario YAML file into a layout: where
each of the two agents starts, where it is going, the path it wants to take, the walls,
and where the physical conflict region lies along each path. :meth:`Scenario.build` adds
the settings every scenario shares and returns a :class:`ScenarioSpec`.

Canonical slots and agent indices are separate things. A layout lists its two slots in a
fixed order (for the doorway: north, then south). Agent 0 takes the first slot unless the
config says ``swap_sides: true``. Per-agent settings (``agents``, ``start_offsets``) always
go by agent index.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Mapping, Optional

from ..configutil import ConfigError, as_bool, as_choice, as_number, check_keys
from ..conflict.detection import ConflictDetector, make_detector
from ..control.base import MotionController, make_controller
from ..core.agent import AgentSpec
from ..core.geometry import Polyline, Rect, Vec
from ..core.state import Pose
from ..core.world import World

SCHEMA_VERSION = 1

_REQUIRED = ("type", "dt", "max_time", "geometry", "agent_defaults", "conflict", "controller")
_OPTIONAL = (
    "schema_version",
    "description",
    "goal_tolerance",
    "agents",
    "start_offsets",
    "swap_sides",
    "observation",
    "deadlock",
)
_AGENT_KEYS = ("radius", "max_speed", "max_turn_rate", "initial_speed")


@dataclass(frozen=True)
class RegionInfo:
    """The physical place the two agents cannot both be in: its kind and size in metres."""

    kind: str
    width: float
    length: float

    def as_dict(self) -> dict:
        return {"kind": self.kind, "width_m": self.width, "length_m": self.length}


@dataclass(frozen=True)
class ConflictSettings:
    predictor: str
    safety_margin: float
    zone_half_length: Optional[float]  # None: computed from the geometry ("auto")

    def as_dict(self) -> dict:
        return {
            "predictor": self.predictor,
            "safety_margin_m": self.safety_margin,
            "zone_half_length_m": "auto" if self.zone_half_length is None else self.zone_half_length,
        }


@dataclass(frozen=True)
class ObservationSettings:
    """When two agents can see each other. GameChat does not model occlusion."""

    max_range: Optional[float]
    walls_block_sight: bool

    def as_dict(self) -> dict:
        return {"max_range_m": self.max_range, "walls_block_sight": self.walls_block_sight}


@dataclass(frozen=True)
class DeadlockSettings:
    window_s: float
    speed_eps: float

    def as_dict(self) -> dict:
        return {"window_s": self.window_s, "speed_eps_mps": self.speed_eps}


@dataclass(frozen=True)
class SlotLayout:
    start: Pose
    goal: Vec
    path: Polyline
    side: str
    region_entry_s: float
    region_exit_s: float


@dataclass(frozen=True)
class Layout:
    slots: tuple[SlotLayout, SlotLayout]
    obstacles: tuple[Rect, ...]
    region: RegionInfo


@dataclass(frozen=True)
class ScenarioSpec:
    """A fully resolved scenario: everything needed to build the world and to log it."""

    scenario_type: str
    description: str
    dt: float
    max_time: float
    goal_tolerance: float
    agents: tuple[AgentSpec, ...]
    obstacles: tuple[Rect, ...]
    region: RegionInfo
    conflict: ConflictSettings
    observation: ObservationSettings
    deadlock: DeadlockSettings
    controller: Mapping[str, Any]
    swap_sides: bool
    start_offsets: tuple[float, ...]
    geometry: Mapping[str, float]

    def build_world(self) -> World:
        return World(self.agents, self.obstacles, self.dt, self.goal_tolerance)

    def build_detector(self) -> ConflictDetector:
        return make_detector(
            self.conflict.predictor, self.conflict.safety_margin, self.conflict.zone_half_length
        )

    def build_controller(self) -> MotionController:
        params = {k: v for k, v in self.controller.items() if k != "backend"}
        return make_controller(self.controller["backend"], **params)

    @property
    def max_steps(self) -> int:
        return int(round(self.max_time / self.dt))

    def as_dict(self) -> dict:
        return {
            "type": self.scenario_type,
            "description": self.description,
            "dt_s": self.dt,
            "max_time_s": self.max_time,
            "goal_tolerance_m": self.goal_tolerance,
            "geometry": dict(self.geometry),
            "swap_sides": self.swap_sides,
            "start_offsets_m": list(self.start_offsets),
            "region": self.region.as_dict(),
            "conflict": self.conflict.as_dict(),
            "observation": self.observation.as_dict(),
            "deadlock": self.deadlock.as_dict(),
            "controller": dict(self.controller),
            "agents": [agent.as_dict() for agent in self.agents],
            "obstacles": [obstacle.as_dict() for obstacle in self.obstacles],
        }


class Scenario(ABC):
    """Base class: subclasses supply the geometry, this class supplies everything else."""

    type_name: ClassVar[str]
    geometry_keys: ClassVar[tuple[str, ...]]

    @abstractmethod
    def layout(self, geometry: Mapping[str, float], offsets: tuple[float, float]) -> Layout:
        """Lay out the two canonical slots. ``offsets[k]`` moves slot ``k``'s start back."""

    def check(self, spec: ScenarioSpec) -> None:
        """Scenario-specific sanity checks; raise :class:`ConfigError` on failure."""

    def build(self, cfg: Mapping[str, Any]) -> ScenarioSpec:
        where = f"scenario '{self.type_name}'"
        check_keys(cfg, where, _REQUIRED, _OPTIONAL)
        version = cfg.get("schema_version", SCHEMA_VERSION)
        if version != SCHEMA_VERSION:
            raise ConfigError(f"{where}: schema_version {version!r} is not supported ({SCHEMA_VERSION})")

        check_keys(cfg["geometry"], f"{where}.geometry", self.geometry_keys)
        geometry = {
            key: as_number(cfg["geometry"][key], f"{where}.geometry.{key}", minimum=0.0)
            for key in self.geometry_keys
        }

        dt = as_number(cfg["dt"], f"{where}.dt", minimum=0.0, strict_minimum=True)
        max_time = as_number(cfg["max_time"], f"{where}.max_time", minimum=0.0, strict_minimum=True)
        goal_tolerance = as_number(
            cfg.get("goal_tolerance", 0.1), f"{where}.goal_tolerance", minimum=0.0, strict_minimum=True
        )
        swap_sides = as_bool(cfg.get("swap_sides", False), f"{where}.swap_sides")

        offsets_raw = cfg.get("start_offsets", [0.0, 0.0])
        if not isinstance(offsets_raw, (list, tuple)) or len(offsets_raw) != 2:
            raise ConfigError(f"{where}.start_offsets: expected a list of two numbers, one per agent")
        offsets = tuple(
            as_number(v, f"{where}.start_offsets[{k}]", minimum=0.0) for k, v in enumerate(offsets_raw)
        )

        # Agent k takes canonical slot k, or the other one if the sides are swapped.
        slot_of_agent = (1, 0) if swap_sides else (0, 1)
        slot_offsets = [0.0, 0.0]
        for agent_id, slot in enumerate(slot_of_agent):
            slot_offsets[slot] = offsets[agent_id]
        layout = self.layout(geometry, (slot_offsets[0], slot_offsets[1]))

        agents = tuple(
            self._agent_spec(agent_id, layout.slots[slot], cfg, where)
            for agent_id, slot in enumerate(slot_of_agent)
        )

        spec = ScenarioSpec(
            scenario_type=self.type_name,
            description=str(cfg.get("description", "")).strip(),
            dt=dt,
            max_time=max_time,
            goal_tolerance=goal_tolerance,
            agents=agents,
            obstacles=layout.obstacles,
            region=layout.region,
            conflict=self._conflict_settings(cfg["conflict"], agents, f"{where}.conflict"),
            observation=self._observation_settings(cfg.get("observation", {}), f"{where}.observation"),
            deadlock=self._deadlock_settings(cfg.get("deadlock", {}), f"{where}.deadlock"),
            controller=self._controller_settings(cfg["controller"], f"{where}.controller"),
            swap_sides=swap_sides,
            start_offsets=offsets,
            geometry=geometry,
        )
        self._check_common(spec, where)
        self.check(spec)
        return spec

    def _agent_spec(
        self, agent_id: int, slot: SlotLayout, cfg: Mapping[str, Any], where: str
    ) -> AgentSpec:
        defaults = check_keys(
            cfg["agent_defaults"],
            f"{where}.agent_defaults",
            ("radius", "max_speed", "max_turn_rate"),
            ("initial_speed",),
        )
        overrides_list = cfg.get("agents", [{}, {}])
        if not isinstance(overrides_list, (list, tuple)) or len(overrides_list) != 2:
            raise ConfigError(f"{where}.agents: expected a list of two mappings, one per agent")
        overrides = overrides_list[agent_id] or {}
        check_keys(overrides, f"{where}.agents[{agent_id}]", (), _AGENT_KEYS)
        params = {**defaults, **overrides}
        label = f"{where}.agents[{agent_id}]"
        radius = as_number(params["radius"], f"{label}.radius", minimum=0.0, strict_minimum=True)
        max_speed = as_number(
            params["max_speed"], f"{label}.max_speed", minimum=0.0, strict_minimum=True
        )
        max_turn_rate = as_number(
            params["max_turn_rate"], f"{label}.max_turn_rate", minimum=0.0, strict_minimum=True
        )
        initial_speed = (
            max_speed
            if params.get("initial_speed") is None
            else as_number(params["initial_speed"], f"{label}.initial_speed", minimum=0.0)
        )
        if initial_speed > max_speed:
            raise ConfigError(f"{label}.initial_speed {initial_speed} exceeds max_speed {max_speed}")
        return AgentSpec(
            agent_id=agent_id,
            radius=radius,
            max_speed=max_speed,
            max_turn_rate=max_turn_rate,
            start=slot.start,
            goal=slot.goal,
            path=slot.path,
            side=slot.side,
            region_entry_s=slot.region_entry_s,
            region_exit_s=slot.region_exit_s,
            initial_speed=initial_speed,
        )

    @staticmethod
    def _conflict_settings(
        raw: Any, agents: tuple[AgentSpec, ...], where: str
    ) -> ConflictSettings:
        check_keys(raw, where, ("predictor", "safety_margin"), ("zone_half_length",))
        predictor = as_choice(raw["predictor"], f"{where}.predictor", ("heading_ray", "desired_path"))
        margin = as_number(raw["safety_margin"], f"{where}.safety_margin", minimum=0.0)
        half = raw.get("zone_half_length", "auto")
        if half == "auto":
            half_length = None
        else:
            # A zone shorter than a body would give the conflict region a negative length.
            half_length = as_number(
                half, f"{where}.zone_half_length", minimum=max(a.radius for a in agents)
            )
            if predictor != "heading_ray":
                raise ConfigError(
                    f"{where}.zone_half_length: a fixed value needs predictor 'heading_ray'; "
                    "use 'auto' with 'desired_path'"
                )
        return ConflictSettings(predictor, margin, half_length)

    @staticmethod
    def _observation_settings(raw: Any, where: str) -> ObservationSettings:
        check_keys(raw, where, (), ("max_range", "walls_block_sight"))
        max_range = raw.get("max_range")
        if max_range is not None:
            max_range = as_number(max_range, f"{where}.max_range", minimum=0.0, strict_minimum=True)
        return ObservationSettings(
            max_range, as_bool(raw.get("walls_block_sight", False), f"{where}.walls_block_sight")
        )

    @staticmethod
    def _deadlock_settings(raw: Any, where: str) -> DeadlockSettings:
        check_keys(raw, where, (), ("window_s", "speed_eps"))
        return DeadlockSettings(
            as_number(raw.get("window_s", 3.0), f"{where}.window_s", minimum=0.0, strict_minimum=True),
            as_number(raw.get("speed_eps", 0.01), f"{where}.speed_eps", minimum=0.0),
        )

    @staticmethod
    def _controller_settings(raw: Any, where: str) -> dict[str, Any]:
        if not isinstance(raw, Mapping) or "backend" not in raw:
            raise ConfigError(f"{where}: expected a mapping with a 'backend' key")
        settings = dict(raw)
        try:
            make_controller(settings["backend"], **{k: v for k, v in settings.items() if k != "backend"})
        except (TypeError, ValueError) as exc:
            raise ConfigError(f"{where}: {exc}") from exc
        return settings

    @staticmethod
    def _check_common(spec: ScenarioSpec, where: str) -> None:
        for agent in spec.agents:
            if 2.0 * agent.radius >= spec.region.width:
                raise ConfigError(
                    f"{where}: agent {agent.agent_id} is {2.0 * agent.radius:.2f} m wide and "
                    f"cannot fit through a {spec.region.kind} {spec.region.width:.2f} m wide"
                )
            clearance = _path_clearance(agent.path, spec.obstacles)
            if clearance < agent.radius:
                raise ConfigError(
                    f"{where}: agent {agent.agent_id} has radius {agent.radius:.2f} m but its "
                    f"path passes {clearance:.2f} m from a wall, so it cannot follow the path "
                    "without hitting the wall"
                )
        world = spec.build_world()
        if world.agent_collisions():
            raise ConfigError(f"{where}: the agents overlap at their starting positions")
        conflict = spec.build_detector().zone(world.agents[0], world.agents[1])
        if conflict is not None and all(view.d_in <= 0.0 for view in conflict.views.values()):
            raise ConfigError(
                f"{where}: both agents start inside the conflict zone, so neither can give way. "
                "Move the starts further apart or reduce conflict.safety_margin."
            )


def _path_clearance(path: Polyline, obstacles: tuple[Rect, ...], spacing: float = 0.02) -> float:
    """Smallest distance between a path and any obstacle, sampled every ``spacing`` metres."""
    if not obstacles:
        return float("inf")
    samples = max(1, int(path.length / spacing))
    return min(
        obstacle.distance_to(path.point_at(k * path.length / samples))
        for k in range(samples + 1)
        for obstacle in obstacles
    )
