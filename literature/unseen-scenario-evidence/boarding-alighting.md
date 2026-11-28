# Q2. Boarding and alighting at train and bus doors

> For issue [#37](https://github.com/M450NCH00/CrowdSimulation/issues/37), PT-3 of track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34). Literature only. Read on
> 2026-10-18. Grades are defined in [`reference-behaviours.md`](reference-behaviours.md) §1 (a
> **proposal**). As the issue requires, only field observations and controlled experiments count
> as human evidence; simulation papers count only for the field data they cite.

Companion files: [verdict](verdict.md) · [reference behaviours](reference-behaviours.md) ·
[queue cutting](queue-cutting.md) · [Singapore](singapore.md) · [search log](search-log.md) ·
[missing papers](missing-papers.md)

---

## The short answer

- **Do people let others off first?** Mostly, but not cleanly. In the London lab mock-up,
  "alighting occurs first than boarding", and boarders "give way to those who are alighting or wait
  for a gap" ([Seriani-BARatio] §4.2). But when boarders outnumber alighters four to one, boarding
  starts earlier and alighters are squeezed into a single narrow lane (§§4.2-4.3). In real London
  Underground footage, boarding and alighting **overlap** at the door, and the overlap grows with
  demand ([Seriani-PEDsLondon], Figure 4).
- **How is the door shared?** Boarders wait **beside** the doors (queues at the sides) as well as
  in front of them; platform edge doors increase waiting beside the doors at low and high demand
  ([Seriani-PEDsLondon], Figure 3 and Discussion). Alighters form one or two lanes through the door
  depending on how crowded the platform is ([Seriani-BARatio] §4.3: 8% of alighters in two lanes
  when boarders outnumber alighters 4:1; 38% when alighters outnumber boarders 4:1).
- **Boarding without waiting.** Two field studies of exactly this ("non-compliance" in Hong Kong
  and mainland China; Paris-region railway stations) exist but could not be opened (stubs below).
  **No usable number for how often boarders push in before alighting ends was obtained.** This is
  the biggest gap in Q2.
- **Crowding.** In London peak hours, at one door, people chose to wait for the next train after
  22% of trains (135 of 615) ([Seriani-PEDsLondon], "Observed behaviour frequencies"). The two
  lab studies **disagree** about whether a crowded carriage slows boarding: one finds door flow
  starts to fall above about 4 passengers/m² inside ([Seriani-BARatio] §4.4); the other finds the
  boarding rate rising up to 2.5-3.0 passengers/m² and no clear fall up to about 5
  ([Luangboriboon-Density], abstract and §§4-5).
- **Markings and staff.** Across a worldwide survey dataset of over 6,000 station stops, a 1-5
  score of "management action" (staffing, platform markings, barriers) was not a significant
  predictor of passenger movement rates ([Harris-Rates] §3.4, p. 74). This is about speed, not
  order; it does not say markings fail to change who goes first.
- **Buses**: no field or controlled study of bus boarding *order* was obtained. Two Singapore bus
  studies are stubbed (see [`singapore.md`](singapore.md)). The only bus-queue data read are 8
  queue-intrusion trials at the Port Authority bus boarding queue in New York, 1978
  ([Brintzenhofe-MilgramRevisited] Table 3.3, p. 72, in [`queue-cutting.md`](queue-cutting.md)).
- **Age and gender**: participants' ages and genders are reported, but no study read analyses
  behaviour by age or gender.

---

## Entries

### [Seriani-PEDsLondon]: Combined Effect of Platform Edge Doors and Level Access on the Boarding and Alighting Process in the London Underground
- Authors / Year / Venue / Link: Seriani, S., de Ana Rodríguez, G. and Holloway, C. (2017).
  *Transportation Research Record* 2648(1), 60-67. doi:10.3141/2648-07 (Crossref). Copy read:
  the authors' submitted manuscript dated 30 July 2016, UCL Discovery,
  https://discovery.ucl.ac.uk/10068152/ (cached on disk only: `refs/he_seriani2017_peds_lu.*`).
- Status: published (peer-reviewed). Read: full text of the submitted manuscript. **Locators are
  to the manuscript's page numbers and headings**; the published version may differ.
- Scenario: boarding and alighting (metro).
- Study type: field observation (video footage under normal operation).
- Place, year of data collection, sample size: London Underground, Jubilee line southbound;
  Westminster (platform edge doors, two double doors, November 2014) and Green Park (no platform
  edge doors, one double door on a level-access platform hump, 23 November to 7 December 2015),
  weekday peaks 08:15-09:15 and 17:15-18:15 (Methods, pp. 4-5). 615 trains at Green Park
  ("Observed behaviour frequencies", p. 7); Table 2 (p. 7) lists 609 observations at Green Park and
  1,703 at Westminster. Doors 1.60 m wide (p. 5).
- What people did, with numbers:
  - **Waiting for the next train**: after 22% of trains (135 of 615) at Green Park, passengers
    "preferred to stand on the platform and wait for the next service"; the authors cannot tell
    whether because of crowding or destination (p. 7).
  - **Queues beside the doors**: "Queues beside the doors help passengers alight, reducing the
    conflict at the PTI" (p. 7, Figure 2).
  - **Lanes**: in the circulation space behind the waiting passengers, "passengers form flow lanes
    to avoid collisions with people coming in the opposite direction" (p. 7).
  - **Overlap** of boarding and alighting at the door exists at both stations and grows with total
    demand; with more than 25 passengers, overlap time differs by up to 4 s and overlapping
    passengers by up to 6 between the stations (Overlap, pp. 8-9, Figure 4). The figure's values
    are not given in the text [unverified beyond the text].
  - With platform edge doors, boarding peaks later, "probably due to people giving way to
    alighters" (p. 6; the authors' interpretation).
- What changed the behaviour: platform edge doors "encourage passengers to wait beside the doors"
  at low (under 15) and high (over 25) numbers of boarders, but not at medium (Discussion, p. 9;
  Figure 3, p. 8); "demand ... is more important on the BAT and passenger behaviours than the
  presence of PEDs" (abstract).
- Effects of age or gender reported: none.
- Limits stated: descriptive statistics only, "without formal statistical significance tests"
  (p. 5); on-train
  demand comes from a separate, coarse dataset (p. 7); the stations' boarder-alighter ratios
  differ by 63% (p. 9). **Western (London), 2014-2015, two
  platforms.**
- Reference behaviours it supports: BA-1 (supporting), BA-3, BA-4, BA-5 [inference].
- BibTeX: `seriani2017combined`.

### [Seriani-BARatio]: Exploring the Effect of Boarding and Alighting Ratio on Passengers' Behaviour at Metro Stations by Laboratory Experiments
- Authors / Year / Venue / Link: Seriani, S., Fernandez, R., Luangboriboon, N. and Fujiyama, T.
  (2019). *Journal of Advanced Transportation* 2019, Article 6530897 (12 pp.).
  doi:10.1155/2019/6530897 (Crossref). Copy read: the accepted manuscript on UCL Discovery,
  https://discovery.ucl.ac.uk/10073126/ (the published article is open access; cached:
  `refs/he_seriani2019_ratio_am.*`).
