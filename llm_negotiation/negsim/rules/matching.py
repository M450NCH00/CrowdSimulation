"""The matching policy: which rule a pair follows, from step to step (``docs/rule-matching.md``).

For every pair of agents that has an interaction open (at least one perceives the other),
on every step:

* **One shared snapshot.** The rules are evaluated once for the pair, on one snapshot
  (``snapshot.py``), and each agent gets the directive of its role.
* **When rules are evaluated.** When the pair forms; then on every step while no rule
  holds; and when its encounter class changes while one does. A rule whose threshold on,
  say, the time to collision is met only later can therefore still fire.
* **Several matches.** The highest priority wins. Two rules at that priority with
  different directives: ``ambiguous_match``, logged, and the one with the lower
  ``rule_id`` is applied. (Rule sets in which that can happen are refused before the run,
  where the grid of ``ambiguity.py`` finds it.)
* **No match.** Plain ORCA, the baseline, logged as ``no_rule_matched``.
* **One rule per pair.** The winning rule supplies the whole directive of the pair;
  fields it leaves out take their baseline values. Fields are never merged across rules.
* **Holding a match.** A rule that has matched holds until it expires, whatever its
  condition does meanwhile, unless a rule of strictly higher priority matches at a
  re-evaluation, which replaces it.
* **Hysteresis.** A change of encounter class counts only once the new class has been seen
  on ``hysteresis_steps`` steps in a row, so a class that flickers at a boundary triggers
  nothing. A held match ignores its condition. And a pair whose match has expired is not
  evaluated again until its (steady) class has changed: two agents that have just passed
  each other do not pick the rule up again while still in range.
* **Expiry.** A match whose rule says ``expiry: passed`` (the default) ends on the first
  step on which the encounter has passed: the two are separating (``p · v > 0``) and
  clear of each other by more than the pair's clearance margin
  (``docs/derivations.md``, section 15). With ``expiry: out_of_range`` it ends when the
  pair interaction does. Either way it ends if the pair interaction ends first.
* **Several neighbours.** Rules are matched per pair. Where the matches of one agent's
  pairs contradict each other in a field that is the agent's own (its speed) or that
  states an order (its side, its place in a queue), ``cross_pair_conflict`` is logged
  and the documented resolution applies (:data:`CONFLICT_RESOLUTIONS`).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping, Optional, Protocol, Sequence

from ..avoidance.directives import PLAIN_ORCA, SIDE_NONE, AvoidanceDirective, ORDER_NONE
from ..avoidance.perception import PairFeatures
from ..core.agent import AgentRuntime
from .ambiguity import different
from .database import ActiveRuleSet
from .model import EXPIRY_PASSED, Match, Rule
from .snapshot import PairSnapshot, snapshot_of_pair

if TYPE_CHECKING:  # pragma: no cover
    from ..avoidance.simulation import PairInteraction

UNMATCHED, HELD, SPENT = "unmatched", "held", "spent"

# The outcome of one evaluation.
RULE_MATCHED = "rule_matched"
NO_RULE_MATCHED = "no_rule_matched"
AMBIGUOUS_MATCH = "ambiguous_match"
KEPT = "kept"  # a held rule stays: nothing of strictly higher priority matched
OUTCOMES = (RULE_MATCHED, NO_RULE_MATCHED, AMBIGUOUS_MATCH, KEPT)

# Why a match ended.
END_PASSED = "passed"
END_REPLACED = "replaced"
MATCH_END_REASONS = (END_PASSED, END_REPLACED, "out_of_range", "agent_arrived", "run_ended")

#: How each kind of cross-pair conflict is settled (``docs/rule-matching.md``).
CONFLICT_RESOLUTIONS = {
    "side_preference": (
        "none needed: a side preference acts only on the half-plane of its own pair, so each pair keeps its own side"
    ),
    "speed_scale": "the smallest speed_scale applies, as with any several directives (DD40)",
    "passage_order": (
        "each pair's order goes to the arbiter separately; ordering three or more agents is out of scope "
        "(architecture.md, section 4)"
    ),
}

DEFAULT_HYSTERESIS_STEPS = 3


class StepView(Protocol):
    """What the run loop shows the matcher on one step (``AvoidanceSimulation`` provides it)."""

    step: int
    time_s: float
    visibility: Mapping[str, bool]
    attributes: Mapping[int, Mapping[str, Any]]
    pairs: Sequence["PairInteraction"]

    def agent(self, agent_id: int) -> AgentRuntime: ...
    def directions(self, pair: "PairInteraction") -> list[tuple[int, int]]: ...
    def current_directive(self, observer: int, neighbour: int) -> AvoidanceDirective: ...
    def encounter_class(self, i: int, j: int) -> Optional[str]: ...
    def features(self, i: int, j: int) -> PairFeatures: ...
    def passed(self, i: int, j: int, clearance: float) -> bool: ...


@dataclass(frozen=True)
class Evaluation:
    outcome: str
    match: Optional[Match]
    ambiguous_with: tuple[Rule, ...] = ()
    candidates: int = 0


def evaluate(active: ActiveRuleSet, snapshot: PairSnapshot, above: Optional[int] = None) -> Evaluation:
    """Try the rules for the snapshot's class, highest priority first.

    Only rules of priority strictly above ``above`` are tried, if it is given. The first
    priority at which anything matches decides; several different matches there are
    ambiguous, and the lowest ``rule_id`` among them is applied.
    """
    candidates = [rule for rule in active.candidates(snapshot.encounter_class) if above is None or rule.priority > above]
    top: list[Match] = []
    for rule in candidates:
        if top and rule.priority < top[0].rule.priority:
            break
        found = rule.match(snapshot)
        if found is not None:
            top.append(found)
    if not top:
        return Evaluation(NO_RULE_MATCHED, None, (), len(candidates))
    first = top[0]
    others = tuple(item.rule for item in top[1:] if different(item, first))
    if others:
        return Evaluation(AMBIGUOUS_MATCH, first, others, len(candidates))
    return Evaluation(RULE_MATCHED, first, (), len(candidates))


@dataclass
class PairRules:
    """What the matcher knows and has recorded about one pair interaction.

    It is kept on the run loop's ``PairInteraction`` and written out with it
    (``pair_interactions.jsonl``, ``docs/log-schema.md``).
    """

    agents: tuple[int, int]
    class_used: Optional[str]
    state: str = UNMATCHED
    candidate: Optional[str] = None
    candidate_count: int = 0
    held: Optional[Match] = None
    held_entry: Optional[dict[str, Any]] = None
    evaluations: list[dict[str, Any]] = field(default_factory=list)
    matches: list[dict[str, Any]] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    independent_agrees: Optional[bool] = None

    def debounce(self, raw: Optional[str], steps: int) -> bool:
        """Feed this step's class; True if the steady class changed on this step."""
        if raw == self.class_used:
            self.candidate, self.candidate_count = None, 0
            return False
        if raw == self.candidate:
            self.candidate_count += 1
        else:
            self.candidate, self.candidate_count = raw, 1
        if self.candidate_count >= steps:
            self.class_used, self.candidate, self.candidate_count = raw, None, 0
            return True
        return False

    def log(self, step: int, time_s: float, evaluation: Evaluation, snapshot: Optional[PairSnapshot], encounter: Optional[str]) -> None:
        """Record one evaluation. Consecutive evaluations with the same result share an entry."""
        rule = None if evaluation.match is None else evaluation.match.rule.key
        others = [item.key for item in evaluation.ambiguous_with]
        last = self.evaluations[-1] if self.evaluations else None
        if (
            last is not None
            and last["to_step"] == step - 1
            and (last["outcome"], last["rule"], last["encounter_class"], last["ambiguous_with"])
            == (evaluation.outcome, rule, encounter, others)
        ):
            last["to_step"], last["count"] = step, last["count"] + 1
            return
        self.evaluations.append(
            {
                "from_step": step,
                "from_time_s": round(time_s, 6),
                "to_step": step,
                "count": 1,
                "encounter_class": encounter,
                "outcome": evaluation.outcome,
                "rule": rule,
                "ambiguous_with": others,
                "candidates": evaluation.candidates,
                "snapshot": None if snapshot is None else snapshot.as_dict(),
            }
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "state_at_end": self.state,
            "independent_agrees": self.independent_agrees,
            "evaluations": list(self.evaluations),
            "matches": list(self.matches),
            "cross_pair_conflicts": list(self.conflicts),
        }


