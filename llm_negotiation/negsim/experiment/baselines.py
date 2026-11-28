"""Named, versioned, frozen baselines: what "plain ORCA" means in an experiment (issue #28).

A baseline fixes the settings of the ORCA layer that every comparison is measured
against: the perturbation of preferred velocities, the tie-break, and, for every agent
type of a scenario, the neighbour limit and the sensing radius. It sets no directive:
"plain ORCA" is a baseline with no provider, and "rule-following" is the same baseline
with the rule provider on top. ``docs/baseline.md`` has the values and their reasons.

Baselines live in ``configs/baselines/<name>.yaml``. **They are never edited**: the SHA-256
of each file is frozen in ``configs/baselines/MANIFEST.json`` (line endings normalised to
LF), and :func:`load_baseline` refuses a file that is not listed there or no longer
matches. A change is a new file with the next version in its name, ``_v2``.

An experiment names a baseline with ``baseline: <name>``, at the top or in a level of a
factor. Its settings are laid on the scenario before the experiment's own
``scenario_overrides``, so a level can still vary one of them (the 5 m sensitivity check
does), and the run records both.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ..avoidance.orca import TIE_BREAKS
from ..avoidance.simulation import Perturbation
from ..configutil import PACKAGE_ROOT, ConfigError, as_choice, as_number, check_keys, load_yaml
from ..rules.database import file_sha256

BASELINE_DIR = PACKAGE_ROOT / "configs" / "baselines"
MANIFEST = "MANIFEST.json"
NAME = re.compile(r"^[a-z][a-z0-9_]*_v(?P<version>[1-9][0-9]*)$")
_KEYS = ("schema_version", "name", "version", "role", "description", "sign_off", "perturbation", "orca", "agent_types")
ROLES = ("primary", "secondary")
AGENT_TYPE_SETTINGS = ("max_neighbours", "sensing_radius")


@dataclass(frozen=True)
class Baseline:
    name: str
    version: int
    role: str
    description: str
    sign_off: str
    perturbation: Perturbation
    tie_break: str
    agent_types: Mapping[str, Any]
    file: str
    sha256: str

    def scenario_overrides(self, scenario_config: Mapping[str, Any]) -> dict[str, Any]:
        """The baseline's settings as overrides of one scenario's config."""
        return {
            "orca": {"tie_break": self.tie_break},
            "agent_types": {name: dict(self.agent_types) for name in scenario_config.get("agent_types", {})},
        }

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "role": self.role,
            "file": self.file,
            "sha256": self.sha256,
            "perturbation": self.perturbation.as_dict(),
            "orca": {"tie_break": self.tie_break},
            "agent_types": dict(self.agent_types),
            "sign_off": self.sign_off,
        }


def load_baseline(name: Any, directory: Path = BASELINE_DIR) -> Baseline:
    """A frozen baseline by name, or a :class:`ConfigError` saying why it cannot be used."""
    where = f"baseline {name!r}"
    if not isinstance(name, str) or NAME.match(name) is None:
        raise ConfigError(f"{where}: a baseline's name ends in its version, e.g. orca_perturbed_v1")
    path = directory / f"{name}.yaml"
    if not path.is_file():
        known = sorted(item.stem for item in directory.glob("*.yaml"))
        raise ConfigError(f"{where}: no such baseline; known: {known}")
    manifest = json.loads((directory / MANIFEST).read_text(encoding="utf-8")).get("files", {})
    relative = path.name
    if relative not in manifest:
        raise ConfigError(f"{where}: {relative} is not frozen in {MANIFEST}; a baseline must be")
    sha256 = file_sha256(path)
    if sha256 != manifest[relative]["sha256"]:
        raise ConfigError(
            f"{where}: {relative} has been edited since it was frozen. A baseline is never edited: a change is a "
            f"new file, {name.rsplit('_v', 1)[0]}_v{int(NAME.match(name)['version']) + 1}.yaml."
        )

    raw = load_yaml(path)
    check_keys(raw, where, _KEYS)
    if raw["schema_version"] != 1:
        raise ConfigError(f"{where}: schema_version {raw['schema_version']!r} is not supported")
    if raw["name"] != name or raw["version"] != int(NAME.match(name)["version"]):
        raise ConfigError(f"{where}: its name and version must match its file name")
    perturbation = check_keys(raw["perturbation"], f"{where}.perturbation", ("magnitude_mps",))
    orca = check_keys(raw["orca"], f"{where}.orca", ("tie_break",))
    agent_types = check_keys(raw["agent_types"], f"{where}.agent_types", AGENT_TYPE_SETTINGS)
    neighbours = agent_types["max_neighbours"]
    if isinstance(neighbours, bool) or not isinstance(neighbours, int) or neighbours < 1:
        raise ConfigError(f"{where}.agent_types.max_neighbours: expected a whole number, 1 or more")
    return Baseline(
        name=name,
        version=raw["version"],
        role=as_choice(raw["role"], f"{where}.role", ROLES),
        description=" ".join(str(raw["description"]).split()),
        sign_off=" ".join(str(raw["sign_off"]).split()),
        perturbation=Perturbation(as_number(perturbation["magnitude_mps"], f"{where}.perturbation.magnitude_mps", minimum=0.0)),
        tie_break=as_choice(orca["tie_break"], f"{where}.orca.tie_break", TIE_BREAKS),
        agent_types={
            "max_neighbours": neighbours,
            "sensing_radius": as_number(
                agent_types["sensing_radius"], f"{where}.agent_types.sensing_radius", minimum=0.0, strict_minimum=True
            ),
        },
        file=f"configs/baselines/{relative}",
        sha256=sha256,
    )
