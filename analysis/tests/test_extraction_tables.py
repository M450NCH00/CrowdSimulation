"""Issue #66 (RF-11): negsim's rule extractor builds its tables in the standard library; they must
say what RF-8's analysis says of the same sessions (the other's factors as told, the outcomes, the
coin-flip cells). Run on round 1's data (RF-10 re-executed and RF-30, pooled)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from analysis import load as L
from analysis import noise as N

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [ROOT / "llm_negotiation" / "runs" / name / "outcomes.csv"
           for name in ("rf10_round1_head_on_keep_line", "rf30_round1_head_on_keep_line")]


@pytest.fixture(scope="module")
def both():
    pytest.importorskip("yaml")
    sys.path.insert(0, str(ROOT / "llm_negotiation"))
    from negsim.extraction import table as T

    sources = [T.read_source(path.parent) for path in SOURCES]
    sessions = [s for s in T.pooled_sessions(sources) if s.completed]
    rows = {}
    for session in sessions:
        record = session.source.record(session.session_id)
        for person in ("p1", "p2"):
            rows[(session.session_id, person)] = T.agent_row(session, person, record, "untested")
    raw = L.read_outcomes(SOURCES)
    table, _ = L.sessions_table(raw)
    agents, _ = L.agents_table(raw, table)
    agents = agents.set_index(["session_id", "role"])
    return T, sources, rows, agents


def test_the_others_factors_as_told_agree_with_rf8(both):
    T, _, rows, agents = both
    for (session_id, person), row in rows.items():
        theirs = agents.loc[(session_id, person)]
        assert (row["other_age"] != T.NOT_TOLD) == bool(theirs["other_age_told"])
        assert (row["other_gender"] != T.NOT_TOLD) == bool(theirs["other_gender_told"])
        for name in T.OBSERVABLE:
            assert (row[f"other_{name}"] != T.NOT_SEEN) == bool(theirs[f"other_{name}"]), (session_id, person, name)
        told = theirs["other_ethnicity"]
        assert row["other_ethnicity"] == (T.NOT_TOLD if not isinstance(told, str) else told)
        assert (row["finds_other_attractive"] == "yes") == bool(theirs["finds_other_attractive"])
        assert (row["knows_other"] == "yes") == bool(theirs["knows_other"])


def test_the_outcomes_agree_with_rf8(both):
    _, _, rows, agents = both
    for (session_id, person), row in rows.items():
        theirs = agents.loc[(session_id, person)]
        first = theirs["passed_first"]  # RF-8: missing, 1 (this person), 0 (the other, or together)
        if first != first:
            assert row["passed_first"] == ""
        else:
            assert row["passed_first"] in (("yes",) if first == 1 else ("no", "together"))
        kept_left = theirs["kept_left"]
        assert row["passing_side"] == ("" if kept_left != kept_left else "left" if kept_left == 1 else "right")
        for key in ("stopped", "backed_up"):
            assert row[key] == ("" if theirs[key] != theirs[key] else "yes" if theirs[key] == 1 else "no")
        for key in ("slowed", "stopped", "backed_up"):
            value = theirs[f"plan_{key}"]
            assert row[f"first_{key}"] == ("" if value != value else "yes" if value == 1 else "no")


def test_the_coin_flip_cells_are_rf8s(both):
    T, sources, _, _ = both
    raw = L.read_outcomes(SOURCES)
    table, _ = L.sessions_table(raw)
    theirs = N.stability(table)
    mine = T.coin_flip_cells(sources)
    assert len(mine) == len(theirs) == 24
    expected = {cell: bool(flip) for cell, flip in zip(theirs["cell"], theirs["coin_flip"])}
    assert {cell: entry["coin_flip"] for cell, entry in mine.items()} == expected
    assert sum(expected.values()) == 23
