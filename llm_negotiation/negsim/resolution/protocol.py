"""The Step 1 encounter protocol (issue #58, RF-3; ``docs/resolution.md``, D3 to D6, D8 and D13).

One **session** puts LLM agents into one case's own run (its source run, on its seed) under one
condition, and records everything they were told and replied:

1. **The trigger** (D4). The run goes on as plain ORCA until, for one of the case's two people,
   all of these hold: it sees the other (RF-17's view: the view cone, the seeing range, nobody
   and no wall in between) or hears them speak to it; the distance between them is shrinking;
   and the scenario predicts a conflict between them (:meth:`Scenario.conflict_predicted`).
   That is the encounter's first decision point.
2. **Who is in the encounter** comes from the scenario (:meth:`Scenario.encounter_members`):
   the two who started it, or more (D11). At most ``max_prompted`` of them are in it (a cost
   cap, D12); the rest stay plain ORCA, and the session records how many were left out.
3. **Decision points** (D5). At the first, every member for whom D4 holds is prompted, all on
   the same world state; a member for whom it does not yet hold (the person ahead, who cannot
   see the one behind) is first prompted when it does. After its first, an agent is prompted
   again only when (a) the conflict still matters (still predicted with someone in the
   encounter, or its plan has ended) and (b) something new happened from its point of view:
   someone in the encounter changed speed or direction noticeably, stopped or started backing
   up (``perceive.changes_since``); someone signalled to it or it heard something; someone came
   into view; its own plan is failing (the closest approach to its partner at the present
   velocities is below the safety distance again, having been clear since it decided); or its
   plan has ended. Guards: only the agent who noticed is prompted, at least ``min_gap_s``
   between two prompts of one agent, at most ``max_decision_points`` per agent, and every
   decision point logs why it fired.
4. **Between decision points** the simulator carries out the plans in ``plan_only`` (RF-4's
   driver): ORCA does not steer the encounter's members apart.
5. **The conditions** (D3): *independent*, one decision point per agent, no message, no signal;
   *non-verbal*, signals and movement, up to the cap; *talk*, the same and one message per
   agent per decision point. A signal is seen by whoever sees the agent when it is made. A
   message takes time to say (``speech_words_per_second``) and is heard, when it has been said,
   by everyone within hearing range: an event for each listener.
6. **The end.** The encounter ends when every conflict pair has passed (or one of the pair has
   arrived), when no conflict between members has been predicted for ``no_conflict_end_s``,
   on deadlock, when the run stops on a collision, or at the run's time limit. If every prompted agent has used its decision
   points and has no plan left to carry out while the conflict is still predicted, the
   encounter is **not resolved by the LLM**: it is handed to ORCA (``PlanDriver.release``),
   and what ORCA does after that is in the ``plan_only`` replay, recorded separately.
7. **The debrief** (D8): after the end, one call per agent that made a readable decision, with
   its last prompt, its reply, and every decision it made.

**Prompt history is compact:** every decision point is a fresh request of two messages, and an
earlier decision point reappears only as its lines in WHAT YOU HAVE DONE SO FAR (D2, D7).

**What is recorded** (``as_dict``): when and why each decision point fired, the structured view,
the exact messages sent, every attempt with its raw reply, the parsed reply, the plan given, and
what came of it before the agent's next decision point; the encounter's start, members,
conflict pairs, end and why, the hand-over to ORCA; the debriefs; everything said and
signalled; and the decisions and release in the form a replay reads (``replay.py``), so that
both replays are rebuilt from the record alone (D13).

**Assumptions of this module** (``WORK_LOG-58.md``), none of them sourced:

- an agent's first prompt needs D4 to hold for it, even at the encounter's first decision point;
- a plan with no steps (``[]``, "carry on") never *ends* in D5's sense;
- an unreadable reply (after its retry) uses up a decision point; the agent carries on with its
  plan, or with none (``[]``) if it had none, and its look is dropped so its history shows no
  decision it did not make;
- ORCA takes over as in point 6, which is when "the last decision point" (D6) has played out.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional, Sequence

from ..avoidance.simulation import STATUS_COLLISION, STATUS_COMPLETED, STATUS_DEADLOCK
from ..configutil import ConfigError, as_choice, as_number, check_keys
from ..llm.base import LLMClient, Usage
from ..negotiation.protocol import MAX_ATTEMPTS_PER_TURN, request_with_retry
from ..rulegen.protocol import LLMSettings
from .execute import COMPLETED, EXECUTION_RF4, EXECUTIONS, MODE_PLAN_ONLY, RUNNING, WAITING, PlanRun
from .perceive import (
    Exchange, LLMViewSettings, Perceiver, bodies_in, changes_since, in_sight, perceiver_for, safety_distance, sees, view_in,
)
from .prompt import CoreTemplate, DebriefTemplate, RenderedPrompt, debrief_messages, render
from .reply import START_AFTER_SECONDS, START_AT_DISTANCE, ParsedReply, ReplyContext, Step, parse_debrief, reply_parser
from .scenario import Scenario
from .view import CONDITION_INDEPENDENT, CONDITION_TALK, CONDITIONS

# How a session can end.
SESSION_COMPLETED = "completed"  # an encounter took place and was recorded to its end
SESSION_NO_ENCOUNTER = "no_encounter"  # the trigger never fired: nobody was prompted
SESSION_ABORTED = "aborted"  # the budget guard refused, or the model could not be used
SESSION_OUTCOMES = (SESSION_COMPLETED, SESSION_NO_ENCOUNTER, SESSION_ABORTED)

# How an encounter can end.
END_PASSED = "passed"
END_NO_CONFLICT = "no_conflict"
END_DEADLOCK = "deadlock"
END_TIME_LIMIT = "time_limit"
END_ORCA_TOOK_OVER = "orca_took_over"  # not resolved by the LLM: ORCA took it over
END_COLLISION = "collision"  # the run stopped on a collision (a scenario with on_collision: stop)
END_REASONS = (END_PASSED, END_NO_CONFLICT, END_DEADLOCK, END_TIME_LIMIT, END_ORCA_TOOK_OVER, END_COLLISION)
#: The ends that leave the encounter not resolved by the LLM, whatever is still predicted.
NOT_RESOLVED_ENDS = (END_ORCA_TOOK_OVER, END_DEADLOCK, END_COLLISION)
#: The reason a release names when the protocol hands the encounter to ORCA.
RELEASE_NOT_RESOLVED = "not_resolved_by_llm"

# Why a decision point fired (each logged with the agent it concerns, "reason:agent").
REASON_TRIGGER = "trigger"  # the agent's first prompt: D4 holds for it
REASON_PERCEIVES = "perceives"  # with the trigger: whom it sees or hears
REASON_HEARD = "heard"
REASON_SIGNALLED = "signalled"
REASON_CAME_INTO_VIEW = "came_into_view"
REASON_PLAN_FAILING = "plan_failing"
REASON_PLAN_ENDED = "plan_ended"
REASON_OTHER = "other_"  # prefix of a change of someone in the encounter: other_stopped, other_moved_left, ...

_EPS = 1e-9


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


# --- settings -------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ProtocolSettings:
    """The protocol's numbers (``docs/parameters.md``, section 8.6, says which are placeholders)."""

    max_decision_points: int = 3  # D5
    min_gap_s: float = 1.0  # D5
    no_conflict_end_s: float = 1.0  # [placeholder]
    max_prompted: Optional[int] = None  # the cap on prompted people per encounter (D11, D12); None: no cap
    speech_words_per_second: float = 2.5  # [placeholder]
    execution: str = EXECUTION_RF4  # issue #64: how a plan is carried out (execute.EXECUTIONS)

    KEYS = ("max_decision_points", "min_gap_s", "no_conflict_end_s", "max_prompted", "speech_words_per_second", "execution")

    def __post_init__(self) -> None:
        if self.max_decision_points < 1:
            raise ConfigError("protocol.max_decision_points: at least 1")
        if self.max_prompted is not None and (isinstance(self.max_prompted, bool) or not isinstance(self.max_prompted, int) or self.max_prompted < 2):
            raise ConfigError(f"protocol.max_prompted: a whole number of at least 2, or null, got {self.max_prompted!r}")
        if self.speech_words_per_second <= 0.0:
            raise ConfigError("protocol.speech_words_per_second: more than 0")
        if self.execution not in EXECUTIONS:
            raise ConfigError(f"protocol.execution: one of {EXECUTIONS}, got {self.execution!r}")

    @classmethod
    def from_mapping(cls, raw: Any, where: str = "protocol") -> "ProtocolSettings":
        block = check_keys(raw or {}, where, (), cls.KEYS)
        default = cls()
        return cls(
            max_decision_points=int(as_number(block.get("max_decision_points", default.max_decision_points), f"{where}.max_decision_points", minimum=1)),
            min_gap_s=as_number(block.get("min_gap_s", default.min_gap_s), f"{where}.min_gap_s", minimum=0.0),
            no_conflict_end_s=as_number(block.get("no_conflict_end_s", default.no_conflict_end_s), f"{where}.no_conflict_end_s", minimum=0.0),
            max_prompted=block.get("max_prompted", default.max_prompted),
            speech_words_per_second=as_number(block.get("speech_words_per_second", default.speech_words_per_second), f"{where}.speech_words_per_second", minimum=0.0, strict_minimum=True),
            execution=as_choice(block.get("execution", default.execution), f"{where}.execution", EXECUTIONS),
        )

    def decision_points_for(self, condition: str) -> int:
        """At most this many decision points per agent in ``condition`` (D3)."""
        return 1 if condition == CONDITION_INDEPENDENT else self.max_decision_points

    def as_dict(self) -> dict[str, Any]:
        described = asdict(self)
        if self.execution == EXECUTION_RF4:  # issue #64: named only when not the default, so older records read as before
            del described["execution"]
        return described


