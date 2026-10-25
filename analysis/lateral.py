"""How far apart sideways two head-on walkers were when level, and how far each moved aside
(issue #65, RF-10): why a `plan_only` encounter did or did not resolve.

For each of the design's sessions (first runs, no counterfactual pair; as ``analysis.gate``), it
reads the ``plan_only`` replay's ``trajectory.csv`` and takes the step at which the two are level
along the corridor (the smallest difference in x). There it measures their **lateral separation**
(the difference in y) and how far **each moved aside** from its own starting line. The sessions
are grouped by outcome: resolved, collision, near miss. Head-on cases only: agent 0 walks towards
+x and agent 1 towards -x along the corridor's axis. Standard library only.

**Which way each stepped** (added after PR #95's first report): each agent's move aside in its
own frame (agent 0's left is +y, agent 1's left is -y), classed as

- ``same_own_side``: both moved to their own left, or both to their own right (they make room);
- ``towards_same_wall``: one moved to its left and the other to its right, so both moved towards
  the same wall (the "pavement dance");
- ``not_both_aside``: one or both moved less than ``MOVED_M`` from its starting line.

The side each went by on at the closest approach (``passing_side_*`` in ``outcomes.csv``) cannot
show this: for two people walking towards each other it always agrees, whoever moved.
``MOVED_M`` (5 cm) is a judgement, not a sourced number.

    python -m analysis.lateral llm_negotiation/runs/rf10_round1_head_on
"""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from .gate import design_rows

#: A move aside smaller than this (metres) counts as not moving aside.
MOVED_M = 0.05
SIDESTEPS = ("same_own_side", "towards_same_wall", "not_both_aside")


def outcome_of(row: Mapping[str, str]) -> str:
    if row["resolved_plan_only"] == "True":
        return "resolved"
    return "collision" if row["collision_plan_only"] == "True" else "near_miss"


def sidestep(own_0_m: float, own_1_m: float) -> str:
    """Which way the two stepped, from each one's move to its own left (metres, negative: right)."""
    if abs(own_0_m) < MOVED_M or abs(own_1_m) < MOVED_M:
        return "not_both_aside"
    return "same_own_side" if (own_0_m > 0) == (own_1_m > 0) else "towards_same_wall"


def when_level(trajectory: Path) -> dict[str, float]:
    """Lateral separation when level, and each agent's move aside from its own start (metres).

    ``own_0_m`` and ``own_1_m`` are the same moves signed in each agent's own frame: positive to
    its left."""
    track: dict[int, dict[int, tuple[float, float]]] = defaultdict(dict)
    with trajectory.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            track[int(row["step"])][int(row["agent_id"])] = (float(row["x_m"]), float(row["y_m"]))
    steps = sorted(step for step, bodies in track.items() if 0 in bodies and 1 in bodies)
    if not steps:
        raise ValueError(f"{trajectory}: the two are never on the same step")
    start = track[steps[0]]
    level = min(steps, key=lambda step: abs(track[step][0][0] - track[step][1][0]))
    (_, y0), (_, y1) = track[level][0], track[level][1]
    own_0, own_1 = y0 - start[0][1], -(y1 - start[1][1])
    return {
        "separation_m": abs(y0 - y1), "aside_0_m": abs(own_0), "aside_1_m": abs(own_1),
        "own_0_m": own_0, "own_1_m": own_1,
    }


def summarise(experiment: Path) -> dict[str, dict[str, Any]]:
    with (experiment / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        rows = [row for row in design_rows(list(csv.DictReader(handle))) if row["outcome"] == "completed"]
    groups: dict[str, list[dict[str, float]]] = defaultdict(list)
    for row in rows:
        groups[outcome_of(row)].append(when_level(experiment / "replay" / row["session_id"] / "plan_only" / "trajectory.csv"))
    out = {}
    for name, found in sorted(groups.items()):
        separations = [f["separation_m"] for f in found]
        asides = [f[key] for f in found for key in ("aside_0_m", "aside_1_m")]
        quartiles = statistics.quantiles(separations, n=4) if len(separations) > 1 else [separations[0]] * 3
        out[name] = {
            "sessions": len(found),
            "separation_median_m": round(statistics.median(separations), 3),
            "separation_iqr_m": [round(quartiles[0], 3), round(quartiles[2], 3)],
            "aside_median_m": round(statistics.median(asides), 3),
            "sidesteps": {kind: sum(1 for f in found if sidestep(f["own_0_m"], f["own_1_m"]) == kind) for kind in SIDESTEPS},
        }
    return out


def markdown(summary: Mapping[str, Mapping[str, Any]]) -> str:
    lines = ["| plan_only outcome | Sessions | Lateral separation when level, median (IQR) | Each agent's move aside, median |",
             "| --- | --- | --- | --- |"]
    for name, s in summary.items():
        low, high = s["separation_iqr_m"]
        lines.append(f"| {name} | {s['sessions']} | {s['separation_median_m']:.2f} m ({low:.2f} to {high:.2f}) | {s['aside_median_m']:.2f} m |")
    lines += ["", f"Which way each stepped, when level (a move under {MOVED_M * 100:.0f} cm counts as none):", "",
              "| plan_only outcome | Both to their own same side | Towards the same wall | One or both not aside |",
              "| --- | --- | --- | --- |"]
    for name, s in summary.items():
        counts = s["sidesteps"]
        lines.append(f"| {name} | {counts['same_own_side']} | {counts['towards_same_wall']} | {counts['not_both_aside']} |")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m analysis.lateral", description=__doc__.split("\n\n")[0])
    parser.add_argument("experiment", type=Path, help="the experiment's folder (outcomes.csv and replay/)")
    args = parser.parse_args(argv)
    text = markdown(summarise(args.experiment))
    out = args.experiment / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    (out / "lateral.md").write_text(text, encoding="utf-8", newline="\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
