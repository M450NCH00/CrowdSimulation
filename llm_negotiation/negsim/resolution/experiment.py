"""The resolution experiment type (issue #58, RF-3; ``docs/resolution.md``, D3 to D6, D8, D13).

A config with ``layer: resolution`` (``configs/resolution/``) runs, in order:

1. **case selection**, from the frozen case store, by case set and/or id (``id@version``);
2. **the design**: the session list, every condition, case and cell (``design.py``);
3. **a worst-case cost preview** (:func:`preview_cost`), printed and written before any call.
   With a paid client nothing is sent unless it fits the budget cap *and* the run is confirmed
   (``--confirm``); without that the experiment stops after the preview;
4. **the sessions** (``protocol.py``), each written whole when it ends, with its transcript;
5. **both replays** of every session with an encounter, ``plan_only`` and ``plan_orca``
   (``replay.py``), with no LLM call, beside plain ORCA on the same seed;
6. **the tables**: ``decisions.jsonl``, ``debriefs.jsonl``, ``outcomes.jsonl`` and
   ``outcomes.csv`` (one row per session), then ``cost.json``, ``summary.json``, ``report.md``.

**Running an experiment again resumes it.** A session with a record is read back, never run or
written again: a paid session's record is never deleted or overwritten (D13). An aborted
session's record is kept as ``<session_id>.aborted<n>.json`` and the session runs again. The
replays and the tables are rebuilt from the records whenever they are missing or derived. A
folder that holds another config, or a run with another client, is refused.

The budget guard (issue #24) and its scoped cap are #30's (``rulegen.experiment``): only this
experiment's own calls count against its cap. The fictional group is not a factor here.

**The core and situational factors** (issue #60, RF-5) are used only when the design varies one:
then the config may name ``templates.factors`` (default ``resolve_factors_v1``) and
``factor_values`` (default ``configs/resolution/factors_v1.yaml``), each session record gains
``factors`` (the levels, the switches, the template) and, when someone carries a load, ``bodies``
(the radii every run of the session uses), and the session's ``surroundings`` sets its hearing
range. A config that varies none of them writes exactly what it wrote before.

**The pairwise perception factors** (issue #61, RF-6; ``pairwise.py``) work the same way: used
only when the design varies one, with ``templates.pairwise`` (default ``resolve_pairwise_v1``);
each session record gains ``pairwise`` (the block, its switches and the template), and the
outcome row each person's own perception as 0 or 1. **Perceived attractiveness needs the
supervisor's ethics sign-off for a paid run** (``negsim.ethics``; ``docs/pairwise-factors.md``,
section 6): without the sentence in ``CLAUDE.md`` the run is refused before anything is sent
(``refused_no_sign_off``). A mock run needs none.

**The core template** is ``resolve_v2`` unless the config names one, and ``resolve_v3`` for a
design that varies an RF-5 or RF-6 factor (``prompt.default_core``; the user's decision of
2026-10-23, issue #61): ``resolve_v3`` also prints a person's factor lines on the short line of
someone 5 to 10 m away. A config that names ``resolve_v2`` keeps it, and ``--plan`` says that
its factor lines then reach an agent only within 5 m.
"""

from __future__ import annotations

import argparse
import csv
import functools
import io
import json
import math
import platform
import sys
from collections import Counter
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from .. import __version__, ethics
from ..configutil import PACKAGE_ROOT, ConfigError, as_choice, as_number, check_keys, load_yaml, resolve_path
from ..experiment.avoidance import simulation_for
from ..llm.base import LLMClient, LLMFatalError
from ..llm.budget import BudgetedClient, BudgetExceededError, BudgetGuard, SpendLedger, estimate_prompt_tokens
from ..llm.deepseek import DeepSeekClient
from ..llm.mock import MockClient
from ..llm.pricing import PriceTable
from ..negotiation.protocol import MAX_ATTEMPTS_PER_TURN
from ..rulegen.cases import CaseStore
from ..rulegen.protocol import LLMSettings
from ..rulegen.replay import source_plan
from ..runlog.schema import OUTCOME_FILE
from ..scenarios.registry import build_crowd_scenario
from .design import ALL_FACTORS, KIND_FRACTIONAL, KIND_SAMPLE, PERSON_FACTORS, ResolutionDesign, Session, cell_code, sessions_for
from .execute import MODES, MODE_PLAN_ONLY, MODE_PLAN_ORCA
from .factors import FACTOR_TEMPLATE, FACTOR_VALUES_CONFIG, FactorTemplate, FactorValues, SessionFactors, with_bodies
from .mock import POLICIES as MOCK_POLICIES
from .outcomes import GENERAL_COLUMNS, MODE_PLAIN_ORCA, RESOLVED
from .pairwise import ATTRACTIVENESS, FAMILIARITY, PAIRWISE_TEMPLATE, PairwiseFactors, PairwiseTemplate
from .perceive import LLM_VIEW_CONFIG, LLMViewSettings
from .factors import SWITCHES as OBSERVABLE
from .prompt import DEBRIEF_TEMPLATE, CoreTemplate, DebriefTemplate, default_core
from .protocol import SESSION_ABORTED, SESSION_COMPLETED, EncounterSession, ProtocolSettings
from .replay import plain_orca, replay_session, run_plan_for
from .reply import ParsedReply
from .scenario import Scenario
from .screening import base_count, resolution
from .scenarios import load_scenario, plugin_for
from .transcript import render as render_transcript
from .view import CHANGES, CONDITION_TALK, CONDITIONS, DETAIL_FULL, DETAIL_SHORT, MOTION_WALKING, Done, Heard, Me, SeenPerson, TimeToMeet, View

LAYER_RESOLUTION = "resolution"
SCHEMA_VERSION = 1  # of the config
#: The version of the files a resolution experiment writes (``docs/log-schema.md``, "Resolution
#: experiments"); the run folders under ``replay/`` are avoidance runs.
RESOLUTION_LOG_VERSION = 1
CLIENTS = ("mock", "deepseek")
RUNS_DIR, MOCK_RUNS_DIR = PACKAGE_ROOT / "runs", PACKAGE_ROOT / "runs_mock"

CONFIG_FILE = "config.json"
INVOCATIONS_FILE = "invocations.jsonl"
CASES_FILE = "cases.json"
DESIGN_FILE = "design.jsonl"
PREVIEW_FILE = "preview.json"
SESSIONS_DIR = "sessions"
DECISIONS_FILE = "decisions.jsonl"
DEBRIEFS_FILE = "debriefs.jsonl"
OUTCOMES_JSONL = "outcomes.jsonl"
OUTCOMES_CSV = "outcomes.csv"
COST_FILE = "cost.json"
SUMMARY_FILE = "summary.json"
REPORT_FILE = "report.md"
REPLAY_DIR = "replay"

STATUS_COMPLETED = "completed"
STATUS_PARTIAL = "partial"
STATUS_ABORTED = "aborted"
STATUS_AWAITING = "awaiting_confirmation"

#: The labels of a physical outcome row, which a session's row has already; every other column
#: (RF-4's general ones, then the scenario's own) is taken into the row once per mode.
PHYSICAL_LABELS = ("session_id", "case_id", "encounter_type", "mode", "agent_a", "agent_b", RESOLVED)
PHYSICAL = tuple(c for c in GENERAL_COLUMNS if c not in PHYSICAL_LABELS)

#: Where the supervisor's approvals are recorded (``negsim.ethics``); a test may point it elsewhere.
SIGN_OFF_FILE = ethics.SIGN_OFF_FILE


