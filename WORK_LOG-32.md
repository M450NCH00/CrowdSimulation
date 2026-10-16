# Work Log — Issue #32: [Feature] SI-3a.2: fictional ethnicity attribute and meetings inside a single-file passage

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/32
**Branch:** `feat/32-fictional-ethnicity-passage-meetings`
**Started:** 2026-10-16 20:37 (UTC+8)

## Understanding the issue

This is SI-3a.2, a follow-up to #30 (SI-3a). It changes what rule generation shows a model, so
it has to land before #30's paid pilot (Part 11), whose data would otherwise match no later
run. It makes no paid call. Two independent additions:

1. **A fictional ethnicity attribute** (`ethnic_group`), with invented group labels that carry
   no description, as a design factor of rule generation (group pair same or different, and a
   rotation of which label goes to whom) with a visibility switch of its own. Agents may *see*
   it; **no rule may read it**, and a rule that tries is kept as data in a new validation
   category, `protected_attribute`, since a model conditioning on ethnicity is a finding. It
   is off by default and needs a supervisor's ethics sign-off, recorded in `CLAUDE.md`, before
   any paid run may switch it on. Outcomes (who conceded, whose proposal was accepted, who got
   the larger share) are logged so that they can be stratified by group pair and visibility.
   Fictional groups test in-group against out-group (the minimal group paradigm) and cannot
   show how a model treats real ethnicities; the docs must say so.
2. **Meetings inside a single-file passage.** Today the rule format cannot say "the one who
   has walked less far in backs out". New scenarios start two agents at their meeting point
   inside a passage (symmetric and asymmetric, and with different maximum and backing speeds).
   New pair-level perception fields say whether each is inside the passage and how far it is
   from each end, and a new directive, `back_up`, makes an agent back out of the passage, wait
   for the other to clear, and go on. Rule schema version 3 carries both, with a load-time check
   that exactly one role backs up, and a seed rule, `passage_shorter_backs_out`. Intentional
   backing must be told apart from issue #26's walking-backwards artefact.

Then the prompts (a new frozen version), new case versions, a mock that exercises every new
path, a re-preview of the pilot's cost with an options table for open question Q5 of #30, and
behaviour checks over at least 20 seeds.

**What the code already does inside a passage (Part 2.1), established before anything was
written** (the 20:40 entry below has the numbers): the arbiter takes the pair on the first
step, makes the one that will be out of the segment sooner (going forward) the leader, and
gives the follower a speed bound of 0. It has no backing of its own: ORCA, in which the
follower does all of the avoiding (share 1) and the leader none, pushes the follower
*backwards* at almost the leader's speed until the leader has cleared, and that motion is
counted as issue #26's walking-backwards artefact. There is nothing in the arbiter to expose,
so `back_up` is new.

**Assumptions** (small ambiguities, stated rather than asked):
- A1. "A flag marking it as not referenceable by rules" is a flag on the attribute's
  definition (`AttributeSpec.rule_referenceable = False`, exported by the perception module
  and documented in `perception.md`), not a key repeated in every record.
- A2. "Pair-level fields that both agents compute identically" are per-agent values computed
  once per pair from the two positions and the passage geometry, as `time_to_segment_s` is; in
  the rule format they are agent-level fields (`either.`, `both.`, `agent.`). Their names are
  the issue's (`segment_distance_travelled`, not `..._m`).
- A3. The consistency check of 2.5 applies to rules that state `back_up`, as the passage-order
  check applies to rules that state a passage order: such a rule must make exactly one role
  back up. A rule that states no `back_up` leaves an in-passage meeting to the arbiter, as
  before. (A stricter reading is an open question below.)
- A4. Tests that pin what this issue changes (the visibility switches, the directive fields,
  the log schema version) are updated, with the reason recorded; #28's A2 reading.

### Prerequisites (checked before anything else)

