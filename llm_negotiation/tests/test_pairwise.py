"""Issue #61 (RF-6): the pairwise perception factors, perceived attractiveness (a matrix: who looks,
who is seen) and familiarity: the block, the lines each observer is told and nobody else is, the
switches, the design, the numeric outcome columns, the ethics gate, the rule check, and that
everything written before them behaves as before (``docs/pairwise-factors.md``;
``docs/resolution.md``, D2). And ``resolve_v3`` (the user's decision of 2026-10-23), which prints
the factor lines on the short line of someone 5 to 10 m away too, and is the default core
template of a design with factors."""

from __future__ import annotations

import json

import pytest

from negsim import ethics
from negsim.configutil import ConfigError
from negsim.negotiation import prompts
from negsim.resolution import design as D
from negsim.resolution import experiment as E
from negsim.resolution import pairwise as W
from negsim.resolution.perceive import Exchange
from negsim.resolution import factors as F
from negsim.resolution.prompt import FACTOR_CORE_TEMPLATE, SIMULATION_CORE_TEMPLATE, CoreTemplate, default_core, render
from negsim.resolution.transcript import render as transcript
from negsim.rulegen import experiment as rg
from negsim.rulegen.design import visibility_of
from negsim.rulegen.validate import PROTECTED_ATTRIBUTE, SCHEMA_ERROR, validate_proposal
from negsim.rules.database import RULE_DB_ROOT, load_validator
from negsim.rules.errors import RuleError
from negsim.rules.fields import CONDITION_PREFIXES, ROLE_PREFIXES, resolve
from negsim.rules.model import parse_rule
from negsim.avoidance.perception import default_visibility
from test_encounter_protocol import GIT, OVERTAKING, PASSAGE, SLOW, reply, session_on
from test_perceive import PASSING, SETTINGS, V1, V2, at, look, perceiver
from test_resolution import GROUP_WORDS, ORDER_WORDS, SUGGESTIONS
from test_rulegen_validate import rule, when

TEMPLATE = W.PairwiseTemplate.load()
V3 = CoreTemplate.load(FACTOR_CORE_TEMPLATE)
SIGN_OFF = "Ethics sign-off for the perceived-attractiveness factor (issue #61): approved by the supervisor on 2026-11-02"
ATTRACTIVE, UNREMARKABLE = TEMPLATE.line(W.ATTRACTIVENESS, "attractive"), TEMPLATE.line(W.ATTRACTIVENESS, "unremarkable")
STRANGERS, ACQUAINTANCES = TEMPLATE.line(W.FAMILIARITY, "strangers"), TEMPLATE.line(W.FAMILIARITY, "acquaintances")
ALL_LINES = (ATTRACTIVE, UNREMARKABLE, STRANGERS, ACQUAINTANCES)
#: Issue #61's own example: agent 0 finds agent 1 attractive; agent 1 does not find agent 0 attractive.
ISSUE_BLOCK = {"perceived_attractiveness": [[None, "attractive"], ["unremarkable", None]], "familiarity": "strangers"}


def pairwise(block=None, visible=None):
    return W.PairwiseFactors.from_block(ISSUE_BLOCK if block is None else block, TEMPLATE, visible)


def quiet(_):
    pass


# --- the template ----------------------------------------------------------------------------------


def test_the_pairwise_template_is_frozen_and_has_issue_61s_lines():
    entry = prompts.load_manifest()[W.PAIRWISE_TEMPLATE]
    assert entry["kind"] == W.KIND_PAIRWISE and entry["sha256"] == TEMPLATE.sha256
    assert {factor: tuple(lines) for factor, lines in TEMPLATE.data["lines"].items()} == W.LEVELS
    assert (ATTRACTIVE, UNREMARKABLE) == ("You find them attractive.", "You do not find them especially attractive.")
    assert (ACQUAINTANCES, STRANGERS) == ("You know each other from your classes.", "You have never seen them before.")


def test_the_template_refuses_a_missing_level_or_factor():
    for broken in (
        {"perceived_attractiveness": {"attractive": "x"}, "familiarity": TEMPLATE.data["lines"]["familiarity"]},
        {"familiarity": TEMPLATE.data["lines"]["familiarity"]},
    ):
        with pytest.raises(ConfigError, match="pairwise template"):
            W.PairwiseTemplate(TEMPLATE.key, {**TEMPLATE.data, "lines": broken}, TEMPLATE.sha256)


def test_no_pairwise_line_names_a_convention_an_order_a_group_a_place_or_how_the_other_feels():
    for line in ALL_LINES:
        lowered = line.lower()
        for word in (*ORDER_WORDS, *SUGGESTIONS, *GROUP_WORDS, "left", "right", "keep", "side", "corridor", "passage", "queue", "train"):
            assert word.lower() not in lowered, (word, line)
        assert "they find" not in lowered and "they think" not in lowered and "you" in lowered


# --- the block (task 1) ----------------------------------------------------------------------------


