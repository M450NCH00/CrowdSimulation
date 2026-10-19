# Describing environments to LLMs: the five entries

> For issue [#52](https://github.com/M450NCH00/CrowdSimulation/issues/52). Literature only. Any
> description format these entries point towards is **a design proposal, not agreed**; it needs
> the supervisor's sign-off.
>
> - Each entry was confirmed from its own page (arXiv abs page, the journal's article page, the
>   proceedings record on Crossref or ML Anthology), and its status is recorded.
> - Every quotation was checked by script against the cached extract named in the entry
>   (`refs/ed_*.txt`, made with `pdftotext -enc UTF-8`, reading order). Page numbers are PDF pages
>   of the version read, counted from the form feeds in the extract; for Ntarouis & Geraerts they
>   are the journal's page numbers.
> - `[inference]` marks my reasoning, not the source's claim. A table value is named by its table.

Companion files: [findings](findings.md) · [verdict](verdict.md) · [token estimates](token-estimates.md) ·
[search log](search-log.md) · [missing papers](missing-papers.md) ·
[BibTeX](refs-environment-description.bib)

**The five, by relevance tier** (tiers as defined in the issue)

| # | Handle | Tier | Why it is here, in one line |
|---|---|---|---|
| 1 | [Durupinar-AffectCrowd] | 1: crowd simulator | Field-of-view perception, the three nearest in full, the rest as counts; prompt printed; prompt variants measured |
| 2 | [Ntarouis-CrowdGenAgents] | 1: crowd simulator | Radius perception with positions and distances; scaling from 10 to 250 agents measured |
| 3 | [Park-GenerativeAgents] | 2: multi-agent sandbox | The world as a tree in prose; each agent knows only what it has seen; the architecture tier 1 builds on |
| 4 | [Chen-MAPFLLM] | 2: multi-agent pathfinding, with a measured comparison | Image vs obstacle-coordinate list vs text map (Table 3); success by number of agents (Table 1) |
| 5 | [Martorell-TextToSpace] | 2/3: grid world, with a measured comparison | Six text encodings of the same grid state, three classes, 1B to 90B models, with statistics |

---

### [Durupinar-AffectCrowd]: How Affect Propagates among LLM Agents: Emergent Emotional Contagion in Crowd Simulation

- **Authors / Year / Venue / Link / DOI:** Funda Durupinar (University of Massachusetts Boston) /
  2026 / arXiv:2607.25140v1 [cs.AI], 27 July 2026 / https://arxiv.org/abs/2607.25140 / no DOI.
- **Status:** `[preprint]`. No published version found (Crossref title search, 2026-10-19).
  **Read:** full text, 31 pages, from `refs/ed_durupinar2026_affect.txt`.
- **Why it is one of the five:** tier 1. It is the only source found that describes a crowd
  simulator's state to an LLM with an explicit field of view, occlusion and a cap on how many
  neighbours are described in full, and it prints its prompt and tests prompt variants.
- **The environment:** a Unity crowd simulator; LLM agents above a conventional steering layer.
  "At each step, an agent perceives the observable behavior of nearby agents, and the LLM
  appraises this input considering the agent's personality, current affective state, memory, and
  context." (§3, p. 4). Five scenarios, 10 to 26 agents: "An open 56 × 56 m room where 10 agents
  stroll between points of interest" (Calm Plaza) up to "A long, narrow 9 × 80 m lane. 26 agents
  mill in place" (Standing Line) (§4.1, p. 7). The LLM decides affect and expression, plus a few
  steering parameters: "Appraisal influences motion only through a speed multiplier, a
  forcefulness value, a personal-space preference, and a discrete navigation intent." (§6, p. 23).
- **How the environment is described:**
  - *Form*: second-person prose made by a fixed template from a perception snapshot: "a snapshot
    of the perceptual state is taken and converted into natural language by a fixed template"
    (§3.1, p. 5), inserted into a user prompt with capitalised section headers.
  - *What is included*: the crowd, not the walls. "The description begins with a one-line summary
    of the visible crowd, giving its size, density, coherence, and mean speed, and notes any
    visibly fallen individuals." (§3.1, p. 5). The place enters as a free-text "situational
    context" per scenario: "Contexts are inserted verbatim into the prompt" (Table 5 caption,
    p. 29). `[inference]` No geometry (widths, wall distances) reaches the LLM; walls act only
    through occlusion and the steering layer.
  - *Numbers and directions*: "distance and direction" are given for the nearest people (§3.1,
    p. 5), but the paper does not print a rendered description, so the units, rounding and the
    form of "direction" are **not reported**.
  - *Prompt excerpt describing the environment*: "== WHO YOU ARE == Your character: <personality
    description> Where you are: <scenario context>" and "== WHAT YOU SEE AND HEAR RIGHT NOW ==
    <perception description>" (Appendix A, p. 28). The system prompt sets the perceptual stance:
    "You only see/hear OUTWARD behavior of others (motion, speed, gestures, faces, sounds, crowd
    density, forces)" (Appendix A, p. 27).