def attractiveness_signed_off(path: Optional[Path] = None) -> bool:
    """Whether ``CLAUDE.md`` (or ``path``) records the supervisor's ethics sign-off for perceived
    attractiveness (issue #61; ``docs/pairwise-factors.md``, section 6)."""
    return ethics.recorded(ethics.ATTRACTIVENESS_SIGN_OFF, SIGN_OFF_FILE if path is None else path)


def is_resolution_config(raw: Any) -> bool:
    return isinstance(raw, Mapping) and raw.get("layer") == LAYER_RESOLUTION


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
class ResolutionConfig:
    experiment_name: str
    description: str
    source: str
    case_store: str
    case_set: Optional[str]
    case_ids: tuple[str, ...]
    scenarios: Mapping[str, str]
    conditions: tuple[str, ...]
    design: ResolutionDesign
    protocol: ProtocolSettings
    templates: Mapping[str, str]
    llm_view: str
    llm: Mapping[str, Any]
    budget: Mapping[str, Any]
    factor_values: Optional[str] = None  # issue #60: only when the design varies a core or situational factor

    @classmethod
    def load(cls, path: Path | str) -> "ResolutionConfig":
        return cls.from_raw(load_yaml(resolve_path(path)), str(path).replace("\\", "/"))

    @classmethod
    def from_raw(cls, raw: Any, source: str = "<config>") -> "ResolutionConfig":
        where = f"resolution config {source}"
        check_keys(
            raw, where, ("layer", "experiment_name", "conditions", "design", "llm"),
            ("schema_version", "description", "cases", "scenarios", "protocol", "templates", "llm_view", "budget", "factor_values"),
        )
        if raw["layer"] != LAYER_RESOLUTION:
            raise ConfigError(f"{where}.layer: expected {LAYER_RESOLUTION!r}")
        if raw.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
            raise ConfigError(f"{where}: schema_version {raw['schema_version']!r} is not supported")
        name = str(raw["experiment_name"])
        if not name or not all(ch.isalnum() or ch in "_-" for ch in name):
            raise ConfigError(f"{where}.experiment_name: letters, digits, '_' and '-' only, got {name!r}")
        geometries = isinstance(raw["design"], Mapping) and raw["design"].get("geometries") is not None
        cases = check_keys(raw.get("cases") or {}, f"{where}.cases", (), ("store", "set", "ids"))
        if geometries and (cases.get("set") or cases.get("ids")):
            raise ConfigError(f"{where}: design.geometries are the cases the design runs on; cases may then give only the store")
        if not geometries and not cases.get("set") and not cases.get("ids"):
            raise ConfigError(f"{where}.cases: name a case set, or case ids, or both (or list design.geometries)")
        ids = cases.get("ids") or []
        if not isinstance(ids, list) or len(set(ids)) != len(ids):
            raise ConfigError(f"{where}.cases.ids: a list of distinct case ids (each may be id@version)")
        conditions = raw["conditions"]
        if not isinstance(conditions, list) or not conditions or any(c not in CONDITIONS for c in conditions) or len(set(conditions)) != len(conditions):
            raise ConfigError(f"{where}.conditions: a list of distinct conditions from {list(CONDITIONS)}, got {conditions!r}")
        scenarios = raw.get("scenarios") or {}
        if not isinstance(scenarios, Mapping):
            raise ConfigError(f"{where}.scenarios: a mapping of case id to scenario plug-in")
        templates = check_keys(raw.get("templates") or {}, f"{where}.templates", (), ("core", "debrief", "factors", "pairwise"))
        llm = check_keys(raw["llm"], f"{where}.llm", (), ("client", "mock_policy", "model", "temperature", "max_tokens", "thinking", "transport_retries"))
        budget = check_keys(raw.get("budget") or {}, f"{where}.budget", (), ("cap_usd", "ledger"))
        policy = str(llm.get("mock_policy", "resolution_rehearsal_v1"))
        if policy not in MOCK_POLICIES:
            raise ConfigError(f"{where}.llm.mock_policy: one of {sorted(MOCK_POLICIES)}, got {policy!r}")
        design = ResolutionDesign.from_config(raw["design"], f"{where}.design")
        if not design.uses_factors and (templates.get("factors") is not None or raw.get("factor_values") is not None):
            raise ConfigError(f"{where}: templates.factors and factor_values are for a design that varies a core or situational factor")
        if not design.uses_pairwise and templates.get("pairwise") is not None:
            raise ConfigError(f"{where}: templates.pairwise is for a design that varies a pairwise perception factor")
        core = templates.get("core", default_core(design.uses_factors or design.uses_pairwise))
        chosen = {"core": str(core), "debrief": str(templates.get("debrief", DEBRIEF_TEMPLATE))}
        if design.uses_factors:
            chosen["factors"] = str(templates.get("factors", FACTOR_TEMPLATE))
        if design.uses_pairwise:
            chosen["pairwise"] = str(templates.get("pairwise", PAIRWISE_TEMPLATE))
        default_values = str(FACTOR_VALUES_CONFIG.relative_to(PACKAGE_ROOT)).replace("\\", "/")
        return cls(
            experiment_name=name,
            description=" ".join(str(raw.get("description", "")).split()),
            source=source,
            case_store=str(cases.get("store", "cases")),
            case_set=cases.get("set"),
            case_ids=tuple(str(case) for case in ids),
            scenarios={str(case): str(plugin) for case, plugin in scenarios.items()},
            conditions=tuple(conditions),
            design=design,
            protocol=ProtocolSettings.from_mapping(raw.get("protocol"), f"{where}.protocol"),
            templates=chosen,
            llm_view=str(raw.get("llm_view", str(LLM_VIEW_CONFIG.relative_to(PACKAGE_ROOT)).replace("\\", "/"))),
            llm={
                "client": as_choice(llm.get("client", "mock"), f"{where}.llm.client", CLIENTS),
                "mock_policy": policy,
                "model": str(llm.get("model", "deepseek-flash")),
                "temperature": as_number(llm.get("temperature", 1.0), f"{where}.llm.temperature", minimum=0.0),
                "max_tokens": int(as_number(llm.get("max_tokens", 400), f"{where}.llm.max_tokens", minimum=1)),
                "thinking": as_choice(llm.get("thinking", "disabled"), f"{where}.llm.thinking", ("disabled", "enabled")),
                "transport_retries": int(as_number(llm.get("transport_retries", 2), f"{where}.llm.transport_retries", minimum=0)),
            },
            budget={
                "cap_usd": as_number(budget.get("cap_usd", 0.05), f"{where}.budget.cap_usd", minimum=0.0),
                "ledger": str(budget.get("ledger", "spend_ledger.jsonl")),
            },
            factor_values=str(raw.get("factor_values", default_values)) if design.uses_factors else None,
        )

    def llm_settings(self) -> LLMSettings:
        return LLMSettings(self.llm["model"], self.llm["temperature"], self.llm["max_tokens"], self.llm["thinking"] == "enabled")

    def factor_template(self) -> Optional[FactorTemplate]:
        return FactorTemplate.load(self.templates["factors"]) if "factors" in self.templates else None

    def values(self) -> Optional[FactorValues]:
        return FactorValues.load(resolve_path(self.factor_values)) if self.factor_values is not None else None

    def pairwise_template(self) -> Optional[PairwiseTemplate]:
        return PairwiseTemplate.load(self.templates["pairwise"]) if "pairwise" in self.templates else None

    def as_dict(self) -> dict[str, Any]:
        described = {
            "experiment_name": self.experiment_name,
            "description": self.description,
            "source": self.source,
            "cases": {"store": self.case_store, "set": self.case_set, "ids": list(self.case_ids)},
            "scenarios": dict(self.scenarios),
            "conditions": list(self.conditions),
            "design": self.design.as_dict(),
            "protocol": self.protocol.as_dict(),
            "templates": dict(self.templates),
            "llm_view": self.llm_view,
            "llm": dict(self.llm),
            "budget": dict(self.budget),
        }
        if self.factor_values is not None:  # only a design with factors of issue #60: an older config is described as before
            described["factor_values"] = self.factor_values
        return described


