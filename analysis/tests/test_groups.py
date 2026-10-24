"""Real ethnicity (issue #92): outcomes by group, the other's as told, and rates weighted back to
random resident pairs."""

from __future__ import annotations

import math

from analysis import groups as G
from analysis import load as L
from synthetic import row, write_csv


def tables(tmp_path, rows):
    raw = L.read_outcomes([write_csv(rows, tmp_path / "outcomes.csv")])
    sessions, _ = L.sessions_table(raw)
    agents, _ = L.agents_table(raw, sessions)
    return sessions, agents


def ethnic_row(session_id, p1, p2, told, weight, resolved=True, first="p1", visible=True):
    out = row(session_id, cell={"ethnicity_pair": "same" if p1 == p2 else "different", "ethnicity_visible": visible},
              people={"p1": {"ethnicity": p1}, "p2": {"ethnicity": p2}}, shown={"p1": {"ethnicity": told}, "p2": {"ethnicity": told}},
              resolved=resolved, first=first)
    out["ethnicity_weight"] = weight
    return out


def test_outcomes_by_group_use_the_others_group_as_told(tmp_path):
    rows = [
        ethnic_row("a_r1", "indian", "chinese", 1, 2.0, first="p1"),
        ethnic_row("b_r1", "indian", "chinese", 1, 2.0, first="p2"),
        ethnic_row("c_r1", "indian", "chinese", 0, 2.0, first="p1"),  # never told
        ethnic_row("d_r1", "malay", "malay", 2, 0.5, first="p2"),
    ]
    _, agents = tables(tmp_path, rows)
    frame = G.by_group(agents).set_index(["own", "other_as_told"])
    assert frame.loc[("indian", "chinese"), "n"] == 2 and math.isclose(frame.loc[("indian", "chinese"), "passed_first"], 0.5)
    assert frame.loc[("indian", G.NOT_TOLD), "n"] == 1 and frame.loc[("indian", G.NOT_TOLD), "passed_first"] == 1.0
    assert frame.loc[("chinese", "indian"), "n"] == 2 and frame.loc[("malay", "malay"), "n"] == 2
    assert list(dict.fromkeys(frame.index.get_level_values("own"))) == ["chinese", "malay", "indian"]  # negsim's order


def test_rates_are_weighted_back_and_the_cost_is_reported(tmp_path):
    rows = [ethnic_row("a_r1", "chinese", "chinese", 1, 3.0, resolved=True), ethnic_row("b_r1", "others", "others", 1, 1.0, resolved=False)]
    sessions, _ = tables(tmp_path, rows)
    table = G.weighted(sessions).set_index("outcome")
    assert math.isclose(table.loc["resolved_plan_only", "unweighted"], 0.5)
    assert math.isclose(table.loc["resolved_plan_only", "weighted"], 0.75)
    assert math.isclose(table.loc["resolved_plan_only", "effective_sessions"], 16 / 10)


def test_without_ethnicity_there_are_no_tables(tmp_path):
    sessions, agents = tables(tmp_path, [row("a_r1"), row("b_r1")])
    assert G.by_group(agents) is None and G.weighted(sessions) is None
