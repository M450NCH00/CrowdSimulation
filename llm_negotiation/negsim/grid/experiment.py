"""Round 1's sessions on the grid, with LLM agents (issue #140, RF-51): mock only.

    python -m negsim.grid.experiment configs/grid/round1_grid.yaml --out runs_mock/rf51_grid [--limit N]
    python -m negsim.grid.experiment configs/grid/round1_grid.yaml --plan

**The sessions** are RF-40's silent cells and people (``docs/action-space.md``, section 3; AS2: the
grid runs silent only): the design of ``design_from`` (RF-40's config) is planned with
:func:`negsim.resolution.experiment.plan`, and its silent sessions are kept. Each session's case
becomes a grid geometry (``geometries``): ``head_on_de176842`` (aligned) is ``aligned``, and
``head_on_02dfbadb`` (20 cm apart, which rounds to aligned on the grid, RF-50) is ``one_lane_apart``.

**Who starts off the centre lane** in ``one_lane_apart`` is counterbalanced (the user's decision of
2026-11-26): in a cell's repeats 1 and 2, person 2 is one lane off (RF-50's layout, lanes 2 and 1);
in repeats 3 and 4, person 1 is (lanes 3 and 2). Either way each person is off to its own left of
the other and sees the other to its own right, as in ``apart_20cm``. Repeats 1-2 against 3-4 keeps
it apart from who is asked first, which alternates odd and even (``first_asked``). Both sessions of
a counterfactual pair are first runs (repeat 1), so person 2 is off centre in both.

**No paid call.** This entry point runs the mock client only; RF-52 (#141) adds the paid run, with
its own approval and cap recorded in ``CLAUDE.md`` first.

**The cost estimate** (:func:`estimate_cost`) prices the rehearsal's calls as RF-40's silent calls
were priced: tokens per character of prompt, the share of prompt tokens read from the cache, and
the reply length are measured on RF-40's own silent records (``runs/rf40_round1_head_on_turn_taking``),
at off-peak prices. The mock's call count stands in for the model's.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ..configutil import ConfigError, check_keys, load_yaml, resolve_path
from ..llm.mock import MockClient
from ..llm.pricing import OFF_PEAK, PEAK, PriceTable
from ..resolution import experiment as E
from ..resolution.design import Session
from ..resolution.mock import POLICIES as MOCK_POLICIES
from ..resolution.perceive import LLMViewSettings
from ..resolution.prompt import DebriefTemplate
from ..rulegen.protocol import LLMSettings
from .agents import COMPLETED, GridSession
from .cases import lanes_for
from .measures import trajectory_csv
from .prompt import GridTemplate
from .world import GridConfig, as_dict, load_config

LAYER = "grid_resolution"
SESSIONS_DIR, TRAJECTORIES_DIR = "sessions", "trajectories"
#: RF-40's records, which the cost estimate is calibrated on.
CALIBRATION_RUN = "runs/rf40_round1_head_on_turn_taking"


@dataclass(frozen=True)
class GridExperimentConfig:
    experiment_name: str
    description: str
    design_from: str
    conditions: tuple[str, ...]
    grid: GridConfig
    geometries: Mapping[str, str]
    counterbalance_off_centre: bool
    templates: Mapping[str, str]
    max_decision_points: int
    min_gap_s: float
    llm_view: str
    llm: Mapping[str, Any]
    cap_usd: float
    source: str

    @classmethod
    def load(cls, path: Path | str) -> "GridExperimentConfig":
        raw = load_yaml(resolve_path(path))
        where = str(path)
        check_keys(raw, where, required=(
            "schema_version", "type", "experiment_name", "description", "design_from", "conditions", "grid", "geometries",
            "counterbalance_off_centre", "templates", "protocol", "llm_view", "llm", "budget",
        ))
        if raw["schema_version"] != 1 or raw["type"] != "grid_experiment":
            raise ConfigError(f"{where}: expected schema_version 1 and type grid_experiment")
        if list(raw["conditions"]) != ["silent"]:
            raise ConfigError(f"{where}: conditions: the grid runs silent only (AS2), got {raw['conditions']!r}")
        if raw["llm"].get("client") != "mock" or float(raw["budget"]["cap_usd"]) != 0.0:
            raise ConfigError(f"{where}: RF-51 is mock only: llm.client mock and budget.cap_usd 0 (RF-52 adds the paid run)")
        for case_id, geometry in raw["geometries"].items():
            lanes_for(load_config(raw["grid"]), geometry)  # an unknown geometry is refused here
        GridTemplate.load(raw["templates"]["core"])
        DebriefTemplate.load(raw["templates"]["debrief"])
        return cls(
            str(raw["experiment_name"]), " ".join(str(raw["description"]).split()), str(raw["design_from"]),
            tuple(raw["conditions"]), load_config(raw["grid"]), dict(raw["geometries"]), bool(raw["counterbalance_off_centre"]),
            dict(raw["templates"]), int(raw["protocol"]["max_decision_points"]), float(raw["protocol"]["min_gap_s"]),
            str(raw["llm_view"]), dict(raw["llm"]), float(raw["budget"]["cap_usd"]), where,
        )

    def llm_settings(self) -> LLMSettings:
        thinking = self.llm.get("thinking", "disabled") not in ("disabled", False)
        return LLMSettings(str(self.llm["model"]), float(self.llm["temperature"]), int(self.llm["max_tokens"]), thinking)


def design_config(config: GridExperimentConfig) -> E.ResolutionConfig:
    return E.ResolutionConfig.load(config.design_from)


def grid_sessions(config: GridExperimentConfig) -> tuple[E.ResolutionConfig, list[Session]]:
    """RF-40's sessions in the grid's conditions (silent), in RF-40's order."""
    base = design_config(config)
    planned = E.plan(base)
    sessions = [s for s in planned.sessions if s.condition in config.conditions]
    unknown = sorted({s.case_id for s in sessions} - set(config.geometries))
    if unknown:
        raise ConfigError(f"{config.source}: geometries has no grid geometry for the case(s) {unknown}")
    return base, sessions


