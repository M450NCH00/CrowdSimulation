"""The scenario interface, description side (``docs/resolution.md``, D16).

A scenario is a plug-in; the pipeline never names one. On the description side a scenario
supplies, from a frozen scenario template ``scenario_<name>_v<n>.yaml`` of kind
``resolution_scenario``:

- the lines of its WHERE YOU ARE block (``place_lines``), and any block of its own beyond it,
  such as YOUR QUEUE (``extra_blocks``);
- its ``until`` events, with their wording (``events``), which the reply format lists and the
  reply parser accepts;
- its own factor lines (``factor_lines``; RF-5 fills them).

On the execution side (issue #59, RF-4) a scenario supplies:

- what its ``until`` events mean, geometrically (:meth:`Scenario.happened`); the plan executor
  (``negsim.resolution.execute``) asks, and knows no event itself;
- its conflict zone, as when each encounter agent left it (:meth:`Scenario.zone_exits`), from
  which "who passed first" and "time to clear" are measured;
- its own outcome columns (:meth:`Scenario.outcome_columns`) and what "resolved" means for it
  (:meth:`Scenario.resolved`).

Adding a scenario adds a subclass and a template. It never edits the core template
(``resolve_v1``), the parser, the executor, or another scenario. The plug-ins themselves live in
:mod:`negsim.resolution.scenarios`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

from ..configutil import ConfigError
from ..negotiation.prompts import check_template_data, load_template_data
from ..rulegen.describe import fill
from .view import Block

KIND_SCENARIO = "resolution_scenario"


@dataclass(frozen=True)
class EventContext:
    """What a scenario is shown when the executor asks whether an event has happened: the running
    simulation (read only), whose step it is and who the partner is, when the step began, and a
    dictionary the scenario may keep notes in for the length of the step."""

    simulation: Any
    agent_id: int
    partner_id: int
    step_started_s: float
    memory: dict

    @property
    def agent(self) -> Any:
        return self.simulation.world.agents[self.agent_id]

    @property
    def partner(self) -> Any:
        return self.simulation.world.agents[self.partner_id]


class Scenario:
    """A scenario's description side. Subclasses set ``TEMPLATE`` and write ``place_lines``."""

    #: The frozen scenario template :meth:`load` reads.
    TEMPLATE: Optional[str] = None

    def __init__(self, key: str, data: Mapping[str, Any], sha256: str):
        check_template_data(key, data)
        if data.get("kind") != KIND_SCENARIO:
            raise ConfigError(f"prompt template {key!r} is of kind {data.get('kind')!r}, not {KIND_SCENARIO!r}")
        events = data["events"]
        if not isinstance(events, Mapping) or not events:
            raise ConfigError(f"scenario template {key!r}: events must name at least one event")
        self.key, self.data, self.sha256 = key, data, sha256

    @classmethod
    def load(cls, key: Optional[str] = None) -> "Scenario":
        """The scenario with its frozen template, checked against the manifest."""
        key = key or cls.TEMPLATE
        if key is None:
            raise ConfigError(f"{cls.__name__} names no template")
        data, digest = load_template_data(key, KIND_SCENARIO)
        return cls(key, data, digest)

    def identity(self) -> dict[str, str]:
        return {"key": self.key, "sha256": self.sha256}

    @property
    def events(self) -> dict[str, str]:
        """Each ``until`` event's name and the words that tell the agent what it means, in order."""
        return dict(self.data["events"])

    def place_lines(self, case: Mapping[str, Any], record: Mapping[str, Any]) -> list[str]:
        """The WHERE YOU ARE lines of an agent with perception record ``record`` in ``case``."""
        raise NotImplementedError

    def extra_blocks(self, case: Mapping[str, Any], record: Mapping[str, Any]) -> list[Block]:
        """Blocks of the scenario's own beyond WHERE YOU ARE, from its template's ``extra_blocks``."""
        return []

    def factor_lines(self, levels: Mapping[str, Any]) -> list[str]:
        """The scenario's own factor lines for these levels (RF-5), placed in WHERE YOU ARE."""
        lines = []
        for name, value in levels.items():
            if name not in self.data["factor_lines"]:
                raise ConfigError(f"scenario template {self.key!r} has no factor line {name!r}")
            line = self.data["factor_lines"][name]
            if isinstance(line, Mapping):  # one line per level
                if value not in line:
                    raise ConfigError(f"scenario template {self.key!r}: factor {name!r} has no line for {value!r}")
                lines.append(line[value])
            else:
                lines.append(fill(line, value=value))
        return lines

    # --- the execution side (issue #59) ---------------------------------------------------------

    def happened(self, event: str, context: EventContext) -> bool:
        """Whether ``event`` has happened for ``context``'s agent, on the state at the start of the
        present step."""
        raise NotImplementedError(f"{type(self).__name__} does not define the event {event!r}")

    def zone_exits(self, simulation: Any, track: Sequence[Any], agents: Sequence[int], start_step: int) -> dict[int, Optional[float]]:
        """When each of ``agents`` left the encounter's conflict zone for good (s), from the rows of
        ``track`` (``execute.TrackRow``) after ``start_step``; ``None`` for one that never did.
        ``simulation`` is the finished run, for its geometry and its agents' specs."""
        raise NotImplementedError(f"{type(self).__name__} defines no conflict zone")

    def outcome_columns(self, simulation: Any, track: Sequence[Any], agents: Sequence[int], start_step: int, general: Mapping[str, Any]) -> dict[str, Any]:
        """The scenario's own outcome columns, beside the general ones in ``general``."""
        return {}

    def resolved(self, columns: Mapping[str, Any]) -> bool:
        """Whether an encounter with these outcome columns was resolved, as this scenario means it."""
        raise NotImplementedError(f"{type(self).__name__} does not say what resolved means")
