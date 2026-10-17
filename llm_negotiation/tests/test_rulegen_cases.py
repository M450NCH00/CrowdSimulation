"""Issue #30, Part 2: conflict cases taken from baseline runs, and the frozen case store."""

from __future__ import annotations

import io
import json
import shutil

import pytest

from negsim.avoidance.simulation import AvoidanceSimulation
from negsim.configutil import PACKAGE_ROOT
from negsim.experiment import AvoidanceExperiment, run_avoidance_experiment
from negsim.rules.snapshot import snapshot_of_pair
from negsim.rulegen.cases import (
    CASES_ROOT,
    REASON_BASELINE,
    REASON_FORMATION_CLASS,
    REASON_ONE_SIDED,
    REASON_PROVIDER,
    REASON_TIER,
    CaseError,
    CaseStore,
    ExtractionConfig,
    case_id_for,
    case_json,
    extract,
    main,
    restep_case,
)
from negsim.scenarios.registry import build_crowd_scenario

GIT = {"commit": "test", "dirty": False}
QUIET = lambda line: None  # noqa: E731


def source(name: str, scenario: str, factors=None, **extra) -> AvoidanceExperiment:
    raw = {
        "layer": "avoidance", "experiment_name": name, "scenario": f"configs/scenarios/{scenario}.yaml",
        "baseline": "orca_perturbed_v1", "design": {"seed": 40, "factors": factors or {}},
    }
    raw.update(extra)
    return AvoidanceExperiment(raw)


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    """Small baseline runs: a head-on that conflicts and one that does not, a crowd in which
    some pairs form one-sided, and runs that are not eligible as a whole."""
    root = tmp_path_factory.mktemp("runs")
    layouts = [{"name": "aligned"}, {"name": "apart_60cm", "scenario_overrides": {"geometry": {"lateral_offsets": [0.3, -0.3]}}}]
    run_avoidance_experiment(source("src_head_on", "wide_corridor_head_on", {"layout": layouts}), out_root=root, report=QUIET, git=GIT)
    crowd = {"geometry": {"agents_per_direction": 8, "length": 20.0}, "agent_types": {"pedestrian": {"max_neighbours": 2}}}
    run_avoidance_experiment(source("src_flow", "bidirectional_flow", scenario_overrides=crowd), out_root=root, report=QUIET, git=GIT)
    run_avoidance_experiment(
        source("src_other", "wide_corridor_head_on", baseline="orca_unperturbed_v1",
               design={"seed": 1, "factors": {"mode": [{"name": "static", "directives": {"provider": "static", "default": {"clearance_margin": 0.1}}}]}}),
        out_root=root, report=QUIET, git=GIT,
    )
    return root


