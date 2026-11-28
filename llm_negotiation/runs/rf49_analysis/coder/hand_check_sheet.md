# RF-45 hand check sheet (issue #134)

Each entry: what the prompt showed (the view's fields), the reply, and the coder's flags. Judgements are in `hand_check_judgements.json`.

## Random sample (150)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_02604456_r2/dp2 (silent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Pass Person 1 without fuss while pulling my suitcase, since I'm easy-going and recognize them.
- **reason:** I want to give way and keep the narrow passage clear; moving slightly right (where there's a bit more room than the left wall side) lets us pass comfortably.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_02dfbadb_1868bff4_r1/dp8 (silent, agent 0, decision 4)
- seen: +21° (+ left), 2.5 m, walking, signal none, changes ['moved_left', 'turned'], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- history: 3.1 s ago "Keep to my side of the passage and give the man with the suitcase room to pass.", signal none, message "", sideways -0.68 m (+ left)
- history: 2.1 s ago "Keep giving the man with the suitcase room to pass without crowding the wall", signal none, message "", sideways -0.21 m (+ left)
- history: 1.1 s ago "Let the man with the suitcase pass without me getting squeezed against the wall", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.45 m from you, the wall on your right 0.30 m.
- **intent:** Avoid getting squeezed against the right wall as the man with the suitcase passes
- **reason:** I'm already close to the right wall and he's drifting toward my right, so slowing right down lets him pass without me being pinned against the wall.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_1caa9a84_r3/dp4 (silent, agent 0, decision 2)
- seen: +9° (+ left), 7.1 m, walking, signal none, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 1.2 s ago "Pass the man safely without getting in his way, since he's distracted by his phone and pulling a suitcase", signal none, message "", sideways -0.68 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.45 m from you, the wall on your right 0.30 m.
- **intent:** Keep clear of the distracted man with the cane and suitcase while getting past him
- **reason:** He's drifting toward my left, and he's looking at his phone and pulling a suitcase, so I'll edge further right to leave him plenty of room and avoid a collision.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_1caa9a84_r4/dp4 (silent, agent 1, decision 2)
- seen: +2° (+ left), 7.6 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep out of the way of the woman coming toward me, since the passage is narrow and I'm pulling a suitcase and using a cane.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep to my side of the narrow passage and let the woman pass without a collision, since I'm juggling a cane, a suitcase and my phone.
- **reason:** I'm already slightly right of centre and she's coming straight at me; a small shift to the right keeps me clear of her while staying off the wall, and after being bumped earlier today I'd rather give way early and obviously.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_02dfbadb_5767d932_r2/dp2 (silent, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep heading to the emergency room without another collision, giving way gently.
- **reason:** There's more space on my right (0.98 m) than my left, and shifting slightly right lets the oncoming man pass while I keep moving with my suitcase.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_5767d932_r4/dp4 (silent, agent 0, decision 2)
- seen: +6° (+ left), 7.5 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep heading to the emergency room without bumping into the man ahead, since I'm distracted by my phone and pulling a suitcase.", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.24 m from you, the wall on your right 0.51 m.
- **intent:** Keep heading to the emergency room without bumping into the man ahead, since I'm distracted by my phone and pulling a suitcase.
- **reason:** I've already moved right to give him room, and there's still a wide gap on that side, so I can keep my line and watch my phone.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_02dfbadb_68f09b97_r1/dp3 (silent, agent 0, decision 2)
- seen: -5° (+ left), 7.3 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the supermarket without yielding more than needed.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep walking to the supermarket without yielding more than needed.
- **reason:** I have the right to my line and there is room to pass; the oncoming woman can adjust, and at 70 with a cane and suitcase I am not going to swerve for every approaching stranger.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_02dfbadb_81209f4f_xaac00b3d/dp3 (silent, agent 0, decision 2)
- seen: +6° (+ left), 7.5 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the supermarket, but make a little room so we pass comfortably.", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.24 m from you, the wall on your right 0.51 m.
- **intent:** Keep walking to the supermarket and pass the attractive man comfortably.
- **reason:** I've already moved to my right to give us room, and there's plenty of space between us now, so I'll just keep walking at my normal pace.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_02dfbadb_8ea28db3_r3/dp3 (silent, agent 0, decision 2)
- seen: +2° (+ left), 7.6 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep my path but slow down so I don't bump into her, given I'm distracted by my phone and someone already walked into me today.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Avoid bumping into the classmate I recognize while I'm distracted by my phone, and make room to pass her politely.
- **reason:** Someone already walked into me today and I'm looking at my phone, so I'll shift right to give her a clear line and avoid another collision, while staying easy-going.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_02dfbadb_9950986f_r1/dp3 (silent, agent 1, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep moving toward the emergency room without losing time, staying on my line and being ready to acknowledge my classmate.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep making steady progress to the emergency room without losing time, holding my line past my classmate.
- **reason:** I'm in a hurry and already committed to my line; there's enough room for both of us and I'll just acknowledge them as we pass.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_9b752a36_r4/dp1 (silent, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Give the elderly woman with the suitcase plenty of room to pass without fuss.
- **reason:** She is older and pulling a large suitcase, and my right side has more space (0.98 m) than my left, so moving right gives her an easier path while staying out of the wall.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_02dfbadb_b59c2831_r4/dp1 (silent, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits ['They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep my path clear but give a friendly nod to someone I know from class; no need to change course much.
- **reason:** She's busy on her phone and there's enough room in the passage, so I'll just keep walking normally and let us pass.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_02dfbadb_bcb9cb2c_r4/dp1 (silent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep to my side of the passage and give the woman with the cane and suitcase plenty of room to pass
- **reason:** She is pulling a large suitcase and using a cane, so she needs extra space; moving a little toward my right opens the gap without crowding the wall.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_02dfbadb_c36d5d49_r2/dp1 (silent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep heading to the supermarket while making room for an older acquaintance coming the other way.
- **reason:** Giving way to an elderly person is polite, and I have the wider gap on my right so a small step keeps us both moving comfortably.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_02dfbadb_ce2a06ef_r3/dp6 (silent, agent 1, decision 3)
- seen: +4° (+ left), 5.0 m, walking, signal none, changes ['moved_left'], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- history: 2.0 s ago "I want to pass the elderly woman with the cane and suitcase without getting in her way, so I'll move a bit toward my left.", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Pass the elderly woman with the cane and suitcase without getting in her way, leaving her plenty of room.", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Pass the elderly woman with the cane and suitcase without crowding her in the narrow passage.
- **reason:** I already drifted right, so I've taken up too much of her side; shifting back toward my left restores room for her cane and suitcase while still letting us pass.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_02dfbadb_ce2a06ef_r3/dp9 (silent, agent 1, decision 5)
- seen: -9° (+ left), 0.6 m, walking, signal none, changes ['slowed_down'], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- history: 4.0 s ago "I want to pass the elderly woman with the cane and suitcase without getting in her way, so I'll move a bit toward my left.", signal none, message "", sideways +0.47 m (+ left)
- history: 3.0 s ago "Pass the elderly woman with the cane and suitcase without getting in her way, leaving her plenty of room.", signal none, message "", sideways +0.00 m (+ left)
- history: 2.0 s ago "Pass the elderly woman with the cane and suitcase without crowding her in the narrow passage.", signal none, message "", sideways +0.47 m (+ left)
- history: 1.0 s ago "Give the elderly woman with the cane and suitcase plenty of room to pass without crowding her.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.31 m from you, the wall on your right 1.44 m.
- **intent:** Avoid crowding the elderly woman with the cane and suitcase as we meet in the narrow passage.
- **reason:** She has slowed down and is very close; slowing greatly gives her room and time to pass safely without me bumping into her.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_02dfbadb_f3d09c23_r1/dp1 (silent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep heading to the emergency room without slowing, since there's ample room to pass.
- **reason:** The passage is wide enough for us to pass each other, and I want to get to the ER without delay.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_de176842_0f57f8a5_r1/dp1 (silent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking to the supermarket while glancing at my phone, but give a little room so I don't collide with the classmate I know coming the other way.
- **reason:** A small shift left keeps me moving at my usual pace in this narrow passage while leaving space for her to pass on my right, and it's someone I know so I'd rather avoid an awkward bump.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_de176842_0f57f8a5_r4/dp2 (silent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep heading to the supermarket without disrupting my pace, since I know Person 1 and the passage is busy but there's plenty of room.
- **reason:** I am determined and tend to hold my ground; with nearly 10 m between us and a 1.75 m wide passage, there is no need to change my line or speed.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_de176842_1868bff4_r2/dp5 (silent, agent 0, decision 3)
- seen: +12° (+ left), 5.0 m, walking, signal none, changes ['moved_left'], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- history: 2.0 s ago "keep heading to the supermarket without fuss, easing past the man with the suitcase", signal none, message "", sideways -0.58 m (+ left)
- history: 1.0 s ago "keep heading to the supermarket without fuss, giving the man with the suitcase room to pass", signal none, message "", sideways -0.11 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.45 m from you, the wall on your right 0.30 m.
- **intent:** keep heading to the supermarket while giving the man with the suitcase room to pass on my left
- **reason:** I've already shifted right twice to make space; staying my course lets him pass smoothly without more fuss.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/S_head_on_de176842_231c8154_r4/dp2 (silent, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Get past the person I know without a fuss, since I'm in a hurry to the emergency room.
- **reason:** I'm easy-going and used to giving way; a small shift left keeps things smooth as we pass, even while I'm glancing at my phone.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_de176842_2ec958bb_r3/dp3 (silent, agent 1, decision 2)
- seen: +4° (+ left), 7.3 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep my line and my pace toward the supermarket; I have as much right to this passage as anyone.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking to the supermarket at my own pace without giving way, but avoid another collision by holding a clear line.
- **reason:** I have as much right to this passage as anyone, and I am already slightly right of center; I keep my line and pace so the oncoming man can go around me.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_de176842_3cb16ae9_r3/dp3 (silent, agent 1, decision 2)
- seen: +4° (+ left), 7.3 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep heading to the supermarket without changing course for the oncoming woman", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep heading toward the supermarket without yielding course to the oncoming woman
- **reason:** I'm determined and hold my ground; there's plenty of room and I have no reason to change my line just because someone is approaching.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_de176842_3dee0df5_r2/dp8 (silent, agent 1, decision 4)
- seen: +15° (+ left), 2.3 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 3.1 s ago "Keep walking to the supermarket without yielding unnecessarily, since the passage is wide enough for both of us to pass.", signal none, message "", sideways -0.00 m (+ left)
- history: 2.1 s ago "Keep walking steadily to the supermarket, holding my line since the passage is wide enough for both of us.", signal none, message "", sideways -0.00 m (+ left)
- history: 1.1 s ago "Keep walking steadily to the supermarket without being pushed around, but avoid another collision like earlier today.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking toward the supermarket without being shoved aside, but give Person 1 a small berth so we don't collide again like earlier today.
- **reason:** They've slowed and we're about to meet head-on; I've been walked into once already tonight, so a slight shift to the right keeps me moving forward while making room to pass safely.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_de176842_51dfba80_r2/dp2 (silent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep walking to the supermarket while watching my phone, but shift a bit aside so we don't bump shoulders with the young man I know.
- **reason:** He's walking toward me and I don't want another collision like earlier today, but I'm not going to stop or slow down — I'll just give us a bit of extra room while staying on my way.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_de176842_55c9ae40_r2/dp2 (silent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep making my way to the emergency room without getting knocked over again
- **reason:** I'm in a hurry to get to the ER, the passage is narrow but there's room for both of us, and I'll hold my line so nobody bumps into me again.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/S_head_on_de176842_5767d932_r2/dp4 (silent, agent 0, decision 2)
- seen: -0° (+ left), 7.4 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep heading to the emergency room without bumping into the man ahead, since someone already collided with me today.", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.34 m from you, the wall on your right 0.41 m.
- **intent:** Keep heading to the emergency room without bumping into the man ahead, staying clear of him
- **reason:** I already shifted right and have room on that side; a small further nudge gives extra clearance so we pass safely, since someone bumped into me earlier today.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_de176842_800a3b04_r4/dp2 (silent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep my line and avoid bumping into the woman ahead; I'm in a hurry to the ER but courteous.
- **reason:** She's walking toward me and I'm distracted by my phone; slowing slightly lets her pass safely without a fuss.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_de176842_9b752a36_r1/dp7 (silent, agent 1, decision 4)
- seen: +25° (+ left), 2.5 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep making my way to the emergency room without delay", signal none, message "", sideways -0.47 m (+ left)
- history: 2.0 s ago "Keep making my way to the emergency room without delay", signal none, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Keep making my way to the emergency room without delay", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.34 m from you, the wall on your right 0.41 m.
- **intent:** Keep making my way to the emergency room quickly, but avoid a collision with the young man approaching from my left
- **reason:** I have already drifted rightwards and there is only 0.41 m of space to my right wall, but a small sideways shift plus holding my line should let us pass without me slowing down. I am in a hurry and will not stop for someone who can easily go around me.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/S_head_on_de176842_b1d97a31_r2/dp2 (silent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Avoid bumping into the woman walking toward me, especially after being walked into earlier today.
- **reason:** Giving way slightly to the right keeps me clear of her path while staying well within the passage, and being easy-going I'd rather yield than risk another collision.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_de176842_c36d5d49_r4/dp4 (silent, agent 0, decision 2)
- seen: +4° (+ left), 7.3 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep moving toward the emergency room at my usual pace, holding my line, and greet the young man from my classes as we pass.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep heading to the emergency room and greet the young man from my classes as we pass.
- **reason:** I'm in a hurry to reach the emergency room and holding my line is fine; I know him and we have room to pass.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/S_head_on_de176842_e57e5fb0_r1/dp8 (silent, agent 1, decision 4)
- seen: -35° (+ left), 1.8 m, walking, signal none, changes ['slowed_down', 'moved_left', 'turned'], age 25, width 0.5, traits []
- history: 3.7 s ago "Avoid bumping into Person 1 while getting past her in the narrow passage, especially after being walked into earlier today.", signal none, message "", sideways +0.46 m (+ left)
- history: 2.7 s ago "Pass Person 1 without bumping into her in this narrow passage, giving her plenty of room.", signal none, message "", sideways +0.93 m (+ left)
- history: 1.6 s ago "Avoid a collision with Person 1 in the narrow passage, since she is drifting toward my right where the wall is close.", signal none, message "", sideways +0.93 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.42 m from you, the wall on your right 1.33 m.
- **intent:** Pass Person 1 safely in the narrow passage without bumping into her, while making room for her since she has moved over and slowed down.
- **reason:** She has slowed and moved toward my left, so easing my pace gives her more space to pass in the tight passage, and after being bumped into earlier I'd rather be cautious than collide.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/S_head_on_de176842_e57e5fb0_r3/dp4 (silent, agent 0, decision 2)
- seen: -7° (+ left), 7.5 m, walking, signal none, changes ['moved_right'], age 70, width 0.7, traits ['They are pulling a large suitcase.']
- history: 1.0 s ago "Make room for the man pulling a large suitcase, an older acquaintance, to pass comfortably.", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.40 m from you, the wall on your right 1.35 m.
- **intent:** Give the older man with the suitcase plenty of room to pass, since there's more space on my left.
- **reason:** I've already shifted left, leaving a clear gap for him and his suitcase; continuing straight on my new line is the easiest way to let him pass comfortably.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/S_head_on_de176842_f3d09c23_r3/dp1 (silent, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep heading to the emergency room without a fuss, giving the woman a little room to pass.
- **reason:** She's coming the other way and the passage is narrow; a small step right opens the gap and I'm easy-going about yielding.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_02dfbadb_1868bff4_r2/dp8 (talk, agent 1, decision 4)
- seen: -18° (+ left), 2.2 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- heard: "Sure, go ahead." (frame facing)
- history: 3.0 s ago "Keep my line and make eye contact so she gives way, without slowing my rush to the ER", signal eye_contact, message "", sideways +0.00 m (+ left)
- history: 2.0 s ago "Hold my line and keep eye contact so she gives way, without slowing my rush to the ER", signal eye_contact, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep my line but warn her clearly so she gives way and I don't lose time or get walked into again", signal eye_contact, message "Excuse me, coming through — I'm in a hurry.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Acknowledge her courtesy and keep moving quickly toward the ER now that she has clearly given way
- **reason:** She has explicitly said I can go ahead, so holding my line at my usual fast pace is both safe and respectful of her gesture; slowing or weaving would waste time I need to get to the emergency room.
- **message:** Thanks — much appreciated!
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_02dfbadb_231c8154_r1/dp3 (talk, agent 0, decision 2)
- seen: -5° (+ left), 7.3 m, walking, signal none, changes [], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 1.0 s ago "Greet the familiar person warmly and give him a little extra room since he's on his phone.", signal wave_on, message "Hello! Fancy seeing you here.", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.30 m from you, the wall on your right 1.45 m.
- **intent:** Keep giving the older man room since he's distracted by his phone, and stay friendly
- **reason:** I already said hello and stepped left to give him space; he's looking at his phone and I'm easy-going, so I'll just keep walking along this line and watch for his reaction.
- **signal:** eye_contact; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_231c8154_r3/dp1 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Greet the person I know and keep moving toward the emergency room without bumping into her.
- **reason:** I'm easy-going and give way; moving a little left keeps me clear of her while I stay on my way to the ER.
- **message:** Hello there, coming through—excuse me.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_02dfbadb_3cb16ae9_r3/dp4 (talk, agent 0, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal eye_contact, changes [], age 25, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 1.0 s ago "Keep walking but shift slightly aside so we pass comfortably, and catch his eye politely", signal eye_contact, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.24 m from you, the wall on your right 0.51 m.
- **intent:** Be friendly and let him pass comfortably without bumping into him
- **reason:** He's on his phone and looking at me, so easing off my pace while staying to the right gives us both room to pass safely.
- **message:** Hi there!
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_02dfbadb_51dfba80_r4/dp1 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Greet the person I know from class and make room for her to pass, since she's distracted by her phone and pulling a suitcase.
- **reason:** She's looking at her phone and wheeling a suitcase, and there's more space on my right, so I'll shift over slightly to give her a clear path and greet her warmly.
- **message:** Hello there!
- **signal:** wave_on; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_02dfbadb_55c9ae40_r3/dp6 (talk, agent 1, decision 3)
- seen: +3° (+ left), 5.0 m, walking, signal nod, changes [], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 2.0 s ago "Give way to the elderly man and avoid a collision", signal none, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Give way to the elderly man and avoid a collision", signal hold_up_hand, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.24 m from you, the wall on your right 0.51 m.
- **intent:** Give way to the elderly man and avoid a collision
- **reason:** He is elderly, using a cane and looking at his phone, so I slow right down to give him plenty of room and time to pass safely.
- **signal:** hold_up_hand; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_02dfbadb_5767d932_r3/dp1 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep to my side and pass by Person 1 without bumping into him
- **reason:** I'm on the right side of the passage already and there's room to give him a bit more space, which suits my easy-going habit after that earlier collision.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 2:own_position (claimed: on my right; walls left 0.77, right 0.98)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_68f09b97_r1/dp4 (talk, agent 1, decision 2)
- seen: +4° (+ left), 6.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- history: 1.2 s ago "Give the elderly man plenty of room as we pass in the narrow passage", signal none, message "", sideways -0.68 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.45 m from you, the wall on your right 0.30 m.
- **intent:** Keep clear of the elderly man with the cane and suitcase as we pass
- **reason:** I have already stepped well to my right and there is 0.30 m of wall space on that side; holding this line keeps me out of his way while he passes with his cane and suitcase.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_8ea28db3_r1/dp3 (talk, agent 0, decision 2)
- seen: -2° (+ left), 7.4 m, walking, signal wave_on, changes ['moved_right'], age 25, width 0.5, traits []
- heard: "Hey! No worries — you go ahead, I'll keep to my side." (frame facing)
- history: 1.0 s ago "Greet the person I know and make room for them to pass safely.", signal wave_on, message "Oh, hey! Good to see you — sorry, I'm a bit glued to my phone here.", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.24 m from you, the wall on your right 0.51 m.
- **intent:** Acknowledge her kindness, keep to my side, and pass her safely while staying aware of the narrow gap.
- **reason:** She's keeping to her side as promised, and the right wall is close but there's still room; sliding a bit further right gives her clear space and avoids another collision like earlier today. I'll look up from my phone as I go.
- **message:** Thanks! Appreciate it — see you in class!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_02dfbadb_8ea28db3_r3/dp8 (talk, agent 1, decision 4)
- seen: -5° (+ left), 2.5 m, walking, signal nod, changes ['sped_up'], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- heard: "Got it, thanks!" (frame facing)
- history: 3.0 s ago "Greet my classmate and keep moving along, letting him pass on his way.", signal wave_on, message "Hey! Good to see you!", sideways +0.47 m (+ left)
- history: 2.0 s ago "Acknowledge him and step aside a little so he can pass safely since he's on his phone with a cane.", signal none, message "No worries, take care!", sideways +0.47 m (+ left)
- history: 1.0 s ago "Stay out of his path and let him pass on my left since I've already moved left twice", signal wave_on, message "Coming through on your right!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.31 m from you, the wall on your right 1.44 m.
- **intent:** Give him room and let him pass safely on his own side, since I've already moved left twice and he's on his phone
- **reason:** He's looking at his phone and using a cane, so slowing down a bit gives us both more time and space to pass without a bump.
- **signal:** hold_up_hand; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_9950986f_r1/dp4 (talk, agent 0, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal nod, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "Hi, sorry, I'm in a hurry — heading to the ER." (frame facing)
- history: 1.0 s ago "Greet her back and keep to my side so we can pass comfortably.", signal nod, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.24 m from you, the wall on your right 0.51 m.
- **intent:** Let her pass easily and safely on my left side since she's in a hurry and has a cane and suitcase.
- **reason:** She's hurrying to the ER with a cane and suitcase and looking at her phone, so easing my pace and giving her room lets her pass comfortably without either of us bumping.
- **message:** Hi! No worries — go ahead, I'll keep clear.
- **signal:** wave_on; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_9b752a36_r4/dp8 (talk, agent 1, decision 4)
- seen: +12° (+ left), 2.2 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep walking straight to the emergency room; I have no reason to give way, and there is room enough for both of us.", signal none, message "", sideways +0.00 m (+ left)
- history: 2.0 s ago "Keep walking straight to the emergency room at my usual pace, returning the nod politely but not yielding ground.", signal nod, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep walking straight to the emergency room without yielding ground; I have already returned the nod.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Hold my line to the emergency room; there is still room even though he has shifted toward my left.
- **reason:** He has moved over to my left, which opens a gap on my right; I am determined to keep my ground and get to the hospital without fuss.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says left, the plan turns none)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_b59c2831_r2/dp2 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Greet him warmly and keep walking, since he's waving me on and there's room to pass
- **reason:** He's a friendly classmate waving me on, and the passage is wide enough for us both to pass without trouble.
- **message:** Hey! Good to see you.
- **signal:** wave_on; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_02dfbadb_b59c2831_r4/dp7 (talk, agent 0, decision 4)
- seen: +18° (+ left), 2.4 m, walking, signal wave_on, changes [], age 25, width 0.5, traits ['They are looking at their phone as they walk.']
- heard: "Thanks! Take care too!" (frame facing)
- history: 3.0 s ago "Keep walking at my normal pace and pass Person 1, staying on my line since there's room on either side", signal none, message "", sideways -0.47 m (+ left)
- history: 2.0 s ago "Greet Person 1 back and continue past her, waving to acknowledge her wave.", signal wave_on, message "Hey! Hi, how's it going?", sideways -0.47 m (+ left)
- history: 1.0 s ago "Let her hurry past on the left side she's chosen, giving her plenty of room", signal wave_on, message "Oh no, hope everything's okay! Go ahead, take care!", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.24 m from you, the wall on your right 0.51 m.
- **intent:** Keep to my side so we pass each other cleanly and I don't crowd her
- **reason:** I've already given her plenty of room on my right and she's just beside me; there's no need to adjust further, so I'll just keep walking my line and let her pass.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_c36d5d49_r3/dp7 (talk, agent 0, decision 4)
- seen: +12° (+ left), 2.2 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- heard: "No worries, plenty of room!" (frame facing)
- history: 3.0 s ago "Acknowledge Person 1 as I pass, without slowing my pace toward the emergency room", signal nod, message "", sideways +0.00 m (+ left)
- history: 2.0 s ago "Acknowledge Person 1 warmly but keep moving quickly to the emergency room without stopping to chat.", signal wave_on, message "Hi! Sorry, I'm in a hurry — heading to the emergency room. Take care!", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep moving briskly toward the emergency room and pass Person 1 cleanly on the right side, since they've moved over to my left.", signal wave_on, message "Thank you — I'm hurrying on!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep my brisk pace and pass Person 1 cleanly on my right, since they've given me room and waved me on.
- **reason:** There's plenty of space, Person 1 has already moved aside and waved me through, and I'm in a hurry to reach the emergency room. No need to slow or shift further.
- **message:** Thanks, dear — coming through!
- **signal:** wave_on; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_cb859069_r2/dp3 (talk, agent 0, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal nod, changes [], age 70, width 0.5, traits ['They are walking with a cane.']
- history: 1.0 s ago "Give way politely to the elderly woman with a cane and keep the passage clear for her.", signal nod, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.24 m from you, the wall on your right 0.51 m.
- **intent:** Make room and let the elderly woman with the cane pass comfortably on my left
- **reason:** I have 0.51 m to my right wall and she needs clear space with her cane; moving further right keeps my side clear while she passes on the wider left side, and a polite gesture shows I've seen her.
- **message:** Good afternoon! Please, after you.
- **signal:** hold_up_hand; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_02dfbadb_cb859069_r3/dp6 (talk, agent 0, decision 3)
- seen: +0° (+ left), 4.9 m, walking, signal nod, changes [], age 70, width 0.5, traits ['They are walking with a cane.']
- history: 2.0 s ago "Give way to the elderly woman with a cane and keep a comfortable distance", signal none, message "", sideways -0.68 m (+ left)
- history: 1.0 s ago "Keep well clear of the elderly woman with the cane as we pass", signal none, message "", sideways -0.21 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.45 m from you, the wall on your right 0.30 m.
- **intent:** Let the elderly woman with the cane pass safely, staying well over to my right
- **reason:** I have already moved well to my right, leaving her plenty of room on her side of the passage, and I want to keep my pace steady so she can predict my path. A nod acknowledges hers politely.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_dbd98c92_r1/dp2 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal hold_up_hand, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "Excuse me, coming through — mind the suitcase." (frame facing)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Acknowledge them and give way to make room for the suitcase
- **reason:** They are elderly, using a cane, and pulling a large suitcase, so I'll shift toward the wall on my left to give them space to pass.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_02dfbadb_dbd98c92_r1/dp7 (talk, agent 1, decision 4)
- seen: -18° (+ left), 2.2 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- history: 3.0 s ago "Let Person 1 know I'm here and keep my line without colliding, since I'm in a hurry to the emergency room.", signal hold_up_hand, message "Excuse me, coming through — mind the suitcase.", sideways +0.00 m (+ left)
- history: 2.0 s ago "Acknowledge Person 1 and keep my line so we pass safely, since I'm in a hurry to the ER.", signal nod, message "Evening—good to see you. I'm heading to the emergency room, so I'll keep to my side.", sideways +0.00 m (+ left)
- history: 1.0 s ago "Acknowledge Person 1's courtesy and keep my line so we pass safely, since I'm in a hurry to the ER.", signal nod, message "Thanks—appreciate it. Coming through, I'll stay on my side.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep my line past Person 1 and stay on my way to the ER without colliding.
- **reason:** She waved me on and we have an understanding; I'm in a hurry, I've announced myself clearly, and holding my line keeps things predictable with the suitcase and cane.
- **message:** Thank you, dear—coming through on my side.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_02dfbadb_e57e5fb0_r4/dp4 (talk, agent 1, decision 2)
- seen: -2° (+ left), 7.4 m, walking, signal nod, changes ['moved_right'], age 25, width 0.5, traits []
- heard: "Yes, just a quick run for some groceries. Take care with that suitcase!" (frame facing)
- history: 1.0 s ago "Greet her warmly and keep to my side so we can pass comfortably", signal nod, message "Hello! Yes, late night errand run for me. Nice to see a familiar face.", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.25 m from you, the wall on your right 0.50 m.
- **intent:** Say goodnight and keep to my side of the passage so we pass safely
- **reason:** I've already moved to my right and she is on my left, so there is enough room for us to pass without crowding; keeping a steady pace is simple and she has a clear side.
- **message:** Thanks, will do! Good night!
- **signal:** wave_on; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_f3d09c23_r1/dp1 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep moving toward the emergency room without fuss, giving the woman room to pass.
- **reason:** She's coming straight at me, and I'm the easy-going sort, so I'll shift a bit toward the wider side on my right to let her pass cleanly.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_02dfbadb_f79677df_r1/dp6 (talk, agent 0, decision 3)
- seen: +6° (+ left), 4.8 m, walking, signal nod, changes [], age 70, width 0.5, traits ['They are walking with a cane.']
- heard: "Take care too, girl! See you in class." (frame facing)
- history: 2.0 s ago "Greet the older man warmly and keep walking, giving him plenty of room since he uses a cane", signal nod, message "Hello, Uncle! How nice to see you. How have you been?", sideways -0.68 m (+ left)
- history: 1.0 s ago "Keep the friendly greeting going while giving the older man with a cane plenty of room to pass", signal wave_on, message "I'm doing well, thanks! Just picking up a few things for lunch. Take care, Uncle!", sideways -0.21 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.45 m from you, the wall on your right 0.30 m.
- **intent:** Keep giving the older man with a cane plenty of room as we pass
- **reason:** He uses a cane and needs space; I have room on my right to move further aside while staying friendly and keeping the greeting going.
- **message:** See you in class, Uncle!
- **signal:** wave_on; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_02dfbadb_f79677df_r3/dp5 (talk, agent 1, decision 3)
- seen: +3° (+ left), 4.7 m, walking, signal eye_contact, changes [], age 25, width 0.5, traits []
- history: 2.0 s ago "Greet her warmly and keep walking along my line at my steady pace", signal nod, message "Hello, dear! Good to see you.", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep walking steadily on my line and greet her with a look as we pass", signal eye_contact, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Greet her again and keep my steady line while she passes on her own side
- **reason:** I am old and steady on my cane, and we already greeted each other happily; there is room for us both to pass without me dodging about.
- **message:** Hello again, dear! Go ahead, I've got my cane, I'll keep to my side.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_de176842_1caa9a84_r3/dp4 (talk, agent 0, decision 2)
- seen: -1° (+ left), 7.5 m, walking, signal eye_contact, changes ['moved_left'], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Give him plenty of room since he's on his phone, with a cane, and pulling a suitcase", signal none, message "", sideways +0.58 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.29 m from you, the wall on your right 1.46 m.
- **intent:** Keep well to the left to give him plenty of room, since he's distracted with his phone and has a cane and suitcase
- **reason:** I've already moved well over to my left, so there's enough space for him to pass safely; no need to change anything now.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says left, the plan turns none)

### rf49_round1_head_on_menu/T_head_on_de176842_3dee0df5_r4/dp2 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- heard: "Hi! Fancy meeting you here this late." (frame facing)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Greet them back and keep my line, acknowledging their wave to pass
- **reason:** They've waved me on and there's plenty of room in this passage; after being bumped earlier I'm keeping my own line steady at my usual pace.
- **message:** Hi! Small world — I'm just heading to the supermarket.
- **signal:** wave_on; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_de176842_51dfba80_r1/dp1 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Greet the young man I know from class and keep walking toward the supermarket.
- **reason:** I am determined and hold my ground; I have plenty of room and know this person, so I will greet him and keep my line at my usual pace.
- **message:** Hello there!
- **signal:** wave_on; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_de176842_68f09b97_r2/dp2 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep my course and pass by Person 1 without fuss
- **reason:** The passage is narrow but there is room for both of us to pass, and I am steady on my feet with my cane and suitcase; no need to yield.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_de176842_6ab9c72e_r2/dp7 (talk, agent 1, decision 4)
- seen: -23° (+ left), 2.7 m, walking, signal none, changes ['slowed_down'], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- history: 3.0 s ago "Greet him warmly and make room for him and his suitcase to pass", signal wave_on, message "Hi! Fancy seeing you here so late.", sideways +0.58 m (+ left)
- history: 2.0 s ago "Answer him warmly and keep giving him and his suitcase room to pass", signal eye_contact, message "Oh no, the ER? Hope everything's alright. I'm just off to the supermarket — grab some late-night snacks. Take care, okay?", sideways +0.11 m (+ left)
- history: 1.0 s ago "Give him plenty of room to pass with his cane and suitcase, staying friendly and easy-going", signal nod, message "Thanks! Night!", sideways +0.11 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.30 m from you, the wall on your right 1.45 m.
- **intent:** Keep well to my left so he and his suitcase can pass comfortably
- **reason:** I have already stepped well left and there is enough room; keeping my line lets him pass without fuss.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says left, the plan turns none)

### rf49_round1_head_on_menu/T_head_on_de176842_8ea28db3_r1/dp4 (talk, agent 1, decision 2)
- seen: +4° (+ left), 7.3 m, walking, signal wave_on, changes [], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- heard: "Thanks! See you in class." (frame facing)
- history: 1.0 s ago "Greet my classmate and give way to him since he waved me on and is using a cane and looking at his phone.", signal nod, message "Oh, hi! Good to see you. Go ahead, you first.", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.35 m from you, the wall on your right 0.40 m.
- **intent:** Acknowledge his thanks and keep to the side I've moved to, letting him pass safely.
- **reason:** He has already seen me and said thanks; I've shifted right, and there's still room on that side, so carrying on at a steady pace is easy-going and lets him pass without further fuss.
- **message:** Thanks! See you in class.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_de176842_9950986f_r1/dp5 (talk, agent 1, decision 3)
- seen: -5° (+ left), 5.0 m, walking, signal wave_on, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Take care! Text me later when you can." (frame facing)
- history: 2.0 s ago "Acknowledge my classmate with eye contact and keep moving past him; I have no time to lose getting to the ER.", signal eye_contact, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "acknowledge him briefly and keep moving quickly toward the emergency room", signal nod, message "Hi! Sorry, can't stop — I'm heading to the ER.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge him and keep moving toward the ER without stopping
- **reason:** I'm in a hurry to get to the emergency room, he's already waved me on and slowed down, so there's room to pass; no need to change my line.
- **message:** Thanks — I'll text you later!
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says stop_and_wait, the plan does not)

### rf49_round1_head_on_menu/T_head_on_de176842_9950986f_r3/dp4 (talk, agent 0, decision 2)
- seen: -5° (+ left), 7.3 m, walking, signal nod, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Let my classmate with the cane and suitcase pass comfortably, since she's busy on her phone.", signal wave_on, message "Hi! Coming through — let me give you some room.", sideways +0.58 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.29 m from you, the wall on your right 1.46 m.
- **intent:** Keep well to my left so my classmate with the cane and suitcase can pass without bumping into me
- **reason:** I already said I'd give her room and have moved left; moving a bit further left keeps the walkway clear for her, and the wall is close so I won't go too far.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says left, the plan turns none)

### rf49_round1_head_on_menu/T_head_on_de176842_b59c2831_r2/dp3 (talk, agent 0, decision 2)
- seen: -0° (+ left), 7.4 m, walking, signal nod, changes ['moved_right'], age 25, width 0.5, traits ['They are looking at their phone as they walk.']
- heard: "Hey, you're going the wrong way for the ER too, huh?" (frame facing)
- history: 1.0 s ago "Let her know I'm here and give her room to pass while she's on her phone", signal wave_on, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.34 m from you, the wall on your right 0.41 m.
- **intent:** Reassure her and let her pass while she's on her phone
- **reason:** She's distracted by her phone and it's late; easing off my pace gives her room to pass safely.
- **message:** Ha, no—just heading to the supermarket. You're fine, go ahead.
- **signal:** wave_on; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_de176842_b59c2831_r3/dp1 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Greet him briefly and make room so we pass safely without bumping into each other.
- **reason:** I'm a bit distracted on my phone and someone bumped into me earlier today, so I'll shift slightly right to give us a clear path while I look up and acknowledge him.
- **message:** Oh, hi! Sorry, I'm in a rush—heading to the ER.
- **signal:** eye_contact; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_de176842_c36d5d49_r2/dp4 (talk, agent 0, decision 2)
- seen: +4° (+ left), 7.3 m, walking, signal wave_on, changes ['moved_left'], age 25, width 0.5, traits []
- heard: "Hello! Go ahead, no problem—hope everything's alright." (frame facing)
- history: 1.0 s ago "Greet him warmly but make clear I can't stop to chat, and keep moving toward the ER.", signal nod, message "Hello! Sorry, I'm in a hurry—I'm heading to the emergency room.", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge him and keep moving straight toward the ER without stopping
- **reason:** He waved me on and I'm in a hurry to reach the emergency room; I'll hold my line and keep my pace since he's moving aside for me.
- **message:** Thank you—I'll keep going!
- **signal:** wave_on; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says stop_and_wait, the plan does not)

### rf49_round1_head_on_menu/T_head_on_de176842_dbd98c92_r1/dp1 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** I want to catch Person 1's eye so we can pass each other without a collision, since someone bumped into me earlier today.
- **reason:** I'm in a hurry to the emergency room and I hold my ground; making eye contact while continuing at my pace warns her to leave room, and it also lets me greet someone I know from class.
- **signal:** eye_contact; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_de176842_dbd98c92_r1/dp7 (talk, agent 1, decision 4)
- seen: -14° (+ left), 2.4 m, walking, signal wave_on, changes ['sped_up'], age 25, width 0.5, traits []
- heard: "Take your time, uncle!" (frame facing)
- history: 3.0 s ago "I want to catch Person 1's eye so we can pass each other without a collision, since someone bumped into me earlier today.", signal eye_contact, message "", sideways -0.00 m (+ left)
- history: 2.0 s ago "Acknowledge her warmly, keep my line and let her move aside as she offered.", signal nod, message "Hello, my dear! Thank you, that's kind of you.", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep my line and let her pass me on my right, staying steady with the cane and suitcase so we don't collide.", signal nod, message "Thank you, dear. Coming through, excuse me.", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.
- **intent:** Hold my line steadily so she passes on my right, keeping the cane and suitcase from catching her.
- **reason:** She waved me on and told me to take my time, and I'm determined to hold my ground after being bumped earlier; at this closing distance, sudden sideways moves with a cane and suitcase would risk a collision.
- **message:** Coming through, dear, thank you!
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says left, the plan turns none)

### rf49_round1_head_on_menu/T_head_on_de176842_e57e5fb0_r4/dp2 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Greet the person I know and keep moving along the passage, giving a little room as I pass.
- **reason:** Since I'm pulling a large suitcase and recently got bumped into, I'll shift slightly toward the right to leave clear space for Person 1 to pass without a collision.
- **message:** Good evening!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_de176842_f79677df_r1/dp5 (talk, agent 1, decision 3)
- seen: -7° (+ left), 4.8 m, walking, signal wave_on, changes ['moved_right'], age 25, width 0.5, traits []
- heard: "Take care, uncle!" (frame facing)
- history: 2.0 s ago "Keep my line and acknowledge her as we approach, since we know each other", signal eye_contact, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Greet her warmly while continuing on my way, keeping to my line as is my habit.", signal nod, message "Hello! Good to see you too, my dear.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge her kindness and keep my line as I walk on to the supermarket
- **reason:** She has already moved aside for me and waved me on; I am steady on my cane and prefer to hold my line rather than shuffle about at my age.
- **message:** Thank you, dear! You take care too.
- **signal:** wave_on; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_de176842_f79677df_r2/dp4 (talk, agent 1, decision 2)
- seen: +4° (+ left), 7.3 m, walking, signal eye_contact, changes ['moved_left'], age 25, width 0.5, traits []
- heard: "Hello! Good to see you too!" (frame facing)
- history: 1.0 s ago "Greet her warmly and keep walking my line toward the supermarket.", signal nod, message "Hello there, good to see you!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Greet my classmate again and keep walking steadily toward the supermarket.
- **reason:** We have already greeted each other warmly; there is plenty of room in the passage and I am determined to hold my line at my usual pace with my cane.
- **message:** Morning! Nice to see a familiar face.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu/T_head_on_de176842_f79677df_r2/dp7 (talk, agent 0, decision 4)
- seen: +13° (+ left), 2.2 m, walking, signal nod, changes [], age 70, width 0.5, traits ['They are walking with a cane.']
- heard: "Plenty of room, yes — you take care too!" (frame facing)
- history: 3.0 s ago "Acknowledge the older man I know from class and give him plenty of room to pass", signal nod, message "", sideways -0.47 m (+ left)
- history: 2.0 s ago "Greet the older man warmly and keep well to my right so he has plenty of room to pass with his cane", signal eye_contact, message "Hello! Good to see you too!", sideways -0.00 m (+ left)
- history: 1.0 s ago "Greet him back and keep well to my right so he can pass comfortably with his cane", signal nod, message "Morning! Take care, plenty of room here.", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.34 m from you, the wall on your right 0.41 m.
- **intent:** Keep to my right so the older man with his cane can pass comfortably
- **reason:** I already moved right and there's plenty of room; the gap is closing fast and no further adjustment is needed.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf49_round1_head_on_menu_abs/S_head_on_02dfbadb_51dfba80_r1/dp2 (silent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.98 m from the blue wall and 0.77 m from the yellow wall.
- **intent:** Give the older woman with the suitcase plenty of room to pass, since there's not much width and she's distracted by her phone.
- **reason:** She's elderly, pulling a suitcase, and looking at her phone, so she won't notice me well. Moving toward the yellow wall opens up space and keeps me clear of her path, and I'm easy-going so I don't mind giving way.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/S_head_on_02dfbadb_7eed7b59_r1/dp2 (silent, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.77 m from the blue wall and 0.98 m from the yellow wall.
- **intent:** make room for the elderly woman with the cane and suitcase so we can pass comfortably
- **reason:** She is elderly, using a cane and pulling a suitcase, and is distracted by her phone; giving way slightly lets her pass without trouble, and I have room on the yellow side.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/S_head_on_02dfbadb_800a3b04_r1/dp2 (silent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.98 m from the blue wall and 0.77 m from the yellow wall.
- **intent:** Give way to the elderly man with a suitcase and phone by moving towards the yellow wall so we can pass safely.
- **reason:** He is elderly, distracted by his phone, and pulling a large suitcase, so giving him more room makes passing safer and is the easy-going thing to do.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/S_head_on_02dfbadb_9950986f_r2/dp3 (silent, agent 0, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Give way to Person 1, who is distracted by her phone and pulling a suitcase, and pass safely.", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.24 m from the blue wall and 0.51 m from the yellow wall.
- **intent:** Give Person 1 plenty of room to pass, since she's distracted by her phone and pulling a suitcase.
- **reason:** She is looking at her phone and managing a cane and suitcase, so she needs a clear path; I'm already near the yellow wall, and moving further over keeps me out of her way.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/S_head_on_02dfbadb_b59c2831_r1/dp4 (silent, agent 0, decision 2)
- seen: -9° (+ left), 7.5 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 1.0 s ago "Keep walking to the supermarket, easing a little toward the blue wall so we pass cleanly since she's on her phone.", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.30 m from the blue wall and 1.45 m from the yellow wall.
- **intent:** Keep walking to the supermarket and pass her cleanly since she's on her phone
- **reason:** I've already moved toward the blue wall and there's enough space to pass without further adjusting; she's just someone I know from class and it's quiet, so no need to slow or stop.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/S_head_on_02dfbadb_b7fe7ead_r2/dp2 (silent, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.77 m from the blue wall and 0.98 m from the yellow wall.
- **intent:** Keep heading to the emergency room without slowing, holding my line and letting Person 1 pass.
- **reason:** I am in a hurry and tend to hold my ground; we are in the same classes, and there is enough room for us to pass without me changing course.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/S_head_on_02dfbadb_bcb9cb2c_r2/dp8 (silent, agent 0, decision 4)
- seen: +6° (+ left), 2.4 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep walking toward the supermarket without swerving, but be ready to prevent another collision.", signal none, message "", sideways -0.47 m (+ left)
- history: 2.0 s ago "Keep walking toward the supermarket while avoiding another collision with the approaching man", signal none, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Pass the approaching man without colliding, giving him room by the yellow wall.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.24 m from the blue wall and 0.51 m from the yellow wall.
- **intent:** Keep my line by the yellow wall and pass the man without colliding; I'm done swerving further.
- **reason:** I've already given him plenty of room by the yellow wall, and he has shifted toward the blue wall, so there's a clear gap between us. Holding my line is the safest and most predictable thing to do.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/S_head_on_de176842_02604456_r1/dp4 (silent, agent 0, decision 2)
- seen: -7° (+ left), 7.5 m, walking, signal none, changes ['moved_right'], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- history: 1.0 s ago "Make room for Person 1 and her suitcase to pass comfortably, since I know her and the passage is narrow.", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.40 m from the blue wall and 1.35 m from the yellow wall.
- **intent:** Make room for Person 1 and her suitcase to pass comfortably, since I know her and the passage is narrow.
- **reason:** I have already stepped towards the blue wall to give her space, so I just keep walking my line and let her pass on the yellow-wall side.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs/S_head_on_de176842_3dee0df5_r2/dp5 (silent, agent 0, decision 3)
- seen: +7° (+ left), 4.8 m, walking, signal none, changes [], age 25, width 0.5, traits ['They are walking with a cane.']
- history: 2.0 s ago "I recognize a classmate ahead who is walking with a cane; I'll make room so she can pass comfortably.", signal none, message "", sideways -0.58 m (+ left)
- history: 1.0 s ago "Recognise my classmate with the cane ahead and give her plenty of room to pass comfortably.", signal none, message "", sideways -0.11 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.45 m from the blue wall and 0.30 m from the yellow wall.
- **intent:** Give my classmate with the cane plenty of room to pass comfortably, since I've already moved close to the yellow wall.
- **reason:** I've already stepped well towards the yellow wall, so there's no more room to give; I'll just keep walking steadily along my line and let her pass.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/S_head_on_de176842_6ab9c72e_r1/dp2 (silent, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.87 m from the blue wall and 0.88 m from the yellow wall.
- **intent:** Give way to the man with the cane and suitcase since the passage is narrow
- **reason:** He has a cane and a large suitcase, so he needs more room; I'll move over to make space for him to pass
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/S_head_on_de176842_81bae7c3_r2/dp6 (silent, agent 0, decision 3)
- seen: +0° (+ left), 5.1 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep to my side and let Person 1 pass without fuss", signal none, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Keep to my side and let Person 1 pass without fuss", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.35 m from the blue wall and 0.40 m from the yellow wall.
- **intent:** Keep well to my side near the yellow wall and let Person 1 pass without fuss
- **reason:** I am already close to the yellow wall at 0.40 m and easy-going, so I will just keep walking along this line and let him pass.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_1868bff4_r1/dp3 (talk, agent 1, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal nod, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Make eye contact so she knows I'm here and we pass cleanly, while keeping my line and my speed since I'm in a hurry to the emergency room.", signal eye_contact, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.97 m from the blue wall and 0.78 m from the yellow wall.
- **intent:** Keep my line and pace toward the emergency room, but ease off slightly so we pass cleanly given the narrow gap and my suitcase.
- **reason:** I'm in a hurry but the passage is narrow and I'm pulling a large suitcase; a slight slowdown lets her pass without a collision or a repeat of what happened earlier today.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_2ec958bb_r1/dp2 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.77 m from the blue wall and 0.98 m from the yellow wall.
- **intent:** Give the elderly woman plenty of room since she's distracted by her phone
- **reason:** She's looking at her phone and may not notice me, so moving well towards the yellow wall gives her space and keeps a safe distance as we pass.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_5841fc4a_x10cdea10/dp1 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.77 m from the blue wall and 0.98 m from the yellow wall.
- **intent:** give way slightly to let the oncoming man pass comfortably
- **reason:** There is enough room, and being easy-going I'll shift a bit towards my side so we can pass without trouble.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_9b752a36_r2/dp4 (talk, agent 1, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal nod, changes ['moved_left'], age 25, width 0.5, traits []
- heard: "You're welcome. Have a good evening." (frame None)
- history: 1.0 s ago "Acknowledge his courtesy and keep moving to the emergency room without slowing down unnecessarily.", signal nod, message "Thank you, dear. That's very kind.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.97 m from the blue wall and 0.78 m from the yellow wall.
- **intent:** Keep my line and pace towards the emergency room, letting the young man pass on his side.
- **reason:** He has already stepped aside in courtesy and there is room to pass; I am in a hurry and hold my ground at my usual pace.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_b59c2831_r2/dp4 (talk, agent 1, decision 2)
- seen: -2° (+ left), 7.4 m, walking, signal wave_on, changes ['moved_left'], age 25, width 0.5, traits []
- heard: "Hey! Yeah, late-night snack run. Good to see you!" (frame None)
- history: 1.0 s ago "Greet him warmly while keeping to my side of the passage so we pass safely.", signal nod, message "Hey, fancy seeing you here this late!", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.44 m from the blue wall and 0.31 m from the yellow wall.
- **intent:** Acknowledge him warmly and keep to my side of the passage so we pass safely, since I'm already near the yellow wall.
- **reason:** I've already stepped over towards the yellow wall and there's room to pass; he waved me on and I'm easy-going, so I just keep walking my line to avoid bumping into him.
- **message:** Good to see you too! Take care out there.
- **signal:** wave_on; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_bcb9cb2c_r2/dp1 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.98 m from the blue wall and 0.77 m from the yellow wall.
- **intent:** Give way to the woman with the cane and suitcase who is coming towards me
- **reason:** She is walking with a cane and pulling a suitcase, so she needs more room; I have space on the yellow side and I'm easy-going about giving way.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_dbd98c92_r1/dp2 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal eye_contact, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.77 m from the blue wall and 0.98 m from the yellow wall.
- **intent:** Make it easy for the elderly man with the cane and suitcase to pass safely.
- **reason:** He's elderly, using a cane and pulling a suitcase while on his phone, and he's on my side—moving toward the blue wall gives him a clear path.
- **message:** Excuse me, coming through—let me give you some room.
- **signal:** wave_on; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_e57e5fb0_r1/dp3 (talk, agent 1, decision 2)
- seen: -1° (+ left), 7.4 m, walking, signal nod, changes ['moved_left'], age 25, width 0.5, traits []
- heard: "Hello! Sure, go ahead — I'll move over." (frame None)
- history: 1.0 s ago "Greet an acquaintance and make room so we pass safely without bumping.", signal nod, message "Hello there, coming through on your side.", sideways +0.37 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.34 m from the blue wall and 0.41 m from the yellow wall.
- **intent:** Acknowledge her courtesy and continue past safely on the yellow side.
- **reason:** She has already offered to move over and I am now well over towards the yellow wall, so I can keep walking straight on at my usual pace and pass her without bumping.
- **message:** Thanks, that's kind of you. Have a good night!
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_de176842_0f57f8a5_r2/dp1 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.87 m from the blue wall and 0.88 m from the yellow wall.
- **intent:** Greet Person 1 and shift towards the blue wall so they can pass with the suitcase
- **reason:** They're distracted by their phone and pulling a large suitcase, so giving them a bit more room on their side makes it easier for both of us to pass.
- **signal:** wave_on; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_de176842_0f57f8a5_r2/dp2 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.88 m from the blue wall and 0.87 m from the yellow wall.
- **intent:** Acknowledge Person 1's wave and keep walking along my line, holding my course since the passage is narrow and I have a suitcase.
- **reason:** We know each other from classes and she waved me on, so a nod is enough; holding my line keeps things predictable and avoids squeezing past her awkwardly.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_de176842_0f57f8a5_r2/dp5 (talk, agent 1, decision 3)
- seen: +12° (+ left), 5.0 m, walking, signal nod, changes ['moved_left'], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "Got it — I'll stay on the yellow side, see you!" (frame None)
- history: 2.0 s ago "Greet Person 1 and shift towards the blue wall so they can pass with the suitcase", signal wave_on, message "", sideways -0.57 m (+ left)
- history: 1.0 s ago "Greet Person 1, keep well over near the blue wall so they can pass with the suitcase, and keep walking to the supermarket.", signal wave_on, message "Hi! Coming through — I'll keep to the blue side.", sideways -0.10 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.30 m from the blue wall and 1.45 m from the yellow wall.
- **intent:** Keep clear of the suitcase, stay near the blue wall, and keep heading to the supermarket
- **reason:** Person 1 is taking the yellow side with the suitcase and I'm already well over near the blue wall, so there's room for both of us to pass.
- **message:** Great, thanks! See you!
- **signal:** wave_on; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs/T_head_on_de176842_1caa9a84_r1/dp3 (talk, agent 1, decision 2)
- seen: -4° (+ left), 7.6 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep to my side of the passage and give Person 1 room to pass, since I'm easy-going and there's plenty of space.", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.34 m from the blue wall and 0.41 m from the yellow wall.
- **intent:** Keep close to the yellow wall and slow a touch so Person 1 can pass comfortably without a close call.
- **reason:** I'm already near the yellow wall and easy-going; easing off the pace gives the oncoming woman extra room, especially after someone bumped into me earlier today.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_de176842_2ec958bb_r1/dp3 (talk, agent 1, decision 2)
- seen: -0° (+ left), 7.4 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "I want to keep to my line but make room so we don't bump into each other after what happened earlier today.", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.34 m from the blue wall and 0.41 m from the yellow wall.
- **intent:** Keep to my line near the yellow wall, since I've already made room, and hold my ground as we pass.
- **reason:** I've already stepped towards the yellow wall to make space, and I tend to hold my ground; no need to change course again.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_de176842_3cb16ae9_r2/dp6 (talk, agent 1, decision 3)
- seen: -6° (+ left), 4.7 m, walking, signal nod, changes ['moved_right'], age 25, width 0.5, traits []
- history: 2.0 s ago "I want to keep my line and make eye contact to acknowledge her as we pass, without slowing down.", signal eye_contact, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep my line and acknowledge her with a nod as we pass, without slowing down.", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.87 m from the blue wall and 0.88 m from the yellow wall.
- **intent:** Keep walking straight on my line as we pass, letting her have the room by the blue wall.
- **reason:** She has already moved toward the blue wall to make space, and I am determined to hold my line; there is enough clearance to pass without slowing or stepping aside.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_de176842_5767d932_r1/dp1 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.88 m from the blue wall and 0.87 m from the yellow wall.
- **intent:** Keep to my side and avoid a collision with the oncoming person without making a fuss
- **reason:** They are nearer the blue wall, so easing slightly toward the yellow wall gives us room to pass; I'm easy-going and don't want another bump like earlier today.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_de176842_5841fc4a_x42411b7c_flipped/dp1 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.88 m from the blue wall and 0.87 m from the yellow wall.
- **intent:** Keep to my side so we can pass each other easily
- **reason:** I'm easy-going and there's plenty of room; shifting slightly toward the yellow wall gives the oncoming man more space to pass.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_de176842_6ab9c72e_r2/dp7 (talk, agent 1, decision 4)
- seen: -3° (+ left), 2.3 m, walking, signal nod, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- heard: "See you!" (frame None)
- history: 3.0 s ago "Greet the person I know and make space for them to pass since they're pulling a suitcase and using a cane.", signal wave_on, message "Hi! Fancy seeing you here so late.", sideways +0.58 m (+ left)
- history: 2.0 s ago "Be friendly and keep well clear so they can pass safely with the cane and suitcase", signal wave_on, message "Hey! It's going well, just heading to the supermarket. You take care with that suitcase, yeah?", sideways +0.11 m (+ left)
- history: 1.0 s ago "Stay close to the yellow wall and let them pass safely with the cane and suitcase", signal wave_on, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.45 m from the blue wall and 0.30 m from the yellow wall.
- **intent:** Let them pass safely along the yellow wall side and say goodbye warmly
- **reason:** They're close to the yellow wall and I'm already near it, so slowing a bit while keeping my line gives them room to pass safely with the cane and suitcase.
- **message:** See you! Take care, yeah?
- **signal:** wave_on; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_de176842_74cb78c1_x10cdea10/dp2 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.87 m from the blue wall and 0.88 m from the yellow wall.
- **intent:** Keep walking to the supermarket and give Person 1 room to pass
- **reason:** I'm easy-going and tend to give way; moving slightly towards the yellow wall opens a clear path for the oncoming woman to pass on my blue-wall side.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_de176842_74cb78c1_x10cdea10/dp4 (talk, agent 1, decision 2)
- seen: -0° (+ left), 7.4 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the supermarket and give Person 1 room to pass", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.34 m from the blue wall and 0.41 m from the yellow wall.
- **intent:** Keep walking to the supermarket while giving Person 1 plenty of room to pass
- **reason:** I have already moved over towards the yellow wall, so there is enough space for the other person to pass. No further change is needed.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs/T_head_on_de176842_81bae7c3_r2/dp3 (talk, agent 1, decision 2)
- seen: -0° (+ left), 7.4 m, walking, signal wave_on, changes ['moved_left'], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- heard: "Oh, hello there! Late night for both of us, I suppose." (frame None)
- history: 1.0 s ago "Give the elderly woman plenty of room and avoid startling her, since she's looking at her phone and using a cane", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.34 m from the blue wall and 0.41 m from the yellow wall.
- **intent:** Greet her warmly and make sure she knows I'm giving her plenty of space to pass safely
- **reason:** She's elderly, looking at her phone, using a cane, and has waved me on. Since I'm already near the yellow wall giving her room, slowing slightly keeps things safe and friendly without startling her.
- **message:** Hello! Yes, late one for me too. Take your time, no rush.
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs/T_head_on_de176842_dbd98c92_r2/dp1 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.88 m from the blue wall and 0.87 m from the yellow wall.
- **intent:** Be friendly but get past safely; I'll shift toward the blue wall to give the older man with his cane and suitcase more room.
- **reason:** He is looking at his phone and pulling a suitcase, so he may not see me; giving him space is kind and reduces the chance of a bump.
- **signal:** wave_on; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs/T_head_on_de176842_f3d09c23_r2/dp4 (talk, agent 1, decision 2)
- seen: -0° (+ left), 7.4 m, walking, signal nod, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep a polite, steady pace and give a little room so we can pass comfortably.", signal nod, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.34 m from the blue wall and 0.41 m from the yellow wall.
- **intent:** I'll keep to the yellow side and pass comfortably, giving a friendly nod in return.
- **reason:** I'm already near the yellow wall with room to pass, and I'm easy-going, so I'll just keep my steady pace and acknowledge them politely.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/S_head_on_02dfbadb_1868bff4_r2/dp4 (silent, agent 1, decision 2)
- seen: -8° (+ left), 7.5 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep heading to the emergency room without losing time, while avoiding another collision like earlier today.", signal none, message "", sideways +0.37 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.34 m from the yellow wall and 0.41 m from the blue wall.
- **intent:** Keep heading to the emergency room at a steady pace, holding my line, while giving enough room to avoid another collision.
- **reason:** I am near the blue wall now with a large suitcase, and the oncoming woman is well over by the yellow wall, so our lines already clear each other. After the earlier bump I want to stay predictable rather than swerve again.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs_swap/S_head_on_02dfbadb_231c8154_r1/dp4 (silent, agent 0, decision 2)
- seen: -2° (+ left), 7.4 m, walking, signal none, changes ['moved_right'], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 1.0 s ago "Pass by the older man I know from class without a fuss, shifting enough room for him since he's distracted by his phone.", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.24 m from the yellow wall and 0.51 m from the blue wall.
- **intent:** Pass the older man I know from class smoothly, giving him room since he's distracted by his phone
- **reason:** I've already shifted toward the blue wall to make room, and at our speeds we'll pass fine; no need to change anything now.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs_swap/S_head_on_02dfbadb_800a3b04_r2/dp4 (silent, agent 0, decision 2)
- seen: -2° (+ left), 7.4 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep heading toward the emergency room without crowding the woman coming the other way.", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.24 m from the yellow wall and 0.51 m from the blue wall.
- **intent:** Keep making steady progress toward the emergency room while giving the woman coming the other way plenty of room, since I'm already near the blue wall.
- **reason:** I've already shifted over toward the blue wall and there's a clear gap now; I'm in a hurry for the ER, so I'll just keep walking straight at my usual pace and let her pass.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs_swap/S_head_on_02dfbadb_b6a40c60_r2/dp1 (silent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.98 m from the yellow wall and 0.77 m from the blue wall.
- **intent:** Keep walking to the supermarket without crowding the woman with the cane.
- **reason:** She's using a cane and looking at her phone, so giving her a bit more room on her side makes it easier for both of us to pass.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not)

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_1868bff4_r1/dp3 (silent, agent 1, decision 2)
- seen: +4° (+ left), 7.6 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep moving quickly toward the emergency room without colliding with the woman ahead", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Keep moving toward the emergency room without colliding, holding my line with my suitcase
- **reason:** I'm determined and hold my ground; there's plenty of gap on either side and I trust her to steer, but I'll keep my steady pace and watch her closely after what happened earlier today.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_1868bff4_r2/dp1 (silent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.88 m from the yellow wall and 0.87 m from the blue wall.
- **intent:** Keep moving toward the supermarket while making room for the man with the suitcase.
- **reason:** He is pulling a large suitcase and walking opposite me; shifting slightly toward the yellow wall gives him more clearance without slowing either of us.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_6ab9c72e_r2/dp2 (silent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.88 m from the yellow wall and 0.87 m from the blue wall.
- **intent:** Make room for Person 1 to pass so we don't bump into each other, and maybe say a friendly hello since I know her.
- **reason:** I'm easy-going and tend to give way; moving slightly towards the blue wall opens space on her side so we pass comfortably despite my cane and suitcase.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_74cb78c1_xaac00b3d/dp4 (silent, agent 1, decision 2)
- seen: -0° (+ left), 7.4 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "keep walking to the supermarket and pass by Person 1 with no fuss", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.34 m from the yellow wall and 0.41 m from the blue wall.
- **intent:** keep walking to the supermarket and pass by Person 1 without fuss
- **reason:** I have already shifted towards the blue wall, giving us enough room to pass; no need to change anything further.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_8ea28db3_r2/dp1 (silent, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Keep to my side so the man with the cane can pass comfortably
- **reason:** He's using a cane and looking at his phone, so giving him a bit more room on the yellow-wall side is the polite, easy-going thing to do.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_9950986f_r1/dp2 (silent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.88 m from the yellow wall and 0.87 m from the blue wall.
- **intent:** Make room for the woman with the cane and suitcase to pass safely.
- **reason:** She is looking at her phone and pulling a heavy suitcase, so giving her extra space on her side keeps us from bumping and is the polite thing to do.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_9950986f_r2/dp2 (silent, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Keep heading to the emergency room without losing time, staying on my line.
- **reason:** I'm walking in the middle of the passage with enough clearance, and I'm in a hurry to get to the ER; I'll hold my ground and let the gap between us sort itself out.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_b1d97a31_r1/dp1 (silent, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.88 m from the yellow wall and 0.87 m from the blue wall.
- **intent:** Keep to my side of the passage and let the young woman pass without any trouble.
- **reason:** She is slightly on the yellow-wall side, and after being bumped into earlier today I would rather give her a clear berth and avoid another collision.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_b59c2831_r2/dp4 (silent, agent 1, decision 2)
- seen: +4° (+ left), 7.3 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep heading to the emergency room without bumping into Person 1, and maybe catch their eye since I know them.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Acknowledge Person 1 as we pass and shift over a bit so we don't collide, since I know them from class.
- **reason:** I'm easy-going and tend to give way; after someone bumped into me earlier I want to avoid that, and moving towards the blue wall opens space while I glance up from my phone.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_bcb9cb2c_r2/dp7 (silent, agent 1, decision 4)
- seen: -3° (+ left), 2.5 m, walking, signal none, changes ['slowed_down'], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- history: 3.0 s ago "Give the woman with the cane and suitcase plenty of room as we pass", signal none, message "", sideways +0.58 m (+ left)
- history: 2.0 s ago "Keep clear of the woman with the cane and suitcase while passing her", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Give the woman with the cane and suitcase plenty of room as we pass, keeping to the blue side since she has moved towards the blue wall", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.45 m from the yellow wall and 0.30 m from the blue wall.
- **intent:** Give the woman with the cane and suitcase plenty of room as we pass
- **reason:** She is close to the blue wall already, so I will move as far to the blue side as I can to leave her space to pass safely.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_e57e5fb0_r2/dp4 (silent, agent 1, decision 2)
- seen: +7° (+ left), 7.5 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Make room for Person 1 to pass, since I'm pulling a suitcase and tend to give way", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.40 m from the yellow wall and 1.35 m from the blue wall.
- **intent:** Keep giving Person 1 plenty of room to pass, since I know her and I'm pulling a suitcase
- **reason:** I've already stepped well over toward the yellow wall, so there's clear space for her to pass; slowing or stopping would only get in the way at this point.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_f3d09c23_r1/dp9 (silent, agent 0, decision 5)
- seen: -8° (+ left), 0.7 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits ['They are walking with a cane.']
- history: 4.0 s ago "Keep to my side and let the man with the cane pass comfortably", signal none, message "", sideways -0.47 m (+ left)
- history: 3.0 s ago "Keep to my side and let the man with the cane pass comfortably", signal none, message "", sideways -0.00 m (+ left)
- history: 2.0 s ago "Stay close to the blue wall and let the man with the cane pass comfortably", signal none, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Give the man with the cane plenty of room to pass, staying close to the blue wall", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.34 m from the yellow wall and 0.41 m from the blue wall.
- **intent:** Give the man with the cane room to pass by hugging the blue wall
- **reason:** He uses a cane and is close and slowing, so I ease further toward the blue wall to leave him space and avoid a collision.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_f79677df_r2/dp6 (silent, agent 1, decision 3)
- seen: +7° (+ left), 4.8 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep walking to the supermarket and pass Person 1 without fuss", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep walking to the supermarket and pass Person 1 without fuss", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Keep walking to the supermarket and pass Person 1 without fuss, giving a little room
- **reason:** She has moved towards the blue wall, so there is more space on the yellow side; a small step over lets us pass comfortably without slowing my steady pace.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_02dfbadb_5841fc4a_x3d3cadc7_base/dp4 (talk, agent 1, decision 2)
- seen: -9° (+ left), 7.5 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the supermarket, giving way slightly to let the woman pass comfortably", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.44 m from the yellow wall and 0.31 m from the blue wall.
- **intent:** Keep to my side of the passage and let the woman pass comfortably
- **reason:** I'm already close to the blue wall and have given way; there's enough room for her to pass, so I just keep walking straight to the supermarket.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs_swap/T_head_on_02dfbadb_74cb78c1_r2/dp6 (talk, agent 0, decision 3)
- seen: -2° (+ left), 4.8 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 2.0 s ago "I'll keep walking but ease towards the blue wall so we can pass each other comfortably", signal none, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Keep to my new line near the blue wall and pass comfortably", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.24 m from the yellow wall and 0.51 m from the blue wall.
- **intent:** Keep to the blue-wall side and pass Person 1 comfortably, since they have also moved towards the blue wall
- **reason:** Person 1 has moved towards the blue wall too, narrowing the gap between us. Easing my speed gives us both a bit more room to pass without crowding.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_02dfbadb_7eed7b59_r2/dp3 (talk, agent 0, decision 2)
- seen: -1° (+ left), 7.4 m, walking, signal none, changes ['moved_right'], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Give the elderly woman with the cane and suitcase plenty of room to pass", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.24 m from the yellow wall and 0.51 m from the blue wall.
- **intent:** Keep well clear of the elderly woman with the cane and suitcase as we pass
- **reason:** I've already moved over towards the blue wall to give her plenty of room; staying on this line keeps a comfortable gap while she passes.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_02dfbadb_800a3b04_r2/dp2 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- heard: "Excuse me, coming through on your left." (frame None)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.77 m from the yellow wall and 0.98 m from the blue wall.
- **intent:** Let the young woman pass on my left and shift toward the yellow wall so she has room.
- **reason:** She called out she's coming through on my left, so I'll give way by easing toward the yellow wall and keep out of her path, since I'm easy-going and pulling a big suitcase.
- **message:** Sorry, sorry — go ahead, I'll move over.
- **signal:** hold_up_hand; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says right, the plan turns left)

### rf49_round1_head_on_menu_abs_swap/T_head_on_02dfbadb_9950986f_r2/dp2 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.98 m from the yellow wall and 0.77 m from the blue wall.
- **intent:** Keep my line and acknowledge my classmate as we pass; I'm in a hurry to the ER.
- **reason:** I'm determined and holding my ground at my usual pace, and a friendly nod returns the greeting without slowing my progress.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_02dfbadb_b59c2831_r2/dp2 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.98 m from the yellow wall and 0.77 m from the blue wall.
- **intent:** Keep heading to the emergency room while making friendly eye contact with someone I know from class
- **reason:** I'm in a hurry to the ER and Person 1 is far enough away; being easy-going, I'll just look up briefly to acknowledge them and keep walking my line.
- **signal:** eye_contact; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_02604456_r1/dp1 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Greet my classmate warmly and make room for him to pass, since I'm easy-going and pulling a suitcase.
- **reason:** He's near the yellow wall, so I'll shift slightly toward it to open a clear path on the blue side and also say hello since we know each other.
- **message:** Hi there!
- **signal:** wave_on; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_02604456_r1/dp3 (talk, agent 1, decision 2)
- seen: +7° (+ left), 7.5 m, walking, signal wave_on, changes ['moved_left'], age 25, width 0.5, traits []
- heard: "Hi! Thanks, I'll come through on my side." (frame None)
- history: 1.0 s ago "Greet my classmate warmly and make room for him to pass, since I'm easy-going and pulling a suitcase.", signal wave_on, message "Hi there!", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.40 m from the yellow wall and 1.35 m from the blue wall.
- **intent:** Keep to my side near the yellow wall and let my classmate pass on his side of the passage.
- **reason:** He said he'll come through on his side, and I've already shifted towards the yellow wall, so we can pass each other cleanly without fuss.
- **message:** Sounds good, see you!
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_1868bff4_r2/dp1 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.88 m from the yellow wall and 0.87 m from the blue wall.
- **intent:** Give way to the man with the suitcase by moving slightly toward the yellow wall, since he has a large suitcase and needs room
- **reason:** He is pulling a large suitcase and occupies more space; I am easy-going and prefer to make room so we can pass without trouble.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_1caa9a84_r1/dp2 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.88 m from the yellow wall and 0.87 m from the blue wall.
- **intent:** Make room for the man with the cane and suitcase to pass comfortably
- **reason:** He's distracted by his phone and dealing with a cane and suitcase, so I'll give him extra space by shifting toward the blue wall and stay easy-going about it.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_231c8154_r1/dp8 (talk, agent 0, decision 4)
- seen: +0° (+ left), 3.0 m, walking, signal wave_on, changes ['sped_up'], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- heard: "Go ahead, I've got room on this side." (frame None)
- history: 3.0 s ago "Acknowledge the older man I know from classes and give him room to pass, since he's distracted by his phone", signal nod, message "", sideways -0.47 m (+ left)
- history: 2.0 s ago "Greet the older man I know and give him room to pass safely while he's on his phone", signal wave_on, message "Hi, good to see you! Watch out ahead.", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep giving the older man room to pass while he's on his phone, easing along the blue wall side", signal nod, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.34 m from the yellow wall and 0.41 m from the blue wall.
- **intent:** Acknowledge him and slip past on the blue wall side since he's told me to go ahead
- **reason:** He waved me on and said he has room on his side, and he's distracted by his phone, so I'll ease slightly further toward the blue wall to pass safely.
- **message:** Thanks, coming through on the blue side!
- **signal:** wave_on; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_55c9ae40_r1/dp5 (talk, agent 0, decision 3)
- seen: -7° (+ left), 4.8 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- heard: "No problem, take your time." (frame None)
- history: 2.0 s ago "Let her know I'm here and keep my line toward the emergency room", signal hold_up_hand, message "Excuse me, coming through.", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep my line toward the emergency room without being slowed or bumped again", signal nod, message "Thank you, coming through.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Keep my line toward the emergency room without being bumped again
- **reason:** She has already said she'll give me time and nodded; I'm determined to hold my ground and keep my pace toward the ER.
- **message:** Thank you, I'll keep to my side.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_68f09b97_r1/dp2 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Give the older man with the cane and suitcase plenty of room by moving toward the yellow wall side, since he is closer to that side and needs space
- **reason:** He is elderly, using a cane and pulling a large suitcase, so he needs a clear path; stepping toward the blue wall keeps me out of his way while he stays near the yellow wall.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_74cb78c1_x10cdea10/dp2 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Keep to my side and pass Person 1 without fuss
- **reason:** She's slightly nearer the yellow wall, so giving a bit of space on the blue side makes passing easy and is the polite, easy-going thing to do.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_74cb78c1_x10cdea10/dp5 (talk, agent 0, decision 3)
- seen: +0° (+ left), 4.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 2.0 s ago "I'll keep a steady line and give way slightly so we pass comfortably", signal none, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Give way slightly so we pass comfortably", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.35 m from the yellow wall and 0.40 m from the blue wall.
- **intent:** Keep giving way towards the blue wall so we pass comfortably
- **reason:** I'm already close to the blue wall and easy-going; a small extra shift gives us both room without much room left to spare.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_74cb78c1_xaac00b3d/dp4 (talk, agent 1, decision 2)
- seen: -0° (+ left), 7.4 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "keep to my side and pass quietly", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.34 m from the yellow wall and 0.41 m from the blue wall.
- **intent:** keep to my side near the blue wall and pass quietly
- **reason:** I have already moved close to the blue wall, leaving plenty of room; staying the course keeps things simple and avoids bumping into her.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_8ea28db3_r2/dp5 (talk, agent 1, decision 3)
- seen: +5° (+ left), 5.2 m, walking, signal nod, changes [], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 2.0 s ago "Keep my usual line and give way slightly so the man with the cane can pass comfortably", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Greet my classmate warmly and keep giving him room to pass with his cane", signal wave_on, message "Hi! Good to see you!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Keep giving my classmate room to pass with his cane without slowing him down
- **reason:** He is looking at his phone and using a cane, so making a clear gap on his side lets him pass comfortably while I keep walking to the supermarket
- **message:** Coming through, thanks!
- **signal:** hold_up_hand; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_9950986f_r1/dp4 (talk, agent 0, decision 2)
- seen: +4° (+ left), 7.3 m, walking, signal nod, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "I see you — we're fine, plenty of room." (frame None)
- history: 1.0 s ago "Greet a classmate warmly and nudge her to watch where she's going, while giving her room to pass", signal wave_on, message "Hey! Watch out for the suitcase and the phone, yeah?", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.34 m from the yellow wall and 0.41 m from the blue wall.
- **intent:** Keep to my side near the blue wall and let my classmate pass comfortably with her cane and suitcase
- **reason:** She has acknowledged me and says there's plenty of room; I've already moved toward the blue wall, so I can just keep walking my line and we'll pass safely.
- **message:** Thanks! Take care on that side.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_9b752a36_r1/dp5 (talk, agent 1, decision 3)
- seen: +7° (+ left), 4.8 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- heard: "No problem, take care." (frame None)
- history: 2.0 s ago "Warn the approaching man and keep my line so I can get past with my suitcase", signal hold_up_hand, message "Please make way, I'm in a hurry to the hospital.", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep my line and hurry past him to the hospital, trusting he will move aside", signal nod, message "Thank you, thank you.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Keep my line and hurry past him toward the hospital
- **reason:** He has already acknowledged me and said to take care, so he is making way; holding my line keeps my suitcase clear and gets me there fastest.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_b1d97a31_r2/dp8 (talk, agent 0, decision 4)
- seen: +3° (+ left), 2.3 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep out of the way of the young woman coming towards me so we pass without a bump", signal none, message "", sideways -0.58 m (+ left)
- history: 2.0 s ago "Keep well clear of the young woman coming towards me so we pass without a bump, since someone walked into me earlier today", signal none, message "", sideways -0.11 m (+ left)
- history: 1.0 s ago "Keep close to the blue wall so the young woman and I pass without bumping, since I'm already near it.", signal nod, message "Coming through, excuse me.", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.45 m from the yellow wall and 0.30 m from the blue wall.
- **intent:** Stay close to the blue wall and let the young woman pass without a bump, returning her nod politely.
- **reason:** I'm already as close to the blue wall as I can comfortably be, and she has nodded at me, so keeping my line is the calmest way to pass safely without any fuss.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_b59c2831_r1/dp1 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Acknowledge Person 1 while stepping aside to avoid a collision, since someone bumped into me earlier.
- **reason:** I'm easy-going and want to give way; Person 1 is nearer the yellow wall, so I shift toward the blue wall to open a clear path, and I look up to acknowledge them since we know each other from class.
- **signal:** eye_contact; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_b59c2831_r1/dp2 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal eye_contact, changes [], age 25, width 0.5, traits ['They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.88 m from the yellow wall and 0.87 m from the blue wall.
- **intent:** greet her and keep to my side so we can pass easily
- **reason:** She's looking at her phone and we know each other from class; a small nod is friendly, and moving toward the blue wall gives us both room to pass without fuss.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_b7fe7ead_r2/dp3 (talk, agent 1, decision 2)
- seen: -4° (+ left), 7.3 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- heard: "Hey, good to see you — I'm in a hurry, heading to the ER. Keep to your side and I'll keep to mine." (frame None)
- history: 1.0 s ago "Greet the classmate I know and keep walking, giving a little room toward the blue wall so we pass easily.", signal nod, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.34 m from the yellow wall and 0.41 m from the blue wall.
- **intent:** Let him pass quickly since he's rushing to the ER, staying close to the blue wall so we don't bump.
- **reason:** He's in a hurry and asked us each to keep to our side; I'm already near the blue wall, so nudging a bit closer keeps my side clear and lets him pass easily.
- **message:** Hey! Good to see you too — go ahead, I'll keep to my side.
- **signal:** wave_on; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_b7fe7ead_r2/dp6 (talk, agent 0, decision 3)
- seen: -7° (+ left), 4.8 m, walking, signal wave_on, changes ['moved_right'], age 25, width 0.5, traits []
- heard: "All good — passing on your side!" (frame None)
- history: 2.0 s ago "Acknowledge her greeting, warn her I'm in a hurry, and keep my line without colliding", signal nod, message "Hey, good to see you — I'm in a hurry, heading to the ER. Keep to your side and I'll keep to mine.", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep my line at my usual pace and pass her without collision, since she has waved me on and agreed to keep to her side.", signal nod, message "Thanks — coming through on my side.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Keep my line at my usual pace and pass her cleanly since we've both agreed to stay on our sides.
- **reason:** She waved me on and said she's passing on my side, moving toward the blue wall. Holding my line keeps things predictable and avoids the collision I had earlier today.
- **message:** Coming through — staying my side.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_cb859069_r1/dp2 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.5, traits ['They are walking with a cane.']
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.88 m from the yellow wall and 0.87 m from the blue wall.
- **intent:** Give way to the elderly woman with a cane and pass her on my left side
- **reason:** She is elderly and using a cane, so I shift toward the blue wall to give her plenty of room and show respect as we pass.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** none

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_f79677df_r1/dp4 (talk, agent 0, decision 2)
- seen: +4° (+ left), 7.3 m, walking, signal nod, changes [], age 70, width 0.5, traits ['They are walking with a cane.']
- heard: "Thank you, that's kind of you. I'll keep to my side." (frame None)
- history: 1.0 s ago "Greet the elderly man, return his wave, and give him plenty of room by shifting toward the blue wall as we pass.", signal wave_on, message "Hello! Good to see you too. Please, after you — I'll keep to the blue wall side.", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.34 m from the yellow wall and 0.41 m from the blue wall.
- **intent:** Keep to the blue wall side and pass the elderly man with plenty of room.
- **reason:** I already stepped over toward the blue wall and he's keeping to his side, so I'll just keep walking my line and let him pass.
- **message:** You're welcome! Take care.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** none

## Every flag of a small rule (95)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_1868bff4_r1/dp9 (silent, agent 1, decision 5)
- seen: +34° (+ left), 0.9 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep moving quickly to the emergency room while holding my line, since I'm determined and won't be pushed around.", signal none, message "", sideways +0.00 m (+ left)
- history: 3.0 s ago "Keep moving quickly toward the emergency room without giving up my line, but avoid another head-on collision like earlier today.", signal none, message "", sideways +0.00 m (+ left)
- history: 2.0 s ago "Get past the woman ahead without another head-on collision, since she has drifted toward my line.", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Get past the woman without another head-on collision, keeping toward the emergency room", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Avoid a head-on collision with the woman while still getting past her toward the emergency room.
- **reason:** She's drifted toward my line and we'd meet in 0.4 s; I already moved left earlier, so shifting right now opens a gap on her other side and gets me past without another collision.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: ['slowed_down'])

### rf49_round1_head_on_menu/S_head_on_02dfbadb_51dfba80_r3/dp9 (silent, agent 1, decision 5)
- seen: +35° (+ left), 0.8 m, walking, signal none, changes ['slowed_down'], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 4.0 s ago "I want to make room for the older woman with the suitcase, since she is distracted by her phone and we know each other from class.", signal none, message "", sideways -0.67 m (+ left)
- history: 3.0 s ago "Keep making room for the older woman with the suitcase by giving her a wider berth, since she's distracted by her phone.", signal none, message "", sideways -0.20 m (+ left)
- history: 2.0 s ago "Give the older woman with the suitcase plenty of berth so she can pass safely while distracted by her phone.", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Give the distracted older woman with the suitcase plenty of room to pass safely without crowding her.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.45 m from you, the wall on your right 0.30 m.
- **intent:** Give the distracted older woman with the suitcase plenty of room to pass safely.
- **reason:** We would meet in about 0.4 s and she is looking at her phone while pulling a suitcase. I am already near the right wall with little room left to step aside, so slowing down a lot lets her pass safely without crowding her.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.7 m)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_55c9ae40_r3/dp7 (silent, agent 1, decision 4)
- seen: +11° (+ left), 2.5 m, walking, signal none, changes ['sped_up'], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 3.0 s ago "Give the elderly man plenty of room and avoid startling him since he's looking at his phone.", signal none, message "", sideways -0.67 m (+ left)
- history: 2.0 s ago "Give the elderly man plenty of room since he's distracted by his phone and using a cane", signal none, message "", sideways -0.20 m (+ left)
- history: 1.0 s ago "Keep well clear of the elderly man with the cane and give him a wide berth as we pass", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.45 m from you, the wall on your right 0.30 m.
- **intent:** Avoid the elderly man who is distracted by his phone and using a cane, but I'm already close to the right wall so I shouldn't crowd myself further
- **reason:** He is looking at his phone and has sped up, so I can't predict his line, and I'm already near the right wall with little room. Slowing a little gives him more time and space to pass without either of us bumping into the other.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_68f09b97_r2/dp4 (silent, agent 0, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the supermarket without dodging around people unnecessarily", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep walking steadily to the supermarket and let the young woman pass by, holding my line with my cane and suitcase
- **reason:** There's plenty of room and time yet at 7 metres apart, and I'm determined not to dodge around people unnecessarily. She can see an elderly man with a cane and a suitcase and will make room.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf49_round1_head_on_menu/S_head_on_02dfbadb_68f09b97_r3/dp5 (silent, agent 0, decision 3)
- seen: +6° (+ left), 4.8 m, walking, signal none, changes ['moved_right', 'turned'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep walking to the supermarket without yielding; a young person should make room for someone with a cane and suitcase.", signal none, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep walking straight to the supermarket without yielding; a young person should make room for someone with a cane and suitcase.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking straight to the supermarket; I have a cane and a suitcase and I'll hold my line.
- **reason:** I've held my ground twice already and she has room on her side; a young person can step aside for an older man with a cane and luggage.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf49_round1_head_on_menu/S_head_on_02dfbadb_68f09b97_r4/dp6 (silent, agent 0, decision 3)
- seen: +6° (+ left), 4.8 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep walking steadily toward the supermarket, expecting the young woman to make room for me.", signal none, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep heading straight to the supermarket without yielding, trusting the young woman to step aside.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking steadily to the supermarket without yielding, expecting the young woman to move aside.
- **reason:** I'm determined and hold my ground; she has already shifted to her left, so there's room for her to pass me on my right side without me changing course.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left']; position: ['left']); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_74cb78c1_xaac00b3d/dp7 (silent, agent 0, decision 4)
- seen: +11° (+ left), 2.5 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep walking toward the supermarket without fuss, giving the oncoming man a bit of room.", signal none, message "", sideways +0.00 m (+ left)
- history: 2.0 s ago "Keep walking to the supermarket without fuss, staying clear of the oncoming man.", signal none, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Keep walking to the supermarket and avoid bumping into the oncoming man, who has shifted toward my side.", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep walking to the supermarket while making sure I don't bump into the oncoming man
- **reason:** He's shifted toward my side and we'd meet in under a second; a small step right gives him room without fuss, and I still have space before the wall.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_into_line (changes shown: []); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_81bae7c3_r3/dp7 (silent, agent 1, decision 4)
- seen: +10° (+ left), 2.7 m, walking, signal none, changes ['slowed_down'], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- history: 3.0 s ago "Give the elderly woman with a cane plenty of room so we can pass safely.", signal none, message "", sideways -0.65 m (+ left)
- history: 2.0 s ago "Give the elderly woman with a cane plenty of room so we can pass safely, since she's drifting toward my right.", signal none, message "", sideways +1.30 m (+ left)
- history: 1.0 s ago "Keep clear of the elderly woman with a cane so we can pass safely, now giving her room on my right since she is drifting toward my left.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.43 m from you, the wall on your right 0.32 m.
- **intent:** Let the elderly woman with a cane pass safely without crowding her against the wall
- **reason:** She's drifting on my left and I have very little room on my right, but since I recently shifted left toward her, easing back right keeps a comfortable gap as we meet in about a second.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room on my left; gap 1.18 m, other 0.5 m wide)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_b1d97a31_r1/dp9 (silent, agent 1, decision 5)
- seen: nobody
- history: 4.0 s ago "Keep walking to the supermarket without any fuss, giving the elderly man room to pass.", signal none, message "", sideways +0.47 m (+ left)
- history: 3.0 s ago "Give the elderly man plenty of room to pass without fuss, staying clear of the wall on my right.", signal none, message "", sideways +0.94 m (+ left)
- history: 2.0 s ago "Keep giving the elderly man room to pass comfortably without fuss.", signal none, message "", sideways +0.47 m (+ left)
- history: 1.0 s ago "Give the elderly man plenty of room to pass while keeping clear of the wall, without fuss.", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.31 m from you, the wall on your right 1.44 m.
- **intent:** Get back to a sensible position in the passage and continue to the supermarket.
- **reason:** I've drifted close to the left wall to make way for the old man, but he's gone now and I'm nearly against the wall; I should move back toward the middle of the passage.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: []); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_b1d97a31_r4/dp4 (silent, agent 0, decision 2)
- seen: +9° (+ left), 7.1 m, walking, signal none, changes ['moved_left', 'turned'], age 25, width 0.5, traits []
- history: 1.2 s ago "Give the young woman plenty of room so we don't collide, since I was bumped earlier and don't want a repeat.", signal none, message "", sideways -0.68 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.45 m from you, the wall on your right 0.30 m.
- **intent:** Keep well clear of the young woman coming toward me, since she's drifting toward my side and I don't want another bump.
- **reason:** She's drifting to her left, which is my right, and I'm already close to the right wall; moving further right gives her the widest gap and avoids a collision.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left', 'turned']; position: ['left'])

### rf49_round1_head_on_menu/S_head_on_02dfbadb_b59c2831_r2/dp7 (silent, agent 0, decision 4)
- seen: +24° (+ left), 2.9 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 3.0 s ago "Keep heading to the supermarket and pass by Person 1 comfortably, since the passage is wide and we know each other.", signal none, message "", sideways -0.68 m (+ left)
- history: 2.0 s ago "Keep heading to the supermarket and pass Person 1 comfortably, giving a bit of room since they're distracted by their phone.", signal none, message "", sideways -0.68 m (+ left)
- history: 1.0 s ago "Pass Person 1 comfortably and get to the supermarket, giving them room since they're distracted by their phone.", signal none, message "", sideways -0.21 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.45 m from you, the wall on your right 0.30 m.
- **intent:** Pass Person 1 comfortably and get to the supermarket, keeping to my side since I'm already close to the right wall.
- **reason:** I've already shifted right three times and I'm only 0.30 m from the wall, so I have no room left to give way further. They've slowed down, and the passage gap should be enough to pass comfortably.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_b6a40c60_r2/dp4 (silent, agent 0, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep heading to the emergency room without losing time or awkwardly dodging, since there's enough room to pass.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep making steady progress toward the emergency room without wasting time, while giving a small, natural berth to the man approaching.
- **reason:** He's attractive and I don't want an awkward head-on meeting with no room to spare; a small shift right keeps my pace and line mostly intact while we pass.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_b6a40c60_r3/dp2 (silent, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **unreadable:** unknown_action: action: got 'step well to my left'; the menu's options are ('carry on', 'slow down a little', 'slow down a lot', 'stop and wait', 'step a little to your left', 'step a little to your right', 'step well to your left', 'step well to your right', 'step back')
- **flags:** 5:unreadable (unknown_action: action: got 'step well to my left'; the menu's options are ('carry on', 'slow down a little', 'slow down a lot', 'stop and wait', 'step a little to your left', 'step a little to your right', 'step well to your left', 'step well to your right', 'step back'))

### rf49_round1_head_on_menu/S_head_on_02dfbadb_dbd98c92_r4/dp3 (silent, agent 0, decision 2)
- seen: +2° (+ left), 7.6 m, walking, signal none, changes ['moved_left'], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Keep making my way to the supermarket without crowding the older man with the suitcase.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Give the older man with the cane plenty of room to pass without crowding him
- **reason:** He's elderly, using a cane and distracted by his phone with a suitcase, so I'll move well over to my left to leave him a clear path even though it's a bit tight against the wall.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.53 / 0.72 m)

### rf49_round1_head_on_menu/S_head_on_02dfbadb_e57e5fb0_r1/dp2 (silent, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **unreadable:** unknown_action: action: got 'step well to my left'; the menu's options are ('carry on', 'slow down a little', 'slow down a lot', 'stop and wait', 'step a little to your left', 'step a little to your right', 'step well to your left', 'step well to your right', 'step back')
- **flags:** 5:unreadable (unknown_action: action: got 'step well to my left'; the menu's options are ('carry on', 'slow down a little', 'slow down a lot', 'stop and wait', 'step a little to your left', 'step a little to your right', 'step well to your left', 'step well to your right', 'step back'))

### rf49_round1_head_on_menu/S_head_on_02dfbadb_f79677df_r1/dp5 (silent, agent 1, decision 3)
- seen: +6° (+ left), 4.8 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 2.0 s ago "I want to keep walking to the supermarket at my steady pace without fussing over an oncoming pedestrian.", signal none, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep my steady pace to the supermarket and greet my classmate as we pass.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep walking straight to the supermarket and greet my classmate as we pass, without fussing over the path.
- **reason:** I have the right to hold my line, and she has moved to her left, which is toward my side; but I am steady and determined and will simply keep my pace and greet her.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left']; position: ['left'])

### rf49_round1_head_on_menu/S_head_on_de176842_1868bff4_r2/dp6 (silent, agent 1, decision 3)
- seen: +12° (+ left), 5.0 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep moving quickly toward the emergency room while avoiding another collision.", signal none, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Keep my line and speed toward the emergency room but give a bit of room so we pass cleanly.", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.34 m from you, the wall on your right 0.41 m.
- **intent:** Keep moving toward the emergency room without another collision, holding my ground on the right side
- **reason:** I've already shifted well to my right twice and have room on that side; she moved to her left as well, so our lines should pass cleanly if I just keep my steady pace.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left']; position: ['left']); 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf49_round1_head_on_menu/S_head_on_de176842_1868bff4_r3/dp6 (silent, agent 0, decision 3)
- seen: +12° (+ left), 5.0 m, walking, signal none, changes ['moved_left'], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- history: 2.0 s ago "Keep to my side of the passage so the man with the suitcase can pass without fuss", signal none, message "", sideways -0.58 m (+ left)
- history: 1.0 s ago "Give the man with the suitcase plenty of room so we pass without fuss", signal none, message "", sideways -0.11 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.45 m from you, the wall on your right 0.30 m.
- **intent:** Keep giving the man with the suitcase room to pass without fuss
- **reason:** I'm already well over to my right near the wall, and he has moved to his left, so there's enough gap for us to pass; no need to change course.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left']; position: ['left']); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/S_head_on_de176842_231c8154_r2/dp10 (silent, agent 0, decision 5)
- seen: +52° (+ left), 0.6 m, walking, signal none, changes ['sped_up'], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 4.1 s ago "Keep walking to the supermarket without fussing, but give the older man on his phone a bit of room since he's distracted.", signal none, message "", sideways +0.10 m (+ left)
- history: 3.1 s ago "Give the distracted older man plenty of room so we pass without bumping, since he's on his phone.", signal none, message "", sideways -0.37 m (+ left)
- history: 2.1 s ago "Avoid bumping into the distracted older man while still getting past him on my way to the supermarket.", signal none, message "", sideways -0.47 m (+ left)
- history: 1.1 s ago "Pass the distracted older man safely without bumping into him, since we'll meet in about a second.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Avoid a collision with the distracted older man who is about to reach me, and keep moving toward the supermarket.
- **reason:** He's on his phone and only 0.2 s from me; a small shift right gives us a bit more clearance while I'm already close to the right side and there's still some wall space.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 2:own_position (claimed: on my right; walls left 0.77, right 0.98)

### rf49_round1_head_on_menu/S_head_on_de176842_231c8154_r2/dp9 (silent, agent 1, decision 5)
- seen: +38° (+ left), 0.8 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep heading to the emergency room while giving way to the young woman I know from my classes.", signal none, message "", sideways -0.57 m (+ left)
- history: 3.0 s ago "Keep making room for the young woman I know so we can pass without trouble, while staying on my way to the emergency room.", signal none, message "", sideways -0.10 m (+ left)
- history: 2.0 s ago "Give way to the young woman I know so we pass without trouble, keeping to the space near my right wall.", signal none, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep giving way to the young woman I know so we pass without trouble, staying near my right wall.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.44 m from you, the wall on your right 0.31 m.
- **intent:** Give the young woman I know a little more room so we pass without trouble, keeping to my right wall.
- **reason:** She has slowed down and we are about to meet; a small shift right, where I already have little space, lets her pass comfortably without much effort from me.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m); 3:intent_against_plan (intent says keep_to_side, the plan does not; intent says right, the plan turns none)

### rf49_round1_head_on_menu/S_head_on_de176842_9950986f_r4/dp6 (silent, agent 1, decision 3)
- seen: +7° (+ left), 4.8 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 2.0 s ago "Get to the emergency room quickly and keep my line in this narrow passage", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Get to the emergency room quickly and keep my line in this narrow passage", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Get to the emergency room quickly without being slowed or pushed off my line by the oncoming person.
- **reason:** I know him from my classes and he has already moved to his left, which opens space on my right; I'll hold my line with my cane and suitcase and keep moving quickly rather than yield more ground in this narrow passage.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left']; position: ['left']); 3:intent_against_plan (intent says slow_down, the plan does not)

### rf49_round1_head_on_menu/S_head_on_de176842_b59c2831_r4/dp5 (silent, agent 0, decision 3)
- seen: +1° (+ left), 4.9 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 2.0 s ago "Keep walking to the supermarket and pass Person 1 without fuss", signal none, message "", sideways +0.47 m (+ left)
- history: 1.0 s ago "Keep walking to the supermarket and pass Person 1 safely, giving her room since she's distracted by her phone", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.40 m from you, the wall on your right 1.35 m.
- **intent:** Keep walking to the supermarket and pass Person 1 without crowding her, since she's on her phone and we've both drifted left
- **reason:** She has moved over to her left and so have I, which puts us on a collision line near the left wall. I have room on my right, so a small step right gives us both space and avoids a bump.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left']; position: ['ahead'])

### rf49_round1_head_on_menu/S_head_on_de176842_ce2a06ef_r1/dp2 (silent, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **unreadable:** unknown_action: action: got 'step well to my right'; the menu's options are ('carry on', 'slow down a little', 'slow down a lot', 'stop and wait', 'step a little to your left', 'step a little to your right', 'step well to your left', 'step well to your right', 'step back')
- **flags:** 5:unreadable (unknown_action: action: got 'step well to my right'; the menu's options are ('carry on', 'slow down a little', 'slow down a lot', 'stop and wait', 'step a little to your left', 'step a little to your right', 'step well to your left', 'step well to your right', 'step back'))

### rf49_round1_head_on_menu/S_head_on_de176842_dbd98c92_r1/dp7 (silent, agent 1, decision 4)
- seen: +10° (+ left), 2.7 m, walking, signal none, changes ['sped_up', 'moved_left'], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep my line and my pace so the young woman from my class sees me being steady and confident, despite the cane and suitcase.", signal none, message "", sideways -0.47 m (+ left)
- history: 2.0 s ago "Keep my steady line and pace so the young woman from my class sees me as confident and composed, and make sure we don't collide in this narrow passage.", signal none, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Avoid colliding with the young woman in this narrow passage while keeping my dignity and steady presence, since someone walked into me earlier today.", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.34 m from you, the wall on your right 0.41 m.
- **intent:** Avoid another collision with the young woman while keeping my dignity and steady presence, and give myself room since I'm close to the right wall already.
- **reason:** She's moved over to her left toward my line and we'd meet in a second. Slowing slightly gives her room to pass without me bumping into anyone, and keeps me composed despite the cane and suitcase.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left', 'sped_up']; position: ['left']); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/S_head_on_de176842_dbd98c92_r1/dp9 (silent, agent 0, decision 5)
- seen: nobody
- history: 4.1 s ago "Make room for the older man with the cane and suitcase so we can pass safely.", signal none, message "", sideways -0.47 m (+ left)
- history: 3.1 s ago "Make sure there is safe room for the older man with the cane and suitcase to pass, since he is looking at his phone and not watching where he is going.", signal none, message "", sideways -0.94 m (+ left)
- history: 2.0 s ago "Give the older man with the cane and suitcase more room so he can pass safely, since he's drifting toward my left while looking at his phone.", signal none, message "", sideways -0.94 m (+ left)
- history: 1.0 s ago "Keep giving the older man plenty of room so we can pass safely, since he's on his phone with a cane and suitcase.", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.34 m from you, the wall on your right 0.41 m.
- **intent:** Keep walking to the supermarket now that the older man has passed and the way is clear.
- **reason:** I've already shifted well to my right for the man with the cane, and now I don't see anyone nearby, so I can just walk on along my line.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [])

### rf49_round1_head_on_menu/S_head_on_de176842_dbd98c92_r4/dp8 (silent, agent 1, decision 4)
- seen: -2° (+ left), 3.8 m, walking, signal none, changes ['sped_up', 'moved_right'], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep heading to the emergency room without a collision, though I am distracted by my phone and my suitcase and cane make me slow to dodge.", signal none, message "", sideways -0.47 m (+ left)
- history: 2.0 s ago "Keep moving toward the emergency room and pass Person 1 without another collision, since I recognize her from my classes.", signal none, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Keep moving toward the emergency room and pass Person 1 safely, since I recognize her from my classes.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.34 m from you, the wall on your right 0.41 m.
- **intent:** Avoid colliding with Person 1 while continuing toward the emergency room, even though she has shifted toward my right where I already am.
- **reason:** She has moved over to her right, which is my left, so the gap between us is closing on that side; shifting slightly to my left moves me away from her path while I keep my footing with the cane and suitcase.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['moved_right', 'sped_up']; position: ['ahead'])

### rf49_round1_head_on_menu/S_head_on_de176842_e57e5fb0_r1/dp6 (silent, agent 1, decision 3)
- seen: -1° (+ left), 4.9 m, walking, signal none, changes ['moved_right', 'turned'], age 25, width 0.5, traits []
- history: 2.1 s ago "Avoid bumping into Person 1 while getting past her in the narrow passage, especially after being walked into earlier today.", signal none, message "", sideways -0.47 m (+ left)
- history: 1.1 s ago "Pass Person 1 without bumping into her in this narrow passage, giving her plenty of room.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.35 m from you, the wall on your right 0.40 m.
- **intent:** Avoid a collision with Person 1 in the narrow passage, since she is drifting toward my right where the wall is close.
- **reason:** She is heading toward my right and the wall there is only 0.40 m away, so I have no room to keep right. Moving well left opens space and gives her room, which suits my easy-going habit and helps me avoid another bump after this morning's collision.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_0f57f8a5_r4/dp8 (talk, agent 0, decision 4)
- seen: +7° (+ left), 2.1 m, walking, signal hold_up_hand, changes [], age 25, width 0.5, traits []
- heard: "See you!" (frame facing)
- history: 3.0 s ago "Acknowledge my classmate and let her know I'm passing on my side, while I keep my line so we don't bump", signal nod, message "Eh, hi! Coming through, sorry ah—", sideways +0.00 m (+ left)
- history: 2.0 s ago "Keep my line and pass her on my side of the passage since she's waved me on", signal wave_on, message "Thanks ah—", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep my line and pass her on my side, since she's already waved me on and we've said our greetings", signal nod, message "See you!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep my line and pass my classmate on my side without bumping
- **reason:** She already waved me on and we've said our goodbyes; holding my line keeps things predictable as we pass.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['hold_up_hand']); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_231c8154_r2/dp6 (talk, agent 1, decision 3)
- seen: +6° (+ left), 4.8 m, walking, signal nod, changes ['moved_left'], age 25, width 0.5, traits []
- history: 2.0 s ago "Acknowledge my classmate and keep my path steady so we can pass each other smoothly.", signal nod, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Acknowledge my classmate's warning and keep a steady line so we can pass safely.", signal nod, message "Thanks, I'll watch it.", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep a steady line and pass my classmate smoothly, giving her room on my right.
- **reason:** She has moved over to her left, so easing a little to my right opens the gap and avoids a collision while still acknowledging her with a nod.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left']; position: ['left'])

### rf49_round1_head_on_menu/T_head_on_02dfbadb_231c8154_r4/dp9 (talk, agent 1, decision 5)
- seen: +39° (+ left), 2.1 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- heard: "Hi Uncle, I'm on your right!" (frame facing)
- history: 3.1 s ago "Acknowledge the familiar face and keep my path so we can pass easily", signal nod, message "", sideways -0.06 m (+ left)
- history: 2.1 s ago "Acknowledge her warning and keep my line so we pass smoothly", signal wave_on, message "Thanks, I see you!", sideways -0.06 m (+ left)
- history: 1.1 s ago "Keep to my own line and let her pass on her side, so we pass smoothly", signal none, message "", sideways -0.06 m (+ left)
- history: 0.1 s ago "Keep to my line and let her pass, stepping slightly aside to be safe", signal none, message "", sideways -0.06 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.84 m from you, the wall on your right 0.91 m.
- **intent:** Keep to my line and let her pass on my left, easing over slightly so we clear each other
- **reason:** She says she's on my right, but her warning plus her drift means I've been edging right into her path; moving a little left keeps me clear of her and the wall while I glance up from my phone.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:position_side (claimed: on my right; position: ['left'])

### rf49_round1_head_on_menu/T_head_on_02dfbadb_3cb16ae9_r3/dp5 (talk, agent 1, decision 3)
- seen: +3° (+ left), 5.0 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "Hi there!" (frame facing)
- history: 2.0 s ago "Keep walking toward the supermarket without changing course, glancing up briefly to track the oncoming woman.", signal none, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep my line to the supermarket and hold eye contact briefly to acknowledge her before looking back at my phone.", signal eye_contact, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Acknowledge her greeting politely while keeping my course to the supermarket.
- **reason:** She's friendly and I've already nodded back, but I'm determined to keep my line and I don't want to make a big thing of it in a narrow passage late at night.
- **message:** Hi! Sorry, I'm just on my way somewhere.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 2:own_signal (claimed: nodded; own earlier signals: ['eye_contact', 'none'])

### rf49_round1_head_on_menu/T_head_on_02dfbadb_51dfba80_r1/dp7 (talk, agent 0, decision 4)
- seen: +6° (+ left), 2.6 m, walking, signal eye_contact, changes [], age 25, width 0.5, traits []
- heard: "Just heading to the supermarket myself — good to see you!" (frame facing)
- history: 3.0 s ago "Keep my line but look up briefly to make eye contact so we pass without bumping", signal eye_contact, message "", sideways +0.00 m (+ left)
- history: 2.0 s ago "Greet the person warmly and keep my line so we pass each other cleanly.", signal nod, message "Hi! Lovely to see you.", sideways -0.00 m (+ left)
- history: 1.0 s ago "Greet my classmate warmly while keeping to my line so we can pass each other cleanly without bumping", signal eye_contact, message "I've been well, thank you! Just heading to the supermarket — how about you?", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Acknowledge them and keep a clear line so we pass without a bump, keeping the suitcase on my side.
- **reason:** There's more room on my right against the wall, and shifting slightly keeps my suitcase out of their path so we pass cleanly after last time's collision.
- **message:** Let's squeeze past — mind the suitcase!
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.42 / 0.63 m)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_5767d932_r2/dp2 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep moving toward the emergency room while staying aware of the oncoming man so we don't collide
- **reason:** I'm in a hurry, but after being walked into earlier I want to give a bit more clearance; there's more room on my right side against the wall.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.42 / 0.63 m)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_5767d932_r4/dp2 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep heading toward the emergency room while avoiding a collision with the oncoming man, giving him plenty of room on my right since I'm on the right side of the passage.
- **reason:** He's directly ahead coming toward me, and after being bumped into earlier I want to make my path clearly predictable. Shifting slightly left keeps me well inside the passage and leaves him a wide gap on his side.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 2:own_position (claimed: on my right; walls left 0.77, right 0.98)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_68f09b97_r3/dp3 (talk, agent 0, decision 2)
- seen: -5° (+ left), 7.3 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking steadily toward the supermarket without slowing, expecting Person 1 to make room.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Keep my line and expect the young woman to make room for an old man with a cane and suitcase
- **reason:** I am determined and hold my ground; the passage is wide enough for her to step aside, and I will not slow my steady pace toward the supermarket.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25]); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_68f09b97_r4/dp4 (talk, agent 0, decision 2)
- seen: -5° (+ left), 7.3 m, walking, signal nod, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking at my steady pace and let the young woman make room for me", signal eye_contact, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Acknowledge the young woman's nod and keep my steady line; she can step aside for an old man with a cane and suitcase
- **reason:** She nodded politely, so I'll return it and hold my ground at my usual pace; there's room enough for her to pass and I won't slow down or swerve for someone half my age.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25]); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_7eed7b59_r4/dp2 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Keep to my side and let the young man pass, since I'm easy-going and he's coming opposite
- **reason:** I'm near my right wall but shifting slightly right keeps me out of the middle line where he's walking, and I'll keep watching my phone and my footing with the cane and suitcase.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 2:own_position (claimed: on my right; walls left 0.77, right 0.98)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_9b752a36_r2/dp1 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Give the elderly woman with the suitcase plenty of room to pass
- **reason:** She is older and pulling a large suitcase, so I'll move over to give her space, and my right side has more room against the wall anyway.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.52 / 0.73 m)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_9b752a36_r4/dp5 (talk, agent 0, decision 3)
- seen: +3° (+ left), 4.7 m, walking, signal nod, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.']
- history: 2.0 s ago "Give way to the elderly woman pulling a suitcase by moving slightly aside", signal none, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Keep clear of the elderly woman with the suitcase and pass her without trouble", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.24 m from you, the wall on your right 0.51 m.
- **intent:** Give the elderly woman with the suitcase plenty of room to pass safely
- **reason:** She is elderly and pulling a large suitcase, and there is 0.51 m to the wall on my right. Moving further right gives her more space, and I have little room to my left.
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room on my left; gap 0.99 m, other 0.7 m wide)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_bcb9cb2c_r1/dp6 (talk, agent 1, decision 3)
- seen: +3° (+ left), 4.7 m, walking, signal hold_up_hand, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- heard: "Coming through on your left." (frame facing)
- history: 2.0 s ago "Acknowledge her with a friendly nod and give her plenty of room to pass, since she has a cane and a suitcase.", signal nod, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Keep well to the right and let her pass comfortably, since I've already shifted over and she has a cane and suitcase.", signal eye_contact, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.24 m from you, the wall on your right 0.51 m.
- **intent:** Reassure her and stay well to the right so she can pass with her cane and suitcase.
- **reason:** I've already moved well to my right and she's asked for the left, which is my right side. Staying my line keeps me out of her way.
- **message:** No problem, go ahead.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:misread_heard_side (restated: my right; the heard message puts it on my left); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_c36d5d49_r1/dp5 (talk, agent 0, decision 3)
- seen: +6° (+ left), 4.8 m, walking, signal nod, changes ['moved_left'], age 25, width 0.5, traits []
- heard: "Take care! Hope everything's alright." (frame facing)
- history: 2.0 s ago "Keep my pace, acknowledge the familiar face, and stay on my path toward the emergency room", signal eye_contact, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Acknowledge my classmate warmly but keep moving quickly toward the ER, staying on my side of the passage.", signal nod, message "Hi! Good to see you too — sorry, I'm in a hurry, on my way to the emergency room.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m.
- **intent:** Acknowledge their kindness and keep my pace, staying on my line since they've already shifted to their left to make room
- **reason:** They moved over for me, so there's no need to change my line; I'm in a hurry to the ER and want to keep my speed and hold my ground.
- **message:** Thank you — they've moved over, so we'll pass fine.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left']; position: ['left']); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_cb859069_r4/dp4 (talk, agent 1, decision 2)
- seen: +6° (+ left), 7.5 m, walking, signal nod, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep to my side of the passage and pass Person 1 safely, since he's already looking at me.", signal eye_contact, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 1.25 m from you, the wall on your right 0.50 m.
- **intent:** Return his greeting and keep to my side so we pass safely
- **reason:** He has already nodded and made eye contact, so he has seen me. I am already over to my right, away from his line, and I am in a hurry to the emergency room, so I will keep walking steadily along my line.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s)); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_02dfbadb_dbd98c92_r2/dp4 (talk, agent 1, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal hold_up_hand, changes ['moved_left'], age 25, width 0.5, traits []
- heard: "Yes, you go ahead — after you!" (frame facing)
- history: 1.0 s ago "Greet her warmly and keep my line toward the emergency room, acknowledging her wave.", signal wave_on, message "Evening! Nice to see you!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.78 m from you, the wall on your right 0.97 m.
- **intent:** Accept her offer and continue past her toward the emergency room, keeping my line.
- **reason:** She has waved me on, and I am determined to hold my line, but a slightly slower, steadier pace with my cane and suitcase will make it safer to pass her in this narrow, busy passage — especially after being bumped earlier today.
- **message:** Thank you kindly, I'll keep coming through!
- **signal:** nod; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['hold_up_hand']); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf49_round1_head_on_menu/T_head_on_de176842_1868bff4_r1/dp5 (talk, agent 1, decision 3)
- seen: -7° (+ left), 4.8 m, walking, signal nod, changes ['moved_right'], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep my line and pace, but make eye contact so she sees me and we don't collide, given the narrow passage and my suitcase.", signal eye_contact, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep my line and pace while holding eye contact so we pass cleanly without a collision, given the narrow passage and my suitcase.", signal eye_contact, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Hold my line and pace and keep eye contact so we pass cleanly on her right side.
- **reason:** She has already moved over to her right, which opens a gap on my left side, and I am determined to hold my ground without swerving into the wall with my suitcase.
- **signal:** eye_contact; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['moved_right']; position: ['right']); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_de176842_1868bff4_r2/dp5 (talk, agent 0, decision 3)
- seen: +0° (+ left), 4.6 m, walking, signal nod, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.']
- history: 2.0 s ago "Keep my line and stay predictable; there's room to pass a suitcase-puller easily.", signal none, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep my line and pass the suitcase-puller easily, staying predictable", signal eye_contact, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.
- **intent:** Acknowledge the nod and give the suitcase-puller a bit more room by shifting slightly to my left
- **reason:** He's pulling a large suitcase, so giving a little extra space on my side keeps the passing smooth and safe, while a friendly nod returns his greeting.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf49_round1_head_on_menu/T_head_on_de176842_3dee0df5_r2/dp2 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge my classmate and warn him to give me room so we don't collide like earlier today.
- **reason:** I know him from class, so a nod and a clear heads-up is friendly. I'm determined and tend to hold my ground, and I'm walking in a straight line in a narrow passage — he's the one coming toward me, so he should shift aside rather than me squeezing against the wall with my cane.
- **message:** Hey, watch out — I'm right in the middle here.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.63 / 0.62 m); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_de176842_51dfba80_r4/dp4 (talk, agent 0, decision 2)
- seen: -5° (+ left), 7.3 m, walking, signal nod, changes ['moved_right'], age 25, width 0.5, traits []
- heard: "I'm good, thank you! Take care, aunty." (frame facing)
- history: 1.0 s ago "Greet him warmly and keep walking, since he has waved me on and we know each other", signal wave_on, message "Good afternoon! How are you, dear?", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Greet him back warmly and keep walking in my line, holding my ground as usual.
- **reason:** He has already waved me on and spoken kindly; we know each other, so there is no need to dodge — I keep my steady pace and my line.
- **message:** Ay, take care, beta! See you in class.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['nod'])

### rf49_round1_head_on_menu/T_head_on_de176842_68f09b97_r1/dp7 (talk, agent 0, decision 4)
- seen: -15° (+ left), 2.2 m, walking, signal eye_contact, changes ['moved_right'], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep walking on my side of the passage and go about my business.", signal none, message "", sideways +0.00 m (+ left)
- history: 2.0 s ago "Keep walking straight on my side of the passage, holding my ground as I go to the supermarket", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep walking straight on my side of the passage and acknowledge the young woman's nod, holding my ground as I head to the supermarket.", signal nod, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep my line on my side of the passage, hold my ground, and pass the young woman without fuss.
- **reason:** She has already moved over to her right and is making eye contact, so there is room to pass; at 70 with a cane and a suitcase I keep a steady, predictable line rather than swerving late.
- **signal:** eye_contact; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['moved_right']; position: ['right']); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_de176842_81bae7c3_r1/dp2 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal nod, changes [], age 70, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge the familiar older woman and give her plenty of room, since she's distracted by her phone and using a cane
- **reason:** She's elderly, has a cane, and isn't watching where she's going, so I'll move well over to make sure she passes safely, and a nod returns her greeting.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf49_round1_head_on_menu/T_head_on_de176842_8ea28db3_r3/dp6 (talk, agent 1, decision 3)
- seen: +5° (+ left), 5.0 m, walking, signal nod, changes ['sped_up', 'moved_left'], age 25, width 0.5, traits ['They are walking with a cane.', 'They are looking at their phone as they walk.']
- heard: "Thanks! After you." (frame facing)
- history: 2.0 s ago "Greet my classmate warmly and acknowledge his wave-on gesture while carrying on past him.", signal wave_on, message "Hey! Good to see you too — nice surprise!", sideways -0.00 m (+ left)
- history: 1.0 s ago "Keep greeting my classmate and carry on walking past him, since we've already acknowledged each other.", signal wave_on, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge his courtesy and pass by him smoothly
- **reason:** He has moved to his left (my right) and is giving way with a cane and looking at his phone, so I shift slightly right to open a clear path for both of us.
- **message:** Thanks, see you around!
- **signal:** nod; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my right; changes shown: ['moved_left', 'sped_up']; position: ['left'])

### rf49_round1_head_on_menu/T_head_on_de176842_8ea28db3_r4/dp2 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Acknowledge her greeting and keep moving past her smoothly
- **reason:** She waved me on and there's plenty of room to pass; no need to change my line, and being friendly is natural since we know each other from class.
- **message:** Hey! Good to see you — thanks!
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf49_round1_head_on_menu/T_head_on_de176842_9b752a36_r1/dp2 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Give way to the elderly woman with the suitcase by easing toward my left so we can pass comfortably
- **reason:** She is elderly and pulling a large suitcase, so she needs room; I am easy-going and it's polite to shift slightly aside, and my left has a bit more space against the wall.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 7:wall_close (claimed: wall beside me; gaps to walls 0.63 / 0.62 m)

### rf49_round1_head_on_menu/T_head_on_de176842_c36d5d49_r3/dp5 (talk, agent 0, decision 3)
- seen: -6° (+ left), 4.7 m, walking, signal hold_up_hand, changes ['moved_right'], age 25, width 0.5, traits []
- heard: "Oh no, everything alright? Take care — let me know if you need anything!" (frame facing)
- history: 2.0 s ago "Greet my classmate warmly while continuing on my way to the emergency room.", signal nod, message "Hello! It's good to see a familiar face.", sideways +0.00 m (+ left)
- history: 1.0 s ago "Answer my classmate briefly and keep moving toward the emergency room without losing time.", signal nod, message "I'm on my way to the emergency room, actually — just heading there now. Good to see you!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.
- **intent:** Acknowledge his kindness, keep my line, and pass him without delay so I reach the emergency room fast.
- **reason:** He's already moved to his right, opening a gap on my left, and I don't want to lose any time; holding my line at my usual pace keeps things predictable as we pass.
- **message:** Thank you — I'm fine, just need to get there quickly. Good night!
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['moved_right']; position: ['right'])

### rf49_round1_head_on_menu/T_head_on_de176842_c36d5d49_r3/dp7 (talk, agent 0, decision 4)
- seen: -15° (+ left), 2.2 m, walking, signal wave_on, changes ['moved_right'], age 25, width 0.5, traits []
- heard: "Good night! Take care!" (frame facing)
- history: 3.0 s ago "Greet my classmate warmly while continuing on my way to the emergency room.", signal nod, message "Hello! It's good to see a familiar face.", sideways +0.00 m (+ left)
- history: 2.0 s ago "Answer my classmate briefly and keep moving toward the emergency room without losing time.", signal nod, message "I'm on my way to the emergency room, actually — just heading there now. Good to see you!", sideways -0.00 m (+ left)
- history: 1.0 s ago "Acknowledge his kindness, keep my line, and pass him without delay so I reach the emergency room fast.", signal nod, message "Thank you — I'm fine, just need to get there quickly. Good night!", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.88 m from you, the wall on your right 0.87 m.
- **intent:** Keep my line and pass him quickly on my way to the emergency room.
- **reason:** He has already moved to his right, giving me room on my side, and he waved me on; holding my line keeps me moving toward the emergency room without delay.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:moved_side (claimed: to my left; changes shown: ['moved_right']; position: ['right'])

### rf49_round1_head_on_menu/T_head_on_de176842_cb859069_r1/dp3 (talk, agent 1, decision 2)
- seen: -4° (+ left), 7.3 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep to my side of the passage and avoid another collision", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.41 m from you, the wall on your right 1.34 m.
- **intent:** Ask the young man to keep clear so we pass safely, and slow my pace to let him go by
- **reason:** Someone walked straight into me earlier today, so I want to be careful; I've already moved left, but I'll ease my pace and politely ask him to give way rather than risk another collision.
- **message:** Excuse me, young man, could I trouble you to give an old lady some room? I'm on my way to the hospital.
- **signal:** hold_up_hand; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf49_round1_head_on_menu/T_head_on_de176842_ce2a06ef_r1/dp5 (talk, agent 1, decision 3)
- seen: -11° (+ left), 5.6 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- history: 2.0 s ago "Acknowledge her, slow down and give her plenty of room so she can get past safely with her cane and suitcase", signal hold_up_hand, message "Hello, no problem — which side would you like me to pass on?", sideways +0.58 m (+ left)
- history: 1.0 s ago "Move over to my left so I pass on her right side as she asked, giving her and her suitcase plenty of room", signal nod, message "Got it, I'll pass on your right — coming through.", sideways +0.58 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.30 m from you, the wall on your right 1.45 m.
- **intent:** Keep to the left and pass the older woman on her right, leaving her room for her cane and suitcase
- **reason:** She asked me to pass on her right and I've already moved well over to my left; continuing straight keeps a clear gap for her.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s)); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu/T_head_on_de176842_dbd98c92_r4/dp5 (talk, agent 0, decision 3)
- seen: +0° (+ left), 4.8 m, walking, signal hold_up_hand, changes ['moved_left'], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- heard: "Will do — don't worry, I've got it. Excuse me a moment, coming through." (frame facing)
- history: 2.0 s ago "Make myself known to Person 1 so he notices me before we meet, and keep going at a steady pace.", signal wave_on, message "", sideways +0.47 m (+ left)
- history: 1.0 s ago "Greet him warmly and keep to my side so we pass safely, since he's distracted by his phone and pulling a suitcase", signal eye_contact, message "Hello! Good to see you too — careful with that suitcase, uncle.", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide. The wall on your left is 0.41 m from you, the wall on your right 1.34 m.
- **intent:** Keep clear of his suitcase and cane by passing on the open right side while he's distracted
- **reason:** He's drifted over to my left with a suitcase and cane and he's looking at his phone, so the right side has more room and I won't crowd him.
- **message:** Coming through on your right, uncle — go steady!
- **signal:** hold_up_hand; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

### rf49_round1_head_on_menu_abs/S_head_on_de176842_68f09b97_r2/dp5 (silent, agent 1, decision 3)
- seen: +7° (+ left), 4.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- history: 2.0 s ago "Keep to my side of the passage and make room for the older man with the cane and suitcase to pass.", signal none, message "", sideways -0.57 m (+ left)
- history: 1.0 s ago "Give the older man with the cane and suitcase plenty of room as we pass.", signal none, message "", sideways -0.10 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.30 m from the blue wall and 1.45 m from the yellow wall.
- **intent:** Keep giving the older man with the cane and suitcase plenty of room as we pass, since I'm already close to the blue wall.
- **reason:** He's elderly with a cane and a large suitcase, so slowing slightly gives him more time and space to pass safely, and I'm already near the blue wall so there's little room to step further over.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.7 m)

### rf49_round1_head_on_menu_abs/S_head_on_de176842_7eed7b59_r1/dp5 (silent, agent 0, decision 3)
- seen: +1° (+ left), 5.1 m, walking, signal none, changes ['slowed_down'], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 2.0 s ago "Give the elderly woman with the cane and suitcase plenty of room as we pass", signal none, message "", sideways -0.57 m (+ left)
- history: 1.0 s ago "Keep clear of the elderly woman as we pass, staying against the yellow wall", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.44 m from the blue wall and 0.31 m from the yellow wall.
- **intent:** Give the elderly woman plenty of room as we pass, but I'm already tight against the yellow wall so slowing down will keep the gap safe
- **reason:** She's elderly, using a cane, pulling a suitcase, and looking at her phone, so she may not hold her line. I'm already near the yellow wall with little space to step further, so easing my speed gives her time and space to pass safely.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.7 m); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs/S_head_on_de176842_7eed7b59_r2/dp4 (silent, agent 1, decision 2)
- seen: +4° (+ left), 7.6 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep to my side and let the young man pass without fuss, since I'm slow with a cane and suitcase and looking at my phone.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.87 m from the blue wall and 0.88 m from the yellow wall.
- **intent:** Let the young man pass safely without fuss; I'm slow with my cane and suitcase and looking at my phone.
- **reason:** I'm already on my side and easy-going; slowing slightly gives him more room and time to pass, which is safer for an elderly woman with a cane and suitcase in a busy, narrow passage.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25]); 3:intent_against_plan (intent says slow_down, the plan does not)

### rf49_round1_head_on_menu_abs/S_head_on_de176842_9b752a36_r1/dp3 (silent, agent 1, decision 2)
- seen: -4° (+ left), 7.3 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking toward the emergency room without changing my line, since the passage is narrow and there is room to pass.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.87 m from the blue wall and 0.88 m from the yellow wall.
- **intent:** Keep heading to the emergency room without being delayed, holding my line in the narrow passage.
- **reason:** He is young and steady on his feet, and the passage is too narrow for both of us plus my suitcase unless one of us gives way a bit; easing my pace slightly lets him pass safely without me having to stop.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m); 3:intent_against_plan (intent says carry_on, the plan does not)

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_1868bff4_r2/dp4 (talk, agent 1, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal nod, changes ['moved_left'], age 25, width 0.5, traits []
- history: 1.0 s ago "Pass Person 1 without incident, keeping to my side and holding my ground", signal eye_contact, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.97 m from the blue wall and 0.78 m from the yellow wall.
- **intent:** Acknowledge her nod and pass her cleanly, keeping to my side since I have the suitcase and no room to swerve
- **reason:** We have about 0.7 m of clearance each side of the middle; her nod suggests she'll keep her line too, and holding my ground with the suitcase avoids a clumsy sidestep at the last moment.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_55c9ae40_r2/dp4 (talk, agent 0, decision 2)
- seen: -2° (+ left), 7.4 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 1.0 s ago "Keep walking to the emergency room without being bumped into again", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.24 m from the blue wall and 0.51 m from the yellow wall.
- **intent:** Keep clear of the oncoming woman without losing my pace toward the emergency room
- **reason:** I've already shifted well over toward the yellow wall and have little room left; holding my line keeps things predictable, and I'm determined not to be pushed around again like earlier today.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_800a3b04_r1/dp2 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.98 m from the blue wall and 0.77 m from the yellow wall.
- **intent:** Let the older man with the suitcase know I'm passing and give him room
- **reason:** He's busy on his phone and pulling a suitcase, so I'll shift towards the yellow wall to give him space and avoid a collision.
- **message:** Excuse me, coming through on your left.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_800a3b04_r2/dp6 (talk, agent 0, decision 3)
- seen: -2° (+ left), 4.8 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- heard: "Take your time, I'm keeping to the yellow wall." (frame None)
- history: 2.0 s ago "Politely give way and keep heading to the emergency room without delay.", signal wave_on, message "Excuse me, sorry—just passing through.", sideways -0.47 m (+ left)
- history: 1.0 s ago "Acknowledge her kindness and keep moving toward the emergency room along the yellow wall side.", signal nod, message "Thank you, much appreciated.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.24 m from the blue wall and 0.51 m from the yellow wall.
- **intent:** Acknowledge her and slip past along the blue-wall side since she's keeping to the yellow wall
- **reason:** She's holding the yellow wall and waved me on, so I'll give a bit more clearance toward the blue wall while keeping my pace to reach the ER without delay.
- **message:** Thanks again—coming through on your left.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_800a3b04_r2/dp8 (talk, agent 0, decision 4)
- seen: -16° (+ left), 2.5 m, walking, signal wave_on, changes [], age 25, width 0.5, traits []
- heard: "Coming through, thank you!" (frame None)
- history: 3.0 s ago "Politely give way and keep heading to the emergency room without delay.", signal wave_on, message "Excuse me, sorry—just passing through.", sideways +0.00 m (+ left)
- history: 2.0 s ago "Acknowledge her kindness and keep moving toward the emergency room along the yellow wall side.", signal nod, message "Thank you, much appreciated.", sideways +0.47 m (+ left)
- history: 1.0 s ago "Acknowledge her and slip past along the blue-wall side since she's keeping to the yellow wall", signal nod, message "Thanks again—coming through on your left.", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.77 m from the blue wall and 0.98 m from the yellow wall.
- **intent:** Slip past Person 1 along the blue wall side, since she is keeping to the yellow wall, and keep heading to the emergency room.
- **reason:** She waved me on and is keeping to the yellow side, so I'll shift slightly further toward the blue wall to give her clear room while continuing on my way without delay.
- **message:** Coming through on your left, thank you!
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 3:intent_against_plan (intent says carry_on, the plan does not); 4:coming_through_on_your_side (own move: left)

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_81209f4f_xaac00b3d/dp3 (talk, agent 0, decision 2)
- seen: -5° (+ left), 7.3 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- history: 1.0 s ago "Acknowledge the attractive man and give him room to pass while staying friendly and relaxed", signal eye_contact, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.30 m from the blue wall and 1.45 m from the yellow wall.
- **intent:** Return his greeting and keep clear of him as we pass
- **reason:** I've already moved over near the blue wall to give him room, so I just keep walking my line and nod back politely.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s)); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_9950986f_r2/dp1 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.77 m from the blue wall and 0.98 m from the yellow wall.
- **intent:** Greet my classmate and let her know I'm passing, while moving aside to give her room since she's on her phone with a cane and suitcase.
- **reason:** She's distracted by her phone and managing a cane and large suitcase, so I'll give her plenty of space by shifting towards the blue wall and keep walking.
- **message:** Hi, excuse me — coming through on your left.
- **signal:** wave_on; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf49_round1_head_on_menu_abs/T_head_on_02dfbadb_ce2a06ef_r2/dp2 (talk, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.77 m from the blue wall and 0.98 m from the yellow wall.
- **intent:** greet Person 1 and politely ask them to make space so we don't bump into each other
- **reason:** I'm slow with a cane and suitcase, and someone recently walked into me; moving slightly toward the blue wall keeps me clear of them while staying polite since I give way easily.
- **message:** Hello dear, mind giving an old lady some room? I'm heading to the emergency room.
- **signal:** nod; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [25])

### rf49_round1_head_on_menu_abs/T_head_on_de176842_231c8154_r2/dp6 (talk, agent 1, decision 3)
- seen: +1° (+ left), 5.1 m, walking, signal nod, changes ['slowed_down'], age 25, width 0.5, traits []
- heard: "No problem, uncle — plenty of room. Go ahead." (frame None)
- history: 2.0 s ago "Acknowledge her greeting and keep moving, easing towards one side so we can pass safely.", signal wave_on, message "Hello! Thank you, I'll keep to my side.", sideways -0.57 m (+ left)
- history: 1.0 s ago "Acknowledge her kindly and give her room to pass by easing a little towards the blue wall.", signal nod, message "Thank you, I'll keep to my side.", sideways -0.10 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.30 m from the blue wall and 1.45 m from the yellow wall.
- **intent:** Keep moving toward the emergency room while giving Person 1 a clear path, since she says there's plenty of room.
- **reason:** She waved me on and said there's plenty of room, so I just keep walking straight along my line near the blue wall at my usual pace; no need to slow or shift further.
- **message:** Thank you, thank you — coming through.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['nod'])

