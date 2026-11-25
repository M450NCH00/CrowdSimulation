"""Turn parsing, consensus, the situation report, and the dialogue protocol."""

from __future__ import annotations

import json

import pytest

from helpers import scenario
from negsim.configutil import ConfigError
from negsim.core import Control
from negsim.llm import LLMTransientError, MockClient
from negsim.negotiation import (
    END_CONSENSUS,
    END_MESSAGE_LIMIT,
    INFO_FIELDS,
    Dialogue,
    NegotiationSettings,
    Participant,
    Stance,
    TurnParseError,
    agreed_leader,
    default_visibility,
    find_consensus,
    load_template,
    observe,
    parse_turn_output,
    region_status,
    render_report,
    resolve_info_fields,
)
from negsim.personas import validate_persona

I, YOU, UND = Stance.I_GO_FIRST, Stance.YOU_GO_FIRST, Stance.UNDECIDED


def reply(message: str, stance: str) -> str:
    return json.dumps({"message": message, "stance": stance})


# --- parsing ---------------------------------------------------------------------------------


def test_a_valid_turn_is_parsed():
    turn = parse_turn_output('{"message": " After you. ", "stance": "YOU_GO_FIRST"}')
    assert (turn.message, turn.stance) == ("After you.", YOU)
    assert json.loads(turn.as_json()) == {"message": "After you.", "stance": "YOU_GO_FIRST"}


def test_parsing_tolerates_only_harmless_variation():
    assert parse_turn_output('{"stance": " i_go_first ", "message": "Me first.", "confidence": 0.9}').stance is I
    assert parse_turn_output('```json\n{"message": "Hi", "stance": "UNDECIDED"}\n```').stance is UND
    assert parse_turn_output('```\n{"message": "Hi", "stance": "UNDECIDED"}\n```').message == "Hi"
    assert parse_turn_output('\n  {"message": "Hi", "stance": "UNDECIDED"}  \n').message == "Hi"


@pytest.mark.parametrize(
    "raw, code",
    [
        (None, "empty_output"),
        ("", "empty_output"),
        ("   \n", "empty_output"),
        ("I think you should go first.", "not_json"),
        ('{"message": "Hi", "stance": "UNDECIDED"', "not_json"),  # cut off, e.g. by max_tokens
        ('Sure! {"message": "Hi", "stance": "UNDECIDED"}', "not_json"),
        ("1", "not_an_object"),  # GameChat's own consensus signal is not a turn here
        ('["Hi", "UNDECIDED"]', "not_an_object"),
        ('{"stance": "UNDECIDED"}', "missing_message"),
        ('{"message": 42, "stance": "UNDECIDED"}', "message_not_text"),
        ('{"message": "  ", "stance": "UNDECIDED"}', "empty_message"),
        ('{"message": "Hi"}', "missing_stance"),
        ('{"message": "Hi", "stance": "MAYBE"}', "invalid_stance"),
        ('{"message": "Hi", "stance": null}', "invalid_stance"),
        ('{"message": "Hi", "stance": 1}', "invalid_stance"),
    ],
)
def test_malformed_output_is_rejected_with_a_stable_code(raw, code):
    with pytest.raises(TurnParseError) as error:
        parse_turn_output(raw)
    assert error.value.code == code


# --- consensus -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "previous, current, leader",
    [
        ((0, I), (1, YOU), 0),
        ((0, YOU), (1, I), 1),
        ((1, I), (0, YOU), 1),
        ((0, I), (1, I), None),  # both insist
        ((0, YOU), (1, YOU), None),  # both defer: polite, but not an agreement
        ((0, I), (1, UND), None),
        ((0, UND), (1, YOU), None),
        ((0, I), (0, YOU), None),  # one agent changing its mind is not two agents agreeing
    ],
)
def test_consensus_is_complementary_stances_on_consecutive_turns(previous, current, leader):
    assert agreed_leader(previous, current) == leader


def test_consensus_is_found_at_the_first_complementary_pair():
    turns = [(0, UND), (1, I), (0, I), (1, YOU), (0, YOU)]
    assert find_consensus(turns) == (0, 3)  # agent 0 says I, agent 1 then says YOU
    assert find_consensus([(0, I)]) is None
    assert find_consensus([]) is None


