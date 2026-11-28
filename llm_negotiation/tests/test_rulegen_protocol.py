"""Issue #30, Parts 5 and 6: condition A (negotiate a standing rule) and condition B (state a rule)."""

from __future__ import annotations

import json
import math

import pytest

from negsim.llm import BudgetExceededError, MockClient
from negsim.negotiation.parsing import TurnParseError
from negsim.rules.canonical import canonical_hash, proposal_id
from negsim.rulegen.cases import CaseStore
from negsim.rulegen.describe import KIND_NEGOTIATE, KIND_STATE, load_templates, negotiation_prompt, statement_prompt
from negsim.rulegen.design import DesignSettings, sessions_for
from negsim.rulegen.protocol import (
    ACCEPT_NOTHING_PROPOSED,
    ACCEPT_OWN,
    ACCEPT_STALE,
    ACCEPT_UNKNOWN,
    ACCEPT_WITH_COUNTER,
    LLMSettings,
    RuleNegotiation,
    RuleStatement,
    parse_negotiation_turn,
    parse_statement,
    stability,
)

A = load_templates("rulegen_negotiate_v1", KIND_NEGOTIATE)
B = load_templates("rulegen_state_v1", KIND_STATE)
CASE = CaseStore().get("head_on_de176842")
LLM = LLMSettings("deepseek-flash", 1.0, 600)

KEEP_ROOM = {"encounter": "any", "when": {"all": []}, "roles": "symmetric", "directive": {"both": {"clearance_margin": 0.15}}, "priority": 100}
WIDER = {**KEEP_ROOM, "directive": {"both": {"clearance_margin": 0.3}}}
SLOWER = {**KEEP_ROOM, "directive": {"both": {"speed_scale": 0.8}}}


def session(condition="negotiated", order="lower_first", **levels):
    chosen = {
        "age_pair": "p1_older", "gender_pair": "p1_female", "task": "p1_urgent",
        "demographics_visible": True, "mapping": "p1_lower", "order": order, **levels,
    }
    settings = DesignSettings.from_config({"seed": 1, "factors": {name: [value] for name, value in chosen.items()}})
    (found,) = sessions_for([(CASE["case_id"], 1, tuple(CASE["agents"]))], settings, [condition], {}, "test")
    return found


def turn(message="Hello.", proposal=None, accept=None, no_rule=False) -> str:
    return json.dumps({"message": message, "proposal": proposal, "accept": accept, "no_rule_possible": no_rule})


def negotiate(*replies, max_messages=4, order="lower_first"):
    client = MockClient(script=list(replies))
    talk = RuleNegotiation(CASE, session(order=order), A, client, LLM, max_messages)
    talk.run()
    return talk, client


# --- condition A: agreement by canonical hash -------------------------------------------------------


def test_agreement_is_accepting_the_others_latest_proposal_by_its_id():
    talk, client = negotiate(turn("This?", KEEP_ROOM), turn("Yes.", accept=proposal_id(KEEP_ROOM)))
    assert talk.outcome == "agreed" and len(client.requests) == 2
    agreement = talk.agreement
    assert agreement["rule"] == KEEP_ROOM and agreement["canonical_hash"] == canonical_hash(KEEP_ROOM)
    assert (agreement["proposed_by"], agreement["accepted_by"]) == (0, 1)  # lower_first: agent 0 speaks first
    assert (agreement["proposed_at_turn"], agreement["accepted_at_turn"], agreement["proposer_spoke_first"]) == (0, 1, True)
    record = talk.as_dict()
    assert record["first_speaker"] == 0 and record["turns"][1]["accept_status"] == "agreed"
    assert [p["agreed"] for p in record["proposals"]] == [True]


def test_the_id_is_the_first_twelve_characters_of_the_hash_and_the_whole_hash_works_too():
    whole = canonical_hash(KEEP_ROOM)
    assert proposal_id(KEEP_ROOM) == whole[:12]
    talk, _ = negotiate(turn("This?", KEEP_ROOM), turn("Yes.", accept=whole.upper()))
    assert talk.outcome == "agreed"
    talk, _ = negotiate(turn("This?", KEEP_ROOM), turn("Yes?", accept=whole[:11]), max_messages=1)
    assert talk.outcome == "no_agreement" and talk.turns[1].accept_status == ACCEPT_UNKNOWN


def test_a_changed_rule_is_a_counter_proposal_not_an_acceptance():
    talk, client = negotiate(
        turn("This?", KEEP_ROOM),
        turn("Yes, but wider.", WIDER, accept=proposal_id(KEEP_ROOM)),
        turn("Fine.", accept=proposal_id(WIDER)),
    )
    assert talk.turns[1].accept_status == ACCEPT_WITH_COUNTER
    assert talk.outcome == "agreed" and talk.agreement["rule"] == WIDER
    assert (talk.agreement["proposed_by"], talk.agreement["proposer_spoke_first"]) == (1, False)
    shown = client.requests[2].messages[-1]["content"]
    assert f"proposal id {proposal_id(WIDER)}" in shown
    assert "under \"accept\"" not in shown  # it was a counter-proposal; it is shown as the new proposal it is


