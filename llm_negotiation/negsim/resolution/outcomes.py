"""Physical outcomes of an encounter's plans, and the report of how often plans resolve it (issue
#59, RF-4; ``docs/resolution.md``, D6 and D16).

**The general columns**, one row per session and mode, measured from the encounter's start (its
first decision) to the end of the run. ``a`` and ``b`` are the encounter's two agents, in the
order the session gives them.

| Column | Meaning |
| --- | --- |
| ``collision`` | either of the two touched someone or a wall (``collision_kinds``: ``each_other``, ``someone_else``, ``wall``) |
| ``min_separation_m`` | the smallest gap between the two bodies |
| ``near_miss`` | the two came within the scenario's ``near_miss_distance`` (a collision is one too) |
| ``deadlock`` | the run's deadlock monitor stopped it |
| ``cleared``, ``time_to_clear_s`` | both left the scenario's conflict zone, and how long after the start the second did |
| ``delay_a_s``, ``delay_b_s`` | the agent's time to its goal, minus its time in plain ORCA on the same seed |
| ``who_passed_first`` | the agent who first left the conflict zone; ``together`` if both did on the same step |
| ``passing_side_a``, ``passing_side_b`` | the side the agent went by on, in its own frame, at the closest approach: ``left`` means it kept to its left and the other went by on its right; empty if the two were not abreast then |
| ``stopped_a``, ``stopped_b`` | its speed fell below the deadlock monitor's ``speed_eps`` |
| ``backed_up_a``, ``backed_up_b``, ``backed_distance_*_m`` | it moved against its path faster than the backward-walking threshold (``metrics.md``, section 10), and how far |

The scenario adds its own columns and says what ``resolved`` means (D16).

**The report** gives the physical resolution rate per encounter type and mode, beside plain ORCA
on the same cases and seeds, and beside the C0 runs (no LLM, Strategy 1 only) of the negotiation
layer. C0's scenarios are GameChat's doorway, intersection and hallway, not these encounters: it
is shown as the existing no-LLM baseline, not as a like-for-like comparison.
"""

from __future__ import annotations

import csv
import io
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from ..configutil import PACKAGE_ROOT
from ..metrics.avoidance import ArtefactThresholds
from .scenario import Scenario

MODE_PLAIN_ORCA = "plain_orca"
TOGETHER = "together"
GENERAL_COLUMNS = (
    "session_id", "case_id", "encounter_type", "mode", "agent_a", "agent_b", "run_status", "encounter_start_s",
    "collision", "collision_kinds", "min_separation_m", "near_miss", "deadlock", "cleared", "time_to_clear_s",
    "delay_a_s", "delay_b_s", "who_passed_first", "passing_side_a", "passing_side_b",
    "stopped_a", "stopped_b", "backed_up_a", "backed_up_b", "backed_distance_a_m", "backed_distance_b_m",
)
RESOLVED = "resolved"


def _rounded(value: Optional[float], places: int = 6) -> Optional[float]:
    return None if value is None else round(value, places)


