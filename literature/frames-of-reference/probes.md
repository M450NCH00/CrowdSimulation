# RF-43, task 4: static probes of the left-and-right conversion (optional, **not run**)

*Issue #144 (RF-53), 2026-11-28:* these probes are frozen, with small wording changes listed in its header, as `llm_negotiation/configs/probe/frames_probes_v1.yaml`, which RF-53's stage 1 sends (`python -m negsim.probe`). This file stays as RF-43 wrote it.

Issue #132. **Nothing here has been sent to a model.** A run would be a paid call. By `CLAUDE.md` it needs the user's approval and a cap recorded for its own issue first ("Pending sign-offs", item 1). It would also need the mock client first, like every feature.

**Why.** RF-40's errors (README, E1 to E3) happened inside a simulation, mixed with timing, distance and late moves. These prompts test only the conversion, with one answer each. They separate:
- the model's own frame;
- the listener's frame;
- the facing note;
- an absolute frame, with and without a heading;
- a grid.

They are written so that the probe can be run with thinking off and on (README, section 5.3).

## The shared opening (every probe)

> You are walking along a straight corridor 1.75 m wide. Another person is walking towards you, facing you, 6 m ahead, in the middle of the corridor, as you are. Answer with one word or lane number on the first line, then one sentence saying why.

Probes 12 and 17 to 20 change the opening as stated. "Expected" is the correct answer. The reasoning is in brackets, with these facts:
- facing each other, the other's left is on your right side;
- facing east, north is on your left.

## A. You hear a side in the speaker's own frame (RF-40's E2)

1. They say: "I'll keep to my left." Which way do you move, left or right? **Expected: left.** (They move to their left, which is your right side.)
2. They say: "I'll keep to my right." Which way do you move? **Expected: right.**
3. They say: "I'll pass you on my right." Which way do you move? **Expected: left.** (You are to be on their right, which is your left side.)

## B. You hear a side in your own frame (RF-40's E2, the listener's frame)

4. They say: "Go ahead, plenty of room on your right." Which way do you move? **Expected: right.**
5. They say: "Coming through on your right." Which way do you move? **Expected: left.** (They will be on your right.)
6. They say: "Coming through on your left." Which way do you move? **Expected: right.**

## C. The same messages with `resolve_v9`'s facing note (RF-40's E3)

Each adds, after the message: *(Person 2 is facing you: their left is your right, and their right is your left.)*

7. Probe 1 with the note. **Expected: left.** The note applies: the words are in their frame.
8. Probe 4 with the note. **Expected: right.** The note does not apply: "your right" is already your frame.
9. Probe 5 with the note. **Expected: left.** The note does not apply.

## D. You are the speaker (RF-40's E1)

10. You have decided to move to your left. Tell the other person which side of *them* you will pass on, using *their* left or right. **Expected: "your right".**
11. You have decided to move to your right. The same question. **Expected: "your left".**
12. *Changed opening: the other person walks ahead of you, the same way, 3 m ahead, and you are overtaking.* You will move to your left to pass. Which side of them will you pass on, in their left or right? **Expected: "your left"** (facing the same way, the frames coincide).

## E. An absolute frame with no heading (README, section 6, item 3: does the model invent a heading?)

The opening adds: *The corridor has two long walls, the north wall and the south wall. You are 0.9 m from the north wall.* Probes 15 and 16 replace the names with "the window side" and "the shop side".

13. Is the north wall on your left or on your right? **Expected: "cannot tell"** (no heading is given). Any side is an invented heading.
14. They say: "I'll keep to the south wall." Which wall do you move towards? **Expected: north.**
15. Is the window side on your left or on your right? **Expected: "cannot tell".**
16. They say: "I'll keep to the window side." Which side do you move towards? **Expected: the shop side.**

Comparing 13 with 15 shows whether compass names, more than landmark names, make the model assume a heading.

## F. An absolute frame with the heading told (the conversion AS5 avoids)

17. *Adds: you are walking east.* Is the north wall on your left or on your right? **Expected: left.**
18. *Adds: you are walking west.* Is the north wall on your left or on your right? **Expected: right.**

## G. A grid (variants D and E of `action-space.md`)

The opening is replaced by: *The corridor is 5 lanes wide, numbered 1 to 5 from the north wall. You are in lane 3, walking east. Another person is in lane 3, 6 cells ahead, walking west towards you.*

19. They say: "I'm moving to lane 2." Which lane do you move to, if you move? **Expected: 4.** (Lane 2 is theirs; lane 4 keeps you apart. Staying in lane 3 also avoids them, so score 3 or 4 as correct, 2 as wrong.)
20. They say: "I'm stepping one lane to my left." Which lane will they be in? **Expected: 4.** (Walking west, their left is south. Lanes count up towards the south wall.)

## How a run would be scored, and what it might cost

- **Repeats:** each probe 10 times, at RF-40's settings (`deepseek-flash`, temperature 1.0, a reply cap of 300), thinking off; then again with thinking on. That makes 20 × 10 × 2 = 400 calls.
- **Measures:**
  - the share correct per group A to G;
  - for C against A and B, whether the note helps (7) or hurts (8, 9);
  - for 13 and 15, the share that invents a side.
- **Cost, a rough estimate only:**
  - RF-40 spent USD 1.2261 on 7,051 calls, about USD 0.00017 a call, with much longer prompts than these;
  - so 200 calls with thinking off would cost under about USD 0.04 `[inference]`;
  - thinking on bills its reasoning as output and could cost several times more `[unverified]`, so a pilot of one repeat (40 calls) should come first.
- **Before any run:**
  - the mock client;
  - the model fingerprint check (`action-space.md`, section 3);
  - the balance;
  - the user's approval and cap, recorded in `CLAUDE.md`.
