"""What becomes of a proposed rule: its category (issue #30, Part 7; ``docs/rule-generation.md``).

Every rule a model proposes, in either condition, is run through the rule loader of issue #28
and given exactly one category. Nothing is discarded: a refused rule is data.

``valid``                It loads, and the session's visibility settings let both agents see
                         everything it reads.
``needs_communication``  It reads private or unobservable information: a field the loader
                         refuses as ``unobservable_field`` (a task, an agent's own position,
                         one agent's point of view), a field that names private information
                         (:data:`PRIVATE_WORDS`), or a field the session hides (age or gender
                         when demographics are hidden). Such a rule could only be followed if
                         the two talked first. The format is not extended to read private
                         information (a decision of the issue, pending the supervisor).
``inconsistent``         Refused for shares that sum to less than 1, opposite sides, or
                         passage orders that are not one leader and one follower.
``schema_error``         Refused for its structure: an unknown key or field, a wrong type or
                         unit, a missing tie policy, roles that do not fit the directive.
``format_limit``         It asks for something the format cannot express, as far as that can
                         be told mechanically: more than two roles; roles given by a category
                         (the format orders the two by a number only, so "the woman goes first"
                         cannot be written); or a formula where a constant or a field is
                         required (a share that grows with the age gap, a threshold that scales
                         with something). A formula is a value that depends on something
                         (:func:`is_formula`): a field, a word such as "if" or "per", or
                         arithmetic on a named quantity. Arithmetic on numbers alone ("1/2") and
                         a number with its unit ("0.5 m") are constants written wrongly:
                         ``schema_error``.

The categories are tried in that order of precedence: a rule that reads private information
is ``needs_communication`` even if it is also malformed, and a rule written as a formula is
``format_limit`` though the loader would call it a schema error. Whether what a
``format_limit`` rule wanted could have been written another way is not judged here.

What cannot be told mechanically is flagged for **manual review** (:data:`REVIEW_PATTERNS`):
an ``intent``, a ``reason``, a message of the conversation or a value written as text that
speaks of scaling ("grows with"), of "the more ..., the more ...", of a rate ("per year") or
of more than two people. A flag never changes the category; flags are counted on their own.
"""

from __future__ import annotations

import functools
import re
from dataclasses import dataclass, field
from typing import Any, Iterator, Mapping, Optional, Sequence

from ..rules.database import RULE_DB_ROOT, RuleSchemas, load_validator
from ..rules.errors import RuleError
from ..rules.fields import AGENT_FIELDS, CATEGORY, CONDITION_PREFIXES, PAIR_FIELDS, ROLE_PREFIXES, resolve
from ..rules.model import parse_rule

VALID = "valid"
NEEDS_COMMUNICATION = "needs_communication"
INCONSISTENT = "inconsistent"
SCHEMA_ERROR = "schema_error"
FORMAT_LIMIT = "format_limit"
CATEGORIES = (VALID, NEEDS_COMMUNICATION, INCONSISTENT, SCHEMA_ERROR, FORMAT_LIMIT)

#: The loader's reasons for refusing a rule, and the category each falls in.
LOADER_CATEGORIES = {
    "unobservable_field": NEEDS_COMMUNICATION,
    "visibility": NEEDS_COMMUNICATION,
    "reciprocity": INCONSISTENT,
    "side": INCONSISTENT,
    "passage_order": INCONSISTENT,
    "schema": SCHEMA_ERROR,
    "unknown_field": SCHEMA_ERROR,
    "unit": SCHEMA_ERROR,
    "value": SCHEMA_ERROR,
    "operator": SCHEMA_ERROR,
    "roles": SCHEMA_ERROR,
    "no_tie_policy": SCHEMA_ERROR,
}
#: Words that, in an unknown field's name, name private information: the session's errand
#: and its urgency, and what an errand implies about a person.
PRIVATE_WORDS = frozenset(
    {"task", "tasks", "errand", "urgency", "urgent", "hurry", "rush", "rushing", "destination", "goal", "purpose", "late", "deadline", "appointment", "emergency"}
)
#: The keys of a rule that the writer fills and a model may not: what a model writes there is
#: ignored and logged (issue #30, Part 8).
METADATA_KEYS = ("schema_version", "rule_id", "version", "status", "provenance", "screening")
#: The directive fields, each of which takes a constant.
DIRECTIVE_FIELDS = ("side_preference", "responsibility_share", "speed_scale", "clearance_margin", "passage_order")
#: Patterns that suggest something the format cannot express, each with the name its flag is
#: recorded under. They read words, so they only flag, for a person to look at.
REVIEW_PATTERNS = (
    ("scaling", re.compile(r"\b(proportional(ly)?|in proportion|scales? with|scaled by|grows? with|increases? with|decreases? with|var(y|ies) with|as a function of)\b")),
    ("the_more_the_more", re.compile(r"\bthe (more|less|fewer|[a-z]+er)\b[^.;:!?]{0,80}?,\s*the (more|less|fewer|[a-z]+er)\b")),
    ("rate", re.compile(r"\bper (year|years|second|seconds|metre|meter|m|unit)\b")),
    ("more_than_two_people", re.compile(r"\b(more than two (people|persons|agents|roles)|three or more|three people|a group|groups of|the group)\b")),
)
_ARITHMETIC = re.compile(r"[+*/×÷^]|(?<=[\w)])\s*-\s*(?=[\w(.])")  # a minus between two terms, not a sign
_FIELD = re.compile(r"\b(pair|either|both|agent)\.[a-z_]+")
_DEPENDENCY = re.compile(r"\b(times|plus|minus|per|proportional(ly)?|depending|depends|scales?|grows?|increases?|decreases?|if|when|unless)\b")
_WORD = re.compile(r"[a-z_][a-z_0-9]*")
_SCIENTIFIC = re.compile(r"\d(\.\d*)?e[+-]?\d+")
_UNIT_WORDS = frozenset({"m", "s", "rad", "deg", "years", "year", "metre", "metres", "meter", "meters", "second", "seconds", "sec", "mps"})
_PLACEHOLDER_RULE_ID = "proposal_under_check"


