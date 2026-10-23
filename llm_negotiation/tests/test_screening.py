"""Issue #62 (RF-7): screening designs (fractional, sample), geometries, the exact-repeat set and
counterfactual pairs, in the resolution layer."""

from __future__ import annotations

import itertools
import json
import math
import random
import re
from collections import Counter
from pathlib import Path

import pytest

from negsim.configutil import ConfigError, load_yaml, resolve_path
from negsim.llm.mock import MockClient
from negsim.resolution import design as D
from negsim.resolution import experiment as E
from negsim.resolution import screening as S
from negsim.resolution.mock import POLICIES

REFS = Path(__file__).resolve().parents[2] / "refs"
GIT = {"commit": "test", "dirty": False}
CASES = [("head_on_aaaaaaaa", 2, (0, 1), "passing"), ("head_on_bbbbbbbb", 2, (0, 1), "passing")]
HEAD_ON = ["head_on_de176842@2", "head_on_02dfbadb@2"]  # aligned, and 20 cm apart

#: Sixteen two-level factors of the resolution layer, mapping among them; then one more.
SIXTEEN = {
    "age_pair": ["same", "p1_older"], "gender_pair": ["p1_female", "p1_male"], "urgency": ["neither", "p1"],
    "mobility_aid": ["neither", "p1"], "load": ["neither", "p1"], "distraction": ["neither", "p1"],
    "assertiveness": ["neither", "p1"], "residence": ["neither", "p1"], "memory_note": ["neither", "p1"],
    "demographics_visible": [True, False], "mobility_aid_visible": [True, False], "load_visible": [True, False],
    "surroundings": ["quiet", "busy"], "time_of_day": ["daytime", "late_night"], "familiarity": ["strangers", "acquaintances"],
    "mapping": ["p1_lower", "p1_higher"],
}
SEVENTEENTH = {"distraction_visible": [True, False]}


def factors(count, fixed=None):
    """The first ``count`` of :data:`SIXTEEN` (mapping always among them), the rest at one level."""
    names = [name for name in SIXTEEN if name != "mapping"][: count - 1] + ["mapping"]
    chosen = {name: (levels if name in names else levels[:1]) for name, levels in SIXTEEN.items()}
    # a switch needs its factor varied; at one level the factor is "neither" for both people
    return {**chosen, **(fixed or {})}


def design(**raw):
    return D.ResolutionDesign.from_config({"seed": 7, **raw})


# --- the fraction -----------------------------------------------------------------------------------


@pytest.mark.parametrize("count, cells", [(12, 32), (16, 32), (8, 16)])
def test_a_fractional_design_has_the_fewest_cells_that_hold_its_factors_at_resolution_iv(count, cells):
    found = design(kind="fractional", factors=factors(count))
    assert len(found.screened) == count and found.size == cells and found.cells() == cells
    assert len(found.cell_list()) == cells
    assert S.resolution(count, cells) >= 4
    rows = [[1 if cell[name] == found.levels[name][1] else -1 for name in found.screened] for cell in found.cell_list()]
    assert S.aliasing_problems(rows, found.screened) == []  # no main effect aliased with a main effect or a two-factor interaction
    assert len({json.dumps(cell, sort_keys=True) for cell in found.cell_list()}) == cells  # distinct cells


@pytest.mark.parametrize("count", [8, 12, 16])
def test_every_factor_of_a_fraction_is_balanced_mapping_included(count):
    found = design(kind="fractional", factors=factors(count))
    half = found.cells() // 2
    for name in found.screened:
        assert sorted(Counter(cell[name] for cell in found.cell_list()).values()) == [half, half], name
    assert "mapping" in found.screened  # counterbalanced: a column of the fraction like any other
    for name in found.factors:
        if name not in found.screened:
            assert {json.dumps(cell[name]) for cell in found.cell_list()} == {json.dumps(found.levels[name][0])}


