"""Issue #60 (RF-5): the core factors (seven person attributes) with their visibility switches, and
the situational factors: their lines in each block of D2, who is told what, the wider body of
``load``, the hearing range of ``surroundings``, the design's coding, the rule check of task 6, and
that everything written before them behaves as before (``docs/resolution.md``, D1, D2, D7, D15)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace

import pytest

from negsim.avoidance.perception import default_visibility
from negsim.configutil import ConfigError
from negsim.negotiation import prompts
from negsim.personas import ATTRIBUTES, FACTOR_ATTRIBUTES, PersonaError, load_personas, validate_persona
from negsim.resolution import design as D
from negsim.resolution import experiment as E
from negsim.resolution import factors as F
from negsim.resolution import protocol as P
from negsim.resolution.prompt import render
from negsim.rulegen.cases import CaseStore
from negsim.rulegen.design import visibility_of
from negsim.rulegen.replay import source_plan
from negsim.rulegen.validate import NEEDS_COMMUNICATION, validate_proposal
from negsim.scenarios.registry import build_crowd_scenario
from test_encounter_protocol import GIT, HEAD_ON, PASSAGE, SLOW, SWERVE_LEFT, session_on, small_config
from test_perceive import ME, PASSING, V2, at, look, perceiver
from test_resolution import GROUP_WORDS, ORDER_WORDS, SUGGESTIONS
from test_rulegen_validate import rule, when

TEMPLATE = F.FactorTemplate.load()
VALUES = F.FactorValues.load()
STORE = CaseStore()
#: Each core factor at its other level, and the block its own line goes to.
MARKED = {name: ATTRIBUTES[name].levels[1] for name in FACTOR_ATTRIBUTES}
EVERYTHING = {0: dict(MARKED), 1: {name: ATTRIBUTES[name].levels[0] for name in FACTOR_ATTRIBUTES}}
SITUATION = {"surroundings": "busy", "time_of_day": "late_night"}


def factors(people=None, visible=None, situation=None):
    return F.SessionFactors(TEMPLATE, EVERYTHING if people is None else people, visible or {}, SITUATION if situation is None else situation)


def blocks(text):
    """The rendered description, block by block: {header: [lines]}."""
    found = {}
    for chunk in text.split("\n\n"):
        lines = chunk.splitlines()
        found[lines[0]] = lines[1:]
    return found


# --- the schema (task 1) ---------------------------------------------------------------------------


def test_the_seven_attributes_are_declared_with_two_levels_and_the_issues_observability():
    expected = {
        "urgency": (("routine", "urgent"), False),
        "mobility_aid": (("none", "cane"), True),
        "load": (("none", "large_suitcase"), True),
        "distraction": (("none", "phone"), True),
        "assertiveness": (("gives_way", "holds_ground"), False),
        "residence": (("local", "visitor"), False),
        "memory_note": (("none", "bad_experience"), False),
    }
    assert FACTOR_ATTRIBUTES == tuple(expected)
    for name, (levels, observable) in expected.items():
        spec = ATTRIBUTES[name]
        assert (spec.levels, spec.observable, spec.required, spec.fill_default) == (levels, observable, False, False)


def test_a_persona_takes_the_factors_checks_their_levels_and_spells_them_in_a_derived_id():
    base = {"persona_id": "f25", "age": 25, "gender": "female", "task": "the post office"}
    persona = validate_persona({**base, "mobility_aid": "cane", "residence": "visitor"})
    assert persona.attributes["mobility_aid"] == "cane" and "load" not in persona.attributes
    with pytest.raises(PersonaError, match="mobility_aid"):
        validate_persona({**base, "mobility_aid": "wheelchair"})
    assert persona.with_overrides(load="large_suitcase").persona_id == "f25+load=large_suitcase"


def test_personas_written_before_keep_exactly_their_attributes():
    for persona in load_personas("configs/personas/personas.yaml").values():
        assert set(persona.attributes) <= {"age", "gender", "backstory", "task", "ethnic_group"}
        assert not set(persona.attributes) & set(FACTOR_ATTRIBUTES)


def test_the_older_layers_visibility_settings_are_unchanged():
    assert not set(default_visibility()) & set(FACTOR_ATTRIBUTES)
    assert default_visibility() == prompts.default_visibility()


# --- the template (task 2) -------------------------------------------------------------------------


def test_the_factor_template_is_frozen_and_matches_the_schema():
    entry = prompts.load_manifest()[F.FACTOR_TEMPLATE]
    assert entry["kind"] == F.KIND_FACTORS and entry["sha256"] == TEMPLATE.sha256
    for name in FACTOR_ATTRIBUTES:
        assert tuple(TEMPLATE.data["attributes"][name]) == ATTRIBUTES[name].levels
    # every base level of an attribute with a "none" level renders nothing
    for name in ("mobility_aid", "load", "distraction", "memory_note"):
        assert all(TEMPLATE.line(name, "none", kind) is None for kind in F.LINE_KINDS)


def test_the_template_refuses_a_line_others_could_see_for_an_unobservable_attribute():
    data = json.loads(json.dumps(TEMPLATE.data))
    data["attributes"]["assertiveness"]["holds_ground"]["other"] = "They look determined."
    with pytest.raises(ConfigError, match="not observable"):
        F.FactorTemplate(TEMPLATE.key, data, TEMPLATE.sha256)
    data = json.loads(json.dumps(TEMPLATE.data))
    data["attributes"]["load"] = {"none": {}}
    with pytest.raises(ConfigError, match="levels"):
        F.FactorTemplate(TEMPLATE.key, data, TEMPLATE.sha256)


def test_no_factor_line_names_a_convention_an_order_a_group_or_a_place():
    """Issue #32's list of words that hint at a way of settling a meeting, and the order words of D2.
    One exception, the issue's own wording: assertiveness is a disposition to give way or to hold
    one's ground, so its lines say "give way". They appear only when a design varies it."""
    lines = [(name, line.lower()) for name, levels in TEMPLATE.data["attributes"].items() for entry in levels.values() for line in (entry or {}).values()]
    lines += [(name, line.lower()) for name, levels in TEMPLATE.data["situations"].items() for line in levels.values()]
    for name, line in lines:
        for word in (*ORDER_WORDS, *SUGGESTIONS, *GROUP_WORDS, "left", "right", "keep", "side", "corridor", "passage", "queue", "train"):
            if name == "assertiveness" and word == "give way":
                continue
            assert word.lower() not in line, (word, line)


