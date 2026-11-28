"""RF-49 (issue #138): round 1 (head-on) with the action menu, in the agent's own frame and in an
absolute frame, against RF-40's free steps, session by session.

RF-49 ran RF-40's silent and talk sessions three times over:

- ``own``: the menu in the agent's own frame (``resolve_menu_v1``), every session of RF-40's;
- ``abs``: the menu in the corridor's own frame, the two walls named by colour. It is split over
  two experiments by repeat (the user's decision of 2026-11-27, "Counterbalance, same size"):
  ``resolve_menu_abs_v1`` (the blue wall at +y) runs repeats 1 and 2, and
  ``resolve_menu_abs_swap_v1`` (the yellow wall at +y) runs the other two. A swapped session's
  r1 and r2 are RF-40's r3 and r4 (the same session, the same parity of who is asked first).

The counterfactual pairs ran in both absolute halves, so they are left out of every comparison
here: **the sessions compared are RF-40's 256 design sessions per condition** (32 cells, 2
geometries, 4 repeats), and each arm has each of them once. Written to ``menu.json`` and
``menu.md``:

1. **The rate per arm and condition**, paired with RF-40 (McNemar's exact test) and the two menu
   arms with each other: resolved on the plans alone (``plan_only``, RF-10's measure), collisions,
   near misses, deadlocks, and the rate with ORCA under the plans (``plan_orca``). By layout too.
2. **The dance at the start**: the two first plans' sides, each in its own frame
   (``analysis.sidestep_reprompt.start_kind``), and how many of each kind resolved.
3. **The walls in the absolute frame**: which wall each first move aside went towards, by the
   wall's place (``a`` is +y in both halves, named and listed first, and the wall positions are
   measured from) and by its colour, per half, layout and person. If the lean follows the colour,
   the wall chosen flips between the halves; if it follows the place, it does not (Fisher's exact
   test on half by wall). The swap cannot tell the place from being listed first or being the
   reference wall: they go together.
4. **The nearer wall**: in the 20 cm layout each person starts 10 cm to its own left of the
   centre line. How many first moves went towards the nearer wall, in each arm.
5. **The replies**: unreadable decision points, ``no_room`` and ``capped_by_wall`` flags, and the
   options chosen first.
6. **The pass distance** (RF-37's H2): the smallest distance between the two centres, in the
   resolved sessions, from ``plan_only``'s ``trajectory.csv``; and the share within H2's tolerance
   (0.93 m, within one SD of 0.17, ``docs/human-targets.md``).
7. **Talk**: messages that name a side or a wall, and what the speaker and the listener did.
8. **The hand check** (RF-45's definition, scored as RF-52 did), with Fisher's exact test of the
   own frame's headline share against the absolute frame's.
9. **The first plans as options** (menu arms): the two first options as a pair of kinds, and how
   each pair came out; and the sessions where one person stepped a little and the other carried
   on, by layout and the side stepped to. "A little" is 0.47 m, under two half-bodies (0.5 m), so
   a lone little step from an aligned start does not clear the other on its own.

Standard library only; it never imports negsim (``analysis/README.md``).

    python -m analysis.menu --rf40 llm_negotiation/runs/rf40_round1_head_on_turn_taking \\
        --own llm_negotiation/runs/rf49_round1_head_on_menu \\
        --abs llm_negotiation/runs/rf49_round1_head_on_menu_abs \\
        --swap llm_negotiation/runs/rf49_round1_head_on_menu_abs_swap \\
        --out llm_negotiation/runs/rf49_analysis
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from .compare import mcnemar_exact
from .gate import COMPLETED
from .hallucination import CATEGORIES, HEADLINE, _facts
from .noise import wilson
from .sidestep_reprompt import SIDES, fisher_exact, more_room, start_kind

CONDITIONS = ("silent", "talk")
#: Which wall each absolute template names by which colour. ``a`` is at +y in both (person 1, who
#: walks +x, has it on its left); checked against the templates' own ``walls`` by the tests.
WALLS_BY_TEMPLATE = {
    "resolve_menu_abs_v1": {"blue": "a", "yellow": "b"},
    "resolve_menu_abs_swap_v1": {"yellow": "a", "blue": "b"},
}
HALVES = {"resolve_menu_abs_v1": "blue_at_+y", "resolve_menu_abs_swap_v1": "yellow_at_+y"}
TOWARDS = re.compile(r"towards the (\w+) wall", re.IGNORECASE)
FROM_WALLS = re.compile(r"You are ([\d.]+) m from the (\w+) wall and ([\d.]+) m from the (\w+) wall")
COLOURS = re.compile(r"\b(blue|yellow)\b", re.IGNORECASE)
SIDE_WORDS = re.compile(r"\b(left|right)\b", re.IGNORECASE)
#: A difference in wall distance smaller than this (metres) means neither wall is nearer
#: (``analysis.sidestep_reprompt.ROOM_M``, a judgement: the aligned layout differs by rounding).
ROOM_M = 0.05
#: RF-37's H2 (Moussaid 2009 via ``docs/human-targets.md``): 0.93 m between centres, SD 0.17.
H2_MEAN_M, H2_SD_M = 0.93, 0.17


class MenuError(ValueError):
    """The runs cannot be read or compared as they are."""


def rf40_id(session_id: str, shift: int = 0) -> str:
    """The RF-40 session a session pairs with: its repeat moved by ``shift`` (2 for the swap)."""
    if not shift:
        return session_id
    found = re.search(r"_r(\d+)$", session_id)
    if not found:
        raise MenuError(f"{session_id}: not a repeat of a design session")
    return f"{session_id[:found.start()]}_r{int(found.group(1)) + shift}"


def wall_of(action: Optional[str], template: Optional[str]) -> Optional[tuple[str, str]]:
    """The wall (``a`` or ``b``) and colour an absolute option moves towards, or None."""
    walls = WALLS_BY_TEMPLATE.get(template or "")
    found = TOWARDS.search(action or "")
    if not walls or not found or found.group(1).lower() not in walls:
        return None
    colour = found.group(1).lower()
    return walls[colour], colour


def nearer_colour(place: Sequence[str]) -> Optional[str]:
    """The nearer wall's colour in an absolute prompt's WHERE YOU ARE lines, or None."""
    for line in place or []:
        found = FROM_WALLS.search(line)
        if found:
            d1, c1, d2, c2 = float(found.group(1)), found.group(2).lower(), float(found.group(3)), found.group(4).lower()
            if abs(d1 - d2) < ROOM_M:
                return None
            return c1 if d1 < d2 else c2
    return None


def min_centre_distance(trajectory: Path) -> Optional[float]:
    """The smallest distance between agents 0 and 1's centres over the run (RF-37's pass distance)."""
    if not trajectory.exists():
        return None
    where: dict[str, dict[str, tuple[float, float]]] = defaultdict(dict)
    with trajectory.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            where[row["step"]][row["agent_id"]] = (float(row["x_m"]), float(row["y_m"]))
    both = [math.dist(at["0"], at["1"]) for at in where.values() if "0" in at and "1" in at]
    return round(min(both), 4) if both else None


# --- loading ------------------------------------------------------------------------------------

def _truth(value: Optional[str]) -> bool:
    return str(value) == "True"


def load(experiment: Path, arm: str, shift: int = 0, conditions: Sequence[str] = CONDITIONS,
         distances: bool = True) -> list[dict[str, Any]]:
    """Every completed session of ``conditions`` that is not a counterfactual pair, with what the
    analysis needs from its record and its ``plan_only`` replay."""
    if not (experiment / "outcomes.csv").exists():
        raise MenuError(f"{experiment}: no outcomes.csv")
    with (experiment / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        rows = [r for r in csv.DictReader(handle)
                if r["outcome"] == COMPLETED and not r.get("pair_id") and r["condition"] in conditions]
    sessions = []
    for row in rows:
        record = json.loads((experiment / "sessions" / f"{row['session_id']}.json").read_text(encoding="utf-8"))
        template = ((record.get("templates") or {}).get("core") or {}).get("key")
        points: dict[int, list] = defaultdict(list)
        for point in record.get("decision_points") or []:
            points[point["agent_id"]].append(point)
        agents = {}
        for agent_id, found in sorted(points.items()):
            found.sort(key=lambda p: p["number"])
            decisions = []
            for point in found:
                parsed = point.get("parsed") or {}
                readable = point.get("parse_error") is None and bool(parsed)
                side = (point.get("coded") or {}).get("side") if readable else None
                place = (point.get("view") or {}).get("place") or []
                wall = wall_of(parsed.get("action"), template) if readable else None
                decisions.append({
                    "readable": readable, "action": parsed.get("action") if readable else None,
                    "side": side if side in SIDES else ("none" if readable else None),
                    "wall": wall[0] if wall else None, "colour": wall[1] if wall else None,
                    "flags": list(parsed.get("flags") or []),
                    "message": parsed.get("message") or "",
                    "heard": [h.get("message") or "" for h in (point.get("view") or {}).get("heard") or []],
                    "more_room": more_room(place), "nearer_colour": nearer_colour(place),
                })
            agents[agent_id] = decisions
        sessions.append({
            "arm": arm, "experiment": experiment.name, "session_id": row["session_id"],
            "rf40_id": rf40_id(row["session_id"], shift), "template": template,
            "half": HALVES.get(template or ""), "condition": row["condition"], "geometry": row["geometry"],
            "resolved": _truth(row["resolved_plan_only"]), "collision": _truth(row["collision_plan_only"]),
            "near_miss": _truth(row["near_miss_plan_only"]), "deadlock": _truth(row["deadlock_plan_only"]),
            "resolved_plan_orca": _truth(row["resolved_plan_orca"]),
            "agents": agents,
            "pass_distance_m": (min_centre_distance(experiment / "replay" / row["session_id"] / "plan_only" / "trajectory.csv")
                                if distances and _truth(row["resolved_plan_only"]) else None),
        })
    return sessions


# --- measures -----------------------------------------------------------------------------------

def _rate(k: int, n: int) -> dict[str, Any]:
    low, high = wilson(k, n)
    return {"k": k, "n": n, "rate": None if n == 0 else round(k / n, 4),
            "ci95": None if n == 0 else [round(low, 4), round(high, 4)]}


def first_side(session: Mapping[str, Any], agent: int) -> Optional[str]:
    decisions = session["agents"].get(agent) or []
    return decisions[0]["side"] if decisions else None


def start_of(session: Mapping[str, Any]) -> str:
    return start_kind(first_side(session, 0), first_side(session, 1))


def rates(sessions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    n = len(sessions)
    out = {m: _rate(sum(s[m] for s in sessions), n) for m in ("resolved", "collision", "near_miss", "deadlock", "resolved_plan_orca")}
    starts: dict[str, list] = defaultdict(list)
    for s in sessions:
        starts[start_of(s)].append(s)
    out["start"] = {kind: {"sessions": len(group), "resolved": sum(s["resolved"] for s in group)} for kind, group in sorted(starts.items())}
    return out


def paired(base: Mapping[str, Mapping[str, Any]], new: Mapping[str, Mapping[str, Any]], measure: str = "resolved") -> dict[str, Any]:
    """Sessions in both, by RF-40 id: both, only base, only new, neither, McNemar's exact p."""
    shared = sorted(set(base) & set(new))
    cells = Counter((bool(base[k][measure]), bool(new[k][measure])) for k in shared)
    only_base, only_new = cells[(True, False)], cells[(False, True)]
    return {"sessions": len(shared), "both": cells[(True, True)], "only_base": only_base, "only_new": only_new,
            "neither": cells[(False, False)], "mcnemar_p": round(mcnemar_exact(only_base, only_new), 6)}


