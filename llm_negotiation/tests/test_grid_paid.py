"""RF-52 (issue #141): the grid's paid entry point, tested on the mock only.

The grid is an add-on (AS1): everything tested here is a new file (``negsim/grid/paid.py``,
``configs/grid/rf52_*.yaml``). The mock stands in for DeepSeek behind the real budget guard, so the
cap, the refusals and resuming after an abort are tested without a paid call.
"""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone

import pytest

from negsim.configutil import ConfigError, load_yaml, resolve_path
from negsim.llm.base import LLMRequest
from negsim.llm.budget import BudgetedClient, BudgetExceededError, SpendLedger
from negsim.llm.mock import MockClient
from negsim.llm.pricing import PriceTable
from negsim.resolution.mock import POLICIES
from negsim.grid import experiment as GE
from negsim.grid import paid as P

OWN, ABS = "configs/grid/rf52_round1_grid.yaml", "configs/grid/rf52_round1_grid_abs.yaml"
OFF_PEAK = datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)   # a Thursday, off-peak
PEAK = datetime(2026, 11, 26, 7, 0, tzinfo=timezone.utc)        # a Thursday, inside 06:00-10:00


def _config(path, tmp_path, cap=0.80):
    config = P.PaidGridConfig.load(path)
    return replace(config, ledger=str(tmp_path / "ledger.jsonl"), grid=replace(config.grid, cap_usd=cap))


def _paid_mock(config, now=OFF_PEAK):
    """The mock behind the real shared guard, standing in for DeepSeek."""
    guard = P.SharedBudgetGuard(SpendLedger(config.ledger), config.grid.cap_usd, PriceTable.from_yaml(), config.shared_with)
    return BudgetedClient(MockClient(policy=POLICIES[config.grid.llm["mock_policy"]]), guard, now=lambda: now)


class _Refuses:
    name, max_attempts = "deepseek", 1

    def complete(self, request):
        raise AssertionError("no call may be sent")


def test_the_configs_are_rf51s_sessions_with_rf40s_model_settings_and_one_cap_over_both_frames():
    rf40 = load_yaml(resolve_path("configs/resolution/round1_head_on_turn_taking.yaml"))["llm"]
    own, abs_ = P.PaidGridConfig.load(OWN), P.PaidGridConfig.load(ABS)
    assert (own.base_config, abs_.base_config) == ("configs/grid/round1_grid.yaml", "configs/grid/round1_grid_abs.yaml")
    assert (own.experiment_name, abs_.experiment_name) == ("rf52_round1_grid", "rf52_round1_grid_abs")
    for config, template in ((own, "resolve_grid_v1"), (abs_, "resolve_grid_abs_v1")):
        base = GE.GridExperimentConfig.load(config.base_config)
        assert config.grid.templates == base.templates and config.grid.templates["core"] == template
        assert config.grid.geometries == base.geometries and config.grid.conditions == ("silent",)
        assert config.grid.counterbalance_off_centre and config.grid.max_decision_points == 6
        for key in ("model", "temperature", "max_tokens", "thinking", "transport_retries"):
            assert config.grid.llm[key] == rf40[key], key
        assert config.grid.cap_usd == 0.80 and config.shared_with == ("rf52_round1_grid", "rf52_round1_grid_abs")
        assert config.gate == {"measure": "resolved_plan_only", "threshold": 0.50}
        assert config.expected_fingerprint == "bc19ba97cbe016479903222bb1578db6"
        assert len(GE.grid_sessions(config.grid)[1]) == 272


def test_the_config_refuses_a_cap_not_shared_with_itself_and_another_gate(tmp_path):
    raw = load_yaml(resolve_path(OWN))
    for change, match in (
        ({"budget": {**raw["budget"], "shared_with": ["rf52_round1_grid_abs"]}}, "shared_with"),
        ({"budget": {**raw["budget"], "over_cap": "refuse"}}, "over_cap"),
        ({"gate": {"measure": "resolved_plan_orca", "threshold": 0.5}}, "gate"),
        ({"llm": {**raw["llm"], "client": "openai"}}, "client"),
    ):
        path = tmp_path / "c.yaml"
        path.write_text(json.dumps({**raw, **change}), encoding="utf-8")
        with pytest.raises(ConfigError, match=match):
            P.PaidGridConfig.load(path)


