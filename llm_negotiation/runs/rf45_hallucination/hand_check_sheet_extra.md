# RF-45 hand check sheet (issue #134)

Each entry: what the prompt showed (the view's fields), the reply, and the coder's flags. Judgements are in `hand_check_judgements.json`.

## Random sample (0)

## Extra precision sample (seed 1345): 7:no_room 20, 7:wall_close 15, 1:moved_side 20 (55)

### rf39_round1_head_on_sidestep_reprompt/I_head_on_de176842_bcb9cb2c_r3/dp1 (independent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking toward the supermarket, holding my line, and pass Person 1 without incident.
- **reason:** After being walked into earlier today, I want to give a little room so we don't collide, but I'm not going to squeeze myself against the wall or stop. A small sidestep left, keeping my pace, should let him pass while I hold my ground.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.53 / 0.52 m); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_3dee0df5_r3/dp8 (non_verbal, agent 1, decision 4)
- seen: -7° (+ left), 1.1 m, walking, signal nod, changes ['moved_right'], age 25, width 0.5, traits []
- history: 3.6 s ago "Acknowledge him and keep my line; he can step aside this time.", signal eye_contact, message "", sideways -0.06 m (+ left)
- history: 2.6 s ago "Acknowledge my classmate and keep walking my line; he can give way this time.", signal nod, message "", sideways -0.06 m (+ left)
- history: 1.6 s ago "Keep my line and let my classmate step aside; he already waved me on.", signal none, message "", sideways -0.07 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.84 m from you, the wall on your right 0.91 m.
- **intent:** Hold my line and ask him to give way, since he is drifting into my path
- **reason:** He is drifting into my space at 30 degrees and I got knocked into earlier today; I know him, he nodded, so I will signal with my hand and hold a straight line rather than be pushed against the wall. I am determined to hold my ground.
- **signal:** hold_up_hand; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.59 / 0.66 m); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_68f09b97_r4/dp5 (non_verbal, agent 0, decision 3)
- seen: -8° (+ left), 1.0 m, walking, signal hold_up_hand, changes ['slowed_down', 'moved_right'], age 25, width 0.5, traits []
- history: 3.8 s ago "Keep walking steadily to the supermarket and hold my line; the passage is narrow, so I'll keep to my side and let the young woman pass.", signal none, message "", sideways +0.06 m (+ left)
- history: 1.0 s ago "Hold my line and keep walking steadily to the supermarket, letting the young woman pass across in front of me", signal none, message "", sideways -0.55 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.72 m from you, the wall on your right 1.03 m.
- **intent:** Acknowledge the young woman's raised hand and hold my ground, slowing a little so she can pass around me without a collision
- **reason:** She has raised her hand, perhaps to steady herself or to ask me to wait, and the passage is too narrow for both of us at full stride. I am determined to keep my line, but at my age with a cane and a suitcase I cannot dodge quickly, so slowing and letting her clear me is the safest way to keep going to the supermarket.
- **signal:** hold_up_hand; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_02dfbadb_9950986f_r2/dp2 (non_verbal, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep my course to the emergency room and keep looking at my phone, but stay aware of Person 1
- **reason:** I'm in a hurry to the ER and know this person from class, but I don't need to stop and chat. I'll keep my line, glance up as we get close, and shift slightly left against the wall to make room so we can pass without the suitcase catching.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.42 / 0.63 m); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_74cb78c1_xaac00b3d/dp3 (non_verbal, agent 1, decision 2)
- seen: +1° (+ left), 3.0 m, walking, signal none, changes ['turned'], age 25, width 0.5, traits []
- history: 2.6 s ago "Keep walking to the supermarket and give way slightly so we can pass each other comfortably", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Pass the woman comfortably by giving way to my right, since she is drifting to my left
- **reason:** She's heading toward my left side, so shifting right keeps us clear of each other with plenty of room in this narrow passage.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['turned']; position: ['ahead']); 3:intent_against_plan (intent says left, the plan turns right)

### rf39_round1_head_on_sidestep_reprompt/N_head_on_de176842_f79677df_r3/dp2 (non_verbal, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Greet the young woman I know from class and keep walking steadily to the supermarket.
- **reason:** I recognise her and want to be polite, but I have my cane and I am not going to squeeze myself against the wall for anyone.
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.63 / 0.62 m); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_1caa9a84_r3/dp3 (talk, agent 0, decision 2)
- seen: -4° (+ left), 7.4 m, walking, signal eye_contact, changes ['moved_right'], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Keep walking normally and give the man with the cane and suitcase plenty of room to pass", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Give the man with the cane and suitcase plenty of room while slipping past him
- **reason:** He's looking at his phone and has a cane and suitcase, so he needs the space; my right side has more room against the wall, and I'll keep it steady and slow through the gap.
- **signal:** eye_contact; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.53 / 0.72 m)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_55c9ae40_r2/dp3 (talk, agent 0, decision 2)
- seen: +16° (+ left), 2.7 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 2.9 s ago "Keep walking toward the hospital without colliding with the young woman, holding my line but giving her room", signal none, message "", sideways -0.06 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.84 m from you, the wall on your right 0.91 m.
- **intent:** Steady my line so the young woman has clear room on my left, and keep heading to the hospital
- **reason:** She is drifting toward my right, into my path, so I'll move a bit further right against the wall to leave her space, hold my line, and not get knocked over like earlier today.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.59 / 0.66 m)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_5767d932_r3/dp9 (talk, agent 0, decision 5)
- seen: -6° (+ left), 0.9 m, walking, signal eye_contact, changes ['slowed_down', 'moved_right'], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep moving toward the emergency room while making sure I don't bump into the man coming toward me, since someone already walked into me today.", signal none, message "", sideways -0.62 m (+ left)
- history: 3.0 s ago "Keep well to my right and pass the man without a collision, while staying alert since he's looking at me", signal eye_contact, message "", sideways -0.33 m (+ left)
- history: 2.0 s ago "Keep to my right and slip past the man without a collision, staying alert", signal eye_contact, message "", sideways -0.03 m (+ left)
- history: 1.0 s ago "Keep to my right, pass the man safely, and continue toward the emergency room.", signal nod, message "Excuse me, coming through.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Slip past the man to my right without bumping into him, then keep going to the emergency room.
- **reason:** He's already moved to his right and slowed, and I'm close to the right wall, so a small extra step right should open enough gap for him to pass while I keep moving. Someone bumped into me earlier today, so I'd rather give way than collide again.
- **message:** Sorry, excuse me.
- **signal:** eye_contact; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['moved_right', 'slowed_down']; position: ['right'])

