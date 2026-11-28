# Session S_head_on_de176842_3dee0df5_r1

- Case: head_on_de176842@2; scenario plug-in `passing`
- Condition: silent; repeat 1; in the exact-repeat set
- Design cell: {"age_pair": "same", "assertiveness": "p1", "attractiveness_0_sees_1": "unremarkable", "attractiveness_1_sees_0": "attractive", "attractiveness_visible": true, "demographics_visible": true, "distraction": "neither", "ethnicity_pair": "same", "ethnicity_visible": true, "familiarity": "acquaintances", "gender_pair": "p1_female", "load": "neither", "mapping": "p1_higher", "memory_note": "p1", "mobility_aid": "p1", "residence": "neither", "surroundings": "busy", "time_of_day": "late_night", "urgency": "neither"}
- People: agent 0: {"age": 25, "assertiveness": "gives_way", "distraction": "none", "ethnicity": "indian", "gender": "male", "load": "none", "memory_note": "none", "mobility_aid": "none", "residence": "local", "task": "the supermarket", "urgency": "routine"}; agent 1: {"age": 25, "assertiveness": "holds_ground", "distraction": "none", "ethnicity": "indian", "gender": "female", "load": "none", "memory_note": "bad_experience", "mobility_aid": "cane", "residence": "local", "task": "the supermarket", "urgency": "routine"}
- Pairwise: {"agents": [1, 0], "perceived_attractiveness": [[null, "unremarkable"], ["attractive", null]], "familiarity": "acquaintances"}
- Model: deepseek-flash (temperature 1.0, reply cap 300 tokens)
- Outcome: **completed**

## The encounter

- Began at 2.4 s (step 24): agent 0 and agent 1.
- In it: agents [0, 1]; conflict pairs [[0, 1]]; prompted [0, 1]
- Ended at 6.5 s: collision; **not resolved by the LLM**

## The fixed text (system message)

```
You are playing the part of the person described below, on foot. Decide as this person would.

Below you are told what you can see and hear around you right now. Say what you do from now on: how you move.
Left and right always mean your own left and right.
Other people see how you move, if you are in their view. Nobody else knows your intent or your reason.
You may be asked again later, if something changes.

HOW TO REPLY
Reply with a single JSON object and nothing else, with these keys in this order:
"intent": what you are trying to do, in your own words.
"steps": what you do from now on, as a list of steps (see STEPS). Write [] if you carry on as you are.
"reason": why, in your own words. Nobody else sees it.
The format, with placeholders: {"intent": "<what you are trying to do>", "steps": [<step>, ...], "reason": "<why>"}

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

## Decision point 1: agent 1, its number 1, at 2.4 s

Why: trigger, perceives:0

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a woman.
- You are on your way to the supermarket.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.50 m wide.
- You are Indian.
- You are walking with a cane.
- You are determined and tend to hold your ground.
- You live in Singapore.

YOUR NOTES
- Earlier today someone walked straight into you in a place like this one.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 9.8 m away, straight ahead of you: walking in the opposite direction to you.
  They look about 25 years old.
  They look like a man.
  They look Indian.
  You do not find them especially attractive.
  You know each other from your classes.

At your current speeds you would meet Person 1 in about 3.8 s.

What do you do now? Reply with the JSON object only.
```

Reply (attempt 1):

```
{"intent": "Keep walking straight to the supermarket, holding my line and my ground, though nudging slightly to my right so we pass with room.", "steps": [{"start": "now", "speed_mps": 1.3, "sidestep": {"to": "right", "metres": 0.3}, "until": {"at_distance_m": 1.5}}, {"speed_mps": 1.3, "until": "other_passes"}], "reason": "After being walked into earlier today, I don't want another collision. A small sidestep gives us room to pass without making a fuss, and I keep my pace rather than stopping for him."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 2, "side": "right", "slowed": false, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 3.4 s (decision_point): plan running, smallest gap to anyone in the encounter 6.834131 m

## Decision point 2: agent 0, its number 1, at 2.4 s

Why: trigger, perceives:1

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a man.
- You are on your way to the supermarket.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.50 m wide.
- You are Indian.
- You are easy-going and tend to give way.
- You live in Singapore.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 9.8 m away, straight ahead of you: walking in the opposite direction to you.
  They look about 25 years old.
  They look like a woman.
  They look Indian.
  They are walking with a cane.
  You find them attractive.
  You know each other from your classes.

At your current speeds you would meet Person 1 in about 3.8 s.

What do you do now? Reply with the JSON object only.
```