def test_no_consensus_within_the_turn_limit():
    stubborn = [(k % 2, I) for k in range(8)]  # four messages each, nobody gives way
    assert find_consensus(stubborn) is None
    # Complementary stances that are not on consecutive turns do not count.
    assert find_consensus([(0, I), (1, UND), (0, UND), (1, YOU)]) is None


# --- the situation report ----------------------------------------------------------------------


def hallway_world():
    spec = scenario("hallway")
    return spec, spec.build_world()


def test_info_fields_setting():
    assert resolve_info_fields("all") == INFO_FIELDS
    assert resolve_info_fields("none") == () == resolve_info_fields(None)
    assert resolve_info_fields(["own_size", "elapsed_time"]) == ("elapsed_time", "own_size")  # canonical order
    with pytest.raises(ConfigError, match="unknown field"):
        resolve_info_fields(["other_max_speed"])  # not observable, so not a field at all
    with pytest.raises(ConfigError):
        resolve_info_fields("some")


def test_full_report_has_one_line_per_field_with_units_and_consistent_rounding():
    spec, world = hallway_world()
    report = render_report(observe(world, spec, 0, 1, 0.0), INFO_FIELDS, default_visibility(), load_template("persona_v1"))
    assert report.splitlines() == [
        "What you can see right now:",
        "- Time since the two of you first saw each other: 0.0 s.",
        "- Your walking speed right now: 1.30 m/s.",
        "- The fastest you can walk: 1.30 m/s.",
        "- Your body width: 0.50 m.",
        "- Your distance to your end of the hallway: 2.34 m.",
        "- At your fastest you would reach your end of the hallway in about 1.8 s.",
        "- The other person's walking speed right now: 1.30 m/s.",
        "- The other person's body width: 0.50 m.",
        "- The other person's distance to their end of the hallway: 2.34 m.",
        "- At the speed they are walking now, the other person would reach their end of the hallway in about 1.8 s.",
        "- The hallway is 0.80 m wide and 4.00 m long.",
    ]


@pytest.mark.parametrize("field", INFO_FIELDS)
def test_each_field_can_be_switched_off_on_its_own(field):
    spec, world = hallway_world()
    observation, template = observe(world, spec, 0, 1, 0.0), load_template("persona_v1")
    everything = render_report(observation, INFO_FIELDS, default_visibility(), template).splitlines()
    without = render_report(
        observation, tuple(f for f in INFO_FIELDS if f != field), default_visibility(), template
    ).splitlines()
    assert len(without) == len(everything) - 1
    assert len(set(everything) - set(without)) == 1


@pytest.mark.parametrize("field", INFO_FIELDS)
def test_each_field_can_be_switched_on_on_its_own(field):
    spec, world = hallway_world()
    report = render_report(observe(world, spec, 0, 1, 0.0), (field,), default_visibility(), load_template("persona_v1"))
    assert len(report.splitlines()) == 2  # the header and that one line


def test_no_fields_means_no_report_at_all():
    spec, world = hallway_world()
    assert render_report(observe(world, spec, 0, 1, 0.0), (), default_visibility(), load_template("persona_v1")) == ""


def test_the_report_never_reveals_what_cannot_be_observed():
    spec = scenario("hallway", agents=[{}, {"max_speed": 0.77, "radius": 0.3}])
    world = spec.build_world()
    world.agents[1].speed = 0.4  # the other person is walking slower than they could
    report = render_report(observe(world, spec, 0, 1, 0.0), INFO_FIELDS, default_visibility(), load_template("persona_v1"))
    assert "0.77" not in report  # their maximum speed is never shown
    assert "The other person's walking speed right now: 0.40 m/s." in report
    assert "The other person's body width: 0.60 m." in report
    # ...and each agent is told its own maximum, not the other's.
    assert "The fastest you can walk: 1.30 m/s." in report
    own = render_report(observe(world, spec, 1, 0, 0.0), INFO_FIELDS, default_visibility(), load_template("persona_v1"))
    assert "The fastest you can walk: 0.77 m/s." in own and "1.30 m/s." in own  # 1.30 is agent 0's *current* speed