### rf49_round1_head_on_menu_abs/T_head_on_de176842_b59c2831_r2/dp10 (talk, agent 1, decision 5)
- seen: -62° (+ left), 0.5 m, walking, signal none, changes ['sped_up'], age 25, width 0.5, traits []
- history: 4.0 s ago "To keep walking toward the emergency room while giving a friendly glance to someone I know from class.", signal eye_contact, message "", sideways +0.47 m (+ left)
- history: 3.0 s ago "Keep moving toward the emergency room while acknowledging my classmate and making room to pass safely.", signal wave_on, message "Hey, sorry, I'm in a bit of a rush tonight — mind if I squeeze past?", sideways +0.47 m (+ left)
- history: 2.0 s ago "Keep heading to the emergency room, staying along the yellow wall so we pass safely.", signal nod, message "Thanks — see you in class!", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep heading to the emergency room, staying close to the yellow wall so my classmate and I can pass safely.", signal nod, message "Thanks — see you in class!", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.35 m from the blue wall and 0.40 m from the yellow wall.
- **intent:** Keep close to the yellow wall and slip past my classmate safely toward the emergency room.
- **reason:** I'm already hugging the yellow wall with little room left, and we meet in a fraction of a second — slowing or side-stepping now would only make a collision more likely.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m)

