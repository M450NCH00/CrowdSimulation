"""What a pilot measures that the factor analysis does not (issue #64, RF-9, task 4).

Every cost figure before RF-9 was an estimate; event-driven prompting makes the number of calls
per session vary, so only a real run shows the typical cost against the worst case. This module
reads one resolution experiment's folder (``llm_negotiation/runs/<experiment>/``) and reports:

- **tokens per call**, for decision points and debriefs apart: prompt, reply and cache-hit
  tokens per send, against the preview's bound on one send (``preview.json``: ``S_decision``,
  ``S_debrief`` and the reply cap), and how many replies were cut off at the cap;
- **the cost**: the estimate per send (``cost_usd``), by price tier, per session and condition,
  against the preview, and the cache-hit share of input tokens;
- **decision points per agent** and their **trigger reasons**, **sends per session** (a retried
  call counts twice) against the bound on calls (k d + k), and **unreadable replies by reason**;
- **who passed first and on which side** (``outcomes.csv``, per mode), **signals** and messages.

The noise floor, stability, the debrief kinds and intent against plan are the main analysis's
(``python -m analysis``); this module does not repeat them. Standard library only, and it never
imports negsim: it reads the JSON the experiment wrote (``docs/log-schema.md``).

    python -m analysis.pilot llm_negotiation/runs/rf_pilot
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

MODES = ("plan_only", "plan_orca", "plain_orca")
KIND_DECISION, KIND_DEBRIEF = "decision", "debrief"


def _spread(values: Sequence[float], digits: int = 2) -> dict[str, Any]:
    if not values:
        return {"n": 0, "mean": None, "median": None, "max": None}
    return {"n": len(values), "mean": round(statistics.fmean(values), digits), "median": round(statistics.median(values), digits),
            "max": round(max(values), digits)}


def _sends(record: Mapping[str, Any]) -> Iterable[tuple[str, Mapping[str, Any]]]:
    """Every send of a session, labelled decision or debrief."""
    for point in record.get("decision_points") or []:
        for attempt in point.get("attempts") or []:
            yield KIND_DECISION, attempt
    for debrief in record.get("debriefs") or []:
        for attempt in debrief.get("attempts") or []:
            yield KIND_DEBRIEF, attempt


def _reason(error: Optional[str]) -> str:
    """``not_json: ...`` -> ``not_json``: the parser's reason, without the detail."""
    return str(error).split(":", 1)[0].strip() or "unknown"


def load_records(experiment: Path) -> list[dict[str, Any]]:
    """Session records, the aborted ones (``<id>.aborted<n>.json``) included: their calls were paid for."""
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted((experiment / "sessions").glob("*.json"))]


