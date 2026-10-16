"""Issue #30, Parts 9 and 10: the rule-generation experiment type, end to end on the mock client,
with replay and crowd screening; the cost preview; the budget guard; resuming."""

from __future__ import annotations

import json
import urllib.request
from collections import Counter
from datetime import datetime, timezone

import pytest

import negsim.llm.env as env_module
from negsim.configutil import ConfigError, PACKAGE_ROOT
from negsim.experiment import cli
from negsim.llm import BudgetedClient, BudgetGuard, LLMFatalError, MockClient, PriceTable, SpendLedger
from negsim.llm.budget import estimate_prompt_tokens
from negsim.rules.database import RULE_DB_ROOT, RuleDatabase
from negsim.rulegen import experiment as rg
from negsim.rulegen.mock import NEGOTIATION_PATHS, STATEMENT_PATHS, rulegen_agree
from negsim.rulegen.protocol import RuleNegotiation
from negsim.rulegen.validate import CATEGORIES
from negsim.rulegen.writer import StagingDatabase

GIT = {"commit": "test", "dirty": False}
PEAK_TUESDAY = datetime(2026, 10, 13, 7, 30, tzinfo=timezone.utc)
SMALL_CROWD = {"geometry": {"agents_per_direction": 4, "length": 20.0}, "max_time": 60.0}


def raw_config(**changes):
    raw = {
        "layer": "rule_generation",
        "experiment_name": "rg_test",
        "cases": {"set": "si3_v1", "ids": ["head_on_de176842", "overtaking_2d08db11"]},
        "conditions": ["negotiated", "stated"],
        "design": {
            "seed": 3,
            "factors": {
                "age_pair": ["same", "p1_older"], "gender_pair": ["p1_female"], "task": ["none", "p1_urgent"],
                "demographics_visible": [True, False], "mapping": ["p1_lower"], "order": ["lower_first"],
            },
        },
        "statement": {"repeats": 2},
        "llm": {"client": "mock", "mock_policy": "rulegen_paths"},
        "replay": {"enabled": True},
        "screening": {"enabled": True, "repeats": 1, "scenario_overrides": SMALL_CROWD},
    }
    raw.update(changes)
    return raw


def config(**changes):
    return rg.RuleGenConfig.from_raw(raw_config(**changes), "test")


def quiet(*_):
    pass


def no_network(*args, **kwargs):
    raise AssertionError("a test tried to open a network connection")


@pytest.fixture(scope="module")
def full_run(tmp_path_factory):
    """The whole experiment on the mock, once for this module, with the network blocked."""
    out = tmp_path_factory.mktemp("rulegen")
    rule_db_manifest = (RULE_DB_ROOT / "MANIFEST.json").read_text(encoding="utf-8")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(urllib.request, "urlopen", no_network)
        patch.setattr(env_module, "ENV_FILE_CANDIDATES", ())
        patch.delenv("DEEPSEEK_API_KEY", raising=False)
        result = rg.run_rule_generation(config(), out_root=out, report=quiet, git=GIT)
    folder = result.experiment_dir
    records = {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in (folder / rg.SESSIONS_DIR).glob("*.json")}
    validations = [json.loads(line) for line in (folder / rg.VALIDATION_FILE).read_text(encoding="utf-8").splitlines()]
    written = [json.loads(line) for line in (folder / rg.WRITTEN_FILE).read_text(encoding="utf-8").splitlines()]
    return {"result": result, "folder": folder, "records": records, "validations": validations, "written": written, "rule_db_manifest": rule_db_manifest}


