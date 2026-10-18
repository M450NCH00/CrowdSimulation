# Q3. Lifts and escalators (a short pass)

> For issue [#37](https://github.com/M450NCH00/CrowdSimulation/issues/37), PT-3 of track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34). Read on 2026-10-18. The issue made
> Q3 conditional on budget after Q1, Q2 and Q4. **This is a short pass: two primary sources read,
> plus the Singapore escalator statistics already in [`singapore.md`](singapore.md). It is not a
> full review**; leads not followed are listed at the end.

Companion files: [verdict](verdict.md) · [reference behaviours](reference-behaviours.md) ·
[Singapore](singapore.md) · [search log](search-log.md)

---

## The short answer

- **Priority in lifts for wheelchairs and prams** has one good field study, from Taipei, the
  closest culture to Singapore read in this issue ([Huang-TaipeiLifts]). At four Taipei MRT
  transfer stations in the 2018 weekday morning peak, a lift trip needed someone to give way to a
  wheelchair, pram or walking-frame user in 89 of 604 trips (15%). **In those 89 trips, everyone
  gave way in 24%, some did in 27%, and nobody did in 49%.** People were more likely to give way
  when more people, and more high-need users, were waiting.
- **Who gets the last place in a lift** (among people without a need): no study found.
- **Standing and walking on escalators**: the one primary source read is London Underground's own
  report of a three-week pilot at Holborn in 2015 ([TfL-Holborn2016]). Asking people to stand on
  both sides raised capacity by about 30% on a 24 m escalator, **but people complied only while
  staff were there**, became less compliant after 09:00, and went back to standing on the right and
  walking on the left as soon as the tests ended.
- **Singapore**: escalator incident statistics only (BCA 2023; more than half of the bulky-item
  incidents involved users aged 55 and over). See [`singapore.md`](singapore.md).

---

## Entries

### [Huang-TaipeiLifts]: An Observation of Accessible Elevator Users in Taipei MRT System
- Authors / Year / Venue / Link: Huang, S. and Chang, K. (2022). 捷運技術 (*Journal of Rapid Transit
  System and Technology*), No. 57, pp. 15-40. doi:10.29670/JRTST.202210_(57).0002 (printed on the
  article's first page; resolves to the issue's e-book). Read on the journal's
  e-book site: https://ebook.dorts.gov.taipei/JRTST/ebook/no57/files/basic-html/page26.html
  (e-book pages 26-48; cached on disk only: `refs/he_huang2022_taipei_lifts.txt`).
- Status: published in the technical journal of Taipei's Department of Rapid Transit Systems; the
  authors are at the Institute of Transportation, Ministry of Transportation and Communications
  (p. 16). Received 27 May 2019, accepted 22 November 2019 (p. 16); whether it is peer-reviewed is
  not stated [unverified]. Read: full text (in Chinese; English abstract p. 16). Journal page =
  e-book page minus 10. The text read is
  the e-book's text layer, in which the two columns are interleaved; numbers were checked against
  Table 4 (p. 24).
- Scenario: lift.
- Study type: field observation (observers at the lift doors; no interviews; p. 23).
- Place, year of data collection, sample size: Taipei MRT, 10 platform lifts at four transfer
  stations (Taipei Main, Zhongxiao Xinsheng, Zhongshan, Minquan West Road; station codes in
  Table 4, p. 24, defined pp. 29-31); weekday morning peak 08:00-10:00, August to October 2018 (ROC year 107); 2 hours
  per lift, 20 hours in total; **2,413 users, 604 lift trips** (p. 23).
- How users were classed (Table 2, p. 22): *high need*: wheelchair, pram (娃娃車) or walking
  frame, who cannot use stairs or escalators; *medium need*: cane, luggage trolley or shopping
  cart; *low need*: everyone else. Classed by the observer's visual judgement (p. 23).
- What people did, with numbers:
  - In 89 of 604 trips (15%), a medium- or low-need user should have given way to a high-need user
    (Table 4, p. 24; p. 27).
  - In those 89 trips: **full yielding 21 (24%), partial yielding 24 (27%), no yielding 44 (49%)**
    (Table 4, p. 24; p. 27). The yielding pattern did not differ significantly between lifts
    (χ² = 18.486, p. 27).
  - High-need users had a 15% chance of having to wait for more than one lift (up to 30% at some
    lifts), against 6% for all users (p. 35; p. 26).
- What changed the behaviour: a logistic regression found that more people queueing at the lift,
  and more high-need users queueing, both raised the odds that others gave way (Table 6, p. 32).
  The authors note that priority waiting areas already exist at many stations, but crowds "often do
  not queue where planned" (p. 33, translated). Lifts serving three levels had longer waits
  (pp. 22, 33).
- Effects of age or gender reported: none (users classed by mobility, not age or gender).
- Limits stated: observers' subjective classification (p. 23); small sample of yielding situations,
  so full and partial yielding could not be modelled separately (p. 32); station transfer volumes
  and platform features not included (p. 35); limited to some Taipei stations (p. 35). **East Asian
  (Taipei), 2018, morning peak only.**
- Reference behaviours it supports: LE-1, LE-2 [inference].
- BibTeX: `huang2022observation`.

### [TfL-Holborn2016]: Report on Holborn Pilot for Standing on Both Sides of Escalators
- Authors / Year / Venue / Link: Harrison, C., Kukadia, N., Stoneman, P. and Dyer, G. (6 January
  2016). London Underground internal report, released under Freedom of Information request
  FOI-2015-1920 (redacted) `[official]`:
  https://foi.tfl.gov.uk/FOI-2015-1920/2015-1920-Report%20on%20Holborn%20Station%20Pilot_Redacted.pdf
  (cached on disk only: `refs/he_tfl2016_holborn.*`).
- Status: `[official]`, not peer-reviewed. Read: §§1-9 in full (pp. 1-32); appendices skimmed.
- Scenario: escalator.
- Study type: field experiment (a staffed pilot with counts, observers and CCTV; §5.3, p. 13).
- Place, year, sample: Holborn station, London Underground; escalators 5, 6 and 7, up from the
  platforms, vertical rise 24 m (p. 4, p. 7); three weeks of morning tests from 23 November 2015
  (p. 9); one escalator in week 1, two in week 2, three in week 3, with staff at the bottom
  encouraging people to stand on both sides (§5.5, p. 14); "an approximate 130,000 customers
  affected by the tests" (§8.3, p. 31).
- What people did, with numbers:
  - Capacity: comparing escalator 5 in week 2 (the only walking escalator) with week 3 (standing on
    both sides) showed "an approximate increase of 30%" (§8.2, p. 30).
  - Compliance: "the change was only effective while staff were present ... and produced no lasting
    change" (abstract, p. 2); "'normal' escalator usage resuming immediately that the tests were
    over" (§9, p. 32).
  - Resistance was highest on the first day of each week, and by week 3 most customers complied by
    Tuesday (§6.3, p. 19).
  - "Every day there was a noticeable change in customer behaviour after 9am, when customers became
    less compliant and less patient" (§6.3, p. 19).
  - "if customers stood side by side and talked, or held hands, customers behind them did not
    attempt to pass them" (§6.3, p. 19; §8.3, p. 31).
  - "those customers who really wanted to walk found a way to do so (some weaving between other
    customers on both sides of escalator)" (§6.3, p. 20).
