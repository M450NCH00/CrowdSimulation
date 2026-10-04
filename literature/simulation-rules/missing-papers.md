# Missing papers — one consolidated list

> For issue [#22](https://github.com/M450NCH00/CrowdSimulation/issues/22). These sources were
> confirmed to exist but their full text could not be opened on 2026-10-04. **None is summarised
> anywhere in this review** — no abstract-based summary, no partly filled template. Each has a
> `[NOT OBTAINED]` stub in the sub-area file it would belong to. If you can supply the PDFs, a
> follow-up issue can add the summaries.

**Count: 5 papers** (all peer-reviewed) **+ 1 industry documentation source.**

## Papers

| # | Paper | Venue | Why it could not be opened | Link to try | Would go in | Why it matters |
|---|---|---|---|---|---|---|
| M1 | Vesentini, Muradore, Fiorini (2024). **A survey on Velocity Obstacle paradigm.** | *Robotics and Autonomous Systems* 174, 104645 | Paywall (Unpaywall reports no open copy) | https://doi.org/10.1016/j.robot.2024.104645 | [S1](s1-crowd-simulation.md) | **Highest priority.** This was the issue's `[secondhand]` seed. It is now **confirmed to exist** — title, authors, venue, volume and article number from Crossref — but unread. The issue judged it "likely the best single entry point for S1" and for covering the pre-window methods through a recent source. |
| M2 | van Toll, Pettré (2021). **Algorithms for Microscopic Crowd Simulation: Advancements in the 2010s.** | *Computer Graphics Forum* 40(2), 731–754 (Eurographics state-of-the-art report) | The open copy on HAL sits behind an automated-browser check the download tool could not pass; the publisher copy is paywalled | https://inria.hal.science/hal-03197198 (should open in an ordinary browser) | [S1](s1-crowd-simulation.md) | **High priority, and probably the easiest to get** — it is open access for a human with a browser. A survey of exactly the S1 literature, from a venue the issue names. |
| M3 | Karamouzas, Sohre, Narain, Guy (2017). **Implicit Crowds.** | *ACM Transactions on Graphics* 36(4) (SIGGRAPH 2017) | ACM download returned an access page | https://doi.org/10.1145/3072959.3073705 | [S1](s1-crowd-simulation.md) | Medium. A SIGGRAPH crowd-simulation method; [Sung-ArrivalTime] §2 describes it as energy-based and hard to run in real time for large crowds — a second-hand remark I have not been able to check. |
| M4 | Zhang, Li, Surynek, Kumar, Koenig (2022). **Multi-agent path finding with mutex propagation** (journal version). | *Artificial Intelligence* 311, 103766 | Paywall | https://doi.org/10.1016/j.artint.2022.103766 | [S3](s3-mapf-robotics.md) | Low. The ICAPS 2020 version was read and summarised as [Zhang-Mutex]. This is the version the issue actually named; whatever the journal version adds is not represented. |
| M5 | Zhou, Wang, Bandyopadhyay, Schwager (2017). **Fast, On-line Collision Avoidance for Dynamic Vehicles Using Buffered Voronoi Cells.** | *IEEE Robotics and Automation Letters* 2(2), 1047–1054 | Paywall (Unpaywall reports no open copy) | https://doi.org/10.1109/LRA.2017.2656241 | [S3](s3-mapf-robotics.md) | Medium. I identified it as a candidate from prior knowledge of the field, not from any source read here, and could not open it. **No description of its content is given**, because I have nothing I could cite for one. (I first drafted this cell saying [Grover-Deadlock] cites it; on checking that paper's reference list, the "Zhou et al. 2017" it cites is a different paper by different authors. Corrected before commit and logged in [search-log.md](search-log.md) §6.) |

## Industry documentation

| # | Source | Why it could not be opened | Link to try | Would go in |
|---|---|---|---|---|
| M6 | Unity Manual — "NavMesh Agent" and "Inner Workings of the Navigation System". `[industry, not peer reviewed]` | The pages returned a script-redirect stub rather than content | https://docs.unity3d.com/Manual/class-NavMeshAgent.html ; https://docs.unity3d.com/Manual/nav-InnerWorkings.html | [S2](s2-games.md) |

No statement about what the Unity pages say is made anywhere in this review.

## What obtaining these would change

- **M1 and M2 together** would most likely change [category-summary.md](category-summary.md) and
  [research-gap.md](research-gap.md): they are the two surveys of the sub-area (S1) where this
  review's sample is smallest and least systematic. The claim in research-gap.md §4 that no
  in-window category C rule for pedestrians was found is the one most exposed to them.
- **M3, M4, M5, M6**: I have no basis for saying what they would change. M4 is a journal extension
  of a paper already read, so it is the least likely to matter.