### rf39_round1_head_on_sidestep_reprompt/T_head_on_02dfbadb_cb859069_r4/dp2 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking toward the emergency room, giving Person 1 plenty of room to pass.
- **reason:** I'm in a hurry to get to the emergency room but I'm easy-going and don't want a repeat of being bumped into earlier today. Shifting a little to my left against the wall side gives the young man room to pass without either of us colliding.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.52 / 0.73 m)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_02604456_r4/dp10 (talk, agent 1, decision 5)
- seen: -6° (+ left), 1.0 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 4.1 s ago "Greet my classmate warmly and make room to pass in the narrow passage.", signal wave_on, message "Hi! Fancy seeing you here.", sideways -0.53 m (+ left)
- history: 3.1 s ago "Greet my classmate and keep to the right so we can pass each other easily in the narrow passage.", signal wave_on, message "Hey, good to see you! Go ahead, I'm making room.", sideways -0.18 m (+ left)
- history: 2.1 s ago "Greet my classmate warmly, keep well to the right, and let us pass each other easily in the narrow passage.", signal wave_on, message "Hey! All good, I'm keeping to the right — see you!", sideways +0.00 m (+ left)
- history: 1.1 s ago "Keep to the right and let my classmate pass so we can squeeze by each other in the narrow passage.", signal wave_on, message "Hey, good to see you! Go ahead, I'm staying right here.", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Let my classmate pass me on my left since I'm already hugging the right wall, and keep moving toward the supermarket.
- **reason:** I've already moved right against the wall and there's little room left; rather than shuffle further I'll hold my line, wave him past on my left, then pick up my normal pace to the supermarket.
- **message:** Hi again! Just squeeze past me on the left — I'm up against the wall here.
- **signal:** wave_on; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m); 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_51dfba80_r4/dp1 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking toward Person 1, look up from my phone to acknowledge them, and stay steady in my path since the passage is too narrow to avoid them anyway.
- **reason:** After being bumped earlier, I want to be alert and make eye contact so we both see each other coming. I'll slow and edge slightly to my left to give a bit of room, but I won't scurry out of the way — I have as much right to this passage.
- **signal:** eye_contact; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_74cb78c1_xaac00b3d/dp3 (talk, agent 0, decision 2)
- seen: -0° (+ left), 7.3 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the supermarket and shift slightly to my right so we can pass each other comfortably.", signal none, message "", sideways -0.30 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.18 m from you, the wall on your right 0.57 m.
- **intent:** Keep walking to the supermarket and pass Person 1 comfortably to my right
- **reason:** We are already offset to the right and have room against the right wall; keeping my line and speed lets us pass without fuss.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.93 / 0.32 m)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_b6a40c60_r1/dp5 (talk, agent 0, decision 3)
- seen: -8° (+ left), 0.9 m, walking, signal nod, changes ['slowed_down', 'moved_right'], age 25, width 0.5, traits []
- history: 3.9 s ago "Keep my pace toward the emergency room, glance up at the attractive man, but hold my line down the passage", signal eye_contact, message "", sideways -0.04 m (+ left)
- history: 2.9 s ago "Keep my pace toward the emergency room, hold my line, and keep an eye on the attractive man coming toward me", signal eye_contact, message "", sideways -0.05 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.92 m from you, the wall on your right 0.83 m.
- **intent:** Keep my line and my pace toward the emergency room, asking the man to give me room rather than swerving aside for him.
- **reason:** I'm in pain and on my way to the ER; he's already moved to his right and slowed, so a small step left keeps me clear of him and lets me keep going without losing time. There's no real space to step far aside in this crowded passage.
- **message:** Excuse me, coming through — I need to get past.
- **signal:** eye_contact; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['moved_right', 'slowed_down']; position: ['right'])

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_b7fe7ead_r4/dp1 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking at my normal pace toward the emergency room, holding my line since the passage is narrow.
- **reason:** I'm in a hurry to the ER and the passage is too narrow to give much room. I'll hold my lane but shift slightly right at the last moment to avoid a repeat of being walked into, while keeping my pace.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_bcb9cb2c_r2/dp7 (talk, agent 0, decision 4)
- seen: -7° (+ left), 2.3 m, walking, signal nod, changes ['slowed_down', 'moved_right'], age 25, width 0.5, traits []
- heard: "Excuse me." (frame None)
- history: 3.0 s ago "Keep my line and make sure he sees me coming, so he steps aside rather than colliding like the person earlier did.", signal eye_contact, message "", sideways -0.35 m (+ left)
- history: 2.0 s ago "Make him notice me and give me room so he steps aside, while keeping my line", signal eye_contact, message "Excuse me — coming through, please.", sideways -0.35 m (+ left)
- history: 1.0 s ago "Acknowledge his nod and hold my line so he steps aside, given the narrow passage and my suitcase.", signal nod, message "Thank you — I'm just going to keep my line here.", sideways -0.35 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.23 m from you, the wall on your right 0.52 m.
- **intent:** Keep to my line and pass him safely without a collision, using the space he has given me
- **reason:** He has slowed and moved aside, and there's little room for me and my suitcase; holding my line avoids another collision like earlier today.
- **message:** Thanks — squeezing past now.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m)

