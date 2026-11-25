"""Runs every run of an experiment and writes its ``summary.csv``."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Optional

from ..configutil import PACKAGE_ROOT, REPO_ROOT, ConfigError, resolve_path
from ..llm.base import LLMClient
from ..llm.budget import BudgetedClient, BudgetGuard, SpendLedger, estimate_prompt_tokens
from ..llm.deepseek import DeepSeekClient
from ..llm.mock import MockClient
from ..llm.pricing import PriceTable
from ..negotiation.protocol import MAX_ATTEMPTS_PER_TURN
from ..runlog.schema import CONFIG_FILE, OUTCOME_FILE
from ..runlog.writer import write_summary
from .config import ExperimentConfig, RunPlan
from .runner import RunAborted, build_dialogue, execute_run

# Paid runs and runs without a model are research data and go under runs/, which is
# committed. Rehearsals with the mock client go under runs_mock/, which git ignores, so
# that a rehearsal can never be mistaken for, or block, the real thing.
RUNS_DIR = PACKAGE_ROOT / "runs"
MOCK_RUNS_DIR = PACKAGE_ROOT / "runs_mock"


def git_state() -> dict[str, Any]:
    """Current commit, and whether the code differs from it (run logs are not counted)."""

    def git(*args: str) -> Optional[str]:
        try:
            result = subprocess.run(
                ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=30, check=False
            )
        except (OSError, subprocess.SubprocessError):
            return None
        return result.stdout.strip() if result.returncode == 0 else None

    commit = git("rev-parse", "HEAD")
    status = git(
        "status", "--porcelain", "--", ".",
        ":(exclude)llm_negotiation/runs", ":(exclude)llm_negotiation/runs_mock",
        ":(exclude)llm_negotiation/spend_ledger.jsonl",
    )
    return {"commit": commit, "dirty": None if status is None else bool(status)}


def make_client(config: ExperimentConfig, client_name: Optional[str] = None) -> Optional[LLMClient]:
    """The client an experiment asks for; ``None`` if it does not negotiate."""
    if not config.negotiation["enabled"]:
        return None
    name = client_name or config.llm["client"]
    if name == "mock":
        return MockClient(policy=config.llm["mock_policy"])
    if name == "deepseek":
        prices = PriceTable.from_yaml()
        prices.price_of(config.llm["model"])  # refuse to start without a price for the model
        ledger = SpendLedger(resolve_path(config.budget["ledger"]))
        guard = BudgetGuard(ledger, config.budget["cap_usd"], prices)
        return BudgetedClient(DeepSeekClient.from_env(), guard)
    raise ConfigError(f"unknown client {name!r}; expected 'mock' or 'deepseek'")


def worst_case_cost(config: ExperimentConfig, plans: list[RunPlan], sends_per_call: int = 1) -> float:
    """An upper bound on what the planned runs could cost with the paid client.

    Every turn is assumed to be taken, every turn to need its retry, every prompt to
    carry the whole history at full length, and every call to be billed at peak rates.
    """
    if not config.negotiation["enabled"]:
        return 0.0
    from ..scenarios.registry import build_scenario

    prices = PriceTable.from_yaml()
    model, max_tokens = config.llm["model"], config.llm["max_tokens"]
    total = 0.0
    for plan in plans:
        dialogue = build_dialogue(plan, build_scenario(plan.scenario_config), MockClient())
        system_tokens = max(
            estimate_prompt_tokens([{"content": prompt}]) for prompt in dialogue.system_prompts.values()
        )
        per_turn_tokens = max_tokens + 300  # a reply plus a generous situation report
        for turn in range(dialogue.max_turns):
            prompt_tokens = system_tokens + (turn + 2) * per_turn_tokens
            total += MAX_ATTEMPTS_PER_TURN * sends_per_call * prices.worst_case(model, prompt_tokens, max_tokens)
    return total


def summary_row(config: Mapping[str, Any], outcome: Mapping[str, Any]) -> dict[str, Any]:
    """One row of ``summary.csv`` from a run's ``config.json`` and ``outcome.json``."""
    talk, roles, truth = outcome["negotiation"], outcome["roles"], outcome["ground_truth"] or {}
    tokens = talk["tokens"] or {}
    template = config["negotiation"]["prompt_template"] or {}
    row = {
        "experiment_name": config["experiment_name"],
        "run_id": config["run_id"],
        "condition": config["condition"],
        "scenario": config["scenario"]["type"],
        "scenario_variant": config["scenario_variant"],
        "info_variant": config["negotiation"]["info_variant"],
        "seed": config["seed"],
        "repeat": config["repeat"],
        "swap_sides": config["assignment"]["swap_sides"],
        "first_speaker": config["negotiation"]["first_speaker"],
        "timing_mode": config["negotiation"]["timing"]["mode"] if talk["enabled"] else None,
        "prompt_template": template.get("key"),
        "model": config["llm"]["model"],
        "temperature": config["llm"]["temperature"],
        "status": outcome["status"],
        "consensus_reached": talk["consensus_reached"],
        "turns_used": talk["turns_used"],
        "end_reason": talk["end_reason"],
        "negotiated_leader": talk["negotiated_leader"],
        "first_through": outcome["first_through"],
        "negotiated_roles_followed": roles["negotiated_roles_followed"],
        "fallback_used": outcome["fallback_used"],
        "collisions": outcome["collisions"]["agent_agent"] + outcome["collisions"]["agent_wall"],
        "deadlock": outcome["deadlock"],
        "makespan_s": outcome["makespan_s"],
        "time_to_goal_0_s": outcome["time_to_goal_s"]["0"],
        "time_to_goal_1_s": outcome["time_to_goal_s"]["1"],
        "follower": outcome["follower"],
        "follower_min_speed_mps": outcome["follower_min_speed_mps"],
        "path_deviation_m": outcome["path_deviation_m"]["mean"],
        "higher_priority_agent": truth.get("higher_priority_agent"),
        "higher_priority_first": truth.get("higher_priority_first"),
        "higher_priority_time_to_goal_s": truth.get("higher_priority_time_to_goal_s"),
        "llm_calls": talk["llm_calls"],
        "parse_failures": talk["parse_failures"],
        "prompt_tokens": tokens.get("prompt_tokens"),
        "completion_tokens": tokens.get("completion_tokens"),
        "cost_usd": talk["cost_usd"],
        "llm_latency_s": talk["llm_latency_s"],
        "git_commit": (config["git"].get("commit") or "")[:10],
    }
    for participant in config["participants"]:
        prefix, persona = f"agent{participant['agent_id']}", participant.get("persona") or {}
        row.update(
            {
                f"{prefix}_persona": persona.get("persona_id"),
                f"{prefix}_age": persona.get("age"),
                f"{prefix}_gender": persona.get("gender"),
                f"{prefix}_task_type": participant["task_type"],
                f"{prefix}_task": participant["task"],
                f"{prefix}_side": participant["side"],
            }
        )
    return row


