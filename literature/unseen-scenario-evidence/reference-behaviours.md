# Q5 and Q6. Reference behaviours for the unseen-scenario tests

> For issue [#37](https://github.com/M450NCH00/CrowdSimulation/issues/37), PT-3 of track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34). **Everything in this file is a
> proposal awaiting the supervisor's sign-off**: the grading scale, the wording of each statement,
> and the conflict-type labels, which use the vocabulary proposed (not agreed) in #34.
>
> Each statement is short and testable: an unseen-scenario test (PT-2's protocol, issue #36) can
> compare a rule's or a model's behaviour against it. Sources and locators are in the topic files:
> [queue cutting](queue-cutting.md) · [boarding and alighting](boarding-alighting.md) ·
> [lifts and escalators](lifts-escalators.md) · [Singapore](singapore.md).

---

## §1. Evidence grades (proposal)

The issue offered a four-level scale; I adopt it, with one rule and five flags added.

| Grade | Meaning |
|---|---|
| **A** | Replicated field or controlled data: **two or more independent research groups** report numbers pointing the same way |
| **B** | One field study or controlled experiment with numbers (several experiments by one group count as one) |
| **C** | Observation without numbers in the text; or field data cited inside a simulation or review; or a statistic about a related outcome rather than the behaviour itself |
| **D** | Theory, official statement of a norm, or anecdote |

**Flags**, written after the grade, which the test protocol should weigh when choosing what to test
against:

| Flag | Meaning |
|---|---|
| `old` | Data collected before 2001 (more than 25 years ago) |
| `W` | Western setting (Europe, North America); the evidence may not hold in Singapore |
| `EA` | East Asian setting (here, Taipei); culturally closest to Singapore of what was read, but not Singapore |
| `SG` | Singapore data |
| `lab` | Controlled experiment; participants knew they were observed |
| `repro` | Numbers read through a verbatim reproduction of the original table (work log A6), not the paper itself |
| `off` | From an official report or statement, not peer-reviewed |

**Rule**: a `repro` statement cannot be graded above B, whatever the original's quality.

**Contested** statements (two sources disagree) are listed with both sources and marked
**CONTESTED**. They are reference *non*-behaviours: a test should not require a rule to reproduce
either side.

---

## §2. The statements

Conflict types follow #34's proposed vocabulary: `exclusive_access.queue`,
`exclusive_access.vehicle_door`, `capacity`, `passing_room` (overtaking on an escalator).

### Queue cutting (`exclusive_access.queue`)

| ID | Reference behaviour | Source | Study type | Place, year of data | n | Grade |
|---|---|---|---|---|---|---|
| QC-1 | When one person cuts into a queue, **objection comes mostly from the person directly behind the cut, and falls off steeply with distance**: 36% directly behind, 14% two places back, 0% three places back. | [Brintzenhofe-MilgramRevisited] Table 3.2, p. 70 (Milgram et al. data) | Field experiment | New York City, 1978 | 22 trials (Condition 1) | **B** `old` `W` `repro` |
| QC-2 | **Most people directly behind a single queue-cutter do not object to the cutter** (14 of 22 did not). | as QC-1 | Field experiment | New York City, 1978 | 22 | **B** `old` `W` `repro` |
| QC-3 | **Two cutters together draw objection from the person directly behind more than twice as often as one** (87% vs 36%), and more physical ejection (6 of 23 vs 1 of 22). | as QC-1 | Field experiment | New York City, 1978 | 23 vs 22 trials | **B** `old` `W` `repro` |
| QC-4 | **A cutter who appears to be joining a friend already in the queue draws far less objection than a stranger** (10-13% vs 37-60%). | [Brintzenhofe-MilgramRevisited] Table 3.1, p. 66 (Schmitt et al. 1992, Table 1, p. 813) | Field experiment | Grand Central Terminal, New York; before 1992 | 120 (4 × 30) | **B** `old` `W` `repro` |
| QC-5 | **The person cut in front of objects more when more people are queued behind them** (60% vs 37% for a stranger). | as QC-4 | Field experiment | as QC-4 | 60 | **B** `old` `W` `repro` |
| QC-6 | When someone **asks** to go first, **a reason that sounds self-serving ("I don't want to wait") is granted less often than other reasons** (68% vs 95% for "I feel really sick"; 70% vs 94% and 54% vs 73% against placebic or real reasons). | [Folkes-PartialReplication] pp. 602-603 | Field experiments (3) | UCLA and University of Sussex, before 1985 | 38, 42, 96 | **B** `old` `W` |
| QC-7 | When the **favour asked is big** (it would delay you a lot), **people grant it far less often** (24-42% vs 60-94%), and only a real reason helps. | [Langer-PlacebicInfo] Table 1, p. 637 | Field experiment | CUNY Graduate Center, New York; before 1978 | 120 | **B** `old` `W` |
| QC-8 | **CONTESTED**: whether giving *any* reason, even an empty one, raises compliance with a small request to go first. Langer et al.: yes (60% with no reason, 93-94% with one). Folkes: no (93% vs 94%; 83% vs 73%, not significant). | [Langer-PlacebicInfo] Table 1; [Folkes-PartialReplication] pp. 600, 603 | Field experiments | New York; Los Angeles and Brighton | 120; 42, 96 | **CONTESTED** `old` `W` |

[inference] QC-6 to QC-8 bear directly on #34's decision 4 (whether a rule may depend on a stated
reason). The evidence supports *the kind of reason* mattering (QC-6) and *the size of the favour*
mattering (QC-7), not the mere presence of a reason (QC-8).

### Boarding and alighting (`exclusive_access.vehicle_door`)

| ID | Reference behaviour | Source | Study type | Place, year of data | n | Grade |
|---|---|---|---|---|---|---|
| BA-1 | At a train door, **alighting mostly starts before boarding: boarders give way or wait for a gap**. | [Seriani-BARatio] §4.2; consistent with [Seriani-PEDsLondon] p. 6 (boarding peaks later with platform edge doors, "probably due to people giving way") | Controlled experiment; field observation | London (PAMELA mock-up); London Underground 2014-2015 | 110 participants; 615 + 1,703 door observations | **B** `W` `lab` |
| BA-2 | **The more boarders there are relative to alighters, the earlier boarding starts and the narrower the alighting stream**: with four boarders per alighter, 8% of alighters used a second lane; with four alighters per boarder, 38% did. | [Seriani-BARatio] §§4.2-4.3 | Controlled experiment | London (PAMELA) | 152 and 471 alighters | **B** `W` `lab` |
| BA-3 | **In real operation boarding and alighting overlap at the door, and the overlap grows with the number of passengers.** | [Seriani-PEDsLondon] pp. 8-9, Figure 4 | Field observation | London Underground, 2014-2015 | as BA-1 | **C** `W` (levels only in a figure) |
| BA-4 | **Boarders wait beside the doors as well as in front of them**; platform edge doors increase waiting beside the doors at low and high demand. | [Seriani-PEDsLondon] p. 7, p. 9, Figure 3 | Field observation | London Underground, 2014-2015 | as BA-1 | **C** `W` (frequencies only in a figure) |
| BA-5 | **At peak times some passengers let a train go and wait for the next one** (after 22% of trains at one door). | [Seriani-PEDsLondon] p. 7 | Field observation | Green Park, London, Nov-Dec 2015 | 135 of 615 trains | **B** `W` |
| BA-6 | **CONTESTED**: whether a crowded carriage slows boarding. One lab study finds door flow falling once density inside passes about 4 passengers/m²; another finds the boarding rate rising up to 2.5-3.0 and no clear fall up to about 5. | [Seriani-BARatio] §4.4; [Luangboriboon-Density] abstract, §§4-5 | Controlled experiments | London (PAMELA) | 50 per run; ~120 per day | **CONTESTED** `W` `lab` |
| BA-7 | **Platform markings, staffing and barriers, scored together, did not measurably change how fast people board and alight.** (Speed, not order.) | [Harris-Rates] §3.4, p. 74, reporting the authors' previous regression | Field observation (survey data) | Worldwide (operators unnamed) | not given for that regression | **C** |
| BA-8 | **GAP**: how often boarders start boarding before alighting has finished. Two field studies measure this (Hong Kong and mainland China; Paris region) but could not be opened. | [Li-NonComplianceThesis]; [Baali-NonCompliance] (stubs) | - | - | - | **none** |

### Lifts (`capacity`) and escalators (`passing_room`)

| ID | Reference behaviour | Source | Study type | Place, year of data | n | Grade |
|---|---|---|---|---|---|---|
| LE-1 | When a wheelchair, pram or walking-frame user is waiting for a lift, **other passengers let all of them in first in about a quarter of cases (24%), some do in another quarter (27%), and nobody gives way in about half (49%)**. | [Huang-TaipeiLifts] Table 4, p. 24; p. 27 | Field observation | Taipei MRT, Aug-Oct 2018, weekday morning peak | 89 trips needing priority (of 604; 2,413 users) | **B** `EA` |
| LE-2 | **People give way at a lift more often when more people, and more high-need users, are waiting.** | [Huang-TaipeiLifts] Table 6, p. 32 | Field observation | as LE-1 | as LE-1 | **B** `EA` |
| LE-3 | **Asked to stand on both sides of a long escalator, people comply only while staff are there to ask, and go back to "stand on one side, walk on the other" as soon as the request stops**; compliance drops after 09:00. | [TfL-Holborn2016] abstract, §6.3 p. 19, §9 p. 32 | Field experiment (staffed pilot) | Holborn, London, Nov-Dec 2015 | ~130,000 passengers affected | **B** `W` `off` |
| LE-4 | **People who want to walk up an escalator stop trying to pass when two people stand side by side talking or holding hands; the most determined weave past anyway.** | [TfL-Holborn2016] §6.3 pp. 19-20 | Field experiment, observers' notes | as LE-3 | not counted | **C** `W` `off` |

### Singapore context

| ID | Reference behaviour | Source | Study type | Place, year of data | n | Grade |
|---|---|---|---|---|---|---|
| SG-1 | **On Singapore MRT platforms, a large minority of passengers move between waiting spots before boarding** (44% at Serangoon, 37% at Bishan), and walk at about 0.8-0.9 m/s on the platform. | [Cheung-WiFiSG] pp. 2439, 2444 | Field observation (Wi-Fi tracking) | Serangoon and Bishan, Circle Line, Sep-Oct 2019 | 129,354 devices | **B** `SG` |
| SG-2 | **The norms promoted in Singapore**: give way to alighting passengers; let wheelchair users and the less mobile board first; use priority queues at train doors and lifts; double queue lines at busy stations to separate boarders from alighters. *These are norms, not observed behaviour.* | [MOT-StaffPilot2026] para. 1-2; [SMRT-SCET2018] items A2, A8 | Official statements | Singapore, 2018 and 2026 | - | **D** `SG` `off` |
| SG-3 | **In Singapore, people with prams, luggage and trolleys still ride escalators; these account for 17% of reported escalator incidents, and more than half of those involve users aged 55 and over.** | [BCA-Escalator2023] paras. 2-3 | Official incident statistics | Singapore, Jan-Oct 2023 | 632 incidents | **C** `SG` `off` (an incident count, not a behaviour rate) |

---

## §3. Q5: effects of age and gender in these scenarios

**Answer: almost none has been measured.** The table lists every age or gender result found in the
sources read for this issue.

| Scenario | What is reported | Source | Grade |
|---|---|---|---|
| Queue cutting (asking to go first) | A **female requester** got more compliance than a male one, F(1, 108) = 6.67, p < .01; no figures by gender. Confounded: the female experimenter did not know the hypotheses, the male one did. The *queuers'* gender is not analysed. | [Langer-PlacebicInfo] pp. 636-637 | B `old` `W` |
| Queue cutting (intrusion) | Nothing on the age or gender of the queuers or the cutters, in the data reproduced. | [Brintzenhofe-MilgramRevisited] | - |
| Boarding and alighting | Participants' ages and genders reported (54% women; ages from under 24 to over 65), **but not analysed**. | [Seriani-BARatio] §3.2; [Luangboriboon-Density] §3.2 | - |
| MRT platform (Singapore) | Age and gender **unknown** to the authors (Wi-Fi data). | [Cheung-WiFiSG] p. 2433 | - |
| Lift priority | Users classed by **mobility** (wheelchair, pram, walking frame), not by age or gender. | [Huang-TaipeiLifts] Table 2, p. 22 | - |
| Escalators (Singapore) | More than half of the bulky-item incidents involved **users aged 55 and over**. | [BCA-Escalator2023] para. 3 | C `SG` `off` |
| Escalators (London) | **Non-commuters** "tend to stand rather than walk" (a category, not an age). Cited from Davis and Dutta (2002), not read. | [TfL-Holborn2016] §4.2, p. 8 | C `W` `off` |

**Cross-reference with `literature/demographic-personas/human-demographic-effects.md`** (not
repeated here):

- That file's strongest measured result is that **young adults take on more of the avoidance when
  meeting an older adult** ([Rapos-CollisionAvoidance]), in passing, not in queues or at doors.
  Nothing read for this issue confirms or contradicts it for the five unseen scenarios.
  [inference] The closest analogue here is the mobility-based priority in Taipei lifts (LE-1),
  which is about wheelchairs and prams, not age, and shows priority being given **less than half
  the time**.
- That file warns that much "demographic" crowd evidence is a **simulation input, not a
  measurement**. The same applies here: none of the seed simulation papers on boarding gave
  demographic data that could count as evidence.
- [inference] **Consequence for the personas**: for queue cutting, boarding, lifts and
  escalators, an age or gender difference produced by the LLM personas **cannot be checked against
  human data from these sources**. If a persona-based model shows, say, older personas being
  given priority at lift doors, the only human comparison available is mobility-based priority
  (LE-1), and that comparison should be labelled as such.

---

## §4. What the evidence can and cannot support (for PT-2's protocol)

[inference] Summarised in [`verdict.md`](verdict.md). In short:

- **Testable now, with caveats**: queue cutting (QC-1 to QC-7), at grade B, but every statement is
  `old` and `W`, and QC-1 to QC-5 are `repro`.
- **Partly testable**: train doors (BA-1, BA-2, BA-5 at grade B, `W`); the central question, how
  often people board before alighting ends (BA-8), has no number.
- **Lifts**: one solid East Asian field study (LE-1, LE-2).
- **Escalators**: one staffed pilot (LE-3); nothing for Singapore beyond incident counts.
- **Bus boarding**: no reference behaviour at all.
- **No statement reaches grade A.** Every grade-B statement rests on one study or one research
  group.
