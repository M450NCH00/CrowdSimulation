"""Human-readable transcript of one run (``transcript.md``).

Built from the same records that go into ``config.json``, ``conversation.jsonl`` and
``outcome.json``, so the transcript cannot say anything the data files do not.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

_FENCE = "~~~"


def _block(text: str) -> list[str]:
    return [f"{_FENCE}text", text, _FENCE, ""]


def _fmt(value: Any, unit: str = "", none: str = "n/a") -> str:
    if value is None:
        return none
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        value = f"{value:.4g}"
    return f"{value} {unit}" if unit else f"{value}"


def _agent(agent_id: Optional[int]) -> str:
    return "n/a" if agent_id is None else f"agent {agent_id}"


def render_transcript(
    config: Mapping[str, Any], turns: Sequence[Mapping[str, Any]], outcome: Mapping[str, Any]
) -> str:
    negotiation, llm = config["negotiation"], config["llm"]
    participants, agents = config["participants"], config["scenario"]["agents"]
    lines = [
        f"# Transcript: {config['run_id']}",
        "",
        f"- Experiment: `{config['experiment_name']}`, condition {config['condition']}",
        f"- Scenario: {config['scenario']['type']} (variant `{config['scenario_variant']}`)",
        f"- Seed: {config['seed']}; repeat {config['repeat']}",
        f"- Code: commit `{config['git'].get('commit')}`"
        + (" with uncommitted changes" if config["git"].get("dirty") else ""),
    ]
    if negotiation["enabled"]:
        template = negotiation["prompt_template"]
        lines += [
            f"- Model: `{llm['model']}` via the {llm['client']} client, temperature {llm['temperature']}, "
            f"thinking {llm['thinking']}",
            f"- Prompt template: `{template['key']}` (sha256 `{template['sha256'][:12]}`)",
            f"- First speaker: agent {negotiation['first_speaker']}; timing mode `{negotiation['timing']['mode']}`",
            f"- Situation fields shown: {', '.join(negotiation['info_fields']) or 'none'}",
            "- What each agent can see of the other: "
            + ", ".join(f"{key} {'yes' if value else 'no'}" for key, value in negotiation["visibility"].items()),
        ]
    else:
        lines.append("- Negotiation: disabled (Strategy 1 only)")

    lines += ["", "## Participants", "", "| | agent 0 | agent 1 |", "|---|---|---|"]

    def row(label: str, values: Sequence[Any]) -> str:
        return f"| {label} | " + " | ".join(_fmt(v, none="") for v in values) + " |"

    personas = [p.get("persona") or {} for p in participants]
    lines += [
        row("starts", [a["side"] for a in agents]),
        row("persona", [p.get("persona_id") for p in personas]),
        row("age", [p.get("age") for p in personas]),
        row("gender", [p.get("gender") for p in personas]),
        row("backstory", [p.get("backstory") for p in personas]),
        row("task", [p["task"] for p in participants]),
        row("task type", [p["task_type"] for p in participants]),
        row("maximum speed (m/s)", [a["max_speed_mps"] for a in agents]),
        row("body width (m)", [2.0 * a["radius_m"] for a in agents]),
        "",
    ]

    if negotiation["enabled"]:
        lines += ["## System prompts", ""]
        for key, prompt in negotiation["rendered_system_prompts"].items():
            lines += [f"### {key.replace('_', ' ').capitalize()}", "", *_block(prompt)]

        lines += ["## Conversation", ""]
        if not turns:
            lines += ["No turns were taken.", ""]
        for turn in turns:
            side = agents[turn["speaker"]]["side"]
            lines += [
                f"### Turn {turn['turn_index'] + 1}: agent {turn['speaker']} ({side}) at t = {turn['sim_time_s']:.1f} s",
                "",
                "Shown to this agent before it spoke:",
                "",
                *_block(turn["attempts"][0]["prompt_messages"][-1]["content"]),
            ]
            if turn["message"]:
                lines += ["Said to the other agent:", "", *_block(turn["message"])]
            else:
                lines += ["Said to the other agent: nothing (the reply could not be read).", ""]
            lines += [f"Stance, not shown to the other agent: `{turn['stance']}`", ""]
            if turn["n_attempts"] > 1 or not turn["parse_ok"]:
                errors = [a["parse_error"] or f"api error: {a['api_error']}" for a in turn["attempts"]]
                accepted = "the last one was accepted" if turn["parse_ok"] else "none was accepted"
                lines += [
                    f"Attempts: {turn['n_attempts']}; {accepted}. "
                    + "; ".join(f"attempt {i + 1}: {err or 'ok'}" for i, err in enumerate(errors)),
                    "",
                ]

    lines += ["## Outcome", ""]
    talk, roles = outcome["negotiation"], outcome["roles"]
    lines.append(f"- Run status: **{outcome['status']}**" + (f" ({outcome['status_detail']})" if outcome["status_detail"] else ""))
    if talk["enabled"]:
        if talk["consensus_reached"]:
            lines.append(
                f"- Consensus: yes, after {talk['turns_used']} turns. Agreed to go first: {_agent(talk['negotiated_leader'])}."
            )
        else:
            lines.append(f"- Consensus: no ({talk['turns_used']} turns; dialogue ended: {talk['end_reason']}).")
        lines.append(
            f"- Fallback to Strategy 1 used: {_fmt(outcome['fallback_used'])}"
            + (f" ({', '.join(outcome['fallback_reasons'])})" if outcome["fallback_reasons"] else "")
        )
    lines += [
        f"- Went through first: {_agent(outcome['first_through'])}; followed: {_agent(outcome['follower'])}",
    ]
    if roles["negotiated_roles_followed"] is not None:
        lines.append(f"- Motion followed the agreement: {_fmt(roles['negotiated_roles_followed'])}")
    lines += [
        f"- Collisions: agent-agent {outcome['collisions']['agent_agent']}, agent-wall {outcome['collisions']['agent_wall']}; deadlock: {_fmt(outcome['deadlock'])}",
        f"- Time to goal: agent 0 {_fmt(outcome['time_to_goal_s']['0'], 's')}, agent 1 {_fmt(outcome['time_to_goal_s']['1'], 's')}; makespan {_fmt(outcome['makespan_s'], 's')}",
        f"- Follower's lowest speed before the conflict region: {_fmt(outcome['follower_min_speed_mps'], 'm/s')}",
        f"- Mean deviation from the desired paths: {_fmt(outcome['path_deviation_m']['mean'], 'm')}",
    ]
    truth = outcome["ground_truth"]
    if truth is not None:
        lines.append(
            f"- Ground truth ({' > '.join(truth['priority_order'])}): higher-priority agent is "
            f"{_agent(truth['higher_priority_agent'])}; it went first: {_fmt(truth['higher_priority_first'])}"
        )
    else:
        lines.append("- Ground truth: none for this condition. The outcome is recorded, not judged.")
    if talk["enabled"]:
        tokens = talk["tokens"] or {}
        lines.append(
            f"- Model usage: {talk['llm_calls']} calls, {tokens.get('prompt_tokens', 0)} prompt + "
            f"{tokens.get('completion_tokens', 0)} completion tokens, estimated cost USD {talk['cost_usd']:.6f}, "
            f"{talk['llm_latency_s']:.1f} s waiting for the model"
        )
    return "\n".join(lines) + "\n"
