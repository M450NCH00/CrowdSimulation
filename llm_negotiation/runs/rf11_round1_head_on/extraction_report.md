# RF-11, round 1 (head-on): the rules behind how the LLM agents resolved it

Issue #66. Step 2 of track #55: from the head-on sessions the LLM agents resolved, an extractor
(`deepseek-flash`, template `extract_v1`) wrote the rules behind how they did it, three times.
The code checked each rule, scored it on held-out sessions, and matched the rules across the
runs (`docs/rule-extraction.md`). The generated summary is `report.md`; the rules are in
`head_on/extracted_rules/`; every prompt and raw reply is in `head_on/runs/`.

**Paid:** approved by the user for issue #66 only, 2026-10-26, cap USD 0.05. **Spent USD
0.022513** (6 calls, off-peak, 04:02 to 04:04 UTC, no transport error; ledger lines with
`experiment: rf11_round1_head_on`). Balance USD 0.65 before, **USD 0.64** after (DeepSeek's balance
endpoint shows two decimals).

## 1. What was extracted from

- **Sessions:** RF-30's pooled design sessions of head-on (192): the independent condition is
  RF-10's re-executed under `keep_line`, non-verbal and talk are RF-30's. Gate recomputed: 102 of
  192 resolved in `plan_only` (0.53, 95% CI 0.46 to 0.60), threshold 0.50: passes, narrowly. The
  user decided on 2026-10-26 that head-on goes on to extraction.
- **Split (seed 66):** 26 of the 102 resolved sessions held out (52 agent rows), never shown; 76
  in the main table (152 rows); the 90 failed sessions shown separately, counted.
- **Each run** showed the same tables and 15 resolved sessions in full, a different sample per
  run (seeds 1101, 1102, 1103). Prompts were 31.1k to 32.7k tokens; replies 3.3k to 4.0k (the cap).
