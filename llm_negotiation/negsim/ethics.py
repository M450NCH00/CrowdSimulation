"""The supervisor's ethics sign-offs, as ``CLAUDE.md`` records them (issue #32; issue #61).

A factor that needs an ethics sign-off is off by default, and no paid run may switch it on until
the user has recorded the supervisor's approval in ``CLAUDE.md``: one exact sentence, with the
date. The experiment that uses the factor refuses a paid run without it, before anything is sent
(``refused_no_sign_off`` in its ``invocations.jsonl``). A mock run needs none, so that the
pipeline can be rehearsed. Nothing in negsim writes either sentence.

=======================================  ==========================================  =================================
Factor                                   The sentence, with the date filled in       Where
=======================================  ==========================================  =================================
the fictional group (issue #32)          :data:`ETHNICITY_SIGN_OFF`                  ``docs/fictional-groups.md``, 6
perceived attractiveness (issue #61)     :data:`ATTRACTIVENESS_SIGN_OFF`             ``docs/pairwise-factors.md``, 6
=======================================  ==========================================  =================================
"""

from __future__ import annotations

import re
from pathlib import Path

from .configutil import REPO_ROOT

#: Where the supervisor's approvals are recorded.
SIGN_OFF_FILE = REPO_ROOT / "CLAUDE.md"
ETHNICITY_SIGN_OFF = re.compile(
    r"Ethics sign-off for the fictional-group factor \(issue #32\): approved by the supervisor on \d{4}-\d{2}-\d{2}"
)
ATTRACTIVENESS_SIGN_OFF = re.compile(
    r"Ethics sign-off for the perceived-attractiveness factor \(issue #61\): approved by the supervisor on \d{4}-\d{2}-\d{2}"
)


def recorded(sentence: re.Pattern[str], path: Path) -> bool:
    """Whether the file at ``path`` holds ``sentence``."""
    return path.is_file() and sentence.search(path.read_text(encoding="utf-8")) is not None
