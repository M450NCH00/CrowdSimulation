"""The passing scenarios of rounds 1 to 3 (``docs/resolution.md``, D17): head-on in a corridor,
meeting in a narrow passage, and someone behind saying "excuse me". They share one description
side, ``scenario_passing_v1``: the wall, passage and narrowing lines of issue #32, and the events
``other_passes``, ``other_stops`` and ``i_am_out_of_the_stretch``."""

from __future__ import annotations

from typing import Any, Mapping

from ...rulegen.describe import _place
from ..scenario import Scenario


class PassingScenario(Scenario):
    TEMPLATE = "scenario_passing_v1"
    #: The case types of rounds 1 to 3 (``negsim.scenarios``). The place lines read only walls,
    #: passage widths and narrowings, so a case of another type renders the same way.
    CASE_TYPES = ("wide_corridor_head_on", "passage_meeting", "overtaking")

    def place_lines(self, case: Mapping[str, Any], record: Mapping[str, Any]) -> list[str]:
        """``describe._place``, the lines of ``rulegen_negotiate_v2`` (issue #32), unchanged."""
        return _place(case, record, self.data["place"])