- Status: published (peer-reviewed). Read: full text of the accepted manuscript. Locators are
  section numbers.
- Scenario: boarding and alighting (metro).
- Study type: controlled experiment (full-scale mock-up of a next-generation London Underground
  carriage and platform at UCL's PAMELA laboratory).
- Place, year of data collection, sample size: London (PAMELA); year not stated in the manuscript
  [unverified]. 110 participants, 46% men and 54% women, 78% regular London Underground users;
  ages: 15% under 24, 26% 25-34, 19% 35-44, 27% 45-59, 7% 60-64, 7% over 65 (§3.2). Boarders
  wore red hats, alighters white; participants were told to walk "naturally" (§3.2). Boarder to
  alighter ratios R = 4, 1 and 0.25 under crowded and non-crowded platform conditions (§3.1,
  Table 1).
- What people did, with numbers:
  - "alighting occurs first than boarding, i.e. passengers on the platform give way to those who
    are alighting or wait for a gap in space to board the train" (§4.2). **The manuscript's
    abstract says the opposite ("In most cases boarding is first, and passengers compete for
    space")**; the body (§§4.2, 4.4) supports alighting first, with boarding starting earlier
    when R = 4. The published abstract was not checked [unverified].
  - With R = 4 (40 boarders, 10 alighters), boarding started earlier; with R = 0.25, boarders
    "almost wait until alighting was finished" (§4.2).
  - Lanes of alighters: R = 4, 12 of 152 alighters (8%) used two lanes; R = 0.25, 179 of 471 (38%)
    (§4.3).
  - Density inside the train at R = 4 (crowded): door flow rose to 1.38 passengers/s at about
    4.03 passengers/m² inside, then fell (§4.4); closing doors at that point would leave 22% of
    boarders for the next train (§4.4).
- What changed the behaviour: the boarder-alighter ratio (§§4.2-4.3) and crowding on the platform
  and in the carriage (§4.4).
- Effects of age or gender reported: demographics are reported (§3.2) but not analysed.
- Limits stated: no arrival process (all boarders present before the doors open) because of space
  (§3.2); camera positions hid where alighters stood inside the train (§4.2); "More experiments
  are needed" (abstract). Lab participants act knowing they are observed [inference]. **Western
  (London), laboratory.**
- Reference behaviours it supports: BA-1, BA-2, BA-6 [inference].
- BibTeX: `seriani2019exploring`.

### [Luangboriboon-Density]: The influence of the density inside a train carriage on passenger boarding rate
- Authors / Year / Venue / Link: Luangboriboon, N., Seriani, S. and Fujiyama, T. (2020).
  *International Journal of Rail Transportation* 9(5), 445-460. doi:10.1080/23248378.2020.1846633
  (Crossref; issue dated 2021, online December 2020). Copy read: the accepted manuscript on UCL
  Discovery, https://discovery.ucl.ac.uk/10114155/ (cached on disk only:
  `refs/he_luangboriboon2020_density_am.*`).
- Status: published (peer-reviewed). Read: full text of the accepted manuscript.
- Scenario: boarding (metro), effect of crowding inside the carriage.
- Study type: controlled experiment (PAMELA mock-up).
- Place, year, sample: London; about 120 participants per day over five days, 55% male (§3.2);
  in the scenario analysed, 45 boarders and 5 alighters (§3.1). Year not given in the text read
  [unverified].
- What people did, with numbers: "the passenger boarding rate increased as the density increased,
  up to approximately 2.5-3.0 passengers/m². Beyond that point, our results suggested that the
  boarding rate may have decreased, but the evidence was not conclusive" (abstract; §§4-5,
  Figures 3-6). Up to about 5 passengers/m², density had no "apparent negative effects on the
  boarding rate" (abstract).
