"""A rule-extraction experiment (issue #66, RF-11; ``docs/rule-extraction.md``): Step 2 of track #55.

    python run_experiment.py configs/extraction/round1_head_on.yaml --plan
    python run_experiment.py configs/extraction/round1_head_on.yaml                      # mock, runs_mock/
    python run_experiment.py configs/extraction/round1_head_on.yaml --client deepseek    # preview only
    python run_experiment.py configs/extraction/round1_head_on.yaml --client deepseek --confirm

For each encounter type of the sources that passed its resolution gate: the held-out split, the
tables, then ``runs`` extractions (three), each with its own seeded sample of sessions shown in
full; each rule checked, scored on the held-out rows, matched across the runs, and stored with
provenance. A type that failed its gate is skipped, and the report says so.

**Money.** With a paid client nothing is sent without ``--confirm``; every call goes through the
budget guard on this experiment's own calls (``budget.cap_usd``), which refuses a call whose worst
case could take the recorded spend past the cap. A paid run needs the gate (``gate.require``), and
the ethics sign-offs of the factors its table shows (``negsim.ethics``): the table holds each
person's ethnicity and perceived attractiveness, which no rule may read but the extractor sees.

**Records.** Each run's record (``<type>/runs/run_<k>.json``: the exact messages, every raw reply,
tokens, cost, the rules as read and checked) is written once, when the run ends, and never
rewritten; running the experiment again reuses it, and redoes only a run that was aborted (set
aside as ``run_<k>.aborted<n>.json``). The tables and the split are rebuilt and must come out the
same.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from .. import __version__, ethics
from ..configutil import PACKAGE_ROOT, ConfigError, as_choice, as_number, check_keys, load_yaml, resolve_path
from ..llm.base import LLMClient, LLMFatalError, LLMRequest, LLMTransientError
from ..llm.budget import BudgetedClient, BudgetExceededError, BudgetGuard, SpendLedger, estimate_prompt_tokens
from ..llm.deepseek import DeepSeekClient
from ..llm.mock import MockClient
from ..llm.pricing import PriceTable
from ..rules.database import file_sha256
from . import rules as R
from .mock import POLICIES as MOCK_POLICIES
from .prompt import DESIGN_FACTORS, ExtractTemplate, RenderedExtraction, render, retry_message, sample_sessions
from .table import COLUMNS, Tables, as_csv, build_tables, factor_margins, failed_table, gate, pooled_sessions, read_source

LAYER = "rule_extraction"
SCHEMA_VERSION = 1
EXTRACTION_LOG_VERSION = 1
CLIENTS = ("mock", "deepseek")
DEFAULT_TEMPLATE = "extract_v1"
RUNS_DIR, MOCK_RUNS_DIR = PACKAGE_ROOT / "runs", PACKAGE_ROOT / "runs_mock"
#: Most attempts at one extraction: a first reply, and one retry if it cannot be read.
MAX_ATTEMPTS = 2
SAMPLE_MIN, SAMPLE_MAX = 10, 20  # the issue's 10 to 20 sessions shown in full
#: The reply cap when a config gives none. RF-11's round 1 ran at 4,000 and one reply was cut off
#: there (the others used 3,300 to 3,993); twice that, by the user's decision of 2026-10-26.
DEFAULT_MAX_TOKENS = 8000

RUN_COMPLETED, RUN_UNREADABLE, RUN_ABORTED = "completed", "unreadable", "aborted"
STATUS_COMPLETED, STATUS_PARTIAL, STATUS_AWAITING = "completed", "partial", "awaiting_confirmation"
STORE_DIR = "extracted_rules"


def is_extraction_config(raw: Any) -> bool:
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


# --- the config ----------------------------------------------------------------------------------


@dataclass(frozen=True)
class ExtractionConfig:
    experiment_name: str
    description: str
    source: str
    sources: tuple[str, ...]
    encounter_types: Optional[tuple[str, ...]]
    encounter_descriptions: Mapping[str, str]
    gate_required: bool
    held_out_share: float
    held_out_seed: int
    run_seeds: tuple[int, ...]
    sample_size: int
    agreement_min: float
    min_runs: int
    template: str
    llm: Mapping[str, Any]
    budget: Mapping[str, Any]

    @classmethod
    def load(cls, path: Path | str) -> "ExtractionConfig":
        return cls.from_raw(load_yaml(resolve_path(path)), str(path).replace("\\", "/"))

    @classmethod
    def from_raw(cls, raw: Any, source: str = "<config>") -> "ExtractionConfig":
        where = f"rule-extraction config {source}"
        check_keys(raw, where, ("layer", "experiment_name", "sources", "encounter_descriptions", "llm"),
                   ("schema_version", "description", "encounter_types", "gate", "held_out", "runs", "sample", "matching",
                    "template", "budget"))
        if raw["layer"] != LAYER:
            raise ConfigError(f"{where}.layer: expected {LAYER!r}")
        if raw.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
            raise ConfigError(f"{where}: schema_version {raw['schema_version']!r} is not supported")
        name = str(raw["experiment_name"])
        if not name or not all(ch.isalnum() or ch in "_-" for ch in name):
            raise ConfigError(f"{where}.experiment_name: letters, digits, '_' and '-' only, got {name!r}")
        sources = raw["sources"]
        if not isinstance(sources, list) or not sources or len(set(sources)) != len(sources):
            raise ConfigError(f"{where}.sources: a list of distinct resolution experiment folders")
        types = raw.get("encounter_types")
        if types is not None and (not isinstance(types, list) or not types):
            raise ConfigError(f"{where}.encounter_types: a list of encounter types, or leave it out for every type")
        descriptions = raw["encounter_descriptions"]
        if not isinstance(descriptions, Mapping) or not descriptions or not all(isinstance(v, str) and v.strip() for v in descriptions.values()):
            raise ConfigError(f"{where}.encounter_descriptions: one line of text per encounter type")
        gate_ = check_keys(raw.get("gate") or {}, f"{where}.gate", (), ("require",))
        held = check_keys(raw.get("held_out") or {}, f"{where}.held_out", (), ("share", "seed"))
        runs = check_keys(raw.get("runs") or {}, f"{where}.runs", ("seeds",), ())
        seeds = runs["seeds"]
        if not isinstance(seeds, list) or not seeds or len(set(seeds)) != len(seeds) or not all(isinstance(s, int) for s in seeds):
            raise ConfigError(f"{where}.runs.seeds: a list of distinct integers, one per extraction run")
        sample = check_keys(raw.get("sample") or {}, f"{where}.sample", (), ("size",))
        size = int(as_number(sample.get("size", 15), f"{where}.sample.size", minimum=SAMPLE_MIN))
        if size > SAMPLE_MAX:
            raise ConfigError(f"{where}.sample.size: {SAMPLE_MIN} to {SAMPLE_MAX} sessions (issue #66), got {size}")
        matching = check_keys(raw.get("matching") or {}, f"{where}.matching", (), ("agreement_min", "min_runs"))
        agreement = as_number(matching.get("agreement_min", 0.95), f"{where}.matching.agreement_min", minimum=0.0)
        if agreement > 1.0:
            raise ConfigError(f"{where}.matching.agreement_min: a share, 0 to 1")
        min_runs = int(as_number(matching.get("min_runs", 2), f"{where}.matching.min_runs", minimum=1))
        if min_runs > len(seeds):
            raise ConfigError(f"{where}.matching.min_runs: at most the number of runs ({len(seeds)})")
        llm = check_keys(raw["llm"], f"{where}.llm", (), ("client", "mock_policy", "model", "temperature", "max_tokens", "thinking", "transport_retries"))
        policy = str(llm.get("mock_policy", "extract_rehearsal_v1"))
        if policy not in MOCK_POLICIES:
            raise ConfigError(f"{where}.llm.mock_policy: one of {sorted(MOCK_POLICIES)}, got {policy!r}")
        budget = check_keys(raw.get("budget") or {}, f"{where}.budget", (), ("cap_usd", "ledger"))
        return cls(
            experiment_name=name,
            description=" ".join(str(raw.get("description", "")).split()),
            source=source,
            sources=tuple(str(s) for s in sources),
            encounter_types=None if types is None else tuple(str(t) for t in types),
            encounter_descriptions={str(k): " ".join(str(v).split()) for k, v in descriptions.items()},
            gate_required=bool(gate_.get("require", True)),
            held_out_share=as_number(held.get("share", 0.25), f"{where}.held_out.share", minimum=0.0),
            held_out_seed=int(as_number(held.get("seed", 66), f"{where}.held_out.seed")),
            run_seeds=tuple(int(s) for s in seeds),
            sample_size=size,
            agreement_min=agreement,
            min_runs=min_runs,
            template=str(raw.get("template", DEFAULT_TEMPLATE)),
            llm={
                "client": as_choice(llm.get("client", "mock"), f"{where}.llm.client", CLIENTS),
                "mock_policy": policy,
                "model": str(llm.get("model", "deepseek-flash")),
                "temperature": as_number(llm.get("temperature", 1.0), f"{where}.llm.temperature", minimum=0.0),
                "max_tokens": int(as_number(llm.get("max_tokens", DEFAULT_MAX_TOKENS), f"{where}.llm.max_tokens", minimum=1)),
                "thinking": as_choice(llm.get("thinking", "disabled"), f"{where}.llm.thinking", ("disabled", "enabled")),
                "transport_retries": int(as_number(llm.get("transport_retries", 1), f"{where}.llm.transport_retries", minimum=0)),
            },
            budget={
                "cap_usd": as_number(budget.get("cap_usd", 0.05), f"{where}.budget.cap_usd", minimum=0.0),
                "ledger": str(budget.get("ledger", "spend_ledger.jsonl")),
            },
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "experiment_name": self.experiment_name, "description": self.description, "source": self.source,
            "sources": list(self.sources), "encounter_types": None if self.encounter_types is None else list(self.encounter_types),
            "encounter_descriptions": dict(self.encounter_descriptions), "gate": {"require": self.gate_required},
            "held_out": {"share": self.held_out_share, "seed": self.held_out_seed}, "runs": {"seeds": list(self.run_seeds)},
            "sample": {"size": self.sample_size}, "matching": {"agreement_min": self.agreement_min, "min_runs": self.min_runs},
            "template": self.template, "llm": dict(self.llm), "budget": dict(self.budget),
        }


# --- the plan: what would be sent ----------------------------------------------------------------


@dataclass
class TypePlan:
    """One encounter type: its gate, and if it passed, its tables and each run's messages."""

    encounter_type: str
    gate: dict[str, Any]
    tables: Optional[Tables] = None
    rendered: list[RenderedExtraction] = field(default_factory=list)
    skipped: Optional[str] = None