### rf39_round1_head_on_sidestep_reprompt/T_head_on_de176842_c36d5d49_r4/dp3 (talk, agent 0, decision 2)
- seen: +2° (+ left), 7.4 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge him and keep moving toward the emergency room
- **reason:** He nodded, so I nod back. He's drifting to my left, so I edge right to pass him cleanly without slowing down, since I need to get to the emergency room.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: []; position: ['ahead'])

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_2ec958bb_r3/dp4 (non_verbal, agent 0, decision 2)
- seen: +27° (+ left), 2.5 m, walking, signal eye_contact, changes [], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 2.8 s ago "Keep walking toward the supermarket, easing aside to let the older woman pass since she is distracted by her phone.", signal none, message "", sideways -0.06 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.84 m from you, the wall on your right 0.91 m.
- **intent:** Keep easing to my right to give the older woman room, letting her pass on my left
- **reason:** She is drifting to my right while looking at her phone, so moving slightly further right and slowing my own drift keeps us from bumping; at 70 she may not be watching where she goes.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: []; position: ['left'])

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_5841fc4a_x3d3cadc7_flipped/dp5 (non_verbal, agent 0, decision 3)
- seen: -5° (+ left), 1.7 m, walking, signal none, changes ['slowed_down', 'turned'], age 25, width 0.5, traits []
- history: 3.2 s ago "Keep walking towards the supermarket, easing slightly to my left to leave room for the oncoming man", signal none, message "", sideways +0.30 m (+ left)
- history: 2.2 s ago "Keep walking to the supermarket, staying slightly left so there is room to pass the oncoming man", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.47 m from you, the wall on your right 1.28 m.
- **intent:** Give the oncoming man a bit more room by easing further to my left, and slow slightly so we pass comfortably
- **reason:** He is drifting to my left and we are closing fast; I'm easy-going and would rather yield a little space than bump into him in this narrow passage.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['slowed_down', 'turned']; position: ['right'])

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_68f09b97_r1/dp10 (non_verbal, agent 1, decision 5)
- seen: +41° (+ left), 0.9 m, walking, signal eye_contact, changes ['slowed_down', 'moved_left', 'turned'], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- history: 4.0 s ago "I move to my right to give the old man plenty of room, since he's using a cane and pulling a suitcase", signal none, message "", sideways -0.72 m (+ left)
- history: 3.0 s ago "Keep well to my right to give the old man with the cane and suitcase plenty of room", signal none, message "", sideways -0.32 m (+ left)
- history: 2.0 s ago "Keep well to my right and slow slightly to give the old man with the cane and suitcase plenty of room to pass", signal none, message "", sideways -0.02 m (+ left)
- history: 1.0 s ago "Keep well to my right, friendly eye contact, and give the old man with the cane and suitcase room to pass", signal eye_contact, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Give the old man with the cane and suitcase plenty of room on his right, with a friendly greeting
- **reason:** He's elderly with a cane and suitcase and is drifting toward my left where there's little room, so I'll nudge a bit further right and slow to let him pass comfortably while returning his eye contact with a nod.
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.7 m)

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_9b752a36_r2/dp3 (non_verbal, agent 1, decision 2)
- seen: -3° (+ left), 2.5 m, walking, signal none, changes ['slowed_down', 'turned'], age 25, width 0.5, traits []
- history: 2.8 s ago "Keep walking straight to the emergency room, pulling my suitcase, and hold my line rather than yield to him.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Warn him to go around me and keep my straight line to the emergency room
- **reason:** He is drifting into my left side at a good pace and I have right-of-way in my own line; I'll signal and edge just enough to the right so my suitcase doesn't catch him, but I won't give up my whole path.
- **signal:** hold_up_hand; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['slowed_down', 'turned']; position: ['ahead'])

### rf40_round1_head_on_turn_taking/N_head_on_02dfbadb_b7fe7ead_r3/dp6 (non_verbal, agent 0, decision 4)
- seen: +23° (+ left), 0.9 m, walking, signal none, changes ['slowed_down', 'turned'], age 25, width 0.5, traits []
- history: 3.5 s ago "Acknowledge my classmate and keep to my side of the passage so we can pass cleanly without a repeat of this morning's collision", signal eye_contact, message "", sideways -0.20 m (+ left)
- history: 2.5 s ago "Acknowledge my classmate and hold my line on the right so we pass cleanly without another collision", signal nod, message "", sideways -0.00 m (+ left)
- history: 1.5 s ago "Keep to my side on the right and pass my classmate cleanly", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.98 m from you, the wall on your right 0.77 m.
- **intent:** Steady my line on the right to avoid another collision and pass my classmate cleanly
- **reason:** She is drifting into my path at 30 degrees; I raise my hand to signal and shift slightly right against the wall to make room so we pass without bumping.
- **signal:** hold_up_hand; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.73 / 0.52 m)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_3cb16ae9_r4/dp3 (non_verbal, agent 1, decision 2)
- seen: -2° (+ left), 1.7 m, walking, signal none, changes ['turned'], age 25, width 0.5, traits []
- history: 3.1 s ago "Keep walking toward the supermarket and pass by Person 1 without fuss", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep my line and pass Person 1 on my left, glancing up from my phone to acknowledge her
- **reason:** She's drifting into my right side, so I'll hold my course and edge slightly left to give us both room to pass cleanly. I look up to make sure she sees me and avoid a bump.
- **signal:** eye_contact; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['turned']; position: ['ahead'])

