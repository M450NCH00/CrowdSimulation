"""The tables the rule extractor reads, and the held-out split (issue #66, RF-11, tasks 1 to 3).

**Sources.** One encounter type's sessions may be in several resolution experiments (round 1:
the independent condition re-executed in ``runs/rf10_round1_head_on_keep_line``, non-verbal and
talk in ``runs/rf30_round1_head_on_keep_line``). Their **design** sessions are pooled, as
``analysis.gate`` pools them: the first run of each cell (``repeat`` 1) and no counterfactual pair,
so that no cell counts twice. A session may be in only one source.

**Resolved** means resolved physically in the ``plan_only`` replay (RF-4): both left the conflict
zone, with no collision, no near miss and no deadlock, within the time limit
(``resolved_plan_only``). Only completed sessions count.

**The gate.** An encounter type is extracted only if it passed the resolution gate its experiments
fixed before their runs (``resolution_gate.plan_only_resolved_min`` in each ``config.json``, all
equal), recomputed here over the pooled design sessions with ``analysis.gate``'s rule. A type
that fails is skipped, and the output says so.

**The agent table** has one row per agent per session, in words an LLM can read. A factor of the
other person counts only as the agent was told it (RF-8's rule, ``analysis/load.py``): the other's
age and gender when ``<p>_other_age_shown`` (``_gender_shown``) >= 1; an observable factor's
marked level when its switch is on and ``<p>_other_observable_shown`` >= 1; the other's group when
``<p>_other_ethnicity_shown`` >= 1; a pairwise factor when ``<p>_pairwise_lines_shown`` >= 1.
``tests/test_extraction_analysis.py`` (in ``analysis/tests``) checks this table against
``analysis.load.agents_table`` on round 1's data.

**Coin-flip cells** (RF-8, ``analysis/noise.py``): a cell of the exact-repeat set whose commonest
behaviour (who passed first, each one's passing side, whether each stopped or backed up, in
``plan_only``) came up in fewer than 3 in 4 of its repeats. The table marks the rows of such a
cell, so that a rule does not claim certainty there.

**The split** (task 2): a seeded 25% of one encounter type's resolved sessions is set aside before
anything is shown to the extractor. It is by session, so both people of a held-out session are
held out.

Standard library only, as the rest of negsim.
"""

from __future__ import annotations

import csv
import json
import math
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ..configutil import ConfigError

COMPLETED = "completed"
CONDITIONS = ("independent", "non_verbal", "talk")
TOGETHER = "together"
COIN_FLIP_BELOW = 0.75  # RF-8's default (analysis.noise.COIN_FLIP_BELOW)

#: Person attributes (RF-5): base level, marked level, observable (``analysis/factors.py``).
PERSON: dict[str, tuple[str, str, bool]] = {
    "urgency": ("routine", "urgent", False),
    "mobility_aid": ("none", "cane", True),
    "load": ("none", "large_suitcase", True),
    "distraction": ("none", "phone", True),
    "assertiveness": ("gives_way", "holds_ground", False),
    "residence": ("local", "visitor", False),
    "memory_note": ("none", "bad_experience", False),
}
OBSERVABLE = tuple(name for name, (_, _, seen) in PERSON.items() if seen)
SITUATIONS = ("surroundings", "time_of_day")
PAIRWISE = ("finds_other_attractive", "knows_other")

NOT_TOLD = "not_told"
NOT_SEEN = "not_seen"
NOT_APPLICABLE = "n/a"

