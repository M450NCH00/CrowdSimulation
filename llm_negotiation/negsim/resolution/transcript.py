"""A resolution session's record, for reading (``sessions/<session_id>.md``; issue #58, RF-3).

Rendered from the record alone, so it can always be rebuilt: who met where, when the encounter
began and ended and why, and per decision point why it fired, what the agent was told (the
description; the fixed system text is the same for every decision point of a condition and is
shown once), what it replied, word for word, and what came of it; then the debriefs.
"""

from __future__ import annotations

import json
from typing import Any, Mapping


def _fence(text: str) -> list[str]:
    return ["```", text.rstrip(), "```"]


def render(record: Mapping[str, Any]) -> str:
    session, encounter = record["session"], record.get("encounter") or {}
    lines = [
        f"# Session {record['session_id']}",
        "",
        f"- Case: {record['case']['case_id']}@{record['case']['version']}; scenario plug-in `{record['scenario']}`",
        f"- Condition: {record['condition']}; repeat {session['repeat']}"
        + ("; in the exact-repeat set" if session.get("exact_repeat_set") else ""),
        f"- Design cell: {json.dumps(session['cell'], sort_keys=True)}",
        f"- People: " + "; ".join(f"agent {agent}: {json.dumps(person, sort_keys=True)}" for agent, person in session["personas"].items()),
        # Issue #61: how each sees the other (a row is who is looking); only a session that has it.
        *([f"- Pairwise: {json.dumps(session['pairwise'])}"] if session.get("pairwise") else []),
        f"- Model: {record['llm']['model']} (temperature {record['llm']['temperature']}, reply cap {record['llm']['max_tokens']} tokens)",
        f"- Outcome: **{record['outcome']}**" + (f" ({record['error']})" if record.get("error") else ""),
        "",
    ]
    trigger, end = encounter.get("trigger"), encounter.get("end") or {}
    if trigger is None:
        lines += ["The trigger never fired: nobody was prompted.", ""]
    else:
        lines += [
            "## The encounter",
            "",
            f"- Began at {trigger['time_s']} s (step {trigger['step']}): agent {trigger['agent_id']} and agent {trigger['other_id']}.",
            f"- In it: agents {encounter['agents']}; conflict pairs {encounter['pairs']}; prompted {encounter['prompted']}"
            + (f"; left out by the cap: {len(encounter['left_out_by_cap'])}" if encounter.get("left_out_by_cap") else ""),
            f"- Ended at {end.get('time_s')} s: {end.get('reason')}"
            + ("; **not resolved by the LLM**" if end.get("not_resolved_by_llm") else ""),
        ]
        if encounter.get("orca_took_over"):
            lines.append(f"- ORCA took over at step {encounter['orca_took_over']['step']}.")
        lines.append("")
    points = record.get("decision_points") or []
    if points:
        lines += ["## The fixed text (system message)", "", *_fence(points[0]["prompt"]["messages"][0]["content"]), ""]
    for point in points:
        lines += [
            f"## Decision point {point['index']}: agent {point['agent_id']}, its number {point['number']}, at {point['time_s']} s",
            "",
            f"Why: {', '.join(point['trigger_reasons'])}",
            "",
            "What it was told:",
            "",
            *_fence(point["prompt"]["messages"][1]["content"]),
            "",
        ]
        for attempt in point["attempts"]:
            lines += [f"Reply (attempt {attempt['attempt']}):", "", *_fence(attempt.get("raw_output") or "(none)")]
            if attempt.get("parse_error"):
                lines.append(f"Could not be read: {attempt['parse_error']}")
            lines.append("")
        if point.get("coded"):
            lines.append(f"Coded: {json.dumps(point['coded'], sort_keys=True)}")
        after = point.get("until_next")
        if after:
            lines.append(
                f"What came of it, until {after['time_s']} s ({after['ended_by']}): plan {after['plan_state']}, "
                f"smallest gap to anyone in the encounter {after['smallest_gap_m']} m"
            )
        lines.append("")
    for said in record.get("utterances") or []:
        lines.append(f"- {said['time_s']} s, agent {said['speaker_id']} said \"{said['message']}\"; heard by {sorted(said['heard_by'])}")
    for made in record.get("signals") or []:
        lines.append(f"- {made['time_s']} s, agent {made['signaller_id']} signalled {made['signal']}; seen by {made['seen_by']}")
    if record.get("utterances") or record.get("signals"):
        lines.append("")
    for debrief in record.get("debriefs") or []:
        lines += [f"## Debrief: agent {debrief['agent_id']}", ""]
        for attempt in debrief["attempts"]:
            lines += [f"Reply (attempt {attempt['attempt']}):", "", *_fence(attempt.get("raw_output") or "(none)"), ""]
    totals = record.get("totals") or {}
    lines += [
        "## Totals",
        "",
        f"{totals.get('llm_calls', 0)} call(s), {totals.get('retries', 0)} retried; tokens {json.dumps(totals.get('tokens', {}), sort_keys=True)}; "
        f"USD {totals.get('cost_usd', 0)}",
    ]
    return "\n".join(lines) + "\n"
