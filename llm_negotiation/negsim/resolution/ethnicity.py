"""Real ethnicity as a factor (issue #92, RF-26; ``docs/ethnicity.md``).

The user decided on 2026-10-24 that real ethnicity replaces the fictional group of issue #32 in
track #55: Singapore's four census groups, at their shares of the resident population
(``configs/resolution/ethnicity_sg_2026.yaml``, from SingStat's *Population Trends 2026*).

**The design factors** (``design.py``):

=====================  ======================  ==================================================
Factor                 Levels (base first)     What it sets
=====================  ======================  ==================================================
``ethnicity_pair``     ``same``, ``different``  whether the two people are of one group
``ethnicity_visible``  ``true``, ``false``     whether each is told the other's (a switch; on
                                               when left out). One's own is always told
=====================  ======================  ==================================================

**The draw** (:meth:`EthnicityShares.draw`): person 1's group at the shares; person 2's the same
group (``same``), or one of the other three at their shares renormalised (``different``). So the
screen estimates same against different while the people keep the population's real mix. The
random stream is the design's seed, the case and the cell (or a counterfactual pair), never the
condition or the repeat (``WORK_LOG-92.md``, A1): an exact repeat is the same two people, and so
is the same cell under another condition.

**Two ways to draw** (``design.ethnicity_draw``; the user's decision of 2026-10-24, after the
first build, issue #92's open question 3):

``real``      (the default) as above: person 1 at the resident shares. Few sessions for the
              smaller groups (Others: about 3.6% of person 1s)
``balanced``  every group equally often, assigned in a fixed rotation rather than at random so
              that the counts come out even: within each level of ``ethnicity_pair``, person 1
              is each group in a quarter of the sessions and, in a ``different`` session, each
              ordered pair of groups is a twelfth (:func:`balanced_assignment`). So a per-group
              effect gets enough sessions to be estimated

Either way each session carries a weight (:func:`weights`): its pair's chance between two
residents met at random, each at the shares, over the pair's share of the design's sessions
(post-stratification on the pairs actually drawn). The weighted sessions then stand for random
resident pairs exactly: each person at the shares, a same-group pair 57.4% of the time, whatever
the draw and the design's share of ``same`` sessions (neither draw is that on its own: the design
sets the share of ``same``, and task 2's ``different`` keeps person 1 at the shares). A
population-level figure (how often a Singapore pair resolves the conflict) is the weighted one; a
comparison between groups, or same against different, uses the sessions as they are. This is how
a survey oversamples a small group and then reweights.

**Limits.** The shares are of residents only (4.23 of 6.21 million). A visitor is drawn at the
same shares (the user's decision, 2026-10-24). Applying a difference the screen finds to people is
not the point: no rule may read ethnicity (``negsim.rules.fields``, ``protected_attribute``), and a
paid run that varies it needs the supervisor's ethics sign-off (``negsim.ethics``).
"""

from __future__ import annotations

import math
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ..configutil import PACKAGE_ROOT, ConfigError, as_number, check_keys, load_yaml

SHARES_CONFIG = PACKAGE_ROOT / "configs" / "resolution" / "ethnicity_sg_2026.yaml"
#: Singapore's census groups, in the order of the shares file, the template and every table.
GROUPS = ("chinese", "malay", "indian", "others")
SAME, DIFFERENT = "same", "different"
#: How the groups are drawn (``design.ethnicity_draw``).
DRAW_REAL, DRAW_BALANCED = "real", "balanced"
DRAWS = (DRAW_REAL, DRAW_BALANCED)
#: The ordered pairs of a ``different`` session, in blocks of four: within a block each group is
#: person 1 once and person 2 once, so any whole number of blocks balances both people.
DIFFERENT_PAIRS = tuple((first, GROUPS[(k + offset) % len(GROUPS)]) for offset in (1, 2, 3) for k, first in enumerate(GROUPS))
PAIR_LEVELS = (SAME, DIFFERENT)
#: The design factors of issue #92: the pair, and its visibility switch.
PAIR_FACTOR, SWITCH_FACTOR = "ethnicity_pair", "ethnicity_visible"
ETHNICITY_FACTORS = (PAIR_FACTOR, SWITCH_FACTOR)