def test_visibility_settings_gate_the_other_agents_speed_and_size():
    spec, world = hallway_world()
    observation, template = observe(world, spec, 0, 1, 0.0), load_template("persona_v1")
    no_speed = render_report(observation, INFO_FIELDS, {**default_visibility(), "speed": False}, template)
    assert "The other person's walking speed" not in no_speed and "the other person would reach" not in no_speed
    assert "The other person's body width" in no_speed and "The other person's distance" in no_speed
    no_size = render_report(observation, INFO_FIELDS, {**default_visibility(), "size": False}, template)
    assert "The other person's body width" not in no_size and "The other person's walking speed" in no_size


def test_the_report_is_rebuilt_from_the_current_state():
    spec, world = hallway_world()
    template = load_template("persona_v1")
    before = render_report(observe(world, spec, 0, 1, 0.0), INFO_FIELDS, default_visibility(), template)
    for _ in range(10):  # one second: agent 0 walks on, agent 1 stands still
        world.step({0: Control(1.3, 0.0), 1: Control(0.0, 0.0)})
    after = render_report(observe(world, spec, 0, 1, 0.0), INFO_FIELDS, default_visibility(), template)
    assert before != after
    assert "- Time since the two of you first saw each other: 1.0 s." in after
    assert "- The other person is standing still at the moment." in after
    assert "the other person would reach" not in after
    assert "- The other person's walking speed right now: 0.00 m/s." in after


def test_region_status_goes_from_approaching_to_inside_to_past():
    spec, world = hallway_world()
    agent = world.agents[0]
    assert region_status(agent).state == "approaching"
    agent.path_s = agent.spec.region_entry_s + 1.0
    assert region_status(agent).state == "inside" and region_status(agent).distance == 0.0
    report = render_report(observe(world, spec, 0, 1, 0.0), INFO_FIELDS, default_visibility(), load_template("persona_v1"))
    assert "- You are inside the hallway." in report and "you would reach" not in report
    agent.path_s = agent.spec.region_exit_s + 1.0
    assert region_status(agent).state == "past"


def test_task_only_template_has_its_own_wording_for_the_report():
    spec = scenario("doorway")
    report = render_report(observe(spec.build_world(), spec, 0, 1, 0.0), INFO_FIELDS, default_visibility(), load_template("gamechat_task_v1"))
    assert "- The other agent's current speed: 0.30 m/s." in report
    assert "- The doorway is 0.40 m wide." in report
    assert "person" not in report


# --- the dialogue protocol ---------------------------------------------------------------------


def make_dialogue(client, template="gamechat_task_v1", first_speaker=0, max_messages=4, info_fields=(), name="doorway", visibility=None):
    spec = scenario(name)
    if template == "persona_v1":
        participants = {
            0: Participant(0, "the clinic", persona=validate_persona({"persona_id": "a", "age": 70, "gender": "female", "task": "the clinic"})),
            1: Participant(1, "the gym", persona=validate_persona({"persona_id": "b", "age": 25, "gender": "male", "task": "the gym"})),
        }
    else:
        participants = {0: Participant(0, "the hospital", "hospital"), 1: Participant(1, "buy groceries", "grocery")}
    settings = NegotiationSettings(
        template=load_template(template), max_messages_per_agent=max_messages, first_speaker=first_speaker,
        info_fields=info_fields, visibility=visibility or default_visibility(), model="mock-model",
        temperature=0.7, max_tokens=123,
    )
    dialogue = Dialogue(settings, participants, spec, client, labels={"run_id": "t"})
    world = spec.build_world()
    dialogue.start(world.time)
    return dialogue, world


def run_to_end(dialogue, world):
    while dialogue.active:
        dialogue.take_turn(world)
    return dialogue


def test_dialogue_ends_at_consensus_and_names_the_leader():
    client = MockClient(script=[reply("I am going to the hospital.", "UNDECIDED"), reply("Groceries. You go.", "YOU_GO_FIRST"), reply("Thanks, going.", "I_GO_FIRST")])
    dialogue = run_to_end(*make_dialogue(client))
    assert dialogue.end_reason == END_CONSENSUS and dialogue.consensus
    assert dialogue.leader == 0 and len(dialogue.turns) == 3
    assert [turn.speaker for turn in dialogue.turns] == [0, 1, 0]
    assert dialogue.messages_sent() == {0: 2, 1: 1}


