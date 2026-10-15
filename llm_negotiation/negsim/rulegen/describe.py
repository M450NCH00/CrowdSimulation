"""Situation descriptions, the field glossary and the format example (issue #30, Part 4).

Deterministic renderers that turn a case and a session into the text a model is shown. All
the wording is in frozen templates (``negsim/negotiation/templates/rulegen_*_v1.yaml``,
pinned in ``MANIFEST.json`` by the tool of issue #24); this module only chooses lines and
puts numbers into them.

**First-person** (condition A): what one person can perceive of itself, of the place and of
the other, from its own perception record in the case, plus its own private information.
Nothing about the other that cannot be seen: not its errand, its preferred or maximum
speed, its goal or its path. **Third-person** (condition B): both people's observable state
and both people's private information, as Person 1 and Person 2, in the order the session
gives. Age and gender appear only when the session shows demographics, and then also in the
glossary; otherwise in neither.

**Numbers**, the same everywhere: distances along the way (between the two, to a narrowing,
the length of a stretch) to 0.1 m; widths (of a passage, of a body, to a wall) to 0.01 m;
speeds to 0.01 m/s; angles to the whole degree; ages in whole years.

**The glossary** is generated from the rule format's field catalogue (``negsim.rules.fields``,
documented in ``docs/rule-format.md`` section 5 and ``docs/perception.md``) and the rule
schema (``rule_db/schema/rule.v2.schema.json``), in a fixed order. Its SHA-256 is pinned in
the common template, so a change to either is refused until a new template version is frozen.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from ..negotiation.prompts import TemplateIntegrityError, load_template_data
from ..rules.database import RULE_DB_ROOT, schema_path
from ..rules.fields import AGENT_FIELDS, CATEGORY, PAIR_FIELDS, FieldSpec
from ..rules.model import LATEST_SCHEMA_VERSION
from .design import Session

KIND_COMMON = "rule_generation_common"
KIND_NEGOTIATE = "rule_generation_negotiate"
KIND_STATE = "rule_generation_state"
DEMOGRAPHIC_SWITCHES = ("age", "gender")


@dataclass(frozen=True)
class Templates:
    """A condition's template and the common template it uses, both checked against the manifest."""

    key: str
    kind: str
    data: Mapping[str, Any]
    sha256: str
    common_key: str
    common: Mapping[str, Any]
    common_sha256: str

    def identity(self) -> dict[str, Any]:
        return {"key": self.key, "sha256": self.sha256, "uses": {"key": self.common_key, "sha256": self.common_sha256}}


def load_templates(key: str, kind: str) -> Templates:
    data, digest = load_template_data(key, kind)
    common, common_digest = load_template_data(data["uses"], KIND_COMMON)
    templates = Templates(key, kind, data, digest, data["uses"], common, common_digest)
    for visible in (True, False):
        check_glossary(templates, visible)
    return templates


# --- small things ---------------------------------------------------------------------------------


def fill(text: str, **values: Any) -> str:
    """Replace ``{name}`` for the names given and nothing else, so JSON braces are left alone."""
    for name, value in values.items():
        text = text.replace("{" + name + "}", str(value))
    return text


def along(metres: float) -> str:
    return f"{metres:.1f}"


def across(metres: float) -> str:
    return f"{metres:.2f}"


def speed(mps: float) -> str:
    return f"{mps:.2f}"


def degrees(radians: float) -> int:
    return int(round(abs(math.degrees(radians))))


def listing(values: Any, quote: bool = True) -> str:
    """``"a", "b" or "c"``."""
    items = [f'"{value}"' if quote else str(value) for value in values]
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " or " + items[-1]


def rule_schema() -> dict[str, Any]:
    return json.loads((RULE_DB_ROOT / schema_path(LATEST_SCHEMA_VERSION)).read_text(encoding="utf-8"))


