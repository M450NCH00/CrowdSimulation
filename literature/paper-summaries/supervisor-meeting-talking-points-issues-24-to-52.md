# FYP meeting — what was built and found, 13 to 19 October (issues #24 to #41, and #52)

Speaking notes for the meeting after Tuesday 6 October. They cover three pieces of work:

| Issue | What | Kind |
|---|---|---|
| #24 | A two-agent LLM negotiation simulator ("negsim"): GameChat rebuilt, with age and gender personas | code |
| #26 | An avoidance layer: many walkers stepping round each other (ORCA) | code |
| #28 | A rule format, a rule database, and walkers that follow the rules | code |
| #30 | Turning a conflict into a candidate rule with an LLM (built; run on a free mock LLM only) | code |
| #32 | Two people meeting *inside* a narrow passage; a fictional group that no rule may use | code |
| #35–#41 | "Portable rules" track (#34): four literature reviews, a simulator survey, a hands-on trial, a synthesis | research |
| #52 | How to describe a scene with several people to an LLM | research |

Full detail is in each issue's `WORK_LOG-<n>.md`, in `llm_negotiation/README.md`, and in
`portable_rules/docs/supervisor-brief.md` (two pages, ten decisions). Anything marked *(my view)* is
my own interpretation. Anything called a "proposal" needs your sign-off.

**Three things to say up front:**
- **No rule has been extracted from an LLM yet.** The six rules in the database are hand-written
  test rules. The paid pilot that would produce the first LLM rules is on hold.
- **Almost everything ran for free.** The 12 paid smoke runs in #24 cost about USD 0.004. Everything
  else ran on a mock LLM, a script that stands in for the model. Mock results show that the pipeline
  works. They say nothing about LLMs or people. Total spend so far: about USD 0.10 of the USD 2 credit.
- **I wrote simulation code before the literature review was discussed.** Your earlier instruction is
  not recorded as lifted, and I went ahead anyway. I need to know whether it is lifted (Part 6,
  decision 1).

---

## Part 1 — How the code works now

### 1.1 The pipeline in five steps
1. **Walkers move** under ORCA, the standard avoidance rule from last meeting's notes. Each walker
   picks the velocity closest to the one it wants that avoids a collision over the next few seconds,
   assuming the other does half the dodging. Nobody talks.
2. **When two walkers meet**, the simulator checks the rule database. If a rule matches, each person
   gets a role and an instruction (for example "pass on the left" or "you back out").
3. **If no rule matches**, plain ORCA carries on. At a gap only one person fits through, an "arbiter"
   lets whoever would arrive first go first.
4. **To get new rules**, a conflict is taken from a finished run and described to an LLM in words.
   Then either two LLM agents negotiate a rule, or one LLM sees both sides and states a rule.
5. **Every proposed rule is checked automatically**, tested on its own conflict and in a crowd of 100,
   and stored in a staging database. Only a person can promote it to the real rule database.

`simulate → conflict → describe to LLM → candidate rule → checks + crowd test → staging → (person promotes) → rule database → simulate`

- Steps 1 to 3 never call a model and cost nothing. Steps 4 and 5 call the LLM, and have run only on
  the mock so far.
- 1,381 automated tests. None of them calls a model.

### 1.2 GameChat rebuilt (#24)
- Two agents talk through DeepSeek. On each turn an agent sends a message and a stance: "I go first",
  "you go first" or "undecided". When one says "I go first" and the other "you go first", that is an
  agreement. The leader walks on and the follower slows down. With no agreement after four messages
  each, whoever would arrive first goes first.
- Three scenes: a doorway, an intersection, and a hallway only one person fits through.
- **Results (12 paid runs):**
  - With tasks only, the higher-priority task went first in 6 of 6 doorway runs, as GameChat reports.
  - With age and gender personas in the hallway, **the first speaker gave way in 5 of 6**.
  - Six runs only show that the platform works. Still, the second result means speaking order has to
    be balanced in any experiment, and the platform already does that.
- **A problem in GameChat's method:** its speed formula, applied to round bodies, lets them overlap at
  a right-angle crossing. I replaced its conflict "point" with a zone.
