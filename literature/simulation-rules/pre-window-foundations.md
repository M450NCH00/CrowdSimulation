# Pre-window foundations — pointers only

> **This file contains no summaries, by rule.** Issue
> [#22](https://github.com/M450NCH00/CrowdSimulation/issues/22) restricts summaries to papers
> published in 2016 or later. The methods below predate that window. Each is recorded as a pointer:
> name, authors, year, and a one-line statement of the rule. None has a template entry anywhere in
> this review, and **none was opened or read for this issue.**

Companion files: [S1](s1-crowd-simulation.md) · [S2](s2-games.md) · [S3](s3-mapf-robotics.md) ·
[S4](s4-traffic-vehicles.md) · [rule catalogue](rule-catalogue-simulation.md) ·
[search log](search-log.md) · [refs](refs-simulation-rules.bib)

## What each column is, and where it comes from

- **Bibliographic record** — confirmed in Crossref on 2026-10-04 (cached as
  `refs/sr_cr_prewindow.json`) unless the row says otherwise. I checked that each returned title
  matched the one I was looking for.
- **One-line rule** — **taken from the in-window source named in the last column, not from the
  original paper.** It is that source's description of the method. Where the wording is a
  quotation it is in quotation marks. I have not checked any of these statements against the
  originals, so each is a second-hand characterisation and should be treated as such.
- **Covered through** — the 2016-or-later entry in this review that describes the method, which
  is how the issue asked for the substance to be covered.

## The list

| # | Method | Authors, year, venue | One-line statement of the rule (as given by the in-window source) | Covered through |
|---|---|---|---|---|
| P1 | **Velocity obstacle (VO)** | Paolo Fiorini, Zvi Shiller, 1998, *Int. J. Robotics Research* 17(7), 760–772 | Treat each neighbour as moving at constant velocity; exclude the velocities that would lead to collision and choose one outside that set. | [SunshineHill-RVO-ORCA] §19.2; [Charlton-FastCrowd] §2; [MartinezBaselga-AVOCADO] §I, §III |
| P2 | **Reciprocal velocity obstacles (RVO)** | Jur van den Berg, Ming Lin, Dinesh Manocha, 2008, IEEE ICRA, pp. 1928–1935 | "Each agent would move only halfway out of the way of a collision, anticipating that the other agent would do its part". | [SunshineHill-RVO-ORCA] §19.2.1; [Sudkhot-BDI-RVO] §2.2; [Epic-UnrealAvoidance] Overview |
| P3 | **Optimal reciprocal collision avoidance (ORCA)** | Jur van den Berg, Stephen J. Guy, Ming Lin, Dinesh Manocha, 2011, in *Robotics Research* (Springer Tracts in Advanced Robotics), pp. 3–19 | For each neighbour build a half-plane of velocities that avoid collision within a time horizon; take the velocity inside all half-planes closest to the preferred one. | [Charlton-FastCrowd] §3; [Sung-ArrivalTime] §3.4; [SunshineHill-RVO-ORCA] §19.5; [MartinezBaselga-AVOCADO] §IV-A; [Dergachev-ORCA-MAPF] §II, §IV |
| P4 | **Social force model** | Dirk Helbing, Péter Molnár, 1995, *Physical Review E* 51(5), 4282–4286 | Move pedestrians by summing an attraction toward the goal with repulsions from other pedestrians, in analogy with Newtonian forces. | [Tordeux-CFSM] §1; [Charlton-FastCrowd] §2; [Xu-AVM] §1 |
| P5 | **Boids** | Craig W. Reynolds, 1987, *ACM SIGGRAPH Computer Graphics* 21(4), 25–34 | Simulate flocks from interactions between individuals. *(The in-window source gives no more than this — it names the model and says only that it is "for simulating flocks based on interactions between individuals".)* | [Sung-ArrivalTime] §2 |
| P6 | **Steering behaviours (obstacle avoidance)** | Craig W. Reynolds, 1999, *Proc. Game Developers Conference*, pp. 763–782 — **not in Crossref; recorded as cited in [Martel-ACSyndicate]'s reference list** | Give the agent "a lateral pushing force and a braking force" to clear a circular obstacle. | [Martel-ACSyndicate] §15.2.2 |
| P7 | **Optimal velocity model** (road traffic) | M. Bando, K. Hasebe, A. Nakayama, A. Shibata, Y. Sugiyama, 1995, *Physical Review E* 51(2), 1035–1042 | Set speed as a function of the spacing to the vehicle in front. | [Tordeux-CFSM] §2.1 ("The approach is borrowed from road traffic model") |
| P8 | **Prioritised planning** | Michael Erdmann, Tomás Lozano-Pérez, 1986 (IEEE ICRA, pp. 1419–1424, per Crossref); cited in the MAPF literature as 1987, *Algorithmica* 2, 477–521 (per [Zhou-LSRP]'s reference list — **the journal record was not confirmed in Crossref**) | Agents "sequentially plan paths according to their unique priorities while avoiding conflicts with previously planned paths". | [Okumura-PIBT] §2.2; [Wang-MAPFSurvey] §3.4; [Yang-S2AN] §2.2 |
| P9 | **Cooperative pathfinding (HCA\*, WHCA\*)** | David Silver, 2005, *Proc. AAAI Conf. on Artificial Intelligence and Interactive Digital Entertainment* 1(1), 117–122 | Prioritised planning in a shared space-time reservation; the windowed form "repeatedly plans fixed-length (windowed) paths for all agents". | [Okumura-PIBT] §2.2 (which notes PIBT is this with a window of one); [Ma-TokenPassing] §4.1 |
| P10 | **Push and Swap** | Ryan Luna, Kostas E. Bekris, 2011, IJCAI, pp. 294–300 — **recorded as cited in [Zhou-LSRP]'s reference list; the Crossref search returned only a related AAAI abstract by the same authors** | Two primitives: "push" an agent toward its goal, and "swap" two agents' locations without disturbing the others. | [Okumura-PIBT] §2.2 |
| P11 | **Push and Rotate** | Boris de Wilde, Adriaan W. ter Mors, Cees Witteveen, 2013, AAMAS, pp. 87–94 (journal version: *J. Artificial Intelligence Research* 51, 443–492, 2014) | A corrected, complete variant of Push and Swap for arbitrary graphs. *(The in-window source says only that Push and Swap "is incomplete as pointed out in" this paper.)* | [Okumura-PIBT] §2.2, §5.1.1; [Dergachev-ORCA-MAPF] §IV-C, which uses it as its fast solver and calls it "a complete, polynomial-time algorithm" |
| P12 | **Conflict-Based Search (CBS)** | Guni Sharon, Roni Stern, Ariel Felner, Nathan R. Sturtevant, 2015, *Artificial Intelligence* 219, 40–66 | Plan each agent's cheapest path independently; when two paths conflict, branch, forbidding one agent or the other from the conflicting vertex or edge at that time. | [Zhang-Mutex] §2.2; [Wang-MAPFSurvey] §3.1; [Dergachev-ORCA-MAPF] §II |
| P13 | **Priority inheritance** (real-time systems) | L. Sha, R. Rajkumar, J. P. Lehoczky, 1990, *IEEE Transactions on Computers* 39(9), 1175–1185 | A low-priority holder of a resource temporarily takes on the priority of the higher-priority party waiting for it. | [Okumura-PIBT] §1, §4.1.1 |
| P14 | **Autonomous intersection management / reservation; first-come-first-served** | Kurt Dresner, Peter Stone, 2004, AAMAS, pp. 530–537; journal version 2008, *J. Artificial Intelligence Research* 31, 591–656 | Divide the intersection into cells and assign them to vehicles "in a roughly First-In-First-Out (FIFO) manner"; vehicles request a time slot from an intersection manager. | [Xu-TreeSearch] §I; [Mariani-CoordSurvey] §3.2.1; [Wang-MAPFSurvey] §3.4 |

## Notes

- **Why the list is this long and no longer.** These are the pre-window methods that the in-window
  entries actually name and describe. I have not added foundational methods I know of but that no
  in-window source I read describes — doing so would mean stating a rule with no source at all.
- **One pre-window rule is already in the repository.** Issue #20's catalogue includes a
  pedestrian cell-contention rule from 2014 (Bouzat & Kuperman, rule R9 in
  [`../game-theory/candidate-rule-catalogue.md`](../game-theory/candidate-rule-catalogue.md)). It
  is outside this issue's window and is not repeated here, but it matters for
  [research-gap.md](research-gap.md) §4, because it is a category C rule for pedestrians and this
  review found none in-window.
- **A pre-window lead with no row.** A late web search surfaced a 2003 cellular-automaton rule for
  two pedestrians wanting the same cell (Ansgar Kirchner, Katsuhiro Nishinari, Andreas
  Schadschneider, "Friction effects and clogging in a cellular automaton model for pedestrian
  dynamics", *Physical Review E* 67(5); record confirmed in Crossref,
  `refs/sr_cr_late_additions.json`). It has no row because no in-window source I read describes
  it, so I have no sourced one-line statement to give. It is recorded in
  [search-log.md](search-log.md) §5 as a lead.
- **A method the issue named that has no row: none.** The issue listed ORCA, RVO, the social force
  model, boids and Conflict-Based Search; all five are above (P2–P5, P12).