def _comparable(experiment: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in experiment.items() if key != "source"}


def selected_cases(config: ResolutionConfig) -> list[dict[str, Any]]:
    """The cases, in case-id order: a case set's, and/or the ids listed (``id`` or ``id@version``;
    an id of the set without a version takes the set's version, else the latest)."""
    store = CaseStore(resolve_path(config.case_store))
    if config.design.geometries:  # issue #62: the design's geometries are its cases
        chosen = [entry.partition("@") for entry in config.design.geometries]
        return [store.get(case_id, int(version) if version else None) for case_id, _, version in sorted(chosen)]
    in_set = dict(store.case_set(config.case_set)) if config.case_set else {}
    wanted: dict[str, Optional[int]] = {} if config.case_ids else dict(in_set)
    for entry in config.case_ids:
        case_id, _, version = entry.partition("@")
        if config.case_set and case_id not in in_set and not version:
            raise ConfigError(f"case {case_id} is not in case set {config.case_set!r}; give its version (id@version)")
        wanted[case_id] = int(version) if version else in_set.get(case_id)
    return [store.get(case_id, version) for case_id, version in sorted(wanted.items())]


@dataclass(frozen=True)
class Plan:
    cases: Mapping[str, Mapping[str, Any]]
    scenarios: Mapping[str, str]
    sessions: list[Session]
    preview: Mapping[str, Any]


def plan(config: ResolutionConfig) -> Plan:
    """The cases, their plug-ins, the session list and the cost preview: everything that needs no client."""
    cases = {case["case_id"]: case for case in selected_cases(config)}
    unknown = sorted(set(config.scenarios) - set(cases))
    if unknown:
        raise ConfigError(f"scenarios: names cases that are not selected: {unknown}")
    scenarios = {case_id: plugin_for(case, config.scenarios.get(case_id)) for case_id, case in cases.items()}
    geometry_of = check_geometries(cases, scenarios) if config.design.geometries else None
    sessions = sessions_for(
        [(case_id, case["version"], tuple(case["agents"]), scenarios[case_id]) for case_id, case in cases.items()],
        config.design, config.conditions, config.experiment_name, geometry_of,
    )
    if config.design.uses_factors:
        check_bodies(config, sessions, cases)
    return Plan(cases, scenarios, sessions, preview_cost(config, sessions, cases, PriceTable.from_yaml()))


def geometry_label(case: Mapping[str, Any]) -> str:
    """A case's geometry as a session records it: its variant (``layout=apart_20cm``), or its id."""
    variant = case["scenario"].get("variant") or {}
    return ";".join(f"{key}={value}" for key, value in sorted(variant.items())) or case["case_id"]


def check_geometries(cases: Mapping[str, Mapping[str, Any]], scenarios: Mapping[str, str]) -> dict[str, str]:
    """Issue #62 (D14): the geometries of a design are cases of one encounter type, run by one
    plug-in, each a geometry of its own. Returns each case's geometry, by case id."""
    kinds = {(case["formation"]["encounter_class"] or case["scenario"]["type"], scenarios[case_id]) for case_id, case in cases.items()}
    if len(kinds) != 1:
        raise ConfigError(f"design.geometries: cases of one encounter type and one scenario plug-in, got {sorted(map(list, kinds))}")
    labels = {case_id: geometry_label(case) for case_id, case in cases.items()}
    if len(set(labels.values())) != len(labels):
        raise ConfigError(f"design.geometries: two cases have the same geometry: {labels}")
    return labels


# --- the cost preview (task 10) -------------------------------------------------------------------


def _longest(words: Mapping[str, str]) -> str:
    return max(words.values(), key=len)


def worst_view(
    core: CoreTemplate, scenario: Scenario, case: Mapping[str, Any], seen: int, heard: int, history: int, errand: str,
    factor_lines: Optional[Mapping[str, Sequence[str]]] = None,
) -> View:
    """A view with every line a description can have: ``seen`` people in full detail with every
    change, a signal and both demographics; ``heard`` voices from someone unseen; ``history``
    earlier decision points with a signal, both kinds of movement and the outcome "replaced". Its
    free texts (messages, intents) are empty: the preview adds them at the reply cap each.
    ``factor_lines`` are the longest factor lines of each kind (``FactorTemplate.longest``, RF-5):
    the agent's own and its notes, the setting, and what it is told of everyone it sees; and under
    ``pairwise``, the longest pairwise line of each pairwise factor (RF-6), under everyone it sees."""
    lines = factor_lines or {}
    record = case["observations"][str(case["agents"][0])]
    person = SeenPerson(
        1, DETAIL_FULL, 9.99, 1.0, 1.99, 3.0, 1.99, 0.99, MOTION_WALKING, 120, "female", _longest_signal(core), CHANGES,
        factor_lines=tuple(lines.get("other", ())), pairwise_lines=tuple(lines.get("pairwise", ())),
    )
    return View(
        agent_id=case["agents"][0],
        decision_point=2 if history else 1,
        me=Me(1.99, 1.99, 1.99, 0.99, 120, "female", errand, factor_lines=tuple(lines.get("self", ()))),
        place=(*scenario.place_lines(case, record), *lines.get("place", ())),
        notes=tuple(lines.get("note", ())),
        templates={"core": core.identity(), "scenario": scenario.identity()},
        seen=tuple(replace(person, label=n) for n in range(1, seen + 1)),
        heard=tuple(Heard("", None, "behind", "close") for _ in range(heard)),
        history=tuple(Done(99.9, "", "replaced", "", _longest_signal(core), -9.99, 9.99) for _ in range(history)),
        extra_blocks=tuple(scenario.extra_blocks(case, record)),
        time_to_meet=TimeToMeet(1, 99.9) if seen else None,
    )


def _longest_signal(core: CoreTemplate) -> str:
    seen = core.data["view"]["signals_seen"]
    return max(seen, key=lambda name: len(seen[name]))


