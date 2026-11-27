# RF-49: round 1 (head-on) with the action menu, in the agent's own frame and in an absolute frame

Issue #138, track #55. Run 2026-11-27 on `deepseek-flash`. The generated tables are in `menu.md`; this
report reads them.

## Summary

- **With the menu, LLM agents resolve the head-on meeting less often than with RF-40's free steps,
  in both frames.** None of the three configs passes RF-10's gate (0.50, the first repeats):
  - own frame 63 of 128 (0.49);
  - absolute frame, blue wall at +y: 40 of 128 (0.31);
  - absolute frame, yellow wall at +y: 38 of 128 (0.30);
  - RF-40 passed on the same design at 123 of 192 (0.64).
- **Over all four repeats** (RF-40's 256 design sessions per condition, paired session by session):

  | | Silent | Talk |
  | --- | --- | --- |
  | RF-40, free steps | 163 (0.64) | 150 (0.59) |
  | Menu, own frame | 136 (0.53), p = 0.018 | 88 (0.34), p < 0.001 |
  | Menu, absolute frame | 79 (0.31), p < 0.001 | 66 (0.26), p < 0.001 |

  p is McNemar's exact test against RF-40, on the same sessions.
- **Why the own frame does worse: the menu makes "carry on" a first choice, and "a little" is too
  little alone.**
  - A third of first plans are "carry on" or slowing (351 of 1,024). In RF-40, 93% of first plans
    had a sidestep.
  - RF-40's sidesteps were not bigger (median 0.4 m). What changed is that both people usually
    moved.
  - "Step a little" is 0.47 m: half of the human passing distance H1, chosen so that two people who
    each step a little pass at H1 (AS3). Two bodies 0.5 m wide need 0.5 m between centres, so
    **one person stepping a little while the other carries on still collides** unless someone
    re-plans. That pair is the commonest start (99 silent sessions; 33 resolved).
  - When both stepped a little to the same own side (each its own right, say), all 66 silent sessions
    resolved.
- **Why the absolute frame does worse still: both people lean to the same wall.**
  - First moves went towards the wall at -y 575 times and towards +y 156 times. The swap shows
    **this follows the wall's place, not its colour** (Fisher's exact test: half by place p = 0.28;
    half by colour p < 0.001).
  - The -y wall is one person's right and the other's left, so a shared lean is a dance. When both
    stepped a little: same wall in 62 silent sessions (2 resolved), different walls in 36 (34
    resolved).
  - The own frame's lean (to the right) is the same kind of habit, but there it coordinates.
  - **This answers RF-52's open question:** the grid's lean to "the yellow wall" was the same wall
    (b, at -y) and is not about the colour. Place, being named second, and not being the wall
    positions are measured from all go together, so which of them it is stays open.
- **Talk makes the menu worse, not better** (own frame 0.53 to 0.34). Talking agents choose "carry on"
  more (181 against 127 first choices), and 27 talk sessions began with two little steps to opposite
  own sides (none resolved).
