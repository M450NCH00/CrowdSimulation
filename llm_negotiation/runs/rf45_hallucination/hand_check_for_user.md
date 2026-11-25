# RF-45: 20 hand-check judgements for the user to agree or correct

Issue #134, task 4. The assistant judged 337 decision points (`hand_check_judgements.json`). These 20 cover each kind of call, including the coding choices in `report.md`, section 4. For each, say **agree** or **disagree**. A disagreement changes the judgement file, and the precision and shares are recomputed.

"View" is what the agent's prompt showed. Bearings: + is to the agent's left.

| # | Decision point | What the agent said | What the view showed | Judgement |
| --- | --- | --- | --- | --- |
| 1 | rf40 `T_head_on_02dfbadb_9950986f_r1` dp5 | "told me to go ahead on my right, but since he's facing me that's my left" | heard "plenty of room on your right" | **hallucination** (misread heard side; RF-40's E3) |
| 2 | rf40 `T_head_on_02dfbadb_7eed7b59_r2` dp12 | "He has offered me room on his left, which is my right" | heard "giving you room on your left" | **hallucination** (misread heard side) |
| 3 | rf40 `T_head_on_02dfbadb_51dfba80_r3` dp4 | "she keeps her side (my right) and I keep my left" | heard "you keep to your left, I'll stay my side" | **not** (the "(my right)" is where she stays; keeping left is right) |
| 4 | rf40 `S_head_on_02dfbadb_1868bff4_r1` dp3 | "she is drifting to my right" | changes: slowed, turned; straight ahead | **hallucination** (a turn is not a drift to one side) |
| 5 | rf39 `T_head_on_02dfbadb_5767d932_r3` dp9 | "He's already moved to his right" | he moved over to the agent's right (= his left) | **hallucination** (wrong frame) |
| 6 | rf40 `T_head_on_02dfbadb_e57e5fb0_r1` dp7 | "She has moved over to her left, which is my right" | she moved to the agent's left, but said "I'll keep to the left" | **not** (it restates her words correctly) |
| 7 | rf40 `N_head_on_02dfbadb_2ec958bb_r3` dp4 | "She is drifting to my right" | no change; she is 27° to the agent's left | **hallucination** |
| 8 | rf39 `N_head_on_02dfbadb_9950986f_r3` dp6 | "They're drifting into my path at close range" | changes: slowed only | **hallucination** |
| 9 | rf39 `N_head_on_02dfbadb_81bae7c3_r2` dp7 | "Acknowledge her greeting" | she nodded (non-verbal) | **not** (a nod is a greeting) |
| 10 | rf40 `N_head_on_de176842_231c8154_r3` dp4 | "He said hello" | a nod only; nothing heard | **hallucination** (claims speech) |
| 11 | rf39 `N_head_on_de176842_51dfba80_r3` dp5 | "He already waved me on" | eye contact now; its own earlier intent (in history) says "since he waved me on" | **not** (it repeats its own input) |
| 12 | rf40 `N_head_on_de176842_02604456_r3` dp9 | "He's already waved-through" | he nodded; nothing in history says he waved | **hallucination** |
| 13 | rf39 `I_head_on_de176842_55c9ae40_r3` dp1 | "I'm an old man with a cane" | (the agent describing itself) | **not** (the coder mistook a self-description for the other) |
| 14 | rf39 `N_head_on_de176842_81bae7c3_r1` dp9 | "so an older lady with a cane passes safely" | the other is 25, with no cane | **hallucination** |
| 15 | rf39 `T_head_on_de176842_51dfba80_r4` dp1 | "the passage is too narrow to avoid them anyway" | 1.75 m passage; bodies 0.7 + 0.5 m | **hallucination** (misstated the setting) |
| 16 | rf39 `N_head_on_02dfbadb_68f09b97_r4` dp5 | "too narrow for both of us at full stride" | the same widths | **not** (a judgement of ease) |
| 17 | rf40 `T_head_on_de176842_51dfba80_r2` dp11 | "keeping to my left against the wall" | 1.02 m to the left wall, 0.73 m to the right | **hallucination** (misstated its position) |
| 18 | rf39 `I_head_on_de176842_68f09b97_r1` dp1 | intent "holding my line"; plan sidesteps right and slows | | **self-contradiction** (category 3) |
| 19 | rf39 `N_head_on_02dfbadb_b1d97a31_r1` dp6 | intent "Keep well to my right"; plan does not move | 0.63 m from the right wall | **not** (staying where it is keeps to the right) |
| 20 | rf40 `T_head_on_02dfbadb_dbd98c92_r2` dp11 | "said he is passing on my left (my right side physically)" | heard "passing on your left!" | **hallucination**, missed by the coder |