#: The columns of the agent table, in order. ``row`` and ``session`` label a row; the others are
#: what a rule's ``predict`` may read (:data:`CONDITION_COLUMNS`) or predict (:data:`TARGETS`).
CONTEXT_COLUMNS = ("condition", "geometry", "person")
OWN_COLUMNS = ("own_age", "own_gender", *(f"own_{name}" for name in PERSON), "own_ethnicity")
OTHER_COLUMNS = ("other_age", "other_gender", *(f"other_{name}" for name in OBSERVABLE), "other_ethnicity")
SITUATION_COLUMNS = (*SITUATIONS, *PAIRWISE)
DECISION_COLUMNS = (
    "decision_points", "first_decision_distance_m", "first_side", "first_slowed", "first_stopped", "first_backed_up",
    "first_start_distance_m", "final_side", "signalled", "spoke", "debrief_kind",
)
OUTCOME_COLUMNS = ("passed_first", "passing_side", "stopped", "backed_up")
MARK_COLUMNS = ("cell_stability",)
COLUMNS = ("row", "session", *CONTEXT_COLUMNS, *OWN_COLUMNS, *OTHER_COLUMNS, *SITUATION_COLUMNS, *DECISION_COLUMNS, *OUTCOME_COLUMNS, *MARK_COLUMNS)

#: What a rule may predict: an agent's own first plan, its signalling, and the physical outcome.
TARGETS = ("first_side", "first_slowed", "first_stopped", "first_backed_up", "final_side", "signalled", "spoke", *OUTCOME_COLUMNS)
#: What a rule's conditions may read: the situation, each person's factors (the other's as told),
#: when the agent decided, and whether it signalled or spoke (a rule that does needs
#: communication). Never an outcome, the debrief, or the cell's stability.
CONDITION_COLUMNS = (*CONTEXT_COLUMNS, *OWN_COLUMNS, *OTHER_COLUMNS, *SITUATION_COLUMNS, "decision_points", "first_decision_distance_m", "signalled", "spoke")
#: Columns no rule may read (``negsim.rules.fields.PROTECTED``): ethnicity and perceived attractiveness.
PROTECTED_COLUMNS = ("own_ethnicity", "other_ethnicity", "finds_other_attractive")
#: Reading these makes a rule need communication (``resolution.md``, D9).
COMMUNICATION_COLUMNS = ("signalled", "spoke")
NUMERIC_COLUMNS = ("own_age", "other_age", "decision_points", "first_decision_distance_m", "first_start_distance_m")


class ExtractionInputError(ConfigError):
    """The sources cannot be read as the extractor needs them."""


# --- sources -------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Source:
    """One resolution experiment's folder, read."""

    folder: Path
    config: Mapping[str, Any]
    rows: Sequence[Mapping[str, str]]

    @property
    def gate(self) -> Optional[dict[str, Any]]:
        gate = (self.config.get("experiment") or {}).get("resolution_gate")
        return None if not gate else dict(gate)

    @property
    def client(self) -> str:
        return str(self.config.get("client_name"))

    def record(self, session_id: str) -> dict[str, Any]:
        path = self.folder / "sessions" / f"{session_id}.json"
        if not path.is_file():
            raise ExtractionInputError(f"{path}: no session record")
        return json.loads(path.read_text(encoding="utf-8"))