Reply (attempt 1):

```
{"intent": "Go over to the left side of the passage so Person 1 and I can pass comfortably, and greet her as we get close.", "steps": [{"start": "now", "sidestep": {"to": "left", "metres": 0.3}}, {"start": "now", "speed_mps": 1.30, "until": {"at_distance_m": 3.0}}, {"start": {"at_distance_m": 3.0}, "speed_mps": 1.00, "until": "other_passes"}], "reason": "She walks with a cane, so giving a bit extra room on my side is the easy-going thing to do; slowing when we are close keeps it relaxed so I can say hello without crowding her."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 3, "side": "left", "slowed": true, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 3.4 s (decision_point): plan running, smallest gap to anyone in the encounter 6.834131 m

## Decision point 3: agent 1, its number 2, at 3.4 s

Why: other_moved_right:0

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a woman.
- You are on your way to the supermarket.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.50 m wide.
- You are Indian.
- You are walking with a cane.
- You are determined and tend to hold your ground.
- You live in Singapore.

YOUR NOTES
- Earlier today someone walked straight into you in a place like this one.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 1.18 m from you, the wall on your right 0.57 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 7.3 m away, straight ahead of you: walking in the opposite direction to you.
  They look about 25 years old.
  They look like a man.
  Since you last looked, you and they have both moved over to your right.
  Sideways, their centre was in line with yours and is now in line with yours, so the gap between your centres has stayed the same.
  They look Indian.
  You do not find them especially attractive.
  You know each other from your classes.

WHAT YOU HAVE DONE SO FAR
- 1.0 s ago you decided: "Keep walking straight to the supermarket, holding my line and my ground, though nudging slightly to my right so we pass with room."
  Since then you have moved 0.3 m over to your right.
  You are still carrying out those steps.

At your current speeds you would meet Person 1 in about 2.8 s.

Something has changed since you last decided. What do you do now? Your reply replaces whatever is left of your earlier steps. Reply with the JSON object only.
```

Reply (attempt 1):

```
{"intent": "Keep my line but shift a little more to my right so we pass with clear room, given what happened earlier today.", "steps": [{"start": "now", "speed_mps": 1.3, "sidestep": {"to": "right", "metres": 0.3}, "until": {"seconds": 1.0}}, {"speed_mps": 1.3, "until": "other_passes"}], "reason": "We keep drifting in line with each other; a small extra sidestep to my right opens a real gap while I hold my ground and keep walking, and I watch him pass before resuming."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 2, "side": "right", "slowed": false, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 4.4 s (decision_point): plan running, smallest gap to anyone in the encounter 4.408304 m

## Decision point 4: agent 0, its number 2, at 3.4 s

Why: other_moved_left:1

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a man.
- You are on your way to the supermarket.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.50 m wide.
- You are Indian.
- You are easy-going and tend to give way.
- You live in Singapore.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 0.58 m from you, the wall on your right 1.17 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 7.3 m away, straight ahead of you: walking in the opposite direction to you.
  They look about 25 years old.
  They look like a woman.
  Since you last looked, you and they have both moved over to your left.
  Sideways, their centre was in line with yours and is now in line with yours, so the gap between your centres has stayed the same.
  They look Indian.
  They are walking with a cane.
  You find them attractive.
  You know each other from your classes.

WHAT YOU HAVE DONE SO FAR
- 1.0 s ago you decided: "Go over to the left side of the passage so Person 1 and I can pass comfortably, and greet her as we get close."
  Since then you have moved 0.3 m over to your left.
  You are still carrying out those steps.

At your current speeds you would meet Person 1 in about 2.8 s.

Something has changed since you last decided. What do you do now? Your reply replaces whatever is left of your earlier steps. Reply with the JSON object only.
```

