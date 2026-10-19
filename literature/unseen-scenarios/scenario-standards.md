# Q3. Scenario descriptions that do not depend on one simulator

> For issue [#36](https://github.com/M450NCH00/CrowdSimulation/issues/36) (PT-2), part of the
> portable-rules track (#34). **The portable-rules idea is a proposal and has not been agreed.**
> Everything under "Which scenario-card fields should borrow from it" is `[inference]`: a
> suggestion for a later issue, not a design decision.
>
> **The question.** How are test scenarios specified so that several simulators can run them? For
> each format: what one scenario contains, how a simulator consumes it, and what it cannot
> express (queues, service points, vehicles, scripted events, personas, communication).
>
> **Labels.** `[standard]`, `[documentation]`, `[preprint]` as in the issue. Locators are to the
> cached copy named in each entry (`refs/us_*`). Standards were read in their relevant sections
> only, as the issue allows; the sections read are listed in each entry.

**Summary.** Two families exist, and neither does what the FYP needs on its own.

1. **Test catalogues for evacuation models** (RiMEA, IMO, NIST TN 1822 / ISO 20414). Each test is a
   short prose description plus a figure: a geometry, a population, sometimes a stimulus (doors
   closed, counterflow added), and a qualitative or numerical expected result. Every simulator
   vendor re-builds the test by hand. None has queues, service points, vehicles, or rules about
   who goes first.
2. **Machine-readable scenario languages** (OpenSCENARIO, and JuPedSim's journeys in a
   simulator-specific way). These have an initial state, actors, and actions started by triggers,
   so a scenario *runs* rather than being re-typed. OpenSCENARIO's entities are road users; its
   pedestrians have a category but no persona. JuPedSim has queues and waiting sets, but only as a
   FIFO line released from outside.

ODD sits apart: it describes a *model*, not a *test*, and says so (entry [ODD-2020]).
SteerBench is the only one built around two- to four-person encounters of the FYP's kind
(doorway, narrow hallway, overtaking), with per-test pass conditions.

---

## Entries

### [RiMEA-4.1.1]: RiMEA Guideline for Microscopic Evacuation Analysis, version 4.1.1 `[standard]`

- **Publisher / Year / Link / Access:** RiMEA e.V. / 2025 (© 2004-2025) /
  https://rimeaweb.wordpress.com/wp-content/uploads/2025/09/rimea-4.1.1-d-e-1.pdf, linked from
  rimea.de / **open**, licensed CC BY-ND 4.0 (title page, p. 1). German and English in parallel
  columns. Cached: `refs/us_rimea_4.1.1_de_en.pdf`, text `refs/us_rimea_4.1.1_de_en.txt` (made
  with `pdftotext -layout`, so the English is the right-hand column). **Read:** contents (pp. 2-3),
  §3 categories (titles only, pp. 11-16), Annex 1 A2-A5 and Tests 1-16 (pp. 22-49).
- **What one scenario contains:**
  - The guideline groups simulation inputs into three categories: **Geometry, Population and
    Routes** (§§3.1-3.3, contents p. 3). Population includes "characteristics of the population",
    "initial distribution of agents" and "age distribution of population" (§§3.2.2-3.2.4).
  - The **tests** in Annex 1 are short prose specifications with a figure. Older tests state a
    geometry, a population and a numerical acceptance band, e.g. Test 1: a 2 m × 40 m corridor, one
    person at 1.33 m/s, and "the travel time should lie in the range of 26 to 34 seconds" (Test 1,
    p. 29). Newer tests use the headings **Background / Aim / Setup** (Test 12a, p. 37; Test 12d,
    p. 41; Test 16, p. 47), and some compare against empirical data: Test 16 uses "the 10% and 90%
    percentiles of the data of real life tests" as its reference (Test 16, p. 47).
  - Tests are grouped as **testing of components, functional verification, qualitative
    verification and quantitative verification** (Annex 1, A2-A5, contents p. 3).
- **How a simulator consumes it:** by hand. Each vendor builds the geometry and population in its
  own tool from the prose and figure, and reports results; for Test 8 the results "will be freely
  accessible to all on the RiMEA homepage" (Test 8, pp. 31-32). There is no file format.
  `[inference]` from the absence of any schema or file in the document.
- **What it cannot express:**
  - **queues and service points:** no test has a service point or a queue discipline `[inference]`
    (Tests 1-16, pp. 29-49);
  - **vehicles:** no test has a vehicle `[inference]`;
  - **scripted events:** only as a fixed setup step (e.g. a stated pre-movement distribution, Test
    5, p. 30), not as a trigger during a run `[inference]`;
  - **personas:** only as demographic parameter distributions (Test 7, "allocation of demographic
    parameters", p. 31);
  - **communication:** none `[inference]`.
- **Also relevant to Q1 (cross-scenario calibration).** RiMEA warns: "Model parameters which are
  highly relevant in one situation (e.g. the obstacle posed to the flow of persons by the corner in
  test 6) may be meaningless in another (e.g. test 4). A calibration process which only works with
  situation B may not provide a good value for the parameter used in the realistic simulation of
  situation A" (Annex 1, A2, "Limited requirements", p. 26).
- **Which scenario-card fields should borrow from it:** `[inference]` the **Background / Aim /
  Setup** headings; the **Geometry / Population / Routes** grouping of inputs; and a stated
  **acceptance band** with an empirical reference where one exists (Test 16's percentile band).

### [IMO-Circ1533]: IMO MSC.1/Circ.1533, Revised Guidelines on Evacuation Analysis for New and Existing Passenger Ships `[standard]`

- **Publisher / Year / Link / Access:** International Maritime Organization / 2016 /
  https://www.traffgo-ht.com/downloads/pedestrians/downloads/documents/MSC.1,Circ.1533,2016.pdf
  (a vendor's copy of the IMO document; IMO's own edocs link is printed in the footer) / **open
  copy, IMO copyright**. Cached on disk only: `refs/us_imo_circ1533.*`. **Read:** paras 1-11,
  Annex 3 and its Appendices 1-3.
- **Version.** The issue names **MSC.1/Circ.1238** (2007). Circ.1533 states: "This circular
  supersedes MSC.1/Circ.1238" (para. 11). Circ.1238 was also cached
  (`refs/us_imo_circ1238.*`) but is cited only through TN 1822's review of it.
- **What one scenario contains:**
  - Inputs fall into four categories, "GEOMETRICAL, POPULATION, ENVIRONMENTAL and PROCEDURAL"
    (Annex 3, Appendix 1, §2.1). Population is a fixed mix by **age band, gender and mobility
    impairment** (Table 3.1), with walking speeds drawn uniformly within a range per group (Table
    3.4).
  - Four **benchmark cases** (night and day, with all or some escape routes available; Appendix 1,
    §3.1.1).
  - Twelve **verification tests** in Appendix 2: component tests 1-7 (e.g. Test 4: "100 persons
    (p) in a room of size 8 m by 5 m with a 1 m exit ... The flow rate over the entire period should
    not exceed 1.33 p/s"), and qualitative tests 8-12 (counterflow, crowd dissipation, exit-route
    allocation, staircase, flow-density relation). Each has a geometry, a population and an
    expected result, e.g. Test 8: "the recorded duration increases with the number of persons in
    counterflow" (Annex 3, Appendix 2, paras 3-18).
  - **Quantitative verification is not required**: "there is insufficient reliable experimental
    data ... Until such data becomes available the first three components of the verification
    process are considered sufficient" (Appendix 2, para. 19).
  - **Repetitions:** "a minimum of 50 different simulations ... made up of at least 10 different
    randomly generated populations ... repeated at least 5 times" (Appendix 3, paras 1-2).
- **How a simulator consumes it:** by hand, as with RiMEA. Each model rebuilds the tests from the
  prose and figures. `[inference]`
- **What it cannot express:** queues appear only in the **simplified** (hand-calculation) method,
  where "a queue is formed" when a flow exceeds the maximum (Annex 2, pp. 14 and 16), not as a
  behaviour; no service points, no vehicles or boarding, no scripted events beyond closing doors
  between steps (Test 9, step 2), no communication. Personas exist only as the age/gender/mobility
  mix. `[inference]` for every absence.
- **Which scenario-card fields should borrow from it:** `[inference]` the **population mix by age,
  gender and mobility** (the closest existing precedent for the FYP's persona axes, see
  `dataset/personas.yaml`); the four **input categories**; and the **repetition rule** (several
  random populations × several seeds) for L0.

### [ISO-20414]: ISO 20414:2020, Fire safety engineering — Verification and validation protocol for building fire evacuation models `[standard]`, full text not obtained

Only the ISO catalogue page was used (cached on disk: `refs/us_iso20414_page.txt`). Per the issue,
the public description is used and the standard itself is stubbed.

- **What the public page says (and nothing more is claimed):** Edition 1, published 2020-11, 69
  pages, ISO/TC 92/SC 4; "last reviewed and confirmed in 2026. Therefore this version remains
  current". The abstract says it "includes a list of components for verification and validation
  testing as well as a methodology for the analysis and assessment of accuracy", with "the
  procedure for the analysis of acceptance criteria"; that the components "are divided into
  different categories" by model sophistication and scope; that "Annex A [is] a reporting template"
  and "exemplary application of verification and validation tests are presented in Annex B"; and
  that it "is not intended to cover aspects of transportation systems in motion (e.g. trains,
  ships)" (ISO page, Abstract and General information).
- **Stub (the standard itself):**
  - Title: Fire safety engineering — Verification and validation protocol for building fire
    evacuation models
  - Authors, year and venue: ISO/TC 92/SC 4 / 2020 / International Standard ISO 20414:2020
  - Link tried: https://www.iso.org/standard/78348.html
  - Reason unavailable: paywalled; no open copy found
  - Date attempted: 2026-10-18
  - Status: awaiting PDF from user
- **Note for the card.** The public abstract excludes "trains, ships" in motion. `[inference]` Bus
  and MRT boarding with a stationary vehicle is not obviously excluded, but nothing in the public
  text says the standard covers boarding either.

### [Ronchi-TN1822]: The Process of Verification and Validation of Building Fire Evacuation Models (NIST TN 1822) `[standard]`-adjacent technical report

- **Publisher / Year / Link / Access:** Ronchi, E., Kuligowski, E. D., Reneke, P. A., Peacock,
  R. D., Nilsson, D. / NIST Technical Note 1822 / November 2013 / doi:10.6028/NIST.TN.1822 /
  **open** (US government work). Cached: `refs/us_nist_tn1822.*`. It is the issue's
  `[unverified lead]`, now **confirmed** (title page and Crossref). **Read:** Abstract, §§1-3.1
  (pp. iii-25), §3.0's test structure, Verif.2.7 and 2.9; §4 skimmed for the acceptance-criteria
  step. Used here as an **open secondary source on the road to ISO 20414**: it was "prepared to
  contribute to the on-going effort made by the ISO/TC92/SC4 Working Group 7" (§1.1, p. 3). It is
  not ISO 20414 and its contents may differ from the standard.
- **What one scenario contains:** every suggested test has four parts: "1) Geometry ... 2)
  Scenario(s) ... 3) Expected result ... and 4) Test method", qualitative or quantitative (§3.0,
  p. 13). Tests are organised by five "core components": pre-evacuation time, movement and
  navigation, exit usage, route availability, flow constraints (§3.1, p. 14; Table 1). New tests
  beyond IMO's include **elevator usage**, **group behaviours**, people with movement
  disabilities, and **social influence** and **affiliation** (Table 1, p. 15).
