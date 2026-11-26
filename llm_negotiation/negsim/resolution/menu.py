"""A menu of described actions, with amounts in words (issue #136, RF-47; ``docs/action-space.md``,
section 6, AS3 and AS4).

Under a core template with a menu (``resolve_menu_v1``), an agent's reply names one option
(``"action": "step a little to your left"``) in place of ``steps``. This module turns that option
into a plan in the existing step format (:class:`~negsim.resolution.reply.Step`), so that the
executor, the replay, ``code_plan`` and the analyses read it as they read any plan. The agent
never sees a number: the amounts are in the table, a config file (``configs/resolution/
menu_table_v1.yaml``), and the plan given is recorded in the decision point as usual.

**The kinds of plan** a table option may have:

- ``carry_on``: no steps (``[]``), exactly a free-step reply's "carry on as you are";
- ``slow``: one step at ``speed_factor`` x the agent's usual speed, until the table's event;
- ``wait``: one step standing still (``speed_mps`` 0) for ``seconds``;
- ``sidestep``: one step that moves ``metres`` to the ``to`` side of the line walked along, then
  walks on parallel to it (``resolve_v8``'s sidestep, at its 30 degrees, at the usual speed);
- ``back_up``: one step walking backwards ``metres``, at the agent's backing speed (D1).

**As far as the wall allows** (AS3). A sidestep is never planned further than the room on that
side: the distance from the agent's centre to the wall, across its path, less its body radius
(less ``WALL_MARGIN_M``). With less room than ``MIN_SIDESTEP_M`` there is no sidestep: the plan
is ``[]`` and the reply is flagged ``no_room:<side>``. A shortened sidestep is flagged
``capped_by_wall:<side>``. With no wall in range on that side, nothing is capped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional

from ..configutil import ConfigError, load_yaml, resolve_path

KINDS = ("carry_on", "slow", "wait", "sidestep", "back_up")
SIDES = ("left", "right")
#: A sidestep planned up to the wall stops this far short of touching it (m). **[design]**: ORCA
#: keeps a body off a wall by its own margin, and a sidestep that cannot reach its distance never
#: ends; 0.05 m is a numerical allowance, not a behaviour.
WALL_MARGIN_M = 0.05
#: Less room than this to a side and a sidestep there is not planned at all (m). **[design]**
MIN_SIDESTEP_M = 0.05


def normalise(name: str) -> str:
    """An option's name as matched: lower case, single spaces, no surrounding quotes or full stop."""
    text = re.sub(r"\s+", " ", name.strip().lower())
    return text.strip(" \"'").rstrip(".").strip()


@dataclass(frozen=True)
class Option:
    name: str
    kind: str
    speed_factor: Optional[float] = None
    until: Optional[str] = None
    seconds: Optional[float] = None
    to: Optional[str] = None
    metres: Optional[float] = None

    def as_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


def _positive(raw: Mapping[str, Any], key: str, where: str) -> float:
    value = raw.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ConfigError(f"{where}.{key}: a positive number, got {value!r}")
    return float(value)


def _option(name: str, raw: Any, where: str) -> Option:
    if not isinstance(raw, Mapping):
        raise ConfigError(f"{where}: a mapping, got {raw!r}")
    kind = raw.get("plan")
    if kind not in KINDS:
        raise ConfigError(f"{where}.plan: one of {KINDS}, got {kind!r}")
    allowed = {
        "carry_on": {"plan"}, "slow": {"plan", "speed_factor", "until"}, "wait": {"plan", "seconds"},
        "sidestep": {"plan", "to", "metres"}, "back_up": {"plan", "metres"},
    }[kind]
    extra = set(raw) - allowed
    if extra:
        raise ConfigError(f"{where}: unknown keys {sorted(extra)} for a {kind} plan")
    if kind == "slow":
        factor = _positive(raw, "speed_factor", where)
        if factor >= 1.0:
            raise ConfigError(f"{where}.speed_factor: below 1, got {factor}")
        until = raw.get("until")
        if not isinstance(until, str) or not until:
            raise ConfigError(f"{where}.until: an event name, got {until!r}")
        return Option(name, kind, speed_factor=factor, until=until)
    if kind == "wait":
        return Option(name, kind, seconds=_positive(raw, "seconds", where))
    if kind == "sidestep":
        if raw.get("to") not in SIDES:
            raise ConfigError(f"{where}.to: one of {SIDES}, got {raw.get('to')!r}")
        return Option(name, kind, to=raw["to"], metres=_positive(raw, "metres", where))
    if kind == "back_up":
        return Option(name, kind, metres=_positive(raw, "metres", where))
    return Option(name, kind)


