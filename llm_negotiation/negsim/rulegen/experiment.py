"""The rule-generation experiment type (issue #30, Part 10; ``docs/rule-generation.md``).

A config with ``layer: rule_generation`` runs, in order:

1. **case selection**: cases from the case store, by case set and, optionally, by id;
2. **the design matrix**: the session list (``negsim.rulegen.design``);
3. **a worst-case cost preview** (:func:`preview_cost`), printed and written before any call.
   With a paid client nothing is sent unless the preview fits the budget cap *and* the run is
   explicitly confirmed (``--confirm``); without that the experiment stops after the preview,
   and no paid client is even built;
4. **the sessions** of condition A (negotiate) and/or B (state), each written whole as soon
   as it ends, so that an interrupted experiment resumes without paying twice for a session;
5. **validation** of every proposed rule;
6. **the writer**: each valid agreed (A) or stated (B) rule into the experiment's staging
   database, once per canonical rule, with every supporting session;
7. optionally **replay** and **crowd screening** of every rule written, recorded on the rule;
8. **the report**: categories by condition and scenario, agreement rate, stability, tokens
   and cost against the preview.

The budget cap is enforced through issue #24's guard and ledger, on this experiment's own calls
(``BudgetGuard`` scoped to the experiment's name). Everything is logged and linked by session id
(``docs/log-schema.md``, "Rule-generation experiments"). A mock run goes under ``runs_mock/``,
which git ignores; a paid one under ``runs/``.

**Running an experiment again resumes it.** A session with a record is read back, not run
again; a session that was aborted (the budget guard refused, the model could not be used) is
run again, its first log kept beside the new one. Writing, replay and screening are idempotent.
A folder that holds another config, or a run with another client, is refused.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from .. import __version__
from ..configutil import PACKAGE_ROOT, REPO_ROOT, ConfigError, as_bool, as_choice, as_number, check_keys, load_yaml, resolve_path
from ..llm.base import LLMClient, LLMFatalError
from ..llm.budget import BudgetedClient, BudgetExceededError, BudgetGuard, SpendLedger, estimate_prompt_tokens
from ..llm.deepseek import DeepSeekClient
from ..llm.mock import MockClient
from ..llm.pricing import PriceTable
from ..negotiation.protocol import MAX_ATTEMPTS_PER_TURN
from .cases import CaseStore
from .describe import KIND_NEGOTIATE, KIND_STATE, Templates, load_templates, negotiation_prompt, statement_prompt
from .design import CONDITION_NEGOTIATED, CONDITION_STATED, CONDITIONS, DesignSettings, Session, cell_code, sessions_for
from .mock import POLICIES as MOCK_POLICIES
from .outcomes import OUTCOMES_FILE, outcome_row
from .protocol import (
    DEFAULT_MAX_MESSAGES_PER_AGENT,
    OUTCOME_ABORTED,
    OUTCOME_AGREED,
    OUTCOME_NULL_RULE,
    OUTCOME_STATED,
    LLMSettings,
    RuleNegotiation,
    RuleStatement,
    stability,
)
from .replay import KIND_CROWD, KIND_REPLAY, CrowdScreen, ScreeningSettings, crowd_size, mixed_population, replay
from .transcript import render as render_transcript
from .validate import CATEGORIES, VALID, validate_proposal
from .writer import STAGING_DIR, StagingDatabase, Support, build_rule, with_screening

LAYER_RULE_GENERATION = "rule_generation"
SCHEMA_VERSION = 1  # of the config
#: The version of the files a rule-generation experiment writes (``docs/log-schema.md``,
#: "Rule-generation experiments"); the run folders of its replays are avoidance runs. Version 2
#: (issue #32) adds ``outcomes.jsonl`` and the fictional group of a session.
RULEGEN_LOG_VERSION = 2
CLIENTS = ("mock", "deepseek")
RUNS_DIR, MOCK_RUNS_DIR = PACKAGE_ROOT / "runs", PACKAGE_ROOT / "runs_mock"

# The files of a rule-generation experiment folder (``docs/log-schema.md``).
CONFIG_FILE = "config.json"
INVOCATIONS_FILE = "invocations.jsonl"
CASES_FILE = "cases.json"
DESIGN_FILE = "design.jsonl"
PREVIEW_FILE = "preview.json"
SESSIONS_DIR = "sessions"
VALIDATION_FILE = "validation.jsonl"
WRITTEN_FILE = "written.jsonl"
SCREENING_FILE = "screening.jsonl"
COST_FILE = "cost.json"
SUMMARY_FILE = "summary.json"
REPORT_FILE = "report.md"
REPLAY_DIR, SCREENING_DIR = "replay", "screening"

STATUS_COMPLETED = "completed"  # every session has a record
STATUS_PARTIAL = "partial"  # some have none yet (``--limit``)
STATUS_ABORTED = "aborted"  # a session was stopped: the budget guard refused, or the model could not be used
STATUS_AWAITING = "awaiting_confirmation"  # a paid client, not confirmed: nothing was sent

#: Where the supervisor's approvals are recorded, and the sentence that records the ethics
#: sign-off for the fictional-group factor (issue #32, Part 1.4; ``docs/fictional-groups.md``,
#: section 6). Without it, no paid run may switch the factor on.
SIGN_OFF_FILE = REPO_ROOT / "CLAUDE.md"
ETHNICITY_SIGN_OFF = re.compile(
    r"Ethics sign-off for the fictional-group factor \(issue #32\): approved by the supervisor on \d{4}-\d{2}-\d{2}"
)


def ethnicity_signed_off(path: Optional[Path] = None) -> bool:
    """Whether ``CLAUDE.md`` (or ``path``) records the supervisor's ethics sign-off for the
    fictional-group factor."""
    path = SIGN_OFF_FILE if path is None else path
    return path.is_file() and ETHNICITY_SIGN_OFF.search(path.read_text(encoding="utf-8")) is not None


def is_rule_generation_config(raw: Any) -> bool:
    return isinstance(raw, Mapping) and raw.get("layer") == LAYER_RULE_GENERATION


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _append_jsonl(path: Path, row: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


# --- the config -----------------------------------------------------------------------------------


@dataclass(frozen=True)
class RuleGenConfig:
    experiment_name: str
    description: str
    source: str
    case_store: str
    case_set: Optional[str]
    case_ids: tuple[str, ...]
    conditions: tuple[str, ...]
    design: DesignSettings
    negotiation_template: str
    max_messages_per_agent: int
    statement_template: str
    statement_repeats: int
    llm: Mapping[str, Any]
    budget: Mapping[str, Any]
    replay_enabled: bool
    screening: Optional[ScreeningSettings]

    @classmethod
    def load(cls, path: Path | str) -> "RuleGenConfig":
        return cls.from_raw(load_yaml(resolve_path(path)), str(path).replace("\\", "/"))

    @classmethod
    def from_raw(cls, raw: Any, source: str = "<config>") -> "RuleGenConfig":
        where = f"rule-generation config {source}"
        check_keys(
            raw, where, ("layer", "experiment_name", "cases", "conditions", "design", "llm"),
            ("schema_version", "description", "negotiation", "statement", "budget", "replay", "screening"),
        )
        if raw["layer"] != LAYER_RULE_GENERATION:
            raise ConfigError(f"{where}.layer: expected {LAYER_RULE_GENERATION!r}")
        if raw.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
            raise ConfigError(f"{where}: schema_version {raw['schema_version']!r} is not supported")
        name = str(raw["experiment_name"])
        if not name or not all(ch.isalnum() or ch in "_-" for ch in name):
            raise ConfigError(f"{where}.experiment_name: letters, digits, '_' and '-' only, got {name!r}")
        cases = check_keys(raw["cases"], f"{where}.cases", (), ("store", "set", "ids"))
        if not cases.get("set") and not cases.get("ids"):
            raise ConfigError(f"{where}.cases: name a case set, or case ids, or both")
        if cases.get("ids") is not None and (not isinstance(cases["ids"], list) or len(set(cases["ids"])) != len(cases["ids"])):
            raise ConfigError(f"{where}.cases.ids: a list of distinct case ids")
        conditions = raw["conditions"]
        if not isinstance(conditions, list) or not conditions or any(c not in CONDITIONS for c in conditions) or len(set(conditions)) != len(conditions):
            raise ConfigError(f"{where}.conditions: a list of distinct conditions from {list(CONDITIONS)}, got {conditions!r}")
        negotiation = check_keys(raw.get("negotiation") or {}, f"{where}.negotiation", (), ("template", "max_messages_per_agent"))
        statement = check_keys(raw.get("statement") or {}, f"{where}.statement", (), ("template", "repeats"))
        llm = check_keys(raw["llm"], f"{where}.llm", (), ("client", "mock_policy", "model", "temperature", "max_tokens", "thinking", "transport_retries"))
        budget = check_keys(raw.get("budget") or {}, f"{where}.budget", (), ("cap_usd", "ledger"))
        replay_raw = check_keys(raw.get("replay") or {}, f"{where}.replay", (), ("enabled",))
        screening_raw = check_keys(raw.get("screening") or {}, f"{where}.screening", (), ("enabled", "scenario", "baseline", "seed", "repeats", "scenario_overrides"))
        screening = None
        if as_bool(screening_raw.get("enabled", False), f"{where}.screening.enabled"):
            screening = ScreeningSettings.from_config(screening_raw, f"{where}.screening")
        policy = str(llm.get("mock_policy", "rulegen_paths"))
        if policy not in MOCK_POLICIES:
            raise ConfigError(f"{where}.llm.mock_policy: one of {sorted(MOCK_POLICIES)}, got {policy!r}")
        return cls(
            experiment_name=name,
            description=" ".join(str(raw.get("description", "")).split()),
            source=source,
            case_store=str(cases.get("store", "cases")),
            case_set=cases.get("set"),
            case_ids=tuple(cases.get("ids") or ()),
            conditions=tuple(conditions),
            design=DesignSettings.from_config(raw["design"], f"{where}.design"),
            negotiation_template=str(negotiation.get("template", "rulegen_negotiate_v1")),
            max_messages_per_agent=int(as_number(negotiation.get("max_messages_per_agent", DEFAULT_MAX_MESSAGES_PER_AGENT), f"{where}.negotiation.max_messages_per_agent", minimum=1)),
            statement_template=str(statement.get("template", "rulegen_state_v1")),
            statement_repeats=int(as_number(statement.get("repeats", 3), f"{where}.statement.repeats", minimum=1)),
            llm={
                "client": as_choice(llm.get("client", "mock"), f"{where}.llm.client", CLIENTS),
                "mock_policy": policy,
                "model": str(llm.get("model", "deepseek-flash")),
                "temperature": as_number(llm.get("temperature", 1.0), f"{where}.llm.temperature", minimum=0.0),
                "max_tokens": int(as_number(llm.get("max_tokens", 600), f"{where}.llm.max_tokens", minimum=1)),
                "thinking": as_choice(llm.get("thinking", "disabled"), f"{where}.llm.thinking", ("disabled", "enabled")),
                "transport_retries": int(as_number(llm.get("transport_retries", 2), f"{where}.llm.transport_retries", minimum=0)),
            },
            budget={
                "cap_usd": as_number(budget.get("cap_usd", 0.05), f"{where}.budget.cap_usd", minimum=0.0),
                "ledger": str(budget.get("ledger", "spend_ledger.jsonl")),
            },
            replay_enabled=as_bool(replay_raw.get("enabled", True), f"{where}.replay.enabled"),
            screening=screening,
        )

    def llm_settings(self) -> LLMSettings:
        return LLMSettings(self.llm["model"], self.llm["temperature"], self.llm["max_tokens"], self.llm["thinking"] == "enabled")

    def as_dict(self) -> dict[str, Any]:
        return {
            "experiment_name": self.experiment_name,
            "description": self.description,
            "source": self.source,
            "cases": {"store": self.case_store, "set": self.case_set, "ids": list(self.case_ids)},
            "conditions": list(self.conditions),
            "design": self.design.as_dict(),
            "negotiation": {"template": self.negotiation_template, "max_messages_per_agent": self.max_messages_per_agent},
            "statement": {"template": self.statement_template, "repeats": self.statement_repeats},
            "llm": dict(self.llm),
            "budget": dict(self.budget),
            "replay": {"enabled": self.replay_enabled},
            "screening": None if self.screening is None else {"enabled": True, **self.screening.as_dict()},
        }


def _comparable(experiment: Mapping[str, Any]) -> dict[str, Any]:
    """A config as written to ``config.json``, less where it was read from: what must not change
    between two invocations of one experiment."""
    return {key: value for key, value in experiment.items() if key != "source"}


def selected_cases(config: RuleGenConfig) -> list[dict[str, Any]]:
    """The cases of the experiment, in case-id order, each read from the frozen store."""
    store = CaseStore(resolve_path(config.case_store))
    wanted = dict(store.case_set(config.case_set)) if config.case_set else {}
    if config.case_ids:
        if config.case_set:
            missing = [case_id for case_id in config.case_ids if case_id not in wanted]
            if missing:
                raise ConfigError(f"cases {missing} are not in case set {config.case_set!r}")
            wanted = {case_id: wanted[case_id] for case_id in config.case_ids}
        else:
            wanted = {case_id: None for case_id in config.case_ids}
    return [store.get(case_id, version) for case_id, version in sorted(wanted.items())]


@dataclass(frozen=True)
class Plan:
    """What an experiment will do, before it does anything."""

    cases: Mapping[str, Mapping[str, Any]]
    sessions: list[Session]
    templates: Mapping[str, Templates]
    preview: Mapping[str, Any]


def plan(config: RuleGenConfig) -> Plan:
    """The cases, the session list and the cost preview: everything that needs no client."""
    cases = {case["case_id"]: case for case in selected_cases(config)}
    sessions = sessions_for(
        [(case_id, case["version"], tuple(case["agents"])) for case_id, case in cases.items()],
        config.design, config.conditions, {CONDITION_STATED: config.statement_repeats}, config.experiment_name,
    )
    templates = {
        CONDITION_NEGOTIATED: load_templates(config.negotiation_template, KIND_NEGOTIATE),
        CONDITION_STATED: load_templates(config.statement_template, KIND_STATE),
    }
    return Plan(cases, sessions, templates, preview_cost(config, sessions, cases, templates, PriceTable.from_yaml()))


# --- the cost preview -----------------------------------------------------------------------------


def _turn_wrapper(templates: Templates) -> str:
    """Every line a turn can wrap around the other agent's reply, at their longest."""
    words = templates.data["turns"]
    return "\n".join([
        words["header"], words["message"].replace("{message}", ""),
        words["proposal"].replace("{proposal_id}", "0" * 12).replace("{proposal}", ""),
        words["accept_other"].replace("{accept}", "0" * 64), words["no_rule"], "", words["your_turn"], words["first"],
    ])


