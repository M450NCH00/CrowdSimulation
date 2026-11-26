"""The grid's entry point (issue #139, RF-50). No model is called.

    python -m negsim.grid scripts [--seeds 20]          # every scripted pair, both geometries: a table
    python -m negsim.grid run --script keep_right --geometry aligned --seed 1 [--print] [--out DIR]
    python -m negsim.grid cases                         # round 1's cases placed on the grid
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

from .cases import GEOMETRIES, lanes_for, round1_placements
from .measures import gate_columns, pair_outcome, trajectory_csv
from .render import print_run
from .walkers import SCRIPTS
from .world import DEFAULT_CONFIG, GridConfig, Run, as_dict, head_on, load_config, run


def run_script(config: GridConfig, script: str, geometry: str, seed: int) -> Run:
    if script not in SCRIPTS:
        raise SystemExit(f"unknown script {script!r}; known: {sorted(SCRIPTS)}")
    p0, p1 = SCRIPTS[script]()
    state = head_on(config, lanes_for(config, geometry), seed)
    return run(state, {0: p0, 1: p1})


def scripts_table(config: GridConfig, seeds: Sequence[int]) -> str:
    lines = [
        f"Scripted walkers on the grid ({config.source}; {len(seeds)} seeds each). "
        "Counts are runs out of the seeds.", "",
        "| Script | Geometry | Resolved | Passed | Squeezed past | Blocked face to face | Dance | Deadlock | Passing distance (m) | Ticks to pass |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for script in SCRIPTS:
        for geometry in GEOMETRIES:
            outcomes = [pair_outcome(run_script(config, script, geometry, seed)) for seed in seeds]
            count = lambda key: sum(bool(o[key]) for o in outcomes)  # noqa: E731
            distances = Counter(o["passing_distance_m"] for o in outcomes if o["passed"])
            ticks = sorted(o["passed_tick"] for o in outcomes if o["passed"])
            tick_text = "-" if not ticks else (str(ticks[0]) if ticks[0] == ticks[-1] else f"{ticks[0]} to {ticks[-1]}")
            dist_text = ", ".join(f"{d:.1f} ({n})" for d, n in sorted(distances.items())) or "-"
            lines.append(
                f"| {script} | {geometry} | {count('resolved')} | {count('passed')} | {count('squeezed_past')} | "
                f"{count('blocked_face_to_face')} | {count('dance')} | {count('deadlock')} | {dist_text} | {tick_text} |"
            )
    return "\n".join(lines) + "\n"


def cases_table(config: GridConfig) -> str:
    lines = ["| Case | Layout | Continuous offsets (m) | Grid lanes | Grid offsets (m) | Lost to rounding (m) |",
             "| --- | --- | --- | --- | --- | --- |"]
    for p in round1_placements(config):
        lines.append(
            f"| {p['case_id']} | {p['layout']} | {p['continuous']['lateral_offsets_m']} | {p['grid']['lanes']} | "
            f"{p['grid']['lateral_offsets_m']} | {p['rounding_lost_m']} |"
        )
    lines += ["", "The grid's geometries (lanes; the centre lane is "
              f"{config.centre_lane}): " + ", ".join(f"{g} {list(lanes_for(config, g))}" for g in GEOMETRIES)]
    return "\n".join(lines) + "\n"


def write_run(out: Path, result: Run, outcome: dict[str, Any], meta: dict[str, Any]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "trajectory.csv").write_text(trajectory_csv(result), encoding="utf-8", newline="\n")
    (out / "grid.txt").write_text(print_run(result), encoding="utf-8", newline="\n")
    record = {**meta, "grid": as_dict(result.config), "outcome": outcome, "gate_columns": gate_columns(outcome)}
    (out / "outcome.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m negsim.grid", description="The grid corridor (RF-50); no model call.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="the grid's config (default %(default)s)")
    sub = parser.add_subparsers(dest="command", required=True)
    p_scripts = sub.add_parser("scripts", help="every scripted pair on both geometries, as a table")
    p_scripts.add_argument("--seeds", type=int, default=20)
    p_run = sub.add_parser("run", help="one scripted run")
    p_run.add_argument("--script", required=True, choices=sorted(SCRIPTS))
    p_run.add_argument("--geometry", default="aligned", choices=sorted(GEOMETRIES))
    p_run.add_argument("--seed", type=int, default=1)
    p_run.add_argument("--print", action="store_true", help="print the grid at every tick")
    p_run.add_argument("--out", type=Path, help="write trajectory.csv, grid.txt and outcome.json here")
    sub.add_parser("cases", help="round 1's cases placed on the grid")
    args = parser.parse_args(argv)
    config = load_config(args.config)

    if args.command == "scripts":
        print(scripts_table(config, list(range(1, args.seeds + 1))), end="")
    elif args.command == "cases":
        print(cases_table(config), end="")
    else:
        result = run_script(config, args.script, args.geometry, args.seed)
        outcome = pair_outcome(result)
        if args.print:
            print(print_run(result))
        print(json.dumps(outcome, indent=2))
        if args.out:
            write_run(args.out, result, outcome, {"script": args.script, "geometry": args.geometry, "seed": args.seed})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
