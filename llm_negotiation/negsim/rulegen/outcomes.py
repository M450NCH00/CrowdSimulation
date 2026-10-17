"""What each session came to, person by person: rows for analysis by group (issue #32, Part 1.5).

Whether a model treats people differently by their group need not show in what a rule *reads*
(no rule may read a group, ``rule-format.md`` section 14): it can show in who gives way. So
every session gets one row of ``outcomes.jsonl`` that says, for each of its two people,

* in condition A, **who proposed what and who conceded**: how many proposals each made, whose
  proposal was accepted, and who accepted the other's (``conceded_by``); who said that no rule
  is possible;
* in both conditions, **what the agreed or stated rule does to each of them on the case's own
  pair**: the rule is loaded and matched on the case's snapshot, with the session's people in
  it (their ages and genders as far as the session shows them), and the row gives each person's
  role and directive, **who got the larger responsibility share**, who goes first through a
  single-file passage, and who backs up;

beside everything to stratify by: the cell of the design, each person's group (issue #32) and
whether it was shown, and the demographics. Nothing here judges an outcome.

The rule's effect is read on the snapshot the case recorded, not on a run: it says what the
rule tells these two people at that moment. Replay (``replay.py``) says what then happens.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

from ..rules.errors import RuleError
from ..rules.model import parse_rule
from ..rules.snapshot import PairSnapshot
from .validate import _schemas, as_full_rule

OUTCOMES_FILE = "outcomes.jsonl"
#: Who got the larger responsibility share when the two are given the same.
EQUAL = "equal"


def case_snapshot(case: Mapping[str, Any], session: Mapping[str, Any]) -> PairSnapshot:
    """The case's shared snapshot, with the session's people in it.

    The case's snapshot was taken in a run without personas. Each person's age and gender are
    put in where the session shows them (its ``visibility``), and the age difference with them;
    nothing else changes. A person's group is never put in: no rule may read it.
    """
    taken = case["snapshot"]
    agents = (int(taken["agents"][0]), int(taken["agents"][1]))
    visibility, personas = session["visibility"], session["personas"]
    values = []
    for agent in agents:
        entry = dict(taken["agent"][str(agent)])
        person = personas.get(str(agent)) or personas.get(agent) or {}
        entry["age"] = person.get("age") if visibility.get("age") else None
        entry["gender"] = person.get("gender") if visibility.get("gender") else None
        values.append(entry)
    pair = dict(taken["pair"])
    ages = [entry["age"] for entry in values]
    pair["age_difference_years"] = abs(ages[0] - ages[1]) if None not in ages else None
    return PairSnapshot(taken["step"], taken["time_s"], agents, pair, (values[0], values[1]))


def rule_effect(
    proposal: Any,
    case: Mapping[str, Any],
    session: Mapping[str, Any],
    schema_version: int = 2,
    terms: Sequence[str] = (),
) -> dict[str, Any]:
    """What ``proposal`` tells each of the session's two people on the case's own pair.

    ``loads`` false (with the loader's ``reason``) when the rule cannot be loaded; ``matches``
    false when it loads but does not apply to the pair (its condition does not hold, or its
    role assignment ties). Otherwise each person's ``role`` and ``directive``, and, keyed by
    agent: ``larger_share`` (or ``"equal"``), ``goes_first`` (the leader its passage orders
    name, or the one that does not back up) and ``backs_up``.
    """
    effect: dict[str, Any] = {
        "loads": False, "reason": None, "matches": False, "roles": None, "directives": None,
        "larger_share": None, "goes_first": None, "backs_up": None,
    }
    try:
        rule = parse_rule(as_full_rule(proposal, schema_version), _schemas(), "proposal", terms)
    except RuleError as error:
        effect["reason"] = error.category
        return effect
    effect["loads"] = True
    match = rule.match(case_snapshot(case, session))
    if match is None:
        return effect
    first, second = match.agents
    shares = {agent: match.directive_of(agent).responsibility_share for agent in match.agents}
    effect.update(
        matches=True,
        roles={str(agent): match.role_of(agent) for agent in match.agents},
        directives={str(agent): match.directive_of(agent).as_dict() for agent in match.agents},
        larger_share=EQUAL if shares[first] == shares[second] else max(shares, key=shares.get),
    )
    backers = [agent for agent in match.agents if match.directive_of(agent).back_up]
    leaders = [agent for agent in match.agents if match.directive_of(agent).passage_order == "leader"]
    if len(backers) == 1:
        effect["backs_up"] = backers[0]
        effect["goes_first"] = second if backers[0] == first else first
    elif len(leaders) == 1:
        effect["goes_first"] = leaders[0]
    return effect


def outcome_row(
    record: Mapping[str, Any],
    case: Mapping[str, Any],
    validations: Sequence[Mapping[str, Any]] = (),
    schema_version: int = 2,
    terms: Sequence[str] = (),
) -> dict[str, Any]:
    """The row of one session (``outcomes.jsonl``; ``docs/log-schema.md``). ``schema_version``
    is the rule format the session's prompt described, and ``terms`` the words its groups were
    introduced with, as for validation."""
    session = record["session"]
    cell, personas = session["cell"], session["personas"]
    agents = [int(agent) for agent in session["agents"]]
    groups = {str(agent): (personas.get(str(agent)) or {}).get("ethnic_group") for agent in agents}
    row: dict[str, Any] = {
        "session_id": session["session_id"],
        "condition": record["condition"],
        "case_id": session["case_id"],
        "scenario": case["scenario"]["type"],
        "repeat": session["repeat"],
        "cell": dict(cell),
        "agents": agents,
        "first": session["first"],
        "demographics_visible": bool(cell["demographics_visible"]),
        "groups_on": any(label is not None for label in groups.values()),
        "group_pair": cell.get("group_pair"),
        "label_rotation": cell.get("label_rotation"),
        "ethnicity_visible": cell.get("ethnicity_visible"),
        "framing": session.get("framing"),
        "people": {
            str(agent): {
                "age": (personas.get(str(agent)) or {}).get("age"),
                "gender": (personas.get(str(agent)) or {}).get("gender"),
                "urgency": (personas.get(str(agent)) or {}).get("urgency"),
                "ethnic_group": groups[str(agent)],
            }
            for agent in agents
        },
        "outcome": record["outcome"],
        "proposals_by": None,
        "proposed_by": None,
        "conceded_by": None,
        "said_no_rule_possible": None,
        "rule_hash": None,
        "category": None,
        "effect": None,
    }
    rule: Optional[Mapping[str, Any]] = None
    if record["condition"] == "negotiated":
        made = [proposal["proposer"] for proposal in record["proposals"]]
        row["proposals_by"] = {str(agent): made.count(agent) for agent in agents}
        row["said_no_rule_possible"] = sorted({turn["speaker"] for turn in record["turns"] if turn.get("no_rule_possible")})
        agreement = record.get("agreement")
        if record["outcome"] == "agreed" and agreement:
            row["proposed_by"], row["conceded_by"] = agreement["proposed_by"], agreement["accepted_by"]
            rule, row["rule_hash"] = agreement["rule"], agreement["canonical_hash"]
    elif record["outcome"] == "stated":
        rule, row["rule_hash"] = record["rule"], record["canonical_hash"]
    if rule is not None:
        mine = [entry for entry in validations if entry["session_id"] == session["session_id"] and entry["agreed"]]
        row["category"] = mine[0]["category"] if mine else None
        row["effect"] = rule_effect(rule, case, session, schema_version, terms)
    return row