- **Other agents:** three layers. Everyone visible is summarised and counted by cue: "It then
  counts the visible agents displaying each facial expression, gesture, and kind of movement, and
  those emitting each kind of vocalization, and reports any voices that are audible but not
  visible, with the distance and direction of the nearest." Then the nearest few in full:
  "Finally, for up to three nearest visible individuals, it gives the distance and direction
  together with the full expressive state, including face, gesture, voice, movement, speed, and
  spacing." (both §3.1, p. 5). *Order*: by distance (nearest first) `[inference from "three
  nearest"; the order within the three is not stated]`. In practice few are seen: "The mean number
  of visually perceived neighbors within the 8 m visual range is ≈ 3 for Concert and Evacuation,
  ≈ 2 in Standing Line, and ≈ 1 for the Calm Plaza control." (§4.1, p. 7).
- **Perceivable or omniscient:** perceivable only, and the rule is explicit: "A neighbor is seen
  only if it lies within a limited visual range of 8 m, inside a 200° field-of-view cone, and is
  not occluded by a wall or by intervening bodies." Sound has its own range: "loud calls ... carry
  farther (20 m) than quiet ones such as chattering and gasping (10 m)." (both §3.1, p. 4).
  Attributes are outward only (faces, gestures, voice, movement); no age or gender of others is
  described `[inference: none appears in the list of described features]`.
- **How well it works:**
  - *Model choice matters more than wording.* Four backends on the same appraisal probe:
    "Reliability and directional validity hold for the three capable backends and fail only at the
    smallest." (§4.3.4, p. 19). For the smallest: "67% of its generations fail to produce
    schema-valid JSON, and the ones that parse order the cues incorrectly." (Fig. 12 text, p. 20).
    gpt-4o-mini "nearly erases the personality gap on the calm, alarm, and joyous scenes (|∆V | ≤
    0.01, Holm-adjusted p ≥ 0.64)" (§4.3.4, p. 19). Table 4 (p. 20): parse errors 0% for
    gemini-3.1-flash-lite, gpt-4o-mini and llama3.1:8b, 67% for llama3.2:3b.
  - *Which perceived cue matters* (a channel ablation, 20 runs per condition, §4.2.4): "Voice has
    the greatest exposure rate, with alarm cues perceived in 53% of appraisals." and "Gesture is
    perceived in more appraisals than face, 0.31 versus 0.07, and has a higher conditional panic
    rate, 0.80 versus 0.60." (§4.2.4, Table 1 discussion, p. 12).
- **Ablations or comparisons between description formats:** seven prompt variants on an isolated
  appraisal probe: "the base prompt, two semantic paraphrases (plain and formal) that leave the
  JSON contract unchanged, and four ablations that drop the personality block, the situational
  context, the outward-behavior clause, or the social-framing line." (§4.3, p. 17). Results:
  "plain versus formal wording makes essentially no difference. Both paraphrases place all four
  cues within 0.06 valence of the base prompt for both dispositions" and "Dropping the
  outward-only clause, the social-framing line, or the situational context barely moves any cue."
  (§4.3.3, p. 19). The probe scene is fixed: "Each scene places the agent in a small local group
  (5 others in the calm baseline, 6 in the cue scenes)" (§4.3, p. 17). **The perception
  description itself is never varied** (no change of format, number of people or field of view).
