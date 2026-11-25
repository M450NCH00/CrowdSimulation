"""Turn token counts into an estimated cost, from a price table kept in a config file.

The cost is an estimate: tokens as the provider reports them, times the prices on its
public pricing page on the date recorded in the table. The provider's own bill is the
only authoritative figure.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any, Mapping

from ..configutil import PACKAGE_ROOT, ConfigError, as_number, check_keys, load_yaml
from .base import Usage

DEFAULT_PRICE_TABLE = PACKAGE_ROOT / "configs" / "llm" / "deepseek_pricing.yaml"
PEAK, OFF_PEAK = "peak", "off_peak"
_PER_MILLION = 1_000_000.0


@dataclass(frozen=True)
class TieredPrice:
    """USD per million tokens, in peak and in off-peak hours."""

    peak: float
    off_peak: float

    def at(self, tier: str) -> float:
        return self.peak if tier == PEAK else self.off_peak


@dataclass(frozen=True)
class ModelPrice:
    input_cache_hit: TieredPrice
    input_cache_miss: TieredPrice
    output: TieredPrice


@dataclass(frozen=True)
class CostEstimate:
    usd: float
    tier: str


class PriceTable:
    def __init__(
        self,
        models: Mapping[str, ModelPrice],
        peak_windows: list[tuple[time, time]],
        source_url: str,
        date_checked: str,
    ):
        self.models = dict(models)
        self.peak_windows = list(peak_windows)
        self.source_url = source_url
        self.date_checked = date_checked

    @classmethod
    def from_yaml(cls, path: Path | str = DEFAULT_PRICE_TABLE) -> "PriceTable":
        raw = load_yaml(path)
        where = str(path)
        check_keys(
            raw,
            where,
            ("source_url", "date_checked", "peak_hours_utc", "models"),
            ("schema_version", "provider", "currency", "unit"),
        )
        windows = []
        for index, window in enumerate(raw["peak_hours_utc"]):
            try:
                start, end = (time.fromisoformat(str(value)) for value in window)
            except (TypeError, ValueError) as exc:
                raise ConfigError(f"{where}.peak_hours_utc[{index}]: expected ['HH:MM', 'HH:MM']") from exc
            if not start < end:
                raise ConfigError(f"{where}.peak_hours_utc[{index}]: start must be before end")
            windows.append((start, end))
        models = {}
        for name, entry in raw["models"].items():
            label = f"{where}.models.{name}"
            check_keys(entry, label, ("input_cache_hit", "input_cache_miss", "output"), ("model_version",))
            models[name] = ModelPrice(
                *(
                    _tiered(entry[key], f"{label}.{key}")
                    for key in ("input_cache_hit", "input_cache_miss", "output")
                )
            )
        return cls(models, windows, str(raw["source_url"]), str(raw["date_checked"]))

    def price_of(self, model: str) -> ModelPrice:
        if model not in self.models:
            raise ConfigError(
                f"no price is recorded for model {model!r} (known: {sorted(self.models)}); "
                "the budget cap cannot be enforced without one"
            )
        return self.models[model]

    def tier_at(self, when_utc: datetime) -> str:
        """Peak on Monday to Friday inside a peak window (UTC), off-peak otherwise."""
        when_utc = when_utc.astimezone(timezone.utc)
        if when_utc.weekday() >= 5:
            return OFF_PEAK
        clock = when_utc.time()
        return PEAK if any(start <= clock < end for start, end in self.peak_windows) else OFF_PEAK

    def cost(self, model: str, usage: Usage, when_utc: datetime) -> CostEstimate:
        price, tier = self.price_of(model), self.tier_at(when_utc)
        # If the provider did not split the prompt tokens, cost them all as cache misses.
        hit = usage.cache_hit_tokens
        miss = max(usage.cache_miss_tokens, usage.prompt_tokens - hit)
        usd = (
            hit * price.input_cache_hit.at(tier)
            + miss * price.input_cache_miss.at(tier)
            + usage.completion_tokens * price.output.at(tier)
        ) / _PER_MILLION
        return CostEstimate(usd, tier)

    def worst_case(self, model: str, prompt_tokens: int, max_output_tokens: int) -> float:
        """Most a call could cost: peak rates, nothing cached, the full output allowance."""
        price = self.price_of(model)
        return (
            prompt_tokens * price.input_cache_miss.peak + max_output_tokens * price.output.peak
        ) / _PER_MILLION

    def describe(self) -> dict[str, Any]:
        return {"source_url": self.source_url, "date_checked": self.date_checked}


def _tiered(raw: Any, where: str) -> TieredPrice:
    check_keys(raw, where, (PEAK, OFF_PEAK))
    return TieredPrice(
        as_number(raw[PEAK], f"{where}.{PEAK}", minimum=0.0),
        as_number(raw[OFF_PEAK], f"{where}.{OFF_PEAK}", minimum=0.0),
    )