- **P1. PRs #25, #27, #29 and #31 merged, and this branch created from `main` — FAILED.** All
  four PRs are in state `MERGED`, but each into its stacked parent branch, not into `main`:
  #25 into `docs/22-simulation-conflict-rules-literature` (PR #23, open), #27 into
  `feat/24-llm-negotiation-simulator`, #29 into `feat/26-orca-avoidance-layer`, #31 into
  `feat/28-rule-format-database-following` (merge commit `32bd93e`). `origin/main` is still
  `5a0f7be` (2026-09-06) and has no `llm_negotiation/` at all; 130 commits of `feat/28` are not
  on it. Between `main` and the simulator stack sit seven open literature PRs (#9, #13, #15,
  #17, #19, #21, #23), each based on the one before. As the issue instructs, I stopped and
  asked. **The user's answer (2026-10-16, in this session): "Stack on #31"**: commit the two
  #30 leftovers to `feat/30-conflict-cases-rule-generation` and push them, cut this branch
  from it, and target the PR at `feat/30-…`. Such a PR will not close #32 on merge (only a
  merge into the default branch does), as #31 did not close #30.
- **P2. The two uncommitted #30 items — DONE.** Both were clear in status, so they were
  committed to `feat/30-conflict-cases-rule-generation` and pushed (`e49ab46..2dad845`), not
  discarded:
  - `a18f727` *feat: optional random starts for the two-way crowd (spawn_pattern: random)*:
    `negsim/scenarios/bidirectional_flow.py`, its tests in `test_crowd_scenarios.py` (7 new),
    a replay check in `test_rulegen_replay.py`, one row each in `llm_negotiation/README.md` and
    `docs/parameters.md`. Before committing, the full suite ran on the working tree: **1,230
    passed** (#30's 1,223 plus these 7; 289 s), pyflakes 4.0.3 clean.
  - `2dad845` *docs: a beginner's guide to the whole repository* (`BEGINNERS_GUIDE.md`,
    1,015 lines; checked for anything resembling an API key first: none).
- **P3. `WORK_LOG-30.md` read**, including DD65 to DD84 and open questions Q1 to Q6. This issue
  is implemented against those decisions as they stand; any change is recorded below as one.

## Plan

Written before writing code; the progress log records where it changes. Baseline: **1,230
tests pass**, pyflakes 4.0.3 clean (P2 above; Python 3.13.3, PyYAML 6.0.3, pytest 9.1.1,
matplotlib 3.10.8, a fresh virtual environment in the session scratchpad).

The constraint that shapes most of it: **nothing frozen may change.** Committed runs and cases
hash the resolved scenario, sessions are named by a hash of their design cell, the v1 prompt
templates pin a hash of the field glossary, the old mock's paths cycle by index, and committed
run folders are checked against their own log version. So every addition is versioned or
written only when set, and the old versions keep working.

1. **Part 2.1 first**: write down what the arbiter does in an in-passage meeting, from the
   code and from the scratchpad measurement (done: 20:40 entry), in `derivations.md`.