def walls(sessions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The absolute frame's first moves aside, by wall place and colour (section 3 of the docstring)."""
    by: dict[str, Counter] = defaultdict(Counter)
    for s in sessions:
        if not s.get("half"):
            continue
        layout = s["geometry"]
        for agent, decisions in s["agents"].items():
            if not decisions or decisions[0]["wall"] is None:
                continue
            wall, colour = decisions[0]["wall"], decisions[0]["colour"]
            for key in (f"{s['half']}", f"{s['half']}|{layout}", f"{s['half']}|agent{agent}", f"{s['half']}|{s['condition']}"):
                by[key][f"wall_{wall}"] += 1
                by[key][colour] += 1
    halves = sorted({s["half"] for s in sessions if s.get("half")})
    test = None
    if len(halves) == 2:
        (h1, h2) = halves
        test = {"halves": halves, "fisher_p_half_by_wall": round(fisher_exact(
            by[h1]["wall_a"], by[h1]["wall_b"], by[h2]["wall_a"], by[h2]["wall_b"]), 6),
            "fisher_p_half_by_colour": round(fisher_exact(
                by[h1]["blue"], by[h1]["yellow"], by[h2]["blue"], by[h2]["yellow"]), 6)}
    return {"counts": {k: dict(v) for k, v in sorted(by.items())}, "test": test}


def nearer(sessions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """First moves aside towards the nearer wall, where one wall is nearer by ``ROOM_M`` or more."""
    out: dict[str, Counter] = defaultdict(Counter)
    for s in sessions:
        for decisions in s["agents"].values():
            if not decisions or decisions[0]["side"] not in SIDES:
                continue
            first = decisions[0]
            if first["nearer_colour"] is not None:
                towards = first["colour"] == first["nearer_colour"]
            elif first["more_room"] is not None:  # the own frame: more room is the far wall
                towards = first["side"] != first["more_room"]
            else:
                continue
            out[f"{s['geometry']}|{s['condition']}"]["towards_nearer" if towards else "towards_farther"] += 1
    return {k: dict(v) for k, v in sorted(out.items())}


def replies(sessions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    points = unreadable = 0
    flags: Counter = Counter()
    firsts: Counter = Counter()
    every: Counter = Counter()
    for s in sessions:
        for decisions in s["agents"].values():
            for i, d in enumerate(decisions):
                points += 1
                unreadable += not d["readable"]
                for flag in d["flags"]:
                    flags[flag.split(":")[0]] += 1
                if d["readable"] and d["action"]:  # RF-40's free steps have no action
                    every[d["action"]] += 1
                    if i == 0:
                        firsts[d["action"]] += 1
    return {"decision_points": points, "unreadable": unreadable, "flags": dict(flags),
            "first_actions": dict(firsts.most_common()), "all_actions": dict(every.most_common())}


def pass_distance(sessions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    found = sorted(s["pass_distance_m"] for s in sessions if s["pass_distance_m"] is not None)
    if not found:
        return {"n": 0}
    low, high = H2_MEAN_M - H2_SD_M, H2_MEAN_M + H2_SD_M
    q = statistics.quantiles(found, n=4) if len(found) > 1 else [found[0]] * 3
    return {"n": len(found), "median_m": round(statistics.median(found), 3), "q1_m": round(q[0], 3), "q3_m": round(q[2], 3),
            "within_h2": sum(low <= d <= high for d in found), "below_h2": sum(d < low for d in found),
            "above_h2": sum(d > high for d in found)}


def talk(sessions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Talk's messages: how many name a side or a wall; for a message naming one wall by colour,
    whether the speaker's own move at that decision went towards it; for a heard message naming
    one wall, where the listener's move at that decision went."""
    out: Counter = Counter()
    for s in sessions:
        if s["condition"] != "talk":
            continue
        for decisions in s["agents"].values():
            for d in decisions:
                if not d["readable"]:
                    continue
                out["decisions"] += 1
                said = d["message"].strip()
                if said:
                    out["with_message"] += 1
                    out["names_a_side"] += bool(SIDE_WORDS.search(said))
                    colours = {c.lower() for c in COLOURS.findall(said)}
                    out["names_a_wall"] += bool(colours)
                    if len(colours) == 1 and d["colour"] is not None:
                        out["speaker_moved_towards_named_wall" if d["colour"] in colours else "speaker_moved_towards_other_wall"] += 1
                for heard in d["heard"]:
                    colours = {c.lower() for c in COLOURS.findall(heard)}
                    if len(colours) == 1:
                        out["heard_one_wall"] += 1
                        if d["colour"] is None:
                            out["listener_not_aside"] += 1
                        else:
                            out["listener_towards_named_wall" if d["colour"] in colours else "listener_towards_other_wall"] += 1
    return dict(out)


def option_kind(action: Optional[str]) -> str:
    """A menu option as a kind: aside a little or well, carry on, step back, or slowing and stopping."""
    if action is None:
        return "unreadable"
    if action.startswith("step a little"):
        return "aside_little"
    if action.startswith("step well"):
        return "aside_well"
    return {"carry on": "carry_on", "step back": "back"}.get(action, "slow_or_stop")


def first_options(sessions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The two first plans as a pair of option kinds (menu arms), and how each pair came out. Two
    moves aside are split by direction: in the own frame the same own side makes room; in the
    absolute frame the same wall does not."""
    out: dict[str, Counter] = defaultdict(Counter)
    for s in sessions:
        firsts = {agent: decisions[0] for agent, decisions in s["agents"].items() if decisions}
        if len(firsts) < 2:
            key = "only one asked"
        else:
            a, b = firsts[0], firsts[1]
            kinds = sorted((option_kind(a["action"]), option_kind(b["action"])))
            key = " + ".join(kinds)
            if all(k.startswith("aside") for k in kinds):
                if a["wall"] is not None and b["wall"] is not None:
                    key += " (same wall)" if a["wall"] == b["wall"] else " (different walls)"
                else:
                    key += " (same own side)" if a["side"] == b["side"] else " (opposite own sides)"
        out[key]["sessions"] += 1
        out[key]["resolved"] += bool(s["resolved"])
        out[key]["collision"] += bool(s["collision"])
    return {k: dict(v) for k, v in sorted(out.items(), key=lambda kv: (-kv[1]["sessions"], kv[0]))}


def lone_step(sessions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Sessions whose first plans are one 'step a little' and one 'carry on', by layout and the
    side (own frame) the step went to. In the 20 cm layout the other starts on each person's right."""
    out: dict[str, Counter] = defaultdict(Counter)
    for s in sessions:
        firsts = [decisions[0] for decisions in s["agents"].values() if decisions]
        kinds = sorted(option_kind(d["action"]) for d in firsts)
        if kinds != ["aside_little", "carry_on"]:
            continue
        mover = next(d for d in firsts if option_kind(d["action"]) == "aside_little")
        key = f"{s['geometry']}|stepped_{mover['side']}"
        out[key]["sessions"] += 1
        out[key]["resolved"] += bool(s["resolved"])
    return {k: dict(v) for k, v in sorted(out.items())}


def _by(sessions: Iterable[Mapping[str, Any]], *keys: str) -> dict[tuple, list]:
    groups: dict[tuple, list] = defaultdict(list)
    for s in sessions:
        groups[tuple(s[k] for k in keys)].append(s)
    return groups


def summarise(arms: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict[str, Any]:
    """``arms``: ``rf40``, ``own`` and ``abs`` (both halves), each a list of loaded sessions."""
    for name, sessions in arms.items():
        ids = Counter((s["condition"], s["rf40_id"]) for s in sessions)
        twice = [k for k, n in ids.items() if n > 1]
        if twice:
            raise MenuError(f"{name}: {len(twice)} session(s) of RF-40 appear more than once, e.g. {twice[0]}")
    out: dict[str, Any] = {"arms": {}, "paired": {}, "by_layout": {}, "walls": {}, "nearer": {}, "replies": {},
                           "pass_distance": {}, "talk": {}, "first_options": {}, "lone_step": {}}
    keyed = {name: {c: {s["rf40_id"]: s for s in sessions if s["condition"] == c} for c in CONDITIONS} for name, sessions in arms.items()}
    for name, sessions in arms.items():
        for condition in CONDITIONS:
            group = [s for s in sessions if s["condition"] == condition]
            out["arms"][f"{name}|{condition}"] = rates(group)
            out["replies"][f"{name}|{condition}"] = replies(group)
            out["pass_distance"][f"{name}|{condition}"] = pass_distance(group)
            if name != "rf40":  # RF-40's free steps have no options
                out["first_options"][f"{name}|{condition}"] = first_options(group)
        if name != "rf40":
            out["lone_step"][name] = lone_step(sessions)
        out["nearer"][name] = nearer(sessions)
        for (condition, layout), group in sorted(_by(sessions, "condition", "geometry").items()):
            out["by_layout"][f"{name}|{condition}|{layout}"] = rates(group)
        out["talk"][name] = talk(sessions)
    if "abs" in arms:
        out["walls"] = walls(arms["abs"])
        for (condition, half), group in sorted(_by([s for s in arms["abs"]], "condition", "half").items()):
            out["arms"][f"abs:{half}|{condition}"] = rates(group)
    for base, new in (("rf40", "own"), ("rf40", "abs"), ("own", "abs")):
        if base in arms and new in arms:
            for condition in CONDITIONS:
                for measure in ("resolved", "collision"):
                    out["paired"][f"{base}->{new}|{condition}|{measure}"] = paired(keyed[base][condition], keyed[new][condition], measure)
    return out


# --- the hand check (RF-45's method, as RF-52 ran it) -------------------------------------------

def points(experiment: Path, arm: str) -> list[dict[str, Any]]:
    """Every decision point of the completed sessions not in a counterfactual pair."""
    with (experiment / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        keep = {r["session_id"] for r in csv.DictReader(handle) if r["outcome"] == COMPLETED and not r.get("pair_id")}
    out = []
    for session_id in sorted(keep):
        record = json.loads((experiment / "sessions" / f"{session_id}.json").read_text(encoding="utf-8"))
        for point in record.get("decision_points") or []:
            parsed = point.get("parsed") or {}
            out.append({"key": f"{experiment.name}/{session_id}/dp{point['index']}", "arm": arm,
                        "condition": record.get("condition"), "agent_id": point["agent_id"], "number": point["number"],
                        "readable": point.get("parse_error") is None and bool(parsed), "parse_error": point.get("parse_error"),
                        "action": parsed.get("action"), "flags": list(parsed.get("flags") or []), "signal": parsed.get("signal"),
                        "texts": {k: parsed.get(k) or "" for k in ("intent", "reason", "message")},
                        "coded": point.get("coded") or {}, "view": point.get("view") or {}})
    return out


def hand_sample(found: Sequence[Mapping[str, Any]], n_per_arm: int = 75, seed: int = 138) -> list[str]:
    """A seeded random sample of ``n_per_arm`` decision points from each menu arm."""
    rng = random.Random(seed)
    chosen = []
    for arm in ("own", "abs"):
        keys = sorted(p["key"] for p in found if p["arm"] == arm)
        chosen += sorted(rng.sample(keys, min(n_per_arm, len(keys))))
    return chosen


def hand_sheet(found: Sequence[Mapping[str, Any]], chosen: Sequence[str]) -> str:
    by_key = {p["key"]: p for p in found}
    out = ["# RF-49 hand check: hallucinated decisions with the menu", "",
           "RF-45's definition (categories 1, 2, 5, 7 the headline; 3 and 4 self-contradiction), RF-52's two extra marks "
           "(a side error; a move against the geometry). Each point read against what its prompt gave.", ""]
    for key in chosen:
        p = by_key[key]
        out += [f"## {key} ({p['arm']} frame, {p['condition']}, agent {p['agent_id']}, decision {p['number']})", ""]
        out += [f"- {line}" for line in _facts(p)]
        if p["readable"]:
            out += [f"- **option:** {p['action']}" + (f" (flags {p['flags']})" if p["flags"] else ""),
                    f"- **intent:** {p['texts']['intent']}", f"- **reason:** {p['texts']['reason']}"]
            if p["texts"]["message"] or (p["signal"] and p["signal"] != "none"):
                out.append(f"- **signal:** {p['signal']}; **message:** {p['texts']['message']}")
        else:
            out.append(f"- **unreadable:** {p['parse_error']}")
        out.append("")
    return "\n".join(out)


def score_hand(found: Sequence[Mapping[str, Any]], judgements: Mapping[str, Any]) -> dict[str, Any]:
    """``judgements[key] = {"categories": [...], "side_error": bool, "move_against_geometry": bool,
    "note": ...}``, the mapping itself or under ``"judgements"`` (RF-52's format)."""
    if isinstance(judgements.get("judgements"), Mapping):
        judgements = judgements["judgements"]
    by_key = {p["key"]: p for p in found}
    out = {}
    for arm in ("own", "abs", "all"):
        keys = [k for k in judgements if k in by_key and (arm == "all" or by_key[k]["arm"] == arm)]
        def share(test) -> dict[str, Any]:
            return _rate(sum(1 for k in keys if test(judgements[k])), len(keys))
        out[arm] = {"headline": share(lambda j: bool(set(j.get("categories") or []) & set(HEADLINE))),
                    "self_contradiction": share(lambda j: bool(set(j.get("categories") or []) & {"3", "4"})),
                    "side_error": share(lambda j: bool(j.get("side_error"))),
                    "move_against_geometry": share(lambda j: bool(j.get("move_against_geometry")))}
        out[arm]["by_category"] = {c: share(lambda j, c=c: c in (j.get("categories") or [])) for c in CATEGORIES}
    return out


# --- report -------------------------------------------------------------------------------------

def _pct(rate: Mapping[str, Any]) -> str:
    if rate["rate"] is None:
        return "n/a"
    low, high = rate["ci95"]
    return f"{rate['k']} of {rate['n']} ({rate['rate']:.2f}, {low:.2f} to {high:.2f})"


def _p(p: float) -> str:
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def markdown(summary: Mapping[str, Any]) -> str:
    lines = ["# RF-49: the menu against RF-40's free steps (generated by `analysis.menu`)", "",
             "Sessions: RF-40's design sessions (all four repeats, no counterfactual pair), each once per arm.", "",
             "## 1. Resolved on the plans alone, and the other measures", "",
             "| Arm, condition | Resolved | Collision | Near miss | Deadlock | Resolved with ORCA |", "| --- | --- | --- | --- | --- | --- |"]
    for key, r in summary["arms"].items():
        lines.append(f"| {key} | {_pct(r['resolved'])} | {r['collision']['k']} | {r['near_miss']['k']} | {r['deadlock']['k']} | {_pct(r['resolved_plan_orca'])} |")
    lines += ["", "Paired, session by session (McNemar's exact test):", "",
              "| Comparison | Sessions | Both | Only the first | Only the second | Neither | p |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for key, p in summary["paired"].items():
        lines.append(f"| {key} | {p['sessions']} | {p['both']} | {p['only_base']} | {p['only_new']} | {p['neither']} | {_p(p['mcnemar_p'])} |")
    lines += ["", "By layout:", "", "| Arm, condition, layout | Resolved | Collision |", "| --- | --- | --- |"]
    for key, r in summary["by_layout"].items():
        lines.append(f"| {key} | {_pct(r['resolved'])} | {r['collision']['k']} |")
    lines += ["", "## 2. The dance at the start (the two first plans, each side in its own frame)", "",
              "| Arm, condition | Same own side (room made) | Of them resolved | Towards the same wall | Of them resolved | Not both aside | Of them resolved |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for key, r in summary["arms"].items():
        st = r["start"]
        cells = []
        for kind in ("same_own_side", "towards_same_wall", "not_both_aside"):
            g = st.get(kind, {"sessions": 0, "resolved": 0})
            cells += [str(g["sessions"]), str(g["resolved"])]
        lines.append(f"| {key} | " + " | ".join(cells) + " |")
    w = summary.get("walls") or {}
    if w:
        lines += ["", "## 3. The walls in the absolute frame (first moves aside)", "",
                  "`a` is at +y in both halves (person 1's left), named and listed first, the reference wall.", "",
                  "| Group | Wall a (+y) | Wall b (-y) | Blue | Yellow |", "| --- | --- | --- | --- | --- |"]
        for key, c in w["counts"].items():
            lines.append(f"| {key} | {c.get('wall_a', 0)} | {c.get('wall_b', 0)} | {c.get('blue', 0)} | {c.get('yellow', 0)} |")
        if w.get("test"):
            t = w["test"]
            lines += ["", f"Fisher's exact test, half by wall: p = {_p(t['fisher_p_half_by_wall'])}; half by colour: p = {_p(t['fisher_p_half_by_colour'])}."]
    lines += ["", "## 4. Towards the nearer wall (first moves aside)", "", "| Arm | Layout, condition | Towards the nearer | Towards the farther |", "| --- | --- | --- | --- |"]
    for arm, groups in summary["nearer"].items():
        for key, c in groups.items():
            lines.append(f"| {arm} | {key} | {c.get('towards_nearer', 0)} | {c.get('towards_farther', 0)} |")
    lines += ["", "## 5. The replies", "", "| Arm, condition | Decision points | Unreadable | Flags | Options chosen first |", "| --- | --- | --- | --- | --- |"]
    for key, r in summary["replies"].items():
        firsts = "; ".join(f"{a}: {n}" for a, n in list(r["first_actions"].items())[:6])
        lines.append(f"| {key} | {r['decision_points']} | {r['unreadable']} | {r['flags'] or '-'} | {firsts} |")
    lines += ["", f"## 6. The pass distance in resolved sessions (RF-37's H2: {H2_MEAN_M} m, within {H2_SD_M})", "",
              "| Arm, condition | Sessions | Median (m) | Q1 to Q3 | Within H2 | Below | Above |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for key, d in summary["pass_distance"].items():
        if d["n"]:
            lines.append(f"| {key} | {d['n']} | {d['median_m']} | {d['q1_m']} to {d['q3_m']} | {d['within_h2']} | {d['below_h2']} | {d['above_h2']} |")
    lines += ["", "## 7. Talk", "", "| Arm | Counts |", "| --- | --- |"]
    for arm, c in summary["talk"].items():
        lines.append(f"| {arm} | {c} |")
    if summary.get("hand_check"):
        lines += ["", "## 8. The hand check (RF-45's definition; a seeded sample per arm)", "",
                  "| Arm | Headline (1, 2, 5, 7) | Self-contradiction (3, 4) | Side error | Move against the geometry |", "| --- | --- | --- | --- | --- |"]
        for arm, h in summary["hand_check"].items():
            lines.append(f"| {arm} | {_pct(h['headline'])} | {_pct(h['self_contradiction'])} | {_pct(h['side_error'])} | {_pct(h['move_against_geometry'])} |")
        if summary.get("hand_check_test") is not None:
            lines += ["", f"Headline, own frame against absolute frame: Fisher's exact p = {_p(summary['hand_check_test'])}."]
    if summary.get("first_options"):
        lines += ["", "## 9. The first plans as options (menu arms)", "",
                  "| Arm, condition | The two first options | Sessions | Resolved | Collision |", "| --- | --- | --- | --- | --- |"]
        for key, pairs in summary["first_options"].items():
            for pair, c in pairs.items():
                lines.append(f"| {key} | {pair} | {c['sessions']} | {c.get('resolved', 0)} | {c.get('collision', 0)} |")
        lines += ["", "One person stepped a little (0.47 m), the other carried on; in the 20 cm layout the other starts on the stepper's right:", "",
                  "| Arm | Layout, side stepped to | Sessions | Resolved |", "| --- | --- | --- | --- |"]
        for arm, groups in summary["lone_step"].items():
            for key, c in groups.items():
                lines.append(f"| {arm} | {key} | {c['sessions']} | {c.get('resolved', 0)} |")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m analysis.menu", description=__doc__.split("\n\n")[0])
    parser.add_argument("--rf40", type=Path, required=True, help="RF-40's experiment folder")
    parser.add_argument("--own", type=Path, required=True, help="RF-49's own-frame experiment folder")
    parser.add_argument("--abs", dest="abs_", type=Path, required=True, help="RF-49's absolute frame, blue at +y")
    parser.add_argument("--swap", type=Path, required=True, help="RF-49's absolute frame, yellow at +y (r1, r2 = RF-40's r3, r4)")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--hand", type=Path, default=None,
                        help="hand-check judgements (default: <out>/hand_judgements.json, if it exists)")
    args = parser.parse_args(argv)
    arms = {"rf40": load(args.rf40, "rf40"), "own": load(args.own, "own"),
            "abs": load(args.abs_, "abs") + load(args.swap, "abs", shift=2)}
    summary = summarise(arms)
    found = points(args.own, "own") + points(args.abs_, "abs") + points(args.swap, "abs")
    summary["hand_sample"] = hand_sample(found)
    hand = args.hand or args.out / "hand_judgements.json"
    if hand.is_file():
        summary["hand_check"] = score_hand(found, json.loads(hand.read_text(encoding="utf-8")))
        own, abs_ = summary["hand_check"].get("own"), summary["hand_check"].get("abs")
        if own and abs_ and own["headline"]["n"] and abs_["headline"]["n"]:
            o, a = own["headline"], abs_["headline"]
            summary["hand_check_test"] = round(fisher_exact(o["k"], o["n"] - o["k"], a["k"], a["n"] - a["k"]), 6)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "hand_check_sheet.md").write_text(hand_sheet(found, summary["hand_sample"]), encoding="utf-8")
    (args.out / "menu.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (args.out / "menu.md").write_text(markdown(summary), encoding="utf-8")
    print(f"wrote {args.out / 'menu.json'} and menu.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
