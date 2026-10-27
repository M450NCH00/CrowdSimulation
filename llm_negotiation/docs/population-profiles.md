# Population profiles: who is in a simulated crowd (issue #112, RF-33)

**Status: draft, session 1 of 2.** Section 2 (the sources) is done. The profile files, the
generator and the config keys follow once the user has decided the questions in section 4.

RF-18's crowd gave people their factors by cycling each factor's levels
(`negsim.rulegen.replay.mixed_population`), so every factor sits at exactly half: half the crowd is
70, half carries a cane, half pulls a large suitcase, half looks at a phone. The user decided on
2026-10-27 to **simulate realistic scenarios wherever possible, and keep scenarios with exaggerated
shares only to test rules that would rarely apply in a normal one.** A profile says what share of
the crowd has each level of each factor, and where each share comes from.

## 1. What needs a share

Only what a rule can read: `age`, `gender`, and the visible core factors `mobility_aid` (none,
cane), `load` (none, large_suitcase) and `distraction` (none, phone); in rule format 4's own-only
conditions, also a person's own unobservable factors (`assertiveness`, `urgency`, `residence`,
`memory_note`). In the avoidance simulator none of these changes a body or a speed, so a share
matters only through the rules that read it. Real ethnicity is read by no rule and is not part of
a profile.

## 2. The sources

Every source was read on 2026-10-27 and is cached in `refs/` (repo root). A share with no source
is marked **[placeholder]**.

### 2.1 Age and gender: SingStat, residents at end-June 2026

Singapore Department of Statistics, *Singapore Residents By Age Group, Ethnic Group And Sex, At End
June, Annual* (table M810011), data last updated 2026-09-25, read through the SingStat Table
Builder API (`tablebuilder.singstat.gov.sg/api/table/tabledata/M810011?timeFilter=2026`), cached
as `refs/rf33_singstat_M810011_2026.json`. Five-year bands to 85–89, then 90 and over, by sex.