def test_issue_61s_block_loads_as_written_with_the_rows_as_agents_0_and_1():
    mine = pairwise()
    assert mine.agents == (0, 1)
    assert mine.perceives(0, 1) == {W.ATTRACTIVENESS: "attractive", W.FAMILIARITY: "strangers"}
    assert mine.perceives(1, 0) == {W.ATTRACTIVENESS: "unremarkable", W.FAMILIARITY: "strangers"}
    assert mine.block() == {"agents": [0, 1], **ISSUE_BLOCK}
    assert W.PairwiseFactors.from_block(mine.block()).block() == mine.block()  # it reads back what it writes


def test_a_block_with_its_agents_names_which_agent_each_row_is():
    mine = pairwise({**ISSUE_BLOCK, "agents": [7, 3]})
    assert mine.perceives(7, 3)[W.ATTRACTIVENESS] == "attractive" and mine.perceives(3, 7)[W.ATTRACTIVENESS] == "unremarkable"
    assert mine.perceives(0, 1) == {W.ATTRACTIVENESS: None, W.FAMILIARITY: None}  # not in the block


@pytest.mark.parametrize("block, match", [
    ({"perceived_attractiveness": [["attractive", "attractive"], ["unremarkable", None]]}, "nobody is seen by themselves"),
    ({"agents": [0, 1], "perceived_attractiveness": [[None, "attractive"]]}, "matrix"),
    ({"perceived_attractiveness": [[None, "gorgeous"], [None, None]]}, "unremarkable"),
    ({"familiarity": "friends"}, "strangers"),
    ({"agents": [0, 0]}, "distinct"),
    ({"agents": [0, 1], "trust": "high"}, "unknown key"),
    ({"perceived_attractiveness": "attractive"}, "list of rows"),
])
def test_a_malformed_block_is_refused(block, match):
    with pytest.raises(ConfigError, match=match):
        W.PairwiseFactors.from_block(block)


# --- who is told what (task 2) ---------------------------------------------------------------------


def test_an_asymmetric_matrix_renders_each_observers_own_row_under_the_other_person():
    mine = pairwise()
    for observer, other, own, theirs in ((0, 1, ATTRACTIVE, UNREMARKABLE), (1, 0, UNREMARKABLE, ATTRACTIVE)):
        view = look([at(observer, 0.0, 0.0, vx=1.3), at(other, 3.0, 0.0, vx=-1.3)], perceiver(observer, other), pairwise_lines=mine.lines_for(observer))
        (person,) = view.seen
        assert person.pairwise_lines == (own, STRANGERS)
        seen = render(view, "talk", PASSING, V2).user.split("WHO YOU CAN SEE\n", 1)[1].split("\n\n", 1)[0].splitlines()
        assert seen[0].startswith("- Person 1,") and f"  {own}" in seen and f"  {STRANGERS}" in seen
        assert theirs not in "\n".join(seen)


def test_an_observer_is_told_nothing_of_itself_and_nobody_outside_the_block_gets_a_line():
    mine = pairwise()
    assert set(mine.lines_for(0)) == {1} and set(mine.lines_for(1)) == {0}
    assert mine.lines_for(5) == {}


@pytest.mark.parametrize("where, shown", [
    ((3.0, 0.0), True),     # in view, within 5 m: full detail
    ((3.0, 180.0), False),  # behind: not in view
    ((3.0, 80.0), False),   # beyond the 75° of the view cone
    ((8.0, 0.0), False),    # in view, beyond 5 m: one short line (D2), no extra lines
])
def test_a_pairwise_line_is_printed_only_for_a_person_in_view_in_full_detail(where, shown):
    distance, degrees = where
    view = look([at(0, 0.0, 0.0, vx=1.3), at(1, distance, degrees, vx=-1.3)], perceiver(), pairwise_lines=pairwise().lines_for(0))
    text = render(view, "talk", PASSING, V2).user
    assert (ATTRACTIVE in text) is shown and (STRANGERS in text) is shown


def test_a_person_who_is_only_heard_gets_no_pairwise_line():
    exchange = Exchange(SETTINGS)
    behind, observer = at(1, 1.5, 180.0, vx=1.3), at(0, 0.0, 0.0, vx=1.3)
    exchange.say(0.5, 1, "Excuse me.", [observer, behind])
    view = look([observer, behind], perceiver(), exchange=exchange, pairwise_lines=pairwise().lines_for(0))
    text = render(view, "talk", PASSING, V2).user
    assert view.seen == () and view.heard and "Excuse me." in text
    assert not any(line in text for line in ALL_LINES)


def told_in(record):
    """Everything each agent was told, joined: {agent: text}."""
    told = {}
    for point in record["decision_points"]:
        told[point["agent_id"]] = told.get(point["agent_id"], "") + point["prompt"]["messages"][1]["content"]
    return told


def test_neither_agent_is_ever_told_how_the_other_sees_them():
    """In the narrow passage both start within 5 m: each is told its own row and never the other's."""
    _, record, _ = session_on(PASSAGE, "talk", {0: SLOW, 1: SLOW}, pairwise=pairwise())
    told = told_in(record)
    assert set(told) == {0, 1}
    assert ATTRACTIVE in told[0] and UNREMARKABLE not in told[0]
    assert UNREMARKABLE in told[1] and ATTRACTIVE not in told[1]
    assert STRANGERS in told[0] and STRANGERS in told[1]  # familiarity is the same for both
    for point in record["decision_points"]:
        other = 1 - point["agent_id"]
        for person in point["view"]["seen"]:
            assert tuple(person["pairwise_lines"]) == pairwise().lines_for(point["agent_id"])[other]


