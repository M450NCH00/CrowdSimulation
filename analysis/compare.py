"""Two runs of the same sessions, compared cell for cell (issue #98, RF-27): did the change between
them (a new core template, say) change what the agents did?

The two experiments must hold the same sessions (the same ``session_id`` with the same cell,
people and seed; RF-27's config reproduces RF-10's independent sessions). For the sessions of one
condition that completed in both, it reports:

- the **resolution rate** in ``plan_only`` of each, over the design's sessions (as
  ``analysis.gate``: the first run of each cell, no counterfactual pair), pooled and per geometry,
  with Wilson intervals;
- the **paired table**: resolved in both, in only one, in neither; and McNemar's exact test on the
  sessions that changed (two-sided, the binomial at one half on the discordant pairs), which is the
  test for paired yes/no outcomes;
- **how they stepped** (``analysis.lateral``): making room, towards the same wall, not aside;
- **stability** on the exact-repeat set: of its cells, how many had the same ``plan_only``
  outcome (resolved, collision, near miss) in every run;
- **unreadable replies**: decision points whose reply could not be read after the retry;
- the **model string and fingerprint** the API returned in each, since a model name can be
  re-pointed between two runs (``docs/llm-backend.md``, section 3).

``--readable-only`` (issue #100) keeps only the sessions whose every reply was readable in both
runs, so that a reply format one model writes and the parser refuses does not count as a decision.

    python -m analysis.compare llm_negotiation/runs/rf10_round1_head_on llm_negotiation/runs/rf27_round1_head_on_v7 --condition independent
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from .gate import COMPLETED, design_rows
from .lateral import SIDESTEPS, outcome_of, sidestep, when_level
from .noise import wilson


class CompareError(ValueError):
    """The two experiments cannot be compared as they are."""


def outcome_rows(experiment: Path, condition: str) -> dict[str, dict[str, str]]:
    """The completed sessions of ``condition``, by session id."""
    with (experiment / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        return {
            row["session_id"]: row
            for row in csv.DictReader(handle)
            if row["condition"] == condition and row["outcome"] == COMPLETED
        }


def mcnemar_exact(only_base: int, only_new: int) -> float:
    """McNemar's exact test, two-sided: the chance of a split at least this uneven of the
    sessions that changed, if a change either way were equally likely."""
    n = only_base + only_new
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(min(only_base, only_new) + 1)) / 2**n
    return min(1.0, 2 * tail)


def _rate(rows: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    k, n = sum(row["resolved_plan_only"] == "True" for row in rows), len(rows)
    low, high = wilson(k, n)
    return {"resolved": k, "n": n, "rate": None if n == 0 else round(k / n, 4),
            "ci95": None if n == 0 else [round(low, 4), round(high, 4)]}


def _sidesteps(experiment: Path, rows: Sequence[Mapping[str, str]]) -> dict[str, dict[str, int]]:
    found: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        level = when_level(experiment / "replay" / row["session_id"] / "plan_only" / "trajectory.csv")
        found[outcome_of(row)][sidestep(level["own_0_m"], level["own_1_m"])] += 1
    return {name: {kind: found[name][kind] for kind in SIDESTEPS} for name in sorted(found)}


def _stability(rows: Mapping[str, Mapping[str, str]]) -> dict[str, int]:
    """Of the exact-repeat set's cells, how many had one ``plan_only`` outcome in every run."""
    runs: dict[str, list[str]] = defaultdict(list)
    for session_id, row in rows.items():
        if row.get("exact_repeat_set") == "True" and not row.get("pair_id"):
            runs[session_id.rsplit("_r", 1)[0]].append(outcome_of(row))
    return {"cells": len(runs), "same_in_every_run": sum(len(set(found)) == 1 for found in runs.values()),
            "runs": sum(len(found) for found in runs.values())}


def _sessions(experiment: Path, ids: Sequence[str]) -> dict[str, Any]:
    """Unreadable decision points, and the model strings and fingerprints returned."""
    points = unreadable = 0
    models: Counter = Counter()
    for session_id in ids:
        record = json.loads((experiment / "sessions" / f"{session_id}.json").read_text(encoding="utf-8"))
        for point in record.get("decision_points") or []:
            points += 1
            unreadable += point.get("parse_error") is not None
            for attempt in point.get("attempts") or []:
                models[f"{attempt.get('model')} / {attempt.get('system_fingerprint')}"] += 1
        core = ((record.get("templates") or {}).get("core") or {}).get("key")
        models[f"template {core}"] += 0
    return {"decision_points": points, "unreadable": unreadable, "models": dict(models)}


def readable(experiment: Path, session_id: str) -> bool:
    """Whether every decision point of the session had a readable reply (after the retry)."""
    record = json.loads((experiment / "sessions" / f"{session_id}.json").read_text(encoding="utf-8"))
    return all(point.get("parse_error") is None for point in record.get("decision_points") or [])