2. **`ethnic_group` (1.1, 1.2).** A persona attribute, hidden by default, never filled in when
   absent (so #24's personas and logs are unchanged), validated as a fictional label. Perception
   record version 3 carries it (own and, when visible, the neighbour's). In `negsim/rules`: a
   new refusal category `protected_attribute`, checked before the schema, for any reference to
   it in a condition, a role assignment or a tie policy, derived names included. Tests,
   including that no execution path reaches it (no field reads it, no snapshot holds it).
3. **Segment fields (2.3).** `in_segment`, `segment_distance_travelled`, `_ahead`, `_behind`,
   computed once per pair in `pair_features`, in both records and both snapshots; `null`
   outside the passage. Rule fields gain the schema version that added them, and a `boolean`
   kind.
4. **Rule schema 3, `back_up` and the manoeuvre (2.4, 2.5).** `rule.v3.schema.json` (boolean
   values, `back_up`), frozen; v1 and v2 load unchanged and cannot read v3 fields. The
   consistency check. In the run loop: a back-up manoeuvre (back out to beyond the passage's
   end, wait for the other to clear, go on) at the agent's own backing speed, a new optional
   physical parameter; the pair released from the arbiter while it lasts; its own phase in the
   trajectory, events and outcome, and excluded from the walking-backwards artefact. Log schema
   version 5, with folders of versions 1 to 4 still checked against their own.
5. **Scenarios and the seed rule (2.2, 2.5).** A `passage_meeting` scenario type;
   `passage_meet_middle_v1.yaml` and `passage_meet_with_speeds_v1.yaml`, every number cited or
   tagged; the seed rule `passage_shorter_backs_out` (`test_seed`); the choice criterion in
   `derivations.md`.
6. **The design factors (1.3 to 1.5).** An optional `design.ethnicity` block (off unless
   `enabled: true`): `group_pair`, `label_rotation`, `ethnicity_visible`, the labels and the
   framing word. Cells and session ids of designs without it unchanged. A paid run with it on
   refused unless `CLAUDE.md` records the sign-off. Per-session outcome rows for stratification.
   The full-factorial size, reported.
7. **Prompts, cases, mock (Part 3).** Templates version 2 (frozen with the existing tool), the
   glossary generated per template version so that version 1 still checks; new case versions
   of the 18 cases by re-stepping their source runs (every field of the old version checked
   equal); case-source runs and cases for the two new scenarios; a new mock policy beside the
   old one; validation of `protected_attribute` and of the previous format's category.
8. **Behaviour checks**: 20 seeds, both new scenarios and their variants, the arbiter's
   fallback against the seed rule against plain ORCA: deadlocks, time to clear, backing
   distance (intentional and artefact), makespan.
9. **End-to-end mock runs** with ethnicity on, then off, with the in-passage cases.
10. **Part 4**: the pilot's worst case under the new prompt version, the mock's largest valid
    reply as a floor for m, and the options table for Q5. The pilot config is not changed.
11. **Docs**: `fictional-groups.md` (new); `perception.md`, `rule-format.md`, `derivations.md`,
    `cases.md`, `rule-generation.md`, `log-schema.md`, `metrics.md`, `parameters.md`,
    `architecture.md` (decisions from DD85), READMEs.
12. **Verify** (full suite with the network blocked, pyflakes, a search for the API key, zero
    spend), push, and a PR into `feat/30-conflict-cases-rule-generation`.

## Progress log

### 2026-10-16 20:37 — Prerequisites checked; branch created

- What I did: read `github_issue_workflow.md` and the issue; checked P1 to P3 (above); asked
  the user about P1; committed and pushed the #30 leftovers; created this branch from
  `feat/30-conflict-cases-rule-generation` at `2dad845`.
- Why: the issue makes all three hard stops.
- Result / what I found: P1 failed (the stack never reached `main`); the user chose to stack.
- Next step: read the code and documents this issue changes (the arbiter first, since Part 2.1
  asks for its in-passage behaviour to be documented before anything is written), then fill in
  the understanding and the plan.

### 2026-10-16 20:40 — Part 2.1: what the arbiter does when two agents meet inside a passage

- What I did: read `negsim/avoidance/coordination.py`, `negsim/control/strategy1.py`,
  `negsim/conflict/{roles,timing,zone}.py` and the run loop, then measured it. A scratchpad
  script (not shipped) subclasses `corridor_to_bottleneck` to start both agents inside its
  4 m, 0.8 m segment, facing each other 0.1 m apart, and runs it with the arbiter on and off.
- What the code does, step by step:
  1. **Trigger.** On the first step on which the two perceive each other, a single-file
     segment lies on both paths and neither has cleared it, and their occupancy intervals of
     the conflict zone overlap. Both being inside already, both intervals start at 0: the
     arbiter takes the pair on step 0.
  2. **Who goes first** (`decide_roles`). Exactly one inside: it leads (physical precedence).
     Both inside: a negotiated leader if the directives name one (`passage_order`); otherwise
     Strategy 1, whose first measure (time to the zone) ties at 0, so its second decides: the
     time to *clear* the zone going forward at the agent's walking speed, `d_out / v`. The one
     out sooner leads; an exact tie goes to the lower index (or a seeded draw).
  3. **The follower** gets a speed bound of 0 (`follower_speed_bound`: it is at or past the
     zone's entry and the leader is not clear), so the speed it *wants* is 0. ORCA is not
     switched off: the follower takes all of the avoidance (share 1), the leader none (share 0).
  4. **Nobody decides to back up.** The leader walks on at its full speed; in a passage too
     narrow to step aside, the only velocities ORCA allows the follower are backward ones, so it
     is pushed back at nearly the leader's speed until the leader has cleared the zone. That
     is issue #26's walking-backwards artefact (`metrics.md`, section 10), and it is counted as
     one. The arbiter's own view of the follower does not move meanwhile: `path_s` never
     decreases, so its `d_in` stays where it was.
- Measured (one seed; no perturbation):

  | Start (agent 0, agent 1 in, m) | Arbiter | Result |
  |---|---|---|
  | 1.7, 1.7 (symmetric) | on | leader 0 (tie, lower index); agent 1 pushed back 0.0–2.4 s at up to 1.282 m/s, from x = 0.30 to 3.24 (1.24 m past the end); handed back to ORCA at 2.3 s; completed 12.3 s; 1 backward episode, 2.5 s |
  | 2.7, 0.7 (agent 0 further in) | on | leader 0 (out sooner); agent 1 pushed back 0.0–1.6 s at up to 1.277 m/s, x 1.30 to 3.21; completed 11.3 s |
  | both | off | deadlock at 4.6 s: the two creep together at about 0.01 m/s and stop; no backward motion |
  | 2.7, 0.7, agent 1 walking 0.5 m/s with a maximum of 0.8 | on | **collision at 0.3 s**: the follower cannot retreat as fast as the leader (share 0) advances |

- So: at equal speeds the arbiter's fallback already makes the agent that has walked *less*
  far in give way, but by an ORCA artefact, not by a decision, at a speed nobody chose, and only
  while the follower can outrun the leader backwards. There is no backing inside the arbiter to
  expose as a directive, so `back_up` is new; it will release the pair from the arbiter while it
  runs (the 21:30 entry and DD93 below say how).
- Next step: the plan; the labels; then the code.

### 2026-10-16 21:10 — Part 1.1: the default labels, searched

- What I did: web searches (standard mode), one or more per candidate, recorded in full in
  `docs/fictional-groups.md`. Treated as data.
- Result: **Zorvel, Kestrop, Dremmik** pass: no exact hit as an ethnonym, nationality, place,
  language, surname or word, including searches aimed at Malay, Tamil and Chinese; their near
  matches are a drug brand (Zoryve), a Danish street (Kestrupvej) and a tool brand (Dremel).
  Rejected: *Orvane* (the French river Orvanne and a former commune of that name), *Kelbrin*
  (Kilbrin, a parish in Cork), *Hollvek* (Höllviken, Sweden), *Fyrrel* (the surnames Farrell,
  Ferrell), *Quorlan* (the Cornish place-name element *korlan*), and three that passed the search
  but echo a word of a Singapore community, which a fictional label must not: *Velorn* (Tamil
  *vel*), *Tessivar* (the Tamil pronoun *ivar*), *Melvori* (*Melayu*). *Brannoq* passed and
  is kept as a spare (its nearest match is an ancient Gaulish tribe, the Brannovices).
- Also for Part 2.4: the backing speed can be cited. Nakahara, Ishii, Ida, Nakazawa and Yamamoto
  (2005), ISBS 2005, pp. 823–826, "Results and Discussion": ten healthy adults (21.8 years)
  walked backwards at 0.43 (slow), 0.92 (normal) and 1.68 (fast) m/s; the normal pace agrees
  with Grasso, Bianchi and Lacquaniti (1998). One small sample of young adults: it is a cited
  value, not a population norm, and `parameters.md` will say so.

## Open questions / risks

<Filled in as they arise.>

## Summary (fill in at the end)

<What changed, why, how it was verified.>
