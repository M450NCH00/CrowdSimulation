"""Step 5 (part 2) — aggregate raw DeepSeek responses into canonical records.

    python pipeline/aggregate.py --run-id 20260904T101500-ab12cd

Reads   dataset/generated/raw/<run_id>.jsonl
Writes  dataset/generated/behaviour_records.jsonl   (canonical, matches schema)
        dataset/generated/behaviour_records.csv     (flattened convenience view)

Aggregation rules are documented in dataset/schema/README.md.
Re-running is free (no API calls) — safe to iterate on the rules here.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import statistics as stats
import sys
from collections import Counter, defaultdict

import config

CATEG = {
    "movement_profile": ["reaction_speed", "body_size", "acceleration_tendency"],
    "disposition": ["patience", "assertiveness", "rule_compliance",
                    "risk_tolerance", "situational_awareness"],
    "conflict_behaviour": ["fallback_action", "expected_resolution_time", "locality"],
}


def _mode(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return Counter(values).most_common(1)[0][0]


def _union_ranked(list_of_lists, cap):
    """Union of all phrases across repeats, deduped case-insensitively, ordered by
    how many repeats mention them (then first appearance), capped at `cap`.

    Free-text phrases almost never repeat verbatim across 3 samples, so a
    frequency *threshold* would wipe the list out. The union keeps signal; the
    ranking still surfaces anything the model said more than once first.
    """
    seen = {}   # lower -> [count, first_index, original]
    for idx, lst in enumerate(list_of_lists):
        for raw in (lst or []):
            s = str(raw).strip()
            if not s:
                continue
            key = s.lower()
            if key not in seen:
                seen[key] = [0, idx, s]
            seen[key][0] += 1
    ranked = sorted(seen.values(), key=lambda t: (-t[0], t[1]))
    return [orig for _, _, orig in ranked][:cap]


def aggregate_cell(rows):
    """rows: list of parsed `parsed` dicts for one (scenario, age, gender)."""
    mp = [r.get("movement_profile", {}) for r in rows]
    dp = [r.get("disposition", {}) for r in rows]
    cb = [r.get("conflict_behaviour", {}) for r in rows]

    speeds = [m.get("walking_speed_mps", {}) for m in mp]
    est = [s.get("estimate") for s in speeds if isinstance(s.get("estimate"), (int, float))]
    lo = [s.get("low") for s in speeds if isinstance(s.get("low"), (int, float))]
    hi = [s.get("high") for s in speeds if isinstance(s.get("high"), (int, float))]

    primary = [c.get("primary_action") for c in cb]
    primary_mode = _mode(primary)
    agreement = (sum(1 for p in primary if p == primary_mode) / len(primary)) if primary else 0.0

    yl = [c.get("yield_likelihood") for c in cb if isinstance(c.get("yield_likelihood"), (int, float))]

    out = {
        "movement_profile": {
            "walking_speed_mps": {
                "estimate": round(stats.mean(est), 3) if est else None,
                "low": round(min(lo), 3) if lo else (round(min(est), 3) if est else None),
                "high": round(max(hi), 3) if hi else (round(max(est), 3) if est else None),
            },
            **{k: _mode([m.get(k) for m in mp]) for k in CATEG["movement_profile"]},
        },
        "disposition": {k: _mode([d.get(k) for d in dp]) for k in CATEG["disposition"]},
        "conflict_behaviour": {
            "primary_action": primary_mode,
            "yield_likelihood": round(stats.mean(yl), 3) if yl else None,
            "decision_factors": _union_ranked([c.get("decision_factors") for c in cb], cap=8),
            "priority_rules": _union_ranked([c.get("priority_rules") for c in cb], cap=6),
            "narrative": max((c.get("narrative", "") for c in cb), key=len, default="")[:900],
            **{k: _mode([c.get(k) for c in cb]) for k in CATEG["conflict_behaviour"]},
        },
        "_agreement": round(agreement, 3),
        "_yl_std": round(stats.pstdev(yl), 3) if len(yl) > 1 else 0.0,
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()

    raw_path = config.OUT_DIR / "raw" / f"{args.run_id}.jsonl"
    if not raw_path.exists():
        print(f"[error] {raw_path} not found")
        return 1

    groups = defaultdict(list)   # (scenario, age, gender) -> [(raw_id, parsed)]
    n_total = n_ok = 0
    for line in raw_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        n_total += 1
        if rec.get("status") != "ok" or not rec["response"].get("parsed_ok"):
            continue
        n_ok += 1
        key = (rec["scenario_id"], rec["age_group"], rec["gender"])
        groups[key].append((rec["raw_id"], rec["response"]["parsed"]))

    print(f"[read] {n_total} raw rows, {n_ok} usable, {len(groups)} cells")

    out_jsonl = config.OUT_DIR / "behaviour_records.jsonl"
    out_csv = config.OUT_DIR / "behaviour_records.csv"
    now = dt.datetime.now(dt.timezone.utc).isoformat()

    records = []
    for (scn, age, gen), items in sorted(groups.items()):
        raw_ids = [i for i, _ in items]
        agg = aggregate_cell([p for _, p in items])
        low_agree = agg["_agreement"] < 0.6
        rec = {
            "record_id": f"sg__{scn}__{age}__{gen}",
            "schema_version": 1,
            "country": "Singapore",
            "scenario_id": scn, "age_group": age, "gender": gen,
            "movement_profile": agg["movement_profile"],
            "disposition": agg["disposition"],
            "conflict_behaviour": agg["conflict_behaviour"],
            "aggregation": {
                "n_repeats": len(items),
                "primary_action_agreement": agg["_agreement"],
                "yield_likelihood_std": agg["_yl_std"],
                "notes": ("LOW AGREEMENT — LLM inconsistent across repeats; treat with care"
                          if low_agree else "ok"),
            },
            "provenance": {
                "model": config.MODEL, "prompt_version": "v1",
                "generated_utc": now, "run_id": args.run_id,
                "raw_response_ids": raw_ids,
            },
        }
        records.append(rec)

    with open(out_jsonl, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    flat_cols = [
        "record_id", "scenario_id", "age_group", "gender",
        "speed_est", "speed_low", "speed_high", "reaction_speed", "body_size",
        "patience", "assertiveness", "rule_compliance", "risk_tolerance",
        "primary_action", "fallback_action", "yield_likelihood",
        "expected_resolution_time", "locality",
        "n_repeats", "primary_action_agreement", "notes",
    ]
    with open(out_csv, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=flat_cols)
        w.writeheader()
        for r in records:
            mp, dp, cb = r["movement_profile"], r["disposition"], r["conflict_behaviour"]
            w.writerow({
                "record_id": r["record_id"], "scenario_id": r["scenario_id"],
                "age_group": r["age_group"], "gender": r["gender"],
                "speed_est": mp["walking_speed_mps"]["estimate"],
                "speed_low": mp["walking_speed_mps"]["low"],
                "speed_high": mp["walking_speed_mps"]["high"],
                "reaction_speed": mp["reaction_speed"], "body_size": mp["body_size"],
                "patience": dp["patience"], "assertiveness": dp["assertiveness"],
                "rule_compliance": dp["rule_compliance"], "risk_tolerance": dp["risk_tolerance"],
                "primary_action": cb["primary_action"], "fallback_action": cb["fallback_action"],
                "yield_likelihood": cb["yield_likelihood"],
                "expected_resolution_time": cb["expected_resolution_time"],
                "locality": cb["locality"],
                "n_repeats": r["aggregation"]["n_repeats"],
                "primary_action_agreement": r["aggregation"]["primary_action_agreement"],
                "notes": r["aggregation"]["notes"],
            })

    low = [r["record_id"] for r in records if r["aggregation"]["primary_action_agreement"] < 0.6]
    print(f"[write] {len(records)} records -> {out_jsonl.name}, {out_csv.name}")
    if low:
        print(f"[flag] {len(low)} low-agreement cells (a finding for the RQ):")
        for rid in low:
            print(f"        {rid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
