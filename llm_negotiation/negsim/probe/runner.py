"""RF-53, stage 1 (issue #144): RF-43's static probes, sent with thinking off and on.

    python -m negsim.probe configs/probe/rf53_stage1_frames_probe.yaml --plan
    python -m negsim.probe configs/probe/rf53_stage1_frames_probe.yaml                      # mock, runs_mock/
    python -m negsim.probe configs/probe/rf53_stage1_frames_probe.yaml --client deepseek    # preview only
    python -m negsim.probe configs/probe/rf53_stage1_frames_probe.yaml --client deepseek --confirm --limit 40

Each probe (``configs/probe/frames_probes_v1.yaml``) is one user message with one right answer, sent
``repeats`` times in each **arm** (thinking off, thinking on). There is no simulation and no
conversation: a call is one request and one reply, and the reply is scored by keyword
(:mod:`negsim.probe.score`).

**The order of calls** is repeat by repeat, and within a repeat arm by arm and probe by probe, so
``--limit 40`` is the pilot RF-53 asks for: one repeat of every probe in both arms.

**Money.** The mock client is the default and costs nothing. With ``--client deepseek``:

- nothing is sent without ``--confirm`` (the plan is printed and written instead);
- every call goes through the budget guard, capped on this experiment's own calls (``budget.cap_usd``);
  the cap is 0 in the config until the user's approval and cap are recorded in ``CLAUDE.md``;
- **no call in DeepSeek's peak hours** (``configs/llm/deepseek_pricing.yaml``) unless
  ``--allow-peak``; checked before each call, so a run that reaches peak hours stops there;
- each reply's model fingerprint is compared with ``expected_fingerprint`` (RF-40's) in the summary.

**Records.** One JSON file per call (``calls/<arm>/<probe>_r<NN>.json``): the exact message, the
request settings, the raw reply, the reasoning text (thinking on), tokens, cost, fingerprint and the
score. It is written once and never rewritten. Running the config again resumes: a call with a
record is not sent again, and one that failed is set aside (``.failed<N>.json``) and sent again.
``results.csv`` (a row per call) and ``summary.json`` are rewritten from the records at the end of
every invocation, and ``invocations.jsonl`` gets a line per invocation.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from ..configutil import PACKAGE_ROOT, ConfigError, as_choice, as_number, check_keys, load_yaml, resolve_path
from ..llm.base import LLMClient, LLMError, LLMFatalError, LLMRequest, LLMResponse
from ..llm.budget import BudgetedClient, BudgetExceededError, BudgetGuard, SpendLedger
from ..llm.deepseek import DeepSeekClient
from ..llm.mock import MockClient
from ..llm.pricing import PEAK, PriceTable
from ..negotiation.prompts import template_sha256
from . import score as S

LAYER = "probe"
SCHEMA_VERSION = 1
RECORD_VERSION = 1
CLIENTS = ("mock", "deepseek")
RUNS_DIR, MOCK_RUNS_DIR = PACKAGE_ROOT / "runs", PACKAGE_ROOT / "runs_mock"
CALLS_DIR, RESULTS_FILE, SUMMARY_FILE = "calls", "results.csv", "summary.json"
CONFIG_FILE, PLAN_FILE, INVOCATIONS_FILE = "config.json", "plan.json", "invocations.jsonl"
STATUS_COMPLETED, STATUS_PARTIAL = "completed", "partial"
STATUS_AWAITING, STATUS_PEAK, STATUS_CAP, STATUS_FAILED = (
    "awaiting_confirmation", "refused_peak_hours", "stopped_at_cap", "stopped_on_error")
RESULT_COLUMNS = (
    "call_id", "arm", "thinking", "probe_id", "group", "kind", "repeat", "label", "outcome", "ambiguous",
    "first_line", "finish_reason", "prompt_tokens", "completion_tokens", "reasoning_tokens",
    "reasoning_chars", "cost_usd", "price_tier", "system_fingerprint", "latency_s", "started_utc",
)


def is_probe_config(raw: Any) -> bool:
    return isinstance(raw, Mapping) and raw.get("layer") == LAYER


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def _append_jsonl(path: Path, row: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def file_sha256(path: Path) -> str:
    """As a prompt template's (``negotiation.prompts.template_sha256``): of the text with line endings
    normalised, so that a CRLF checkout on Windows hashes the same."""
    return template_sha256(path)


# --- the probe set and the config ----------------------------------------------------------------


@dataclass(frozen=True)
class ProbeSet:
    name: str
    path: str
    sha256: str
    answer_line: str
    groups: Mapping[str, str]
    probes: tuple[Mapping[str, Any], ...]

    def message(self, probe: Mapping[str, Any]) -> str:
        """The whole user message of ``probe``: its prompt, then the answer instruction."""
        return f"{probe['prompt'].strip()}\n\n{self.answer_line.strip()}"

    def by_id(self, probe_id: str) -> Mapping[str, Any]:
        return next(probe for probe in self.probes if probe["id"] == probe_id)

    @classmethod
    def load(cls, path: str, expected_sha256: str) -> "ProbeSet":
        resolved = resolve_path(path)
        raw = load_yaml(resolved)
        where = path
        check_keys(raw, where, ("schema_version", "name", "source", "answer_line", "groups", "probes"))
        found = file_sha256(resolved)
        if found != expected_sha256:
            raise ConfigError(
                f"{where}: SHA-256 {found} is not the config's probes_sha256 {expected_sha256}; a probe set is "
                "frozen, so a wording change needs a new version, not an edit"
            )
        groups = dict(check_keys(raw["groups"], f"{where}.groups", (), list(raw["groups"])))
        probes, seen = [], set()
        for index, probe in enumerate(raw["probes"]):
            at = f"{where}.probes[{index}]"
            check_keys(probe, at, ("id", "group", "kind", "correct", "wrong", "prompt"))
            if probe["id"] in seen:
                raise ConfigError(f"{at}: duplicate id {probe['id']!r}")
            seen.add(probe["id"])
            as_choice(probe["kind"], f"{at}.kind", S.KINDS)
            if probe["group"] not in groups:
                raise ConfigError(f"{at}.group: {probe['group']!r} is not one of the groups {sorted(groups)}")
            correct, wrong = [str(x) for x in probe["correct"]], [str(x) for x in probe["wrong"]]
            if not correct or set(correct) & set(wrong):
                raise ConfigError(f"{at}: correct must be non-empty and share no label with wrong")
            probes.append({**probe, "correct": correct, "wrong": wrong})
        return cls(str(raw["name"]), path, found, str(raw["answer_line"]), groups, tuple(probes))


@dataclass(frozen=True)
class Arm:
    name: str
    thinking: bool
    max_tokens: int


@dataclass(frozen=True)
class ProbeConfig:
    experiment_name: str
    issue: int
    description: str
    probes: ProbeSet
    repeats: int
    arms: tuple[Arm, ...]
    llm: Mapping[str, Any]
    budget: Mapping[str, Any]
    expected_fingerprint: Optional[str]
    source: str

    @classmethod
    def load(cls, path: Path | str) -> "ProbeConfig":
        return cls.from_raw(load_yaml(resolve_path(path)), str(path))

    @classmethod
    def from_raw(cls, raw: Any, source: str = "<raw>") -> "ProbeConfig":
        where = source
        check_keys(raw, where, ("schema_version", "layer", "experiment_name", "issue", "probes", "probes_sha256", "repeats", "arms", "llm", "budget"),
                   ("description", "expected_fingerprint"))
        if raw["layer"] != LAYER or raw["schema_version"] != SCHEMA_VERSION:
            raise ConfigError(f"{where}: expected layer {LAYER!r} and schema_version {SCHEMA_VERSION}")
        repeats = int(as_number(raw["repeats"], f"{where}.repeats", minimum=1))
        arms, names = [], set()
        for index, arm in enumerate(raw["arms"]):
            at = f"{where}.arms[{index}]"
            check_keys(arm, at, ("name", "thinking", "max_tokens"))
            if arm["name"] in names:
                raise ConfigError(f"{at}: duplicate arm name {arm['name']!r}")
            names.add(arm["name"])
            thinking = as_choice(arm["thinking"], f"{at}.thinking", ("disabled", "enabled")) == "enabled"
            arms.append(Arm(str(arm["name"]), thinking, int(as_number(arm["max_tokens"], f"{at}.max_tokens", minimum=1))))
        if not arms:
            raise ConfigError(f"{where}.arms: at least one arm is needed")
        llm = check_keys(raw["llm"], f"{where}.llm", ("model", "temperature"), ("client", "mock_policy", "transport_retries"))
        budget = check_keys(raw["budget"], f"{where}.budget", ("cap_usd",), ("ledger",))
        policy = str(llm.get("mock_policy", "probe_expected"))
        if policy not in MOCK_POLICIES:
            raise ConfigError(f"{where}.llm.mock_policy: expected one of {sorted(MOCK_POLICIES)}, got {policy!r}")
        return cls(
            experiment_name=str(raw["experiment_name"]),
            issue=int(raw["issue"]),
            description=str(raw.get("description", "")).strip(),
            probes=ProbeSet.load(str(raw["probes"]), str(raw["probes_sha256"])),
            repeats=repeats,
            arms=tuple(arms),
            llm={
                "client": as_choice(llm.get("client", "mock"), f"{where}.llm.client", CLIENTS),
                "mock_policy": policy,
                "model": str(llm["model"]),
                "temperature": as_number(llm["temperature"], f"{where}.llm.temperature", minimum=0.0),
                "transport_retries": int(as_number(llm.get("transport_retries", 2), f"{where}.llm.transport_retries", minimum=0)),
            },
            budget={
                "cap_usd": as_number(budget["cap_usd"], f"{where}.budget.cap_usd", minimum=0.0),
                "ledger": str(budget.get("ledger", "spend_ledger.jsonl")),
            },
            expected_fingerprint=(str(raw["expected_fingerprint"]) if raw.get("expected_fingerprint") else None),
            source=source,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "experiment_name": self.experiment_name, "issue": self.issue, "description": self.description,
            "probes": {"path": self.probes.path, "name": self.probes.name, "sha256": self.probes.sha256, "n": len(self.probes.probes)},
            "repeats": self.repeats,
            "arms": [{"name": a.name, "thinking": "enabled" if a.thinking else "disabled", "max_tokens": a.max_tokens} for a in self.arms],
            "llm": dict(self.llm), "budget": dict(self.budget), "expected_fingerprint": self.expected_fingerprint,
            "source": self.source,
        }


# --- the calls -----------------------------------------------------------------------------------


@dataclass(frozen=True)
class Call:
    call_id: str
    arm: Arm
    probe: Mapping[str, Any]
    repeat: int

    @property
    def path(self) -> str:
        return f"{CALLS_DIR}/{self.arm.name}/{self.probe['id']}_r{self.repeat:02d}.json"


def calls(config: ProbeConfig) -> list[Call]:
    """Every call, repeat by repeat, then arm by arm, then probe by probe (so the first
    ``len(arms) * len(probes)`` calls are one repeat of everything: the pilot)."""
    return [
        Call(f"{arm.name}/{probe['id']}_r{repeat:02d}", arm, probe, repeat)
        for repeat in range(1, config.repeats + 1)
        for arm in config.arms
        for probe in config.probes.probes
    ]


def request_for(config: ProbeConfig, call: Call) -> LLMRequest:
    return LLMRequest(
        messages=[{"role": "user", "content": config.probes.message(call.probe)}],
        model=config.llm["model"],
        temperature=config.llm["temperature"],
        max_tokens=call.arm.max_tokens,
        json_mode=False,
        thinking=call.arm.thinking,
        # Labels for the spend ledger; never sent to the provider (LLMRequest.metadata).
        metadata={"experiment": config.experiment_name, "issue": config.issue, "call_id": call.call_id,
                  "arm": call.arm.name, "probe_id": call.probe["id"], "repeat": call.repeat},
    )


def plan(config: ProbeConfig, prices: Optional[PriceTable] = None) -> dict[str, Any]:
    """The calls and their cost: the guard's worst case (every call at the peak rate, uncached, with the
    whole reply cap used) and rough estimates at several reasoning lengths, off-peak."""
    prices = prices or PriceTable.from_yaml()
    price = prices.price_of(config.llm["model"])
    guard = BudgetGuard(SpendLedger(Path("unused")), 0.0, prices)
    every = calls(config)
    per_arm: dict[str, dict[str, Any]] = {}
    for arm in config.arms:
        mine = [c for c in every if c.arm.name == arm.name]
        worst = math.fsum(guard.worst_case(request_for(config, c)) for c in mine)
        prompt_tokens = [math.ceil(len(config.probes.message(c.probe)) * 0.3) for c in mine]
        reply_tokens = 40  # a one-line answer and one sentence
        estimate = lambda reasoning: math.fsum(  # noqa: E731
            (p * price.input_cache_miss.off_peak + (reply_tokens + reasoning) * price.output.off_peak) / 1e6 for p in prompt_tokens
        )
        per_arm[arm.name] = {
            "calls": len(mine), "thinking": arm.thinking, "max_tokens": arm.max_tokens,
            "worst_case_usd": round(worst, 6),
            "estimate_off_peak_usd": ({str(r): round(estimate(r), 4) for r in (500, 1000, 2000, 4000)} if arm.thinking
                                      else {"0": round(estimate(0), 4)}),
        }
    return {
        "experiment_name": config.experiment_name, "calls": len(every), "pilot_calls": len(config.arms) * len(config.probes.probes),
        "per_arm": per_arm, "worst_case_usd": round(math.fsum(a["worst_case_usd"] for a in per_arm.values()), 6),
        "cap_usd": config.budget["cap_usd"], "prices_date_checked": prices.date_checked,
        "estimate_note": "off-peak, every prompt token a cache miss, 40 reply tokens a call, plus the reasoning tokens shown (thinking on)",
    }


# --- the mock policies ---------------------------------------------------------------------------


def _probe_mock(answer: Callable[[Mapping[str, Any]], str]):
    """A mock policy that answers each probe from its own entry (the runner passes the probe set)."""

    def make(probes: ProbeSet):
        def policy(request: LLMRequest) -> str:
            probe = probes.by_id(str(request.metadata["probe_id"]))
            return f"{answer(probe)}\nMock reply (no model was called) for {probe['id']}."

        policy.__name__ = answer.__name__
        return policy

    return make


def _say(label: str, kind: str) -> str:
    if kind == "their_side":
        return f"Your {label}."
    if kind == "wall":
        return f"The {label} wall."
    if kind == "named_side":
        return f"The {label} side."
    if kind == "lane":
        return f"Lane {label}."
    return "Cannot tell." if label == S.CANNOT_TELL else label.capitalize() + "."


def probe_expected(probe: Mapping[str, Any]) -> str:
    """Always the first correct answer: a rehearsal in which every probe is scored correct."""
    return _say(probe["correct"][0], probe["kind"])


def probe_wrong(probe: Mapping[str, Any]) -> str:
    """Always the first wrong answer: every probe scored wrong."""
    return _say(probe["wrong"][0], probe["kind"])


MOCK_POLICIES: dict[str, Callable[[ProbeSet], Callable[[LLMRequest], str]]] = {
    "probe_expected": _probe_mock(probe_expected),
    "probe_wrong": _probe_mock(probe_wrong),
}


def make_client(config: ProbeConfig, client_name: Optional[str] = None) -> LLMClient:
    """The mock client, or DeepSeek behind a budget guard on this experiment's own calls."""
    name = client_name or config.llm["client"]
    if name == "mock":
        return MockClient(policy=MOCK_POLICIES[config.llm["mock_policy"]](config.probes))
    if name != "deepseek":
        raise ConfigError(f"unknown client {name!r}; expected one of {list(CLIENTS)}")
    prices = PriceTable.from_yaml()
    prices.price_of(config.llm["model"])
    guard = BudgetGuard(SpendLedger(resolve_path(config.budget["ledger"])), config.budget["cap_usd"], prices, scope=config.experiment_name)
    return BudgetedClient(DeepSeekClient.from_env(max_retries=config.llm["transport_retries"]), guard)