def test_the_person_ahead_who_only_hears_the_one_behind_is_told_nothing_of_them():
    """Overtaking: the one behind (agent 0) closes in and says "Excuse me." twice; the second time
    the one ahead hears it and is prompted, but it cannot see behind, so it is told how it sees
    nobody."""
    ask = reply("Ask to get past.", [{"speed_mps": 1.8, "until": {"seconds": 3}}], message="Excuse me.")
    _, record, _ = session_on(OVERTAKING, "talk", {0: ask, 1: SLOW}, pairwise=pairwise())
    ahead = [point for point in record["decision_points"] if point["agent_id"] == 1]
    assert ahead and ahead[0]["trigger_reasons"] == ["trigger", "perceives:0"]
    for point in ahead:
        assert not point["view"]["seen"] and point["view"]["heard"]
        assert not any(line in point["prompt"]["messages"][1]["content"] for line in ALL_LINES)
    assert any(ATTRACTIVE in point["prompt"]["messages"][1]["content"] for point in record["decision_points"] if point["agent_id"] == 0)


# --- the switches (task 3) -------------------------------------------------------------------------


@pytest.mark.parametrize("attractiveness, familiarity", [("attractive", "acquaintances"), ("unremarkable", "strangers")])
def test_a_switch_on_shows_either_level_and_off_shows_neither(attractiveness, familiarity):
    block = {"perceived_attractiveness": [[None, attractiveness], [None, None]], "familiarity": familiarity}
    on = pairwise(block).lines_for(0)[1]
    assert on == (TEMPLATE.line(W.ATTRACTIVENESS, attractiveness), TEMPLATE.line(W.FAMILIARITY, familiarity))
    assert pairwise(block, {W.ATTRACTIVENESS: False}).lines_for(0)[1] == (TEMPLATE.line(W.FAMILIARITY, familiarity),)
    assert pairwise(block, {W.ATTRACTIVENESS: False, W.FAMILIARITY: False}).lines_for(0) == {}
    assert pairwise(block).lines_for(1) == {0: (TEMPLATE.line(W.FAMILIARITY, familiarity),)}  # row 1 was not designed


# --- the design (task 4) ---------------------------------------------------------------------------


def pairwise_config(name, ids=("passage_02fac1e4@1",), conditions=("independent",), factors_=None, **extra):
    raw_factors = {"age_pair": ["same"], "gender_pair": ["p1_female"], "task": ["none"], "demographics_visible": [True], "mapping": ["p1_lower"]}
    raw_factors.update(factors_ or {})
    return E.ResolutionConfig.from_raw({
        "layer": "resolution", "experiment_name": name, "cases": {"ids": list(ids)}, "conditions": list(conditions),
        "design": {"seed": 1, "factors": raw_factors}, "llm": {"client": "mock", "mock_policy": "resolution_rehearsal_v1"}, **extra,
    })


FULL = {
    "attractiveness_0_sees_1": ["unremarkable", "attractive"], "attractiveness_1_sees_0": ["unremarkable", "attractive"],
    "familiarity": ["strangers", "acquaintances"], "mapping": ["p1_lower", "p1_higher"],
}


def test_the_three_design_factors_each_have_two_levels_and_cross():
    config = pairwise_config("design", factors_=FULL)
    assert config.design.cells() == 16 and config.design.uses_pairwise and config.design.uses_attractiveness
    assert not config.design.uses_factors  # RF-5's factors are not varied: no factor template, no factor values
    assert config.templates == {"core": "resolve_v3", "debrief": "resolve_debrief_v1", "pairwise": "resolve_pairwise_v1"}
    assert config.factor_values is None
    for name in W.DESIGN_FACTORS:
        assert len(D.FACTOR_LEVELS[name]) == 2


def test_a_sessions_block_lists_person_1_first_and_attractiveness_0_sees_1_is_person_1_looking():
    for session in E.plan(pairwise_config("rows", factors_=FULL)).sessions:
        block = session.pairwise
        first = session.agents[0] if session.cell["mapping"] == "p1_lower" else session.agents[1]
        assert block["agents"][0] == first and session.person_of(block["agents"][1]) == 2
        mine = W.PairwiseFactors.from_block(block)
        assert mine.perceives(block["agents"][0], block["agents"][1])[W.ATTRACTIVENESS] == session.cell["attractiveness_0_sees_1"]
        assert mine.perceives(block["agents"][1], block["agents"][0])[W.ATTRACTIVENESS] == session.cell["attractiveness_1_sees_0"]
        assert block["familiarity"] == session.cell["familiarity"]
        assert session.as_dict()["pairwise"] == block
        assert session.visibility[W.ATTRACTIVENESS] is True and session.visibility[W.FAMILIARITY] is True