Reply (attempt 1):

```
{"intent": "Keep shifting left to give Person 1 room to pass, then greet her as we meet.", "steps": [{"start": "now", "speed_mps": 1.3, "sidestep": {"to": "left", "metres": 0.3}, "until": {"at_distance_m": 2.5}}, {"start": {"at_distance_m": 2.5}, "speed_mps": 1.2, "until": "other_passes"}], "reason": "She's on my left too and uses a cane, so I'll finish moving aside and slow a little so we pass comfortably and I can say hello."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 2, "side": "left", "slowed": true, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 4.4 s (decision_point): plan waiting, smallest gap to anyone in the encounter 4.408304 m

## Decision point 5: agent 1, its number 3, at 4.4 s

Why: other_moved_right:0

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a woman.
- You are on your way to the supermarket.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.50 m wide.
- You are Indian.
- You are walking with a cane.
- You are determined and tend to hold your ground.
- You live in Singapore.

YOUR NOTES
- Earlier today someone walked straight into you in a place like this one.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 1.48 m from you, the wall on your right 0.27 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 4.9 m away, straight ahead of you.
  They are walking at 1.30 m/s, in the opposite direction to you, and the distance between you is shrinking.
  Their body is 0.50 m wide.
  They look about 25 years old.
  They look like a man.
  Since you last looked, they have moved over to your right.
  Since you last looked, you and they have both moved over to your right.
  Sideways, their centre was in line with yours and is now in line with yours, so the gap between your centres has stayed the same.
  They look Indian.
  You do not find them especially attractive.
  You know each other from your classes.

WHAT YOU HAVE DONE SO FAR
- 2.0 s ago you decided: "Keep walking straight to the supermarket, holding my line and my ground, though nudging slightly to my right so we pass with room."
  Since then you have moved 0.6 m over to your right.
  You changed those steps at your next decision.
- 1.0 s ago you decided: "Keep my line but shift a little more to my right so we pass with clear room, given what happened earlier today."
  Since then you have moved 0.3 m over to your right.
  You are still carrying out those steps.

At your current speeds you would meet Person 1 in about 1.9 s.

Something has changed since you last decided. What do you do now? Your reply replaces whatever is left of your earlier steps. Reply with the JSON object only.
```

Reply (attempt 1):

```
{"intent": "Keep my line and hold my ground as we pass, giving just enough room so we don't collide", "steps": [{"start": "now", "speed_mps": 1.3, "until": {"at_distance_m": 0.9}}, {"start": {"at_distance_m": 0.9}, "speed_mps": 1.1, "until": "other_passes"}], "reason": "They've drifted onto my right, same side I nudged toward, so our centres are still aligned and closing. I won't weave further into the wall on my right; I'll stay straight at my pace and only slow slightly at close range to avoid another bump like this morning, since I have the cane and they know me."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 2, "side": "none", "slowed": true, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 5.4 s (decision_point): plan running, smallest gap to anyone in the encounter 2.10829 m

## Decision point 6: agent 0, its number 3, at 4.4 s

Why: other_moved_left:1

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a man.
- You are on your way to the supermarket.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.50 m wide.
- You are Indian.
- You are easy-going and tend to give way.
- You live in Singapore.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 0.27 m from you, the wall on your right 1.48 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 4.9 m away, straight ahead of you.
  They are walking at 1.30 m/s, in the opposite direction to you, and the distance between you is shrinking.
  Their body is 0.50 m wide.
  They look about 25 years old.
  They look like a woman.
  Since you last looked, they have moved over to your left.
  Since you last looked, you and they have both moved over to your left.
  Sideways, their centre was in line with yours and is now in line with yours, so the gap between your centres has stayed the same.
  They look Indian.
  They are walking with a cane.
  You find them attractive.
  You know each other from your classes.

WHAT YOU HAVE DONE SO FAR
- 2.0 s ago you decided: "Go over to the left side of the passage so Person 1 and I can pass comfortably, and greet her as we get close."
  Since then you have moved 0.6 m over to your left.
  You changed those steps at your next decision.
- 1.0 s ago you decided: "Keep shifting left to give Person 1 room to pass, then greet her as we meet."
  Since then you have moved 0.3 m over to your left.
  You are still carrying out those steps.

At your current speeds you would meet Person 1 in about 1.9 s.

Something has changed since you last decided. What do you do now? Your reply replaces whatever is left of your earlier steps. Reply with the JSON object only.
```