def is_formula(text: str) -> bool:
    """Whether a value written as text depends on something: it names a field, uses a word of
    dependence ("if", "per", "grows", ...), or does arithmetic with a named quantity in it.
    ``"0.5 + 0.01 * pair.age_difference_years"`` and ``"2 * speed"`` are formulas;
    ``"1/2"`` and ``"0.5 m"`` are constants (``m/s`` is a unit, not a division)."""
    lowered = _SCIENTIFIC.sub("0", text.lower().replace("m/s", " "))
    if _FIELD.search(lowered) or _DEPENDENCY.search(lowered):
        return True
    named = [word for word in _WORD.findall(lowered) if word not in _UNIT_WORDS]
    return bool(_ARITHMETIC.search(lowered) and named)


@functools.lru_cache(maxsize=1)
def _schemas() -> RuleSchemas:
    return load_validator(RULE_DB_ROOT)


@dataclass
class Validation:
    """What one proposed rule turned out to be."""

    category: str
    loader_category: Optional[str]
    message: str
    fields: list[str] = field(default_factory=list)
    ignored_metadata: dict[str, Any] = field(default_factory=dict)
    review_flags: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "loader_category": self.loader_category,
            "message": self.message,
            "fields": list(self.fields),
            "ignored_metadata": dict(self.ignored_metadata),
            "review_flags": list(self.review_flags),
        }


def _comparisons(condition: Any, where: str) -> Iterator[tuple[str, Mapping[str, Any]]]:
    if isinstance(condition, Mapping):
        for kind in ("all", "any"):
            if isinstance(condition.get(kind), list):
                for index, item in enumerate(condition[kind]):
                    yield from _comparisons(item, f"{where}.{kind}[{index}]")
                return
        yield where, condition


def field_references(proposal: Mapping[str, Any]) -> list[tuple[str, str, tuple[str, ...]]]:
    """Every field the proposal names: (where, the field as written, the prefixes allowed there)."""
    found = []
    for where, comparison in _comparisons(proposal.get("when"), "when"):
        if isinstance(comparison.get("field"), str):
            found.append((where, comparison["field"], CONDITION_PREFIXES))
    roles = proposal.get("roles")
    if isinstance(roles, Mapping) and isinstance(roles.get("by"), Mapping) and isinstance(roles["by"].get("field"), str):
        found.append(("roles.by", roles["by"]["field"], ROLE_PREFIXES))
    return found


