"""Watch runs move: an animated, interactive view of run folders, in the browser.

    python -m negsim.viz.viewer runs/<experiment>/<run_id>       # one run
    python -m negsim.viz.viewer runs/<experiment>                # every run of an experiment, with a picker
    python -m negsim.viz.viewer PATH [PATH ...] [--out FILE] [--no-open]

The viewer is a single HTML file with the runs' logs inside it. It needs no server, no
network and no library, so it opens anywhere and can be sent to anyone. It is written to
``views/`` in ``llm_negotiation/``, which git ignores, unless ``--out`` says otherwise, and
opened in the default browser unless ``--no-open`` is given.

Both kinds of run can be shown: a negotiation run of issue #24 and an avoidance run of
issue #26. Nothing is simulated again; everything on screen is read from the log files.
A run that follows rules (issue #28) shows which rule fired for each pair, when, with the
role and directive each agent got, read from ``pair_interactions.jsonl`` (issue #30).

A replay of a resolution session (``runs/<experiment>/replay/<session_id>/plan_only`` or
``plan_orca``) is shown with its session record, ``sessions/<session_id>.json`` (issue #96):
every decision point with what the LLM replied (intent, steps, signal, message, private
reason), when each step ran in this replay (from its ``outcome.json``), each agent's factors
and debrief, and its view cone and hearing range from the session's ``llm_view``. Give the
session's replay folder to see both modes, with a picker:

    python -m negsim.viz.viewer runs/rf10_round1_head_on/replay/<session_id>

A row of ``trajectory.csv`` gives an agent's position at the start of a step and the
velocity it moved with during that step, so between two consecutive steps an agent moves in
a straight line and drawing it that way is exact. Where a run logged only every n-th step
(``logging.trajectory_stride``), the positions in between are drawn in a straight line as
well. That is an approximation, and the viewer says so on screen.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from .. import __version__
from ..configutil import PACKAGE_ROOT
from ..runlog.schema import (
    CONFIG_FILE,
    CONVERSATION_FILE,
    EVENTS_FILE,
    OUTCOME_FILE,
    PAIR_INTERACTIONS_FILE,
    RUN_KIND_AVOIDANCE,
    RUN_KIND_NEGOTIATION,
    TRAJECTORY_FILE,
)

TEMPLATE = Path(__file__).with_name("viewer.html")
VIEWS_DIR = PACKAGE_ROOT / "views"
DATA_PLACEHOLDER = "__NEGSIM_RUN_DATA__"
SESSIONS_DIR = "sessions"
TITLE_PLACEHOLDER = "__NEGSIM_TITLE__"

# What an agent was doing on a step, one bit each. viewer.html reads the same values.
FLAG_EXPOSED = 1  # ORCA had to change the velocity it wanted, because of another agent
FLAG_FALLBACK = 2  # no velocity satisfied every half-plane; ORCA's fallback chose
FLAG_ARBITER = 4  # in a pair the arbiter held
FLAG_LEADER = 8
FLAG_FOLLOWER = 16
FLAG_IN_CONFLICT = 32  # the arbiter found a live conflict for it on this step
FLAG_DIALOGUE = 64  # a negotiation was going on (issue #24)
# A back-up manoeuvre (issue #32): the one backing out, then waiting outside; and the other.
FLAG_BACKING = 128
FLAG_WAITING = 256
FLAG_PROCEEDING = 512

#: Above this many agents a run is drawn as a crowd: no arrival events, labels off.
CROWD = 12


class ViewerError(ValueError):
    """A path that is not a run folder, or a run folder that cannot be read."""


# --- reading run folders ---------------------------------------------------------------------------


def run_folders(path: Path | str) -> list[Path]:
    """The run folders at ``path``: the folder itself, or every run folder directly inside it."""
    path = Path(path)
    if (path / CONFIG_FILE).is_file():
        return [path]
    if path.is_dir():
        found = sorted(child for child in path.iterdir() if (child / CONFIG_FILE).is_file())
        if found:
            return found
    raise ViewerError(f"{path}: not a run folder (it has no {CONFIG_FILE}) and holds no run folders")


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ViewerError(f"{path.parent}: missing {path.name}") from exc


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _read_rows(path: Path) -> dict[int, list[dict[str, str]]]:
    """Trajectory rows grouped by agent, in the order they were written."""
    if not path.is_file():
        raise ViewerError(f"{path.parent}: missing {path.name}")
    rows: dict[int, list[dict[str, str]]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.setdefault(int(row["agent_id"]), []).append(row)
    return rows


def _number(text: Optional[str]) -> Optional[float]:
    return None if text in (None, "") else float(text)


def _r(value: Optional[float], digits: int = 4) -> Optional[float]:
    return None if value is None else round(value, digits)


def _flag(row: dict[str, str], column: str) -> bool:
    return row.get(column) == "true"


def _role_flags(row: dict[str, str]) -> int:
    role = row.get("role")
    flags = FLAG_LEADER if role == "leader" else FLAG_FOLLOWER if role == "follower" else 0
    return flags | (FLAG_IN_CONFLICT if _flag(row, "in_conflict") else 0)


#: The trajectory's ``back_up`` column (log schema 5), as flags; a run of version 4 or earlier has none.
_BACK_UP_FLAGS = {"backing": FLAG_BACKING, "waiting": FLAG_WAITING, "proceeding": FLAG_PROCEEDING}


def _back_up_flags(row: dict[str, str]) -> int:
    return _BACK_UP_FLAGS.get(row.get("back_up") or "", 0)


def _fmt(value: Optional[float], unit: str = "", digits: int = 1) -> str:
    if value is None:
        return "–"
    return f"{value:.{digits}f}{(' ' + unit) if unit else ''}"


def _base(config: dict, outcome: dict, kind: str) -> dict[str, Any]:
    scenario = config["scenario"]
    return {
        "key": f"{config['experiment_name']}/{config['run_id']}",
        "experiment": config["experiment_name"],
        "run_id": config["run_id"],
        "kind": kind,
        "scenario": scenario["type"],
        "description": scenario.get("description", ""),
        "dt": scenario["dt_s"],
        "status": outcome["status"],
        "end_time": outcome["sim_time_s"],
        "walls": [[w["xmin"], w["ymin"], w["xmax"], w["ymax"]] for w in scenario.get("obstacles", [])],
        "segments": [],
        "stride": 1,
        "conversation": [],
    }


def _track(samples: Iterable[tuple]) -> dict[str, list]:
    """Column arrays from ``(t, x, y, heading, vx, vy, wanted vx, wanted vy, flags, neighbours)``."""
    columns: dict[str, list] = {key: [] for key in ("t", "x", "y", "h", "vx", "vy", "wx", "wy", "f", "n")}
    for t, x, y, heading, vx, vy, wx, wy, flags, neighbours in samples:
        columns["t"].append(round(t, 4))
        columns["x"].append(_r(x))
        columns["y"].append(_r(y))
        columns["h"].append(_r(heading))
        columns["vx"].append(_r(vx))
        columns["vy"].append(_r(vy))
        columns["wx"].append(_r(wx))
        columns["wy"].append(_r(wy))
        columns["f"].append(flags)
        columns["n"].append(neighbours)
    return columns


# --- an avoidance run (issue #26) ------------------------------------------------------------------


#: Plain ORCA's directive: what a field left out of a directive is (``rule-format.md``, section 7).
_PLAIN = {
    "side_preference": "none",
    "responsibility_share": 0.5,
    "speed_scale": 1.0,
    "clearance_margin": 0.0,
    "passage_order": "none",
    "back_up": False,
}


def _directive_fields(directive: dict) -> str:
    """The fields of a directive that are not plain ORCA's, in words; "plain ORCA" if none."""
    words = {
        "side_preference": lambda value: f"side {value}",
        "responsibility_share": lambda value: f"share {value:g}",
        "speed_scale": lambda value: f"speed ×{value:g}",
        "clearance_margin": lambda value: f"clearance {value:g} m",
        "passage_order": lambda value: f"order {value}",
        "back_up": lambda value: "backs up",
    }
    shown = [words[name](directive[name]) for name in _PLAIN if name in directive and directive[name] != _PLAIN[name]]
    return ", ".join(shown) or "plain ORCA"