def preview_cost(config: ResolutionConfig, sessions: Sequence[Session], cases: Mapping[str, Mapping[str, Any]], prices: PriceTable) -> dict[str, Any]:
    """The most the sessions could cost (``docs/encounter-protocol.md``, section 6, derives it).

    Per session, with c the reply cap, k the most people prompted, d the most decision points
    per agent (1 in the independent condition), and every text's tokens estimated high as the
    budget guard does: a decision call's prompt is at most S = P + D + c + R, where P + D is the
    fixed text and the longest description (``worst_view``, with (k - 1) d messages heard in the
    talk condition and d - 1 earlier decisions, each free text at c), c and R the room for a
    failed reply and the retry instruction; a debrief's is at most S + c + B + d c + c + R_B,
    where B is the debrief text with no decision in it. Input <= k d S + k S_B, output <=
    (k d + k) c, each times the most sends a call can make, 2 (1 + transport retries), at the
    peak cache-miss and output prices.
    """
    model, cap = config.llm["model"], config.llm["max_tokens"]
    price = prices.price_of(model)
    p_in, p_out = price.input_cache_miss.peak / 1e6, price.output.peak / 1e6
    sends = MAX_ATTEMPTS_PER_TURN * (1 + config.llm["transport_retries"])
    core, debrief = CoreTemplate.load(config.templates["core"]), DebriefTemplate.load(config.templates["debrief"])
    errand = max(config.design.tasks.values(), key=len)
    view_settings = LLMViewSettings.load(resolve_path(config.llm_view))
    factors, pairwise = config.factor_template(), config.pairwise_template()
    longest = factors.longest(config.design.factors) if factors is not None else None
    if pairwise is not None:
        longest = {**(longest or {}), "pairwise": pairwise.longest(config.design.factors)}
    cache: dict[tuple, dict[str, Any]] = {}
    rows, totals = [], {condition: 0.0 for condition in config.conditions}
    for session in sessions:
        case = cases[session.case_id]
        scenario = load_scenario(session.scenario)
        n = case["scenario"]["n_agents"]
        k = min(scenario.MAX_MEMBERS or n, config.protocol.max_prompted or n, n)
        d = config.protocol.decision_points_for(session.condition)
        seen = min(n - 1, view_settings.max_people or n - 1)
        key = (session.case_id, session.scenario, session.condition)
        if key not in cache:
            heard = (k - 1) * d if session.condition == CONDITION_TALK else 0
            view = worst_view(core, scenario, case, seen, heard, d - 1, errand, longest)
            system = core.system(session.condition, scenario)
            user = core.description(view) + "\n\n" + core.wrapper(view)
            fixed = estimate_prompt_tokens([{"content": system}, {"content": user}]) + (heard + (d - 1)) * cap
            retry = estimate_prompt_tokens([{"content": core.retry(session.condition)}])
            s_decision = fixed + cap + retry
            empty = ParsedReply(session.condition, "", "none", "", (), "")
            b = estimate_prompt_tokens([{"content": debrief.text([empty])}])
            s_debrief = fixed + cap + b + d * cap + cap + estimate_prompt_tokens([{"content": debrief.retry()}])
            cache[key] = {"S_decision": s_decision, "S_debrief": s_debrief}
        bound = cache[key]
        input_tokens = k * d * bound["S_decision"] + k * bound["S_debrief"]
        output_tokens = (k * d + k) * cap
        usd = sends * (input_tokens * p_in + output_tokens * p_out)
        totals[session.condition] += usd
        rows.append({
            "session_id": session.session_id, "condition": session.condition, "k_prompted": k, "d_decision_points": d,
            "calls": k * d + k, "S_decision_tokens": bound["S_decision"], "S_debrief_tokens": bound["S_debrief"],
            "reply_cap_tokens": cap, "input_tokens_bound": sends * input_tokens, "output_tokens_bound": sends * output_tokens,
            "usd_bound": round(usd, 8),
        })
    total = math.fsum(totals.values())
    return {
        "computed_utc": _utc_now(),
        "model": model,
        "prices": {"input_cache_miss_peak_per_million": price.input_cache_miss.peak, "output_peak_per_million": price.output.peak, **prices.describe()},
        "reply_cap_tokens": cap,
        "sends_per_call": sends,
        "sends_from": {"attempts_per_call": MAX_ATTEMPTS_PER_TURN, "transport_retries_per_attempt": config.llm["transport_retries"]},
        "sessions": len(sessions),
        "sessions_by_condition": dict(Counter(session.condition for session in sessions)),
        "usd_by_condition": {name: round(value, 8) for name, value in totals.items()},
        "usd_total": round(total, 8),
        "cap_usd": config.budget["cap_usd"],
        "fits_the_cap": total <= config.budget["cap_usd"],
        "per_session": rows,
    }


# --- the client -----------------------------------------------------------------------------------


def make_client(config: ResolutionConfig, client_name: Optional[str] = None) -> LLMClient:
    """The mock client, or the paid client behind a budget guard on this experiment's own calls."""
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
    """A stable number for each session's case and cell within its condition (the mock reads it)."""
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


def _set_aside(path: Path) -> Path:
    number = 1
    while (aside := path.with_name(f"{path.stem}.aborted{number}.json")).exists():
        number += 1
    path.rename(aside)
    if path.with_suffix(".md").is_file():
        path.with_suffix(".md").rename(aside.with_suffix(".md"))
    return aside


def run_session(
    config: ResolutionConfig, session: Session, case: Mapping[str, Any], client: LLMClient, path_index: int,
    view_settings: LLMViewSettings,
) -> dict[str, Any]:
    """Run one session and return its whole record. A refusal or an unusable model ends it as
    ``aborted``, with everything sent before it."""
    scenario = load_scenario(session.scenario)
    core, debrief = CoreTemplate.load(config.templates["core"]), DebriefTemplate.load(config.templates["debrief"])
    labels = {
        "experiment": config.experiment_name, "session_id": session.session_id, "condition": session.condition,
        "case_id": session.case_id, "repeat": session.repeat, "path_index": path_index,
    }
    run_plan, factors, bodies = source_plan(case), None, {}
    pairwise = session_pairwise(config, session) if session.uses_pairwise else None
    if session.uses_factors:
        factors, values = session_factors(config, session), config.values()
        bodies = session_bodies(factors, values, session, run_plan)
        run_plan = with_bodies(run_plan, bodies)
        hearing = factors.hearing_range_m(values)
        if hearing is not None:
            view_settings = replace(view_settings, hearing_range_m=hearing)
    protocol = EncounterSession(
        simulation_for(run_plan), session.agents, scenario, session.condition, client, config.llm_settings(),
        config.protocol, view_settings, core, debrief, people=session.people,
        show_age=session.visibility.get("age", True), show_gender=session.visibility.get("gender", True), labels=labels,
        factors=factors, pairwise=pairwise,
    )
    started = _utc_now()
    try:
        protocol.run_session()
    except (BudgetExceededError, LLMFatalError):
        pass  # recorded as aborted by the protocol
    record: dict[str, Any] = {
        "resolution_log_version": RESOLUTION_LOG_VERSION,
        "session_id": session.session_id,
        "session": session.as_dict(),
        "case": {"case_id": case["case_id"], "version": case["version"]},
        "scenario": session.scenario,
        "templates": {"core": core.identity(), "debrief": debrief.identity(), "scenario": scenario.identity()},
        "llm": config.llm_settings().as_dict(),
        "started_utc": started,
    }
    if factors is not None:  # issue #60: only a design that varies a core or situational factor
        record["templates"]["factors"] = factors.template.identity()
        record["factors"] = {**factors.as_dict(), "hearing_range_m": view_settings.hearing_range_m}
        if bodies:
            record["bodies"] = bodies
    if pairwise is not None:  # issue #61: only a design that varies a pairwise perception factor
        record["templates"]["pairwise"] = pairwise.template.identity()
        record["pairwise"] = pairwise.as_dict()
    record.update(protocol.as_dict())
    record["encounter"]["type"] = case["formation"]["encounter_class"] or case["scenario"]["type"]
    record["ended_utc"] = _utc_now()
    names = sorted({a["model"] for a in protocol.attempts() if a.get("model")})
    record["model_returned"] = ", ".join(names) or None
    record["replays"] = (
        {mode: f"{REPLAY_DIR}/{session.session_id}/{mode}" for mode in MODES}
        if record["outcome"] == SESSION_COMPLETED else None
    )
    return record


def session_factors(config: ResolutionConfig, session: Session) -> SessionFactors:
    """The core and situational factors of a session (issue #60): each person's levels, the
    switches of the observable ones the design varies, and the setting."""
    visible = {name: session.visibility[name] for levels in session.factor_levels.values() for name in levels if name in session.visibility}
    return SessionFactors(config.factor_template(), session.factor_levels, visible, session.situation)


def session_pairwise(config: ResolutionConfig, session: Session) -> PairwiseFactors:
    """The pairwise perception factors of a session (issue #61): its block, with the switches of
    the factors the design varies."""
    visible = {factor: session.visibility[factor] for factor in (ATTRACTIVENESS, FAMILIARITY) if factor in session.visibility}
    return PairwiseFactors.from_block(session.pairwise, config.pairwise_template(), visible, f"session {session.session_id}: pairwise")


