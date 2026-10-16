"""Why a rule, a rule set or the rule database was refused."""

from __future__ import annotations

#: The reasons a rule can be refused, by category. ``docs/rule-format.md`` explains each.
CATEGORIES = (
    "file",  # the file cannot be read, or its name does not match its contents
    "manifest",  # the file is not the version the manifest froze, or is not listed
    "history",  # the versions of a rule do not run 1, 2, 3, ...
    "schema",  # the JSON Schema check failed
    "unknown_field",  # a field no rule can read, or not where it was used
    "unobservable_field",  # a field that exists but that the two agents cannot both see
    "protected_attribute",  # a person's group, or anything derived from it, which no rule may read (issue #32)
    "unit",  # a number without its unit, or in a unit that does not fit the field
    "value",  # a value of the wrong kind for its field or operator
    "operator",  # an operator that does not apply to its field
    "roles",  # the roles and the directives do not fit together
    "no_tie_policy",  # a role assignment that does not say what happens on a tie
    "reciprocity",  # responsibility shares that sum to less than 1
    "passage_order",  # passage orders that are not one leader and one follower
    "back_up",  # a rule that says who backs up but not exactly one role (issue #32)
    "side",  # two roles told to pass on opposite sides
    "ambiguous",  # two rules at one priority that can match the same pair with different directives
    "visibility",  # a rule reads a field the run's visibility settings hide
    "status",  # a rule set enables a rule whose status does not allow it
    "ruleset",  # a rule set names a rule or version that is not in the database
)


class RuleError(ValueError):
    """A rule (or rule set) that cannot be used, with the category of the reason.

    ``category`` is one of :data:`CATEGORIES`; the message says what was wrong and where.
    """

    def __init__(self, category: str, message: str):
        if category not in CATEGORIES:
            raise ValueError(f"unknown rule error category {category!r}")
        super().__init__(message)
        self.category = category

    def __str__(self) -> str:
        return f"[{self.category}] {super().__str__()}"
