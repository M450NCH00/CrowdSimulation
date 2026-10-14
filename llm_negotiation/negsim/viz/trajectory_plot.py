"""Trajectory plot of one run, drawn from its log folder.

    python -m negsim.viz.trajectory_plot runs/<experiment>/<run_id> [output.png]

Plots are made on demand and are not part of a run's log folder: the logs are small text
files that are committed, and images are not. Without ``output.png`` the image is written
into the run folder as ``trajectory.png``, which git ignores.

Both kinds of run can be drawn: a negotiation run of issue #24 and an avoidance run of
issue #26. When a run has more agents than there are colours, the agents are coloured by
group instead of one by one. To watch a run move, use ``negsim.viz.viewer``.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Optional

from ..runlog.schema import CONFIG_FILE, OUTCOME_FILE, RUN_KIND_AVOIDANCE, TRAJECTORY_FILE

_COLOURS = ("tab:blue", "tab:red", "tab:green", "tab:purple")


def _title(config: dict, outcome: dict) -> str:
    """The run, how it ended, and the one fact most worth reading off the plot."""
    if config.get("run_kind") != RUN_KIND_AVOIDANCE:
        return f"{config['run_id']}: {outcome['status']}, first through: agent {outcome['first_through']}"
    parts = [f"{config['run_id']}: {outcome['status']}", f"{outcome['arrived']} of {outcome['n_agents']} arrived"]
    collisions = outcome["collisions"]["agent_agent"] + outcome["collisions"]["agent_wall"]
    if collisions:
        parts.append(f"{collisions} collision episode{'s' if collisions != 1 else ''}")
    first = [segment["first_through"] for segment in outcome.get("single_file", []) if segment["first_through"] is not None]
    if first:
        parts.append(f"first through: agent {first[0]}")
    return ", ".join(parts)


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

    scenario = config["scenario"]
    agents = scenario["agents"]
    # A crowd is coloured by group (in an avoidance run "side" is the agent's group), so
    # that a hundred agents give two colours and two legend entries, not a hundred.
    by_group = len(agents) > len(_COLOURS)
    groups = sorted({agent["side"] for agent in agents})

    def colour_of(agent: dict) -> str:
        index = groups.index(agent["side"]) if by_group else agent["agent_id"]
        return _COLOURS[index % len(_COLOURS)]

    xs_all = [x for track in tracks.values() for x, _ in track]
    ys_all = [y for track in tracks.values() for _, y in track]
    wide = bool(xs_all) and (max(ys_all) - min(ys_all) + 1.0) < 0.3 * (max(xs_all) - min(xs_all) + 1.0)
    figure, axis = plt.subplots(figsize=(12, 4) if wide else (8, 5))
    for obstacle in scenario["obstacles"]:
        axis.add_patch(
            patches.Rectangle(
                (obstacle["xmin"], obstacle["ymin"]),
                obstacle["xmax"] - obstacle["xmin"],
                obstacle["ymax"] - obstacle["ymin"],
                color="0.3",
            )
        )
    for index, segment in enumerate(scenario.get("single_file", {}).get("segments", [])):
        axis.add_patch(
            patches.Rectangle(
                (segment["xmin"], segment["ymin"]),
                segment["xmax"] - segment["xmin"],
                segment["ymax"] - segment["ymin"],
                color="gold",
                alpha=0.25,
                label="single-file segment" if index == 0 else None,
            )
        )

    labelled: set[str] = set()
    line_width = 1.0 if by_group else 2.0
    for agent in agents:
        agent_id, colour = agent["agent_id"], colour_of(agent)
        xs, ys = zip(*agent["path"])
        axis.plot(xs, ys, linestyle=":", color=colour, linewidth=1, alpha=0.5 if by_group else 1.0)
        track = tracks.get(agent_id, [])
        if track:
            if by_group:
                label = None
                if agent["side"] not in labelled:
                    labelled.add(agent["side"])
                    count = sum(1 for other in agents if other["side"] == agent["side"])
                    label = f"{agent['side']} ({count} agents)"
            else:
                label = f"agent {agent_id} ({agent['side']})"
            xs, ys = zip(*track)
            axis.plot(xs, ys, color=colour, linewidth=line_width, alpha=0.7 if by_group else 1.0, label=label)
            axis.add_patch(patches.Circle(track[0], agent["radius_m"], fill=False, color=colour))
            axis.add_patch(patches.Circle(track[-1], agent["radius_m"], color=colour, alpha=0.4))
        if not by_group:
            axis.plot(agent["goal"]["x"], agent["goal"]["y"], marker="x", color=colour, markersize=9)
    axis.set_aspect("equal", adjustable="datalim")
    axis.set_xlabel("x (m)")
    axis.set_ylabel("y (m)")
    axis.set_title(_title(config, outcome))
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