def session_bodies(factors: SessionFactors, values: FactorValues, session: Session, run_plan: Any) -> dict[str, dict[str, Any]]:
    """The radii ``load`` sets for the session's run (issue #60), from the radii the case's run gives."""
    specs = build_crowd_scenario(run_plan.scenario_config).agents
    return factors.bodies({agent: specs[agent].radius for agent in session.agents}, values)


def check_bodies(config: ResolutionConfig, sessions: Sequence[Session], cases: Mapping[str, Mapping[str, Any]]) -> None:
    """Refuse a design whose wider bodies (``load``, issue #60) do not fit a case's run: two people
    who would overlap at the start, a path too narrow for the body, or a loaded body that starts
    closer to someone than the scenario's near-miss distance (the session would begin as a near
    miss, and in the passage cases of issue #32 rounding alone decides whether such a start
    "overlaps"). Checked once per case and set of loaded people, before anything runs."""
    values, checked = None, set()
    for session in sessions:
        loaded = tuple(sorted(agent for agent, levels in session.factor_levels.items() if levels.get("load") == "large_suitcase"))
        if not loaded or (session.case_id, loaded) in checked:
            continue
        checked.add((session.case_id, loaded))
        values = values or config.values()
        run_plan = source_plan(cases[session.case_id])
        bodies = session_bodies(session_factors(config, session), values, session, run_plan)
        try:
            spec = build_crowd_scenario(with_bodies(run_plan, bodies).scenario_config)
            near = spec.thresholds.near_miss_distance
            for agent in loaded:
                me = spec.agents[agent]
                for other in spec.agents:
                    gap = math.dist(me.start.xy, other.start.xy) - me.radius - other.radius
                    if other.agent_id != agent and gap < near:
                        raise ConfigError(
                            f"agents {agent} and {other.agent_id} would start {gap:.3f} m apart, closer than the near-miss "
                            f"distance, {near} m"
                        )
        except ConfigError as exc:
            raise ConfigError(
                f"case {session.case_id}: a person pulling a large suitcase is {values.load_width_added_m} m wider "
                f"(factor_values), and the case's run cannot take that body: {exc}. Leave load out of the design for "
                "this case (docs/resolution.md, D15; WORK_LOG-60.md, open questions)"
            ) from exc


def replay_record(record: Mapping[str, Any], experiment_dir: Path, experiment: str, git: Mapping[str, Any], store: CaseStore) -> dict[str, Any]:
    """Both replays of a session (built if missing) and plain ORCA: each mode's outcome columns."""
    found: dict[str, Any] = {}
    plain = None
    for mode in MODES:
        run_dir = experiment_dir / REPLAY_DIR / record["session_id"] / mode
        if (run_dir / OUTCOME_FILE).is_file():
            block = json.loads((run_dir / OUTCOME_FILE).read_text(encoding="utf-8"))["plans"]
            found[mode], plain = block["physical_outcome"], block["plain_orca"]
            continue
        if plain is None:
            case = store.get(record["case"]["case_id"], record["case"]["version"])
            plain = plain_orca(record, case, run_plan_for(record, case), load_scenario(record["scenario"]))
        found[mode] = replay_session(record, mode, run_dir, experiment, git, store, plain)
    found[MODE_PLAIN_ORCA] = plain["physical_outcome"]
    return found


# --- the tables -----------------------------------------------------------------------------------