def lanes_of(config: GridExperimentConfig, session: Session) -> tuple[str, tuple[int, int], str]:
    """The session's grid geometry, the two people's lanes, and who is off the centre lane."""
    geometry = config.geometries[session.case_id]
    lanes = lanes_for(config.grid, geometry)
    off = "neither" if lanes[0] == lanes[1] else "p2"
    if off == "p2" and config.counterbalance_off_centre and session.repeat in (3, 4):
        # Person 1 one lane to its own left (+y, heading +x), person 2 in the centre lane.
        centre = config.grid.centre_lane
        lanes, off = (centre + 1, centre), "p1"
    return geometry, lanes, off


def seed_of(session_id: str) -> int:
    return int(hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:8], 16)


def run_session(config: GridExperimentConfig, base: E.ResolutionConfig, session: Session, client: Any, path_index: int,
                view_settings: LLMViewSettings) -> tuple[dict[str, Any], GridSession]:
    geometry, lanes, off = lanes_of(config, session)
    if tuple(session.agents) != (0, 1):
        raise ConfigError(f"session {session.session_id}: the grid's walkers are 0 and 1, the case's people are {session.agents}")
    factors = E.session_factors(base, session) if session.uses_factors else None
    pairwise = E.session_pairwise(base, session) if session.uses_pairwise else None
    labels = {
        "experiment": config.experiment_name, "session_id": session.session_id, "condition": session.condition,
        "case_id": session.case_id, "repeat": session.repeat, "path_index": path_index,
    }
    grid = GridSession(
        config.grid, lanes, seed_of(session.session_id), GridTemplate.load(config.templates["core"]), client,
        config.llm_settings(), DebriefTemplate.load(config.templates["debrief"]), people=session.people,
        show_age=session.visibility.get("age", True), show_gender=session.visibility.get("gender", True),
        factors=factors, pairwise=pairwise, labels=labels, first_asked=E.first_asked(session),
        view_settings=view_settings, max_decision_points=config.max_decision_points, min_gap_s=config.min_gap_s,
    )
    grid.run_session()
    record = {
        "grid_log_version": 1,
        "experiment": config.experiment_name,
        "session_id": session.session_id,
        "session": session.as_dict(),
        "grid_geometry": geometry,
        "off_centre": off,
        "grid": as_dict(config.grid),
        "templates": {"core": grid.template.identity(), "debrief": grid.debrief_template.identity()},
        "llm": config.llm_settings().as_dict(),
        **({"factors": factors.as_dict()} if factors is not None else {}),
        **({"pairwise": pairwise.as_dict()} if pairwise is not None else {}),
        **grid.as_dict(),
    }
    return record, grid