def test_more_than_sixteen_factors_in_32_cells_is_refused_with_a_clear_message():
    with pytest.raises(ConfigError, match=r"17 two-level factors .* at most 32 cells: N cells hold at most N/2"):
        design(kind="fractional", factors={**SIXTEEN, **SEVENTEENTH})
    with pytest.raises(ConfigError, match=r"17 two-level factors in 32 cells: at resolution IV, 32 cells hold at most 16"):
        design(kind="fractional", cells=32, factors={**SIXTEEN, **SEVENTEENTH})
    with pytest.raises(ConfigError, match=r"12 two-level factors in 16 cells: at resolution IV, 16 cells hold at most 8"):
        design(kind="fractional", cells=16, factors=factors(12))


@pytest.mark.parametrize("raw, message", [
    ({"kind": "fractional", "factors": {**factors(8), "age_pair": ["same", "p1_older", "p2_older"]}}, "two-level factors only"),
    ({"kind": "fractional", "factors": factors(3)}, "use kind full"),
    ({"kind": "fractional", "cells": 64, "factors": factors(8)}, "16 or 32 cells, not 64"),
    ({"kind": "full", "cells": 32, "factors": factors(8)}, "a full design has every cell"),
    ({"kind": "sample", "factors": factors(8)}, "a sample needs the number of cells"),
    ({"kind": "sample", "cells": 300, "factors": factors(8)}, "ask for at most 256"),
    ({"kind": "screened", "factors": factors(8)}, "one of"),
    ({"kind": "fractional", "factors": factors(8), "exact_repeats": {"cells": 17, "times": 3}}, "the design has 16 cell"),
    ({"kind": "fractional", "factors": factors(8), "exact_repeats": {"cells": 8, "times": 1}}, "times"),
    ({"factors": factors(8), "repeats": 2, "exact_repeats": {"cells": 8, "times": 3}}, "not both"),
    ({"factors": factors(8), "geometries": ["head_on_de176842@2", "head_on_de176842@1"]}, "listed twice"),
])
def test_a_bad_screening_design_is_refused(raw, message):
    with pytest.raises(ConfigError, match=message):
        design(**raw)


def test_every_published_design_has_resolution_iv_or_more_checked_on_its_cells():
    for (runs, count), _ in S.GENERATORS.items():
        rows = S.fraction(count, runs)
        assert len(rows) == runs and S.aliasing_problems(rows) == [], (runs, count)
        assert S.resolution(count, runs) >= 4
    # the check catches a design that breaks resolution IV: a column that is the product of two others
    broken = [row + (row[0] * row[1],) for row in S.fraction(5, 16)]
    assert any("aliased with the interaction 1 x 2" in problem for problem in S.aliasing_problems(broken))
    assert any(problem == "1 is aliased with 6" for problem in S.aliasing_problems([row + (row[0],) for row in S.fraction(5, 16)]))


def test_the_nist_generators_are_those_of_the_cached_table():
    for (runs, count), words in S.GENERATORS.items():
        if S.SOURCES[(runs, count)] != S.NIST:
            continue
        text = (REFS / f"rf7_nist_2to{count}m{count - S.base_count(runs)}.txt").read_text(encoding="utf-8")
        assert f"NUMBER OF OBSERVATIONS           = {runs}" in text
        defined = re.findall(r"^\s+\(?(\d+)\)?\s+(\d+)\s", text, flags=re.MULTILINE)
        generated = [definition for factor, definition in defined if int(factor) > S.base_count(runs)][: len(words)]
        assert tuple(generated) == words, (runs, count)


def test_12_to_16_factors_in_32_cells_are_minimum_aberration_projections_of_the_saturated_design():
    """Chen & Cheng (2006), Corollary 3.6: every regular resolution IV design with 10 < k <= 16
    factors in 32 runs deletes columns from the saturated 2^(16-11) design (every odd-length product
    of the five base factors). The affine maps of that design take any five independent columns to
    the base factors, so searching the deletions that keep the base ones searches them all."""
    odd = ["123", "124", "125", "134", "135", "145", "234", "235", "245", "345", "12345"]
    for count in range(12, 17):
        assert set(S.GENERATORS[(32, count)]) <= set(odd) and S.SOURCES[(32, count)] == S.CHEN_CHENG
        ours = S.word_length_pattern(count, 32)
        for chosen in itertools.combinations(odd, count - 5):
            original = S.GENERATORS[(32, count)]
            S.GENERATORS[(32, count)] = chosen
            try:
                other = S.word_length_pattern(count, 32)
            finally:
                S.GENERATORS[(32, count)] = original
            assert ours[2:] <= other[2:], (count, chosen)
    assert S.word_length_pattern(16, 32)[3] == 140  # the 140 planes of AG(4, 2): the saturated design's four-letter words


