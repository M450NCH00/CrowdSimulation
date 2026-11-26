"""RF-52 (issue #141): round 1 on the grid, paid, in the agent's own frame and in the absolute frame.

    python -m negsim.grid.paid configs/grid/rf52_round1_grid.yaml --plan
    python -m negsim.grid.paid configs/grid/rf52_round1_grid.yaml --client deepseek --confirm --limit 6
    python -m negsim.grid.paid configs/grid/rf52_round1_grid.yaml --client mock --out runs_mock/rf52

**Why a module of its own.** RF-51's runner (:mod:`negsim.grid.experiment`) is mock only by design,
and the grid is an add-on (AS1): no existing file is edited. This module imports RF-51's sessions,
session runner and records unchanged, and adds what a paid run needs:

- **an RF-52 config** that names RF-51's config as its base (``base_config``) and sets its own
  experiment name, model settings and budget; the grid, the sessions, templates and protocol are
  the base's, untouched;
- **one cap over both frames** (the user's approval of 2026-11-26: USD 0.80 for #141's calls, both
  frames together): :class:`SharedBudgetGuard` counts the ledger lines of every experiment in
  ``budget.shared_with`` and refuses a call that could take their total past the cap. As the
  continuous runner's ``stop_at_cap``, the run starts and the guard stops it at the cap;
- **the ethics gates** of the continuous runner (RF-40's design varies perceived attractiveness and
  real ethnicity; both are signed off in ``CLAUDE.md``);
- **``--confirm``** before any paid call, and **no paid call in DeepSeek's peak hours** unless
  ``--allow-peak`` is given (the user asked for an off-peak run); checked before each session;
- **resume:** a completed session is never rerun; an aborted one is set aside
  (``<id>.aborted<N>.json``) and run again; a run stops at its first aborted session;
- **the record:** RF-51's session records, trajectories and ``outcomes.csv``, plus each call's
  model fingerprint in ``summary.json`` (checked against RF-40's, ``docs/action-space.md`` section 3),
  the recorded spend, and one line per invocation in ``invocations.jsonl``.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from ..configutil import ConfigError, check_keys, load_yaml, resolve_path
from ..llm.base import LLMClient
from ..llm.budget import BudgetedClient, BudgetExceededError, BudgetGuard, SpendLedger
from ..llm.mock import MockClient
from ..llm.pricing import PEAK, PriceTable
from ..resolution import experiment as E
from ..resolution.mock import POLICIES as MOCK_POLICIES
from ..resolution.perceive import LLMViewSettings
from . import experiment as X
from .agents import ABORTED, COMPLETED
from .measures import trajectory_csv
from .world import as_dict

CLIENTS = ("mock", "deepseek")
INVOCATIONS_FILE = "invocations.jsonl"
STATUS_COMPLETED, STATUS_PARTIAL, STATUS_ABORTED = "completed", "partial", "aborted"
STATUS_AWAITING, STATUS_PEAK = "awaiting_confirmation", "refused_peak_hours"
LLM_KEYS = ("client", "model", "temperature", "max_tokens", "thinking", "transport_retries")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class PaidGridConfig:
    """RF-52's config: RF-51's experiment (``grid``) with this run's name, model settings and budget."""

    grid: X.GridExperimentConfig
    issue: int
    base_config: str
    shared_with: tuple[str, ...]
    ledger: str
    expected_fingerprint: Optional[str]
    gate: Mapping[str, Any]
    source: str

    @property
    def experiment_name(self) -> str:
        return self.grid.experiment_name

    @classmethod
    def load(cls, path: Path | str) -> "PaidGridConfig":
        raw = load_yaml(resolve_path(path))
        where = str(path)
        check_keys(raw, where, required=(
            "schema_version", "type", "issue", "base_config", "experiment_name", "description", "llm", "budget", "gate",
        ), optional=("expected_fingerprint",))
        if raw["schema_version"] != 1 or raw["type"] != "grid_paid_experiment":
            raise ConfigError(f"{where}: expected schema_version 1 and type grid_paid_experiment")
        llm = check_keys(raw["llm"], f"{where}.llm", required=LLM_KEYS)
        if llm["client"] not in CLIENTS:
            raise ConfigError(f"{where}.llm.client: one of {list(CLIENTS)}, got {llm['client']!r}")
        budget = check_keys(raw["budget"], f"{where}.budget", required=("cap_usd", "shared_with", "ledger", "over_cap"))
        if budget["over_cap"] != E.OVER_CAP_STOP:
            raise ConfigError(f"{where}.budget.over_cap: the grid has no worst-case preview, so only {E.OVER_CAP_STOP!r}")
        cap = float(budget["cap_usd"])
        if cap < 0.0:
            raise ConfigError(f"{where}.budget.cap_usd must not be negative")
        shared = tuple(str(name) for name in budget["shared_with"])
        if str(raw["experiment_name"]) not in shared:
            raise ConfigError(f"{where}.budget.shared_with must name this experiment, {raw['experiment_name']!r}")
        gate = check_keys(raw["gate"], f"{where}.gate", required=("measure", "threshold"))
        if gate["measure"] != "resolved_plan_only" or not 0.0 < float(gate["threshold"]) <= 1.0:
            raise ConfigError(f"{where}.gate: measure resolved_plan_only and a threshold in (0, 1]")
        base = X.GridExperimentConfig.load(raw["base_config"])  # RF-51's own checks, unchanged
        grid = replace(
            base, experiment_name=str(raw["experiment_name"]), description=" ".join(str(raw["description"]).split()),
            llm={**base.llm, **{k: llm[k] for k in LLM_KEYS}}, cap_usd=cap, source=where,
        )
        return cls(grid, int(raw["issue"]), str(raw["base_config"]), shared, str(budget["ledger"]),
                   raw.get("expected_fingerprint"), {"measure": gate["measure"], "threshold": float(gate["threshold"])}, where)

    def as_dict(self) -> dict[str, Any]:
        g = self.grid
        return {
            "source": self.source, "issue": self.issue, "base_config": self.base_config,
            "experiment_name": g.experiment_name, "description": g.description, "design_from": g.design_from,
            "conditions": list(g.conditions), "grid": as_dict(g.grid), "geometries": dict(g.geometries),
            "counterbalance_off_centre": g.counterbalance_off_centre, "templates": dict(g.templates),
            "max_decision_points": g.max_decision_points, "min_gap_s": g.min_gap_s, "llm_view": g.llm_view,
            "llm": dict(g.llm), "budget": {"cap_usd": g.cap_usd, "shared_with": list(self.shared_with), "ledger": self.ledger},
            "expected_fingerprint": self.expected_fingerprint, "gate": dict(self.gate),
        }