- **Cost:** one LLM call per agent per appraisal: "every agent consumes a call each step" (§4.1,
  p. 7); output capped: "200 max tokens" (§4.1 footnote 2, p. 7). Tokens per prompt and latency:
  not reported.
- **Limits stated by the author:** "Per-agent appraisal costs restrict the number of LLM-driven
  agents that can be simulated, resulting in crowds that are smaller and less dense than real
  gatherings." (§6, p. 23). On validity: "We evaluate the observed dynamics against theoretical
  expectations and qualitative parallels to human and animal collective behavior, not against
  empirical crowd data." (§6, p. 23). On the probe: "the probe does not vary the framing itself and
  therefore cannot determine how the same cue and personality would be appraised under different
  situational contexts." (§6, p. 23).
- **What it means for negsim's prompts:** `[inference]` (1) A tested pattern for scaling beyond one
  neighbour without the prompt growing with crowd size: a summary line for everyone, full detail
  for at most three, nearest first. (2) A concrete, citable perceivability rule (range, cone,
  occlusion) to replace "Other people are walking around you as well." (3) Its evidence is about
  wording around the description, not the description: it does not tell negsim whether three
  in full is enough for a doorway decision. (4) Its backend result matches issue #16's finding that
  effects differ between models: any format test must be run on more than one model.
- **BibTeX:** `durupinar2026affect`

### [Ntarouis-CrowdGenAgents]: Generative agents in crowd simulation: a cognitive approach with Large Language Models

- **Authors / Year / Venue / Link / DOI:** Nizar Ntarouis, Roland Geraerts (Utrecht University) /
  2026 / *Acta Polytechnica CTU Proceedings* 57:263–274, in the section "Pedestrian and Evacuation
  Dynamics 2025" (journal article page) / https://ojs.cvut.cz/ojs/index.php/APP/article/view/11557 /
  doi:10.14311/APP.2026.57.0263 (resolves on Crossref; published 16 June 2026).
- **Status:** published (conference proceedings of PED 2025); CC BY 4.0 (p. 263). **Read:** full
  text, 12 pages, `refs/ed_ntarouis2026_crowd_genagents.txt`. **Not read:** the supplementary
  materials that hold the prompts (Zenodo, doi:10.5281/zenodo.19519677; automated download refused,
  HTTP 403; see [missing-papers.md](missing-papers.md)).
- **Why it is one of the five:** tier 1, peer-reviewed, and the only crowd source found that
  measures how an LLM crowd behaves as the number of agents grows (10 to 250).
- **The environment:** crowd evacuation and crisis scenarios; LLM agents choose goals and actions,
  a crowd framework moves them: "The LLM-based architecture produces high-level decisions, such as
  goal positions and intended actions, which are then passed to a crowd simulation framework [20]
  that handles path planning, trajectory computation, and collision avoidance." (§2.7, p. 268).
  Models: "GPT-3.5 Turbo and GPT-4 (mid-2024)" (§3.3, p. 271).
