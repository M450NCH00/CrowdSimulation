"""Round 1 against the human targets: rule arms, plain ORCA and Step 1's agents (issue #122, RF-37).

    python -m negsim.human_targets.report               # writes runs/rf37_human_targets/{summary.json,report.md}
    python -m negsim.human_targets.report --study rf38  # writes runs/rf38_human_targets/ (issue #124)

Reads finished runs only; no simulation is run and no model is called. The subjects:

* **Plain ORCA and each rule arm**, from the rule-set evaluations ``rf37_head_on`` (head-on pairs in
  Moussaid2009's corridor at 1.3 m/s, and at Huber2014's three speeds for H3) and, for the crowd
  targets, RF-33's ``flow_realistic`` (50 + 50) with ``rf37_flow_density``'s 15 + 15 and 75 + 75.
* **Step 1's agents**, each condition its own subject: the sessions of RF-10 (independent) and RF-30
  (non-verbal, talk) carried out under ``keep_line``, the sessions whose plans alone resolved the
  meeting (``resolved_plan_only``), measured on their ``plan_only`` replays (the agents' own plans,
  no ORCA underneath).

``--study rf38`` (issue #124, RF-38) reads ``rf38_cane_head_on`` in place of the head-on runs: pairs in
which exactly one person walks with a cane, drawn from a realistic crowd (no speeds, no crowds). Step 1's
subjects are then the resolved sessions with exactly one cane user. It adds how often each rule
matched, and who adapts in a cane pair (described, not a target: no study read is about a cane).
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ..configutil import PACKAGE_ROOT
from . import judge as J
from .measures import TURN_RATE_FLOOR_RAD_S, crowd_measures, pair_measures
from .targets import TARGETS_DIR, TargetFile

RUNS = PACKAGE_ROOT / "runs"
OUT = RUNS / "rf37_human_targets"
TARGETS = TARGETS_DIR / "head_on_v1.yaml"
ARMS = ("plain", "passed_screening", "cane_rule_alone", "all_runnable", "reference_default")
HEAD_ON = ("rf37_head_on", "head_on")
SPEEDS = (("rf37_head_on", "head_on_slow"), ("rf37_head_on", "head_on_normal"), ("rf37_head_on", "head_on_fast"))
FLOWS = (("rf37_flow_density", "flow_15"), ("rf18_round1_realistic", "flow_realistic"), ("rf37_flow_density", "flow_75"))
STEP1 = (("step1_independent", "rf10_round1_head_on_keep_line", "independent"),
         ("step1_non_verbal", "rf30_round1_head_on_keep_line", "non_verbal"),
         ("step1_talk", "rf30_round1_head_on_keep_line", "talk"))
PERSON = ("age", "gender", "assertiveness", "mobility_aid", "load", "distraction")


@dataclass(frozen=True)
class Study:
    """The runs one report reads."""
    key: str
    title: str
    out: Path
    head_on: tuple[str, str]
    speeds: tuple[tuple[str, str], ...] = ()
    flows: tuple[tuple[str, str], ...] = ()
    #: Since issue #124: Step 1's sessions with exactly one person at this level only, and who adapts
    #: in such pairs.
    one_with: Optional[tuple[str, str]] = None


STUDIES = {
    "rf37": Study("rf37", "Round 1 against the human targets (issue #122, RF-37)", OUT, HEAD_ON, SPEEDS, FLOWS),
    "rf38": Study("rf38", "Round 1 in head-on pairs with one cane user, against the human targets (issue #124, RF-38)",
                  RUNS / "rf38_human_targets", ("rf38_cane_head_on", "head_on_cane"), one_with=("mobility_aid", "cane")),
}


@dataclass
class Subject:
    name: str
    pairs: list[dict[str, Any]]                     # head-on, at the scenario's own speed
    speed_pairs: list[dict[str, Any]]               # head-on at Huber2014's three speeds (H3)
    runs: list[dict[str, Any]]                      # two-way flows (C1, C3)
    note: str = ""


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _seed_dirs(experiment: str, scenario: str, arm: str) -> list[Path]:
    folder = RUNS / experiment / "runs" / scenario / arm
    return sorted((p for p in folder.iterdir() if (p / "trajectory.csv").is_file()), key=lambda p: int(p.name)) if folder.is_dir() else []


def evaluation_pairs(experiment: str, scenario: str, arm: str) -> list[dict[str, Any]]:
    out = []
    for run in _seed_dirs(experiment, scenario, arm):
        config = _json(run / "config.json")
        people = {entry["agent_id"]: entry["attributes"] for entry in config["population"]}
        measured = pair_measures(run)
        agents = measured["agents"]
        speeds = {agent["agent_id"]: agent["preferred_speed_mps"] for agent in config["scenario"]["agents"]}
        out.append({"source": f"{experiment}/{scenario}/{arm}/{run.name}", "seed": int(run.name), "speed_mps": speeds[agents[0]],
                    "agents": agents, "people": [{k: people[a].get(k) for k in PERSON} for a in agents],
                    "passed_first": measured["passed_first"], "measures": measured})
    return out


def evaluation_runs(arm: str, flows: Sequence[tuple[str, str]] = FLOWS) -> list[dict[str, Any]]:
    out = []
    for experiment, scenario in flows:
        for run in _seed_dirs(experiment, scenario, arm):
            out.append({"source": f"{experiment}/{scenario}/{arm}/{run.name}", "scenario": scenario, **crowd_measures(run)})
    return out


def step1_pairs(experiment: str, condition: str, one_with: Optional[tuple[str, str]] = None) -> tuple[list[dict[str, Any]], int]:
    """The resolved sessions of one condition, and how many sessions it had in all; with ``one_with``,
    of the sessions with exactly one person at that level only."""
    rows = [row for row in csv.DictReader((RUNS / experiment / "outcomes.csv").open(encoding="utf-8")) if row["condition"] == condition]
    if one_with is not None:
        name, level = one_with
        rows = [row for row in rows if (row[f"p1_{name}"] == level) + (row[f"p2_{name}"] == level) == 1]
    out = []
    for row in rows:
        if row["resolved_plan_only"] != "True":
            continue
        run = RUNS / experiment / "replay" / row["session_id"] / "plan_only"
        people = {int(row[f"{p}_agent"]): {k: (int(row[f"{p}_{k}"]) if k == "age" else row.get(f"{p}_{k}") or None) for k in PERSON}
                  for p in ("p1", "p2")}
        measured = pair_measures(run)
        agents = measured["agents"]
        first = row["who_passed_first_plan_only"]
        config = _json(run / "config.json")
        out.append({"source": f"{experiment}/{row['session_id']}", "seed": None, "session_id": row["session_id"],
                    "speed_mps": config["scenario"]["agents"][0]["preferred_speed_mps"], "agents": agents,
                    "people": [people[a] for a in agents], "passed_first": int(first) if first.isdigit() else (first or None),
                    "measures": measured})
    return out, len(rows)


def subjects(study: Study = STUDIES["rf37"]) -> list[Subject]:
    out = []
    for arm in ARMS:
        speed_pairs = [pair for experiment, scenario in study.speeds for pair in evaluation_pairs(experiment, scenario, arm)]
        out.append(Subject(arm, evaluation_pairs(*study.head_on, arm), speed_pairs, evaluation_runs(arm, study.flows)))
    which = "" if study.one_with is None else f" with exactly one person at {study.one_with[0]} {study.one_with[1]}"
    for name, experiment, condition in STEP1:
        pairs, total = step1_pairs(experiment, condition, study.one_with)
        out.append(Subject(name, pairs, [], [], f"{len(pairs)} of {total} sessions{which} resolved by the plans alone"))
    return out


def rule_matches(experiment: str, scenario: str, arm: str) -> dict[str, int]:
    """For each rule, in how many of an arm's runs it matched at least once (``measures.json``)."""
    out: dict[str, int] = {}
    for run in _seed_dirs(experiment, scenario, arm):
        for rule, count in _json(run / "measures.json")["matches_by_rule"].items():
            out[rule] = out.get(rule, 0) + (count > 0)
    return dict(sorted(out.items()))