@dataclass
class Plan:
    sources: list[Any]
    types: list[TypePlan]
    template: ExtractTemplate
    preview: dict[str, Any]


def sends_per_attempt(config: ExtractionConfig, paid: bool = True) -> int:
    return config.llm["transport_retries"] + 1 if paid else 1


def preview_cost(config: ExtractionConfig, types: Sequence[TypePlan], template: ExtractTemplate, prices: PriceTable) -> dict[str, Any]:
    """The most the extraction could cost: every run's every attempt at its worst case (peak, no
    cache, the full reply allowance), each send of it as often as the transport may retry. A
    retry's prompt is the first prompt, a reply of the full allowance, and the retry message."""
    model, cap_tokens = config.llm["model"], config.llm["max_tokens"]
    sends = sends_per_attempt(config)
    rows, total = [], 0.0
    retry_tokens = estimate_prompt_tokens([retry_message(template, "x" * 200)])
    for plan_ in types:
        for index, rendered in enumerate(plan_.rendered):
            first = estimate_prompt_tokens(rendered.messages)
            attempts = [first, first + cap_tokens + retry_tokens][:MAX_ATTEMPTS]
            usd = sum(prices.worst_case(model, tokens, cap_tokens) for tokens in attempts) * sends
            per_call = prices.worst_case(model, attempts[-1], cap_tokens) * sends
            rows.append({"encounter_type": plan_.encounter_type, "run": index + 1, "prompt_tokens_bound": first,
                         "usd_bound": round(usd, 8), "largest_call_bound_usd": round(per_call, 8)})
            total += usd
    return {
        "model": model, "price_date_checked": prices.date_checked, "max_tokens": cap_tokens,
        "attempts_per_run": MAX_ATTEMPTS, "sends_per_attempt": sends, "runs": rows,
        "usd_total": round(total, 8), "cap_usd": config.budget["cap_usd"], "fits_the_cap": total <= config.budget["cap_usd"],
        "note": ("A bound, not an estimate: peak prices, nothing cached, every reply at the full allowance, every retry taken. "
                 "The budget guard checks each call against the cap before it is sent."),
    }


