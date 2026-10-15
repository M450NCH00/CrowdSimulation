"""Benchmark: what following the rules costs per simulation step in the two-way flow (issue #28).

    python -m negsim.rules.benchmark                                    # 100 and 1,000 agents
    python -m negsim.rules.benchmark --out runs/si2_benchmark/benchmark.json

For each crowd size the shipped ``bidirectional_flow`` scenario is built as issue #26's
benchmark builds it (``negsim.avoidance.benchmark.corridor_for``: the same starting density
at every size), with the primary baseline laid on it (``orca_perturbed_v1``: 40 neighbours,
12.5 m, the perturbation). It is stepped from the same start, with the same seed, under
plain ORCA and with the rule provider and the ``default`` rule set, the two in turn,
``--repeats`` times each, so that a drift in the machine's speed falls on both alike. Each
step is timed, and with the rules the time spent inside the provider (its per-step hook,
which is the matching policy, and its answer when a pair forms) is timed on its own.
Nothing is logged during the timing, and no model is called.

The two modes start alike and then drift apart, because the rules change how the agents
move. The difference in time per step therefore mixes the cost of matching with the cost
of a slightly different crowd; the time inside the provider is the cost of matching alone.

This is a measurement. It has no pass mark.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ..avoidance.benchmark import SCENARIO, corridor_for, environment
from ..avoidance.directives import NullProvider
from ..avoidance.perception import default_visibility
from ..avoidance.simulation import AvoidanceSimulation
from ..configutil import deep_merge, resolve_path
from ..experiment.baselines import load_baseline
from ..experiment.batch import git_state
from ..scenarios.registry import build_crowd_scenario, load_scenario_config
from .database import RuleDatabase
from .provider import RuleDatabaseProvider

BASELINE = "orca_perturbed_v1"
RULESET = "default"
MODES = ("plain", "rules")


class _TimedProvider(RuleDatabaseProvider):
    """The rule provider, with the time it spends added up."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.seconds = {"update": 0.0, "directive": 0.0}

    def update(self, view: Any):
        started = time.perf_counter()
        try:
            return super().update(view)
        finally:
            self.seconds["update"] += time.perf_counter() - started

    def directive(self, record: Any):
        started = time.perf_counter()
        try:
            return super().directive(record)
        finally:
            self.seconds["directive"] += time.perf_counter() - started


def _spec(n_agents: int, gap: float):
    baseline = load_baseline(BASELINE)
    base = load_scenario_config(SCENARIO)
    overrides = deep_merge(
        baseline.scenario_overrides(base),
        {"geometry": corridor_for(n_agents, gap), "on_collision": "continue", "max_time": 1.0e6},
    )
    return build_crowd_scenario(load_scenario_config(SCENARIO, overrides)), baseline


def _time_once(mode: str, n_agents: int, steps: int, gap: float, seed: int) -> dict[str, Any]:
    """Step one simulation ``steps`` times in one mode, timing each step."""
    spec, baseline = _spec(n_agents, gap)
    provider = NullProvider() if mode == "plain" else _TimedProvider(RuleDatabase.load().activate(RULESET), default_visibility())
    simulation = AvoidanceSimulation(
        spec, provider=provider, seed=seed, perturbation=baseline.perturbation, record_trajectory=False
    )
    durations, open_pairs = [], []
    for _ in range(steps):
        if simulation.status is not None:
            break
        before = time.perf_counter()
        simulation.step()
        durations.append((time.perf_counter() - before) * 1000.0)
        open_pairs.append(len(simulation.open_pairs))
    result = simulation.finish()
    ordered = sorted(durations)
    entry: dict[str, Any] = {
        "agents": len(spec.agents),
        "steps_timed": len(durations),
        "ms_per_step_mean": round(statistics.fmean(durations), 3),
        "ms_per_step_median": round(statistics.median(durations), 3),
        "ms_per_step_p90": round(ordered[min(len(ordered) - 1, int(0.9 * len(ordered)))], 3),
        "open_pairs_per_step_mean": round(statistics.fmean(open_pairs), 1),
    }
    if mode == "rules":
        summary = result.provider_summary
        entry["provider_ms_per_step_mean"] = round(1000.0 * sum(provider.seconds.values()) / len(durations), 3)
        entry["update_ms_per_step_mean"] = round(1000.0 * provider.seconds["update"] / len(durations), 3)
        entry["directive_ms_per_step_mean"] = round(1000.0 * provider.seconds["directive"] / len(durations), 3)
        entry["evaluations_per_step_mean"] = round(sum(summary["evaluations"].values()) / len(durations), 1)
        entry["evaluations"] = summary["evaluations"]
        entry["matches_begun"] = summary["matches_begun"]
    return entry


