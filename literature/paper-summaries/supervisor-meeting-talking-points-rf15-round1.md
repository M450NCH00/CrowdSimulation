# FYP meeting — round 1 finished, and decisions needed (issue #70, RF-15, 31 October 2026)

Speaking notes for the next meeting. They cover round 1 of the resolve-first track (#55): head-on in a
corridor, from the paid pilot (RF-9) to the human targets (RF-38). The full summary, with the file behind
every number, is `llm_negotiation/docs/round1-results.md`; draft report text is
`llm_negotiation/docs/interim-report-draft.md`. Anything marked *(my view)* is my own interpretation.

**Three things to say up front:**
- **Round 1 is done, all four steps.** Round 1 cost about USD 1.34 in total, each paid run under its own cap.
- **The answer to "can the LLM resolve it?" is "barely, and only for two people".** It resolves a two-person
  head-on about half the time, and the rules behind it are weak. The behaviour that looks most human, its
  passing distance, is exactly what the extracted rules do not carry over.
- **I need decisions from you** (Part 3), the first on the budget.

---

## Part 1 — What round 1 found

- **Step 1: the agents resolve a head-on meeting 53% of the time** (102 of 192, 95% CI 0.46 to 0.60),
  just over the 50% gate I set before the run. Plain ORCA never "resolves" by this measure: it never
  collides, but always passes too close.
- **Talking or signalling does not help** (independent 0.55, non-verbal 0.58, talk 0.47; no difference).
  The failures are a "pavement dance", both stepping to the same side, and the agents' nods and words do
  not say which side (4 of 92 messages name one).
- **It does not scale.** Groups of three or four resolve 6 to 14% of meetings; inside a crowd the LLM's
  plans are worse than plain ORCA in 50 of 64 encounters.
- **Step 2: the extracted rules are weak.** Of 25 rules, 4 were found consistently, and one beat its
  baseline: an assertive person keeps their line and slows only late. "Keep right" is in every run's words
  but not in its numbers. No rule cites a real source, and no agent did either, in 2,681 debriefs.
- **Translating the rules into the simulator loses most of them.** One translated rule (both turn 10° left)
  helps a crowd: fewer severe conflicts on every one of 30 seeds. Another (slow down for a cane) gridlocks
  a crowd on 1 seed in 30.
- **Step 3: against people.** Every rule is at best partly supported by published studies. Assertiveness as
  the cause is contradicted (Knorr et al. 2016: who goes first depends on speed and heading, not personality).
  No study says which side Singaporeans keep. *(My view:* this is the gap that matters most for a
  Singapore model.)
- **The LLM agents pass at a human distance; the rules do not.** Agents pass 0.93 to 0.97 m apart, as people
  do (0.93 ± 0.17 m, Rapos et al. 2021). Every rule passes either at ORCA's 0.50 m (bodies touching) or at
  1.25 m. A rule that only says who gives way cannot fix this: the distance comes from ORCA underneath.
  **No round 1 rule is promoted.**
- **Step 4: factors change *how* agents act, not *whether* they resolve.** Assertive agents slow less;
  knowing or finding the other attractive makes them signal more. Nothing predicts who goes first. The
  model is very random: identical prompts change its behaviour 83% of the time, and no single-factor flip
  stood out from that.
- **What the agents say is not what they do.** They cite age, luggage, a phone and urgency, which show no
  effect; what does have an effect (familiarity, attractiveness) they rarely mention. The attractiveness
  effect is recorded as the model's bias, never as a rule.
- **Toward 10,000 agents:** the rules add about half again to a simulation step at 1,000 agents, but ORCA
  itself grows tenfold from 100 to 1,000. *(My view:* the bottleneck for 10,000 is ORCA and the neighbour
  search, not the rules.)

## Part 2 — Decisions I made (for your information)

All on my own authority, recorded in `CLAUDE.md`, #55 and the docs named.

- **22 October — the resolution design** (`docs/resolution.md`, D1 to D17):
  - the agent says what it physically does, never "who goes first" (measured from the replay instead);
  - it is told what a person would perceive (75° view to 10 m, detail within 5 m, hearing all round);
  - three conditions: independent, non-verbal, talk;
  - it is prompted only when a conflict is predicted, at most three times;
  - each agent is debriefed afterwards for the source of its decision;
  - the LLM is used only in set-up conflicts, never to run a whole crowd;
  - one scenario at a time, in rounds.
- **24 October — the factors**: perceived attractiveness and real ethnicity are in the screen (both ethics
  sign-offs approved by you that day). Rules may never read ethnicity.
- **25 October — plans are carried out "keep line"**: the simulator was undoing sidesteps; fixing it
  raised resolution from 31% to 53%. Every result since uses it.
- **26 October — head-on went on to rule extraction** although its gate passed narrowly.
- **27 October — how rules are judged in a crowd:** collisions count separately; factors at realistic
  Singapore shares; 30 seeds where a factor is rare. (Your decision of 26 October, that a rule may read
  attractiveness only as a person's own view of the other, is in `CLAUDE.md`.)
- **30 October — the goal is human accuracy, not efficiency.** "Verify with real human behaviour" means
  published studies only; measurable targets with tolerances fixed before measuring.
- **31 October — the promotion test:** a rule is promoted if it does not harm, is supported, and misses no
  human target that applies to it. Under it, nothing in round 1 is promoted. A target from a study that
  did not include a factor (for example a cane) will not count against a rule from the next run on.

## Part 3 — What I need from you

1. **Budget.** The DeepSeek balance is **USD 0.17** (29 October). The overall cap for paid runs (about USD
   1.80) is still not approved (pending item 1 in `CLAUDE.md`), and round 2 needs about USD 0.10 to 0.20.
   Can we top up, and what is the cap?
2. **Direction after round 1.** *(My view:* the LLM is useful for *how* people pass (distance, who adapts,
   attention), less for *rules* that a simulator runs.) Options:
   - (a) continue as planned: round 2 (narrow passage), then round 3 ("excuse me");
   - (b) move from rules to **parameters**: use what the agents do well, such as the passing distance and who
     adapts, to set ORCA's parameters, and test those against the human targets;
   - (c) both: round 2 as planned, with the rules judged on distance as well.
3. **The passing distance.** No rule can meet the human targets while ORCA sets the distance. Should a rule be
   allowed to set a margin, or should ORCA's own parameters change?
4. **The pending portable-rules question** (pending item 5): is the portable-rules track paused for the build
   only, or for the remaining literature issues too?
5. **For the interim report:** is round 1 enough for the results section, with rounds 2 and 3 as planned
   work, or do you want round 2 in it?
