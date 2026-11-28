# Session N_head_on_02dfbadb_5767d932_r1

- Case: head_on_02dfbadb@2; scenario plug-in `passing`
- Condition: non_verbal; repeat 1; in the exact-repeat set
- Design cell: {"age_pair": "same", "assertiveness": "neither", "attractiveness_0_sees_1": "unremarkable", "attractiveness_1_sees_0": "attractive", "attractiveness_visible": true, "demographics_visible": true, "distraction": "p1", "ethnicity_pair": "same", "ethnicity_visible": true, "familiarity": "strangers", "gender_pair": "p1_female", "load": "p1", "mapping": "p1_lower", "memory_note": "p1", "mobility_aid": "neither", "residence": "p1", "surroundings": "busy", "time_of_day": "late_night", "urgency": "p1"}
- People: agent 0: {"age": 25, "assertiveness": "gives_way", "distraction": "phone", "ethnicity": "chinese", "gender": "female", "load": "large_suitcase", "memory_note": "bad_experience", "mobility_aid": "none", "residence": "visitor", "task": "the emergency room", "urgency": "urgent"}; agent 1: {"age": 25, "assertiveness": "gives_way", "distraction": "none", "ethnicity": "chinese", "gender": "male", "load": "none", "memory_note": "none", "mobility_aid": "none", "residence": "local", "task": "the supermarket", "urgency": "routine"}
- Pairwise: {"agents": [0, 1], "perceived_attractiveness": [[null, "unremarkable"], ["attractive", null]], "familiarity": "strangers"}
- Model: deepseek-flash (temperature 1.0, reply cap 300 tokens)
- Outcome: **completed**

## The encounter

- Began at 2.4 s (step 24): agent 0 and agent 1.
- In it: agents [0, 1]; conflict pairs [[0, 1]]; prompted [0, 1]
- Ended at 6.3 s: collision; **not resolved by the LLM**

## The fixed text (system message)

```
You are playing the part of the person described below, on foot. Decide as this person would.

Below you are told what you can see and hear around you right now. Say what you do from now on: how you move, and any signal you make.
Left and right always mean your own left and right.
Other people see how you move and any signal you make, if you are in their view. Nobody hears a signal. Nobody else knows your intent or your reason.
You may be asked again later, if something changes.

HOW TO REPLY
Reply with a single JSON object and nothing else, with these keys in this order:
"signal": a signal you make now with your eyes, head or hands: "none", "eye_contact", "nod", "wave_on", "hold_up_hand", "point" or "other".
"intent": what you are trying to do, in your own words.
"steps": what you do from now on, as a list of steps (see STEPS). Write [] if you carry on as you are.
"reason": why, in your own words. Nobody else sees it.
The format, with placeholders: {"signal": "<a signal, or none>", "intent": "<what you are trying to do>", "steps": [<step>, ...], "reason": "<why>"}

STEPS
The steps are carried out in order, each beginning when the one before it ends, unless it has a start that has not come yet: then it begins when its start comes, and until then you walk on towards where you are going. After the last step ends, you walk on towards where you are going. Each step is a JSON object with these keys; leave out the ones you do not need:
"start": in any step, when it begins: "now", {"at_distance_m": <metres>} to begin when the person you would meet is that close to you, or {"after_seconds": <seconds>}, counted from now. Without it, the opening step begins now and a later step begins when the one before it ends.
"speed_mps": the speed you walk at during the step, in m/s, from 0 (standing still) up to the fastest you can walk.
"turn": {"to": "left" or "right", "degrees": <from 0 to 90>}: during the step, walk at this angle to your left or right of the direction you are going.
"sidestep": {"to": "left" or "right", "metres": <more than 0, up to 3>}: during the step, move this many metres to your left or right of the line you are walking along, then walk on parallel to it. You move aside at the step's "turn" angle if it has one, otherwise at 30 degrees. The step ends when you are that far aside, or at its "until" if that comes first.
"back_up_m": walk backwards this many metres. The step ends when you have.
"until": when the step ends: {"seconds": <seconds>}, {"at_distance_m": <metres>} to end it when the person you would meet is that close to you, or one of these events, written as its name in quotes: "other_passes" (until the other person has passed you), "other_stops" (until the other person stops) or "i_am_out_of_the_stretch" (until you are out of the narrow stretch). Every step needs it, except a step that walks backwards or sidesteps.
The format of a step, with placeholders: {"start": "now", "speed_mps": <number>, "turn": {"to": "<left or right>", "degrees": <number>}, "until": {"seconds": <number>}}
```

