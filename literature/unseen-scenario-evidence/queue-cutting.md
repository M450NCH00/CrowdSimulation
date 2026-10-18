# Q1. Queue cutting: what people do when someone cuts in

> For issue [#37](https://github.com/M450NCH00/CrowdSimulation/issues/37), PT-3 of track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34). Literature only. All sources were
> read on 2026-10-18. Grades (A-D, plus the flags `old`, `W`, `repro`) are defined in
> [`reference-behaviours.md`](reference-behaviours.md) §1, and are a **proposal**.

Companion files: [verdict](verdict.md) · [reference behaviours](reference-behaviours.md) ·
[boarding and alighting](boarding-alighting.md) · [lifts and escalators](lifts-escalators.md) ·
[Singapore](singapore.md) · [search log](search-log.md) · [missing papers](missing-papers.md) ·
[BibTeX](refs-unseen-evidence.bib)

---

## The short answer

- **The primary queue-intrusion papers could not be opened.** Milgram et al. (1986), Schmitt et
  al. (1992), Mann (1969), Helweg-Larsen and LoMonaco (2008), Dold and Khadjavi (2017) and
  Oberholzer-Gee (2006) are all paywalled with no open copy that could be downloaded. Each has a
  stub at the end of this file and a row in [`missing-papers.md`](missing-papers.md). **None of
  them is summarised from an abstract or a secondary summary.**
- **But the core numbers of the two field experiments are available, reproduced verbatim.** An
  open-access (CC BY-NC-ND) chapter by Brintzenhofe (2023) reproduces, with the American
  Psychological Association's permission, Schmitt et al.'s Table 1 and the per-position reaction
  rates of Milgram et al.'s experiment, the latter alongside unpublished raw data from the Milgram
  archive at Yale. These numbers are attributed below to the chapter and flagged `repro`. This is a
  judgement call (work log A6): a verbatim table reproduced with the publisher's permission is not
  a "secondary summary", but it is also not the paper, so it carries the flag.
- **Milgram: 1978 or 1986?** Both are right. The experiment was "conducted by his graduate
  students in the spring of 1978 and published shortly after his death (Milgram et al., 1986)"
  ([Brintzenhofe-MilgramRevisited], p. 65). Data year 1978; publication year 1986.
- **What the readable evidence says** (details and locators in the entries):
  1. Objection comes overwhelmingly from the person **directly behind** the cut, and falls off
     steeply with distance: 36% at +1, 14% at +2, 0% at +3 for one intruder.
  2. **Two intruders roughly double** the rate directly behind (87% at +1) and the severity
     (more ejections).
  3. **Distance, not who stands in between, is what the table shows.** Putting silent
     confederates ("buffers") between the cut and a queuer gives no consistent change over having
     ordinary queuers there (for two intruders: .200 against .435 at +2, but .150 against .091 at
     +3). Secondary summaries say Milgram et al. found that silent buffers reduced protest; that
     analysis is in the unread paper and is not used here.
  4. A cutter who **looks legitimate** (joins a friend already in line) draws far less objection
     (10-13%) than a stranger (37-60%).
  5. For **asking** to go first (rather than cutting), giving a reason helps, and *which* reason
     matters: an uncontrollable reason ("I feel really sick") is granted more than a controllable
     one ("I don't want to wait"). Langer et al.'s famous "any reason works" result for small
     favours **was not replicated** by Folkes (1985).
  6. When the **favour is big** (the asker would delay you a lot), compliance drops sharply
     (from 60-94% to 24-42%).
- **Gender and age**: almost nothing. Langer et al. report that a female experimenter got more
  compliance than a male one (no numbers given); no source read reports the queuer's age or
  gender as a factor. See Q5 in [`reference-behaviours.md`](reference-behaviours.md) §3.
- **All of this is old (1977-1990) and Western** (New York, Los Angeles, Brighton).

---

## Entries (read in full or in the sections stated)

### [Brintzenhofe-MilgramRevisited]: Revisiting Milgram's 1978 "Response to Intrusion into Waiting Lines" Experiment
- Authors / Year / Venue / Link: Brintzenhofe, K. T. (2023). Chapter 3 of *Investigating Human
  Interaction through Mathematical Analysis: The Queue Transform*, Routledge, pp. 65-109.
  doi:10.4324/9781003325161-4 (the chapter DOI ends in -4; the book calls it Chapter 3).
  Open copy: https://api.taylorfrancis.com/content/chapters/oa-mono/download?identifierName=doi&identifierValue=10.4324/9781003325161-4&type=chapterpdf
  (cached: `refs/he_brintzenhofe2023_ch3.pdf`, `.txt`).
- Status: published (Routledge open-access monograph, CC BY-NC-ND 4.0, per the Crossref licence
  record and the chapter's first page, p. 65); single author; not a peer-reviewed journal.
  Read: full chapter text; the data tables 3.1-3.3 (pp. 66, 70, 72) read as page images, since
  they are images in the PDF. **The mathematical model (§3.3, pp. 73-104) and the chapter's
  speculation about the Golden Ratio and evolution (§3.4.1, pp. 105-109) are not used here.**
- Scenario: queue cutting.
- Study type: re-analysis (a model) of two field experiments; **the field data are what is used
  here**: Milgram et al. (1986) as reproduced with APA permission, Schmitt et al. (1992) Table 1 as
  reproduced with APA permission, and unpublished summary data from the Stanley Milgram Papers (MS
  1406), Yale University Library.
- Place, year of data collection, sample size:
  - **Milgram et al.**: New York City, spring 1978 (p. 65). 129 trials in six conditions [inference:
    the first-position denominators of Table 3.2, p. 70, are 22 + 24 + 20 + 23 + 20 + 20 = 129;
    Table 3.3, p. 72, gives the same totals per condition]. 17 queue locations, including a bank,
    a post office, a passport office, Grand Central Terminal's ticket counter, an off-track betting
    parlour, LaGuardia's TWA boarding line, and Port Authority bus ticket and **bus boarding**
    queues (Table 3.3, p. 72). Six conditions: one or two confederate intruders, with zero, one or
    two silent confederate "buffers" between the intrusion point and the person observed (p. 65;
    Table 3.2, p. 70). Positions *ahead* of the intrusion point were not analysed (p. 71).
  - **Schmitt et al.**: Grand Central Terminal ticket counter, New York (p. 66); 120 observations,
    four conditions of 30 (p. 66). Year of data collection not given in the chapter [unverified].
- What people did, with numbers (proportion of the person at each position behind the intrusion
  who reacted *towards the intruder*; Table 3.2, p. 70, `repro`):

  | Condition | Intruders | Silent buffers | +1 | +2 | +3 | +4 |
  |---|---|---|---|---|---|---|
  | 1 | 1 | 0 | **8/22 = .364** | 2/14 = .143 | 0/9 = .000 | |
  | 2 | 1 | 1 (at +1) | (buffer) | 4/24 = .167 | 0/15 = .000 | |
  | 3 | 1 | 2 (at +1, +2) | (buffer) | (buffer) | 0/20 = .000 | |
  | 4 | 2 | 0 | **20/23 = .870** | 10/23 = .435 | 2/22 = .091 | |
  | 5 | 2 | 1 | (buffer) | 4/20 = .200 | 0/15 = .000 | |
  | 6 | 2 | 2 | (buffer) | (buffer) | 3/20 = .150 | 2/17 = .118 |

  - "Reaction" counts physical ejection, verbal ejection, verbal disapproval and non-verbal
    disapproval directed at the intruder (Table 3.2, p. 70; p. 71). Most people showed **no
    detectable reaction** in most conditions (row "# No Reaction Detected", Table 3.2, p. 70: for
    example 15 of 24 at +2 in Condition 2; 2 of 23 at +1 in Condition 4).
  - Severity: with one intruder, reactions at +1 were "mostly verbal disapproval or verbal
    ejection"; with two, "predominantly ... verbal and physical ejection" (p. 71). Physical
    ejection at +1: 1 of 22 (one intruder) against 6 of 23 (two intruders) (Table 3.2, p. 70).
  - Schmitt et al.'s Table 1 (as reproduced in Table 3.1, p. 66, `repro`), probability that the
    person intruded in front of reacts:

    | Intruder | Low social obligation (cut in front of the last person) | High social obligation (cut in front of the third-to-last; two confederates queue behind) |
    |---|---|---|
    | Illegitimate (a stranger) | .366 | .600 |
    | Legitimate (acts as a friend of the confederate ahead) | .100 | .133 |

- What changed the behaviour:
  - **Position**: reaction falls from +1 to +3 in every condition (Table 3.2, p. 70).
  - **Number of intruders**: two intruders more than double the reaction at +1 (.364 against
    .870) and at +2 (.143 against .435) (Table 3.2, p. 70).
  - **Silent buffers** (people in between who do nothing), compared with ordinary queuers at the
    same distance (Table 3.2, p. 70): one intruder, +2: .167 (buffer) against .143; +3: .000
    against .000. Two intruders, +2: .200 against .435; +3: .150 against .091. **No consistent
    buffer effect** [inference]. Conditions were run at different mixes of locations, so location
    and buffer effects are confounded (Table 3.3, p. 72) [inference].
  - **People behind the queuer** (social obligation): .366 against .600 for a stranger
    (Table 3.1, p. 66).
  - **Legitimacy of the cutter**: a cutter who appears to join a friend draws .100-.133 against
    .366-.600 (Table 3.1, p. 66).
  - **What is queued for**: the author groups the bus terminal, airport, rail ticket and betting
    queues as "high" stakes (limited resource or time) and the rest as "low" (p. 73); the
    confounding of condition with location is visible in Table 3.3 (p. 72), where 18 of
    Condition 4's 23 trials are at the Grand Central rail ticket counter (p. 73).
- Effects of age or gender reported: none in the chapter.
- Limits stated by the author; age and culture of the evidence: the 126 per-trial coding sheets
  are lost, so the per-position data are summary data only (p. 69); queue length beyond +5 had
  to be approximated (p. 70); positions ahead of the cut are not analysed (p. 71). The author frames
  the work as about "the western culture with its own social norms" (p. 105). Data are from New
  York in 1978 (Milgram) and before 1992 (Schmitt). **Old, Western, one city.**
- Reference behaviours it supports (copied into `reference-behaviours.md`): QC-1 to QC-5
  [inference].
- BibTeX: `brintzenhofe2023revisiting` in [`refs-unseen-evidence.bib`](refs-unseen-evidence.bib).

### [Langer-PlacebicInfo]: The mindlessness of ostensibly thoughtful action: The role of "placebic" information in interpersonal interaction
- Authors / Year / Venue / Link: Langer, E. J., Blank, A. and Chanowitz, B. (1978). *Journal of
  Personality and Social Psychology* 36(6), 635-642. doi:10.1037/0022-3514.36.6.635 (Crossref
  confirms all fields).
- Status: published (peer-reviewed). Read: full text, a copy of the APA typeset PDF on a
  third-party site (communicationcache.com); not openly licensed, so kept on disk only
  (`refs/he_langer1978.*`, see `.gitignore`).
- Scenario: queue cutting (asking to go first at a photocopier; Experiment 1 only. Experiments 2
  and 3 are about mail and are not used).
- Study type: field experiment.
- Place, year of data collection, sample size: the copying machine at the Graduate Center of the
  City University of New York; 120 adults, 68 male and 52 female (p. 636). Year of data collection
  not stated [unverified; before 1978].
- What people did, with numbers: proportion who let the experimenter go first (Table 1, p. 637):

  | Favour | No reason | Placebic reason ("because I have to make copies") | Real reason ("because I'm in a rush") |
  |---|---|---|---|
  | Small (5 pages) | .60 (n=15) | .93 (n=15) | .94 (n=16) |
  | Big (20 pages) | .24 (n=25) | .24 (n=25) | .42 (n=24) |

- What changed the behaviour: the size of the favour, F(1, 108) = 43.40, p < .001; the request
  wording, F(2, 108) = 3.02, p < .05 (p. 637). With a small favour, any reason helped; with a big
  one, only a real reason did (p. 637).
- Effects of age or gender reported: "the female experimenter had a higher rate of compliance than
  the male experimenter", F(1, 108) = 6.67, p < .01, with no interaction with the other variables
  (p. 637). No numbers by experimenter are given, and the subjects' own gender is not analysed.
  One female experimenter (blind to the hypotheses) and one male (who knew them) ran the sessions
  (p. 636), so experimenter gender is confounded with knowing the hypotheses [inference].
- Limits stated by the authors; age and culture: the authors themselves note the risk of
  "generalizing to successfully nonthinking people" from thinking subjects (p. 642). **Old (1970s),
  one US university, small cells (15-25).** The headline small-favour result was not replicated
  by [Folkes-PartialReplication].
- Reference behaviours it supports: QC-6, QC-7 [inference].
- BibTeX: `langer1978mindlessness`.

### [Folkes-PartialReplication]: Mindlessness or mindfulness: A partial replication and extension of Langer, Blank, and Chanowitz
- Authors / Year / Venue / Link: Folkes, V. S. (1985). *Journal of Personality and Social
  Psychology* 48(3), 600-604. doi:10.1037/0022-3514.48.3.600 (Crossref confirms all fields).
- Status: published (peer-reviewed). Read: full text, a copy of the APA typeset PDF on the same
  third-party site; kept on disk only (`refs/he_folkes1985.*`).
- Scenario: queue cutting (asking to go first at a copier).
- Study type: three field experiments (Experiments 1-3) and one questionnaire (Experiment 4, not
  used: it is a hypothetical, not behaviour).
- Place, year of data collection, sample size: Experiment 1, UCLA libraries, 82 people, of whom 38
  were asked a small favour (p. 602); Experiment 2, University of Sussex library, Brighton,
  England, 42 people (p. 602); Experiment 3, UCLA libraries, 96 people (p. 603). Years not stated
  [unverified; before 1985]. All requests were small (5 pages).
- What people did, with numbers:
  - Experiment 1: 18 of 19 complied with an uncontrollable reason ("because I feel really sick")
    against 13 of 19 with a controllable one ("because I don't want to wait") (p. 602).
  - Experiment 2: 70% complied with the controllable reason against 94% for the placebic and real
    reasons combined (p. 602); the no-reason condition got 93% against 94% for the combined
    placebic and real conditions, not significant (p. 603; Table 1, p. 601).
  - Experiment 3: 54% with the controllable reason against 73% for placebic and real combined
    (p. 603); no-reason compliance was 83% (p. 603).
- What changed the behaviour: whether the stated reason was outside the asker's control (pp.
  602-603). **Giving any reason versus none made no difference in Experiments 2 and 3**: "Neither
  study replicated Langer et al.'s results" (abstract, p. 600). The author notes a possible
  ceiling effect from the high no-reason compliance (93%, 83%) (p. 603).
- Effects of age or gender reported: experimenters' genders are listed (p. 602, p. 603) but no
  gender effect is reported for the field experiments.
- Limits; age and culture: small samples, student populations, US and UK, 1980s. **Old, Western.**
- Reference behaviours it supports: QC-6, QC-7 [inference].
- BibTeX: `folkes1985mindlessness`.

### [AllonHanany-CuttingInLine]: Cutting in Line: Social Norms in Queues
- Authors / Year / Venue / Link: Allon, G. and Hanany, E. (2012). *Management Science* 58(3),
  493-506. doi:10.1287/mnsc.1110.1438 (Crossref confirms all fields).
- Status: published (peer-reviewed). Read: **pp. 493-500 only** (§§1-6 and the start of §7): the
  copy on a Wharton faculty page is the INFORMS PDF truncated at 8 pages. Kept on disk only
  (`refs/he_allon_hanany2012_partial.*`).
- Scenario: queue cutting.
- Study type: **theory** (repeated games). No data of its own.
- Place, year, sample: n/a.
- What it says (as theory, not as evidence of behaviour): in a one-shot interaction (for example
  an overnight line), the only equilibrium priority rule is first-in-first-out, and "intrusions
  must be rejected in equilibrium" (§1, result 1, p. 494); with repeated interaction, priority for
  urgent customers can be sustained (result 2, pp. 494-495); with queue-length-dependent
  strategies, "customers with urgent requests ... are allowed to push only if the queue length is
  below a threshold" can be an equilibrium (result 3, p. 495); with private monitoring, the
  efficient rule is sustained by "contagious punishment" (result 4, p. 495).
- What it says about the empirical literature (§2.2, pp. 495-496): Milgram et al.'s intruder said
  only "Excuse me, I would like to get in here"; Allon and Hanany read that study as a setting
  where nobody has a more urgent need, so FIFO is the only sustainable rule (p. 496). They describe
  Mann (1969) as studying an overnight line for sports tickets and treating first-come-first-served
  as fundamental (pp. 495-496). **These are Allon and Hanany's descriptions; Mann and Milgram were
  not read.**
- Effects of age or gender: none.
- Limits: theory; a customer's request type "can be only verified ex post, i.e., after customers
  complete their service" (§3, p. 497).
- Reference behaviours it supports: none directly (grade D). It gives the decision structure (cut
  or join; admit or refuse) that the portable vocabulary's `admit` / `refuse` / `join_tail`
  actions already mirror [inference].
- BibTeX: `allon2012cutting`.

---

## Used only to find leads (not evidence)

**Furnham, A., Treglown, L. and Horne, G. (2020). The Psychology of Queuing. *Psychology* 11,
480-498. doi:10.4236/psych.2020.113033.** CC BY 4.0 (cached and committed:
`refs/he_furnham2020.*`). A narrative review in a Scientific Research Publishing journal, a
publisher whose peer review has been widely questioned [inference]. It pointed to Helweg-Larsen and
LoMonaco (2008), Dold and Khadjavi (2017) and Zhou and Soman (2003, 2008) (p. 484 and references).
**Its account of Milgram et al. (p. 483: "In only 10% of cases did the queuer physically not allow
the experimenter to cut in line ... the rate of objection increased to 91%") cannot be checked
against the paper and is not used.** It may refer to per-queue rates (anyone in the queue
objecting), which Table 3.2 above does not give [unverified].

---

## Stubs: confirmed to exist, full text not obtained

Each was confirmed on Crossref (DOI, authors, venue, pages). **None is summarised.**

### [Milgram-Intrusion]
- Title: Response to intrusion into waiting lines
- Authors, year, venue: Milgram, S., Liberty, H. J., Toledo, R. and Wackenhut, J. (1986).
  *Journal of Personality and Social Psychology* 51(4), 683-689. doi:10.1037/0022-3514.51.4.683
- Link tried: https://doi.org/10.1037/0022-3514.51.4.683 (APA PsycNet, paywalled); OpenAlex
  reports no open copy.
- Reason unavailable: paywalled; no open copy found.
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

### [Schmitt-QueueSocialSystem]
- Title: Intrusions into waiting lines: Does the queue constitute a social system?
- Authors, year, venue: Schmitt, B. H., Dubé, L. and Leclerc, F. (1992). *Journal of Personality
  and Social Psychology* 63(5), 806-815. doi:10.1037/0022-3514.63.5.806 (the issue's
  `[unverified lead]` is confirmed)
- Link tried: https://doi.org/10.1037/0022-3514.63.5.806; OpenAlex reports no open copy.
- Reason unavailable: paywalled; no open copy found.
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

### [Mann-QueueCulture]
- Title: Queue Culture: The Waiting Line as a Social System
- Authors, year, venue: Mann, L. (1969). *American Journal of Sociology* 75(3), 340-354.
  doi:10.1086/224787
- Link tried: https://www.journals.uchicago.edu/doi/10.1086/224787 (paywalled; also on JSTOR)
- Reason unavailable: paywalled; no open copy found.
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

### [HelwegLarsen-U2]
- Title: Queuing Among U2 Fans: Reactions to Social Norm Violations
- Authors, year, venue: Helweg-Larsen, M. and LoMonaco, B. L. (2008). *Journal of Applied Social
  Psychology* 38(9), 2378-2393. doi:10.1111/j.1559-1816.2008.00396.x (Crossref)
- Link tried: https://doi.org/10.1111/j.1559-1816.2008.00396.x; OpenAlex reports no open copy.
- Reason unavailable: paywalled; no open copy found.
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

### [DoldKhadjavi-JumpingQueue]
- Title: Jumping the queue: An experiment on procedural preferences
- Authors, year, venue: Dold, M. and Khadjavi, M. (2017). *Games and Economic Behavior* 102,
  127-137. doi:10.1016/j.geb.2016.12.002
- Link tried: https://doi.org/10.1016/j.geb.2016.12.002 and https://ideas.repec.org/a/eee/gamebe/v102y2017icp127-137.html
- Reason unavailable: paywalled; no working-paper version found.
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

### [OberholzerGee-MarketForTime]
- Title: A Market for Time: Fairness and Efficiency in Waiting Lines
- Authors, year, venue: Oberholzer-Gee, F. (2006). *Kyklos* 59(3), 427-440.
  doi:10.1111/j.1467-6435.2006.00340.x
- Link tried: https://www.econstor.eu/bitstream/10419/214280/1/2003-04.pdf (the 2003 working
  paper, open on EconStor)
- Reason unavailable: the journal version is paywalled; EconStor returned a bot-check page instead
  of the PDF. **It should open in an ordinary browser.**
- Date attempted: 2026-10-18
- Status: awaiting PDF from user