def decision_rows(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    """One line per decision point (``decisions.jsonl``)."""
    rows = []
    for point in record.get("decision_points") or []:
        parsed = point.get("parsed") or {}
        rows.append({
            "session_id": record["session_id"], "agent_id": point["agent_id"], "index": point["index"], "number": point["number"],
            "time_s": point["time_s"], "condition": record["condition"], "trigger_reasons": point["trigger_reasons"],
            "parse_error": point.get("parse_error"),
            "message": parsed.get("message"), "signal": parsed.get("signal"), "intent": parsed.get("intent"),
            "steps": parsed.get("steps"), "reason": parsed.get("reason"), "coded": point.get("coded"),
        })
    return rows


def debrief_rows(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    """One line per debrief (``debriefs.jsonl``); every source is unchecked (RF-14 checks it)."""
    rows = []
    for debrief in record.get("debriefs") or []:
        parsed = debrief.get("parsed") or {}
        rows.append({
            "session_id": record["session_id"], "agent_id": debrief["agent_id"], "parse_error": debrief.get("parse_error"),
            "basis": parsed.get("basis"), "kind": parsed.get("kind"), "source": parsed.get("source"),
            "applies_to": parsed.get("applies_to"), "check_status": parsed.get("source_status", "unchecked"),
        })
    return rows


def _agent_columns(record: Mapping[str, Any], agent: Optional[int], prefix: str) -> dict[str, Any]:
    session = record["session"]
    persona = session["personas"].get(str(agent), {}) if agent is not None else {}
    points = [p for p in record.get("decision_points") or [] if p["agent_id"] == agent]
    coded = [p["coded"] for p in points if p.get("coded")]
    first, final = (coded[0], coded[-1]) if coded else ({}, {})
    debrief = next((d.get("parsed") or {} for d in record.get("debriefs") or [] if d["agent_id"] == agent), {})
    signals = [p["parsed"]["signal"] for p in points if p.get("parsed") and p["parsed"]["signal"] != "none"]
    messages = [p for p in points if p.get("parsed") and p["parsed"]["message"]]
    columns = {
        f"{prefix}_agent": agent,
        f"{prefix}_age": persona.get("age"), f"{prefix}_gender": persona.get("gender"),
        f"{prefix}_urgency": persona.get("urgency"), f"{prefix}_errand": persona.get("task"),
        # Issue #60: each core factor the design varies, as this person's level.
        **{f"{prefix}_{name}": persona[name] for name in PERSON_FACTORS if name != "urgency" and name in persona},
        f"{prefix}_decision_points": len(points),
        f"{prefix}_trigger_reasons": "|".join(";".join(p["trigger_reasons"]) for p in points) or None,
        f"{prefix}_unreadable": sum(1 for p in points if p.get("parse_error")),
        f"{prefix}_signals": ";".join(signals) or None,
        f"{prefix}_messages": len(messages),
        f"{prefix}_debrief_kind": debrief.get("kind"), f"{prefix}_debrief_source": debrief.get("source"),
    }
    for which, coding in (("first", first), ("final", final)):
        for key in ("side", "slowed", "stopped", "backed_up", "start_distance_m"):
            columns[f"{prefix}_{which}_{key}"] = coding.get(key)
    return columns


def _pairwise_columns(record: Mapping[str, Any], agent: int, other: int, prefix: str) -> dict[str, Any]:
    """Issue #61: how ``agent`` sees ``other``, from its own point of view, as 0 or 1 (RF-8), for
    each pairwise factor the design varies, whether or not it was told (the switches are the cell's
    columns); and at how many of its decision points it was shown a pairwise line about them, which
    ``resolve_v1`` and ``resolve_v2`` print only in full detail (within 5 m, D2) and ``resolve_v3``
    on a short line too (issue #61)."""
    block = record["session"].get("pairwise")
    if block is None:
        return {}
    values = PairwiseFactors.from_block(block).values(agent, other)
    columns: dict[str, Any] = {}
    if ATTRACTIVENESS in block:
        columns[f"{prefix}_finds_other_attractive"] = values[ATTRACTIVENESS]
    if FAMILIARITY in block:
        columns[f"{prefix}_knows_other"] = values[FAMILIARITY]
    printed = _core(record["templates"]["core"]["key"]).prints_extra_lines
    shown = 0
    for point in record.get("decision_points") or []:
        if point["agent_id"] != agent:
            continue
        label = (point["view"].get("labels") or {}).get("label_of_agent", {}).get(str(other))
        if any(p["label"] == label and printed(p["detail"]) and p.get("pairwise_lines") for p in point["view"]["seen"]):
            shown += 1
    columns[f"{prefix}_pairwise_lines_shown"] = shown
    return columns


@functools.lru_cache(maxsize=None)
def _core(key: str) -> CoreTemplate:
    return CoreTemplate.load(key)


def outcome_row(record: Mapping[str, Any], case: Mapping[str, Any], physical: Optional[Mapping[str, Mapping[str, Any]]]) -> dict[str, Any]:
    """One session's row (task 9): design, factors, both people's decisions, both modes' physical
    outcome, the debriefs, tokens and cost."""
    session, encounter = record["session"], record.get("encounter") or {}
    end = encounter.get("end") or {}
    agents = session["agents"]
    first = agents[0] if session["cell"]["mapping"] == "p1_lower" else agents[1]
    second = agents[1] if first == agents[0] else agents[0]
    variant = case["scenario"].get("variant") or {}
    row: dict[str, Any] = {
        "session_id": record["session_id"], "outcome": record["outcome"], "case_id": case["case_id"], "case_version": case["version"],
        "case_geometry": ";".join(f"{key}={value}" for key, value in sorted(variant.items())) or None,
        "encounter_type": encounter.get("type") or case["formation"]["encounter_class"], "scenario_plugin": record["scenario"],
        "condition": record["condition"], "mapping": session["cell"]["mapping"], "repeat": session["repeat"],
        "exact_repeat_set": session["exact_repeat_set"],
        # Issue #62: only when the design lists geometries, or the session is half of a counterfactual pair.
        **{key: session[key] for key in ("geometry", "pair_id", "pair_role", "pair_factor") if key in session},
        "model": record["llm"]["model"], "temperature": record["llm"]["temperature"],
        **{name: session["cell"][name] for name in ALL_FACTORS if name in session["cell"]},
        **_agent_columns(record, first, "p1"),
        **_pairwise_columns(record, first, second, "p1"),
        **_agent_columns(record, second, "p2"),
        **_pairwise_columns(record, second, first, "p2"),
        "encounter_size": len(encounter.get("agents") or []),
        "prompted": len(encounter.get("prompted") or []),
        "left_out_by_cap": len(encounter.get("left_out_by_cap") or []),
        "encounter_start_s": None if not encounter.get("trigger") else encounter["trigger"]["time_s"],
        "end_reason": end.get("reason"), "end_s": end.get("time_s"),
        "not_resolved_by_llm": end.get("not_resolved_by_llm") if encounter.get("trigger") else None,
        "orca_took_over_s": None,
    }
    if encounter.get("orca_took_over"):
        row["orca_took_over_s"] = round(encounter["orca_took_over"]["step"] * case["scenario"]["dt_s"], 6)
    for mode in (MODE_PLAN_ONLY, MODE_PLAN_ORCA, MODE_PLAIN_ORCA):
        columns = (physical or {}).get(mode) or {}
        for name in [*PHYSICAL, *(key for key in columns if key not in PHYSICAL and key not in PHYSICAL_LABELS)]:
            row[f"{name}_{mode}"] = columns.get(name)
        row[f"resolved_{mode}"] = columns.get(RESOLVED)
    resolved = row[f"resolved_{MODE_PLAN_ONLY}"]
    row["resolved_by_llm"] = None if resolved is None else bool(resolved and not row["not_resolved_by_llm"])
    totals = record.get("totals") or {}
    row.update({
        "llm_calls": totals.get("llm_calls"), "prompt_tokens": (totals.get("tokens") or {}).get("prompt_tokens"),
        "completion_tokens": (totals.get("tokens") or {}).get("completion_tokens"), "cost_usd": totals.get("cost_usd"),
    })
    others = [agent for agent in encounter.get("agents") or [] if agent not in agents]
    row["others"] = [_agent_columns(record, agent, "other") for agent in others]
    return row


def outcomes_csv(rows: Sequence[Mapping[str, Any]]) -> str:
    """``outcomes.csv``: every column of the rows but ``others`` (in ``outcomes.jsonl`` only)."""
    names: list[str] = []
    for row in rows:
        names.extend(key for key in row if key not in names and key != "others")
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=names, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: ("" if row.get(key) is None else row.get(key)) for key in names})
    return out.getvalue()


# --- the summary and the report -------------------------------------------------------------------


def _rate(values: Sequence[Any]) -> Optional[float]:
    known = [bool(v) for v in values if v is not None]
    return round(sum(known) / len(known), 4) if known else None


def summarise(config: ResolutionConfig, status: str, records: Sequence[Mapping[str, Any]], rows: Sequence[Mapping[str, Any]], preview: Mapping[str, Any], aborted_usd: float) -> dict[str, Any]:
    groups: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = f"{row['encounter_type']}/{row['scenario_plugin']}/{row['condition']}"
        groups.setdefault(key, {"encounter_type": row["encounter_type"], "scenario_plugin": row["scenario_plugin"], "condition": row["condition"], "rows": []})["rows"].append(row)
    by_group = {}
    for key, group in sorted(groups.items()):
        mine = group["rows"]
        met = [row for row in mine if row["outcome"] == SESSION_COMPLETED]
        by_group[key] = {
            "encounter_type": group["encounter_type"], "scenario_plugin": group["scenario_plugin"], "condition": group["condition"], "sessions": len(mine),
            "with_an_encounter": len(met),
            "resolved_plan_only": _rate([row["resolved_plan_only"] for row in met]),
            "resolved_plan_orca": _rate([row["resolved_plan_orca"] for row in met]),
            "resolved_by_llm": _rate([row["resolved_by_llm"] for row in met]),
            "resolved_plain_orca": _rate([row["resolved_plain_orca"] for row in met]),
            "not_resolved_by_llm": sum(bool(row["not_resolved_by_llm"]) for row in met),
            "mean_decision_points": round(sum(row["p1_decision_points"] + row["p2_decision_points"] + sum(o["other_decision_points"] for o in row["others"]) for row in mine) / len(mine), 3),
            "mean_calls": round(sum(row["llm_calls"] or 0 for row in mine) / len(mine), 3),
            "cap_reached": sum(1 for row in mine if row["left_out_by_cap"]),
        }
    preview_by_session = {row["session_id"]: row for row in preview["per_session"]}
    tokens = []
    for record in records:
        totals = record["totals"]
        bound = preview_by_session.get(record["session_id"], {})
        tokens.append({
            "session_id": record["session_id"], "condition": record["condition"], "outcome": record["outcome"],
            "llm_calls": totals["llm_calls"], "prompt_tokens": totals["tokens"]["prompt_tokens"],
            "completion_tokens": totals["tokens"]["completion_tokens"], "cost_usd": totals["cost_usd"],
            "preview_input_tokens": bound.get("input_tokens_bound"), "preview_output_tokens": bound.get("output_tokens_bound"),
            "preview_usd": bound.get("usd_bound"),
        })
    shares = [
        max(row["prompt_tokens"] / row["preview_input_tokens"], row["completion_tokens"] / row["preview_output_tokens"])
        for row in tokens if row["preview_input_tokens"] and row["preview_output_tokens"]
    ]
    failures: Counter[str] = Counter()
    for record in records:
        for point in record.get("decision_points") or []:
            if len(point["attempts"]) > 1:
                failures["retried_decision_points"] += 1
            if point.get("parse_error"):
                failures[f"unreadable_decision_point:{point['parse_error'].split(':')[0]}"] += 1
        for debrief in record.get("debriefs") or []:
            if debrief.get("parse_error"):
                failures[f"unreadable_debrief:{debrief['parse_error'].split(':')[0]}"] += 1
        failures[f"outcome_{record['outcome']}"] += 1
    spent = math.fsum(row["cost_usd"] for row in tokens) + aborted_usd
    return {
        "experiment": config.experiment_name,
        "status": status,
        "sessions": len(records),
        "sessions_planned": preview["sessions"],
        "by_encounter_type_and_condition": by_group,
        "end_reasons": dict(Counter(row["end_reason"] for row in rows)),
        "debrief_kinds": dict(Counter(d["kind"] for record in records for d in debrief_rows(record) if d["kind"])),
        "tokens_per_session": tokens,
        "largest_share_of_the_preview_used": round(max(shares), 4) if shares else None,
        "cost": {"preview_usd": preview["usd_total"], "actual_usd": round(spent, 10), "of_which_aborted_sessions_usd": round(aborted_usd, 10), "cap_usd": config.budget["cap_usd"]},
        "failure_modes": dict(sorted(failures.items())),
    }


