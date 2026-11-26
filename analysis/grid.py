"""RF-52 (issue #141): round 1 on the grid, in the agent's own frame and in the absolute frame.

    python -m analysis.grid llm_negotiation/runs/rf52_round1_grid llm_negotiation/runs/rf52_round1_grid_abs \\
        --rf40 llm_negotiation/runs/rf40_round1_head_on_turn_taking --out llm_negotiation/runs/rf52_grid_analysis

No model call. It reads the grid's session records (``negsim/grid/paid.py``), the scripted walkers
beside them (``scripted_walkers.csv``, ``python -m negsim.grid.baseline``) and RF-40's outcomes, and
writes ``grid.json``, ``sessions.csv``, ``agents.csv``, ``points.csv``, ``effects_terms.csv`` and
``grid.md``.

**What it measures** (``docs/action-space.md`` sections 4 and 8.1; #141):

- **the gate** (the user's decision of 2026-11-26): RF-10's 0.50 on the share of sessions the
  agents' own plans resolve, with Wilson intervals, by frame and geometry. The grid has no ORCA,
  so the baselines are not available; the **scripted walkers** on the same lanes and seeds are
  reported beside it as context only (random walkers resolved 10 of 20 in RF-50's check);
- **RF-50's measures:** passed, blocked face to face, squeezed past, the pavement dance, deadlock,
  passing distance and time to pass;
- **the two frames paired** session by session (same people, cells and seeds): a 2 x 2 table and
  McNemar's exact test on the discordant pairs;
- **RF-40's silent condition beside it** (free steps in the continuous corridor), by rate only: a
  different world, so no pairing;
- **sides:** each agent's first move aside (own frame), the pair's convention (both to their own
  right, both left, or one each, which is a move towards the same wall), and the side each kept
  when passing;
- **hallucinated decisions** (RF-45's definition and codebook, ``analysis.hallucination``) through
  an adapter from the grid's view to the fields that codebook reads (:func:`as_rf45_point`), with
  only the rules RF-45's hand check found reliable counted as the coder's share; the share to
  quote comes from a hand check (RF-45's method);
- **side errors** on the grid (:func:`side_flags`), the grid's own checks of what a reply says about
  sides against the lanes its prompt gave;
- **the factor effects:** ``analysis.effects`` unchanged, on RF-40's factor columns for the same
  sessions (the grid's sessions are RF-40's silent ones: same ids, people and cells) with the
  grid's outcomes put in their place. Who passed first is not defined on the grid (both pass on
  one tick), so it is left empty.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

import numpy as np
import pandas as pd

from . import effects as EF
from . import load as L
from .hallucination import CATEGORIES, HEADLINE, check_point, checkable, load_codebook, wilson
from .intent import load_codebook as load_intent_codebook

FRAMES = {"rf52_round1_grid": "own", "rf52_round1_grid_abs": "absolute"}
CONDITION_OF = {"own": "grid_own", "absolute": "grid_absolute"}
#: RF-45's hand check (``runs/rf45_hallucination/report.md``): the coder's rules precise enough to count.
RELIABLE_RULES = ("5:unreadable", "1:moved_side", "1:moved_into_line")
#: RF-40's silent baseline (``docs/action-space.md`` section 3), quoted, and recomputed from its outcomes when given.
RF40_SILENT = {"resolved": 163, "n": 256}
SIDES = ("left", "right")


# --- reading ------------------------------------------------------------------------------------


def load_records(folder: Path) -> list[dict[str, Any]]:
    """The completed session records of a grid run (aborted ones set aside are left out)."""
    out = []
    for path in sorted((folder / "sessions").glob("*.json")):
        if ".aborted" in path.name:
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["outcome"] == "completed":
            out.append(record)
    return out


def frame_of(record: Mapping[str, Any]) -> str:
    key = record["templates"]["core"]["key"]
    return "absolute" if key.endswith("_abs_v1") else "own"


def trajectory(folder: Path, session_id: str) -> dict[int, dict[int, tuple[int, int]]]:
    """tick -> walker -> (row, lane)."""
    out: dict[int, dict[int, tuple[int, int]]] = defaultdict(dict)
    with (folder / "trajectories" / f"{session_id}.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            out[int(row["step"])][int(row["agent_id"])] = (int(row["row"]), int(row["lane"]))
    return out


# --- per session --------------------------------------------------------------------------------


def session_rows(records: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    rows = []
    for r in records:
        g, s = r["grid_outcome"], r["session"]
        rows.append({
            "session_id": r["session_id"], "frame": frame_of(r), "case_id": s["case_id"], "geometry": r["grid_geometry"],
            "off_centre": r["off_centre"], "layout": f"{r['grid_geometry']}/{r['off_centre']}", "repeat": s["repeat"],
            "pair_id": s.get("pair_id") or "", "first_asked": r["first_asked"],
            **{k: g[k] for k in ("resolved", "passed", "blocked_face_to_face", "squeezed_past", "dance",
                                 "first_changes_towards_same_wall", "deadlock", "ended_by", "passing_distance_m", "time_to_pass_s")},
            "decision_points": r["totals"]["decision_points"], "unreadable": r["totals"]["unreadable"],
            "calls": r["totals"]["calls"], "cost_usd": r["totals"]["cost_usd"],
        })
    return pd.DataFrame(rows)


def _rate(k: int, n: int) -> dict[str, Any]:
    low, high = wilson(k, n)
    return {"k": int(k), "n": int(n), "rate": (k / n) if n else None, "low": low, "high": high}


def gate_table(sessions: pd.DataFrame, threshold: float) -> list[dict[str, Any]]:
    """Resolved in plan_only (the grid's own result), by frame, and by frame and layout."""
    out = []
    for frame, mine in sessions.groupby("frame", sort=False):
        alone = mine.loc[mine["pair_id"] == ""]
        for layout, part in [("all", mine), ("all, pairs left out", alone), *sorted(mine.groupby("layout"))]:
            rate = _rate(int(part["resolved"].sum()), len(part))
            out.append({"frame": frame, "layout": layout, **rate,
                        "gate": None if layout != "all" else ("pass" if rate["rate"] >= threshold else "fail")})
    return out


MEASURES = ("resolved", "passed", "blocked_face_to_face", "squeezed_past", "dance", "first_changes_towards_same_wall", "deadlock")


def measures_table(sessions: pd.DataFrame) -> list[dict[str, Any]]:
    out = []
    for frame, mine in sessions.groupby("frame", sort=False):
        for layout, part in [("all", mine), *sorted(mine.groupby("layout"))]:
            row = {"frame": frame, "layout": layout, "n": len(part)}
            for m in MEASURES:
                row[m] = int(part[m].astype(bool).sum())
            passed = part.loc[part["passed"].astype(bool)]
            row["passing_distance_m"] = dict(Counter(round(float(v), 1) for v in passed["passing_distance_m"].dropna()))
            row["time_to_pass_s_median"] = float(passed["time_to_pass_s"].median()) if len(passed) else None
            row["decision_points_mean"] = float(part["decision_points"].mean())
            row["ended_by"] = dict(Counter(part["ended_by"]))
            out.append(row)
    return out


def exact_binomial_two_sided(k: int, n: int) -> float:
    """McNemar's exact test: the discordant pairs against a fair coin."""
    k, n = int(k), int(n)  # numpy integers overflow in 2 ** n
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def paired_frames(sessions: pd.DataFrame, measure: str = "resolved") -> dict[str, Any]:
    own = sessions.loc[sessions["frame"] == "own"].set_index("session_id")[measure].astype(bool)
    abs_ = sessions.loc[sessions["frame"] == "absolute"].set_index("session_id")[measure].astype(bool)
    both = own.index.intersection(abs_.index)
    a, b = own[both], abs_[both]
    table = {"both": int((a & b).sum()), "own_only": int((a & ~b).sum()), "absolute_only": int((~a & b).sum()), "neither": int((~a & ~b).sum())}
    discordant = table["own_only"] + table["absolute_only"]
    return {"measure": measure, "pairs": int(len(both)), **table,
            "mcnemar_exact_p": exact_binomial_two_sided(table["own_only"], discordant)}


def paired_with_rf40(sessions: pd.DataFrame, rf40_silent: pd.DataFrame) -> list[dict[str, Any]]:
    """Each frame against RF-40's silent condition, session by session (the same session ids): resolved in
    the agents' own plans on the grid against RF-40's ``resolved_plan_only``, with McNemar's exact test."""
    rf40 = rf40_silent.set_index("session_id")["resolved_plan_only"].eq("True")
    out = []
    for frame in ("own", "absolute"):
        grid = sessions.loc[sessions["frame"] == frame].set_index("session_id")["resolved"].astype(bool)
        both = grid.index.intersection(rf40.index)
        g, r = grid[both], rf40[both]
        table = {"both": int((g & r).sum()), "grid_only": int((g & ~r).sum()), "rf40_only": int((~g & r).sum()), "neither": int((~g & ~r).sum())}
        out.append({"frame": frame, "pairs": int(len(both)), **table,
                    "mcnemar_exact_p": exact_binomial_two_sided(table["rf40_only"], table["grid_only"] + table["rf40_only"])})
    return out


def scripted_table(folders: Sequence[Path]) -> list[dict[str, Any]]:
    """The scripted walkers on the same lanes and seeds (``scripted_walkers.csv``), by frame folder."""
    out = []
    for folder in folders:
        path = folder / "scripted_walkers.csv"
        if not path.is_file():
            continue
        data = pd.read_csv(path)
        for script, part in data.groupby("script", sort=False):
            out.append({"run": folder.name, "script": script, **_rate(int(part["resolved"].sum()), len(part)),
                        "dance": int(part["dance"].sum()), "deadlock": int(part["deadlock"].sum())})
    return out


# --- per agent ----------------------------------------------------------------------------------


def _first_readable(points: Sequence[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
    return next((p for p in points if p["parsed"] is not None), None)


def _plan_kind(option: Optional[str]) -> dict[str, bool]:
    option = (option or "").lower()
    return {"slowed": option.startswith("slow down"), "stopped": option.startswith("stop and wait"),
            "backed_up": option.startswith("step back"), "carry_on": option.startswith("carry on")}


def kept_side(track: Mapping[int, Mapping[int, tuple[int, int]]], passed_tick: Optional[int], me: int,
              direction: int) -> Optional[str]:
    """The side of the other that ``me`` passed on, in its own frame: ``left`` when the other went by
    on its right. Read at the last tick before passing, or at the passing tick if they were in one
    lane then (a diagonal slide)."""
    if passed_tick is None:
        return None
    for tick in (passed_tick - 1, passed_tick):
        cells = track.get(tick)
        if not cells or len(cells) < 2:
            continue
        offset = (cells[1 - me][1] - cells[me][1]) * direction  # the other's lanes to my own left
        if offset:
            return "right" if offset > 0 else "left"
    return None


def agent_rows(records: Sequence[Mapping[str, Any]], folder: Path) -> pd.DataFrame:
    rows = []
    for r in records:
        g = r["grid_outcome"]
        track = trajectory(folder, r["session_id"]) if (folder / "trajectories").is_dir() else {}
        for agent in (0, 1):
            points = [p for p in r["decision_points"] if p["agent_id"] == agent]
            first = _first_readable(points)
            last = next((p for p in reversed(points) if p["parsed"] is not None), None)
            direction = 1 if agent == 0 else -1
            option = first["parsed"]["action"] if first else None
            walker = g["walkers"][str(agent)]
            debrief = next((d for d in r["debriefs"] if d["agent_id"] == agent), None)
            parsed_debrief = (debrief or {}).get("parsed") or {}
            rows.append({
                "session_id": r["session_id"], "frame": frame_of(r), "agent": agent, "geometry": r["grid_geometry"],
                "off_centre": r["off_centre"], "starts_off_centre": r["off_centre"] == ("p1" if agent == 0 else "p2"),
                "decision_points": len(points), "unreadable": sum(1 for p in points if p["parsed"] is None),
                "first_option": option, "first_side": first["side"] if first else None,
                **({f"first_{k}": v for k, v in _plan_kind(option).items()} if first else {}),
                "final_side": last["side"] if last else None,
                "first_lane_change": _first_change(track, agent, direction),
                "kept_side": kept_side(track, g.get("passed_tick"), agent, direction) if g["passed"] else None,
                "lane_changes": walker["lane_changes"], "waits": walker["waits"], "backs": walker["backs"],
                "debrief_kind": parsed_debrief.get("kind"), "debrief_source": parsed_debrief.get("source"),
            })
    return pd.DataFrame(rows)


def _first_change(track: Mapping[int, Mapping[int, tuple[int, int]]], me: int, direction: int) -> Optional[str]:
    """The side of the agent's first lane change, in its own frame."""
    previous = None
    for tick in sorted(track):
        lane = track[tick].get(me, (None, None))[1]
        if lane is None:
            continue
        if previous is not None and lane != previous:
            return "left" if (lane - previous) * direction > 0 else "right"
        previous = lane
    return None


def conventions(agents: pd.DataFrame, column: str = "first_side") -> list[dict[str, Any]]:
    """Per frame: how the two people's first moves aside combine. ``right/right`` and ``left/left``
    put them on different walls; one each is towards the same wall (the dance's start)."""
    out = []
    for frame, mine in agents.groupby("frame", sort=False):
        combos: Counter = Counter()
        for _, pair in mine.groupby("session_id"):
            sides = tuple(str(s) if s in SIDES else "none" for s in pair.sort_values("agent")[column])
            key = ("same_wall" if set(sides) == {"left", "right"} else
                   "both_right" if sides == ("right", "right") else "both_left" if sides == ("left", "left") else
                   "one_only" if "none" in sides and set(sides) != {"none"} else "neither")
            combos[key] += 1
        out.append({"frame": frame, "column": column, **dict(combos)})
    return out


# --- RF-45's hallucinations, through an adapter ---------------------------------------------------

WALL_LINE = "The wall on your left is {left:.2f} m from you, the wall on your right {right:.2f} m"
MOTION = {"towards": "walking", "same_way": "walking", "away": "walking", "walking": "walking", "still": "still", "backing": "backing"}


def as_rf45_point(record: Mapping[str, Any], point: Mapping[str, Any], run: str) -> dict[str, Any]:
    """One grid decision point in the shape ``analysis.hallucination.check_point`` reads.

    - the other's bearing: the grid says the side in words ("one lane to your right"), so any lane
      offset is a side (0.5 rad), and the same lane is straight ahead;
    - a lane move since the last look is ``moved_left`` or ``moved_right``;
    - the walls: from the agent's centre, (lanes to that wall + 0.5) cells; the passage is the
      corridor's width; each person one cell wide;
    - its history: a lane move is ``sideways_m`` (positive to its left);
    - the plan, coded as RF-8's: the option's side, and whether it slows, stops or backs up.
    """
    view = point["view"]
    cell, lanes, lane, direction = view["cell_m"], view["lanes"], view["lane"], view["direction"]
    left_lanes = (lanes - 1 - lane) if direction > 0 else lane
    right_lanes = lanes - 1 - left_lanes
    seen = []
    for s in view.get("seen") or []:
        changes = list(s.get("changes") or [])
        moved = s.get("lanes_moved_left") or 0
        if moved:
            changes.append("moved_left" if moved > 0 else "moved_right")
        offset = s.get("lanes_left") or 0
        seen.append({
            "bearing_rad": 0.0 if offset == 0 else math.copysign(0.5, offset), "motion": MOTION.get(s.get("motion"), s.get("motion")),
            "changes": changes, "factor_lines": list(s.get("factor_lines") or []), "age": s.get("age"), "signal": "none",
            "width_m": cell,
        })
    history = [{"sideways_m": (h.get("lanes_left") or 0) * cell, "signal": "none", "message": None} for h in view.get("history") or []]
    place = [WALL_LINE.format(left=(left_lanes + 0.5) * cell, right=(right_lanes + 0.5) * cell), f"passage {lanes * cell:.1f} m wide"]
    parsed = point.get("parsed") or {}
    option = parsed.get("action")
    kind = _plan_kind(option)
    coded = {"side": point.get("side") if point.get("side") in SIDES else "none", "slowed": kind["slowed"],
             "stopped": kind["stopped"], "backed_up": kind["backed_up"]} if parsed else {}
    return {
        "run": run, "session_id": record["session_id"], "frame": frame_of(record), "condition": "silent",
        "resolved": bool(record["grid_outcome"]["resolved"]), "pair_id": record["session"].get("pair_id") or None,
        "agent_id": point["agent_id"], "number": point["number"], "index": point["index"],
        "readable": point.get("parse_error") is None and bool(parsed), "parse_error": point.get("parse_error"),
        "texts": {"intent": parsed.get("intent") or "", "reason": parsed.get("reason") or "", "message": ""},
        "signal": "none", "coded": coded, "option": option,
        "view": {"seen": seen, "heard": [], "history": history, "place": place, "me": {"width_m": cell}},
        "grid_view": view,
    }


def hallucination_points(records: Sequence[Mapping[str, Any]], run: str) -> list[dict[str, Any]]:
    codebook, intent_codebook = load_codebook(), load_intent_codebook()
    points = []
    for record in records:
        for point in record["decision_points"]:
            p = as_rf45_point(record, point, run)
            p["flags"] = check_point(p, codebook, intent_codebook)
            p["checkable"] = checkable(p, intent_codebook)
            p["side_flags"] = side_flags(p)
            points.append(p)
    return points


def _flag_keys(point: Mapping[str, Any]) -> set[str]:
    return {f"{f['category']}:{f['rule']}" for f in point["flags"]}


def coder_shares(points: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """RF-45's coder on the grid: every rule's count, and the share over its reliable rules only."""
    by_rule = Counter(key for p in points for key in _flag_keys(p))
    reliable = sum(1 for p in points if _flag_keys(p) & set(RELIABLE_RULES))
    return {"points": len(points), "reliable_rules": list(RELIABLE_RULES), "reliable": _rate(reliable, len(points)),
            "by_rule": dict(by_rule.most_common()),
            "headline_all_rules": _rate(sum(1 for p in points if {f["category"] for f in p["flags"]} & set(HEADLINE)), len(points))}


# --- side errors on the grid -------------------------------------------------------------------------

OTHER = r"(?:person 1|they|he|she|the other (?:person|pedestrian)|the (?:man|woman|guy|lady|person))"
LINK = r"(?:'s|'re|'ve| is| are| was| were| has| have| now| still| already| currently)*"
NUMBERS = {"one": 1, "a": 1, "an": 1, "two": 2, "three": 3, "four": 4, "1": 1, "2": 2, "3": 3, "4": 4}
#: "Person 1 is one lane to my right", "they are two lanes to my left", "he is on my right".
OTHER_LANES_SIDE = re.compile(
    rf"\b{OTHER}{LINK}\s+(?:(?:about|just|only)\s+)?(?:(?P<n>one|two|three|four|a|an|1|2|3|4)\s+lanes?\s+)?(?:to|on)\s+my\s+(?P<side>left|right)\b",
    re.IGNORECASE)
#: "Person 1 is in my lane", "we are in the same lane".
OTHER_SAME_LANE = re.compile(rf"\b(?:{OTHER}{LINK}\s+(?:directly\s+)?in\s+my\s+lane|we(?:'re| are)\s+in\s+the\s+same\s+lane)\b", re.IGNORECASE)
#: "Person 1 is in lane 3", "he is coming toward me in lane 2"; "I am in lane 2", "we are head-on in lane 3".
OTHER_LANE_NUMBER = re.compile(
    rf"\b{OTHER}{LINK}\s+(?:(?:walking|coming|approaching|heading|moving)\b[^.,;]{{0,25}}?\s)?in\s+lane\s+(?P<lane>[1-5])\b", re.IGNORECASE)
OWN_LANE_NUMBER = re.compile(
    r"\b(?:I(?:'m| am)(?:\s+currently)?|we(?:'re| are)\s+(?:both\s+|head-on\s+)?)\s*in\s+lane\s+(?P<lane>[1-5])\b", re.IGNORECASE)
#: "She moved a lane to her left", "they have drifted one lane to my right" (RF-52's pilot wording).
OTHER_MOVE_SIDE = re.compile(
    rf"\b{OTHER}{LINK}\s+(?:moved|shifted|drifted|stepped|edged|eased|swung)\s+(?:over\s+|back\s+)?"
    rf"(?:(?P<n>one|two|three|four|a|an|1|2|3|4)\s+lanes?\s+)?(?:to|towards?)\s+(?:the\s+)?(?P<whose>my|her|his|their)\s+(?P<side>left|right)\b",
    re.IGNORECASE)
#: "She appears to have moved towards the yellow wall", "he has drifted towards the blue side".
OTHER_MOVE_WALL = re.compile(
    rf"\b{OTHER}{LINK}(?:\s+(?:appears|seems)\s+to\s+have)?\s+(?:moved|shifted|drifted|stepped|edged|eased|swung)\s+(?:over\s+|back\s+)?"
    r"(?:(?:one|two|a|1|2)\s+lanes?\s+)?(?:to|towards?)\s+the\s+(?P<wall>blue|yellow)\s+(?:wall|side)\b",
    re.IGNORECASE)
#: An intent that opens with the speaker's own move to a side or a wall: "Step a little to my right",
#: "I'll move over towards the blue wall", "Keep to the yellow side".
SELF_MOVE = re.compile(
    r"\s*(?:I(?:'ll| will| am going to)?\s+)?(?:move|step|shift|ease|edge|keep|stay|go|head|veer|drift|swing|slide)\b"
    r"[^.,;]{0,30}?\b(?:(?:to|towards?|on)\s+(?:my|the)\s+(?P<side>left|right)\b|(?:to|towards?)\s+the\s+(?P<wall>blue|yellow)\s+(?:wall|side)\b)",
    re.IGNORECASE)
WALL_WORDS = re.compile(r"\b(blue|yellow)\s+(?:wall|side)\b", re.IGNORECASE)
SIDE_WORDS = re.compile(r"\b(left|right)\b", re.IGNORECASE)


def lane_number(view: Mapping[str, Any], lane: int) -> int:
    """The lane's number as the absolute-frame prompt gives it: lane 1 is next to the blue wall (+y),
    so lane ``lanes - lane`` (``negsim.grid.prompt``, ``_lane_number``)."""
    return int(view["lanes"]) - int(lane)


def _option_wall(option: Optional[str]) -> Optional[str]:
    found = WALL_WORDS.search(option or "")
    return found.group(1).lower() if found else None


def side_flags(point: Mapping[str, Any]) -> list[dict[str, Any]]:
    """What a readable reply says about sides and lanes, checked against the lanes its prompt gave.

    - ``other_side``: puts the other on the wrong side, or the wrong number of lanes away (own frame);
    - ``other_same_lane``: says the other is in its lane when the prompt put them in another;
    - ``other_move_side``: says the other moved to one side (theirs or the reader's own) when the prompt
      gave the other one, or no move: the error the supervisor raised (SV8);
    - ``other_move_wall``: says the other moved towards one wall when the prompt gave the other one;
    - ``other_lane_number`` / ``own_lane_number``: names the wrong lane (absolute frame; lane 1 is next
      to the blue wall, at +y, so lane ``lanes - lane``);
    - ``intent_side``: the intent names one own side, and the option moves to the other one;
    - ``intent_wall``: the intent names one wall, and the option moves towards the other one;
    - ``uses_own_sides``: an absolute-frame reply that speaks of left or right at all (not an
      error by itself: a frame the prompt did not use).
    """
    if not point["readable"]:
        return []
    view = point["grid_view"]
    texts = f"{point['texts']['intent']} {point['texts']['reason']}"
    seen = (view.get("seen") or [None])[0]
    flags = []
    if seen is not None:
        offset = seen["lanes_left"]
        for match in OTHER_LANES_SIDE.finditer(texts):
            side, n = match.group("side").lower(), NUMBERS.get((match.group("n") or "").lower())
            actual = "left" if offset > 0 else "right" if offset < 0 else None
            if actual != side or (n is not None and n != abs(offset)):
                flags.append({"rule": "other_side", "claim": match.group(0), "evidence": f"the prompt: {abs(offset)} lane(s) to the {actual or 'same lane'}"})
        if offset != 0 and OTHER_SAME_LANE.search(texts):
            flags.append({"rule": "other_same_lane", "claim": OTHER_SAME_LANE.search(texts).group(0), "evidence": f"the prompt: {abs(offset)} lane(s) off"})
        moved_left = int(seen.get("lanes_moved_left") or 0)
        for match in OTHER_MOVE_SIDE.finditer(texts):
            side, whose = match.group("side").lower(), match.group("whose").lower()
            n = NUMBERS.get((match.group("n") or "").lower())
            # The view gives the move in the reader's own frame; the other faces the other way, so their
            # own left is the reader's right.
            to_readers_left = side == "left" if whose == "my" else side == "right"
            # A move the view does not give (none since the reader was last asked) cannot be checked: the
            # claim may be about an earlier one (RF-52's flags read against the replies).
            if moved_left != 0 and ((moved_left > 0) != to_readers_left or (n is not None and n != abs(moved_left))):
                flags.append({"rule": "other_move_side", "claim": match.group(0),
                              "evidence": f"the prompt: moved {moved_left:+d} lane(s) to own left"})
        moved_plus_y = int(seen.get("lanes_moved_plus_y") or 0)
        for match in OTHER_MOVE_WALL.finditer(texts):
            to_blue = match.group("wall").lower() == "blue"  # the blue wall is at +y
            if moved_plus_y != 0 and (moved_plus_y > 0) != to_blue:
                flags.append({"rule": "other_move_wall", "claim": match.group(0),
                              "evidence": f"the prompt: moved {moved_plus_y:+d} lane(s) towards the blue wall"})
        if point["frame"] == "absolute":
            for match in OTHER_LANE_NUMBER.finditer(texts):
                if int(match.group("lane")) != lane_number(view, seen["lane"]):
                    flags.append({"rule": "other_lane_number", "claim": match.group(0),
                                  "evidence": f"the prompt: lane {lane_number(view, seen['lane'])}"})
    if point["frame"] == "absolute":
        for match in OWN_LANE_NUMBER.finditer(texts):
            if int(match.group("lane")) != lane_number(view, view["lane"]):
                flags.append({"rule": "own_lane_number", "claim": match.group(0),
                              "evidence": f"the prompt: lane {lane_number(view, view['lane'])}"})
    option = point.get("option")
    # The intent's own move: only an intent that opens with a move of the speaker's own ("Step to my
    # right", "Move towards the blue wall"). A side or wall named anywhere else in it is, as often as
    # not, where the other is or went (RF-52's flags read against the replies).
    own_move = SELF_MOVE.match(point["texts"]["intent"] or "")
    if point["frame"] == "own":
        said = own_move.group("side").lower() if own_move and own_move.group("side") else None
        moved = point["coded"].get("side")
        if said in SIDES and moved in SIDES and said != moved:
            flags.append({"rule": "intent_side", "claim": own_move.group(0), "evidence": f"option: {option}"})
    else:
        said = own_move.group("wall").lower() if own_move and own_move.group("wall") else None
        wall = _option_wall(option)
        if said is not None and wall is not None and said != wall:
            flags.append({"rule": "intent_wall", "claim": own_move.group(0), "evidence": f"option: {option}"})
        if SIDE_WORDS.search(texts):
            flags.append({"rule": "uses_own_sides", "claim": SIDE_WORDS.search(texts).group(0), "evidence": "absolute frame"})
    return flags


def move_side_claims(texts: str, moved_left: int) -> tuple[int, int]:
    """``(claims, wrong)``: the claims in ``texts`` about which side the other moved to ("she moved a lane to
    her left", "they shifted to my right"), and how many put it on the wrong side, against the view's move
    in the reader's own frame (``moved_left`` > 0: to the reader's left, which is the other's own right).
    Only a view that gives a move is checked (as ``side_flags``)."""
    if moved_left == 0:
        return 0, 0
    claims = wrong = 0
    for match in OTHER_MOVE_SIDE.finditer(texts):
        side, whose = match.group("side").lower(), match.group("whose").lower()
        claims += 1
        wrong += (moved_left > 0) != (side == "left" if whose == "my" else side == "right")
    return claims, wrong


def _move_side_row(rows: Iterable[tuple[str, int]]) -> dict[str, Any]:
    with_move = [(t, m) for t, m in rows if m != 0]
    counted = [move_side_claims(t, m) for t, m in with_move]
    claiming = sum(1 for c, _ in counted if c)
    wrong_points = sum(1 for _, w in counted if w)
    return {"points_with_a_move": len(with_move), "points_claiming": claiming, "claims": sum(c for c, _ in counted),
            "wrong_claims": sum(w for _, w in counted), "wrong_among_claiming": _rate(wrong_points, claiming),
            "wrong_among_points_with_a_move": _rate(wrong_points, len(with_move))}


def move_side_comparison(points: Sequence[Mapping[str, Any]], rf40: Optional[Path]) -> dict[str, Any]:
    """The supervisor's left-and-right point (SV8), like for like: claims about the side the other moved to,
    on the grid (each frame) and in RF-40's silent condition (the continuous corridor, free steps), where
    the view gives the move as ``moved_left`` / ``moved_right`` in the reader's own frame."""
    out = {}
    for frame in ("own", "absolute"):
        rows = []
        for p in points:
            if p["frame"] != frame or not p["readable"]:
                continue
            seen = (p["grid_view"].get("seen") or [None])[0]
            rows.append((f"{p['texts']['intent']} {p['texts']['reason']}", int((seen or {}).get("lanes_moved_left") or 0)))
        out[frame] = _move_side_row(rows)
    if rf40 is not None and (rf40 / "sessions").is_dir():
        rows = []
        for path in sorted((rf40 / "sessions").glob("*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            if record.get("condition") != "silent":
                continue
            for point in record.get("decision_points") or []:
                parsed = point.get("parsed") or {}
                if point.get("parse_error") is not None or not parsed:
                    continue
                seen = ((point.get("view") or {}).get("seen") or [None])[0] or {}
                changes = seen.get("changes") or []
                moved = 1 if "moved_left" in changes else -1 if "moved_right" in changes else 0
                rows.append((f"{parsed.get('intent') or ''} {parsed.get('reason') or ''}", moved))
        out["rf40_silent"] = _move_side_row(rows)
    return out


SIDE_ERRORS = ("other_side", "other_same_lane", "other_move_side", "other_move_wall", "other_lane_number", "own_lane_number",
               "intent_side", "intent_wall")


def side_error_table(points: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for frame in ("own", "absolute"):
        mine = [p for p in points if p["frame"] == frame]
        readable = [p for p in mine if p["readable"]]
        row = {"frame": frame, "points": len(mine), "readable": len(readable)}
        for rule in (*SIDE_ERRORS, "uses_own_sides"):
            row[rule] = sum(1 for p in readable if any(f["rule"] == rule for f in p["side_flags"]))
        row["any_side_error"] = _rate(sum(1 for p in readable if any(f["rule"] in SIDE_ERRORS for f in p["side_flags"])), len(readable))
        out.append(row)
    return out


# --- the hand check (RF-45's method) --------------------------------------------------------------


def key_of(point: Mapping[str, Any]) -> str:
    return f"{point['run']}/{point['session_id']}/dp{point['index']}"


def hand_sample(points: Sequence[Mapping[str, Any]], n_per_frame: int, seed: int = 141) -> list[str]:
    rng = random.Random(seed)
    chosen = []
    for frame in ("own", "absolute"):
        keys = sorted(key_of(p) for p in points if p["frame"] == frame)
        chosen += sorted(rng.sample(keys, min(n_per_frame, len(keys))))
    return chosen


def facts(point: Mapping[str, Any]) -> str:
    """What the prompt gave, briefly, for reading a reply against it."""
    v = point["grid_view"]
    lanes, lane, d = v["lanes"], v["lane"], v["direction"]
    left = (lanes - 1 - lane) if d > 0 else lane
    parts = [f"own lanes to the wall: left {left}, right {lanes - 1 - left}; lane {lane_number(v, lane)} from the blue wall"]
    for s in v.get("seen") or []:
        off = s["lanes_left"]
        where = "same lane" if off == 0 else f"{abs(off)} lane(s) to own {'left' if off > 0 else 'right'}"
        parts.append(f"other: {s['cells_ahead']} cells ahead, {where} (lane {lane_number(v, s['lane'])}), {s['motion']}, changes {s['changes'] or '-'}"
                     + (f", moved {s['lanes_moved_left']:+d} lane(s) to own left, {s.get('lanes_moved_plus_y', 0):+d} towards the blue wall"
                        if s.get("lanes_moved_left") else ""))
    for h in v.get("history") or []:
        parts.append(f"history: {h['ago_s']:.1f} s ago '{h['intent']}' ({h['outcome']}), moved {h['lanes_left']:+d} lane(s) to own left, back {h['cells_back']}")
    lines = [line for s in v.get("seen") or [] for line in s.get("factor_lines") or []]
    if lines:
        parts.append("other's lines: " + "; ".join(lines))
    return "\n".join(f"  - {p}" for p in parts)


def hand_sheet(points: Sequence[Mapping[str, Any]], chosen: Sequence[str]) -> str:
    by_key = {key_of(p): p for p in points}
    out = ["# RF-52 hand check: hallucinated decisions on the grid", "",
           "RF-45's definition (categories 1, 2, 5, 7; 3 and 4 as self-contradiction). Each point read against what its prompt gave.", ""]
    for key in chosen:
        p = by_key[key]
        out += [f"## {key} ({p['frame']} frame, agent {p['agent_id']}, decision {p['number']})", "", facts(p), "",
                f"- **option:** {p['option']}", f"- **intent:** {p['texts']['intent']}", f"- **reason:** {p['texts']['reason']}",
                f"- **coder flags:** {sorted(_flag_keys(p)) or '-'}; side flags: {[f['rule'] for f in p['side_flags']] or '-'}", ""]
    return "\n".join(out)


def score_hand(points: Sequence[Mapping[str, Any]], judgements: Mapping[str, Any]) -> dict[str, Any]:
    """Shares from the hand check: ``judgements[key] = {"categories": [...], "side_error": bool,
    "move_against_geometry": bool, "note": ...}``, either as the mapping itself or under ``"judgements"``.

    ``move_against_geometry`` is RF-52's own: a move that, by the reply's own account of where the other
    is or went, closes the gap while the reply says it gives room. It is not one of RF-45's categories."""
    if "judgements" in judgements and isinstance(judgements["judgements"], Mapping):
        judgements = judgements["judgements"]
    by_key = {key_of(p): p for p in points}
    out = {}
    for frame in ("own", "absolute", "all"):
        keys = [k for k in judgements if k in by_key and (frame == "all" or by_key[k]["frame"] == frame)]
        hall = sum(1 for k in keys if set(judgements[k].get("categories") or []) & set(HEADLINE))
        contra = sum(1 for k in keys if set(judgements[k].get("categories") or []) & {"3", "4"})
        side = sum(1 for k in keys if judgements[k].get("side_error"))
        geometry = sum(1 for k in keys if judgements[k].get("move_against_geometry"))
        out[frame] = {"headline": _rate(hall, len(keys)), "self_contradiction": _rate(contra, len(keys)), "side_error": _rate(side, len(keys)),
                      "move_against_geometry": _rate(geometry, len(keys))}
    return out


# --- factor effects (analysis.effects, unchanged) -----------------------------------------------------


def effects_raw(rf40_outcomes: Path, sessions: pd.DataFrame, agents: pd.DataFrame) -> pd.DataFrame:
    """RF-40's outcome rows for the grid's sessions (their factor columns), with the grid's outcomes
    put in place of the continuous ones, one block per frame (its condition is the frame)."""
    rf40 = pd.read_csv(rf40_outcomes, dtype=str, keep_default_na=False, na_values=[""])
    rf40 = rf40.loc[rf40["condition"] == "silent"].set_index("session_id")
    blocks = []
    for frame, mine in sessions.groupby("frame", sort=False):
        block = rf40.loc[mine["session_id"]].reset_index().copy()
        grid = mine.set_index("session_id").loc[block["session_id"]]
        people = agents.loc[agents["frame"] == frame].set_index(["session_id", "agent"])
        block["source"] = f"grid_{frame}"
        block["session_key"] = block["source"] + "::" + block["session_id"]
        block["condition"] = CONDITION_OF[frame]
        block["geometry"] = grid["geometry"].to_numpy()
        block["outcome"] = "completed"
        block["resolved_plan_only"] = grid["resolved"].astype(bool).astype(str).to_numpy()
        for column in ("resolved_plan_orca", "resolved_by_llm", "who_passed_first_plan_only"):
            block[column] = np.nan  # not on the grid
        for person, agent_col in (("p1", "p1_agent"), ("p2", "p2_agent")):
            ids = block[agent_col].astype(int)
            rows = [people.loc[(sid, aid)] for sid, aid in zip(block["session_id"], ids)]
            block[f"{person}_decision_points"] = [str(r["decision_points"]) for r in rows]
            block[f"{person}_unreadable"] = [str(r["unreadable"]) for r in rows]
            block[f"{person}_first_side"] = [r["first_side"] if r["first_side"] in SIDES else ("none" if r["first_option"] else np.nan) for r in rows]
            for key in ("slowed", "stopped", "backed_up"):
                block[f"{person}_first_{key}"] = [str(bool(r.get(f"first_{key}"))) if r["first_option"] else np.nan for r in rows]
            block[f"{person}_first_start_distance_m"] = np.nan
            block[f"{person}_signals"] = np.nan
            block[f"{person}_debrief_kind"] = [r["debrief_kind"] for r in rows]
            for shown in ("other_age_shown", "other_gender_shown", "other_observable_shown", "other_ethnicity_shown", "pairwise_lines_shown"):
                block[f"{person}_{shown}"] = [str(int(r["decision_points"])) for r in rows]  # every grid view shows every line
        for which, agent in (("a", 0), ("b", 1)):
            rows = [people.loc[(sid, agent)] for sid in block["session_id"]]
            block[f"passing_side_{which}_plan_only"] = [r["kept_side"] for r in rows]
            block[f"stopped_{which}_plan_only"] = [str(r["waits"] > 0) for r in rows]
            block[f"backed_up_{which}_plan_only"] = [str(r["backs"] > 0) for r in rows]
        block["encounter_agents"] = "0;1"
        blocks.append(block)
    return pd.concat(blocks, ignore_index=True)


def factor_effects(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sessions_tab, _ = L.sessions_table(raw)
    agents_tab, predictors = L.agents_table(raw, sessions_tab)
    fitted = EF.run_all(agents_tab, L.varied(agents_tab, predictors), sessions_tab)
    return EF.terms_frame(fitted), EF.models_frame(fitted)


# --- the report -----------------------------------------------------------------------------------


def _pct(rate: Mapping[str, Any]) -> str:
    if not rate.get("n"):
        return "-"
    return f"{rate['k']} / {rate['n']} ({rate['rate']:.2f}, 95% CI {rate['low']:.2f} to {rate['high']:.2f})"


def analyse(folders: Sequence[Path], rf40: Optional[Path], threshold: float = 0.5, hand: Optional[Path] = None,
            n_hand: int = 50) -> dict[str, Any]:
    records = {f.name: load_records(f) for f in folders}
    sessions = pd.concat([session_rows(r) for r in records.values()], ignore_index=True)
    agents = pd.concat([agent_rows(records[f.name], f) for f in folders], ignore_index=True)
    points = [p for f in folders for p in hallucination_points(records[f.name], f.name)]
    result: dict[str, Any] = {
        "runs": [str(f) for f in folders], "threshold": threshold,
        "gate": gate_table(sessions, threshold), "measures": measures_table(sessions),
        "paired_frames": {m: paired_frames(sessions, m) for m in ("resolved", "dance", "deadlock", "blocked_face_to_face", "squeezed_past")},
        "scripted": scripted_table(folders),
        "conventions": conventions(agents, "first_side") + conventions(agents, "first_lane_change"),
        "first_options": {fr: dict(Counter(agents.loc[agents["frame"] == fr, "first_option"].fillna("(none)"))) for fr in ("own", "absolute")},
        "kept_side": {fr: dict(Counter(agents.loc[agents["frame"] == fr, "kept_side"].fillna("(not passed)"))) for fr in ("own", "absolute")},
        "unreadable": {fr: _rate(sum(1 for p in points if p["frame"] == fr and not p["readable"]), sum(1 for p in points if p["frame"] == fr))
                       for fr in ("own", "absolute")},
        "parse_errors": dict(Counter(str(p["parse_error"]).split(":")[0] for p in points if not p["readable"])),
        "coder": {fr: coder_shares([p for p in points if p["frame"] == fr]) for fr in ("own", "absolute")},
        "side_errors": side_error_table(points),
        "debriefs": {fr: dict(Counter(agents.loc[agents["frame"] == fr, "debrief_kind"].fillna("(none)"))) for fr in ("own", "absolute")},
    }
    if rf40 is not None:
        rows = pd.read_csv(rf40 / "outcomes.csv", dtype=str, keep_default_na=False, na_values=[""])
        silent = rows.loc[(rows["condition"] == "silent") & (rows["outcome"] == "completed")]
        result["rf40_silent"] = _rate(int((silent["resolved_plan_only"] == "True").sum()), len(silent))
        alone = silent.loc[silent["pair_id"].isna()]  # RF-40's report quotes 163 / 256: its pairs left out
        result["rf40_silent_without_pairs"] = _rate(int((alone["resolved_plan_only"] == "True").sum()), len(alone))
        result["paired_with_rf40"] = paired_with_rf40(sessions, silent)
        result["move_side"] = move_side_comparison(points, rf40)
        raw = effects_raw(rf40 / "outcomes.csv", sessions, agents)
        terms, models = factor_effects(raw)
        result["effects"] = {"significant": terms.loc[terms.get("significant", pd.Series(dtype=bool)).fillna(False).astype(bool)].to_dict("records")
                             if "significant" in terms.columns else [], "models": len(models)}
        result["_terms"], result["_models"] = terms, models
    if hand is not None and hand.is_file():
        result["hand_check"] = score_hand(points, json.loads(hand.read_text(encoding="utf-8")))
    result["hand_sample"] = hand_sample(points, n_hand)
    result["_sessions"], result["_agents"], result["_points"] = sessions, agents, points
    return result


def write(result: Mapping[str, Any], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    public = {k: v for k, v in result.items() if not k.startswith("_")}
    (out / "grid.json").write_text(json.dumps(public, indent=2, default=str) + "\n", encoding="utf-8")
    result["_sessions"].to_csv(out / "sessions.csv", index=False, lineterminator="\n")
    result["_agents"].to_csv(out / "agents.csv", index=False, lineterminator="\n")
    pd.DataFrame([{
        "key": key_of(p), "frame": p["frame"], "readable": p["readable"], "option": p["option"],
        "intent": p["texts"]["intent"], "reason": p["texts"]["reason"],
        "coder_flags": ";".join(sorted(_flag_keys(p))), "side_flags": ";".join(f["rule"] for f in p["side_flags"]),
        "side_claims": " | ".join(f"{f['rule']}: {f['claim']} ({f['evidence']})" for f in p["side_flags"]),
    } for p in result["_points"]]).to_csv(out / "points.csv", index=False, lineterminator="\n")
    if "_terms" in result:
        result["_terms"].to_csv(out / "effects_terms.csv", index=False, lineterminator="\n")
        result["_models"].to_csv(out / "effects_models.csv", index=False, lineterminator="\n")
    (out / "hand_check_sheet.md").write_text(hand_sheet(result["_points"], result["hand_sample"]), encoding="utf-8", newline="\n")
    (out / "grid.md").write_text(markdown(public), encoding="utf-8", newline="\n")


def markdown(r: Mapping[str, Any]) -> str:
    lines = ["# RF-52: round 1 on the grid (generated tables)", "",
             "Generated by `python -m analysis.grid`; the report with its reading is `report.md`.", "",
             f"## The gate (threshold {r['threshold']:.2f}, resolved in the agents' own plans)", "",
             "| Frame | Layout | Resolved | Gate |", "| --- | --- | --- | --- |"]
    for g in r["gate"]:
        lines.append(f"| {g['frame']} | {g['layout']} | {_pct(g)} | {g['gate'] or ''} |")
    if "rf40_silent" in r:
        lines += ["", f"RF-40's silent condition (free steps, continuous corridor, `plan_only`): {_pct(r['rf40_silent'])}; "
                  f"pairs left out, as RF-40's report: {_pct(r['rf40_silent_without_pairs'])}."]
    if "paired_with_rf40" in r:
        lines += ["", "Session by session against RF-40's silent condition (the same session ids):", "",
                  "| Frame | Pairs | Both resolved | Grid only | RF-40 only | Neither | McNemar exact p |", "| --- | --- | --- | --- | --- | --- | --- |"]
        for p in r["paired_with_rf40"]:
            lines.append(f"| {p['frame']} | {p['pairs']} | {p['both']} | {p['grid_only']} | {p['rf40_only']} | {p['neither']} | {p['mcnemar_exact_p']:.3g} |")
    lines += ["", "## Scripted walkers on the same lanes and seeds (context only)", "", "| Run | Script | Resolved | Dance | Deadlock |",
              "| --- | --- | --- | --- | --- |"]
    for s in r["scripted"]:
        lines.append(f"| {s['run']} | {s['script']} | {_pct(s)} | {s['dance']} | {s['deadlock']} |")
    lines += ["", "## RF-50's measures", "", "| Frame | Layout | n | " + " | ".join(MEASURES) + " | median time to pass (s) | decision points (mean) |",
              "| --- | --- | --- | " + " | ".join("---" for _ in MEASURES) + " | --- | --- |"]
    for m in r["measures"]:
        lines.append(f"| {m['frame']} | {m['layout']} | {m['n']} | " + " | ".join(str(m[k]) for k in MEASURES)
                     + f" | {m['time_to_pass_s_median'] if m['time_to_pass_s_median'] is None else round(m['time_to_pass_s_median'], 2)} | {m['decision_points_mean']:.2f} |")
    lines += ["", "Passing distances (m: sessions): " + "; ".join(f"{m['frame']}/{m['layout']} {m['passing_distance_m']}" for m in r["measures"] if m["layout"] == "all"),
              "", "## The two frames, paired session by session", "", "| Measure | Pairs | Both | Own only | Absolute only | Neither | McNemar exact p |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for p in r["paired_frames"].values():
        lines.append(f"| {p['measure']} | {p['pairs']} | {p['both']} | {p['own_only']} | {p['absolute_only']} | {p['neither']} | {p['mcnemar_exact_p']:.3g} |")
    lines += ["", "## Sides", "", "| Frame | Read from | Both right | Both left | One each (same wall) | One only | Neither |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for c in r["conventions"]:
        lines.append(f"| {c['frame']} | {c['column']} | {c.get('both_right', 0)} | {c.get('both_left', 0)} | {c.get('same_wall', 0)} | {c.get('one_only', 0)} | {c.get('neither', 0)} |")
    lines += ["", f"Side kept when passing (own frame of each agent): {r['kept_side']}", "", f"First options: {r['first_options']}", "",
              "## Side errors (the grid's checks)", "", "| Frame | Readable points | " + " | ".join((*SIDE_ERRORS, "uses_own_sides")) + " | Any side error |",
              "| --- | --- | " + " | ".join("---" for _ in range(len(SIDE_ERRORS) + 1)) + " | --- |"]
    for s in r["side_errors"]:
        lines.append(f"| {s['frame']} | {s['readable']} | " + " | ".join(str(s[k]) for k in (*SIDE_ERRORS, "uses_own_sides")) + f" | {_pct(s['any_side_error'])} |")
    if "move_side" in r:
        lines += ["", "## Which side the other moved to: the grid against RF-40's silent condition (SV8)", "",
                  "Readable decision points whose view gives a move of the other; a claim is \"she moved to her left\", \"they shifted to my right\".", "",
                  "| Run | Points with a move | Points with a claim | Claims | Wrong claims | Wrong, of points with a claim | Wrong, of points with a move |",
                  "| --- | --- | --- | --- | --- | --- | --- |"]
        for name, m in r["move_side"].items():
            lines.append(f"| {name} | {m['points_with_a_move']} | {m['points_claiming']} | {m['claims']} | {m['wrong_claims']} | "
                         f"{_pct(m['wrong_among_claiming'])} | {_pct(m['wrong_among_points_with_a_move'])} |")
    lines += ["", "## Unreadable replies and RF-45's coder", ""]
    for fr in ("own", "absolute"):
        lines.append(f"- {fr}: unreadable after the retry {_pct(r['unreadable'][fr])}; coder, reliable rules {_pct(r['coder'][fr]['reliable'])}; "
                     f"all rules' headline {_pct(r['coder'][fr]['headline_all_rules'])}; by rule {r['coder'][fr]['by_rule']}")
    lines.append(f"- parse errors: {r['parse_errors']}")
    if "hand_check" in r:
        lines += ["", "## The hand check", ""]
        for fr, v in r["hand_check"].items():
            lines.append(f"- {fr}: hallucinated {_pct(v['headline'])}; self-contradiction {_pct(v['self_contradiction'])}; side error {_pct(v['side_error'])}; "
                         f"move against its own geometry {_pct(v['move_against_geometry'])}")
    if "effects" in r:
        lines += ["", f"## Factor effects (Holm over all {r['effects']['models']} models; significant terms)", "",
                  "| Outcome | Subset | Term | OR (logistic) or coefficient | 95% CI | Holm p |", "| --- | --- | --- | --- | --- | --- |"]
        for t in r["effects"]["significant"]:
            odds = t.get("odds_ratio")
            has_or = odds is not None and not (isinstance(odds, float) and math.isnan(odds))
            est, low, high = (odds, t["or_low"], t["or_high"]) if has_or else (t["estimate"], t["ci_low"], t["ci_high"])
            lines.append(f"| {t.get('outcome')} | {t.get('subset')} | {t.get('term')} | {est:.2f} | {low:.2f} to {high:.2f} | {t['p_holm']:.3g} |")
    lines += ["", f"## Debriefs", "", f"{r['debriefs']}", ""]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m analysis.grid", description="RF-52: round 1 on the grid (#141).")
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--rf40", type=Path, help="RF-40's run folder (its outcomes.csv): the baseline and the factor columns")
    parser.add_argument("--hand", type=Path, help="the hand check's judgements (JSON)")
    parser.add_argument("--n-hand", type=int, default=50, help="decision points per frame in the hand-check sample")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    result = analyse(args.runs, args.rf40, args.threshold, args.hand, args.n_hand)
    write(result, args.out)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