def test_the_shared_guard_counts_both_frames_and_refuses_a_third_experiment(tmp_path):
    ledger = SpendLedger(tmp_path / "ledger.jsonl")
    for name, usd in (("rf52_round1_grid", 0.30), ("rf52_round1_grid_abs", 0.45), ("rf40_other", 5.0)):
        ledger.append({"experiment": name, "cost_usd": usd})
    guard = P.SharedBudgetGuard(ledger, 0.80, PriceTable.from_yaml(), ("rf52_round1_grid", "rf52_round1_grid_abs"))
    assert guard.spent_usd() == pytest.approx(0.75)
    small = LLMRequest([{"role": "user", "content": "x"}], "deepseek-flash", 1.0, 10, metadata={"experiment": "rf52_round1_grid_abs"})
    assert guard.authorise(small) > 0
    with pytest.raises(BudgetExceededError, match="not one of"):
        guard.authorise(replace(small, metadata={"experiment": "rf40_other"}))
    big = replace(small, max_tokens=300_000)
    with pytest.raises(BudgetExceededError, match="cap"):
        guard.authorise(big)


def test_a_paid_run_sends_nothing_unconfirmed_or_in_peak_hours(tmp_path):
    config = _config(OWN, tmp_path)
    summary = P.run(config, "deepseek", tmp_path / "runs", limit=1, confirm=False, client=_Refuses(), echo=lambda *a, **k: None)
    assert summary["status"] == P.STATUS_AWAITING
    with pytest.raises(ConfigError, match="peak"):
        P.run(config, "deepseek", tmp_path / "runs", limit=1, confirm=True, client=_Refuses(), echo=lambda *a, **k: None,
              now=lambda: PEAK)
    lines = (tmp_path / "runs" / "rf52_round1_grid" / P.INVOCATIONS_FILE).read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["status"] for line in lines] == [P.STATUS_AWAITING, P.STATUS_PEAK]
    assert not list((tmp_path / "runs" / "rf52_round1_grid" / "sessions").glob("*.json"))
    assert not (tmp_path / "ledger.jsonl").exists()


def test_the_guard_stops_the_run_at_the_cap_and_a_resume_sets_the_aborted_session_aside(tmp_path):
    config = _config(ABS, tmp_path, cap=0.006)
    out = tmp_path / "runs"
    first = P.run(config, "deepseek", out, limit=8, confirm=True, client=_paid_mock(config), echo=lambda *a, **k: None,
                  now=lambda: OFF_PEAK)
    assert first["status"] == P.STATUS_ABORTED
    spent = SpendLedger(config.ledger).total_usd()
    assert 0.001 < spent <= 0.006
    sessions = out / "rf52_round1_grid_abs" / "sessions"
    aborted = [p for p in sessions.glob("*.json") if json.loads(p.read_text(encoding="utf-8"))["outcome"] == "aborted"]
    assert len(aborted) == 1
    bigger = replace(config, grid=replace(config.grid, cap_usd=0.80))
    second = P.run(bigger, "deepseek", out, limit=1, confirm=True, client=_paid_mock(bigger), echo=lambda *a, **k: None,
                   now=lambda: OFF_PEAK)
    assert list(sessions.glob(f"{aborted[0].stem}.aborted1.json"))
    assert json.loads(aborted[0].read_text(encoding="utf-8"))["outcome"] == "completed"
    assert second["cost_usd_set_aside"] > 0
    assert second["cost_usd"] == pytest.approx(SpendLedger(config.ledger).total_usd(), abs=1e-6)
    assert all(entry["experiment"] == "rf52_round1_grid_abs" for entry in SpendLedger(config.ledger).entries())


def test_a_resumed_run_never_reruns_a_completed_session_and_reports_the_fingerprints(tmp_path):
    config = _config(OWN, tmp_path)
    out = tmp_path / "runs"
    P.run(config, "mock", out, limit=2, echo=lambda *a, **k: None)
    sessions = out / "rf52_round1_grid" / "sessions"
    before = {p.name: p.stat().st_mtime_ns for p in sessions.glob("*.json")}
    summary = P.run(config, "mock", out, limit=1, echo=lambda *a, **k: None)
    after = {p.name: p.stat().st_mtime_ns for p in sessions.glob("*.json")}
    assert len(after) == 3 and all(after[name] == stamp for name, stamp in before.items())
    assert summary["completed"] == 3 and summary["fingerprints"] == {"None": summary["calls"]}
    assert summary["gate"]["threshold"] == 0.50 and summary["gate"]["n"] == 3
    with pytest.raises(ConfigError, match="mock client"):
        P.run(config, "deepseek", out, limit=1, confirm=True, client=_paid_mock(config), echo=lambda *a, **k: None,
              now=lambda: OFF_PEAK)
