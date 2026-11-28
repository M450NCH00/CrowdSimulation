"""The extractor's prompt (issue #66, RF-11, task 3): the sample of sessions shown in full, and the
two messages rendered from the frozen template ``extract_v1``.

**The sample** of each run is 10 to 20 resolved sessions of the main table (never held-out, never
failed), chosen with the run's seed to cover each outcome and condition: the strata are the
condition and the two people's passing sides; one session of each stratum is taken, in an order
the seed shuffles, until the sample size is reached, and the rest is filled at random. The tables
are the same in every run; only the sample differs.
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..configutil import ConfigError
from ..negotiation.prompts import load_template_data
from .table import COLUMNS, CONDITION_COLUMNS, TARGETS, Session, Tables, as_csv, factor_margins, failed_table, geometry_name, physical

KIND = "rule_extraction"
#: The design factors whose levels the factor table counts (``negsim.resolution.design``).
DESIGN_FACTORS = (
    "age_pair", "gender_pair", "urgency", "mobility_aid", "load", "distraction", "assertiveness", "residence", "memory_note",
    "ethnicity_pair", "attractiveness_0_sees_1", "attractiveness_1_sees_0", "familiarity", "surroundings", "time_of_day",
    "demographics_visible", "ethnicity_visible", "attractiveness_visible",
)


class ExtractTemplate:
    """A frozen ``rule_extraction`` template."""

    def __init__(self, key: str):
        self.key = key
        self.data, self.sha256 = load_template_data(key, KIND)

    def identity(self) -> dict[str, Any]:
        return {"key": self.key, "id": self.data["template_id"], "version": self.data["version"], "sha256": self.sha256}

    def __getitem__(self, name: str) -> Any:
        return self.data[name]


def stratum(session: Session) -> tuple[str, str]:
    p1, p2 = physical(session.row, "p1"), physical(session.row, "p2")
    return session.condition, f"{p1['passing_side'] or '-'}/{p2['passing_side'] or '-'}"


def sample_sessions(sessions: Sequence[Session], seed: int, size: int) -> list[Session]:
    """``size`` sessions (all, if fewer), covering the strata first; in id order."""
    rng = random.Random(seed)
    ordered = sorted(sessions, key=lambda s: s.session_id)
    if len(ordered) <= size:
        return ordered
    by: dict[tuple[str, str], list[Session]] = defaultdict(list)
    for session in ordered:
        by[stratum(session)].append(session)
    keys = sorted(by)
    rng.shuffle(keys)
    chosen: list[Session] = []
    for key in keys:
        if len(chosen) == size:
            break
        chosen.append(rng.choice(by[key]))
    rest = [s for s in ordered if s not in chosen]
    chosen += rng.sample(rest, size - len(chosen))
    return sorted(chosen, key=lambda s: s.session_id)


# --- one session in full -------------------------------------------------------------------------


def _steps(steps: Any) -> str:
    if not steps:
        return "none (carry on as before)"
    return json.dumps(steps, ensure_ascii=False, separators=(", ", ": "))


def _why(reasons: Sequence[str]) -> str:
    """The decision point's reasons without the agent numbers they name (``perceives:0``), which
    are not the table's person 1 and person 2."""
    return ", ".join(dict.fromkeys(str(reason).split(":", 1)[0] for reason in reasons)) or "-"


def _distance(point: Mapping[str, Any]) -> str:
    view = point.get("view") or {}
    label = ((view.get("labels") or {}).get("label_of_agent") or {}).get(str(point.get("partner_id")))
    for person in view.get("seen") or []:
        if person.get("label") == label:
            return f"{person['distance_m']:.1f}"
    return "?"


