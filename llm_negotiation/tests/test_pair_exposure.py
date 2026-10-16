"""Issue #30, Part 1: pair exposure, the severity tiers, and paired seeds.

Pair exposure is the conflict measure of a pair: whether the two intended velocities put
it inside the bodies' truncated velocity obstacle (``docs/metrics.md``, section 11;
``docs/derivations.md``, section 16). The tests check the geometry against an independent
definition, that the measure reads no directive and in particular no share, that the
tiers come out in their order, and that a baseline run and a rule run with no rule on one
seed are the same run.
"""

from __future__ import annotations

import copy
import csv
import json
import math
import random

import pytest

from helpers import crowd, run_avoidance, static
from negsim.avoidance.directives import AvoidanceDirective
from negsim.avoidance.exposure import obstacle_depth, pair_exposed
from negsim.avoidance.perception import time_to_collision
from negsim.avoidance.simulation import AvoidanceSimulation
from negsim.configutil import ConfigError
from negsim.experiment import AvoidanceExperiment, execute_avoidance_run, run_avoidance_experiment
from negsim.experiment.baselines import load_baseline
from negsim.metrics.avoidance import TIERS, severity_tier
from negsim.runlog.schema import OUTCOME_FILE, PAIR_INTERACTIONS_FILE, TRAJECTORY_FILE, validate_run_dir

GIT = {"commit": "test", "dirty": False}
QUIET = lambda line: None  # noqa: E731
PERTURBED = load_baseline("orca_perturbed_v1")
R, TAU = 0.5, 3.0


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def inside(rel_pos, rel_vel, radius=R, tau=TAU) -> bool:
    """The definition, independently of ORCA's geometry: the bodies touch within tau."""
    ttc = time_to_collision(rel_pos, (-rel_vel[0], -rel_vel[1]), radius)
    return ttc is not None and ttc <= tau


def perturbed(name: str, **overrides):
    """A shipped scenario with the primary baseline laid on it."""
    from negsim.configutil import deep_merge
    from negsim.scenarios.registry import build_crowd_scenario, load_scenario_config

    path = f"configs/scenarios/{name}.yaml"
    config = load_scenario_config(path, deep_merge(PERTURBED.scenario_overrides(load_scenario_config(path)), overrides))
    return build_crowd_scenario(config)


# --- the geometry ------------------------------------------------------------------------------


def test_the_obstacle_depth_matches_hand_computed_cases():
    # Exactly head-on, 10 m apart: on a collision course within 3 s once the closing speed
    # exceeds the gap over tau, (10 - 0.5) / 3; the depth is the excess.
    for closing, depth in ((2.6, 2.6 - 9.5 / 3), (3.2, 3.2 - 9.5 / 3), (0.0, -9.5 / 3)):
        assert obstacle_depth((10.0, 0.0), (closing, 0.0), R, TAU) == pytest.approx(depth, abs=1e-12)
    # Bodies that already touch are inside, however they move.
    assert obstacle_depth((0.3, 0.2), (-5.0, 0.0), R, TAU) == math.inf
    # Two lines 0.6 m apart never meet (0.6 > 0.5); 0.4 m apart they do, unless too far off.
    assert obstacle_depth((5.0, 0.6), (2.6, 0.0), R, TAU) < 0.0
    assert obstacle_depth((5.0, 0.4), (2.6, 0.0), R, TAU) > 0.0
    assert obstacle_depth((10.0, 0.4), (2.6, 0.0), R, TAU) < 0.0  # they would touch after 3.7 s, beyond tau


