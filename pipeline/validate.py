"""Step 6 (automatable part) — validate the aggregated dataset.

    python pipeline/validate.py

Reads   dataset/generated/behaviour_records.jsonl
Writes  dataset/generated/validation_report.md  (+ .json)

Covers the checks that can be done mechanically and defended in a report:
  1. schema conformance
  2. coverage (all 140 cells present)
  3. reliability (repeat agreement)
  4. free-flow walking-speed vs published bands  (citable)
  5. directional hypotheses (elderly slower, elderly yield more, ...)
  6. persona effect (a scenario must not collapse to one action for everyone)
  7. gender-difference audit (flag, do not fail)
  8. locality tally (singapore_specific / universal / mixed)

The parts that still need HUMAN judgement are listed in
dataset/schema/VALIDATION.md — this script does not replace them.
"""

from __future__ import annotations

import json
import statistics as stats
import sys
from collections import Counter, defaultdict

import config

AGES = ["child", "teenager", "young_adult", "middle_aged", "elderly"]
GENDERS = ["male", "female"]

# Free-flow walking speed bands (m/s). Loose, literature-informed; cite in report.
#   Weidmann 1993 (adult mean ~1.34), Bohannon 1997 (gait-speed norms),
#   child gait literature. These apply to the FREE-WALKING scenario only.
SPEED_BANDS = {
    "child":       (0.80, 1.35),
    "teenager":    (1.15, 1.65),
    "young_adult": (1.15, 1.65),
    "middle_aged": (1.05, 1.55),
    "elderly":     (0.75, 1.35),
}
FREE_WALK_SCENARIO = "covered_walkway_walking"
ORD = {"low": 0, "medium": 1, "high": 2, "slow": 0, "normal": 1, "fast": 2}


def load_records():
    path = config.OUT_DIR / "behaviour_records.jsonl"
    if not path.exists():
        print(f"[error] {path} not found — run generate.py then aggregate.py first")
        sys.exit(1)
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def check_schema(records):
    msgs = []
    try:
        import jsonschema
        schema = json.loads((config.DATASET_DIR / "schema" / "behaviour_record.schema.json").read_text("utf-8"))
        v = jsonschema.Draft202012Validator(schema)
        for r in records:
            for e in v.iter_errors(r):
                msgs.append(f"{r.get('record_id','?')}: {e.message}")
    except ImportError:
        msgs.append("jsonschema not installed — ran shallow checks only")
        for r in records:
            cb = r.get("conflict_behaviour", {})
            if cb.get("primary_action") not in (
                "proceed", "slow", "halt", "yield_step_aside", "speed_up", "back_off", "reroute"):
                msgs.append(f"{r.get('record_id','?')}: bad primary_action {cb.get('primary_action')}")
            yl = cb.get("yield_likelihood")
            if not isinstance(yl, (int, float)) or not (0 <= yl <= 1):
                msgs.append(f"{r.get('record_id','?')}: yield_likelihood out of [0,1]: {yl}")
    return msgs


