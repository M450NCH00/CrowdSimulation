"""Each subject (a rule arm, plain ORCA, Step 1's agents) against each human target (issue #122, RF-37;
``docs/human-targets.md``, section 3).

The tolerances are the user's of 2026-10-30, fixed before any rule was measured:

* A **value** target: the subject's mean over the pairs it applies to lies within the study's mean
  +/- one reported SD: **within** or **outside**.
* A **direction** target: judged by its ``check`` with the exact two-sided sign test of RF-18
  (``negsim.ruleset_eval.verdicts.sign_test``) at ``ALPHA``: **agrees** (significantly the study's
  way), **opposite** (significantly the other way) or **not shown** (neither).
* Two targets that **disagree** (``disagrees_with``) are shown side by side with **no verdict**.
* A target with no pair or run it applies to is **not comparable**.

The checks (each a sign test over pairs or runs; ties and undefined pairs dropped):

| Check | Counted for | The study's way |
| --- | --- | --- |
| ``increases_with_speed`` | each seed: the walkers' mean start of turning at the fast speed against the slow (same people) | fast earlier |
| ``giver_adapts_more`` | each pair with distinct roles: the giver's lateral share against the first's | giver more |
| ``younger_adapts_more`` | each pair of an older and a young walker: the young one's share against the older one's | young more |
| ``not_predicted_by_traits`` | each trait the two differ in: the walker at the trait's first level passed first, or the other | no trait significant at ``ALPHA`` / the number of traits tested (Bonferroni) |
| ``segregated`` | each run: whether more walkers kept to one own side than chance would (sign test of left against right, p < ``ALPHA``) | most runs segregated |
| ``speed_decreases_with_density`` | each run: the sign of the least-squares slope of speed on density | most runs negative |

``no_speed_change`` and ``speed_decreases`` (H4, H5) disagree, so they only report the speed change.
"""

from __future__ import annotations

import math
from typing import Any, Iterable, Mapping, Optional, Sequence

from ..ruleset_eval.verdicts import sign_test
from .targets import DIRECTION, VALUE, Target, TargetFile

ALPHA = 0.05
WITHIN, OUTSIDE = "within", "outside"
AGREES, OPPOSITE, NOT_SHOWN = "agrees", "opposite", "not shown"
NO_VERDICT, NOT_COMPARABLE = "no verdict (studies disagree)", "not comparable"
#: The traits a person in these runs has that a study says do not decide the roles (Knorr2016:
#: gender, height, personality traits), each with the level counted as "first". Height is not modelled.
TRAITS = {"assertiveness": "holds_ground", "gender": "female", "older": True}
#: [design] A speed change above this counts as slowing in the report of H4 and H5 (no verdict).
SLOWING_MPS = 0.1


def _mean(values: Iterable[Optional[float]]) -> Optional[float]:
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 4) if values else None


def _sd(values: Iterable[Optional[float]]) -> Optional[float]:
    values = [v for v in values if v is not None]
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    return round(math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - 1)), 4)


def _direction(ours: int, theirs: int, alpha: float = ALPHA) -> dict[str, Any]:
    """The study's way ``ours`` times, the other way ``theirs`` times."""
    p = sign_test(ours, theirs)
    verdict = NOT_COMPARABLE if ours + theirs == 0 else AGREES if p < alpha and ours > theirs else OPPOSITE if p < alpha else NOT_SHOWN
    return {"verdict": verdict, "study_way": ours, "other_way": theirs, "p": round(p, 6)}


def age_group(age: Optional[int], groups: Mapping[str, tuple[int, int]]) -> Optional[str]:
    for name, (low, high) in groups.items():
        if age is not None and low <= age <= high:
            return name
    return None


def applies(target: Target, pair: Mapping[str, Any], groups: Mapping[str, tuple[int, int]]) -> bool:
    """Whether a pair record is one the target applies to (``applies.pair_ages``)."""
    wanted = target.applies.get("pair_ages")
    if not wanted:
        return True
    have = [age_group(person.get("age"), groups) for person in pair["people"]]
    first, second = wanted
    return any((first == "any" or have[i] == first) and (second == "any" or have[1 - i] == second) for i in (0, 1))


