# [YC-AgentsInGames]: "Agents in Games", YC Labs with Olam Labs (October 2026): how the agents' decisions are modelled, and what to borrow

Prepared for issue [#133](https://github.com/M450NCH00/CrowdSimulation/issues/133) (RF-44, track #55). It answers the supervisor's point 8 of November 2026 (SV14): "take a look at this and see how they model the agent's decisions". Read on 2026-11-25. No model call, nothing cloned or run, USD 0.

## Sources and how to read the citations

| Short name | What it is | Cached as (local only; passages in `refs/rf44_excerpts.txt`) |
| --- | --- | --- |
| **page** | The web page, https://labs.ycombinator.com/projects/games/index.html, fetched on 2026-11-25 and turned into text. The whole page loaded, including the Mindustry section, so the user does not need to save it as a PDF (issue task 1) | `refs/rf44_yc_agents_in_games_page.txt` |
| **mc-tools**, **mc-arch**, **mc-prompt**, **mc-obs**, **mc-readme** | `yc-software/minecraft-agent-harness` (MIT) at commit `775d558`: `docs/tools.md`, `docs/architecture.md`, `src/prompt.js`, `src/tools/game/observation.js`, `README.md` | `refs/rf44_mc_*.txt` |
| **md-instr**, **md-readme** | `olamlabs/multi-agent-mindustry` (GPL-3.0) at commit `1374e46`: `mindustry-series/instruction.md` (the text every agent receives) and `mindustry-series/README.md`. **Confirmed:** this is the repository the issue marked "to confirm" (page line 1187) | `refs/rf44_md_*.txt` |

`[page:53]` means line 53 of the cached page text. The other files are cited the same way. Every passage cited is copied into `refs/rf44_excerpts.txt` under its file and line. The repositories were read through GitHub's API and raw files at a pinned commit; nothing was cloned, installed or run. `[inference]` marks my reasoning, not the sources'.

**What was run** `[page:39, 1009, 1121]`:
- **Civ50:** 50 GPT-6.1 Sol agents in survival Minecraft for 3 hours, with one goal: "Build a thriving civilization."
- **Bed Wars:** nine 45-minute games, 10 Claude Opus 5.5 agents against 10 GPT-6.1 Sol agents, with the instruction "win the game".
- **Mindustry:** a 7-game PvP series, GPT-6.1 Sol in Codex against Claude Opus 5.5 in Claude Code, won 6–1 by the GPTs, about 9.5 hours in all.

*Correction to the issue:* the Mindustry series was **50 against 50**, not "teams of 10". The repository's table lists "50 Opus 5.5 vs 50 Sol 6.1 | 7 | None | 19m 40s–4h 16m 22s per game; 9h 29m total" `[md-readme:276]`. The page names seats up to "GPT #87" `[page:1175]`.

## Answers to the issue's questions

### 1. What does each agent observe, and how often does it decide?

**Minecraft (the harness):**
- **Before every model call, a fresh observation is appended to the request.** It holds the visible blocks and entities, inventory, health, hunger, oxygen, unread messages, recent hits, and an optional image. "It is not saved in the transcript." `[mc-arch:26-28]`
- **The observation is structured JSON** `[mc-obs:38-56]`. It gives the agent's own `position` {x, y, z}, its `yaw` and `pitch` (numbers), a list of blocks and of entities, each with an absolute `position`, and the line "360-degree local line-of-sight survey; not a chunk or hidden-entity scan."
- **Sight is a line of sight within 64 blocks** in every direction `[mc-arch:48-49]`. It is not a view cone like negsim's 75°.
- **When it decides:** "The runner is continuous. After a natural final answer it idles (10 s by default) and wakes on a timer or on an event." Events such as chat, DMs, damage, low oxygen and respawn are queued and merged. Urgent ones wake the agent at once and can interrupt the current body action `[mc-arch:31-34]`.
- **The world does not stop while it thinks.** When the server is slowed, the prompt says the world runs "continuously while you think" `[mc-prompt:18-21]`.

**Mindustry:**
- **There is no pushed observation.** The agent pulls state with `query` (current records) and `events` (its log), then waits in `POST /wait` until an entry matches its wake list. By default that list is messages from other seats `[md-instr:34-40]`.
- "The game runs in real time while you think, and every seat acts at the same time." `[md-instr:3]`
- Every reply carries `status`, which includes the agent's own unit and its `x`, `y` `[md-instr:32]`.

**Against negsim** `[inference]`: Minecraft's wake-on-event is close to negsim's event-driven decision points (D5). Neither game pauses for an exchange, which RF-40's `turn_taking` does.

### 2. What is the action space, and how are actions described?

**Minecraft: a fixed menu of named, high-level tools**, 51 rows in the tool reference `[mc-tools]`. Each is described in plain words of what it does physically:
- `go_to`: "Walk to coordinates … Stops within `distance` blocks of the target (default 2) and reports where it actually stopped. Failures explain why and suggest a next step." `[mc-tools:19]`
- `flee` replans "about twice a second" `[mc-tools:22]`.
- `attack` takes `chase` and `max_distance` `[mc-tools:56]`.
- "Each call returns structured JSON; failures carry a short `failureCode` and a hint for the next call." `[mc-tools:3]`
- Body actions "run one at a time through the action runner and can be cancelled" `[mc-tools:3]`.
- An agent can also write scripts in its own Linux sandbox that call the same tools (`tool go_to '{"x": 120, …}'`) `[mc-tools:97-113]`. The page shows such scripts: fishing loops, and a one-line pearl throw `[page:1031]`.
- **What the model sees is frozen:** a test "checks every tool name, description and schema against a committed snapshot, so moving code between files cannot change what the model sees" `[mc-arch:76-79]`.

**Mindustry: five API tools** (`query`, `events`, `act`, `say`, `wake`) `[md-instr:34]`.
- `act {ops:[…]}` applies inputs such as `{"op": "input", "move_to": {"x": 80, "y": 34}}`.
- Each result has `ok` and an `effect`, or an `error` (`code`, `message`, `facts`). "An accepted input has started, not finished." `[md-instr:38]`
- `query {of:"ops"}` lists every input that `act` accepts `[md-instr:36]`.

**In both games, the agent names a target and code moves the body.** A pathfinder walks to coordinates, so the model never chooses walking angles. The only angles are `look`'s yaw and pitch for aiming `[mc-tools:12]`.

### 3. Are positions absolute or relative to the agent?

**Absolute, in both.**
- Minecraft gives world coordinates (x, y, z) for the agent, every block and every entity `[mc-obs:30, 37, 41]`.
- Agents write absolute coordinates into their shared notes: "Lit underground refuge centered (1532,62,1493), entry gate (1532,62,1496)" `[page:53]`; "Reliable station: stand (1575.49,63,1488.51) … look yaw 0 pitch 20" `[page:368]`.
- Mindustry is a **tile grid in compass axes**: "Coordinates are tiles, with x east and y north; … Rotation `0` faces east (`+x`), `1` north (`+y`), `2` west (`−x`), and `3` south (`−y`)." `[md-instr:46]`
- **Neither interface uses directional left or right.** In the Minecraft tool reference the words appear only for mouse clicks (`click_slot`, `interact_entity`) `[mc-tools]`. They are not in the observation `[mc-obs]` or the prompt `[mc-prompt]`. Mindustry's instructions do not contain them at all `[md-instr]`. (Checked by searching the cached files.)

### 4. What kind of mistake is each blooper, and which RF-45 categories would catch it?

RF-45's draft categories (#134):
1. misperceived the other;
2. misremembered itself;
3. says one thing, plans another;
4. says a side it does not take;
5. not an available action;
6. made-up source.

| Blooper (page) | What kind of mistake | RF-45 category |
| --- | --- | --- |
| Game 1: a Claude retracts "hand-mining coal" as useless; a teammate's measurement ("core coal went 124 -> 1235 in 35s") proves it works `[page:1173]` | A wrong belief about what an action can do, corrected by a measurement | None fits. Nearest: a claim about the world the input contradicts. **A gap:** see below |
| Game 3: "myCorvusCANNOT-AIR assertion wasWRONG" `[page:1175]` | A false claim about a unit's ability | The same gap |
| Game 3: "a mix-up over who was flying a Corvus" `[page:1175]` | Misattributing who did something | 1 (misperceived the other) |
| Game 5: "first-wave loss observed" at the moment the other team's core died; it was a win `[page:1177]` | Misreading the outcome | 1 (misperceived the state) |
| Game 6: 55 of 74 anti-air turrets loaded with copper instead of graphite `[page:1179]` | A wrong action choice, found by an audit. **Not a hallucination:** nothing claimed was false | Not counted. An outcome error, as RF-45 says of random decisions |
| Game 7: the series result "to nine decimal places" `[page:1181]` | Style, not an error | — |
| Civ50: "Transfer tool reported one cooked chicken dropped to you and picked up", but another agent had picked it up and eaten it `[page:930, 947]` | A tool's report taken as the outcome | Closest to 2 (an agent believing its own act succeeded). The agents' fix: "Ledger marks served only after recipient confirms actual consumption, not tool pickup report" `[page:982]` |
| Bed Wars: a tool bug stopped block-breaking. GPT found the workaround; "several Claudes concluded breaking was impossible" `[page:1071-1078]` | Generalising from one failure to a false rule | The same gap as Games 1 and 3 |
| Bed Wars: Claude players wrote lessons in memory ("Died AGAIN: attack chase pulled me onto south wool bridge") and "repeated the mistakes anyway" `[page:1083-1102]` | Not acting on one's own stated lesson | Like 3 (says one thing, does another), across time |

**None of the bloopers is a left-and-right or frame error.** The one spatial kind is falling off edges, an error of movement near a hazard `[page:1089-1102]`. `[inference]` These interfaces never ask the model for a body-relative side (question 3), so a left-and-right error has no way to occur.

**For RF-45** (a suggestion; RF-45 fixes its definition with the user first): add a category **"misstated the setting"**. It would cover a claim about the corridor, the rules or what a step can do that contradicts the description, for example "there is no room to pass" when the description gives the widths. Games 1 and 3 and the Bed Wars case would fall there.

### 5. What can be borrowed, and what does not fit?

The two settings differ sharply `[inference]`:
- **Game agents** run for minutes to hours, with code, notes and an audit trail. They are judged on winning, with no human comparison.
- **negsim's agents** decide in about a second, at most 6 times, and are judged against human behaviour (RF-37).

| Idea from the study | Where it is | Fits? | Issue that would use it |
| --- | --- | --- | --- |
| **A fixed menu of named actions, each described in one plain sentence of what it does physically**, with a validated schema | mc-tools; mc-arch:76-79 | **Yes.** It is what SV10 and SV11 ask for | **RF-47** (the menu): describe each option by its effect ("step a little to your left: you move about half a metre aside, then walk on"), as AS3's table already does |
| **Name a target; code moves the body** (`go_to` coordinates, a pathfinder; no angles) | mc-tools:19; md-instr:38 | **Yes.** It is the same move as AS4 and AS5: the parser converts | **RF-47, RF-48** (code turns a choice into steps); **RF-50, RF-51** (code turns a choice into cells) |
| **A refusal with a code and a hint for the next call** ("failures … suggest a next step"; "error (code, message, facts)") | mc-tools:3; md-instr:38 | **Partly.** negsim retries an unreadable reply once | **RF-47:** the retry message names what was wrong (option not on the menu, a value out of range). Any wording change is a new template version |
| **Absolute coordinates in compass axes, and a tile grid** ("x east and y north"; rotation 0 faces east) | md-instr:46; mc-obs | **Yes,** as support for an absolute frame. The game agents are told their own position and never convert someone else's left and right | **RF-48** (positions from a wall); **RF-50, RF-51** (lanes as tiles). It does not settle RF-43's question of compass against landmark names: Mindustry uses compass axes, but its agents read coordinates, not wall names |
| **Grounding lines in the prompt:** "Only observations establish what is currently visible"; "Never claim a tool action succeeded unless its result supports that"; "An accepted input has started, not finished" | mc-prompt:63; md-instr:38 | **Yes** | **RF-45:** these are the failure kinds to count. **RF-47 and later templates:** one such line ("only what is described above is what you perceive") as a new template version, tested against RF-45's share |
| **Correcting a known false belief in the instructions** ("The core-spawned Gamma … bullets deal **zero damage to buildings**") | md-instr:17-19 | **Yes** | After **RF-45**: if one false belief recurs (for example the facing note applied to words already in the listener's frame, RF-40's E3), state the fact in the next template |
| **The model's view frozen by a snapshot test** | mc-arch:76-79 | Already done: negsim freezes templates and hashes them in a MANIFEST | — |
| **Private reasoning recorded and read alongside the messages** ("R_Felix · private reasoning · 43:18") | page:1045-1050 | **Yes** | **RF-53** (#144): store DeepSeek's reasoning text. The default Mindustry job runs its agents at "high reasoning effort" `[md-readme:119]`; the page reports no comparison with it off |
| **Wake on events, interrupt on urgent ones** | mc-arch:31-34 | Already done (D5) | — |
| **No pause; every seat acts at once** | md-instr:3 | **No** for talk: RF-40's pause is what lets a message arrive in time | — |
| **Memory files, shared notes, a directory, scripts and code in a sandbox** | mc-tools:97-117; page:1193 | **No.** A meeting lasts seconds with at most 6 decisions. Code would let an agent compute geometry, which RF-43 suggests doing in negsim's own code instead | — |
| **A 360° line-of-sight survey** | mc-obs:54 | **No.** negsim's 75° cone to 10 m is chosen to match human perception (Moussaïd et al. 2011) | — |
| **Leaders chosen by directory order:** "46 of the other 49 agents sent their first message to Ada, the first name on the roster" | page:988, 1079 | A caution about order effects. RF-40 already counterbalanced who is asked first and found no effect | — |

## Open questions and limits

- **A blog-style write-up, not a paper.** It reports no rates, no repeats and no tests. The bloopers are anecdotes chosen to amuse.
- **The model names in the page** (GPT-6.1 Sol, Claude Opus 5.5) and the repositories' defaults (GPT-6.1 Terra, `gpt-6-luna`) differ. The page does not give the exact settings of each run beyond "GPT-6.1 Sol in Codex" and "Claude Opus 5.5 in Claude Code" `[page:1121]`.
- **What the Minecraft agents are told in a Civ50 or Bed Wars run** (their `soul` or personality text) is not in the page. The prompt builder shows the structure only `[mc-prompt]`.
- **The Mindustry instructions are the repository's current version** (commit `1374e46`, pushed 2026-11-19), which may be newer than the series on the page (October 2026). For example, the Gamma correction may have been added after a blooper `[inference]`.
- Only the files named above were read, not the harnesses' full code.
