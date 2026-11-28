"""Issue #144 (RF-53), stage 1: the static probe runner, its frozen probe set and its scorer.

Everything here runs on the mock client or on a fake transport; nothing touches the network.
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone

import pytest
import yaml

from negsim.configutil import PACKAGE_ROOT, REPO_ROOT, ConfigError
from negsim.llm import BudgetedClient, BudgetGuard, DeepSeekClient, PriceTable, SpendLedger
from negsim.probe import runner as R
from negsim.probe import score as S

CONFIG = "configs/probe/rf53_stage1_frames_probe.yaml"
GIT = {"commit": "test", "dirty": False}
OFF_PEAK = datetime(2026, 11, 28, 12, 0, tzinfo=timezone.utc)  # a Saturday
PEAK = datetime(2026, 11, 27, 7, 30, tzinfo=timezone.utc)  # a Friday, 07:30 UTC
FAKE_KEY = "sk-test-0123456789abcdef-NOT-A-REAL-KEY"


def config(**changes) -> R.ProbeConfig:
    raw = yaml.safe_load((PACKAGE_ROOT / CONFIG).read_text(encoding="utf-8"))
    raw.update(changes)
    return R.ProbeConfig.from_raw(raw, CONFIG)


def quiet(_):
    return None


# --- the probe set -------------------------------------------------------------------------------


def test_the_probe_set_has_rf43s_twenty_probes_in_its_seven_groups():
    probes = config().probes
    assert [p["id"] for p in probes.probes] == [f"p{n:02d}" for n in range(1, 21)]
    assert {g: sum(p["group"] == g for p in probes.probes) for g in probes.groups} == {"A": 3, "B": 3, "C": 3, "D": 3, "E": 4, "F": 2, "G": 2}


def test_every_expected_answer_is_probes_md_s():
    """Each probe's first correct label is the answer RF-43 wrote in probes.md ("**Expected: ...**")."""
    text = (REPO_ROOT / "literature" / "frames-of-reference" / "probes.md").read_text(encoding="utf-8")
    expected = {int(n): answer for n, answer in re.findall(r"^(\d+)\. .*?\*\*Expected: (.+?)\*\*", text, flags=re.M)}
    assert sorted(expected) == list(range(1, 21))
    for probe in config().probes.probes:
        label, _ = S.read_label(probe["kind"], expected[int(probe["id"][1:])])
        assert label in probe["correct"], (probe["id"], expected[int(probe["id"][1:])], label)


def test_group_c_adds_resolve_v9s_facing_note_word_for_word_and_nothing_else():
    probes = config().probes
    template = yaml.safe_load((PACKAGE_ROOT / "negsim" / "negotiation" / "templates" / "resolve_v9.yaml").read_text(encoding="utf-8"))
    note = re.search(r"\(Person \{n\} is facing you.*?\)", template["view"]["heard_seen_facing"]).group(0).replace("{n}", "2")
    for c, plain in (("p07", "p01"), ("p08", "p04"), ("p09", "p05")):
        with_note, without = probes.message(probes.by_id(c)), probes.message(probes.by_id(plain))
        assert note in with_note and with_note.replace(f" {note}", "") == without


def test_an_edited_probe_set_is_refused(tmp_path):
    copy = tmp_path / "frames_probes_v1.yaml"
    shutil.copy(PACKAGE_ROOT / "configs" / "probe" / "frames_probes_v1.yaml", copy)
    copy.write_text(copy.read_text(encoding="utf-8").replace("Which way do you move", "Where do you move", 1), encoding="utf-8")
    with pytest.raises(ConfigError, match="frozen"):
        config(probes=str(copy))