@dataclass(frozen=True)
class EthnicityShares:
    """The groups and their shares, in percent, as the shares file gives them (``source`` names the
    file, relative to the package when it is inside it)."""

    shares: Mapping[str, float]
    source: str
    cited: Mapping[str, Any]

    def __post_init__(self) -> None:
        if tuple(self.shares) != GROUPS:
            raise ConfigError(f"ethnicity shares: the groups are {list(GROUPS)}, in that order, got {list(self.shares)}")
        total = math.fsum(self.shares.values())
        if abs(total - 100.0) > 0.15:  # a published table of shares to 0.1 may not add up to 100 exactly
            raise ConfigError(f"ethnicity shares: they add up to {total}, not 100")

    @classmethod
    def from_mapping(cls, raw: Any, source: str) -> "EthnicityShares":
        where = f"ethnicity shares {source}"
        data = check_keys(raw, where, ("schema_version", "groups", "source", "limits"))
        if data["schema_version"] != 1:
            raise ConfigError(f"{where}: schema_version 1 is the only one, got {data['schema_version']!r}")
        groups = data["groups"]
        if not isinstance(groups, Mapping):
            raise ConfigError(f"{where}.groups: a mapping of group to percent")
        shares = {str(name): as_number(value, f"{where}.groups.{name}", minimum=0.0, strict_minimum=True) for name, value in groups.items()}
        cited = check_keys(data["source"], f"{where}.source", ("publisher", "title", "url", "read", "sentence"), ("published", "cached"))
        if not isinstance(data["limits"], list) or not data["limits"]:
            raise ConfigError(f"{where}.limits: a non-empty list; the resident-only limit must be said wherever the shares are used")
        return cls(shares, source, {**cited, "limits": list(data["limits"])})

    @classmethod
    def load(cls, path: Path | str = SHARES_CONFIG) -> "EthnicityShares":
        path = Path(path)
        try:
            source = str(path.resolve().relative_to(PACKAGE_ROOT)).replace("\\", "/")
        except ValueError:
            source = str(path).replace("\\", "/")
        return cls.from_mapping(load_yaml(path), source)

    def probability(self, group: str, excluding: Optional[str] = None) -> float:
        """The chance of drawing ``group``: its share, or, with ``excluding``, its share among the
        other groups (renormalised)."""
        if group == excluding:
            return 0.0
        pool = math.fsum(share for name, share in self.shares.items() if name != excluding)
        return self.shares[group] / pool

    def _pick(self, rng: random.Random, excluding: Optional[str] = None) -> str:
        names = [name for name in GROUPS if name != excluding]
        cumulative, point = 0.0, rng.random()
        for name in names:
            cumulative += self.probability(name, excluding)
            if point < cumulative:
                return name
        return names[-1]  # rounding at the top end

    def draw(self, level: str, key: str) -> tuple[str, str]:
        """Person 1's group and person 2's for a session at ``level`` (``same`` or ``different``),
        from the random stream named by ``key``. Person 1 is drawn first, the same way at either
        level, so that two sessions of one key differ only in person 2."""
        if level not in PAIR_LEVELS:
            raise ConfigError(f"ethnicity_pair: one of {list(PAIR_LEVELS)}, got {level!r}")
        rng = random.Random(f"ethnicity:{key}")
        first = self._pick(rng)
        return (first, first) if level == SAME else (first, self._pick(rng, excluding=first))

    def expected_pairs(self, sessions: Mapping[str, int]) -> dict[tuple[str, str], float]:
        """The expected number of sessions with each (person 1, person 2) pair of groups, given the
        number of sessions at each level of ``ethnicity_pair`` (``sessions``)."""
        expected: dict[tuple[str, str], float] = {}
        for first in GROUPS:
            p_first = self.probability(first)
            expected[(first, first)] = sessions.get(SAME, 0) * p_first
            for second in GROUPS:
                if second != first:
                    expected[(first, second)] = sessions.get(DIFFERENT, 0) * p_first * self.probability(second, excluding=first)
        return expected

    def pair_probability(self, level: str, first: str, second: str) -> float:
        """The chance of the pair (person 1, person 2) at ``level`` under the resident shares."""
        if level == SAME:
            return self.probability(first) if first == second else 0.0
        return self.probability(first) * self.probability(second, excluding=first)

    def as_dict(self) -> dict[str, Any]:
        return {"source": self.source, "shares": dict(self.shares)}


def resident_pair(shares: EthnicityShares, first: str, second: str) -> float:
    """The chance that two residents met at random are of these groups, person 1 then person 2:
    each at the shares, independently (a same-group pair 57.4% of the time at the 2026 shares)."""
    return (shares.shares[first] / 100) * (shares.shares[second] / 100)


def weights(shares: EthnicityShares, pairs: Sequence[tuple[str, str]]) -> list[float]:
    """Each session's weight back to the resident shares, for sessions given as (person 1's group,
    person 2's group): the pair's chance between two residents met at random (:func:`resident_pair`)
    times the number of sessions, over the number of sessions with that pair (post-stratification
    on the pairs the design drew). The weights add up to the number of sessions, shared among the
    pairs as between residents met at random, whatever the draw and whatever the design's share of
    ``same`` sessions. A pair the design never drew loses its share (:func:`missing_pairs`)."""
    with_pair = Counter(pairs)
    return [round(resident_pair(shares, a, b) * len(pairs) / with_pair[(a, b)], 6) for a, b in pairs]


def missing_pairs(pairs: Sequence[tuple[str, str]]) -> list[tuple[str, str]]:
    """The pairs of groups that none of the sessions has: their share is missing from the weighted
    figures (a design that runs only ``same``, say, stands for same-group pairs only)."""
    drawn = set(pairs)
    return [(a, b) for a in GROUPS for b in GROUPS if (a, b) not in drawn]