class SharedBudgetGuard(BudgetGuard):
    """One cap over several experiments' calls together (#141: both frames under USD 0.80).

    A call must be labelled for one of ``scopes``; the spend is the sum of their ledger lines. A
    call that could take that sum past the cap is refused, as :class:`BudgetGuard` refuses one."""

    def __init__(self, ledger: SpendLedger, cap_usd: float, prices: PriceTable, scopes: Sequence[str]):
        super().__init__(ledger, cap_usd, prices, scope=None)
        self.scopes = tuple(scopes)

    def spent_usd(self) -> float:
        return math.fsum(self.ledger.total_usd(scope) for scope in self.scopes)

    def authorise(self, request: Any, max_attempts: int = 1) -> float:
        labelled = request.metadata.get("experiment")
        if labelled not in self.scopes:
            raise BudgetExceededError(f"call refused: it is labelled for experiment {labelled!r}, not one of {list(self.scopes)}")
        return super().authorise(request, max_attempts)


def make_client(config: PaidGridConfig, client_name: str, inner: Optional[LLMClient] = None) -> LLMClient:
    """The mock client (RF-51's mock policy), or the paid client behind the shared guard.
    ``inner`` stands in for DeepSeek in tests."""
    if client_name == "mock":
        return MockClient(policy=MOCK_POLICIES[config.grid.llm["mock_policy"]])
    if client_name != "deepseek":
        raise ConfigError(f"unknown client {client_name!r}; expected one of {list(CLIENTS)}")
    prices = PriceTable.from_yaml()
    prices.price_of(config.grid.llm["model"])
    guard = SharedBudgetGuard(SpendLedger(resolve_path(config.ledger)), config.grid.cap_usd, prices, config.shared_with)
    if inner is None:
        from ..llm.deepseek import DeepSeekClient

        inner = DeepSeekClient.from_env(max_retries=int(config.grid.llm["transport_retries"]))
    return BudgetedClient(inner, guard)


def _set_aside(path: Path) -> Path:
    number = 1
    while (aside := path.with_name(f"{path.stem}.aborted{number}.json")).exists():
        number += 1
    path.rename(aside)
    return aside