- **How a simulator consumes it:** by hand; testers also list "the user's actions during the
  calibration" (§3.0, p. 13).
- **What it cannot express:** the elevator test has one occupant and the elevator is the only
  route ("Insert an occupant ... The elevator is the only egress component", Verif.2.7, p. 25), so
  it tests the mechanism, **not a contest for capacity**. No queue discipline, vehicles or boarding.
  `[inference]` for the absences. Note an internal inconsistency: the section heading calls the
  elevator test "Verif.2.7" (p. 24), while the summary paragraph calls it "Verif.2.8" (§3.1.2,
  p. 17).
- **Its warning about reusing tests outside their context**, which bears on transfer: the IMO
  tests "are often employed for the V&V of models outside their original context of use (e.g.
  building fires instead of maritime applications)" (Abstract, p. iii), and "they are designed to
  test populations which are specific to the maritime context" (§2.1, p. 12).
- **Which scenario-card fields should borrow from it:** `[inference]` the four-part test
  structure **Geometry / Scenario / Expected result / Test method**, and the habit of stating
  which **context of use** a test was designed for.

### [OpenSCENARIO-1.4]: ASAM OpenSCENARIO XML 1.4.0, storyboard, entities, conditions and triggers `[standard]` `[documentation]`

- **Publisher / Year / Link / Access:** ASAM e.V. / v1.4.0 (the newest of the versions the site
  lists: 1.3.0, 1.3.1, 1.4.0) /
  https://openscenario.asam.net/ASAM_OpenSCENARIO_XML/v1.4.0/07_components_scenario/07_02_storyboard_entities.html
  and `07_06_conditions_triggers.html` / **open to read online**, ASAM copyright. The issue's
  `latest/` link returned HTTP 404 on 2026-10-18. Cached on disk only:
  `refs/us_osc_v1.4.0_storyboard.txt`, `refs/us_osc_v1.4.0_triggers.txt`. **Read:** §7.2 and §7.6.