def meaning_of(spec: FieldSpec) -> Optional[str]:
    """A field's meaning, or ``None`` where it only repeats the field's name or its values."""
    words = spec.meaning.replace(",", " ").replace(" or ", " ").split()
    if spec.meaning.strip().lower() == spec.name.replace("_", " ") or (spec.kind == CATEGORY and set(words) <= set(spec.categories)):
        return None
    return spec.meaning


def shown_fields(table: Mapping[str, FieldSpec], demographics_visible: bool) -> list[FieldSpec]:
    """The fields of a table in their fixed order, leaving out demographic ones when hidden."""
    return [
        spec for spec in table.values()
        if demographics_visible or not set(spec.needs) & set(DEMOGRAPHIC_SWITCHES)
    ]


# --- the glossary and the format example ----------------------------------------------------------


def glossary_text(common: Mapping[str, Any], demographics_visible: bool) -> str:
    """The description of the rule format and of every field a rule may read."""
    g = common["glossary"]
    schema = rule_schema()
    defs, properties = schema["$defs"], schema["properties"]
    directive = defs["directive"]["properties"]
    units = [unit for unit in defs["unit"]["enum"] if unit != "deg"]
    lines = [g["header"], g["intro"].strip(), "", g["keys_header"]]
    key_values = {
        "encounter": {"values": listing(properties["encounter"]["enum"])},
        "priority": {"minimum": properties["priority"]["minimum"], "maximum": properties["priority"]["maximum"]},
        "expiry": {"values": listing(properties["expiry"]["enum"])},
    }
    for key in ("encounter", "when", "roles", "directive", "priority", "expiry", "intent"):
        lines.append("- " + fill(" ".join(g["keys"][key].split()), **key_values.get(key, {})))
    lines += ["", g["encounters_header"]]
    lines += [f"- {g['encounters'][name]}" for name in properties["encounter"]["enum"]]
    lines += ["", fill(" ".join(g["comparison"].split()), operators=listing(defs["comparison"]["properties"]["op"]["enum"], quote=True), units=listing(units, quote=False))]
    lines += ["", " ".join(g["prefixes"].split())]
    for header, table, prefix in ((g["pair_fields_header"], PAIR_FIELDS, "pair."), (g["agent_fields_header"], AGENT_FIELDS, "")):
        lines += ["", header]
        for spec in shown_fields(table, demographics_visible):
            meaning = meaning_of(spec)
            if spec.kind == CATEGORY:
                line = fill(g["category_line"], name=prefix + spec.name, values=listing(spec.categories))
            else:
                line = fill(g["field_line"], name=prefix + spec.name, unit=spec.unit)
            lines.append("- " + (fill(line, meaning=meaning) if meaning else line.split(": {meaning}")[0]))
    order = defs["role_assignment"]["properties"]["by"]["properties"]["order"]["enum"]
    lines += ["", g["roles_header"], fill(" ".join(g["roles"].split()), orders=listing(order))]
    lines += ["", g["directive_header"]]
    for name, words in g["directive_fields"].items():
        spec = directive[name]
        lines.append("- " + fill(words, values=listing(spec.get("enum", [])) if "enum" in spec else "", minimum=spec.get("minimum", ""), maximum=spec.get("maximum", "")))
    lines += [" ".join(g["consistency"].split())]
    return "\n".join(lines)


def glossary_sha256(common: Mapping[str, Any], demographics_visible: bool) -> str:
    return hashlib.sha256(glossary_text(common, demographics_visible).encode("utf-8")).hexdigest()


def check_glossary(templates: Templates, demographics_visible: bool) -> None:
    """Refuse a glossary that is not the one the common template was frozen with."""
    variant = "with_demographics" if demographics_visible else "without_demographics"
    pinned = templates.common["glossary_sha256"][variant]
    actual = glossary_sha256(templates.common, demographics_visible)
    if actual != pinned:
        raise TemplateIntegrityError(
            f"the field glossary generated for {templates.common_key} ({variant}) is not the one it was frozen with "
            f"(sha256 {actual}, pinned {pinned}). The field catalogue or the rule schema has changed: freeze a new "
            "version of the common template with the new hash, and record why in the work log."
        )