def _rule_matches(pairs: list[dict]) -> list[tuple[dict, dict]]:
    """Every rule match of a run, with its pair, in order."""
    return [(pair, match) for pair in pairs for match in ((pair.get("rules") or {}).get("matches") or [])]


def _directive_text(config: dict, agent_id: int, pairs: Optional[list[dict]] = None) -> str:
    directives = config.get("directives", {})
    provider = directives.get("provider")
    if provider == "rules":
        switched_on = ", ".join(f"{rule['rule_id']}@{rule['version']}" for rule in directives.get("rules", [])) or "none"
        mine = [
            f"{match['rule_id']}@{match['version']} with agent {next(a for a in pair['agents'] if a != agent_id)} "
            f"from {match['from_time_s']:.1f} s: {match['roles'][str(agent_id)]}, "
            f"{_directive_fields(match['directives'][str(agent_id)])}"
            for pair, match in _rule_matches(pairs or [])
            if agent_id in pair["agents"]
        ]
        fired = "; ".join(mine) if mine else "no rule fired for it, so plain ORCA throughout"
        return f"from the rule database (switched on: {switched_on}). {fired}"
    if provider != "static":
        return "plain ORCA (no directives)"
    entry = dict(directives.get("default", {}))
    entry.update(directives.get("agents", {}).get(str(agent_id), {}))
    text = (
        f"side {entry.get('side_preference', 'none')}, share {entry.get('responsibility_share', 0.5):g}, "
        f"speed ×{entry.get('speed_scale', 1.0):g}, clearance {entry.get('clearance_margin', 0.0):g} m, "
        f"order {entry.get('passage_order', 'none')}"
        + (", backs up" if entry.get("back_up") else "")
    )
    pairs = [pair for pair in directives.get("pairs", []) if pair.get("observer") == agent_id]
    if pairs:
        text += f"; {len(pairs)} entr{'y' if len(pairs) == 1 else 'ies'} for particular neighbours"
    return text


def _rule_events(pairs: list[dict]) -> list[dict]:
    """One event per rule match: which rule, for which pair, each agent's role and directive."""
    shown = []
    for pair, match in _rule_matches(pairs):
        a, b = pair["agents"]
        given = "; ".join(
            f"agent {agent} {match['roles'][str(agent)]} ({_directive_fields(match['directives'][str(agent)])})" for agent in (a, b)
        )
        ending = (
            f"; ends at {match['to_time_s']:.1f} s ({match['end_reason']}"
            + (f", by {match['replaced_by']}" if match.get("replaced_by") else "")
            + ")"
            if match.get("to_time_s") is not None
            else ""
        )
        shown.append(
            {
                "type": "rule",
                "t": match["from_time_s"],
                "t_end": match.get("to_time_s"),
                "agents": [a, b],
                "text": f"Rule {match['rule_id']}@{match['version']} fires for agents {a} and {b}: {given}{ending}",
            }
        )
    return shown


