"""The pairwise perception factors (issue #61, RF-6; ``docs/pairwise-factors.md``;
``docs/resolution.md``, D2).

A pairwise factor is how one person sees another, so it belongs to a pair of people, not to one
person, and it need not be mutual:

============================  ========================  =========  =================================
Factor                        Levels (base first)       Mutual     Design factors
============================  ========================  =========  =================================
``perceived_attractiveness``  unremarkable, attractive  no         ``attractiveness_0_sees_1``,
                                                                   ``attractiveness_1_sees_0``
``familiarity``               strangers, acquaintances  yes        ``familiarity``
============================  ========================  =========  =================================

**The block** (a session's ``pairwise``, in issue #61's format)::

    pairwise:
      agents: [1, 0]              # which agent each row (and column) is; without it, 0, 1, ...
      perceived_attractiveness:   # row = who is looking, column = who is seen
        - [null, attractive]      # the agent of row 0 finds the agent of row 1 attractive
        - [unremarkable, null]    # the agent of row 1 does not find the agent of row 0 attractive
      familiarity: strangers      # the same for everyone in the block

A design's session lists person 1 first and person 2 second (``agents``), so
``attractiveness_0_sees_1`` is person 1 looking at person 2. A ``null`` off the diagonal was not
designed: it renders nothing and has no value in the outcome row.

**Who is told what** (:meth:`PairwiseFactors.lines_for`): an observer is told, of each other person
in the block, its own row's entry and the familiarity, while the factor's visibility switch is on
(``visible``; on unless the design switches it off). With a switch on, both levels have a line;
with it off, neither has. The view attaches the lines only to people in view (RF-17), and the core
template prints them only in full detail (within 5 m, D2), so a person who is only heard, or who
is further away, gets none. Nobody is ever told another person's row.

**Only in the prompt.** Neither factor changes anything in the simulator.

**Perceived attractiveness is gated.** It is off unless a design names it; a paid run with it is
refused until ``CLAUDE.md`` records the supervisor's ethics sign-off (``negsim.ethics``); and no
rule may read it (``negsim.rules.fields``, ``protected_attribute``). It stays in the outcome rows,
for RF-8's factor analysis and the factor-to-decision mapping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

from ..configutil import ConfigError, check_keys
from ..negotiation.prompts import check_template_data, load_template_data

KIND_PAIRWISE = "resolution_pairwise"
PAIRWISE_TEMPLATE = "resolve_pairwise_v1"

ATTRACTIVENESS = "perceived_attractiveness"
FAMILIARITY = "familiarity"
#: Each pairwise factor's two levels, the base level first; the order is the order of the lines.
LEVELS: dict[str, tuple[str, str]] = {
    ATTRACTIVENESS: ("unremarkable", "attractive"),
    FAMILIARITY: ("strangers", "acquaintances"),
}
#: Each factor's visibility switch, a design factor: off, it has no line at all.
SWITCHES: dict[str, str] = {ATTRACTIVENESS: "attractiveness_visible", FAMILIARITY: "familiarity_visible"}
#: The design factors: the factor each sets, and for the matrix the row (who looks) and the
#: column (who is seen), 0 for person 1 and 1 for person 2.
DESIGN_FACTORS: dict[str, tuple[str, Optional[int], Optional[int]]] = {
    "attractiveness_0_sees_1": (ATTRACTIVENESS, 0, 1),
    "attractiveness_1_sees_0": (ATTRACTIVENESS, 1, 0),
    "familiarity": (FAMILIARITY, None, None),
}
#: The design factors of perceived attractiveness: a design that names one switches it on.
ATTRACTIVENESS_FACTORS = tuple(name for name, (factor, _, _) in DESIGN_FACTORS.items() if factor == ATTRACTIVENESS)


def numeric(factor: str, level: Optional[str]) -> Optional[int]:
    """A level as RF-8 reads it: 0 for the base level, 1 for the other, ``None`` if not designed."""
    return None if level is None else LEVELS[factor].index(level)


def block_for(cell: Mapping[str, Any], persons: Sequence[int]) -> Optional[dict[str, Any]]:
    """The pairwise block of a design's cell, with ``persons`` (person 1's agent, person 2's) as
    its rows; ``None`` if the cell varies no pairwise factor."""
    names = [name for name in DESIGN_FACTORS if name in cell]
    if not names:
        return None
    block: dict[str, Any] = {"agents": [int(agent) for agent in persons]}
    if any(name in cell for name in ATTRACTIVENESS_FACTORS):
        matrix: list[list[Optional[str]]] = [[None] * len(persons) for _ in persons]
        for name in ATTRACTIVENESS_FACTORS:
            if name in cell:
                _, row, column = DESIGN_FACTORS[name]
                matrix[row][column] = cell[name]
        block[ATTRACTIVENESS] = matrix
    if "familiarity" in cell:
        block[FAMILIARITY] = cell["familiarity"]
    return block


# --- the template -------------------------------------------------------------------------------


class PairwiseTemplate:
    """``resolve_pairwise_v<n>``: one line per factor and level, checked on loading: every factor
    of :data:`LEVELS`, in order, each with exactly its levels, in order, each a line of text."""

    def __init__(self, key: str, data: Mapping[str, Any], sha256: str):
        check_template_data(key, data)
        if data.get("kind") != KIND_PAIRWISE:
            raise ConfigError(f"prompt template {key!r} is of kind {data.get('kind')!r}, not {KIND_PAIRWISE!r}")
        lines = data["lines"]
        if not isinstance(lines, Mapping) or list(lines) != list(LEVELS):
            raise ConfigError(f"pairwise template {key!r}: lines must be given for {list(LEVELS)}, in that order")
        for factor, by_level in lines.items():
            if not isinstance(by_level, Mapping) or tuple(by_level) != LEVELS[factor]:
                raise ConfigError(f"pairwise template {key!r}: {factor} must have the levels {list(LEVELS[factor])}, in that order")
            for level, line in by_level.items():
                if not isinstance(line, str) or not line.strip():
                    raise ConfigError(f"pairwise template {key!r}: {factor}.{level} must be a line of text")
        self.key, self.data, self.sha256 = key, data, sha256

    @classmethod
    def load(cls, key: str = PAIRWISE_TEMPLATE) -> "PairwiseTemplate":
        data, digest = load_template_data(key, KIND_PAIRWISE)
        return cls(key, data, digest)

    def identity(self) -> dict[str, str]:
        return {"key": self.key, "sha256": self.sha256}

    def line(self, factor: str, level: str) -> str:
        if level not in self.data["lines"][factor]:
            raise ConfigError(f"pairwise template {self.key!r}: {factor} has no level {level!r}")
        return self.data["lines"][factor][level]

    def longest(self, factors: Sequence[str]) -> tuple[str, ...]:
        """The longest line of each pairwise factor that ``factors`` (a design's) set: what the
        cost preview counts under every person in view."""
        found = {DESIGN_FACTORS[name][0] for name in factors if name in DESIGN_FACTORS}
        return tuple(max(self.data["lines"][factor].values(), key=len) for factor in LEVELS if factor in found)


# --- one session --------------------------------------------------------------------------------


def _level(value: Any, factor: str, where: str) -> Optional[str]:
    if value is not None and value not in LEVELS[factor]:
        raise ConfigError(f"{where}: one of {list(LEVELS[factor])}, or null, got {value!r}")
    return value


@dataclass(frozen=True)
class PairwiseFactors:
    """One session's pairwise factors: the agents of the rows (``agents``), the matrix of
    perceived attractiveness (``attractiveness``, by row then column; ``None`` if not designed),
    the familiarity, and the visibility switches (``visible``, by factor; on when left out).
    ``template`` is needed only for the lines."""

    agents: tuple[int, ...]
    attractiveness: Optional[tuple[tuple[Optional[str], ...], ...]] = None
    familiarity: Optional[str] = None
    visible: Mapping[str, bool] = field(default_factory=dict)
    template: Optional[PairwiseTemplate] = None

    def __post_init__(self) -> None:
        if len(self.agents) < 2 or len(set(self.agents)) != len(self.agents):
            raise ConfigError(f"pairwise.agents: two or more distinct agents, got {list(self.agents)}")
        if self.attractiveness is not None:
            n = len(self.agents)
            if len(self.attractiveness) != n or any(len(row) != n for row in self.attractiveness):
                raise ConfigError(f"pairwise.{ATTRACTIVENESS}: a {n} x {n} matrix, one row and one column per agent")
            for k, row in enumerate(self.attractiveness):
                if row[k] is not None:
                    raise ConfigError(f"pairwise.{ATTRACTIVENESS}[{k}][{k}]: null; nobody is seen by themselves")
                for j, value in enumerate(row):
                    _level(value, ATTRACTIVENESS, f"pairwise.{ATTRACTIVENESS}[{k}][{j}]")
        _level(self.familiarity, FAMILIARITY, f"pairwise.{FAMILIARITY}")
        unknown = sorted(set(self.visible) - set(LEVELS))
        if unknown:
            raise ConfigError(f"pairwise visibility for {unknown}; the pairwise factors are {list(LEVELS)}")

    @classmethod
    def from_block(
        cls, raw: Any, template: Optional[PairwiseTemplate] = None, visible: Optional[Mapping[str, bool]] = None, where: str = "pairwise",
    ) -> "PairwiseFactors":
        """Load a block in issue #61's format (the module's docstring). Without ``agents`` the rows
        are agents 0, 1, ... by id."""
        block = check_keys(raw, where, (), ("agents", ATTRACTIVENESS, FAMILIARITY))
        matrix = block.get(ATTRACTIVENESS)
        if matrix is not None and (not isinstance(matrix, list) or not all(isinstance(row, list) for row in matrix)):
            raise ConfigError(f"{where}.{ATTRACTIVENESS}: a list of rows, each a list (row = who is looking, column = who is seen)")
        agents = block.get("agents")
        if agents is None:
            agents = list(range(len(matrix) if matrix is not None else 2))
        if not isinstance(agents, list) or any(isinstance(a, bool) or not isinstance(a, int) for a in agents):
            raise ConfigError(f"{where}.agents: a list of agent ids, got {agents!r}")
        return cls(
            agents=tuple(agents),
            attractiveness=None if matrix is None else tuple(tuple(row) for row in matrix),
            familiarity=block.get(FAMILIARITY),
            visible=dict(visible or {}),
            template=template,
        )

    def _shown(self, factor: str) -> bool:
        return self.visible.get(factor, True)

    def perceives(self, observer: int, seen: int) -> dict[str, Optional[str]]:
        """How ``observer`` sees ``seen``, by factor: its level, or ``None`` if not designed (or if
        either is not in the block)."""
        if observer not in self.agents or seen not in self.agents or observer == seen:
            return {factor: None for factor in LEVELS}
        row, column = self.agents.index(observer), self.agents.index(seen)
        return {
            ATTRACTIVENESS: None if self.attractiveness is None else self.attractiveness[row][column],
            FAMILIARITY: self.familiarity,
        }

    def lines_for(self, observer: int) -> dict[int, tuple[str, ...]]:
        """What ``observer`` is told of each other person in the block, by agent id: the view's
        ``pairwise_lines`` for this observer, and for nobody else. Empty for anyone not in it."""
        if self.template is None:
            raise ValueError("the pairwise lines need the template")
        found = {}
        for seen in self.agents:
            levels = self.perceives(observer, seen)
            lines = tuple(
                self.template.line(factor, levels[factor]) for factor in LEVELS
                if levels[factor] is not None and self._shown(factor)
            )
            if lines:
                found[seen] = lines
        return found

    def values(self, observer: int, seen: int) -> dict[str, Optional[int]]:
        """:meth:`perceives` as 0 or 1 (RF-8): the level, whether or not the observer was told it."""
        return {factor: numeric(factor, level) for factor, level in self.perceives(observer, seen).items()}

    def block(self) -> dict[str, Any]:
        """The block, in issue #61's format, with its ``agents``."""
        found: dict[str, Any] = {"agents": list(self.agents)}
        if self.attractiveness is not None:
            found[ATTRACTIVENESS] = [list(row) for row in self.attractiveness]
        if self.familiarity is not None:
            found[FAMILIARITY] = self.familiarity
        return found

    def as_dict(self) -> dict[str, Any]:
        """What a session record keeps: the template, the block, and the switches."""
        return {
            **({"template": self.template.identity()} if self.template is not None else {}),
            **self.block(),
            "visible": {factor: self._shown(factor) for factor in LEVELS if factor in self.block()},
        }