# --- the sample -------------------------------------------------------------------------------------


def test_a_sample_draws_distinct_cells_balanced_across_each_factors_levels():
    raw = {**factors(8), "age_pair": ["same", "p1_older", "p2_older"], "task": ["none", "p1_urgent", "p2_urgent"]}
    del raw["urgency"]
    found = design(kind="sample", cells=20, factors=raw)
    cells = found.cell_list()
    assert len(cells) == found.cells() == 20 and len({json.dumps(cell, sort_keys=True) for cell in cells}) == 20
    for name in found.screened:
        counts = Counter(json.dumps(cell[name]) for cell in cells)
        assert len(counts) == len(found.levels[name]) and max(counts.values()) - min(counts.values()) <= 1, (name, counts)
    every = math.prod(len(found.levels[name]) for name in found.factors)
    assert design(kind="sample", cells=every, factors=raw).cell_list() == design(factors=raw).cell_list()  # all of it: the full factorial


def test_the_same_seed_gives_the_same_design_and_another_seed_another_sample():
    raw = {"kind": "sample", "cells": 32, "factors": factors(12), "exact_repeats": {"cells": 8, "times": 3}}
    one, two = design(**raw), design(**raw)
    assert one.cell_list() == two.cell_list()
    assert one.exact_repeat_plan(one.cell_list(), ["a", "b"]) == two.exact_repeat_plan(two.cell_list(), ["a", "b"])
    assert D.ResolutionDesign.from_config({**raw, "seed": 8}).cell_list() != one.cell_list()
    fractional = {"kind": "fractional", "factors": factors(12)}
    assert design(**fractional).cell_list() == design(**fractional).cell_list()
    sessions = [D.sessions_for(CASES, design(**raw), ["talk"], "x") for _ in range(2)]
    assert [s.as_dict() for s in sessions[0]] == [s.as_dict() for s in sessions[1]]


# --- geometries and the exact-repeat set ------------------------------------------------------------


def test_every_factor_level_meets_every_geometry_equally_often():
    found = design(kind="fractional", factors=factors(12), geometries=["head_on_aaaaaaaa", "head_on_bbbbbbbb"], exact_repeats={"cells": 8, "times": 3})
    sessions = D.sessions_for(CASES, found, ["independent", "talk"], "x", {"head_on_aaaaaaaa": "layout=aligned", "head_on_bbbbbbbb": "layout=apart_20cm"})
    design_sessions = [s for s in sessions if s.repeat == 1 and s.pair_id is None]
    assert len(design_sessions) == 32 * 2 * 2
    for condition in ("independent", "talk"):
        mine = [s for s in design_sessions if s.condition == condition]
        for name in found.screened:
            counts = Counter((s.geometry, s.cell[name]) for s in mine)
            assert len(counts) == 2 * 2 and set(counts.values()) == {16}, (name, counts)
    assert {s.geometry for s in sessions} == {"layout=aligned", "layout=apart_20cm"}
    assert all(s.as_dict()["geometry"] == s.geometry for s in sessions)


