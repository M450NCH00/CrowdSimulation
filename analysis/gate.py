"""The resolution gate (issue #65, RF-10, tasks 3 and 6): is the encounter type resolved by the LLM?

The threshold is the one fixed in the experiment's config before the run
(``resolution_gate.plan_only_resolved_min``, recorded in ``config.json``), never one given here,
so that the gate cannot be moved after the results are seen. The rate is ``resolved_plan_only``
over the **design's** sessions: every cell once per geometry and condition, the first run of
each (``repeat`` 1), and no counterfactual pair (``pair_id`` empty). Exact repeats and pairs are
left out so that no cell counts more than once. Only completed sessions are counted; sessions that
never had an encounter, or were aborted (the budget guard), are reported beside it.

Also reported, not part of the gate: the rate per condition and per geometry, with Wilson
intervals, and the same rate in ``plan_orca`` and in plain ORCA, the baselines (Step 1).

    python -m analysis.gate llm_negotiation/runs/rf10_round1_head_on
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from .noise import wilson

MODES = ("plan_only", "plan_orca", "plain_orca")
COMPLETED = "completed"


class GateError(ValueError):
    """The experiment cannot be gated as it is."""


def threshold(experiment: Path) -> dict[str, Any]:
    """The gate as the config fixed it before the run."""
    config = json.loads((experiment / "config.json").read_text(encoding="utf-8"))
    gate = (config.get("experiment") or {}).get("resolution_gate")
    if not gate:
        raise GateError(f"{experiment}: its config fixed no resolution_gate before the run")
    return dict(gate)


def design_rows(rows: Sequence[Mapping[str, str]]) -> list[Mapping[str, str]]:
    """The design's sessions: the first run of each cell, no counterfactual pair."""
    return [row for row in rows if str(row.get("repeat", "1")) == "1" and not row.get("pair_id")]


def _rate(rows: Sequence[Mapping[str, str]], mode: str) -> dict[str, Any]:
    k, n = sum(row[f"resolved_{mode}"] == "True" for row in rows), len(rows)
    low, high = wilson(k, n)
    return {"resolved": k, "n": n, "rate": None if n == 0 else round(k / n, 4),
            "ci95": None if n == 0 else [round(low, 4), round(high, 4)]}


def gate(experiment: Path) -> dict[str, Any]:
    fixed = threshold(experiment)
    with (experiment / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        rows = design_rows(list(csv.DictReader(handle)))
    completed = [row for row in rows if row["outcome"] == COMPLETED]
    if not completed:
        raise GateError(f"{experiment}: no completed session of the design")
    pooled = _rate(completed, "plan_only")
    by: dict[str, dict[str, Any]] = {}
    for column in ("condition", "geometry"):
        groups: dict[str, list] = defaultdict(list)
        for row in completed:
            groups[row[column]].append(row)
        by[column] = {value: _rate(group, "plan_only") for value, group in sorted(groups.items())}
    skipped = defaultdict(int)
    for row in rows:
        if row["outcome"] != COMPLETED:
            skipped[row["outcome"]] += 1
    return {
        "threshold": fixed["plan_only_resolved_min"],
        "reason": fixed["reason"],
        "plan_only": pooled,
        "passes": pooled["rate"] >= fixed["plan_only_resolved_min"],
        "by_condition": by["condition"],
        "by_geometry": by["geometry"],
        "baselines": {mode: _rate(completed, mode) for mode in MODES[1:]},
        "design_sessions_not_completed": dict(skipped),
    }


def _line(name: str, rate: Mapping[str, Any]) -> str:
    low, high = rate["ci95"] or (None, None)
    shown = "n/a" if rate["rate"] is None else f"{rate['rate']:.2f} (95% CI {low:.2f} to {high:.2f})"
    return f"| {name} | {rate['resolved']} / {rate['n']} | {shown} |"


def markdown(result: Mapping[str, Any]) -> str:
    verdict = "**passes**" if result["passes"] else "**fails**"
    lines = [
        "# The resolution gate",
        "",
        f"Threshold, fixed in the config before the run: {result['threshold']:.2f} of the design's sessions resolved in "
        f"`plan_only`. Reason: {result['reason']}",
        "",
        f"Pooled `plan_only`: {result['plan_only']['resolved']} of {result['plan_only']['n']} "
        f"({result['plan_only']['rate']:.2f}). The encounter type {verdict} the gate.",
        "",
        "| Group | Resolved | Rate |",
        "| --- | --- | --- |",
        _line("all (plan_only)", result["plan_only"]),
        *(_line(f"condition {name}", rate) for name, rate in result["by_condition"].items()),
        *(_line(f"geometry {name}", rate) for name, rate in result["by_geometry"].items()),
        *(_line(f"baseline {mode}", rate) for mode, rate in result["baselines"].items()),
        "",
    ]
    if result["design_sessions_not_completed"]:
        lines.append(f"Design sessions not counted: {result['design_sessions_not_completed']}.")
        lines.append("")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m analysis.gate", description=__doc__.split("\n\n")[0])
    parser.add_argument("experiment", type=Path, help="the experiment's folder (config.json and outcomes.csv)")
    parser.add_argument("--out", type=Path, help="folder for gate.json and gate.md (default: <experiment>/analysis)")
    args = parser.parse_args(argv)
    result = gate(args.experiment)
    out = args.out or args.experiment / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    (out / "gate.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    (out / "gate.md").write_text(markdown(result), encoding="utf-8", newline="\n")
    print(markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