# --- running -------------------------------------------------------------------------------------


@dataclass
class ProbeResult:
    experiment_dir: Path
    status: str = STATUS_COMPLETED
    sent: int = 0
    skipped: int = 0
    failed: int = 0
    cost_usd: float = 0.0
    detail: Optional[str] = None


def _record(config: ProbeConfig, call: Call, request: LLMRequest, response: Optional[LLMResponse], error: Optional[str],
            started: datetime, is_mock: bool) -> dict[str, Any]:
    scored = S.score(call.probe, response.content if response else None) if response else None
    return {
        "record_version": RECORD_VERSION,
        "experiment_name": config.experiment_name,
        "call_id": call.call_id, "arm": call.arm.name, "thinking": call.arm.thinking,
        "probe_id": call.probe["id"], "group": call.probe["group"], "kind": call.probe["kind"], "repeat": call.repeat,
        "probes_sha256": config.probes.sha256,
        "started_utc": started.isoformat(timespec="milliseconds"),
        "messages": [dict(m) for m in request.messages],
        "request": request.params(),
        "is_mock": is_mock,
        "raw_output": response.content if response else None,
        "reasoning_content": response.reasoning_content if response else None,
        "finish_reason": response.finish_reason if response else None,
        "response_id": response.response_id if response else None,
        "model": response.model if response else None,
        "system_fingerprint": response.system_fingerprint if response else None,
        "usage": response.usage.as_dict() if response else None,
        "cost_usd": round(response.cost_usd, 10) if response else None,
        "price_tier": response.price_tier if response else None,
        "latency_s": round(response.latency_s, 4) if response else None,
        "expected": {"correct": list(call.probe["correct"]), "wrong": list(call.probe["wrong"])},
        "score": scored.as_dict() if scored else None,
        "api_error": error,
    }


