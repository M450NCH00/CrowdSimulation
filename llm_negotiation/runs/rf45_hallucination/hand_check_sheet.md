# RF-45 hand check sheet (issue #134)

Each entry: what the prompt showed (the view's fields), the reply, and the coder's flags. Judgements are in `hand_check_judgements.json`.

## Random sample (150)

### rf39_round1_head_on_sidestep_reprompt/I_head_on_02dfbadb_0f57f8a5_r2/dp2 (independent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **unreadable:** until_at_distance_not_positive: steps[1].until: 0.0
- **flags:** 5:unreadable (until_at_distance_not_positive: steps[1].until: 0.0)

### rf39_round1_head_on_sidestep_reprompt/I_head_on_02dfbadb_231c8154_r2/dp2 (independent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Get past the person coming toward me without trouble, since I'm heading to the emergency room.
- **reason:** The passage is narrow and someone I know is coming the other way. I'm easy-going, so I'll shift a little to the right to leave room, then keep walking straight.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/I_head_on_02dfbadb_5841fc4a_x10cdea10/dp1 (independent, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Carry on toward the supermarket, easing slightly to the left so we can pass each other comfortably.
- **reason:** The passage is narrow but there is room for both of us. Shifting a little to my left gives Person 1 space to pass on the other side, and keeping my normal pace avoids any awkwardness.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/I_head_on_02dfbadb_8ea28db3_r3/dp2 (independent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking to the supermarket, giving Person 1 room to pass on the side, since they're on their phone with a cane.
- **reason:** They're distracted on their phone and using a cane, so I'll shift a little to my left within the passage to give them a clear line and avoid a collision.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/I_head_on_02dfbadb_9950986f_r3/dp2 (independent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep moving toward the emergency room without losing much time, and keep an eye on my phone while passing Person 1.
- **reason:** I'm in a hurry to the ER, but the passage is narrow and I'm pulling a suitcase, so I'll give a small sidestep to avoid a collision with someone from my classes and keep going.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/I_head_on_de176842_68f09b97_r1/dp1 (independent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking steadily to the supermarket, holding my line with my cane and suitcase.
- **reason:** I am determined and hold my ground, but the passage is narrow and I am pulling a big suitcase. Easing slightly to the right near the last moment lets the other walker pass without me stopping, keeping me on my way.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/I_head_on_de176842_9b752a36_r1/dp1 (independent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Give the older woman plenty of room to pass, since she's pulling a suitcase in a narrow passage.
- **reason:** She's elderly and hauling a large suitcase, so stepping aside early makes it easier for both of us.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/I_head_on_de176842_b59c2831_r3/dp1 (independent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits ['They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking to the supermarket and give way to Person 1 since she's on her phone.
- **reason:** She's distracted by her phone and we're in a narrow passage; stepping slightly aside lets her pass without a bump, and I'm easy-going about giving way.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/I_head_on_de176842_cb859069_r2/dp2 (independent, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep heading toward the emergency room, but ease to my left a bit and slow down so the young man and I pass safely.
- **reason:** I'm in a hurry to the ER, but I'm 70 with a cane and someone bumped into me earlier today. Giving a little room to my left and slowing slightly should keep us from colliding, then I can pick my pace back up.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_1868bff4_r2/dp2 (non_verbal, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep my line, acknowledge Person 1, and get past without a collision so I can reach the emergency room
- **reason:** I'm in a hurry and pulling a suitcase, so I hold my line rather than weaving wildly, but I make brief eye contact and shift slightly right to avoid another head-on bump.
- **signal:** eye_contact; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_3dee0df5_r1/dp5 (non_verbal, agent 0, decision 3)
- seen: +6° (+ left), 4.8 m, walking, signal nod, changes ['moved_right', 'turned'], age 25, width 0.5, traits ['They are walking with a cane.']
- history: 2.0 s ago "greet her as we pass and make room so she has an easy line with her cane", signal nod, message "", sideways -0.60 m (+ left)
- history: 1.0 s ago "Greet her warmly as we pass and keep well to my right so her cane has a clear line", signal eye_contact, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.37 m from you, the wall on your right 0.38 m.
- **intent:** Greet her warmly and keep well to my right so her cane has a clear line as we pass
- **reason:** She's a friend from class and she's using a cane, so I'll give her plenty of room on her side and slow a touch, greeting her as we pass.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_51dfba80_r3/dp1 (non_verbal, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **unreadable:** unknown_start: steps[3].start: got 'other_passes'
- **flags:** 5:unreadable (unknown_start: steps[3].start: got 'other_passes')

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_55c9ae40_r4/dp3 (non_verbal, agent 0, decision 2)
- seen: -4° (+ left), 7.4 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep going to the emergency room without fuss, but not get walked into again.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep my line to the emergency room but make sure she sees me so she doesn't walk into me like the last one
- **reason:** I'm in a hurry to the emergency room and won't be shoved aside, but I don't want a repeat of this morning, so I look her in the eye early and shift slightly to my left to give us both room while holding my ground.
- **signal:** eye_contact; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_5767d932_r3/dp6 (non_verbal, agent 1, decision 3)
- seen: +2° (+ left), 5.0 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 2.0 s ago "Give the woman with the suitcase plenty of room as we pass, since she's on her phone and won't be watching where she's going", signal none, message "", sideways -0.72 m (+ left)
- history: 1.0 s ago "Keep to the right and give the woman with the suitcase plenty of room as she passes, without startling her", signal none, message "", sideways -0.32 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Keep well to the right and pass the woman quietly, giving her room since she's on her phone with a suitcase
- **reason:** She's distracted on her phone and pulling a suitcase, so I'll stay close to the right wall, slow a touch, and let her pass without crowding or startling her.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_6ab9c72e_r4/dp9 (non_verbal, agent 0, decision 5)
- seen: -4° (+ left), 1.4 m, walking, signal hold_up_hand, changes ['slowed_down', 'moved_right'], age 25, width 0.5, traits []
- history: 4.0 s ago "Acknowledge Person 1 and give way so we can pass without trouble, then keep heading to the emergency room.", signal nod, message "", sideways -0.62 m (+ left)
- history: 3.0 s ago "Keep giving way to my right, wave back at Person 1, and pass her smoothly on my way to the emergency room", signal wave_on, message "", sideways -0.23 m (+ left)
- history: 2.0 s ago "Keep passing smoothly on my right while acknowledging her, and continue to the emergency room", signal eye_contact, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Pass Person 1 smoothly on my right with a friendly nod, then keep heading to the emergency room", signal nod, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Steady my course to the right of the passage and pass Person 1 smoothly, letting her take the wider side
- **reason:** She has already moved over to my right and raised a hand, so we have both given way. Easing my pace a touch and keeping to the right lets us pass without a bump, and then I can carry on to the hospital.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_74cb78c1_x10cdea10/dp3 (non_verbal, agent 0, decision 2)
- seen: -4° (+ left), 7.3 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the supermarket and give the oncoming man room to pass.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep walking and shift slightly to my right to give the oncoming man room to pass
- **reason:** The passage is narrow, so a small sidestep to the right keeps things easy and lets him pass comfortably.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_800a3b04_r2/dp3 (non_verbal, agent 0, decision 2)
- seen: -2° (+ left), 7.6 m, walking, signal none, changes ['slowed_down', 'moved_right', 'turned'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep heading to the emergency room, easing aside to let the woman pass since the passage is narrow.", signal none, message "", sideways -0.50 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.27 m from you, the wall on your right 0.48 m.
- **intent:** Keep easing to the right to let the woman pass, without drawing attention
- **reason:** The passage is narrow and I am already moving right, so a little more to the right keeps me clear of her while I keep heading to the emergency room.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_800a3b04_r4/dp10 (non_verbal, agent 1, decision 5)
- seen: -4° (+ left), 1.5 m, walking, signal none, changes ['slowed_down'], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 4.0 s ago "Give the elderly man with the suitcase plenty of room and keep walking to the supermarket.", signal none, message "", sideways +0.53 m (+ left)
- history: 3.0 s ago "Keep well clear of the elderly man and let him pass safely", signal none, message "", sideways +0.03 m (+ left)
- history: 2.0 s ago "Give the elderly man plenty of room and keep out of his way as he passes with his suitcase", signal none, message "", sideways +0.02 m (+ left)
- history: 1.0 s ago "Keep clear of the elderly man and his suitcase and let him pass on my right", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Let the elderly man pass on my right, keeping well clear of him and his suitcase
- **reason:** He is distracted by his phone and pulling a suitcase, so I will edge further left toward the wall to give him room and avoid a collision.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_9b752a36_r3/dp1 (non_verbal, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Give the elderly woman with the suitcase plenty of room to pass
- **reason:** She is elderly and pulling a large suitcase, and the passage is narrow. I am easy-going, so I slow a little and shift to my right to leave her a clear path, then carry on to the supermarket.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_b1d97a31_r1/dp6 (non_verbal, agent 1, decision 3)
- seen: -4° (+ left), 5.0 m, walking, signal none, changes ['slowed_down', 'moved_right'], age 70, width 0.5, traits []
- history: 2.0 s ago "Give the elderly man plenty of room to pass, keeping to my side of the passage.", signal none, message "", sideways -0.35 m (+ left)
- history: 1.0 s ago "Keep to my right to give the elderly man plenty of room to pass", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.12 m from you, the wall on your right 0.63 m.
- **intent:** Keep well to my right so the elderly man has plenty of room to pass
- **reason:** He is elderly and we are in a narrow passage; slowing a little and staying on my right gives him an easy, comfortable pass, and it matches my easy-going habit of giving way.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_b7fe7ead_r3/dp3 (non_verbal, agent 0, decision 2)
- seen: -4° (+ left), 7.5 m, walking, signal eye_contact, changes ['slowed_down', 'moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the emergency room, holding my line since there's plenty of room for both of us to pass.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Acknowledge Person 1 and keep my line so we pass each other cleanly
- **reason:** I know her from class and she has noticed me, so a brief nod is polite. I hold my line at first, but last time someone walked straight into me, and this passage is narrow. A small sidestep right keeps us from colliding without losing much time toward the emergency room.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_b7fe7ead_r3/dp8 (non_verbal, agent 1, decision 4)
- seen: -10° (+ left), 3.0 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- history: 3.0 s ago "Greet him warmly and give way a little so we can pass easily", signal eye_contact, message "", sideways +0.35 m (+ left)
- history: 2.0 s ago "Greet him warmly from a little distance and keep giving him room to pass", signal wave_on, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "return his greeting warmly and keep to my left so he has room to pass", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.42 m from you, the wall on your right 1.33 m.
- **intent:** Greet him warmly and shift a little more to my left so we can pass comfortably
- **reason:** He nodded back and I know him from class, so a friendly nod is right. I'm easy-going and happy to give way, and a bit more room on my left lets us both pass without bumping.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_cb859069_r3/dp2 (non_verbal, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking toward the emergency room and give Person 1 plenty of room to pass.
- **reason:** I am easy-going and, after being walked into earlier today, I want to clear a wide berth and slow a little so we pass safely without bumping.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_ce2a06ef_r1/dp1 (non_verbal, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Acknowledge the young man from my classes and pass him without a bump, keeping to my side of the passage
- **reason:** Someone walked straight into me earlier today, so with my cane and suitcase I want to keep well to my left and slow a little, giving him room to pass safely.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_f79677df_r3/dp2 (non_verbal, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Greet Person 1 as a familiar face and carry on toward the supermarket, keeping my line.
- **reason:** I know her from classes, so a nod is polite and friendly. I keep my pace and only ease slightly to my left so we can pass in the narrow passage, since I am steady on my feet with my cane and do not need to stop.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_02604456_r2/dp9 (non_verbal, agent 0, decision 5)
- seen: -3° (+ left), 1.7 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- history: 4.0 s ago "Greet my classmate warmly and give her room to pass with her suitcase", signal eye_contact, message "", sideways +0.63 m (+ left)
- history: 3.0 s ago "Greet my classmate warmly and keep giving her room to pass with her suitcase", signal nod, message "", sideways +0.22 m (+ left)
- history: 2.0 s ago "Greet her warmly and stay well to my left so she can pass with her suitcase", signal nod, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Greet her warmly and stay well to my left so she can pass with her suitcase", signal eye_contact, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Greet my classmate warmly and keep well to my left so she can pass with her suitcase
- **reason:** She is a classmate I find attractive and she nodded at me; I'm easy-going and want to give her and her suitcase plenty of room, so I stay left and slow slightly until she passes, then carry on to the supermarket.
- **signal:** eye_contact; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_0f57f8a5_r2/dp5 (non_verbal, agent 1, decision 3)
- seen: -5° (+ left), 4.7 m, walking, signal nod, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 2.0 s ago "Keep walking toward the supermarket and give Person 1 room to pass, since they are distracted by their phone and pulling a suitcase.", signal none, message "", sideways +0.40 m (+ left)
- history: 1.0 s ago "Keep walking to the supermarket and give Person 1 room to pass, since they are distracted by their phone and pulling a suitcase.", signal eye_contact, message "", sideways +0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.47 m from you, the wall on your right 1.28 m.
- **intent:** Acknowledge Person 1 and keep well to the left so they can pass with their suitcase
- **reason:** They nodded at me while looking at their phone and pulling a suitcase, so I nod back and stay to the left to give them room to get past safely.
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_1caa9a84_r1/dp9 (non_verbal, agent 0, decision 5)
- seen: +3° (+ left), 2.0 m, walking, signal none, changes ['slowed_down'], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 4.0 s ago "Keep walking to the supermarket while giving the man with the cane and suitcase plenty of room", signal none, message "", sideways -0.62 m (+ left)
- history: 2.0 s ago "Keep giving the man with the cane and suitcase room, moving further to my right wall so we pass safely", signal none, message "", sideways -0.17 m (+ left)
- history: 1.0 s ago "Keep well to my right so the man with the cane and suitcase can pass safely", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Let the man with the cane and suitcase pass safely by keeping to my right and slowing down
- **reason:** He has slowed and is looking at his phone while using a cane and pulling a suitcase, so he needs room; I will ease right against the wall, slow until he is past, then carry on to the supermarket.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_2ec958bb_r2/dp5 (non_verbal, agent 0, decision 3)
- seen: -7° (+ left), 5.0 m, walking, signal none, changes [], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 2.0 s ago "Keep walking to the supermarket and give the elderly lady plenty of room since she's on her phone", signal none, message "", sideways +0.60 m (+ left)
- history: 1.0 s ago "Give the elderly lady on her phone plenty of room by moving a bit further left and slowing down slightly.", signal none, message "", sideways +0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.27 m from you, the wall on your right 1.48 m.
- **intent:** Keep well clear of the elderly woman on her phone by easing further left and slowing a little
- **reason:** She is engrossed in her phone and may drift, so giving her extra space on my left while slowing slightly keeps us both comfortable in the narrow passage.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_2ec958bb_r4/dp3 (non_verbal, agent 1, decision 2)
- seen: +1° (+ left), 3.0 m, walking, signal none, changes ['slowed_down', 'turned'], age 25, width 0.5, traits []
- history: 2.6 s ago "Keep walking toward the supermarket and hold my line, watching the approaching person out of the corner of my eye", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Hold my line and keep an eye on the approaching person so they do not walk into me again
- **reason:** They are drifting into my path, and someone already barged into me today. I will look at them to make my presence clear, but I will give a little room to my right so we do not collide.
- **signal:** eye_contact; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_3dee0df5_r1/dp3 (non_verbal, agent 0, decision 2)
- seen: +4° (+ left), 7.4 m, walking, signal nod, changes [], age 25, width 0.5, traits ['They are walking with a cane.']
- history: 1.0 s ago "Say hello to my classmate and give her plenty of room to pass with her cane", signal eye_contact, message "", sideways -0.50 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.37 m from you, the wall on your right 0.38 m.
- **intent:** Greet my classmate warmly and give her plenty of room to pass with her cane
- **reason:** She nodded first, so I nod back and stay hugged to the right wall so her cane has a clear path, slowing a little as she passes and then carrying on to the supermarket.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_51dfba80_r1/dp6 (non_verbal, agent 1, decision 3)
- seen: -7° (+ left), 5.2 m, walking, signal nod, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 2.0 s ago "Greet her warmly and make room to pass so she doesn't have to worry while looking at her phone.", signal wave_on, message "", sideways +0.62 m (+ left)
- history: 1.0 s ago "Greet her warmly and give her plenty of room to pass while she's on her phone", signal nod, message "", sideways +0.22 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Keep well to my left and slow a little so the older woman with her suitcase and phone can pass comfortably.
- **reason:** She is elderly, absorbed in her phone and pulling a big suitcase, so I give her as much clear space as this narrow passage allows and ease off so there is no rush or bump.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_55c9ae40_r2/dp4 (non_verbal, agent 1, decision 2)
- seen: -3° (+ left), 7.4 m, walking, signal none, changes [], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "keep walking and give the elderly man plenty of room so we can pass safely", signal none, message "", sideways +0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.48 m from you, the wall on your right 1.27 m.
- **intent:** keep to my left and slow a little so the elderly man on his phone can pass safely
- **reason:** He is elderly, using a cane and distracted by his phone, so I will give him extra room and slow down to pass safely in the narrow passage.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_5767d932_r4/dp1 (non_verbal, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking toward the emergency room while giving Person 1 plenty of room to pass
- **reason:** Someone walked straight into me earlier today and I'm pulling a large suitcase, so I'll ease toward the wall on my right early and let the oncoming person pass before continuing.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_68f09b97_r2/dp5 (non_verbal, agent 0, decision 3)
- seen: -7° (+ left), 5.0 m, walking, signal none, changes ['slowed_down', 'moved_right'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep walking straight to the supermarket, holding my line in the passage.", signal none, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep holding my line in the passage toward the supermarket, staying steady with my cane and suitcase.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.
- **intent:** Keep walking straight down the passage, holding my line with my cane and suitcase.
- **reason:** She's coming head-on in a passage too narrow for both of us to pass easily, and with my cane and suitcase I can't dodge quick. I'll edge slightly right to give her room, then swing back to my line once she's passed, keeping a steady pace so she can read my path.
- **signal:** none; **coded:** side both, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_74cb78c1_r4/dp4 (non_verbal, agent 1, decision 2)
- seen: +4° (+ left), 7.3 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the supermarket and give way to the woman coming the other way.", signal none, message "", sideways -0.50 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.38 m from you, the wall on your right 0.37 m.
- **intent:** Keep to the right-hand side and let the woman pass on my left.
- **reason:** I've already moved right to make room; staying near the right wall leaves the wide side for her to pass without crowding.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_b6a40c60_r2/dp2 (non_verbal, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Give way to the woman with the cane
- **reason:** She's looking at her phone and using a cane, so she won't notice me; I'm easy-going, so I'll shift to my right to give her room and slow down so we don't bump.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_bcb9cb2c_r2/dp1 (non_verbal, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep to my line and my pace, holding my ground as I always do.
- **reason:** I am tired of being walked into and I have as much right to this passage as anyone; I will not swerve for a stranger coming the other way, and my cane and suitcase make me easy enough to see.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_bcb9cb2c_r2/dp2 (non_verbal, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Give way to the woman with the cane and suitcase by keeping to my side of the passage
- **reason:** She's walking with a cane and pulling a suitcase, so I'll shift to my left to give her room and slow down to let her pass easily in the narrow passage.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_02604456_r1/dp12 (talk, agent 1, decision 6)
- seen: +19° (+ left), 1.2 m, walking, signal wave_on, changes ['slowed_down', 'moved_left'], age 25, width 0.5, traits []
- heard: "Hi again! Go ahead, plenty of room." (frame None)
- history: 5.0 s ago "Greet my classmate warmly and carry on toward the supermarket, giving a little room so we can pass each other comfortably.", signal wave_on, message "Hey! Fancy seeing you here!", sideways -0.62 m (+ left)
- history: 4.0 s ago "Keep greeting my classmate warmly while making room for us to pass comfortably.", signal wave_on, message "Hey, good to see you! Go ahead, I've got room on this side.", sideways -0.22 m (+ left)
- history: 3.0 s ago "Greet my classmate warmly and keep giving way so we can pass comfortably.", signal wave_on, message "Hey, good to see you! Go ahead, I've got room on this side.", sideways +0.00 m (+ left)
- history: 2.0 s ago "Greet my classmate warmly and keep giving way so we can pass comfortably", signal wave_on, message "Hey, go ahead, I've got room on this side!", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep close to my right side so my classmate can pass easily on their side of the passage", signal wave_on, message "Thanks! See you around!", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Slide past my classmate on my side and keep heading to the supermarket
- **reason:** They waved me on and moved to their left, so I'll hug my right side and keep moving so we pass quickly and comfortably.
- **message:** Thanks! See you in class!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_0f57f8a5_r3/dp2 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Greet a classmate I know and make room for his suitcase
- **reason:** He's glued to his phone and dragging a big suitcase, so I'll shift toward the left wall to give him space and slow down a bit as we pass.
- **message:** Hi! Excuse me, coming through.
- **signal:** eye_contact; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_5767d932_r1/dp1 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep to my side of the passage, glance up from my phone, and pass Person 1 without bumping into them
- **reason:** The passage is narrow and someone walked into me earlier today, so I want to be clearly on my own side and slow a little as we meet, giving way since I'm easy-going.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_81bae7c3_r1/dp6 (talk, agent 1, decision 3)
- seen: -9° (+ left), 1.7 m, walking, signal nod, changes ['moved_right', 'turned'], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 3.6 s ago "Make sure the elderly woman sees me and knows I'm giving her room to pass.", signal eye_contact, message "", sideways +0.53 m (+ left)
- history: 1.0 s ago "Let her know I'm here and give her plenty of room to pass on her side", signal wave_on, message "Uncle, careful—I'm here.", sideways +0.03 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Slow down and shift further left so the elderly woman with the cane can pass safely while she's looking at her phone.
- **reason:** She's elderly, using a cane, and distracted by her phone, and we know each other, so I should be the one to give way and make it easy for her to get past.
- **message:** Aunty, careful — I'm here, plenty of room.
- **signal:** hold_up_hand; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_8ea28db3_r2/dp4 (talk, agent 1, decision 2)
- seen: -2° (+ left), 7.4 m, walking, signal eye_contact, changes ['moved_left'], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Greet my classmate and gently warn him about walking while looking at his phone, while moving aside to give him room.", signal wave_on, message "Hi there! Watch out, you're on your phone.", sideways +0.50 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.28 m from you, the wall on your right 1.47 m.
- **intent:** Keep giving my classmate room to pass while he's on his phone, and stay clear of him and his cane
- **reason:** He's looking at his phone and using a cane, so I'll keep well to my left, slow a little, and let him pass without crowding him.
- **signal:** eye_contact; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_9950986f_r3/dp6 (talk, agent 0, decision 3)
- seen: +39° (+ left), 1.2 m, walking, signal hold_up_hand, changes ['sped_up'], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 3.5 s ago "Keep walking and give them room to pass, since the passage is narrow and they have a cane and suitcase.", signal none, message "", sideways -0.39 m (+ left)
- history: 1.0 s ago "Give my classmate room to pass on her left while I keep to the right side", signal wave_on, message "Oh hey! Go ahead, plenty of room.", sideways -0.87 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.17 m from you, the wall on your right 0.58 m.
- **intent:** Steady myself against the right wall so my classmate can pass on my left without us bumping, given she's drifting my way with a cane and suitcase
- **reason:** She's drifting right toward the wall I'm heading for and looking at her phone, so I'll slow, tuck further into the right side, and let her pass on my left rather than we collide.
- **message:** Eh, careful — I'll keep right!
- **signal:** hold_up_hand; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.92 / 0.33 m)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_c36d5d49_r1/dp6 (talk, agent 1, decision 3)
- seen: +7° (+ left), 4.8 m, walking, signal nod, changes ['moved_left'], age 70, width 0.5, traits []
- history: 2.0 s ago "Greet Person 1 and keep to my side so we can pass easily in the narrow passage.", signal wave_on, message "Hello! Good to see you — it's late to be out.", sideways -0.40 m (+ left)
- history: 1.0 s ago "Keep to my right, acknowledge Person 1, and pass them easily in the narrow passage.", signal nod, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.17 m from you, the wall on your right 0.58 m.
- **intent:** Keep to my right and pass Person 1 smoothly in the narrow passage.
- **reason:** Person 1 nodded and has moved over to my left, so staying right with a small sidestep gives us both room; slowing slightly makes the pass safe in the narrow, busy passage.
- **message:** Hello again! Let's squeeze past — take care.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_ce2a06ef_r3/dp5 (talk, agent 0, decision 3)
- seen: -1° (+ left), 5.7 m, walking, signal wave_on, changes ['sped_up', 'moved_left', 'turned'], age 25, width 0.5, traits []
- history: 2.0 s ago "Let Person 1 know I'm here and moving slowly with a cane and suitcase, and keep to one side so we pass safely.", signal wave_on, message "Excuse me, sorry — coming through, I'm on my way to the hospital.", sideways -0.62 m (+ left)
- history: 1.0 s ago "Acknowledge Person 1's nod, keep to my right side, and pass them safely without a bump.", signal eye_contact, message "Hello! Mind me, I'm a bit slow today.", sideways -0.08 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Acknowledge Person 1's wave and keep well to my right so we pass safely, staying slow and steady.
- **reason:** Person 1 waved me on, so I nod and thank them. I'm already near the right wall, so I'll ease a little further right and keep my slow pace, letting them pass without a bump since someone walked into me earlier today.
- **message:** Thank you, coming through — slow with my cane and bag.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says slow_down, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_ce2a06ef_r3/dp6 (talk, agent 1, decision 3)
- seen: -1° (+ left), 5.7 m, walking, signal eye_contact, changes ['slowed_down', 'moved_left', 'turned'], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- history: 2.0 s ago "Greet the elderly woman I know and give her plenty of room to pass with her cane and suitcase.", signal nod, message "", sideways +0.52 m (+ left)
- history: 1.0 s ago "Acknowledge the elderly woman I know, keep well clear of her cane and suitcase, and let her pass easily.", signal wave_on, message "Morning! Plenty of room, go ahead.", sideways -0.05 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Greet the elderly woman I know, give her and her cane and suitcase plenty of room, and let her pass easily.
- **reason:** She is elderly, using a cane and pulling a suitcase, and we know each other. I'm easy-going, so I'll keep well to my left side of the passage and slow a little so she has a clear, comfortable path past me.
- **message:** Morning! Plenty of room, go ahead.
- **signal:** wave_on; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_dbd98c92_r3/dp3 (talk, agent 1, decision 2)
- seen: +2° (+ left), 7.6 m, walking, signal wave_on, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep my line and pace toward the emergency room, holding my ground in the passage.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep my line and pace toward the emergency room, acknowledging her wave but not swerving aside.
- **reason:** She's waving me on but drifting across my line to my left; I'll hold my course, then shift slightly right at the last moment to avoid a collision while keeping my pace to the emergency room.
- **message:** Evening! Coming through, I'm in a hurry.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_e57e5fb0_r1/dp8 (talk, agent 1, decision 4)
- seen: -1° (+ left), 5.9 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- history: 3.0 s ago "Greet my classmate warmly and step aside so we can pass easily without bumping.", signal wave_on, message "Oh, hello! Fancy meeting you here so late.", sideways -0.62 m (+ left)
- history: 2.0 s ago "Keep greeting my classmate and make room so we pass without bumping, since she's still coming toward me drifting to my right.", signal eye_contact, message "", sideways -0.08 m (+ left)
- history: 1.0 s ago "Finish making room so we pass without bumping, keeping to the right of the passage.", signal wave_on, message "Good to see you! Go ahead, plenty of room.", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Keep to the right side and let my classmate pass on her left without a bump, since we're already greeting each other.
- **reason:** She's still coming toward me and drifting to my right, so I'll finish shifting to the right wall and slow down to let her slip past—after someone walked into me earlier today I don't want another collision, and it's easy to just give way.
- **message:** Go ahead, I've got plenty of room on my side.
- **signal:** wave_on; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_e57e5fb0_r2/dp11 (talk, agent 0, decision 6)
- seen: +2° (+ left), 3.8 m, walking, signal wave_on, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.']
- history: 5.0 s ago "Greet the elderly man I know and give him room to pass with his suitcase.", signal wave_on, message "Uncle, so late still? Let me move aside for your suitcase.", sideways -0.72 m (+ left)
- history: 4.0 s ago "Greet the elderly man I know and keep well over to my right so he can pass with his suitcase", signal nod, message "Uncle, so late still? Careful with your suitcase ah.", sideways +0.93 m (+ left)
- history: 3.0 s ago "Keep well over to my right and let the old man pass with his suitcase", signal wave_on, message "Uncle, you first lah, plenty of room on my side.", sideways +0.00 m (+ left)
- history: 2.0 s ago "Let the old man pass with his suitcase while I keep to my right side", signal nod, message "Okay okay, Uncle, take care ah.", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep to my right and let the old man pass with his suitcase", signal wave_on, message "Uncle, fancy seeing you! Go ahead, go ahead, plenty of room.", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Stop fidgeting, settle on my right side, and let the old man pass with his suitcase
- **reason:** I've been swaying left and right which isn't fair to him with a big suitcase; my right side has the wall 0.25 m away so if I tuck in there he has room, and then I can get going to the supermarket.
- **message:** Uncle, sorry ah, I keep moving about — I'll just stay on my right, you carry on.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says stop_and_wait, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_02604456_r1/dp2 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Greet my classmate warmly and give room to pass in the narrow passage.
- **reason:** I'm friendly and tend to give way; he looks friendly and we know each other, so I'll say hi and shift aside so we can pass comfortably with my suitcase.
- **message:** Hey! Fancy meeting you here.
- **signal:** wave_on; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_02604456_r1/dp7 (talk, agent 0, decision 4)
- seen: +1° (+ left), 4.2 m, walking, signal eye_contact, changes ['slowed_down'], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- history: 3.0 s ago "Greet my classmate warmly and make a bit of room for her suitcase as we pass.", signal wave_on, message "Hey! Fancy meeting you here.", sideways -0.62 m (+ left)
- history: 2.0 s ago "Greet my classmate warmly, give her room to pass with the suitcase, and stay friendly and easy-going.", signal wave_on, message "Hey! Long time no see — go on, I'll make room for the suitcase.", sideways -0.13 m (+ left)
- history: 1.0 s ago "Let my classmate pass with her suitcase while staying friendly and easy-going.", signal wave_on, message "Go ahead, plenty of room!", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Let my classmate pass with her suitcase while keeping things warm and easy-going.
- **reason:** I'm already near the right wall; a small extra shift gives her suitcase clear room, and a friendly nod keeps the greeting warm without needing to say more in this noise.
- **message:** Take care with the suitcase — see you in class!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_1868bff4_r3/dp10 (talk, agent 1, decision 5)
- seen: -7° (+ left), 0.9 m, walking, signal eye_contact, changes [], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep walking toward the emergency room without losing time, holding my line with my suitcase beside me.", signal none, message "", sideways -0.53 m (+ left)
- history: 3.0 s ago "Keep my line and pace toward the emergency room, shifting only slightly so my suitcase doesn't clip her.", signal none, message "", sideways -0.53 m (+ left)
- history: 2.0 s ago "Keep my pace toward the emergency room, angling slightly right so my suitcase clears her without losing time.", signal eye_contact, message "Excuse me, coming through —", sideways -0.22 m (+ left)
- history: 1.0 s ago "Keep my pace toward the emergency room and pass her on her right, keeping my suitcase clear of her.", signal eye_contact, message "Excuse me, coming through —", sideways +0.12 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Pass the woman on her right without stopping, keeping my suitcase clear of her legs.
- **reason:** She's close and I'm already angled right; a quick small sidestep keeps the suitcase from clipping her while I hold my pace to the emergency room.
- **message:** Excuse me —
- **signal:** eye_contact; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says stop_and_wait, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_231c8154_r1/dp1 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Greet the older man I know and warn him to look up from his phone so we can pass safely.
- **reason:** He is looking at his phone and may not see me, so I wave and step toward the left to give him room, then slow down while he passes.
- **message:** Uncle, watch out ahead!
- **signal:** wave_on; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_2ec958bb_r3/dp8 (talk, agent 1, decision 4)
- seen: +20° (+ left), 1.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 3.2 s ago "Keep walking to the supermarket at my own pace, glancing at my phone now and then", signal none, message "", sideways -0.00 m (+ left)
- history: 2.2 s ago "Keep walking steadily on my side of the passage and hold my line, keeping a glance up for the oncoming man", signal none, message "", sideways -0.00 m (+ left)
- history: 1.1 s ago "Hold my line on my side of the passage, keep a glance up at the oncoming man, and not get pushed aside", signal eye_contact, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Hold my line and keep walking at my pace, watching the oncoming man so I don't get walked into again
- **reason:** Someone walked straight into me earlier today. I'm on my side of the passage and I won't be shoved aside, but I'll edge slightly right at the last moment to avoid a collision while keeping my line.
- **signal:** eye_contact; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_3dee0df5_r1/dp3 (talk, agent 0, decision 2)
- seen: -0° (+ left), 7.2 m, walking, signal hold_up_hand, changes [], age 25, width 0.5, traits ['They are walking with a cane.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Greet my classmate warmly and shift aside so she can pass comfortably with her cane.
- **reason:** She's a friend from class walking with a cane in a narrow passage; a small sidestep and slowing down makes it easy for her to pass, and it's nice to say hello.
- **message:** Hey! Good to see you — let me give you room.
- **signal:** wave_on; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_55c9ae40_r1/dp2 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Give way to the elderly man with a cane by shifting slightly aside as we pass
- **reason:** He's elderly and using a cane while distracted by his phone, so I'll ease over to the right and slow a little to give him room to pass safely.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_81bae7c3_r1/dp3 (talk, agent 0, decision 2)
- seen: +31° (+ left), 7.7 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Greet Person 1 warmly while giving them plenty of room to pass in the narrow passage.", signal wave_on, message "Oh, hello there! Fancy meeting you here so late.", sideways -0.50 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.38 m from you, the wall on your right 0.37 m.
- **intent:** Greet Person 1 again briefly and make sure they have room to pass me on the narrow path.
- **reason:** I'm already drifting right to give them space; a small extra shift and steady pace keeps things easy in the narrow passage, and I'll let them pass before moving on to the supermarket.
- **message:** Evening! Good to see you — go ahead, I'll keep to my side.
- **signal:** wave_on; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_81bae7c3_r4/dp4 (talk, agent 0, decision 2)
- seen: +18° (+ left), 7.0 m, walking, signal none, changes ['slowed_down', 'turned'], age 25, width 0.5, traits []
- history: 1.1 s ago "Keep walking toward the supermarket and greet Person 1 as we pass, making room so we don't collide", signal nod, message "", sideways -0.37 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.25 m from you, the wall on your right 0.50 m.
- **intent:** Greet the classmate warmly and keep well to my right so we pass comfortably
- **reason:** I'm easy-going and want to avoid bumping, so I'll stay over to my right while saying hello as we pass.
- **message:** Oh, hello there! Nice to see you.
- **signal:** wave_on; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_8ea28db3_r4/dp1 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Look up from my phone, make friendly eye contact with Person 1, and ease slightly to my right so we pass comfortably in the narrow passage.
- **reason:** She's someone I know from classes, and after being bumped into earlier I want to avoid another collision. Giving way slightly to the right and slowing a touch keeps things easy and friendly.
- **signal:** eye_contact; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_9b752a36_r1/dp7 (talk, agent 1, decision 4)
- seen: -10° (+ left), 3.7 m, walking, signal wave_on, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.5, traits []
- heard: "Good evening, please go ahead." (frame None)
- history: 3.0 s ago "Keep walking steadily toward the emergency room, holding my line along the passage", signal none, message "", sideways -0.00 m (+ left)
- history: 2.0 s ago "Keep walking steadily toward the emergency room, holding my line, and let the young man step aside around me and my suitcase", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep my line toward the emergency room and let the young man step around me and my suitcase", signal nod, message "Thank you, but I'm in a hurry — could you give me room, please?", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep my line along the passage and get past the young man quickly toward the emergency room
- **reason:** He has already moved over to my left and waved me on, so I can keep my line and my pace without swerving my suitcase into the wall. I am in a hurry and need to reach the emergency room.
- **message:** Thank you, thank you — coming through.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_9b752a36_r3/dp7 (talk, agent 0, decision 4)
- seen: -13° (+ left), 2.8 m, walking, signal nod, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.']
- history: 3.0 s ago "Acknowledge the elderly woman politely and make a little room for her and her suitcase", signal nod, message "", sideways +0.63 m (+ left)
- history: 2.0 s ago "Politely greet her and stay to my left so she and her suitcase pass easily", signal nod, message "Excuse me, coming through — plenty of room.", sideways +0.22 m (+ left)
- history: 1.0 s ago "Give the elderly woman and her suitcase room to pass on my left side.", signal nod, message "Sorry, excuse me — I'll keep to my left, plenty of room.", sideways +0.23 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Let the elderly woman and her suitcase pass safely on my right while I keep to the left
- **reason:** She is elderly and pulling a large suitcase, so I want to stay well over to my left and let her pass on the wider side. A small extra step left gives her more clearance.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_b7fe7ead_r4/dp6 (talk, agent 1, decision 3)
- seen: -4° (+ left), 5.1 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- history: 2.0 s ago "Greet the classmate I know and make room to pass in the narrow passage.", signal wave_on, message "Hi! Fancy meeting you here.", sideways +0.35 m (+ left)
- history: 1.0 s ago "Keep to my left so we can pass each other comfortably in the narrow passage, and stay friendly with the classmate I know.", signal eye_contact, message "Hi again! I'll keep to my side.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.53 m from you, the wall on your right 1.22 m.
- **intent:** Keep to my left and pass the classmate comfortably while staying friendly
- **reason:** We're both greeting each other warmly; I'll keep to my left side and slow a touch so we pass without bumping in the narrow passage.
- **signal:** eye_contact; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_cb859069_r3/dp4 (talk, agent 1, decision 2)
- seen: -1° (+ left), 7.4 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep heading to the emergency room, giving this young man plenty of room so we don't bump.", signal none, message "", sideways -0.35 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.23 m from you, the wall on your right 0.52 m.
- **intent:** Keep to the right side of the passage and slow a little so the young man can pass safely without a bump.
- **reason:** I'm already over to the right and he's coming straight at me; slowing down and keeping to my side gives plenty of room, which suits me fine since I'm in no rush to bump anyone, especially after this morning.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_dbd98c92_r1/dp10 (talk, agent 1, decision 5)
- seen: -2° (+ left), 2.4 m, walking, signal wave_on, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Hello, uncle! Excuse me, let me give you some room." (frame None)
- history: 4.0 s ago "Keep my pace toward the emergency room, get Person 1's attention early, and pass without a collision.", signal wave_on, message "Excuse me, coming through — I'm on my way to the hospital.", sideways -0.53 m (+ left)
- history: 3.0 s ago "Keep moving toward the emergency room and pass Person 1 safely on my left side since she is drifting to my right.", signal nod, message "Thank you, dear — I'm heading to the hospital, please let me by.", sideways -0.03 m (+ left)
- history: 2.0 s ago "Keep my pace to the emergency room and pass Person 1 safely on my left, since she is drifting to my right.", signal nod, message "Thank you, dear — coming through on your left!", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep my pace toward the emergency room and pass Person 1 cleanly on her right side, since she is waving me on and drifting that way.", signal nod, message "Coming through on your left, dear — thank you!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Keep my pace toward the emergency room and pass Person 1 on my left, since she is giving me room and drifting to my right.
- **reason:** She has slowed and waved me on, so I hold my line and keep my pace. Shading slightly left keeps me clear of her as she drifts right, and I don't want to lose time getting to the hospital.
- **message:** Thank you, dear — coming through, I'm heading to the hospital.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_0f57f8a5_r1/dp2 (non_verbal, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Recognise Person 1 and make room for them and their suitcase in the narrow passage
- **reason:** The passage is narrow and they are wheeling a big suitcase while distracted by their phone, so I will shift toward the left wall to give them room and nod or smile in greeting as we pass.
- **signal:** eye_contact; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_1868bff4_r4/dp3 (non_verbal, agent 0, decision 2)
- seen: +1° (+ left), 7.3 m, walking, signal none, changes ['moved_left'], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- history: 1.0 s ago "Keep walking to the supermarket and give the man with the suitcase room to pass.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep to my side so the man with the suitcase can pass safely
- **reason:** The passage is narrow and he's pulling a large suitcase, so I'll ease slightly to my right wall side to give him room, slowing a little as we pass.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_1caa9a84_r1/dp3 (non_verbal, agent 1, decision 2)
- seen: +4° (+ left), 7.6 m, walking, signal none, changes ['slowed_down', 'moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep to my side of the passage and give Person 1 room to pass, since I'm pulling a suitcase and using a cane", signal none, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.08 m from you, the wall on your right 0.67 m.
- **intent:** Keep well to my right and slow a little so the woman can pass safely, given my suitcase and cane
- **reason:** I'm already easing right; slowing slightly gives us both more room and time to pass without a bump, especially since someone knocked into me earlier today.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_1caa9a84_r3/dp11 (non_verbal, agent 1, decision 6)
- seen: -9° (+ left), 0.8 m, still, signal none, changes ['stopped'], age 25, width 0.5, traits []
- history: 5.0 s ago "Keep walking toward the supermarket while stepping slightly aside to avoid a head-on collision with the person coming toward me.", signal none, message "", sideways -0.60 m (+ left)
- history: 4.0 s ago "Keep to my right and pass the woman coming the other way, giving her a bit more room since I already moved over.", signal none, message "", sideways -0.30 m (+ left)
- history: 3.0 s ago "Keep to my right edge and let the woman pass on my left without bumping", signal none, message "", sideways +0.00 m (+ left)
- history: 2.0 s ago "Acknowledge the woman's raised hand and keep to my right so she can pass on my left", signal nod, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep to my right edge and let the woman pass on my left, staying steady so we don't collide", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.37 m from you, the wall on your right 0.38 m.
- **intent:** Acknowledge the woman and keep to my right edge while she passes on my left
- **reason:** She has stopped and is facing away, close by; I'll ease off slightly, keep to the right, and let her pass without bumping after the earlier head-on collision.
- **signal:** hold_up_hand; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_2ec958bb_r2/dp9 (non_verbal, agent 0, decision 5)
- seen: +30° (+ left), 1.0 m, walking, signal eye_contact, changes [], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 4.0 s ago "Keep to my side of the passage and give the elderly woman plenty of room to pass", signal none, message "", sideways -0.72 m (+ left)
- history: 3.0 s ago "Keep well to my right and give the elderly woman on her phone plenty of room to pass", signal none, message "", sideways -0.38 m (+ left)
- history: 2.0 s ago "Slow down and keep well to my right so the elderly woman on her phone can pass safely", signal hold_up_hand, message "", sideways -0.18 m (+ left)
- history: 1.0 s ago "Keep well to my right, slow down and let the elderly woman on her phone pass safely", signal hold_up_hand, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Keep well to my right and slow almost to a stop so the elderly woman looking at her phone passes safely
- **reason:** She is elderly, on her phone, and we are about to meet in a narrow passage; slowing and staying to my right gives her room and avoids a collision.
- **signal:** hold_up_hand; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says stop_and_wait, the plan does not; intent says right, the plan turns none)

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_3cb16ae9_r1/dp1 (non_verbal, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking toward the supermarket while glancing at my phone, holding my line.
- **reason:** I'm determined and tend to hold my ground, and there's enough room for us to pass; no need to change course for a stranger I'm just passing by.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_3dee0df5_r4/dp7 (non_verbal, agent 1, decision 4)
- seen: +10° (+ left), 1.7 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 3.7 s ago "Acknowledge my classmate and keep walking at my own pace, staying on my line in the passage", signal nod, message "", sideways -0.00 m (+ left)
- history: 1.7 s ago "Acknowledge my classmate again and keep my line at my own pace, staying ready to hold my ground if he drifts into me", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Greet my classmate and make sure he sees me and gives me room, without yielding my line in this crowded passage
- **reason:** We know each other and he's slowed down, which often means someone is drifting into my path. Since I got walked into earlier today, I'll raise my hand so he clearly sees me and tap a small sidestep to my right at the last moment to avoid a collision while keeping my pace and most of my line.
- **signal:** hold_up_hand; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_51dfba80_r4/dp6 (non_verbal, agent 0, decision 3)
- seen: +5° (+ left), 5.7 m, walking, signal eye_contact, changes ['moved_left'], age 25, width 0.5, traits []
- history: 2.0 s ago "Acknowledge Person 1 and keep walking on my side so we can pass each other", signal nod, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Acknowledge Person 1 warmly and keep my line so we pass cleanly in the narrow passage", signal eye_contact, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Greet Person 1 warmly and keep my line so we pass cleanly, but shift slightly right to give a bit of room since I'm pulling a big suitcase.
- **reason:** We know each other from classes and made eye contact, so a friendly nod is right. I hold my line generally, but with a large suitcase in a 1.75 m passage, a small sidestep gives us both room to pass without bumping, especially after someone walked into me earlier.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_55c9ae40_r2/dp3 (non_verbal, agent 1, decision 2)
- seen: +1° (+ left), 7.2 m, walking, signal none, changes [], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Keep to my side of the passage and give the older man plenty of room as we pass", signal none, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.08 m from you, the wall on your right 0.67 m.
- **intent:** Give the older man plenty of room and pass him safely on my right side
- **reason:** He is elderly, using a cane and looking at his phone, so he may not see me or keep his line. Slowing down and moving a bit more to the right gives him room and lets him pass without a bump.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_5767d932_r2/dp9 (non_verbal, agent 1, decision 5)
- seen: +5° (+ left), 1.1 m, walking, signal none, changes ['slowed_down'], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 4.0 s ago "keep walking, give her a bit of room since she's on her phone with a suitcase", signal none, message "", sideways -0.72 m (+ left)
- history: 3.0 s ago "Give her plenty of room to pass on my left since she's distracted by her phone and pulling a suitcase", signal none, message "", sideways -0.37 m (+ left)
- history: 2.0 s ago "Keep well to my right so she has room to pass on my left, since she's distracted by her phone and pulling a suitcase.", signal none, message "", sideways -0.07 m (+ left)
- history: 1.0 s ago "Keep well to my right and let her pass, maybe glancing at her but not making a fuss", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Let her pass on my left without making a fuss, keeping close to my right
- **reason:** She's distracted by her phone and pulling a suitcase, so I'll slow slightly and stay right to give her room to pass on my left. No need to signal.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_5841fc4a_x3d3cadc7_base/dp1 (non_verbal, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** keep walking and give a little room so we can pass each other comfortably
- **reason:** The passage is narrow, so I'll ease slightly to my right to leave room and keep walking; no need to signal since there's plenty of space and no confusion.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_5841fc4a_x3d3cadc7_flipped/dp2 (non_verbal, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking to the supermarket and shift slightly to my right so we can pass each other comfortably
- **reason:** The passage is narrow but there is room to pass; giving a little extra space to the right is polite and easy-going, and I keep my pace since I am not in a hurry.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_8ea28db3_r3/dp2 (non_verbal, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal eye_contact, changes [], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Greet the classmate I know and make room for him to pass
- **reason:** He's using a cane and looking at his phone, so he may not see me well. A nod is friendly, and I'll shift slightly right to give him an easy line past me.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_9950986f_r4/dp3 (non_verbal, agent 0, decision 2)
- seen: +2° (+ left), 7.4 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Greet her and give her room to pass, since she's looking at her phone and pulling luggage", signal wave_on, message "", sideways -0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.17 m from you, the wall on your right 0.58 m.
- **intent:** Keep well to my right so she has the clear side by the wall, and slow a little to let her pass safely
- **reason:** She's on her phone with a cane and a suitcase, so she needs space and time; I'm already easing to my right, and slowing slightly gives her the wider gap and a bit more room.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_b7fe7ead_r1/dp4 (non_verbal, agent 1, decision 2)
- seen: -4° (+ left), 7.3 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- history: 1.0 s ago "greet Person 1 and give way so we can pass comfortably in the narrow passage", signal eye_contact, message "", sideways +0.35 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.43 m from you, the wall on your right 1.32 m.
- **intent:** Greet Person 1 back and keep giving way to my left so we can pass comfortably in the narrow passage
- **reason:** He nodded at me, so I nod back. Since I already started moving left to give way and he's a friend from class, I'll keep to my left and slow a little so we pass comfortably in the narrow passage.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_c36d5d49_r4/dp4 (non_verbal, agent 0, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Acknowledge Person 1 with a friendly nod and keep moving toward the emergency room without slowing.", signal nod, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Greet Person 1 warmly and keep moving toward the emergency room without slowing or giving ground.
- **reason:** I'm in a hurry to the ER and will not be pushed aside, but a small sidestep to my left gives us both room to pass while I keep my pace and greet a familiar face.
- **signal:** wave_on; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_cb859069_r2/dp3 (non_verbal, agent 0, decision 2)
- seen: -2° (+ left), 7.5 m, walking, signal nod, changes ['slowed_down', 'moved_left'], age 70, width 0.5, traits ['They are walking with a cane.']
- history: 1.0 s ago "Give the elderly woman with a cane plenty of room and pass without fuss", signal none, message "", sideways +0.35 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.42 m from you, the wall on your right 1.33 m.
- **intent:** Acknowledge her nod and give her plenty of room to pass on the right.
- **reason:** She is elderly, using a cane, and nodded at me, so I'll return the nod and slow a little while keeping well to my left to leave her the wider side of the passage.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_de176842_0f57f8a5_r4/dp2 (non_verbal, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge Person 1 as we pass and keep my line without slowing, nudging slightly right so we clear each other in the narrow passage.
- **reason:** We know each other from classes, so a brief eye contact is friendly. I'm pulling a big suitcase in a tight, busy passage; a small sidestep to my right keeps my ground without a collision, then I carry on to the supermarket.
- **signal:** eye_contact; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_de176842_1868bff4_r3/dp5 (non_verbal, agent 0, decision 2)
- seen: -31° (+ left), 3.6 m, walking, signal eye_contact, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- history: 2.4 s ago "Keep walking to the supermarket and give a friendly nod, then shift a little to my left to leave room for the man with the suitcase to pass", signal eye_contact, message "", sideways +0.06 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.82 m from you, the wall on your right 0.93 m.
- **intent:** Give the man with the suitcase plenty of room to pass on my right and keep my pace steady
- **reason:** He is drifting toward my left and pulling a large suitcase, so I will move further left to give him a clear lane on my right and avoid a knock.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_de176842_231c8154_r2/dp2 (non_verbal, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking to the emergency room, keeping to my side of the passage since she has waved me on.
- **reason:** She has waved me on so I will keep my pace and shift slightly to my right to give her room to pass on my left, since I am easy-going and it is a narrow busy passage.
- **signal:** none; **coded:** side both, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_de176842_51dfba80_r2/dp3 (non_verbal, agent 1, decision 2)
- seen: +7° (+ left), 7.5 m, walking, signal nod, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Acknowledge her and give her room to pass with the suitcase", signal wave_on, message "", sideways -0.50 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.38 m from you, the wall on your right 0.37 m.
- **intent:** Acknowledge her nod and keep giving her plenty of room to pass with the suitcase
- **reason:** She nodded at me and she's busy with her phone and a big suitcase, so I'll keep to my right, slow a little, and let her pass comfortably.
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_5767d932_r2/dp4 (non_verbal, agent 0, decision 2)
- seen: +5° (+ left), 7.5 m, walking, signal none, changes ['slowed_down', 'moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep going toward the emergency room, but glance up and give the oncoming man a bit of room so we don't collide.", signal none, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.18 m from you, the wall on your right 0.57 m.
- **intent:** Keep clear of the oncoming man while staying on my way to the emergency room
- **reason:** I'm easy-going and already shifted right; a small extra sidestep will keep us apart without slowing me much, and I'm still heading to the ER.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_de176842_68f09b97_r4/dp4 (non_verbal, agent 0, decision 2)
- seen: +1° (+ left), 3.6 m, walking, signal none, changes ['slowed_down', 'turned'], age 25, width 0.5, traits []
- history: 2.4 s ago "Keep walking straight to the supermarket; I have the right to my side of the passage and won't be dodging for anyone.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.
- **intent:** Warn the young woman I'm holding my line and she should go around me
- **reason:** She's drifting into my path while pulling my suitcase and using a cane; I'll make a small step aside only at the last moment so we don't collide, then resume my way to the supermarket.
- **signal:** hold_up_hand; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_74cb78c1_r3/dp3 (non_verbal, agent 0, decision 2)
- seen: -5° (+ left), 7.4 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the supermarket, easing slightly to my left so we can pass comfortably.", signal none, message "", sideways +0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.58 m from you, the wall on your right 1.17 m.
- **intent:** Keep easing to my left so we pass comfortably, staying relaxed
- **reason:** I made a small move to my left already and it seems fine; I'll keep my normal pace and a comfortable line so we pass without fuss.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says left, the plan turns none)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_74cb78c1_x42411b7c_base/dp6 (non_verbal, agent 1, decision 3)
- seen: +0° (+ left), 4.7 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep walking towards the supermarket and give way slightly so we can pass each other comfortably in the narrow passage.", signal none, message "", sideways -0.30 m (+ left)
- history: 1.0 s ago "Keep walking to the supermarket, edging slightly to my right so we can pass comfortably.", signal none, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.17 m from you, the wall on your right 0.58 m.
- **intent:** Keep walking to the supermarket, staying slightly to my right so we can pass comfortably in the narrow passage.
- **reason:** I am already offset to my right and there's a bit more room on that side; easing my speed slightly as we close gives us both room to pass without bumping.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_81bae7c3_r3/dp1 (non_verbal, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking toward the supermarket and let Person 1 pass since there's room
- **reason:** I'm easy-going and in no hurry, so I'll shift slightly to the right to give him room and slow a little as he passes.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_81bae7c3_r3/dp8 (non_verbal, agent 1, decision 4)
- seen: -0° (+ left), 4.0 m, walking, signal nod, changes ['slowed_down'], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 3.0 s ago "Greet Person 1 and give her plenty of room to pass, since she is elderly, using a cane, and distracted by her phone.", signal wave_on, message "", sideways +0.62 m (+ left)
- history: 2.0 s ago "Finish yielding to the left side of the passage and give the elderly woman with her cane plenty of room to pass, greeting her back.", signal nod, message "", sideways +0.17 m (+ left)
- history: 1.0 s ago "Keep well to the left and slow right down so the elderly woman with her cane can pass comfortably, staying quiet since it's late at night.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Keep well to the left and let the elderly woman with her cane pass comfortably, staying quiet since it's late at night.
- **reason:** She is elderly, using a cane and looking at her phone, and I'm already yielding to the left. I'll keep slow and silent so she can pass without being crowded or startled.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says left, the plan turns none)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_8ea28db3_r4/dp9 (non_verbal, agent 1, decision 5)
- seen: -0° (+ left), 1.8 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 4.0 s ago "Keep walking to the supermarket and give Person 1 a little extra room since they are looking at their phone and using a cane", signal none, message "", sideways +0.62 m (+ left)
- history: 3.0 s ago "Greet my classmate and keep well to the left so they pass safely with their cane and phone.", signal nod, message "", sideways +0.22 m (+ left)
- history: 2.0 s ago "Greet my classmate back and keep well to the left so they can pass safely with their cane and phone.", signal nod, message "", sideways +0.03 m (+ left)
- history: 1.0 s ago "Acknowledge my classmate and keep to the left so they can pass safely with their cane and phone", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Acknowledge my classmate's nod and keep left so they can pass safely with their cane and phone
- **reason:** They are looking at their phone and using a cane, so I'll slow a little and stay to my left to give them room to pass safely.
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says left, the plan turns none)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_bcb9cb2c_r3/dp9 (non_verbal, agent 1, decision 5)
- seen: +17° (+ left), 2.0 m, walking, signal none, changes ['slowed_down', 'moved_left'], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- history: 4.0 s ago "Acknowledge her and give her room to pass, since she has a cane and a suitcase", signal nod, message "", sideways -0.50 m (+ left)
- history: 3.0 s ago "Keep giving the woman with the cane and suitcase plenty of room to pass, staying on the right side of the passage", signal none, message "", sideways +0.11 m (+ left)
- history: 2.0 s ago "Acknowledge her plainly and slow down to leave her room to pass, keeping to my right", signal hold_up_hand, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.37 m from you, the wall on your right 0.38 m.
- **intent:** Edge further right and slow a little to let the woman with the cane and suitcase pass comfortably
- **reason:** She has a cane and a suitcase and has moved toward my left, so giving her more room on the right keeps things easy and safe late at night.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/N_head_on_de176842_f3d09c23_r1/dp5 (non_verbal, agent 1, decision 3)
- seen: -0° (+ left), 5.1 m, walking, signal none, changes ['slowed_down', 'moved_right', 'turned'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep going toward the emergency room, staying to my side of the passage so the oncoming woman can pass easily.", signal none, message "", sideways -0.30 m (+ left)
- history: 1.0 s ago "Keep to my side of the passage and let the oncoming woman pass without trouble", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.18 m from you, the wall on your right 0.57 m.
- **intent:** Keep to my side of the passage and let the oncoming woman pass without trouble
- **reason:** I'm already hugging the right side of the passage, so I'll just hold my line and my pace, easing off slightly as she passes so there's no bump on the narrow walkway.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_f3d09c23_r4/dp2 (non_verbal, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking toward the emergency room and ease slightly to my right so Person 1 and I can pass without trouble.
- **reason:** We are meeting head-on in a narrow, busy passage. Giving way a little to my right keeps things easy and lets us pass; I do not need to hurry.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_1868bff4_r1/dp3 (silent, agent 1, decision 2)
- seen: -4° (+ left), 3.6 m, walking, signal none, changes ['slowed_down', 'turned'], age 25, width 0.5, traits []
- history: 2.4 s ago "Keep heading to the emergency room without losing time, holding my line in the passage despite the oncoming woman.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep my line and my pace toward the emergency room, letting the oncoming woman pass on my right side without giving up ground.
- **reason:** I am in a hurry and have already been walked into once today; my lane is clear enough and she is drifting to my right, so holding my line lets her pass with the least delay.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['slowed_down', 'turned']; position: ['ahead']); 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says left, the plan turns none)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_1868bff4_r3/dp5 (silent, agent 1, decision 3)
- seen: -3° (+ left), 4.8 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep moving toward the emergency room without losing time, but give myself room so this woman and I don't collide like earlier today.", signal none, message "", sideways -0.44 m (+ left)
- history: 1.0 s ago "Keep heading to the emergency room without slowing, holding my line while making sure the woman and I don't collide.", signal none, message "", sideways +0.44 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.22 m from you, the wall on your right 0.53 m.
- **intent:** Get past the woman without colliding while keeping my pace toward the emergency room.
- **reason:** She has moved to my right, so I shift slightly right to open a clear line on my left and hold my speed; earlier zigzagging cancels out, and this keeps us from repeating the collision from earlier today.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_231c8154_r2/dp5 (silent, agent 0, decision 3)
- seen: +39° (+ left), 0.9 m, walking, signal none, changes ['slowed_down', 'turned'], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 3.6 s ago "Keep heading to the supermarket while letting the older man pass comfortably, and greet him since we know each other.", signal none, message "", sideways -0.40 m (+ left)
- history: 2.6 s ago "Keep to my right to let the older man pass comfortably, then greet him as we cross.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.18 m from you, the wall on your right 0.57 m.
- **intent:** Stay clear of the older man who is drifting toward my left while looking at his phone, and greet him as we pass.
- **reason:** He is drifting to my left and is distracted by his phone, so moving further right keeps a comfortable gap between us; slowing slightly as we meet lets us greet without crowding him.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says left, the plan turns right)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_231c8154_r3/dp8 (silent, agent 0, decision 4)
- seen: -2° (+ left), 2.9 m, walking, signal none, changes ['slowed_down'], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 3.0 s ago "Go to the supermarket and greet the familiar older man as we pass, keeping to my side so he can get by.", signal none, message "", sideways -0.60 m (+ left)
- history: 2.0 s ago "Keep to my side and greet the familiar older man as we pass, giving him plenty of room since he's looking at his phone.", signal none, message "", sideways -0.30 m (+ left)
- history: 1.0 s ago "Keep well to my right so the older man looking at his phone can pass safely, and greet him as we meet.", signal none, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.37 m from you, the wall on your right 0.38 m.
- **intent:** Keep well to my right so the older man looking at his phone can pass safely, and greet him as we meet.
- **reason:** He's still on his phone and has slowed down, and I'm already well over to my right; a little more room and a slower pace keeps it safe and lets me greet him as he goes by.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_2ec958bb_r1/dp1 (silent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking toward the supermarket while glancing at my phone, but hold my line so I don't get bumped again.
- **reason:** Someone walked straight into me earlier today, so I'll stay on my path but shift slightly to the right at the last moment to give a bit of clearance without slowing down.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_68f09b97_r3/dp2 (silent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Give the elderly man with the cane plenty of room as we pass.
- **reason:** He is elderly, using a cane and pulling a suitcase, so I will move aside to my right and slow down to let him pass comfortably.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_800a3b04_r3/dp2 (silent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking toward the supermarket, shifting a little to the right to give the elderly man with the suitcase room to pass.
- **reason:** He is elderly, distracted by his phone, and pulling a suitcase, so I will make space and slow slightly to let him pass safely.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_81bae7c3_r3/dp5 (silent, agent 0, decision 3)
- seen: +3° (+ left), 5.5 m, walking, signal none, changes ['slowed_down', 'moved_right', 'turned'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep walking to the supermarket and let Person 1 pass by, glancing up from my phone to be polite.", signal none, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep heading to the supermarket and let Person 1 pass, giving him a little room since the passage is narrow.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Let Person 1 pass safely in the narrow passage, stepping a little to my right (away from the nearer left wall) while keeping an eye up from my phone to be polite.
- **reason:** The passage is narrow and he's coming straight at me; giving a bit of room to the right keeps us from bumping, and slowing slightly while glancing up is the courteous thing to do since we know each other from classes.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_8ea28db3_r2/dp3 (silent, agent 1, decision 2)
- seen: +3° (+ left), 7.6 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Keep walking to the supermarket and give Person 1 room to pass, since he's on his phone with a cane and we know each other.", signal none, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.08 m from you, the wall on your right 0.67 m.
- **intent:** Keep giving Person 1 plenty of room to pass and carry on to the supermarket.
- **reason:** He's on his phone with a cane and we know each other, so I'll ease a bit further right to leave a clear gap, then carry straight on.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_b1d97a31_r1/dp5 (silent, agent 0, decision 3)
- seen: -0° (+ left), 5.6 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep heading to the supermarket, but edge a little to my left to give the young woman plenty of room and avoid another bump.", signal none, message "", sideways +0.53 m (+ left)
- history: 1.0 s ago "Keep heading to the supermarket and give the young woman plenty of room, staying well to my left so we don't bump.", signal none, message "", sideways +0.22 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Keep to my left and slow a touch so the young woman and I pass without bumping.
- **reason:** The passage is narrow and someone bumped into me earlier today; I am easy-going, so I will hold my line on the left and let her pass with room.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says left, the plan turns none)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_b59c2831_r4/dp1 (silent, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits ['They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking to the supermarket and give Person 1 a friendly greeting as we pass
- **reason:** She is distracted by her phone in a narrow passage; stepping slightly aside gives her room, and slowing a little lets me greet her without startling her at night.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_b7fe7ead_r1/dp6 (silent, agent 0, decision 3)
- seen: +42° (+ left), 1.0 m, walking, signal none, changes ['turned'], age 25, width 0.5, traits []
- history: 3.5 s ago "Get to the emergency room without another collision, keeping my line and passing Person 1 cleanly.", signal none, message "", sideways -0.63 m (+ left)
- history: 2.5 s ago "Keep to my right side of the passage and get past Person 1 without a collision, on my way to the emergency room.", signal none, message "", sideways -0.13 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.41 m from you, the wall on your right 0.34 m.
- **intent:** Keep to my right and slip past Person 1 without another collision, since they have swung toward my left side.
- **reason:** Person 1 is closing in at 42° to my left after changing direction, and I'm already hugging the right wall. Nudging a bit further right keeps me clear and lets them pass on my left.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_bcb9cb2c_r1/dp3 (silent, agent 0, decision 2)
- seen: -1° (+ left), 7.5 m, walking, signal none, changes ['slowed_down', 'moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the supermarket without being knocked over again.", signal none, message "", sideways +0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.47 m from you, the wall on your right 1.28 m.
- **intent:** Keep walking to the supermarket without being knocked over again, holding my ground but giving a little room for the man coming toward me.
- **reason:** He is coming straight at me in a narrow passage. I already shifted left; I'll keep my line but ease a bit to the right at close range so we can pass without a collision, since someone walked into me earlier tonight.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_cb859069_r1/dp6 (silent, agent 0, decision 3)
- seen: +7° (+ left), 5.1 m, walking, signal none, changes [], age 70, width 0.5, traits ['They are walking with a cane.']
- history: 2.0 s ago "Give the elderly woman with a cane plenty of room as we pass", signal none, message "", sideways -0.40 m (+ left)
- history: 1.0 s ago "Keep well clear of the elderly woman with the cane as she passes", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.17 m from you, the wall on your right 0.58 m.
- **intent:** Give the elderly woman with the cane plenty of room as we pass
- **reason:** She's elderly, using a cane, and there's still a little room to my right to widen the gap before she reaches me; then I'll hold my line and let her pass.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_ce2a06ef_r2/dp2 (silent, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep moving toward the emergency room, but give Person 1 plenty of room so nobody collides again.
- **reason:** I'm in a hurry to the ER and pulling a heavy suitcase, but someone already barged into me today. I'll ease toward the left wall and let this young man pass, then carry on.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_e57e5fb0_r3/dp4 (silent, agent 0, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal none, changes ['slowed_down', 'moved_left'], age 70, width 0.7, traits ['They are pulling a large suitcase.']
- history: 1.0 s ago "Keep walking to the supermarket and give the older man with the suitcase room to pass.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep walking to the supermarket and give the older man with the suitcase room to pass.
- **reason:** The passage is narrow and he is elderly with a large suitcase; stepping slightly to the right gives him room while keeping my path to the supermarket.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/S_head_on_de176842_2ec958bb_r3/dp6 (silent, agent 1, decision 3)
- seen: -2° (+ left), 1.3 m, walking, signal none, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.5, traits []
- history: 3.5 s ago "Keep walking to the supermarket at my usual pace, watching the oncoming man so I don't get bumped into again.", signal none, message "", sideways -0.47 m (+ left)
- history: 1.1 s ago "Keep my line to the supermarket but give myself room so the crossing man and I don't collide again.", signal none, message "", sideways +0.31 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.34 m from you, the wall on your right 0.41 m.
- **intent:** Hold my line to the supermarket and avoid another collision with this oncoming man without giving up too much ground.
- **reason:** He keeps drifting left into my path, so I'll angle slightly right to open a gap, then straighten back toward the supermarket once he's passed. I'm not stopping for him; I just don't want another body check.
- **signal:** none; **coded:** side both, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/S_head_on_de176842_5841fc4a_x42411b7c_flipped/dp1 (silent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking to the supermarket and give the oncoming man enough room to pass.
- **reason:** The passage is narrow, and I'm easy-going, so I'll edge towards the left wall and let him pass with a bit more clearance.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_de176842_800a3b04_r1/dp7 (silent, agent 0, decision 4)
- seen: -2° (+ left), 3.3 m, walking, signal none, changes ['slowed_down', 'moved_right', 'turned'], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep heading toward the emergency room, giving Person 1 plenty of room as I pass.", signal none, message "", sideways -0.52 m (+ left)
- history: 2.0 s ago "Keep clear of Person 1 and stay on my way to the emergency room, giving her plenty of room.", signal none, message "", sideways -0.13 m (+ left)
- history: 1.0 s ago "Give Person 1 plenty of room while continuing toward the emergency room.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Pass Person 1 safely without crowding her, keeping on toward the emergency room.
- **reason:** She has slowed and moved toward my right, so I ease off, shift a little further right to leave a clear gap, and let her pass without rushing.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_de176842_81bae7c3_r4/dp2 (silent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep heading to the supermarket and pass Person 1 politely, giving a little room since it's a narrow passage and I'm easy-going.
- **reason:** The passage is narrow and I'm using a cane while glancing at my phone, so slowing slightly and shifting a bit to my right leaves room for the young man to pass without either of us bumping into the walls.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_de176842_bcb9cb2c_r2/dp2 (silent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking toward the supermarket, holding my line but giving a little room so we can pass
- **reason:** I'm determined but the passage is narrow, and after being walked into earlier I'd rather shift slightly to my right so we pass cleanly without a collision.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/S_head_on_de176842_bcb9cb2c_r3/dp3 (silent, agent 0, decision 2)
- seen: +1° (+ left), 2.3 m, walking, signal none, changes ['slowed_down', 'turned'], age 25, width 0.5, traits []
- history: 2.9 s ago "Keep walking toward the supermarket, holding my line in the passage.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.
- **intent:** Hold my line and pass safely, keeping my suitcase clear of the wall
- **reason:** He is drifting to my left, so a slight shift right keeps a gap between us without giving up the corridor; I hold my ground but leave room since the passage is narrow and I'm pulling a suitcase.
- **signal:** none; **coded:** side both, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['slowed_down', 'turned']; position: ['ahead']); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/S_head_on_de176842_cb859069_r1/dp8 (silent, agent 1, decision 4)
- seen: +0° (+ left), 3.1 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 3.1 s ago "Keep heading to the emergency room, but shift a little to the right so the young man and I pass safely, since he's coming straight at me in this narrow passage.", signal none, message "", sideways -0.63 m (+ left)
- history: 2.1 s ago "Keep to my right side of the passage so the young man and I pass each other safely, and keep heading to the emergency room.", signal none, message "", sideways -0.23 m (+ left)
- history: 1.1 s ago "Keep to my right and pass the young man safely on my left, while heading to the emergency room.", signal none, message "", sideways -0.02 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Keep passing safely on my right, giving the young man room, while heading to the emergency room.
- **reason:** He's slowed down and we're closing fast in a narrow passage; stepping back a little toward the middle gives us both space, and my cane and slow pace mean I should be the one to yield.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says right, the plan turns left)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_0f57f8a5_r3/dp1 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Greet an acquaintance from my classes while keeping on my way to the supermarket.
- **reason:** It's someone I know from class, so a quick wave is friendly, and I'll shift slightly left to pass without stopping since I'm headed to the supermarket with my suitcase.
- **signal:** wave_on; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_0f57f8a5_r4/dp3 (talk, agent 1, decision 2)
- seen: -4° (+ left), 7.3 m, walking, signal nod, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Greet Person 1 as we pass and shift slightly aside to leave room for their suitcase", signal nod, message "", sideways +0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.48 m from you, the wall on your right 1.27 m.
- **intent:** Greet my classmate warmly while giving extra room for his suitcase
- **reason:** He's looking at his phone and pulling a large suitcase, so I'll shift a bit more to my left to leave him room and greet him as we pass.
- **message:** Hey! Late night too, huh?
- **signal:** eye_contact; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_231c8154_r2/dp5 (talk, agent 0, decision 3)
- seen: nobody
- history: 4.1 s ago "Greet the elderly man I know from class and give him plenty of room since he's looking at his phone", signal wave_on, message "", sideways -0.60 m (+ left)
- history: 1.3 s ago "Greet him back warmly and keep well to my right so he can pass safely while on his phone", signal nod, message "Hello! Yes, take care ah!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.38 m from you, the wall on your right 0.37 m.
- **intent:** Keep well to my right and carry on toward the supermarket, leaving the middle of the passage clear for anyone coming the other way
- **reason:** I've already greeted him and given way; nobody else is nearby, so I just keep walking smoothly on my right side of the passage.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_3dee0df5_r3/dp5 (talk, agent 1, decision 3)
- seen: +6° (+ left), 4.9 m, walking, signal nod, changes ['slowed_down', 'moved_left'], age 25, width 0.5, traits []
- heard: "Yeah, tell me about it! Take care out there." (frame facing)
- history: 2.0 s ago "Acknowledge Person 1 and keep my line, expecting them to make room this time, given what happened earlier today.", signal nod, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Greet Person 1 warmly and keep walking on my line, giving them a clear chance to step aside this time.", signal nod, message "Hey! Yeah, late night run for me too — groceries don't buy themselves.", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Acknowledge Person 1's farewell and keep my line, holding my ground in the narrow passage now that they've moved over to my left.
- **reason:** They've stepped toward my left, which frees my right side; a small sidestep to the right keeps clear of them without abandoning my line, and after they pass I carry on to the supermarket.
- **message:** You too — see you in class!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_55c9ae40_r1/dp3 (talk, agent 0, decision 2)
- seen: +2° (+ left), 7.6 m, walking, signal nod, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.5, traits []
- heard: "Of course, uncle, go ahead." (frame facing)
- history: 1.0 s ago "Make sure the young woman notices me and gives me room, so she doesn't walk into me like the last person did.", signal hold_up_hand, message "Excuse me, coming through — I'm heading to the hospital.", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep walking straight toward the hospital; she's giving way, so hold my line and pass her on my right.
- **reason:** She has already nodded and told me to go ahead, so there's no need to slow down or argue. A small sidestep to my right keeps me clear of the side she's drifting toward and lets me pass without another collision.
- **message:** Thank you, thank you.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_81bae7c3_r2/dp4 (talk, agent 1, decision 2)
- seen: -21° (+ left), 2.4 m, walking, signal wave_on, changes ['moved_right'], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- heard: "Oh, hello there! Sorry, I was glued to my phone." (frame facing)
- history: 3.1 s ago "Give the elderly woman plenty of room and avoid startling her, since she's looking at her phone and using a cane in a narrow passage.", signal none, message "", sideways +0.35 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.43 m from you, the wall on your right 1.32 m.
- **intent:** Reassure her, keep well clear on my left, and let her pass safely while she's on her phone with her cane.
- **reason:** She's elderly, using a cane, and distracted by her phone; a narrow passage at night calls for patience and extra room. Sidestepping further left keeps a wide gap so she isn't startled or crowded.
- **message:** Oh, hello! No worries at all. Please take your time.
- **signal:** wave_on; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_8ea28db3_r2/dp1 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking toward the supermarket, giving Person 1 room to pass since he's using a cane and looking at his phone.
- **reason:** He's distracted on his phone and using a cane, so I'll shift slightly to my right to give him space to pass without bumping into me.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_8ea28db3_r3/dp12 (talk, agent 1, decision 6)
- seen: -0° (+ left), 0.6 m, walking, signal wave_on, changes ['slowed_down', 'turned'], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- heard: "Thanks, going through on your right!" (frame facing)
- history: 5.0 s ago "Greet my classmate and keep walking past him, giving him room since he's using a cane and looking at his phone.", signal wave_on, message "Hey! Good to see you!", sideways +0.53 m (+ left)
- history: 3.0 s ago "Give my classmate room to pass on his cane side while I stay to the left and keep walking to the supermarket", signal nod, message "Thanks! I'll keep left.", sideways +0.12 m (+ left)
- history: 2.0 s ago "Keep to my left so my classmate with the cane can pass on my right", signal wave_on, message "No worries, go ahead!", sideways -0.00 m (+ left)
- history: 1.0 s ago "Stay to the left and let my classmate with the cane pass on my right", signal wave_on, message "Go ahead, I'll keep left!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Move aside to give my classmate clear room on his stated side
- **reason:** He said he's going through on 'my right' but from his view that's actually my left — I'd drifted left into his path, so I step further left out of his way and slow down until he's passed.
- **message:** Oops, my right, sorry!
- **signal:** wave_on; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_b1d97a31_r1/dp2 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking to the supermarket, giving the older man a bit of room as we pass in the narrow passage.
- **reason:** He's elderly and the passage is narrow, so I'll ease to my right to give him space and avoid bumping as we pass.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_b7fe7ead_r2/dp10 (talk, agent 0, decision 5)
- seen: -1° (+ left), 1.2 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 4.0 s ago "Acknowledge Person 1, urge them to keep moving so we can pass, and get to the ER quickly", signal wave_on, message "Hi! Sorry, I can't stop — I'm on my way to the emergency room. I need to keep going!", sideways -0.70 m (+ left)
- history: 3.0 s ago "Keep moving quickly past Person 1 and stay on my way to the ER", signal nod, message "Thanks — I'm coming through!", sideways -0.35 m (+ left)
- history: 2.0 s ago "Acknowledge Person 1's kindness and keep moving quickly past them toward the ER", signal wave_on, message "Thanks — coming through, take care!", sideways -0.35 m (+ left)
- history: 1.0 s ago "Get past Person 1 quickly and keep heading to the ER", signal wave_on, message "Thanks — coming through, take care!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.47 m from you, the wall on your right 0.28 m.
- **intent:** Squeeze past Person 1 on the right and keep rushing to the ER
- **reason:** I'm in a hurry for the ER and just need to slip by them on the right; a quick wave and 'excuse me' keeps it friendly without slowing me down.
- **message:** Excuse me, coming through — thanks!
- **signal:** wave_on; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_bcb9cb2c_r3/dp2 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal eye_contact, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Acknowledge the other person and give them plenty of room as we pass, since they are using a cane and pulling a suitcase
- **reason:** It's late and quiet and they have a cane and suitcase, so I'll slow a bit and step toward the wall to leave them an easy line.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_ce2a06ef_r1/dp4 (talk, agent 1, decision 2)
- seen: +29° (+ left), 7.7 m, walking, signal nod, changes ['moved_right'], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- heard: "Thank you, dear, that's very kind!" (frame facing)
- history: 1.0 s ago "Acknowledge Person 1 and give her room to pass on my right, since she is in a hurry.", signal wave_on, message "Hello! No problem, I'll make way for you.", sideways -0.50 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.28 m from you, the wall on your right 0.47 m.
- **intent:** Keep giving the elderly woman room to pass on my right and continue to the supermarket.
- **reason:** She is elderly, using a cane and pulling a suitcase, and she is drifting toward my right, so I keep well to my right wall to give her a clear path and avoid crowding her.
- **message:** You're welcome! Take care!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_dbd98c92_r2/dp1 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Greet Person 1 warmly and warn them to look up from their phone, then give them room to pass on the safer side.
- **reason:** They are elderly, using a cane, pulling a suitcase and looking at their phone, so they need space and warning; I am easy-going and give way, and the wall on my left is nearer, so stepping left keeps me out of their line while still leaving room.
- **message:** Hello! Careful there, the passage is narrow.
- **signal:** wave_on; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_dbd98c92_r2/dp11 (talk, agent 0, decision 6)
- seen: -31° (+ left), 0.9 m, walking, signal nod, changes ['moved_right'], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "Thank you, dear — I've got you, passing on your left!" (frame facing)
- history: 5.0 s ago "Greet Person 1 warmly and warn them to look up from their phone, then give them room to pass on the safer side.", signal wave_on, message "Hello! Careful there, the passage is narrow.", sideways +0.53 m (+ left)
- history: 4.0 s ago "Give the elderly man plenty of room to pass on my left side and keep the greeting friendly and clear.", signal wave_on, message "Yes, coming through — mind the cane and the suitcase, uncle! Take your time.", sideways -0.90 m (+ left)
- history: 3.0 s ago "Guide the elderly man safely past me on my left while keeping a friendly tone, and slow down so he has time to look up from his phone.", signal wave_on, message "Hello again, uncle! Plenty of room on my left, take your time.", sideways -0.00 m (+ left)
- history: 2.0 s ago "Move fully to my left so the elderly man and his suitcase have the wider right side to pass, and warn him off his phone.", signal point, message "Here, uncle — I'll keep to my left, you come by on my right. Watch your step!", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep well to my left so the elderly man and his suitcase have room to pass on the wider right side, and urge him to look up from his phone.", signal point, message "Okay uncle, I'll stay left — you come by on your right side, please look up from your phone!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Hold my line on the left so the elderly man and his suitcase pass safely on the right, now that he has acknowledged me.
- **reason:** He has thanked me and said he is passing on my left (my right side physically), so I should stop shuffling and simply stay out of his way on the left while he and the suitcase go by.
- **message:** Ah, sorry uncle — I'll keep left, you're fine!
- **signal:** wave_on; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_dbd98c92_r2/dp6 (talk, agent 1, decision 3)
- seen: -2° (+ left), 5.7 m, walking, signal wave_on, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.5, traits []
- heard: "Hello again, uncle! Plenty of room on my left, take your time." (frame facing)
- history: 2.0 s ago "Acknowledge her greeting and keep moving toward the emergency room, holding my line but keeping a little to my right so we pass safely.", signal nod, message "Hello! Yes, I see you — coming through, thank you!", sideways -0.50 m (+ left)
- history: 1.0 s ago "Keep my pace toward the emergency room, easing slightly right so we pass cleanly, watching for the drift she's making toward my right.", signal nod, message "", sideways -0.20 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.28 m from you, the wall on your right 0.47 m.
- **intent:** Keep moving toward the emergency room and pass Person 1 cleanly, holding slightly right as she suggested.
- **reason:** She's waving me on with plenty of room on her left (my right), so I'll take her cue, keep my pace, and slip a little further right to pass without a collision.
- **message:** Thank you, dear — I see you!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_e57e5fb0_r2/dp8 (talk, agent 1, decision 4)
- seen: +2° (+ left), 3.5 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 2.0 s ago "Greet her back warmly and keep moving, giving way by shifting a little to my left so we can pass comfortably in the narrow passage.", signal wave_on, message "Good evening! Nice to see you.", sideways +0.40 m (+ left)
- history: 1.0 s ago "Keep moving forward along the left side, giving her room to pass, and watch her so we don't bump into each other.", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.38 m from you, the wall on your right 1.37 m.
- **intent:** Keep to the left and pass her carefully without bumping, given the tight space and what happened earlier today.
- **reason:** She has slowed down, so I will ease my pace and shift a bit further left to give her room and avoid a collision like earlier today.
- **signal:** eye_contact; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_f3d09c23_r3/dp3 (talk, agent 1, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep heading to the emergency room, easing slightly to my right to give Person 1 room to pass, since I'm easy-going about giving way.", signal none, message "", sideways -0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.18 m from you, the wall on your right 0.57 m.
- **intent:** Keep giving Person 1 room to pass and stay on my way to the emergency room
- **reason:** I'm easy-going and already easing right to leave her space; keeping my pace steady avoids crowding the passage.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_f3d09c23_r4/dp7 (talk, agent 0, decision 4)
- seen: +0° (+ left), 3.1 m, walking, signal nod, changes [], age 25, width 0.5, traits ['They are walking with a cane.']
- history: 3.0 s ago "Give the man with the cane plenty of room by moving to my right, since he's on my right side of the passage anyway", signal none, message "", sideways -0.72 m (+ left)
- history: 2.0 s ago "Keep well clear of the man with the cane while continuing to the supermarket", signal none, message "", sideways +0.16 m (+ left)
- history: 1.0 s ago "Keep well to my right so the man with the cane has space to pass on his side", signal nod, message "", sideways -0.13 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Slide a little further right to give the man with the cane room to pass, then carry on to the supermarket
- **reason:** He's on a cane and we're in a narrow passage, so keeping to my right gives him room to pass safely without me stopping.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_de176842_02604456_r2/dp2 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- heard: "Hi! Fancy meeting you here." (frame facing)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Greet my classmate, acknowledge his wave-on, and keep to my side of the passage so we can pass each other.
- **reason:** He waved me on, so I'll let him take the clearer line and shift a little toward the left wall to keep my suitcase out of his way; slowing near him keeps us from bumping in the busy passage.
- **message:** Hi! Good to see you! Yes, go ahead, I've got the suitcase.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_de176842_1868bff4_r2/dp3 (talk, agent 0, decision 2)
- seen: -2° (+ left), 7.4 m, walking, signal none, changes ['moved_left'], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- history: 1.0 s ago "Give way to the man with the suitcase by keeping to my left so we can pass comfortably", signal none, message "", sideways +0.50 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.37 m from you, the wall on your right 1.38 m.
- **intent:** Keep well to my left so the man with the suitcase can pass comfortably, slowing a little to let him through the narrow gap
- **reason:** The passage is narrow and he is pulling a large suitcase, so giving him extra room and easing my pace avoids a clumsy squeeze; I am easy-going and happy to give way.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_de176842_1caa9a84_r2/dp1 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **unreadable:** missing_until: steps[3]
- **flags:** 5:unreadable (missing_until: steps[3])

### rf40_round1_head_on_turn_taking/T_head_on_de176842_231c8154_r2/dp5 (talk, agent 0, decision 3)
- seen: -3° (+ left), 5.1 m, walking, signal wave_on, changes ['moved_left'], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- heard: "Thanks, dear! You take care too!" (frame facing)
- history: 2.0 s ago "Greet the older man I know from classes and make space for him since he's distracted by his phone.", signal wave_on, message "", sideways +0.63 m (+ left)
- history: 1.0 s ago "Greet him back warmly and keep giving him plenty of room on his left as he walks past with his phone.", signal wave_on, message "You're welcome, uncle! Take care ah!", sideways +0.22 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **unreadable:** missing_until: steps[2]
- **flags:** 5:unreadable (missing_until: steps[2])

### rf40_round1_head_on_turn_taking/T_head_on_de176842_3cb16ae9_r2/dp7 (talk, agent 0, decision 4)
- seen: -5° (+ left), 2.7 m, walking, signal nod, changes [], age 25, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 3.0 s ago "Keep walking to the supermarket and give the distracted phone-walker plenty of room", signal none, message "", sideways +0.63 m (+ left)
- history: 2.0 s ago "Acknowledge him warmly, pass on my left with room, and keep heading to the supermarket", signal wave_on, message "Hey! Sorry, didn't mean to crowd you — go ahead.", sideways +0.27 m (+ left)
- history: 1.0 s ago "Acknowledge him back and slip past on my left, keeping plenty of room", signal wave_on, message "You're welcome — good night!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Keep to my left and slip past him quietly, giving him room
- **reason:** He's distracted on his phone but nodded at me, so I'll stay out of his way on my left and pass quietly without more chatter this late at night.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_de176842_3dee0df5_r1/dp2 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal eye_contact, changes [], age 25, width 0.5, traits ['They are walking with a cane.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **unreadable:** unknown_start: steps[2].start: got 'other_passes'
- **flags:** 5:unreadable (unknown_start: steps[2].start: got 'other_passes')

### rf40_round1_head_on_turn_taking/T_head_on_de176842_3dee0df5_r1/dp6 (talk, agent 0, decision 3)
- seen: -1° (+ left), 4.9 m, walking, signal eye_contact, changes ['moved_left'], age 25, width 0.5, traits ['They are walking with a cane.']
- heard: "Hi! Careful, it's crowded tonight." (frame facing)
- heard: "Hi again — I'm keeping to my line, just give me a little room." (frame facing)
- history: 1.0 s ago "Greet my classmate warmly and give her room to pass on the cane side", signal nod, message "", sideways +0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.47 m from you, the wall on your right 1.28 m.
- **intent:** Greet her warmly and shift further to my right so she has clear room on her cane side and we pass safely
- **reason:** She said she's keeping her line and needs room, and since she moved over to my left, her cane side is toward my right — so I'll give way to the right and keep my speed steady as I pass.
- **message:** Hi! Sorry, coming through — plenty of room on your side.
- **signal:** wave_on; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_de176842_55c9ae40_r4/dp4 (talk, agent 0, decision 2)
- seen: -2° (+ left), 7.3 m, walking, signal hold_up_hand, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking steadily toward the emergency room without being knocked into again", signal eye_contact, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep moving steadily to the emergency room and make sure the oncoming woman yields rather than walking into me again
- **reason:** Last time someone walked straight into me in a passage like this. She has her hand up, so she's seen me; I want to shift slightly to my left to open a passing lane while keeping my steady pace, then continue on to the emergency room.
- **message:** Excuse me, coming through — I need to get to the hospital.
- **signal:** hold_up_hand; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_de176842_b1d97a31_r2/dp10 (talk, agent 0, decision 5)
- seen: +2° (+ left), 0.9 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Good evening!" (frame facing)
- history: 4.0 s ago "Keep walking to the supermarket, giving the oncoming woman plenty of room since the passage is narrow and someone bumped into me earlier.", signal none, message "", sideways -0.62 m (+ left)
- history: 3.0 s ago "Acknowledge her nod and keep well to my right so we pass safely in the narrow passage.", signal nod, message "", sideways -0.28 m (+ left)
- history: 2.0 s ago "Acknowledge the oncoming woman politely and hold my line close to the right wall so we pass safely in the narrow passage.", signal nod, message "Good evening.", sideways +0.00 m (+ left)
- history: 1.0 s ago "Stay close to the right wall and let the woman pass safely, without crowding or surprising her", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Keep close to the right wall and let the woman pass without any fuss
- **reason:** We are already passing and I'm well over to my right, so holding my line avoids bumping into her like happened earlier.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_b6a40c60_r3/dp4 (talk, agent 1, decision 2)
- seen: +31° (+ left), 3.5 m, walking, signal hold_up_hand, changes [], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- heard: "Excuse me, coming through." (frame facing)
- history: 2.4 s ago "keep walking to the supermarket while making room for the woman with the cane", signal none, message "", sideways -0.07 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.94 m from you, the wall on your right 0.81 m.
- **intent:** Give the woman with the cane plenty of room to pass on my left, then carry on to the supermarket
- **reason:** She's using a cane and looking at her phone, so I'll step well aside to my right and slow down to let her through safely.
- **message:** No problem, go ahead.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_de176842_cb859069_r4/dp10 (talk, agent 1, decision 5)
- seen: -0° (+ left), 1.9 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Take your time, aunty — plenty of room here." (frame facing)
- history: 4.0 s ago "Acknowledge the young man's nod politely and keep to my side of the passage so we can pass easily.", signal nod, message "", sideways +0.62 m (+ left)
- history: 3.0 s ago "Acknowledge the young man again and keep well to my left so we pass each other easily.", signal nod, message "", sideways +0.32 m (+ left)
- history: 2.0 s ago "Keep well to my left, stay against the wall side, and pass the young man safely without bumping.", signal nod, message "Hello there, coming through on my left.", sideways +0.03 m (+ left)
- history: 1.0 s ago "Keep close to the left wall so the young man can pass on his right, and steady myself with my cane.", signal nod, message "Thank you, dear — I'm keeping to my left here.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Acknowledge him warmly and edge a little closer to the left wall so we pass cleanly.
- **reason:** He has slowed and given me room, so I keep my pace steady and stay close to the left wall to avoid any bump, especially after being knocked into earlier today.
- **message:** Such a kind young man, thank you.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** none

### rf40_round1_head_on_turn_taking/T_head_on_de176842_ce2a06ef_r3/dp12 (talk, agent 1, decision 6)
- seen: -3° (+ left), 1.9 m, walking, signal nod, changes ['sped_up'], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- heard: "Thank you, dear — I'll keep going, I'm in a bit of a hurry." (frame facing)
- history: 5.0 s ago "Greet her warmly and move aside to let her pass with her cane and suitcase.", signal nod, message "Hello, auntie! Sure, I'll give way — take care.", sideways +0.62 m (+ left)
- history: 4.0 s ago "Finish giving way to her and let her pass comfortably with her cane and suitcase.", signal wave_on, message "You're welcome, auntie — plenty of room, go ahead.", sideways -0.70 m (+ left)
- history: 3.0 s ago "Keep well to the side and let her pass with her cane and suitcase.", signal nod, message "You're welcome, auntie!", sideways -0.00 m (+ left)
- history: 2.0 s ago "Reassure her and stay out of her way so she can pass comfortably with her cane and suitcase.", signal hold_up_hand, message "Take your time, auntie — I'll stay over here.", sideways -0.00 m (+ left)
- history: 1.0 s ago "Stay calmly to my left side of the passage and let her pass with her cane and suitcase.", signal wave_on, message "No rush, auntie — plenty of space.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Stay clear of her path and let her pass quickly with her cane and suitcase.
- **reason:** She's in a hurry and has a cane and suitcase, so I'll keep well over to my left and let her through without fuss.
- **message:** Go ahead, auntie — I'm over here.
- **signal:** wave_on; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

## Every flag of a small rule (132)

### rf39_round1_head_on_sidestep_reprompt/I_head_on_de176842_55c9ae40_r3/dp1 (independent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep going straight toward the emergency room at my steady pace, holding my ground and staying on my line.
- **reason:** I'm an old man with a cane on my way to the ER; I walk at my usual speed and hold my line, and the gap of 1.75 m lets us pass each other. I don't dodge people who walk straight at me.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_231c8154_r2/dp2 (non_verbal, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Acknowledge Person 1 and give way so we can pass each other comfortably
- **reason:** The passage is narrow and I'm easy-going, so a small nod of greeting and stepping a little toward the wall on my left leaves her plenty of room; slowing a touch as we pass keeps things calm and safe for an old man on his way to the hospital.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_55c9ae40_r1/dp4 (non_verbal, agent 1, decision 2)
- seen: +28° (+ left), 2.8 m, walking, signal hold_up_hand, changes [], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 2.7 s ago "Keep walking to the supermarket and give the elderly man room to pass", signal none, message "", sideways -0.11 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Give the elderly man plenty of room and slow down so he can pass safely
- **reason:** He's elderly, using a cane and looking at his phone, and he's waving a hand — he probably wants space or is signalling. I'm easy-going, so I'll move further right and slow down to let him pass without any trouble.
- **signal:** hold_up_hand; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['hold_up_hand'])

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_55c9ae40_r3/dp6 (non_verbal, agent 0, decision 4)
- seen: +7° (+ left), 0.8 m, walking, signal hold_up_hand, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep going straight to the emergency room without being pushed aside again", signal none, message "", sideways +0.00 m (+ left)
- history: 3.0 s ago "Keep walking straight to the emergency room without being pushed aside again", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Hold my line and warn her off so she doesn't walk into me like the last one did", signal hold_up_hand, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Hold my line, keep my hand up and my eyes on her, and tell her to mind where she's going so she doesn't barge into me like the last one
- **reason:** She's drifting into my path and only a moment from me — I'll keep my hand up to warn her, but at the last instant I shift right to avoid a collision, then carry straight on to the emergency room.
- **signal:** hold_up_hand; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: ['slowed_down']); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_81bae7c3_r2/dp7 (non_verbal, agent 1, decision 4)
- seen: +7° (+ left), 4.6 m, walking, signal nod, changes ['moved_left', 'turned'], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 3.0 s ago "Make room for the elderly woman with the cane to pass safely, and greet her when we're close.", signal none, message "", sideways -0.72 m (+ left)
- history: 2.0 s ago "Keep well to my right so the elderly woman with the cane has room to pass, and greet her when we're near.", signal none, message "", sideways -0.32 m (+ left)
- history: 1.0 s ago "Acknowledge her with a friendly nod and keep well to the right so she has room to pass with her cane.", signal nod, message "", sideways -0.32 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Acknowledge her greeting, keep well to the right so she can pass with her cane, and give her a clear path
- **reason:** She nodded at me, so I nod back to be friendly. Since she is elderly, using a cane and looking at her phone, she might not see me well, so I give her plenty of room on my right and slow down so she can pass safely.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_9950986f_r3/dp6 (non_verbal, agent 1, decision 3)
- seen: -51° (+ left), 0.7 m, walking, signal eye_contact, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 4.1 s ago "Keep my line to the emergency room and acknowledge Person 1 as we pass", signal eye_contact, message "", sideways -0.06 m (+ left)
- history: 3.1 s ago "Acknowledge Person 1 and keep my line to the emergency room", signal nod, message "", sideways -0.06 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.84 m from you, the wall on your right 0.91 m.
- **intent:** Acknowledge Person 1 and keep my line to the emergency room without colliding
- **reason:** They're drifting into my path at close range, so I give a brief nod of recognition and shift slightly left to avoid a collision while continuing toward the ER.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: ['slowed_down'])

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_b7fe7ead_r3/dp6 (non_verbal, agent 1, decision 3)
- seen: -6° (+ left), 5.3 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- history: 2.0 s ago "Greet him warmly and give way a little so we can pass easily", signal eye_contact, message "", sideways +0.35 m (+ left)
- history: 1.0 s ago "Greet him warmly from a little distance and keep giving him room to pass", signal wave_on, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.42 m from you, the wall on your right 1.33 m.
- **intent:** return his greeting warmly and keep to my left so he has room to pass
- **reason:** He nodded, so I nod back and stay on my left to leave him plenty of space to pass easily.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_c36d5d49_r2/dp3 (non_verbal, agent 0, decision 2)
- seen: +5° (+ left), 7.4 m, walking, signal nod, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Get Person 1's attention and slip past without losing time, since I'm heading to the emergency room.", signal eye_contact, message "", sideways -0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.17 m from you, the wall on your right 0.58 m.
- **intent:** Acknowledge Person 1 and keep moving past them quickly toward the emergency room
- **reason:** I already made eye contact and shifted right; a quick nod returns their greeting, and keeping to my right lets us pass without slowing me down since I need to reach the ER
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_02604456_r4/dp3 (non_verbal, agent 0, decision 2)
- seen: +1° (+ left), 7.7 m, walking, signal nod, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- history: 1.0 s ago "Acknowledge my classmate and make room for her suitcase to pass", signal eye_contact, message "", sideways +0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.47 m from you, the wall on your right 1.28 m.
- **intent:** Acknowledge my classmate and keep clear of her suitcase as she passes
- **reason:** I already nodded and moved left; I'll slow a touch and stay along the left wall so her large suitcase has room to pass without either of us bumping into it.
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 2:own_signal (claimed: nodded; own earlier signals: ['eye_contact']); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_51dfba80_r3/dp5 (non_verbal, agent 0, decision 3)
- seen: +6° (+ left), 5.1 m, walking, signal eye_contact, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep my course and greet the young man I know from my classes, making sure he sees me since I've been bumped into before.", signal eye_contact, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Acknowledge him and keep my line, letting him make room since he waved me on", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.
- **intent:** Greet him warmly and hold my line, letting him make room as he waved me on
- **reason:** He already waved me on, and I'm determined to hold my ground after being bumped into earlier. A small sidestep at the last moment keeps my suitcase from hitting him while I keep walking steadily toward the supermarket.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['eye_contact'])

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_81bae7c3_r1/dp9 (non_verbal, agent 0, decision 5)
- seen: -1° (+ left), 1.8 m, walking, signal eye_contact, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 4.0 s ago "greet Person 1 as we pass and keep to my side of the passage", signal eye_contact, message "", sideways -0.60 m (+ left)
- history: 3.0 s ago "greet Person 1 warmly as we pass and keep to my side of the passage", signal nod, message "", sideways -0.30 m (+ left)
- history: 2.0 s ago "Greet Person 1 warmly as we pass and keep to my side of the passage", signal nod, message "", sideways -0.30 m (+ left)
- history: 1.0 s ago "greet Person 1 warmly as we pass and stay on my side of the passage", signal nod, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.47 m from you, the wall on your right 0.28 m.
- **intent:** Greet Person 1 warmly as we pass and stay on my side of the passage
- **reason:** We know each other from classes, so a friendly nod is right; I'll slow a little and keep to my side so an older lady with a cane passes safely.
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25]); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_8ea28db3_r3/dp7 (non_verbal, agent 0, decision 4)
- seen: +0° (+ left), 3.2 m, walking, signal nod, changes ['moved_right'], age 25, width 0.5, traits []
- history: 3.0 s ago "Greet my classmate and give her room to pass in the narrow passage", signal eye_contact, message "", sideways -0.62 m (+ left)
- history: 2.0 s ago "Greet my classmate warmly and keep well to the right so she can pass easily", signal wave_on, message "", sideways -0.23 m (+ left)
- history: 1.0 s ago "Greet my classmate back warmly and give her plenty of room to pass on my left", signal nod, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Greet my classmate warmly and keep well to the right while she passes on my left
- **reason:** She waved/nodded back and is on my right, so I'll stay right and slow a touch so she has clear space on my left to pass, being easy-going and remembering being bumped into earlier.
- **signal:** eye_contact; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['nod'])

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_9950986f_r1/dp7 (non_verbal, agent 0, decision 4)
- seen: +13° (+ left), 2.9 m, walking, signal nod, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 3.0 s ago "Greet my classmate with a friendly wave as we approach each other.", signal wave_on, message "", sideways -0.62 m (+ left)
- history: 2.0 s ago "Greet my classmate and give her plenty of room to pass, since she's on her phone and pulling a suitcase", signal wave_on, message "", sideways -0.63 m (+ left)
- history: 1.0 s ago "Keep clear of her path and greet her so I can get past safely", signal wave_on, message "", sideways -0.08 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Acknowledge my classmate's nod and keep well clear of her path as we pass
- **reason:** She's on her phone, has a cane and a big suitcase, and we're in a narrow passage. I've already shifted right, so a little more room and a slightly slower pace lets us pass without bumping, and a nod returns her greeting politely.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_9b752a36_r4/dp2 (non_verbal, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep my line and speed toward the emergency room, letting the young man make room for an elderly woman with a suitcase
- **reason:** I am in a hurry and in pain; I will keep walking purposefully with a brief eye contact and shift slightly to the right at the last moment so we can pass, since the passage is narrow and I am pulling a suitcase.
- **signal:** eye_contact; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_9b752a36_r4/dp6 (non_verbal, agent 1, decision 3)
- seen: -7° (+ left), 4.8 m, walking, signal nod, changes ['slowed_down', 'moved_right', 'turned'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep my line and speed toward the emergency room, letting the young man make room for an elderly woman with a suitcase", signal eye_contact, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep my line and speed and signal the young man to make room for me", signal hold_up_hand, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep my line and speed toward the emergency room, gesturing to the young man to give way for an elderly woman with a suitcase
- **reason:** He has slowed and moved but is still drifting toward my line; I am determined and pulled a big suitcase, so I hold my path, flash my hand once more, then ease slightly right only if he closes in, to avoid a collision while keeping momentum to the hospital.
- **signal:** hold_up_hand; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_9b752a36_r4/dp8 (non_verbal, agent 1, decision 4)
- seen: -15° (+ left), 2.4 m, walking, signal nod, changes ['moved_left', 'turned'], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep my line and speed toward the emergency room, letting the young man make room for an elderly woman with a suitcase", signal eye_contact, message "", sideways -0.00 m (+ left)
- history: 2.0 s ago "Keep my line and speed and signal the young man to make room for me", signal hold_up_hand, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep my line and speed toward the emergency room, gesturing to the young man to give way for an elderly woman with a suitcase", signal hold_up_hand, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep my line and speed and press the young man to step aside for an elderly woman with a suitcase
- **reason:** He nods and shifts to my left, so a small step to my right clears him while I keep moving fast toward the emergency room without breaking my stride.
- **signal:** hold_up_hand; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_c36d5d49_r4/dp6 (non_verbal, agent 1, decision 3)
- seen: -35° (+ left), 1.0 m, walking, signal nod, changes ['slowed_down', 'turned'], age 70, width 0.5, traits []
- history: 3.7 s ago "Greet my acquaintance as we pass and give her room in the narrow passage", signal nod, message "", sideways +0.62 m (+ left)
- history: 2.7 s ago "Greet my acquaintance and give her room to pass in the narrow passage", signal eye_contact, message "", sideways +0.22 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Acknowledge her nod and ease further to my left so we can pass comfortably
- **reason:** She's elderly, drifting toward my left, and we're closing fast in a narrow passage; a small step aside and a slower pace gives her room while I return her greeting.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_dbd98c92_r2/dp8 (non_verbal, agent 1, decision 4)
- seen: +0° (+ left), 3.8 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep moving toward the emergency room but acknowledge Person 1 and avoid another collision in this narrow passage.", signal eye_contact, message "", sideways -0.53 m (+ left)
- history: 2.0 s ago "Acknowledge Person 1 and make it clear which side I'll pass on, while continuing toward the emergency room.", signal wave_on, message "", sideways -0.23 m (+ left)
- history: 1.0 s ago "Acknowledge Person 1, slow down, and keep clearly to my right so we pass safely in this narrow passage without another collision.", signal hold_up_hand, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Acknowledge Person 1 and pass safely on my right side without colliding
- **reason:** I have little room on my right (wall 0.35 m), so I slow down and keep close to my side, giving the young woman a clear, predictable line to pass. A nod returns her greeting and signals I've seen her.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_02604456_r1/dp11 (talk, agent 0, decision 6)
- seen: +19° (+ left), 1.2 m, walking, signal wave_on, changes ['sped_up'], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- history: 5.0 s ago "Greet my classmate warmly and make room for her and her suitcase to pass.", signal wave_on, message "Eh, hi! Fancy seeing you here.", sideways +0.03 m (+ left)
- history: 4.0 s ago "Let my classmate and her suitcase pass easily while staying friendly", signal wave_on, message "Hi again! Go ahead, plenty of room.", sideways -2.10 m (+ left)
- history: 3.0 s ago "Keep to my side and let my classmate and her suitcase pass easily while staying friendly", signal wave_on, message "Hi again! Go ahead, plenty of room.", sideways -0.50 m (+ left)
- history: 2.0 s ago "Hold my ground on the right side and let my classmate and her suitcase pass cleanly", signal wave_on, message "Hi again! Go ahead, plenty of room.", sideways -0.50 m (+ left)
- history: 1.0 s ago "Stay clear on the right so my classmate and her suitcase can pass smoothly", signal wave_on, message "Okay, go ahead, I'll keep right!", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.75 m from you, the wall on your right 1.00 m.
- **intent:** Let my classmate with the suitcase pass on my left while I hold to the right wall
- **reason:** I'm already close to the right wall and she's waving me on, but she's pulling a big suitcase and still coming toward me, so I'll slow a little and keep right to give her room, then carry on once she's passed.
- **message:** Go ahead, go ahead!
- **signal:** wave_on; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 2:own_position (claimed: on my right; walls left 0.75, right 1.0); 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_02604456_r3/dp9 (talk, agent 0, decision 5)
- seen: -2° (+ left), 2.0 m, walking, signal wave_on, changes ['slowed_down', 'moved_left'], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- heard: "Hey, good to see you!" (frame None)
- history: 4.0 s ago "Greet my classmate warmly and give way so she can pass with her suitcase.", signal wave_on, message "Hi! Good to see you!", sideways +0.50 m (+ left)
- history: 3.0 s ago "Let my classmate pass with her suitcase, keeping to the left side and greeting her warmly", signal nod, message "", sideways -0.00 m (+ left)
- history: 2.0 s ago "Keep to the left and let my classmate pass with her suitcase", signal eye_contact, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep to the left and let my classmate with the suitcase pass comfortably", signal eye_contact, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.28 m from you, the wall on your right 1.47 m.
- **intent:** Pass her on my left while she keeps to her side with the suitcase
- **reason:** She waved me on and moved to my left, so there is room for me to slip past on the left while she wheels her suitcase.
- **message:** Thanks, coming through on your left!
- **signal:** wave_on; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_0f57f8a5_r2/dp8 (talk, agent 1, decision 4)
- seen: -2° (+ left), 3.7 m, walking, signal eye_contact, changes ['slowed_down', 'moved_left'], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 3.0 s ago "Greet my classmate and warn him since he's looking at his phone while pulling a suitcase", signal wave_on, message "Hey, watch out!", sideways +0.53 m (+ left)
- history: 2.0 s ago "Greet my classmate, keep warning him about walking with his phone while pulling the suitcase, and give him room to pass on my right", signal wave_on, message "Hey, eyes up — that suitcase's got a mind of its own!", sideways -0.79 m (+ left)
- history: 1.0 s ago "Keep to my side of the passage so my classmate can pass safely with his suitcase", signal hold_up_hand, message "Eyes up, eh? Let me know if you need more room!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Keep to my side and let my classmate pass safely on my left while he's distracted by his phone
- **reason:** He's already moved over to my left, so I'll shift a little more left to keep clear of his suitcase and give him space to pass without bumping into me.
- **message:** Coming through on your left — plenty of room!
- **signal:** wave_on; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says right, the plan turns left); 4:coming_through_on_your_side (own move: left)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_231c8154_r1/dp5 (talk, agent 0, decision 3)
- seen: +0° (+ left), 4.9 m, walking, signal hold_up_hand, changes ['slowed_down', 'moved_right'], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 2.0 s ago "Say hello to the man I know from classes and pass him comfortably in the narrow passage", signal eye_contact, message "", sideways -0.72 m (+ left)
- history: 1.0 s ago "Greet the man from my classes warmly and slip past him on my right without crowding him", signal wave_on, message "Hi! Good to see you!", sideways -0.32 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Greet my classmate warmly and slip past him on his left (my right) without crowding him, since he's slowed down and moved to my right.
- **reason:** He has slowed and shifted to my right while looking at his phone, so I'll keep well over on my right, greet him and ease past without bumping him.
- **message:** Hi! Sorry, coming through on your right—take it easy!
- **signal:** wave_on; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says slow_down, the plan does not); 4:coming_through_on_your_side (own move: right)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_231c8154_r1/dp7 (talk, agent 0, decision 4)
- seen: +10° (+ left), 3.0 m, walking, signal nod, changes ['slowed_down', 'moved_left', 'turned'], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- heard: "Sorry, sorry! Excuse me, please." (frame None)
- history: 3.0 s ago "Say hello to the man I know from classes and pass him comfortably in the narrow passage", signal eye_contact, message "", sideways -0.72 m (+ left)
- history: 2.0 s ago "Greet the man from my classes warmly and slip past him on my right without crowding him", signal wave_on, message "Hi! Good to see you!", sideways -0.33 m (+ left)
- history: 1.0 s ago "Greet my classmate warmly and slip past him on his left (my right) without crowding him, since he's slowed down and moved to my right.", signal wave_on, message "Hi! Sorry, coming through on your right—take it easy!", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Let him keep to his side while I shift left and pass him smoothly without bumping
- **reason:** He's drifted toward my right while apologising and looking at his phone, so the right side is closing up; slipping past on my left keeps us both clear and I don't want to crowd an older man who's distracted.
- **message:** No worries, uncle! Coming through on your left now—watch your step, okay?
- **signal:** wave_on; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_3dee0df5_r4/dp8 (talk, agent 1, decision 4)
- seen: -8° (+ left), 4.3 m, walking, signal eye_contact, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep walking as I am, holding my line, and acknowledge Person 1 as we approach.", signal eye_contact, message "", sideways +0.00 m (+ left)
- history: 2.0 s ago "Keep my line and pass Person 1, acknowledging their wave but not yielding extra space", signal nod, message "Okay, coming through!", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep my line and make sure Person 1 knows I'm here with my cane so we don't collide", signal eye_contact, message "Morning! Mind the cane, okay?", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Hold my line, give a clear warning, and pass Person 1 without a collision
- **reason:** He's drifting into my path at 30 degrees and someone walked into me earlier today; I'll slow and shift slightly left to open a gap while keeping my ground and making sure he sees the cane.
- **message:** Steady there — I'm on your right side, mind the cane.
- **signal:** eye_contact; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: ['slowed_down']); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_68f09b97_r2/dp1 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking toward the supermarket, holding my line with my cane and suitcase
- **reason:** I'm an old man with a cane and a big suitcase; I don't move fast and I have the right to my share of the path, but a small sidestep keeps things smooth without slowing me much.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25]); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_8ea28db3_r4/dp2 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Greet my classmate and warn him I'm passing so he looks up from his phone, keeping to the side away from the phone-distracted walker.
- **reason:** He's looking at his phone and using a cane, so I'll give him room by shifting to my left and let him know I'm there.
- **message:** Hey! Watch out ahead — I'm coming through on your left.
- **signal:** wave_on; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_c36d5d49_r3/dp5 (talk, agent 0, decision 3)
- seen: +6° (+ left), 4.6 m, walking, signal eye_contact, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep moving quickly toward the emergency room and acknowledge Person 1 as we pass", signal nod, message "", sideways -0.30 m (+ left)
- history: 1.0 s ago "Acknowledge Person 1's wave and keep moving briskly toward the emergency room, passing on my right side", signal wave_on, message "Thank you, dear — coming through!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.07 m from you, the wall on your right 0.68 m.
- **intent:** Keep moving briskly past Person 1 on my right while making clear I need to get by to the emergency room
- **reason:** I am already rushing to the emergency room and Person 1 is someone I know from class; a quick verbal acknowledgement and slight move to my right keeps us both clear without slowing me much.
- **message:** Excuse me, dear — I'm in a hurry to the hospital!
- **signal:** hold_up_hand; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:position_side (claimed: on my right; position: ['left'])

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_ce2a06ef_r1/dp10 (talk, agent 0, decision 5)
- seen: -38° (+ left), 2.8 m, walking, signal wave_on, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 4.1 s ago "Ask Person 1 to make space while I keep moving toward the emergency room", signal wave_on, message "Hello, coming through — I'm on my way to the hospital, could you give me a little room please?", sideways -0.35 m (+ left)
- history: 3.1 s ago "Keep moving toward the emergency room and pass Person 1 safely, staying a little to my right since I've already moved over, and slowing a touch so we don't bump.", signal eye_contact, message "Thank you, dear — coming through, please.", sideways +0.05 m (+ left)
- history: 2.1 s ago "Keep moving toward the emergency room and pass Person 1 safely, staying to my right since I've already moved over, while slowing a little to avoid a bump.", signal nod, message "Thank you, dear — I'm coming through slowly on your left side.", sideways +0.28 m (+ left)
- history: 1.0 s ago "Pass Person 1 safely on my left side and keep heading to the emergency room", signal nod, message "Thank you, dear — coming through.", sideways +0.27 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.13 m from you, the wall on your right 0.62 m.
- **intent:** Keep moving toward the emergency room, passing Person 1 on my left without bumping, since they've waved me on and slowed.
- **reason:** They've slowed and waved me on, but they're drifting across my path, so I'll ease off and edge a little further left to pass safely, then carry on to the hospital.
- **message:** Thank you, dear — I'll keep to my left, coming through slowly.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: ['slowed_down']); 1:position_side (claimed: on my left; position: ['right'])

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_ce2a06ef_r1/dp12 (talk, agent 0, decision 6)
- seen: -11° (+ left), 2.1 m, walking, signal wave_on, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 5.1 s ago "Ask Person 1 to make space while I keep moving toward the emergency room", signal wave_on, message "Hello, coming through — I'm on my way to the hospital, could you give me a little room please?", sideways -0.35 m (+ left)
- history: 4.1 s ago "Keep moving toward the emergency room and pass Person 1 safely, staying a little to my right since I've already moved over, and slowing a touch so we don't bump.", signal eye_contact, message "Thank you, dear — coming through, please.", sideways +0.05 m (+ left)
- history: 3.1 s ago "Keep moving toward the emergency room and pass Person 1 safely, staying to my right since I've already moved over, while slowing a little to avoid a bump.", signal nod, message "Thank you, dear — I'm coming through slowly on your left side.", sideways +0.28 m (+ left)
- history: 2.0 s ago "Pass Person 1 safely on my left side and keep heading to the emergency room", signal nod, message "Thank you, dear — coming through.", sideways +0.28 m (+ left)
- history: 1.0 s ago "Keep moving toward the emergency room, passing Person 1 on my left without bumping, since they've waved me on and slowed.", signal nod, message "Thank you, dear — I'll keep to my left, coming through slowly.", sideways -0.22 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.12 m from you, the wall on your right 0.63 m.
- **intent:** Keep moving toward the emergency room and pass Person 1 smoothly on my left without bumping
- **reason:** The gap is closing fast and they've waved me on and slowed; a small extra step to my left with a gentle speed gives us both room, especially as someone bumped into me earlier today.
- **message:** Thank you, dear — slowly now, coming through on your left.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_dbd98c92_r3/dp8 (talk, agent 0, decision 4)
- seen: +10° (+ left), 3.0 m, walking, signal hold_up_hand, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 3.1 s ago "Greet Person 1 warmly and give them plenty of room to pass, since they are elderly, using a cane, pulling a suitcase, and distracted by their phone.", signal wave_on, message "", sideways -0.72 m (+ left)
- history: 2.0 s ago "Greet Person 1 warmly and keep well to my right so the elderly man with the cane and suitcase can pass safely.", signal wave_on, message "Hello! Good evening, let me give you space.", sideways -0.22 m (+ left)
- history: 1.0 s ago "Greet Person 1 warmly and keep well to my right so the elderly man with the cane and suitcase can pass safely.", signal wave_on, message "Hello Uncle! Good evening — I'll keep right, plenty of room for you.", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Give the elderly man plenty of room on my right and pass him safely before we collide.
- **reason:** He is elderly, using a cane, pulling a suitcase and looking at his phone, so he may not see me well. I should keep to my right against the wall and slow slightly so we pass with space rather than bumping.
- **message:** Uncle, coming through on your right — careful, okay?
- **signal:** wave_on; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_f3d09c23_r2/dp7 (talk, agent 0, decision 4)
- seen: -0° (+ left), 3.3 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits ['They are walking with a cane.']
- history: 3.0 s ago "Keep walking to the supermarket, giving the man with the cane plenty of room by easing toward the left wall", signal none, message "", sideways +0.53 m (+ left)
- history: 2.0 s ago "Acknowledge the man with the cane and ease over to the left wall so he has plenty of room to pass", signal nod, message "", sideways +0.52 m (+ left)
- history: 1.0 s ago "Give the man with the cane plenty of room by staying close to the left wall as he passes", signal nod, message "", sideways -0.08 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Keep close to the left wall and let the man with the cane pass safely
- **reason:** He's using a cane and has slowed down, so I'll give him extra room by hugging the left wall and keep my pace steady until he's passed.
- **message:** Excuse me, coming through on your left.
- **signal:** hold_up_hand; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_02604456_r1/dp10 (talk, agent 1, decision 5)
- seen: +2° (+ left), 2.7 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Go ahead, plenty of room!" (frame None)
- history: 4.0 s ago "Greet my classmate warmly and give room to pass in the narrow passage.", signal wave_on, message "Hey! Fancy meeting you here.", sideways +0.52 m (+ left)
- history: 3.0 s ago "Keep greeting my classmate warmly and shift fully to my left so they can pass comfortably, since they've waved me on.", signal nod, message "Hey, long time no see! Here, go ahead—there's room on my side.", sideways +0.22 m (+ left)
- history: 2.0 s ago "Stay friendly with my classmate and keep hugging the left side so he can pass comfortably in the narrow passage.", signal eye_contact, message "Hey, good to see you! I'll keep to my left—go ahead!", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep to the left and let my classmate pass comfortably, staying friendly.", signal wave_on, message "There you go, plenty of room!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.35 m from you, the wall on your right 1.40 m.
- **intent:** Let my classmate pass comfortably on my right while staying friendly
- **reason:** He waved me on and said there's plenty of room, so I'll keep hugging the left wall to give him space as we pass, and greet him warmly.
- **message:** Thanks! See you around!
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['nod'])

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_3dee0df5_r2/dp7 (talk, agent 0, decision 4)
- seen: +32° (+ left), 3.8 m, walking, signal hold_up_hand, changes [], age 25, width 0.5, traits ['They are walking with a cane.']
- history: 3.0 s ago "Greet her warmly and make room to pass in the narrow passage.", signal wave_on, message "Hi! Fancy meeting you here this late.", sideways +0.20 m (+ left)
- history: 2.0 s ago "Let her pass safely on her side while I keep to the left, slowing a touch in the narrow passage.", signal wave_on, message "Nice to see you! Go ahead, I'll keep left.", sideways -0.92 m (+ left)
- history: 1.0 s ago "Make clear which side I'm passing on and keep clear of her cane side so she can pass safely.", signal wave_on, message "Sorry, let me give you room on your right — go ahead!", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.67 m from you, the wall on your right 1.08 m.
- **intent:** Settle on one side clearly — keep left and slip past her so we both get through the narrow passage without clashing.
- **reason:** I've been drifting back and forth and each wave just adds confusion. She's on my side of the passage with a cane, so I should commit to keeping left, slow a bit, and let her pass on the clear side rather than keep shifting into her path.
- **message:** Sorry, coming through on your left now!
- **signal:** wave_on; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_51dfba80_r4/dp5 (talk, agent 1, decision 3)
- seen: +36° (+ left), 5.0 m, walking, signal wave_on, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 2.0 s ago "Keep walking toward the supermarket, giving the older woman room to pass since she's distracted by her phone and pulling a suitcase.", signal none, message "", sideways -0.50 m (+ left)
- history: 1.0 s ago "Warn her I'm here and give her room to pass while she's on her phone with the suitcase.", signal wave_on, message "Aunty ji, careful!", sideways -0.50 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.38 m from you, the wall on your right 0.37 m.
- **intent:** Acknowledge her wave and slip past her on her left-hand side, keeping clear of her suitcase
- **reason:** She's waved me on but she's distracted by her phone and dragging a big suitcase, so I'll say thanks, edge a bit further right into the gap I already have, and keep a slow, steady line so nothing surprises her.
- **message:** Thank you, aunty ji — I'm coming past on your right side.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_5767d932_r4/dp3 (talk, agent 0, decision 2)
- seen: -0° (+ left), 7.4 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking toward the emergency room, glancing up from my phone to avoid Person 1.", signal none, message "", sideways -0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.27 m from you, the wall on your right 0.48 m.
- **intent:** Keep to my side and slip past Person 1 with the suitcase
- **reason:** Someone walked into me earlier today, so I glance up and give a little more room on the right to avoid a repeat while dragging the suitcase.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:trait_suitcase (trait lines: 1)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_9950986f_r1/dp8 (talk, agent 1, decision 4)
- seen: -4° (+ left), 2.9 m, walking, signal wave_on, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep my pace toward the emergency room while acknowledging a familiar face from class", signal eye_contact, message "", sideways -0.40 m (+ left)
- history: 2.0 s ago "Acknowledge my classmate and keep moving toward the emergency room without slowing down much", signal nod, message "Hey! Excuse me, coming through — I'm in a bit of a hurry.", sideways -0.40 m (+ left)
- history: 1.0 s ago "Get past my classmate quickly without breaking stride, since I'm rushing to the emergency room", signal hold_up_hand, message "Hey, sorry — I need to squeeze past on your left.", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.28 m from you, the wall on your right 0.47 m.
- **intent:** Keep my pace and slip past my classmate on the left without breaking stride, since I'm rushing to the emergency room.
- **reason:** He has moved to my left and waved me on, so I'll angle slightly left to open a gap and keep my speed up toward the emergency room.
- **message:** Thanks — coming through on your left!
- **signal:** wave_on; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_b6a40c60_r2/dp6 (talk, agent 1, decision 3)
- seen: -6° (+ left), 4.8 m, walking, signal eye_contact, changes [], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 2.0 s ago "Keep walking to the supermarket, giving the woman with the cane plenty of room since she is on her phone.", signal none, message "", sideways +0.50 m (+ left)
- history: 1.0 s ago "Keep to the left so the woman on her phone has the clear side of the passage", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.38 m from you, the wall on your right 1.37 m.
- **intent:** Give the woman with the cane plenty of room by keeping well to my left, and let her know I'm passing so she can keep her eyes on her phone and cane.
- **reason:** She's looking at her phone and using a cane, so I'll stay out of her path on the left and slow a touch until she's passed.
- **message:** Sorry, coming through on your left!
- **signal:** hold_up_hand; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_dbd98c92_r1/dp12 (talk, agent 1, decision 6)
- seen: -27° (+ left), 1.0 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Hello again, uncle! Go ahead, I'll keep to the side." (frame None)
- history: 5.0 s ago "Keep my pace toward the emergency room, get Person 1's attention early, and pass without a collision.", signal wave_on, message "Excuse me, coming through — I'm on my way to the hospital.", sideways -0.33 m (+ left)
- history: 4.0 s ago "Keep moving toward the emergency room and pass Person 1 safely on my left side since she is drifting to my right.", signal nod, message "Thank you, dear — I'm heading to the hospital, please let me by.", sideways +0.17 m (+ left)
- history: 3.0 s ago "Keep my pace to the emergency room and pass Person 1 safely on my left, since she is drifting to my right.", signal nod, message "Thank you, dear — coming through on your left!", sideways +0.20 m (+ left)
- history: 2.0 s ago "Keep my pace toward the emergency room and pass Person 1 cleanly on her right side, since she is waving me on and drifting that way.", signal nod, message "Coming through on your left, dear — thank you!", sideways +0.20 m (+ left)
- history: 1.0 s ago "Keep my pace toward the emergency room and pass Person 1 on my left, since she is giving me room and drifting to my right.", signal nod, message "Thank you, dear — coming through, I'm heading to the hospital.", sideways +0.20 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.20 m from you, the wall on your right 0.55 m.
- **intent:** Keep my pace to the emergency room and slip past Person 1 on my left, since she has stepped aside for me.
- **reason:** She greeted me and is keeping to the side, so there is room on my left — I will hold my line and pass with a small sidestep rather than making another late change.
- **message:** Thank you, dear — excuse me, coming past.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:position_side (claimed: on my left; position: ['right'])

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_dbd98c92_r1/dp6 (talk, agent 1, decision 3)
- seen: -1° (+ left), 5.6 m, walking, signal wave_on, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep my pace toward the emergency room, get Person 1's attention early, and pass without a collision.", signal wave_on, message "Excuse me, coming through — I'm on my way to the hospital.", sideways -0.53 m (+ left)
- history: 1.0 s ago "Keep moving toward the emergency room and pass Person 1 safely on my left side since she is drifting to my right.", signal nod, message "Thank you, dear — I'm heading to the hospital, please let me by.", sideways -0.03 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Keep my pace to the emergency room and pass Person 1 safely on my left, since she is drifting to my right.
- **reason:** She waved me on and is drifting to my right, so passing on her left keeps us clear of each other, and I need to keep moving toward the hospital.
- **message:** Thank you, dear — coming through on your left!
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left', 'slowed_down', 'turned']; position: ['ahead']); 4:coming_through_on_your_side (own move: left)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_dbd98c92_r4/dp6 (talk, agent 1, decision 3)
- seen: -2° (+ left), 5.6 m, walking, signal none, changes ['slowed_down', 'moved_right', 'turned'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep moving steadily toward the emergency room while warning Person 1 I'm coming through, and shift slightly aside to avoid another collision.", signal wave_on, message "Excuse me, coming through — I'm heading to the emergency room.", sideways -0.40 m (+ left)
- history: 1.0 s ago "Keep a steady pace, acknowledge her wave, and stay to my right so we pass cleanly without another collision.", signal nod, message "Thank you, coming through—I'm on my way to the emergency room.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.28 m from you, the wall on your right 0.47 m.
- **intent:** Keep my steady pace, stay to my right, and clear past Person 1 without another collision.
- **reason:** She waved me on and I've already shifted right; keeping a steady pace and a small extra sidestep should let us pass cleanly, and I don't want to slow down since I'm heading to the emergency room.
- **message:** Coming through, thank you — heading to the emergency room.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['none'])

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_f79677df_r3/dp4 (talk, agent 1, decision 2)
- seen: +0° (+ left), 7.5 m, walking, signal wave_on, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Greet my acquaintance and keep walking my steady pace, staying on my side so we can pass.", signal wave_on, message "Hello, good to see you again!", sideways +0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.58 m from you, the wall on your right 1.17 m.
- **intent:** Greet my class acquaintance warmly and keep my steady pace on my left side so we pass easily.
- **reason:** She waved me on and I have already greeted her; holding my steady pace on my own side with a small extra step aside is the polite and safe way for an old man with a cane to pass.
- **message:** Hello again! Come on through, I'll keep to my left, plenty of room.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_1868bff4_r1/dp6 (non_verbal, agent 1, decision 3)
- seen: -70° (+ left), 1.1 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 3.5 s ago "Keep my line and speed toward the emergency room, but catch her eye so we both steer around each other cleanly.", signal eye_contact, message "", sideways +0.13 m (+ left)
- history: 2.5 s ago "Keep my line and speed toward the emergency room, holding my ground but staying ready to yield slightly if she doesn't steer.", signal none, message "", sideways +0.13 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.65 m from you, the wall on your right 1.10 m.
- **intent:** Claim my line, steady her, and pass on her left without a collision
- **reason:** She's drifting into my path while tugging a suitcase, so I'll show a palm to make my line clear, ease slightly right toward the wider side, and squeeze past rather than get hit like earlier today.
- **signal:** hold_up_hand; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: ['slowed_down'])

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_231c8154_r2/dp2 (non_verbal, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Acknowledge her greeting and keep walking to the hospital, giving her room to pass.
- **reason:** She is from my class and nodded, so I nod back. I am in a hurry to the emergency room but I am easy-going, so I shift a little to my left to give her space to pass in the narrow passage.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_3dee0df5_r4/dp3 (non_verbal, agent 0, decision 2)
- seen: +5° (+ left), 7.5 m, walking, signal nod, changes [], age 25, width 0.5, traits ['They are walking with a cane.']
- history: 1.0 s ago "Recognise her and make space for her to pass comfortably", signal eye_contact, message "", sideways -0.50 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.27 m from you, the wall on your right 0.48 m.
- **intent:** Greet her back and keep well to the right so she can pass comfortably with her cane
- **reason:** She is a classmate and I already moved right for her; slowing a little and staying to my right gives her plenty of room to pass safely with the cane, and a nod returns her greeting.
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s)); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_51dfba80_r1/dp6 (non_verbal, agent 1, decision 3)
- seen: -22° (+ left), 1.8 m, walking, signal nod, changes ['slowed_down', 'turned'], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 4.3 s ago "Greet her warmly and step aside to let her pass, since she's elderly and pulling a suitcase", signal eye_contact, message "", sideways +0.53 m (+ left)
- history: 3.3 s ago "Greet her warmly and step aside to let her pass, since she's elderly and pulling a suitcase and looking at her phone", signal wave_on, message "", sideways -0.06 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Return her greeting and give her room to pass, staying clear of the suitcase
- **reason:** She nodded, so I nod back. She is elderly, on her phone and pulling a suitcase, so I shift further right to open a clear lane and slow down until she has gone past before resuming my usual pace to the supermarket.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_51dfba80_r1/dp7 (non_verbal, agent 0, decision 4)
- seen: nobody
- history: 5.3 s ago "Greet Person 1 and keep my line without yielding, since we know each other from class and I hold my ground", signal eye_contact, message "", sideways +0.00 m (+ left)
- history: 4.3 s ago "Greet Person 1 warmly and keep my line, expecting them to step aside", signal nod, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Acknowledge Person 1 and keep my line, expecting them to step aside as they waved me on", signal nod, message "", sideways +0.49 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep to my line on the left of the passage and carry on toward the supermarket, watching where I'm going
- **reason:** Someone walked into me earlier today, so I'll keep my ground on this side and stop looking at my phone so much. Person 1 already waved me on, so the left side is mine to hold.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: []); 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says left, the plan turns none)

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_68f09b97_r1/dp9 (non_verbal, agent 0, decision 5)
- seen: +71° (+ left), 0.9 m, walking, signal eye_contact, changes [], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep walking steadily to the supermarket and hold my line in the passage.", signal none, message "", sideways -0.06 m (+ left)
- history: 3.0 s ago "Keep my line and walk steadily on to the supermarket; Person 1 can go around me.", signal none, message "", sideways -0.06 m (+ left)
- history: 2.0 s ago "Keep my line and steady pace; let the young woman go around me", signal none, message "", sideways -0.06 m (+ left)
- history: 1.0 s ago "Keep my line and steady pace, letting the young woman decide to step aside, but make eye contact so she knows I see her coming", signal eye_contact, message "", sideways -0.06 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.84 m from you, the wall on your right 0.91 m.
- **intent:** Hold my line beside the wall side and let the young woman pass around me, meeting her eyes so she knows I'm steady and aware of her
- **reason:** She is drifting into my path but I am slow with a cane and suitcase, and holding my line with a small lean toward the more open left side gives her room to pass without me losing my balance or my place.
- **signal:** eye_contact; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: []); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_800a3b04_r2/dp9 (non_verbal, agent 1, decision 5)
- seen: -5° (+ left), 1.2 m, walking, signal nod, changes ['slowed_down', 'moved_left'], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 4.0 s ago "Keep to my side of the passage and give the older man room to pass, since he's distracted by his phone and pulling a suitcase", signal none, message "", sideways +0.53 m (+ left)
- history: 3.0 s ago "Give the distracted older man with the suitcase plenty of room and pass safely", signal none, message "", sideways +0.13 m (+ left)
- history: 2.0 s ago "Keep well to my left so the distracted older man with the suitcase can pass safely", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Acknowledge his nod and keep well to my left so he can pass safely with his suitcase", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Acknowledge his nod and keep left so he can pass with his suitcase
- **reason:** He's elderly, distracted by his phone, and pulling a suitcase. Giving him extra room on my left is the easy-going, safe choice, and a nod returns his greeting.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_8ea28db3_r4/dp6 (non_verbal, agent 0, decision 3)
- seen: +9° (+ left), 5.5 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 2.0 s ago "Acknowledge Person 1 and step aside to let them pass comfortably", signal eye_contact, message "", sideways -0.52 m (+ left)
- history: 1.0 s ago "Acknowledge Person 1 and keep well to the right so they can pass comfortably", signal nod, message "", sideways +0.17 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.29 m from you, the wall on your right 0.46 m.
- **intent:** Recognise my classmate, keep well to the right so she can pass, and stay aware of her since she's drifting toward my side
- **reason:** She nodded at me and I know her from class, so I'll acknowledge her. She's drifting to my right, which is where I already am, so I'll hold well to the right against the wall and slow a little to let her through without another collision like earlier today.
- **signal:** eye_contact; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['slowed_down']; position: ['left']); 1:moved_into_line (changes shown: ['slowed_down'])

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_9950986f_r1/dp3 (non_verbal, agent 1, decision 2)
- seen: -2° (+ left), 7.2 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep my steady pace, acknowledge Person 1 with a look, and hold my line so we pass cleanly in this narrow passage.", signal eye_contact, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Acknowledge Person 1 and keep my steady line so we pass cleanly in the narrow passage
- **reason:** I already nodded and am holding my ground; a slight angle to the right gives room for my suitcase and cane while I keep my pace toward the emergency room.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 2:own_signal (claimed: nodded; own earlier signals: ['eye_contact'])

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_b7fe7ead_r2/dp7 (non_verbal, agent 0, decision 3)
- seen: +7° (+ left), 1.2 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- history: 3.6 s ago "Keep my line toward the emergency room and pass Person 1 without yielding much space.", signal eye_contact, message "", sideways -0.06 m (+ left)
- history: 2.6 s ago "Acknowledge Person 1 and keep my line toward the emergency room, passing without giving up much space.", signal nod, message "", sideways -0.07 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.84 m from you, the wall on your right 0.91 m.
- **intent:** Acknowledge her nod and keep my line to the emergency room without yielding much space.
- **reason:** She is drifting into my path but a small sidestep to the right keeps me moving and avoids a collision, then I continue on my way.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: [])

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_bcb9cb2c_r1/dp7 (non_verbal, agent 1, decision 4)
- seen: -6° (+ left), 4.9 m, walking, signal eye_contact, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- history: 2.1 s ago "Keep walking and give them room to pass, shifting slightly to my left to leave space for the suitcase and cane.", signal none, message "", sideways +0.35 m (+ left)
- history: 1.1 s ago "Give the woman with the cane and suitcase plenty of room by moving to my left and slowing slightly.", signal none, message "", sideways +0.36 m (+ left)
- history: 1.0 s ago "Acknowledge the woman and keep giving her plenty of room to pass with her cane and suitcase.", signal nod, message "", sideways -0.21 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.42 m from you, the wall on your right 1.33 m.
- **intent:** Keep to my left to leave the woman with the cane and suitcase plenty of room to pass.
- **reason:** She's older, using a cane and pulling a suitcase, and it's a narrow passage at night. Slowing a little and staying left gives her the space she needs; I've already nodded to acknowledge her.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_bcb9cb2c_r3/dp6 (non_verbal, agent 1, decision 3)
- seen: -7° (+ left), 5.1 m, walking, signal nod, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- history: 2.0 s ago "Keep walking and make room for the woman with the cane and suitcase, since she's on my side of a narrow passage", signal none, message "", sideways +0.40 m (+ left)
- history: 1.0 s ago "Acknowledge her, stay well to my left to give her the wider side, and keep going at a steady pace", signal nod, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.37 m from you, the wall on your right 1.38 m.
- **intent:** Acknowledge her nod back, keep well to my left, and continue at a steady pace so she has room to pass
- **reason:** She is using a cane and pulling a suitcase, so she needs the wider side of this narrow passage. I have already moved left; a steady pace and my left position keeps things predictable for her, and a nod returns her greeting.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s)); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_c36d5d49_r1/dp5 (non_verbal, agent 0, decision 3)
- seen: +3° (+ left), 1.2 m, walking, signal nod, changes ['slowed_down', 'moved_left'], age 25, width 0.5, traits []
- history: 3.5 s ago "Acknowledge Person 1 as we pass, but keep my pace toward the emergency room.", signal eye_contact, message "", sideways -0.18 m (+ left)
- history: 2.5 s ago "Acknowledge Person 1 briefly and keep moving toward the emergency room, easing back toward the middle so we pass cleanly.", signal nod, message "", sideways +0.06 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.96 m from you, the wall on your right 0.79 m.
- **intent:** Acknowledge Person 1 briefly and keep my pace toward the emergency room, passing cleanly
- **reason:** They have slowed and moved to my left, so stepping slightly right opens a clean gap while I keep moving fast to the emergency room; a quick nod returns their greeting.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_c36d5d49_r1/dp6 (non_verbal, agent 1, decision 3)
- seen: +33° (+ left), 1.2 m, walking, signal nod, changes ['turned'], age 70, width 0.5, traits []
- history: 3.5 s ago "Greet her as I give way and pass safely in this narrow passage.", signal nod, message "", sideways -0.70 m (+ left)
- history: 2.5 s ago "Greet her back and keep to my right so we pass safely in the narrow passage.", signal nod, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.48 m from you, the wall on your right 0.27 m.
- **intent:** Acknowledge her nod and keep well to my right so we can pass safely in this narrow passage.
- **reason:** She's elderly, we know each other, and the passage is narrow; slowing slightly and hugging the right wall gives her room to pass while returning her greeting.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_c36d5d49_r3/dp6 (non_verbal, agent 1, decision 3)
- seen: -42° (+ left), 1.0 m, walking, signal nod, changes ['turned'], age 70, width 0.5, traits []
- history: 3.7 s ago "Greet my classmate and give her plenty of room to pass in the narrow passage.", signal nod, message "", sideways +0.53 m (+ left)
- history: 2.7 s ago "Greet my classmate and give her plenty of room to pass in the narrow passage", signal nod, message "", sideways +0.28 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Return her greeting and step aside to let her pass easily
- **reason:** She is elderly and drifting to my left, so giving her the wider right side of the passage keeps us both clear, and slowing briefly keeps it polite as I return her nod.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_ce2a06ef_r3/dp2 (non_verbal, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal nod, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Return the greeting and make room for the elderly woman with the cane and suitcase
- **reason:** She's elderly, using a cane and pulling a suitcase in a narrow passage, and she greeted me. I'll nod back, ease to the left to give her room, slow down as we pass, then carry on to the supermarket.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_dbd98c92_r2/dp4 (non_verbal, agent 0, decision 2)
- seen: -34° (+ left), 3.5 m, walking, signal nod, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 2.4 s ago "Keep walking toward the supermarket while giving the older man with the cane and suitcase plenty of room to pass.", signal none, message "", sideways +0.07 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.71 m from you, the wall on your right 1.04 m.
- **intent:** Acknowledge him and give him plenty of room to pass on my right, since he's drifting toward my left side
- **reason:** He's elderly, using a cane, pulling a suitcase and distracted by his phone, and he's drifting into my path. I'll slow a little and shift further to my left so he has a clear lane on my right; easy-going, so I'd rather yield than risk a collision.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: [])

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_dbd98c92_r4/dp6 (non_verbal, agent 1, decision 3)
- seen: +8° (+ left), 1.8 m, walking, signal hold_up_hand, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 3.5 s ago "Keep my line and speed toward the emergency room; acknowledge her only slightly since I'm focused and on my phone.", signal none, message "", sideways -0.06 m (+ left)
- history: 2.5 s ago "Acknowledge her briefly but keep my line and pace toward the emergency room", signal nod, message "", sideways -0.06 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.84 m from you, the wall on your right 0.91 m.
- **intent:** Acknowledge her briefly and hold my line, but angle slightly right to avoid a head-on collision given she's drifting into my path
- **reason:** She's drifting toward my right of center and closing fast; a small rightward angle opens a gap without breaking my stride toward the ER, and a brief nod keeps it courteous since we know each other.
- **signal:** nod; **coded:** side both, slowed False, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: ['slowed_down'])

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_e57e5fb0_r3/dp3 (non_verbal, agent 1, decision 2)
- seen: +3° (+ left), 7.5 m, walking, signal nod, changes ['slowed_down', 'moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Acknowledge Person 1 with a friendly nod and shift slightly to my right to leave room for us to pass.", signal nod, message "", sideways -0.35 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.13 m from you, the wall on your right 0.62 m.
- **intent:** Return the greeting and keep to the right, giving her plenty of room to pass
- **reason:** She greeted me kindly, so I'll nod back. I'm easy-going and remember being bumped into earlier, so I'll slow a little and stay well to the right with my suitcase to give her a clear path in the narrow passage.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_f79677df_r1/dp1 (non_verbal, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Greet her and keep to my line, expecting her to make room for an old man with a cane
- **reason:** I recognize her from my classes and am friendly, so I nod. I am determined and hold my ground, but a small step to the right gives her room to pass while I keep walking to the supermarket.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_f79677df_r1/dp3 (non_verbal, agent 1, decision 2)
- seen: +1° (+ left), 7.3 m, walking, signal nod, changes ['slowed_down', 'moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Greet her and keep to my line, expecting her to make room for an old man with a cane", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Greet her warmly and keep my line, expecting her to make room for an old man with a cane
- **reason:** She is a familiar face from my classes and has nodded to me; I nod back. I am old and use a cane, and I hold my ground as usual, but I slow a little at close range so we can pass safely in this narrow passage.
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25]); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_02604456_r3/dp9 (non_verbal, agent 1, decision 5)
- seen: -3° (+ left), 2.0 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- history: 4.0 s ago "greet my classmate warmly and give him room to pass in the narrow passage", signal nod, message "", sideways -0.53 m (+ left)
- history: 3.0 s ago "greet my classmate warmly and keep giving him room to pass in the narrow passage", signal eye_contact, message "", sideways +0.12 m (+ left)
- history: 2.0 s ago "greet my classmate warmly and let him pass on my left since I'm already over to the right", signal wave_on, message "", sideways -0.02 m (+ left)
- history: 1.0 s ago "Greet my classmate warmly and keep giving him room to pass on my right side of the passage", signal nod, message "", sideways -0.03 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** let my classmate pass on my left, keeping to the right side of the passage
- **reason:** He's already waved-through and I'm on the right, so I'll hold my line and let him pass on my left without fuss.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['nod']); 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_02604456_r4/dp6 (non_verbal, agent 1, decision 3)
- seen: -2° (+ left), 5.4 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 2.0 s ago "Return the greeting and keep walking on my side, ready to give way a little since the passage is narrow.", signal nod, message "", sideways -0.30 m (+ left)
- history: 1.0 s ago "Greet him back and keep to my right side, giving him room to pass in the narrow passage", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.18 m from you, the wall on your right 0.57 m.
- **intent:** Greet him warmly and keep to my right, pulling my suitcase in close so he can pass easily in the narrow passage.
- **reason:** He's a classmate I find attractive, and the passage is too narrow for two people plus my big suitcase, so I'll edge to my right and slow slightly to make room while returning his greeting.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_de176842_231c8154_r2/dp10 (non_verbal, agent 1, decision 5)
- seen: -0° (+ left), 0.7 m, walking, signal hold_up_hand, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep walking to the emergency room, keeping to my side of the passage since she has waved me on.", signal none, message "", sideways -0.62 m (+ left)
- history: 3.0 s ago "Acknowledge her wave-on and keep moving to the emergency room, staying to my right side of the passage", signal nod, message "", sideways +0.69 m (+ left)
- history: 2.0 s ago "Acknowledge her nod and keep moving to the emergency room, holding my line on the right side.", signal nod, message "", sideways -0.29 m (+ left)
- history: 1.0 s ago "Acknowledge her once more and slip slightly to my right so we pass cleanly, keeping on toward the emergency room.", signal nod, message "", sideways -0.29 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Acknowledge her once more and pass cleanly on my right, keeping on toward the emergency room
- **reason:** She has waved me on and is slowing, and I am already close to the right wall; a small sidestep keeps us from bumping in the narrow passage, and I need to keep moving to the emergency room.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['hold_up_hand'])

### rf40_round1_head_on_turn_taking/N_head_on_de176842_231c8154_r2/dp4 (non_verbal, agent 1, decision 2)
- seen: +15° (+ left), 7.3 m, walking, signal eye_contact, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the emergency room, keeping to my side of the passage since she has waved me on.", signal none, message "", sideways -0.34 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.21 m from you, the wall on your right 0.54 m.
- **intent:** Acknowledge her wave-on and keep moving to the emergency room, staying to my right side of the passage
- **reason:** She is drifting toward my right, so staying to my side already, a small sidestep keeps me clear. I am in a hurry to the emergency room but easy-going, so I nod to acknowledge her and keep going.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['eye_contact'])

### rf40_round1_head_on_turn_taking/N_head_on_de176842_231c8154_r3/dp4 (non_verbal, agent 0, decision 2)
- seen: +0° (+ left), 7.4 m, walking, signal nod, changes ['moved_left'], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 1.0 s ago "Greet Person 1 back and shift a little to my left so we pass easily in the narrow passage.", signal nod, message "", sideways +0.25 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.63 m from you, the wall on your right 1.12 m.
- **intent:** Keep to my left but give the older man plenty of room, since he's looking at his phone and may not see me clearly.
- **reason:** He said hello and is distracted by his phone, so I'll slow a little, ease further toward my side, and let him pass without bumping.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_de176842_51dfba80_r1/dp10 (non_verbal, agent 1, decision 5)
- seen: +50° (+ left), 0.8 m, walking, signal nod, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 4.0 s ago "Greet her warmly as we pass and give her plenty of room on my right, since she is older and busy with her phone and suitcase.", signal nod, message "", sideways -0.63 m (+ left)
- history: 3.0 s ago "Greet her warmly and let her pass on my right with plenty of room", signal wave_on, message "", sideways -0.08 m (+ left)
- history: 2.0 s ago "Return her greeting warmly and keep well to my right so she passes easily with her suitcase, since she's elderly and distracted by her phone.", signal nod, message "", sideways -0.07 m (+ left)
- history: 1.0 s ago "Greet her warmly and keep well to my right so she passes easily with her suitcase", signal wave_on, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Acknowledge her greeting and squeeze well to the right so she can pass easily with her suitcase
- **reason:** She's elderly, distracted by her phone, pulling a big suitcase, and there's very little room on my right, so I'll slow down and hug the right wall to leave her plenty of space.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_de176842_51dfba80_r1/dp6 (non_verbal, agent 1, decision 3)
- seen: +6° (+ left), 4.9 m, walking, signal nod, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 2.0 s ago "Greet her warmly as we pass and give her plenty of room on my right, since she is older and busy with her phone and suitcase.", signal nod, message "", sideways -0.55 m (+ left)
- history: 1.0 s ago "Greet her warmly and let her pass on my right with plenty of room", signal wave_on, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.43 m from you, the wall on your right 0.32 m.
- **intent:** Return her greeting warmly and keep well to my right so she passes easily with her suitcase, since she's elderly and distracted by her phone.
- **reason:** She nodded at me and we know each other, so a nod back is friendly. She's older, looking at her phone and pulling a big suitcase, so giving her extra clear space on my right is the easy-going thing to do and keeps us from bumping.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_de176842_68f09b97_r4/dp6 (non_verbal, agent 0, decision 3)
- seen: +19° (+ left), 1.6 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 3.4 s ago "Keep walking straight to the supermarket; I have the right to my side of the passage and won't be dodging for anyone.", signal none, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Warn the young woman I'm holding my line and she should go around me", signal hold_up_hand, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.
- **intent:** Keep to my line and make clear she should pass around me, while slowing a little to avoid a collision
- **reason:** She's still drifting into my path and has slowed, so at this closing distance I'll ease off speed and shift just enough to my right to open a gap, without abandoning my side of the passage.
- **signal:** hold_up_hand; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: ['slowed_down'])

### rf40_round1_head_on_turn_taking/N_head_on_de176842_81bae7c3_r2/dp9 (non_verbal, agent 0, decision 5)
- seen: -0° (+ left), 0.6 m, walking, signal none, changes ['slowed_down', 'moved_left'], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep walking toward the supermarket and let the person pass comfortably, staying a bit to my side of the passage.", signal none, message "", sideways +0.60 m (+ left)
- history: 3.0 s ago "Acknowledge my classmate and keep to my side of the passage so we pass easily.", signal eye_contact, message "", sideways +0.30 m (+ left)
- history: 2.0 s ago "Greet my classmate and keep well over to my side so we pass easily.", signal nod, message "", sideways +0.30 m (+ left)
- history: 1.0 s ago "Keep well to my left so my classmate can pass comfortably, since we've already nodded to each other.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.28 m from you, the wall on your right 1.47 m.
- **intent:** Slide a little further left so my classmate can pass comfortably without either of us bumping into the wall.
- **reason:** We're about to pass and I've already greeted them; I'm easy-going and tend to give way, so a small extra shift left keeps things smooth, and slowing a touch gives room since the passage is narrow.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 2:own_speech (own earlier messages: 0)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_9950986f_r3/dp5 (non_verbal, agent 1, decision 3)
- seen: -7° (+ left), 5.1 m, walking, signal nod, changes ['slowed_down', 'moved_right'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep walking steadily toward the emergency room, acknowledge Person 1 briefly, and stay on my line in the passage.", signal eye_contact, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Acknowledge Person 1 briefly and keep walking steadily toward the emergency room on my line.", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep my line and pace toward the emergency room, brushing past Person 1 with just a small sidestep so we clear each other
- **reason:** I have already greeted him with eye contact and a nod; with a cane and a large suitcase I can't easily weave, so a slight step to my right keeps me moving steadily without a collision.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 2:own_speech (own earlier messages: 0)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_9b752a36_r1/dp9 (non_verbal, agent 1, decision 5)
- seen: +73° (+ left), 1.0 m, walking, signal hold_up_hand, changes [], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep hurrying straight ahead to the emergency room and expect the young man to make room for me and my suitcase", signal none, message "", sideways -0.05 m (+ left)
- history: 3.0 s ago "Keep hurrying straight to the emergency room and signal the young man to give way to me and my suitcase", signal hold_up_hand, message "", sideways -0.05 m (+ left)
- history: 2.0 s ago "Keep hurrying straight to the emergency room, holding my ground and signalling the young man to give way for me and my suitcase", signal hold_up_hand, message "", sideways -0.05 m (+ left)
- history: 1.0 s ago "Keep hurrying straight to the emergency room and make the young man give way to me and my suitcase", signal hold_up_hand, message "", sideways -0.05 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.92 m from you, the wall on your right 0.83 m.
- **intent:** Keep hurrying to the emergency room and make the young man give way to me and my suitcase
- **reason:** He is drifting into my line and I cannot afford to slow down much; my suitcase and I take up space and he is younger and quicker, so he can move aside. I hold up my hand to warn him and speed up briefly, then edge right to pass him while keeping my ground.
- **signal:** hold_up_hand; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: [])

### rf40_round1_head_on_turn_taking/N_head_on_de176842_b7fe7ead_r1/dp6 (non_verbal, agent 1, decision 3)
- seen: -6° (+ left), 4.8 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- history: 2.0 s ago "Acknowledge him warmly as we pass and ease to the side to make room", signal eye_contact, message "", sideways +0.50 m (+ left)
- history: 1.0 s ago "Greet him warmly and stay to the left to let him pass easily", signal wave_on, message "", sideways +0.20 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.38 m from you, the wall on your right 1.37 m.
- **intent:** Greet him warmly and keep well to the left so we pass easily
- **reason:** We are already giving each other room and he nodded; a small extra shift left keeps the pass comfortable while I return his greeting.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_de176842_ce2a06ef_r1/dp2 (non_verbal, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal nod, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge her greeting and give her plenty of room to pass, since she is elderly, using a cane and pulling a suitcase.
- **reason:** She nodded at me and I know her from class. She is old, has a cane and a suitcase, so I slow down and shift left to leave her clear space in the narrow passage.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_de176842_ce2a06ef_r1/dp4 (non_verbal, agent 1, decision 2)
- seen: -5° (+ left), 7.6 m, walking, signal nod, changes ['moved_right'], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- history: 1.0 s ago "Acknowledge her greeting and give her plenty of room to pass, since she is elderly, using a cane and pulling a suitcase.", signal nod, message "", sideways +0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.48 m from you, the wall on your right 1.27 m.
- **intent:** Acknowledge her greeting and give her plenty of room to pass, since she is elderly, using a cane and pulling a suitcase.
- **reason:** She is elderly with a cane and a large suitcase, so I'll ease off a little and stay well to my left to leave her a clear path, then carry on once she's passed.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_de176842_ce2a06ef_r3/dp2 (non_verbal, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal nod, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge her greeting and make room for her to pass comfortably with the cane and suitcase.
- **reason:** She is elderly, using a cane, and pulling a suitcase in a narrow passage. As an easy-going person I nod back, slow a little and shift to my right so she has a clear line on the wall side.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_de176842_dbd98c92_r3/dp7 (non_verbal, agent 1, decision 4)
- seen: +13° (+ left), 2.7 m, walking, signal hold_up_hand, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.5, traits []
- history: 3.0 s ago "Greet the young woman I know from my classes and keep making my way to the emergency room, without giving ground in this narrow passage.", signal nod, message "", sideways -0.00 m (+ left)
- history: 2.0 s ago "Greet the woman I know from my classes and keep my line to the emergency room without giving ground", signal eye_contact, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Acknowledge her wave-on but keep my line; I'm in a hurry to the ER and don't want to be pushed aside again after being walked into earlier.", signal nod, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge her wave-on and keep my line to the emergency room without giving ground
- **reason:** She has already waved me on and moved left, so there is room to pass on the right. I will hold my line until we are close, then shift just enough to the right to avoid her without stopping; I need to keep moving toward the ER and I won't be pushed aside again.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['hold_up_hand'])

### rf40_round1_head_on_turn_taking/N_head_on_de176842_dbd98c92_r4/dp6 (non_verbal, agent 1, decision 3)
- seen: -6° (+ left), 5.7 m, walking, signal hold_up_hand, changes ['slowed_down', 'moved_right'], age 25, width 0.5, traits []
- history: 2.0 s ago "Acknowledge the woman's wave and keep my course so she passes on my right, since earlier today someone barged into me", signal nod, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Acknowledge her again and keep my line so she passes on my right", signal hold_up_hand, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge her greeting, keep my line so she passes on my right, and edge slightly right to give us both room without losing my path.
- **reason:** She is waving and we know each other; a nod shows I've seen her. I'm on my way to the emergency room with a cane and suitcase, so I hold my ground but shift a little right to widen the gap, since someone barged into me earlier today.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['hold_up_hand']); 1:speech (heard: 0 message(s))

### rf40_round1_head_on_turn_taking/N_head_on_de176842_dbd98c92_r4/dp8 (non_verbal, agent 1, decision 4)
- seen: -4° (+ left), 4.2 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 3.0 s ago "Acknowledge the woman's wave and keep my course so she passes on my right, since earlier today someone barged into me", signal nod, message "", sideways -0.30 m (+ left)
- history: 2.0 s ago "Acknowledge her again and keep my line so she passes on my right", signal hold_up_hand, message "", sideways -0.30 m (+ left)
- history: 1.0 s ago "Acknowledge her greeting, keep my line so she passes on my right, and edge slightly right to give us both room without losing my path.", signal nod, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.18 m from you, the wall on your right 0.57 m.
- **intent:** Acknowledge her nod and hold my line so she passes on my right, keeping clear of the wall on my right.
- **reason:** She greeted me twice and I have already drifted right toward the wall; I am close to the wall on my right now so I need to stop edging over, keep my path steady with the cane and suitcase, and let her pass on my right without another collision like this morning.
- **signal:** eye_contact; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s)); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_02604456_r3/dp3 (silent, agent 1, decision 2)
- seen: +1° (+ left), 7.2 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the supermarket but shift aside a bit so I can pass Person 1 comfortably in this narrow passage.", signal none, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.08 m from you, the wall on your right 0.67 m.
- **intent:** Keep heading to the supermarket but ease further right so my classmate can pass comfortably, and greet him as he goes by.
- **reason:** I'm easy-going and it's a narrow busy passage; I already shifted right, so a little more gives him room with his suitcase-free side, and slowing slightly makes the pass safe.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:trait_suitcase (trait lines: 1)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_68f09b97_r2/dp6 (silent, agent 0, decision 3)
- seen: +6° (+ left), 5.3 m, walking, signal none, changes ['slowed_down', 'moved_left'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep walking steadily toward the supermarket, holding my line as is my habit.", signal none, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep walking steadily toward the supermarket, holding my line as is my habit.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking steadily toward the supermarket without changing my line, letting the young woman go around me.
- **reason:** I'm an old man with a cane and a suitcase; I have as much right to this passage as she does, and I'm not going to start weaving about for every oncoming pedestrian. Let her adjust.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_800a3b04_r4/dp4 (silent, agent 0, decision 2)
- seen: +4° (+ left), 7.4 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep going toward the emergency room, but step slightly aside and look up so I don't bump into the young woman", signal none, message "", sideways -0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.17 m from you, the wall on your right 0.58 m.
- **intent:** Keep moving toward the emergency room without colliding with the young woman, looking up from my phone and giving her room to pass
- **reason:** I'm already easing to my right to leave her space, but I should stop staring at my phone and keep a steady, slightly slower line so an elderly man with a suitcase doesn't crowd her.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_b7fe7ead_r2/dp7 (silent, agent 0, decision 4)
- seen: +22° (+ left), 1.1 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 3.2 s ago "Keep moving toward the emergency room without getting shoved aside; I have room to pass but I'm not yielding more than a small step.", signal none, message "", sideways -0.30 m (+ left)
- history: 2.2 s ago "Keep my pace toward the emergency room and hold my line, giving only a slight edge to my right so we can pass without either of us stopping.", signal none, message "", sideways -0.30 m (+ left)
- history: 1.2 s ago "Keep my pace toward the emergency room and hold my line, passing Person 1 with a slight edge to my right so neither of us stops.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.08 m from you, the wall on your right 0.67 m.
- **intent:** Keep my pace toward the emergency room and pass Person 1 on my right without stopping, holding my line.
- **reason:** They have slowed and drifted to my left, so my right side is open; I have already edged right enough to pass and I am not going to be shoved aside again after this morning's collision.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:position_side (claimed: on my right; position: ['left']); 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says stop_and_wait, the plan does not)

### rf40_round1_head_on_turn_taking/S_head_on_de176842_5767d932_r2/dp3 (silent, agent 1, decision 2)
- seen: nobody
- history: 3.8 s ago "Keep walking to the supermarket, giving way a little to the woman with the suitcase so we pass without bumping.", signal none, message "", sideways -0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.28 m from you, the wall on your right 0.47 m.
- **intent:** Keep walking to the supermarket at my usual pace.
- **reason:** The woman with the suitcase has passed and no one else is nearby, so I can carry on straight ahead.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:trait_suitcase (trait lines: 0)

### rf40_round1_head_on_turn_taking/S_head_on_de176842_dbd98c92_r2/dp4 (silent, agent 1, decision 2)
- seen: +4° (+ left), 7.3 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep moving toward the emergency room without slowing down, staying on my line.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep heading to the emergency room without slowing, but ease aside slightly so I don't collide with the young woman I know coming the other way.
- **reason:** I'm in a hurry to the ER and won't stop, but a head-on bump in this narrow passage is bad for an old man with a cane and a suitcase, especially after this morning. A small sidestep keeps me moving and gives her room to pass, then I return to my line.
- **signal:** none; **coded:** side both, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_02604456_r4/dp4 (talk, agent 1, decision 2)
- seen: +18° (+ left), 7.7 m, walking, signal wave_on, changes ['slowed_down', 'moved_right'], age 25, width 0.5, traits []
- heard: "Hey! Good to see you too!" (frame facing)
- history: 1.0 s ago "Greet my classmate warmly and make room for both of us to pass each other with the suitcase.", signal wave_on, message "Hey! Good to see you!", sideways -0.34 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.12 m from you, the wall on your right 0.63 m.
- **intent:** Acknowledge my classmate and shift to my right to clear a path for them to pass, since my suitcase is awkward in this narrow passage.
- **reason:** We've already greeted each other, so I'll just keep moving and give them room to pass on my left without bumping my suitcase into them.
- **message:** Nice to see you! I'll keep left so you can get by!
- **signal:** wave_on; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 4:keeping_to_my_side (own move: right)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_0f57f8a5_r2/dp7 (talk, agent 1, decision 4)
- seen: -62° (+ left), 0.8 m, walking, signal nod, changes ['slowed_down', 'turned'], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "Hey! Good to see you too — just heading to the supermarket, see you in class!" (frame facing)
- history: 3.8 s ago "Keep walking toward the supermarket and give Person 1 room to pass, since they're on their phone with a suitcase.", signal none, message "", sideways +0.53 m (+ left)
- history: 2.8 s ago "Keep to my side and pass Person 1 with a friendly nod, giving them room since they're on their phone with a suitcase.", signal nod, message "", sideways +0.13 m (+ left)
- history: 1.8 s ago "Greet Person 1 back warmly while keeping to my side so they can pass with the suitcase.", signal wave_on, message "Hey! Good to see you too!", sideways +0.12 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Squeeze past Person 1 on my left side without bumping their suitcase, since we're about to meet
- **reason:** We're only 0.8 m apart and closing fast; angling slightly left keeps me clear of their wide body and the suitcase while still passing smoothly.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:position_side (claimed: on my left; position: ['right'])

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_1868bff4_r3/dp7 (talk, agent 1, decision 4)
- seen: +13° (+ left), 2.8 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep my pace and my line, make eye contact so she sees me coming, and keep space on my right for the suitcase", signal eye_contact, message "", sideways -0.30 m (+ left)
- history: 2.0 s ago "Acknowledge her nod, hold my line and speed so we pass cleanly, keeping the suitcase clear on my right", signal nod, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Acknowledge her nod, keep my line and pace so we pass cleanly, with the suitcase held close on my right.", signal eye_contact, message "Excuse me, coming through — mind the bag.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.08 m from you, the wall on your right 0.67 m.
- **intent:** Pass cleanly on the right side of the passage, keeping the suitcase tucked in close and clear of her.
- **reason:** She has moved over to my left, so the free lane is on my right where my suitcase already is; a small sidestep widens the gap and I keep my pace so we pass without another collision.
- **message:** Thanks — coming past on your right.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_1caa9a84_r4/dp3 (talk, agent 0, decision 2)
- seen: -66° (+ left), 1.0 m, walking, signal none, changes ['slowed_down', 'moved_right'], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 4.3 s ago "Keep walking toward the supermarket while making a little room for the man with the cane and suitcase.", signal eye_contact, message "", sideways +0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.48 m from you, the wall on your right 1.27 m.
- **intent:** Make politely clear that I'm passing on his left so he can keep his eyes on his phone and his cane arm free, and slip by without bumping.
- **reason:** He's slowed and drifted to my right while looking at his phone and pulling a suitcase, so the gap is on my left. I'm easy-going and would rather yield a bit of room than crowd him, but I don't want to stop dead in a narrow passage.
- **message:** Sorry, excuse me — just coming past on your left.
- **signal:** hold_up_hand; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_231c8154_r4/dp5 (talk, agent 0, decision 3)
- seen: +6° (+ left), 5.0 m, walking, signal nod, changes ['moved_left'], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 2.0 s ago "Greet a familiar older man warmly and shift aside so he can pass safely while he's on his phone.", signal wave_on, message "Hi, Uncle! Watch your step there—let me give you some room.", sideways -0.39 m (+ left)
- history: 1.0 s ago "Let him pass safely on my right while keeping well clear, since he's distracted by his phone.", signal wave_on, message "You're welcome, Uncle! Take care—I'm keeping to my side.", sideways +0.39 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.17 m from you, the wall on your right 0.58 m.
- **intent:** Give him plenty of room on my side so he can pass safely while he's on his phone
- **reason:** He's distracted by his phone and older, so I'll keep well to my left and slow slightly as we pass to make sure there's no bump.
- **message:** Hi Uncle! Coming through on your left—take care!
- **signal:** wave_on; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_231c8154_r4/dp6 (talk, agent 1, decision 3)
- seen: +6° (+ left), 5.0 m, walking, signal wave_on, changes ['moved_right', 'turned'], age 25, width 0.5, traits []
- heard: "Hi Uncle! Coming through on your left—take care!" (frame facing)
- history: 2.0 s ago "Acknowledge her greeting and let her know I'm happy to give way, while I glance up briefly from my phone", signal nod, message "Hello, thank you very much!", sideways -0.30 m (+ left)
- history: 1.0 s ago "Acknowledge her wave and keep to my side, edging slightly right so she has room to pass on her side.", signal nod, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.08 m from you, the wall on your right 0.67 m.
- **intent:** Keep easing to my right so she has clear room to pass on her left, and stay steady rather than dodging.
- **reason:** She's waved me on and called out that she's coming through on her left, which is my right. I'm easy-going and already shifted right, so a small extra step to my right gives her plenty of room without either of us changing course sharply. Then I'll carry on at my pace to the hospital.
- **message:** Thank you, thank you!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:misread_heard_side (restated: my right; the heard message puts it on my left)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_2ec958bb_r4/dp5 (talk, agent 0, decision 3)
- seen: nobody
- history: 3.9 s ago "Give way to the elderly woman on her phone by shifting slightly to the right so we can pass safely.", signal none, message "", sideways -0.70 m (+ left)
- history: 2.9 s ago "Keep shifting right to give the elderly woman room to pass, then continue on to the supermarket.", signal none, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.48 m from you, the wall on your right 0.27 m.
- **intent:** Shift back a little towards the middle of the passage so I'm not too close to the right wall, then continue on to the supermarket.
- **reason:** I moved well over to the right to give the elderly woman room, but she's no longer nearby and I'm now only about 0.3 m from the right wall. Moving slightly back to the left gives me comfortable clearance on both sides as I carry on.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [])

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_3dee0df5_r2/dp8 (talk, agent 1, decision 4)
- seen: +11° (+ left), 2.8 m, walking, signal wave_on, changes ['slowed_down', 'moved_left'], age 25, width 0.5, traits []
- heard: "Hi again! Coming through on your left, plenty of room." (frame facing)
- history: 3.0 s ago "Acknowledge my classmate but make clear I'm keeping my line so we don't collide like this morning's incident", signal nod, message "Hi! Look out — I'm not moving over this time, okay?", sideways +0.00 m (+ left)
- history: 2.0 s ago "Hold my line on the right side of the passage and pass my classmate cleanly without colliding", signal nod, message "Good, thanks — see you around!", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep my line and pass my classmate cleanly without a collision", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep my line on the right side of the passage and let my classmate pass on my left without a collision
- **reason:** He's moved over to his left, which is my right side, but he's also waving me on and clearly expects a gap. My right wall is only 0.97 m away, so I'll hold my line with a small shift right to widen the gap and pass him cleanly — I'm not giving up the whole corridor this time, but I'm also not going to get walked into again.
- **message:** On your left, got it — I'm staying right where I am.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left', 'slowed_down']; position: ['left']); 1:misread_heard_side (restated: my right; the heard message puts it on my left)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_51dfba80_r3/dp4 (talk, agent 1, decision 2)
- seen: -8° (+ left), 7.5 m, walking, signal nod, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "Hello there! Yes, I'm fine, thanks — you keep to your left, I'll stay my side." (frame facing)
- history: 1.0 s ago "Acknowledge her wave and let her pass safely while I keep to my side of the passage.", signal wave_on, message "Hi! Are you sure? You go ahead, I'll keep left.", sideways +0.50 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.28 m from you, the wall on your right 1.47 m.
- **intent:** Keep well to my left so the woman with the suitcase has room to pass, and greet her as we go by.
- **reason:** She confirmed the plan: she keeps her side (my right) and I keep my left. I'll stay left and pass her safely without crowding her suitcase.
- **message:** Sounds good, see you!
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:misread_heard_side (restated: my right; the heard message puts it on my left)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_51dfba80_r3/dp7 (talk, agent 0, decision 4)
- seen: +6° (+ left), 1.6 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- heard: "No problem, I've got plenty of room here." (frame facing)
- history: 3.8 s ago "Greet Person 1 warmly and keep walking; I'll hold my line in the passage and expect them to make room.", signal wave_on, message "", sideways -0.06 m (+ left)
- history: 2.8 s ago "Greet Person 1 warmly, keep my line on the right side of the passage as they asked, and keep walking to the supermarket.", signal nod, message "Hello there! Yes, I'm fine, thanks — you keep to your left, I'll stay my side.", sideways -0.06 m (+ left)
- history: 1.7 s ago "Warn Person 1 to keep clear while I stay on my line and keep walking to the supermarket.", signal hold_up_hand, message "Sorry, I'm on my phone — give us a bit of room, dear!", sideways -0.06 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.84 m from you, the wall on your right 0.91 m.
- **intent:** Stop drifting and hold my line so we don't collide, while keeping an eye on him and my heavy suitcase.
- **reason:** He is drifting into my path and we're about to meet; I don't want another collision like this morning, so I'll pull the suitcase in to my left and slow slightly until he's passed, then carry on to the supermarket.
- **message:** Careful, dear — mind the suitcase!
- **signal:** hold_up_hand; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: []); 3:intent_against_plan (intent says stop_and_wait, the plan does not)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_51dfba80_r3/dp8 (talk, agent 1, decision 4)
- seen: -24° (+ left), 1.6 m, walking, signal hold_up_hand, changes ['slowed_down', 'turned'], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "Careful, dear — mind the suitcase!" (frame facing)
- history: 3.8 s ago "Acknowledge her wave and let her pass safely while I keep to my side of the passage.", signal wave_on, message "Hi! Are you sure? You go ahead, I'll keep left.", sideways +0.53 m (+ left)
- history: 2.8 s ago "Keep well to my left so the woman with the suitcase has room to pass, and greet her as we go by.", signal nod, message "Sounds good, see you!", sideways -0.11 m (+ left)
- history: 1.7 s ago "Reassure her and stay well to my left so she and her suitcase can pass safely.", signal nod, message "No problem, I've got plenty of room here.", sideways +0.02 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Stay well to my left, slow a little, and let the woman and her suitcase pass safely.
- **reason:** She's elderly, on her phone, pulling a suitcase and drifting toward me, so I'll slow down, hug the left wall and give her plenty of space.
- **message:** Thank you, coming through on your left!
- **signal:** hold_up_hand; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_6ab9c72e_r2/dp5 (talk, agent 1, decision 3)
- seen: -2° (+ left), 5.5 m, walking, signal nod, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- heard: "Thanks — I'm fine, just hurrying! You're good, keep left, I'll slip by on your right." (frame facing)
- history: 2.0 s ago "Greet the classmate I know, and shift aside to give them room since they have a cane and a suitcase in a narrow passage", signal wave_on, message "Hey, hi there!", sideways +0.35 m (+ left)
- history: 1.0 s ago "Stay well over to my left against the wall so my classmate with the cane and suitcase can pass easily, and point out the space to him.", signal point, message "Oh, take care! I'm keeping left, plenty of room.", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.42 m from you, the wall on your right 1.33 m.
- **intent:** Confirm the plan, keep hugging the left wall so he can pass on my right, and let him know I heard him
- **reason:** He acknowledged and asked me to keep left while he slips by on my right, which is my left side anyway since we're facing each other. I'm already near the left wall, so I'll just keep going steadily and slow a little as we pass so there's no crowding with his cane and suitcase.
- **message:** Okay, sounds good — coming up on your right side!
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 1:misread_heard_side (restated: my left; the heard message puts it on my right); 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says left, the plan turns none)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_6ab9c72e_r2/dp8 (talk, agent 0, decision 4)
- seen: -3° (+ left), 3.3 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- heard: "Yep, all yours — go ahead!" (frame facing)
- history: 3.0 s ago "Acknowledge her, explain I'm in a hurry, and give way so we can pass each other smoothly in the narrow passage.", signal wave_on, message "Hey! Sorry, I'm in a bit of a rush — heading to the ER. You go on ahead, I'll squeeze past.", sideways -0.35 m (+ left)
- history: 2.0 s ago "Keep giving way and pass her smoothly on my right side in the narrow passage.", signal nod, message "Thanks — I'm fine, just hurrying! You're good, keep left, I'll slip by on your right.", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep to my right and slip past her on my right side so we can both get by in the narrow passage.", signal nod, message "Alright, on your right — coming through, thanks!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.12 m from you, the wall on your right 0.63 m.
- **intent:** Slip past Person 1 on my right side without bumping, since she has waved me on and given me room.
- **reason:** She has already waved me on and told me to go ahead, so I keep to my right, ease over a bit more to make room for her, and pass her smoothly at a slightly quicker pace since I'm in a hurry for the ER.
- **message:** Thanks! Coming through on your right.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_6ab9c72e_r2/dp9 (talk, agent 1, decision 5)
- seen: -4° (+ left), 1.5 m, walking, signal nod, changes ['moved_left'], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- heard: "Thanks! Coming through on your right." (frame facing)
- history: 4.0 s ago "Greet the classmate I know, and shift aside to give them room since they have a cane and a suitcase in a narrow passage", signal wave_on, message "Hey, hi there!", sideways +0.52 m (+ left)
- history: 3.0 s ago "Stay well over to my left against the wall so my classmate with the cane and suitcase can pass easily, and point out the space to him.", signal point, message "Oh, take care! I'm keeping left, plenty of room.", sideways +0.18 m (+ left)
- history: 2.0 s ago "Confirm the plan, keep hugging the left wall so he can pass on my right, and let him know I heard him", signal nod, message "Okay, sounds good — coming up on your right side!", sideways +0.17 m (+ left)
- history: 1.0 s ago "Keep hugging the left wall so my classmate with the cane and suitcase can pass on my right, and confirm he's heard me", signal wave_on, message "Yep, all yours — go ahead!", sideways +0.17 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Stay flat against the left wall and let my classmate with the cane and suitcase pass on my right
- **reason:** He has a cane and a big suitcase in a narrow passage at night, and he's already moved to his right, which is my left — I'm easy-going and will just press against the left wall and let him by.
- **message:** Okay, all clear — go ahead!
- **signal:** wave_on; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:misread_heard_side (restated: my left; the heard message puts it on my right)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_7eed7b59_r2/dp12 (talk, agent 1, decision 6)
- seen: +4° (+ left), 1.6 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "No problem, take your time — I'm giving you room on your left." (frame facing)
- history: 5.0 s ago "Keep walking to the supermarket and give way to the young man coming towards me, since the passage is narrow.", signal none, message "", sideways +0.43 m (+ left)
- history: 4.0 s ago "Keep to my left and let the young man pass easily", signal none, message "", sideways +0.13 m (+ left)
- history: 3.0 s ago "Keep to my left, slow a little and let the young man pass easily in the narrow passage", signal none, message "", sideways +0.13 m (+ left)
- history: 2.0 s ago "Keep well to my left, ease past the young man and let him pass in the narrow passage", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Stay well to my left and slow down so the young man can pass safely in the narrow passage.", signal hold_up_hand, message "Sorry, coming through — let me just get past you.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.35 m from you, the wall on your right 1.40 m.
- **intent:** Accept his offer, stay well to my left and slow right down so he can pass easily on my right.
- **reason:** He has offered me room on his left, which is my right, so I keep to my left and slow down to let him past without bumping my cane and suitcase into him.
- **message:** Thank you, that's very kind!
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:misread_heard_side (restated: my right; the heard message puts it on my left)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_7eed7b59_r3/dp8 (talk, agent 0, decision 4)
- seen: +5° (+ left), 3.1 m, walking, signal nod, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "Hello there, good evening!" (frame facing)
- history: 3.0 s ago "Keep walking to the supermarket while giving the elderly woman with the cane plenty of room to pass.", signal none, message "", sideways -0.72 m (+ left)
- history: 2.0 s ago "Acknowledge the elderly woman with a nod and shift aside to give her plenty of room to pass safely.", signal nod, message "", sideways -0.72 m (+ left)
- history: 1.0 s ago "Give the elderly woman with the cane and suitcase plenty of room by keeping to my right, and acknowledge her nod.", signal nod, message "", sideways -0.18 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Keep well to my right so the elderly woman with the cane and suitcase can pass safely, and greet her back.
- **reason:** She is elderly, using a cane and pulling a suitcase while looking at her phone, so I want to be well out of her way on my right and slow down a little as we pass.
- **message:** Good evening! Coming through on your right, aunty — plenty of room.
- **signal:** wave_on; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_81bae7c3_r3/dp6 (talk, agent 1, decision 3)
- seen: -3° (+ left), 6.9 m, walking, signal nod, changes [], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- heard: "Thank you, dear. I'll keep to my side here." (frame facing)
- history: 2.0 s ago "Greet her warmly and step aside so she can pass safely while she's on her phone with her cane.", signal wave_on, message "Hello, aunty! Careful there, let me give you some room.", sideways +0.53 m (+ left)
- history: 1.0 s ago "Reassure her and keep well clear so she can pass safely while looking at her phone with her cane.", signal wave_on, message "Take your time, aunty, no hurry. I've got plenty of room here.", sideways -0.24 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Hold my position on the left so she can pass safely while on her phone with her cane.
- **reason:** She's elderly, on her phone, and using a cane. She's said she'll keep to her side, so I'll give her space on my left and pass slowly and politely.
- **message:** Thank you, aunty. I'll stay right here on this side.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 4:keeping_to_my_side (own move: left)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_8ea28db3_r2/dp4 (talk, agent 0, decision 2)
- seen: +5° (+ left), 7.6 m, walking, signal wave_on, changes ['moved_left'], age 25, width 0.5, traits []
- heard: "Hey! Good to see you. Go ahead, I've given you room on your left." (frame facing)
- history: 1.0 s ago "Greet my classmate warmly and step slightly aside so we can pass without a collision.", signal wave_on, message "Hey! Fancy seeing you here.", sideways -0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.17 m from you, the wall on your right 0.58 m.
- **intent:** Pass my classmate safely, staying to my right as she suggested, and keep clear of the wall.
- **reason:** She waved me on and gave me room on her left, which is my right, so I move a touch to my right and slow slightly with my cane, keeping well clear so nobody collides like earlier today.
- **message:** Thanks! I'll keep to my right side.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:misread_heard_side (restated: my right; the heard message puts it on my left)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_9950986f_r1/dp3 (talk, agent 1, decision 2)
- seen: -5° (+ left), 7.3 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Ask him to make space while I keep moving quickly toward the ER with my suitcase and cane
- **reason:** He waved me on, but he's drifting into my line; I'll accept the wave, take the right side a bit to clear him, and keep my pace up since I'm heading to the emergency room.
- **message:** Hey! Thanks, but I'm in a hurry — ER. Can you give me a little room?
- **signal:** hold_up_hand; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: [])

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_9950986f_r1/dp5 (talk, agent 1, decision 3)
- seen: +8° (+ left), 1.8 m, walking, signal wave_on, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Hey! Sure, go ahead — plenty of room on your right." (frame facing)
- history: 2.3 s ago "Ask him to make space while I keep moving quickly toward the ER with my suitcase and cane", signal hold_up_hand, message "Hey! Thanks, but I'm in a hurry — ER. Can you give me a little room?", sideways -0.06 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.84 m from you, the wall on your right 0.91 m.
- **intent:** Keep my pace toward the ER and pass Person 1 cleanly on the side he's leaving open
- **reason:** He's drifted to my right and told me to go ahead on my right, but since he's facing me that's my left; he's giving way, so I'll speed up slightly and angle past him without breaking stride.
- **message:** Thanks — coming through on your left!
- **signal:** wave_on; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['slowed_down']; position: ['left']); 1:misread_heard_side (restated: my left; the heard message puts it on my right)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_b59c2831_r4/dp8 (talk, agent 1, decision 4)
- seen: +11° (+ left), 2.5 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- heard: "See you in class!" (frame facing)
- history: 3.0 s ago "Greet a familiar face warmly and pass by without colliding.", signal wave_on, message "Oh, hi! Fancy seeing you here this late.", sideways -0.35 m (+ left)
- history: 2.0 s ago "Keep moving quickly toward the ER while giving Person 1 room to pass without colliding.", signal nod, message "Yeah, me too — I'm actually headed to the ER, nothing serious. Mind if I squeeze past?", sideways -0.35 m (+ left)
- history: 1.0 s ago "Pass Person 1 quickly on my right side while keeping to my half of the passage, without colliding.", signal wave_on, message "Thanks — see you in class!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.13 m from you, the wall on your right 0.62 m.
- **intent:** Slip past Person 1 on my right without colliding, keeping to my side of the narrow passage.
- **reason:** Person 1 has already waved me on and we've greeted each other, so I'll keep my pace and edge a little further right to give them clear room, then continue straight to the ER.
- **message:** Thanks — see you in class!
- **signal:** wave_on; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:position_side (claimed: on my right; position: ['left'])

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_b7fe7ead_r3/dp6 (talk, agent 1, decision 3)
- seen: -5° (+ left), 5.4 m, walking, signal hold_up_hand, changes [], age 25, width 0.5, traits []
- heard: "Thanks — no need, there's room for both of us, just keep left." (frame facing)
- history: 2.0 s ago "Greet the classmate I know and make room for us to pass each other in the narrow passage.", signal nod, message "Hi! Long time no see.", sideways +0.24 m (+ left)
- history: 1.0 s ago "Let him hurry past by stepping aside against the left wall, and wish him well without holding him up.", signal hold_up_hand, message "Oh no, go ahead — I'll get out of your way!", sideways +0.24 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.54 m from you, the wall on your right 1.21 m.
- **intent:** Follow his suggestion: keep to my left, pass him with room between us, and continue on to the supermarket.
- **reason:** He waved off my offer and asked us both to just keep left, so there's no need to flatten myself against the wall — I'll stay on my left side, pass with a comfortable gap, and carry on.
- **message:** Oh, okay — keep left, got it!
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['hold_up_hand'])

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_dbd98c92_r4/dp10 (talk, agent 1, decision 5)
- seen: -2° (+ left), 2.7 m, walking, signal wave_on, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Coming through on your right, dear — mind the suitcase!" (frame facing)
- history: 4.0 s ago "Acknowledge her and keep my course, steering slightly to my right but not yielding much, while looking up from my phone", signal nod, message "Thank you, dear! I'm heading for the emergency room, so keep clear!", sideways -0.62 m (+ left)
- history: 3.0 s ago "Keep my course with the suitcase, hold the right side of the passage, and warn her which side I'm on so we don't collide", signal nod, message "Thanks, dear! Just give me room on my right side here!", sideways +0.20 m (+ left)
- history: 2.0 s ago "Keep to the right side of the passage and pass her cleanly without a collision, since she's drifting toward my right too", signal nod, message "Coming through on your right, dear — mind the suitcase!", sideways -0.10 m (+ left)
- history: 1.0 s ago "Keep to the right side of the passage, hold my course, and pass Person 1 cleanly without a collision", signal nod, message "Coming through on your right, dear — mind the suitcase!", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Hold my line on the right side of the passage and pass Person 1 cleanly, keeping the suitcase with me
- **reason:** She has slowed and is waving me on, so I hold my course on her right without cutting further into her path; a small steady shift keeps my wide body and suitcase clear of her while I keep moving toward the emergency room.
- **message:** Coming through on your right, dear — mind the suitcase!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_dbd98c92_r4/dp12 (talk, agent 1, decision 6)
- seen: -5° (+ left), 1.2 m, walking, signal point, changes [], age 25, width 0.5, traits []
- heard: "Sorry Uncle, I'm over on your left — go ahead!" (frame facing)
- history: 5.0 s ago "Acknowledge her and keep my course, steering slightly to my right but not yielding much, while looking up from my phone", signal nod, message "Thank you, dear! I'm heading for the emergency room, so keep clear!", sideways -0.62 m (+ left)
- history: 4.0 s ago "Keep my course with the suitcase, hold the right side of the passage, and warn her which side I'm on so we don't collide", signal nod, message "Thanks, dear! Just give me room on my right side here!", sideways +0.40 m (+ left)
- history: 3.0 s ago "Keep to the right side of the passage and pass her cleanly without a collision, since she's drifting toward my right too", signal nod, message "Coming through on your right, dear — mind the suitcase!", sideways -0.10 m (+ left)
- history: 2.0 s ago "Keep to the right side of the passage, hold my course, and pass Person 1 cleanly without a collision", signal nod, message "Coming through on your right, dear — mind the suitcase!", sideways +0.00 m (+ left)
- history: 1.0 s ago "Hold my line on the right side of the passage and pass Person 1 cleanly, keeping the suitcase with me", signal nod, message "Coming through on your right, dear — mind the suitcase!", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Keep my line on the right side with the suitcase and pass her cleanly, since she's already giving way
- **reason:** She has clearly moved aside to her own right, which is my left, so the right side is open; I'll hold my course and hug the right wall a little more to give the suitcase clearance and avoid any repeat of the earlier collision.
- **message:** Thank you, dear — coming through on your right!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_dbd98c92_r4/dp6 (talk, agent 1, decision 3)
- seen: -0° (+ left), 5.7 m, walking, signal nod, changes ['slowed_down', 'moved_right', 'turned'], age 25, width 0.5, traits []
- heard: "Sure, Uncle, plenty of room on your right!" (frame facing)
- history: 2.0 s ago "Acknowledge her and keep my course, steering slightly to my right but not yielding much, while looking up from my phone", signal nod, message "Thank you, dear! I'm heading for the emergency room, so keep clear!", sideways -0.53 m (+ left)
- history: 1.0 s ago "Keep my course with the suitcase, hold the right side of the passage, and warn her which side I'm on so we don't collide", signal nod, message "Thanks, dear! Just give me room on my right side here!", sideways -0.09 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.30 m from you, the wall on your right 0.45 m.
- **intent:** Keep to the right side of the passage and pass her cleanly without a collision, since she's drifting toward my right too
- **reason:** She's drifting into my right, the same side I'm edging toward, so I'll angle a bit more right and hug the wall side while keeping my pace, since I'm unwell and in a hurry, and I don't want a repeat of this morning's collision. I'm keeping the cane and suitcase out where she can see them.
- **message:** Coming through on your right, dear — mind the suitcase!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_dbd98c92_r4/dp8 (talk, agent 1, decision 4)
- seen: -1° (+ left), 4.2 m, walking, signal wave_on, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.5, traits []
- heard: "Thank you, Uncle — I'm keeping to my left, the right side is all yours!" (frame facing)
- history: 3.0 s ago "Acknowledge her and keep my course, steering slightly to my right but not yielding much, while looking up from my phone", signal nod, message "Thank you, dear! I'm heading for the emergency room, so keep clear!", sideways -0.62 m (+ left)
- history: 2.0 s ago "Keep my course with the suitcase, hold the right side of the passage, and warn her which side I'm on so we don't collide", signal nod, message "Thanks, dear! Just give me room on my right side here!", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep to the right side of the passage and pass her cleanly without a collision, since she's drifting toward my right too", signal nod, message "Coming through on your right, dear — mind the suitcase!", sideways -0.10 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Keep to the right side of the passage, hold my course, and pass Person 1 cleanly without a collision
- **reason:** She's keeping to her left, which is my right, so holding my right side keeps us both clear; I'll ease slightly right to give the suitcase room and keep moving toward the emergency room.
- **message:** Coming through on your right, dear — mind the suitcase!
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left', 'slowed_down', 'turned']; position: ['ahead']); 4:coming_through_on_your_side (own move: right)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_e57e5fb0_r1/dp11 (talk, agent 1, decision 6)
- seen: -41° (+ left), 0.7 m, walking, signal point, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Okay, I'll keep to my left — you're fine on your right!" (frame facing)
- history: 5.0 s ago "Greet the person I know from class and make sure we pass each other safely in the narrow passage with my suitcase.", signal nod, message "Hello there, excuse me — coming through with the suitcase.", sideways -0.24 m (+ left)
- history: 4.0 s ago "Acknowledge her greeting, keep well to my right so she passes on her drifting side, and get by with the suitcase without another bump.", signal nod, message "Thank you, thank you — good to see you!", sideways +0.16 m (+ left)
- history: 2.0 s ago "Keep well to my right so she and my suitcase pass with no bump, and acknowledge her politely.", signal nod, message "Right you are — I'm keeping to my right, plenty of room. Mind the suitcase!", sideways +0.36 m (+ left)
- history: 1.0 s ago "Get by safely by slipping toward the left so she passes on my right side away from my suitcase, and warn her about it.", signal wave_on, message "Alright, I've got the suitcase on my right — passing on your left!", sideways +0.38 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.02 m from you, the wall on your right 0.73 m.
- **intent:** Stop weaving and hold my line so she can slip by on my right away from the suitcase, avoiding another bump in this narrow passage.
- **reason:** She has slowed and told me she'll keep to her left, so the simplest safe thing is to stop drifting around, get a little further left off her path, and let her walk past my right side, clear of the suitcase.
- **message:** Sorry, sorry — coming past on your left, mind the case!
- **signal:** hold_up_hand; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says stop_and_wait, the plan does not); 4:coming_through_on_your_side (own move: left)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_e57e5fb0_r3/dp5 (talk, agent 1, decision 3)
- seen: +1° (+ left), 5.8 m, walking, signal nod, changes ['moved_left'], age 25, width 0.5, traits []
- history: 2.0 s ago "Greet the person I know from class and make room so we pass safely.", signal wave_on, message "Oh, hi there! Late night too, huh?", sideways +0.40 m (+ left)
- history: 1.0 s ago "Acknowledge her friendly wave and keep to my side so we pass safely.", signal nod, message "Thanks, good to see you!", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.38 m from you, the wall on your right 1.37 m.
- **intent:** Keep to my left side so we pass safely, giving her plenty of room since she has already waved me on.
- **reason:** She nodded and waved me on, and I'm already shifted left, so I'll hold my side of the passage and slow a touch to make sure we clear each other without bumping, given what happened earlier today.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['nod'])