class RuleMatcher:
    """Runs the matching policy over every open pair, step by step."""

    def __init__(self, active: ActiveRuleSet, hysteresis_steps: int = DEFAULT_HYSTERESIS_STEPS):
        if hysteresis_steps < 1:
            raise ValueError(f"hysteresis_steps must be at least 1, got {hysteresis_steps}")
        self.active = active
        self.hysteresis_steps = hysteresis_steps
        self.counts: Counter[str] = Counter()  # evaluation outcomes, counted per evaluation
        self.fired: Counter[str] = Counter()  # matches begun, by rule key
        self.match_ends: Counter[str] = Counter()
        self.conflict_events: list[dict[str, Any]] = []
        self.formation_checks = 0
        self.formation_mismatches = 0
        self._open_conflicts: dict[tuple[int, str], frozenset] = {}

    # --- one step -------------------------------------------------------------------------------

    def step(self, view: StepView) -> dict[tuple[int, int], AvoidanceDirective]:
        """Update every open pair; return the directives that change, by (observer, neighbour)."""
        changes: dict[tuple[int, int], AvoidanceDirective] = {}
        for pair in view.pairs:
            i, j = pair.agents
            raw = view.encounter_class(i, j)
            state: Optional[PairRules] = pair.provider_record
            formed = state is None
            if formed:
                state = pair.provider_record = PairRules(pair.agents, raw)
                changed = False
            else:
                changed = state.debounce(raw, self.hysteresis_steps)

            if state.state == HELD and state.held.rule.expiry == EXPIRY_PASSED:
                clearance = max(directive.clearance_margin for directive in state.held.directives)
                if view.passed(i, j, clearance):
                    self._end(state, view.step, view.time_s, END_PASSED)
                    state.state = SPENT
            if state.state == SPENT and changed:
                state.state = UNMATCHED

            if state.state == UNMATCHED:
                self._evaluate(state, view, i, j, raw, above=None)
            elif state.state == HELD and changed:
                self._evaluate(state, view, i, j, raw, above=state.held.rule.priority)

            for observer, neighbour in view.directions(pair):
                wanted = state.held.directive_of(observer) if state.state == HELD else PLAIN_ORCA
                current = view.current_directive(observer, neighbour)
                if formed:
                    self.formation_checks += 1
                    agrees = current == wanted
                    self.formation_mismatches += not agrees
                    state.independent_agrees = agrees if state.independent_agrees is None else state.independent_agrees and agrees
                if current != wanted:
                    changes[(observer, neighbour)] = wanted
        self._cross_pair_conflicts(view)
        return changes

    def close(self, pair: "PairInteraction", step: int, time_s: float, reason: str) -> None:
        """A pair interaction has ended: end its match, if it has one, for the same reason."""
        state: Optional[PairRules] = pair.provider_record
        if state is not None and state.state == HELD:
            self._end(state, step, time_s, reason)
            state.state = SPENT

    # --- internals ------------------------------------------------------------------------------

    def _evaluate(self, state: PairRules, view: StepView, i: int, j: int, raw: Optional[str], above: Optional[int]) -> None:
        snapshot = None
        if any(above is None or rule.priority > above for rule in self.active.candidates(raw)):
            a, b = view.agent(i), view.agent(j)
            snapshot = snapshot_of_pair(view.step, view.time_s, a, b, view.features(i, j), view.visibility, view.attributes)
            evaluation = evaluate(self.active, snapshot, above)
        else:
            evaluation = Evaluation(NO_RULE_MATCHED, None, (), 0)
        if above is not None and evaluation.match is None:
            evaluation = Evaluation(KEPT, None, (), evaluation.candidates)
        self.counts[evaluation.outcome] += 1
        state.log(view.step, view.time_s, evaluation, snapshot, raw)
        if evaluation.match is None:
            return
        if state.state == HELD:
            self._end(state, view.step, view.time_s, END_REPLACED, replaced_by=evaluation.match.rule.key)
        match = evaluation.match
        state.held, state.state = match, HELD
        self.fired[match.rule.key] += 1
        state.held_entry = {
            "rule_id": match.rule.rule_id,
            "version": match.rule.version,
            "priority": match.rule.priority,
            "encounter": match.rule.encounter,
            "expiry": match.rule.expiry,
            "outcome": evaluation.outcome,
            "ambiguous_with": [rule.key for rule in evaluation.ambiguous_with],
            "from_step": view.step,
            "from_time_s": round(view.time_s, 6),
            "roles": {str(agent): role for agent, role in zip(match.agents, match.roles)},
            "directives": {str(agent): directive.as_dict() for agent, directive in zip(match.agents, match.directives)},
            "snapshot": snapshot.as_dict(),
            "to_step": None,
            "to_time_s": None,
            "end_reason": None,
            "replaced_by": None,
        }
        state.matches.append(state.held_entry)

    def _end(self, state: PairRules, step: int, time_s: float, reason: str, replaced_by: Optional[str] = None) -> None:
        entry = state.held_entry
        entry["to_step"], entry["to_time_s"], entry["end_reason"] = step, round(time_s, 6), reason
        entry["replaced_by"] = replaced_by
        self.match_ends[reason] += 1
        state.held, state.held_entry = None, None

    def _cross_pair_conflicts(self, view: StepView) -> None:
        """Log each contradiction between the matches of one agent's pairs when it appears."""
        held: dict[int, list[tuple[PairInteraction, Match]]] = {}
        for pair in view.pairs:
            state: PairRules = pair.provider_record
            if state.state == HELD:
                for agent in pair.agents:
                    held.setdefault(agent, []).append((pair, state.held))
        current: dict[tuple[int, str], frozenset] = {}
        for agent, items in held.items():
            if len(items) < 2:
                continue
            for name, values in self._contradictions(agent, items).items():
                current[(agent, name)] = frozenset(values)
                if self._open_conflicts.get((agent, name)) == current[(agent, name)]:
                    continue
                event = {
                    "step": view.step,
                    "time_s": round(view.time_s, 6),
                    "agent_id": agent,
                    "field": name,
                    "values": [{"pair": list(pair_agents), "rule": key, "value": value} for pair_agents, key, value in sorted(values)],
                    "resolution": CONFLICT_RESOLUTIONS[name],
                }
                self.conflict_events.append(event)
                for pair, _ in items:
                    pair.provider_record.conflicts.append(event)
        self._open_conflicts = current

    @staticmethod
    def _contradictions(agent: int, items) -> dict[str, set]:
        found: dict[str, set] = {}
        for name, bad in (
            ("side_preference", lambda values: len(values - {SIDE_NONE}) > 1),  # both left and right
            ("speed_scale", lambda values: len(values) > 1),  # two different speeds asked for
            ("passage_order", lambda values: len(values - {ORDER_NONE}) > 1),  # leader in one, follower in another
        ):
            entries = set()
            for pair, match in items:
                role = match.role_of(agent)
                if name in match.rule.set_fields[role]:
                    entries.add((pair.agents, match.rule.key, getattr(match.directive_of(agent), name)))
            if bad({value for _, _, value in entries}):
                found[name] = entries
        return found