def read_source(folder: Path | str) -> Source:
    folder = Path(folder)
    for name in ("config.json", "outcomes.csv"):
        if not (folder / name).is_file():
            raise ExtractionInputError(f"{folder}: no {name}; is it a resolution experiment's folder?")
    config = json.loads((folder / "config.json").read_text(encoding="utf-8"))
    if config.get("layer") != "resolution":
        raise ExtractionInputError(f"{folder}: layer {config.get('layer')!r}, not a resolution experiment")
    with (folder / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for column in ("session_id", "outcome", "condition", "encounter_type", "p1_agent", "p2_agent", "encounter_agents", "resolved_plan_only"):
        if rows and column not in rows[0]:
            raise ExtractionInputError(f"{folder}/outcomes.csv: no column {column!r}")
    return Source(folder, config, rows)


def is_design_row(row: Mapping[str, str]) -> bool:
    """The first run of a cell, not in a counterfactual pair (``analysis.gate.design_rows``)."""
    return str(row.get("repeat", "1")) == "1" and not row.get("pair_id")


@dataclass(frozen=True)
class Session:
    """One design session of the pooled sources."""

    session_id: str
    source: Source
    row: Mapping[str, str]

    @property
    def condition(self) -> str:
        return self.row["condition"]

    @property
    def encounter_type(self) -> str:
        return self.row["encounter_type"]

    @property
    def completed(self) -> bool:
        return self.row["outcome"] == COMPLETED

    @property
    def resolved(self) -> bool:
        return self.completed and self.row["resolved_plan_only"] == "True"


def pooled_sessions(sources: Sequence[Source]) -> list[Session]:
    """Every design session of every source, refusing a session id found twice."""
    sessions, seen = [], {}
    for source in sources:
        for row in source.rows:
            if not is_design_row(row):
                continue
            if row["session_id"] in seen:
                raise ExtractionInputError(f"session {row['session_id']} is in both {seen[row['session_id']]} and {source.folder}")
            seen[row["session_id"]] = source.folder
            sessions.append(Session(row["session_id"], source, row))
    return sessions


# --- the gate ------------------------------------------------------------------------------------


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    """The Wilson score interval of k in n (``analysis.noise.wilson``)."""
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centre - half), min(1.0, centre + half))


def gate(sources: Sequence[Source], sessions: Sequence[Session], encounter_type: str, require: bool = True) -> dict[str, Any]:
    """The resolution gate of one encounter type, over the pooled design sessions.

    Every source must have fixed the same gate before its run. With none fixed, a mock rehearsal
    may go on (``require`` false: the result says ``no_gate_fixed``); otherwise it is refused."""
    gates = {json.dumps(source.gate, sort_keys=True) for source in sources}
    if len(gates) > 1:
        raise ExtractionInputError(f"the sources fixed different resolution gates: {sorted(gates)}")
    fixed = sources[0].gate if sources else None
    mine = [session for session in sessions if session.encounter_type == encounter_type and session.completed]
    k, n = sum(session.resolved for session in mine), len(mine)
    low, high = wilson(k, n)
    result: dict[str, Any] = {
        "encounter_type": encounter_type, "resolved": k, "n": n,
        "rate": None if n == 0 else round(k / n, 4), "ci95": None if n == 0 else [round(low, 4), round(high, 4)],
    }
    if fixed is None:
        if require:
            raise ExtractionInputError("the sources fixed no resolution_gate before their runs; only a mock rehearsal may go on without one (gate.require: false)")
        return {**result, "threshold": None, "passes": n > 0 and k > 0, "status": "no_gate_fixed"}
    threshold = float(fixed["plan_only_resolved_min"])
    passes = n > 0 and k / n >= threshold
    return {**result, "threshold": threshold, "passes": passes, "status": "passes" if passes else "fails"}


# --- the agent table -----------------------------------------------------------------------------


def _number(text: Any) -> Optional[float]:
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(value) else value


def _count(text: Any) -> int:
    value = _number(text)
    return 0 if value is None else int(value)


def _yes_no(text: Any) -> str:
    if text in ("True", "true", "1", "1.0"):
        return "yes"
    if text in ("False", "false", "0", "0.0"):
        return "no"
    return ""


def _switch_on(row: Mapping[str, str], name: str) -> bool:
    """A visibility switch: on unless the design switched it off."""
    return row.get(name, "") not in ("False", "false", "0")


def _format_number(value: Optional[float], digits: int = 1) -> str:
    if value is None:
        return ""
    rounded = round(value, digits)
    return str(int(rounded)) if float(rounded).is_integer() else f"{rounded:.{digits}f}"


def geometry_name(row: Mapping[str, str]) -> str:
    raw = row.get("geometry") or row.get("case_geometry") or row.get("case_id", "")
    return raw.split("=", 1)[1] if raw.startswith("layout=") else raw


