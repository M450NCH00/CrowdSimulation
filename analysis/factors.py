"""The factors of a resolution experiment, as the analysis codes them (issue #63, RF-8).

negsim declares them (``negsim/personas/schema.py``, ``negsim/resolution/factors.py``,
``pairwise.py``); the analysis keeps its own copy so that it never imports negsim, and
``tests/test_load.py`` checks that the two agree.

**Person attributes** (RF-5): each has a base level and a marked level. In a design, a factor is
``neither`` or ``p1``: only person 1 ever has the marked level. Observable ones have a line that
someone else can be told (``<name>_visible`` switches it); the base level has no line.

**Situational factors** (RF-5): the same for both people.

**Pairwise factors** (RF-6): from the outcome row's own point of view columns
(``p1_finds_other_attractive``, ``p1_knows_other``), 0 or 1; both levels have a line.

**Real ethnicity** (RF-26, issue #92; ``negsim/resolution/ethnicity.py``): each person's group
(``p1_ethnicity``, ``p2_ethnicity``, one of :data:`ETHNICITY_GROUPS`); the design's
``ethnicity_pair`` (same or different) and its switch ``ethnicity_visible``. Every group has a
line, so the other's is told whenever ``<p>_other_ethnicity_shown`` >= 1.
"""

from __future__ import annotations

#: name -> (base level, marked level, observable)
PERSON: dict[str, tuple[str, str, bool]] = {
    "urgency": ("routine", "urgent", False),
    "mobility_aid": ("none", "cane", True),
    "load": ("none", "large_suitcase", True),
    "distraction": ("none", "phone", True),
    "assertiveness": ("gives_way", "holds_ground", False),
    "residence": ("local", "visitor", False),
    "memory_note": ("none", "bad_experience", False),
}
OBSERVABLE = tuple(name for name, (_, _, seen) in PERSON.items() if seen)
#: name -> (base level, marked level)
SITUATIONS: dict[str, tuple[str, str]] = {
    "surroundings": ("quiet", "busy"),
    "time_of_day": ("daytime", "late_night"),
}
#: The pairwise factors: the outcome row's column suffix -> the factor's name.
PAIRWISE: dict[str, str] = {
    "finds_other_attractive": "perceived_attractiveness",
    "knows_other": "familiarity",
}
#: Real ethnicity's groups (issue #92), in negsim's order.
ETHNICITY_GROUPS = ("chinese", "malay", "indian", "others")
#: Every design column a cell may have (``negsim.resolution.design.ALL_FACTORS``).
DESIGN_COLUMNS = (
    "age_pair", "gender_pair", "task", *PERSON, "ethnicity_pair", "demographics_visible", *(f"{name}_visible" for name in OBSERVABLE),
    "ethnicity_visible", *SITUATIONS, "attractiveness_0_sees_1", "attractiveness_1_sees_0", "familiarity",
    "attractiveness_visible", "familiarity_visible", "mapping",
)


#: The base level of a design column, where it has one; a session-level term is the other level
#: against it (``load[p1]``). A column not listed takes its levels in sorted order.
BASE_LEVEL: dict[str, str] = {
    **{name: "neither" for name in PERSON},
    **{name: base for name, (base, _) in SITUATIONS.items()},
    "age_pair": "same", "task": "none", "mapping": "p1_lower", "demographics_visible": "True",
    **{f"{name}_visible": "True" for name in OBSERVABLE},
    "attractiveness_visible": "True", "familiarity_visible": "True", "condition": "independent",
    "ethnicity_pair": "same", "ethnicity_visible": "True",
}


def factor_of(predictor: str) -> str:
    """The factor a predictor column belongs to (``own_load``, ``other_load`` and ``load[p1]`` ->
    ``load``)."""
    if "[" in predictor:
        return predictor.split("[", 1)[0]
    for prefix in ("own_", "other_"):
        if predictor.startswith(prefix):
            rest = predictor[len(prefix):]
            if rest.startswith("age"):
                return "age"
            if rest in ("female",):
                return "gender"
            if rest in ("demographics_hidden", "demographics_unseen"):
                return "demographics_visible"
            return rest
    for column, name in PAIRWISE.items():
        if predictor.startswith(column):
            return name
    if predictor == "pairwise_unseen":
        return "pairwise_visible"
    if predictor == "same_ethnicity":  # issue #92
        return "ethnicity_pair"
    if predictor == "ethnicity_unseen":
        return "ethnicity_visible"
    for name, (_, marked) in SITUATIONS.items():
        if predictor == f"{name}_{marked}":
            return name
    return predictor
