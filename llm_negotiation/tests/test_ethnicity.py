"""Issue #92 (RF-26): real ethnicity as a factor, replacing the fictional group in track #55: the
shares as data, the draw, the frozen template ``resolve_factors_v2``, what each agent is told, the
design factors ``ethnicity_pair`` and ``ethnicity_visible``, the outcome rows, the ethics gate,
the rule check, ``--plan``, and that everything written before behaves as before
(``docs/ethnicity.md``)."""

from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import replace

import pytest

from negsim.avoidance.perception import default_visibility
from negsim.configutil import PACKAGE_ROOT, REPO_ROOT, ConfigError
from negsim.negotiation import prompts
from negsim.resolution import design as D
from negsim.resolution import ethnicity as Y
from negsim.resolution import experiment as E
from negsim.resolution import factors as F
from negsim.rulegen import experiment as rg
from negsim.rulegen.validate import PROTECTED_ATTRIBUTE, validate_proposal
from negsim.rules.database import RULE_DB_ROOT, load_validator
from negsim.rules.errors import RuleError
from negsim.rules.fields import CONDITION_PREFIXES, ROLE_PREFIXES, protected_reference, resolve
from negsim.rules.model import parse_rule
from test_encounter_protocol import GIT
from test_resolution import ORDER_WORDS, SUGGESTIONS
from test_rulegen_validate import rule, when

SHARES = Y.EthnicityShares.load()
V1, V2 = F.FactorTemplate.load("resolve_factors_v1"), F.FactorTemplate.load("resolve_factors_v2")
SIGN_OFF = "Ethics sign-off for the real-ethnicity factor (issue #92): approved by the supervisor on 2026-11-02"
OWN = {
    "chinese": "- You are Chinese.", "malay": "- You are Malay.", "indian": "- You are Indian.",
    "others": "- You are of another ethnicity, neither Chinese, Malay nor Indian.",
}
SEEN = {
    "chinese": "They look Chinese.", "malay": "They look Malay.", "indian": "They look Indian.",
    "others": "They look neither Chinese, Malay nor Indian.",
}
BASE = {"age_pair": ["same"], "gender_pair": ["p1_female"], "task": ["none"], "demographics_visible": [True], "mapping": ["p1_lower"]}


def quiet(_):
    pass


def config(name, factors_=None, ids=("passage_02fac1e4@1",), conditions=("independent",), design=None, **extra):
    raw = {
        "layer": "resolution", "experiment_name": name, "cases": {"ids": list(ids)}, "conditions": list(conditions),
        "design": {"seed": 1, "factors": {**BASE, **(factors_ or {})}, **(design or {})},
        "llm": {"client": "mock", "mock_policy": "resolution_rehearsal_v1"}, **extra,
    }
    return E.ResolutionConfig.from_raw(raw)


# --- the shares (task 1) ---------------------------------------------------------------------------


def test_the_shares_are_singstats_and_the_source_is_cached():
    assert dict(SHARES.shares) == {"chinese": 73.9, "malay": 13.5, "indian": 9.0, "others": 3.6}
    assert math.isclose(math.fsum(SHARES.shares.values()), 100.0)
    assert SHARES.source == "configs/resolution/ethnicity_sg_2026.yaml"
    cited = SHARES.cited
    assert cited["url"] == "https://www.singstat.gov.sg/publication-resources/population-trends-2026" and cited["read"] == "2026-10-24"
    cached = (REPO_ROOT / cited["cached"]).read_text(encoding="utf-8")
    assert " ".join(cited["sentence"].split()) in " ".join(cached.split())  # the source's own sentence, word for word
    assert "4.23 million" in cached and "6.21 million" in cached
    assert any("resident population only" in limit for limit in cited["limits"])
    assert any("visitor" in limit for limit in cited["limits"])  # the user's decision of 2026-10-24


def test_a_shares_file_that_is_malformed_is_refused():
    good = {"schema_version": 1, "groups": dict(SHARES.shares), "source": {k: SHARES.cited[k] for k in ("publisher", "title", "url", "read", "sentence")}, "limits": ["x"]}
    Y.EthnicityShares.from_mapping(good, "t")
    for broken in (
        {**good, "groups": {"malay": 13.5, "chinese": 73.9, "indian": 9.0, "others": 3.6}},  # out of order
        {**good, "groups": {"chinese": 80.0, "malay": 13.5, "indian": 9.0, "others": 3.6}},  # not 100
        {**good, "groups": {"chinese": 73.9, "malay": 13.5, "indian": 12.6}},  # a group missing
        {**good, "limits": []},  # the resident-only limit must be said
    ):
        with pytest.raises(ConfigError, match="ethnicity shares"):
            Y.EthnicityShares.from_mapping(broken, "t")


# --- the draw (task 2) -----------------------------------------------------------------------------


def test_same_is_one_group_and_different_is_two_with_person_1_drawn_the_same_way():
    for k in range(200):
        first, second = SHARES.draw("same", f"k{k}")
        assert first == second
        one, two = SHARES.draw("different", f"k{k}")
        assert one != two and one == first  # person 1 is the first draw of the stream at either level
    assert SHARES.draw("different", "x") == SHARES.draw("different", "x")  # the stream is the key's
    with pytest.raises(ConfigError, match="ethnicity_pair"):
        SHARES.draw("mixed", "x")


