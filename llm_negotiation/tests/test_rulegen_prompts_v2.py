"""Issue #32, Part 3: prompt version 2. The frozen templates, the glossary of rule format 3, how
a meeting inside a single-file passage is told, and a person's fictional group: stated when the
session shows it, and nowhere at all when it does not."""

from __future__ import annotations

import json

import pytest

from helpers import crowd
from negsim.avoidance.perception import default_visibility, perceive
from negsim.negotiation import prompts
from negsim.personas.groups import DEFAULT_GROUP_LABELS
from negsim.rules import fields
from negsim.rulegen import describe
from negsim.rulegen.cases import CASES_ROOT, CaseStore
from negsim.rulegen.describe import KIND_NEGOTIATE, KIND_STATE, load_templates
from negsim.rulegen.design import DesignSettings, sessions_for

A1, B1 = load_templates("rulegen_negotiate_v1", KIND_NEGOTIATE), load_templates("rulegen_state_v1", KIND_STATE)
A2, B2 = load_templates("rulegen_negotiate_v2", KIND_NEGOTIATE), load_templates("rulegen_state_v2", KIND_STATE)
SUGGESTIONS = (
    "keep left", "keep right", "keep to the", "to the left", "to the right", "give way", "giving way", "right of way",
    "yield", "courtesy", "polite", "elder", "seniority", "convention", "custom", "should go", "ought", "fair", "etiquette",
    "first come", "ladies", "respect", "shorter", "less far", "further in",
)
GROUP_WORDS = (*DEFAULT_GROUP_LABELS, "ethnic", "belong", "community")


def passage_case(name="passage_meet_with_speeds_v1", **overrides):
    """A case as the store keeps one, built from the scenario's first step: both inside the passage."""
    spec = crowd(name, **overrides)
    world = spec.build_world()
    a, b = world.agents
    visibility = default_visibility()

    def record(observer, neighbour):
        stretches = [(entry, out) for _, entry, out in observer.spec.single_file_stretches]
        return perceive(0, 0.0, observer, neighbour, world.obstacles, visibility, {}, observer.spec.preferred_speed, stretches, 12.5, segments=spec.single_file_segments)

    return {
        "case_id": "passage_test",
        "agents": [0, 1],
        "scenario": {"type": "passage_meeting", "n_agents": 2, "single_file_segments": [{"name": "passage", "width_m": 0.8, "length_m": 4.0}]},
        "observations": {"0": record(a, b).as_dict(), "1": record(b, a).as_dict()},
    }


def session(case, condition="negotiated", groups=None, **levels):
    chosen = {
        "age_pair": "p1_older", "gender_pair": "p1_female", "task": "p1_urgent",
        "demographics_visible": True, "mapping": "p1_lower", "order": "lower_first", **levels,
    }
    raw = {"seed": 1, "factors": {name: [value] for name, value in chosen.items()}}
    if groups is not None:
        raw["ethnicity"] = {"enabled": True, "factors": {name: [value] for name, value in groups.items()}}
    (found,) = sessions_for([(case["case_id"], 1, tuple(case["agents"]))], DesignSettings.from_config(raw), [condition], {}, "test")
    return found


SHOWN = {"group_pair": "different", "label_rotation": 0, "ethnicity_visible": True}
HIDDEN = {**SHOWN, "ethnicity_visible": False}


# --- frozen, and for rule format 3 -------------------------------------------------------------------


def test_version_2_is_frozen_with_the_tool_and_describes_rule_format_3():
    manifest = prompts.load_manifest()
    for key, kind in (("rulegen_common_v2", "rule_generation_common"), ("rulegen_negotiate_v2", KIND_NEGOTIATE), ("rulegen_state_v2", KIND_STATE)):
        assert manifest[key]["kind"] == kind and manifest[key]["frozen_on"] == "2026-10-17"
    assert A2.common_key == B2.common_key == "rulegen_common_v2"
    assert describe.rule_schema_version_of(A2.common) == 3 and describe.rule_schema_version_of(A1.common) == 2
    for template in (A1, B1):  # version 1 is as it was, glossary hash and all
        assert template.common_key == "rulegen_common_v1" and template.sha256 == manifest[template.key]["sha256"]


def test_the_glossary_of_version_2_has_the_passage_fields_back_up_and_never_a_group():
    glossary = describe.glossary_text(A2.common, True)
    agent_part = glossary[glossary.index("Fields of each person"):]
    _, agent_fields = fields.fields_of(3)
    positions = [agent_part.index(f"- {name} (") for name in agent_fields]
    assert positions == sorted(positions) and len(positions) == 9
    assert "- in_segment (true or false): whether this person is inside the single-file segment" in glossary
    assert "- back_up (true or false; usual: false): when the two meet inside a stretch too narrow" in glossary
    assert "gives back_up true to exactly one of the two roles" in glossary
    for variant in (True, False):
        text = describe.glossary_text(A2.common, variant).lower()
        assert not any(word.lower() in text for word in GROUP_WORDS)  # the group is no field a rule may read
    hidden = describe.glossary_text(A2.common, False)
    assert "- age (" not in hidden and "segment_distance_travelled" in hidden
    assert describe.glossary_text(A1.common, True).count("segment_distance") == 0  # version 1 never had them


# --- a meeting inside a passage -----------------------------------------------------------------------


