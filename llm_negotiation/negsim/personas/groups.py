"""Fictional group labels for the ethnicity attribute (issue #32, Part 1).

A person may belong to a **fictional** group, named by an invented label such as ``Kestrop``.
The labels carry nothing but a name: no description, history, appearance or customs. They let
an experiment test in-group against out-group effects, which have a human baseline in the
minimal group paradigm, without reproducing any real group's stereotypes; for the same reason
they cannot show how a model treats a real ethnicity (``docs/fictional-groups.md``).

The default labels were each searched on the web, and confirmed not to be a real ethnonym,
nationality, place name, language or common word in English, Malay, Chinese or Tamil; the
searches and their results are recorded in ``docs/fictional-groups.md``, section 2. A config
may give its own labels. **The check of a new label is that search, not this module**:
:func:`check_labels` only refuses what is malformed and, as a guard against an obvious mistake,
the names in :data:`REAL_GROUP_NAMES`.

No rule may read a person's group (``negsim.rules``, ``protected_attribute``).
"""

from __future__ import annotations

import re
from typing import Any

#: The default label set, in rotation order (``docs/fictional-groups.md``, section 2).
DEFAULT_GROUP_LABELS = ("Kestrop", "Dremmik", "Pellund")
#: The words that introduce the attribute in a prompt ("You belong to the Kestrop ethnic group.").
#: A setting of each experiment, recorded with every session; a decision pending the
#: supervisor (DD86).
DEFAULT_FRAMING = "ethnic group"
#: A label is one capitalised word of letters: no spaces, digits or punctuation, so that no
#: description can be written into one.
LABEL_PATTERN = re.compile(r"^[A-Z][a-z]{2,15}$")
FRAMING_PATTERN = re.compile(r"^[a-z]+( [a-z]+){0,2}$")
MIN_LABELS = 3

#: Real names refused as labels, lower-case: Singapore's census ethnic groups and the
#: communities within them, and other groups, nationalities and languages present in
#: Singapore. A guard against an obvious mistake, not the check itself.
REAL_GROUP_NAMES = frozenset(
    {
        # The census groups, and the words for them in Malay, Chinese (pinyin) and Tamil.
        "chinese", "malay", "indian", "eurasian", "others", "melayu", "cina", "huaren", "huayi",
        "tamil", "tamilan", "serani", "india",
        # Chinese dialect groups.
        "hokkien", "teochew", "cantonese", "hakka", "hainanese", "foochow", "henghua", "hockchia",
        "shanghainese", "hokchew",
        # Malay communities.
        "javanese", "boyanese", "bawean", "bugis", "minangkabau", "banjar", "orang",
        # Indian communities.
        "malayalee", "malayali", "punjabi", "sikh", "bengali", "gujarati", "sindhi", "telugu",
        "sinhalese", "pakistani", "bangladeshi", "kannadiga",
        # Others, and Singapore's own.
        "peranakan", "baba", "nyonya", "kristang", "arab", "armenian", "jewish", "filipino",
        "thai", "vietnamese", "burmese", "japanese", "korean", "caucasian", "european",
        "african", "american", "british", "australian", "singaporean", "malaysian",
        "indonesian",
    }
)


class GroupLabelError(ValueError):
    """A group label, a label set or a framing word that cannot be used."""


def check_label(value: Any) -> str:
    """One label: a capitalised word of 3 to 16 letters that is not a real group's name."""
    if not isinstance(value, str) or not LABEL_PATTERN.match(value):
        raise GroupLabelError(
            f"a group label is one capitalised word of 3 to 16 letters and nothing else (a fictional name, "
            f"no description), got {value!r}"
        )
    if value.lower() in REAL_GROUP_NAMES:
        raise GroupLabelError(f"{value!r} is the name of a real group; a label must be fictional (docs/fictional-groups.md)")
    return value


def check_labels(values: Any) -> tuple[str, ...]:
    """A label set: at least three labels, each valid, no two the same ignoring case."""
    if not isinstance(values, (list, tuple)) or len(values) < MIN_LABELS:
        raise GroupLabelError(f"a label set is a list of at least {MIN_LABELS} labels, got {values!r}")
    labels = tuple(check_label(value) for value in values)
    if len({label.lower() for label in labels}) != len(labels):
        raise GroupLabelError(f"two labels of {list(labels)} are the same")
    return labels


def check_framing(value: Any) -> str:
    """The words that introduce the attribute: one to three lower-case words."""
    if not isinstance(value, str) or not FRAMING_PATTERN.match(value):
        raise GroupLabelError(f"a framing is one to three lower-case words, such as {DEFAULT_FRAMING!r}, got {value!r}")
    return value