### rf40_round1_head_on_turn_taking/N_head_on_de176842_3dee0df5_r3/dp5 (non_verbal, agent 1, decision 3)
- seen: +5° (+ left), 4.7 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 2.0 s ago "Greet Person 1 briefly and keep to my line against the wall so we can pass each other", signal nod, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Acknowledge Person 1 and keep my line along the passage so we can pass cleanly", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Hold my line against the left wall and pass Person 1 cleanly, giving a small nod of recognition
- **reason:** They have moved over to my left, so holding my line against the wall keeps things predictable; with someone having bumped into me earlier I won't swerve, and I'll ease slightly as we meet to avoid contact.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.63 / 0.62 m); 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says left, the plan turns none)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_74cb78c1_x42411b7c_base/dp7 (non_verbal, agent 1, decision 4)
- seen: -4° (+ left), 0.9 m, walking, signal none, changes ['turned'], age 25, width 0.5, traits []
- history: 3.5 s ago "Keep walking towards the supermarket and give way slightly so we can pass each other comfortably in the narrow passage.", signal none, message "", sideways -0.30 m (+ left)
- history: 2.5 s ago "Keep walking to the supermarket, edging slightly to my right so we can pass comfortably.", signal none, message "", sideways -0.30 m (+ left)
- history: 1.5 s ago "Keep walking to the supermarket, staying slightly to my right so we can pass comfortably in the narrow passage.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.17 m from you, the wall on your right 0.58 m.
- **intent:** Pass Person 1 comfortably in the narrow passage by keeping to my right
- **reason:** The passage is narrow and the other person is drifting towards my right, so easing off slightly and shifting a little further right gives us room to pass without bumping.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['turned']; position: ['ahead'])

### rf40_round1_head_on_turn_taking/N_head_on_de176842_74cb78c1_xaac00b3d/dp5 (non_verbal, agent 0, decision 3)
- seen: -10° (+ left), 1.6 m, walking, signal none, changes ['turned'], age 25, width 0.5, traits []
- history: 3.2 s ago "Keep walking to the supermarket and shift a little to my left so we can pass comfortably.", signal none, message "", sideways +0.35 m (+ left)
- history: 2.2 s ago "Keep to my left and pass Person 1 comfortably", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.52 m from you, the wall on your right 1.23 m.
- **intent:** Pass Person 1 comfortably by shifting a bit more to my left, since they're drifting toward my left too.
- **reason:** They're drifting to my left, so I'll give a little more room to my left to avoid collision, then walk on past them. I'm easy-going and tend to give way.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['turned']; position: ['right'])

### rf40_round1_head_on_turn_taking/N_head_on_de176842_7eed7b59_r3/dp5 (non_verbal, agent 1, decision 3)
- seen: +30° (+ left), 5.6 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 2.0 s ago "keep walking to the supermarket and give the young man plenty of room to pass", signal none, message "", sideways -0.50 m (+ left)
- history: 1.0 s ago "Keep walking and ease aside to give the young man room to pass", signal none, message "", sideways -0.50 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.38 m from you, the wall on your right 0.37 m.
- **intent:** Keep moving toward the supermarket and give the young man room to pass on my left
- **reason:** He is drifting to my right, so I will keep to the right wall and give him space on my left, walking steadily so we pass safely.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['slowed_down']; position: ['left'])

### rf40_round1_head_on_turn_taking/N_head_on_de176842_800a3b04_r1/dp9 (non_verbal, agent 0, decision 5)
- seen: +1° (+ left), 1.4 m, still, signal hold_up_hand, changes ['stopped'], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep heading to the emergency room, glance up from my phone and give way comfortably as we pass.", signal none, message "", sideways -0.52 m (+ left)
- history: 3.0 s ago "Glance up from my phone and give way to the right so we pass comfortably, keeping on toward the emergency room.", signal none, message "", sideways -0.53 m (+ left)
- history: 2.0 s ago "Keep yielding right toward the wall and pass Person 1 smoothly, staying on my way to the emergency room.", signal none, message "", sideways -0.12 m (+ left)
- history: 1.0 s ago "Glance up, acknowledge her, and slide a little more to the right to pass comfortably without crowding the wall.", signal eye_contact, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.40 m from you, the wall on your right 0.35 m.
- **intent:** Acknowledge her raised hand and slow down, giving her room to pass or sort herself out, while still heading to the emergency room.
- **reason:** She has stopped and raised a hand, so something is up. I'm easy-going and there's little room, so I'll slow and nudge a bit further right to pass without crowding her, just a brief pause before I continue to the ER.
- **signal:** hold_up_hand; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_b6a40c60_r2/dp4 (non_verbal, agent 1, decision 2)
- seen: +31° (+ left), 2.8 m, walking, signal hold_up_hand, changes [], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 2.7 s ago "Keep walking towards the supermarket, giving way to the woman with the cane", signal none, message "", sideways -0.05 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.93 m from you, the wall on your right 0.82 m.
- **intent:** Keep to my side and give the woman with the cane plenty of room as she passes
- **reason:** She is drifting towards my right and looking at her phone with a cane, so I will edge a little further right and hold my line to let her pass safely.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: []; position: ['left'])