def test_the_exact_repeat_set_is_balanced_and_runs_on_one_geometry_per_cell():
    found = design(kind="fractional", factors=factors(12), exact_repeats={"cells": 8, "times": 3})
    sessions = D.sessions_for(CASES, found, ["independent", "non_verbal", "talk"], "x")
    assert len(sessions) == 3 * (32 * 2 + 8 * 2)
    for condition in ("independent", "non_verbal", "talk"):
        in_set = [s for s in sessions if s.condition == condition and s.exact_repeat_set]
        assert len(in_set) == 8 * 3 and sorted(Counter(s.repeat for s in in_set).values()) == [8, 8, 8]
        by_cell = {}
        for s in in_set:
            by_cell.setdefault(D.cell_code(s.cell), set()).add(s.case_id)
        assert len(by_cell) == 8 and all(len(cases) == 1 for cases in by_cell.values())  # one geometry per cell
        assert sorted(Counter(next(iter(cases)) for cases in by_cell.values()).values()) == [4, 4]  # the geometries in turn
        firsts = [s.cell for s in in_set if s.repeat == 1]
        for name in found.screened:
            assert sorted(Counter(cell[name] for cell in firsts).values()) == [4, 4], name
        assert not [s for s in sessions if s.condition == condition and not s.exact_repeat_set and s.repeat > 1]
    # the same cells in every condition
    chosen = {cond: {(D.cell_code(s.cell), s.case_id) for s in sessions if s.condition == cond and s.repeat == 3} for cond in ("independent", "talk")}
    assert chosen["independent"] == chosen["talk"]


def test_the_exact_repeat_sessions_of_one_cell_send_byte_identical_prompts(tmp_path):
    config = E.ResolutionConfig.from_raw({
        "layer": "resolution", "experiment_name": "repeats", "conditions": ["non_verbal"],
        "design": {"seed": 3, "kind": "sample", "cells": 2, "geometries": ["head_on_02dfbadb@2"], "exact_repeats": {"cells": 1, "times": 3},
                   "factors": {"age_pair": ["same", "p1_older"], "gender_pair": ["p1_female"], "task": ["p1_urgent"],
                               "demographics_visible": [True], "mapping": ["p1_lower"]}},
        "llm": {"client": "mock", "mock_policy": "resolution_rehearsal_v1"},
    })
    client = MockClient(policy=POLICIES["resolution_rehearsal_v1"])
    result = E.run_resolution(config, client=client, out_root=tmp_path, report=lambda _: None, git=GIT)
    assert result.status == E.STATUS_COMPLETED and len(result.executed) == 4
    sent: dict[str, list[str]] = {}
    for request in client.requests:
        sent.setdefault(request.metadata["session_id"], []).append(json.dumps(list(request.messages), ensure_ascii=False))
    repeated = sorted(sid for sid in sent if re.search(r"_r[23]$", sid))
    assert len(repeated) == 2
    first = repeated[0][:-1] + "1"
    assert sent[first] and all(sent[sid] == sent[first] for sid in repeated)  # byte for byte, every call
    other = next(sid for sid in sent if sid not in repeated and sid != first)
    assert sent[other] != sent[first]
    rows = [json.loads(line) for line in (result.experiment_dir / E.OUTCOMES_JSONL).read_text(encoding="utf-8").splitlines()]
    assert {row["geometry"] for row in rows} == {"layout=apart_20cm"} and sum(row["exact_repeat_set"] for row in rows) == 3


# --- counterfactual pairs ---------------------------------------------------------------------------


BASE = {"age_pair": "same", "gender_pair": "p1_female", "urgency": "neither", "mobility_aid": "neither", "load": "neither",
        "distraction": "neither", "assertiveness": "neither", "residence": "neither", "memory_note": "neither",
        "demographics_visible": True, "mobility_aid_visible": True, "load_visible": True, "surroundings": "quiet",
        "time_of_day": "daytime", "familiarity": "strangers", "mapping": "p1_higher"}


