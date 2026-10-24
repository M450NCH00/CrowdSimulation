"""The LLM layer: the mock client, the DeepSeek client (against a fake transport),
pricing, the spend ledger and the budget guard. Nothing here touches the network."""

from __future__ import annotations

import json
import urllib.error
from datetime import datetime, timezone

import pytest

from negsim.configutil import ConfigError
from negsim.llm import (
    BudgetedClient,
    BudgetExceededError,
    BudgetGuard,
    DeepSeekClient,
    LLMFatalError,
    LLMRequest,
    LLMTransientError,
    MockClient,
    PriceTable,
    SpendLedger,
    Usage,
    estimate_prompt_tokens,
)
from negsim.llm.deepseek import API_KEY_ENV, DEFAULT_BASE_URL
from negsim.llm.env import get_setting, read_env_file
from negsim.negotiation import parse_turn_output

FAKE_KEY = "sk-test-0123456789abcdef-NOT-A-REAL-KEY"
PEAK_TUESDAY = datetime(2026, 10, 13, 7, 30, tzinfo=timezone.utc)
OFF_PEAK_TUESDAY = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)
SATURDAY = datetime(2026, 10, 17, 7, 30, tzinfo=timezone.utc)


def request(content="Say hello in JSON.", max_tokens=300, model="deepseek-flash", **kwargs) -> LLMRequest:
    messages = [{"role": "system", "content": "You are terse."}, {"role": "user", "content": content}]
    return LLMRequest(messages=messages, model=model, temperature=1.0, max_tokens=max_tokens, **kwargs)


def api_response(content='{"message": "Hi", "stance": "UNDECIDED"}', prompt=120, completion=15, hit=100) -> bytes:
    return json.dumps(
        {
            "id": "resp-123",
            "model": "deepseek-flash",
            "system_fingerprint": "fp_test",
            "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": content}}],
            "usage": {
                "prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": prompt + completion,
                "prompt_cache_hit_tokens": hit, "prompt_cache_miss_tokens": prompt - hit,
                "completion_tokens_details": {"reasoning_tokens": 0},
            },
        }
    ).encode()