def plan(config: ExtractionConfig) -> Plan:
    sources = [read_source(resolve_path(folder)) for folder in config.sources]
    sessions = pooled_sessions(sources)
    found = sorted({session.encounter_type for session in sessions})
    wanted = list(config.encounter_types) if config.encounter_types is not None else found
    unknown = [t for t in wanted if t not in found]
    if unknown:
        raise ConfigError(f"encounter_types {unknown} are in none of the sources (found: {found})")
    template = ExtractTemplate(config.template)
    types = []
    for encounter_type in wanted:
        if encounter_type not in config.encounter_descriptions:
            raise ConfigError(f"encounter_descriptions: no line for {encounter_type!r}")
        result = gate(sources, sessions, encounter_type, require=config.gate_required)
        plan_ = TypePlan(encounter_type, result)
        if not result["passes"] and result["status"] == "no_gate_fixed":
            plan_.skipped = (f"{encounter_type}: no gate was fixed, and none of its {result['n']} design sessions resolved in "
                             "plan_only: there is nothing to extract")
        elif not result["passes"]:
            plan_.skipped = (f"{encounter_type} failed its resolution gate ({result['resolved']} of {result['n']} design sessions "
                             f"resolved in plan_only, threshold {result['threshold']}): no rule is extracted from it")
        else:
            tables = build_tables(sessions, sources, encounter_type, config.held_out_share, config.held_out_seed)
            if not tables.main_sessions:
                plan_.skipped = f"{encounter_type}: no resolved session is left for the main table"
            else:
                plan_.tables = tables
                plan_.rendered = [
                    render(template, tables, sample_sessions(tables.main_sessions, seed, config.sample_size),
                           config.encounter_descriptions[encounter_type])
                    for seed in config.run_seeds
                ]
        types.append(plan_)
    prices = PriceTable.from_yaml()
    return Plan(sources, types, template, preview_cost(config, types, template, prices))


# --- the client ----------------------------------------------------------------------------------


def make_client(config: ExtractionConfig, client_name: Optional[str] = None) -> LLMClient:
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


def ethics_needed(tables: Tables) -> list[str]:
    """Which ethics sign-offs a paid call that shows ``tables`` needs."""
    rows = [*tables.main]
    needed = []
    if any(row.get("own_ethnicity") for row in rows):
        needed.append("real_ethnicity")
    if any(row.get("finds_other_attractive") in ("yes", "no") for row in rows):
        needed.append("perceived_attractiveness")
    return needed


SIGN_OFFS = {
    "real_ethnicity": (ethics.REAL_ETHNICITY_SIGN_OFF, "docs/ethnicity.md, section 6"),
    "perceived_attractiveness": (ethics.ATTRACTIVENESS_SIGN_OFF, "docs/pairwise-factors.md, section 6"),
}


# --- one run -------------------------------------------------------------------------------------


def _usage(response: Any) -> dict[str, int]:
    return response.usage.as_dict()