- **How the environment is described:**
  - *Form*: a mix of short text events and labelled entities with positions: "The simulation
    environment is represented through a hybrid symbolic spatial encoding." (§2.4, p. 265).
  - *What is included*: events, objects and agents, each as text: "Events are textual descriptions
    of actions, state changes, or environmental conditions (e.g., "bar is closed", "fire alarm
    triggered", "agent_0 is running")." Agents are anonymous IDs: "Agents are labeled with unique
    identifiers (agent_0, agent_1, etc.), and their actions are described textually by the
    system." (§2.4, p. 265).
  - *Numbers and directions*: absolute positions plus distances, no egocentric bearing reported:
    "agents observe all entities within a configurable distance threshold, receiving both their
    absolute positions and relative distances to establish 2D depth perception." (§2.4, p. 265).
    Units and rounding: not reported.
  - *Prompt excerpt*: not printed in the paper; the authors point to the supplement: "Example
    prompts for room selection, object choice, and immediate action decisions are provided in the
    supplementary materials [16]." (§2.7, p. 268).
- **Other agents:** everyone inside the radius, then filtered by novelty and importance, not by a
  count: "All entities within the perceptual radius are compared against recently observed
  information in memory. New observations are processed and stored, whereas existing entities have
  their recency scores updated" (§2.4, p. 266). Each perceived event is scored by the LLM:
  "Perceived events are classified as dangerous or attractive and assigned importance scores from
  1 to 10" (§2.4, p. 266). Order of listing: not reported.
- **Perceivable or omniscient:** perceivable (radius-based), with an explicit reason for
  filtering: "Employing selective attention, filtering by spatial proximity, importance thresholds,
  and temporal novelty balances the complexity of managing computational costs and context window
  limitations while preserving behavioral realism." (§2.4, p. 267). The radius value used is not
  stated: "The visual radius is a parameter that the experimenter can adjust." (§2.5.1, p. 267).
- **How well it works:** human judges, not a format comparison: "We conducted a within-subjects
  study with 25 participants." (§3.1, p. 269); "The simulation's capture of diversity in human
  behavior received a mean score of 3.64 (SD = 0.86)" (§3.2.4, p. 271). **Scaling** (fire
  evacuation, one room, one exit; §3.3, p. 271): "processing time increases from 5 seconds (10
  agents) to 40 seconds (100 agents)"; "Total LLM requests show clear positive correlation with
  agent count, rising almost linearly from approximately 2 000 requests for 50 agents to over 6 000
  for 250 agents." The authors' explanation ties cost to what is perceived: "The exponential
  increase in processing with agent count occurs because agents process other agents' actions.
  Event count grows with agent actions within the environment, increasing processing load for each
  agent as they perceive these events." (§3.3, p. 271).
- **Ablations or comparisons between description formats:** none.
- **Cost:** requests and latency as above (§3.3, p. 271); tokens per prompt: not reported.
- **Limits stated by the authors:** one is about what the description leaves out: "The absence of
  trajectory information in the environmental representation prevented authentic herding pattern
  formation. This lack of sophisticated spatial awareness, in addition, resulted in some
  unrealistic navigation behaviors, such as proximity to walls and erratic pacing." (§4.1, p. 272).
  On scale: "the architecture was limited to approximately 250 agents before exceeding API
  capacity." (§4.1, p. 272).
- **What it means for negsim's prompts:** `[inference]` (1) The authors' own diagnosis is that
  leaving motion out of the description changed collective behaviour (no herding). negsim already
  gives speed, heading and whether the gap is closing for its one neighbour; extending that to more
  people is the open part. (2) Radius-only selection with no cap makes the prompt and the call
  count grow with density, which their scaling run shows; a cap (as in [Durupinar-AffectCrowd]) is
  the obvious counter. (3) The evidence is evacuation, not two-person conflicts.
- **BibTeX:** `ntarouis2026crowd`

### [Park-GenerativeAgents]: Generative Agents: Interactive Simulacra of Human Behavior

- **Authors / Year / Venue / Link / DOI:** Joon Sung Park, Joseph C. O'Brien, Carrie J. Cai,
  Meredith Ringel Morris, Percy Liang, Michael S. Bernstein / 2023 / UIST '23 (Proceedings of the
  36th Annual ACM Symposium on User Interface Software and Technology), pp. 1–22 /
  https://arxiv.org/abs/2304.03442 / doi:10.1145/3586183.3606763 (Crossref).
- **Status:** published at UIST 2023. **Read:** full text, arXiv:2304.03442v2 (6 August 2023), 22
  pages, `refs/ed_park2023_generative_agents.txt`. The ACM version was not read.
- **Why it is one of the five:** tier 2 (a sandbox town of 25 agents). It is the reference design
  for turning a simulated world into prose for LLM agents, including partial knowledge of the
  world, and it is the architecture [Ntarouis-CrowdGenAgents] says it builds on.
- **The environment:** "a small town of twenty-five agents" in a sandbox "inspired by The Sims"
  (Abstract, p. 1). The LLM decides plans, reactions, where to go, and what to say; movement uses
  game pathfinding: "we use traditional game path algorithms to animate the agent's movement so
  that it travels to the location indicated by the leaf node." (§5.1, p. 13).
