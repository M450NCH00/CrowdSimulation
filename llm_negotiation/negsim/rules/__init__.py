"""Rules: a declarative format, a database of rule versions, and a provider that follows them.

Issue #28 (SI-2). A rule maps a condition on what two agents can both perceive to a
directive per role. ``docs/rule-format.md`` describes the format, ``docs/rule-matching.md``
the matching policy. The pieces:

``fields``      what a rule may read, in what unit, needing what to be visible
``conditions``  comparisons and ``all``/``any`` groups; data, never code
``model``       a rule: parsing, roles, the load-time consistency checks
``snapshot``    the values a rule is evaluated on, for one pair at one step
``ambiguity``   whether two rules at one priority can clash
``database``    the files, the manifest that freezes them, rule sets
``matching``    the per-pair matching policy and its record
``provider``    ``RuleDatabaseProvider``, behind the directive-provider interface
``cli``         the read-only command line: list, validate, history, show
"""

from .database import RULE_DB_ROOT, ActiveRuleSet, RuleDatabase, RuleSet
from .errors import RuleError
from .model import Rule
from .provider import RuleDatabaseProvider

__all__ = ["RULE_DB_ROOT", "ActiveRuleSet", "Rule", "RuleDatabase", "RuleDatabaseProvider", "RuleError", "RuleSet"]