- **Measured:** a count of all residents (citizens and permanent residents), excluding those
  overseas for 12 months or more (the table's footnote). 4,231,524 residents.
- Aged 65 and over: 825,322 (19.5% of residents; 21.3% of those aged 10 and over).
- Male share by band: 51.2% at 10–14, 47.1% at 40–44, 46.1% at 75–79, 31.7% at 90 and over.

**Limits.**
- **Residents only:** 4.23 of 6.21 million people at end-June 2026 (`refs/rf26_singstat_population_trends_2026.txt`).
  The total population comes only in broad bands (issue #16, `literature/demographic-personas/population-data-sources.md`).
- **Who lives here is not who is out walking.** Two street counts show the observed mix differs
  from the census: Elche (2.3) saw 15.9% aged over 65, the four Chinese cities (2.3) 12.4% over 60.
  No Singapore count of pedestrians by age was found.

### 2.2 A cane, by age: NHATS 2011 (United States)

Gell NM, Wallace RB, LaCroix AZ, Mroz TM, Patel KV (2015). Mobility device use in older adults and
incidence of falls and worry about falling: findings from the 2011–2012 National Health and Aging
Trends Study. *Journal of the American Geriatrics Society*. doi:10.1111/jgs.13393. Full text from
PMC4439269 (NCBI E-utilities), cached as `refs/rf33_gell2015_nhats_mobility_devices.xml`.

- **Measured:** in-person interviews at home of a nationally representative sample of US Medicare
  beneficiaries aged 65 and over living in the community (n = 7,609), 2011: "used a cane in the
  last month". Table 2:

| Age | 65–69 | 70–74 | 75–79 | 80–84 | 85–89 | 90+ |
| --- | --- | --- | --- | --- | --- | --- |
| Cane (%) | 8.6 | 11.6 | 16.3 | 23.7 | 32.5 | 36.6 |

  Men 14.0%, women 18.3% (all 65+). Any cane: 16.4% of all aged 65 and over.
- At Singapore's 2026 age mix this gives **14.8% of residents aged 65 and over, 3.2% of a crowd
  aged 10 and over**.

**Limits.**
- **The United States, not Singapore.** No Singapore figure for walking-aid use was found (searched:
  the National Survey of Senior Citizens, the Singapore Longitudinal Ageing Study; the nearest is a
  pooled 20.8% "limitations in locomotion" among community-dwelling older Singaporeans).
- **"In the last month", not "on this street now".** Overstates a cane in hand at one moment, and
  people who need a cane may go out less; the two errors push in opposite directions.
- **Under 65: [placeholder].** NHATS covers 65 and over only. NHIS 1994 (US, National Center for
  Health Statistics, *Number of persons using assistive technology devices*, Table 1b, cached as
  `refs/rf33_nhis1994_assistive_devices_tb1.htm`) counts cane users, in thousands, as 434 aged 44
  and under, 1,116 aged 45 to 64, 3,212 aged 65 and over. These are counts without the population
  they are out of (the report's rate table is not archived), so no rate is taken from them; they
  show that under-65 use is not zero.

### 2.3 Looking at a phone: Elche 2019 (Spain), on the street

Fernández C, Vicente MA, Carrillo I, Guilabert M, Mira JJ (2020). Factors Influencing the
Smartphone Usage Behavior of Pedestrians: Observational Study on "Spanish Smombies". *Journal of
Medical Internet Research* 22(8):e19350. doi:10.2196/19350. Full text from Europe PMC
(PMC7455880), cached as `refs/rf33_fernandez2020_elche_smombies.xml`.

- **Measured:** 3,301 pedestrians **walking on the street** in Elche, Spain (a city of 230,000),
  each recorded once by an observer, in 43 sessions on working days at midday (12:00–14:00) and
  evening (19:00–21:30) rush hours, July to November 2019; city centre, residential areas and a
  university campus. Groups of more than four, cyclists, people standing still and people at work
  were excluded. Each person's most problematic use was recorded: not visible, talking, headphones,
  holding, or **"smombie" (looking at the screen)**. `distraction: phone` (looking at a phone,
  which narrows what a person sees) is the "smombie" level; holding a phone is not.

| | 10–18 | 18–35 | 35–65 | over 65 | city centre | all |
| --- | --- | --- | --- | --- | --- | --- |
| Smombie (%) | 14.6 | 19.3 | 6.4 | 1.7 | 8.3 | 10.9 |

  Bands as published (18 and 35 sit in two). At Singapore's 2026 age mix: **8.9% of a crowd aged
  10 and over**.

**Cross-check, an Asian city:** Hao, Wang, Zhou, Yi et al. (2022), *International Journal of Public Health*,
doi:10.3389/ijph.2022.1604601, cached as `refs/rf33_hao2022_china_smombies.xml`: 13,086 pedestrians
**crossing** at intersections in four Chinese cities (Changchun, Lanzhou, Zhuzhou, Luzhou), 2020,
without intervention; 4,289 (32.8%) used a smartphone in any way (talking, earphones, holding,
looking), 42.4% at 11–25 and 8.4% over 60. Any use while crossing a road is a wider category than
looking at a screen on a pavement, so it is not used as the share; it says a Singapore share could
be higher than Elche's.

**Considered and not used:** Chen and Pai (2018), Taipei, *BMC Public Health* 18:1342
(`refs/rf33_chen2018_taipei_smartphone.pdf`, `.txt`): the interviewed sample was chosen to compare
users with non-users (2,215 against 341), so it gives no share.

**Limits.** Spain, 2019, rush hours on working days. No Singapore count was found.

### 2.4 A large suitcase: [placeholder]

No count of the share of pedestrians pulling a suitcase was found for any street or station (searched:
station capacity guidance, airport-terminal luggage adjustments, platform counts). Leads not
followed up: platform luggage counts in a TU Wien thesis (Germany and Austria, 2007), and a
watch-and-trace survey at Shinagawa Shinkansen station (both would need the full text). It
clearly depends on the place: near zero on a residential street, more at an MRT interchange, most
at the airport. **[placeholder]** for every profile.

### 2.5 The unobservable factors: no population share exists

`assertiveness` (gives way, holds ground), `urgency`, `residence` and `memory_note` are designed
contrasts of Step 1, not counted traits. `residence: visitor` could be sourced (visitor arrivals
against the population), the others not. **[placeholder]** wherever a profile gives them.

## 3. What a sourced street crowd looks like

At the shares above (people aged 10 and over), a crowd of 100 has about **21 aged 65 and over**,
**3 with a cane** and **9 looking at a phone**, against 50 of each in RF-18's crowd. A large
suitcase is a placeholder.

## 4. Open for the user (before the build)

1. **Whose crowd:** SingStat residents (Singapore, fine bands, residents only), or the observed
   street age mix of Elche (who is out walking, but Spain)?
2. **The youngest:** count from 10, as Elche's observers did (younger children mostly walk with an
   adult and are not alone in an encounter), or from 0?
3. **The placeholders:** a cane under 65, a large suitcase on a street, and assertiveness: which
   values, or leave a factor out of the realistic profile.
4. **Small numbers:** at 3% a crowd of 100 has 3 people with a cane, so a cane rule applies rarely
   and its verdict over 10 seeds may be "not used" or "no change". Is that the intended reading
   (the user's decision: a stress scenario tests whether the rule works where it applies)?
