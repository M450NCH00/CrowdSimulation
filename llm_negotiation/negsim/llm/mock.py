"""Deterministic mock client: no network, no cost.

Used by every test, and by ``run_experiment.py --client mock`` to rehearse an experiment
config before spending anything. Its replies are a fixed function of the request, so a
mock run is exactly reproducible.

Two ways to drive it:

``script``
    A list of raw replies returned in order (``None`` stands for an empty reply). This is
    how the tests produce malformed output, stubborn agents and so on.

``policy``
    A named rule that reads the prompt and answers in the turn format. The rules are
    deliberately crude; they stand in for a model, they do not imitate one.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from typing import Any, Callable, Optional, Sequence

from .base import LLMClient, LLMRequest, LLMResponse, Usage

Policy = Callable[[LLMRequest], Optional[str]]

# Words that give away one of GameChat's three task types (lower number = higher priority).
_TASK_KEYWORDS = (
    (0, "hospital", ("hospital", "emergency room", "operating room", "the er", "surgery")),
    (1, "airport", ("airport", "flight", "plane")),
    (2, "grocery store", ("grocery", "groceries", "supermarket", "the store")),
)


def _reply(message: str, stance: str) -> str:
    return json.dumps({"message": message, "stance": stance})


def _task_rank(text: str) -> Optional[tuple[int, str]]:
    lowered = text.lower()
    for rank, label, keywords in _TASK_KEYWORDS:
        if any(re.search(rf"\b{re.escape(keyword)}\b", lowered) for keyword in keywords):
            return rank, label
    return None


def task_priority(request: LLMRequest) -> str:
    """Rank the two tasks as hospital > airport > grocery and take the matching stance.

    Its own task is read from the lines of the system prompt that describe the agent
    itself ("You are ..."), the other agent's from what the other agent has said so far.
    """
    system = next((m["content"] for m in request.messages if m["role"] == "system"), "")
    own_lines = [
        line for line in system.splitlines() if line.lstrip("- ").startswith("You are")
    ]
    own = _task_rank(" ".join(own_lines))
    other = _task_rank(" ".join(m["content"] for m in request.messages if m["role"] == "user"))
    label = own[1] if own else "somewhere"
    if own is None or other is None or own[0] == other[0]:
        return _reply(f"I am headed to the {label}. Where are you headed?", "UNDECIDED")
    if own[0] < other[0]:
        return _reply(f"I am headed to the {label}, which is urgent. I will go first.", "I_GO_FIRST")
    return _reply(f"I am headed to the {label}, which can wait. You go first.", "YOU_GO_FIRST")


def first_speaker_goes(request: LLMRequest) -> str:
    """Whoever speaks first claims the way; the other agent agrees at once.

    The dialogue labels each request with its turn index, and the agents alternate, so
    the first speaker is the one who is asked on the even turns.
    """
    if int(request.metadata.get("turn_index", 0)) % 2 == 0:
        return _reply("I will go first.", "I_GO_FIRST")
    return _reply("Go ahead, I will wait.", "YOU_GO_FIRST")


def insist(request: LLMRequest) -> str:
    """Never gives way, so two of these never reach a consensus."""
    return _reply("I am going first.", "I_GO_FIRST")


def undecided(request: LLMRequest) -> str:
    return _reply("I am not sure yet.", "UNDECIDED")


POLICIES: dict[str, Policy] = {
    "task_priority": task_priority,
    "first_speaker_goes": first_speaker_goes,
    "insist": insist,
    "undecided": undecided,
}


class MockClient(LLMClient):
    name = "mock"

    def __init__(
        self,
        policy: str | Policy = "first_speaker_goes",
        script: Optional[Sequence[Optional[str]]] = None,
    ):
        if isinstance(policy, str):
            if policy not in POLICIES:
                raise ValueError(f"unknown mock policy {policy!r}; expected one of {sorted(POLICIES)}")
            self.policy_name, self._policy = policy, POLICIES[policy]
        else:
            self.policy_name, self._policy = getattr(policy, "__name__", "custom"), policy
        self._script = None if script is None else list(script)
        self.requests: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        if self._script is not None:
            if not self._script:
                raise AssertionError("the mock client's script ran out of replies")
            content = self._script.pop(0)
        else:
            content = self._policy(request)
        prompt_chars = sum(len(m["content"] or "") for m in request.messages)
        prompt_tokens = math.ceil(prompt_chars * 0.3)
        return LLMResponse(
            content=content,
            finish_reason="stop",
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=math.ceil(len(content or "") * 0.3),
                cache_miss_tokens=prompt_tokens,
            ),
            model=f"mock:{self.policy_name if self._script is None else 'script'}",
            latency_s=0.0,
            started_utc=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            is_mock=True,
        )

    def describe(self) -> dict[str, Any]:
        return {
            "client": self.name,
            "policy": "script" if self._script is not None else self.policy_name,
        }
