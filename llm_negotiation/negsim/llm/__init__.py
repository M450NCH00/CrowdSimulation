"""LLM layer: the client interface, the DeepSeek and mock clients, pricing, the budget guard."""

from .base import (
    LLMClient,
    LLMError,
    LLMFatalError,
    LLMRequest,
    LLMResponse,
    LLMTransientError,
    Usage,
)
from .budget import (
    BudgetedClient,
    BudgetExceededError,
    BudgetGuard,
    SpendLedger,
    estimate_prompt_tokens,
)
from .deepseek import DeepSeekClient
from .mock import POLICIES as MOCK_POLICIES
from .mock import MockClient
from .pricing import DEFAULT_PRICE_TABLE, CostEstimate, PriceTable

__all__ = [
    "DEFAULT_PRICE_TABLE",
    "MOCK_POLICIES",
    "BudgetExceededError",
    "BudgetGuard",
    "BudgetedClient",
    "CostEstimate",
    "DeepSeekClient",
    "LLMClient",
    "LLMError",
    "LLMFatalError",
    "LLMRequest",
    "LLMResponse",
    "LLMTransientError",
    "MockClient",
    "PriceTable",
    "SpendLedger",
    "Usage",
    "estimate_prompt_tokens",
]
