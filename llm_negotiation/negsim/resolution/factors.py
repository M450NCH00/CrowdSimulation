"""The core factors and the situational factors (issue #60, RF-5; ``docs/resolution.md``, D1, D2,
D7 and D15).

**The core factors** are seven person attributes, declared in the persona table
(``negsim.personas.schema.ATTRIBUTES``, each with two ``levels``, the base level first):

=================  =========================  ==========  ==========================================
Attribute          Levels                     Observable  Where its lines go
=================  =========================  ==========  ==========================================
``urgency``        routine, urgent            no          the errand line of ABOUT YOU (the design
                                                          picks the errand); no line of its own
``mobility_aid``   none, cane                 yes         ABOUT YOU; WHO YOU CAN SEE for others
``load``           none, large_suitcase       yes         the same; and a wider body (below)
``distraction``    none, phone                yes         the same
``assertiveness``  gives_way, holds_ground    no          ABOUT YOU
``residence``      local, visitor             no          ABOUT YOU
``memory_note``    none, bad_experience       no          YOUR NOTES (a designed note, D7)
=================  =========================  ==========  ==========================================

**The situational factors** (:data:`SITUATIONS`, the session's choice, recorded in
``WORK_LOG-60.md``) describe the setting: everyone in a session gets the same level and the same
line, after the scenario's lines in WHERE YOU ARE. ``surroundings`` (quiet, busy) also sets the
LLM's hearing range (``llm_view.hearing_range_m``, RF-17); ``time_of_day`` (daytime, late_night)
is in the prompt only.

The wording is ``resolve_factors_v1``'s (a frozen template of kind ``resolution_factors``); the
core template places it verbatim (``View``: ``Me.factor_lines``, ``notes``,
``SeenPerson.factor_lines`` and ``place``). A level with no line renders nothing.

**What someone else sees** of a person (:meth:`SessionFactors.seen`): the ``other`` line of an
observable attribute whose visibility switch (``<name>_visible``, a design factor) is on. The
view adds it under that person only when they are in view (RF-17), and the core template prints
it only in full detail (within 5 m, D2). An unobservable attribute has no ``other`` line, so it
can never reach another person's view.

**Only ``load`` and ``surroundings`` change anything outside the prompt.** ``load`` widens the
person's body by ``load.large_suitcase.width_added_m`` (:class:`FactorValues`), fixed from the
start of the run and never changed during it (D1): the run's scenario gets a per-agent radius
override (:func:`with_bodies`), the way ``docs/parameters.md``, section 5, links a persona to a
physical change, and the session record keeps it so that both replays and plain ORCA run the
same bodies. Everything else exists only in the prompt: the simulator does not slow a person with
a cane, narrow the view of one looking at a phone, or fill a busy corridor. A factor's effect is
therefore an effect on the decision, not on the physics.
"""

from __future__ import annotations

import copy
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ..configutil import PACKAGE_ROOT, ConfigError, as_number, check_keys, load_yaml
from ..negotiation.prompts import check_template_data, load_template_data
from ..personas.schema import ATTRIBUTES, FACTOR_ATTRIBUTES

KIND_FACTORS = "resolution_factors"
FACTOR_TEMPLATE = "resolve_factors_v1"
FACTOR_VALUES_CONFIG = PACKAGE_ROOT / "configs" / "resolution" / "factors_v1.yaml"

#: The situational factors chosen in issue #60 (task 7), each with its two levels, the base first.
SITUATIONS: dict[str, tuple[str, str]] = {
    "surroundings": ("quiet", "busy"),
    "time_of_day": ("daytime", "late_night"),
}
#: The observable core factors, each with its visibility switch (a design factor).
SWITCHES: dict[str, str] = {name: f"{name}_visible" for name in FACTOR_ATTRIBUTES if ATTRIBUTES[name].observable}
#: The keys a level of an attribute may have in the template.
LINE_KINDS = ("self", "other", "note")


def levels_of(name: str) -> tuple[str, ...]:
    """The two levels of a core or situational factor, the base level first."""
    if name in ATTRIBUTES and ATTRIBUTES[name].levels:
        return ATTRIBUTES[name].levels
    if name in SITUATIONS:
        return SITUATIONS[name]
    raise KeyError(f"{name!r} is neither a core nor a situational factor")


# --- the template -------------------------------------------------------------------------------


