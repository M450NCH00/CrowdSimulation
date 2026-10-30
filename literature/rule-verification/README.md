# RF-14, round 1 (head-on): the rules, references and factor effects against human evidence

Issue #69, Step 3 of track #55. No model call, USD 0. **"Real human behaviour" means published
studies only** (the user's decision, 2026-10-30; `CLAUDE.md`, pending sign-offs item 6), so no plan for
observed data is made here (the issue's task 8).

| File | What it holds |
| --- | --- |
| `references-check.md` | Tasks 1 and 2: every extractor reference (27) and every debrief (2,681) checked |
| `evidence/<rule>.md` | Task 5: one evidence file per rule (4 kept rules), the keep-right pattern, and the factor effects |
| `sources.md` | Every source, how much of it was read, and its cached copy in `refs/rf14_*` |
| `search-log.md` | The searches, and what could not be reached |

**Grades** (#69, task 4): **Supported** (published evidence shows people do this), **Partly supported**
(part of the rule, or its direction, is shown; the rest is not), **No evidence** (nothing found either
way), **Contradicted** (published evidence shows people do otherwise). #37's scale was not used: it has
no supervisor approval.

## Summary table (task 7)

Extractor references that check out: **0 of 27** as sources (24 give none; 3 cite the participants,
of which 2 report the debriefs correctly). Debrief sources that check out: **0 of 0**: no agent named
a source in 2,681 debriefs; 3% said `none`.

| Rule or effect | Grade | RF-18 verdict (of record: RF-33, realistic crowd) | Key source | #55's table says |
| --- | --- | --- | --- | --- |
| `x_head_on_aacce0961b`: who holds their ground keeps their line; slows only late | **Partly supported**: the behaviour by role yes, assertiveness as its cause no | not run (translation never matches; now refused) | Olivier2013; against: Knorr2016 | a finding: the format cannot give roles by one's own disposition |
| `x_head_on_6455ca5589`: who gives way slows for an elderly, encumbered or distracted other | **Partly supported**: age yes; cane, suitcase, phone no evidence | **harms** (cane translation: gridlock 1 of 30 seeds) | Rapos2021 | a finding: the translation slows everyone facing a cane; people give way mostly by turning |
| `x_head_on_0ecc2d1a6e`, extracted: people almost never stop or back up | **Partly supported** (consistent, indirect) | not run on its own | Moussaid2009, Huber2014, Olivier2013 | stays staged |
| `x_head_on_0ecc2d1a6e`, format 4 translation: both turn 10° left | **Partly supported**: a shared side yes; *left in Singapore* rests on guidance only (no study) | **helps** | Moussaid2009, Echeverria2026; guidance MOT2024; against: Jung2013 | **promote** (not done here: see "Promotion") |
| `x_head_on_4eb7a97c8d`: people signal when they can (needs communication) | **Partly supported**: gaze read, yes; nods and waves between strangers, no | not expressible | Nummenmaa2009; against: Arminen2023 | a finding: no field for signals |
| Keep right (every run's words, not kept) | **No evidence** for Singapore; a finding about the model | – | Moussaid2009, CircleAntipode2019, Jung2013 | not staged |
| Own assertiveness → slows less (Holm) | **Contradicted** (`[needs full text]` for the traits) | – | Knorr2016 | factor, not a rule |
| Knowing the other → signals (Holm) | **Partly supported** | – | Arminen2023 (Goffman) | factor |
| Finding the other attractive → signals (Holm) | **Partly supported** as attention; **the model's bias, never a rule** | – | Valuch2015 | factor |
| The other is 70 → slows | **Supported** in direction | – | Rapos2021 | factor |
| Visiting from the United States → turns right | **Partly supported** by analogy | – | Moussaid2009, CircleAntipode2019 | factor |
| The other has a cane → signals | **Partly supported** (looks, not signals) | – | Arminen2023 | factor |
| Real ethnicity | **Not graded** (no effect beyond the noise floor) | – | – | factor; never read by a rule |

## What round 1 shows

1. **The LLM names no source, and its references cannot be checked.** Neither the extractor nor any
   agent cites a law, guidance or study; they say common sense and habit. The design's hope that the
   model would point to where a rule comes from (D8) did not hold for head-on.
2. **No rule is wrong about people, and none is fully right.** Every kept rule is partly supported:
   the behaviour usually matches the laboratory studies, but the reasons and the details do not (who
   goes on is decided by assertiveness for the agents, by speed and heading for people; giving way is
   slowing for the agents, more often turning for people).
3. **The model says Singapore's convention and does another country's.** Its debriefs follow
   Singapore's guidance (keep left); its passes follow the right-hand convention measured in France and
   China. No published study says which side Singapore pedestrians actually keep, so neither can be
   checked against Singapore behaviour.
4. **The one factor the screen was sure of for avoidance, assertiveness, is the one the evidence
   contradicts.** The factors the evidence supports (the other's age; one's country for the side) are
   the ones common sense would predict.
5. **Numbers that compare:** a 25-year-old slows for a 70-year-old in 0.90 of first plans against 0.52
   for another 25-year-old, the direction of Rapos2021; Step 1's passing distance (about 0.91 m between
   centres, assuming the 0.25 m default radius) is close to Rapos2021's 0.79 to 0.93 m, but unlike in that
   study the agents pass an older person no closer.

## Promotion (task 6)

By #55's table, a rule that is Supported or Partly supported **and** helps in RF-18 is promoted. Exactly
one qualifies: **`ext_head_on_0ecc2d1a6e`** (both turn 10° to their left), Partly supported, helps. **It
was not promoted in this issue**, for two reasons the user should decide:

1. **The grade is borderline under the user's decision.** What is supported by published studies is
   that a shared side helps; that the side is *left* in Singapore rests on official guidance and on
   Japan, not on a study of Singapore. Read strictly ("published studies only"), the side has no
   evidence, and the grade would be No evidence → "stays staged, labelled a stall-removing heuristic".
2. **The promotion command refuses the staging database.** `python -m negsim.rulegen promote
   runs/rf31_round1_head_on/rule_db_staging/extracted ext_head_on_0ecc2d1a6e` loads the whole staging
   database strictly, and RF-31's `ext_head_on_aacce0961b` is now refused there (`constant_roles`), so the
   command stops before copying anything (tried on a scratch copy of `rule_db/`, 2026-10-30). Promoting
   needs a small change (load only the rule being promoted, or skip refused rules), which is the only
   code #69 allows. It would also be the first rule in `rule_db/` that is not a `test_seed`.

## Limits

- Three of the key studies (Olivier2013, Knorr2016, Nummenmaa2009) and Rapos2021 were read as abstracts
  only (bot checks on HAL, mediaTUM and Turku); Jung2013 too. Claims from them go no further than the
  abstract.
- Almost all the evidence is from laboratory experiments in Europe, Canada and China; none from
  Singapore. Searches for Singapore observation found only guidance.
- Grades are one reader's judgment against a small set of sources found in one session; the search
  log lists what was looked for and not found.
- The Step 1 numbers here are from the 216 sessions of RF-10's re-execution and RF-30 outside the
  exact-repeat set (counterfactual pairs included), not RF-11's 192-session table; RF-11's own figures
  are quoted as RF-11's.