def session_in_full(template: ExtractTemplate, tables: Tables, session: Session) -> str:
    """One sampled session: every decision point's intent, steps, signal, message and private
    reason, and each person's debrief, with the rows of the table they are."""
    record = tables.records[session.session_id]
    label = tables.label[session.session_id]
    rows = {row["person"]: row["row"] for row in tables.main if row["session"] == label}
    p1, p2 = physical(session.row, "p1"), physical(session.row, "p2")
    first = {"yes": "person 1", "no": "person 2", "together": "together"}.get(p1["passed_first"], "not measured")
    lines = [template["session"].format(
        session=label, condition=session.condition, geometry=geometry_name(session.row),
        outcome=template["outcome"].format(p1_side=p1["passing_side"] or "?", p2_side=p2["passing_side"] or "?", first=first),
    )]
    debriefs = {int(entry["agent_id"]): entry for entry in record.get("debriefs") or []}
    for person in ("p1", "p2"):
        agent = int(session.row[f"{person}_agent"])
        lines.append(template["person"].format(person={"p1": "Person 1", "p2": "Person 2"}[person], row=rows.get(person, "?")))
        for point in record.get("decision_points") or []:
            if int(point["agent_id"]) != agent:
                continue
            parsed = point.get("parsed")
            fields = {"number": point["number"], "distance": _distance(point), "why": _why(point.get("trigger_reasons") or [])}
            if not parsed:
                lines.append(template["unreadable"].format(**fields))
                continue
            lines.append(template["decision"].format(**fields, intent=parsed.get("intent") or "", steps=_steps(parsed.get("steps"))))
            if parsed.get("signal") not in (None, "", "none"):
                lines.append(template["signal"].format(signal=parsed["signal"]))
            if parsed.get("message"):
                lines.append(template["said"].format(message=parsed["message"]))
            if parsed.get("reason"):
                lines.append(template["reason"].format(reason=parsed["reason"]))
        debrief = (debriefs.get(agent) or {}).get("parsed")
        if debrief:
            lines.append(template["debrief"].format(kind=debrief.get("kind") or "?", basis=debrief.get("basis") or "",
                                                    source=debrief.get("source") or "none"))
        else:
            lines.append(template["no_debrief"])
    return "\n".join(lines)


# --- the two messages ----------------------------------------------------------------------------


@dataclass(frozen=True)
class RenderedExtraction:
    messages: list[dict[str, str]]
    sampled: list[str]  # session ids shown in full
    template: dict[str, Any]


def render(template: ExtractTemplate, tables: Tables, sampled: Sequence[Session], encounter_description: str) -> RenderedExtraction:
    present = [column for column in COLUMNS if column in template["columns"]]
    missing = [column for column in COLUMNS if column not in template["columns"]]
    if missing:
        raise ConfigError(f"template {template.key} describes no column {missing}")
    system = template["system"].format(
        targets=", ".join(TARGETS), conditions=", ".join(CONDITION_COLUMNS), reply_format=template["reply_format"].strip(),
    )
    flips = [cell for cell in tables.coin_flips.values()]
    flipped_rows = sum(row["cell_stability"] == "coin_flip" for row in tables.main)
    coin_flips = (
        template["coin_flips"].format(coin_flip=sum(c["coin_flip"] for c in flips), tested=len(flips), rows=flipped_rows)
        if flips else template["no_coin_flips"]
    )
    resolved = [*tables.main_sessions]
    user = template["user"].format(
        encounter_description=encounter_description.strip(),
        columns="\n".join(f"- {column}: {template['columns'][column]}" for column in present),
        rows=len(tables.main), sessions=len(tables.main_sessions),
        main_table=as_csv(tables.main, present),
        failed=len(tables.failed_sessions),
        failed_table=as_csv(failed_table(tables.failed_sessions), ("condition", "geometry", "first_sides_of_the_two", "failure", "sessions")),
        factor_table=as_csv(factor_margins(resolved, tables.failed_sessions, DESIGN_FACTORS), ("factor", "level", "resolved", "failed")),
        coin_flips=coin_flips,
        sampled=len(sampled),
        sessions_in_full="\n\n".join(session_in_full(template, tables, session) for session in sampled),
    )
    return RenderedExtraction(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        [session.session_id for session in sampled], template.identity(),
    )


def retry_message(template: ExtractTemplate, error: str) -> dict[str, str]:
    return {"role": "user", "content": template["retry"].format(error=error).strip()}