def format_example_text(common: Mapping[str, Any]) -> str:
    example = common["format_example"]
    return "\n".join([example["header"], example["text"].rstrip(), " ".join(example["note"].split())])


# --- the situation --------------------------------------------------------------------------------


def _direction(bearing: float, phrases: Mapping[str, str]) -> str:
    """Where the other is, from the observer's heading: 0 ahead, positive to the left."""
    angle = abs(math.degrees(bearing))
    side = "left" if bearing > 0 else "right"
    if angle <= 5.0:
        return phrases["ahead"]
    if angle >= 175.0:
        return phrases["behind"]
    if 85.0 <= angle <= 95.0:
        return fill(phrases["side"], side=side)
    if angle < 85.0:
        return fill(phrases["ahead_side"], angle=int(round(angle)), side=side)
    return fill(phrases["behind_side"], angle=int(round(180.0 - angle)), side=side)


def _heading(relative: float, phrases: Mapping[str, str]) -> str:
    """The other's direction of travel against the observer's: positive crosses from its right to its left."""
    angle = abs(math.degrees(relative))
    if angle <= 10.0:
        return phrases["same"]
    if angle >= 170.0:
        return phrases["opposite"]
    from_side, to_side = ("right", "left") if relative > 0 else ("left", "right")
    return fill(phrases["across"], from_side=from_side, to_side=to_side, angle=int(round(angle)))


def _change(closing: Optional[float], phrases: Mapping[str, str]) -> str:
    if closing is None:
        raise ValueError("a situation is described with the other's speed visible; this record hides it")
    return phrases["shrinking"] if closing > 0.0 else phrases["not_shrinking"]