- **"Agreement" can be silent:** in 3 of the 6 runs an agent gave way in its hidden stance while its
  spoken message only stated its task. What counts as agreeing is a question for the study.

### 1.3 The avoidance layer (#26)
- It handles any number of walkers, walls, a sensing radius, and a record of what each walker can see
  of another: age and gender if visible, never the other's errand.
- **Plain ORCA deadlocks when a meeting is perfectly symmetric.**
  - Head-on, in a corridor wide enough to pass, two walkers brake to a stop 2 cm apart.
  - If both keep left, they pass with no delay. A 10 cm sideways offset also works.
  - So the deadlock comes from perfect symmetry, as Grover proved (last meeting, Part 1.4).
- **ORCA does things people don't do:**
  - told to do all the dodging but given no side, a walker walks backwards in front of the other;
  - a slower walker is pushed along by a faster one behind it;
  - passes are a few millimetres apart.

  These are habits of the algorithm, not behaviour. They will matter when we compare against people.
- **Speed:** 10,000 walkers take about 1.5 s of computing per 0.1 s simulated, about 15 times slower
  than real time in plain Python. This does not meet the 10,000-agent target yet.

### 1.4 Rules in action (#28)
- Six hand-written test rules (Part 2.6) were run against two frozen versions of plain ORCA: one with
  a tiny random nudge to break exact symmetry, one without.
- **Keep-left removes the symmetric deadlock.** Against the nudged version, which never deadlocks, it
  only makes the passing side predictable.
- **A rule that is safe for two people can fail in a crowd:**
  - with 50 walkers each way, the rules clear the crowd in 47 s instead of 83 s;
  - but the worst overlap between two bodies grows to about 20 cm, from 3 cm;
  - the cause is one rule, "the overtaker does all the avoiding": used alone, it gridlocks the flow
    in 15 of 20 runs.
