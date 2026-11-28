"""The extractor's rules: reading the reply, checking each rule, ``predict``, the fidelity scorer,
and matching rules across runs (issue #66, RF-11, tasks 4 to 6).

**The reply** is a YAML block with a list ``rules``. Each rule has ``rule``, ``applies_when``,
``action``, ``exceptions``, ``factors_used``, ``needs_communication``, ``references`` (each with
``citation``, ``locator``, ``kind``, ``claim``; or ``no known source``), ``debrief_support``,
``coverage`` and ``predict``.

**``predict``** is a decision list over the agent table's own columns::

    predict:
      target: first_side
      if:
        - when: {other_load: large_suitcase, condition: [non_verbal, talk]}
          then: left
      default: right

A ``when`` is a conjunction. A value is matched as text; a list is "one of"; a mapping with one of
``==``, ``!=``, ``<``, ``<=``, ``>``, ``>=`` compares numbers (a row whose cell is not a number does
not match). The first ``when`` that matches gives the decision, else ``default``. It may read only
:data:`negsim.extraction.table.CONDITION_COLUMNS`, never its own target, and predict only one of
:data:`negsim.extraction.table.TARGETS`.

**Categories** (``negsim.rulegen.validate``'s names):

- ``protected_attribute``: the rule reads ethnicity or perceived attractiveness, in ``predict``,
  in ``factors_used`` or in its words. Kept and counted, never stored as a rule, never passed to
  RF-12. Checked first.
- ``schema_error``: a field is missing or malformed, or ``predict`` cannot be evaluated.
- ``needs_communication``: the rule is otherwise valid but holds only with a signal or a message
  (it says so, or ``predict`` reads ``signalled`` or ``spoke``; ``resolution.md``, D9).
- ``valid``.

**Fidelity** (task 6): ``predict`` applied mechanically to the held-out rows whose target is known,
against the majority-class baseline (the main table's commonest value of the target).

**Matching** (task 5): two rules from different runs match when they predict the same target and
give the same decision on at least ``agreement_min`` (95% ``[placeholder]``) of the main table's
rows. Rules are grouped in run order: a rule joins the first group whose first rule it matches and
that has no rule of its run yet. A group found in at least ``min_runs`` (2) of the runs is kept,
with its ``extraction_stability`` (2/3 or 3/3); a group found once is ``unstable``.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

import yaml

from ..rules.fields import ATTRACTIVENESS_PATTERN, PROTECTED_STEM, REAL_ETHNICITY_WORDS
from .table import COMMUNICATION_COLUMNS, CONDITION_COLUMNS, NUMERIC_COLUMNS, PROTECTED_COLUMNS, TARGETS

VALID = "valid"
NEEDS_COMMUNICATION = "needs_communication"
SCHEMA_ERROR = "schema_error"
PROTECTED_ATTRIBUTE = "protected_attribute"
CATEGORIES = (VALID, NEEDS_COMMUNICATION, SCHEMA_ERROR, PROTECTED_ATTRIBUTE)
STORED = (VALID, NEEDS_COMMUNICATION)

REQUIRED = ("rule", "applies_when", "action", "exceptions", "factors_used", "needs_communication", "references",
            "debrief_support", "coverage", "predict")
REFERENCE_KEYS = ("citation", "locator", "kind", "claim")
REFERENCE_KINDS = ("law_or_guidance", "published_study", "local_custom", "habit", "common_sense", "none")
NO_KNOWN_SOURCE = "no known source"
OPERATORS = ("==", "!=", "<", "<=", ">", ">=")

_FENCE = re.compile(r"```(?:ya?ml)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
_WORDS = re.compile(r"[^a-z0-9]+")


class ReplyError(ValueError):
    """The reply cannot be read as a list of rules."""


def read_reply(text: Optional[str]) -> list[Any]:
    """The ``rules`` of a reply: the YAML in its first fenced block, or the whole reply."""
    if not text or not text.strip():
        raise ReplyError("the reply is empty")
    found = _FENCE.search(text)
    body = found.group(1) if found else text
    try:
        data = yaml.safe_load(body)
    except yaml.YAMLError as exc:
        raise ReplyError(f"the reply is not YAML: {str(exc).splitlines()[0]}") from exc
    if isinstance(data, Mapping) and isinstance(data.get("rules"), list):
        return list(data["rules"])
    raise ReplyError("the reply has no list 'rules'")


# --- predict -------------------------------------------------------------------------------------


def _as_number(text: Any) -> Optional[float]:
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _text(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _test_matches(cell: str, test: Any) -> bool:
    if isinstance(test, Mapping):
        (op, value), = test.items()
        if op in ("==", "!="):
            same = _text(cell) == _text(value)
            return same if op == "==" else not same
        left, right = _as_number(cell), _as_number(value)
        if left is None or right is None:
            return False
        return {"<": left < right, "<=": left <= right, ">": left > right, ">=": left >= right}[op]
    if isinstance(test, list):
        return any(_text(cell) == _text(item) for item in test)
    return _text(cell) == _text(test)


@dataclass(frozen=True)
class Predict:
    target: str
    branches: tuple[tuple[tuple[tuple[str, Any], ...], str], ...]
    default: str

    @property
    def columns(self) -> list[str]:
        return sorted({column for when, _ in self.branches for column, _ in when})

    def decide(self, row: Mapping[str, str]) -> str:
        for when, then in self.branches:
            if all(_test_matches(row.get(column, ""), test) for column, test in when):
                return then
        return self.default

    def as_dict(self) -> dict[str, Any]:
        return {"target": self.target, "if": [{"when": dict(when), "then": then} for when, then in self.branches], "default": self.default}


def read_predict(raw: Any) -> Predict:
    """A ``predict`` block, checked against the table's columns; ``ValueError`` if it is not usable."""
    if not isinstance(raw, Mapping):
        raise ValueError("predict: expected a mapping with target, if and default")
    target = raw.get("target")
    if target not in TARGETS:
        raise ValueError(f"predict.target: {target!r} is not one of {list(TARGETS)}")
    if "default" not in raw or raw["default"] is None or isinstance(raw["default"], (Mapping, list)):
        raise ValueError("predict.default: one value of the target")
    branches = []
    for index, branch in enumerate(raw.get("if") or []):
        where = f"predict.if[{index}]"
        if not isinstance(branch, Mapping) or not isinstance(branch.get("when"), Mapping) or not branch["when"] or "then" not in branch:
            raise ValueError(f"{where}: expected {{when: {{column: value, ...}}, then: value}}")
        if branch["then"] is None or isinstance(branch["then"], (Mapping, list)):
            raise ValueError(f"{where}.then: one value of the target")
        tests = []
        for column, test in branch["when"].items():
            if column == target:
                raise ValueError(f"{where}: reads its own target {column!r}")
            if column not in CONDITION_COLUMNS and column not in PROTECTED_COLUMNS:
                raise ValueError(f"{where}: {column!r} is not a column a rule may read ({list(CONDITION_COLUMNS)})")
            if isinstance(test, Mapping):
                if len(test) != 1 or next(iter(test)) not in OPERATORS:
                    raise ValueError(f"{where}.when.{column}: a comparison is one of {list(OPERATORS)} with a value")
                op, value = next(iter(test.items()))
                if op not in ("==", "!=") and (column not in NUMERIC_COLUMNS or _as_number(value) is None):
                    raise ValueError(f"{where}.when.{column}: {op} compares numbers, and {column!r} is not a number column")
                tests.append((str(column), {op: value}))
            elif isinstance(test, list):
                if not test or any(isinstance(item, (Mapping, list)) for item in test):
                    raise ValueError(f"{where}.when.{column}: a list of values")
                tests.append((str(column), [_text(item) for item in test]))
            elif test is None:
                raise ValueError(f"{where}.when.{column}: no value")
            else:
                tests.append((str(column), _text(test)))
        branches.append((tuple(tests), _text(branch["then"])))
    return Predict(str(target), tuple(branches), _text(raw["default"]))