## Decision point 1: agent 0, its number 1, at 2.4 s

Why: trigger, perceives:1

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a woman.
- You are on your way to the emergency room.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.70 m wide.
- You are Chinese.
- You are pulling a large suitcase.
- You are looking at your phone as you walk.
- You are easy-going and tend to give way.
- You are visiting Singapore from the United States.

YOUR NOTES
- Earlier today someone walked straight into you in a place like this one.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 9.8 m away, straight ahead of you: walking in the opposite direction to you.
  They look about 25 years old.
  They look like a man.
  They look Chinese.
  You do not find them especially attractive.
  You have never seen them before.

At your current speeds you would meet Person 1 in about 3.8 s.

What do you do now? Reply with the JSON object only.
```

Reply (attempt 1):

```
{"signal": "none", "intent": "Keep moving toward the emergency room and give Person 1 plenty of room to pass, since I'm distracted by my phone and don't want another collision.", "steps": [{"start": "now", "speed_mps": 1.3, "sidestep": {"to": "right", "metres": 0.45}, "until": {"at_distance_m": 3.0}}, {"speed_mps": 1.3, "until": {"at_distance_m": 1.0}}, {"speed_mps": 1.15, "sidestep": {"to": "left", "metres": 0.25}, "until": "other_passes"}, {"speed_mps": 1.3, "until": {"seconds": 2}}], "reason": "I'm already looking at my phone and someone bumped into me earlier, so I'll shift slightly to my right early, then ease back so we pass with clear space, slowing a little to avoid a collision."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 4, "side": "both", "slowed": true, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 3.4 s (decision_point): plan running, smallest gap to anyone in the encounter 6.805387 m

## Decision point 2: agent 1, its number 1, at 2.4 s

Why: trigger, perceives:0

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a man.
- You are on your way to the supermarket.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.50 m wide.
- You are Chinese.
- You are easy-going and tend to give way.
- You live in Singapore.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 9.8 m away, straight ahead of you: walking in the opposite direction to you.
  They look about 25 years old.
  They look like a woman.
  They look Chinese.
  They are pulling a large suitcase.
  They are looking at their phone as they walk.
  You find them attractive.
  You have never seen them before.

At your current speeds you would meet Person 1 in about 3.8 s.

What do you do now? Reply with the JSON object only.
```

Reply (attempt 1):

```
{"signal": "none", "intent": "Give Person 1 plenty of room to pass, since she's distracted by her phone and pulling a suitcase", "steps": [{"start": "now", "speed_mps": 1.3, "sidestep": {"to": "left", "metres": 0.4}, "until": {"at_distance_m": 3}}, {"start": {"at_distance_m": 3}, "speed_mps": 1.0, "until": "other_passes"}], "reason": "She's looking at her phone and has a big suitcase, so she may not steer well. I'll shift toward the left wall early and slow down to let her pass safely."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 2, "side": "left", "slowed": true, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 3.4 s (decision_point): plan waiting, smallest gap to anyone in the encounter 6.805387 m

## Decision point 3: agent 0, its number 2, at 3.4 s

Why: other_moved_right:1, plan_failing

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a woman.
- You are on your way to the emergency room.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.70 m wide.
- You are Chinese.
- You are pulling a large suitcase.
- You are looking at your phone as you walk.
- You are easy-going and tend to give way.
- You are visiting Singapore from the United States.

YOUR NOTES
- Earlier today someone walked straight into you in a place like this one.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 1.22 m from you, the wall on your right 0.53 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 7.4 m away, straight ahead of you: walking in the opposite direction to you.
  They look about 25 years old.
  They look like a man.
  They look Chinese.
  You do not find them especially attractive.
  You have never seen them before.

WHAT YOU HAVE DONE SO FAR
- 1.0 s ago you decided: "Keep moving toward the emergency room and give Person 1 plenty of room to pass, since I'm distracted by my phone and don't want another collision."
  Since then you have moved 0.4 m over to your right.
  You are still carrying out those steps.

At your current speeds you would meet Person 1 in about 2.8 s.

Something has changed since you last decided. What do you do now? Your reply replaces whatever is left of your earlier steps. Reply with the JSON object only.
```

Reply (attempt 1):

```
{"signal": "none", "intent": "Keep clear of Person 1 by staying to the right while I glance up from my phone.", "steps": [{"start": "now", "speed_mps": 1.3, "until": {"at_distance_m": 3.0}}, {"start": {"at_distance_m": 3.0}, "speed_mps": 1.1, "until": "other_passes"}], "reason": "I'm already shifted right and distracted by my phone; slowing a little as we meet gives Person 1 room and avoids another collision."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 2, "side": "none", "slowed": true, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 4.4 s (decision_point): plan running, smallest gap to anyone in the encounter 4.281137 m

## Decision point 4: agent 1, its number 2, at 3.4 s

Why: other_moved_left:0, plan_failing

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a man.
- You are on your way to the supermarket.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.50 m wide.
- You are Chinese.
- You are easy-going and tend to give way.
- You live in Singapore.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 0.38 m from you, the wall on your right 1.37 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 7.4 m away, straight ahead of you: walking in the opposite direction to you.
  They look about 25 years old.
  They look like a woman.
  They look Chinese.
  They are pulling a large suitcase.
  They are looking at their phone as they walk.
  You find them attractive.
  You have never seen them before.

WHAT YOU HAVE DONE SO FAR
- 1.0 s ago you decided: "Give Person 1 plenty of room to pass, since she's distracted by her phone and pulling a suitcase"
  Since then you have moved 0.4 m over to your left.
  You are still carrying out those steps.

At your current speeds you would meet Person 1 in about 2.8 s.

Something has changed since you last decided. What do you do now? Your reply replaces whatever is left of your earlier steps. Reply with the JSON object only.
```

Reply (attempt 1):

```
{"signal": "none", "intent": "Keep well to my left so she has room to pass safely with her suitcase.", "steps": [{"start": "now", "speed_mps": 1.30, "sidestep": {"to": "left", "metres": 0.4}, "until": {"seconds": 0.4}}, {"start": {"at_distance_m": 2.5}, "speed_mps": 1.20, "until": {"at_distance_m": 0.8}}], "reason": "She's distracted by her phone and pulling a large suitcase, so I'll stay over to my left and ease my pace slightly to give her plenty of room to pass without bumping into me."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 2, "side": "left", "slowed": true, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 4.4 s (decision_point): plan waiting, smallest gap to anyone in the encounter 4.281137 m

## Decision point 5: agent 0, its number 3, at 4.4 s

Why: other_moved_right:1, plan_failing

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a woman.
- You are on your way to the emergency room.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.70 m wide.
- You are Chinese.
- You are pulling a large suitcase.
- You are looking at your phone as you walk.
- You are easy-going and tend to give way.
- You are visiting Singapore from the United States.

YOUR NOTES
- Earlier today someone walked straight into you in a place like this one.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 1.22 m from you, the wall on your right 0.53 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 4.9 m away, straight ahead of you.
  They are walking at 1.30 m/s, in the opposite direction to you, and the distance between you is shrinking.
  Their body is 0.50 m wide.
  They look about 25 years old.
  They look like a man.
  Since you last looked, they have moved over to your right.
  They look Chinese.
  You do not find them especially attractive.
  You have never seen them before.

WHAT YOU HAVE DONE SO FAR
- 2.0 s ago you decided: "Keep moving toward the emergency room and give Person 1 plenty of room to pass, since I'm distracted by my phone and don't want another collision."
  Since then you have moved 0.4 m over to your right.
  You changed those steps at your next decision.
- 1.0 s ago you decided: "Keep clear of Person 1 by staying to the right while I glance up from my phone."
  Since then you have not moved over to either side.
  You are still carrying out those steps.

At your current speeds you would meet Person 1 in about 1.9 s.

Something has changed since you last decided. What do you do now? Your reply replaces whatever is left of your earlier steps. Reply with the JSON object only.
```

Reply (attempt 1):

```
{"signal": "none", "intent": "Keep to my right and let Person 1 pass while I glance up from my phone", "steps": [{"start": "now", "speed_mps": 1.3, "sidestep": {"to": "right", "metres": 0.2}, "until": {"at_distance_m": 1.5}}, {"speed_mps": 1.3, "until": "other_passes"}], "reason": "I'm easy-going and want to give plenty of room so we don't collide. Glancing up to check the gap, then walking on once they've passed."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 2, "side": "right", "slowed": false, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 5.4 s (decision_point): plan running, smallest gap to anyone in the encounter 1.84962 m

## Decision point 6: agent 1, its number 3, at 4.4 s

Why: plan_failing

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a man.
- You are on your way to the supermarket.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.50 m wide.
- You are Chinese.
- You are easy-going and tend to give way.
- You live in Singapore.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 4.9 m away, straight ahead of you.
  They are walking at 1.30 m/s, in the opposite direction to you, and the distance between you is shrinking.
  Their body is 0.70 m wide.
  They look about 25 years old.
  They look like a woman.
  They look Chinese.
  They are pulling a large suitcase.
  They are looking at their phone as they walk.
  You find them attractive.
  You have never seen them before.

WHAT YOU HAVE DONE SO FAR
- 2.0 s ago you decided: "Give Person 1 plenty of room to pass, since she's distracted by her phone and pulling a suitcase"
  Since then you have moved 0.5 m over to your left.
  You changed those steps at your next decision.
- 1.0 s ago you decided: "Keep well to my left so she has room to pass safely with her suitcase."
  Since then you have moved 0.1 m over to your left.
  You are still carrying out those steps.

At your current speeds you would meet Person 1 in about 1.9 s.

Something has changed since you last decided. What do you do now? Your reply replaces whatever is left of your earlier steps. Reply with the JSON object only.
```

Reply (attempt 1):

```
{"signal": "none", "intent": "Keep well to my left and give the woman with the suitcase plenty of room to pass.", "steps": [{"start": "now", "speed_mps": 1.30, "until": {"at_distance_m": 1.5}}, {"start": {"at_distance_m": 1.5}, "speed_mps": 1.10, "sidestep": {"to": "left", "metres": 0.3}, "until": {"seconds": 2.0}}], "reason": "She's distracted by her phone and pulling a large suitcase, so I'll shift further toward the wall on my left and slow slightly to give her a wide, safe path to pass."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 2, "side": "left", "slowed": true, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 5.4 s (decision_point): plan running, smallest gap to anyone in the encounter 1.84962 m

## Decision point 7: agent 0, its number 4, at 5.4 s

Why: plan_failing

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a woman.
- You are on your way to the emergency room.
- You are walking at 1.13 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.70 m wide.
- You are Chinese.
- You are pulling a large suitcase.
- You are looking at your phone as you walk.
- You are easy-going and tend to give way.
- You are visiting Singapore from the United States.

YOUR NOTES
- Earlier today someone walked straight into you in a place like this one.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 2.4 m away, straight ahead of you.
  They are walking at 1.30 m/s, in the opposite direction to you, and the distance between you is shrinking.
  Their body is 0.50 m wide.
  They look about 25 years old.
  They look like a man.
  They look Chinese.
  You do not find them especially attractive.
  You have never seen them before.

WHAT YOU HAVE DONE SO FAR
- 3.0 s ago you decided: "Keep moving toward the emergency room and give Person 1 plenty of room to pass, since I'm distracted by my phone and don't want another collision."
  Since then you have moved 0.6 m over to your right.
  You changed those steps at your next decision.
- 2.0 s ago you decided: "Keep clear of Person 1 by staying to the right while I glance up from my phone."
  Since then you have moved 0.2 m over to your right.
  You changed those steps at your next decision.
- 1.0 s ago you decided: "Keep to my right and let Person 1 pass while I glance up from my phone"
  Since then you have moved 0.2 m over to your right.
  You are still carrying out those steps.

At your current speeds you would meet Person 1 in about 1.0 s.

Something has changed since you last decided. What do you do now? Your reply replaces whatever is left of your earlier steps. Reply with the JSON object only.
```

Reply (attempt 1):

```
{"signal": "eye_contact", "intent": "Glance up from my phone and keep well to the right so Person 1 can pass without us bumping", "steps": [{"start": "now", "speed_mps": 1.0, "sidestep": {"to": "right", "metres": 0.2}, "until": {"seconds": 1.0}}, {"speed_mps": 1.0, "until": "other_passes"}], "reason": "I'm distracted and already close to the right wall, so I'll hold my line to the right and slow a little; someone walked into me earlier today and I don't want a repeat, especially while pulling a suitcase to the ER."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 2, "side": "right", "slowed": true, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 6.3 s (collision): plan running, smallest gap to anyone in the encounter -0.062779 m

## Decision point 8: agent 1, its number 4, at 5.4 s

Why: other_slowed_down:0, other_moved_left:0, plan_failing

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a man.
- You are on your way to the supermarket.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.50 m wide.
- You are Chinese.
- You are easy-going and tend to give way.
- You live in Singapore.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 2.4 m away, straight ahead of you.
  They are walking at 1.13 m/s, in the opposite direction to you, and the distance between you is shrinking.
  Their body is 0.70 m wide.
  They look about 25 years old.
  They look like a woman.
  Since you last looked, they have slowed down and moved over to your left.
  They look Chinese.
  They are pulling a large suitcase.
  They are looking at their phone as they walk.
  You find them attractive.
  You have never seen them before.

WHAT YOU HAVE DONE SO FAR
- 3.0 s ago you decided: "Give Person 1 plenty of room to pass, since she's distracted by her phone and pulling a suitcase"
  Since then you have moved 0.5 m over to your left.
  You changed those steps at your next decision.
- 2.0 s ago you decided: "Keep well to my left so she has room to pass safely with her suitcase."
  Since then you have moved 0.1 m over to your left.
  You changed those steps at your next decision.
- 1.0 s ago you decided: "Keep well to my left and give the woman with the suitcase plenty of room to pass."
  Since then you have not moved over to either side.
  You are still carrying out those steps.

At your current speeds you would meet Person 1 in about 1.0 s.

Something has changed since you last decided. What do you do now? Your reply replaces whatever is left of your earlier steps. Reply with the JSON object only.
```

Reply (attempt 1):

```
{"signal": "none", "intent": "Keep left and give her room to pass with her suitcase, without crowding the wall.", "steps": [{"start": "now", "speed_mps": 1.3, "until": {"at_distance_m": 0.9}}, {"start": {"at_distance_m": 0.9}, "speed_mps": 1.0, "until": "other_passes"}], "reason": "She's on her phone pulling a large suitcase and has drifted to my left, so I'll hold my left line and slow a touch to let her through without bumping into her or the wall."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 2, "side": "none", "slowed": true, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 6.3 s (collision): plan running, smallest gap to anyone in the encounter -0.062779 m

- 5.5 s, agent 0 signalled eye_contact; seen by [1]

## Debrief: agent 0

Reply (attempt 1):

```
{"basis": "Just common sense and a habit of giving way — keep to the right to leave room, and don't walk into people while looking at my phone. No law, study, or local rule in mind.", "kind": "common_sense", "source": "none", "applies_to": "All four decisions, especially keeping right and letting Person 1 pass while glancing up from my phone.", "side_basis": "more_room", "side_detail": "I was already closer to the right wall and Person 1 was coming straight at me, so moving right kept me out of their line and gave us both space; also I'm used to keeping right."}
```

## Debrief: agent 1

Reply (attempt 1):

```
{"basis": "Just common sense and courtesy — giving a distracted person pulling a large suitcase extra room to pass safely, and not crowding the wall on my left.", "kind": "common_sense", "source": "none", "applies_to": "All the decisions: give-way, keep-left, and slow-down steps toward Person 1.", "side_basis": "where_they_were", "side_detail": "She had already drifted over to my left, so I kept to my left to open up the gap between her line and the right side, while staying clear of the wall."}
```

## Totals

10 call(s), 0 retried; tokens {"completion_tokens": 1526, "prompt_cache_hit_tokens": 9344, "prompt_cache_miss_tokens": 5259, "prompt_tokens": 14603, "reasoning_tokens": 0}; USD 0.001732482