def test_a_design_may_set_one_direction_only_and_the_other_row_says_nothing():
    (session,) = E.plan(pairwise_config("one_way", factors_={"attractiveness_1_sees_0": ["attractive"]})).sessions
    assert session.pairwise == {"agents": [0, 1], "perceived_attractiveness": [[None, None], ["attractive", None]]}
    mine = W.PairwiseFactors.from_block(session.pairwise, TEMPLATE)
    assert mine.lines_for(0) == {} and mine.lines_for(1) == {0: (ATTRACTIVE,)}


def test_the_switches_are_design_factors_and_need_their_factor():
    config = pairwise_config("switched", factors_={"familiarity": ["acquaintances"], "familiarity_visible": [True, False]})
    for session in E.plan(config).sessions:
        assert session.visibility[W.FAMILIARITY] is session.cell["familiarity_visible"]
        assert W.ATTRACTIVENESS not in session.visibility
    with pytest.raises(ConfigError, match="switches perceived_attractiveness"):
        pairwise_config("bad", factors_={"familiarity": ["strangers"], "attractiveness_visible": [False]})
    with pytest.raises(ConfigError, match="templates.pairwise"):
        E.ResolutionConfig.from_raw({**json.loads(json.dumps(RAW)), "templates": {"pairwise": "resolve_pairwise_v1"}})
    with pytest.raises(ConfigError, match="unknown level"):
        pairwise_config("bad_level", factors_={"familiarity": ["friends"]})


# --- the outcome rows (task 5) ---------------------------------------------------------------------


