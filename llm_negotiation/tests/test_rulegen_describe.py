"""Issue #30, Part 4: situation descriptions, the field glossary and the format example."""

from __future__ import annotations

import copy
import json
import math
import re

import pytest

from negsim.configutil import PACKAGE_ROOT
from negsim.negotiation import prompts
from negsim.negotiation.prompts import TemplateIntegrityError
from negsim.rules import fields
from negsim.rulegen import describe
from negsim.rulegen.cases import CASES_ROOT, CaseStore
from negsim.rulegen.describe import KIND_NEGOTIATE, KIND_STATE, load_templates
from negsim.rulegen.design import DesignSettings, sessions_for

A = load_templates("rulegen_negotiate_v1", KIND_NEGOTIATE)
B = load_templates("rulegen_state_v1", KIND_STATE)
STORE = CaseStore(CASES_ROOT)
CASES = {case_id: STORE.get(case_id, version) for case_id, version in STORE.case_set("si3_v1")}


def session(case, condition="negotiated", **levels):
    chosen = {
        "age_pair": "p1_older", "gender_pair": "p1_female", "task": "p1_urgent",
        "demographics_visible": True, "mapping": "p1_lower", "order": "lower_first", **levels,
    }
    settings = DesignSettings.from_config({"seed": 1, "factors": {name: [value] for name, value in chosen.items()}})
    (found,) = sessions_for([(case["case_id"], 1, tuple(case["agents"]))], settings, [condition], {}, "test")
    return found


# --- frozen ------------------------------------------------------------------------------------


def test_the_templates_are_frozen_with_the_tool_of_issue_24():
    manifest = prompts.load_manifest()
    for key, kind in (("rulegen_common_v1", "rule_generation_common"), ("rulegen_negotiate_v1", KIND_NEGOTIATE), ("rulegen_state_v1", KIND_STATE)):
        assert manifest[key]["kind"] == kind
    assert A.common_key == B.common_key == "rulegen_common_v1" and A.identity()["uses"]["sha256"] == manifest["rulegen_common_v1"]["sha256"]
    assert "rulegen_negotiate_v1" not in prompts.available_templates()  # not offered to negotiation experiments


def test_a_changed_field_catalogue_or_schema_is_refused(monkeypatch):
    spec = fields.PAIR_FIELDS["distance_m"]
    monkeypatch.setitem(fields.PAIR_FIELDS, "distance_m", spec.__class__(**{**spec.__dict__, "meaning": "how far apart, more or less"}))
    with pytest.raises(TemplateIntegrityError, match="not the one it was frozen with"):
        load_templates("rulegen_negotiate_v1", KIND_NEGOTIATE)


def test_an_edited_template_is_refused(tmp_path, monkeypatch):
    import shutil

    copy_dir = tmp_path / "templates"
    shutil.copytree(prompts.TEMPLATE_DIR, copy_dir)
    monkeypatch.setattr(prompts, "TEMPLATE_DIR", copy_dir)
    monkeypatch.setattr(prompts, "MANIFEST_PATH", copy_dir / "MANIFEST.json")
    path = copy_dir / "rulegen_state_v1.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("State one rule", "State one fair rule"), encoding="utf-8")
    with pytest.raises(TemplateIntegrityError, match="has been edited"):
        load_templates("rulegen_state_v1", KIND_STATE)


# --- every scenario type, both perspectives ----------------------------------------------------


@pytest.mark.parametrize("case_id", sorted(CASES))
def test_every_case_renders_in_both_conditions(case_id):
    case = CASES[case_id]
    a, b = session(case), session(case, "stated")
    for agent in case["agents"]:
        text = describe.first_person(case, a, agent, A)
        assert text.startswith("ABOUT YOU") and "THE OTHER PERSON" in text
    text = describe.third_person(case, b, B)
    assert "PERSON 1" in text and "PERSON 2" in text and "THE TWO OF THEM" in text
    for prompt in (describe.negotiation_prompt(case, a, case["agents"][0], A), describe.statement_prompt(case, b, B)):
        assert "{" + "situation" + "}" not in prompt and "THE RULE FORMAT" in prompt and "HOW TO REPLY" in prompt


