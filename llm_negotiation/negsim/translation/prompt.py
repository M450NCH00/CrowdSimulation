"""The translator's prompt (issue #67, RF-12, task 1), rendered from the frozen template ``translate_v1``.

The system message is the role, the task, and the rule format as ``rulegen_common_v2`` describes it
to rule generation (#32), word for word: its field list is generated from the field catalogue and
the schema of format 3, and refused if it is not the one that template was frozen with
(``negsim.rulegen.describe.check_glossary``). It is the same for every rule, so the provider's
prompt cache can reuse it. The user message is the extracted rule: its words, its factors with
each column's meaning as the extraction template described it to the extractor, and its predict
list. Nothing else is shown: not its fidelity, debrief support or references (the code fills the
references in, ``negsim.translation.experiment``).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

from ..rulegen.describe import Templates, fill, format_example_text, glossary_text, load_templates

KIND = "rule_translation"
DEFAULT_TEMPLATE = "translate_v1"


def load(key: str = DEFAULT_TEMPLATE) -> Templates:
    """A translation template and the common template it uses, both checked against the manifest."""
    return load_templates(key, KIND)


def _line(text: Any) -> str:
    return " ".join(str(text).split())


def _items(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_line(item) for item in value if str(item).strip()]
    return [_line(value)] if value is not None and str(value).strip() else []


@dataclass(frozen=True)
class RenderedTranslation:
    messages: list[dict[str, str]]
    template: dict[str, Any]


def system_message(templates: Templates) -> str:
    """The same for every rule: the demographic fields are listed (a format 3 rule may read age and
    gender; whether a run shows them is the run's visibility)."""
    return fill(
        templates.data["system"],
        glossary=glossary_text(templates.common, True),
        format_example=format_example_text(templates.common),
        reply_format=templates.data["reply_format"].strip(),
    ).strip()


def render(templates: Templates, rule: Mapping[str, Any], column_meanings: Mapping[str, str], encounter_description: str) -> RenderedTranslation:
    """The two messages for one extracted rule (an RF-11 rule file, read)."""
    data = templates.data
    exceptions = _items(rule.get("exceptions"))
    factors = _items(rule.get("factors_used"))
    predict = rule.get("predict")
    target = str(predict.get("target", "")) if isinstance(predict, Mapping) else ""

    def column_line(column: str) -> str:
        return fill(data["factor_line"], column=column, meaning=_line(column_meanings.get(column, "not a column of the table")))

    user = fill(
        data["user"],
        encounter_description=_line(encounter_description),
        rule=_line(rule.get("rule", "")),
        applies_when=_line(rule.get("applies_when", "")),
        action=_line(rule.get("action", "")),
        exceptions="\n".join(fill(data["exception_line"], exception=text) for text in exceptions) or data["no_exceptions"],
        needs_communication=data["answer_yes"] if rule.get("needs_communication") is True else data["answer_no"],
        factors="\n".join(column_line(column) for column in factors) or data["no_exceptions"],
        predict=json.dumps(predict, ensure_ascii=False),
        target=column_line(target) if target else data["no_exceptions"],
    ).strip()
    return RenderedTranslation([{"role": "system", "content": system_message(templates)}, {"role": "user", "content": user}], templates.identity())


def retry_message(templates: Templates, error: str) -> dict[str, str]:
    return {"role": "user", "content": fill(" ".join(templates.data["retry"].split()), error=error)}