# --- one rule ------------------------------------------------------------------------------------


def _protected_word(text: Any) -> Optional[str]:
    """A word about ethnicity or perceived attractiveness in a rule's own words. As
    ``negsim.rules.fields.protected_reference``, except that "pretty" alone (as in "pretty
    close") is not taken for attractiveness in prose."""
    if not isinstance(text, str):
        return None
    lowered = text.lower()
    if PROTECTED_STEM in lowered:
        return PROTECTED_STEM
    for found in ATTRACTIVENESS_PATTERN.finditer(lowered):
        if found.group(0) != "pretty":
            return found.group(0)
    words = set(_WORDS.split(lowered))
    for word in REAL_ETHNICITY_WORDS:
        if word in words:
            return word
    return None


def _texts(rule: Mapping[str, Any]) -> list[tuple[str, str]]:
    out = []
    for key in ("rule", "applies_when", "action", "coverage"):
        if isinstance(rule.get(key), str):
            out.append((key, rule[key]))
    for index, item in enumerate(rule.get("exceptions") or [] if isinstance(rule.get("exceptions"), list) else []):
        if isinstance(item, str):
            out.append((f"exceptions[{index}]", item))
    return out


@dataclass
class Checked:
    """One rule as the extractor wrote it, and what the check made of it."""

    raw: Any
    category: str
    message: str
    predict: Optional[Predict] = None
    references: list[dict[str, str]] = field(default_factory=list)
    reads_communication: bool = False

    @property
    def stored(self) -> bool:
        return self.category in STORED

    def as_dict(self) -> dict[str, Any]:
        return {"category": self.category, "message": self.message, "reads_communication": self.reads_communication,
                "predict": None if self.predict is None else self.predict.as_dict(), "references": self.references, "raw": self.raw}