# --- every line in its block (task 8) --------------------------------------------------------------


@pytest.mark.parametrize("name", [name for name in FACTOR_ATTRIBUTES if name != "urgency"])
def test_every_attribute_renders_in_its_own_agents_view(name):
    mine = factors({0: {name: MARKED[name]}}, situation={})
    view = look([at(0, 0.0, 0.0), at(1, 3.0, 0.0, vx=-1.3)], perceiver(), notes=mine.notes(0))
    view = replace(view, me=replace(ME, factor_lines=mine.own(0)))
    described = blocks(render(view, "talk", PASSING, V2).user)
    kind = "note" if name == "memory_note" else "self"
    line = TEMPLATE.line(name, MARKED[name], kind)
    if kind == "self":
        assert line in described["ABOUT YOU"]
    else:
        assert f"- {line}" in described["YOUR NOTES"] and "YOUR NOTES" not in render(replace(view, notes=()), "talk", PASSING, V2).user


def test_urgency_has_no_line_of_its_own_and_picks_the_errand():
    assert all(TEMPLATE.line("urgency", level, kind) is None for level in ("routine", "urgent") for kind in F.LINE_KINDS)
    design = D.ResolutionDesign.from_config({"seed": 1, "factors": {
        "age_pair": ["same"], "gender_pair": ["same_female"], "urgency": ["neither", "p1"], "demographics_visible": [True], "mapping": ["p1_lower"]}})
    sessions = D.sessions_for([("c", 1, (0, 1), "passing")], design, ["talk"], "x")
    by_level = {s.cell["urgency"]: s.personas for s in sessions}
    assert by_level["neither"][0]["task"] == by_level["neither"][1]["task"] == design.tasks["routine"]
    assert (by_level["p1"][0]["task"], by_level["p1"][0]["urgency"]) == (design.tasks["urgent"], "urgent")
    assert (by_level["p1"][1]["task"], by_level["p1"][1]["urgency"]) == (design.tasks["routine"], "routine")


