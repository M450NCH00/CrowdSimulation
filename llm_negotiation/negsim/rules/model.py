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
   one follower, and one side for the pair (``docs/derivations.md``, sections 9 to 11);
   and, from version 3, a rule that says who backs up says it of exactly one of two roles,
   and not of the role that goes first (``back_up``, section 17).

A role assignment that does not say what happens on a tie is refused on its own
(``no_tie_policy``), before the schema check, so that its reason is plain. Before even that, a
rule whose condition or role assignment (its tie policy included) names a person's group, or
anything derived from it, is refused as ``protected_attribute`` (issue #32): whatever else is
wrong with it, that is what it is counted as.

Four schema versions exist (``docs/rule-format.md``, sections 12, 14 and 15). Version 2 (issue
#30) adds the source type ``stated``, an ``intent`` in words and a ``screening`` list, for
rules a model generates. Version 3 (issue #32) adds the directive field ``back_up``, the four
passage fields, and true or false as a comparison's value. Version 4 (issue #108) adds roles by a
condition (:class:`ConditionRoles`), own-only conditions (``own_when``: :class:`OwnWhen`, read on
a person's own private factors and switching on only that person's own movement; anything else
is refused as ``own_only_scope``, before the schema check), the directive field ``steps`` (a plan
in Step 1's vocabulary, carried out by the plan executor), and the three visible attributes. A
file is read against the schema of its own version, and may read only that version's fields, so a
version 1, 2 or 3 rule is read exactly as before.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field, replace
from typing import Any, Iterable, Iterator, Mapping, Optional

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
from .fields import (
    BOOLEAN,
    CATEGORY,
    OWN_ATTRACTIVENESS,
    OWN_PREFIXES,
    PROTECTED_NAMES,
    ROLE_PREFIXES,
    FieldRef,
    protected_attribute_of,
    protected_reference,
    resolve,
)
from .jsonschema_subset import Validator
from .snapshot import PairSnapshot

SCHEMA_VERSION = 1
#: Every version of the rule format, oldest first; a rule names its own in ``schema_version``.
SCHEMA_VERSIONS = (1, 2, 3, 4)
LATEST_SCHEMA_VERSION = SCHEMA_VERSIONS[-1]
#: The single role of a symmetric rule: both agents get its directive.
SYMMETRIC_ROLE = "both"
TIE_NO_MATCH = "no_match"
EXPIRY_PASSED, EXPIRY_OUT_OF_RANGE = "passed", "out_of_range"
STATUSES = ("test_seed", "candidate", "validated", "rejected", "retired")
#: Version 4 (issue #108): where a role by a condition may read, and what an own-only condition may
#: switch on. Only the person's own movement: never what both must agree on (a side, a share, an
#: order, backing up).
ROLE_CONDITION_PREFIXES = ("agent", "pair")
OWN_ONLY_FIELDS = ("speed_scale", "clearance_margin", "steps")
#: The events a rule's step may end at (issue #108; Step 1's ``other_passes``).
STEP_EVENTS = ("other_passes",)
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

    def comparisons(self) -> Iterator[Any]:
        return iter(())


@dataclass(frozen=True)
class ConditionRoles:
    """Version 4 (issue #108): the person for whom ``when`` holds gets ``assign[0]``, the other
    ``assign[1]``. When it holds for both or for neither, the rule does not match (``no_match``);
    a missing value makes it not hold, as any comparison on a missing value is false."""

    when: Condition
    assign: tuple[str, str]
    tie: str

    def roles(self, snapshot: PairSnapshot) -> Optional[tuple[str, str]]:
        first, second = self.when.evaluate_for(snapshot, 0), self.when.evaluate_for(snapshot, 1)
        if first == second:
            return None
        return self.assign if first else (self.assign[1], self.assign[0])

    def comparisons(self) -> Iterator[Any]:
        return self.when.comparisons()


@dataclass(frozen=True)
class OwnWhen:
    """Version 4 (issue #108): a role's own-only condition. While ``when`` holds for the person (on
    their own private factors and the pair's fields), ``speed_scale`` and ``clearance_margin`` (if
    given) replace the role's, and ``steps`` (if given) are that person's plan."""

    when: Condition
    speed_scale: Optional[float]
    clearance_margin: Optional[float]
    steps: Optional[tuple[Any, ...]]

    def apply(self, directive: AvoidanceDirective, steps: Optional[tuple[Any, ...]]) -> tuple[AvoidanceDirective, Optional[tuple[Any, ...]]]:
        changes = {name: value for name, value in (("speed_scale", self.speed_scale), ("clearance_margin", self.clearance_margin)) if value is not None}
        return (replace(directive, **changes) if changes else directive), (self.steps if self.steps is not None else steps)


@dataclass(frozen=True)
class Match:
    """A rule that matched a snapshot: the role and the directive of each of its two agents,
    in the snapshot's order."""

    rule: "Rule"
    agents: tuple[int, int]
    roles: tuple[str, str]
    directives: tuple[AvoidanceDirective, AvoidanceDirective]
    #: Version 4 (issue #108): each agent's plan (parsed Step 1 steps), or ``None``.
    steps: tuple[Optional[tuple[Any, ...]], Optional[tuple[Any, ...]]] = (None, None)

    def directive_of(self, agent_id: int) -> AvoidanceDirective:
        return self.directives[self.agents.index(agent_id)]

    def steps_of(self, agent_id: int) -> Optional[tuple[Any, ...]]:
        return self.steps[self.agents.index(agent_id)]

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
    roles: Optional[RoleAssignment | ConditionRoles]  # None for a symmetric rule
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
    #: Version 4 (issue #108): each role's plan, and each role's own-only condition, by role.
    steps: Mapping[str, tuple[Any, ...]] = field(default_factory=dict)
    own_when: Mapping[str, OwnWhen] = field(default_factory=dict)

    @property
    def key(self) -> str:
        """``rule_id@version``: how logs name a rule version."""
        return f"{self.rule_id}@{self.version}"

    @property
    def role_names(self) -> tuple[str, ...]:
        return (SYMMETRIC_ROLE,) if self.roles is None else self.roles.assign

    @property
    def has_steps(self) -> bool:
        """Whether following the rule can give someone a plan (version 4)."""
        return bool(self.steps) or any(own.steps for own in self.own_when.values())

    def comparisons(self) -> list[Any]:
        """Every comparison the rule makes: its condition, a role by a condition, and every own-only
        condition (version 4)."""
        found = list(self.when.comparisons())
        if self.roles is not None:
            found += list(self.roles.comparisons())
        for own in self.own_when.values():
            found += list(own.when.comparisons())
        return found

    def field_refs(self) -> list[FieldRef]:
        refs = [comparison.ref for comparison in self.comparisons()]
        if isinstance(self.roles, RoleAssignment):
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
                return None  # a tie, a value that cannot be ordered, or both or neither meet the condition: no_match
        if not self.steps and not self.own_when:
            return Match(self, snapshot.agents, roles, (self.directives[roles[0]], self.directives[roles[1]]))
        directives, plans = [], []
        for index, role in enumerate(roles):
            directive, steps = self.directives[role], self.steps.get(role)
            own = self.own_when.get(role)
            if own is not None and own.when.evaluate_for(snapshot, index):
                directive, steps = own.apply(directive, steps)
            directives.append(directive)
            plans.append(steps)
        return Match(self, snapshot.agents, roles, (directives[0], directives[1]), (plans[0], plans[1]))

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


def _strings(value: Any, path: str) -> Iterator[tuple[str, str]]:
    """Every key and string value under ``value``, with where it is."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield f"{path}.{key}", str(key)
            yield from _strings(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _strings(item, f"{path}[{index}]")


def _own_attractiveness(where: str, text: str) -> bool:
    """Whether ``text`` at ``where`` is the one place a version 4 rule may read perceived
    attractiveness: ``self.finds_other_attractive`` as the field of a comparison inside a role's
    own-only condition (issue #108)."""
    return text == OWN_ATTRACTIVENESS and where.startswith("directive.") and ".own_when.when" in where and where.endswith(".field")


def protected_part(raw: Mapping[str, Any], terms: Iterable[str] = (), schema_version: Optional[int] = None) -> Optional[tuple[str, str, str]]:
    """Where a written rule names a person's group, or (issue #61) perceived attractiveness:
    ``(where, the text, the protected word)``.

    Every key and string of its condition (``when``) and of its roles (the role assignment:
    its field, its role names and its tie policy) is read, in its written form, before the
    rule is checked against anything else (issue #32). From version 4 (issue #108) its
    directive is read too, since an own-only condition lives there; the one string let through is
    ``self.finds_other_attractive`` as a field of an own-only condition. ``schema_version`` is the
    rule's, if known; a rule that does not say is read as version 4 is when it says 4.
    """
    terms = tuple(terms)
    if schema_version is None:
        written = raw.get("schema_version")
        schema_version = written if isinstance(written, int) and not isinstance(written, bool) else None
    later = schema_version is not None and schema_version >= 4
    for part in ("when", "roles", "directive") if later else ("when", "roles"):
        if part in raw:
            for where, text in _strings(raw[part], part):
                if later and _own_attractiveness(where, text):
                    continue
                word = protected_reference(text, terms)
                if word is not None:
                    return where, text, word
    return None


def own_only_scope(raw: Mapping[str, Any], where: str) -> None:
    """Refuse an own-only condition that would switch on anything but the person's own movement
    (version 4, issue #108): checked before the schema, so that the reason is plain."""
    directive = raw.get("directive")
    if not isinstance(directive, Mapping):
        return
    for role, entry in directive.items():
        own = entry.get("own_when") if isinstance(entry, Mapping) else None
        then = own.get("then") if isinstance(own, Mapping) else None
        if not isinstance(then, Mapping):
            continue
        other = sorted(str(name) for name in then if name not in OWN_ONLY_FIELDS)
        if other:
            raise RuleError(
                "own_only_scope",
                f"{where}.directive.{role}.own_when.then: {other} cannot be switched on by an own-only condition. A person's own "
                f"private factors may change only their own movement ({list(OWN_ONLY_FIELDS)}), never what the two must agree "
                "on (a side, a share, an order, backing up), which the other cannot know (docs/rule-format.md, section 15).",
            )


def parse_rule(raw: Any, validator: Validator, where: str = "rule", terms: Iterable[str] = ()) -> Rule:
    """A :class:`Rule` from its written form, or a :class:`RuleError` saying why not.

    ``terms`` are more words that name a person's group, beside the attribute's name and the
    default labels: a rule-generation session's labels and the words it introduced groups with.
    """
    raw = normalise(raw)
    if not isinstance(raw, Mapping):
        raise RuleError("schema", f"{where}: a rule is a mapping, got {type(raw).__name__}")
    found = protected_part(raw, terms)
    if found is not None:
        part, text, word = found
        raise RuleError(
            "protected_attribute",
            f"{where}.{part}: {text!r} refers to {PROTECTED_NAMES[protected_attribute_of(word)]} ({word!r}), which no rule "
            "may read, in a condition, a role assignment or a tie policy (docs/rule-format.md, section 14). The attempt is "
            "kept, as data.",
        )
    later = isinstance(raw.get("schema_version"), int) and raw["schema_version"] >= 4
    if later:
        own_only_scope(raw, where)
    roles_raw = raw.get("roles")
    if isinstance(roles_raw, Mapping):
        for key in ("by", "by_condition") if later else ("by",):
            if isinstance(roles_raw.get(key), Mapping) and "tie" not in roles_raw[key]:
                raise RuleError(
                    "no_tie_policy",
                    f"{where}.roles.{key}: says how to give the two agents their roles but not what happens when they tie. "
                    f"Every role assignment must state its tie policy; the one offered is 'tie: {TIE_NO_MATCH}' "
                    "(on a tie the rule does not apply).",
                )
    problems = validator.errors(raw)
    if problems:
        raise RuleError("schema", f"{where} does not fit the rule schema:\n  " + "\n  ".join(problems))

    version = raw["schema_version"]
    when = parse_condition(raw["when"], f"{where}.when", version, terms)
    roles: Optional[RoleAssignment | ConditionRoles] = None
    if isinstance(raw["roles"], Mapping) and "by_condition" in raw["roles"]:
        roles = _condition_roles(raw["roles"]["by_condition"], f"{where}.roles.by_condition", version, terms)
    elif raw["roles"] != "symmetric":
        roles = _role_assignment(raw["roles"]["by"], f"{where}.roles.by", version, terms)
    names = (SYMMETRIC_ROLE,) if roles is None else roles.assign
    written = raw["directive"]
    if set(written) != set(names):
        raise RuleError(
            "roles",
            f"{where}.directive: needs one entry per role, named {sorted(names)}, got {sorted(written)}"
            + (" (a symmetric rule has the single role 'both')" if roles is None else ""),
        )
    directives, steps, own_when = {}, {}, {}
    for name in names:
        entry = dict(written[name] or {})
        if "steps" in entry:
            steps[name] = parse_steps(entry.pop("steps"), f"{where}.directive.{name}.steps")
        if "own_when" in entry:
            own_when[name] = _own_when(entry.pop("own_when"), f"{where}.directive.{name}.own_when", version, terms)
        try:
            directives[name] = AvoidanceDirective.from_mapping(entry, f"{where}.directive.{name}", base=PLAIN_ORCA)
        except ConfigError as exc:
            raise RuleError("value", str(exc)) from exc
    check_consistency(names, directives, where, {name: tuple(written[name] or {}) for name in names})

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
        steps=steps,
        own_when=own_when,
    )


def _condition_roles(raw: Mapping[str, Any], where: str, schema_version: int, terms: Iterable[str] = ()) -> ConditionRoles:
    if SYMMETRIC_ROLE in raw["assign"]:
        raise RuleError("roles", f"{where}.assign: '{SYMMETRIC_ROLE}' is the role of a symmetric rule; name the two roles otherwise")
    when = parse_condition(raw["when"], f"{where}.when", schema_version, terms, ROLE_CONDITION_PREFIXES)
    if not any(comparison.ref.prefix == "agent" for comparison in when.comparisons()):
        raise RuleError(
            "roles",
            f"{where}.when: reads no agent. field, so it holds for both people or for neither and can never give them "
            "different roles",
        )
    return ConditionRoles(when, (raw["assign"][0], raw["assign"][1]), raw["tie"])


def _own_when(raw: Mapping[str, Any], where: str, schema_version: int, terms: Iterable[str] = ()) -> OwnWhen:
    when = parse_condition(raw["when"], f"{where}.when", schema_version, terms, OWN_PREFIXES)
    then = raw["then"]
    values = {}
    for name in ("speed_scale", "clearance_margin"):
        if name in then:
            values[name] = float(then[name])
    steps = parse_steps(then["steps"], f"{where}.then.steps") if "steps" in then else None
    return OwnWhen(when, values.get("speed_scale"), values.get("clearance_margin"), steps)


def parse_steps(raw: Any, where: str) -> tuple[Any, ...]:
    """A rule's ``steps`` (version 4, issue #108), read with Step 1's own step parser
    (``negsim.resolution.reply``), so that the limits are Step 1's: a turn of 0 to 90 degrees, a
    sidestep of up to 3 m, a positive back-up, a step that does not back up or step aside has an
    ``until``. Speeds are clipped to each person's own maximum when the plan is carried out, and a
    start or end at a distance is read against the person the rule matched them with."""
    import math

    from ..negotiation.parsing import TurnParseError
    from ..resolution.reply import ReplyContext, _step
    from ..resolution.view import CONDITION_TALK

    context = ReplyContext(
        CONDITION_TALK, math.inf, STEP_EVENTS, math.inf, later_step_start=True, until_at_distance=True, sidestep=True,
    )
    flags: list[str] = []
    try:
        parsed = tuple(_step(index, dict(item), context, flags) for index, item in enumerate(raw))
    except TurnParseError as exc:
        raise RuleError("steps", f"{where}: {exc}") from exc
    if flags:
        raise RuleError("steps", f"{where}: not Step 1's step vocabulary: {flags}")
    return parsed


def _role_assignment(raw: Mapping[str, Any], where: str, schema_version: Optional[int] = None, terms: Iterable[str] = ()) -> RoleAssignment:
    ref = resolve(raw["field"], f"{where}.field", ROLE_PREFIXES, schema_version, terms)
    if ref.spec.kind in (CATEGORY, BOOLEAN):
        kind = "a category" if ref.spec.kind == CATEGORY else "true or false"
        raise RuleError(
            "operator", f"{where}.field: roles are given by ordering the two agents on a number; '{ref.written}' is {kind}"
        )
    if SYMMETRIC_ROLE in raw["assign"]:
        raise RuleError("roles", f"{where}.assign: '{SYMMETRIC_ROLE}' is the role of a symmetric rule; name the two roles otherwise")
    tie_within = 0.0
    if "tie_within" in raw:
        tie_within = ref.spec.convert(raw["tie_within"], raw.get("unit"), f"{where}.tie_within")
    elif "unit" in raw:
        raise RuleError("unit", f"{where}.unit: states the unit of tie_within, which is not given")
    return RoleAssignment(ref, raw["order"], (raw["assign"][0], raw["assign"][1]), raw["tie"], tie_within)


def check_consistency(
    roles: tuple[str, ...],
    directives: Mapping[str, AvoidanceDirective],
    where: str,
    stated: Optional[Mapping[str, Iterable[str]]] = None,
) -> None:
    """The consistency rules, for the two agents of a pair that follows the rule.

    A symmetric rule gives both agents the same directive, so it is checked as a pair of
    two identical directives. ``stated`` gives the directive fields each role's entry writes:
    a rule that writes ``back_up`` for any role is checked for it (issue #32).
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
    if stated is not None and any("back_up" in stated[name] for name in roles):
        backs = (first.back_up, second.back_up)
        if len(roles) == 1:
            raise RuleError(
                "back_up",
                f"{where}.directive: {label} says back_up: {str(first.back_up).lower()} for both people, so both would back "
                "up, or neither would. A rule that says who backs up gives back_up true to exactly one of two roles "
                "(docs/derivations.md, section 17).",
            )
        if backs == (True, True):
            raise RuleError(
                "back_up",
                f"{where}.directive: {label} both back up. Inside a single-file passage exactly one backs out and the "
                "other goes on; with both backing out, neither gets through (docs/derivations.md, section 17).",
            )
        if backs == (False, False):
            raise RuleError(
                "back_up",
                f"{where}.directive: {label} both go on (back_up false for both). Inside a single-file passage neither can "
                "pass the other: a rule that says who backs up makes exactly one of them back up (docs/derivations.md, "
                "section 17).",
            )
    for name in roles:
        if directives[name].back_up and directives[name].passage_order == ORDER_LEADER:
            raise RuleError(
                "back_up",
                f"{where}.directive.{name}: backs up and goes first (passage_order leader). The one that backs out lets the "
                "other go first (docs/derivations.md, section 17).",
            )
    sides = {first.side_preference, second.side_preference} - {SIDE_NONE}
    if len(sides) > 1:
        raise RuleError(
            "side",
            f"{where}.directive: {label} are told to pass on opposite sides, {sorted(sides)}. Both would step the same "
            "way and stay on a collision course; a pair has one side (docs/derivations.md, section 10).",
        )
