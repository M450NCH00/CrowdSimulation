# x_head_on_6455ca5589: a person who gives way slows for an elderly, encumbered or distracted other

Issue #69 (RF-14). Sources keyed as in `../sources.md`.

- **Says (RF-11):** a person who gives way slows in their first plan when the other was described as
  elderly, using a cane, pulling a suitcase or looking at a phone. Found in 3 of 3 runs; predicts
  `first_slowed`.
- **Fidelity (RF-11):** 37 of 52 held out (0.71), **below** its baseline "always slows" (0.75).
- **Its format 4 translation (RF-31, the paid retry):** the person facing someone with a cane slows to
  0.75 of their speed, and if they tend to give way also follows a plan (0.95 m/s from 9.8 m).
- **Simulation (RF-18; RF-33's realistic crowd, verdict of record): harms.** It gridlocked the
  two-way flow on 1 seed of 30 (2 of 10 in RF-18's stress crowd).

## Step 1 numbers against the evidence

In the 216 sessions outside the exact-repeat set (RF-10's re-execution under `keep_line` and RF-30):

| First plan slows | Meeting a 25-year-old | Meeting a 70-year-old |
| --- | --- | --- |
| A 25-year-old | 137 of 262 (0.52) | **75 of 83 (0.90)** |
| A 70-year-old | 54 of 83 (0.65) | (none in the design) |

(4 plans with no recorded value left out.) RF-10's screen gives the same direction: the other being
70 makes a person slow, OR 3.44 [1.57, 7.57], uncorrected.

## Evidence

**For (age):** "Whenever an older adult was on a collision course with a young adult, the young adult
contributed more to the avoidance regardless of passing order" ([Rapos2021], abstract, Results;
17 older and 17 young adults, Canada). The Step 1 agents do the same: the younger person adjusts more
when meeting an older one.

**Passing distance:** Rapos2021 reports minimum predicted distances of 0.79 ± 0.18 m (older with young)
and 0.93 ± 0.17 m (two young), between the walkers. Step 1's resolved sessions keep a mean gap between
the two bodies of 0.41 m (older with young, n = 49) and 0.42 m (two young, n = 67); with the body radius
of 0.25 m, about 0.91 m between centres `[inference: assumes the default radius, which hallway.yaml marks
as a placeholder; a suitcase widens a body]`. Similar to the young pairs; unlike the study, the agents
pass an older person no closer.

**Mixed (slowing as the means):** in a head-on meeting walkers slow ([Moussaid2009], section 4.2); in
[Huber2014]'s head-on scenario they changed path, not speed; the one giving way "also adapts his speed"
([Olivier2013], abstract). So slowing is one of the ways people give way, not the only one.

**No evidence found** that people give way more to someone with a **cane**, a **suitcase** or a
**phone**. A visibly marked person does draw far more looks: breaches of civil inattention toward
"marked" recipients were 10-fold ([Arminen2023], abstract), which is attention, not giving way.

## Grade: Partly supported

Giving more of the avoidance to an older person is supported (Rapos2021), and the agents do it in
the same direction. The cane, suitcase and phone have no evidence, and slowing is only one of the
ways people give way.

## Decision (#55's table)

**Matches (partly), does not help → "a finding: record why".** The likely reasons, from RF-31 and RF-33:
- **The translation:** "slows" became "slow to 0.75 of your speed whenever you face a cane", applied
  by everyone who meets a cane, all the way to the passing. People in the studies above give way mostly
  by turning, and the young adult adjusts *more*, not by stopping the flow.
- **The ORCA layer and the crowd:** slowing in a dense two-way flow lets the oncoming stream close up,
  and one gridlock in 30 seeds counts as harm by the verdict rule fixed before RF-18.
- Stays staged, with its grade. Not dropped.