def main() -> int:
    records = load_records()
    by_key = {(r["scenario_id"], r["age_group"], r["gender"]): r for r in records}
    scenarios = sorted({r["scenario_id"] for r in records})
    report = {"summary": {}, "fail": [], "review": [], "info": []}

    # 1. schema
    schema_msgs = check_schema(records)
    report["fail"] += [f"[schema] {m}" for m in schema_msgs if "not installed" not in m]
    report["info"] += [f"[schema] {m}" for m in schema_msgs if "not installed" in m]

    # 2. coverage
    expected = {(s, a, g) for s in scenarios for a in AGES for g in GENDERS}
    missing = expected - set(by_key)
    if missing:
        report["fail"].append(f"[coverage] {len(missing)} cells missing, e.g. {sorted(missing)[:5]}")
    report["summary"]["records"] = len(records)
    report["summary"]["scenarios"] = len(scenarios)

    # 3. reliability
    low_agree = [r["record_id"] for r in records
                 if r["aggregation"]["primary_action_agreement"] < 0.6]
    agree_vals = [r["aggregation"]["primary_action_agreement"] for r in records]
    report["summary"]["mean_primary_action_agreement"] = round(stats.mean(agree_vals), 3) if agree_vals else None
    report["summary"]["low_agreement_cells"] = len(low_agree)
    report["review"] += [f"[reliability] low repeat-agreement: {rid}" for rid in low_agree]

    # 4. free-flow speed vs bands
    for a in AGES:
        for g in GENDERS:
            r = by_key.get((FREE_WALK_SCENARIO, a, g))
            if not r:
                continue
            est = r["movement_profile"]["walking_speed_mps"].get("estimate")
            lo, hi = SPEED_BANDS[a]
            if est is None:
                report["fail"].append(f"[speed] {r['record_id']}: no estimate")
            elif not (lo <= est <= hi):
                report["review"].append(
                    f"[speed] {r['record_id']}: free-walk speed {est} m/s outside band {lo}-{hi}")

    # 5. directional hypotheses (averaged over scenarios per age, both genders)
    def age_mean_speed(a):
        vals = [by_key[(s, a, g)]["movement_profile"]["walking_speed_mps"]["estimate"]
                for s in scenarios for g in GENDERS
                if by_key.get((s, a, g)) and by_key[(s, a, g)]["movement_profile"]["walking_speed_mps"].get("estimate") is not None]
        return stats.mean(vals) if vals else None

    ya, el, ch = age_mean_speed("young_adult"), age_mean_speed("elderly"), age_mean_speed("child")
    hyp = []
    if ya and el:
        hyp.append(("elderly walk slower than young adults", el < ya))
    if ya and ch:
        hyp.append(("children walk slower than young adults", ch < ya))

    def age_mean_yield(a):
        vals = [by_key[(s, a, g)]["conflict_behaviour"]["yield_likelihood"]
                for s in scenarios for g in GENDERS
                if by_key.get((s, a, g)) and isinstance(by_key[(s, a, g)]["conflict_behaviour"]["yield_likelihood"], (int, float))]
        return stats.mean(vals) if vals else None

    ya_y, el_y = age_mean_yield("young_adult"), age_mean_yield("elderly")
    if ya_y is not None and el_y is not None:
        hyp.append(("elderly yield at least as much as young adults", el_y >= ya_y - 0.05))

    for name, ok in hyp:
        (report["info"] if ok else report["review"]).append(
            f"[hypothesis] {'PASS' if ok else 'FAIL'}: {name}")

    # 6. persona effect: a scenario must show >1 distinct primary_action across its 10 cells
    for s in scenarios:
        acts = {by_key[(s, a, g)]["conflict_behaviour"]["primary_action"]
                for a in AGES for g in GENDERS if by_key.get((s, a, g))}
        if len(acts) <= 1:
            report["review"].append(
                f"[persona-effect] scenario '{s}': every persona has the same primary_action ({acts}) "
                f"— persona may not be influencing the model")

    # 7. gender-difference audit (flag only)
    for s in scenarios:
        for a in AGES:
            m, f = by_key.get((s, a, "male")), by_key.get((s, a, "female"))
            if not (m and f):
                continue
            ym = m["conflict_behaviour"]["yield_likelihood"]
            yf = f["conflict_behaviour"]["yield_likelihood"]
            if isinstance(ym, (int, float)) and isinstance(yf, (int, float)) and abs(ym - yf) > 0.25:
                report["review"].append(
                    f"[gender-audit] {s}/{a}: yield_likelihood male={ym} female={yf} "
                    f"(Δ={round(ym-yf,2)}) — check this is evidence-based, not stereotype")
            am = m["conflict_behaviour"]["primary_action"]
            af = f["conflict_behaviour"]["primary_action"]
            if am != af:
                report["review"].append(
                    f"[gender-audit] {s}/{a}: primary_action male={am} female={af} — justify or flag")

    # 8. locality tally
    loc = Counter(r["conflict_behaviour"]["locality"] for r in records)
    report["summary"]["locality"] = dict(loc)

    # blind spot-check template (only if absent — never overwrite your answers).
    # Generated values go to a SEPARATE answers file you open only after filling.
    sc_path = config.OUT_DIR / "spotcheck_template.csv"
    ans_path = config.OUT_DIR / "spotcheck_answers.csv"
    import csv as _csv
    import random as _random
    rng = _random.Random(42)
    sample = rng.sample(sorted(by_key), k=min(15, len(by_key)))
    if not sc_path.exists():
        with open(sc_path, "w", encoding="utf-8", newline="") as fh:
            w = _csv.writer(fh)
            w.writerow(["scenario_id", "age_group", "gender",
                        "expected_primary_action", "expected_yield_likelihood", "expected_notes",
                        "verdict(agree|partial|disagree)", "reason"])
            for s, a, g in sample:
                w.writerow([s, a, g, "", "", "", "", ""])
        report["info"].append(f"[spotcheck] wrote blank template: {sc_path.name} "
                              f"— fill expected_* BEFORE opening {ans_path.name}")
    with open(ans_path, "w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(["scenario_id", "age_group", "gender",
                    "generated_primary_action", "generated_yield_likelihood", "generated_narrative"])
        for s, a, g in sample:
            r = by_key[(s, a, g)]
            cb = r["conflict_behaviour"]
            w.writerow([s, a, g, cb["primary_action"], cb["yield_likelihood"], cb["narrative"]])

    # ---- write report -----------------------------------------------------
    out_md = config.OUT_DIR / "validation_report.md"
    out_json = config.OUT_DIR / "validation_report.json"
    lines = ["# Dataset validation report", ""]
    lines.append("## Summary")
    for k, v in report["summary"].items():
        lines.append(f"- **{k}**: {v}")
    for bucket, title in [("fail", "FAIL — must fix"),
                          ("review", "REVIEW — human judgement needed"),
                          ("info", "INFO")]:
        lines += ["", f"## {title} ({len(report[bucket])})"]
        lines += [f"- {m}" for m in report[bucket]] or ["- none"]
    lines += ["", "## Still requires a human (see dataset/schema/VALIDATION.md)",
              "- blind spot-check of ~15 cells against hand-written expectations",
              "- comparison of emergent simulation behaviour vs RiMEA acceptance ranges",
              "- optional: expert / survey rating of sampled records"]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n".join(lines))
    print(f"\n[write] {out_md}\n[write] {out_json}")
    return 1 if report["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