- **Hallucinated decisions** (RF-45's method, 75 points per frame, each read against its prompt):
  own frame **1 of 75 (0.01, 0.00 to 0.07)**, absolute frame **8 of 75 (0.11, 0.06 to 0.20)**
  (Fisher p = 0.034).
  - The absolute frame's errors are about where things are against the walls: the other placed by
    the wrong wall (6), its own place misstated (2).
  - On the grid it was the other way round (own 5 of 75, absolute 1 of 75). The continuous absolute
    frame gives distances to compare ("1.45 m from the blue wall" against its own 1.24 m), not lanes.
- **The menu works as an interface.** 3 of 2,955 own-frame decision points were unreadable ("step
  well to **my** left"), none of 3,143 in the absolute frame. RF-40 had 94 of 3,306.
- **The pass distance in resolved sessions** stays near the human one (H2, 0.93 m): own frame median
  0.93 m, absolute 0.95 m, RF-40 0.91 m.
- **Cost:** USD 1.024 of the USD 2.00 cap, over the three experiments together. The balance went from
  USD 2.61 to **USD 1.59**. All 8,348 calls returned RF-40's model fingerprint.
- **Two prompt issues found, both older than RF-49** (section 6): the history's cumulative lines
  are read as separate moves, and the history's sideways distance is occasionally impossible.

## 1. What ran

| | Own frame | Absolute, blue at +y | Absolute, yellow at +y |
| --- | --- | --- | --- |
| Config | `rf49_round1_head_on_menu.yaml` | `rf49_round1_head_on_menu_abs.yaml` | `rf49_round1_head_on_menu_abs_swap.yaml` |
| Template | `resolve_menu_v1` | `resolve_menu_abs_v1` | `resolve_menu_abs_swap_v1` |
| Sessions | 544 (RF-40's silent and talk, 4 repeats) | 288 (repeats 1, 2) | 288 (repeats 1, 2 = RF-40's 3, 4) |
| Decision points | 2,955 | 1,570 | 1,573 |
| Calls (with retries and debriefs) | 4,050 | 2,148 | 2,150 |
| Cost (USD, ledger) | 0.4870 | 0.2687 | 0.2682 |

- The configs are in `llm_negotiation/configs/resolution/` (commit `4a657af23`). Each keeps RF-40's
  design (cases, people, layouts, repeats, counterbalancing) and changes the conditions (silent and
  talk, AS2), the core and debrief templates (`resolve_debrief_v3`), the experiment name and the cap.
- The absolute frame names the two walls by colour. The user chose on 2026-11-27 to
  counterbalance which colour is at +y at the same size ("Counterbalance, same size"). So the
  absolute frame has one session per RF-40 session, half with each colour at +y.
  - In both templates the +y wall is named first, and the other person's position is given as a
    distance from it. The swap changes only the colour.
  - The counterfactual pairs ran in both halves (32 sessions more than "same size"). They are left
    out of every comparison here.
- Silent and talk only (AS2). The pilot (28 sessions, USD 0.0265) ran first, at 10:00 UTC. The rest
  ran from 10:11 to 16:02 UTC, all off-peak.

## 2. The gate, and the comparison with RF-40

**The gate** (`analysis.gate`, RF-10's 0.50 on each config's first repeats, as fixed before the run):

| Config | Resolved (plan_only) | Silent | Talk | Aligned | 20 cm apart |
| --- | --- | --- | --- | --- | --- |
| Own frame | 63 / 128 (0.49) **fails** | 38 / 64 | 25 / 64 | 30 / 64 | 33 / 64 |
| Absolute, blue at +y | 40 / 128 (0.31) **fails** | 22 / 64 | 18 / 64 | 20 / 64 | 20 / 64 |
| Absolute, yellow at +y | 38 / 128 (0.30) **fails** | 17 / 64 | 21 / 64 | 12 / 64 | 26 / 64 |
| RF-40 (3 conditions) | 123 / 192 (0.64) passes | 42 / 64 | 41 / 64 (talk) | 68 / 96 | 55 / 96 |

The gate's reason text in the configs is RF-40's ("192 sessions ... 3 conditions"). The threshold
and the rule are the same; only the wording is stale.

**All four repeats, paired with RF-40** (`menu.md`, section 1). Resolved, both / only RF-40 / only
the menu / neither:

| | Silent | Talk |
| --- | --- | --- |
| RF-40 to own frame | 89 / 74 / 47 / 46 (p = 0.018) | 48 / 102 / 40 / 66 (p < 0.001) |
| RF-40 to absolute | 45 / 118 / 34 / 59 (p < 0.001) | 40 / 110 / 26 / 80 (p < 0.001) |
| Own to absolute | 52 / 84 / 27 / 93 (p < 0.001) | 29 / 59 / 37 / 131 (p = 0.032) |

- **Collisions rise to match:** silent 74 (RF-40), 106 (own), 155 (absolute) of 256. No session
  deadlocked.
- **ORCA under the plans** (`plan_orca`) helps the menu a little (own talk 0.34 to 0.46) but does not
  close the gap.
- **The layouts swap round in the own frame.** RF-40 resolved more when the two start aligned (0.71)
  than 20 cm apart (0.56). The menu resolves less aligned (0.44) than apart (0.62). A lone little
  step from 20 cm apart clears the other when it goes away from them (section 3).

**Against the grid (RF-52).** On the same 256 silent design sessions, the grid resolved 223 (own
frame) and 216 (absolute), against the continuous menu's 136 and 79. Paired: 103 against 16, and
150 against 13 (McNemar p < 0.001 both). **The grid's gains over RF-40 come from the grid** (cells,
fixed lanes, no ORCA), **not from the menu**: the menu alone, in the continuous corridor, does worse
than free steps. This is what RF-52's option 3 (task 3) was for.

## 3. The own frame: what the menu changed

**The first plans as a pair** (`menu.md`, section 9; silent, 256 sessions):

| First options | Sessions | Resolved | Collision |
| --- | --- | --- | --- |
| one a little, the other carries on | 99 | 33 | 58 |
| both a little, same own side | 66 | **66** | 0 |
| both a little, opposite own sides (the dance) | 32 | 7 | 22 |
| one a little, the other slows or stops | 17 | 12 | 5 |
| one well, the other carries on | 13 | 6 | 4 |
| one a little and one well, same own side | 8 | 8 | 0 |
| one a little and one well, opposite own sides | 8 | 1 | 7 |
| both carry on, or carry on and slow | 9 | 0 | 9 |

- **Carrying on is the new behaviour.** RF-40's first plans moved aside 93% of the time (934 of 1,024
  agents, silent and talk). The menu's did 65% (670 of 1,024): "carry on" was the second commonest
  first option, after "step a little to your right".
  - RF-40's free steps never offered "keep walking" as a named option. The menu lists it first, and
    agents who "hold my ground" or are "in a hurry" take it.
  - *Assumption, not tested:* the listing order may also matter.