def read_references(raw: Any) -> list[dict[str, str]]:
    """References as a list of {citation, locator, kind, claim}; ``no known source`` as one entry
    with that citation and kind ``none``."""
    if isinstance(raw, str):
        if raw.strip().lower().rstrip(".") == NO_KNOWN_SOURCE:
            return [{"citation": NO_KNOWN_SOURCE, "locator": "none", "kind": "none", "claim": "none"}]
        raise ValueError(f"references: a list, or {NO_KNOWN_SOURCE!r}")
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"references: a list of {list(REFERENCE_KEYS)}, or {NO_KNOWN_SOURCE!r}")
    out = []
    for index, entry in enumerate(raw):
        if isinstance(entry, str) and entry.strip().lower().rstrip(".") == NO_KNOWN_SOURCE:
            out.append({"citation": NO_KNOWN_SOURCE, "locator": "none", "kind": "none", "claim": "none"})
            continue
        if not isinstance(entry, Mapping) or any(key not in entry for key in REFERENCE_KEYS):
            raise ValueError(f"references[{index}]: needs {list(REFERENCE_KEYS)}")
        if entry["kind"] not in REFERENCE_KINDS:
            raise ValueError(f"references[{index}].kind: {entry['kind']!r} is not one of {list(REFERENCE_KINDS)}")
        out.append({key: _text(entry[key]) for key in REFERENCE_KEYS})
    return out


def check_rule(raw: Any) -> Checked:
    """Categorise one rule of the reply (protected attribute first)."""
    if not isinstance(raw, Mapping):
        return Checked(raw, SCHEMA_ERROR, "a rule must be a mapping")
    predict_raw = raw.get("predict") if isinstance(raw.get("predict"), Mapping) else {}
    read = [str(column) for branch in (predict_raw.get("if") or []) if isinstance(branch, Mapping)
            for column in (branch.get("when") or {} if isinstance(branch.get("when"), Mapping) else {})]
    for column in read:
        if column in PROTECTED_COLUMNS or _protected_word(column.replace("_", " ")):
            return Checked(raw, PROTECTED_ATTRIBUTE, f"predict reads {column!r}, which no rule may read")
    for name in raw.get("factors_used") or [] if isinstance(raw.get("factors_used"), list) else []:
        if str(name) in PROTECTED_COLUMNS or _protected_word(str(name).replace("_", " ")):
            return Checked(raw, PROTECTED_ATTRIBUTE, f"factors_used names {name!r}, which no rule may read")
    for where, text in _texts(raw):
        word = _protected_word(text)
        if word is not None:
            return Checked(raw, PROTECTED_ATTRIBUTE, f"{where} uses {word!r}: ethnicity or perceived attractiveness, which no rule may read")
    missing = [key for key in REQUIRED if key not in raw]
    if missing:
        return Checked(raw, SCHEMA_ERROR, f"missing {missing}")
    for key in ("rule", "applies_when", "action"):
        if not isinstance(raw[key], str) or not raw[key].strip():
            return Checked(raw, SCHEMA_ERROR, f"{key}: text")
    if not isinstance(raw["exceptions"], list) or not isinstance(raw["factors_used"], list):
        return Checked(raw, SCHEMA_ERROR, "exceptions and factors_used: lists")
    if not isinstance(raw["needs_communication"], bool):
        return Checked(raw, SCHEMA_ERROR, "needs_communication: true or false")
    try:
        references = read_references(raw["references"])
        predict = read_predict(raw["predict"])
    except ValueError as exc:
        return Checked(raw, SCHEMA_ERROR, str(exc))
    communication = any(column in COMMUNICATION_COLUMNS for column in predict.columns)
    if raw["needs_communication"] or communication:
        why = "it says it needs communication" if raw["needs_communication"] else f"predict reads {[c for c in predict.columns if c in COMMUNICATION_COLUMNS]}"
        return Checked(raw, NEEDS_COMMUNICATION, why, predict, references, communication)
    return Checked(raw, VALID, "ok", predict, references, communication)