def measure(n_agents: int, steps: int, gap: float, repeats: int, seed: int = 1) -> dict[str, Any]:
    """Time both modes ``repeats`` times each, in turn, and compare their medians."""
    runs: dict[str, list[dict[str, Any]]] = {mode: [] for mode in MODES}
    for _ in range(repeats):
        for mode in MODES:
            runs[mode].append(_time_once(mode, n_agents, steps, gap, seed))
    row: dict[str, Any] = {"agents": runs["plain"][0]["agents"], "steps_timed": steps, "repeats": repeats}
    for mode in MODES:
        means = [entry["ms_per_step_mean"] for entry in runs[mode]]
        row[mode] = {"ms_per_step_mean_median": round(statistics.median(means), 3), "ms_per_step_mean_each": means}
        if mode == "rules":
            provider = [entry["provider_ms_per_step_mean"] for entry in runs[mode]]
            row[mode]["provider_ms_per_step_median"] = round(statistics.median(provider), 3)
            row[mode]["provider_ms_per_step_each"] = provider
        row[mode]["first_repeat"] = runs[mode][0]
    plain, rules = row["plain"]["ms_per_step_mean_median"], row["rules"]["ms_per_step_mean_median"]
    row["overhead_ms_per_step"] = round(rules - plain, 3)
    row["overhead_ratio"] = round(rules / plain, 3) if plain else None
    row["provider_share_of_rule_step"] = round(row["rules"]["provider_ms_per_step_median"] / rules, 3) if rules else None
    return row


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--agents", type=int, nargs="+", default=[100, 1000], help="crowd sizes (total agents)")
    parser.add_argument("--steps", type=int, default=100, help="steps to time for each size, mode and repeat")
    parser.add_argument("--repeats", type=int, default=3, help="times each mode is timed, in turn with the other")
    parser.add_argument("--gap", type=float, default=6.0, help="metres between the two crowds at the start")
    parser.add_argument("--out", type=Path, help="write the results to this JSON file")
    args = parser.parse_args(argv)
    if args.repeats < 1 or args.steps < 1:
        parser.error("--repeats and --steps must be at least 1")

    report: dict[str, Any] = {
        "benchmark": "bidirectional_flow, rule-matching overhead per simulation step",
        "scenario": SCENARIO,
        "baseline": BASELINE,
        "ruleset": RULESET,
        "run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git": git_state(),
        "gap_m": args.gap,
        "environment": environment(),
        "results": [],
    }
    for n_agents in args.agents:
        print(f"{n_agents} agents: timing {args.steps} steps, plain and with rules, {args.repeats} times each ...", file=sys.stderr, flush=True)
        row = measure(n_agents, args.steps, args.gap, args.repeats)
        report["results"].append(row)
        print(
            f"  {row['agents']:>6} agents  plain {row['plain']['ms_per_step_mean_median']:>9.2f} ms/step  "
            f"rules {row['rules']['ms_per_step_mean_median']:>9.2f} ms/step  "
            f"(inside the provider {row['rules']['provider_ms_per_step_median']:.2f}; x{row['overhead_ratio']})"
        )
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
