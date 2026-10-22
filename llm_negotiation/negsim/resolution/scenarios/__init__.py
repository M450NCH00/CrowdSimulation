"""The scenario plug-ins (``docs/resolution.md``, D16). One module per scenario; adding one adds
a module and a line here, and edits nothing else."""

from __future__ import annotations

from ...configutil import ConfigError
from ..scenario import Scenario
from .passing import PassingScenario

PLUGINS: dict[str, type[Scenario]] = {
    "passing": PassingScenario,
}


def load_scenario(name: str) -> Scenario:
    """A registered scenario, with its frozen template."""
    if name not in PLUGINS:
        raise ConfigError(f"unknown scenario {name!r}; known: {sorted(PLUGINS)}")
    return PLUGINS[name].load()


__all__ = ["PLUGINS", "PassingScenario", "load_scenario"]