def test_the_depth_is_the_distance_to_the_boundary_of_the_definition():
    """On random cases, the sign of the depth is the definition's verdict, and its size is
    the smallest change of the relative velocity that changes the verdict."""
    rng = random.Random(30)
    for _ in range(200):
        angle = rng.uniform(-math.pi, math.pi)
        distance = rng.uniform(0.6, 12.0)
        rel_pos = (distance * math.cos(angle), distance * math.sin(angle))
        rel_vel = (rng.uniform(-3.0, 3.0), rng.uniform(-3.0, 3.0))
        depth = obstacle_depth(rel_pos, rel_vel, R, TAU)
        if abs(depth) < 1e-6:
            continue
        assert (depth > 0.0) == inside(rel_pos, rel_vel), (rel_pos, rel_vel, depth)
    # The size, by a search along rays in every direction. A ray from outside can cross the
    # obstacle and leave it again, so each is scanned from its start, not judged by its end.
    for rel_pos, rel_vel in (((6.0, 0.3), (2.6, 0.0)), ((4.0, -1.0), (1.0, 0.1)), ((3.0, 2.0), (0.5, 1.5)), ((8.0, 0.0), (3.5, 0.2))):
        verdict = inside(rel_pos, rel_vel)
        nearest = math.inf
        for k in range(360):
            ux, uy = math.cos(k * math.pi / 180.0), math.sin(k * math.pi / 180.0)
            point = lambda s: (rel_vel[0] + s * ux, rel_vel[1] + s * uy)  # noqa: E731
            step = 0.01
            crossing = next((n * step for n in range(1, 400) if inside(rel_pos, point(n * step)) != verdict), None)
            if crossing is None:
                continue
            low, high = crossing - step, crossing
            for _ in range(40):
                middle = (low + high) / 2.0
                if inside(rel_pos, point(middle)) == verdict:
                    low = middle
                else:
                    high = middle
            nearest = min(nearest, high)
        assert abs(obstacle_depth(rel_pos, rel_vel, R, TAU)) == pytest.approx(nearest, abs=3e-3), (rel_pos, rel_vel)


def test_the_measure_is_symmetric_in_the_two_agents():
    rng = random.Random(31)
    for _ in range(300):
        a, b = (rng.uniform(-6, 6), rng.uniform(-6, 6)), (rng.uniform(-6, 6), rng.uniform(-6, 6))
        va, vb = (rng.uniform(-2, 2), rng.uniform(-2, 2)), (rng.uniform(-2, 2), rng.uniform(-2, 2))
        assert pair_exposed(a, b, va, vb, R, TAU, 1e-3) == pair_exposed(b, a, vb, va, R, TAU, 1e-3)
        p, w = (b[0] - a[0], b[1] - a[1]), (va[0] - vb[0], va[1] - vb[1])
        if p[0] ** 2 + p[1] ** 2 > R * R:
            assert obstacle_depth(p, w, R, TAU) == pytest.approx(obstacle_depth((-p[0], -p[1]), (-w[0], -w[1]), R, TAU), abs=1e-12)


def test_the_shortcut_for_far_pairs_never_changes_the_verdict():
    rng = random.Random(32)
    for _ in range(2000):
        a, b = (0.0, 0.0), (rng.uniform(-14, 14), rng.uniform(-14, 14))
        va, vb = (rng.uniform(-2, 2), rng.uniform(-2, 2)), (rng.uniform(-2, 2), rng.uniform(-2, 2))
        full = obstacle_depth((b[0] - a[0], b[1] - a[1]), (va[0] - vb[0], va[1] - vb[1]), R, TAU) > 1e-3
        assert pair_exposed(a, b, va, vb, R, TAU, 1e-3) == full


def test_the_perturbation_alone_cannot_make_a_step_count():
    """A relative velocity on the boundary, moved by up to 2e-4 m/s, stays below 1e-3."""
    rng = random.Random(33)
    for _ in range(500):
        rel_pos = (rng.uniform(2.0, 12.0), rng.uniform(-0.6, 0.6))
        # A relative velocity just outside the obstacle: grazing the boundary.
        base = (rng.uniform(0.5, 3.0), 0.0)
        while obstacle_depth(rel_pos, base, R, TAU) > 0.0:
            base = (base[0], base[1] + 0.01 * (1 if rel_pos[1] < 0 else -1))
        for _ in range(5):
            angle = rng.uniform(-math.pi, math.pi)
            shift = rng.uniform(0.0, 2e-4)
            moved = (base[0] + shift * math.cos(angle), base[1] + shift * math.sin(angle))
            assert obstacle_depth(rel_pos, moved, R, TAU) < 1e-3


# --- it reads no directive ---------------------------------------------------------------------