@dataclass(frozen=True)
class Menu:
    """A table of options, in the order the template lists them."""

    key: str
    options: tuple[Option, ...]

    @classmethod
    def load(cls, path: Path | str) -> "Menu":
        raw = load_yaml(resolve_path(path))
        where = str(path).replace("\\", "/")
        if raw.get("type") != "action_menu" or raw.get("schema_version") != 1:
            raise ConfigError(f"{where}: expected type action_menu, schema_version 1")
        options = raw.get("options")
        if not isinstance(options, Mapping) or not options:
            raise ConfigError(f"{where}.options: a non-empty mapping of option names to plans")
        built = []
        for name, entry in options.items():
            if normalise(str(name)) != str(name):
                raise ConfigError(f"{where}.options: {name!r} is not written as it is matched ({normalise(str(name))!r})")
            built.append(_option(str(name), entry, f"{where}.options.{name}"))
        return cls(Path(where).stem, tuple(built))

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(option.name for option in self.options)

    def find(self, name: str) -> Optional[Option]:
        wanted = normalise(name)
        return next((option for option in self.options if option.name == wanted), None)

    def events(self) -> tuple[str, ...]:
        return tuple(option.until for option in self.options if option.until is not None)

    def steps_for(
        self, option: Option, usual_speed_mps: float, room_m: Mapping[str, Optional[float]], radius_m: float,
    ) -> tuple[tuple[Any, ...], tuple[str, ...]]:
        """The plan of ``option`` for an agent walking at ``usual_speed_mps`` by habit, with
        ``room_m`` (centre to wall across its path, None with no wall in range) on each side and a
        body of ``radius_m``. Returns the steps and any flags."""
        from .reply import Sidestep, Step, Until  # here: reply imports this module

        if option.kind == "carry_on":
            return (), ()
        if option.kind == "slow":
            return (Step(speed_mps=round(usual_speed_mps * option.speed_factor, 2), until=Until(event=option.until)),), ()
        if option.kind == "wait":
            return (Step(speed_mps=0.0, until=Until(seconds=option.seconds)),), ()
        if option.kind == "back_up":
            return (Step(back_up_m=option.metres),), ()
        wall = room_m.get(option.to)
        if wall is None:
            return (Step(sidestep=Sidestep(option.to, option.metres)),), ()
        room = wall - radius_m - WALL_MARGIN_M
        if room < MIN_SIDESTEP_M:
            return (), (f"no_room:{option.to}",)
        if room < option.metres:
            return (Step(sidestep=Sidestep(option.to, round(room, 2))),), (f"capped_by_wall:{option.to}",)
        return (Step(sidestep=Sidestep(option.to, option.metres)),), ()


_CACHE: dict[str, Menu] = {}


def load_menu(path: str) -> Menu:
    """A menu table by its path (relative to the package root), loaded once."""
    if path not in _CACHE:
        _CACHE[path] = Menu.load(path)
    return _CACHE[path]


def menu_context(simulation: Any, agent: int) -> dict[str, Any]:
    """What the conversion needs of ``agent`` now: its usual speed, its body radius, and the room
    to each wall across its path (``avoidance.perception.environment_features``)."""
    from ..avoidance.perception import environment_features

    a = simulation.world.agents[agent]
    features = environment_features(a, simulation.world.obstacles, (), simulation.environment_range)
    return {
        "usual_speed_mps": a.spec.preferred_speed,
        "radius_m": a.spec.radius,
        "room_left_m": features.free_width_left_m,
        "room_right_m": features.free_width_right_m,
    }
