"""Prompt templates: loading, integrity checking, and rendering the system prompt.

All wording an agent ever sees lives in one YAML file per template version, under
``templates/``. A template version is frozen once it has been used: its SHA-256 is pinned
in ``templates/MANIFEST.json`` and checked on every load, so wording cannot change without
a new version number. That is how "no undocumented prompt tuning" is enforced rather than
merely promised.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional

import yaml

from ..configutil import ConfigError
from ..personas.schema import ATTRIBUTES, Persona

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
MANIFEST_PATH = TEMPLATE_DIR / "MANIFEST.json"

_REQUIRED_KEYS = ("template_id", "version", "requires_persona", "system", "output_format", "turns", "report")
_TURN_KEYS = ("first", "incoming", "no_reply", "retry")


class TemplateIntegrityError(ConfigError):
    """A template file does not match the hash pinned for it."""


@dataclass(frozen=True)
class Participant:
    """One side of a negotiation: an agent, its task, and its persona if it has one."""

    agent_id: int
    task: str
    task_type: Optional[str] = None
    persona: Optional[Persona] = None

    def attribute(self, name: str) -> Any:
        """The value of a persona attribute; the task is always the participant's own."""
        if name == "task":
            return self.task
        return None if self.persona is None else self.persona.attributes.get(name)

    def as_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "task": self.task,
            "task_type": self.task_type,
            "persona": None if self.persona is None else self.persona.as_dict(),
        }


def default_visibility() -> dict[str, bool]:
    """What one agent can see of the other unless the experiment says otherwise.

    Persona attributes take their default from the schema (age and gender are visible,
    task and backstory are not). ``speed`` and ``size`` are physical and visible.
    """
    visibility = {name: spec.observable for name, spec in ATTRIBUTES.items()}
    visibility.update({"speed": True, "size": True})
    return visibility


def resolve_visibility(raw: Any) -> dict[str, bool]:
    """Visibility settings from an experiment config: ``"default"`` or a partial mapping."""
    visibility = default_visibility()
    if raw is None or raw == "default":
        return visibility
    if not isinstance(raw, Mapping):
        raise ConfigError(f"visibility: expected 'default' or a mapping, got {raw!r}")
    for key, value in raw.items():
        if key not in visibility:
            raise ConfigError(f"visibility: unknown attribute {key!r}; known: {sorted(visibility)}")
        if not isinstance(value, bool):
            raise ConfigError(f"visibility.{key}: expected true or false, got {value!r}")
        visibility[key] = value
    return visibility


def template_sha256(path: Path) -> str:
    """SHA-256 of a template file's text with line endings normalised.

    Git on Windows may check the file out with CRLF line endings; the hash must not
    depend on that.
    """
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_manifest() -> dict[str, dict[str, Any]]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["templates"]


class PromptTemplate:
    def __init__(self, key: str, data: Mapping[str, Any], sha256: str):
        missing = [k for k in _REQUIRED_KEYS if k not in data]
        if missing:
            raise ConfigError(f"prompt template {key!r}: missing key(s) {missing}")
        missing_turns = [k for k in _TURN_KEYS if k not in data["turns"]]
        if missing_turns:
            raise ConfigError(f"prompt template {key!r}: turns is missing {missing_turns}")
        if f"{data['template_id']}_v{data['version']}" != key:
            raise ConfigError(
                f"prompt template file {key}.yaml declares "
                f"{data['template_id']!r} version {data['version']!r}"
            )
        self.key = key
        self.template_id: str = data["template_id"]
        self.version: int = data["version"]
        self.sha256 = sha256
        self.requires_persona: bool = data["requires_persona"]
        self._data = data

    def identity(self) -> dict[str, Any]:
        """What a run records about the template it used."""
        return {"key": self.key, "id": self.template_id, "version": self.version, "sha256": self.sha256}

    @property
    def report(self) -> Mapping[str, Any]:
        return self._data["report"]

    # --- system prompt -------------------------------------------------------------

    def render_system(
        self,
        participant: Participant,
        counterpart: Participant,
        scenario_type: str,
        visibility: Mapping[str, bool],
    ) -> str:
        """The system prompt for ``participant``: who it is and what it sees of ``counterpart``."""
        if self.requires_persona and participant.persona is None:
            raise ConfigError(
                f"prompt template {self.key!r} needs a persona, but agent "
                f"{participant.agent_id} has only a task"
            )
        fields = {
            "task": participant.task,
            "output_format": self._data["output_format"].strip(),
            "self_lines": self._self_lines(participant),
            "other_lines": self._other_lines(counterpart, visibility),
            "scene": self._scene(scenario_type),
        }
        return self._data["system"].format_map(fields).strip()

    def _values(self, participant: Participant) -> dict[str, Any]:
        """Attribute values for rendering, plus the words derived from them."""
        values = {"task": participant.task}
        if participant.persona is not None:
            values.update(participant.persona.attributes)
            values["task"] = participant.task
            nouns = self._data.get("gender_nouns", {})
            values["gender_noun"] = nouns.get(participant.persona.gender, participant.persona.gender)
        return values

    def _self_lines(self, participant: Participant) -> str:
        values = self._values(participant)
        lines = [
            line.format_map(values)
            for name, line in self._data.get("self_lines", {}).items()
            if values.get(name) not in (None, "")
        ]
        return "\n".join(lines)

    def _other_lines(self, counterpart: Participant, visibility: Mapping[str, bool]) -> str:
        values = self._values(counterpart)
        hidden_notes = self._data.get("other_hidden", {})
        lines = []
        for name, line in self._data.get("other_lines", {}).items():
            if visibility.get(name, False):
                if values.get(name) not in (None, ""):
                    lines.append(line.format_map(values))
            elif name in hidden_notes:
                lines.append(hidden_notes[name])
        return "\n".join(lines) if lines else self._data.get("other_nothing", "")

    def _scene(self, scenario_type: str) -> str:
        scenes = self._data.get("scenes")
        if scenes is None:
            return ""
        if scenario_type not in scenes:
            raise ConfigError(
                f"prompt template {self.key!r} has no scene text for scenario type {scenario_type!r}"
            )
        return scenes[scenario_type].strip()

    # --- turn wording ----------------------------------------------------------------

    def first_turn(self) -> str:
        return self._data["turns"]["first"]

    def incoming(self, message: str) -> str:
        return self._data["turns"]["incoming"].format(message=message)

    def no_reply(self) -> str:
        return self._data["turns"]["no_reply"]

    def retry(self) -> str:
        return self._data["turns"]["retry"]


def available_templates() -> list[str]:
    return sorted(load_manifest())


def load_template(key: str) -> PromptTemplate:
    """Load a template by key (e.g. ``persona_v1``) and check it against the manifest."""
    manifest = load_manifest()
    path = TEMPLATE_DIR / f"{key}.yaml"
    if key not in manifest or not path.is_file():
        raise ConfigError(f"unknown prompt template {key!r}; available: {sorted(manifest)}")
    digest = template_sha256(path)
    if digest != manifest[key]["sha256"]:
        raise TemplateIntegrityError(
            f"prompt template {key!r} has been edited: its hash no longer matches "
            "templates/MANIFEST.json. A template that has been used is frozen. Restore the "
            "file, or save the new wording as the next version, add it to the manifest, and "
            "record the reason in the work log."
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return PromptTemplate(key, data, digest)
