"""Carrying out a rule's steps in a crowd (issue #108, RF-31; ``docs/rule-format.md``, section 15).

A version 4 rule may give a role a plan, ``steps``, in Step 1's own vocabulary
(``negsim.resolution.reply``). When a pair's match begins, each of its two people whose role has
steps gets them as a plan, once for that encounter. :class:`RuleStepDriver` carries the plans out
with the plan executor's own mechanics (``negsim.resolution.execute.PlanDriver``: each step's
start, speed, turn, sidestep, back-up and until), as ``plan_orca`` runs them under the ``keep_line``
execution: the plan sets the person's preferred velocity, and **ORCA still avoids everyone
underneath**, the partner included. So a rule's plan can shape how someone gives way, but never
walks them into anyone.

What differs from one Step 1 encounter is that a crowd has many encounters at once:

- **Anyone can have a plan**, each with its own partner (the person the rule matched them with):
  a ``start`` or an ``until`` at a distance is read against the partner, and ``other_passes`` is
  the partner going by (the passing scenario's event, ``negsim.resolution.scenarios.passing``).
- **One plan per person at a time.** A match that would give a person a plan while their earlier
  plan is still in force is skipped and counted (``skipped_busy``), as a back-up manoeuvre
  already is (``docs/rule-matching.md``, section 7): the first plan to start runs to its end.
- **After the last step**, the person keeps the line the plan took them to, walking parallel to
  their path, until they and the partner have passed each other, the partner has arrived, or the
  pair's match was replaced; then they are plain ORCA again (steering back towards their path).
- Before a delayed first step the person walks as plain ORCA would.

Nothing here runs unless an enabled rule has steps: the rule provider builds the driver only then
(``RuleDatabaseProvider.step_driver``), and the simulation attaches it only if there is one, so
every run without such a rule is exactly as before.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any, Optional, Sequence

from ..resolution.execute import (
    COMPLETED,
    ENDED_RUN_ENDED,
    EXECUTION_KEEP_LINE,
    MODE_PLAN_ORCA,
    REPLACED,
    RUNNING,
    WAITING,
    BodyState,
    Plan,
    PlanDriver,
    TrackRow,
)

#: Why a person's plan stopped being in force (after its steps were done or cut short).
OVER_PASSED = "passed"
OVER_PARTNER_ARRIVED = "partner_arrived"
OVER_ARRIVED = "arrived"


class RuleStepDriver(PlanDriver):
    """The plans that rules gave people in one avoidance run (module docstring).

    The simulation calls it as it calls any plan driver (``prepare``, ``velocity``, ``ignores``,
    ``backing``, ``after_step``, ``finish``). The rule matcher calls :meth:`start` when a match
    gives someone steps. ``track_agents``, if given, are recorded after every step, as a Step 1
    driver records its encounter (the identity check measures them).
    """

    def __init__(self, scenario: Any = None, track_agents: Sequence[int] = ()):
        # PlanDriver.__init__ is for one encounter of known agents; a crowd has none fixed.
        if scenario is None:
            from ..resolution.scenarios.passing import PassingScenario

            scenario = PassingScenario.load()
        self.mode, self.scenario, self.execution = MODE_PLAN_ORCA, scenario, EXECUTION_KEEP_LINE
        self._as_prompted = True
        self.agents: tuple[int, ...] = tuple(int(agent) for agent in track_agents)
        self.plans: dict[int, Plan] = {}
        self.decisions: list[Plan] = []
        self._pending: dict[int, list[tuple[int, tuple[Any, ...], int]]] = {}
        self.started_step: Optional[int] = None
        self.started_time_s: Optional[float] = None
        self.released_step = self.released_time_s = self.release_reason = None
        self._releases: dict[int, str] = {}
        self.released_on_request = False
        self.track: list[TrackRow] = []
        self.counts: Counter[str] = Counter()
        self.over: Counter[str] = Counter()
        self._rules: dict[int, str] = {}  # agent -> the rule key of its plan in force
        self.decision_rules: list[str] = []  # the rule key of each plan in decisions, in order

    # --- the matcher's call ---------------------------------------------------------------------

    def start(self, step: int, agent: int, partner: int, steps: Sequence[Any], rule_key: str) -> bool:
        """Give ``agent`` the plan ``steps`` against ``partner`` from simulation step ``step`` on;
        ``False`` (and counted) if the person already has a plan in force."""
        agent, partner = int(agent), int(partner)
        if agent in self.plans or any(entry[0] == agent for entry in self._pending.get(step, ())):
            self.counts["skipped_busy"] += 1
            return False
        self._pending.setdefault(int(step), []).append((agent, tuple(steps), partner))
        self._rules[agent] = rule_key
        self.counts["started"] += 1
        return True

    # --- the simulation's calls -----------------------------------------------------------------

    def prepare(self, simulation: Any) -> None:
        world = simulation.world
        step, now = world.step_index, world.time
        for agent, steps, partner in self._pending.pop(step, []):
            self._take_up(agent, steps, partner, step, now, simulation)
        for agent in sorted(self.plans):
            plan = self.plans[agent]
            if plan.state in (WAITING, RUNNING):
                self._move_on(simulation, plan)
            if plan.state not in (WAITING, RUNNING):
                reason = self._finished(simulation, plan)
                if reason is not None:
                    self.over[reason] += 1
                    del self.plans[agent]
                    self._rules.pop(agent, None)

    def velocity(self, simulation: Any, agent: Any, own_speed: float, bound: Optional[float]) -> Optional[tuple[float, float]]:
        plan = self.plans.get(agent.agent_id)
        if plan is None:
            return None
        step = plan.step
        if step is not None:
            velocity = self._step_velocity(simulation, agent, plan, step, own_speed)
        elif plan.records:
            # After the steps (or between them), keep the line the plan took the person to.
            heading = agent.spec.path.heading_at(agent.path_s)
            velocity = (own_speed * math.cos(heading), own_speed * math.sin(heading))
        else:
            return None  # a delayed first step not begun: plain ORCA meanwhile
        if bound is not None:
            speed = math.hypot(*velocity)
            if speed > bound:
                scale = bound / speed if speed > 0.0 else 0.0
                velocity = (velocity[0] * scale, velocity[1] * scale)
        return velocity

    def ignores(self, i: int, j: int) -> bool:
        return False  # ORCA avoids everyone, as in plan_orca

    def after_step(self, simulation: Any) -> None:
        if not self.agents:
            return
        world = simulation.world
        bodies = {}
        for agent_id in self.agents:
            agent = world.agents[agent_id]
            vx, vy = agent.velocity
            bodies[agent_id] = BodyState(agent.pose.x, agent.pose.y, vx, vy, agent.path_s, agent.goal_time is not None)
        self.track.append(TrackRow(world.step_index, world.time, bodies))

    def finish(self, simulation: Any) -> None:
        world = simulation.world
        for plan in self.plans.values():
            if plan.state in (WAITING, RUNNING) and plan.ended_step is None:
                self._end_step(plan, world.step_index, world.time, ENDED_RUN_ENDED, simulation)
                plan.ended_step, plan.ended_time_s = world.step_index, world.time

    # --- inside -----------------------------------------------------------------------------------

    def _take_up(self, agent: int, steps: tuple[Any, ...], partner: int, step: int, now: float, simulation: Any = None) -> None:
        number = 1 + sum(1 for plan in self.decisions if plan.agent_id == agent)
        plan = Plan(agent, partner, number, step, now, steps)
        self.plans[agent] = plan
        self.decisions.append(plan)
        self.decision_rules.append(self._rules.get(agent, ""))
        if self.started_step is None:
            self.started_step, self.started_time_s = step, now

    def _finished(self, simulation: Any, plan: Plan) -> Optional[str]:
        """Why a plan whose steps are over is no longer in force, or ``None`` while the person
        still keeps their line."""
        agents = simulation.world.agents
        if plan.state == REPLACED:
            return OVER_PASSED
        if agents[plan.agent_id].goal_time is not None:
            return OVER_ARRIVED
        if agents[plan.partner_id].goal_time is not None:
            return OVER_PARTNER_ARRIVED
        if simulation._passed(plan.agent_id, plan.partner_id, simulation.spec.single_file_safety_margin):
            return OVER_PASSED
        return None

    def summary(self) -> dict[str, Any]:
        """What a run's outcome records of the plans rules gave."""
        ended: Counter[str] = Counter()
        for plan in self.decisions:
            for record in plan.records:
                ended[record.ended_by or "running"] += 1
        return {
            "plans_started": self.counts["started"],
            "plans_skipped_busy": self.counts["skipped_busy"],
            "plans_taken_up": len(self.decisions),
            "plans_by_rule": dict(sorted(Counter(self.decision_rules).items())),
            "plans_completed": sum(1 for plan in self.decisions if plan.state == COMPLETED),
            "steps_ended_by": dict(sorted(ended.items())),
            "plans_over": dict(sorted(self.over.items())),
        }


class Drivers:
    """Two plan drivers in one simulation's single slot: a run's own (a Step 1 watcher, say) and a
    rule's steps. The first that gives a velocity sets it; either may leave a half-plane out, or
    count a step as backing; every driver is told of every step."""

    def __init__(self, *drivers: Any):
        self.drivers = tuple(driver for driver in drivers if driver is not None)

    def prepare(self, simulation: Any) -> None:
        for driver in self.drivers:
            driver.prepare(simulation)

    def velocity(self, simulation: Any, agent: Any, own_speed: float, bound: Optional[float]) -> Optional[tuple[float, float]]:
        for driver in self.drivers:
            velocity = driver.velocity(simulation, agent, own_speed, bound)
            if velocity is not None:
                return velocity
        return None

    def ignores(self, i: int, j: int) -> bool:
        return any(driver.ignores(i, j) for driver in self.drivers)

    def backing(self, i: int) -> bool:
        return any(driver.backing(i) for driver in self.drivers)

    def after_step(self, simulation: Any) -> None:
        for driver in self.drivers:
            driver.after_step(simulation)

    def finish(self, simulation: Any) -> None:
        for driver in self.drivers:
            driver.finish(simulation)