def test_the_hash_does_not_depend_on_line_endings(tmp_path):
    crlf = tmp_path / "frames_probes_v1.yaml"
    crlf.write_bytes((PACKAGE_ROOT / "configs" / "probe" / "frames_probes_v1.yaml").read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    assert config(probes=str(crlf)).probes.sha256 == config().probes.sha256


def test_the_config_is_rf53s_design():
    c = config()
    assert c.repeats == 10 and [(a.name, a.thinking) for a in c.arms] == [("thinking_off", False), ("thinking_on", True)]
    assert c.llm["model"] == "deepseek-flash" and c.llm["temperature"] == 1.0
    assert c.arms[0].max_tokens == 300  # RF-40's and probes.md's
    assert len(R.calls(c)) == 400 and R.plan(c)["pilot_calls"] == 40
    request = R.request_for(c, R.calls(c)[0])
    assert request.json_mode is False and [m["role"] for m in request.messages] == ["user"]
    assert "probe_id" in request.metadata and "correct" not in json.dumps(dict(request.metadata))


def test_the_pilot_is_one_repeat_of_every_probe_in_both_arms():
    first = R.calls(config())[:40]
    assert {c.repeat for c in first} == {1}
    assert sorted((c.arm.name, c.probe["id"]) for c in first) == sorted((a, f"p{n:02d}") for a in ("thinking_off", "thinking_on") for n in range(1, 21))


# --- the scorer ----------------------------------------------------------------------------------


@pytest.mark.parametrize("kind, reply, label, ambiguous", [
    ("side", "Left.\nBecause they move to their left.", "left", False),
    ("side", "**Right**\nWhy.", "right", False),
    ("side", "Answer: left", "left", False),
    ("side", "I move to my left (their right).", "left", True),
    ("side", "Cannot tell.\nNo heading is given.", "cannot_tell", False),
    ("side", "It can't be determined from the information given.", "cannot_tell", False),
    ("side", "Not enough information to say left or right.", "cannot_tell", False),
    ("side", "\n\n  Right\n", "right", False),
    ("side", "", "empty", False),
    ("side", None, "empty", False),
    ("side", "Straight ahead.", "unclear", False),
    ("their_side", '"Your right."', "right", False),
    ("their_side", "I'll pass on your left.", "left", False),
    ("their_side", "On my left.", "unclear", False),
    ("wall", "The north wall.", "north", False),
    ("named_side", "The shop side.", "shop", False),
    ("lane", "Lane 4.", "4", False),
    ("lane", "4", "4", False),
    ("lane", "I stay in lane 3.", "3", False),
    ("lane", "From lane 3 to lane 4.", "3", True),
    ("lane", "Lane 3.5", "unclear", False),
    ("lane", "Lane 12", "unclear", False),
])
def test_the_first_line_is_read_for_one_label(kind, reply, label, ambiguous):
    assert S.read_label(kind, S.first_line(reply)) == (label, ambiguous)


def test_a_score_is_correct_wrong_or_unclear():
    probe = config().probes.by_id("p13")  # cannot tell is right; left and right are invented headings
    assert S.score(probe, "Cannot tell.").outcome == S.CORRECT
    assert S.score(probe, "Left.").outcome == S.WRONG
    assert S.score(probe, "Behind me.").outcome == S.UNCLEAR
    lane = config().probes.by_id("p19")
    assert [S.score(lane, f"Lane {n}.").outcome for n in (1, 2, 3, 4, 5)] == [S.UNCLEAR, S.WRONG, S.CORRECT, S.CORRECT, S.UNCLEAR]


# --- running on the mock -------------------------------------------------------------------------


def run(tmp_path, c=None, **kwargs):
    return R.run_probe(c or config(), out_root=tmp_path, report=quiet, git=GIT, **kwargs)


def summary(tmp_path, c=None):
    return json.loads((tmp_path / (c or config()).experiment_name / R.SUMMARY_FILE).read_text(encoding="utf-8"))


def test_the_mock_rehearsal_scores_every_probe_right_and_costs_nothing(tmp_path):
    result = run(tmp_path)
    assert result.status == R.STATUS_COMPLETED and result.sent == 400 and result.cost_usd == 0.0
    s = summary(tmp_path)
    for arm in s["per_arm"].values():
        assert (arm["n"], arm["correct"], arm["wrong"], arm["unclear"]) == (200, 200, 0, 0)
    assert s["per_arm"]["thinking_off"]["reasoning_tokens"]["max"] == 0 and s["per_arm"]["thinking_on"]["reasoning_tokens"]["min"] > 0


def test_a_mock_that_always_answers_wrong_is_scored_wrong(tmp_path):
    raw = yaml.safe_load((PACKAGE_ROOT / CONFIG).read_text(encoding="utf-8"))
    raw["llm"]["mock_policy"] = "probe_wrong"
    run(tmp_path, R.ProbeConfig.from_raw(raw, CONFIG))
    assert all(arm["wrong"] == 200 for arm in summary(tmp_path)["per_arm"].values())


def test_records_keep_the_message_the_reply_and_the_reasoning_only_with_thinking_on(tmp_path):
    run(tmp_path, limit=40)
    base = tmp_path / config().experiment_name / R.CALLS_DIR
    off = json.loads((base / "thinking_off" / "p01_r01.json").read_text(encoding="utf-8"))
    on = json.loads((base / "thinking_on" / "p01_r01.json").read_text(encoding="utf-8"))
    assert off["messages"][0]["content"] == config().probes.message(config().probes.by_id("p01"))
    assert off["reasoning_content"] is None and off["request"]["thinking"] is False and off["request"]["max_tokens"] == 300
    assert on["reasoning_content"].startswith("Mock reasoning") and on["request"]["thinking"] is True
    assert on["score"]["outcome"] == S.CORRECT and on["is_mock"] is True


def test_a_limited_run_resumes_without_sending_a_recorded_call_again(tmp_path):
    first = run(tmp_path, limit=40)
    assert first.status == R.STATUS_PARTIAL and first.sent == 40
    second = run(tmp_path)
    assert second.sent == 360 and second.skipped == 40 and second.status == R.STATUS_COMPLETED
    assert run(tmp_path).sent == 0
    lines = (tmp_path / config().experiment_name / R.INVOCATIONS_FILE).read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["sent"] for line in lines] == [40, 360, 0]


