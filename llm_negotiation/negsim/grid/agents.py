"""LLM agents on the grid: one session (issue #140, RF-51; ``docs/action-space.md``, section 8).

Two people walk towards each other on RF-50's grid (:func:`negsim.grid.world.head_on`). Each is an
LLM agent, asked only at decision points, and carries out what it chose between them. The
session runs RF-50's tick update (:func:`negsim.grid.world.step`) in a loop of its own that ends as
:func:`negsim.grid.world.run` does (everyone arrived, a deadlock, or the time limit), with the
decision points before each tick.

**When an agent is asked** (D4 and D5 on the grid; the assistant's reading, for the user):

- **a meeting is predicted** when the other person is in view (RF-40's seeing range and half-angle,
  between cell centres), ahead of the agent along its way, and at most one lane from it. Two lanes
  apart is 0.8 m between centres, inside H1, so no meeting; one lane apart is 0.4 m, closer than
  two bodies (RF-50's "squeezed past"). The first decision point is the first tick at which this
  holds;
- **asked again** while a meeting is still predicted and the two have not passed, at least
  ``min_gap_s`` after its last decision point (D5's 1 s: 4 ticks), when the other has done something
  new since it last looked (moved lanes, stopped, started, slowed, sped up, walked backwards, came
  into view), or its own plan has ended (a wait, a step aside, a step back), or its move was blocked
  (the cell was taken, a crossing, or a contest lost); at most ``max_decision_points`` times (6).

Both are asked at the same tick in the order :func:`negsim.resolution.experiment.first_asked`
gives; the world does not move between them (silent: neither hears the other's choice).

**Between decisions** (``docs/action-space.md``, section 8.2): the moves of the chosen option first
(:mod:`negsim.grid.menu`; a lane change while walking, a wait, a step back), then forward, at the
option's speed until the other has passed. A move into a taken cell is tried again on the next tick
(and the agent may be asked again); a move into a wall is dropped. An unreadable reply after the
retry changes nothing: the agent goes on with what it was doing (as ``EncounterSession`` does).

**The debrief** (D8) follows the run: each agent that decided is asked for the reference behind
its decisions, with ``resolve_debrief_v3`` (each decision listed by the option chosen).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Mapping, Optional, Sequence

from ..llm.base import LLMClient, LLMFatalError
from ..llm.budget import BudgetExceededError
from ..negotiation.protocol import request_with_retry
from ..resolution.perceive import Body, LLMViewSettings, in_cone
from ..resolution.prompt import DebriefTemplate, RenderedPrompt, debrief_messages
from ..resolution.reply import ParsedReply, ReplyContext, parse_debrief, parse_reply
from ..rulegen.protocol import LLMSettings
from .measures import gate_columns, pair_outcome
from .menu import CARRY_ON, GridPlan, left_wall_of, plan_for, side_of
from .prompt import GridDone, GridMe, GridSeen, GridTemplate, GridView
from .world import GridConfig, GridState, Move, Run, Tick, Walker, head_on, step

CONDITION = "silent"
#: The until events a menu option may name (RF-47's slow-downs end when the other has passed).
EVENTS = ("other_passes",)
#: Moves that did not happen because of someone else: the agent may be asked again.
BLOCKERS = ("occupied", "crossing", "contest_lost")
COMPLETED, ABORTED = "completed", "aborted"


@dataclass
class _Decision:
    tick: int
    intent: str
    row: int
    lane: int
    plan: GridPlan
    replaced: bool = False


@dataclass
class _Member:
    walker_id: int
    slot: int
    usual_mps: float
    plan: GridPlan = CARRY_ON
    queue: list[Move] = field(default_factory=list)
    plan_ended: bool = False
    blocked: bool = False
    prompts: int = 0
    last_tick: Optional[int] = None
    last_look: Optional[dict[str, Any]] = None  # what it saw of the other at its last decision
    decisions: list[_Decision] = field(default_factory=list)
    replies: list[ParsedReply] = field(default_factory=list)
    last_prompt: Optional[RenderedPrompt] = None
    last_raw: Optional[str] = None


class _Stopped(Exception):
    pass


class GridSession:
    """One head-on session on the grid with two LLM agents (walkers 0 and 1)."""

    def __init__(
        self,
        config: GridConfig,
        lanes: Sequence[int],
        seed: int,
        template: GridTemplate,
        client: LLMClient,
        llm: LLMSettings,
        debrief: DebriefTemplate,
        people: Optional[Mapping[int, Mapping[str, Any]]] = None,
        show_age: bool = True,
        show_gender: bool = True,
        factors: Optional[Any] = None,
        pairwise: Optional[Any] = None,
        labels: Optional[Mapping[str, Any]] = None,
        first_asked: int = 0,
        view_settings: Optional[LLMViewSettings] = None,
        max_decision_points: int = 6,
        min_gap_s: float = 1.0,
        usual_speed_mps: Optional[float] = None,
    ):
        if first_asked not in (0, 1):
            raise ValueError(f"first_asked: walker 0 or 1, got {first_asked!r}")
        usual = config.reference_speed_mps if usual_speed_mps is None else float(usual_speed_mps)
        self.config, self.seed, self.template, self.client, self.llm = config, int(seed), template, client, llm
        self.debrief_template = debrief
        self.state: GridState = head_on(config, lanes, seed, speeds=(usual, usual))
        self.people, self.show_age, self.show_gender = people or {}, show_age, show_gender
        self.factors, self.pairwise = factors, pairwise
        self.labels = dict(labels or {})
        self.order = (first_asked, 1 - first_asked)
        self.view_settings = view_settings or LLMViewSettings.load()
        self.max_dp = int(max_decision_points)
        self.min_gap_ticks = math.ceil(min_gap_s / config.tick_s - 1e-9)
        self.members = {w.id: _Member(w.id, w.id, usual) for w in self.state.walkers}
        self.last_action: dict[int, Any] = {}
        self.passed = False
        self.decision_points: list[dict[str, Any]] = []
        self.debriefs: list[dict[str, Any]] = []
        self.outcome: Optional[str] = None
        self.error: Optional[str] = None
        self.run: Optional[Run] = None

    # --- the run ------------------------------------------------------------------------------

    def run_session(self) -> str:
        state, config = self.state, self.config
        ticks = [Tick(state.tick, state.positions(), [])]
        still, ended_by = 0, "timeout"
        try:
            while state.tick < config.max_ticks:
                if not state.active():
                    ended_by = "all_arrived"
                    break
                self._update_passed()
                if not self.passed:
                    self._decide()
                intents = {w.id: self._intent(w) for w in state.active()}
                actions = step(state, intents)
                ticks.append(Tick(state.tick, state.positions(), actions))
                self._after(actions)
                advanced = any(a.moved[0] * state.walker(a.walker).direction > 0 for a in actions)
                still = 0 if advanced else still + 1
                if not state.active():
                    ended_by = "all_arrived"
                    break
                if still >= config.deadlock_ticks:
                    ended_by = "deadlock"
                    break
            self.run = Run(config, state.seed, list(state.walkers), ticks, ended_by)
            self._debrief()
            self.outcome = COMPLETED
        except _Stopped as stop:
            self.run = Run(config, state.seed, list(state.walkers), ticks, "aborted")
            self.outcome, self.error = ABORTED, f"{type(stop.__cause__).__name__}: {stop.__cause__}"
        return self.outcome

    def _update_passed(self) -> None:
        a, b = self.state.walkers
        if not (a.active and b.active) or (a.row - b.row) * a.direction > 0:
            self.passed = True

    def _intent(self, walker: Walker) -> Move:
        m = self.members[walker.id]
        factor = 1.0 if self.passed else m.plan.speed_factor
        walker.speed_mps = round(m.usual_mps * factor, 2)
        return m.queue[0] if m.queue else Move.FORWARD

    def _after(self, actions: Sequence[Any]) -> None:
        for action in actions:
            m = self.members[action.walker]
            self.last_action[action.walker] = action
            if action.blocked == "not_due" and not (m.queue and m.queue[0] == Move.WAIT):
                continue
            m.blocked = action.blocked in BLOCKERS
            if m.queue:
                head = m.queue[0]
                if head == Move.WAIT or action.blocked in (None, "wall", "not_due"):
                    m.queue.pop(0)
                    if not m.queue:
                        m.plan_ended = True

    # --- what a walker perceives ------------------------------------------------------------

    def _body(self, walker: Walker) -> Body:
        c = self.config
        facing = 0.0 if walker.direction > 0 else math.pi
        return Body(walker.id, (c.x_m(walker.row), c.y_m(walker.lane)), (0.0, 0.0), facing, c.body_radius_m)

    def _sees(self, observer: Walker, other: Walker) -> bool:
        return other.active and in_cone(self._body(observer), self._body(other), self.view_settings)

    def _motion(self, walker: Walker) -> tuple[str, float]:
        """How a walker is moving, from its last tick: walking (at its speed), still or backing."""
        action = self.last_action.get(walker.id)
        if action is None:
            return "walking", walker.speed_mps
        if action.moved[0] * walker.direction < 0:
            return "backing", walker.speed_mps
        if action.moved == (0, 0) and action.blocked != "not_due":
            return "still", 0.0
        return "walking", walker.speed_mps

    def _meeting(self, observer: Walker, other: Walker) -> bool:
        ahead = (other.row - observer.row) * observer.direction
        return self._sees(observer, other) and ahead > 0 and abs(other.lane - observer.lane) <= 1

    def _snapshot(self, observer: Walker, other: Walker) -> dict[str, Any]:
        motion, speed_mps = self._motion(other)
        return {"seen": self._sees(observer, other), "lane": other.lane, "motion": motion, "speed_mps": speed_mps}

    def _changes(self, m: _Member, observer: Walker, other: Walker) -> tuple[tuple[str, ...], int]:
        """What the other did since ``m`` last looked: (changes, lanes moved towards +y)."""
        now = self._snapshot(observer, other)
        last = m.last_look
        if last is None or not now["seen"]:
            return (), 0
        if not last["seen"]:
            return ("came_into_view",), 0
        found = []
        was, is_ = last["motion"], now["motion"]
        if is_ == "backing" and was != "backing":
            found.append("backing_up")
        elif was == "walking" and is_ == "still":
            found.append("stopped")
        elif was == "still" and is_ == "walking":
            found.append("started_walking")
        elif was == is_ == "walking" and now["speed_mps"] < last["speed_mps"] - 1e-9:
            found.append("slowed_down")
        elif was == is_ == "walking" and now["speed_mps"] > last["speed_mps"] + 1e-9:
            found.append("sped_up")
        return tuple(found), other.lane - last["lane"]

    # --- decision points ----------------------------------------------------------------------

    def _decide(self) -> None:
        due = []
        for agent in self.order:
            m = self.members[agent]
            me, other = self.state.walker(agent), self.state.walker(1 - agent)
            if not me.active or not other.active or m.prompts >= self.max_dp or not self._meeting(me, other):
                continue
            if m.prompts == 0:
                due.append((agent, ["trigger"]))
                continue
            if self.state.tick - m.last_tick < self.min_gap_ticks:
                continue
            reasons = []
            changes, moved = self._changes(m, me, other)
            if moved:
                reasons.append("other_moved_lanes")
            reasons += [f"other_{c}" for c in changes]
            if m.plan_ended:
                reasons.append("plan_ended")
            if m.blocked:
                reasons.append("blocked")
            if reasons:
                due.append((agent, reasons))
        for agent, reasons in due:
            self._ask(agent, reasons)

    def _view(self, agent: int) -> GridView:
        m, me, other = self.members[agent], self.state.walker(agent), self.state.walker(1 - agent)
        config, tick = self.config, self.state.tick
        person = self.people.get(agent, {})
        motion, speed_mps = self._motion(me)
        lines = self._factor_lines(agent)
        seen: tuple[GridSeen, ...] = ()
        meet = None
        if self._sees(me, other):
            o_motion, o_speed = self._motion(other)
            ahead = (other.row - me.row) * me.direction
            if o_motion == "walking":
                o_motion = "same_way" if other.direction == me.direction else ("towards" if ahead > 0 else "away")
            changes, moved = self._changes(m, me, other)
            info = self.people.get(1 - agent, {})
            seen = (GridSeen(
                label=1, cells_ahead=ahead, lanes_left=(other.lane - me.lane) * me.direction, lane=other.lane,
                motion=o_motion, speed_mps=o_speed,
                age=info.get("age") if self.show_age else None, gender=info.get("gender") if self.show_gender else None,
                changes=changes, lanes_moved_left=moved * me.direction, lanes_moved_plus_y=moved,
                factor_lines=tuple(lines["seen"]), pairwise_lines=tuple(lines["pairwise"]),
            ),)
            closing = (speed_mps if motion == "walking" else 0.0) + (o_speed if o_motion == "towards" else 0.0)
            if self._meeting(me, other) and closing > 0:
                meet = (1, max(0, ahead - 1) * config.cell_m / closing)
        history = []
        for d in m.decisions:
            moved_plus_y = me.lane - d.lane
            back = -(me.row - d.row) * me.direction
            history.append(GridDone(
                ago_s=round((tick - d.tick) * config.tick_s, 6), intent=d.intent, outcome=self._outcome(m, d),
                lanes_left=moved_plus_y * me.direction, lanes_plus_y=moved_plus_y, cells_back=max(0, back),
            ))
        return GridView(
            agent_id=agent, decision_point=m.prompts + 1, tick=tick,
            me=GridMe(
                m.usual_mps, speed_mps if motion == "walking" else 0.0, motion,
                person.get("age") if self.show_age else None, person.get("gender") if self.show_gender else None,
                person.get("errand"), tuple(lines["own"]),
            ),
            lanes=config.lanes, lane=me.lane, direction=me.direction, cell_m=config.cell_m, tick_s=config.tick_s,
            situation_lines=tuple(lines["place"]), notes=tuple(lines["notes"]), seen=seen, history=tuple(history),
            time_to_meet=meet, template=self.template.identity(),
        )

    def _outcome(self, m: _Member, d: _Decision) -> str:
        if d.replaced:
            return "replaced"
        if d is m.decisions[-1] and d.plan.moves and not m.queue:
            return "completed"
        return "ongoing"

    def _factor_lines(self, agent: int) -> dict[str, Sequence[str]]:
        other = 1 - agent
        lines: dict[str, Sequence[str]] = {"own": (), "notes": (), "seen": (), "place": (), "pairwise": ()}
        if self.factors is not None:
            lines.update(own=self.factors.own(agent), notes=self.factors.notes(agent),
                         seen=self.factors.seen_lines().get(other, ()), place=self.factors.place())
        if self.pairwise is not None:
            lines["pairwise"] = self.pairwise.lines_for(agent).get(other, ())
        return lines

    def _ask(self, agent: int, reasons: Sequence[str]) -> None:
        m, me, other = self.members[agent], self.state.walker(agent), self.state.walker(1 - agent)
        view = self._view(agent)
        messages = self.template.messages(view)
        prompt = RenderedPrompt(tuple(messages), CONDITION, view.decision_point, {"core": self.template.identity()})
        left_wall = left_wall_of(me.direction) if self.template.frame == "absolute" else None
        context = ReplyContext(
            CONDITION, 2.0, EVENTS, None, menu=self.template.menu, usual_speed_mps=m.usual_mps,
            radius_m=self.config.body_radius_m, left_wall=left_wall,
        )
        metadata = {
            **self.labels, "kind": "decision", "agent_id": agent, "agent_slot": m.slot,
            "decision_point": view.decision_point, "tick": self.state.tick,
        }
        try:
            reply = request_with_retry(
                self.client, messages, self.llm.model, self.llm.temperature, self.llm.max_tokens, self.llm.thinking,
                metadata, lambda raw: parse_reply(raw, context), self.template.retry(),
            )
        except (BudgetExceededError, LLMFatalError) as exc:
            raise _Stopped() from exc
        m.prompts += 1
        m.last_tick = self.state.tick
        given = None
        parsed: Optional[ParsedReply] = reply.parsed
        if parsed is not None:
            plan = plan_for(self.template.menu.find(parsed.action), me, self.config)
            if m.decisions and self._outcome(m, m.decisions[-1]) != "completed":
                m.decisions[-1].replaced = True
            m.plan, m.queue, m.plan_ended, m.blocked = plan, list(plan.moves), False, False
            m.decisions.append(_Decision(self.state.tick, parsed.intent, me.row, me.lane, plan))
            m.replies.append(parsed)
            m.last_prompt, m.last_raw = prompt, reply.attempts[-1].raw_output
            m.last_look = self._snapshot(me, other)
            given = plan.as_dict()
        self.decision_points.append({
            "index": len(self.decision_points), "agent_id": agent, "number": m.prompts, "tick": self.state.tick,
            "time_s": round(self.state.tick * self.config.tick_s, 6), "reasons": list(reasons),
            "view": view.as_dict(), "prompt": prompt.as_dict(),
            "attempts": [a.as_dict() for a in reply.attempts], "parse_error": reply.failure,
            "parsed": None if parsed is None else parsed.as_dict(), "plan_given": given,
            "side": side_of(m.plan if parsed is not None else None),
        })
        if reply.stopped is not None:
            raise _Stopped() from reply.stopped

    def _debrief(self) -> None:
        for agent in self.order:
            m = self.members[agent]
            if not m.replies:
                continue
            messages, templates = debrief_messages(m.last_prompt, m.last_raw or "", m.replies, self.debrief_template)
            metadata = {**self.labels, "kind": "debrief", "agent_id": agent, "agent_slot": m.slot, "decision_point": None}
            try:
                reply = request_with_retry(
                    self.client, messages, self.llm.model, self.llm.temperature, self.llm.max_tokens, self.llm.thinking,
                    metadata, partial(parse_debrief, side=self.debrief_template.side_question), self.debrief_template.retry(),
                )
            except (BudgetExceededError, LLMFatalError) as exc:
                raise _Stopped() from exc
            self.debriefs.append({
                "agent_id": agent, "templates": templates, "attempts": [a.as_dict() for a in reply.attempts],
                "parse_error": reply.failure, "parsed": None if reply.parsed is None else reply.parsed.as_dict(),
            })
            if reply.stopped is not None:
                raise _Stopped() from reply.stopped

    # --- the record ---------------------------------------------------------------------------

    def attempts(self) -> list[dict[str, Any]]:
        return [a for p in self.decision_points for a in p["attempts"]] + [a for d in self.debriefs for a in d["attempts"]]

    def as_dict(self) -> dict[str, Any]:
        outcome = pair_outcome(self.run) if self.run is not None and self.outcome == COMPLETED else None
        attempts = self.attempts()
        return {
            "outcome": self.outcome,
            "error": self.error,
            "condition": CONDITION,
            "lanes": [w.start[1] for w in self.state.walkers],
            "seed": self.seed,
            "first_asked": self.order[0],
            "max_decision_points": self.max_dp,
            "min_gap_ticks": self.min_gap_ticks,
            "decision_points": self.decision_points,
            "debriefs": self.debriefs,
            "grid_outcome": outcome,
            "gate_columns": None if outcome is None else gate_columns(outcome),
            "totals": {
                "calls": len(attempts),
                "decision_points": len(self.decision_points),
                "unreadable": sum(1 for p in self.decision_points if p["parsed"] is None),
                "cost_usd": round(sum(a.get("cost_usd") or 0.0 for a in attempts), 9),
            },
        }
