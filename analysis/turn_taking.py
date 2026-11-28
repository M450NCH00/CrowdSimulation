"""Talk as a turn-taking exchange (issue #129, RF-40): what the agents said and when, whether a
listener's move fitted a side it heard named, and whether it matters who is asked first.

RF-40 ran round 1's head-on sessions under ``protocol.exchange: turn_taking`` with
``always_heard``: at a decision point the simulation pauses, those due are asked one at a time
(``first_asked`` first, counterbalanced over a cell's repeats), and a message is heard at once, in
full, by everyone in the encounter. It reads every completed design session (all repeats, no
counterfactual pair) and writes ``analysis/turn_taking.json`` and ``.md``:

1. **When talk speaks and names a side**, by decision number: replies with a message, and
   messages naming a side (``left`` or ``right``, a keyword match).
2. **A side heard, and the listener's next move.** For each readable reply whose message names a
   side, the other agent's next readable decision that heard it (in the same pause or later):
   whether its side *fits* the speaker's side at the decision it spoke (both to their own same
   side, so they make room), puts them *towards the same wall*, or one of the two did not move
   aside. Split by the message's frame (``frame_of``): ``own`` ("I'll keep left": the speaker's
   own side), ``yours`` ("on your right": the listener's side), ``both`` or ``other``. Against a
   fair coin (binomial, two-sided). Also: replies whose reason or intent restates a side in the
   other's frame ("that's my left", "(his right)"), a keyword match.
3. **Do speakers' words match their own moves?** ``own`` statements of keeping to a side against
   the speaker's coded side; "coming through on your X", which, facing each other, means the
   speaker's own other side.
4. **Who is asked first**, per condition: resolved in ``plan_only`` when person 1 was asked first
   (``first_asked`` ``p1``) and when person 2 was (Fisher's exact test, two-sided).

Every side is the decision point's coded side (``coded.side``, in the agent's own frame), as in
``analysis.sidestep_reprompt``. "Fits" compares the listener's side with the speaker's side at the
decision it spoke, not with where the speaker ended up: a speaker may change side again. The
keyword matches are the assistant's coding choices, not a reading of every text.

    python -m analysis.turn_taking llm_negotiation/runs/rf40_round1_head_on_turn_taking
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .gate import COMPLETED
from .sidestep_reprompt import NAMES_A_SIDE, SIDES, fisher_exact

FRAMES = ("own", "yours", "both", "other")
FITS = ("fits", "towards_same_wall", "not_both_aside")
YOURS = re.compile(r"\byour (left|right)\b", re.IGNORECASE)
OWN = re.compile(
    r"\b(?:i'?ll|i will|i'?m|i am)\s+(?:keep(?:ing)?|stay(?:ing)?|go(?:ing)?|mov(?:e|ing))\s+(?:over\s+)?(?:to\s+)?(?:my\s+|the\s+)?(left|right)\b"
    r"|\bmy (left|right)\b",
    re.IGNORECASE,
)
KEEPING = re.compile(
    r"\b(?:i'?ll|i will|i'?m|i am)\s+(?:keep(?:ing)?|stay(?:ing)?)\s+(?:to\s+)?(?:my\s+|the\s+)?(left|right)\b", re.IGNORECASE
)
COMING_THROUGH = re.compile(r"\bcoming (?:through|past|by) on your (left|right)\b", re.IGNORECASE)
TRANSLATES = re.compile(
    r"(?:that'?s|which is|is) (?:my|his|her|their) (?:left|right)|\((?:my|his|her|their) (?:left|right)\)", re.IGNORECASE
)
OTHER_SIDE = {"left": "right", "right": "left"}


def frame_of(message: str) -> str:
    """The frame a side is named in: ``own``, ``yours``, ``both`` or ``other``."""
    own, yours = bool(OWN.search(message)), bool(YOURS.search(message))
    return "both" if own and yours else "own" if own else "yours" if yours else "other"


def fit(speaker_side: Optional[str], listener_side: Optional[str]) -> str:
    """Whether two head-on sides, each in its own frame, make room (``fits``)."""
    if speaker_side not in SIDES or listener_side not in SIDES:
        return "not_both_aside"
    return "fits" if speaker_side == listener_side else "towards_same_wall"


def words_match_move(message: str, side: Optional[str]) -> Optional[tuple[str, bool]]:
    """``(kind, matches)`` for a statement of the speaker's own side, or None."""
    if side not in SIDES:
        return None
    found = KEEPING.search(message)
    if found:
        return "keeping_to_my_side", found.group(1).lower() == side
    found = COMING_THROUGH.search(message)
    if found:  # on the listener's right, facing each other, is the speaker's own left
        return "coming_through_on_your_side", OTHER_SIDE[found.group(1).lower()] == side
    return None


