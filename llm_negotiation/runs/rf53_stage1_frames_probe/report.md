# RF-53, stage 1: does thinking mode fix left and right? (issue #144)

Run on 2026-11-28, 03:32 to 04:15 UTC (a Saturday, so off-peak), on `deepseek-flash`, fingerprint
`bc19ba97cbe016479903222bb1578db6` on all 400 calls (RF-40's). **Cost USD 0.2106** of a USD 0.50 cap
(400 ledger lines); balance USD 1.59 before, **USD 1.38** after.

**What was sent.** RF-43's 20 static probes (`literature/frames-of-reference/probes.md`), frozen as
`configs/probe/frames_probes_v1.yaml`, each 10 times with thinking off and 10 times with it on. A probe
is one plain question with one right answer. The two arms differ only in the thinking setting and its
consequences: temperature 1.0 has no effect with thinking on, and the reply cap is 300 off and 8,000 on.

**How it was scored.** The reply's first line is read for one label by keyword (`negsim/probe/score.py`).
**Hand check:** all 400 first lines were read by eye against the scorer's label, and none was misread.
The tables are recomputed from `calls/` by `python -m negsim.probe.report`; they are in
`report_tables.md`, and the main ones are repeated below.

## Question 1: does thinking mode fix the left-and-right conversion, outside the simulation?

**Mostly, yes.** Thinking on answered 187 of 200 correctly (0.94, Wilson 95% interval 0.89 to 0.96),
thinking off 114 of 200 (0.57, 0.50 to 0.64); Fisher exact p < 0.0001. All 13 thinking-on misses are on
two probes, which are explained below.

| Group | What it tests | Thinking off | Thinking on | p |
| --- | --- | --- | --- | --- |
| A | a side said in the speaker's own frame | 11/30 (0.37) | 21/30 (0.70) | 0.02 |
| B | a side said in your frame | 20/30 (0.67) | 30/30 (1.00) | 0.0008 |
| C | as A and B, with `resolve_v9`'s facing note | 11/30 (0.37) | 30/30 (1.00) | < 0.0001 |
| D | you say which side of them you pass | 24/30 (0.80) | 30/30 (1.00) | 0.02 |
| E | walls named, no heading given | 21/40 (0.53) | 36/40 (0.90) | 0.0004 |
| F | walls named, heading given | 14/20 (0.70) | 20/20 (1.00) | 0.02 |
| G | a grid of lanes | 13/20 (0.65) | 20/20 (1.00) | 0.0083 |

(Fisher exact test, two-sided, per row: seven tests. With Holm's correction at 0.05, C, E, B and G hold.
A (p = 0.019) misses its threshold of 0.0167, so A, F and D do not hold under Holm, as the procedure
stops at its first miss. The "all" row is p < 0.0001.)

**Where thinking on still misses: probe 3, and cut-off replies.**
- **Probe 3** ("I'll pass you on my right"): 1 correct, 3 wrong, 6 cut off. The reasoning texts show
  why. **The sentence has two readings:**
  - "you will be on my right", which gives `probes.md`'s answer, left;
  - "I'll keep to my right", which gives right.

  The three "right" replies took the second reading and were consistent with it (for example: "he will
  move to his own right. You should move to your own right"). The six cut-off replies spent all 8,000
  tokens going back and forth between the two readings. So probe 3 measures the ambiguity of the
  English, not the frame conversion. **Without probe 3, group A is 20/20 with thinking on, against 8/20
  with it off.**
- **Cut off at the reply cap:** 10 of 200 thinking-on replies. Their reasoning used all 8,000 tokens
  (`reasoning_tokens` = 8,000, `finish_reason: length`, no answer), scored `unclear`. Six were on probe
  3, one on probe 13 and three on probe 15. **This shows that DeepSeek's `max_tokens` counts the
  reasoning**, which the documentation implies but does not say.

## The facing note (probes 7 to 9 against 1, 4 and 5)

**With thinking off, the note did not help, and on probe 9 it did worse.**

| With the note | Without it | Thinking off: with / without | Thinking on: with / without |
| --- | --- | --- | --- |
| p07 ("I'll keep to my left") | p01 | 0/10 / 1/10 | 10/10 / 10/10 |
| p08 ("plenty of room on your right") | p04 | 10/10 / 6/10 | 10/10 / 10/10 |
| p09 ("coming through on your right") | p05 | 1/10 / 4/10 | 10/10 / 10/10 |

- On p08, where the note does not apply, the note helped (10/10 against 6/10).
- On p09, where it also does not apply, it did worse (1/10 against 4/10). RF-43 feared this: the note
  invites a second conversion of words already in the listener's frame.
- With thinking on, all six are 10/10, so there is nothing left for the note to do.

## What goes wrong with thinking off: the step after the conversion

The thinking-off replies' one-sentence reasons show that **the conversion itself is mostly right**.
On p01 and p07, 19 replies are wrong. **17 of them state the conversion correctly** ("their left, which
is your right") and then move into that same side ("so you should move to your right to pass on the
opposite side"). The error is in the next step: making room means moving *away* from the side the other
person takes, and the model moves towards it. Probe 3's wrong replies state no conversion at all. Probe 2,
where the model's preference for moving right happens to be correct, shows the same pattern in 2 of its
3 wrong replies.

**Thinking off leans to "right":** right is the label in 74 of the 90 thinking-off replies of groups A to C
(all of which answered left or right), although the right answer is right in only 4 of those 9 probes.
That fits a bias towards keeping right, more than a misread frame.

## Question 4: does the reasoning show the conversion being done right?

A hand check of thinking-on reasoning texts: repeat 5 of every probe (20 texts), plus probe 3's three
wrong replies. **In all 23, the answer given is the one the reasoning reached.**
- **Converting by compass:** where the probe needs a conversion, the reasoning usually works it out with
  compass points or vectors, and gets it right in every text read. For example, on p07: "Person2's left
  when facing south is east ... In your frame facing north, east is right. So person2 shifts east = your
  right. Therefore you should move west = your left". The same happens on p17, p18 and p20.
- **Converting in words:** "when facing each other, your left is their right" (p10, p11).
- **Using a convention instead:** one text (p02) reached the right answer from a convention ("if both
  keep to their own right") rather than a conversion.
- **Not inventing a heading:** on the no-heading probes the reasoning says the direction of travel is
  not given, and spends many tokens doing so (2,291 on p13 and 1,529 on p15 in this sample). Over all ten
  repeats, p15's median of 6,050 reasoning tokens is the longest after probe 3's (8,000), and p13's mean
  (3,379) the longest after those two.

## Invented headings (probes 13 and 15)

| Probe | Thinking off: a side invented | Thinking on: a side invented |
| --- | --- | --- |
| p13 (compass walls) | 10/10 | 0/10 (1 cut off) |
| p15 (window and shop sides) | 9/10 | 0/10 (3 cut off) |

- **Thinking off invents a heading** almost every time ("You are facing Person 2 ... so the north wall
  is on your right"). Landmark names (p15) did no better than compass names (p13): 9 against 10.
- **Thinking on never invents one.** It says the side "cannot be determined", or runs out of tokens
  trying. This bears on AS5 and RF-48: in an absolute frame with no heading, an agent with thinking off
  will assume one.

## Question 3: cost, length and time

| | Thinking off | Thinking on |
| --- | --- | --- |
| Reasoning tokens a call | 0 | median 687, mean 1,629, 90th percentile 4,776, max 8,000 |
| Reply latency, seconds | median 0.6, mean 0.7 | median 4.6, mean 9.6, max 48.0 |
| Cost for 200 calls, off-peak | USD 0.0079 | USD 0.2027 (26 times as much) |

## What it means for stage 2 (RF-40's sessions with thinking on), not approved

- **Cost.** These estimates are rough `[inference]`. Stage 2's prompts are much longer than a probe and
  ask a harder question, so reasoning may well be longer than here.
  - The issue's formula is RF-40's cost plus USD 0.0014 (silent) or 0.0015 (talk) for each reasoning
    token a call.
  - At this run's mean of 1,629 tokens it gives about **USD 2.7 for silent and 2.9 for talk, about 5.6
    for both**, off-peak, at RF-40's numbers of calls.
  - The balance is USD 1.38, so stage 2 needs a top-up, or a pilot first to measure its own reasoning
    length.
- **Reply cap.** It must allow for the reasoning. At 8,000, 5% of probe replies were cut off, and a
  cut-off decision point would be an unreadable reply in a session. A larger cap (for example 16,000), or
  `reasoning_effort: low`, is a choice for stage 2.
- **Wall time.** At a mean of 9.6 s a call, RF-40's 4,697 silent and talk calls would take about **12.5
  hours** one after another `[inference]`, against about one hour with thinking off.
- **Temperature.** It has no effect with thinking on, so the noise floor (exact repeats) must be measured
  again (the issue's point).
- **The probes suggest** that thinking mode removes the frame errors behind RF-40's E1 to E3. Whether it
  also improves resolution in the simulation is stage 2's question, not this one's.

## Limits

- Ten repeats a probe, so a probe's share has a wide interval (for 10/10, 0.72 to 1.00).
- One wording per probe, written by the assistant from `probes.md` (the changes are listed in the probe
  file's header). Probe 3's wording is ambiguous, so its "expected" answer is one of two defensible ones.
- Temperature differs in effect between the arms, so only the shares correct are compared, not the spread.
- A probe is a question about a described scene, not a decision inside a simulation, with its timing,
  distances and history (RF-43's reason for the probe).
- The scorer reads the first line only. All 400 were checked by eye, but the reasons were read for a
  sample only: 23 thinking-on reasoning texts, and the thinking-off replies of p01, p02, p03 and p07
  (counted by a keyword pattern and spot-read).
