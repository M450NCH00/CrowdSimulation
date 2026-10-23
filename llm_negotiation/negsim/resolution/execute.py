"""Carrying out LLM agents' plans in the simulator (issue #59, RF-4; ``docs/resolution.md``, D1, D6
and D16).

An agent's reply (D1) gives ``steps``. This module has the simulator carry them out, one step
after another, in a running :class:`~negsim.avoidance.simulation.AvoidanceSimulation`:

- ``speed_mps`` sets the preferred speed, clipped to the agent's ``max_speed``; a step without it
  keeps the speed the agent would walk at anyway (its preferred speed, under the run's
  directives);
- ``turn`` offsets the preferred direction from the desired path direction (toward the point
  ``lookahead`` metres further along the path, as plain ORCA aims) by its degrees, to the agent's
  own left or right;
- ``back_up_m`` walks backwards, against the path's direction where the agent is, at the agent's
  ``backing_speed``, until it has backed that far (measured along that direction from where the
  step began). If the step also has an ``until``, it ends at whichever comes first;
- ``start`` delays the first step: until the encounter partner is no further than
  ``at_distance_m`` (centre to centre, as the agent is told distances), or until
  ``after_seconds`` have passed since the decision. Meanwhile the agent carries on as it was;
- ``until`` ends a step after its ``seconds``, or when its event has happened. **The executor
  knows no event**: it asks the scenario plug-in (:meth:`Scenario.happened`, D16).

After the last step the agent steers back towards its goal as usual. An empty plan (``[]``)
changes nothing. Bodies never change size. A later decision of the same agent replaces what is
left of its plan.

**Two modes** (D6):

- ``plan_only``: from the encounter's first decision until it is over, ORCA does not treat the
  encounter's two agents as obstacles to each other, and the arbiter's speed bound does not
  apply to them. ORCA still handles walls and everyone else; everyone outside the encounter is
  plain ORCA. Between the plan's steps (before a delayed start, after the last step) an
  encounter agent walks its path at its own speed, still not steered away from the other. The
  encounter is over when it is released (:meth:`PlanDriver.release`; RF-3 does this when the
  encounter is recorded as not resolved by the LLM and ORCA takes over), when one of the two has
  arrived, or when the two have passed each other with no plan of theirs left to carry out.
- ``plan_orca``: the plan sets the preferred velocity, and everything else runs as in the plain
  run: ORCA in full and, where the scenario has one, the arbiter's speed bound. An agent with no
  step running is plain ORCA, so empty plans reproduce the plain run exactly.

**For RF-3:** :class:`PlanRun` holds a simulation and its driver, and :func:`advance` runs it from
one decision point to the next, returning the :class:`WorldState` there. Every plan given is
logged (:meth:`PlanDriver.decisions_record`) in the form a replay reads back
(``negsim.resolution.replay``), so a live run and its replay are the same run.

**Assumptions of this module** (``WORK_LOG-59.md``), none of them sourced:

- a step with no ``speed_mps`` walks at the agent's own speed;
- a back-up step backs against the path's direction, and with an ``until`` ends at whichever
  comes first;
- in ``plan_only`` the arbiter's bound is lifted as well as ORCA's avoidance, because it too
  steers the two apart; in ``plan_orca`` it stays, because it is part of the plain run;
- the plan is in force from its decision, including any delay before its first step.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Sequence

from .reply import START_AFTER_SECONDS, START_AT_DISTANCE, START_NOW, ReplyContext, Step, _step
from .scenario import EventContext, Scenario
from .view import CONDITION_TALK, OUTCOME_COMPLETED, OUTCOME_ONGOING, OUTCOME_REPLACED

MODE_PLAN_ONLY = "plan_only"
MODE_PLAN_ORCA = "plan_orca"
MODES = (MODE_PLAN_ONLY, MODE_PLAN_ORCA)

# The states of a plan.
WAITING = "waiting"  # given, its first step not yet started
RUNNING = "running"
COMPLETED = "completed"
REPLACED = "replaced"

# Why a step ended (besides the name of its event).
ENDED_SECONDS = "seconds"
ENDED_BACKED_UP = "backed_up"
ENDED_REPLACED = "replaced"
ENDED_ARRIVED = "arrived"
ENDED_RUN_ENDED = "run_ended"

# Why ORCA took the encounter back in plan_only.
RELEASE_PASSED = "passed"
RELEASE_ARRIVED = "arrived"
RELEASE_RUN_ENDED = "run_ended"

#: A back-up step has backed far enough within this much of its distance (m), as the simulator's
#: own back-up manoeuvre counts reaching its point (``simulation.BACK_UP_REACHED_M``).
BACKED_UP_EPS_M = 1e-3
_EPS = 1e-9

Vec = tuple[float, float]


def steps_from_dicts(steps: Sequence[Mapping[str, Any]], max_speed_mps: float, events: Sequence[str]) -> tuple[Step, ...]:
    """Steps in the reply format (``Step.as_dict``), read back with the reply parser's own checks.

    A recorded ``start.at_distance_m`` was checked against the distance when it was given; it is
    not checked again here.
    """
    context = ReplyContext(CONDITION_TALK, max_speed_mps, tuple(events), math.inf)
    flags: list[str] = []
    parsed = tuple(_step(index, dict(data), context, flags) for index, data in enumerate(steps))
    if flags:
        raise ValueError(f"recorded steps are not in the reply format: {flags}")
    return parsed


# --- one plan -------------------------------------------------------------------------------------


@dataclass
class StepRecord:
    """When one step of a plan ran, and why it ended."""

    index: int
    start_step: int
    start_time_s: float
    end_step: Optional[int] = None
    end_time_s: Optional[float] = None
    ended_by: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "start_step": self.start_step,
            "start_time_s": round(self.start_time_s, 6),
            "end_step": self.end_step,
            "end_time_s": None if self.end_time_s is None else round(self.end_time_s, 6),
            "ended_by": self.ended_by,
        }


@dataclass
class Plan:
    """One decision of one agent: its steps, and how far it has got through them."""

    agent_id: int
    partner_id: int
    decision_point: int
    given_step: int
    given_time_s: float
    steps: tuple[Step, ...]
    state: str = WAITING
    current: int = -1
    records: list[StepRecord] = field(default_factory=list)
    ended_step: Optional[int] = None
    ended_time_s: Optional[float] = None
    _origin: Vec = (0.0, 0.0)
    _tangent: Vec = (1.0, 0.0)
    _memory: dict[str, Any] = field(default_factory=dict)

    @property
    def step(self) -> Optional[Step]:
        return self.steps[self.current] if self.state == RUNNING else None

    @property
    def outcome(self) -> str:
        """What came of it, in the words of a view's history (``view.OUTCOMES``)."""
        if self.state == COMPLETED:
            return OUTCOME_COMPLETED
        return OUTCOME_REPLACED if self.state == REPLACED else OUTCOME_ONGOING

    def as_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "decision_point": self.decision_point,
            "given_step": self.given_step,
            "given_time_s": round(self.given_time_s, 6),
            "steps": [step.as_dict() for step in self.steps],
            "state": self.state,
            "outcome": self.outcome,
            "ended_step": self.ended_step,
            "ended_time_s": None if self.ended_time_s is None else round(self.ended_time_s, 6),
            "step_records": [record.as_dict() for record in self.records],
        }