def _avoidance_events(events: list[dict], goal_times: dict, n_agents: int, pairs: Optional[list[dict]] = None) -> list[dict]:
    shown = _rule_events(pairs or [])
    for event in events:
        kind = event["type"]
        item: dict[str, Any] = {"type": kind, "t": event["time_s"], "t_end": event.get("end_time_s")}
        if kind == "collision":
            a, b = event["pair"]
            item.update(agents=[a, b], text=f"Agents {a} and {b} overlap, by up to {event['max_overlap_m'] * 1000:.1f} mm")
        elif kind == "wall_collision":
            item.update(agents=[event["agent_id"]], text=f"Agent {event['agent_id']} overlaps a wall, by up to {event['max_overlap_m'] * 1000:.1f} mm")
        elif kind == "near_miss":
            a, b = event["pair"]
            item.update(agents=[a, b], text=f"Near miss: agents {a} and {b} come within {max(event['min_separation_m'], 0.0) * 100:.1f} cm")
        elif kind == "yield":
            item.update(
                agents=[event["agent_id"]],
                text=f"Agent {event['agent_id']} yields for {event['duration_s']:.1f} s (slowest {event['min_speed_mps']:.2f} m/s)",
            )
        elif kind == "handoff":
            a, b = event["pair"]
            if event["to"] == "arbiter":
                text = f"Agents {a} and {b} handed to the arbiter: agent {event['leader']} goes first ({event['role_source']})"
            elif event["to"] == "back_up":
                text = f"Agents {a} and {b} taken from the arbiter: {event['reason']}"
            else:
                text = f"Agents {a} and {b} handed back to ORCA: {event['reason']}"
            item.update(agents=[a, b], text=text)
        elif kind == "back_up":
            backer, other = event["backer"], event["other"]
            text = {
                "started": f"Agent {backer} starts to back out of the {event['segment']} for agent {other}"
                + (f", having walked {event['travelled_m']:.1f} m in" if event.get("travelled_m") is not None else ""),
                "out": f"Agent {backer} is out of the {event['segment']} and waits for agent {other}",
                "ended": f"Agent {backer} goes on ({str(event.get('reason', '')).replace('_', ' ')})",
            }.get(event["phase"], f"Agent {backer}: back-up {event['phase']}")
            item.update(agents=[backer, other], text=text)
        elif kind == "reciprocity_violation":
            a, b = event["agents"]
            item.update(
                agents=[a, b],
                text=(
                    f"Reciprocity violation between {a} and {b} on {event['field']}: asked for "
                    f"{event['given'][0]} and {event['given'][1]}, used {event['resolved'][0]} and {event['resolved'][1]}"
                ),
            )
        elif kind == "ambiguous_match":
            a, b = event["pair"]
            item.update(
                agents=[a, b],
                text=f"Ambiguous match for agents {a} and {b}: {event['applied']} applied, also {', '.join(event['ambiguous_with'])}",
            )
        elif kind == "cross_pair_conflict":
            values = ", ".join(f"{entry['rule']} says {entry['value']} with agents {entry['pair']}" for entry in event["values"])
            item.update(agents=[event["agent_id"]], text=f"Agent {event['agent_id']}'s rules disagree on {event['field']}: {values}")
        else:
            item.update(agents=[], text=kind)
        shown.append(item)
    if n_agents <= CROWD:
        for agent_id, time in sorted(goal_times.items(), key=lambda kv: (kv[1] is None, kv[1], int(kv[0]))):
            if time is not None:
                shown.append({"type": "arrival", "t": time, "t_end": None, "agents": [int(agent_id)], "text": f"Agent {agent_id} arrives"})
    shown.sort(key=lambda item: item["t"])
    return shown


