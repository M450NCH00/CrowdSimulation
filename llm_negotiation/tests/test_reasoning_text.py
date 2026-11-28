"""Issue #144 (RF-53), task 2: the reasoning text of thinking mode is kept, and only then.

DeepSeek returns its chain of thought as ``message.reasoning_content`` in thinking mode
(``refs/ln_deepseek_thinking_mode_docs_2026-11-28.txt``). The client used to drop it. Now the response,
the attempt record and a session's record carry it, and a call with thinking off writes exactly what
it wrote before. Nothing here touches the network.
"""

from __future__ import annotations

import json

from negsim.llm import DeepSeekClient, LLMRequest, MockClient
from negsim.negotiation.protocol import Attempt, request_with_retry
from negsim.resolution import experiment as E
from negsim.runlog.schema import ATTEMPT_KEYS
from test_encounter_protocol import GIT

FAKE_KEY = "sk-test-0123456789abcdef-NOT-A-REAL-KEY"
REPLY = '{"message": "Hi", "stance": "UNDECIDED"}'


def request(thinking: bool) -> LLMRequest:
    return LLMRequest(
        messages=[{"role": "user", "content": "Say hello in JSON."}], model="deepseek-flash",
        temperature=1.0, max_tokens=300, thinking=thinking,
    )


def api_body(reasoning=None, reasoning_tokens=0) -> bytes:
    message = {"role": "assistant", "content": REPLY}
    if reasoning is not None:
        message["reasoning_content"] = reasoning
    return json.dumps({
        "id": "resp-1", "model": "deepseek-flash", "system_fingerprint": "fp_test",
        "choices": [{"index": 0, "finish_reason": "stop", "message": message}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 15 + reasoning_tokens, "prompt_cache_hit_tokens": 0,
                  "prompt_cache_miss_tokens": 10, "completion_tokens_details": {"reasoning_tokens": reasoning_tokens}},
    }).encode()


def deepseek(body: bytes) -> DeepSeekClient:
    return DeepSeekClient(FAKE_KEY, transport=lambda url, headers, data, timeout: (200, body), sleep=lambda _: None)


def test_the_client_keeps_the_reasoning_text_that_thinking_mode_returns():
    response = deepseek(api_body("Facing me, their left is my right.", 9)).complete(request(thinking=True))
    assert response.reasoning_content == "Facing me, their left is my right."
    assert response.usage.reasoning_tokens == 9 and response.content == REPLY


def test_a_reply_without_reasoning_has_none():
    assert deepseek(api_body()).complete(request(thinking=False)).reasoning_content is None
    assert deepseek(api_body(reasoning=None)).complete(request(thinking=True)).reasoning_content is None


def test_the_mock_gives_a_reasoning_text_only_with_thinking_on():
    off = MockClient(script=[REPLY]).complete(request(thinking=False))
    assert off.reasoning_content is None and off.usage.reasoning_tokens == 0
    assert off.usage.completion_tokens == len(REPLY) * 3 // 10 + (len(REPLY) * 3 % 10 > 0)  # as before #144
    on = MockClient(script=[REPLY]).complete(request(thinking=True))
    assert on.reasoning_content.startswith("Mock reasoning (no model was called)")
    assert on.usage.reasoning_tokens > 0 and on.usage.completion_tokens == off.usage.completion_tokens + on.usage.reasoning_tokens
    assert MockClient(script=[REPLY]).complete(request(thinking=True)) .reasoning_content == on.reasoning_content  # reproducible


def test_an_attempt_record_has_the_key_only_when_there_is_a_reasoning_text():
    plain = Attempt(attempt=1, prompt_messages=[], request={}, wall_clock_utc="t")
    assert tuple(plain.as_dict()) == ATTEMPT_KEYS  # exactly the keys, in the order, of before #144
    thought = Attempt(attempt=1, prompt_messages=[], request={}, wall_clock_utc="t", reasoning_content="r")
    assert tuple(thought.as_dict()) == (*ATTEMPT_KEYS, "reasoning_content") and thought.as_dict()["reasoning_content"] == "r"


def test_request_with_retry_records_the_reasoning_in_each_attempt():
    for thinking, expected in ((False, None), (True, str)):
        reply = request_with_retry(
            MockClient(script=[REPLY]), [{"role": "user", "content": "hello"}], "deepseek-flash", 1.0, 300, thinking,
            {}, lambda raw: raw, "again",
        )
        record = reply.attempts[0].as_dict()
        if expected is None:
            assert "reasoning_content" not in record
        else:
            assert isinstance(record["reasoning_content"], str)


def config(name: str, thinking: str):
    return E.ResolutionConfig.from_raw({
        "layer": "resolution", "experiment_name": name, "cases": {"ids": ["head_on_02dfbadb@2"]}, "conditions": ["talk"],
        "design": {"seed": 1, "factors": {"age_pair": ["same"], "gender_pair": ["p1_female"], "task": ["p1_urgent"],
                                          "demographics_visible": [True], "mapping": ["p1_lower"]}},
        "llm": {"client": "mock", "mock_policy": "resolution_rehearsal_v1", "thinking": thinking},
    })


def session_records(tmp_path, name, thinking):
    E.run_resolution(config(name, thinking), out_root=tmp_path, report=lambda _: None, git=GIT)
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((tmp_path / name / "sessions").glob("*.json"))]


def test_a_resolution_session_with_thinking_off_carries_no_reasoning_and_with_it_on_every_attempt_does(tmp_path):
    off = session_records(tmp_path, "off", "disabled")
    assert off and "reasoning_content" not in json.dumps(off)
    on = session_records(tmp_path, "on", "enabled")
    attempts = [a for record in on for a in _attempts(record)]
    assert attempts and all(isinstance(a.get("reasoning_content"), str) for a in attempts)


def _attempts(node):
    """Every attempt record anywhere in a session record."""
    if isinstance(node, dict):
        if "attempt" in node and "raw_output" in node:
            yield node
        for value in node.values():
            yield from _attempts(value)
    elif isinstance(node, list):
        for value in node:
            yield from _attempts(value)
