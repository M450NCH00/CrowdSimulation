"""The sidestep with a second chance (issue #127, RF-39): does being prompted again end the
pavement dance, and is the side an agent takes a preference or a coin flip?

RF-39 ran round 1's head-on sessions under ``resolve_v8`` (the sidestep in metres) in all three
conditions, every cell 4 times. It reads every completed session of the design (all repeats, no
counterfactual pair; ``analysis.gate`` keeps only the first run) and writes
``analysis/sidestep_reprompt.json`` and ``.md``:

1. **The rate**, per condition: resolved in ``plan_only``, over all repeats and over the first
   runs only (the sessions that pair with RF-29 and RF-30, for ``analysis.compare``).
2. **A dance at the start**: how the two *first* plans stepped (each agent's coded side, in its own
   frame): ``same_own_side`` (they make room), ``towards_same_wall`` (one to its left, one to its
   right: the pavement dance), ``not_both_aside`` (one or both did not move aside, or its reply
   was unreadable). For the sessions that started towards the same wall, how many still resolved.
   Independent has one decision point, so it is the reference with no second chance; non-verbal
   and talk are compared with it (Fisher's exact test, two-sided).
3. **How a dance ended**, in non-verbal and talk, for the sessions that started towards the same
   wall: how many agents changed side at a later decision (none, one, both), whether a message
   named a side (``left`` or ``right``, a keyword match), whether anyone pointed, the decision
   points used, and how the two stood when level (``analysis.lateral``).
4. **The side across repeats**: a *unit* is one agent of one cell in one condition (the same
   person, the same prompt, 4 times). For the units whose first plan moved aside in every repeat,
   the number of repeats it went right, against a coin weighted by the pooled share of right
   (binomial). A preference shows as more units all one way (4 of 4) than the coin gives; a
   chi-square test on {4-0, 3-1, 2-2} with one degree of freedom (one parameter estimated).
5. **The side against the room and what the agent said**: whether the first side was the side
   with more room (the wall distances of the agent's first prompt, a difference of at least
   ``ROOM_M``), by layout; and the debrief's ``side_basis`` (``resolve_debrief_v2``) beside it.

The side is the first plan's (the reply to the first prompt, the same in every condition but for
the signal and talk lines); the debrief is asked about the whole encounter. A unit whose replies
were unreadable in some repeat is counted apart, not dropped silently. ``ROOM_M`` (5 cm) is a
judgement, not a sourced number: the aligned layout's walls differ by 1 cm (rounding), the 20 cm
layout's by about 20 cm.

    python -m analysis.sidestep_reprompt llm_negotiation/runs/rf39_round1_head_on_sidestep_reprompt
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .gate import COMPLETED
from .lateral import SIDESTEPS, outcome_of, sidestep, when_level
from .noise import wilson

CONDITIONS = ("independent", "non_verbal", "talk")
SIDES = ("left", "right")
#: A difference in wall distance smaller than this (metres) means neither side has more room.
ROOM_M = 0.05
WALLS = re.compile(r"The wall on your left is ([\d.]+) m from you, the wall on your right ([\d.]+) m")
NAMES_A_SIDE = re.compile(r"\b(left|right)\b", re.IGNORECASE)


def start_kind(side_0: Optional[str], side_1: Optional[str]) -> str:
    """How the two first plans stepped, from each one's side in its own frame."""
    if side_0 not in SIDES or side_1 not in SIDES:
        return "not_both_aside"
    return "same_own_side" if side_0 == side_1 else "towards_same_wall"


def more_room(place: Sequence[str]) -> Optional[str]:
    """The side with more room in a prompt's WHERE YOU ARE lines, or None if neither has
    ``ROOM_M`` more (or the line is missing)."""
    for line in place:
        found = WALLS.search(line)
        if found:
            left, right = float(found.group(1)), float(found.group(2))
            if abs(left - right) < ROOM_M:
                return None
            return "left" if left > right else "right"
    return None


def fisher_exact(a: int, b: int, c: int, d: int) -> float:
    """Fisher's exact test, two-sided, on the table [[a, b], [c, d]]: the chance, with the margins
    fixed, of a table no more likely than this one."""
    row, col, n = a + b, a + c, a + b + c + d
    if n == 0:
        return 1.0

    def p(x: int) -> float:
        return math.comb(col, x) * math.comb(n - col, row - x) / math.comb(n, row)

    observed = p(a)
    low, high = max(0, row + col - n), min(row, col)
    return min(1.0, sum(p(x) for x in range(low, high + 1) if p(x) <= observed * (1 + 1e-9)))