def extract_once(
    config: ExtractionConfig, plan_: TypePlan, index: int, template: ExtractTemplate, client: LLMClient,
) -> dict[str, Any]:
    """One extraction run: the call (and a retry if its reply cannot be read), and the rules read,
    checked and scored. Returns the run's record; an aborted run says why."""
    rendered = plan_.rendered[index]
    tables = plan_.tables
    assert tables is not None
    messages = [dict(m) for m in rendered.messages]
    record: dict[str, Any] = {
        "extraction_log_version": EXTRACTION_LOG_VERSION, "experiment": config.experiment_name,
        "encounter_type": plan_.encounter_type, "run": index + 1, "seed": config.run_seeds[index],
        "started_utc": _utc_now(), "template": rendered.template,
        "llm": {key: config.llm[key] for key in ("model", "temperature", "max_tokens", "thinking")},
        "sampled_sessions": list(rendered.sampled), "sampled_labels": [tables.label[s] for s in rendered.sampled],
        "messages": [dict(m) for m in messages], "attempts": [], "outcome": None, "error": None, "rules": [],
    }
    rules_raw: Optional[list[Any]] = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        request = LLMRequest(
            messages=messages, model=config.llm["model"], temperature=config.llm["temperature"],
            max_tokens=config.llm["max_tokens"], json_mode=False, thinking=config.llm["thinking"] == "enabled",
            metadata={"experiment": config.experiment_name, "encounter_type": plan_.encounter_type, "run": index + 1, "attempt": attempt},
        )
        entry: dict[str, Any] = {"attempt": attempt, "messages_sent": len(messages)}
        if attempt > 1:
            entry["appended"] = messages[-2:]
        try:
            response = client.complete(request)
        except BudgetExceededError as exc:
            entry["error"] = f"budget: {exc}"
            record["attempts"].append(entry)
            record.update(outcome=RUN_ABORTED, error=f"budget: {exc}")
            break
        except LLMTransientError as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"
            record["attempts"].append(entry)
            record.update(outcome=RUN_ABORTED, error=entry["error"])
            break
        entry.update({
            "raw": response.content, "model": response.model, "system_fingerprint": response.system_fingerprint,
            "response_id": response.response_id, "finish_reason": response.finish_reason, "usage": _usage(response),
            "cost_usd": response.cost_usd, "price_tier": response.price_tier, "latency_s": response.latency_s,
            "started_utc": response.started_utc, "failed_sends": response.failed_attempts,
        })
        try:
            rules_raw = R.read_reply(response.content)
            entry["parse_error"] = None
            record["attempts"].append(entry)
            break
        except R.ReplyError as exc:
            entry["parse_error"] = str(exc)
            record["attempts"].append(entry)
            if attempt < MAX_ATTEMPTS:
                messages = [*messages, {"role": "assistant", "content": response.content or ""}, retry_message(template, str(exc))]
    if record["outcome"] is None:
        record["outcome"] = RUN_COMPLETED if rules_raw is not None else RUN_UNREADABLE
    for position, raw in enumerate(rules_raw or [], start=1):
        checked = R.check_rule(raw)
        entry = {"index": position, **checked.as_dict()}
        if checked.stored and checked.predict is not None:
            entry["fidelity"] = R.fidelity(checked.predict, tables.main, tables.held_out)
        record["rules"].append(entry)
    record["counts"] = dict(Counter(rule["category"] for rule in record["rules"]))
    record["totals"] = {
        "calls": sum(1 for a in record["attempts"] if "raw" in a or a.get("error")),
        "cost_usd": round(math.fsum(a.get("cost_usd") or 0.0 for a in record["attempts"]), 10),
        "prompt_tokens": sum((a.get("usage") or {}).get("prompt_tokens", 0) for a in record["attempts"]),
        "completion_tokens": sum((a.get("usage") or {}).get("completion_tokens", 0) for a in record["attempts"]),
        "cache_hit_tokens": sum((a.get("usage") or {}).get("prompt_cache_hit_tokens", 0) for a in record["attempts"]),
    }
    record["ended_utc"] = _utc_now()
    return record


# --- across the runs -----------------------------------------------------------------------------


