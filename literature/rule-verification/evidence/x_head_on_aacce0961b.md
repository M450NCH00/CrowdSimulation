# x_head_on_aacce0961b: a person who holds their ground keeps their line and slows only at close range

Issue #69 (RF-14). Sources keyed as in `../sources.md`.

- **Says (RF-11):** a person who holds their ground keeps their line at full speed at the first
  decision and only steps aside or slows at close range. Found in 2 of 3 runs; predicts
  `first_slowed`, reading the person's own assertiveness.
- **Fidelity (RF-11):** 43 of 52 held out (0.83) against 0.75: the one kept rule that beats its
  baseline. RF-10's screen: own assertiveness makes a first plan slow less, OR 0.26 [0.14, 0.48],
  Holm-significant.
- **Simulation:** none. Its format 4 translation gave roles by a condition that holds for both people,
  so it never matched (0 of 76 sessions), and the loader now refuses it (`constant_roles`, RF-31). It was
  not in RF-18's rule sets.

## Evidence

**For (the behaviour by role):** "the crossing order impacts both the contribution and the strategies
used: the participant giving way contributes more than the one passing first … Both walkers reorient
their path but the participant giving way also adapts his speed" ([Olivier2013], abstract). The one
who goes on keeps their speed and turns a little; the one who gives way also slows. That is the
behaviour the rule describes.

**Against (the reason):** "we investigated whether crossing order, path, and speed adjustments
correlate with subject-specific parameters, such as gender, height, and personality traits … individuals'
collision avoidance behavior was not correlated with any of these factors"; instead initial speed and
heading predicted who crosses first with 95% confidence 2.5 m before the crossing ([Knorr2016],
abstract). Which personality traits were measured is not in the abstract `[needs full text]`.

## Grade: Partly supported

What a person who goes on does matches the studies (Olivier2013). Why they go on does not: in people,
who goes first follows from speed and heading, not from personality (Knorr2016), so a rule that
reads assertiveness reads the wrong cause. As a model of how the LLM agents decide, it is the
strongest of the round; as a model of people, it is half right.

## Decision (#55's table)

**Matches (partly), not tested in the simulation** (it could not be translated into a runnable rule).
Recorded why: **the translation**. Format 4 reads one's own disposition only inside an own-only
condition, which cannot assign roles (RF-31, finding 1). Given Knorr2016, a later version might assign
the roles by speed and heading instead, which format 4 can read. Stays staged, with its grade.