def test_the_five_scenario_types_are_told_by_what_can_be_seen():
    by_type = {}
    for case in CASES.values():
        by_type.setdefault(case["scenario"]["type"], case)
    text = {name: describe.first_person(case, session(case), case["agents"][0], A) for name, case in by_type.items()}
    assert "passage 1.75 m wide" in text["wide_corridor_head_on"] and "in the opposite direction to you" in text["wide_corridor_head_on"]
    assert "no walls near you" in text["open_crossing"] and "across your direction of travel" in text["open_crossing"]
    assert "in the same direction as you" in text["overtaking"]
    assert re.search(r"ahead of you, the passage narrows to 0\.80 m for 4\.0 m", text["corridor_to_bottleneck"])
    assert "Other people are walking around you as well." in text["bidirectional_flow"] and "passage 4.00 m wide" in text["bidirectional_flow"]
    for words in text.values():
        assert re.search(r"They are \d+\.\d m away", words)  # distances along the way to 0.1 m
        assert re.search(r"walking at \d\.\d\d m/s", words) and re.search(r"Your body is \d\.\d\d m wide", words)


# --- what each condition is told ------------------------------------------------------------------


def test_first_person_tells_nothing_about_the_other_that_cannot_be_seen():
    case = copy.deepcopy(CASES[next(case_id for case_id in CASES if case_id.startswith("bottleneck"))])
    me, them = case["agents"]
    # Give the other person things nobody else can see, each recognisable if it leaked.
    case["bodies"][str(them)].update(preferred_speed_mps=1.37, max_speed_mps=2.71)
    case["observations"][str(them)]["observer"]["preferred_speed_mps"] = 1.37
    case["observations"][str(them)]["environment"].update(free_width_left_m=3.33, free_width_right_m=4.44, nearest_wall_distance_m=3.33)
    a = session(case, task="p2_urgent")
    a.personas[them]["task"] = "a very particular errand"
    text = describe.first_person(case, a, me, A)
    for secret in ("1.37", "2.71", "3.33", "4.44", "a very particular errand", "urgent", "routine"):
        assert secret not in text, secret
    assert "You do not know where they are going" in text
    # The other agent's own description does show what it knows of itself.
    theirs = describe.first_person(case, a, them, A)
    assert "1.37" in theirs and "a very particular errand" in theirs and "3.33" in theirs


def test_third_person_shows_both_peoples_private_information_in_the_session_order():
    case = CASES[next(case_id for case_id in CASES if case_id.startswith("head_on"))]
    lower, higher = case["agents"]
    b = session(case, "stated", task="p1_urgent", order="higher_first")
    text = describe.third_person(case, b, B)
    assert "Person 1 is on their way to the supermarket." in text  # person 1 is the higher agent, with the routine errand
    assert "Person 2 is on their way to the emergency room." in text
    assert text.index("PERSON 1") < text.index("25 years old") < text.index("PERSON 2") < text.index("70 years old")
    a = session(case, task="p1_urgent")
    assert "the supermarket" not in describe.first_person(case, a, lower, A)  # the other's errand: never in condition A


@pytest.mark.parametrize("condition", ["negotiated", "stated"])
def test_hidden_demographics_appear_in_neither_the_situation_nor_the_glossary(condition):
    for case in CASES.values():
        s = session(case, condition, demographics_visible=False)
        prompt = describe.statement_prompt(case, s, B) if condition == "stated" else describe.negotiation_prompt(case, s, case["agents"][0], A)
        for word in ("years old", "woman", "female", "gender", "age (years)", "age_difference_years", "look like"):
            assert word not in prompt, (case["case_id"], word)
    shown = describe.negotiation_prompt(case, session(case), case["agents"][0], A)
    assert "years old" in shown and "gender (one of" in shown and "pair.age_difference_years" in shown


def test_both_conditions_get_the_same_glossary_and_format_example():
    case = next(iter(CASES.values()))
    a, b = describe.negotiation_prompt(case, session(case), case["agents"][0], A), describe.statement_prompt(case, session(case, "stated"), B)
    for visible in (True, False):
        glossary = describe.glossary_text(A.common, visible)
        assert glossary == describe.glossary_text(B.common, visible)
    assert describe.glossary_text(A.common, True) in a and describe.glossary_text(A.common, True) in b
    assert describe.format_example_text(A.common) in a and describe.format_example_text(A.common) in b


# --- neutral wording -------------------------------------------------------------------------------

#: Words that would describe or hint at a way of settling a meeting.
SUGGESTIONS = (
    "keep left", "keep right", "keep to the", "to the left", "to the right", "give way", "giving way", "right of way",
    "yield", "courtesy", "polite", "elder", "seniority", "convention", "custom", "should go", "ought", "fair", "etiquette",
    "first come", "ladies", "respect",
)