# --- the paid path, on a fake transport ----------------------------------------------------------


def body(content="Left.\nWhy.", reasoning=None, reasoning_tokens=0, fingerprint="bc19ba97cbe016479903222bb1578db6") -> bytes:
    message = {"role": "assistant", "content": content, **({"reasoning_content": reasoning} if reasoning else {})}
    return json.dumps({
        "id": "r", "model": "deepseek-flash", "system_fingerprint": fingerprint,
        "choices": [{"index": 0, "finish_reason": "stop", "message": message}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 20 + reasoning_tokens, "prompt_cache_hit_tokens": 0,
                  "prompt_cache_miss_tokens": 100, "completion_tokens_details": {"reasoning_tokens": reasoning_tokens}},
    }).encode()


class Transport:
    def __init__(self, *bodies):
        self.bodies, self.sent = list(bodies), []

    def __call__(self, url, headers, data, timeout):
        self.sent.append(json.loads(data))
        status, raw = self.bodies.pop(0) if self.bodies else (200, body())
        return status, raw


def paid(tmp_path, cap, transport, when=OFF_PEAK):
    guard = BudgetGuard(SpendLedger(tmp_path / "ledger.jsonl"), cap, PriceTable.from_yaml(), scope=config().experiment_name)
    inner = DeepSeekClient(FAKE_KEY, transport=transport, sleep=lambda _: None, max_retries=0)
    return BudgetedClient(inner, guard, now=lambda: when)


def test_a_paid_client_sends_nothing_without_confirm(tmp_path):
    transport = Transport()
    result = run(tmp_path, client=paid(tmp_path, 1.0, transport))
    assert result.status == R.STATUS_AWAITING and transport.sent == [] and not (tmp_path / "ledger.jsonl").exists()


def test_a_cap_of_zero_refuses_every_paid_call(tmp_path):
    transport = Transport()
    result = run(tmp_path, client=paid(tmp_path, 0.0, transport), confirm=True, now=lambda: OFF_PEAK)
    assert result.status == R.STATUS_CAP and transport.sent == [] and result.sent == 0


def test_the_committed_cap_is_the_one_claude_md_records_for_issue_144_stage_1():
    """The config held a cap of 0 until the user's approval of 2026-11-28 (USD 0.50) was recorded."""
    recorded = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "**Approved for issue #144 only, stage 1, 2026-11-28:**" in recorded and "a cap of **USD 0.50**" in recorded
    assert config().budget["cap_usd"] == 0.50


