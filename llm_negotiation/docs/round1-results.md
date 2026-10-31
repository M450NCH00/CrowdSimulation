# Round 1 results: head-on in a corridor (RF-15, issue #70)

The results of round 1 of the resolve-first track (#55), gathered for the interim report (due 25 January
2027) and the next supervisor meeting. Round 1 is the only round finished. Rounds 2 (a narrow passage)
and 3 (someone behind says "excuse me") are planned work, and this document is to be updated when they
finish.

**Every number has a source.** Paths are from the repository root. `runs/` means `llm_negotiation/runs/`.
A number with no file beside it is derived in the text from numbers that have one. Nothing here is new
except `runs/rf15_round1_keep_line_analysis/`, RF-8's existing analysis rerun on the execution of record
(section 1). No model was called for this document.

**How to read the claims.** Round 1's results are about an LLM (`deepseek-flash`) in a simulated corridor.
They are not findings about people, except where section 3 compares them with published studies, and even
there the settings differ (`docs/human-targets.md`).

Contents: 1. Data and execution. 2. Step 1, can the agents resolve it? 3. Steps 2 and 3, the rules and how
they compare with people. 4. Step 4, the factors and the mapping. 5. The full simulation. 6. Method and
limits. Appendix: the compact mapping.

## 1. Data and execution

Round 1 is two people meeting head-on in a corridor (`wide_corridor_head_on`), on two geometries (walking
lines aligned, and 20 cm apart), under three conditions: **independent** (each agent decides alone),
**non-verbal** (each sees the other move and signal) and **talk** (they can also speak).

| | |
| --- | --- |
| Design | 16 two-level factors in a 2^(16−11) resolution IV fraction: 32 cells × 2 geometries × 3 conditions = 192 design sessions; plus 48 exact repeats and 48 sessions in counterfactual pairs: 288 (`runs/rf10_round1_head_on/screen_report.md`, section 1) |
| Model and template | `deepseek-flash`, core template `resolve_v6`, reply cap 400 tokens (`runs/rf10_round1_head_on/config.json`) |
| Measure | `plan_only`: the agents' own plans replayed with no collision avoidance between them; a session resolves if both leave the zone with no collision, no near miss and no deadlock, within the time limit. `plan_orca`: the same plans with ORCA underneath (`docs/resolution.md`) |