def test_no_template_and_no_prompt_suggests_what_a_rule_should_say():
    """Everything a model is shown: every rendered prompt, and every line of a turn."""
    texts = [json.dumps(A.data["turns"]).lower(), B.data["retry"].lower()]
    for case in CASES.values():
        texts.append(describe.negotiation_prompt(case, session(case), case["agents"][0], A).lower())
        texts.append(describe.statement_prompt(case, session(case, "stated"), B).lower())
    for text in texts:
        for phrase in SUGGESTIONS:
            assert phrase not in text, phrase
        assert "{name}" not in text  # no personal names, as in issue #24's templates


def test_the_format_example_is_a_placeholder_and_no_real_rule():
    example = json.loads(A.common["format_example"]["text"])
    leaves = []

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                leaves.append(key)
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        else:
            leaves.append(value)

    walk(example)
    names = set(fields.PAIR_FIELDS) | set(fields.AGENT_FIELDS) | {"side_preference", "responsibility_share", "speed_scale", "clearance_margin", "passage_order"}
    for leaf in leaves:
        assert not any(re.search(rf"{name}", str(leaf)) for name in names), leaf
        assert str(leaf).startswith("<") or leaf in ("encounter", "when", "all", "field", "op", "value", "unit", "roles", "by", "order", "assign", "tie", "directive", "priority", "intent", "no_match"), leaf


# --- the glossary is generated, in a fixed order, from the documented catalogue -----------------------


def test_the_glossary_lists_every_field_in_the_catalogues_order():
    glossary = describe.glossary_text(A.common, True)
    # A common template describes one version of the rule format (issue #32): version 1 describes
    # rule schema 2, so its glossary lists the fields of version 2, and no later field.
    pair_fields, agent_fields = fields.fields_of(describe.rule_schema_version_of(A.common))
    assert describe.rule_schema_version_of(A.common) == 2 and "in_segment" not in glossary
    positions = [glossary.index(f"- pair.{name} (") for name in pair_fields]
    assert positions == sorted(positions)
    agent_part = glossary[glossary.index("Fields of each person"):]
    positions = [agent_part.index(f"- {name} (") for name in agent_fields]
    assert positions == sorted(positions)
    hidden = describe.glossary_text(A.common, False)
    assert "pair.age_difference_years" not in hidden and "- age (" not in hidden and "- gender (" not in hidden
    for name in ("distance_m", "time_to_collision_s", "min_corridor_width_m"):
        assert f"pair.{name}" in hidden


def test_the_catalogue_and_its_documentation_agree():
    """The glossary is generated from the catalogue; the tables of rule-format.md, section 5,
    document it. Every field and unit must be the same in both."""
    document = (PACKAGE_ROOT / "docs" / "rule-format.md").read_text(encoding="utf-8")
    section = document[document.index("## 5. What a rule may read"):document.index("## 6. Roles")]
    rows = re.findall(r"^\| `([a-z_]+)` \| ([^|]+) \|", section, re.M)
    documented = {name: unit.strip() for name, unit in rows if name in fields.PAIR_FIELDS or name in fields.AGENT_FIELDS}
    assert set(documented) == set(fields.PAIR_FIELDS) | set(fields.AGENT_FIELDS)
    for name, unit in documented.items():
        spec = fields.PAIR_FIELDS.get(name) or fields.AGENT_FIELDS[name]
        assert (unit.startswith("name") and spec.kind == "category") or (unit == "true/false" and spec.kind == "boolean") or unit == spec.unit, name


@pytest.mark.parametrize(
    "bearing, words",
    [(0.0, "straight ahead of you"), (math.pi, "straight behind you"), (math.radians(30), "ahead of you and 30° to your left"),
     (math.radians(-90), "to your right"), (math.radians(-150), "behind you and 30° to your right"), (math.radians(4), "straight ahead of you")],
)
def test_directions(bearing, words):
    assert describe._direction(bearing, A.data["situation"]["directions"]) == words


@pytest.mark.parametrize(
    "relative, words",
    [(0.05, "in the same direction as you"), (math.pi, "in the opposite direction to you"),
     (math.pi / 2, "across your direction of travel from your right to your left, at 90° to it"),
     (-math.radians(45), "across your direction of travel from your left to your right, at 45° to it")],
)
def test_headings(relative, words):
    assert describe._heading(relative, A.data["situation"]["headings"]) == words
