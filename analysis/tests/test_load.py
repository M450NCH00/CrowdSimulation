"""Reading and reshaping (issue #63, task 2): one row per agent, the other's factors as told."""

from __future__ import annotations

import sys

import pytest

from analysis import factors as F
from analysis import load as L
from synthetic import row, write_csv

LOAD_CELL = {"load": "p1"}
P1_LOAD = {"p1": {"load": "large_suitcase"}, "p2": {"load": "none"}}


def agents_of(tmp_path, rows, name="outcomes.csv"):
    raw = L.read_outcomes([write_csv(rows, tmp_path / name)])
    sessions, left_out = L.sessions_table(raw)
    agents, predictors = L.agents_table(raw, sessions)
    return sessions, agents, predictors, left_out


def one(agents, session_id, role):
    (found,) = agents.loc[(agents["session_id"] == session_id) & (agents["role"] == role)].to_dict("records")
    return found


def test_a_factor_never_printed_to_an_agent_is_not_counted_as_seen(tmp_path):
    rows = [
        row("never_r1", cell=LOAD_CELL, people=P1_LOAD, shown={"p2": {"observable": 0}}),
        row("printed_r1", cell=LOAD_CELL, people=P1_LOAD, shown={"p2": {"observable": 2}}),
        row("switched_off_r1", cell={**LOAD_CELL, "load_visible": False}, people=P1_LOAD, shown={"p2": {"observable": 2}}),
    ]
    _, agents, predictors, _ = agents_of(tmp_path, rows)
    assert "other_load" in predictors
    assert one(agents, "never_r1", "p2")["other_load"] == 0 and one(agents, "never_r1", "p2")["other_load_actual"] == 1
    assert one(agents, "printed_r1", "p2")["other_load"] == 1
    assert one(agents, "switched_off_r1", "p2")["other_load"] == 0
    assert all(one(agents, s, "p1")["own_load"] == 1 and one(agents, s, "p2")["own_load"] == 0 for s in ("never_r1", "printed_r1"))


def test_the_others_age_and_gender_count_only_where_they_were_printed(tmp_path):
    older = {"p1": {"age": 70, "gender": "male"}, "p2": {"age": 25, "gender": "female"}}
    rows = [
        row("far_r1", cell={"age_pair": "p1_older"}, people=older, shown={"p2": {"age": 0, "gender": 0}}),
        row("near_r1", cell={"age_pair": "p1_older"}, people=older, shown={"p2": {"age": 1, "gender": 1}}),
        row("hidden_r1", cell={"age_pair": "p1_older", "demographics_visible": False}, people=older),
    ]
    _, agents, _, _ = agents_of(tmp_path, rows)
    far, near, hidden = (one(agents, s, "p2") for s in ("far_r1", "near_r1", "hidden_r1"))
    assert (far["other_age_high"], far["other_female"], far["other_demographics_unseen"]) == (0, 0, 1)
    assert (near["other_age_high"], near["other_demographics_unseen"]) == (1, 0)
    assert one(agents, "near_r1", "p1")["own_age_high"] == 1
    assert one(agents, "hidden_r1", "p1")["own_age_high"] == 0 and hidden["own_demographics_hidden"] == 1


def test_the_others_ethnicity_counts_only_where_it_was_told(tmp_path):
    # Issue #92: one's own group is always told; the other's only where its line was printed.
    malay_chinese = {"p1": {"ethnicity": "malay"}, "p2": {"ethnicity": "chinese"}}
    both_indian = {"p1": {"ethnicity": "indian"}, "p2": {"ethnicity": "indian"}}
    rows = [
        row("same_told_r1", cell={"ethnicity_pair": "same"}, people=both_indian, shown={"p1": {"ethnicity": 2}, "p2": {"ethnicity": 1}}),
        row("same_far_r1", cell={"ethnicity_pair": "same"}, people=both_indian, shown={"p1": {"ethnicity": 0}, "p2": {"ethnicity": 0}}),
        row("different_told_r1", cell={"ethnicity_pair": "different"}, people=malay_chinese, shown={"p1": {"ethnicity": 1}, "p2": {"ethnicity": 3}}),
        row("hidden_r1", cell={"ethnicity_pair": "same", "ethnicity_visible": False}, people=both_indian, shown={"p1": {"ethnicity": 0}, "p2": {"ethnicity": 0}}),
    ]
    _, agents, predictors, _ = agents_of(tmp_path, rows)
    assert "same_ethnicity" in predictors and "ethnicity_unseen" in predictors
    assert not any(name in predictors for name in ("own_ethnicity", "other_ethnicity", "other_ethnicity_actual"))  # descriptive only (A3)
    told = one(agents, "same_told_r1", "p2")
    assert (told["same_ethnicity"], told["ethnicity_unseen"], told["other_ethnicity"]) == (1, 0, "indian")
    far = one(agents, "same_far_r1", "p1")
    assert (far["same_ethnicity"], far["ethnicity_unseen"], far["own_ethnicity"], far["other_ethnicity_actual"]) == (0, 1, "indian", "indian")
    assert far["other_ethnicity"] != far["other_ethnicity"]  # NaN: not told
    different = one(agents, "different_told_r1", "p1")
    assert (different["same_ethnicity"], different["ethnicity_unseen"], different["other_ethnicity"]) == (0, 0, "chinese")
    assert one(agents, "hidden_r1", "p1")["ethnicity_unseen"] == 1
    assert F.factor_of("same_ethnicity") == "ethnicity_pair" and F.factor_of("ethnicity_unseen") == "ethnicity_visible"