def _set_aside(path: Path) -> None:
    n = 1
    while (aside := path.with_name(f"{path.stem}.failed{n}.json")).exists():
        n += 1
    path.rename(aside)


def run_probe(
    config: ProbeConfig,
    client: Optional[LLMClient] = None,
    client_name: Optional[str] = None,
    out_root: Optional[Path | str] = None,
    confirm: bool = False,
    allow_peak: bool = False,
    limit: Optional[int] = None,
    now: Callable[[], datetime] = _utc_now,
    report: Callable[[str], None] = print,
    git: Optional[Mapping[str, Any]] = None,
) -> ProbeResult:
    """Run (or resume) the probe. ``limit`` sends at most N calls that have no record yet."""
    name = client.name if client is not None else (client_name or config.llm["client"])
    if name not in CLIENTS:
        raise ConfigError(f"unknown client {name!r}; expected one of {list(CLIENTS)}")
    paid = name != "mock"
    experiment_dir = Path(out_root if out_root is not None else (RUNS_DIR if paid else MOCK_RUNS_DIR)) / config.experiment_name
    result = ProbeResult(experiment_dir)
    prices = PriceTable.from_yaml()
    preview = plan(config, prices)
    if git is None:
        from ..experiment.batch import git_state

        git = git_state()
    experiment_dir.mkdir(parents=True, exist_ok=True)
    _write_json(experiment_dir / CONFIG_FILE, {"config": config.as_dict(), "client": name, "git": dict(git)})
    _write_json(experiment_dir / PLAN_FILE, preview)
    started = now()
    if paid and not confirm:
        result.status = STATUS_AWAITING
        result.detail = "a paid client sends nothing without --confirm; the plan is in plan.json"
        report(f"{config.experiment_name}: {preview['calls']} call(s), worst case USD {preview['worst_case_usd']:.4f}, cap USD {config.budget['cap_usd']:.2f}: nothing sent (no --confirm)")
        _finish(config, result, started, name, now, limit)
        return result
    client = client or make_client(config, name)
    for call in calls(config):
        path = experiment_dir / call.path
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if existing.get("api_error") is None:
                result.skipped += 1
                continue
            _set_aside(path)
        if limit is not None and result.sent + result.failed >= limit:
            result.status = STATUS_PARTIAL
            break
        when = now()
        if paid and not allow_peak and prices.tier_at(when) == PEAK:
            result.status, result.detail = STATUS_PEAK, f"{when.isoformat(timespec='seconds')} is in DeepSeek's peak hours; pass --allow-peak to send anyway"
            break
        request = request_for(config, call)
        try:
            response = client.complete(request)
        except BudgetExceededError as exc:
            result.status, result.detail = STATUS_CAP, str(exc)
            break
        except LLMFatalError as exc:
            _write_json(path, _record(config, call, request, None, f"{type(exc).__name__}: {exc}", when, not paid))
            result.failed += 1
            result.status, result.detail = STATUS_FAILED, str(exc)
            break
        except LLMError as exc:
            _write_json(path, _record(config, call, request, None, f"{type(exc).__name__}: {exc}", when, not paid))
            result.failed += 1
            continue
        _write_json(path, _record(config, call, request, response, None, when, not paid))
        result.sent += 1
        result.cost_usd += response.cost_usd
    else:
        if result.failed:
            result.status = STATUS_PARTIAL
    _finish(config, result, started, name, now, limit)
    report(
        f"{config.experiment_name}: {result.sent} sent, {result.skipped} already recorded, {result.failed} failed; "
        f"status {result.status}; cost of this invocation USD {result.cost_usd:.6f}"
        + (f" ({result.detail})" if result.detail else "")
    )
    return result