def test_a_counterfactual_pair_is_two_sessions_identical_but_for_one_factor():
    found = design(kind="fractional", factors=factors(16), counterfactual_pairs=[{"base": BASE, "factor": "urgency"}, {"base": BASE, "factor": "age_pair", "to": "p2_older"}])
    sessions = D.sessions_for(CASES, found, ["independent", "talk"], "x")
    paired = [s for s in sessions if s.pair_id is not None]
    assert len(paired) == 2 * 2 * 2 * 2  # pairs x cases x conditions x two sessions
    by_pair: dict[str, list[D.Session]] = {}
    for s in paired:
        by_pair.setdefault(s.pair_id, []).append(s)
    assert len(by_pair) == 8
    for pair_id, (one, two) in by_pair.items():
        base, flipped = sorted((one, two), key=lambda s: s.pair_role)
        assert (base.pair_role, flipped.pair_role) == ("base", "flipped") and base.pair_factor == flipped.pair_factor
        assert (base.case_id, base.case_version, base.condition, base.agents, base.scenario) == (flipped.case_id, flipped.case_version, flipped.condition, flipped.agents, flipped.scenario)
        differs = [name for name in base.cell if base.cell[name] != flipped.cell[name]]
        assert differs == [base.pair_factor] and base.cell["mapping"] == flipped.cell["mapping"] == "p1_higher"
        assert base.cell == {**BASE} and base.repeat == flipped.repeat == 1 and not base.exact_repeat_set
        assert pair_id.startswith(f"{D.CONDITION_LETTER[base.condition]}_{base.case_id}_x")
        assert base.as_dict()["pair_id"] == pair_id and base.as_dict()["pair_role"] == "base"
    urgency = next(s for s in paired if s.pair_factor == "urgency" and s.pair_role == "flipped")
    person1, person2 = urgency.persons
    assert urgency.personas[person1]["urgency"] == "urgent" and urgency.personas[person2]["urgency"] == "routine"
    assert {s.pair_factor for s in paired} == {"urgency", "age_pair"}
    assert not [s for s in sessions if s.pair_id is None and "pair_id" in s.as_dict()]


@pytest.mark.parametrize("pair, message", [
    ({"base": BASE, "factor": "mapping"}, "same mapping"),
    ({"base": {**BASE, "urgency": "p2"}, "factor": "load"}, "one of the design's levels"),
    ({"base": {k: v for k, v in BASE.items() if k != "load"}, "factor": "urgency"}, "missing required key"),
    ({"base": BASE, "factor": "age_pair"}, "name the one to flip to"),
    ({"base": BASE, "factor": "urgency", "to": "neither"}, "other than the base's"),
    ({"base": BASE, "factor": "distraction_visible"}, "a factor the design names"),
])
def test_a_bad_counterfactual_pair_is_refused(pair, message):
    with pytest.raises(ConfigError, match=message):
        design(kind="fractional", factors=factors(16), counterfactual_pairs=[pair])
    with pytest.raises(ConfigError, match="listed twice"):
        design(kind="fractional", factors=factors(16), counterfactual_pairs=[{"base": BASE, "factor": "urgency"}] * 2)


# --- the experiment layer ---------------------------------------------------------------------------


def screening_config(name="screening", **design_changes):
    return E.ResolutionConfig.from_raw({
        "layer": "resolution", "experiment_name": name, "conditions": ["independent", "non_verbal", "talk"],
        "design": {"seed": 62, "kind": "fractional", "geometries": HEAD_ON, "exact_repeats": {"cells": 8, "times": 3},
                   "factors": factors(12), **design_changes},
        "llm": {"client": "mock", "mock_policy": "resolution_rehearsal_v1"},
    })


def test_the_geometries_are_the_cases_and_must_be_of_one_encounter_type():
    config = screening_config()
    found = E.plan(config)
    assert sorted(found.cases) == ["head_on_02dfbadb", "head_on_de176842"]
    assert len(found.sessions) == 3 * (32 * 2 + 8 * 2)
    assert {s.geometry for s in found.sessions} == {"layout=aligned", "layout=apart_20cm"}
    with pytest.raises(ConfigError, match="one encounter type"):
        E.plan(screening_config(geometries=["head_on_02dfbadb@2", "passage_36a66c39@1"]))
    with pytest.raises(ConfigError, match="cases may then give only the store"):
        E.ResolutionConfig.from_raw({**config_raw(), "cases": {"ids": ["head_on_02dfbadb@2"]}})
    with pytest.raises(ConfigError, match="or list design.geometries"):
        E.ResolutionConfig.from_raw({**config_raw(), "design": {"seed": 1, "factors": factors(8)}})