def test_the_same_rule_written_differently_is_the_same_proposal():
    reordered = {"priority": 100, "directive": {"both": {"clearance_margin": 0.150}}, "roles": "symmetric", "when": {"all": []}, "encounter": "any"}
    assert canonical_hash(reordered) == canonical_hash(KEEP_ROOM)
    talk, _ = negotiate(turn("This?", KEEP_ROOM), turn("Agreed, as I would write it.", reordered, accept=proposal_id(KEEP_ROOM)))
    assert talk.outcome == "agreed" and talk.agreement["rule"] == KEEP_ROOM  # the proposer's own wording is kept


def test_only_the_latest_proposal_can_be_accepted():
    talk, client = negotiate(
        turn("This?", KEEP_ROOM), turn("Or this?", WIDER), turn("Or this?", SLOWER),
        turn("Your first one.", accept=proposal_id(KEEP_ROOM)), turn("Your latest, then.", accept=proposal_id(WIDER)),
    )
    assert [record.accept_status for record in talk.turns] == [None, None, None, ACCEPT_STALE, "agreed"]
    assert talk.agreement["rule"] == WIDER and talk.agreement["accepted_at_turn"] == 4
    told = client.requests[4].messages[-1]["content"]
    assert f'They put {proposal_id(KEEP_ROOM)} under "accept", which is not the id of your latest proposal.' in told


def test_accepting_ones_own_proposal_an_unknown_id_or_nothing_is_not_agreement():
    talk, _ = negotiate(
        turn("Yes?", accept="abcdefabcdef"), turn("This?", KEEP_ROOM, accept=proposal_id(KEEP_ROOM)),
        turn("That?", accept="0123456789ab"), turn("Mine.", accept=proposal_id(KEEP_ROOM)),
        max_messages=2,
    )
    assert [record.accept_status for record in talk.turns] == [ACCEPT_NOTHING_PROPOSED, ACCEPT_OWN, ACCEPT_UNKNOWN, ACCEPT_OWN]
    assert talk.outcome == "no_agreement" and talk.agreement is None


def test_no_rule_is_possible_when_both_say_so_one_after_the_other():
    talk, _ = negotiate(
        turn("Nothing works without talking.", no_rule=True), turn("Try this.", KEEP_ROOM),
        turn("Still no.", no_rule=True), turn("I agree, none.", no_rule=True),
    )
    assert talk.outcome == "no_rule_possible" and len(talk.turns) == 4
    assert [record.turn.no_rule_possible for record in talk.turns] == [True, False, True, True]


def test_the_message_limit_ends_without_agreement():
    talk, client = negotiate(*[turn("Mine.", rule) for rule in (KEEP_ROOM, WIDER, SLOWER, KEEP_ROOM)], max_messages=2)
    assert talk.outcome == "no_agreement" and len(client.requests) == 4 and talk.max_turns == 4
    assert len(talk.proposals()) == 4 and not any(p["agreed"] for p in talk.proposals())


def test_an_unreadable_turn_is_retried_once_then_ends_the_negotiation():
    talk, client = negotiate("not json", turn("This?", KEEP_ROOM), turn("Yes.", accept=proposal_id(KEEP_ROOM)))
    assert talk.outcome == "agreed" and talk.turns[0].as_dict()["n_attempts"] == 2
    retry = client.requests[1].messages
    assert retry[-2] == {"role": "assistant", "content": "not json"} and retry[-1]["content"] == A.data["turns"]["retry"]
    talk, _ = negotiate("not json", '{"message": 3}')
    assert talk.outcome == "parse_failure" and talk.turns[0].parse_error.startswith("message_not_text")


def test_speaking_order_and_each_agents_own_prompt_and_history():
    talk, client = negotiate(turn("This?", KEEP_ROOM), turn("No.", WIDER), turn("Yes.", accept=proposal_id(WIDER)), order="higher_first")
    assert talk.order == (1, 0) and [request.metadata["speaker"] for request in client.requests] == [1, 0, 1]
    first, second, third = (request.messages for request in client.requests)
    assert first[0]["content"] == negotiation_prompt(CASE, talk.session, 1, A) != second[0]["content"] == negotiation_prompt(CASE, talk.session, 0, A)
    assert first[-1]["content"] == "You speak first."
    assert [message["role"] for message in third] == ["system", "user", "assistant", "user"]
    assert json.loads(third[2]["content"])["proposal"] == KEEP_ROOM  # its own turn, as it is kept
    assert "They say: \"No.\"" in third[3]["content"] and proposal_id(WIDER) in third[3]["content"]
    assert [request.metadata["speaker_role"] for request in client.requests] == ["first", "second", "first"]