- **How the environment is described:**
  - *Form*: a tree of areas and objects, flattened into prose: "we represent the sandbox
    environment—areas and objects—as a tree data structure, with an edge in the tree indicating a
    containment relationship in the sandbox world. We convert this tree into natural language to
    pass to the generative agents. For instance, "stove" being a child of "kitchen" is rendered
    into "there is a stove in the kitchen."" (§5.1, p. 12).
  - *What is included*: places and objects by name, and other agents as action statements: "the
    agents output a natural language statement describing their current action, such as "Isabella
    Rodriguez is writing in her journal"" (§3.1.1, p. 5). No geometry.
  - *Numbers and directions*: none. Location is a path of names, e.g. the output "The Lin family's
    house: garden: house garden." (§5.1, p. 13). `[inference]` Distances, sizes and directions do
    not appear in any printed prompt.
  - *Prompt excerpt describing the environment*: "Eddy Lin is currently in The Lin family's house:
    Eddy Lin's bedroom: desk) that has Mei and John Lin's bedroom, Eddy Lin's bedroom, common room,
    kitchen, bathroom, and garden. Eddy Lin knows of the following areas: The Lin family's house,
    Johnson Park, Harvey Oak Supply Store, The Willows Market and Pharmacy, Hobbs Cafe, The Rose and
    Crown Pub." (§5.1, p. 12; the unbalanced parenthesis is in the source).
- **Other agents:** whoever is within a visual range, as observations: "The sandbox server is also
  responsible for sending all agents and objects that are within a preset visual range for each
  agent to that agent's memory" (§5, p. 12). What reaches a decision prompt is one observation plus
  retrieved memories about that agent, e.g. "Observation: John saw Eddy taking a short walk around
  his workplace. Summary of relevant context from John's memory: Eddy Lin is John's Lin's son."
  (§4.3.1, p. 11). The value of the visual range, a cap, and an order: not reported.
- **Perceivable or omniscient:** perceivable, including the map itself: "Agents are not
  omniscient: their tree may get out of date as they leave an area, and is updated when they
  re-enter the area." (§5.1, p. 12). "Agents remember a subgraph that reflects the parts of the
  world they have seen, maintaining the state of those parts as they observed them." (Figure 2
  caption, p. 5).
- **How well it works:** believability of interview answers, ranked by human evaluators: "100
  participants compared interview responses generated by four different agent architectures and a
  human-authored condition" (§6.1, p. 13), scored with TrueSkill (§6.5.1, p. 14). "the full generative agent architecture produced
  the most believable behavior" with μ = 29.89, σ = 0.72, against μ = 21.21, σ = 0.70 for the
  ablation "with no access to memory, planning, or reflection" (§6.5.1, p. 14; ⚠ the extract
  garbles the μ and σ glyphs, so the quoted words exclude them; the values are as printed). Effect
  size: "a standardized effect size of" d "= 8.16, or eight standard deviations." (§6.5.1, p. 14;
  same glyph caveat).
- **Ablations or comparisons between description formats:** none. The ablations remove memory,
  reflection and planning, not parts of the environment description. The paper does report a
  description failure and its proposed fix: "erratic behaviors caused by misclassification of what
  is considered proper behavior, especially when the physical norms of certain locations that are
  hard to convey in natural language did not percolate to the agents." The example: "the college
  dorm has a bathroom that can only be occupied by one person despite its name, but some agents
  assumed that the bathroom is for more than one person" and the fix: "describing the dorm bathroom
  as a "one-person bathroom," instead of a "dorm bathroom."" (§7.2, p. 17). The proposed fix was
  not tested in the paper `[inference: no result for it is reported]`.
- **Cost:** "The present study required substantial time and resources to simulate 25 agents for
  two days, costing thousands of dollars in token credits and taking multiple days to complete."
  (§8.2, p. 17). Model: "Our current implementation utilizes the gpt3.5-turbo version of ChatGPT"
  (§4, p. 8). Tokens per prompt: not reported.