def negotiation_bound(messages: int, fixed: int, previous: int, cap: int) -> tuple[int, int]:
    """Issue #30's bound on one negotiation, per send of each turn: input <= 2M S + m M (2M - 1),
    output <= 2M c. Turn t (from 0) carries the fixed prompt S and the t turns before it, each
    at most m tokens; summed over the 2M turns."""
    return 2 * messages * fixed + previous * messages * (2 * messages - 1), 2 * messages * cap


def statement_bound(fixed: int, cap: int) -> tuple[int, int]:
    """Issue #30's bound on one statement, per send: input <= S, output <= c (the issue's (S + m))."""
    return fixed, cap


def preview_cost(
    config: RuleGenConfig,
    sessions: Sequence[Session],
    cases: Mapping[str, Mapping[str, Any]],
    templates: Mapping[str, Templates],
    prices: PriceTable,
) -> dict[str, Any]:
    """The most the sessions could cost: issue #30's bound, every token at the peak cache-miss rate.

    With c the reply cap (``max_tokens``), and every text's tokens estimated high
    (``estimate_prompt_tokens``): condition A, with M messages per agent, a fixed prompt of S
    tokens and a previous turn re-appearing as at most m tokens, has input <= 2M S + m M (2M - 1)
    and output <= 2M c per session; condition B has input <= S and output <= c per call. Each is
    multiplied by the most sends one turn can make, 1 + R (``sends_per_turn``): two attempts (the
    retry on an unreadable reply) times 1 + the client's transport retries. S is the larger
    system prompt plus the longest turn wrapper W, plus room for a failed reply (c) and the retry
    instruction; m = c + W. ``docs/rule-generation.md``, section 9, derives it.
    """
    model, cap = config.llm["model"], config.llm["max_tokens"]
    price = prices.price_of(model)
    p_in, p_out = price.input_cache_miss.peak / 1e6, price.output.peak / 1e6
    sends = MAX_ATTEMPTS_PER_TURN * (1 + config.llm["transport_retries"])
    rows, totals = [], {condition: 0.0 for condition in config.conditions}
    for session in sessions:
        case, templ = cases[session.case_id], templates[session.condition]
        if session.condition == CONDITION_NEGOTIATED:
            wrapper = estimate_prompt_tokens([{"content": _turn_wrapper(templ)}])
            retry = estimate_prompt_tokens([{"content": templ.data["turns"]["retry"]}])
            system = max(estimate_prompt_tokens([{"content": negotiation_prompt(case, session, agent, templ)}]) for agent in session.agents)
            fixed, m, messages = system + wrapper + cap + retry, cap + wrapper, config.max_messages_per_agent
            input_bound, output_bound = negotiation_bound(messages, fixed, m, cap)
        else:
            retry = estimate_prompt_tokens([{"content": templ.data["retry"]}])
            fixed = estimate_prompt_tokens([{"content": statement_prompt(case, session, templ)}]) + cap + retry
            m, messages = cap, None
            input_bound, output_bound = statement_bound(fixed, cap)
        usd = sends * (input_bound * p_in + output_bound * p_out)
        totals[session.condition] += usd
        rows.append({
            "session_id": session.session_id, "condition": session.condition, "S_tokens": fixed, "m_tokens": m,
            "reply_cap_tokens": cap, "M_messages_per_agent": messages,
            "input_tokens_bound": sends * input_bound, "output_tokens_bound": sends * output_bound, "usd_bound": round(usd, 8),
        })
    total = math.fsum(totals.values())
    return {
        "computed_utc": _utc_now(),
        "model": model,
        "prices": {"input_cache_miss_peak_per_million": price.input_cache_miss.peak, "output_peak_per_million": price.output.peak, **prices.describe()},
        "reply_cap_tokens": cap,
        "max_messages_per_agent": config.max_messages_per_agent if CONDITION_NEGOTIATED in config.conditions else None,
        "sends_per_turn": sends,
        "max_retries_per_turn": sends - 1,
        "sends_from": {"attempts_per_turn": MAX_ATTEMPTS_PER_TURN, "transport_retries_per_attempt": config.llm["transport_retries"]},
        "sessions": len(sessions),
        "sessions_by_condition": dict(Counter(session.condition for session in sessions)),
        "usd_by_condition": {name: round(value, 8) for name, value in totals.items()},
        "usd_total": round(total, 8),
        "cap_usd": config.budget["cap_usd"],
        "fits_the_cap": total <= config.budget["cap_usd"],
        "per_session": rows,
    }


