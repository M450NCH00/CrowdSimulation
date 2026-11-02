# RF-40: round 1 (head-on), talk as a turn-taking exchange

Issue #129, track #55. Paid run of 2026-11-02 (Monday, off-peak only), approved by the user for this
issue only with a cap of USD 1.80 (`CLAUDE.md`, pending item 1). Spent USD 1.2261 (7,051 calls).
Every number below comes from a file named with it; the process is in `WORK_LOG-129.md`. Tables:
`analysis/turn_taking.md` (this issue's module, `python -m analysis.turn_taking`),
`analysis/sidestep_reprompt.md`, `analysis/gate.md`, `analysis/lateral.md`, `analysis/compare_*.md`
and the factor report `analysis/report.md` (`python -m analysis`).

## In short

- **Being asked again is what helps, not signals or talk.** Silent (no signal, no talk, asked again
  under D5) resolved **163 of 256 (0.64)**, against RF-39's independent (one decision, the same people)
  **91 of 256 (0.36)**, Fisher's exact p < 0.0001. Non-verbal (0.56) and talk (0.59) did no better than
  silent (p = 0.10 and 0.28), and no better than in RF-39 (0.59 each; p = 0.66 and 1.0).
- **Round 1 now passes the gate.** First runs, 123 of 192 (0.64, 95% CI 0.57 to 0.71) against the 0.50
  carried over from RF-10; RF-39 failed narrowly at 0.48. Silent 0.66, non-verbal 0.62, talk 0.64.
  First runs are all "person 1 asked first" (repeat 1).
- **Every message is now heard, but nobody coordinates a side at the start.** At the first pause, 182
  of 499 talk replies had a message, nearly all greetings ("Hi! Fancy seeing you here."); **4 named a
  side**. Sides are named from the second decision on, mostly once the two are already heading for
  the same wall (31, 38, 39, 24, 14 at decisions 2 to 6).
- **When a side is heard, the listener's next move makes room less often than a coin would.** Of 100
  heard side messages where both moved aside, the listener's side fitted the speaker's in **35**
  (p = 0.004 against a coin). Both frames go wrong: "I'll keep left" (the speaker's own side) 14 of
  42; "on your right" (the listener's side) 12 of 44.
- **Speakers mean their own-frame words; "on your right" is often said the wrong way round.** "I'll
  keep to my left" matched the speaker's own move 44 times in 46. "Coming through on your right"
  matched in 11 of 27: in 16 the speaker moved to the side that puts it on the listener's *left*.
- **Listeners translate, and still go wrong.** 44 listener replies restate the side in the other's
  frame ("that's my left", "(her right)"); they fitted in 18. One reads "plenty of room on your right"
  as "since he's facing me that's my left": the note on a speaker's facing applied to words already
  in the listener's frame.
- **Who is asked first does not matter** (person 1 first against person 2 first: silent 0.62 / 0.66,
  non-verbal 0.53 / 0.59, talk 0.64 / 0.53; Fisher p = 0.60, 0.38, 0.10). No factor predicts
  resolution; `asked_first` is significant for no outcome in the factor report.

## 1. What was run

RF-39's design (32 cells x 2 geometries x 4 repeats, and 16 counterfactual pairs, per condition; 816
sessions), the same people in each cell, `keep_line_replan`, 6 decision points, `resolve_debrief_v2`,
`deepseek-flash` (fingerprint `bc19ba97...`, as RF-39), with the user's decisions of 2026-11-01 and
2026-11-02:

- **The turn-taking exchange** (`protocol.exchange: turn_taking`): the simulation pauses while those
  due are asked one at a time; a signal is seen and a message heard at once, in full; whoever perceives
  it is asked next in the same pause. Who is asked first is counterbalanced: person 1 in repeats 1 and
  3, person 2 in 2 and 4. An answer reaches the first speaker at its next decision point (D5's 1 s gap).
- **Always heard** (`protocol.always_heard`): in a pause everyone in the encounter hears a message
  whatever the distance. **A departure from D2's hearing range** (8.9 m quiet, 3.2 m busy), which
  would have left about half the messages unheard (RF-40's first mock: 56 of 113).
- **Silent** replaces independent: no signal and no message, asked again under D5.
- **`resolve_v9`**: `resolve_v8` for the paused exchange, with a note beside a heard message on which
  way the speaker faces ("Person 1 is facing you: their left is your right, and their right is your
  left."); the message is never rewritten.

Unreadable after the retry: 121 of 5,256 decision points (`report.md`, failure modes; the commonest,
`start: "other_passes"`, 61). Debriefs: 1,631 of 1,632 (one agent's only reply was unreadable).

## 2. The Step 1 answer

| Condition | All repeats | First runs | RF-39, all repeats |
| --- | --- | --- | --- |
| silent | 163 / 256 (0.64) | 42 / 64 (0.66) | independent 91 / 256 (0.36) |
| non_verbal | 144 / 256 (0.56) | 40 / 64 (0.62) | 150 / 256 (0.59) |
| talk | 150 / 256 (0.59) | 41 / 64 (0.64) | 151 / 256 (0.59) |

(`sidestep_reprompt.md` section 1; RF-39's from its own.) The gate (`gate.md`): 123 of 192 first
runs, **passes**; by geometry, aligned 0.71 and 20 cm apart 0.57. Plain ORCA resolves none (0 of 192):
it passes within the near-miss distance. The paired comparison with RF-39 on the same sessions
(`compare_*.md`) finds no change in non-verbal or talk (McNemar's exact test, talk p = 0.60).

Silent against RF-39's independent changes one thing for the agent: it is asked again. The pause does
not change what a silent agent knows (nothing is signalled or said, and no simulated time passes).
So the near doubling is the second chance's, as RF-39 found for non-verbal and talk; RF-39 could not
separate it from the signals and words, and this run does: signals and words add nothing measurable.

## 3. The pavement dance

| Condition | Dance at the start (towards the same wall) | Of them resolved | RF-39 |
| --- | --- | --- | --- |
| silent | 92 of 256 | 38 (0.41) | independent: 90, 0 resolved |
| non_verbal | 89 of 256 | 27 (0.30) | 120, 47 resolved (0.39) |
| talk | 107 of 256 | 36 (0.34) | 124, 41 resolved (0.33) |

(`sidestep_reprompt.md` section 2.) **Fewer non-verbal dances at the start than in RF-39** (89
against 120, Fisher p = 0.007): in the pause the second agent sees the first one's signal before it
decides. Talk's fall (107 against 124) is within chance (p = 0.16). But fewer of non-verbal's dances
ended well, so the overall rate did not move. How a dance ends is as in RF-39: one agent changes side
and the other holds (silent 37 of 38 rescued, talk 33 of 36); in the dances that did not end, often
nobody changed side (non-verbal 49 of 62, talk 51 of 71), and in silent 28 of 54 had one agent change
side, too late.

## 4. What talk said, and when

| Decision | Readable replies | With a message | Naming a side |
| --- | --- | --- | --- |
| 1 | 499 | 182 | 4 |
| 2 | 433 | 214 | 31 |
| 3 | 323 | 180 | 38 |
| 4 | 227 | 135 | 39 |
| 5 | 153 | 114 | 24 |
| 6 | 49 | 42 | 14 |

(`turn_taking.md` section 1.) The first messages are greetings to an acquaintance (the familiarity
factor: `knows_other` raises signalling by an odds ratio of about 160, `report.md`): "Hi! Fancy seeing
you here.", "Hey! Good to see you!". At the start, when the pause would let one agent say a side and
the other follow it, almost nobody does. A side comes up once the plans are already failing.

## 5. A side heard, and what the listener did

| Message's frame | Listener's side fits | Towards the same wall | Fits, of both aside | p (coin) |
| --- | --- | --- | --- | --- |
| own ("I'll keep left") | 14 | 28 | 14 / 42 | 0.04 |
| yours ("on your right") | 12 | 32 | 12 / 44 | 0.004 |
| both / other | 9 | 5 | 9 / 14 | |
| **all** | **35** | **65** | **35 / 100** | **0.004** |
| all, answered in the same pause | 25 | 38 | 25 / 63 | 0.13 |
| all, at a later decision | 10 | 27 | 10 / 37 | 0.008 |

(`turn_taking.md` section 2; another 24 had one of the two not moving aside.) In RF-39, words almost
never arrived in time (12 of 108 side messages heard, 4 in time, all 4 followed the wrong way). Now
124 are heard before the listener's next decision; where both moved aside (100), the listener's move
makes room in about a third: worse than a coin.

Where it goes wrong (`turn_taking.md` section 3, and the session records):

- **Speakers.** "I'll keep to my left" names the speaker's own side and matches its move (44 of 46).
  "Coming through on your right" should put the speaker at its own left; 16 of 27 moved to their
  right. The speaker says the listener's side and gets it wrong.
- **Listeners.** 44 replies restate the side in the other's frame; 18 of them fitted. Examples
  (verbatim, dashes shortened):
  - `T_head_on_02dfbadb_9950986f_r1`, decision 2: the speaker, moving left, says "Hey! Sure, go ahead
    … plenty of room on your right." The listener: "He's drifted to my right and told me to go ahead
    on my right, but since he's facing me that's my left", and moves right. The note's flip applied
    to words already in the listener's own frame.
  - `T_head_on_02dfbadb_6ab9c72e_r2`: "Oh, take care! I'm keeping left, plenty of room." (moving
    left). The listener: "She's keeping left and promising room, so I keep my side and edge slightly
    further right". Towards the same wall.
  - A fit, `T_head_on_02dfbadb_51dfba80_r2`: "Thanks, dear! I'll keep left … mind the suitcase now."
    The listener: "She said she'll keep left, so I keep to my left (her right)".

**What this run cannot say.** Every heard message carried the note, so the run cannot tell whether the
note makes listeners worse or better: there is no turn-taking run without it. The cases are also not
a random sample: side messages come mostly in dances already under way, where any move is late.

## 6. Who is asked first

| Condition | Person 1 first | Person 2 first | Fisher's exact p |
| --- | --- | --- | --- |
| silent | 79 / 128 (0.62) | 84 / 128 (0.66) | 0.60 |
| non_verbal | 68 / 128 (0.53) | 76 / 128 (0.59) | 0.38 |
| talk | 82 / 128 (0.64) | 68 / 128 (0.53) | 0.10 |

(`turn_taking.md` section 4.) No effect; in the factor report `asked_first` is significant for no
outcome (passing first: OR 1.20, Holm p = 1.0).

## 7. Factors and debriefs

As in RF-10 to RF-39, no factor predicts resolution (`report.md` section 1). Who passes first follows
the agent's own assertiveness (OR 8.4); slowing down follows the other's mobility aid (OR 4.7), age
(4.3) and load (2.9), knowing them (2.7), and finding them attractive (1.8); silent agents slow less
(OR 0.51). The side: residents of Singapore go left more often than visitors (`plan_right`, visitors
OR 2.25), and so do older agents. 163 of 192 cells are coin flips for the overall behaviour
(stability below 0.75). Debriefs: common sense 1,285, habit 266, a local custom 23, none 57.

## 8. Coding choices (the assistant's)

- A message names a side if it has `left` or `right`; its frame is `own` ("I'll keep/stay/go … left",
  "my left") or `yours` ("your left"), a keyword match (`turn_taking.FRAMES`).
- "Fits" compares the listener's next readable decision that heard the message with the speaker's side
  at the decision it spoke, each in its own frame; a speaker may change again afterwards.
- "Restates the side": the reason or intent has "that's my left", "(her right)" and the like.

## 9. For the user

1. **Step 1 for head-on:** the gate passes; the second chance is what resolves, signals and words add
   nothing measurable. Whether round 1 goes on to extraction again (RF-11 was run on RF-10's data) is
   your call.
2. **Talk does not coordinate.** Two possible follow-ups, both a new template and a paid run, neither
   built: a turn-taking run without the facing note (does the note hurt?), or one where the frame is
   stated in the instructions instead. Or accept the result: LLM agents that talk do not agree a side.
3. **The departure from D2** (always heard) must be stated wherever RF-40's talk results are reported.