class FakeTransport:
    """Stands in for the HTTP layer and records what would have been sent."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, url, headers, body, timeout):
        self.calls.append({"url": url, "headers": dict(headers), "body": json.loads(body), "timeout": timeout})
        outcome = self.responses.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def client(*responses, **kwargs) -> tuple[DeepSeekClient, FakeTransport]:
    transport = FakeTransport(*responses)
    return DeepSeekClient(FAKE_KEY, transport=transport, sleep=lambda seconds: None, **kwargs), transport


# --- mock client -----------------------------------------------------------------------------


def test_mock_client_is_deterministic_free_and_offline():
    first, second = MockClient(policy="insist").complete(request()), MockClient(policy="insist").complete(request())
    assert first.content == second.content and first.is_mock and first.cost_usd == 0.0
    assert parse_turn_output(first.content).stance.value == "I_GO_FIRST"
    assert first.usage.prompt_tokens > 0 and first.latency_s == 0.0


def test_mock_script_is_replayed_in_order_then_runs_out():
    mock = MockClient(script=["one", None])
    assert mock.complete(request()).content == "one"
    assert mock.complete(request()).content is None
    with pytest.raises(AssertionError, match="ran out"):
        mock.complete(request())
    assert len(mock.requests) == 3


def test_mock_task_priority_policy_ranks_hospital_airport_grocery():
    def ask(own_task, heard):
        messages = [
            {"role": "system", "content": f"You are taking someone to {own_task}. There is another agent taking someone to a location.\n\nReply with JSON."},
            {"role": "user", "content": heard},
        ]
        return parse_turn_output(MockClient(policy="task_priority").complete(LLMRequest(messages, "m", 1.0, 100)).content).stance.value

    assert ask("the ER", "Other agent says: Begin the conversation") == "UNDECIDED"
    assert ask("the ER", "Other agent says: I am headed to the airport.") == "I_GO_FIRST"
    assert ask("buy groceries", "Other agent says: I am headed to the airport.") == "YOU_GO_FIRST"
    assert ask("catch a flight", "Other agent says: I am headed to the airport.") == "UNDECIDED"


def test_unknown_mock_policy():
    with pytest.raises(ValueError, match="unknown mock policy"):
        MockClient(policy="oracle")


# --- DeepSeek client: what is sent -------------------------------------------------------------


def test_request_goes_to_the_chat_completions_endpoint_with_the_documented_body():
    deepseek, transport = client((200, api_response()))
    deepseek.complete(request())
    call = transport.calls[0]
    assert call["url"] == f"{DEFAULT_BASE_URL}/chat/completions"
    assert call["body"] == {
        "model": "deepseek-flash",
        "messages": [{"role": "system", "content": "You are terse."}, {"role": "user", "content": "Say hello in JSON."}],
        "temperature": 1.0,
        "max_tokens": 300,
        "stream": False,
        "thinking": {"type": "disabled"},  # otherwise temperature would have no effect
        "response_format": {"type": "json_object"},
    }
    assert call["headers"]["Authorization"] == f"Bearer {FAKE_KEY}"


def test_thinking_and_json_mode_can_be_switched():
    payload = DeepSeekClient.build_payload(request(thinking=True, json_mode=False))
    assert payload["thinking"] == {"type": "enabled"} and "response_format" not in payload


def test_metadata_is_never_sent_to_the_provider():
    deepseek, transport = client((200, api_response()))
    deepseek.complete(request(metadata={"run_id": "secret-plan", "turn_index": 3}))
    assert "secret-plan" not in json.dumps(transport.calls[0]["body"])


def test_base_url_is_configurable_and_normalised():
    deepseek, transport = client((200, api_response()), base_url="https://example.invalid/v1/")
    deepseek.complete(request())
    assert transport.calls[0]["url"] == "https://example.invalid/v1/chat/completions"


# --- DeepSeek client: what comes back ----------------------------------------------------------


def test_response_is_parsed_including_cache_usage():
    deepseek, _ = client((200, api_response(prompt=120, completion=15, hit=100)))
    response = deepseek.complete(request())
    assert response.content == '{"message": "Hi", "stance": "UNDECIDED"}'
    assert response.usage == Usage(prompt_tokens=120, completion_tokens=15, cache_hit_tokens=100, cache_miss_tokens=20)
    assert (response.finish_reason, response.model, response.response_id, response.system_fingerprint) == (
        "stop", "deepseek-flash", "resp-123", "fp_test",
    )
    assert response.latency_s >= 0.0 and not response.is_mock and response.failed_attempts == 0


def test_empty_content_is_passed_through_for_the_parser_to_reject():
    # "the API may occasionally return empty content" (DeepSeek JSON Output guide).
    body = json.loads(api_response())
    body["choices"][0]["message"]["content"] = None
    deepseek, _ = client((200, json.dumps(body).encode()))
    assert deepseek.complete(request()).content is None


@pytest.mark.parametrize("status", [429, 500, 503])
def test_documented_transient_errors_are_retried(status):
    deepseek, transport = client((status, b'{"error": {"message": "busy"}}'), (200, api_response()))
    response = deepseek.complete(request())
    assert len(transport.calls) == 2 and response.failed_attempts == 1


def test_network_errors_are_retried_then_reported_as_transient():
    deepseek, transport = client(urllib.error.URLError("no route"), TimeoutError("timed out"), ConnectionResetError("reset"))
    with pytest.raises(LLMTransientError, match="after 3 attempts") as error:
        deepseek.complete(request())
    assert len(transport.calls) == 3 and error.value.attempts == 3


@pytest.mark.parametrize(
    "status, text",
    [(400, "Invalid Format"), (401, "Authentication Fails"), (402, "Insufficient Balance"), (422, "Invalid Parameters")],
)
def test_errors_that_retrying_cannot_fix_are_fatal_and_not_retried(status, text):
    deepseek, transport = client((status, json.dumps({"error": {"message": text}}).encode()))
    with pytest.raises(LLMFatalError, match=f"HTTP {status}: {text}"):
        deepseek.complete(request())
    assert len(transport.calls) == 1


def test_an_unreadable_success_body_is_transient():
    deepseek, _ = client((200, b"<html>gateway</html>"))
    with pytest.raises(LLMTransientError, match="unreadable response body"):
        deepseek.complete(request())


# --- the API key -------------------------------------------------------------------------------


def test_the_key_never_appears_in_repr_describe_or_errors():
    echoing = json.dumps({"error": {"message": f"bad key {FAKE_KEY}"}}).encode()
    deepseek, _ = client((401, echoing))
    assert FAKE_KEY not in repr(deepseek) and FAKE_KEY not in json.dumps(deepseek.describe())
    with pytest.raises(LLMFatalError) as error:
        deepseek.complete(request())
    assert FAKE_KEY not in str(error.value) and "<redacted>" in str(error.value)
    flaky, _ = client(urllib.error.URLError(f"proxy said {FAKE_KEY}"), max_retries=0)
    with pytest.raises(LLMTransientError) as error:
        flaky.complete(request())
    assert FAKE_KEY not in str(error.value)


def test_key_is_read_from_the_environment_or_a_dotenv_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(f'# comment\n\n{API_KEY_ENV}="{FAKE_KEY}"\nDEEPSEEK_BASE_URL=https://example.invalid\nnot a setting\n')
    assert read_env_file(env_file) == {API_KEY_ENV: FAKE_KEY, "DEEPSEEK_BASE_URL": "https://example.invalid"}
    from_file = DeepSeekClient.from_env(env_file=env_file)
    assert from_file.base_url == "https://example.invalid" and from_file._api_key == FAKE_KEY
    monkeypatch.setenv(API_KEY_ENV, "sk-from-environment")
    assert get_setting(API_KEY_ENV, env_file) == "sk-from-environment"  # the environment wins


def test_missing_key_is_a_clear_fatal_error(tmp_path):
    with pytest.raises(LLMFatalError, match="DEEPSEEK_API_KEY is not set"):
        DeepSeekClient.from_env(env_file=tmp_path / "absent.env")
    with pytest.raises(LLMFatalError):
        DeepSeekClient("")


# --- pricing -----------------------------------------------------------------------------------


def test_price_table_records_its_source_and_date():
    prices = PriceTable.from_yaml()
    assert prices.source_url == "https://api-docs.deepseek.com/quick_start/pricing"
    assert prices.date_checked == "2026-10-24"  # the pricing check of issue #64 (docs/pricing-check.md)
    assert sorted(prices.models) == ["deepseek-flash", "deepseek-v4-pro"]


@pytest.mark.parametrize(
    "when, tier",
    [
        (PEAK_TUESDAY, "peak"),
        (datetime(2026, 10, 13, 1, 0, tzinfo=timezone.utc), "peak"),
        (datetime(2026, 10, 13, 3, 59, tzinfo=timezone.utc), "peak"),
        (datetime(2026, 10, 13, 4, 0, tzinfo=timezone.utc), "off_peak"),
        (datetime(2026, 10, 13, 5, 59, tzinfo=timezone.utc), "off_peak"),
        (datetime(2026, 10, 13, 10, 0, tzinfo=timezone.utc), "off_peak"),
        (OFF_PEAK_TUESDAY, "off_peak"),
        (SATURDAY, "off_peak"),
    ],
)
def test_peak_hours_are_weekdays_0100_to_0400_and_0600_to_1000_utc(when, tier):
    assert PriceTable.from_yaml().tier_at(when) == tier


def test_cost_uses_cache_hit_miss_and_output_rates():
    prices = PriceTable.from_yaml()
    usage = Usage(prompt_tokens=1_000_000, completion_tokens=1_000_000, cache_hit_tokens=400_000, cache_miss_tokens=600_000)
    peak = prices.cost("deepseek-flash", usage, PEAK_TUESDAY)
    assert peak.tier == "peak" and peak.usd == pytest.approx(0.4 * 0.006 + 0.6 * 0.30 + 1.20)
    off = prices.cost("deepseek-flash", usage, OFF_PEAK_TUESDAY)
    assert off.usd == pytest.approx(peak.usd / 2)  # "Off-peak rates are half of the peak rates"


def test_unsplit_prompt_tokens_are_costed_as_cache_misses():
    prices = PriceTable.from_yaml()
    assert prices.cost("deepseek-flash", Usage(prompt_tokens=1_000_000), PEAK_TUESDAY).usd == pytest.approx(0.30)


def test_worst_case_is_peak_uncached_full_output():
    assert PriceTable.from_yaml().worst_case("deepseek-flash", 1000, 300) == pytest.approx((1000 * 0.30 + 300 * 1.20) / 1e6)


def test_a_model_without_a_price_cannot_be_used():
    with pytest.raises(ConfigError, match="no price is recorded"):
        PriceTable.from_yaml().price_of("deepseek-chat")  # the Phase 1 model name, no longer listed


# --- ledger and budget guard -------------------------------------------------------------------


def guard(tmp_path, cap) -> BudgetGuard:
    return BudgetGuard(SpendLedger(tmp_path / "ledger.jsonl"), cap, PriceTable.from_yaml())


def test_prompt_token_estimate_errs_high():
    messages = [{"role": "user", "content": "x" * 1000}]
    assert estimate_prompt_tokens(messages) == 450 + 8  # 1000 chars * 0.3 * 1.5, plus per-message overhead
    assert estimate_prompt_tokens(messages) > 1000 * 0.3


def test_every_paid_call_is_recorded_with_tokens_and_cost(tmp_path):
    deepseek, _ = client((200, api_response(prompt=120, completion=15, hit=100)), (200, api_response()))
    budgeted = BudgetedClient(deepseek, guard(tmp_path, cap=0.50), now=lambda: PEAK_TUESDAY)
    response = budgeted.complete(request(metadata={"experiment": "e", "run_id": "r1", "turn_index": 0, "attempt": 1}))
    assert response.price_tier == "peak"
    assert response.cost_usd == pytest.approx((100 * 0.006 + 20 * 0.30 + 15 * 1.20) / 1e6)
    budgeted.complete(request())
    entries = SpendLedger(tmp_path / "ledger.jsonl").entries()
    assert len(entries) == 2
    first = entries[0]
    assert (first["experiment"], first["run_id"], first["turn_index"], first["model"]) == ("e", "r1", 0, "deepseek-flash")
    assert (first["prompt_tokens"], first["completion_tokens"], first["prompt_cache_hit_tokens"]) == (120, 15, 100)
    assert first["cost_usd"] == pytest.approx(response.cost_usd) and first["error"] is None
    assert entries[1]["cumulative_usd"] == pytest.approx(first["cost_usd"] + entries[1]["cost_usd"])
    assert FAKE_KEY not in (tmp_path / "ledger.jsonl").read_text()


def test_a_call_that_could_exceed_the_cap_is_refused_before_it_is_sent(tmp_path):
    deepseek, transport = client((200, api_response()))
    budgeted = BudgetedClient(deepseek, guard(tmp_path, cap=0.0001))
    with pytest.raises(BudgetExceededError, match="call refused"):
        budgeted.complete(request(max_tokens=300))  # worst case ~ USD 0.0011 with three possible sends
    assert transport.calls == [] and not (tmp_path / "ledger.jsonl").exists()


def test_the_cap_counts_what_earlier_runs_spent(tmp_path):
    ledger = SpendLedger(tmp_path / "ledger.jsonl")
    ledger.append({"cost_usd": 0.4995, "note": "an earlier session"})
    deepseek, transport = client((200, api_response()))
    budgeted = BudgetedClient(deepseek, BudgetGuard(ledger, 0.50, PriceTable.from_yaml()))
    with pytest.raises(BudgetExceededError):
        budgeted.complete(request())
    assert transport.calls == [] and ledger.total_usd() == pytest.approx(0.4995)
    assert BudgetGuard(ledger, 0.50, PriceTable.from_yaml()).remaining_usd() == pytest.approx(0.0005)


def test_spend_can_never_exceed_the_cap(tmp_path):
    cap, ledger_guard = 0.01, guard(tmp_path, cap=0.01)
    responses = [(200, api_response(prompt=1500, completion=300, hit=0))] * 50
    budgeted = BudgetedClient(client(*responses)[0], ledger_guard, now=lambda: PEAK_TUESDAY)
    made = 0
    with pytest.raises(BudgetExceededError):
        for _ in range(50):
            budgeted.complete(request(content="x" * 4000))
            made += 1
    # Each call costs USD 0.00081 at peak; the tenth is refused because, with its possible
    # resends, it could no longer be guaranteed to fit.
    assert made == 9 and ledger_guard.ledger.total_usd() == pytest.approx(9 * 0.00081)
    assert ledger_guard.ledger.total_usd() <= cap


def test_failed_sends_that_may_have_been_billed_count_at_their_worst_case(tmp_path):
    ledger_guard = guard(tmp_path, cap=0.50)
    deepseek, _ = client(TimeoutError("t"), TimeoutError("t"), TimeoutError("t"))
    with pytest.raises(LLMTransientError):
        BudgetedClient(deepseek, ledger_guard).complete(request())
    entry = ledger_guard.ledger.entries()[0]
    assert entry["cost_is_upper_bound"] and entry["error"].startswith("LLMTransientError")
    assert entry["cost_usd"] == pytest.approx(3 * ledger_guard.worst_case(request()))


def test_a_rejected_request_costs_nothing(tmp_path):
    ledger_guard = guard(tmp_path, cap=0.50)
    deepseek, _ = client((401, b'{"error": {"message": "Authentication Fails"}}'))
    with pytest.raises(LLMFatalError):
        BudgetedClient(deepseek, ledger_guard).complete(request())
    assert ledger_guard.ledger.total_usd() == 0.0 and ledger_guard.ledger.entries()[0]["error"].startswith("LLMFatalError")


def test_guard_refuses_a_model_it_cannot_price(tmp_path):
    deepseek, transport = client((200, api_response()))
    with pytest.raises(ConfigError, match="no price is recorded"):
        BudgetedClient(deepseek, guard(tmp_path, cap=0.50)).complete(request(model="some-new-model"))
    assert transport.calls == []


def test_negative_cap_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        guard(tmp_path, cap=-1.0)


def test_a_cap_scoped_to_an_experiment_counts_that_experiments_calls_only(tmp_path):
    """Issue #30: a pilot has a cap of its own, beside what earlier experiments spent."""
    ledger = SpendLedger(tmp_path / "ledger.jsonl")
    ledger.append({"experiment": "an_earlier_one", "cost_usd": 0.40})
    ledger.append({"experiment": "pilot", "cost_usd": 0.01})
    assert ledger.total_usd() == pytest.approx(0.41) and ledger.total_usd("pilot") == pytest.approx(0.01)
    scoped = BudgetGuard(ledger, 0.05, PriceTable.from_yaml(), scope="pilot")
    assert scoped.remaining_usd() == pytest.approx(0.04)
    deepseek, transport = client((200, api_response()))
    budgeted = BudgetedClient(deepseek, scoped)
    budgeted.complete(request(metadata={"session_id": "s1"}))  # unlabelled: recorded under the scope
    assert len(transport.calls) == 1 and ledger.entries()[-1]["experiment"] == "pilot"
    assert budgeted.describe()["budget_scope"] == "pilot"
    with pytest.raises(BudgetExceededError, match="labelled for experiment 'another'"):
        budgeted.complete(request(metadata={"experiment": "another"}))
    with pytest.raises(BudgetExceededError, match=r"ledger\.jsonl, "):  # unscoped, 0.41 counts against 0.05
        BudgetedClient(client((200, api_response()))[0], BudgetGuard(ledger, 0.05, PriceTable.from_yaml())).complete(request())
    tight = BudgetGuard(ledger, ledger.total_usd("pilot") + 0.0001, PriceTable.from_yaml(), scope="pilot")
    with pytest.raises(BudgetExceededError, match="ledger.jsonl for pilot"):
        BudgetedClient(client((200, api_response()))[0], tight).complete(request())