def _pct(value: Optional[float]) -> str:
    return "-" if value is None else f"{100.0 * value:.0f}%"


def report_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        f"# Resolution: {summary['experiment']}",
        "",
        f"Status {summary['status']}: {summary['sessions']} of {summary['sessions_planned']} session(s) have a record.",
        "",
        "## Physical resolution, per encounter type and condition",
        "",
        "Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near "
        "miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in "
        "`plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were "
        "chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.",
        "",
        "| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for group in summary["by_encounter_type_and_condition"].values():
        lines.append(
            f"| {group['encounter_type']} | {group['scenario_plugin']} | {group['condition']} | {group['sessions']} | {group['with_an_encounter']} | "
            f"{_pct(group['resolved_plan_only'])} | {_pct(group['resolved_plan_orca'])} | {_pct(group['resolved_by_llm'])} | "
            f"{_pct(group['resolved_plain_orca'])} | {group['not_resolved_by_llm']} | {group['mean_decision_points']} | "
            f"{group['mean_calls']} | {group['cap_reached']} |"
        )
    cost = summary["cost"]
    lines += [
        "",
        "## How encounters ended",
        "",
        *[f"- {reason}: {count}" for reason, count in summary["end_reasons"].items()],
        "",
        "## Debriefs",
        "",
        *([f"- {kind}: {count}" for kind, count in sorted(summary["debrief_kinds"].items())] or ["None."]),
        "",
        "## Tokens and cost",
        "",
        f"Preview (worst case) USD {cost['preview_usd']}; actual USD {cost['actual_usd']} (aborted sessions USD "
        f"{cost['of_which_aborted_sessions_usd']}); cap USD {cost['cap_usd']}. At most {summary['largest_share_of_the_preview_used']} "
        "of a session's preview was used.",
        "",
        "## Failure modes",
        "",
        *[f"- {name}: {count}" for name, count in summary["failure_modes"].items()],
    ]
    return "\n".join(lines) + "\n"


# --- one experiment -------------------------------------------------------------------------------


@dataclass
class ResolutionResult:
    experiment_dir: Path
    status: str = STATUS_COMPLETED
    preview: Optional[Mapping[str, Any]] = None
    executed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    aborted: Optional[str] = None
    summary: Optional[dict[str, Any]] = None


def _start_folder(experiment_dir: Path, config: ResolutionConfig, client_name: str, git: Mapping[str, Any], view_settings: LLMViewSettings) -> None:
    """Write the config, or check that the folder's is this one, once a session has run."""
    path = experiment_dir / CONFIG_FILE
    started = any((experiment_dir / SESSIONS_DIR).glob("*.json"))
    if path.is_file() and started:
        existing = json.loads(path.read_text(encoding="utf-8"))
        if _comparable(existing.get("experiment", {})) != _comparable(config.as_dict()):
            raise ConfigError(
                f"{experiment_dir} holds a run of another config of {config.experiment_name}; give the changed config a new "
                "experiment_name, or another --out"
            )
        if existing.get("client_name") != client_name:
            raise ConfigError(f"{experiment_dir} was run with the {existing.get('client_name')} client, not {client_name}")
        return
    _write_json(path, {
        "resolution_log_version": RESOLUTION_LOG_VERSION, "layer": LAYER_RESOLUTION, "experiment": config.as_dict(),
        "client_name": client_name, "created_utc": _utc_now(), "git": dict(git),
        "software": {"negsim_version": __version__, "python": platform.python_version()},
        "templates": {
            "core": CoreTemplate.load(config.templates["core"]).identity(),
            "debrief": DebriefTemplate.load(config.templates["debrief"]).identity(),
        },
        "llm_view": view_settings.as_dict(),
        **({"factors": {"template": config.factor_template().identity(), "values": config.values().as_dict()}} if config.factor_values is not None else {}),
        **({"pairwise": {"template": config.pairwise_template().identity()}} if "pairwise" in config.templates else {}),
    })


def run_resolution(
    config: ResolutionConfig,
    client: Optional[LLMClient] = None,
    client_name: Optional[str] = None,
    out_root: Optional[Path | str] = None,
    confirm: bool = False,
    limit: Optional[int] = None,
    report: Callable[[str], None] = print,
    git: Optional[Mapping[str, Any]] = None,
) -> ResolutionResult:
    """Run (or resume) a resolution experiment end to end. ``limit`` runs at most N sessions that
    have no record yet."""
    name = client.name if client is not None else (client_name or config.llm["client"])
    if name not in CLIENTS:
        raise ConfigError(f"unknown client {name!r}; expected one of {list(CLIENTS)}")
    paid = name != "mock"
    experiment_dir = Path(out_root if out_root is not None else (RUNS_DIR if paid else MOCK_RUNS_DIR)) / config.experiment_name
    result = ResolutionResult(experiment_dir)
    if git is None:
        from ..experiment.batch import git_state

        git = git_state()
    plan_ = plan(config)
    cases, sessions, preview = plan_.cases, plan_.sessions, plan_.preview
    result.preview = preview
    view_settings = LLMViewSettings.load(resolve_path(config.llm_view))
    _start_folder(experiment_dir, config, name, git, view_settings)
    _write_json(experiment_dir / CASES_FILE, [
        {"case_id": case_id, "version": case["version"], "scenario": case["scenario"]["type"], "plugin": plan_.scenarios[case_id],
         "encounter_class": case["formation"]["encounter_class"], "n_agents": case["scenario"]["n_agents"], "agents": case["agents"]}
        for case_id, case in cases.items()
    ])
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
            "status": status, "executed": list(result.executed), "aborted": result.aborted, "preview_usd": preview["usd_total"],
        })

    if paid:
        if config.design.uses_attractiveness and not attractiveness_signed_off():
            invocation("refused_no_sign_off", {"client": name})
            raise ConfigError(
                "the design varies perceived attractiveness, and the supervisor's ethics sign-off for it is not recorded in "
                "CLAUDE.md: no paid run may switch it on until it is (docs/pairwise-factors.md, section 6)"
            )
        if not preview["fits_the_cap"]:
            invocation("refused_over_cap", {"client": name})
            raise ConfigError(
                f"the worst-case cost, USD {preview['usd_total']:.6f}, exceeds the cap, USD {config.budget['cap_usd']:.2f}: "
                "shrink the design (docs/encounter-protocol.md, section 6)"
            )
        if not confirm:
            result.status = STATUS_AWAITING
            invocation(STATUS_AWAITING, {"client": name})
            report("  a paid client, not confirmed: nothing was sent. Read the preview, then run again with --confirm.")
            return result
    if client is None:
        client = make_client(config, name)

    store = CaseStore(resolve_path(config.case_store))
    indices = path_indices(sessions)
    records: dict[str, dict[str, Any]] = {}
    budget = len(sessions) if limit is None else max(0, limit)
    for session in sessions:
        path = _session_path(experiment_dir, session.session_id)
        previous = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
        if previous is not None and previous["outcome"] != SESSION_ABORTED:
            records[session.session_id] = previous
            result.skipped.append(session.session_id)
            if not path.with_suffix(".md").is_file():
                path.with_suffix(".md").write_text(render_transcript(previous), encoding="utf-8", newline="\n")
            continue
        if result.aborted is not None or len(result.executed) >= budget:
            continue
        if previous is not None:
            _set_aside(path)
        record = run_session(config, session, cases[session.case_id], client, indices[session.session_id], view_settings)
        _write_json(path, record)
        path.with_suffix(".md").write_text(render_transcript(record), encoding="utf-8", newline="\n")
        result.executed.append(session.session_id)
        report(
            f"[{session.index}/{len(sessions)}] {session.session_id}: {record['outcome']}"
            + (f", {record['encounter']['end']['reason']}" if record["encounter"].get("end") else "")
            + f", {record['totals']['llm_calls']} call(s), USD {record['totals']['cost_usd']:.6f}"
        )
        if record["outcome"] == SESSION_ABORTED:
            result.aborted = record["error"]
            report(f"  stopped: {record['error']}")
            continue
        records[session.session_id] = record
    result.status = STATUS_ABORTED if result.aborted else STATUS_COMPLETED if len(records) == len(sessions) else STATUS_PARTIAL

    ordered = [records[session.session_id] for session in sessions if session.session_id in records]
    _write_jsonl(experiment_dir / DECISIONS_FILE, [row for record in ordered for row in decision_rows(record)])
    _write_jsonl(experiment_dir / DEBRIEFS_FILE, [row for record in ordered for row in debrief_rows(record)])
    rows = []
    for record in ordered:
        physical = None
        if record["outcome"] == SESSION_COMPLETED:
            physical = replay_record(record, experiment_dir, config.experiment_name, git, store)
        rows.append(outcome_row(record, cases[record["case"]["case_id"]], physical))
    _write_jsonl(experiment_dir / OUTCOMES_JSONL, rows)
    (experiment_dir / OUTCOMES_CSV).write_text(outcomes_csv(rows), encoding="utf-8", newline="\n")
    aborted_usd = math.fsum(
        json.loads(p.read_text(encoding="utf-8"))["totals"]["cost_usd"] for p in sorted((experiment_dir / SESSIONS_DIR).glob("*.aborted*.json"))
    )
    summary = summarise(config, result.status, ordered, rows, preview, aborted_usd)
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


