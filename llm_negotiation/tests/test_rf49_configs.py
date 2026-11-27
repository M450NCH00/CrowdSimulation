"""Issue #138 (RF-49): the configs of round 1 with the menu, in the agent's own frame and in an
absolute frame, and the colour-swapped half of the absolute frame (``resolve_menu_abs_swap_v1``).

The user's decisions of 2026-11-27: RF-47's and RF-48's choices as built, and which colour is on
person 1's left counterbalanced at the same size. The absolute frame is split over two configs,
each with two of RF-40's four repeats (one odd, one even: who is asked first goes by parity) and
the counterfactual pairs. Every session is RF-40's, with the same people; a swapped session's
prompts are RF-48's with "blue" and "yellow" exchanged.
"""

from __future__ import annotations

import json
import re
from dataclasses import replace

import pytest

from negsim.configutil import load_yaml, resolve_path
from negsim.resolution import experiment as E
from negsim.resolution import protocol as P
from negsim.resolution import execute as X
from negsim.resolution.menu import load_menu
from negsim.resolution.prompt import CoreTemplate
from negsim.resolution.view import WALL_A, WALL_B
from test_encounter_protocol import STORE, session_on

RF40 = "configs/resolution/round1_head_on_turn_taking.yaml"
RF47 = "configs/resolution/round1_head_on_menu.yaml"
RF48 = "configs/resolution/round1_head_on_menu_abs.yaml"
OWN = "configs/resolution/rf49_round1_head_on_menu.yaml"
ABS = "configs/resolution/rf49_round1_head_on_menu_abs.yaml"
SWAP = "configs/resolution/rf49_round1_head_on_menu_abs_swap.yaml"
ABS_T = CoreTemplate.load("resolve_menu_abs_v1")
SWAP_T = CoreTemplate.load("resolve_menu_abs_swap_v1")
TURN = P.ProtocolSettings(execution=X.EXECUTION_KEEP_LINE_REPLAN, max_decision_points=6, exchange=P.EXCHANGE_TURN_TAKING)
HEADER = ("template_id", "version", "description", "provenance", "menu_table")


def swap(text: str) -> str:
    """"blue" and "yellow" exchanged, as the template was written."""
    return re.sub(r"\b(blue|yellow)\b", lambda m: "yellow" if m.group(1) == "blue" else "blue", text)


def choose(action):
    return json.dumps({"intent": "Do this.", "action": action, "reason": "r"})


# --- the template and its table ---------------------------------------------------------------------


def test_the_swap_template_is_rf48s_with_blue_and_yellow_exchanged():
    old = {k: v for k, v in ABS_T.data.items() if k not in HEADER}
    new = {k: v for k, v in SWAP_T.data.items() if k not in HEADER}
    assert json.loads(swap(json.dumps(old))) == new
    assert SWAP_T.walls == {WALL_A: "the yellow wall", WALL_B: "the blue wall"}
    assert SWAP_T.data["menu_table"] == "configs/resolution/menu_table_abs_swap_v1.yaml"
    assert SWAP_T.exchange == ABS_T.exchange and SWAP_T.heard_frame == ABS_T.heard_frame


def test_the_swap_table_is_rf48s_with_the_wall_names_exchanged():
    old = load_yaml(resolve_path("configs/resolution/menu_table_abs_v1.yaml"))["options"]
    new = load_yaml(resolve_path("configs/resolution/menu_table_abs_swap_v1.yaml"))["options"]
    assert list(new) == [swap(name) for name in old]
    assert all(new[swap(name)] == plan for name, plan in old.items())
    menu = load_menu("configs/resolution/menu_table_abs_swap_v1.yaml")
    assert menu.by_wall and set(menu.names) == set(load_menu("configs/resolution/menu_table_abs_v1.yaml").names)