def holder_pairs(pairs: Sequence[Mapping[str, Any]], one_with: tuple[str, str]) -> dict[str, Any]:
    """Who adapts in the pairs with exactly one person at a level (issue #124): that person (the holder)
    against the other. Described, not judged: no target is about such a person. Each count is the
    other's way against the holder's, with the exact sign test's p (ties and undefined dropped):
    ``other_adapts_more`` by lateral share, ``other_slows_more`` by speed change."""
    name, level = one_with
    n = 0
    shares: list[float] = []
    adapts, slows = [0, 0], [0, 0]
    first = {"holder": 0, "other": 0, "together": 0, "none": 0}
    for pair in pairs:
        at = [person.get(name) == level for person in pair["people"]]
        per = pair["measures"].get("per_agent")
        if sum(at) != 1 or not per:
            continue
        n += 1
        h = at.index(True)
        holder, other = (per[str(pair["agents"][i])] for i in (h, 1 - h))
        if other["lateral_share"] is not None:
            shares.append(other["lateral_share"])
            if other["lateral_share"] != 0.5:
                adapts[other["lateral_share"] < 0.5] += 1
        if holder["speed_change_mps"] != other["speed_change_mps"]:
            slows[holder["speed_change_mps"] > other["speed_change_mps"]] += 1
        passed = pair["passed_first"]
        first["none" if passed is None else "together" if passed == "together" else "holder" if passed == pair["agents"][h] else "other"] += 1
    return {"pairs": n, "other_mean_lateral_share": J._mean(shares), "other_adapts_more": J._direction(*adapts),
            "other_slows_more": J._direction(*slows), "passed_first": first}