@pytest.mark.parametrize(
    "raw, expected",
    [
        ('{"message": "hi"}', ("hi", None, None, False)),
        ('```json\n{"message": " hi ", "accept": " ABCDEFABCDEF ", "extra": 1}\n```', ("hi", None, "abcdefabcdef", False)),
        ('{"message": "", "proposal": {"a": 1}, "accept": "null", "no_rule_possible": true}', ("", {"a": 1}, None, True)),
    ],
)
def test_a_turn_is_read_with_issue_24s_tolerances(raw, expected):
    read = parse_negotiation_turn(raw)
    assert (read.message, read.proposal, read.accept, read.no_rule_possible) == expected


@pytest.mark.parametrize(
    "raw, code",
    [
        ("", "empty_output"), ("[1]", "not_an_object"), ("{", "not_json"), ('{"proposal": null}', "missing_message"),
        ('{"message": "x", "proposal": "a rule"}', "proposal_not_an_object"), ('{"message": "x", "accept": 7}', "accept_not_text"),
        ('{"message": "x", "no_rule_possible": "yes"}', "no_rule_possible_not_a_boolean"),
    ],
)
def test_a_turn_that_cannot_be_read(raw, code):
    with pytest.raises(TurnParseError) as caught:
        parse_negotiation_turn(raw)
    assert caught.value.code == code


# --- refusals: what was paid for is kept ----------------------------------------------------------


class RefusesAt:
    """A client that answers from a script and refuses the call numbered ``at`` (from 1)."""

    name = "mock"

    def __init__(self, at, *replies):
        self.inner, self.at, self.calls = MockClient(script=list(replies)), at, 0

    def complete(self, request):
        self.calls += 1
        if self.calls == self.at:
            raise BudgetExceededError("call refused")
        return self.inner.complete(request)

    def describe(self):
        return {"client": "refuses"}


def test_a_refusal_stops_the_negotiation_and_keeps_every_attempt_sent():
    talk = RuleNegotiation(CASE, session(), A, RefusesAt(3, turn("This?", KEEP_ROOM), "not json"), LLM)
    with pytest.raises(BudgetExceededError):
        talk.run()
    assert talk.outcome == "aborted" and len(talk.turns) == 2  # the second turn's first attempt was sent, its retry refused
    assert [len(record.attempts) for record in talk.turns] == [1, 2] and talk.turns[1].attempts[1].api_error.startswith("BudgetExceededError")
    talk = RuleNegotiation(CASE, session(), A, RefusesAt(1), LLM)
    with pytest.raises(BudgetExceededError):
        talk.run()
    assert talk.outcome == "aborted" and talk.turns == []  # nothing was sent, nothing to record


# --- condition B ------------------------------------------------------------------------------------


def test_a_statement_is_one_call_with_the_third_person_prompt():
    client = MockClient(script=[json.dumps({"rule": KEEP_ROOM, "reason": "More room."})])
    state = RuleStatement(CASE, session("stated", order="higher_first"), B, client, LLM)
    assert state.run() == "stated" and state.canonical_hash == canonical_hash(KEEP_ROOM)
    (request,) = client.requests
    assert request.messages == [{"role": "system", "content": statement_prompt(CASE, state.session, B)}]
    assert "PERSON 1" in request.messages[0]["content"] and state.as_dict()["person_1"] == 1  # higher_first: agent 1 is Person 1
    assert request.json_mode and request.temperature == 1.0 and state.as_dict()["reason"] == "More room."


def test_a_statement_may_be_no_rule_and_is_retried_once():
    state = RuleStatement(CASE, session("stated"), B, MockClient(script=['{"reason": "none"}', '{"rule": null}']), LLM)
    assert state.run() == "no_rule" and state.canonical_hash is None and len(state.attempts) == 2
    assert state.attempts[0].parse_error == "missing_rule"
    state = RuleStatement(CASE, session("stated"), B, MockClient(script=["x", '{"rule": 1}']), LLM)
    assert state.run() == "parse_failure" and state.parse_error.startswith("rule_not_an_object")


def test_parse_statement():
    assert parse_statement('{"rule": null, "reason": null}').reason == ""
    with pytest.raises(TurnParseError):
        parse_statement('{"rule": {}, "reason": 3}')


def test_stability_is_the_share_of_repeats_giving_the_commonest_answer():
    assert stability(["a", "a", "b"]) == pytest.approx(2 / 3)
    assert stability(["a", "a"]) == 1.0 and stability(["no_rule", "no_rule", "a"]) == pytest.approx(2 / 3)
    assert math.isnan(stability([]))
