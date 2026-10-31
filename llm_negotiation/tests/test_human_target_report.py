"""Issue #124 (RF-38): the human-targets report's studies, and who adapts in a pair with one cane user."""

from __future__ import annotations

import pytest

from negsim.human_targets import report as R

CANE = ("mobility_aid", "cane")


def _pair(canes=(True, False), shares=(0.3, 0.7), changes=(0.1, 0.3), first="together"):
    per_agent = {str(i): {"lateral_share": shares[i], "speed_change_mps": changes[i]} for i in (0, 1)}
    return {"agents": [0, 1], "passed_first": first, "people": [{"mobility_aid": "cane" if c else "none"} for c in canes],
            "measures": {"per_agent": per_agent}}


def test_rf37s_study_reads_the_runs_it_always_read():
    rf37 = R.STUDIES["rf37"]
    assert (rf37.out, rf37.head_on, rf37.speeds, rf37.flows, rf37.one_with) == (R.OUT, R.HEAD_ON, R.SPEEDS, R.FLOWS, None)
    assert rf37.title == "Round 1 against the human targets (issue #122, RF-37)"


def test_the_report_refuses_to_overwrite_when_the_runs_are_missing(tmp_path, monkeypatch):
    """PR #125's review: the trajectories are gitignored, so a fresh clone has no runs to read."""
    monkeypatch.setattr(R, "_seed_dirs", lambda *args: [])
    with pytest.raises(SystemExit):
        R.main(["--study", "rf38", "--out", str(tmp_path)])
    assert not list(tmp_path.iterdir())


def test_rf38s_study_reads_the_cane_pairs_only():
    rf38 = R.STUDIES["rf38"]
    assert rf38.head_on == ("rf38_cane_head_on", "head_on_cane") and rf38.one_with == CANE
    assert (rf38.speeds, rf38.flows) == ((), ())
    assert rf38.out == R.RUNS / "rf38_human_targets"


def test_who_adapts_counts_the_others_way_against_the_holders():
    pairs = [_pair(), _pair(canes=(False, True), shares=(0.8, 0.2), changes=(0.4, 0.0), first=0),
             _pair(shares=(0.6, 0.4), changes=(0.5, 0.2), first=0),  # the cane user adapts and slows more, and goes first
             _pair(shares=(0.5, 0.5), changes=(0.2, 0.2)),           # ties: dropped from both counts
             _pair(canes=(True, True)), _pair(canes=(False, False))]  # not one holder: not counted
    h = R.holder_pairs(pairs, CANE)
    assert h["pairs"] == 4
    assert (h["other_adapts_more"]["study_way"], h["other_adapts_more"]["other_way"]) == (2, 1)
    assert (h["other_slows_more"]["study_way"], h["other_slows_more"]["other_way"]) == (2, 1)
    assert h["passed_first"] == {"holder": 1, "other": 1, "together": 2, "none": 0}
    assert h["other_mean_lateral_share"] == pytest.approx((0.7 + 0.8 + 0.4 + 0.5) / 4, abs=1e-4)


def test_a_pair_without_measures_is_not_counted():
    assert R.holder_pairs([{"agents": [0, 1], "passed_first": None, "people": [{"mobility_aid": "cane"}, {"mobility_aid": "none"}],
                            "measures": {"min_centre_distance_m": None}}], CANE)["pairs"] == 0


def test_step1_sessions_are_filtered_to_exactly_one_holder(tmp_path, monkeypatch):
    rows = [("s1", "cane", "none", "True"), ("s2", "none", "cane", "False"), ("s3", "cane", "cane", "True"),
            ("s4", "none", "none", "True"), ("s5", "none", "cane", "True")]
    folder = tmp_path / "exp"
    folder.mkdir()
    (folder / "outcomes.csv").write_text(
        "session_id,condition,p1_agent,p2_agent,p1_age,p2_age,p1_mobility_aid,p2_mobility_aid,resolved_plan_only,who_passed_first_plan_only\n"
        + "".join(f"{s},independent,0,1,70,30,{a},{b},{r},together\n" for s, a, b, r in rows), encoding="utf-8")
    monkeypatch.setattr(R, "RUNS", tmp_path)
    monkeypatch.setattr(R, "pair_measures", lambda run: {"agents": [0, 1]})
    monkeypatch.setattr(R, "_json", lambda path: {"scenario": {"agents": [{"preferred_speed_mps": 1.3}]}})
    pairs, total = R.step1_pairs("exp", "independent", CANE)
    assert total == 3 and [p["session_id"] for p in pairs] == ["s1", "s5"]  # one holder: s1, s2, s5; resolved: s1, s5
    pairs, total = R.step1_pairs("exp", "independent")
    assert total == 5 and [p["session_id"] for p in pairs] == ["s1", "s3", "s4", "s5"]  # as RF-37 read them
