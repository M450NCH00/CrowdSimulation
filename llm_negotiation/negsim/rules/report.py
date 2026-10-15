"""Tables of issue #28's behaviour checks, read from the committed run logs.

    python -m negsim.rules.report                              # every experiment of the checks
    python -m negsim.rules.report si2_head_on --out FILE.md

One section per experiment, one row per condition (a combination of the levels of its
factors), over that condition's seeds. The first table has the outcome of every pair
interaction, the conflict metrics as mean ± standard deviation [min, max], the counts of
issue #26's two artefacts, and the rules that fired; the second, what decided the outcomes
and what the matching policy did. Every number is read from a run's ``config.json``,
``outcome.json`` and ``trajectory.csv``; nothing is simulated, and the same logs always give
the same tables. ``docs/behaviour-checks.md`` quotes them, and a test checks that it does so
exactly.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Optional, Sequence

from ..configutil import PACKAGE_ROOT

RUNS_DIR = PACKAGE_ROOT / "runs"

#: The experiments of the behaviour checks (``configs/rule_following/``), in the order reported:
#: the eight the issue asks for, then the follow-up ablation of the flow.
EXPERIMENTS = (
    "si2_head_on",
    "si2_keep_left_vs_right",
    "si2_open_crossing",
    "si2_overtaking",
    "si2_bottleneck",
    "si2_bidirectional_flow",
    "si2_head_on_r5",
    "si2_overtaking_r5",
    "si2_bidirectional_flow_ablation",
)

#: A pass to one side is a lateral excursion of more than this, from where agent 0 started (m).
SIDE_THRESHOLD_M = 0.05


def spread(values: Iterable[Optional[float]], digits: int, ranged: bool = True) -> str:
    """``mean ± sd [min, max]`` over the values present; the range only if they differ."""
    present = [value for value in values if value is not None]
    if not present:
        return "–"
    mean = statistics.fmean(present)
    sd = statistics.stdev(present) if len(present) > 1 else 0.0
    text = f"{mean:.{digits}f} ± {sd:.{digits}f}"
    if ranged and min(present) != max(present):
        text += f" [{min(present):.{digits}f}, {max(present):.{digits}f}]"
    return text


def side_passed(run_dir: Path, agent_id: str = "0") -> str:
    """The side an agent passed on, as it saw it: the sign of its largest lateral excursion
    from where it started, across its heading at the start. ``none`` if it never moved more
    than :data:`SIDE_THRESHOLD_M` to either side."""
    with (run_dir / "trajectory.csv").open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["agent_id"] == agent_id]
    if not rows:
        return "?"
    x0, y0, theta = float(rows[0]["x_m"]), float(rows[0]["y_m"]), float(rows[0]["theta_rad"])
    lateral = [-math.sin(theta) * (float(row["x_m"]) - x0) + math.cos(theta) * (float(row["y_m"]) - y0) for row in rows]
    extreme = max(lateral, key=abs)
    return "left" if extreme > SIDE_THRESHOLD_M else "right" if extreme < -SIDE_THRESHOLD_M else "none"


def load_conditions(experiment_dir: Path) -> dict[tuple[tuple[str, str], ...], list[tuple[Path, dict, dict]]]:
    """The runs of one experiment, grouped by condition, in run order."""
    groups: dict[tuple[tuple[str, str], ...], list[tuple[Path, dict, dict]]] = {}
    for config_path in sorted(experiment_dir.glob("*/config.json")):
        outcome_path = config_path.parent / "outcome.json"
        if not outcome_path.is_file():
            continue
        config = json.loads(config_path.read_text(encoding="utf-8"))
        outcome = json.loads(outcome_path.read_text(encoding="utf-8"))
        groups.setdefault(tuple(config["variant"].items()), []).append((config_path.parent, config, outcome))
    return groups


def _label(key: Sequence[tuple[str, str]]) -> str:
    return ", ".join(level for _, level in key)


def _counted(counter: Counter) -> str:
    return ", ".join(f"{key} {count}" for key, count in sorted(counter.items())) or "–"


def experiment_tables(experiment: str, runs_dir: Path = RUNS_DIR) -> list[str]:
    """The Markdown lines of one experiment's section."""
    groups = load_conditions(runs_dir / experiment)
    if not groups:
        return [f"### {experiment}", "", "No runs found.", ""]
    with_side = all(config["scenario"]["type"] == "wide_corridor_head_on" for runs in groups.values() for _, config, _ in runs)
    code = Counter(
        f"`{config['git']['commit'][:7]}`" + (" with uncommitted changes" if config["git"]["dirty"] else "")
        for runs in groups.values()
        for _, config, _ in runs
    )
    total = sum(len(runs) for runs in groups.values())
    lines = [f"### {experiment}", "", f"{total} runs, from {_counted(code)}.", ""]

    head = (
        "| Condition | Runs | Deadlock runs | Collision runs | Pairs: avoided / resolved / failed "
        "| Exposure, all agents (s) | Yield events | Near misses | Min separation (mm) | Mean time to goal (s) "
        "| Largest path deviation (m) | Backward / hurried episodes | Rules fired (matches begun) |"
    )
    if with_side:
        head += " Agent 0 passed |"
    lines += [head, "|" + "---|" * (head.count("|") - 1)]
    for key, runs in groups.items():
        outcomes = [outcome for _, _, outcome in runs]
        totals = [outcome["totals"] for outcome in outcomes]
        pairs = [outcome["interaction_outcomes"] for outcome in outcomes]
        artefacts = [outcome["artefacts"]["totals"] for outcome in outcomes]
        fired: Counter = Counter()
        for outcome in outcomes:
            fired.update((outcome.get("rules") or {}).get("matches_begun") or {})
        row = (
            f"| {_label(key)} | {len(runs)} "
            f"| {sum(1 for outcome in outcomes if outcome['deadlock'])} "
            f"| {sum(1 for outcome in outcomes if outcome['collisions']['agent_agent'] + outcome['collisions']['agent_wall'])} "
            f"| {sum(p['avoided'] for p in pairs)} / {sum(p['resolved'] for p in pairs)} / {sum(p['failed'] for p in pairs)} "
            f"| {spread((t['conflict_exposure_time_s'] for t in totals), 1)} "
            f"| {spread((t['yield_events'] for t in totals), 1)} "
            f"| {spread((t['near_misses'] for t in totals), 1)} "
            f"| {spread((None if t['min_separation_m'] is None else 1000.0 * t['min_separation_m'] for t in totals), 3)} "
            f"| {spread((t['mean_time_to_goal_s'] for t in totals), 2)} "
            f"| {spread((t['max_path_deviation_m'] for t in totals), 3)} "
            f"| {sum(a['backward_episodes'] for a in artefacts)} / {sum(a['hurried_episodes'] for a in artefacts)} "
            f"| {', '.join(f'{rule} ×{count}' for rule, count in sorted(fired.items())) or '–'} |"
        )
        if with_side:
            row += f" {_counted(Counter(side_passed(run_dir) for run_dir, _, _ in runs))} |"
        lines.append(row)

    lines += [
        "",
        "| Condition | Arrived | Makespan (s) | Pairs with exposure / a yield / a collision / a deadlock / open at timeout "
        "| Evaluations, by outcome | Matches ended, by reason | Formation mismatches | Cross-pair conflicts |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for key, runs in groups.items():
        outcomes = [outcome for _, _, outcome in runs]
        ingredients: Counter = Counter()
        evaluations: Counter = Counter()
        ends: Counter = Counter()
        mismatches = conflicts = 0
        for outcome in outcomes:
            ingredients.update(outcome["interaction_outcomes"]["pairs_with"])
            rules = outcome.get("rules") or {}
            evaluations.update(rules.get("evaluations") or {})
            ends.update(rules.get("match_ends") or {})
            mismatches += rules.get("formation_mismatches") or 0
            conflicts += rules.get("cross_pair_conflicts") or 0
        has_rules = any(outcome.get("rules") for outcome in outcomes)
        lines.append(
            f"| {_label(key)} | {sum(o['arrived'] for o in outcomes)} of {sum(o['n_agents'] for o in outcomes)} "
            f"| {spread((o['makespan_s'] for o in outcomes), 2)} "
            f"| {ingredients['exposed']} / {ingredients['yielded']} / {ingredients['collided']} / {ingredients['deadlocked']} / {ingredients['open_at_timeout']} "
            f"| {_counted(evaluations)} | {_counted(ends)} "
            f"| {mismatches if has_rules else '–'} | {conflicts if has_rules else '–'} |"
        )

    same = [
        _label(key)
        for key, runs in groups.items()
        if len(runs) > 1 and len({(run_dir / "trajectory.csv").read_bytes() for run_dir, _, _ in runs}) == 1
    ]
    if same:
        lines += ["", f"Conditions whose seeds all gave the same trajectory: {'; '.join(same)}."]
    lines.append("")
    return lines


def report(experiments: Sequence[str] = EXPERIMENTS, runs_dir: Path = RUNS_DIR) -> str:
    lines: list[str] = []
    for experiment in experiments:
        lines += experiment_tables(experiment, runs_dir)
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiments", nargs="*", help=f"experiment names (default: the {len(EXPERIMENTS)} of the behaviour checks)")
    parser.add_argument("--runs", type=Path, default=RUNS_DIR, help="the folder holding the experiments (default: runs/)")
    parser.add_argument("--out", type=Path, help="write the tables to this file instead of printing them")
    args = parser.parse_args(argv)
    text = report(args.experiments or EXPERIMENTS, args.runs)
    if args.out is None:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")  # the tables use ± and ×
        print(text)
    else:
        args.out.write_text(text + "\n", encoding="utf-8", newline="\n")
        print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