def test_a_pairwise_value_counts_only_where_its_line_was_shown(tmp_path):
    rows = [
        row("shown_r1", shown={"p1": {"pairwise": 2}, "p2": {"pairwise": 2}}),
        row("unshown_r1", shown={"p1": {"pairwise": 0}, "p2": {"pairwise": 0}}),
    ]
    for r in rows:
        r.update({"p1_finds_other_attractive": 1, "p2_finds_other_attractive": 0, "p1_knows_other": 1, "p2_knows_other": 1})
    _, agents, predictors, _ = agents_of(tmp_path, rows)
    assert {"finds_other_attractive", "knows_other", "pairwise_unseen"} <= set(predictors)
    shown, unshown = one(agents, "shown_r1", "p1"), one(agents, "unshown_r1", "p1")
    assert (shown["finds_other_attractive"], shown["knows_other"], shown["pairwise_unseen"]) == (1, 1, 0)
    assert (unshown["finds_other_attractive"], unshown["knows_other"], unshown["pairwise_unseen"]) == (0, 0, 1)


def test_the_physical_columns_follow_the_encounters_order_not_person_1(tmp_path):
    """Person 1 is agent 1 and agent 1 noticed first, so it is ``a``."""
    rows = [row("swapped_r1", p1_agent=1, order=(1, 0), first="p2", sides={"p1": "right", "p2": "left"},
                stopped={"p1": True}, backed={"p2": True})]
    sessions, agents, _, _ = agents_of(tmp_path, rows)
    raw = L.read_outcomes([tmp_path / "outcomes.csv"])
    assert raw.loc[0, "passing_side_a_plan_only"] == "right" and raw.loc[0, "who_passed_first_plan_only"] == "0"
    p1, p2 = one(agents, "swapped_r1", "p1"), one(agents, "swapped_r1", "p2")
    assert (p1["agent"], p1["passed_first"], p1["kept_left"], p1["stopped"], p1["backed_up"]) == (1, 0, 0, 1, 0)
    assert (p2["agent"], p2["passed_first"], p2["kept_left"], p2["stopped"], p2["backed_up"]) == (0, 1, 1, 0, 1)
    assert p1["is_lower_agent"] == 0 and p2["is_lower_agent"] == 1


def test_together_is_not_first_and_nobody_leaving_is_unknown(tmp_path):
    _, agents, _, _ = agents_of(tmp_path, [row("t_r1", first="together"), row("n_r1", first=None)])
    assert one(agents, "t_r1", "p1")["passed_first"] == 0 == one(agents, "t_r1", "p2")["passed_first"]
    assert agents.loc[agents["session_id"] == "n_r1", "passed_first"].isna().all()


def test_sessions_without_an_encounter_are_left_out_and_counted(tmp_path):
    sessions, agents, _, left_out = agents_of(tmp_path, [row("a_r1"), row("b_r1", outcome="no_encounter"), row("c_r1", outcome="aborted")])
    assert list(sessions["session_id"]) == ["a_r1"] and len(agents) == 2
    assert left_out == {"no_encounter": 1, "aborted": 1}


def test_an_older_outcomes_csv_is_refused_with_how_to_rebuild_it(tmp_path):
    r = row("old_r1")
    del r["encounter_agents"]
    with pytest.raises(L.AnalysisError, match="run the experiment again"):
        L.read_outcomes([write_csv([r], tmp_path / "outcomes.csv")])


def test_the_first_plan_and_signals_are_coded_per_agent(tmp_path):
    rows = [row("p_r1", "talk", plans={"p1": {"side": "left", "slowed": True, "start_distance_m": 6.0}, "p2": {"side": "both", "backed_up": True}},
                signals={"p1": "nod;wave_on"}),
            row("i_r1", "independent")]
    _, agents, _, _ = agents_of(tmp_path, rows)
    p1, p2 = one(agents, "p_r1", "p1"), one(agents, "p_r1", "p2")
    assert (p1["plan_left"], p1["plan_right"], p1["plan_slowed"], p1["start_distance_m"], p1["signalled"]) == (1, 0, 1, 6.0, 1)
    assert (p2["plan_left"], p2["plan_right"], p2["plan_backed_up"], p2["signalled"]) == (0, 0, 1, 0)
    assert agents.loc[agents["session_id"] == "i_r1", "signalled"].isna().all()  # no signal in the independent condition


def test_the_factor_table_agrees_with_negsim():
    pytest.importorskip("yaml")
    sys.path.insert(0, str(L.Path(__file__).resolve().parents[2] / "llm_negotiation"))
    from negsim.personas.schema import ATTRIBUTES, FACTOR_ATTRIBUTES
    from negsim.resolution import design, ethnicity, factors, pairwise

    assert list(F.PERSON) == list(FACTOR_ATTRIBUTES)
    for name, (base, marked, observable) in F.PERSON.items():
        assert ATTRIBUTES[name].levels == (base, marked) and ATTRIBUTES[name].observable == observable
    assert F.SITUATIONS == factors.SITUATIONS
    assert set(F.DESIGN_COLUMNS) == set(design.ALL_FACTORS)
    assert set(pairwise.SWITCHES.values()) <= set(F.DESIGN_COLUMNS)
    assert F.ETHNICITY_GROUPS == ethnicity.GROUPS and set(ethnicity.ETHNICITY_FACTORS) <= set(F.DESIGN_COLUMNS)
