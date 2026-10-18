# Q4. Singapore: what exists, and what does not

> For issue [#37](https://github.com/M450NCH00/CrowdSimulation/issues/37), PT-3 of track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34). Searched and read on 2026-10-18.
> Every search run is listed in §4 and in [`search-log.md`](search-log.md).

Companion files: [verdict](verdict.md) · [reference behaviours](reference-behaviours.md) ·
[queue cutting](queue-cutting.md) · [boarding and alighting](boarding-alighting.md) ·
[lifts and escalators](lifts-escalators.md) · [missing papers](missing-papers.md)

---

## §1. The finding

**No Singapore study was found that observes or measures any of the five target behaviours**:
queue cutting, letting passengers alight first at MRT or bus doors, boarding order at bus stops,
who gets into a nearly full lift, or standing and walking on escalators. **This absence is the main
Q4 result.** Within the searches in §4 (web search in English only, open repositories, and the
official sites of MOT, LTA, SMRT, SBS Transit and BCA), what does exist is:

1. **One open academic field study of MRT platform behaviour**, about where people wait, not about
   conflict at the door ([Cheung-WiFiSG], §2).
2. **Two academic bus studies that use Singapore data**, both stubbed because the full text could
   not be downloaded ([Sun-BusDynamics], [Liu-BusStopDesign], §3).
3. **Official statements**, which describe *measures* (queue lines, priority queues, staff on
   platforms, safety advice) and one *perception* survey, but no observation of behaviour (§2).
4. **Press and social-media debate** (for example on prams and wheelchairs in lifts), which is not
   evidence and is not used.

[inference] For the test protocol, Singapore can supply the **norms that are officially promoted**
(give way to alighting passengers; priority queues for wheelchair users and the less mobile; hold
the handrail; use lifts with bulky items), but **not how often people follow them**. Any
reference behaviour for the Singapore scenarios therefore has to be borrowed from elsewhere (London,
New York, Hong Kong), and must carry the `W` or "not Singapore" flag.

**One correction for `dataset/scenarios.yaml`.** The `escalator_entry_merge` scenario's
`sg_variant` says "note local campaigns discouraging the old keep-left / walk-right habit and
asking people to stand on both sides". **No Singapore source found says "stand on both sides".**
BCA's 2023 advice is "Hold on to the handrail and stand within the yellow lines on the escalator
steps" ([BCA-Escalator2023] para. 6). A Hong Kong government newsletter (2015) says Singapore's
railway authority "calls for 'walking on the right and standing on the left'" ([EMSD-2015],
pp. 1-2). A 2025 Hong Kong budget reply lists Singapore among governments encouraging people to
"stand firm and hold the handrail" ([DEVB-2025]). This is a dataset-wording question for the
supervisor, not a change made here.

---

## §2. Entries

### [Cheung-WiFiSG]: Investigating passenger behaviour on the metro platform with Wi-Fi location tracking data: a case study of Singapore
- Authors / Year / Venue / Link: Cheung, M., Cheng, Y. and Fujiyama, T. (2024 online; 2026 issue).
  *Transportation* 53(4), 2429-2451. doi:10.1007/s11116-024-10570-w (Crossref). CC BY-NC-ND 4.0
  (p. 2448; cached:
  `refs/he_cheung2024_wifi_sg.*`).
- Status: published (peer-reviewed). Read: full text.
- Scenario: other (waiting on an MRT platform; relevant to `mrt_door_alight_board` only as context).
- Study type: field observation (passive Wi-Fi location tracking).
- Place, year of data collection, sample size: Serangoon and Bishan stations, Circle Line,
  Singapore; 30 September to 13 October 2019; 129,354 devices (abstract p. 2429; p. 2433). The
  Wireless@SG data has a 5 m positional error (p. 2432). Platform edge doors at both stations
  (p. 2435).
- What people did, with numbers: 44.16% (Serangoon) and 37.44% (Bishan) of passengers had two or
  more "staying phases", i.e. they stopped, moved, and stopped again before boarding (p. 2439);
  stays concentrated near the platform entry points (p. 2441); platform walking speeds averaged
  0.82 m/s (Serangoon) and 0.93 m/s (Bishan), slower than the 1.23 m/s on Singapore sidewalks
  reported by Tanaboriboon et al. (1986) (pp. 2444, 2446).
- What changed the behaviour: station layout and entry point, direction of travel, weekday versus
  weekend, peak versus off-peak (Table on p. 2439, all p < 0.001).
- Effects of age or gender reported: none possible: "The user characteristics (e.g., gender, age,
  etc.) of the Wi-Fi service were unknown to the authors" (p. 2433).