def test_one_state_gives_the_same_pair_exposure_under_any_shares():
    spec = crowd("wide_corridor_head_on", geometry={"lateral_offsets": [0.05, -0.05]})
    plain = run_avoidance(spec)
    first = plain.pairs[0].first_pair_exposed_step
    simulation = AvoidanceSimulation(spec)
    while simulation.world.step_index < first:
        simulation.step()
    counted, per_agent = {}, {}
    for shares in ((0.5, 0.5), (1.0, 0.0), (0.0, 1.0), (0.8, 0.2)):
        branch = copy.deepcopy(simulation)
        branch.open[0][1].directive = AvoidanceDirective(responsibility_share=shares[0])
        branch.open[1][0].directive = AvoidanceDirective(responsibility_share=shares[1])
        branch.pair_cache.clear()
        before = (branch.pairs[0].pair_exposure_steps, dict(branch.pairs[0].exposure_steps))
        branch.step()
        counted[shares] = branch.pairs[0].pair_exposure_steps - before[0]
        per_agent[shares] = tuple(branch.pairs[0].exposure_steps.get(agent, 0) - before[1].get(agent, 0) for agent in (0, 1))
    assert set(counted.values()) == {1}  # exposed on that step, under every share
    # The per-agent measure reads the share: the agent with share 0 is not exposed.
    assert per_agent[(0.5, 0.5)] == (1, 1) and per_agent[(1.0, 0.0)] == (1, 0) and per_agent[(0.0, 1.0)] == (0, 1)


def test_a_side_and_shares_leave_the_first_exposed_step_as_it_was():
    spec = perturbed("wide_corridor_head_on")
    rules = static(agent_0={"side_preference": "left", "responsibility_share": 1.0},
                   agent_1={"side_preference": "left", "responsibility_share": 0.0})
    plain = run_avoidance(spec, seed=7, perturbation=PERTURBED.perturbation)
    ruled = run_avoidance(spec, rules, seed=7, perturbation=PERTURBED.perturbation)
    first = plain.pairs[0].first_pair_exposed_step
    assert first is not None and ruled.pairs[0].first_pair_exposed_step == first
    # The two runs are the same run before that step, and start it in the same state with the
    # same intended velocities; on it the side and the shares act for the first time.
    before = lambda result: [row for row in result.trajectory if row["step"] < first]  # noqa: E731
    assert before(plain) == before(ruled)
    state = ("x_m", "y_m", "pref_vx_mps", "pref_vy_mps")
    at = lambda result: [tuple(row[key] for key in state) for row in result.trajectory if row["step"] == first]  # noqa: E731
    assert at(plain) == at(ruled)
    moved = lambda result: [row["vy_mps"] for row in result.trajectory if row["step"] == first]  # noqa: E731
    assert moved(plain) != moved(ruled)
    # A clearance margin acts on every step, not only on a collision course: it changes the tier.
    clear = run_avoidance(spec, static(clearance_margin=0.15), seed=7, perturbation=PERTURBED.perturbation)
    assert (plain.pairs[0].severity_tier, clear.pairs[0].severity_tier) == ("T3", "T1")


def test_pair_exposure_can_be_recomputed_from_the_trajectory_alone(tmp_path):
    """From positions, intended velocities, radii and horizons in the logs, with no directive."""
    for label, directives in (("plain", {}), ("shares", {"provider": "static", "agents": {0: {"responsibility_share": 1.0}, 1: {"responsibility_share": 0.0}}})):
        config = AvoidanceExperiment(
            {
                "layer": "avoidance", "experiment_name": "recompute", "scenario": "configs/scenarios/wide_corridor_head_on.yaml",
                "baseline": "orca_perturbed_v1", "scenario_overrides": {"geometry": {"lateral_offsets": [0.08, -0.08]}},
                "directives": directives, "design": {"seed": 3},
            }
        )
        run_dir = tmp_path / label
        execute_avoidance_run(config.plans()[0], run_dir, GIT)
        scene = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))["scenario"]
        radius = {agent["agent_id"]: agent["radius_m"] for agent in scene["agents"]}
        tau = max(agent["time_horizon_s"] for agent in scene["agents"])
        eps = scene["metrics"]["pair_exposure_eps_mps"]
        (pair,) = read_jsonl(run_dir / PAIR_INTERACTIONS_FILE)
        rows: dict[int, dict[int, dict]] = {}
        with (run_dir / TRAJECTORY_FILE).open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row["pref_vx_mps"] != "":
                    rows.setdefault(int(row["step"]), {})[int(row["agent_id"])] = row
        exposed = borderline = 0
        for step in range(pair["start_step"], pair["end_step"]):
            a, b = rows[step][0], rows[step][1]
            xa, xb = (float(a["x_m"]), float(a["y_m"])), (float(b["x_m"]), float(b["y_m"]))
            va, vb = (float(a["pref_vx_mps"]), float(a["pref_vy_mps"])), (float(b["pref_vx_mps"]), float(b["pref_vy_mps"]))
            exposed += pair_exposed(xa, xb, va, vb, radius[0] + radius[1], tau, eps)
            depth = obstacle_depth((xb[0] - xa[0], xb[1] - xa[1]), (va[0] - vb[0], va[1] - vb[1]), radius[0] + radius[1], tau)
            borderline += abs(depth - eps) < 1e-5  # where the logs' rounding to 1e-6 could flip it
        assert abs(exposed * 0.1 - pair["pair_exposure_time_s"]) <= borderline * 0.1 + 1e-9, label
        assert pair["pair_exposure_time_s"] > 0.0


