"""``RuleDatabaseProvider``: directives from stored rules, behind the directive-provider interface.

It answers the interface's one question, ``directive(record)``, as one agent applying the
rules on its own would: it builds the snapshot that agent can build from its own record
and returns the directive of that agent's role. Because a rule reads only what both
agents compute identically, the answer is the same as the one the shared snapshot gives,
and the run counts every case in which it is not (``formation_mismatches``; it should
stay 0).

In a run it also follows the pairs (``follows_pairs``), which is where the matching policy
lives: the run loop calls :meth:`update` on every step and :meth:`close_pair` when a pair
interaction ends, and the :class:`RuleMatcher` keeps each pair's state and record
(``matching.py``, ``docs/rule-matching.md``). No other part of the avoidance layer knows
that the directives come from rules.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from ..avoidance.directives import PLAIN_ORCA, AvoidanceDirective, DirectiveProvider
from ..avoidance.perception import PerceptionRecord
from .database import ActiveRuleSet
from .matching import DEFAULT_HYSTERESIS_STEPS, RuleMatcher, evaluate
from .snapshot import snapshot_of_record


class RuleDatabaseProvider(DirectiveProvider):
    name = "rules"
    follows_pairs = True

    def __init__(
        self,
        active: ActiveRuleSet,
        visibility: Mapping[str, bool],
        hysteresis_steps: int = DEFAULT_HYSTERESIS_STEPS,
        database: str = "rule_db",
    ):
        active.check_visibility(visibility)
        self.active = active
        self.visibility = dict(visibility)
        self.database = database
        self.matcher = RuleMatcher(active, hysteresis_steps)

    def directive(self, record: PerceptionRecord) -> AvoidanceDirective:
        """What the observer concludes from its own record alone: its role's directive, or
        plain ORCA if no rule matches."""
        evaluation = evaluate(self.active, snapshot_of_record(record, self.visibility))
        return PLAIN_ORCA if evaluation.match is None else evaluation.match.directive_of(record.observer_id)

    def update(self, view: Any) -> Mapping[tuple[int, int], AvoidanceDirective]:
        return self.matcher.step(view)

    def close_pair(self, pair: Any, step: int, time_s: float, reason: str) -> None:
        self.matcher.close(pair, step, time_s, reason)

    def describe(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "database": self.database,
            "ruleset": self.active.name,
            "rules": self.active.describe(),
            "hysteresis_steps": self.matcher.hysteresis_steps,
            "unchecked_pairs": [clash.describe() for clash in self.active.unchecked],
        }

    def summary(self) -> Optional[dict[str, Any]]:
        matcher = self.matcher
        return {
            "evaluations": {outcome: matcher.counts[outcome] for outcome in sorted(matcher.counts)},
            "matches_begun": {key: matcher.fired[key] for key in sorted(matcher.fired)},
            "match_ends": {reason: matcher.match_ends[reason] for reason in sorted(matcher.match_ends)},
            "cross_pair_conflicts": len(matcher.conflict_events),
            "formation_checks": matcher.formation_checks,
            "formation_mismatches": matcher.formation_mismatches,
        }