def combine(config: ExtractionConfig, plan_: TypePlan, records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Match the stored rules of the runs, keep those found in ``min_runs``, and count the rest."""
    tables = plan_.tables
    assert tables is not None
    predicts: list[list[Optional[R.Predict]]] = []
    for record in records:
        row = []
        for rule in record["rules"]:
            stored = rule["category"] in R.STORED and rule["predict"] is not None
            row.append(R.read_predict(rule["predict"]) if stored else None)
        predicts.append(row)
    groups = R.group_rules(predicts, tables.main, config.agreement_min)
    runs = len(config.run_seeds)
    out = []
    for group in groups:
        first_run, first_index = group.members[0]
        representative = records[first_run]["rules"][first_index]
        found = len(group.runs())
        members = []
        for run, index in group.members:
            share = R.agreement(predicts[first_run][first_index], predicts[run][index], tables.main)
            members.append({"run": run + 1, "rule_index": index + 1, "agreement_with_first": round(share, 4),
                            "rule": records[run]["rules"][index]["raw"].get("rule"),
                            "fidelity": records[run]["rules"][index].get("fidelity")})
        out.append({
            "status": "candidate" if found >= config.min_runs else "unstable",
            "extraction_stability": f"{found}/{runs}",
            "category": representative["category"],
            "representative": {"run": first_run + 1, "rule_index": first_index + 1},
            "members": members,
        })
    counts: Counter = Counter()
    for record in records:
        counts.update(rule["category"] for rule in record["rules"])
    return {"groups": out, "categories": dict(counts), "runs": runs,
            "unreadable_runs": [r["run"] for r in records if r["outcome"] == RUN_UNREADABLE]}


def measured_debriefs(predict: R.Predict, rows: Sequence[Mapping[str, str]]) -> dict[str, int]:
    """The debrief kinds of the main-table rows the rule predicts rightly (D8's kinds)."""
    right = [row for row in rows if row.get(predict.target, "") != "" and predict.decide(row) == row[predict.target]]
    return dict(sorted(Counter(row.get("debrief_kind") or "no_answer" for row in right).items()))


class ExtractionStore:
    """Where the kept and unstable rules are written: write-once files under ``rules/``, each frozen
    with its SHA-256 in ``MANIFEST.json``, as the writer's staging databases are
    (``negsim.rulegen.writer``). Not a rule database: these rules are not in a rule format yet
    (RF-12 translates them), so nothing here is checked against the rule schemas."""

    def __init__(self, root: Path):
        self.root = Path(root)

    def manifest(self) -> dict[str, Any]:
        path = self.root / "MANIFEST.json"
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
        return {"about": ("Rules extracted by RF-11 (issue #66), written by negsim.extraction only. SHA-256 of every file, "
                          "line endings normalised to LF; a file is frozen once listed. Status candidate (found in enough runs) "
                          "or unstable (not passed to RF-12). References and debrief sources are unchecked (RF-14)."),
                "files": {}}

    def write(self, rule: Mapping[str, Any], note: str) -> tuple[str, bool]:
        import yaml

        name = f"rules/{rule['rule_id']}.v{rule['version']}.yaml"
        path = self.root / name
        # A copy through JSON, so that a value used twice is written out twice, not as a YAML alias.
        text = yaml.safe_dump(json.loads(json.dumps(dict(rule))), sort_keys=False, allow_unicode=True, width=100)
        manifest = self.manifest()
        if path.is_file() or name in manifest["files"]:
            if path.is_file() and path.read_text(encoding="utf-8").replace("\r\n", "\n") == text:
                return name, False
            raise ConfigError(f"{path} is frozen with other contents; an extraction's rules are written once")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        manifest["files"][name] = {"sha256": file_sha256(path), "frozen_on": date.today().isoformat(), "note": note}
        manifest["files"] = dict(sorted(manifest["files"].items()))
        _write_json(self.root / "MANIFEST.json", manifest)
        return name, True


def stored_rule(config: ExtractionConfig, plan_: TypePlan, group: Mapping[str, Any], records: Sequence[Mapping[str, Any]],
                sources: Sequence[Any]) -> dict[str, Any]:
    """The rule file of one group: the representative as the extractor wrote it, what was measured,
    and the provenance (the writer's, never the model's)."""
    tables = plan_.tables
    assert tables is not None
    run, index = group["representative"]["run"] - 1, group["representative"]["rule_index"] - 1
    entry = records[run]["rules"][index]
    raw = entry["raw"]
    predict = R.read_predict(entry["predict"])
    body = {key: raw[key] for key in R.REQUIRED if key in raw and key not in ("references", "predict")}
    rule_id = f"x_{plan_.encounter_type}_{R.rule_hash({'raw': raw, 'predict': entry['predict']})[:10]}"
    models = sorted({a.get("model") for r in records for a in r["attempts"] if a.get("model")})
    return {
        "rule_id": rule_id,
        "version": 1,
        "status": group["status"],
        "encounter_type": plan_.encounter_type,
        "category": group["category"],
        "extraction_stability": group["extraction_stability"],
        **body,
        "references": [{**reference, "check_status": "unchecked"} for reference in entry["references"]],
        "predict": predict.as_dict(),
        "measured": {
            "fidelity": entry.get("fidelity"),
            "debrief_kinds_where_it_holds": measured_debriefs(predict, tables.main),
            "matched_in_runs": group["members"],
        },
        "provenance": {
            "source_type": "extracted",
            "experiment": config.experiment_name,
            "created_utc": records[run]["ended_utc"],
            "author": f"negsim.extraction, from {', '.join(models) or '?'} with prompt template {records[run]['template']['key']}",
            "notes": ("Extracted by a language model from the resolved sessions of Step 1 (RF-11, issue #66); its id, status, "
                      "measured values and provenance are the code's, never the model's. A candidate, not checked against "
                      "evidence about people (RF-14)."),
            "sources": [str(Path(s.folder).resolve().relative_to(PACKAGE_ROOT)).replace("\\", "/") if Path(s.folder).resolve().is_relative_to(PACKAGE_ROOT) else str(s.folder) for s in sources],
            "sessions_used": [s.session_id for s in tables.main_sessions],
            "held_out_sessions": [s.session_id for s in tables.held_out_sessions],
            "failed_sessions_shown": [s.session_id for s in tables.failed_sessions],
            "sampled_sessions": {f"run_{r['run']}": r["sampled_sessions"] for r in records},
            "debrief_sources_status": "unchecked",
        },
    }


# --- the experiment ------------------------------------------------------------------------------


@dataclass
class ExtractionResult:
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


def _source_identity(source: Any) -> dict[str, Any]:
    folder = Path(source.folder).resolve()
    where = str(folder.relative_to(PACKAGE_ROOT)).replace("\\", "/") if folder.is_relative_to(PACKAGE_ROOT) else str(folder)
    return {"folder": where, "client": source.client, "outcomes_sha256": file_sha256(folder / "outcomes.csv"),
            "resolution_gate": source.gate}


def _comparable(described: Mapping[str, Any]) -> dict[str, Any]:
    """What must not change once a run has a record: everything but when, the commit, and the
    budget (which changes nothing that is sent: a cap raised later lets an aborted run finish)."""
    out = {key: value for key, value in described.items() if key not in ("created_utc", "git")}
    out["experiment"] = {key: value for key, value in (out.get("experiment") or {}).items() if key not in ("budget", "source")}
    return out


def write_tables(folder: Path, plan_: TypePlan) -> None:
    """The split and the tables, exactly as the extractor is shown them (and the held-out rows)."""
    tables = plan_.tables
    assert tables is not None
    _write_json(folder / "split.json", {
        "encounter_type": plan_.encounter_type, "gate": plan_.gate,
        "main_sessions": [s.session_id for s in tables.main_sessions],
        "held_out_sessions": [s.session_id for s in tables.held_out_sessions],
        "failed_sessions": [s.session_id for s in tables.failed_sessions],
        "labels": dict(sorted(tables.label.items(), key=lambda item: item[1])),
        "coin_flip_cells": tables.coin_flips,
    })
    for name, rows in (("main.csv", tables.main), ("held_out.csv", tables.held_out)):
        (folder / "tables").mkdir(parents=True, exist_ok=True)
        (folder / "tables" / name).write_text(as_csv(rows, COLUMNS) + "\n", encoding="utf-8", newline="\n")
    (folder / "tables" / "failed.csv").write_text(
        as_csv(failed_table(tables.failed_sessions), ("condition", "geometry", "first_sides_of_the_two", "failure", "sessions")) + "\n",
        encoding="utf-8", newline="\n")
    (folder / "tables" / "factors.csv").write_text(
        as_csv(factor_margins(tables.main_sessions, tables.failed_sessions, DESIGN_FACTORS), ("factor", "level", "resolved", "failed")) + "\n",
        encoding="utf-8", newline="\n")


def run_extraction(
    config: ExtractionConfig,
    client: Optional[LLMClient] = None,
    client_name: Optional[str] = None,
    out_root: Optional[Path | str] = None,
    confirm: bool = False,
    limit: Optional[int] = None,
    report: Callable[[str], None] = print,
    git: Optional[Mapping[str, Any]] = None,
    sign_off_file: Optional[Path] = None,
) -> ExtractionResult:
    """Run (or resume) the extraction. ``limit`` makes at most N runs that have no record yet."""
    name = client.name if client is not None else (client_name or config.llm["client"])
    if name not in CLIENTS:
        raise ConfigError(f"unknown client {name!r}; expected one of {list(CLIENTS)}")
    paid = name != "mock"
    experiment_dir = Path(out_root if out_root is not None else (RUNS_DIR if paid else MOCK_RUNS_DIR)) / config.experiment_name
    result = ExtractionResult(experiment_dir)
    if git is None:
        from ..experiment.batch import git_state

        git = git_state()
    plan_ = plan(config)
    preview = plan_.preview
    experiment_dir.mkdir(parents=True, exist_ok=True)
    described = {
        "extraction_log_version": EXTRACTION_LOG_VERSION, "layer": LAYER, "experiment": config.as_dict(), "client_name": name,
        "software": {"negsim": __version__}, "template": plan_.template.identity(),
        "sources": [_source_identity(s) for s in plan_.sources],
    }
    config_path = experiment_dir / "config.json"
    created = _utc_now()
    if config_path.is_file():
        before = json.loads(config_path.read_text(encoding="utf-8"))
        created = before.get("created_utc", created)
        if _comparable(before) != _comparable(described):
            if any(any((experiment_dir / t.encounter_type / "runs").glob("run_*.json")) for t in plan_.types):
                raise ConfigError(f"{experiment_dir}: it holds runs made with another config, client or source data; give the config a new experiment_name")
    _write_json(config_path, {**described, "created_utc": created, "git": dict(git)})
    _write_json(experiment_dir / "preview.json", preview)
    report(f"{config.experiment_name}: {sum(len(t.rendered) for t in plan_.types)} extraction run(s); worst-case cost USD "
           f"{preview['usd_total']:.6f}; cap USD {config.budget['cap_usd']:.2f}")

    def invocation(status: str, client_described: Mapping[str, Any]) -> None:
        _append_jsonl(experiment_dir / "invocations.jsonl", {
            "utc": _utc_now(), "git": dict(git), "client": dict(client_described), "confirm": confirm, "limit": limit,
            "status": status, "executed": list(result.executed), "aborted": result.aborted, "preview_usd": preview["usd_total"],
        })

    if paid:
        if not config.gate_required:
            invocation("refused_no_gate", {"client": name})
            raise ConfigError("a paid extraction needs the resolution gate (gate.require: true); only a mock rehearsal may go without it")
        path = sign_off_file or ethics.SIGN_OFF_FILE
        for plan_type in plan_.types:
            for needed in ethics_needed(plan_type.tables) if plan_type.tables is not None else ():
                sentence, where = SIGN_OFFS[needed]
                if not ethics.recorded(sentence, path):
                    invocation("refused_no_sign_off", {"client": name})
                    raise ConfigError(f"the table shows {needed.replace('_', ' ')}, and its ethics sign-off is not recorded in CLAUDE.md ({where})")
        if not confirm:
            result.status = STATUS_AWAITING
            invocation(STATUS_AWAITING, {"client": name})
            report("  a paid client, not confirmed: nothing was sent. Read the preview, then run again with --confirm.")
            return result
    if client is None:
        client = make_client(config, name)

    budget = math.inf if limit is None else max(0, limit)
    types_out = []
    for plan_type in plan_.types:
        folder = experiment_dir / plan_type.encounter_type
        if plan_type.skipped is not None:
            report(f"  {plan_type.skipped}")
            _write_json(folder / "split.json", {"encounter_type": plan_type.encounter_type, "gate": plan_type.gate, "skipped": plan_type.skipped})
            types_out.append({"encounter_type": plan_type.encounter_type, "gate": plan_type.gate, "skipped": plan_type.skipped})
            continue
        write_tables(folder, plan_type)
        records: list[Optional[dict[str, Any]]] = []
        for index in range(len(plan_type.rendered)):
            path = folder / "runs" / f"run_{index + 1}.json"
            previous = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
            if previous is not None and previous["outcome"] != RUN_ABORTED:
                if previous["messages"] != plan_type.rendered[index].messages:
                    raise ConfigError(f"{path}: its messages are not what this config renders now; the inputs changed under the experiment")
                records.append(previous)
                result.skipped.append(f"{plan_type.encounter_type}/run_{index + 1}")
                continue
            if result.aborted is not None or len(result.executed) >= budget:
                records.append(None)
                continue
            if previous is not None:
                _set_aside(path)
            record = extract_once(config, plan_type, index, plan_.template, client)
            _write_json(path, record)
            result.executed.append(f"{plan_type.encounter_type}/run_{index + 1}")
            report(f"  {plan_type.encounter_type} run {index + 1}: {record['outcome']}, {len(record['rules'])} rule(s) "
                   f"{record['counts']}, USD {record['totals']['cost_usd']:.6f}")
            if record["outcome"] == RUN_ABORTED:
                result.aborted = record["error"]
                report(f"  stopped: {record['error']}")
                records.append(None)
                continue
            records.append(record)
        entry: dict[str, Any] = {"encounter_type": plan_type.encounter_type, "gate": plan_type.gate,
                                 "split": {"main_sessions": len(plan_type.tables.main_sessions), "main_rows": len(plan_type.tables.main),
                                           "held_out_sessions": len(plan_type.tables.held_out_sessions), "held_out_rows": len(plan_type.tables.held_out),
                                           "failed_sessions": len(plan_type.tables.failed_sessions)},
                                 "coin_flip_cells": sum(c["coin_flip"] for c in plan_type.tables.coin_flips.values()),
                                 "repeated_cells": len(plan_type.tables.coin_flips),
                                 "runs": [None if r is None else {"run": r["run"], "outcome": r["outcome"], "rules": len(r["rules"]),
                                                                  "counts": r["counts"], "cost_usd": r["totals"]["cost_usd"],
                                                                  "sampled": r["sampled_labels"]} for r in records]}
        if all(r is not None for r in records):
            combined = combine(config, plan_type, records)  # type: ignore[arg-type]
            store = ExtractionStore(folder / STORE_DIR)
            stored = []
            for group in combined["groups"]:
                rule = stored_rule(config, plan_type, group, records, plan_.sources)  # type: ignore[arg-type]
                file_name, _ = store.write(rule, f"{group['status']}, found in {group['extraction_stability']} runs")
                group["rule_id"], group["file"] = rule["rule_id"], file_name
                stored.append({"rule_id": rule["rule_id"], "status": rule["status"], "category": rule["category"],
                               "extraction_stability": rule["extraction_stability"], "rule": rule.get("rule"),
                               "target": rule["predict"]["target"], "fidelity": rule["measured"]["fidelity"],
                               "references": [r["citation"] for r in rule["references"]],
                               "needs_communication": rule["category"] == R.NEEDS_COMMUNICATION, "file": file_name})
            _write_json(folder / "rules.json", combined)
            entry["rules"] = stored
            entry["categories"] = combined["categories"]
            entry["unreadable_runs"] = combined["unreadable_runs"]
        types_out.append(entry)
    complete = all(t.get("skipped") or "rules" in t for t in types_out)
    result.status = STATUS_COMPLETED if complete and result.aborted is None else STATUS_PARTIAL
    # Every run record counts, an aborted one and those set aside included: what it spent before it
    # stopped was charged.
    cost = math.fsum(
        json.loads(path.read_text(encoding="utf-8"))["totals"]["cost_usd"]
        for t in plan_.types for path in sorted((experiment_dir / t.encounter_type / "runs").glob("run_*.json"))
    )
    summary = {"experiment": config.experiment_name, "status": result.status, "client": name, "types": types_out,
               "cost": {"preview_usd": preview["usd_total"], "actual_usd": round(cost, 10), "cap_usd": config.budget["cap_usd"]}}
    _write_json(experiment_dir / "summary.json", summary)
    (experiment_dir / "report.md").write_text(report_markdown(config, summary), encoding="utf-8", newline="\n")
    result.summary = summary
    invocation(result.status, client.describe())
    return result


# --- the report ----------------------------------------------------------------------------------


def _accuracy(fidelity: Optional[Mapping[str, Any]]) -> str:
    if not fidelity or fidelity["held_out"]["accuracy"] is None:
        return "n/a"
    held = fidelity["held_out"]
    return (f"{held['correct']}/{held['rows']} ({held['accuracy']:.2f}) against "
            f"{fidelity['baseline_accuracy']:.2f} for always `{fidelity['baseline_value']}`")


def report_markdown(config: ExtractionConfig, summary: Mapping[str, Any]) -> str:
    lines = [f"# Rule extraction: {config.experiment_name}", "", config.description, "",
             f"Status: {summary['status']}; client {summary['client']}; cost USD {summary['cost']['actual_usd']:.6f} "
             f"(worst case USD {summary['cost']['preview_usd']:.6f}, cap USD {summary['cost']['cap_usd']:.2f}).", ""]
    for entry in summary["types"]:
        gate_ = entry["gate"]
        lines += [f"## {entry['encounter_type']}", ""]
        rate = "n/a" if gate_["rate"] is None else f"{gate_['rate']:.2f} (95% CI {gate_['ci95'][0]:.2f} to {gate_['ci95'][1]:.2f})"
        lines.append(f"Gate: {gate_['resolved']} of {gate_['n']} design sessions resolved in `plan_only`, {rate}; "
                     f"threshold {gate_['threshold']}: **{gate_['status']}**.")
        lines.append("")
        if entry.get("skipped"):
            lines += [f"Skipped: {entry['skipped']}.", ""]
            continue
        split = entry["split"]
        lines += [f"Main table {split['main_sessions']} sessions ({split['main_rows']} rows); held out {split['held_out_sessions']} "
                  f"sessions ({split['held_out_rows']} rows); failed sessions shown {split['failed_sessions']}. "
                  f"Coin-flip cells: {entry['coin_flip_cells']} of {entry['repeated_cells']} repeated.", "",
                  "| Run | Outcome | Rules | Categories | Cost (USD) |", "| --- | --- | --- | --- | --- |"]
        for run in entry["runs"]:
            if run is None:
                lines.append("| - | not run | | | |")
                continue
            lines.append(f"| {run['run']} | {run['outcome']} | {run['rules']} | {run['counts']} | {run['cost_usd']:.6f} |")
        lines.append("")
        if "rules" not in entry:
            lines += ["Not every run has a record yet: the rules are matched once all have.", ""]
            continue
        lines += [f"Across the runs: {entry['categories']} (a `protected_attribute` rule is counted, never stored).", "",
                  "| Rule | Status | Found in | Target | Held-out accuracy | References |", "| --- | --- | --- | --- | --- | --- |"]
        for rule in entry["rules"]:
            flag = " (needs communication)" if rule["needs_communication"] else ""
            lines.append(f"| {rule['rule']}{flag} | {rule['status']} | {rule['extraction_stability']} | `{rule['target']}` | "
                         f"{_accuracy(rule['fidelity'])} | {'; '.join(rule['references'])} |")
        lines.append("")
    lines += ["Fidelity says whether a rule describes the LLM agents' behaviour, not whether it describes people (RF-14). "
              "References and debrief sources are unchecked.", ""]
    return "\n".join(lines)


# --- the command line ----------------------------------------------------------------------------


def print_plan(config: ExtractionConfig, out: Callable[[str], None] = print) -> Plan:
    plan_ = plan(config)
    preview = plan_.preview
    out(f"{config.experiment_name}: rule extraction from {len(plan_.sources)} source(s), template {config.template}, model {config.llm['model']}")
    for plan_type in plan_.types:
        gate_ = plan_type.gate
        out(f"  {plan_type.encounter_type}: gate {gate_['status']} ({gate_['resolved']} of {gate_['n']}, threshold {gate_['threshold']})")
        if plan_type.skipped:
            out(f"    skipped: {plan_type.skipped}")
            continue
        t = plan_type.tables
        assert t is not None
        out(f"    main {len(t.main_sessions)} sessions ({len(t.main)} rows), held out {len(t.held_out_sessions)}, failed {len(t.failed_sessions)}")
        for index, rendered in enumerate(plan_type.rendered):
            chars = sum(len(m["content"]) for m in rendered.messages)
            out(f"    run {index + 1} (seed {config.run_seeds[index]}): {len(rendered.sampled)} sessions in full, {chars} characters")
    out(f"  worst-case cost USD {preview['usd_total']:.6f} ({preview['attempts_per_run']} attempt(s) per run, "
        f"{preview['sends_per_attempt']} send(s) each); cap USD {preview['cap_usd']:.2f}; largest single call bound USD "
        f"{max((r['largest_call_bound_usd'] for r in preview['runs']), default=0.0):.6f}")
    if not preview["fits_the_cap"]:
        out("  the worst case exceeds the cap: a confirmed paid run starts anyway, and the budget guard refuses any call that "
            "could take this experiment's recorded spend past the cap, so a run may be aborted (a rerun redoes it)")
    return plan_


def cli_run(args: argparse.Namespace) -> int:
    """What ``run_experiment.py`` does with a config that says ``layer: rule_extraction``."""
    try:
        config = ExtractionConfig.load(args.config)
        if args.plan:
            print_plan(config)
            return 0
        result = run_extraction(config, client_name=args.client, out_root=args.out, confirm=args.confirm, limit=args.limit)
    except (ConfigError, LLMFatalError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"logs: {result.experiment_dir}")
    if result.status == STATUS_AWAITING:
        return 4
    print(f"{result.status}: {len(result.executed)} run(s) made, {len(result.skipped)} already done; "
          f"actual cost USD {result.summary['cost']['actual_usd']:.6f}")
    if result.aborted:
        print(f"stopped early: {result.aborted}", file=sys.stderr)
        return 3
    return 0
