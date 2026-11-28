# FYP meeting — the first paid pilot, and decisions needed (issue #64, 24 October 2026)

Speaking notes for the next meeting. They cover the first paid run of the resolve-first track
(#55): round 1's pilot, head-on in a corridor (RF-9, issue #64; PR #91). The full report is
`llm_negotiation/runs/rf_pilot_v2/pilot_report.md`; the detail is in `WORK_LOG-64.md`.
Anything marked *(my view)* is my own interpretation.

**Three things to say up front:**
- **The pilot worked, and it was cheap.** 72 sessions, all three conditions (independent,
  non-verbal, talk), about USD 0.0009 a session. The whole issue spent USD 0.075.
- **It caught a flaw in my own pipeline before the big run.** The simulator did not carry out the
  agents' plans the way the prompt describes them. I fixed that before the main pilot.
- **I need four decisions from you** (Part 3), two of them ethics sign-offs.

---

## Part 1 — What the pilot found

- **Can the LLM agents resolve a head-on meeting by themselves?** Sometimes. With only their own
  plans (no collision avoidance between them), they resolved it in 17 of 72 sessions: independent
  8 of 24, non-verbal 5, talk 4. Plain ORCA, the standard avoidance model, never "resolves" by
  this measure: it always passes within the near-miss distance.
- **More interaction did not help yet.** Talk did worst, and the agents spoke once in 24 talk
  sessions. *(My view:* part of this is a wording problem in what agents are told: a slight drift
  by the other person is described as "walking across your direction", and 28 of 30 agents told
  that reasoned about a crossing. I propose to fix the wording before the screen.)
- **The model keeps right.** Both people kept to their right in 56 of 72 sessions. Singapore
  drives on the left; whether its pedestrians keep left is for the verification step (RF-14).
- **It is very random.** Asked the identical question again, the agents behaved differently in
  77% of pairs. A factor will have to change behaviour a lot to stand out from that.
- **It cites no sources.** Asked afterwards what their decision was based on, 85% said "common
  sense" or courtesy; almost none named a rule or study.

**The flaw it caught.** In the first 12 sessions, plans like "drift right 10° for 2 s" moved an
agent only about 0.3 m, and as soon as the step ended the agent was steered back to its old line.
No session resolved. With plans carried out as the prompt describes them, the same plans resolve
4 of 12. I made that change (and allowed a step to start at a distance or a time, which the model
kept asking for) before the main pilot.

## Part 2 — Decisions I have made (for your information)

1. **Factors for the actual run (RF-10):** I want to include **perceived attractiveness** (your
   suggestion), because bias can affect the decision a person makes; and **real ethnicity**,
   replacing the invented "fictional" groups of issue #32, because the simulations are set in
   Singapore. Ethnicity would use Singapore's groups at their real resident shares: 73.9%
   Chinese, 13.5% Malay, 9.0% Indian, 3.6% Others (SingStat, *Population Trends 2026*). Neither
   is used in a paid run until you sign off (Part 3).
2. **No extracted rule may read a person's ethnicity or attractiveness.** The study measures
   whether the model is biased; the simulator must never apply that bias to people.
3. **The other person's age and gender are told from 10 m**, not only within 5 m: in a head-on
   meeting nobody was ever within 5 m when asked.

## Part 3 — Decisions I need from you

1. **Paid runs and the budget.** The pilot was approved for that issue only. I need approval
   for RF-10 and a cap: about **USD 0.30** for a screen of 250 sessions, more if it is sized for
   the randomness (USD 0.33 to 0.55; see 4). The account holds USD 1.41, not the USD 1.90 my
   records implied: about USD 0.41 of the original USD 2 is unaccounted for. The track's planned
   total of about USD 1.80 needs revising to fit.
2. **Ethics sign-off for perceived attractiveness.** Agents would be told "You find them
   attractive." or "You do not find them especially attractive." about the other person, and we
   measure whether it changes who gives way.
3. **Ethics sign-off for real ethnicity**, and three questions on how it is done:
   - is it acceptable to tell an agent the other person's ethnicity as seen from appearance
     ("They look Malay.")?
   - how should "Others" be described to the agent (for example "You are of another ethnicity,
     neither Chinese, Malay nor Indian.")?
   - real shares mean few sessions with Malay, Indian and especially Others: is a
     same-or-different comparison at real shares enough, or should the screen over-sample the
     smaller groups and weight them back?
4. **How to size the screen against the randomness.** For about 10 outcome events per factor, a
   screen of 13 factors needs over 600 sessions. Options: screen fewer factors (6 to 8: 375 to
   460 sessions); drop the talk condition, which was barely used; or lower the model's
   temperature to reduce its randomness, which changes what we measure.

**Still open from before:** what "verify with real human behaviour" means (published studies
only, or observed data in Singapore), and how far the portable-rules track is paused.