def test_the_draws_follow_the_shares():
    n = 20000
    firsts = Counter(SHARES.draw("same", f"s{k}")[0] for k in range(n))
    for group in Y.GROUPS:
        p = SHARES.shares[group] / 100
        assert abs(firsts[group] / n - p) < 4 * math.sqrt(p * (1 - p) / n), group
    # Person 2 of a "different" session: the other three groups at their shares renormalised.
    seconds = Counter(SHARES.draw("different", f"d{k}") for k in range(n))
    chinese_first = sum(count for (first, _), count in seconds.items() if first == "chinese")
    p_malay = 13.5 / (100 - 73.9)
    assert abs(seconds[("chinese", "malay")] / chinese_first - p_malay) < 4 * math.sqrt(p_malay * (1 - p_malay) / chinese_first)
    assert SHARES.probability("chinese", excluding="chinese") == 0.0
    assert math.isclose(sum(SHARES.probability(g, excluding="malay") for g in Y.GROUPS), 1.0)


def test_the_expected_pairs_add_up_and_say_how_few_the_smaller_groups_get():
    expected = SHARES.expected_pairs({"same": 100, "different": 100})
    assert math.isclose(sum(expected.values()), 200.0)
    assert math.isclose(expected[("others", "others")], 3.6) and math.isclose(expected[("chinese", "chinese")], 73.9)
    assert math.isclose(sum(v for (a, b), v in expected.items() if a != b), 100.0)  # the different sessions, all of them two groups
    shares = Y.person_shares(SHARES, {"same": 100, "different": 0})
    assert all(math.isclose(shares[g], SHARES.shares[g] / 100) for g in Y.GROUPS)  # all same: persons at the shares
    mixed = Y.person_shares(SHARES, {"same": 50, "different": 50})
    assert mixed["chinese"] < 0.739 and mixed["others"] > 0.036  # person 2 of a different session favours the smaller groups
    assert math.isclose(sum(mixed.values()), 1.0)


# --- the template (task 3) -------------------------------------------------------------------------


def test_resolve_factors_v2_is_frozen_and_is_v1_word_for_word_plus_the_ethnicity_lines():
    entry = prompts.load_manifest()["resolve_factors_v2"]
    assert entry["kind"] == F.KIND_FACTORS and entry["sha256"] == V2.sha256
    assert V2.data["attributes"] == V1.data["attributes"] and V2.data["situations"] == V1.data["situations"]
    assert not V1.has_ethnicity and V2.has_ethnicity
    assert {group: V2.ethnicity(group, "self") for group in Y.GROUPS} == OWN
    assert {group: V2.ethnicity(group, "other") for group in Y.GROUPS} == SEEN
    assert prompts.load_manifest()["resolve_factors_v1"]["sha256"] == V1.sha256  # v1 stays as it was


def test_no_ethnicity_line_names_a_convention_an_order_or_a_trait():
    for line in (*OWN.values(), *SEEN.values()):
        lowered = line.lower()
        for word in (*ORDER_WORDS, *SUGGESTIONS, "left", "right", "keep", "side", "polite", "rude", "usually", "tend"):
            assert word not in lowered, (line, word)


def test_the_template_refuses_a_malformed_ethnicity_block():
    for broken in (
        {group: V2.data["ethnicity"][group] for group in ("malay", "chinese", "indian", "others")},  # out of order
        {**V2.data["ethnicity"], "others": {"self": "- x"}},  # no other line
        {**V2.data["ethnicity"], "indian": {"self": "- x", "other": " "}},  # an empty line
    ):
        with pytest.raises(ConfigError, match="ethnicity"):
            F.FactorTemplate(V2.key, {**V2.data, "ethnicity": broken}, V2.sha256)
    with pytest.raises(ConfigError, match="no ethnicity lines"):
        V1.ethnicity("chinese", "self")


# --- what each agent is told (tasks 3 and 4) -------------------------------------------------------


def session_factors(visible=True, people=None, template=V2):
    return F.SessionFactors(template, people or {0: {"mobility_aid": "cane"}, 1: {"mobility_aid": "none"}}, {}, {},
                            ethnicity={0: "malay", 1: "others"}, ethnicity_visible=visible)


def test_ones_own_ethnicity_comes_first_in_about_you_and_is_always_told():
    for visible in (True, False):
        factors = session_factors(visible)
        assert factors.own(0) == (OWN["malay"], "- You are walking with a cane.")
        assert factors.own(1) == (OWN["others"],)


def test_the_others_ethnicity_is_told_under_them_only_when_visible():
    shown = session_factors(True)
    assert shown.seen(0) == (SEEN["malay"], "They are walking with a cane.") and shown.seen(1) == (SEEN["others"],)
    assert shown.seen_lines() == {0: (SEEN["malay"], "They are walking with a cane."), 1: (SEEN["others"],)}
    hidden = session_factors(False)
    assert hidden.seen(0) == ("They are walking with a cane.",) and hidden.seen(1) == ()
    assert hidden.seen_lines() == {0: ("They are walking with a cane.",)}
    # Someone with a group and no core factor still gets their line.
    alone = F.SessionFactors(V2, {}, {}, {}, ethnicity={3: "indian"})
    assert alone.seen_lines() == {3: (SEEN["indian"],)} and alone.own(3) == (OWN["indian"],)


