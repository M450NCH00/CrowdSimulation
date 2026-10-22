"""Rendering a view into the messages an agent is sent, and the debrief (``docs/resolution.md``,
D2, D3 and D8).

**The order (D2).** The system message is the fixed text: the role, the condition's
instructions, its reply format, and the step format with the scenario's ``until`` events. It
depends on the condition and the scenario and on nothing else, so it is byte for byte the same
for every agent at every decision point, which is the prefix a provider's prompt cache reuses.
The user message is the description of the view, then the decision-point wrapper.

**Numbers** are those of ``negsim.rulegen.describe``: distances along the way to 0.1 m, widths
to 0.01 m, speeds to 0.01 m/s, angles to the whole degree; times here to 0.1 s.

**The debrief** (D8) follows the agent's last decision point: that prompt, the agent's reply to
it, and then the debrief question with every decision the agent made.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

from ..configutil import ConfigError
from ..negotiation.prompts import load_template_data
from ..rulegen.describe import _direction, _heading, across, along, fill, speed
from .scenario import Scenario
from .view import CONDITIONS, DETAIL_FULL, MOTION_BACKING, MOTION_STILL, View

KIND_CORE = "resolution"
KIND_DEBRIEF = "resolution_debrief"
CORE_TEMPLATE = "resolve_v1"
DEBRIEF_TEMPLATE = "resolve_debrief_v1"


def seconds(value: float) -> str:
    return f"{value:.1f}"


def _check_condition(condition: str) -> None:
    if condition not in CONDITIONS:
        raise ConfigError(f"condition: one of {CONDITIONS}, got {condition!r}")


@dataclass(frozen=True)
class RenderedPrompt:
    """What one decision point sends, and the templates it was rendered from."""

    messages: tuple[Mapping[str, str], ...]
    condition: str
    decision_point: int
    templates: Mapping[str, Mapping[str, str]]

    @property
    def system(self) -> str:
        return self.messages[0]["content"]

    @property
    def user(self) -> str:
        return self.messages[1]["content"]

    def as_dict(self) -> dict[str, Any]:
        return {
            "messages": [dict(m) for m in self.messages],
            "condition": self.condition,
            "decision_point": self.decision_point,
            "templates": {name: dict(entry) for name, entry in self.templates.items()},
        }


class CoreTemplate:
    """``resolve_v<n>``: one section per condition, every block of D2, the wrapper."""

    def __init__(self, key: str, data: Mapping[str, Any], sha256: str):
        missing = [c for c in CONDITIONS if c not in data["conditions"]]
        if missing:
            raise ConfigError(f"prompt template {key!r} has no section for {missing}")
        self.key, self.data, self.sha256 = key, data, sha256

    @classmethod
    def load(cls, key: str = CORE_TEMPLATE) -> "CoreTemplate":
        data, digest = load_template_data(key, KIND_CORE)
        return cls(key, data, digest)

    def identity(self) -> dict[str, str]:
        return {"key": self.key, "sha256": self.sha256}

    # --- the fixed text -------------------------------------------------------------------------

    def events_text(self, scenario: Scenario) -> str:
        items = [fill(self.data["event_item"], name=name, words=words) for name, words in scenario.events.items()]
        return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " or " + items[-1]

    def system(self, condition: str, scenario: Scenario) -> str:
        """The fixed text of a condition in a scenario: the same for every agent and decision point."""
        _check_condition(condition)
        section = self.data["conditions"][condition]
        return fill(
            self.data["system"],
            role=self.data["role"].strip(),
            instructions=section["instructions"].strip(),
            reply_format=section["reply_format"].strip(),
            step_format=fill(self.data["step_format"].strip(), events=self.events_text(scenario)),
        ).strip()

    def retry(self, condition: str) -> str:
        _check_condition(condition)
        return " ".join(self.data["conditions"][condition]["retry"].split())

    # --- the description ------------------------------------------------------------------------

    def description(self, view: View) -> str:
        v = self.data["view"]
        blocks = [self._me(view), self._notes(view), self._place(view)]
        blocks += [[block.header, *block.lines] for block in view.extra_blocks]
        blocks += [self._seen(view), self._heard(view), self._history(view)]
        if view.time_to_meet is not None:
            blocks.append([fill(v["time_to_meet"], n=view.time_to_meet.label, seconds=seconds(view.time_to_meet.seconds))])
        return "\n\n".join("\n".join(block) for block in blocks if block)

    def _me(self, view: View) -> list[str]:
        v, me = self.data["view"], view.me
        lines = [v["self_header"]]
        if me.age is not None:
            lines.append(fill(v["self_age"], age=me.age))
        if me.gender is not None:
            lines.append(fill(v["self_gender"], gender=v["genders"][me.gender]))
        if me.errand:
            lines.append(fill(v["self_errand"], errand=me.errand))
        if round(me.speed_mps, 2) == 0.0:
            lines.append(fill(v["self_still"], preferred=speed(me.preferred_speed_mps)))
        else:
            lines.append(fill(v["self_motion"], speed=speed(me.speed_mps), preferred=speed(me.preferred_speed_mps)))
        lines.append(fill(v["self_fastest"], fastest=speed(me.max_speed_mps)))
        lines.append(fill(v["self_body"], width=across(me.width_m)))
        lines += list(me.factor_lines)
        return lines

    def _notes(self, view: View) -> list[str]:
        v = self.data["view"]
        return [v["notes_header"], *(fill(v["note"], note=note) for note in view.notes)] if view.notes else []

    def _place(self, view: View) -> list[str]:
        return [self.data["view"]["place_header"], *view.place]

    def _seen(self, view: View) -> list[str]:
        v = self.data["view"]
        lines = [v["seen_header"]]
        if not view.seen:
            return lines + [v["seen_nobody"]]
        for person in view.seen:
            direction = _direction(person.bearing_rad, v["directions"])
            heading = _heading(person.heading_relative_rad, v["headings"])
            if person.detail != DETAIL_FULL:
                motion = fill(v["short_motion"][person.motion], heading=heading)
                lines.append(fill(v["seen_short"], n=person.label, distance=along(person.distance_m), direction=direction, motion=motion))
                continue
            lines.append(fill(v["seen_full"], n=person.label, distance=along(person.distance_m), direction=direction))
            if person.motion == MOTION_STILL:
                lines.append(fill(v["seen_still"], heading=heading))
            else:
                change = v["changes"]["shrinking" if (person.closing_speed_mps or 0.0) > 0.0 else "not_shrinking"]
                key = "seen_backing" if person.motion == MOTION_BACKING else "seen_motion"
                lines.append(fill(v[key], speed=speed(person.speed_mps), heading=heading, change=change))
            lines.append(fill(v["seen_body"], width=across(person.width_m)))
            if person.age is not None:
                lines.append(fill(v["seen_age"], age=person.age))
            if person.gender is not None:
                lines.append(fill(v["seen_gender"], gender=v["genders"][person.gender]))
            if person.signal != "none":
                lines.append(fill(v["seen_signal"], signal=v["signals_seen"][person.signal]))
            if person.changes:
                words = [v["since_last_look"][change] for change in person.changes]
                joined = words[0] if len(words) == 1 else ", ".join(words[:-1]) + f" {v['and']} " + words[-1]
                lines.append(fill(v["seen_changes"], changes=joined))
            lines += [fill(v["seen_extra"], line=line) for line in (*person.factor_lines, *person.pairwise_lines)]
        return lines

    def _heard(self, view: View) -> list[str]:
        v = self.data["view"]
        if not view.heard:
            return []
        lines = [v["heard_header"]]
        for heard in view.heard:
            if heard.label is None:
                lines.append(fill(v["heard_unseen"], message=heard.message))
            else:
                lines.append(fill(v["heard_seen"], n=heard.label, message=heard.message))
        return lines

    def _history(self, view: View) -> list[str]:
        v = self.data["view"]
        if not view.history:
            return []
        lines = [v["history_header"]]
        for done in view.history:
            lines.append(fill(v["history_intent"], ago=seconds(done.ago_s), intent=done.intent))
            if done.message:
                lines.append(fill(v["history_said"], message=done.message))
            if done.signal != "none":
                lines.append(fill(v["history_signal"], signal=v["signals_made"][done.signal]))
            lines.append(v["history_outcome"][done.outcome])
        return lines

    def wrapper(self, view: View) -> str:
        return self.data["decision_point"]["opening" if view.decision_point == 1 else "again"]


def render(view: View, condition: str, scenario: Scenario, core: Optional[CoreTemplate] = None) -> RenderedPrompt:
    """The messages of one decision point: the fixed text, then the description and the wrapper."""
    core = core or CoreTemplate.load()
    templates = {"core": core.identity(), "scenario": scenario.identity()}
    if {name: dict(entry) for name, entry in view.templates.items()} != templates:
        raise ConfigError(f"the view was built for templates {dict(view.templates)}, not {templates}")
    user = core.description(view) + "\n\n" + core.wrapper(view)
    messages = ({"role": "system", "content": core.system(condition, scenario)}, {"role": "user", "content": user})
    return RenderedPrompt(messages, condition, view.decision_point, templates)


# --- the debrief (D8) ---------------------------------------------------------------------------


class DebriefTemplate:
    def __init__(self, key: str, data: Mapping[str, Any], sha256: str):
        self.key, self.data, self.sha256 = key, data, sha256

    @classmethod
    def load(cls, key: str = DEBRIEF_TEMPLATE) -> "DebriefTemplate":
        data, digest = load_template_data(key, KIND_DEBRIEF)
        return cls(key, data, digest)

    def identity(self) -> dict[str, str]:
        return {"key": self.key, "sha256": self.sha256}

    def retry(self) -> str:
        return " ".join(self.data["retry"].split())

    def text(self, decisions: Sequence[Any]) -> str:
        """The debrief question, with each decision (a :class:`~negsim.resolution.reply.ParsedReply`)."""
        if not decisions:
            raise ValueError("a debrief is for an agent that made at least one decision")
        d, lines = self.data, []
        for decision in decisions:
            steps = json.dumps([step.as_dict() for step in decision.steps], ensure_ascii=False) if decision.steps else d["no_steps"]
            lines.append(fill(d["decision"], intent=decision.intent))
            lines.append(fill(d["steps"], steps=steps))
            if decision.message:
                lines.append(fill(d["said"], message=decision.message))
            if decision.signal != "none":
                lines.append(fill(d["signal"], signal=decision.signal))
        # The agent's own words go in last, so that nothing it wrote is read as a placeholder.
        return fill(d["text"], reply_format=d["reply_format"].strip(), decisions="\n".join(lines)).strip()


def debrief_messages(
    last: RenderedPrompt, last_raw_reply: str, decisions: Sequence[Any], template: Optional[DebriefTemplate] = None
) -> tuple[list[dict[str, str]], dict[str, Mapping[str, str]]]:
    """The debrief request of D8: the agent's last decision point, its reply, then the question.
    Returns the messages and the templates they came from."""
    template = template or DebriefTemplate.load()
    messages = [dict(m) for m in last.messages]
    messages.append({"role": "assistant", "content": last_raw_reply})
    messages.append({"role": "user", "content": template.text(decisions)})
    return messages, {**{name: dict(entry) for name, entry in last.templates.items()}, "debrief": template.identity()}
