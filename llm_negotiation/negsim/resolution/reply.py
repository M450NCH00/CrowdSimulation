"""Reading an agent's reply (``docs/resolution.md``, D1) and its debrief (D8).

**The reply**::

    {"message": "...", "signal": "eye_contact", "intent": "...",
     "steps": [{"start": {"at_distance_m": 6}, "turn": {"to": "left", "degrees": 10},
                "speed_mps": 1.1, "until": {"seconds": 2}},
               {"speed_mps": 1.1, "until": "other_passes"}],
     "reason": "..."}

**Tolerated, as in issue #24:** surrounding whitespace, a Markdown code fence, extra keys (an
unknown key inside a step is also flagged). Enum values ignore case and surrounding spaces.

**Defaults:** a missing ``signal`` is ``none``; a missing ``message`` is ``""``; a missing
``reason`` is ``""`` and flagged. ``steps`` is required, and ``[]`` is the explicit "carry on".

**Parse failures**, each with its code (:class:`~negsim.negotiation.parsing.TurnParseError`, so
``request_with_retry`` asks once more): an unknown enum value; an event the scenario does not
have; ``start`` on any step but the opening one (unless the core template allows it,
``resolve_v5``, issue #64); ``speed_mps`` outside 0 to the agent's
``max_speed``; ``turn.degrees`` outside 0 to 90 **[placeholder]**; ``back_up_m`` not positive;
``until.seconds`` not positive; ``start.at_distance_m`` larger than the current distance; and
the structural ones (no ``intent``, ``steps`` not a list, a step with no ``until`` that does
not walk backwards, a number that is not a number).

**Ignored and flagged, not a failure:** a ``message`` or a ``signal`` in a condition that does
not allow it, and a speed or a turn on a step that walks backwards (it walks back at the
agent's backing speed, D1).

**Under ``resolve_v6``** (issue #65) an ``until`` may also be ``{"at_distance_m": <metres>}``, the
step ending when the person the agent would meet is that close (checked as a start's is); and an
event written as an object, ``{"other_passes": true}``, is read as the event and flagged
(``until_event_as_object``), unless its value is ``false``. RF-9's pilot (issue #64) lost 58 of
63 unreadable sends to these two forms. Earlier templates read an ``until`` as before.

**Under ``resolve_v8``** (issue #101; the template's ``sidestep`` flag) a step may also have
``"sidestep": {"to": "left" | "right", "metres": <number>}``: move that far to that side of the
line walked along, then walk on parallel to it. ``metres`` is more than 0 and at most
``MAX_SIDESTEP_M`` **[placeholder]**; a ``turn`` in the same step gives the angle and must be to
the same side; a sidestep cannot walk backwards nor stand still (``speed_mps`` 0); and its
``until`` is optional (the step ends when the agent is that far aside, or at the ``until`` if that
comes first). Under every earlier template a ``sidestep`` key is an unknown step key, flagged and
ignored, as before.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional

from ..negotiation.parsing import TurnParseError, _strip_code_fence
from .view import CONDITION_INDEPENDENT, CONDITION_TALK, CONDITIONS, SIGNALS, View

#: The largest turn a step may ask for, in degrees. **[placeholder]**
MAX_TURN_DEGREES = 90.0
#: The largest sidestep a step may ask for, in metres (``resolve_v8``, issue #101). **[placeholder]**
MAX_SIDESTEP_M = 3.0
SIDES = ("left", "right")
STEP_KEYS = ("start", "speed_mps", "turn", "back_up_m", "until")
SIDESTEP_KEY = "sidestep"  # a step key only under a template with the sidestep flag (resolve_v8)
START_NOW = "now"
START_AT_DISTANCE = "at_distance_m"
START_AFTER_SECONDS = "after_seconds"

#: The kinds of basis of D8.
DEBRIEF_KINDS = ("law_or_guidance", "published_study", "local_custom", "habit", "common_sense", "none")
SOURCE_UNCHECKED = "unchecked"


# --- what a reply is ------------------------------------------------------------------------------


@dataclass(frozen=True)
class Start:
    kind: str  # now, at_distance_m or after_seconds
    value: Optional[float] = None

    def as_json(self) -> Any:
        return START_NOW if self.kind == START_NOW else {self.kind: self.value}


@dataclass(frozen=True)
class Turn:
    to: str
    degrees: float


@dataclass(frozen=True)
class Sidestep:
    """Move ``metres`` to the ``to`` side of the line walked along (``resolve_v8``, issue #101)."""

    to: str
    metres: float


@dataclass(frozen=True)
class Until:
    seconds: Optional[float] = None
    event: Optional[str] = None
    at_distance_m: Optional[float] = None  # resolve_v6 (issue #65)

    def as_json(self) -> Any:
        if self.event is not None:
            return self.event
        if self.at_distance_m is not None:
            return {START_AT_DISTANCE: self.at_distance_m}
        return {"seconds": self.seconds}


@dataclass(frozen=True)
class Step:
    start: Optional[Start] = None
    speed_mps: Optional[float] = None
    turn: Optional[Turn] = None
    back_up_m: Optional[float] = None
    until: Optional[Until] = None
    sidestep: Optional[Sidestep] = None  # resolve_v8 (issue #101)

    def as_dict(self) -> dict[str, Any]:
        """The step in the reply format, without the keys it leaves out."""
        out: dict[str, Any] = {}
        if self.start is not None:
            out["start"] = self.start.as_json()
        if self.speed_mps is not None:
            out["speed_mps"] = self.speed_mps
        if self.turn is not None:
            out["turn"] = {"to": self.turn.to, "degrees": self.turn.degrees}
        if self.sidestep is not None:
            out[SIDESTEP_KEY] = {"to": self.sidestep.to, "metres": self.sidestep.metres}
        if self.back_up_m is not None:
            out["back_up_m"] = self.back_up_m
        if self.until is not None:
            out["until"] = self.until.as_json()
        return out


@dataclass(frozen=True)
class ParsedReply:
    condition: str
    message: str
    signal: str
    intent: str
    steps: tuple[Step, ...]
    reason: str
    flags: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "condition": self.condition,
            "message": self.message,
            "signal": self.signal,
            "intent": self.intent,
            "steps": [step.as_dict() for step in self.steps],
            "reason": self.reason,
            "flags": list(self.flags),
        }