def _share(pair: Mapping[str, Any], index: int) -> Optional[float]:
    return pair["measures"]["per_agent"][str(pair["agents"][index])]["lateral_share"]


def judge_value(target: Target, pairs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    values = [p["measures"][target.measure] for p in pairs if p["measures"].get(target.measure) is not None]
    if not values:
        return {"verdict": NOT_COMPARABLE, "n": 0}
    mean = _mean(values)
    low, high = target.band
    return {"verdict": WITHIN if low <= mean <= high else OUTSIDE, "n": len(values), "mean": mean, "sd": _sd(values),
            "band": [low, high]}


def increases_with_speed(pairs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Fast against slow on the same seed (the same people): who started turning earlier."""
    by_speed: dict[float, dict[int, Optional[float]]] = {}
    for pair in pairs:
        starts = [v["turning_start_m"] for v in pair["measures"]["per_agent"].values()]
        by_speed.setdefault(pair["speed_mps"], {})[pair["seed"]] = _mean(starts)
    if len(by_speed) < 2:
        return {"verdict": NOT_COMPARABLE, "reason": "one walking speed only"}
    slow, fast = by_speed[min(by_speed)], by_speed[max(by_speed)]
    ours = theirs = 0
    for seed in sorted(set(slow) & set(fast)):
        if slow[seed] is None or fast[seed] is None or slow[seed] == fast[seed]:
            continue
        ours, theirs = (ours + 1, theirs) if fast[seed] > slow[seed] else (ours, theirs + 1)
    return {**_direction(ours, theirs), "mean_by_speed": {str(speed): _mean(seeds.values()) for speed, seeds in sorted(by_speed.items())}}


def giver_adapts_more(pairs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    ours = theirs = 0
    for pair in pairs:
        first = pair["passed_first"]
        if first not in pair["agents"]:
            continue
        giver = 1 - pair["agents"].index(first)
        share = _share(pair, giver)
        if share is None or share == 0.5:
            continue
        ours, theirs = (ours + 1, theirs) if share > 0.5 else (ours, theirs + 1)
    return _direction(ours, theirs)


def younger_adapts_more(pairs: Sequence[Mapping[str, Any]], groups: Mapping[str, tuple[int, int]]) -> dict[str, Any]:
    ours = theirs = 0
    for pair in pairs:
        kinds = [age_group(person.get("age"), groups) for person in pair["people"]]
        if sorted(map(str, kinds)) != ["older", "young"]:
            continue
        share = _share(pair, kinds.index("young"))
        if share is None or share == 0.5:
            continue
        ours, theirs = (ours + 1, theirs) if share > 0.5 else (ours, theirs + 1)
    return _direction(ours, theirs)


def _trait(person: Mapping[str, Any], name: str, groups: Mapping[str, tuple[int, int]]) -> Any:
    return age_group(person.get("age"), groups) == "older" if name == "older" else person.get(name)


def not_predicted_by_traits(pairs: Sequence[Mapping[str, Any]], groups: Mapping[str, tuple[int, int]]) -> dict[str, Any]:
    tested = {}
    for name, level in TRAITS.items():
        at_level_first = other_first = 0
        for pair in pairs:
            first = pair["passed_first"]
            if first not in pair["agents"]:
                continue
            values = [_trait(person, name, groups) for person in pair["people"]]
            if values[0] == values[1] or level not in values:
                continue
            at_level_first, other_first = ((at_level_first + 1, other_first) if values[pair["agents"].index(first)] == level
                                           else (at_level_first, other_first + 1))
        if at_level_first + other_first:
            tested[name] = {"level": level, "level_passed_first": at_level_first, "other_passed_first": other_first,
                            "p": round(sign_test(at_level_first, other_first), 6)}
    if not tested:
        return {"verdict": NOT_COMPARABLE, "reason": "no pair with distinct roles differs in a trait"}
    threshold = ALPHA / len(tested)
    predicted = sorted(name for name, entry in tested.items() if entry["p"] < threshold)
    return {"verdict": OPPOSITE if predicted else AGREES, "predicted_by": predicted, "threshold": round(threshold, 6), "traits": tested,
            "note": "speed and heading do not differ between the two walkers in these runs, so that half of the finding is not tested"}


def segregated(runs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    ours = theirs = 0
    shares = []
    for run in runs:
        lanes = run.get("lanes")
        if not lanes or not lanes["agents"]:
            continue
        left = round(lanes["share_left"] * lanes["agents"])
        right = round(lanes["share_right"] * lanes["agents"])
        shares.append(lanes["share_right"])
        ours, theirs = (ours + 1, theirs) if sign_test(left, right) < ALPHA else (ours, theirs + 1)
    return {**_direction(ours, theirs), "runs": ours + theirs, "mean_share_own_right": _mean(shares)}


def _slope(points: Sequence[tuple[float, float]]) -> Optional[float]:
    if len(points) < 3:
        return None
    mx = sum(x for x, _ in points) / len(points)
    my = sum(y for _, y in points) / len(points)
    sxx = sum((x - mx) ** 2 for x, _ in points)
    return None if sxx == 0 else sum((x - mx) * (y - my) for x, y in points) / sxx


def density_bins(runs: Sequence[Mapping[str, Any]], width: float = 0.25) -> list[dict[str, Any]]:
    """Mean speed and specific flow (density times speed) per density bin, over every sample."""
    bins: dict[int, list[tuple[float, float]]] = {}
    for run in runs:
        for density, speed in run.get("speed_by_density") or []:
            bins.setdefault(int(density // width), []).append((density, speed))
    return [{"density_from": round(k * width, 3), "density_to": round((k + 1) * width, 3), "samples": len(v),
             "mean_speed_mps": _mean(s for _, s in v), "specific_flow_per_m_s": _mean(d * s for d, s in v)}
            for k, v in sorted(bins.items())]


def speed_decreases_with_density(runs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    ours = theirs = 0
    for run in runs:
        slope = _slope(run.get("speed_by_density") or [])
        if slope is None or slope == 0:
            continue
        ours, theirs = (ours + 1, theirs) if slope < 0 else (ours, theirs + 1)
    return {**_direction(ours, theirs), "bins": density_bins(runs)}


def speed_change_report(pairs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    changes = [v["speed_change_mps"] for p in pairs for v in p["measures"]["per_agent"].values()]
    return {"verdict": NO_VERDICT, "walkers": len(changes), "mean_speed_change_mps": _mean(changes),
            "share_slowing": round(sum(c > SLOWING_MPS for c in changes) / len(changes), 4) if changes else None,
            "slowing_above_mps": SLOWING_MPS}


def judge(target: Target, file: TargetFile, pairs: Sequence[Mapping[str, Any]], runs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """One target against one subject's pair records (head-on) and crowd runs (two-way flow)."""
    if target.applies.get("scenario") == "two_way_flow":
        if not runs:
            return {"verdict": NOT_COMPARABLE, "reason": "no two-way flow"}
        return segregated(runs) if target.check == "segregated" else speed_decreases_with_density(runs)
    mine = [pair for pair in pairs if applies(target, pair, file.age_groups)]
    if not mine:
        return {"verdict": NOT_COMPARABLE, "n": 0}
    if target.disagrees_with is not None:
        return speed_change_report(mine)
    if target.kind == VALUE:
        return judge_value(target, mine)
    assert target.kind == DIRECTION
    if target.check == "increases_with_speed":
        return increases_with_speed(mine)
    if target.check == "giver_adapts_more":
        return giver_adapts_more(mine)
    if target.check == "younger_adapts_more":
        return younger_adapts_more(mine, file.age_groups)
    if target.check == "not_predicted_by_traits":
        return not_predicted_by_traits(mine, file.age_groups)
    raise ValueError(f"{target.id}: no judge for check {target.check!r}")


def sides(pairs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """How the walkers passed, in their own frames: both on their own left, both on their right, or
    neither (the two kept different sides at the closest point, which in a head-on means they were
    not abreast, or one was pushed across)."""
    counts = {"left": 0, "right": 0, "mixed": 0}
    for pair in pairs:
        kept = {v["side"] for v in pair["measures"]["per_agent"].values()}
        counts[kept.pop() if len(kept) == 1 and None not in kept else "mixed"] += 1
    total = sum(counts.values())
    return {**counts, "pairs": total, "share_left": round(counts["left"] / total, 4) if total else None,
            "share_right": round(counts["right"] / total, 4) if total else None}
