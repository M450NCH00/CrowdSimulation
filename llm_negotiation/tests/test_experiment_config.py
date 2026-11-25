"""Experiment configs: the shipped ones, design expansion, counterbalancing, and guardrails."""

from __future__ import annotations

import copy
from collections import Counter
from pathlib import Path

import pytest

from helpers import c1_config, c2_config, experiment
from negsim.configutil import PACKAGE_ROOT, ConfigError
from negsim.experiment import ExperimentConfig

CONFIG_DIR = PACKAGE_ROOT / "configs" / "experiments"
SHIPPED = sorted(path.name for path in CONFIG_DIR.glob("*.yaml"))
PAIRS = [
    [{"task_type": "hospital"}, {"task_type": "airport"}],
    [{"task_type": "hospital"}, {"task_type": "grocery"}],
    [{"task_type": "airport"}, {"task_type": "grocery"}],
]


def factorial(**design) -> dict:
    return c1_config(design={"mode": "factorial", "seed": 10, "pairs": PAIRS, **design})


def types(plan) -> tuple[str, str]:
    return tuple(participant.task_type for participant in plan.participants)


# --- the shipped configs -----------------------------------------------------------------------


def test_the_configs_named_in_the_issue_exist():
    assert {"c0_no_llm.yaml", "c1_gamechat_replication.yaml", "c2_task_plus_persona.yaml"} <= set(SHIPPED)


@pytest.mark.parametrize("name", SHIPPED)
def test_every_shipped_config_loads_and_defaults_to_the_free_client(name):
    config = ExperimentConfig.load(CONFIG_DIR / name)
    assert config.plans()
    assert config.llm["client"] == "mock"  # paying is always an explicit --client deepseek
    assert config.budget["cap_usd"] == 0.50


def test_all_five_conditions_are_covered_by_a_shipped_config():
    conditions = {ExperimentConfig.load(CONFIG_DIR / name).condition for name in SHIPPED}
    assert conditions == {"C0", "C1", "C2", "C3", "C4"}


@pytest.mark.parametrize(
    "name, runs",
    [
        ("c0_no_llm.yaml", 18),  # "We created 18 versions of each scenario" (Sec V-A)
        ("c0_no_llm_intersection.yaml", 18),
        ("c0_no_llm_hallway.yaml", 18),
        ("c1_gamechat_replication.yaml", 36),
        ("c1_smoke.yaml", 6),
        ("c2_smoke.yaml", 6),
    ],
)
def test_design_sizes(name, runs):
    assert len(ExperimentConfig.load(CONFIG_DIR / name).plans()) == runs


def test_c1_smoke_covers_every_ordered_pair_and_balances_speaking_order_and_index():
    plans = ExperimentConfig.load(CONFIG_DIR / "c1_smoke.yaml").plans()
    order = ["hospital", "airport", "grocery"]
    assert sorted(types(plan) for plan in plans) == sorted((a, b) for a in order for b in order if a != b)
    higher_speaks_first, higher_is_agent_0 = Counter(), 0
    for plan in plans:
        higher = min((0, 1), key=lambda agent: order.index(types(plan)[agent]))
        higher_speaks_first[(frozenset(types(plan)), plan.first_speaker == higher)] += 1
        higher_is_agent_0 += higher == 0
    assert all(count == 1 for count in higher_speaks_first.values()) and len(higher_speaks_first) == 6
    assert higher_is_agent_0 == 3
    assert all(plan.info_fields == () for plan in plans)  # GameChat: a task and nothing else


def test_c2_smoke_pairs_differ_in_age_and_gender_and_swap_roles_between_runs():
    plans = ExperimentConfig.load(CONFIG_DIR / "c2_smoke.yaml").plans()
    for plan in plans:
        a, b = (participant.persona for participant in plan.participants)
        assert a.age != b.age and a.gender != b.gender
    for first, second in zip(plans[0::2], plans[1::2]):
        ids = lambda plan: [participant.persona.persona_id for participant in plan.participants]
        assert ids(first) == ids(second)[::-1]  # same two people, agent index and side swapped
        speaker = lambda plan: plan.participants[plan.first_speaker].persona.persona_id
        assert speaker(first) != speaker(second)  # and the other one speaks first
    assert all(plan.scoring["ground_truth"] is None for plan in plans)