@dataclass(frozen=True)
class ReplyContext:
    """What a reply is read against: the condition, the agent's top speed, the scenario's events,
    the current distance to the person the agent would meet (``None``: nobody in view), whether a
    later step may have a ``start`` (``resolve_v5``, issue #64; before it, only the opening step
    may), whether an ``until`` may be a distance or an event written as an object
    (``resolve_v6``, issue #65), and whether a step may sidestep (``resolve_v8``, issue #101)."""

    condition: str
    max_speed_mps: float
    events: tuple[str, ...]
    distance_m: Optional[float] = None
    later_step_start: bool = False
    until_at_distance: bool = False
    until_event_as_object: bool = False
    sidestep: bool = False

    def __post_init__(self) -> None:
        if self.condition not in CONDITIONS:
            raise ValueError(f"condition: one of {CONDITIONS}, got {self.condition!r}")

    @classmethod
    def of(
        cls, view: View, condition: str, events: Mapping[str, str] | tuple[str, ...], later_step_start: bool = False,
        until_at_distance: bool = False, until_event_as_object: bool = False, sidestep: bool = False,
    ) -> "ReplyContext":
        return cls(
            condition, view.me.max_speed_mps, tuple(events), view.meeting_distance_m(), later_step_start,
            until_at_distance, until_event_as_object, sidestep,
        )


# --- small readers --------------------------------------------------------------------------------


def _fail(code: str, detail: str = "") -> TurnParseError:
    return TurnParseError(code, detail)


def _object(raw: Optional[str]) -> dict[str, Any]:
    if raw is None or not raw.strip():
        raise _fail("empty_output")
    try:
        data = json.loads(_strip_code_fence(raw.strip()))
    except ValueError as exc:
        raise _fail("not_json", str(exc)) from exc
    if not isinstance(data, dict):
        raise _fail("not_an_object", f"got {type(data).__name__}")
    return data