def _role_assignment(proposal: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
    roles = proposal.get("roles")
    return roles["by"] if isinstance(roles, Mapping) and isinstance(roles.get("by"), Mapping) else None


def _is_number_field(written: Any) -> bool:
    if not isinstance(written, str) or "." not in written:
        return False
    table = PAIR_FIELDS if written.split(".", 1)[0] == "pair" else AGENT_FIELDS
    spec = table.get(written.split(".", 1)[1])
    return spec is not None and spec.kind != CATEGORY


def text_slots(proposal: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Every value written as text where the format takes a constant: a directive field, the
    value of a comparison on a number, ``tie_within``. As (where, the text)."""
    found = []
    directive = proposal.get("directive")
    if isinstance(directive, Mapping):
        for role, entry in directive.items():
            if isinstance(entry, Mapping):
                found += [(f"directive.{role}.{name}", entry[name]) for name in DIRECTIVE_FIELDS if isinstance(entry.get(name), str)]
    for where, comparison in _comparisons(proposal.get("when"), "when"):
        value = comparison.get("value")
        if _is_number_field(comparison.get("field")):
            found += [(f"{where}.value", item) for item in (value if isinstance(value, list) else [value]) if isinstance(item, str)]
    by = _role_assignment(proposal)
    if by is not None and isinstance(by.get("tie_within"), str):
        found.append(("roles.by.tie_within", by["tie_within"]))
    return found


def _needs_communication(proposal: Mapping[str, Any], visibility: Mapping[str, bool]) -> Optional[tuple[str, str]]:
    """Why the proposal reads what the two could not both see, if it does."""
    for where, written, prefixes in field_references(proposal):
        try:
            ref = resolve(written, where, prefixes)
        except RuleError as error:
            if error.category == "unobservable_field":
                return "unobservable_field", str(error)
            words = set(re.split(r"[^a-z]+", written.lower()))
            if error.category == "unknown_field" and words & PRIVATE_WORDS:
                return "private_information", f"{where}: '{written}' names private information ({sorted(words & PRIVATE_WORDS)})"
            continue
        hidden = sorted(name for name in ref.spec.needs if not visibility.get(name, False))
        if hidden:
            return "hidden_in_session", f"{where}: '{written}' reads {hidden}, which this session's people cannot see"
    return None


def _format_limit(proposal: Mapping[str, Any]) -> Optional[str]:
    """Something the format cannot express, if it can be told mechanically."""
    directive = proposal.get("directive")
    if isinstance(directive, Mapping) and len(directive) > 2:
        return f"directive: {len(directive)} roles ({sorted(directive)}); a rule gives at most two"
    by = _role_assignment(proposal)
    if by is not None:
        assign = by.get("assign")
        if isinstance(assign, list) and len(assign) > 2:
            return f"roles.by.assign: {len(assign)} roles; a rule gives at most two"
        if isinstance(by.get("field"), str):
            try:
                ref = resolve(by["field"], "roles.by.field", ROLE_PREFIXES)
            except RuleError:
                ref = None
            if ref is not None and ref.spec.kind == CATEGORY:
                return (
                    f"roles.by.field: '{by['field']}' is a category; the format gives the two their roles by ordering them "
                    f"on a number, so roles by {ref.spec.name} cannot be written"
                )
    for where, written, _ in field_references(proposal):
        if _ARITHMETIC.search(written) or _DEPENDENCY.search(written.lower()):
            return f"{where}: a formula, {written!r}, where a field is required"
    for where, text in text_slots(proposal):
        if is_formula(text):
            return f"{where}: a formula, {text!r}, where a constant is required"
    return None


def review_flags(texts: Sequence[str]) -> list[str]:
    """The names of the :data:`REVIEW_PATTERNS` found in any of ``texts``."""
    lowered = " ".join(" ".join(text.lower().split()) for text in texts if text)
    return [name for name, pattern in REVIEW_PATTERNS if pattern.search(lowered)]


def as_full_rule(proposal: Mapping[str, Any], schema_version: int = 2) -> dict[str, Any]:
    """The proposal as the loader reads a rule file: the model's body under placeholder metadata."""
    body = {key: value for key, value in proposal.items() if key not in METADATA_KEYS}
    return {
        "schema_version": schema_version,
        "rule_id": _PLACEHOLDER_RULE_ID,
        "version": 1,
        "status": "candidate",
        "provenance": {
            "source_type": "stated",
            "source_ref": "a proposal being checked",
            "created_at": "2026-01-01",
            "author": "negsim.rulegen.validate",
            "notes": "",
            "validation_evidence": [],
        },
        **body,
    }


def validate_proposal(
    proposal: Any,
    visibility: Mapping[str, bool],
    texts: Sequence[str] = (),
    schemas: Optional[RuleSchemas] = None,
) -> Validation:
    """Categorise one proposed rule. ``texts`` are the words around it (a reason, the
    conversation) that are read, with its ``intent`` and any value written as text, for the
    manual-review flags."""
    if not isinstance(proposal, Mapping):
        return Validation(SCHEMA_ERROR, "schema", f"a rule is a JSON object, got {type(proposal).__name__}", review_flags=review_flags(texts))
    ignored = {key: proposal[key] for key in METADATA_KEYS if key in proposal}
    references = [written for _, written, _ in field_references(proposal)]
    flags = review_flags([str(proposal.get("intent", "")), *texts, *(text for _, text in text_slots(proposal))])

    def result(category: str, loader: Optional[str], message: str) -> Validation:
        return Validation(category, loader, message, references, ignored, flags)

    private = _needs_communication(proposal, visibility)
    if private is not None:
        return result(NEEDS_COMMUNICATION, private[0], private[1])
    limit = _format_limit(proposal)
    if limit is not None:
        return result(FORMAT_LIMIT, None, limit)
    try:
        rule = parse_rule(as_full_rule(proposal), schemas or _schemas(), "proposal")
    except RuleError as error:
        return result(LOADER_CATEGORIES.get(error.category, SCHEMA_ERROR), error.category, str(error))
    hidden = sorted(name for name in rule.needs() if not visibility.get(name, False))
    if hidden:
        return result(NEEDS_COMMUNICATION, "visibility", f"the rule reads {hidden}, which this session's people cannot see")
    return result(VALID, None, "loads, and both people can see everything it reads")