OUTCOME_COLUMNS = (
    "session_id", "condition", "case_id", "grid_geometry", "lane_p1", "lane_p2", "off_centre", "repeat", "pair_id",
    "first_asked", "outcome", "resolved", "passed", "blocked_face_to_face", "squeezed_past", "dance",
    "first_changes_towards_same_wall", "deadlock", "ended_by", "passing_distance_m", "time_to_pass_s",
    "decision_points", "unreadable", "calls", "resolved_plan_only", "collision_plan_only",
)


def outcome_row(record: Mapping[str, Any]) -> dict[str, Any]:
    session, g = record["session"], record.get("grid_outcome") or {}
    gate = record.get("gate_columns") or {}
    row = {
        "session_id": record["session_id"], "condition": record["condition"], "case_id": session["case_id"],
        "grid_geometry": record["grid_geometry"], "lane_p1": record["lanes"][0], "lane_p2": record["lanes"][1],
        "off_centre": record["off_centre"], "repeat": session["repeat"], "pair_id": session.get("pair_id") or "",
        "first_asked": record["first_asked"], "outcome": record["outcome"],
        "decision_points": record["totals"]["decision_points"], "unreadable": record["totals"]["unreadable"],
        "calls": record["totals"]["calls"],
        "resolved_plan_only": gate.get("resolved_plan_only", ""), "collision_plan_only": gate.get("collision_plan_only", ""),
    }
    for key in ("resolved", "passed", "blocked_face_to_face", "squeezed_past", "dance", "first_changes_towards_same_wall",
                "deadlock", "ended_by", "passing_distance_m", "time_to_pass_s"):
        row[key] = g.get(key, "")
    for name, level in sorted(session["cell"].items()):
        row[f"cell_{name}"] = level
    return row