- That is why rule generation (#30) tests every new rule in a crowd as well.
- Checking rules makes each simulation step 2.3 to 3 times slower (100 to 1,000 walkers).

### 1.5 Turning a conflict into a rule (#30): built, not yet run on a real LLM
- **18 conflict cases** are frozen from baseline runs. Each has a severity grade, from T0 (only in
  range) to T4 (a collision or a deadlock).
- **Two ways to get a rule.** Comparing them asks whether negotiating gives different rules from one
  model thinking alone.
  - **A: negotiation.** Two LLM agents negotiate, each seeing only its own view and its own errand.
    Agreement means accepting the other's exact proposal by its ID, so a changed rule is never
    mistaken for agreement.
  - **B: a single model.** One LLM sees both people and states a rule. It is asked several times, to
    check that it gives the same answer.
- **Every proposal is kept and sorted:** valid; needs talking first (it uses someone's errand);
  inconsistent; badly formed; or asks for something the format cannot say. The last two are findings
  about the format.
- **On the mock, the crowd test already caught bad rules.** Rules asking both people for 15 cm or
  30 cm more room settled their own conflict. In the two-way crowd, though, only 98 and 23 of 100
  walkers arrived within two minutes, against all 100 in 52 s without those rules.
- **The paid pilot is on hold.** Its worst-case cost is USD 0.65, against a USD 0.05 cap. Recommended
  fix: a hard spend cap, with sessions run in priority order (Part 6, decision 2).

### 1.6 Narrow passages and fictional groups (#32)
- **Meeting inside a one-person passage.**
  - New instruction, "back up": back out of the passage, wait, then go on.
  - Test rule: *the one who has walked less far in backs out*.
  - When the two start standing still, the fallback (whoever arrives first) gets neither through:
    80 of 80 runs stall. The test rule gets both through in 160 of 160 runs.
  - With one slow backer, choosing by distance means 0.64 m less backing but about 3 s more time than
    choosing the faster backer. The quicker choice needs each person's backing speed, which nobody
    can see, so no rule can state it.
- **A fictional group.**
  - Invented labels such as Kestrop or Pellund, with no description.
  - Agents may see the group. No rule may use it. A rule that tries is kept and counted, since a
    model trying is itself a finding.
  - It can test in-group against out-group treatment, not how a model treats real ethnicities.
  - **It is off by default, and needs your ethics sign-off before any paid run.**

---

## Part 2 — The rule format today

### 2.1 A rule in one sentence
**When** two people meet in a certain way and a condition holds on what *both* can see, **give them
roles**, and **tell each role what to do**. A rule is stored as data (a YAML file), never as code.

### 2.2 An example from the database

```yaml
rule_id: younger_yields_head_on        # a hand-written test rule, not a claim about people
encounter: head_on                     # kind of meeting: head_on, crossing, overtaking, single_file_segment
when:                                  # condition: every line must hold
  all:
    - {field: pair.time_to_collision_s, op: "<=", value: 6.0, unit: s}
    - {field: pair.age_difference_years, op: ">=", value: 20, unit: years}
roles:                                 # rank the two by age: the younger becomes "yielder"
  by: {field: agent.age, order: ascending, assign: [yielder, other], tie: no_match}
directive:                             # what each role does
  yielder: {responsibility_share: 1.0} # does all of the dodging
  other:   {responsibility_share: 0.0} # walks straight on
priority: 20                           # if two rules match, the higher priority wins
```

In words: *"When two people of quite different ages meet head-on, within 6 s of colliding, the younger
does all the avoiding."* Each file also records the rule's version, its status, and where it came from.

### 2.3 What a rule may read, and what it may not
- **May read** two kinds of thing:
  - quantities both people would compute the same way: distance, time to collision, how far apart
    their directions are, the narrowest width between them, the age difference;
  - what each can see of the other: age, gender, speed, body size, and how far into a passage they are.
- **May not read:**
  - **the other person's errand.** A rule that needs it could only work after the two had talked, so
    it is sorted as "needs talking first";
  - anything only one person knows, such as their own preferred speed or goal;
  - **the fictional group.** This is refused before any other check, and counted.

### 2.4 What a rule can tell a person to do

| Instruction | Meaning |
|---|---|
| `side_preference` | pass on the left or on the right |
| `responsibility_share` | how much of the dodging this person does, 0 to 1 (plain ORCA: 0.5) |
| `speed_scale` | walk faster or slower |
| `clearance_margin` | keep extra room from the other person |
| `passage_order` | go first, or wait, at a gap only one person fits through |
| `back_up` | back out of a passage and let the other through |

### 2.5 Safeguards built in
- **A version is never edited.** Any change is a new version, and each file's fingerprint is frozen.
- **Every rule records where it came from.** LLM rules go to a staging database. They reach the real
  one only when a person promotes them and gives a reason.
- **Ties are explicit.** If the two people tie (same age, say), the rule does not apply, and the next
  rule or plain ORCA decides.
- **A rule never fires on something its people cannot see.**

### 2.6 The six rules in the database (all hand-written tests)
Keep left when meeting head-on (and its mirror image, keep right); the overtaker keeps clear; first to
arrive goes first through a one-person gap; the younger yields head-on; the one who has walked less far
in backs out of a passage.

### 2.7 Why it has to change
- **It is tied to our simulator.** The kinds of meeting are defined by angles. Thresholds such as "6 s
  to collision" are tuned to ORCA. The instructions are ORCA's own settings, and time is counted in
  simulation steps. Another simulator could not read these rules as they stand.
- **It handles two people only, and gives roles only by ranking a number.** It cannot say "people
  getting off go first" (a role by category), or "the person behind a queue-cutter objects" (an
  observer).
- **It cannot use a stated reason**, although the best queue-cutting evidence is about people asking
  to go first and giving a reason.

---

## Part 3 — How we plan to change it (the portable-rules track, #34 to #41)

### 3.1 Why
You asked that a rule should not be tied to spatial conflict, and should ideally work in any simulator.
The plan is also to test rules on conflicts they were not made from, such as queue cutting and bus
boarding. Six studies checked whether this is feasible.

### 3.2 What the six studies found
- **#35, writing a rule independently of any simulator:** possible, and norm research already does it
  (with "institutional grammar"). But every study that re-ran a behaviour rule in a second simulator
  found differences. They came from details outside the rule: update order, tie-breaking, "≤" against
  "<".
- **#36, testing on unseen scenarios:** no field we read holds out a whole kind of situation, so our
  hold-out design is our own. People carry a convention over to a new game only within the same class
  of games.
- **#37, human evidence for the unseen scenarios:**
  - queue cutting has the best evidence (New York, 1978): the person directly behind a cutter objects
    36% of the time, and nobody three places back does;
  - at lifts in Taipei, people with wheelchairs or prams were fully let in first in only 24% of the
    trips where they should have been;
  - **no Singapore observation was found** for any of the five behaviours.
- **#38, training models on the rules:**
  - the cheapest decider used at large scale is a lookup table filled by LLM calls (8.4 million agents
    from 400 queries);
  - recommended first step: small decision trees;
  - keeping ethnic group out of a model's inputs is not enough on its own: a counterfactual test is
    also needed.
- **#39 and #40, other simulators:**
  - JuPedSim (an open pedestrian simulator) and Mesa (a general agent toolkit) both ran, and repeated
    runs gave identical results;
  - JuPedSim's built-in queue cannot let anyone in part-way, so we would keep the queue order
    ourselves (47 lines of code did it);
  - at 10,000 agents JuPedSim was about 3 times faster than ours, but still slower than real time.
- **#41, synthesis:** every part is **feasible with changes, under a narrower claim**. Five sub-claims
  were dropped, for example identical behaviour across simulators, and realism for bus boarding and
  escalators.

### 3.3 The narrower claim
- *Before:* a rule behaves the same in any simulator.
- *Now:* **in the same kind of conflict, a rule gives the same decision in any simulator that passes a
  shared set of tests.** How people then move is measured and compared, not promised.

### 3.4 Today's format against the proposed one (a proposal)

| | Today (format 3) | Proposed portable rule |
|---|---|---|
| Shape | when → roles → instruction | who; must, may or must not; which action; when it applies; what happens if someone breaks it |
| Kinds of conflict | head-on, crossing, overtaking, single file, defined by angles | room to pass; one at a time (passage, queue, vehicle door); limited capacity |
| What decides the kind of conflict | thresholds written in the rule, measured by ORCA (e.g. ≤ 6 s to collision) | each simulator's "perception translator"; thresholds go in a settings file per simulator, frozen before testing |
| People | exactly two, ranked by a number | any number; roles by category; observers of someone breaking the rule |
| Actions | ORCA settings (dodging share 1.0 / 0.0) | intentions (proceed, wait, back out, join the back), which each simulator's "action translator" turns into movement |
| Time | simulation steps | seconds |
| Words | "arrival order" used in two senses | every word defined (unit, ties, who can observe it); "predicted arrival" and "recorded arrival" kept apart |
| Where it runs | inside negsim | a stand-alone rule engine, plus two small translators per simulator: negsim, JuPedSim, Mesa, and CrowdGym once its code is available |

**An example.** Today's `single_file_first_arrival` becomes: "in a one-at-a-time *passage*, whoever is
*predicted* to arrive first goes, and the others wait." Using it at a *queue*, where arrival is
*recorded* and waiting means joining the back, is no longer the same rule. It becomes a deliberate
transfer test, reported whatever the result.

**The first check:** after conversion, the six test rules must give identical decisions and identical
paths in negsim. If they don't, the new format loses something and has to be revisited.

### 3.5 Proposed order of work (free until the pilot)
1. Your decisions (Part 6).
2. #42: a first frozen vocabulary and format. Convert the six rules, and the human evidence, on paper.
3. The rule engine and negsim's two translators, with the identity check above.
4. Written descriptions ("scenario cards") for queue cutting, train doors and lift priority, plus the
   JuPedSim and Mesa testbeds.
5. The evaluation harness, rehearsed on the six test rules.
6. **Prompt version 3 and the paid pilot.** The LLM writes rules directly in the new format, and these
   are the first LLM rules.
7. Optional: trained decision trees. Blocked: CrowdGym, until its code is available.

*(my view)* Running the pilot before step 2 would produce LLM rules in a format we are about to replace.

---

## Part 4 — How the scene is described to the LLM

### 4.1 How it is done today
- **Text only**, built from fixed sentence templates. Each template is frozen with a fingerprint, so
  changing the wording means a new version.
- **Two views of the same conflict:**
  - negotiation (A), first person: each agent sees only its own view, under "ABOUT YOU", "WHERE YOU
    ARE" and "THE OTHER PERSON";
  - single model (B), third person, both people: "PERSON 1", "PERSON 2", "THE TWO OF THEM".
- **Directions are relative to the person** ("ahead of you and 15° to your left"), with metric numbers.
  Distances are rounded to 0.1 m, widths to 0.01 m, speeds to 0.01 m/s, angles to whole degrees.
- **Only what a person standing there could perceive.** The other's age and gender appear only if
  visible, and their errand never does.
- **No convention is named.** The prompt never says "keep left", so the test is whether the model
  brings one itself (the prompt question from last meeting, 6.7 item 3).
- After the scene come the rule format (the fields and instructions from Part 2), a placeholder
  example that is not a real rule, and the reply format (JSON).

**What agent A is shown** (the template's lines, filled with example values):

```text
ABOUT YOU
- You are 34 years old.
- You are a woman.
- You are on your way to work.
- You are walking at 1.21 m/s. Your usual walking speed is 1.34 m/s.
- Your body is 0.46 m wide.

WHERE YOU ARE
- You are in a passage 2.40 m wide. The wall on your left is 0.82 m from you, the wall on your right 1.12 m.
- 4.0 m ahead of you, the passage narrows to 0.90 m for 1.5 m.
- Other people are walking around you as well.        <- the only line about everyone else

THE OTHER PERSON
- They are 3.2 m away, ahead of you and 15° to your left.
- They are walking at 1.05 m/s, in the opposite direction to you, and the distance between you is shrinking.
- Their body is 0.44 m wide.
- They look about 70 years old.
- They look like a man.
- You do not know where they are going, unless they tell you.
```

**Its limits:**
- **One other person is described in full, and everyone else gets one line.** That is fine for two
  people. It is not enough for a queue or a crowded train door.
- **It gives widths, not capacities.** The rule-generation prompts say "narrows to 0.90 m", not "only
  one person fits through at a time". (The #24 negotiation prompt does say it.)
- The scene part is about 220 tokens.

### 4.2 What the literature says (#52: five papers read in full, about 15 screened)
- **No study compares ways of describing a scene for pedestrian or crowd conflicts.**
- The two measured comparisons are spatial puzzles:
  - multi-agent pathfinding: a text map did better than a list of coordinates and better than an image,
    which did worst (very few runs);
  - grid navigation: coordinates (e.g. JSON) did better than grid drawings and prose, especially for
    mid-sized models (an 8-billion-parameter model: 66% against 30%).
- **The one LLM crowd simulator with a perception rule** describes only people within 8 m, inside a
  200° field of view, and not hidden. Only **the three nearest** are described in full; the rest are
  counted. So its prompt stops growing as the crowd grows. In another crowd simulator with no cap,
  requests grew roughly in line with crowd size (about 2,000 at 50 agents, over 6,000 at 250).
- **Two reported failures, neither tested:**
  - agents went into a bathroom meant for one because it was called a "dorm bathroom". The authors
    suggest calling it a "one-person bathroom", i.e. stating the capacity;
  - another crowd simulator blamed the lack of herding on giving agents no information about how
    others were moving.

### 4.3 Proposal: to test, not to adopt yet
1. **Keep today's first-person lines**, so new runs stay comparable with the old ones.
2. **Add a rule for who is perceived:** within a range, inside a field of view, not hidden by walls or
   bodies.
3. **Describe the three nearest people in full**, nearest first, and the rest in **one summary line**
   (how many, how many are getting closer, the range of distances).
4. **Give movement** (speed, heading, whether the gap is closing) for everyone described in full.
5. **State capacities** ("only one person fits through at a time"), not just widths.

**Tests to run before freezing a new prompt.** Each uses the same cases, changes one thing, and runs on
at least two LLMs:
- T1: prose against one JSON line per person;
- T2: one, three, or everyone described in full, with 2, 5 and 10 people present;
- T3: width alone against width plus capacity;
- T4: change one person's apparent age or gender, all else equal.

**Cost is not the problem.** Tokens for the scene part:

| Format | 2 people | 5 people | 10 people |
|---|---|---|---|
| Today (1 in full) | 220 | 220 | 220 |
| Everyone in full | 301 | 545 | 940 |
| Proposed (3 in full + summary) | 333 | 448 | 448 |
| One JSON line per person | 282 | 479 | 805 |

At DeepSeek's price, even 940 tokens comes to about USD 0.26 per 1,000 calls. The cost is driven by
the number of calls, not their length.

*(my view)* The values 8 m, 200° and "three" come from one single-author preprint. They are design
choices for us to make, not findings.

---

## Part 5 — Bigger picture

### 5.1 In one minute
- The machinery runs end to end and is free to run: walkers, rules, a rule database, and a pipeline
  that turns a conflict into a candidate rule and tests it.
- What is missing is the part the research question is about: **rules that come from an LLM**. Getting
  them needs the paid pilot.
- **A rule that works for two people can fail in a crowd**, so every rule gets a crowd test.
- The rule format should become portable **before** the first paid run.

### 5.2 Caveats to raise myself
- Apart from the 12 smoke runs, every result comes from hand-written rules or the mock LLM. **None of
  it is evidence about LLMs or about people.**
- The physical parameters are not from Singapore: body size comes from four young men in Japan, walking
  speed from forty people in France. Several values are placeholders.
- The reviews are web searches, not systematic reviews. Some papers were read selectively, and 14
  papers for #37 could not be obtained.
- Human evidence for the unseen scenarios is old, Western and thin. For bus boarding there is none.

---

## Part 6 — Decisions I need from the meeting

**Must decide now (they block the next step):**
1. **Is the "no new simulation code until the literature review is discussed" instruction lifted?**
   Code already exists from #24 to #32, and the next step (#42) writes more.
2. **The paid pilot.** Do you approve a hard spend cap, with sessions run in priority order? And
   should it run only after the new format is frozen? (Worst case today: USD 0.65 against a USD 0.05
   cap. About USD 1.90 of the credit is left.)
3. **The claim:** "the same kind of conflict, in any simulator" (recommended), rather than "any
   conflict".
4. **Seen and held-out conflicts, fixed before any rule is extracted** (recommended). Seen: passing
   and narrow passages. Held out: queues, vehicle doors, lift capacity.
5. **Can I get CrowdGym's code, or at least its dependency list?** Without it, CrowdGym is a target in
   name only. Also: is the public GitHub repository `ntu-fyp-25/crowdgym` the senior's? I have not
   opened it.

**On the new rule format (my recommendation in brackets):**
6. Freeze the first vocabulary before any unseen test, or let it grow? *(freeze)*
7. Allow rules for more than two people, and roles by category? *(yes)*
8. May a rule depend on the *kind* of reason someone gives (none, self-serving, genuine)? *(yes, as a
   visible feature)*

**On testing:**
9. Testbeds: negsim, plus JuPedSim with our own queue layer, plus Mesa? *(yes)*
10. Must each held-out conflict run in two different simulators? *(yes: it is the test the claim
    needs)*
11. Accept foreign human evidence labelled with city and year, and request 14 papers through the
    library, including two Singapore bus studies? *(yes)*
12. Trained models as optional and secondary: small decision trees, compared against a lookup table?
    *(yes)*

**On the LLM prompt (#52):**
13. Run tests T1 to T4 before freezing prompt version 3? And who sets the perception values (range,
    field of view, how many people in full)?

**Still pending from earlier:**
14. The ethics sign-off for the fictional-group factor, or should it be dropped?

**Smaller questions, fine by email:**
- Plain ORCA passes people a few millimetres apart, inside our 0.1 m "near miss" distance. Do we
  report that as a finding, or tie the distance to a published personal-space figure?
- Rules that give one person all the dodging gridlock a crowd. Should they be limited to sparse
  meetings, softened in crowds, or refused?
- Should passage-meeting cases start with the two people standing still or walking? Standing, the
  fallback always stalls. Walking, it gets them through only by pushing one person backwards.
- In a negotiation, is a hidden stance enough to count as agreeing, or must the concession be said out
  loud?
