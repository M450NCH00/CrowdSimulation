# Interim report: draft methods and results (RF-15, issue #70)

Draft text for the methods and results sections of the interim report (due 25 January 2027), covering
round 1, the only round finished. It is written to be edited into the report, not read as a record. Every
number is from `docs/round1-results.md`, which names the file behind each one; check there before changing
a number. Square brackets mark what still has to be decided or filled in.

---

## Methods

### Approach

The project asks whether a large language model (LLM) can serve as a model of how pedestrians resolve
conflicts, such as two people meeting head-on in a corridor. Following the supervisor's direction of
20 October 2026, the work proceeds in four steps. Step 1 tests whether LLM agents can resolve a conflict
at all, without being asked for a rule. Step 2 extracts the rule or pattern behind the resolutions, with
the reference it comes from. Step 3 checks the rule against published studies of human behaviour. Step 4
varies many factors of the people involved and finds which of them actually change the decision. The work
proceeds one scenario at a time, in rounds; round 1 is a head-on meeting in a corridor.

### Step 1: LLM agents in a simulated encounter

Each of the two people is an LLM agent (`deepseek-flash`). An agent is prompted only when a conflict is
predicted, and again only when something new happens, at most three times, at least one second apart. It
is told what a person in its place would perceive: everyone in front of it within 75° and 10 m and not
hidden (after Moussaïd et al., 2011), in full detail within 5 m (after Rio et al., 2018), with no fixed
number of people (after Wirth et al., 2023), what it hears from any direction, what has changed since it
last looked, and when the two would meet. The other person's factors are given from 10 m.

The agent replies with what it is trying to do (an intent) and what it physically does (a plan of steps:
a speed, a turn or a sidestep, backing up, and when each starts and ends). It is never asked who should go
first; who went first is measured from the replay. Three conditions differ in what the agents can share:
**independent** (each decides alone), **non-verbal** (each sees the other move and signal) and **talk**
(they can also speak). After each encounter, each agent is asked, outside its role, what its decision was
based on.

The plans are carried out in a two-dimensional pedestrian simulator. The Step 1 measure, `plan_only`,
replays the agents' own plans with no collision avoidance between them. A session counts as resolved if
both people leave the zone with no collision, no near miss and no deadlock, within the time limit. A second
replay, `plan_orca`, runs the same plans with ORCA (van den Berg et al., 2011) underneath, as a baseline.
Every prompt and reply is stored, and every replay can be rebuilt from its seed and the recorded plans.

### Design

Sixteen two-level factors were varied in a fractional factorial design (a 2^(16−11) resolution IV
fraction): the two people's ages and genders, urgency, a mobility aid (a cane), a load (a suitcase), being
distracted by a phone, assertiveness, residence, a note of a bad memory, ethnicity, the surroundings, the
time of day, perceived attractiveness in each direction, familiarity, and which agent is person 1. The 32
cells were run on two geometries (walking lines aligned, and 20 cm apart) in all three conditions: 192
design sessions. To measure the model's own randomness, 8 cells in each condition were run twice more with
identical prompts, three times in all (48 sessions). Counterfactual pairs, in which a single factor is
flipped and everything else is kept, added 48 more: 288 in all.

Before the run, a gate was fixed: the agents count as resolving the encounter if at least half of the 192
design sessions resolve in `plan_only`. The threshold is a judgement, not a sourced value. [Ethics: the
perceived-attractiveness and real-ethnicity factors were approved by the supervisor on 24 October 2026; no
rule may read a person's ethnicity, and a rule may read attractiveness only as a person's own view of the
other.]

### Step 2: rule extraction and translation

From the resolved sessions, an extractor (the same model) was shown the outcomes as tables and 15 sessions in
full, and asked for the rules behind them, with a reference for each. It was run three times on different
samples; a rule was kept if it decided like another run's rule on at least 95% of the rows. Each kept rule
was scored on held-out sessions (26 of the 102 resolved) against always predicting the commonest value.
The kept rules were then translated by the model into a rule format the simulator runs, and checked by
running each translation on the sessions it came from (the identity check).

### Testing in the simulation

The translated rules were run together on crowds, with ORCA for every pair no rule matches, against plain
ORCA on the same seeds: a two-way flow of 50 people each way, an opposing bottleneck and a narrow passage.
Whether a rule set "helps" or "harms" was fixed before any run: an exact sign test over paired seeds on
severe conflicts, throughput and delay, with collisions counted separately and any gridlock plain ORCA does
not have counting as harm. A rule's verdict comes from a crowd at realistic shares of each factor (Singapore
residents by age and sex; a cane by age), over 30 seeds.

### Step 3: comparison with human behaviour

The rules, their references and the factor effects were graded against published studies only. Measurable
targets were then taken from those studies (for example, the distance at which two people pass), each with a
tolerance fixed before any rule was measured: a value within one reported standard deviation of the study's
mean, or a direction by the same sign test. A rule is promoted only if it does not harm in a realistic
crowd, is at least partly supported by the studies, and is not outside or opposite on any target that
applies to it.

### Step 4: factor analysis