def test_first_speaker_setting_is_respected():
    client = MockClient(script=[reply("You first.", "YOU_GO_FIRST"), reply("Thank you.", "I_GO_FIRST")])
    dialogue = run_to_end(*make_dialogue(client, first_speaker=1))
    assert [turn.speaker for turn in dialogue.turns] == [1, 0]
    assert dialogue.leader == 0  # agent 1 deferred, agent 0 accepted


def test_dialogue_stops_after_four_messages_each_without_agreement():
    dialogue = run_to_end(*make_dialogue(MockClient(policy="insist")))
    assert dialogue.end_reason == END_MESSAGE_LIMIT and not dialogue.consensus
    assert dialogue.leader is None and len(dialogue.turns) == 8
    assert dialogue.messages_sent() == {0: 4, 1: 4}
    with pytest.raises(RuntimeError):
        dialogue.take_turn(make_dialogue(MockClient())[1])


def test_message_limit_is_configurable_and_consensus_can_come_on_the_last_turn():
    client = MockClient(script=[reply("Hm.", "UNDECIDED"), reply("Hm.", "UNDECIDED"), reply("I go.", "I_GO_FIRST"), reply("Fine.", "YOU_GO_FIRST")])
    dialogue = run_to_end(*make_dialogue(client, max_messages=2))
    assert dialogue.end_reason == END_CONSENSUS and len(dialogue.turns) == 4


def test_only_the_message_reaches_the_other_agent_never_the_stance():
    client = MockClient(script=[reply("Where are you headed?", "I_GO_FIRST"), reply("The shops.", "UNDECIDED"), reply("OK.", "UNDECIDED")])
    dialogue, world = make_dialogue(client)
    dialogue.take_turn(world)
    dialogue.take_turn(world)
    seen_by_agent_1 = client.requests[1].messages
    assert seen_by_agent_1[-1] == {"role": "user", "content": "Other agent says: Where are you headed?"}
    assert not any("I_GO_FIRST" in m["content"] for m in seen_by_agent_1 if m["role"] != "system")
    # An agent does see its own earlier stance, in its own history.
    dialogue.take_turn(world)
    own_history = client.requests[2].messages
    assert [m["role"] for m in own_history] == ["system", "user", "assistant", "user"]
    assert json.loads(own_history[2]["content"]) == {"message": "Where are you headed?", "stance": "I_GO_FIRST"}
    assert own_history[3]["content"] == "Other agent says: The shops."


def test_each_agent_is_given_its_own_system_prompt_and_the_run_settings():
    client = MockClient(policy="insist")
    dialogue, world = make_dialogue(client)
    dialogue.take_turn(world)
    dialogue.take_turn(world)
    assert "taking someone to the hospital" in client.requests[0].messages[0]["content"]
    assert "taking someone to buy groceries" in client.requests[1].messages[0]["content"]
    request = client.requests[0]
    assert (request.model, request.temperature, request.max_tokens, request.json_mode, request.thinking) == ("mock-model", 0.7, 123, True, False)
    assert request.metadata == {"run_id": "t", "turn_index": 0, "speaker": 0, "attempt": 1}
    assert client.requests[0].messages[1]["content"] == "Other agent says: Begin the conversation"


def test_malformed_output_is_retried_once_and_the_retry_can_succeed():
    client = MockClient(script=["Sure, go ahead!", reply("Go ahead.", "YOU_GO_FIRST"), reply("Thanks.", "I_GO_FIRST")])
    dialogue, world = make_dialogue(client)
    turn = dialogue.take_turn(world)
    assert turn.parse_ok and turn.stance is YOU and turn.message == "Go ahead."
    assert len(turn.attempts) == 2
    assert turn.attempts[0].parse_error.startswith("not_json") and turn.attempts[1].parse_error is None
    # The retry shows the model its unreadable reply and asks again; neither reaches the history.
    retry_messages = client.requests[1].messages
    assert retry_messages[-2] == {"role": "assistant", "content": "Sure, go ahead!"}
    assert "could not be read" in retry_messages[-1]["content"]
    dialogue.take_turn(world)
    assert "Sure, go ahead!" not in json.dumps(client.requests[2].messages)
    assert dialogue.totals()["retries"] == 1 and dialogue.totals()["parse_failures"] == 0