def compare(base: Path, new: Path, condition: str, readable_only: bool = False) -> dict[str, Any]:
    """``readable_only`` keeps only the sessions whose every reply was readable in both runs, so
    that a reply format one model writes and the parser refuses does not count as a decision."""
    a, b = outcome_rows(base, condition), outcome_rows(new, condition)
    shared = sorted(set(a) & set(b))
    dropped = 0
    if readable_only:
        kept = [s for s in shared if readable(base, s) and readable(new, s)]
        dropped, shared = len(shared) - len(kept), kept
    if not shared:
        raise CompareError(f"{base} and {new} have no completed {condition} session in common")
    design = [row["session_id"] for row in design_rows([b[s] for s in shared])]
    cells = Counter()
    for session_id in design:
        cells[(a[session_id]["resolved_plan_only"] == "True", b[session_id]["resolved_plan_only"] == "True")] += 1
    by_geometry = {}
    for geometry in sorted({b[s]["geometry"] for s in design}):
        ids = [s for s in design if b[s]["geometry"] == geometry]
        by_geometry[geometry] = {"base": _rate([a[s] for s in ids]), "new": _rate([b[s] for s in ids])}
    only_base, only_new = cells[(True, False)], cells[(False, True)]
    return {
        "condition": condition,
        "base": str(base), "new": str(new),
        "sessions_in_common": len(shared),
        "readable_only": readable_only, "dropped_unreadable": dropped,
        "only_in_base": len(set(a) - set(b)), "only_in_new": len(set(b) - set(a)),
        "design_sessions": len(design),
        "rate": {"base": _rate([a[s] for s in design]), "new": _rate([b[s] for s in design])},
        "by_geometry": by_geometry,
        "paired": {"both": cells[(True, True)], "only_base": only_base, "only_new": only_new, "neither": cells[(False, False)],
                   "mcnemar_p": round(mcnemar_exact(only_base, only_new), 6)},
        "sidesteps": {"base": _sidesteps(base, [a[s] for s in design]), "new": _sidesteps(new, [b[s] for s in design])},
        "stability": {"base": _stability({s: a[s] for s in shared}), "new": _stability({s: b[s] for s in shared})},
        "sessions": {"base": _sessions(base, shared), "new": _sessions(new, shared)},
    }


def _shown(rate: Mapping[str, Any]) -> str:
    if rate["rate"] is None:
        return "n/a"
    low, high = rate["ci95"]
    return f"{rate['resolved']} / {rate['n']}: {rate['rate']:.2f} ({low:.2f} to {high:.2f})"


def markdown(result: Mapping[str, Any]) -> str:
    p = result["paired"]
    lines = [
        f"# {Path(result['new']).name} against {Path(result['base']).name}, condition {result['condition']}",
        "",
        f"Sessions completed in both: {result['sessions_in_common']} (only in the first: {result['only_in_base']}, "
        f"only in the second: {result['only_in_new']}); of them, the design's: {result['design_sessions']}."
        + (f" **Readable only:** {result['dropped_unreadable']} session(s) with an unreadable reply in either run left out."
           if result.get("readable_only") else ""),
        "",
        "## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)",
        "",
        f"| Group | {Path(result['base']).name} | {Path(result['new']).name} |",
        "| --- | --- | --- |",
        f"| all | {_shown(result['rate']['base'])} | {_shown(result['rate']['new'])} |",
        *(f"| {name} | {_shown(r['base'])} | {_shown(r['new'])} |" for name, r in result["by_geometry"].items()),
        "",
        "## The same sessions, paired",
        "",
        "| | resolved in the second | not resolved in the second |",
        "| --- | --- | --- |",
        f"| resolved in the first | {p['both']} | {p['only_base']} |",
        f"| not resolved in the first | {p['only_new']} | {p['neither']} |",
        "",
        f"McNemar's exact test (two-sided) on the {p['only_base'] + p['only_new']} sessions that changed: p = {p['mcnemar_p']:.4f}.",
        "",
        "## How they stepped, when level (`analysis.lateral`)",
        "",
        "| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |",
        "| --- | --- | --- | --- | --- |",
    ]
    for arm in ("base", "new"):
        for name, counts in result["sidesteps"][arm].items():
            lines.append(f"| {Path(result[arm]).name} | {name} | {counts['same_own_side']} | {counts['towards_same_wall']} | {counts['not_both_aside']} |")
    lines += ["", "## Stability, unreadable replies, model", ""]
    for arm in ("base", "new"):
        s, r = result["stability"][arm], result["sessions"][arm]
        lines.append(
            f"- **{Path(result[arm]).name}**: exact-repeat set, {s['same_in_every_run']} of {s['cells']} cells with one `plan_only` "
            f"outcome in every run ({s['runs']} runs); unreadable after the retry, {r['unreadable']} of {r['decision_points']} "
            f"decision points; " + "; ".join(f"{key} ({count} sends)" if count else key for key, count in sorted(r["models"].items())) + "."
        )
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m analysis.compare", description=__doc__.split("\n\n")[0])
    parser.add_argument("base", type=Path, help="the first experiment's folder (outcomes.csv, sessions/, replay/)")
    parser.add_argument("new", type=Path, help="the second experiment's folder")
    parser.add_argument("--condition", default="independent", help="the condition to compare (default: independent)")
    parser.add_argument("--readable-only", action="store_true",
                        help="keep only the sessions whose every reply was readable in both runs")
    args = parser.parse_args(argv)
    result = compare(args.base, args.new, args.condition, readable_only=args.readable_only)
    text = markdown(result)
    out = args.new / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    name = f"compare_{args.base.name}" + ("_readable_only" if args.readable_only else "")
    (out / f"{name}.md").write_text(text, encoding="utf-8", newline="\n")
    (out / f"{name}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
