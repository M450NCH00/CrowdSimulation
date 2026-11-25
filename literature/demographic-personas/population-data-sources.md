# B5 — Population composition sources (gender and age)

Prepared for issue [#16](https://github.com/M450NCH00/CrowdSimulation/issues/16), sub-area B5.
This is **data sourcing, not literature**. Companion files:
[`llm-demographic-effects.md`](llm-demographic-effects.md),
[`human-demographic-effects.md`](human-demographic-effects.md),
[`realism-vs-bias-comparison.md`](realism-vs-bias-comparison.md),
[`search-log.md`](search-log.md).

**Per the issue, no data is copied into this repository.** Only the source, publisher, date
and available breakdown are recorded. Every URL below was fetched and checked on
**2026-09-21**; what was checked is stated for each.

---

## Location scope assumption — stated explicitly, as the issue requires

**Assumption: Singapore.** `CLAUDE.md` states, under "Current task": *"Scope confirmed
2026-09-04: dataset is Singapore-only, organised by age group and gender
(`dataset/personas.yaml`)"*. The issue instructs that if `CLAUDE.md` does not state the
current scope, Singapore sources should be recorded and the scope question flagged. **It does
state it**, so the assumption is documented rather than open — but it is still an assumption
inherited from a September 2026 note, and it is repeated under "Open questions / risks" in
`WORK_LOG-16.md` because a change of scope would invalidate this entire file.

**A second, sharper scope question this sub-area surfaces** — and which the issue does not
pre-empt:

> **Whose population?** Singapore's *resident* population (citizens + PRs) and its *total*
> population differ substantially, because a large non-resident population lives and moves in
> the country. A crowd simulation of an MRT platform or a covered walkway models **everybody
> physically present**, not the citizenry. The sources below are therefore split by which
> universe they cover, and **the project must choose one deliberately**. Getting this wrong
> would misstate the age and sex mix of a simulated crowd regardless of how good the
> behavioural model is.

This matters concretely for `dataset/scenarios.yaml`, whose scenarios (`mrt_door_alight_board`,
`bus_queue_boarding`, `covered_walkway_walking`) are public-space settings where the
non-resident share is not negligible.

---

## Primary source 1 — SingStat, *Singapore Residents By Age Group, Ethnic Group And Sex*

| Field | Value |
|---|---|
| **Publisher** | Singapore Department of Statistics (SingStat) |
| **Distributed via** | data.gov.sg, dataset ID `d_3cf667d761b4bdc6d4d3d3aeec37dea5` |
| **Dataset title (verbatim)** | "Singapore Residents By Age Group, Ethnic Group And Sex, At End June, Annual" |
| **Coverage** | 1957 → 2025 |
| **Data last updated** | 29/09/2025 (stated in the dataset description) |
| **Update frequency** | Annual |
| **Universe** | **Residents** — citizens and permanent residents only |
| **Breakdown available** | age group × ethnic group × sex, annual, at end-June |
| **Underlying SingStat table** | M810011 |
| **How verified** | Metadata fetched from the data.gov.sg v2 API and cached at `refs/dg_d_3cf667d761b4bdc6d4d3d3aeec37dea5.json`; title, coverage dates and description read from that record. |

**Footnote the dataset itself carries, and which affects any crowd model:** *"Data from 2003
onwards exclude residents who are overseas for a continuous period of 12 months or longer as at
the reference period."*

**Fitness for this project:** this is the natural source for an age × sex distribution, and its
age-group bands are the ones `dataset/personas.yaml`'s bands would have to be mapped onto.
**It excludes non-residents**, so on its own it does not describe a Singapore street crowd.

---

## Primary source 2 — SingStat, *Total Population By Broad Age Group And Sex*

| Field | Value |
|---|---|
| **Publisher** | Singapore Department of Statistics (SingStat) |
| **Distributed via** | data.gov.sg, dataset ID `d_6c26f6181f2e5dd62bf3210fa1029074` |
| **Dataset title (verbatim)** | "Total Population By Broad Age Group And Sex, At End June, Annual" |
| **Coverage** | 1957 → 2025 |
| **Universe** | **Total population** — includes non-residents |
| **Breakdown available** | broad age group × sex, annual, at end-June |
| **How verified** | Metadata fetched from the data.gov.sg v2 API, cached at `refs/dg_d_6c26f6181f2e5dd62bf3210fa1029074.json`. |

**Fitness:** the right *universe* for a public-space crowd, but only **broad** age groups —
coarser than source 1. [inference] The likely practical answer is to take the age × sex shape
from source 1 and re-weight it against the total-population totals here, and to say so
explicitly in the report rather than silently using one or the other.

---

## Primary source 3 — SingStat, *Singapore Residents By Single Year Of Age And Sex*

| Field | Value |
|---|---|
| **Publisher** | Singapore Department of Statistics (SingStat) |
| **Distributed via** | data.gov.sg, dataset ID `d_4bd9ffc2595acd61fd1a7f642caf8f36` |
| **Dataset title (verbatim)** | "Singapore Residents By Single Year Of Age And Sex, At End June, Annual" |
| **Coverage** | 1980 → 2025 |
| **Universe** | Residents |
| **Breakdown available** | **single year of age** × sex, annual |
| **How verified** | Metadata fetched from the data.gov.sg v2 API, cached at `refs/dg_d_4bd9ffc2595acd61fd1a7f642caf8f36.json`. |

**Fitness:** the finest age resolution available, and therefore the source to use if the
simulation ever needs to sample a continuous age rather than a band — for example to give each
of 10,000 agents an individual walking speed from an age–speed curve, rather than one of five
band-averaged speeds. [inference] Given that the project's stated end goal is 10,000 agents,
band-averaging is a real loss of variety, and this dataset removes that constraint at no cost.

---

## Primary source 4 — SingStat, *Singapore Residents By Planning Region, Age Group And Sex*

| Field | Value |
|---|---|
| **Publisher** | Singapore Department of Statistics (SingStat) |
| **Distributed via** | data.gov.sg, dataset ID `d_3c4dc32382bdc23189428af2126dd188` |
| **Dataset title (verbatim)** | "Singapore Residents By Planning Region, Age Group And Sex, End June, Annual" |
| **Coverage** | 2019 → 2025 |
| **Universe** | Residents |
| **Breakdown available** | **planning region** × age group × sex, annual |
| **How verified** | Metadata fetched from the data.gov.sg v2 API, cached at `refs/dg_d_3c4dc32382bdc23189428af2126dd188.json`. |

**Fitness:** the only *spatial* breakdown of the four. [inference] This is the source that would
let the project answer a question a supervisor is likely to ask — *whose crowd is this?* — since
the age mix at a town-centre walkway in a mature estate differs from one in a young town. It is
not needed for Phase 1, but it is the natural route from "a generic Singapore crowd" to "a
named, defensible location", and worth recording now.

---

## Primary source 5 — *Population in Brief 2025*

| Field | Value |
|---|---|
| **Title** | Population in Brief 2025 |
| **Publishers (verbatim, "A JOINT PUBLICATION BY:")** | National Population and Talent Division, Strategy Group, Prime Minister's Office; Singapore Department of Statistics; Ministry of Home Affairs; Immigration & Checkpoints Authority; Ministry of Manpower |
| **Date** | **September 2025**, with the note "Data are accurate at time of publication" |
| **Frequency** | Annual |
| **URL** | `https://www.population.gov.sg/files/media-centre/publications/Population_in_Brief_2025.pdf` |
| **Breakdown available** | Annex Table 2 "Singapore citizens by age group, ethnic group and sex" (p. 23); Table 6 "Median age" (p. 25); Table 1 "Total population" (p. 22); plus sections on Overall Population, Longevity, Marriage & Parenthood, Immigration |
| **Universe** | Primarily **citizens**, with total-population and resident/non-resident splits in the Overall Population section |
| **How verified** | PDF downloaded and read; cached at `refs/b5_population_in_brief_2025.pdf` with text extract `refs/b5_pib.txt`. Publisher list, date and table titles quoted from the document itself (contents pp. 2–3; publisher block at the end). |

**Fitness:** the best single **citable** source for a report — a short, official, annual
publication with a stable citation, as opposed to a raw dataset. It is the right thing to cite
in the FYP write-up; the data.gov.sg datasets above are the right things to compute from.

⚠ **Caution about its universe:** its annex tables are largely **citizen**-based, which is a
*third* universe, narrower still than residents. Citizens ≠ residents ≠ total population.

---

## Also checked

- **SingStat Table Builder, table M810011** — `https://tablebuilder.singstat.gov.sg/table/TS/M810011`
  returned HTTP 200 on 2026-09-21. This is the interactive front-end for the same series as
  primary source 1. Recorded for completeness; the data.gov.sg API is the better programmatic
  route.
- **`https://www.population.gov.sg/library/population-in-brief/`** — ⚠ **do not use.** This URL
  returns **HTTP 200 but renders a "The requested page could not be found" page** (a soft 404).
  It is recorded here as a warning, because a link-checker that only tests status codes will
  pass it. The working path is the direct PDF URL in primary source 5.

## Not checked, and why

- **Census of Population 2020** (SingStat) — the decennial census would give the richest
  breakdown, but it was **not** opened and verified in this pass, so it is not recorded as a
  source. It should be added if a finer or historical breakdown is needed.
- **Location-specific footfall data** (e.g. LTA ridership by station) — would describe who is
  actually present at a scenario location rather than who lives in the country. Out of scope
  for B5 as the issue defines it, but noted as the obvious next step if a specific site is
  chosen.

---

## What this means for `run01` — and one thing it does not

`dataset/personas.yaml` organises the dataset by age band and gender, and `run01` generated
records per persona. **Nothing in this sub-area validates or invalidates the *behaviour* in
those records** — population composition tells you how many of each kind of agent to create,
not how they act.

Two consequences worth stating plainly:

1. **Composition and behaviour are separate problems, and only one of them is solved by data.**
   The sources above settle the mix completely and uncontroversially. The behaviour is where
   all the uncertainty documented in
   [`realism-vs-bias-comparison.md`](realism-vs-bias-comparison.md) lives. [inference] It is
   worth separating these explicitly in the report, because a reader can otherwise mistake a
   well-sourced population mix for evidence that the behaviour is well-sourced too.
2. **A demographically accurate crowd built on a demographically wrong behaviour model is
   worse than a uniform one**, not better — it applies the suspect gender and age effects to
   the right number of agents, which makes the error systematic rather than random.
   [inference] This is an argument for keeping the population weighting *configurable and
   switchable off*, so a uniform-behaviour control run is always available as a baseline.