def physical(row: Mapping[str, str], person: str, mode: str = "plan_only") -> dict[str, str]:
    """A person's physical outcomes in ``mode``, mapped from the encounter's ``_a``/``_b`` through
    ``encounter_agents`` (``analysis.load.sessions_table``)."""
    members = [part for part in (row.get("encounter_agents") or "").split(";") if part != ""]
    agent = _count(row[f"{person}_agent"])
    which = "a" if members and int(members[0]) == agent else "b" if len(members) > 1 and int(members[1]) == agent else None
    first = row.get(f"who_passed_first_{mode}", "")
    if first == "":
        passed = ""
    elif first == TOGETHER:
        passed = TOGETHER
    else:
        passed = "yes" if int(float(first)) == agent else "no"
    out = {"passed_first": passed, "passing_side": "", "stopped": "", "backed_up": ""}
    if which is not None:
        out["passing_side"] = row.get(f"passing_side_{which}_{mode}", "")
        out["stopped"] = _yes_no(row.get(f"stopped_{which}_{mode}", ""))
        out["backed_up"] = _yes_no(row.get(f"backed_up_{which}_{mode}", ""))
    return out


def behaviour_key(row: Mapping[str, str], mode: str = "plan_only") -> str:
    """A session's behaviour (``analysis.load.BEHAVIOUR``): who passed first, each one's passing
    side, whether each stopped, whether each backed up."""
    p1, p2 = physical(row, "p1", mode), physical(row, "p2", mode)
    first = row.get(f"who_passed_first_{mode}", "")
    if first == "":
        who = "-"
    elif first == TOGETHER:
        who = TOGETHER
    else:
        who = "p1" if int(float(first)) == _count(row["p1_agent"]) else "p2" if int(float(first)) == _count(row["p2_agent"]) else "-"
    parts = [who, p1["passing_side"] or "-", p2["passing_side"] or "-"]
    for key in ("stopped", "backed_up"):
        parts += [{"yes": "1", "no": "0"}.get(p1[key], "-"), {"yes": "1", "no": "0"}.get(p2[key], "-")]
    return "|".join(parts)


def repeat_group(session_id: str) -> str:
    return re.sub(r"_r\d+$", "", session_id)


def coin_flip_cells(sources: Sequence[Source], below: float = COIN_FLIP_BELOW) -> dict[str, dict[str, Any]]:
    """Per cell of the exact-repeat set (keyed by its sessions' id without ``_r<n>``): its repeats,
    its stability (the commonest behaviour's share) and whether it is a coin flip
    (``analysis.noise.stability``)."""
    groups: dict[tuple[str, str], list[Mapping[str, str]]] = defaultdict(list)
    for source in sources:
        for row in source.rows:
            if row.get("exact_repeat_set") == "True" and row["outcome"] == COMPLETED and not row.get("pair_id"):
                groups[(str(source.folder), repeat_group(row["session_id"]))].append(row)
    cells = {}
    for (_, cell), members in sorted(groups.items()):
        if len(members) < 2:
            continue
        counts = Counter(behaviour_key(row) for row in members)
        stability = counts.most_common(1)[0][1] / len(members)
        cells[cell] = {"repeats": len(members), "stability": round(stability, 4), "coin_flip": stability < below,
                       "condition": members[0]["condition"], "commonest": counts.most_common(1)[0][0]}
    return cells


def first_decision_distance(record: Mapping[str, Any], agent: int) -> Optional[float]:
    """How far away the person the agent would meet was at its first decision point."""
    for point in record.get("decision_points") or []:
        if int(point["agent_id"]) != agent:
            continue
        view = point.get("view") or {}
        label = ((view.get("labels") or {}).get("label_of_agent") or {}).get(str(point.get("partner_id")))
        for person in view.get("seen") or []:
            if person.get("label") == label:
                return person.get("distance_m")
        return None  # the partner was only heard
    return None