def test_c3_configs_vary_exactly_one_attribute():
    for name, varied, fixed in (("c3_age_only.yaml", "age", "gender"), ("c3_gender_only.yaml", "gender", "age")):
        for plan in ExperimentConfig.load(CONFIG_DIR / name).plans():
            a, b = (participant.persona for participant in plan.participants)
            assert a.attributes[varied] != b.attributes[varied]
            assert a.attributes[fixed] == b.attributes[fixed]
            assert a.task == b.task and a.backstory == b.backstory


def test_c4_crosses_the_same_runs_with_each_information_setting():
    plans = ExperimentConfig.load(CONFIG_DIR / "c4_info_ablation.yaml").plans()
    by_variant = Counter(plan.info_variant for plan in plans)
    assert by_variant == {"info_all": 4, "info_none": 4, "info_no_other": 4}
    assert {len(plan.info_fields) for plan in plans if plan.info_variant == "info_none"} == {0}
    assert all(not field.startswith("other_") for plan in plans if plan.info_variant == "info_no_other" for field in plan.info_fields)


# --- design expansion and counterbalancing -----------------------------------------------------


def test_factorial_default_is_one_run_per_pair():
    plans = experiment(factorial()).plans()
    assert [types(plan) for plan in plans] == [("hospital", "airport"), ("hospital", "grocery"), ("airport", "grocery")]
    assert all(plan.first_speaker == 0 and not plan.swap_sides for plan in plans)


def test_counterbalancing_speaking_order_doubles_the_runs():
    plans = experiment(factorial(first_speaker="counterbalance")).plans()
    assert len(plans) == 6
    assert Counter(plan.first_speaker for plan in plans) == {0: 3, 1: 3}


def test_counterbalancing_agent_index_puts_each_participant_in_each_slot():
    plans = experiment(factorial(assignment="counterbalance")).plans()
    assert Counter(types(plan) for plan in plans) == Counter(
        [(a, b) for a, b in (("hospital", "airport"), ("hospital", "grocery"), ("airport", "grocery"))]
        + [(b, a) for a, b in (("hospital", "airport"), ("hospital", "grocery"), ("airport", "grocery"))]
    )


def test_counterbalancing_sides_swaps_where_agent_0_starts():
    plans = experiment(factorial(sides="counterbalance")).plans()
    assert Counter(plan.swap_sides for plan in plans) == {False: 3, True: 3}
    assert all(plan.scenario_config["swap_sides"] == plan.swap_sides for plan in plans)


def test_all_factors_cross_fully():
    design = dict(
        assignment="counterbalance", sides="counterbalance", first_speaker="counterbalance", repeats=2,
        scenario_variants=[{"name": "near", "overrides": {}}, {"name": "far", "overrides": {"start_offsets": [0.25, 0]}}],
        info_variants=[{"name": "on", "info_fields": "all"}, {"name": "off", "info_fields": "none"}],
    )
    plans = experiment(factorial(**design)).plans()
    assert len(plans) == 3 * 2 * 2 * 2 * 2 * 2 * 2
    cells = Counter(
        (types(plan), plan.scenario_variant, plan.info_variant, plan.swap_sides, plan.first_speaker, plan.repeat)
        for plan in plans
    )
    assert set(cells.values()) == {1}
    assert len({plan.run_id for plan in plans}) == len(plans)
    assert [plan.index for plan in plans] == list(range(1, len(plans) + 1))


def test_every_run_records_its_own_seed_and_repeats_differ_only_in_seed():
    plans = experiment(factorial(repeats=3)).plans()
    assert [plan.seed for plan in plans] == [10 + plan.index for plan in plans]
    assert len({plan.seed for plan in plans}) == 9
    assert [plan.repeat for plan in plans[:3]] == [1, 2, 3]


