"""Spend ledger and budget guard.

Every paid call is appended to a ledger file that persists across runs. Before a call is
made, the guard works out the most it could cost and refuses it if that would take the
ledger's total past the cap. The cap is therefore a hard one: the recorded total can never
exceed it, at the price of sometimes refusing a call that would in fact have fitted.
"""

from __future__ import annotations

import json
import math
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from .base import LLMClient, LLMError, LLMRequest, LLMResponse, LLMTransientError, Usage
from .pricing import PEAK, PriceTable

# DeepSeek's rule of thumb is "1 English character ~ 0.3 token" (api-docs.deepseek.com/
# quick_start/token_usage, checked 2026-10-13). The guard inflates it so that it errs high.
TOKENS_PER_CHAR = 0.3
ESTIMATE_SAFETY_FACTOR = 1.5
TOKENS_PER_MESSAGE_OVERHEAD = 8


class BudgetExceededError(RuntimeError):
    """A call was refused because it could take the recorded spend past the cap."""


def estimate_prompt_tokens(messages: Sequence[Mapping[str, str]]) -> int:
    """A deliberately high estimate of the prompt tokens in ``messages``."""
    characters = sum(len(message.get("content") or "") for message in messages)
    return (
        math.ceil(characters * TOKENS_PER_CHAR * ESTIMATE_SAFETY_FACTOR)
        + TOKENS_PER_MESSAGE_OVERHEAD * len(messages)
    )


class SpendLedger:
    """An append-only JSON Lines file with one line per paid call."""

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def entries(self) -> list[dict[str, Any]]:
        if not self.path.is_file():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def total_usd(self) -> float:
        """Sum of every recorded cost, read from the file so that it survives restarts."""
        return math.fsum(entry.get("cost_usd", 0.0) for entry in self.entries())

    def append(self, entry: Mapping[str, Any]) -> dict[str, Any]:
        record = dict(entry)
        record["cumulative_usd"] = round(self.total_usd() + record.get("cost_usd", 0.0), 10)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record


class BudgetGuard:
    def __init__(self, ledger: SpendLedger, cap_usd: float, prices: PriceTable):
        if cap_usd < 0.0:
            raise ValueError(f"the budget cap must not be negative, got {cap_usd}")
        self.ledger = ledger
        self.cap_usd = cap_usd
        self.prices = prices

    def remaining_usd(self) -> float:
        return self.cap_usd - self.ledger.total_usd()

    def worst_case(self, request: LLMRequest) -> float:
        """The most one send of ``request`` could cost."""
        return self.prices.worst_case(
            request.model, estimate_prompt_tokens(request.messages), request.max_tokens
        )

    def authorise(self, request: LLMRequest, max_attempts: int = 1) -> float:
        """Return the worst-case cost of one send, or raise if the call could exceed the cap.

        A client that retries may send the request ``max_attempts`` times, so that many
        worst cases have to fit under the cap.
        """
        worst = self.worst_case(request)
        spent = self.ledger.total_usd()
        if spent + worst * max_attempts > self.cap_usd:
            raise BudgetExceededError(
                f"call refused: USD {spent:.6f} is already recorded in {self.ledger.path.name}, "
                f"this call could cost up to USD {worst * max_attempts:.6f}, and the cap is "
                f"USD {self.cap_usd:.2f}"
            )
        return worst

    def record(
        self,
        request: LLMRequest,
        when_utc: datetime,
        usage: Usage,
        cost_usd: float,
        tier: str,
        cost_is_upper_bound: bool = False,
        error: Optional[str] = None,
    ) -> dict[str, Any]:
        return self.ledger.append(
            {
                "utc": when_utc.astimezone(timezone.utc).isoformat(timespec="seconds"),
                **dict(request.metadata),
                "model": request.model,
                **usage.as_dict(),
                "price_tier": tier,
                "cost_usd": round(cost_usd, 10),
                "cost_is_upper_bound": cost_is_upper_bound,
                "prices_date_checked": self.prices.date_checked,
                "error": error,
            }
        )


class BudgetedClient(LLMClient):
    """Wraps a paid client so that no call can be made without passing the budget guard."""

    def __init__(
        self,
        inner: LLMClient,
        guard: BudgetGuard,
        now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ):
        self.inner = inner
        self.guard = guard
        self.name = inner.name
        self.max_attempts = inner.max_attempts
        self._now = now  # the time of a call decides whether it is costed at the peak rate

    def complete(self, request: LLMRequest) -> LLMResponse:
        worst = self.guard.authorise(request, self.inner.max_attempts)
        started = self._now()
        try:
            response = self.inner.complete(request)
        except LLMError as exc:
            # A send that failed may still have reached the provider and been billed, so
            # each one is counted at its worst case; a run of timeouts cannot overspend.
            sends = exc.attempts if isinstance(exc, LLMTransientError) else 0
            self.guard.record(
                request,
                started,
                Usage(),
                worst * sends,
                PEAK if sends else self.guard.prices.tier_at(started),
                cost_is_upper_bound=bool(sends),
                error=f"{type(exc).__name__}: {exc}",
            )
            raise
        estimate = self.guard.prices.cost(request.model, response.usage, started)
        cost = estimate.usd + worst * response.failed_attempts
        self.guard.record(
            request,
            started,
            response.usage,
            cost,
            estimate.tier,
            cost_is_upper_bound=response.failed_attempts > 0,
        )
        return replace(response, cost_usd=cost, price_tier=estimate.tier)

    def describe(self) -> dict[str, Any]:
        return {
            **self.inner.describe(),
            "budget_cap_usd": self.guard.cap_usd,
            "spend_ledger": self.guard.ledger.path.name,
            "prices": self.guard.prices.describe(),
        }