### rf40_round1_head_on_turn_taking/N_head_on_de176842_bcb9cb2c_r1/dp7 (non_verbal, agent 0, decision 4)
- seen: +13° (+ left), 2.8 m, walking, signal nod, changes ['slowed_down', 'moved_left'], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep walking steadily on my side of the passage and let the man pass on his own side", signal none, message "", sideways +0.00 m (+ left)
- history: 2.0 s ago "Keep my line and let him pass on his side, but make eye contact so he knows I'm here and holds his side", signal eye_contact, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep my line and signal him clearly to hold his side, since he's drifting toward me", signal hold_up_hand, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.
- **intent:** Keep the little space I have and make him go round the suitcase, giving a clear palm-out signal to stay on his side
- **reason:** He has already moved to my left and slowed, and the passage is too narrow for me to give way much with a suitcase and cane. I hold my line and signal clearly, then shift only slightly right so the suitcase clears him — after being walked into earlier today, I'm not yielding the whole passage.
- **signal:** hold_up_hand; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m)

### rf40_round1_head_on_turn_taking/N_head_on_de176842_f79677df_r3/dp5 (non_verbal, agent 1, decision 3)
- seen: -9° (+ left), 0.9 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 3.9 s ago "Greet her warmly as we pass and keep my line toward the supermarket.", signal nod, message "", sideways -0.05 m (+ left)
- history: 2.9 s ago "Greet her warmly as we pass and keep my line toward the supermarket", signal nod, message "", sideways -0.05 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.93 m from you, the wall on your right 0.82 m.
- **intent:** Stop her from drifting into me and pass safely, keeping my line to the supermarket
- **reason:** She is coming straight at my side and there is little room; slowing and edging left off her drift line avoids a collision while keeping me on my way to the supermarket, and a raised hand warns her I am holding my ground.
- **signal:** hold_up_hand; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m); 3:intent_against_plan (intent says stop_and_wait, the plan does not)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_7eed7b59_r2/dp1 (silent, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Make room for the elderly woman with the cane and suitcase by easing toward my right, and slow down so we pass safely.
- **reason:** She is old, using a cane, pulling a suitcase and looking at her phone, so she has little room to adjust. I am easy-going and will give way, moving slightly right to leave her a clear path and slowing so we don't collide.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.7 m)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_9950986f_r2/dp7 (silent, agent 1, decision 4)
- seen: +9° (+ left), 3.0 m, walking, signal none, changes ['slowed_down', 'moved_right', 'turned'], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep heading to the emergency room without slowing down, and acknowledge my classmate as we pass.", signal none, message "", sideways -0.30 m (+ left)
- history: 2.0 s ago "Keep heading to the emergency room without slowing, and pass my classmate comfortably in this narrow passage.", signal none, message "", sideways -0.30 m (+ left)
- history: 1.0 s ago "Keep moving steadily toward the emergency room and pass my classmate without slowing, giving him room on my left.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.08 m from you, the wall on your right 0.67 m.
- **intent:** Keep moving toward the emergency room without slowing, and pass my classmate cleanly on his side of the passage.
- **reason:** He is drifting into my path on the right, so rather than get pushed against the wall I'll shift slightly left to open a gap and keep my pace up; I'm in a hurry and using a cane and suitcase, so a clear, steady line matters more than a chat.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.73 / 0.32 m); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_9b752a36_r1/dp6 (silent, agent 0, decision 3)
- seen: +28° (+ left), 1.7 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.']
- history: 3.3 s ago "Keep walking to the supermarket, easing to the right to give the elderly woman with the suitcase room to pass.", signal none, message "", sideways -0.72 m (+ left)
- history: 2.3 s ago "Keep walking to the supermarket, giving the elderly woman with the suitcase plenty of room to pass in the narrow passage.", signal none, message "", sideways -0.22 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.49 m from you, the wall on your right 0.26 m.
- **intent:** Keep out of the elderly woman's way, hugging the right wall so she and her suitcase pass safely in the narrow passage.
- **reason:** She is elderly, moving faster than me and pulling a bulky suitcase, and the passage is too narrow for us to pass comfortably side by side. I am easy-going about these things, so I will slow and press closer to the right wall until she has gone by.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.7 m)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_b1d97a31_r3/dp12 (silent, agent 1, decision 6)
- seen: +15° (+ left), 1.2 m, walking, signal none, changes ['slowed_down'], age 70, width 0.5, traits []
- history: 5.1 s ago "Give way to the elderly man coming towards me so we pass without bumping in the narrow passage.", signal none, message "", sideways -0.72 m (+ left)
- history: 4.1 s ago "Pass the elderly man safely in the narrow passage by keeping to my right and slowing a little.", signal none, message "", sideways -0.27 m (+ left)
- history: 3.1 s ago "Keep well to my right so the elderly man and I pass without bumping in the narrow passage.", signal none, message "", sideways -0.28 m (+ left)
- history: 2.0 s ago "Keep well to my right, slow down a bit more, and let the elderly man pass safely.", signal none, message "", sideways -0.28 m (+ left)
- history: 1.0 s ago "Let the elderly man pass safely by staying close to my right and slowing right down.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.50 m from you, the wall on your right 0.25 m.
- **intent:** Keep close to my right and let the elderly man pass safely.
- **reason:** He is old, still drifting toward my left, and there is little room; staying right at a slow pace lets us pass without a bump.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m); 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_b59c2831_r3/dp5 (silent, agent 1, decision 3)
- seen: +6° (+ left), 4.9 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep heading to the ER, but look up from my phone and give Person 1 a friendly greeting and plenty of room as we pass.", signal none, message "", sideways -0.35 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.12 m from you, the wall on your right 0.63 m.
- **intent:** Greet my classmate warmly while giving him room to pass, keeping to my right and slowing a touch so we don't collide.
- **reason:** I already moved right to give him space and he's shifted to his left, so we're lined up to pass cleanly. Slowing slightly near the moment of passing feels natural and safe, especially after someone bumped into me earlier today, and lets me say hi without being rushed.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left']; position: ['left']); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_bcb9cb2c_r2/dp10 (silent, agent 0, decision 5)
- seen: +11° (+ left), 0.7 m, walking, signal none, changes ['slowed_down', 'moved_right'], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep walking toward the supermarket without being knocked over, but I won't mind passing close to him.", signal none, message "", sideways -0.47 m (+ left)
- history: 3.0 s ago "Pass Person 1 safely in the narrow passage without being knocked over, giving a little extra room since I'm pulling a suitcase and using a cane", signal none, message "", sideways -0.02 m (+ left)
- history: 2.0 s ago "Keep passing Person 1 safely while holding my line in the narrow passage, since he's nearly upon me and I'm pulling a suitcase and using a cane.", signal none, message "", sideways -0.36 m (+ left)
- history: 1.0 s ago "Keep passing Person 1 safely without being knocked over, holding my line since he is nearly upon me and I have a suitcase and cane.", signal none, message "", sideways -0.06 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.25 m from you, the wall on your right 0.50 m.
- **intent:** Pass Person 1 without a collision, holding my line with the suitcase and cane since he's right on top of me.
- **reason:** He's only 0.7 m away and drifting into my path; there's no time to dodge and no room to spare, so I keep my line and speed and let him go around me. I was nearly knocked over earlier today and I'm not yielding with a suitcase and cane on a narrow passage.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_bcb9cb2c_r3/dp3 (silent, agent 0, decision 2)
- seen: -4° (+ left), 7.3 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the supermarket, holding my line so the oncoming man passes me cleanly.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep my line and my pace so the oncoming man passes me cleanly, without yielding the space I need with my cane and suitcase.
- **reason:** The passage is too narrow for both of us to keep our exact lines, and he is coming straight at me. I won't stop or cede the whole path, but a small step to my right with my cane and suitcase should let him slip past without a collision like the one earlier today.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m)

