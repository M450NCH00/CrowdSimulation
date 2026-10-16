"""Issue #30, Part 3: the persona design matrix and the session list."""

from __future__ import annotations

import itertools
from collections import Counter

import pytest

from negsim.configutil import ConfigError
from negsim.personas.schema import NAME_LIKE_FIELDS
from negsim.rulegen.design import (
    FACTOR_LEVELS,
    FACTORS,
    DesignSettings,
    balance,
    personas_of,
    sessions_for,
    visibility_of,
)

FULL = {name: list(levels) for name, levels in FACTOR_LEVELS.items()}
CASES = [("head_on_aaaaaaaa", 1, (0, 1)), ("flow_bbbbbbbb", 1, (13, 51))]


def settings(**changes):
    raw = {"seed": 7, "factors": FULL, **changes}
    return DesignSettings.from_config(raw)


def test_the_full_factorial_is_every_combination_for_every_case_and_condition():
    sessions = sessions_for(CASES, settings(), ["negotiated", "stated"], {"stated": 3}, "test")
    cells = 3 * 4 * 3 * 2 * 2 * 2
    assert len(sessions) == len(CASES) * cells * (1 + 3)
    assert [session.index for session in sessions] == list(range(1, len(sessions) + 1))
    assert len({session.session_id for session in sessions}) == len(sessions)


def test_every_level_and_every_pair_of_levels_is_equally_often_in_every_block():
    sessions = sessions_for(CASES, settings(), ["negotiated", "stated"], {"stated": 2}, "test")
    for block, counts in balance(sessions).items():
        for name in FACTORS:
            assert len(set(counts[name].values())) == 1, (block, name, counts[name])
    for condition, case in itertools.product(("negotiated", "stated"), [case for case, _, _ in CASES]):
        mine = [session for session in sessions if (session.condition, session.case_id) == (condition, case)]
        for first, second in itertools.combinations(FACTORS, 2):
            pairs = Counter((str(session.cell[first]), str(session.cell[second])) for session in mine)
            assert len(pairs) == len(FACTOR_LEVELS[first]) * len(FACTOR_LEVELS[second])
            assert len(set(pairs.values())) == 1, (first, second)


def test_the_list_is_reproducible_and_its_ids_do_not_depend_on_its_order():
    one = sessions_for(CASES, settings(), ["negotiated"], {}, "test")
    two = sessions_for(CASES, settings(), ["negotiated"], {}, "test")
    assert [session.as_dict() for session in one] == [session.as_dict() for session in two]
    other = sessions_for(CASES, settings(seed=8), ["negotiated"], {}, "test")
    assert [session.session_id for session in other] != [session.session_id for session in one]  # another order
    assert {session.session_id: session.cell for session in other} == {session.session_id: session.cell for session in one}
    alone = sessions_for(CASES[:1], settings(), ["negotiated"], {}, "test")
    assert {session.session_id for session in alone} < {session.session_id for session in one}


def test_the_people_of_a_cell():
    design = settings()
    cell = {"age_pair": "p1_older", "gender_pair": "p1_female", "task": "p2_urgent", "demographics_visible": True, "mapping": "p1_higher", "order": "lower_first"}
    people = personas_of(cell, (13, 51), design)
    assert people[51] == {"age": 70, "gender": "female", "task": "the supermarket", "urgency": "routine"}  # person 1, the higher agent
    assert people[13] == {"age": 25, "gender": "male", "task": "the emergency room", "urgency": "urgent"}
    swapped = personas_of({**cell, "mapping": "p1_lower"}, (13, 51), design)
    assert swapped[13] == people[51] and swapped[51] == people[13]
    none = personas_of({**cell, "task": "none", "age_pair": "same", "gender_pair": "same_male"}, (0, 1), design)
    assert none[0] == none[1] == {"age": 25, "gender": "male", "task": None, "urgency": None}
    for person in [*people.values(), *none.values()]:
        assert not NAME_LIKE_FIELDS & set(person)  # no names, anywhere


def test_hidden_demographics_and_the_order_of_speaking_or_describing():
    cell = {"age_pair": "same", "gender_pair": "same_female", "task": "none", "demographics_visible": False, "mapping": "p1_lower", "order": "higher_first"}
    visibility = visibility_of(cell)
    assert visibility["age"] is False and visibility["gender"] is False and visibility["speed"] and visibility["size"]
    assert visibility["task"] is False and visibility_of({**cell, "demographics_visible": True})["age"] is True
    (session,) = [s for s in sessions_for(CASES[1:], settings(), ["stated"], {}, "test") if s.cell == cell]
    assert (session.first, session.second) == (51, 13) and session.visibility == visibility


def test_levels_can_be_narrowed_per_case():
    design = settings(factors={**FULL, "demographics_visible": [True, False]}, per_case={"flow_bbbbbbbb": {"demographics_visible": [False], "task": ["none"]}})
    sessions = sessions_for(CASES, design, ["negotiated"], {}, "test")
    flow = [session for session in sessions if session.case_id == "flow_bbbbbbbb"]
    assert {session.cell["demographics_visible"] for session in flow} == {False} and {session.cell["task"] for session in flow} == {"none"}
    head_on = [session for session in sessions if session.case_id == "head_on_aaaaaaaa"]
    assert {session.cell["demographics_visible"] for session in head_on} == {True, False}


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"factors": {**FULL, "age_pair": ["older"]}}, "unknown level"),
        ({"factors": {**FULL, "demographics_visible": [1, 0]}}, "unknown level"),
        ({"factors": {key: value for key, value in FULL.items() if key != "task"}}, "missing required key"),
        ({"factors": {**FULL, "order": []}}, "non-empty list"),
        ({"factors": {**FULL, "mapping": ["p1_lower", "p1_lower"]}}, "listed twice"),
        ({"base_age": 100, "age_difference": 45}, "at most 120"),
        ({"tasks": {"urgent": "x"}}, "missing required key"),
        ({"per_case": {"x": {"colour": ["red"]}}}, "unknown key"),
    ],
)
def test_a_bad_design_is_refused(changes, message):
    with pytest.raises(ConfigError, match=message):
        settings(**changes)


def test_an_unknown_condition_and_a_repeated_case_are_refused():
    with pytest.raises(ConfigError, match="unknown condition"):
        sessions_for(CASES, settings(), ["voted"], {}, "test")
    with pytest.raises(ConfigError, match="same id"):
        sessions_for(CASES + CASES[:1], settings(), ["negotiated"], {}, "test")
