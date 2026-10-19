# Portable conflict rules: brief for the supervisor

*Choo Zhen Ming · 19 October 2026 · A proposal for discussion; nothing here is agreed.*

## What was found

You asked that an extracted rule should not be tied to spatial conflict and should ideally work in
any simulator. We reviewed four bodies of literature, surveyed six simulators besides our own, and
trialled two. **Verdict: feasible, with changes and a narrower claim.**

- **A rule can be written once, independently of any simulator.** Norm research has long done this
  with institutional grammar (Crawford and Ostrom; Frantz and Siddiki). We would adapt it.
- **Identical behaviour across simulators cannot be promised.** One behaviour layer over three
  motion models gave three sets of trajectories (Curtis et al.), and every re-implementation study
  we read found differences. We can promise the **same decision** in the same situation, and
  **measure** how far the movement differs.
- **Testing on unseen conflicts is possible, but human evidence is thin.** Queue cutting has usable,
  old American evidence (Milgram et al.; Langer et al.). Train doors and lift priority have a little
  (London, Taipei). Bus boarding has none. **No Singapore observation was found.**
- **Two findings change the plan.** No rule has yet been extracted from the LLM agents: the six we
  have are hand-written tests, as the paid pilot is on hold. And the best queue evidence concerns
  bystanders objecting and people asking to go first with a reason, which our rule format cannot
  yet express.
- **What is new** is the combination: rules extracted from LLM agents, run by ordinary agents in
  different simulators, tested on kinds of conflict they were not extracted from, against human
  evidence. The closest work, Zhang et al. 2026 (NTU), turns an LLM crowd into code, but in one
  simulator, on a new layout of the same task, checked against the LLM rather than people.

## Decisions needed

**1. The claim.** (a) "the same kind of conflict, in any simulator", or (b) "any conflict".
**Recommend (a):** the same decision, with behaviour measured against a standard set in advance.
*Evidence:* people carried conventions between games only within one class of game, in one
direction, sometimes to their cost (Cooper and Van Huyck; Cason et al.).

**2. The vocabulary.** Freeze its first version before any unseen test, or let it grow.
**Recommend freezing.** Define each term precisely (unit, ties, who can observe it), and cover rule
breaking and who reacts. *Evidence:* our draft already uses "arrival order" in two senses;
re-implementations diverged over "≤" against "<" (Edmonds and Hales).

**3. Rules for more than two people, and roles by category** ("people getting off go first").
**Recommend allowing both.** Otherwise neither the train-door evidence nor the finding that the
person directly behind a cutter objects most (Milgram et al.) can be tested.

**4. May a rule depend on a stated reason?** Such rules are rejected today. Options: keep rejecting;
allow the *kind* of reason (none, self-serving, genuine) as an observable feature; study it
separately. **Recommend the feature.** The asking-first evidence (Langer et al.; Folkes) is about
this; whether *any* reason helps is contested between them, and we would report that.

**5. The testbeds.** Use simulators as shipped, build our own, or a hybrid. **Recommend the
hybrid:** our current simulator; JuPedSim, an open pedestrian simulator, with our own small
queue-order layer, since its built-in queue cannot let anyone in part-way; and Mesa as a discrete
queue model. *Evidence:* both ran in our trial and repeated runs were identical; JuPedSim was about
three times faster than ours at 10,000 agents, though still slower than real time. The hybrid ranked
first under every weighting but one (decision 8).

**6. Seen and held-out conflicts.** **Recommend fixing the split before extracting any rule.** Seen:
passing and narrow passages. Held out: queues, vehicle doors, lift capacity. *Evidence:* tuning on
the test scenario hides failures (Wolinski et al.). No study we found holds out a whole kind of
conflict, so this design is ours, and we should say so.

**7. Trained models instead of rules.** **Recommend optional and secondary:** small decision trees
against a simple lookup table, with the rule engine as the reference. Labels from several LLMs (their
disagreements reported) combined with the rules; human data as the yardstick. Also needed: which
personal attributes must **not** change each decision. *Evidence:* trees run at 10,000 agents and
can be fully checked; reinforcement-learning policies need one per simulator, and none has been
shown to transfer between simulators.

**8. (New) Must each held-out conflict run in two different simulators?** **Recommend yes:** it is
the test the claim needs. It is also the only choice that changes the simulator recommendation:
without it, using JuPedSim and Mesa as shipped does as well.

**9. (New) What counts as human evidence?** **Recommend accepting** foreign evidence labelled with
city and year, and tables reproduced verbatim in later work (Milgram's queue data survives only so).
Obtain fourteen papers through the library, including two Singapore bus studies. Until then, test
bus boarding and escalators for clearance only, not realism.

**10. (New) The go-ahead and the order of work.** The next step writes code, and the earlier
instruction (no new simulation code until the literature is discussed) is not recorded as lifted.
**Recommend:** confirm it is lifted for this track; approve a small, capped pilot **after** the
vocabulary is frozen, so the first LLM-extracted rules are in the portable form; and, if possible,
obtain CrowdGym's code or dependency list, without which CrowdGym is a target in name only.

## What the evidence does not support

Identical behaviour across simulators; transfer to unrelated kinds of conflict; statistical
generality (only five kinds of conflict); Singapore-, age- or gender-specific realism in these
scenarios; trained models beating the rules; and any claim that these tests show LLMs "understand"
people, since they test the extracted rules.

*Still pending from earlier:* the ethics sign-off for the fictional-group factor, which this track
does not use.