def config_raw():
    return {"layer": "resolution", "experiment_name": "raw", "conditions": ["talk"],
            "design": {"seed": 1, "factors": factors(8), "geometries": HEAD_ON}, "llm": {"client": "mock"}}


def test_plan_prints_the_kind_cells_geometries_exact_repeats_pairs_and_the_worst_case_cost():
    said: list[str] = []
    E.print_plan(screening_config(counterfactual_pairs=[{"base": {k: v for k, v in BASE.items() if k in factors(12) and len(factors(12)[k]) > 1}, "factor": "urgency"}]), out=said.append)
    text = "\n".join(said)
    assert "design: fractional, a 2^(12-7) fraction of 12 two-level factor(s), resolution 4; 32 cell(s) per case and condition" in text
    assert "geometries: 2, every cell once on each: head_on_02dfbadb (layout=apart_20cm), head_on_de176842 (layout=aligned)" in text
    assert "exact-repeat set: 8 cell(s), each run 3 times in all on one geometry: 48 session(s) more" in text
    assert "counterfactual pairs: 1 (flipping urgency)" in text
    assert "talk: 84 session(s): 64 of the design, 16 exact repeat(s), 4 in pairs" in text
    assert "worst-case cost USD" in text and "talk: 84 session(s), USD" in text and "per session at most 8 call(s)" in text


# --- what stays as it was ---------------------------------------------------------------------------


def old_sessions_for(cases, found, conditions, experiment):
    """The session list as RF-3 built it, before issue #62 (``design.py`` at commit 8e67310)."""
    unordered = []
    for condition in conditions:
        for case_id, version, agents, scenario in cases:
            for values in itertools.product(*(found.levels[name] for name in found.factors)):
                cell = dict(zip(found.factors, values))
                for repeat in range(1, found.repeats + 1):
                    unordered.append((f"{D.CONDITION_LETTER[condition]}_{case_id}_{D.cell_code(cell)}_r{repeat}", cell, repeat))
    order = sorted(unordered, key=lambda entry: entry[0])
    random.Random(f"{experiment}:{found.seed}").shuffle(order)
    return order


@pytest.mark.parametrize("path", [
    "configs/resolution/resolve_mock_rehearsal.yaml",
    "configs/resolution/resolve_factors_mock_rehearsal.yaml",
    "configs/resolution/resolve_pairwise_mock_rehearsal.yaml",
])
def test_a_config_without_design_kind_gives_the_cells_and_session_ids_it_gave_before(path):
    config = E.ResolutionConfig.load(path)
    assert config.design.kind == D.KIND_FULL and "kind" not in config.as_dict()["design"]
    assert set(config.as_dict()["design"]) == {"seed", "factors", "repeats", "base_age", "age_difference", "tasks"}
    found = E.plan(config)
    cases = [(case_id, case["version"], tuple(case["agents"]), found.scenarios[case_id]) for case_id, case in found.cases.items()]
    old = old_sessions_for(cases, config.design, config.conditions, config.experiment_name)
    assert [(s.session_id, s.cell, s.repeat) for s in found.sessions] == old
    for session in found.sessions:
        assert not {"geometry", "pair_id", "pair_role", "pair_factor"} & set(session.as_dict())
    with_kind = E.ResolutionConfig.from_raw({**_raw(path), "design": {**_raw(path)["design"], "kind": "full"}})
    assert [s.as_dict() for s in E.plan(with_kind).sessions] == [s.as_dict() for s in found.sessions]


def _raw(path):
    return load_yaml(resolve_path(path))


def test_the_rehearsal_config_is_round_1s_shape():
    config = E.ResolutionConfig.load("configs/resolution/resolve_screening_mock_rehearsal.yaml")
    found = E.plan(config)
    assert config.design.kind == "fractional" and config.design.cells() == 32 and len(config.design.screened) == 12
    assert len(found.sessions) == 192 + 48 + 12
    assert not config.design.uses_attractiveness  # its ethics sign-off is pending
