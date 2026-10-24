"""How far apart sideways two head-on walkers were when level, and how far each moved aside
(issue #65, RF-10): why a `plan_only` encounter did or did not resolve.

For each of the design's sessions (first runs, no counterfactual pair; as ``analysis.gate``), it
reads the ``plan_only`` replay's ``trajectory.csv`` and takes the step at which the two are level
along the corridor (the smallest difference in x). There it measures their **lateral separation**
(the difference in y) and how far **each moved aside** from its own starting line. The sessions
are grouped by outcome: resolved, collision, near miss. Head-on cases only: agent 0 walks towards
+x and agent 1 towards -x along the corridor's axis. Standard library only.

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


def outcome_of(row: Mapping[str, str]) -> str:
    if row["resolved_plan_only"] == "True":
        return "resolved"
    return "collision" if row["collision_plan_only"] == "True" else "near_miss"


def when_level(trajectory: Path) -> dict[str, float]:
    """Lateral separation when level, and each agent's move aside from its own start (metres)."""
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
    return {"separation_m": abs(y0 - y1), "aside_0_m": abs(y0 - start[0][1]), "aside_1_m": abs(y1 - start[1][1])}


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
        }
    return out


def markdown(summary: Mapping[str, Mapping[str, Any]]) -> str:
    lines = ["| plan_only outcome | Sessions | Lateral separation when level, median (IQR) | Each agent's move aside, median |",
             "| --- | --- | --- | --- |"]
    for name, s in summary.items():
        low, high = s["separation_iqr_m"]
        lines.append(f"| {name} | {s['sessions']} | {s['separation_median_m']:.2f} m ({low:.2f} to {high:.2f}) | {s['aside_median_m']:.2f} m |")
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