@dataclass
class ExperimentResult:
    experiment_dir: Path
    summary_path: Optional[Path] = None
    executed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    aborted: Optional[str] = None
    rows: list[dict[str, Any]] = field(default_factory=list)

    @property
    def cost_usd(self) -> float:
        return sum(row["cost_usd"] or 0.0 for row in self.rows if row["run_id"] in self.executed)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_experiment(
    config: ExperimentConfig,
    client: Optional[LLMClient] = None,
    client_name: Optional[str] = None,
    out_root: Optional[Path | str] = None,
    limit: Optional[int] = None,
    overwrite: bool = False,
    report: Callable[[str], None] = print,
) -> ExperimentResult:
    """Execute an experiment's runs in order.

    A run whose folder already holds a finished outcome is skipped unless ``overwrite``
    is set, so an interrupted experiment can be resumed without paying twice. If a run is
    aborted (budget refused, model unreachable) the experiment stops there.
    """
    plans = config.plans()
    if limit is not None:
        plans = plans[:limit]
    if client is None:
        client = make_client(config, client_name)
    client_label = None if client is None else client.name
    if out_root is None:
        out_root = MOCK_RUNS_DIR if client_label == "mock" else RUNS_DIR
    experiment_dir = Path(out_root) / config.experiment_name
    experiment_dir.mkdir(parents=True, exist_ok=True)
    result = ExperimentResult(experiment_dir)
    git = git_state()

    for plan in plans:
        run_dir = experiment_dir / plan.run_id
        outcome_path = run_dir / OUTCOME_FILE
        if outcome_path.is_file() and not overwrite:
            previous = _read(run_dir / CONFIG_FILE)
            if previous["llm"]["client"] != client_label:
                raise ConfigError(
                    f"{run_dir} already holds a run made with client "
                    f"{previous['llm']['client']!r}, not {client_label!r}. Use another output "
                    "folder or pass overwrite."
                )
            if _read(outcome_path)["status"] != "aborted":
                result.skipped.append(plan.run_id)
                report(f"[{plan.index}/{len(plans)}] {plan.run_id}: already done, skipped")
                continue
        try:
            outcome = execute_run(plan, client, run_dir, git)
        except RunAborted as exc:
            result.aborted = str(exc)
            report(f"[{plan.index}/{len(plans)}] {plan.run_id}: ABORTED. {exc}")
            break
        result.executed.append(plan.run_id)
        talk = outcome["negotiation"]
        report(
            f"[{plan.index}/{len(plans)}] {plan.run_id}: {outcome['status']}"
            + (
                f", consensus {'yes' if talk['consensus_reached'] else 'no'} in {talk['turns_used']} turns"
                f", first through agent {outcome['first_through']}, USD {talk['cost_usd']:.6f}"
                if talk["enabled"]
                else f", first through agent {outcome['first_through']}"
            )
        )

    for plan in plans:
        run_dir = experiment_dir / plan.run_id
        if (run_dir / OUTCOME_FILE).is_file():
            result.rows.append(summary_row(_read(run_dir / CONFIG_FILE), _read(run_dir / OUTCOME_FILE)))
    result.summary_path = write_summary(experiment_dir, result.rows)
    return result