def agent_row(session: Session, person: str, record: Optional[Mapping[str, Any]], stability: str) -> dict[str, str]:
    """One person's row of the agent table (without ``row`` and ``session``)."""
    row = session.row
    other = "p2" if person == "p1" else "p1"
    demographics = _switch_on(row, "demographics_visible")
    age_told = _count(row.get(f"{person}_other_age_shown")) >= 1
    gender_told = _count(row.get(f"{person}_other_gender_shown")) >= 1
    observable_told = _count(row.get(f"{person}_other_observable_shown")) >= 1
    out: dict[str, str] = {
        "condition": row["condition"], "geometry": geometry_name(row), "person": person,
        "own_age": row.get(f"{person}_age", "") if demographics else NOT_TOLD,
        "own_gender": row.get(f"{person}_gender", "") if demographics else NOT_TOLD,
    }
    for name in PERSON:
        out[f"own_{name}"] = row.get(f"{person}_{name}", "")
    out["own_ethnicity"] = row.get(f"{person}_ethnicity", "")
    out["other_age"] = row.get(f"{other}_age", "") if age_told else NOT_TOLD
    out["other_gender"] = row.get(f"{other}_gender", "") if gender_told else NOT_TOLD
    for name in OBSERVABLE:
        marked = PERSON[name][1]
        told = row.get(f"{other}_{name}") == marked and _switch_on(row, f"{name}_visible") and observable_told
        out[f"other_{name}"] = marked if told else NOT_SEEN
    ethnicity_told = _count(row.get(f"{person}_other_ethnicity_shown")) >= 1
    out["other_ethnicity"] = row.get(f"{other}_ethnicity", "") if ethnicity_told and row.get(f"{other}_ethnicity") else NOT_TOLD
    for name in SITUATIONS:
        out[name] = row.get(name, "")
    pairwise_told = _count(row.get(f"{person}_pairwise_lines_shown")) >= 1
    for name in PAIRWISE:
        value = _yes_no(row.get(f"{person}_{name}", ""))
        out[name] = value if pairwise_told and value else NOT_TOLD
    agent = _count(row[f"{person}_agent"])
    out["decision_points"] = str(_count(row.get(f"{person}_decision_points")))
    out["first_decision_distance_m"] = _format_number(None if record is None else first_decision_distance(record, agent))
    out["first_side"] = row.get(f"{person}_first_side", "")
    for key in ("slowed", "stopped", "backed_up"):
        out[f"first_{key}"] = _yes_no(row.get(f"{person}_first_{key}", ""))
    out["first_start_distance_m"] = _format_number(_number(row.get(f"{person}_first_start_distance_m")))
    out["final_side"] = row.get(f"{person}_final_side", "")
    condition = row["condition"]
    out["signalled"] = NOT_APPLICABLE if condition == "independent" else ("yes" if row.get(f"{person}_signals") else "no")
    out["spoke"] = "yes" if _count(row.get(f"{person}_messages")) > 0 else ("no" if condition == "talk" else NOT_APPLICABLE)
    out["debrief_kind"] = row.get(f"{person}_debrief_kind", "")
    out.update(physical(row, person))
    out["cell_stability"] = stability
    return out


@dataclass
class Tables:
    """One encounter type's tables. ``label`` gives each session a short name (``S001``) in the
    order the sessions were read; ``main`` and ``held_out`` are agent rows; ``failed`` are the
    failed sessions' rows, never in ``main`` or ``held_out``."""

    encounter_type: str
    label: dict[str, str]
    main: list[dict[str, str]]
    held_out: list[dict[str, str]]
    failed_sessions: list[Session]
    main_sessions: list[Session]
    held_out_sessions: list[Session]
    records: dict[str, dict[str, Any]] = field(default_factory=dict)
    coin_flips: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def columns(self) -> list[str]:
        return list(COLUMNS)


def held_out_split(sessions: Sequence[Session], share: float, seed: int) -> tuple[list[Session], list[Session]]:
    """The seeded split of resolved sessions into (main, held out), by session id order."""
    if not 0.0 <= share < 1.0:
        raise ConfigError(f"held_out.share: from 0 up to (not including) 1, got {share}")
    ordered = sorted(sessions, key=lambda session: session.session_id)
    k = int(math.floor(len(ordered) * share + 0.5))
    chosen = set(random.Random(seed).sample([session.session_id for session in ordered], k))
    return [s for s in ordered if s.session_id not in chosen], [s for s in ordered if s.session_id in chosen]