def config_for(tmp_path, runs, *, sources=("src_head_on", "src_flow"), per_stratum=1, seed=3, by=("scenario", "variant", "tier"), name="test_set", formation=None):
    path = tmp_path / f"{name}.yaml"
    classes = "" if formation is None else f", formation_classes: [{', '.join(formation)}]"
    lines = [
        "schema_version: 1", f"case_set: {name}", "sources:",
        *[f"  - {(runs / source).as_posix()}" for source in sources],
        f"eligibility: {{baseline: orca_perturbed_v1, min_tier: T1{classes}}}",
        f"strata: {{by: [{', '.join(by)}], per_stratum: {per_stratum}, seed: {seed}}}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ExtractionConfig.load(path)


def test_a_case_holds_what_the_two_agents_saw_when_the_pair_formed(tmp_path, runs):
    store = CaseStore(tmp_path / "cases")
    report = extract(config_for(tmp_path, runs, sources=("src_head_on",)), store)
    (case_id,) = report.selected  # the aligned head-on is T3; 60 cm apart they never conflict (T0)
    case = store.get(case_id)
    assert case["case_id"] == case_id == case_id_for("wide_corridor_head_on", "src_head_on", "001_aligned", 0)
    assert case["scenario"]["type"] == "wide_corridor_head_on" and case["scenario"]["variant"] == {"layout": "aligned"}
    assert case["source"]["run_id"] == "001_aligned" and case["source"]["baseline"]["name"] == "orca_perturbed_v1"
    assert case["agents"] == [0, 1] and case["formation"]["encounter_class"] == "head_on"
    assert case["private"] == {"0": {"task": None}, "1": {"task": None}}  # filled by a session, never here
    assert case["severity_tier"] == "T3" and case["baseline_outcome"]["category"] == "resolved"
    for agent, other in ((0, 1), (1, 0)):
        record = case["observations"][str(agent)]
        assert (record["observer_id"], record["neighbour_id"], record["step"]) == (agent, other, case["formation"]["step"])
    # The snapshot is the one the run loop would have evaluated rules on at that step.
    plan = source("src_head_on", "wide_corridor_head_on").plans()[0]
    spec = build_crowd_scenario(plan.scenario_config)
    simulation = AvoidanceSimulation(spec, seed=plan.seed, perturbation=plan.perturbation, visibility=plan.visibility)
    while simulation.world.step_index < case["formation"]["step"]:
        simulation.step()
    a, b = simulation.world.agents
    live = snapshot_of_pair(simulation.world.step_index, simulation.world.time, a, b, simulation.pair_features(0, 1), plan.visibility, {}).as_dict()
    assert case["snapshot"] == live


def test_eligibility_tier_one_sided_formation_baseline_and_provider(tmp_path, runs):
    report = extract(config_for(tmp_path, runs, sources=("src_head_on", "src_flow", "src_other")), CaseStore(tmp_path / "cases"), write=False)
    by_run = {source.run: source for source in report.sources}
    assert by_run["src_head_on/002_apart_60cm"].excluded == {REASON_TIER: 1} and by_run["src_head_on/002_apart_60cm"].eligible == 0
    flow = by_run["src_flow/001_base"]
    assert flow.excluded[REASON_ONE_SIDED] > 0 and flow.eligible > 0  # with two neighbours, many pairs form one-sided
    assert flow.pairs == flow.eligible + sum(flow.excluded.values())
    assert by_run["src_other/001_static"].run_excluded in (REASON_BASELINE, REASON_PROVIDER)
    # Pairs not approaching each other when they formed (neighbours side by side at the start
    # of the flow) can be left out.
    approaching = extract(
        config_for(tmp_path, runs, sources=("src_flow",), formation=("head_on", "crossing", "overtaking")),
        CaseStore(tmp_path / "cases"), write=False,
    )
    (flow_only,) = approaching.sources
    assert flow_only.excluded[REASON_FORMATION_CLASS] > 0 and flow_only.eligible < flow.eligible


def test_sampling_is_stratified_seeded_and_each_stratum_draws_on_its_own(tmp_path, runs):
    first = extract(config_for(tmp_path, runs, per_stratum=2, seed=3), CaseStore(tmp_path / "a"), write=False)
    again = extract(config_for(tmp_path, runs, per_stratum=2, seed=3), CaseStore(tmp_path / "b"), write=False)
    assert first.selected == again.selected and first.strata == again.strata
    for row in first.strata:
        assert len(row["selected"]) == min(2, row["eligible"])
    assert {row["stratum"]["tier"] for row in first.strata} >= {"T3"}
    other = extract(config_for(tmp_path, runs, per_stratum=2, seed=4), CaseStore(tmp_path / "c"), write=False)
    flow = lambda report: [row["selected"] for row in report.strata if row["stratum"]["scenario"] == "bidirectional_flow" and row["eligible"] > 2]  # noqa: E731
    assert flow(other) != flow(first)  # another seed draws another sample
    # Without the head-on runs, the flow's strata draw exactly the same cases.
    alone = extract(config_for(tmp_path, runs, sources=("src_flow",), per_stratum=2, seed=3), CaseStore(tmp_path / "d"), write=False)
    assert flow(alone) == flow(first)


def test_cases_are_frozen_ids_are_stable_and_extraction_is_repeatable(tmp_path, runs):
    store = CaseStore(tmp_path / "cases")
    first = extract(config_for(tmp_path, runs), store)
    assert first.written and store.check() == []
    again = extract(config_for(tmp_path, runs), store)
    assert again.written == [] and again.selected == first.selected  # the same cases, file for file
    name = first.written[0]
    path = store.root / name
    case = json.loads(path.read_text(encoding="utf-8"))
    case["severity_tier"] = "T0"
    with pytest.raises(CaseError, match="never an edit"):
        store.add(case)
    path.write_text(case_json(case), encoding="utf-8")
    assert any("not the version frozen" in problem for problem in store.check())
    with pytest.raises(CaseError, match="does not match its manifest"):
        store.get(case["case_id"])


def test_a_case_set_is_recorded_once(tmp_path, runs):
    store = CaseStore(tmp_path / "cases")
    extract(config_for(tmp_path, runs), store)
    manifest = store.manifest()
    entry = manifest["case_sets"]["test_set"]
    assert entry["cases"] == sorted(entry["cases"]) and (store.root / entry["extraction"]).is_file()
    assert [f"{case_id}@{version}" for case_id, version in store.case_set("test_set")] == entry["cases"]
    with pytest.raises(CaseError, match="other contents"):
        extract(config_for(tmp_path, runs, per_stratum=2), store)  # another selection under the same name


@pytest.mark.parametrize(
    "lines, message",
    [
        (["case_set: xy", "sources: []", "strata: {by: [tier], per_stratum: 1, seed: 1}"], "sources"),
        (["case_set: xy", "sources: [runs/x]", "strata: {by: [colour], per_stratum: 1, seed: 1}"], "strata.by"),
        (["case_set: xy", "sources: [runs/x]", "eligibility: {min_tier: T7}", "strata: {by: [tier], per_stratum: 1, seed: 1}"], "min_tier"),
        (["case_set: X Y", "sources: [runs/x]", "strata: {by: [tier], per_stratum: 1, seed: 1}"], "case_set"),
    ],
)
def test_a_bad_extraction_config_is_refused(tmp_path, lines, message):
    path = tmp_path / "bad.yaml"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(Exception, match=message):
        ExtractionConfig.load(path)


# --- the committed store ---------------------------------------------------------------------------


def test_the_committed_case_store_matches_its_manifest_and_its_source_runs():
    store = CaseStore(CASES_ROOT)
    assert store.check() == []
    cases = store.case_set("si3_v1")
    assert len(cases) == 18
    scenarios = set()
    for case_id, version in cases:
        case = store.get(case_id, version)
        scenarios.add(case["scenario"]["type"])
        assert case["severity_tier"] in ("T1", "T2", "T3", "T4") and case["source"]["baseline"]["name"] == "orca_perturbed_v1"
        run_dir = PACKAGE_ROOT / "runs" / case["source"]["experiment"] / case["source"]["run_id"]
        config = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
        assert config["seed"] == case["source"]["seed"] and config["git"]["dirty"] is False
        pairs = [json.loads(line) for line in (run_dir / "pair_interactions.jsonl").read_text(encoding="utf-8").splitlines()]
        assert pairs[case["source"]["pair_id"]]["agents"] == case["agents"]
        assert pairs[case["source"]["pair_id"]]["severity_tier"] == case["severity_tier"]
    assert scenarios == {"wide_corridor_head_on", "open_crossing", "overtaking", "corridor_to_bottleneck", "bidirectional_flow"}


def test_extracting_again_from_issue_30s_runs_gives_the_committed_files(tmp_path):
    """Issue #32 raised the case format to 2 for what it adds; a case that holds none of it (its
    records are of perception version 2) is written as version 1, as before."""
    report = extract(ExtractionConfig.load(PACKAGE_ROOT / "configs" / "cases" / "si3_cases_v1.yaml"), CaseStore(tmp_path))
    assert len(report.written) == 18
    for name in report.written:
        assert (tmp_path / name).read_text(encoding="utf-8") == (CASES_ROOT / name).read_text(encoding="utf-8"), name
    assert CaseStore(tmp_path).manifest()["case_format_version"] == 1


def test_a_case_from_a_run_of_log_schema_5_is_of_format_2_and_says_who_came_out_first(tmp_path, runs):
    store = CaseStore(tmp_path / "cases")
    (case_id,) = extract(config_for(tmp_path, runs, sources=("src_head_on",)), store).selected
    case = store.get(case_id)
    assert case["case_format_version"] == 2 and case["observations"]["0"]["schema_version"] == 3
    assert case["baseline_outcome"]["first_out"] is None  # no single-file segment in a head-on corridor
    assert "derived_from" not in case and store.manifest()["case_format_version"] == 2


def test_a_case_gets_a_next_version_with_newer_records_by_re_stepping_its_source_run():
    """Issue #32: version 2 of a case holds perception records of version 3, made by running its
    source run again to the step its pair formed; every field of version 1 must come out equal."""
    case = CaseStore(CASES_ROOT).get("head_on_de176842", 1)
    newer = restep_case(case, GIT)
    assert (newer["case_id"], newer["version"], newer["case_format_version"]) == ("head_on_de176842", 2, 2)
    assert newer["derived_from"]["case"] == "head_on_de176842@1" and newer["derived_from"]["method"] == "re-stepped"
    assert (newer["derived_from"]["perception_schema_version"], newer["derived_from"]["git_commit"]) == (3, "test")
    for agent in ("0", "1"):
        old, new = case["observations"][agent], newer["observations"][agent]
        assert (old["schema_version"], new["schema_version"]) == (2, 3)
        for key, value in old.items():  # what version 1 held, version 2 holds the same; the rest it adds
            if key != "schema_version":
                assert ({name: new[key][name] for name in value} if isinstance(value, dict) else new[key]) == value, key
        assert set(new["observer"]) - set(old["observer"]) == {"in_segment", "segment_distance_travelled", "segment_distance_ahead", "segment_distance_behind"}
        assert new["observer"]["in_segment"] is None and new["neighbour_in_segment"] is None  # a head-on meeting has no passage
    added = set(newer["snapshot"]["agent"]["0"]) - set(case["snapshot"]["agent"]["0"])
    assert added == {"in_segment", "segment_distance_travelled", "segment_distance_ahead", "segment_distance_behind"}
    for key in ("scenario", "source", "agents", "formation", "bodies", "private", "severity_tier", "baseline_outcome"):
        assert newer[key] == case[key], key
    tampered = json.loads(json.dumps(case))
    tampered["observations"]["0"]["distance_m"] += 0.5
    with pytest.raises(CaseError, match=r"observations\.0\.distance_m"):
        restep_case(tampered, GIT)


def test_the_command_line_lists_shows_and_checks(tmp_path):
    out = io.StringIO()
    assert main(["list", "--set", "si3_v1"], out=out) == 0 and "head_on_" in out.getvalue()
    out = io.StringIO()
    assert main(["check"], out=out) == 0 and "matches its manifest" in out.getvalue()
    out = io.StringIO()
    case_id = CaseStore(CASES_ROOT).case_set("si3_v1")[0][0]
    assert main(["show", case_id], out=out) == 0 and json.loads(out.getvalue())["case_id"] == case_id
    broken = tmp_path / "cases"
    shutil.copytree(CASES_ROOT, broken)
    (broken / "stray.v1.json").write_text("{}\n", encoding="utf-8")
    out = io.StringIO()
    assert main(["--store", str(broken), "check"], out=out) == 1 and "not in MANIFEST.json" in out.getvalue()