def coin_test(counts: Mapping[int, int], repeats: int = 4) -> dict[str, Any]:
    """Units by how many of ``repeats`` went right, against a binomial coin at the pooled share.

    Categories: all one way (0 or ``repeats``), one off (1 or ``repeats - 1``), and the rest; with
    4 repeats these are 4-0, 3-1 and 2-2. Chi-square with one degree of freedom."""
    units = sum(counts.values())
    if units == 0:
        return {"units": 0}
    p = sum(k * v for k, v in counts.items()) / (units * repeats)

    def binom(k: int) -> float:
        return math.comb(repeats, k) * p**k * (1 - p) ** (repeats - k)

    groups = {"all_one_way": (0, repeats), "one_off": (1, repeats - 1)}
    rest = tuple(k for k in range(repeats + 1) if k not in (0, 1, repeats - 1, repeats))
    if rest:
        groups["split"] = rest
    observed = {name: sum(counts.get(k, 0) for k in set(ks)) for name, ks in groups.items()}
    expected = {name: units * sum(binom(k) for k in set(ks)) for name, ks in groups.items()}
    chi2 = sum((observed[g] - expected[g]) ** 2 / expected[g] for g in groups if expected[g] > 0)
    df = len(groups) - 2
    p_value = math.erfc(math.sqrt(chi2 / 2)) if df == 1 else None
    return {
        "units": units, "share_right": round(p, 4),
        "observed": observed, "expected": {g: round(v, 2) for g, v in expected.items()},
        "all_one_way_share": round(observed["all_one_way"] / units, 4),
        "all_one_way_expected_share": round(expected["all_one_way"] / units, 4),
        "chi2": round(chi2, 3), "df": df, "p": None if p_value is None else round(p_value, 4),
    }


def _rate(k: int, n: int) -> dict[str, Any]:
    low, high = wilson(k, n)
    return {"k": k, "n": n, "rate": None if n == 0 else round(k / n, 4),
            "ci95": None if n == 0 else [round(low, 4), round(high, 4)]}


def load(experiment: Path) -> list[dict[str, Any]]:
    """Every completed design session (all repeats, no counterfactual pair), with what the
    analysis needs from its record."""
    with (experiment / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["outcome"] == COMPLETED and not row.get("pair_id")]
    sessions = []
    for row in rows:
        record = json.loads((experiment / "sessions" / f"{row['session_id']}.json").read_text(encoding="utf-8"))
        points = defaultdict(list)
        for point in record.get("decision_points") or []:
            points[point["agent_id"]].append(point)
        agents = {}
        for agent_id, found in points.items():
            found.sort(key=lambda point: point["number"])
            sides = [None if point.get("parse_error") else (point.get("coded") or {}).get("side") for point in found]
            parsed = [point.get("parsed") or {} for point in found]
            agents[agent_id] = {
                "first_side": sides[0], "sides": sides, "decisions": len(found),
                "more_room": more_room((found[0].get("view") or {}).get("place") or []),
                "messages": [p.get("message") or "" for p in parsed],
                "signals": [p.get("signal") or "none" for p in parsed],
            }
        for debrief in record.get("debriefs") or []:
            if debrief["agent_id"] in agents:
                agents[debrief["agent_id"]]["side_basis"] = (debrief.get("parsed") or {}).get("side_basis")
        sessions.append({
            "session_id": row["session_id"], "unit": row["session_id"].rsplit("_r", 1)[0],
            "repeat": int(row["repeat"]), "condition": row["condition"], "geometry": row["geometry"],
            "outcome": outcome_of(row), "resolved": row["resolved_plan_only"] == "True",
            "agents": agents,
            "level": when_level(experiment / "replay" / row["session_id"] / "plan_only" / "trajectory.csv"),
        })
    return sessions


def _start(session: Mapping[str, Any]) -> str:
    agents = session["agents"]
    return start_kind((agents.get(0) or {}).get("first_side"), (agents.get(1) or {}).get("first_side"))


def _switched(agent: Mapping[str, Any]) -> bool:
    """Whether a later readable decision moved to the other side from the first plan's."""
    first = agent["first_side"]
    return first in SIDES and any(side in SIDES and side != first for side in agent["sides"][1:])


