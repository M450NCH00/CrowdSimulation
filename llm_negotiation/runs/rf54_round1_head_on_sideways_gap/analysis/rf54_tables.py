"""RF-54 (issue #155): resolve_v11 (the sideways gap since the last look) against RF-40 (resolve_v9), silent.

All 256 design sessions of each (4 repeats; the counterfactual pairs left out), paired by session id:
- resolved in `plan_only`, pooled and per geometry, with McNemar's exact test on the changed pairs;
- RF-40's own churn between its repeats, as the noise floor;
- how they started (analysis.start_walls) and how often a same-wall start recovered, with Fisher's test;
- the reaction the cue is meant to change: at a decision where, since that person's last decision, both
  moved more than 0.1 m towards the same wall (measured in the plan_only replay, identically in both
  runs), did the reply step back towards the other wall, keep to the same wall, or not step aside?
  In RF-54 those people were told so; in RF-40 they were not.

    PYTHONPATH=. uv run --no-project --python 3.13 --with-requirements analysis/requirements.txt --with scipy \
        python llm_negotiation/runs/rf54_round1_head_on_sideways_gap/analysis/rf54_tables.py
"""
import collections
import csv
import itertools
import json
from pathlib import Path

from scipy.stats import binomtest, fisher_exact

from analysis import start_walls as W

RUNS = Path("llm_negotiation/runs")
BASE, NEW = "rf40_round1_head_on_turn_taking", "rf54_round1_head_on_sideways_gap"
MOVED_M = 0.1


def design(name):
    return W.design_sessions(RUNS / name)


def mcnemar(pairs):
    b = sum(x and not y for x, y in pairs)
    c = sum(y and not x for x, y in pairs)
    return b, c, (binomtest(b, b + c, 0.5).pvalue if b + c else 1.0)


def track(name, sid):
    ys = collections.defaultdict(dict)
    with (RUNS / name / "replay" / sid / "plan_only" / "trajectory.csv").open(encoding="utf-8", newline="") as h:
        for row in csv.DictReader(h):
            ys[round(float(row["time_s"]), 3)][int(row["agent_id"])] = float(row["y_m"])
    return ys


def y_at(ys, t):
    known = [s for s in ys if s <= t + 1e-9 and 0 in ys[s] and 1 in ys[s]]
    return ys[max(known)] if known else None


def reactions(name):
    rows = design(name)
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for line in (RUNS / name / "decisions.jsonl").open(encoding="utf-8"):
        d = json.loads(line)
        if d["session_id"] in rows:
            by[d["session_id"]][int(d["agent_id"])].append(d)
    out = collections.Counter()
    for sid, agents in by.items():
        ys = track(name, sid)
        for agent, ds in agents.items():
            ds = sorted(ds, key=lambda d: d["number"])
            for prev, d in zip(ds, ds[1:]):
                a, b = y_at(ys, float(prev["time_s"])), y_at(ys, float(d["time_s"]))
                if a is None or b is None:
                    continue
                m0, m1 = b[0] - a[0], b[1] - a[1]
                if abs(m0) < MOVED_M or abs(m1) < MOVED_M or (m0 > 0) != (m1 > 0):
                    continue
                shared = 1 if m0 > 0 else -1
                side = W.sidesteps([d])
                if not d.get("steps"):
                    out["unreadable"] += 1
                elif not side:
                    out["no sidestep"] += 1
                else:
                    out["back towards the other wall" if side[0][1] != shared else "further to the same wall"] += 1
    return out


def main():
    base, new = design(BASE), design(NEW)
    both = sorted(set(base) & set(new))
    print(f"# RF-54 against RF-40, silent: {len(both)} design sessions in both\n")
    print("## Resolved in plan_only (all four repeats)\n\n| Group | RF-40 | RF-54 | lost | gained | McNemar p |\n| --- | --- | --- | --- | --- | --- |")
    for label, keep in (("all", lambda r: True), ("layout=aligned", lambda r: r["geometry"] == "layout=aligned"),
                        ("layout=apart_20cm", lambda r: r["geometry"] == "layout=apart_20cm")):
        ids = [s for s in both if keep(base[s])]
        pairs = [(base[s]["resolved_plan_only"] == "True", new[s]["resolved_plan_only"] == "True") for s in ids]
        lost, gained, p = mcnemar(pairs)
        print(f"| {label} | {sum(x for x, _ in pairs)}/{len(ids)} | {sum(y for _, y in pairs)}/{len(ids)} | {lost} | {gained} | {p:.4f} |")

    cells = collections.defaultdict(dict)
    for r in base.values():
        cells[r["session_id"].rsplit("_r", 1)[0]][int(r["repeat"])] = r["resolved_plan_only"] == "True"
    print("\n## RF-40's own churn between two of its repeats (64 cells), the noise floor\n\n| repeats | lost | gained | McNemar p |\n| --- | --- | --- | --- |")
    for a, b in itertools.combinations(range(1, 5), 2):
        lost, gained, p = mcnemar([(v[a], v[b]) for v in cells.values()])
        print(f"| {a} and {b} | {lost} | {gained} | {p:.4f} |")

    s_base, s_new = W.sessions(RUNS / BASE), W.sessions(RUNS / NEW)
    print("\n## How they started, and recovery (analysis.start_walls)\n")
    print(W.markdown(BASE, W.table(s_base)) + "\n\n" + W.markdown(NEW, W.table(s_new)) + "\n")
    tb, tn = W.table(s_base), W.table(s_new)
    for start in ("same_wall", "opposite_walls"):
        kb, nb, kn, nn = tb[start]["resolved"], tb[start]["n"], tn[start]["resolved"], tn[start]["n"]
        p = fisher_exact([[kn, nn - kn], [kb, nb - kb]]).pvalue
        print(f"- {start}, resolved: RF-54 {kn}/{nn} ({kn / nn:.2f}), RF-40 {kb}/{nb} ({kb / nb:.2f}), Fisher p = {p:.4f}")
    p = fisher_exact([[tn['same_wall']['n'], len(s_new) - tn['same_wall']['n']], [tb['same_wall']['n'], len(s_base) - tb['same_wall']['n']]]).pvalue
    print(f"- same-wall starts: RF-54 {tn['same_wall']['n']}/{len(s_new)}, RF-40 {tb['same_wall']['n']}/{len(s_base)}, Fisher p = {p:.4f} (decision 1's prompt is the same)")
    print(f"- paired starts: {json.dumps(W.paired(s_base, s_new)['start_moves'])}\n")

    print(f"## The reaction: a decision after both moved over {MOVED_M} m or more towards the same wall\n")
    rb, rn = reactions(BASE), reactions(NEW)
    keys = ["back towards the other wall", "further to the same wall", "no sidestep", "unreadable"]
    print("| Reply | RF-40 (not told) | RF-54 (told) |\n| --- | --- | --- |")
    for k in keys:
        print(f"| {k} | {rb[k]} | {rn[k]} |")
    print(f"| all | {sum(rb.values())} | {sum(rn.values())} |")
    kb, kn = rb[keys[0]], rn[keys[0]]
    p = fisher_exact([[kn, sum(rn.values()) - kn], [kb, sum(rb.values()) - kb]]).pvalue
    print(f"\nBack towards the other wall: RF-54 {kn}/{sum(rn.values())}, RF-40 {kb}/{sum(rb.values())}, Fisher p = {p:.4f}")


if __name__ == "__main__":
    main()