- **Coin flips:** 23 of the 24 cells of the exact-repeat set gave different behaviour on
  identical prompts (18 of the main table's rows are in such a cell). The model's own randomness
  is large; any rule is a tendency, not a certainty.

## 2. What the extractor wrote

25 rules over the three runs (8, 8 and 9):

| Category | Rules | Meaning |
| --- | --- | --- |
| valid | 15 | stored |
| needs_communication | 6 | stored, tagged: they read `signalled` or `spoke`, or say so |
| schema_error | 4 | their `predict` read the agent's own first plan (`first_side`, `first_stopped`) or predicted `first_start_distance_m`, which the format does not allow |
| protected_attribute | **0** | no rule read ethnicity or perceived attractiveness |

**Every run's first reply was unreadable**: in runs 1 and 2, YAML prose with an unquoted colon;
in run 3 the reply reached the 4,000-token cap and was cut off (`finish_reason: length`). The one
retry was read each time (run 3's at 3,993 tokens, just under the cap). The retries' prompts came
mostly from the provider's cache, so they cost about USD 0.002 each.

## 3. The rules kept (found in at least 2 of 3 runs)

A rule is kept when its `predict` list decides like another run's on at least 95% of the main
table's rows. Held-out accuracy is on the 52 held-out rows, against always predicting the main
table's commonest value.

| Rule (as run 1 or 2 worded it) | Found in | Predicts | Held out | Baseline |
| --- | --- | --- | --- | --- |
| A person who **holds their ground** keeps their line at full speed at the first decision and only steps aside or slows at close range | 2/3 | `first_slowed` | **43/52 (0.83)** | 0.75 |
| A person who **gives way** slows when the other was described as elderly, using a cane, pulling a suitcase or looking at a phone | 3/3 | `first_slowed` | 37/52 (0.71) | 0.75 |
| People almost never stop or back up (worded with the layout) | 2/3 | `stopped` | 52/52 (1.00) | 1.00 |
| People signal (eye contact, nod, wave on) in the non-verbal and talk conditions (**needs communication**) | 2/3 | `signalled` | 40/52 (0.77) | 0.35 |

What this says:

- **One rule is a finding: assertiveness decides whether a person slows.** In the main table
  101 of 118 gives-way rows slow in their first plan and 21 of 33 holds-ground rows do not; on the
  held-out rows the rule gets 43 of 52 against 39 for "always slows". It reads the person's own
  disposition, not anything about the other, so a simulator can apply it to an agent that has
  that parameter. Assertiveness is on RF-10's Phase B shortlist. It is a rule about **how much**
  a person gives way, not about **who goes first**, and it says nothing about the side.
- **The rule found in all three runs does not beat its baseline.** "Gives way to a constrained
  other" (0.71) is worse than "always slows" (0.75): nearly everyone slows, whatever the other
  carries.
- **The other two kept rules are close to trivial.** Nobody in a resolved session stopped or
  backed up, so "never stops" is the baseline. "Signals in non-verbal and talk" mostly restates the
  condition (`signalled` is n/a in the independent condition); it beats the baseline only because
  the baseline ignores the condition.

## 4. Keep right: in every run's words, in no run's numbers

- **Each run wrote a "keep to your own right" rule** (run 1: "a gives-way person turns to their
  own right"; run 2: "people default to steering to their own right"; run 3: "people default to
  turning to their own right ... right shoulder to right shoulder"). None was kept: their
  `predict` lists differ (run 1 predicts "both" in the aligned layout), so no two agree on 95% of
  the rows, and each is `unstable` (1/3).
- **None predicts the first plan's side better than "always right"** (0.35, 0.44 and 0.38 against
  0.46): the first plan turns right in only 66 of 152 main-table rows, and "both" (one way, then
  the other) in 45.
- **The pattern is in how the pairs pass, not in the first plan.** All 76 resolved pairs passed
  on the same side of their own (as they must, to pass): 47 on their right, 29 on their left (62%;
  held out 19 and 7). A rule on the pair's passing side was written once (run 2: "the pair settles
  on passing to their own right") and equals the baseline (0.73).

So the convention that would cure the remaining failures (RF-30: mostly pairs that did not settle
on a side) shows in the data as a majority, not as a rule the agents follow from the start.

## 5. References and debriefs

- **No rule names a law, official guidance or published study.** Of the 27 references of the 25
  rules, 24 are "no known source"; three cite what the participants reported ("Singapore
  pedestrian keep-left convention as reported by participants", "everyday courtesy to elders",
  "everyday courtesy and keep-side custom"), which are the debriefs, not sources.
  Every reference is stored `unchecked` (RF-14).
- **What agents say is not what they do.** 66 of the 384 agent debriefs of these sessions say
  they kept left ("keeping left as people generally do on walkways", a Singapore custom); those
  agents passed on their left 33 times and on their right 33 times. 10 debriefs say they kept
  right. The debrief kinds are mostly common sense and habit (`measured.debrief_kinds_where_it_holds`
  in each rule file). This stated-against-measured gap is for RF-14.

## 6. Caveats

- **Head-on passed the gate narrowly** (lower bound 0.46): whether the LLM "can resolve" head-on
  is borderline, and everything above describes the half of the meetings that resolved.
- **The held-out set is small:** 26 sessions, 52 rows, so one row is 2 points of accuracy; the
  holds-ground rule's margin is 4 rows.
- **Fidelity is about the LLM agents**, not people. Whether holds-ground people slow less, or
  whether people keep right, is RF-14's question.
- **The 95% matching threshold is a placeholder.** It split the three keep-right rules, which say
  the same thing in words but decide differently in the aligned layout.
- **Rows in coin-flip cells** (18 of 152) are in the table like any other; the extractor was told
  which they are.

## 7. For the user to decide

1. **`extract_v2` for later rounds** (a template change, so a new version): ask for every text
   value in quotes, since two first replies failed on an unquoted colon; ask for fewer, shorter
   rules or raise the reply cap (4,000 tokens cut run 3's first reply off; a config change, no new
   template); and say plainly that `predict` may not read the agent's own plan (4 rules did).
2. **Whether to add a pair-level target** (the pair's passing side, or "settled on one side"), so
   that a convention like keep right can be scored as what it is: a property of the pair.
3. **Whether 95% stays the matching threshold** (`[placeholder]`), or rules are also matched on
   their target and wording.
4. **For the supervisor:** the narrow gate, and that the one solid rule is about assertiveness and
   slowing, not about the side.