# --- coding a plan mechanically (task 9) ----------------------------------------------------------


def code_plan(steps: Sequence[Step], current_speed_mps: float) -> dict[str, Any]:
    """A plan coded mechanically: the side of its turns, whether it slows (a speed below the
    current one, as the agent was told it: to 0.01 m/s, issue #64), stops, or backs up, and when
    it starts."""
    told = round(current_speed_mps, 2)  # issue #64: 1.3 against 1.30005 is not slowing down
    sides = {step.turn.to for step in steps if step.turn is not None and step.turn.degrees > 0.0}
    start = steps[0].start if steps else None
    return {
        "carry_on": not steps,
        "n_steps": len(steps),
        "side": "none" if not sides else sides.pop() if len(sides) == 1 else "both",
        "slowed": any(step.speed_mps is not None and step.speed_mps < told - _EPS for step in steps),
        "stopped": any(step.speed_mps == 0.0 for step in steps),
        "backed_up": any(step.back_up_m is not None for step in steps),
        "start_distance_m": start.value if start is not None and start.kind == START_AT_DISTANCE else None,
        "start_after_s": start.value if start is not None and start.kind == START_AFTER_SECONDS else None,
    }


# --- one agent across the encounter ---------------------------------------------------------------


@dataclass
class _Member:
    agent_id: int
    slot: int  # its place in the encounter's member list
    partner: Optional[int] = None
    perceiver: Optional[Perceiver] = None
    prompts: int = 0
    last_prompt_s: float = -math.inf
    #: The driver decision behind each of the perceiver's decisions, in order.
    driver_decisions: list[int] = field(default_factory=list)
    replies: list[ParsedReply] = field(default_factory=list)
    last_prompt: Optional[RenderedPrompt] = None  # of its last readable decision
    last_raw: Optional[str] = None
    clear_since_decision: bool = False
    ended_noticed: int = 0  # how many of its plans' ends it has been prompted for
    smallest_gap_m: float = math.inf  # since its last decision point
    open_record: Optional[dict[str, Any]] = None  # its latest decision point, until what came of it is known