def binomial_two_sided(k: int, n: int) -> float:
    """The two-sided binomial test of ``k`` of ``n`` against a fair coin."""
    if n == 0:
        return 1.0
    p = [math.comb(n, i) / 2**n for i in range(n + 1)]
    return min(1.0, sum(x for x in p if x <= p[k] * (1 + 1e-9)))


def load(experiment: Path) -> list[dict[str, Any]]:
    """Every completed design session, its decision points in the order they were asked."""
    with (experiment / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["outcome"] == COMPLETED and not row.get("pair_id")]
    sessions = []
    for row in rows:
        record = json.loads((experiment / "sessions" / f"{row['session_id']}.json").read_text(encoding="utf-8"))
        points = []
        for point in sorted(record.get("decision_points") or [], key=lambda p: (p["step"], p.get("turn", 0))):
            parsed = point.get("parsed") or {}
            readable = not point.get("parse_error") and bool(parsed)
            points.append({
                "agent_id": point["agent_id"], "number": point["number"], "step": point["step"], "readable": readable,
                "side": (point.get("coded") or {}).get("side") if readable else None,
                "message": parsed.get("message") or "",
                "reason": f"{parsed.get('reason') or ''} {parsed.get('intent') or ''}",
                "heard": [h.get("message") for h in (point.get("view") or {}).get("heard") or []],
            })
        sessions.append({
            "session_id": row["session_id"], "condition": row["condition"], "first_asked": row.get("first_asked") or None,
            "resolved": row["resolved_plan_only"] == "True", "points": points,
        })
    return sessions