- What changed the behaviour: staff presence (abstract; §9); time of day (§6.3); congestion:
  standing on both sides "was most effective when the mid-circulating area was congested" (§8.3,
  p. 31). The report cites Davis and Dutta (2002) that fewer people walk on taller escalators and
  that "Passengers will not stand on both sides of an escalator simply because they are asked to"
  (§4.2, pp. 7-8); that study was not read.
- Effects of age or gender reported: none measured. The report cites Davis and Dutta (2002) that
  "Non-commuters ... tend to stand rather than walk" (§4.2, p. 8).
- Limits: safety data "statistically insignificant" (abstract); a short, heavily staffed pilot with
  intense media attention (§8.3, p. 30); one station with tall escalators; the report itself warns
  that shorter escalators are more efficient when walking is allowed (§9, p. 32). **Western
  (London), 2015.**
- Reference behaviours it supports: LE-3, LE-4 [inference].
- BibTeX: `tfl2016holborn`.

---

## Leads not followed (for a later session)

- **Davis, P. and Dutta, G. (2002)**, the London Underground escalator capacity study cited in
  [TfL-Holborn2016] §4.2. Secondary sources give walking shares by escalator height that disagree
  with each other [unverified lead].
- **The 2016 six-month Holborn trial**: press reports give 151 against 115 passengers per minute
  (standing-only against walking-allowed); no TfL report on it was found [unverified lead].
- **Santiago Metro escalator pilot (2023)**, Universidad de los Andes repository
  (https://repositorio.uandes.cl/handle/uandes/59180): video-based study of standing and walking
  [unverified lead].
- **Delhi Metro escalator level-of-service study**, *European Journal of Transport and
  Infrastructure Research* (open access; https://journals.open.tudelft.nl/ejtir/article/download/7868/6472/34465):
  reports the share of people walking on escalators [unverified lead].
- **Cheung, C. Y. and Lam, W. H. K. (1998)**, *Journal of Transportation Engineering* 124(3), 277,
  on escalator-versus-stairs choice in Hong Kong MTR stations [unverified lead; the DOI appeared in
  a search result].
- **Lift "last place" behaviour**: no study found by the one search run; a dedicated search
  ("elevator crowding", "lift boarding order") was not done.
