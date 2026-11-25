"""Runs one simulation from a :class:`RunPlan` and writes its log folder.

The loop, once per time step:

1. Negotiation. The dialogue begins the first time the two agents can see each other. In
   ``pre_conflict`` mode the whole dialogue happens at that instant and simulated time
   stands still while it does. In ``concurrent`` mode one message is exchanged every
   ``seconds_per_message`` of simulated time and the agents keep moving meanwhile.
2. Arbitration. The arbiter detects a conflict, decides who leads (the negotiated
   agreement if there is one and it can still be honoured, otherwise Strategy 1) and
   bounds the follower's speed.
3. Control and motion. The controller turns each agent's speed bound into a control, and
   the world advances one step.
4. Bookkeeping: who entered the conflict region, who reached their goal, collisions,
   deadlock.
"""

from __future__ import annotations

import platform
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

from .. import __version__
from ..conflict.roles import RoleSource
from ..control.strategy1 import Arbiter
from ..core.world import World
from ..llm.base import LLMClient, LLMFatalError
from ..llm.budget import BudgetExceededError
from ..metrics.compute import (
    DeadlockMonitor,
    Sample,
    first_through,
    makespan,
    min_speed_before,
    path_deviation,
    priority_ground_truth,
)
from ..negotiation.prompts import load_template
from ..negotiation.protocol import (
    END_ABORTED,
    END_CONFLICT_OVER,
    Dialogue,
    NegotiationSettings,
)
from ..runlog.schema import LOG_SCHEMA_VERSION, validate_run_dir
from ..runlog.writer import RunLogger
from ..scenarios.base import ScenarioSpec
from ..scenarios.registry import build_scenario
from ..viz.transcript import render_transcript
from .config import GROUND_TRUTH_TASK_PRIORITY, RunPlan

END_RUN_ENDED = "run_ended"
_TIME_EPS = 1e-9


class RunAborted(RuntimeError):
    """A run could not be completed (budget refused, or the model could not be reached)."""


def build_dialogue(plan: RunPlan, spec: ScenarioSpec, client: Optional[LLMClient]) -> Optional[Dialogue]:
    if not plan.negotiation["enabled"]:
        return None
    if client is None:
        raise ValueError("this run negotiates, so it needs an LLM client")
    settings = NegotiationSettings(
        template=load_template(plan.negotiation["template"]),
        max_messages_per_agent=plan.negotiation["max_messages_per_agent"],
        first_speaker=plan.first_speaker,
        info_fields=plan.info_fields,
        visibility=plan.visibility,
        model=plan.llm["model"],
        temperature=plan.llm["temperature"],
        max_tokens=plan.llm["max_tokens"],
        thinking=plan.llm["thinking"] == "enabled",
    )
    participants = {participant.agent_id: participant for participant in plan.participants}
    labels = {"experiment": plan.experiment_name, "run_id": plan.run_id}
    return Dialogue(settings, participants, spec, client, labels)


def resolved_config(
    plan: RunPlan,
    spec: ScenarioSpec,
    dialogue: Optional[Dialogue],
    client: Optional[LLMClient],
    git: Mapping[str, Any],
) -> dict[str, Any]:
    """The fully resolved configuration of a run, as written to ``config.json``."""
    template = dialogue.settings.template.identity() if dialogue else None
    client_info = client.describe() if (client is not None and dialogue is not None) else {"client": None}
    return {
        "log_schema_version": LOG_SCHEMA_VERSION,
        "experiment_name": plan.experiment_name,
        "run_id": plan.run_id,
        "run_index": plan.index,
        "condition": plan.condition,
        "seed": plan.seed,
        "repeat": plan.repeat,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git": dict(git),
        "software": {"negsim_version": __version__, "python": platform.python_version()},
        "scenario_file": plan.scenario_file,
        "scenario_variant": plan.scenario_variant,
        "scenario": spec.as_dict(),
        "participants": [
            {**participant.as_dict(), "side": spec.agents[participant.agent_id].side}
            for participant in plan.participants
        ],
        "assignment": {
            "agent_0": plan.slots[0].as_dict(),
            "agent_1": plan.slots[1].as_dict(),
            "swap_sides": plan.swap_sides,
            "first_speaker": plan.first_speaker,
        },
        "negotiation": {
            "enabled": plan.negotiation["enabled"],
            "prompt_template": template,
            "max_messages_per_agent": plan.negotiation["max_messages_per_agent"],
            "first_speaker": plan.first_speaker,
            "timing": dict(plan.negotiation["timing"]),
            "info_variant": plan.info_variant,
            "info_fields": list(plan.info_fields),
            "visibility": dict(plan.visibility),
            "rendered_system_prompts": (
                {f"agent_{agent_id}": prompt for agent_id, prompt in sorted(dialogue.system_prompts.items())}
                if dialogue
                else None
            ),
        },
        "llm": {
            **client_info,
            "model": plan.llm["model"] if dialogue else None,
            "temperature": plan.llm["temperature"] if dialogue else None,
            "max_tokens": plan.llm["max_tokens"] if dialogue else None,
            "thinking": plan.llm["thinking"] if dialogue else None,
            "json_mode": True if dialogue else None,
            "seed_parameter": None,  # the DeepSeek API has none; see docs/llm-backend.md
        },
        "arbitration": dict(plan.arbitration),
        "scoring": {**plan.scoring, "priority_order": list(plan.priority_order)},
        "budget": dict(plan.budget),
    }