- **What one scenario contains:**
  - A **Storyboard** of an **Init** element that "sets the initial states ... such as the position
    and speed", where "it is not possible to specify conditional behavior", then **Stories** of
    **Acts** ("when"), **ManeuverGroups** ("who", assigning entities as actors), **Maneuvers**
    ("what") and **Events** that fire **Actions** "via user-defined Condition instances", and a
    **stopTrigger** (§7.2.1).
  - A **trigger** is an OR of condition groups, each an AND of conditions (§7.6.1, formula).
  - **Entities** are Vehicle, Pedestrian and MiscObject; "a Pedestrian is specified by a property
    pedestrianCategory" (§7.2.2). Groups can be addressed as an **EntitySelection** (§7.2.2.2).
- **How a simulator consumes it:** an XML file conforming to a published schema (the 1.4.0 schema,
  model and examples are offered as downloads on the same pages). Simulators implement the
  standard; optional features "may be ignored, depending on the simulator's support for this
  feature" (§7.2.2.7, on 3D models, Fig. 26).
- **What it cannot express:**
  - **personas**: only a pedestrian *category*; no age, mobility or other attributes are named in
    §7.2.2 `[inference]` from §7.2.2;
  - **queues and service points**: none in §§7.2 or 7.6 `[inference]`;
  - **communication between actors**: none in §§7.2 or 7.6 `[inference]`;
  - it **does** express vehicles and scripted events, which the evacuation catalogues lack.
