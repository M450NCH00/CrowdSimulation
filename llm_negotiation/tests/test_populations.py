"""Issue #112 (RF-33): population profiles and the generator of exact shares."""

from __future__ import annotations

import copy
import json

import pytest

from negsim import populations as P
from negsim.configutil import PACKAGE_ROOT, ConfigError, load_yaml
from negsim.rules.database import file_sha256
from negsim.rulegen.replay import mixed_population

STREET = P.POPULATIONS_DIR / "singapore_street_v1.yaml"
STRESS = P.POPULATIONS_DIR / "stress_all_factors_v1.yaml"
REFS = PACKAGE_ROOT.parent / "refs"
#: The profiles are frozen: a change is a new file (pinned when each was written, issue #112).
FROZEN = {
    "singapore_street_v1.yaml": "dfd92225553c999a2b5de0400489d100daba6d5fc88900e59860171bfe8b8045",
    "stress_all_factors_v1.yaml": "1537734fdec24340ff11a4ebf428f7f6d0425cc0a7fef63b2da5f2cf92cf814b",
}


@pytest.fixture(scope="module")
def street():
    return P.Profile.load(STREET)


@pytest.fixture(scope="module")
def stress():
    return P.Profile.load(STRESS)


# --- the largest-remainder method -----------------------------------------------------------------


def test_apportion_gives_exact_totals_and_breaks_ties_by_order():
    assert P.apportion(10, [1, 1, 1]) == [4, 3, 3]
    assert P.apportion(100, [0.5, 0.25, 0.25]) == [50, 25, 25]
    assert P.apportion(3, [1, 0, 0]) == [3, 0, 0]
    for total in range(0, 40):
        assert sum(P.apportion(total, [3, 7, 11, 0.5])) == total
    assert P.apportion(5, [0, 0]) == [0, 0]


# --- the realistic profile: every share sourced ---------------------------------------------------


def test_the_street_profile_is_realistic_and_every_share_names_a_listed_source(street):
    assert (street.name, street.purpose, street.generator) == ("singapore_street_v1", P.REALISTIC, P.QUOTAS)
    for factor in street.factors:
        for _, _, _, source in factor.by_age:
            assert source in street.sources
    assert P.PLACEHOLDER in street.sources and "[placeholder]" in street.sources[P.PLACEHOLDER]["cite"]
    for name, source in street.sources.items():
        if "cached" in source:  # every cached source is in refs/
            assert (PACKAGE_ROOT.parent / source["cached"]).is_file(), name


def test_the_street_profile_age_bands_are_singstats_counts_word_for_word(street):
    table = json.loads((REFS / "rf33_singstat_M810011_2026.json").read_text(encoding="utf-8"))["Data"]["row"]
    by_text = {}
    for row in table:
        series = row["seriesNo"].split(".")[0]
        if series in ("2", "3") and "." in row["seriesNo"]:  # total male, total female residents by band
            by_text.setdefault(row["rowText"], {})[series] = int(row["columns"][0]["value"])
    for start, end, male, female in street.bands:
        text = "90 Years & Over" if start == 90 else f"{start} - {end} Years"
        assert (male, female) == (by_text[text]["2"], by_text[text]["3"]), text


def test_the_street_profile_shares_are_the_sources_numbers(street):
    shares = {f.name: {(a, b): s for a, b, s, _ in f.by_age} for f in street.factors}
    # Gell et al. 2015, Table 2, cane by age (NHATS 2011)
    assert [shares["mobility_aid"][k] for k in ((65, 69), (70, 74), (75, 79), (80, 84), (85, 89), (90, 94))] == [0.086, 0.116, 0.163, 0.237, 0.325, 0.366]
    # Fernández et al. 2020, Table 3, smombie by age (Elche 2019)
    assert [shares["distraction"][k] for k in ((10, 19), (20, 34), (35, 64), (65, 94))] == [0.146, 0.193, 0.064, 0.017]
    # the user's placeholders of 2026-10-27
    assert shares["mobility_aid"][(10, 64)] == 0.005 and shares["load"][(10, 94)] == 0.01 and shares["assertiveness"][(10, 94)] == 0.5
    assert street.expected() == {"age_65_and_over": 0.2128, "mobility_aid_cane": 0.0355, "distraction_phone": 0.0892,
                                 "load_large_suitcase": 0.01, "assertiveness_holds_ground": 0.5}


def test_the_profiles_are_frozen():
    for name, sha in FROZEN.items():
        assert file_sha256(P.POPULATIONS_DIR / name) == sha
    assert sorted(path.name for path in P.POPULATIONS_DIR.glob("*.yaml")) == sorted(FROZEN)


# --- the generator of exact shares (task 3) -------------------------------------------------------