# --- the client ---------------------------------------------------------------------------------


def make_client(config: RuleGenConfig, client_name: Optional[str] = None) -> LLMClient:
    """The mock client, or the paid client behind a budget guard on this experiment's calls."""
    name = client_name or config.llm["client"]
    if name == "mock":
        return MockClient(policy=MOCK_POLICIES[config.llm["mock_policy"]])
    if name != "deepseek":
        raise ConfigError(f"unknown client {name!r}; expected one of {list(CLIENTS)}")
    prices = PriceTable.from_yaml()
    prices.price_of(config.llm["model"])
    guard = BudgetGuard(SpendLedger(resolve_path(config.budget["ledger"])), config.budget["cap_usd"], prices, scope=config.experiment_name)
    return BudgetedClient(DeepSeekClient.from_env(max_retries=config.llm["transport_retries"]), guard)


# --- one session ----------------------------------------------------------------------------------


def path_indices(sessions: Sequence[Session]) -> dict[str, int]:
    """A stable number for each session's design cell within its condition: the repeats of one
    cell share it. Only the mock client reads it (to give each cell a path); a provider never
    sees it, as no label is sent."""
    groups: dict[str, list[str]] = {}
    for session in sessions:
        groups.setdefault(session.condition, []).append(f"{session.case_id}/{cell_code(session.cell)}")
    index = {}
    for condition, keys in groups.items():
        ordered = sorted(set(keys))
        for session in sessions:
            if session.condition == condition:
                index[session.session_id] = ordered.index(f"{session.case_id}/{cell_code(session.cell)}")
    return index


