"""RF-55 (issue #157): resolve_v12 (only "they have moved over" on short lines) against RF-40 (resolve_v9) and
RF-54 (resolve_v11, the sideways gap), silent.

All 256 design sessions of each (4 repeats; the counterfactual pairs left out), paired by session id, with
RF-54's method (`runs/rf54_round1_head_on_sideways_gap/analysis/rf54_tables.py`):
- resolved in `plan_only`, pooled and per geometry; McNemar's exact test RF-55 against RF-40 (the move on
  short lines alone) and RF-54 against RF-55 (the gap numbers and "both moved over", given the move);
- how they started and how often a same-wall start recovered (analysis.start_walls), with Fisher's test;
- the reaction after both moved 0.1 m or more towards the same wall since that person's last decision.

    PYTHONPATH=. uv run --no-project --python 3.13 --with-requirements analysis/requirements.txt --with scipy \
        python llm_negotiation/runs/rf55_round1_head_on_short_moved/analysis/rf55_tables.py
"""
import importlib.util
from pathlib import Path

from scipy.stats import fisher_exact

from analysis import start_walls as W

RUNS = Path("llm_negotiation/runs")
RUN = {"RF-40": "rf40_round1_head_on_turn_taking", "RF-54": "rf54_round1_head_on_sideways_gap", "RF-55": "rf55_round1_head_on_short_moved"}

# RF-54's helpers (design sessions, McNemar, the reaction), loaded from its committed script.
_spec = importlib.util.spec_from_file_location("rf54_tables", RUNS / RUN["RF-54"] / "analysis" / "rf54_tables.py")
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)


def main():
    rows = {k: T.design(v) for k, v in RUN.items()}
    both = sorted(set.intersection(*(set(r) for r in rows.values())))
    print(f"# RF-55 against RF-40 and RF-54, silent: {len(both)} design sessions in all three\n")
    print("## Resolved in plan_only (all four repeats)\n")
    print("| Group | RF-40 (v9) | RF-55 (v12) | RF-54 (v11) | RF-55 vs RF-40: lost, gained, p | RF-54 vs RF-55: lost, gained, p |")
    print("| --- | --- | --- | --- | --- | --- |")
    for label, keep in (("all", lambda r: True), ("layout=aligned", lambda r: r["geometry"] == "layout=aligned"),
                        ("layout=apart_20cm", lambda r: r["geometry"] == "layout=apart_20cm")):
        ids = [s for s in both if keep(rows["RF-40"][s])]
        ok = {k: [rows[k][s]["resolved_plan_only"] == "True" for s in ids] for k in RUN}
        a = T.mcnemar(list(zip(ok["RF-40"], ok["RF-55"])))
        b = T.mcnemar(list(zip(ok["RF-55"], ok["RF-54"])))
        cells = " | ".join(f"{sum(ok[k])}/{len(ids)} ({sum(ok[k]) / len(ids):.2f})" for k in ("RF-40", "RF-55", "RF-54"))
        print(f"| {label} | {cells} | {a[0]}, {a[1]}, {a[2]:.4f} | {b[0]}, {b[1]}, {b[2]:.4f} |")

    print("\n## How they started, and recovery (analysis.start_walls)\n")
    tables = {}
    for k, v in RUN.items():
        found = W.sessions(RUNS / v)
        tables[k] = (W.table(found), len(found))
        print(W.markdown(f"{k} ({v})", tables[k][0]) + "\n")
    for start in ("same_wall", "opposite_walls"):
        line = []
        for k in ("RF-40", "RF-55", "RF-54"):
            t = tables[k][0][start]
            line.append(f"{k} {t['resolved']}/{t['n']} ({t['resolved'] / t['n']:.2f})")
        t40, t55 = tables["RF-40"][0][start], tables["RF-55"][0][start]
        p = fisher_exact([[t55["resolved"], t55["n"] - t55["resolved"]], [t40["resolved"], t40["n"] - t40["resolved"]]]).pvalue
        print(f"- {start}, resolved: " + ", ".join(line) + f"; RF-55 against RF-40, Fisher p = {p:.4f}")
    print()

    print(f"## The reaction: a decision after both moved over {T.MOVED_M} m or more towards the same wall\n")
    keys = ["back towards the other wall", "further to the same wall", "no sidestep", "unreadable"]
    found = {k: T.reactions(v) for k, v in RUN.items()}
    print("| Reply | RF-40 (not told) | RF-55 (told they moved) | RF-54 (told the gap) |\n| --- | --- | --- | --- |")
    for key in keys + ["all"]:
        print("| " + key + " | " + " | ".join(str(sum(found[k].values()) if key == "all" else found[k][key]) for k in ("RF-40", "RF-55", "RF-54")) + " |")
    k40, k55 = found["RF-40"][keys[0]], found["RF-55"][keys[0]]
    n40, n55 = sum(found["RF-40"].values()), sum(found["RF-55"].values())
    p = fisher_exact([[k55, n55 - k55], [k40, n40 - k40]]).pvalue
    print(f"\nBack towards the other wall: RF-55 {k55}/{n55}, RF-40 {k40}/{n40}, Fisher p = {p:.4f}")


if __name__ == "__main__":
    main()