### rf40_round1_head_on_turn_taking/S_head_on_02dfbadb_f3d09c23_r3/dp9 (silent, agent 0, decision 4)
- seen: -28° (+ left), 0.9 m, walking, signal none, changes ['slowed_down', 'turned'], age 25, width 0.5, traits ['They are walking with a cane.']
- history: 4.0 s ago "Keep walking toward the supermarket and give way to the man with the cane so we can pass safely in the narrow passage.", signal none, message "", sideways +0.49 m (+ left)
- history: 3.0 s ago "Keep to the left side of the passage and pass the man with the cane safely, slowing a little to give him room.", signal none, message "", sideways +0.09 m (+ left)
- history: 2.0 s ago "Pass the man with the cane safely in the narrow passage, keeping well to my left and slowing down to give him room.", signal none, message "", sideways +0.09 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.29 m from you, the wall on your right 1.46 m.
- **intent:** Give the man with the cane plenty of room by keeping well to my left and slowing right down so we can pass safely.
- **reason:** He is drifting towards my left and closing fast, and with a cane he needs extra space in this narrow passage. Slowing and hugging the left wall keeps us both safe.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['slowed_down', 'turned']; position: ['right'])

### rf40_round1_head_on_turn_taking/S_head_on_de176842_51dfba80_r1/dp3 (silent, agent 0, decision 2)
- seen: +1° (+ left), 3.6 m, walking, signal none, changes ['slowed_down', 'turned'], age 25, width 0.5, traits []
- history: 2.4 s ago "Keep walking towards the supermarket and pass Person 1 without another collision, holding my line but making a little room.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.
- **intent:** Keep my line toward the supermarket and pass Person 1 without another collision, edging slightly to my right to give room since they're drifting to my left.
- **reason:** They are drifting into my left side and have already slowed and changed direction once; a small step to my right keeps me clear of them while I hold my course. I slow a touch because I'm looking at my phone and don't want another bump like earlier today.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['slowed_down', 'turned']; position: ['ahead'])

### rf40_round1_head_on_turn_taking/S_head_on_de176842_55c9ae40_r3/dp9 (silent, agent 1, decision 4)
- seen: -21° (+ left), 0.6 m, walking, signal none, changes ['slowed_down', 'moved_right'], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 4.1 s ago "Keep heading to the supermarket while making sure I don't bump into the elderly man looking at his phone.", signal none, message "", sideways +0.62 m (+ left)
- history: 3.1 s ago "Keep heading to the supermarket while safely passing the elderly man on his phone", signal none, message "", sideways +0.22 m (+ left)
- history: 1.0 s ago "Avoid bumping into the distracted elderly man while still heading to the supermarket", signal none, message "", sideways -0.27 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Get past the elderly man without bumping into him
- **reason:** He's drifting to my left while looking at his phone, so I'll slow down and shift right to give him room and let him pass safely.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['moved_right', 'slowed_down']; position: ['right'])

### rf40_round1_head_on_turn_taking/S_head_on_de176842_68f09b97_r2/dp9 (silent, agent 0, decision 5)
- seen: -47° (+ left), 0.8 m, walking, signal none, changes ['moved_left', 'turned'], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep walking steadily toward the supermarket, holding my line with my cane and suitcase.", signal none, message "", sideways +0.00 m (+ left)
- history: 3.0 s ago "Keep walking steadily toward the supermarket, holding my line, and let the oncoming woman make room.", signal none, message "", sideways -0.00 m (+ left)
- history: 2.0 s ago "Keep my line toward the supermarket and let the oncoming woman move around me and my suitcase.", signal none, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep my line toward the supermarket and let the oncoming woman move around me and my suitcase.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Hold my line toward the supermarket and let the oncoming woman move around me and my suitcase.
- **reason:** She is drifting across my path but there is little room and I am steady with my cane and suitcase; at 0.3 s to meeting, sudden moves would be worse than keeping my line and letting her adjust.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m)

