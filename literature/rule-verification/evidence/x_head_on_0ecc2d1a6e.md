# x_head_on_0ecc2d1a6e: people almost never stop or back up; and its translation, both keep left

Issue #69 (RF-14). Sources keyed as in `../sources.md`. Grades: Supported, Partly supported, No
evidence, Contradicted.

This rule has two forms that say different things, so each is graded.

## A. The extracted rule (RF-11)

- **Says:** in a head-on meeting people keep the side their final plan takes, and almost never stop
  or back up; they slow and turn instead. Found in 2 of 3 runs; predicts `stopped`.
- **Fidelity (RF-11):** 52 of 52 held out, equal to its baseline (nobody stopped).
- **Step 1 numbers:** 3 first-plan stops in 432 agent plans, 1 session with a stop and 1 with backing
  up in `plan_only`, over the 216 sessions of RF-10's re-execution under `keep_line` and RF-30
  outside the exact-repeat set.

**Evidence for**
- [Moussaid2009], section 4.2 (full text): "a pedestrian i essentially continues to move at the
  previous speed and mainly adjusts the direction of walking" when the other is to the side; "in
  case of head-on encounters, a binary decision takes place … This decision process goes along with
  a significant decrease of walking speed". Slowing, not stopping.
- [Huber2014], discussion (full text): in the head-on (180°) scenario "only the walking path, but not
  the walking speed, was adjusted"; path changes were used in every scenario with an interferer.
- [Olivier2013] (abstract): "Both walkers reorient their path but the participant giving way also
  adapts his speed."

**Evidence against:** none found.

**Limits:** all three are laboratory tasks in which participants were told to walk to a goal, which
itself discourages stopping; none counts stops in everyday head-on meetings. No study found that
measures how often people stop or step back on a walkway.

**Grade: Partly supported.** Every study found describes avoidance by turning and, at most, slowing;
none reports stopping. The evidence is consistent but indirect.

## B. Its format 4 translation (RF-31): both turn 10° to their own left from 9.8 m

- **Says:** when the corridor is at least 0.2 m wide, both people turn 10° to their left from 9.8 m
  until the other has passed. The translator chose the side (the user accepted that, 2026-10-26).
- **Simulation (RF-18, verdict of record from RF-33's realistic crowd, 30 seeds): helps.** Severe
  conflicts fewer on 30 of 30 seeds, collided pairs fewer on 21 of 30 (p = 0.043), throughput better on
  25. On the 76 resolved Step 1 sessions it resolves all 76 but reproduces the agents' own outcome less
  than plain ORCA (0.20 against 0.36), because the agents mostly passed right to right.

**Where "left" came from: the translator, with no source.** RF-31's translation prompt
(`llm_negotiation/runs/rf31_round1_head_on/translations/x_head_on_0ecc2d1a6e.json`) never mentions
Singapore or keeping left; the extracted rule said "passing side equal to final_side" (each pair keeps
whatever side its plans take). The translator's own note: "the side choice [is approximated] by a fixed
left turn of 10 degrees". So the side is an arbitrary pick by the translator that happens to match
Singapore's guidance ([MOT2024], [LTA2025], [NParks-PCN]); the guidance can be cited for it, but it is
not where the rule came from. What made the rule help in RF-18 is that both people take the *same*
side, which is what the evidence below supports.

**Evidence for a shared side**
- [Moussaid2009], section 5 (full text): the side bias "can be interpreted as a behavioural
  convention that emerges because the coordination during evading manoeuvres is enhanced when both
  pedestrians favour the same side"; "it is therefore advantageous for an individual to develop the
  same preference as the majority". The mechanism of the rule, both choosing the same side, is
  supported.

**Evidence on which side, for Singapore**
- For left: Japan, also a left-driving country, is "a country where lanes in bidirectional flows
  conspicuously appear on the left side, as pedestrians generally avoid others by stepping to the
  left", confirmed there by a questionnaire ([Echeverria2026], full text). Singapore's official guidance
  advises pedestrians "to keep left when not overtaking" ([MOT2024]): guidance, not a study.
- Against reading the side from car traffic: "The side preference is not directly coupled to … the
  direction of car traffic, as can be illustrated … by the observed right-hand traffic organization in
  some areas of Great Britain" ([Moussaid2009], section 5).
- Against reading it from guidance: in Korea, under a keep-left rule for pedestrians, 59.3% kept left
  and 73.7% said they preferred the right ([Jung2013], abstract).
- The LLM agents themselves passed right to right in most resolved sessions (RF-11: 47 of 76; in the
  216 sessions above, 67 of 116 resolved).
- **No published study of the side Singapore pedestrians keep was found** (two searches,
  `../search-log.md`, rows 3 and 7).

**Grade: Partly supported.** That both choose one side is supported; that the side is left in
Singapore rests on guidance and on a neighbouring left-driving country, not on a study of Singapore,
and evidence elsewhere shows guidance and behaviour can diverge. Under the user's decision of
2026-10-30 (published studies only), the side itself has **no evidence** for Singapore.

## Decision (#55's table)

- A (never stops): Partly supported; it was not run on its own in RF-18 (it is what its translation
  replaced). Stays staged with its grade.
- B (both keep left): **Partly supported and helps → "the goal: promote" by #55's table.** Not promoted
  in this issue; see `../README.md`, "Promotion", for why it waits for the user.