def test_a_session_record_says_both_groups_and_the_switch_and_an_old_one_does_not():
    record = session_factors(False).as_dict()
    assert record["ethnicity"] == {"0": "malay", "1": "others"} and record["ethnicity_visible"] is False
    plain = F.SessionFactors(V1, {0: {"mobility_aid": "cane"}}, {}, {}).as_dict()
    assert set(plain) == {"template", "people", "visible", "situation"}


def test_groups_need_a_template_with_their_lines_and_must_be_known():
    with pytest.raises(ConfigError, match="no ethnicity lines"):
        session_factors(template=V1)
    with pytest.raises(ConfigError, match="ethnicity is one of"):
        F.SessionFactors(V2, {}, {}, {}, ethnicity={0: "kestrop"})


# --- the design (tasks 2 and 4) --------------------------------------------------------------------


def test_the_design_draws_each_sessions_groups_at_its_level():
    c = config("draw", {"ethnicity_pair": ["same", "different"], "ethnicity_visible": [True, False]}, conditions=("independent", "talk"))
    assert c.design.uses_ethnicity and c.design.uses_factors and c.templates["factors"] == "resolve_factors_v2"
    sessions = E.plan(c).sessions
    assert len(sessions) == 8
    for session in sessions:
        first, second = session.persons
        groups = session.ethnicity
        assert set(groups) == set(session.agents) and session.personas[first]["ethnicity"] == groups[first]
        assert (groups[first] == groups[second]) == (session.cell["ethnicity_pair"] == "same")
        assert session.visibility["ethnicity"] == session.cell["ethnicity_visible"]
        assert session.as_dict()["personas"][str(first)]["ethnicity"] == groups[first]
    # The same cell on the same case is the same two people under every condition (A1).
    by_cell = {}
    for session in sessions:
        by_cell.setdefault(D.cell_code(session.cell), set()).add(tuple(sorted(session.ethnicity.items())))
    assert all(len(draws) == 1 for draws in by_cell.values())
    assert c.design.as_dict()["ethnicity_shares"] == {"source": "configs/resolution/ethnicity_sg_2026.yaml", "shares": dict(SHARES.shares)}


def test_an_exact_repeat_is_the_same_two_people():
    c = config("repeats", {"ethnicity_pair": ["same", "different"], "age_pair": ["same", "p1_older"]}, design={"exact_repeats": {"cells": 2, "times": 3}})
    repeats: dict = {}
    for session in E.plan(c).sessions:
        repeats.setdefault(D.cell_code(session.cell), set()).add(tuple(sorted(session.ethnicity.items())))
    assert all(len(draws) == 1 for draws in repeats.values())


def test_a_counterfactual_pair_keeps_person_1s_group_and_flips_only_what_it_names():
    base = {"age_pair": "same", "ethnicity_pair": "same", "mapping": "p1_lower"}
    c = config("pairs", {"ethnicity_pair": ["same", "different"], "age_pair": ["same", "p1_older"]}, design={"counterfactual_pairs": [
        {"base": base, "factor": "ethnicity_pair"}, {"base": base, "factor": "age_pair", "to": "p1_older"},
    ]})
    pairs: dict = {}
    for session in E.plan(c).sessions:
        if session.pair_id is not None:
            first, second = session.persons
            pairs.setdefault(session.pair_id, {})[session.pair_role] = (session.pair_factor, session.ethnicity[first], session.ethnicity[second])
    assert len(pairs) == 2
    for roles in pairs.values():
        (factor, b1, b2), (_, f1, f2) = roles["base"], roles["flipped"]
        assert b1 == b2 == f1  # person 1 keeps its group
        assert (f2 != b2) if factor == "ethnicity_pair" else (f2 == b2)


def test_the_switch_and_the_shares_need_the_pair_and_the_template_needs_its_lines():
    with pytest.raises(ConfigError, match="ethnicity_visible: switches real ethnicity"):
        config("switch", {"ethnicity_visible": [True]})
    with pytest.raises(ConfigError, match="ethnicity_shares"):
        config("shares", {"mobility_aid": ["p1"]}, design={"ethnicity_shares": "configs/resolution/ethnicity_sg_2026.yaml"})
    with pytest.raises(ConfigError, match="no ethnicity lines"):
        config("v1", {"ethnicity_pair": ["same"]}, templates={"factors": "resolve_factors_v1"})
    with pytest.raises(ConfigError, match="unknown level"):
        config("level", {"ethnicity_pair": ["mixed"]})