- **A lone little step is not enough by design.** From an aligned start, one little step (0.47 m)
  leaves the centres 3 cm closer than two half-bodies:

  | Lone little step, other carries on | Own frame | Absolute frame |
  | --- | --- | --- |
  | aligned | 23 of 105 resolved | 12 of 98 |
  | 20 cm apart, stepping away from the other (own left) | 16 of 28 | 28 of 50 |
  | 20 cm apart, stepping towards the other's side (own right) | 25 of 82 | 1 of 45 |

  The ones that resolve do so by a later decision: re-planning works sometimes.
- **The keep-right habit persists and, in the own frame, coordinates.** First moves went right 441
  times and left 229. In the 20 cm layout that means towards the farther wall (143 to 34, silent),
  across the other's side.
- **Talk hurts.** Talking agents choose "carry on" more, often after the other "waved me on" or said
  "go ahead". Then both keep going, or one steps a little: own talk resolved 88 of 256.

## 4. The absolute frame: the walls

**Which wall the first move aside went to** (`menu.md`, section 3; silent and talk, both people):

| Half | Wall at +y (named first) | Wall at -y (named second) |
| --- | --- | --- |
| Blue at +y | 83 (blue) | 277 (yellow) |
| Yellow at +y | 73 (yellow) | 298 (blue) |

- **The colour does not matter;** the place does. The lean holds for each person, each layout and
  each condition (`menu.md`).
