"""Stated against measured, and intent against plan, on hand-made tables (issue #63, task 12)."""

from __future__ import annotations

import pandas as pd
import pytest

from analysis import cli
from analysis import effects as E
from analysis import intent as I
from analysis import stated as S
from synthetic import row, write_csv


def decision(session, agent, reason="", intent="Carry on as I am.", coded=None, condition="talk", parse_error=None):
    return {"session_id": session, "session_key": f"x::{session}", "agent_id": agent, "number": 1, "condition": condition,
            "reason": reason, "intent": intent, "parse_error": parse_error,
            "coded": coded if coded is not None else {"carry_on": True, "side": "none", "slowed": False, "stopped": False, "backed_up": False}}


REASONS = pd.DataFrame([
    decision("s1", 0, "She is pulling a suitcase, so I give her room."),
    decision("s1", 0, "Still the suitcase."),
    decision("s1", 1, "I am in a hurry to the emergency room."),
    decision("s2", 0, "Nothing in particular."),
    decision("s2", 1, ""),  # no reason: not counted
])


def test_the_reason_mentions_are_exact_on_a_hand_made_table():
    named = S.mentions(REASONS).set_index("factor")
    assert named.loc["load", ["reasons", "naming", "agents", "agents_naming"]].tolist() == [4, 2, 3, 1]
    assert named.loc["load", "share_of_reasons"] == 0.5 and named.loc["load", "share_of_agents"] == pytest.approx(1 / 3)
    assert named.loc["urgency", "naming"] == 1 and named.loc["gender", "naming"] == 0  # "her" is not a gender word
    assert named.loc["mobility_aid", "naming"] == 0


def fitted(terms):
    model = E.Fitted("stopped", "agent", E.ALL, "logistic", E.OK, 100, 30, 50)
    model.terms = [{"outcome": "stopped", "term": name, "factor": factor, "estimate": 1.0, "odds_ratio": 2.7, "p_holm": p, "significant": p < 0.05}
                   for name, factor, p in terms]
    return [model]


def test_the_stated_against_measured_table_is_exact_on_a_hand_made_table():
    named = S.mentions(REASONS)
    models = fitted([("other_load", "load", 0.4), ("own_urgency", "urgency", 0.01), ("surroundings_busy", "surroundings", 0.002)])
    table = S.stated_against_measured(named, models, ["load", "urgency", "surroundings", "distraction"], named_often=0.25).set_index("factor")
    assert table.loc["load", "verdict"] == S.NAMED_NOT_MEASURED  # named in 2 of 4, no effect
    assert table.loc["urgency", "verdict"] == S.NAMED_AND_MEASURED  # 1 of 4 = 0.25, an effect
    assert table.loc["surroundings", "verdict"] == S.MEASURED_NOT_NAMED
    assert table.loc["distraction", "verdict"] == S.NEITHER
    assert table.loc["mobility_aid", "verdict"] == S.NOT_VARIED
    assert table.loc["urgency", "strongest_term"] == "own_urgency" and table.loc["urgency", "strongest_p_holm"] == 0.01


def test_a_model_that_did_not_fit_gives_no_measured_effect():
    models = fitted([("own_urgency", "urgency", 0.01)])
    models[0].status = E.SEPARATION
    table = S.stated_against_measured(S.mentions(REASONS), models, ["urgency"], named_often=0.25).set_index("factor")
    assert table.loc["urgency", "measured_effect"] is False or table.loc["urgency", "measured_effect"] == False  # noqa: E712


def test_the_debrief_kinds_are_counted_per_condition(tmp_path):
    rows = [row("a_r1", "talk", debriefs={"p1": "habit", "p2": "none"}), row("b_r1", "talk", debriefs={"p1": "habit", "p2": "local_custom"}),
            row("c_r1", "independent", debriefs={"p1": "law_or_guidance", "p2": None})]
    results = cli.analyse([write_csv(rows, tmp_path / "outcomes.csv")])
    kinds = results.kinds
    assert kinds.loc["habit", "talk"] == 2 and kinds.loc["local_custom", "talk"] == 1 and kinds.loc["none", "talk"] == 1
    assert kinds.loc["(none given)", "independent"] == 1 and kinds.loc["all", "all"] == 6


PLAN = {"carry_on": False, "side": "none", "slowed": False, "stopped": False, "backed_up": False}
CHECKS = pd.DataFrame([
    decision("m1", 0, intent="Move over to my left a little.", coded={**PLAN, "side": "left"}),  # match
    decision("m2", 0, intent="Move over to my left a little.", coded={**PLAN, "side": "right"}),  # mismatch: side
    decision("m3", 0, intent="Slow down and let them by.", coded={**PLAN, "slowed": True, "side": "left"}),  # match: the plan does more
    decision("m4", 0, intent="Slow down.", coded={**PLAN, "carry_on": True}),  # mismatch: no slowing
    decision("m5", 0, intent="Run past.", coded=PLAN),  # uncoded
    decision("m6", 0, intent=None, coded=None, parse_error="not JSON"),  # unreadable
    decision("m7", 0, intent="Carry on as I am.", condition="independent"),  # match
    decision("m8", 0, intent="Step back and wait.", condition="independent", coded={**PLAN, "backed_up": True}),  # mismatch: no wait
])


def test_the_intent_against_plan_check_is_exact_on_a_hand_made_table():
    checked = I.check(CHECKS).set_index("session_id")
    assert checked["status"].to_dict() == {"m1": "match", "m2": "mismatch", "m3": "match", "m4": "mismatch", "m5": "uncoded",
                                           "m6": "unreadable", "m7": "match", "m8": "mismatch"}
    assert checked.loc["m2", "why"] == "intent says left, the plan turns right"
    assert checked.loc["m4", "why"] == "intent says slow_down, the plan does not"
    summary = I.summary(I.check(CHECKS)).set_index("subset")
    assert summary.loc["all", ["decision_points", "unreadable", "uncoded", "compared", "mismatches"]].tolist() == [8, 1, 1, 6, 3]
    assert summary.loc["all", "rate"] == 0.5
    assert summary.loc["talk", "rate"] == 0.5 and summary.loc["independent", "rate"] == 0.5


@pytest.mark.parametrize("text, categories, side", [
    ("Move over to my right and walk on.", {"keep_to_side"}, "right"),
    ("Keep going for a moment, then slow down.", {"slow_down"}, None),
    ("Let them pass on my right.", {"keep_to_side"}, None),  # a side said of the other: unknown
    ("All right, I'll wait.", {"stop_and_wait"}, None),
    ("Step back, then wait.", {"back_up", "stop_and_wait"}, None),
    ("Signal and carry on.", {"carry_on"}, None),
    ("Hold my ground.", {"other"}, None),
])
def test_the_intent_codebook_codes_these_intents(text, categories, side):
    assert I.code_intent(text, I.load_codebook()) == (frozenset(categories), side)


def test_the_codebooks_are_versioned_files():
    assert I.load_codebook()["version"] == 1 and S.load_codebook()["version"] == 1
    assert list(I.load_codebook()["categories"]) == list(I.CATEGORIES)
