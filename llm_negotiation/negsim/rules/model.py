"""A rule: when it applies, who gets which role, and what each role is told.

``docs/rule-format.md`` describes the format; this module turns the written form of one
rule version into a :class:`Rule` and refuses it, with a :class:`RuleError` naming the
category, if it is not usable. In this order:

1. the structure, against the versioned JSON Schema (``rule_db/schema/``);
2. every field, against the list of fields both agents can see (``fields.py``), with
   its operator, value and unit;
3. the roles and the directives: one directive per role, named as the roles are;
4. the consistency rules, which keep ORCA's guarantee for a pair that follows the rule:
   responsibility shares that sum to at least 1, passage orders that are one leader and
   one follower, and one side for the pair (``docs/derivations.md``, sections 9 to 11).

A role assignment that does not say what happens on a tie is refused on its own
(``no_tie_policy``), before the schema check, so that its reason is plain.

Two schema versions exist (``docs/rule-format.md``, section 12). Version 2 (issue #30) adds
the source type ``stated``, an ``intent`` in words and a ``screening`` list, for rules a
model generates; a version 1 file is read against the version 1 schema, as before. What a
rule *does* is the same in both, so everything after the schema check is shared.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from ..avoidance.directives import (
    ORDER_FOLLOWER,
    ORDER_LEADER,
    ORDER_NONE,
    PLAIN_ORCA,
    SHARE_SUM_TOLERANCE,
    SIDE_NONE,
    AvoidanceDirective,
)
from ..configutil import ConfigError
from .conditions import Condition, parse_condition
from .errors import RuleError
from .fields import CATEGORY, ROLE_PREFIXES, FieldRef, resolve
from .jsonschema_subset import Validator
from .snapshot import PairSnapshot

SCHEMA_VERSION = 1
#: Every version of the rule format, oldest first; a rule names its own in ``schema_version``.
SCHEMA_VERSIONS = (1, 2)
LATEST_SCHEMA_VERSION = SCHEMA_VERSIONS[-1]
#: The single role of a symmetric rule: both agents get its directive.
SYMMETRIC_ROLE = "both"
TIE_NO_MATCH = "no_match"
EXPIRY_PASSED, EXPIRY_OUT_OF_RANGE = "passed", "out_of_range"
STATUSES = ("test_seed", "candidate", "validated", "rejected", "retired")
#: The statuses with which a rule may be switched on in an experiment.
USABLE_STATUSES = ("test_seed", "candidate", "validated")


@dataclass(frozen=True)
class RoleAssignment:
    """Order the two agents by an agent-level number and give them the two roles in turn.

    ``ascending``: the agent with the smaller value gets ``assign[0]``. Two values no more
    than ``tie_within`` apart (in the field's unit; 0 means exactly equal) are a tie, and
    a missing value cannot be ordered; on either the rule does not match (``no_match``).
    """

    ref: FieldRef
    order: str
    assign: tuple[str, str]
    tie: str
    tie_within: float

    def roles(self, snapshot: PairSnapshot) -> Optional[tuple[str, str]]:
        """The roles of the snapshot's two agents, in its order; ``None`` on a tie or a gap."""
        name = self.ref.spec.name
        first, second = snapshot.agent_value(0, name), snapshot.agent_value(1, name)
        if first is None or second is None or abs(first - second) <= self.tie_within:
            return None
        first_leads = first < second if self.order == "ascending" else first > second
        return self.assign if first_leads else (self.assign[1], self.assign[0])


@dataclass(frozen=True)
class Match:
    """A rule that matched a snapshot: the role and the directive of each of its two agents,
    in the snapshot's order."""

    rule: "Rule"
    agents: tuple[int, int]
    roles: tuple[str, str]
    directives: tuple[AvoidanceDirective, AvoidanceDirective]

    def directive_of(self, agent_id: int) -> AvoidanceDirective:
        return self.directives[self.agents.index(agent_id)]

    def role_of(self, agent_id: int) -> str:
        return self.roles[self.agents.index(agent_id)]


@dataclass(frozen=True)
class Rule:
    """One version of one rule. Immutable: a change is a new version (``database.py``)."""

    rule_id: str
    version: int
    status: str
    provenance: Mapping[str, Any]
    description: str
    encounter: str
    when: Condition
    roles: Optional[RoleAssignment]  # None for a symmetric rule
    directives: Mapping[str, AvoidanceDirective]  # by role
    set_fields: Mapping[str, tuple[str, ...]]  # by role: the directive fields the rule itself sets
    priority: int
    expiry: str
    written: Mapping[str, Any] = field(repr=False, compare=False)
    source: str = ""
    sha256: Optional[str] = None
    schema_version: int = SCHEMA_VERSION
    #: Version 2: what the rule is meant to do, in words. Never executed.
    intent: str = ""
    #: Version 2: the results of replaying and screening the rule (issue #30, Part 9).
    screening: tuple[Mapping[str, Any], ...] = field(default=(), compare=False)

    @property
    def key(self) -> str:
        """``rule_id@version``: how logs name a rule version."""
        return f"{self.rule_id}@{self.version}"

    @property
    def role_names(self) -> tuple[str, ...]:
        return (SYMMETRIC_ROLE,) if self.roles is None else self.roles.assign

    def field_refs(self) -> list[FieldRef]:
        refs = [comparison.ref for comparison in self.when.comparisons()]
        if self.roles is not None:
            refs.append(self.roles.ref)
        return refs

    def needs(self) -> set[str]:
        """The visibility switches the rule needs on: those of every field it reads, and
        those of the encounter class, which every rule reads."""
        needed = {"speed", "size"}
        for ref in self.field_refs():
            needed.update(ref.spec.needs)
        return needed

    def applies_to(self, encounter_class: Optional[str]) -> bool:
        if encounter_class is None or encounter_class == "none":
            return False
        return self.encounter == "any" or self.encounter == encounter_class

    def match(self, snapshot: PairSnapshot) -> Optional[Match]:
        """The roles and directives this rule gives the snapshot's pair, or ``None``."""
        if not self.applies_to(snapshot.encounter_class) or not self.when.evaluate(snapshot):
            return None
        if self.roles is None:
            roles = (SYMMETRIC_ROLE, SYMMETRIC_ROLE)
        else:
            roles = self.roles.roles(snapshot)
            if roles is None:
                return None  # a tie, or a value that cannot be ordered: no_match
        return Match(self, snapshot.agents, roles, (self.directives[roles[0]], self.directives[roles[1]]))

    def describe(self) -> dict[str, Any]:
        """What a run's config records about an enabled rule."""
        return {
            "rule_id": self.rule_id,
            "version": self.version,
            "schema_version": self.schema_version,
            "status": self.status,
            "encounter": self.encounter,
            "priority": self.priority,
            "expiry": self.expiry,
            "sha256": self.sha256,
        }


# --- reading a rule ----------------------------------------------------------------------------


def normalise(raw: Any) -> Any:
    """YAML reads an unquoted date as a date; the schema wants text. Nothing else changes."""
    if isinstance(raw, (_dt.date, _dt.datetime)):
        return raw.isoformat()[:10]
    if isinstance(raw, Mapping):
        return {key: normalise(value) for key, value in raw.items()}
    if isinstance(raw, list):
        return [normalise(item) for item in raw]
    return raw


def parse_rule(raw: Any, validator: Validator, where: str = "rule") -> Rule:
    """A :class:`Rule` from its written form, or a :class:`RuleError` saying why not."""
    raw = normalise(raw)
    if not isinstance(raw, Mapping):
        raise RuleError("schema", f"{where}: a rule is a mapping, got {type(raw).__name__}")
    roles_raw = raw.get("roles")
    if isinstance(roles_raw, Mapping) and isinstance(roles_raw.get("by"), Mapping) and "tie" not in roles_raw["by"]:
        raise RuleError(
            "no_tie_policy",
            f"{where}.roles.by: says how to order the two agents but not what happens when they tie. "
            f"Every role assignment must state its tie policy; the one offered is 'tie: {TIE_NO_MATCH}' "
            "(on a tie the rule does not apply).",
        )
    problems = validator.errors(raw)
    if problems:
        raise RuleError("schema", f"{where} does not fit the rule schema:\n  " + "\n  ".join(problems))

    when = parse_condition(raw["when"], f"{where}.when")
    roles = None if raw["roles"] == "symmetric" else _role_assignment(raw["roles"]["by"], f"{where}.roles.by")
    names = (SYMMETRIC_ROLE,) if roles is None else roles.assign
    written = raw["directive"]
    if set(written) != set(names):
        raise RuleError(
            "roles",
            f"{where}.directive: needs one entry per role, named {sorted(names)}, got {sorted(written)}"
            + (" (a symmetric rule has the single role 'both')" if roles is None else ""),
        )
    directives = {}
    for name in names:
        try:
            directives[name] = AvoidanceDirective.from_mapping(written[name] or {}, f"{where}.directive.{name}", base=PLAIN_ORCA)
        except ConfigError as exc:
            raise RuleError("value", str(exc)) from exc
    check_consistency(names, directives, where)

    return Rule(
        rule_id=raw["rule_id"],
        version=raw["version"],
        status=raw["status"],
        provenance=dict(raw["provenance"]),
        description=" ".join(str(raw.get("description", "")).split()),
        encounter=raw["encounter"],
        when=when,
        roles=roles,
        directives=directives,
        set_fields={name: tuple(sorted(written[name] or {})) for name in names},
        priority=raw["priority"],
        expiry=raw.get("expiry", EXPIRY_PASSED),
        written=raw,
        schema_version=raw["schema_version"],
        intent=" ".join(str(raw.get("intent", "")).split()),
        screening=tuple(raw.get("screening") or ()),
    )


def _role_assignment(raw: Mapping[str, Any], where: str) -> RoleAssignment:
    ref = resolve(raw["field"], f"{where}.field", ROLE_PREFIXES)
    if ref.spec.kind == CATEGORY:
        raise RuleError(
            "operator", f"{where}.field: roles are given by ordering the two agents on a number; '{ref.written}' is a category"
        )
    if SYMMETRIC_ROLE in raw["assign"]:
        raise RuleError("roles", f"{where}.assign: '{SYMMETRIC_ROLE}' is the role of a symmetric rule; name the two roles otherwise")
    tie_within = 0.0
    if "tie_within" in raw:
        tie_within = ref.spec.convert(raw["tie_within"], raw.get("unit"), f"{where}.tie_within")
    elif "unit" in raw:
        raise RuleError("unit", f"{where}.unit: states the unit of tie_within, which is not given")
    return RoleAssignment(ref, raw["order"], (raw["assign"][0], raw["assign"][1]), raw["tie"], tie_within)


def check_consistency(roles: tuple[str, ...], directives: Mapping[str, AvoidanceDirective], where: str) -> None:
    """The three consistency rules, for the two agents of a pair that follows the rule.

    A symmetric rule gives both agents the same directive, so it is checked as a pair of
    two identical directives.
    """
    first, second = (directives[roles[0]], directives[roles[-1]])
    label = f"'{roles[0]}' and '{roles[-1]}'" if len(roles) == 2 else f"'{roles[0]}' (given to both agents)"

    total = first.responsibility_share + second.responsibility_share
    if total < 1.0 - SHARE_SUM_TOLERANCE:
        raise RuleError(
            "reciprocity",
            f"{where}.directive: the responsibility shares of {label} sum to {total:g}, less than 1. ORCA keeps a pair "
            "free of collisions for its time horizon only if the two shares sum to at least 1 "
            "(docs/derivations.md, section 9).",
        )
    orders = (first.passage_order, second.passage_order)
    if orders != (ORDER_NONE, ORDER_NONE) and sorted(orders) != [ORDER_FOLLOWER, ORDER_LEADER]:
        raise RuleError(
            "passage_order",
            f"{where}.directive: the passage orders of {label} are {list(orders)}. Passage order must be "
            "complementary: one leader and one follower, or neither set (docs/derivations.md, section 11).",
        )
    sides = {first.side_preference, second.side_preference} - {SIDE_NONE}
    if len(sides) > 1:
        raise RuleError(
            "side",
            f"{where}.directive: {label} are told to pass on opposite sides, {sorted(sides)}. Both would step the same "
            "way and stay on a collision course; a pair has one side (docs/derivations.md, section 10).",
        )