- **What "the place" is cannot be split here.** The -y wall is named second in every line of the
  prompt, and it is never the wall positions are measured from ("Person 1 ... 0.77 m from the blue
  wall"). Its being at -y means nothing to the agent, which is never told its own left or right.
  - *My reading, not tested:* agents step "away" from the reference wall the other is placed by.
  - A template that measures from the second wall would tell.
- **The lean is a shared convention that fails.** "Towards the yellow wall" is one person's right
  and the other's left. When both step a little:

  | Both a little | Silent | Talk |
  | --- | --- | --- |
  | same wall | 62 (2 resolved) | 62 (3 resolved) |
  | different walls | 36 (34 resolved) | 24 (23 resolved) |

  Every pair that took different walls nearly always passed. The frame removes the left/right
  confusion, but agents do not use the shared names to split the walls.
- **The nearer wall:** in the 20 cm layout, first moves went towards the nearer wall 216 times and the
  farther 158 times, unlike the own frame's 93 to 245. This is the -y lean again: person 2 starts
  nearer -y.
- **Talk names walls but rarely settles them.** 94 of 730 messages named a wall. Of the 80 times a
  listener heard one named wall, 57 times it did not move aside, 12 times it went to the other wall
  (the split that works) and 11 to the named one.
  - Example: "I'll keep to the yellow wall, you carry on past"; the listener reasoned "I'm already
    shifted toward the yellow wall as agreed" and kept to it.

## 5. Hallucinated decisions (RF-45's method)

RF-45's definition and categories (`analysis/codebooks/hallucination_v2.json`). The headline is
categories 1, 2, 5 and 7: misperceived the other, misremembered itself, not an available action,
misstated the setting.

- **The sample:** 75 decision points per frame, seeded (seed 138). The absolute frame's 75 are drawn
  from both halves together.
- **The judge:** the assistant read each point in full against what its prompt gave
  (`hand_check_sheet.md`). The doubtful absolute-frame points were also checked against the full
  prompt in the session's `.md`. The judgements and notes are in `hand_judgements.json`, in RF-52's
  format.

| | Own frame | Absolute frame | Grid own (RF-52) | Grid absolute (RF-52) | RF-40 (RF-45) |
| --- | --- | --- | --- | --- | --- |
| **Headline (1, 2, 5, 7)** | **1 / 75 (0.01, 0.00 to 0.07)** | **8 / 75 (0.11, 0.06 to 0.20)** | 5 / 75 | 1 / 75 | 14 / 150 (0.09) |
| Self-contradiction (3, 4) | 0 / 75 | 2 / 75 | 0 / 75 | 1 / 75 | 12 / 150 |
| A left/right mix-up | 1 / 75 | 1 / 75 | 2 / 75 | 1 / 75 | |
| A move against its own geometry | 0 / 75 | 1 / 75 | 9 / 75 | 5 / 75 | not counted |

- **The absolute frame's eight:**
  - the other placed by the wrong wall (6), for example "she's on the yellow side" when the prompt
    gives her 1.45 m from the yellow wall and 0.30 m from the blue;
  - its own place misstated (2), for example "I'm nearer the blue wall side" at 0.77 m from yellow
    and 0.98 m from blue.
- **Its two self-contradictions:** a wall chosen and a different one named in the reason; and "shift
  toward my right" for the yellow wall, which is that person's left (the prompt gives no left or
  right).
- **The own frame's one:** "enough room for him to pass on my right" when the prompt puts him 6° to
  its left.
- **The frames compare the other way round from the grid** (Fisher p = 0.034 here). On the grid the
  absolute frame gives lanes; here it gives two distances per person, which agents have to compare,
  and they compare them wrongly about one time in ten.
- **RF-45's keyword coder,** with only the rules its hand check found reliable
  (`rf49_analysis/coder/`): own frame 23 of 2,955, absolute 8 of 3,143. Its rules read left and
  right, so it cannot see the absolute frame's wall errors. The share to quote is the hand check's.

## 6. Two issues in the prompt, older than RF-49

Neither is a hallucination, and neither explains the difference between the arms. Both are reported
here, not fixed: a fix would change the prompts of configs that must keep behaving as before.

1. **The history's lines are cumulative, and agents add them up.**
   - "Since then you have moved 0.5 m over to your right" counts from that decision to now, as
     `resolve_v2`'s template comment says ("how far the agent has moved since").
   - So after one step right, two later lines can both say "0.5 m to your right". Two of the 150
     sampled points read them as two moves ("I've already shifted right twice"), and one of those
     agents was back where it started.
   - A later template version could state each decision's own move instead.
2. **The history's sideways distance is sometimes impossible.**
   - One agent pressed against the blue wall was told "Since then you have moved 1.3 m over towards
     the yellow wall".
   - `perceive._done` measures the move against the way the person faced when deciding, which can be
     turned from the walking line (mid-step, or after a turn).
   - Values over 1.25 m (the most the corridor allows): 20 of 3,591 RF-40 points with a history, 9 of
     3,858 RF-49 points. Smaller wrong values are not counted, so this is a lower bound.
   - Measuring against the corridor's axis would fix it, behind a flag.

## 7. Other measures