def summarise(sessions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {"sessions": len(sessions), "rate": {}, "start": {}, "dance_vs_independent": {},
                           "dance_ending": {}, "level": {}, "side": {}, "room": {}, "stated": {}}
    by_condition = defaultdict(list)
    for session in sessions:
        by_condition[session["condition"]].append(session)
    conditions = [c for c in CONDITIONS if c in by_condition]

    for c in conditions:
        found = by_condition[c]
        first = [s for s in found if s["repeat"] == 1]
        out["rate"][c] = {"all_repeats": _rate(sum(s["resolved"] for s in found), len(found)),
                          "first_runs": _rate(sum(s["resolved"] for s in first), len(first))}
        starts = defaultdict(list)
        for s in found:
            starts[_start(s)].append(s)
        out["start"][c] = {kind: _rate(sum(s["resolved"] for s in starts[kind]), len(starts[kind])) for kind in SIDESTEPS}
        level = defaultdict(Counter)
        for s in found:
            level[s["outcome"]][sidestep(s["level"]["own_0_m"], s["level"]["own_1_m"])] += 1
        out["level"][c] = {name: {kind: level[name][kind] for kind in SIDESTEPS} for name in sorted(level)}

    if "independent" in out["start"]:
        ref = out["start"]["independent"]["towards_same_wall"]
        for c in conditions:
            if c != "independent":
                new = out["start"][c]["towards_same_wall"]
                out["dance_vs_independent"][c] = round(fisher_exact(new["k"], new["n"] - new["k"], ref["k"], ref["n"] - ref["k"]), 4)

    for c in conditions:
        if c == "independent":
            continue
        dances = [s for s in by_condition[c] if _start(s) == "towards_same_wall"]
        ending = {}
        for label, group in (("resolved", [s for s in dances if s["resolved"]]), ("not_resolved", [s for s in dances if not s["resolved"]])):
            switches = Counter(sum(_switched(a) for a in s["agents"].values()) for s in group)
            ending[label] = {
                "sessions": len(group),
                "switched": {"none": switches[0], "one": switches[1], "both": switches[2]},
                "a_message_names_a_side": sum(any(NAMES_A_SIDE.search(m) for a in s["agents"].values() for m in a["messages"]) for s in group),
                "someone_pointed": sum(any(sig == "point" for a in s["agents"].values() for sig in a["signals"]) for s in group),
                "decision_points_median": statistics.median([sum(a["decisions"] for a in s["agents"].values()) for s in group]) if group else None,
                "when_level": dict(Counter(sidestep(s["level"]["own_0_m"], s["level"]["own_1_m"]) for s in group)),
            }
        out["dance_ending"][c] = ending

    units: dict[tuple[str, int], list[Optional[str]]] = defaultdict(list)
    meta: dict[tuple[str, int], tuple[str, str]] = {}
    for s in sessions:
        for agent_id, agent in s["agents"].items():
            units[(s["unit"], agent_id)].append(agent["first_side"])
            meta[(s["unit"], agent_id)] = (s["condition"], s["geometry"])
    groups: dict[str, Counter] = defaultdict(Counter)
    left_out: Counter = Counter()
    unit_stable: dict[tuple[str, int], bool] = {}
    for key, sides in units.items():
        condition, geometry = meta[key]
        if len(sides) != 4 or any(side not in SIDES for side in sides):
            left_out["fewer_than_4_runs" if len(sides) != 4 else "not_aside_or_unreadable_in_some_run"] += 1
            continue
        k = sides.count("right")
        unit_stable[key] = k in (0, 4)
        for name in ("all", f"condition {condition}", f"geometry {geometry}"):
            groups[name][k] += 1
    out["side"] = {"left_out": dict(left_out),
                   **{name: {"right_of_4": {k: counts.get(k, 0) for k in range(5)}, **coin_test(counts)} for name, counts in sorted(groups.items())}}

    room: dict[str, Counter] = defaultdict(Counter)
    stated: dict[str, Counter] = defaultdict(Counter)
    for s in sessions:
        for agent_id, agent in s["agents"].items():
            side = agent["first_side"]
            if side in SIDES and agent["more_room"]:
                room[s["geometry"]]["more_room_side" if side == agent["more_room"] else "less_room_side"] += 1
            elif side in SIDES:
                room[s["geometry"]]["no_side_has_more_room"] += 1
            basis = agent.get("side_basis") or "missing"
            stated["all"][basis] += 1
            if (s["unit"], agent_id) in unit_stable:
                stated["unit_all_one_way" if unit_stable[(s["unit"], agent_id)] else "unit_split"][basis] += 1
            if side in SIDES and agent["more_room"]:
                stated[f"{basis}: took the more-room side"][side == agent["more_room"]] += 1
    out["room"] = {g: dict(c) for g, c in sorted(room.items())}
    out["stated"] = {g: {str(k): v for k, v in c.most_common()} for g, c in sorted(stated.items())}
    return out


def _p(p: Optional[float]) -> str:
    """A p value as text: ``< 0.0001`` where rounding would show 0."""
    if p is None:
        return "n/a"
    return "< 0.0001" if p < 0.0001 else f"= {p:.4f}"


def _shown(rate: Mapping[str, Any]) -> str:
    if not rate["n"]:
        return "0 / 0"
    low, high = rate["ci95"]
    return f"{rate['k']} / {rate['n']} ({rate['rate']:.2f}, {low:.2f} to {high:.2f})"


def markdown(summary: Mapping[str, Any]) -> str:
    lines = ["# RF-39: the sidestep with a second chance", "",
             f"{summary['sessions']} completed design sessions (all repeats, no counterfactual pair). Rates are "
             "resolved in `plan_only`, k / n (rate, 95% Wilson interval).", "",
             "## 1. Resolved, by condition", "", "| Condition | All repeats | First runs only |", "| --- | --- | --- |"]
    for c, r in summary["rate"].items():
        lines.append(f"| {c} | {_shown(r['all_repeats'])} | {_shown(r['first_runs'])} |")
    lines += ["", "## 2. How the first plans stepped, and how many of each resolved", "",
              "| Condition | Both to their own same side | Towards the same wall (a dance) | One or both not aside |",
              "| --- | --- | --- | --- |"]
    for c, starts in summary["start"].items():
        lines.append(f"| {c} | " + " | ".join(_shown(starts[kind]) for kind in SIDESTEPS) + " |")
    for c, p in summary["dance_vs_independent"].items():
        lines.append(f"\nA dance at the start, resolved in {c} against independent: Fisher's exact p {_p(p)}.")
    lines += ["", "## 3. How a dance at the start ended (non-verbal and talk)", "",
              "| Condition | Ended | Sessions | Changed side: none / one / both | A message names a side | Someone pointed | Decision points (median) | When level: own same side / same wall / not both aside |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c, ending in summary["dance_ending"].items():
        for label, e in ending.items():
            sw, lv = e["switched"], e["when_level"]
            lines.append(f"| {c} | {label} | {e['sessions']} | {sw['none']} / {sw['one']} / {sw['both']} | {e['a_message_names_a_side']} | "
                         f"{e['someone_pointed']} | {e['decision_points_median']} | {lv.get('same_own_side', 0)} / {lv.get('towards_same_wall', 0)} / {lv.get('not_both_aside', 0)} |")
    lines += ["", "## 4. How the two stood when level, by outcome", "",
              "| Condition | Outcome | Both to their own same side | Towards the same wall | One or both not aside |", "| --- | --- | --- | --- | --- |"]
    for c, level in summary["level"].items():
        for name, counts in level.items():
            lines.append(f"| {c} | {name} | {counts['same_own_side']} | {counts['towards_same_wall']} | {counts['not_both_aside']} |")
    side = summary["side"]
    lines += ["", "## 5. The side across a cell's 4 repeats (first plans), against a weighted coin", "",
              f"Units left out: {side['left_out'] or 'none'}.", "",
              "| Units | n | Right in 0 / 1 / 2 / 3 / 4 of 4 | Share right | All one way: observed (coin) | chi-square (df 1), p |",
              "| --- | --- | --- | --- | --- | --- |"]
    for name, s in side.items():
        if name == "left_out" or not s.get("units"):
            continue
        counts = " / ".join(str(s["right_of_4"][k]) for k in range(5))
        lines.append(f"| {name} | {s['units']} | {counts} | {s['share_right']:.2f} | {s['all_one_way_share']:.2f} ({s['all_one_way_expected_share']:.2f}) | {s['chi2']}, p {_p(s['p'])} |")
    lines += ["", "## 6. The first side against the room each agent was told it had", "",
              f"More room: a wall at least {ROOM_M * 100:.0f} cm farther on one side in the first prompt.", "",
              "| Geometry | Took the more-room side | Took the less-room side | Neither side had more room |", "| --- | --- | --- | --- |"]
    for g, c in summary["room"].items():
        lines.append(f"| {g} | {c.get('more_room_side', 0)} | {c.get('less_room_side', 0)} | {c.get('no_side_has_more_room', 0)} |")
    lines += ["", "## 7. What the agents said (`side_basis`, debrief v2)", "", "| Group | Answers |", "| --- | --- |"]
    for g, c in summary["stated"].items():
        lines.append(f"| {g} | " + ", ".join(f"{k} {v}" for k, v in c.items()) + " |")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m analysis.sidestep_reprompt", description=__doc__.split("\n\n")[0])
    parser.add_argument("experiment", type=Path, help="the experiment's folder (outcomes.csv, sessions/ and replay/)")
    args = parser.parse_args(argv)
    summary = summarise(load(args.experiment))
    out = args.experiment / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    (out / "sidestep_reprompt.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    text = markdown(summary)
    (out / "sidestep_reprompt.md").write_text(text, encoding="utf-8", newline="\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