# --- what the driver records of the encounter, step by step ---------------------------------------


@dataclass(frozen=True)
class BodyState:
    """One encounter agent after one step's move."""

    x: float
    y: float
    vx: float
    vy: float
    path_s: float
    done: bool

    @property
    def xy(self) -> Vec:
        return (self.x, self.y)

    @property
    def speed_mps(self) -> float:
        return math.hypot(self.vx, self.vy)


@dataclass(frozen=True)
class TrackRow:
    """The encounter's agents after the move of one step: at ``step`` and ``time_s``, the state the
    next step starts from."""

    step: int
    time_s: float
    bodies: Mapping[int, BodyState]


# --- the driver -----------------------------------------------------------------------------------


class PlanDriver:
    """Carries out the plans of one encounter's agents in one run.

    The simulation calls :meth:`prepare` once per step, before it chooses velocities; then
    :meth:`velocity` for every agent, :meth:`ignores` for every pair it would build a half-plane
    for, :meth:`backing` in its bookkeeping, and :meth:`after_step` after the move. A plan is
    given with :meth:`give` (now) or :meth:`schedule` (at a later step); either way it takes
    effect in the next :meth:`prepare`, so a live run and a replay of its log are the same run.
    """

    def __init__(self, mode: str, scenario: Scenario, agents: Sequence[int]):
        if mode not in MODES:
            raise ValueError(f"mode: one of {MODES}, got {mode!r}")
        agents = tuple(int(agent) for agent in agents)
        if len(agents) != 2 or agents[0] == agents[1]:
            raise ValueError(f"an encounter has two different agents (rounds 1 to 3, D11), got {agents}")
        self.mode, self.scenario, self.agents = mode, scenario, agents
        self.plans: dict[int, Plan] = {}
        self.decisions: list[Plan] = []
        self._pending: dict[int, list[tuple[int, tuple[Step, ...]]]] = {}
        self.started_step: Optional[int] = None
        self.started_time_s: Optional[float] = None
        self.released_step: Optional[int] = None
        self.released_time_s: Optional[float] = None
        self.release_reason: Optional[str] = None
        self._releases: dict[int, str] = {}
        self.released_on_request = False
        self.track: list[TrackRow] = []

    # --- giving plans -----------------------------------------------------------------------

    def partner_of(self, agent: int) -> int:
        if agent not in self.agents:
            raise ValueError(f"agent {agent} is not in the encounter {self.agents}")
        return self.agents[1] if agent == self.agents[0] else self.agents[0]

    def schedule(self, step: int, agent: int, steps: Sequence[Step]) -> None:
        """Give ``agent`` the plan ``steps`` at the start of simulation step ``step``."""
        self.partner_of(agent)
        if any(not isinstance(item, Step) for item in steps):
            raise TypeError("steps: parsed reply steps (negsim.resolution.reply.Step)")
        if self.released_step is not None:
            raise ValueError("the encounter has been released to ORCA; no plan can be given after it")
        self._pending.setdefault(int(step), []).append((agent, tuple(steps)))

    def give(self, simulation: Any, agent: int, steps: Sequence[Step]) -> None:
        """Give ``agent`` the plan ``steps`` now, before the simulation's next step."""
        self.schedule(simulation.world.step_index, agent, steps)

    def schedule_release(self, step: int, reason: str) -> None:
        """Hand the encounter back to ORCA at the start of simulation step ``step``."""
        if not reason:
            raise ValueError("a release has a reason")
        self._releases[int(step)] = reason

    def release(self, simulation: Any, reason: str) -> None:
        """Hand the encounter back to ORCA from the next step on (``plan_only``): what ORCA does
        after it is recorded separately (D6). Any plan still running is left to run."""
        self.schedule_release(simulation.world.step_index, reason)

    def release_record(self) -> Optional[dict[str, Any]]:
        """The release a session records for its replay: only one asked for (:meth:`release`);
        one that follows from the run (passed, arrived) the replay finds again by itself."""
        if not self.released_on_request:
            return None
        return {"step": self.released_step, "reason": self.release_reason}

    @property
    def active(self) -> bool:
        """Whether the encounter is under its plans: begun, and not yet handed back to ORCA."""
        return self.started_step is not None and self.released_step is None

    def decisions_record(self) -> list[dict[str, Any]]:
        """Every plan given, in order, in the form a replay schedules from."""
        return [
            {
                "agent_id": plan.agent_id,
                "decision_point": plan.decision_point,
                "step": plan.given_step,
                "time_s": round(plan.given_time_s, 6),
                "steps": [step.as_dict() for step in plan.steps],
            }
            for plan in self.decisions
        ]

    def outcomes(self, agent: int) -> list[str]:
        """What came of each of ``agent``'s decisions so far, in order (for a view's history)."""
        return [plan.outcome for plan in self.decisions if plan.agent_id == agent]

    # --- the simulation's calls -------------------------------------------------------------

    def prepare(self, simulation: Any) -> None:
        """At the start of a step: take up the plans due now, move every plan on, and end the
        encounter if it is over. Read from the state at the start of the step."""
        world = simulation.world
        step, now = world.step_index, world.time
        for agent, steps in self._pending.pop(step, []):
            self._take_up(agent, steps, step, now)
        for agent in self.agents:
            plan = self.plans.get(agent)
            if plan is not None and plan.state in (WAITING, RUNNING):
                self._move_on(simulation, plan)
        requested = self._releases.pop(step, None)
        if self.active:
            reason = requested or self._over(simulation)
            if reason is not None:
                self.released_step, self.released_time_s, self.release_reason = step, now, reason
                self.released_on_request = requested is not None

    def velocity(self, simulation: Any, agent: Any, own_speed: float, bound: Optional[float]) -> Optional[Vec]:
        """The preferred velocity a plan gives ``agent`` on this step, or ``None`` to leave it to
        the run. ``own_speed`` is the speed it would walk at (its directives applied, the
        arbiter's ``bound`` not)."""
        i = agent.agent_id
        if i not in self.agents or self.started_step is None:
            return None
        plan = self.plans.get(i)
        step = None if plan is None else plan.step
        if step is None:
            if self.mode == MODE_PLAN_ORCA or not self.active:
                return None
            # plan_only: carry on along the path, at its own speed, free of the arbiter.
            return simulation._preferred_velocity(agent, own_speed)
        velocity = self._step_velocity(simulation, agent, plan, step, own_speed)
        if self.mode == MODE_PLAN_ORCA and bound is not None:
            speed = math.hypot(*velocity)
            if speed > bound:
                scale = bound / speed if speed > 0.0 else 0.0
                velocity = (velocity[0] * scale, velocity[1] * scale)
        return velocity

    def ignores(self, i: int, j: int) -> bool:
        """Whether ORCA leaves out the half-plane of ``i`` toward ``j`` (``plan_only`` only)."""
        return self.mode == MODE_PLAN_ONLY and self.active and i in self.agents and j in self.agents

    def backing(self, i: int) -> bool:
        """Whether ``i`` is on a back-up step: intentional backing, never an artefact."""
        plan = self.plans.get(i)
        step = None if plan is None else plan.step
        return step is not None and step.back_up_m is not None

    def after_step(self, simulation: Any) -> None:
        world = simulation.world
        bodies = {}
        for agent_id in self.agents:
            agent = world.agents[agent_id]
            vx, vy = agent.velocity
            bodies[agent_id] = BodyState(agent.pose.x, agent.pose.y, vx, vy, agent.path_s, agent.goal_time is not None)
        self.track.append(TrackRow(world.step_index, world.time, bodies))

    def finish(self, simulation: Any) -> None:
        """At the end of the run (``AvoidanceSimulation.finish`` calls it): close the step of every
        plan still going, which stays ``ongoing``, and the encounter. Calling it again does nothing."""
        world = simulation.world
        for plan in self.plans.values():
            if plan.state in (WAITING, RUNNING) and plan.ended_step is None:
                self._end_step(plan, world.step_index, world.time, ENDED_RUN_ENDED)
                plan.ended_step, plan.ended_time_s = world.step_index, world.time
        if self.active:
            self.released_step, self.released_time_s, self.release_reason = world.step_index, world.time, RELEASE_RUN_ENDED

    # --- inside -----------------------------------------------------------------------------

    def _take_up(self, agent: int, steps: tuple[Step, ...], step: int, now: float) -> None:
        old = self.plans.get(agent)
        if old is not None and old.state in (WAITING, RUNNING):
            self._end_step(old, step, now, ENDED_REPLACED)
            old.state, old.ended_step, old.ended_time_s = REPLACED, step, now
        number = 1 + sum(1 for plan in self.decisions if plan.agent_id == agent)
        plan = Plan(agent, self.partner_of(agent), number, step, now, steps)
        if not steps:
            plan.state, plan.ended_step, plan.ended_time_s = COMPLETED, step, now
        self.plans[agent] = plan
        self.decisions.append(plan)
        if self.started_step is None:
            self.started_step, self.started_time_s = step, now

    def _move_on(self, simulation: Any, plan: Plan) -> None:
        world = simulation.world
        step, now = world.step_index, world.time
        agent = world.agents[plan.agent_id]
        if agent.goal_time is not None:
            self._end_step(plan, step, now, ENDED_ARRIVED)
            plan.state, plan.ended_step, plan.ended_time_s = COMPLETED, step, now
            return
        if plan.state == WAITING:
            if not self._may_start(simulation, plan):
                return
            self._begin(simulation, plan, 0)
        while plan.state == RUNNING:
            ended_by = self._ended(simulation, plan)
            if ended_by is None:
                return
            self._end_step(plan, step, now, ended_by)
            if plan.current + 1 < len(plan.steps):
                self._begin(simulation, plan, plan.current + 1)
            else:
                plan.state, plan.ended_step, plan.ended_time_s = COMPLETED, step, now

    def _may_start(self, simulation: Any, plan: Plan) -> bool:
        start = plan.steps[0].start
        if start is None or start.kind == START_NOW:
            return True
        world = simulation.world
        if start.kind == START_AFTER_SECONDS:
            return world.time - plan.given_time_s >= start.value - _EPS
        if start.kind == START_AT_DISTANCE:
            me, other = world.agents[plan.agent_id], world.agents[plan.partner_id]
            return other.goal_time is not None or math.dist(me.pose.xy, other.pose.xy) <= start.value + _EPS
        raise ValueError(f"unknown start {start.kind!r}")

    def _begin(self, simulation: Any, plan: Plan, index: int) -> None:
        world = simulation.world
        agent = world.agents[plan.agent_id]
        heading = agent.spec.path.heading_at(agent.path_s)
        plan.state, plan.current = RUNNING, index
        plan._origin, plan._tangent, plan._memory = agent.pose.xy, (math.cos(heading), math.sin(heading)), {}
        plan.records.append(StepRecord(index, world.step_index, world.time))

    @staticmethod
    def _end_step(plan: Plan, step: int, now: float, reason: str) -> None:
        if plan.state == RUNNING and plan.records and plan.records[-1].ended_by is None:
            record = plan.records[-1]
            record.end_step, record.end_time_s, record.ended_by = step, now, reason

    def _backed(self, simulation: Any, plan: Plan) -> float:
        agent = simulation.world.agents[plan.agent_id]
        dx, dy = agent.pose.x - plan._origin[0], agent.pose.y - plan._origin[1]
        return -(dx * plan._tangent[0] + dy * plan._tangent[1])

    def _ended(self, simulation: Any, plan: Plan) -> Optional[str]:
        step = plan.steps[plan.current]
        if step.back_up_m is not None and self._backed(simulation, plan) >= step.back_up_m - BACKED_UP_EPS_M:
            return ENDED_BACKED_UP
        until = step.until
        if until is None:
            return None
        if until.seconds is not None:
            started = plan.records[-1].start_time_s
            return ENDED_SECONDS if simulation.world.time - started >= until.seconds - _EPS else None
        context = EventContext(simulation, plan.agent_id, plan.partner_id, plan.records[-1].start_time_s, plan._memory)
        return until.event if self.scenario.happened(until.event, context) else None

    def _step_velocity(self, simulation: Any, agent: Any, plan: Plan, step: Step, own_speed: float) -> Vec:
        if step.back_up_m is not None:
            remaining = max(0.0, step.back_up_m - self._backed(simulation, plan))
            speed = min(agent.spec.backing_speed_mps, remaining / simulation.world.dt)
            return (-speed * plan._tangent[0], -speed * plan._tangent[1])
        speed = own_speed if step.speed_mps is None else min(step.speed_mps, agent.spec.max_speed)
        if speed <= 0.0:
            return (0.0, 0.0)
        ux, uy = simulation._preferred_velocity(agent, 1.0)
        if step.turn is not None:
            angle = math.radians(step.turn.degrees) * (1.0 if step.turn.to == "left" else -1.0)
            ux, uy = ux * math.cos(angle) - uy * math.sin(angle), ux * math.sin(angle) + uy * math.cos(angle)
        return (speed * ux, speed * uy)

    def _over(self, simulation: Any) -> Optional[str]:
        agents = simulation.world.agents
        if any(agents[agent].goal_time is not None for agent in self.agents):
            return RELEASE_ARRIVED
        if any(plan.state in (WAITING, RUNNING) for plan in self.plans.values()):
            return None
        i, j = self.agents
        return RELEASE_PASSED if simulation._passed(i, j, simulation.spec.single_file_safety_margin) else None

    def as_dict(self) -> dict[str, Any]:
        """What the driver did, for a run's ``outcome.json``."""
        return {
            "mode": self.mode,
            "agents": list(self.agents),
            "started_step": self.started_step,
            "started_time_s": None if self.started_time_s is None else round(self.started_time_s, 6),
            "released_step": self.released_step,
            "released_time_s": None if self.released_time_s is None else round(self.released_time_s, 6),
            "release_reason": self.release_reason,
            "decisions": [plan.as_dict() for plan in self.decisions],
        }