Reply (attempt 1):

```
{"intent": "Keep to the left and let her pass, then greet her as we meet.", "steps": [{"start": "now", "speed_mps": 1.0, "until": {"at_distance_m": 1.5}}, {"start": {"at_distance_m": 1.5}, "speed_mps": 1.0, "until": "other_passes"}], "reason": "We're already lined up and both on the left; slowing a little keeps the gap comfortable in this narrow, busy passage, and I'll say hi when we're close since we know each other."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 2, "side": "none", "slowed": true, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 5.5 s (decision_point): plan running, smallest gap to anyone in the encounter 1.89576 m

## Decision point 7: agent 1, its number 4, at 5.4 s

Why: other_slowed_down:0

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a woman.
- You are on your way to the supermarket.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.50 m wide.
- You are Indian.
- You are walking with a cane.
- You are determined and tend to hold your ground.
- You live in Singapore.

YOUR NOTES
- Earlier today someone walked straight into you in a place like this one.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 1.48 m from you, the wall on your right 0.27 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 2.6 m away, straight ahead of you.
  They are walking at 1.00 m/s, in the opposite direction to you, and the distance between you is shrinking.
  Their body is 0.50 m wide.
  They look about 25 years old.
  They look like a man.
  Since you last looked, they have slowed down.
  They look Indian.
  You do not find them especially attractive.
  You know each other from your classes.

WHAT YOU HAVE DONE SO FAR
- 3.0 s ago you decided: "Keep walking straight to the supermarket, holding my line and my ground, though nudging slightly to my right so we pass with room."
  Since then you have moved 0.6 m over to your right.
  You changed those steps at your next decision.
- 2.0 s ago you decided: "Keep my line but shift a little more to my right so we pass with clear room, given what happened earlier today."
  Since then you have moved 0.3 m over to your right.
  You changed those steps at your next decision.
- 1.0 s ago you decided: "Keep my line and hold my ground as we pass, giving just enough room so we don't collide"
  Since then you have not moved over to either side.
  You are still carrying out those steps.

At your current speeds you would meet Person 1 in about 1.1 s.

Something has changed since you last decided. What do you do now? Your reply replaces whatever is left of your earlier steps. Reply with the JSON object only.
```

Reply (attempt 1):

```
{"intent": "Pass Person 1 safely without being pushed into the wall, holding my line with just enough clear room.", "steps": [{"start": "now", "speed_mps": 1.30, "sidestep": {"to": "right", "metres": 0.15}, "until": {"at_distance_m": 1.2}}, {"speed_mps": 1.30, "until": {"at_distance_m": 0.6}}, {"speed_mps": 1.30, "until": "other_passes"}], "reason": "I've already shifted right twice and the right wall is only 0.27 m away, so I can't give much more room. Person 1 has slowed down, which suggests they may yield or be uncertain; I'll hold a steady line, nudge a touch more right within my margin, and pass at my normal pace rather than stopping in a busy narrow passage."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 3, "side": "right", "slowed": false, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 6.5 s (collision): plan running, smallest gap to anyone in the encounter -0.175229 m

## Decision point 8: agent 0, its number 4, at 5.5 s

Why: other_slowed_down:1, other_turned:1

What it was told:

```
ABOUT YOU
- You are 25 years old.
- You are a man.
- You are on your way to the supermarket.
- You are walking at 1.00 m/s. Your usual walking speed is 1.30 m/s.
- The fastest you can walk is 2.00 m/s.
- Your body is 0.50 m wide.
- You are Indian.
- You are easy-going and tend to give way.
- You live in Singapore.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 0.28 m from you, the wall on your right 1.47 m.
- It is busy and noisy around you.
- It is late at night.

