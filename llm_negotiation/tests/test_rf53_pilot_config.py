"""Issue #144 (RF-53), stage 2 pilot: RF-40's silent sessions, repeat 1 and the counterfactual pairs, with
thinking mode on. The user's choices of 2026-11-28: cap USD 1.00, "Repeat 1, with pairs".

The config is RF-40's with only the name, the conditions, the repeats and the llm block's thinking, reply
cap and timeout changed (and the cap); every session is RF-40's, with the same people. The new optional
``llm.timeout_s`` leaves every earlier config exactly as it was.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from negsim.configutil import PACKAGE_ROOT, REPO_ROOT, load_yaml, resolve_path
from negsim.llm import BudgetedClient
from negsim.resolution import experiment as E

RF40 = "configs/resolution/round1_head_on_turn_taking.yaml"
PILOT = "configs/resolution/rf53_stage2_pilot_thinking.yaml"


def test_the_pilot_is_rf40_with_thinking_on_silent_only_and_one_repeat():
    rf40, pilot = E.ResolutionConfig.load(RF40), E.ResolutionConfig.load(PILOT)
    assert pilot.experiment_name == "rf53_stage2_pilot_thinking"
    assert pilot.conditions == ("silent",) and rf40.design.repeats == 4 and pilot.design.repeats == 1
    assert replace(pilot.design, repeats=4) == rf40.design
    assert (pilot.protocol, pilot.templates, pilot.resolution_gate, pilot.llm_view, pilot.factor_values) == (
        rf40.protocol, rf40.templates, rf40.resolution_gate, rf40.llm_view, rf40.factor_values)
    changed = {"thinking": "enabled", "max_tokens": 16000, "timeout_s": 240.0}
    assert dict(pilot.llm) == {**dict(rf40.llm), **changed}
    assert pilot.llm_settings().thinking is True and rf40.llm_settings().thinking is False
    assert pilot.llm["client"] == "mock" and pilot.budget == {**rf40.budget, "cap_usd": 1.00}


def test_the_cap_is_the_one_claude_md_records_for_the_pilot():
    recorded = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "**Approved for issue #144 only, stage 2 pilot, 2026-11-28:**" in recorded and "**USD 1.00** on that experiment" in recorded
    assert load_yaml(resolve_path(PILOT))["budget"]["cap_usd"] == 1.00


def test_every_pilot_session_is_rf40s_repeat_1_or_pair_with_the_same_people():
    rf40 = {s.session_id: s for s in E.plan(E.ResolutionConfig.load(RF40)).sessions if s.condition == "silent"}
    pilot = {s.session_id: s for s in E.plan(E.ResolutionConfig.load(PILOT)).sessions}
    assert len(pilot) == 80 and sum("_x" in k for k in pilot) == 16
    assert set(pilot) == {k for k, s in rf40.items() if s.repeat == 1 or "_x" in k}
    for key, session in pilot.items():
        theirs = rf40[key]
        assert dict(session.personas) == dict(theirs.personas) and session.cell == theirs.cell
        assert session.repeat == theirs.repeat  # who is asked first goes by repeat parity


def test_no_earlier_resolution_config_gets_a_timeout_and_the_pilots_client_does(monkeypatch, tmp_path):
    for path in sorted((PACKAGE_ROOT / "configs" / "resolution").glob("*.yaml")):
        raw = load_yaml(path)
        if not E.is_resolution_config(raw) or path.name == Path(PILOT).name:
            continue
        assert "timeout_s" not in E.ResolutionConfig.load(path).llm, path.name
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-0123456789abcdef-NOT-A-REAL-KEY")  # nothing is sent
    pilot = E.make_client(E.ResolutionConfig.load(PILOT), "deepseek")
    assert isinstance(pilot, BudgetedClient) and pilot.inner.timeout_s == 240.0
    assert E.make_client(E.ResolutionConfig.load(RF40), "deepseek").inner.timeout_s == 60.0  # the client's default