def test_task_strings_are_drawn_from_the_papers_table_and_reproducibly():
    config = factorial(repeats=5)
    first, second = experiment(config).plans(), experiment(config).plans()
    assert [p.participants[0].task for p in first] == [p.participants[0].task for p in second]
    table = experiment(config).tasks
    assert table.priority_order == ("hospital", "airport", "grocery")
    assert set(table.task_strings["hospital"]) == {"the hospital", "the emergency room", "the operating room", "the ER", "get surgery"}
    assert all(len(strings) == 5 for strings in table.task_strings.values())
    for plan in first:
        for participant in plan.participants:
            assert participant.task in table.task_strings[participant.task_type]
    assert len({plan.participants[0].task for plan in first}) > 1  # different seeds, different strings


def test_scenario_overrides_reach_the_run_and_variants_stack_on_top():
    config = factorial(scenario_variants=[{"name": "back", "overrides": {"start_offsets": [0.25, 0.0]}}])
    config["scenario_overrides"] = {"conflict": {"zone_half_length": 0.25}}
    plan = experiment(config).plans()[0]
    assert plan.scenario_config["conflict"]["zone_half_length"] == 0.25
    assert plan.scenario_config["conflict"]["predictor"] == "heading_ray"  # merged, not replaced
    assert plan.scenario_config["start_offsets"] == [0.25, 0.0]


def test_persona_runs_can_override_single_attributes_and_tag_a_task_type():
    config = c2_config()
    config["design"]["runs"] = [
        {"agents": [{"persona": "f25", "age": 70}, {"persona": "m25", "task": "the clinic", "task_type": "hospital"}], "first_speaker": 1}
    ]
    plan = experiment(config).plans()[0]
    older, tagged = plan.participants
    assert (older.persona.age, older.persona.gender, older.persona.persona_id) == (70, "female", "f25+age=70")
    assert (tagged.task, tagged.task_type, tagged.persona.persona_id) == ("the clinic", "hospital", "m25")
    assert plan.run_id == "001_f25+age70-vs-m25+hospital_fs1"


def test_a_persona_can_take_its_task_from_a_task_type():
    config = c2_config()
    config["design"]["runs"] = [{"agents": [{"persona": "f25", "task_type": "airport"}, {"persona": "m70"}]}]
    traveller, shopper = experiment(config).plans()[0].participants
    assert traveller.task in experiment(config).tasks.task_strings["airport"] and traveller.persona.task == traveller.task
    assert shopper.task == "the supermarket to buy groceries" and shopper.task_type is None


# --- guardrails ----------------------------------------------------------------------------------


def test_only_task_only_conditions_can_be_scored_against_ground_truth():
    with pytest.raises(ConfigError, match="Only C0 and C1 are scored"):
        experiment(c2_config(scoring={"ground_truth": "task_priority"}))
    scored_persona = c1_config(personas="configs/personas/personas.yaml")
    scored_persona["design"]["runs"][0]["agents"][0] = {"persona": "f70", "task_type": "hospital"}
    scored_persona["negotiation"]["template"] = "persona_v1"
    with pytest.raises(ConfigError, match="a participant has a persona"):
        experiment(scored_persona)


def test_ground_truth_needs_two_different_task_types():
    same = c1_config()
    same["design"]["runs"][0]["agents"] = [{"task_type": "airport"}, {"task_type": "airport"}]
    with pytest.raises(ConfigError, match="no higher-priority agent"):
        experiment(same)
    same["scoring"] = {}
    assert experiment(same).plans()[0].scoring["ground_truth"] is None  # allowed, just not scored