def test_no_paid_call_in_peak_hours_without_allow_peak(tmp_path):
    transport = Transport()
    result = run(tmp_path, client=paid(tmp_path, 1.0, transport, PEAK), confirm=True, now=lambda: PEAK)
    assert result.status == R.STATUS_PEAK and transport.sent == []
    result = run(tmp_path, client=paid(tmp_path, 1.0, transport, PEAK), confirm=True, now=lambda: PEAK, allow_peak=True, limit=1)
    assert result.sent == 1 and len(transport.sent) == 1


def test_a_paid_pilot_sends_thinking_as_configured_keeps_the_reasoning_and_checks_the_fingerprint(tmp_path):
    transport = Transport(*[(200, body())] * 20, *[(200, body(reasoning="Their left is my right.", reasoning_tokens=300))] * 20)
    result = run(tmp_path, client=paid(tmp_path, 1.0, transport), confirm=True, now=lambda: OFF_PEAK, limit=40)
    assert result.sent == 40 and len(transport.sent) == 40
    assert [p["thinking"]["type"] for p in transport.sent] == ["disabled"] * 20 + ["enabled"] * 20
    assert [p["max_tokens"] for p in transport.sent] == [300] * 20 + [8000] * 20
    assert all("response_format" not in p for p in transport.sent)
    s = summary(tmp_path)
    assert s["fingerprint_matches"] is True and s["per_arm"]["thinking_on"]["reasoning_tokens"]["median"] == 300
    on = json.loads((tmp_path / config().experiment_name / R.CALLS_DIR / "thinking_on" / "p01_r01.json").read_text(encoding="utf-8"))
    assert on["reasoning_content"] == "Their left is my right." and on["is_mock"] is False
    ledger = [json.loads(line) for line in (tmp_path / "ledger.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(ledger) == 40 and {e["experiment"] for e in ledger} == {config().experiment_name}
    assert math_close(sum(e["cost_usd"] for e in ledger), s["cost_usd"])


def math_close(a, b):
    return abs(a - b) < 1e-6


def test_a_changed_fingerprint_is_reported(tmp_path):
    transport = Transport(*[(200, body(fingerprint="fp_other"))] * 2)
    run(tmp_path, client=paid(tmp_path, 1.0, transport), confirm=True, now=lambda: OFF_PEAK, limit=2)
    assert summary(tmp_path)["fingerprint_matches"] is False


def test_a_failed_call_is_recorded_set_aside_and_sent_again(tmp_path):
    transport = Transport((503, b'{"error": {"message": "overloaded"}}'))
    first = run(tmp_path, client=paid(tmp_path, 1.0, transport), confirm=True, now=lambda: OFF_PEAK, limit=1)
    assert first.failed == 1 and first.status == R.STATUS_PARTIAL
    path = tmp_path / config().experiment_name / R.CALLS_DIR / "thinking_off" / "p01_r01.json"
    assert json.loads(path.read_text(encoding="utf-8"))["api_error"].startswith("LLMTransientError")
    second = run(tmp_path, client=paid(tmp_path, 1.0, transport), confirm=True, now=lambda: OFF_PEAK, limit=1)
    assert second.sent == 1 and path.with_name("p01_r01.failed1.json").exists()
    assert json.loads(path.read_text(encoding="utf-8"))["api_error"] is None


# --- the report ----------------------------------------------------------------------------------

from negsim.probe import report as P  # noqa: E402


def test_fisher_and_wilson_give_known_values():
    assert abs(P.fisher_two_sided(8, 2, 1, 5) - 0.03497) < 1e-4  # R: fisher.test(matrix(c(8,1,2,5),2))
    assert P.fisher_two_sided(5, 5, 5, 5) == 1.0
    low, high = P.wilson(0, 10)
    assert low == 0.0 and abs(high - 0.2775) < 1e-4
    low, high = P.wilson(10, 10)
    assert abs(low - 0.7225) < 1e-4 and high == 1.0


def test_the_report_is_built_from_the_records(tmp_path):
    run(tmp_path)
    text = P.report(tmp_path / config().experiment_name)
    assert "Records: 400 of 400 planned" in text
    assert "| all | 200/200 (1.00; 0.98 to 1.00) | 200/200 (1.00; 0.98 to 1.00) | 1.00 |" in text
    assert "| p13 | 0/10 | 0/10 |" in text  # the mock always answers right: no invented heading
    assert "cut off at the reply cap 0" in text