def measure(experiment: Path) -> dict[str, Any]:
    records = load_records(experiment)
    preview = json.loads((experiment / "preview.json").read_text(encoding="utf-8"))
    bounds = {row["session_id"]: row for row in preview["per_session"]}
    reply_cap = preview["reply_cap_tokens"]

    tokens: dict[str, dict[str, list[float]]] = {kind: defaultdict(list) for kind in (KIND_DECISION, KIND_DEBRIEF)}
    tiers: Counter = Counter()
    unreadable: Counter = Counter()
    api_errors: Counter = Counter()
    hit = prompt = 0
    cost_total = 0.0
    for record in records:
        bound = bounds.get(record["session_id"], {})
        for kind, attempt in _sends(record):
            usage = attempt.get("usage") or {}
            if attempt.get("api_error"):
                api_errors[_reason(attempt["api_error"])] += 1
            if attempt.get("parse_error"):
                unreadable[f"{kind}:{_reason(attempt['parse_error'])}"] += 1
            if not usage:
                continue
            rows = tokens[kind]
            rows["prompt"].append(usage.get("prompt_tokens", 0))
            rows["completion"].append(usage.get("completion_tokens", 0))
            rows["cache_hit"].append(usage.get("prompt_cache_hit_tokens", 0))
            rows["cut_off"].append(attempt.get("finish_reason") == "length")
            limit = bound.get("S_decision_tokens" if kind == KIND_DECISION else "S_debrief_tokens")
            if limit:
                rows["share_of_bound"].append(usage.get("prompt_tokens", 0) / limit)
            hit += usage.get("prompt_cache_hit_tokens", 0)
            prompt += usage.get("prompt_tokens", 0)
            cost_total += attempt.get("cost_usd") or 0.0
            tiers[attempt.get("price_tier") or "none"] += 1

    per_kind = {}
    for kind, rows in tokens.items():
        per_kind[kind] = {
            "sends": len(rows["prompt"]),
            "prompt_tokens": _spread(rows["prompt"]),
            "completion_tokens": _spread(rows["completion"]),
            "cache_hit_tokens": _spread(rows["cache_hit"]),
            "cache_hit_share": round(sum(rows["cache_hit"]) / sum(rows["prompt"]), 4) if sum(rows["prompt"]) else None,
            "cut_off_at_reply_cap": sum(rows["cut_off"]),
            "largest_share_of_the_bound_on_one_prompt": round(max(rows["share_of_bound"]), 4) if rows["share_of_bound"] else None,
        }

    by_condition: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    triggers: dict[str, Counter] = defaultdict(Counter)
    signals: dict[str, Counter] = defaultdict(Counter)
    messages: Counter = Counter()
    outcomes: Counter = Counter()
    for record in records:
        condition = record["condition"]
        outcomes[record["outcome"]] += 1
        rows = by_condition[condition]
        totals = record.get("totals") or {}
        bound = bounds.get(record["session_id"], {})
        rows["calls"].append(totals.get("llm_calls", 0))
        rows["cost"].append(totals.get("cost_usd", 0.0))
        if bound:
            rows["calls_bound"].append(bound["calls"])
            rows["cost_bound"].append(bound["usd_bound"])
            if bound["usd_bound"]:
                rows["share_of_preview"].append((totals.get("cost_usd") or 0.0) / bound["usd_bound"])
        per_agent = Counter(point["agent_id"] for point in record.get("decision_points") or [])
        for agent in (record.get("encounter") or {}).get("prompted") or []:
            rows["decision_points_per_agent"].append(per_agent.get(agent, 0))
        for point in record.get("decision_points") or []:
            for reason in point.get("trigger_reasons") or []:
                triggers[condition][reason.split(":", 1)[0]] += 1
        for signal in record.get("signals") or []:
            signals[condition][signal["signal"]] += 1
        messages[condition] += len(record.get("utterances") or [])

    conditions = {}
    for condition, rows in sorted(by_condition.items()):
        conditions[condition] = {
            "sessions": len(rows["calls"]),
            "calls_per_session": _spread(rows["calls"]),
            "calls_bound_per_session": max(rows["calls_bound"]) if rows["calls_bound"] else None,
            "decision_points_per_agent": dict(sorted(Counter(rows["decision_points_per_agent"]).items())),
            "cost_per_session_usd": _spread(rows["cost"], digits=6),
            "cost_usd": round(sum(rows["cost"]), 6),
            "preview_usd": round(sum(rows["cost_bound"]), 6),
            "largest_share_of_a_session_preview": round(max(rows["share_of_preview"]), 4) if rows["share_of_preview"] else None,
            "trigger_reasons": dict(triggers[condition].most_common()),
            "signals": dict(signals[condition].most_common()),
            "messages": messages[condition],
        }

    return {
        "experiment": experiment.name,
        "session_records": len(records),
        "session_outcomes": dict(outcomes),
        "reply_cap_tokens": reply_cap,
        "sends_per_call": preview["sends_per_call"],
        "preview_usd": preview["usd_total"],
        "cost_usd": round(cost_total, 6),
        "sends_by_price_tier": dict(tiers),
        "cache_hit_share_of_input": round(hit / prompt, 4) if prompt else None,
        "per_kind": per_kind,
        "per_condition": conditions,
        "unreadable_sends": dict(unreadable.most_common()),
        "api_errors": dict(api_errors.most_common()),
        "passing": passing(experiment / "outcomes.csv"),
    }


def passing(path: Path) -> dict[str, Any]:
    """Per mode and condition: resolved, who passed first (person a or b of the encounter's order,
    or none) and the passing sides, from ``outcomes.csv``."""
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out: dict[str, Any] = {}
    for mode in MODES:
        for condition in sorted({row["condition"] for row in rows}):
            mine = [row for row in rows if row["condition"] == condition and row.get(f"run_status_{mode}")]
            if not mine:
                continue
            out[f"{mode}/{condition}"] = {
                "sessions": len(mine),
                "resolved": sum(row.get(f"resolved_{mode}") == "True" for row in mine),
                "collision": sum(row.get(f"collision_{mode}") == "True" for row in mine),
                "near_miss": sum(row.get(f"near_miss_{mode}") == "True" for row in mine),
                "who_passed_first": dict(Counter(row.get(f"who_passed_first_{mode}") or "none" for row in mine).most_common()),
                "passing_sides": dict(Counter(
                    f"{row.get(f'passing_side_a_{mode}') or 'none'}/{row.get(f'passing_side_b_{mode}') or 'none'}" for row in mine
                ).most_common()),
            }
    out["resolved_by_llm"] = {
        condition: sum(row.get("resolved_by_llm") == "True" for row in rows if row["condition"] == condition)
        for condition in sorted({row["condition"] for row in rows})
    }
    return out