- **Limits stated by the authors:** the growing world model: "synthesizing an increasingly larger
  set of memory not only posed a challenge in retrieving the most relevant pieces of information
  but also in determining the appropriate space to execute an action, given the increasing number
  of locations that the agent learned about." (§7.2, p. 16).
- **What it means for negsim's prompts:** `[inference]` (1) The bathroom example is negsim's
  doorway in miniature: a capacity of one must be stated as a capacity ("lets only one person
  through at a time", as `persona_v1.yaml` already does), not left to a name or to a width. Layer 4's
  description gives the width ("narrows to 0.90 m") and leaves the capacity to the model; that is
  worth testing. (2) Its prose has no numbers at all, so it is no evidence that numbers help or
  hurt. (3) It shows a perceivable-only design at town scale, but its "other agents" are described
  by what they do, not where they are, which is the part negsim needs.
- **BibTeX:** `park2023generative`

### [Chen-MAPFLLM]: Why Solving Multi-agent Path Finding with Large Language Models has not Succeeded Yet

- **Authors / Year / Venue / Link / DOI:** Weizhe Chen, Sven Koenig, Bistra Dilkina / 2024 /
  arXiv:2401.03630v2 (9 February 2024) / https://arxiv.org/abs/2401.03630. Published version:
  *Transactions on Machine Learning Research* 2025, under the title "Solving Multi-Agent Path
  Finding as an LLM Benchmark: How, How Good and Why" (ML Anthology record
  https://mlanthology.org/tmlr/2025/chen2025tmlr-solving/; OpenReview
  https://openreview.net/forum?id=8hAxEFRVQT).
- **Status:** published in TMLR 2025 (revised and retitled). **Read:** the arXiv v2 preprint,
  13 pages, `refs/ed_chen2024_mapf_llm.txt`; the TMLR version refused automated download (HTTP
  403), so **locators are to arXiv v2** and the published tables may differ (see
  [missing-papers.md](missing-papers.md), V1).
- **Why it is one of the five:** tier 2, and it gives a **measured comparison of description
  formats in a multi-agent setting**, plus success as the number of agents grows: the closest
  domain to pedestrian conflicts among the measured comparisons found.
- **The environment:** multi-agent path finding (MAPF) on standard benchmark grid maps; the LLM
  picks every agent's next move: "a four-connected grid map, where each agent is given a start cell
  and a goal cell. ... A conflict happens if two agents end up in the same cell at the same
  timestep." (§2.1, p. 2). A rule-based checker reports collisions back: "We do not provide any
  additional guidance on how the LLM should deconflict the solution but just describe the
  conflicts." (§2.2, p. 3). Model: "By default, we are using the GPT-4-1106-preview model" (§2.3.1,
  p. 4).
- **How the environment is described:**
  - *Form*: third-person text with allocentric grid coordinates, plus an ASCII map; the moves
    available to each agent are listed every step (the "single-step observation").
  - *Prompt excerpt describing the environment*: "Agent 1 is currently in (0,2), and wants to go to
    (3,1). Agent 2 is currently in (1,3), and wants to go to (2,0). The map is as follows, where '@'
    denotes a cell with an obstacle that an agent cannot pass, and '.' denotes an empty cell that an
    agent can pass." and "In the next step: Agent 1 can move ['stay at (0, 2)', 'right to (1, 2)',
    'up to (0, 3)', 'down to (0, 1)']." (Figure 2, p. 3; quotation marks normalised).
  - *Numbers and directions*: integer cell coordinates; "The bottom-left cell is (0,0)" (Figure 2,
    p. 3); directions as up, down, left, right.
- **Other agents:** all agents are listed, every step, each with current cell and goal (Figure 2,
  p. 3). No selection: the LLM is a central planner, so every agent is relevant. Order: by agent
  number.
- **Perceivable or omniscient:** omniscient (global map and all agents) by design: the LLM plans
  for everyone. Table 2 compares global observation alone (GO) with GO plus single-step observation
  (SSO) (§3.3, p. 6).