- Limits: 5 m error; only Wi-Fi users (about 57% of passengers by the authors' estimate, p. 2433);
  nothing about the door itself.
- Reference behaviours it supports: SG-1 [inference].
- BibTeX: `cheung2024investigating`.

### [MOT-CGI]: Commuter Graciousness Index (written parliamentary replies)
- Authors / Year / Venue / Link: Ministry of Transport, Singapore `[official]`.
  (a) Written reply by Minister Khaw Boon Wan to Er Dr Lee Bee Wah, **5 August 2019**:
  https://www.mot.gov.sg/news-resources/newsroom/written-reply-by-minister-for-transport-khaw-boon-wan-to-parliamentary-question-on-updates-on-commuter-graciousness-index-and-plans-to-engage-in-public-education/
  (b) Written reply by Acting Minister Jeffrey Siow to Mr Chua Kheng Wee Louis, **15 October
  2025**: https://www.mot.gov.sg/news-resources/newsroom/publishing-commuter-graciousness-index-and-commuter-graciousness-survey-results/
  (cached on disk only: `refs/he_mot2019_cgi.txt`, `refs/he_mot2025_cgi.txt`).
- Status: `[official]`. Read: full text of both replies.
- Scenario: all public-transport scenarios (unspecified behaviours).
- Study type: survey of perceptions (LTA). Not observation.
- Place, year, sample: Singapore; surveys "every one to two years" (a, para. 1). Sample size and
  question wording not given [unverified].
- What it reports: "the percentage of commuters noticing gracious behaviour on public transport
  has increased, from 52% in 2016 to 56% in 2018" (a, para. 1). In 2025 the government is
  "currently reviewing the methodology of the LTA survey that was previously used to derive the
  Commuter Graciousness Index" (b, para. 2), and the reply does not publish newer figures.
  Higher earlier figures circulated in the press (38.6% in 2012 to 61.3% in 2014) could not be
  traced to an official page and are **not used** [unverified].
- Effects of age or gender: none reported.
- Limits: perception, not behaviour; which behaviours count is not defined in either reply.
- Reference behaviours it supports: none (grade D at most).
- BibTeX: `mot2019cgi`, `mot2025cgi`.

### [MOT-StaffPilot2026]: LTA Staff Deployment Pilot Programme for Peak Hour Commuter Etiquette Interventions at Busy MRT Stations
- Authors / Year / Venue / Link: Ministry of Transport, Singapore (written reply by Acting Minister
  Jeffrey Siow to Mr Dennis Tan Lip Fong), **8 April 2026** `[official]`.
  https://www.mot.gov.sg/news-resources/newsroom/lta-staff-deployment-pilot-programme-for-peak-hour-commuter-etiquette-interventions-at-busy-mrt-stations/
  (cached on disk only: `refs/he_mot2026_staff_pilot.txt`).
- Status: `[official]`. Read: full text.
- Scenario: boarding and alighting (MRT); lifts.
- Study type: official statement of practice. No data.
- What it says: operators "deploy staff during peak hours at the platforms of busier stations to
  manage crowds and encourage gracious commuting behaviour such as giving way to alighting
  passengers, and allowing wheelchair users and other passengers who are less mobile to board
  first" (para. 1); "more prominent priority queues for boarding trains and lifts will be
  introduced to nudge commuters to give way to those in need" (para. 2).
- [inference] That staff are needed at busy stations to encourage giving way implies the norm is
  not always followed there, but the reply gives no rate.
- Reference behaviours it supports: SG-2 (the promoted norm, not observed compliance).
- BibTeX: `mot2026staff`.

### [SMRT-SCET2018]: Annex C, Past SMRT Commuter Experience Touchpoints (SCET) Initiatives
- Authors / Year / Venue / Link: SMRT, issued with the media release "Empowering Commuters with
  Up-to-date Information to Improve the Journey Experience", **5 February 2018** `[official]`.
  https://www.smrt.com.sg/getmedia/02c71b02-f115-42f3-85ab-ed6e0c51c726/annex-c-past-scet-initatives.pdf
  (cached on disk only: `refs/he_smrt2018_annexc.*`).
- Status: `[official]`. Read: full text (5 pp.).
- Scenario: boarding and alighting (MRT); lifts.
- What it says: item A8, "Double Queue Line": "SMRT installed double queues at platforms of busy
  MRT stations such as Jurong East, Buona Vista and Bishan to reducing criss-crossing of commuters
  when they alight and board trains" (p. 2). Item A2: floor stickers for "priority queues at the
  entrance to lifts and escalators at MRT stations" (p. 1). No evaluation is reported.
- Reference behaviours it supports: SG-2, SG-3 (as design intent).
- BibTeX: `smrt2018scet`.

### [BCA-Escalator2023]: 97% of escalator incidents reported to BCA linked to improper use of escalator
- Authors / Year / Venue / Link: Building and Construction Authority, Singapore, media release,
  **27 November 2023** `[official]`.
  https://isomer-user-content.by.gov.sg/338/7fcee25f-0cfd-46a0-8cb6-87dd4d1c1c95/bca-escalator-incidents-media-release.pdf
  (cached on disk only: `refs/he_bca2023_escalator.*`).
- Status: `[official]`. Read: full text.
- Scenario: escalator.
- Study type: official incident statistics (reports to the regulator).
- Place, year, sample: Singapore, 632 escalator incidents reported from January to October 2023
  (para. 1).
- What it reports: 97% (616) "attributed to user behaviour" (para. 1). Top causes: bulky items
  including prams, luggage and trolleys 17%; "Moving on escalator or not holding the handrail" 16%;
  physical condition 12%; distraction 11%; entrapment 9% (para. 2).
- Effects of age reported: "more than half" of the bulky-item incidents "involved users aged 55 and
  above" (para. 3).
- What it advises: "Hold on to the handrail and stand within the yellow lines on the escalator
  steps"; people with trolleys, prams, luggage, or limited mobility "should use the lifts instead"
  (para. 6).
- Limits: incidents, not everyday behaviour; the denominator (total rides) is unknown.
- Reference behaviours it supports: LE-3 (age, bulky items) [inference].
- BibTeX: `bca2023escalator`.

### [EMSD-2015] and [DEVB-2025]: Hong Kong government statements about Singapore's escalator advice
- (a) Electrical and Mechanical Services Department, Hong Kong, *Lift and Escalator Newsletter*,
  Vol. 1, **2 December 2015**, pp. 1-2 `[official]`:
  https://www.emsd.gov.hk/filemanager/en/content_1132/Lift%20and%20Escalator%20Newsletter%20(Vol.1_2015.12)%20(E).pdf
  "their counterpart in Singapore calls for 'walking on the right and standing on the left'".
- (b) Development Bureau, Hong Kong, *Examination of Estimates of Expenditure 2025-26*, Controlling
  Officer's Reply DEVB(W)095 `[official]`:
  https://www.emsd.gov.hk/filemanager/en/content_1552/DEVB(W)095-3063.pdf
  lists Singapore among cities whose "governments ... encourage passengers to stand firm and hold
  the handrail when using escalators".
- Status: `[official]`, but **secondary for Singapore** (a foreign government describing Singapore's
  advice, without citing a Singapore document). Cached on disk only (`refs/he_emsd2015.txt`,
  `refs/he_devb2025.txt`). Grade D.
- Reference behaviours it supports: none; it bears on the `scenarios.yaml` wording (§1).

---

## §3. Stubs: Singapore studies confirmed to exist, full text not obtained

### [Sun-BusDynamics]
- Title: Models of bus boarding and alighting dynamics
- Authors, year, venue: Sun, L., Tirachini, A., Axhausen, K. W., Erath, A. and Lee, D.-H. (2014).
  *Transportation Research Part A* 69, 447-460. doi:10.1016/j.tra.2014.09.007 (Crossref). Uses
  Singapore smart-card data according to a search-engine summary [unverified].
- Link tried: https://repositorio.uchile.cl/handle/2250/126576 (open repository copy)
- Reason unavailable: the repository returned a bot-check page instead of the PDF; it should open in
  a browser. ETH's copy (http://hdl.handle.net/20.500.11850/68608) offered no PDF link to an
  automated request.
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

### [Liu-BusStopDesign]
- Title: Impact of Different Bus Stop Designs on Bus Operating Time Components
- Authors, year, venue: Liu, X., Yao, Y., Meng, M. and Rau, A. [author names from OpenAlex;
  Crossref's author list is garbled] (2017). *Journal of Public Transportation* 20(1), 104-118.
  doi:10.5038/2375-0901.20.1.6. Surveys at Singapore bus stops in July 2014 according to a
  search-engine summary [unverified].
- Link tried: https://digitalcommons.usf.edu/cgi/viewcontent.cgi?article=1601&context=jpt (open
  access)
- Reason unavailable: HTTP 403 to automated requests; it should open in a browser.
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

### Not stubbed, recorded only
- Tanaboriboon, Y., Hwa, S. S. and Chor, C. H. (1986). "Pedestrian Characteristics Study in
  Singapore". *Journal of Transportation Engineering* 112(3), 229-235.
  doi:10.1061/(ASCE)0733-947X(1986)112:3(229). About walking speed and flow, not the target
  behaviours; paywalled; cited here only through [Cheung-WiFiSG] (p. 2446).

---

## §4. Searches run for Singapore (all 2026-10-18)

| # | Where | Query or route | Outcome |
|---|---|---|---|
| S1 | Web search | Singapore bus stop queue boarding behaviour study OR survey OR observation LTA commuters queue | [Cheung-WiFiSG]; [Liu-BusStopDesign]; an etiquette blog (not used) |
| S2 | Web search | Singapore MRT "alight first" OR "let passengers alight" boarding behaviour study platform markings SMRT LTA | [Sun-BusDynamics]; no study of alight-first compliance |
| S3 | Web search | Singapore Kindness Movement Graciousness Index survey public transport queue behaviour results | [MOT-CGI] (2019, 2025); press figures for 2012-2014 not traceable to an official page |
| S4 | Web search | Singapore escalator "stand on both sides" OR "keep left" LTA campaign walk escalator etiquette study | [EMSD-2015], [DEVB-2025] (Hong Kong documents); no Singapore campaign page found |
| S5 | Web search | Singapore pedestrian behaviour study queue OR lift OR escalator NUS NTU journal observation Tanaboriboon | Tanaboriboon et al. 1986 (walking only); BCA escalator incidents |
| S6 | Web search | LTA Singapore escalator safety "hold the handrail" campaign walk left stand right discouraged 2018 2019 press release | [BCA-Escalator2023]; SMRT's "Safe Travel" page; no LTA press release on walking or standing sides |
| S7 | Web search | Singapore HDB lift etiquette study OR survey wheelchair pram priority lift Singapore research | MND parliamentary answers on lift access (no behaviour data); a Singapore Kindness Movement open letter and press items on a pram-and-lift dispute (opinion, not used) |
| S8 | Web search | Singapore MRT platform floor markings arrows "alighting" boarders stand aside queue lines introduced SMRT LTA news | [SMRT-SCET2018]; [MOT-StaffPilot2026]; a press item on LTA's 2016 priority queues (consistent with SMRT A2, not used separately) |
| S9 | OpenAlex API | searches for the titles of the Singapore leads | OA status of [Cheung-WiFiSG], [Liu-BusStopDesign], [Sun-BusDynamics], Tanaboriboon 1986 |
| S10 | MOT newsroom | the 2019 and 2025 replies on the Commuter Graciousness Index, the 2026 reply on staff deployment | read in full |

**Not searched** (for a later session): Chinese-language and Malay-language sources; NUS and NTU
thesis repositories (DR-NTU and ScholarBank) beyond what web search surfaced; the Public Transport
Council's own studies, which the 2025 reply mentions but does not cite; HDB lift-usage studies.