For each outcome (whether the meeting resolved, who passed first, the side, whether an agent slowed,
stopped, backed up or signalled), a logistic or linear regression on the factors, with Holm's correction
over every term in the analysis. A decision tree of depth three predicted who passes first, scored on
held-out sessions. Each counterfactual pair's flip rate was compared with the noise floor, the flip rate of
identical prompts. Factors named in the agents' private reasons were compared with the factors that had a
measured effect.

---

## Results

### Can LLM agents resolve a head-on meeting? (Step 1)

On their own plans, the agents resolved 102 of 192 design sessions (0.53, 95% CI 0.46 to 0.60), so round 1
passes its gate, but narrowly: the interval includes 0.50. Plain ORCA never resolved a session by this
measure (0 of 192); it avoids collisions but always passes within the near-miss distance. The three
conditions did not differ (independent 0.55, non-verbal 0.58, talk 0.47; paired McNemar p = 0.86, 0.49,
0.30). Signals and messages did not carry the information that mattered: nearly all signals were nods,
eye contact or waving the other on, and 4 of 92 messages named a side.

Most failures were a "pavement dance": both people stepped aside towards the same wall (16 of 22 collisions
in the non-verbal condition, 19 of 26 in talk). The model leaned right (66 of the 102 resolved pairs passed
on their right), but did not coordinate on it. Neither a more detailed description of the other's position
(17 of 64 resolved against 22) nor a larger model (18 of 64) helped.

The result did not carry over beyond two people. Groups of three or four resolved 4 of 64 meetings in the
independent condition and 9 of 64 in the non-verbal condition, against 35 and 37 of 64 for pairs. Inside a
crowd, the agents' plans were worse than plain ORCA in 50 of 64 encounters and better in 6.

### What rules lie behind the resolutions? (Step 2)

Three extraction runs wrote 25 rules, of which 4 were found in at least two runs. None read ethnicity or
perceived attractiveness. Only one beat its baseline on held-out sessions: a person who holds their ground
keeps their line at full speed and steps aside or slows only at close range (0.83 against 0.75). Every run
described a "keep right" convention in words, but none predicted the agents' first plans better than always
guessing right. No rule named a law, guidance or study as its reference, and no agent named a source in
2,681 debriefs.

Translating the rules into the simulator's rule format lost most of their content. In the earlier format,
two translations were equivalent to plain ORCA and a third gridlocked a crowd. In a richer format, one rule
(both people turn 10° left from 9.8 m) resolved every Step 1 session it was run on, but reproduced the
agents' outcomes less often than plain ORCA (0.20 against 0.36), because it sent every pair left where the
agents mostly went right.

### Do the rules help in a crowd, and do they match people? (Step 3)

In a realistic crowd over 30 seeds, the left-turn rule helped: fewer severe conflicts on all 30 seeds and
fewer collided pairs on 21 (p = 0.043). The cane rule (whoever faces a person with a cane slows) harmed: it
gridlocked the flow on one seed of 30.

Against published studies, every kept rule was at best partly supported. In particular, the extracted
rule's cause, assertiveness, is contradicted by Knorr et al. (2016), who found that who passes first is
predicted by walking speed and heading, not by personality. No published study of the side Singapore
pedestrians keep was found. Against the measurable targets, the agents passed at a human distance (0.93 to
0.97 m between centres, against 0.93 ± 0.17 m for two young adults; Rapos et al., 2021), but every rule
passed either at ORCA's 0.50 m, two bodies touching, or at the left-turn rule's 1.25 m. A rule that only
decides who gives way cannot fix this distance, which is set by the avoidance model underneath. No round 1
rule was promoted.

### Which factors drive the decision? (Step 4)

No factor had an effect on whether the meeting resolved, or on who passed first, after correction. The
factors changed how the agents acted instead: an assertive agent was less likely to slow (OR 0.10, 95% CI
0.05 to 0.21) and more likely to signal (OR 13.6), and an agent who knew the other, or found them
attractive, signalled more (OR 445 and 6.5). The decision tree for who passes first did no better on
held-out sessions than always guessing the commoner outcome (0.837 against 0.843).

The model's own randomness was large. Identical prompts changed the agents' behaviour in 0.83 of repeat
pairs, 23 of 24 repeated cells were coin flips, and no counterfactual pair moved behaviour beyond that noise
floor. What the agents said drove them did not match what did: age, load, a phone and urgency were named in
12% to 29% of their reasons with no measured effect, while familiarity and attractiveness had an effect but
were named in 6% and 3%. The attractiveness effect is treated as the model's bias, not a rule.

### Summary of round 1

[Draft paragraph.] An LLM can resolve a two-person head-on meeting about half the time, about as often as
ORCA with the agents' plans on top, and it does so for reasons it does not state and that published studies
only partly support. The behaviour it shows most clearly, a passing distance close to people's, is the part
the extracted rules do not carry into the simulator. In groups and crowds, the LLM's plans do worse than
ORCA alone. The rules that are extracted are either too weak to change ORCA or, where they change it, do not
match human targets.

[For the limitations section: one model and one scenario; the 0.50 gate is a judgement; most studies are
from Europe or North America, in laboratories; placeholders still in use (`docs/round1-results.md`,
section 6); the model's randomness. For the cost: about USD 1.34 for round 1 (USD 1.44 including Phase 1).]
