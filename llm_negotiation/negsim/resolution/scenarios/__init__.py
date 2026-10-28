"""The scenario plug-ins (``docs/resolution.md``, D16). One module per scenario; adding one adds
a module and a line here, and edits nothing else."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from ...configutil import ConfigError
from ..scenario import Scenario
from .passing import PassingScenario
from .passing_crowd import PassingCrowdScenario
from .passing_group import PassingGroupScenario

PLUGINS: dict[str, type[Scenario]] = {
    "passing": PassingScenario,
    "passing_crowd": PassingCrowdScenario,
    "passing_group": PassingGroupScenario,  # issue #110
}


def load_scenario(name: str) -> Scenario:
    """A registered scenario, with its frozen template."""
    if name not in PLUGINS:
        raise ConfigError(f"unknown scenario {name!r}; known: {sorted(PLUGINS)}")
    return PLUGINS[name].load()


def plugin_for(case: Mapping[str, Any], named: Optional[str] = None) -> str:
    """The plug-in for ``case`` (issue #58): ``named`` if given, else the one plug-in whose
    ``CASE_TYPES`` holds the case's scenario type."""
    if named is not None:
        if named not in PLUGINS:
            raise ConfigError(f"unknown scenario {named!r}; known: {sorted(PLUGINS)}")
        return named
    kind = case["scenario"]["type"]
    found = [name for name, plugin in PLUGINS.items() if kind in plugin.CASE_TYPES]
    if len(found) != 1:
        raise ConfigError(
            f"case {case['case_id']} (type {kind!r}): {'no' if not found else 'more than one'} scenario plug-in takes it "
            f"({found}); name one in the config's scenarios"
        )
    return found[0]


__all__ = ["PLUGINS", "PassingCrowdScenario", "PassingGroupScenario", "PassingScenario", "load_scenario", "plugin_for"]