### rf49_round1_head_on_menu_abs/T_head_on_de176842_f3d09c23_r2/dp7 (talk, agent 0, decision 4)
- seen: +3° (+ left), 2.3 m, walking, signal nod, changes [], age 25, width 0.5, traits ['They are walking with a cane.']
- history: 3.0 s ago "Give way to the man with the cane by stepping toward the yellow wall so we can pass easily.", signal nod, message "", sideways -0.58 m (+ left)
- history: 2.0 s ago "Keep giving way to the man with the cane and pass without fuss", signal nod, message "", sideways -0.11 m (+ left)
- history: 1.0 s ago "Keep well to the yellow wall side so the man with the cane can pass easily.", signal nod, message "", sideways -0.11 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 1.45 m from the blue wall and 0.30 m from the yellow wall.
- **intent:** Stay close to the yellow wall so the man with the cane can pass comfortably
- **reason:** I've already moved well over to the yellow wall side; there's little room left and I just need to keep walking straight so we pass each other smoothly.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m)

### rf49_round1_head_on_menu_abs/T_head_on_de176842_f79677df_r2/dp10 (talk, agent 1, decision 5)
- seen: +36° (+ left), 0.8 m, walking, signal eye_contact, changes ['sped_up'], age 25, width 0.5, traits []
- history: 4.0 s ago "Greet her warmly and keep walking on my side of the passage.", signal nod, message "Ah, good afternoon! Nice to see you again.", sideways -0.00 m (+ left)
- history: 3.0 s ago "Acknowledge her wave and keep to my side of the passage without slowing much.", signal wave_on, message "Thank you! After you, dear.", sideways -0.00 m (+ left)
- history: 2.0 s ago "Acknowledge her thanks warmly and keep walking steadily on my side to pass her safely.", signal nod, message "Ah, you're welcome! You too, take care ah!", sideways +0.00 m (+ left)
- history: 1.0 s ago "Keep to my side and pass her safely without slowing; she's already slowed and given way politely.", signal nod, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.88 m from the blue wall and 0.87 m from the yellow wall.
- **intent:** Keep steady on my line and pass her safely since we're about to meet, she's already slowed and given way.
- **reason:** She sped up slightly but we are only 0.3 s from meeting and there is barely room to shift; holding my line with a steady cane keeps things predictable and avoids a last-moment collision.
- **message:** Careful, dear — coming through on my side.
- **signal:** hold_up_hand; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:slowed (changes shown: ['sped_up']); 3:intent_against_plan (intent says slow_down, the plan does not)