- **The pass distance in resolved sessions** (RF-37's H2, 0.93 m ± 0.17):

  | | Sessions | Median | Q1 to Q3 | Within H2 | Below | Above |
  | --- | --- | --- | --- | --- | --- | --- |
  | RF-40 silent | 163 | 0.91 m | 0.80 to 1.03 | 107 | 31 | 25 |
  | Own silent | 136 | 0.93 m | 0.75 to 1.03 | 91 | 39 | 6 |
  | Absolute silent | 79 | 0.95 m | 0.88 to 1.05 | 54 | 19 | 6 |

  The menu's fixed amounts cut the wide passes (6 above H2 against 25) but add close ones.
- **Wall flags:** "step well" was cut short by the wall (`capped_by_wall`) 593 times, and 294
  decisions asked to step towards a wall with no room left (`no_room`), over all four arms.
- **Unreadable replies:** own frame 3 (the option written with "my" for "your"), absolute 0. RF-40:
  94 of 3,306 decision points.
- **Factor effects** were not modelled for RF-49. With the gate failed, Step 4's mapping from these
  runs would describe a convention that does not resolve the meeting. *This is my choice; the
  sessions are kept, so it can be done if wanted.*

## 8. What this means for the next step

- **The menu as built does not help in the continuous corridor.** For a menu to replace free steps,
  two things would need changing. Both are changes to AS3's amounts and wording, and the user's to
  decide:
  - "a little" at or above one body width (0.5 m), so that one person's small step clears;
  - a different place for "carry on", or a menu with no "carry on".
- **The absolute frame needs the agents to split the walls,** and nothing in the prompt does that.
  The positions (distances from the reference wall) also produce misreadings.
  - Possible next tests: an absolute frame that measures from the second wall (tells place from
    reference), or one that gives both people's positions from both walls.
- **For task 3 of RF-52:** the user chose "the grid as a test bench, RF-49 tests". RF-49's answer is
  that **the grid's gains come from the grid, not from the menu.** So the grid's results speak to the
  grid's world, not to free steps in the continuous corridor.

## 9. Limits

- **One judge for the hand check,** the assistant, as in RF-45 and RF-52. The 20 judgements with a
  note are the ones to check first.
- **The colour swap does not separate place, listing order and reference wall** (section 4).
- **The menu's amounts and order are one design** (AS3, RF-47). A different "a little", or no "carry
  on", may change the result. These were not varied.
- **`deepseek-flash` only,** with RF-40's fingerprint throughout, so the comparison with RF-40 is on
  the same model.
- **No factor model** (section 7).

## 10. Files

| File | What |
| --- | --- |
| `runs/rf49_round1_head_on_menu/`, `..._abs/`, `..._abs_swap/` | The runs: `config.json`, `sessions/*.json` and `.md` (every prompt, reply and plan), `replay/` (`plan_only`, `plan_orca`; interaction logs not tracked, rebuilt by `python -m negsim.resolution.replay`), `outcomes.csv`, `analysis/gate.md` |
| `runs/rf49_analysis/menu.md`, `menu.json` | The generated tables (`python -m analysis.menu`) |
| `hand_check_sheet.md`, `hand_judgements.json` | The hand check |
| `coder/` | RF-45's keyword coder over every decision point |

To reproduce, from the repo root:
```
python -m analysis.gate llm_negotiation/runs/rf49_round1_head_on_menu        # and _abs, _abs_swap
python -m analysis.menu --rf40 llm_negotiation/runs/rf40_round1_head_on_turn_taking \
  --own llm_negotiation/runs/rf49_round1_head_on_menu \
  --abs llm_negotiation/runs/rf49_round1_head_on_menu_abs \
  --swap llm_negotiation/runs/rf49_round1_head_on_menu_abs_swap \
  --out llm_negotiation/runs/rf49_analysis
python -m analysis.hallucination llm_negotiation/runs/rf49_round1_head_on_menu \
  llm_negotiation/runs/rf49_round1_head_on_menu_abs llm_negotiation/runs/rf49_round1_head_on_menu_abs_swap \
  --out llm_negotiation/runs/rf49_analysis/coder
```