# --- the config -----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"layer": "avoidance"}, "layer"),
        ({"experiment_name": "a b"}, "letters, digits"),
        ({"cases": {}}, "name a case set"),
        ({"cases": {"ids": ["a", "a"]}}, "distinct case ids"),
        ({"conditions": ["voted"]}, "distinct conditions"),
        ({"conditions": ["stated", "stated"]}, "distinct conditions"),
        ({"llm": {"client": "openai"}}, "expected one of"),
        ({"llm": {"mock_policy": "cheer"}}, "mock_policy"),
        ({"llm": {"temperature": -1}}, "at least"),
        ({"screening": {"enabled": True, "colour": "red"}}, "unknown key"),
        ({"budget": {"cap": 1}}, "unknown key"),
    ],
)
def test_a_bad_config_is_refused(changes, message):
    with pytest.raises(ConfigError, match=message):
        config(**changes)


def test_every_shipped_config_loads_names_the_mock_and_plans():
    shipped = sorted((PACKAGE_ROOT / "configs" / "rule_generation").glob("*.yaml"))
    assert [path.name for path in shipped] == ["si3_mock_rehearsal.yaml", "si3_pilot.yaml"]
    for path in shipped:
        cfg = rg.RuleGenConfig.load(path)
        assert cfg.llm["client"] == "mock", path.name  # paying is always an explicit --client deepseek
        assert rg.plan(cfg).preview["sessions"] > 0
    pilot = rg.plan(rg.RuleGenConfig.load(shipped[1])).preview
    assert pilot["sessions_by_condition"] == {"negotiated": 4, "stated": 8}
    assert pilot["usd_total"] == pytest.approx(0.6189372, abs=1e-6) and not pilot["fits_the_cap"]  # docs/rule-generation.md, section 10


def test_cases_by_set_and_id():
    assert [case["case_id"] for case in rg.selected_cases(config())] == ["head_on_de176842", "overtaking_2d08db11"]
    assert len(rg.selected_cases(config(cases={"set": "si3_v1"}))) == 18
    with pytest.raises(ConfigError, match="not in case set"):
        rg.selected_cases(config(cases={"set": "si3_v1", "ids": ["head_on_00000000"]}))


# --- the cost preview -----------------------------------------------------------------------------


@pytest.mark.parametrize("messages", [1, 2, 4, 6])
def test_the_negotiation_bound_is_the_sum_over_turns(messages):
    fixed, previous, cap = 1000, 650, 600
    turns = range(2 * messages)
    assert rg.negotiation_bound(messages, fixed, previous, cap) == (sum(fixed + t * previous for t in turns), 2 * messages * cap)
    assert rg.negotiation_bound(4, 1000, 650, 600) == (2 * 4 * 1000 + 650 * 4 * 7, 4800)
    assert rg.statement_bound(1200, 600) == (1200, 600)


def test_the_preview_prices_every_token_at_the_peak_cache_miss_rate_and_every_send():
    cfg = config(negotiation={"max_messages_per_agent": 3}, llm={"client": "mock", "max_tokens": 500, "transport_retries": 1})
    plan = rg.plan(cfg)
    preview, prices = plan.preview, PriceTable.from_yaml().price_of("deepseek-flash")
    assert preview["sends_per_turn"] == 2 * (1 + 1) and preview["max_retries_per_turn"] == 3
    assert preview["sessions_by_condition"] == {"negotiated": 16, "stated": 32}
    templates = plan.templates
    for row in preview["per_session"]:
        session = next(s for s in plan.sessions if s.session_id == row["session_id"])
        case, templ = plan.cases[session.case_id], templates[session.condition]
        if row["condition"] == "negotiated":
            wrapper = estimate_prompt_tokens([{"content": rg._turn_wrapper(templ)}])
            system = max(estimate_prompt_tokens([{"content": rg.negotiation_prompt(case, session, agent, templ)}]) for agent in session.agents)
            retry = estimate_prompt_tokens([{"content": templ.data["turns"]["retry"]}])
            assert (row["S_tokens"], row["m_tokens"]) == (system + wrapper + 500 + retry, 500 + wrapper)
            expected_in, expected_out = rg.negotiation_bound(3, row["S_tokens"], row["m_tokens"], 500)
        else:
            assert row["S_tokens"] == estimate_prompt_tokens([{"content": rg.statement_prompt(case, session, templ)}]) + 500 + estimate_prompt_tokens([{"content": templ.data["retry"]}])
            expected_in, expected_out = rg.statement_bound(row["S_tokens"], 500)
        assert (row["input_tokens_bound"], row["output_tokens_bound"]) == (4 * expected_in, 4 * expected_out)
        assert row["usd_bound"] == pytest.approx(4 * (expected_in * prices.input_cache_miss.peak + expected_out * prices.output.peak) / 1e6, abs=1e-8)
    assert preview["usd_total"] == pytest.approx(sum(row["usd_bound"] for row in preview["per_session"]), abs=1e-6)
    assert preview["fits_the_cap"] is (preview["usd_total"] <= 0.05)


