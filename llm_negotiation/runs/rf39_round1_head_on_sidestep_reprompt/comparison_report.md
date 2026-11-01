# RF-39: round 1 (head-on), the sidestep with a second chance

Issue #127, track #55. Paid run of 2026-11-01 (Sunday, off-peak), approved by the user for this issue
only with a cap of USD 1.60 (`CLAUDE.md`, pending item 1). Every number below comes from a file named
with it; the process is in `WORK_LOG-127.md`. Tables: `analysis/sidestep_reprompt.md` (this issue's
module, `python -m analysis.sidestep_reprompt`), `analysis/gate.md`, `analysis/lateral.md`,
`analysis/compare_*.md` and the factor report `analysis/report.md` (`python -m analysis`).

## In short

- **A second chance ends about a third of pavement dances.** Of the sessions whose *first* plans went
  towards the same wall (one agent to its left, the other to its right), **47 of 120 resolved in
  non-verbal (0.39) and 41 of 124 in talk (0.33)**, against 0 of 90 in independent, where there is no
  second decision (Fisher's exact p < 0.0001 for each). Over all repeats, non-verbal and talk resolve
  **0.59** against independent's **0.36** (OR 2.6 and 2.8, Holm p < 0.001). Talking adds nothing over
  signalling (dances rescued: p = 0.35).
- **How a dance ends: one agent changes side, the other holds.** In 37 of the 47 rescued dances in
  non-verbal and 37 of 41 in talk exactly one agent moved to its other side at a later decision. In the
  dances that did not end, nobody changed side in 54 of 73 and 64 of 83: each agent kept its own side,
  up to 6 decisions, until they collided against the same wall.
- **Words do not carry the side in a way that helps.** Nobody points in non-verbal. In talk, a message
  names a side in 41 of the 83 dances that did not end and 9 of the 41 that did: the speaker names its
  *own* side ("I'll keep to my left"), and the other, heading for the same wall, does not switch. The
  unresolved sessions are also twice as long (median 10 decision points against 5), so more chances to
  speak; the difference is not evidence that naming a side hurts.
- **The side is a weak preference, not a pure coin flip, and it follows the person.** An agent's first
  side across its cell's 4 identical repeats was the same all 4 times in 0.30 (non-verbal) and 0.29
  (talk) of agents, against 0.13 and 0.15 for a coin (p < 0.0001, p = 0.0001); independent is within a
  coin (0.21 against 0.18, p = 0.15). A visitor from the United States goes right (0.68 to 0.79 of first
  sides); assertive and urgent people go right, older people left (Holm-significant). Locals barely lean
  (right 0.36 to 0.60, depending on the condition). Between identical repeats the side the pair passed
  on still flips 0.45 of the time (the noise floor), and 158 of 192 cells are coin flips by #63's rule.
- **What agents say about the side does not match what they do.** "More room" is the commonest reason
  (604 of the design sessions' 1,536 agents), but in the layout where one side has 21 cm more room, agents took that side
  in 366 of 703 first plans (0.52), and those who *said* more room in 201 of 382 (0.53): "more room" is
  read both as "take the wider side" and as "keep to the narrow side and leave the other the wider".
  Visitors keep right but name a custom in 4 of 377 debriefs (0.01).
- **The gate, on its fixed definition, fails narrowly**: 92 of 192 first runs resolved (0.48, CI 0.41
  to 0.55; threshold 0.50). The interval includes 0.50, as RF-30's pass (0.53) did. Over all 768
  repeats: 392 (0.51).
- **Against RF-30 and RF-29 (the same sessions, first runs, paired): no difference.** Non-verbal 37 →
  35 of 64 (p = 0.86), talk 30 → 37 (p = 0.25), independent 27 → 20 (p = 0.26). **The model's
  fingerprint changed between those runs and this one** (below), so these comparisons change the model
  as well as the template and the decision limit. The within-run comparisons above do not.

## 1. The run (`cost.json`, `../../spend_ledger.jsonl`)

| | |
| --- | --- |
| Sessions | 816 of 816: 272 per condition (32 cells x 2 geometries x 4 repeats = 256, and 16 in counterfactual pairs); repeat 1 has RF-30's (non-verbal, talk) and RF-29's (independent) session ids and people |
| Changes from RF-30 | `resolve_v8` (the sidestep in metres), all three conditions, every cell 4 times, `keep_line_replan` (the line is kept across a later decision), up to 6 decision points an agent (D5: 3), `resolve_debrief_v2` (why that side) |
| Cost | **USD 0.988492** (5,753 calls: 4,151 decisions, 1,602 debriefs; all off-peak, no error, no upper-bound cost) of the USD 1.60 cap. Pilot 24 sessions USD 0.0370, then 792. Mock estimate USD 1.08; pilot projection 1.07 |
| Balance | USD 5.17 before (after the user's top-up) → **USD 4.18** |
| Calls a session | independent 4.03, non-verbal 8.59, talk 8.54 (the mock: 4.11, 11.14, 11.43) |
| Decision points used | an agent reached 6 in 16 non-verbal and 35 talk sessions |
| Unreadable decisions (after the retry) | independent 29 of 544, non-verbal 57 of 1,705, talk 26 of 1,738 (RF-29: 2 of 192; RF-30: 11 of 515, 6 of 524). Commonest: a missing `until` (28), `until: {"event": "other_passes"}` (23), `start: "other_passes"` (19) |
| Debriefs | 1,602, none unreadable; `side_basis` missing in 2 |
| Model | `deepseek-flash`, version `DeepSeek-V4.1-Flash-1017` on the pricing page, fingerprint **`bc19ba97cbe016479903222bb1578db6`** in every call |

**The fingerprint.** RF-29 and RF-30 (2026-10-25) ran on `e72d3c7f663d3e1383b00b3884cb4501`; every run
from RF-32 (2026-10-28) on, this one included, on `bc19ba97…`. The model name and the listed version
did not change. Nothing recorded this until now. A fingerprint is the provider's configuration of the
model, so the paired comparisons with RF-29 and RF-30 (section 4) mix the change of model with the
change of method. The unreadable rate in independent (5.3% against RF-29's 1.0%) may be part of it.

## 2. Does a second chance end the pavement dance? (`analysis/sidestep_reprompt.md`, sections 1 to 4)

Resolved in `plan_only`, all repeats (768 design sessions, no counterfactual pair):

| Condition | All repeats | First runs only |
| --- | --- | --- |
| independent (one decision) | 91 / 256: 0.36 (0.30 to 0.42) | 20 / 64: 0.31 (0.21 to 0.43) |
| non-verbal (up to 6) | 150 / 256: 0.59 (0.52 to 0.64) | 35 / 64: 0.55 (0.43 to 0.66) |
| talk (up to 6) | 151 / 256: 0.59 (0.53 to 0.65) | 37 / 64: 0.58 (0.46 to 0.69) |

How the two *first* plans stepped (each agent's coded side in its own frame), and how many of each
resolved:

| Condition | Both to their own same side (make room) | Towards the same wall (a dance) | One or both not aside, or unreadable |
| --- | --- | --- | --- |
| independent | 79 / 95: 0.83 | **0 / 90: 0.00** | 12 / 71: 0.17 |
| non-verbal | 85 / 107: 0.79 | **47 / 120: 0.39 (0.31 to 0.48)** | 18 / 29: 0.62 |
| talk | 89 / 100: 0.89 | **41 / 124: 0.33 (0.25 to 0.42)** | 21 / 32: 0.66 |

- Independent's 0 of 90 is close to certain by construction: with one decision and no ORCA, a dance in
  the first plans cannot be undone. It is the reference for "no second chance", not a finding.
- Fisher's exact test, dances rescued: non-verbal against independent p = 3e-14, talk p = 8e-12;
  non-verbal against talk p = 0.35.
- Dances at the start were *commoner* in non-verbal and talk (0.47, 0.48 of sessions) than in
  independent (0.35). The first prompts differ only in the signal and talk lines, but the first side
  shifts with them (section 5); a second chance has more dances to undo.
- Most of the gain of non-verbal over independent (150 against 91, 59 sessions) is rescued dances (47).

How a dance at the start ended:

| Condition | Ended | Sessions | Changed side: none / one / both | A message names a side | Someone pointed | Decision points (median, both agents) | When level: own same side / same wall / not both aside |
| --- | --- | --- | --- | --- | --- | --- | --- |
| non-verbal | resolved | 47 | 9 / **37** / 1 | — | 0 | 6 | 36 / 3 / 8 |
| non-verbal | not resolved | 73 | **54** / 15 / 4 | — | 0 | 10 | 4 / 63 / 6 |
| talk | resolved | 41 | 3 / **37** / 1 | 9 | 1 | 5 | 36 / 1 / 4 |
| talk | not resolved | 83 | **64** / 17 / 2 | 41 | 4 | 10 | 2 / 74 / 7 |

- "Changed side": a later readable decision with a side other than the agent's first. "Both" changing
  (a second dance the other way) is rare: 4 and 2 unresolved sessions.
- "Names a side": the words `left` or `right` in a message (a keyword match, mine). Read examples
  (`WORK_LOG-127.md`): the speaker names its own side ("I'll keep to my left, plenty of room") and the
  other, moving to the same wall, does not switch; some messages send the other into the speaker's own
  path ("plenty of room on your right", from an agent on that side). Most messages are greetings.
- Fisher's exact test on messages naming a side, resolved against not: p = 0.004, but the unresolved
  sessions are twice as long; not read as an effect.
- Perception, unchanged from RF-30: an agent is told the other "moved over to your right/left" only
  within 5 m (the detail range, `docs/resolution.md`). A prompt triggered by a move farther away does
  not say it.

How the two stood when level along the corridor, first runs (`analysis/lateral.md`): of 82
collisions, 66 were towards the same wall; of 92 resolved, 88 had both on their own same side.

## 3. The gate (`analysis/gate.md`)

Fixed in the config before the run (RF-10's): 0.50 of the design's first runs resolved in `plan_only`.

| Group | Resolved | Rate (95% CI) |
| --- | --- | --- |
| **all (the gate)** | **92 / 192** | **0.48 (0.41 to 0.55): fails** |
| independent | 20 / 64 | 0.31 (0.21 to 0.43) |
| non-verbal | 35 / 64 | 0.55 (0.43 to 0.66) |
| talk | 37 / 64 | 0.58 (0.46 to 0.69) |
| walking lines aligned | 49 / 96 | 0.51 (0.41 to 0.61) |
| walking lines 20 cm apart | 43 / 96 | 0.45 (0.35 to 0.55) |
| `plan_orca` (baseline) | 101 / 192 | 0.53 (0.46 to 0.60) |
| plain ORCA | 0 / 192 | 0.00 (0.00 to 0.02) |

RF-30 passed at 0.53 (0.46 to 0.60) and this fails at 0.48 (0.41 to 0.55): the two intervals overlap
almost entirely, and both include 0.50. What moved is independent (RF-29: 27 of 64; here 20), and
paired that change is not significant (section 4). **Head-on sits at the gate's threshold; whether it
"passes" depends on the run.** Over all 4 repeats the rate is 392 of 768 (0.51); the gate's fixed
definition counts first runs only, so that is not the gate.

## 4. Against RF-30 and RF-29, the same sessions paired (`analysis/compare_*.md`)

| Condition | Earlier run | Earlier | RF-39 | Only earlier / only RF-39 | McNemar p |
| --- | --- | --- | --- | --- | --- |
| non-verbal | RF-30 (`resolve_v6`, 3 decisions) | 37 / 64 | 35 / 64 | 18 / 16 | 0.86 |
| talk | RF-30 | 30 / 64 | 37 / 64 | 10 / 17 | 0.25 |
| independent | RF-29 (`resolve_v8`, re-executed under `keep_line`) | 27 / 64 | 20 / 64 | 18 / 11 | 0.26 |
| independent, readable only | RF-29 | 24 / 57 | 20 / 57 | 15 / 11 | 0.56 |

With the sidestep and twice the decisions, non-verbal and talk are not measurably better than RF-30's
turning by degrees with 3 decisions. Three things changed at once (the template, the decision limit,
the model's fingerprint), and repeat 1 matches RF-30 only up to the third decision. `compare.py`'s
stability line in these files counts only the shared sessions (mostly one run a cell) and is not
comparable; section 5 has the stability over 4 repeats.

## 5. Is the side a preference or a coin flip? (`analysis/sidestep_reprompt.md`, section 5; `analysis/report.md`)

**From behaviour.** A unit is one agent of one cell in one condition: the same person and prompt 4
times. For the 274 units whose first plan moved aside in all 4 (110 left out: not aside or unreadable
in some repeat), the number of repeats it went right, against a coin weighted by the condition's share:

| Units | n | Right in 0 / 1 / 2 / 3 / 4 of 4 | Share right | All one way: observed (coin) | chi-square (df 1), p |
| --- | --- | --- | --- | --- | --- |
| independent | 72 | 2 / 12 / 18 / 27 / 13 | 0.63 | 0.21 (0.18) | 2.04, p = 0.15 |
| non-verbal | 102 | 13 / 27 / 21 / 23 / 18 | 0.51 | 0.30 (0.13) | 33.6, p < 0.0001 |
| talk | 100 | 21 / 30 / 24 / 17 / 8 | 0.40 | 0.29 (0.15) | 15.6, p = 0.0001 |
| walking lines aligned | 133 | 19 / 32 / 29 / 33 / 20 | 0.51 | 0.29 (0.13) | 38.8, p < 0.0001 |
| walking lines 20 cm apart | 141 | 17 / 37 / 34 / 34 / 19 | 0.50 | 0.26 (0.12) | 25.9, p < 0.0001 |

(The pooled row, 0.27 against 0.12, mixes conditions with different leans, which by itself inflates
"all one way"; the per-condition rows are the test.) More agents stick to one side than a coin gives,
so part of the side is a preference; but about 70% of these agents still change side at least once
in 4 identical repeats.

**Which factors move the side** (first plans, logistic regression, every condition, Holm-significant
over the whole report; `analysis/report.md`, section 1):

| Factor (own, as told) | Goes right (`plan_right`) | Goes left (`plan_left`) |
| --- | --- | --- |
| visiting Singapore from the United States (against living in Singapore) | OR 2.59 [1.90, 3.53] | OR 0.30 [0.21, 0.42] |
| in a hurry | OR 2.12 [1.56, 2.88] | OR 0.40 [0.29, 0.56] |
| assertive | — | OR 0.25 [0.17, 0.35] |
| older (70) | OR 0.51 [0.37, 0.69] | OR 2.31 [1.64, 3.25] |
| the talk condition | OR 0.47 [0.36, 0.60] | OR 2.83 [2.17, 3.71] |
| knows the other | OR 1.55 [1.25, 1.91] | — |

First side by residence (share right of first plans with a side): visitors 0.78 (independent), 0.79
(non-verbal), 0.68 (talk); locals 0.60, 0.44, 0.36. The prompt names only where the person lives, never
a side or a custom (`resolve_factors_v2`). A visitor meeting a local starts with a dance no more often
than two locals (independent 45 against 45 of 128, non-verbal 56 against 64, talk 64 against 60),
because the locals' side is itself near a coin. **No factor predicts whether the pair resolves**; only
the condition does (`resolved_plan_only`). A person's side follows the person; the pair's success needs
the two sides to match, and nothing in either person's factors makes them match.

At the cell level, the side the pair passed on flips between identical repeats 0.45 of the time (0.42
to 0.49; a coin would be 0.50), and the whole behaviour 0.79; 158 of 192 cells are coin flips by #63's
rule (`analysis/report.md`, sections 3 and 4). RF-11 should claim no rule for those cells.

## 6. What the agents said (`resolve_debrief_v2`), against what they did

The 1,536 agents of the design's 768 sessions (all repeats, no counterfactual pair); "missing": not
debriefed (never prompted) or no side basis in the reply.

| Answer (`side_basis`) | Agents | Share |
| --- | --- | --- |
| more room on that side | 604 | 0.39 |
| where the other person was | 547 | 0.36 |
| either side would have done | 221 | 0.14 |
| a custom or rule | 52 | 0.03 |
| what the other person did | 50 | 0.03 |
| did not move aside | 30 | 0.02 |
| missing | 32 | 0.02 |

- **"More room" does not predict the side.** In the 20 cm layout each agent starts 10 cm to its own
  left (walls 0.77 m left, 0.98 m right), with the other about 20 cm to its right. First plans took the
  roomier side (right) in 366 of 703 (0.52); agents who said "more room" in 201 of 382 (0.53). Read
  answers show two opposite meanings: "kept me in the wider gap" and "kept me tight to the wall and left
  the wider space on his side". In this layout the two cues, room (go right) and the other's line (go
  left), point opposite ways; either, used by both, would resolve it.
- **"Either side" does not mark the agents who flip.** It was given by 13% of debriefs in units that
  took one side all 4 times and 15% in units that changed: the agents do not know which of their sides
  are coin flips.
- **The visitor's convention is not stated.** Visitors keep right, but name a custom in 4 of 377
  debriefs (0.01), locals in 54 of 1,225 (0.04) (all 816 sessions, the counterfactual pairs included). One of the four: "I instinctively keep to the right, as
  I would back home in the US and as Singapore traffic generally does" (Singapore drives on the left).
- The debrief is asked about the whole encounter; the side compared is the first plan's. Round 1's
  finding that stated drivers often do not show in behaviour (`docs/round1-results.md`, 4.4) holds for
  the side too.

## 7. What it means for the next steps

- **Step 1, head-on:** LLM agents with a second chance resolve 0.59 of head-on meetings on their own
  plans; with one decision, 0.36. The gate is at its threshold either way (0.48 here, 0.53 in RF-30).
- **Step 2, candidate patterns** (for RF-11 to test, not rules yet):
  1. *After a dance, one person changes side and the other holds.* 74 of 88 rescued dances; when
     nobody changes, the dance does not end.
  2. *A visitor from a keep-right country keeps right* (and assertive or hurried people go right, older
     people left): a person-level side preference that the agents themselves do not name.
  3. Words and signals in these agents do not settle the side: the tie-breaker in pattern 1 comes from
     a change of plan, not from what was said.
- **Step 3:** pattern 1 and 2 are the kind of claim the published-studies check (RF-14) can test: side
  preference by country of origin, and how a pavement dance ends. Neither is checked here.
- **For the simulation:** the agents do not coordinate the side reliably; a rule that picks the side
  for the pair (a convention, or "the one who … switches") would remove most collisions, and the data
  above say which persons lean which way.

## 8. Caveats

- The model's fingerprint changed between RF-29/30 and this run (section 1): compare across runs with
  care. Within RF-39 every call is the same fingerprint.
- Independent's 0 of 90 rescued dances is close to certain by construction.
- The mock overstated the calls a session (11.1 against 8.6), so the cost estimate was high by ~10%.
- The keyword match for a side in a message, and `ROOM_M` (5 cm) for "more room", are mine.
- The first side is the reply to the first prompt; conditions differ in the signal and talk lines of
  that prompt, which moves the side (section 5): the conditions are not the same first decision.
- Repeat 1 pairs with RF-30 only up to the third decision; the sessions that reach it (most failures)
  go on differently.