@pytest.mark.parametrize("where, shown", [
    ((3.0, 0.0), True),     # in view, within 5 m: full detail
    ((3.0, 180.0), False),  # behind: not in view
    ((8.0, 0.0), False),    # in view, beyond 5 m: one short line (D2), no factor lines
])
def test_an_observable_line_reaches_the_other_only_in_view_in_full_detail_and_with_its_switch_on(where, shown):
    for switch in (True, False):
        mine = factors({1: {"mobility_aid": "cane", "load": "large_suitcase", "distraction": "phone"}}, {"load": switch}, situation={})
        distance, degrees = where
        view = look([at(0, 0.0, 0.0, vx=1.3), at(1, distance, degrees, vx=-1.3)], perceiver(), factor_lines=mine.seen_lines())
        text = render(view, "talk", PASSING, V2).user
        assert ("They are walking with a cane." in text) is shown
        assert ("They are looking at their phone as they walk." in text) is shown
        assert ("They are pulling a large suitcase." in text) is (shown and switch)


def test_an_unobservable_attribute_never_reaches_anyone_else():
    hidden = {name: MARKED[name] for name in FACTOR_ATTRIBUTES if not ATTRIBUTES[name].observable}
    mine = factors({1: hidden}, situation={})
    assert mine.seen(1) == () and mine.seen_lines() == {}
    _, record, _ = session_on(HEAD_ON, "talk", {0: SWERVE_LEFT, 1: SLOW}, factors=mine)
    own = [TEMPLATE.line(name, level, kind) for name, level in hidden.items() for kind in F.LINE_KINDS]
    own = [line for line in own if line]
    told = {0: "", 1: ""}
    for point in record["decision_points"]:
        told[point["agent_id"]] += point["prompt"]["messages"][1]["content"]
    assert told[0] and told[1]
    assert all(line in told[1] for line in own)  # person 1 is told its own
    assert not any(line in told[0] for line in own)  # and the other is never told any of it


def test_the_protocol_puts_every_line_where_d2_says_and_the_setting_is_the_same_for_both():
    _, record, _ = session_on(HEAD_ON, "talk", {0: SWERVE_LEFT, 1: SLOW}, factors=factors())
    places = {}
    for point in record["decision_points"]:
        described = blocks(point["prompt"]["messages"][1]["content"])
        agent = point["agent_id"]
        assert described["WHERE YOU ARE"][-2:] == ["- It is busy and noisy around you.", "- It is late at night."]
        places.setdefault(agent, described["WHERE YOU ARE"][-2:])
        if agent == 0:
            for line in factors().own(0):
                assert line in described["ABOUT YOU"]
            assert described["YOUR NOTES"] == ["- " + TEMPLATE.line("memory_note", "bad_experience", "note")]
        else:
            assert described["ABOUT YOU"][-2:] == ["- You are easy-going and tend to give way.", "- You live in Singapore."]
            assert "YOUR NOTES" not in described
    assert places[0] == places[1]


# --- load and surroundings outside the prompt (tasks 3 and 7) --------------------------------------


def test_a_load_widens_the_body_for_the_whole_run_and_both_replays(tmp_path):
    config = factor_config("loaded", factors_={"load": ["p1"], "surroundings": ["busy"]}, conditions=("non_verbal",))
    E.run_resolution(config, out_root=tmp_path, report=lambda _: None, git=GIT)
    folder = tmp_path / "loaded"
    record = json.loads(next((folder / "sessions").glob("*_r1.json")).read_text(encoding="utf-8"))
    radius = build_crowd_scenario(source_plan(HEAD_ON).scenario_config).agents[0].radius
    expected = round(radius + VALUES.load_width_added_m / 2.0, 6)
    assert record["bodies"] == {"0": {"radius_m": expected, "because": "load=large_suitcase"}}
    widths = {round(p["view"]["me"]["width_m"], 6) for p in record["decision_points"] if p["agent_id"] == 0}
    assert widths == {round(2.0 * expected, 6)}  # the same at every decision point: never changed during the run
    for mode in ("plan_only", "plan_orca"):
        config_json = json.loads((folder / "replay" / record["session_id"] / mode / "config.json").read_text(encoding="utf-8"))
        assert config_json["plans"]["bodies"] == record["bodies"]
        assert [a["radius_m"] for a in config_json["scenario"]["agents"]][:2] == [expected, radius]


def test_surroundings_set_the_hearing_range_and_nothing_else_does():
    for level in ("quiet", "busy"):
        mine = factors(situation={"surroundings": level})
        assert mine.hearing_range_m(VALUES) == VALUES.hearing_range_m[level]
    assert factors(situation={"time_of_day": "daytime"}).hearing_range_m(VALUES) is None
    assert VALUES.hearing_range_m["quiet"] > VALUES.hearing_range_m["busy"]