def test_a_fractional_design_holds_the_pair_and_its_switch_as_columns():
    c = E.ResolutionConfig.load("configs/resolution/resolve_ethnicity_mock_rehearsal.yaml")
    assert c.design.kind == "fractional" and {"ethnicity_pair", "ethnicity_visible"} <= set(c.design.screened)
    cells = c.design.cell_list()
    for name in ("ethnicity_pair", "ethnicity_visible"):
        assert Counter(cell[name] for cell in cells) == Counter({level: len(cells) // 2 for level in D.FACTOR_LEVELS[name]})


# --- the outcome rows (task 5) ---------------------------------------------------------------------


@pytest.mark.parametrize("visible", [True, False])
def test_the_outcome_row_has_both_groups_the_pair_and_how_often_each_was_told(tmp_path, visible):
    c = config("row", {"ethnicity_pair": ["different"], "ethnicity_visible": [visible], "mobility_aid": ["p1"]}, ids=("passage_02fac1e4@1", "head_on_02dfbadb@2"))
    c = replace(c, templates={**c.templates, "core": "resolve_v5"})
    E.run_resolution(c, out_root=tmp_path, report=quiet, git=GIT)
    for line in (tmp_path / "row" / "outcomes.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        record = json.loads((tmp_path / "row" / "sessions" / f"{row['session_id']}.json").read_text(encoding="utf-8"))
        groups = record["factors"]["ethnicity"]
        assert (row["p1_ethnicity"], row["p2_ethnicity"]) == (groups[str(row["p1_agent"])], groups[str(row["p2_agent"])])
        assert row["p1_ethnicity"] != row["p2_ethnicity"] and row["ethnicity_pair"] == "different" and row["ethnicity_visible"] is visible
        for me, other in (("p1", "p2"), ("p2", "p1")):
            told = 0
            for point in record["decision_points"]:
                if point["agent_id"] != row[f"{me}_agent"]:
                    continue
                text = point["prompt"]["messages"][1]["content"]
                assert OWN[row[f"{me}_ethnicity"]] in text  # one's own, always
                told += SEEN[row[f"{other}_ethnicity"]] in text
                assert visible or not any(line_ in text for line_ in SEEN.values())
            assert row[f"{me}_other_ethnicity_shown"] == told
            if visible:
                assert told == row[f"{me}_other_observable_shown"] >= 1  # printed where the observable lines are


def test_a_design_without_ethnicity_has_no_ethnicity_columns(tmp_path):
    E.run_resolution(config("plain", {"mobility_aid": ["p1"]}), out_root=tmp_path, report=quiet, git=GIT)
    row = json.loads((tmp_path / "plain" / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert not [key for key in row if "ethnic" in key]


# --- the ethics gate (task 6) ----------------------------------------------------------------------


def test_the_repository_records_the_supervisors_sign_off_for_real_ethnicity():
    """Recorded by the user in CLAUDE.md on 2026-10-24 (PR #93), before this issue was built: so
    the issue's "the repository records no sign-off" no longer holds (WORK_LOG-92.md)."""
    assert E.ethnicity_signed_off()
    assert not rg.ethnicity_signed_off()  # the fictional group's own sentence is not there


def test_the_sign_off_is_one_exact_sentence_and_stands_for_no_other(tmp_path):
    claude = tmp_path / "CLAUDE.md"
    assert not E.ethnicity_signed_off(claude)
    claude.write_text("Ethics sign-off for the real-ethnicity factor (issue #92): approved by the supervisor on YYYY-MM-DD\n", encoding="utf-8")
    assert not E.ethnicity_signed_off(claude)  # the form in the issue, not filled in
    claude.write_text("Ethics sign-off for the fictional-group factor (issue #32): approved by the supervisor on 2026-11-02\n"
                      "Ethics sign-off for the perceived-attractiveness factor (issue #61): approved by the supervisor on 2026-11-02\n", encoding="utf-8")
    assert not E.ethnicity_signed_off(claude)  # neither of the others counts
    claude.write_text("## Approvals\n- " + SIGN_OFF + ".\n", encoding="utf-8")
    assert E.ethnicity_signed_off(claude) and not E.attractiveness_signed_off(claude) and not rg.ethnicity_signed_off(claude)


def test_a_paid_run_with_ethnicity_on_is_refused_until_the_sign_off_is_recorded(tmp_path, monkeypatch):
    budget = {"cap_usd": 100.0, "ledger": str(tmp_path / "ledger.jsonl")}
    raw = lambda name, factors_: {  # noqa: E731
        "layer": "resolution", "experiment_name": name, "cases": {"ids": ["passage_02fac1e4@1"]}, "conditions": ["independent"],
        "design": {"seed": 1, "factors": {**BASE, **factors_}}, "llm": {"client": "deepseek"}, "budget": budget,
    }
    paid = E.ResolutionConfig.from_raw(raw("rf26_paid", {"ethnicity_pair": ["same"], "ethnicity_visible": [False]}))
    monkeypatch.setattr(E, "SIGN_OFF_FILE", tmp_path / "missing.md")
    with pytest.raises(ConfigError, match="varies real ethnicity.*not recorded in CLAUDE.md"):
        E.run_resolution(paid, out_root=tmp_path, confirm=True, report=quiet, git=GIT)
    folder = tmp_path / "rf26_paid"
    assert not (folder / E.SESSIONS_DIR).exists() and not (tmp_path / "ledger.jsonl").exists()
    (line,) = (folder / E.INVOCATIONS_FILE).read_text(encoding="utf-8").splitlines()
    assert json.loads(line)["status"] == "refused_no_sign_off"
    claude = tmp_path / "CLAUDE.md"
    claude.write_text("Ethics sign-off for the perceived-attractiveness factor (issue #61): approved by the supervisor on 2026-11-02\n", encoding="utf-8")
    monkeypatch.setattr(E, "SIGN_OFF_FILE", claude)
    with pytest.raises(ConfigError, match="real ethnicity"):  # another factor's sentence does not count
        E.run_resolution(paid, out_root=tmp_path, report=quiet, git=GIT)
    claude.write_text(SIGN_OFF + "\n", encoding="utf-8")
    assert E.run_resolution(paid, out_root=tmp_path, report=quiet, git=GIT).status == "awaiting_confirmation"  # on to the next check
    plain = E.ResolutionConfig.from_raw(raw("rf26_plain", {"mobility_aid": ["p1"]}))
    monkeypatch.setattr(E, "SIGN_OFF_FILE", tmp_path / "missing.md")
    assert E.run_resolution(plain, out_root=tmp_path, report=quiet, git=GIT).status == "awaiting_confirmation"  # no ethnicity, no gate


def test_a_mock_run_with_ethnicity_on_needs_no_sign_off(tmp_path, monkeypatch):
    monkeypatch.setattr(E, "SIGN_OFF_FILE", tmp_path / "missing.md")
    assert E.run_resolution(config("mock_on", {"ethnicity_pair": ["different"]}), out_root=tmp_path, report=quiet, git=GIT).status == "completed"


# --- no rule may read it (task 7) ------------------------------------------------------------------


@pytest.mark.parametrize("reference", [
    "either.ethnicity", "pair.same_ethnicity", "pair.ethnicity_pair", "agent.p1_ethnicity", "both.ethnicity_visible",
    "either.chinese", "agent.Malay", "pair.both_indian", "either.race", "pair.same_race", "agent.racial_group", "pair.Indians",
])
def test_a_rule_reading_ethnicity_is_protected_whatever_the_prefix(reference):
    for prefixes in (CONDITION_PREFIXES, ROLE_PREFIXES):
        with pytest.raises(RuleError) as caught:
            resolve(reference, "where", prefixes)
        assert caught.value.category == "protected_attribute", reference


def test_a_group_name_is_reported_as_a_persons_ethnicity_and_others_alone_is_an_ordinary_word():
    with pytest.raises(RuleError, match=r"refers to a person's ethnicity \('malay'\)"):
        resolve("either.malay", "where", CONDITION_PREFIXES)
    with pytest.raises(RuleError, match=r"refers to a person's group \('ethnic'\)"):  # issue #32's wording, as before
        resolve("either.ethnicity", "where", CONDITION_PREFIXES)
    for ordinary in ("either.others", "pair.distance_m", "agent.speed_mps", "trace", "embrace", "terrace"):
        assert protected_reference(ordinary) is None, ordinary


def test_every_path_of_a_rule_keeps_and_counts_ethnicity_as_protected_attribute():
    for proposal in (
        rule(when=when({"field": "either.ethnicity", "op": "==", "value": "malay"})),
        rule(when=when({"field": "pair.distance_m", "op": "<", "value": 3, "unit": "m"}, {"field": "pair.same_race", "op": "==", "value": True})),
        rule(roles={"by": {"field": "agent.ethnicity", "order": "ascending", "assign": ["a", "b"], "tie": "no_match"}},
             directive={"a": {"responsibility_share": 1.0}, "b": {"responsibility_share": 0.0}}),
        rule(roles={"by": {"field": "agent.age", "order": "ascending", "assign": ["a", "b"], "tie": "agent.ethnicity_pair"}},
             directive={"a": {}, "b": {}}),  # the tie policy
        rule(roles={"by": {"field": "agent.age", "order": "ascending", "assign": ["a", "b"], "tie": "no_match", "tie_within": "same race"}},
             directive={"a": {}, "b": {}}),
        rule(roles={"by": {"field": "agent.speed_mps", "order": "descending", "assign": ["the_chinese_one", "b"], "tie": "no_match"}},
             directive={"the_chinese_one": {}, "b": {}}),  # a role name
        rule(when=when({"field": "either.gender", "op": "==", "value": "Indian"})),  # a value
    ):
        result = validate_proposal(proposal, default_visibility())
        assert result.category == PROTECTED_ATTRIBUTE, result.message
    seeded = {"schema_version": 2, "rule_id": "probe", "version": 1, "status": "test_seed",
              "provenance": {"source_type": "hand_written", "source_ref": "t", "created_at": "2026-10-24", "author": "t", "notes": "", "validation_evidence": []}}
    with pytest.raises(RuleError, match="protected_attribute|ethnicity"):
        parse_rule({**rule(when=when({"field": "either.malay", "op": "==", "value": True})), **seeded}, load_validator(RULE_DB_ROOT))


# --- --plan (task 9) -------------------------------------------------------------------------------


def test_the_plan_prints_the_sessions_per_pair_of_groups_and_the_gate(tmp_path, monkeypatch):
    said: list[str] = []
    c = E.ResolutionConfig.load("configs/resolution/resolve_ethnicity_mock_rehearsal.yaml")
    plan_ = E.print_plan(c, out=said.append)
    text = "\n".join(said)
    assert "shares of residents only" in text and "draw balanced" in text and "persons weighted:" in text
    drawn = Counter(tuple(s.personas[a]["ethnicity"] for a in s.persons) for s in plan_.sessions)
    for (first, second), count in drawn.items():
        assert f"{first} / {second}: drawn {count} (expected" in text
    # Weighted, the persons are at the resident shares exactly (every pair of groups is drawn).
    assert "chinese 73.9% (residents 73.9%)" in text and "others 3.6% (residents 3.6%)" in text and "never drawn" not in text
    assert "real ethnicity is on" not in text  # the repository records the sign-off
    monkeypatch.setattr(E, "SIGN_OFF_FILE", tmp_path / "missing.md")
    said.clear()
    E.print_plan(c, out=said.append)
    assert any("real ethnicity is on: a paid run is refused" in line for line in said)
    said.clear()
    E.print_plan(config("none", {"mobility_aid": ["p1"]}), out=said.append)
    assert not any("ethnicity" in line for line in said)


def test_the_cost_preview_counts_the_ethnicity_lines():
    plain = E.plan(config("p0", {"mobility_aid": ["p1"]})).preview["per_session"][0]["S_decision_tokens"]
    on = E.plan(config("p1", {"mobility_aid": ["p1"], "ethnicity_pair": ["same"]})).preview["per_session"][0]["S_decision_tokens"]
    assert on > plain


# --- what was written before (task 8 and the acceptance criteria) ----------------------------------


@pytest.mark.parametrize("path", sorted(str(p.relative_to(PACKAGE_ROOT)).replace("\\", "/") for p in (PACKAGE_ROOT / "configs" / "resolution").glob("*.yaml")))
def test_configs_written_before_have_no_ethnicity_anywhere(path):
    if path.endswith(("ethnicity_sg_2026.yaml", "resolve_ethnicity_mock_rehearsal.yaml", "llm_view_v1.yaml", "factors_v1.yaml",
                      "round1_head_on_screening.yaml",  # issue #65: RF-10's screen, written after #92, varies ethnicity
                      "round1_head_on_v7.yaml",  # issue #98: RF-27, RF-10's independent sessions under resolve_v7
                      "round1_head_on_v4pro.yaml",  # issue #100: RF-28, the same sessions on deepseek-v4-pro
                      "round1_head_on_v4pro_cap600.yaml",  # issue #100: the same, reply cap 600 (the run of record)
                      "round1_head_on_sidestep.yaml",  # issue #101: RF-29, the same sessions under resolve_v8
                      "round1_head_on_keep_line.yaml")):  # issue #104: RF-30, RF-10's non-verbal and talk under keep_line
        pytest.skip("not an experiment config written before issue #92")
    c = E.ResolutionConfig.load(path)
    assert not c.design.uses_ethnicity and c.design.ethnicity_shares is None and "ethnicity_shares" not in c.design.as_dict()
    # Issue #110: RF-32's configs name RF-30's factor template (resolve_factors_v1 word for word plus the
    # ethnicity lines, which a design that does not vary ethnicity never renders), and vary no ethnicity.
    rf32 = path.endswith(("round1_group_head_on.yaml", "round1_group_head_on_orca_groups.yaml"))
    assert c.templates.get("factors") in ((None, "resolve_factors_v1", "resolve_factors_v2") if rf32 else (None, "resolve_factors_v1"))
    for session in E.plan(c).sessions:
        assert not session.ethnicity and "ethnicity" not in session.visibility
        assert all("ethnicity" not in persona for persona in session.personas.values())


def test_the_old_factor_template_and_the_fictional_groups_layer_are_unchanged():
    # resolve_factors_v1's hash as the manifest pinned it before this issue (commit 03f1f86).
    assert prompts.load_manifest()["resolve_factors_v1"]["sha256"] == "bb3351d414f9c0c2d634348dfd19a868ab63e7afb70e14f93b1bfc5eca87865b"
    assert F.FACTOR_TEMPLATE == "resolve_factors_v1" and F.default_factor_template(False) == "resolve_factors_v1"
    assert F.default_factor_template(True) == "resolve_factors_v2"
    from negsim.personas.groups import DEFAULT_GROUP_LABELS
    assert DEFAULT_GROUP_LABELS == ("Kestrop", "Dremmik", "Pellund")


# --- the balanced draw and the weights (the user's decision of 2026-10-24, open question 3) --------


def test_the_balanced_rotation_gives_every_group_and_every_ordered_pair_equally_often():
    units = {("c", f"s{k}"): frozenset({"same"}) for k in range(16)}
    units.update({("c", f"d{k}"): frozenset({"different"}) for k in range(24)})
    units.update({("c", f"x{k}"): frozenset({"same", "different"}) for k in range(12)})
    found = Y.balanced_assignment(units, seed=5)
    same = Counter(found[("c", f"s{k}")]["same"] for k in range(16))
    assert same == Counter({(g, g): 4 for g in Y.GROUPS})
    different = Counter(found[("c", f"d{k}")]["different"] for k in range(24))
    assert different == Counter({pair: 2 for pair in Y.DIFFERENT_PAIRS}) and len(Y.DIFFERENT_PAIRS) == 12
    for k in range(12):  # a pair that flips ethnicity_pair keeps person 1
        both = found[("c", f"x{k}")]
        assert both["same"] == (both["different"][0],) * 2 and both["different"][0] != both["different"][1]
    # Any whole block of four different pairs balances person 1 and person 2.
    for block in range(3):
        four = Y.DIFFERENT_PAIRS[4 * block: 4 * block + 4]
        assert sorted(a for a, _ in four) == sorted(Y.GROUPS) == sorted(b for _, b in four)
    assert Y.balanced_assignment(units, seed=5) == found and Y.balanced_assignment(units, seed=6) != found


def test_a_balanced_design_balances_each_level_and_keeps_the_people_across_conditions():
    c = config("bal", {"ethnicity_pair": ["same", "different"], "age_pair": ["same", "p1_older"], "gender_pair": ["p1_female", "p1_male"],
                       "mapping": ["p1_lower", "p1_higher"]}, conditions=("independent", "talk"), design={"ethnicity_draw": "balanced"})
    assert c.design.ethnicity_draw == "balanced" and c.design.as_dict()["ethnicity_draw"] == "balanced"
    sessions = E.plan(c).sessions
    for level, groups in (("same", 4), ("different", 4)):
        firsts = Counter(s.ethnicity[s.persons[0]] for s in sessions if s.cell["ethnicity_pair"] == level)
        assert set(firsts) == set(Y.GROUPS) and len(set(firsts.values())) == 1, (level, firsts)  # 8 cells x 2 conditions: 4 each
    people = {}
    for s in sessions:
        people.setdefault(D.cell_code(s.cell), set()).add(tuple(sorted(s.ethnicity.items())))
    assert all(len(draws) == 1 for draws in people.values())


def test_the_weights_make_the_sessions_stand_for_random_resident_pairs():
    pairs = [(a, b) for a in Y.GROUPS for b in Y.GROUPS] * 3 + [("chinese", "malay")] * 5  # every pair, one over-drawn
    w = Y.weights(SHARES, pairs)
    assert math.isclose(sum(w), len(pairs), rel_tol=1e-5)
    persons = Counter()
    for (a, b), weight_ in zip(pairs, w):
        persons[a] += weight_
        persons[b] += weight_
    for g in Y.GROUPS:
        assert math.isclose(persons[g] / (2 * sum(w)), SHARES.shares[g] / 100, rel_tol=1e-5)
    same = sum(weight_ for (a, b), weight_ in zip(pairs, w) if a == b) / sum(w)
    assert math.isclose(same, sum((s / 100) ** 2 for s in SHARES.shares.values()), rel_tol=1e-5)  # 57.4%
    assert math.isclose(same, 0.574, abs_tol=0.0005)
    assert Y.missing_pairs(pairs) == [] and ("others", "others") in Y.missing_pairs([("chinese", "chinese")])


@pytest.mark.parametrize("draw", ["real", "balanced"])
def test_every_session_of_an_ethnicity_design_carries_its_weight_into_the_record_and_the_row(tmp_path, draw):
    c = config(f"w_{draw}", {"ethnicity_pair": ["same", "different"]}, design={"ethnicity_draw": draw})
    sessions = E.plan(c).sessions
    assert all(s.ethnicity_weight is not None and s.as_dict()["ethnicity_weight"] == s.ethnicity_weight for s in sessions)
    assert math.isclose(sum(s.ethnicity_weight for s in sessions), len(sessions), rel_tol=1e-4) or Y.missing_pairs(
        [tuple(s.ethnicity[a] for a in s.persons) for s in sessions])  # unless a pair was never drawn
    E.run_resolution(c, out_root=tmp_path, report=quiet, git=GIT)
    by_id = {s.session_id: s for s in sessions}
    for line in (tmp_path / f"w_{draw}" / "outcomes.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        assert row["ethnicity_weight"] == by_id[row["session_id"]].ethnicity_weight
    plain = E.plan(config("plain_w", {"mobility_aid": ["p1"]})).sessions
    assert all(s.ethnicity_weight is None and "ethnicity_weight" not in s.as_dict() for s in plain)


def test_the_draw_must_be_known_and_needs_the_pair_and_real_is_the_default():
    with pytest.raises(ConfigError, match="ethnicity_draw: one of"):
        config("bad", {"ethnicity_pair": ["same"]}, design={"ethnicity_draw": "equal"})
    with pytest.raises(ConfigError, match="ethnicity_draw: for a design that varies ethnicity_pair"):
        config("nopair", {"mobility_aid": ["p1"]}, design={"ethnicity_draw": "balanced"})
    real = config("default", {"ethnicity_pair": ["same", "different"]})
    assert real.design.ethnicity_draw == "real" and "ethnicity_draw" not in real.design.as_dict()
    # The real draw is unchanged by the balanced option: the same stream as before.
    for s in E.plan(real).sessions:
        unit = (s.case_id, D.cell_code(s.cell))
        assert tuple(s.ethnicity[a] for a in s.persons) == SHARES.draw(s.cell["ethnicity_pair"], f"{real.design.seed}:{unit[0]}:{unit[1]}")


# --- counterfactual pairs that flip one person's group (the user's request, 2026-10-24) ------------


FLIP_BASE = {"age_pair": "same", "ethnicity_pair": "different", "mapping": "p1_lower"}


def flip_config(name, pairs, factors_=None, **kwargs):
    return config(name, {"ethnicity_pair": ["same", "different"], "age_pair": ["same", "p1_older"], **(factors_ or {})},
                  design={"counterfactual_pairs": pairs, **kwargs.pop("design", {})}, **kwargs)


def test_a_group_flip_fixes_both_groups_and_changes_only_the_flipped_persons():
    c = flip_config("flip", [
        {"base": FLIP_BASE, "factor": "p2_ethnicity", "ethnicity": {"p1": "chinese", "p2": "malay"}, "to": "indian"},
        {"base": {**FLIP_BASE, "ethnicity_pair": "same"}, "factor": "p2_ethnicity", "ethnicity": {"p1": "chinese", "p2": "chinese"}, "to": "indian"},
        {"base": FLIP_BASE, "factor": "p1_ethnicity", "ethnicity": {"p1": "others", "p2": "malay"}, "to": "malay"},
    ], conditions=("independent", "talk"))
    found: dict = {}
    for s in E.plan(c).sessions:
        if s.pair_change is None:
            continue
        found.setdefault((s.condition, s.pair_change, s.pair_factor), {})[s.pair_role] = (s.cell, tuple(s.ethnicity[a] for a in s.persons), s.session_id)
    assert len(found) == 6  # three pairs, two conditions
    for (condition, change, factor), roles in found.items():
        (base_cell, base_groups, base_id), (flip_cell, flip_groups, flip_id) = roles["base"], roles["flipped"]
        assert base_id.endswith("_base") and flip_id.endswith("_flipped") and base_id != flip_id
        assert {k: v for k, v in base_cell.items() if k != "ethnicity_pair"} == {k: v for k, v in flip_cell.items() if k != "ethnicity_pair"}
        for cell, groups in ((base_cell, base_groups), (flip_cell, flip_groups)):
            assert cell["ethnicity_pair"] == ("same" if groups[0] == groups[1] else "different")  # follows from the groups
        kept, moved = (0, 1) if factor == "p2_ethnicity" else (1, 0)
        assert base_groups[kept] == flip_groups[kept] and f"{base_groups[moved]}->{flip_groups[moved]}" == change
    assert {key[1] for key in found} == {"malay->indian", "chinese->indian", "others->malay"}


def test_a_group_flip_is_told_in_the_prompts_and_recorded_in_the_rows(tmp_path):
    c = flip_config("flip_run", [{"base": FLIP_BASE, "factor": "p2_ethnicity", "ethnicity": {"p1": "chinese", "p2": "malay"}, "to": "indian"}])
    E.run_resolution(c, out_root=tmp_path, report=quiet, git=GIT)
    rows = [json.loads(line) for line in (tmp_path / "flip_run" / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()]
    pair = {row["pair_role"]: row for row in rows if row.get("pair_change")}
    assert set(pair) == {"base", "flipped"} and all(row["pair_change"] == "malay->indian" and row["pair_factor"] == "p2_ethnicity" for row in pair.values())
    assert (pair["base"]["p1_ethnicity"], pair["base"]["p2_ethnicity"], pair["flipped"]["p2_ethnicity"]) == ("chinese", "malay", "indian")
    record = json.loads((tmp_path / "flip_run" / "sessions" / f"{pair['flipped']['session_id']}.json").read_text(encoding="utf-8"))
    p1, p2 = pair["flipped"]["p1_agent"], pair["flipped"]["p2_agent"]
    texts = {point["agent_id"]: point["prompt"]["messages"][1]["content"] for point in record["decision_points"]}
    assert OWN["indian"] in texts[p2] and OWN["chinese"] in texts[p1] and SEEN["indian"] in texts[p1]


def test_a_group_flip_is_checked():
    good = {"base": FLIP_BASE, "factor": "p2_ethnicity", "ethnicity": {"p1": "chinese", "p2": "malay"}, "to": "indian"}
    for broken, message in (
        ({**good, "ethnicity": {"p1": "chinese", "p2": "chinese"}}, "are 'same', not 'different'"),  # the groups contradict the cell
        ({**good, "to": "malay"}, "a group other than 'malay'"),
        ({**good, "to": "kestrop"}, "a group other than"),
        ({**good, "ethnicity": {"p1": "chinese"}}, "ethnicity"),
        ({**good, "ethnicity": {"p1": "eurasian", "p2": "malay"}}, "ethnicity.p1"),
        ({"base": FLIP_BASE, "factor": "age_pair", "to": "p1_older", "ethnicity": {"p1": "chinese", "p2": "malay"}}, "fixed only by a pair that flips"),
    ):
        with pytest.raises(ConfigError, match=message):
            flip_config("bad", [broken])
    with pytest.raises(ConfigError, match="which the design does not run"):  # to the other's group, in a design of different only
        flip_config("only_different", [{**good, "to": "chinese"}], factors_={"ethnicity_pair": ["different"]})
    with pytest.raises(ConfigError, match="does not vary ethnicity_pair"):
        config("no_eth", {"age_pair": ["same", "p1_older"]}, design={"counterfactual_pairs": [
            {"base": {"age_pair": "same"}, "factor": "p2_ethnicity", "ethnicity": {"p1": "chinese", "p2": "malay"}, "to": "indian"}]})


def test_every_other_pair_keeps_its_code_and_ids():
    base = {"age_pair": "same", "gender_pair": "p1_female", "mapping": "p1_lower"}
    plain = D.CounterfactualPair(base, "age_pair", "p1_older")
    named = {"base": D.cell_code(base), "factor": "age_pair", "to": "p1_older"}
    import hashlib
    assert plain.code == hashlib.sha256(json.dumps(named, sort_keys=True).encode("utf-8")).hexdigest()[:8]
    assert plain.groups is None and plain.change is None and "ethnicity" not in plain.as_dict()
    c = config("old_pair", {"age_pair": ["same", "p1_older"]}, design={"counterfactual_pairs": [{"base": {"age_pair": "same"}, "factor": "age_pair", "to": "p1_older"}]})
    for s in E.plan(c).sessions:
        if s.pair_id is not None:
            assert not s.session_id.endswith(("_base", "_flipped")) and s.pair_change is None and "pair_change" not in s.as_dict()