def _avoidance_run(run_dir: Path, config: dict, outcome: dict) -> dict[str, Any]:
    run = _base(config, outcome, RUN_KIND_AVOIDANCE)
    scenario = config["scenario"]
    run["stride"] = config.get("logging", {}).get("trajectory_stride", 1)
    run["segments"] = [
        [s["xmin"], s["ymin"], s["xmax"], s["ymax"], s["name"]] for s in scenario.get("single_file", {}).get("segments", [])
    ]
    rows = _read_rows(run_dir / TRAJECTORY_FILE)
    pairs = _read_jsonl(run_dir / PAIR_INTERACTIONS_FILE)
    personas = {entry["agent_id"]: entry for entry in config.get("population", [])}
    goal_times = outcome["time_to_goal_s"]

    agents = []
    for spec in scenario["agents"]:
        agent_id = spec["agent_id"]
        mine = rows.get(agent_id, [])
        steps = [row for row in mine if row["speed_mps"] != ""]  # a step: state at its start, motion during it
        final = [row for row in mine if row["speed_mps"] == ""]  # the state at the end of the run
        samples = [
            (
                float(row["time_s"]), float(row["x_m"]), float(row["y_m"]), float(row["theta_rad"]),
                _number(row["vx_mps"]), _number(row["vy_mps"]), _number(row["pref_vx_mps"]), _number(row["pref_vy_mps"]),
                (FLAG_EXPOSED if _flag(row, "exposed") else 0)
                | (FLAG_FALLBACK if _flag(row, "fallback") else 0)
                | (FLAG_ARBITER if row["control_mode"] == "arbiter" else 0)
                | _role_flags(row)
                | _back_up_flags(row),
                int(row["n_neighbours"]) if row["n_neighbours"] != "" else None,
            )
            for row in steps
        ]
        arrival = goal_times.get(str(agent_id))
        if final:
            end = final[-1]
            # An agent that arrives leaves the scene and stops where it arrived, so its last
            # sample is its final position at the moment it arrived, not at the end of the run.
            when = arrival if arrival is not None else float(end["time_s"])
            if not samples or when > samples[-1][0]:
                samples.append(
                    (when, float(end["x_m"]), float(end["y_m"]), float(end["theta_rad"]), None, None, None, None, 0, None)
                )
        stats = outcome["agents"][str(agent_id)]
        persona = personas.get(agent_id, {})
        attributes = persona.get("attributes") or {}
        details = [
            ["Group", spec["group"]],
            ["Persona", f"{persona['persona_id']} ({', '.join(f'{k} {v}' for k, v in attributes.items() if v not in (None, ''))})"]
            if persona.get("persona_id") else ["Persona", "none"],
            ["Body radius", f"{spec['radius_m']:g} m"],
            ["Preferred / maximum speed", f"{spec['preferred_speed_mps']:g} / {spec['max_speed_mps']:g} m/s"],
            ["Sensing radius, neighbours", f"{spec['sensing_radius_m']:g} m, at most {spec['max_neighbours']}"],
            ["Directives", _directive_text(config, agent_id, pairs)],
            ["Time to goal", _fmt(stats["time_to_goal_s"], "s") if stats["time_to_goal_s"] is not None else "did not arrive"],
            ["Conflict exposure", _fmt(stats["conflict_exposure_time_s"], "s")],
            ["Yield time", _fmt(stats["yield_time_s"], "s")],
            ["Largest path deviation", _fmt(stats["path_deviation_max_m"], "m", 3)],
            ["Smallest gap to a neighbour", _fmt(stats["min_separation_m"], "m", 3)],
        ]
        agents.append(
            {
                "id": agent_id,
                "group": spec["group"],
                "radius": spec["radius_m"],
                "sensing": spec["sensing_radius_m"],
                "path": [[_r(x), _r(y)] for x, y in spec["path"]],
                "goal": [spec["goal"]["x"], spec["goal"]["y"]],
                "arrival": arrival,
                "leaves": True,
                "details": details,
                **_track(samples),
            }
        )
    run["agents"] = agents

    totals, collisions = outcome["totals"], outcome["collisions"]
    variant = ", ".join(f"{factor} = {level}" for factor, level in config.get("variant", {}).items())
    ended = "every agent arrived" if outcome["status"] == "completed" else outcome["status"]
    summary = [
        ["Scenario", scenario["type"]],
        ["Variant", variant or "–"],
        ["Outcome", f"{ended}, at {outcome['sim_time_s']:.1f} s"],
        ["Arrived", f"{outcome['arrived']} of {outcome['n_agents']}"],
        [
            "Collisions",
            f"{collisions['agent_agent']} between agents, {collisions['agent_wall']} with walls"
            + (f"; deepest {collisions['max_overlap_m'] * 1000:.1f} mm" if collisions["max_overlap_m"] else ""),
        ],
        ["Conflict exposure, all agents", _fmt(totals["conflict_exposure_time_s"], "s")],
        ["Yield events", f"{totals['yield_events']} ({_fmt(totals['yield_time_s'], 's')})"],
        ["Near misses", str(totals["near_misses"])],
        ["Smallest gap between bodies", _fmt(totals["min_separation_m"], "m", 3)],
        ["Steps with no allowed velocity", str(totals["steps_with_fallback"])],
        ["Reciprocity violations", str(len(outcome["reciprocity_violations"]))],
        ["Handoffs to and from the arbiter", str(len(outcome["handoffs"]))],
        ["Directives", _provider_text(config)],
    ]
    rules = outcome.get("rules")
    if rules is not None:
        fired = rules.get("matches_begun") or {}
        summary.append(["Rules fired", ", ".join(f"{key} ×{count}" for key, count in sorted(fired.items())) or "none"])
    back_up = outcome.get("back_up")
    run["back_ups"] = len((back_up or {}).get("manoeuvres") or [])
    if back_up is not None:  # log schema 5 (issue #32)
        totals_back = back_up["totals"]
        summary.append([
            "Backing out of a passage",
            f"{totals_back['manoeuvres']} manoeuvre(s), {_fmt(totals_back['backing_distance_m'], 'm', 2)} backed"
            if totals_back["manoeuvres"] else "none",
        ])
    tiers = (outcome.get("interaction_outcomes") or {}).get("tiers")
    if tiers is not None:
        summary.append(["Pair interactions by tier", ", ".join(f"{tier} {count}" for tier, count in tiers.items())])
    if run["stride"] > 1:
        summary.append(["Logged", f"every {run['stride']} steps; positions in between are interpolated"])
    run["summary"] = summary
    run["events"] = _avoidance_events(_read_jsonl(run_dir / EVENTS_FILE), goal_times, len(agents), pairs)
    _add_resolution(run_dir, config, outcome, run)
    return run


