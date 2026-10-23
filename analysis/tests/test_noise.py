"""Counterfactual flip rates against the noise floor, and stability (issue #63, task 12)."""

from __future__ import annotations

import random

import pandas as pd
import pytest

from analysis import load as L
from analysis import noise as N
from synthetic import row, write_csv

OUTCOMES = [("p1", "left"), ("p2", "left"), ("p1", "right"), ("p2", "right")]


def behaviour(rng: random.Random, base: int, noise: float) -> tuple[str, str]:
    """The cell's own outcome, or, with probability ``noise``, another drawn at random."""
    if rng.random() < noise:
        return OUTCOMES[rng.choice([k for k in range(len(OUTCOMES)) if k != base])]
    return OUTCOMES[base]


def experiment(seed: int, effect: bool, noise: float = 0.1, cells: int = 30, pairs: int = 60) -> list[dict]:
    """``cells`` cells of the exact-repeat set, 3 repeats each, and ``pairs`` counterfactual
    pairs. With ``effect``, flipping the factor changes the outcome (who passes first); without,
    the flipped session draws from the same outcome as its base. Both draw ``noise``."""
    rng = random.Random(f"noise:{seed}")
    rows = []
    for c in range(cells):
        base = rng.randrange(len(OUTCOMES))
        for r in range(1, 4):
            first, side = behaviour(rng, base, noise)
            rows.append(row(f"T_c{c:03d}_r{r}", "talk", first=first, sides={"p1": side, "p2": side}, exact_repeat_set=True))
    for k in range(pairs):
        base = rng.randrange(len(OUTCOMES))
        flipped = base ^ 1 if effect else base  # p1 <-> p2 passes first
        for role, which in (("base", base), ("flipped", flipped)):
            first, side = behaviour(rng, which, noise)
            rows.append(row(f"T_x{k:03d}_{role}", "talk", first=first, sides={"p1": side, "p2": side}, pair=(f"T_x{k:03d}", role, "urgency")))
    return rows


def sessions_of(tmp_path, rows):
    sessions, _ = L.sessions_table(L.read_outcomes([write_csv(rows, tmp_path / "outcomes.csv")]))
    return sessions


@pytest.mark.parametrize("component", ["who_passed_first", "behaviour"])
def test_a_planted_factor_effect_is_above_the_noise_floor(tmp_path, component):
    sessions = sessions_of(tmp_path, experiment(seed=1, effect=True))
    floors, flips = N.summaries(sessions, seed=1, components=[component])
    talk = flips.loc[flips["subset"] == "talk"].iloc[0]
    assert talk["verdict"] == "above the noise floor"
    assert talk["rate"] > 0.7 and 0 < talk["noise_rate"] < 0.35


@pytest.mark.parametrize("seed", [2, 3])
def test_with_noise_only_the_flip_rate_is_not_above_the_noise_floor(tmp_path, seed):
    sessions = sessions_of(tmp_path, experiment(seed=seed, effect=False))
    _, flips = N.summaries(sessions, seed=seed, components=["behaviour"])
    assert set(flips["verdict"]) == {"not distinguishable from the noise floor"}


def test_the_noise_floor_counts_every_pair_of_repeats_exactly(tmp_path):
    rows = [
        row("T_a_r1", "talk", first="p1", exact_repeat_set=True), row("T_a_r2", "talk", first="p1", exact_repeat_set=True),
        row("T_a_r3", "talk", first="p2", exact_repeat_set=True),  # 2 of 3 pairs differ
        row("T_b_r1", "talk", first="p1", exact_repeat_set=True), row("T_b_r2", "talk", first="p1", exact_repeat_set=True),  # 0 of 1
        row("T_c_r1", "talk", first="p1"),  # not in the set
    ]
    floor = N.noise_floor(sessions_of(tmp_path, rows), "who_passed_first", bootstrap=200)
    talk = floor.loc[floor["subset"] == "talk"].iloc[0]
    assert (talk["cells"], talk["pairs"], talk["flips"]) == (2, 4, 2) and talk["rate"] == 0.5
    assert talk["ci_low"] <= 0.5 <= talk["ci_high"]


def test_stability_and_coin_flip_cells_are_exact_on_a_hand_made_table(tmp_path):
    rows = [
        *(row(f"T_same_r{r}", "talk", first="p1", exact_repeat_set=True) for r in (1, 2, 3)),
        *(row(f"T_split_r{r}", "talk", first=f, exact_repeat_set=True) for r, f in ((1, "p1"), (2, "p1"), (3, "p2"))),
        *(row(f"T_three_r{r}", "talk", first=f, exact_repeat_set=True) for r, f in ((1, "p1"), (2, "p2"), (3, "together"))),
        *(row(f"T_side_r{r}", "talk", first="p1", sides={"p1": s, "p2": s}, exact_repeat_set=True)
          for r, s in ((1, "left"), (2, "left"), (3, "left"), (4, "right"))),
    ]
    table = N.stability(sessions_of(tmp_path, rows)).set_index("cell")
    assert table.loc["T_same", "stability_behaviour"] == 1 and not table.loc["T_same", "coin_flip"]
    assert table.loc["T_split", "stability_who_passed_first"] == pytest.approx(2 / 3) and table.loc["T_split", "coin_flip"]
    assert table.loc["T_three", "stability_who_passed_first"] == pytest.approx(1 / 3) and table.loc["T_three", "coin_flip"]
    side = table.loc["T_side"]
    assert (side["repeats"], side["stability_who_passed_first"], side["stability_passing_side"]) == (4, 1, 0.75)
    assert not side["coin_flip"]  # 3 in 4 is not below 3 in 4
    distribution = N.stability_distribution(table.reset_index())
    who = distribution.loc[distribution["component"] == "who_passed_first"].set_index("stability")["cells"]
    assert who.to_dict() == {round(1 / 3, 4): 1, round(2 / 3, 4): 1, 1.0: 2}


def test_a_pair_with_one_session_missing_is_left_out(tmp_path):
    rows = [row("T_x1_base", "talk", pair=("T_x1", "base", "load")), row("T_x1_flipped", "talk", first="p2", pair=("T_x1", "flipped", "load")),
            row("T_x2_base", "talk", pair=("T_x2", "base", "load"))]
    flips = N.flip_rates(sessions_of(tmp_path, rows), "who_passed_first")
    assert flips.loc[flips["subset"] == "talk", ["pairs", "flips"]].iloc[0].tolist() == [1, 1]


def test_the_wilson_interval():
    low, high = N.wilson(5, 10)
    assert low == pytest.approx(0.2366, abs=1e-4) and high == pytest.approx(0.7634, abs=1e-4)
    assert N.wilson(0, 10)[0] == 0.0