def rows_of(folder):
    return [json.loads(line) for line in (folder / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()]


def test_the_outcome_row_holds_each_persons_own_view_as_0_or_1(tmp_path):
    factors_ = {"attractiveness_0_sees_1": ["attractive"], "attractiveness_1_sees_0": ["unremarkable"], "familiarity": ["acquaintances"],
                "mapping": ["p1_lower", "p1_higher"]}
    E.run_resolution(pairwise_config("numeric", factors_=factors_), out_root=tmp_path, report=quiet, git=GIT)
    rows = rows_of(tmp_path / "numeric")
    assert len(rows) == 2
    for row in rows:
        assert (row["p1_finds_other_attractive"], row["p2_finds_other_attractive"]) == (1, 0)
        assert (row["p1_knows_other"], row["p2_knows_other"]) == (1, 1)
        assert (row["attractiveness_0_sees_1"], row["attractiveness_1_sees_0"], row["familiarity"]) == ("attractive", "unremarkable", "acquaintances")
        assert row["p1_pairwise_lines_shown"] >= 1 and row["p2_pairwise_lines_shown"] >= 1  # the passage: within 5 m from the start
    record = json.loads(next((tmp_path / "numeric" / "sessions").glob("*.json")).read_text(encoding="utf-8"))
    assert record["pairwise"]["template"] == TEMPLATE.identity() and record["templates"]["pairwise"] == TEMPLATE.identity()
    assert record["pairwise"]["visible"] == {W.ATTRACTIVENESS: True, W.FAMILIARITY: True}
    assert "- Pairwise: " in (tmp_path / "numeric" / "sessions" / f"{record['session_id']}.md").read_text(encoding="utf-8")
    header = (tmp_path / "numeric" / "outcomes.csv").read_text(encoding="utf-8").splitlines()[0].split(",")
    assert {"p1_finds_other_attractive", "p2_knows_other", "p1_pairwise_lines_shown"} <= set(header)


def test_a_line_switched_off_is_still_logged_as_designed_but_never_shown(tmp_path):
    factors_ = {"attractiveness_0_sees_1": ["attractive"], "attractiveness_visible": [False]}
    E.run_resolution(pairwise_config("hidden", factors_=factors_), out_root=tmp_path, report=quiet, git=GIT)
    (row,) = rows_of(tmp_path / "hidden")
    assert (row["p1_finds_other_attractive"], row["p2_finds_other_attractive"], row["attractiveness_visible"]) == (1, None, False)
    assert row["p1_pairwise_lines_shown"] == 0 and "p1_knows_other" not in row


@pytest.mark.parametrize("core, shown", [("resolve_v3", True), ("resolve_v2", False)])
def test_in_the_head_on_case_the_lines_reach_both_agents_only_under_resolve_v3(tmp_path, core, shown):
    """In round 1's case every decision point is further than 5 m. resolve_v2 prints one short line
    per person there, so the designed perception never reached either agent (WORK_LOG-61.md);
    resolve_v3, the default for a design with factors, prints it under the short line."""
    factors_ = {"attractiveness_0_sees_1": ["attractive"], "familiarity": ["acquaintances"]}
    config = pairwise_config("far", ids=("head_on_02dfbadb@2",), conditions=("independent", "talk"), factors_=factors_,
                             **({} if core == "resolve_v3" else {"templates": {"core": core}}))
    assert config.templates["core"] == core
    E.run_resolution(config, out_root=tmp_path, report=quiet, git=GIT)
    for row in rows_of(tmp_path / "far"):
        assert row["outcome"] == "completed" and row["p1_finds_other_attractive"] == 1
        if shown:  # at every decision point of each, all of them on a short line
            assert row["p1_pairwise_lines_shown"] == row["p1_decision_points"] >= 1
            assert row["p2_pairwise_lines_shown"] == row["p2_decision_points"] >= 1
        else:
            assert row["p1_pairwise_lines_shown"] == row["p2_pairwise_lines_shown"] == 0
    record = json.loads(next((tmp_path / "far" / "sessions").glob("I_*.json")).read_text(encoding="utf-8"))
    for point in record["decision_points"]:
        assert all(person["detail"] == "short" for person in point["view"]["seen"])
        assert (ACQUAINTANCES in point["prompt"]["messages"][1]["content"]) is shown


def test_the_cost_preview_counts_the_pairwise_lines():
    plain = E.plan(pairwise_config("p0")).preview["per_session"][0]["S_decision_tokens"]
    counted = E.plan(pairwise_config("p1", factors_={"attractiveness_0_sees_1": ["attractive"], "familiarity": ["strangers"]})).preview
    assert counted["per_session"][0]["S_decision_tokens"] > plain


# --- the ethics gate (task 6) ----------------------------------------------------------------------


def test_the_repository_records_no_sign_off_for_attractiveness_yet():
    assert not E.attractiveness_signed_off()


def test_the_sign_off_is_one_exact_sentence(tmp_path):
    claude = tmp_path / "CLAUDE.md"
    assert not E.attractiveness_signed_off(claude)
    claude.write_text("Ethics sign-off for the perceived-attractiveness factor (issue #61): approved by the supervisor on YYYY-MM-DD\n", encoding="utf-8")
    assert not E.attractiveness_signed_off(claude)  # the form in the docs, not filled in
    claude.write_text("## Approvals\n- " + SIGN_OFF + ".\n", encoding="utf-8")
    assert E.attractiveness_signed_off(claude)
    assert not rg.ethnicity_signed_off(claude)  # one sign-off does not stand for the other


def test_a_paid_run_with_attractiveness_on_is_refused_until_the_sign_off_is_recorded(tmp_path, monkeypatch):
    paid_llm = {"client": "deepseek", "mock_policy": "resolution_rehearsal_v1"}
    budget = {"cap_usd": 100.0, "ledger": str(tmp_path / "ledger.jsonl")}
    raw = lambda name, factors_: {  # noqa: E731
        "layer": "resolution", "experiment_name": name, "cases": {"ids": ["passage_02fac1e4@1"]}, "conditions": ["independent"],
        "design": {"seed": 1, "factors": {**RAW["design"]["factors"], **factors_}}, "llm": paid_llm, "budget": budget,
    }
    paid = E.ResolutionConfig.from_raw(raw("rf6_paid", {"attractiveness_0_sees_1": ["attractive"], "attractiveness_visible": [False]}))
    monkeypatch.setattr(E, "SIGN_OFF_FILE", tmp_path / "missing.md")
    with pytest.raises(ConfigError, match="ethics sign-off for it is not recorded in CLAUDE.md"):
        E.run_resolution(paid, out_root=tmp_path, confirm=True, report=quiet, git=GIT)
    folder = tmp_path / "rf6_paid"
    assert not (folder / E.SESSIONS_DIR).exists() and not (tmp_path / "ledger.jsonl").exists()
    (line,) = (folder / E.INVOCATIONS_FILE).read_text(encoding="utf-8").splitlines()
    assert json.loads(line)["status"] == "refused_no_sign_off"
    # With the sentence recorded, the run goes on to the next check: confirmation.
    claude = tmp_path / "CLAUDE.md"
    claude.write_text(SIGN_OFF + "\n", encoding="utf-8")
    monkeypatch.setattr(E, "SIGN_OFF_FILE", claude)
    assert E.run_resolution(paid, out_root=tmp_path, report=quiet, git=GIT).status == "awaiting_confirmation"
    # Familiarity alone needs no sign-off, and the fictional group's sentence does not count.
    claude.write_text("Ethics sign-off for the fictional-group factor (issue #32): approved by the supervisor on 2026-11-02\n", encoding="utf-8")
    assert rg.ethnicity_signed_off(claude) and not E.attractiveness_signed_off(claude)
    with pytest.raises(ConfigError, match="ethics sign-off"):
        E.run_resolution(paid, out_root=tmp_path, report=quiet, git=GIT)
    familiar = E.ResolutionConfig.from_raw(raw("rf6_familiar", {"familiarity": ["acquaintances"]}))
    assert E.run_resolution(familiar, out_root=tmp_path, report=quiet, git=GIT).status == "awaiting_confirmation"


def test_a_mock_run_with_attractiveness_on_needs_no_sign_off(tmp_path, monkeypatch):
    monkeypatch.setattr(E, "SIGN_OFF_FILE", tmp_path / "missing.md")
    result = E.run_resolution(pairwise_config("mock_on", factors_={"attractiveness_0_sees_1": ["attractive"]}), out_root=tmp_path, report=quiet, git=GIT)
    assert result.status == "completed"


def test_the_plan_says_a_paid_run_would_be_refused():
    said = []
    E.print_plan(pairwise_config("said", factors_={"attractiveness_1_sees_0": ["unremarkable"]}), out=said.append)
    assert any("perceived attractiveness is on" in line for line in said)
    said.clear()
    E.print_plan(pairwise_config("unsaid", factors_={"familiarity": ["strangers"]}), out=said.append)
    assert not any("attractiveness" in line for line in said)


def test_the_two_gates_share_one_file_and_one_check():
    assert rg.SIGN_OFF_FILE == E.SIGN_OFF_FILE == ethics.SIGN_OFF_FILE
    assert rg.ETHNICITY_SIGN_OFF is ethics.ETHNICITY_SIGN_OFF


# --- the rule check (task 7) -----------------------------------------------------------------------


@pytest.mark.parametrize("reference", [
    "either.perceived_attractiveness", "pair.mutual_attraction", "agent.attractiveness", "both.finds_other_attractive",
    "either.Attractive", "either.good_looking", "pair.beauty_difference", "either.handsome", "agent.pretty",
])
def test_a_rule_reading_perceived_attractiveness_is_protected_whatever_the_prefix(reference):
    for prefixes in (CONDITION_PREFIXES, ROLE_PREFIXES):
        with pytest.raises(RuleError) as caught:
            resolve(reference, "where", prefixes)
        assert caught.value.category == "protected_attribute" and "perceived attractiveness" in str(caught.value), reference


def test_rule_generation_keeps_and_counts_such_a_rule_as_protected_attribute():
    for proposal in (
        rule(when=when({"field": "either.finds_other_attractive", "op": "==", "value": True})),
        rule(roles={"by": {"field": "agent.attractiveness", "order": "descending", "assign": ["a", "b"], "tie": "no_match"}},
             directive={"a": {"responsibility_share": 1.0}, "b": {"responsibility_share": 0.0}}),
        rule(roles={"by": {"field": "agent.speed_mps", "order": "descending", "assign": ["the_attractive_one", "b"], "tie": "no_match"}},
             directive={"the_attractive_one": {}, "b": {}}),
    ):
        result = validate_proposal(proposal, default_visibility())
        assert result.category == PROTECTED_ATTRIBUTE and "perceived attractiveness" in result.message, result.message
    with pytest.raises(RuleError, match="perceived attractiveness"):
        parse_rule({**rule(when=when({"field": "pair.attraction", "op": "==", "value": True})), "schema_version": 2, "rule_id": "probe",
                    "version": 1, "status": "test_seed", "provenance": {"source_type": "hand_written", "source_ref": "t", "created_at": "2026-10-23",
                                                                        "author": "t", "notes": "", "validation_evidence": []}},
                   load_validator(RULE_DB_ROOT))


def test_the_groups_refusal_reads_as_before_and_familiarity_is_not_protected():
    with pytest.raises(RuleError) as caught:
        resolve("either.ethnic_group", "where", CONDITION_PREFIXES)
    assert "refers to a person's group ('ethnic')" in str(caught.value)
    result = validate_proposal(rule(when=when({"field": "either.familiarity", "op": "==", "value": "acquaintances"})), default_visibility())
    assert result.category == SCHEMA_ERROR and result.loader_category == "unknown_field"


# --- resolve_v3 (the user's decision of 2026-10-23) ------------------------------------------------


def test_resolve_v3_is_resolve_v2_with_one_line_more():
    assert prompts.load_manifest()[FACTOR_CORE_TEMPLATE]["kind"] == "resolution"
    for condition in ("independent", "non_verbal", "talk"):
        assert V3.system(condition, PASSING) == V2.system(condition, PASSING)
    assert {k: v for k, v in V3.data["view"].items() if k != "seen_short_extra"} == V2.data["view"]
    assert V3.data["view"]["seen_short_extra"] == V2.data["view"]["seen_extra"] == "  {line}"
    for key in ("conditions", "step_format", "event_item", "decision_point", "role", "system"):
        assert V3.data[key] == V2.data[key]
    assert (V1.prints_extra_lines("short"), V2.prints_extra_lines("short"), V3.prints_extra_lines("short")) == (False, False, True)
    assert all(core.prints_extra_lines("full") for core in (V1, V2, V3))


@pytest.mark.parametrize("where", [(3.0, 0.0), (8.0, 0.0), (8.0, 40.0), (3.0, 180.0)])
def test_without_factor_lines_resolve_v3_renders_exactly_what_resolve_v2_does(where):
    distance, degrees = where
    bodies = [at(0, 0.0, 0.0, vx=1.3), at(1, distance, degrees, vx=-1.3)]
    two = render(look(bodies, perceiver(core=V2)), "talk", PASSING, V2).user
    three = render(look(bodies, perceiver(core=V3)), "talk", PASSING, V3).user
    assert two == three


@pytest.mark.parametrize("where, shown", [
    ((3.0, 0.0), True),     # within 5 m: full detail, as under resolve_v2
    ((8.0, 0.0), True),     # 5 to 10 m: under the short line
    ((9.9, 30.0), True),
    ((3.0, 180.0), False),  # behind: not in view
    ((3.0, 80.0), False),   # outside the view cone
    ((10.5, 0.0), False),   # beyond the seeing range
])
def test_resolve_v3_prints_the_factor_and_pairwise_lines_for_anyone_in_view(where, shown):
    distance, degrees = where
    for switch in (True, False):
        seen = F.SessionFactors(F.FactorTemplate.load(), {1: {"mobility_aid": "cane", "load": "large_suitcase"}}, {"load": switch}, {})
        view = look([at(0, 0.0, 0.0, vx=1.3), at(1, distance, degrees, vx=-1.3)], perceiver(core=V3),
                    factor_lines=seen.seen_lines(), pairwise_lines=pairwise().lines_for(0))
        text = render(view, "talk", PASSING, V3).user
        assert ("  They are walking with a cane." in text) is shown
        assert ("  They are pulling a large suitcase." in text) is (shown and switch)
        assert (f"  {ATTRACTIVE}" in text) is shown and (f"  {STRANGERS}" in text) is shown
        assert UNREMARKABLE not in text  # never the other's row
        if shown and distance > 5.0:
            seen_block = text.split("WHO YOU CAN SEE\n", 1)[1].split("\n\n", 1)[0].splitlines()
            assert ":" in seen_block[0] and "They look" not in text  # the short line: no age, gender or body width


# --- resolve_v4 (the user's decision of 2026-10-24, issue #64) ---------------------------------------


V4 = CoreTemplate.load("resolve_v4")
SHORT_DEMOGRAPHICS = ("seen_short_age", "seen_short_gender")


def test_resolve_v4_is_resolve_v3_with_two_lines_more():
    assert prompts.load_manifest()["resolve_v4"]["kind"] == "resolution"
    for condition in ("independent", "non_verbal", "talk"):
        assert V4.system(condition, PASSING) == V3.system(condition, PASSING)
    assert {k: v for k, v in V4.data["view"].items() if k not in SHORT_DEMOGRAPHICS} == V3.data["view"]
    assert (V4.data["view"]["seen_short_age"], V4.data["view"]["seen_short_gender"]) == (V3.data["view"]["seen_age"], V3.data["view"]["seen_gender"])
    for key in ("conditions", "step_format", "event_item", "decision_point", "role", "system"):
        assert V4.data[key] == V3.data[key]
    assert [core.prints_demographics("short") for core in (V1, V2, V3, V4)] == [False, False, False, True]
    assert all(core.prints_demographics("full") for core in (V1, V2, V3, V4))
    assert V4.prints_extra_lines("short")


@pytest.mark.parametrize("where, shown", [
    ((3.0, 0.0), True),     # within 5 m: full detail, as under resolve_v3
    ((8.0, 0.0), True),     # 5 to 10 m: under the short line
    ((9.9, 30.0), True),
    ((3.0, 180.0), False),  # behind: not in view
    ((10.5, 0.0), False),   # beyond the seeing range
])
def test_resolve_v4_prints_the_others_age_and_gender_for_anyone_in_view_when_visible(where, shown):
    distance, degrees = where
    bodies = [at(0, 0.0, 0.0, vx=1.3), at(1, distance, degrees, vx=-1.3)]
    text = render(look(bodies, perceiver(core=V4)), "talk", PASSING, V4).user
    assert ("  They look about 71 years old." in text) is shown and ("  They look like a man." in text) is shown
    if shown and distance > 5.0:
        seen_block = text.split("WHO YOU CAN SEE\n", 1)[1].split("\n\n", 1)[0].splitlines()
        assert ":" in seen_block[0] and seen_block[1:3] == ["  They look about 71 years old.", "  They look like a man."]
        assert "wide" not in "\n".join(seen_block)  # body width stays a full-detail line
        three = render(look(bodies, perceiver(core=V3)), "talk", PASSING, V3).user
        assert three == text.replace("\n  They look about 71 years old.\n  They look like a man.", "")
    for age, gender in ((False, True), (True, False), (False, False)):  # demographics_visible false, or one of them off
        hidden = render(look(bodies, perceiver(core=V4, show_age=age, show_gender=gender)), "talk", PASSING, V4).user
        assert ("years old" in hidden) is (shown and age) and ("They look like" in hidden) is (shown and gender)


def test_without_demographics_or_anyone_beyond_5_m_resolve_v4_renders_what_resolve_v3_does():
    for distance in (3.0, 8.0):
        bodies = [at(0, 0.0, 0.0, vx=1.3), at(1, distance, 0.0, vx=-1.3)]
        if distance < 5.0:
            assert render(look(bodies, perceiver(core=V4)), "talk", PASSING, V4).user == render(look(bodies, perceiver(core=V3)), "talk", PASSING, V3).user
        hidden = dict(show_age=False, show_gender=False)
        assert (render(look(bodies, perceiver(core=V4, **hidden)), "talk", PASSING, V4).user
                == render(look(bodies, perceiver(core=V3, **hidden)), "talk", PASSING, V3).user)


def test_the_default_core_template_is_resolve_v3_only_for_a_design_with_factors():
    assert (default_core(False), default_core(True)) == (SIMULATION_CORE_TEMPLATE, FACTOR_CORE_TEMPLATE) == ("resolve_v2", "resolve_v3")
    assert E.ResolutionConfig.from_raw(RAW).templates["core"] == "resolve_v2"
    assert pairwise_config("rf6", factors_={"familiarity": ["strangers"]}).templates["core"] == "resolve_v3"
    assert pairwise_config("rf5", factors_={"residence": ["p1"]}).templates["core"] == "resolve_v3"
    named = pairwise_config("named", factors_={"familiarity": ["strangers"]}, templates={"core": "resolve_v2"})
    assert named.templates["core"] == "resolve_v2"  # a config that names one keeps it
    for path, core in (("configs/resolution/resolve_mock_rehearsal.yaml", "resolve_v2"),
                       ("configs/resolution/resolve_factors_mock_rehearsal.yaml", "resolve_v2"),
                       ("configs/resolution/resolve_pairwise_mock_rehearsal.yaml", "resolve_v3")):
        assert E.ResolutionConfig.load(path).templates["core"] == core


def test_the_protocol_picks_the_same_default():
    run, _, _ = session_on(PASSAGE, "talk", {0: SLOW, 1: SLOW}, pairwise=pairwise())
    assert run.core.key == "resolve_v3"
    run, _, _ = session_on(PASSAGE, "talk", {0: SLOW, 1: SLOW})
    assert run.core.key == "resolve_v2"


def test_the_plan_warns_when_a_design_with_lines_for_others_keeps_resolve_v2():
    said = []
    E.print_plan(E.ResolutionConfig.load("configs/resolution/resolve_factors_mock_rehearsal.yaml"), out=said.append)
    assert any("core template resolve_v2" in line and "within 5 m" in line for line in said)
    for config in (pairwise_config("v3", factors_={"familiarity": ["strangers"]}), pairwise_config("own", factors_={"residence": ["p1"]}),
                   E.ResolutionConfig.from_raw(RAW)):
        said.clear()
        E.print_plan(config, out=said.append)
        assert not any("core template" in line for line in said)  # resolve_v3, or no line for others to be told


def test_a_design_with_no_errand_and_a_core_factor_runs(tmp_path):
    """Found by this issue (an RF-5 bug): with task "none" each person's urgency is None, which was
    passed on as a level, and every session refused."""
    config = pairwise_config("no_errand", factors_={"mobility_aid": ["p1"]})
    (session,) = E.plan(config).sessions
    assert session.personas[0]["urgency"] is None and all("urgency" not in levels for levels in session.factor_levels.values())
    assert E.run_resolution(config, out_root=tmp_path, report=quiet, git=GIT).status == "completed"


# --- what was written before (task 9) --------------------------------------------------------------


RAW = {
    "layer": "resolution", "experiment_name": "raw", "cases": {"ids": ["head_on_02dfbadb@2"]}, "conditions": ["talk"],
    "design": {"seed": 1, "factors": {"age_pair": ["same"], "gender_pair": ["p1_female"], "task": ["p1_urgent"], "demographics_visible": [True], "mapping": ["p1_lower"]}},
    "llm": {"client": "mock"},
}


@pytest.mark.parametrize("path", ["configs/resolution/resolve_mock_rehearsal.yaml", "configs/resolution/resolve_factors_mock_rehearsal.yaml"])
def test_configs_written_before_have_no_pairwise_block_anywhere(path):
    config = E.ResolutionConfig.load(path)
    assert not config.design.uses_pairwise and "pairwise" not in config.templates and config.pairwise_template() is None
    assert set(config.design.levels) <= set(D.FACTORS) | set(D.RF5_FACTORS)
    for session in E.plan(config).sessions:
        assert session.pairwise is None and "pairwise" not in session.as_dict()
        assert not set(session.visibility) & set(W.LEVELS)
        assert not set(session.cell) & set(D.PAIRWISE_FACTORS + D.PAIRWISE_SWITCH_FACTORS)


def test_a_session_without_pairwise_factors_records_and_renders_as_before():
    _, record, _ = session_on(PASSAGE, "talk", {0: SLOW, 1: SLOW})
    _, again, _ = session_on(PASSAGE, "talk", {0: SLOW, 1: SLOW}, pairwise=None)
    strip = lambda r: [(p["prompt"]["messages"], p["view"]) for p in r["decision_points"]]  # noqa: E731
    assert strip(record) == strip(again)
    for point in record["decision_points"]:
        assert all(not person["pairwise_lines"] for person in point["view"]["seen"])


def test_the_old_cell_codes_and_visibility_are_unchanged_by_the_new_factors():
    config = E.ResolutionConfig.from_raw(RAW)
    (session,) = E.plan(config).sessions
    assert session.visibility == visibility_of(session.cell) and not session.uses_pairwise
    assert session.session_id == "T_head_on_02dfbadb_" + D.cell_code({name: session.cell[name] for name in D.FACTORS}) + "_r1"
    assert "- Pairwise" not in transcript({
        "session_id": "x", "session": session.as_dict(), "case": {"case_id": "c", "version": 1}, "scenario": "passing", "condition": "talk",
        "llm": {"model": "m", "temperature": 1.0, "max_tokens": 400}, "outcome": "no_encounter",
    })