- What changed the behaviour: density inside the vestibule (§3.3 onwards).
- Effects of age or gender: participants' age distribution is shown (Figure 2) but not analysed.
- Limits stated: results hold only up to about 5 passengers/m² (§5); weak evidence for a drop-off
  point (§5). **Western, laboratory.**
- Reference behaviours it supports: BA-6 [inference] (it partly contradicts [Seriani-BARatio]
  §4.4).
- BibTeX: `luangboriboon2020influence`.

### [Harris-Rates]: A Comprehensive Analysis of Passenger Alighting and Boarding Rates
- Authors / Year / Venue / Link: Harris, N. G., de Simone, F. and Condry, B. (2022). *Urban Rail
  Transit* 8(1), 67-98. doi:10.1007/s40864-021-00161-8 (Crossref). CC BY 4.0 (cached:
  `refs/he_harris2022_rates.*`).
- Status: published (peer-reviewed). Read: §§1-3 and §4.1 in full; §5 (regression results) only
  as far as needed for the two points below.
- Scenario: boarding and alighting (urban rail, worldwide).
- Study type: field observation (a meta-analysis of station-stop surveys done to a common London
  Underground procedure, two observers at the busiest door; §4.1, p. 75).
- Place, year, sample: operators in the benchmarking groups of "c. 90 companies" (§1, p. 68);
  "over 6000 data points" (§4.1, p. 75). Operators and cities are not named [inference: the
  benchmarking is confidential]. Years not given [unverified].
- What it found that bears on this issue:
  - A previous regression's 1-5 "management action" score, "which included measures such as levels
    of staffing, platform markings, physical barriers, etc.", "did not turn out to be a
    statistically significant variable" (§3.4, p. 74).
  - Platform edge doors were among the variables "shown to provide no statistical explanation" of
    the rates (abstract, p. 67).
- Effects of age or gender: none analysed (luggage share is a variable).
- Limits: rates, not order or conflict; the management score is coarse (§3.4).
- Reference behaviours it supports: BA-7 [inference].
- BibTeX: `harris2022comprehensive`.

---

## Read but not used as evidence

- **Chen, F., Gao, Y., Wang, Z. and Liu, Y. (2018).** "Analysis on Alighting and Boarding Movement
  Laws in Subway Using Modified Social Force Model". PED 2018, *Collective Dynamics*. A
  simulation; it mentions "observation in metro stations" without giving numbers or a source, so
  there is no field data to use. Cached on disk only.