def fingerprints(records: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    """How many calls returned each model fingerprint (``None``: the mock, or no reply)."""
    found: Counter = Counter()
    for record in records:
        for point in record["decision_points"]:
            for attempt in point["attempts"]:
                found[str(attempt.get("system_fingerprint"))] += 1
        for debrief in record["debriefs"]:
            for attempt in debrief["attempts"]:
                found[str(attempt.get("system_fingerprint"))] += 1
    return dict(found.most_common())


def _comparable(experiment: Mapping[str, Any]) -> dict[str, Any]:
    """What must match for a folder to be resumed: everything but where the config was read from
    and the budget (a raised cap changes no session)."""
    return {key: value for key, value in experiment.items() if key not in ("source", "budget")}


def _start_folder(experiment_dir: Path, config: PaidGridConfig, client_name: str) -> None:
    path = experiment_dir / "config.json"
    started = any((experiment_dir / X.SESSIONS_DIR).glob("*.json"))
    if path.is_file() and started:
        existing = json.loads(path.read_text(encoding="utf-8"))
        if _comparable(existing.get("experiment", {})) != _comparable(json.loads(json.dumps(config.as_dict()))):
            raise ConfigError(f"{experiment_dir} holds a run of another config of {config.experiment_name}; give the changed "
                              "config a new experiment_name, or another --out")
        if existing.get("client_name") != client_name:
            raise ConfigError(f"{experiment_dir} was run with the {existing.get('client_name')} client, not {client_name}")
        return
    from ..experiment.batch import git_state

    path.write_text(json.dumps({
        "grid_log_version": 1, "layer": X.LAYER, "experiment": config.as_dict(), "client_name": client_name,
        "created_utc": _utc_now().isoformat(timespec="seconds"), "git": dict(git_state()),
    }, indent=2) + "\n", encoding="utf-8")


def run(
    config: PaidGridConfig, client_name: str, out_root: Path, limit: Optional[int] = None, confirm: bool = False,
    allow_peak: bool = False, client: Optional[LLMClient] = None, echo: Callable[..., None] = print,
    now: Callable[[], datetime] = _utc_now,
) -> dict[str, Any]:
    """Run (or resume) one frame. ``limit``: at most N sessions with no completed record yet."""
    grid = config.grid
    paid = client_name != "mock"
    base, sessions = X.grid_sessions(grid)
    experiment_dir = Path(out_root) / grid.experiment_name
    (experiment_dir / X.SESSIONS_DIR).mkdir(parents=True, exist_ok=True)
    (experiment_dir / X.TRAJECTORIES_DIR).mkdir(exist_ok=True)
    executed: list[str] = []
    status = STATUS_PARTIAL
    prices = PriceTable.from_yaml()

    def invocation(state: str, described: Mapping[str, Any]) -> None:
        with (experiment_dir / INVOCATIONS_FILE).open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps({
                "utc": now().isoformat(timespec="seconds"), "client": dict(described), "confirm": confirm, "limit": limit,
                "allow_peak": allow_peak, "status": state, "executed": executed,
            }) + "\n")

    if paid:
        design = base.design
        if design.uses_attractiveness and not E.attractiveness_signed_off():
            invocation("refused_no_sign_off", {"client": client_name})
            raise ConfigError("the design varies perceived attractiveness and its ethics sign-off is not recorded in CLAUDE.md")
        if design.uses_ethnicity and not E.ethnicity_signed_off():
            invocation("refused_no_sign_off", {"client": client_name})
            raise ConfigError("the design varies real ethnicity and its ethics sign-off is not recorded in CLAUDE.md")
        if not confirm:
            invocation(STATUS_AWAITING, {"client": client_name})
            echo(f"{grid.experiment_name}: {len(sessions)} session(s); a paid client, not confirmed: nothing was sent. "
                 "Run again with --confirm.")
            return {"status": STATUS_AWAITING}
        if not allow_peak and prices.tier_at(now()) == PEAK:
            invocation(STATUS_PEAK, {"client": client_name})
            raise ConfigError("DeepSeek's peak hours: no paid call now (the user asked for an off-peak run); --allow-peak overrides")
    if client is None:
        client = make_client(config, client_name)
    _start_folder(experiment_dir, config, client_name)

    view_settings = LLMViewSettings.load(resolve_path(grid.llm_view))
    indices = E.path_indices(sessions)
    budget = len(sessions) if limit is None else max(0, limit)
    aborted: Optional[str] = None
    for number, session in enumerate(sessions, 1):
        path = experiment_dir / X.SESSIONS_DIR / f"{session.session_id}.json"
        previous = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
        if previous is not None and previous["outcome"] == COMPLETED:
            continue
        if aborted is not None or len(executed) >= budget:
            continue
        if paid and not allow_peak and prices.tier_at(now()) == PEAK:
            aborted = "peak hours began: stopped before the next session"
            echo(f"  stopped: {aborted}", flush=True)
            continue
        if previous is not None:
            _set_aside(path)
        record, session_run = X.run_session(grid, base, session, client, indices[session.session_id], view_settings)
        path.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        if session_run.run is not None and record["outcome"] == COMPLETED:
            (experiment_dir / X.TRAJECTORIES_DIR / f"{session.session_id}.csv").write_text(
                trajectory_csv(session_run.run), encoding="utf-8", newline="\n")
        executed.append(session.session_id)
        g = record.get("grid_outcome") or {}
        echo(f"[{number}/{len(sessions)}] {session.session_id}: {record['outcome']}, "
             f"{'resolved' if g.get('resolved') else g.get('ended_by', '-')}, {record['totals']['calls']} call(s), "
             f"USD {record['totals']['cost_usd']:.6f}", flush=True)
        if record["outcome"] == ABORTED:
            aborted = record["error"]
            echo(f"  stopped: {aborted}", flush=True)

    records = []
    for session in sessions:
        path = experiment_dir / X.SESSIONS_DIR / f"{session.session_id}.json"
        if path.is_file():
            record = json.loads(path.read_text(encoding="utf-8"))
            if record["outcome"] == COMPLETED:
                records.append(record)
    status = STATUS_ABORTED if aborted else STATUS_COMPLETED if len(records) == len(sessions) else STATUS_PARTIAL
    (experiment_dir / "outcomes.csv").write_text(X.outcomes_csv([X.outcome_row(r) for r in records]), encoding="utf-8", newline="\n")
    set_aside = sorted((experiment_dir / X.SESSIONS_DIR).glob("*.aborted*.json"))
    aborted_usd = math.fsum(json.loads(p.read_text(encoding="utf-8"))["totals"]["cost_usd"] for p in set_aside)
    resolved = sum(bool(r["grid_outcome"]["resolved"]) for r in records)
    summary = {
        "experiment": grid.experiment_name, "issue": config.issue, "client": client_name, "status": status,
        "planned": len(sessions), **X.summarise(records),
        "gate": {**config.gate, "rate": resolved / len(records) if records else None, "n": len(records),
                 "baselines": "not available on the grid (no ORCA): the user's decision of 2026-11-26"},
        "cost_usd": round(math.fsum(r["totals"]["cost_usd"] for r in records) + aborted_usd, 6),
        "cost_usd_set_aside": round(aborted_usd, 6),
        "fingerprints": fingerprints(records), "expected_fingerprint": config.expected_fingerprint,
    }
    if paid:
        summary["cap"] = {"cap_usd": grid.cap_usd, "shared_with": list(config.shared_with),
                          "spent_usd_all_shared": round(client.guard.spent_usd(), 6) if hasattr(client, "guard") else None}
    (experiment_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    invocation(status, client.describe())
    echo(f"{status}: {len(executed)} session(s) run now, {len(records)} of {len(sessions)} completed; "
         f"USD {summary['cost_usd']:.6f} recorded for {grid.experiment_name}", flush=True)
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m negsim.grid.paid", description="RF-52: round 1 on the grid, paid (#141).")
    parser.add_argument("config")
    parser.add_argument("--client", choices=CLIENTS, help="overrides llm.client")
    parser.add_argument("--out", type=Path, help="default: runs/ for a paid client, runs_mock/ for the mock")
    parser.add_argument("--limit", type=int, help="run at most N sessions with no completed record yet")
    parser.add_argument("--confirm", action="store_true", help="needed before any paid call")
    parser.add_argument("--allow-peak", action="store_true", help="allow paid calls in DeepSeek's peak hours")
    parser.add_argument("--plan", action="store_true", help="list the sessions; run nothing")
    args = parser.parse_args(argv)
    config = PaidGridConfig.load(args.config)
    client_name = args.client or config.grid.llm["client"]
    if args.plan:
        _, sessions = X.grid_sessions(config.grid)
        layouts = Counter(X.lanes_of(config.grid, s)[0] + "/" + X.lanes_of(config.grid, s)[2] for s in sessions)
        print(f"{config.experiment_name}: {len(sessions)} silent session(s); "
              + ", ".join(f"{k}: {v}" for k, v in sorted(layouts.items()))
              + f"; cap USD {config.grid.cap_usd:.2f} shared with {list(config.shared_with)}")
        return 0
    out = args.out or resolve_path("runs" if client_name != "mock" else "runs_mock")
    summary = run(config, client_name, out, args.limit, args.confirm, args.allow_peak)
    return 0 if summary.get("status") in (STATUS_COMPLETED, STATUS_PARTIAL, STATUS_AWAITING) else 1


if __name__ == "__main__":
    sys.exit(main())
