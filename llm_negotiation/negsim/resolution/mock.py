"""Mock-client policies for Step 1: every path of the reply and the debrief, with no network and
no cost (issue #57).

As those of issue #30 (``negsim.rulegen.mock``), these stand in for a model; they do not imitate
one. Each request takes one *path*, chosen by its ``path_index`` label (``metadata``, never sent
to a provider); ``attempt`` tells a retry apart. The replies are the same in every condition: a
condition that does not allow a message or a signal ignores it and flags it, which is itself a
path the parser must take.

``resolve_paths_v1``: carry on (``[]``); swerve left; swerve right; slow down, then resume; stop
until the other passes; back up, then wait; a delayed start; each signal; a talk message;
unreadable once, then a valid reply; unreadable twice; an out-of-range speed; an unknown event.

``debrief_paths_v1``: a debrief that names a source, and one that names none.

The speeds stay at or below 1.3 m/s, below every case's top speed (1.4 to 2.0 m/s).
"""

from __future__ import annotations

import json
from typing import Any, Callable

from ..llm.base import LLMRequest

UNREADABLE = "Sure! I would step aside: {intent: move"


def _reply(intent: str, steps: list[dict[str, Any]], reason: str = "A mock reply.", **extra: Any) -> str:
    return json.dumps({**extra, "intent": intent, "steps": steps, "reason": reason})


CARRY_ON = _reply("Carry on as I am.", [])

#: The paths of ``resolve_paths_v1``, in the order ``path_index`` cycles through them, each with
#: its reply (``None``: a path whose reply depends on the attempt).
RESOLVE_PATHS: dict[str, Any] = {
    "carry_on": CARRY_ON,
    "swerve_left": _reply("Move over to my left and walk on.", [{"start": "now", "turn": {"to": "left", "degrees": 20}, "speed_mps": 1.2, "until": {"seconds": 2}}]),
    "swerve_right": _reply("Move over to my right and walk on.", [{"turn": {"to": "right", "degrees": 20}, "speed_mps": 1.2, "until": {"seconds": 2}}]),
    "slow_then_resume": _reply(
        "Slow down for a moment, then walk on.",
        [{"speed_mps": 0.6, "until": {"seconds": 2}}, {"speed_mps": 1.3, "until": {"seconds": 1}}],
    ),
    "stop_until_other_passes": _reply("Stop and let them pass.", [{"speed_mps": 0, "until": "other_passes"}]),
    "back_up_then_wait": _reply("Step back, then wait.", [{"back_up_m": 1.0}, {"speed_mps": 0, "until": "other_passes"}]),
    "delayed_start": _reply("Keep going for a moment, then slow down.", [{"start": {"after_seconds": 1.5}, "speed_mps": 0.8, "until": {"seconds": 2}}]),
    **{
        f"signal_{signal}": _reply("Signal and carry on.", [], signal=signal)
        for signal in ("eye_contact", "nod", "wave_on", "hold_up_hand", "point", "other")
    },
    "talk_message": _reply("Tell them and carry on.", [], message="Excuse me.", signal="none"),
    "unreadable_then_carry_on": None,
    "unreadable_twice": UNREADABLE,
    "out_of_range": _reply("Run past.", [{"speed_mps": 9.9, "until": {"seconds": 1}}]),
    "unknown_event": _reply("Wait for a sign.", [{"speed_mps": 0, "until": "other_waves"}]),
}
RESOLVE_PATH_NAMES = tuple(RESOLVE_PATHS)


def resolve_paths_v1(request: LLMRequest) -> str:
    meta = request.metadata
    path = RESOLVE_PATH_NAMES[int(meta.get("path_index", 0)) % len(RESOLVE_PATH_NAMES)]
    if path == "unreadable_then_carry_on":
        return UNREADABLE if int(meta.get("attempt", 1)) == 1 else CARRY_ON
    return RESOLVE_PATHS[path]


#: The paths of ``debrief_paths_v1``.
DEBRIEF_PATHS: dict[str, str] = {
    "with_source": json.dumps({
        "basis": "A mock basis: guidance on walking in public places.", "kind": "law_or_guidance",
        "source": "A mock citation, 2020.", "applies_to": "my decision",
    }),
    "none": json.dumps({"basis": "Nothing in particular.", "kind": "none", "source": "none", "applies_to": "my decision"}),
}
DEBRIEF_PATH_NAMES = tuple(DEBRIEF_PATHS)


def debrief_paths_v1(request: LLMRequest) -> str:
    index = int(request.metadata.get("path_index", 0))
    return DEBRIEF_PATHS[DEBRIEF_PATH_NAMES[index % len(DEBRIEF_PATH_NAMES)]]


POLICIES: dict[str, Callable[[LLMRequest], str]] = {
    "resolve_paths_v1": resolve_paths_v1, "debrief_paths_v1": debrief_paths_v1,
}