# --- fidelity ------------------------------------------------------------------------------------


def majority(rows: Sequence[Mapping[str, str]], target: str) -> Optional[str]:
    """The commonest known value of ``target`` (ties broken by the value, so it is fixed)."""
    counts = Counter(row.get(target, "") for row in rows if row.get(target, "") != "")
    if not counts:
        return None
    best = max(counts.values())
    return sorted(value for value, count in counts.items() if count == best)[0]


def accuracy(predict: Predict, rows: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    """``predict`` on the rows whose target is known: how many it gets right."""
    known = [row for row in rows if row.get(predict.target, "") != ""]
    right = sum(predict.decide(row) == row[predict.target] for row in known)
    return {"rows": len(known), "correct": right, "accuracy": None if not known else round(right / len(known), 4)}


def fidelity(predict: Predict, main: Sequence[Mapping[str, str]], held_out: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    """Held-out accuracy against the majority-class baseline (the main table's commonest value),
    and the same on the main table (in-sample)."""
    base = majority(main, predict.target)
    known = [row for row in held_out if row.get(predict.target, "") != ""]
    baseline = sum(row[predict.target] == base for row in known)
    held = accuracy(predict, held_out)
    return {
        "target": predict.target,
        "held_out": held,
        "baseline_value": base,
        "baseline_accuracy": None if not known else round(baseline / len(known), 4),
        "beats_baseline": None if not known else held["correct"] > baseline,
        "main": accuracy(predict, main),
    }


# --- matching across runs ------------------------------------------------------------------------


def agreement(one: Predict, two: Predict, rows: Sequence[Mapping[str, str]]) -> Optional[float]:
    """The share of ``rows`` on which two predict lists of the same target decide alike; ``None``
    for different targets."""
    if one.target != two.target or not rows:
        return None
    return sum(one.decide(row) == two.decide(row) for row in rows) / len(rows)


@dataclass
class Group:
    """Rules of different runs that match: ``members`` are (run index, rule index), in run order."""

    members: list[tuple[int, int]]

    def runs(self) -> set[int]:
        return {run for run, _ in self.members}


def group_rules(rules: Sequence[Sequence[Optional[Predict]]], rows: Sequence[Mapping[str, str]], agreement_min: float) -> list[Group]:
    """Group the rules of each run (``rules[run][index]``; ``None`` for one that is not grouped)."""
    groups: list[Group] = []
    for run, predicts in enumerate(rules):
        for index, predict in enumerate(predicts):
            if predict is None:
                continue
            for group in groups:
                first_run, first_index = group.members[0]
                if run in group.runs():
                    continue
                share = agreement(rules[first_run][first_index], predict, rows)
                if share is not None and share >= agreement_min:
                    group.members.append((run, index))
                    break
            else:
                groups.append(Group([(run, index)]))
    return groups


def rule_hash(rule: Mapping[str, Any]) -> str:
    """A stable hash of a rule's content (its id in the store)."""
    return hashlib.sha256(json.dumps(rule, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()