def _segment(case: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
    segments = case["scenario"]["single_file_segments"]
    return segments[0] if len(segments) == 1 else None


def _place(case: Mapping[str, Any], record: Mapping[str, Any], lines: Mapping[str, str], **who: Any) -> list[str]:
    """The observer's surroundings, from its own record."""
    environment = record["environment"]
    out = []
    if environment["free_width_m"] is not None:
        out.append(fill(lines["passage"], width=across(environment["free_width_m"]), left=across(environment["free_width_left_m"]), right=across(environment["free_width_right_m"]), **who))
    elif environment["nearest_wall_distance_m"] is not None:
        out.append(fill(lines["wall"], distance=across(environment["nearest_wall_distance_m"]), **who))
    else:
        out.append(fill(lines["open"], **who))
    ahead, segment = environment["single_file_ahead_m"], _segment(case)
    if ahead is not None and segment is not None:
        if ahead > 0.0:
            out.append(fill(lines["narrowing"], distance=along(ahead), width=across(segment["width_m"]), length=along(segment["length_m"]), **who))
        else:
            out.append(fill(lines["inside_narrowing"], width=across(segment["width_m"]), length=along(segment["length_m"]), **who))
    return out


def _demographics_visible(session: Session) -> bool:
    return all(session.visibility.get(name, False) for name in DEMOGRAPHIC_SWITCHES)


def first_person(case: Mapping[str, Any], session: Session, agent: int, templates: Templates) -> str:
    """What ``agent`` is told of the situation (condition A)."""
    s = templates.data["situation"]
    other = session.second if agent == session.first else session.first
    record = case["observations"][str(agent)]
    me, them = session.personas[agent], session.personas[other]
    visible = _demographics_visible(session)
    observer = record["observer"]

    lines = [s["self_header"]]
    if visible:
        lines += [fill(s["self_age"], age=me["age"]), fill(s["self_gender"], gender=s["genders"][me["gender"]])]
    if me.get("task"):
        lines.append(fill(s["self_task"], task=me["task"]))
    lines.append(fill(s["self_motion"], speed=speed(observer["speed_mps"]), preferred=speed(observer["preferred_speed_mps"])))
    lines.append(fill(s["self_body"], width=across(2.0 * observer["radius_m"])))

    lines += ["", s["place_header"]]
    lines += _place(case, record, {name: s[f"place_{name}"] for name in ("passage", "wall", "open", "narrowing", "inside_narrowing")})
    if case["scenario"]["n_agents"] > 2:
        lines.append(s["place_others"])

    lines += ["", s["other_header"]]
    lines.append(fill(s["other_where"], distance=along(record["distance_m"]), direction=_direction(record["bearing_rad"], s["directions"])))
    lines.append(
        fill(
            s["other_motion"],
            speed=speed(record["neighbour_speed_mps"]),
            heading=_heading(record["neighbour_heading_relative_rad"], s["headings"]),
            change=_change(record["closing_speed_mps"], s["changes"]),
        )
    )
    lines.append(fill(s["other_body"], width=across(2.0 * record["neighbour_radius_m"])))
    if visible:
        lines += [fill(s["other_age"], age=them["age"]), fill(s["other_gender"], gender=s["genders"][them["gender"]])]
    if any(person.get("task") for person in session.personas.values()):
        lines.append(s["other_task"])
    return "\n".join(lines)


def third_person(case: Mapping[str, Any], session: Session, templates: Templates) -> str:
    """The situation as condition B is told it: Person 1 is ``session.first``."""
    s = templates.data["situation"]
    visible = _demographics_visible(session)
    people = (session.first, session.second)
    lines: list[str] = []
    for n, agent in enumerate(people, start=1):
        record, person = case["observations"][str(agent)], session.personas[agent]
        observer = record["observer"]
        if lines:
            lines.append("")
        lines.append(fill(s["person_header"], n=n))
        if visible:
            lines += [fill(s["person_age"], n=n, age=person["age"]), fill(s["person_gender"], n=n, gender=s["genders"][person["gender"]])]
        if person.get("task"):
            lines.append(fill(s["person_task"], n=n, task=person["task"]))
        lines.append(fill(s["person_motion"], n=n, speed=speed(observer["speed_mps"]), preferred=speed(observer["preferred_speed_mps"])))
        lines.append(fill(s["person_body"], n=n, width=across(2.0 * observer["radius_m"])))
        lines += _place(case, record, {name: s[f"person_{name}"] for name in ("passage", "wall", "open", "narrowing", "inside_narrowing")}, n=n)
    record = case["observations"][str(people[0])]
    lines += ["", s["pair_header"]]
    lines.append(fill(s["pair_where"], distance=along(record["distance_m"]), direction=_direction(record["bearing_rad"], s["directions"])))
    lines.append(fill(s["pair_motion"], heading=_heading(record["neighbour_heading_relative_rad"], s["headings"]), change=_change(record["closing_speed_mps"], s["changes"])))
    if case["scenario"]["n_agents"] > 2:
        lines.append(s["pair_others"])
    return "\n".join(lines)


def system_prompt(templates: Templates, situation: str, demographics_visible: bool) -> str:
    """A condition's system prompt: its frame, the situation, the shared glossary and format."""
    return fill(
        templates.data["system"],
        situation=situation,
        glossary=glossary_text(templates.common, demographics_visible),
        format_example=format_example_text(templates.common),
        reply_format=templates.data["reply_format"].strip(),
    ).strip()


def negotiation_prompt(case: Mapping[str, Any], session: Session, agent: int, templates: Templates) -> str:
    return system_prompt(templates, first_person(case, session, agent, templates), _demographics_visible(session))


def statement_prompt(case: Mapping[str, Any], session: Session, templates: Templates) -> str:
    return system_prompt(templates, third_person(case, session, templates), _demographics_visible(session))