def physical_outcome(
    simulation: Any,
    result: Any,
    track: Sequence[Any],
    agents: Sequence[int],
    start_step: int,
    scenario: Scenario,
    plain_goal_times: Optional[Mapping[int, Optional[float]]] = None,
    labels: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """The outcome columns of one encounter in one finished run.

    ``track`` holds the encounter agents' states after each step (``execute.TrackRow``);
    ``start_step`` is the step of the encounter's first decision. ``labels`` (session id, case,
    encounter type, mode) are put first, as given.
    """
    a, b = agents
    world = simulation.world
    specs = {agent: world.agents[agent].spec for agent in agents}
    dt = world.dt
    start_time = start_step * dt
    rows = [row for row in track if row.step > start_step]
    pair = tuple(sorted(agents))

    kinds = set()
    for episode in result.collision_episodes:
        if episode.end_time_s >= start_time - 1e-9 and set(episode.pair) & set(agents):
            kinds.add("each_other" if tuple(sorted(episode.pair)) == pair else "someone_else")
    if any(episode["agent_id"] in agents and episode["end_time_s"] >= start_time - 1e-9 for episode in result.wall_collision_episodes):
        kinds.add("wall")
    near = any(
        tuple(sorted(episode.pair)) == pair and episode.end_time_s >= start_time - 1e-9 for episode in result.near_misses
    )

    radii = specs[a].radius + specs[b].radius
    present = [row for row in rows if not (row.bodies[a].done or row.bodies[b].done)]
    gaps = [math.dist(row.bodies[a].xy, row.bodies[b].xy) - radii for row in present]

    exits = scenario.zone_exits(simulation, track, agents, start_step)
    cleared = all(exits[agent] is not None for agent in agents)
    if exits[a] is None and exits[b] is None:
        first: Any = None
    elif exits[a] is None or exits[b] is None:
        first = a if exits[b] is None else b
    elif abs(exits[a] - exits[b]) < dt / 2.0:
        first = TOGETHER
    else:
        first = a if exits[a] < exits[b] else b

    sides = {agent: None for agent in agents}
    if present:
        closest = present[min(range(len(gaps)), key=lambda k: (gaps[k], k))]
        for me, other in ((a, b), (b, a)):
            heading = specs[me].path.heading_at(closest.bodies[me].path_s)
            tx, ty = math.cos(heading), math.sin(heading)
            rx, ry = closest.bodies[other].x - closest.bodies[me].x, closest.bodies[other].y - closest.bodies[me].y
            cross = tx * ry - ty * rx  # > 0: the other is on its left
            if abs(rx * tx + ry * ty) <= radii and cross != 0.0:
                sides[me] = "left" if cross < 0.0 else "right"

    eps, backward = simulation.spec.deadlock.speed_eps, ArtefactThresholds().backward_speed_mps
    motion = {}
    for agent in agents:
        mine = [row.bodies[agent] for row in rows if not row.bodies[agent].done]
        forward = []
        for body in mine:
            heading = specs[agent].path.heading_at(body.path_s)
            forward.append(body.vx * math.cos(heading) + body.vy * math.sin(heading))
        motion[agent] = {
            "stopped": any(body.speed_mps < eps for body in mine),
            "backed_up": any(value < -backward for value in forward),
            "backed_distance_m": round(sum(max(0.0, -value) for value in forward) * dt, 6),
        }

    def delay(agent: int) -> Optional[float]:
        mine, plain = result.goal_times.get(agent), (plain_goal_times or {}).get(agent)
        return None if mine is None or plain is None else round(mine - plain, 6)

    columns: dict[str, Any] = {key: None for key in GENERAL_COLUMNS}
    columns.update(dict(labels or {}))
    columns.update({
        "agent_a": a,
        "agent_b": b,
        "run_status": result.status,
        "encounter_start_s": _rounded(start_time),
        "collision": bool(kinds),
        "collision_kinds": ";".join(sorted(kinds)) or None,
        "min_separation_m": _rounded(min(gaps)) if gaps else None,
        "near_miss": near,
        "deadlock": bool(result.deadlock),
        "cleared": cleared,
        "time_to_clear_s": _rounded(max(exits[a], exits[b]) - start_time) if cleared else None,
        "delay_a_s": delay(a),
        "delay_b_s": delay(b),
        "who_passed_first": first,
        "passing_side_a": sides[a],
        "passing_side_b": sides[b],
        "stopped_a": motion[a]["stopped"],
        "stopped_b": motion[b]["stopped"],
        "backed_up_a": motion[a]["backed_up"],
        "backed_up_b": motion[b]["backed_up"],
        "backed_distance_a_m": motion[a]["backed_distance_m"],
        "backed_distance_b_m": motion[b]["backed_distance_m"],
    })
    columns.update(scenario.outcome_columns(simulation, track, agents, start_step, columns))
    columns[RESOLVED] = bool(scenario.resolved(columns))
    return columns


# --- writing and reporting ------------------------------------------------------------------------


def columns_of(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """The general columns, then every scenario's own in the order first seen, then ``resolved``."""
    names = list(GENERAL_COLUMNS)
    for row in rows:
        names.extend(key for key in row if key not in names and key != RESOLVED)
    return [*names, RESOLVED]


def to_csv(rows: Sequence[Mapping[str, Any]]) -> str:
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=columns_of(rows), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: ("" if value is None else value) for key, value in row.items()})
    return out.getvalue()


