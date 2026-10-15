"""The turn format and how a model's raw reply is read.

Each turn the model returns a JSON object with two keys::

    {"message": "<what it says to the other agent>", "stance": "I_GO_FIRST"}

Only ``message`` is shown to the other agent. ``stance`` is the speaker's current position
on who goes first and is what consensus is computed from.

This departs from GameChat, which asks the model to "output the number 1 and nothing else"
once it thinks a consensus has been reached and then asks each agent separately whether it
is the more important one (``LLM_utils.py:45`` and ``:67-77``, commit c49c35a). The reasons
are set out in ``docs/gamechat-notes.md``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Stance(str, Enum):
    I_GO_FIRST = "I_GO_FIRST"
    YOU_GO_FIRST = "YOU_GO_FIRST"
    UNDECIDED = "UNDECIDED"


@dataclass(frozen=True)
class ParsedTurn:
    message: str
    stance: Stance

    def as_json(self) -> str:
        """The turn re-serialised in the canonical form kept in the dialogue history."""
        return json.dumps({"message": self.message, "stance": self.stance.value}, ensure_ascii=False)


class TurnParseError(ValueError):
    """A reply that cannot be read as a turn. ``code`` is a short, stable identifier."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


def _strip_code_fence(text: str) -> str:
    """Remove a Markdown code fence around the reply, the one repair that is tolerated."""
    if not (text.startswith("```") and text.endswith("```") and len(text) >= 6):
        return text
    inner = text[3:-3]
    first_line, separator, rest = inner.partition("\n")
    # A fence may carry a language tag on its first line: ```json
    if separator and first_line.strip().isalpha():
        inner = rest
    return inner.strip()


def parse_turn_output(raw: Optional[str]) -> ParsedTurn:
    """Read a raw reply. Raises :class:`TurnParseError` if it is not a valid turn.

    Accepted: a JSON object with a non-empty text ``message`` and a ``stance`` that is one
    of the three values (case and surrounding spaces are ignored). Extra keys are ignored.
    A Markdown code fence around the object is removed first. Nothing else is repaired.
    """
    if raw is None or not raw.strip():
        raise TurnParseError("empty_output")
    try:
        data = json.loads(_strip_code_fence(raw.strip()))
    except ValueError as exc:
        raise TurnParseError("not_json", str(exc)) from exc
    if not isinstance(data, dict):
        raise TurnParseError("not_an_object", f"got {type(data).__name__}")

    if "message" not in data:
        raise TurnParseError("missing_message")
    message = data["message"]
    if not isinstance(message, str):
        raise TurnParseError("message_not_text", f"got {type(message).__name__}")
    message = message.strip()
    if not message:
        raise TurnParseError("empty_message")

    if "stance" not in data:
        raise TurnParseError("missing_stance")
    stance = data["stance"]
    if not isinstance(stance, str) or stance.strip().upper() not in Stance.__members__:
        raise TurnParseError("invalid_stance", f"got {stance!r}")
    return ParsedTurn(message, Stance[stance.strip().upper()])