def test_the_bound_holds_for_a_negotiation_that_uses_every_message_at_the_cap():
    """Replies as long as the cap allows (by the mock's count, 0.3 token a character), never
    agreeing: what the mock was sent stays under the preview's input bound for one send."""
    cfg = config(conditions=["negotiated"], llm={"client": "mock", "max_tokens": 600})
    plan = rg.plan(cfg)
    session = plan.sessions[0]
    rule = {"encounter": "any", "when": {"all": []}, "roles": "symmetric", "directive": {"both": {"clearance_margin": 0.1}}, "priority": 100}
    replies = []
    for k in range(8):
        reply = {"message": "", "proposal": {**rule, "priority": k}, "accept": None, "no_rule_possible": False}
        filler = int(600 / 0.3) - len(json.dumps(reply)) - 1
        reply["message"] = "word " * (filler // 5)
        replies.append(json.dumps(reply))
        assert len(replies[-1]) * 0.3 <= 600
    client = MockClient(script=replies)
    talk = RuleNegotiation(plan.cases[session.case_id], session, plan.templates["negotiated"], client, cfg.llm_settings(), 4)
    assert talk.run() == "no_agreement"
    used = talk.totals()["tokens"]["prompt_tokens"]
    row = next(r for r in plan.preview["per_session"] if r["session_id"] == session.session_id)
    assert used <= row["input_tokens_bound"] / plan.preview["sends_per_turn"]


# --- the whole experiment on the mock -----------------------------------------------------------


def test_every_path_of_both_protocols_is_taken(full_run):
    records = full_run["records"]
    negotiated = [r for r in records.values() if r["condition"] == "negotiated"]
    stated = [r for r in records.values() if r["condition"] == "stated"]
    assert len(negotiated) == 16 and len(stated) == 32 and full_run["result"].status == "completed"
    assert {r["outcome"] for r in negotiated} == {"agreed", "no_agreement", "no_rule_possible", "parse_failure"}
    assert {r["outcome"] for r in stated} == {"stated", "no_rule", "parse_failure"}
    statuses = Counter(turn["accept_status"] for r in negotiated for turn in r["turns"])
    assert {"agreed", "accepted_but_counter_proposed", "stale"} <= set(statuses)
    assert any(turn["n_attempts"] == 2 and turn["parse_ok"] for r in negotiated for turn in r["turns"])  # retried, then read
    assert any(len(r["attempts"]) == 2 and r["outcome"] == "stated" for r in stated)
    assert len({r["session"]["first"] for r in negotiated}) == 1  # one order level in this design
    assert len(NEGOTIATION_PATHS) <= 16 and len(STATEMENT_PATHS) <= 16


def test_every_proposal_is_categorised_and_none_is_discarded(full_run):
    records, validations = full_run["records"], full_run["validations"]
    proposals = sum(len(r["proposals"]) for r in records.values() if r["condition"] == "negotiated")
    rules = sum(1 for r in records.values() if r["condition"] == "stated" and r.get("rule") is not None)
    assert len(validations) == proposals + rules
    for condition in ("negotiated", "stated"):
        assert {row["category"] for row in validations if row["condition"] == condition} == set(CATEGORIES), condition
    sneaky = [row for row in validations if row["ignored_metadata"]]
    assert sneaky and all(row["ignored_metadata"]["rule_id"] == "the_models_own_id" for row in sneaky)
    summary = full_run["result"].summary
    counted = sum(sum(cell.values()) for scenarios in summary["categories_by_condition_and_scenario"].values() for cell in scenarios.values())
    assert counted == len(validations)


def test_only_valid_agreed_or_stated_rules_are_written_and_only_to_staging(full_run):
    folder, written, validations = full_run["folder"], full_run["written"], full_run["validations"]
    assert written and (RULE_DB_ROOT / "MANIFEST.json").read_text(encoding="utf-8") == full_run["rule_db_manifest"]
    valid = {(row["session_id"], row["canonical_hash"]) for row in validations if row["category"] == "valid" and row["agreed"]}
    for entry in written:
        assert all((session, entry["canonical_hash"]) in valid for session in entry["sessions"])
        rule = StagingDatabase(folder / "rule_db_staging" / entry["condition"]).latest(entry["rule_id"])
        assert rule.status == "candidate" and rule.provenance["source_type"] == entry["condition"]
        assert [s["session_id"] for s in rule.provenance["generation"]["sessions"]] == entry["sessions"]
    for condition in ("negotiated", "stated"):
        database = RuleDatabase.load(folder / "rule_db_staging" / condition)
        text = "".join(path.read_text(encoding="utf-8") for path in (database.root / "rules").glob("*.yaml"))
        assert "the_models_own_id" not in text and "status: validated" not in text
    assert len({entry["rule_id"] for entry in written}) == len(written)
    assert any(len(entry["sessions"]) > 1 for entry in written)  # one canonical rule, several sessions


def test_every_written_rule_is_replayed_and_screened_alone(full_run):
    folder = full_run["folder"]
    rows = [json.loads(line) for line in (folder / rg.SCREENING_FILE).read_text(encoding="utf-8").splitlines()]
    assert {row["rule_id"] for row in rows} == {entry["rule_id"] for entry in full_run["written"]}
    for row in rows:
        kinds = {entry["kind"]: entry for entry in row["entries"]}
        assert set(kinds) == {"replay", "crowd"}
        replayed = kinds["replay"]["results"]
        assert replayed["baseline_reproduces_case"] and kinds["replay"]["verdict"] == "recorded"
        assert replayed["run"]["baseline"]["rule_fired"] == 0
        assert (folder / replayed["folders"]["rule"] / "outcome.json").is_file()
        crowd = kinds["crowd"]
        assert crowd["verdict"] in ("passed", "failed") and crowd["scenario"] == "bidirectional_flow"
        assert crowd["results"]["per_seed"][0]["baseline"]["n_agents"] == 8
        config = json.loads((folder / crowd["results"]["per_seed"][0]["folders"]["rule"] / "config.json").read_text(encoding="utf-8"))
        assert [rule["rule_id"] for rule in config["directives"]["rules"]] == [row["rule_id"]]  # alone
        rule = StagingDatabase(folder / "rule_db_staging" / row["condition"]).latest(row["rule_id"])
        assert rule.version == row["version"] == 2 and len(rule.screening) == 2


def test_the_report_and_the_logs(full_run):
    folder, summary = full_run["folder"], full_run["result"].summary
    for name in (rg.CONFIG_FILE, rg.INVOCATIONS_FILE, rg.CASES_FILE, rg.DESIGN_FILE, rg.PREVIEW_FILE, rg.COST_FILE, rg.SUMMARY_FILE, rg.REPORT_FILE):
        assert (folder / name).is_file(), name
    written_config = json.loads((folder / rg.CONFIG_FILE).read_text(encoding="utf-8"))
    assert written_config["rulegen_log_version"] == rg.RULEGEN_LOG_VERSION and written_config["client_name"] == "mock"
    assert sum(sum(counts.values()) for counts in summary["outcomes"].values()) == summary["sessions"] == 48
    agreement = summary["agreement"]
    assert agreement["rate"] == pytest.approx(agreement["agreed"] / 16)
    assert agreement["accepted_rule_proposed_by_first_speaker"] + agreement["accepted_rule_proposed_by_second_speaker"] == agreement["agreed"]
    assert summary["stability"]["groups"] == 16 and 0.5 <= summary["stability"]["mean"] < 1.0  # one path changes its rule between repeats
    assert summary["cost"]["actual_usd"] == 0.0 and summary["model_wrote_metadata"] >= 2
    for row in summary["tokens_per_session"]:
        assert row["prompt_tokens"] <= row["preview_input_tokens"] and row["completion_tokens"] <= row["preview_output_tokens"]
    report = (folder / rg.REPORT_FILE).read_text(encoding="utf-8")
    assert "## Agreement (condition A)" in report and "needs_communication" in report
    record = next(iter(full_run["records"].values()))
    assert {"session", "templates", "llm", "outcome", "totals", "model_returned"} <= set(record)


def test_running_again_resumes_and_changes_nothing(full_run, tmp_path):
    folder = full_run["folder"]
    before = {path: path.read_text(encoding="utf-8") for path in (folder / "rule_db_staging").rglob("*") if path.is_file()}
    again = rg.run_rule_generation(config(), out_root=folder.parent, report=quiet, git=GIT)
    assert again.executed == [] and len(again.skipped) == 48 and again.status == "completed"
    after = {path: path.read_text(encoding="utf-8") for path in (folder / "rule_db_staging").rglob("*") if path.is_file()}
    assert after == before
    assert len((folder / rg.INVOCATIONS_FILE).read_text(encoding="utf-8").splitlines()) == 2
    with pytest.raises(ConfigError, match="another config"):
        rg.run_rule_generation(config(statement={"repeats": 3}), out_root=folder.parent, report=quiet, git=GIT)


# --- paid clients, the budget guard, resuming --------------------------------------------------------


def test_a_paid_client_sends_nothing_without_confirmation_and_is_not_even_built(tmp_path):
    cfg = config(llm={"client": "deepseek"}, budget={"cap_usd": 100.0, "ledger": str(tmp_path / "ledger.jsonl")}, replay={"enabled": False}, screening={"enabled": False})
    result = rg.run_rule_generation(cfg, out_root=tmp_path, report=quiet, git=GIT)  # no API key exists in a test
    assert result.status == "awaiting_confirmation" and result.executed == []
    assert (result.experiment_dir / rg.PREVIEW_FILE).is_file() and not (result.experiment_dir / rg.SESSIONS_DIR).exists()
    assert not (tmp_path / "ledger.jsonl").exists()
    (line,) = (result.experiment_dir / rg.INVOCATIONS_FILE).read_text(encoding="utf-8").splitlines()
    assert json.loads(line)["status"] == "awaiting_confirmation"
    with pytest.raises(LLMFatalError, match="DEEPSEEK_API_KEY"):  # only a confirmed run builds the paid client
        rg.run_rule_generation(cfg, out_root=tmp_path, confirm=True, report=quiet, git=GIT)


def test_a_preview_over_the_cap_is_refused_before_anything(tmp_path):
    cfg = config(llm={"client": "deepseek"}, budget={"cap_usd": 0.0001})
    with pytest.raises(ConfigError, match="exceeds the cap"):
        rg.run_rule_generation(cfg, out_root=tmp_path, confirm=True, report=quiet, git=GIT)


def test_the_budget_guard_stops_the_experiment_and_a_resume_runs_the_stopped_session_again(tmp_path):
    ledger = SpendLedger(tmp_path / "ledger.jsonl")
    ledger.append({"experiment": "an_earlier_experiment", "cost_usd": 5.0})  # the cap is the experiment's own
    cfg = config(llm={"client": "mock", "mock_policy": "rulegen_agree"}, replay={"enabled": False}, screening={"enabled": False})

    def client(cap):
        guard = BudgetGuard(ledger, cap, PriceTable.from_yaml(), scope=cfg.experiment_name)
        return BudgetedClient(MockClient(policy=rulegen_agree), guard, now=lambda: PEAK_TUESDAY)

    first = rg.run_rule_generation(cfg, client=client(0.004), out_root=tmp_path, report=quiet, git=GIT)
    assert first.status == "aborted" and "call refused" in first.aborted
    spent = ledger.total_usd(cfg.experiment_name)
    assert 0 < spent <= 0.004 and ledger.total_usd() == pytest.approx(5.0 + spent)
    stopped = first.executed[-1]
    assert json.loads((first.experiment_dir / rg.SESSIONS_DIR / f"{stopped}.json").read_text(encoding="utf-8"))["outcome"] == "aborted"
    assert all(entry["session_id"] for entry in ledger.entries()[1:])  # every paid call names its session

    second = rg.run_rule_generation(cfg, client=client(1.0), out_root=tmp_path, report=quiet, git=GIT)
    assert second.status == "completed" and second.executed[0] == stopped
    assert (first.experiment_dir / rg.SESSIONS_DIR / f"{stopped}.aborted1.json").is_file()  # the stopped attempt's log is kept
    assert second.summary["cost"]["actual_usd"] == pytest.approx(ledger.total_usd(cfg.experiment_name), rel=1e-6)


def test_a_limited_run_is_partial_and_running_again_completes_it(tmp_path):
    cfg = config(llm={"client": "mock", "mock_policy": "rulegen_agree"}, replay={"enabled": False}, screening={"enabled": False})
    first = rg.run_rule_generation(cfg, out_root=tmp_path, limit=5, report=quiet, git=GIT)
    assert first.status == "partial" and len(first.executed) == 5 and first.summary["sessions"] == 5
    second = rg.run_rule_generation(cfg, out_root=tmp_path, report=quiet, git=GIT)
    assert second.status == "completed" and len(second.executed) == 43 and len(second.skipped) == 5
    for entry in json.loads("[" + ",".join((second.experiment_dir / rg.WRITTEN_FILE).read_text(encoding="utf-8").splitlines()) + "]"):
        rule = StagingDatabase(second.experiment_dir / "rule_db_staging" / entry["condition"]).latest(entry["rule_id"])
        assert [s["session_id"] for s in rule.provenance["generation"]["sessions"]] == entry["sessions"]


# --- the command line -------------------------------------------------------------------------------


def test_the_command_line(tmp_path, capsys):
    path = tmp_path / "rg.yaml"
    budget = {"cap_usd": 100.0, "ledger": str(tmp_path / "ledger.jsonl")}
    path.write_text(json.dumps(raw_config(replay={"enabled": False}, screening={"enabled": False}, budget=budget)), encoding="utf-8")
    assert cli.main([str(path), "--plan"]) == 0
    out = capsys.readouterr().out
    assert "rule generation, 48 session(s) over 2 case(s)" in out and "worst-case cost USD" in out
    assert cli.main([str(path), "--client", "deepseek", "--out", str(tmp_path)]) == 4  # previewed; nothing sent
    assert "nothing was sent" in capsys.readouterr().out
    assert cli.main([str(path), "--overwrite"]) == 2
    assert cli.main([str(PACKAGE_ROOT / "configs" / "avoidance" / "si1_open_crossing.yaml"), "--confirm", "--plan"]) == 2
    assert cli.main([str(path), "--client", "mock", "--out", str(tmp_path / "mock"), "--limit", "3"]) == 0
    assert "partial: 3 session(s) run" in capsys.readouterr().out