def build_tables(sessions: Sequence[Session], sources: Sequence[Source], encounter_type: str, share: float, seed: int) -> Tables:
    """The main and held-out agent tables and the failed sessions of one encounter type."""
    mine = [session for session in sessions if session.encounter_type == encounter_type and session.completed]
    resolved = [session for session in mine if session.resolved]
    failed = sorted((session for session in mine if not session.resolved), key=lambda s: s.session_id)
    main, held = held_out_split(resolved, share, seed)
    order = sorted(mine, key=lambda s: (CONDITIONS.index(s.condition) if s.condition in CONDITIONS else 99, s.session_id))
    width = max(3, len(str(len(order))))
    label = {session.session_id: f"S{index:0{width}d}" for index, session in enumerate(order, start=1)}
    flips = coin_flip_cells(sources)
    records = {session.session_id: session.source.record(session.session_id) for session in mine}

    def rows(group: Sequence[Session], start: int) -> list[dict[str, str]]:
        out = []
        for session in sorted(group, key=lambda s: label[s.session_id]):
            cell = flips.get(repeat_group(session.session_id))
            stability = "untested" if cell is None else ("coin_flip" if cell["coin_flip"] else "stable")
            for person in ("p1", "p2"):
                out.append({"row": str(start + len(out)), "session": label[session.session_id],
                            **agent_row(session, person, records[session.session_id], stability)})
        return out

    return Tables(encounter_type, label, rows(main, 1), rows(held, 1), failed, main, held, records, flips)


# --- the failed sessions -------------------------------------------------------------------------


def failure_of(row: Mapping[str, str], mode: str = "plan_only") -> str:
    """What went wrong in ``mode``: collision, deadlock, near miss or not cleared, in that order."""
    for key in ("collision", "deadlock", "near_miss"):
        if row.get(f"{key}_{mode}") == "True":
            return key
    return "not_cleared"


def failed_table(failed: Sequence[Session]) -> list[dict[str, str]]:
    """The failed sessions counted per condition, geometry, the two first plans' sides and the
    failure (the per-session factor combinations are almost all distinct)."""
    counts: Counter = Counter()
    for session in failed:
        row = session.row
        sides = "/".join(sorted((row.get("p1_first_side") or "-", row.get("p2_first_side") or "-")))
        counts[(row["condition"], geometry_name(row), sides, failure_of(row))] += 1
    return [
        {"condition": condition, "geometry": geometry, "first_sides_of_the_two": sides, "failure": failure, "sessions": str(count)}
        for (condition, geometry, sides, failure), count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def factor_margins(resolved: Sequence[Session], failed: Sequence[Session], factors: Sequence[str]) -> list[dict[str, str]]:
    """Per level of each design factor that varies: how many sessions resolved and how many failed."""
    out = []
    for name in factors:
        levels = sorted({s.row.get(name, "") for s in (*resolved, *failed)})
        if len(levels) < 2:
            continue
        for level in levels:
            k = sum(s.row.get(name, "") == level for s in resolved)
            f = sum(s.row.get(name, "") == level for s in failed)
            out.append({"factor": name, "level": level, "resolved": str(k), "failed": str(f)})
    return out


def as_csv(rows: Sequence[Mapping[str, str]], columns: Sequence[str]) -> str:
    """A compact CSV (``\\n`` line ends), with only ``columns``."""
    lines = [",".join(columns)]
    for row in rows:
        cells = []
        for column in columns:
            value = str(row.get(column, ""))
            cells.append(f'"{value}"' if any(ch in value for ch in ',"\n') else value)
        lines.append(",".join(cells))
    return "\n".join(lines)
