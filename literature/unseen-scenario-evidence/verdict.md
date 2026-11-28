# Verdict: is there human evidence to test unseen scenarios against?

> Issue [#37](https://github.com/M450NCH00/CrowdSimulation/issues/37) (PT-3 of track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34)), 2026-10-18. Grades and the
> statements cited are in [`reference-behaviours.md`](reference-behaviours.md); **the grading scale
> is a proposal**. Track #34 itself is a proposal, not agreed.

| Scenario | Best evidence obtained | Grade | Strong enough to test against? |
|---|---|---|---|
| **Queue cutting** (not yet in `scenarios.yaml`) | Milgram et al.'s 1978 New York field experiment (129 queues) and Schmitt et al.'s (Grand Central), both read only as tables reproduced in an open chapter; Langer 1978 and Folkes 1985 for asking to go first | B `old` `W` (`repro` for the intrusion data) | **Yes, for the pattern, not the exact rates.** Who objects (directly behind, QC-1), how many intruders (QC-3), friend vs stranger (QC-4), size of favour (QC-7), kind of reason (QC-6) |
| **`mrt_door_alight_board`** | London Underground video (2014-2015) and two London lab experiments | B/C `W` | **Partly.** Alighting first and door-side waiting, yes (BA-1, BA-2, BA-4). **How often people board before alighting ends: no number** (BA-8; two studies stubbed) |
| **`bus_queue_boarding`** | Nothing on boarding order; 8 queue-intrusion trials at a New York bus boarding queue (1978) | none | **No.** Two Singapore bus studies are stubbed |
| **`lift_boarding_capacity`** | Taipei MRT field observation, 2018, 604 lift trips | B `EA` | **Yes, for priority only** (LE-1, LE-2: full priority in 24% of cases, none in 49%). Who takes the last place among ordinary users: nothing |
| **`escalator_entry_merge`** | London Underground's Holborn pilot, 2015 | B `W` `off` | **Weakly.** Compliance with "stand on both sides" only while staff ask (LE-3). Nothing on step-on timing or merging at the escalator mouth |

**Singapore (Q4).** No Singapore study observing any of the five behaviours was found (searches in
[`singapore.md`](singapore.md) §4). Singapore supplies the **norms it promotes** (give way to
alighters; priority queues; hold the handrail), one perception survey now under methodology review,
one platform-waiting study (SG-1), and escalator incident counts (SG-3). **Every reference behaviour
for the Singapore scenarios must therefore be borrowed from London, New York or Taipei, and labelled
so.**

**Q5 (age and gender).** Almost nothing is measured in these scenarios: a female requester got more
compliance in Langer et al. (confounded); older users dominate bulky-item escalator incidents in
Singapore. Persona differences by age or gender in these scenarios **cannot be checked against
human data** from these sources.

**Three things for the supervisor:**

1. **Is a verbatim table reproduced in another work acceptable evidence?** QC-1 to QC-5 depend on
   it (work log A6). If not, they drop to grade C until the 1986 and 1992 papers are obtained.
2. **Fourteen sources need a library or browser download** ([`missing-papers.md`](missing-papers.md)).
   The most valuable: Milgram et al. 1986; Schmitt et al. 1992; the CityU thesis and Baali et al.
   2024 on boarding before alighting (they would fill BA-8); the two Singapore bus studies.
3. **`scenarios.yaml` wording**: `escalator_entry_merge` mentions a Singapore "stand on both sides"
   campaign; no source found supports it. The official advice found is "hold the handrail"; a Hong
   Kong source says Singapore advises standing on the left and walking on the right.

**Bottom line.** Queue cutting is the best-evidenced unseen scenario, which makes it the natural
first held-out test, but its evidence is old, Western, and partly second-hand. Train doors and lifts
can support a few pattern-level tests. Bus boarding and escalator merging cannot yet. **No statement
reaches grade A.**
