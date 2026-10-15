"""Rule generation: turning a conflict into a candidate rule (issue #30, SI-3a).

A conflict is taken from a finished baseline run as a **case**; a **design matrix** pairs
each case's geometry with persona pairs; each session is described in words by frozen
**templates**, first-person for two negotiating agents (condition A) or third-person for
one stating model (condition B); every proposed rule is **validated** and categorised; the
**writer** stores the valid ones in a staging database, never in ``rule_db/``; and each is
**replayed** alone on its case's scenario and **screened** alone in a crowd.
``docs/rule-generation.md`` describes the whole; ``docs/cases.md`` the cases.

``cases``       conflict cases: extraction from baseline runs, the frozen case store
``design``      the persona design matrix and the session list
``describe``    situation descriptions, the field glossary, the format example
``protocol``    condition A (negotiate a standing rule) and condition B (state a rule)
``validate``    the categories of a proposed rule
``writer``      the staging databases, and promotion into ``rule_db/``
``replay``      single-rule replay and crowd screening
``experiment``  the rule-generation experiment type, its cost preview and its logs
``mock``        mock-client policies that exercise every path without a network
"""
