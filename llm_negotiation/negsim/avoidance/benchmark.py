"""Performance benchmark: milliseconds per simulation step in the bidirectional flow.

    python -m negsim.avoidance.benchmark                       # 100 and 1,000 agents
    python -m negsim.avoidance.benchmark --agents 100 1000 10000
    python -m negsim.avoidance.benchmark --out runs/si1_benchmark/benchmark.json

For each crowd size the shipped ``bidirectional_flow`` scenario is built with half the
agents walking each way, plain ORCA, and the agent type of the config unchanged. Only the
corridor is resized, so that every size starts at the same density: the agents stand one
metre apart in two blocks that fill the corridor's width, with ``--gap`` metres between
the fronts of the two blocks. The run is stepped ``--steps`` times and each step is timed.
Nothing is logged during the timing, and no model is called.

This is a measurement. It has no pass mark.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ..configutil import resolve_path
from ..scenarios.registry import load_crowd_scenario
from .simulation import AvoidanceSimulation

SCENARIO = "configs/scenarios/bidirectional_flow.yaml"


def corridor_for(n_agents: int, gap: float, spacing: float = 1.0, wall_clearance: float = 0.5) -> dict[str, Any]:
    """A corridor for ``n_agents`` (half each way) at the shipped starting density.

    The width grows with the square root of the crowd, so that the two blocks stay
    compact: about as deep as they are wide, up to the 4 m of the shipped scenario.
    """
    per_direction = n_agents // 2
    columns = max(4, math.ceil(math.sqrt(per_direction / 3.0)))
    rows = math.ceil(per_direction / columns)
    width = (columns - 1) * spacing + 2.0 * wall_clearance
    length = 2.0 * (rows - 1) * spacing + gap
    return {
        "agents_per_direction": per_direction,
        "width": width,
        "length": length,
        "spawn_spacing": spacing,
        "wall_clearance": wall_clearance,
    }


def measure(n_agents: int, steps: int, gap: float) -> dict[str, Any]:
    geometry = corridor_for(n_agents, gap)
    started = time.perf_counter()
    spec = load_crowd_scenario(SCENARIO, {"geometry": geometry, "on_collision": "continue", "max_time": 1.0e6})
    simulation = AvoidanceSimulation(spec, record_trajectory=False)
    setup_s = time.perf_counter() - started

    durations = []
    for _ in range(steps):
        if simulation.status is not None:
            break
        before = time.perf_counter()
        simulation.step()
        durations.append((time.perf_counter() - before) * 1000.0)
    result = simulation.finish()
    ordered = sorted(durations)
    agent_steps = sum(stats.samples for stats in result.stats.values())
    return {
        "agents": len(spec.agents),
        "steps_timed": len(durations),
        "corridor_width_m": geometry["width"],
        "corridor_length_m": geometry["length"],
        "ms_per_step_mean": round(statistics.fmean(durations), 3),
        "ms_per_step_median": round(statistics.median(durations), 3),
        "ms_per_step_p90": round(ordered[min(len(ordered) - 1, int(0.9 * len(ordered)))], 3),
        "ms_per_step_min": round(ordered[0], 3),
        "ms_per_step_max": round(ordered[-1], 3),
        "microseconds_per_agent_step": round(1000.0 * sum(durations) / agent_steps, 2) if agent_steps else None,
        "simulated_time_s": round(result.sim_time_s, 3),
        "real_time_factor": round(result.sim_time_s / (sum(durations) / 1000.0), 3),
        "setup_s": round(setup_s, 3),
        "interactions_started": len(result.interactions),
        "steps_with_fallback": result.steps_with_fallback,
        "collision_episodes": result.collisions["agent_agent"],
        "status_when_stopped": result.status,
    }


def environment() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "logical_cpus": os.cpu_count(),
        "note": "single process, single thread, pure Python; no compiled extension is used",
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--agents", type=int, nargs="+", default=[100, 1000], help="crowd sizes (total agents)")
    parser.add_argument("--steps", type=int, default=100, help="steps to time for each size")
    parser.add_argument("--gap", type=float, default=6.0, help="metres between the two crowds at the start")
    parser.add_argument("--out", type=Path, help="write the results to this JSON file")
    args = parser.parse_args(argv)

    report = {
        "benchmark": "bidirectional_flow, plain ORCA, time per simulation step",
        "scenario": SCENARIO,
        "run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "time_step_s": None,
        "gap_m": args.gap,
        "environment": environment(),
        "results": [],
    }
    for n_agents in args.agents:
        print(f"{n_agents} agents: timing {args.steps} steps ...", file=sys.stderr, flush=True)
        row = measure(n_agents, args.steps, args.gap)
        report["results"].append(row)
        print(
            f"  {row['agents']:>6} agents  {row['ms_per_step_mean']:>10.2f} ms/step mean  "
            f"{row['ms_per_step_median']:>10.2f} median  {row['ms_per_step_p90']:>10.2f} p90  "
            f"({row['microseconds_per_agent_step']} us per agent per step, {row['steps_timed']} steps)"
        )
    report["time_step_s"] = load_crowd_scenario(SCENARIO).dt
    if args.out is not None:
        path = resolve_path(args.out) if not args.out.is_absolute() else args.out
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2)
            handle.write("\n")
        print(f"written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