# --- the interface for RF-3 -----------------------------------------------------------------------


@dataclass(frozen=True)
class WorldState:
    """Where a :class:`PlanRun` stands at the end of :func:`advance`."""

    step: int
    time_s: float
    status: Optional[str]  # None while the run goes on; otherwise how it ended
    plans: Mapping[int, Mapping[str, Any]]  # per encounter agent: its current plan's state
    outcomes: Mapping[int, tuple[str, ...]]  # per encounter agent: what came of each decision (view.OUTCOMES)
    encounter_active: bool

    @property
    def finished(self) -> bool:
        return self.status is not None


class PlanRun:
    """A simulation with a plan driver attached: one encounter's live run, or its replay."""

    def __init__(self, simulation: Any, mode: str, scenario: Scenario, agents: Sequence[int]):
        if simulation.plans is not None:
            raise ValueError("the simulation already has a plan driver")
        self.simulation = simulation
        self.driver = PlanDriver(mode, scenario, agents)
        simulation.plans = self.driver
        self.result: Any = None

    @property
    def finished(self) -> bool:
        sim = self.simulation
        return sim.status is not None or sim.world.step_index >= sim.spec.max_steps

    def state(self) -> WorldState:
        sim, driver = self.simulation, self.driver
        plans = {}
        for agent in driver.agents:
            plan = driver.plans.get(agent)
            plans[agent] = {} if plan is None else {
                "decision_point": plan.decision_point, "state": plan.state, "step_index": plan.current,
            }
        status = sim.status if sim.status is not None else ("timeout" if self.finished else None)
        return WorldState(
            sim.world.step_index, sim.world.time, status, plans,
            {agent: tuple(driver.outcomes(agent)) for agent in driver.agents}, driver.active,
        )

    def advance(
        self,
        plans: Mapping[int, Sequence[Step]],
        until_time_s: float,
        stop_when: Optional[Callable[["PlanRun"], bool]] = None,
    ) -> WorldState:
        """Give each agent in ``plans`` its plan now, then run until ``until_time_s``, the end of
        the run, or (checked after every step) ``stop_when``. Returns the state there."""
        if self.result is not None:
            raise ValueError("the run has been finished")
        for agent, steps in sorted(plans.items()):
            self.driver.give(self.simulation, agent, steps)
        sim = self.simulation
        while not self.finished and sim.world.time < until_time_s - _EPS:
            sim.step()
            if stop_when is not None and stop_when(self):
                break
        return self.state()

    def release(self, reason: str) -> None:
        self.driver.release(self.simulation, reason)

    def finish(self) -> Any:
        """Close the run and return its ``SimulationResult``."""
        if self.result is None:
            self.result = self.simulation.finish()
        return self.result


def advance(run: PlanRun, plans: Mapping[int, Sequence[Step]], until_time_s: float, **kwargs: Any) -> WorldState:
    """Run ``run`` from one decision point to the next (RF-3's interface): see :meth:`PlanRun.advance`."""
    return run.advance(plans, until_time_s, **kwargs)
