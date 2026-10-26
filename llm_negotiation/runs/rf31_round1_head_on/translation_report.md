# RF-31, round 1 (head-on): what rule format 4 kept of the extracted rules

Issue #108. Paid run of 2026-10-26, calls from 13:16 to 13:20 UTC (off-peak), approved for this issue only
with a cap of USD 0.05 (`CLAUDE.md`). Five calls to `deepseek-flash` at temperature 0 (one rule
first, read, then the other three; one reply asked again): **USD 0.0025** (worst case USD 0.043).
Template `translate_v2`, the format as `rulegen_common_v3` describes version 4; method in
`docs/rule-translation.md`, section 13. The same four rules, model, temperature and settings as
RF-12 (`runs/rf12_round1_head_on/translation_report.md`), only the format and template changed. The
machine-written table is `report.md`; the numbers here are from `summary.json`, `translations/`,
`identity/` and the staged rules (`rule_db_staging/extracted/`).

## Findings

**1. Two valid translations, one not expressible, one unreadable.**

| Extracted rule (shortened) | RF-12, format 3 | RF-31, format 4 |
| --- | --- | --- |
| `0ecc2d1a6e`: in the 20 cm layout the pair keep the side their final plan takes, and almost never stop or back up | valid: plain ORCA (speed scale 1, no side) | **valid**: when the corridor is at least 0.2 m wide, both people turn 10° to their left from 9.8 m until the other passes |
| `4eb7a97c8d`: people signal and speak when the other drifts to their side or the plan fails | not expressible | **not expressible** ("entirely about signalling and speaking") |
| `6455ca5589`: a person who gives way slows on the first plan when the other is elderly, has a cane, pulls a suitcase or looks at a phone | valid: both slow to 0.73 in every head-on | **unreadable**, twice (below) |
| `aacce0961b`: a person who holds their ground keeps their line at full speed and steps aside or slows only at close range | valid: plain ORCA | **valid but never matches**: roles "by" `agent.speed_mps >= 0`, which holds for both, so the rule never applies |

- **`0ecc2d1a6e`** used steps, as the template asks. It listed what it approximated: the layout (as a
  corridor-width test, which holds in every round 1 case), the side each pair's final plan took
  (as a fixed 10° left turn for both), the range of turns and speeds.
- **`6455ca5589`** was the translation that used all of format 4: roles by the other's cane, an own-only
  condition on the giver's own assertiveness, and a plan (slow to 0.95 m/s from 9.8 m until the other
  passes, speed scale 0.7). Both replies were malformed JSON in the same place: the giver's own-only
  condition was never closed, so `"other": {}` fell inside the giver's entry and the object ended one
  `}` short. The reader cannot repair a missing brace, so the record is `unreadable` and nothing was
  written. **Format 4's nesting (a plan inside an own-only condition inside a directive) is harder for
  the model to write as valid JSON** than format 3's flat directives.
- **`aacce0961b`**: the extracted rule is about a person who holds their ground, which only that person
  knows. Format 4 can read it only in an own-only condition, which cannot give roles. The translator
  wrote a condition that holds for everyone, so roles by it never differ and the rule never matches
  (0 of 76 sessions). A valid but empty rule; the loader cannot tell it from a meaningful one.

**2. What was lost.** Mechanically, format 4 reads 3 of 4 rules' factors (format 3: 2) and none is
`unobservable` any more (format 3: 2); the layout, a decision count and signals still have no field
(3 rules). Of the action's words, only the signalling rule's are beyond format 4 (format 3: starts in
4 rules, speeds in 3, turns in 2). The translator's own list shrank less: conditions in 3 rules, speeds,
starts and turns approximated in 2 each.

**3. The identity check: format 4 changes what ORCA does, and resolves every head-on.**
Each valid rule alone, on the 76 resolved Step 1 sessions it was extracted from:

| | Same agent first | Same passing sides | Reproduced | Resolved (Step 1's sense) |
| --- | --- | --- | --- | --- |
| `ext_head_on_0ecc2d1a6e`, format 4 (turn left 10°) | 0.51 | 0.38 | **0.20** | **1.00** |
| `ext_head_on_aacce0961b`, format 4 (never matches) | 0.67 | 0.55 | 0.36 | 0.00 |
| Each of RF-12's three format 3 translations | 0.67 | 0.55 | 0.36 | 0.00 |
| Plain ORCA, same seeds | 0.67 | 0.55 | 0.36 | 0.00 |

- In every round 1 session, plain ORCA comes within the near-miss distance; under the left-turn rule
  **all 76 pass with no collision and no near miss.** It is the first translated rule that changes
  the outcome at all.
- It reproduces the agents' own outcome **less** than plain ORCA does (0.20 against 0.36), because it
  fixes the side: every pair passes left to left, while the agents themselves passed right to right in
  47 of the 76 sessions and left to left in 29. The extracted rule said "keep the side the final plan
  takes", which differs pair by pair; the translation chose one side for everyone. Keep right was the
  agents' majority (RF-11); the translator wrote left.
- The identity share measures "does ORCA under the rule do what the agents did", not "does it resolve
  the meeting". The two point in opposite directions here.

**4. Crowd screening: both valid rules pass.** In the two-way flow (50 + 50, two seeds; people given
canes, suitcases, phones and assertiveness in turn), against the baseline on the same seeds:

| | Collision episodes | Throughput (agents per minute) | Verdict |
| --- | --- | --- | --- |
| `ext_head_on_0ecc2d1a6e` (turn left 10°) | 82, 88 (baseline 86, 68) | 78.1, 87.1 (baseline 115.4, 75.7) | passed |
| `ext_head_on_aacce0961b` (never matches) | 86, 68: the baseline's | the baseline's | passed |

The left turn neither gridlocks nor adds collisions on the whole; throughput fell on one seed and rose
on the other. RF-12's slow-down rule, which gridlocked the crowd, did not come back in format 4 (its
translation is the unreadable one).

## What this means for the track

- Format 4 can say what format 3 could not (a plan in time, who gives way by what one sees, what only
  one person knows), and the translator used it. One rule now changes ORCA's outcome, and safely.
- But the gain is fragile: one of four translations was lost to malformed JSON in the deeper nesting,
  one is empty (a condition that always holds), and the one that works reproduces the agents less than
  plain ORCA because it turned "keep your own side" into "everyone keeps left". These are findings
  about the translation step as much as the format.
- For RF-18 (#74): round 1 has one runnable rule that does something, `ext_head_on_0ecc2d1a6e`.

## Limitations

- One translation per rule at temperature 0, as RF-12. Another sample might close the brace, or write
  roles that differ.
- The identity check compares who passed first and the sides; resolution is reported beside it.
- A rule reads a cane, suitcase or phone at any distance; Step 1's agents saw them only within 5 m.
- Crowd screening ran two seeds of one flow. Nobody in the crowd has a view of another person, and a
  suitcase does not widen anyone there.

## Files

`translations/<x_rule_id>.json` (prompts and every raw reply), `rule_db_staging/extracted/` (the two
written rules, v1 as translated and v2 with their screening), `identity/<ext_rule_id>.csv` (76 rows
each), `screening/` (each crowd run's `config.json`, `outcome.json` and `events.jsonl`; the bulky logs
are not committed and are rebuilt by running the experiment again), `summary.json`, `report.md`.