- **How well it works:** success falls with the number of agents (Table 1, p. 4; 5 scenarios per
  setting, §2.3.1): step-by-step generation succeeds in 100% / 100% / 100% / 60% of runs on the
  empty map with 2 / 4 / 8 / 16 agents, 100% / 80% / 20% on the room map with 2 / 4 / 8 agents,
  and 0% on the maze with 2 agents (values checked on the rendered page). In the authors' words:
  "GPT-4 fails to generate valid solutions when there are more agents on the same map." (§2.3.2,
  p. 4). On why, part of it is reading lists of coordinates: "LLM cannot tell whether a list of
  tuples of numbers has any duplicates." (§3.1, p. 5).
- **Ablations or comparisons between description formats:** yes, three ways to give the map,
  everything else the same: "1. A multimodal-based method MM where we use an image to give the
  picture of the map, and text to describe the problem and the scenario. 2. A text-only method that
  describes the map by listing all the coordinates of the obstacles, named TOO. 3. A text-only
  method that describes the map by feeding the text version of the map with '@' denoting the
  obstacles and '.' denoting an empty space, named TOM." (§3.3, p. 7). Results (Table 3, p. 6, room
  map, success %): MM / TOO / TOM = 100 / 100 / 100 with 2 agents; 20 / 60 / 80 with 4; 0 / 0 / 20
  with 8. The authors: "We found that with an image-based input, the results are even worse." and
  "The failure of TOO further indicates that LLMs do not know how to combine high-level intuitions
  of where obstacles are with concrete reasoning during path planning." (§3.3, p. 7). ⚠ Small
  samples: 5 scenarios per setting (§2.3.1, p. 4), so each cell rests on very few runs. Other prompt
  changes were tried without effect: "breaking the big paragraph into bullet-point style
  instruction, removing some 'useless' instruction, adding a whole example for in-context learning,
  and using the theory of mind to guess other agent's intuitions" — "These tricks did not show any
  help in any scenarios" (§3.1, p. 6).
- **Cost:** tokens grow faster than the number of agents: "with the growing number of agents, this
  average is also growing, which means that the output length is growing faster than linear."
  (Appendix B, p. 12). Figure 9 (p. 13) reads, approximately, 120 / 125 / 240 / 610 tokens per
  agent step at 2 / 4 / 8 / 16 agents for one series `[read off the bar chart, which has no legend;
  approximate]`.
- **Limits stated by the authors:** the setting is centralised and small: "the goal is to
  demonstrate that LLMs can solve small problems simply through prompting and discussing what is
  stopping them from solving larger ones." (§4, p. 7). On scale: "in the real-world applications of
  MAPF, the total number of agents running in the environment could be up to a few thousand."
  (§3.2, p. 6). ⚠ A small inconsistency in the source: the Table 1 caption names ROOM-32-32-4, the
  text "ROOM-32-32-1" (p. 4).
- **What it means for negsim's prompts:** `[inference]` (1) In a multi-agent spatial task, a text
  map beat a list of coordinates and an image, but only at 4 and 8 agents, on very few runs, with
  one model; at 2 agents all three tied. (2) The decline from 2 to 8 agents is the only measured
  quality-versus-number-of-agents result found in this review, but it is for a central planner
  that must move everyone, not for one person perceiving others. (3) Its device of listing the options each
  agent has (the single-step observation) is the analogue of telling a negsim agent its
  possible moves; the authors report it helped (§3.3), which supports keeping negsim's explicit
  stance options.
- **BibTeX:** `chen2024mapf`

### [Martorell-TextToSpace]: From Text to Space: Mapping Abstract Spatial Models in LLMs during a Grid-World Navigation Task

- **Authors / Year / Venue / Link / DOI:** Nicolas Martorell (University of Buenos Aires; CONICET)
  / 2025 / *Explainable Artificial Intelligence*, Communications in Computer and Information Science
  (Springer), pp. 268–291, published 14 October 2025 / https://arxiv.org/abs/2502.16690 /
  doi:10.1007/978-3-032-08330-2_13 (Crossref).
