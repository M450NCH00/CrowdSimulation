"""RF-53 (issue #144), stage 2 pilot: the tables of pilot_report.md that analysis.compare does not give.

RF-40's silent design sessions over all four repeats (256), against the pilot's (64, repeat 1):
how they stepped when level (analysis.lateral), whether an agent reversed its sidestep, and whether
one agent never sidestepped; and RF-40's own repeat-to-repeat churn, as the noise floor.

    PYTHONPATH=. uv run --no-project --python 3.13 --with-requirements analysis/requirements.txt --with scipy \
        python llm_negotiation/runs/rf53_stage2_pilot_thinking/analysis/pilot_tables.py
"""
import collections
import csv
import itertools
import json
from pathlib import Path

from scipy.stats import fisher_exact

from analysis.lateral import outcome_of, sidestep, when_level

RUNS = Path("llm_negotiation/runs")
BASE, PILOT = "rf40_round1_head_on_turn_taking", "rf53_stage2_pilot_thinking"


def design(name):
    with (RUNS / name / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        return {r["session_id"]: r for r in csv.DictReader(handle)
                if r["condition"] == "silent" and r["outcome"] == "completed" and "_x" not in r["session_id"]}


def tables(name):
    rows, steps, modes = design(name), collections.Counter(), collections.Counter()
    decisions = collections.defaultdict(lambda: collections.defaultdict(list))
    for line in (RUNS / name / "decisions.jsonl").open(encoding="utf-8"):
        d = json.loads(line)
        if d["session_id"] in rows:
            decisions[d["session_id"]][d["agent_id"]].append(d)
    for sid, row in rows.items():
        outcome = outcome_of(row)
        level = when_level(RUNS / name / "replay" / sid / "plan_only" / "trajectory.csv")
        steps[(outcome, sidestep(level["own_0_m"], level["own_1_m"]))] += 1
        reversal = never = False
        for ds in decisions[sid].values():
            dirs = [s["sidestep"]["to"] for d in sorted(ds, key=lambda d: d["number"])
                    for s in (d["steps"] or []) if isinstance(s, dict) and s.get("sidestep")]
            reversal |= any(a != b for a, b in zip(dirs, dirs[1:]))
            never |= not dirs
        modes[(outcome, "one never sidesteps" if never else ("a sidestep reversed" if reversal else "no reversal"))] += 1
    return rows, steps, modes


def main():
    out = {}
    for name in (BASE, PILOT):
        rows, steps, modes = tables(name)
        out[name] = steps, modes
        print(f"## {name}: {len(rows)} design sessions, silent\n")
        print("| plan_only outcome | how they stepped when level | sessions |\n| --- | --- | --- |")
        for (o, k), v in sorted(steps.items()):
            print(f"| {o} | {k} | {v} |")
        print("\n| plan_only outcome | failure mode | sessions |\n| --- | --- | --- |")
        for (o, k), v in sorted(modes.items()):
            print(f"| {o} | {k} | {v} |")
        print()
    by = collections.defaultdict(dict)
    for r in design(BASE).values():
        by[r["session_id"].rsplit("_r", 1)[0]][int(r["repeat"])] = r["resolved_plan_only"] == "True"
    print("## RF-40's own churn between repeats (silent, 64 cells)\n\n| repeats | changed | resolved, first | resolved, second |\n| --- | --- | --- | --- |")
    for a, b in itertools.combinations(range(1, 5), 2):
        pairs = [(v[a], v[b]) for v in by.values()]
        print(f"| {a} and {b} | {sum(x != y for x, y in pairs)} | {sum(x for x, _ in pairs)} | {sum(y for _, y in pairs)} |")

    def share(name, pred):
        return sum(v for k, v in out[name][0].items() if pred(k))
    print("\n## Fisher exact tests, two-sided (pilot 64 against RF-40's 256)\n")
    k_base = sum(r["resolved_plan_only"] == "True" for r in design(BASE).values())
    tests = {
        "resolved": (46, k_base),
        "both towards the same wall": (share(PILOT, lambda k: k[1] == "towards_same_wall"), share(BASE, lambda k: k[1] == "towards_same_wall")),
        "both to their own same side": (share(PILOT, lambda k: k[1] == "same_own_side"), share(BASE, lambda k: k[1] == "same_own_side")),
    }
    for label, (kp, kb) in tests.items():
        p = fisher_exact([[kp, 64 - kp], [kb, 256 - kb]]).pvalue
        print(f"- {label}: pilot {kp}/64, RF-40 {kb}/256, p = {p:.4f}")


if __name__ == "__main__":
    main()