def balanced_assignment(units: Mapping[Any, frozenset], seed: int) -> dict[Any, dict[str, tuple[str, str]]]:
    """The ``balanced`` draw: for each unit (a case and a cell, or a case and a counterfactual
    pair; every session of a unit sees the same people) and each level of ``ethnicity_pair`` it
    runs at, the pair of groups (person 1, person 2).

    The units are taken stratum by stratum (those that run only ``same``, only ``different``,
    and pairs that flip ``ethnicity_pair``, which run both), in an order shuffled with the seed,
    and given the pairs in rotation: the four groups for ``same``, :data:`DIFFERENT_PAIRS` for
    the others. A unit of both levels is ``same`` with its ``different`` pair's person 1."""
    found: dict[Any, dict[str, tuple[str, str]]] = {}
    strata: dict[tuple[str, ...], list[Any]] = {}
    for unit, levels in units.items():
        strata.setdefault(tuple(sorted(levels)), []).append(unit)
    for stratum, members in sorted(strata.items()):
        members = sorted(members, key=repr)
        random.Random(f"ethnicity_balanced:{seed}:{'+'.join(stratum)}").shuffle(members)
        for k, unit in enumerate(members):
            if stratum == (SAME,):
                group = GROUPS[k % len(GROUPS)]
                found[unit] = {SAME: (group, group)}
            else:
                first, second = DIFFERENT_PAIRS[k % len(DIFFERENT_PAIRS)]
                found[unit] = {level: (first, first) if level == SAME else (first, second) for level in stratum}
    return found


def pair_table(
    shares: EthnicityShares, drawn: Sequence[tuple[str, str]], at_level: Mapping[str, int], draw: str = DRAW_REAL, weights: Sequence[float] = (),
) -> list[str]:
    """``--plan``'s lines (task 9): for each pair of groups (person 1, person 2), the sessions
    drawn, what the draw should give, and the weighted number, which is what the sessions stand for
    between residents met at random; then each group's share of the persons, drawn and weighted."""
    if draw == DRAW_BALANCED:
        expected = {(a, b): at_level.get(SAME, 0) / len(GROUPS) if a == b else at_level.get(DIFFERENT, 0) / len(DIFFERENT_PAIRS)
                    for a in GROUPS for b in GROUPS}
    else:
        expected = shares.expected_pairs(at_level)
    counts: dict[tuple[str, str], int] = {}
    weighted: dict[tuple[str, str], float] = {}
    for k, pair in enumerate(drawn):
        counts[pair] = counts.get(pair, 0) + 1
        weighted[pair] = weighted.get(pair, 0.0) + (weights[k] if weights else 1.0)
    how = "every group equally often" if draw == DRAW_BALANCED else "person 1 at the shares"
    lines = [
        f"ethnicity: {len(drawn)} session(s), {at_level.get(SAME, 0)} same and {at_level.get(DIFFERENT, 0)} different; draw {draw} "
        f"({how}); shares of residents only ({shares.source})",
        "  per pair (person 1 / person 2): drawn (expected under the draw); weighted (ethnicity_weight: as between residents met at random):",
    ]
    for a in GROUPS:
        for b in GROUPS:
            lines.append(f"  {a} / {b}: drawn {counts.get((a, b), 0)} (expected {expected.get((a, b), 0.0):.1f}); weighted {weighted.get((a, b), 0.0):.1f}")
    persons = [group for pair in drawn for group in pair]
    lines.append("  persons drawn: " + ", ".join(
        f"{group} {persons.count(group)} ({100 * persons.count(group) / len(persons):.1f}%)" if persons else f"{group} 0" for group in GROUPS
    ))
    total = 2 * math.fsum(weighted.values())
    lines.append("  persons weighted: " + ", ".join(
        f"{group} {100 * math.fsum(w for pair, w in weighted.items() for who in pair if who == group) / total:.1f}% (residents {shares.shares[group]}%)"
        if total else f"{group} 0" for group in GROUPS
    ))
    missing = missing_pairs(list(drawn))
    if missing and drawn:
        share = math.fsum(resident_pair(shares, a, b) for a, b in missing)
        lines.append(f"  never drawn, so missing from the weighted figures ({100 * share:.1f}% of random resident pairs): "
                     + ", ".join(f"{a} / {b}" for a, b in missing))
    return lines


def person_shares(shares: EthnicityShares, at_level: Mapping[str, int]) -> dict[str, float]:
    """The expected share of each group among all the persons of the sessions (two per session),
    given the number of sessions at each level of ``ethnicity_pair``."""
    expected = shares.expected_pairs(at_level)
    total = 2 * sum(at_level.get(level, 0) for level in PAIR_LEVELS)
    return {
        group: (math.fsum(value for (first, second), value in expected.items() for who in (first, second) if who == group) / total) if total else 0.0
        for group in GROUPS
    }
