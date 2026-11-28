"""Population profiles: who is in a simulated crowd (issue #112, RF-33; ``docs/population-profiles.md``).

A profile is a frozen file under ``configs/populations/`` that says, for a rule-set evaluation
scenario, what people the crowd is made of and why:

- ``purpose``: ``realistic`` (sourced shares; a rule's verdict of record comes from these) or
  ``stress`` (exaggerated shares, to see whether a rule works where it applies; never a verdict of
  record on its own). The user's decision of 2026-10-27.
- ``generator``:

  ``quotas``  Exact shares on every seed (:func:`quota_people`): the age bands by sex, and each
              factor's share by age band, each share naming its source (``placeholder`` when none
              was found). A realistic profile must be of this kind.
  ``cycle``   Each factor's levels cycle (``negsim.rulegen.replay.mixed_population``), RF-18's crowd,
              so that a scenario with it runs the same people as RF-18 did.

Only what a rule can read is given: age, gender and the core factors of ``negsim.personas.schema``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .configutil import PACKAGE_ROOT, ConfigError, as_choice, as_number, check_keys, load_yaml
from .personas.schema import ATTRIBUTES, FACTOR_ATTRIBUTES, MAX_AGE, MIN_AGE
from .rules.database import file_sha256

POPULATIONS_DIR = PACKAGE_ROOT / "configs" / "populations"
REALISTIC, STRESS = "realistic", "stress"
PURPOSES = (REALISTIC, STRESS)
QUOTAS, CYCLE = "quotas", "cycle"
GENERATORS = (QUOTAS, CYCLE)
PLACEHOLDER = "placeholder"
#: The age from which a person counts as older in a profile's summary (SingStat's "65 Years & Over").
OLDER_FROM = 65


def apportion(total: int, weights: Sequence[float]) -> list[int]:
    """Whole numbers adding up to ``total``, in proportion to ``weights``: each gets the whole part
    of its quota, and what is left goes to the largest remainders (the earlier one on a tie), the
    largest-remainder method. Deterministic."""
    weight = math.fsum(weights)
    if total < 0 or weight <= 0:
        return [0] * len(weights)
    quotas = [total * w / weight for w in weights]
    counts = [math.floor(q) for q in quotas]
    order = sorted(range(len(weights)), key=lambda i: (-(quotas[i] - counts[i]), i))
    for i in order[: total - sum(counts)]:
        counts[i] += 1
    return counts


def _nearest(value: float) -> int:
    """The nearest whole number, a half rounded up (not Python's round-half-to-even)."""
    return math.floor(value + 0.5)


@dataclass(frozen=True)
class FactorShares:
    name: str
    level: str                                   # the level whose share is given
    other: str                                   # everyone else's level
    by_age: tuple[tuple[int, int, float, str], ...]  # (from, to, share, source)

    def share(self, low: int, high: int) -> float:
        for start, end, value, _ in self.by_age:
            if start <= low and high <= end:
                return value
        raise ConfigError(f"factor {self.name}: no share for ages {low} to {high}")


@dataclass(frozen=True)
class Profile:
    name: str
    purpose: str
    generator: str
    source: str        # the file, relative to the package when it is inside it
    sha256: str
    limits: tuple[str, ...]
    bands: tuple[tuple[int, int, int, int], ...] = ()       # quotas: (from, to, male, female)
    factors: tuple[FactorShares, ...] = ()                  # quotas
    sources: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    cycle: Mapping[str, Any] = field(default_factory=dict)  # cycle: ages, genders, factors

    # --- loading ---------------------------------------------------------------------------------

    @classmethod
    def load(cls, path: Path | str) -> "Profile":
        path = Path(path)
        try:
            source = path.resolve().relative_to(PACKAGE_ROOT).as_posix()
        except ValueError:
            source = path.as_posix()
        return cls.from_mapping(load_yaml(path), source, file_sha256(path))

    @classmethod
    def from_mapping(cls, raw: Any, source: str, sha256: str = "") -> "Profile":
        where = f"population {source}"
        head = check_keys(raw, where, ("schema_version", "name", "purpose", "generator", "limits"), ("age", "factors", "sources", "ages", "genders"))
        if head["schema_version"] != 1:
            raise ConfigError(f"{where}: schema_version 1 is the only one, got {head['schema_version']!r}")
        purpose = as_choice(head["purpose"], f"{where}.purpose", PURPOSES)
        generator = as_choice(head["generator"], f"{where}.generator", GENERATORS)
        limits = head["limits"]
        if not isinstance(limits, list) or not limits or not all(str(item).strip() for item in limits):
            raise ConfigError(f"{where}.limits: a non-empty list; a profile's limits are said wherever it is used")
        common = dict(name=str(head["name"]), purpose=purpose, generator=generator, source=source, sha256=sha256,
                      limits=tuple(" ".join(str(item).split()) for item in limits))
        if generator == CYCLE:
            if purpose == REALISTIC:
                raise ConfigError(f"{where}: a realistic profile gives sourced shares (generator: quotas); a cycling mix has none")
            check_keys(raw, where, ("schema_version", "name", "purpose", "generator", "limits", "ages", "genders"), ("factors",))
            return cls(**common, cycle=_cycle(raw, where))
        check_keys(raw, where, ("schema_version", "name", "purpose", "generator", "limits", "age", "factors", "sources"))
        sources = raw["sources"]
        if not isinstance(sources, Mapping) or not sources:
            raise ConfigError(f"{where}.sources: a mapping of source name to its citation")
        for key, entry in sources.items():
            check_keys(entry, f"{where}.sources.{key}", ("cite",), ("measured", "url", "read", "cached"))
        age = check_keys(raw["age"], f"{where}.age", ("source", "bands"))
        _known_source(age["source"], sources, f"{where}.age.source")
        bands = tuple(_band(entry, f"{where}.age.bands[{i}]") for i, entry in enumerate(age["bands"] or []))
        if not bands:
            raise ConfigError(f"{where}.age.bands: at least one band")
        for (_, end, _, _), (start, _, _, _) in zip(bands, bands[1:]):
            if start != end + 1:
                raise ConfigError(f"{where}.age.bands: the bands must follow on from each other, without gaps or overlaps")
        factors = tuple(_factor_shares(name, entry, sources, bands, f"{where}.factors.{name}") for name, entry in (raw["factors"] or {}).items())
        return cls(**common, bands=bands, factors=factors, sources={str(k): dict(v) for k, v in sources.items()})

    # --- people ----------------------------------------------------------------------------------

    def people(self, n_agents: int, seed: int, repeat: int = 1, rotate: bool = False, pool: Optional[int] = None,
               one_with: Optional[tuple[str, str]] = None) -> dict[int, dict[str, Any]]:
        """The people of one run, the same for every arm on a seed. ``one_with`` (quotas only): exactly
        one of them at a factor's level (:func:`one_with_people`)."""
        if self.generator == CYCLE:
            if one_with is not None:
                raise ConfigError(f"population {self.source}: one_with needs a profile of quotas")
            from .rulegen.replay import mixed_population

            offset = repeat - 1 if rotate else 0
            mixed = mixed_population(offset + n_agents, self.cycle["ages"], self.cycle["genders"], self.cycle["factors"])
            return {k: mixed[offset + k] for k in range(n_agents)}
        return quota_people(self, n_agents, seed, pool, one_with)

    def check_one_with(self, raw: Any, where: str) -> tuple[str, str]:
        """``{factor: level}``, one entry, the level whose share this profile gives (issue #124)."""
        if self.generator != QUOTAS:
            raise ConfigError(f"{where}: only with a population of quotas")
        if not isinstance(raw, Mapping) or len(raw) != 1:
            raise ConfigError(f"{where}: one factor and its level, e.g. {{mobility_aid: cane}}")
        (name, level), = raw.items()
        given = {factor.name: factor.level for factor in self.factors}
        if name not in given:
            raise ConfigError(f"{where}: {name!r} is not a factor of {self.source} ({', '.join(given)})")
        if level != given[name]:
            raise ConfigError(f"{where}.{name}: {level!r}, but {self.source} gives the share of {given[name]!r}")
        return str(name), str(level)

    def expected(self) -> dict[str, float]:
        """The share of a crowd aged ``OLDER_FROM`` and over, and at each factor's level, as the
        profile gives them (quotas only)."""
        weights = [male + female for _, _, male, female in self.bands]
        total = math.fsum(weights)
        out = {f"age_{OLDER_FROM}_and_over": math.fsum(w for (start, _, _, _), w in zip(self.bands, weights) if start >= OLDER_FROM) / total}
        for factor in self.factors:
            out[f"{factor.name}_{factor.level}"] = math.fsum(w * factor.share(start, end) for (start, end, _, _), w in zip(self.bands, weights)) / total
        return {key: round(value, 4) for key, value in out.items()}

    def describe(self) -> dict[str, Any]:
        return {"name": self.name, "file": self.source, "sha256": self.sha256, "purpose": self.purpose, "generator": self.generator,
                **({"expected": self.expected()} if self.generator == QUOTAS else {}), "limits": list(self.limits)}


def _known_source(name: Any, sources: Mapping[str, Any], where: str) -> str:
    if name not in sources:
        raise ConfigError(f"{where}: {name!r} is not under 'sources' (a share with no source says '{PLACEHOLDER}', which must be listed too)")
    return str(name)


def _age_number(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not MIN_AGE <= value <= MAX_AGE:
        raise ConfigError(f"{where}: a whole number of years from {MIN_AGE} to {MAX_AGE}, got {value!r}")
    return value


def _band(entry: Any, where: str) -> tuple[int, int, int, int]:
    if not isinstance(entry, list) or len(entry) != 4:
        raise ConfigError(f"{where}: [from, to, male, female]")
    start, end = _age_number(entry[0], f"{where}[0]"), _age_number(entry[1], f"{where}[1]")
    if end < start:
        raise ConfigError(f"{where}: 'to' is below 'from'")
    male, female = (int(as_number(value, f"{where}[{i}]", minimum=0)) for i, value in ((2, entry[2]), (3, entry[3])))
    if male + female == 0:
        raise ConfigError(f"{where}: a band with nobody in it")
    return start, end, male, female


def _factor_shares(name: str, entry: Any, sources: Mapping[str, Any], bands: Sequence[tuple[int, int, int, int]], where: str) -> FactorShares:
    if name not in FACTOR_ATTRIBUTES:
        raise ConfigError(f"{where}: not a core factor; known: {list(FACTOR_ATTRIBUTES)}")
    entry = check_keys(entry, where, ("level", "by_age"))
    levels = ATTRIBUTES[name].levels
    level = as_choice(entry["level"], f"{where}.level", levels)
    by_age = []
    for i, row in enumerate(entry["by_age"] or []):
        row_where = f"{where}.by_age[{i}]"
        row = check_keys(row, row_where, ("ages", "share", "source"))
        ages = row["ages"]
        if not isinstance(ages, list) or len(ages) != 2:
            raise ConfigError(f"{row_where}.ages: [from, to]")
        share = as_number(row["share"], f"{row_where}.share", minimum=0.0)
        if share > 1:
            raise ConfigError(f"{row_where}.share: a share from 0 to 1, got {share}")
        by_age.append((_age_number(ages[0], f"{row_where}.ages[0]"), _age_number(ages[1], f"{row_where}.ages[1]"), share,
                       _known_source(row["source"], sources, f"{row_where}.source")))
    factor = FactorShares(name, level, next(other for other in levels if other != level), tuple(by_age))
    for start, end, _, _ in bands:  # every band lies wholly inside one row, so each band has one share
        if sum(a <= start and end <= b for a, b, _, _ in by_age) != 1:
            raise ConfigError(f"{where}.by_age: ages {start} to {end} (a band) must lie inside exactly one row")
    return factor


def _cycle(raw: Mapping[str, Any], where: str) -> dict[str, Any]:
    ages = [_age_number(age, f"{where}.ages") for age in raw["ages"] or []]
    genders = [as_choice(g, f"{where}.genders", ("female", "male")) for g in raw["genders"] or []]
    if not ages or not genders:
        raise ConfigError(f"{where}: at least one age and one gender")
    factors = {}
    for name, levels in (raw.get("factors") or {}).items():
        if name not in FACTOR_ATTRIBUTES:
            raise ConfigError(f"{where}.factors.{name}: not a core factor; known: {list(FACTOR_ATTRIBUTES)}")
        factors[name] = [as_choice(level, f"{where}.factors.{name}", ATTRIBUTES[name].levels) for level in levels or []]
    return {"ages": ages, "genders": genders, "factors": factors}


def quota_people(profile: Profile, n_agents: int, seed: int, pool: Optional[int] = None,
                 one_with: Optional[tuple[str, str]] = None) -> dict[int, dict[str, Any]]:
    """People at exact shares, the same for every arm on a seed, and different from seed to seed.

    1. The ``size`` people (``pool``, or ``n_agents`` if larger) are shared out over the age bands
       by sex by the largest-remainder method (:func:`apportion`), so the counts are exact.
    2. Each person's age is drawn evenly from their band.
    3. Each factor: the crowd's number at its level is the nearest whole number to what the shares
       give, shared out over the bands in proportion to their expected numbers (never more than a
       band holds); within a band, who gets it is drawn. Factors are drawn independently of each
       other (a profile gives no joint shares beyond age).
    4. The people are shuffled onto the agents, and the first ``n_agents`` of them are the run's.
       With ``pool`` above ``n_agents``, a small scenario takes a sample of a crowd at exact shares,
       rather than the same two kinds of person on every seed.
    5. With ``one_with``, the run's people are chosen from the shuffled crowd by
       :func:`one_with_people` in place of step 4's first ``n_agents``.

    Every draw comes from one random stream named by the profile and the seed, so the same profile
    and seed give the same people (``random.Random`` seeded with a string is the same on every
    platform and Python 3 run).
    """
    size = max(n_agents, pool or 0)
    rng = random.Random(f"{profile.name}:{seed}")
    people: list[dict[str, Any]] = []
    members: list[list[int]] = []
    counts = apportion(size, [w for _, _, male, female in profile.bands for w in (male, female)])
    for b, (start, end, _, _) in enumerate(profile.bands):
        members.append([])
        for gender, count in (("male", counts[2 * b]), ("female", counts[2 * b + 1])):
            for _ in range(count):
                members[b].append(len(people))
                people.append({"age": rng.randint(start, end), "gender": gender})
    for factor in profile.factors:
        expected = [len(members[b]) * factor.share(start, end) for b, (start, end, _, _) in enumerate(profile.bands)]
        wanted = [0] * len(expected)
        left, open_bands = _nearest(math.fsum(expected)), list(range(len(expected)))
        while left > 0 and open_bands:  # share out, capping a band at its size and sharing the rest again
            given = apportion(left, [expected[b] for b in open_bands])
            for b, extra in zip(open_bands, given):
                wanted[b] += extra
            over = [b for b in open_bands if wanted[b] > len(members[b])]
            left = sum(wanted[b] - len(members[b]) for b in over)
            for b in over:
                wanted[b] = len(members[b])
            open_bands = [b for b in open_bands if b not in over and wanted[b] < len(members[b])]
        for b, band in enumerate(members):
            chosen = set(rng.sample(band, wanted[b]))
            for person in band:
                people[person][factor.name] = factor.level if person in chosen else factor.other
    rng.shuffle(people)
    if one_with is not None:
        return one_with_people(people, n_agents, seed, one_with)
    return {k: people[k] for k in range(n_agents)}


def one_with_people(crowd: Sequence[dict[str, Any]], n_agents: int, seed: int, one_with: tuple[str, str]) -> dict[int, dict[str, Any]]:
    """Exactly one of the run's people at a factor's level (issue #124, RF-38; the user's decision of
    2026-10-31): a meeting that does happen in real life, so that a rule about a rare factor can be
    judged where it applies.

    From a crowd at exact shares, already shuffled: the person at the level is the crowd's first at it
    (so their age and other factors are as the profile gives them for such people, a cane mostly at
    65 and over), and the others are the crowd's first ``n_agents - 1`` not at it. The holder is agent
    ``seed % n_agents``, so in a pair the end that starts with the factor alternates by seed. No draw
    is added: the crowd and its random stream are those of :func:`quota_people` without ``one_with``.
    """
    name, level = one_with
    holders = [person for person in crowd if person[name] == level]
    others = [person for person in crowd if person[name] != level]
    if not holders:
        raise ConfigError(f"one_with {name}: {level}: nobody in this crowd of {len(crowd)} is at it; give a larger pool")
    if len(others) < n_agents - 1:
        raise ConfigError(f"one_with {name}: {level}: this crowd of {len(crowd)} has {len(others)} people not at it, "
                          f"{n_agents - 1} are needed; give a larger pool")
    chosen = others[:n_agents - 1]
    chosen.insert(int(seed) % n_agents, holders[0])
    return dict(enumerate(chosen))


def counts(people: Mapping[int, Mapping[str, Any]]) -> dict[str, int]:
    """How many of ``people`` are aged ``OLDER_FROM`` and over, and at each core factor's second
    level (a cane, a large suitcase, a phone, holding their ground, ...)."""
    out = {"n": len(people), f"age_{OLDER_FROM}_and_over": sum(p["age"] >= OLDER_FROM for p in people.values())}
    for name in FACTOR_ATTRIBUTES:
        level = ATTRIBUTES[name].levels[1]
        given = sum(p.get(name) == level for p in people.values())
        if any(name in p for p in people.values()):
            out[f"{name}_{level}"] = given
    return out
