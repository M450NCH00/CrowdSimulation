"""Personas (loading, validation), prompt rendering, visibility, and template integrity."""

from __future__ import annotations

import shutil

import pytest

import negsim.negotiation.prompts as prompts
from negsim.configutil import ConfigError
from negsim.negotiation import (
    Participant,
    TemplateIntegrityError,
    available_templates,
    default_visibility,
    load_template,
    resolve_visibility,
    template_sha256,
)
from negsim.personas import ATTRIBUTES, PersonaError, load_personas, validate_persona

PERSONAS = "configs/personas/personas.yaml"
VALID = {"persona_id": "p1", "age": 34, "gender": "female", "task": "the pharmacy"}


def participant(agent_id: int, **changes) -> Participant:
    persona = validate_persona({**VALID, **changes})
    return Participant(agent_id, task=persona.task, persona=persona)


# --- personas --------------------------------------------------------------------------------


def test_shipped_personas_load_and_form_an_age_by_gender_grid():
    personas = load_personas(PERSONAS)
    assert sorted(personas) == ["f25", "f70", "m25", "m70"]
    assert {(p.age, p.gender) for p in personas.values()} == {(25, "female"), (25, "male"), (70, "female"), (70, "male")}
    assert all(p.backstory == "" for p in personas.values())
    assert len({p.task for p in personas.values()}) == 1  # one task, so age and gender can be isolated


def test_a_valid_persona_and_its_defaults():
    persona = validate_persona(VALID)
    assert (persona.persona_id, persona.age, persona.gender, persona.task, persona.backstory) == (
        "p1", 34, "female", "the pharmacy", "",
    )
    assert persona.as_dict() == {**VALID, "backstory": ""}


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"age": "34"}, "age must be a whole number"),
        ({"age": 34.5}, "age must be a whole number"),
        ({"age": True}, "age must be a whole number"),
        ({"age": 0}, "age must be between"),
        ({"age": 300}, "age must be between"),
        ({"gender": "F"}, "gender must be one of"),
        ({"gender": None}, "gender must be one of"),
        ({"task": ""}, "task must not be empty"),
        ({"task": 7}, "task must be text"),
        ({"backstory": 12}, "backstory must be text"),
        ({"persona_id": "Mrs Tan"}, "a code, not a name"),
        ({"persona_id": ""}, "needs a 'persona_id'"),
        ({"height_cm": 170}, "unknown field"),
    ],
)
def test_invalid_personas_are_rejected_with_the_reason(changes, message):
    with pytest.raises(PersonaError, match=message):
        validate_persona({**VALID, **changes})


@pytest.mark.parametrize("field", ["age", "gender", "task"])
def test_required_fields(field):
    raw = {key: value for key, value in VALID.items() if key != field}
    with pytest.raises(PersonaError, match=f"missing required field '{field}'"):
        validate_persona(raw)


@pytest.mark.parametrize("field", ["name", "first_name", "surname", "nickname"])
def test_personal_names_are_refused(field):
    with pytest.raises(PersonaError, match="must not have personal names"):
        validate_persona({**VALID, field: "Wei Ling"})


def test_age_and_gender_vary_independently():
    base = validate_persona(VALID)
    older = base.with_overrides(age=70)
    assert (older.age, older.gender, older.task) == (70, "female", "the pharmacy")
    assert older.persona_id == "p1+age=70"
    male = base.with_overrides(gender="male")
    assert (male.age, male.gender) == (34, "male") and male.persona_id == "p1+gender=male"
    assert base.with_overrides(task="the airport").persona_id == "p1"  # a task is not part of who they are
    assert base.with_overrides(backstory="Lives nearby.").persona_id == "p1+backstory*"
    assert base.with_overrides() is base
    with pytest.raises(PersonaError):
        base.with_overrides(age=-5)