def test_a_meeting_inside_the_passage_is_told_with_how_far_each_has_walked_in():
    case = passage_case()
    a, b = session(case), session(case, "stated")
    lower = describe.first_person(case, a, 0, A2)
    assert "- You are standing still. Your usual walking speed is 1.30 m/s." in lower
    assert "- You have walked 2.0 m into this stretch. Its end ahead of you is 2.0 m away, and the end behind you 2.0 m." in lower
    assert "- They are standing still, facing in the opposite direction to you." in lower
    assert "- They are inside the stretch too, and have walked 1.4 m into it from its other end." in lower
    higher = describe.first_person(case, a, 1, A2)
    assert "- You have walked 1.4 m into this stretch. Its end ahead of you is 2.6 m away, and the end behind you 1.4 m." in higher
    told = describe.third_person(case, b, B2)
    assert "- Person 1 has walked 2.0 m into this stretch. Its end ahead of them is 2.0 m away, and the end behind them 2.0 m." in told
    assert "- Person 2 has walked 1.4 m into this stretch." in told and "- Person 2 is standing still, facing in the opposite direction to Person 1." in told
    # Walking into each other, the motion is told as before.
    walking = passage_case(geometry={"start_speed": "preferred"})
    assert "- You are walking at 1.30 m/s." in describe.first_person(walking, session(walking), 0, A2)


def test_version_1_tells_the_same_case_as_it_always_told_any_case():
    case = passage_case()
    text = describe.first_person(case, session(case), 0, A1) + describe.third_person(case, session(case, "stated"), B1)
    for added in ("standing still", "into this stretch", "inside the stretch too"):
        assert added not in text
    assert "- You are walking at 0.00 m/s." in text  # version 1's own wording, unchanged


@pytest.mark.parametrize("condition", ["negotiated", "stated"])
def test_no_version_2_prompt_suggests_who_should_back_out(condition):
    case = passage_case()
    for groups in (None, SHOWN):
        chosen = session(case, condition, groups)
        text = (describe.negotiation_prompt(case, chosen, 0, A2) if condition == "negotiated" else describe.statement_prompt(case, chosen, B2)).lower()
        for phrase in SUGGESTIONS:
            assert phrase not in text, phrase


# --- the group ----------------------------------------------------------------------------------------


def test_the_group_is_stated_when_the_session_shows_it():
    case = passage_case()
    shown = session(case, groups=SHOWN)
    assert {person["ethnic_group"] for person in shown.personas.values()} == {"Kestrop", "Dremmik"}
    me, them = shown.personas[0]["ethnic_group"], shown.personas[1]["ethnic_group"]
    first = describe.first_person(case, shown, 0, A2)
    assert f"- You belong to the {me} ethnic group." in first and f"- They belong to the {them} ethnic group." in first
    told = describe.third_person(case, session(case, "stated", SHOWN), B2)
    assert f"- Person 1 belongs to the {me} ethnic group." in told and f"- Person 2 belongs to the {them} ethnic group." in told


def test_the_framing_word_is_the_sessions():
    case = passage_case()
    raw = {"seed": 1, "factors": {name: [value] for name, value in {
        "age_pair": "same", "gender_pair": "same_male", "task": "none", "demographics_visible": False, "mapping": "p1_lower", "order": "lower_first",
    }.items()}, "ethnicity": {"enabled": True, "framing": "community", "factors": {name: [value] for name, value in SHOWN.items()}}}
    (chosen,) = sessions_for([("passage_test", 1, (0, 1))], DesignSettings.from_config(raw), ["negotiated"], {}, "test")
    text = describe.first_person(case, chosen, 0, A2)
    assert "- You belong to the Kestrop community." in text and "ethnic" not in text
    assert "years old" not in text  # demographics hidden, groups shown: the two switches are apart


@pytest.mark.parametrize("condition", ["negotiated", "stated"])
def test_a_hidden_group_appears_nowhere_in_what_a_model_is_shown(condition):
    case = passage_case()
    chosen = session(case, condition, HIDDEN)
    assert chosen.framing == "ethnic group" and all(person.get("ethnic_group") for person in chosen.personas.values())
    if condition == "negotiated":
        texts = [describe.negotiation_prompt(case, chosen, agent, A2) for agent in (0, 1)]
    else:
        texts = [describe.statement_prompt(case, chosen, B2)]
    texts += [json.dumps(A2.data["turns"]), B2.data["retry"]]
    for text in texts:
        lowered = text.lower()
        assert not any(word.lower() in lowered for word in GROUP_WORDS), text[:200]


def test_version_1_never_states_a_group_even_when_the_session_shows_one():
    case = passage_case()
    text = describe.negotiation_prompt(case, session(case, groups=SHOWN), 0, A1) + describe.statement_prompt(case, session(case, "stated", SHOWN), B1)
    assert not any(word.lower() in text.lower() for word in GROUP_WORDS)


def test_every_case_of_the_store_renders_with_version_2():
    store = CaseStore(CASES_ROOT)
    for case_id, version in store.case_set("si3_v1"):
        case = store.get(case_id, version)
        for groups in (None, SHOWN):
            chosen = session(case, groups=groups)
            for agent in case["agents"]:
                assert describe.negotiation_prompt(case, chosen, agent, A2)
            assert describe.statement_prompt(case, session(case, "stated", groups), B2)