def _spread(pairs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    values = [p["measures"]["min_centre_distance_m"] for p in pairs if p["measures"].get("min_centre_distance_m") is not None]
    return {"n": len(values), "mean": J._mean(values), "min": min(values) if values else None, "max": max(values) if values else None}


def evaluate(file: TargetFile, found: Sequence[Subject], study: Study = STUDIES["rf37"]) -> dict[str, Any]:
    results: dict[str, dict[str, Any]] = {}
    for target in file.targets.values():
        results[target.id] = {}
        for subject in found:
            pairs = subject.speed_pairs if target.check == "increases_with_speed" else subject.pairs
            results[target.id][subject.name] = J.judge(target, file, pairs, subject.runs)
    return {
        "targets_file": file.describe(),
        "turn_rate_floor_rad_s": TURN_RATE_FLOOR_RAD_S,
        "subjects": {s.name: {"pairs": len(s.pairs), "speed_pairs": len(s.speed_pairs), "runs": len(s.runs), "note": s.note,
                              "sides": J.sides(s.pairs), "centre_distance_all_pairs": _spread(s.pairs)} for s in found},
        "results": results,
        "pairs": {s.name: [{k: v for k, v in p.items()} for p in s.pairs + s.speed_pairs] for s in found},
        **({} if study.one_with is None else {
            "study": study.key, "one_with": {study.one_with[0]: study.one_with[1]},
            "rule_matches": {arm: rule_matches(*study.head_on, arm) for arm in ARMS},
            "holder_pairs": {s.name: holder_pairs(s.pairs, study.one_with) for s in found},
            "h7_known_factor": {s.name: J.not_predicted_by_traits_given(s.pairs, file.age_groups, study.one_with) for s in found},
            "holder_younger": {s.name: J.holder_younger(s.pairs, file.age_groups, study.one_with) for s in found},
        }),
    }


# --- the report ----------------------------------------------------------------------------------


def _cell(entry: Mapping[str, Any]) -> str:
    verdict = entry["verdict"]
    if "mean" in entry:
        return f"{verdict}: {entry['mean']} (n {entry['n']})"
    if "mean_by_speed" in entry:
        return f"{verdict}: {entry['study_way']} to {entry['other_way']}; m: " + ", ".join(str(v) for v in entry["mean_by_speed"].values())
    if "mean_share_own_right" in entry:
        return f"{verdict}: {entry['study_way']} of {entry['runs']} runs; own right {entry['mean_share_own_right']}"
    if "study_way" in entry and verdict != J.NOT_COMPARABLE:
        return f"{verdict}: {entry['study_way']} to {entry['other_way']}, p {entry['p']:.3g}"
    if verdict == J.NO_VERDICT:
        return f"{entry['mean_speed_change_mps']} m/s; {entry['share_slowing']} slow"
    if "predicted_by" in entry:
        return f"{verdict}" + (f" ({', '.join(entry['predicted_by'])})" if entry["predicted_by"] else "")
    return verdict


def report_markdown(file: TargetFile, summary: Mapping[str, Any], study: Study = STUDIES["rf37"]) -> str:
    names = list(summary["subjects"])
    lines = [
        f"# {study.title}", "",
        f"Targets: `{file.source}` (sha256 `{file.sha256[:12]}`). Method: `docs/human-targets.md`. No model call, USD 0.", "",
        "**Tolerances** (the user's decision of 2026-10-30, fixed before any rule was measured): a value target is met",
        "within one reported SD of the study's mean; a target with no reported spread is judged on its direction, by the",
        "exact two-sided sign test at 0.05; two studies that disagree are shown with no verdict.", "",
        "**Every comparison marked `[setting differs]` is in a setting unlike the study's** (each target's `differs` in the",
        "targets file says how). The verdicts are about the simulation against the study's numbers, not proof about people.", "",
        "## Subjects", "", "| Subject | Head-on pairs | Pairs at three speeds | Crowd runs | Note |", "| --- | --- | --- | --- | --- |",
    ]
    for name, entry in summary["subjects"].items():
        lines.append(f"| {name} | {entry['pairs']} | {entry['speed_pairs']} | {entry['runs']} | {entry['note']} |")
    lines += ["", "## Verdicts", "", "| Target | " + " | ".join(names) + " |", "| --- |" + " --- |" * len(names)]
    for target in file.targets.values():
        label = f"{target.id}{' [setting differs]' if target.setting_differs else ''}"
        lines.append(f"| {label} | " + " | ".join(_cell(summary["results"][target.id][n]) for n in names) + " |")
    lines += ["", "How to read a cell: a value target gives the subject's mean and the pairs it applies to; a direction target",
              "gives how many seeds, pairs or runs went the study's way against the other (H3 also its mean start of turning",
              "at 1.15, 1.42 and 1.78 m/s; C1 how many runs separated, and the mean share on their own right); H4 and H5 give",
              f"the mean speed change and the share of walkers slowing by more than {J.SLOWING_MPS} m/s, with no verdict.",
              "**A significant direction can be a small effect**: these runs are nearly deterministic, so a consistent",
              "difference of centimetres is significant. Read H3 with its numbers.", "",
              "**Pass distance over all pairs, any ages** (no round 1 rule reads age, so in the rule arms and plain ORCA the",
              "distance does not depend on who the two are; the realistic crowd gives few pairs of two young adults):", "",
              "| Subject | Pairs | Mean centre distance (m) | Smallest | Largest |", "| --- | --- | --- | --- | --- |"]
    for name, entry in summary["subjects"].items():
        d = entry["centre_distance_all_pairs"]
        lines.append(f"| {name} | {d['n']} | {d['mean']} | {d['min']} | {d['max']} |")
    if "holder_pairs" in summary:
        lines += holder_markdown(summary, file.age_groups["older"][0])
    if study.flows:
        lines += ["", "**Speed against density** (C3; Zhang2012 reports a free speed of 1.55 ± 0.18 m/s, no difference from one-way",
                  "flow below 1.0 person/m², and a flow per metre of width that levels off from about 1.0 and peaks at 1.5 /(m·s) at",
                  "2.0 person/m²). Mean speed (m/s) and flow per metre (/(m·s)) by density bin, over every sample:", ""]
        for name in names:
            bins = summary["results"]["C3"][name].get("bins")
            if bins:
                lines.append(f"- {name}: " + "; ".join(f"{b['density_from']}-{b['density_to']}: {b['mean_speed_mps']}, {b['specific_flow_per_m_s']} ({b['samples']})"
                                                       for b in bins if b["samples"] >= 5))
    lines += ["", "## The targets", ""]
    for target in file.targets.values():
        source = file.sources[target.source]["cite"].split(".")[0]
        lines += [f"**{target.id}.** {target.claim} *{source}*, {target.where} ({target.read}).",
                  f"Setting: {target.setting}"]
        if target.kind == "value":
            low, high = target.band
            lines.append(f"Target: {target.value} ± {target.sd} {target.unit} (met from {low} to {high}).")
        if target.reported:
            lines.append(f"Reported: {json.dumps(target.reported)}.")
        for item in target.differs:
            lines.append(f"- Differs: {item}")
        lines.append("")
    lines += ["## Sides (a parameter by place, not judged)", "",
              "For Singapore no published study was found (#69), so no side is judged. Places with a study:", ""]
    for place, entry in file.sides["places"].items():
        lines.append(f"- {place}: {entry['side']} {json.dumps(entry['shares'])} ({entry['source']}, {entry['read']})")
    lines += ["", "| Subject | Both on own left | Both on own right | Mixed | Share left |", "| --- | --- | --- | --- | --- |"]
    for name, entry in summary["subjects"].items():
        s = entry["sides"]
        lines.append(f"| {name} | {s['left']} | {s['right']} | {s['mixed']} | {s['share_left']} |")
    lines += ["", "**The side both ways.** The corridor is symmetric about its centre line, so a rule that turns right in place of",
              "left gives the mirror image of the left-turn rule's runs: every target but the side is the same, apart from the",
              "baseline's random perturbation `[derived: mirror symmetry; not run]`. Which side matches Singapore is unknown.", "",
              "## Left out", ""]
    for entry in file.not_targets:
        lines.append(f"- **{entry['id']}** ({entry['source']}): {entry['claim']} Reason: {entry['reason']}.")
    return "\n".join(lines) + "\n"


def holder_markdown(summary: Mapping[str, Any], older_from: int) -> list[str]:
    """Issue #124: how often each rule matched, and who adapts in the pairs with one holder."""
    (name, level), = summary["one_with"].items()
    lines = ["", f"**How often each rule matched** (runs in which it matched at least once, of each arm's pairs):", "",
             "| Arm | Pairs | Rules matched |", "| --- | --- | --- |"]
    for arm, matched in summary["rule_matches"].items():
        what = ", ".join(f"`{rule}` {count}" for rule, count in matched.items()) or "none"
        lines.append(f"| {arm} | {summary['subjects'][arm]['pairs']} | {what} |")
    lines += ["", f"**Who adapts in a pair with one person at {name} {level}** (described, not a target: no study read is about",
              f"this; H8 is about age). Counts are the other's way against the {level}",
              "user's, ties dropped, with the exact sign test's p:", "",
              f"| Subject | Pairs | The other's mean lateral share | The other deviates more | The other slows more | Passed first: {level} user / other / together / none |",
              "| --- | --- | --- | --- | --- | --- |"]
    for subject, h in summary["holder_pairs"].items():
        a, s, f = h["other_adapts_more"], h["other_slows_more"], h["passed_first"]
        lines.append(f"| {subject} | {h['pairs']} | {h['other_mean_lateral_share']} | "
                     f"{a['study_way']} to {a['other_way']}, p {a['p']:.3g} | {s['study_way']} to {s['other_way']}, p {s['p']:.3g} | "
                     f"{f['holder']} / {f['other']} / {f['together']} / {f['none']} |")
    if "h7_known_factor" in summary:
        lines += h7_known_markdown(summary, level, older_from)
    return lines


def _known_trait(entry: Mapping[str, Any]) -> str:
    parts = []
    if "unseparated" in entry:
        u = entry["unseparated"]
        parts.append(f"both or neither: {u['level_passed_first']} to {u['other_passed_first']}, p {u['p']:.3g}")
    for key in ("separated", "not_separable"):
        if key in entry:
            w, a = entry[key]["with"], entry[key]["against"]
            text = f"holder first with {w['holder_passed_first']} of {sum(w.values())}, against {a['holder_passed_first']} of {sum(a.values())}"
            parts.append(text + (f", p {entry[key]['p']:.3g}" if key == "separated" else ", not separable"))
    return "; ".join(parts)


def h7_known_markdown(summary: Mapping[str, Any], level: str, older_from: int) -> list[str]:
    """Issue #124: H7 with the factor held fixed, and who went first when its holder is the younger."""
    traits = list(J.TRAITS)
    lines = ["", f"**H7 with the {level} held fixed** (not the verdict of record, which is H7's row above). A trait is tested",
             f"apart from the {level}: in pairs where both or neither have it, by H7's sign test; in pairs with one {level} user,",
             f"by whether the {level} user passes first as often when the trait is at its level on the {level} user's side",
             "(\"with\") as on the other's (\"against\"), by Fisher's exact test. A trait whose pairs all fall on one side cannot",
             f"be told apart from the {level} and is not counted. Bonferroni over every test made.", "",
             "| Subject | H7 as recorded | With the " + level + " held fixed | " + " | ".join(traits) + " |",
             "| --- | --- | --- |" + " --- |" * len(traits)]
    for subject, entry in summary["h7_known_factor"].items():
        cell = _cell(entry) + (f"; not separable: {', '.join(entry['not_separable'])}" if entry.get("not_separable") else "")
        lines.append(f"| {subject} | {_cell(summary['results']['H7'][subject])} | {cell} | "
                     + " | ".join(_known_trait(entry["traits"][t]) if t in entry["traits"] else "–" for t in traits) + " |")
    lines += ["", f"**When the {level} user is the younger** (who passed first: {level} user / other / together / none). If age,",
              f"not the {level}, decided who went first, the other would go first here. By group: the {level} user under {older_from}, the other {older_from} or over.", "",
              "| Subject | Younger by years | Younger by age group |", "| --- | --- | --- |"]
    for subject, entry in summary["holder_younger"].items():
        lines.append(f"| {subject} | " + " | ".join(f"{e['pairs']} pairs: {e['holder']} / {e['other']} / {e['together']} / {e['none']}"
                                                    for e in (entry["by_years"], entry["by_group"])) + " |")
    return lines


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--study", choices=sorted(STUDIES), default="rf37", help="which runs to read (default: rf37, issue #122)")
    parser.add_argument("--out", type=Path, default=None, help="default: the study's own folder")
    args = parser.parse_args(argv)
    study = STUDIES[args.study]
    out = args.out or study.out
    if not _seed_dirs(*study.head_on, "plain"):
        # the trajectories are gitignored (.gitignore, RF-37 and RF-38): on a fresh clone the report would
        # find no pair and overwrite the committed summary with empty results
        parser.error(f"no runs in runs/{study.head_on[0]}: rebuild them first (negsim.ruleset_eval ... --overwrite)")
    file = TargetFile.load(TARGETS)
    summary = evaluate(file, subjects(study), study)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    (out / "report.md").write_text(report_markdown(file, summary, study), encoding="utf-8")
    print(f"wrote {out / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
