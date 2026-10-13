"""Trajectory plot of one run, drawn from its log folder.

    python -m negsim.viz.trajectory_plot runs/<experiment>/<run_id> [output.png]

Plots are made on demand and are not part of a run's log folder: the logs are small text
files that are committed, and images are not.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Optional

from ..runlog.schema import CONFIG_FILE, OUTCOME_FILE, TRAJECTORY_FILE

_COLOURS = ("tab:blue", "tab:red", "tab:green", "tab:purple")


def plot_run(run_dir: Path | str, output: Optional[Path | str] = None) -> Path:
    """Draw the walls, the desired paths and the paths actually taken; return the image path."""
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import patches
    from matplotlib import pyplot as plt

    run_dir = Path(run_dir)
    config = json.loads((run_dir / CONFIG_FILE).read_text(encoding="utf-8"))
    outcome = json.loads((run_dir / OUTCOME_FILE).read_text(encoding="utf-8"))
    tracks: dict[int, list[tuple[float, float]]] = {}
    with (run_dir / TRAJECTORY_FILE).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            tracks.setdefault(int(row["agent_id"]), []).append((float(row["x_m"]), float(row["y_m"])))

    figure, axis = plt.subplots(figsize=(8, 5))
    for obstacle in config["scenario"]["obstacles"]:
        axis.add_patch(
            patches.Rectangle(
                (obstacle["xmin"], obstacle["ymin"]),
                obstacle["xmax"] - obstacle["xmin"],
                obstacle["ymax"] - obstacle["ymin"],
                color="0.3",
            )
        )
    for agent in config["scenario"]["agents"]:
        agent_id, colour = agent["agent_id"], _COLOURS[agent["agent_id"] % len(_COLOURS)]
        xs, ys = zip(*agent["path"])
        axis.plot(xs, ys, linestyle=":", color=colour, linewidth=1)
        track = tracks.get(agent_id, [])
        if track:
            xs, ys = zip(*track)
            axis.plot(xs, ys, color=colour, linewidth=2, label=f"agent {agent_id} ({agent['side']})")
            axis.add_patch(patches.Circle(track[0], agent["radius_m"], fill=False, color=colour))
            axis.add_patch(patches.Circle(track[-1], agent["radius_m"], color=colour, alpha=0.4))
        axis.plot(agent["goal"]["x"], agent["goal"]["y"], marker="x", color=colour, markersize=9)
    axis.set_aspect("equal", adjustable="datalim")
    axis.set_xlabel("x (m)")
    axis.set_ylabel("y (m)")
    axis.set_title(f"{config['run_id']}: {outcome['status']}, first through: agent {outcome['first_through']}")
    axis.legend(loc="best")
    axis.autoscale_view()

    output = Path(output) if output is not None else run_dir / "trajectory.png"
    figure.savefig(output, dpi=120, bbox_inches="tight")
    plt.close(figure)
    return output


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        raise SystemExit(__doc__)
    print(plot_run(*sys.argv[1:]))