@pytest.mark.parametrize("n", [100, 37, 1000])
def test_quota_people_have_the_exact_shares_on_every_seed(street, n):
    expected = street.expected()
    cells = P.apportion(n, [w for _, _, m, f in street.bands for w in (m, f)])  # by band and sex
    older = sum(cells[2 * b] + cells[2 * b + 1] for b, band in enumerate(street.bands) if band[0] >= 65)
    assert abs(older - n * expected["age_65_and_over"]) <= 2
    for seed in (30901, 30902, 7):
        counts = P.counts(street.people(n, seed))
        assert counts["n"] == n
        assert counts["age_65_and_over"] == older
        for key in ("mobility_aid_cane", "distraction_phone", "load_large_suitcase", "assertiveness_holds_ground"):
            assert abs(counts[key] - n * expected[key]) <= 1, (n, seed, key)


def test_quota_people_by_sex_and_band_are_exact(street):
    people = street.people(100, 30901)
    wanted = P.apportion(100, [w for _, _, m, f in street.bands for w in (m, f)])
    for b, (start, end, _, _) in enumerate(street.bands):
        in_band = [p for p in people.values() if start <= p["age"] <= end]
        assert sum(p["gender"] == "male" for p in in_band) == wanted[2 * b]
        assert sum(p["gender"] == "female" for p in in_band) == wanted[2 * b + 1]


def test_quota_people_are_deterministic_and_differ_from_seed_to_seed(street):
    assert street.people(100, 30901) == street.people(100, 30901)
    assert street.people(100, 30901) != street.people(100, 30902)
    # every person has age, gender and each factor at one of its two levels
    for person in street.people(100, 30901).values():
        assert set(person) == {"age", "gender", "mobility_aid", "distraction", "load", "assertiveness"}
        assert 10 <= person["age"] <= 94


def test_a_cane_goes_mostly_to_older_people(street):
    canes = [p["age"] for p in street.people(10000, 1).values() if p["mobility_aid"] == "cane"]
    assert len(canes) == 355 and sum(age >= 65 for age in canes) / len(canes) > 0.85


def test_a_small_scenario_takes_the_first_people_of_a_pool(street):
    pool = street.people(100, 30905)
    assert street.people(2, 30905, pool=100) == {0: pool[0], 1: pool[1]}
    # without a pool, two people are always from the two largest cells
    pairs = {tuple((p["age"] // 5, p["gender"]) for p in street.people(2, seed).values()) for seed in range(30901, 30911)}
    assert all(gender == "female" for pair in pairs for _, gender in pair)
    pooled = {tuple((p["age"], p["gender"]) for p in street.people(2, seed, pool=100).values()) for seed in range(30901, 30911)}
    assert len(pooled) == 10


def test_the_stress_profile_gives_rf18s_people(stress):
    rf18 = load_yaml(PACKAGE_ROOT / "configs" / "rule_set_evaluation" / "rf18_round1.yaml")["people"]
    assert (stress.purpose, stress.generator) == (P.STRESS, P.CYCLE)
    assert stress.people(100, 30901) == mixed_population(100, rf18["ages"], rf18["genders"], rf18["factors"])
    assert stress.people(2, 30901, repeat=3, rotate=True) == {k: mixed_population(4, rf18["ages"], rf18["genders"], rf18["factors"])[2 + k] for k in range(2)}
    assert P.counts(stress.people(100, 1)) == {"n": 100, "age_65_and_over": 50, "mobility_aid_cane": 48, "load_large_suitcase": 48,
                                               "distraction_phone": 48, "assertiveness_holds_ground": 36}


# --- refusals -------------------------------------------------------------------------------------


def raw_street():
    return load_yaml(STREET)


@pytest.mark.parametrize("change, match", [
    (lambda r: r.update(purpose="typical"), "purpose"),
    (lambda r: r.update(limits=[]), "limits"),
    (lambda r: r["factors"]["mobility_aid"]["by_age"][1].update(source="nowhere"), "not under 'sources'"),
    (lambda r: r["factors"]["mobility_aid"]["by_age"][1].update(share=1.5), "share"),
    (lambda r: r["factors"].update(ethnic_group={"level": "malay", "by_age": []}), "not a core factor"),
    (lambda r: r["factors"]["mobility_aid"].update(level="walker"), "level"),
    (lambda r: r["factors"]["distraction"]["by_age"].__setitem__(0, {"ages": [10, 17], "share": 0.1, "source": "fernandez2020_elche"}), "exactly one row"),
    (lambda r: r["age"]["bands"].pop(3), "follow on"),
    (lambda r: r["age"].update(source="nowhere"), "not under 'sources'"),
])
def test_a_bad_profile_is_refused(change, match):
    raw = copy.deepcopy(raw_street())
    change(raw)
    with pytest.raises(ConfigError, match=match):
        P.Profile.from_mapping(raw, "test")


def test_a_realistic_profile_cannot_be_a_cycling_mix():
    raw = load_yaml(STRESS)
    raw["purpose"] = P.REALISTIC
    with pytest.raises(ConfigError, match="realistic profile gives sourced shares"):
        P.Profile.from_mapping(raw, "test")