- **Which scenario-card fields should borrow from it:** `[inference]` the split **initial state
  (no conditional logic) / actors / events started by triggers / stop condition**. That is the
  form needed to script "a newcomer arrives and tries to join mid-queue at t = 20 s" or "the bus
  door opens when the bus has stopped".

### [ODD-2020]: The ODD Protocol for Describing Agent-Based and Other Simulation Models: A Second Update (Grimm et al. 2020)

- **Publisher / Year / Link / Access:** Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U.,
  Gallagher, C., DeAngelis, D. L., Edmonds, B., Ge, J., et al. / 2020 / *Journal of Artificial
  Societies and Social Simulation* 23(2) 7, doi:10.18564/jasss.4259 /
  https://www.jasss.org/23/2/7.html / **open to read**, © JASSS. Cached on disk only:
  `refs/us_odd_grimm2020.txt`. Status: published, peer-reviewed. **Read:** full article text;
  supplements not read.
- **What one scenario contains:** ODD describes a **model**, in **seven elements**: "1. Purpose
  and patterns", "2. Entities, state variables and scales", "3. Process overview and scheduling",
  "4. Design concepts", "5. Initialization", "6. Input data", "7. Submodels" (§1 Introduction,
  Fig. 1). The "patterns" in element 1 are "the criteria you will use to decide when your model is
  realistic enough" (§4, "ODD learning materials and guidance"), and authors should also report
  patterns the model "consistently failed to reproduce", to avoid HARKing (§4, "Linking ODD to
  pattern-oriented modelling"). Note: the paper numbers "Design concepts" as element 4 in §1 and as
  "5. Design concepts" in §5 ("ODD for non-agent-based simulation models"); I follow Fig. 1.
- **How a simulator consumes it:** it does not. ODDs "are based on written text and intended to be
  read by humans. They are independent of the hardware and software used to implement the model"
  (§1). **Simulation experiments are deliberately out of ODD's scope**: "the same model can be used
  for different simulation experiments, and the same experiments are sometimes executed using
  different models" (§5, "ODD and description of simulation experiments"); a TRACE-based template is
  offered instead in Supplement S7 (not read).
- **What it cannot express:** a *test* as such, since experiments are out of scope (above).
  Queues, vehicles, personas and communication can all be *described* in prose; whether the
  design-concept list names communication explicitly is in the guidance supplement, which I did not
  read `[unverified]`.
- **Which scenario-card fields should borrow from it:** `[inference]` **purpose and patterns**,
  including patterns a rule is known *not* to reproduce; **entities and state variables** (who is
  in the scene and what can be observed about them); **initialization**. And one boundary: ODD's
  own authors keep the *experiment* separate from the *model*, which supports keeping the scenario
  card separate from the rule core.

### [SteerBench-2009]: SteerBench: a benchmark suite for evaluating steering behaviors

- **Publisher / Year / Link / Access:** Singh, S., Kapadia, M., Faloutsos, P., Reinman, G. / 2009 /
  *Computer Animation and Virtual Worlds* 20(5-6):533-548, doi:10.1002/cav.277 (confirmed on
  Crossref and on the paper's first page) / publisher's PDF read from a course website:
  https://ics-websites.science.uu.nl/docs/vakken/mcrws/papers_new/Singh%20et%20al%20-%202009%20-%20SteerBench.pdf
  / Wiley copyright. Cached on disk only: `refs/us_steerbench_singh2009.*`. Status: published,
  peer-reviewed. The issue's `[unverified lead]` is **confirmed**. **Read:** full text.
- **What one scenario contains:** "38 scenarios ... a total of 56 test cases" in five categories,
  from "simple validation scenarios" and "basic one-on-one interactions" to "large-scale scenarios"
  (section "Overview of SteerBench", Tables 1-5). "Each test case specifies a number of agents and
  static objects. Static objects are specified by a bounding box. Agents are specified by their
  size, initial position, initial direction, desired speed, and target location(s). Additionally,
  each agent has a set of weights that configure the evaluation process. Finally, each test case
  also specifies conditions that define 'passing' or 'failing'" (same section). Scenarios include
  **Doorway-two-way** ("two oncoming agents walk through a doorway from opposite sides. One agent
  must ...") and **overtaking** in a hallway (Table 2), and **deadlock avoidance** is a stated design
  goal: "stepping out of the way or backtracking" (section "Test Case Design Choices").
- **How a simulator consumes it:** "SteerBench provides a C++ library that reads and writes a
  specific file format"; the user records "the position, direction, and goal target of every agent
  for every frame", and the evaluator computes metrics "blind to the specifics of the steering
  algorithm" (Fig. 1 and the workflow paragraph; Conclusion). Users can write custom scenarios in
  the same format (section "Customizing the Suite").
- **What it cannot express:** agents are "1 m" discs at "1.3 m/second" approximating "typical
  humans" (section "Customizing the Suite"), so **no personas**; no queues as a service discipline (it has
  "crowd queuing" only as a crowd behaviour, "Test Case Design Choices"); no vehicles, scripted
  events or communication `[inference]`.
- **Which scenario-card fields should borrow from it:** `[inference]` per-agent **start, heading,
  speed and goal**; **pass/fail conditions written into the case**; and evaluation **from logged
  trajectories only**, independent of the algorithm, which is exactly what makes a test portable
  across simulators.

### [JuPedSim-1.4.2]: JuPedSim routing concepts: journeys, stages and transitions `[documentation]`

- **Publisher / Year / Link / Access:** JuPedSim project (Forschungszentrum Jülich) / docs for
  version 1.4.2 ("stable") / https://www.jupedsim.org/stable/concepts/routing.html / **open**.
  Cached on disk only: `refs/us_jupedsim_routing.txt`. **Read:** the whole routing page.
- **What one scenario contains:** routes are networks called **Journeys**, with **Stages** as nodes
  and **Transitions** as edges ("Route planning"). Stage types: **Waypoint** (reach within a
  distance), **Exit** (agent removed), **Waiting Queue** ("agents will wait at predefined
  positions ... at the first available spot. When agents leave the queue, the other agents will move
  up"; release needs "a signal ... that the first n agents in the queue are permitted to exit"),
  and **Waiting Set** (positions filled in order; active or inactive) ("Stages"). Transitions are
  fixed, round-robin (weighted) or least-targeted ("Transitions").
- **How a simulator consumes it:** through JuPedSim's own Python API (`add_queue_stage`,
  `JourneyDescription`, ...); it is a vocabulary inside one simulator, not an exchange format.
- **What it cannot express:** a queue is a fixed, ordered set of spots that agents join at "the
  first available spot" and leave only when released from outside ("Waiting Queue"). So
  `[inference]` **queue cutting** (joining part-way along) and **admitting or refusing** a newcomer
  are not stage behaviours; a vehicle door or lift would have to be modelled as a queue or waiting
  set released by a script. No personas or communication on this page.
- **Which scenario-card fields should borrow from it:** `[inference]` a **journey of stages**
  (waypoint, queue, waiting area, exit) as the simulator-neutral way to state *where people are
  trying to go and where they must wait*. It is the one source that names queues and waiting areas
  at all.

---

## Comparison table

✓ = expressed; ~ = partly, or only as a fixed parameter; ✗ = not expressed in the sections read.
Every ✗ is `[inference]` from the sections read.

| Format | Geometry | Population / personas | Goals / routes | Scripted events (triggers) | Expected result / pass criterion | Queues, service points | Vehicles, boarding | Communication | How consumed |
|---|---|---|---|---|---|---|---|---|---|
| [RiMEA-4.1.1] | ✓ prose + figure | ~ demographic distributions | ✓ | ~ setup only | ✓ bands; some empirical | ✗ | ✗ | ✗ | rebuilt by hand |
| [IMO-Circ1533] | ✓ prose + figure | ~ age × gender × mobility mix | ✓ | ~ between steps | ✓ mostly qualitative | ✗ (hand-calc queue only) | ✗ | ✗ | rebuilt by hand |
| [ISO-20414] | not read | not read | not read | not read | ✓ (acceptance criteria, per abstract) | not read | trains/ships in motion excluded | not read | not read |
| [Ronchi-TN1822] | ✓ | ~ groups, disabilities | ✓ | ~ | ✓ four-part test | ✗ | ✗ (elevator, one person) | ~ social influence test | rebuilt by hand |
| [OpenSCENARIO-1.4] | via road network | ~ pedestrian category only | ✓ via actions | ✓ storyboard + triggers | ✗ (not in §§7.2, 7.6) | ✗ | ✓ | ✗ | XML + schema, many tools |
| [ODD-2020] | ✓ prose | ✓ prose | ✓ prose | ✓ prose | ~ "patterns" | ✓ prose | ✓ prose | ✓ prose | read by humans; not executable |
| [SteerBench-2009] | ✓ boxes | ✗ uniform agents | ✓ targets | ✗ | ✓ per-case pass/fail | ✗ | ✗ | ✗ | file format + C++ library |
| [JuPedSim-1.4.2] | ✓ (API) | ✗ on this page | ✓ journeys | ~ release signals from a script | ✗ | ✓ FIFO queue, waiting set | ✗ | ✗ | one simulator's API |

**What no format covers.** `[inference]` None of the eight states **who should go first** and
**why** in a contested resource, which is exactly what a conflict rule decides; none has
**communication between agents** as a scenario element; and only JuPedSim has a queue, with no
way to join it part-way. A scenario card for queue cutting, boarding/alighting and lift capacity
therefore has to add those fields itself (see `test-protocol-draft.md`, "Scenario card").