class FactorTemplate:
    """``resolve_factors_v<n>``: one entry per attribute and level, and the situational lines.

    Loading checks it against the schema: every core factor, with exactly its levels in order;
    an ``other`` line only for an observable attribute; every situational factor and level.
    """

    def __init__(self, key: str, data: Mapping[str, Any], sha256: str):
        check_template_data(key, data)
        if data.get("kind") != KIND_FACTORS:
            raise ConfigError(f"prompt template {key!r} is of kind {data.get('kind')!r}, not {KIND_FACTORS!r}")
        attributes, situations = data["attributes"], data["situations"]
        if not isinstance(attributes, Mapping) or list(attributes) != list(FACTOR_ATTRIBUTES):
            raise ConfigError(f"factor template {key!r}: attributes must be {list(FACTOR_ATTRIBUTES)}, in that order")
        for name, levels in attributes.items():
            spec = ATTRIBUTES[name]
            if not isinstance(levels, Mapping) or tuple(levels) != spec.levels:
                raise ConfigError(f"factor template {key!r}: {name} must have the levels {list(spec.levels)}, in that order")
            for level, lines in levels.items():
                unknown = sorted(set(lines or {}) - set(LINE_KINDS))
                if unknown:
                    raise ConfigError(f"factor template {key!r}: {name}.{level} has unknown key(s) {unknown}; known: {list(LINE_KINDS)}")
                if (lines or {}).get("other") and not spec.observable:
                    raise ConfigError(f"factor template {key!r}: {name} is not observable, so {name}.{level} may have no 'other' line")
        if not isinstance(situations, Mapping) or list(situations) != list(SITUATIONS):
            raise ConfigError(f"factor template {key!r}: situations must be {list(SITUATIONS)}, in that order")
        for name, lines in situations.items():
            if not isinstance(lines, Mapping) or tuple(lines) != SITUATIONS[name]:
                raise ConfigError(f"factor template {key!r}: {name} must have the levels {list(SITUATIONS[name])}, in that order")
        self.key, self.data, self.sha256 = key, data, sha256

    @classmethod
    def load(cls, key: str = FACTOR_TEMPLATE) -> "FactorTemplate":
        data, digest = load_template_data(key, KIND_FACTORS)
        return cls(key, data, digest)

    def identity(self) -> dict[str, str]:
        return {"key": self.key, "sha256": self.sha256}

    def line(self, attribute: str, level: str, kind: str) -> Optional[str]:
        """An attribute's ``self``, ``other`` or ``note`` line at a level, or ``None``."""
        if level not in self.data["attributes"][attribute]:
            raise ConfigError(f"factor template {self.key!r}: {attribute} has no level {level!r}")
        return (self.data["attributes"][attribute][level] or {}).get(kind) or None

    def situation(self, name: str, level: str) -> str:
        if level not in self.data["situations"][name]:
            raise ConfigError(f"factor template {self.key!r}: {name} has no level {level!r}")
        return self.data["situations"][name][level]

    def longest(self, names: Sequence[str]) -> dict[str, tuple[str, ...]]:
        """The longest line of each kind that ``names`` (factors of a design) can render: what the
        cost preview counts. Keys ``self``, ``note``, ``other`` and ``place``."""
        found: dict[str, list[str]] = {"self": [], "note": [], "other": [], "place": []}
        for name in names:
            if name in FACTOR_ATTRIBUTES:
                for kind in LINE_KINDS:
                    lines = [self.line(name, level, kind) for level in ATTRIBUTES[name].levels]
                    lines = [line for line in lines if line]
                    if lines:
                        found[kind].append(max(lines, key=len))
            elif name in SITUATIONS:
                found["place"].append(max((self.situation(name, level) for level in SITUATIONS[name]), key=len))
        return {kind: tuple(lines) for kind, lines in found.items()}


# --- the values ---------------------------------------------------------------------------------


@dataclass(frozen=True)
class FactorValues:
    """The numbers of ``configs/resolution/factors_v1.yaml``: what the two factors that act
    outside the prompt do. Every value is ``[placeholder]`` (``docs/parameters.md``, section 8.7)."""

    load_width_added_m: float
    hearing_range_m: Mapping[str, float]  # by level of ``surroundings``

    def __post_init__(self) -> None:
        if set(self.hearing_range_m) != set(SITUATIONS["surroundings"]):
            raise ConfigError(f"factor values: a hearing range for each level of surroundings, {list(SITUATIONS['surroundings'])}")

    @classmethod
    def from_mapping(cls, raw: Any, where: str = "factor values") -> "FactorValues":
        data = check_keys(raw, where, ("schema_version", "load", "surroundings"))
        if data["schema_version"] != 1:
            raise ConfigError(f"{where}: schema_version 1 is the only one, got {data['schema_version']!r}")
        load = check_keys(data["load"], f"{where}.load", ("large_suitcase",))
        suitcase = check_keys(load["large_suitcase"], f"{where}.load.large_suitcase", ("width_added_m",))
        surroundings = check_keys(data["surroundings"], f"{where}.surroundings", SITUATIONS["surroundings"])
        hearing = {}
        for level in SITUATIONS["surroundings"]:
            block = check_keys(surroundings[level], f"{where}.surroundings.{level}", ("hearing_range_m",))
            hearing[level] = as_number(block["hearing_range_m"], f"{where}.surroundings.{level}.hearing_range_m", minimum=0.0, strict_minimum=True)
        return cls(
            load_width_added_m=as_number(suitcase["width_added_m"], f"{where}.load.large_suitcase.width_added_m", minimum=0.0),
            hearing_range_m=hearing,
        )

    @classmethod
    def load(cls, path: Path | str = FACTOR_VALUES_CONFIG) -> "FactorValues":
        return cls.from_mapping(load_yaml(path), Path(path).name)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


# --- one session --------------------------------------------------------------------------------