def _session_path(experiment_dir: Path, session_id: str) -> Path:
    return experiment_dir / SESSIONS_DIR / f"{session_id}.json"


def _read_record(path: Path) -> Optional[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def _set_aside(path: Path) -> Path:
    """Keep an aborted session's log, and its transcript, under names of their own before the
    session runs again."""
    number = 1
    while (aside := path.with_name(f"{path.stem}.aborted{number}.json")).exists():
        number += 1
    path.rename(aside)
    if path.with_suffix(".md").is_file():
        path.with_suffix(".md").rename(aside.with_suffix(".md"))
    return aside


def run_session(
    config: RuleGenConfig, session: Session, case: Mapping[str, Any], templates: Templates, client: LLMClient, path_index: int
) -> dict[str, Any]:
    """Run one session and return its whole record. A refusal or an unusable model is recorded
    as the outcome ``aborted``, with everything sent before it."""
    labels = {
        "experiment": config.experiment_name, "session_id": session.session_id, "condition": session.condition,
        "case_id": session.case_id, "repeat": session.repeat, "path_index": path_index,
    }
    record: dict[str, Any] = {"session": session.as_dict(), "started_utc": _utc_now(), "templates": templates.identity(), "llm": config.llm_settings().as_dict()}
    stopped: Optional[Exception] = None
    if session.condition == CONDITION_NEGOTIATED:
        protocol: Any = RuleNegotiation(case, session, templates, client, config.llm_settings(), config.max_messages_per_agent, labels)
    else:
        protocol = RuleStatement(case, session, templates, client, config.llm_settings(), labels)
    try:
        protocol.run()
    except (BudgetExceededError, LLMFatalError) as exc:
        stopped = exc
    record.update(protocol.as_dict())
    record["ended_utc"] = _utc_now()
    record["model_returned"] = _model_returned(record)
    if stopped is not None:
        record["outcome"], record["error"] = OUTCOME_ABORTED, f"{type(stopped).__name__}: {stopped}"
    return record


def _attempts_of(record: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    if record["condition"] == CONDITION_NEGOTIATED:
        return [attempt for turn in record["turns"] for attempt in turn["attempts"]]
    return list(record["attempts"])


def _model_returned(record: Mapping[str, Any]) -> Optional[str]:
    names = sorted({attempt["model"] for attempt in _attempts_of(record) if attempt.get("model")})
    return ", ".join(names) or None


# --- validation, the writer, replay and screening -------------------------------------------------


def validate_session(record: Mapping[str, Any], case: Mapping[str, Any]) -> list[dict[str, Any]]:
    """One validation row per rule the session proposed (A: every proposal; B: the rule)."""
    session = record["session"]
    rows = []
    base = {"session_id": session["session_id"], "condition": record["condition"], "case_id": session["case_id"], "scenario": case["scenario"]["type"]}
    if record["condition"] == CONDITION_NEGOTIATED:
        messages = [turn["message"] for turn in record["turns"] if turn.get("message")]
        for proposal in record["proposals"]:
            result = validate_proposal(proposal["proposal"], session["visibility"], messages)
            rows.append({
                **base, "turn_index": proposal["turn_index"], "proposer": proposal["proposer"],
                "canonical_hash": proposal["canonical_hash"], "agreed": proposal["agreed"], **result.as_dict(),
            })
    elif record.get("rule") is not None:
        result = validate_proposal(record["rule"], session["visibility"], [record.get("reason") or ""])
        rows.append({**base, "turn_index": 0, "proposer": None, "canonical_hash": record["canonical_hash"], "agreed": True, **result.as_dict()})
    return rows


def write_rules(
    config: RuleGenConfig, records: Sequence[Mapping[str, Any]], validations: Sequence[Mapping[str, Any]], experiment_dir: Path
) -> list[dict[str, Any]]:
    """Every valid agreed (A) or stated (B) rule into its condition's staging database, once per
    canonical rule and case, with every session that produced it."""
    valid = {(row["session_id"], row["canonical_hash"]) for row in validations if row["category"] == VALID and row["agreed"]}
    groups: dict[tuple[str, str, str], list[Support]] = {}
    for record in records:
        session = record["session"]
        if record["condition"] == CONDITION_NEGOTIATED and record["outcome"] == OUTCOME_AGREED:
            agreement = record["agreement"]
            proposal, digest, proposer = agreement["rule"], agreement["canonical_hash"], agreement["proposed_by"]
        elif record["condition"] == CONDITION_STATED and record["outcome"] == OUTCOME_STATED:
            proposal, digest, proposer = record["rule"], record["canonical_hash"], None
        else:
            continue
        if (session["session_id"], digest) not in valid:
            continue
        groups.setdefault((record["condition"], session["case_id"], digest), []).append(
            Support(
                session_id=session["session_id"], design_cell=session["cell"], model=record["llm"]["model"],
                model_returned=record.get("model_returned"), prompt_template=record["templates"],
                created_utc=record["started_utc"], proposed_by=proposer, repeat=session["repeat"], proposal=proposal,
            )
        )
    written = []
    for (condition, case_id, digest), supports in sorted(groups.items()):
        supports = sorted(supports, key=lambda support: (support.created_utc, support.session_id))
        staging = StagingDatabase(experiment_dir / STAGING_DIR / condition)
        staging.create()
        rule = build_rule(condition, case_id, digest, supports, config.experiment_name)
        name, version, fresh = staging.stage(rule, f"generated by {config.experiment_name}, {len(supports)} session(s)")
        written.append({
            "rule_id": rule["rule_id"], "version": version, "condition": condition, "case_id": case_id,
            "canonical_hash": digest, "file": (staging.root / name).relative_to(experiment_dir).as_posix(),
            "written": fresh, "sessions": [support.session_id for support in supports],
        })
    return written


def replay_and_screen(
    config: RuleGenConfig,
    written: Sequence[Mapping[str, Any]],
    records: Mapping[str, Mapping[str, Any]],
    cases: Mapping[str, Mapping[str, Any]],
    experiment_dir: Path,
    git: Mapping[str, Any],
    report: Callable[[str], None],
) -> list[dict[str, Any]]:
    """Replay each written rule on its case and screen it in the crowd, each alone, and store
    the results on it as its next version. A rule already replayed and screened by this
    experiment is left as it is.

    The replay uses the people of the rule's earliest supporting session; the crowd is given
    the design's two ages and two genders in turn (``mixed_population``), so that a rule that
    reads them can apply in it; both use that session's visibility.
    """
    screen = None
    if config.screening is not None:
        ages = (config.design.base_age, config.design.base_age + config.design.age_difference)
        population = mixed_population(crowd_size(config.screening), ages, ("female", "male"))
        screen = CrowdScreen(config.screening, experiment_dir / SCREENING_DIR, config.experiment_name, git, population, SCREENING_DIR)
    results = []
    for entry in written:
        staging = StagingDatabase(experiment_dir / STAGING_DIR / entry["condition"])
        rule = staging.latest(entry["rule_id"])
        done = {item["kind"] for item in rule.screening if item.get("experiment") == config.experiment_name}
        wanted = [kind for kind, on in ((KIND_REPLAY, config.replay_enabled), (KIND_CROWD, screen is not None)) if on and kind not in done]
        if not wanted:
            continue
        session = records[entry["sessions"][0]]["session"]
        personas = {int(agent): person for agent, person in session["personas"].items()}
        entries = []
        if KIND_REPLAY in wanted:
            where = f"{REPLAY_DIR}/{rule.rule_id}"
            entries.append(replay(rule, staging.root, cases[entry["case_id"]], personas, session["visibility"], experiment_dir / where, config.experiment_name, git, where))
        if KIND_CROWD in wanted:
            entries.append(screen.screen(rule, staging.root, session["visibility"]))
        newer = with_screening(rule.written, entries)
        staging.write(newer, "replay and screening results added")
        verdicts = ", ".join(f"{item['kind']} {item['verdict']}" for item in entries)
        report(f"  {rule.key}: {verdicts}; now {newer['rule_id']}@{newer['version']}")
        results.append({"rule_id": rule.rule_id, "version": newer["version"], "kinds": [item["kind"] for item in entries]})
    return results


def screening_rows(experiment_dir: Path, written: Sequence[Mapping[str, Any]], experiment: str) -> list[dict[str, Any]]:
    """What this experiment's replay and screening stored on each written rule, read from the
    rule's newest version: one row per rule that has any."""
    rows = []
    for entry in written:
        rule = StagingDatabase(experiment_dir / STAGING_DIR / entry["condition"]).latest(entry["rule_id"])
        mine = [dict(item) for item in rule.screening if item.get("experiment") == experiment]
        if mine:
            rows.append({
                "rule_id": rule.rule_id, "version": rule.version, "condition": entry["condition"], "case_id": entry["case_id"],
                "file": f"{STAGING_DIR}/{entry['condition']}/{rule.source}", "entries": mine,
            })
    return rows


# --- the report -----------------------------------------------------------------------------------


def _aborted_costs(experiment_dir: Path) -> float:
    """What the kept logs of aborted sessions cost: paid for, though the sessions ran again."""
    return math.fsum(
        json.loads(path.read_text(encoding="utf-8"))["totals"]["cost_usd"]
        for path in sorted((experiment_dir / SESSIONS_DIR).glob("*.aborted*.json"))
    )


def design_size(config: RuleGenConfig, cases: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """The size of the full factorial (issue #32 asks for it with the fictional group's factors):
    cells per case and condition, and the sessions they make. SI-3b will need a fraction of it."""
    design = config.design
    per_case = {case_id: design.cells_per_case(case_id) for case_id in sorted(cases)}
    repeats = {condition: (config.statement_repeats if condition == CONDITION_STATED else 1) for condition in config.conditions}
    return {
        "factors": {name: len(design.levels_for("")[name]) for name in design.factors},
        "groups_on": design.groups is not None,
        "cells_per_case": per_case,
        "sessions_by_condition": {condition: sum(per_case.values()) * repeat for condition, repeat in repeats.items()},
        "sessions": sum(sum(per_case.values()) * repeat for repeat in repeats.values()),
    }


def groups_summary(outcomes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """How the sessions came out, by group pair and by whether the groups were shown: counts to
    stratify by, not a judgement (``outcomes.jsonl`` has every session's row)."""
    rows = [row for row in outcomes if row["groups_on"]]
    strata: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = f"{row['condition']}/{row['group_pair']}/{'shown' if row['ethnicity_visible'] else 'hidden'}"
        entry = strata.setdefault(key, {"sessions": 0, "outcomes": Counter(), "rules_that_apply": 0})
        entry["sessions"] += 1
        entry["outcomes"][row["outcome"]] += 1
        entry["rules_that_apply"] += bool(row["effect"] and row["effect"]["matches"])
    return {
        "on": bool(rows),
        "strata": {key: {**entry, "outcomes": dict(sorted(entry["outcomes"].items()))} for key, entry in sorted(strata.items())},
    }


def summarise(
    config: RuleGenConfig,
    status: str,
    records: Sequence[Mapping[str, Any]],
    validations: Sequence[Mapping[str, Any]],
    written: Sequence[Mapping[str, Any]],
    screening: Sequence[Mapping[str, Any]],
    cases: Mapping[str, Mapping[str, Any]],
    preview: Mapping[str, Any],
    aborted_usd: float = 0.0,
    outcome_rows: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """The numbers the issue asks the pilot to report, from the logs; and, with the fictional
    group on (issue #32), the sessions' outcomes by group pair and whether the groups were shown."""
    by_scenario = {case_id: case["scenario"]["type"] for case_id, case in cases.items()}
    categories: dict[str, dict[str, dict[str, int]]] = {}
    for row in validations:
        cell = categories.setdefault(row["condition"], {}).setdefault(row["scenario"], {name: 0 for name in CATEGORIES})
        cell[row["category"]] += 1
    agreed_only: dict[str, dict[str, int]] = {}
    for row in validations:
        if row["agreed"]:
            cell = agreed_only.setdefault(row["condition"], {name: 0 for name in CATEGORIES})
            cell[row["category"]] += 1
    outcomes = {condition: Counter(record["outcome"] for record in records if record["condition"] == condition) for condition in config.conditions}
    negotiated = [record for record in records if record["condition"] == CONDITION_NEGOTIATED]
    agreed = [record for record in negotiated if record["outcome"] == OUTCOME_AGREED]
    agreement = {
        "sessions": len(negotiated),
        "agreed": len(agreed),
        "rate": round(len(agreed) / len(negotiated), 4) if negotiated else None,
        "accepted_rule_proposed_by_first_speaker": sum(record["agreement"]["proposer_spoke_first"] for record in agreed),
        "accepted_rule_proposed_by_second_speaker": sum(not record["agreement"]["proposer_spoke_first"] for record in agreed),
        "sessions_where_someone_said_no_rule_is_possible": sum(
            any(turn.get("no_rule_possible") for turn in record["turns"]) for record in negotiated
        ),
    }
    groups: dict[str, list[Optional[str]]] = {}
    for record in records:
        if record["condition"] == CONDITION_STATED and record["outcome"] != OUTCOME_ABORTED:
            session = record["session"]
            answer = record.get("canonical_hash") if record["outcome"] == OUTCOME_STATED else record["outcome"]
            groups.setdefault(f"{session['case_id']}/{cell_code(session['cell'])}", []).append(answer)
    stabilities = {group: stability(answers) for group, answers in sorted(groups.items())}
    tokens = []
    preview_by_session = {row["session_id"]: row for row in preview["per_session"]}
    for record in records:
        usage = record["totals"]["tokens"]
        bound = preview_by_session.get(record["session"]["session_id"], {})
        tokens.append({
            "session_id": record["session"]["session_id"], "condition": record["condition"],
            "scenario": by_scenario[record["session"]["case_id"]], "outcome": record["outcome"],
            "llm_calls": record["totals"]["llm_calls"], "prompt_tokens": usage["prompt_tokens"],
            "completion_tokens": usage["completion_tokens"], "cost_usd": record["totals"]["cost_usd"],
            "preview_input_tokens": bound.get("input_tokens_bound"), "preview_output_tokens": bound.get("output_tokens_bound"),
            "preview_usd": bound.get("usd_bound"),
        })
    per_condition = {}
    for condition in config.conditions:
        mine = [row for row in tokens if row["condition"] == condition]
        if mine:
            per_condition[condition] = {
                "sessions": len(mine),
                "mean_llm_calls": round(sum(row["llm_calls"] for row in mine) / len(mine), 3),
                "mean_prompt_tokens": round(sum(row["prompt_tokens"] for row in mine) / len(mine), 1),
                "max_prompt_tokens": max(row["prompt_tokens"] for row in mine),
                "mean_completion_tokens": round(sum(row["completion_tokens"] for row in mine) / len(mine), 1),
                "max_completion_tokens": max(row["completion_tokens"] for row in mine),
                "mean_cost_usd": round(sum(row["cost_usd"] for row in mine) / len(mine), 8),
                "largest_share_of_the_preview_used": max(
                    max(row["prompt_tokens"] / row["preview_input_tokens"], row["completion_tokens"] / row["preview_output_tokens"])
                    for row in mine
                ) if all(row["preview_input_tokens"] for row in mine) else None,
            }
    spent = math.fsum(row["cost_usd"] for row in tokens) + aborted_usd
    failure_modes: Counter[str] = Counter()
    for record in records:
        if record["condition"] == CONDITION_NEGOTIATED:
            for turn in record["turns"]:
                if turn["n_attempts"] > 1:
                    failure_modes["retried_turns"] += 1
                if turn.get("parse_error"):
                    failure_modes[f"unreadable_turn:{turn['parse_error'].split(':')[0]}"] += 1
                if turn.get("accept_status") not in (None, "agreed"):
                    failure_modes[f"accept_{turn['accept_status']}"] += 1
        else:
            if len(record["attempts"]) > 1:
                failure_modes["retried_statements"] += 1
            if record.get("parse_error"):
                failure_modes[f"unreadable_statement:{record['parse_error'].split(':')[0]}"] += 1
        failure_modes[f"outcome_{record['outcome']}"] += 1
    return {
        "experiment": config.experiment_name,
        "status": status,
        "sessions": len(records),
        "sessions_planned": preview["sessions"],
        "outcomes": {condition: dict(sorted(counter.items())) for condition, counter in outcomes.items()},
        "categories_by_condition_and_scenario": categories,
        "categories_of_agreed_or_stated_rules": agreed_only,
        "flagged_for_manual_review": sum(1 for row in validations if row["review_flags"]),
        "review_flags": dict(Counter(flag for row in validations for flag in row["review_flags"])),
        "model_wrote_metadata": sum(1 for row in validations if row["ignored_metadata"]),
        "agreement": agreement,
        "null_rules_stated": sum(record["outcome"] == OUTCOME_NULL_RULE for record in records if record["condition"] == CONDITION_STATED),
        "stability": {
            "groups": len(stabilities),
            "mean": round(sum(stabilities.values()) / len(stabilities), 4) if stabilities else None,
            "by_group": stabilities,
        },
        "tokens_by_condition": per_condition,
        "tokens_per_session": tokens,
        "cost": {"preview_usd": preview["usd_total"], "actual_usd": round(spent, 10), "of_which_aborted_sessions_usd": round(aborted_usd, 10), "cap_usd": config.budget["cap_usd"]},
        "rules_written": len(written),
        "screening": list(screening),
        "failure_modes": dict(sorted(failure_modes.items())),
        "design": design_size(config, cases),
        "groups": groups_summary(outcome_rows),
    }


def report_markdown(summary: Mapping[str, Any]) -> str:
    lines = [f"# Rule generation: {summary['experiment']}", "", f"Status {summary['status']}: {summary['sessions']} of {summary['sessions_planned']} session(s) have a record.", "", "## Outcomes", ""]
    for condition, counts in summary["outcomes"].items():
        lines.append(f"- {condition}: " + (", ".join(f"{name} {count}" for name, count in counts.items()) or "none"))
    lines += ["", "## Validation categories, every proposal", "", "| Condition | Scenario | " + " | ".join(CATEGORIES) + " |", "|---|---|" + "---|" * len(CATEGORIES)]
    for condition, scenarios in summary["categories_by_condition_and_scenario"].items():
        for scenario, counts in scenarios.items():
            lines.append(f"| {condition} | {scenario} | " + " | ".join(str(counts[name]) for name in CATEGORIES) + " |")
    agreement = summary["agreement"]
    lines += [
        "", f"Flagged for manual review: {summary['flagged_for_manual_review']} {summary['review_flags']}. "
        f"Proposals in which the model wrote an id or provenance of its own (ignored): {summary['model_wrote_metadata']}.",
        "", "## Agreement (condition A)", "",
        f"{agreement['agreed']} of {agreement['sessions']} session(s) agreed (rate {agreement['rate']}); the accepted rule was proposed "
        f"by the first speaker in {agreement['accepted_rule_proposed_by_first_speaker']} and by the second in "
        f"{agreement['accepted_rule_proposed_by_second_speaker']}. Someone said no rule is possible without talking in "
        f"{agreement['sessions_where_someone_said_no_rule_is_possible']}.",
        "", "## Stability (condition B)", "",
        f"{summary['stability']['groups']} cell(s), mean stability {summary['stability']['mean']}; null rules stated: {summary['null_rules_stated']}.",
        "", "## Tokens and cost", "",
    ]
    for condition, numbers in summary["tokens_by_condition"].items():
        lines.append(
            f"- {condition}: {numbers['sessions']} session(s), {numbers['mean_llm_calls']} call(s) each on average; prompt tokens "
            f"mean {numbers['mean_prompt_tokens']}, max {numbers['max_prompt_tokens']}; completion tokens mean "
            f"{numbers['mean_completion_tokens']}, max {numbers['max_completion_tokens']}; at most "
            f"{numbers['largest_share_of_the_preview_used']} of a session's preview used"
        )
    cost = summary["cost"]
    lines += ["", f"Preview (worst case) USD {cost['preview_usd']}; actual USD {cost['actual_usd']} (aborted sessions USD {cost['of_which_aborted_sessions_usd']}); cap USD {cost['cap_usd']}.",
              "", "## Rules written, replayed and screened", "", f"{summary['rules_written']} rule(s) written."]
    for item in summary["screening"]:
        lines.append(f"- {item['rule_id']}@{item['version']}: " + ", ".join(f"{kind} {verdict}" for kind, verdict in item.items() if kind not in ("rule_id", "version")))
    lines += ["", "## Failure modes", ""] + [f"- {name}: {count}" for name, count in summary["failure_modes"].items()]
    return "\n".join(lines) + "\n"


# --- one experiment -------------------------------------------------------------------------------


@dataclass
class RuleGenResult:
    experiment_dir: Path
    status: str = STATUS_COMPLETED
    preview: Optional[Mapping[str, Any]] = None
    executed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    aborted: Optional[str] = None
    summary: Optional[dict[str, Any]] = None


def _start_folder(experiment_dir: Path, config: RuleGenConfig, client_name: str, git: Mapping[str, Any], plan_: Plan) -> None:
    """Write the config, or check that the folder's is this one: one folder, one experiment.

    Until a session has run (a paid run refused over its cap, or awaiting confirmation, sends
    nothing), the config may still change: it is written again, and ``invocations.jsonl``
    keeps the earlier attempts.
    """
    path = experiment_dir / CONFIG_FILE
    started = any((experiment_dir / SESSIONS_DIR).glob("*.json"))
    if path.is_file() and started:
        existing = json.loads(path.read_text(encoding="utf-8"))
        if _comparable(existing.get("experiment", {})) != _comparable(config.as_dict()):
            raise ConfigError(
                f"{experiment_dir} holds a run of another config of {config.experiment_name}; give the changed config a "
                "new experiment_name, or another --out"
            )
        if existing.get("client_name") != client_name:
            raise ConfigError(f"{experiment_dir} was run with the {existing.get('client_name')} client, not {client_name}")
        return
    _write_json(path, {
        "rulegen_log_version": RULEGEN_LOG_VERSION, "layer": LAYER_RULE_GENERATION, "experiment": config.as_dict(), "client_name": client_name,
        "created_utc": _utc_now(), "git": dict(git),
        "software": {"negsim_version": __version__, "python": platform.python_version()},
        "templates": {condition: plan_.templates[condition].identity() for condition in config.conditions},
    })


def run_rule_generation(
    config: RuleGenConfig,
    client: Optional[LLMClient] = None,
    client_name: Optional[str] = None,
    out_root: Optional[Path | str] = None,
    confirm: bool = False,
    limit: Optional[int] = None,
    report: Callable[[str], None] = print,
    git: Optional[Mapping[str, Any]] = None,
) -> RuleGenResult:
    """Run (or resume) a rule-generation experiment end to end (the steps of the module's
    docstring). ``limit`` runs at most the first N sessions of the list that have no record."""
    name = client.name if client is not None else (client_name or config.llm["client"])
    if name not in CLIENTS:
        raise ConfigError(f"unknown client {name!r}; expected one of {list(CLIENTS)}")
    paid = name != "mock"
    experiment_dir = Path(out_root if out_root is not None else (RUNS_DIR if paid else MOCK_RUNS_DIR)) / config.experiment_name
    result = RuleGenResult(experiment_dir)
    if git is None:
        from ..experiment.batch import git_state

        git = git_state()
    plan_ = plan(config)
    cases, sessions, templates, preview = plan_.cases, plan_.sessions, plan_.templates, plan_.preview
    result.preview = preview
    _start_folder(experiment_dir, config, name, git, plan_)
    _write_json(experiment_dir / CASES_FILE, [{"case_id": case_id, "version": case["version"], "scenario": case["scenario"]["type"], "severity_tier": case["severity_tier"]} for case_id, case in cases.items()])
    _write_jsonl(experiment_dir / DESIGN_FILE, [session.as_dict() for session in sessions])
    _write_json(experiment_dir / PREVIEW_FILE, preview)
    by_condition = ", ".join(f"{condition} USD {value:.6f}" for condition, value in preview["usd_by_condition"].items())
    report(
        f"{config.experiment_name}: {len(sessions)} session(s) over {len(cases)} case(s); worst-case cost USD "
        f"{preview['usd_total']:.6f} ({by_condition}); cap USD {config.budget['cap_usd']:.2f}"
    )

    def invocation(status: str, described: Mapping[str, Any]) -> None:
        _append_jsonl(experiment_dir / INVOCATIONS_FILE, {
            "utc": _utc_now(), "git": dict(git), "client": dict(described), "confirm": confirm, "limit": limit,
            "status": status, "executed": list(result.executed), "aborted": result.aborted,
            "preview_usd": preview["usd_total"],
        })

    if paid:
        if config.design.groups is not None and not ethnicity_signed_off():
            invocation("refused_no_sign_off", {"client": name})
            raise ConfigError(
                "the fictional-group factor (design.ethnicity) is on, and the supervisor's ethics sign-off is not "
                "recorded in CLAUDE.md: no paid run may switch it on until it is (docs/fictional-groups.md, section 6)"
            )
        if not preview["fits_the_cap"]:
            invocation("refused_over_cap", {"client": name})
            raise ConfigError(
                f"the worst-case cost, USD {preview['usd_total']:.6f}, exceeds the cap, USD {config.budget['cap_usd']:.2f}: "
                "shrink the design (docs/rule-generation.md, section 9)"
            )
        if not confirm:
            result.status = STATUS_AWAITING
            invocation(STATUS_AWAITING, {"client": name})
            report("  a paid client, not confirmed: nothing was sent. Read the preview, then run again with --confirm.")
            return result
    if client is None:
        client = make_client(config, name)

    indices = path_indices(sessions)
    records: dict[str, dict[str, Any]] = {}
    budget = len(sessions) if limit is None else max(0, limit)
    for session in sessions:
        path = _session_path(experiment_dir, session.session_id)
        previous = _read_record(path)
        if previous is not None and previous["outcome"] != OUTCOME_ABORTED:
            records[session.session_id] = previous
            result.skipped.append(session.session_id)
            if not path.with_suffix(".md").is_file():  # a record written before transcripts were
                path.with_suffix(".md").write_text(render_transcript(previous), encoding="utf-8", newline="\n")
            continue
        if result.aborted is not None or len(result.executed) >= budget:
            continue
        if previous is not None:
            _set_aside(path)
        record = run_session(config, session, cases[session.case_id], templates[session.condition], client, indices[session.session_id])
        _write_json(path, record)
        path.with_suffix(".md").write_text(render_transcript(record), encoding="utf-8", newline="\n")
        result.executed.append(session.session_id)
        report(f"[{session.index}/{len(sessions)}] {session.session_id}: {record['outcome']}, USD {record['totals']['cost_usd']:.6f}")
        if record["outcome"] == OUTCOME_ABORTED:
            result.aborted = record["error"]
            report(f"  stopped: {record['error']}")
            continue
        records[session.session_id] = record
    result.status = STATUS_ABORTED if result.aborted else STATUS_COMPLETED if len(records) == len(sessions) else STATUS_PARTIAL

    ordered = [records[session.session_id] for session in sessions if session.session_id in records]
    validations = [row for record in ordered for row in validate_session(record, cases[record["session"]["case_id"]])]
    _write_jsonl(experiment_dir / VALIDATION_FILE, validations)
    outcomes = [outcome_row(record, cases[record["session"]["case_id"]], validations) for record in ordered]
    _write_jsonl(experiment_dir / OUTCOMES_FILE, outcomes)
    written = write_rules(config, ordered, validations, experiment_dir)
    _write_jsonl(experiment_dir / WRITTEN_FILE, written)
    if result.status != STATUS_ABORTED and (config.replay_enabled or config.screening is not None):
        replay_and_screen(config, written, records, cases, experiment_dir, git, report)
    screened = screening_rows(experiment_dir, written, config.experiment_name)
    _write_jsonl(experiment_dir / SCREENING_FILE, screened)
    verdicts = [
        {"rule_id": row["rule_id"], "version": row["version"], **{item["kind"]: item["verdict"] for item in row["entries"]}}
        for row in screened
    ]
    summary = summarise(config, result.status, ordered, validations, written, verdicts, cases, preview, _aborted_costs(experiment_dir), outcomes)
    _write_json(experiment_dir / COST_FILE, {
        **summary["cost"], "client": name, "sessions": summary["tokens_per_session"],
        "note": (
            "The mock client is never charged: its actual cost is 0 and its tokens are its own count (0.3 per character)."
            if not paid else "Estimated from the tokens the API reported, at the price table's rates; the provider's bill is authoritative."
        ),
    })
    _write_json(experiment_dir / SUMMARY_FILE, summary)
    (experiment_dir / REPORT_FILE).write_text(report_markdown(summary), encoding="utf-8", newline="\n")
    result.summary = summary
    invocation(result.status, client.describe())
    return result


# --- the command line ---------------------------------------------------------------------------


def cli_run(args: argparse.Namespace) -> int:
    """What ``run_experiment.py`` does with a config that says ``layer: rule_generation``."""
    try:
        config = RuleGenConfig.load(args.config)
        if args.plan:
            plan_ = plan(config)
            preview = plan_.preview
            print(
                f"{config.experiment_name}: rule generation, {len(plan_.sessions)} session(s) over {len(plan_.cases)} case(s) "
                f"({', '.join(f'{name} {count}' for name, count in preview['sessions_by_condition'].items())})"
            )
            print(
                f"  worst-case cost USD {preview['usd_total']:.6f} with model {preview['model']} "
                f"({', '.join(f'{name} USD {value:.6f}' for name, value in preview['usd_by_condition'].items())}); "
                f"cap USD {preview['cap_usd']:.2f}; {'fits' if preview['fits_the_cap'] else 'DOES NOT FIT'}"
            )
            if (args.client or config.llm["client"]) == "mock":
                print("  (with the mock client nothing is charged: this is what the same sessions could cost with deepseek)")
            size = design_size(config, plan_.cases)
            factors = " x ".join(f"{name} {count}" for name, count in size["factors"].items())
            print(f"  design: {factors} = {max(size['cells_per_case'].values(), default=0)} cell(s) per case and condition")
            if config.design.groups is not None and not ethnicity_signed_off():
                print("  the fictional-group factor is on: a paid run is refused until CLAUDE.md records the ethics sign-off")
            return 0
        result = run_rule_generation(config, client_name=args.client, out_root=args.out, confirm=args.confirm, limit=args.limit)
    except (ConfigError, LLMFatalError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"logs: {result.experiment_dir}")
    if result.status == STATUS_AWAITING:
        return 4
    summary = result.summary
    print(
        f"{result.status}: {len(result.executed)} session(s) run, {len(result.skipped)} already done; "
        f"{summary['rules_written']} rule(s) written; actual cost USD {summary['cost']['actual_usd']:.6f}"
    )
    if result.status == STATUS_ABORTED:
        print(f"stopped early: {result.aborted}", file=sys.stderr)
        return 3
    return 0