# --- the tiers ------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "exposure, yields, near, collisions, deadlock, tier",
    [
        (0.0, 0, 0, 0, False, "T0"),
        (0.1, 0, 0, 0, False, "T1"),
        (0.0, 1, 0, 0, False, "T2"),
        (2.0, 1, 0, 0, False, "T2"),
        (0.0, 0, 1, 0, False, "T3"),
        (3.0, 2, 1, 0, False, "T3"),
        (3.0, 2, 1, 1, False, "T4"),
        (0.0, 0, 0, 0, True, "T4"),
    ],
)
def test_the_tier_is_the_highest_that_applies(exposure, yields, near, collisions, deadlock, tier):
    assert severity_tier(exposure, 0.0, yields, near, collisions, deadlock) == tier


def test_the_collision_course_threshold_is_a_setting():
    assert severity_tier(0.3, 0.5, 0, 0, 0, False) == "T0" and severity_tier(0.6, 0.5, 0, 0, 0, False) == "T1"
    spec = perturbed("wide_corridor_head_on", metrics={"collision_course_min_s": 100.0, "near_miss_distance": 0.0})
    (pair,) = run_avoidance(spec, static(clearance_margin=0.15), perturbation=PERTURBED.perturbation).pairs
    assert pair.severity_tier == "T0" and pair.pair_exposure_steps > 0
    assert spec.thresholds.as_dict()["collision_course_min_s"] == 100.0


@pytest.mark.parametrize(
    "scenario, overrides, provider, perturb, tier",
    [
        ("wide_corridor_head_on", {}, None, False, "T4"),  # exactly symmetric, unperturbed: deadlock
        ("wide_corridor_head_on", {}, None, True, "T3"),  # perturbed: they pass, just clear
        ("wide_corridor_head_on", {}, {"clearance_margin": 0.15}, True, "T1"),
        ("wide_corridor_head_on", {"geometry": {"lateral_offsets": [0.3, -0.3]}}, None, True, "T0"),
        ("wide_corridor_head_on", {"geometry": {"lateral_offsets": [0.26, -0.26]}}, None, True, "T3"),  # a near miss with no exposure
    ],
)
def test_each_tier_occurs_where_it_should(scenario, overrides, provider, perturb, tier):
    spec = perturbed(scenario, **overrides) if perturb else crowd(scenario, **overrides)
    result = run_avoidance(
        spec, None if provider is None else static(**provider), seed=4,
        perturbation=PERTURBED.perturbation if perturb else None,
    )
    (pair,) = result.pairs
    assert pair.severity_tier == tier and pair.severity_tier in TIERS
    if tier == "T3" and overrides:
        assert pair.pair_exposure_steps == 0 and pair.tier_detail["near_misses"] == 1