- **Lindner, J., Pechinger, M. and Bogenberger, K. (2025).** "Modeling Passenger Boarding Times
  Using Sumonity's Sub-Microscopic Pedestrian Simulation". SUMO User Conference,
  doi:10.52825/scp.v6i.2618 (seed lead). The authors state "real-world validation of our
  simulation scenarios is not feasible", and compare only with a laboratory study (Fernández et
  al., *TRR*), so there is **no field data to use**. Of note for the testbeds: its passengers start
  from random positions and walk to the nearest door; there is no queue.
- **Seriani, S., Fujiyama, T. and Holloway, C. (2016)**, *Transportation Planning and Technology*
  (UCL accepted manuscript), and **Seriani and Fujiyama (2019)**, *Collective Dynamics*: both
  PAMELA experiments on interaction space and train design. Obtained, but they measure space and
  timing rather than the behaviours this issue asks about, so they are listed only.

---

## Stubs: confirmed to exist, full text not obtained

### [Li-NonComplianceThesis]
- Title: Study on Metro Passengers' Alighting and Boarding Process by Computer Simulation
- Authors, year, venue: Li, Zitong (2020). PhD thesis, City University of Hong Kong (supervisor
  S. M. Lo) `[thesis]`. Its record says field surveys in Hong Kong and mainland China found
  boarders entering while alighters were still inside.
- Link tried: http://lbms03.cityu.edu.hk/theses/ftt/phd-ca-55258924.pdf (from
  https://scholars.cityu.edu.hk/en/studentTheses/study-on-metro-passengers-alighting-and-boarding-process-by-compu/)
- Reason unavailable: the server returns a copyright-acknowledgement form before the PDF. I did
  not accept terms on the user's behalf.
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

### [Baali-NonCompliance]
- Title: The impact of passenger non-compliance during alighting and boarding on railway stations
- Authors, year, venue: Baali, M., Buisson, C., Coulaud, R. and Moussaïd, M. (2024). HAL
  hal-04811675 (document type not stated on HAL) `[preprint]`.
- Link tried: https://hal.science/hal-04811675/document
- Reason unavailable: HAL's bot protection (Anubis) refused automated access. It should open in a
  browser.
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

### [Li-EagerToBoard]
- Title: Modeling metro passengers being eager to get aboard during the alighting and boarding process
- Authors, year, venue: Li, Z., Lo, S. M., Liu, S., Ma, J. and Huang, D. (2021). *Transportmetrica
  A* 17(4), 714-738. doi:10.1080/23249935.2020.1809548 (seed lead; Crossref).
- Link tried: https://www.worldtransitresearch.info/research/8487 (abstract only) and the DOI.
- Reason unavailable: paywalled. A simulation, so only its cited field data would count.
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

### [Qu-BoardingCA]
- Title: Modeling pedestrian behaviors of boarding and alighting dynamics in urban railway stations
- Authors, year, venue: Qu, Y., Liu, X., Wu, J. and Wei, Y. (2023). *Transportmetrica A* 19(1),
  2035845. doi:10.1080/23249935.2022.2035845 (seed lead; from the World Transit Research record).
- Link tried: https://www.worldtransitresearch.info/research/9582 and the DOI.
- Reason unavailable: paywalled. Its record says time headways were extracted from surveillance
  video, which would count as field data.
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

### [Kim-QueueMicrosim]
- Title: Modeling pedestrian queuing using micro-simulation
- Authors, year, venue: Kim, I., Galiza, R. and Ferreira, L. (2013). *Transportation Research Part
  A* 49, 232-240. doi:10.1016/j.tra.2013.01.018 (seed lead; Crossref).
- Link tried: the DOI; OpenAlex reports no open copy.
- Reason unavailable: paywalled.
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

### [SerianiFernandez-TrafficMgmt]
- Title: Pedestrian traffic management of boarding and alighting in metro stations
- Authors, year, venue: Seriani, S. and Fernandez, R. (2015). *Transportation Research Part C* 53,
  76-92. doi:10.1016/j.trc.2015.02.003 (Crossref)
- Link tried: the DOI; OpenAlex and Semantic Scholar report it closed.
- Reason unavailable: paywalled.
- Date attempted: 2026-10-18
- Status: awaiting PDF from user