def cases_of(case_set):
    return json.loads((STORE.root / "MANIFEST.json").read_text(encoding="utf-8"))["case_sets"][case_set]["cases"]


@pytest.mark.parametrize("case", cases_of("si32_passage_v1"))
def test_issue_32s_passage_cases_cannot_take_the_wider_body_and_are_refused_before_anything_runs(case):
    """Every one starts the pair 0.1 m apart: a body 0.2 m wider overlaps (asymmetric) or touches
    (symmetric, by rounding), inside the near-miss distance either way."""
    with pytest.raises(ConfigError, match="large suitcase"):
        E.plan(factor_config("tight", ids=(case,), factors_={"load": ["p1"]}))
    E.plan(factor_config("tight_ok", ids=(case,), factors_={"mobility_aid": ["p1"]}))  # no load: it runs as before


@pytest.mark.parametrize("case", cases_of("rf5_passage_v1"))
def test_the_passage_cases_of_issue_60_take_a_loaded_person_whichever_agent_it_is(case):
    E.plan(factor_config("roomy", ids=(case,), factors_={"load": ["p1"], "mapping": ["p1_lower", "p1_higher"]}))


# --- the design (task 5) ---------------------------------------------------------------------------


def factor_config(name, ids=("head_on_02dfbadb@2",), conditions=("independent",), factors_=None):
    base = small_config(name, ids=ids, conditions=conditions)
    raw_factors = {"age_pair": ["same"], "gender_pair": ["p1_female"], "task": ["p1_urgent"], "demographics_visible": [True], "mapping": ["p1_lower"]}
    raw_factors.update(factors_ or {})
    if "urgency" in raw_factors:
        raw_factors.pop("task")
    return E.ResolutionConfig.from_raw({
        "layer": "resolution", "experiment_name": name, "cases": {"ids": list(ids)}, "conditions": list(conditions),
        "design": {"seed": 1, "factors": raw_factors}, "llm": dict(base.llm),
    })


def test_each_factor_is_neither_or_one_agent_and_mapping_says_which():
    config = factor_config("coding", factors_={"assertiveness": ["neither", "p1"], "mapping": ["p1_lower", "p1_higher"]})
    sessions = E.plan(config).sessions
    assert len(sessions) == 4 and config.design.cells() == 4
    for session in sessions:
        first = session.agents[0] if session.cell["mapping"] == "p1_lower" else session.agents[1]
        second = next(agent for agent in session.agents if agent != first)
        assert session.personas[second]["assertiveness"] == "gives_way"
        assert session.personas[first]["assertiveness"] == ("holds_ground" if session.cell["assertiveness"] == "p1" else "gives_way")


def test_the_visibility_switches_are_design_factors_on_unless_switched_off():
    config = factor_config("switches", factors_={"load": ["p1"], "load_visible": [True, False], "mobility_aid": ["p1"]})
    for session in E.plan(config).sessions:
        assert session.visibility["load"] is session.cell["load_visible"]
        assert session.visibility["mobility_aid"] is True  # varied, but its switch left out: on
        assert "distraction" not in session.visibility  # not varied
    with pytest.raises(ConfigError, match="switches load"):
        factor_config("bad", factors_={"load_visible": [True]})


def test_task_and_urgency_are_one_factor_named_one_way():
    with pytest.raises(ConfigError, match="task or urgency"):
        E.ResolutionConfig.from_raw({**json.loads(json.dumps(RAW)), "design": {"seed": 1, "factors": {**RAW["design"]["factors"], "urgency": ["p1"]}}})
    with pytest.raises(ConfigError, match="task or urgency"):
        factors_ = dict(RAW["design"]["factors"])
        factors_.pop("task")
        E.ResolutionConfig.from_raw({**RAW, "design": {"seed": 1, "factors": factors_}})


def test_templates_factors_and_factor_values_are_only_for_a_design_with_factors():
    with pytest.raises(ConfigError, match="factor_values"):
        E.ResolutionConfig.from_raw({**RAW, "factor_values": "configs/resolution/factors_v1.yaml"})
    with pytest.raises(ConfigError, match="factor_values"):
        E.ResolutionConfig.from_raw({**RAW, "templates": {"factors": "resolve_factors_v1"}})