### rf49_round1_head_on_menu_abs_swap/S_head_on_02dfbadb_2ec958bb_r1/dp4 (silent, agent 0, decision 2)
- seen: +2° (+ left), 7.3 m, walking, signal none, changes [], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- history: 1.0 s ago "Keep to my side so an elderly distracted woman can pass safely.", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.24 m from the yellow wall and 0.51 m from the blue wall.
- **intent:** Keep to my side so the elderly distracted woman can pass safely
- **reason:** I've already moved well over toward the blue wall and I'm close to it, so there's no room to give more; I'll just keep walking straight on my line and let her pass.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs_swap/S_head_on_02dfbadb_81bae7c3_r2/dp7 (silent, agent 0, decision 4)
- seen: -4° (+ left), 2.7 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 3.0 s ago "Make room for the young man to pass comfortably, since I'm easy-going and he's someone I know from class.", signal none, message "", sideways -0.47 m (+ left)
- history: 2.0 s ago "I've already moved over to give the young man room; I'll just keep walking calmly along my new line and let him pass.", signal none, message "", sideways -0.00 m (+ left)
- history: 1.0 s ago "Let the young man I know from class pass without any fuss, keeping to my side of the passage.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.24 m from the yellow wall and 0.51 m from the blue wall.
- **intent:** Keep my line near the blue wall and let the young man pass without fuss, easing off slightly so we don't bump.
- **reason:** We know each other from class and there's little room; I'm already over by the blue wall, so easing my pace lets him pass comfortably and avoids any awkward contact.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m)