def execute_run(
    plan: RunPlan,
    client: Optional[LLMClient],
    run_dir: Path | str,
    git: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Run one simulation, write its folder, and return the outcome.

    Raises :class:`RunAborted` if the budget guard refuses a call or the model cannot be
    reached at all. The folder is still written, with ``status: aborted``.
    """
    spec = build_scenario(plan.scenario_config)
    world = spec.build_world()
    if len(world.agents) != 2:
        raise ValueError("the experiment runner supports exactly two agents")
    controller = spec.build_controller()
    arbiter = Arbiter(
        spec.build_detector(),
        policy=plan.arbitration["policy"],
        tie_break=plan.arbitration["tie_break"],
        rng=random.Random(plan.seed),
    )
    dialogue = build_dialogue(plan, spec, client)
    logger = RunLogger(run_dir)
    config = resolved_config(plan, spec, dialogue, client, git or {"commit": None, "dirty": None})
    logger.write_config(config)

    timing = plan.negotiation["timing"]
    pair = (0, 1)
    rows: list[dict[str, Any]] = []
    samples: list[Sample] = []
    entry_times: dict[int, float] = {}
    source_steps = {source.value: 0 for source in RoleSource}
    monitor = DeadlockMonitor(spec.deadlock.window_s, spec.deadlock.speed_eps)
    status, detail = "timeout", None
    collisions = {"agent_agent": 0, "agent_wall": 0, "time_s": None, "agents": []}
    deadlock = False
    next_turn_time = 0.0

    def can_see(i: int, j: int) -> bool:
        return world.mutually_visible(
            i, j, spec.observation.max_range, spec.observation.walls_block_sight
        )

    turns_logged = 0

    def take_turn() -> None:
        """One turn of the dialogue, written to disk at once, even if it ends in an abort."""
        nonlocal turns_logged
        try:
            dialogue.take_turn(world)
        finally:
            for turn in dialogue.turns[turns_logged:]:
                logger.append_turn(turn.as_dict())
            turns_logged = len(dialogue.turns)

    try:
        for _ in range(spec.max_steps):
            now = world.time

            # 1. Negotiation.
            if dialogue is not None:
                if not dialogue.started and can_see(*pair):
                    dialogue.start(now)
                    next_turn_time = now
                if dialogue.active:
                    if timing["mode"] == "pre_conflict":
                        while dialogue.active:
                            take_turn()
                    elif _conflict_over(arbiter, world):
                        dialogue.stop(END_CONFLICT_OVER, now)
                    elif now >= next_turn_time - _TIME_EPS:
                        take_turn()
                        next_turn_time = now + timing["seconds_per_message"]
            negotiated = {pair: dialogue.leader} if dialogue and dialogue.leader is not None else None

            # 2. Arbitration.
            decisions = arbiter.resolve(world, negotiated, visible=can_see)
            in_conflict = [d for d in decisions.values() if d.in_conflict and d.role_source]
            if in_conflict:
                source_steps[in_conflict[0].role_source.value] += 1

            # 3. Control and motion.
            controls = {
                agent.agent_id: controller.compute(agent, decisions[agent.agent_id].speed_bound, world)
                for agent in world.agents
            }
            before = [(agent.agent_id, agent.pose, agent.path_s) for agent in world.agents]
            applied = world.step(controls)
            for agent_id, pose, path_s in before:
                decision, control = decisions[agent_id], applied[agent_id]
                talking = bool(dialogue and dialogue.active)
                rows.append(
                    _row(world.step_index - 1, now, agent_id, pose, path_s, control.v, control.omega, decision, talking)
                )
                samples.append(Sample(now, agent_id, pose.xy, control.v))

            # 4. Bookkeeping.
            for agent in world.agents:
                if agent.agent_id not in entry_times and agent.path_s >= agent.spec.region_entry_s:
                    entry_times[agent.agent_id] = world.time
            hit_agents, hit_walls = world.agent_collisions(), world.wall_collisions()
            if hit_agents or hit_walls:
                collisions = {
                    "agent_agent": len(hit_agents),
                    "agent_wall": len(hit_walls),
                    "time_s": round(world.time, 4),
                    "agents": sorted({a for pair_ in hit_agents for a in pair_} | set(hit_walls)),
                }
                status = "collision"
                break
            if world.all_done:
                status = "completed"
                break
            moving = [applied[agent.agent_id].v for agent in world.agents if not agent.done]
            if monitor.update(now, world.time, moving):
                status, deadlock = "deadlock", True
                break
    except (BudgetExceededError, LLMFatalError) as exc:
        status, detail = "aborted", f"{type(exc).__name__}: {exc}"
        if dialogue is not None:
            dialogue.stop(END_ABORTED, world.time)

    if dialogue is not None and dialogue.active:
        dialogue.stop(END_RUN_ENDED, world.time)
    for agent in world.agents:
        rows.append(_row(world.step_index, world.time, agent.agent_id, agent.pose, agent.path_s, None, None, None, False))

    outcome = _outcome(
        plan, world, dialogue, status, detail, collisions, deadlock, entry_times, samples, source_steps
    )
    logger.write_trajectory(rows)
    logger.write_outcome(outcome)
    turns = [turn.as_dict() for turn in dialogue.turns] if dialogue else []
    logger.write_transcript(render_transcript(config, turns, outcome))

    problems = validate_run_dir(run_dir)
    if problems:
        raise RuntimeError(f"run {plan.run_id} wrote a log folder that fails its own schema: {problems}")
    if status == "aborted":
        raise RunAborted(f"run {plan.run_id} aborted: {detail}")
    return outcome


def _conflict_over(arbiter: Arbiter, world: World) -> bool:
    """True once negotiating is pointless: an agent has finished or has left the zone."""
    a, b = world.agents
    if a.done or b.done:
        return True
    conflict = arbiter.detector.zone(a, b)
    return conflict is not None and not conflict.live


def _row(step, time_s, agent_id, pose, path_s, v, omega, decision, dialogue_active) -> dict[str, Any]:
    return {
        "step": step,
        "time_s": round(time_s, 6),
        "agent_id": agent_id,
        "x_m": round(pose.x, 6),
        "y_m": round(pose.y, 6),
        "theta_rad": round(pose.theta, 6),
        "path_s_m": round(path_s, 6),
        "v_mps": None if v is None else round(v, 6),
        "omega_radps": None if omega is None else round(omega, 6),
        "speed_bound_mps": None if decision is None else round(decision.speed_bound, 6),
        "role": None if decision is None or decision.role is None else decision.role.value,
        "role_source": (
            None if decision is None or decision.role_source is None else decision.role_source.value
        ),
        "in_conflict": None if decision is None else decision.in_conflict,
        "zone_d_in_m": None if decision is None or decision.zone_d_in is None else round(decision.zone_d_in, 6),
        "zone_d_out_m": None if decision is None or decision.zone_d_out is None else round(decision.zone_d_out, 6),
        "dialogue_active": dialogue_active,
    }


def _rounded(value: Optional[float], digits: int = 4) -> Optional[float]:
    return None if value is None else round(value, digits)


def _fallback_reasons(dialogue: Dialogue, source_steps: Mapping[str, int]) -> list[str]:
    """Why something other than the negotiated agreement decided who led, if anything did.

    Counted over the steps on which a conflict was live. Once the agents have agreed, the
    arbiter never reports Strategy 1 as the source, so Strategy 1 steps in a run that did
    reach a consensus must have come before it (possible only in ``concurrent`` mode).
    """
    reasons = []
    if source_steps[RoleSource.STRATEGY1.value]:
        if not dialogue.started:
            reasons.append("dialogue_not_started")
        elif dialogue.leader is None:
            reasons.append("no_consensus")
        else:
            reasons.append("conflict_before_consensus")
    if source_steps[RoleSource.PHYSICAL_PRECEDENCE.value]:
        reasons.append("negotiated_roles_not_feasible")
    return reasons


def _outcome(
    plan: RunPlan,
    world: World,
    dialogue: Optional[Dialogue],
    status: str,
    detail: Optional[str],
    collisions: Mapping[str, Any],
    deadlock: bool,
    entry_times: Mapping[int, float],
    samples: list[Sample],
    source_steps: Mapping[str, int],
) -> dict[str, Any]:
    ids = [agent.agent_id for agent in world.agents]
    goal_times = {agent.agent_id: agent.goal_time for agent in world.agents}
    leader = first_through(entry_times)
    follower = None if leader is None else next(i for i in ids if i != leader)
    min_speeds = {i: min_speed_before(samples, i, entry_times.get(i)) for i in ids}
    deviation = path_deviation(samples, {agent.agent_id: agent.spec.path for agent in world.agents})

    if dialogue is None:
        negotiation = {
            "enabled": False, "started": False, "start_time_s": None, "end_time_s": None,
            "end_reason": None, "consensus_reached": None, "turns_used": 0,
            "messages_per_agent": {str(i): 0 for i in ids}, "stances": [],
            "negotiated_leader": None, "llm_calls": 0, "parse_failures": 0, "retries": 0,
            "tokens": None, "cost_usd": 0.0, "llm_latency_s": 0.0,
        }
        fallback_used, reasons = None, []
    else:
        negotiation = {
            "enabled": True,
            "started": dialogue.started,
            "start_time_s": _rounded(dialogue.started_at),
            "end_time_s": _rounded(dialogue.ended_at),
            "end_reason": dialogue.end_reason,
            "consensus_reached": dialogue.consensus,
            "turns_used": len(dialogue.turns),
            "messages_per_agent": {str(i): n for i, n in sorted(dialogue.messages_sent().items())},
            "stances": [[turn.speaker, turn.stance.value] for turn in dialogue.turns],
            "negotiated_leader": dialogue.leader,
            **dialogue.totals(),
        }
        reasons = _fallback_reasons(dialogue, source_steps)
        fallback_used = bool(reasons)

    ground_truth = None
    if plan.scoring["ground_truth"] == GROUND_TRUTH_TASK_PRIORITY:
        higher = priority_ground_truth(
            {participant.agent_id: participant.task_type for participant in plan.participants},
            plan.priority_order,
        )
        ground_truth = {
            "type": GROUND_TRUTH_TASK_PRIORITY,
            "priority_order": list(plan.priority_order),
            "higher_priority_agent": higher,
            "higher_priority_first": None if leader is None or higher is None else leader == higher,
            "higher_priority_time_to_goal_s": None if higher is None else _rounded(goal_times[higher]),
        }

    return {
        "log_schema_version": LOG_SCHEMA_VERSION,
        "run_id": plan.run_id,
        "status": status,
        "status_detail": detail,
        "sim_time_s": _rounded(world.time),
        "steps": world.step_index,
        "negotiation": negotiation,
        "roles": {
            "negotiated_leader": None if dialogue is None else dialogue.leader,
            "executed_leader": leader,
            "executed_follower": follower,
            "negotiated_roles_followed": (
                None if dialogue is None or dialogue.leader is None or leader is None else dialogue.leader == leader
            ),
            "role_source_steps": dict(source_steps),
        },
        "fallback_used": fallback_used,
        "fallback_reasons": reasons,
        "collisions": dict(collisions),
        "deadlock": deadlock,
        "makespan_s": _rounded(makespan(goal_times)),
        "time_to_goal_s": {str(i): _rounded(goal_times[i]) for i in ids},
        "region_entry_time_s": {str(i): _rounded(entry_times.get(i)) for i in ids},
        "first_through": leader,
        "follower": follower,
        "follower_min_speed_mps": None if follower is None else _rounded(min_speeds[follower]),
        "min_speed_before_region_mps": {str(i): _rounded(min_speeds[i]) for i in ids},
        "path_deviation_m": {key: _rounded(value, 6) for key, value in deviation.items()},
        "ground_truth": ground_truth,
    }
