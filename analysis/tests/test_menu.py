"""RF-49's analysis (issue #138): the menu arms against RF-40, the walls, the pass distance."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

from analysis import menu as M

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "llm_negotiation" / "negsim" / "negotiation" / "templates"


def test_the_wall_colours_are_the_templates_own():
    for key, colours in M.WALLS_BY_TEMPLATE.items():
        text = (TEMPLATES / f"{key}.yaml").read_text(encoding="utf-8")
        for colour, wall in colours.items():
            assert re.search(rf"^\s+{wall}: the {colour} wall\s*$", text, re.MULTILINE), (key, colour, wall)


def test_rf40_id_moves_the_repeat_for_the_swap_only():
    assert M.rf40_id("S_head_on_de176842_51dfba80_r1") == "S_head_on_de176842_51dfba80_r1"
    assert M.rf40_id("S_head_on_de176842_51dfba80_r1", 2) == "S_head_on_de176842_51dfba80_r3"
    assert M.rf40_id("T_head_on_02dfbadb_1caa9a84_r2", 2) == "T_head_on_02dfbadb_1caa9a84_r4"
    with pytest.raises(M.MenuError):
        M.rf40_id("S_head_on_de176842_5841fc4a_x42411b7c_flipped", 2)


def test_wall_of_reads_the_colour_by_the_template():
    assert M.wall_of("step a little towards the blue wall", "resolve_menu_abs_v1") == ("a", "blue")
    assert M.wall_of("step well towards the yellow wall", "resolve_menu_abs_v1") == ("b", "yellow")
    assert M.wall_of("step a little towards the blue wall", "resolve_menu_abs_swap_v1") == ("b", "blue")
    assert M.wall_of("step a little towards the yellow wall", "resolve_menu_abs_swap_v1") == ("a", "yellow")
    assert M.wall_of("carry on", "resolve_menu_abs_v1") is None
    assert M.wall_of("step a little to your right", "resolve_menu_v1") is None


def test_nearer_colour_needs_five_centimetres():
    line = "- You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are {} m from the blue wall and {} m from the yellow wall."
    assert M.nearer_colour([line.format("0.77", "0.98")]) == "blue"
    assert M.nearer_colour([line.format("0.98", "0.77")]) == "yellow"
    assert M.nearer_colour([line.format("0.88", "0.87")]) is None
    assert M.nearer_colour(["- It is quiet around you."]) is None


def _write_trajectory(path: Path, points):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        w = csv.writer(handle)
        w.writerow(["step", "time_s", "agent_id", "x_m", "y_m"])
        for step, (a, b) in enumerate(points):
            w.writerow([step, step / 10, 0, *a])
            w.writerow([step, step / 10, 1, *b])


def test_min_centre_distance_is_the_closest_approach(tmp_path):
    path = tmp_path / "trajectory.csv"
    _write_trajectory(path, [((-2, 0.4), (2, -0.4)), ((0, 0.45), (0.3, -0.45)), ((2, 0.4), (-2, -0.4))])
    assert M.min_centre_distance(path) == pytest.approx(0.9487, abs=1e-4)  # sqrt(0.3^2 + 0.9^2)
    assert M.min_centre_distance(tmp_path / "missing.csv") is None


# --- a small run on disk ------------------------------------------------------------------------

COLUMNS = ["session_id", "outcome", "condition", "geometry", "repeat", "pair_id", "resolved_plan_only", "collision_plan_only",
           "near_miss_plan_only", "deadlock_plan_only", "resolved_plan_orca"]
PLACE = "- You are in a passage 1.75 m wide, between the {0} wall and the {1} wall. You are 0.77 m from the {0} wall and 0.98 m from the {1} wall."


def point(agent, number, action, side, template, colours=("blue", "yellow"), message="", heard=(), error=None):
    return {"agent_id": agent, "number": number, "index": 2 * number + agent, "parse_error": error,
            "parsed": None if error else {"action": action, "message": message, "flags": []},
            "coded": {"side": side}, "view": {"place": [PLACE.format(*colours)], "heard": [{"message": h} for h in heard]}}


def experiment(folder: Path, template: str, sessions):
    """``sessions``: (session_id, condition, resolved, pair_id, [points])."""
    (folder / "sessions").mkdir(parents=True)
    with (folder / "outcomes.csv").open("w", encoding="utf-8", newline="") as handle:
        w = csv.DictWriter(handle, COLUMNS)
        w.writeheader()
        for session_id, condition, resolved, pair_id, points in sessions:
            w.writerow({"session_id": session_id, "outcome": "completed", "condition": condition, "geometry": "layout=aligned",
                        "repeat": session_id[-1], "pair_id": pair_id, "resolved_plan_only": str(resolved),
                        "collision_plan_only": str(not resolved), "near_miss_plan_only": "False", "deadlock_plan_only": "False",
                        "resolved_plan_orca": str(resolved)})
            record = {"session_id": session_id, "templates": {"core": {"key": template}}, "decision_points": points}
            (folder / "sessions" / f"{session_id}.json").write_text(json.dumps(record), encoding="utf-8")
            if resolved:
                _write_trajectory(folder / "replay" / session_id / "plan_only" / "trajectory.csv",
                                  [((-1, 0.45), (1, -0.45)), ((0, 0.45), (0, -0.45))])
    return folder


def test_a_run_is_loaded_paired_and_the_walls_counted(tmp_path):
    abs_t, swap_t = "resolve_menu_abs_v1", "resolve_menu_abs_swap_v1"
    rf40 = experiment(tmp_path / "rf40", "resolve_v9", [
        (f"S_c1_r{r}", "silent", r % 2 == 1, "", [point(0, 1, None, "right", "resolve_v9"), point(1, 1, None, "right", "resolve_v9")])
        for r in (1, 2, 3, 4)])
    # Blue at +y: both go towards yellow (-y), the same wall: a dance, not resolved.
    a = experiment(tmp_path / "abs", abs_t, [
        (f"S_c1_r{r}", "silent", False, "", [point(0, 1, "step a little towards the yellow wall", "right", abs_t),
                                             point(1, 1, "step a little towards the yellow wall", "left", abs_t)])
        for r in (1, 2)] + [("S_c1_x1_base", "silent", True, "p1", [])])
    # Yellow at +y: both go towards blue, now at -y: the same place, the other colour; resolved.
    s = experiment(tmp_path / "swap", swap_t, [
        (f"S_c1_r{r}", "silent", True, "", [point(0, 1, "step a little towards the blue wall", "right", swap_t, ("yellow", "blue")),
                                            point(1, 1, "step a little towards the blue wall", "left", swap_t, ("yellow", "blue"))])
        for r in (1, 2)])
    arms = {"rf40": M.load(rf40, "rf40"), "abs": M.load(a, "abs") + M.load(s, "abs", shift=2)}
    assert [x["rf40_id"] for x in arms["abs"]] == ["S_c1_r1", "S_c1_r2", "S_c1_r3", "S_c1_r4"]  # the pair left out
    summary = M.summarise(arms)
    assert summary["arms"]["abs|silent"]["resolved"]["k"] == 2
    assert summary["arms"]["abs|silent"]["start"] == {"towards_same_wall": {"sessions": 4, "resolved": 2}}
    assert summary["arms"]["rf40|silent"]["start"] == {"same_own_side": {"sessions": 4, "resolved": 2}}
    p = summary["paired"]["rf40->abs|silent|resolved"]
    # RF-40 resolved r1 and r3; RF-49 r3 and r4 (the swap's r1 and r2): r1 only RF-40, r2 neither, r3 both, r4 only RF-49.
    assert (p["sessions"], p["both"], p["only_base"], p["only_new"], p["neither"]) == (4, 1, 1, 1, 1)
    counts = summary["walls"]["counts"]
    assert counts["blue_at_+y"] == {"wall_b": 4, "yellow": 4}
    assert counts["yellow_at_+y"] == {"wall_b": 4, "blue": 4}
    assert summary["walls"]["test"]["fisher_p_half_by_wall"] == 1.0          # the place did not change
    assert summary["walls"]["test"]["fisher_p_half_by_colour"] < 0.05        # the colour did
    # 0.77 m from the first-named wall (a): the nearer wall is a; both moved towards b.
    assert summary["nearer"]["abs"] == {"layout=aligned|silent": {"towards_farther": 8}}
    assert summary["pass_distance"]["abs|silent"]["n"] == 2 and summary["pass_distance"]["abs|silent"]["median_m"] == 0.9
    assert "## 3. The walls" in M.markdown(summary)


def test_a_session_twice_in_one_arm_is_refused(tmp_path):
    t = "resolve_menu_abs_v1"
    a = experiment(tmp_path / "abs", t, [("S_c1_r1", "silent", True, "", [])])
    b = experiment(tmp_path / "b", t, [("S_c1_r1", "silent", True, "", [])])
    with pytest.raises(M.MenuError):
        M.summarise({"abs": M.load(a, "abs") + M.load(b, "abs")})


def test_talk_counts_named_walls_and_what_the_speaker_and_listener_did(tmp_path):
    t = "resolve_menu_abs_v1"
    a = experiment(tmp_path / "abs", t, [("T_c1_r1", "talk", True, "", [
        point(0, 1, "step a little towards the blue wall", "left", t, message="I'll keep to the blue wall."),
        point(1, 1, "step a little towards the yellow wall", "left", t, heard=["I'll keep to the blue wall."]),
        point(1, 2, "carry on", "none", t, error="unknown_action"),
    ])])
    out = M.talk(M.load(a, "abs"))
    assert out["decisions"] == 2 and out["with_message"] == 1 and out["names_a_wall"] == 1
    assert out["speaker_moved_towards_named_wall"] == 1 and out["listener_towards_other_wall"] == 1
    assert M.replies(M.load(a, "abs"))["unreadable"] == 1
