"""Prompt rendering shared by estimate_cost.py and the generator.

Keeping this in one place guarantees the cost estimate is computed from the
exact strings that will later be sent to the API.
"""

from __future__ import annotations

import functools
from pathlib import Path

import yaml

import config


# ----------------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------------
def _load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@functools.lru_cache(maxsize=1)
def load_all():
    scenarios = _load_yaml(config.SCENARIOS_YAML)["scenarios"]
    personas = _load_yaml(config.PERSONAS_YAML)
    action_space = _load_yaml(config.ACTION_SPACE_YAML)
    system_prompt = (config.PROMPTS_DIR / "system_sg.txt").read_text(encoding="utf-8").strip()
    user_template = (config.PROMPTS_DIR / "user_template.txt").read_text(encoding="utf-8").strip()
    output_contract = (config.PROMPTS_DIR / "output_contract.json").read_text(encoding="utf-8").strip()
    return {
        "scenarios": scenarios,
        "personas": personas,
        "action_space": action_space,
        "system_prompt": system_prompt,
        "user_template": user_template,
        "output_contract": output_contract,
    }


# ----------------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------------
def allowed_actions_block(scenario: dict, action_space: dict) -> str:
    by_id = {a["id"]: a for a in action_space["high_level"]}
    ids = scenario.get("expected_actions") or list(by_id)
    lines = []
    for aid in ids:
        a = by_id[aid]
        lines.append(f"  - {aid}: {a['label']}")
    return "\n".join(lines)


def cells():
    """Yield every (scenario, age_group, gender) combination to generate."""
    data = load_all()
    genders = data["personas"]["genders"]
    age_groups = data["personas"]["age_groups"]
    for sc in data["scenarios"]:
        for ag in age_groups:
            for g in genders:
                yield sc, ag, g


def render_user_prompt(scenario: dict, age_group: dict, gender: dict) -> str:
    data = load_all()
    geo = scenario["geometry"]
    filled = data["user_template"].format(
        age_label=age_group["label"],
        age_low=age_group["age_range"][0],
        age_high=age_group["age_range"][1],
        gender_label=gender["label"],
        scenario_name=scenario["name"],
        scenario_description=scenario["description"].strip(),
        sg_variant=scenario.get("sg_variant", "").strip() or "n/a",
        layout=geo["layout"],
        passage_width_m=geo["passage_width_m"],
        agents_involved=scenario["agents_involved"],
        conflict_type=scenario["conflict_type"],
        allowed_actions=allowed_actions_block(scenario, data["action_space"]),
        output_contract=data["output_contract"],
    )
    return filled


def build_messages(scenario: dict, age_group: dict, gender: dict):
    data = load_all()
    return [
        {"role": "system", "content": data["system_prompt"]},
        {"role": "user", "content": render_user_prompt(scenario, age_group, gender)},
    ]
