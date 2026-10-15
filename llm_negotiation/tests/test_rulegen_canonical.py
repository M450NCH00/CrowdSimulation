"""Issue #30: the canonical form of a rule and its hash (``docs/rule-format.md``, section 13)."""

from __future__ import annotations

import copy
import json

import yaml

from negsim.configutil import PACKAGE_ROOT
from negsim.rules.canonical import (
    CANONICAL_KEYS,
    PROPOSAL_ID_LENGTH,
    canonical_form,
    canonical_hash,
    canonical_json,
    normalise_number,
    proposal_id,
)

RULE = yaml.safe_load((PACKAGE_ROOT / "rule_db" / "rules" / "younger_yields_head_on.v1.yaml").read_text(encoding="utf-8"))


def reordered(value):
    """The same mapping with its keys in reverse order, at every depth."""
    if isinstance(value, dict):
        return {key: reordered(value[key]) for key in reversed(list(value))}
    if isinstance(value, list):
        return [reordered(item) for item in value]
    return value


def test_key_order_does_not_change_the_hash():
    assert canonical_hash(reordered(RULE)) == canonical_hash(RULE)
    assert canonical_json(reordered(RULE)) == canonical_json(RULE)


def test_number_formatting_does_not_change_the_hash():
    written = copy.deepcopy(RULE)
    written["when"]["all"][0]["value"] = 6  # 6.0 in the file
    written["when"]["all"][1]["value"] = 20.0  # 20 in the file
    written["directive"]["yielder"]["responsibility_share"] = 1  # 1.0 in the file
    written["directive"]["other"]["responsibility_share"] = 0.000  # 0.0
    assert canonical_hash(written) == canonical_hash(RULE)
    assert normalise_number(0.1 + 0.2) == 0.3 and normalise_number(1e-13) == 1e-13
    assert normalise_number(True) is True and normalise_number("6") == "6"


def test_metadata_does_not_change_the_hash_and_what_the_rule_does_does():
    metadata = copy.deepcopy(RULE)
    metadata.update(rule_id="other_name", version=7, status="candidate", priority=999, description="x", intent="y")
    metadata["provenance"] = {"source_type": "stated"}
    assert canonical_hash(metadata) == canonical_hash(RULE)
    assert set(canonical_form(RULE)) == {"encounter", "when", "roles", "directive"}
    for change in (
        lambda rule: rule["directive"]["other"].update(responsibility_share=0.1),
        lambda rule: rule.update(encounter="crossing"),
        lambda rule: rule["when"]["all"][0].update(op="<"),
        lambda rule: rule["roles"]["by"].update(order="descending"),
        lambda rule: rule.update(expiry="passed"),  # stated, even at its default: written differently
        lambda rule: rule["when"]["all"].reverse(),  # the order of a group is kept
        lambda rule: rule["when"]["all"][1].update(value=20.0001),
    ):
        changed = copy.deepcopy(RULE)
        change(changed)
        assert canonical_hash(changed) != canonical_hash(RULE), change
    # Beyond 12 significant digits a difference is rounding: 20.000000000001 is 20.
    beyond = copy.deepcopy(RULE)
    beyond["when"]["all"][1]["value"] = 20.000000000001
    assert canonical_hash(beyond) == canonical_hash(RULE) and normalise_number(20.000000000001) == 20


def test_units_are_not_converted():
    in_degrees = {"encounter": "any", "when": {"field": "pair.heading_difference_rad", "op": ">", "value": 90, "unit": "deg"}}
    in_radians = {"encounter": "any", "when": {"field": "pair.heading_difference_rad", "op": ">", "value": 1.5707963267949, "unit": "rad"}}
    assert canonical_hash(in_degrees) != canonical_hash(in_radians)


def test_the_hash_and_the_id():
    digest = canonical_hash(RULE)
    assert len(digest) == 64 and int(digest, 16) >= 0
    assert proposal_id(RULE) == digest[:PROPOSAL_ID_LENGTH] and PROPOSAL_ID_LENGTH == 12
    assert CANONICAL_KEYS == ("encounter", "when", "roles", "directive", "expiry")
    assert json.loads(canonical_json(RULE))["roles"]["by"]["assign"] == ["yielder", "other"]


def test_anything_shaped_like_a_rule_has_a_hash_valid_or_not():
    assert len(canonical_hash({"directive": {"a": {"responsibility_share": "0.5 + age"}}, "roles": "everyone"})) == 64
    assert canonical_hash({}) == canonical_hash({"rule_id": "x"})  # nothing that a rule does: the empty form
    assert canonical_hash({"when": {"value": float("nan")}}) == canonical_hash({"when": {"value": float("nan")}})