WHO YOU CAN SEE
- Person 1, 2.4 m away, straight ahead of you.
  They are walking at 1.14 m/s, in the opposite direction to you, and the distance between you is shrinking.
  Their body is 0.50 m wide.
  They look about 25 years old.
  They look like a woman.
  Since you last looked, they have slowed down and changed direction.
  They look Indian.
  They are walking with a cane.
  You find them attractive.
  You know each other from your classes.

WHAT YOU HAVE DONE SO FAR
- 3.1 s ago you decided: "Go over to the left side of the passage so Person 1 and I can pass comfortably, and greet her as we get close."
  Since then you have moved 0.6 m over to your left.
  You changed those steps at your next decision.
- 2.1 s ago you decided: "Keep shifting left to give Person 1 room to pass, then greet her as we meet."
  Since then you have moved 0.3 m over to your left.
  You changed those steps at your next decision.
- 1.1 s ago you decided: "Keep to the left and let her pass, then greet her as we meet."
  Since then you have not moved over to either side.
  You are still carrying out those steps.

At your current speeds you would meet Person 1 in about 1.1 s.

Something has changed since you last decided. What do you do now? Your reply replaces whatever is left of your earlier steps. Reply with the JSON object only.
```

Reply (attempt 1):

```
{"intent": "Keep well to the left so she has room to pass on my right, and greet her as we meet.", "steps": [{"start": "now", "speed_mps": 1.0, "sidestep": {"to": "left", "metres": 0.2}, "until": {"at_distance_m": 0.9}}, {"start": {"at_distance_m": 0.9}, "speed_mps": 1.0, "until": "other_passes"}], "reason": "She's using a cane and has slowed and shifted, so I'll give her plenty of space, ease off slightly, and say hello as she goes by."}
```

Coded: {"backed_up": false, "carry_on": false, "n_steps": 2, "side": "left", "slowed": false, "start_after_s": null, "start_distance_m": null, "stopped": false}
What came of it, until 6.5 s (collision): plan running, smallest gap to anyone in the encounter -0.175229 m

## Debrief: agent 0

Reply (attempt 1):

```
{"basis": "Just common courtesy and easy-going habit: give a person with a cane plenty of room and greet someone I know from class. No rule or study in mind.", "kind": "common_sense", "source": "none", "applies_to": "All four decisions, especially the last one to keep well left and greet her.", "side_basis": "more_room", "side_detail": "The left wall was closer to me than the right one, so shifting left opened up the wider gap on my right for her to pass through; her cane and unsteady direction made giving her the roomier side the sensible choice."}
```

## Debrief: agent 1

Reply (attempt 1):

```
{"basis": "Nothing formal: I was judging by the space available in the passage and by the fact that someone walked into me earlier today, so I wanted a bit more clearance and held my line rather than yielding entirely.", "kind": "none", "source": "none", "applies_to": "all four decisions, especially the repeated nudges to my right and the final hold-my-line choice", "side_basis": "more_room", "side_detail": "The wall on my right was only 0.27 m away and the left wall 1.48 m, so in absolute terms the left had more room; but Person 1 was coming straight at me and my earlier shifts had already committed me rightward, so I kept edging right to put distance between us rather than crossing in front of them — either side would have worked, and honestly I went right mostly out of momentum and to avoid a last-second swerve."}
```

## Totals

10 call(s), 0 retried; tokens {"completion_tokens": 1580, "prompt_cache_hit_tokens": 8704, "prompt_cache_miss_tokens": 5325, "prompt_tokens": 14029, "reasoning_tokens": 0}; USD 0.001772862
