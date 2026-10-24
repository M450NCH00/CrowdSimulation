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

**Limits.** The shares are of residents only (4.23 of 6.21 million). A visitor is drawn at the
same shares (the user's decision, 2026-10-24). Applying a difference the screen finds to people is
not the point: no rule may read ethnicity (``negsim.rules.fields``, ``protected_attribute``), and a
paid run that varies it needs the supervisor's ethics sign-off (``negsim.ethics``).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ..configutil import PACKAGE_ROOT, ConfigError, as_number, check_keys, load_yaml

SHARES_CONFIG = PACKAGE_ROOT / "configs" / "resolution" / "ethnicity_sg_2026.yaml"
#: Singapore's census groups, in the order of the shares file, the template and every table.
GROUPS = ("chinese", "malay", "indian", "others")
SAME, DIFFERENT = "same", "different"
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

    def as_dict(self) -> dict[str, Any]:
        return {"source": self.source, "shares": dict(self.shares)}


def pair_table(shares: EthnicityShares, drawn: Sequence[tuple[str, str]], at_level: Mapping[str, int]) -> list[str]:
    """``--plan``'s lines: for each pair of groups (person 1, person 2), the expected and the drawn
    number of sessions, then each group's share of the persons drawn (task 9)."""
    expected = shares.expected_pairs(at_level)
    counts: dict[tuple[str, str], int] = {}
    for pair in drawn:
        counts[pair] = counts.get(pair, 0) + 1
    lines = [f"ethnicity: {len(drawn)} session(s), {at_level.get(SAME, 0)} same and {at_level.get(DIFFERENT, 0)} different; "
             f"shares of residents only ({shares.source}); per pair (person 1 / person 2), expected and drawn:"]
    for pair in sorted(expected, key=lambda p: (GROUPS.index(p[0]), GROUPS.index(p[1]))):
        lines.append(f"  {pair[0]} / {pair[1]}: expected {expected[pair]:.1f}, drawn {counts.get(pair, 0)}")
    persons = [group for pair in drawn for group in pair]
    lines.append("  persons drawn: " + ", ".join(
        f"{group} {persons.count(group)} ({100 * persons.count(group) / len(persons):.1f}%)" if persons else f"{group} 0" for group in GROUPS
    ))
    share = person_shares(shares, at_level)
    lines.append("  persons expected: " + ", ".join(f"{group} {100 * share[group]:.1f}% (residents {shares.shares[group]}%)" for group in GROUPS))
    if at_level.get(DIFFERENT, 0):
        lines.append("  (person 2 of a 'different' session is drawn from the other three groups, so the smaller groups are more")
        lines.append("  common among persons than among residents; person 1, and both people of a 'same' session, are at the shares)")
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
