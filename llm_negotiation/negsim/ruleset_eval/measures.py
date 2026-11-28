"""What one avoidance run of a rule-set evaluation measured (issue #74, RF-18; ``docs/rule-set-evaluation.md``).

Everything here is read back from a finished run folder (``config.json``, ``outcome.json``,
``pair_interactions.jsonl``, ``trajectory.csv``), so a measure can be recomputed from committed
or rebuilt logs without running the simulation again.

* **Severe conflicts**: pair interactions at tier T3 or T4 (a near miss, a collision or a deadlock
  while the pair was open; ``metrics.md``, section 11.3). The main measure of the verdict.
* **Delay per agent**: time to goal minus the path's length over the agent's preferred speed,
  mean over the agents that arrived. A side measure.
* **Throughput**: agents arrived per minute of simulated time. A side measure.
* **Lane formation**, in the two-way flow only: for each agent, the mean of its lateral position
  on its own left (positive) or right, over the samples it spends in the middle stretch of the
  corridor; reported as the share of agents on their left and on their right. **[design]** the
  stretch, ``LANE_ZONE_HALF_LENGTH_M`` either side of the middle, is where the two groups meet.
* **Rule conflicts**: pairs matched by more than one rule over their life, ambiguous matches,
  cross-pair conflicts and plans not started because the person had one in force.
* **Uncovered conflicts**: pair interactions at tier T1 or above that no rule matched, grouped by
  encounter class (the class the pair spent most of its evaluations in; its class at the start if
  it has none) and tier.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Optional

from ..runlog.schema import PAIR_INTERACTIONS_FILE

SEVERE_TIERS = ("T3", "T4")
TIERS = ("T0", "T1", "T2", "T3", "T4")
GRIDLOCK_STATUSES = ("deadlock", "timeout")
LANE_SCENARIOS = ("bidirectional_flow",)
LANE_ZONE_HALF_LENGTH_M = 10.0
NO_CLASS = "none"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _mean(values: list[float]) -> Optional[float]:
    return round(sum(values) / len(values), 4) if values else None


def delay(config: Mapping[str, Any], outcome: Mapping[str, Any]) -> dict[str, Any]:
    """Each arrived agent's time to goal minus its free walk (path length over preferred speed)."""
    delays = []
    for agent in config["scenario"]["agents"]:
        reached = (outcome.get("time_to_goal_s") or {}).get(str(agent["agent_id"]))
        if reached is None or not agent.get("preferred_speed_mps"):
            continue
        delays.append(reached - agent["path_length_m"] / agent["preferred_speed_mps"])
    return {"mean_delay_s": _mean(delays), "max_delay_s": round(max(delays), 4) if delays else None, "agents_measured": len(delays)}


def lanes(run_dir: Path, config: Mapping[str, Any], half_length_m: float = LANE_ZONE_HALF_LENGTH_M) -> Optional[dict[str, Any]]:
    """The share of agents keeping to their left or right in the middle of a two-way corridor;
    ``None`` for another scenario or without a trajectory."""
    scenario = config["scenario"]
    path = run_dir / "trajectory.csv"
    if scenario.get("type") not in LANE_SCENARIOS or not path.is_file():
        return None
    direction = {}
    for agent in scenario["agents"]:
        dx = agent["goal"]["x"] - agent["start"]["x"]
        direction[agent["agent_id"]] = 1.0 if dx > 0 else -1.0
    offsets: dict[int, list[float]] = defaultdict(list)
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if abs(float(row["x_m"])) <= half_length_m:
                agent = int(row["agent_id"])
                offsets[agent].append(float(row["y_m"]) * direction[agent])  # positive: on its own left
    sides = Counter()
    for values in offsets.values():
        mean = sum(values) / len(values)
        sides["left" if mean > 0 else "right" if mean < 0 else "middle"] += 1
    counted = sum(sides.values())
    return {
        "zone_half_length_m": half_length_m,
        "agents": counted,
        "share_left": round(sides["left"] / counted, 4) if counted else None,
        "share_right": round(sides["right"] / counted, 4) if counted else None,
        "mean_offset_to_own_left_m": _mean([sum(v) / len(v) for v in offsets.values()]),
    }


def pair_class(pair: Mapping[str, Any]) -> str:
    """The encounter class a pair spent most of its evaluations in, else its class at the start."""
    counts: Counter = Counter()
    for entry in ((pair.get("rules") or {}).get("evaluations") or []):
        if entry.get("encounter_class") not in (None, NO_CLASS):
            counts[entry["encounter_class"]] += entry.get("count", 1)
    if counts:
        return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
    return pair.get("encounter_class_at_start") or NO_CLASS


def pair_measures(run_dir: Path) -> dict[str, Any]:
    """Rule conflicts and uncovered conflicts, from the run's pair interactions."""
    pairs = _read_jsonl(run_dir / PAIR_INTERACTIONS_FILE)
    several_rules = ambiguous = 0
    uncovered: Counter = Counter()
    for pair in pairs:
        rules = pair.get("rules")
        matches = (rules or {}).get("matches") or []
        if len({match["rule_id"] for match in matches}) > 1:
            several_rules += 1
        ambiguous += sum(1 for match in matches if match.get("outcome") == "ambiguous_match")
        tier = pair.get("severity_tier")
        if rules is not None and not matches and tier in TIERS[1:]:
            uncovered[(pair_class(pair), tier)] += 1
    return {
        "pairs": len(pairs),
        "pairs_matched_by_several_rules": several_rules,
        "ambiguous_matches": ambiguous,
        "uncovered": [{"encounter_class": cls, "tier": tier, "pairs": n} for (cls, tier), n in sorted(uncovered.items())],
    }


def run_measures(run_dir: Path) -> dict[str, Any]:
    """Every measure of one finished run."""
    run_dir = Path(run_dir)
    config, outcome = _read_json(run_dir / "config.json"), _read_json(run_dir / "outcome.json")
    tiers = (outcome.get("interaction_outcomes") or {}).get("tiers") or {}
    elapsed, arrived = outcome["sim_time_s"], outcome["arrived"]
    rules = outcome.get("rules") or {}
    plans = rules.get("plans") or {}
    return {
        "status": outcome["status"],
        "gridlocked": outcome["status"] in GRIDLOCK_STATUSES,
        "n_agents": outcome["n_agents"],
        "arrived": arrived,
        "sim_time_s": elapsed,
        "steps": outcome["steps"],
        "severe_conflicts": sum(tiers.get(tier, 0) for tier in SEVERE_TIERS),
        "tiers": {tier: tiers.get(tier, 0) for tier in TIERS},
        "collision_episodes": outcome["collisions"]["agent_agent"] + outcome["collisions"]["agent_wall"],
        "near_misses": outcome["totals"]["near_misses"],
        "throughput_agents_per_min": round(60.0 * arrived / elapsed, 4) if elapsed else None,
        **delay(config, outcome),
        "lanes": lanes(run_dir, config),
        "rule_matches": sum((rules.get("matches_begun") or {}).values()),
        "matches_by_rule": dict(rules.get("matches_begun") or {}),
        "cross_pair_conflicts": rules.get("cross_pair_conflicts", 0),
        "formation_mismatches": rules.get("formation_mismatches", 0),
        "plans_started": plans.get("plans_started", 0),
        "plans_skipped_busy": plans.get("plans_skipped_busy", 0),
        **pair_measures(run_dir),
    }
