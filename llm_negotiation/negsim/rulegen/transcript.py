"""A session of rule generation, for reading: ``sessions/<session_id>.md`` (issue #30, Part 5).

Issue #24 writes a ``transcript.md`` beside every run's ``conversation.jsonl``
(``negsim/viz/transcript.py``); this is the same for a session of condition A or B, rendered
from the session's record alone (``sessions/<session_id>.json``), which stays the record. It
shows who the people were, the system prompts, every turn as it was shown and answered, the
proposals with their ids and how each acceptance was read, and the outcome: what a person
needs for the manual review of section 6 of ``docs/rule-generation.md``.
"""

from __future__ import annotations

import json
from typing import Any, Mapping

FENCE = "~~~"


def _block(text: str, kind: str = "text") -> list[str]:
    return [f"{FENCE}{kind}", text.rstrip(), FENCE]


def _rule(rule: Any) -> list[str]:
    return _block(json.dumps(rule, indent=2, ensure_ascii=False), "json")


def _yes(value: Any) -> str:
    return "yes" if value else "no"


def _header(record: Mapping[str, Any]) -> list[str]:
    session, llm, templates = record["session"], record["llm"], record["templates"]
    cell = session["cell"]
    condition = {"negotiated": "A (negotiated)", "stated": "B (stated)"}[record["condition"]]
    replied = f", replied as `{record['model_returned']}`" if record.get("model_returned") else ""
    return [
        f"# Transcript: {session['session_id']}",
        "",
        f"- Condition {condition}; repeat {session['repeat']}",
        f"- Case: `{session['case_id']}` version {session['case_version']}, agents {session['agents'][0]} and {session['agents'][1]}",
        "- Design cell: " + ", ".join(f"{name} `{value}`" for name, value in cell.items()),
        f"- Model: `{llm['model']}`{replied}; temperature {llm['temperature']}, at most {llm['max_tokens']} tokens a reply, thinking {'on' if llm['thinking'] else 'off'}",
        f"- Templates: `{templates['key']}` (sha256 `{templates['sha256'][:12]}`), with `{templates['uses']['key']}` (sha256 `{templates['uses']['sha256'][:12]}`)",
        f"- Started {record['started_utc']}, ended {record.get('ended_utc')}",
    ]


def _people(record: Mapping[str, Any]) -> list[str]:
    session = record["session"]
    agents = [str(agent) for agent in session["agents"]]
    personas = session["personas"]
    if record["condition"] == "negotiated":
        role = {str(session["first"]): "speaks first"}
    else:
        role = {str(session["first"]): "Person 1"}
    lines = ["", "## People", "", "| | " + " | ".join(f"agent {agent}" for agent in agents) + " |", "|---|" + "---|" * len(agents)]
    lines.append("| role | " + " | ".join(role.get(agent, "speaks second" if record["condition"] == "negotiated" else "Person 2") for agent in agents) + " |")
    for key, label in (("age", "age"), ("gender", "gender"), ("task", "errand"), ("urgency", "urgency")):
        lines.append(f"| {label} | " + " | ".join(str(personas[agent].get(key) or "") for agent in agents) + " |")
    visibility = session["visibility"]
    lines += ["", "Age and gender shown to the other: " + _yes(visibility.get("age") and visibility.get("gender")) + ". An errand is never shown."]
    return lines


def _negotiation(record: Mapping[str, Any]) -> list[str]:
    lines = ["", "## System prompts"]
    for agent, prompt in record["system_prompts"].items():
        lines += ["", f"### Agent {agent}", "", *_block(prompt)]
    lines += ["", "## Negotiation"]
    for turn in record["turns"]:
        lines += ["", f"### Turn {turn['turn_index'] + 1}: agent {turn['speaker']}", "", "Shown to this agent:", "", *_block(turn["shown"])]
        if len(turn["attempts"]) > 1 or not turn["parse_ok"]:
            for attempt in turn["attempts"]:
                problem = attempt.get("parse_error") or attempt.get("api_error")
                if problem:
                    lines += ["", f"Attempt {attempt['attempt']} could not be used ({problem}). It replied:", "", *_block(str(attempt.get("raw_output")))]
        if not turn["parse_ok"]:
            lines += ["", f"**No readable turn** ({turn['parse_error']})."]
            continue
        lines += ["", "Said:", "", *_block(turn["message"] or "(nothing)")]
        if turn["proposal"] is not None:
            lines += ["", f"Proposed, proposal id `{turn['proposal_id']}`:", "", *_rule(turn["proposal"])]
        if turn["accept"] is not None:
            lines += ["", f"Accepted: `{turn['accept']}`, read as **{turn['accept_status']}**."]
        if turn["no_rule_possible"]:
            lines += ["", "Said no rule is possible unless people can talk first."]
    agreement = record.get("agreement")
    lines += ["", "## Outcome", "", f"- **{record['outcome']}**" + (f" ({record['error']})" if record.get("error") else "")]
    if agreement:
        lines.append(
            f"- The rule of agent {agreement['proposed_by']} (turn {agreement['proposed_at_turn'] + 1}, proposal id "
            f"`{agreement['proposal_id']}`), accepted by agent {agreement['accepted_by']} at turn "
            f"{agreement['accepted_at_turn'] + 1}; its proposer spoke first: {_yes(agreement['proposer_spoke_first'])}"
        )
    return lines


def _statement(record: Mapping[str, Any]) -> list[str]:
    lines = ["", "## System prompt", "", *_block(record["system_prompt"]), "", "## Reply"]
    for attempt in record["attempts"]:
        problem = attempt.get("parse_error") or attempt.get("api_error")
        if problem:
            lines += ["", f"Attempt {attempt['attempt']} could not be used ({problem}). It replied:", "", *_block(str(attempt.get("raw_output")))]
    if record.get("rule") is not None:
        lines += ["", f"The rule, canonical hash `{record['canonical_hash'][:12]}`:", "", *_rule(record["rule"])]
    if record.get("reason") is not None:
        lines += ["", "The reason:", "", *_block(record["reason"] or "(none)")]
    lines += ["", "## Outcome", "", f"- **{record['outcome']}**" + (f" ({record['error']})" if record.get("error") else "")]
    return lines


def render(record: Mapping[str, Any]) -> str:
    """The transcript of one session record, as Markdown."""
    lines = _header(record) + _people(record)
    lines += _negotiation(record) if record["condition"] == "negotiated" else _statement(record)
    totals = record["totals"]
    lines.append(
        f"- Calls {totals['llm_calls']} ({totals['retries']} retried); prompt tokens {totals['tokens']['prompt_tokens']}, "
        f"completion tokens {totals['tokens']['completion_tokens']}; cost USD {totals['cost_usd']:.6f}"
    )
    return "\n".join(lines) + "\n"