@dataclass(frozen=True)
class SessionFactors:
    """One session's factors: each person's levels (``people``, by agent id, only the core
    factors the design varies), the visibility switches of the observable ones (``visible``),
    and the situational levels (``situation``). Anyone without an entry (the others of a crowd
    encounter) has no factor line."""

    template: FactorTemplate
    people: Mapping[int, Mapping[str, str]]
    visible: Mapping[str, bool]
    situation: Mapping[str, str]

    def __post_init__(self) -> None:
        for agent, levels in self.people.items():
            for name, level in levels.items():
                if name not in FACTOR_ATTRIBUTES:
                    raise ConfigError(f"person {agent}: {name!r} is not a core factor; the core factors are {list(FACTOR_ATTRIBUTES)}")
                if level not in ATTRIBUTES[name].levels:
                    raise ConfigError(f"person {agent}: {name} is one of {list(ATTRIBUTES[name].levels)}, got {level!r}")
        unknown = sorted(set(self.visible) - set(SWITCHES))
        if unknown:
            raise ConfigError(f"visibility switches for {unknown}, which are not observable core factors; those are {list(SWITCHES)}")
        for name, level in self.situation.items():
            if name not in SITUATIONS or level not in SITUATIONS[name]:
                raise ConfigError(f"situational factor {name}={level!r}: known {SITUATIONS}")

    def _levels(self, agent: int) -> Mapping[str, str]:
        return self.people.get(agent, self.people.get(str(agent), {}))  # type: ignore[call-overload]

    def own(self, agent: int) -> tuple[str, ...]:
        """ABOUT YOU: the person's own lines, in the schema's order."""
        levels = self._levels(agent)
        return tuple(line for name in FACTOR_ATTRIBUTES if name in levels and (line := self.template.line(name, levels[name], "self")))

    def notes(self, agent: int) -> tuple[str, ...]:
        """YOUR NOTES: the person's designed notes."""
        levels = self._levels(agent)
        return tuple(line for name in FACTOR_ATTRIBUTES if name in levels and (line := self.template.line(name, levels[name], "note")))

    def seen(self, agent: int) -> tuple[str, ...]:
        """What someone who sees ``agent`` is told of its factors: the observable ones whose switch
        is on (on unless the design switches it off)."""
        levels = self._levels(agent)
        return tuple(
            line for name in FACTOR_ATTRIBUTES
            if name in levels and name in SWITCHES and self.visible.get(name, True)
            and (line := self.template.line(name, levels[name], "other"))
        )

    def seen_lines(self) -> dict[int, tuple[str, ...]]:
        """:meth:`seen` for everyone who has a line: the view's ``factor_lines``."""
        return {int(agent): lines for agent in self.people if (lines := self.seen(int(agent)))}

    def place(self) -> tuple[str, ...]:
        """WHERE YOU ARE: the situational lines, the same for everyone."""
        return tuple(self.template.situation(name, self.situation[name]) for name in SITUATIONS if name in self.situation)

    def hearing_range_m(self, values: FactorValues) -> Optional[float]:
        """The hearing range ``surroundings`` sets, or ``None`` if the design does not vary it."""
        level = self.situation.get("surroundings")
        return None if level is None else values.hearing_range_m[level]

    def bodies(self, radius_m: Mapping[int, float], values: FactorValues) -> dict[str, dict[str, Any]]:
        """The bodies ``load`` widens: each loaded person's radius, from its radius in the run
        (``radius_m``, by agent id) and the added width. Empty when nobody is loaded."""
        widened = {}
        for agent in sorted(int(a) for a in self.people):
            if self._levels(agent).get("load") == "large_suitcase":
                radius = radius_m[agent] + values.load_width_added_m / 2.0
                widened[str(agent)] = {"radius_m": round(radius, 6), "because": "load=large_suitcase"}
        return widened

    def as_dict(self) -> dict[str, Any]:
        return {
            "template": self.template.identity(),
            "people": {str(agent): dict(levels) for agent, levels in sorted(self.people.items(), key=lambda item: int(item[0]))},
            "visible": dict(self.visible),
            "situation": dict(self.situation),
        }


# --- a wider body -------------------------------------------------------------------------------


def with_bodies(plan: Any, bodies: Optional[Mapping[str, Mapping[str, Any]]]) -> Any:
    """``plan`` (an ``AvoidanceRunPlan``) with the radii of ``bodies`` (agent id, as text, to
    ``{"radius_m": r}``) set as per-agent overrides in its scenario config, for the whole run.
    With no bodies, ``plan`` itself."""
    if not bodies:
        return plan
    config = copy.deepcopy(dict(plan.scenario_config))
    if "agent_types" not in config:
        raise ConfigError(f"scenario {config.get('type')!r} has no agent types, so a body cannot be widened in it")
    agents = dict(config.get("agents") or {})
    overrides = {int(agent): dict(entry or {}) for agent, entry in (agents.get("overrides") or {}).items()}
    for agent, body in bodies.items():
        overrides[int(agent)] = {**overrides.get(int(agent), {}), "radius": body["radius_m"]}
    agents["overrides"] = dict(sorted(overrides.items()))
    config["agents"] = agents
    return replace(plan, scenario_config=config)