def test_two_malformed_outputs_make_the_stance_undecided_and_are_logged():
    client = MockClient(script=["nope", None, reply("Hello?", "UNDECIDED")])
    dialogue, world = make_dialogue(client)
    turn = dialogue.take_turn(world)
    assert not turn.parse_ok and turn.stance is UND and turn.message == ""
    assert turn.parse_error == "empty_output"
    assert [a.parse_error.split(":")[0] for a in turn.attempts] == ["not_json", "empty_output"]
    assert len(client.requests) == 2  # exactly one retry, not more
    record = turn.as_dict()
    assert record["n_attempts"] == 2 and record["parse_error"] == "empty_output" and record["raw_output"] is None
    # The other agent is told there was no intelligible reply, and the dialogue goes on.
    dialogue.take_turn(world)
    assert client.requests[2].messages[-1]["content"] == "The other agent's reply could not be understood."
    assert dialogue.active and dialogue.totals()["parse_failures"] == 1


def test_a_failed_turn_cannot_complete_a_consensus():
    client = MockClient(script=[reply("I go.", "I_GO_FIRST"), "garbage", "more garbage", reply("I go.", "I_GO_FIRST")])
    dialogue, world = make_dialogue(client)
    dialogue.take_turn(world)
    dialogue.take_turn(world)
    assert dialogue.active and dialogue.leader is None


def test_a_transient_api_error_counts_as_a_failed_attempt():
    class Flaky(MockClient):
        def complete(self, request):
            if len(self.requests) == 0:
                self.requests.append(request)
                raise LLMTransientError("HTTP 503: overloaded", attempts=3)
            return super().complete(request)

    client = Flaky(script=[reply("Go ahead.", "YOU_GO_FIRST")])
    dialogue, world = make_dialogue(client)
    turn = dialogue.take_turn(world)
    assert turn.parse_ok and len(turn.attempts) == 2
    assert turn.attempts[0].api_error == "HTTP 503: overloaded" and turn.attempts[0].raw_output is None


def test_situation_report_is_placed_before_what_the_other_agent_said():
    client = MockClient(policy="first_speaker_goes")
    dialogue, world = make_dialogue(client, template="persona_v1", info_fields=("own_speed", "region_geometry"), name="hallway")
    first = dialogue.take_turn(world)
    assert client.requests[0].messages[-1]["content"] == (
        "What you can see right now:\n- Your walking speed right now: 1.30 m/s.\n"
        "- The hallway is 0.80 m wide and 4.00 m long.\n\nYou speak first."
    )
    assert first.situation_report.startswith("What you can see right now:")
    assert first.situation_values["own_max_speed_mps"] == 1.3
    dialogue.take_turn(world)
    assert client.requests[1].messages[-1]["content"].endswith('\n\nThe other person says: "I will go first."')
    assert dialogue.leader == 0


def test_turn_record_carries_everything_the_log_schema_asks_for():
    from negsim.runlog.schema import ATTEMPT_KEYS, TURN_KEYS

    dialogue, world = make_dialogue(MockClient(policy="first_speaker_goes"))
    record = dialogue.take_turn(world).as_dict()
    assert set(TURN_KEYS) <= set(record)
    assert set(ATTEMPT_KEYS) <= set(record["attempts"][0])
    assert record["prompt_messages"][0]["role"] == "system"
    assert json.loads(record["raw_output"])["stance"] == record["stance"] == "I_GO_FIRST"
    assert record["tokens"]["prompt_tokens"] > 0 and record["cost_usd"] == 0.0
    assert json.loads(json.dumps(record)) == record  # plain JSON all the way down


def test_dialogue_validates_its_setup():
    spec = scenario("doorway")
    settings = NegotiationSettings(load_template("gamechat_task_v1"), 4, 0, (), default_visibility(), "m", 1.0, 100)
    two = {0: Participant(0, "a"), 1: Participant(1, "b")}
    with pytest.raises(ValueError, match="exactly two"):
        Dialogue(settings, {**two, 2: Participant(2, "c")}, spec, MockClient())
    bad_speaker = NegotiationSettings(load_template("gamechat_task_v1"), 4, 5, (), default_visibility(), "m", 1.0, 100)
    with pytest.raises(ValueError, match="first_speaker"):
        Dialogue(bad_speaker, two, spec, MockClient())
