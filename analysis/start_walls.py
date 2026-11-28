"""How a head-on pair started, and whether they recovered (issue #155, RF-54).

For each silent design session (every repeat, no counterfactual pair: ``_x`` in the id), it reads
``decisions.jsonl`` and takes the first sidestep each person planned, in decision order, and the wall
it goes towards. Agent 0 walks towards +x and agent 1 towards -x, so agent 0's left is the +y wall and
agent 1's left the -y wall (as ``analysis.lateral``). The session's **start** is

- ``same_wall``: both first sidesteps go towards the same wall (one to its own left, the other to its
  own right): the frame error of RF-43;
- ``opposite_walls``: they go towards opposite walls (both to their own left, or both to their own right);
- ``one_never_sidesteps``: one or both planned no sidestep at all.

A **dance** is both people planning a sidestep towards the other wall at decision times less than
``DANCE_WITHIN_S`` apart: D5's least gap between two decision points of one person (``min_gap_s``,
1.0 s), so neither can have been asked again in between. Under the turn-taking exchange the second
may be asked 0.1 s after the first (6.4 s and 6.5 s), before a move begun at 6.4 s is 0.1 m aside;
in silent neither sees the other's new choice first. The window is a judgement, not a sourced number.

The outcome is ``plan_only``'s (``resolved_plan_only``). Only planned sidesteps are read, not turns:
a turn by degrees has no amount to compare (``analysis.lateral`` measures the moves themselves).
Standard library only.

    python -m analysis.start_walls llm_negotiation/runs/rf40_round1_head_on_turn_taking llm_negotiation/runs/rf54_round1_head_on_sideways_gap
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

STARTS = ("same_wall", "opposite_walls", "one_never_sidesteps")
#: Two changes of wall less than this many seconds apart are at once (D5's ``min_gap_s``).
DANCE_WITHIN_S = 1.0
#: Agent 0 faces +x (its left is +y), agent 1 faces -x (its left is -y).
FACING = {0: 1, 1: -1}


def design_sessions(run: Path, condition: str = "silent") -> dict[str, Mapping[str, str]]:
    """The run's completed design sessions in ``condition``: every repeat, no counterfactual pair."""
    with (run / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        return {r["session_id"]: r for r in csv.DictReader(handle)
                if r["condition"] == condition and r["outcome"] == "completed" and "_x" not in r["session_id"]}


def sidesteps(decisions: Sequence[Mapping[str, Any]]) -> list[tuple[float, int]]:
    """One person's planned sidesteps, in decision order: (decision time, wall), the wall +1 for +y and
    -1 for -y; the first sidestep of each reply only."""
    found = []
    for d in sorted(decisions, key=lambda d: d["number"]):
        for step in d.get("steps") or []:
            if isinstance(step, dict) and isinstance(step.get("sidestep"), dict) and step["sidestep"].get("to") in ("left", "right"):
                found.append((round(float(d["time_s"]), 3), (1 if step["sidestep"]["to"] == "left" else -1) * FACING[int(d["agent_id"])]))
                break
    return found


def classify(by_agent: Mapping[int, Sequence[Mapping[str, Any]]]) -> dict[str, Any]:
    """A session's start, and whether the two changed wall at the same decision time."""
    steps = {agent: sidesteps(by_agent.get(agent, ())) for agent in FACING}
    if not steps[0] or not steps[1]:
        start = "one_never_sidesteps"
    else:
        start = "same_wall" if steps[0][0][1] == steps[1][0][1] else "opposite_walls"
    changed = {agent: [t for (_, w), (t, w2) in zip(s, s[1:]) if w != w2] for agent, s in steps.items()}
    dance = any(abs(t0 - t1) < DANCE_WITHIN_S - 1e-9 for t0 in changed[0] for t1 in changed[1])
    return {"start": start, "dance": dance, "reversed": any(changed.values())}


def sessions(run: Path, condition: str = "silent") -> dict[str, dict[str, Any]]:
    rows = design_sessions(run, condition)
    decisions: dict[str, dict[int, list]] = defaultdict(lambda: defaultdict(list))
    with (run / "decisions.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            d = json.loads(line)
            if d["session_id"] in rows:
                decisions[d["session_id"]][int(d["agent_id"])].append(d)
    return {sid: {**classify(decisions[sid]), "resolved": row["resolved_plan_only"] == "True"} for sid, row in rows.items()}


def table(found: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for start in STARTS:
        mine = [s for s in found.values() if s["start"] == start]
        out[start] = {"n": len(mine), "resolved": sum(s["resolved"] for s in mine),
                      "dance": sum(s["dance"] for s in mine), "dance_failed": sum(s["dance"] and not s["resolved"] for s in mine)}
    return out


def paired(base: Mapping[str, Mapping[str, Any]], new: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Sessions in both runs: how the start moved, and recovery from a same-wall start in each."""
    both = sorted(set(base) & set(new))
    moves = Counter((base[s]["start"], new[s]["start"]) for s in both)
    return {"n": len(both), "start_moves": {f"{a} -> {b}": n for (a, b), n in sorted(moves.items())}}


def markdown(name: str, counts: Mapping[str, Mapping[str, int]]) -> str:
    lines = [f"## {name}", "", "| Start | Sessions | Resolved | Dance (both change wall at once) | Dance, failed |", "| --- | --- | --- | --- | --- |"]
    total = sum(c["n"] for c in counts.values())
    for start, c in counts.items():
        share = f" ({c['n'] / total:.2f})" if total else ""
        rate = f" ({c['resolved'] / c['n']:.2f})" if c["n"] else ""
        lines.append(f"| {start} | {c['n']}{share} | {c['resolved']}{rate} | {c['dance']} | {c['dance_failed']} |")
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("runs", nargs="+", type=Path, help="run folders; with two, the second is paired with the first")
    parser.add_argument("--condition", default="silent")
    args = parser.parse_args(argv)
    found = [sessions(run, args.condition) for run in args.runs]
    for run, mine in zip(args.runs, found):
        print(markdown(run.name, table(mine)) + "\n")
    if len(found) == 2:
        print("## Paired\n\n" + json.dumps(paired(*found), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