### rf40_round1_head_on_turn_taking/S_head_on_de176842_9950986f_r4/dp6 (silent, agent 1, decision 3)
- seen: -7° (+ left), 4.9 m, walking, signal none, changes ['slowed_down', 'moved_right'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep moving toward the emergency room, staying my course, but glance up from my phone so I don't bump into my classmate in the narrow passage.", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep moving toward the emergency room without slowing, glance up and give my classmate a quick nod while holding my line.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep heading to the emergency room, hold my line, and acknowledge my classmate as we pass in the narrow passage.
- **reason:** He has moved to his right, which is my left; holding my line could put us too close with my cane and suitcase, so I keep my pace and give a small step to my right to clear him, then carry on.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['moved_right', 'slowed_down']; position: ['right']); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/S_head_on_de176842_f3d09c23_r2/dp2 (silent, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep heading to the emergency room, giving way to the woman coming the other way.
- **reason:** I'm easy-going and there's little room in this narrow passage, so I'll shift slightly to my right to leave the woman room to pass, then continue on my way.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room on my right; gap 0.62 m, other 0.5 m wide); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_68f09b97_r1/dp9 (talk, agent 0, decision 5)
- seen: -16° (+ left), 1.2 m, walking, signal hold_up_hand, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Sorry, go ahead." (frame facing)
- history: 4.0 s ago "Keep walking steadily toward the supermarket, holding my line and my ground.", signal none, message "", sideways -0.40 m (+ left)
- history: 3.0 s ago "Keep my lane and my pace toward the supermarket; I'm not dodging for anyone in a narrow passage.", signal none, message "", sideways -0.00 m (+ left)
- history: 2.0 s ago "Hold my line and pace toward the supermarket; make the other walker go around me, since I have a suitcase and cane and little room to move.", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep my line and pace toward the supermarket; let the young woman go around me since I'm pulling a suitcase and using a cane.", signal hold_up_hand, message "Excuse me, coming through.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.18 m from you, the wall on your right 0.57 m.
- **intent:** Acknowledge her courtesy and continue steadily toward the supermarket, keeping my line and letting her step aside.
- **reason:** She has kindly slowed and given way, so a nod and thanks is polite; I keep walking at a steady pace with my suitcase and cane since there is little room to maneuver.
- **message:** Thank you, thank you.
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_800a3b04_r3/dp4 (talk, agent 1, decision 2)
- seen: +2° (+ left), 7.6 m, walking, signal eye_contact, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Give way to the older man with the suitcase by stepping aside, since he's distracted by his phone", signal none, message "", sideways -0.40 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.18 m from you, the wall on your right 0.57 m.
- **intent:** Keep moving to the right against the wall to make plenty of room for the older man with the suitcase, and slow a little until he passes
- **reason:** He's elderly, distracted by his phone, and towing a suitcase, so I'll finish stepping aside to my right and ease off a bit to give him a wide berth rather than squeezing past.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.93 / 0.32 m)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_b7fe7ead_r3/dp4 (talk, agent 1, decision 2)
- seen: -2° (+ left), 7.2 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- heard: "Hi! Yeah, it's been a while — sorry, I'm actually rushing to the emergency room right now." (frame facing)
- history: 1.0 s ago "Greet the classmate I know and make room for us to pass each other in the narrow passage.", signal nod, message "Hi! Long time no see.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Let him hurry past by stepping aside against the left wall, and wish him well without holding him up.
- **reason:** He's rushing to the emergency room, so I should clear the passage quickly rather than chat; stepping toward the left wall gives him the wider side to pass.
- **message:** Oh no, go ahead — I'll get out of your way!
- **signal:** hold_up_hand; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.53 / 0.72 m)

### rf40_round1_head_on_turn_taking/T_head_on_02dfbadb_e57e5fb0_r1/dp7 (talk, agent 1, decision 4)
- seen: -2° (+ left), 3.9 m, walking, signal point, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.5, traits []
- heard: "Careful on the left — I'll keep to this side." (frame facing)
- heard: "Hello! I'll keep to the left so your suitcase can pass." (frame facing)
- history: 3.0 s ago "Greet the person I know from class and make sure we pass each other safely in the narrow passage with my suitcase.", signal nod, message "Hello there, excuse me — coming through with the suitcase.", sideways -0.60 m (+ left)
- history: 2.0 s ago "Acknowledge her greeting, keep well to my right so she passes on her drifting side, and get by with the suitcase without another bump.", signal nod, message "Thank you, thank you — good to see you!", sideways -0.20 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.38 m from you, the wall on your right 0.37 m.
- **intent:** Keep well to my right so she and my suitcase pass with no bump, and acknowledge her politely.
- **reason:** She has moved over to her left, which is my right, so staying on my right keeps us apart. Slowing a little and giving the suitcase a touch more room avoids another collision in this narrow passage.
- **message:** Right you are — I'm keeping to my right, plenty of room. Mind the suitcase!
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left', 'slowed_down', 'turned']; position: ['ahead'])

