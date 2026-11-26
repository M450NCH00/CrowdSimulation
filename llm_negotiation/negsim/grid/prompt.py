"""What an agent on the grid is told, and its prompt (issue #140, RF-51; ``docs/action-space.md``,
sections 7 and 8).

**The templates** are the grid's own: ``negsim/grid/templates/``, frozen, with their own
``MANIFEST.json`` (AS1: no existing manifest changes). Two of them, silent only (AS2):

- ``resolve_grid_v1``: the agent's own left and right;
- ``resolve_grid_abs_v1``: the absolute frame of RF-48 (AS5 as revised by the user on 2026-11-26),
  with lanes numbered from the blue wall ("lane 1 is next to the blue wall").

Their fixed text is ``resolve_menu_v1``'s (or ``resolve_menu_abs_v1``'s) silent section and ACTIONS
block, word for word; the view is the grid's, in cells and lanes.

**The view** (:class:`GridView`) holds, as data, what one walker perceives at a decision point.
D2's limits are RF-40's (``configs/resolution/llm_view_v1.yaml``): a person is in view within the
seeing range and half-angle, measured between cell centres (``negsim.resolution.perceive.in_cone``).
Nothing in it is what the walker cannot perceive.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional

import yaml

from ..configutil import ConfigError
from ..negotiation.prompts import template_sha256
from ..resolution.menu import Menu, load_menu
from ..rulegen.describe import fill, speed

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
MANIFEST = TEMPLATES_DIR / "MANIFEST.json"
KIND = "grid_resolution"
FRAMES = ("own", "absolute")

#: What a person in view is doing, as the grid shows it.
MOTIONS = ("towards", "away", "same_way", "still", "backing")
#: What a person did since the walker last looked (D5), besides moving lanes.
CHANGES = ("slowed_down", "sped_up", "stopped", "started_walking", "backing_up", "came_into_view")
OUTCOMES = ("completed", "ongoing", "replaced")


@dataclass(frozen=True)
class GridMe:
    preferred_speed_mps: float
    speed_mps: float
    motion: str  # walking, still or backing
    age: Optional[int] = None
    gender: Optional[str] = None
    errand: Optional[str] = None
    factor_lines: tuple[str, ...] = ()


@dataclass(frozen=True)
class GridSeen:
    """One person in view. ``cells_ahead``: rows ahead along the walker's way (negative: behind).
    ``lanes_left``: lanes to the walker's own left (negative: right). ``lane``: their lane, 0 at -y.
    ``lanes_moved_left`` and ``lanes_moved_plus_y``: how far they moved across since the walker last
    looked, in its own frame and towards +y (wall a)."""

    label: int
    cells_ahead: int
    lanes_left: int
    lane: int
    motion: str
    speed_mps: float
    age: Optional[int] = None
    gender: Optional[str] = None
    changes: tuple[str, ...] = ()
    lanes_moved_left: int = 0
    lanes_moved_plus_y: int = 0
    factor_lines: tuple[str, ...] = ()
    pairwise_lines: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.motion not in MOTIONS:
            raise ValueError(f"motion: one of {MOTIONS}, got {self.motion!r}")
        unknown = [c for c in self.changes if c not in CHANGES]
        if unknown:
            raise ValueError(f"changes: unknown {unknown}")


@dataclass(frozen=True)
class GridDone:
    """One earlier decision: how far the walker has moved since, across (to its own left, and
    towards +y) and back (cells), and what became of the plan."""

    ago_s: float
    intent: str
    outcome: str
    lanes_left: int = 0
    lanes_plus_y: int = 0
    cells_back: int = 0

    def __post_init__(self) -> None:
        if self.outcome not in OUTCOMES:
            raise ValueError(f"outcome: one of {OUTCOMES}, got {self.outcome!r}")


@dataclass(frozen=True)
class GridView:
    agent_id: int
    decision_point: int
    tick: int
    me: GridMe
    lanes: int
    lane: int  # the walker's lane, 0 at -y
    direction: int  # +1 heading +x, -1 heading -x (never told; it sets the own frame)
    cell_m: float
    tick_s: float
    situation_lines: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    seen: tuple[GridSeen, ...] = ()
    history: tuple[GridDone, ...] = ()
    time_to_meet: Optional[tuple[int, float]] = None  # (label, seconds)
    template: Mapping[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_manifest() -> dict[str, dict[str, Any]]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["templates"]


def _words(n: int, one: str, many: str, numbers: Mapping[Any, str]) -> str:
    word = numbers.get(n, numbers.get(str(n), str(n)))
    return f"{word} {one if n == 1 else many}"


class GridTemplate:
    """A grid template, frozen: its hash is checked against the grid's own manifest when loaded."""

    def __init__(self, key: str, data: Mapping[str, Any], sha256: str):
        if f"{data.get('template_id')}_v{data.get('version')}" != key:
            raise ConfigError(f"grid template file {key}.yaml declares {data.get('template_id')!r} version {data.get('version')!r}")
        if data.get("kind") != KIND:
            raise ConfigError(f"grid template {key!r} is of kind {data.get('kind')!r}, not {KIND!r}")
        if data.get("frame") not in FRAMES:
            raise ConfigError(f"grid template {key!r}: frame is one of {FRAMES}")
        if (data["frame"] == "absolute") != ("walls" in data):
            raise ConfigError(f"grid template {key!r}: names walls if and only if its frame is absolute")
        self.key, self.data, self.sha256 = key, data, sha256
        listed = tuple(str(name) for name in data["menu_options"])
        if listed != self.menu.names:
            raise ConfigError(f"grid template {key!r} lists the options {listed}, its table has {self.menu.names}")
        if self.menu.by_wall != (self.frame == "absolute"):
            raise ConfigError(f"grid template {key!r}: an absolute frame needs a table by the walls, and the own frame one by sides")

    @classmethod
    def load(cls, key: str) -> "GridTemplate":
        manifest = load_manifest()
        if key not in manifest:
            raise ConfigError(f"grid template {key!r} is not in {MANIFEST}")
        path = TEMPLATES_DIR / f"{key}.yaml"
        digest = template_sha256(path)
        if digest != manifest[key]["sha256"]:
            raise ConfigError(f"grid template {key!r} has changed since it was frozen (sha256 {digest}); make a new version")
        return cls(key, yaml.safe_load(path.read_text(encoding="utf-8")), digest)

    def identity(self) -> dict[str, str]:
        return {"key": self.key, "sha256": self.sha256}

    @property
    def frame(self) -> str:
        return str(self.data["frame"])

    @property
    def menu(self) -> Menu:
        return load_menu(str(self.data["menu_table"]))

    @property
    def walls(self) -> Optional[dict[str, str]]:
        walls = self.data.get("walls")
        return None if walls is None else {"a": str(walls["a"]), "b": str(walls["b"])}

    # --- the fixed text ---------------------------------------------------------------------------

    def system(self) -> str:
        d = self.data
        actions = "\n".join(fill(d["action_item"], name=name, says=says) for name, says in d["menu_options"].items())
        return fill(
            d["system"], role=d["role"].strip(), instructions=d["instructions"].strip(),
            reply_format=d["reply_format"].strip(), actions=fill(d["actions"].strip(), actions=actions),
        ).strip()

    def retry(self) -> str:
        return " ".join(self.data["retry"].split())

    def wrapper(self, view: GridView) -> str:
        return self.data["decision_point"]["opening" if view.decision_point == 1 else "again"]

    def messages(self, view: GridView) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.system()},
            {"role": "user", "content": self.description(view) + "\n\n" + self.wrapper(view)},
        ]

    # --- the description --------------------------------------------------------------------------

    def _lanes(self, n: int) -> str:
        v = self.data["view"]
        return _words(n, v["lane_word"], v["lanes_word"], v["numbers"])

    def _cells(self, n: int) -> str:
        v = self.data["view"]
        return f"{n} {v['cell_word'] if n == 1 else v['cells_word']}"

    def _lane_number(self, view: GridView, lane: int) -> int:
        """Absolute frame: lanes numbered from wall a (+y): lane 1 is next to it."""
        return view.lanes - lane

    def _across(self, lanes_left: int, lanes_plus_y: int, key: str) -> str:
        """A move across, in the frame: "one lane to your left" or "one lane towards the blue wall"."""
        v, n = self.data["view"], abs(lanes_left)
        if self.frame == "own":
            return fill(v[key], count=self._lanes(n), side="left" if lanes_left > 0 else "right")
        walls = self.walls
        return fill(v[key], count=self._lanes(n), wall=walls["a" if lanes_plus_y > 0 else "b"])

    def description(self, view: GridView) -> str:
        blocks = [self._me(view), self._notes(view), self._place(view), self._seen(view), self._history(view)]
        if view.time_to_meet is not None:
            label, seconds = view.time_to_meet
            blocks.append([fill(self.data["view"]["time_to_meet"], n=label, seconds=f"{seconds:.1f}")])
        return "\n\n".join("\n".join(block) for block in blocks if block)

    def _me(self, view: GridView) -> list[str]:
        v, me = self.data["view"], view.me
        lines = [v["self_header"]]
        if me.age is not None:
            lines.append(fill(v["self_age"], age=me.age))
        if me.gender is not None:
            lines.append(fill(v["self_gender"], gender=v["genders"][me.gender]))
        if me.errand:
            lines.append(fill(v["self_errand"], errand=me.errand))
        key = {"walking": "self_motion", "still": "self_still", "backing": "self_backing"}[me.motion]
        lines.append(fill(v[key], speed=speed(me.speed_mps), preferred=speed(me.preferred_speed_mps)))
        return lines + list(me.factor_lines)

    def _notes(self, view: GridView) -> list[str]:
        v = self.data["view"]
        return [v["notes_header"], *(fill(v["note"], note=note) for note in view.notes)] if view.notes else []

    def _place(self, view: GridView) -> list[str]:
        v = self.data["view"]
        grid = fill(
            v["place_grid"], lanes=self._lanes(view.lanes), cell=f"{view.cell_m:.1f}",
            preferred=speed(view.me.preferred_speed_mps), tick=f"{view.tick_s:.1f}",
        )
        if self.frame == "own":
            left = view.lanes - 1 - view.lane if view.direction > 0 else view.lane
            right = view.lanes - 1 - left
            where = fill(v["place_lane"], left=self._lanes(left), right=self._lanes(right))
        else:
            walls = self.walls
            where = fill(v["place_lane"], wall_a=walls["a"], wall_b=walls["b"], last=view.lanes, lane=self._lane_number(view, view.lane))
        return [v["place_header"], grid, where, *view.situation_lines]

    def _seen(self, view: GridView) -> list[str]:
        v = self.data["view"]
        lines = [v["seen_header"]]
        if not view.seen:
            return lines + [v["seen_nobody"]]
        for p in view.seen:
            if p.cells_ahead > 0:
                where = fill(v["ahead"], cells=self._cells(p.cells_ahead))
            elif p.cells_ahead < 0:
                where = fill(v["behind"], cells=self._cells(-p.cells_ahead))
            else:
                where = v["level"]
            if self.frame == "own":
                across = v["same_lane"] if p.lanes_left == 0 else fill(v["other_lane"], count=self._lanes(abs(p.lanes_left)), side="left" if p.lanes_left > 0 else "right")
            else:
                across = fill(v["in_lane"], lane=self._lane_number(view, p.lane))
            motion = fill(v["motions"][p.motion], speed=speed(p.speed_mps))
            lines.append(fill(v["seen"], n=p.label, where=where, across=across, motion=motion))
            if p.age is not None:
                lines.append(fill(v["seen_age"], age=p.age))
            if p.gender is not None:
                lines.append(fill(v["seen_gender"], gender=v["genders"][p.gender]))
            changes = []
            if p.lanes_moved_left:
                changes.append(self._across(p.lanes_moved_left, p.lanes_moved_plus_y, "moved_across"))
            changes += [v["since_last_look"][c] for c in p.changes]
            if changes:
                joined = changes[0] if len(changes) == 1 else ", ".join(changes[:-1]) + f" {v['and']} " + changes[-1]
                lines.append(fill(v["seen_changes"], changes=joined))
            lines += [fill(v["seen_extra"], line=line) for line in (*p.factor_lines, *p.pairwise_lines)]
        return lines

    def _history(self, view: GridView) -> list[str]:
        v = self.data["view"]
        if not view.history:
            return []
        lines = [v["history_header"]]
        for done in view.history:
            lines.append(fill(v["history_intent"], ago=f"{done.ago_s:.1f}", intent=done.intent))
            if done.lanes_left:
                lines.append(self._across(done.lanes_left, done.lanes_plus_y, "history_moved"))
            else:
                lines.append(v["history_not_moved"])
            if done.cells_back > 0:
                lines.append(fill(v["history_back"], cells=self._cells(done.cells_back)))
            lines.append(v["history_outcome"][done.outcome])
        return lines