def _number(value: Any, code: str, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _fail(code, f"{where}: expected a number, got {value!r}")
    return float(value)


def _enum(value: Any, allowed: tuple[str, ...], code: str, where: str) -> str:
    if not isinstance(value, str) or value.strip().lower() not in allowed:
        raise _fail(code, f"{where}: got {value!r}; expected one of {allowed}")
    return value.strip().lower()


def _text(data: Mapping[str, Any], key: str, required: bool) -> Optional[str]:
    if key not in data or data[key] is None:
        if required:
            raise _fail(f"missing_{key}")
        return None
    if not isinstance(data[key], str):
        raise _fail(f"{key}_not_text", f"got {type(data[key]).__name__}")
    return data[key].strip()


# --- the reply ------------------------------------------------------------------------------------


def _at_distance(amount: Any, context: ReplyContext, prefix: str, where: str) -> float:
    """A distance a ``start`` (or, under ``resolve_v6``, an ``until``) waits for: positive, someone
    in view, and no further than they are now. ``prefix`` names the failure codes."""
    metres = _number(amount, f"{prefix}_not_a_number", where)
    if metres <= 0.0:
        raise _fail(f"{prefix}_at_distance_not_positive", f"{where}: {metres}")
    if context.distance_m is None:
        raise _fail(f"{prefix}_at_distance_with_nobody_in_view", where)
    if metres > context.distance_m:
        raise _fail(f"{prefix}_at_distance_beyond_current", f"{where}: {metres} m, but the other is {context.distance_m:.1f} m away")
    return metres


def _start(value: Any, context: ReplyContext, where: str) -> Start:
    if isinstance(value, str):
        if value.strip().lower() != START_NOW:
            raise _fail("unknown_start", f"{where}: got {value!r}")
        return Start(START_NOW)
    if not isinstance(value, dict) or len(value) != 1:
        raise _fail("unknown_start", f"{where}: got {value!r}")
    ((kind, amount),) = value.items()
    if kind == START_AT_DISTANCE:
        return Start(START_AT_DISTANCE, _at_distance(amount, context, "start", where))
    if kind == START_AFTER_SECONDS:
        delay = _number(amount, "start_not_a_number", where)
        if delay < 0.0:
            raise _fail("start_after_seconds_negative", f"{where}: {delay}")
        return Start(START_AFTER_SECONDS, delay)
    raise _fail("unknown_start", f"{where}: got {value!r}")


def _until(value: Any, context: ReplyContext, where: str, flags: Optional[list[str]] = None) -> Until:
    if isinstance(value, str):
        event = value.strip().lower()
        if event not in context.events:
            raise _fail("unknown_event", f"{where}: got {value!r}; this scenario's events are {context.events}")
        return Until(event=event)
    if isinstance(value, dict) and set(value) == {"seconds"}:
        duration = _number(value["seconds"], "until_not_a_number", where)
        if duration <= 0.0:
            raise _fail("until_seconds_not_positive", f"{where}: {duration}")
        return Until(seconds=duration)
    if context.until_at_distance and isinstance(value, dict) and set(value) == {START_AT_DISTANCE}:
        return Until(at_distance_m=_at_distance(value[START_AT_DISTANCE], context, "until", where))
    if context.until_event_as_object and isinstance(value, dict) and len(value) == 1:
        ((name, amount),) = value.items()
        event = name.strip().lower() if isinstance(name, str) else None
        if event in context.events and amount is not False:
            if flags is not None:
                flags.append(f"until_event_as_object:{where}")
            return Until(event=event)
    raise _fail("unknown_until", f"{where}: got {value!r}")


def _step(index: int, data: Any, context: ReplyContext, flags: list[str]) -> Step:
    where = f"steps[{index}]"
    if not isinstance(data, dict):
        raise _fail("step_not_an_object", f"{where}: got {type(data).__name__}")
    known = STEP_KEYS + ((SIDESTEP_KEY,) if context.sidestep else ())
    flags.extend(f"unknown_step_key:{where}.{key}" for key in data if key not in known)
    start = None
    if "start" in data:
        if index > 0 and not context.later_step_start:
            raise _fail("start_on_later_step", where)
        start = _start(data["start"], context, f"{where}.start")
    back_up = None
    if data.get("back_up_m") is not None:
        back_up = _number(data["back_up_m"], "back_up_not_a_number", f"{where}.back_up_m")
        if back_up <= 0.0:
            raise _fail("back_up_not_positive", f"{where}.back_up_m: {back_up}")
    speed = None
    if data.get("speed_mps") is not None:
        speed = _number(data["speed_mps"], "speed_not_a_number", f"{where}.speed_mps")
        if not 0.0 <= speed <= context.max_speed_mps:
            raise _fail("speed_out_of_range", f"{where}.speed_mps: {speed}, allowed 0 to {context.max_speed_mps}")
    turn = None
    if data.get("turn") is not None:
        raw = data["turn"]
        if not isinstance(raw, dict) or "to" not in raw or "degrees" not in raw:
            raise _fail("unknown_turn", f"{where}.turn: got {raw!r}")
        side = _enum(raw["to"], SIDES, "unknown_turn_side", f"{where}.turn.to")
        angle = _number(raw["degrees"], "turn_not_a_number", f"{where}.turn.degrees")
        if not 0.0 <= angle <= MAX_TURN_DEGREES:
            raise _fail("turn_degrees_out_of_range", f"{where}.turn.degrees: {angle}, allowed 0 to {MAX_TURN_DEGREES:g}")
        turn = Turn(side, angle)
    sidestep = None
    if context.sidestep and data.get(SIDESTEP_KEY) is not None:  # resolve_v8 (issue #101)
        sidestep = _sidestep(data[SIDESTEP_KEY], f"{where}.{SIDESTEP_KEY}")
        if back_up is not None:
            raise _fail("sidestep_with_back_up", where)
        if speed == 0.0:
            raise _fail("sidestep_standing_still", f"{where}: a sidestep needs a speed above 0")
        if turn is not None and turn.degrees > 0.0 and turn.to != sidestep.to:
            raise _fail("sidestep_turn_other_side", f"{where}: turn to the {turn.to}, sidestep to the {sidestep.to}")
    until = None
    if data.get("until") is not None:
        until = _until(data["until"], context, f"{where}.until", flags)
    elif back_up is None and sidestep is None:
        raise _fail("missing_until", where)
    if back_up is not None:
        if speed is not None:
            flags.append(f"speed_ignored_on_back_up:{where}")
            speed = None
        if turn is not None:
            flags.append(f"turn_ignored_on_back_up:{where}")
            turn = None
    return Step(start, speed, turn, back_up, until, sidestep)


def _sidestep(raw: Any, where: str) -> Sidestep:
    if not isinstance(raw, dict) or set(raw) != {"to", "metres"}:
        raise _fail("unknown_sidestep", f"{where}: got {raw!r}")
    side = _enum(raw["to"], SIDES, "unknown_sidestep_side", f"{where}.to")
    metres = _number(raw["metres"], "sidestep_not_a_number", f"{where}.metres")
    if not 0.0 < metres <= MAX_SIDESTEP_M:
        raise _fail("sidestep_out_of_range", f"{where}.metres: {metres}, allowed more than 0 up to {MAX_SIDESTEP_M:g}")
    return Sidestep(side, metres)


def parse_reply(raw: Optional[str], context: ReplyContext) -> ParsedReply:
    """Read a raw reply against ``context``. Raises :class:`TurnParseError` if it cannot be used."""
    data = _object(raw)
    flags: list[str] = []

    message = ""
    if context.condition == CONDITION_TALK:
        message = _text(data, "message", required=False) or ""
    elif data.get("message") not in (None, ""):
        flags.append("message_ignored")

    signal = "none"
    if data.get("signal") is not None:
        if context.condition == CONDITION_INDEPENDENT:
            if not (isinstance(data["signal"], str) and data["signal"].strip().lower() == "none"):
                flags.append("signal_ignored")
        else:
            signal = _enum(data["signal"], SIGNALS, "unknown_signal", "signal")

    intent = _text(data, "intent", required=True)
    if not intent:
        raise _fail("empty_intent")

    if "steps" not in data:
        raise _fail("missing_steps")
    if not isinstance(data["steps"], list):
        raise _fail("steps_not_a_list", f"got {type(data['steps']).__name__}")
    steps = tuple(_step(i, step, context, flags) for i, step in enumerate(data["steps"]))

    reason = _text(data, "reason", required=False)
    if reason is None:
        flags.append("no_reason")
    return ParsedReply(context.condition, message, signal, intent, steps, reason or "", tuple(flags))


def reply_parser(context: ReplyContext) -> Callable[[Optional[str]], ParsedReply]:
    """``parse_reply`` bound to a context, in the form ``request_with_retry`` takes."""
    return lambda raw: parse_reply(raw, context)


# --- the debrief ----------------------------------------------------------------------------------


@dataclass(frozen=True)
class DebriefReply:
    basis: str
    kind: str
    source: Optional[str]  # None: the agent named no source
    applies_to: str
    source_status: str = SOURCE_UNCHECKED  # every source is stored unchecked; RF-14 checks it
    flags: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "basis": self.basis, "kind": self.kind, "source": self.source,
            "applies_to": self.applies_to, "source_status": self.source_status, "flags": list(self.flags),
        }


def parse_debrief(raw: Optional[str]) -> DebriefReply:
    """Read a debrief reply. ``source`` may be ``"none"`` (or null): no source is named."""
    data = _object(raw)
    basis = _text(data, "basis", required=True)
    if not basis:
        raise _fail("empty_basis")
    if "kind" not in data:
        raise _fail("missing_kind")
    kind = _enum(data["kind"], DEBRIEF_KINDS, "unknown_kind", "kind")
    if "source" not in data:
        raise _fail("missing_source")
    source = _text(data, "source", required=False)
    if source is not None and source.lower() in ("", "none"):
        source = None
    applies_to = _text(data, "applies_to", required=True)
    if not applies_to:
        raise _fail("empty_applies_to")
    flags = ("source_but_kind_none",) if source is not None and kind == "none" else ()
    return DebriefReply(basis, kind, source, applies_to, SOURCE_UNCHECKED, flags)