### rf49_round1_head_on_menu_abs_swap/S_head_on_02dfbadb_9950986f_r2/dp1 (silent, agent 0, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.77 m from the yellow wall and 0.98 m from the blue wall.
- **intent:** Make room for Person 1, who is using a cane and pulling a suitcase while on her phone, so we can pass comfortably.
- **reason:** She has little room to maneuver with the cane and luggage, and I am closer to the blue wall side, so shifting that way gives her more space without slowing either of us much.
- **signal:** none; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.7 m)

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_5841fc4a_x42411b7c_flipped/dp8 (silent, agent 1, decision 4)
- seen: +3° (+ left), 2.3 m, walking, signal none, changes ['moved_left'], age 25, width 0.5, traits []
- history: 3.0 s ago "Keep walking to the supermarket and pass the oncoming woman without fuss.", signal none, message "", sideways +0.47 m (+ left)
- history: 2.0 s ago "Keep walking to the supermarket and pass the oncoming woman without fuss, giving her a bit of room.", signal none, message "", sideways +0.47 m (+ left)
- history: 1.0 s ago "Keep walking to the supermarket and pass the oncoming woman without fuss, staying near the blue wall where I already am.", signal none, message "", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.35 m from the yellow wall and 0.40 m from the blue wall.
- **intent:** Keep walking to the supermarket and slip past the oncoming woman near the blue wall without fuss.
- **reason:** I'm already close to the blue wall and she has moved over towards the blue wall too, so there's little room to give way further; holding my line and speed keeps things simple and we should pass cleanly.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m)

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_8ea28db3_r1/dp5 (silent, agent 0, decision 3)
- seen: -1° (+ left), 5.1 m, walking, signal none, changes ['moved_right'], age 25, width 0.5, traits []
- history: 2.0 s ago "Give way to Person 1 and avoid another collision, while keeping it friendly since I know her from class.", signal none, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Give way to Person 1 and keep it friendly, staying safely close to the blue wall as we pass.", signal none, message "", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.34 m from the yellow wall and 0.41 m from the blue wall.
- **intent:** Pass Person 1 safely and politely, keeping to the blue-wall side since she's a classmate and I've already shifted that way
- **reason:** I'm right next to the blue wall, so I have little room to move further; easing my pace lets her pass cleanly without another collision, and it's friendly since I know her.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m)

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_b59c2831_r2/dp6 (silent, agent 1, decision 3)
- seen: +0° (+ left), 4.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep heading to the emergency room without bumping into Person 1, and maybe catch their eye since I know them.", signal none, message "", sideways +0.47 m (+ left)
- history: 1.0 s ago "Acknowledge Person 1 as we pass and shift over a bit so we don't collide, since I know them from class.", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.35 m from the yellow wall and 0.40 m from the blue wall.
- **intent:** Pass Person 1 safely without another collision, giving them room since I'm close to the blue wall now
- **reason:** I'm already near the blue wall and have little room left to step aside; slowing a bit lets them pass cleanly, and I don't want a repeat of being walked into earlier today.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m); 3:intent_against_plan (intent says keep_to_side, the plan does not)

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_bcb9cb2c_r2/dp6 (silent, agent 0, decision 3)
- seen: -1° (+ left), 4.9 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep to my line and my pace, giving a steady, predictable path so we pass safely", signal none, message "", sideways -0.47 m (+ left)
- history: 1.0 s ago "Pass Person 1 safely without colliding, given my cane and suitcase, and keep a predictable line", signal none, message "", sideways -0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.35 m from the yellow wall and 0.40 m from the blue wall.
- **intent:** Pass Person 1 safely without colliding, keeping a predictable line given my cane and suitcase
- **reason:** I'm already close to the blue wall with little room to spare, and slowing slightly gives us a safer, more predictable gap as we meet.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m)