**The execution of record is `keep_line`.** RF-10 (#65) ran under `as_prompted` execution, which
turned out to undo sidesteps: a step with no turn steered the agent back to its starting line (RF-29,
#101). From RF-29 on, every result uses `protocol.execution: keep_line`. The agents' replies are the same
under both; only how a plan is carried out differs.

- Independent: RF-10's 96 sessions carried out again under `keep_line`, with no model call
  (`runs/rf10_round1_head_on_keep_line/NOTE.md`).
- Non-verbal and talk: RF-30's run (#104), RF-10's sessions with every first prompt word for word, under
  `keep_line` (`runs/rf30_round1_head_on_keep_line/comparison_report.md`).
- **RF-8's factor analysis rerun on these 288 sessions for this document**, with RF-10's settings (seed 63,
  Holm's correction over the whole report): `runs/rf15_round1_keep_line_analysis/` (`NOTE.md` gives the
  command). RF-10's own analysis, under `as_prompted`, is kept unchanged as the record of that run.

## 2. Step 1: can the agents resolve it?

**Answer: barely, in pairs; not in groups or crowds.**

### 2.1 Pairs (the gate)

The gate was fixed before RF-10's run: the agents resolve the encounter type if at least 0.50 of the 192
design sessions resolve in `plan_only`. The threshold is a judgement, not a sourced number.

| | Resolved | Rate (95% CI) |
| --- | --- | --- |
| **All three conditions (the gate)** | **102 / 192** | **0.53 (0.46 to 0.60): passes narrowly** |
| Independent | 35 / 64 | 0.55 (0.43 to 0.66) |
| Non-verbal | 37 / 64 | 0.58 (0.46 to 0.69) |
| Talk | 30 / 64 | 0.47 (0.35 to 0.59) |
| Walking lines aligned | 55 / 96 | 0.57 (0.47 to 0.67) |
| Walking lines 20 cm apart | 47 / 96 | 0.49 (0.39 to 0.59) |
| Baseline: `plan_orca` (the plans with ORCA underneath) | 106 / 192 | 0.55 (0.48 to 0.62) |
| Baseline: plain ORCA | 0 / 192 | 0.00 (0.00 to 0.02) |

Source: `runs/rf30_round1_head_on_keep_line/analysis/gate_pooled.md`. The interval includes 0.50: head-on
passes on the point estimate, not by a clear margin. The user decided on 2026-10-26 that it goes on to
extraction (#55). Plain ORCA never collides in these sessions but always comes within the near-miss
distance, so it never counts as resolved (`runs/rf12_round1_head_on/translation_report.md`, finding 3).

**How the execution rule mattered.** Under `as_prompted` the same plans resolved 59 of 192 (0.31): each
condition gained under `keep_line` (independent 22 → 35, McNemar p = 0.0002; non-verbal 17 → 37,
p = 0.0008; talk 20 → 30, p = 0.099) (`runs/rf30_round1_head_on_keep_line/comparison_report.md`, section 3;
`runs/rf29_round1_head_on_sidestep/comparison_report.md`).

**Changing the description or the model did not help** (all independent, 64 sessions, against
`resolve_v6`'s 22 under `as_prompted`):

| Change | Resolved | Paired test | Source |
| --- | --- | --- | --- |
| `resolve_v7`: where the other is against one's line, the other's width, direction to 1° (RF-27) | 17 / 64 | p = 0.44 | `runs/rf27_round1_head_on_v7/comparison_report.md` |
| `deepseek-v4-pro`, the same prompts (RF-28) | 18 / 64 | p = 0.57 | `runs/rf28_round1_head_on_v4pro_cap600/comparison_report.md` |
| Under `keep_line`: RF-10's plans / `resolve_v7` / the sidestep / v4-pro (RF-29) | 35 / 27 / 27 / 21 of 64 | v4-pro worse, p = 0.024 | `runs/rf29_round1_head_on_sidestep/comparison_report.md` |

### 2.2 Independent, non-verbal and talk

**Signalling and talking did not help.** Paired by cell, no condition differs from another (McNemar
p = 0.86, 0.49, 0.30). With a signal seen, 29 of 49 non-verbal sessions resolved, against 8 of 15 without;
in talk, 17 of 34 with a message, against 13 of 30 without (`runs/rf30_round1_head_on_keep_line/comparison_report.md`).
**The reason: the signals and words do not carry the side.** Nods, eye contact and "wave on" make up nearly
all signals, and only 4 of 92 messages name a side (same file).

**Decision points.** An independent agent decides once. Non-verbal and talk sessions used 3.4 and 3.5 more
decision points a session than independent ones (`runs/rf15_round1_keep_line_analysis/report.md`, section 1);
in RF-9's pilot most interactive agents reached the cap of 3 (`runs/rf_pilot_v2/pilot_report.md`, section 2).

### 2.3 How it fails

**The "pavement dance".** In most remaining collisions both stepped aside, towards the same wall
(non-verbal 16 of 22, talk 19 of 26) (`runs/rf30_round1_head_on_keep_line/comparison_report.md`). Of the 102
resolved, 66 passed keeping right (same file). The model leans right but does not coordinate on it: in
RF-11's main table only 66 of 152 first plans turn right (`runs/rf11_round1_head_on/extraction_report.md`,
section 4).

### 2.4 Beyond two people (Step 1 only)

| Setting | Resolved | Against | Source |
| --- | --- | --- | --- |
| Groups of 3 or 4, independent (RF-32) | 4 / 64 (0.06) | pairs 35 / 64, p < 0.0001 | `runs/rf32_round1_group_head_on_orca_groups/group_report.md` |
| Groups of 3 or 4, non-verbal (RF-34) | 9 / 64 (0.14) | pairs 37 / 64, p < 0.0001 | `runs/rf34_round1_group_head_on_non_verbal_partner/group_report.md` |
| Encounters inside a crowd, independent (RF-35) | 14 / 64 (0.22), against plain ORCA on the same seed | plans worse than ORCA in 50, better in 6 (p < 0.001) | `runs/rf35_crowd_encounters/crowd_report.md` |
| Encounters inside a crowd, non-verbal (RF-36) | 9 / 60 (0.15) | RF-35's 13 on the same 60 (p = 0.22) | `runs/rf36_crowd_encounters_non_verbal/crowd_report.md` |

In groups, every collision is with an oncoming person, never between friends. Inside a crowd, "worse" is
mostly millimetres of extra overlap, but the plans added collisions in 30 of 64 sessions and removed them in
2 (RF-35). **The LLM's plans are not better than ORCA anywhere outside the two-person meeting.**

### 2.5 What the agents say they based it on

No agent named a source in 2,681 debriefs (`literature/rule-verification/README.md`, summary table). In
round 1's 288 sessions the debriefs' kind of basis was common sense 293, habit 210, local custom 60 and
"none" 8 of 576 (`runs/rf15_round1_keep_line_analysis/report.md`, section 6).

## 3. Steps 2 and 3: the rules, and how they compare with people

### 3.1 Extraction (RF-11)

From the 102 resolved sessions (76 shown, 26 held out), an extractor wrote 25 rules over three runs, and 4
were kept (found in at least 2 runs). **None read ethnicity or perceived attractiveness**
(`runs/rf11_round1_head_on/extraction_report.md`).

| Kept rule (shortened) | Found in | Held out | Baseline |
| --- | --- | --- | --- |
| A person who **holds their ground** keeps their line at full speed at first, and steps aside or slows only at close range (`aacce0961b`) | 2/3 | **43/52 (0.83)** | 0.75 |
| A person who **gives way** slows when the other is elderly, has a cane, pulls a suitcase or looks at a phone (`6455ca5589`) | 3/3 | 37/52 (0.71) | 0.75 |
| People almost never stop or back up (`0ecc2d1a6e`) | 2/3 | 52/52 (1.00) | 1.00 |
| People signal in the non-verbal and talk conditions (`4eb7a97c8d`, needs communication) | 2/3 | 40/52 (0.77) | 0.35 |

**Only one beats its baseline**: assertiveness decides whether a person slows. "Keep right" is in every
run's words but in no run's numbers: no "keep right" rule predicts the first plan's side better than always
guessing right.

### 3.2 Translation into rule formats, and the identity check

The identity check runs a translated rule on the 76 resolved sessions it came from and counts how many
outcomes (who first, and the sides) it reproduces. Plain ORCA's own share is the floor.

| | Format 3 (RF-12) | Format 4 (RF-31, with the retry) |
| --- | --- | --- |
| Translations valid / not expressible / unreadable | 3 / 1 / 0 | 2 / 1 / 1, then the retry valid |
| What the valid ones do | two are plain ORCA; one makes both people slow in every head-on | both turn 10° left from 9.8 m (`0ecc2d1a6e`); whoever faces a cane slows (`6455ca5589`, retry); one never matches (`aacce0961b`, now refused) |
| Identity check (plain ORCA: 0.36) | 0.36 for every rule | left turn 0.20; cane rule 0.34 |
| Crowd screening | the slow-down gridlocks | left turn passes; cane rule gridlocks on one seed |

Sources: `runs/rf12_round1_head_on/translation_report.md`, `runs/rf31_round1_head_on/translation_report.md`.
**What was lost:** format 3 could not read a cane, a suitcase, a phone, the layout, or who gives way; it
refused what only the person knows. Format 4 reads 3 of 4 rules' factors, but its deeper nesting was harder
for the model to write as valid JSON. **No rule reproduces the agents better than plain ORCA.**

### 3.3 Against published studies (RF-14)

Published studies only (the user's decision, 2026-10-30). Source: `literature/rule-verification/README.md`.

- **References: none checks out.** 0 of 27 extractor references are sources (24 give none, 3 cite the
  participants); no agent named a source.
- **Every kept rule is "partly supported"**: the behaviour by role yes, but assertiveness as its cause is
  contradicted (Knorr et al. 2016); giving way to an older person yes (Rapos et al. 2021), to a cane, a
  suitcase or a phone, no evidence; a shared side yes, but **no published study says which side Singapore
  pedestrians keep**. The left-turn translation's side was the translator's pick, not from any source.

### 3.4 Against measurable human targets (RF-37, RF-38)

Targets from published studies, with tolerances fixed with the user before any rule was measured
(`docs/human-targets.md`). Every comparison but one is in a setting unlike the study's.

| Target | Study | Plain ORCA | Left-turn rule | Cane rule | Step 1's agents |
| --- | --- | --- | --- | --- | --- |
| H1 pass distance, two young adults (0.93 ± 0.17 m) | Rapos et al. 2021 | outside, 0.51 | outside, 1.25 | outside, 0.51 | **within, 0.93 to 0.97** |
| H2 pass distance with an older adult | Rapos et al. 2021 | outside, 0.51 | outside, 1.25 | outside, 0.50 to 0.51 | within except non-verbal (0.98) |
| H8 with an older adult, the young adapts more | Rapos et al. 2021 | not shown | not comparable | not shown | **agrees** in all three conditions |
| C1 lanes form in two-way flow | Moussaïd et al. 2009 | opposite, 3 of 50 runs | not shown, 32 of 50 | opposite, 4 of 50 | not comparable |

Sources: `runs/rf37_human_targets/report.md` (H1, H8, C1; H1 for the rule arms rests on one pair of two young
adults), `runs/rf38_human_targets/findings.md` (H2 for the cane rule, in pairs with one cane user).
**Step 1's agents pass at a human distance; every rule passes at ORCA's 0.50 m, two bodies touching, or the
left-turn rule's 1.25 m.** (Both rules on together come out "within" on H2, 0.92 m, but only as the average
of pairs at 0.50 and 1.25 m: `runs/rf37_human_targets/report.md`, H2 and the pass distance table.) A rule that only decides who gives way cannot fix the distance, which comes from
ORCA underneath. In RF-38's cane pairs the cane rule made the other person give way in 30 of 30, as Step 1's
agents also do (14 to 3, 21 to 2, 12 to 4 by condition).

**Promotion: no round 1 rule is promoted** under the table the user adopted on 2026-10-31 (`docs/human-targets.md`,
section 6): the left-turn rule is outside on H1 and H2; the cane rule harms (RF-33) and is outside on H2.

## 4. Step 4: the factors and the mapping

All from `runs/rf15_round1_keep_line_analysis/report.md` unless named. Effects are odds ratios (OR) with 95%
intervals; Holm's correction runs over every term in the report.

### 4.1 Effects that survive Holm's correction

| Outcome | Factor | Effect [95% CI] | Holm p | n |
| --- | --- | --- | --- | --- |
| Slowed in the first plan | Own assertiveness (holds ground) | OR 0.10 [0.05, 0.21] | < 0.001 | 571 |
| Signalled | Knows the other | OR 445 [47, 4,165] | < 0.001 | 384 |
| Signalled | Own assertiveness | OR 13.6 [4.5, 41.1] | 0.003 | 384 |
| Signalled | Finds the other attractive | OR 6.5 [2.7, 15.9] | 0.024 | 384 |
| Start distance of the first plan | Own cane | +2.25 m [+1.19, +3.31] | 0.022 | **13** |
| Decision points a session | Condition non-verbal / talk | +3.37 / +3.46 | < 0.001 | 288 |

(Rows for single conditions are in the report.) **No factor survives on whether the meeting resolves, or on
who passes first.** The strongest uncorrected effect on resolution is person 1 carrying a load (OR 0.60,
p = 0.057). Signalling is counted in the non-verbal and talk conditions only. The cane effect rests on 13
rows and should not be reported without that caveat.

**Under `as_prompted` (RF-10)** the same effects survived, except assertiveness on signalling and the cane
on start distance, which are new (`runs/rf10_round1_head_on/analysis/report.md`, section 1).

### 4.2 The decision tree

A tree of depth 3 predicting who passes first scores 0.837 on held-out sessions, against 0.843 for always
guessing the commoner outcome: **no usable pattern** (section 2; figure `tree.png`). RF-10's tree under
`as_prompted` was the same (0.733 against 0.754).

### 4.3 Against the model's own randomness

- **Noise floor:** identical prompts flip the behaviour (who first, sides, stopping, backing up) in 0.83 of
  repeat pairs (95% CI 0.74 to 0.92); who passes first alone, 0.69 (section 3).
- **Counterfactual pairs** (one factor flipped, everything else the same): **all 80 comparisons are within
  the noise floor** (`flip_rates.csv`).
- **Stability:** 23 of the 24 exact-repeat cells are coin flips (section 4).
- **Interactions** (for example gender by attractiveness) were not tested: RF-13 moved to round 2 (#55).

### 4.4 Stated against measured

How often a factor is named in the agents' private reasons, against whether it has a measured effect
(section 6):

| Factor | Named in reasons | Measured effect | Verdict |
| --- | --- | --- | --- |
| Load | 0.29 | none | named often, no effect |
| Mobility aid (cane) | 0.25 | start distance (13 rows) | named often, an effect |
| Assertiveness | 0.24 | slowing, signalling | named often, an effect |
| Distraction (phone) | 0.23 | none | named often, no effect |
| Age | 0.19 | none | named often, no effect |
| Memory note | 0.13 | none | named often, no effect |
| Urgency | 0.12 | none | named often, no effect |
| Familiarity | 0.06 | signalling | an effect, rarely named |
| Perceived attractiveness | 0.03 | signalling | an effect, rarely named |

**What the agents say drives them (age, load, a phone, urgency) mostly does not show in what they do; what
does show (knowing or finding the other attractive) they rarely say.** The intents also disagree with the
plans at a measurable rate: 0.22 non-verbal, 0.24 talk (section 7), 0.34 independent
(`runs/rf10_round1_head_on/analysis/report.md`, section 7; those plans are unchanged under `keep_line`).

### 4.5 Effects flagged as possible LLM bias

- **Finding the other attractive → signals more** (OR 6.5): graded "partly supported" as attention, and
  recorded as **the model's bias, never a rule** (RF-14). Rules may read a person's own view of the other's
  attractiveness only from format 4, by the supervisor's decision (`CLAUDE.md`); none of round 1's does.
- **Real ethnicity:** no effect beyond the noise floor (counterfactual pairs, section 3), so not graded
  (RF-14). No rule may read it, in any format.
- **Keep right:** the model keeps right (66 of 102 resolved pairs), and some debriefs say "keep left, as
  people do here" while passing either way (33 left, 33 right, of 66; RF-11, section 5). RF-14 grades it
  "no evidence for Singapore; a finding about the model".

### 4.6 The mapping

The full mapping (`mapping.csv`) has every combination of the 20 varied factors, geometry and condition seen
in the data: **402 combinations, 330 of them seen once**, too sparse to read as a lookup table.

The **compact mapping** (`mapping_compact.csv`, the appendix) uses only the four factors with an effect that
survives Holm (own assertiveness, knowing the other, finding the other attractive, own cane), chosen by that
rule before looking at it. It shows the effects of section 4.1 as shares with counts, for example in the
non-verbal condition: an agent who gives way, knows no one, sees no one attractive and has no cane slowed in
25 of 54 rows and signalled in 7 of 54; one who knows the other signalled in 23 of 24.

Which entries are backed by human evidence: RF-14's grades of the factor effects
(`literature/rule-verification/README.md`, summary table; sources by their keys there). RF-14 graded RF-10's
effects; the ones that survive under `keep_line` are the first three.

| Effect | RF-14's grade |
| --- | --- |
| Holds ground → slows less (in the compact mapping) | **contradicted** as a cause (Knorr2016) |
| Knows the other → signals (in the compact mapping) | partly supported (Arminen2023, after Goffman) |
| Finds the other attractive → signals (in the compact mapping) | partly supported as attention (Valuch2015); the model's bias, never a rule |
| The other is 70 → slows | supported in direction (Rapos2021) |
| The other has a cane → signals | partly supported: people look, not signal (Arminen2023) |
| Own cane → starts earlier (in the compact mapping; new under `keep_line`) | not graded |

## 5. The full simulation (RF-18, RF-33)

All rules on together, ORCA for pairs no rule matches, against plain ORCA, on paired seeds. "Helps" and
"harms" were fixed with the user before any run (`docs/rule-set-evaluation.md`). A rule's verdict of record
comes from its realistic scenarios (RF-33).

| Rule | Stress crowd (RF-18, 10 seeds) | Realistic crowd (RF-33, 30 seeds, of record) |
| --- | --- | --- |
| Left turn (`0ecc2d1a6e`) | **helps**: severe conflicts 569 against 804, fewer on 10 of 10 | **helps**: severe conflicts fewer on 30 of 30; collided pairs fewer on 21 of 30 (p = 0.043) |
| Cane rule (`6455ca5589`) | **harms**: gridlock on 2 of 10 seeds | **harms**: gridlock on 1 of 30 seeds |
| Both | harms (more collisions on 10 of 10) | helps |

Sources: `runs/rf18_round1/evaluation_report.md`, `runs/rf18_round1_realistic/evaluation_report.md`. In the
opposing bottleneck no rule changes anything; in the narrow passage no rule matches and plain ORCA deadlocks
on every seed (round 2's scenario).

- **Lanes:** the left-turn rule makes 61% of the crowd keep left, against 49% under plain ORCA (RF-18). By
  RF-37's lane target, plain ORCA forms lanes in 3 of 50 runs, the left-turn rule 32, the hand-written keep-left
  defaults 40 (`runs/rf37_human_targets/report.md`, C1).
- **Runtime per step:** at 1,000 agents plain ORCA takes 687 ms a step, and the rules add half again (×1.51
  and ×1.57). ORCA itself grows about tenfold from 100 to 1,000 agents, so **the 10,000-agent goal is limited
  by ORCA and neighbour search before the rules** (RF-18, section 6).
- **Rule conflicts:** the two rules clashed at equal priority; the narrower one (the cane rule) was given
  priority 600 (the user's choice). With both on, 31,094 cross-pair conflicts arose, through which the cane
  rule's slowing spreads; under the left-turn rule, 45,373 matches did not start a plan, because a person runs
  one plan at a time, against 4,077 that did (RF-18, section 4).
- **Uncovered conflicts:** what no rule covers is mostly **overtaking** (15,368 pairs at T1 or above with both
  rules on), then single-file meetings (RF-18, section 5). These are rounds 3 and 2: the loop agrees with #55's
  order, and no new scenario is proposed.

## 6. Method and limits

**The mock against the real model.** Every feature was built and tested on a mock client first. The mock
checks the plumbing and the cost bound, but it could not show three things the real model did:
- **Replies in unforeseen forms:** 63 of 492 sends unreadable in RF-9's pilot (12.8%), 63 of 1,887 in RF-10
  after the template fixes (3.3%) (`runs/rf10_round1_head_on/screen_report.md`, section 1).
- **The model's randomness:** identical prompts flipped the behaviour in 0.77 of pairs in RF-9
  (`runs/rf_pilot_v2/pilot_report.md`), 0.83 in round 1.
- **An executor that did not do what the prompt said**: found with the first real plans (0 of 12 resolved),
  and again in RF-29 (sidesteps undone).

**Cost** (`llm_negotiation/spend_ledger.jsonl`; `pipeline/config.py`, `ALREADY_SPENT_USD`):
- Round 1 (RF-9 to RF-36): **USD 1.336** in 13 paid issues, each under its own cap; RF-36 stopped at its cap
  with 66 of 72 sessions. RF-14, RF-18, RF-33, RF-37 and RF-38 made no model call.
- Everything spent on the project: the ledger's USD 1.340 (with two earlier smoke tests) plus the Phase 1
  dataset's USD 0.10: **about USD 1.44**.
- The overall cap for paid runs (about USD 1.80) is still pending supervisor approval (`CLAUDE.md`, pending
  item 1). The DeepSeek balance was **USD 0.17** on 2026-10-29, enough for at most a lean round.

**Placeholders still in use** (no source; `docs/parameters.md`, sections 3, 8.2 and 8.7;
`docs/population-profiles.md`). The hearing range, eye-contact range and D5's change thresholds were
replaced by sourced values on 2026-10-23, before any run read them. Still placeholders:
- in the protocol: the largest turn in a reply (90°), speech rate (2.5 words a second), the end of an
  encounter after 1 s with no predicted conflict, the drift band (45°), the reply cap (400 tokens);
- in the factors: a suitcase's added width (0.2 m), hearing range when quiet or busy (8.9 m, 3.2 m);
- in the populations: a large suitcase (1%), a cane under 65 (0.5%), assertiveness (half of people);
- in the scenarios: the bottleneck's and the passage's width and length (0.8 m, 4.0 m), the flow's spawn
  spacing (1.0 m);
- the gate's threshold (0.50) is a judgement.

**`plan_orca` is an approximation.** It runs the agents' plans with ORCA underneath, which the agents did not
plan for. Step 1's measure is `plan_only`; `plan_orca` is a baseline only (`docs/resolution.md`).

**Foreign evidence.** Most of the studies behind RF-14 and RF-37 are from Europe or North America, in
laboratories or other countries' streets. A cane's prevalence by age is from the United States (NHATS 2011).
**No published study of which side Singapore pedestrians keep was found** (#69).

**Other limits.**
- One model (`deepseek-flash`), one scenario, one corridor width. RF-28's v4-pro did no better.
- Every round 1 rule covers head-on meetings only.
- In the avoidance simulator a factor changes only what a rule reads: a cane user walks at the same speed
  with the same body (`runs/rf38_human_targets/findings.md`).
- The factor analysis is on agents' replies to a description; what the agents were told is what counts as a
  factor (RF-8).

## Appendix: the compact mapping

From `runs/rf15_round1_keep_line_analysis/mapping_compact.csv`. Each row is one combination of the four
factors with a Holm-significant effect, from one agent's point of view, per condition; the other factors vary
within a row. A cell is "rows with the outcome / rows where it is known". "Passed first" leaves out pairs
that passed together; "signalled" does not apply to the independent condition (–).

| Condition | Holds ground | Knows the other | Finds attractive | Own cane | Rows | Slowed in first plan | Signalled | Passed first | Passed on own left |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| independent | no | no | no | no | 54 | 27/53 | – | 2/30 | 21/54 |
| independent | no | no | no | yes | 6 | 4/6 | – | 2/5 | 5/6 |
| independent | no | no | yes | no | 28 | 23/27 | – | 1/14 | 15/28 |
| independent | no | no | yes | yes | 4 | 4/4 | – | 0/1 | 2/4 |
| independent | no | yes | no | no | 24 | 20/23 | – | 1/14 | 5/24 |
| independent | no | yes | no | yes | 4 | 4/4 | – | 0/4 | 1/4 |
| independent | no | yes | yes | no | 26 | 22/26 | – | 2/19 | 7/26 |
| independent | no | yes | yes | yes | 6 | 6/6 | – | 1/2 | 3/6 |
| independent | yes | no | no | no | 6 | 2/6 | – | 2/4 | 3/6 |
| independent | yes | no | no | yes | 6 | 2/6 | – | 1/5 | 1/6 |
| independent | yes | no | yes | no | 4 | 1/4 | – | 1/2 | 2/4 |
| independent | yes | no | yes | yes | 4 | 1/4 | – | 1/1 | 1/4 |
| independent | yes | yes | no | no | 4 | 1/3 | – | 0/2 | 1/4 |
| independent | yes | yes | no | yes | 6 | 5/6 | – | 0/2 | 2/6 |
| independent | yes | yes | yes | no | 6 | 4/6 | – | 1/4 | 0/6 |
| independent | yes | yes | yes | yes | 4 | 1/3 | – | 1/1 | 1/4 |
| non-verbal | no | no | no | no | 54 | 25/54 | 7/54 | 5/36 | 33/54 |
| non-verbal | no | no | no | yes | 6 | 5/6 | 1/6 | 0/3 | 4/6 |
| non-verbal | no | no | yes | no | 28 | 23/28 | 10/28 | 2/20 | 13/28 |
| non-verbal | no | no | yes | yes | 4 | 2/4 | 3/4 | 1/3 | 3/4 |
| non-verbal | no | yes | no | no | 24 | 22/24 | 23/24 | 1/16 | 6/24 |
| non-verbal | no | yes | no | yes | 4 | 2/4 | 4/4 | 1/2 | 1/4 |
| non-verbal | no | yes | yes | no | 26 | 24/26 | 25/26 | 1/11 | 12/26 |
| non-verbal | no | yes | yes | yes | 6 | 4/6 | 6/6 | 0/5 | 1/6 |
| non-verbal | yes | no | no | no | 6 | 0/6 | 3/6 | 3/4 | 1/6 |
| non-verbal | yes | no | no | yes | 6 | 2/6 | 1/6 | 3/5 | 3/6 |
| non-verbal | yes | no | yes | no | 4 | 1/4 | 3/4 | 2/3 | 3/4 |
| non-verbal | yes | no | yes | yes | 4 | 1/4 | 4/4 | 2/4 | 2/4 |
| non-verbal | yes | yes | no | no | 4 | 0/4 | 4/4 | 0/2 | 3/4 |
| non-verbal | yes | yes | no | yes | 6 | 5/6 | 6/6 | 2/4 | 3/6 |
| non-verbal | yes | yes | yes | no | 6 | 4/6 | 6/6 | 0/4 | 1/6 |
| non-verbal | yes | yes | yes | yes | 4 | 2/4 | 4/4 | 0/2 | 1/4 |
| talk | no | no | no | no | 54 | 28/54 | 12/54 | 2/36 | 31/54 |
| talk | no | no | no | yes | 6 | 4/6 | 4/6 | 0/3 | 5/6 |
| talk | no | no | yes | no | 28 | 25/28 | 16/28 | 1/18 | 14/28 |
| talk | no | no | yes | yes | 4 | 4/4 | 3/4 | 1/3 | 2/4 |
| talk | no | yes | no | no | 24 | 21/24 | 24/24 | 1/13 | 9/24 |
| talk | no | yes | no | yes | 4 | 4/4 | 4/4 | – | 1/4 |
| talk | no | yes | yes | no | 26 | 26/26 | 26/26 | 3/14 | 13/26 |
| talk | no | yes | yes | yes | 6 | 6/6 | 6/6 | 1/3 | 2/6 |
| talk | yes | no | no | no | 6 | 2/6 | 5/6 | 3/5 | 2/6 |
| talk | yes | no | no | yes | 6 | 4/6 | 5/6 | 0/4 | 3/6 |
| talk | yes | no | yes | no | 4 | 1/4 | 4/4 | 0/3 | 4/4 |
| talk | yes | no | yes | yes | 4 | 1/4 | 4/4 | 2/2 | 3/4 |
| talk | yes | yes | no | no | 4 | 0/4 | 4/4 | 1/2 | 2/4 |
| talk | yes | yes | no | yes | 6 | 1/6 | 6/6 | 1/4 | 3/6 |
| talk | yes | yes | yes | no | 6 | 3/6 | 6/6 | 0/3 | 2/6 |
| talk | yes | yes | yes | yes | 4 | 2/4 | 4/4 | 0/3 | 2/4 |
