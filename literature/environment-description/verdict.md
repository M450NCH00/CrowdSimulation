# Verdict for negsim: describing multi-person scenes (Q6)

> **Proposal, not agreed.** For issue [#52](https://github.com/M450NCH00/CrowdSimulation/issues/52);
> needs the supervisor's sign-off (`CLAUDE.md`). Any change would be a later issue with a new frozen
> template version; nothing in `llm_negotiation/` was changed. Evidence: [findings.md](findings.md).

**The evidence in one line.** No study compares description formats for pedestrian conflicts (gap
G1); the closest evidence is a crowd simulator's perception rule ([Durupinar-AffectCrowd]) and two
spatial-task comparisons ([Chen-MAPFLLM], [Martorell-TextToSpace]). So this verdict picks a format
to **test**, not one shown to work.

## Proposed description method

1. **Keep text, keep negsim's egocentric prose lines.** No study found supports images for this
   (an image did worst in [Chen-MAPFLLM], Table 3). Keeping the existing per-person lines
   (`other_where`, `other_motion`, `other_body`, `other_age`, `other_gender`) keeps runs comparable
   with the `v1`/`v2` data already collected.
2. **Add a perceivability rule for who is described:** within a range, inside a field of view, not
   hidden by walls or bodies. This is [Durupinar-AffectCrowd]'s rule (8 m, 200°, occlusion; §3.1).
   The values for negsim are a design decision to make, not taken from the source.
3. **Describe the three nearest in full, nearest first; summarise the rest in one line** (count, how
   many are getting closer, distance range). Prompt length then stops growing after the third
   person, which matters for dense scenes ([Ntarouis-CrowdGenAgents] shows what happens without a
   cap). "Three" is Durupinar's choice, not a tested value.
4. **Give motion for everyone described in full** (speed, heading, whether the gap is closing), as
   negsim already does for one person. [Ntarouis-CrowdGenAgents] blames the missing herding on the
   lack of "trajectory information in the environmental representation" (§4.1).
5. **State capacities as capacities**, not only as widths ("only one person fits through at a
   time"), after [Park-GenerativeAgents]'s "one-person bathroom" failure (§7.2). `persona_v1.yaml`
   does this; the Layer 4 description gives only a width.

## What must be tested first (before freezing a template)

Each test uses the same frozen cases, changes one thing, and is run on **at least two models**
(results differed by backend in [Durupinar-AffectCrowd] and in issue #16):

- **T1, format:** prose (B) against one JSON line per person (D). Measure whether the decision
  changes (stance, who goes first), parse failures, and agreement between runs.
  [Martorell-TextToSpace] favours structured coordinates, but for a grid, one agent, and mostly
  smaller models.
- **T2, cap:** 1 in full (today), 3 in full + summary (C), everyone in full (B), at 2, 5 and 10
  people. Does the decision change when people beyond the third are only summarised? (Gap G2.)
- **T3, capacity:** the same doorway described by width alone against width plus an explicit
  capacity (gap G5).
- **T4, attributes:** with several people visible, vary one person's apparent age or gender, all
  else equal ([Yoldas-YieldBias]'s design), to see whether a decision turns on who stands where.

## Rough token cost per prompt (offline, DeepSeek-V3 tokenizer)

Situation block only, from [token-estimates.md](token-estimates.md); the rest of the prompt is a fixed
amount on top.

| Format | 2 people | 5 people | 10 people |
|---|---|---|---|
| A. negsim today (1 in full) | 220 | 220 | 220 |
| B. Prose, everyone in full | 301 | 545 | 940 |
| C. Proposed: 3 in full + summary | 333 | 448 | 448 |
| D. JSON line per person | 282 | 479 | 805 |

At $0.28 per million input tokens (`pipeline/config.py`), even 940 tokens is about $0.26 per
1,000 calls. Token length is not the constraint; the number of calls is.