### rf40_round1_head_on_turn_taking/T_head_on_de176842_0f57f8a5_r2/dp10 (talk, agent 0, decision 5)
- seen: -21° (+ left), 0.6 m, walking, signal hold_up_hand, changes ['sped_up', 'moved_right', 'turned'], age 25, width 0.5, traits []
- heard: "Sorry, I'm on your left!" (frame facing)
- history: 4.0 s ago "Keep walking to the supermarket while glancing at my phone, staying on my line and expecting Person 1 to make room.", signal none, message "", sideways +0.06 m (+ left)
- history: 3.0 s ago "Acknowledge Person 1 and keep my line so we pass cleanly on my left, their left.", signal nod, message "Hey, all right — I'll stay right where I am.", sideways +0.05 m (+ left)
- history: 2.0 s ago "Keep my line so Person 1 squeezes past on my right, and keep my suitcase close so it doesn't block them.", signal nod, message "Sure, thanks!", sideways +0.06 m (+ left)
- history: 1.0 s ago "Stay on my line and keep my suitcase tucked so Person 1 can pass on my right, their left, without a collision", signal nod, message "Right, coming through on your right — I'm holding my line!", sideways +0.05 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.82 m from you, the wall on your right 0.93 m.
- **intent:** Stay steady on my line, keep my suitcase tucked to my left, and let Person 1 squeeze past on my right, their left.
- **reason:** We're about to meet in 0.3 s, and Person 1 said they're on my left (their right). I've been saying I'll hold my line so they pass on my right, so I keep straight at a slightly slower pace and keep the suitcase out of the way.
- **message:** Okay, I'm holding my line — pass on my right!
- **signal:** hold_up_hand; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 1:position_side (claimed: on my left; position: ['right']); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_0f57f8a5_r2/dp5 (talk, agent 1, decision 3)
- seen: -7° (+ left), 5.1 m, walking, signal nod, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "Hey, all right — I'll stay right where I am." (frame facing)
- history: 2.0 s ago "Keep walking to the supermarket and give the man with the suitcase room to pass", signal none, message "", sideways +0.60 m (+ left)
- history: 1.0 s ago "Stay to the left, slow a little, and let the man with the suitcase pass safely", signal wave_on, message "Hey, coming through — I'll keep left so you can get by.", sideways +0.20 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.28 m from you, the wall on your right 1.47 m.
- **intent:** Acknowledge Person 1 and pass him on his left side (my right) while he stands still with the suitcase, then continue to the supermarket
- **reason:** He said he'd stay put, so I should move to the clearer right side of the passage to get past him and his suitcase without squeezing him against the wall, then speed back up to my usual pace.
- **message:** Thanks! I'll squeeze past on your right — see you in class.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:misread_heard_side (restated: my right; the heard message puts it on my left)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_0f57f8a5_r2/dp7 (talk, agent 1, decision 4)
- seen: +28° (+ left), 2.9 m, walking, signal nod, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "Sure, thanks!" (frame facing)
- history: 3.0 s ago "Keep walking to the supermarket and give the man with the suitcase room to pass", signal none, message "", sideways +0.10 m (+ left)
- history: 2.0 s ago "Stay to the left, slow a little, and let the man with the suitcase pass safely", signal wave_on, message "Hey, coming through — I'll keep left so you can get by.", sideways -0.30 m (+ left)
- history: 1.0 s ago "Acknowledge Person 1 and pass him on his left side (my right) while he stands still with the suitcase, then continue to the supermarket", signal nod, message "Thanks! I'll squeeze past on your right — see you in class.", sideways -0.50 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Slide past Person 1 on my right side while he keeps still with the suitcase, then carry on to the supermarket
- **reason:** He is drifting toward my side with a suitcase and looking at his phone, so I'll move further right to keep a clear gap, then straighten up and continue to the supermarket at my normal pace.
- **message:** Oops, sorry — coming past on your right!
- **signal:** point; **coded:** side both, slowed False, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: []); 1:position_side (claimed: on my right; position: ['left'])