@pytest.mark.parametrize("case_id", ["head_on_de176842", "head_on_02dfbadb"])
@pytest.mark.parametrize("condition", ["silent", "talk"])
def test_a_session_under_the_swap_is_rf48s_with_the_two_words_exchanged(case_id, condition):
    # The same physical choice under each naming: person a moves towards the wall at -y (wall b),
    # yellow in RF-48's template and blue in the swap.
    case = STORE.get(case_id, 2)
    a, b = case["agents"]
    runs = {}
    for core, toward_b in ((ABS_T, "step a little towards the yellow wall"), (SWAP_T, "step a little towards the blue wall")):
        runs[core.key] = session_on(
            case, condition, {a: [choose(toward_b)] * 6, b: [choose("carry on")] * 6}, settings=TURN, core=core, first_asked=a,
        )
    (_, old, old_client), (_, new, new_client) = runs["resolve_menu_abs_v1"], runs["resolve_menu_abs_swap_v1"]
    assert old_client.requests and len(old_client.requests) == len(new_client.requests)
    for before, after in zip(old_client.requests, new_client.requests):
        assert [{**m, "content": swap(m["content"])} for m in before.messages] == list(after.messages)
    assert old["outcome"] == new["outcome"]
    # The same plans, carried out the same way: only the words differ.
    keys = ("agent_id", "time_s", "plan_given", "coded", "until_next")
    assert [{k: p[k] for k in keys} for p in old["decision_points"]] == [{k: p[k] for k in keys} for p in new["decision_points"]]
    assert any(p["plan_given"] for p in new["decision_points"])


# --- the configs ---------------------------------------------------------------------------------


def test_rf49s_own_frame_config_is_rf47s_under_its_own_name():
    rf47, own = E.ResolutionConfig.load(RF47), E.ResolutionConfig.load(OWN)
    assert own.experiment_name == "rf49_round1_head_on_menu"
    assert (own.conditions, own.design, own.protocol, own.templates, own.llm, own.resolution_gate) == (
        rf47.conditions, rf47.design, rf47.protocol, rf47.templates, rf47.llm, rf47.resolution_gate)


def test_rf49s_absolute_configs_are_rf48s_split_in_two_by_repeat_with_the_names_swapped_in_one():
    rf48, a, s = (E.ResolutionConfig.load(p) for p in (RF48, ABS, SWAP))
    assert (a.experiment_name, s.experiment_name) == ("rf49_round1_head_on_menu_abs", "rf49_round1_head_on_menu_abs_swap")
    assert rf48.design.repeats == 4 and a.design.repeats == s.design.repeats == 2
    for new in (a, s):
        assert replace(new.design, repeats=4) == rf48.design
        assert (new.conditions, new.protocol, new.llm, new.resolution_gate) == (rf48.conditions, rf48.protocol, rf48.llm, rf48.resolution_gate)
    assert a.templates == rf48.templates and s.templates == {**rf48.templates, "core": "resolve_menu_abs_swap_v1"}


def test_rf49s_caps_sum_to_the_cap_claude_md_records_and_the_client_is_chosen_on_the_command_line():
    # CLAUDE.md, 2026-11-27: USD 2.00 for issue #138, over its three experiments together.
    caps = [load_yaml(resolve_path(path))["budget"]["cap_usd"] for path in (OWN, ABS, SWAP)]
    assert caps == [0.95, 0.525, 0.525] and round(sum(caps), 6) == 2.00
    for path in (OWN, ABS, SWAP):
        raw = load_yaml(resolve_path(path))
        assert raw["llm"]["client"] == "mock" and raw["budget"]["over_cap"] == "stop_at_cap"


def test_every_rf49_session_is_rf40s_with_the_same_people():
    def sessions(path):
        return {s.session_id: s for s in E.plan(E.ResolutionConfig.load(path)).sessions}

    def as_rf40(session_id):  # the swap's r1 and r2 are RF-40's r3 and r4: the same session, the same parity
        return re.sub(r"_r(\d+)$", lambda m: f"_r{int(m.group(1)) + 2}", session_id)

    rf40 = {k: v for k, v in sessions(RF40).items() if v.condition in ("silent", "talk")}
    own, a, s = sessions(OWN), sessions(ABS), sessions(SWAP)
    assert set(own) == set(rf40) and len(own) == 544
    assert set(a) | {as_rf40(k) for k in s} == set(rf40)
    assert len(a) == len(s) == 288 and {k for k in a if "_x" in k} == {k for k in s if "_x" in k}  # the pairs in both
    for mine, to_rf40 in ((own, str), (a, str), (s, as_rf40)):
        for key, session in mine.items():
            theirs = rf40[to_rf40(key)]
            assert dict(session.personas) == dict(theirs.personas) and session.cell == theirs.cell
            assert session.repeat % 2 == theirs.repeat % 2  # who is asked first
