"""The LLM client interface.

Everything that talks to a language model goes through :class:`LLMClient`. There are two
implementations: :class:`negsim.llm.deepseek.DeepSeekClient`, which costs money, and
:class:`negsim.llm.mock.MockClient`, which does not and is what every test uses.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence


class LLMError(RuntimeError):
    """A call to the model failed."""


class LLMTransientError(LLMError):
    """The call failed in a way that might not happen again (timeout, overload, rate limit).

    ``attempts`` is how many times the request was sent. Any of them may have reached the
    provider and been billed, so the budget guard counts each at its worst-case cost.
    """

    def __init__(self, message: str, attempts: int = 1):
        super().__init__(message)
        self.attempts = attempts


class LLMFatalError(LLMError):
    """The call failed in a way that retrying will not fix (bad key, no balance, bad request)."""


@dataclass(frozen=True)
class Usage:
    """Token counts as reported by the provider (or estimated, for the mock)."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_hit_tokens: int = 0
    cache_miss_tokens: int = 0
    reasoning_tokens: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "prompt_cache_hit_tokens": self.cache_hit_tokens,
            "prompt_cache_miss_tokens": self.cache_miss_tokens,
            "reasoning_tokens": self.reasoning_tokens,
        }

    def __add__(self, other: "Usage") -> "Usage":
        return Usage(
            self.prompt_tokens + other.prompt_tokens,
            self.completion_tokens + other.completion_tokens,
            self.cache_hit_tokens + other.cache_hit_tokens,
            self.cache_miss_tokens + other.cache_miss_tokens,
            self.reasoning_tokens + other.reasoning_tokens,
        )


@dataclass(frozen=True)
class LLMRequest:
    """One chat completion request.

    ``metadata`` is never sent to the provider; it labels the call in the spend ledger.
    """

    messages: Sequence[Mapping[str, str]]
    model: str
    temperature: float
    max_tokens: int
    json_mode: bool = True
    thinking: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def params(self) -> dict[str, Any]:
        """The sampling settings, for the logs (no messages, no credentials)."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "json_mode": self.json_mode,
            "thinking": self.thinking,
        }


@dataclass(frozen=True)
class LLMResponse:
    content: Optional[str]
    finish_reason: Optional[str]
    usage: Usage
    model: str
    latency_s: float
    started_utc: str
    response_id: Optional[str] = None
    system_fingerprint: Optional[str] = None
    is_mock: bool = False
    failed_attempts: int = 0  # sends that failed before this reply arrived
    cost_usd: float = 0.0
    price_tier: Optional[str] = None


class LLMClient(ABC):
    name: str
    max_attempts: int = 1  # most times one call to complete() can send the request

    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResponse:
        """Send one request and return the model's reply."""

    @abstractmethod
    def describe(self) -> dict[str, Any]:
        """Settings worth recording in a run's config. Must not contain credentials."""
