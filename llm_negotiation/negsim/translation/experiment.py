"""A rule-translation experiment (issue #67, RF-12; ``docs/rule-translation.md``).

    python run_experiment.py configs/translation/round1_head_on.yaml --plan
    python run_experiment.py configs/translation/round1_head_on.yaml                      # mock, runs_mock/
    python run_experiment.py configs/translation/round1_head_on.yaml --client deepseek    # preview only
    python run_experiment.py configs/translation/round1_head_on.yaml --client deepseek --confirm

For each rule a rule extraction kept (RF-11, ``status: candidate``): one call translates it into
rule format 3 (template ``translate_v1``), or since issue #108 (RF-31) into rule format 4
(``translate_v2``; the format is the one its common template describes), the rule loader's checks give it a category
(``negsim.rulegen.validate``), and what the format could not say is recorded, by the translator and
mechanically (``negsim.translation.losses``). A valid translation is written into the experiment's
staging database, then switched on alone and run on the Step 1 sessions it was extracted from (the
identity check, ``negsim.translation.identity``) and in a crowd (``negsim.rulegen.replay``), and
both results are stored as its next version. A rule extracted as ``needs_communication`` is
translated and written, but marked not runnable in ORCA, and neither replayed nor screened.

**Money.** With a paid client nothing is sent without ``--confirm``; every call goes through the
budget guard on this experiment's own calls (``budget.cap_usd``). A paid run translates only
``candidate`` rules.

**Records.** Each rule's translation record (``translations/<rule_id>.json``: the exact messages,
every raw reply, tokens, cost, the reply as read) is written once, when its call ends, and never
rewritten; running the experiment again reuses it and redoes only an aborted one (set aside as
``<rule_id>.aborted<n>.json``). Writing, the identity check and screening are idempotent: a staged
rule that has its screening already is not run again.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

import yaml

from .. import __version__
from ..configutil import PACKAGE_ROOT, ConfigError, as_choice, as_number, check_keys, load_yaml, resolve_path
from ..extraction.prompt import ExtractTemplate
from ..llm.base import LLMClient, LLMFatalError, LLMRequest, LLMTransientError
from ..llm.budget import BudgetedClient, BudgetExceededError, BudgetGuard, SpendLedger, estimate_prompt_tokens
from ..llm.deepseek import DeepSeekClient
from ..llm.mock import MockClient
from ..llm.pricing import PriceTable
from ..negotiation.parsing import TurnParseError
from ..rules.database import MANIFEST_FILE, file_sha256
from ..rulegen import validate as V
from ..rulegen.describe import rule_schema_version_of
from ..rules.fields import VISIBLE_FACTOR_SWITCHES
from ..rulegen.replay import CrowdScreen, ScreeningSettings, crowd_size, mixed_population
from ..rulegen.writer import StagingDatabase, with_screening
from ..personas.schema import ATTRIBUTES
from . import identity as I
from .losses import action_flags, counted, factor_losses
from .mock import POLICIES as MOCK_POLICIES
from .prompt import DEFAULT_TEMPLATE, RenderedTranslation, load as load_template, render, retry_message
from .reply import parse_translation, repair_one_brace

LAYER = "rule_translation"
SCHEMA_VERSION = 1
TRANSLATION_LOG_VERSION = 1
CLIENTS = ("mock", "deepseek")
RUNS_DIR, MOCK_RUNS_DIR = PACKAGE_ROOT / "runs", PACKAGE_ROOT / "runs_mock"
#: Most attempts at one translation: a first reply, and one retry if it cannot be read.
MAX_ATTEMPTS = 2
#: The reply cap when a config gives none: a format 3 rule, the parts lost and a note.
DEFAULT_MAX_TOKENS = 1500
STATUSES = ("candidate", "unstable")
#: The rule format the translations of ``translate_v1`` are written in (``rulegen_common_v2``
#: describes it). A later template's common template says its own (issue #108: ``translate_v2``, 4).
RULE_SCHEMA_VERSION = 3
STAGING_DIR = "rule_db_staging/extracted"
TRANSLATIONS_DIR = "translations"
IDENTITY_DIR = "identity"
SCREENING_DIR = "screening"
#: The category of a translation whose rule is null: the translator said no part of it can be written.
NOT_EXPRESSIBLE = "not_expressible"

RUN_COMPLETED, RUN_UNREADABLE, RUN_ABORTED = "completed", "unreadable", "aborted"
STATUS_COMPLETED, STATUS_PARTIAL, STATUS_AWAITING = "completed", "partial", "awaiting_confirmation"
#: What both people can see in the crowd and in the validation: a format 3 rule may read age and gender.
ALL_VISIBLE = {"speed": True, "size": True, "age": True, "gender": True}


def visible_for(schema_version: int) -> dict[str, bool]:
    """What both people can see, for a rule of ``schema_version``: from format 4 (issue #108) also a
    cane, a suitcase and a phone. A format 3 translation is checked and screened exactly as before."""
    return {**ALL_VISIBLE, **({name: True for name in VISIBLE_FACTOR_SWITCHES} if schema_version >= 4 else {})}


def is_translation_config(raw: Any) -> bool:
    return isinstance(raw, Mapping) and raw.get("layer") == LAYER


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def _append_jsonl(path: Path, row: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _relative(path: Path | str) -> str:
    resolved = Path(path).resolve()
    return resolved.relative_to(PACKAGE_ROOT).as_posix() if resolved.is_relative_to(PACKAGE_ROOT) else resolved.as_posix()


# --- the config ----------------------------------------------------------------------------------


@dataclass(frozen=True)
class TranslationConfig:
    experiment_name: str
    description: str
    source: str
    extraction: str
    statuses: tuple[str, ...]
    encounter_types: Optional[tuple[str, ...]]
    template: str
    llm: Mapping[str, Any]
    budget: Mapping[str, Any]
    identity: bool
    screening: Optional[ScreeningSettings]
    crowd_ages: tuple[int, ...]
    crowd_genders: tuple[str, ...]
    #: Issue #108: core factors the screening crowd is given in turn (``mixed_population``), so that a
    #: format 4 rule that reads them can apply. Empty: ages and genders only, as before.
    crowd_factors: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    #: Issue #108: only these extracted rules (by id), or every one of the statuses (``None``).
    rules: Optional[tuple[str, ...]] = None
    #: Issue #108: read a reply one closing brace short, where exactly one placement loads (``reply.py``).
    repair_one_brace: bool = False

    @classmethod
    def load(cls, path: Path | str) -> "TranslationConfig":
        return cls.from_raw(load_yaml(resolve_path(path)), str(path).replace("\\", "/"))

    @classmethod
    def from_raw(cls, raw: Any, source: str = "<config>") -> "TranslationConfig":
        where = f"rule-translation config {source}"
        check_keys(raw, where, ("layer", "experiment_name", "extraction", "llm"),
                   ("schema_version", "description", "statuses", "encounter_types", "template", "budget", "identity", "screening", "rules", "reader"))
        if raw["layer"] != LAYER:
            raise ConfigError(f"{where}.layer: expected {LAYER!r}")
        if raw.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
            raise ConfigError(f"{where}: schema_version {raw['schema_version']!r} is not supported")
        name = str(raw["experiment_name"])
        if not name or not all(ch.isalnum() or ch in "_-" for ch in name):
            raise ConfigError(f"{where}.experiment_name: letters, digits, '_' and '-' only, got {name!r}")
        statuses = raw.get("statuses", ["candidate"])
        if not isinstance(statuses, list) or not statuses or not set(statuses) <= set(STATUSES) or len(set(statuses)) != len(statuses):
            raise ConfigError(f"{where}.statuses: a list of {list(STATUSES)}, got {statuses!r}")
        types = raw.get("encounter_types")
        if types is not None and (not isinstance(types, list) or not types):
            raise ConfigError(f"{where}.encounter_types: a list of encounter types, or leave it out for every type")
        llm = check_keys(raw["llm"], f"{where}.llm", (), ("client", "mock_policy", "model", "temperature", "max_tokens", "thinking", "transport_retries"))
        policy = str(llm.get("mock_policy", "translate_rehearsal_v1"))
        if policy not in MOCK_POLICIES:
            raise ConfigError(f"{where}.llm.mock_policy: one of {sorted(MOCK_POLICIES)}, got {policy!r}")
        budget = check_keys(raw.get("budget") or {}, f"{where}.budget", (), ("cap_usd", "ledger"))
        reader = check_keys(raw.get("reader") or {}, f"{where}.reader", (), ("repair_one_brace",))
        only = raw.get("rules")
        if only is not None and (not isinstance(only, list) or not only or not all(isinstance(r, str) for r in only)):
            raise ConfigError(f"{where}.rules: a list of extracted rule ids, or leave it out for every rule of the statuses")
        identity = check_keys(raw.get("identity") or {}, f"{where}.identity", (), ("enabled",))
        screening_raw = dict(raw.get("screening") or {})
        ages = screening_raw.pop("ages", [25, 70])
        genders = screening_raw.pop("genders", ["female", "male"])
        factors = screening_raw.pop("factors", {}) or {}
        if not isinstance(factors, Mapping) or not all(isinstance(levels, list) and levels for levels in factors.values()):
            raise ConfigError(f"{where}.screening.factors: a mapping from a core factor to a list of its levels")
        for factor, levels in factors.items():
            known = ATTRIBUTES.get(factor)
            if known is None or not known.levels or not set(levels) <= set(known.levels):
                raise ConfigError(f"{where}.screening.factors.{factor}: a core factor and its levels {list(known.levels) if known and known.levels else ''}")
        if not isinstance(ages, list) or not ages or not all(isinstance(a, int) and a > 0 for a in ages):
            raise ConfigError(f"{where}.screening.ages: a list of whole numbers of years")
        if not isinstance(genders, list) or not genders or not set(genders) <= {"female", "male", "nonbinary"}:
            raise ConfigError(f"{where}.screening.genders: a list of female, male or nonbinary")
        settings = ScreeningSettings.from_config(screening_raw, f"{where}.screening")
        return cls(
            experiment_name=name,
            description=" ".join(str(raw.get("description", "")).split()),
            source=source,
            extraction=str(raw["extraction"]),
            statuses=tuple(str(s) for s in statuses),
            encounter_types=None if types is None else tuple(str(t) for t in types),
            template=str(raw.get("template", DEFAULT_TEMPLATE)),
            llm={
                "client": as_choice(llm.get("client", "mock"), f"{where}.llm.client", CLIENTS),
                "mock_policy": policy,
                "model": str(llm.get("model", "deepseek-flash")),
                "temperature": as_number(llm.get("temperature", 0.0), f"{where}.llm.temperature", minimum=0.0),
                "max_tokens": int(as_number(llm.get("max_tokens", DEFAULT_MAX_TOKENS), f"{where}.llm.max_tokens", minimum=1)),
                "thinking": as_choice(llm.get("thinking", "disabled"), f"{where}.llm.thinking", ("disabled", "enabled")),
                "transport_retries": int(as_number(llm.get("transport_retries", 1), f"{where}.llm.transport_retries", minimum=0)),
            },
            budget={
                "cap_usd": as_number(budget.get("cap_usd", 0.0), f"{where}.budget.cap_usd", minimum=0.0),
                "ledger": str(budget.get("ledger", "spend_ledger.jsonl")),
            },
            identity=bool(identity.get("enabled", True)),
            screening=settings if screening_raw.get("enabled", True) else None,
            crowd_ages=tuple(int(a) for a in ages),
            crowd_genders=tuple(str(g) for g in genders),
            crowd_factors={str(name): tuple(str(level) for level in levels) for name, levels in factors.items()},
            rules=None if only is None else tuple(only),
            repair_one_brace=bool(reader.get("repair_one_brace", False)),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "experiment_name": self.experiment_name, "description": self.description, "source": self.source,
            "extraction": self.extraction, "statuses": list(self.statuses),
            "encounter_types": None if self.encounter_types is None else list(self.encounter_types),
            "template": self.template, "llm": dict(self.llm), "budget": dict(self.budget), "identity": {"enabled": self.identity},
            "screening": None if self.screening is None else {
                **self.screening.as_dict(), "ages": list(self.crowd_ages), "genders": list(self.crowd_genders),
                **({"factors": {name: list(levels) for name, levels in self.crowd_factors.items()}} if self.crowd_factors else {}),
            },
            # Issue #108: written only when set, so that an earlier config records what it did.
            **({"rules": list(self.rules)} if self.rules is not None else {}),
            **({"reader": {"repair_one_brace": True}} if self.repair_one_brace else {}),
        }


# --- what RF-11 kept -----------------------------------------------------------------------------


@dataclass(frozen=True)
class ExtractedRule:
    """One rule file of a rule extraction, read and checked against its manifest."""

    rule_id: str
    version: int
    encounter_type: str
    file: str  # under the package root
    sha256: str
    data: Mapping[str, Any]

    def identity(self, experiment: str) -> dict[str, Any]:
        """The ``extraction`` block: which RF-11 rule this is, and what RF-11 measured of it."""
        fidelity = (self.data.get("measured") or {}).get("fidelity") or {}
        return {
            "experiment": experiment, "rule_id": self.rule_id, "version": self.version, "file": self.file, "sha256": self.sha256,
            "status": self.data.get("status"), "category": self.data.get("category"),
            "extraction_stability": self.data.get("extraction_stability"), "target": (self.data.get("predict") or {}).get("target"),
            "held_out_accuracy": (fidelity.get("held_out") or {}).get("accuracy"), "baseline_accuracy": fidelity.get("baseline_accuracy"),
            "beats_baseline": fidelity.get("beats_baseline"),
        }


@dataclass(frozen=True)
class Extraction:
    folder: Path
    config: Mapping[str, Any]
    rules: list[ExtractedRule]

    @property
    def name(self) -> str:
        return str(self.config["experiment"]["experiment_name"])


def read_extraction(folder: Path | str, statuses: Sequence[str], encounter_types: Optional[Sequence[str]] = None) -> Extraction:
    """The rules a finished rule extraction stored with one of ``statuses``, each checked against the
    SHA-256 its store froze it with. A ``protected_attribute`` rule is never stored, so never read."""
    folder = Path(folder)
    for name in ("config.json", "summary.json"):
        if not (folder / name).is_file():
            raise ConfigError(f"{folder}: no {name}; is it a rule extraction's folder?")
    config = json.loads((folder / "config.json").read_text(encoding="utf-8"))
    if config.get("layer") != "rule_extraction":
        raise ConfigError(f"{folder}: layer {config.get('layer')!r}, not a rule extraction")
    summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    rules = []
    for entry in summary["types"]:
        encounter_type = entry["encounter_type"]
        if encounter_types is not None and encounter_type not in encounter_types:
            continue
        if entry.get("skipped"):
            continue
        if "rules" not in entry:
            raise ConfigError(f"{folder}: {encounter_type}'s extraction is not complete (not every run has a record)")
        store = folder / encounter_type / "extracted_rules"
        manifest = json.loads((store / MANIFEST_FILE).read_text(encoding="utf-8"))["files"]
        for listed in entry["rules"]:
            if listed["status"] not in statuses:
                continue
            path = store / listed["file"]
            digest = file_sha256(path)
            if listed["file"] not in manifest or manifest[listed["file"]]["sha256"] != digest:
                raise ConfigError(f"{path}: not the file its extraction store froze")
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if data.get("category") not in ("valid", "needs_communication"):
                raise ConfigError(f"{path}: category {data.get('category')!r}; only a valid or needs_communication rule is stored")
            rules.append(ExtractedRule(data["rule_id"], int(data["version"]), encounter_type, _relative(path), digest, data))
    return Extraction(folder, config, sorted(rules, key=lambda r: (r.encounter_type, r.rule_id)))


# --- the plan ------------------------------------------------------------------------------------


@dataclass
class Item:
    extracted: ExtractedRule
    rendered: RenderedTranslation


@dataclass
class Plan:
    extraction: Extraction
    items: list[Item]
    templates: Any
    preview: dict[str, Any]

    @property
    def rule_schema_version(self) -> int:
        """The rule format the translations are written in: the one the template's common template describes."""
        return rule_schema_version_of(self.templates.common)


def sends_per_attempt(config: TranslationConfig) -> int:
    return config.llm["transport_retries"] + 1


def preview_cost(config: TranslationConfig, items: Sequence[Item], templates: Any, prices: PriceTable) -> dict[str, Any]:
    """The most the translations could cost: every call's every attempt at its worst case (peak, no
    cache, the full reply allowance), each send as often as the transport may retry."""
    model, cap_tokens, sends = config.llm["model"], config.llm["max_tokens"], sends_per_attempt(config)
    retry_tokens = estimate_prompt_tokens([retry_message(templates, "x" * 200)])
    rows, total = [], 0.0
    for item in items:
        first = estimate_prompt_tokens(item.rendered.messages)
        attempts = [first, first + cap_tokens + retry_tokens][:MAX_ATTEMPTS]
        usd = sum(prices.worst_case(model, tokens, cap_tokens) for tokens in attempts) * sends
        rows.append({"rule_id": item.extracted.rule_id, "prompt_tokens_bound": first, "usd_bound": round(usd, 8),
                     "largest_call_bound_usd": round(prices.worst_case(model, attempts[-1], cap_tokens) * sends, 8)})
        total += usd
    return {
        "model": model, "price_date_checked": prices.date_checked, "max_tokens": cap_tokens, "attempts_per_rule": MAX_ATTEMPTS,
        "sends_per_attempt": sends, "rules": rows, "usd_total": round(total, 8), "cap_usd": config.budget["cap_usd"],
        "fits_the_cap": total <= config.budget["cap_usd"],
        "note": ("A bound, not an estimate: peak prices, nothing cached, every reply at the full allowance, every retry taken. "
                 "The budget guard checks each call against the cap before it is sent."),
    }


def plan(config: TranslationConfig) -> Plan:
    extraction = read_extraction(resolve_path(config.extraction), config.statuses, config.encounter_types)
    if config.rules is not None:
        missing = sorted(set(config.rules) - {rule.rule_id for rule in extraction.rules})
        if missing:
            raise ConfigError(f"rules {missing} are not among the extraction's {list(config.statuses)} rules")
        extraction = Extraction(extraction.folder, extraction.config, [rule for rule in extraction.rules if rule.rule_id in config.rules])
    templates = load_template(config.template)
    meanings = ExtractTemplate(extraction.config["template"]["key"])["columns"]
    descriptions = extraction.config["experiment"]["encounter_descriptions"]
    items = [Item(rule, render(templates, rule.data, meanings, descriptions[rule.encounter_type])) for rule in extraction.rules]
    return Plan(extraction, items, templates, preview_cost(config, items, templates, PriceTable.from_yaml()))


# --- the client ----------------------------------------------------------------------------------


def make_client(config: TranslationConfig, client_name: Optional[str] = None) -> LLMClient:
    """The mock, or the paid client behind a budget guard on this experiment's own calls."""
    name = client_name or config.llm["client"]
    if name == "mock":
        return MockClient(policy=MOCK_POLICIES[config.llm["mock_policy"]])
    if name != "deepseek":
        raise ConfigError(f"unknown client {name!r}; expected one of {list(CLIENTS)}")
    prices = PriceTable.from_yaml()
    prices.price_of(config.llm["model"])
    guard = BudgetGuard(SpendLedger(resolve_path(config.budget["ledger"])), config.budget["cap_usd"], prices, scope=config.experiment_name)
    return BudgetedClient(DeepSeekClient.from_env(max_retries=config.llm["transport_retries"]), guard)


# --- one translation -----------------------------------------------------------------------------


def accepts_structure(schema_version: int) -> Callable[[Any], bool]:
    """What a repaired reply must give (issue #108): null, or a rule the loader reads whole, in the rule
    format ``schema_version``: ``valid``, ``needs_communication`` or ``inconsistent``. Not a schema error
    or a format limit (a brace in the wrong place puts keys where they do not belong, such as a priority
    among the roles), nor a protected attribute (checked before the structure)."""
    def accept(translation: Any) -> bool:
        if translation.rule is None:
            return True
        category = V.validate_proposal(translation.rule, visible_for(schema_version), schema_version=schema_version).category
        return category in (V.VALID, V.NEEDS_COMMUNICATION, V.INCONSISTENT)
    return accept


def translate_once(
    config: TranslationConfig, extraction: Extraction, item: Item, templates: Any, client: LLMClient, schema_version: int = RULE_SCHEMA_VERSION,
) -> dict[str, Any]:
    """One rule's call (and a retry if its reply cannot be read). Returns its record; an aborted one says why.
    With ``config.repair_one_brace`` (issue #108) a reply one closing brace short is repaired, where
    exactly one placement loads, before anything is asked again."""
    rule = item.extracted
    messages = [dict(m) for m in item.rendered.messages]
    record: dict[str, Any] = {
        "translation_log_version": TRANSLATION_LOG_VERSION, "experiment": config.experiment_name,
        "extraction": rule.identity(extraction.name), "started_utc": _utc_now(), "template": item.rendered.template,
        "llm": {key: config.llm[key] for key in ("model", "temperature", "max_tokens", "thinking")},
        "messages": [dict(m) for m in messages], "attempts": [], "outcome": None, "error": None, "translation": None,
    }
    for attempt in range(1, MAX_ATTEMPTS + 1):
        request = LLMRequest(
            messages=messages, model=config.llm["model"], temperature=config.llm["temperature"], max_tokens=config.llm["max_tokens"],
            json_mode=False, thinking=config.llm["thinking"] == "enabled",
            metadata={"experiment": config.experiment_name, "rule_id": rule.rule_id, "attempt": attempt},
        )
        entry: dict[str, Any] = {"attempt": attempt, "messages_sent": len(messages)}
        if attempt > 1:
            entry["appended"] = messages[-2:]
        try:
            response = client.complete(request)
        except (BudgetExceededError, LLMTransientError) as exc:
            entry["error"] = f"budget: {exc}" if isinstance(exc, BudgetExceededError) else f"{type(exc).__name__}: {exc}"
            record["attempts"].append(entry)
            record.update(outcome=RUN_ABORTED, error=entry["error"])
            break
        entry.update({
            "raw": response.content, "model": response.model, "system_fingerprint": response.system_fingerprint,
            "response_id": response.response_id, "finish_reason": response.finish_reason, "usage": response.usage.as_dict(),
            "cost_usd": response.cost_usd, "price_tier": response.price_tier, "latency_s": response.latency_s,
            "started_utc": response.started_utc, "failed_sends": response.failed_attempts,
        })
        try:
            record["translation"] = parse_translation(response.content).as_dict()
            entry["parse_error"] = None
            record["attempts"].append(entry)
            break
        except TurnParseError as exc:
            entry["parse_error"] = str(exc)
            repaired = repair_one_brace(response.content, accepts_structure(schema_version)) if config.repair_one_brace else None
            if repaired is not None:
                entry["repaired"] = repaired.as_dict()
                record["translation"] = repaired.translation.as_dict()
                record["attempts"].append(entry)
                break
            record["attempts"].append(entry)
            if attempt < MAX_ATTEMPTS:
                messages = [*messages, {"role": "assistant", "content": response.content or ""}, retry_message(templates, str(exc))]
    if record["outcome"] is None:
        record["outcome"] = RUN_COMPLETED if record["translation"] is not None else RUN_UNREADABLE
    record["totals"] = {
        "calls": sum(1 for a in record["attempts"] if "raw" in a or a.get("error")),
        "cost_usd": round(math.fsum(a.get("cost_usd") or 0.0 for a in record["attempts"]), 10),
        "prompt_tokens": sum((a.get("usage") or {}).get("prompt_tokens", 0) for a in record["attempts"]),
        "completion_tokens": sum((a.get("usage") or {}).get("completion_tokens", 0) for a in record["attempts"]),
        "cache_hit_tokens": sum((a.get("usage") or {}).get("prompt_cache_hit_tokens", 0) for a in record["attempts"]),
    }
    record["ended_utc"] = _utc_now()
    return record


def assess(extracted: ExtractedRule, record: Mapping[str, Any], schema_version: int = RULE_SCHEMA_VERSION) -> dict[str, Any]:
    """A translation's category (``negsim.rulegen.validate``, in the rule format ``schema_version``),
    and what was lost: the translator's list and the mechanical checks of the extracted rule's
    factors and words."""
    data = extracted.data
    out: dict[str, Any] = {
        "extracted_rule_id": extracted.rule_id, "encounter_type": extracted.encounter_type, "rule": data.get("rule"),
        "extracted_status": data.get("status"), "extracted_category": data.get("category"),
        "extraction_stability": data.get("extraction_stability"), "target": (data.get("predict") or {}).get("target"),
        "needs_communication": data.get("category") == "needs_communication",
        "factor_losses": factor_losses(data.get("factors_used"), schema_version),
        "action_flags": action_flags([data.get("rule"), data.get("action")], schema_version),
        "outcome": record["outcome"], "category": None, "message": None, "lost": [], "note": None, "review_flags": [],
    }
    translation = record.get("translation")
    if translation is None:
        return out
    out.update(lost=translation["lost"], note=translation["note"])
    if translation["rule"] is None:
        out.update(category=NOT_EXPRESSIBLE, message=f"the translator said no part of the rule can be written in format {schema_version}")
        return out
    texts = [translation["note"], *(item["part"] for item in translation["lost"])]
    checked = V.validate_proposal(translation["rule"], visible_for(schema_version), texts, schema_version=schema_version)
    out.update(category=checked.category, message=checked.message, loader_category=checked.loader_category,
               fields=checked.fields, review_flags=checked.review_flags, ignored_metadata=checked.ignored_metadata)
    return out


# --- writing -------------------------------------------------------------------------------------


def rule_id_for(extracted: ExtractedRule) -> str:
    """``ext_`` and the extracted rule's id without its ``x_``: the two name each other."""
    return "ext_" + extracted.rule_id.removeprefix("x_")


def build_rule(
    config: TranslationConfig, extraction: Extraction, extracted: ExtractedRule, record: Mapping[str, Any], runnable: bool,
    schema_version: int = RULE_SCHEMA_VERSION,
) -> dict[str, Any]:
    """The rule file (format ``schema_version``) of a valid translation: the translator's body, and the
    code's own metadata (never the model's). The extracted rule's references become its
    ``validation_evidence``, each ``unchecked`` (RF-14 checks them)."""
    body = record["translation"]["rule"]
    models = sorted({a.get("model") for a in record["attempts"] if a.get("model")})
    step = "(RF-12, issue #67)" if schema_version == 3 else "(RF-31, issue #108)"
    notes = (f"Extracted by a language model from Step 1's resolved sessions (RF-11) and translated into rule format {schema_version} "
             f"{step}; its id and provenance are the code's, never a model's. A candidate, not checked against "
             "evidence about people (RF-14).")
    if not runnable:
        notes += (" NOT RUNNABLE IN ORCA: the extracted rule needs communication (it held only when a signal or words were "
                  "used, D9), and nobody signals or talks in ORCA. Not replayed and not screened.")
    rule: dict[str, Any] = {"schema_version": schema_version, "rule_id": rule_id_for(extracted), "version": 1, "status": "candidate"}
    if extracted.data.get("rule"):
        rule["description"] = " ".join(str(extracted.data["rule"]).split())
    if isinstance(body.get("intent"), str):
        rule["intent"] = body["intent"]
    rule["provenance"] = {
        "source_type": "extracted",
        "source_ref": (f"extracted rule {extracted.rule_id} v{extracted.version} of rule-extraction experiment {extraction.name} "
                       f"({extracted.file}, sha256 {extracted.sha256}), translated by rule-translation experiment "
                       f"{config.experiment_name} ({TRANSLATIONS_DIR}/{extracted.rule_id}.json)"),
        "created_at": record["ended_utc"][:10],
        "author": f"negsim.translation, from {', '.join(models) or '?'} with prompt template {record['template']['key']}",
        "notes": notes,
        "validation_evidence": [
            {"from": "extraction", "citation": ref.get("citation"), "locator": ref.get("locator"), "source_kind": ref.get("kind"),
             "claim": ref.get("claim"), "status": "unchecked"}
            for ref in extracted.data.get("references") or []
        ],
    }
    for key in ("encounter", "when", "roles", "directive", "priority", "expiry"):
        if key in body:
            rule[key] = body[key]
    return rule


def staging(experiment_dir: Path, schema_version: int = RULE_SCHEMA_VERSION) -> StagingDatabase:
    """The experiment's staging database, laid out as the writer's, with its own note of what it holds."""
    database = StagingDatabase(experiment_dir / STAGING_DIR)
    if not database.manifest_path.is_file():
        issue = "issue #67, RF-12" if schema_version == 3 else "issue #108, RF-31"
        _write_json(database.manifest_path, {
            "about": (f"A staging rule database of a rule-translation experiment ({issue}): extracted rules translated "
                      f"into rule format {schema_version}, status candidate, written by negsim.translation only. SHA-256 of every file, line endings "
                      "normalised to LF; a file is frozen once listed, and a change is the next version. Nothing here is in "
                      "rule_db/ unless it is promoted, with a reason."),
            "files": {},
        })
    database.create()
    return database


# --- the experiment ------------------------------------------------------------------------------


@dataclass
class TranslationResult:
    experiment_dir: Path
    status: str = STATUS_COMPLETED
    executed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    aborted: Optional[str] = None
    summary: dict[str, Any] = field(default_factory=dict)


def _set_aside(path: Path) -> Path:
    n = 1
    while (target := path.with_name(f"{path.stem}.aborted{n}.json")).exists():
        n += 1
    path.rename(target)
    return target


def _comparable(described: Mapping[str, Any]) -> dict[str, Any]:
    """What must not change once a translation has a record: everything but when, the commit, the
    budget, and what is done after the calls (the identity check and the screening)."""
    out = {key: value for key, value in described.items() if key not in ("created_utc", "git")}
    out["experiment"] = {key: value for key, value in (out.get("experiment") or {}).items() if key not in ("budget", "source", "identity", "screening")}
    return out


def evaluate(
    config: TranslationConfig, plan_: Plan, experiment_dir: Path, database: StagingDatabase, entry: dict[str, Any],
    extracted: ExtractedRule, checker: Optional[I.IdentityCheck], crowd: Optional[CrowdScreen], git: Mapping[str, Any],
    report: Callable[[str], None],
) -> None:
    """Replay a written rule on its Step 1 sessions and screen it in a crowd, unless its newest
    staged version has the results already; store them as its next version."""
    latest = database.latest(entry["staged_rule_id"])
    assert latest is not None
    if latest.version > 1 and latest.screening:
        entry["screening_version"] = latest.version
        entry["screening"] = [dict(e) for e in latest.screening]
        return
    rule = latest
    entries = []
    if checker is not None:
        sessions = list(extracted.data["provenance"]["sessions_used"])
        rows = checker.run(rule, database.root, sessions)
        folder = experiment_dir / IDENTITY_DIR
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{rule.rule_id}.csv").write_text(I.as_csv(rows), encoding="utf-8", newline="\n")
        summary = I.summarise(rows)
        reasons = [] if not summary["plain_not_the_recorded_run"] else [
            f"plain ORCA was not the run the session recorded in {summary['plain_not_the_recorded_run']} session(s): left out of the shares"]
        entries.append({
            "kind": "replay", "experiment": config.experiment_name, "scenario": f"step1_sessions:{extracted.encounter_type}",
            "baseline": "plain_orca", "case_id": None, "seeds": sorted({int(row["seed"]) for row in rows}), "screened_utc": _utc_now(),
            "verdict": "recorded", "reasons": reasons,
            "results": {"identity": summary, "rows": f"{IDENTITY_DIR}/{rule.rule_id}.csv", "sessions_from": extracted.rule_id},
        })
        report(f"  {rule.rule_id}: identity {summary['all']['rule_reproduces']} (plain ORCA {summary['all']['plain_reproduces']}), "
               f"matched {summary['rule_matched']} of {summary['trusted']}")
    if crowd is not None:
        screened = crowd.screen(rule, database.root, visible_for(rule.schema_version))
        entries.append(screened)
        report(f"  {rule.rule_id}: crowd {screened['verdict']}")
    if entries:
        newer = with_screening(rule.written, entries)
        database.write(newer, "with the identity check and crowd screening (RF-12)" if rule.schema_version == 3 else "with the identity check and crowd screening (RF-31)")
        entry["screening_version"] = newer["version"]
        entry["screening"] = entries


def run_translation(
    config: TranslationConfig,
    client: Optional[LLMClient] = None,
    client_name: Optional[str] = None,
    out_root: Optional[Path | str] = None,
    confirm: bool = False,
    limit: Optional[int] = None,
    report: Callable[[str], None] = print,
    git: Optional[Mapping[str, Any]] = None,
) -> TranslationResult:
    """Run (or resume) the translation. ``limit`` makes at most N translations that have no record yet."""
    name = client.name if client is not None else (client_name or config.llm["client"])
    if name not in CLIENTS:
        raise ConfigError(f"unknown client {name!r}; expected one of {list(CLIENTS)}")
    paid = name != "mock"
    experiment_dir = Path(out_root if out_root is not None else (RUNS_DIR if paid else MOCK_RUNS_DIR)) / config.experiment_name
    result = TranslationResult(experiment_dir)
    if git is None:
        from ..experiment.batch import git_state

        git = git_state()
    plan_ = plan(config)
    preview = plan_.preview
    experiment_dir.mkdir(parents=True, exist_ok=True)
    described = {
        "translation_log_version": TRANSLATION_LOG_VERSION, "layer": LAYER, "experiment": config.as_dict(), "client_name": name,
        "software": {"negsim": __version__}, "template": plan_.templates.identity(),
        "extraction": {"folder": _relative(plan_.extraction.folder), "experiment": plan_.extraction.name,
                       "rules": [{"rule_id": r.rule_id, "file": r.file, "sha256": r.sha256} for r in plan_.extraction.rules]},
    }
    config_path = experiment_dir / "config.json"
    created = _utc_now()
    if config_path.is_file():
        before = json.loads(config_path.read_text(encoding="utf-8"))
        created = before.get("created_utc", created)
        if _comparable(before) != _comparable(described) and any((experiment_dir / TRANSLATIONS_DIR).glob("*.json")):
            raise ConfigError(f"{experiment_dir}: it holds translations made with another config, client or extraction; give the config a new experiment_name")
    _write_json(config_path, {**described, "created_utc": created, "git": dict(git)})
    _write_json(experiment_dir / "preview.json", preview)
    report(f"{config.experiment_name}: {len(plan_.items)} rule(s) to translate; worst-case cost USD {preview['usd_total']:.6f}; "
           f"cap USD {config.budget['cap_usd']:.2f}")

    def invocation(status: str, client_described: Mapping[str, Any]) -> None:
        _append_jsonl(experiment_dir / "invocations.jsonl", {
            "utc": _utc_now(), "git": dict(git), "client": dict(client_described), "confirm": confirm, "limit": limit,
            "status": status, "executed": list(result.executed), "aborted": result.aborted, "preview_usd": preview["usd_total"],
        })

    if paid:
        if set(config.statuses) != {"candidate"}:
            invocation("refused_statuses", {"client": name})
            raise ConfigError("a paid translation translates only candidate rules (RF-11 passes no unstable rule to RF-12)")
        if not confirm:
            result.status = STATUS_AWAITING
            invocation(STATUS_AWAITING, {"client": name})
            report("  a paid client, not confirmed: nothing was sent. Read the preview, then run again with --confirm.")
            return result
    if client is None:
        client = make_client(config, name)

    budget = math.inf if limit is None else max(0, limit)
    records: list[Optional[dict[str, Any]]] = []
    for item in plan_.items:
        path = experiment_dir / TRANSLATIONS_DIR / f"{item.extracted.rule_id}.json"
        previous = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
        if previous is not None and previous["outcome"] != RUN_ABORTED:
            if previous["messages"] != item.rendered.messages:
                raise ConfigError(f"{path}: its messages are not what this config renders now; the inputs changed under the experiment")
            records.append(previous)
            result.skipped.append(item.extracted.rule_id)
            continue
        if result.aborted is not None or len(result.executed) >= budget:
            records.append(None)
            continue
        if previous is not None:
            _set_aside(path)
        record = translate_once(config, plan_.extraction, item, plan_.templates, client, plan_.rule_schema_version)
        _write_json(path, record)
        result.executed.append(item.extracted.rule_id)
        report(f"  {item.extracted.rule_id}: {record['outcome']}, USD {record['totals']['cost_usd']:.6f}")
        if record["outcome"] == RUN_ABORTED:
            result.aborted = record["error"]
            report(f"  stopped: {record['error']}")
            records.append(None)
            continue
        records.append(record)

    version = plan_.rule_schema_version
    database = staging(experiment_dir, version)
    checker = None
    if config.identity:
        sources = sorted({source for r in plan_.extraction.rules for source in r.data["provenance"]["sources"]})
        checker = I.IdentityCheck(I.SessionSource([resolve_path(source) for source in sources]))
    crowd = None
    if config.screening is not None:
        crowd = CrowdScreen(config.screening, experiment_dir / SCREENING_DIR, config.experiment_name, git,
                            mixed_population(crowd_size(config.screening), config.crowd_ages, config.crowd_genders, config.crowd_factors), where=SCREENING_DIR)
    rules_out = []
    for item, record in zip(plan_.items, records):
        if record is None:
            rules_out.append({"extracted_rule_id": item.extracted.rule_id, "outcome": "not_run"})
            continue
        entry = assess(item.extracted, record, version)
        entry["extraction"] = record["extraction"]
        entry["cost_usd"] = record["totals"]["cost_usd"]
        entry["runnable_in_orca"] = entry["category"] == V.VALID and not entry["needs_communication"]
        if entry["category"] == V.VALID:
            rule = build_rule(config, plan_.extraction, item.extracted, record, entry["runnable_in_orca"], version)
            name_, _ = database.write(rule, f"translated from {item.extracted.rule_id} ({'RF-12' if version == 3 else 'RF-31'})")
            entry.update(staged_rule_id=rule["rule_id"], staged_file=f"{STAGING_DIR}/{name_}", translated_rule=record["translation"]["rule"])
            if entry["runnable_in_orca"]:
                evaluate(config, plan_, experiment_dir, database, entry, item.extracted, checker, crowd, git, report)
        rules_out.append(entry)

    done = [entry for entry in rules_out if entry.get("outcome") != "not_run"]
    complete = len(done) == len(plan_.items)
    result.status = STATUS_COMPLETED if complete and result.aborted is None else STATUS_PARTIAL
    cost = math.fsum(json.loads(path.read_text(encoding="utf-8"))["totals"]["cost_usd"]
                     for path in sorted((experiment_dir / TRANSLATIONS_DIR).glob("*.json")))
    summary = {
        "experiment": config.experiment_name, "status": result.status, "client": name,
        **({"rule_schema_version": version} if version != RULE_SCHEMA_VERSION else {}),
        "extraction": {"folder": _relative(plan_.extraction.folder), "experiment": plan_.extraction.name, "statuses": list(config.statuses)},
        "rules": rules_out,
        "counts": {
            "rules": len(plan_.items), "translated": len(done),
            "outcomes": dict(Counter(entry["outcome"] for entry in done)),
            "categories": dict(Counter(entry["category"] for entry in done if entry["category"] is not None)),
            "needs_communication_extracted": sum(entry["needs_communication"] for entry in done),
            "needs_communication_written_not_runnable": sum(entry["needs_communication"] and entry["category"] == V.VALID for entry in done),
            "written": sum("staged_rule_id" in entry for entry in done),
            "runnable_in_orca": sum(bool(entry.get("runnable_in_orca")) for entry in done),
        },
        "lost": counted(done),
        "cost": {"preview_usd": preview["usd_total"], "actual_usd": round(cost, 10), "cap_usd": config.budget["cap_usd"]},
    }
    _write_json(experiment_dir / "summary.json", summary)
    (experiment_dir / "report.md").write_text(report_markdown(config, summary), encoding="utf-8", newline="\n")
    result.summary = summary
    invocation(result.status, client.describe())
    return result


# --- the report ----------------------------------------------------------------------------------


def _share(value: Optional[float]) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def _identity(entry: Mapping[str, Any]) -> str:
    for screened in entry.get("screening") or []:
        if screened["kind"] == "replay":
            found = screened["results"]["identity"]
            every, matched = found["all"], found["matched"]
            return (f"{_share(every['rule_reproduces'])} against plain ORCA {_share(every['plain_reproduces'])} "
                    f"(n {every['n']}; the rule matched {found['rule_matched']}, reproducing {_share(matched['rule_reproduces'])} of those)")
    return "not run"


def _crowd(entry: Mapping[str, Any]) -> str:
    for screened in entry.get("screening") or []:
        if screened["kind"] == "crowd":
            return screened["verdict"] + (f" ({'; '.join(screened['reasons'])})" if screened["reasons"] else "")
    return "not run"


def report_markdown(config: TranslationConfig, summary: Mapping[str, Any]) -> str:
    counts = summary["counts"]
    version = summary.get("rule_schema_version", RULE_SCHEMA_VERSION)
    lines = [f"# Rule translation: {config.experiment_name}", "", config.description, "",
             f"Status: {summary['status']}; client {summary['client']}; cost USD {summary['cost']['actual_usd']:.6f} "
             f"(worst case USD {summary['cost']['preview_usd']:.6f}, cap USD {summary['cost']['cap_usd']:.2f}).", "",
             f"From `{summary['extraction']['folder']}` ({', '.join(summary['extraction']['statuses'])} rules): {counts['rules']} rule(s), "
             f"{counts['translated']} translated; categories {counts['categories']}; written {counts['written']}; "
             f"runnable in ORCA {counts['runnable_in_orca']}; extracted as needing communication {counts['needs_communication_extracted']} "
             f"(written but not runnable: {counts['needs_communication_written_not_runnable']}).", "",
             f"A `format_limit` or `not_expressible` translation is a finding about rule format {version}, not about the model.", "",
             f"| Extracted rule | Category | Lost (translator) | Factors format {version} cannot read | Action words with no directive | Identity check | Crowd |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for entry in summary["rules"]:
        if entry.get("outcome") == "not_run":
            lines.append(f"| `{entry['extracted_rule_id']}` | not run | | | | | |")
            continue
        lost = "; ".join(f"{item['kind']} ({item['how'] or '?'}): {item['part']}" for item in entry["lost"]) or "none"
        unreadable = ", ".join(f"{f['column']} ({f['status']})" for f in entry["factor_losses"] if f["status"] in ("unobservable", "no_field", "communication", "protected")) or "none"
        category = entry["category"] or entry["outcome"]
        if entry["needs_communication"]:
            category += " (extracted as needing communication: not runnable in ORCA)"
        lines.append(f"| `{entry['extracted_rule_id']}`: {entry['rule']} | {category} | {lost} | {unreadable} | "
                     f"{', '.join(entry['action_flags']) or 'none'} | {_identity(entry)} | {_crowd(entry)} |")
    lost = summary["lost"]
    lines += ["", f"Across the {lost['rules']} translated rule(s), rules with each: factor status {lost['factor_status']}; "
              f"action words {lost['action_flags']}; kinds the translator said it lost {lost['lost_kinds']}.", "",
              "The identity check runs each runnable rule alone in ORCA on the Step 1 sessions it was extracted from, and gives the "
              "share whose who-passed-first and both passing sides match what the agents' plans did in `plan_only`, beside plain "
              "ORCA on the same seeds. References are copied from the extraction, unchecked (RF-14).", ""]
    return "\n".join(lines)


# --- the command line ----------------------------------------------------------------------------


def print_plan(config: TranslationConfig, out: Callable[[str], None] = print) -> Plan:
    plan_ = plan(config)
    preview = plan_.preview
    out(f"{config.experiment_name}: rule translation of {len(plan_.items)} rule(s) from {plan_.extraction.name} "
        f"({', '.join(config.statuses)}), template {config.template}, model {config.llm['model']}")
    for item in plan_.items:
        chars = sum(len(m["content"]) for m in item.rendered.messages)
        out(f"  {item.extracted.rule_id} ({item.extracted.data.get('category')}, {item.extracted.data.get('extraction_stability')}): {chars} characters")
    out(f"  worst-case cost USD {preview['usd_total']:.6f} ({preview['attempts_per_rule']} attempt(s) per rule, "
        f"{preview['sends_per_attempt']} send(s) each); cap USD {preview['cap_usd']:.2f}")
    if not preview["fits_the_cap"]:
        out("  the worst case exceeds the cap: the budget guard refuses any call that could take this experiment's recorded "
            "spend past the cap, so a translation may be aborted (a rerun redoes it)")
    return plan_


def cli_run(args: argparse.Namespace) -> int:
    """What ``run_experiment.py`` does with a config that says ``layer: rule_translation``."""
    try:
        config = TranslationConfig.load(args.config)
        if args.plan:
            print_plan(config)
            return 0
        result = run_translation(config, client_name=args.client, out_root=args.out, confirm=args.confirm, limit=args.limit)
    except (ConfigError, LLMFatalError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"logs: {result.experiment_dir}")
    if result.status == STATUS_AWAITING:
        return 4
    print(f"{result.status}: {len(result.executed)} translation(s) made, {len(result.skipped)} already done; "
          f"actual cost USD {result.summary['cost']['actual_usd']:.6f}")
    if result.aborted:
        print(f"stopped early: {result.aborted}", file=sys.stderr)
        return 3
    return 0