def test_the_outcome_counts_the_tiers_and_the_logs_check_out(tmp_path):
    config = AvoidanceExperiment(
        {"layer": "avoidance", "experiment_name": "tiers", "scenario": "configs/scenarios/wide_corridor_head_on.yaml",
         "baseline": "orca_perturbed_v1", "design": {"seed": 1}}
    )
    outcome = execute_avoidance_run(config.plans()[0], tmp_path / "run", GIT)
    assert outcome["interaction_outcomes"]["tiers"] == {"T0": 0, "T1": 0, "T2": 0, "T3": 1, "T4": 0}
    assert outcome["totals"]["pair_exposure_time_s"] > 0 and outcome["thresholds"]["pair_exposure_eps_mps"] == 1e-3
    (pair,) = read_jsonl(tmp_path / "run" / PAIR_INTERACTIONS_FILE)
    assert pair["severity_tier"] == "T3" and pair["outcome"] == "resolved" and pair["outcome_detail"]["pair_exposed"]
    assert validate_run_dir(tmp_path / "run") == []
    damaged = tmp_path / "damaged"
    import shutil

    shutil.copytree(tmp_path / "run", damaged)
    pair["severity_tier"] = "T9"
    (damaged / PAIR_INTERACTIONS_FILE).write_text(json.dumps(pair) + "\n", encoding="utf-8")
    assert any("severity_tier" in problem for problem in validate_run_dir(damaged))


# --- paired seeds (Part 1.2) ----------------------------------------------------------------------


def two_modes(seeding: str, repeats: int = 2) -> AvoidanceExperiment:
    return AvoidanceExperiment(
        {
            "layer": "avoidance", "experiment_name": f"paired_{seeding}",
            "scenario": "configs/scenarios/wide_corridor_head_on.yaml", "baseline": "orca_perturbed_v1",
            "design": {
                "seed": 3000, "repeats": repeats, "seeding": seeding,
                "factors": {"mode": [{"name": "plain"}, {"name": "no_rule", "directives": {"provider": "rules"}}]},
            },
        }
    )


def test_paired_seeds_are_the_base_seed_plus_the_repeat_for_every_level():
    paired, per_run = two_modes("paired").plans(), two_modes("per_run").plans()
    assert [(plan.run_id, plan.seed) for plan in paired] == [
        ("001_plain_r1", 3001), ("002_plain_r2", 3002), ("003_no_rule_r1", 3001), ("004_no_rule_r2", 3002),
    ]
    assert [plan.seed for plan in per_run] == [3001, 3002, 3003, 3004]
    assert {plan.seeding for plan in paired} == {"paired"} and {plan.seeding for plan in per_run} == {"per_run"}
    with pytest.raises(ConfigError, match="seeding"):
        AvoidanceExperiment({"layer": "avoidance", "experiment_name": "x", "scenario": "configs/scenarios/wide_corridor_head_on.yaml", "design": {"seeding": "random"}})


def test_a_rule_run_with_no_rule_writes_the_baseline_trajectory(tmp_path):
    result = run_avoidance_experiment(two_modes("paired", repeats=1), out_root=tmp_path, report=QUIET, git=GIT)
    plain, no_rule = (result.experiment_dir / run_id for run_id in result.executed)
    assert (plain / TRAJECTORY_FILE).read_bytes() == (no_rule / TRAJECTORY_FILE).read_bytes()
    first, second = (json.loads((folder / OUTCOME_FILE).read_text(encoding="utf-8")) for folder in (plain, no_rule))
    assert first["interaction_outcomes"]["tiers"] == second["interaction_outcomes"]["tiers"]
    assert json.loads((no_rule / "config.json").read_text(encoding="utf-8"))["directives"]["rules"] == []
    # Seeded per run, the same two levels draw different perturbations and are not the same run.
    result = run_avoidance_experiment(two_modes("per_run", repeats=1), out_root=tmp_path, report=QUIET, git=GIT)
    plain, no_rule = (result.experiment_dir / run_id for run_id in result.executed)
    assert (plain / TRAJECTORY_FILE).read_bytes() != (no_rule / TRAJECTORY_FILE).read_bytes()


def test_the_committed_experiments_are_pinned_to_their_own_seeds():
    from negsim.configutil import PACKAGE_ROOT, load_yaml

    for folder in ("avoidance", "rule_following"):
        for path in sorted((PACKAGE_ROOT / "configs" / folder).glob("*.yaml")):
            assert load_yaml(path)["design"]["seeding"] == "per_run", path.name