def outcomes_csv(rows: Sequence[Mapping[str, Any]]) -> str:
    out = io.StringIO()
    columns = list(OUTCOME_COLUMNS) + sorted({k for r in rows for k in r if k not in OUTCOME_COLUMNS})
    writer = csv.DictWriter(out, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def summarise(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    done = [r for r in records if r["outcome"] == COMPLETED]
    points = [p for r in records for p in r["decision_points"]]
    actions = Counter(p["parsed"]["action"] for p in points if p["parsed"])
    flags = Counter(f.split(":")[0] for p in points if p["plan_given"] for f in p["plan_given"]["flags"])
    errors = Counter(str(p["parse_error"]).split(":")[0] for p in points if p["parsed"] is None)
    by_geometry: dict[str, dict[str, int]] = {}
    for r in done:
        g = by_geometry.setdefault(f"{r['grid_geometry']}/{r['off_centre']}", Counter())
        g["sessions"] += 1
        for key in ("resolved", "passed", "blocked_face_to_face", "squeezed_past", "dance", "deadlock"):
            g[key] += int(bool(r["grid_outcome"][key]))
    return {
        "sessions": len(records), "completed": len(done),
        "resolved": sum(bool(r["grid_outcome"]["resolved"]) for r in done),
        "by_geometry": {k: dict(v) for k, v in sorted(by_geometry.items())},
        "decision_points": len(points), "calls": sum(r["totals"]["calls"] for r in records),
        "debriefs": sum(len(r["debriefs"]) for r in records),
        "unreadable": sum(1 for p in points if p["parsed"] is None),
        "actions": dict(actions.most_common()), "flags": dict(flags), "parse_errors": dict(errors),
        "reasons": dict(Counter(reason.split(":")[0] for p in points for reason in p["reasons"])),
    }


# --- the cost estimate ------------------------------------------------------------------------------


def _chars(messages: Sequence[Mapping[str, str]]) -> int:
    return sum(len(m["content"]) for m in messages)


def calibration(run_dir: Path | str = CALIBRATION_RUN, condition_prefix: str = "S_") -> dict[str, float]:
    """From RF-40's silent records: tokens per prompt character, the cached share of prompt tokens,
    and the mean reply length of a decision and of a debrief call."""
    chars = prompt = hit = 0
    out: dict[str, list[int]] = {"decision": [], "debrief": []}
    for path in sorted(resolve_path(run_dir).joinpath("sessions").glob(f"{condition_prefix}*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        kinds = [("decision", a) for p in record["decision_points"] for a in p["attempts"]]
        kinds += [("debrief", a) for d in record["debriefs"] for a in d["attempts"]]
        for kind, attempt in kinds:
            usage = attempt.get("usage") or {}
            if not usage.get("prompt_tokens"):
                continue
            chars += _chars(attempt["prompt_messages"])
            prompt += usage["prompt_tokens"]
            hit += usage.get("prompt_cache_hit_tokens", 0)
            out[kind].append(usage["completion_tokens"])
    if not prompt:
        raise ConfigError(f"no priced calls in {run_dir} to calibrate on")
    return {
        "tokens_per_char": prompt / chars, "cache_hit_share": hit / prompt,
        "decision_output_tokens": sum(out["decision"]) / len(out["decision"]),
        "debrief_output_tokens": sum(out["debrief"]) / len(out["debrief"]),
        "calls": len(out["decision"]) + len(out["debrief"]),
    }


def estimate_cost(records: Sequence[Mapping[str, Any]], model: str, cal: Mapping[str, float],
                  shorter_reply_tokens: float = 50.0) -> dict[str, Any]:
    """What the rehearsal's calls would cost on ``model``, priced as RF-40's silent calls were.
    The range: RF-40's mean reply length, and that less ``shorter_reply_tokens`` for a decision (a
    menu reply has no steps; an assumption, not a measurement, as RF-47's estimate)."""
    price = PriceTable.from_yaml().price_of(model)
    prompt_tokens = decisions = debriefs = 0.0
    for record in records:
        for p in record["decision_points"]:
            for a in p["attempts"]:
                prompt_tokens += _chars(a["prompt_messages"]) * cal["tokens_per_char"]
                decisions += 1
        for d in record["debriefs"]:
            for a in d["attempts"]:
                prompt_tokens += _chars(a["prompt_messages"]) * cal["tokens_per_char"]
                debriefs += 1
    result: dict[str, Any] = {"calls": int(decisions + debriefs), "prompt_tokens": round(prompt_tokens), "calibration": dict(cal)}
    for tier in (OFF_PEAK, PEAK):
        def usd(out_decision: float) -> float:
            hit = prompt_tokens * cal["cache_hit_share"]
            miss = prompt_tokens - hit
            out = decisions * out_decision + debriefs * cal["debrief_output_tokens"]
            return (hit * price.input_cache_hit.at(tier) + miss * price.input_cache_miss.at(tier) + out * price.output.at(tier)) / 1e6
        result[tier] = {
            "low_usd": round(usd(max(0.0, cal["decision_output_tokens"] - shorter_reply_tokens)), 4),
            "high_usd": round(usd(cal["decision_output_tokens"]), 4),
        }
    return result


# --- the run ----------------------------------------------------------------------------------------


def run_experiment(config: GridExperimentConfig, out: Path, limit: Optional[int] = None, echo=print) -> dict[str, Any]:
    base, sessions = grid_sessions(config)
    experiment_dir = out / config.experiment_name
    (experiment_dir / SESSIONS_DIR).mkdir(parents=True, exist_ok=True)
    (experiment_dir / TRAJECTORIES_DIR).mkdir(exist_ok=True)
    (experiment_dir / "config.json").write_text(json.dumps({
        "source": config.source, "experiment_name": config.experiment_name, "description": config.description,
        "design_from": config.design_from, "grid": as_dict(config.grid), "geometries": dict(config.geometries),
        "counterbalance_off_centre": config.counterbalance_off_centre, "templates": dict(config.templates),
        "max_decision_points": config.max_decision_points, "min_gap_s": config.min_gap_s, "llm": dict(config.llm),
    }, indent=2) + "\n", encoding="utf-8")
    client = MockClient(policy=MOCK_POLICIES[config.llm["mock_policy"]])
    view_settings = LLMViewSettings.load(resolve_path(config.llm_view))
    indices = E.path_indices(sessions)
    run_now = sessions if limit is None else sessions[:limit]
    ran = 0
    for number, session in enumerate(run_now, 1):
        path = experiment_dir / SESSIONS_DIR / f"{session.session_id}.json"
        if path.exists():
            continue
        record, grid = run_session(config, base, session, client, indices[session.session_id], view_settings)
        path.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        if grid.run is not None:
            (experiment_dir / TRAJECTORIES_DIR / f"{session.session_id}.csv").write_text(trajectory_csv(grid.run), encoding="utf-8", newline="\n")
        ran += 1
        g = record.get("grid_outcome") or {}
        echo(f"[{number}/{len(run_now)}] {session.session_id}: {record['outcome']}, "
             f"{'resolved' if g.get('resolved') else g.get('ended_by', '-')}, {record['totals']['calls']} call(s)", flush=True)
    records = [json.loads((experiment_dir / SESSIONS_DIR / f"{s.session_id}.json").read_text(encoding="utf-8"))
               for s in sessions if (experiment_dir / SESSIONS_DIR / f"{s.session_id}.json").exists()]
    (experiment_dir / "outcomes.csv").write_text(outcomes_csv([outcome_row(r) for r in records]), encoding="utf-8", newline="\n")
    summary = {"experiment": config.experiment_name, "planned": len(sessions), **summarise(records)}
    if len(records) == len(sessions):
        summary["cost_estimate"] = estimate_cost(records, config.llm["model"], calibration())
    (experiment_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    echo(f"{'completed' if len(records) == len(sessions) else 'partial'}: {ran} session(s) run, "
         f"{len(records) - ran} already done, {len(sessions)} planned; mock only, USD 0", flush=True)
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m negsim.grid.experiment", description="Round 1 on the grid with LLM agents (RF-51; mock only).")
    parser.add_argument("config")
    parser.add_argument("--out", type=Path, help="the folder to write the experiment into")
    parser.add_argument("--limit", type=int, help="run only the first N sessions")
    parser.add_argument("--plan", action="store_true", help="list the sessions and their grid geometries; run nothing")
    args = parser.parse_args(argv)
    config = GridExperimentConfig.load(args.config)
    if args.plan:
        _, sessions = grid_sessions(config)
        layouts = Counter(lanes_of(config, s)[0] + "/" + lanes_of(config, s)[2] for s in sessions)
        print(f"{config.experiment_name}: {len(sessions)} silent session(s); " + ", ".join(f"{k}: {v}" for k, v in sorted(layouts.items())))
        return 0
    if args.out is None:
        parser.error("--out is needed to run")
    run_experiment(config, args.out, args.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