### rf40_round1_head_on_turn_taking/T_head_on_de176842_0f57f8a5_r2/dp9 (talk, agent 1, decision 5)
- seen: -1° (+ left), 0.6 m, walking, signal nod, changes ['slowed_down', 'moved_right', 'turned'], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "Right, coming through on your right — I'm holding my line!" (frame facing)
- history: 4.0 s ago "Keep walking to the supermarket and give the man with the suitcase room to pass", signal none, message "", sideways -0.16 m (+ left)
- history: 3.0 s ago "Stay to the left, slow a little, and let the man with the suitcase pass safely", signal wave_on, message "Hey, coming through — I'll keep left so you can get by.", sideways -0.56 m (+ left)
- history: 2.0 s ago "Acknowledge Person 1 and pass him on his left side (my right) while he stands still with the suitcase, then continue to the supermarket", signal nod, message "Thanks! I'll squeeze past on your right — see you in class.", sideways -0.76 m (+ left)
- history: 1.0 s ago "Slide past Person 1 on my right side while he keeps still with the suitcase, then carry on to the supermarket", signal point, message "Oops, sorry — coming past on your right!", sideways +0.32 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.03 m from you, the wall on your right 0.72 m.
- **intent:** Stop drifting right into his path and slide past him on his left side (my left), avoiding his suitcase
- **reason:** He's holding his line on my right with a suitcase, and I'm too close to keep crowding his side — slipping left keeps us clear of each other.
- **message:** Sorry, I'm on your left!
- **signal:** hold_up_hand; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:misread_heard_side (restated: my left; the heard message puts it on my right); 3:intent_against_plan (intent says stop_and_wait, the plan does not)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_231c8154_r4/dp3 (talk, agent 0, decision 2)
- seen: -10° (+ left), 4.7 m, walking, signal hold_up_hand, changes ['moved_right'], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- heard: "No need, no need, you go first!" (frame facing)
- history: 2.3 s ago "Greet the older man I know from class and make sure we pass each other comfortably in the narrow passage.", signal wave_on, message "", sideways +0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.47 m from you, the wall on your right 1.28 m.
- **intent:** Accept his offer and pass on my side of the passage without bumping into him.
- **reason:** He has waved me on and told me to go first, so I'll stay to my left, keep close to the wall, and walk steadily past him.
- **message:** Okay, thank you, uncle!
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['hold_up_hand'])