# --- the command line -----------------------------------------------------------------------------


def print_plan(config: ResolutionConfig, client_name: Optional[str] = None, out: Callable[[str], None] = print) -> Plan:
    plan_ = plan(config)
    preview = plan_.preview
    out(
        f"{config.experiment_name}: resolution, {len(plan_.sessions)} session(s) over {len(plan_.cases)} case(s) "
        f"({', '.join(f'{name} {count}' for name, count in preview['sessions_by_condition'].items())})"
    )
    out(f"  worst-case cost USD {preview['usd_total']:.6f} with model {preview['model']}; cap USD {preview['cap_usd']:.2f}; "
        f"{'fits' if preview['fits_the_cap'] else 'DOES NOT FIT'}")
    for condition in config.conditions:
        mine = [row for row in preview["per_session"] if row["condition"] == condition]
        out(
            f"  {condition}: {len(mine)} session(s), USD {preview['usd_by_condition'][condition]:.6f}; per session at most "
            f"{max((row['calls'] for row in mine), default=0)} call(s) of up to {preview['sends_per_call']} send(s) each, "
            f"USD {max((row['usd_bound'] for row in mine), default=0.0):.6f}"
        )
    if (client_name or config.llm["client"]) == "mock":
        out("  (with the mock client nothing is charged: this is what the same sessions could cost with deepseek)")
    for line in design_lines(config, plan_):
        out(f"  {line}")
    if config.design.uses_attractiveness and not attractiveness_signed_off():
        out("  perceived attractiveness is on: a paid run is refused until CLAUDE.md records the ethics sign-off")
    seen_lines = config.design.uses_pairwise or any(name in config.design.levels for name in OBSERVABLE)
    if seen_lines and not _core(config.templates["core"]).prints_extra_lines(DETAIL_SHORT):
        out(
            f"  core template {config.templates['core']}: what others are told of a person's factors is printed only within 5 m, "
            "so in a head-on case it never reaches an agent (resolve_v3 prints it from 10 m; docs/pairwise-factors.md, section 1)"
        )
    return plan_


def design_lines(config: ResolutionConfig, plan_: Plan) -> list[str]:
    """What ``--plan`` says of the design (issue #62, task 8): its kind and cells, the cases or
    geometries, the exact-repeat set, the counterfactual pairs, and the sessions per condition."""
    design = config.design
    if design.kind == KIND_FRACTIONAL:
        k = len(design.screened)
        found = resolution(k, design.size)
        kind = f"a 2^({k}-{k - base_count(design.size)}) fraction of {k} two-level factor(s), " + (f"resolution {found}" if found else "in full")
    elif design.kind == KIND_SAMPLE:
        kind = f"a balanced random sample of the {math.prod(len(design.levels[name]) for name in design.factors)} cells of the full factorial"
    else:
        kind = "every combination"
    lines = [f"design: {design.kind}, {kind}; {design.cells()} cell(s) per case and condition, {design.repeats} repeat(s) each"]
    if design.geometries:
        geometries = sorted({(session.case_id, session.geometry) for session in plan_.sessions})
        lines.append(f"geometries: {len(geometries)}, every cell once on each: " + ", ".join(f"{case} ({label})" for case, label in geometries))
    if design.exact_repeats is not None:
        cells, times = design.exact_repeats
        extra = sum(1 for session in plan_.sessions if session.exact_repeat_set and session.repeat > 1)
        lines.append(f"exact-repeat set: {cells} cell(s), each run {times} times in all on one geometry: {extra} session(s) more")
    if design.counterfactual_pairs:
        named = ", ".join(sorted({pair.factor for pair in design.counterfactual_pairs}))
        lines.append(f"counterfactual pairs: {len(design.counterfactual_pairs)} (flipping {named}), two sessions each per case and condition")
    for condition in config.conditions if design.exact_repeats is not None or design.counterfactual_pairs else ():
        mine = [session for session in plan_.sessions if session.condition == condition]
        repeats = sum(1 for session in mine if session.repeat > 1)
        pairs = sum(1 for session in mine if session.pair_id is not None)
        lines.append(f"{condition}: {len(mine)} session(s): {len(mine) - repeats - pairs} of the design, {repeats} exact repeat(s), {pairs} in pairs")
    return lines


def cli_run(args: argparse.Namespace) -> int:
    """What ``run_experiment.py`` does with a config that says ``layer: resolution``."""
    try:
        config = ResolutionConfig.load(args.config)
        if args.plan:
            print_plan(config, args.client)
            return 0
        result = run_resolution(config, client_name=args.client, out_root=args.out, confirm=args.confirm, limit=args.limit)
    except (ConfigError, LLMFatalError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"logs: {result.experiment_dir}")
    if result.status == STATUS_AWAITING:
        return 4
    summary = result.summary
    print(f"{result.status}: {len(result.executed)} session(s) run, {len(result.skipped)} already done; actual cost USD {summary['cost']['actual_usd']:.6f}")
    if result.status == STATUS_ABORTED:
        print(f"stopped early: {result.aborted}", file=sys.stderr)
        return 3
    return 0
