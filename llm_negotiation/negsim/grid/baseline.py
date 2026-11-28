"""The scripted walkers on RF-52's sessions (issue #141): a reference rate for the gate, no model call.

    python -m negsim.grid.baseline runs/rf52_round1_grid runs/rf52_round1_grid_abs

For every completed session record in a grid run folder, RF-50's scripted pairs
(:data:`negsim.grid.walkers.SCRIPTS`) walk the same corridor from the same lanes with the same seed
(so the same contest draws), and RF-50's measures are taken. The result is written beside the run
as ``scripted_walkers.csv``: one row per session and script.

**What it is for** (#141, the open decision): in RF-50's check, random walkers (mostly forward)
resolved 10 of 20 runs on each geometry, the same as RF-10's threshold. The user chose RF-10's 0.50
as the grid's gate on 2026-11-26; the random walkers' rate on the same sessions is reported beside
the LLM's only as context, and decides nothing.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from .measures import pair_outcome
from .walkers import SCRIPTS
from .world import head_on, load_config, run

COLUMNS = ("session_id", "grid_geometry", "off_centre", "lane_p1", "lane_p2", "seed", "script", "resolved", "passed",
           "blocked_face_to_face", "squeezed_past", "dance", "deadlock", "ended_by", "passing_distance_m", "time_to_pass_s")


def scripted_rows(record: dict[str, Any], scripts: Sequence[str] = tuple(SCRIPTS)) -> list[dict[str, Any]]:
    """Each script on one session's lanes and seed."""
    config = load_config(record["grid"]["source"])
    rows = []
    for script in scripts:
        p0, p1 = SCRIPTS[script]()
        outcome = pair_outcome(run(head_on(config, record["lanes"], record["seed"]), {0: p0, 1: p1}))
        rows.append({
            "session_id": record["session_id"], "grid_geometry": record["grid_geometry"], "off_centre": record["off_centre"],
            "lane_p1": record["lanes"][0], "lane_p2": record["lanes"][1], "seed": record["seed"], "script": script,
            **{key: outcome[key] for key in COLUMNS[7:]},
        })
    return rows


def write(experiment_dir: Path) -> Path:
    rows = []
    for path in sorted((experiment_dir / "sessions").glob("*.json")):
        if ".aborted" in path.name:
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["outcome"] == "completed":
            rows.extend(scripted_rows(record))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    target = experiment_dir / "scripted_walkers.csv"
    target.write_text(out.getvalue(), encoding="utf-8", newline="\n")
    return target


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m negsim.grid.baseline", description=__doc__.splitlines()[0])
    parser.add_argument("runs", nargs="+", type=Path, help="grid run folders (each with sessions/)")
    args = parser.parse_args(argv)
    for folder in args.runs:
        print(write(folder))
    return 0


if __name__ == "__main__":
    sys.exit(main())