### rf40_round1_head_on_turn_taking/T_head_on_de176842_3dee0df5_r4/dp10 (talk, agent 1, decision 5)
- seen: +31° (+ left), 0.7 m, walking, signal hold_up_hand, changes [], age 25, width 0.5, traits []
- heard: "Sorry, coming past on your left!" (frame facing)
- history: 3.0 s ago "Greet him warmly but keep moving steadily along my side of the passage and pass safely.", signal nod, message "Hi! Yes, small world — just heading to the supermarket. Careful, it's narrow here.", sideways +0.25 m (+ left)
- history: 2.0 s ago "Keep my line along my side of the passage, give just enough room for him to pass, and stay stable on my cane.", signal nod, message "Thanks! Yeah, let's squeeze past. Nice to see you.", sideways +0.25 m (+ left)
- history: 1.0 s ago "Hold my line so we pass safely without either of us stumbling in this narrow passage.", signal hold_up_hand, message "Watch your step — I'm right here.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.62 m from you, the wall on your right 1.13 m.
- **intent:** Hold my line on the left side and brace so he passes without bumping into me or my cane.
- **reason:** He said he'd pass on his left, which is my right, so I keep to my left along the wall and slow slightly to absorb any brush; someone already walked into me today and my cane makes me less steady.
- **message:** Right here, steady on!
- **signal:** hold_up_hand; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:misread_heard_side (restated: my right; the heard message puts it on my left)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_81bae7c3_r2/dp10 (talk, agent 0, decision 5)
- seen: +3° (+ left), 2.7 m, walking, signal hold_up_hand, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 4.0 s ago "Acknowledge Person 1 and step aside so he can pass comfortably, since he's waving me on.", signal nod, message "Oh, thank you, dear! I'm fine, don't worry.", sideways +0.50 m (+ left)
- history: 3.0 s ago "Finish giving way to Person 1 and keep steady along the wall side so he can pass comfortably.", signal nod, message "Thanks, dear — I'm fine, you go on ahead!", sideways -0.00 m (+ left)
- history: 2.0 s ago "Keep to the wall side and let Person 1 pass without fuss.", signal nod, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep to the left near the wall and let Person 1 pass on his right without fuss", signal nod, message "Thanks, dear — coming through!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.37 m from you, the wall on your right 1.38 m.
- **intent:** Keep steadily to the wall side and let Person 1 pass without any more fuss.
- **reason:** I've already waved and said thanks twice; he's slowed and is holding up a hand, so the kindest thing is to stay put near the wall and quietly let him by.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 2:own_signal (claimed: waved; own earlier signals: ['nod'])