def markdown(measured: Mapping[str, Any]) -> str:
    lines = [f"# Pilot measures: {measured['experiment']}", ""]
    lines += [
        f"{measured['session_records']} session record(s) ({', '.join(f'{k} {v}' for k, v in measured['session_outcomes'].items())}). "
        f"Estimated cost USD {measured['cost_usd']} against a worst-case preview of USD {measured['preview_usd']}; "
        f"cache-hit share of input tokens {measured['cache_hit_share_of_input']}; sends by price tier "
        f"{measured['sends_by_price_tier']}. Reply cap {measured['reply_cap_tokens']} tokens.",
        "",
        "## Tokens per send",
        "",
        "| Kind | Sends | Prompt mean / median / max | Reply mean / median / max | Cache hit share | Cut off at the cap | Largest share of the bound |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for kind, row in measured["per_kind"].items():
        p, c = row["prompt_tokens"], row["completion_tokens"]
        lines.append(
            f"| {kind} | {row['sends']} | {p['mean']} / {p['median']} / {p['max']} | {c['mean']} / {c['median']} / {c['max']} | "
            f"{row['cache_hit_share']} | {row['cut_off_at_reply_cap']} | {row['largest_share_of_the_bound_on_one_prompt']} |"
        )
    lines += [
        "",
        "## Per condition",
        "",
        f"| Condition | Sessions | Sends mean / median / max (bound on calls, each up to {measured['sends_per_call']} sends) | Decision points per agent | Cost USD (preview) | Per session mean / max | Largest share of a session's preview |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for condition, row in measured["per_condition"].items():
        calls, cost = row["calls_per_session"], row["cost_per_session_usd"]
        points = ", ".join(f"{k}: {v}" for k, v in row["decision_points_per_agent"].items())
        lines.append(
            f"| {condition} | {row['sessions']} | {calls['mean']} / {calls['median']} / {calls['max']} ({row['calls_bound_per_session']}) | "
            f"{points} | {row['cost_usd']} ({row['preview_usd']}) | {cost['mean']} / {cost['max']} | {row['largest_share_of_a_session_preview']} |"
        )
    lines += ["", "## Trigger reasons, signals and messages", ""]
    for condition, row in measured["per_condition"].items():
        lines.append(f"- **{condition}**: triggers {row['trigger_reasons']}; signals {row['signals'] or 'none'}; messages {row['messages']}")
    lines += ["", "## Unreadable sends, by reason", ""]
    lines += [f"- {reason}: {count}" for reason, count in measured["unreadable_sends"].items()] or ["- none"]
    if measured["api_errors"]:
        lines += ["", "API errors:", *(f"- {reason}: {count}" for reason, count in measured["api_errors"].items())]
    lines += ["", "## Passing, per mode and condition", "", "| Mode / condition | Sessions | Resolved | Collision | Near miss | Who passed first | Passing sides (a/b) |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for key, row in measured["passing"].items():
        if key == "resolved_by_llm":
            continue
        lines.append(f"| {key} | {row['sessions']} | {row['resolved']} | {row['collision']} | {row['near_miss']} | {row['who_passed_first']} | {row['passing_sides']} |")
    if "resolved_by_llm" in measured["passing"]:
        lines += ["", f"Resolved by the LLM (resolved in `plan_only` and not handed to ORCA): {measured['passing']['resolved_by_llm']}"]
    return "\n".join(lines) + "\n"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiment", type=Path, help="a resolution experiment's folder, e.g. llm_negotiation/runs/rf_pilot")
    parser.add_argument("--out", type=Path, help="output folder (default: the experiment's analysis/ folder)")
    args = parser.parse_args(argv)
    measured = measure(args.experiment)
    out = args.out or args.experiment / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pilot_measures.json").write_text(json.dumps(measured, indent=2) + "\n", encoding="utf-8", newline="\n")
    (out / "pilot_measures.md").write_text(markdown(measured), encoding="utf-8", newline="\n")
    print(f"wrote {out / 'pilot_measures.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