def _provider_text(config: dict) -> str:
    """Where the run's directives came from, in words."""
    directives = config.get("directives", {})
    provider = directives.get("provider", "null")
    if provider == "rules":
        named = directives.get("ruleset")
        count = len(directives.get("rules", []))
        return f"rules: {count} switched on" + (f", from rule set {named}" if named else "")
    if provider == "static":
        return "static: written in the experiment config"
    return "none: plain ORCA"


# --- a replay of a resolution session (issue #96) ----------------------------------------------------


def session_record(run_dir: Path, config: dict) -> Optional[dict[str, Any]]:
    """The session record a replay was made from, or None.

    A replay is ``<experiment>/replay/<session_id>/<mode>`` and names its session in
    ``plans.session_id``; the record is ``<experiment>/sessions/<session_id>.json``."""
    session_id = (config.get("plans") or {}).get("session_id")
    if not session_id:
        return None
    path = run_dir.parent.parent.parent / SESSIONS_DIR / f"{session_id}.json"
    if not path.is_file():
        return None
    record = _read_json(path)
    return record if record.get("session_id") == session_id else None


def _words(value: Any) -> str:
    if value is None or value == "":
        return "–"
    return str(value).replace("_", " ")


def _metres(value: float) -> str:
    return f"{value:g} m"


#: The events a step can start or end on, in words (``reply.py``; the scenario plug-ins add their own).
_STEP_EVENTS = {
    "other_passes": "the other has passed",
    "other_stops": "the other stops",
    "i_am_out_of_the_stretch": "out of the narrow stretch",
}
_SIGNALS = {
    "eye_contact": "makes eye contact", "nod": "nods", "wave_on": "waves the other on",
    "hold_up_hand": "holds up a hand", "point": "points", "other": "makes a gesture",
}


def step_text(step: Mapping[str, Any]) -> str:
    """One step of a plan, in words: when it starts, what the agent does, and until when."""
    parts = []
    start = step.get("start")
    if isinstance(start, Mapping) and "at_distance_m" in start:
        parts.append(f"from {_metres(start['at_distance_m'])} away:")
    elif isinstance(start, Mapping) and "after_seconds" in start:
        parts.append(f"after {start['after_seconds']:g} s:")
    elif isinstance(start, str) and start != "now":
        parts.append(f"once {_STEP_EVENTS.get(start, _words(start))}:")
    if step.get("back_up_m") is not None:
        parts.append(f"walk backwards {_metres(step['back_up_m'])}")
    speed = step.get("speed_mps")
    if speed is not None:
        parts.append("stand still" if speed == 0 else f"walk at {speed:g} m/s")
    turn = step.get("turn")
    if isinstance(turn, Mapping) and turn.get("degrees"):
        parts.append(f"{turn['degrees']:g}° to the {turn.get('to', '?')}")
    until = step.get("until")
    if isinstance(until, Mapping) and "seconds" in until:
        parts.append(f"for {until['seconds']:g} s")
    elif isinstance(until, Mapping) and "at_distance_m" in until:
        parts.append(f"until {_metres(until['at_distance_m'])} away")
    elif isinstance(until, str):
        parts.append(f"until {_STEP_EVENTS.get(until, _words(until))}")
    return " ".join(parts) or "carry on"


def _why(reasons: Iterable[Any]) -> str:
    """Why a decision point fired (``protocol.py``, D5), in words."""
    shown = []
    for reason in reasons:
        name, _, who = str(reason).partition(":")
        if name == "trigger":
            shown.append("the encounter begins")
        elif name == "perceives":
            continue
        elif name == "plan_failing":
            shown.append("its plan is failing")
        elif name == "plan_ended":
            shown.append("its plan has ended")
        elif name == "came_into_view":
            shown.append(f"agent {who} came into view")
        elif name == "signalled":
            shown.append(f"agent {who} signalled")
        elif name == "heard":
            shown.append(f"heard agent {who}")
        elif name.startswith("other_"):
            shown.append(f"agent {who} {_words(name[len('other_'):])}")
        else:
            shown.append(_words(reason))
    return ", ".join(dict.fromkeys(shown)) or "–"


def _distance_to_partner(point: Mapping[str, Any]) -> Optional[float]:
    view = point.get("view") or {}
    label = ((view.get("labels") or {}).get("label_of_agent") or {}).get(str(point.get("partner_id")))
    for person in view.get("seen") or []:
        if label is not None and person.get("label") == label:
            return _r(person.get("distance_m"), 2)
    return None