### rf49_round1_head_on_menu_abs_swap/S_head_on_de176842_cb859069_r2/dp6 (silent, agent 1, decision 3)
- seen: -1° (+ left), 4.9 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep out of the young man's way and avoid another collision while I head to the emergency room", signal none, message "", sideways +0.58 m (+ left)
- history: 1.0 s ago "Keep out of the young man's way and avoid another collision while I head to the emergency room", signal none, message "", sideways +0.11 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.45 m from the yellow wall and 0.30 m from the blue wall.
- **intent:** Stay clear of the young man and avoid another collision while heading to the emergency room
- **reason:** He is close and walking straight at me; easing my pace lets him pass safely, and I am already near the blue wall with little room to move further.
- **signal:** none; **coded:** side none, slowed True, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m)

### rf49_round1_head_on_menu_abs_swap/T_head_on_02dfbadb_231c8154_r2/dp5 (talk, agent 0, decision 3)
- seen: +0° (+ left), 4.9 m, walking, signal nod, changes [], age 70, width 0.5, traits ['They are looking at their phone as they walk.']
- heard: "Thank you! Go ahead, I'm fine." (frame None)
- history: 2.0 s ago "Greet the older man I know and give him room to pass", signal wave_on, message "", sideways -0.68 m (+ left)
- history: 1.0 s ago "Greet the older man I know and make sure he has space to pass on his side", signal wave_on, message "Hi! Good to see you — go ahead, I'm giving you room.", sideways -0.21 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.45 m from the yellow wall and 0.30 m from the blue wall.
- **intent:** Pass the older man safely, staying close to the blue wall so he has plenty of room
- **reason:** He has waved me on and said he's fine, and I've already moved over near the blue wall, so I just keep walking along my line and let him pass on his side.
- **message:** Thanks! Have a good day!
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['nod'])

