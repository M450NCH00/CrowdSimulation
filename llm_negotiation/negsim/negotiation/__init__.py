"""Negotiation: prompt templates, persona rendering, the situation report, the protocol."""

from .consensus import agreed_leader, find_consensus
from .parsing import ParsedTurn, Stance, TurnParseError, parse_turn_output
from .prompts import (
    Participant,
    PromptTemplate,
    TemplateIntegrityError,
    available_templates,
    default_visibility,
    load_template,
    resolve_visibility,
    template_sha256,
)
from .protocol import (
    END_ABORTED,
    END_CONFLICT_OVER,
    END_CONSENSUS,
    END_MESSAGE_LIMIT,
    MAX_ATTEMPTS_PER_TURN,
    Attempt,
    Dialogue,
    NegotiationSettings,
    Turn,
)
from .situation import (
    INFO_FIELDS,
    REQUIRES_VISIBILITY,
    Observation,
    RegionStatus,
    observe,
    region_status,
    render_report,
    resolve_info_fields,
)

__all__ = [
    "END_ABORTED",
    "END_CONFLICT_OVER",
    "END_CONSENSUS",
    "END_MESSAGE_LIMIT",
    "INFO_FIELDS",
    "MAX_ATTEMPTS_PER_TURN",
    "REQUIRES_VISIBILITY",
    "Attempt",
    "Dialogue",
    "NegotiationSettings",
    "Observation",
    "ParsedTurn",
    "Participant",
    "PromptTemplate",
    "RegionStatus",
    "Stance",
    "TemplateIntegrityError",
    "Turn",
    "TurnParseError",
    "agreed_leader",
    "available_templates",
    "default_visibility",
    "find_consensus",
    "load_template",
    "observe",
    "parse_turn_output",
    "region_status",
    "render_report",
    "resolve_info_fields",
    "resolve_visibility",
    "template_sha256",
]