# --- the summary ---------------------------------------------------------------------------------


def load_records(experiment_dir: Path) -> list[dict[str, Any]]:
    return [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted((experiment_dir / CALLS_DIR).glob("*/*.json"))
        if ".failed" not in p.name
    ]


def _row(record: Mapping[str, Any]) -> dict[str, Any]:
    usage, scored = record.get("usage") or {}, record.get("score") or {}
    return {
        "call_id": record["call_id"], "arm": record["arm"], "thinking": record["thinking"], "probe_id": record["probe_id"],
        "group": record["group"], "kind": record["kind"], "repeat": record["repeat"],
        "label": scored.get("label"), "outcome": scored.get("outcome"), "ambiguous": scored.get("ambiguous"),
        "first_line": scored.get("first_line"), "finish_reason": record.get("finish_reason"),
        "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
        "reasoning_tokens": usage.get("reasoning_tokens"),
        "reasoning_chars": len(record["reasoning_content"]) if record.get("reasoning_content") else 0,
        "cost_usd": record.get("cost_usd"), "price_tier": record.get("price_tier"),
        "system_fingerprint": record.get("system_fingerprint"), "latency_s": record.get("latency_s"),
        "started_utc": record.get("started_utc"),
    }


def _tally(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    outcomes = Counter(r["outcome"] for r in rows)
    scored = outcomes[S.CORRECT] + outcomes[S.WRONG]
    return {
        "n": len(rows), "correct": outcomes[S.CORRECT], "wrong": outcomes[S.WRONG], "unclear": outcomes[S.UNCLEAR],
        "ambiguous": sum(1 for r in rows if r["ambiguous"]),
        "share_correct": round(outcomes[S.CORRECT] / len(rows), 4) if rows else None,
        "share_correct_of_readable": round(outcomes[S.CORRECT] / scored, 4) if scored else None,
        "labels": dict(sorted(Counter(r["label"] for r in rows).items())),
    }


def _stats(values: Sequence[float]) -> Optional[dict[str, float]]:
    if not values:
        return None
    ordered = sorted(values)
    return {"mean": round(statistics.fmean(ordered), 1), "median": statistics.median(ordered), "min": ordered[0],
            "p90": ordered[min(len(ordered) - 1, math.ceil(0.9 * len(ordered)) - 1)], "max": ordered[-1]}


def summarise(config: ProbeConfig, experiment_dir: Path) -> dict[str, Any]:
    rows = [_row(r) for r in load_records(experiment_dir) if r.get("api_error") is None]
    per_arm = {}
    for arm in config.arms:
        mine = [r for r in rows if r["arm"] == arm.name]
        per_arm[arm.name] = {
            "thinking": arm.thinking, **_tally(mine),
            "groups": {g: _tally([r for r in mine if r["group"] == g]) for g in config.probes.groups},
            "probes": {p["id"]: _tally([r for r in mine if r["probe_id"] == p["id"]]) for p in config.probes.probes},
            "reasoning_tokens": _stats([r["reasoning_tokens"] or 0 for r in mine]),
            "completion_tokens": _stats([r["completion_tokens"] or 0 for r in mine]),
            "finish_reasons": dict(Counter(str(r["finish_reason"]) for r in mine)),
            "cost_usd": round(math.fsum(r["cost_usd"] or 0.0 for r in mine), 6),
            "price_tiers": dict(Counter(str(r["price_tier"]) for r in mine)),
            "latency_s": _stats([r["latency_s"] or 0.0 for r in mine]),
        }
    fingerprints = Counter(str(r["system_fingerprint"]) for r in rows)
    return {
        "experiment_name": config.experiment_name, "probes_sha256": config.probes.sha256,
        "calls_recorded": len(rows), "calls_planned": len(calls(config)),
        "per_arm": per_arm,
        "fingerprints": dict(fingerprints),
        "expected_fingerprint": config.expected_fingerprint,
        "fingerprint_matches": (None if config.expected_fingerprint is None or not rows
                                else set(fingerprints) == {config.expected_fingerprint}),
        "cost_usd": round(math.fsum(r["cost_usd"] or 0.0 for r in rows), 6),
    }


def _finish(config: ProbeConfig, result: ProbeResult, started: datetime, client: str, now: Callable[[], datetime],
            limit: Optional[int]) -> None:
    rows = [_row(r) for r in load_records(result.experiment_dir)]
    with (result.experiment_dir / RESULTS_FILE).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    _write_json(result.experiment_dir / SUMMARY_FILE, summarise(config, result.experiment_dir))
    _append_jsonl(result.experiment_dir / INVOCATIONS_FILE, {
        "started_utc": started.isoformat(timespec="seconds"), "ended_utc": now().isoformat(timespec="seconds"),
        "client": client, "limit": limit, "status": result.status, "detail": result.detail,
        "sent": result.sent, "skipped": result.skipped, "failed": result.failed, "cost_usd": round(result.cost_usd, 10),
    })


# --- the command line ----------------------------------------------------------------------------


def print_plan(preview: Mapping[str, Any], out: Callable[[str], None] = print) -> None:
    out(f"{preview['experiment_name']}: {preview['calls']} call(s); the pilot (--limit {preview['pilot_calls']}) is one repeat of every probe in every arm")
    for name, arm in preview["per_arm"].items():
        estimates = ", ".join(f"{k} reasoning tokens: USD {v:.4f}" for k, v in arm["estimate_off_peak_usd"].items())
        out(f"  {name}: {arm['calls']} calls, thinking {'on' if arm['thinking'] else 'off'}, reply cap {arm['max_tokens']}; "
            f"worst case USD {arm['worst_case_usd']:.4f}; estimate off-peak ({estimates})")
    out(f"  worst case in all USD {preview['worst_case_usd']:.4f}; cap USD {preview['cap_usd']:.2f} (prices checked {preview['prices_date_checked']})")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config", help="a probe config, e.g. configs/probe/rf53_stage1_frames_probe.yaml")
    parser.add_argument("--client", choices=CLIENTS, help="override the config's llm.client")
    parser.add_argument("--out", type=Path, help="output root (default: runs/, or runs_mock/ for the mock client)")
    parser.add_argument("--limit", type=int, help="send at most N calls that have no record yet")
    parser.add_argument("--plan", action="store_true", help="print the calls and their cost, then stop")
    parser.add_argument("--confirm", action="store_true", help="with a paid client: send the calls")
    parser.add_argument("--allow-peak", action="store_true", help="with a paid client: send in DeepSeek's peak hours too")
    args = parser.parse_args(argv)
    try:
        config = ProbeConfig.load(args.config)
        if args.plan:
            print_plan(plan(config))
            return 0
        result = run_probe(config, client_name=args.client, out_root=args.out, confirm=args.confirm,
                           allow_peak=args.allow_peak, limit=args.limit)
    except (ConfigError, LLMError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"records: {result.experiment_dir}")
    return 0 if result.status in (STATUS_COMPLETED, STATUS_PARTIAL, STATUS_AWAITING) else 3