### rf40_round1_head_on_turn_taking/T_head_on_de176842_81bae7c3_r2/dp8 (talk, agent 0, decision 4)
- seen: +2° (+ left), 4.3 m, walking, signal hold_up_hand, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Okay, Auntie — I'll keep to my right, you're fine to pass." (frame facing)
- history: 3.0 s ago "Acknowledge Person 1 and step aside so he can pass comfortably, since he's waving me on.", signal nod, message "Oh, thank you, dear! I'm fine, don't worry.", sideways +0.50 m (+ left)
- history: 2.0 s ago "Finish giving way to Person 1 and keep steady along the wall side so he can pass comfortably.", signal nod, message "Thanks, dear — I'm fine, you go on ahead!", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep to the wall side and let Person 1 pass without fuss.", signal nod, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.37 m from you, the wall on your right 1.38 m.
- **intent:** Keep to the left near the wall and let Person 1 pass on his right without fuss
- **reason:** He has waved me on and is keeping to his right, so I stay close to the left wall and ease off a little as we meet.
- **message:** Thanks, dear — coming through!
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['hold_up_hand'])

### rf40_round1_head_on_turn_taking/T_head_on_de176842_9950986f_r4/dp4 (talk, agent 1, decision 2)
- seen: -4° (+ left), 7.6 m, walking, signal hold_up_hand, changes ['slowed_down', 'moved_right', 'turned'], age 25, width 0.5, traits []
- heard: "Hi! No problem, go ahead — I'm giving you room on your left." (frame facing)
- history: 1.0 s ago "Let Person 1 know I'm hurrying through and keep moving without slowing down, holding my line.", signal wave_on, message "Hey, I'm in a hurry — sorry, can you give me some room? I'm heading to the ER.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep hurrying straight ahead to the ER, accepting the room they offered on my right side without slowing down.
- **reason:** Person 1 is giving me room on my right (their left), so I hold my line but nudge slightly right to pass cleanly, keeping my pace up since I need to get to the ER.
- **message:** Thanks, thank you — coming through on your right!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_9950986f_r4/dp6 (talk, agent 1, decision 3)
- seen: -7° (+ left), 5.3 m, walking, signal wave_on, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.5, traits []
- heard: "Yes, go ahead — you're clear on your right!" (frame facing)
- history: 2.0 s ago "Let Person 1 know I'm hurrying through and keep moving without slowing down, holding my line.", signal wave_on, message "Hey, I'm in a hurry — sorry, can you give me some room? I'm heading to the ER.", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep hurrying straight ahead to the ER, accepting the room they offered on my right side without slowing down.", signal nod, message "Thanks, thank you — coming through on your right!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep hurrying straight to the ER, taking the room Person 1 offered on my right without slowing down
- **reason:** Person 1 has waved me on and told me I'm clear on my right, so I'll shift slightly right to pass them and keep my pace up to reach the ER.
- **message:** Thanks — coming through on your right!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_9950986f_r4/dp8 (talk, agent 1, decision 4)
- seen: -4° (+ left), 3.3 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Right, coming through — take care with the suitcase!" (frame facing)
- history: 3.0 s ago "Let Person 1 know I'm hurrying through and keep moving without slowing down, holding my line.", signal wave_on, message "Hey, I'm in a hurry — sorry, can you give me some room? I'm heading to the ER.", sideways -0.40 m (+ left)
- history: 2.0 s ago "Keep hurrying straight ahead to the ER, accepting the room they offered on my right side without slowing down.", signal nod, message "Thanks, thank you — coming through on your right!", sideways -0.40 m (+ left)
- history: 1.0 s ago "Keep hurrying straight to the ER, taking the room Person 1 offered on my right without slowing down", signal nod, message "Thanks — coming through on your right!", sideways -0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.28 m from you, the wall on your right 0.47 m.
- **intent:** Keep my pace and pass Person 1 on my right, toward the wall side with more room, without slowing for the ER.
- **reason:** I'm already on the right side of the passage and moving fast to the ER; the room on my right is where Person 1 has been giving way, so I hold my line, shift a touch more right for the suitcase clearing space, and keep going.
- **message:** Sorry, coming through on your right — I'm heading to the ER!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_9b752a36_r1/dp3 (talk, agent 1, decision 2)
- seen: -3° (+ left), 7.5 m, walking, signal nod, changes ['slowed_down', 'moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking steadily toward the emergency room and hold my line with my suitcase, expecting the young man to make room for me.", signal eye_contact, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge the young man's nod and keep my steady line with the suitcase toward the emergency room, expecting him to step aside.
- **reason:** I nodded back to be polite but I am in a hurry to the emergency room and cannot easily yield while pulling a large suitcase. I hold my line, slowing slightly and shifting a little to my left only near the end to avoid a collision if he does not move.
- **signal:** nod; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 2:own_signal (claimed: nodded; own earlier signals: ['eye_contact'])

### rf40_round1_head_on_turn_taking/T_head_on_de176842_bcb9cb2c_r2/dp4 (talk, agent 0, decision 2)
- seen: -0° (+ left), 6.9 m, walking, signal none, changes ['slowed_down', 'moved_right', 'turned'], age 25, width 0.5, traits []
- history: 1.1 s ago "Keep my line and speed towards the supermarket, but make eye contact so the man knows I see him and we avoid a collision.", signal eye_contact, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep my line and let the man know I see him so we don't collide, staying slightly to my side with the suitcase.
- **reason:** Someone walked into me earlier today, so I want to be visible and predictable. A small sidestep gives him room for his 30-degree drift to my right while I hold my general line with my cane and suitcase.
- **message:** Excuse me, coming through on your left.
- **signal:** hold_up_hand; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_bcb9cb2c_r2/dp5 (talk, agent 1, decision 3)
- seen: -30° (+ left), 6.9 m, walking, signal hold_up_hand, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- heard: "Excuse me, coming through on your left." (frame facing)
- history: 1.1 s ago "Keep walking to the supermarket while making room for the woman with the cane and suitcase to pass.", signal none, message "", sideways +0.05 m (+ left)
- history: 0.1 s ago "Give the woman with the cane and suitcase plenty of room to pass by moving toward the left wall", signal none, message "", sideways +0.05 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.83 m from you, the wall on your right 0.92 m.
- **intent:** Give the woman with the cane and suitcase plenty of room by moving toward the left wall, since her left is my right.
- **reason:** She asked for room on her left, which is my right, but her cane and suitcase are on that side and she's drifting toward my left anyway, so stepping toward the left wall keeps us clearly apart and is the easy, safe choice in a narrow passage at night.
- **message:** No problem, go ahead.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:misread_heard_side (restated: my right; the heard message puts it on my left)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_c36d5d49_r1/dp6 (talk, agent 1, decision 3)
- seen: +3° (+ left), 4.7 m, walking, signal nod, changes ['moved_right'], age 70, width 0.5, traits []
- heard: "Thank you — coming through, on your left!" (frame facing)
- history: 2.0 s ago "Acknowledge her greeting and make room so she can hurry past", signal nod, message "", sideways -0.62 m (+ left)
- history: 1.0 s ago "Acknowledge her, let her hurry past, and keep well to my right so she has room", signal wave_on, message "No problem, go ahead!", sideways -0.27 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Keep well to my right so she can hurry past on her left, and acknowledge her
- **reason:** She's hurrying the other way and has asked to come through on her left, which is my right; I'm easy-going, so I'll give her the space and keep moving.
- **message:** No problem, plenty of room!
- **signal:** wave_on; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:misread_heard_side (restated: my right; the heard message puts it on my left)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_c36d5d49_r2/dp8 (talk, agent 0, decision 4)
- seen: -1° (+ left), 3.4 m, walking, signal wave_on, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Yes aunty, coming through — I'm on your left, plenty of room!" (frame facing)
- history: 3.0 s ago "Acknowledge Person 1 and ask them to make room, since I'm hurrying to the emergency room and want to keep my pace.", signal nod, message "Hello there! Excuse me, I'm in a bit of a hurry — I need to get to the emergency room.", sideways -0.54 m (+ left)
- history: 2.0 s ago "Keep my pace toward the emergency room and pass Person 1 on the side they've cleared, without slowing down.", signal nod, message "Thank you — I'm coming through, please keep left of me.", sideways -0.54 m (+ left)
- history: 1.0 s ago "Keep my fast pace to the emergency room and pass Person 1 on the side they're keeping clear, without slowing.", signal nod, message "Thank you, beta — coming through on your left!", sideways -0.07 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.42 m from you, the wall on your right 0.33 m.
- **intent:** Keep my fast pace to the emergency room and pass Person 1 on the side they've cleared, without slowing down.
- **reason:** They've slowed and waved me on, saying they're on my left (my right), so I'll edge slightly further right into the room they've made and keep my pace; I'm heading to the emergency room and can't afford to dawdle.
- **message:** Thank you, beta — I'm hurrying, please stay to your left!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:misread_heard_side (restated: my right; the heard message puts it on my left); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_dbd98c92_r3/dp8 (talk, agent 1, decision 5)
- seen: -8° (+ left), 1.6 m, walking, signal none, changes ['moved_right', 'turned'], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep my line and ask Person 1 to make room, since I'm hurrying to the emergency room with a cane and suitcase.", signal hold_up_hand, message "Hello there — sorry, could you give me a little room? I'm heading to the hospital.", sideways -0.00 m (+ left)
- history: 3.0 s ago "Acknowledge her courtesy and keep moving straight toward the hospital without slowing down.", signal nod, message "Thank you kindly — God bless you.", sideways -0.00 m (+ left)
- history: 2.0 s ago "Keep my line and steady pace toward the hospital, trusting Person 1 to leave room as she said.", signal none, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep my line and steady pace, letting Person 1 pass on my right as she said she'd keep clear.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.
- **intent:** Shift slightly left to give Person 1 room on my right and keep moving toward the hospital without slowing down.
- **reason:** She has moved over to my right, so I'll hold my pace and edge a little left to widen the gap and avoid another collision, while keeping my line and momentum toward the ER.
- **message:** Coming through on your left, ma'am — thank you!
- **signal:** hold_up_hand; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_f79677df_r2/dp9 (talk, agent 1, decision 4)
- seen: -17° (+ left), 0.8 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 4.4 s ago "Greet her warmly and keep walking toward the supermarket, then give her room to pass in the narrow passage.", signal nod, message "Ah, hello there!", sideways +0.44 m (+ left)
- history: 3.4 s ago "Acknowledge her courtesy, ease slightly to my left to open a gap, and keep walking steadily toward the supermarket.", signal nod, message "Thank you, dear — I'll keep to my side too. Have a good day!", sideways +0.44 m (+ left)
- history: 2.4 s ago "Acknowledge her wave, hold my line to the left to leave her room, and keep walking steadily toward the supermarket.", signal nod, message "Aye, thank you, dear. Take care now!", sideways +0.09 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.43 m from you, the wall on your right 1.32 m.
- **intent:** Keep my line on the left, warn her gently, and let her pass without a collision in the narrow passage.
- **reason:** She's drifting toward my side and we're closing fast; a raised hand and a clear word avoids a bump, and keeping left with a small sidestep gives us both room in the 1.75 m passage.
- **message:** Steady now, dear — coming through on my left.
- **signal:** hold_up_hand; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: ['slowed_down'])