- **Status:** published (CCIS chapter). **Read:** the arXiv:2502.16690v1 preprint (23 February
  2025), 24 pages, `refs/ed_martorell2025_text_to_space.txt`; the Springer chapter was not read
  (see [missing-papers.md](missing-papers.md), V2), so locators are to arXiv v1.
- **Why it is one of the five:** the cleanest measured comparison of **text** formats for a spatial
  decision found: six encodings of identical information, three classes, six model sizes, with
  statistics. negsim is text-only, so this is the comparison it needs most.
- **The environment:** "an agent and a goal are placed in an 5×5 grid" and the LLM picks a move each
  step: "The LLM is required to respond with a JSON object containing a single key, "action", whose
  value is one of four commands: "UP", "DOWN", "LEFT", or "RIGHT"." (§3, p. 4). One agent; no other
  agents, no obstacles.
- **How the environment is described:** three classes: "Cartesian representations: The LLM
  receives explicit (x, y) coordinates for the agent and the goal, along with the grid size.",
  "Topographic representations: The two-dimensional structure of the grid is preserved by
  representing cells and objects using characters or words." and "Textual representations: The
  world state is described in prose-like language." (§3, p. 4). Two variants each, "JSON and Chess
  Notation for Cartesian, Symbol and Word Grid for Topographic, and Row and Column Description for
  Textual" (§3, p. 4).
  - *Prompt excerpts* (Figure 1, p. 5): JSON: "{ "grid_size": 5, "agent_position": { "column": 1,
    "row": 3 }, "goal_position": { "column": 3, "row": 0 }"; Row Description: "The first row has 3
    empty cells, then the goal, then 1 empty cell."
  - *Numbers and directions*: integer grid positions; directions as screen directions (UP, DOWN,
    LEFT, RIGHT); all formats allocentric `[inference from Figure 1: none is relative to the agent's
    heading]`.
- **Other agents:** not described (single-agent task).
- **Perceivable or omniscient:** the full 5×5 grid is given `[inference from Figure 1]`.
- **How well it works:** 100 trials per model and format, LLaMA 3.2-1B to 3.2-90B (§4, p. 5).
  "Notably, Cartesian SIRs consistently outperformed Topographic and Textual SIRs across model sizes
  (Binomial GLM: success ∼ representation + model_size, βtopographic = 1.385, p < .001; βtextual =
  1.270, p < .001)" (§4, p. 6). Mid-sized models show the biggest gap: "the 8B model achieves a 66%
  success rate with the JSON SIR but only 30% with its best non-cartesian SIR (Symbol Grid)." Small
  models are near chance whatever the format: "The smallest models (1B and 3B) perform near chance
  level—around 10%—for all SIR types except for JSON, while the largest models (70B and 90B) always
  exceed a 74% success rate." (§4, p. 6). Within-class variants agree: "this pattern holds
  regardless of formatting variations within each SIR class" (§4, p. 6). ⚠ The reported β values are
  positive for the non-Cartesian classes although the text says they did worse; the sign convention
  is not explained, so I rely on the stated direction and the 66% vs 30% example, not on the β signs.
- **Ablations or comparisons between description formats:** the whole study is one (above). Its
  "ablations" (Appendix B.3) silence model units, not prompt parts.
- **Cost:** not reported.
- **Limits stated by the author:** "While this setting allowed us to isolate the effects of
  different spatial representations, it also limits the generalizability of our findings to more
  complex spatial reasoning scenarios." and future work should test "navigating environments with
  obstacles, multiple goals, or even three-dimensional spaces." (§7, p. 13).
- **What it means for negsim's prompts:** `[inference]` (1) For a spatial decision, explicit
  coordinates in a structured form did better than prose describing the same layout, most of all
  for mid-sized models; DeepSeek-chat is far larger, where the gap narrowed (70B and 90B all above
  74%). (2) negsim's prose already gives explicit numbers (distances, angles), which sits between
  Martorell's "Cartesian" and "Textual" classes; the study did not test egocentric prose with
  numbers, so it cannot say whether negsim's form is good or bad. (3) No other agents, no
  conflicts: it is evidence about encoding positions, not about encoding people.
- **BibTeX:** `martorell2025text`