def test_c0_means_no_negotiation_and_the_other_conditions_mean_negotiation():
    with pytest.raises(ConfigError, match="condition C0"):
        experiment(c1_config(condition="C0"))
    with pytest.raises(ConfigError, match="condition C0"):
        experiment(c1_config(negotiation={"enabled": False}))
    c0 = experiment(c1_config(condition="C0", negotiation={"enabled": False}))
    assert c0.plans()[0].first_speaker is None


def test_persona_template_needs_personas_and_task_only_agents_cannot_carry_persona_fields():
    no_persona = c2_config()
    no_persona["design"]["runs"][0]["agents"][0] = {"task_type": "hospital"}
    with pytest.raises(ConfigError, match="needs a persona for every participant"):
        experiment(no_persona)
    stray = c1_config()
    stray["design"]["runs"][0]["agents"][0] = {"task_type": "hospital", "age": 70}
    with pytest.raises(ConfigError, match="can only be set on a persona"):
        experiment(stray)


@pytest.mark.parametrize(
    "mutate, message",
    [
        (lambda c: c.update(experiment_name="has spaces"), "letters, digits"),
        (lambda c: c.update(condition="C9"), "condition"),
        (lambda c: c.update(colour="blue"), "unknown key"),
        (lambda c: c.pop("design"), "missing required key"),
        (lambda c: c["negotiation"].update(template="persona_v7"), "unknown prompt template"),
        (lambda c: c["negotiation"].update(template=None), "needed when negotiation is enabled"),
        (lambda c: c["negotiation"].update(timing={"mode": "telepathic"}), "timing.mode"),
        (lambda c: c["negotiation"].update(info_fields=["other_max_speed"]), "unknown field"),
        (lambda c: c["negotiation"].update(visibility={"aura": True}), "unknown attribute"),
        (lambda c: c["negotiation"].update(max_messages_per_agent=0), "max_messages_per_agent"),
        (lambda c: c["llm"].update(client="openai"), "client"),
        (lambda c: c["llm"].update(temperature=-1), "temperature"),
        (lambda c: c["llm"].update(thinking="maybe"), "thinking"),
        (lambda c: c.update(arbitration={"tie_break": "seniority"}), "tie_break"),
        (lambda c: c.update(budget={"cap_usd": -1}), "cap_usd"),
        (lambda c: c["design"].update(mode="latin_square"), "mode"),
        (lambda c: c["design"].update(runs=[]), "non-empty list"),
        (lambda c: c["design"]["runs"][0].update(first_speaker=2), "first_speaker"),
        (lambda c: c["design"]["runs"][0].update(agents=[{"task_type": "hospital"}]), "exactly two"),
        (lambda c: c["design"]["runs"][0].update(agents=[{"task_type": "hospital"}, {"task_type": "spa"}]), "unknown task_type"),
        (lambda c: c["design"]["runs"][0].update(agents=[{"task_type": "hospital"}, {}]), "give a 'persona' or a 'task_type'"),
        (lambda c: c["design"]["runs"][0].update(scenario_overrides={"dt": -1}), "dt"),
        (lambda c: c.update(scenario="configs/scenarios/nowhere.yaml"), "not found"),
    ],
)
def test_bad_experiment_configs_fail_before_anything_runs(mutate, message):
    config = copy.deepcopy(c1_config())
    config.setdefault("llm", {})
    mutate(config)
    with pytest.raises(ConfigError, match=message):
        experiment(config)


def test_unknown_persona_and_missing_personas_file():
    config = c2_config()
    config["design"]["runs"][0]["agents"][0] = {"persona": "nobody"}
    with pytest.raises(ConfigError, match="unknown persona 'nobody'"):
        experiment(config)
    config = c2_config()
    del config["personas"]
    with pytest.raises(ConfigError, match="no 'personas' file"):
        experiment(config)


def test_config_paths_resolve_from_the_package_folder_whatever_the_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert len(ExperimentConfig.load("configs/experiments/c1_smoke.yaml").plans()) == 6
    assert len(ExperimentConfig.load(Path(CONFIG_DIR / "c1_smoke.yaml")).plans()) == 6