RAW = {
    "layer": "resolution", "experiment_name": "raw", "cases": {"ids": ["head_on_02dfbadb@2"]}, "conditions": ["talk"],
    "design": {"seed": 1, "factors": {"age_pair": ["same"], "gender_pair": ["p1_female"], "task": ["p1_urgent"], "demographics_visible": [True], "mapping": ["p1_lower"]}},
    "llm": {"client": "mock"},
}


def test_the_outcome_row_has_each_factor_and_each_persons_level(tmp_path):
    config = factor_config("row", factors_={"distraction": ["p1"], "time_of_day": ["daytime"], "urgency": ["p1"]})
    E.run_resolution(config, out_root=tmp_path, report=lambda _: None, git=GIT)
    row = json.loads((tmp_path / "row" / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert (row["distraction"], row["time_of_day"], row["urgency"]) == ("p1", "daytime", "p1")
    assert (row["p1_distraction"], row["p2_distraction"], row["p1_urgency"], row["p2_urgency"]) == ("phone", "none", "urgent", "routine")
    assert "task" not in row


def told_counts(record, agent, other):
    """What the views say the agent was told of the other, counted independently of the row."""
    counts = {"age": 0, "gender": 0, "short": 0, "full": 0}
    for point in record["decision_points"]:
        if point["agent_id"] != agent:
            continue
        label = point["view"]["labels"]["label_of_agent"][str(other)]
        for person in point["view"]["seen"]:
            if person["label"] == label:
                counts[person["detail"]] += 1
                counts["age"] += person["detail"] == "full" and person["age"] is not None
                counts["gender"] += person["detail"] == "full" and person["gender"] is not None
    return counts


@pytest.mark.parametrize("core", ["resolve_v4", "resolve_v3", "resolve_v2"])
def test_the_outcome_row_counts_what_each_agent_was_told_of_the_other_in_the_head_on_case(tmp_path, core):
    """Issue #63 (RF-8): in round 1's head-on case every decision point is beyond 5 m, so under
    resolve_v2 and resolve_v3 neither is ever told the other's age or gender; resolve_v3 prints the
    observable lines on the short line. Issue #64: resolve_v4 prints age and gender there too."""
    config = factor_config("told", conditions=("independent", "talk"), factors_={"distraction": ["p1"]})
    if core != "resolve_v3":
        config = replace(config, templates={**config.templates, "core": core})
    E.run_resolution(config, out_root=tmp_path, report=lambda _: None, git=GIT)
    for line in (tmp_path / "told" / "outcomes.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        record = json.loads((tmp_path / "told" / "sessions" / f"{row['session_id']}.json").read_text(encoding="utf-8"))
        assert row["encounter_agents"] == ";".join(str(a) for a in record["encounter"]["agents"])
        for me, other in (("p1", "p2"), ("p2", "p1")):
            counts = told_counts(record, row[f"{me}_agent"], row[f"{other}_agent"])
            assert counts["full"] == 0 and row[f"{me}_decision_points"] >= 1
            demographics = counts["short"] if core == "resolve_v4" else 0
            assert row[f"{me}_other_age_shown"] == row[f"{me}_other_gender_shown"] == demographics
            expected = counts["short"] if core != "resolve_v2" else 0
            assert row[f"{me}_other_observable_shown"] == expected
        if core != "resolve_v2":
            assert row["p1_other_observable_shown"] == row["p1_decision_points"]
        if core == "resolve_v4":
            assert row["p1_other_age_shown"] == row["p1_decision_points"] and row["p2_other_gender_shown"] == row["p2_decision_points"]


@pytest.mark.parametrize("visible", [True, False])
def test_within_5_m_the_row_counts_age_and_gender_only_when_the_demographics_are_visible(tmp_path, visible):
    config = factor_config("near", ids=("passage_02fac1e4@1",), factors_={"distraction": ["p1"], "demographics_visible": [visible]})
    E.run_resolution(config, out_root=tmp_path, report=lambda _: None, git=GIT)
    (line,) = (tmp_path / "near" / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()
    row = json.loads(line)
    record = json.loads((tmp_path / "near" / "sessions" / f"{row['session_id']}.json").read_text(encoding="utf-8"))
    for me, other in (("p1", "p2"), ("p2", "p1")):
        counts = told_counts(record, row[f"{me}_agent"], row[f"{other}_agent"])
        assert counts["full"] >= 1
        assert row[f"{me}_other_age_shown"] == row[f"{me}_other_gender_shown"] == (counts["full"] if visible else 0)
        assert row[f"{me}_other_observable_shown"] == counts["full"] + counts["short"]


def test_a_design_without_factors_has_the_age_and_gender_counts_but_no_observable_count(tmp_path):
    E.run_resolution(small_config("plain", conditions=("independent",)), out_root=tmp_path, report=lambda _: None, git=GIT)
    row = json.loads((tmp_path / "plain" / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert {"p1_other_age_shown", "p2_other_gender_shown", "encounter_agents"} <= set(row)
    assert "p1_other_observable_shown" not in row


def test_the_cost_preview_counts_the_factor_lines(tmp_path):
    plain = E.plan(factor_config("p0", factors_={"mobility_aid": ["neither"]})).preview
    full = {name: ["p1"] for name in FACTOR_ATTRIBUTES}
    full.update({"surroundings": ["quiet"], "time_of_day": ["late_night"]})
    loaded = E.plan(factor_config("p1", factors_=full, conditions=("independent",))).preview
    assert loaded["per_session"][0]["S_decision_tokens"] > plain["per_session"][0]["S_decision_tokens"]
    result = E.run_resolution(factor_config("bound", factors_=full), out_root=tmp_path, report=lambda _: None, git=GIT)
    assert result.summary["largest_share_of_the_preview_used"] <= 1.0


# --- validation (task 6) ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["assertiveness", "residence", "memory_note"])
def test_a_rule_reading_an_attribute_nobody_else_can_see_needs_communication(name):
    for prefix in ("either", "both"):
        result = validate_proposal(rule(when=when({"field": f"{prefix}.{name}", "op": "==", "value": MARKED[name]})), default_visibility())
        assert (result.category, result.loader_category) == (NEEDS_COMMUNICATION, "unobservable_field"), result.message


# --- what was written before (task 8) --------------------------------------------------------------


def test_configs_written_before_plan_and_describe_themselves_exactly_as_before():
    config = E.ResolutionConfig.load("configs/resolution/resolve_mock_rehearsal.yaml")
    assert not config.design.uses_factors and config.factor_values is None
    assert set(config.as_dict()) == {"experiment_name", "description", "source", "cases", "scenarios", "conditions", "design", "protocol", "templates", "llm_view", "llm", "budget"}
    assert config.templates == {"core": "resolve_v2", "debrief": "resolve_debrief_v1"}
    assert list(config.design.as_dict()["factors"]) == list(D.FACTORS)
    for session in E.plan(config).sessions:
        # the cell code is the hash of the five factors of issue #58, as it was
        old = hashlib.sha256(json.dumps({name: session.cell[name] for name in D.FACTORS}, sort_keys=True).encode("utf-8")).hexdigest()[:8]
        assert session.session_id.split("_")[-2] == old and list(session.cell) == list(D.FACTORS)
        assert all(set(persona) == {"age", "gender", "task", "urgency"} for persona in session.personas.values())
        assert session.visibility == visibility_of(session.cell) and not session.uses_factors


def test_a_session_without_factors_records_and_renders_as_before():
    _, record, _ = session_on(HEAD_ON, "talk", {0: SWERVE_LEFT, 1: SLOW})
    _, again, _ = session_on(HEAD_ON, "talk", {0: SWERVE_LEFT, 1: SLOW}, factors=None)
    strip = lambda r: [(p["prompt"]["messages"], p["view"]) for p in r["decision_points"]]  # noqa: E731
    assert strip(record) == strip(again)
    for point in record["decision_points"]:
        assert not point["view"]["me"]["factor_lines"] and not point["view"]["notes"]
        assert "YOUR NOTES" not in point["prompt"]["messages"][1]["content"]


def test_the_templates_written_before_are_unchanged():
    manifest = prompts.load_manifest()
    assert manifest["resolve_v1"]["sha256"] == "5855543924a71def16eb7a9005d6f0ea9848e201a82d60cca5d87128c8c03fe8"
    assert manifest["resolve_v2"]["sha256"] == "cea7f2d647746bdaf56c99a0225ad8681c451ef7ed3a436b5ca946309711a4cb"
    assert manifest["scenario_passing_v1"]["sha256"] == "f3ca88c2339157406812cd80c1e1fd011c00caf727b88104e3e0b8b93d8ff422"