def heard_sides(session: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Each readable message naming a side, with the other's next readable decision that heard it."""
    found = []
    points = session["points"]
    for i, point in enumerate(points):
        if not point["readable"] or not NAMES_A_SIDE.search(point["message"]):
            continue
        listener = next(
            (q for q in points[i + 1:] if q["agent_id"] != point["agent_id"] and q["readable"] and point["message"] in q["heard"]), None
        )
        if listener is None:
            continue
        found.append({
            "session_id": session["session_id"], "frame": frame_of(point["message"]), "fit": fit(point["side"], listener["side"]),
            "same_pause": listener["step"] == point["step"], "translates": bool(TRANSLATES.search(listener["reason"])),
            "message": point["message"], "reply": listener["message"],
        })
    return found


def summarise(sessions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    talk = [s for s in sessions if s["condition"] == "talk"]
    by_number: dict[int, Counter] = defaultdict(Counter)
    consistency: dict[str, Counter] = defaultdict(Counter)
    for session in talk:
        for point in session["points"]:
            if not point["readable"]:
                continue
            counts = by_number[point["number"]]
            counts["replies"] += 1
            counts["spoke"] += bool(point["message"])
            counts["names_a_side"] += bool(NAMES_A_SIDE.search(point["message"]))
            matched = words_match_move(point["message"], point["side"])
            if matched:
                consistency[matched[0]]["matches" if matched[1] else "contradicts"] += 1
    heard = [entry for session in talk for entry in heard_sides(session)]
    by_frame: dict[str, Counter] = defaultdict(Counter)
    for entry in heard:
        by_frame[entry["frame"]][entry["fit"]] += 1
        by_frame["all"][entry["fit"]] += 1
        by_frame["all, same pause" if entry["same_pause"] else "all, a later decision"][entry["fit"]] += 1
        by_frame["all, listener restates the side"][entry["fit"]] += entry["translates"]
    fit_tests = {}
    for frame, counts in by_frame.items():
        k, n = counts["fits"], counts["fits"] + counts["towards_same_wall"]
        fit_tests[frame] = {**{name: counts[name] for name in FITS}, "fits_of_both_aside": [k, n],
                            "p_vs_coin": round(binomial_two_sided(k, n), 4)}
    asked: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    for session in sessions:
        if session["first_asked"] in ("p1", "p2"):
            asked[session["condition"]][session["first_asked"]]["resolved" if session["resolved"] else "not_resolved"] += 1
    asked_first = {}
    for condition, by in sorted(asked.items()):
        a, b = by["p1"]["resolved"], by["p1"]["not_resolved"]
        c, d = by["p2"]["resolved"], by["p2"]["not_resolved"]
        asked_first[condition] = {"p1": [a, a + b], "p2": [c, c + d], "fisher_p": round(fisher_exact(a, b, c, d), 4)}
    return {
        "sessions": len(sessions), "talk_sessions": len(talk),
        "talk_by_decision": {str(n): dict(c) for n, c in sorted(by_number.items())},
        "heard_side": fit_tests, "words_and_moves": {k: dict(v) for k, v in consistency.items()},
        "asked_first": asked_first,
    }


def markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# RF-40: talk as a turn-taking exchange", "",
        f"{summary['sessions']} completed design sessions (all repeats, no counterfactual pair), "
        f"{summary['talk_sessions']} of them in talk.", "",
        "## 1. Talk: replies that speak, and that name a side, by decision number", "",
        "| Decision | Readable replies | With a message | Naming a side |", "| --- | --- | --- | --- |",
    ]
    for number, c in summary["talk_by_decision"].items():
        lines.append(f"| {number} | {c.get('replies', 0)} | {c.get('spoke', 0)} | {c.get('names_a_side', 0)} |")
    lines += [
        "", "## 2. A side heard, and the listener's next move", "",
        "`fits`: the two sides make room (both to their own same side); against a fair coin over the cases where both moved aside.", "",
        "| Message's frame | fits | towards_same_wall | not_both_aside | fits of both aside | p (coin) |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for frame, t in summary["heard_side"].items():
        k, n = t["fits_of_both_aside"]
        lines.append(f"| {frame} | {t['fits']} | {t['towards_same_wall']} | {t['not_both_aside']} | {k} / {n} | {t['p_vs_coin']} |")
    lines += ["", "## 3. Speakers' words against their own moves", "", "| Statement | matches | contradicts |", "| --- | --- | --- |"]
    for kind, c in summary["words_and_moves"].items():
        lines.append(f"| {kind} | {c.get('matches', 0)} | {c.get('contradicts', 0)} |")
    lines += ["", "## 4. Who is asked first (resolved in `plan_only`)", "",
              "| Condition | Person 1 first | Person 2 first | Fisher's exact p |", "| --- | --- | --- | --- |"]
    for condition, t in summary["asked_first"].items():
        (a, n1), (c, n2) = t["p1"], t["p2"]
        lines.append(f"| {condition} | {a} / {n1} ({a / n1:.2f}) | {c} / {n2} ({c / n2:.2f}) | {t['fisher_p']} |")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m analysis.turn_taking", description=__doc__.split("\n\n")[0])
    parser.add_argument("experiment", type=Path, help="the experiment's folder (outcomes.csv and sessions/)")
    args = parser.parse_args(argv)
    summary = summarise(load(args.experiment))
    out = args.experiment / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    (out / "turn_taking.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    text = markdown(summary)
    (out / "turn_taking.md").write_text(text, encoding="utf-8", newline="\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
