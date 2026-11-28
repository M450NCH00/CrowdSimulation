"""Factor effects, the tree and the mapping on synthetic screens (issue #63, task 12)."""

from __future__ import annotations

import math
import random

import pandas as pd
import pytest

from analysis import cli
from analysis import effects as E
from analysis import load as L
from synthetic import row, screen, write_csv


def analysed(tmp_path, rows, **options):
    return cli.analyse([write_csv(rows, tmp_path / "outcomes.csv")], cli.Options(**options))


def term(results, outcome, name, subset=E.ALL):
    model = next(m for m in results.fitted if m.outcome == outcome and m.subset == subset)
    assert model.status == E.OK, (model.status, model.note)
    return next(t for t in model.terms if t["term"] == name)


def test_a_planted_effect_is_recovered_with_the_right_sign(tmp_path):
    results = analysed(tmp_path, screen(seed=1, urgency_effect=1.5, told_load_effect=2.0))
    urgent = term(results, "passed_first", "own_urgency")
    assert urgent["significant"] and urgent["odds_ratio"] > 1 and urgent["or_low"] > 1
    told = term(results, "stopped", "other_load")
    assert told["significant"] and told["odds_ratio"] > 1
    for condition in ("independent", "talk"):  # in each condition on its own too
        assert term(results, "passed_first", "own_urgency", condition)["estimate"] > 0
    # Only the agent told of the suitcase changed: the one carrying it did not.
    assert not term(results, "stopped", "own_load")["significant"]


def test_with_no_planted_effect_nothing_is_significant_after_correction(tmp_path):
    results = analysed(tmp_path, screen(seed=2))
    significant = [(t["outcome"], t["subset"], t["term"], t["p_holm"]) for m in results.fitted for t in m.terms if t["significant"]]
    # Holm over every term of the report (the default family). Over one model at a time, this
    # seed lets two terms through by chance (WORK_LOG-63.md).
    assert significant == []
    fitted = [m for m in results.fitted if m.status == E.OK]
    assert len(fitted) >= 20  # the check is not empty


def test_standard_errors_are_clustered_by_session(tmp_path):
    """Duplicating every session's rows changes nothing once rows are clustered by session; the
    naive standard error would shrink by about the square root of 2."""
    rows = screen(seed=3, urgency_effect=1.0)
    raw = L.read_outcomes([write_csv(rows, tmp_path / "outcomes.csv")])
    sessions, _ = L.sessions_table(raw)
    agents, predictors = L.agents_table(raw, sessions)
    predictors = L.varied(agents, predictors)
    outcome = next(o for o in L.AGENT_OUTCOMES if o.name == "passed_first")
    once = E.fit_one(agents, outcome, predictors, ["condition"], E.ALL, "session_key")
    twice = E.fit_one(pd.concat([agents, agents], ignore_index=True), outcome, predictors, ["condition"], E.ALL, "session_key")
    se = {t["term"]: t["se"] for t in once.terms}
    for t in twice.terms:
        assert t["se"] == pytest.approx(se[t["term"]], rel=0.02), t["term"]


def holm(p):
    """Holm's step-down adjustment, written out."""
    order = sorted(range(len(p)), key=lambda i: p[i])
    adjusted, running = [0.0] * len(p), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(p) - rank) * p[i]))
        adjusted[i] = running
    return adjusted


def test_holm_runs_over_one_model_alone_and_over_every_term_of_the_report(tmp_path):
    rng = random.Random(9)
    frame = pd.DataFrame({"y": [rng.random() < 0.4 for _ in range(200)], "a": [rng.random() < 0.5 for _ in range(200)],
                          "b": [rng.random() < 0.5 for _ in range(200)], "session_key": [f"s{i // 2}" for i in range(200)]}).astype(
        {"y": float, "a": float, "b": float})
    fitted = E.fit_one(frame, L.Outcome("y", "binary", "agent", ""), ["a", "b"], [], E.ALL, "session_key")
    assert [t["p_holm"] for t in fitted.terms] == pytest.approx(holm([t["p"] for t in fitted.terms]))
    assert {t["holm_family"] for t in fitted.terms} == {"model"}
    results = analysed(tmp_path, screen(seed=10))
    terms = [t for m in results.fitted for t in m.terms]
    assert [t["p_holm"] for t in terms] == pytest.approx(holm([t["p"] for t in terms]))
    assert {t["family_size"] for t in terms} == {len(terms)} and len(terms) > 100
    with pytest.raises(L.AnalysisError, match="family"):
        E.correct(results.fitted, "everything")


def test_a_separated_outcome_is_reported_as_separation_never_as_an_effect():
    frame = pd.DataFrame({"y": [0, 0, 0, 0, 1, 1, 1, 1] * 5, "a": [0, 0, 0, 0, 1, 1, 1, 1] * 5, "session_key": [f"s{i}" for i in range(40)]})
    fitted = E.fit_one(frame, L.Outcome("y", "binary", "agent", ""), ["a"], [], E.ALL, "session_key")
    assert fitted.status == E.SEPARATION and fitted.terms == []


def test_a_constant_or_collinear_column_is_left_out_and_listed():
    frame = pd.DataFrame({"x": [0.0, 1.0, 0.0, 1.0], "same": [0.0, 1.0, 0.0, 1.0], "flat": [1.0] * 4})
    kept, dropped = E.full_rank(frame)
    assert list(kept.columns) == ["x"] and dropped == ["same (collinear)", "flat (constant)"]


def test_a_named_interaction_is_fitted(tmp_path):
    results = analysed(tmp_path, screen(seed=4), interactions=("own_urgency:own_age_high",))
    model = next(m for m in results.fitted if m.outcome == "passed_first" and m.subset == E.ALL)
    assert "own_urgency:own_age_high" in {t["term"] for t in model.terms}
    with pytest.raises(L.AnalysisError, match="interaction"):
        analysed(tmp_path, screen(seed=4), interactions=("own_urgency:no_such_column",))


def test_the_tree_finds_a_planted_split_and_stays_within_depth_3(tmp_path):
    results = analysed(tmp_path, screen(seed=5, urgency_effect=3.0))
    tree = results.tree
    assert tree.model is not None and tree.model.get_depth() <= 3
    assert "own_urgency" in tree.used and tree.cv_accuracy > tree.majority
    with pytest.raises(ValueError):
        from analysis.tree import grow

        grow(results.agents, results.varied_predictors, max_depth=4)


def test_the_mapping_counts_every_row_once_and_its_shares_are_the_means(tmp_path):
    results = analysed(tmp_path, screen(seed=6, sessions_per_condition=64))
    table, agents = results.mapping, results.agents
    assert table["rows"].sum() == len(agents)
    key = ["condition", *results.mapping_factors]
    for _, entry in table.head(10).iterrows():
        mask = pd.Series(True, index=agents.index)
        for name in key:
            mask &= agents[name] == entry[name]
        known = agents.loc[mask, "passed_first"].dropna()
        assert entry["n_passed_first"] == len(known)
        assert (math.isnan(entry["p_passed_first"]) and known.empty) or entry["p_passed_first"] == pytest.approx(known.mean())