### rf49_round1_head_on_menu_abs_swap/T_head_on_02dfbadb_2ec958bb_r1/dp9 (talk, agent 1, decision 5)
- seen: -20° (+ left), 0.6 m, walking, signal none, changes ['slowed_down'], age 25, width 0.5, traits []
- history: 4.0 s ago "Keep walking to the supermarket without being pushed off my line; I hold my ground after being bumped earlier.", signal none, message "", sideways +0.47 m (+ left)
- history: 3.0 s ago "Keep my line to the supermarket without being shoved, but I'll look up and make eye contact so this young man knows I'm here and we don't collide like this morning.", signal eye_contact, message "", sideways +0.47 m (+ left)
- history: 2.0 s ago "Hold my line toward the blue wall side and acknowledge this young man so we pass without a collision", signal nod, message "", sideways +0.47 m (+ left)
- history: 1.0 s ago "Hold my line and pass this young man without a collision, keeping to the blue wall side of the passage", signal eye_contact, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.45 m from the yellow wall and 0.30 m from the blue wall.
- **intent:** Hold my line on the blue wall side and signal the young man to keep clear so we pass without another collision
- **reason:** He has already slowed down and there is very little room left; holding my ground with a raised hand warns him to stay clear, and stepping aside again would put me against the blue wall.
- **signal:** hold_up_hand; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m)