# --- one session ----------------------------------------------------------------------------------


class EncounterSession:
    """One session: an encounter in one case's run, under one condition.

    ``simulation`` is the case's source run, built and not yet stepped (``simulation_for``);
    ``pair`` the case's two people, who can start the encounter. ``people`` gives each agent's
    ``age``, ``gender`` and ``errand`` (the design's two people; anyone else has none), and
    ``show_age``/``show_gender`` are the visibility switches. ``factors`` are the session's core
    and situational factors (RF-5, :class:`~negsim.resolution.factors.SessionFactors`): their lines
    go into every view. ``pairwise`` are its pairwise perception factors (RF-6,
    :class:`~negsim.resolution.pairwise.PairwiseFactors`): each agent's view gets only its own
    lines, under the people it sees. ``labels`` go with every request, as its metadata (never sent
    to a provider).
    """

    def __init__(
        self,
        simulation: Any,
        pair: Sequence[int],
        scenario: Scenario,
        condition: str,
        client: LLMClient,
        llm: LLMSettings,
        settings: Optional[ProtocolSettings] = None,
        view_settings: Optional[LLMViewSettings] = None,
        core: Optional[CoreTemplate] = None,
        debrief: Optional[DebriefTemplate] = None,
        people: Optional[Mapping[Any, Mapping[str, Any]]] = None,
        show_age: bool = True,
        show_gender: bool = True,
        labels: Optional[Mapping[str, Any]] = None,
        factors: Optional[Any] = None,
        pairwise: Optional[Any] = None,
    ):
        if condition not in CONDITIONS:
            raise ConfigError(f"condition: one of {CONDITIONS}, got {condition!r}")
        if simulation.plans is not None or simulation.world.step_index != 0:
            raise ValueError("the session needs its case's run fresh: built, not stepped, with no plan driver")
        self.sim, self.pair, self.scenario, self.condition = simulation, tuple(int(a) for a in pair), scenario, condition
        self.client, self.llm = client, llm
        self.settings = settings or ProtocolSettings()
        self.view_settings = view_settings or LLMViewSettings.load()
        from .prompt import default_core

        # resolve_v3 when the session has factor lines (issue #61), as the experiment layer chooses
        self.core = core or CoreTemplate.load(default_core(factors is not None or pairwise is not None))
        self.debrief_template = debrief or DebriefTemplate.load()
        self.people, self.show_age, self.show_gender = people, show_age, show_gender
        self.factors, self.pairwise = factors, pairwise
        self.labels = dict(labels or {})
        self.max_dp = self.settings.decision_points_for(condition)

        self.outcome: Optional[str] = None
        self.error: Optional[str] = None
        self.run: Optional[PlanRun] = None
        self.exchange = Exchange(self.view_settings)
        self.members: dict[int, _Member] = {}
        self.order: list[int] = []
        self.left_out: list[int] = []
        self.pairs: list[tuple[int, int]] = []
        self.trigger: Optional[dict[str, Any]] = None
        self.end: Optional[dict[str, Any]] = None
        self.release: Optional[dict[str, Any]] = None
        self.decision_points: list[dict[str, Any]] = []
        self.debriefs: list[dict[str, Any]] = []
        self._pending_speech: list[tuple[float, int, str]] = []
        self._last_conflict_s = -math.inf

    # --- the run ----------------------------------------------------------------------------

    @property
    def _finished(self) -> bool:
        sim = self.sim
        return sim.status is not None or sim.world.step_index >= sim.spec.max_steps

    def run_session(self) -> str:
        """Run the session to its end, debrief, and return its outcome. A refusal of the budget
        guard, or a model that cannot be used, is recorded as ``aborted`` and raised."""
        try:
            if not self._find_trigger():
                self.outcome = SESSION_NO_ENCOUNTER
                self.end = self._end_record(self._run_end_reason() or END_TIME_LIMIT)
                return self.outcome
            self._encounter()
            self._debrief()
        except _Stopped as stopped:
            self.outcome, self.error = SESSION_ABORTED, f"{type(stopped.cause).__name__}: {stopped.cause}"
            raise stopped.cause
        self.outcome = SESSION_COMPLETED
        return self.outcome

    def _find_trigger(self) -> bool:
        a, b = self.pair
        while not self._finished:
            for observer, other in ((a, b), (b, a)):
                if self._d4(observer, other):
                    self._start(observer, other)
                    return True
            self.sim.step()
        return False

    def _start(self, observer: int, other: int) -> None:
        sim = self.sim
        members = [int(m) for m in self.scenario.encounter_members(sim, observer, other)]
        if members[:2] != [observer, other] or len(set(members)) != len(members):
            raise ValueError(f"{type(self.scenario).__name__}.encounter_members must list the two who started it first, once each")
        cap = self.settings.max_prompted
        if cap is not None and len(members) > cap:
            members, self.left_out = members[:cap], members[cap:]
        self.order = members
        self.members = {agent: _Member(agent, slot) for slot, agent in enumerate(members)}
        self.pairs = [(observer, other)] + [
            (p, q) for k, p in enumerate(members) for q in members[k + 1:]
            if {p, q} != {observer, other} and self.scenario.conflict_predicted(sim, p, q)
        ]
        self.trigger = {"step": sim.world.step_index, "time_s": round(sim.world.time, 6), "agent_id": observer, "other_id": other}
        self.run = PlanRun(sim, MODE_PLAN_ONLY, self.scenario, members, self.settings.execution)
        self._last_conflict_s = sim.world.time

    def _encounter(self) -> None:
        sim = self.sim
        while True:
            self._deliver_speech()
            reason = self._end_reason()
            if reason is not None:
                break
            due = []
            for agent in self.order:
                member = self.members[agent]
                if sim.world.agents[agent].done:
                    continue
                if member.prompts == 0:
                    partner = self._first_partner(agent)
                    if partner is not None:
                        due.append((agent, partner, [REASON_TRIGGER, f"{REASON_PERCEIVES}:{partner}"]))
                elif member.prompts < self.max_dp and sim.world.time - member.last_prompt_s >= self.settings.min_gap_s - _EPS:
                    reasons = self._d5(member)
                    if reasons:
                        due.append((agent, member.partner, reasons))
            if due:
                self._decision_point(due)
            if self._llm_done() and self._conflict_now() and self.run.driver.active:
                self.run.release(RELEASE_NOT_RESOLVED)
                self.release = {"step": sim.world.step_index, "reason": RELEASE_NOT_RESOLVED}
                reason = END_ORCA_TOOK_OVER
                break
            sim.step()
            self._after_step()
        self.end = self._end_record(reason)
        for member in self.members.values():
            self._close(member, reason)

    # --- D4 and D5 --------------------------------------------------------------------------

    def _bodies(self) -> tuple[list[Any], dict[int, Any]]:
        bodies = bodies_in(self.sim)
        return bodies, {body.agent_id: body for body in bodies}

    def _heard_from(self, listener: int, speaker: int, since_s: float) -> bool:
        return any(
            said.speaker_id == speaker and listener in said.heard_by and since_s < said.time_s <= self.sim.world.time + _EPS
            for said in self.exchange.utterances
        )

    def _d4(self, observer: int, other: int, since_s: float = -math.inf) -> bool:
        """D4 for ``observer`` toward ``other``: perceives them, the distance shrinks, a conflict is predicted."""
        agents = self.sim.world.agents
        if agents[observer].done or agents[other].done:
            return False
        bodies, by_id = self._bodies()
        me, them = by_id[observer], by_id[other]
        if not (sees(me, them, bodies, self.sim.world.obstacles, self.view_settings) or self._heard_from(observer, other, since_s)):
            return False
        rx, ry = them.position[0] - me.position[0], them.position[1] - me.position[1]
        vx, vy = them.velocity[0] - me.velocity[0], them.velocity[1] - me.velocity[1]
        if rx * vx + ry * vy >= 0.0:  # the distance is not shrinking
            return False
        return self.scenario.conflict_predicted(self.sim, observer, other)

    def _first_partner(self, agent: int) -> Optional[int]:
        """The nearest member for whom D4 holds, if any (ties by agent id)."""
        since = self.trigger["time_s"] - _EPS
        here = self.sim.world.agents[agent].pose.xy
        found = [
            (math.dist(here, self.sim.world.agents[other].pose.xy), other)
            for other in self.order if other != agent and self._d4(agent, other, since)
        ]
        return min(found)[1] if found else None

    def _conflict_with_others(self, agent: int) -> bool:
        return any(self.scenario.conflict_predicted(self.sim, agent, other) for other in self.order if other != agent)

    def _conflict_now(self) -> bool:
        return any(self.scenario.conflict_predicted(self.sim, p, q) for k, p in enumerate(self.order) for q in self.order[k + 1:])

    def _plan_of(self, member: _Member) -> Any:
        return self.run.driver.plans.get(member.agent_id)

    def _plan_ended(self, member: _Member) -> bool:
        """Its latest plan had steps and has been carried out, and it has not been asked since."""
        plan = self._plan_of(member)
        ended = plan is not None and plan.steps and plan.state == COMPLETED
        return bool(ended) and member.ended_noticed < plan.decision_point

    def _d5(self, member: _Member) -> list[str]:
        """Why ``member`` is to be prompted again (D5), or nothing."""
        if self.max_dp <= 1:
            return []
        ended = self._plan_ended(member)
        if not (ended or self._conflict_with_others(member.agent_id)):
            return []
        sim, settings = self.sim, self.view_settings
        agent = member.agent_id
        last = member.perceiver.looks[-1] if member.perceiver.looks else None
        since = last.time_s if last is not None else self.trigger["time_s"] - _EPS
        reasons: list[str] = []
        bodies, by_id = self._bodies()
        observer = by_id[agent]
        visible = in_sight(observer, bodies, sim.world.obstacles, settings)
        seen_then = {} if last is None else last.seen
        for body in visible:
            other = body.agent_id
            if other not in seen_then:
                reasons.append(f"{REASON_CAME_INTO_VIEW}:{other}")
            elif other in self.members:
                reasons += [f"{REASON_OTHER}{change}:{other}" for change in changes_since(seen_then[other], body, observer.facing_rad, settings)]
        for made in self.exchange.signals:
            if made.signaller_id != agent and agent in made.seen_by and since < made.time_s <= sim.world.time + _EPS:
                reasons.append(f"{REASON_SIGNALLED}:{made.signaller_id}")
        for said in self.exchange.utterances:
            if said.speaker_id != agent and agent in said.heard_by and since < said.time_s <= sim.world.time + _EPS:
                reasons.append(f"{REASON_HEARD}:{said.speaker_id}")
        if member.clear_since_decision and self._failing(member):
            reasons.append(REASON_PLAN_FAILING)
        if ended:
            reasons.append(REASON_PLAN_ENDED)
        return list(dict.fromkeys(reasons))

    def _failing(self, member: _Member) -> bool:
        """The closest approach to its partner at the present velocities is below the safety distance."""
        agents = self.sim.world.agents
        if member.partner is None or agents[member.partner].done:
            return False
        a, b = agents[member.agent_id], agents[member.partner]
        rx, ry = b.pose.x - a.pose.x, b.pose.y - a.pose.y
        vx, vy = b.velocity[0] - a.velocity[0], b.velocity[1] - a.velocity[1]
        v2 = vx * vx + vy * vy
        if v2 <= 0.0:
            return False
        t = -(rx * vx + ry * vy) / v2
        if t <= 0.0:
            return False
        return math.hypot(rx + vx * t, ry + vy * t) < safety_distance(self.sim, member.agent_id, member.partner)

    def _llm_done(self) -> bool:
        """Every prompted member has used its decision points and has no plan left to carry out."""
        prompted = [member for member in self.members.values() if member.prompts > 0]
        if not prompted:
            return False
        for member in prompted:
            plan = self._plan_of(member)
            if member.prompts < self.max_dp and not self.sim.world.agents[member.agent_id].done:
                return False
            if plan is not None and plan.state in (WAITING, RUNNING):
                return False
        return True

    # --- one decision point -----------------------------------------------------------------

    def _decision_point(self, due: Sequence[tuple[int, int, list[str]]]) -> None:
        """Prompt every agent in ``due`` on the same world state, then carry out their replies."""
        sim = self.sim
        now, step = sim.world.time, sim.world.step_index
        asked = []
        for agent, partner, reasons in due:
            member = self.members[agent]
            if member.perceiver is None:
                member.partner = partner
                member.perceiver = perceiver_for(
                    sim, agent, partner, self.scenario, self.view_settings, self.core,
                    people=self.people, show_age=self.show_age, show_gender=self.show_gender, since_s=self.trigger["time_s"] - _EPS,
                )
            outcomes = self.run.driver.outcomes(agent)
            view = view_in(sim, member.perceiver, self.exchange, outcomes=[outcomes[k] for k in member.driver_decisions], **self._factor_lines(agent))
            prompt = render(view, self.condition, self.scenario, self.core)
            context = ReplyContext.of(view, self.condition, self.scenario.events, self.core.later_step_start)
            metadata = {
                **self.labels, "kind": "decision", "agent_id": agent, "agent_slot": member.slot,
                "decision_point": member.prompts + 1, "step": step,
            }
            try:
                reply = request_with_retry(
                    self.client, [dict(m) for m in prompt.messages], self.llm.model, self.llm.temperature, self.llm.max_tokens,
                    self.llm.thinking, metadata, reply_parser(context), self.core.retry(self.condition),
                )
            except Exception as exc:  # refused before anything was sent for this agent
                self._keep_unapplied(asked, now, step)
                raise _Stopped(exc) from exc
            asked.append((member, partner, reasons, view, prompt, reply))
            if reply.stopped is not None:
                self._keep_unapplied(asked, now, step)
                raise _Stopped(reply.stopped)
        bodies, by_id = self._bodies()
        for member, partner, reasons, view, prompt, reply in asked:
            self._close(member, "decision_point")
            agent = member.agent_id
            member.prompts += 1
            member.last_prompt_s = now
            member.clear_since_decision = False
            member.smallest_gap_m = math.inf
            plan = self._plan_of(member)
            if plan is not None:
                member.ended_noticed = max(member.ended_noticed, plan.decision_point)
            parsed: Optional[ParsedReply] = reply.parsed
            given: Optional[list[dict[str, Any]]] = None
            if parsed is not None:
                self.run.driver.give(sim, agent, parsed.steps, member.partner)
                given = [s.as_dict() for s in parsed.steps]
                member.driver_decisions.append(self._next_decision_index(agent))
                member.perceiver.decided(now, by_id[agent], parsed.intent, parsed.message, parsed.signal)
                member.replies.append(parsed)
                member.last_prompt, member.last_raw = prompt, reply.attempts[-1].raw_output
                if parsed.signal != "none":
                    # Made during the step after the decision: after everyone looked at this
                    # decision point, so that it is new to them (perceive counts what came after a look).
                    self.exchange.signal(now + sim.world.dt, agent, parsed.signal, bodies, sim.world.obstacles)
                if parsed.message and self.condition == CONDITION_TALK:
                    words = max(1, len(parsed.message.split()))
                    self._pending_speech.append((now + words / self.settings.speech_words_per_second, agent, parsed.message))
            else:
                member.perceiver.looks.pop()  # it made no decision: its next view is from its last look
                if plan is None:
                    self.run.driver.give(sim, agent, (), member.partner)  # it carries on as it is
                    given = []
            self._record(member, reasons, view, prompt, reply, given, now, step)

    def _factor_lines(self, agent: int) -> dict[str, Any]:
        """The lines of the session's factors in ``agent``'s view (RF-5): its own, its notes, what
        it is told of everyone it sees, and the setting; and how it sees each of them (RF-6), which
        is in its view only. Nothing without factors."""
        lines: dict[str, Any] = {}
        if self.factors is not None:
            lines.update({
                "own_lines": self.factors.own(agent), "notes": self.factors.notes(agent),
                "factor_lines": self.factors.seen_lines(), "situation_lines": self.factors.place(),
            })
        if self.pairwise is not None:
            lines["pairwise_lines"] = self.pairwise.lines_for(agent)
        return lines

    def _next_decision_index(self, agent: int) -> int:
        """The index, among ``agent``'s driver decisions, of the plan just given (taken up next step)."""
        return len(self.run.driver.outcomes(agent)) + sum(
            1 for entries in self.run.driver._pending.values() for entry in entries if entry[0] == agent
        ) - 1

    def _keep_unapplied(self, asked: Sequence[tuple], now: float, step: int) -> None:
        """The session is stopping: record every reply of this decision point received so far,
        none of them carried out, so that nothing paid for is lost (D13)."""
        for member, _, reasons, view, prompt, reply in asked:
            self._record(member, reasons, view, prompt, reply, None, now, step, number=member.prompts + 1)

    def _record(self, member, reasons, view, prompt, reply, given, now, step, number: Optional[int] = None) -> None:
        parsed = reply.parsed
        record = {
            "index": len(self.decision_points) + 1,
            "agent_id": member.agent_id,
            "partner_id": member.partner,
            "number": member.prompts if number is None else number,
            "step": step,
            "time_s": round(now, 6),
            "trigger_reasons": list(reasons),
            "view": view.as_dict(),
            "prompt": prompt.as_dict(),
            "attempts": [attempt.as_dict() for attempt in reply.attempts],
            "parse_error": reply.failure,
            "parsed": None if parsed is None else parsed.as_dict(),
            "plan_given": given,
            "coded": None if parsed is None else code_plan(parsed.steps, view.me.speed_mps),
            "until_next": None,
        }
        self.decision_points.append(record)
        member.open_record = record

    def _close(self, member: _Member, ended_by: str) -> None:
        """What came of ``member``'s latest decision point, now that its next one (or the end) is here."""
        record = member.open_record
        if record is None:
            return
        plan = self._plan_of(member)
        record["until_next"] = {
            "time_s": round(self.sim.world.time, 6),
            "ended_by": ended_by,
            "plan_state": None if plan is None else plan.state,
            "plan_outcome": None if plan is None else plan.outcome,
            "smallest_gap_m": None if math.isinf(member.smallest_gap_m) else round(member.smallest_gap_m, 6),
        }
        member.open_record = None

    # --- between decision points ------------------------------------------------------------

    def _deliver_speech(self) -> None:
        now = self.sim.world.time
        due = [item for item in self._pending_speech if item[0] <= now + _EPS]
        if not due:
            return
        self._pending_speech = [item for item in self._pending_speech if item[0] > now + _EPS]
        bodies, _ = self._bodies()
        for _, speaker, message in due:
            if not self.sim.world.agents[speaker].done:
                self.exchange.say(now, speaker, message, bodies)

    def _after_step(self) -> None:
        sim = self.sim
        agents = sim.world.agents
        for member in self.members.values():
            if member.prompts and not member.clear_since_decision and not self._failing(member):
                member.clear_since_decision = True
        for k, p in enumerate(self.order):
            for q in self.order[k + 1:]:
                if agents[p].done or agents[q].done:
                    continue
                gap = math.dist(agents[p].pose.xy, agents[q].pose.xy) - agents[p].spec.radius - agents[q].spec.radius
                for agent in (p, q):
                    member = self.members[agent]
                    member.smallest_gap_m = min(member.smallest_gap_m, gap)
        if self._conflict_now():
            self._last_conflict_s = sim.world.time

    # --- the end ----------------------------------------------------------------------------

    def _run_end_reason(self) -> Optional[str]:
        sim = self.sim
        if sim.status == STATUS_DEADLOCK or sim.deadlock:
            return END_DEADLOCK
        if sim.status == STATUS_COLLISION:
            return END_COLLISION
        if sim.status == STATUS_COMPLETED:
            return END_PASSED
        if sim.status is not None or sim.world.step_index >= sim.spec.max_steps:
            return END_TIME_LIMIT
        return None

    def _end_reason(self) -> Optional[str]:
        reason = self._run_end_reason()
        if reason is not None:
            return reason
        agents, margin = self.sim.world.agents, self.sim.spec.single_file_safety_margin
        # Two people standing still can read as separating by a rounding error, so a pair has
        # passed only if no conflict between them is predicted any more.
        if all(
            agents[p].done or agents[q].done or (self.sim._passed(p, q, margin) and not self.scenario.conflict_predicted(self.sim, p, q))
            for p, q in self.pairs
        ):
            return END_PASSED
        if self.sim.world.time - self._last_conflict_s >= self.settings.no_conflict_end_s - _EPS:
            return END_NO_CONFLICT
        return None

    def _end_record(self, reason: str) -> dict[str, Any]:
        sim = self.sim
        still = self.run is not None and reason != END_PASSED and self._conflict_now()
        return {
            "reason": reason,
            "step": sim.world.step_index,
            "time_s": round(sim.world.time, 6),
            "conflict_still_predicted": still,
            "not_resolved_by_llm": reason in NOT_RESOLVED_ENDS or (reason == END_TIME_LIMIT and still),
        }

    # --- the debrief (D8) -------------------------------------------------------------------

    def _debrief(self) -> None:
        for agent in self.order:
            member = self.members[agent]
            if not member.replies:
                continue
            messages, templates = debrief_messages(member.last_prompt, member.last_raw or "", member.replies, self.debrief_template)
            metadata = {**self.labels, "kind": "debrief", "agent_id": agent, "agent_slot": member.slot, "decision_point": None}
            try:
                reply = request_with_retry(
                    self.client, messages, self.llm.model, self.llm.temperature, self.llm.max_tokens, self.llm.thinking,
                    metadata, parse_debrief, self.debrief_template.retry(),
                )
            except Exception as exc:
                raise _Stopped(exc) from exc
            self.debriefs.append({
                "agent_id": agent,
                "templates": templates,
                "attempts": [attempt.as_dict() for attempt in reply.attempts],
                "parse_error": reply.failure,
                "parsed": None if reply.parsed is None else reply.parsed.as_dict(),
            })
            if reply.stopped is not None:
                raise _Stopped(reply.stopped)

    # --- what is recorded -------------------------------------------------------------------

    def attempts(self) -> list[dict[str, Any]]:
        return [a for dp in self.decision_points for a in dp["attempts"]] + [a for d in self.debriefs for a in d["attempts"]]

    def totals(self) -> dict[str, Any]:
        tokens = Usage().as_dict()
        for attempt in self.attempts():
            for key in tokens:
                tokens[key] += attempt["usage"].get(key, 0)
        return {
            "decision_points": len(self.decision_points),
            "debriefs": len(self.debriefs),
            "llm_calls": len(self.attempts()),
            "retries": sum(len(dp["attempts"]) - 1 for dp in self.decision_points) + sum(len(d["attempts"]) - 1 for d in self.debriefs),
            "tokens": tokens,
            "cost_usd": round(sum(a["cost_usd"] for a in self.attempts()), 10),
        }

    def as_dict(self) -> dict[str, Any]:
        driver = None if self.run is None else self.run.driver
        return {
            "outcome": self.outcome,
            "error": self.error,
            "condition": self.condition,
            "protocol": self.settings.as_dict(),
            "llm_view": self.view_settings.as_dict(),
            "max_decision_points_per_agent": self.max_dp,
            "max_attempts_per_call": MAX_ATTEMPTS_PER_TURN,
            "encounter": {
                "agents": list(self.order),
                "pairs": [list(pair) for pair in self.pairs],
                "left_out_by_cap": list(self.left_out),
                "trigger": self.trigger,
                "start_step": None if self.trigger is None else self.trigger["step"],
                "end": self.end,
                "orca_took_over": self.release,
                "prompted": [agent for agent in self.order if self.members[agent].prompts > 0],
            },
            "decision_points": self.decision_points,
            "debriefs": self.debriefs,
            "utterances": [
                {"time_s": round(u.time_s, 6), "speaker_id": u.speaker_id, "message": u.message,
                 "heard_by": {str(k): list(v) for k, v in sorted(u.heard_by.items())}}
                for u in self.exchange.utterances
            ],
            "signals": [
                {"time_s": round(s.time_s, 6), "signaller_id": s.signaller_id, "signal": s.signal, "seen_by": sorted(s.seen_by)}
                for s in self.exchange.signals
            ],
            "decisions": [] if driver is None else driver.decisions_record(),
            "release": self.release,
            "totals": self.totals(),
        }


class _Stopped(Exception):
    """The session must stop: the budget guard refused, or the model could not be used."""

    def __init__(self, cause: Exception):
        super().__init__(str(cause))
        self.cause = cause
