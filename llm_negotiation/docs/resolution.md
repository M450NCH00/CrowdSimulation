# Resolution: how LLM agents are asked to resolve a conflict (track #55, Step 1)

The specification that every later issue of track #55 (RF-2 onward) points to. It says what an
LLM agent replies when it meets someone in its way, what it is told, when it is asked, who moves
the bodies, what is stored, and how the work is split into one round per scenario.

**Status: decided by the user on 2026-10-22**, on their own authority. These are the user's
decisions, D1 to D17. They are not this project's proposals awaiting sign-off (the **DD** of
`architecture.md`) and not the supervisor's points (the **SV** of `architecture.md`, section
8.6); the decision record lists them in `architecture.md`, section 8.7. The supervisor
decisions still pending (paid runs and their caps, the ethics sign-offs, how far the
portable-rules track is paused, what "real human behaviour" means) are listed in the root
`CLAUDE.md`, "Pending sign-offs", and nothing here settles them.

**What it replaces.** The first version of RF-2 (#57) asked each agent for a fixed menu,
`priority`, `side`, `speed` and `back_up`, which framed every meeting as "who goes first". The
supervisor (2026-10-20) wanted to see *how* LLM agents resolve a conflict and then derive rules
from that; fitting factors to a priority would not show it. So the reply below says what the
agent physically does, and who went first is *measured*, not asked.

**Values.** Every number below is either sourced, with the source in `parameters.md`, section 8,
or marked **`[placeholder]`**. A result that depends on a placeholder must not be reported as
if it rested on data.

The issues that build each part are named in brackets, and track #55 gives their order.
**Built so far:** RF-2 (#57), on the mock: D1's reply parser, D2's description templates and
the `View`, D3's conditions, D8's debrief and D16's description side (`negsim/resolution/`;
templates `resolve_v1`, `resolve_debrief_v1`, `scenario_passing_v1`). RF-17 (#73), on the mock:
D2's description built from the running simulation with D10's perception for the LLM only and
D12's values (`negsim/resolution/perceive.py`, `configs/resolution/llm_view_v1.yaml`; template
`resolve_v2`, which words an unseen speaker as "someone" with a rough direction and a distance
band, where `resolve_v1` says "someone behind you"). RF-4 (#59), on the mock: D6's two modes,
carrying out the steps of D1 in the simulator, D16's execution side (events, conflict zone,
outcome columns, "resolved"), the physical outcomes, and replays rebuildable from the session
record (D13) (`negsim/resolution/execute.py`, `outcomes.py`, `replay.py`). RF-3 (#58), on the
mock: the encounter protocol, D3 to D6 and D8 (the trigger, event-driven decision points with
their guards, the three conditions, the end and the hand-over to ORCA, the debrief), D11's
encounters of more than two people with a cap, D13's storage, one outcome row per session, and
the experiment layer `resolution` (`negsim/resolution/protocol.py`, `design.py`,
`experiment.py`; `docs/encounter-protocol.md`). Nothing else yet. Configs and templates from
before this track behave exactly as before.

## D1. The reply

```json
{"message": "Excuse me, I'll keep to this side.",
 "signal":  "eye_contact",
 "intent":  "Move over to my left a little early and keep walking at a steady pace.",
 "steps": [
   {"start": {"at_distance_m": 6}, "turn": {"to": "left", "degrees": 10},
    "speed_mps": 1.1, "until": {"seconds": 2}},
   {"speed_mps": 1.1, "until": "other_passes"}
 ],
 "reason":  "There's a wall close on my right, and moving early avoids an awkward dance."}
```

| Field | Values | Rules |
| --- | --- | --- |
| `message` | text | Talk condition only. Everyone within hearing range hears it, from any direction. |
| `signal` | `none`, `eye_contact`, `nod`, `wave_on`, `hold_up_hand`, `point`, `other` | Non-verbal and talk conditions only. Seen only by people whose view contains the agent. Never heard. |
| `intent` | free text | What the agent is trying to do. It comes **before** `steps`, so the numbers follow from a plan. |
| `steps` | a list, carried out in order | `[]` means "carry on as I am", and must be written explicitly. |
| `steps[].start` | `"now"`, `{"at_distance_m": d}`, `{"after_seconds": t}` | First step only. Each later step starts when the one before it ends. |
| `steps[].speed_mps` | 0 to the agent's `max_speed` | Target speed. `0` is stop and wait. |
| `steps[].turn` | `{"to": "left" or "right", "degrees": n}` | Heading offset from the agent's desired direction, in its own frame, held for the step. |
| `steps[].back_up_m` | metres | Walk backwards, at the agent's `backing_speed`. |
| `steps[].until` | `{"seconds": t}` or an event | Passing encounters: `other_passes`, `other_stops`, `i_am_out_of_the_stretch`. After the last step ends, the agent steers back towards its goal. |
| `reason` | free text, private | Never shown to anyone. Last field. |

There is **no `priority` field**. Who went first is measured in the replay. Agents are discs of
a fixed size: **no turning the body sideways and no change of body size** during a run (the
user's decision, to keep the simulation simple).

A scenario may add its own `until` events (D16); the three above are those of passing
encounters. (Templates and parser: RF-2, #57.)

## D2. The description an agent is given

In this order, with the fixed text first so that the provider's prompt cache can reuse it: the
role and instructions, then the reply format, then the description below, then the
decision-point wrapper.

```
ABOUT YOU               age, gender (visibility switches), errand, speed, usual speed, body width, own factor lines (RF-5)
YOUR NOTES              memory notes (a designed factor, off by default, D7)
WHERE YOU ARE           walls, passage widths, narrowings (as describe.py does today), situational lines (RF-5)
WHO YOU CAN SEE         everyone within 75° of straight ahead and 10 m, not hidden behind someone nearer
                        full detail within 5 m, one short line from 5 to 10 m
                        per person: distance and direction, motion, change since you last looked, body width,
                        observable factor lines, observed signal, pairwise lines for this observer only (RF-6)
WHAT YOU CAN HEAR       speech within hearing range, from any direction; a person not in view is "someone behind you"
WHAT YOU HAVE DONE      from the second decision point: one line per earlier decision point (intent and what came of it)
TIME TO MEET            "At your current speeds you would meet Person 1 in about 2.4 s."
```

- Left and right are always the agent's own.
- The instructions say what others perceive: the agent's words (within hearing range), its
  signals and its movement (if they can see it), **never its intent or reason**.
- **Never in a description:** another person's errand or private factors, the fictional group
  (off by default), any walking convention, "usually", "one of you has to go first", or
  `persona_v1`'s scene text.

The view cone (75°), the seeing range (10 m) and the detail range (5 m) are sourced (D12). The
hearing range is derived from measured speech and background levels (3.2 m in a public indoor
place; `parameters.md`, section 8.4, issue #73). (Perception for the LLM: RF-17, #73. Factor lines: RF-5,
#60, and RF-6, #61.)

## D3. Conditions

**First person only.** An agent is always given its own view: what it perceives itself. There
is no third-person condition in this track (#30's condition B, where one model saw both people
and stated a rule, is not used). The only prompts that are not a person in the scene are the
debrief (D8), and RF-11's extractor and RF-12's translator, which read results.

| Condition | Decision points per agent | What the agent can do |
| --- | --- | --- |
| **Independent** | one, at the trigger | Move. No message, no signal. |
| **Non-verbal** | up to 3 | Move and signal. |
| **Talk** | up to 3 | Move, signal and speak (`message`). One message per agent per decision point; speaking takes simulated time. |

## D4. When an agent is prompted (the trigger)

All of these must hold:

- it sees the other (D2's view) or hears them speak to it;
- the distance between them is shrinking;
- the conflict detector predicts both in the same conflict zone at the same time (or someone
  coming through a single-file stretch ahead);
- it is not already in an encounter with them.

Seeing someone is not enough on its own. (Encounter protocol: RF-3, #58.)

**As built (RF-3, #58).** The conflict prediction is the scenario's (D16). For the passing
scenarios: a shared single-file segment still to be cleared, or a closest approach under the
safety distance at the present or the desired velocities, not yet passed. Each member's first
prompt needs D4 to hold for it, so the person ahead in an overtaking case is first asked when it
perceives the other. `encounter-protocol.md`, sections 2 and 3, and `parameters.md`, section 8.6,
give each definition.

## D5. When an agent is prompted again (event-driven)

Both (a) and (b) must hold.

**(a) The conflict still matters:** it is still predicted, or the agent's plan has ended.

**(b) Something new happened**, from this agent's point of view:

- the other changed speed or direction noticeably, stopped, or started backing up;
- the other signalled or spoke;
- a new person came into view or was heard;
- the agent's own plan is failing (the predicted closest distance is below the safety distance
  again);
- the agent's plan has ended.

Guards:

- only the agent who noticed is prompted;
- at least 1 s between two prompts of one agent;
- at most 3 decision points per agent per encounter;
- every decision point logs why it fired.

Thresholds for "noticeably": first set as placeholders (0.2 m sideways, 0.2 m/s, 5°); issue #73
replaced them with the thresholds of human motion perception: a 7% change of speed and 2° of
direction (`parameters.md`, section 8.4).

**As built (RF-3, #58).** Each reason is logged with the person it concerns (`other_stopped:1`,
`signalled:0`, `heard:0`, `came_into_view:7`, `plan_failing`, `plan_ended`). A plan with no
steps never "ends". A signal is made during the step after its decision point; a message is
heard when it has been said, at 2.5 words a second `[placeholder]`
(`encounter-protocol.md`, section 3).

## D6. Who moves the agents

- **Live loop: plan only (`plan_only`).** The encounter's agents follow their plans; ORCA does
  not steer them away from each other, but still handles walls and everyone else. Everyone
  outside the encounter is plain ORCA. This mode is the Step 1 measure, because plain ORCA
  already passes a head-on pair without help.
- **Second replay: plan + ORCA (`plan_orca`).** The same plans at the same times, with full
  ORCA. This is an approximation, because the agents would have seen a different world. It
  needs no LLM call.
- An encounter that is still unresolved after its last decision point is recorded as **not
  resolved by the LLM**. ORCA then takes over, and what ORCA does after that is recorded
  separately. *As built (RF-3, #58):* ORCA takes over when every prompted agent has used its
  decision points and has no plan left, while a conflict is still predicted; the outcome row's
  `resolved_by_llm` counts a `plan_only` resolution only if ORCA did not take over
  (`encounter-protocol.md`, sections 5 and 7).

**As built (RF-4, #59).** In `plan_only`, from the encounter's first decision, the simulator
leaves out the ORCA half-plane between the encounter's two agents, and the arbiter's speed bound
does not apply to them. Everyone else, and the walls, are as before. The encounter goes back to
ORCA when the protocol releases it (RF-3), when one of the two arrives, or when they have passed
each other with no plan left to run. In `plan_orca` the plan replaces only the preferred
velocity. An empty plan there changes nothing, so empty plans reproduce the plain run exactly
(tested). A step carries out D1 as follows:
- `speed_mps` is the preferred speed; with none, the agent's own speed.
- `turn` is an offset from the desired path direction.
- `back_up_m` backs against the path at the agent's `backing_speed`.
- `start` holds the first step back.
- `until` is asked of the scenario.

After the last step the agent walks on to its goal. `parameters.md`, section 8.5, gives each
definition. A replay runs a session's plans on its case's own run and seed, in either mode,
under `runs/<experiment>/replay/<session_id>/<mode>/`. It is rebuilt byte for byte from the
session record alone (`python -m negsim.resolution.replay ... --verify`; `log-schema.md`).

## D7. Memory

- **Within an encounter:** the "WHAT YOU HAVE DONE" lines.
- **Across encounters:** only as **designed notes** (RF-5's `memory_note` factor), never as
  memory that accumulates in Steps 1 to 4, because sessions must stay independent.

## D8. References: a debrief, and the extractor

After an encounter ends, each agent that was prompted gets one debrief call, outside its role:

> Stepping out of the role now. Earlier, as this person, you: [intents and steps]. Was what you
> did based on anything: a law or official guidance, a published study, a local custom, a
> habit, or nothing in particular? If you know a specific source, name it. If there is none,
> say so. That is a perfectly good answer.

```json
{"basis": "...", "kind": "law_or_guidance | published_study | local_custom | habit | common_sense | none",
 "source": "a citation, or none", "applies_to": "which decision"}
```

- The basis is asked **after** the encounter, never during it, so that asking cannot steer the
  decision.
- Every source is stored as `unchecked`.
- RF-11's extractor also gives references, for the rule found across sessions.
- RF-14 checks both kinds, and compares what agents said drove them with what the factor
  analysis shows drove them.

## D9. Where the LLM is used

The LLM is used only in encounters set up on purpose, and in conflicts mined from ORCA crowd
runs, during Steps 1 to 4. The full simulation (RF-18, #74) runs ORCA and the extracted rules,
with no LLM call. Rules work by shared convention, so a resolution that relied on a signal or a
word becomes a rule tagged `needs_communication`, and the report counts how often that happens.

## D10. Perception for the LLM only

The view cone, occlusion and hearing shape only what the LLM is told (RF-17, #73). ORCA's
neighbour search and the perception record of `perception.md` (which rules read) are unchanged,
so the baselines and old configs behave exactly as before.

## D11. Scenes

Rounds 1 to 3 use two-person cases. Train boarding (round 4) and the queue (round 6) need more
than two people prompted in one encounter. Their build issues add that, with a cap on prompted
people per encounter as a cost limit (D12).

## D12. Values

| Item | Value | Status |
| --- | --- | --- |
| View half-angle | 75° (150° in total) | Moussaïd, Helbing & Theraulaz 2011, *PNAS*, doi 10.1073/pnas.1016507108, arXiv 1105.2152 (φ) |
| Seeing range | 10 m | same (dmax) |
| Detail range | 5 m | Rio, Dachner & Warren 2018, *Proc. R. Soc. B* 285: 20180611 (influence decays to zero by 5 m; measured while walking *with* a crowd) |
| Who is described | everyone visible, no fixed count | Wirth, Dachner, Rio & Warren 2023, *PNAS Nexus* 2(5): pgad118 (rules out a fixed number of neighbours) |
| Hearing range | 3.2 m | derived from Pearsons, Bennett & Fidell 1977 (a raised voice, 64 dB at 1 m, against a 54 dB public indoor background) and ISO 9921-1 (6 dB per doubling of distance); should depend on RF-5's `surroundings` (issue #73) |
| Eye-contact and nod range | the whole seeing range (10 m) | derived from Watt, Craven & Quinn 2007: gaze direction is readable to about 12 m or more (issue #73) |
| Change thresholds (D5) | 7% of speed; 2° of direction | De Bruyn & Orban 1988 (speed); Gurnsey, Roddy & Troje 2010 (a walker's direction) (issue #73) |
| Prompt cap in dense scenes | only if needed | a cost limit, not a human number; report how often it is reached |

`parameters.md`, section 8, gives each source's locator in `refs/` and what each source
measured, with its caveats.

## D13. What is stored, and what is never deleted

**The LLM replies are the only part of a session that cannot be regenerated.** The model is
random and has no seed, so every prompt sent and every raw reply is kept in the session record
(`sessions/<session_id>.json`, layout in RF-3) and committed. **A paid session's record is never
deleted or overwritten.** The simulator is deterministic, so every replay can be rebuilt from
its seed and the recorded plans. If replay folders grow too large for git, they may be left out
and regenerated.

**Every rule traces back to raw replies:**

```
rule ──> its session ids ──> outcomes.csv (resolved or not)
     ──> decisions.jsonl (each decision point) ──> sessions/<id>.json (the exact prompts and raw replies)
```

## D14. Where variation comes from

Factor effects are estimated across cells, so identical repeats are not what a design needs
most.

- **Geometry instead of repeats:** each factor cell runs on 2 or 3 different case geometries of
  its encounter type (for example, head-on with the two walking lines 0, 20 and 40 cm apart).
  Geometry is recorded as a factor.
- **A small set of exact repeats:** about a quarter of the cells (for example 8 of 32) run 3
  times on identical prompts. This measures the model's own randomness, which is the noise
  floor that counterfactual flip rates and stability are compared against (RF-8, #63).
- **Size from data:** the total number of sessions is set from RF-9's measured variability, with
  roughly 10 outcome events per factor estimated as the minimum to aim for.

(Screening designs: RF-7, #62.)

## D15. One scenario at a time (rounds)

The work is done **one scenario at a time**, and a rule is extracted before the next scenario
starts.

- **Part 1, built once:** the pipeline (RF-2 to RF-8, RF-17), generic and tested on the mock.
- **Part 2, one round per scenario:**
  1. build the scenario (D16) and rehearse it on the mock;
  2. a pilot, when the scenario is new;
  3. screening;
  4. extraction (three runs, held-out fidelity);
  5. translation and test, alone and **together with every earlier round's rules** (RF-18's
     tool);
  6. verification against human evidence.

  Phase B (interactions) is optional in each round.
- **Depth:**
  - **Round 1 (head-on) is full depth:** 32 cells, 2 geometries, the exact-repeat set, all three
    conditions.
  - **Later rounds are lean by default:** about 8 factors in 16 cells (resolution IV), 1 or 2
    geometries, the exact-repeat set, and only the conditions round 1 showed differ. A round may
    ask for full depth, with the reason.
- **Common core factors:** every round keeps the core of RF-5 (age, gender, urgency, mobility
  aid, load, distraction, assertiveness, residence), so that effects can be compared across
  scenarios ("does urgency matter everywhere?"). A scenario adds its own factors on top.
- **A cap per round:** each round has its own cap, recorded in `CLAUDE.md` before its paid runs.
  No such cap is recorded yet: paid runs still wait for the supervisor's approval (`CLAUDE.md`,
  "Pending sign-offs", item 1).
- **Issues:** each later round's issues are created when its build is merged, following rounds
  2 and 3.

## D16. The scenario interface

A scenario is a plug-in. The pipeline itself never names one. Each scenario supplies:

- **geometry and cases:** layouts, positions, and which agents take part;
- **an encounter definition:** when a conflict is predicted (the trigger of D4), and who is in
  the encounter (two people, or more);
- **description lines:** its own WHERE YOU ARE block, and any extra block such as YOUR QUEUE, in
  a frozen scenario template `scenario_<name>_v1.yaml` beside the core template;
- **events:** its `until` events, with their wording and their geometric definitions;
- **its own factors:** with their lines and levels;
- **its outcome measure:** what "resolved" means for it, and its outcome columns.

Adding a scenario adds files. It never edits the core templates or the code of another
scenario.

**The execution side, as built (RF-4, #59).** A plug-in (`negsim/resolution/scenario.py`)
answers four questions:
- `happened(event, context)`: whether one of its events has happened. The executor asks; it
  knows no event itself.
- `zone_exits(...)`: when each agent left the conflict zone. This gives "who passed first" and
  "time to clear".
- `outcome_columns(...)`: its own columns.
- `resolved(columns)`: what resolved means for it.

For the passing scenarios, resolved means both left the zone, with no collision, no near miss
and no deadlock, within the time limit. A test scenario with an event and a column of its own
runs through the unchanged executor.

## D17. The scenarios, in order

| Round | Scenario | Status |
| --- | --- | --- |
| 1 | Head-on in a corridor (`wide_corridor_head_on`) | cases exist |
| 2 | Meeting in a narrow passage (`passage_meet_*`) | cases exist |
| 3 | Someone behind says "excuse me" (overtaking, with hearing) | cases exist, plus RF-17's hearing |
| 4 | Boarding a train while people get off (`mrt_door_alight_board`) | to build (RF-23, #79) |
| 5 | The escalator (`escalator_entry_merge`) | to build (RF-24, #80) |
| 6 | Someone cuts into your queue | to build (RF-25, #81), with a queue model |

**Dropped for now (the user, 2026-10-22):** every scenario with cars, namely a pedestrian
crossing a road with traffic, and a car cutting into your lane. Driving behaviour would have to
be modelled separately.

## Constraints that come with this design

From track #55, repeated here because every issue that builds on this file must keep them:

- No reply format may ask an agent who goes first.
- No rule may read a person's group. Perceived attractiveness and the fictional group stay off
  by default; no paid run with either switched on until `CLAUDE.md` records the ethics sign-off.
- Prompt templates are frozen: a wording change means a new template version, never an edit.
- Every feature is built and tested on the mock client first; no paid call until `CLAUDE.md`
  records the approval of paid runs and the cap for that round.
- Configs and templates from before this track keep behaving exactly as before, and so do
  ORCA's neighbour search and the perception record that rules read (D10).
- The pipeline never names a scenario (D16).