### rf49_round1_head_on_menu_abs_swap/T_head_on_02dfbadb_2ec958bb_r2/dp2 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.98 m from the yellow wall and 0.77 m from the blue wall.
- **intent:** Keep walking straight to the supermarket; I was bumped earlier and I'm not yielding my line for someone on their phone-free approach.
- **reason:** I hold my ground and there's room to pass; no need to change my line.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:trait_phone (trait lines: 1)

### rf49_round1_head_on_menu_abs_swap/T_head_on_02dfbadb_68f09b97_r1/dp2 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.']
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.98 m from the yellow wall and 0.77 m from the blue wall.
- **intent:** Make space for the elderly man and his suitcase to pass safely
- **reason:** He is elderly, using a cane, and pulling a suitcase, so I should give way and clear some room on his side
- **message:** Excuse me, coming through on your right
- **signal:** hold_up_hand; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

### rf49_round1_head_on_menu_abs_swap/T_head_on_02dfbadb_800a3b04_r2/dp1 (talk, agent 1, decision 1)
- seen: -1° (+ left), 9.8 m, walking, signal none, changes [], age 70, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.98 m from the yellow wall and 0.77 m from the blue wall.
- **intent:** Move towards the blue wall so the older man with the suitcase and phone can pass safely.
- **reason:** He's looking at his phone and pulling a suitcase, so I'll give him room to pass without bumping into me.
- **message:** Excuse me, coming through on your left.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf49_round1_head_on_menu_abs_swap/T_head_on_02dfbadb_b59c2831_r2/dp6 (talk, agent 1, decision 3)
- seen: -2° (+ left), 4.8 m, walking, signal hold_up_hand, changes [], age 25, width 0.5, traits []
- heard: "No worries, go ahead!" (frame None)
- history: 2.0 s ago "Keep heading to the emergency room while making friendly eye contact with someone I know from class", signal eye_contact, message "", sideways +0.47 m (+ left)
- history: 1.0 s ago "Greet my classmate warmly but keep moving quickly toward the emergency room, shifting slightly to the blue wall to pass him cleanly.", signal wave_on, message "Hey! Fancy seeing you here this late — sorry, I'm in a bit of a rush.", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.44 m from the yellow wall and 0.31 m from the blue wall.
- **intent:** Pass my classmate cleanly on the blue-wall side and keep heading to the emergency room
- **reason:** He has already waved me on and stepped aside, so I can just keep my line along the blue wall and pass him without slowing down.
- **message:** Thanks! Have a good night!
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:signal_wave (signals shown: ['hold_up_hand'])

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_02604456_r2/dp6 (talk, agent 1, decision 3)
- seen: +0° (+ left), 4.8 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- history: 2.0 s ago "Accept his offer and keep walking past him with a small friendly greeting", signal nod, message "Thanks, that's kind of you!", sideways +0.47 m (+ left)
- history: 1.0 s ago "Move politely toward the blue wall as he suggested so we pass easily, keeping a friendly greeting.", signal nod, message "Thanks again, see you in class!", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.35 m from the yellow wall and 0.40 m from the blue wall.
- **intent:** Keep greeting him warmly and stay close to the blue wall so we pass each other easily, despite my suitcase.
- **reason:** I've already shifted well toward the blue wall and there's little room left, so carrying on at my usual pace keeps things smooth and friendly.
- **message:** Hi again! Coming through on the blue side.
- **signal:** wave_on; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m)

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_0f57f8a5_r2/dp8 (talk, agent 0, decision 4)
- seen: -11° (+ left), 2.4 m, walking, signal none, changes ['sped_up'], age 25, width 0.5, traits []
- history: 3.1 s ago "Keep walking to the supermarket and greet my classmate with a nod as we pass.", signal nod, message "", sideways +0.00 m (+ left)
- history: 2.1 s ago "Acknowledge my classmate and keep walking to the supermarket without slowing down", signal nod, message "Thanks! Good to see you too.", sideways -0.00 m (+ left)
- history: 1.1 s ago "Acknowledge my classmate's goodbye and keep heading to the supermarket", signal wave_on, message "Thanks! Take care!", sideways +0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.88 m from the yellow wall and 0.87 m from the blue wall.
- **intent:** Keep my line and pace to the supermarket; the passage is narrow and I'm pulling a suitcase, so I'll hold my ground and let them pass.
- **reason:** I'm determined and tend to hold my ground, and we're nearly at each other with little room either side; steady walking is safest with a big suitcase.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.7 + 0.5 m)

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_55c9ae40_r1/dp10 (talk, agent 1, decision 5)
- seen: nobody
- heard: "Thank you, coming through." (frame None)
- history: 4.0 s ago "Give the elderly man with a cane plenty of room to pass and keep walking to the supermarket.", signal nod, message "Of course, go ahead.", sideways +0.58 m (+ left)
- history: 3.0 s ago "Keep well clear of the elderly man with the cane and continue to the supermarket.", signal nod, message "No problem, take your time.", sideways -0.00 m (+ left)
- history: 2.0 s ago "Give the elderly man with the cane plenty of room and keep walking to the supermarket.", signal nod, message "", sideways +0.00 m (+ left)
- history: 1.0 s ago "Reassure the elderly man and keep clear while he passes on the yellow side of me.", signal hold_up_hand, message "Go ahead, I've given you room.", sideways -0.00 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.46 m from the yellow wall and 0.29 m from the blue wall.
- **intent:** Let the elderly man with the cane pass safely on the yellow side while I keep to the blue side and carry on to the supermarket.
- **reason:** I'm already well over near the blue wall giving him room, and he's just thanking me, so there's nothing more to do but keep walking straight ahead at my pace.
- **message:** You're welcome, all clear.
- **signal:** wave_on; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:trait_elderly (ages shown: [])

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_5767d932_r1/dp2 (talk, agent 1, decision 1)
- seen: -0° (+ left), 9.8 m, walking, signal none, changes [], age 25, width 0.7, traits ['They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.87 m from the yellow wall and 0.88 m from the blue wall.
- **intent:** Give a friendly heads-up so she isn't startled from her phone, and keep to my side to pass safely
- **reason:** She's absorbed in her phone and pulling a big suitcase, so a small shift toward the blue wall gives us comfortable clearance without making a fuss.
- **message:** Excuse me, coming through on your left.
- **signal:** none; **coded:** side left, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: left)

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_74cb78c1_x10cdea10/dp7 (talk, agent 0, decision 4)
- seen: +3° (+ left), 2.3 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 3.0 s ago "I'll keep a steady line and give way slightly so we pass comfortably", signal none, message "", sideways -0.57 m (+ left)
- history: 2.0 s ago "Give way slightly so we pass comfortably", signal none, message "", sideways -0.57 m (+ left)
- history: 1.0 s ago "Keep giving way towards the blue wall so we pass comfortably", signal none, message "", sideways -0.10 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.45 m from the yellow wall and 0.30 m from the blue wall.
- **intent:** Keep close to the blue wall so we can pass each other comfortably
- **reason:** I'm already near the blue wall and there's no room to move further over, so holding my line is the easy-going thing to do.
- **signal:** none; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m)

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_b1d97a31_r2/dp6 (talk, agent 0, decision 3)
- seen: +1° (+ left), 4.9 m, walking, signal none, changes [], age 25, width 0.5, traits []
- history: 2.0 s ago "Keep out of the way of the young woman coming towards me so we pass without a bump", signal none, message "", sideways -0.58 m (+ left)
- history: 1.0 s ago "Keep well clear of the young woman coming towards me so we pass without a bump, since someone walked into me earlier today", signal none, message "", sideways -0.11 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 1.45 m from the yellow wall and 0.30 m from the blue wall.
- **intent:** Keep close to the blue wall so the young woman and I pass without bumping, since I'm already near it.
- **reason:** I've already moved well over towards the blue wall and there's little room left; staying steady on my line keeps things predictable so she can pass on the yellow side.
- **message:** Coming through, excuse me.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 7:no_room (claimed: no room; passage 1.75 m, bodies 0.5 + 0.5 m)

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_b7fe7ead_r2/dp2 (talk, agent 0, decision 1)
- seen: +0° (+ left), 9.8 m, walking, signal nod, changes [], age 25, width 0.5, traits []
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.88 m from the yellow wall and 0.87 m from the blue wall.
- **intent:** Acknowledge her greeting, warn her I'm in a hurry, and keep my line without colliding
- **reason:** I'm determined and hold my ground, but after being walked into earlier today I want to be clear about my line; we have plenty of room to pass at 0.87 m apart.
- **message:** Hey, good to see you — I'm in a hurry, heading to the ER. Keep to your side and I'll keep to mine.
- **signal:** nod; **coded:** side none, slowed False, stopped False, backed up False
- **flags:** 1:speech (heard: 0 message(s))

### rf49_round1_head_on_menu_abs_swap/T_head_on_de176842_dbd98c92_r2/dp3 (talk, agent 0, decision 2)
- seen: -4° (+ left), 7.3 m, walking, signal eye_contact, changes [], age 70, width 0.7, traits ['They are walking with a cane.', 'They are pulling a large suitcase.', 'They are looking at their phone as they walk.']
- history: 1.0 s ago "Give way to the older man with a cane and suitcase who is distracted by his phone", signal none, message "", sideways +0.47 m (+ left)
- place: - You are in a passage 1.75 m wide, between the yellow wall and the blue wall. You are 0.40 m from the yellow wall and 1.35 m from the blue wall.
- **intent:** Warn the older man I know from class that I'm passing on his right, and give him room with his cane and suitcase
- **reason:** He's distracted by his phone and pulling a suitcase near the yellow wall; moving well toward the blue wall keeps clear of both him and his luggage and he'll hear my voice to look up
- **message:** Hello uncle, excuse me, coming through on your right side.
- **signal:** wave_on; **coded:** side right, slowed False, stopped False, backed up False
- **flags:** 4:coming_through_on_your_side (own move: right)