### rf40_round1_head_on_turn_taking/T_head_on_de176842_0f57f8a5_r1/dp9 (talk, agent 1, decision 5)
- seen: -27° (+ left), 0.7 m, walking, signal none, changes ['moved_left', 'turned'], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 4.0 s ago "Greet Person 1 and make room for them to pass with the suitcase", signal wave_on, message "", sideways +0.62 m (+ left)
- history: 3.0 s ago "Greet my classmate and keep well to the left so they can pass with the suitcase", signal wave_on, message "Hey! Coming through — I'll give you room.", sideways +0.22 m (+ left)
- history: 2.0 s ago "Acknowledge my classmate's thanks and keep to my left so they can pass with the suitcase", signal nod, message "No problem, see you around!", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep well to the left and let my classmate pass with the suitcase without bumping into them", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.25 m from you, the wall on your right 1.50 m.
- **intent:** Keep well to the left and let my classmate with the suitcase pass without bumping into them
- **reason:** We are about to meet head-on with little room; I'm already greeting them and giving way, so I hug the left wall a little more and slow down till they pass with the suitcase.
- **signal:** none; **coded:** side left, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.7 m)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_51dfba80_r2/dp11 (talk, agent 1, decision 6)
- seen: -31° (+ left), 0.7 m, walking, signal nod, changes ['moved_right'], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "Thank you, dear! See you in class." (frame facing)
- history: 5.0 s ago "Greet her warmly and give her room to pass while she's on her phone with a suitcase", signal wave_on, message "", sideways -0.15 m (+ left)
- history: 4.0 s ago "Greet her warmly and keep well clear so she can pass safely while distracted by her phone and suitcase", signal wave_on, message "Hello! Good to see you!", sideways +1.38 m (+ left)
- history: 3.0 s ago "Greet her warmly and keep well clear to my left so she can pass safely while on her phone with her suitcase", signal wave_on, message "Hello! Good to see you too! I'll keep to this side, take your time.", sideways +0.48 m (+ left)
- history: 2.0 s ago "Stay clearly to my left against the wall so she can pass safely while distracted by her phone and suitcase", signal wave_on, message "Hello! Good to see you too! I'll keep to this side, take your time.", sideways -0.23 m (+ left)
- history: 1.0 s ago "Stay close to my left against the wall and slow down so she can pass safely while distracted by her phone and suitcase", signal hold_up_hand, message "", sideways -0.05 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.02 m from you, the wall on your right 0.73 m.
- **intent:** Acknowledge her thanks warmly and stay clear to my left so she can pass safely while distracted by her phone and suitcase
- **reason:** She is older, on her phone, pulling a suitcase, and already has moved to her side; keeping to my left against the wall and slow lets her pass without any bump.
- **message:** You're welcome! See you in class!
- **signal:** wave_on; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.77 / 0.48 m)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_5767d932_r4/dp3 (talk, agent 0, decision 2)
- seen: +1° (+ left), 3.6 m, walking, signal none, changes ['slowed_down', 'turned'], age 25, width 0.5, traits []
- history: 2.4 s ago "Keep heading to the emergency room while avoiding a collision with the oncoming man", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.
- **intent:** Keep moving toward the emergency room while giving the oncoming man room to pass on my right
- **reason:** He is drifting to my left, so stepping to my right opens a clear gap; I am easy-going and would rather give way than risk another collision like earlier today.
- **signal:** none; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['slowed_down', 'turned']; position: ['ahead'])

### rf40_round1_head_on_turn_taking/T_head_on_de176842_68f09b97_r2/dp3 (talk, agent 0, decision 2)
- seen: -1° (+ left), 2.8 m, walking, signal none, changes ['slowed_down', 'turned'], age 25, width 0.5, traits []
- history: 2.7 s ago "Keep walking straight to the supermarket, holding my line in the passage.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.
- **intent:** Keep walking straight at my steady pace and let the younger woman go around me, holding my line in the passage.
- **reason:** I am determined and tend to hold my ground; with a cane and suitcase I can't easily dodge in a narrow busy passage, and she is already drifting to my right, so she can pass on that side. I slow a little only to avoid a collision.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['slowed_down', 'turned']; position: ['ahead']); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_b1d97a31_r4/dp9 (talk, agent 1, decision 5)
- seen: -4° (+ left), 1.0 m, walking, signal nod, changes [], age 70, width 0.5, traits []
- history: 3.0 s ago "Acknowledge the elderly man politely and give him plenty of room to pass in the narrow passage.", signal nod, message "", sideways -0.55 m (+ left)
- history: 2.0 s ago "Keep to my right so the elderly man can pass comfortably in the narrow passage", signal none, message "", sideways -0.20 m (+ left)
- history: 1.0 s ago "Give the elderly man room to pass by keeping to my right, slowing slightly so we pass comfortably in the narrow passage", signal none, message "", sideways -0.20 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.42 m from you, the wall on your right 0.33 m.
- **intent:** Keep well to my right and slow a little so the elderly man passes comfortably in the narrow passage
- **reason:** He is elderly and there is little space; I have already moved right, so I just need to slow slightly and stay right until he has passed, then carry on to the supermarket at my usual pace.
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m); 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_f79677df_r2/dp2 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Greet her warmly and keep walking toward the supermarket, then give her room to pass in the narrow passage.
- **reason:** She's an acquaintance from my classes and nodded at me, so I return the greeting. The passage is too narrow for the two of us to pass side by side comfortably without one giving way, so I shift slightly to my right at reduced pace to let her through, then carry on to the supermarket.
- **message:** Ah, hello there!
- **signal:** nod; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room on my right; gap 0.62 m, other 0.5 m wide)

### rf40_round1_head_on_turn_taking/T_head_on_de176842_f79677df_r4/dp2 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- heard: "Uncle, hello! Don't worry, I'll give you room." (frame facing)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Greet her warmly and carry on at my normal pace, keeping to my side of the passage.
- **reason:** She's a familiar face from my classes and has kindly offered room, so I acknowledge her politely. I'll keep my pace and edge slightly to my right so we pass comfortably without either of us having to squeeze against the wall.
- **message:** Hello, hello! Thank you, my dear. No need to fuss, I'm steady on my feet.
- **signal:** wave_on; **coded:** side right, slowed True, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.63 / 0.62 m)