def test_loader_reports_the_file_and_the_entry(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("personas:\n  - {persona_id: a1, age: 30, gender: male, task: work}\n  - {persona_id: a2, age: old, gender: male, task: work}\n")
    with pytest.raises(PersonaError, match=r"personas\[1\].*age must be a whole number"):
        load_personas(bad)
    bad.write_text("personas:\n  - {persona_id: a1, age: 30, gender: male, task: work}\n  - {persona_id: a1, age: 31, gender: male, task: work}\n")
    with pytest.raises(PersonaError, match="defined twice"):
        load_personas(bad)
    bad.write_text("people: []\n")
    with pytest.raises(PersonaError, match="'personas' list"):
        load_personas(bad)
    with pytest.raises(PersonaError, match="not found"):
        load_personas(tmp_path / "missing.yaml")


def test_the_schema_is_a_table_so_an_attribute_can_be_added_without_touching_the_loader(monkeypatch):
    from negsim.personas.schema import AttributeSpec, _text

    monkeypatch.setitem(ATTRIBUTES, "occupation", AttributeSpec("occupation", _text(False), False, "", False))
    persona = validate_persona({**VALID, "occupation": "nurse"})
    assert persona.attributes["occupation"] == "nurse"
    assert "occupation" in default_visibility()


# --- visibility ------------------------------------------------------------------------------


def test_default_visibility_shows_what_a_bystander_could_see():
    assert default_visibility() == {
        "age": True, "gender": True, "backstory": False, "task": False, "ethnic_group": False, "speed": True, "size": True,
    }  # ethnic_group: issue #32, off unless a run switches it on


def test_visibility_can_be_changed_per_attribute():
    assert resolve_visibility("default") == default_visibility()
    custom = resolve_visibility({"task": True, "age": False})
    assert custom["task"] is True and custom["age"] is False and custom["gender"] is True
    with pytest.raises(ConfigError, match="unknown attribute"):
        resolve_visibility({"shoe_size": True})
    with pytest.raises(ConfigError, match="true or false"):
        resolve_visibility({"age": "yes"})


# --- rendering -------------------------------------------------------------------------------


def test_persona_prompt_states_who_the_agent_is_and_what_it_can_see():
    template = load_template("persona_v1")
    me = participant(0, age=70, gender="female", task="the hospital emergency room")
    them = participant(1, persona_id="p2", age=25, gender="male", task="the airport to catch a flight")
    prompt = template.render_system(me, them, "hallway", default_visibility())
    assert "- You are 70 years old." in prompt
    assert "- You are a woman." in prompt
    assert "- You are on your way to the hospital emergency room." in prompt
    assert "narrow hallway" in prompt
    assert "- They look about 25 years old." in prompt
    assert "- They look like a man." in prompt
    # The other person's task is private by default, and the agent is told so.
    assert "airport" not in prompt
    assert "- You do not know where they are going or why, unless they tell you." in prompt
    assert '"stance"' in prompt and "JSON" in prompt  # DeepSeek's JSON mode needs the word in the prompt


def test_each_agent_gets_its_own_prompt_not_the_others():
    template = load_template("persona_v1")
    a = participant(0, age=70, gender="female")
    b = participant(1, persona_id="p2", age=25, gender="male")
    prompt_a = template.render_system(a, b, "doorway", default_visibility())
    prompt_b = template.render_system(b, a, "doorway", default_visibility())
    assert "You are 70 years old" in prompt_a and "They look about 25" in prompt_a
    assert "You are 25 years old" in prompt_b and "They look about 70" in prompt_b


@pytest.mark.parametrize(
    "attribute, line",
    [("age", "They look about 25 years old."), ("gender", "They look like a man.")],
)
def test_hiding_an_attribute_removes_exactly_that_line(attribute, line):
    template = load_template("persona_v1")
    me, them = participant(0), participant(1, persona_id="p2", age=25, gender="male")
    shown = template.render_system(me, them, "hallway", default_visibility())
    hidden = template.render_system(me, them, "hallway", {**default_visibility(), attribute: False})
    assert line in shown and line not in hidden
    assert set(shown.splitlines()) - set(hidden.splitlines()) == {f"- {line}"}


def test_making_the_task_visible_shows_it_and_drops_the_notice():
    template = load_template("persona_v1")
    me, them = participant(0), participant(1, persona_id="p2", task="the airport to catch a flight")
    prompt = template.render_system(me, them, "hallway", {**default_visibility(), "task": True})
    assert "- They are on their way to the airport to catch a flight." in prompt
    assert "You do not know where they are going" not in prompt


def test_nothing_visible_is_said_plainly():
    template = load_template("persona_v1")
    nothing = {key: False for key in default_visibility()}
    prompt = template.render_system(participant(0), participant(1, persona_id="p2"), "hallway", nothing)
    assert "- You do not know where they are going or why, unless they tell you." in prompt
    assert "They look" not in prompt


def test_backstory_appears_only_when_there_is_one():
    template = load_template("persona_v1")
    them = participant(1, persona_id="p2")
    plain = template.render_system(participant(0), them, "hallway", default_visibility())
    storied = template.render_system(participant(0, backstory="You have a bad knee."), them, "hallway", default_visibility())
    assert "- You have a bad knee." in storied
    assert len(storied.splitlines()) == len(plain.splitlines()) + 1


def test_every_scenario_has_a_scene_and_they_differ():
    template = load_template("persona_v1")
    me, them = participant(0), participant(1, persona_id="p2")
    scenes = {kind: template.render_system(me, them, kind, default_visibility()) for kind in ("doorway", "intersection", "hallway")}
    assert len(set(scenes.values())) == 3
    with pytest.raises(ConfigError, match="no scene text"):
        template.render_system(me, them, "roundabout", default_visibility())


def test_gamechat_prompt_is_the_papers_with_the_consensus_sentence_replaced():
    template = load_template("gamechat_task_v1")
    prompt = template.render_system(
        Participant(0, task="the hospital", task_type="hospital"),
        Participant(1, task="buy groceries", task_type="grocery"),
        "doorway",
        default_visibility(),
    )
    paper = (
        "You are taking someone to the hospital. There is another agent taking someone to a location. "
        "You will have a conversation until you determine whether you have more or less priority as them "
        "depending on the tasks you and they are performing. Do not include pleasantries and be concise. "
        "Remembering your task correctly is paramount!"
    )
    assert prompt.startswith(paper)
    assert "output the number 1" not in prompt
    assert "groceries" not in prompt  # the other agent's task is learned only by talking
    assert "years old" not in prompt and "doorway" not in prompt  # no persona, no scene


def test_persona_template_refuses_a_participant_without_a_persona():
    template = load_template("persona_v1")
    with pytest.raises(ConfigError, match="needs a persona"):
        template.render_system(Participant(0, task="the hospital"), participant(1), "hallway", default_visibility())


def test_prompts_never_contain_a_personal_name_field():
    for key in available_templates():
        text = (prompts.TEMPLATE_DIR / f"{key}.yaml").read_text(encoding="utf-8")
        assert "{name}" not in text and "{persona_id}" not in text


# --- template integrity ----------------------------------------------------------------------


def test_every_template_file_matches_its_pinned_hash():
    manifest = prompts.load_manifest()
    files = sorted(path.stem for path in prompts.TEMPLATE_DIR.glob("*.yaml"))
    assert files == sorted(manifest)
    # Since issue #30 the manifest also freezes templates of other kinds (rule generation).
    assert available_templates() == sorted(key for key, entry in manifest.items() if "kind" not in entry)
    for key, entry in manifest.items():
        assert template_sha256(prompts.TEMPLATE_DIR / f"{key}.yaml") == entry["sha256"]
        if "kind" in entry:
            assert prompts.load_template_data(key, entry["kind"])[1] == entry["sha256"]
        else:
            assert load_template(key).identity()["sha256"] == entry["sha256"]


def test_an_edited_template_is_refused(tmp_path, monkeypatch):
    """No silent prompt tuning: changing one word of a frozen template stops it loading."""
    copy = tmp_path / "templates"
    shutil.copytree(prompts.TEMPLATE_DIR, copy)
    monkeypatch.setattr(prompts, "TEMPLATE_DIR", copy)
    monkeypatch.setattr(prompts, "MANIFEST_PATH", copy / "MANIFEST.json")
    assert load_template("persona_v1").version == 1
    path = copy / "persona_v1.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("to settle who goes first", "to agree that the elder goes first"), encoding="utf-8")
    with pytest.raises(TemplateIntegrityError, match="has been edited"):
        load_template("persona_v1")


def test_template_hash_ignores_line_endings(tmp_path):
    unix, windows = tmp_path / "u.yaml", tmp_path / "w.yaml"
    unix.write_bytes(b"a: 1\nb: 2\n")
    windows.write_bytes(b"a: 1\r\nb: 2\r\n")
    assert template_sha256(unix) == template_sha256(windows)


def test_unknown_template():
    with pytest.raises(ConfigError, match="unknown prompt template"):
        load_template("persona_v99")