def _decisions(record: Mapping[str, Any], driver: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Every decision point, with what the replay made of its plan: when each step ran."""
    played = {(entry["agent_id"], entry["decision_point"]): entry for entry in driver.get("decisions") or []}
    cap = record.get("max_decision_points_per_agent")
    shown = []
    for point in record.get("decision_points") or []:
        agent, number = point["agent_id"], point["number"]
        parsed = point.get("parsed") or {}
        steps = point.get("plan_given") or parsed.get("steps") or []
        entry = played.get((agent, number)) or {}
        times: list[Optional[list[Optional[float]]]] = [None] * len(steps)
        for step in entry.get("step_records") or []:
            if 0 <= step["index"] < len(times):
                times[step["index"]] = [step.get("start_time_s"), step.get("end_time_s")]
        shown.append(
            {
                "agent": agent,
                "number": number,
                "cap": cap,
                "t": point["time_s"],
                "t_end": entry.get("ended_time_s"),
                "distance_m": _distance_to_partner(point),
                "why": _why(point.get("trigger_reasons") or []),
                "readable": point.get("parse_error") is None and bool(parsed),
                "intent": parsed.get("intent") or "",
                "steps": [step_text(step) for step in steps],
                "step_times": times,
                "signal": _SIGNALS.get(parsed.get("signal") or "none", ""),
                "message": parsed.get("message") or "",
                "reason": parsed.get("reason") or "",
                "outcome": _words(entry.get("outcome") or entry.get("state")),
            }
        )
    shown.sort(key=lambda item: (item["t"], item["agent"]))
    return shown


def _debriefs(record: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    shown = {}
    for debrief in record.get("debriefs") or []:
        parsed = debrief.get("parsed") or {}
        if parsed:
            shown[str(debrief["agent_id"])] = {
                "basis": parsed.get("basis") or "", "kind": _words(parsed.get("kind")),
                "source": parsed.get("source") or "none given", "applies_to": parsed.get("applies_to") or "",
            }
    return shown


#: An agent's own factors, in the order the panel lists them (``session.personas``).
_PERSON_ROWS = (
    ("age", "Age"), ("gender", "Gender"), ("ethnicity", "Ethnicity"), ("task", "Errand"), ("urgency", "Urgency"),
    ("mobility_aid", "Mobility aid"), ("load", "Load"), ("distraction", "Distraction"),
    ("assertiveness", "Assertiveness"), ("residence", "Residence"), ("memory_note", "Memory note"),
)
#: Lines of a person that the other may be shown (``session.visibility``).
_SHOWN = ("age", "gender", "ethnicity", "mobility_aid", "load", "distraction", "perceived_attractiveness", "familiarity")


def _person_rows(record: Mapping[str, Any], agent_id: int, others: Sequence[int], radius_m: float) -> list[list[str]]:
    session = record["session"]
    person = (session.get("personas") or {}).get(str(agent_id)) or {}
    rows = [[label, _words(person[key])] for key, label in _PERSON_ROWS if key in person]
    pairwise = session.get("pairwise") or {}
    order, matrix = pairwise.get("agents") or [], pairwise.get("perceived_attractiveness")
    for other in others:
        if matrix and agent_id in order and other in order:  # a row is who looks (pairwise.py)
            rows.append([f"Finds agent {other}", _words(matrix[order.index(agent_id)][order.index(other)])])
    if pairwise.get("familiarity"):
        rows.append(["Familiarity", _words(pairwise["familiarity"])])
    body = (record.get("bodies") or {}).get(str(agent_id))
    width = _metres(round(2 * (body["radius_m"] if body else radius_m), 3))
    rows.append(["Body width", width + (f" ({_words(body['because'])})" if body and body.get("because") else "")])
    visibility = session.get("visibility") or {}
    rows.append(["The other may be shown", ", ".join(_words(key) for key in _SHOWN if visibility.get(key)) or "none of these"])
    return rows


def _add_resolution(run_dir: Path, config: dict, outcome: dict, run: dict[str, Any]) -> None:
    """Add what the LLM agents decided, who they were and what they could see (issue #96).

    Nothing is added to a run that is not the replay of a session with its record beside it."""
    record = session_record(run_dir, config)
    if record is None:
        return
    plans = outcome.get("plans") or {}
    driver = plans.get("driver") or {}
    view = record.get("llm_view") or {}
    llm = record.get("llm") or {}
    decisions = _decisions(record, driver)
    debriefs = _debriefs(record)
    run["llm"] = {
        "session_id": record["session_id"],
        "condition": record.get("condition"),
        "mode": plans.get("mode") or (config.get("plans") or {}).get("mode"),
        "view": {key: view.get(key) for key in ("half_angle_deg", "range_m", "detail_range_m", "hearing_range_m", "walls_block_sight")},
        "decisions": decisions,
        "debriefs": debriefs,
    }

    ids = [agent["id"] for agent in run["agents"]]
    members = set((record.get("encounter") or {}).get("agents") or [])
    for agent in run["agents"]:
        if agent["id"] in members or str(agent["id"]) in (record["session"].get("personas") or {}):
            others = [other for other in ids if other != agent["id"]]
            # The replay's population has no persona; the session's people are the agents.
            agent["details"] = [row for row in agent["details"] if row[0] != "Persona"]
            agent["details"] += _person_rows(record, agent["id"], others, agent["radius"])
            debrief = debriefs.get(str(agent["id"]))
            if debrief:
                agent["details"].append(["Debrief", f"{debrief['basis']} ({debrief['kind']}; source: {debrief['source']})"])

    session, encounter = record["session"], record.get("encounter") or {}
    end = encounter.get("end") or {}
    situation = (record.get("factors") or {}).get("situation") or {}
    run["summary"] += [
        ["LLM session", f"{record['session_id']}, {run['llm']['condition']} condition, replayed {_words(run['llm']['mode'])}"],
        ["Model", f"{llm.get('model', '–')}, temperature {llm.get('temperature', '–')}, template {((record.get('templates') or {}).get('core') or {}).get('key', '–')}"],
        ["Encounter", (
            f"from {(encounter.get('trigger') or {}).get('time_s', '–')} s, ended at {end.get('time_s', '–')} s ({_words(end.get('reason'))})"
            + ("; not resolved by the LLM" if end.get("not_resolved_by_llm") else "")
        ) if encounter else "none"],
        ["Decision points", f"{len(decisions)}, at most {record.get('max_decision_points_per_agent', '–')} per agent"],
        ["Situation", ", ".join(_words(value) for value in situation.values()) or "–"],
    ]

    events = []
    for item in decisions:
        distance = f", {item['distance_m']:.1f} m away" if item["distance_m"] is not None else ""
        said = item["intent"] if item["readable"] else "(its reply could not be read)"
        events.append({  # a moment on the timeline; how long the plan ran is in run["llm"]
            "type": "decision", "t": item["t"], "t_end": None, "agents": [item["agent"]],
            "text": f"Agent {item['agent']} decides ({item['number']} of {item['cap']}{distance}; {item['why']}): {said}",
        })
    for made in record.get("signals") or []:
        seen = ", ".join(str(who) for who in made.get("seen_by") or [])
        events.append({
            "type": "signal", "t": made["time_s"], "t_end": None, "agents": [made["signaller_id"], *(made.get("seen_by") or [])],
            "text": f"Agent {made['signaller_id']} {_SIGNALS.get(made['signal'], _words(made['signal']))}" + (f" (seen by agent {seen})" if seen else " (nobody saw it)"),
        })
    for said in record.get("utterances") or []:
        events.append({
            "type": "message", "t": said["time_s"], "t_end": None, "agents": [said["speaker_id"]],
            "text": f"Agent {said['speaker_id']} says: {said['message']}",
        })
        run["conversation"].append({"t": said["time_s"], "speaker": said["speaker_id"], "stance": "says", "message": said["message"]})
    # A release asked for (protocol.py, point 6) hands the encounter to ORCA; one that follows
    # from the run (passed, arrived, run ended) only ends the plans' control.
    if record.get("release") and driver.get("released_time_s") is not None:
        events.append({
            "type": "release", "t": driver["released_time_s"], "t_end": None, "agents": sorted(members),
            "text": f"Not resolved by the LLM: every plan is used up and ORCA takes over ({_words(record['release'].get('reason'))})",
        })
    elif driver.get("released_time_s") is not None and driver.get("release_reason") != "run_ended":
        events.append({
            "type": "release", "t": driver["released_time_s"], "t_end": None, "agents": sorted(members),
            "text": f"The plans stop steering ({_words(driver.get('release_reason'))})",
        })
    run["events"] = sorted(run["events"] + events, key=lambda item: item["t"])
    run["conversation"].sort(key=lambda turn: turn["t"])


# --- a negotiation run (issue #24) -----------------------------------------------------------------


def _negotiation_run(run_dir: Path, config: dict, outcome: dict) -> dict[str, Any]:
    run = _base(config, outcome, RUN_KIND_NEGOTIATION)
    scenario = config["scenario"]
    rows = _read_rows(run_dir / TRAJECTORY_FILE)
    participants = {entry["agent_id"]: entry for entry in config.get("participants", [])}
    goal_times = outcome.get("time_to_goal_s", {})
    roles = outcome.get("roles", {})

    agents = []
    for spec in scenario["agents"]:
        agent_id = spec["agent_id"]
        samples = []
        for row in rows.get(agent_id, []):
            heading, speed = float(row["theta_rad"]), _number(row["v_mps"])
            vx = None if speed is None else speed * math.cos(heading)
            vy = None if speed is None else speed * math.sin(heading)
            flags = _role_flags(row) | (FLAG_DIALOGUE if _flag(row, "dialogue_active") else 0)
            samples.append((float(row["time_s"]), float(row["x_m"]), float(row["y_m"]), heading, vx, vy, None, None, flags, None))
        participant = participants.get(agent_id, {})
        persona = participant.get("persona") or {}
        role = (
            "leader" if roles.get("executed_leader") == agent_id else "follower" if roles.get("executed_follower") == agent_id else "–"
        )
        details = [
            ["Starts", spec["side"]],
            ["Task", f"{participant.get('task', '–')} ({participant.get('task_type', '–')})"],
            ["Persona", f"{persona.get('persona_id')} ({persona.get('gender')}, {persona.get('age')})" if persona else "none"],
            ["Body radius", f"{spec['radius_m']:g} m"],
            ["Maximum speed", f"{spec['max_speed_mps']:g} m/s"],
            ["Role it played", role],
            ["Time to goal", _fmt(goal_times.get(str(agent_id)), "s") if goal_times.get(str(agent_id)) is not None else "did not arrive"],
        ]
        agents.append(
            {
                "id": agent_id,
                "group": spec["side"],
                "radius": spec["radius_m"],
                "sensing": None,
                "path": [[_r(x), _r(y)] for x, y in spec["path"]],
                "goal": [spec["goal"]["x"], spec["goal"]["y"]],
                "arrival": goal_times.get(str(agent_id)),
                "leaves": False,
                "details": details,
                **_track(samples),
            }
        )
    run["agents"] = agents

    dialogue = outcome.get("negotiation", {})
    turns = _read_jsonl(run_dir / CONVERSATION_FILE)
    run["conversation"] = [
        {"t": turn.get("sim_time_s") or 0.0, "speaker": turn["speaker"], "stance": turn.get("stance"), "message": turn.get("message") or ""}
        for turn in turns
    ]
    if not dialogue.get("enabled"):
        talk = "no dialogue (this condition does not negotiate)"
    else:
        talk = f"{dialogue.get('end_reason') or 'not started'}, {dialogue.get('turns_used', 0)} messages"
    collisions = outcome.get("collisions", {})
    truth = outcome.get("ground_truth")
    summary = [
        ["Condition", str(config.get("condition", "–"))],
        ["Scenario", f"{scenario['type']} ({config.get('scenario_variant', '–')})"],
        ["Outcome", f"{outcome['status']}, at {outcome['sim_time_s']:.1f} s"],
        ["Dialogue", talk],
        ["Agreed leader", str(roles.get("negotiated_leader")) if roles.get("negotiated_leader") is not None else "none"],
        ["First through", str(outcome.get("first_through"))],
        ["Makespan", _fmt(outcome.get("makespan_s"), "s")],
        ["Follower's slowest speed", _fmt(outcome.get("follower_min_speed_mps"), "m/s", 3)],
        ["Collisions", str(collisions.get("agent_agent", 0) + collisions.get("agent_wall", 0))],
    ]
    if truth:
        summary.append(["Higher-priority task went first", "yes" if truth.get("higher_priority_first") else "no"])
    run["summary"] = summary

    events: list[dict[str, Any]] = []
    if dialogue.get("started"):
        events.append({"type": "dialogue", "t": dialogue.get("start_time_s") or 0.0, "t_end": dialogue.get("end_time_s"), "agents": [], "text": f"Dialogue: {talk}"})
    for agent_id, time in (outcome.get("region_entry_time_s") or {}).items():
        if time is not None:
            events.append({"type": "region", "t": time, "t_end": None, "agents": [int(agent_id)], "text": f"Agent {agent_id} enters the conflict region"})
    for agent_id, time in goal_times.items():
        if time is not None:
            events.append({"type": "arrival", "t": time, "t_end": None, "agents": [int(agent_id)], "text": f"Agent {agent_id} arrives"})
    if collisions.get("time_s") is not None:
        events.append({"type": "collision", "t": collisions["time_s"], "t_end": None, "agents": list(collisions.get("agents", [])), "text": "Collision: the run stops"})
    events.sort(key=lambda item: item["t"])
    run["events"] = events
    return run


# --- the viewer ------------------------------------------------------------------------------------


def load_run(run_dir: Path | str) -> dict[str, Any]:
    """Everything the viewer shows of one run, read from its log folder."""
    run_dir = Path(run_dir)
    config = _read_json(run_dir / CONFIG_FILE)
    outcome = _read_json(run_dir / OUTCOME_FILE)
    kind = config.get("run_kind", RUN_KIND_NEGOTIATION)
    if kind == RUN_KIND_AVOIDANCE:
        return _avoidance_run(run_dir, config, outcome)
    if kind == RUN_KIND_NEGOTIATION:
        return _negotiation_run(run_dir, config, outcome)
    raise ViewerError(f"{run_dir}: unknown run_kind {kind!r}")


def render(runs: list[dict[str, Any]], title: str) -> str:
    """The viewer page with ``runs`` inside it."""
    template = TEMPLATE.read_text(encoding="utf-8")
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "negsim_version": __version__,
        "flags": {
            "exposed": FLAG_EXPOSED, "fallback": FLAG_FALLBACK, "arbiter": FLAG_ARBITER, "leader": FLAG_LEADER,
            "follower": FLAG_FOLLOWER, "in_conflict": FLAG_IN_CONFLICT, "dialogue": FLAG_DIALOGUE,
            "backing": FLAG_BACKING, "waiting": FLAG_WAITING, "proceeding": FLAG_PROCEEDING,
        },
        "runs": runs,
    }
    # "<" is escaped so that nothing in a log (an LLM's message, say) can close the script
    # element that holds the data. JSON.parse reads < back as "<".
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c")
    safe_title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return template.replace(TITLE_PLACEHOLDER, safe_title, 1).replace(DATA_PLACEHOLDER, data, 1)


def default_output(paths: list[Path]) -> Path:
    """Where the viewer goes without ``--out``: ``views/``, named after what it shows."""
    if len(paths) == 1:
        path = paths[0].resolve()
        name = f"{path.parent.name}__{path.name}" if (path / CONFIG_FILE).is_file() else path.name
    else:
        name = "viewer"
    return VIEWS_DIR / f"{name}.html"


def build_viewer(paths: Iterable[Path | str], output: Optional[Path | str] = None) -> Path:
    """Write the viewer for the runs at ``paths`` and return where it was written."""
    paths = [Path(path) for path in paths]
    if not paths:
        raise ViewerError("give at least one run folder or experiment folder")
    folders = [folder for path in paths for folder in run_folders(path)]
    runs = [load_run(folder) for folder in folders]
    output = Path(output) if output is not None else default_output(paths)
    title = runs[0]["key"] if len(runs) == 1 else f"{runs[0]['experiment']} ({len(runs)} runs)"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(runs, f"Run viewer: {title}"), encoding="utf-8", newline="\n")
    return output


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", type=Path, help="run folders, or experiment folders holding run folders")
    parser.add_argument("--out", type=Path, help="where to write the viewer (default: views/<name>.html)")
    parser.add_argument("--no-open", action="store_true", help="write the file but do not open it in the browser")
    args = parser.parse_args(argv)
    try:
        output = build_viewer(args.paths, args.out)
    except (ViewerError, json.JSONDecodeError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"viewer: {output.resolve()}")
    if not args.no_open:
        webbrowser.open(output.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