def c0_baselines(runs_root: Path | str = PACKAGE_ROOT / "runs") -> list[dict[str, Any]]:
    """The committed C0 runs (no LLM, Strategy 1): per scenario, how many completed with no
    collision and no deadlock."""
    found = []
    for summary in sorted(Path(runs_root).glob("c0_no_llm*/summary.csv")):
        with summary.open(encoding="utf-8", newline="") as handle:
            runs = list(csv.DictReader(handle))
        for scenario in sorted({run["scenario"] for run in runs}):
            mine = [run for run in runs if run["scenario"] == scenario]
            good = sum(run["status"] == "completed" and run["collisions"] in ("0", "") and run["deadlock"] != "true" for run in mine)
            found.append({"experiment": summary.parent.name, "scenario": scenario, "runs": len(mine), "resolved": good})
    return found


def _rate(resolved: int, total: int) -> str:
    return f"{resolved}/{total} ({100.0 * resolved / total:.0f}%)" if total else "0/0"


def report(rows: Iterable[Mapping[str, Any]], c0: Optional[Sequence[Mapping[str, Any]]] = None) -> str:
    """The physical resolution rate per encounter type and mode, as Markdown."""
    rows = list(rows)
    lines = [
        "# Physical resolution of the agents' plans",
        "",
        "Resolved: as each scenario defines it (for the passing scenarios: both left the conflict zone, "
        "with no collision, no near miss and no deadlock, within the time limit). `plain_orca` is the "
        "case's own run with no plan, on the same seed.",
        "",
        "| Encounter type | Mode | Sessions | Resolved | Collisions | Near misses | Deadlocks | Mean time to clear (s) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    order = {"plan_only": 0, "plan_orca": 1, MODE_PLAIN_ORCA: 2}
    groups = sorted({(row["encounter_type"], row["mode"]) for row in rows}, key=lambda key: (str(key[0]), order.get(key[1], 9), key[1]))
    for encounter, mode in groups:
        mine = [row for row in rows if row["encounter_type"] == encounter and row["mode"] == mode]
        times = [row["time_to_clear_s"] for row in mine if row["time_to_clear_s"] is not None]
        mean = f"{sum(times) / len(times):.2f}" if times else "-"
        lines.append(
            f"| {encounter} | {mode} | {len(mine)} | {_rate(sum(bool(row[RESOLVED]) for row in mine), len(mine))} | "
            f"{sum(bool(row['collision']) for row in mine)} | {sum(bool(row['near_miss']) for row in mine)} | "
            f"{sum(bool(row['deadlock']) for row in mine)} | {mean} |"
        )
    lines += [
        "",
        "## The C0 baseline (no LLM, Strategy 1 only)",
        "",
        "The negotiation layer's committed C0 runs, in GameChat's scenarios. They are not the encounters "
        "above; they are the existing no-LLM baseline. Resolved: completed with no collision and no deadlock.",
        "",
    ]
    if c0:
        lines += ["| Experiment | Scenario | Runs | Resolved |", "| --- | --- | --- | --- |"]
        lines += [f"| {entry['experiment']} | {entry['scenario']} | {entry['runs']} | {_rate(entry['resolved'], entry['runs'])} |" for entry in c0]
    else:
        lines.append("No C0 runs were found.")
    return "\n".join(lines) + "\n"
